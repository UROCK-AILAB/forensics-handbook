---
title: "번들 ID와 팀 ID"
parent: "기반 · 값 읽는 법"
nav_order: 320
---

# 번들 ID와 팀 ID (Bundle ID·Team ID)

맥의 기록은 앱을 `com.apple.TextEdit` 같은 번들 ID 로 가리키는 일이 많지만 번들 ID 는 개발자가 마음대로 적는 문자열이라서, 어느 개발자의 코드인지는 코드 서명 인증서에 든 팀 ID 와 지정 요구사항으로 판단합니다.

## 이 형식을 쓰는 아티팩트

번들 ID 와 팀 ID 가 확정된 형태로 드러나는 곳은 앱의 코드 서명입니다. 코드 서명에는 코드 서명 식별자(code signing identifier)와 팀 ID, 그리고 둘을 묶은 지정 요구사항(designated requirement)이 들어 있습니다[1].

| 값 | 어디에 있나 | 예 (TN3127) |
|---|---|---|
| 코드 서명 식별자 | 코드 서명 안, 서명한 쪽이 정함 | `com.apple.TextEdit`, `com.apple.iWork.Numbers`, `com.example.apple-samplecode.AppWithTool` |
| 팀 ID | 서명 인증서 가운데 말단(leaf) 인증서의 `subject.OU`(조직 단위) | `SKMME9E2Y8`, `K36BKF7T3D` (Numbers) |
| 지정 요구사항 | 코드 서명 안, 이 코드를 같은 코드로 인정할 조건 | 아래 "구조" 절 |

앱의 설정 파일, 실행 기록, 다운로드 기록, 로그인 항목처럼 번들 ID 나 팀 ID 로 앱을 가리키는 아티팩트는 여럿이고, 어느 필드에 어떤 이름으로 남는지는 각각 [앱 번들 정보](../../02-artifacts/embedded-metadata/app-bundle.md), [KnowledgeC](../../02-artifacts/execution/knowledgec/index.md), [격리 속성과 다운로드 기록](../../02-artifacts/filesystem/quarantine/index.md), [로그인 항목](../../02-artifacts/persistence/login-items.md) 에서 다룹니다. 서명·공증 체계 전체는 [서명·공증·무결성 보호](../protection/codesign-notarization-sip.md)에서 다룹니다.

## 구조

### 번들 ID 와 서명 식별자

코드 서명 식별자는 서명한 쪽이 정하는 문자열입니다[1]. 번들 형태의 코드는 보통 번들 ID 를 서명 식별자로 쓰지만 서명자가 다른 값을 넣을 수도 있어서, 번들 ID 와 서명 식별자가 늘 같지는 않습니다.

### 팀 ID

팀 ID 는 개발 팀마다 다른 값이고, Apple 이 발급한 서명 인증서 가운데 말단 인증서의 `subject.OU` 필드에 들어 있습니다. 팀 ID 의 예는 모두 영문 대문자와 숫자 10자입니다[1]. 이 길이와 글자 구성은 예에서 보이는 형태일 뿐이라서, 정해진 규칙으로 보지 않습니다.

### 지정 요구사항

지정 요구사항은 "어떤 조건을 만족하면 이 코드와 같은 코드로 본다" 를 적은 식이고, 서명 종류별 예는 아래와 같습니다[1].

| 서명 종류 | 지정 요구사항 (TN3127 의 예) |
|---|---|
| Apple 자체 코드 (TextEdit) | `identifier "com.apple.TextEdit" and anchor apple` |
| Developer ID 로 서명한 앱 | `anchor apple generic and identifier "..." and (LeafIsMacAppStore or IssuerIsDeveloperID and LeafIsDeveloperIDApp and certificate leaf[subject.OU] = SKMME9E2Y8)` 형태 |
| Mac App Store 앱 (Numbers) | `anchor apple generic` 에 인증서 OID 확장이 있어야 한다는 조건(`1.2.840.113635.100.6.1.9` 등), `certificate leaf[subject.OU] = K36BKF7T3D`, `identifier "com.apple.iWork.Numbers"` 를 더한 형태 |
| Apple Development 로 서명한 코드 | `anchor apple generic` 에 `certificate leaf[subject.CN] = "Apple Development: …"` 와 `certificate 1[field.1.2.840.113635.100.6.2.1] /* exists */` 를 더한 형태 |

Developer ID 줄의 `LeafIsMacAppStore`·`IssuerIsDeveloperID`·`LeafIsDeveloperIDApp` 는 설명용으로 줄여 쓴 이름이라서 `codesign` 출력에는 나오지 않습니다[1]. 실제 출력에는 각각 `certificate leaf[field.1.2.840.113635.100.6.1.9] /* exists */`, `certificate 1[field.1.2.840.113635.100.6.2.6] /* exists */`, `certificate leaf[field.1.2.840.113635.100.6.1.13] /* exists */` 로 나옵니다.

`anchor apple` 은 Apple 이 자기 코드에 서명한 경우만 받아들이고, `anchor apple generic` 은 Apple 이 발급한 서명 인증서라면 어느 것이든 받아들입니다. 그래서 Apple 자체 코드의 요구사항에는 팀 ID 가 없고, 외부 개발자 앱의 요구사항에는 `certificate leaf[subject.OU]` 로 팀 ID 가 들어갑니다[1].

## 읽는 법

지정 요구사항을 읽고 검사하는 명령은 두 가지입니다[1]. 증거 원본 대신 확보한 사본의 앱 번들 경로를 넣어 실행합니다.

```text
codesign --display -r - <앱 경로>
    → 지정 요구사항을 출력합니다.
      예: designated => identifier "com.apple.TextEdit" and anchor apple

codesign --verify -v -R '<요구사항>' <앱 경로>
    → 이 앱이 -R 로 넘긴 요구사항을 만족하는지 검사합니다.
```

앱 하나를 읽는 순서는 다음과 같습니다.

1. `codesign --display -r -` 로 지정 요구사항을 출력합니다.
2. `identifier "..."` 부분에서 서명 식별자를 읽고, 기록에 남은 번들 ID 와 같은지 봅니다.
3. `anchor apple` 인지 `anchor apple generic` 인지 봅니다. 앞쪽이면 Apple 자체 코드입니다.
4. `certificate leaf[subject.OU] = ...` 가 있으면 그 값을 팀 ID 로 적습니다.
5. 같은 번들 ID 를 쓰는 다른 사본이나 기록이 있으면, 4단계의 팀 ID 로 `codesign --verify -R` 을 돌려 같은 개발자의 코드인지 확인합니다.

`codesign -dv` 같은 다른 출력에서 팀 ID 가 어떤 줄로 나오는지, 서명이 없거나 애드혹으로 서명한 코드에서 팀 ID 가 어떻게 표시되는지는 분석에 쓰는 맥에서 직접 실행해 확인합니다.

## 포렌식에서 중요한 점

번들 ID 는 누구나 적을 수 있는 문자열이라서, 번들 ID 가 같아도 팀 ID 나 서명 주체가 다르면 다른 개발자의 코드일 가능성이 큽니다. 실행 기록이나 로그인 항목에 알려진 앱의 번들 ID 가 보여도 그것만으로 정상 앱이 돌았다고 적지 않고, 디스크에 남은 앱 번들의 팀 ID 와 지정 요구사항을 함께 확인합니다. 알려진 앱을 흉내 낸 코드를 가려내는 흐름은 [악성 코드 흔적 분석](../../03-techniques/analysis/malware-triage/index.md)과 [악성 코드 지속성 찾기](../../04-scenarios/incident/persistence.md)에서 다룹니다.

팀 ID 는 한 개발 팀이 만든 여러 앱을 묶는 열쇠로도 씁니다. 번들 ID 가 서로 다른 앱들이 같은 팀 ID 를 쓰면 같은 팀이 서명했다고 볼 수 있고, 이 묶음으로 한 개발자의 도구가 맥에 몇 개 있었는지 셀 수 있습니다.

앱을 지운 뒤에는 코드 서명을 다시 읽을 수 없어서, 기록에 남은 번들 ID 나 팀 ID 문자열만 남습니다. 이때는 그 문자열로 확인되는 만큼만 적습니다. 보고서에는 "이 번들 ID 로 기록된 앱이 이 시각에 실행된 기록이 있다" 처럼 쓰고, 서명을 확인하지 못했다는 점을 함께 적습니다.

## 함정

번들 ID 와 서명 식별자를 같은 값으로 여기기 쉽지만 서명자는 다른 식별자를 넣을 수 있습니다[1]. 기록의 번들 ID 와 `identifier "..."` 가 다르면 그 자체로 이상하다고 단정하지 말고, 같은 앱의 다른 판과 비교해 봅니다.

`anchor apple generic` 만 보고 Apple 이 만든 코드라고 읽으면 틀립니다. 이 조건은 Apple 이 발급한 인증서로 서명했다는 뜻이고, Apple 자체 코드는 `anchor apple` 입니다.

`codesign` 결과를 적을 때는 분석에 쓴 맥의 macOS 버전도 함께 적어 두어야 나중에 같은 조건으로 다시 확인할 수 있습니다. 앱 컨테이너 폴더 이름에 번들 ID 가 쓰이는지, 그룹 컨테이너 이름에 팀 ID 가 앞에 붙는지는 실제 데이터로 확인합니다.

## 도구

| 도구 | 쓰임 |
|---|---|
| `codesign` (macOS 기본 명령) | 지정 요구사항 출력(`--display -r -`)과 요구사항 검사(`--verify -v -R`) |

도구 결과를 보고서에 옮길 때는 출력 원문을 그대로 붙이고, 해석은 따로 적습니다. 도구 출력을 검증하는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 참고 문헌

1. Apple, TN3127: Inside Code Signing: Requirements (문서 JSON), https://developer.apple.com/tutorials/data/documentation/technotes/tn3127-inside-code-signing-requirements.json
