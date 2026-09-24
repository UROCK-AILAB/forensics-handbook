# USB 저장장치 흔적 (USB Storage Artifacts)

## 한 줄 요약

USB 저장장치 흔적 (USB Storage Artifacts) 은 USB 메모리나 외장 디스크를 PC 에 꽂았을 때 윈도가 레지스트리와 로그 파일에 남기는 기록입니다. 기록은 한곳에 모여 있지 않고 SYSTEM·SOFTWARE·NTUSER.DAT 하이브와 `setupapi.dev.log` 에 흩어져 있습니다. 시리얼 번호와 볼륨 식별자로 이 기록들을 이어 붙이면 어떤 장치가 언제 어느 드라이브 문자로 붙었는지 알 수 있습니다.

## 왜 중요한가

- 자료 유출 조사에서 가장 먼저 보는 흔적입니다. 특정 장치가 이 PC 에 연결된 적이 있는지 알려 줍니다.
- 장치를 특정할 수 있습니다. 제조사·제품 이름·리비전과 시리얼 번호가 남습니다. 압수한 USB 메모리의 값과 맞춰 볼 수 있습니다.
- 시각이 여러 곳에 남습니다. Windows 8 부터는 장치 속성에 마지막 연결 시각과 마지막 해제 시각이 따로 남습니다.
- 드라이브 문자와 볼륨 식별자가 남습니다. 이 값으로 바로가기 파일이나 셸백에 남은 `E:\` 같은 경로를 실제 장치와 이을 수 있습니다.
- 사용자별 흔적이 따로 있습니다. SYSTEM 하이브에는 사용자 정보가 없어서, 사용자는 NTUSER.DAT 의 MountPoints2 로 좁힙니다.
- 장치를 뽑아도 기록은 지워지지 않습니다. 마운트 관리자 (Mount Manager) 는 볼륨이 빠진 뒤에도 그 볼륨의 이름을 레지스트리에 그대로 둡니다.

증명하지 못하는 것도 분명합니다.

- 연결 기록은 파일을 옮겼다는 증거가 아닙니다. 장치 안의 어떤 파일을 열었는지는 바로가기 파일·점프리스트·셸백 같은 다른 흔적으로 봅니다.
- 시각은 대부분 처음과 마지막만 남습니다. 그 사이에 몇 번 꽂았는지는 이 흔적만으로 알 수 없습니다. 이벤트 로그가 남아 있으면 그 사이 연결을 더 찾을 수 있습니다.
- 인스턴스 ID (Instance ID) 의 두 번째 글자가 `&` 이면 장치에 시리얼 번호가 없어서 윈도가 만든 값입니다. 이 값은 장치 자체의 번호가 아니므로 장치를 특정하는 근거로 약합니다.
- 모든 외부 저장장치가 USBSTOR 에 남지는 않습니다. UASP (USB Attached SCSI) 로 붙는 장치와 MTP (Media Transfer Protocol) 로 붙는 스마트폰은 다른 위치에 남습니다.
- 레지스트리 키의 마지막 기록 시각 (Last Write Time) 은 연결이 아닌 다른 일로도 바뀔 수 있습니다. 키 시각만으로 연결 시각을 단정하지 않습니다.
- 정리 도구로 키를 지울 수 있습니다. 이때는 `setupapi.dev.log`, 이벤트 로그, 하이브 안에 남은 지워진 키, 섀도 복사본에서 흔적을 다시 찾습니다.

## 한눈에 보기

> 그림 자리: USB 메모리 하나를 꽂았을 때 기록이 남는 곳(SYSTEM 의 USBSTOR·Enum\USB·장치 속성·DeviceClasses·MountedDevices, SOFTWARE 의 WPD·EMDMgmt, NTUSER.DAT 의 MountPoints2, setupapi.dev.log)과 이들을 잇는 열쇠(시리얼 번호·볼륨 GUID·볼륨 시리얼 번호)를 한 장에 보여 주는 그림

### 위치

SYSTEM 하이브의 `ControlSet00X` 는 오프라인 분석에서 어느 컨트롤셋을 볼지 먼저 골라야 합니다. 고르는 법은 [컨트롤셋 고르기](/01-foundations/database-log-formats/registry-hive/controlset-select.md) 에서 다룹니다. 하이브 파일이 디스크 어디에 있는지는 [하이브 파일 종류와 위치](/01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md) 를 봅니다.

| 흔적 | 하이브·위치 | 알려 주는 것 |
|---|---|---|
| USBSTOR | SYSTEM `ControlSet00X\Enum\USBSTOR\Disk&Ven_<제조사>&Prod_<제품>&Rev_<리비전>\<인스턴스 ID>` | 저장장치 종류·제조사·제품·리비전, 시리얼 번호 |
| Enum\USB | SYSTEM `ControlSet00X\Enum\USB\VID_<16진수 4자리>&PID_<16진수 4자리>\<인스턴스 ID>` | 제조사 코드 (VID)·제품 코드 (PID) |
| 장치 속성 시각 | USBSTOR 인스턴스 키 아래 `Properties\{83da6326-97a6-4088-9453-a1923f573b29}\0064`·`0065`·`0066`·`0067` | 마지막 설치·처음 설치·마지막 연결·마지막 해제 시각 |
| DeviceClasses | SYSTEM `ControlSet00X\Control\DeviceClasses\{53f56307-b6bf-11d0-94f2-00a0c91efb8b}` (디스크)·`{53f5630d-b6bf-11d0-94f2-00a0c91efb8b}` (볼륨) | 키 마지막 기록 시각으로 본 연결 무렵 |
| MountedDevices | SYSTEM `MountedDevices` | 드라이브 문자·볼륨 GUID 와 장치의 짝 |
| MountPoints2 | NTUSER.DAT `Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2` | 그 사용자 세션에 나타난 볼륨 GUID |
| setupapi.dev.log | `%SystemRoot%\INF\setupapi.dev.log` | 장치 드라이버를 설치한 기록 |
| WPD | SOFTWARE `Microsoft\Windows Portable Devices\Devices` | 장치의 표시 이름 (볼륨 이름·드라이브 문자) |
| EMDMgmt | SOFTWARE `Microsoft\Windows NT\CurrentVersion\EMDMgmt` | 볼륨 시리얼 번호·볼륨 이름 |

장치 속성 값 네 개의 뜻은 다음과 같습니다. 0064 는 마지막으로 설치한 시각입니다. 이 값은 드라이버를 업데이트할 때마다 바뀝니다. 0065 는 처음 설치한 시각입니다. 이 값은 드라이버를 업데이트해도 바뀌지 않습니다. 0066 은 마지막으로 연결한 시각이고, 0067 은 마지막으로 뺀 시각입니다.

### Windows 버전에 따라 달라지는 점

| 항목 | 남는 버전 | 버전별 차이 |
|---|---|---|
| USBSTOR·Enum\USB·MountedDevices·MountPoints2 | XP 부터 | 이 페이지에서 다루는 기본 위치는 같습니다. |
| setupapi.dev.log | Vista 부터 | Vista 부터 이 이름과 위치를 씁니다. |
| 장치 속성 0064·0065 | 7 부터 | 7 은 `{GUID}\00xx\00000000\Data` 에 값이 있습니다. 8 부터는 `{GUID}\00xx` 에 바로 있습니다. |
| 장치 속성 0066·0067 | 8 부터 (10·11 포함) | 7 에는 없습니다. 7 에서는 마지막 연결 시각을 다른 흔적으로 짐작해야 합니다. |
| WPD·EMDMgmt | Vista 부터 | 모든 PC 에 남지는 않습니다. 남는 조건은 하위 페이지에서 다룹니다. |

### 시각 기준

- 장치 속성 0064~0067 은 FILETIME 형식이고 UTC 입니다.
- 레지스트리 키의 마지막 기록 시각도 UTC 입니다. 이 시각이 무엇이 바뀔 때 바뀌는지는 [키 마지막 기록 시각](/01-foundations/database-log-formats/registry-hive/last-write-time.md) 에서 다룹니다.
- `setupapi.dev.log` 의 시각은 현지 시각입니다. 다른 흔적과 맞춰 보려면 [시간대 설정](/02-artifacts/system-account/time-zone.md) 을 확인해 UTC 로 바꿉니다.

### 이어 붙이는 열쇠

| 열쇠 | 어디와 어디를 잇나 |
|---|---|
| 인스턴스 ID (시리얼 번호) | USBSTOR ↔ Enum\USB ↔ DeviceClasses ↔ MountedDevices ↔ setupapi.dev.log |
| 볼륨 GUID (`Volume{GUID}`) | MountedDevices ↔ MountPoints2 |
| 볼륨 시리얼 번호 | EMDMgmt ↔ 바로가기 파일·프리페치의 볼륨 정보 |
| 드라이브 문자 | MountedDevices ↔ 바로가기 파일·점프리스트·셸백에 남은 경로 |

드라이브 문자는 장치를 뽑고 다른 장치를 꽂으면 다시 쓰입니다. 그래서 드라이브 문자 하나만으로 장치를 잇지 않고, 시각과 볼륨 식별자를 함께 맞춥니다.

## 읽는 순서

1. [USB 저장장치 목록 (USBSTOR)](/02-artifacts/external-devices/usb-storage-artifacts/usbstor.md) — 연결된 저장장치 목록을 읽습니다. 키 이름에서 제조사·제품·리비전을, 인스턴스 ID 에서 시리얼 번호를 꺼냅니다.
2. [USB 장치 식별자 (Enum\USB VID·PID)](/02-artifacts/external-devices/usb-storage-artifacts/enum-usb-vid-pid.md) — USBSTOR 항목과 같은 장치를 `Enum\USB` 에서 찾아 VID·PID 를 읽습니다. VID·PID 로 제조사와 제품을 다시 확인합니다.
3. [연결·해제 시각 (DeviceClasses·Device Properties 0064·0066·0067)](/02-artifacts/external-devices/usb-storage-artifacts/deviceclasses-device-properties-0064-0066-0067.md) — 장치 속성에 남은 설치·연결·해제 시각과 DeviceClasses 키 시각을 읽습니다. 버전마다 남는 값이 다른 점을 정리합니다.
4. [드라이브 문자 매핑 (MountedDevices)](/02-artifacts/external-devices/usb-storage-artifacts/mounteddevices.md) — 드라이브 문자와 볼륨 GUID 가 어느 장치를 가리키는지 값 데이터로 풀어 봅니다.
5. [사용자별 장치 연결 (MountPoints2)](/02-artifacts/external-devices/usb-storage-artifacts/mountpoints2.md) — 사용자 하이브에서 볼륨 GUID 를 찾아 장치가 어느 사용자 세션에 나타났는지 좁힙니다.
6. [장치 설치 로그 (setupapi.dev.log)](/02-artifacts/external-devices/usb-storage-artifacts/setupapi-dev-log.md) — 장치를 처음 설치한 기록을 텍스트 로그에서 찾습니다. 현지 시각을 UTC 로 바꾸는 법도 다룹니다.
7. [휴대용 장치·볼륨 이름 기록 (WPD·EMDMgmt)](/02-artifacts/external-devices/usb-storage-artifacts/wpd-emdmgmt.md) — 볼륨 이름과 볼륨 시리얼 번호를 SOFTWARE 하이브에서 읽습니다. 이 값을 바로가기 파일의 볼륨 정보와 맞춥니다.
8. [USBSTOR 에 안 남는 장치 (UASP·SCSI·SD 카드)](/02-artifacts/external-devices/usb-storage-artifacts/uasp-scsi-sd.md) — USBSTOR 에서 찾지 못하는 저장장치를 다룹니다. UASP 장치는 Usbstor.sys 대신 Uaspstor.sys 가 맡기 때문에 기록 위치가 다릅니다.

## 함께 볼 페이지

- [USB 로 무엇을 가져갔나 (USB)](/04-scenarios/exfiltration/data-exfiltration/usb.md) — 이 흔적들을 다른 아티팩트와 함께 읽는 조사 순서입니다.
- [스마트폰으로 옮겼나 (MTP·Phone Link)](/04-scenarios/exfiltration/data-exfiltration/mtp-phone-link.md) — USBSTOR 에 남지 않는 스마트폰 연결을 다룹니다.
- [외부 장치 연결 이벤트 (Partition/Diagnostic·Kernel-PnP·DriverFrameworks)](/02-artifacts/event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) — 처음과 마지막 사이의 연결을 이벤트 로그에서 찾습니다.
- [외부 장치·네트워크·압축 폴더 탐색 흔적](/02-artifacts/file-folder-usage/shellbags/removable-network-zip.md) — 장치 안의 폴더를 연 흔적입니다.
- [바로가기 파일 (LNK)](/02-artifacts/file-folder-usage/lnk.md) · [점프리스트 (Jump Lists)](/02-artifacts/file-folder-usage/jump-lists.md) — 장치 안의 파일을 연 흔적과 볼륨 시리얼 번호가 남습니다.
- [장치 항목 (InventoryDevicePnp)](/02-artifacts/execution/amcache-hve/inventorydevicepnp.md) — AmCache 에 따로 남는 장치 목록입니다.
- [지워진 키·값 복구 (Deleted Keys·Values)](/01-foundations/database-log-formats/registry-hive/deleted-keys-values.md) · [트랜잭션 로그와 반영 안 된 변경 (.LOG1·.LOG2)](/01-foundations/database-log-formats/registry-hive/log1-log2.md) — 정리 도구로 지운 USBSTOR 키를 되살립니다.
- [섀도 복사본 활용 (Volume Shadow Copy Analysis)](/03-techniques/analysis/volume-shadow-copy-analysis.md) — 예전 시점의 하이브에서 지금은 없는 장치 기록을 꺼냅니다.
- [시각 값 형식 (FILETIME·Unix·WebKit·DOS·OLE)](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) — 장치 속성의 FILETIME 값을 사람이 읽는 시각으로 바꿉니다.

## 참고 문헌

- Microsoft Learn, "DEVPKEY_Device_FirstInstallDate" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/devpkey-device-firstinstalldate
- Microsoft Learn, "Supporting Mount Manager Requests in a Storage Class Driver" — https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/supporting-mount-manager-requests-in-a-storage-class-driver
- Microsoft Learn, "SetupAPI Text Logs" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/setupapi-text-logs
- Yogesh Khatri, "Windows 8 New Registry Artifacts Part 1 - New Device Timestamps" (2013) — https://www.swiftforensics.com/2013/11/windows-8-new-registry-artifacts-part-1.html
- ForensicsWiki, "USB History Viewing" — https://forensics.wiki/usb_history_viewing/
- Harlan Carvey, RegRipper 3.0 플러그인 mp2.pl·emdmgmt.pl·portdev.pl — https://github.com/keydet89/RegRipper3.0/tree/master/plugins
