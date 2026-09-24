# 로그 (ODL·ODLGZ)

## 한 줄 요약

OneDrive 동기화 앱은 `logs` 폴더에 ODL 이라는 이진 로그를 남깁니다. 로그 한 줄은 "어느 소스 파일의 어느 함수가 불렸고, 어떤 값을 넘겼는지" 입니다. 파일·폴더 이름 같은 값은 가려져 있어서, 같은 폴더의 키 파일로 풀어야 읽을 수 있습니다.

> **(관찰)** 표시는 Windows 11 빌드 26200 에 OneDrive 26.168.0830.0006 이 깔린 PC 한 대에서 직접 본 내용입니다. 이 PC 에는 개인 계정 1개와 회사 계정 1개가 연결돼 있었습니다. 다른 PC 와 다른 앱 버전에서는 다를 수 있습니다. 표시가 없는 내용은 공개 자료에서 확인한 것입니다.

## 무엇을 기록하나 · 왜 생기나

- ODL 은 OneDrive 앱이 부른 주요 함수의 기록입니다.
- 레코드마다 시각, 소스 코드 파일 이름, 함수 이름, 그 함수에 넘긴 값이 들어 있습니다.
- 그래서 올리기·내려받기·동기화가 있었음을 보이거나, 지운 항목을 찾는 데 쓸 수 있습니다.
- 넘긴 값 부분은 형식이 다 밝혀지지 않았습니다.
- 파일·폴더 이름, URL, 사용자 이름은 가려서 적습니다. 가리는 방식은 앱 버전에 따라 다릅니다(아래 "가려진 이름 풀기").

## 위치와 버전별 차이

### 폴더

| OS | 위치 |
|---|---|
| Windows | `C:\Users\<USER>\AppData\Local\Microsoft\OneDrive\logs\` |
| macOS | `/Users/<USER>/Library/Logs/OneDrive/` |

- Windows 에서는 `logs\` 아래에 `Common`, `Business1`, `Personal` 하위 폴더가 흔히 있습니다.
- 관찰한 PC 에는 `logs\ListSync\Business1` 과 `logs\ListSync\Consumer_<16자리 16진수>` 폴더도 있었습니다 (관찰).
- 같은 폴더에는 `general.keystore`, `SyncDiagnostics.log`, `telemetryCache.otc`(와 `-wal`·`-shm`), `DeviceHealthSummaryConfiguration.ini` 도 있었습니다 (관찰).
- 관찰한 PC 에는 `ObfuscationStringMap.txt` 가 없었습니다 (관찰).

### 파일 종류

| 확장자 | 내용 |
|---|---|
| `.odl` | 지금 쓰고 있는 로그 |
| `.odlgz` | 오래된 로그를 gzip 으로 압축한 것 |
| `.odlsent`, `.aodl` | 일부 폴더와 버전에서 보이는 로그 |

공개 도구 문서(odl.py, OneDriveExplorer README, 2026-09 확인)는 지원 확장자를 `.odl`, `.odlgz`, `.odlsent`, `.aold` 로 적습니다. 관찰한 PC 디스크의 실제 확장자는 `.aold` 가 아니라 `.aodl` 이었습니다 (관찰). 파일을 모을 때 `.aodl`·`.aold` 두 표기를 모두 찾습니다.

### 관찰한 PC 의 파일

| 폴더 | 파일 |
|---|---|
| `logs\Personal`, `logs\Business1` | `SyncEngine-<YYYY-MM-DD>.<HHMM>.<PID>.<순번>.odlsent` 여러 개와 같은 형식의 `.aodl` 1개 |
| `logs\Common` | `FileCoAuth-….odl`, `OneDriveLauncher-….odl` |
| `logs\ListSync\Business1` | `Nucleus-….odlgz` |
| `logs\ListSync\Consumer_<16자리>` | `NucleusPersonal-….odlgz` |

- `.odlgz` 는 `ListSync` 아래에서만 보였고, 모두 23개였습니다 (관찰).
- 파일 이름의 날짜·시각은 UTC 였습니다 (관찰). 이름이 `0714` 인 파일의 첫 레코드 시각이 07:14:51 UTC 였고, PC 시간대는 UTC+9 였습니다.
- 파일 이름의 PID 자리는 실행 중이던 `OneDrive.exe` 의 프로세스 ID 와 같았습니다 (관찰).
- 남아 있던 기간은 `Personal`·`Business1` 이 4~5일 치, `Common` 이 약 4주 치였습니다 (관찰). 지우는 규칙은 확인하지 못했습니다.

### 버전에 따른 차이

| 항목 | 옛 모습 | 새 모습 |
|---|---|---|
| 파일 머리의 `odl_version` | 2 (2022년 2월 블로그 당시 관찰값) | 3 (관찰) |
| 레코드 머리 | 56바이트 (버전 2) | 32바이트 (버전 3) |
| 이름 가리기 | `ObfuscationStringMap.txt` 사전 | AES 암호화. 키는 `general.keystore` (적어도 2022년 4월 이후 버전) |

## 구조

> 그림 자리: ODL 파일 하나를 파일 머리(0x100바이트) → (압축된 경우 gzip 덩어리) → 레코드 머리 + 레코드 내용이 이어지는 모양으로 보여 주는 그림

### 파일 머리 (256바이트, 0x100)

| 오프셋 | 크기 | 이름 | 내용 |
|---|---|---|---|
| 0x00 | 8 | signature | 문자열 `EBFGONED` |
| 0x08 | 4 | odl_version | uint32. 위 버전 표 참고 |
| 0x0C | 4 | unknown | uint32. 관찰한 PC 에서 `.odlsent`·`.odlgz` 는 0xD7, `.aodl`·`.odl` 은 0xC7 이었습니다 (관찰). 뜻은 확인하지 못했습니다 |
| 0x10 | 8 | unknown | uint64. 값은 0 |
| 0x18 | 4 | unknown | uint32. 값은 1 |
| 0x1C | 0x40 | one_drive_version | 앱 버전 문자열. 관찰한 PC 에서는 `26.168.0830.0006` |
| 0x5C | 0x40 | windows_version | Windows 버전 문자열. 관찰한 PC 에서는 `10.0.26200` |
| 0x9C | 0x64 | reserved | 예약. 여기까지 합쳐 0x100바이트 |

### 압축

- `.odlgz` 는 파일 머리가 같고, 그 뒤에 gzip 덩어리 하나가 옵니다.
- odl.py 는 `1F 8B 08 00` 을 gzip 머리로 보고 zlib 로 풉니다.
- 관찰한 PC 에서는 `.odlsent` 도 0x100 자리에 `1F 8B 08 00` 이 있었습니다. 즉 압축돼 있었습니다 (관찰).
- `.aodl`·`.odl` 은 0x100 자리에 바로 레코드 머리 `CC DD EE FF` 가 있었습니다. 즉 압축돼 있지 않았습니다 (관찰).

확장자만 보고 압축 여부를 정하지 않습니다. 0x100 자리의 네 바이트를 먼저 봅니다.

### 레코드 머리 (0xCCDDEEFF)

파일 머리의 `odl_version` 에 따라 레코드 머리의 크기와 모양이 다릅니다.

**버전 3 (32바이트)**

| 오프셋 | 크기 | 이름 |
|---|---|---|
| 0x00 | 4 | signature `CC DD EE FF` |
| 0x04 | 2 | context_data_len (uint16) |
| 0x06 | 2 | unknown_flag (uint16) |
| 0x08 | 8 | timestamp (uint64, Unix 밀리초) |
| 0x10 | 4 | unk1 (uint32) |
| 0x14 | 4 | unk2 (uint32) |
| 0x18 | 4 | data_len (uint32) |
| 0x1C | 4 | reserved (uint32) |

**버전 2 (56바이트)**

| 오프셋 | 크기 | 이름 |
|---|---|---|
| 0x00 | 4 | signature `CC DD EE FF` |
| 0x04 | 4 | unknown_flag (uint32) |
| 0x08 | 8 | timestamp (uint64, Unix 밀리초) |
| 0x10 | 4 | unk1 (uint32) |
| 0x14 | 4 | unk2 (uint32) |
| 0x18 | 20 | unknown |
| 0x2C | 4 | one (uint32) |
| 0x30 | 4 | data_len (uint32) |
| 0x34 | 4 | reserved (uint32) |

### 레코드 내용

레코드 머리 뒤에 내용이 이어집니다. 앞부분은 아래 순서입니다.

| 순서 | 항목 |
|---|---|
| 1 | code_file_name_len (uint32) |
| 2 | code_file_name (소스 코드 파일 이름) |
| 3 | unknown (uint32) |
| 4 | code_function_name_len (uint32) |
| 5 | code_function_name (함수 이름) |
| 6 | 함수에 넘긴 값. 형식이 다 밝혀지지 않았습니다 |

## 가려진 이름 풀기

### 옛 방식: ObfuscationStringMap.txt

- 파일·폴더 이름, URL, 사용자 이름을 사전 방식으로 가립니다.
- 짝이 되는 사전 파일이 `ObfuscationStringMap.txt` 입니다. 항목은 탭으로 나눕니다.
- 사전 파일 인코딩은 Windows 에서 UTF-16LE, macOS 에서 UTF-8 입니다.

이 사전을 쓸 때 조심할 점이 넷 있습니다.

- 확장자는 가리지 않습니다.
- 새 항목은 파일 맨 위에 붙습니다.
- 항목이 시간이 지나면 지워질 수 있습니다.
- 키를 다시 쓰므로, 같은 키가 다른 때에 다른 이름을 가리킬 수 있습니다.

### 새 방식: general.keystore 와 AES

- 적어도 2022년 4월 이후 버전은 사전을 쓰지 않습니다. 가릴 값을 AES 로 암호화합니다.
- 키는 `general.keystore` 에 있습니다. 이 파일은 JSON 이고, `"Key"`(base64)와 `"Version"` 칸이 있습니다.
- 푸는 법은 AES-CBC 입니다. IV 는 0 으로 채운 16바이트이고, 푼 뒤 끝의 패딩을 떼어 냅니다.
- 암호문 base64 는 `_` 를 `/` 로, `-` 를 `+` 로 바꾼 뒤 읽습니다.
- OneDriveExplorer 는 `general.keystore` 말고 `vault.keystore` 도 받습니다.
- 관찰한 PC 에서는 `logs\Personal`, `logs\Business1`, `logs\Common` 에 각각 `general.keystore` 가 있었습니다 (관찰). 내용은 보지 않았습니다.

키 파일이 없으면 이름과 경로를 풀 수 없습니다. 로그를 모을 때 같은 폴더의 `general.keystore`(있으면 `ObfuscationStringMap.txt`)를 반드시 함께 모읍니다.

## 증거로서 의미

### 증명하는 것

- 레코드 시각에 OneDrive 앱이 그 함수를 불렀습니다.
- 올리기·내려받기·동기화 관련 함수가 불린 기록이 있으면 그 시각에 그런 작업이 있었다는 근거가 됩니다.
- 키로 푼 이름이 있으면 그 작업이 어느 파일·폴더와 관련됐는지 좁힐 수 있습니다.
- 지운 항목을 찾는 단서가 됩니다.
- 파일 이름의 PID 로 그 로그를 쓴 `OneDrive.exe` 프로세스를 가릴 수 있습니다. 이름의 시각은 그 파일 첫 레코드 무렵의 UTC 시각이었습니다 (관찰).

### 증명하지 못하는 것

- 사용자가 직접 한 동작인지, 앱이 스스로 한 동기화인지는 함수 이름만으로 가리기 어렵습니다.
- 넘긴 값의 형식이 다 밝혀지지 않았습니다. 도구가 보여 주는 값의 뜻을 단정하지 않습니다.
- 키 파일이 없으면 어느 파일인지 알 수 없습니다.
- 로그가 없다고 활동이 없었던 것은 아닙니다. 관찰한 PC 에서도 계정 폴더 로그는 4~5일 치만 남아 있었습니다.

보고서에는 "파일 X 를 올렸다" 대신 이렇게 씁니다. "`logs\Business1` 의 ODL 에 Y(UTC) 시각 `<함수 이름>` 레코드가 있고, `general.keystore` 로 푼 이름은 X 이다."

## 시각 해석

| 값 | 형식 | 기준 |
|---|---|---|
| 레코드 머리의 `timestamp` | uint64, Unix 밀리초 | 1970-01-01 00:00 UTC 부터 센 밀리초. 변환하면 UTC 입니다 |
| 파일 이름의 날짜·시각 | `<YYYY-MM-DD>.<HHMM>` | UTC 였습니다 (관찰) |

- OneDrive 레지스트리와 동기화 DB 의 시각은 Unix **초** 입니다. 로그 레코드만 Unix **밀리초** 입니다. 한 시간 축에 놓을 때 단위를 맞춥니다.
- 파일 이름의 시각을 현지 시각으로 읽으면 시간대만큼 어긋납니다. 관찰한 PC 에서는 9시간 차이였습니다.
- 변환은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.

## 함정과 한계

- **확장자 표기가 문서와 디스크에서 다릅니다.** 도구 문서의 `.aold` 로만 찾으면 `.aodl` 을 놓칩니다. 도구가 `.aodl` 파일을 읽었는지도 확인합니다.
- **확장자로 압축 여부를 정하지 않습니다.** 관찰한 PC 에서는 `.odlsent` 도 압축돼 있었습니다.
- **키 파일을 빠뜨리지 않습니다.** 로그만 모으면 이름을 풀 수 없습니다.
- **사전 방식의 키는 다시 쓰입니다.** 옛 로그를 지금 사전으로 풀면 다른 이름이 나올 수 있습니다.
- **로그는 금방 지워집니다.** 사건 뒤 시간이 지났다면 [섀도 복사본 활용](/03-techniques/analysis/volume-shadow-copy-analysis.md) 이나 [삭제 데이터 복구](/03-techniques/analysis/data-recovery/index.md) 로 옛 로그 파일을 찾습니다.
- **형식이 앱 버전에 따라 바뀝니다.** 파일 머리의 `odl_version` 을 먼저 보고, 도구가 그 버전을 읽는지 확인합니다.
- **빈 곳을 짐작으로 채우지 않습니다.** 파일 머리의 unknown 칸과 레코드 머리의 unk 칸은 뜻을 확인하지 못했습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 odl.py 의 구조 정의로 만든 예시입니다. 특정 파일에서 나온 값이 아닙니다. `vv`·`uu` 는 버전과 unknown 칸 자리입니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000000  45 42 46 47 4F 4E 45 44 vv vv vv vv uu uu uu uu  EBFGONED........
   …      (0x1C 부터 앱 버전 문자열, 0x5C 부터 Windows 버전 문자열)
00000100  1F 8B 08 00 …                                     ← 압축된 파일: gzip 머리
00000100  CC DD EE FF …                                     ← 압축 안 된 파일: 첫 레코드 머리
```

1. 0x00 의 8바이트가 `EBFGONED` 인지 봅니다. 아니면 ODL 파일이 아닙니다.
2. 0x08 의 `odl_version` 으로 레코드 머리가 32바이트인지 56바이트인지 정합니다.
3. 0x100 의 네 바이트로 압축 여부를 가립니다. `1F 8B 08 00` 이면 그 뒤를 풀고 나서 레코드를 찾습니다.
4. 레코드 머리의 `timestamp` 를 Unix 밀리초로 바꿉니다. 예를 들어 1704067200000 이면 1000 으로 나눈 1704067200 초이고, 2024-01-01 00:00:00 UTC 입니다.

### 공개 도구로 한 번

- 공개 도구 odl.py(Yogesh Khatri)는 ODL 로그를 CSV 로 풀어 줍니다. 출력에는 함수 이름, 넘긴 값, 시각이 들어 있습니다.
- 공개 도구 OneDriveExplorer 는 ODL 로그를 동기화 DB 의 항목과 엮어 보여 줍니다. `general.keystore` 와 `vault.keystore` 를 받아 이름을 풉니다.
- 도구를 돌리기 전에 `logs` 폴더를 하위 폴더째 사본으로 뜹니다. 확장자 표기가 다른 파일까지 도구가 읽었는지 파일 수로 확인합니다.
- 도구가 보여 준 첫 레코드 시각을 위 헥스 절차로 한 번 직접 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 동기화 DB | 로그 시각 무렵의 서비스 작업 기록과 파일 행을 봅니다 | [동기화 DB](/02-artifacts/cloud-notes/onedrive/syncenginedatabase-db.md) |
| 계정·설정 레지스트리 | 로그 폴더(`Personal`·`Business1`)가 어느 계정 것인지 봅니다 | [계정·설정 레지스트리](/02-artifacts/cloud-notes/onedrive/accounts-settings.md) |
| 회사 계정 | `logs\Business1`·`ListSync` 로그를 조직 계정과 이어 봅니다 | [회사용 OneDrive와 SharePoint 동기화](/02-artifacts/cloud-notes/onedrive/business-tenant.md) |
| 프로세스 생성 | 파일 이름의 PID 와 시각이 `OneDrive.exe` 실행 기록과 맞는지 봅니다 | [프로세스 생성](/02-artifacts/event-logs/4688.md) |
| 프리페치 | `OneDrive.exe` 가 언제 실행됐는지 봅니다 | [프리페치](/02-artifacts/execution/prefetch/index.md) |
| SRUM | 그 시간대에 `OneDrive.exe` 가 네트워크로 얼마나 주고받았는지 봅니다 | [SRUM](/02-artifacts/execution/system-resource-usage-monitor/index.md) |
| USN 변경 저널 | 로그 파일이 언제 생기고 지워졌는지 봅니다 | [USN 변경 저널](/02-artifacts/filesystem/usnjrnl.md) |

## 실습

OneDrive 를 쓴 공개 검체(NIST CFReDS 등)에서 사용자의 `AppData\Local\Microsoft\OneDrive\logs` 폴더를 통째로 꺼내 아래 질문을 풀어 봅니다.

1. 하위 폴더마다 확장자별 파일 수는 몇 개입니까? `.aodl` 과 `.aold` 가운데 어느 표기입니까?
2. 파일 하나를 골라 0x08 의 `odl_version` 과 0x1C·0x5C 의 버전 문자열을 읽습니다.
3. 0x100 자리의 네 바이트로 압축된 파일과 압축 안 된 파일을 나눕니다. 확장자와 맞습니까?
4. `general.keystore` 와 `ObfuscationStringMap.txt` 가운데 무엇이 있습니까?
5. 파일 이름의 시각과 그 파일 첫 레코드의 시각을 비교합니다. 둘 다 UTC 로 보면 몇 초 차이입니까?
6. 가장 오래된 로그와 가장 최근 로그는 며칠 차이입니까? 폴더마다 다릅니까?

## 참고 문헌

1. Yogesh Khatri, "Reading OneDrive Logs" (Swift Forensics, 2022-02) — https://www.swiftforensics.com/2022/02/reading-onedrive-logs.html
2. ydkhatri/OneDrive, odl.py 소스 — https://raw.githubusercontent.com/ydkhatri/OneDrive/main/odl.py
3. ydkhatri/OneDrive, README (OneDrive .ODL Parser) — https://github.com/ydkhatri/OneDrive
4. Beercow/OneDriveExplorer, README — https://github.com/Beercow/OneDriveExplorer
