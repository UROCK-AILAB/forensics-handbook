---
title: "식별자 읽기"
parent: "기반 · 값 읽는 법"
nav_order: 310
---

# 식별자 읽기 (UUID·UID·GUID)

## 한 줄 요약

맥의 아티팩트에는 볼륨·계정·항목을 가리키는 128비트 UUID 와 파일 시스템이 매기는 번호(HFS+ 의 CNID, APFS 의 아이노드 번호, 사용자 UID)가 섞여 나와서, 값이 어떤 종류인지 먼저 가리고 UUID 라면 버전 자리를 읽어 그 안에 시각이나 기기 정보가 들어 있는지부터 판단합니다.

## 이 형식을 쓰는 아티팩트

| 쓰는 곳 | 식별자 | 뜻 | 구조 페이지 |
|---|---|---|---|
| APFS 볼륨 슈퍼블록 | `apfs_vol_uuid` (`uuid_t`, 16바이트) | 볼륨 UUID | [APFS 구조](../disk-volume/apfs/index.md) |
| APFS 아이노드 | `owner` (uid_t), `group` (gid_t) | 소유 사용자 ID, 그룹 ID | [APFS 구조](../disk-volume/apfs/index.md) |
| APFS 디렉터리 항목 | `j_drec_val_t.file_id` (uint64) | 이 항목이 가리키는 아이노드 번호 | [APFS 구조](../disk-volume/apfs/index.md) |
| HFS+ 카탈로그 | CNID (`HFSCatalogNodeID`, UInt32) | 파일·폴더 번호 | [HFS+ 구조](../disk-volume/hfs-plus.md) |
| 북마크 데이터 | 키 0x1030 대상 CNID, 0x1005 CNID 경로, 0x2011 볼륨 UUID, 0xc012 만든 사용자 UID | 대상 파일과 볼륨, 북마크를 만든 사용자 | [파일 참조 데이터](alias-bookmark.md) |
| Alias 레코드 | 포함 폴더 CNID, 대상 CNID | 대상 파일과 그 폴더 | [파일 참조 데이터](alias-bookmark.md) |

로컬 계정의 UID 와 계정 UUID 가 어떻게 매겨지고 어디에 남는지는 [사용자 계정](../../02-artifacts/system-account/user-accounts/index.md)에서 다룹니다. 제목의 GUID 는 윈도우에서 흔히 쓰는 이름이고, 이 페이지에서는 RFC 9562 가 정의한 UUID 형식으로 다룹니다.

## 구조

### UUID 글자 표현과 버전 자리

2024년 5월에 나온 RFC 9562 가 RFC 4122 를 대체했고, 아래 내용은 RFC 9562 를 따릅니다. UUID 는 16진수 32자를 8-4-4-4-12 로 묶어 하이픈을 넣은 36자로 적고, 입력할 때는 대소문자를 구분하지 않습니다.

```text
xxxxxxxx-xxxx-Mxxx-Nxxx-xxxxxxxxxxxx
              ^    ^
              |    +-- 넷째 묶음 첫 자리 N: 변형 (비트 64~65)
              +------- 셋째 묶음 첫 자리 M: 버전 (비트 48~51)
```

변형(variant) 자리가 8·9·A·B 가운데 하나면 RFC 가 정한 변형이고, 이때 버전 자리로 아래처럼 뜻을 가립니다.

| 버전 | 만드는 방식 | 안에 든 정보 |
|---|---|---|
| 1 | 시각 기반 | 1582-10-15 00:00:00 UTC 부터 100나노초 단위로 센 60비트 시각, 시계 순번(clock sequence), 노드 필드 (IEEE 802 MAC 주소가 들어갈 수 있음) |
| 3 | 이름공간 ID 와 이름의 MD5 | 같은 이름이면 같은 값 |
| 4 | 무작위 | 버전·변형 비트를 뺀 122비트가 모두 무작위 |
| 5 | 이름공간 ID 와 이름의 SHA-1 (앞 128비트) | 같은 이름이면 같은 값 |
| 7 | 유닉스 시각 기반 | 48비트 유닉스 시각(밀리초)과 74비트 무작위 값 또는 카운터 |

모든 비트가 0 인 값을 Nil UUID, 모든 자리가 F 인 값을 Max UUID 라고 부릅니다. 바이너리로 적을 때는 네트워크 바이트 순서(빅엔디언)를 씁니다.

### APFS 의 UUID 와 번호

APFS 의 `uuid_t` 는 `unsigned char[16]` 입니다[2]. 볼륨 UUID 는 볼륨 슈퍼블록의 `apfs_vol_uuid` 에 있고, 아이노드의 `owner` 는 아이노드 소유자의 사용자 식별자, `group` 은 그룹 식별자입니다[2]. 디렉터리 항목 값 `j_drec_val_t` 의 `file_id` 는 그 이름이 가리키는 아이노드 번호입니다.

APFS 에는 개인 복구 키를 가리키는 고정 UUID 상수 `APFS_FV_PERSONAL_RECOVERY_KEY_UUID` 도 있어서[2], APFS 안에서 만나는 UUID 가 모두 무작위로 만든 값은 아닙니다. 이 상수가 쓰이는 자리는 [파일볼트](../protection/filevault/index.md)에서 다룹니다.

### HFS+ 의 CNID

HFS+ 는 카탈로그의 파일과 폴더마다 카탈로그 노드 ID(CNID, `HFSCatalogNodeID`, UInt32)를 매기고, 폴더의 CNID 를 폴더 ID(dirID), 파일의 CNID 를 파일 ID 라고 부릅니다. 앞쪽 번호는 특수 파일에 예약되어 있습니다.

| CNID | 쓰임 |
|---|---|
| 1 | 루트 폴더의 부모 |
| 2 | 루트 폴더 |
| 3 | 익스텐트 파일 |
| 4 | 카탈로그 파일 |
| 5 | 불량 블록 파일 |
| 6 | 할당 파일 |
| 7 | 시작 파일 |
| 8 | 속성 파일 |
| 14 | 복구 카탈로그 파일 |
| 15 | 가짜 익스텐트 파일 |
| 16 | 사용자 파일·폴더에 쓰는 첫 번호 (`kHFSFirstUserCatalogNodeID`) |

CNID 는 한 바퀴 돌아 다시 쓰일 수 있고, 이런 볼륨은 볼륨 헤더 `attributes` 의 `kHFSCatalogNodeIDsReusedBit` 로 표시합니다[3].

## 읽는 법

아래 값은 명세로 만든 예시이고, 특정 검체에서 나온 값이 아닙니다.

```text
00112233-4455-4677-8899-AABBCCDDEEFF
              ^    ^
              |    +-- 넷째 묶음 첫 자리 8 → RFC 변형
              +------- 셋째 묶음 첫 자리 4 → 버전 4 (무작위)

바이너리 (16바이트, 네트워크 바이트 순서)
00 11 22 33 44 55 46 77 88 99 AA BB CC DD EE FF
                  ^^    ^^
                  버전  변형
```

UUID 하나를 만나면 다음 순서로 읽습니다.

1. 넷째 묶음 첫 자리가 8·9·A·B 인지 봅니다. 아니면 RFC 변형이 아니라서 위 버전 표를 그대로 적용하지 않습니다.
2. 셋째 묶음 첫 자리에서 버전을 읽습니다.
3. 버전 4 면 값 안에 시각이나 기기 정보가 없어서, 같은 값이 나오는 다른 기록을 찾아 서로 잇는 열쇠로만 씁니다.
4. 버전 1·7 이면 만든 시각이 들어 있어서, RFC 9562 를 구현한 도구로 시각을 꺼내 보고 버전 1 은 노드 필드도 확인합니다.
5. 버전 3·5 면 같은 이름공간과 이름에서 늘 같은 값이 나와서, 만든 시각을 뜻하지 않습니다.

파이썬 표준 라이브러리로는 아래처럼 버전과 변형을 확인할 수 있습니다.

```python
import uuid
u = uuid.UUID("00112233-4455-4677-8899-AABBCCDDEEFF")
print(u.version, u.variant)   # 4 specified in RFC 4122
```

CNID·아이노드 번호·UID 는 UUID 와 달리 그냥 정수라서 값만으로는 뜻을 알 수 없고, 어느 볼륨의 어느 구조에서 읽었는지를 함께 적어야 의미가 생깁니다. HFS+ CNID 가 16 보다 작으면 위 예약 표에서 뜻을 찾고(표에 없는 번호도 있습니다), 16 이상이면 카탈로그에서 그 번호의 레코드를 찾아 이름과 부모 폴더를 확인합니다.

## 포렌식에서 중요한 점

볼륨 UUID 는 여러 기록을 한 볼륨으로 묶는 열쇠입니다. 북마크 데이터에 남은 볼륨 UUID(키 0x2011)를 조사 대상 볼륨의 `apfs_vol_uuid` 와 맞춰 보면 그 북마크가 가리킨 파일이 이 볼륨에 있었는지 다른 볼륨에 있었는지 가늠할 수 있습니다. 북마크의 0x2011 은 UUID 형식이 아니라 문자열이므로[4], 16바이트 `apfs_vol_uuid` 를 글자 표현으로 바꿔 대소문자를 무시하고 비교합니다. 두 값이 같은 UUID 를 가리키는지는 검체에서 확인해야 해서, 알고 있는 볼륨 하나로 먼저 맞춰 본 뒤에 씁니다. 외장 장치 쪽 흐름은 [USB 저장 장치](../../02-artifacts/external-devices/usb/index.md)에서 다룹니다.

HFS+ 에서 `kHFSCatalogNodeIDsReusedBit` 가 켜진 볼륨이면 같은 CNID 가 시점에 따라 다른 파일을 가리켰을 수 있습니다. 북마크나 Alias 에 남은 대상 CNID 로 지금 볼륨에서 파일을 찾았을 때는, 이름과 생성 시각도 함께 맞춰 보고 같은 파일이라고 적습니다.

APFS 아이노드의 `owner` 와 북마크의 만든 사용자 UID(0xc012)·사용자 이름(0xc011)은 파일이나 북마크가 어느 계정과 엮여 있는지 보여 주지만, 그 계정을 실제로 쓴 사람이 누구인지는 말하지 않습니다. 사람을 특정하는 흐름은 [그 시각에 맥을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)에서 다룹니다.

버전 1 UUID 의 노드 필드에 MAC 주소가 들어 있으면 그 값을 만든 기기의 네트워크 카드를 가리킬 수 있지만, 노드 필드에 MAC 주소가 꼭 들어가는 것은 아니어서 무작위 값일 수도 있습니다[1]. 노드 값을 기기 식별 근거로 쓸 때는 [컴퓨터 이름과 하드웨어 정보](../../02-artifacts/system-account/computer-name-hardware.md)의 다른 기록과 맞춰 봅니다.

## 함정

UUID 를 바이트로 저장한 자리를 읽을 때, RFC 9562 의 UUID 는 네트워크 바이트 순서로 적지만[1], 윈도우 GUID 의 바이트 저장 순서는 따로 확인해야 합니다. 윈도우에서 만든 값이나 윈도우용 도구의 출력을 섞어 볼 때는 글자 표현과 원시 바이트를 따로 대조합니다.

글자로 적힌 UUID 는 대소문자를 가리지 않아서, 문자열 검색은 대소문자를 무시하고 해야 빠뜨리지 않습니다. 하이픈을 빼고 32자로 적거나 중괄호로 감싸 적는 기록도 있을 수 있어서, 검색어를 여러 모양으로 만들어 봅니다.

`FFFFEEEE` 로 시작하는 계정 UUID 를 시스템 계정으로 보는 도구 규칙, 일반 사용자 UID 가 501 부터 시작한다는 관례, 하드웨어 UUID 가 남는 자리가 도구 결과에 나오면 [사용자 계정](../../02-artifacts/system-account/user-accounts/index.md)과 해당 도구 문서를 따로 확인합니다.

## 도구

UUID 버전·변형 확인은 위처럼 파이썬 `uuid` 모듈로 충분하고, 버전 1·7 에서 시각을 꺼낼 때는 RFC 9562 를 구현한 라이브러리를 씁니다. APFS·HFS+ 의 UUID 와 번호는 파일 시스템을 읽는 공개 도구(The Sleuth Kit 등)의 메타데이터 출력에서 확인하고, 의심스러우면 [APFS 구조](../disk-volume/apfs/index.md)와 [HFS+ 구조](../disk-volume/hfs-plus.md)를 보고 헥스로 필드 하나를 따라가 봅니다.

## 참고 문헌

1. IETF, RFC 9562: Universally Unique IDentifiers (UUIDs) (2024-05), https://www.rfc-editor.org/rfc/rfc9562.html
2. Apple, Apple File System Reference (2020-06-22 판), https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
3. Apple, Technical Note TN1150: HFS Plus Volume Format, https://developer.apple.com/library/archive/technotes/tn/tn1150.html
4. mac_alias 문서, Mac Bookmark Format, https://mac-alias.readthedocs.io/en/latest/bookmark_fmt.html
5. mac_alias 문서, Mac Alias Format, https://mac-alias.readthedocs.io/en/latest/alias_fmt.html
