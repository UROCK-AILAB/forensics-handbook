---
title: "사용자 접근 로그 (UAL)"
parent: "아티팩트 · 네트워크"
nav_order: 2462
---

# 사용자 접근 로그 (User Access Logging, UAL)

사용자 접근 로그 (User Access Logging, UAL) 는 Windows Server 2012 부터 서버에 기본으로 켜져 있는 기능입니다. 어느 계정이 어느 IP 주소에서 파일 서버·AD DS·DHCP 같은 서버 역할에 몇 번 접근했는지를 해마다 모아 `C:\Windows\System32\LogFiles\Sum` 의 ESE 데이터베이스에 적습니다. 이벤트 로그가 덮어쓰이거나 지워진 뒤에도 최대 2~3년치 계정·주소·역할 조합이 남아 있을 수 있어서, 서버 침해 사고에서 측면 이동 경로와 처음 접근한 때를 찾는 데 씁니다. Windows 10·11 같은 클라이언트 Windows 에는 없습니다.

## 무엇을 기록하나 · 왜 생기나

UAL 은 원래 관리자가 서버 역할과 제품을 얼마나 많은 사용자·기기가 쓰는지 세어 라이선스를 관리하려고 만든 기능입니다[1]. 서비스 이름은 `UALSVC` 이고 표시 이름은 "User Access Logging Service" 입니다[2]. 설치 직후부터 따로 설정하지 않아도 거의 실시간으로 데이터를 모읍니다[1].

한 번 접근할 때마다 한 줄씩 쌓는 로그가 아니라 모아서 세는 기록입니다. 역할·사용자 이름·클라이언트 주소 조합마다 그 해에 처음 접근한 시각, 마지막으로 접근한 시각, 모두 몇 번 접근했는지, 날짜별로 몇 번 접근했는지를 적습니다[3]. 그래서 개별 접근 시각은 처음과 마지막 두 개만 남고, 그 사이는 날짜별 횟수로만 알 수 있습니다.

UAL 이 데이터를 받는 역할과 서비스는 아래와 같습니다[1].

| 분류 | 역할·서비스 |
|---|---|
| 디렉터리·인증서 | Active Directory 인증서 서비스 (AD CS), Active Directory 권한 관리 서비스 (AD RMS) |
| 파일·인쇄 | 파일 서비스, 인쇄 및 문서 서비스, BranchCache, FTP 서버, 팩스 서버 |
| 네트워크 | DHCP, DNS, 네트워크 정책 및 액세스 서비스, 라우팅 및 원격 액세스 (RRAS) |
| 그 밖 | Hyper-V, 웹 서버 (IIS), 메시지 큐 (MSMQ), Windows 배포 서비스 (WDS), Windows Server Update Services (WSUS) |

- 파일 서비스와 인쇄 및 문서 서비스는 기본 기능이 늘 설치되어 있어서, 역할을 따로 설치하지 않은 서버에도 이 두 역할이 나타납니다[2].
- DNS 와 Hyper-V 데이터는 24시간마다 모읍니다[1].
- IIS 는 `iisual.exe` 로 따로 켜야 UAL 에 기록됩니다[1]. 작업 폴더 (Work Folders) 도 기본으로 꺼져 있고, `HKLM\Software\Microsoft\Windows\CurrentVersion\SyncShareSrv` 의 `EnableWorkFoldersUAL` 값을 1 로 두어야 기록됩니다[2].
- 파일 서버 역할 레코드에는 SMB 접근이 남습니다[3]. 도메인 컨트롤러에서는 AD DS 역할 레코드에 도메인 계정과 컴퓨터 계정(`$` 로 끝나는 이름)이 함께 나타납니다[7].

## 위치와 버전별 차이

모든 파일은 `C:\Windows\System32\LogFiles\Sum` 한 폴더에 있습니다[2][3].

| 파일 | 담는 것 |
|---|---|
| `Current.mdb` | 올해 데이터를 지금 쓰고 있는 DB |
| `{GUID}.mdb` | 연도별 사본. 올해 사본 하나와 지난해·재작년 사본이 있을 수 있습니다[3] |
| `SystemIdentity.mdb` | 서버 정보, 역할 GUID 와 역할 이름 대응표, 연도별 사본 파일 목록 |
| 트랜잭션 로그·체크포인트 파일 | ESE 엔진이 쓰는 파일. DB 파일과 함께 수집합니다 |

- 서비스는 `Current.mdb` 를 24시간마다 `{GUID}.mdb` 로 복사하고, 1월 1일에 새 `{GUID}.mdb` 를 만듭니다[2]. 복사 간격은 `HKLM\System\CurrentControlSet\Control\WMI\AutoLogger\Sum` 의 `PollingInterval`(REG_DWORD, 밀리초) 값으로 바꿀 수 있고, 기본값은 24시간입니다[2]. 분석할 서버에 이 값이 있으면 기록해 둡니다.
- 몇 년치를 남기는지는 Microsoft 문서끼리 다릅니다. "Get Started" 문서는 최대 3년치를 저장할 수 있다고 적고[1], "Manage" 문서는 2년치를 남기고 2년이 지나면 처음 `{GUID}.mdb` 를 덮어쓴다고 적습니다[2]. 그래서 실제 보관 범위는 `SystemIdentity.mdb` 의 `CHAINED_DATABASES` 표에 적힌 연도와 폴더에 실제로 있는 파일로 확인합니다.
- Windows Server 2012 부터 기본으로 켜져 있습니다[2][6]. 역할 GUID 목록(`ROLE_IDS`)은 서버마다 설치된 역할과 제품에 따라 다릅니다.
- ESE 형식과 로그 파일 이름 규칙은 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md)에서 다룹니다. 이 폴더의 로그 기본 이름은 `svc` 입니다[5]. 실제 이름은 폴더 안 체크포인트 파일 이름으로 확인합니다.

## 구조

### SystemIdentity.mdb

| 표 | 주요 열 | 알려 주는 것 |
|---|---|---|
| `SYSTEM_IDENTITY` | `CreationTime`, `OSMajor`, `OSMinor`, `OSBuildNumber`, `SystemDNSHostName`, `SystemDomainName`, `OSLastBootUpTime` | 이 서버의 OS 버전·호스트 이름·도메인[3][5] |
| `ROLE_IDS` | `RoleGuid`, `ProductName`, `RoleName` | 역할 GUID 와 사람이 읽는 역할 이름의 대응[3][5] |
| `CHAINED_DATABASES` | `Year`, `FileName` | 연도별 `{GUID}.mdb` 파일 이름[3][5] |

### Current.mdb·{GUID}.mdb

| 표 | 주요 열 | 알려 주는 것 |
|---|---|---|
| `CLIENTS` | `RoleGuid`, `AuthenticatedUserName`, `Address`, `ClientName`, `TenantId`, `InsertDate`, `LastAccess`, `TotalAccesses`, `Day1`~`Day366` | 역할·사용자·주소 조합별 첫 접근, 마지막 접근, 총 횟수, 날짜별 횟수[3][5] |
| `ROLE_ACCESS` | `RoleGuid`, `FirstSeen`, `LastSeen` | 그 해에 역할마다 처음·마지막으로 쓰인 시각[3][5] |
| `DNS` | `Address`, `HostName`, `LastSeen` | DNS 서버 역할이 있는 서버에서 IP 주소와 호스트 이름의 대응[3][5] |
| `VIRTUALMACHINES` | `VmGuid`, `BIOSGuid`, `SerialNumber`, `CreationTime`, `LastSeenActive` | Hyper-V 호스트의 가상 머신 정보[3][5] |

`CLIENTS` 표의 열은 이렇게 읽습니다.

| 열 | 저장 형식 | 읽는 법 |
|---|---|---|
| `AuthenticatedUserName` | UTF-16 문자열 | `도메인\사용자` 형식입니다. 로컬 계정, 도메인 계정, 컴퓨터 계정이 모두 들어갑니다[3]. 비어 있는 레코드도 있습니다[4] |
| `Address` | 이진값 | 4바이트면 IPv4, 16바이트면 IPv6 입니다. 바이트 순서 그대로 읽습니다[4][5][6] |
| `RoleGuid` | GUID | `ROLE_IDS` 로 역할 이름을 찾습니다 |
| `InsertDate`·`LastAccess` | 8바이트 FILETIME | 그 해 첫 접근과 마지막 접근 시각입니다[3][4] |
| `TotalAccesses` | 32비트 부호 없는 정수 | 그 해 총 접근 횟수입니다[4] |
| `DayN` | 16비트 부호 없는 정수 | 그 해 N번째 날의 접근 횟수입니다. 접근이 없던 날은 값이 없습니다[4][5] |

날짜별 횟수는 하루 최대 65,535 번까지 셉니다[2].

주요 역할 GUID 는 아래와 같습니다[4]. 서버마다 다른 제품이 더 있을 수 있으므로 먼저 그 서버의 `ROLE_IDS` 를 봅니다.

| RoleGuid | 역할 |
|---|---|
| `{10A9226F-50EE-49D8-A393-9A501D47CE04}` | File Server |
| `{AD495FC3-0EAA-413D-BA7D-8B13FA7EC598}` | Active Directory Domain Services |
| `{C50FCC83-BC8D-4DF5-8A3D-89D7F80F074B}` | Active Directory Certificate Services |
| `{4AD13311-EC3B-447E-9056-14EDE9FA7052}` | Active Directory Lightweight Directory Services |
| `{48EED6B2-9CDC-4358-B5A5-8DEA3B2F3F6A}` | DHCP Server |
| `{952285D9-EDB7-4B6B-9D85-0C09E3DA0BBD}` | Remote Access |
| `{90E64AFA-70DB-4FEF-878B-7EB8C868F091}` | Remote Desktop Services |
| `{1479A8C1-9808-411E-9739-2D3C5923E86A}` | Remote Desktop Gateway |
| `{D6256CF7-98FB-4EB4-AA18-303F1DA1F770}` | Web Server |
| `{D8DC1C8E-EA13-49CE-9A68-C9DCA8DB8B33}` | Windows Server Update Services |
| `{BD7F7C0D-7C36-4721-AFA8-0BA700E26D9E}` | SQL Server Database Engine |
| `{7FB09BD3-7FE6-435E-8348-7D8AEFB6CEA3}` | Print and Document Services |

## 증거로서 의미

**증명하는 것**

- `CLIENTS` 레코드 하나는 그 해에 이 계정 이름으로 이 주소에서 이 역할에 요청이 들어온 기록입니다. 처음과 마지막 시각, 총 횟수가 함께 남습니다.
- `DayN` 값으로 어느 날에 몇 번 접근했는지 알 수 있습니다. 이벤트 로그가 남아 있지 않은 기간의 접근 날짜를 이것으로 찾을 수 있습니다.
- 컴퓨터 계정(`$` 로 끝나는 이름)의 레코드로 어느 컴퓨터 계정이 이 서버의 역할을 썼는지 알 수 있습니다. 어느 단말에서 왔는지는 주소가 루프백이 아닐 때만 알 수 있습니다(아래 함정 7 참고).
- `ROLE_ACCESS` 로 그 서버에서 어떤 역할이 언제부터 언제까지 쓰였는지 알 수 있습니다.
- 연도별 사본이 있으면 몇 해에 걸쳐 같은 계정·주소가 나타나는지 비교할 수 있습니다.

**증명하지 못하는 것**

- 무엇을 했는지는 남지 않습니다. 파일 서버 레코드가 있어도 어떤 공유나 파일을 열었는지는 알 수 없습니다. 파일 단위 기록은 [공유 폴더 접근 (5140·5145)](../event-logs/5140-5145.md)에서 찾습니다.
- 계정 이름은 요청을 인증한 계정입니다. 그 계정을 실제로 누가 썼는지는 알 수 없습니다.
- 주소는 서버가 본 클라이언트 주소입니다. NAT·VPN·프록시 뒤의 실제 단말은 이 기록만으로 알 수 없습니다.
- 처음과 마지막 사이의 개별 접근 시각, 로그온 세션의 길이는 남지 않습니다.
- 레코드가 없다고 접근이 없었던 것은 아닙니다. 서비스가 꺼져 있었거나, 역할이 UAL 에 기록하지 않거나(IIS 를 따로 켜지 않은 경우 등), 폴더가 새로 만들어졌을 수 있습니다(아래 함정 참고).

보고서에는 "`Current.mdb` 의 `CLIENTS` 표에 계정 `EXAMPLE\svc_backup` 이 주소 192.168.10.21 에서 File Server 역할에 2025-03-14 01:23:45 UTC 에 처음 접근하고 모두 37 번 접근한 기록이 있다. 이 기록에는 접근한 공유나 파일이 없다." 처럼 씁니다(만든 예시).

## 시각 해석

- `InsertDate`·`LastAccess`·`FirstSeen`·`LastSeen`·`CreationTime` 은 모두 8바이트 FILETIME 이고 UTC 입니다[3][4][5]. 읽는 법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에 있습니다.
- `InsertDate` 는 그 해에 그 조합이 처음 접근한 시각이고, `LastAccess` 는 그 해 마지막 접근 시각입니다[3]. 해가 바뀌면 새 DB 에 새 레코드가 생기므로, 여러 해에 걸친 첫 접근은 가장 오래된 연도 사본에서 찾습니다. 드물게 `InsertDate` 와 `LastAccess` 의 연도가 다른 레코드도 있어서, KStrike 는 이런 레코드의 날짜별 횟수에 날짜가 맞지 않을 수 있다는 경고를 붙입니다[4].
- `DayN` 의 N 은 1월 1일을 1로 세는 날짜 번호입니다. 예를 들어 `InsertDate` 가 2021-06-13 인 레코드는 `Day164` 에 값이 있습니다[7]. 날짜로 바꾸려면 그 DB 의 연도가 필요하고, 윤년에는 `Day60` 이 2월 29일, 평년에는 3월 1일입니다.
- `DayN` 에는 시각이 없어서 하루 안의 순서는 알 수 없습니다. 날짜 경계를 어느 시간대로 나누는지는 `InsertDate` 의 날짜와 값이 있는 첫 `DayN` 을 비교해 확인합니다. `InsertDate` 가 12월 31일 23시대(UTC)인데 `Day1` 에 값이 있는 레코드가 있을 수 있어서, KStrike 는 이때 연도를 하나 올려 날짜를 계산합니다[4].
- 올해 사본 `{GUID}.mdb` 는 `Current.mdb` 를 복사한 시점의 상태라서, 최근 하루 안팎의 접근은 `Current.mdb` 에만 있을 수 있습니다[2].
- 현지 시각으로 바꿀 때는 그 서버의 [시간대 설정](../system-account/time-zone.md)을 씁니다.

## 함정과 한계

1. **서버에만 있습니다.** UAL 은 Windows Server 2012 이후 서버에만 있고, Windows 10·11 같은 클라이언트 Windows 에는 없습니다[6]. 측면 이동을 볼 때 접근을 받은 서버 쪽 기록이고, 접근한 PC 쪽 기록이 아닙니다.
2. **비정상 종료 상태로 수집됩니다.** 서비스가 돌고 있는 서버에서 가져온 DB 는 대개 비정상 종료 상태입니다. JET API 로 여는 도구는 먼저 사본에서 복구해야 하고, 페이지를 직접 읽는 도구는 로그에만 있는 최근 변경을 보지 못합니다. 판단 기준과 복구 절차는 [트랜잭션 로그와 비정상 종료 상태](../../01-foundations/database-log-formats/extensible-storage-engine/edb-log-dirty-shutdown.md)에서 다룹니다.
3. **실행 중인 서버에서 파일을 옮기거나 고치지 않습니다.** 서비스는 시작할 때마다 소프트 복구를 하고, 파일로 시작하지 못하면 SUM 폴더의 파일을 모두 지운 뒤 새로 만듭니다[2]. 실행 중인 서버의 파일을 옮기거나 고치면 이 정리 과정이 돌 수 있습니다[2]. 수집은 [선별 수집](../../03-techniques/process-acquisition/evidence-acquisition/triage-collection.md)처럼 폴더를 통째로 읽기만 하는 방법을 씁니다.
4. **폴더가 새로 만들어졌을 수 있습니다.** 위 정리 과정이나 관리자가 파일을 지운 경우 기록이 그 시점부터 다시 시작합니다[2]. `SYSTEM_IDENTITY` 의 `CreationTime` 이 서버 설치 시각보다 한참 뒤라면 그 이유를 따로 확인합니다. 설치 시각은 [시스템 기본 정보](../system-account/os-version-computer-name-install-date-shutdown-t.md)에서 봅니다.
5. **서비스가 꺼져 있을 수 있습니다.** 관리자는 개인정보나 운영 이유로 `UALSVC` 를 멈추고 비활성화할 수 있습니다[2]. SYSTEM 하이브의 `Services\UALSVC` 의 `Start` 값과 `LastAccess` 가 끊긴 날짜를 함께 봅니다.
6. **같은 해 기록이 두 파일에 있습니다.** `Current.mdb` 와 올해 `{GUID}.mdb` 에 같은 조합이 함께 있을 수 있습니다. 여러 파일을 합칠 때 중복을 확인하고, 두 값이 다르면 `Current.mdb` 가 더 최근 상태입니다.
7. **루프백 주소 레코드가 있습니다.** AD DS 역할에서 주소가 127.0.0.1 인 레코드, 파일 서버 역할에서 `::1` 인 레코드가 나타납니다[7]. AD DS 역할의 127.0.0.1 레코드에는 그 서버의 컴퓨터 계정뿐 아니라 다른 컴퓨터 계정과 도메인 사용자 계정도 나타납니다[7]. 그래서 루프백 레코드를 원격 접근이 아니라고 바로 빼지 않고, 주소로는 요청한 단말을 알 수 없는 레코드로 보고 계정 이름을 도메인 인증 이벤트와 비교합니다.
8. **역할 이름이 비어 나올 수 있습니다.** `ROLE_IDS` 에 없는 GUID 는 도구가 이름을 붙이지 못합니다[7]. 위 GUID 표나 [4]의 목록으로 확인합니다.
9. **SumECmd 는 `Current.mdb` 의 날짜를 분석 PC 의 올해로 계산합니다.** 연도별 사본은 `CHAINED_DATABASES` 의 `Year` 를 쓰지만, `Current.mdb` 의 `DayN` 은 도구를 실행한 해의 1월 1일을 기준으로 날짜를 붙입니다[5]. 수집한 해와 분석하는 해가 다르면 `InsertDate` 의 연도로 날짜를 다시 계산합니다.
10. **IPv6 주소의 표시 방식이 도구마다 다릅니다.** SumECmd 는 2바이트씩 콜론으로 나눠 앞의 0을 줄이지 않고 보여 주고[5], KStrike 는 `fe80`·`2001` 로 시작하는 주소에서 인터페이스 ID 부분으로 MAC 주소를 계산해 함께 보여 줍니다[4]. 같은 주소를 문자열로 검색할 때는 원시 16진값으로 맞춥니다.

## 직접 분석해 보기

### 헥스로 한 번

`CLIENTS` 레코드의 열 값을 풉니다. ESE 페이지에서 레코드를 찾아가는 방법은 [파일 구조 (Page·B+Tree·Catalog)](../../01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md)에서 다룹니다. 아래 바이트는 모두 만든 예시입니다.

| 열 | 원시 바이트 | 읽는 법 | 값 |
|---|---|---|---|
| `Address` | `C0 A8 0A 15` | 4바이트라 IPv4. 한 바이트씩 10진으로 읽습니다 | 192.168.10.21 |
| `InsertDate` | `80 66 9A BA 7F 94 DB 01` | 리틀 엔디언 64비트 FILETIME | 2025-03-14 01:23:45 UTC |
| `Day73` | `25 00` | 리틀 엔디언 16비트 | 2025년 73번째 날(3월 14일)에 37번 |

같은 풀이를 파이썬으로 확인합니다.

```python
import struct, datetime
addr = bytes.fromhex("C0A80A15")                       # 만든 예시
print(".".join(str(b) for b in addr) if len(addr) == 4 else addr.hex())
ft = struct.unpack("<Q", bytes.fromhex("80669ABA7F94DB01"))[0]
print(datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=ft // 10))  # UTC
year, n = 2025, 73                                     # DB 연도와 DayN 의 N
print(datetime.date(year, 1, 1) + datetime.timedelta(days=n - 1))
```

### 공개 도구로 한 번

SumECmd 는 폴더를 통째로 받아 `SystemIdentity.mdb`·`Current.mdb`·연도별 사본을 차례로 읽고, 역할 이름을 붙여 CSV 로 냅니다[5]. JET API 로 열기 때문에 비정상 종료 DB 는 먼저 사본에서 복구합니다. 처리 중 오류가 나면 `esentutl /mh` 로 상태를 확인하라고 안내합니다[5].

```
SumECmd.exe -d "E:\case\Sum" --csv "E:\case\out"
```

결과 파일 이름은 실행 시각 뒤에 `_SumECmd_DETAIL_Clients_Output.csv` 처럼 표 이름이 붙습니다. 표 이름은 `Clients`, 날짜별로 한 줄씩 펼친 `ClientsDetailed`, `DnsInfo`, `RoleAccesses`, `VmInfo` 이고, `SystemIdentity.mdb` 의 내용은 `SUMMARY_SystemIdentInfo`·`SUMMARY_RoleInfos`·`SUMMARY_ChainedDbInfo` 로 나옵니다[5].

KStrike 는 JET API 를 거치지 않고 libesedb(pyesedb)로 파일을 직접 읽는 파이썬 스크립트입니다[4]. DB 파일 하나씩 넣고, 결과는 `||` 로 구분한 텍스트입니다. `DNS` 표의 호스트 이름을 IPv4 주소 옆에 붙이고, `DayN` 을 `InsertDate` 의 연도로 날짜로 바꿔 보여 줍니다[4].

```
python KStrike.py E:\case\Sum\Current.mdb > Current_mdb.txt
```

Velociraptor 의 `Windows.Forensics.UserAccessLogs` 아티팩트도 자체 ESE 파서로 읽어 복구 없이 실행 중인 서버에서 바로 결과를 냅니다[6]. 두 가지 이상 방식으로 읽은 결과의 행 수를 맞춰 보는 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 로그온·로그오프 | UAL 의 첫·마지막 접근 시각에 같은 계정·주소의 네트워크 로그온이 있는지 | [로그온 세션 잇기](../event-logs/logon-events/logon-id-4624-4634-4647.md) |
| 도메인 인증 이벤트 | 도메인 컨트롤러에서 AD DS 레코드와 같은 계정의 인증 기록 | [도메인 인증 이벤트](../event-logs/logon-events/4768-4769-4776.md) |
| 공유 폴더 접근 | 파일 서버 레코드가 가리키는 날에 어느 공유·파일을 요청했는지 | [공유 폴더 접근](../event-logs/5140-5145.md) |
| 원격 데스크톱 이벤트 | Remote Desktop Services·Gateway 레코드와 같은 주소의 접속 기록 | [원격 데스크톱 이벤트](../event-logs/rdp-event-logs/index.md) |
| 이벤트 로그 삭제 | 이벤트 로그가 지워진 시점과 UAL 이 채워 줄 수 있는 기간 | [이벤트 로그 삭제](../event-logs/1102-104.md) |
| 섀도 복사본 | 지금은 없는 옛 연도 사본이나 정리 전의 SUM 폴더 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

UAL 로 찾은 계정·주소를 다른 서버와 PC 로 이어 가는 순서는 [계정 탈취와 측면 이동](../../04-scenarios/incident/credential-theft-lateral-movement/index.md)과 [랜섬웨어](../../04-scenarios/incident/ransomware.md)에서 다룹니다.

## 실습

공개 시험 이미지(NIST CFReDS 등) 가운데 Windows Server 2012 이후 서버, 특히 도메인 컨트롤러나 파일 서버 이미지를 골라 아래 질문을 풀어 봅니다.

1. SUM 폴더에 어떤 파일이 있습니까? `CHAINED_DATABASES` 에 적힌 연도와 실제 파일이 모두 맞습니까?
2. `SYSTEM_IDENTITY` 의 `CreationTime` 은 언제입니까? 서버 설치 시각과 비교하면 어떻습니까?
3. `Current.mdb` 의 비정상 종료 상태를 확인하고, 복구한 사본과 복구하지 않은 원본을 각각 다른 도구로 읽으면 `CLIENTS` 행 수가 같습니까?
4. File Server 역할에서 루프백이 아닌 주소는 몇 개입니까? 각 주소의 첫 접근 시각은 언제입니까?
5. 컴퓨터 계정 레코드 가운데 가장 늦게 처음 나타난 계정은 무엇입니까? 그 날짜의 `DayN` 값과 Security 로그의 로그온 기록이 맞습니까?

## 참고 문헌

1. Microsoft Learn, "Get Started with User Access Logging". https://learn.microsoft.com/en-us/windows-server/administration/user-access-logging/get-started-with-user-access-logging
2. Microsoft Learn, "Manage User Access Logging". https://learn.microsoft.com/en-us/windows-server/administration/user-access-logging/manage-user-access-logging
3. Patrick Bennett, "UAL Thank Us Later: Leveraging User Access Logging for Forensic Investigations", CrowdStrike 블로그, 2021-06-08. https://www.crowdstrike.com/en-us/blog/user-access-logging-ual-overview/
4. brimorlabs/KStrike, KStrike.py (커밋 daf2070c). https://github.com/brimorlabs/KStrike/blob/daf2070c95a2e1fe17b935b9e03af947a197b785/KStrike.py
5. EricZimmerman/Sum, SumData/Sum.cs·SumECmd/Program.cs (커밋 64b85409). https://github.com/EricZimmerman/Sum/tree/64b85409220278c2b3736c1822736a7136ae4972
6. Velocidex/velociraptor, artifacts/definitions/Windows/Forensics/UserAccessLogs.yaml (커밋 e851953b). https://github.com/Velocidex/velociraptor/blob/e851953bd5bcff06a6e026ae6bb7a2cbd6de1cab/artifacts/definitions/Windows/Forensics/UserAccessLogs.yaml
7. Velocidex/velociraptor, artifacts/testdata/server/testcases/ual.out.yaml (커밋 196f29ff). https://github.com/Velocidex/velociraptor/blob/196f29fff14621edc1f2ed3681e50f0ee470c4cf/artifacts/testdata/server/testcases/ual.out.yaml
