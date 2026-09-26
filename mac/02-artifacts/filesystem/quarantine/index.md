---
title: "격리 속성과 다운로드 기록"
parent: "아티팩트 · 파일 시스템"
nav_order: 970
has_children: true
has_toc: false
---

# 격리 속성과 다운로드 기록 (Quarantine)

격리 (Quarantine)는 인터넷 등에서 받은 파일에 macOS가 표시를 남기는 방식이고, 파일 자체의 확장 속성과 사용자별 DB 두 곳에 기록이 남아서 파일이 어떤 앱을 거쳐 언제, 어디서 들어왔는지를 이어 볼 수 있습니다.

## 왜 중요한가

파일이 어디서 들어왔는지는 악성 코드의 침입 경로를 찾을 때나 자료가 들어온 경위를 따질 때 먼저 묻는 질문이고, 격리 기록은 그 답을 두 곳에 나눠 남깁니다. 파일에 붙는 확장 속성 `com.apple.quarantine` 에는 받은 앱 이름과 격리 시각이 들어 있고, 사용자별 SQLite DB `QuarantineEventsV2` 에는 받은 파일 URL·원래 페이지 URL·격리 이유가 한 행씩 남습니다 [1][2]. 확장 속성의 마지막 필드인 UUID가 DB의 `LSQuarantineEventIdentifier` 와 같은 값이라서, 파일에서 출발해 다운로드 출처까지 따라갈 수 있습니다 [1][2].

격리 속성은 Gatekeeper가 앱을 처음 열 때 무엇을 확인할지 정하는 기준이기도 합니다. Gatekeeper는 격리 속성에 격리 플래그가 서 있는 앱에만 첫 실행 확인을 더 요구하고, 격리 속성이 없는 앱은 공증 확인만 거친 뒤 사용자 조치 없이 실행됩니다 [6]. Gatekeeper는 인터넷에서 받은 소프트웨어를 처음 열 때 사용자 승인을 요청하고, 처음 열 때는 어떤 경로로 들어왔든 모든 소프트웨어를 알려진 악성 코드인지 검사합니다 [4]. 격리 속성이 남아 있는지와 플래그가 어떻게 바뀌었는지는 사용자가 앱을 열면서 어떤 확인을 거쳤는지 따져 볼 단서가 됩니다.

사용자가 System Settings의 Privacy & Security에서 "Open Anyway" 를 누르면 그 앱은 보안 설정의 예외로 저장되고, 그 뒤로는 더블클릭으로 열 수 있습니다 [5]. 로컬에서 빌드해 ad hoc 서명한 앱은 격리되지 않아서 예전처럼 실행됩니다 [6]. 통합 로그 쪽은 [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md)에서 다룹니다.

## 한눈에 보기

| 기록 | 위치 | 알려 주는 것 | 알려 주지 않는 것 |
|---|---|---|---|
| 격리 확장 속성 `com.apple.quarantine` | 받은 파일 자체의 확장 속성 | 플래그, 격리 시각(유닉스 시각), 받은 앱 이름, 이벤트 UUID [1] | 출처 URL, 사용자 계정, 실행 시각 |
| `com.apple.provenance` | 격리를 통과한 앱의 확장 속성(macOS 13 Ventura부터) | ExecPolicy DB의 행을 가리키는 키 [3] | 그 자체로는 번들 ID·cdhash(ExecPolicy DB에서 찾음) |
| 격리 이벤트 DB `QuarantineEventsV2` | `~/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2` | 받은 앱, 받은 파일 URL, 원래 페이지 URL, 격리 이유, 격리 시각(맥 절대 시각) [2] | 파일을 열었는지, 파일이 지금도 있는지 |

격리·Gatekeeper 쪽에서 버전마다 달라진 점은 아래와 같습니다.

| macOS 버전 | 달라진 점 |
|---|---|
| 10.15 Catalina | 기본값으로 소프트웨어가 공증되어 있어야 합니다 [5] |
| 13 Ventura | 격리를 통과한 앱에 `com.apple.provenance` 확장 속성이 새로 붙습니다 [3] |
| 15 Sequoia | 격리된 앱이 공증되지 않았으면 Gatekeeper가 첫 실행을 거부하고, Privacy & Security 설정에서 예외 목록에 넣어야만 실행할 수 있습니다 [6] |

## 읽는 순서

1. [격리 확장 속성 (com.apple.quarantine)](quarantine-xattr.md) — 네 필드 형식과 플래그 비트, 첫 실행 뒤의 플래그 변화, Ventura부터 붙는 `com.apple.provenance` 를 헥스 예시로 풉니다.
2. [격리 이벤트 DB (QuarantineEventsV2)](quarantine-events-db.md) — `LSQuarantineEvent` 표의 열과 격리 이유, 맥 절대 시각을 바꾸는 법, UUID로 파일과 잇는 SQL을 다룹니다.

## 함께 볼 페이지

- [다운로드 출처 속성 (kMDItemWhereFroms)](../where-froms.md) — 같은 파일에 남는 다른 출처 기록
- [실행 정책 평가 기록 (ExecPolicy·Gatekeeper)](../../execution/execpolicy-gatekeeper.md) — `com.apple.provenance` 가 가리키는 DB와 Gatekeeper 평가 기록
- [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../../01-foundations/protection/codesign-notarization-sip.md) — 공증과 SIP의 바탕 개념
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md) — 속성과 DB의 시각 기준이 다를 때
- [사파리 (Safari)](../../browsers/safari/index.md), [크롬·엣지·웨일 (Chromium 계열)](../../browsers/chromium/index.md) — 브라우저 쪽 다운로드 기록
- [에어드롭 (AirDrop)](../../external-devices/airdrop.md) — AirDrop으로 받은 앱에도 격리가 걸릴 때
- [이 파일은 어디서 왔나 (File Origin)](../../../04-scenarios/activity/file-origin.md)
- [악성 코드는 어디서 들어왔나 (Initial Access)](../../../04-scenarios/incident/initial-access.md)
- [악성 코드 흔적 분석 (Malware Triage)](../../../03-techniques/analysis/malware-triage/index.md)

## 참고 문헌

1. Howard Oakley, "xattr: com.apple.quarantine, the quarantine flag" (The Eclectic Light Company, 2017-12-11) — https://eclecticlight.co/2017/12/11/xattr-com-apple-quarantine-the-quarantine-flag/
2. mac_apt 격리 플러그인 소스 quarantine.py (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/quarantine.py
3. Howard Oakley, "Ventura has changed app quarantine with a new xattr" (The Eclectic Light Company, 2023-03-13) — https://eclecticlight.co/2023/03/13/ventura-has-changed-app-quarantine-with-a-new-xattr/
4. Apple Platform Security, "Gatekeeper and runtime protection in macOS" — https://support.apple.com/guide/security/gatekeeper-and-runtime-protection-sec5599b66df/web
5. Apple Support, "Safely open apps on your Mac" (102445) — https://support.apple.com/en-us/102445
6. Howard Oakley, "Gatekeeper and notarization in Sequoia" (The Eclectic Light Company, 2024-08-10) — https://eclecticlight.co/2024/08/10/gatekeeper-and-notarization-in-sequoia/
