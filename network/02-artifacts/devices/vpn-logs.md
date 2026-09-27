---
title: "VPN 서버 로그"
parent: "아티팩트 · 네트워크 장비와 서버 로그"
nav_order: 290
---

# VPN 서버 로그 (OpenVPN·WireGuard)

VPN 서버 로그로는 어느 계정이나 인증서가 어느 외부 IP 에서 들어와 어떤 가상 IP 를 받았는지 알 수 있어서, 내부 방화벽·프록시·흐름 기록에 나오는 가상 IP 를 바깥의 실제 접속 주소와 이을 수 있습니다. OpenVPN 은 텍스트 로그와 상태 파일을 남기지만 기본 설정에서는 남기는 줄이 적습니다. WireGuard 는 접속 이력을 기록하지 않고 실행 중인 메모리 상태만 들고 있어서, 언제 무엇을 수집했는지에 따라 알 수 있는 범위가 크게 달라집니다.

## 무엇을 기록하나 · 왜 생기나

원격 접속 VPN 서버는 클라이언트를 인증한 뒤 가상 IP 를 하나 나눠 주고, 그 뒤 클라이언트의 트래픽은 이 가상 IP 로 내부망에 들어옵니다. 내부 서버의 로그에는 가상 IP 만 남기 때문에, "10.8.0.6 이 그 시각에 누구였나" 는 VPN 서버 기록으로만 풀 수 있습니다. [DHCP 로그](dhcp-logs.md)가 내부 IP 를 MAC 주소와 잇듯이, VPN 서버 기록은 가상 IP 를 인증서 이름·사용자 이름·외부 IP 와 잇습니다.

OpenVPN 서버는 세 종류의 기록을 남깁니다. 첫째는 로그 메시지로, 인증서 확인, 접속 성립, 가상 IP 할당, 오류가 한 줄씩 남습니다[1][2]. 둘째는 상태 파일(`--status`)로, 지금 접속 중인 클라이언트 목록과 경로 표를 정해진 간격마다 새로 씁니다[1][2]. 셋째는 관리자가 붙인 스크립트의 기록입니다. OpenVPN 은 접속과 종료 때 스크립트를 부르면서 인증서 이름, 실제 주소, 가상 IP, 세션 길이, 주고받은 바이트 수를 환경 변수로 넘기고, 스크립트가 이 값을 파일이나 DB 에 적어 두는 곳이 많습니다[1].

WireGuard 는 되도록 조용하게 동작하도록 만든 프로토콜입니다. 인증되지 않은 패킷에는 응답하지 않고, 보낼 데이터가 없으면 패킷도 보내지 않습니다[8][9][10]. 로그 파일은 기본으로 없고, 서버가 알고 있는 것은 피어(peer)마다 마지막 외부 주소, 마지막 핸드셰이크 시각, 누적 송수신 바이트뿐입니다[11][12]. 이 값은 `wg show` 로 읽는 메모리 상태라서 인터페이스를 내리거나 재부팅하면 사라집니다.

## 위치와 버전별 차이

아래 내용은 OpenVPN 2.6 매뉴얼과 release/2.6 소스 기준입니다. 로그 줄 모양은 매뉴얼에 정해져 있지 않고 소스 코드가 정하므로, 다른 버전의 로그는 실제 파일로 한 번 더 확인합니다.

| 기록 | 위치·설정 | 남는 것 | 보존 |
|---|---|---|---|
| OpenVPN 로그(파일) | `--log file` 또는 `--log-append file` | 줄마다 현지 시각 + 메시지 | `--log` 는 시작할 때 기존 파일을 비우고, `--log-append` 는 이어 씁니다[1] |
| OpenVPN 로그(syslog) | `--daemon [progname]` 또는 `--syslog progname`, 이름 기본값 `openvpn` | 시각 없이 메시지만 넘기고 syslog 가 시각을 붙입니다 | syslog 회전 설정을 따릅니다[1][4] |
| OpenVPN 로그(Windows 서비스) | 서비스로 실행하면 `--log` 없이도 파일로 기록합니다[1] | 파일 로그와 같습니다 | 서비스 설정에서 경로를 확인합니다 |
| OpenVPN 상태 파일 | `--status file [n]`, 간격 기본 60초 | 지금 접속 중인 클라이언트와 경로 표 | 간격마다 덮어써서 이력이 없습니다[1] |
| 가상 IP 기억 파일 | `--ifconfig-pool-persist file [seconds]`, 간격 기본 600초 | `Common-Name,IP-address` 쉼표 줄 | 시작·종료 때와 간격마다 다시 씁니다[1] |
| 접속·종료 스크립트 기록 | `--client-connect`·`--client-disconnect` 로 부르는 스크립트 | 스크립트가 적기로 한 환경 변수 | 스크립트마다 다릅니다 |
| WireGuard 상태 | `wg show`, `wg show all dump` | 피어별 엔드포인트·마지막 핸드셰이크·송수신 바이트 | 메모리에만 있습니다[11][12] |
| WireGuard 설정 | `wg showconf`, wg-quick 설정 파일 | 피어 공개 키와 `AllowedIPs` | 파일로 남습니다[9][11] |
| WireGuard 디버그 출력 | 커널 모듈은 `echo module wireguard +p > /sys/kernel/debug/dynamic_debug/control`, 사용자 공간 구현은 `LOG_LEVEL=verbose` | 켜 둔 동안의 동작 메시지 | 기본은 꺼져 있습니다[9] |

`--log` 나 `--log-append` 가 있으면 `--daemon` 의 syslog 출력보다 우선합니다[1]. 설정 파일에서 이 세 옵션을 먼저 찾아야 로그가 파일에 있는지 syslog 에 있는지 알 수 있습니다. 로그 파일은 SIGHUP·SIGUSR1·ping-restart 로 다시 열리지 않으므로, 프로세스를 새로 시작할 때만 `--log` 의 비우기가 일어납니다[1].

로그 양은 `--verb` 로 정하고 기본값은 1 입니다. 0 은 치명적 오류만, 1–4 는 일반 운영 범위, 5 는 패킷마다 `R`·`W` 글자를 찍고, 6–11 은 디버그입니다. 출력에 파묻히지 않고 무슨 일이 일어나는지 요약해 보려면 3 이 알맞습니다[1]. 같은 종류의 메시지가 이어지면 `--mute n` 으로 n 개까지만 남길 수 있습니다[1].

상태 파일 형식은 `--status-version` 으로 고릅니다. 1 은 기본값이고 쉼표로 나눈 옛 형식, 2 는 가상 IPv4·IPv6 주소, 사용자 이름, 클라이언트 ID, 피어 ID, 데이터 채널 암호 방식이 더해진 쉼표 형식, 3 은 2 와 같은 내용을 탭으로 나눈 형식입니다[1]. 이 옵션은 다중 클라이언트 서버에만 적용됩니다[1].

## 구조

### OpenVPN 로그 줄

파일이나 표준 출력으로 쓸 때는 줄 앞에 `YYYY-MM-DD HH:MM:SS` 형식의 시각이 붙고, 그 뒤에 클라이언트 접두어와 메시지가 옵니다[4][5]. 로그 수준이 4 이상이면 시각 뒤에 ` us=마이크로초` 가 붙습니다[4][5][6]. `--suppress-timestamps` 를 주면 시각이 빠지고, `--machine-readable-output` 을 주면 줄 앞이 `에포크초.마이크로초 플래그16진수` 로 바뀝니다[1][4]. syslog 로 보낼 때는 접두어와 메시지만 넘깁니다[4].

서버 모드의 접두어는 `인증서CN/실제주소:포트` 이고, 인증서 확인이 끝나기 전에는 `실제주소:포트` 만 붙습니다[2]. 한 클라이언트의 줄을 모으려면 이 접두어로 찾습니다.

아래 표는 조사에서 주로 쓰는 메시지와 그 메시지가 찍히는 최소 `--verb` 입니다[2][3][6][7].

| 메시지 | 뜻 | 최소 verb |
|---|---|---|
| `[CN] Peer Connection Initiated with [AF_INET]주소:포트` | 인증을 마치고 터널이 맺어짐 | 1 |
| `MULTI_sva: pool returned IPv4=…, IPv6=…` | 주소 풀에서 가상 IP 를 할당 | 1 |
| `MULTI: no free --ifconfig-pool addresses are available` | 풀에 남은 주소가 없음 | 1 |
| `TLS Error: TLS handshake failed` | TLS 핸드셰이크 실패 | 1 |
| `TLS Auth Error: Auth Username/Password verification failed for peer` | 사용자 이름·비밀번호 확인 실패 | 1 |
| `VERIFY ERROR: …` | 인증서 확인 실패 | 1 |
| `VERIFY OK: depth=N, 주체` | 인증서 체인의 N 번째 단계 확인 성공(0 이 클라이언트 인증서) | 2 |
| `MULTI: Learn: 가상주소 -> CN/실제주소` | 가상 주소를 이 클라이언트 경로로 등록 | 3 |
| `MULTI: primary virtual IP for CN/실제주소: 가상IP` | 이 클라이언트의 대표 가상 IP | 3 |
| `MULTI: new connection by client 'CN' will cause previous active sessions by this client to be dropped. …` | 같은 CN 의 새 접속 때문에 이전 세션을 끊음 | 3 |
| `MULTI: connection rejected: …` | 접속 거부 | 3 |

기본값 verb 1 에서는 `Learn` 줄과 `primary virtual IP` 줄이 없습니다. 이때 가상 IP 는 `pool returned` 줄이나 상태 파일에서 찾습니다.

### OpenVPN 상태 파일

버전 2 파일은 다음 순서로 되어 있습니다(값은 만든 예시, 형식은 소스 기준)[2].

```
TITLE,OpenVPN 2.6.12 …
TIME,2026-09-27 11:40:30,1790476830
HEADER,CLIENT_LIST,Common Name,Real Address,Virtual Address,Virtual IPv6 Address,Bytes Received,Bytes Sent,Connected Since,Connected Since (time_t),Username,Client ID,Peer ID,Data Channel Cipher
CLIENT_LIST,alice,198.51.100.44:51514,10.8.0.6,,48213,91022,2026-09-27 10:15:02,1790471702,UNDEF,3,0,AES-256-GCM
HEADER,ROUTING_TABLE,Virtual Address,Common Name,Real Address,Last Ref,Last Ref (time_t)
ROUTING_TABLE,10.8.0.6,alice,198.51.100.44:51514,2026-09-27 11:40:11,1790476811
GLOBAL_STATS,Max bcast/mcast queue length,0
GLOBAL_STATS,dco_enabled,0
END
```

`Real Address` 는 서버가 본 클라이언트의 외부 주소와 포트이고, `Bytes Received`·`Bytes Sent` 는 서버가 그 클라이언트에게서 받고 보낸 바이트 수입니다[2]. `Connected Since` 는 서버가 이 클라이언트 연결을 만든 시각이고, `Last Ref` 는 그 가상 주소 경로를 마지막으로 쓴 시각입니다[2]. 사용자 이름이 없으면 `Username` 에 `UNDEF` 가 들어갑니다[7]. 경로 표의 가상 주소 뒤에 `C` 가 붙으면 캐시된 경로입니다[2]. 버전 1 파일은 `OpenVPN CLIENT LIST`, `Updated,시각`, `Common Name,Real Address,Bytes Received,Bytes Sent,Connected Since`, `ROUTING TABLE`, `GLOBAL STATS`, `END` 순서이고 에포크 시각 열이 없습니다[2].

### OpenVPN 스크립트 환경 변수

접속·종료 스크립트를 두는 서버라면 아래 변수가 스크립트 기록에 들어 있을 수 있습니다[1].

| 변수 | 뜻 | 설정되는 때 |
|---|---|---|
| `common_name` | 인증된 클라이언트 인증서의 CN | client-connect·client-disconnect·auth-user-pass-verify 전 |
| `trusted_ip`·`trusted_ip6`·`trusted_port` | 인증된 클라이언트의 실제 주소·포트 | client-connect·client-disconnect 전 |
| `untrusted_ip`·`untrusted_port` | 아직 인증되지 않은 접속의 주소·포트 | tls-verify·auth-user-pass-verify 전 |
| `ifconfig_pool_remote_ip` | 클라이언트에 준 가상 IPv4 | client-connect·client-disconnect 전 |
| `time_unix`·`time_ascii` | 접속 시각(에포크 정수, 사람이 읽는 문자열) | client-connect 전 |
| `time_duration` | 끊기는 세션의 길이(초) | client-disconnect 전 |
| `bytes_received`·`bytes_sent` | 세션 동안 클라이언트에게서 받은·보낸 바이트 합계 | client-disconnect 전 |
| `username` | 클라이언트가 보낸 사용자 이름 | `via-env` 방식의 auth-user-pass-verify 전 |
| `tls_serial_{n}`·`tls_digest_sha256_{n}`·`X509_{n}_{필드}` | n 단계 인증서의 일련번호·SHA-256 지문·주체 필드 | tls-verify 전 |

클라이언트가 보내는 `IV_VER`(OpenVPN 버전)와 `IV_PLAT`(운영체제)도 스크립트 환경 변수로 넘어옵니다[1][7]. 클라이언트가 `--push-peer-info` 를 켰다면 `IV_HWADDR` 도 오는데, OpenVPN 2.x 는 기본 게이트웨이로 나가는 인터페이스의 MAC 주소를 이 값으로 씁니다[1].

`--script-security` 기본값은 1 이라 사용자 스크립트를 부르지 않습니다. 스크립트 기록이 있으려면 이 값이 2 이상이어야 하고, 3 이면 비밀번호도 환경 변수로 넘어갑니다[1].

### WireGuard 상태

`wg show 인터페이스 dump` 는 탭으로 나눈 여러 줄을 출력합니다. 첫 줄은 인터페이스의 개인 키, 공개 키, 수신 포트, fwmark 이고, 이후 피어마다 공개 키, 사전 공유 키, 엔드포인트, allowed-ips, 마지막 핸드셰이크, 받은 바이트, 보낸 바이트, persistent-keepalive 가 한 줄씩 나옵니다[11]. `wg show all dump` 는 줄마다 인터페이스 이름이 앞에 붙습니다[12]. 마지막 핸드셰이크는 에포크 초이고 한 번도 없으면 `0` 입니다. 엔드포인트나 사전 공유 키가 없으면 `(none)`, keepalive 가 꺼져 있으면 `off` 로 나옵니다[12].

엔드포인트는 그 피어에게서 마지막으로 인증에 성공한 패킷의 바깥 출발지 IP·포트로 바뀝니다[10]. 피어가 다른 네트워크로 옮기면 새 주소로 덮이고 이전 주소는 남지 않습니다.

## 증거로서 의미

### 증명하는 것

OpenVPN 로그와 상태 파일로는 "이 시각에 이 인증서 CN(또는 사용자 이름)으로 이 외부 IP·포트에서 접속해 이 가상 IP 를 받았다" 를 보일 수 있습니다[2][3]. 상태 파일이나 client-disconnect 스크립트 기록이 있으면 그 세션에서 주고받은 바이트 수와 세션 길이도 보일 수 있습니다[1][2]. 인증 실패 줄(`TLS Auth Error`·`VERIFY ERROR`)로는 어느 외부 주소에서 몇 번 실패했는지 셀 수 있습니다[7].

WireGuard 는 수집한 그 시점에 한해 피어 공개 키마다 마지막 엔드포인트, 마지막 핸드셰이크 시각, 누적 송수신 바이트, 그 키에 허용된 가상 주소(allowed-ips)를 보여 줍니다[11][12]. 설정 파일의 `[Peer]` 공개 키와 `AllowedIPs` 로 어떤 가상 IP 가 어느 키에 묶여 있는지 알 수 있습니다.

### 증명하지 못하는 것

- **인증서나 키를 쓴 사람.** 로그에 남는 것은 인증서 CN, 사용자 이름, WireGuard 공개 키입니다. 인증서와 비밀번호는 여러 사람이 나눠 쓸 수 있고, `--duplicate-cn` 을 켠 서버는 같은 CN 의 동시 접속을 허용합니다[1].
- **실제 기기의 주소.** `Real Address`·`trusted_ip`·WireGuard 엔드포인트는 서버가 본 바깥 주소라서, 클라이언트가 NAT 뒤에 있으면 공유기나 통신사 NAT 장비의 주소입니다. NAT 뒤 주소를 해석하는 방법은 [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md)에 있습니다.
- **터널 안에서 한 일.** VPN 서버 로그에는 내부에서 어느 서버에 접속했는지가 없습니다. 가상 IP 와 시각으로 내부 방화벽·프록시·흐름 기록을 찾아야 합니다.
- **WireGuard 의 접속 이력.** 과거 핸드셰이크, 이전 엔드포인트, 끊긴 시각은 어디에도 남지 않습니다[10][12].
- **기본 설정의 세부 기록.** verb 1 에서는 가상 주소 학습 줄과 인증서 확인 성공 줄이 없습니다[6].

## 시각 해석

| 값 | 뜻 | 기준 |
|---|---|---|
| OpenVPN 파일 로그 줄 앞 시각 | 메시지를 쓴 시각 | 서버의 현지 시각, 시간대 표시 없음[5] |
| OpenVPN syslog 줄 시각 | syslog 가 받은 시각 | RFC 3164 형식이면 현지 시각, 연도 없음[4][17] |
| `--machine-readable-output` 줄 앞 | 메시지를 쓴 시각 | 에포크 초.마이크로초[4] |
| 상태 파일 `TIME`·`Updated` | 상태 파일을 쓴 시각 | 사람이 읽는 값은 현지 시각, `TIME` 의 셋째 값은 에포크[2][5] |
| `Connected Since` | 서버가 그 클라이언트 연결을 만든 시각 | 현지 시각, 버전 2·3 의 `(time_t)` 열은 에포크[2] |
| `Last Ref` | 그 가상 주소 경로를 마지막으로 쓴 시각 | 위와 같음[2] |
| `time_unix`·`time_duration` | 접속 시각, 끊길 때의 세션 길이 | 에포크 정수, 초[1] |
| WireGuard 마지막 핸드셰이크 | 마지막으로 성공한 핸드셰이크 | dump 는 에포크 초, 사람용 출력은 "N ago" 상대 시간[12] |

OpenVPN 로그의 시각에는 시간대가 없으므로 서버의 시간대 설정을 먼저 확인합니다. 같은 파일 안에서도 로그 줄은 현지 시각이고 상태 파일의 `(time_t)` 열은 에포크라서, 두 값을 합칠 때 변환을 빠뜨리기 쉽습니다. 여러 기록의 시각을 맞추는 방법은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md)에 있습니다.

WireGuard 는 트래픽이 이어지는 동안 약 2분(Rekey-After-Time 120초)마다 새 핸드셰이크를 맺습니다[10]. 그래서 마지막 핸드셰이크가 몇 분 전이면 그 무렵까지 트래픽이 있었을 가능성이 높습니다. 반대로 핸드셰이크가 오래전이라고 해서 설정이 지워졌거나 피어가 끊겼다고 단정하지는 않습니다. 양쪽 모두 보낼 데이터가 없으면 링크가 조용해질 뿐이고, 180초(Reject-After-Time)의 세 배 동안 새 세션이 없으면 세션 키를 지우지만 피어 설정은 그대로 남습니다[10].

## 함정과 한계

**재시작하면 로그가 비워질 수 있습니다.** `--log` 는 기존 파일을 비우고 새로 씁니다[1]. 서버를 다시 시작한 뒤라면 그 전 기록은 파일에 없으므로, 설정이 `--log` 인지 `--log-append` 인지 먼저 확인하고 백업이나 syslog 사본을 찾습니다.

**상태 파일은 한 순간의 스냅숏입니다.** 기본 60초마다 덮어쓰고 지금 접속 중인 클라이언트만 담습니다[1]. 과거 접속은 누군가 주기적으로 상태 파일을 복사해 두었을 때만 남습니다. SIGUSR2 를 보내면 같은 내용이 syslog 에도 남습니다[1].

**가상 IP 기억 파일은 접속 기록이 아닙니다.** `--ifconfig-pool-persist` 파일은 CN 과 가상 IP 의 대응을 다음 접속 때 다시 주려고 적어 두는 "제안" 목록입니다. 그 CN 이 언제 접속했는지는 없고, 같은 IP 를 받는다는 보장도 없습니다[1].

**가상 IP 는 다시 쓰입니다.** 한 클라이언트가 끊기면 그 주소가 다른 클라이언트에게 갈 수 있습니다. 가상 IP 를 사람과 이을 때는 반드시 그 시각의 할당 기록(로그 줄이나 스크립트 기록)으로 확인합니다.

**같은 CN 의 새 접속은 이전 세션을 끊습니다.** `--duplicate-cn` 이 없으면 같은 CN 이 새로 접속할 때 이전 세션을 끊고, verb 3 이상이면 그 사실이 로그에 남습니다[1][2]. 서로 다른 외부 IP 에서 같은 CN 이 번갈아 끊기면 인증서를 두 곳 이상에서 쓰고 있을 가능성이 있습니다.

**바이트 수에 DCO 카운터가 더해집니다.** 커널 데이터 채널 오프로드 (Data Channel Offload, DCO)를 쓰는 서버의 상태 파일 바이트 수는 사용자 공간 카운터와 DCO 카운터를 더한 값입니다[2]. `GLOBAL_STATS,dco_enabled` 로 켜져 있었는지 확인합니다.

**`wg show all dump` 출력에는 개인 키가 들어 있습니다.** 사람용 `wg show` 는 개인 키와 사전 공유 키를 `(hidden)` 으로 감추지만(환경 변수 `WG_HIDE_KEYS=never` 이면 보여 줍니다) dump 는 그대로 찍습니다[11][12]. 이 출력을 증거로 보관할 때는 비밀 정보로 다룹니다.

**WireGuard 는 스캔으로 찾기 어렵습니다.** 인증되지 않은 패킷에 응답하지 않아 포트 스캔에 드러나지 않고[8][10], 표준 포트도 없습니다[15]. 문서 예시의 51820 은 예시 값일 뿐입니다[9]. 패킷에서는 UDP 페이로드 첫 바이트가 1–4 이고 다음 3바이트가 0 인 모양으로 찾습니다[8][15]. 핸드셰이크 사이에 트래픽이 없으면 흐름 기록에도 빈 구간이 생깁니다[10].

## 직접 분석해 보기

### 헥스로 한 번

WireGuard 메시지는 UDP 페이로드 앞 4바이트가 종류 1바이트와 0 세 바이트이고, 인덱스와 카운터는 리틀 엔디언입니다[8]. 아래는 명세의 구조로 만든 핸드셰이크 시작 메시지의 앞부분입니다.

```
오프셋  바이트                     뜻
0       01                         message_type = 1 (handshake_initiation)
1       00 00 00                   reserved_zero
4       5C 3A 91 0E                sender_index (리틀 엔디언 0x0E913A5C)
8       (32바이트)                 unencrypted_ephemeral
40      (48바이트)                 encrypted_static = 32 + 인증 태그 16
88      (28바이트)                 encrypted_timestamp = 12 + 16
116     (16바이트)                 mac1
132     (16바이트)                 mac2
```

AEAD_LEN(n) 은 n + 16 이므로 핸드셰이크 시작 메시지는 148바이트, 응답(종류 2)은 92바이트, 쿠키 응답(종류 3)은 64바이트입니다[8]. 데이터 메시지(종류 4)는 16바이트 머리(종류·0·receiver_index·8바이트 counter) 뒤에 암호문이 오고, 평문을 16의 배수로 채운 뒤 암호화합니다[8]. 빈 평문을 보내는 keepalive 는 암호문이 인증 태그 16바이트뿐이라 UDP 페이로드가 32바이트입니다[8][10]. 핸드셰이크 시작 메시지의 시각(TAI64N)은 암호화되어 있어 키 없이는 읽을 수 없습니다[8][10].

OpenVPN 상태 파일은 텍스트라서 헥스로 볼 것이 없습니다. 대신 `CLIENT_LIST` 줄의 `Connected Since (time_t)` 값을 직접 바꿔 봅니다. 만든 예시의 `1790471702` 를 `date -u -d @1790471702` 로 바꾸면 2026-09-27 01:15:02 UTC 이고, 같은 줄의 현지 시각 `2026-09-27 10:15:02` 와 9시간 차이가 나므로 이 서버의 시간대가 UTC+9 라는 것을 확인할 수 있습니다.

### 공개 도구로 한 번

OpenVPN 파일 로그에서 한 클라이언트의 접속과 가상 IP 할당을 뽑습니다. 아래 로그는 verb 3 서버를 가정한 만든 예시입니다.

```
2026-09-27 10:15:01 198.51.100.44:51514 VERIFY OK: depth=1, CN=Example VPN CA
2026-09-27 10:15:01 198.51.100.44:51514 VERIFY OK: depth=0, CN=alice
2026-09-27 10:15:02 198.51.100.44:51514 [alice] Peer Connection Initiated with [AF_INET]198.51.100.44:51514
2026-09-27 10:15:02 alice/198.51.100.44:51514 MULTI_sva: pool returned IPv4=10.8.0.6, IPv6=(Not enabled)
2026-09-27 10:15:02 alice/198.51.100.44:51514 MULTI: Learn: 10.8.0.6 -> alice/198.51.100.44:51514
2026-09-27 10:15:02 alice/198.51.100.44:51514 MULTI: primary virtual IP for alice/198.51.100.44:51514: 10.8.0.6
```

```
# 접속 성립과 가상 IP 할당 줄만
grep -E "Peer Connection Initiated|pool returned|primary virtual IP" openvpn.log

# 가상 IP 10.8.0.6 을 받은 CN 과 외부 주소
grep -E "pool returned IPv4=10\.8\.0\.6," openvpn.log | awk '{print $1, $2, $3}'

# 인증 실패를 외부 주소별로 세기
grep -E "TLS Auth Error|VERIFY ERROR|TLS handshake failed" openvpn.log | awk '{print $3}' | sed 's#.*/##; s#:[0-9]*$##' | sort | uniq -c | sort -rn
```

상태 파일 버전 2 는 쉼표 CSV 라서 `CLIENT_LIST` 줄만 골라 열을 뽑으면 됩니다.

```
awk -F, '$1=="CLIENT_LIST"{print $2, $3, $4, $6, $7, $9}' openvpn-status.log
```

WireGuard 는 서버가 실행 중일 때 상태를 떠 두는 것이 전부입니다. 수집 시각과 함께 저장합니다.

```
date -u +%s; wg show all dump
```

피어 줄은 다음과 같은 모양입니다(만든 예시).

```
wg0	bWFkZS11cC1leGFtcGxlLWtleS0wMDAwMDAwMDAwMDA=	(none)	198.51.100.44:48213	10.9.0.2/32	1790476811	1843200	7340032	off
```

`all dump` 에서는 맨 앞에 인터페이스 이름이 붙으므로 여섯째 값이 마지막 핸드셰이크이고, 이 값과 앞에 적은 수집 시각의 차이가 그 피어의 마지막 활동 이후 흐른 초입니다.

패킷 캡처에서는 Wireshark 표시 필터로 VPN 트래픽을 찾습니다. WireGuard 는 `wg.type == 1`(핸드셰이크 시작), `wg.keepalive`, `wg.sender`·`wg.receiver`(세션 인덱스)를 씁니다[13]. OpenVPN 은 `openvpn.opcode`, `openvpn.sessionid`, `openvpn.peerid` 를 씁니다[14]. 조사 대상 환경에 WireGuard 키 로그 파일이 이미 있다면 `editcap --inject-secrets wg,키로그파일` 로 캡처에 넣으면 Wireshark 에서 터널 안의 패킷을 복호화해 볼 수 있습니다[15][16].

## 교차 검증

| 함께 볼 기록 | 알 수 있는 것 | 링크 |
|---|---|---|
| 방화벽 로그·흐름 기록 | VPN 서버 포트로 들어온 외부 주소와 세션 길이, 가상 IP 가 내부에서 접속한 곳 | [방화벽 로그](firewall-logs.md), [흐름 기록](../../01-foundations/records/flow-records.md) |
| Zeek `conn.log` | 터널 바깥 UDP·TCP 세션의 시작 시각과 바이트 수 | [연결 기록](../zeek/zeek-logs/conn-log.md) |
| 프록시·DNS 서버 로그 | 가상 IP 가 요청한 웹 주소와 도메인 | [웹 프록시 로그](proxy-logs.md), [DNS 서버 로그](dns-server-logs.md) |
| DHCP 로그 | 같은 사람이 사내에서 쓰는 기기의 IP·MAC | [DHCP 로그](dhcp-logs.md) |
| 호스트 쪽 VPN 흔적 | 클라이언트 PC·휴대폰의 VPN 설정과 연결 기록 | [Windows VPN 연결 기록](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/vpn-connections.html), [Linux VPN](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/vpn.html), [macOS VPN 구성](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/network/vpn.html), [Android VPN 설정](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/network/vpn.html), [iOS VPN 설정](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/network/vpn.html) |

가상 IP 를 사람에게 잇는 전체 흐름은 [이 시각에 이 IP 를 누가 썼나](../../04-scenarios/user-activity/ip-attribution.md)에, VPN 계정에 비밀번호를 무작위로 넣어 본 흔적은 [비밀번호를 무작위로 넣어 봤나](../../04-scenarios/intrusion/brute-force.md)에 있습니다. 여러 기록을 한 시간순 표로 합치는 방법은 [네트워크 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 실습

Wireshark 시험용 캡처 `wireguard-psk.pcap` 과 `wireguard-ping-tcp.pcap` 의 주소는 Wireshark 위키 WireGuard 페이지에 있습니다[15].

1. 두 캡처에서 `wg.type` 값별 패킷 수를 세고, 종류 1·2 메시지가 있으면 UDP 페이로드 길이가 148·92바이트인지 확인하십시오.
2. 같은 캡처에서 `wg.keepalive` 패킷을 찾아 UDP 페이로드가 32바이트인지 확인하고, 앞뒤 데이터 패킷과의 시간 간격을 보십시오.
3. 종류 1 메시지의 `wg.sender` 값이 종류 2 메시지의 `wg.receiver`, 이후 종류 4 메시지의 `wg.receiver` 와 어떻게 이어지는지 따라가 보십시오.
4. 캡처 필터 `udp[8:1] >= 1 and udp[8:1] <= 4 and udp[9:1] == 0 and udp[10:2] == 0` 을 적용했을 때 WireGuard 가 아닌 UDP 가 섞일 수 있는 경우를 생각해 보십시오[15].
5. 이 페이지의 만든 예시 로그와 상태 파일로, 11:40 에 10.8.0.6 을 쓴 CN·외부 주소·접속 시작 시각(UTC)을 한 문장으로 쓰십시오. 로그 줄의 시각과 상태 파일의 `(time_t)` 열이 같은 순간을 가리키는지 확인하십시오.

## 참고 문헌

1. OpenVPN Inc., "Reference manual for OpenVPN 2.6". https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/
2. OpenVPN 소스 release/2.6, src/openvpn/multi.c. https://github.com/OpenVPN/openvpn/blob/release/2.6/src/openvpn/multi.c
3. OpenVPN 소스 release/2.6, src/openvpn/socket.c. https://github.com/OpenVPN/openvpn/blob/release/2.6/src/openvpn/socket.c
4. OpenVPN 소스 release/2.6, src/openvpn/error.c. https://github.com/OpenVPN/openvpn/blob/release/2.6/src/openvpn/error.c
5. OpenVPN 소스 release/2.6, src/openvpn/otime.c. https://github.com/OpenVPN/openvpn/blob/release/2.6/src/openvpn/otime.c
6. OpenVPN 소스 release/2.6, src/openvpn/errlevel.h. https://github.com/OpenVPN/openvpn/blob/release/2.6/src/openvpn/errlevel.h
7. OpenVPN 소스 release/2.6, src/openvpn/ssl.c, src/openvpn/ssl_verify.c. https://github.com/OpenVPN/openvpn/blob/release/2.6/src/openvpn/ssl.c , https://github.com/OpenVPN/openvpn/blob/release/2.6/src/openvpn/ssl_verify.c
8. WireGuard, "Protocol & Cryptography". https://www.wireguard.com/protocol/
9. WireGuard, "Quick Start". https://www.wireguard.com/quickstart/
10. Jason A. Donenfeld, "WireGuard: Next Generation Kernel Network Tunnel", 백서 초안판 e2da747(2020-06-01), NDSS 2017 발표 논문의 수정판. https://www.wireguard.com/papers/wireguard.pdf
11. wireguard-tools, wg(8) 매뉴얼. https://github.com/WireGuard/wireguard-tools/blob/master/src/man/wg.8
12. wireguard-tools 소스, src/show.c. https://github.com/WireGuard/wireguard-tools/blob/master/src/show.c
13. Wireshark Foundation, 표시 필터 참조 "WireGuard Protocol (wg)". https://www.wireshark.org/docs/dfref/w/wg.html
14. Wireshark Foundation, 표시 필터 참조 "OpenVPN Protocol (openvpn)". https://www.wireshark.org/docs/dfref/o/openvpn.html
15. Wireshark Wiki, "WireGuard". https://wiki.wireshark.org/WireGuard
16. Wireshark Foundation, editcap 매뉴얼(doc/man_pages/editcap.adoc). https://github.com/wireshark/wireshark/blob/master/doc/man_pages/editcap.adoc
17. C. Lonvick, "The BSD syslog Protocol", RFC 3164, 2001. https://www.rfc-editor.org/rfc/rfc3164.txt
