---
title: "앱 번들 정보"
parent: "아티팩트 · 파일 내장 메타데이터"
nav_order: 1890
---

# 앱 번들 정보 (Info.plist·Code Signature)

맥 앱은 `.app` 으로 끝나는 폴더 묶음이고, 그 안의 `Info.plist` 에는 번들 ID·버전·실행 파일 이름·최소 macOS 버전이 적혀 있으며 코드 서명에는 번들 안 파일 목록과 지정 요구 사항이 들어 있어서, 앱을 실행하지 않고도 이 앱이 스스로 무엇이라고 밝히는지와 서명한 뒤에 바뀌었는지를 확인할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

앱 번들 (application bundle)은 실행 코드와 리소스를 정해진 폴더 구조로 묶어 둔 것이고, 기본 모양은 `MyApp.app/Contents/` 아래에 `Info.plist`, `MacOS/`, `Resources/` 가 놓이는 형태입니다 [1]. 시스템은 `Info.plist` 를 읽어 앱을 알아보고 실행할 파일을 찾는데, 여기에는 앱 이름과 번들 ID, 빌드 버전과 출시 버전, 주 실행 파일 이름, 앱이 돌아가는 최소 macOS 버전, 저작권 문구 같은 값이 들어갑니다 [1]. 이 값들은 개발자가 빌드할 때 적어 넣는 것이라서, 앱을 설치한 사람이나 설치한 때가 아니라 앱이 스스로 밝히는 정체를 보여 줍니다.

코드 서명 (code signing)은 개발자가 번들에 서명을 붙여, 이 코드가 누구 것이고 서명한 뒤로 바뀌지 않았는지 확인할 수 있게 하는 장치입니다. 서명된 코드에는 모두 지정 요구 사항 (designated requirement, DR)이 있고, 이 식은 어떤 코드가 이 프로그램으로 인정되려면 무엇을 만족해야 하는지를 적습니다 [2]. 번들 안 파일 목록은 리소스 봉투 (resource envelope)에 적고, 안에 든 코드 (nested code)는 그 코드의 서명을 기록합니다 [2]. 서명 자체의 원리와 공증·Gatekeeper 는 [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../01-foundations/protection/codesign-notarization-sip.md)에서, 번들 ID 와 팀 ID 를 읽는 법과 지정 요구 사항의 예는 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)에서 다루고, 이 페이지는 번들 안에서 이 정보를 찾아 읽는 일을 다룹니다.

## 위치와 버전별 차이

앱 번들은 앱이 놓인 곳이 곧 위치라서 정해진 경로가 하나로 정해져 있지 않습니다. 설치한 앱이 어디에 모이고 설치 영수증이 어떻게 남는지는 [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md)에서 다루고, 받은 파일 안이나 디스크 이미지 안, 사용자 폴더 어디에서든 `.app` 폴더를 찾으면 이 페이지 방법으로 읽을 수 있습니다.

| 항목 | 내용 | 출처 |
|---|---|---|
| 번들 폴더 구조와 `Info.plist` 키 | Apple 보관 문서 기준. 최신 Xcode 가 더 넣는 키는 빠져 있음 | [1] |
| 리소스 봉투 버전 1 | macOS 10.9 Mavericks 이전 방식. `Resources` 폴더 파일만 기록 | [2] |
| 리소스 봉투 버전 2 | macOS 10.9 Mavericks 부터. 사실상 모든 파일, 안에 든 코드의 서명, 심볼릭 링크까지 기록 | [2] |
| macOS 10.15 Catalina 이후 공증 요구 | [서명·공증·무결성 보호](../../01-foundations/protection/codesign-notarization-sip.md), [격리 속성과 다운로드 기록](../filesystem/quarantine/index.md)에서 다룸 | — |
| 10.15 이후 버전마다 `Info.plist`·서명 구조가 달라지는 점 | 공개 자료 없음 | — |

이 핸드북이 주로 다루는 macOS 10.15 Catalina 이후에는 리소스 봉투 버전 2가 기준이 되고, 버전 1 서명은 정의상 약한 서명으로 취급하며 리소스 규칙으로 서명을 약하게 만드는 방법도 더는 허용하지 않습니다 [2].

## 구조

### 번들 폴더

`Contents/` 아래에서 자주 보는 폴더는 아래와 같습니다 [1].

| 폴더·파일 | 담는 것 |
|---|---|
| `Info.plist` | 번들 정보 (아래 키 표) |
| `MacOS/` | 앱의 실행 코드(필수). 보통 주 진입점이 든 바이너리 하나 |
| `Resources/` | 리소스 파일. 지역화한 것과 안 한 것을 나눠 둠 |
| `Frameworks/` | 실행 파일이 쓰는 개인 공유 라이브러리와 프레임워크 |
| `PlugIns/` | 앱 기능을 넓히는 적재형 번들 |
| `SharedSupport/` | 앱 실행에 영향이 없는 부가 리소스 |

서명 정보를 담는 파일과 공증 티켓이 번들 안 어느 경로에 놓이는지는 검체의 번들을 열어 확인합니다.

### Info.plist 키

`Info.plist` 는 속성 목록 파일이고, 파일 형식을 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에서 다룹니다. 아래 키는 거의 반드시 넣어야 하는 키입니다 [1].

| 키 | 뜻 |
|---|---|
| `CFBundleName` | 번들의 짧은 이름. 보통 앱 이름 |
| `CFBundleDisplayName` | 지역화한 앱 이름 |
| `CFBundleIdentifier` | 시스템이 앱을 알아보는 문자열. 영문자·숫자·하이픈·마침표만 쓰는 역DNS 형식(예 com.회사.앱) |
| `CFBundleVersion` | 빌드 버전. 마침표로 나눈 정수 하나 이상이고 계속 커지는 값 |
| `CFBundlePackageType` | 번들 종류. 앱은 늘 네 글자 `APPL` |
| `CFBundleSignature` | 번들의 크리에이터 코드(네 글자) |
| `CFBundleExecutable` | 주 실행 파일 이름 |

아래 키는 넣기를 권하는 키입니다 [1].

| 키 | 뜻 |
|---|---|
| `CFBundleDocumentTypes` | 앱이 다루는 문서 종류 |
| `CFBundleShortVersionString` | 출시 버전. 마침표로 나눈 정수 세 개 |
| `LSMinimumSystemVersion` | 앱이 돌아가는 최소 macOS 버전 |
| `NSHumanReadableCopyright` | 저작권 문구 |
| `NSMainNibFile` | 앱을 시작할 때 여는 nib 파일(확장자 뺀 이름) |
| `NSPrincipalClass` | 앱 번들이면 거의 늘 `NSApplication` 이나 그 하위 클래스 |

같은 앱이라도 `CFBundleVersion` 은 빌드마다 커지는 값이고 `CFBundleShortVersionString` 은 사용자에게 보이는 출시 버전이라서 [1], 버전을 적을 때는 두 값을 따로 적습니다.

### 코드 서명과 리소스 봉투

리소스 봉투는 번들 안 파일 목록이고, 버전 2에서는 사실상 모든 파일을 기록하면서 안에 든 코드는 그 코드의 서명을 기록하고 심볼릭 링크도 기록합니다 [2].

안에 든 코드는 정해진 위치에 둡니다 [2].

| 위치 | 담는 코드 |
|---|---|
| `Contents/MacOS` | 도우미 앱·도구 |
| `Contents/Frameworks` | 프레임워크, dylib |
| `Contents/PlugIns` | 플러그인(적재형 번들과 확장 모두) |
| `Contents/XPCServices` | XPC 서비스 |
| `Contents/Helpers` | 도우미 앱·도구 |
| `Contents/Library/Automator` | Automator 동작 |
| `Contents/Library/Spotlight` | Spotlight 가져오기 모듈 |
| `Contents/Library/LoginItems` | 설치형 로그인 항목 |
| `Contents/Library/LaunchServices` | ServiceManagement 프레임워크로 설치하는 권한 있는 도우미 도구 |

이 위치에는 코드만 두어야 하고, 데이터 파일을 두면 서명되지 않은 코드로 보고 서명 검사에서 거부합니다 [2]. 조사에서는 이 표가 번들 안에서 실행될 수 있는 코드를 빠짐없이 훑는 목록 구실을 하고, 특히 `Contents/Library/LoginItems` 와 `Contents/Library/LaunchServices` 는 로그인 항목과 권한 있는 도우미 도구가 놓이는 곳이라서 지속성 조사와 이어집니다.

## 증거로서 의미

**증명하는 것.** `Info.plist` 는 앱이 스스로 밝히는 정체를 보여 주고, `CFBundleIdentifier` 로 앱을 가리키는 다른 기록(권한 목록, 실행 기록, 설정 파일 이름)과 짝을 맞출 수 있습니다. `CFBundleVersion`·`CFBundleShortVersionString` 은 그 번들이 어느 빌드인지를, `LSMinimumSystemVersion` 은 개발자가 정한 최소 macOS 버전을 보여 줍니다 [1]. 서명 검사를 통과하면 번들이 서명할 때 상태에서 바뀌지 않았다는 뜻이고, `spctl` 검사가 `accepted` 와 `source=Developer ID` 를 돌려주면 Gatekeeper 정책으로도 받아들여지는 Developer ID 서명이라는 뜻입니다 [2].

**증명하지 못하는 것.** `Info.plist` 의 값은 개발자가 적어 넣은 문자열이라서, `CFBundleIdentifier` 나 이름이 알려진 앱과 같아도 그 회사가 만든 앱이라는 증거가 되지 않습니다. 누가 만들었는지는 서명과 지정 요구 사항, 팀 ID 로 판단하고, 그 읽는 법은 [번들 ID와 팀 ID](../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다. 번들이 디스크에 있다는 사실만으로 앱을 실행했다고 말할 수도 없어서, 실행 여부는 [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md)의 기록으로 따로 확인합니다. 서명 검사가 통과해도 앱이 무해하다는 뜻은 아니고, 서명이 말하는 범위는 누가 서명했는지와 그 뒤로 바뀌었는지까지입니다.

보고서에는 "이 앱은 ○○사 제품이다" 가 아니라 "이 번들의 `Info.plist` 에는 `CFBundleIdentifier` 가 이 값으로 적혀 있고, `codesign` 검사 결과 서명은 유효했으며 지정 요구 사항은 이 식이었다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

이 페이지에서 다룬 `Info.plist` 키에는 시각을 적는 키가 없습니다 [1]. 번들이 이 맥에 언제 놓였고 언제 바뀌었는지는 번들 폴더와 그 안 파일의 파일 시스템 시각으로 보고, 그 값은 [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md)와 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에서 다룹니다. `codesign` 출력 칸 설명은 [악성 코드 흔적 분석 (Malware Triage)](../../03-techniques/analysis/malware-triage/index.md)을 봅니다.

`CFBundleVersion` 은 빌드마다 커지는 값이라서 [1] 같은 앱의 번들 여럿을 빌드 순서로 늘어놓는 데는 쓸 수 있지만, 그 빌드가 언제 만들어졌는지는 알려 주지 않습니다.

## 함정과 한계

**이름과 번들 ID 는 흉내 낼 수 있습니다.** `CFBundleIdentifier` 가 알려진 앱을 흉내 내거나, `CFBundleExecutable` 이 가리키는 파일과 `MacOS/` 안 실제 파일이 서로 다르면 살펴볼 만한 번들입니다. 다만 이것만으로 단정하지 말고 서명의 지정 요구 사항과 함께 봅니다.

**서명 오류 문구는 조사 단서입니다.** `code object is not signed at all` 은 안에 든 코드가 서명되지 않았거나 서명이 틀렸을 때 나오는 문구입니다. `sealed resource(s) missing or invalid` 는 리소스 봉투와 관련된 문구이고, 번들 맨 위에 파일이나 폴더를 두지 말고 모두 `Contents` 안에 두어야 합니다 [2]. 조사 중에 두 번째 문구를 만나면 서명한 뒤 번들 안 파일이 더해지거나 바뀌었을 가능성을 떠올리고, 어떤 파일이 목록과 어긋나는지를 확인합니다.

**서명 검사 결과는 검사하는 맥에 따라 달라질 수 있습니다.** `spctl` 은 Gatekeeper 정책으로 검사하는 명령이라서 [2], 분석용 맥의 정책 설정이 결과에 끼어들 수 있습니다. 검사한 맥의 macOS 버전과 명령 출력을 그대로 보고서에 남깁니다.

**보관 문서의 한계.** 키 설명은 Apple 보관 문서를 따르고 [1], 최신 Xcode 가 넣는 키는 이 페이지에서 다루지 않습니다. 표에 없는 키가 보여도 이상 징후로 단정하지 않습니다. 코드 서명 자료 [2]도 보관 문서이고 iOS 서명과 공증·스테이플은 다루지 않습니다.

**실행 경로와 번들 경로가 다를 수 있습니다.** Gatekeeper 는 무해한 앱에 악성 플러그인을 끼워 배포하는 일을 막으려고 받은 앱을 무작위 이름의 읽기 전용 위치에서 열기도 합니다 [3]. 그래서 실행 기록에 남은 경로가 번들이 실제로 놓인 경로와 다를 수 있습니다. 이 동작은 [서명·공증·무결성 보호](../../01-foundations/protection/codesign-notarization-sip.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 [1]의 키 설명으로 만든 예시이고, 특정 검체에서 나온 값이 아닙니다. `Info.plist` 가 XML 로 저장되어 있으면 키와 값이 글자 그대로 보입니다.

```xml
<key>CFBundleIdentifier</key>
<string>com.example.sample</string>
<key>CFBundlePackageType</key>
<string>APPL</string>
<key>CFBundleExecutable</key>
<string>Sample</string>
```

헥스 편집기에서는 오른쪽 글자 칸에서 `CFBundleIdentifier` 같은 키 이름을 찾고, 바로 뒤의 값을 읽습니다. `APPL` 네 글자는 ASCII 바이트로 `41 50 50 4C` 입니다. XML 이 아닌 형식으로 저장된 파일이면 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)의 방법으로 먼저 풀어서 읽습니다. 헥스로 찾은 `CFBundleExecutable` 값과 `MacOS/` 폴더 안 파일 이름이 같은지 한 번 대 보면, 도구가 보여 준 값을 그대로 믿지 않고 확인할 수 있습니다.

### 공개 도구로 한 번

macOS 에 기본으로 들어 있는 `codesign` 과 `spctl` 로 서명을 읽습니다 [2]. 원본 증거 대신 사본에서 꺼낸 번들로 작업하고, 이미지를 다루는 절차는 [맥 증거 확보 (Acquisition)](../../03-techniques/process-acquisition/evidence-acquisition/index.md)를 따릅니다.

1. 번들 안 `Info.plist` 를 속성 목록 도구로 열어 위 키 표의 값을 적습니다.
2. `codesign -dvvvv /path/to/code` 로 서명 정보를 자세히 봅니다 [2]. 출력의 `Sealed Resources version=2` 같은 줄에서 리소스 봉투 버전을 확인합니다 [2].
3. `codesign -d -r- /path/to/code` 로 지정 요구 사항을 봅니다. 예를 들면 `# designated => identifier "com.apple.md5" and anchor apple` 처럼 나옵니다 [2].
4. `codesign --verify --deep --strict --verbose=2 Foo.app` 으로 안에 든 코드까지 서명을 검사하고, 오류 문구가 나오면 그대로 적습니다 [2].
5. `spctl -a -t exec -vv Foo.app` 으로 Gatekeeper 정책 검사를 하고, 통과하면 `Foo.app: accepted` 와 `source=Developer ID` 가 나옵니다 [2].
6. 위 안에 든 코드 위치 표의 폴더를 하나씩 열어, 각 코드도 같은 방법으로 검사합니다.

의심스러운 번들을 여럿 한꺼번에 훑는 순서는 [악성 코드 흔적 분석 (Malware Triage)](../../03-techniques/analysis/malware-triage/index.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) | 설치 패키지로 들어온 앱의 설치 기록 |
| [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) | 번들을 받은 시각과 받은 앱 |
| [다운로드 출처 속성 (kMDItemWhereFroms)](../filesystem/where-froms.md) | 번들이나 그 디스크 이미지를 받은 주소 |
| [실행 정책 평가 기록 (ExecPolicy·Gatekeeper)](../execution/execpolicy-gatekeeper.md) | Gatekeeper 가 이 앱을 평가한 기록 |
| [KnowledgeC (knowledgeC.db)](../execution/knowledgec/index.md) | 번들 ID 로 남은 앱 사용 기록 |
| [개인 정보 보호 권한 (TCC)](../credentials/tcc/index.md) | 번들 ID 로 남은 권한 허용 기록 |
| [로그인 항목 (Login Items)](../persistence/login-items.md) | 번들 안 로그인 항목이 실제로 등록되었는지 |
| [실행 에이전트·데몬 (LaunchAgents·LaunchDaemons)](../persistence/launchd/index.md) | 번들 안 도우미 도구를 띄우는 설정 |
| [보안 도구 기록 (XProtect)](../logs/xprotect.md) | 알려진 악성 내용 검사 기록 |

받은 앱이 어떻게 들어와 실행되었는지 따라가는 순서는 [악성 코드는 어디서 들어왔나 (Initial Access)](../../04-scenarios/incident/initial-access.md)와 [악성 코드 지속성 찾기 (Persistence)](../../04-scenarios/incident/persistence.md)에 정리했습니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 사용자가 설치한 앱이 들어 있는 macOS 이미지를 골라 아래 질문을 풀어 봅니다.

1. 앱 번들 하나를 골라 `CFBundleIdentifier`·`CFBundleVersion`·`CFBundleShortVersionString`·`LSMinimumSystemVersion` 을 적고, 두 버전 값이 무엇을 뜻하는지 구분해 설명할 수 있나요?
2. `CFBundleExecutable` 값과 `MacOS/` 안 실제 파일 이름이 같은가요?
3. 번들 안의 안에 든 코드 위치 표 폴더를 모두 열어 보고, 코드가 아닌 파일이 놓여 있지는 않나요?
4. `codesign` 으로 지정 요구 사항을 뽑아, 식 안의 식별자가 `Info.plist` 의 번들 ID 와 같은지 확인할 수 있나요?
5. 같은 번들 ID 가 격리 속성, 실행 기록, 권한 기록에도 나오는지 찾아 한 줄로 늘어놓을 수 있나요?

## 참고 문헌

1. Apple, "Bundle Programming Guide — Bundle Structures" (보관 문서) — https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFBundles/BundleTypes/BundleTypes.html
2. Apple, "Technical Note TN2206: macOS Code Signing In Depth" (보관 문서) — https://developer.apple.com/library/archive/technotes/tn2206/_index.html
3. Apple Platform Security, "Gatekeeper and runtime protection in macOS" — https://support.apple.com/guide/security/gatekeeper-and-runtime-protection-sec5599b66df/web
