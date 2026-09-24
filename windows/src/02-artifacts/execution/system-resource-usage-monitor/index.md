# SRUM (System Resource Usage Monitor)

## 한 줄 요약

SRUM (System Resource Usage Monitor) 은 윈도가 앱과 사용자별 자원 사용량을 모아 두는 기능입니다. 모은 값은 한 시간 단위로 `C:\Windows\System32\sru\SRUDB.dat` 에 쌓입니다. 이 파일에는 앱이 쓴 CPU·디스크 양, 앱별 네트워크 송수신 바이트, 연결한 네트워크, 배터리 상태가 남습니다.

## 왜 중요한가

행마다 사용자가 남습니다. 각 행의 `UserId` 를 풀면 SID 가 나오므로 프리페치처럼 사용자 칸이 없는 실행 흔적을 보완합니다. 앱이 쓴 CPU 시간과 디스크 읽기·쓰기 양도 시간대별로 남아서, 잠깐 띄운 프로그램인지 오래 돌며 디스크를 많이 쓴 프로그램인지 가늠할 수 있습니다.

앱별로 보낸 바이트와 받은 바이트는 네트워크 인터페이스별로 남습니다. 자료 반출을 조사할 때 "이 시간대에 이 앱이 이만큼 송신한 기록이 있다" 는 근거가 됩니다. WithSecure 연구는 이 송수신 양을 `Ndu.sys` 드라이버가 WFP (Windows Filtering Platform) 위에서 계속 모은다고 설명하며, 이 연구에서는 빠지는 통신을 찾지 못했습니다. 어떤 네트워크에 언제부터 얼마나 연결했는지도 남고, 노트북이면 배터리 충전량과 용량 값도 남습니다.

App Timeline 표에는 1단계 저장소 (Tier1) 를 갱신할 때 돌고 있던 프로세스가 남습니다. 갱신 주기는 기본 60초이고, WithSecure 연구는 이 표를 실행 증거로 봅니다.

기록은 수십 일 동안 남는데, 보존 기간은 자료마다 다르게 적혀 있습니다. SANS ISC 글은 최대 30일, WithSecure 연구는 기본 60일로 적습니다. 이름 끝이 `LT` 인 장기 표는 1,820일(약 5년)입니다.

증명하지 못하는 것도 분명합니다.

- 정확한 실행 시각은 남지 않습니다. 행의 시각 (`TimeStamp`) 은 모은 값을 DB 에 쓴 시각이고, 실제 활동은 그보다 앞서 일어났습니다. Magnet 글은 이 차이를 앞뒤 한 시간 정도로 봅니다.
- 네트워크 표에는 상대방 주소(IP·도메인)를 담는 칸이 없습니다. 어디로 보냈는지는 다른 기록으로 채웁니다.
- 어떤 파일을 보냈는지도 남지 않습니다.
- 송수신 바이트에는 2계층 프레임 크기까지 들어갑니다(WithSecure). 그래서 이 값을 보낸 파일의 크기와 바로 맞춰 보지 않습니다.
- VPN 을 거친 통신은 모두 VPN 프로세스나 서비스의 몫으로 잡힙니다(WithSecure). 실제로 통신한 앱은 따로 찾아야 합니다.
- 마지막으로 DB 에 쓴 뒤의 사용량은 파일에 없을 수 있습니다. 모은 값은 DB 에 들어가기 전에 메모리나 레지스트리에 머뭅니다.

## 한눈에 보기

> 그림 자리: 앱 사용량이 1단계 저장소(메모리, 60초마다 갱신)를 거쳐 SRUDB.dat(1시간마다 기록)에 쌓이는 흐름과, 표의 `AppId`·`UserId` 숫자를 SruDbIdMapTable 에서 앱 이름·SID 로 푸는 과정을 한 장에 보여 주는 그림

### 위치와 함께 모을 파일

| 항목 | 내용 |
|---|---|
| DB 파일 | `C:\Windows\System32\sru\SRUDB.dat` |
| 형식 | ESE (Extensible Storage Engine) 데이터베이스. 형식은 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다. |
| 같은 폴더 | ESE 트랜잭션 로그와 체크포인트 파일 |
| 확장 목록 | SOFTWARE 하이브 `Microsoft\Windows NT\CurrentVersion\SRUM\Extensions`. 표 이름으로 쓰는 GUID 와 그 표를 채우는 DLL 이 여기에 짝지어 있습니다. |
| 사용자 정보 | 있습니다. `UserId` 를 SruDbIdMapTable 에서 찾으면 SID 가 나옵니다. |
| 시각 형식 | 각 표의 `TimeStamp` 는 OLE Automation 날짜이고 UTC 입니다. 네트워크 연결 표의 `ConnectStartTime` 은 FILETIME 입니다. 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다. |

수집할 때 알아 둘 점입니다.

- SRUDB.dat 와 SOFTWARE 하이브를 함께 모읍니다. SOFTWARE 하이브가 있어야 표 GUID 를 확장 이름과 DLL 로 풀 수 있습니다. 네트워크 식별 값을 무선 네트워크 이름(SSID)으로 맞출 때도 이 하이브를 씁니다(SANS ISC).
- 켜져 있는 PC 에서는 운영체제가 SRUDB.dat 를 잠가 둡니다. 공개 도구 가운데에는 잠긴 파일을 볼륨 섀도 복사본에서 꺼내는 것도 있습니다(SANS ISC).
- 압수 이미지에서 꺼낸 SRUDB.dat 는 대부분 비정상 종료 (dirty shutdown) 상태였습니다(현장 관찰). 이미지 안의 로그 사슬이 끊겨 로그로 복구하지 못한 경우도 있었습니다. 페이지를 직접 해석하는 방식은 로그 없이 읽습니다. 원본을 열면 내용이 바뀔 수 있으므로 항상 사본에서 작업합니다. 자세한 내용은 [트랜잭션 로그와 비정상 종료 상태](../../../01-foundations/database-log-formats/extensible-storage-engine/edb-log-dirty-shutdown.md) 에서 다룹니다.
- 손상된 SRUDB.dat 는 읽는 방식에 따라 행 수가 달랐습니다(현장 관찰). 같은 파일의 앱 사용량 표에서 도구마다 1,612행과 1,742행으로 갈렸습니다. B-트리를 끝까지 따라가지 못한 쪽이 적게 냈습니다. 손상된 DB 는 두 가지 이상 방식으로 열어 결과를 비교합니다.

### Windows 버전에 따라 달라지는 점

SRUM 은 Windows 8 에서 처음 들어왔습니다. Windows 7 이전에는 SRUDB.dat 가 없습니다.

| 시기 | DB 에 쓰기 전 머무는 곳 | DB 에 쓰는 때 | 근거 |
|---|---|---|---|
| Windows 8, 옛 Windows 10 (2019년 자료 기준) | 레지스트리 | 한 시간마다, 그리고 시스템을 끌 때 | Magnet, Velociraptor(2019) |
| 최근 Windows 10·11 | 메모리 (1단계 저장소, Tier1). 기본 60초마다 갱신합니다. 레지스트리는 쓰지 않습니다. | 2단계 저장소 (Tier2) 인 DB 에 기본 1시간마다 | WithSecure(2023) |

WithSecure 발표 자료는 데스크톱 윈도에서 Windows 10 1607 뒤로 이 값이 메모리에만 머무는 것으로 보인다고 적습니다. 이 경계는 발표자의 관찰이고 Microsoft 문서로 확인한 것은 아닙니다. 검체마다 SOFTWARE 하이브의 `SRUM` 키 아래를 직접 확인합니다. 두 방식의 차이는 [SRUM 해석 함정](1.md) 에서 다룹니다.

### 표와 알려 주는 것

표 이름은 GUID 입니다. 표 설명은 libyal 문서를 따릅니다. 기본 보존 기간은 WithSecure 연구(2023)를 따릅니다.

| 표 (GUID) | 알려 주는 것 | 기본 보존 기간 | 자세히 |
|---|---|---|---|
| SruDbIdMapTable | 다른 표의 `AppId`·`UserId` 숫자를 문자열로 푸는 사전입니다. `IdType` 이 3 이면 SID 가 들어 있고, 0\~2 이면 UTF-16 문자열이 들어 있습니다. | — | [구조와 ID 매핑](srudbidmaptable.md) |
| 앱별 자원 사용 `{D10CA2FE-6FCF-4F6D-848E-B2E99266FA89}` | 앱·사용자별 CPU 사이클 시간과 디스크 읽기·쓰기 양. 포그라운드 (Foreground) 와 백그라운드 (Background) 로 나눠 남습니다. | 60일 | [앱별 자원 사용](application-resource-usage.md) |
| 네트워크 사용량 `{973F5D5C-1D90-4944-BE8E-24B94231A174}` | 앱·사용자·인터페이스별 보낸 바이트 (`BytesSent`) 와 받은 바이트 (`BytesRecvd`) | 60일 | [네트워크 사용량](network-data-usage.md) |
| 네트워크 연결 `{DD6636C4-8929-4683-974E-22C046A43763}` | 인터페이스·네트워크 프로필별 연결 시작 시각 (`ConnectStartTime`) 과 연결 시간 (`ConnectedTime`) | 60일 | [네트워크 연결 기록](network-connectivity.md) |
| 전원 사용 `{FEE4E14F-02A9-4550-B5CE-5FA2DA202E37}` 과 장기 표 `…}LT` | 배터리 충전량, 설계 용량, 완충 용량, 충방전 횟수 | 60일, 장기 표는 1,820일 | [전원·배터리 사용](energy-usage.md) |
| App Timeline `{5C8CF1C7-7257-4F13-B223-970EF5939312}` | 1단계 저장소를 갱신할 때 돌고 있던 프로세스 | 7일 | 이 페이지 |
| 그 밖의 표 | 푸시 알림 `{D10CA2FE-6FCF-4F6D-848E-B2E99266FA86}`, 에너지 추정 `{DA73FB89-2BEA-4DDC-86B8-6E048C6DA477}`, Tagged Energy `{B6D82AF1-F780-4E17-8077-6CB9AD8A6FC4}`, vfuprov `{7ACBBAA3-D029-4BE4-9A7A-0885927F1D8F}` | 60일·7일·3일·60일 | 이 페이지 |

표 구성은 Windows 판마다 다를 수 있습니다. 검체마다 SOFTWARE 하이브의 확장 목록과 DB 의 실제 표 목록을 먼저 맞춰 봅니다. 윈도 기본 명령 `powercfg /srumutil` 은 SRUM 의 에너지 추정 (Energy Estimation) 데이터를 XML 이나 CSV 로 뽑습니다(Microsoft Learn). 이 명령은 켜져 있는 PC 에서만 씁니다.

## 읽는 순서

1. [구조와 ID 매핑 (SruDbIdMapTable)](srudbidmaptable.md) — SRUDB.dat 의 표 목록과 GUID 를 정리합니다. 각 표의 `AppId`·`UserId` 를 앱 이름과 SID 로 푸는 법도 다룹니다.
2. [앱별 자원 사용 (Application Resource Usage)](application-resource-usage.md) — 앱별 CPU 사이클 시간과 디스크 읽기·쓰기 양을 읽습니다. 이 값을 실행 흔적으로 쓸 수 있는 범위도 봅니다.
3. [네트워크 사용량 (Network Data Usage)](network-data-usage.md) — 앱별 송수신 바이트를 읽습니다. 반출 조사에서 이 값을 어디까지 말할 수 있는지 다룹니다.
4. [네트워크 연결 기록 (Network Connectivity)](network-connectivity.md) — 연결 시작 시각과 연결 시간을 읽습니다. 네트워크 프로필 번호를 이름으로 맞추는 법도 다룹니다.
5. [전원·배터리 사용 (Energy Usage)](energy-usage.md) — 배터리 충전량과 용량 값을 읽습니다. 몇 년 치가 남는 장기 표 (`LT`) 도 다룹니다.
6. [SRUM 해석 함정 (1시간 단위 기록·레지스트리 임시 저장)](1.md) — 시각이 한 시간 단위로 뭉치는 문제를 정리합니다. DB 에 아직 쓰지 않은 값이 어디에 머무는지, 손상된 DB 를 어떻게 읽는지도 다룹니다.

## 함께 볼 페이지

- [ESE 데이터베이스 (Extensible Storage Engine)](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) · [파일 구조 (Page·B+Tree·Catalog)](../../../01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md) — SRUDB.dat 를 직접 읽는 데 필요한 형식입니다.
- [파일 안에 남은 지운 레코드 (Deleted Records)](../../../01-foundations/database-log-formats/extensible-storage-engine/deleted-records.md) — 보존 기간이 지나 지운 행을 찾을 때 봅니다.
- [윈도 식별자 형식 (SID·GUID·CLSID·Known Folder ID)](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) — SruDbIdMapTable 의 SID 와 표 이름 GUID 를 읽습니다.
- [하이브 파일 종류와 위치 (SYSTEM·SOFTWARE·SAM·SECURITY·NTUSER.DAT·UsrClass.dat)](../../../01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md) — 함께 모을 SOFTWARE 하이브의 위치입니다.
- [프리페치 (Prefetch)](../prefetch/index.md) · [AmCache (Amcache.hve)](../amcache-hve/index.md) · [BAM·DAM (Background Activity Moderator)](../background-activity-moderator.md) — 실행 시각과 실행 파일 정보를 더합니다.
- [네트워크 목록 (NetworkList)](../../network/networklist.md) · [Wi-Fi 프로필 (WLAN Profiles)](../../network/wlan-profiles.md) — 연결한 네트워크의 이름과 처음·마지막 연결 시각을 맞춰 봅니다.
- [VPN 연결 기록 (VPN Connections)](../../network/vpn-connections.md) — 송수신 양이 VPN 프로세스로 몰릴 때 봅니다.
- [켜짐·꺼짐 (Power On·Off Events)](../../event-logs/power-on-off-events.md) — 기록이 비는 시간대가 PC 가 꺼져 있던 때인지 확인합니다.
- [섀도 복사본 활용 (Volume Shadow Copy Analysis)](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 보존 기간이 지난 옛 SRUDB.dat 를 꺼냅니다.
- [도구 결과 교차 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md) — 손상된 DB 를 여러 방식으로 읽고 비교합니다.
- [어떤 프로그램을 언제 실행했나 (Program Execution)](../../../04-scenarios/activity/program-execution.md) · [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md) · [PC 사용 시간 재구성 (System Usage Time)](../../../04-scenarios/activity/system-usage-time.md) — SRUM 을 다른 기록과 묶어 읽는 조사 흐름입니다.

## 참고 문헌

- Joachim Metz, "System Resource Usage Monitor (SRUM) database" (libyal esedb-kb) — https://github.com/libyal/esedb-kb/blob/main/documentation/System%20Resource%20Usage%20Monitor%20(SRUM).asciidoc
- WithSecure (Catarina de Faria Cristas·Lucas Echard·Diego Fuschini), "SRUM Analysis", Chainsaw Wiki, SANS DFIR Summit Europe 2023 발표 요약 — https://github.com/WithSecureLabs/chainsaw/wiki/SRUM-Analysis
- Catarina de Faria Cristas·Lucas Echard·Diego Fuschini (WithSecure), "Exploring the depths of SRUM for incident response", SANS DFIR Summit Europe 2023 발표 자료 — https://github.com/ReversecLabs/slide-decks/blob/main/2023-SANS_DFIR_Summit_Europe/Exploring_the_depths_of_SRUM_for_incident_response.pdf
- Microsoft Learn, "Powercfg command-line options" (`/srumutil`) — https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options
- Mark Baggett, "SRUM-DUMP Version 3: Uncovering Malware Activity in Forensics", SANS Internet Storm Center (2025) — https://isc.sans.edu/diary/31896
- Velociraptor, "Digging into the System Resource Usage Monitor (SRUM)" (2019) — https://docs.velociraptor.app/blog/2019/2019-12-31_digging-into-the-system-resource-usage-monitor-srum-afbadb1a375/
- Magnet Forensics, "SRUM: Forensic Analysis of Windows System Resource Utilization Monitor" — https://www.magnetforensics.com/blog/srum-forensic-analysis-of-windows-system-resource-utilization-monitor/
