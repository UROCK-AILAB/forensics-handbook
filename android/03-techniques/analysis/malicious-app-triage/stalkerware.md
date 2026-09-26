---
title: "감시 앱 흔적"
parent: "악성 앱 흔적 분석"
grand_parent: "기법 · 분석"
nav_order: 1510
---

# 감시 앱 흔적 (Stalkerware)

몰래 설치된 감시 앱 (stalkerware) 을 공개된 침해 지표 (Indicator of Compromise, IOC) 와 대조하고, 화면에 드러나지 않은 채 움직인 앱의 활동 흔적을 찾는 방법입니다.

## 언제 쓰나

상대가 내 위치나 대화를 알고 있다는 호소처럼 누군가 폰을 들여다본다는 의심이 있을 때 씁니다. 사건 전체를 어떤 순서로 조사하는지는 [몰래 설치된 감시 앱](../../../04-scenarios/incident/stalkerware.md) 시나리오에 있고, 이 페이지는 그 가운데 지표 대조와 활동 흔적 읽기를 다룹니다. 어떤 앱을 후보로 삼을지는 먼저 [권한과 설정으로 찾기](permissions-settings.md) 로 추려 두면 빠르고, 접근성 권한으로 앱이 할 수 있는 일과 Android 13 이상의 제한된 설정도 그 페이지에 있습니다.

## 공개 지표 목록

Echap 의 stalkerware-indicators 저장소는 Android 와 iOS 감시 앱의 지표를 모읍니다 [1]. 174개 앱을 다루고, 그 가운데 몰래 숨어 도는 감시 앱 (stalkerware) 이 147개, 숨지 않는 감시 앱 (watchware) 이 27개입니다 [1]. 앱 수는 저장소가 갱신되면 바뀝니다. 라이선스는 CC-BY 이고, MVT 가 이 지표를 씁니다 [1].

| 파일 | 담긴 것 |
|---|---|
| `ioc.yaml` | 앱 이름, 패키지 이름, Android 인증서, 웹사이트, 명령 서버 (C2) 도메인 |
| `watchware.yaml` | 숨지 않는 감시 앱 |
| `samples.csv` | 샘플 해시, 패키지 이름, 인증서, 버전 |
| `generated/` 아래 | `hosts`, `hosts_full`, `quad9_blocklist.txt`, `stalkerware.stix2`, `suricata.rules`, `misp_event.json`, `indicators-for-tinycheck.json`, `network.csv` |

`generated/` 아래 파일은 이름으로 보면 hosts 파일, STIX, Suricata 규칙, MISP 이벤트 같은 형식입니다. APK 해시와 인증서를 이 목록과 맞추는 방법은 [APK 확인](apk-check.md) 에 있습니다.

## 절차

1. **조치보다 수집을 먼저 합니다.** 감시 앱을 지우거나 끄면 설치한 사람이 알아챌 수 있다는 안내가 널리 쓰입니다. 지우기 전에 수집을 마쳐 두면 흔적을 잃지 않고, 앱을 지울지 말지는 수집을 마친 뒤 피해자와 함께 정합니다.
2. **설치된 패키지 이름을 지표와 대조합니다.** 기기의 패키지 목록을 `ioc.yaml` 과 `watchware.yaml` 의 패키지 이름과 맞춥니다. 패키지 이름과 UID 를 읽는 법은 [패키지 이름과 UID](../../../01-foundations/value-decoding/package-uid.md) 페이지에 있습니다.
3. **권한·설정 후보와 합칩니다.** [권한과 설정으로 찾기](permissions-settings.md) 에서 추린 후보와 2단계에서 걸린 앱을 한 목록으로 모읍니다.
4. **후보의 활동 흔적을 읽습니다.** 앱 사용 기록과 알림 기록에서 후보 패키지가 언제, 어떤 모양으로 움직였는지 봅니다. 아래 "활동 흔적 읽기" 를 봅니다.
5. **계정 변경 흔적을 봅니다.** 감시 앱이 들어온 무렵에 계정이 더해지거나 빠졌는지 봅니다. 아래 "계정 기록" 을 봅니다.
6. **네트워크 지표를 맞춥니다.** 네트워크 기록이 따로 있으면 `ioc.yaml` 의 명령 서버 도메인이나 `generated/` 의 목록과 맞춰 봅니다.
7. **APK 를 확인합니다.** 남은 후보는 [APK 확인](apk-check.md) 으로 해시와 서명 인증서를 봅니다.

## 활동 흔적 읽기

### 앱 사용 기록

`dumpsys usagestats` 이벤트에는 아래 종류가 있습니다.

| 이벤트 종류 | 함께 나오는 필드 |
|---|---|
| `FOREGROUND_SERVICE_START`, `FOREGROUND_SERVICE_STOP` | time, type, package, class, flags |
| `ACTIVITY_RESUMED`, `ACTIVITY_PAUSED`, `ACTIVITY_STOPPED` | package, class, instanceId, taskRootPackage, taskRootClass |
| `STANDBY_BUCKET_CHANGED` | package, standbyBucket, reason |
| `NOTIFICATION_INTERRUPTION` | channelId |
| `SHORTCUT_INVOCATION` | shortcutId |
| `KEYGUARD_SHOWN`, `KEYGUARD_HIDDEN` | — |
| `SCREEN_INTERACTIVE`, `SCREEN_NON_INTERACTIVE` | — |

같은 출력의 "In-memory daily stats" 에는 패키지마다 `totalTimeUsed`, `lastTimeUsed`, `totalTimeVisible`, `lastTimeVisible`, `lastTimeComponentUsed`, `totalTimeFS` 필드가 있습니다.

화면에 한 번도 보이지 않았는데 포그라운드 서비스 시작·종료 이벤트만 되풀이되는 패키지는 살펴볼 후보로 삼을 수 있습니다. 이는 추론이라서 후보를 고르는 데만 쓰고 결론의 근거로 쓰지 않습니다. dumpsys 출력의 `time` 값은 한글이 섞인 현지 표기로 찍히고, 이벤트 시각의 기준과 보존 기간은 [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) 페이지에서 봅니다.

### 알림 기록

`dumpsys notification` 의 NotificationRecord 에는 `pkg`, `importance`, `key`, `mCreationTimeMs`, `mVisibleSinceMs`, `mUpdateTimeMs` 필드가 있습니다. 늘 떠 있는 알림을 띄우는 앱을 찾을 때 이 필드들로 패키지와 알림이 만들어진 때를 볼 수 있습니다. dumpsys 출력 전반은 [dumpsys 출력](../../../02-artifacts/logs/dumpsys.md), 지난 알림은 [알림 기록](../../../02-artifacts/app-usage/notification-history.md) 페이지에 있습니다.

### 계정 기록

`dumpsys account` 에는 "Accounts History" 절이 있고, 필드 순서는 `AccountId, Action_Type, timestamp, UID, TableName, Key` 입니다. 동작 값으로는 `action_account_add`, `action_account_remove`, `action_called_account_add`, `action_called_account_remove`, `action_authenticator_remove`, `action_clear_password` 가 나옵니다. 필드 이름으로 보면 UID 필드로 어느 앱이 계정 동작을 불렀는지 좁혀 볼 수 있을 것으로 보입니다. 계정 기록의 해석은 [계정](../../../02-artifacts/system-account/accounts/index.md) 페이지에 있습니다.

## 도구

stalkerware-indicators 는 파일을 내려받아 패키지 이름·해시·인증서를 직접 맞춰 볼 수 있고, MVT 처럼 이 지표를 읽는 도구로도 쓸 수 있습니다 [1]. 사용 기록과 알림, 계정 기록은 adb 로 받은 dumpsys 텍스트에서 패키지 이름으로 찾습니다. 수집 도구의 흐름은 [악성 앱 흔적 분석](index.md) 허브에 있습니다.

## 함정과 한계

지표 목록은 누군가 찾아 올린 앱만 담습니다. 목록에 없다는 사실은 감시 앱이 없다는 뜻이 아니고, 새로 나온 앱이나 이름을 바꾼 변종은 빠져 있을 수 있어서 권한·설정과 활동 흔적을 함께 봐야 합니다.

`watchware.yaml` 의 앱은 숨지 않는 감시 앱이라, 걸렸다고 해서 몰래 설치했다는 뜻은 아닙니다. 당사자가 알고 쓰는 앱일 수도 있어서, 누가 설치했고 당사자가 알았는지는 다른 기록으로 판별해야 합니다.

런처에 아이콘이 없다고 해서 설치되지 않았다고 보지 않습니다. 설치 여부는 패키지 목록으로 확인합니다.

dumpsys 출력은 읽은 순간의 상태를 보여 주고, usagestats 의 "In-memory daily stats" 처럼 메모리에 있는 부분도 섞여 있습니다. 시간이 지나면 내용이 바뀌니 조사를 시작할 때 한 번에 받아 둡니다.

## 결과를 어떻게 해석하나

지표 대조로 걸린 결과는 "이 기기에 공개 목록의 감시 앱과 패키지 이름이 같은 앱이 설치되어 있다" 까지만 말합니다. 활동 흔적은 "이 기간에 이 패키지의 포그라운드 서비스 이벤트가 이만큼 기록되어 있다" 처럼 쓰고, 누가 설치했는지나 무엇을 빼 갔는지는 설치 시각, 계정 기록, 네트워크 기록 같은 다른 흔적이 함께 받쳐 줄 때만 씁니다.

## 참고 문헌

1. stalkerware-indicators — AssoEchap (GitHub), https://github.com/AssoEchap/stalkerware-indicators
