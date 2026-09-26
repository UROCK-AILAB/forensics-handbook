---
title: "아웃룩"
parent: "아티팩트 · 메일"
nav_order: 1860
has_children: true
has_toc: false
---

# 아웃룩 (Outlook)

## 한 줄 요약

클래식 Outlook (OUTLOOK.EXE) 은 메일·연락처·일정 같은 항목을 PST·OST 데이터 파일에 담고, 사용자 설정을 사용자 레지스트리에 둡니다. 이 허브는 데이터 파일의 구조와 종류, 지운 메시지, 따로 저장한 메시지, 첨부 사본, 자동완성 목록, 계정 설정을 차례로 안내합니다.

## 왜 중요한가

PST 에는 메일·연락처·일정·작업·메모·업무일지가 들어 있어서 누구와 언제 무엇을 주고받았는지 되짚는 바탕 자료가 됩니다. POP·IMAP 계정은 모든 Outlook 정보를 PST 에 담습니다. Exchange·Microsoft 365 계정은 캐시된 Exchange 모드 (Cached Exchange Mode) 에서 서버 사서함의 사본을 PC 의 OST 에 두지만, 자동 보관 (AutoArchive) 을 쓰면 PST 가 생길 수 있습니다.

지운 메시지는 서버 사서함의 숨은 폴더나 데이터 파일 안의 빈 공간에 남을 수 있습니다. 데이터 파일 밖에도 따로 저장한 `.msg` 파일, 첨부를 열 때 생긴다고 알려진 사본, 메일을 보낸 상대의 자동완성 목록, 레지스트리의 Outlook 설정 같은 흔적이 있어서 데이터 파일이 없어도 단서를 찾을 수 있습니다.

증명하지 못하는 것도 분명합니다. PST 는 다른 PC 에서 옮겨 올 수 있으므로 PST 안에 메일이 있다는 것만으로 이 PC 에서 주고받았다고 보지 않습니다. 또 파일에 없는 메일이 처음부터 없었다고 보지 않는데, 지운 메시지가 서버에만 남아 있을 수 있기 때문입니다.

### 클래식 Outlook 과 새 Outlook

이 허브는 클래식 Outlook 을 다룹니다. 새 Outlook (Outlook for Windows) 은 캐시된 Exchange 모드를 쓰지 않으며, 사서함과 PST 사이에서 메일을 옮기고, 복사하고, 지우고, 끌어 놓을 수 있고 사서함을 PST 로 내보낼 수도 있습니다. 새 Outlook 이 메일을 PC 어디에 어떤 형식으로 두는지는 [새 Outlook](../new-outlook.md) 페이지를 봅니다.

검체를 열면 먼저 어느 Outlook 을 썼는지 확인합니다. 클래식 Outlook 이 없는 PC 에는 이 허브의 흔적 대부분이 없을 수 있습니다.

## 한눈에 보기

> 그림 자리: 서버 사서함(Recoverable Items 포함) ↔ PC 의 OST, PC 의 PST·`.msg`·첨부 사본·자동완성 목록·레지스트리 설정을 한 장에 놓고, 각 흔적이 어느 하위 페이지에서 다뤄지는지 표시한 그림

### 위치와 알려 주는 것

| 흔적 | 어디에 있나 | 판에 따른 차이 | 알려 주는 것 | 자세히 |
|---|---|---|---|---|
| PST | 새 PST 기본 위치는 Outlook 2016 이후 `Documents\Outlook Files\`, 앞선 판 `AppData\Local\Microsoft\Outlook\` (Windows 10 기준) | ANSI·유니코드·4KB 형식 | 메일·연락처·일정 같은 항목과 첨부 | [데이터 파일 구조](pst-ost.md) |
| OST | 공식 자료 없음. 검체에서 확인 | 캐시된 Exchange 모드에서만 생김. 새 Outlook 에는 이 모드가 없음 | 서버 사서함의 사본 | [PST와 OST 차이](cached-mode-exchange.md) |
| Recoverable Items 폴더 | 서버 사서함의 숨은 영역. PC 에는 없음 | 하위 페이지는 Exchange Online 기준 | 지운 항목, 보존 중 고친 항목 | [지운 메시지 복구](recoverable-items-free-blocks.md) |
| 데이터 파일의 빈 공간 | PST·OST 안 | 형식마다 페이지 크기가 다름 | 지운 데이터가 남았을 수 있는 자리 | [지운 메시지 복구](recoverable-items-free-blocks.md) |
| `.msg` | 사용자가 저장한 곳. 정해진 폴더 없음 | Windows 버전과 관계없음 | 메시지 한 통과 그 수신자·첨부 | [개별 메시지 파일](msg.md) |
| 첨부 임시 폴더 | 공식 자료 없음. 검체에서 확인 | Windows 판에 따라 다르다는 설명이 흔함 | 첨부 사본 | [첨부 임시 폴더](olk-content-outlook.md) |
| 자동완성 목록 | Outlook 2007 이전 `%APPDATA%\Microsoft\Outlook` 의 `.nk2`, 2010 이후 기본 메시지 저장소 안의 숨은 메시지 | 판에 따라 저장 방식이 다름 | 메일을 보낸 상대의 주소와 표시 이름 | [자동완성 목록](nk2-stream-autocomplete.md) |
| 레지스트리 설정 | NTUSER.DAT 의 `Software\Microsoft\Office\<버전>\Outlook` | 버전 번호 `11.0`~`16.0` | Outlook 판, 데이터 파일·목록 한도, 계정 | [계정·프로필 레지스트리](outlook-profiles.md) |

- PST 기본 위치는 새 파일을 만들 때의 값입니다. 검체에서는 확장자와 헤더 시그니처로 디스크 전체를 찾습니다.
- OST 위치, 첨부 임시 폴더, 프로필 키의 자리는 공식 자료가 없고 흔한 설명만 있습니다. 각 하위 페이지는 흔한 설명과 공식 자료가 있는 사실을 나눠 적습니다.

### 먼저 확인할 것

1. 어느 Outlook 을 썼는지: 클래식 Outlook 인지, 새 Outlook 인지, 판은 무엇인지 봅니다([설치 프로그램](../../system-account/uninstall.md), [스토어 앱 설치 목록](../../system-account/appx-staterepository.md)).
2. 어떤 계정이었는지: POP·IMAP 인지, Exchange·Microsoft 365 인지 봅니다. 계정 종류에 따라 데이터 파일 종류와 지운 메시지가 남는 자리가 달라집니다.
3. 데이터 파일이 어디에 몇 개 있는지: 확장자와 헤더로 디스크 전체를 찾습니다.
4. 서버 쪽 자료가 필요한지: 지운 메시지나 PC 에 내려받지 않은 메일은 서버에서 따로 확보해야 할 수 있습니다([증거 획득](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)).

## 읽는 순서

1. [데이터 파일 구조 (PST·OST)](pst-ost.md) — 헤더의 시그니처·형식 버전·인코딩을 손으로 읽습니다. 파일 안의 세 층과 항목 번호, 크기 한도 레지스트리 값도 다룹니다.
2. [PST와 OST 차이 (Cached Mode·Exchange)](cached-mode-exchange.md) — 캐시된 Exchange 모드에서 OST 에 무엇이 들어가는지 다룹니다. 계정 종류와 파일 종류가 어떻게 이어지는지도 봅니다.
3. [지운 메시지 복구 (Recoverable Items·Free Blocks)](recoverable-items-free-blocks.md) — 서버 쪽 Recoverable Items 폴더와 파일 쪽 빈 공간을 나눠 봅니다.
4. [개별 메시지 파일 (MSG)](msg.md) — 메시지 한 통을 담은 복합 파일의 저장소·스트림 구조를 읽습니다.
5. [첨부 임시 폴더 (OLK·Content.Outlook)](olk-content-outlook.md) — 첨부를 열 때 생긴다고 알려진 사본 폴더를 찾습니다. 폴더 안 파일을 데이터 파일 안 첨부와 해시로 맞춥니다.
6. [자동완성 목록 (NK2·Stream_Autocomplete)](nk2-stream-autocomplete.md) — 메일을 보낸 상대 목록이 판에 따라 어디에 있는지 다룹니다. 목록이 증명하는 것과 증명하지 못하는 것을 나눕니다.
7. [계정·프로필 레지스트리 (Outlook Profiles)](outlook-profiles.md) — Office 버전 번호로 Outlook 판을 가늠합니다. 계정 정보가 든 키를 하이브에서 직접 찾는 법을 다룹니다.

## 함께 볼 페이지

- [MAPI 속성](../../../01-foundations/app-mail-data/mapi-property.md) — 메시지의 제목·시각·보낸 사람 같은 값이 들어가는 형식입니다.
- [OLE 복합 파일](../../../01-foundations/shell-document-formats/compound-file-binary.md) — `.msg` 파일의 바탕 형식입니다.
- [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) · [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) — 데이터 파일과 레지스트리의 시각·글자를 읽습니다.
- [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) — Outlook 설정 키와 값을 읽습니다.
- [인터넷 메일 형식](../../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) · [메일 헤더 분석](../../../03-techniques/analysis/email-header-analysis.md) — 메시지가 거쳐 온 서버와 보낸 시각을 헤더로 확인합니다.
- [새 Outlook](../new-outlook.md) · [Windows 메일 앱](../hxstore.md) · [썬더버드](../thunderbird.md) · [옛 윈도 메일 프로그램](../outlook-express-windows-live-mail.md) — 다른 메일 프로그램의 흔적입니다.
- [암호화 증거 다루기](../../../03-techniques/analysis/encrypted-evidence/index.md) — 암호화한 데이터 파일을 다룹니다.
- [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) · [파일 내용 검색](../../../03-techniques/analysis/content-search/index.md) — 지운 데이터 파일과 파일 안 글자를 찾습니다.
- [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) — 같은 데이터 파일을 도구 두 개로 열어 비교합니다.
- [누구와 연락을 주고받았나](../../../04-scenarios/activity/communication-reconstruction.md) · [자료를 밖으로 빼돌렸나](../../../04-scenarios/exfiltration/data-exfiltration/index.md) — Outlook 흔적을 쓰는 조사 흐름입니다.

## 참고 문헌

- libyal libpff, "Personal Folder File (PFF) format" (문서 판 0.0.48, 2020-07) — https://raw.githubusercontent.com/libyal/libpff/main/documentation/Personal%20Folder%20File%20(PFF)%20format.asciidoc
- Microsoft 지원, "Introduction to Outlook Data Files (.pst and .ost)" — https://support.microsoft.com/en-us/office/introduction-to-outlook-data-files-pst-and-ost-222eaf92-a995-45d9-bde2-f331f60e2790
- Microsoft 지원, "Turn on Cached Exchange Mode" — https://support.microsoft.com/en-us/office/turn-on-cached-exchange-mode-7885af08-9a60-4ec3-850a-e221c1ed0c1c
- Microsoft Learn, "Recoverable Items folder in Exchange Online" (2026-07-16 갱신) — https://learn.microsoft.com/en-us/exchange/security-and-compliance/recoverable-items-folder/recoverable-items-folder
- Microsoft Learn, "[MS-OXMSG]: Top Level Structure" (2.3 절, 2025-05-20 갱신) — https://learn.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxmsg/1a69e000-f391-4c03-9d43-32d5f554bca7
- Microsoft Learn, "The Outlook AutoComplete list" (옛 KB 2199226, 2025-06-24) — https://learn.microsoft.com/en-us/microsoft-365-apps/outlook/contacts/outlook-autocomplete-list
- Microsoft Learn, "Configure Size Limit for PST and OST Files In Outlook" (옛 KB 832925, 2026-09-10) — https://learn.microsoft.com/en-us/microsoft-365-apps/outlook/data-files/configure-size-limit-outlook-data-files
