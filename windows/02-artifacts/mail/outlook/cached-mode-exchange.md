# PST와 OST 차이 (Cached Mode·Exchange)

> 상위 허브: [아웃룩 (Outlook)](index.md)

## 한 줄 요약

PST 는 Outlook 항목을 PC 에 담아 두는 파일입니다. OST 는 캐시된 Exchange 모드 (Cached Exchange Mode) 에서 서버 사서함의 사본을 두는 파일입니다. OST 의 원본은 서버에 있습니다. 그래서 OST 에 무엇이 들어 있는지는 오프라인 기간과 공유 폴더 설정에 따라 달라집니다.

## 무엇을 기록하나 · 왜 생기나

### 계정 종류와 데이터 파일

| 계정 | 데이터 파일 | 근거 |
|---|---|---|
| POP·IMAP | PST 에 모든 Outlook 정보를 담습니다 | Microsoft 지원 문서 |
| Exchange·Microsoft 365 (캐시 모드) | OST 에 사서함 사본을 둡니다 | Microsoft 지원 문서 |
| Exchange 에서 자동 보관 (AutoArchive) 사용 | 자동 보관용 PST 가 생길 수 있습니다 | Microsoft 지원 문서 |

최신 판 Outlook 에서는 IMAP 계정도 OST 를 쓴다는 설명이 있습니다. 이번에 연 자료로는 확인하지 못했습니다. 그래서 파일 종류만 보고 계정 종류를 단정하지 않습니다. 계정 종류는 [계정·프로필 레지스트리 (Outlook Profiles)](outlook-profiles.md)와 함께 봅니다.

### 캐시된 Exchange 모드

- 캐시 모드는 사서함 사본을 PC 에 두고, Exchange 서버와 자주 맞춥니다.
- 캐시 모드는 Exchange·Microsoft 365 계정에서만 씁니다. POP·IMAP 계정에는 쓰지 못합니다.
- 기본으로 최근 12개월 메일을 오프라인에 둡니다. 사용자가 이 기간을 바꿀 수 있습니다.
- 기간 선택지의 정확한 목록과 그 설정을 담는 레지스트리 값은 이번에 확인하지 못했습니다.
- 캐시 모드를 켜면 기본으로 공유 폴더도 PC 로 내려받습니다. Exchange 공용 폴더와 SharePoint 폴더도 여기에 들어갑니다.
- 공유 폴더 내려받기를 켜 두면 공유 폴더 내용이 로컬 OST 에 들어갑니다. 그래서 OST 가 크게 불어날 수 있습니다.
- Outlook 2013 과 Exchange 2013·SharePoint 2013 을 함께 쓰는 환경에서는 사이트 사서함도 권한이 있으면 프로필에 저절로 붙습니다. 공유 폴더 내려받기가 켜져 있으면 사이트 사서함도 OST 로 동기화합니다.
- 새 Outlook for Windows 에는 캐시 모드가 없습니다([새 Outlook](../new-outlook.md)).

## 위치와 버전별 차이

### PST 와 OST 비교

| 구분 | PST | OST |
|---|---|---|
| 파일 구조 | PFF | PFF (같은 구조) |
| 헤더로 가리기 | 헤더의 `wMagicClient` 칸 값이 서로 다릅니다 | (값은 [데이터 파일 구조](pst-ost.md)에 있습니다) |
| 내용의 원본 | 파일 자체 | 서버 사서함 |
| 들어가는 범위 | 사용자가 넣은 항목, POP·IMAP 계정의 전체 정보, 자동 보관 항목 | 오프라인 기간 안의 메일(기본 12개월)과 설정에 따라 공유 폴더 |
| 크기 한도 | 같은 레지스트리 값을 따릅니다 | 같은 레지스트리 값을 따릅니다 |

- 파일 위치와 헤더 칸, 크기 한도 값은 [데이터 파일 구조 (PST·OST)](pst-ost.md)에서 다룹니다.
- 형식 버전 가운데 4KB 페이지 형식은 libpff 문서가 Outlook 2013 OST 에서 발견했다고 적은 형식입니다. OST 를 읽는 도구가 이 형식을 지원하는지 확인합니다.

### OST 가 크기 한도에 닿을 때

- OST 크기가 한도를 넘은 상태에서 받은편지함 동기화(Shift+F9)를 강제하면, Outlook 2013 은 오류를 내거나 가끔 멈출 수 있습니다.
- 캐시 모드 OST 가 한도에 닿으면 사서함 정리 마법사가 뜹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| OST 는 Outlook 이 서버 사서함의 사본을 둔 파일입니다 | 이 PC 에서 만든 OST 인지. 파일 시스템 기록과 프로필로 따로 확인합니다 |
| OST 안의 폴더와 메시지는 마지막으로 맞춘 무렵 사본에 있던 내용입니다 | OST 에 없는 메일이 서버에도 없다는 것. 오프라인 기간 밖의 메일은 처음부터 내려오지 않습니다 |
| | OST 안의 모든 폴더가 사용자 자신의 사서함이라는 것. 공유 폴더·공용 폴더·사이트 사서함 내용이 들어올 수 있습니다 |
| | 사용자가 그 메일을 이 PC 에서 읽었다는 것. 캐시 모드는 사서함 사본을 두는 기능이므로, OST 에 있다는 사실은 읽었다는 뜻이 아닙니다 |
| | 파일 종류만으로 계정 종류. IMAP 계정의 OST 사용을 확인하지 못했습니다 |

OST 가 사서함 크기에 비해 크게 불어나 있으면 공유 폴더 내려받기가 원인일 수 있습니다.

OST 에 서버 쪽 복구 가능한 항목 (Recoverable Items) 폴더가 동기화되지 않는다는 설명이 흔합니다. 이번에 연 자료로는 확인하지 못했습니다. 지운 메일을 찾을 때는 서버 쪽 자료를 따로 요청합니다([지운 메시지 복구 (Recoverable Items·Free Blocks)](recoverable-items-free-blocks.md)).

### 보고서 문장

아래 폴더 이름과 날짜는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 프로필의 OST 파일 안 받은편지함에 2024-05-02 부터 2025-04-30 까지의 메시지가 있습니다. OST 는 서버 사서함의 사본이므로 이 범위는 오프라인 기간 설정에 따라 정해졌을 수 있습니다."
- 쓰면 안 되는 문장: "사용자는 2024년 5월부터 이 계정을 썼고, 그 전의 메일은 지웠습니다."

## 시각 해석

- OST 안의 시각 값은 PST 와 같은 형식입니다([데이터 파일 구조](pst-ost.md)의 시각 해석).
- OST 에서 가장 오래된 메일의 날짜는 계정을 쓰기 시작한 날이 아닙니다. 기본 12개월 같은 오프라인 기간이 그 경계를 정할 수 있습니다.
- 캐시 모드는 서버와 자주 맞춥니다. 그래서 OST 파일의 NTFS 수정 시각은 동기화 때문에 계속 바뀔 수 있습니다. 이 시각을 사용자 행위 시각으로 읽지 않습니다.
- 공유 폴더 안의 메시지 시각은 사용자 자신의 송수신 시각이 아닐 수 있습니다. 먼저 어느 폴더에 들어 있는지 확인합니다.

## 함정과 한계

1. **OST 를 사용자가 만든 보관 파일로 봅니다.** OST 는 서버 사서함의 사본입니다. 사용자가 일부러 모은 자료로 해석하지 않습니다.
2. **OST 만 보고 사서함 전체를 봤다고 여깁니다.** 오프라인 기간 밖의 메일, 서버의 숨은 폴더는 OST 에 없을 수 있습니다. 사건에 필요하면 서버 쪽 자료를 따로 확보합니다.
3. **공유 폴더 내용을 본인 메일로 씁니다.** 공용 폴더·SharePoint 폴더·사이트 사서함은 다른 사람이 넣은 내용일 수 있습니다. 폴더 계층에서 어느 사서함에 속하는지 먼저 가립니다.
4. **OST 가 없으면 Exchange 를 쓰지 않았다고 단정합니다.** 캐시 모드를 끈 온라인 모드에서 OST 가 만들어지지 않는지는 이번에 확인하지 못했습니다. 새 Outlook 은 캐시 모드가 없습니다. 프로필 레지스트리와 다른 흔적으로 확인합니다.
5. **OST 는 만든 프로필에서만 열린다는 이유로 분석을 포기합니다.** OST 가 만든 프로필·계정에 묶여 다른 프로필에서 바로 열 수 없다는 설명이 흔합니다. 이번에 확인하지 못했습니다. libpff 문서는 OST 형식도 함께 다룹니다. Outlook 에 붙이지 않고 공개 파서로 파일을 직접 읽어 봅니다.
6. **한도에 닿은 무렵의 대량 삭제를 곧바로 증거 인멸로 봅니다.** 한도에 닿으면 사서함 정리 마법사가 뜹니다. 공간을 비우려는 정리였을 가능성도 함께 따져 봅니다([증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)).

## 직접 분석해 보기

### 원시 바이트로 한 번

아래는 libpff 문서의 칸 위치로 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D
000000  21 42 44 4E .. .. .. .. 53 4F 24 00 .. ..
```

1. 오프셋 0 의 `21 42 44 4E` 로 PFF 파일임을 확인합니다.
2. 오프셋 8 의 `53 4F` 는 "SO" 입니다. OST 입니다. PST 라면 이 자리가 "SM" 입니다.
3. 오프셋 10 의 `24 00` 은 36 입니다. 4KB 페이지 형식입니다.
4. 확장자가 `.pst` 인데 이 자리가 "SO" 라면, 이름을 바꾼 OST 입니다. 헤더 값이 확장자보다 앞섭니다.

헤더의 나머지 칸과 파이썬 코드는 [데이터 파일 구조 (PST·OST)](pst-ost.md)에 있습니다.

### 공개 도구로 한 번

libpff 같은 공개 파서로 OST 를 열고 다음을 확인합니다.

- 폴더 계층을 적어 보고, 사용자 자신의 사서함 폴더와 공유 폴더·공용 폴더를 나눕니다.
- 받은편지함·보낸 편지함에서 가장 오래된 메시지의 날짜를 적습니다. 오프라인 기간 설정과 맞는지 봅니다.
- 도구가 4KB 형식을 읽는지, 읽지 못한 블록을 알려 주는지 확인합니다.
- 같은 사용자 폴더에 PST 가 함께 있으면 자동 보관 PST 인지 봅니다. 두 파일의 메시지 기간이 이어지는지 비교합니다.

> 그림 자리: 서버 사서함, 캐시 모드 OST(오프라인 기간·공유 폴더 포함), 자동 보관 PST 세 상자를 그리고 메일이 어디로 흘러가는지 화살표로 보여 주는 그림

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [데이터 파일 구조 (PST·OST)](pst-ost.md) | 헤더의 파일 종류와 형식 버전 |
| [계정·프로필 레지스트리 (Outlook Profiles)](outlook-profiles.md) | 프로필에 어떤 계정이 있었는지 |
| [지운 메시지 복구 (Recoverable Items·Free Blocks)](recoverable-items-free-blocks.md) | 서버 쪽에만 남는 지운 항목 |
| [자동완성 목록 (NK2·Stream_Autocomplete)](nk2-stream-autocomplete.md) | 메일을 보낸 상대 목록 |
| [새 Outlook](../new-outlook.md) | 캐시 모드가 없는 새 Outlook 의 흔적 |
| [메일 헤더 분석](../../../03-techniques/analysis/email-header-analysis.md) | OST 안 메시지가 실제로 어느 경로로 오갔는지 |
| [마스터 파일 테이블](../../filesystem/mft.md) | OST 파일이 생기고 바뀐 시각 |

## 실습

**직접 만든 가상 머신에 클래식 Outlook 과 시험용 Exchange Online 계정을 준비해** 해 봅니다.

1. 오프라인 기간을 기본값으로 두고 OST 를 만든 뒤, 가장 오래된 메시지의 날짜를 적습니다. 기간을 바꾸면 날짜가 어떻게 달라집니까?
2. 공유 폴더 내려받기를 켰을 때와 껐을 때 OST 크기와 폴더 계층을 비교해 보십시오.
3. 캐시 모드를 끄고 Outlook 을 다시 열어 보십시오. 기존 OST 는 남습니까? 새 OST 가 생깁니까?
4. 같은 Outlook 에 IMAP 계정을 더해 보십시오. 데이터 파일은 PST 입니까, OST 입니까? 헤더의 `wMagicClient` 로 확인하십시오.
5. 서버에서 메일 하나를 영구 삭제한 뒤 동기화하고 OST 를 공개 파서로 열어 보십시오. 서버의 지운 항목이 OST 에 보입니까?

**공개 검체(NIST CFReDS 등)** 가운데 Outlook 데이터가 든 이미지에서도 해 봅니다.

1. OST 와 PST 가 각각 몇 개 있습니까? 헤더 값과 확장자가 모두 맞습니까?
2. OST 안에서 사용자 자신의 폴더가 아닌 폴더가 있습니까?

## 참고 문헌

- Microsoft 지원, "Turn on Cached Exchange Mode" — https://support.microsoft.com/en-us/office/turn-on-cached-exchange-mode-7885af08-9a60-4ec3-850a-e221c1ed0c1c
- Microsoft 지원, "Introduction to Outlook Data Files (.pst and .ost)" — https://support.microsoft.com/en-us/office/introduction-to-outlook-data-files-pst-and-ost-222eaf92-a995-45d9-bde2-f331f60e2790
- Microsoft Learn, "Configure Size Limit for PST and OST Files In Outlook" (옛 KB 832925, 2026-09-10) — https://learn.microsoft.com/en-us/microsoft-365-apps/outlook/data-files/configure-size-limit-outlook-data-files
- libyal libpff, "Personal Folder File (PFF) format" (문서 판 0.0.48, 2020-07) — https://raw.githubusercontent.com/libyal/libpff/main/documentation/Personal%20Folder%20File%20(PFF)%20format.asciidoc
