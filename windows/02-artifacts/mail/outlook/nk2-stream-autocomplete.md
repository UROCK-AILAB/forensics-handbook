---
title: "자동완성 목록"
parent: "아웃룩"
grand_parent: "아티팩트 · 메일"
nav_order: 1920
---

# 자동완성 목록 (NK2·Stream_Autocomplete)

> 상위 허브: [아웃룩 (Outlook)](index.md)

클래식 Outlook 은 메일을 보낸 상대의 주소와 표시 이름을 자동완성 목록 (AutoComplete list) 에 모읍니다. Outlook 2007 까지는 이 목록을 `.nk2` 파일에 두었습니다. Outlook 2010 부터는 기본 메시지 저장소 안의 숨은 메시지에 둡니다. 목록은 사용자가 누구에게 메일을 보냈는지 추정하는 단서입니다. 다만 목록만으로 언제 보냈는지는 알 수 없습니다.

## 무엇을 기록하나 · 왜 생기나

이 목록은 닉네임 캐시 (nickname cache) 라고도 부릅니다. 사용자가 Outlook 에서 메일을 보내면 목록이 저절로 만들어지고, 받는 사람 칸에 글자를 칠 때 후보를 띄우는 데 씁니다.

목록에는 이전에 메일을 보낸 상대마다 다음 값이 들어 있습니다.

- SMTP 주소
- LegacyExchangeDN
- 표시 이름

Outlook 의 목록은 웹 Outlook (Outlook on the web) 과 함께 쓰지 않고 웹 Outlook 에는 목록이 따로 있어서, PC 의 목록만 보고 사용자가 메일을 보낸 상대를 모두 알 수는 없습니다.

## 위치와 버전별 차이

### 판에 따른 저장 위치

| Outlook | 저장 위치 |
|---|---|
| 2007 이전 | 디스크의 닉네임 파일 (`.nk2`). 폴더는 `%APPDATA%\Microsoft\Outlook` 입니다 |
| 2010 이후 | 기본 메시지 저장소 안의 숨은 메시지. 메시지 클래스는 `IPM.Configuration.Autocomplete` 입니다 |

Outlook 2010 이후는 옛 `.nk2` 를 가져올 수 있고, 가져오는 명령은 `outlook /importnk2` 입니다. `.nk2` 를 다른 PC 로 옮길 때는 파일 이름을 프로필 이름과 맞춰야 합니다. 프로필은 [계정·프로필 레지스트리 (Outlook Profiles)](outlook-profiles.md)에서 다룹니다.

기본 메시지 저장소는 계정에 따라 PST 이거나 OST 입니다. 어느 쪽인지는 [PST와 OST 차이 (Cached Mode·Exchange)](cached-mode-exchange.md)에서 다룹니다.

### 판 기준과 계정 기준

위 표는 Microsoft Learn 문서가 Outlook 판으로 나눈 설명입니다. 목록을 다른 PC 로 옮기는 Microsoft 지원 문서는 계정 종류로 나눕니다.

- POP3 계정: PC 에 있는 파일. 폴더는 `%APPDATA%\Microsoft\Outlook` 입니다
- Microsoft 365·Exchange·IMAP 계정: Outlook 데이터 파일 안의 숨은 메시지

두 설명은 기준이 다른데 두 문서 모두 이 차이를 풀어 설명하지 않습니다. 그래서 분석 대상에서는 판과 계정 종류에 상관없이 두 곳을 모두 찾습니다.

### 항목 수 한도

Outlook for Microsoft 365·2019·2016 은 모두 항목을 1,000개까지 두고, 한도를 넘으면 Outlook 이 사용 빈도로 무게를 매겨 지울 이름을 고릅니다. 한도는 `HKCU\Software\Microsoft\Office\16.0\Outlook\AutoNameCheck` 의 `MaxNickNames` 값으로 바꿉니다. 값 형식은 REG_DWORD 이고, 10진수로 넣습니다. 이 값이 있으면 한도를 기본값과 다르게 정한 것입니다.

`16.0` 같은 Office 버전 번호와 Outlook 판의 대응은 [계정·프로필 레지스트리 (Outlook Profiles)](outlook-profiles.md)에서 다룹니다.

### 받는 사람 칸 후보가 바뀐 판

Outlook for Microsoft 365 버전 2202(빌드 14931.20604)부터 달라진 점이 있습니다. Exchange Online 사서함에 연결돼 있으면 받는 사람 칸 후보는 Microsoft Search 가 띄웁니다. 이 판 이후에는 화면에 뜬 후보가 로컬 자동완성 목록에서 나왔다고 단정하지 않습니다.

## 구조

### 숨은 메시지

2010 이후의 목록은 메시지 저장소 안의 메시지 하나이고, 이 메시지는 화면의 폴더 목록에 보이지 않습니다. 메시지 클래스 `IPM.Configuration.Autocomplete` 로 이 메시지를 가려냅니다. 이 메시지는 MFCMAPI 로 볼 수 있고, 연관 콘텐츠 표 (Associated Content Table) 에 있습니다. 어느 폴더의 표인지는 공식 문서에 없습니다.

데이터 파일 안에서 메시지를 찾아가는 구조는 [데이터 파일 구조 (PST·OST)](pst-ost.md)에서 다룹니다. 메시지의 값은 [MAPI 속성](../../../01-foundations/app-mail-data/mapi-property.md)으로 들어 있습니다.

### 흔히 알려진 내용

아래 내용은 공개 분석 자료에 널리 퍼져 있고 Microsoft 의 [MS-OXOCFG] 명세에 있다고 알려져 있지만, Microsoft Learn 의 [MS-OXOCFG] 목차에는 자동완성을 다루는 절이 없습니다. 실제 데이터로 직접 확인한 뒤 씁니다.

| 대상 | 흔한 설명 |
|---|---|
| 로컬 사본 파일 | `%LOCALAPPDATA%\Microsoft\Outlook\RoamCache\Stream_Autocomplete_0_<GUID>.dat` |
| 숨은 메시지가 든 폴더 | 받은편지함 (연관 콘텐츠 표라는 점은 위 "숨은 메시지" 절에 있습니다) |
| 목록 데이터가 든 속성 | `PidTagRoamingBinary` |
| 목록 데이터와 `.nk2` 의 바이너리 형식 | 시작 값 `0xBAADF00D`, 주 버전 `0x0C`, 행 수, 행마다 속성 목록 |

이 페이지 제목의 "Stream_Autocomplete" 는 위 로컬 사본 파일 이름에서 온 말입니다. 목록 항목에 마지막 사용 시각이나 사용 횟수 같은 필드가 있는지는 실제 데이터로 확인합니다.

클래식 Outlook 이 없는 PC 에는 `%LOCALAPPDATA%\Microsoft\Outlook\RoamCache` 폴더가 없습니다(Windows 11 25H2 기준).

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 목록에 있는 주소와 표시 이름이 어느 때인가 이 프로필의 목록에 들어갔습니다 | 언제 들어갔는지. 항목에 시각 필드가 있는지는 공개 문서에 나와 있지 않습니다 |
| 목록은 메일을 보낼 때 생깁니다. 그래서 목록의 상대는 메일을 보낸 적이 있는 상대일 수 있습니다 | 이 PC 에서 보냈다는 것. `.nk2` 를 가져오면 다른 PC 에서 만든 목록이 들어옵니다 |
| `MaxNickNames` 값이 있으면 한도를 기본값과 다르게 정했습니다 | 목록에 없는 상대에게는 메일을 보내지 않았다는 것. 사용자가 항목을 지우거나 목록을 비울 수 있고, 한도를 넘으면 Outlook 이 항목을 지웁니다 |
| | 메일 내용, 보낸 횟수, 답장했는지 |
| | 웹 Outlook 에서 보낸 상대. 웹 Outlook 의 목록은 따로 있습니다 |

### 보고서 문장

아래 사용자 이름·주소·표시 이름은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 `kim` 의 OST 안에서 메시지 클래스가 `IPM.Configuration.Autocomplete` 인 숨은 메시지를 찾았습니다. 이 메시지의 자동완성 항목에 `lee@example.com`(표시 이름 `이 과장`)이 있습니다. Microsoft 문서는 이 목록이 Outlook 에서 메일을 보낼 때 만들어진다고 적습니다."
- 쓰면 안 되는 문장: "김 씨는 이 PC 에서 이 과장에게 메일을 보냈습니다."
- 쓰면 안 되는 문장: "목록에 없으므로 김 씨는 박 씨에게 메일을 보내지 않았습니다."

앞 문장에 "메일을 보냈다" 를 더하려면, 보낸 편지함이나 서버 기록에서 그 상대에게 간 메시지를 찾아 함께 적습니다.

## 시각 해석

목록 항목에 시각 필드가 있는지는 공개 문서에 나와 있지 않습니다. 공개 도구가 항목마다 시각을 보여 주면, 그 값이 어느 필드에서 왔는지 도구 문서로 확인합니다. 숨은 메시지의 시각 속성이 언제 바뀌는지는 아래 실습에서 메일을 보내기 전과 뒤를 비교해 봅니다.

- `.nk2` 파일의 NTFS 시각은 파일이 생기고 바뀐 시각입니다. 항목 하나가 들어간 시각이 아닙니다([마스터 파일 테이블](../../filesystem/mft.md)).
- `AutoNameCheck` 키의 마지막 기록 시각은 그 키의 값이 마지막으로 바뀐 때입니다. `MaxNickNames` 를 넣은 무렵을 좁힐 때 씁니다. 키 시각은 UTC 기준입니다. 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)를 봅니다.
- 현지 시각으로 옮길 때는 [시간대 설정](../../system-account/time-zone.md)을 봅니다.

## 함정과 한계

1. **`.nk2` 파일만 찾습니다.** Outlook 2010 이후는 목록을 데이터 파일 안의 숨은 메시지에 둡니다. 화면에 보이는 폴더만 풀어내는 도구는 이 메시지를 빠뜨릴 수 있습니다. 도구가 숨은 메시지까지 풀어내는지 먼저 확인합니다.
2. **판 기준과 계정 기준 가운데 하나만 믿습니다.** 두 Microsoft 문서의 설명은 기준이 다릅니다. `.nk2` 파일과 숨은 메시지를 둘 다 찾습니다.
3. **목록에 없으면 보낸 적이 없다고 봅니다.** 사용자는 항목을 X 로 지울 수 있습니다. 옵션 > 메일 > "자동 완성 목록 비우기" 나 `Outlook.exe /CleanAutoCompleteCache` 로 목록을 통째로 비울 수도 있습니다. 1,000개 한도를 넘으면 Outlook 이 항목을 지웁니다.
4. **지웠다는 진술과 목록이 어긋나면 진술을 거짓으로 봅니다.** X 로 지운 항목도 그 상대에게 다시 메일을 보내면 목록에 되살아납니다. X 는 자동완성 후보에서만 빼므로, 검색 상자 같은 다른 곳에는 그 이름이 계속 뜰 수 있습니다. 지운 뒤에 다시 보냈는지부터 확인합니다.
5. **새 판에서 받는 사람 칸 후보를 이 목록으로 설명합니다.** 버전 2202 이후 Exchange Online 사서함에서는 후보를 Microsoft Search 가 띄웁니다. "화면에 후보가 떴다" 는 진술을 로컬 목록과 바로 잇지 않습니다.
6. **인코딩된 데이터 파일에서 글자를 그대로 찾습니다.** 헤더의 `bCryptMethod` 가 `0x01`·`0x02` 이면 블록 바이트가 원래 글자와 다릅니다. 파서로 먼저 풀어낸 결과를 검색합니다([데이터 파일 구조 (PST·OST)](pst-ost.md)).
7. **흔히 알려진 경로와 형식을 그대로 보고서에 씁니다.** 위 "흔히 알려진 내용" 표는 공식 문서에 없는 설명입니다. 실제 데이터의 경로·값과 다르면 실제 데이터를 따릅니다.

## 직접 분석해 보기

### 원시 바이트로 한 번

찾을 글자를 ASCII 와 UTF-16LE 바이트로 바꿔 계산한 값입니다.

| 찾을 글자 | ASCII | UTF-16LE |
|---|---|---|
| `IPM.Configuration.Autocomplete` | `49 50 4D 2E 43 6F 6E 66 69 67 75 72 61 74 69 6F 6E 2E 41 75 74 6F 63 6F 6D 70 6C 65 74 65` | `49 00 50 00 4D 00 2E 00 43 00 6F 00 6E 00 66 00 69 00 67 00 75 00 72 00 61 00 74 00 69 00 6F 00 6E 00 2E 00 41 00 75 00 74 00 6F 00 63 00 6F 00 6D 00 70 00 6C 00 65 00 74 00 65 00` |
| `MaxNickNames` | `4D 61 78 4E 69 63 6B 4E 61 6D 65 73` | `4D 00 61 00 78 00 4E 00 69 00 63 00 6B 00 4E 00 61 00 6D 00 65 00 73 00` |

데이터 파일에서 숨은 메시지를 찾습니다.

1. PST·OST 헤더의 `bCryptMethod` 를 읽습니다. 읽는 법은 [데이터 파일 구조 (PST·OST)](pst-ost.md)에 있습니다.
2. 값이 `0x00` 이면 원시 바이트에서 메시지 클래스를 찾을 수 있습니다. `0x01`·`0x02` 이면 원시 바이트 검색으로는 찾지 못할 수 있습니다. 이때는 공개 도구 단계로 넘어갑니다.
3. 파일 형식에 따라 글자를 한 바이트로 적을 수도, 두 바이트로 적을 수도 있습니다. 그래서 ASCII 와 UTF-16LE 둘 다 찾습니다.
4. 찾은 자리는 메시지가 있다는 표시일 뿐입니다. 어느 폴더의 어느 메시지인지는 파서로 확인합니다.

레지스트리에서 한도 값을 찾습니다.

1. 사용자의 NTUSER.DAT 에서 `MaxNickNames` 를 찾습니다. 하이브가 값 이름을 어떤 글자 형식으로 적는지는 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)를 봅니다. 여기서는 두 형식을 다 찾습니다.
2. 찾은 값이 `AutoNameCheck` 키에 붙어 있는지 확인합니다.
3. 값 데이터 4바이트를 낮은 바이트가 앞에 오는 순서(리틀 엔디언)로 읽습니다. 예를 들어 `D0 07 00 00` 이면 `0x7D0` = 2,000개입니다. 이 바이트는 설명을 위해 만든 예입니다.
4. 값이 없으면 이 키로는 한도를 바꾸지 않은 것입니다.

아래 파이썬 코드는 파일 하나에서 글자를 두 형식으로 찾아 위치를 적습니다. 파일을 메모리에 통째로 올리지 않으므로 큰 PST 에도 쓸 수 있습니다.

```python
import mmap, sys

path, words = sys.argv[1], sys.argv[2:]
with open(path, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    for w in words:
        for enc in ("ascii", "utf-16-le"):
            b = w.encode(enc)
            pos = m.find(b)
            while pos != -1:
                print(w, enc, hex(pos))
                pos = m.find(b, pos + 1)
```

사용 예: `python find.py archive.pst IPM.Configuration.Autocomplete`

이 코드는 대소문자를 구분하므로 글자를 한 자라도 다르게 넣으면 찾지 못합니다. 원본이 아니라 수집한 사본에서 돌립니다.

> 그림 자리: 2007 이전(`%APPDATA%\Microsoft\Outlook` 의 `.nk2` 파일)과 2010 이후(데이터 파일 안 숨은 메시지 `IPM.Configuration.Autocomplete`)를 나란히 놓고, 각 항목에 SMTP 주소·LegacyExchangeDN·표시 이름이 든다는 것을 보여 주는 그림

### 공개 도구로 한 번

- 숨은 메시지는 MFCMAPI 로 볼 수 있습니다. 분석용 가상 머신에서 데이터 파일의 사본으로 엽니다. 원본 데이터 파일은 Outlook 에 붙이지 않습니다.
- PST·OST 파서(예: libpff 의 pffexport)로 데이터 파일을 풀어낼 때는 숨은 메시지까지 내보내는지 확인합니다.
- 오프라인 하이브를 읽는 공개 레지스트리 도구로 NTUSER.DAT 의 `AutoNameCheck` 키를 엽니다.
- 목록을 풀어 주는 도구를 쓰면, 도구가 보여 준 주소 수와 위 원시 바이트 검색 결과를 맞춰 봅니다. 도구 두 개의 결과를 비교하는 법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [데이터 파일 구조 (PST·OST)](pst-ost.md) | 목록의 상대에게 간 메시지가 보낸 편지함에 있는지 |
| [PST와 OST 차이 (Cached Mode·Exchange)](cached-mode-exchange.md) | 기본 메시지 저장소가 PST 인지 OST 인지 |
| [지운 메시지 복구 (Recoverable Items·Free Blocks)](recoverable-items-free-blocks.md) | 보낸 편지함에 없는 상대라면 지운 메시지가 남았는지 |
| [계정·프로필 레지스트리 (Outlook Profiles)](outlook-profiles.md) | `.nk2` 파일 이름과 프로필 이름. Outlook 판 |
| [개별 메시지 파일 (MSG)](msg.md) | 따로 저장한 메시지의 수신자와 목록의 상대 |
| [마스터 파일 테이블](../../filesystem/mft.md) · [USN 변경 저널](../../filesystem/usnjrnl.md) | `.nk2` 파일이 생기고, 바뀌고, 지워진 기록 |
| [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 예전 시점의 `.nk2`·데이터 파일. 지금 목록과 항목을 비교합니다 |
| [새 Outlook](../new-outlook.md) | 사용자가 새 Outlook 으로 옮겨 갔는지 |

메일 기록을 다른 연락 기록과 합쳐 읽는 순서는 [누구와 연락을 주고받았나](../../../04-scenarios/activity/communication-reconstruction.md)에서 다룹니다.

## 실습

**직접 만든 가상 머신에 클래식 Outlook 을 깔고** 해 봅니다.

1. 처음 쓰는 주소로 메일을 한 통 보냅니다. MFCMAPI 로 숨은 메시지를 열어 그 주소가 들어갔는지 확인해 보십시오. 보내기 전과 뒤에 숨은 메시지의 어느 속성이 바뀌었습니까?
2. `%LOCALAPPDATA%\Microsoft\Outlook\RoamCache` 폴더에 `Stream_Autocomplete_` 로 시작하는 파일이 생겼습니까? 파일 맨 앞 4바이트는 위 "흔히 알려진 내용" 의 시작 값과 맞습니까?
3. 항목 하나를 X 로 지우고 같은 주소로 다시 보내 보십시오. 항목이 되살아납니까?
4. `Outlook.exe /CleanAutoCompleteCache` 로 목록을 비운 뒤 숨은 메시지와 2번 파일은 어떻게 됐습니까?
5. `MaxNickNames` 값을 넣기 전과 뒤에 `AutoNameCheck` 키의 마지막 기록 시각을 비교해 보십시오.
6. POP3 계정 프로필과 IMAP 계정 프로필을 따로 만들고 각각 메일을 보내 보십시오. 목록은 `.nk2` 파일과 숨은 메시지 가운데 어디에 생깁니까? 결과가 위 두 문서의 설명 가운데 어느 쪽과 맞습니까?

**공개 시험 데이터(NIST CFReDS 등)** 가운데 클래식 Outlook 을 쓴 이미지에서도 해 봅니다.

1. 디스크 전체에 `.nk2` 파일이 있습니까? 파일 이름은 무엇입니까?
2. PST·OST 안에 메시지 클래스가 `IPM.Configuration.Autocomplete` 인 메시지가 있습니까?
3. 목록의 주소 가운데 보낸 편지함에서 찾지 못하는 주소가 있습니까? 있다면 어떤 설명이 가능합니까?

## 참고 문헌

- Microsoft Learn, "The Outlook AutoComplete list" (옛 KB 2199226, 2025-06-24) — https://learn.microsoft.com/en-us/microsoft-365-apps/outlook/contacts/outlook-autocomplete-list (옛 주소: https://learn.microsoft.com/en-us/outlook/troubleshoot/contacts/information-about-the-outlook-autocomplete-list)
- Microsoft 지원, "Import or copy the Auto-Complete List to another computer" — https://support.microsoft.com/office/import-or-copy-the-auto-complete-list-to-another-computer-83558574-20dc-4c94-a531-25a42ec8e8f0
