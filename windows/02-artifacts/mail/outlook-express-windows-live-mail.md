---
title: "옛 윈도 메일 프로그램"
parent: "아티팩트 · 메일"
nav_order: 1960
---

# 옛 윈도 메일 프로그램 (Outlook Express·Windows Live Mail)

> 위치: 아티팩트 사전 > 메일

## 한 줄 요약

이 페이지는 옛 메일 프로그램 세 가지를 다룹니다. Outlook Express 는 Windows 98 부터 XP 까지 함께 나왔고, 5.0 판부터 메일 폴더마다 `.dbx` 파일을 하나씩 썼습니다. Vista 의 Windows Mail 은 메시지를 `.eml` 파일로 하나씩 두고 ESE 데이터베이스로 항목을 관리했습니다. Windows Live Mail 도 `.eml` 파일과 ESE 데이터베이스 `Mail.MSMessageStore` 를 썼습니다. 마지막 판인 2012 판의 지원은 2017년 1월 10일에 끝났습니다.

## 이 페이지 내용의 확인 상태

| 내용 | 상태 |
|---|---|
| 판과 함께 나온 Windows, 날짜, 저장 형식, 프로토콜 | 위키백과 문서로 확인했습니다 |
| 파일·폴더 위치 | 흔한 설명. 확인하지 못했습니다 |
| 레지스트리 위치 | 흔한 설명. 확인하지 못해 적지 않습니다 |
| `.dbx` 의 시그니처·헤더 오프셋·내부 구조 | 공개 명세로 확인하지 못해 적지 않습니다 |
| ESE 데이터베이스를 다룰 때의 주의 | 다른 ESE 파일에서 관찰한 내용입니다. `MSMessageStore` 는 직접 보지 않았습니다 |

위키백과는 2차 자료입니다. 판과 날짜를 보고서에 쓰기 전에 검체 안 프로그램 파일의 판 정보로 한 번 더 맞춥니다([실행 파일 메타데이터](../embedded-metadata/pe-header-version-info-digital-signature.md)).

## 무엇을 기록하나 · 왜 생기나

세 프로그램은 모두 메일을 PC 안의 파일로 둡니다[1][2][3]. 요즘 PC 에서는 드물고, 옛 PC 의 이미지, 새 PC 로 옮겨 온 옛 사용자 폴더, 백업 매체에서 만날 수 있습니다. 프로그램과 판에 따라 저장 형식이 다르므로 판을 먼저 정해야 어떤 파일을 찾을지 정할 수 있습니다.

## 위치와 버전별 차이

### Outlook Express

| 판 | 함께 나온 Windows | 저장 형식 |
|---|---|---|
| 4.0 | Windows 98 (1998년 6월), Internet Explorer 4 | `.mbx` 파일[1] |
| 5.0 | Windows 98 SE (1999년 6월), Internet Explorer 5 | `.dbx` 파일, 메일 폴더마다 하나[1] |
| 5.01 | Windows 2000 (2000년 2월) | `.dbx`[1] |
| 5.5 | Windows Me (2000년 6월) | `.dbx`[1] |
| 6.0 | Windows XP (2001년 10월), Internet Explorer 6 | `.dbx`[1] |

Windows Vista 에서 Outlook Express 는 Windows Mail 로 바뀌었습니다[1]. 참고한 문서에는 Outlook Express 의 지원 종료 날짜가 없습니다[1].

### Windows Mail (Vista)

Windows Mail 은 Windows Vista 에 들어 있었고[3], Windows 7 에서는 빠졌습니다[3]. Windows 7 에서는 대신 Windows Live Mail 을 쓰게 했습니다[3].

### Windows Live Mail

| 판 | 나온 날 | 필요한 Windows |
|---|---|---|
| 2009 (Wave 3) | 2009년 1월 8일 정식 판 | Windows XP 를 지원한 마지막 판입니다[2] |
| 2011 (Wave 4) | 2010년 9월 30일 | Vista 이상[2] |
| 2012 (Wave 5) | 2012년 8월 7일 | Windows 7·Server 2008 R2·Windows 8. Vista 지원이 끝났습니다[2] |

2012 판 지원은 2017년 1월 10일에 끝났습니다[2].

지원한 프로토콜은 POP3, IMAP, DeltaSync, Exchange ActiveSync, WebDAV 입니다[2]. DeltaSync 는 Hotmail·Outlook.com 전용이고, 2012 판은 DeltaSync 대신 Exchange ActiveSync 를 썼습니다[2]. Microsoft 는 2016년 6월 30일에 DeltaSync 지원을 끝냈지만, 2011·2012 판은 IMAP 이나 POP3 로 Hotmail 계정을 계속 쓸 수 있었습니다[2].

### 흔히 알려진 위치 (확인하지 못함)

| 프로그램 | 흔히 알려진 위치 |
|---|---|
| Outlook Express | `%USERPROFILE%\Local Settings\Application Data\Identities\{GUID}\Microsoft\Outlook Express\` |
| Windows Mail (Vista) | `%LOCALAPPDATA%\Microsoft\Windows Mail\`, 데이터베이스 파일 `WindowsMail.MSMessageStore` |
| Windows Live Mail | `%LOCALAPPDATA%\Microsoft\Windows Live Mail\` 와 계정별 하위 폴더, 계정 파일 `account{GUID}.oeaccount` |

- Outlook Express 의 저장 폴더와 계정 설정이 레지스트리에 있다는 설명도 흔합니다. 키 이름은 확인하지 못해 적지 않습니다.
- 기본 위치만 보지 않습니다. 디스크 전체에서 확장자(`.dbx`·`.mbx`·`.eml`·`.oeaccount`)와 이름(`MSMessageStore`)으로 찾습니다.
- Windows 11 25H2(빌드 26200) PC 한 대에는 `%LOCALAPPDATA%\Microsoft\Windows Live Mail` 과 `%LOCALAPPDATA%\Microsoft\Windows Mail` 폴더가 없었습니다 (관찰).

### ID 와 사용자 프로필

Outlook Express 는 ID (Identities) 를 썼고[3], Vista 의 Windows Mail 에서 이 ID 가 Windows 사용자 프로필로 바뀌었습니다[3]. ID 로 Windows 사용자 하나 안에 메일 사용자를 여럿 둘 수 있었다는 설명이 흔한데, 이번에 확인하지 못했습니다.

## 구조

### Outlook Express: `.dbx`

메일 폴더마다 `.dbx` 파일이 하나씩 있습니다[1]. `.dbx` 는 2GB 보다 작은 파일만 지원했고, 한계에 가까워지면 성능 문제가 있었습니다[1]. 데이터베이스가 자주 손상돼 복구 도구 시장이 생겼고, 공개 복구 도구로 UnDBX 가 있습니다[1]. 주소록은 Windows 주소록 파일(`.wab`)을 썼습니다[1].


- 폴더 목록 파일 `Folders.dbx` 와 `Inbox.dbx`·`Sent Items.dbx`·`Deleted Items.dbx`·`Offline.dbx`·`Pop3uidl.dbx` 같은 파일이 있다는 설명이 흔합니다. 확인하지 못했습니다.
- 시그니처, 헤더 안 값의 오프셋, 메시지를 담는 방식은 공개 명세로 확인하지 못해 적지 않습니다. 구현 코드로 알려진 값이 있지만, 명세로 다시 맞추기 전에는 보고서에 쓰지 않습니다.
- 지운 메시지 조각이 `.dbx` 안에 남아 되살릴 수 있다는 설명도 있습니다. 이번에 확인하지 못했습니다.

### Windows Mail (Vista)

메시지를 `.eml`·`.nws` 파일로 하나씩 저장했고 `.dbx` 는 쓰지 않았습니다[3]. 항목 관리는 ESE (Extensible Storage Engine) 데이터베이스가 맡았습니다[3]. 설정은 레지스트리 대신 사용자 프로필 안의 XML 파일에 두었고[3], 계정 정보는 메일 데이터 옆의 `.oeaccount` 파일에 있습니다[3].

### Windows Live Mail

메시지를 `.eml` 파일로 하나씩 저장하고[2], 폴더 구조는 ESE 데이터베이스 `Mail.MSMessageStore` 가 관리합니다[2]. 이 데이터베이스의 백업 사본은 `Backup` 하위 폴더에 둡니다[2]. 계정 파일 `account{GUID}.oeaccount` 는 XML 이고 비밀번호는 암호화돼 있다는 설명이 흔한데, 확인하지 못했습니다.

`.eml` 파일의 형식은 [인터넷 메일 형식](../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) 에서, ESE 데이터베이스의 구조는 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| `.dbx`·`.eml` 안에 메시지가 있으면, 그 메시지가 그 메일 폴더에 저장된 적이 있습니다 | 이 PC 에서 받거나 보냈다는 것. 메일 폴더는 다른 PC 에서 옮겨 올 수 있습니다 |
| `.oeaccount` 파일은 그 계정이 프로그램에 설정됐다는 근거입니다 | 그 계정을 쓴 사람이 누구인지 |
| ESE 데이터베이스의 행은 프로그램이 관리하던 메시지·폴더 목록입니다 | 데이터베이스에 행이 없는 메시지가 처음부터 없었다는 것. 손상된 데이터베이스는 읽는 방식에 따라 행 수가 달라집니다 |
| 파일이 들어 있는 사용자 프로필은 그 메일 폴더가 어느 Windows 계정 아래 있었는지 알려 줍니다 | Outlook Express 에서 그 계정의 메일 사용자가 한 사람이라는 것 |

### 보고서 문장

아래 날짜와 주소는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`Windows Live Mail` 폴더 아래 계정 폴더에 `.eml` 파일이 있습니다. 이 파일의 보낸 날짜 헤더는 2015-06-02 09:14 +0900 이고, 받는 사람 헤더에는 `partner@example.com` 이 있습니다."
- 쓰면 안 되는 문장: "사용자는 2015년 6월 2일 이 PC 에서 partner@example.com 에 메일을 보냈습니다."

앞 문장은 파일에 적힌 값만 말합니다. 이 PC 에서 보냈다고 쓰려면 헤더의 거친 서버와 계정 설정을 함께 봐야 합니다([메일 헤더 분석](../../03-techniques/analysis/email-header-analysis.md)).

## 시각 해석

- 메시지 헤더의 시각을 읽는 법은 [인터넷 메일 형식](../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) 과 [메일 헤더 분석](../../03-techniques/analysis/email-header-analysis.md) 에서 다룹니다.
- `.eml`·`.dbx` 파일의 NTFS 시각은 PC 에 파일이 생기고 바뀐 때입니다. 메일을 받은 때와 같다고 쓰려면 같은 판으로 재현해 확인합니다.
- `.dbx` 는 메일 폴더 하나에 파일 하나입니다[1]. 그래서 파일 시각은 폴더 안 어느 메시지가 바뀐 때인지 알려 주지 않습니다.
- ESE 데이터베이스 안의 시각 칸과 형식은 이번에 확인하지 못했습니다. 값을 읽을 때는 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 을 보고, 같은 메시지의 헤더 시각과 맞춰 봅니다.
- 옛 PC 의 이미지는 시간대 설정부터 확인합니다([시간대 설정](../system-account/time-zone.md)).

## 함정과 한계

1. **원본 ESE 데이터베이스를 바로 엽니다.** 압수 이미지에서 꺼낸 ESE 데이터베이스는 비정상 종료 상태인 경우가 많았습니다(관찰). 사본에서만 작업합니다. 비정상 종료와 손상을 다루는 법은 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다. 이 관찰은 SRUDB.dat·WebCacheV01.dat·Windows.edb 에서 한 것이고, `MSMessageStore` 는 직접 보지 않았습니다.
2. **도구 하나의 행 수를 믿습니다.** 손상된 ESE 데이터베이스는 읽는 방식에 따라 행 수가 달랐습니다(관찰). 두 가지 이상으로 열어 비교합니다.
3. **`Backup` 사본을 빠뜨립니다.** Windows Live Mail 은 데이터베이스의 백업 사본을 `Backup` 하위 폴더에 둡니다[2]. 본 데이터베이스와 사본의 목록을 비교합니다.
4. **데이터베이스에 없으면 메일이 없다고 봅니다.** 메시지는 `.eml` 파일로 따로 있습니다[2][3]. 폴더 안 `.eml` 목록과 데이터베이스 목록을 따로 세어 비교합니다.
5. **지운 `.eml` 을 데이터베이스에서만 찾습니다.** `.eml` 은 개별 파일이라, 지운 메일은 파일 시스템에서 찾아야 한다고 추론할 수 있습니다. 문서로 확인하지는 못했습니다. [마스터 파일 테이블](../filesystem/mft.md), [USN 변경 저널](../filesystem/usnjrnl.md), [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 를 함께 봅니다.
6. **크기가 2GB 에 가까운 `.dbx` 를 정상 파일로 봅니다.** `.dbx` 는 2GB 보다 작은 파일만 지원했고 손상도 잦았습니다[1]. 크기가 한계에 가까우면 손상을 의심하고, 복구 도구 두 가지 이상의 결과를 비교합니다.
7. **Windows 계정 하나를 메일 사용자 하나로 봅니다.** Outlook Express 에는 ID 가 있었습니다[3]. ID 로 메일 사용자를 여럿 둘 수 있었다는 설명이 흔합니다(확인하지 못함). `Identities` 아래 `{GUID}` 폴더가 여럿이면 메일 사용자도 여럿일 수 있습니다. 이 폴더 구조도 흔한 설명이라 검체에서 확인합니다.
8. **구현 코드의 값을 명세처럼 씁니다.** `.dbx` 시그니처와 오프셋은 공개 명세로 확인하지 못했습니다. 보고서에 쓸 때는 어느 구현 코드에서 가져온 값인지 밝힙니다.
9. **Hotmail 계정이 DeltaSync 로 계속 동기화됐다고 봅니다.** DeltaSync 지원은 2016년 6월 30일에 끝났습니다[2]. 그 뒤의 메일이 있으면 계정이 어떤 프로토콜로 설정됐는지 계정 파일에서 확인합니다.

## 직접 분석해 보기

### 원시 바이트로 한 번

`.dbx` 의 시그니처 값은 이 페이지에 적지 않았습니다. 대신 검체 안의 파일끼리 비교하는 방법을 씁니다.

1. 디스크에서 `.dbx` 파일을 모두 찾아 사본을 뜹니다.
2. 파일마다 앞 16바이트를 뽑아 나란히 놓습니다. 어느 바이트가 같고 어느 바이트가 다른지 적습니다.
3. 폴더 목록 파일과 메시지 폴더 파일은 첫 바이트가 조금 다르다는 설명이 있습니다. 확인하지 못했으므로 2번 결과로 직접 봅니다.
4. 공개 복구 도구의 소스가 파일을 알아보는 값과 2번 결과를 맞춰 봅니다.
5. 같은 앞 16바이트를 미할당 영역에서 찾으면 지워진 `.dbx` 의 시작 자리를 찾아볼 수 있습니다([삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)).

ESE 데이터베이스는 파일 머리의 상태 값으로 비정상 종료인지 먼저 봅니다. 헥스로 읽는 법은 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다. `.eml` 은 [인터넷 메일 형식](../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) 의 방법으로 헤더와 본문 경계를 찾습니다.

### 공개 도구로 한 번

- `.dbx`: UnDBX 같은 공개 복구 도구로 메시지를 풀어냅니다[1]. 다른 도구의 결과와 메시지 수를 비교합니다.
- `.eml`: 메일 뷰어나 파서로 헤더와 첨부를 뽑습니다.
- `Mail.MSMessageStore`: ESE 를 읽는 공개 도구로 표 목록을 뽑습니다. 도구 두 가지 이상으로 열어 행 수를 비교합니다([도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)).
- `.oeaccount`: 글자 편집기로 열어 계정 설정을 봅니다.

> 그림 자리: Outlook Express(폴더마다 `.dbx`) → Vista Windows Mail(`.eml` + ESE) → Windows Live Mail(`.eml` + `Mail.MSMessageStore` + `Backup`) 으로 저장 방식이 바뀐 흐름을 판·Windows 연대와 함께 보여 주는 그림

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) | 데이터베이스 상태, 복구, 표 읽기 |
| [인터넷 메일 형식](../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) | `.eml` 의 헤더·본문·첨부 |
| [메일 헤더 분석](../../03-techniques/analysis/email-header-analysis.md) | 보낸 시각, 거친 서버 |
| [설치 프로그램](../system-account/uninstall.md) | Windows Live Mail 이 깔렸는지 |
| [사용자 프로필 목록](../system-account/profilelist.md) | 메일 폴더가 어느 사용자 프로필에 속하는지 |
| [마스터 파일 테이블](../filesystem/mft.md) · [USN 변경 저널](../filesystem/usnjrnl.md) | `.eml`·`.dbx` 가 생기고 지워진 때 |
| [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) | 지운 `.eml`·`.dbx` 조각 |

메일로 누구와 연락했는지 정리하는 순서는 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 에서 다룹니다.

## 실습

**공개 검체(NIST CFReDS 등)** 가운데 Windows XP·Vista·7 이미지로 해 봅니다.

1. `.dbx` 파일은 몇 개이고 어느 폴더에 있습니까? 경로 안의 `{GUID}` 는 몇 가지입니까?
2. `.dbx` 파일들의 앞 16바이트를 비교하면 몇 가지 모양이 나옵니까? 어느 파일이 다른 모양입니까?
3. 공개 복구 도구 두 가지로 같은 `.dbx` 를 풀면 메시지 수가 같습니까?
4. Windows Live Mail 을 쓴 이미지라면 `.eml` 파일 수와 `Mail.MSMessageStore` 의 행 수를 비교해 보십시오. `Backup` 폴더의 사본과는 어떻게 다릅니까?
5. 계정 파일에 적힌 프로토콜은 무엇입니까? 2016년 6월 30일 뒤의 메일이 있다면 어떤 프로토콜로 받았습니까?

**직접 만든 가상 머신** 에 옛 Windows 와 Windows Live Mail 을 깔 수 있다면, 메일 하나를 지우기 전과 뒤의 `.eml` 파일과 데이터베이스를 비교해 보십시오. 지운 메일의 `.eml` 은 어디로 갑니까?

## 참고 문헌

1. Wikipedia, "Outlook Express" — https://en.wikipedia.org/wiki/Outlook_Express
2. Wikipedia, "Windows Live Mail" — https://en.wikipedia.org/wiki/Windows_Live_Mail
3. Wikipedia, "Mail (Windows)" — https://en.wikipedia.org/wiki/Windows_Mail
