---
title: "Windows 메일 앱"
parent: "아티팩트 · 메일"
nav_order: 1970
---

# Windows 메일 앱 (HxStore)

Windows 메일 앱은 Windows 8 부터 11 까지 쓰던 메일 앱으로, 일정·사람 앱과 묶여 나왔습니다. Microsoft 는 2024년 12월 31일에 지원을 끝냈고, 그 뒤로는 이 앱으로 메일을 주고받을 수 없습니다. PC 에 저장된 메일·일정·연락처는 지원 종료 뒤에도 내보낼 수 있습니다. 앱은 메일을 `HxStore.hxd` 파일에 둔다고 흔히 알려져 있지만, 형식이 공개되지 않아 실제 데이터로 확인해야 합니다.

## 내용별 근거

| 내용 | 근거·확인 방법 |
|---|---|
| 앱의 성격, 지원 프로토콜, 지원 종료, 내보내기 | Microsoft 지원 문서[1], 위키백과[2] |
| 패키지 이름, 저장 위치, `HxStore.hxd` 형식 | 흔히 알려진 내용. 형식은 공개되지 않음 |
| 본문·첨부를 개별 파일로 따로 둔다는 점 | 흔히 알려진 내용. 실제 데이터로 확인 |
| 지원 종료 뒤 앱을 지우면 저장 파일도 지워지는지 | 시험 기기에서 앱을 지운 뒤 저장 폴더가 남는지 확인 |
| Windows 10 과 11 에서 위치가 같은지 | 실제 데이터로 확인 |
| 최신 Windows 11 PC 의 상태 | Windows 11 25H2(빌드 26200)에는 패키지 폴더가 없을 수 있음 |

`HxStore.hxd` 는 형식이 공개되지 않았으므로, 아래는 형식을 모르는 파일에서 메일 흔적을 찾는 방법을 중심으로 다룹니다.

## 무엇을 기록하나 · 왜 생기나

Windows 8·8.1·10·11 의 메일 앱은 Windows Runtime 기반의 UWP 앱이고, 일정 (Calendar)·사람 (People) 앱과 묶여 나왔습니다[2]. Exchange·IMAP·POP3 계정을 지원하는데, POP3 은 Windows 10 에서 다시 들어왔고 뉴스그룹은 지원하지 않습니다[2]. PC 에 저장된 메일·일정·연락처는 지원 종료 뒤에도 내보낼 수 있으므로[1], 앱이 메일을 PC 안에 저장한다는 뜻입니다.

### 지원 종료

Windows 메일·일정·사람 앱의 지원은 2024년 12월 31일에 끝났고[1][2], 그 뒤로는 메일·일정 앱으로 메일과 일정을 주고받을 수 없습니다[1]. 저장된 자료를 내보내는 방법은 Microsoft 의 "Export emails and contacts from Windows Mail or People and import to new Outlook" 문서에 있습니다[1]. 분석 대상 PC 에 앱이 남아 있는지는 패키지 폴더가 있는지로 확인합니다. 대체 앱은 새 Outlook 이며[1][2], 사용자가 새 Outlook 으로 옮겨 가는 길은 [새 Outlook](new-outlook.md) 에서 다룹니다.

지원 종료 뒤의 PC 에서도 이 앱의 저장 파일을 만날 수 있습니다. 지원 종료 전에 받은 메일이 PC 에 남아 있을 수 있기 때문입니다.

## 위치와 버전별 차이

### 흔히 알려진 위치

| 무엇 | 흔히 알려진 위치 |
|---|---|
| 앱 패키지 데이터 폴더 | `%LOCALAPPDATA%\Packages\microsoft.windowscommunicationsapps_8wekyb3d8bbwe` |
| 주 저장 파일 | 위 폴더 아래 `LocalState\HxStore.hxd` |
| 본문·첨부 | 위 폴더 아래 `LocalState\Files\S0\<번호>\` 의 개별 파일 |

- Windows 10 과 11 에서 위치가 같은지는 실제 데이터로 확인합니다.
- Windows 11 25H2(빌드 26200)에는 `windowscommunicationsapps` 패키지 폴더가 없을 수 있습니다. 폴더가 없을 때 앱이 처음부터 없었는지, 지워졌는지는 폴더만으로 알 수 없습니다.
- 패키지 데이터 폴더 전체의 구성은 [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) 에서 다룹니다.

## 구조

`HxStore.hxd` 는 형식이 공개되지 않아, 구조를 풀기보다 문자열 찾기(카빙, carving) 위주로 봅니다. 본문과 첨부는 `LocalState\Files\S0\<번호>\` 아래 개별 파일로 따로 저장된다고 알려져 있습니다. 그렇다면 첨부는 파일 단위로 꺼내 해시를 구할 수 있습니다. 형식을 모르는 파일에서 글자를 찾을 때는 인코딩 두 가지 이상으로 찾습니다. 인코딩은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 패키지 데이터 폴더가 있으면 이 사용자 프로필에 메일 앱 패키지가 있었습니다 | 사용자가 메일 앱으로 메일을 주고받았다는 것 |
| 저장 파일 안에서 찾은 메일 주소·제목 조각은 그 글자가 파일에 적혀 있었다는 근거입니다 | 그 조각이 받은 메일인지 보낸 메일인지, 어느 폴더에 있었는지, 지운 메일인지. 형식을 모르면 문맥을 확정하지 못합니다 |
| 개별 파일로 꺼낸 첨부의 해시가 다른 곳의 파일과 같으면 내용이 같습니다 | 그 첨부가 어느 메시지에 붙어 있었는지 |
| 저장 파일의 NTFS 시각은 파일이 생기고 바뀐 때를 알려 줍니다 | 메시지 한 통을 받은 때 |

### 보고서 문장

아래 주소는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`HxStore.hxd` 안에 `partner@example.com` 이 UTF-16LE 로 적혀 있습니다. 찾은 자리의 파일 오프셋은 붙임 표에 적었습니다."
- 쓰면 안 되는 문장: "사용자는 메일 앱으로 partner@example.com 과 메일을 주고받았습니다."

앞 문장은 파일 안에 그 글자가 있다는 사실까지만 말합니다. 주고받은 메일로 쓰려면 헤더 조각이나 다른 흔적으로 문맥을 확인합니다.

## 시각 해석

- 구조를 모르는 파일에서 찾은 숫자를 시각으로 읽지 않습니다. 다른 근거와 맞을 때만 씁니다([시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)).
- 파일 안에 메일 헤더 조각이 있으면 그 시각은 메일 쪽 값입니다. 읽는 법은 [메일 헤더 분석](../../03-techniques/analysis/email-header-analysis.md) 에서 다룹니다.
- 저장 파일과 `Files` 아래 파일의 NTFS 시각은 [마스터 파일 테이블](../filesystem/mft.md) 에서 읽습니다.
- 2024년 12월 31일 뒤로는 이 앱으로 메일을 주고받을 수 없습니다[1]. 저장 파일의 수정 시각이 그 뒤라도 새 메일을 받았다고 바로 읽지 않습니다. 앱을 열거나 자료를 내보내기만 해도 파일이 바뀌었을 수 있습니다.

## 함정과 한계

1. **패키지 폴더가 없으니 앱을 쓰지 않았다고 봅니다.** 앱을 지우면 `LocalState` 도 함께 지워질 수 있습니다. [스토어 앱 설치 목록](../system-account/appx-staterepository.md) 에서 패키지가 있었는지 봅니다. [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 과 [USN 변경 저널](../filesystem/usnjrnl.md) 에서 예전 모습을 찾습니다.
2. **글자 찾기 결과를 메일 목록으로 씁니다.** 형식을 모르는 파일에서 찾은 조각은 받은 메일인지, 보낸 메일인지, 지운 메일인지 알 수 없습니다. 조각은 "파일 안에 이 글자가 있다" 로만 적습니다.
3. **인코딩 하나로만 찾습니다.** 같은 글자도 UTF-8 과 UTF-16LE 의 바이트가 다릅니다. 두 가지로 다 찾습니다. 파일 일부가 압축돼 있다면 글자 찾기로는 보이지 않습니다.
4. **지원 종료 날짜를 앱을 그만 쓴 날로 봅니다.** 사용자가 그 전에 새 Outlook 으로 옮겨 갔을 수 있습니다. 새 Outlook 로그의 시작 시각과 맞춰 봅니다([새 Outlook](new-outlook.md)).
5. **내보낸 메일을 놓칩니다.** 저장된 메일은 새 Outlook 으로 내보낼 수 있습니다[1]. 내보낸 결과가 다른 곳에 있는지 봅니다.
6. **Windows 11 에서 알려진 경로를 Windows 10 기기에 그대로 씁니다.** 두 판의 위치가 다를 수 있으므로 디스크 전체에서 `HxStore` 이름으로 찾습니다.
7. **형식을 푼다는 도구의 결과를 그대로 씁니다.** 형식이 공개되지 않은 파일입니다. 도구 결과를 글자 찾기 결과와 맞춰 봅니다([도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)).

## 직접 분석해 보기

### 원시 바이트로 한 번

형식을 모르므로, 사건에서 이미 아는 글자를 바이트로 바꿔 찾습니다. 아래 바이트는 글자를 인코딩 규칙으로 계산한 값입니다. 특정 기기에서 뽑은 값이 아닙니다.

| 찾을 글자 | UTF-8 | UTF-16LE |
|---|---|---|
| `example.com` | `65 78 61 6D 70 6C 65 2E 63 6F 6D` | `65 00 78 00 61 00 6D 00 70 00 6C 00 65 00 2E 00 63 00 6F 00 6D 00` |
| `견적` | `EA B2 AC EC A0 81` | `AC AC 01 C8` |

1. 저장 파일과 `LocalState` 폴더 전체의 사본을 뜹니다.
2. 사건에서 아는 메일 주소·이름·제목 낱말을 고릅니다.
3. 글자마다 UTF-8 과 UTF-16LE 바이트를 구해 둘 다 찾습니다.
4. 찾은 자리의 앞뒤 바이트를 봅니다. 주소 옆에 다른 주소나 제목이 붙어 있으면 한 메시지의 조각일 수 있습니다. 확정하지 않고 오프셋과 함께 적습니다.
5. `Files` 폴더 아래에 개별 파일이 있다면 파일마다 해시를 구하고 첫 바이트로 파일 종류를 구분합니다.

### 공개 도구로 한 번

- 문자열 추출 도구로 `HxStore.hxd` 의 글자를 인코딩별로 뽑습니다. 결과에서 `@` 가 든 줄을 거르면 주소 후보가 나옵니다.
- 파일 내용 검색 도구로 `LocalState` 폴더 전체를 낱말로 찾습니다([파일 내용 검색](../../03-techniques/analysis/content-search/index.md)).
- `Files` 아래 개별 파일의 해시를 다른 폴더의 파일과 맞춥니다([해시셋 대조와 유사 해시](../../03-techniques/analysis/hash-set-fuzzy-hash.md)).

> 그림 자리: 패키지 데이터 폴더 → `LocalState` → `HxStore.hxd` 와 `Files\S0\<번호>\` 의 관계(흔한 설명 기준), 그리고 아는 글자를 UTF-8·UTF-16LE 바이트로 바꿔 찾는 흐름

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [새 Outlook](new-outlook.md) | 사용자가 새 Outlook 으로 옮겨 갔는지, 그 시각 |
| [스토어 앱 설치 목록](../system-account/appx-staterepository.md) | 메일 앱 패키지가 있었는지, 지워졌는지 |
| [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) | 패키지 데이터 폴더의 `settings.dat` 와 폴더 구성 |
| [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 앱을 지우기 전의 `LocalState` |
| [마스터 파일 테이블](../filesystem/mft.md) · [USN 변경 저널](../filesystem/usnjrnl.md) | 저장 파일과 `Files` 아래 파일이 생기고 지워진 때 |
| [윈도 알림 기록](../execution/wpndatabase-db.md) | 새 메일 알림이 남았는지 |
| [파일 내용 검색](../../03-techniques/analysis/content-search/index.md) | 형식을 모르는 파일에서 글자 찾기 |

메일로 누구와 연락했는지 정리하는 순서는 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 에서 다룹니다.

## 실습

**공개 시험 데이터(NIST CFReDS 등)** 가운데 Windows 10 이미지로 해 봅니다.

1. `microsoft.windowscommunicationsapps` 패키지 폴더가 있습니까? `LocalState` 아래에는 무엇이 있습니까?
2. `HxStore.hxd` 가 있다면 크기와 NTFS 시각은 무엇입니까?
3. 이미지 설명에 나오는 메일 주소를 UTF-8 과 UTF-16LE 로 찾아보십시오. 어느 인코딩에서 나옵니까?
4. `Files` 폴더 아래 파일의 해시를 구해, 사용자 폴더의 다른 파일과 같은 것이 있는지 보십시오.
5. 스토어 앱 설치 목록에는 이 패키지가 언제 깔렸다고 적혀 있습니까?

**직접 만든 가상 머신** 가운데 메일 앱이 남아 있는 옛 Windows 10 스냅숏이 있다면, 앱을 지우기 전과 뒤의 `LocalState` 를 비교해 보십시오. 저장 파일이 함께 지워집니까?

## 참고 문헌

1. Microsoft 지원, "Outlook for Windows: The Future of Mail, Calendar and People on Windows 11" — https://support.microsoft.com/en-us/office/outlook-for-windows-the-future-of-mail-calendar-and-people-on-windows-11-715fc27c-e0f4-4652-9174-47faa751b199
2. Wikipedia, "Mail (Windows)" — https://en.wikipedia.org/wiki/Windows_Mail
