---
title: "외부 장치·네트워크·압축 폴더 탐색 흔적"
parent: "셸백"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1180
---

# 외부 장치·네트워크·압축 폴더 탐색 흔적

## 한 줄 요약

셸백은 로컬 디스크 폴더뿐 아니라 USB 드라이브, 휴대폰(MTP), 네트워크 공유, FTP 주소, ZIP 파일 속 폴더를 탐색한 흔적도 남깁니다. 경로를 이루는 셸 아이템의 종류를 보면 그 폴더가 어디에 있었는지 가릴 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

탐색기는 파일 시스템 밖의 것도 다룹니다. 셸 네임스페이스 (Shell Namespace)에는 네트워크 컴퓨터, 프린터, 제어판 같은 가상 폴더도 들어 있고, 매핑한 네트워크 드라이브의 루트도 "내 PC" 아래에 놓입니다. (Microsoft Learn, Introduction to the Shell Namespace)

셸은 네임스페이스의 각 항목을 셸 아이템 (Shell Item)으로 가리킵니다. 셸 아이템의 내용은 그 항목을 담은 폴더가 정하고, 그 형식을 해석할 수 있는 것도 그 폴더뿐입니다. (같은 문서)

그래서 셸백 경로 한 줄은 여러 형식의 셸 아이템이 이어진 것입니다. USB 폴더는 볼륨 아이템 뒤에 파일 항목 아이템이 붙고, 네트워크 공유는 네트워크 위치 아이템으로 시작하며, 휴대폰은 MTP 전용 아이템으로, ZIP 속 폴더는 압축 폴더 아이템으로 기록됩니다. 셸 아이템 공통 구조는 [셸 아이템 (Shell Item·PIDL)](../../../01-foundations/shell-document-formats/shell-item-pidl.md)에서 다룹니다.

셸백은 사용자 레지스트리 하이브에 있습니다. 그래서 장치를 빼거나 공유가 사라져도 항목이 함께 지워지지 않습니다.

> 그림 자리: 셸백 트리 세 가지 경로 — "내 PC → E:\ → 폴더", "네트워크 → \\FS01 → \\FS01\docs → 폴더", "바탕 화면 → … → 자료.zip → ZIP 속 폴더". 각 단계 옆에 셸 아이템 종류를 적는다.

## 위치와 버전별 차이

저장하는 키는 일반 셸백과 같습니다. 하이브·키 경로·BagMRU 트리 읽는 법은 [저장 위치와 구조](ntuser-usrclass-bagmru-bags.md)를 봅니다.

이 페이지 주제와 관련해 눈여겨볼 차이는 아래와 같습니다.

| Windows | 기록 위치의 특징 | 출처 |
|---|---|---|
| XP | NTUSER.DAT 안에서 나뉩니다. `Software\Microsoft\Windows\Shell` 에는 네트워크 폴더, `ShellNoRoam` 에는 로컬 폴더, `StreamMRU` 에는 이동식 장치 폴더가 남습니다. | 4n6k |
| 7 | 로컬·네트워크·이동식 폴더 대부분이 UsrClass.dat `Local Settings\Software\Microsoft\Windows\Shell` 에 남습니다. NTUSER.DAT `Software\Microsoft\Windows\Shell` 에도 네트워크 폴더 항목이 더 남습니다. | 4n6k |

네트워크 흔적을 찾을 때는 두 하이브를 모두 봐야 합니다.

셸 아이템 형식도 버전에 따라 다릅니다.

| 아이템 | 버전 관련 사실 | 출처 |
|---|---|---|
| 압축 폴더 아이템 | XP 형식과 Windows 10 형식이 서로 다릅니다. Windows 10 형식에는 크기·압축 방식·CRC-32 필드가 있습니다. | libfwsi |
| MTP 아이템 | Windows 7 의 BagMRU 와 LNK 파일에서 관찰됐습니다. | libfwsi |
| URI 아이템 확장 블록 | Vista 에서 IE7 과 함께 관찰됐습니다. | libfwsi |

Windows 11 에서 이 아이템들이 바뀌었는지는 실제 데이터로 확인해야 합니다.

## 구조

셸 아이템은 앞 2바이트가 크기이고, 오프셋 2가 종류 표시 (Class Type Indicator)입니다. 종류 표시에 0x70 을 AND 해서 큰 분류를 나누는 아이템이 있고, 서명이나 부모 아이템으로 구분하는 아이템이 있습니다. 아래 표는 libfwsi 명세(Windows Shell Item format)를 따릅니다.

| 무엇을 탐색했나 | 셸 아이템 | 구분 방법 | 들어 있는 값 |
|---|---|---|---|
| USB·외장 디스크 드라이브 | 볼륨 아이템 (Volume Shell Item) | 종류 표시 & 0x70 = 0x20 | 이름 플래그(0x01)가 있으면 오프셋 3부터 20바이트에 `E:\` 같은 ASCII 이름 |
| 탐색 창의 이동식 드라이브 | 위임 폴더 아이템 "Removable Drives" | 끝부분 위임 클래스 GUID `5e591a74-df96-48d3-8d67-1733bcee28ba` 와 폴더 GUID `f5fb2c77-0e2f-4a16-a381-3e560c68bc83` | 안쪽에 볼륨 아이템이 통째로 들어 있음 |
| 네트워크 서버·공유 | 네트워크 위치 아이템 (Network Location Shell Item) | 종류 표시 & 0x70 = 0x40 | 오프셋 5부터 네트워크 이름 또는 UNC 경로(ASCII). 플래그 0x80 이면 설명, 0x40 이면 주석 문자열이 뒤따름 |
| FTP 주소 | URI 아이템 | 종류 표시 = 0x61 | URI 문자열, FILETIME 한 개, 문자열 세 개(FTP 에서는 호스트·사용자 이름·비밀번호로 추정) |
| 휴대폰·카메라(MTP) | 위임 폴더 아이템 "Portable Devices" | 위임 폴더 GUID `35786d3c-b075-49b9-88dd-029876e11c01` | UTF-16 문자열 두 개와 속성 배열 |
| MTP 저장소 | MTP 저장소 볼륨 아이템 | 종류 표시 0x00, 오프셋 6 서명 `0x10312005` | 이름·식별자·파일 시스템 문자열(UTF-16) |
| MTP 저장소 속 폴더 | MTP 파일 항목 아이템 | 종류 표시 0x00, 오프셋 6 서명 `0x07192006` | 폴더 이름 두 개, 폴더 식별자 문자열, 뜻이 확정되지 않은 FILETIME 두 개 |
| ZIP 파일 속 폴더 | 압축 폴더 아이템 (Compressed Folder Shell Item) | 부모 아이템이 ZIP 파일임 | Windows 10 형식: 압축 전 크기(오프셋 8), 압축 후 크기(16), 압축 방식(24, 0x00 없음·0x08 DEFLATE), CRC-32(28), 수정 시각 문자열, 이름 |
| CAB 파일 속 항목 | 캐비닛 파일 아이템 | 오프셋 8 서명 `0x9e5a5871` | 이름(UTF-16) |

네트워크 위치 아이템은 종류 표시의 아래 비트로 무엇을 가리키는지 나눕니다. 0x01 은 도메인·작업 그룹, 0x02 는 서버 UNC 경로, 0x03 은 공유 UNC 경로입니다. 0x06 은 Microsoft Windows Network, 0x07 은 Entire Network 입니다. 실제로 나타난 값은 0x41·0x42·0x46·0x47·0x4c·0xc3 입니다.

ZIP 파일 자체는 일반 파일 항목 아이템으로 기록됩니다. 그 아래에 이어지는 아이템이 압축 폴더 아이템입니다. ZIP 형식에는 원래 폴더 항목이 따로 없어서 셸이 폴더를 흉내 내어 셸 아이템을 만듭니다. (libfwsi)

NTFS 볼륨의 폴더를 가리키는 파일 항목 아이템에는 확장 블록 0xbeef0004 가 붙습니다. 이 블록의 버전 7 이상에는 NTFS 파일 참조(MFT 항목 번호 6바이트 + 순번 2바이트) 필드가 있습니다. 다만 이 필드에 늘 파일 참조가 들어 있는지는 확정되지 않았습니다. (libfwsi)

## 증거로서 의미

### 증명하는 것

- 이 사용자 프로필의 셸이 그 경로를 폴더로 다룬 적이 있습니다.
- 경로가 어떤 종류의 위치였는지 알 수 있습니다. 드라이브 문자, UNC 서버·공유 이름, FTP 주소, MTP 장치·저장소·폴더 이름, ZIP 파일 이름과 그 속 폴더 이름이 남습니다.
- 장치나 공유가 지금 없어도 당시 폴더 구조가 남습니다.
- Windows 10 형식 압축 폴더 아이템이면 ZIP 속 항목의 크기와 CRC-32 가 남습니다. ZIP 파일을 지운 뒤에도 속 내용을 짐작할 단서가 됩니다.

### 증명하지 못하는 것

- 어느 물리 장치였는지 알려 주지 않습니다. 볼륨 아이템에는 드라이브 문자만 있고 장치 일련번호가 없으며, 드라이브 문자는 여러 장치가 돌려 씁니다.
- 매핑한 네트워크 드라이브도 "내 PC" 아래 드라이브로 보입니다. 경로가 `Z:\` 처럼 드라이브 문자로 시작하면 셸백만으로는 로컬 디스크인지 네트워크 드라이브인지 구분하기 어렵습니다.
- 파일을 복사했거나 열었다는 뜻이 아닙니다. 셸백은 폴더 단위 기록입니다.
- 폴더 안을 실제로 들여다봤다는 뜻도 아닙니다. Windows 7 에서는 폴더를 선택만 해도 항목이 생깁니다. (4n6k)
- FTP 로그인에 성공했다는 뜻이 아닙니다. URI 아이템의 FILETIME 은 서버에 처음 접근한 시각으로 추정될 뿐이고, 접근했다고 인증에 성공한 것은 아닙니다. (libfwsi)
- ZIP 속 폴더 이름이 ZIP 안에 폴더 항목으로 있었다는 뜻이 아닙니다. 셸이 파일 경로에서 폴더를 흉내 낸 것일 수 있습니다.

보고서에는 "이 사용자 계정의 셸백에 `E:\자료\2024` 경로가 있다"처럼 기록으로 확인되는 만큼만 씁니다. "USB 에서 자료를 가져갔다"는 다른 아티팩트로 뒷받침될 때만 씁니다.

## 시각 해석

키의 마지막 기록 시각, 처음 연 때와 마지막 바뀐 때를 읽는 법은 [셸백 시각 해석](timestamps.md)에서 다룹니다. 이 페이지에서는 아이템 안에 든 시각 가운데 외부 위치에서만 생기는 문제를 적습니다.

| 아이템 | 시각 | 뜻과 주의점 |
|---|---|---|
| FAT32 USB 속 폴더의 파일 항목 아이템 | 폴더의 수정·접근·생성 시각 | FAT 은 시각을 현지 시각으로 저장합니다. 접근 시각은 날짜만 있습니다(해상도 1일). 수정 시각 해상도는 2초입니다. (Microsoft Learn, File Times) 그래서 접근 시각이 자정이 아닌 이상한 시각으로 보일 수 있습니다. 미국 중부 시간대 시험에서 UTC 12:00 대신 6:00 이 나왔습니다. (4n6k, Windows 7 기준) |
| 압축 폴더 아이템 | 수정 시각 문자열 | Windows 10 형식은 `06/15/2021  18:24:28` 같은 UTF-16 문자열입니다. 시간대 표시가 없습니다. (libfwsi) 이 값은 ZIP 속 폴더의 수정 시각입니다. 사용자가 ZIP 을 연 시각이 아닙니다. (4n6k) |
| URI 아이템 | FILETIME 한 개 | FTP 서버에 처음 접근한 시각으로 추정합니다. 확정된 뜻은 아닙니다. (libfwsi) |
| MTP 파일 항목 아이템 | FILETIME 두 개 | 수정 시각과 생성 시각으로 추정될 뿐입니다. 직접 시험하기 전에는 보고서에 쓰지 않습니다. (libfwsi) |

Windows 7 에서 아이템 안의 시각은 아이템이 처음 만들어진 뒤 갱신되지 않습니다. (4n6k) FAT 날짜·시각 형식 자체는 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)과 [FAT·exFAT 구조](../../../01-foundations/disk-volume/fat-exfat.md)를 봅니다.

## 함정과 한계

- **볼륨 아이템의 0x08 비트를 믿지 않습니다.** 0x08 은 "이동식 매체" 비트로 알려져 있지만, C: 에서도 0x2f(0x08 포함)가 나타났습니다 (libfwsi). 이 비트 하나로 USB 라고 판단하지 않습니다.
- **0x2e 가 볼륨이라는 보장이 없습니다.** "Portable Devices" 위임 폴더 아이템의 종류 표시로 0x2e 가 관찰됐습니다. 0x2e 에 0x70 을 AND 하면 0x20 이라 볼륨 아이템처럼 보입니다. 끝부분의 위임 클래스 GUID 를 먼저 확인해야 합니다.
- **MTP 아이템은 종류 표시가 0x00 입니다.** 오프셋 6의 서명으로만 구분할 수 있습니다. MTP 아이템 구조는 아직 다 밝혀지지 않아 뜻을 모르는 필드가 많습니다.
- **압축 폴더 아이템은 자기 서명이 없습니다.** 부모가 ZIP 파일이라는 사실로만 구분합니다. 도구가 부모를 보지 않고 아이템만 해석하면 알 수 없는 아이템으로 처리할 수 있습니다.
- **ZIP·CAB 말고 다른 압축 형식은 구조가 공개돼 있지 않습니다.** 탐색기 안에서 다른 압축 형식을 열었을 때 남는 아이템은 공개된 분석 자료가 없습니다. 이런 아이템을 만나면 원시 바이트를 직접 봅니다.
- **압축 프로그램 창 안의 탐색은 다른 이야기입니다.** 압축 프로그램이 자기 창에서 보여 준 압축 파일 속 폴더가 탐색기 셸백에 남는다고 단정할 수 없습니다. 그 흔적은 [압축 프로그램 사용 기록](../7-zip-winrar-bandizip.md)에서 찾습니다.
- **도구마다 모르는 아이템을 다루는 방식이 다릅니다.** MTP·URI·위임 폴더처럼 명세가 덜 된 아이템은 도구에 따라 건너뛰거나 경로 일부가 비어 나옵니다.

셸백 전반의 해석 함정은 [셸백 해석 함정](pitfalls.md)에 모았습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 두 예시는 libfwsi 명세에 맞춰 만든 예시입니다. 실제 데이터에서 나온 값이 아닙니다. 실제 아이템은 뒤에 확장 블록이나 모르는 바이트가 더 붙어 더 길 수 있습니다.

네트워크 공유 `\\FS01\docs` 를 가리키는 네트워크 위치 아이템(명세로 만든 예시):

```
00000000: 11 00 C3 01 00 5C 5C 46 53 30 31 5C 64 6F 63 73  .....\\FS01\docs
00000010: 00                                               .
```

| 오프셋 | 바이트 | 뜻 |
|---|---|---|
| 0 | `11 00` | 아이템 크기 0x0011 = 17바이트(크기 필드 포함) |
| 2 | `C3` | 종류 표시. 0xC3 & 0x70 = 0x40 → 네트워크 위치. 아래 비트 0x03 → 공유 UNC 경로 |
| 3 | `01` | 뜻 모름. UNC 경로에서 0x01 이 나타남 |
| 4 | `00` | 플래그. 0x80(설명)·0x40(주석) 모두 없음 |
| 5 | `5C 5C … 73 00` | 위치 문자열 `\\FS01\docs` (ASCII, 끝에 0) |

드라이브 `E:\` 를 가리키는 볼륨 아이템(명세로 만든 예시):

```
00000000: 19 00 2F 45 3A 5C 00 00 00 00 00 00 00 00 00 00  ../E:\..........
00000010: 00 00 00 00 00 00 00 00 00                       .........
```

| 오프셋 | 바이트 | 뜻 |
|---|---|---|
| 0 | `19 00` | 아이템 크기 25바이트 |
| 2 | `2F` | 종류 표시. 0x2F & 0x70 = 0x20 → 볼륨. 0x01 비트 → 이름 있음 |
| 3 | `45 3A 5C 00 …` | 20바이트 이름 필드. `E:\` 뒤는 0 으로 채움 |
| 23 | `00 00` | 뜻 모름(아이콘 번호나 속성으로 추정) |

볼륨 아이템에는 드라이브 문자 말고 장치를 가릴 값이 없습니다. 그래서 아래 교차 검증이 필요합니다.

### 공개 도구로 한 번

공개 셸백 해석 도구(예: SBECmd·ShellBags Explorer, RegRipper 의 셸백 플러그인)나 libfwsi 라이브러리로 경로를 풀 수 있습니다. 결과에서 경로마다 첫 아이템의 종류(볼륨·네트워크·URI·위임 폴더·압축 폴더)를 확인합니다. 명세가 덜 된 아이템이 나온 경로는 도구 두 개의 결과와 원시 바이트를 함께 봅니다.

## 교차 검증

| 확인할 것 | 함께 볼 아티팩트 |
|---|---|
| 그 드라이브 문자가 어느 USB 였나 | [드라이브 문자 매핑 (MountedDevices)](../../external-devices/usb-storage-artifacts/mounteddevices.md), [사용자별 장치 연결 (MountPoints2)](../../external-devices/usb-storage-artifacts/mountpoints2.md), [휴대용 장치·볼륨 이름 기록 (WPD·EMDMgmt)](../../external-devices/usb-storage-artifacts/wpd-emdmgmt.md) |
| 그 시각에 장치가 꽂혀 있었나 | [연결·해제 시각](../../external-devices/usb-storage-artifacts/deviceclasses-device-properties-0064-0066-0067.md), [외부 장치 연결 이벤트](../../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) |
| NTFS USB 를 압수했을 때 같은 장치인가 | 파일 항목 아이템의 파일 참조를 그 장치의 [$MFT](../../filesystem/mft.md) 항목 번호·순번과 맞춰 봄 |
| 휴대폰이었나 | [휴대용 장치·볼륨 이름 기록 (WPD·EMDMgmt)](../../external-devices/usb-storage-artifacts/wpd-emdmgmt.md), [스마트폰으로 옮겼나](../../../04-scenarios/exfiltration/data-exfiltration/mtp-phone-link.md) |
| 네트워크 공유·매핑 드라이브였나 | [공유 폴더·네트워크 드라이브](../../network/network-shares-mapped-drives.md), 서버 쪽 [공유 폴더 접근 이벤트 (5140·5145)](../../event-logs/5140-5145.md) |
| FTP 를 다른 도구로도 썼나 | [SSH·FTP 도구 흔적](../../network/putty-winscp-filezilla-openssh.md) |
| 그 폴더의 파일을 열었나 | [바로가기 파일 (LNK)](../lnk.md), [점프리스트](../jump-lists.md), [열기·저장 대화상자 기록](../comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) |
| ZIP 을 만들거나 풀었나 | [압축 프로그램 사용 기록](../7-zip-winrar-bandizip.md), [퇴사 전 자료를 모으고 압축했나](../../../04-scenarios/exfiltration/data-exfiltration/staging.md) |

USB 반출 조사 전체 흐름은 [USB 로 무엇을 가져갔나](../../../04-scenarios/exfiltration/data-exfiltration/usb.md)를 봅니다. 지금은 없는 폴더를 찾는 법은 [지운 폴더 흔적 찾기](deleted-folders.md)를 봅니다.

## 실습

NIST CFReDS 의 공개 자료 가운데 정보 유출을 다루는 이미지로 풀어 봅니다. 예를 들어 Data Leakage Case 는 Windows 7 SP1 PC 에 USB 저장장치와 회사 공유 네트워크 드라이브가 등장합니다.

1. 사용자의 UsrClass.dat 와 NTUSER.DAT 에서 셸백 경로를 모두 뽑습니다. 첫 아이템이 볼륨·네트워크 위치·URI·위임 폴더인 경로를 따로 나눕니다.
2. 드라이브 문자로 시작하는 경로마다, 같은 시기에 그 문자를 받은 장치를 MountedDevices 와 장치 연결 시각으로 짝지어 봅니다. 짝이 둘 이상 나오면 무엇으로 좁힐 수 있습니까?
3. 네트워크 위치 아이템의 서버·공유 이름을 적습니다. 매핑 드라이브 기록과 이름이 맞습니까?
4. `.zip` 아래로 이어지는 경로가 있으면 압축 폴더 아이템의 형식(XP 형식인지 Windows 10 형식인지)을 먼저 확인합니다. 크기·CRC-32·수정 시각을 적을 수 있는 형식입니까? 그 ZIP 파일이 디스크에 아직 있습니까?
5. 한 경로에 대해 도구 두 개의 결과를 비교합니다. 경로가 다르게 나오면 원시 바이트에서 어떤 아이템 때문인지 찾습니다.

## 참고 문헌

- J. B. Metz, "Windows Shell Item format", libfwsi 문서 — https://github.com/libyal/libfwsi/blob/main/documentation/Windows%20Shell%20Item%20format.asciidoc
- Microsoft Learn, "Introduction to the Shell Namespace" — https://learn.microsoft.com/en-us/windows/win32/shell/namespace-intro
- Microsoft Learn, "File Times" — https://learn.microsoft.com/en-us/windows/win32/sysinfo/file-times
- 4n6k (Dan Pullega), "Shellbags Forensics: Addressing a Misconception", 2013 — https://www.4n6k.com/2013/12/shellbags-forensics-addressing.html
