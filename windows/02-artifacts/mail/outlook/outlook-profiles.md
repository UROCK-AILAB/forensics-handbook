---
title: "계정·프로필 레지스트리"
parent: "아웃룩"
grand_parent: "아티팩트 · 메일"
nav_order: 1930
---

# 계정·프로필 레지스트리 (Outlook Profiles)

> 상위 허브: [아웃룩 (Outlook)](index.md)

## 한 줄 요약

클래식 Outlook 의 사용자 설정은 사용자 레지스트리의 `HKCU\Software\Microsoft\Office\<버전>\Outlook` 아래에 있습니다. `<버전>` 자리의 번호로 Outlook 판을 가늠할 수 있습니다. 계정과 데이터 파일을 묶는 프로필 (Profile) 키가 어디에 있는지는 공식 문서에 없습니다. 그래서 이 페이지는 공식 문서의 내용과 흔한 설명을 나눠 적고, 하이브에서 계정 정보를 직접 찾는 법을 중심으로 씁니다.

## 이 페이지 내용의 근거

| 내용 | 상태 |
|---|---|
| Office 버전 번호와 Outlook 판의 대응 (11.0~16.0) | Microsoft 문서 |
| `Outlook` 키 아래 `PST`·`AutoNameCheck` 하위 키 | Microsoft 문서 |
| 2016 이후 판도 `16.0` 을 쓴다 | 흔한 설명. Microsoft 문서에 간접 근거만 있습니다 |
| 프로필 키의 자리, 계정 하위 키, 값 이름과 형식 | 흔한 설명. 공식 문서 없음 |
| 계정 비밀번호가 보호돼 있다 | 흔한 설명. 공식 문서 없음 |
| 새 Outlook 이 이 프로필 키를 쓰지 않는다 | 흔한 설명. 공식 문서 없음 |
| 클래식 Outlook 이 없는 PC 의 키 상태 | Windows 11 25H2 기준 (아래 "클래식 Outlook 이 없는 PC") |

"흔한 설명" 은 보고서에 그대로 쓰지 않습니다. 조사하는 검체에서 직접 찾아 확인한 뒤 씁니다(아래 "직접 분석해 보기").

## 무엇을 기록하나 · 왜 생기나

### 공식 문서의 내용

Office 는 판마다 레지스트리 경로에 버전 번호를 넣습니다. 대응은 다음과 같습니다.

| 버전 번호 | Outlook 판 |
|---|---|
| `11.0` | Outlook 2003 |
| `12.0` | Outlook 2007 |
| `14.0` | Outlook 2010 |
| `15.0` | Outlook 2013 |
| `16.0` | Outlook 2016 |

2016 이후 판(2019·2021·Microsoft 365)도 `16.0` 을 같이 쓴다는 설명이 흔하지만, 이를 바로 적은 공식 문서는 없습니다. 간접 근거로, Microsoft 의 자동완성 목록 문서는 `Office\<16.0>\Outlook\AutoNameCheck` 키를 안내하면서 Outlook 2021 에 넣을 값을 예로 듭니다. 그래서 `16.0` 키만 보고 Outlook 2016 이라고 단정하지 않으며, 설치된 판은 [설치 프로그램](../../system-account/uninstall.md)에서 함께 확인합니다.

같은 `HKCU\Software\Microsoft\Office\<버전>\Outlook` 아래 하위 키 가운데 공식 문서에 나오는 것은 다음과 같습니다.

| 하위 키 | 담는 것 | 자세히 |
|---|---|---|
| `PST` | 데이터 파일 크기 한도 | [데이터 파일 구조 (PST·OST)](pst-ost.md) |
| `AutoNameCheck` | 자동완성 목록의 항목 수 한도 | [자동완성 목록 (NK2·Stream_Autocomplete)](nk2-stream-autocomplete.md) |

두 키의 값은 기본으로 없고, 값이 있으면 사용자나 관리자, 정책이 따로 넣은 것입니다. 크기 한도는 정책 키에도 들어갈 수 있으며 정책 키의 경로는 [데이터 파일 구조 (PST·OST)](pst-ost.md)에서 다룹니다.

`HKCU` 는 로그온한 사용자의 하이브라서, 검체에서는 사용자마다 NTUSER.DAT 를 따로 엽니다([레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)).

### 흔한 설명 (공식 문서 없음)

분석가 사이에 널리 퍼진 설명은 다음과 같습니다. 모두 공식 문서에는 없는 설명입니다.

프로필은 Outlook 이 계정과 데이터 파일을 묶어 부르는 단위이고, 사용자 레지스트리에 프로필마다 키가 하나 있습니다. 프로필 키 아래에는 계정마다 하위 키가 있고, 여기에 계정 이름·메일 주소·표시 이름·보내는 서버와 받는 서버 이름·사용자 이름 같은 값이 이진 값 (REG_BINARY) 안에 UTF-16 글자로 들어 있습니다. POP3·IMAP 계정의 비밀번호 값은 DPAPI 로 보호돼 있고, 프로필에는 연결된 PST·OST 의 경로도 들어 있습니다. 기본 프로필 이름을 가리키는 값이 따로 있으며, 새 Outlook 은 이 레지스트리 프로필을 쓰지 않습니다.

하위 키 이름과 값 이름도 흔히 알려져 있지만, 공식 문서가 없어 이 페이지에는 적지 않습니다. 검체에서 찾은 이름을 씁니다.

## 위치와 버전별 차이

### 흔히 알려진 프로필 키 (공식 문서 없음)

프로필 키는 Outlook 판에 따라 두 곳 가운데 하나에 있다는 설명이 흔합니다.

| Outlook | 흔히 알려진 자리 |
|---|---|
| 2013 이후 | `HKCU\Software\Microsoft\Office\<15.0 또는 16.0>\Outlook\Profiles\<프로필 이름>` |
| 2010 이전 | `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows Messaging Subsystem\Profiles\<프로필 이름>` |

판이 바뀌면 자리도 바뀐다는 설명이라서 두 자리를 모두 보고, 두 자리에 없으면 아래 방법으로 하이브 전체에서 찾습니다.

### 클래식 Outlook 이 없는 PC

새 Outlook 1.2026.707.300 만 깔린 Windows 11 25H2 에서는 위 표의 두 `Profiles` 키가 모두 없습니다. `HKCU\Software\Microsoft\Office\16.0\Outlook` 키는 있고, 그 아래에는 `Options` 키만 있습니다.

클래식 Outlook 을 쓰지 않은 PC 에도 `Office\16.0\Outlook` 키가 있을 수 있으므로, 이 키가 있다는 것만으로 클래식 Outlook 을 썼다고 보지 않습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| `Office\<번호>\Outlook` 키가 사용자 하이브에 있으면, 그 사용자 하이브에 Outlook 설정 키가 만들어졌습니다 | 그 판의 클래식 Outlook 을 썼다는 것. 클래식 Outlook 이 없는 PC 에도 `16.0\Outlook` 키가 있을 수 있습니다 |
| `PST`·`AutoNameCheck` 아래 값이 있으면 누군가 값을 따로 넣었습니다 | 누가 넣었는지. 사용자·관리자·정책 모두 넣을 수 있습니다 |
| 하이브에서 계정 이름·메일 주소가 든 키를 찾으면, 그 사용자 하이브에 그 계정 정보가 적혀 있었습니다 | 그 계정으로 메일을 주고받았다는 것 |
| 키 경로가 NTUSER.DAT 안에 있으므로 어느 사용자 계정의 설정인지 나뉩니다 | 계정을 언제 추가했는지. 키에는 마지막 기록 시각 하나만 있습니다 |
| | 새 Outlook·웹 메일로 쓴 계정. 이 키에 남는지는 공개 자료가 없습니다 |

### 보고서 문장

아래 사용자 이름·주소·경로는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 `kim` 의 NTUSER.DAT 에서 `kim@example.com` 을 UTF-16LE 로 찾았습니다. 이 글자는 `Software\Microsoft\Office\16.0\Outlook` 아래 하위 키의 값 안에 있습니다. 같은 키의 다른 값에는 `D:\Users\kim\Documents\Outlook Files\archive.pst` 경로가 있습니다."
- 쓰면 안 되는 문장: "김 씨는 Outlook 2016 에 kim@example.com 계정을 등록해 archive.pst 로 메일을 주고받았습니다."

## 시각 해석

레지스트리 키마다 마지막 기록 시각이 하나 있고 값은 UTC 기준입니다. 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다. 키 시각은 그 키가 마지막으로 바뀐 때라서 계정을 처음 추가한 때가 아닐 수 있고, 계정을 추가한 시각이 따로 값으로 남는지는 공개 자료가 없어 검체에서 확인합니다.

- 프로필 값에 적힌 데이터 파일의 NTFS 시각과 키 시각을 나란히 봅니다. 데이터 파일이 생긴 무렵과 설정이 바뀐 무렵을 따로 말할 수 있습니다([마스터 파일 테이블](../../filesystem/mft.md)).
- 현지 시각으로 옮길 때는 [시간대 설정](../../system-account/time-zone.md)을 봅니다.

## 함정과 한계

1. **`Office\16.0\Outlook` 키가 있으니 클래식 Outlook 을 썼다고 봅니다.** 클래식 Outlook 이 없는 PC 에도 이 키가 있을 수 있습니다. 프로필·데이터 파일·설치 기록을 함께 봅니다.
2. **`16.0` 을 Outlook 2016 으로 읽습니다.** 2016 이후 판도 같은 번호를 쓴다는 설명이 흔합니다. 설치 기록으로 판을 확인합니다.
3. **한 자리만 봅니다.** 프로필 키의 자리는 판에 따라 다르다는 설명이 흔합니다. 하이브 안의 모든 `Office\<번호>` 키와 `Windows Messaging Subsystem` 쪽을 모두 보고, 메일 주소로 전체를 한 번 더 찾습니다.
4. **프로필 키가 없으면 메일을 쓰지 않았다고 봅니다.** 새 Outlook 만 깔린 PC 에는 프로필 키가 없습니다. 웹 메일이나 다른 메일 프로그램을 썼을 수 있습니다. 지운 키가 하이브 안에 남았을 수도 있습니다([레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)).
5. **메일 주소를 ASCII 로만 찾습니다.** 값이 이진 값 안에 UTF-16 으로 들어 있다는 설명이 흔합니다. ASCII 와 UTF-16LE 둘 다 찾습니다([문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)).
6. **비밀번호를 평문으로 찾습니다.** 비밀번호 값은 DPAPI 로 보호돼 있다는 설명이 흔합니다. 보호된 값을 다루는 법은 [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md)를 봅니다.
7. **라이브 시스템에서 `HKCU` 만 봅니다.** `HKCU` 는 지금 로그온한 사용자의 하이브입니다. 다른 사용자의 설정은 그 사용자의 NTUSER.DAT 를 따로 열어야 보입니다([사용자 프로필 목록](../../system-account/profilelist.md)).

## 직접 분석해 보기

### 원시 바이트로 한 번

흔히 알려진 경로에 기대지 않고, 사건에서 알려진 메일 주소로 계정 키를 찾습니다. 아래 주소는 설명을 위해 만든 예입니다. 바이트는 글자를 ASCII 와 UTF-16LE 로 바꿔 계산한 값입니다.

| 찾을 글자 | ASCII | UTF-16LE |
|---|---|---|
| `kim@example.com` | `6B 69 6D 40 65 78 61 6D 70 6C 65 2E 63 6F 6D` | `6B 00 69 00 6D 00 40 00 65 00 78 00 61 00 6D 00 70 00 6C 00 65 00 2E 00 63 00 6F 00 6D 00` |
| `.pst` | `2E 70 73 74` | `2E 00 70 00 73 00 74 00` |
| `.ost` | `2E 6F 73 74` | `2E 00 6F 00 73 00 74 00` |

1. 사용자의 NTUSER.DAT 사본에서 메일 주소를 두 형식으로 찾습니다.
2. 찾은 자리가 어느 값의 데이터인지 확인합니다. 그 값이 붙은 키를 부모 쪽으로 따라 올라가 전체 경로를 적습니다. 하이브 안에서 키와 값을 따라가는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)를 봅니다.
3. 적은 경로가 위 "흔히 알려진 자리" 가운데 어디인지, 아니면 다른 자리인지 기록합니다.
4. 같은 키의 다른 값을 읽습니다. 서버 이름·사용자 이름·표시 이름이 있는지 봅니다. 값의 이름은 검체에 적힌 그대로 씁니다.
5. `.pst`·`.ost` 를 찾아 데이터 파일 경로가 든 값을 찾습니다. 경로에 실제로 파일이 있는지 디스크에서 확인합니다.
6. 이 방법으로 찾은 자리는 하이브 본문에 살아 있는 키일 수도, 지운 키일 수도 있습니다. 찾은 자리가 지운 공간인지 확인합니다.

아래 파이썬 코드는 파일 하나에서 글자를 두 형식으로 찾아 위치를 적습니다.

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

사용 예: `python find.py NTUSER.DAT kim@example.com .pst .ost`

- 이 코드는 대소문자를 가립니다. 메일 주소는 검체에 적힌 대소문자와 다를 수 있으므로, 찾지 못하면 대소문자를 바꿔 다시 찾습니다.
- 위치만 알려 줍니다. 그 위치가 어느 키인지는 2번처럼 하이브 구조를 따라가 확인합니다.

> 그림 자리: NTUSER.DAT 에서 메일 주소를 찾은 자리 → 그 값이 붙은 키 → 부모 키로 올라가며 전체 경로를 얻는 흐름. 같은 키의 다른 값(서버·데이터 파일 경로)을 옆에 적은 그림

### 공개 도구로 한 번

- 오프라인 하이브를 읽는 공개 레지스트리 도구로 NTUSER.DAT 를 엽니다.
- `Software\Microsoft\Office` 아래의 버전 번호 키를 모두 적습니다.
- 흔히 알려진 두 `Profiles` 자리를 엽니다. 이진 값을 UTF-16 글자로 풀어 보여 주는지 확인합니다.
- Outlook 프로필을 따로 풀어 주는 도구나 플러그인을 쓰면, 그 도구가 어느 경로를 보는지 확인합니다. 검체의 Outlook 판과 맞지 않는 경로만 보면 결과가 비어 나올 수 있습니다.
- 지운 키와 값도 보여 주는지 확인합니다.
- 도구가 보여 준 계정 수와 위 원시 바이트 검색 결과를 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [데이터 파일 구조 (PST·OST)](pst-ost.md) | 프로필 값의 데이터 파일 경로에 실제 파일이 있는지. 크기 한도 값 |
| [PST와 OST 차이 (Cached Mode·Exchange)](cached-mode-exchange.md) | 계정 종류와 데이터 파일 종류가 맞는지 |
| [자동완성 목록 (NK2·Stream_Autocomplete)](nk2-stream-autocomplete.md) | `.nk2` 파일 이름과 프로필 이름 |
| [설치 프로그램](../../system-account/uninstall.md) | 설치된 Outlook 판과 레지스트리의 버전 번호 |
| [스토어 앱 설치 목록](../../system-account/appx-staterepository.md) · [새 Outlook](../new-outlook.md) | 새 Outlook 앱이 깔려 있었는지 |
| [사용자 프로필 목록](../../system-account/profilelist.md) | NTUSER.DAT 가 어느 사용자 계정의 것인지 |
| [자격 증명 관리자와 볼트](../../credentials/credential-manager-windows-vault.md) · [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) | 메일 계정의 비밀번호가 어디에 어떻게 보호돼 있는지 |
| [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 예전 시점의 NTUSER.DAT. 계정 키가 언제 생기고 사라졌는지 |

계정 정보를 다른 연락 기록과 합쳐 읽는 순서는 [누구와 연락을 주고받았나](../../../04-scenarios/activity/communication-reconstruction.md)에서 다룹니다.

## 실습

**직접 만든 가상 머신에서** 해 봅니다. 이 페이지의 흔한 설명을 확인하는 실습입니다.

1. 클래식 Outlook 을 깔기 전과 깐 뒤, 첫 실행 뒤에 NTUSER.DAT 의 `Software\Microsoft\Office` 아래를 비교해 보십시오. 어느 단계에서 어떤 키가 생깁니까?
2. POP3 계정과 IMAP 계정을 하나씩 더합니다. 위 코드로 메일 주소를 찾아보십시오. 주소는 어느 키에 있습니까? 위 "흔히 알려진 자리" 와 맞습니까?
3. 2번에서 찾은 값은 이진 값입니까, 문자열입니까? 글자는 어떤 형식으로 들어 있습니까?
4. 프로필을 하나 더 만들고 기본 프로필을 바꿔 보십시오. 어느 키의 어느 값이 바뀝니까?
5. 계정 하나를 지운 뒤 하이브를 다시 보십시오. 키가 사라졌습니까? 하이브 안에 지운 키의 흔적이 남았습니까?
6. 새 Outlook 만 깐 가상 머신에서 같은 계정을 더해 보십시오. 레지스트리에 프로필 키가 생깁니까?

**공개 검체(NIST CFReDS 등)** 가운데 클래식 Outlook 을 쓴 이미지에서도 해 봅니다.

1. 사용자마다 `Software\Microsoft\Office` 아래에 버전 번호 키가 몇 개 있습니까?
2. 메일 주소가 든 키의 전체 경로는 무엇입니까?
3. 그 키에 적힌 데이터 파일 경로에 실제로 파일이 있습니까? 없다면 어떤 설명이 가능합니까?

## 참고 문헌

- Microsoft Learn, "Configure Size Limit for PST and OST Files In Outlook" (옛 KB 832925, 2026-09-10) — https://learn.microsoft.com/en-us/microsoft-365-apps/outlook/data-files/configure-size-limit-outlook-data-files
- Microsoft Learn, "The Outlook AutoComplete list" (옛 KB 2199226, 2025-06-24) — https://learn.microsoft.com/en-us/microsoft-365-apps/outlook/contacts/outlook-autocomplete-list
