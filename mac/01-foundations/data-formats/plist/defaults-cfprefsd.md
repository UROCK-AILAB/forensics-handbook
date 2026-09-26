---
title: "기본 설정 도메인과 캐시"
parent: "속성 목록 파일"
grand_parent: "기반 · 데이터 저장 형식"
nav_order: 160
---

# 기본 설정 도메인과 캐시 (Defaults·cfprefsd)

앱 설정(기본 설정, defaults)은 도메인 여러 개에 나뉘어 있고 앞 도메인의 값이 뒤 도메인의 같은 키를 가리며, 앱 도메인은 `Library/Preferences` 아래 plist 파일로 남지만 휘발 도메인은 디스크에 남지 않습니다. 값을 쓰면 메모리 쪽 값이 먼저 바뀌고 파일은 나중에 따로 쓰이기 때문에, 파일 하나만 보고 앱이 그 순간 쓰던 값을 단정하지 않습니다.

## 이 형식을 쓰는 아티팩트

앱 도메인의 설정은 아래 경로에 번들 ID 이름의 plist로 저장됩니다 [1]. 번들 ID를 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../value-decoding/bundle-team-id.md)에서 다룹니다.

```
$HOME/Library/Preferences/<번들 ID>.plist
```

`$HOME` 은 플랫폼과 샌드박스 여부에 따라 앱 홈 디렉터리이기도 하고 사용자 홈 디렉터리이기도 합니다 [1]. 샌드박스 앱의 실제 경로, 전역 도메인·시스템 전체·기기별·관리 설정 파일의 경로, 앱 그룹 설정 파일의 위치는 공개 자료가 없어 검체에서 확인합니다.

cfprefsd 프로세스가 캐시를 어떻게 맡는지, 사용자별·시스템별 인스턴스가 어떻게 나뉘는지, 어느 버전에 들어왔는지, 파일을 새로 쓸 때 inode가 바뀌는지는 Apple 문서에 설명이 없어 검체에서 확인합니다. 아래에서는 Apple 문서에 나온 캐시 동작을 씁니다. 파일 자체의 형식은 [XML·바이너리 plist (XML·bplist00)](xml-binary.md)에서 다룹니다.

## 구조 — 도메인과 검색 순서

앱이 키 하나를 찾을 때는 도메인을 정해진 순서로 뒤지고, 같은 키가 여러 도메인에 있으면 앞쪽 도메인의 값을 씁니다 [1]. 도메인은 디스크에 남는 영구 도메인과 앱이 끝나면 버리는 휘발 도메인으로 나뉩니다 [1][2].

현행 UserDefaults 문서의 순서는 다음과 같습니다 [2].

| 순서 | 도메인 | 종류 | 설명 |
|---|---|---|---|
| 1 | Managed | 영구 | 관리자가 넣은 설정이고 관리 기기에만 있음. 앱은 여기에 쓸 수 없음 |
| 2 | Argument | 휘발 | 명령줄이나 Xcode에서 실행할 때 준 값. 앱이 끝나면 버림 |
| 3 | Educational managed | 영구(서버에 저장) | 교육용 관리 기기의 설정 |
| 4 | App | 영구 | 앱 자기 도메인 |
| 5 | Suite | 영구 | 앱 그룹 등, `addSuite` 로 추가한 도메인 |
| 6 | Global | 영구 | 모든 앱에 적용되는 키. 앱은 여기에 쓸 수 없음 |
| 7 | Registration | 휘발 | 앱이 시작할 때 등록하는 기본값. 앱이 끝나면 버림 |

2013-10-22에 갱신한 옛 가이드는 순서를 조금 다르게 적었습니다 [1].

| 순서 | 도메인 | 종류 |
|---|---|---|
| 1 | `NSArgumentDomain` | 휘발 |
| 2 | 앱 도메인(앱 식별자) | 영구 |
| 3 | `NSGlobalDomain` | 영구 |
| 4 | 언어 도메인 | 휘발 |
| 5 | `NSRegistrationDomain` | 휘발 |

언어 도메인은 `AppleLanguages` 에 든 언어마다 언어 이름으로 만든 도메인입니다 [1]. 옛 가이드에는 Managed·Educational managed·Suite 도메인이 없고 현행 문서에는 언어 도메인이 없어서, 도메인 구성과 순서는 두 문서의 발행 시기를 밝혀 인용합니다. 관리 기기의 설정이 어디서 오는지는 [구성 프로파일 (Configuration Profiles·MDM)](../../../02-artifacts/persistence/configuration-profiles.md)에서 다룹니다.

## 읽는 법

디스크 이미지에서 "이 앱의 이 설정값이 무엇이었나" 를 따질 때는 아래 순서로 봅니다.

1. 앱의 번들 ID를 확인하고 앱 도메인 plist를 찾습니다 [1].
2. 파일 형식(XML 또는 바이너리)을 확인하고 값을 읽습니다. 값이 NSKeyedArchiver로 보관된 데이터라면 [NSKeyedArchiver 풀기 (NSKeyedArchiver)](nskeyedarchiver.md)의 순서로 풉니다.
3. 같은 키가 앞 순서의 영구 도메인(관리 설정 등)에도 있는지 확인합니다. 앞 도메인에 값이 있으면 앱 도메인 파일의 값은 실제로 쓰이지 않았을 수 있습니다 [2].
4. 키가 어느 영구 도메인에도 없으면, 앱이 Registration 도메인에 등록한 기본값을 썼을 수 있습니다. 이 기본값은 휘발 도메인이라서 디스크 파일로는 알 수 없습니다 [2].

## 포렌식에서 중요한 점

### 메모리 쪽 값과 파일 사이의 시차

defaults 값을 쓰면 메모리의 값이 바로 바뀌고 디스크에는 비동기로 씁니다 [2]. 그래서 실행 중인 시스템에서 plist 파일만 복사하면 아직 디스크에 쓰지 않은 값이 빠질 수 있고, 수집 시점의 파일 내용과 실행 중인 앱이 보는 값이 잠시 다를 수 있습니다. 라이브 수집 보고서에는 파일을 복사한 시각과 그 순간 앱이 실행 중이었는지를 함께 적어 둡니다. 수집 절차는 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md)에서 다룹니다.

### 파일을 직접 고친 흔적

defaults 파일을 파일 시스템에서 직접 고치면 데이터가 사라지거나 변경이 늦게 반영되거나 앱이 멈출 수 있어서, macOS에서는 `defaults` 명령으로 보거나 고칩니다 [2]. 파일을 직접 여는 것은 디버깅할 때 들여다보는 용도입니다 [1]. 그래서 누군가 plist 파일을 직접 고쳤더라도 그 뒤에 실행 중인 프로세스가 메모리의 값으로 파일을 다시 써서 고친 흔적이 덮일 수 있습니다. 설정 파일 조작이 의심되면 파일 하나의 현재 내용보다 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md)처럼 시점이 다른 사본을 나란히 놓고 봅니다.

### 휘발 도메인은 남지 않음

Argument·Registration·언어 도메인은 앱이 끝나면 버리는 휘발 도메인이라서 [1][2], 디스크 이미지에서 볼 수 있는 값은 영구 도메인의 값뿐입니다. 명령줄 인자로 준 설정은 이 방식으로는 남지 않으니, 실행 인자는 [통합 로그의 프로세스 실행 기록 (Process Events)](../../../02-artifacts/execution/unified-log-process.md)이나 [터미널 명령 기록 (zsh_history·bash_sessions)](../../../02-artifacts/execution/shell-history.md)처럼 다른 기록에 남았는지 찾아봅니다.

### 암호화하지 않은 저장과 백업

defaults 시스템은 값을 디스크에 암호화하지 않은 채 저장하고, 민감한 정보는 [키체인 (Keychain)](../../protection/keychain/index.md)에 두게 되어 있습니다 [2]. 앱이 토큰이나 계정 정보를 defaults에 넣었다면 plist 파일에서 그대로 읽힐 수 있습니다. defaults는 백업에 들어가고 기기 사이에는 공유되지 않아서(교육용 관리 기기는 예외) [2], 백업 사본도 확인 대상에 넣습니다.

## 함정

- **파일 값이 곧 쓰던 값은 아님**: 앞 순서의 도메인이 같은 키를 가리거나, 휘발 도메인의 값이 쓰였을 수 있습니다 [1][2].
- **문서마다 다른 순서**: 옛 가이드와 현행 문서의 도메인 구성이 다릅니다 [1][2]. 인용할 때는 어느 문서인지 밝힙니다.
- **라이브 복사의 시차**: 비동기 쓰기 때문에 복사한 파일이 최신 값이 아닐 수 있습니다 [2].
- **공개 자료가 없는 경로**: 샌드박스 컨테이너·전역·기기별·관리 설정 파일의 경로는 검체에서 확인하고, 찾은 경로에는 macOS 버전을 붙여 적습니다.

## 도구

macOS에서는 `defaults` 명령으로 설정을 보거나 고칩니다 [2]. 디스크 이미지에서는 plist 파일을 직접 읽고 [XML·바이너리 plist (XML·bplist00)](xml-binary.md)의 방법으로 도구 결과를 헥스와 맞춰 봅니다. 증거 확보 단계에서 파일을 어떻게 떠 오는지는 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)에서 다룹니다.

## 참고 문헌

1. Apple, Preferences and Settings Programming Guide — About the User Defaults System (Updated 2013-10-22) — https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/UserDefaults/AboutPreferenceDomains/AboutPreferenceDomains.html
2. Apple Developer Documentation, UserDefaults (문서 JSON) — https://developer.apple.com/tutorials/data/documentation/foundation/userdefaults.json
