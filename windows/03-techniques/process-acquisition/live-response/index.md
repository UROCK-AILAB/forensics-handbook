# 라이브 응답 (Live Response)

## 한 줄 요약

라이브 응답 (Live Response) 은 켜진 시스템에서 전원을 끄기 전에 데이터를 모으는 일입니다. 대상은 네트워크 연결, 로그온 세션, 실행 중 프로세스처럼 전원이 꺼지면 사라지는 휘발성 데이터 (volatile data) 입니다. 이 허브는 켜진 디스크를 복사하는 일도 함께 다룹니다. 켜진 채로 모을지 정하는 기준은 이 페이지에 있고, 대상마다 모으는 방법은 하위 페이지에 있습니다.

## 왜 중요한가

- 휘발성 OS 데이터는 켜진 시스템에서만 얻을 수 있습니다. 사건 뒤로 재부팅하거나 끄지 않은 시스템이어야 합니다.
- 전원을 끄면 중요한 정보를 얻을 기회가 사라질 수 있습니다.
- 네트워크만 끊어도 사라지는 정보가 있습니다.

켜진 채로 모으는 일에도 위험이 따릅니다.

- 시스템에서 일어나는 동작은 휘발성 데이터를 거의 틀림없이 바꿉니다. 사람이 한 동작이든 OS 가 한 동작이든 같습니다.
- 모으는 동안 파일이 바뀔 수 있습니다.
- 루트킷 (rootkit) 이 거짓 정보를 돌려줄 수 있습니다.
- 루트킷이 파일을 지울 수도 있습니다.

### 켜진 채로 모을지 정하는 기준

NIST SP 800-86 은 아래처럼 권합니다.

- 휘발성 데이터를 보존할지는 빨리 정해야 합니다.
- 판단 기준은 미리 문서로 정해 둡니다.
- 모을 때의 위험과 얻을 정보의 가치를 저울질해 정합니다.

무엇이 필요한지 확신이 서지 않을 때의 원칙과 사건마다 모을 데이터는 [수집 순서와 원칙](/03-techniques/process-acquisition/live-response/order-of-volatility.md)에서 다룹니다. 켜진 디스크를 복사할지 정하는 기준은 [실행 중 시스템 이미징](/03-techniques/process-acquisition/live-response/live-imaging.md)에서 다룹니다.

### 한 일을 모두 적는 까닭

- RFC 3227 3절은 증거를 모으는 방법이 투명하고 다시 해 볼 수 있어야 한다고 적습니다.
- 모든 단계와 쓴 도구를 자세히 적어 두면, 다른 분석관이 나중에 같은 과정을 되풀이할 수 있습니다.
- 가능하면 현장의 한 사람을 증거 관리 담당으로 정합니다.
- 이 사람이 모은 것을 모두 사진으로 찍고, 기록하고, 표시합니다.
- 누가, 어디서, 언제, 무엇을 했는지도 이 사람이 적습니다.

도구마다 적을 항목과 연속 보관 기록의 항목은 [수집 순서와 원칙](/03-techniques/process-acquisition/live-response/order-of-volatility.md)에 있습니다.

## 한눈에 보기

> 그림 자리: 켜진 시스템의 수집 대상(네트워크 연결·로그온 세션·프로세스·열린 파일·네트워크 설정·OS 시각·디스크)을 늘어놓고, 각 대상을 다루는 하위 페이지를 이은 그림

NIST SP 800-86 5.2.1.2 절은 휘발성 데이터의 종류로 메모리 내용, 네트워크 설정, 네트워크 연결, 실행 중 프로세스, 열린 파일, 로그인 세션, OS 시각을 듭니다. 이 허브의 하위 페이지는 이 목록과 대부분 겹칩니다. 메모리를 통째로 모으는 일만 이 허브 밖에서 다룹니다.

### 대상별로 모으는 방법

| 수집 대상 | Windows 에서 모으는 방법 (예) | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 네트워크 연결 | `netstat`, `Get-NetTCPConnection` | 연결 상대 주소와 포트, 연결 상태, 연결을 연 프로세스 | [네트워크 상태 수집](/03-techniques/process-acquisition/live-response/connections-dns-arp-routes.md) |
| DNS 캐시 | `ipconfig /displaydns` | 이 컴퓨터가 최근에 찾은 이름, Hosts 파일에서 올린 항목 | [네트워크 상태 수집](/03-techniques/process-acquisition/live-response/connections-dns-arp-routes.md) |
| ARP 캐시·라우팅 표 | `arp -a`, `route print` | 같은 네트워크에 있는 장치의 IP 주소와 물리 주소, 경로 | [네트워크 상태 수집](/03-techniques/process-acquisition/live-response/connections-dns-arp-routes.md) |
| 네트워크 설정 | `ipconfig /all` | 어댑터마다 지금 쓰는 TCP/IP 설정 | [네트워크 상태 수집](/03-techniques/process-acquisition/live-response/connections-dns-arp-routes.md) |
| 로그온 세션 | `query user`, WMI `Win32_LogonSession` | 로그온한 사용자, 세션 상태, 로그온 시각 | [로그온 세션·클립보드·화면 수집](/03-techniques/process-acquisition/live-response/sessions-clipboard-screen.md) |
| 실행 중 프로세스·DLL | `tasklist`, WMI `Win32_Process` | 실행 중인 프로그램과 서비스, 불러온 DLL, 명령줄, 부모 프로세스, 시작 시각 | [프로세스·DLL·핸들 수집](/03-techniques/process-acquisition/live-response/processes-dlls-handles.md) |
| 열린 파일 (핸들) | Sysinternals Handle | 어느 프로세스가 어떤 파일을 열었는지, 핸들의 객체 종류와 이름 | [프로세스·DLL·핸들 수집](/03-techniques/process-acquisition/live-response/processes-dlls-handles.md) |
| 클립보드 | PowerShell `Get-Clipboard` | 지금 클립보드에 든 내용 한 건 | [로그온 세션·클립보드·화면 수집](/03-techniques/process-acquisition/live-response/sessions-clipboard-screen.md) |
| 화면 | 사진, 메모 | 화면에 떠 있던 문서와 프로그램, 화면 보호기 | [로그온 세션·클립보드·화면 수집](/03-techniques/process-acquisition/live-response/sessions-clipboard-screen.md) |
| OS 시각 | `date`, `time` (NIST 가 든 예) | 대상 시스템의 시각과 시간대, 시계 어긋남 | [수집 순서와 원칙](/03-techniques/process-acquisition/live-response/order-of-volatility.md) |
| 디스크·볼륨 | `\\.\PhysicalDriveX`·`\\.\X:` 직접 열기, 볼륨 섀도 복사본 | 켜진 상태의 디스크 내용, 잠금 해제된 암호화 볼륨의 풀린 내용 | [실행 중 시스템 이미징](/03-techniques/process-acquisition/live-response/live-imaging.md) |
| 메모리 전체 | 이 허브에서 다루지 않습니다 | — | [메모리 분석](/03-techniques/analysis/memory-forensics/index.md) |

`Get-NetTCPConnection`, `arp -a`, `route print`, `Win32_LogonSession`, `Get-Clipboard` 의 결과는 PC 한 대에서 직접 확인했습니다 (확인 범위: Windows 11 Home 10.0.26200). 나머지 명령은 공식 문서로 확인했습니다.

메모리를 복사하는 도구를 돌리면 RAM 이 바뀝니다. 이 변화는 피할 수 없습니다. 그래서 NIST 는 도구가 남기는 흔적을 최소로 하라고 적습니다.

### Windows 버전과 판에 따라 다른 점

| 항목 | 내용 | 근거 |
|---|---|---|
| `Win32_Process` | 최소 지원 버전은 Windows Vista, Windows Server 2008 입니다 | 공식 문서 |
| 클립보드 기록 | 안내 대상은 Windows 10 과 Windows 11 입니다 | 공식 안내 |
| 디스크·볼륨 직접 열기 | 지금 Windows 는 직접 접근을 제한합니다. Windows XP 와 Windows Server 2003 에는 이 제한이 없었습니다 | 공식 문서 |
| `query user` | 문서는 원격 데스크톱 세션 호스트 서버를 기준으로 씁니다. Windows 11 Home 에는 `quser.exe` 도 `query.exe` 도 없었습니다 | 공식 문서, 관찰 (확인 범위: Windows 11 Home 10.0.26200) |
| 섀도 복사본 만들기 | DiskShadow 는 Windows Server 에만 있습니다. `vssadmin` 명령 참조 문서의 클라이언트 명령 목록에는 `create shadow` 가 없습니다. Windows 11 Home 에서도 이 명령이 "Error: Invalid command." 로 끝났습니다 | 공식 문서, 관찰 (확인 범위: Windows 11 Home 10.0.26200) |

## 읽는 순서

1. [수집 순서와 원칙 (Order of Volatility)](/03-techniques/process-acquisition/live-response/order-of-volatility.md) — RFC 3227 과 NIST SP 800-86 의 수집 순서를 견줍니다. 도구 준비, 시각 기록, 끄는 방법, 연속 보관 기록도 다룹니다.
2. [프로세스·DLL·핸들 수집 (Processes·DLLs·Handles)](/03-techniques/process-acquisition/live-response/processes-dlls-handles.md) — `tasklist` 와 `Win32_Process` 로 프로세스 목록, 명령줄, 부모 프로세스를 남깁니다. Handle 로 열린 파일을 봅니다.
3. [네트워크 상태 수집 (Connections·DNS·ARP·Routes)](/03-techniques/process-acquisition/live-response/connections-dns-arp-routes.md) — 연결 목록, DNS 캐시, ARP 캐시, 라우팅 표, 네트워크 설정을 남깁니다. 수집 중에 DNS 캐시를 지우는 명령도 짚습니다.
4. [로그온 세션·클립보드·화면 수집 (Sessions·Clipboard·Screen)](/03-techniques/process-acquisition/live-response/sessions-clipboard-screen.md) — 시스템을 만지기 전에 화면을 찍습니다. 그다음 로그온 세션과 클립보드를 남깁니다.
5. [실행 중 시스템 이미징 (Live Imaging)](/03-techniques/process-acquisition/live-response/live-imaging.md) — 켜진 디스크와 볼륨을 복사할 때의 문제를 다룹니다. BitLocker 볼륨과 볼륨 섀도 복사본도 다룹니다.

읽는 순서와 현장에서 모으는 순서는 다릅니다. 현장에서는 1번 페이지의 절차를 따릅니다.

## 함께 볼 페이지

- [포렌식 조사 절차](/03-techniques/process-acquisition/investigation-process.md) — 조사 전체 흐름을 봅니다.
- [증거 획득](/03-techniques/process-acquisition/evidence-acquisition/index.md) — 끈 시스템의 디스크를 복사하고 검증합니다.
- [메모리 분석](/03-techniques/analysis/memory-forensics/index.md) — 메모리를 통째로 모아 분석합니다. 라이브 응답 결과와 맞춰 봅니다.
- [암호화 증거 다루기](/03-techniques/analysis/encrypted-evidence/index.md) — 암호화된 디스크와 볼륨을 다룹니다.
- [볼륨 섀도 복사본 구조](/01-foundations/disk-volume/volume-shadow-copy.md) · [섀도 복사본 활용](/03-techniques/analysis/volume-shadow-copy-analysis.md) — 섀도 복사본의 저장 구조와 분석 방법을 봅니다.
- [시간대 설정](/02-artifacts/system-account/time-zone.md) · [타임라인 작성](/03-techniques/analysis/timeline/index.md) — 현장에서 적은 시각을 디스크 기록과 맞춥니다.
- [로그온·로그오프](/02-artifacts/event-logs/logon-events/index.md) · [프로세스 생성](/02-artifacts/event-logs/4688.md) — 끈 뒤에 디스크에서 로그온과 프로세스 기록을 읽습니다.
- [hosts 파일](/02-artifacts/network/hosts.md) — DNS 캐시에 올라오는 Hosts 항목의 원래 파일을 봅니다.
- [분석 보고서 작성](/03-techniques/reporting/forensic-report.md) · [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md) — 현장 기록을 보고서로 옮기고, 도구 결과를 검증합니다.

## 참고 문헌

1. D. Brezinski, T. Killalea, "RFC 3227 (BCP 55): Guidelines for Evidence Collection and Archiving", 2002-02. https://www.rfc-editor.org/rfc/rfc3227
2. K. Kent, S. Chevalier, T. Grance, H. Dang, "NIST SP 800-86: Guide to Integrating Forensic Techniques into Incident Response", NIST, 2006-08. https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf
3. Microsoft Learn, "netstat". https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netstat
4. Microsoft Learn, "ipconfig". https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig
5. Microsoft Learn, "tasklist". https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tasklist
6. Microsoft Learn (Sysinternals), "Handle", Mark Russinovich, 2022-10-26. https://learn.microsoft.com/en-us/sysinternals/downloads/handle
7. Microsoft Learn, "Win32_Process class". https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process
8. Microsoft Learn, "query user". https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/query-user
9. Microsoft Support, "Clipboard in Windows". https://support.microsoft.com/en-us/windows/clipboard-in-windows-c436501e-985d-1c8d-97ea-fe46ddf338c6
10. Microsoft Learn, "CreateFileW function (fileapi.h)", Physical Disks and Volumes 절. https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
11. Microsoft Learn, "Volume Shadow Copy Service (VSS)". https://learn.microsoft.com/en-us/windows-server/storage/file-server/volume-shadow-copy-service
12. Microsoft Learn, "vssadmin". https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/vssadmin
