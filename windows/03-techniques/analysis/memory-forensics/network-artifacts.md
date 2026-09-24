# 메모리 속 네트워크 흔적 (Network Artifacts)

> 상위 허브: [메모리 분석 (Memory Forensics)](/03-techniques/analysis/memory-forensics/index.md)

## 한 줄 요약

메모리 이미지에서 TCP·UDP 연결과 수신 대기 (Listening) 흔적을 찾습니다.
그다음 그 흔적을 연 프로세스와 잇습니다.
연결 상태는 전원이 꺼지면 사라지므로 켜진 PC 의 메모리에서 봅니다.

## 언제 쓰나

- 악성코드가 밖의 서버와 통신하고 있었는지 볼 때 씁니다.
- 원격 제어 프로그램이나 원격 데스크톱으로 누가 들어와 있었는지 볼 때 씁니다. [원격 제어 프로그램으로 누가 조작했나](/04-scenarios/incident/remote-access-tool-abuse.md) 와 [원격 데스크톱 침입 확인](/04-scenarios/incident/rdp-intrusion.md) 을 봅니다.
- 자료를 밖으로 보냈는지 볼 때 보조 근거로 씁니다. [자료를 밖으로 빼돌렸나](/04-scenarios/exfiltration/data-exfiltration/index.md) 를 봅니다.
- 디스크 쪽 연결 기록이 없거나 부족할 때 씁니다.

RFC 3227 은 라우팅 표와 ARP 캐시를 메모리와 같은 묶음에 둡니다 [1]. 휘발성이 큰 쪽이라 먼저 모으라는 뜻입니다.

## 플러그인

Volatility 3 에는 네트워크 연결을 보는 플러그인으로 windows.netscan 과 windows.netstat 이 있습니다 [2].
두 플러그인이 연결을 찾는 방식은 아래 "알려진 동작" 에 적었습니다.
플러그인 이름이 버전마다 다를 수 있다는 점은 [프로세스와 DLL 분석](/03-techniques/analysis/memory-forensics/process-analysis.md) 의 "플러그인 이름 읽는 법" 에 있습니다.

## 알려진 동작

아래는 널리 알려진 설명입니다. 이 글의 참고 문헌으로는 확인하지 못했습니다. 쓰는 버전의 도움말과 출력으로 확인하고 씁니다.

- windows.netscan 은 메모리를 긁어 TCP·UDP 연결 객체와 수신 대기 객체를 찾는다고 알려져 있습니다.
- windows.netstat 은 네트워크 드라이버 tcpip.sys 가 관리하는 구조를 따라간다고 알려져 있습니다.
- 긁어 찾는 방식은 이미 닫힌 연결의 흔적도 낼 수 있다고 알려져 있습니다.
- 결과 칸에는 흔히 프로토콜, 로컬·원격 주소와 포트, 상태, 소유 프로세스(PID·이름), 생성 시각이 나온다고 알려져 있습니다.

## 절차

1. 확보 기록부터 봅니다. 네트워크를 언제 끊었는지, 이미지를 네트워크로 보냈는지 확인합니다. [메모리 덤프 확보](/03-techniques/analysis/memory-forensics/memory-acquisition.md) 를 봅니다.
2. windows.netscan 과 windows.netstat 를 둘 다 돌립니다.
3. 두 결과를 나란히 놓습니다. 한쪽에만 있는 항목을 따로 표시합니다.
4. 각 항목의 소유 프로세스를 프로세스 목록과 잇습니다. 목록을 만드는 법은 [프로세스와 DLL 분석](/03-techniques/analysis/memory-forensics/process-analysis.md) 에 있습니다.
5. 소유 PID 가 프로세스 목록에 없으면 이미 끝난 프로세스이거나 숨긴 프로세스일 수 있습니다. [코드 주입·숨긴 프로세스 탐지](/03-techniques/analysis/memory-forensics/injection-rootkit.md) 를 봅니다.
6. 확보 과정에서 생긴 연결을 가려냅니다. 1단계의 기록과 맞춰 봅니다.
7. 남은 원격 주소와 포트를 정리해 디스크 기록과 맞대 봅니다(아래 표).
8. 연결 객체 밖에 남은 호스트 이름·URL 같은 문자열은 문자열·패턴 검색으로 찾습니다. Volatility 3 에는 windows.strings 와 windows.vadyarascan 이 있습니다 [2]. 이 플러그인으로 네트워크 흔적을 찾는 구체적 방법은 이 글의 참고 문헌으로 확인하지 못했습니다. 검색 방법은 [메모리 속 문자열·자격증명·암호 키](/03-techniques/analysis/memory-forensics/strings-credentials-keys.md) 에 있습니다.

## 디스크 기록과 맞대 보기

| 메모리에서 본 것 | 맞대 볼 페이지 |
|---|---|
| 원격 주소·포트와 소유 프로세스 | [윈도 방화벽](/02-artifacts/network/windows-firewall-pfirewall-log.md), [Sysmon 로그](/02-artifacts/event-logs/sysmon/index.md) |
| 프로그램별 네트워크 사용 | [SRUM](/02-artifacts/execution/system-resource-usage-monitor/index.md) |
| 원격 데스크톱 연결 | [원격 데스크톱 이벤트](/02-artifacts/event-logs/rdp-event-logs/index.md) |
| 원격 제어 프로그램의 연결 | [원격 제어 프로그램](/02-artifacts/network/remote-access-tools/index.md) |
| 공유 폴더로 가는 연결 | [공유 폴더·네트워크 드라이브](/02-artifacts/network/network-shares-mapped-drives.md) |
| 호스트 이름 | [hosts 파일](/02-artifacts/network/hosts.md) |
| VPN 을 거친 연결 | [VPN 연결 기록](/02-artifacts/network/vpn-connections.md) |

## 함정과 한계

- **결과가 곧 "지금 열린 연결" 은 아닙니다.** 이미 닫힌 연결의 흔적이 섞일 수 있습니다. 상태 칸과 두 플러그인 결과를 함께 보고 가립니다.
- **확보 과정의 연결이 섞입니다.** 이미지를 네트워크 공유로 보냈거나 원격으로 확보했다면 그 연결이 결과에 보일 수 있습니다.
- **소유 프로세스가 정상 프로그램으로 보일 수 있습니다.** 주입한 코드가 연결을 열면 연결의 주인은 주입당한 정상 프로세스입니다. [코드 주입·숨긴 프로세스 탐지](/03-techniques/analysis/memory-forensics/injection-rootkit.md) 를 봅니다.
- **원격 주소는 상대방의 신원이 아닙니다.** 프록시나 VPN 을 거치면 결과의 원격 주소는 실제 상대가 아닙니다.
- **시각 기준을 확인합니다.** 생성 시각이 나오면 UTC 인지 도구 설정과 출력으로 확인합니다. 이 글의 참고 문헌으로는 확인하지 못했습니다.
- **칸 이름과 칸 수는 버전마다 다를 수 있습니다.** 보고서에는 쓴 도구의 버전과 플러그인 이름을 적습니다.

## 결과를 어떻게 해석하나

- 연결 흔적은 확보한 순간 무렵에 메모리에 있던 연결 객체를 보여 줍니다.
- 연결 흔적은 주소·포트·상태를 알려 줍니다. 주고받은 내용은 알려 주지 않습니다.
- 흔적이 없다고 해서 연결이 없었다는 뜻은 아닙니다. 확보하기 전에 닫히고 흔적이 덮였을 수 있습니다.
- 한 가지 기록으로 결론 내지 않습니다. 디스크 기록과 시각·프로세스·주소가 맞을 때 근거가 단단해집니다.

보고서 문장 예입니다.

- 쓰지 않을 문장: "악성코드가 공격자 서버로 자료를 보냈습니다."
- 쓸 문장: "○○(UTC) 에 확보한 메모리 이미지에서 windows.netscan 결과에 PID ○○(○○.exe) 가 소유한 TCP 연결 흔적이 있습니다. 원격 주소는 ○○, 포트는 ○○, 상태 칸 값은 ○○ 입니다. 같은 항목이 windows.netstat 결과에도 있습니다. 이 기록은 확보한 무렵 이 프로세스와 이 원격 주소 사이에 연결 객체가 있었음을 보여 줍니다. 무엇을 얼마나 주고받았는지는 이 기록으로 알 수 없습니다."

## 도구

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| Volatility 3 (공개) | windows.netscan·windows.netstat 로 연결 흔적을, windows.strings·windows.vadyarascan 으로 문자열을 봅니다 [2] |

## 함께 볼 페이지

- [프로세스와 DLL 분석](/03-techniques/analysis/memory-forensics/process-analysis.md) — 연결의 소유 프로세스를 잇는 목록입니다.
- [메모리 속 문자열·자격증명·암호 키](/03-techniques/analysis/memory-forensics/strings-credentials-keys.md) — 주소·URL 문자열 검색입니다.
- [네트워크 연결 이벤트](/02-artifacts/event-logs/wlan-autoconfig-networkprofile.md) · [네트워크 목록](/02-artifacts/network/networklist.md) — 이 PC 가 어느 네트워크에 붙어 있었는지 봅니다.
- [웹 사용 행위 재구성](/04-scenarios/activity/web-activity.md) — 브라우저 쪽 기록과 잇습니다.

## 참고 문헌

1. IETF, RFC 3227 "Guidelines for Evidence Collection and Archiving" (BCP 55, 2002-02) — https://www.rfc-editor.org/rfc/rfc3227
2. Volatility 3 documentation, "volatility3.plugins.windows package" (latest) — https://volatility3.readthedocs.io/en/latest/volatility3.plugins.windows.html
