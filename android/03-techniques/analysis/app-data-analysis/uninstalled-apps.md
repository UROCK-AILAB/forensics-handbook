---
title: "지운 앱이 남긴 흔적"
parent: "앱 데이터 분석"
grand_parent: "기법 · 분석"
nav_order: 1400
---

# 지운 앱이 남긴 흔적 (Uninstalled Apps)

## 한 줄 요약

앱을 지우면 앱 전용 저장소는 함께 지워지지만, 스토어 앱의 DB·시스템 기록·공용 저장소처럼 그 앱 밖에 적힌 기록에는 흔적이 남을 수 있어서 이런 곳을 차례로 찾아 설치됐던 앱을 되짚는 방법입니다.

## 언제 쓰나

지금 설치 목록에 없는 앱이 사건과 관련 있다고 의심될 때 씁니다. 앱을 지운 행위 자체가 증거 인멸 여부를 가리는 단서가 되기도 해서 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md) 조사에서 함께 쓰고, 지운 파일 자체를 되살리는 방법은 [삭제 데이터 복구 (Data Recovery)](../data-recovery/index.md) 페이지에서 다룹니다. 설치된 앱을 처음부터 분석하는 순서는 [처음 보는 앱 분석 순서](unknown-apps.md) 에 있습니다.

## 지울 때 사라지는 것

사용자가 앱을 지우면 내부 저장소와 외부 저장소의 앱 전용 폴더에 있던 파일이 지워집니다 [1]. 예외가 될 수 있는 속성이 매니페스트의 `android:hasFragileUserData` 이고, 앱을 지울 때 사용자에게 앱 데이터를 남길지 묻는 창을 띄울지를 정하며 기본값은 `"false"` 입니다 [2]. 이 속성이 켜진 앱을 사용자가 데이터를 남기는 쪽으로 지웠을 때 데이터가 어디에 어떤 상태로 남는지와, 이 속성이 몇 번째 API 수준부터 있었는지는 확인하지 못했습니다.

기기의 설치 기록인 packages.xml 에서 지운 앱의 항목이 곧바로 빠지는지도 확인하지 못했습니다. 공개 도구 ALEAPP 의 packageInfo 모듈은 현재 packages.xml 에 있는 항목만 보여 주어서 [3], 이 결과만으로는 지운 앱을 찾을 수 없습니다. 설치 기록 자체의 해석은 [설치된 앱 (packages.xml)](../../../02-artifacts/app-usage/packages/index.md) 페이지에 있습니다.

## 절차

1. **지금 설치된 앱 목록을 먼저 만듭니다.** packages.xml 이나 켜져 있는 기기의 패키지 목록으로 현재 설치된 패키지 이름을 모아 둡니다. 이 목록이 뒤 단계에서 "지금은 없는 이름" 을 가려내는 기준이 됩니다.

2. **Play 스토어 앱의 DB 를 봅니다.** 스토어 앱(`com.android.vending`)이 자기 폴더에 적은 DB 에는 기기 설치 기록과 따로 앱 이름이 남습니다. ALEAPP 가 읽는 두 DB 는 아래와 같습니다 [4][5].

   | DB | ALEAPP 가 찾는 경로 | 읽는 표와 칸 | 출력 칸 |
   |---|---|---|---|
   | frosting.db | `*/com.android.vending/databases/frosting.db*` | `frosting` 표의 `pk`(패키지 이름), `apk_path`, `last_updated` | Last Updated Timestamp, App Package Name, APK Path |
   | library.db | `*/com.android.vending/databases/library.db*` | `ownership` 표의 `purchase_time`, `account`, `doc_id` | User, Purchase Time, Account, Doc ID |

   frosting.db 의 `last_updated` 와 library.db 의 `purchase_time` 은 유닉스 밀리초이고, ALEAPP 는 `last_updated` 가 0 이면 빈칸으로 둡니다 [4][5]. ALEAPP 는 frosting.db 결과를 "App Updates (Frosting.db)" 라는 이름으로 보여 주고, library.db 는 Play 스토어 라이브러리의 앱 구매·소유 기록이라고 설명합니다 [4][5]. library.db 경로에서는 뒤에서 네 번째 부분을 사용자 번호로 쓰고, 그 값이 `data` 면(곧 `/data/data/...` 경로면) 사용자 0 으로 봅니다 [5]. 1단계 목록에 없는 패키지 이름이 이 두 DB 에 나오면 지운 앱 후보로 적습니다. 스토어 기록 전반은 [구글 플레이 기록 (Play Store)](../../../02-artifacts/app-usage/play-store.md) 페이지에 있습니다.

3. **앱 사용 기록을 봅니다.** usagestats 에는 패키지 이름이 이벤트와 누적 통계로 남고, 기간별 보관 기준은 해당 페이지에 있습니다. 앱을 지웠을 때 그 앱의 기록이 함께 지워지는지는 확인하지 못했고, 기록 해석은 [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) 페이지에 있습니다.

4. **계정 기록을 봅니다.** 관찰한 폰의 `dumpsys account` 출력에는 "Accounts History" 절이 있었고, 칸은 `AccountId`, `Action_Type`, `timestamp`, `UID`, `TableName`, `Key` 였습니다 (확인 범위: Android 16, One UI 8.5). 같은 폰에서 본 `Action_Type` 값은 아래와 같습니다 (확인 범위: Android 16, One UI 8.5).

   ```
   action_account_add
   action_account_remove
   action_called_account_add
   action_called_account_remove
   action_authenticator_remove
   action_clear_password
   ```

   `action_authenticator_remove` 는 이름으로 보면 인증기가 없어진 기록이지만, 인증기를 제공하던 앱을 지울 때 생기는 값인지는 확인하지 못했습니다. 계정 기록은 [계정 (Accounts)](../../../02-artifacts/system-account/accounts/index.md) 페이지에서 다룹니다.

5. **오류 기록을 봅니다.** 관찰한 폰의 `settings secure` 에는 `dropbox:data_app_crash`, `dropbox:data_app_anr`, `dropbox:data_app_wtf` 처럼 DropBox 관련 키가 있었습니다 (확인 범위: Android 16, One UI 8.5). DropBox 기록에 지운 앱의 이름이 남는지는 확인하지 못했고, ALEAPP 에는 이 기록을 읽는 androidDropbox.py 모듈이 있습니다 [6]. 오류 기록의 해석은 [앱 오류·종료 기록 (DropBox·tombstones·ANR)](../../../02-artifacts/app-usage/crash-records.md) 페이지에 있습니다.

6. **공용 저장소 폴더를 봅니다.** 앱이 DCIM·Download·Pictures 같은 공용 저장소에 쓴 파일은 앱 전용 저장소가 아니고, 앱을 지울 때 앱 전용 저장소처럼 함께 지워진다는 문장은 공식 문서에서 확인하지 못했습니다. 관찰한 폰에서는 표준이 아닌 폴더가 `/sdcard/DCIM` 아래 19개, `/sdcard/Pictures` 아래 11개, `/sdcard/Download` 아래 36개 있었습니다 (확인 범위: Android 16, One UI 8.5). 이런 폴더 가운데 앱 이름을 딴 것이 있고 그 앱이 1단계 목록에 없으면, 지운 앱을 가리키는 단서로 적습니다. 공용 저장소 구조는 [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md), 사진 파일은 [미디어 저장소 (MediaStore)](../../../02-artifacts/media/mediastore/index.md) 페이지를 봅니다.

7. **찾은 흔적을 한 시간 축에 올립니다.** 스토어 DB 의 시각, usagestats 의 마지막 이벤트, 계정 기록의 시각을 나란히 놓으면 앱이 언제까지 쓰였는지 범위를 좁힐 수 있고, 방법은 [타임라인 작성 (Timeline)](../timeline/index.md) 에 있습니다.

## 도구

ALEAPP 는 packageInfo, frosting, installedappsLibrary 결과를 "Installed Apps" 분류로 묶어 보여 줍니다 [3][4][5]. 폴더 목록에는 installedappsGass.py, installedappsVending.py, installSessions.py, packageRestrictions.py, packageUserStates.py 모듈도 있지만 [6], 각각 어떤 파일과 표를 읽는지는 열어 보지 않아 확인하지 못했습니다. 켜져 있는 기기에서는 관찰한 폰의 `dumpsys package` "Known Packages:" 절에 Uninstaller 역할의 값이 비어 있었습니다 (확인 범위: Android 16, One UI 8.5).

## 함정과 한계

스토어 앱의 DB 구조는 Google 이 공개 문서로 정해 두지 않아서 스토어 판마다 달라질 수 있고, ALEAPP 도 시험 자료마다 스토어 버전을 함께 적습니다(예: Android 16 Pixel 8 Pro 자료의 `com.android.vending` vc 85180930) [4][5]. 도구가 표나 칸을 찾지 못하면 DB 를 직접 열어 구조를 확인합니다.

library.db 의 `ownership` 표는 계정이 소유한 앱 기록이라서 지금 기기에 설치되지 않은 앱도 들어 있을 수 있다는 해석은 ALEAPP 설명에서 끌어낸 것이고, 실제로 지운 앱의 행이 남는지는 확인하지 못했습니다. frosting.db 에 지운 앱의 행이 남는지도 확인하지 못했습니다. 그래서 이 두 DB 에만 나오는 패키지는 "이 기기에서 지운 앱" 이 아니라 "스토어 기록에 이름이 있는 앱" 으로 적고, 이 기기에 설치됐었는지는 다른 기록으로 따로 확인합니다.

지워진 앱 전용 파일을 되살릴 수 있는지는 이 페이지의 출처로 확인하지 못했고, [저장 공간 암호화 (Encryption)](../../../01-foundations/storage/encryption/index.md) 와 [파일 시스템 (ext4·F2FS)](../../../01-foundations/storage/filesystems/index.md) 페이지를 봅니다.

## 결과를 어떻게 해석하나

지금 설치 목록에 없는 패키지 이름이 다른 기록에 나오면 "그 이름이 이 기록에 남아 있다" 까지가 기록이 말하는 범위입니다. 설치됐었다고 쓰려면 usagestats 이벤트처럼 이 기기에서 그 앱이 동작한 기록이 따로 있어야 하고, 사용자가 직접 지웠다고 쓰려면 지운 행위를 적은 기록이 필요합니다. 앱을 언제 썼는지 재구성하는 흐름은 [어떤 앱을 언제 썼나 (App Usage)](../../../04-scenarios/activity/app-usage.md) 페이지에 있습니다.

> 현재 packages.xml 에는 `(패키지 이름)` 항목이 없고, Play 스토어의 frosting.db 에 같은 패키지 이름의 행이 있으며 `last_updated` 는 (시각) UTC 입니다. 같은 기기의 앱 사용 기록에는 이 패키지의 마지막 이벤트가 (시각) UTC 에 있습니다.

## 참고 문헌

1. Access app-specific files — Android Developers, https://developer.android.com/training/data-storage/app-specific
2. `<application>` 매니페스트 요소 — Android Developers, https://developer.android.com/guide/topics/manifest/application-element
3. ALEAPP packageInfo.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/packageInfo.py
4. ALEAPP frosting.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/frosting.py
5. ALEAPP installedappsLibrary.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/installedappsLibrary.py
6. ALEAPP scripts/artifacts 폴더 목록(GitHub API) — https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
