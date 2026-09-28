---
title: "권한 변경 흔적"
parent: "개인 정보 보호 권한"
grand_parent: "아티팩트 · 자격 증명·권한"
nav_order: 1840
---

# 권한 변경 흔적 (Changes)

TCC.db `access` 표의 행마다 마지막으로 바뀐 시각(`last_modified`)이 남고, macOS 11부터는 그 상태를 누가 정했는지(`auth_reason`)도 함께 남아서, 권한이 언제 누구 쪽 결정으로 지금 상태가 됐는지는 읽을 수 있지만, 그 전 상태는 이 표만으로 알기 어렵습니다 [2][3].

## 무엇을 기록하나

`access` 행의 `last_modified`는 그 권한 행이 마지막으로 바뀐 때이고, 공개 도구들은 이 값을 타임라인의 기준 시각으로 씁니다. APOLLO는 `tcc_db` 모듈의 기준 시각(KEY_TIMESTAMP)을 LAST MODIFIED로 두고 [2], Jamf Aftermath는 행을 `last_modified` 내림차순으로 정렬한 뒤 시각·권한 상태·서비스·클라이언트를 한 줄로 묶어 사건 흐름(storyline)에 넣는데, 권한 상태와 서비스는 숫자나 원래 문자열이 아니라 Aftermath 대응표의 이름(예: `allowed`, `fda`)으로 바뀌어 들어갑니다 [3].

```text
시각,tcc_(auth_value 이름),서비스 이름,클라이언트
```

열 구조와 버전 판별은 [권한 DB 구조](tcc-db.md)에, `auth_value`·`auth_reason` 값의 이름은 [권한 기록 해석](interpretation.md)에 있습니다.

## 시각 해석

`last_modified`는 1970-01-01 기준 초인 유닉스 시각이라서 UTC로 읽고, 보고서에는 현지 시각으로 바꾼 값과 함께 원래 값을 적습니다. 2001년 기준인 맥 절대 시각으로 잘못 읽으면 31년 늦은 날짜가 나와서, 값이 앞뒤 사건보다 크게 벗어나면 기준점부터 다시 확인합니다. 시각 값의 기준점은 [맥의 시각 값](../../../01-foundations/value-decoding/mac-time-values.md)에 정리돼 있습니다.

이 값이 상태 값이 바뀔 때만 갱신되는지, 알림창을 다시 띄우는 것 같은 다른 일에도 갱신되는지 단정할 수 없어서, 보고서에는 "이 행이 마지막으로 기록된 시각" 정도로만 씁니다.

## 누가 바꿨나

macOS 11 이상에서는 `auth_reason`으로 사용자 응답(2, userConsent)과 사용자 설정(3, userSet), 시스템 설정(4, systemSet), MDM 정책(6, mdmPolicy), 재정의 정책(7, overridePolicy) 같은 출처를 가를 수 있습니다 [3]. 이 이름은 Aftermath 소스의 대응이고 Apple 공식 정의가 아니라는 점은 [권한 기록 해석](interpretation.md)에서 다룹니다.

## MDM이 준 권한

기업 맥에서는 MDM이 사용자에게 묻지 않고 PPPC 프로파일(`com.apple.TCC.configuration-profile-policy`)로 권한을 미리 줍니다. PPPC는 macOS 10.14부터 쓸 수 있고, 기기 채널로 설치되며 여러 개를 함께 둘 수 있습니다 [1]. 프로파일의 권한 항목에는 아래 키가 들어갑니다 [1].

| 키 | 내용 |
|---|---|
| `Identifier` | 번들 ID 또는 경로 |
| `IdentifierType` | `bundleID` 또는 `path` |
| `CodeRequirement` | `codesign -display -r -`로 얻은 코드 서명 요구 사항 |
| `StaticCode` | 스키마에 있는 키(이 페이지에서는 뜻을 다루지 않음) |
| `Allowed` | 허용 여부(불린) |
| `Authorization` | macOS 11.0부터, `Allow`·`Deny`·`AllowStandardUserToSetSystemService` 중 하나 |

`Allowed`와 `Authorization`은 둘 중 하나만 씁니다. 여러 프로파일이 서로 부딪히면 가장 제한적인 설정, 곧 거부가 적용됩니다 [1]. 카메라(`Camera`)와 마이크(`Microphone`)는 프로파일로 허용할 수 없고 거부만 할 수 있으며, 입력 모니터링(`ListenEvent`)과 화면 기록(`ScreenCapture`)도 프로파일로는 거부만 됩니다. 이 두 서비스는 `AllowStandardUserToSetSystemService`로 관리자 권한이 없는 일반 사용자도 직접 허용할 수 있게 열어 둘 수 있을 뿐입니다 [1]. 스키마는 `Camera`·`Microphone`·`Accessibility`·`SpeechRecognition`·`BluetoothAlways` 키를 macOS 27.0부터 사용 중단(deprecated)으로 표시하고 선언형 관리의 `Privacy` 설정을 쓰라고 안내하므로 [1], 그 이후 버전에서는 PPPC 프로파일만 찾지 말고 선언형 관리 설정도 함께 확인합니다.

`auth_reason`이 6인 행이 있으면 [구성 프로파일](../../persistence/configuration-profiles.md)의 설치 흔적에서 PPPC 프로파일을 찾아 `Identifier`와 서비스가 맞는지 대조합니다.

## 탐지에서 먼저 볼 행

Aftermath 작성자는 전체 디스크 접근(`SystemPolicyAllFiles`)·위치(`Liverpool`)·iCloud(`Ubiquity`)·공유(`ShareKit`)를 "critical"로, 손쉬운 사용(`Accessibility`)·키 입력 보내기(`PostEvent`)·입력 모니터링(`ListenEvent`)·화면 기록(`ScreenCapture`)·개발자 도구(`DeveloperTool`)를 "common"으로 묶습니다 [3]. 도구 작성자의 분류이지만, 사고 대응에서는 이 서비스들의 허용 행을 먼저 검토할 만합니다.

검토는 허용 행의 `last_modified`가 사고 의심 시간대 안에 있는지부터 보고, 이어서 `client`가 알려진 앱인지, 경로형이면 그 파일이 지금도 있고 서명이 어떤지 확인합니다. `auth_reason`이 MDM 정책(6)인데 PPPC 프로파일 흔적이 없거나, 프로파일로는 거부만 할 수 있는 서비스가 MDM 정책으로 허용돼 있는 것처럼 출처와 값이 어긋나는 행은 따로 표시해 두고, 마지막으로 같은 시간대의 앱 설치·실행 흔적과 맞춰 봅니다.

TCC.db를 직접 고쳐 권한을 넣었는지는 이 표만으로 판단할 수 없습니다. 출처와 값이 어긋나는 행을 찾더라도 조작이라고 단정하지 말고, 조작 가능성을 [권한 상승과 TCC 우회 흔적](../../../04-scenarios/incident/privilege-tcc-bypass.md)의 다른 흔적과 함께 따집니다.

## 증거로서 의미

`last_modified`는 이 권한 행이 적어도 그 시각에 지금 상태로 기록됐다는 것을 보여 주고, macOS 11 이상이면 `auth_reason`으로 그 기록이 사용자·시스템·MDM 가운데 어느 쪽에서 나왔는지도 보여 줍니다.

한 행에는 마지막 상태만 남는 것으로 보여서, 허용했다가 거부하고 다시 허용한 것 같은 이력은 이 표만으로 알 수 없을 가능성이 큽니다. 권한을 누가 눌렀는지, 권한을 받은 뒤 앱이 실제로 무엇을 했는지도 이 기록으로는 알 수 없습니다.

## 함정과 한계

`tccutil reset`으로 권한을 지웠을 때 남는 흔적과 TCC 판단이 통합 로그에 남는 모양은 시험 기기에서 재현해 확인합니다. 행이 없다는 사실만으로 권한을 준 적이 없다고 말하지 않습니다.

지난 상태를 알고 싶으면 [스냅숏과 백업 비교](../../../03-techniques/analysis/snapshot-diff.md)의 방법으로 [타임 머신](../../filesystem/time-machine/index.md) 백업이나 스냅숏 안의 TCC.db 사본을 지금 파일과 비교합니다. 사본마다 같은 `service`·`client` 짝의 값과 `last_modified`가 어떻게 달라졌는지 보면 이력을 일부 되살릴 수 있습니다. 파일 자체를 지우거나 바꿔치기한 흔적은 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 직접 분석해 보기

권한 변경을 시간순으로 뽑는 SQL은 아래와 같습니다(macOS 11 이상 구조). 시각 변환은 [권한 DB 구조](tcc-db.md)에서 본 공개 도구의 방식과 같습니다.

```sql
SELECT DATETIME(last_modified, 'UNIXEPOCH') AS last_modified_utc,
       service, client, auth_value, auth_reason
FROM access
WHERE auth_value = 2
  AND service IN ('kTCCServiceSystemPolicyAllFiles', 'kTCCServiceAccessibility',
                  'kTCCServicePostEvent', 'kTCCServiceListenEvent',
                  'kTCCServiceScreenCapture', 'kTCCServiceDeveloperTool')
ORDER BY last_modified;
```

공개 도구로는 APOLLO `tcc_db` 모듈이나 Aftermath의 `tcc.csv`·storyline 출력을 쓰면 다른 아티팩트와 한 타임라인에 합치기 쉽습니다 [2][3]. 보고서에는 기록으로 확인되는 만큼만 씁니다.

> 사용자 A의 TCC.db에 앱 `/Users/A/Downloads/example`의 화면 기록(`kTCCServiceScreenCapture`) 권한이 허용(`auth_value` 2) 상태로 있고, 이 행의 마지막 기록 시각은 2026-01-01 10:00:00 UTC이며, 기록된 사유 값은 3(Aftermath 대응표에서 userSet)입니다.

위 문장의 경로와 시각은 문장 틀을 보이려고 만든 예시입니다.

## 교차 검증

- [구성 프로파일 (Configuration Profiles·MDM)](../../persistence/configuration-profiles.md) — MDM 정책 사유 행의 출처
- [설치한 앱과 영수증 (Applications·Receipts)](../../system-account/installed-apps-receipts.md) — 권한을 받은 앱이 언제 설치됐는지
- [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md) — 같은 시간대의 시스템 사건
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)
- [권한 상승과 TCC 우회 흔적 (Privilege·TCC Bypass)](../../../04-scenarios/incident/privilege-tcc-bypass.md)
- [정보 탈취 악성 코드 (Infostealer)](../../../04-scenarios/incident/infostealer.md)

## 실습

1. TCC.db의 모든 행을 `last_modified` 순으로 늘어놓고, 가장 최근에 바뀐 행 다섯 개가 어떤 서비스와 앱인지 적어 봅니다.
2. `auth_reason`이 6인 행이 있으면 같은 이미지에서 PPPC 프로파일을 찾아 `Identifier`·`IdentifierType`·`Authorization` 값과 대조해 봅니다.
3. 백업이나 스냅숏 안에 TCC.db 사본이 있으면 지금 파일과 비교해 새로 생기거나 값이 바뀐 행을 찾아봅니다.

## 참고 문헌

1. Apple device-management 저장소, PPPC 프로파일 스키마 com.apple.TCC.configuration-profile-policy.yaml — https://raw.githubusercontent.com/apple/device-management/release/mdm/profiles/com.apple.TCC.configuration-profile-policy.yaml
2. APOLLO 모듈 tcc_db.txt (Sarah Edwards, mac4n6) — https://github.com/mac4n6/APOLLO/blob/master/modules/tcc_db.txt
3. Jamf Aftermath 소스 analysis/DatabaseParser.swift — https://github.com/jamf/aftermath/blob/main/analysis/DatabaseParser.swift
