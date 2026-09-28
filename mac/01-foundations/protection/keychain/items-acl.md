---
title: "항목과 접근 제어"
parent: "키체인"
grand_parent: "기반 · 보안·보호"
nav_order: 430
---

# 항목과 접근 제어 (Items·ACL)

키체인 항목은 인터넷 암호, 일반 암호, 인증서, 키 네 종류이고, 파일 기반 키체인은 계정·서비스·서버 같은 메타데이터를 4글자 이름의 속성에 담으며, 어떤 프로그램이 항목을 꺼내 쓸 수 있는지는 파일 기반 키체인이면 접근 제어 목록 (ACL)으로, 데이터 보호 키체인이면 키체인 접근 그룹 (keychain access groups)으로 정합니다.

## 항목 종류

키체인 항목 종류(class)는 인터넷 암호, 일반 암호, 인증서, 키 네 가지입니다 [2]. 파일 기반 키체인에서는 종류마다 표가 따로 있고, 표를 가리키는 레코드 종류 값은 [로그인 키체인 파일 (login.keychain-db)](login-keychain.md)의 표에 정리해 두었습니다. 데이터 보호 키체인이 네 종류를 어떻게 담고 동기화하는지는 [시스템·로컬 항목 키체인 (System·Local Items)](system-local-items.md)에서 다룹니다.

## 속성

### 4글자 속성 이름

파일 기반 키체인의 일반 암호 레코드에는 아래 속성이 있고, 이름은 모두 4글자입니다 [1].

| 자료형 | 속성 |
|---|---|
| 날짜 | `cdat`, `mdat` |
| 바이너리 | `desc`, `icmt`, `prot`, `acct`, `svce`, `gena` |
| 32비트 부호 없는 정수 | `crtr`, `type`, `scrp`, `invi`, `nega`, `cusi` |

인터넷 암호 레코드에는 일반 암호 속성에 `sdmn`, `srvr`, `ptcl`, `atyp`, `port`, `path` 가 더 붙습니다 [1]. 날짜 속성 `cdat`·`mdat` 는 UTC 문자열이고, 읽는 법은 [로그인 키체인 파일 (login.keychain-db)](login-keychain.md)의 날짜 속성 절에 있습니다.

### 도구가 보여 주는 필드 이름

chainbreaker는 같은 레코드를 아래 필드 이름으로 풀어 보여 줍니다 [4].

| 레코드 | chainbreaker 필드 이름 |
|---|---|
| 일반 암호 | CreationDate, ModDate, Description, Creator, Type, PrintName, Alias, Account, Service, SSGPArea |
| 인터넷 암호 | CreationDate, ModDate, Description, Comment, Creator, Type, PrintName, Alias, Protected, Account, SecurityDomain, Server, Protocol, AuthType, Port, Path, SSGPArea |

`svce` 와 Service, `acct` 와 Account, `srvr` 와 Server, `ptcl` 와 Protocol 처럼 이름이 비슷한 짝이 보입니다. 보고서에는 도구가 보여 준 필드 이름과 원래 속성 이름을 함께 적고, 이름만 보고 짝을 단정하지 않습니다.

파일 기반 키체인에서는 계정, 서비스, 서버 같은 메타데이터가 키체인을 풀 수단 없이도 보입니다 [3]. 데이터 보호 키체인은 메타데이터도 암호화하므로 [5] 이렇게 전제하지 않습니다. 푸는 수단과 암호화한 부분의 구조는 [로그인 키체인 파일 (login.keychain-db)](login-keychain.md)에서 다룹니다.

## 접근 제어

### 두 가지 모델

두 키체인 구현은 접근을 정하는 방식이 다릅니다 [2].

| 구현 | 접근 제어 방식 |
|---|---|
| 파일 기반 키체인 | 접근 제어 목록 (ACL, `SecAccess`) |
| 데이터 보호 키체인 | 키체인 접근 그룹과, 필요하면 접근 제어 객체 (`SecAccessControl`) |

데이터 보호 키체인에서 프로그램이 속한 접근 그룹 목록은 그 프로그램의 코드 서명 권한 (entitlements)에서 나옵니다 [2]. 접근 그룹은 같은 개발자의 앱끼리 항목을 나눠 쓰게 해 주고, 서드파티 앱의 접근 그룹에는 Apple Developer Program이 준 접두사가 붙으며, 이 규칙은 코드 서명과 프로비저닝 프로파일로 강제합니다 [5]. Apple은 이 모델이 파일 기반 키체인의 ACL보다 이해하기 쉽고 요즘 플랫폼 규칙에 더 맞다고 적습니다 [2].

접근 그룹이 코드 서명 권한에서 나오니, 어떤 앱이 어떤 그룹의 항목에 닿을 수 있는지는 앱 번들의 서명과 권한에서 실마리를 찾습니다. 앱과 개발자를 가리키는 식별자는 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../value-decoding/bundle-team-id.md)에서, 서명과 권한을 확인하는 법은 [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../codesign-notarization-sip.md)와 [앱 번들 정보 (Info.plist·Code Signature)](../../../02-artifacts/embedded-metadata/app-bundle.md)에서 다룹니다.

### 다루지 않는 부분

파일 기반 키체인 ACL의 내부 구조(신뢰하는 앱 목록과 권한 종류)와, ACL이 파일 안 어느 레코드·필드에 저장되는지는 이 페이지에서 다루지 않습니다.

## 증거로서 의미

항목의 메타데이터는 이 사용자의 키체인에 어떤 서비스나 서버에 쓸 계정이 저장돼 있다는 사실을 보여 주지만, 그 계정으로 실제 로그인했는지나 언제 암호를 꺼내 썼는지는 알 수 없습니다. `mdat` 값만으로는 암호를 바꾼 시각인지, ACL을 바꿀 때 바뀐 값인지 단정할 수 없어서 "암호를 이때 바꿨다" 고 쓰지 않습니다. 보고서에는 "로그인 키체인에 이 서버를 가리키는 인터넷 암호 항목이 있고, 이 항목의 `mdat` 속성 값은 이 시각(UTC)이다" 처럼 기록된 만큼만 씁니다.

키체인에 누가 접근했는지를 남기는 통합 로그 기록의 서브시스템과 카테고리는 실제 데이터로 확인해야 합니다. 키체인 파일에 접근한 흔적을 찾을 때는 [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events/index.md)과 [정보 탈취 악성 코드 (Infostealer)](../../../04-scenarios/incident/infostealer.md)를 함께 봅니다.

## 참고 문헌

1. libyal dtformats — MacOS keychain database file format — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/MacOS%20keychain%20database%20file%20format.asciidoc
2. Apple, TN3137: On Mac keychain APIs and implementations (2022-11-01) — https://developer.apple.com/tutorials/data/documentation/technotes/tn3137-on-mac-keychains.json
3. chainbreaker README (n0fate) — https://github.com/n0fate/chainbreaker
4. chainbreaker 소스 `chainbreaker/__init__.py` — https://raw.githubusercontent.com/n0fate/chainbreaker/master/chainbreaker/__init__.py
5. Apple Platform Security — Keychain data protection — https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
