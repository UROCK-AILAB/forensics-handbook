---
title: "최근 앱 화면"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 510
---

# 최근 앱 화면 (Recents·Snapshots)

## 한 줄 요약

최근 앱 화면 (Recents) 기록은 최근 앱 목록에 오른 태스크(task)마다 어떤 앱의 어떤 화면이었는지와 마지막으로 쓴 시각을 XML 로 남기고, 스냅샷 (Snapshots) 폴더에는 그 태스크 화면의 한 순간을 이미지로 남깁니다 [1].

## 무엇을 기록하나 · 왜 생기나

최근 앱 버튼을 누르면 방금 쓰던 앱들이 화면 미리보기와 함께 나열되고, 시스템은 이 목록과 미리보기에 쓰는 태스크 정보와 화면 그림을 파일로도 남깁니다. ALEAPP 는 이 저장물을 세 갈래로 읽습니다 [1]. `recent_tasks` 에는 태스크마다 XML 이, `recent_images` 에는 태스크 설명 아이콘 그림이, `snapshots` 에는 화면 스냅샷 이미지와 그 속성 파일이 들어 있습니다 [1].

포렌식에서 특히 눈여겨볼 곳은 스냅샷 이미지입니다. 사용자가 앱을 닫거나 대화를 지운 뒤에도 그 앱의 화면 그림이 남아 있을 수 있어서, 앱 DB 에서 사라진 내용을 화면 모습으로 확인할 여지가 있습니다.

## 위치와 버전별 차이

ALEAPP 는 `system_ce` 아래의 세 하위 디렉터리를 찾고, `system_ce` 다음 칸은 사용자 번호입니다 [1].

```
/data/system_ce/<사용자ID>/recent_tasks/
/data/system_ce/<사용자ID>/recent_images/
/data/system_ce/<사용자ID>/snapshots/
```

경로가 사용자 번호로 나뉘어 있어서, 작업 프로필이나 보안 폴더를 쓰는 기기에서는 사용자 번호마다 폴더를 따로 봅니다. 사용자 번호를 읽는 법은 [사용자와 프로필 (Multi-user·users)](../system-account/users-profiles.md) 과 [보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md) 페이지에 있습니다. `/data/system_ce/<사용자ID>` 는 파일 기반 암호화에서 자격 증명 암호화 (Credential Encrypted, CE) 영역에 속하고, 이 영역은 사용자가 기기 잠금을 푼 뒤에만 쓸 수 있습니다 [2]. 재부팅 뒤 한 번도 잠금을 풀지 않은 기기에서는 이 폴더들을 읽을 수 없다는 뜻입니다. 암호화 영역의 구분은 [저장 공간 암호화 (Encryption)](../../01-foundations/storage/encryption/index.md) 에서 다룹니다.

| 기기 | 최근 앱 화면을 맡는 쪽 | 확인한 것 |
|---|---|---|
| AOSP | 확인하지 못함 | 경로와 파일 구성(ALEAPP 기준) [1] |
| 삼성 One UI | `com.sec.android.app.launcher` (One UI 홈) | 역할 패키지 이름만 확인 (확인 범위: Android 16, One UI 8.5) |

관찰 기기의 `dumpsys package` 출력에서 "Known Packages" 의 `Recents:` 역할은 `com.sec.android.app.launcher` 가 맡고 있었습니다 (확인 범위: Android 16, One UI 8.5). 최근 앱 화면을 그리는 앱이 삼성 홈이라는 뜻이지만, 삼성 기기에서 스냅샷 경로와 형식이 AOSP 와 다른지는 확인하지 못했습니다.

## 구조

### recent_tasks — 태스크 XML

ALEAPP 가 태스크 XML 에서 읽는 속성은 다음과 같습니다 [1]. 파일 이름이 어떤 형식인지는 확인하지 못했습니다. 이 XML 이 일반 XML 인지 안드로이드 바이너리 XML 인지도 확인하지 못했으니, 파일 앞부분이 글자로 읽히지 않으면 [안드로이드 바이너리 XML (ABX)](../../01-foundations/data-formats/abx.md) 페이지를 참고합니다.

| 속성 | 담긴 것 |
|---|---|
| `task_id` | 태스크 번호. 스냅샷 파일 이름과 이어짐 |
| `effective_uid`, `user_id` | 태스크를 연 앱의 UID, 사용자 번호 |
| `affinity`, `real_activity` | 태스크 소속과 실제 액티비티 이름 |
| `calling_package` | 태스크를 연 패키지 |
| `first_active_time`, `last_active_time`, `last_time_moved` | 시각 값 (유닉스 밀리초) |
| `task_description_icon_filename` | 설명 아이콘 파일 이름 |

자식 요소에서는 `action` 과 `component` 를 읽습니다 [1]. UID 를 패키지 이름으로 옮기는 법은 [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md) 페이지에 있습니다.

### snapshots — 화면 이미지와 속성

`snapshots` 안에는 태스크 번호로 이름 붙인 파일이 세 종류 있습니다 [1].

| 파일 | 담긴 것 |
|---|---|
| `{task_id}.jpg` | 고해상도 스냅샷 |
| `{task_id}_reduced.jpg` | 저해상도 스냅샷 |
| `{task_id}.proto` | 스냅샷 속성 |

폴더 안이 평평하게 놓인 경우와 한 단계 더 들어간 경우가 둘 다 있어서 도구도 두 구조를 모두 찾습니다 [1]. ALEAPP 가 `.proto` 에서 뽑는 칸은 Snapshot ID, Capture Time, Top Activity, Is Real Snapshot, Orientation, Rotation, Task Size, Windowing Mode, Translucency, Content/Letterbox Insets, Appearance, UI Mode 입니다 [1]. 각 칸의 필드 번호와 Capture Time 의 단위는 확인하지 못했습니다. 프로토콜 버퍼를 스키마 없이 읽는 법은 [프로토콜 버퍼 (Protocol Buffers)](../../01-foundations/data-formats/protobuf.md) 페이지에서 다룹니다.

### recent_images — 설명 아이콘

`recent_images` 의 그림은 태스크 XML 의 `task_description_icon_filename` 값으로 찾거나 `recent_images/{task_id}/` 디렉터리로 찾습니다 [1].

## 증거로서 의미

**증명하는 것**

태스크 XML 은 어떤 앱의 어떤 액티비티가 최근 앱 목록에 올라 있었는지, 그 태스크가 처음과 마지막으로 활성화된 시각이 언제인지를 알려 줍니다. 스냅샷 이미지는 그 태스크의 한 순간 화면 모습이고, 파일 이름의 `task_id` 로 태스크 XML 과 이어 붙이면 "이 앱의 이 화면이 이런 모습이었다" 까지 말할 수 있습니다. `calling_package` 는 어느 앱에서 이 태스크가 열렸는지 짐작하는 데 씁니다.

**증명하지 못하는 것**

스냅샷은 화면 그림일 뿐이라 그 순간 사용자가 화면을 봤는지, 화면에 나온 메시지를 보냈는지는 알려 주지 않습니다. 스냅샷 한 장이 그 태스크의 유일한 화면도 아니어서, 그 사이에 오간 다른 화면은 남지 않습니다. 태스크가 목록에 있다는 기록도 그 앱을 얼마나 오래 썼는지는 말하지 않으니 사용 시간은 [앱 사용 기록 (usagestats)](usagestats/index.md) 에서 구합니다.

## 시각 해석

태스크 XML 의 `first_active_time`, `last_active_time`, `last_time_moved` 는 유닉스 에포크 밀리초이고, ALEAPP 는 1000 으로 나눠 UTC 로 바꾸며 0 이나 빈 값은 비워 둡니다 [1]. 세 값이 각각 정확히 어떤 동작에서 바뀌는지는 소스로 확인하지 못했으니, 보고서에는 속성 이름을 그대로 적고 뜻을 넘겨짚지 않습니다. 스냅샷 속성의 Capture Time 은 단위를 확인하지 못했습니다.

스냅샷 이미지 파일의 파일 시스템 시각(수정 시각 등)도 참고할 수 있지만, 수집 과정에서 파일을 복사하며 바뀌지 않았는지 먼저 확인합니다. 시각 값 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

## 함정과 한계

첫째, 사용자가 최근 앱 목록에서 앱을 밀어 없애면 태스크와 스냅샷도 함께 지워질 수 있지만, 그 동작과 파일 삭제가 어떻게 이어지는지는 확인하지 못했습니다. 파일이 지워졌다면 파일 시스템 수준 복구를 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md) 에서 시도해 볼 수 있습니다.

둘째, 앱이 화면 보안 플래그(`FLAG_SECURE`)를 쓰면 스냅샷이 남지 않거나 가려진다는 설명이 흔하지만 이번에 확인하지 못했습니다. 은행·메신저 앱의 스냅샷이 비어 있다면 이 가능성을 열어 두고, 스냅샷이 없다는 사실만으로 앱을 안 썼다고 결론 내리지 않습니다.

셋째, 삼성 One UI 는 최근 앱 화면을 홈 앱이 맡습니다 (확인 범위: Android 16, One UI 8.5). AOSP 경로에서 아무것도 안 나오면 경로가 다를 가능성을 먼저 따집니다.

넷째, 스냅샷 이미지를 증거로 제시할 때는 원본 파일의 해시를 함께 남기고, 저해상도 판과 고해상도 판이 둘 다 있으면 둘 다 보존합니다.

## 직접 분석해 보기

### 파일로 한 번

1. 수집한 사본에서 `system_ce/<사용자ID>/snapshots` 폴더의 파일 목록을 뽑고 이름에서 태스크 번호를 모읍니다.
2. `recent_tasks` 의 XML 을 열어 `task_id` 가 같은 태스크를 찾고 `real_activity`, `effective_uid`, `last_active_time` 을 적습니다.
3. 같은 번호의 `.jpg` 를 열어 화면 내용을 보고, 저해상도 판만 있으면 그 사실을 적습니다.
4. `.proto` 는 스키마 없이 필드 번호와 값 종류만 풀어 볼 수 있습니다(방법은 프로토콜 버퍼 페이지). 필드 번호와 칸 이름의 짝은 확인하지 못했으니 도구 결과와 맞춰 봅니다.

`.jpg` 파일은 JPEG 파일 서명(`FF D8 FF`)으로 시작하는지 헥스 편집기로 먼저 확인하면, 확장자만 jpg 이고 내용이 다른 파일을 걸러 낼 수 있습니다.

### 공개 도구로 한 번

ALEAPP 의 recentactivity 모듈이 태스크 XML, 스냅샷 이미지, `.proto` 속성을 한 표로 묶어 줍니다 [1]. 도구가 짝지은 이미지와 태스크 번호가 위에서 손으로 맞춘 결과와 같은지 몇 건 확인합니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [앱 사용 기록 (usagestats)](usagestats/index.md) | `last_active_time` 근처에 같은 앱의 ACTIVITY_PAUSED·ACTIVITY_STOPPED 가 있는지 |
| [디지털 웰빙 (Digital Wellbeing)](digital-wellbeing.md) | 같은 앱이 같은 시간대에 앞에 있었는지 |
| [스크린샷과 화면 녹화 (Screenshots·Screen Recording)](../media/screenshots.md) | 사용자가 직접 찍은 화면과 스냅샷을 헷갈리지 않았는지 |
| [앱 데이터 분석 (App Data Analysis)](../../03-techniques/analysis/app-data-analysis/index.md) | 스냅샷에 보이는 대화·게시물이 앱 DB 에 남아 있는지 |

지운 대화를 찾는 흐름은 [지운 대화와 사진 찾기 (Deleted Content)](../../04-scenarios/activity/deleted-content.md) 에서 다룹니다.

## 실습

공개 안드로이드 검체(NIST CFReDS 등)의 `/data/system_ce/` 아래에 이 폴더들이 있으면 아래 질문을 풀어 봅니다.

1. 스냅샷이 남아 있는 태스크는 몇 개이고, 각각 어떤 앱의 어떤 액티비티입니까?
2. `last_active_time` 이 가장 늦은 태스크는 무엇이고, 그 시각은 UTC 로 언제입니까?
3. 스냅샷 이미지에 보이는 내용 가운데 해당 앱 DB 에 없는 것이 있습니까?

## 참고 문헌

1. ALEAPP — scripts/artifacts/recentactivity.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/recentactivity.py
2. Android Open Source Project — File-based encryption — https://source.android.com/docs/security/features/encryption/file-based
