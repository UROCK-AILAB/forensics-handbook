---
title: "속성 목록 파일"
parent: "기반 · 데이터 저장 형식"
nav_order: 130
has_children: true
has_toc: false
---

# 속성 목록 파일 (Property List)

속성 목록 파일 (Property List, plist)은 macOS에서 앱 설정과 앱이 보관한 객체를 담는 데 쓰는 파일 형식이고, 같은 값 구조를 XML이나 바이너리(`bplist00`)로 저장합니다.

## 왜 중요한가

앱 설정(기본 설정, defaults)은 사용자 홈의 `Library/Preferences` 아래에 앱마다 plist 파일로 저장되고 [4], 앱이 객체를 통째로 보관하는 NSKeyedArchiver 형식도 결과를 plist로 씁니다 [3]. 그래서 설정값 하나를 확인하든 앱이 남긴 기록을 풀든 plist를 읽는 일이 먼저이고, 다른 아티팩트 페이지도 이 형식을 안다고 보고 설명합니다.

이 묶음은 형식을 읽는 법뿐만 아니라 값을 해석할 때의 주의점까지 다룹니다. defaults 값을 쓰면 메모리의 값이 먼저 바뀌고 디스크에는 비동기로 씁니다 [5]. 게다가 앱은 여러 도메인 가운데 앞 순서 도메인의 값을 쓰기 때문에 [4][5], 파일 하나의 내용만 보고 그 순간의 설정이라고 단정하지 않습니다. 또 defaults는 값을 암호화하지 않고 저장하기 때문에 [5], 앱이 넣어 둔 값을 그대로 읽을 수 있습니다.

## 한눈에 보기

| 구분 | 알아보는 법 | 위치·버전 | 알려 주는 것 |
|---|---|---|---|
| XML plist | Apple DTD를 따르는 XML 문서 [2] | 아티팩트마다 다름. 날짜는 UTC 초 단위 문자열 [2] | 사전·배열·문자열·숫자·날짜·데이터 값 |
| 바이너리 plist | 첫 8바이트 `bplist00` [1][2] | 구조는 옛 공개판 CF 소스 기준이고 [1], macOS 10.15 이후 파일은 실제 파일로 구조를 확인 | XML과 같은 값. 날짜는 2001-01-01 00:00:00 GMT 기준 초(float64) [1][6] |
| NSKeyedArchiver | 최상위 키 `$archiver`·`$version`·`$objects`·`$top` [3] | plist 안의 한 방식이라 위치는 아티팩트마다 다름. 기본 출력은 바이너리 [3] | 앱 객체의 클래스 이름과 저장한 값 |
| 기본 설정(defaults) | 번들 ID 이름의 plist [4] | `$HOME/Library/Preferences/` 아래 [4] | 앱별 설정값. 휘발 도메인의 값은 남지 않음 [4][5] |

## 읽는 순서

1. [XML·바이너리 plist (XML·bplist00)](xml-binary.md) — XML 요소 규칙과 바이너리의 헤더·객체 표식·오프셋 테이블·트레일러를 헥스 예시로 따라가고, 손상된 파일을 가려내는 읽기 검사 조건을 정리합니다.
2. [NSKeyedArchiver 풀기 (NSKeyedArchiver)](nskeyedarchiver.md) — `$top` 에서 시작해 uid 번호를 따라가며 클래스 이름과 키를 붙여 앱이 보관한 객체를 푸는 순서를 다룹니다.
3. [기본 설정 도메인과 캐시 (Defaults·cfprefsd)](defaults-cfprefsd.md) — 도메인 검색 순서와 저장 위치, 메모리 값과 파일 사이의 시차를 증거 해석과 함께 다룹니다.

## 함께 볼 페이지

- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../value-decoding/mac-time-values.md) — plist 날짜 값을 바꿀 때
- [번들 ID와 팀 ID (Bundle ID·Team ID)](../../value-decoding/bundle-team-id.md) — 설정 파일 이름의 번들 ID를 읽을 때
- [SQLite 데이터베이스 (SQLite)](../sqlite/index.md) — 또 하나의 주요 저장 형식
- [키체인 (Keychain)](../../protection/keychain/index.md) — 민감한 정보를 두는 곳
- [구성 프로파일 (Configuration Profiles·MDM)](../../../02-artifacts/persistence/configuration-profiles.md) — 관리 기기의 설정을 볼 때
- [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md) — 실행 중인 시스템에서 설정 파일을 수집할 때
- [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md) — 지워진 plist를 카빙할 때
- [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md) — plist 도구의 결과를 헥스와 맞춰 볼 때

## 참고 문헌

1. Apple CF 공개 소스, CFBinaryPList.c (저작권 2000-2014/2015) — https://raw.githubusercontent.com/apple-oss-distributions/CF/main/CFBinaryPList.c
2. Apple, PropertyList-1.0.dtd — https://www.apple.com/DTDs/PropertyList-1.0.dtd
3. Apple swift-corelibs-foundation, NSKeyedArchiver.swift — https://raw.githubusercontent.com/apple/swift-corelibs-foundation/main/Sources/Foundation/NSKeyedArchiver.swift
4. Apple, Preferences and Settings Programming Guide — About the User Defaults System (Updated 2013-10-22) — https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/UserDefaults/AboutPreferenceDomains/AboutPreferenceDomains.html
5. Apple Developer Documentation, UserDefaults (문서 JSON) — https://developer.apple.com/tutorials/data/documentation/foundation/userdefaults.json
6. Apple Developer Documentation, CFAbsoluteTime — https://developer.apple.com/documentation/corefoundation/cfabsolutetime
