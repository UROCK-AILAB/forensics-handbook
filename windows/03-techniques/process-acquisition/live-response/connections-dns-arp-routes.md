---
title: "네트워크 상태 수집"
parent: "라이브 응답"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 3140
---

# 네트워크 상태 수집 (Connections·DNS·ARP·Routes)

## 한 줄 요약

켜진 시스템의 네트워크 연결, DNS 캐시, ARP 캐시, 라우팅 표, 네트워크 설정을 글자 파일로 남깁니다. 연결 목록은 몇 초 만에도 바뀌므로 가장 먼저 모읍니다. `netstat` 결과에는 시각 열이 없고, 수집 중에 `ipconfig /flushdns` 를 돌리면 DNS 캐시가 지워집니다.

## 언제 쓰나

NIST SP 800-86 순서에서 네트워크 연결은 첫째, 네트워크 설정은 여섯째입니다. 순서 전체는 [수집 순서와 원칙](order-of-volatility.md)에서 다룹니다.

많은 호스트가 IP 주소를 DHCP 로 받으므로 저장된 설정이 아니라 지금 설정을 봐야 합니다. 유선, 무선, VPN 처럼 인터페이스가 여럿일 수 있는데, 지금 설정을 보면 어느 인터페이스를 쓰는지 압니다. 대부분의 OS 는 원격으로 탑재한 파일 시스템 목록도 보여 주며, 이 목록은 연결 목록보다 자세합니다. 들어오는 연결이 어떤 자원(파일 공유·프린터)을 쓰는지도 볼 수 있습니다.

다른 시스템에서 포트 스캔을 해서 열린 포트를 볼 수도 있지만, 방화벽 때문에 결과가 틀릴 수 있고 스캔 자체가 시스템 상태를 바꿀 수 있습니다. 그래서 대상 시스템 안에서 목록을 뽑습니다.

## 절차

명령 예의 `E:` 는 결과를 받는 외장 매체라고 가정한 것입니다. 명령 파일은 도구 매체의 사본을 씁니다.

1. **연결과 대기 포트를 남깁니다.** 관리자 권한 명령 창에서 돌립니다.
   ```
   netstat -anob > E:\out\netstat_anob.txt
   ```
   `-q` 를 더하면 대기하지 않는 바인딩된 포트까지 나옵니다(예: `netstat -anobq`).
2. **PowerShell 로 한 번 더 남깁니다.** `Get-NetTCPConnection` 과 `Get-NetUDPEndpoint` 는 프로세스 ID 와 `CreationTime` 을 함께 보여 줍니다.
3. **DNS 캐시를 남깁니다.**
   ```
   ipconfig /displaydns > E:\out\dns_cache.txt
   ```
   PowerShell 에서는 `Get-DnsClientCache` 를 씁니다.
4. **ARP 캐시를 남깁니다.** `arp -a` 나 `Get-NetNeighbor` 를 씁니다.
5. **라우팅 표를 남깁니다.** `route print` 나 `Get-NetRoute` 를 씁니다. `netstat -r` 도 같은 내용을 보여 줍니다.
6. **네트워크 설정을 남깁니다.**
   ```
   ipconfig /all > E:\out\ipconfig_all.txt
   ```
7. **결과 파일의 해시와 명령을 돌린 시각을 적습니다.**

`ipconfig /flushdns` 는 어느 단계에서도 돌리지 않습니다.

## 도구와 결과 형식

### netstat

인자 없이 쓰면 활성 TCP 연결을 보여 줍니다.

| 옵션 | 뜻 |
|---|---|
| `-a` | 모든 활성 TCP 연결과, 대기 중인 TCP·UDP 포트를 보여 줍니다 |
| `-n` | 주소와 포트를 숫자로 보여 주고, 이름을 찾지 않습니다 |
| `-o` | 연결마다 PID 를 보여 줍니다. `-a`, `-n`, `-p` 와 함께 쓸 수 있습니다 |
| `-b` | 연결이나 대기 포트를 만든 실행 파일을 보여 줍니다 |
| `-q` | 모든 연결, 대기 포트, 대기하지 않는 바인딩된 TCP 포트를 보여 줍니다 |
| `-r` | IP 라우팅 표를 보여 줍니다. `route print` 와 같습니다 |

`-b` 는 시간이 걸리고, 권한이 모자라면 실패합니다. 실행 파일 하나에 구성 요소가 여럿 들어 있으면 구성 요소 순서를 먼저 보여 주고, 실행 파일 이름은 맨 아래 `[]` 안에 나옵니다.

열은 Proto, Local Address, Foreign Address, State 인데, 문서에 적힌 상태 값과 실제 출력은 조금 다릅니다.

| 문서의 값 | 실제 출력 |
|---|---|
| `LISTEN` | `LISTENING` |
| `TIMED_WAIT` | `TIME_WAIT` |

나머지 상태 값은 `CLOSE_WAIT`, `CLOSED`, `ESTABLISHED`, `FIN_WAIT_1`, `FIN_WAIT_2`, `LAST_ACK`, `SYN_RECEIVED`, `SYN_SEND` 입니다.

한국어 Windows 에서는 머리글이 "프로토콜 / 로컬 주소 / 외부 주소 / 상태 / PID" 로 번역돼 나오고, 상태 값은 영어 그대로 나옵니다.

### Get-NetTCPConnection · Get-NetUDPEndpoint

NetTCPIP 모듈의 명령입니다. PowerShell 5.1 에서 나오는 속성은 아래와 같습니다.

| 명령 | 속성 |
|---|---|
| `Get-NetTCPConnection` | LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess, CreationTime |
| `Get-NetUDPEndpoint` | LocalAddress, LocalPort, OwningProcess, CreationTime |

TCP 항목에는 `CreationTime` 값이 채워져 나옵니다. `Bound` 상태 항목도 나오는데, `netstat` 은 `-q` 를 줘야 이런 포트를 보여 줍니다.

### DNS 캐시

`ipconfig /displaydns` 는 DNS 클라이언트 캐시 내용을 보여 줍니다. 캐시에는 로컬 hosts 파일에서 미리 올린 항목과 이 컴퓨터가 최근에 이름을 찾아 얻은 레코드가 섞여 있습니다.

DNS Client 서비스는 이 캐시로 자주 찾는 이름을 DNS 서버에 묻기 전에 바로 풉니다. hosts 파일 자체는 [hosts 파일](../../../02-artifacts/network/hosts.md)에서 다룹니다.

두 명령이 보여 주는 필드는 아래와 같습니다.

| 명령 | 필드·속성 |
|---|---|
| `ipconfig /displaydns` | Record Name, Record Type, Time To Live, Data Length, Section, 그리고 A (Host) Record 나 CNAME Record 같은 값 줄 |
| `Get-DnsClientCache` | Entry, Name, Type, Status, Section, TimeToLive, DataLength, Data |

### ARP 캐시

RFC 3227 은 ARP 캐시를 메모리와 같은 둘째 단계에 둡니다. 한국어 Windows 의 `arp -a` 출력은 아래 모양입니다.

인터페이스마다 "인터페이스: `<IP>` --- 0x<번호>" 줄이 먼저 나오고, 그 아래에 인터넷 주소, 물리적 주소, 유형 열이 옵니다. 유형은 동적 또는 정적입니다.

`Get-NetNeighbor` 의 `State` 에는 `Permanent`, `Reachable`, `Stale`, `Unreachable` 이 나옵니다.

### 라우팅 표

`route print` 출력은 아래 순서로 나옵니다.

1. 인터페이스 목록
2. IPv4 경로 테이블 — 활성 경로, 영구 경로
3. IPv6 경로 테이블 — 활성 경로, 영구 경로

IPv4 활성 경로의 열은 네트워크 대상, 네트워크 마스크, 게이트웨이, 인터페이스, 메트릭입니다. `Get-NetRoute` 는 DestinationPrefix, NextHop, InterfaceAlias, InterfaceIndex, RouteMetric, IsStatic, TypeOfRoute 같은 속성을 돌려줍니다.

### 네트워크 설정

`ipconfig /all` 은 모든 어댑터의 전체 TCP/IP 설정을 보여 줍니다. 레지스트리에 남은 인터페이스 설정은 [네트워크 인터페이스 설정](../../../02-artifacts/network/tcp-ip-interfaces.md)에서 다룹니다. 원격으로 탑재한 드라이브와 공유는 [공유 폴더·네트워크 드라이브](../../../02-artifacts/network/network-shares-mapped-drives.md)에서 다룹니다.

## 함정과 한계

1. **`ipconfig /flushdns` 를 돌립니다.** 캐시를 비우는 명령입니다. 수집 중에 돌리면 증거를 지웁니다.
2. **`netstat` 결과에서 연결 시각을 찾습니다.** `netstat` 출력에는 시각 열이 없습니다. 명령을 돌린 시각을 따로 적어야 합니다.
3. **`CreationTime` 을 연결 시작 시각으로 씁니다.** 이 값이 정확히 무엇의 시각인지는 공식 문서에 나와 있지 않습니다. 보고서에는 속성 이름 그대로 적습니다.
4. **두 명령의 결과가 같다고 봅니다.** 두 명령을 몇 초 차이로 돌려도 상태별 개수가 조금 다를 수 있습니다. 네트워크 상태는 몇 초 만에도 바뀝니다. 명령마다 돌린 시각을 적습니다.
5. **`netstat -ano` 에 모든 포트가 나온다고 봅니다.** 바인딩만 하고 대기하지 않는 TCP 포트는 `-q` 를 줘야 나옵니다.
6. **`-b` 없이 실행 파일을 짐작합니다.** `-o` 는 PID 만 보여 주므로, `-b` 가 권한 문제로 실패하면 PID 를 프로세스 목록과 맞춰 실행 파일을 찾습니다.
7. **문서의 상태 이름으로 검색합니다.** 실제 출력은 `LISTENING`, `TIME_WAIT` 입니다. 한국어 Windows 는 머리글도 번역돼 나오므로, 결과를 읽는 스크립트는 머리글 이름에 기대지 않게 만듭니다.
8. **DNS 캐시의 모든 항목을 조회 기록으로 봅니다.** hosts 파일에서 올린 항목이 섞여 있습니다.

## 결과를 어떻게 해석하나

### 연결과 프로세스

`-o` 의 PID 와 `OwningProcess` 는 [프로세스·DLL·핸들 수집](processes-dlls-handles.md)에서 모은 목록과 잇습니다. 두 목록은 따로 모은 것이라 그사이에 프로세스가 끝나고 PID 가 다시 쓰였을 수 있습니다. PID 를 잇는 주의점은 그 페이지에서 다룹니다.

### 증명하는 것 / 증명하지 못하는 것

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 수집 시각에 이 PID 가 이 원격 주소·포트와 이 상태로 연결돼 있었습니다 | 연결이 언제 시작됐는지, 얼마나 주고받았는지 |
| 수집 시각에 이 포트가 대기 중이었습니다 | 밖에서 실제로 접속했는지 |
| DNS 캐시에 이 이름의 레코드가 있었습니다 | 그 주소로 실제로 연결했는지. 캐시에는 hosts 파일 항목도 들어 있습니다 |
| 수집 시각의 라우팅 표와 ARP 캐시 내용 | 과거의 네트워크 구성 |

아래 보고서 문장의 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "2025-03-14 10:20 (KST) 에 수집한 `netstat -anob` 결과에서 PID 4120 이 203.0.113.10:443 과 ESTABLISHED 상태였습니다."
- 쓰면 안 되는 문장: "a.exe 가 203.0.113.10 으로 자료를 보냈습니다."

### 함께 볼 기록

켜진 상태의 목록은 한 순간만 보여 줍니다. 과거 연결은 디스크의 기록과 함께 봅니다.

| 함께 볼 페이지 | 무엇을 맞춰 보나 |
|---|---|
| [윈도 방화벽](../../../02-artifacts/network/windows-firewall-pfirewall-log.md) | 방화벽 로그에 남은 과거 연결 |
| [SRUM](../../../02-artifacts/execution/system-resource-usage-monitor/index.md) | 앱별 네트워크 사용량 |
| [네트워크 연결 이벤트](../../../02-artifacts/event-logs/wlan-autoconfig-networkprofile.md) | 어느 네트워크에 붙어 있었는지 |
| [VPN 연결 기록](../../../02-artifacts/network/vpn-connections.md) | VPN 인터페이스를 쓴 기록 |
| [원격 제어 프로그램](../../../02-artifacts/network/remote-access-tools/index.md) | 연결을 연 프로그램이 원격 제어 도구인지 |
| [자료를 밖으로 빼돌렸나](../../../04-scenarios/exfiltration/data-exfiltration/index.md) | 연결을 유출 흐름 안에서 읽는 법 |

## 참고 문헌

- D. Brezinski, T. Killalea, "RFC 3227 (BCP 55): Guidelines for Evidence Collection and Archiving", 2002-02 — https://www.rfc-editor.org/rfc/rfc3227
- K. Kent, S. Chevalier, T. Grance, H. Dang, "NIST SP 800-86: Guide to Integrating Forensic Techniques into Incident Response", NIST, 2006-08 — https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf
- Microsoft Learn, "netstat" — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netstat
- Microsoft Learn, "ipconfig" — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig
