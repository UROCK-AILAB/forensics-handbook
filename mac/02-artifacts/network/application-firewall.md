---
title: "방화벽"
parent: "아티팩트 · 네트워크"
nav_order: 1670
---

# 방화벽 (Application Firewall)

macOS 방화벽 (Application Firewall) 은 들어오는 연결을 다루는 기능이고, 그 설정은 macOS 14 까지 `/Library/Preferences/com.apple.alf.plist` 에 남지만 macOS 15 Sequoia 부터는 plist 에 들어 있지 않아서, 조사할 때는 분석 대상의 macOS 버전부터 확인하고 방화벽이 켜져 있었는지, 관리 프로필로 강제한 설정이 있었는지를 봅니다.

## 무엇을 기록하나 · 왜 생기나

macOS 방화벽의 설정 항목은 모두 들어오는 (incoming) 연결에 대한 것입니다 [1]. 사용자나 관리자는 들어오는 연결을 모두 막거나, 내장 소프트웨어를 자동으로 허용하거나, 내려받은 서명된 소프트웨어를 자동으로 허용하거나, 앱마다 허용·거부를 따로 정할 수 있습니다 [1]. 스텔스 모드를 켜면 ICMP 탐색과 포트 스캔 요청에 응답하지 않습니다 [1].

설정은 사용자가 설정 화면에서 바꿀 수도 있고, 구성 프로필의 Firewall 페이로드를 직접 설치하거나 기기 관리 서비스로 넣을 수도 있습니다 [1]. 그래서 방화벽 상태를 볼 때는 로컬 설정과 관리 프로필 두 쪽을 함께 봅니다.

## 위치와 버전별 차이

| macOS 버전 | 설정이 있는 곳 |
|---|---|
| 14 Sonoma 까지 | `/Library/Preferences/com.apple.alf.plist` [2] |
| 15 Sequoia 부터 | plist 에 들어 있지 않습니다 [2]. 저장 위치는 실제 기기에서 확인 |

macOS 15 부터 방화벽 설정은 속성 목록 파일에 들어 있지 않습니다. `/Library/Preferences/com.apple.alf.plist` 를 고쳐 설정을 바꾸던 앱이나 작업 흐름은 `socketfilterfw` 명령행 도구를 쓰도록 바뀌어야 합니다 [2]. 이 도구의 전체 경로와 옵션은 그 맥에서 확인합니다.

관리 프로필의 Firewall 페이로드는 macOS 10.12 부터 쓸 수 있고, 페이로드 키 가운데 `AllowSigned` 와 `AllowSignedApp` 은 macOS 12.3 부터입니다 [3].

ForensicArtifacts `macos.yaml` 에는 방화벽 관련 정의가 없어서 [4], 이 정의에 기대는 수집 도구로 모은 자료라면 `com.apple.alf.plist` 가 빠지지 않았는지 확인합니다.

## 구조

### com.apple.alf.plist (macOS 14 까지)

속성 목록 파일이고 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)을 따릅니다. 이 파일 안의 키 이름은 실제 파일을 열어 확인하고, 나온 키와 값을 그대로 옮겨 적습니다.

### Firewall 페이로드 (`com.apple.security.firewall`)

페이로드 형식은 `com.apple.security.firewall` 이고, 시스템 범위 (system-scoped) 프로필에 들어 있어야 하며, 기기 채널로만 배포되고 직접 설치도 허용됩니다 [3]. 여러 프로필에 Firewall 페이로드가 있으면 가장 엄격한 설정들의 합집합을 씁니다 [3].

| 키 | 형태 | 뜻 |
|---|---|---|
| `EnableFirewall` | boolean, 필수 | 방화벽을 켭니다 |
| `BlockAllIncoming` | boolean | 들어오는 연결을 모두 막습니다 |
| `EnableStealthMode` | boolean | 스텔스 모드를 켭니다 |
| `Applications` | 배열 | 방화벽이 연결을 통제하는 앱 목록이고, 항목마다 `Firewall.ApplicationsItem` 사전입니다 |
| `AllowSigned` | boolean, macOS 12.3+ | 내장 소프트웨어의 들어오는 연결을 허용합니다. 없으면 true |
| `AllowSignedApp` | boolean, macOS 12.3+ | 내려받은 서명된 소프트웨어가 들어오는 연결을 받도록 허용합니다. 없으면 true |

`Firewall.ApplicationsItem` 사전 안의 키는 실제 프로필에서 확인합니다. 설치된 구성 프로필이 디스크 어디에 남는지는 [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `com.apple.alf.plist` 나 설치된 Firewall 페이로드는 그 시점에 방화벽이 어떻게 설정되어 있었는지 알려 줍니다. 페이로드에 `EnableFirewall` 이 true 이고 `BlockAllIncoming` 이 true 라면 관리 프로필이 들어오는 연결을 모두 막도록 설정했다는 기록입니다 [3]. 다만 Firewall 페이로드가 든 프로필이 여러 개라면 시스템이 가장 엄격한 설정들의 합집합을 쓰기 때문에 [3], 프로필 하나만 보고 적용된 설정을 정하지 않습니다.

**증명하지 못하는 것.** 방화벽 설정 항목은 들어오는 연결을 다루는 것이라 [1], 방화벽이 켜져 있었다는 사실로 나가는 연결을 막았다고 쓰지 않습니다. 설정 기록만으로는 특정 연결이 실제로 막혔는지, 누가 언제 설정을 바꿨는지도 알 수 없습니다. 연결이 실제로 막혔는지는 다른 기록으로 따로 입증합니다.

방화벽을 끄거나 특정 앱을 허용 목록에 넣은 설정은 원격 접속이나 악성 코드의 수신 대기를 쉽게 만든 흔적일 수 있지만, 이 해석은 설정의 뜻에서 끌어낸 판단입니다. 보고서에는 "macOS 14 인 이 맥의 `com.apple.alf.plist` 에 이런 값이 있고, 파일 수정 시각은 이때다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

방화벽 설정과 Firewall 페이로드 키에는 시각 값이 없습니다. macOS 14 까지는 `com.apple.alf.plist` 의 파일 수정 시각과 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)의 해당 경로 기록으로 설정이 바뀐 무렵을 좁히고, 파일 수정 시각은 마지막으로 바뀐 때만 알려 준다는 점을 함께 적습니다. 관리 프로필은 프로필이 설치된 시각을 기준으로 따지고, 그 기록은 구성 프로파일 페이지를 따릅니다. 시각 값의 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다.

## 함정과 한계

- **macOS 15 의 변화.** macOS 15 부터 설정이 plist 에 들어 있지 않아서 [2], `com.apple.alf.plist` 가 없거나 옛 값만 남아 있어도 방화벽이 꺼져 있었다고 단정하지 않습니다. 업그레이드한 맥이라면 남은 plist 가 업그레이드 전 설정일 수 있다는 점도 적습니다.
- **들어오는 연결만.** 방화벽 설정 항목은 모두 들어오는 연결을 다뤄서 [1], 나가는 통신을 막는 기능으로 설명하면 틀립니다.
- **로컬 설정과 관리 프로필.** Firewall 페이로드가 여러 프로필에 있으면 가장 엄격한 설정들의 합집합을 쓰고 [3], 로컬 설정과 관리 프로필이 서로 다를 때 어느 쪽이 적용되는지는 설정 기록만으로 단정할 수 없습니다. 그래서 로컬 plist 만 보고 방화벽 상태를 판단하지 않고 두 쪽을 함께 적습니다.
- **떠도는 키 이름.** `com.apple.alf.plist` 의 키 이름은 여러 자료에 돌아다니지만 근거가 분명하지 않습니다. 도구가 키에 뜻을 붙여 보여 주면 그 근거를 확인한 뒤에 씁니다.
- **수집 정의의 빈틈.** ForensicArtifacts 정의에 방화벽 항목이 없어서 [4], 자동 수집 결과에 설정 파일이 없을 수 있습니다.

### 실제 데이터로 확인할 것

| 항목 | 상태 |
|---|---|
| macOS 15 이후 설정 저장 위치 | 실제 데이터로 확인 |
| `socketfilterfw` 의 전체 경로와 옵션 | 실제 데이터로 확인 |
| `com.apple.alf.plist` 의 키 이름 | 실제 데이터로 확인 |
| 방화벽 로그(`/var/log/appfirewall.log`, 통합 로그 서브시스템 등) | 실제 데이터로 확인 |
| `Firewall.ApplicationsItem` 안의 키 | 실제 데이터로 확인 |

## 직접 분석해 보기

먼저 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../system-account/os-version-install-history.md)에서 분석 대상의 macOS 버전을 확인하고, 14 이하라면 `com.apple.alf.plist` 를 파일 시각을 지키는 방식으로 복사해 사본으로 봅니다.

### 헥스로 한 번

`com.apple.alf.plist` 를 헥스 편집기로 열어 바이너리 plist 인지 XML 인지 첫 바이트로 판별하고, 바이너리라면 오프셋 표를 따라 키 문자열이 든 객체를 찾아갑니다. 머리말과 오프셋 표를 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에서 다루고, 이 파일에서는 실제 파일의 바이트를 그대로 기록합니다.

관리 프로필 쪽은 아래처럼 페이로드 키 [3]로 만든 예시와 설치된 프로필의 내용을 맞춰 봅니다. 실제 데이터에서 나온 값이 아니고, 페이로드의 나머지 공통 키는 생략했습니다.

```xml
<dict>
    <key>EnableFirewall</key>
    <true/>
    <key>BlockAllIncoming</key>
    <false/>
    <key>EnableStealthMode</key>
    <true/>
    <key>AllowSigned</key>
    <true/>
    <key>AllowSignedApp</key>
    <false/>
</dict>
```

이 예시라면 방화벽을 켜고 스텔스 모드를 켜되, 내장 소프트웨어는 허용하고 내려받은 서명된 소프트웨어의 자동 허용은 끈 설정으로 읽습니다 [3].

### 공개 도구로 한 번

macOS 14 이하인 기기는 macOS 의 `plutil` 로 사본을 열어 키와 값을 모두 옮겨 적습니다.

```
plutil -p com.apple.alf.plist
```

macOS 15 이후 맥을 켠 채로 조사한다면 `socketfilterfw` 로 설정을 확인할 수 있지만 [2], 옵션은 그 맥에서 도구의 도움말로 확인한 뒤 명령과 출력을 그대로 기록합니다. 켠 채로 조사하는 절차는 [라이브 대응 (Live Response)](../../03-techniques/process-acquisition/live-response/index.md)을 따릅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md) | Firewall 페이로드가 설치되어 있었는지와 설치 시각 |
| [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../system-account/os-version-install-history.md) | 설정을 plist 에서 찾을 버전인지, 업그레이드 시점 |
| [원격 접속 (Remote Access)](remote-access/index.md) | 들어오는 연결을 받는 원격 접속 기능이 켜져 있었는지 |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | `com.apple.alf.plist` 가 바뀐 무렵 |
| [통합 로그에서 찾을 것 (Unified Log Events)](../logs/unified-log-events/index.md) | 설정 변경과 같은 무렵의 로그 |
| [원격 접속 침입 확인 (Remote Intrusion)](../../04-scenarios/incident/remote-intrusion.md) | 방화벽 설정을 침입 경로와 함께 따지는 흐름 |

## 실습

공개 시험 데이터(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 그 이미지의 macOS 버전은 무엇이고, 그 버전에서 방화벽 설정을 plist 에서 찾을 수 있나요?
2. `com.apple.alf.plist` 가 있다면 키와 값을 모두 표로 옮기고, 파일 수정 시각을 함께 적어 보세요.
3. 설치된 구성 프로필 가운데 페이로드 형식이 `com.apple.security.firewall` 인 것이 있나요? 있다면 `EnableFirewall`, `BlockAllIncoming`, `EnableStealthMode` 값을 적어 보세요.
4. Firewall 페이로드가 든 프로필이 여러 개라면, 합집합 규칙으로 어떤 설정이 적용됐을지 정리해 보세요.

## 참고 문헌

1. Apple Platform Security, "Firewall security in macOS" — https://support.apple.com/guide/security/firewall-security-in-macos-seca0e83763f/web
2. Apple Developer, macOS Sequoia 15 Release Notes — https://developer.apple.com/documentation/macos-release-notes/macos-15-release-notes
3. Apple Developer, Device Management — Firewall — https://developer.apple.com/documentation/devicemanagement/firewall
4. ForensicArtifacts `macos.yaml` — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
