---
title: "다운로드 출처 표시"
parent: "아티팩트 · 파일시스템"
nav_order: 1460
---

# 다운로드 출처 표시 (Zone.Identifier)

`Zone.Identifier` 는 파일에 붙는 대체 데이터 스트림 (Alternate Data Stream, ADS) 의 이름입니다. 내용은 URL 보안 영역 번호를 적은 짧은 텍스트입니다(참고 1). 크롬 계열 브라우저는 받은 주소(HostUrl)와 참조 페이지 주소(ReferrerUrl)도 함께 적습니다(참고 4). 그래서 파일이 인터넷 같은 바깥에서 들어왔는지, 어느 주소에서 왔는지 알려 주는 단서가 됩니다. 다만 표시가 붙지 않거나 지워지는 경우가 있어, 표시가 없다고 해서 안에서 만든 파일이라고 볼 수는 없습니다.

## 무엇을 기록하나 · 왜 생기나

### 파일에 붙는 이름 있는 스트림입니다

`Zone.Identifier` 는 파일 본문과 같은 MFT 항목에 붙는 이름 있는 `$DATA` 스트림입니다(참고 1). 내용은 `[ZoneTransfer]` 줄과 `ZoneId=3` 같은 줄로 이뤄지고, 줄 끝은 CR LF 입니다(참고 1). 스트림의 구조와 이름 쓰는 법은 [대체 데이터 스트림 (ADS)](../../01-foundations/disk-volume/ntfs/ads.md)에서 다룹니다.

### 누가 붙이나

Windows 는 첨부 파일에 영역 정보를 붙이는데, 이 동작은 첨부 파일 관리자 (Attachment Manager) 정책으로 끌 수 있습니다(참고 3). 크롬 계열 브라우저는 보통 Windows 첨부 파일 서비스의 `IAttachmentExecute::Save` 를 불러 표시를 맡깁니다(참고 4). 이 호출은 백신 검사를 할 수 있어서, 정책에 막히거나 감염된 파일은 이 호출이 지울 수 있습니다(참고 4).

브라우저가 표시를 직접 쓰는 경우도 있습니다. 0바이트 파일일 때, 클라이언트 GUID 가 없을 때, 첨부 파일 서비스를 부르지 못했을 때이고, 이때는 늘 `ZoneId=3` 을 씁니다(참고 4). 다른 브라우저, 메신저, 압축 프로그램이 어떤 필드를 쓰는지는 프로그램마다 달라 실제 데이터로 확인합니다. 압축을 풀 때 표시를 옮기는지는 [압축 프로그램 사용 기록](../file-folder-usage/7-zip-winrar-bandizip.md)에서 다룹니다.

### NTFS 가 있어야 붙습니다

영역 정보를 붙이려면 NTFS 가 있어야 하고, FAT32 에서는 알림 없이 실패합니다(참고 3). FAT32 처럼 ADS 가 없는 파일시스템에서는 브라우저가 직접 쓰는 것도 실패합니다(참고 4).

## 위치와 버전별 차이

### 위치

- 표시가 붙은 파일의 MFT 항목 안, 이름이 `Zone.Identifier` 인 `$DATA` 속성입니다([마스터 파일 테이블](mft.md)).
- 스트림 내용이 MFT 항목 안에 있는지, 밖 클러스터에 있는지는 속성 머리로 구분합니다([데이터 런과 상주·비상주 데이터](../../01-foundations/disk-volume/ntfs/data-run-resident-non-resident.md)).

### 표시를 막거나 지우는 정책

첨부 파일 관리자 정책은 사용자 구성 정책입니다(참고 3).

| 정책 | 레지스트리 값 이름 | 켜면 (참고 3) |
|---|---|---|
| Do not preserve zone information in file attachments | `SaveZoneInformation` | Windows 가 첨부 파일에 영역 정보를 붙이지 않습니다. 끄거나 설정하지 않으면 붙입니다 |
| Hide mechanisms to remove zone information | `HideZoneInfoOnProperties` | 파일 속성 창의 "차단 해제 (Unblock)" 버튼과 경고 창의 체크 상자를 숨깁니다 |

- 두 값의 레지스트리 키는 `Software\Microsoft\Windows\CurrentVersion\Policies\Attachments` 입니다. ADMX 파일은 `AttachmentManager.admx` 입니다(참고 3).
- `SaveZoneInformation` 값이 있으면 정책을 건드린 흔적으로 적습니다. 숫자 값(1·2)이 각각 무엇을 뜻하는지는 가상 머신에서 정책을 켜고 꺼 보며 확인합니다.
- 레지스트리 읽는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

### 버전별 차이

| 항목 | 버전 | 근거 |
|---|---|---|
| ZoneId -1 (URLZONE_INVALID) | IE7 부터 | 참고 2 |
| 첨부 파일 관리자 정책 CSP (`./User/Vendor/MSFT/Policy/Config/AttachmentManager/...`) | Windows 10 1703 이상 | 참고 3 |
| 크롬 계열이 ReferrerUrl·HostUrl 을 붙이는 방식 | Windows 10 이상에서 IAttachmentExecute 동작에 맞춤 (코드 주석) | 참고 4 |

## 구조

### 내용

```
[ZoneTransfer]
ZoneId=3
ReferrerUrl=<참조 페이지 주소>
HostUrl=<받은 주소>
```

첫 줄은 절 이름 `[ZoneTransfer]` 이고, `ZoneId` 는 URL 보안 영역 번호입니다(참고 1). 크롬 계열 브라우저가 직접 쓸 때는 `[ZoneTransfer]\r\nZoneId=3\r\n` 다음에 `ReferrerUrl`(있을 때만), 그다음 `HostUrl` 을 쓰는데, 이 순서는 Windows 첨부 파일 서비스가 내는 결과와 맞춘 것입니다(참고 4).

### ZoneId 값

ZoneId 번호는 URLZONE 열거형의 값으로 읽습니다(참고 2).

| 값 | URLZONE_ 뒤 이름 | 뜻 (참고 2) |
|---|---|---|
| 0 | LOCAL_MACHINE | 내 컴퓨터. 화면 설정에는 나오지 않습니다 |
| 1 | INTRANET | 로컬 인트라넷 |
| 2 | TRUSTED | 신뢰할 수 있는 사이트 |
| 3 | INTERNET | 인터넷. 대부분의 사이트가 여기에 듭니다 |
| 4 | UNTRUSTED | 제한된 사이트 |
| -1 | INVALID | 알맞은 영역이 없을 때 (IE7) |
| 1000~10000 | 사용자 정의 영역 | |

문서의 선언에 숫자로 적힌 것은 INVALID = -1, LOCAL_MACHINE = 0, 미리 정한 영역의 상한 999, 사용자 정의 영역 1000~10000 입니다. 1~4 는 숫자 없이 LOCAL_MACHINE 다음에 이어지므로 C 열거형 규칙(앞 값에 1씩 더함)으로 읽은 값입니다(참고 2).

### 크롬 계열 브라우저가 주소를 적는 규칙

- 받은 주소가 비어 있으면 다운로드 요청을 시작한 쪽의 origin(스킴·호스트·포트) 주소를 대신 씁니다. 전체 페이지 주소가 아닙니다(참고 4).
- 다음 경우에는 `HostUrl` 에 `about:internet` 을 넣습니다.
  - 쓸 주소가 없을 때: 주소가 유효하지 않을 때, HTTP·HTTPS 가 아닐 때, 시크릿(off-the-record) 다운로드일 때
  - 주소가 `INTERNET_MAX_URL_LENGTH` 보다 길 때
- 참조 주소가 없거나 너무 길면 `ReferrerUrl` 줄을 빼고 씁니다.
- 주소를 넣기 전에 `SanitizeUrlForQuarantine` 이라는 정리 함수를 거칩니다. 그래서 `HostUrl` 은 원래 주소를 정리한 뒤의 값입니다.

### 실제 PC 한 대에서 본 값

받은 파일 폴더를 `Get-Content -Stream Zone.Identifier` 로 읽은 결과입니다.

| 항목 | 값 |
|---|---|
| 폴더 안 파일 | 262개 |
| `Zone.Identifier` 가 있는 파일 | 211개 |
| ZoneId | 211개 모두 3 |
| 줄 구성 | 대부분 `[ZoneTransfer]`·ZoneId·ReferrerUrl·HostUrl 네 줄. 일부(.csv·.zip·.mp4 등)는 ReferrerUrl 없이 HostUrl 만 |
| HostUrl 의 스킴 | https 195개, http 8개, about 3개 |

about 3개는 `about:internet` 으로 보입니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 파일에 영역 표시가 붙어 있습니다. 표시를 쓴 프로그램이 이 파일을 그 영역(예: 3 인터넷)에서 온 것으로 적었습니다 | 언제 받았는지. 내용에 시각 필드가 없습니다 |
| HostUrl·ReferrerUrl 이 있으면, 표시를 쓴 프로그램이 적은 주소 | 어느 프로그램이 표시를 썼는지 |
| 표시가 붙을 때 파일이 NTFS 볼륨에 있었습니다 | HostUrl 이 파일을 실제로 받은 최종 주소인지 (`about:internet`, origin 대신 쓰기, 주소 정리 함수) |
| | 사용자가 파일을 열거나 실행했는지 |
| | 표시가 없을 때 바깥에서 오지 않았다는 것 |
| | 표시를 붙인 뒤 파일 내용이 바뀌지 않았는지 |

### 보고서 문장

아래 경로와 주소는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`C:\Users\A\Downloads\f.zip` 에 `Zone.Identifier` 스트림이 있습니다. 스트림의 ZoneId 는 3 이고, HostUrl 은 `https://example.org/f.zip` 입니다. 이 값은 표시를 쓴 프로그램이 이 파일을 인터넷 영역의 이 주소에서 온 것으로 적었다는 뜻입니다."
- 쓰면 안 되는 문장: "사용자 A 가 example.org 에서 f.zip 을 내려받아 실행했다."

## 시각 해석

- `Zone.Identifier` 내용에는 시각 필드가 없습니다(참고 1, 참고 4).
- 받은 시각은 다른 기록에서 찾습니다.
  - 브라우저의 다운로드 기록: [방문·다운로드 기록 (History)](../browsers/chrome-edge-whale/history.md), [방문·다운로드·즐겨찾기 (places.sqlite)](../browsers/firefox/places-sqlite.md)
  - 표시가 붙은 파일의 [$MFT](mft.md) 시각
  - [USN 변경 저널](usnjrnl.md)의 레코드
- `Zone.Identifier` 는 이름 있는 스트림이므로, 스트림이 생기거나 지워지면 USN 이유 플래그 STREAM_CHANGE(이름 있는 스트림 추가·삭제)의 정의에 들어맞습니다(참고 1). 실제 다운로드나 차단 해제 때 이 플래그가 찍히는지는 아래 실습 4번처럼 가상 머신에서 확인합니다.
- 여러 기록의 시각을 합칠 때는 [타임라인 작성](../../03-techniques/analysis/timeline/index.md)을 봅니다.

## 함정과 한계

1. **표시가 없다고 안에서 만든 파일이 아닙니다.** FAT32 에서는 표시가 붙지 않고(참고 3, 참고 4), 정책으로 끌 수 있으며(참고 3), 차단 해제로 지울 수도 있습니다(참고 3). 표시를 쓰지 않는 프로그램도 있을 수 있습니다.
2. **ZoneId 3 으로 사이트를 말합니다.** 3 은 인터넷 영역이라는 뜻일 뿐입니다(참고 2). 어느 사이트인지는 HostUrl 과 브라우저 기록으로 따로 봅니다.
3. **HostUrl 을 파일 주소로 단정합니다.** 받은 주소가 비면 요청한 페이지 주소를 대신 쓰고, 시크릿 다운로드나 너무 긴 주소는 `about:internet` 이 됩니다(참고 4). 받은 파일 폴더 하나에서도 `about` 으로 시작하는 HostUrl 이 3개 나왔습니다.
4. **ReferrerUrl 이 없다고 참조 페이지가 없었다고 봅니다.** 참조 주소가 너무 길어도 줄을 뺍니다(참고 4).
5. **다운로드 기록은 있는데 파일이 없습니다.** 첨부 파일 서비스 호출이 정책에 막히거나 감염된 파일을 지울 수 있습니다(참고 4). 백신 기록을 함께 봅니다.
6. **압축을 푼 파일의 표시를 다운로드 표시로 읽습니다.** 압축 프로그램이 압축 파일의 표시를 풀린 파일에 옮겼을 수 있습니다. [압축 프로그램 사용 기록](../file-folder-usage/7-zip-winrar-bandizip.md)을 봅니다.
7. **ZoneId 1~4 를 문서에 적힌 숫자로 인용합니다.** 문서 선언에는 1~4 가 숫자로 적혀 있지 않습니다. 열거형 규칙으로 읽은 값이라고 밝힙니다(참고 2).
8. **옮긴 사본에서 읽습니다.** 파일을 다른 매체로 복사하거나 압축·메일로 옮기면 표시가 따라가지 않을 수 있습니다. 그래서 이미지나 원본 볼륨의 MFT 항목에서 직접 읽습니다.

### 지우기와 조작

- **차단 해제**: 파일 속성 창의 "차단 해제" 버튼과 경고 창의 체크 상자로 영역 정보를 지울 수 있습니다. 지우면 위험한 첨부 파일도 열 수 있게 됩니다(참고 3).
- **정책 변경**: `SaveZoneInformation` 정책을 켜면 표시가 붙지 않습니다(참고 3). 사용자별 정책 값을 확인합니다.
- **스트림 삭제·수정**: 스트림을 지우거나 바꾸면 STREAM_CHANGE 정의에 들어맞는 USN 레코드를 찾아봅니다(참고 1). 스트림을 지운 흔적은 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md)에서도 찾습니다.
- 표시를 일부러 없앤 정황은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md)에서 다른 흔적과 함께 따집니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 위 형식 규칙에 맞춰 만든 예시입니다. 실제 데이터에서 뽑은 값이 아닙니다. 주소는 예시용 도메인입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    5B 5A 6F 6E 65 54 72 61 6E 73 66 65 72 5D 0D 0A   [ZoneTransfer]..
0x10    5A 6F 6E 65 49 64 3D 33 0D 0A 52 65 66 65 72 72   ZoneId=3..Referr
0x20    65 72 55 72 6C 3D 68 74 74 70 73 3A 2F 2F 65 78   erUrl=https://ex
0x30    61 6D 70 6C 65 2E 6F 72 67 2F 0D 0A 48 6F 73 74   ample.org/..Host
0x40    55 72 6C 3D 68 74 74 70 73 3A 2F 2F 65 78 61 6D   Url=https://exam
0x50    70 6C 65 2E 6F 72 67 2F 66 2E 7A 69 70 0D 0A      ple.org/f.zip..
```

1. 0x00 부터 `[ZoneTransfer]` 가 오고, 0x0E 의 `0D 0A` 가 줄 끝(CR LF)입니다.
2. 0x10 의 `ZoneId=3` 은 인터넷 영역입니다. `33` 은 ASCII 문자 '3' 입니다. 숫자 3 을 이진값으로 적은 것이 아닙니다.
3. 0x1A 부터 `ReferrerUrl=https://example.org/` 가 옵니다.
4. 0x3C 부터 `HostUrl=https://example.org/f.zip` 이 옵니다.
5. 스트림 크기는 95바이트입니다. 마지막 두 바이트도 `0D 0A` 입니다.

### 실행 중인 시스템에서

- PowerShell 에서 `Get-Content -Stream Zone.Identifier <파일>` 로 내용을 읽습니다.
- 한 폴더의 파일을 한꺼번에 읽을 때도 같은 명령을 파일마다 돌립니다.

### 이미지에서

1. 파일의 MFT 항목에서 이름이 `Zone.Identifier` 인 `$DATA` 속성을 찾습니다.
2. 상주 속성이면 항목 안의 값을 읽고, 비상주 속성이면 데이터 런을 따라가 클러스터를 읽습니다.
3. 내용을 텍스트로 풀어 절 이름과 키를 확인합니다.
4. 같은 파일의 이름·시각·크기를 함께 적습니다.

### 공개 도구로 한 번

The Sleuth Kit 같은 공개 도구는 MFT 항목의 속성 목록에서 이름 있는 스트림을 보여 줍니다. 어느 도구를 쓰든 아래를 확인합니다.

- 이름 있는 `$DATA` 를 모두 보여 주는지 확인합니다.
- 스트림 내용을 그대로 뽑는지, 줄 끝을 바꾸는지 확인합니다.
- 비할당 MFT 항목의 스트림도 읽는지 확인합니다.
- 몇 개는 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [방문·다운로드 기록 (History)](../browsers/chrome-edge-whale/history.md) | 크롬 계열 브라우저의 다운로드 항목에 적힌 저장 경로·주소·시각 |
| [방문·다운로드·즐겨찾기 (places.sqlite)](../browsers/firefox/places-sqlite.md) | 파이어폭스의 다운로드 기록 |
| [마스터 파일 테이블 ($MFT)](mft.md) | 표시가 붙은 파일의 이름·시각·크기와 이름 있는 `$DATA` |
| [USN 변경 저널 ($UsnJrnl)](usnjrnl.md) | 파일을 만든 기록과 STREAM_CHANGE 레코드 |
| [압축 프로그램 사용 기록](../file-folder-usage/7-zip-winrar-bandizip.md) | 풀린 파일에 표시가 옮겨졌는지 |
| [Windows Defender 탐지](../event-logs/1116-1117.md) | 다운로드 기록은 있는데 파일이 없을 때 백신이 막았는지 |

파일의 출처를 여러 기록으로 좁히는 순서는 [이 파일은 어디서 왔나](../../04-scenarios/activity/file-origin.md)에서 다룹니다. 악성 파일이 들어온 경로를 좇을 때는 [악성코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md)를 봅니다.

## 실습

**직접 만든 Windows 10·11 가상 머신**에서 해 봅니다.

1. 크롬 계열 브라우저로 파일 하나를 NTFS 볼륨에 내려받고 `Get-Content -Stream Zone.Identifier` 로 읽어 보십시오. 줄은 몇 개이고 ZoneId 는 몇입니까?
2. 같은 파일을 시크릿 창에서 내려받아 보십시오. HostUrl 은 무엇입니까?
3. FAT32 로 포맷한 USB 메모리에 바로 내려받아 보십시오. 표시가 붙었습니까?
4. 1번 파일의 속성 창에서 "차단 해제" 를 누른 뒤 다시 읽어 보십시오. 스트림이 남아 있습니까? USN 저널에 어떤 레코드가 생겼습니까?
5. "Do not preserve zone information in file attachments" 정책을 켜고 다시 내려받아 보십시오. 레지스트리의 `SaveZoneInformation` 값은 무엇으로 바뀌었습니까?
6. 내려받은 압축 파일을 여러 압축 프로그램으로 풀어 보십시오. 풀린 파일에 표시가 붙었습니까?

**NIST CFReDS 같은 공개 시험용 Windows 디스크 이미지**로도 풀어 봅니다.

1. 사용자 받은 파일 폴더에서 `Zone.Identifier` 가 있는 파일은 몇 개입니까? ZoneId 는 어떤 값들입니까?
2. HostUrl 이 있는 파일을 하나 골라 브라우저 다운로드 기록과 맞춰 보십시오. 주소와 저장 경로가 같습니까?
3. 다운로드 기록에는 있는데 디스크에 없는 파일이 있다면, 그 이유를 어떤 기록으로 확인할 수 있을지 적어 보십시오.

## 참고 문헌

1. libyal/libfsntfs, "New Technologies File System (NTFS)" 형식 문서 — https://raw.githubusercontent.com/libyal/libfsntfs/main/documentation/New%20Technologies%20File%20System%20(NTFS).asciidoc
2. Microsoft Learn, "URLZONE enumeration" (Internet Explorer 보관 문서, 2017-08-15) — https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/ms537175(v=vs.85)
3. Microsoft Learn, "AttachmentManager Policy CSP" — https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-attachmentmanager
4. Chromium 소스, components/services/quarantine/quarantine_win.cc (main 브랜치) — https://raw.githubusercontent.com/chromium/chromium/main/components/services/quarantine/quarantine_win.cc
