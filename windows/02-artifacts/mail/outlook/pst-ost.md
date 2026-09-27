---
title: "데이터 파일 구조"
parent: "아웃룩"
grand_parent: "아티팩트 · 메일"
nav_order: 1870
---

# 데이터 파일 구조 (PST·OST)

클래식 Outlook 은 메일·연락처·일정 같은 항목을 PST·OST 데이터 파일에 저장하며, 두 파일은 같은 PFF (Personal Folder File) 구조를 씁니다. 파일 맨 앞의 헤더에는 파일 종류, 형식 버전, 인코딩 방식, 파일 크기가 적혀 있어서, 도구로 메시지를 뽑기 전에 헤더부터 확인하면 도구가 파일을 제대로 읽었는지 가릴 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

PFF 구조를 쓰는 파일은 세 종류입니다.

| 종류 | 이름 | 담는 것 |
|---|---|---|
| PST | 개인 폴더 (Personal Folders) | 메일·연락처·일정·작업·메모·업무일지 같은 Outlook 항목 |
| OST | 오프라인 폴더 (Offline Folders) | 서버 사서함의 로컬 사본 |
| PAB | 개인 주소록 (Personal Address Book) | 주소록 |

POP·IMAP 계정은 모든 Outlook 정보를 PST 에 담습니다. Exchange 계정이라도 자동 보관 (AutoArchive) 을 쓰면 PST 가 생길 수 있습니다.

OST 가 언제 생기고 무엇이 들어가는지는 [PST와 OST 차이 (Cached Mode·Exchange)](cached-mode-exchange.md)에서 다루고, 이 페이지는 두 파일이 함께 쓰는 구조만 다룹니다.

파일 안에는 화면에 보이는 폴더 말고도 숨은 메시지가 들어 있을 수 있습니다. 자동완성 목록이 한 예입니다([자동완성 목록 (NK2·Stream_Autocomplete)](nk2-stream-autocomplete.md)).

## 위치와 버전별 차이

### 기본 위치

새 PST 의 기본 위치는 다음과 같습니다(Windows 10 기준).

| Outlook | 새 PST 기본 위치 |
|---|---|
| 2016 이후 | `드라이브:\Users\<사용자>\Documents\Outlook Files\archive.pst` |
| 그보다 앞선 판 | `드라이브:\Users\<사용자>\AppData\Local\Microsoft\Outlook\archive.pst` |

- 이 위치는 새 파일을 만들 때의 기본값이라서, 분석 대상에서는 확장자와 헤더 시그니처로 디스크 전체를 찾습니다.
- OST 는 `%LOCALAPPDATA%\Microsoft\Outlook\` 에 있다는 설명이 흔합니다. 공식 문서에는 OST 경로가 없어 실제 데이터로 확인합니다.
- 클래식 Outlook 이 깔려 있지 않은 PC 에는 `%LOCALAPPDATA%\Microsoft\Outlook` 폴더 자체가 없을 수 있습니다(Windows 11 25H2, 새 Outlook 만 설치된 경우).

### 형식 버전

헤더의 `wVer` 필드로 형식을 알 수 있습니다.

| wVer | 형식 | 비고 |
|---|---|---|
| 14·15 | 32비트 ANSI | |
| 23 이상 | 64비트 유니코드 | 명세는 23 이상을 유니코드로 적습니다. libpff 문서는 21·23 을 64비트 유니코드로 적습니다 |
| 36 | 64비트 유니코드 + 4KB 페이지 | Outlook 2013 OST 에서 발견된 형식입니다 |
| 37 | WIP 를 지원하는 Outlook 이 쓴 파일 | 데이터가 Windows 정보 보호 (Windows Information Protection, WIP) 로 보호됐을 수 있습니다 |

Outlook 2003·2007·2010·2013·2016 은 ANSI·유니코드 두 형식을 모두 지원합니다. Windows 버전보다 Outlook 버전과 파일을 만들 때 고른 형식이 더 중요합니다.

### 크기 한도 (레지스트리)

Outlook 은 데이터 파일의 크기 한도를 레지스트리 값으로 정합니다. 이 설정은 PST·OST 둘 다에 적용됩니다.

| 값 이름 | 형식 | 단위 | 적용 대상 |
|---|---|---|---|
| `MaxLargeFileSize`·`WarnLargeFileSize` | REG_DWORD | MB | 유니코드 파일 |
| `MaxFileSize`·`WarnFileSize` | REG_DWORD | 바이트 | ANSI 파일 |

기본값은 다음과 같습니다.

| Outlook | 최대 | 경고 |
|---|---|---|
| 2010·2013·2016 (유니코드) | `0xC800` = 51,200MB (50GB) | `0xBE00` = 48,640MB (47.5GB) |
| 2003·2007 (유니코드) | `0x5000` = 20,480MB (20GB) | `0x4C00` = 19,456MB (19GB) |
| ANSI | `0x7BB04400` = 2,075,149,312바이트 (1.933GB) | `0x74404400` = 1,950,368,768바이트 (1.816GB) |

- 사용자 설정은 `HKCU\Software\Microsoft\Office\<버전>\Outlook\PST` 에 둡니다.
- 정책은 `HKCU\Software\Policies\Microsoft\Office\<버전>\Outlook\PST` 에 둡니다.
- `<버전>` 자리에는 Office 버전 번호(16.0 등)가 들어갑니다. 번호와 제품 이름의 대응은 [계정·프로필 레지스트리 (Outlook Profiles)](outlook-profiles.md)에서 다룹니다.
- 이 값들은 기본으로는 없고 필요할 때 만들어 넣는 값이라서, 값이 있으면 사용자나 관리자, 정책이 따로 넣은 것입니다.
- ANSI 파일은 `MaxFileSize` 를 크게 줘도 2GB 로 묶입니다. 파일 손상을 막으려는 제한입니다.

레지스트리 값을 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

## 구조

### 세 층

PFF 파일은 세 층으로 되어 있습니다.

| 층 | 하는 일 |
|---|---|
| NDB (노드 데이터베이스) 층 | 맨 아래 층입니다. 블록과 항목을 찾아가는 B-트리 두 개가 있습니다 |
| LTP 층 | NDB 위에서 표와 속성을 만듭니다 |
| 메시지 층 | 맨 위 층입니다. 폴더·메시지·첨부 같은 Outlook 항목을 나타냅니다 |

NDB 층의 B-트리 두 개는 다음과 같습니다.

- 오프셋 색인 (BBT): 블록이 파일의 어느 위치에 있는지 찾습니다.
- 설명자 색인 (NBT): 항목의 계층을 찾습니다.

메시지와 폴더의 값은 MAPI 속성으로 들어 있습니다. 속성 번호와 값 형식은 [MAPI 속성](../../../01-foundations/app-mail-data/mapi-property.md)에서 다룹니다.

### 헤더

헤더는 파일 맨 앞(오프셋 0)에 있습니다. MS-PST 명세의 필드 크기를 더하면 헤더 전체는 32비트(ANSI) 형식이 512바이트, 64비트(유니코드) 형식이 564바이트입니다. libpff 문서는 488·540바이트로 적는데, 앞부분 24바이트(시그니처부터 `dwReserved2` 까지)를 뺀 크기와 같습니다.

| 필드 | 오프셋 (10진) | 값 |
|---|---|---|
| 시그니처 | 0 (4바이트) | `21 42 44 4E` ("!BDN") |
| `wMagicClient` | 8 (2바이트) | PST `53 4D` ("SM"), OST `53 4F` ("SO"), PAB `41 42` ("AB") |
| `wVer` | 10 (2바이트) | 형식 버전. 위 표를 봅니다 |
| `wVerClient` | 12 (2바이트) | 명세가 다루는 값은 19 입니다 |
| `bPlatformCreate`·`bPlatformAccess` | — | 둘 다 `0x01` |
| `dwUnique` | — | 헤더를 고칠 때마다 1씩 늘어나는 값 |
| `rgnid` | — | NID 종류별로 마지막에 쓴 번호 |
| `rgbFM`·`rgbFP` | — | 각 128바이트. 더는 쓰지 않고 `0xFF` 로 채웁니다 |
| ROOT | 아래 표 | 파일 크기와 두 B-트리의 위치 |
| `bSentinel` | ANSI 460 / 유니코드 512 | `0x80` |
| `bCryptMethod` | ANSI 461 / 유니코드 513 | 인코딩 방식. 아래 표를 봅니다 |

- MS-PST 명세는 PST 만 다루므로 `wMagicClient` 를 "SM" 으로만 적고, "SO"·"AB" 는 libpff 문서에 있습니다.
- 빈 PST 를 만들 때 `rgnid` 의 시작값은 일반 폴더 `0x400`, 검색 폴더 `0x4000`, 일반 메시지 `0x10000`, 연관 메시지 `0x8000`, 나머지 `0x400` 입니다.
- 할당표 상태 필드는 지운 데이터를 찾을 때 씁니다. 위치와 값은 [지운 메시지 복구 (Recoverable Items·Free Blocks)](recoverable-items-free-blocks.md)에서 다룹니다.

### ROOT

ROOT 는 헤더 안에 든 구조입니다. 필드 위치는 다음과 같습니다.

| 필드 | 32비트 오프셋 | 64비트 오프셋 |
|---|---|---|
| 파일 전체 크기 | 168 (`0xA8`) | 184 (`0xB8`) |
| 마지막 데이터 할당표 위치 | 172 (`0xAC`) | 192 (`0xC0`) |
| 남은 데이터 공간 크기 | 176 (`0xB0`) | 200 (`0xC8`) |
| 설명자 색인 (NBT) 위치 | 188 (`0xBC`) | 224 (`0xE0`) |
| 오프셋 색인 (BBT) 위치 | 196 (`0xC4`) | 240 (`0xF0`) |

파일 전체 크기 필드는 32비트 형식에서 4바이트, 64비트 형식에서 8바이트입니다. 바로 다음 필드와의 거리로 알 수 있습니다.

### 인코딩 (bCryptMethod)

| 값 | 뜻 | Outlook 화면 이름 |
|---|---|---|
| `0x00` | 인코딩 없음 | |
| `0x01` | 치환 (Permutation) 인코딩 | 압축 가능 암호화 |
| `0x02` | 순환 (Cyclic) 인코딩 | 높은 암호화 |
| `0x10` | WIP 로 암호화 | |

- `0x01`·`0x02` 는 암호화가 아니라 인코딩 (encoded) 입니다.
- `0x02` 는 3 로터 에니그마와 비슷한 방식입니다.
- `0x10` 은 WIP 로 암호화한 파일입니다. 다루는 법은 [암호화 증거 다루기](../../../03-techniques/analysis/encrypted-evidence/index.md)를 봅니다.

### 페이지와 블록

| 형식 | 페이지 크기 | 블록 | 블록 최대 크기 |
|---|---|---|---|
| 보통 (ANSI·유니코드) | 512바이트 | 64바이트 단위 | 8,192바이트 |
| 4KB 형식 (wVer 36) | 4,096바이트 | — | 약 65,536바이트 |

4KB 형식에서는 블록을 deflate (RFC 1951) 로 압축할 수 있고, 이때 블록 끝부분에 압축 전 크기를 적는 필드가 따로 있습니다.

### 항목 번호 (NID)

파일 안의 항목에는 번호 (NID) 가 붙습니다. 몇몇 번호는 고정돼 있습니다.

| 고정 NID | 항목 |
|---|---|
| `0x21` | 메시지 저장소 |
| `0x61` | 이름-ID 대응표 |
| `0x122` | 루트 폴더 |
| `0xA1` | 폴더 틀 |
| `0xC1` | 검색 폴더 틀 |

NID 에는 항목 종류를 나타내는 값이 들어 있습니다.

| 종류 값 | 항목 | 종류 값 | 항목 |
|---|---|---|---|
| `0x02` | 폴더 | `0x0D` | 하위 폴더 표 |
| `0x03` | 검색 폴더 | `0x0E` | 메시지 목록 표 |
| `0x04` | 메시지 | `0x11` | 첨부 표 |
| `0x05` | 첨부 | `0x12` | 수신자 표 |
| `0x08` | 연관 메시지 | | |

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 시그니처와 `wMagicClient` 가 맞으면 PFF 파일이고, PST·OST·PAB 가운데 무엇인지 압니다. 확장자를 바꿔도 헤더는 그대로입니다 | 누가, 어느 PC 에서 이 파일을 만들었는지. 이 페이지의 헤더 필드에는 사용자나 PC 를 가리키는 값이 없습니다 |
| `wVer` 로 ANSI·유니코드·4KB·WIP 형식을 구분합니다 | 파일 안의 메일을 이 PC 에서 보내거나 받았는지. PST 는 다른 PC 에서 옮겨 올 수 있습니다 |
| ROOT 의 파일 크기가 실제 크기와 같으면 파일이 끝까지 있다고 볼 수 있습니다 | 파일에 없는 메일이 처음부터 없었다는 것 ([지운 메시지 복구](recoverable-items-free-blocks.md)) |
| `bCryptMethod` 로 인코딩·WIP 암호화 여부를 압니다 | 헤더의 `dwUnique` 가 언제 바뀌었는지. 이 값은 횟수이지 시각이 아닙니다 |

`rgnid` 는 종류별로 마지막에 쓴 번호입니다. 남아 있는 항목의 번호와 비교하면 지운 항목의 단서가 될 수 있습니다. 다만 번호가 비는 이유는 알려져 있지 않으므로 삭제로 단정하지 않습니다.

### 보고서 문장

아래 경로와 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`D:\Users\<사용자>\Documents\Outlook Files\archive.pst` 는 헤더 시그니처 `!BDN`, 클라이언트 표시 `SM`, 형식 버전 23 인 유니코드 PST 입니다. 헤더에 적힌 파일 크기는 실제 파일 크기와 같습니다."
- 쓰면 안 되는 문장: "이 사용자는 이 PC 의 Outlook 으로 archive.pst 의 메일을 주고받았습니다."

## 시각 해석

- 파일 안의 날짜·시각 값은 UTC 기준 FILETIME 입니다. 바꾸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다.
- 이 페이지에서 다룬 헤더 필드에는 시각이 없습니다. 메시지와 폴더의 시각은 속성 값으로 들어 있습니다([MAPI 속성](../../../01-foundations/app-mail-data/mapi-property.md)).
- PST·OST 파일 자체의 NTFS 시각은 파일이 디스크에서 바뀐 시각입니다. 메시지 시각과 따로 봅니다([마스터 파일 테이블](../../filesystem/mft.md)).
- Outlook 이 언제 파일을 다시 쓰는지는 공개 문서에 나와 있지 않습니다. 그래서 파일 수정 시각을 사용자가 메일을 다룬 시각으로 바로 읽지 않습니다.
- 현지 시각으로 옮길 때는 [시간대 설정](../../system-account/time-zone.md)을 봅니다.

## 함정과 한계

1. **확장자로만 파일을 찾습니다.** 이름을 바꾼 PST 는 확장자 검색에서 빠집니다. 시그니처 `21 42 44 4E` 와 오프셋 8 의 `wMagicClient` 로 한 번 더 찾습니다.
2. **"높은 암호화" 라는 화면 이름을 보고 복호화 키부터 찾습니다.** `0x01`·`0x02` 는 인코딩이므로, 암호로 단정하기 전에 공개 파서로 먼저 열어 봅니다.
3. **인코딩된 파일에서 글자를 그대로 검색합니다.** `bCryptMethod` 가 `0x01`·`0x02` 이면 블록 바이트가 원래 글자와 다릅니다. 원시 바이트 검색에서 본문이 빠질 수 있으므로 파서로 먼저 풀어낸 결과를 검색합니다([파일 내용 검색](../../../03-techniques/analysis/content-search/index.md)).
4. **헤더의 인코딩 값을 그대로 믿습니다.** 인코딩 종류가 0 인데도 내용이 인코딩된 손상 사례가 알려져 있습니다. 도구가 깨진 글자를 내면 이 경우를 의심합니다.
5. **4KB 형식을 옛 도구로 읽습니다.** `wVer` 가 36 이면 페이지 크기와 블록 압축이 다릅니다. 도구가 이 형식을 지원하는지 먼저 확인합니다.
6. **크기 한도 값이 있으면 기본값으로 여깁니다.** 한도 값은 기본으로 없습니다. 값이 있으면 누군가 넣은 것이므로 언제 들어갔는지 [레지스트리 하이브](../../../01-foundations/database-log-formats/registry-hive/index.md)의 키 마지막 기록 시각과 함께 봅니다.
7. **새 Outlook 도 같은 파일을 쓴다고 봅니다.** 새 Outlook 이 자기 메일을 PC 어디에 어떤 형식으로 두는지는 [새 Outlook](../new-outlook.md) 페이지를 봅니다.

## 직접 분석해 보기

### 원시 바이트로 한 번

아래는 위 필드 위치로 만든 예시입니다. 실제 파일에서 뽑은 값이 아닙니다. 파일 크기 값은 설명을 위해 고른 수입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
000000  21 42 44 4E .. .. .. .. 53 4D 17 00 13 00 .. ..
...
0000B0  .. .. .. .. .. .. .. .. 00 50 04 00 00 00 00 00
...
000200  80 01
```

1. 오프셋 0 의 `21 42 44 4E` 는 "!BDN" 입니다. PFF 파일입니다.
2. 오프셋 8 의 `53 4D` 는 "SM" 입니다. PST 입니다.
3. 오프셋 10 의 `17 00` 을 낮은 바이트가 앞에 오는 순서(리틀 엔디언)로 읽으면 23 입니다. 64비트 유니코드 형식입니다.
4. 오프셋 12 의 `13 00` 은 19 입니다. `wVerClient` 값입니다.
5. 유니코드 형식이므로 파일 크기는 오프셋 184(`0xB8`)의 8바이트를 읽습니다. `00 50 04 00 00 00 00 00` 은 `0x45000` = 282,624바이트입니다. 이 값을 실제 파일 크기와 비교합니다.
6. 오프셋 512(`0x200`)의 `80` 은 `bSentinel` 입니다. 이 값이 `0x80` 이면 필드 위치를 제대로 잡은 것입니다.
7. 오프셋 513 의 `01` 은 `bCryptMethod` 입니다. 치환 인코딩입니다.

ANSI 형식(`wVer` 14·15)이면 파일 크기는 오프셋 168 의 4바이트, `bSentinel` 은 460, `bCryptMethod` 는 461 에서 읽습니다.

Windows 11 25H2 의 유니코드 PST 한 예에서는 시그니처가 `!BDN`, `wMagicClient` 가 "SM", `wVer` 가 23, `wVerClient` 가 19 입니다. 오프셋 184 의 값은 실제 파일 크기(4,591,469,568바이트)와 같고, 오프셋 512 는 `0x80`, 513 은 `0x01` 입니다.

아래 파이썬 코드는 위 순서를 옮긴 것입니다.

```python
import os, struct, sys

p = sys.argv[1]
b = open(p, "rb").read(600)
sig = b[0:4]
client = b[8:10]
ver, ver_client = struct.unpack_from("<HH", b, 10)

if ver in (14, 15):                      # 32비트 ANSI
    size, = struct.unpack_from("<I", b, 168)
    sentinel, crypt = b[460], b[461]
else:                                    # 64비트 유니코드 (23·36·37 등)
    size, = struct.unpack_from("<Q", b, 184)
    sentinel, crypt = b[512], b[513]

print("시그니처", sig, "클라이언트", client, "wVer", ver, "wVerClient", ver_client)
print("bSentinel", hex(sentinel), "bCryptMethod", hex(crypt))
print("헤더의 파일 크기", size, "실제 파일 크기", os.path.getsize(p))
```

- `bSentinel` 이 `0x80` 이 아니면 형식을 잘못 골랐거나 헤더가 손상된 것입니다.
- 두 파일 크기가 다르면 파일이 잘렸거나, 뒤에 무언가 붙었거나, 수집이 끝까지 되지 않았을 수 있습니다. 수집 기록과 해시를 먼저 확인합니다([증거 획득](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)).

> 그림 자리: 유니코드 PST 헤더 564바이트를 가로 띠로 그리고, 시그니처·wMagicClient·wVer·ROOT·bSentinel·bCryptMethod 위치를 색으로 표시한 그림

### 공개 도구로 한 번

PFF 파일을 읽는 공개 도구로는 libpff 와 그 명령줄 도구(pffinfo·pffexport 등)를 예로 들 수 있습니다. 어떤 도구를 쓰든 다음을 확인합니다.

- 헤더에서 읽은 `wVer`·`bCryptMethod` 가 위에서 손으로 읽은 값과 같은지 확인합니다.
- 4KB 형식(wVer 36)과 WIP 파일을 지원하는지 확인합니다.
- 시각을 UTC 로 보여 주는지, 현지 시각으로 바꿔 보여 주는지 확인합니다.
- 지운 항목이나 빈 공간을 따로 다루는지, 다룬다면 어떤 방법으로 찾는지 확인합니다.
- 같은 파일을 도구 두 개로 열어 폴더·메시지 수를 비교합니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [PST와 OST 차이 (Cached Mode·Exchange)](cached-mode-exchange.md) | OST 에 들어가는 범위. 서버 사서함과의 관계 |
| [계정·프로필 레지스트리 (Outlook Profiles)](outlook-profiles.md) | 이 PC 의 Outlook 프로필에 어떤 계정과 데이터 파일이 있었는지 |
| [지운 메시지 복구 (Recoverable Items·Free Blocks)](recoverable-items-free-blocks.md) | 파일 안 빈 공간과 서버 쪽 지운 항목 |
| [개별 메시지 파일 (MSG)](msg.md) | 따로 저장한 메시지가 PST 안의 메시지와 같은지 |
| [첨부 임시 폴더 (OLK·Content.Outlook)](olk-content-outlook.md) | PST 안 첨부를 연 흔적 |
| [설치 프로그램](../../system-account/uninstall.md) | 설치된 Outlook 판. 기본 위치와 형식을 추정합니다 |
| [마스터 파일 테이블](../../filesystem/mft.md) · [USN 변경 저널](../../filesystem/usnjrnl.md) | PST·OST 파일이 생기고, 커지고, 옮겨지고, 지워진 기록 |
| [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 예전 시점의 PST. 지금 파일과 폴더·메시지 수를 비교합니다 |
| [휴지통](../../file-folder-usage/recycle-bin.md) | 지운 PST 파일 |

메일 기록을 다른 기록과 합쳐 읽는 순서는 [누구와 연락을 주고받았나](../../../04-scenarios/activity/communication-reconstruction.md)에서 다룹니다.

## 실습

**직접 만든 Windows 10·11 가상 머신에 클래식 Outlook 을 깔고** 해 봅니다.

1. 새 PST 를 만들고 위 파이썬 코드로 헤더를 읽어 보십시오. `wVer` 와 `bCryptMethod` 는 얼마입니까? 파일은 어느 폴더에 생겼습니까?
2. 메시지 하나를 넣고 Outlook 을 닫은 뒤 다시 읽어 보십시오. ROOT 의 파일 크기가 바뀌었습니까? 헤더 564바이트를 앞의 사본과 비교하면 어느 바이트가 바뀌었습니까?
3. PST 를 만들 때 인코딩 선택지가 있으면 바꿔 가며 만들어 보십시오. 화면 이름과 `bCryptMethod` 값이 위 표와 맞습니까?
4. `HKCU\Software\Microsoft\Office\16.0\Outlook\PST` 에 크기 한도 값이 있습니까? 없다면 어떤 동작을 해야 생깁니까?

**공개 시험 데이터(NIST CFReDS 등)** 가운데 메일 데이터가 든 이미지에서도 해 봅니다.

1. 확장자 검색과 시그니처 검색으로 찾은 PFF 파일 수가 같습니까?
2. 파일마다 `wMagicClient` 와 `wVer` 를 표로 만들어 보십시오. OST 가 있습니까?
3. 헤더의 파일 크기와 실제 크기가 다른 파일이 있습니까? 있다면 어떤 설명이 가능합니까?

## 참고 문헌

- libyal libpff, "Personal Folder File (PFF) format" (문서 판 0.0.48, 2020-07) — https://raw.githubusercontent.com/libyal/libpff/main/documentation/Personal%20Folder%20File%20(PFF)%20format.asciidoc
- Microsoft Learn, "[MS-PST]: HEADER" (2025-02-18 갱신) — https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-pst/c9876f5a-664b-46a3-9887-ba63f113abf5
- Microsoft 지원, "Introduction to Outlook Data Files (.pst and .ost)" — https://support.microsoft.com/en-us/office/introduction-to-outlook-data-files-pst-and-ost-222eaf92-a995-45d9-bde2-f331f60e2790
- Microsoft Learn, "Configure Size Limit for PST and OST Files In Outlook" (옛 KB 832925, 2026-09-10) — https://learn.microsoft.com/en-us/microsoft-365-apps/outlook/data-files/configure-size-limit-outlook-data-files
