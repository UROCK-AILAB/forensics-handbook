---
title: "설정 XML과 SharedPreferences"
parent: "기반 · 데이터 저장 형식"
nav_order: 200
---

# 설정 XML과 SharedPreferences (XML·SharedPreferences)

공유 환경설정 (SharedPreferences) 은 앱이 작은 설정 값을 키와 값으로 저장하는 안드로이드 기본 방식이고, 파일은 텍스트 XML 로 남으며 쓰기가 끝나지 못하면 직전 내용을 담은 `.bak` 파일이 함께 남습니다.

## 이 형식을 쓰는 아티팩트

앱은 로그인 여부, 기능을 켰는지, 마지막으로 무엇을 했는지 같은 작은 값을 공유 환경설정에 넣을 수 있고, 어떤 키에 무엇을 넣는지는 앱마다 다릅니다. 파일은 앱 데이터 폴더 안에 있으며 폴더 짜임은 [앱 데이터 폴더 구조](../storage/app-data-layout.md) 에서 다룹니다. 저장과 읽기는 AOSP 의 `android.app.SharedPreferencesImpl` 이 맡기 때문에, SharedPreferences API 로 값을 쓰는 앱이라면 아래의 쓰기 순서와 `.bak` 규칙이 똑같이 적용됩니다.

Google 은 SharedPreferences 를 쓰는 앱에 Jetpack DataStore 로 옮기라고 권하고, DataStore 에는 SharedPreferences 의 값을 옮겨 오는 기능이 들어 있습니다. 그래서 최근 앱은 설정을 이 XML 대신 `files/datastore/` 아래의 프로토콜 버퍼 파일에 둘 수 있고, 그 형식은 [프로토콜 버퍼](protobuf.md) 에서 설명합니다. 옮긴 뒤 옛 XML 파일이 지워지는지는 이 페이지의 출처로 확인되지 않아서 두 곳을 모두 보는 편이 안전합니다.

제목의 "설정 XML" 에는 시스템 설정도 들어갑니다. 시스템 설정 값(global·secure·system)은 기기에서 `settings` 명령으로 키 이름을 읽을 수 있고, 키는 영역마다 수백 개씩 나올 수 있습니다(예: global 596개, secure 464개, system 582개). 이 값이 디스크의 어느 파일에 어떤 형식으로 저장되는지는 이 페이지에서 확인하지 않았고, 키마다 무엇을 뜻하는지는 [설정 값](../../02-artifacts/system-account/settings.md) 에서 다룹니다. 시스템 서비스가 쓰는 XML 은 텍스트가 아니라 바이너리일 수 있으니 [안드로이드 바이너리 XML](abx.md) 도 함께 봅니다.

## 구조

공유 환경설정 파일 하나에는 앱이 정한 설정 묶음 하나의 키와 값이 모두 들어 있습니다. AOSP 코드에서 확인한 동작은 다음과 같습니다.

| 항목 | 동작 | AOSP 코드 |
|---|---|---|
| 파일 쓰기 | 키와 값의 맵을 XML 로 씀 | `XmlUtils.writeMapXml(...)` |
| 파일 읽기 | XML 을 읽어 맵으로 되돌림 | `XmlUtils.readMapXml(...)` |
| 백업 파일 이름 | 원래 경로 뒤에 `.bak` 을 붙임 | `new File(prefsFile.getPath() + ".bak")` |
| 디스크 반영 | 쓴 뒤 디스크에 강제로 내림 | `FileUtils.sync(str)` |
| 파일 권한 | 앱이 넘긴 모드로 권한을 정함 | `ContextImpl.setFilePermissionsFromMode(mFile.getPath(), mMode, 0)` |

파일 안의 태그 이름과 값 형식 표시는 `XmlUtils` 가 정하고, 이 페이지에서는 따로 정리하지 않습니다. 실제 파일을 열어 태그 이름을 그대로 읽으면 됩니다.

쓰기는 기존 파일을 치우는 데서 시작합니다. `.bak` 이 아직 없으면 기존 파일의 이름을 원래 이름 뒤에 `.bak` 을 붙인 이름으로 바꾸고, 이름 바꾸기가 실패하면 이번 쓰기를 포기합니다. `.bak` 이 이미 있으면 그 `.bak` 을 그대로 두고 본 파일만 지웁니다. 그다음 원래 이름으로 새 파일을 만들어 맵 전체를 쓰고, `FileUtils.sync` 로 디스크에 강제로 내린 뒤 `.bak` 을 지웁니다. 쓰다가 실패하면 쓰다 만 본 파일을 지우기 때문에 `.bak` 만 남습니다. 메모리의 값이 디스크보다 새롭지 않으면 파일을 다시 쓰지 않고 건너뜁니다.

읽을 때는 반대 방향으로 확인합니다. `.bak` 이 남아 있으면 본 파일을 지우고 `.bak` 을 본 파일 이름으로 되돌린 다음 읽습니다.

> 그림 자리: 쓰기 전·쓰는 중·쓴 뒤에 폴더에 남는 파일(본 파일과 `.bak`)이 어떻게 바뀌는지 세 단계로 나눠 보여 주는 그림

## 읽는 법

1. 파일 앞 4바이트를 헥스로 봅니다. `41 42 58 00`(ASCII `ABX` 와 0)이면 [안드로이드 바이너리 XML](abx.md) 이고, 그렇지 않으면 텍스트 XML 입니다. `SharedPreferencesImpl.java` 에는 바이너리 XML 을 고르는 코드가 없어서 앱 설정 파일은 대개 텍스트로 읽히지만, `XmlUtils` 내부 구현이 버전마다 바뀌는지는 확인되지 않아 앞 4바이트를 먼저 봅니다.
2. 같은 폴더에 같은 이름 뒤에 `.bak` 이 붙은 파일이 있는지 봅니다. 있으면 두 파일을 따로 읽어 비교합니다(아래 "포렌식에서 중요한 점").
3. 텍스트 XML 이면 편집기나 XML 파서로 열어 키와 값을 표로 옮깁니다. 키 이름은 앱 개발자가 붙인 것이라, 이름이 뜻을 짐작하게 하더라도 앱을 직접 써 보며 확인하기 전에는 추정으로 적습니다.
4. 시각처럼 보이는 큰 숫자는 초인지 밀리초인지부터 구분하고, 단위는 [시각 값](../value-decoding/time-values.md) 에서 확인합니다.

앱마다 어떤 키를 보면 되는지는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md) 과 각 앱 페이지에서 다룹니다.

## 포렌식에서 중요한 점

정상적으로 끝난 쓰기라면 `.bak` 을 지우기 때문에, 이미지에 `이름.xml.bak` 이 남아 있으면 마지막 쓰기가 끝나지 못했을 수 있습니다. 쓰는 도중 전원이 꺼지거나 앱이 강제로 끝난 경우에는 본 파일이 쓰다 만 상태로 남을 수 있고, 쓰기가 실패해 코드가 본 파일을 지운 경우에는 `.bak` 만 남습니다. 어느 쪽이든 `.bak` 쪽이 마지막으로 제대로 쓴 내용입니다. 이 해석은 AOSP 코드의 흐름에서 끌어낸 것이라, 보고서에는 "마지막 쓰기가 끝나지 않았을 가능성이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

실행 중인 기기에서는 이 흔적이 쉽게 사라집니다. 앱이 다음에 설정 파일을 디스크에서 불러오는 순간 본 파일을 지우고 `.bak` 을 되돌리기 때문에, 확보 전에 해당 앱을 실행하면 `.bak` 이 남아 있던 상태를 다시 볼 수 없습니다. 확보 순서는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

쓸 때마다 새 파일을 만들어 맵 전체를 쓰기 때문에, 앱이 지운 키는 새 파일에 들어 있지 않습니다. 옛 파일의 내용이 저장 공간에 남는지는 파일 시스템과 암호화 방식에 달려 있고, [파일 시스템](../storage/filesystems/index.md) 과 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다. 같은 이유로 파일의 수정 시각은 어느 키든 마지막으로 파일을 새로 쓴 때를 가리킬 뿐이고(값이 바뀌지 않으면 다시 쓰지 않습니다), 특정 키가 언제 바뀌었는지는 알려 주지 않습니다.

## 함정

확장자가 `.xml` 이라고 해서 텍스트라고 단정하면 시스템 파일에서 틀리기 쉽고, 편집기에서 깨져 보이는 파일을 손상된 파일로 오해하는 일이 생깁니다. 앞 4바이트를 먼저 보면 피할 수 있습니다.

설정 파일이 비어 있거나 기대한 키가 없다고 해서 앱이 그 값을 저장하지 않았다고 결론 내리면 안 됩니다. 앱이 DataStore 로 옮겨 갔다면 값은 `files/datastore/` 쪽에 있을 수 있습니다.

`settings` 명령 출력은 실행 중인 기기의 현재 값을 보여 주고, 디스크 이미지의 파일과 같은 내용인지는 따로 확인해야 합니다. 명령 출력과 이미지를 함께 쓸 때는 어느 쪽에서 나온 값인지 보고서에 나눠 적습니다.

## 도구

헥스 편집기, 텍스트 편집기, 일반 XML 파서만으로 읽을 수 있습니다. 여러 앱의 설정 파일을 한꺼번에 표로 바꾸는 도구를 쓸 때는 그 도구가 `.bak` 파일까지 읽는지, ABX 파일을 알아보는지 알려진 파일로 먼저 확인하고, 확인 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 참고 문헌

1. SharedPreferencesImpl.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/SharedPreferencesImpl.java
2. DataStore — Android Developers, https://developer.android.com/topic/libraries/architecture/datastore
