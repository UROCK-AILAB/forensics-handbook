---
title: "커널·시스템 확장"
parent: "아티팩트 · 자동 실행·지속성"
nav_order: 630
---

# 커널·시스템 확장 (KEXT·System Extension)

## 한 줄 요약

커널 확장 (Kernel Extension, kext)은 커널 안에서 도는 코드이고 시스템 확장 (System Extension)은 macOS 10.15부터 그 역할을 사용자 공간으로 옮긴 확장이라서, 둘 다 시스템 전체에 영향을 주는 자리이고 macOS 11 이후에는 적재 조건과 보안 수준 설정 자체가 조사 단서가 됩니다.

## 무엇을 기록하나 · 왜 생기나

kext는 장치 드라이버나 보안 제품처럼 커널 수준의 기능이 필요한 코드를 커널에 올리는 방식이고, 한 번 올라가면 시스템 전체에서 가장 높은 권한으로 돕니다. Apple은 macOS 10.15부터 시스템 확장을 들여와, 같은 종류의 기능을 커널이 아닌 사용자 공간에서 DriverKit·NetworkExtension·EndpointSecurity 같은 프레임워크로 구현하게 했습니다 [1][2].

그래서 조사에서는 두 가지를 봅니다. 하나는 kext 파일이 놓인 폴더와 그 kext를 올리기 위해 바꿔야 했던 보안 설정이고, 다른 하나는 시스템 확장을 사용자 승인 없이 허용하는 MDM 구성입니다. 이 페이지는 두 가지의 위치·조건·해석을 다루고, 서명과 무결성 보호 자체는 [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../01-foundations/protection/codesign-notarization-sip.md)에서, 구성 프로파일 전반은 [구성 프로파일 (Configuration Profiles·MDM)](configuration-profiles.md)에서 다룹니다.

## 위치와 버전별 차이

### 위치

| 경로·명령 | 설명 | 출처 |
|---|---|---|
| `/Library/Extensions/*` | kext 파일 | [4] |
| `/System/Library/Extensions/*` | kext 파일 | [4] |
| `/usr/sbin/kextstat` | 적재된 kext 목록을 보는 명령 | [4] |

macOS 11 이후 적재된 kext 목록을 보는 다른 명령이 `kextstat` 을 대신하는지, 시스템 확장의 상태가 어느 파일에 저장되는지, kext 승인 기록이 어느 DB에 남는지, 인텔 맥에서 보조 커널 컬렉션 파일이 데이터 볼륨의 어느 경로에 있는지는 조사 대상 버전의 실제 데이터로 확인합니다.

### 버전별 차이

| macOS | 달라진 점 | 출처 |
|---|---|---|
| 10.13 이후 | 10.13을 설치할 때나 그 뒤에 설치한 kext는 올릴 때 사용자 동의가 필요함 (사용자 승인 kext 적재, User-Approved Kernel Extension Loading) | [2] |
| 10.15 이후 | 시스템 확장 도입, MDM 페이로드 `com.apple.system-extension-policy` 사용 가능 | [1][2][3] |
| 11 이후 | kext를 필요할 때 바로 적재하지 못하고, 보조 커널 컬렉션 (Auxiliary Kernel Collection, AuxKC)으로 합쳐 부팅 때 적재 | [1][2] |
| 12 이후 | 페이로드 키 `RemovableSystemExtensions` 추가 | [3] |
| 15 이후 | 페이로드 키 `NonRemovableSystemExtensions`·`NonRemovableFromUISystemExtensions` 추가 | [3] |

### macOS 11 이후 kext를 올리는 조건

macOS 11 이후 kext는 AuxKC에 합쳐져야 올라가고, AuxKC를 다시 만들려면 사용자 승인과 재시동이 필요하며 보안 부팅을 "보안 수준 낮춤 (Reduced Security)" 으로 설정해야 합니다 [2]. 이 조건은 Apple 실리콘 맥의 조건이고 [2], 인텔 맥에도 같은 조건이 걸리는지는 실제 기기로 확인합니다. Apple 실리콘 맥에서는 시동할 때 전원 버튼을 눌러 복구 모드(1TR)로 들어간 뒤 Reduced Security로 낮추고 커널 확장을 허용하는 확인란을 켜야 kext를 쓸 수 있습니다 [2].

AuxKC가 어디에 기록되는지도 하드웨어마다 다릅니다. Apple 실리콘에서는 AuxKC의 측정값이 LocalPolicy에 서명되어 들어가고, 이전 하드웨어(인텔)에서는 AuxKC가 데이터 볼륨에 있었습니다 [2]. LocalPolicy에는 AuxKC Image4 구조의 SHA-384 해시와 kext 영수증 (receipt)이 들어갑니다 [2].

SIP가 켜져 있으면 각 kext의 서명을 확인한 뒤 AuxKC에 넣고, SIP가 꺼져 있으면 kext 서명을 강제하지 않습니다 [1][2]. 자동 기기 등록 (Automated Device Enrollment, ADE)을 거친 Apple 실리콘 맥에서는 kext를 허용하는 프로파일을 적용할 때 MDM이 부트스트랩 토큰으로 보안 부팅 정책을 Reduced Security로 자동 설정할 수도 있습니다 [1].

## 구조

### 시스템 확장 허용 페이로드

MDM 페이로드 `com.apple.system-extension-policy` 는 macOS 10.15 이후 쓸 수 있고, 기기 채널 전용이며, 사용자 승인 MDM이 필요하고, 한 기기에 여러 개가 들어갈 수 있습니다 [3]. 들어가는 키는 아래와 같습니다 [3].

| 키 | 형식 | 뜻 | 버전 |
|---|---|---|---|
| `AllowedSystemExtensions` | 사전 | 팀 ID마다 허용할 시스템 확장 번들 ID 배열 | 10.15+ |
| `AllowedSystemExtensionTypes` | 사전 | 팀 ID마다 허용할 확장 종류 배열 | 10.15+ |
| `AllowedTeamIdentifiers` | 문자열 배열 | 이 팀 ID로 서명된 확장은 모두 허용 | 10.15+ |
| `AllowUserOverrides` | 불리언 | `false` 면 프로파일이 허용하지 않은 확장을 사용자가 승인할 수 없음. 기본값 `true` | 10.15+ |
| `RemovableSystemExtensions` | 사전 | 스스로 제거할 수 있는 확장 | 12+ |
| `NonRemovableSystemExtensions` | 사전 | SIP가 켜져 있으면 끄거나 지울 수 없는 확장 | 15+ |
| `NonRemovableFromUISystemExtensions` | 사전 | 시스템 설정·Finder에서 끄거나 지울 수 없는 확장 | 15+ |

확장 종류 값은 `DriverExtension`, `NetworkExtension`, `EndpointSecurityExtension` 입니다 [3]. MDM으로 특정 확장, 특정 개발자의 확장, 특정 종류의 확장을 사용자 조작 없이 허용할 수 있고, 구성을 지워서 확장을 내릴 수도 있습니다 [1]. 팀 ID를 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** kext 폴더에 서드파티 kext가 있으면 그 kext가 디스크에 설치돼 있었다는 뜻이고, 파일의 서명으로 개발자 팀 ID를 말할 수 있습니다. Apple 실리콘 맥에 서드파티 kext가 적재돼 있었다면 누군가 보안 수준을 낮췄다는 뜻이고, 그 주체는 1TR에서 사람이 한 조작이거나 MDM일 가능성이 큽니다 [1][2]. 시스템 확장 페이로드의 `AllowedSystemExtensions`·`AllowedSystemExtensionTypes`·`AllowedTeamIdentifiers` 에 든 확장은 사용자 조작 없이 올라올 수 있는 상태였다고 읽을 수 있고, `AllowUserOverrides` 값으로 그 밖의 확장을 사용자가 따로 승인할 수 있었는지를 판별합니다 [1][3].

**증명하지 못하는 것.** kext 파일이 폴더에 있다는 사실은 적재됐다는 뜻이 아닙니다. 보안 수준이 낮아져 있다는 사실만으로 누가, 어떤 목적으로 낮췄는지는 알 수 없고, 보안 제품이나 장치 드라이버처럼 정상적인 이유로 낮춘 맥도 있습니다. 페이로드가 허용한다는 사실도 그 확장이 실제로 설치돼 돌았다는 뜻은 아닙니다.

보고서에는 "이 맥의 보안 부팅 정책이 Reduced Security로 설정돼 있었고, 이 경로에 이 팀 ID로 서명된 kext가 있었다" 처럼 기록으로 확인되는 만큼 나눠서 씁니다.

## 시각 해석

kext가 언제 설치되고 언제 AuxKC에 들어갔는지, 보안 수준을 언제 낮췄는지는 파일 밖의 기록으로 좁힙니다. 설치 시기는 kext 파일의 파일 시스템 시각과 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)로 좁히고, 적재 여부와 시기는 [통합 로그에서 찾을 것 (Unified Log Events)](../logs/unified-log-events/index.md)의 커널 확장 관련 기록과 재시동 시각을 함께 놓아 봅니다. macOS 11 이후 kext는 재시동해야 올라가므로 [2], kext 파일이 생긴 뒤 첫 재시동 시각이 적재 시기를 좁히는 기준이 됩니다. 재시동 시각은 [전원·잠자기 기록 (pmset)](../logs/power-events.md)에서 확인합니다.

## 함정과 한계

`/System/Library/Extensions` 에는 Apple이 넣어 둔 kext도 들어 있을 수 있어서, 파일 목록만 보고 이상 여부를 판별하기 어렵습니다. 서명과 팀 ID로 Apple 것과 서드파티 것을 먼저 나누고, 같은 macOS 버전의 설치본과 비교합니다.

인텔 맥과 Apple 실리콘 맥은 AuxKC가 기록되는 곳이 달라서 [2], Apple 실리콘에서 쓰는 해석(LocalPolicy, 1TR 조작)을 인텔 맥에 그대로 옮기지 않습니다. 조사 전에 하드웨어 종류를 먼저 확인합니다([컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](../system-account/computer-name-hardware.md)).

SIP가 꺼져 있으면 kext 서명을 강제하지 않으므로 [1][2], SIP가 꺼진 맥에서는 "서명된 kext만 올라왔다" 고 가정하지 않습니다. 반대로 시스템 확장 페이로드에서 `AllowUserOverrides` 가 빠져 있으면 기본값 `true` 가 적용되므로 [3], 키가 없다고 해서 사용자 승인이 막혀 있었다고 읽지 않습니다.

지우기 쪽에서 보면, MDM은 구성을 지워서 확장을 내릴 수 있어서 [1] 수집 시점에 페이로드가 없다는 사실이 과거에도 없었다는 뜻은 아닙니다. 지난 상태는 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md)로 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

구성 프로파일 안의 시스템 확장 페이로드는 plist 형식이라서, 헥스 편집기로 열면 키 문자열을 그대로 검색할 수 있습니다. 아래는 [3]의 키 표를 바탕으로 만든 XML plist 예시이고, 팀 ID 값 `EXAMPLE123` 은 설명용으로 넣은 값이며 실제 데이터에서 나온 값이 아닙니다.

```
<key>AllowedTeamIdentifiers</key>
<array>
    <string>EXAMPLE123</string>
</array>
<key>AllowUserOverrides</key>
<true/>
```

바이너리 plist라면 키 문자열 `AllowedTeamIdentifiers` 를 검색해 위치를 잡은 뒤 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)의 순서대로 값까지 따라갑니다. 이 예시는 "이 팀 ID로 서명된 확장은 모두 허용하고, 프로파일이 허용하지 않은 확장도 사용자가 승인할 수 있다" 로 읽습니다.

### 공개 도구로 한 번

ForensicArtifacts 정의 파일 [4]은 공개 아티팩트 정의 모음이라서, 수집 목록을 짤 때 kext 폴더 경로를 그대로 옮겨 챙길 수 있습니다. 가져온 자료는 아래 순서로 봅니다.

1. 하드웨어 종류(인텔·Apple 실리콘)와 macOS 버전을 확인합니다.
2. 두 kext 폴더의 항목마다 서명·팀 ID·파일 시스템 시각을 적고, Apple 것이 아닌 항목을 따로 표시합니다.
3. 실행 중인 시스템이라면 `kextstat` 으로 적재 목록을 저장해 폴더 목록과 맞춥니다 [4].
4. 설치된 구성 프로파일에서 `com.apple.system-extension-policy` 페이로드를 찾아 허용된 팀 ID·번들 ID·종류와 `AllowUserOverrides` 값을 적습니다. 프로파일을 꺼내는 법은 [구성 프로파일](configuration-profiles.md)에 있습니다.

실행 중인 시스템에서 명령을 칠 때의 원칙은 [라이브 대응 (Live Response)](../../03-techniques/process-acquisition/live-response/index.md)을 따릅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 |
|---|---|
| [구성 프로파일 (Configuration Profiles·MDM)](configuration-profiles.md) | 시스템 확장을 허용한 프로파일과 MDM 등록 상태 |
| [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../01-foundations/protection/codesign-notarization-sip.md) | kext 서명과 SIP 상태 |
| [통합 로그에서 찾을 것 (Unified Log Events)](../logs/unified-log-events/index.md) | 커널 확장 적재 관련 기록 |
| [전원·잠자기 기록 (pmset)](../logs/power-events.md) | kext 설치 뒤 재시동 시각 |
| [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) | kext나 시스템 확장을 함께 설치한 앱 |
| [보안 도구 기록 (XProtect)](../logs/xprotect.md) | 같은 시기에 보안 도구가 남긴 기록 |

지속성 위치를 한꺼번에 살펴보는 순서는 [악성 코드 지속성 찾기 (Persistence)](../../04-scenarios/incident/persistence.md)에, 권한을 높인 흔적을 보는 순서는 [권한 상승과 TCC 우회 흔적 (Privilege·TCC Bypass)](../../04-scenarios/incident/privilege-tcc-bypass.md)에 있습니다.

## 실습

NIST CFReDS 같은 공개 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 이미지의 하드웨어 종류와 macOS 버전을 적고, 버전 표에서 어느 규칙이 적용되는지 정합니다.
2. `/Library/Extensions` 에 서드파티 kext가 있는지, 있다면 팀 ID와 파일 시스템 시각을 적습니다.
3. 구성 프로파일이 있다면 시스템 확장 페이로드가 들어 있는지, 들어 있다면 허용 범위를 표로 정리합니다.
4. kext 파일이 생긴 시각 뒤의 첫 재시동 시각을 찾아 함께 적습니다.

## 참고 문헌

1. Apple Platform Deployment, "System and kernel extensions in macOS" — https://support.apple.com/guide/deployment/system-and-kernel-extensions-in-macos-depa5fb8376f/web
2. Apple Platform Security, "Kernel extensions in macOS" — https://support.apple.com/guide/security/kernel-extensions-sec8e454101b/web
3. Apple Developer, Device Management "SystemExtensions" 페이로드 (문서 JSON) — https://developer.apple.com/tutorials/data/documentation/devicemanagement/systemextensions.json
4. ForensicArtifacts, artifacts/data/macos.yaml (main 브랜치) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
