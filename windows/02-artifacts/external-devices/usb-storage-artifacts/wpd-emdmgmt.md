# 휴대용 장치·볼륨 이름 기록 (WPD·EMDMgmt)

## 한 줄 요약

SOFTWARE 하이브의 `Windows Portable Devices\Devices` 키와 `EMDMgmt` 키에는 USB 저장장치의 일련번호가 볼륨 정보와 함께 남습니다. 앞의 키에서는 볼륨 이름을 찾고, 뒤의 키에서는 볼륨 이름과 볼륨 일련번호를 찾습니다. 이 값들로 SYSTEM 하이브에 남은 장치를 LNK·점프리스트에 남은 볼륨과 잇습니다. 연결 시각은 이 두 키만으로 알 수 없습니다.

## 무엇을 기록하나 · 왜 생기나

### WPD

- 휴대용 장치 (Windows Portable Devices, WPD) 는 PC 가 연결된 장치와 데이터를 주고받게 하는 Windows 구성 요소입니다.
- Microsoft 는 WPD 가 다루는 장치로 음악 플레이어, 저장장치, 휴대전화, 카메라를 듭니다.
- USB 저장장치를 꽂으면 그 볼륨이 WPD 장치로도 한 번 더 등록됩니다. Windows 10 관찰 사례에서 Amcache 에 WPD 클래스 항목이 따로 생긴 것이 그 흔적입니다([장치 항목 (InventoryDevicePnp)](../../execution/amcache-hve/inventorydevicepnp.md)).
- 이때 SOFTWARE 하이브의 `Windows Portable Devices\Devices` 아래에 장치마다 하위 키가 생깁니다. 값 `FriendlyName` 에는 사람이 보는 이름이 들어갑니다.
- SANS 가 2009년에 낸 Windows Vista 용 USB 분석 안내서는 이 키에서 일련번호로 장치를 찾아 드라이브 문자와 볼륨 이름을 확인하라고 적었습니다.

### EMDMgmt

- EMDMgmt 는 레디부스트 (ReadyBoost) 가 쓰는 키입니다.
- 레디부스트는 USB 메모리 같은 플래시 장치를 디스크 캐시로 쓰는 기능입니다. Windows Vista 에서 처음 나왔습니다.
- "EMD" 는 흔히 외부 메모리 장치 (External Memory Device) 의 줄임말로 풀이합니다. 이 풀이를 공식 문서로 확인하지는 못했습니다.
- 플래시 장치를 꽂으면 레디부스트 서비스가 장치 성능을 검사합니다. 서비스는 검사 결과를 `EMDMgmt` 아래에 적습니다(Russinovich).
- 사용자가 그 장치를 레디부스트용으로 쓰지 않아도 하위 키는 생깁니다(Cowen, 확인 범위: Vista·7).
- USB 메모리만 남는 것이 아닙니다. eSATA·FireWire 장치와 시스템 디스크가 아닌 로컬 디스크도 남는다고 Cowen 이 적었습니다.
- 그래서 [USBSTOR 에 안 남는 장치](uasp-scsi-sd.md)의 볼륨을 찾을 때도 이 키를 봅니다.

## 위치와 버전별 차이

하이브 파일 위치는 [하이브 파일 종류와 위치](../../../01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md)를, `ControlSet00X` 를 고르는 법은 [컨트롤셋 고르기](../../../01-foundations/database-log-formats/registry-hive/controlset-select.md)를 봅니다.

| 기록 | 하이브와 경로 | 주로 보는 것 |
|---|---|---|
| WPD 장치 목록 | SOFTWARE `Microsoft\Windows Portable Devices\Devices\<장치 키>` | 하위 키 이름, `FriendlyName` |
| WPD 장치 인스턴스 | SYSTEM `ControlSet00X\Enum\SWD\WPDBUSENUM\<인스턴스 키>` | `FriendlyName`·`DeviceDesc`·`Mfg`, `Properties` 아래 장치 속성 |
| 레디부스트 검사 기록 | SOFTWARE `Microsoft\Windows NT\CurrentVersion\EMDMgmt\<장치·볼륨 키>` | 하위 키 이름, `LastTestedTime` |

| Windows | WPD 키 | EMDMgmt | 근거 |
|---|---|---|---|
| XP | SANS 의 XP 용 안내서는 이 키를 쓰지 않습니다. | 없습니다. 레디부스트가 Vista 에서 처음 나왔습니다. | SANS, Russinovich |
| Vista | 볼륨 이름과 드라이브 문자를 찾는 위치로 쓰였습니다. | 레디부스트와 함께 생깁니다. | SANS, Russinovich |
| 7 | 이 글의 자료로 판별 차이를 따로 확인하지 못했습니다. | 시스템 디스크가 SSD 이고 성능 기준을 넘으면 레디부스트를 끕니다. 이때 키가 비어 있을 수 있습니다. | Microsoft(E7 블로그), Cowen |
| 8 이후 (10·11) | 한 공개 플러그인은 2019~2020년 갱신판에서 `Enum\SWD\WPDBUSENUM` 을 읽습니다. | 이 글의 자료로 확인하지 못했습니다. 검체에서 키가 있는지부터 봅니다. | RegRipper 소스 |

- 같은 플러그인 소스에는 예전 경로 `Enum\WpdBusEnumRoot` 가 주석으로 남아 있습니다.
- 어느 판에서 경로가 바뀌었는지는 확인하지 못했습니다. SYSTEM 하이브에서는 두 경로를 모두 찾아봅니다.

## 구조

### Windows Portable Devices\Devices

- 장치 하나가 하위 키 하나입니다.
- 하위 키 이름에 제조사·모델·리비전·일련번호가 `#` 로 구분되어 들어 있습니다.
- 한 공개 플러그인(RegRipper `portdev`)은 이름을 `##` 또는 `??` 뒤에서 자릅니다. 그다음 `#` 로 나눠 둘째 조각을 장치 이름으로, 셋째 조각을 일련번호로 읽습니다.
- 값 `FriendlyName` 에 볼륨 이름이나 드라이브 문자가 들어갑니다.
- SANS 안내서는 여기서 두 가지를 모두 찾으라고 적었습니다. 초기 플러그인은 이 값을 드라이브 문자로 출력합니다.
- 어떤 경우에 둘 중 무엇이 들어가는지 정한 명세는 찾지 못했습니다.
- 이 키에는 볼륨 이름이 없는데 Amcache 의 WPD 항목에는 있던 사례가 있습니다. 이 키가 비어 있으면 [장치 항목 (InventoryDevicePnp)](../../execution/amcache-hve/inventorydevicepnp.md)을 봅니다.

### Enum\SWD\WPDBUSENUM

- 장치 인스턴스 ID (Device Instance ID) 하나가 하위 키 하나입니다.
- 공개 플러그인(RegRipper `wpdbusenum`)은 `FriendlyName`·`DeviceDesc`·`Mfg` 값을 읽습니다.
- `Properties\{83da6326-97a6-4088-9453-a1923f573b29}` 아래 속성 번호 0064~0067 에는 설치·연결·해제 시각이 있습니다. 뜻은 [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md)에서 다룹니다.
- SOFTWARE 쪽 `FriendlyName` 과 이 키의 `FriendlyName` 이 늘 같은지는 확인하지 못했습니다. 검체에서 두 값을 맞춰 봅니다.

> 그림 자리: USBSTOR 일련번호 하나가 WPD Devices 하위 키 이름, SWD\WPDBUSENUM 인스턴스 키 이름, EMDMgmt 하위 키 이름에 모두 들어 있고, EMDMgmt 끝의 볼륨 일련번호가 LNK 파일의 볼륨 일련번호와 이어지는 모습

### EMDMgmt 하위 키 이름

USB 저장장치의 하위 키 이름은 아래 모양입니다. 공개 플러그인(RegRipper `emdmgmt`)이 이름을 자르는 규칙에서 옮긴 것입니다.

```
_??_USBSTOR#<장치 이름>#<일련번호>#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}<볼륨 이름>_<볼륨 일련번호(10진)>
```

| 조각 | 뜻 |
|---|---|
| `_??_USBSTOR` | USB 저장장치라는 표시 |
| `<장치 이름>` | `Disk&Ven_…&Prod_…&Rev_…`. [USBSTOR](usbstor.md)의 장치 키 이름과 같은 모양입니다. |
| `<일련번호>` | USBSTOR 의 인스턴스 키 이름과 같은 모양입니다(끝의 `&0` 포함). |
| `{53f56307-…}` | 디스크 장치 인터페이스 GUID |
| `<볼륨 이름>` | 볼륨 이름(레이블)입니다. 비어 있을 수 있습니다. |
| `<볼륨 일련번호>` | 마지막 밑줄 뒤의 10진 숫자입니다. |

- 볼륨 일련번호 (Volume Serial Number, VSN) 는 파일시스템을 포맷할 때 정해지는 번호입니다. 볼륨 부트 섹터에 저장됩니다([FAT·exFAT 구조](../../../01-foundations/disk-volume/fat-exfat.md), [부트 섹터와 클러스터](../../../01-foundations/disk-volume/ntfs/boot-sector-cluster.md)).
- Windows 가 보여 주는 VSN 은 32비트(4바이트) 값입니다.
- 장치 펌웨어에 박힌 USB 일련번호와는 다른 번호입니다.
- 10진 값을 16진 8자리로 바꾸고 4자리씩 끊으면 `XXXX-XXXX` 모양이 됩니다. Windows 가 볼륨 일련번호를 보여 줄 때 쓰는 모양입니다.
- `_??_USBSTOR` 로 시작하지 않는 하위 키도 있습니다. 공개 플러그인은 이 경우 이름을 밑줄로 나눈 마지막 두 조각을 볼륨 이름과 VSN 으로 읽습니다.
- 값 `LastTestedTime` 은 8바이트입니다. 공개 플러그인은 이 값을 FILETIME 으로 풉니다.
- 나머지 값은 레디부스트가 잰 검사 결과입니다. 값 이름별 뜻은 이 글에서 명세로 확인하지 못했습니다.

## 증거로서 의미

### 증명하는 것

- EMDMgmt 에 하위 키가 있으면 볼륨 이름·VSN 이 그 값인 볼륨이 이 PC 에 연결된 적이 있습니다.
- 하위 키가 `_??_USBSTOR` 형식이면 그 볼륨이 어느 장치(제조사·모델·일련번호)에 있었는지도 함께 알 수 있습니다.
- VSN 은 LNK 파일과 점프리스트에도 적힙니다. 그래서 사용자가 연 파일이 어느 USB 장치에 있었는지 이을 수 있습니다.
- Cowen 은 MountPoints2 말고는 이 키가 장치와 LNK 속 VSN·볼륨 이름을 잇는 유일한 키라고 적었습니다(2013년 글).
- WPD 키에서는 장치 일련번호와 볼륨 이름(또는 드라이브 문자)의 짝을 얻습니다.
- 두 키는 SOFTWARE 하이브에 있습니다. SYSTEM 하이브의 USB 흔적만 정리한 경우 이 키들은 남아 있을 수 있습니다.

### 증명하지 못하는 것

- 연결 시각, 해제 시각, 연결 횟수를 알 수 없습니다.
- 누가 꽂았는지 알 수 없습니다. SOFTWARE 하이브는 사용자별 파일이 아닙니다. 사용자는 [사용자별 장치 연결 (MountPoints2)](mountpoints2.md)에서 찾습니다.
- 장치에서 파일을 복사하거나 열었는지 알 수 없습니다.
- 볼륨 이름은 기록할 때의 이름입니다. 뒤에 이름을 바꿨을 수 있습니다.
- VSN 이 같다고 같은 물리 장치라고 단정할 수 없습니다. VSN 은 부트 섹터에 있는 값이라서 섹터 단위로 복제하면 그대로 따라가고, 부트 섹터를 고치면 바뀝니다.
- 키가 없다고 연결이 없었다는 뜻은 아닙니다. 아래 "함정과 한계" 1번을 봅니다.

### 보고서 문장 예

- 쓰지 않을 문장: "사용자는 1234-ABCD USB 로 문서를 복사했다."
- 쓸 문장: "SOFTWARE 하이브 EMDMgmt 에 일련번호 ○○○ 인 USB 저장장치와 볼륨 이름 ○○·볼륨 일련번호 1234-ABCD 를 함께 적은 하위 키가 있다. 같은 볼륨 일련번호가 사용자 ○○ 의 LNK 파일 ○개에 있다. 이 기록은 해당 파일들이 볼륨 일련번호가 1234-ABCD 인 볼륨에 있었음을 보여 준다. 연결 시각과 복사 여부는 이 기록만으로 정할 수 없다."

## 시각 해석

| 시각 | 무엇이 바뀔 때 바뀌나 | 기준 |
|---|---|---|
| EMDMgmt 하위 키 마지막 기록 시각 | 여러 하위 키의 시각이 같거나 가까운 경우가 많습니다. 연결·해제가 아닌 다른 동작도 이 시각을 바꾼다고 봅니다(RegRipper 소스 주석). | UTC, FILETIME ([키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md)) |
| `LastTestedTime` 값 | 이름으로는 마지막 검사 때로 보이지만 명세는 없습니다. 관심 시간대와 크게 떨어진 경우가 많다고 보고됐습니다. 값이 0 일 수 있습니다. | 공개 플러그인은 FILETIME·UTC 로 풉니다. |
| WPD Devices 하위 키 마지막 기록 시각 | 무엇이 바뀔 때 바뀌는지 공개된 설명을 찾지 못했습니다. | UTC, FILETIME |
| SWD\WPDBUSENUM 장치 속성 0064~0067 | [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md)에서 다룹니다. | UTC, FILETIME |

- 이 페이지의 두 키에서 나온 시각은 연결 시각으로 쓰지 않습니다.
- 연결 시각은 교차 검증 표의 다른 아티팩트에서 정하고, 이 키들은 장치와 볼륨을 잇는 데 씁니다.

## 함정과 한계

1. **EMDMgmt 가 비어 있다고 지운 흔적으로 보는 실수.** Microsoft 는 시스템 디스크가 SSD 이고 성능 기준을 넘으면 Windows 7 이 레디부스트를 끈다고 밝혔습니다. Cowen 은 이 때문에 초보 분석가가 증거 인멸로 오판하기 쉽다고 적었습니다. 레디부스트 서비스를 첫 장치 연결 전에 꺼 둔 경우도 키가 비어 있을 수 있습니다(Cowen). Windows 8 이후 동작은 이 글에서 확인하지 못했습니다.
2. **VSN 을 10진 그대로 쓰는 실수.** LNK 도구와 `dir` 은 16진으로 보여 줍니다. 16진으로 바꿀 때 앞자리 0 을 채워 8자리로 맞춥니다. 한 공개 플러그인(`emdmgmt`)은 8자리가 안 되면 0 을 채우지 않고, 가운데 `-` 도 넣지 않은 채 그대로 냅니다(소스 기준).
3. **볼륨 이름에 밑줄이 있을 때.** 볼륨 이름과 VSN 은 밑줄로 이어져 있습니다. 볼륨 이름이 `MY_DATA` 처럼 밑줄을 품으면 도구가 이름과 VSN 을 잘못 자를 수 있습니다. VSN 은 마지막 밑줄 뒤 숫자로 직접 읽습니다.
4. **한 장치에 하위 키가 여럿.** 하위 키 이름에 볼륨 이름과 VSN 이 함께 들어갑니다. 그래서 장치를 다시 포맷하거나 이름을 바꾼 뒤 꽂으면 다른 하위 키가 생길 수 있습니다. 이 동작은 명세로 확인하지 못했습니다. 같은 일련번호로 하위 키가 여럿 있으면 각 VSN 을 따로 추적합니다.
5. **`FriendlyName` 을 볼륨 이름으로 단정하는 실수.** 드라이브 문자가 들어 있을 수 있습니다.
6. **속성 번호에 붙인 이름이 도구마다 다릅니다.** 한 공개 플러그인(`wpdbusenum`)은 0064 를 "First InstallDate", 0065 를 "InstallDate" 로 표시합니다(소스 기준). 이 위키의 [장치 항목](../../execution/amcache-hve/inventorydevicepnp.md) 페이지는 0064 를 `DEVPKEY_Device_InstallDate`, 0065 를 `DEVPKEY_Device_FirstInstallDate` 로 적었습니다. 도구 출력의 이름 대신 속성 번호로 확인합니다.
7. **지워진 하위 키.** 키가 없으면 [지워진 키·값 복구](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md), [트랜잭션 로그](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md), [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 속 옛 SOFTWARE 하이브를 봅니다.
8. **스마트폰.** Microsoft 는 휴대전화도 WPD 장치로 설명합니다. MTP 로 연결한 스마트폰이 이 키들에 어떻게 남는지는 [스마트폰으로 옮겼나](../../../04-scenarios/exfiltration/data-exfiltration/mtp-phone-link.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

1. SOFTWARE·SYSTEM 하이브와 각 `.LOG1`·`.LOG2` 를 사본으로 확보합니다.
2. [USBSTOR](usbstor.md)에서 조사할 장치의 일련번호를 정합니다.
3. SOFTWARE 하이브에서 일련번호를 ASCII 와 UTF-16LE 로 모두 찾습니다. 키 이름은 ASCII 로 저장되는 경우가 많습니다. 대소문자를 가리지 않고 찾습니다.
4. 걸린 nk 셀에서 부모 키를 따라 올라가 `EMDMgmt` 아래인지 `Devices` 아래인지 확인합니다. 셀 구조는 [하이브 내부 구조 (regf·hbin·Cell)](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)를 봅니다.
5. EMDMgmt 하위 키 이름 끝의 10진 숫자를 16진으로 바꿉니다.
6. Devices 하위 키에서 `FriendlyName` 의 vk 셀을 찾아 데이터 셀의 UTF-16LE 문자열을 읽습니다.
7. USB 장치의 이미지가 있으면 부트 섹터의 VSN 과 맞춰 봅니다. LNK 파일이 있으면 볼륨 정보의 일련번호와 맞춰 봅니다([바로가기 형식 (Shell Link·LNK)](../../../01-foundations/shell-document-formats/shell-link-lnk.md)).

아래는 공개 플러그인이 읽는 이름 규칙과 문자 인코딩 규칙으로 만든 예시입니다. 검체에서 나온 값이 아닙니다.

```
EMDMgmt 하위 키 이름 (만든 예시)
_??_USBSTOR#Disk&Ven_Generic&Prod_Flash_Disk&Rev_8.07#AB12CD34&0#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}WORK_305441741

장치 이름      Disk&Ven_Generic&Prod_Flash_Disk&Rev_8.07
일련번호       AB12CD34&0
볼륨 이름      WORK
VSN (10진)     305441741
VSN (16진)     0x1234ABCD  → 1234-ABCD
```

```
찾는 것                            바이트                              글자
VSN 10진 숫자 (키 이름, ASCII)      33 30 35 34 34 31 37 34 31          "305441741"
FriendlyName 데이터 (UTF-16LE)      57 00 4F 00 52 00 4B 00 00 00       "WORK" + 끝 표시
VSN 이 디스크에 놓인 모양 (리틀 엔디언) CD AB 34 12                      0x1234ABCD
```

- FAT·exFAT 부트 섹터와 LNK 파일은 VSN 을 리틀 엔디언 4바이트로 적습니다. 그래서 헥스 창에서는 `CD AB 34 12` 로 보입니다.
- NTFS 는 부트 섹터에 더 긴 값으로 적습니다. 어느 부분을 맞춰 볼지는 [부트 섹터와 클러스터](../../../01-foundations/disk-volume/ntfs/boot-sector-cluster.md)를 봅니다.
- 이 네 바이트를 USB 이미지와 LNK 파일에서 찾으면 세 기록을 한 줄로 이을 수 있습니다.

### 공개 도구로 한 번

- RegRipper 의 `emdmgmt`·`portdev` 플러그인은 SOFTWARE 하이브를, `wpdbusenum` 플러그인은 SYSTEM 하이브를 읽습니다.
- `emdmgmt` 는 장치 이름, 일련번호, 볼륨 이름, `XXXX-XXXX` 모양의 VSN, `LastTestedTime` 을 냅니다.
- 도구 결과를 헥스로 읽은 값과 맞춰 봅니다. 특히 함정 2·3·6번(앞자리 0, 밑줄, 속성 번호 이름)을 확인합니다.
- 레지스트리 뷰어로 키를 직접 열어 하위 키 이름 전체를 기록해 둡니다. 도구가 자른 결과만 보고서에 옮기지 않습니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 | 링크 |
|---|---|---|
| USBSTOR | 장치 이름과 일련번호 | [USB 저장장치 목록 (USBSTOR)](usbstor.md) |
| Enum\USB | VID·PID | [USB 장치 식별자 (Enum\USB VID·PID)](enum-usb-vid-pid.md) |
| MountedDevices | 드라이브 문자와 볼륨 GUID | [드라이브 문자 매핑 (MountedDevices)](mounteddevices.md) |
| MountPoints2 | 어느 사용자가 그 볼륨을 봤나 | [사용자별 장치 연결 (MountPoints2)](mountpoints2.md) |
| 장치 속성 시각 | 설치·연결·해제 시각 | [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md) |
| setupapi.dev.log | 처음 설치한 때 | [장치 설치 로그 (setupapi.dev.log)](setupapi-dev-log.md) |
| Amcache WPD 항목 | 볼륨 이름 | [장치 항목 (InventoryDevicePnp)](../../execution/amcache-hve/inventorydevicepnp.md) |
| LNK·점프리스트 | VSN·볼륨 이름으로 어떤 파일을 열었나 | [바로가기 파일 (LNK)](../../file-folder-usage/lnk.md), [점프리스트](../../file-folder-usage/jump-lists.md) |
| 셸백 | 외부 장치의 폴더를 탐색했나 | [외부 장치·네트워크·압축 폴더 탐색 흔적](../../file-folder-usage/shellbags/removable-network-zip.md) |
| 이벤트 로그 | 연결 이벤트 | [외부 장치 연결 이벤트](../../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) |

- 사용자가 장치를 레디부스트용으로 쓰기로 하면 장치 루트에 `ReadyBoost.sfcache` 파일이 생깁니다(Russinovich, Vista 기준 설명). USB 이미지가 있으면 이 파일이 있는지 봅니다.
- 전체 흐름은 [USB 로 무엇을 가져갔나](../../../04-scenarios/exfiltration/data-exfiltration/usb.md)에서 다룹니다.

## 실습

NIST CFReDS 의 "Data Leakage Case" 처럼 Windows 7 PC 와 USB 장치가 함께 나오는 공개 검체로 풀어 봅니다. 검체 설명에서 OS 판과 시스템 디스크 종류를 먼저 확인합니다.

1. EMDMgmt 하위 키를 모두 뽑아 `_??_USBSTOR` 형식과 나머지로 나눕니다. 나머지는 어떤 장치입니까?
2. 각 하위 키의 VSN 을 16진 `XXXX-XXXX` 로 바꿉니다. 같은 VSN 이 있는 LNK 파일·점프리스트 항목은 무엇입니까?
3. WPD Devices 의 `FriendlyName` 과 EMDMgmt 의 볼륨 이름을 장치마다 맞춰 봅니다. 다른 장치가 있다면 이유는 무엇일까요?
4. EMDMgmt 하위 키들의 마지막 기록 시각은 서로 얼마나 가깝습니까? 이 시각을 연결 시각으로 쓸 수 있습니까?
5. Windows 10 이상 검체가 있다면 `EMDMgmt` 와 `Enum\SWD\WPDBUSENUM` 이 있는지부터 확인합니다.

## 참고 문헌

1. Microsoft, "Windows Portable Devices", Microsoft Learn (Win32 apps). https://learn.microsoft.com/en-us/windows/win32/windows-portable-devices
2. Mark Russinovich, "Inside the Windows Vista Kernel: Part 2", TechNet Magazine, 2007년 3월 (Microsoft Learn 보관본). https://learn.microsoft.com/en-us/previous-versions/technet-magazine/cc162480(v=msdn.10)
3. Microsoft Engineering Windows 7 블로그, "Support and Q&A for Solid-State Drives", 2009-05-05 (Microsoft Learn 보관본). https://learn.microsoft.com/en-us/archive/blogs/e7/support-and-qa-for-solid-state-drives
4. Rob Lee, "Computer Forensic Guide To Profiling USB Device Thumbdrives on Win7, Vista, and XP", SANS DFIR 블로그, 2009-09-09, 첨부 안내서 USBKEY-Guide.pdf (Internet Archive 보관본으로 열람). https://web.archive.org/web/20191017152228/https://blogs.sans.org/computer-forensics/files/2009/09/USBKEY-Guide.pdf
5. David Cowen, "Daily Blog #65: Understanding the artifacts EMDMgmt", Hacking Exposed Computer Forensics Blog, 2013년 8월. https://www.hecfblog.com/2013/08/daily-blog-65-understanding-artifacts.html
6. Harlan Carvey, RegRipper 3.0 플러그인 소스 `emdmgmt.pl`·`portdev.pl`·`wpdbusenum.pl` (2026-09 열람).
   - https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/emdmgmt.pl
   - https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/portdev.pl
   - https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/wpdbusenum.pl
