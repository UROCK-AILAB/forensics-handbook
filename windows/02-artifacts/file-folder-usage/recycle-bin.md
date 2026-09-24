# 휴지통 (Recycle Bin)

> 위치: 아티팩트 사전 > 파일·폴더 사용 흔적

## 한 줄 요약

휴지통 (Recycle Bin) 은 탐색기 등에서 지운 파일을 바로 없애지 않고 옮겨 두는 숨은 폴더입니다. Windows Vista 부터는 지운 항목마다 파일이 두 개 생깁니다. 내용은 `$R` 파일에 남습니다. 원래 경로·크기·지운 시각은 `$I` 파일에 남습니다. 폴더가 사용자 SID 별로 나뉘므로 어느 계정의 휴지통인지 알 수 있습니다. Windows XP 까지는 항목 정보를 INFO2 라는 파일 하나에 모아 적었습니다.

이 페이지에서 "지운 시각" 은 휴지통으로 옮긴 시각을 뜻합니다. "관찰" 이라고 적은 것은 Windows 11 25H2(빌드 26200) NTFS 볼륨 한 대에서 직접 시험한 결과입니다. 시험에서는 셸의 휴지통 보내기 기능으로 파일과 폴더를 지웠습니다. 되살릴 때는 셸의 복원 명령을 썼습니다.

## 무엇을 기록하나 · 왜 생기나

휴지통은 파일 시스템 기능이 아니라 셸 (Shell) 기능입니다. 프로그램이 셸 함수로 파일을 지울 때 되돌리기 정보를 남기라는 옵션(`FOF_ALLOWUNDO`)을 주면 파일이 휴지통으로 갑니다. 이 옵션을 줘도 파일 이름을 전체 경로로 주지 않으면 휴지통으로 가지 않습니다. 셸 함수에는 휴지통 대신 영구히 지울 때 경고를 띄우는 옵션(`FOF_WANTNUKEWARNING`)도 따로 있습니다. (Microsoft Learn)

그래서 같은 "삭제" 라도 휴지통을 거치는 경우와 거치지 않는 경우가 있습니다. 휴지통에 남는 것은 셸을 거쳐 휴지통으로 보낸 삭제뿐입니다.

휴지통으로 보낼 때 Windows 는 되살리기에 필요한 정보를 따로 적어 둡니다. (Jones, 2003)

- 원래 전체 경로
- 크기
- 휴지통으로 옮긴 시각
- XP 까지는 휴지통 안에서 쓰는 번호와 원래 드라이브 번호도 적습니다

Vista 이후에는 이 정보를 항목마다 `$I` 파일에 적습니다. 원래 파일은 이름이 바뀌어 `$R` 파일이 됩니다. XP 까지는 모든 항목의 정보를 INFO2 한 파일에 레코드로 이어 적었습니다.

## 위치와 버전별 차이

휴지통 폴더는 드라이브마다 루트에 따로 생깁니다. 폴더 이름과 구성은 Windows 버전과 파일 시스템에 따라 다릅니다.

| Windows | 파일 시스템 | 폴더 | 정보 파일 | 근거 |
|---|---|---|---|---|
| 95·98·Me | FAT | `\RECYCLED\` | INFO 또는 INFO2 한 파일. Me 의 레코드는 280바이트 | Jones, libyal |
| NT·2000·XP·2003 | NTFS | `\RECYCLER\<SID>\` | INFO2 한 파일. 레코드는 800바이트 (libyal 은 2000 이후로 적습니다. NT 는 확인한 자료에 없습니다) | Jones, libyal |
| NT·2000·XP·2003 | FAT | `\RECYCLED\` | 사용자를 나누지 않고 한 폴더에 모읍니다 | Chen |
| Vista·7·8·8.1 | NTFS | `\$Recycle.Bin\<SID>\` | 항목마다 `$I` 하나. 형식 버전 1 | libyal, RBCmd 시험 파일 |
| 10·11 | NTFS | `\$Recycle.Bin\<SID>\` | 항목마다 `$I` 하나. 형식 버전 2 | libyal, 관찰 |

- FAT 에는 파일마다 접근 권한을 거는 보안 정보가 없습니다. 그래서 FAT 드라이브에서는 모든 사용자의 항목이 `RECYCLED` 한 폴더에 모입니다. NTFS 에서는 SID 이름의 하위 폴더로 나눕니다. (Chen, 2006)
- 두 폴더 이름이 다른 까닭도 이것입니다. CONVERT 로 FAT 를 NTFS 로 바꾼 뒤 옛 폴더를 새 구조로 잘못 읽지 않게 하려고 이름을 달리했습니다. (Chen, 2006)
- Vista 이후 FAT·exFAT 볼륨에서 폴더가 어떻게 구성되는지 밝힌 자료는 찾지 못했습니다.
- USB 메모리 같은 이동식 매체와 네트워크 드라이브에서 지운 파일은 기본 설정에서 휴지통으로 가지 않는다고 널리 알려져 있습니다. 이 페이지에서는 직접 확인하지 못했습니다. 장치를 분석할 때는 그 볼륨 루트에 휴지통 폴더가 있는지부터 봅니다.
- SID 폴더 이름이 어느 계정인지는 [사용자 프로필 목록 (ProfileList)](/02-artifacts/system-account/profilelist.md) 과 [사용자 계정 (SAM)](/02-artifacts/system-account/sam.md) 에서 찾습니다. SID 읽는 법은 [윈도 식별자 형식](/01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에 있습니다.

관찰한 폴더 모습은 다음과 같습니다.

- `C:\$Recycle.Bin` 아래에 사용자 SID 폴더와 SYSTEM 계정(`S-1-5-18`) 폴더가 있었습니다.
- SID 폴더에는 숨김·시스템 속성이 붙어 있었습니다.
- SID 폴더 안에 `desktop.ini` 가 있었습니다. 이 파일에는 휴지통 CLSID `{645FF040-5081-101B-9F08-00AA002F954E}` 가 적혀 있었습니다.

### 볼륨별 설정 (레지스트리)

휴지통 설정은 사용자 하이브(NTUSER.DAT)에 볼륨별로 남습니다. 아래는 관찰입니다.

| 항목 | 관찰 내용 |
|---|---|
| 키 | `Software\Microsoft\Windows\CurrentVersion\Explorer\BitBucket\Volume\{볼륨 GUID}` |
| 값 | `MaxCapacity`(REG_DWORD), `NukeOnDelete`(REG_DWORD) |
| C: 의 `MaxCapacity` | 볼륨 크기의 5% 남짓을 MB 로 적은 값과 비슷했습니다 |
| 키 개수 | 지금 붙어 있는 볼륨보다 많았습니다. 지금 없는 볼륨 GUID 의 키가 8개 남아 있었습니다 |

- `NukeOnDelete` 는 1 이면 그 볼륨에서 지운 파일이 휴지통을 거치지 않는 설정으로 알려져 있습니다. 이 페이지에서 값을 바꿔 시험하지는 않았습니다.
- 지금 없는 볼륨의 키는 예전에 붙었던 볼륨의 실마리가 됩니다. 볼륨 GUID 는 [드라이브 문자 매핑 (MountedDevices)](/02-artifacts/external-devices/usb-storage-artifacts/mounteddevices.md) 과 맞춰 봅니다.
- 키가 언제 바뀌었는지는 [키 마지막 기록 시각](/01-foundations/database-log-formats/registry-hive/last-write-time.md) 으로 봅니다. 이 시각이 무엇을 뜻하는지 밝힌 자료는 찾지 못했습니다.

## 구조

숫자는 모두 리틀 엔디언입니다. 시각은 모두 UTC 기준 FILETIME 입니다. FILETIME 읽는 법은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.

### INFO2 (Windows XP 까지)

파일 머리는 20바이트입니다. (libyal)

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0x00 | 4 | 알 수 없음. libyal 은 5 로 적었습니다 |
| 0x04 | 4 | 알 수 없음. 항목 개수로 추정합니다 |
| 0x08 | 4 | 알 수 없음. 이전 항목 개수로 추정합니다 |
| 0x0C | 4 | 레코드 크기. 280 또는 800 |
| 0x10 | 4 | 알 수 없음 |

레코드는 0x14 부터 이어집니다. 2000 이후의 800바이트 레코드는 다음과 같습니다. (libyal, Jones)

| 레코드 안 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0x000 | 260 | 원래 경로. ANSI 문자열, 끝 표시 0 |
| 0x104 | 4 | 휴지통 안의 번호 |
| 0x108 | 4 | 원래 드라이브 번호. 0 은 A:, 1 은 B:, 2 는 C: |
| 0x10C | 8 | 지운 시각. FILETIME(UTC) |
| 0x114 | 4 | 크기 |
| 0x118 | 520 | 원래 경로. UTF-16LE, 끝 표시 `00 00` |

- 280바이트 레코드는 0x118 앞까지만 있습니다. UTF-16 경로가 없습니다. (libyal)
- Jones 는 레코드 시작을 0x10 으로 잡았습니다. 그래서 Jones 의 오프셋은 위 표보다 4 씩 큽니다. 파일 안의 실제 위치는 같습니다.
- 휴지통에 들어간 파일은 `DC1.TXT` 처럼 이름이 바뀝니다. 숫자는 INFO2 레코드의 번호와 같습니다. 확장자는 원래 것을 씁니다. (Jones)
- Jones 가 본 XP 에서 크기 칸은 클러스터 크기의 배수였습니다. 파일이 디스크에서 차지한 크기라는 뜻입니다. `dir` 이 보여 주는 크기와 다를 수 있습니다.
- 휴지통을 비우면 INFO2 를 빈 파일로 새로 만듭니다. 번호도 1 부터 다시 셉니다. (Jones)
- ANSI 경로는 그 PC 의 코드 페이지로 읽습니다. 한국어 Windows 라면 CP949 입니다. [문자 인코딩](/01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 을 참고합니다.

### $I 파일 (Vista 이후)

| 오프셋 | 크기 | 버전 1 (Vista~8.1) | 버전 2 (10·11) |
|---|---|---|---|
| 0x00 | 8 | 형식 버전 = 1 | 형식 버전 = 2 |
| 0x08 | 8 | 원래 크기 | 원래 크기 |
| 0x10 | 8 | 지운 시각. FILETIME(UTC) | 지운 시각. FILETIME(UTC) |
| 0x18 | 버전 1: 가변, 버전 2: 4 | 원래 경로 시작. UTF-16LE, 끝 표시 `00 00` | 경로 글자 수 |
| 0x1C | 가변 | — | 원래 경로. UTF-16LE, 끝 표시 `00 00` |

- 버전 1 은 Vista 에서, 버전 2 는 Windows 10 에서 생겼습니다. (libyal)
- 버전 1 에는 경로 길이 칸이 없습니다. 끝 표시가 나올 때까지 읽습니다.
- 공개 파서 RBCmd 저장소에 있는 Windows 7·8.1 시험 파일 9개는 모두 544바이트입니다. 그중 하나를 열어 보니 경로 뒤가 모두 0 이었습니다. 경로 자리를 520바이트(260자)로 잡고 남는 곳을 0 으로 채운 것으로 보입니다.
- 버전 2 는 경로 길이만큼만 적습니다. 그래서 파일 크기가 `28 + 글자 수 × 2` 바이트가 됩니다.
- 버전 2 의 글자 수에는 끝 표시가 들어갑니다. 관찰에서 132자 경로의 글자 수 칸은 133 이었습니다. 이 `$I` 파일은 294바이트였습니다.
- 관찰에서 크기 칸은 파일의 논리 크기였습니다. 5,000바이트 파일은 5,000 이었습니다.
- 폴더를 지우면 크기 칸에 안에 든 파일 크기의 합이 들어갔습니다(관찰). 100바이트와 3,000바이트 파일이 든 폴더는 3,100 이었습니다.

### $R 파일

- 이름은 `$R` 뒤에 6글자와 원래 확장자를 붙입니다. 짝이 되는 `$I` 는 6글자와 확장자가 같습니다. 예를 들어 `$RV1CL6F.txt` 의 짝은 `$IV1CL6F.txt` 입니다(관찰).
- 6글자는 원래 이름과 관계가 없었습니다. 관찰과 공개 시험 파일에서는 영문 대문자와 숫자였습니다.
- 내용은 원래 파일 그대로입니다.
- 폴더를 지우면 `$R` 도 폴더가 됩니다. 그 안의 파일과 하위 폴더는 원래 이름을 그대로 씁니다. `$I` 는 맨 위 폴더에 하나만 생깁니다(관찰). RBCmd 도 `$R` 폴더 안을 뒤져 파일 목록을 만듭니다.

관찰에서 `$R` 은 원래 파일과 파일 ID(MFT 레코드 번호와 순번)가 같았습니다. 복사가 아니라 이름과 부모 폴더만 바꾼 것입니다. 폴더도 같았습니다. `$I` 는 새로 만든 파일이라 새 파일 ID 를 받았습니다. MFT 레코드의 구조는 [MFT 레코드와 속성](/01-foundations/disk-volume/ntfs/file-record-attribute.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

- `$I` 에 적힌 경로에 그 이름의 파일이나 폴더가 있었다는 기록입니다.
- 그 항목을 `$I` 의 시각에 휴지통으로 옮겼다는 기록입니다.
- SID 폴더는 어느 계정의 휴지통인지 알려 줍니다.
- `$R` 이 남아 있으면 지운 파일의 내용을 그대로 얻습니다. 해시를 계산해 다른 곳에서 나온 파일과 맞춰 볼 수 있습니다.
- 같은 경로가 여러 `$I` 에 나오면 그 경로의 항목을 여러 번 휴지통에 넣은 것입니다.

### 증명하지 못하는 것

- 사람이 직접 지웠는지 알려 주지 않습니다. 어떤 프로그램이든 셸 함수로 파일을 휴지통에 보낼 수 있습니다.
- SID 는 계정만 가리킵니다. 그 계정을 그때 누가 썼는지는 [그 시각에 PC 를 쓴 사람이 누구인가](/04-scenarios/activity/user-attribution.md) 의 방법으로 따로 밝힙니다.
- 파일을 언제 만들었는지, 언제 열었는지는 `$I` 에 없습니다.
- 휴지통을 언제 비웠는지는 휴지통 안에 남지 않습니다.
- `$I` 가 없다고 해서 지우지 않았다고 볼 수 없습니다. 휴지통을 거치지 않는 삭제가 많습니다. 아래 "함정과 한계" 에 있습니다.
- `$I` 는 있는데 `$R` 이 없다고 해서 휴지통을 비웠다고 볼 수 없습니다. 관찰에서는 복원한 뒤에도 `$I` 가 남았습니다.
- XP 의 INFO2 크기는 디스크에서 차지한 크기입니다. 원래 파일의 정확한 크기가 아닐 수 있습니다.

보고서에는 기록이 말하는 만큼만 씁니다. 예를 들면 "사용자 ○○(SID …-1001)의 휴지통에 `$I○○○○○○.docx` 가 있다. 이 파일에는 원래 경로 ○○ 와 크기 ○○ 바이트, 휴지통으로 옮긴 시각 ○○(UTC)가 적혀 있다" 처럼 씁니다. "사용자가 파일을 지웠다" 라고 쓰려면 그 시각에 그 계정을 쓴 사람을 따로 밝혀야 합니다.

## 시각 해석

| 시각 | 있는 곳 | 뜻 | 확인 수준 |
|---|---|---|---|
| 지운 시각 | `$I` 0x10, INFO2 레코드 0x10C | 휴지통으로 옮긴 시각. UTC | 명세 |
| `$I` 의 만든 시각 | `$I` 의 $STANDARD_INFORMATION | 관찰에서 지운 시각 칸과 1 ms 안쪽으로 같았습니다 | 관찰 |
| `$R` 의 만든·수정 시각 | `$R` 의 $STANDARD_INFORMATION | 관찰에서 원래 파일 값 그대로였습니다. 지운 시각이 아닙니다 | 관찰 |
| `$R` 의 $FILE_NAME 시각 | `$R` 의 $FILE_NAME | 이름이 바뀔 때 새로 적힐 수 있습니다. 이 페이지에서는 확인하지 않았습니다 | 확인 전 |
| 비운 시각·복원 시각 | [$UsnJrnl](/02-artifacts/filesystem/usnjrnl.md) 의 `$I`·`$R` 삭제·이름 바꾸기 기록 | 휴지통 안에는 남지 않습니다. 저널에 남아 있어야 씁니다 | 추정 |

- 관찰에서 지운 시각 칸은 두 번 모두 밀리초 아래 자리가 0 이었습니다. `$I` 의 만든 시각과 1 ms 안쪽으로 어긋나는 것은 이 때문으로 보입니다.
- 지운 시각은 그때의 시스템 시계를 따릅니다. 시계를 바꿨다면 시각도 틀어집니다. [시스템 시각을 바꿨나](/04-scenarios/activity/anti-forensics/system-time-change.md) 를 참고합니다.
- 화면에 현지 시각으로 보여 줄 때는 [시간대 설정](/02-artifacts/system-account/time-zone.md) 을 확인합니다.
- `$R` 의 만든 시각이 지운 시각보다 한참 앞서는 것은 정상입니다. 두 벌의 시각이 이름 바꾸기에 어떻게 반응하는지는 [두 벌의 시각](/01-foundations/disk-volume/ntfs/standard-information-file-name.md) 과 [파일 시각 네 가지와 변화 규칙](/03-techniques/analysis/timeline/macb-timestamp-rules.md) 에서 다룹니다.

## 함정과 한계

1. **휴지통을 거치지 않는 삭제가 많습니다.** 아래 경우에는 `$I` 가 생기지 않습니다.
   - Shift+Delete 로 바로 지운 경우
   - 명령 프롬프트의 `del` 이나 프로그램이 파일 API 로 직접 지운 경우
   - 셸 함수에 되돌리기 옵션이나 전체 경로를 주지 않은 경우 (Microsoft Learn)
   - 볼륨 설정 `NukeOnDelete` 를 켠 경우
   - 기본 설정의 이동식 매체·네트워크 드라이브 (널리 알려진 내용이며 직접 확인하지 않았습니다)
2. **복원한 뒤에도 `$I` 가 남을 수 있습니다.** 관찰에서 셸 복원 명령을 쓰자 `$R` 은 원래 자리로 돌아갔습니다. 되돌아간 파일의 파일 ID 는 그대로였습니다. 그런데 `$I` 는 30초 넘게 지나도 남아 있었습니다. 한 번 시험한 결과입니다. 짝 없는 `$I` 는 비우기·복원·수동 삭제 가운데 무엇인지 $UsnJrnl 로 가립니다.
3. **셸 화면과 폴더 내용이 다릅니다.** 관찰에서 짝 없는 `$I` 는 셸이 보여 주는 휴지통 목록에 나오지 않았습니다. 휴지통 폴더 자체는 숨김·시스템 속성이라 보통 화면에 보이지 않습니다. 분석은 셸 화면이 아니라 폴더의 파일을 직접 읽어서 합니다.
4. **폴더 안의 파일에는 따로 `$I` 가 없습니다.** 폴더째 지우면 안의 파일은 맨 위 폴더의 `$I` 시각 하나만 씁니다. 안의 파일마다 지운 시각이 따로 남지 않습니다.
5. **비운 뒤에도 흔적이 남을 수 있습니다.** 관찰에서 198바이트짜리 `$I` 의 $DATA 는 MFT 레코드 안에 상주(Resident)했습니다. 이런 `$I` 는 비운 뒤에도 MFT 레코드가 다른 파일에 쓰이기 전까지 내용이 남을 수 있습니다. 544바이트인 버전 1 이 상주하는지는 확인하지 못했습니다. 상주 데이터는 [데이터 런과 상주·비상주 데이터](/01-foundations/disk-volume/ntfs/data-run-resident-non-resident.md) 에서 다룹니다.
6. **`$R` 복구는 저장 장치에 달려 있습니다.** 비운 `$R` 의 내용은 클러스터를 덮어쓰기 전까지만 되살릴 수 있습니다. SSD 는 TRIM 때문에 더 빨리 사라질 수 있습니다. [SSD TRIM과 복구 한계](/03-techniques/analysis/data-recovery/ssd-trim.md) 를 참고합니다.
7. **`$I` 는 고칠 수 있는 평범한 파일입니다.** 서명이나 체크섬이 없습니다. 권한만 있으면 만들거나 고칠 수 있습니다. `$I` 의 만든 시각, $UsnJrnl 기록, `$R` 의 MFT 레코드와 서로 맞는지 확인합니다.
8. **예전 판이 섀도 복사본에 있을 수 있습니다.** 이미 비운 `$I`·`$R` 이나 INFO2 의 예전 판이 남아 있을 수 있습니다. 방법은 [섀도 복사본 활용](/03-techniques/analysis/volume-shadow-copy-analysis.md) 에서 다룹니다.
9. **알려진 SID 가 아닐 수 있습니다.** 지금 프로필 목록에 없는 SID 폴더가 있으면 지운 계정이거나 다른 PC 의 계정일 수 있습니다. 외장 디스크를 다른 PC 에서 쓴 경우에도 생길 수 있습니다. 어느 쪽인지는 다른 기록으로 가립니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 버전 2 `$I` 예시입니다. 실제 검체에서 나온 값이 아닙니다. `C:\t\a.txt`(5,000바이트)를 2024-03-01 09:00:00 UTC 에 지웠다고 가정했습니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00   02 00 00 00 00 00 00 00 88 13 00 00 00 00 00 00
0x10   00 68 3A D7 B6 6B DA 01 0B 00 00 00 43 00 3A 00
0x20   5C 00 74 00 5C 00 61 00 2E 00 74 00 78 00 74 00
0x30   00 00
```

1. 0x00 의 8바이트는 2 입니다. 형식 버전 2 입니다.
2. 0x08 의 8바이트는 0x1388 입니다. 원래 크기 5,000바이트입니다.
3. 0x10 의 8바이트를 리틀 엔디언으로 읽으면 0x01DA6BB6D73A6800 입니다. FILETIME 으로 풀면 2024-03-01 09:00:00 UTC 입니다. 한국 시각으로는 18:00 입니다.
4. 0x18 의 4바이트는 0x0B 입니다. 끝 표시를 넣어 11글자입니다.
5. 0x1C 부터 22바이트(11 × 2)를 UTF-16LE 로 읽습니다. `C:\t\a.txt` 와 끝 표시 `00 00` 입니다.
6. 파일 크기는 28 + 22 = 50바이트(0x32)여야 합니다. 크기가 다르면 뒤에 무엇이 붙었는지 확인합니다.
7. 같은 폴더에서 6글자와 확장자가 같은 `$R` 을 찾습니다. `$R` 의 크기가 0x08 의 값과 맞는지 봅니다.

버전 1 이라면 0x18 에서 바로 경로가 시작합니다. 파일 전체는 544바이트입니다.

### 공개 도구로 한 번

공개 도구의 예로 Eric Zimmerman 의 RBCmd 가 있습니다. 이 도구는 `$I`(버전 1·2)와 INFO2 를 읽습니다. 소스 코드를 보면 형식 버전을 읽은 뒤 버전 1 은 끝 표시까지, 버전 2 는 글자 수만큼 경로를 읽습니다. `$R` 이 폴더이면 그 안의 파일 목록도 함께 보여 줍니다.

Velociraptor 의 `Windows.Forensics.RecycleBin` 수집 규칙은 `C:\$Recycle.Bin` 아래의 `$I` 파일을 찾아 읽습니다. 이 규칙의 설명은 할당된 `$I` 만 읽는다고 밝힙니다. 미할당 MFT 레코드에 남은 `$I` 는 따로 되살려야 합니다. INFO2 는 읽지 않습니다.

도구가 보여 주는 항목 수와 폴더 안의 `$I` 파일 수를 맞춰 봅니다. 짝 없는 `$I`·`$R` 을 도구가 어떻게 다루는지도 확인합니다. 차이가 나면 헥스로 돌아갑니다. 방법은 [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 점 |
|---|---|
| [USN 변경 저널 ($UsnJrnl)](/02-artifacts/filesystem/usnjrnl.md) | 원래 이름이 `$R` 이름으로 바뀐 기록, `$I` 가 생긴 기록, 비우거나 복원한 기록을 봅니다 |
| [마스터 파일 테이블 ($MFT)](/02-artifacts/filesystem/mft.md) | `$R` 의 레코드에서 원래 파일의 만든 시각을 봅니다. 미할당 레코드에서 비운 `$I` 를 찾습니다 |
| [NTFS 트랜잭션 로그 ($LogFile)](/02-artifacts/filesystem/logfile.md) | 짧은 기간의 이름 바꾸기·삭제 동작을 봅니다 |
| [폴더 인덱스와 슬랙 ($I30)](/02-artifacts/filesystem/i30.md) | SID 폴더의 인덱스 슬랙에 예전 `$I`·`$R` 이름이 남았는지 봅니다 |
| [바로가기 파일 (LNK)](/02-artifacts/file-folder-usage/lnk.md) | 지운 파일을 전에 열었는지 봅니다. `$I` 의 경로와 LNK 의 대상 경로를 맞춥니다 |
| [점프리스트 (Jump Lists)](/02-artifacts/file-folder-usage/jump-lists.md) | 어떤 프로그램으로 그 파일을 열었는지 봅니다 |
| [셸백 (ShellBags)](/02-artifacts/file-folder-usage/shellbags/index.md) | 지운 파일이 있던 폴더를 탐색한 흔적을 봅니다 |
| [썸네일 캐시 (thumbcache_*.db·Thumbs.db)](/02-artifacts/file-folder-usage/thumbcache-db-thumbs-db.md) | 지운 그림 파일의 작은 그림이 남았는지 봅니다 |
| [지운 파일·옛 파일 흔적 찾기](/02-artifacts/file-folder-usage/windows-search/deleted-file-traces.md) | 색인 DB 에 지운 파일의 속성이 남았는지 봅니다 |
| [파일 접근 감사 (4656·4663·4660)](/02-artifacts/event-logs/4656-4663-4660.md) | 감사 정책이 켜져 있으면 삭제 요청을 한 프로세스와 계정을 봅니다 |
| [파일 생성·삭제 (Sysmon 이벤트 11·23·26)](/02-artifacts/event-logs/sysmon/11-23-26.md) | Sysmon 이 있으면 파일 삭제 기록을 봅니다. 휴지통으로 옮긴 동작이 이 이벤트로 남는지는 확인하지 못했습니다 |
| [사용자 프로필 목록 (ProfileList)](/02-artifacts/system-account/profilelist.md) | SID 폴더가 어느 계정인지 봅니다 |

조사 전체 흐름은 [지운 파일의 흔적 찾기](/04-scenarios/activity/deleted-file-traces.md) 에서 다룹니다. 완전삭제 도구를 의심한다면 [완전삭제 도구를 썼나](/04-scenarios/activity/anti-forensics/wiping-tools.md) 도 함께 봅니다.

## 실습

NIST CFReDS 의 "Data Leakage Case" PC 이미지는 Windows 7 입니다. 이 이미지로 아래 질문을 풀어 봅니다.

1. `C:\$Recycle.Bin` 아래 SID 폴더는 몇 개입니까? 각 SID 는 어느 계정입니까?
2. `$I` 파일의 형식 버전과 크기는 무엇입니까? 모두 544바이트입니까?
3. 각 `$I` 의 지운 시각과 `$I` 파일 자체의 만든 시각이 맞습니까?
4. 짝이 없는 `$I` 나 `$R` 이 있습니까? 있다면 $UsnJrnl 로 까닭을 설명할 수 있습니까?
5. `$R` 의 MFT 레코드에서 $STANDARD_INFORMATION 과 $FILE_NAME 의 시각을 비교합니다. 어느 쪽이 지운 시각에 가깝습니까?
6. 휴지통이 비어 있다면 $MFT 의 미할당 레코드에서 `$I` 로 시작하는 이름을 찾을 수 있습니까?
7. 지운 파일의 원래 경로가 LNK·점프리스트·셸백에도 나옵니까?

Windows 10·11 의 버전 2 를 보려면 가상 머신을 하나 만들어 직접 시험합니다. 파일 하나와 폴더 하나를 휴지통에 보내고, 하나는 복원하고, 하나는 비웁니다. 그 뒤 `$I`·`$R` 과 $UsnJrnl 이 어떻게 바뀌었는지 기록합니다.

## 참고 문헌

- Joachim Metz, "Windows Recycle.Bin file formats" 와 "Windows Recycler file formats", libyal dtformats — https://github.com/libyal/dtformats/blob/main/documentation/Windows%20Recycle.Bin%20file%20formats.asciidoc , https://github.com/libyal/dtformats/blob/main/documentation/Windows%20Recycler%20file%20formats.asciidoc
- Keith J. Jones, "Forensic Analysis of Microsoft Windows Recycle Bin Records", Foundstone (2003) — https://abelcheung.github.io/rifiuti2/assets/Forensics_Recycle_Bin.pdf
- Raymond Chen, "Why does the Recycle Bin have different file system names on FAT and NTFS?", The Old New Thing (2006) — https://devblogs.microsoft.com/oldnewthing/?p=32453
- Microsoft Learn, "SHFILEOPSTRUCTW structure (shellapi.h)" — https://learn.microsoft.com/en-us/windows/win32/api/shellapi/ns-shellapi-shfileopstructw
- Eric Zimmerman, RBCmd 소스 코드와 시험 파일 (`RecycleBin/DollarI.cs`, `RecycleBin/Info2.cs`) — https://github.com/EricZimmerman/RBCmd
- Velociraptor, "Windows.Forensics.RecycleBin" — https://docs.velociraptor.app/artifact_references/pages/windows.forensics.recyclebin/
