---
title: "서명·공증·무결성 보호"
parent: "기반 · 보안·보호"
nav_order: 440
---

# 서명·공증·무결성 보호 (Code Signing·Notarization·SIP)

## 한 줄 요약

macOS 는 코드 서명 (Code Signing) 과 공증 (Notarization) 으로 앱이 누구에게서 왔고 그 뒤로 바뀌지 않았는지를 확인하고, 시스템 무결성 보호 (System Integrity Protection, SIP) 와 서명된 시스템 볼륨 (Signed System Volume, SSV) 으로 운영체제 영역을 읽기 전용으로 묶어 둡니다. 이 페이지는 각 장치가 무엇을 확인하는지 정리하고, 그 결과 분석가가 어떤 흔적을 믿어도 되고 어떤 흔적을 의심해야 하는지를 다룹니다.

## 이 보호 장치와 이어진 아티팩트

이 페이지는 아티팩트 하나를 설명하지 않고, 여러 아티팩트를 해석할 때 바탕이 되는 규칙을 모아 둡니다. 실제 기록은 아래 페이지에서 읽습니다.

| 아티팩트 | 이 페이지와 이어지는 점 |
|---|---|
| [앱 번들 정보 (Info.plist·Code Signature)](../../02-artifacts/embedded-metadata/app-bundle.md) | 번들 안에 담긴 서명 정보를 읽습니다 |
| [번들 ID와 팀 ID (Bundle ID·Team ID)](../value-decoding/bundle-team-id.md) | 서명과 함께 나오는 앱·개발자 식별값을 읽습니다 |
| [실행 정책 평가 기록 (ExecPolicy·Gatekeeper)](../../02-artifacts/execution/execpolicy-gatekeeper.md) | Gatekeeper 가 서명·공증을 확인한 결과가 남는 곳입니다 |
| [격리 속성과 다운로드 기록 (Quarantine)](../../02-artifacts/filesystem/quarantine/index.md) | 인터넷에서 받은 파일의 표시와 macOS 13·15 에서 달라진 Gatekeeper 동작을 다룹니다 |
| [커널·시스템 확장 (KEXT·System Extension)](../../02-artifacts/persistence/kext-system-extension.md) | 공증 요구가 커널 확장에도 걸립니다 |
| [구성 프로파일 (Configuration Profiles·MDM)](../../02-artifacts/persistence/configuration-profiles.md) | 기기 관리 서비스가 Gatekeeper 설정을 제한할 수 있습니다 |
| [방화벽 (Application Firewall)](../../02-artifacts/network/application-firewall.md) | 방화벽을 통과하는 앱은 해당 권한을 넣어 서명해야 합니다 |
| [APFS 구조 (APFS)](../disk-volume/apfs/index.md), [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../disk-volume/volume-group-firmlinks.md) | SSV 가 쓰는 스냅숏과 시스템·데이터 볼륨의 짜임을 설명합니다 |

## 구조

### 다섯 가지 장치 한눈에 보기

| 장치 | 확인하는 것 | 확인하는 때 | 도입 |
|---|---|---|---|
| 코드 서명 | 개발자가 서명한 뒤 코드가 바뀌지 않았는지 | 실행할 때, 보호된 권한을 쓸 때 | App Store 밖 앱 필수 서명은 macOS 10.15 |
| 공증 | Apple 이 사본을 검사해 알려진 악성 코드를 찾지 못했는지 | Apple 에 올릴 때 검사하고, 실행할 때 티켓을 확인 | 10.14.5 에서 일부, 10.15 에서 확대 |
| Gatekeeper | 확인된 개발자인지, 공증됐는지, 바뀌지 않았는지 | 처음 열 때 | — |
| SIP | 보호 경로를 root 도 고치지 못하게 막음 | 항상(커널이 적용) | OS X 10.11 El Capitan |
| SSV | 시스템 볼륨의 모든 바이트가 Apple 서명과 맞는지 | 부팅할 때와 실행 중 | macOS 11 Big Sur |

### 코드 서명

App Store 앱은 모두 Apple 이 서명하고, macOS 10.15 부터 App Store 밖에서 배포하는 앱은 개발자가 Apple 이 발급한 Developer ID 인증서로 서명해야 합니다. Developer ID 인증서는 개인 키와 인증서를 묶은 것이고, 서명은 개발자가 빌드하고 서명한 뒤로 소프트웨어가 바뀌지 않았음을 증명하는 데 씁니다. 회사 안에서만 쓰는 앱 (in-house) 도 Apple 은 Developer ID 로 서명하도록 권장합니다.

서명은 권한과도 맞물려 있습니다. 필수 접근 제어 (Mandatory Access Control, MAC) 는 시스템이 보호하는 권한 (entitlement) 을 쓰려는 코드에 서명을 요구하고, 예를 들어 방화벽을 통과해야 하는 앱은 그 권한을 넣어 서명해야 합니다. 서명이 번들 안에 어떤 모양으로 들어 있는지는 [앱 번들 정보](../../02-artifacts/embedded-metadata/app-bundle.md) 페이지에서 다룹니다.

### 공증

공증은 Developer ID 로 서명한 소프트웨어를 Apple 이 악성 요소가 있는지 검사했다는 표시이고, 앱 심사 (App Review) 와는 다릅니다. 공증 서비스 (Apple notary service) 는 자동 시스템으로, 악성 내용과 코드 서명 문제를 검사해 결과를 돌려줍니다. 공증은 코드 서명과 별개로 배포 과정의 누구든 받을 수 있고, 그 결과로 알 수 있는 범위는 "Apple 이 코드 사본을 받아 검사했고 알려진 악성 코드를 찾지 못했다" 는 데까지입니다.

공증을 받으려면 아래 요건을 채워야 합니다.

| 항목 | 내용 |
|---|---|
| 인증서 | Developer ID 인증서(응용 프로그램·커널 확장·시스템 확장·설치 프로그램용)로 서명합니다. Mac Distribution·ad hoc·Apple Developer·로컬 개발 인증서로는 받을 수 없습니다 |
| 하드닝된 런타임 (Hardened Runtime) | 앱과 명령줄 도구에서 켜야 합니다 |
| 보안 타임스탬프 (secure timestamp) | 코드 서명에 넣어야 합니다 |
| 대상 형식 | macOS 앱, 앱이 아닌 번들(커널 확장 등), 디스크 이미지(UDIF), 평면 (flat) 설치 패키지 |
| 서비스가 확인하는 것 | 모든 실행 파일의 서명 유효성, 코드 서명 문제, 악성 요소, 권한 목록의 형식(XML, ASCII 인코딩) |

공증을 통과하면 티켓 (ticket) 이 만들어지고, 공증 서비스는 이 티켓을 온라인에 공개해 Gatekeeper 가 찾을 수 있게 합니다. 개발자는 티켓을 앱에 붙일 (staple) 수도 있지만 붙이는 일은 선택이고, 실행할 때 티켓이 온라인에 있든 실행 파일에 붙어 있든 Gatekeeper 는 Apple 이 공증한 소프트웨어로 판단합니다. 공증 서비스는 서명 키로 배포한 소프트웨어의 감사 기록을 남기고, 개발자가 허가 없이 나온 버전을 찾으면 Apple 과 함께 그 버전의 티켓을 취소할 수 있습니다.

### Gatekeeper

Gatekeeper 는 서명과 공증을 실제로 확인하는 곳으로, 소프트웨어가 확인된 개발자의 것인지, Apple 이 공증했는지, 바뀌지 않았는지를 봅니다. 인터넷에서 받은 소프트웨어는 처음 열 때 사용자에게 승인을 묻고, 들어온 경로와 관계없이 모든 소프트웨어는 처음 열 때 알려진 악성 내용 검사를 받습니다. 무해한 앱에 악성 플러그인을 끼워 배포하는 수법을 막으려고 Gatekeeper 는 앱을 무작위로 정한 읽기 전용 위치에서 열기도 합니다.

사용자는 Gatekeeper 정책을 App Store 앱만 허용하도록 바꾸거나, 기본 정책을 무시하거나, 끌 수 있고, 기기 관리 (MDM) 서비스가 이 설정을 제한할 수 있습니다. App Store 앱은 샌드박스 안에서 돌고, 앱끼리는 macOS 가 제공하는 API 와 서비스로만 데이터를 주고받습니다. Gatekeeper 가 판단을 어디에 남기는지는 [실행 정책 평가 기록](../../02-artifacts/execution/execpolicy-gatekeeper.md) 페이지에서, 격리 속성과 macOS 13 Ventura·15 Sequoia 의 변화는 [격리 속성](../../02-artifacts/filesystem/quarantine/index.md) 페이지에서 다룹니다.

### 시스템 무결성 보호 (SIP)

SIP 는 OS X 10.11 El Capitan 에서 처음 나왔고, 10.11 이후로 업그레이드하면 기본으로 켜집니다. SIP 는 커널 권한으로 지정한 중요 위치를 읽기 전용으로 만들고, 샌드박스 안에서 도는지나 관리자 권한이 있는지와 관계없이 모든 프로세스에 이 제한을 겁니다. root 계정도 예외가 아니라서 root 로도 보호된 시스템 구성 요소에 할 수 있는 일이 줄어들고, 소프트웨어가 시동 디스크를 고르는 일도 막힙니다. 바탕 기술은 필수 접근 제어이고, 샌드박스와 Data Vault 보호도 같은 기술을 씁니다.

| 구분 | 경로 |
|---|---|
| SIP 가 보호하는 곳 | `/System`, `/usr`, `/bin`, `/sbin`, `/var`, macOS 에 미리 설치된 앱 |
| 서드파티 앱·설치 프로그램이 계속 쓸 수 있는 곳 | `/Applications`, `/Library`, `/usr/local` |

Intel 맥에서 SIP 를 끄면 그 물리 저장 장치의 모든 파티션에서 보호가 풀립니다. El Capitan 이후로 업그레이드할 때 macOS 는 SIP 와 충돌하는 서드파티 소프트웨어를 옆으로 치워 둘 (set aside) 수 있습니다.

### 서명된 시스템 볼륨 (SSV)

SSV 는 macOS 11 Big Sur 에서 도입한 읽기 전용 시스템 볼륨입니다. 커널은 실행 중에 시스템 내용의 무결성을 확인하고, Apple 의 유효한 암호 서명이 없는 데이터는 코드든 아니든 거부합니다.

짜임은 머클 트리 (Merkle tree) 와 비슷합니다. 파일 시스템 메타데이터 트리의 각 SHA-256 해시를 부모 해시와 대조하고, 맨 위 해시를 봉인 (seal) 이라 부르며, 봉인은 SSV 의 모든 바이트를 포함합니다. 암호 서명은 시스템 볼륨 전체에 걸립니다. SSV 는 APFS 스냅숏을 쓰고, 업데이트에 실패하면 재설치 없이 이전 시스템 버전으로 되돌릴 수 있습니다.

> 그림 자리: SSV 해시 트리 — 파일 메타데이터 해시가 부모 해시로 올라가 맨 위 봉인에 모이고, 부팅 단계에서 봉인을 확인하는 흐름

| 기종 | 봉인을 확인하는 때 |
|---|---|
| Apple silicon 맥 | 부트로더가 커널에 제어를 넘기기 전에 확인합니다 |
| T2 칩이 있는 Intel 맥 | 부트로더가 측정값을 커널에 넘기고, 커널이 루트 파일 시스템을 마운트하기 전에 확인합니다 |

확인에 실패하면 시동이 멈추고 macOS 재설치를 요구합니다. 사용자는 보안 수준을 낮춘 뒤 따로 선택해야만 SSV 를 끌 수 있고, FileVault 가 켜져 있으면 끌 수 없습니다. 읽기 전용 시스템 볼륨 자체는 macOS 10.15 에서 먼저 생겼고, macOS 11 부터 여기에 암호 서명을 걸었습니다.

### 버전별 정리

| macOS 버전 | 달라진 점 |
|---|---|
| OS X 10.11 El Capitan | SIP 도입, 10.11 이후로 업그레이드하면 기본으로 켜짐 |
| macOS 10.14.5 | 새 Developer ID 인증서로 서명한 소프트웨어와 새로 만들거나 갱신한 모든 커널 확장은 공증을 받아야 실행 |
| macOS 10.15 Catalina | 2019년 6월 1일 이후 빌드해 Developer ID 로 배포한 모든 소프트웨어는 공증 필수, App Store 밖 앱은 Developer ID 서명 필수, 시스템 내용을 따로 떼어 낸 읽기 전용 시스템 볼륨 도입 |
| macOS 11 Big Sur | SSV 도입(읽기 전용 시스템 볼륨에 암호 서명을 걸음) |
| macOS 13 Ventura·15 Sequoia | Gatekeeper·격리 관련 변화는 [격리 속성](../../02-artifacts/filesystem/quarantine/index.md) 페이지 참고 |

공증 서비스 쪽 변화도 하나 있습니다. 2023년 11월 1일부터 공증 서비스는 `altool` 과 Xcode 13 이하에서 올린 요청을 받지 않고, 지금은 `notarytool` 로 올리고 `stapler` 로 티켓을 붙입니다.

## 읽는 법

디스크에서 수상한 앱이나 실행 파일을 찾았을 때는 아래 순서로 이 페이지의 규칙을 적용합니다.

1. 서명이 있는지, 있다면 어느 개발자의 Developer ID 인증서인지 [앱 번들 정보](../../02-artifacts/embedded-metadata/app-bundle.md) 와 [번들 ID와 팀 ID](../value-decoding/bundle-team-id.md) 페이지를 따라 확인합니다.
2. 공증 여부를 봅니다. 번들에 티켓이 붙어 있지 않아도 티켓은 Apple 서버에 있을 수 있어서, 붙은 티켓만으로 결론을 내리지 않습니다.
3. 그 맥에서 Gatekeeper 가 실제로 어떤 판단을 내렸는지 [실행 정책 평가 기록](../../02-artifacts/execution/execpolicy-gatekeeper.md) 과 [격리 속성](../../02-artifacts/filesystem/quarantine/index.md) 에서 찾습니다. 서명·공증 상태는 "실행할 수 있었는가" 를 알려 줄 뿐이고, 실제로 실행했는지는 [어떤 앱을 언제 썼나](../../04-scenarios/activity/app-usage.md) 페이지를 따라 따로 확인합니다.
4. 파일이 시스템 영역에 있다면 SIP 보호 경로인지, SSV 에 속하는 파일인지를 따져 보고 아래 "포렌식에서 중요한 점" 을 적용합니다.

## 포렌식에서 중요한 점

**시스템 볼륨과 데이터 볼륨을 나눠 봅니다.** SSV 가 켜져 있으면 봉인이 맞지 않는 시스템으로는 시동되지 않아서, macOS 11 이후 시스템 볼륨에 변조 흔적이 남아 있을 여지는 거의 없고 사용자와 공격자의 흔적은 주로 데이터 볼륨 쪽에 쌓입니다. 다만 보안 수준을 낮춰 SSV 를 끈 맥이라면 이 전제가 무너지므로 SSV·SIP 가 켜져 있었는지부터 따집니다 [6]. 두 볼륨이 어떻게 이어져 보이는지는 [볼륨 그룹과 펌링크](../disk-volume/volume-group-firmlinks.md) 페이지에서 다룹니다. 이미지를 확보할 때 두 볼륨을 모두 담는 방법은 [맥 증거 확보](../../03-techniques/process-acquisition/evidence-acquisition/index.md) 를 봅니다.

**SIP 보호 경로의 이상한 파일은 SIP 가 꺼졌던 흔적일 수 있습니다.** SIP 가 켜진 시스템에서는 `/System`·`/usr`(`/usr/local` 은 빼고)·`/bin`·`/sbin` 에 서드파티가 새 파일을 만들 수 없어서, 이 경로에서 macOS 가 설치하지 않은 파일이 보이면 SIP 가 꺼진 적이 있는지 확인할 근거가 됩니다(macOS 11 이후라면 SSV 도 함께 꺼졌는지 봅니다). 반대로 `/Applications`·`/Library`·`/usr/local` 은 서드파티가 쓸 수 있는 곳이라 지속성 항목과 악성 파일을 찾을 때 먼저 볼 자리로 남습니다 [1]. 실제 탐색 순서는 [악성 코드 지속성 찾기](../../04-scenarios/incident/persistence.md) 와 [권한 상승과 TCC 우회 흔적](../../04-scenarios/incident/privilege-tcc-bypass.md) 을 따릅니다.

**서명·공증이 증명하는 범위는 좁습니다.**

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 서명한 개발자가 빌드한 뒤로 코드가 바뀌지 않았다 | 그 개발자가 믿을 만하다 |
| 공증 당시 Apple 이 사본을 검사했고 알려진 악성 코드를 찾지 못했다 | 앱이 무해하다, 또는 앱 심사를 거쳤다 |
| Gatekeeper 가 확인하는 조건을 채웠다 | 이 맥에서 실제로 실행됐다 |

## 함정

- **붙은 티켓이 없다고 미공증은 아닙니다.** 티켓은 Apple 서버에 저장되고 앱에 붙이는 일은 선택이라서, 번들에서 티켓을 찾지 못한 사실만으로 공증받지 않은 앱이라고 쓰지 않습니다.
- **공증 상태는 시간이 지나면 바뀔 수 있습니다.** Apple 은 개발자와 함께 티켓을 취소할 수 있어서, 사고 당시 실행할 때의 공증 상태와 분석하는 날 온라인으로 확인한 판정이 다를 수 있습니다. 보고서에는 어느 시점의 판정인지 밝힙니다.
- **공증을 앱 심사로 읽지 않습니다.** 공증은 자동 검사이고, App Store 의 앱 심사와 다른 절차입니다.
- **`/usr`·`/System` 아래라고 모두 보호 경로는 아닙니다.** `/usr/local` 은 서드파티가 계속 쓸 수 있는 곳이고, macOS 10.15 이후 `/System/Volumes/Data` 는 데이터 볼륨이 붙는 자리라서([볼륨 그룹과 펌링크](../disk-volume/volume-group-firmlinks.md)), 경로 앞부분만 보고 SIP 우회를 의심하면 잘못 짚게 됩니다.
- **Intel 맥에서 SIP 를 끈 영향은 한 볼륨에 머물지 않습니다.** 같은 물리 저장 장치의 모든 파티션에서 보호가 풀리고, 한 저장 장치에 macOS 가 여러 개 설치돼 있었다면 나머지도 보호가 풀린 상태였을 수 있습니다.

## 도구

서명과 공증은 개발자 쪽 도구와 분석가 쪽 기록이 나뉩니다. 개발자는 `notarytool` 로 소프트웨어를 공증 서비스에 올리고 `stapler` 로 티켓을 붙이는데, 분석 중에 빌드 스크립트나 명령 기록에서 이 이름이 보이면 그 사용자가 공증을 받으려 했다는 단서로 읽을 수 있습니다. 명령 기록은 [터미널 명령 기록](../../02-artifacts/execution/shell-history.md) 에서 찾습니다. 분석가가 실제로 읽는 기록은 [앱 번들 정보](../../02-artifacts/embedded-metadata/app-bundle.md) 의 서명 정보, [실행 정책 평가 기록](../../02-artifacts/execution/execpolicy-gatekeeper.md), [격리 속성](../../02-artifacts/filesystem/quarantine/index.md) 이고, 악성 코드 검사 기록은 [보안 도구 기록 (XProtect)](../../02-artifacts/logs/xprotect.md) 에서 따로 다룹니다. 수상한 실행 파일을 처음 살펴보는 전체 흐름은 [악성 코드 흔적 분석](../../03-techniques/analysis/malware-triage/index.md) 을 봅니다.

## 참고 문헌

1. Apple Platform Security, "System Integrity Protection" — https://support.apple.com/guide/security/system-integrity-protection-secb7ea06b49/web
2. Apple Platform Security, "App code signing process in macOS" — https://support.apple.com/guide/security/app-code-signing-process-sec3ad8e6e53/web
3. Apple Developer Documentation, "Notarizing macOS software before distribution" — https://developer.apple.com/tutorials/data/documentation/security/notarizing-macos-software-before-distribution.json
4. Apple Platform Security, "Gatekeeper and runtime protection in macOS" — https://support.apple.com/guide/security/gatekeeper-and-runtime-protection-sec5599b66df/web
5. Apple Support, "About System Integrity Protection on your Mac" (102149) — https://support.apple.com/en-us/102149
6. Apple Platform Security, "Signed system volume security" — https://support.apple.com/guide/security/signed-system-volume-security-secd698747c9/web
