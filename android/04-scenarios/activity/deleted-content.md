---
title: "지운 대화와 사진 찾기"
parent: "시나리오 · 행위 재구성"
nav_order: 1630
---

# 지운 대화와 사진 찾기 (Deleted Content)

사용자가 지운 사진이나 대화의 내용을 되찾을 수 있는지, 되찾지 못하면 그 내용이 있었다는 흔적이 어디에 남는지 묻는 조사를 다룹니다. 찾기 쉬운 곳부터 차례로 내려가서, MediaStore 휴지통 파일과 삼성 휴지통 제공자를 먼저 보고 앱 DB 의 삭제 표시, SQLite 빈 공간과 부속 파일, 알림을 차례로 확인합니다. 끝으로 앱 사용 기록으로 지울 때 쓴 앱을 좁히고, 항목마다 내용을 되찾았는지 흔적만 남았는지 나눠 적습니다.

## 조사 질문

"사용자가 지운 사진이나 대화의 내용을 지금 되찾을 수 있는가, 되찾지 못한다면 그 내용이 있었다는 흔적은 어디에 남는가" 를 묻는 흐름입니다. 지웠다는 행위와 그 무렵을 따지는 일은 [증거를 없애려 했나](anti-forensics/index.md) 묶음에서 다루고, 이 페이지는 내용 자체를 찾는 데 집중합니다.

Android 에서 "지웠다" 는 한 가지 상태가 아닙니다. 사진은 휴지통으로 옮겨져 파일이 그대로 남아 있을 수 있고, 대화는 앱 DB 안에서 행이 지워졌거나 삭제 표시만 붙었을 수 있으며, 어느 쪽도 아니면 알림처럼 다른 곳에 남은 조각만 있을 수 있습니다. 그래서 찾기 쉬운 곳부터 차례로 내려갑니다.

## 먼저 확인할 것

- **OS 버전과 제조사** — 미디어 저장소(MediaStore)의 휴지통 규칙과 플랫폼 SQLite 빌드 설정은 현행 AOSP 기준이고, 삼성 기기에는 삼성 휴지통 제공자가 따로 있습니다(아래 표). 분석 대상 기기의 Android 버전과 One UI 버전을 먼저 적어 둡니다.
- **시간대** — 휴지통 파일 이름의 숫자는 유닉스 초, 삼성 휴지통 DB 의 시각은 유닉스 밀리초라서 [2][3] 단위를 맞춘 뒤 기기 시간대로 바꿉니다([시각 값](../../01-foundations/value-decoding/time-values.md)).
- **사용자와 프로필** — 삼성 휴지통 DB 에는 `user_id` 열이 있고 휴지통 파일 경로에도 사용자 번호 자리가 있어 [3], 보안 폴더나 작업 프로필이 있으면 사용자별로 따로 찾습니다([보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md)).
- **수집 범위** — 앱 DB 와 휴지통 DB 는 앱 데이터 영역에 있어 전체 파일 시스템을 확보해야 볼 수 있습니다. adb 일반 권한으로 `/sdcard/Android` 를 나열하면 `data`, `media`, `obb` 세 항목만 보일 수 있지만, 숨김 항목이 빠진 결과일 수 있으니 이것만으로 `.Trash` 폴더가 없다고 결론 내지 않습니다. 확보 방식은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 정합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | MediaStore 휴지통 파일 (`.trashed-` 로 시작하는 파일) | 아직 완전히 지워지지 않은 원본 파일과 만료 예정 시각 | [미디어 저장소](../../02-artifacts/media/mediastore/index.md) |
| 2 | 삼성 휴지통 제공자 (`trash.db` 와 `Android/.Trash`) | 휴지통 파일 위치, 원래 경로, 지우기를 시작한 앱, 지운 시각과 만료 시각 | [삼성 갤러리](../../02-artifacts/media/samsung-gallery.md) |
| 3 | 앱 DB 안의 삭제 표시 | 행은 남기고 삭제 표시만 붙인 대화·연락처 | [문자](../../02-artifacts/communications/messages/index.md), [카카오톡](../../02-artifacts/messengers/kakaotalk/index.md), [연락처](../../02-artifacts/communications/contacts.md) |
| 4 | SQLite 파일의 빈 공간과 부속 파일 | 지운 행이 덮이지 않고 남은 조각 | [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) |
| 5 | 알림 | 대화 앱 알림에 담겼던 제목과 본문 | [알림 기록](../../02-artifacts/app-usage/notification-history.md) |
| 6 | 앱 사용 기록 (usagestats) | 지운 무렵 앞에 있던 앱 | [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md) |

| 기록 | 확인된 범위 | 비고 |
|---|---|---|
| MediaStore 휴지통 이름 규칙과 기본 기간 | 현행 AOSP 기준 [2] | 어느 Android 버전부터 이 규칙인지는 실제 기기에서 확인합니다 |
| 삼성 휴지통 제공자 | ALEAPP 시험 자료가 Android 14·15, 행 0~29개 [3] | One UI 몇 버전부터 있는지, 보관 기간이 며칠인지는 실제 기기로 확인해야 합니다 |
| 플랫폼 SQLite 빌드 설정 | 현행 AOSP 기준 [4] | 앱이 자체 SQLite 를 넣어 쓰는 경우는 앱마다 따로 확인합니다 |

## 분석 흐름

1. **공용 저장 공간의 휴지통 파일부터 찾습니다.** 현행 AOSP 의 MediaStore 는 휴지통에 넣은 파일 이름을 아래 모양으로 바꾸고, 앱이 아직 쓰는 중인 파일에는 `.pending-` 을 붙입니다 [2].

   ```
   .trashed-<숫자>-<원래 이름>
   .pending-<숫자>-<이름>
   정규식: (?i)^\.(pending|trashed)-(\d+)-([^/]+)$
   소스 주석의 예: /storage/emulated/0/DCIM/.trashed-1621147340-test.jpg
   ```

   이름 가운데 숫자는 만료 예정 시각(`date_expires`)이고 단위는 유닉스 초이며, 휴지통 기본 기간은 30일, 대기 중 파일은 7일, 연장은 7일입니다 [2]. 파일이 보이면 원본 내용이 그대로 남아 있는 상태라서 해시를 떠 두고 그대로 확보합니다. 이 숫자로 휴지통에 넣은 무렵을 셈하는 법과 연장 때문에 생기는 오차는 [증거를 없애려 했나](anti-forensics/index.md) 묶음에 있습니다. 원래 이름이 UTF-8 로 255바이트를 넘으면 가운데를 잘라 `...` 을 넣으니 [2], 되살린 이름이 처음 이름과 다를 수 있다는 점을 적어 둡니다.

2. **삼성 기기라면 삼성 휴지통 제공자를 봅니다.** 휴지통 DB 와 휴지통 파일은 아래 경로에 있습니다 [3].

   ```
   */com.samsung.android.providers.trash/databases/trash.db*
   */data/media/*/Android/.Trash/*
   */storage/*/Android/.Trash/*
   ```

   `trashes` 표의 열은 `_id`, `_data`, `original_path`, `title`, `_display_name`, `_size`, `mime_type`, `delete_package_name`, `user_id`, `date_deleted`, `date_expires`, `extra` 이고, `date_deleted` 와 `date_expires` 는 유닉스 밀리초라서 1000 으로 나눠 UTC 로 바꿉니다 [3]. `original_path` 는 휴지통에 넣기 전 위치, `delete_package_name` 은 지우기를 시작한 앱입니다 [3]. `_data` 가 가리키는 휴지통 파일이 남아 있으면 내용을 되찾은 것이고, 파일은 없고 행만 남아 있으면 "이 이름·크기의 파일이 이 경로에 있었다" 는 흔적까지만 얻습니다. 갤러리 앱 쪽 휴지통 기록은 [삼성 갤러리](../../02-artifacts/media/samsung-gallery.md) 에서 봅니다.

3. **대화 앱 DB 에서 삭제 표시가 붙은 행을 찾습니다.** 앱에 따라 행을 바로 지우지 않고 삭제 시각이나 삭제 표시 열만 채우는 경우가 있어, 표와 열 이름은 앱마다 [문자](../../02-artifacts/communications/messages/index.md), [카카오톡](../../02-artifacts/messengers/kakaotalk/index.md), [연락처](../../02-artifacts/communications/contacts.md) 같은 앱 페이지에서 확인합니다. `settings global` 에 `contact_setting_trash_bin_on` 키가 있을 수 있지만, 값의 뜻은 실제 기기로 확인해야 합니다.

4. **DB 파일 안에 남은 조각을 찾되 기대치를 낮춥니다.** 현행 AOSP 의 플랫폼 SQLite 는 `-DSQLITE_SECURE_DELETE`, `-DSQLITE_DEFAULT_AUTOVACUUM=1`, `-DSQLITE_DEFAULT_JOURNAL_SIZE_LIMIT=1048576` 으로 빌드하고, 두 번째 설정은 DB 를 자동 비우기(auto-vacuum) 대상으로 만듭니다 [4]. 이 설정대로라면 플랫폼 SQLite 로 만든 DB 는 지운 레코드를 0 으로 덮고 빈 페이지를 잘라 낸다고 해석할 수 있습니다. 다만 저널 크기 한도는 저널·WAL 파일을 비울 때 크기를 1MiB 로 줄이는 설정이지 그 안의 옛 페이지를 지우는 설정이 아니라서, `-wal` 파일에는 지우기 전 페이지가 남아 있을 수 있으니 본 DB 와 함께 확보합니다. 그래서 문자·연락처 같은 시스템 제공자 DB 의 빈 공간에서 되살릴 것이 적더라도 "지운 것이 없었다" 로 읽지 않습니다. 앱이 자체 SQLite 를 넣어 쓰는지, 그 설정이 어떤지는 앱마다 다르니 따로 확인합니다. `settings global` 에 `sqlite_compatibility_wal_flags` 키가 있을 수 있습니다. WAL 파일과 빈 공간을 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 와 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.

5. **알림에 남은 내용을 확인합니다.** `dumpsys notification` 의 대화 앱 알림 항목에는 `android.title` 과 `android.text` 필드가 있어, 대화를 앱에서 지운 뒤에도 알림에 제목과 본문이 남아 있을 수 있습니다. 알림 기록 파일의 위치와 보관 기간은 [알림 기록](../../02-artifacts/app-usage/notification-history.md) 에서 봅니다.

6. **어느 앱으로 지웠는지 좁힙니다.** 휴지통의 삭제 시각 전후로 usagestats 에서 앞에 있던 앱(`ACTIVITY_RESUMED` 등)을 보면 지울 때 쓴 앱을 좁힐 수 있고 [1], 삼성 휴지통의 `delete_package_name` 과 맞춰 봅니다 [3]. 이 단계는 [폰 사용 시간 재구성](usage-time.md) 에서 찾은 구간을 그대로 씁니다.

7. **되찾은 것과 흔적만 남은 것을 나눠 정리합니다.** 항목마다 "내용을 되찾음(파일·행)", "메타데이터만 남음(이름·경로·크기·시각)", "다른 곳에 남은 조각(알림 등)" 가운데 어디에 드는지 적고, 근거 파일과 필드를 함께 남깁니다.

> 그림 자리: 위에서 아래로 "휴지통 파일(내용 있음)", "휴지통 DB 행(메타데이터)", "앱 DB 삭제 표시", "SQLite 빈 공간·저널", "알림" 을 놓고, 아래로 갈수록 되찾을 수 있는 양이 줄어드는 모양을 보여 주는 그림

## 흔한 오판

**`.trashed-` 파일을 "이미 지워진 파일의 흔적" 으로만 보는 경우**가 있습니다. 휴지통 파일은 이름만 바뀐 원본이라서, 내용을 그대로 확보할 수 있는 1순위 대상입니다 [2].

**휴지통 이름의 숫자에서 30일을 뺀 값을 지운 시각으로 확정하는 오판**도 흔합니다. 연장 기간이 따로 있어 [2] 이 셈은 항상 맞지 않습니다.

**`/sdcard` 나열 결과에 `.Trash` 나 `.trashed-` 가 없다고 휴지통이 비었다고 보는 경우**도 조심합니다. 숨김 항목까지 나열했는지부터 확인합니다.

**SQLite 빈 공간에서 아무것도 나오지 않았다고 삭제가 없었다고 보는 오판**이 있습니다. 플랫폼 SQLite 설정이 지운 레코드를 덮도록 되어 있어 [4], 빈 공간이 비어 있는 것이 정상일 수 있습니다.

**도구가 0행을 보여 준 것을 "휴지통 기록 없음" 으로 적는 경우**도 있습니다. ALEAPP 의 삼성 휴지통 시험 자료도 행이 0개인 경우를 포함하고 [3], 경로 패턴이 실제 기기와 맞지 않아도 0행이 나오니 원본 경로를 직접 확인합니다. 도구 결과를 확인하는 법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에 있습니다.

## 보고서 문장 예

| 쓰지 않을 문장 | 쓸 문장 |
|---|---|
| 피의자가 사진을 삭제했다. | `DCIM` 폴더에 `.trashed-` 로 시작하는 파일이 있고, 이 파일은 MediaStore 휴지통으로 옮겨진 파일의 이름 규칙을 따릅니다. 파일 이름의 만료 예정 시각은 UTC ○○일 ○○:○○이고, 파일 내용은 그대로 확보했습니다. |
| 피의자가 갤러리 앱으로 사진을 지웠다. | 삼성 휴지통 DB(`trash.db`)의 `trashes` 표에 원래 경로 ○○, 지우기를 시작한 앱 ○○, 삭제 시각 UTC ○○일 ○○:○○인 행이 있습니다. 이 행에 대응하는 휴지통 파일은 확보한 자료에서 찾지 못했습니다. |
| 지운 대화 내용은 ○○이다. | 대화 앱 ○○의 알림 기록에 제목 ○○, 본문 ○○인 알림이 ○○:○○에 생성된 기록이 있습니다. 같은 내용의 행은 앱 DB 에서 찾지 못했습니다. |

보고서 전체의 틀은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 아티팩트 본문: [미디어 저장소](../../02-artifacts/media/mediastore/index.md), [삼성 갤러리](../../02-artifacts/media/samsung-gallery.md), [알림 기록](../../02-artifacts/app-usage/notification-history.md), [문자](../../02-artifacts/communications/messages/index.md), [카카오톡](../../02-artifacts/messengers/kakaotalk/index.md)
- 메모 앱의 삭제 표시: [삼성 노트](../../02-artifacts/samsung/samsung-notes.md), [구글 Keep](../../02-artifacts/google-services/keep.md)
- 기반 구조: [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), [공용 저장 공간](../../01-foundations/storage/shared-storage.md)
- 기법: [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md), [도구 검증](../../03-techniques/reporting/tool-validation.md)
- 이어지는 시나리오: [증거를 없애려 했나](anti-forensics/index.md), [폰 사용 시간 재구성](usage-time.md)

## 참고 문헌

1. UsageEvents.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/usage/UsageEvents.java
2. FileUtils.java — AOSP packages/providers/MediaProvider (main) — https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/util/FileUtils.java
3. ALEAPP SamsungTrash.py — abrignoni/ALEAPP (main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/SamsungTrash.py
4. Android.bp — AOSP external/sqlite dist (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_external_sqlite/main/dist/Android.bp
