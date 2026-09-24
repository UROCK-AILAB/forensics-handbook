# 공급자와 메시지 파일 (Provider·Message Table)

## 한 줄 요약

이벤트 뷰어에 보이는 설명 문장은 로그 파일 안에 없습니다. 레코드에는 문장의 빈자리(`%1`, `%2` …)에 들어갈 값만 있습니다. 문장 틀은 이벤트를 낸 공급자 (Provider) 의 메시지 파일 (Message File) 에 있습니다. 레지스트리로 메시지 파일을 찾고, 이벤트 식별자로 문장을 고르고, 레코드 값을 채워야 설명 문장이 됩니다.

이 페이지는 [이벤트 로그 형식 (EVTX·EVT·ETL)](/01-foundations/database-log-formats/evtx-evt-etl/index.md) 의 하위 주제입니다. 레코드 안의 값을 꺼내는 법은 [이진 XML 해석 (Binary XML·Template)](/01-foundations/database-log-formats/evtx-evt-etl/binary-xml-template.md) 에 있습니다.

## 이 내용이 쓰이는 때

- 압수 이미지의 EVTX·EVT 에서 이벤트 뷰어와 같은 설명 문장을 다시 만들 때 씁니다.
- 도구마다 설명 문장이 다를 때 원인을 찾는 데 씁니다. 메시지를 보여 주는 프로그램은 레지스트리 읽기, 환경 변수 풀기, 파일 읽기를 저마다 따로 합니다. 그래서 프로그램마다 이벤트 뷰어와 다른 문장이 나올 수 있습니다.

## 구조

> 그림 자리: 레코드의 Provider Guid → Publishers 키 → 메시지 파일(.exe·.dll·.mui) → 메시지 식별자로 고른 문장 → %1·%2 에 레코드 값을 채운 결과로 이어지는 흐름

### 파일 밖에 있는 것

- 이벤트 뷰어가 보여 주는 내용 가운데 일부는 로그 파일 밖에 있습니다.
- 설명 문장은 메시지 파일에 있습니다. 레코드에는 `%1`·`%2` 자리에 들어갈 문자열만 있습니다.
- Vista 부터는 WEVT_TEMPLATE 리소스도 파일 밖에 있습니다. 이 리소스로 메시지 식별자, 채널·키워드·수준·opcode·task 이름의 문자열 식별자, UserData 의 해석을 찾습니다.

### 레지스트리에서 메시지 파일 찾기

키는 두 가지입니다.

**원본 키** — `HKLM\System\CurrentControlSet\Services\EventLog\<로그 종류>\<원본 이름>`

- XP 이하에서 쓰던 방식입니다.
- 로그 종류는 XML 의 `Channel` 요소에서 얻습니다.
- 원본 (Source) 이름은 XML `Provider` 요소의 `EventSourceName` 속성입니다. 이 속성이 없으면 `Name` 속성을 씁니다.
- 원본 이름은 대소문자를 가리지 않습니다.

| 값 | 뜻 |
|---|---|
| EventMessageFile | 메시지 파일. 여러 파일을 세미콜론(`;`)으로 나눠 적을 수 있습니다 |
| CategoryMessageFile | 분류 문장이 든 파일 |
| ParameterMessageFile | 매개변수 문장이 든 파일 |
| CategoryCount | 분류 개수 |
| ProviderGuid | Vista 부터 있습니다. XML `Provider` 요소의 `Guid` 와 같습니다 |

**공급자 키** — `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WINEVT\Publishers\{GUID}`

| 값 | 뜻 |
|---|---|
| MessageFileName | 메시지 파일 |
| ResourceFileName | WEVT_TEMPLATE 리소스가 든 파일 |
| ParameterFileName | 매개변수 문장이 든 파일 |

찾는 순서는 다음과 같습니다.

1. XML `Provider` 요소의 `Guid` 로 공급자 키를 찾아 MessageFileName 을 씁니다.
2. 공급자 키가 없으면 원본 키의 EventMessageFile 을 씁니다. Vista 부터는 원본 키에 EventMessageFile 이 늘 있지는 않습니다.

확인 PC 의 예입니다(확인 범위: Windows 11 25H2 PC 한 대).

- 원본 키 `EventLog\System\Service Control Manager` 에는 ProviderGuid `{555908d1-a6d7-4695-8e1e-26931d2012f4}` 와 EventMessageFile `%SystemRoot%\system32\services.exe` 가 있었습니다.
- 같은 GUID 의 Publishers 키는 기본값이 "Service Control Manager" 였습니다.
- 그 키의 ResourceFileName 과 MessageFileName 은 `%SystemRoot%\system32\services.exe` 였습니다.
- 그 키의 ParameterFileName 은 `%SystemRoot%\system32\kernel32.dll` 이었습니다.
- 그 키 아래에 하위 키 ChannelReferences 가 있었습니다.

살아 있는 시스템에서는 `wevtutil gp <공급자 이름>` 으로 공급자 정보를 봅니다. 수집 절차는 [라이브 응답](/03-techniques/process-acquisition/live-response/index.md) 을 봅니다.

### 경로 풀기

- `%SystemRoot%` 는 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion` 의 SystemRoot 값으로 풉니다.
- `%WinDir%` 는 `HKLM\System\CurrentControlSet\Control\Session Manager\Environment` 의 windir 값으로 풉니다.

| SystemRoot 값 예 | Windows |
|---|---|
| `C:\WINDOWS` | XP 이후 |
| `C:\WINNT` | NT 3.1·4.0·2000 |
| `C:\WINNT35` | NT 3.5x |
| `C:\WTSRV` | NT 4.0 터미널 서버 |

압수 이미지를 분석할 때는 분석 PC 의 환경 변수를 쓰지 않습니다. 이미지 안 SOFTWARE·SYSTEM 하이브의 값으로 경로를 풀고, 파일도 이미지 안에서 찾습니다. 오프라인 하이브를 읽는 법은 [레지스트리 하이브 구조](/01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.

### 메시지 파일의 종류

- 메시지 파일은 `.rsrc` 섹션이 있는 PE/COFF 실행 파일입니다. 확장자는 `.exe`·`.dll`·`.dll.mui`·`.sys` 등입니다. PE 구조는 [실행 파일 메타데이터](/02-artifacts/embedded-metadata/pe-header-version-info-digital-signature.md) 를 봅니다.
- 종류는 두 가지입니다. 메시지 테이블 (Message Table) 리소스가 든 파일과 MUI 리소스 파일입니다.
- 둘 다 있으면 메시지 테이블을 먼저 쓰는 것으로 보입니다.
- 언어 중립 MUI 파일에는 메시지 테이블이 없습니다. 문장은 언어별 파일에 있습니다. 예: `C:\Windows\System32\services.exe` → `C:\Windows\System32\en-US\services.exe.mui`.
- 언어별 파일이 같은 폴더에 있을 수도 있습니다(`C:\Windows\System32\services.exe.mui`).
- 문장은 언어마다 다릅니다. 한 파일에 여러 언어가 들어 있을 수도 있습니다.
- ResourceFileName 의 파일에는 WEVT_TEMPLATE 리소스가 있어야 합니다. 최근 Windows 10 에서는 이 리소스가 `C:\Windows\SystemResources\<파일>.mun` 에 있을 수도 있습니다(예: `tquery.dll.mun`).

확인 PC 에서 본 모습입니다(확인 범위: Windows 11 25H2 PC 한 대).

- `System32\en-US\services.exe.mui` 와 `System32\ko-KR\services.exe.mui` 가 둘 다 있었습니다.
- `C:\Windows\SystemResources` 에는 항목이 172개 있었습니다.
- `tquery.dll.mun` 안에서 "CRIM" 서명이 보였습니다.

### 이벤트 식별자에서 메시지 식별자로

| 방식 | 쓰는 때 | 방법 | 예 |
|---|---|---|---|
| 그대로 | XP 이하 | 이벤트 식별자가 곧 메시지 식별자입니다 | EVT 의 이벤트 3260(0x00000cbc) → "This computer has been successfully joined to %1 '%2'." |
| Qualifiers | Vista 이후 | Qualifiers 값을 16비트 왼쪽으로 밀고 EventID 와 합칩니다 | 아래 계산 |
| WEVT_TEMPLATE | Vista 이후 | Provider Guid 로 WEVT_TEMPLATE 의 공급자를 찾고, 같은 ID 의 이벤트 정의에서 메시지 식별자를 읽습니다 | Microsoft-Windows-UAC 이벤트 1 → 0xb9000001 |

Qualifiers 계산의 예는 다음과 같습니다. 0x40001b7c 의 문장은 "The %1 service entered the %2 state." 입니다.

```
<EventID Qualifiers="16384">7036</EventID>
16384 = 0x4000, 7036 = 0x1b7c
(0x4000 << 16) | 0x1b7c = 0x40001b7c
```

- 메시지 식별자의 위 2비트는 severity 입니다. 0x40001b7c 는 `01`(정보), 0xc0001b7a 는 `11`(오류) 입니다. 비트 구조는 [EVTX 파일 구조](/01-foundations/database-log-formats/evtx-evt-etl/file-header-chunk-record.md) 의 "이벤트 식별자와 수준" 에 있습니다.

확인 PC 의 services.exe WEVT_TEMPLATE 에서 공급자 {555908d1-…} 의 정의를 읽었습니다(확인 범위: Windows 11 25H2 PC 한 대). 이 공급자의 이벤트 정의는 43개였고, 그 가운데 넷은 아래와 같습니다.

| 이벤트 ID | 메시지 식별자 |
|---|---|
| 7034 | 0xc0001b7a |
| 7036 | 0x40001b7c |
| 7040 | 0x40001b80 |
| 7045 | 0x40001b85 |

- 7036 의 값은 위 Qualifiers 계산 결과와 같습니다.
- 이 정의들의 키워드는 0x0080000000000000 이었습니다. libevtx 명세는 이 비트를 "Classic"(win:EventlogClassic) 으로 적습니다.
- 7045 이벤트를 조사에 쓰는 법은 [서비스 설치](/02-artifacts/event-logs/7045-4697.md) 에 있습니다.

### 자리 표시자

- `%1`, `%2` … 는 이벤트의 첫째, 둘째 … 문자열로 바꿉니다.
- `%0` 은 줄바꿈 없이 문장을 끝내라는 뜻입니다. FormatMessage 는 그 뒤를 무시합니다.
- 문장의 자리 표시자가 이벤트 문자열보다 많으면, 채우지 못한 자리는 `%#` 그대로 보이는 것 같습니다.
- 값이 `%%5` 처럼 적혀 있으면 매개변수 파일의 5번 메시지로 바꿉니다. 이를 매개변수 확장이라고 합니다.
  - 예: SCM 이벤트 7006 의 `%%5` → MsObjs.dll 의 5번 "Access is denied."
  - 한 값에 `%%2080 %%2082 %%2084` 처럼 여러 개가 들어갈 수 있습니다(Security-Auditing 4720). 이 이벤트는 [계정 생성·변경](/02-artifacts/event-logs/account-management-events.md) 에서 다룹니다.
  - EVT 예: SCM 0xc0001b58 의 `%%1053` → kernel32.dll 의 1053번 "The service did not respond to the start or control request in a timely fashion."
- 매개변수 파일은 공급자 키의 ParameterFileName 을 먼저 보고, 없으면 원본 키의 ParameterMessageFile 을 봅니다.
- 매개변수 파일이 정해져 있지 않으면, Windows 10 의 이벤트 뷰어는 메시지 파일을 먼저 보고 다음에 MsObjs.dll·kernel32.dll 같은 기본 파일을 보는 것 같습니다.
- 분류 (Category) 는 주로 보안 로그에서 씁니다. CategoryMessageFile 의 메시지 번호가 분류 번호와 같습니다. 분류 문장에는 자리 표시자가 없어야 합니다.

### WEVT_TEMPLATE 리소스 (CRIM)

- Vista 부터 PE 파일의 `WEVT_TEMPLATE` 리소스에 이벤트 매니페스트 (Event Manifest) 가 이진으로 들어갈 수 있습니다.
- 서명 CRIM 은 "Compiled resource instrumentation manifest" 에서 왔거나, Longhorn 시절 이벤트 로그 서비스의 코드명 Crimson 에서 왔다고 libfwevt 명세는 짐작합니다.

**머리**

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 서명 `CRIM` |
| 4 | 4 | 크기 |
| 8 | 2 | 주 버전 (명세 값 3) |
| 10 | 2 | 부 버전 (명세 값 1) |
| 12 | 4 | 공급자 수 |
| 16 | 20 × 공급자 수 | 공급자 설명자. GUID 16바이트와 데이터 오프셋 4바이트 |

- 공급자 데이터는 `WEVT` 서명, 크기, 메시지 테이블 식별자(없으면 0xffffffff), 요소 설명자 수 순서로 시작합니다.

| 요소 서명 | 뜻 |
|---|---|
| CHAN | 채널 |
| EVNT | 이벤트 |
| KEYW | 키워드 |
| LEVL | 수준 |
| MAPS | 값 맵 |
| OPCO | opcode |
| TASK | task |
| TTBL | 템플릿 표 |
| PRVA | 알 수 없음 |

**이벤트 정의 (48바이트)**

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 2 | 이벤트 ID. customer·severity 비트를 뺀 값입니다 |
| 2 | 1 | 버전 |
| 3 | 1 | 채널 |
| 4 | 1 | 수준 |
| 5 | 1 | opcode |
| 6 | 2 | task |
| 8 | 8 | 키워드 |
| 16 | 4 | 메시지 식별자 |
| 20 | 4 | 템플릿 정의 오프셋 |
| 24 | 4 | opcode 정의 오프셋 |
| 28 | 4 | 수준 정의 오프셋 |
| 32 | 4 | task 정의 오프셋 |
| 36 ~ 47 | 12 | 알 수 없음 |

- 템플릿 정의는 `TEMP` 서명으로 시작합니다. 크기, 항목 설명자 수, 항목 이름 수, 항목 오프셋, 알 수 없는 값, GUID 16바이트, 이진 XML 조각, 항목 설명자, 항목 이름이 이어집니다.
- 알 수 없는 값은 EventData 면 1, UserData 면 2 로 보입니다.
- 이 이진 XML 은 EVTX 의 것과 조금 다릅니다. [이진 XML 해석](/01-foundations/database-log-formats/evtx-evt-etl/binary-xml-template.md) 의 "함정" 을 봅니다.
- 이 템플릿 GUID 가 EVTX 레코드 안의 템플릿 GUID 와 같은 값인지는 이 위키가 참고한 자료로 확인하지 못했습니다.

확인 PC 에서 본 모습입니다(확인 범위: Windows 11 25H2 PC 한 대).

- services.exe·wevtapi.dll·tquery.dll.mun 의 CRIM 버전은 5.1 이었습니다. 명세의 3.1 과 다릅니다.
- services.exe 의 CRIM 은 크기가 24,532바이트였고, 공급자가 3개였습니다. 그 가운데 하나가 {555908d1-…}(Service Control Manager) 였습니다.
- 세 공급자 모두 CHAN·TTBL·PRVA·OPCO·LEVL·TASK·KEYW·EVNT 요소 8개가 있었습니다.

## 읽는 법

1. 레코드 XML 에서 `Provider` 의 `Name`·`Guid`·`EventSourceName`, `EventID` 와 `Qualifiers`, `Channel`, 이벤트 데이터 값을 읽습니다.
2. 이미지의 SOFTWARE 하이브에서 공급자 키를 찾아 MessageFileName·ParameterFileName 을 읽습니다. 공급자 키가 없으면 SYSTEM 하이브의 원본 키를 봅니다.
3. 경로의 `%SystemRoot%` 를 이미지 SOFTWARE 하이브의 SystemRoot 값으로 풉니다.
4. 이미지에서 메시지 파일을 꺼냅니다. 메시지 테이블이 없으면 언어별 `.mui` 파일을 찾습니다.
5. 메시지 식별자를 구합니다. Qualifiers 가 있으면 계산합니다. 없으면 WEVT_TEMPLATE 의 이벤트 정의에서 읽습니다.
6. 메시지 테이블에서 문장 틀을 꺼내 `%1`·`%2` 를 채웁니다. `%%n` 은 매개변수 파일에서 찾아 바꿉니다.
7. 만든 문장과 레코드의 원래 값을 함께 기록합니다.

### 헥스로 한 번 따라가기

아래는 명세의 이벤트 정의 배치에 확인 PC 에서 읽은 값(7036 → 0x40001b7c, 키워드 0x0080000000000000)을 넣어 만든 예시입니다. 실제 파일에서 떠낸 바이트가 아닙니다. `??` 는 이 설명에 쓰지 않는 바이트입니다. 오프셋은 이벤트 정의 시작 기준입니다.

```
오프셋    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  7C 1B ?? ?? ?? ?? ?? ??  00 00 00 00 00 00 80 00
00000010  7C 1B 00 40 ?? ?? ?? ??  ?? ?? ?? ?? ?? ?? ?? ??
00000020  ?? ?? ?? ?? ?? ?? ?? ??  ?? ?? ?? ?? ?? ?? ?? ??
```

- 0x00 `7C 1B` 는 이벤트 ID 0x1b7c(7036) 입니다.
- 0x02 ~ 0x07 은 버전·채널·수준·opcode·task 입니다.
- 0x08 의 8바이트는 키워드 0x0080000000000000 입니다. 리틀 엔디언이라 `80` 이 7번째 바이트에 옵니다.
- 0x10 `7C 1B 00 40` 은 메시지 식별자 0x40001b7c 입니다.
- 0x14 ~ 0x23 은 템플릿·opcode·수준·task 정의 오프셋입니다.
- 0x24 ~ 0x2F 는 알 수 없는 값입니다.

메시지 파일(services.exe 또는 그 언어별 `.mui`)에서 0x40001b7c 의 문장 "The %1 service entered the %2 state." 를 꺼냅니다. `%1` 과 `%2` 에 레코드의 첫째·둘째 값을 넣으면 설명 문장이 됩니다.

## 포렌식에서 중요한 점

- 설명 문장은 해석 결과이고, 기록은 레코드의 값입니다. 보고서에는 문장과 함께 원래 값을 적습니다.
- 메시지 파일이 이미지에 없으면 문장을 만들 수 없습니다. 그래도 레코드의 값은 남아 있으므로 값 목록을 그대로 보고합니다.
- 분석 PC 의 레지스트리와 파일로 풀면 다른 버전이나 다른 언어의 문장이 나올 수 있습니다. 이미지 안의 것으로 풉니다.
- 같은 메시지 식별자라도 어느 언어별 파일을 읽었는지에 따라 문장의 언어가 다릅니다.
- 도구마다 문장이 다르면 어느 파일과 어느 레지스트리 값을 읽었는지부터 비교합니다. [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md) 을 봅니다.

## 함정

- EventID 만으로 메시지를 찾으면 못 찾을 수 있습니다. Qualifiers 가 붙은 이벤트는 Qualifiers 를 합친 값(예: 0x40001b7c)이 메시지 식별자입니다.
- EventMessageFile 에 파일이 여러 개 적혀 있을 수 있습니다. 세미콜론으로 나눠 모두 봅니다.
- 원본 이름은 대소문자를 가리지 않습니다. 대소문자만 다른 이름을 다른 원본으로 보지 않습니다.
- `%%n` 을 풀지 않으면 문장에 숫자만 남습니다.
- 문장에 `%#` 이 그대로 보이면 이벤트 문자열이 모자란 것일 수 있습니다.
- CRIM 버전이 명세 값(3.1)과 달라도 버리지 않습니다. 확인 PC 에서는 5.1 이었습니다.
- WEVT_TEMPLATE 은 원래 DLL 이 아니라 `SystemResources` 의 `.mun` 파일에 있을 수 있습니다.

## 도구

- wevtutil: 살아 있는 시스템에서 `wevtutil gp <공급자 이름>` 으로 공급자 정보를 봅니다.
- libevtx·libfwevt: 형식 명세를 공개했습니다. libfwevt 명세는 WEVT_TEMPLATE 구조를 다룹니다.
- 이벤트 뷰어: 살아 있는 시스템에서 만든 문장을 비교 기준으로 삼을 때 씁니다.

## 참고 문헌

1. Joachim Metz, "Windows XML Event Log (EVTX) format", libyal/libevtx (문서 버전 0.0.27, 2026-07) — https://raw.githubusercontent.com/libyal/libevtx/main/documentation/Windows%20XML%20Event%20Log%20(EVTX).asciidoc
2. Joachim Metz, "Windows Event Viewer Log (EVT) format", libyal/libevt (문서 버전 0.0.16) — https://raw.githubusercontent.com/libyal/libevt/main/documentation/Windows%20Event%20Log%20(EVT)%20format.asciidoc
3. Joachim Metz, "Windows Event manifest binary format", libyal/libfwevt (문서 버전 0.0.9, 2024-01) — https://raw.githubusercontent.com/libyal/libfwevt/main/documentation/Windows%20Event%20manifest%20binary%20format.asciidoc
