---
title: "비밀번호를 무작위로 넣어 봤나"
parent: "시나리오 · 침입"
nav_order: 480
---

# 비밀번호를 무작위로 넣어 봤나 (Brute Force)

한 출발지가 SSH·RDP·FTP·웹 로그인·도메인 인증(Kerberos·NTLM)에 짧은 시간 동안 여러 번 로그인을 시도했는지, 그중 하나라도 성공했는지를 네트워크 기록으로 확인하는 순서를 다룹니다. 암호화된 프로토콜에서는 네트워크 기록만으로 성공을 확정하지 못하는 경우가 많아서, 연결 수·크기·시간 간격으로 성공 후보를 좁히고 서버 쪽 인증 로그로 확정합니다. 각 로그의 필드 설명은 아티팩트 페이지에 있고, 이 페이지는 어떤 필드를 어떤 순서로 보는지만 씁니다.

## 조사 질문

- 한 출발지가 짧은 시간에 같은 서비스로 연결을 몇 번 열었고, 그중 몇 번이 인증 실패로 끝났나.
- 그중 크기·길이가 다른 연결, 곧 성공했을 가능성이 있는 연결이 있나. 있다면 언제인가.
- 계정 하나에 여러 비밀번호를 넣었나, 아니면 여러 계정에 몇 번씩 돌려 넣었나(비밀번호 뿌리기 (password spraying)).
- 같은 출발지가 대입 전후에 다른 서비스나 다른 서버로도 연결했나. 성공 후보 뒤에 무엇을 했나.

## 먼저 확인할 것

**센서 위치와 수집 범위.** 외부에서 들어온 대입은 경계 센서에 남지만, 같은 스위치 안의 PC 끼리 주고받은 인증은 경계 센서를 지나지 않습니다. 어느 구간의 트래픽이 기록됐는지 먼저 확인합니다([어디서 캡처하나](../../01-foundations/capture/capture-points.md)).

**출발지 주소가 한 사람인가.** NAT·프록시·VPN 뒤에서는 여러 사용자가 한 IP 로 보입니다. 대입을 한 "사람" 을 말하려면 [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md) 과 [이 시각에 이 IP 를 누가 썼나](../user-activity/ip-attribution.md) 를 함께 봅니다.

**시각의 기준.** 로그마다 `ts` 가 가리키는 순간이 다릅니다. conn.log 는 연결의 첫 패킷 시각[1], ssh.log 는 SSH 연결이 시작된 시각[4], kerberos.log·ntlm.log·rdp.log 는 해당 이벤트가 일어난 시각[15][18][3], ftp.log 는 명령을 보낸 시각[10], http.log 는 요청 시각[24]입니다. Zeek 기본 TSV 의 `ts` 는 epoch 초이고 `zeek-cut -d` 로 사람이 읽는 시각으로 바꿉니다[23]. 서버 인증 로그와 시간순으로 합칠 때는 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 에서 시간대와 시계 차이를 먼저 맞춥니다.

**센서에 어떤 탐지 스크립트·규칙이 켜져 있었나.** Zeek 의 무작위 대입 탐지는 기본 분석(base)이 아니라 정책(policy) 스크립트입니다. Zeek 가 함께 배포하는 `local.zeek` 는 SSH 대입 탐지 스크립트(`protocols/ssh/detect-bruteforcing`)를 불러오지만 FTP 대입 탐지 스크립트는 불러오지 않습니다[8]. 센서가 `misc/loaded-scripts` 를 불러왔다면 loaded_scripts.log 에 실제로 불러온 스크립트 목록이 남습니다[9]. 이 목록에 탐지 스크립트가 없으면 notice.log 에 대입 경고가 없는 것이 정상입니다. Suricata 는 규칙마다 임계값 설정이 달라서, 경고가 몇 번 나왔는지는 규칙의 `threshold`·`detection_filter` 를 보고 해석합니다(아래 분석 흐름 5단계).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 흐름 기록 (NetFlow·IPFIX), 방화벽 로그 | 출발지·목적지·포트별 연결 수와 크기. 센서가 없을 때 유일한 기록일 수 있음 | [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md), [방화벽 로그](../../02-artifacts/devices/firewall-logs.md) |
| 2 | Zeek conn.log | 연결마다 `orig_bytes`·`resp_bytes`·`duration`·`conn_state`. 같은 크기 반복과 튀는 연결 | [연결 기록 (conn.log)](../../02-artifacts/zeek/zeek-logs/conn-log.md) |
| 3 | Zeek ssh.log·rdp.log | 프로토콜 확인, SSH 인증 결과 추정값 | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) |
| 4 | Zeek kerberos.log·ntlm.log·ftp.log·http.log | 평문으로 보이는 인증 결과·계정 이름·응답 코드 | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md), [HTTP 기록 (http.log)](../../02-artifacts/zeek/zeek-logs/http-log.md) |
| 5 | Zeek notice.log, Suricata EVE alert | 센서가 임계값을 넘었다고 판단한 출발지 | [경고 기록 (alert)](../../02-artifacts/suricata/eve-json/alert.md), [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md) |
| 6 | VPN 서버 로그 | VPN 로그인 실패·성공 | [VPN 서버 로그](../../02-artifacts/devices/vpn-logs.md) |
| 7 | 서버 쪽 인증 로그 | 계정별 성공·실패 확정 | [Windows RDP 이벤트](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/event-logs/rdp-event-logs/), [Linux SSH](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/ssh/) |

## 분석 흐름

**1. 연결이 몰린 출발지를 찾습니다.** 흐름 기록만 있으면 nfdump 로 출발지·목적지·목적지 포트별로 묶어 연결 수가 많은 순서로 봅니다. `-A` 는 묶는 기준, `-s record/flows` 는 묶은 레코드를 흐름 수 순서로 보여 줍니다[20]. 시간 범위는 `-t` 대신 `first seen`·`last seen` 필터로 겁니다[20].

```
nfdump -r /flows/2026/09/01 -A srcip,dstip,dstport -s record/flows -n 20 \
  'proto tcp and dst port in [22 3389 21] and first seen >= 2026-09-01T00:00:00 and last seen <= 2026-09-01T06:00:00'
```

`flags S and not flags AFRPU` 처럼 TCP 플래그로 거르면 SYN 만 있는 흐름(응답 없는 연결 시도)을 따로 볼 수 있습니다[20]. SYN 만 있는 흐름이 대부분이면 인증까지 가지 않은 포트 스캔일 가능성이 큽니다. Zeek 가 있으면 conn.log 의 `conn_state` 로도 구분할 수 있습니다. `S0` 은 응답 없는 시도, `REJ` 는 거부된 시도, `SF` 는 정상으로 맺고 닫힌 연결입니다[1].

**2. 같은 크기 연결의 반복과 튀는 연결을 찾습니다.** 도구로 로그인을 자동 반복하면 연결마다 주고받는 바이트 수가 같게 남을 수 있습니다[2]. conn.log 를 출발지·목적지·포트·서비스·바이트 수로 묶어 세면 반복 모양이 드러납니다[2].

```
jq -c '[."id.orig_h", ."id.resp_h", ."id.resp_p", ."service", ."orig_bytes", ."resp_bytes"]' conn.log | sort | uniq -c
```

```
     52 ["203.0.113.45","10.0.20.15",3389,"ssl",1392,1238]
      1 ["203.0.113.45","10.0.20.15",3389,"ssl",3380,4870]
```

(만든 예시) 이 모양이면 크기가 다른 한 줄이 성공한 로그인일 가능성이 있습니다. Zeek 문서의 실험(Windows 10 RDP 에 단어 목록 대입)에서는 같은 크기 연결 38개와 크기가 다른 연결 1개가 있었고, 이어진 대화형 세션은 `duration` 약 109초, `resp_bytes` 1823511바이트로 앞의 연결보다 훨씬 컸습니다[2]. TLS 로 보호되는 RDP 는 conn.log `service` 가 `ssl` 로 나옵니다[2]. 크기가 다른 연결은 "성공 후보" 일 뿐입니다(아래 흔한 오판).

`orig_bytes`·`resp_bytes` 는 TCP 시퀀스 번호로 계산해서 큰 연결에서는 틀릴 수 있습니다[1]. 대화형 세션처럼 큰 연결을 비교할 때는 IP 헤더 기준인 `orig_ip_bytes`·`resp_ip_bytes` 도 함께 봅니다[1].

**3. 프로토콜별로 인증 결과가 보이는지 확인합니다.**

*SSH.* ssh.log 의 `auth_success` 는 T 가 성공, F 가 실패, 비어 있으면 알 수 없음입니다[4]. Zeek 는 이 값을 암호화된 패킷의 크기로 추정하고, 조금이라도 의심스러우면 판정하지 않습니다[4]. `auth_attempts` 는 Zeek 가 본 인증 시도 수인데, 2단계 인증을 쓰는 서버에서는 시도가 모두 실패를 뜻하지는 않습니다[4]. ssh.log 에는 사용자 이름 필드가 없어서[4] 계정 하나에 넣었는지 여러 계정에 돌려 넣었는지는 SSH 서버 로그로만 알 수 있습니다. 22번 포트에 붙기만 하고 아무것도 보내지 않은 연결은 `client` 없이 `server` 만 남고 `auth_attempts` 가 0 입니다[5]. 그래서 `client` 문자열이 있는지로 단순 접속 확인과 로그인 시도를 구분합니다.

*RDP.* rdp.log 로는 로그인 성공·실패를 알 수 없습니다. Zeek 문서의 대입 예에서 대입 단계의 rdp.log 39줄은 모두 `result: "encrypted"`, `security_protocol: "HYBRID"` 로 같아서 어느 연결이 성공했는지 알 수 없었습니다[2]. `cookie` 에는 보통 사용자 이름이 들어가지만 전송 중에 최대 9자로 잘리는 경우가 많습니다[3]. RDP 는 2단계의 크기 비교와 Windows 이벤트 로그로 판정합니다.

*FTP.* ftp.log 에 기록하는 명령 목록(`FTP::logged_commands`) 기본값에 USER·PASS 가 없어서, 평문 프로토콜인데도 로그인 시도가 ftp.log 에 줄마다 남지 않습니다[11]. Zeek 9.0.0 부터는 USER·PASS·QUIT 만 있는 세션도 마지막 명령 한 줄을 남기고, 그 전 버전은 이런 세션을 ftp.log 에 아예 남기지 않습니다[12]. `user` 필드 기본값은 `<unknown>` 이고, 비밀번호는 `FTP::default_capture_password` 가 기본 F 라서 남지 않습니다[10]. 로그인 실패 횟수는 아래 FTP 탐지 스크립트의 notice 나 pcap 에서 셉니다.

*Kerberos.* kerberos.log 에는 `request_type`(AS·TGS), `client`, `service`, `success`, `error_msg` 가 있습니다[15]. `error_msg` 에는 서버가 보낸 오류 문장이 있으면 그 문장이, 없으면 오류 코드의 이름이 들어갑니다[17]. 대입과 관련된 오류 이름은 KDC_ERR_C_PRINCIPAL_UNKNOWN(6, 없는 계정), KDC_ERR_PREAUTH_FAILED(24, 사전 인증 실패), KDC_ERR_CLIENT_REVOKED(18, 클라이언트 자격이 취소됨)입니다[16]. 사전 인증이 필요하다는 응답(`NEEDED_PREAUTH` 등)은 기본 설정(`KRB::ignored_errors`)에서 로그에 남기지 않습니다[15]. 출발지별로 실패한 계정 수를 세면 비밀번호 뿌리기인지 계정 하나에 대한 대입인지 구분할 수 있습니다.

```
jq -r 'select(.error_msg=="KDC_ERR_PREAUTH_FAILED") | [."id.orig_h", .client] | @tsv' kerberos.log | sort -u | cut -f1 | uniq -c | sort -rn
```

출발지 하나에 계정 수가 많고 계정마다 실패가 한두 번이면 뿌리기 모양이고, 계정 하나에 실패가 수십 번이면 한 계정을 노린 대입 모양입니다.

*NTLM.* ntlm.log 에는 클라이언트가 보낸 `username`·`domainname`·`hostname` 과 인증 성공 여부 `success` 가 있습니다[18]. Kerberos 와 같은 방법으로 출발지별 계정 수와 실패 수를 셉니다.

*웹 로그인.* http.log 에는 로그인 성공을 뜻하는 필드가 따로 없습니다. 같은 출발지가 로그인 페이지 URI 에 `method`·`status_code`·`response_body_len` 이 같은 요청을 반복하는지 봅니다[24]. 공개 데이터셋(CSE-CIC-IDS2018)을 분석한 사례에서는 무작위 대입 경고가 난 1시간을 15분 단위로 나눠 연결을 묶었고, 모든 HTTP 연결이 로그인 페이지를 요청한 것을 확인해 경고가 실제 공격임을 판정했습니다[22]. HTTPS 이고 센서가 TLS 를 풀지 못하면 http.log 가 없으므로 2단계의 크기 비교로 돌아갑니다([암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md)).

**4. Zeek notice 를 확인합니다.** SSH 대입 탐지 스크립트는 한 출발지의 실패한 SSH 연결이 30분(`SSH::guessing_timeout`) 동안 30번(`SSH::password_guesses_limit`)에 이르면 notice `SSH::Password_Guessing` 을 남깁니다[6]. notice 문장은 "출발지 appears to be guessing SSH passwords (seen in N connections)." 모양이고, `sub` 필드에 "Sampled servers:" 뒤로 대상 서버 주소 표본을 최대 5개 붙입니다[7]. 여기서 "실패한 연결" 은 Zeek 가 크기 분석으로 실패라고 판정한 연결만 뜻합니다[7][4]. 같은 스크립트의 성공 알림 `SSH::Login_By_Password_Guesser` 는 이름만 정의돼 있고 구현되지 않았습니다[7]. 그래서 이 notice 가 없다고 성공이 없었다고 보면 안 됩니다. FTP 탐지 스크립트는 한 출발지가 USER·PASS 명령에 5xx 응답을 15분(`FTP::bruteforce_measurement_interval`) 동안 20번(`FTP::bruteforce_threshold`) 받으면 notice `FTP::Bruteforcing` 을 남깁니다[13][14]. notice.log 읽는 법은 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) 에서 다룹니다.

**5. Suricata 경고 수를 시도 수로 읽지 않습니다.** 규칙에 `threshold` 나 `detection_filter` 가 있으면 매치 수보다 경고 수가 적어집니다[19]. `type threshold` 는 N번째 매치마다 경고하고, `type limit` 은 정해진 시간에 경고를 N번까지만 내고, `type both` 는 둘을 합칩니다[19]. 예를 들어 SIP `401 Unauthorized` 응답을 세는 규칙은 360초 동안 5번 이상이면 6분에 경고를 한 번만 냅니다[19]. `detection_filter` 는 처음 임계값을 넘은 뒤로 매치마다 경고합니다[19]. 그래서 eve.json 의 경고 수는 규칙의 임계값 설정에 따라 실제 시도 수보다 훨씬 적거나, 처음 몇 번의 시도가 빠져 있을 수 있습니다. 시도 수는 conn.log 나 흐름 기록에서 셉니다. 경고의 `flow_id` 로 같은 흐름의 다른 EVE 이벤트를 묶는 법은 [경고 기록 (alert)](../../02-artifacts/suricata/eve-json/alert.md) 에 있습니다.

**6. 성공 후보 뒤의 행동과 같은 출발지의 다른 시간대를 봅니다.** 성공 후보 연결의 `ts` 뒤로 같은 출발지(또는 대상 서버)가 연 연결을 시간순으로 봅니다. 대상 서버가 새 외부 주소로 연결을 열었거나 내부 다른 호스트의 관리 공유에 붙었다면 [C2 통신](c2-communication.md) 이나 [측면 이동](lateral-movement.md) 으로 넘어갑니다. 앞의 공개 데이터셋 사례에서는 같은 공격자 IP 의 전체 연결을 시간대로 나누자 세 구간이 나왔고, 첫 구간은 대입, 두 번째는 URI 에 `<script>` 가 든 XSS, 세 번째는 SQL 삽입이었습니다[22]. 경고가 난 구간만 보지 말고 같은 출발지의 다른 구간도 확인합니다([웹 서버의 취약점을 노렸나](web-exploitation.md)).

**7. 서버 쪽 인증 로그로 확정합니다.** 네트워크 기록으로 좁힌 성공 후보의 시각과 출발지 주소를 서버 인증 로그와 맞춰 봅니다. Windows 는 [RDP 이벤트](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/event-logs/rdp-event-logs/) 와 [원격 데스크톱 침입 확인](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/incident/rdp-intrusion.html), Linux 는 [SSH](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/ssh/) 와 [SSH 로 들어왔나](https://urock-ailab.github.io/forensics-handbook/linux/04-scenarios/intrusion/ssh-intrusion.html) 에서 이어 갑니다.

## 흔한 오판

**ssh.log 값만으로 "시도 없음" 이라고 쓰는 경우.** Zeek 문서의 예에서 틀린 비밀번호 한 번과 빈 입력 두 번으로 로그인에 실패한 연결이 `auth_success` 없이 `auth_attempts: 0` 으로 남았습니다[5]. 필드 설명은 `auth_attempts` 가 "항상 최소 1" 이라고 하지만[4] 실제 출력 예에는 0 이 나옵니다[5]. 시도가 있었는지는 연결 수·크기·시간 간격으로 판단합니다.

**notice 가 없으니 대입이 없었다고 쓰는 경우.** 탐지 스크립트를 불러오지 않았거나, 대입이 임계값(SSH 30분 30번, FTP 15분 20번)보다 느렸거나[6][13], Zeek 가 SSH 실패를 판정하지 못했으면 notice 가 생기지 않습니다. 느리게 오래 이어진 대입은 하루·일주일 단위로 연결 수를 세야 드러납니다.

**경고의 `action: allowed` 를 로그인 성공으로 읽는 경우.** EVE 경고의 `allowed` 는 센서가 그 패킷을 막지 않았다는 뜻이지 인증이 성공했다는 뜻이 아닙니다([경고 기록 (alert)](../../02-artifacts/suricata/eve-json/alert.md)).

**크기가 다른 연결을 성공으로 단정하는 경우.** 크기가 다른 연결로는 성공 가능성만 알 수 있습니다[2]. 중간에 끊긴 연결, 다른 인증 방식, 정상 사용자의 접속도 크기가 다르게 남을 수 있습니다.

**인터넷에 열린 RDP·SSH 에 대입 흔적이 있는 것을 사고로 보는 경우.** 대입 시도가 있었다는 것만으로는 침입이 있었다고 쓸 수 없습니다. Sigma 의 "Publicly Accessible RDP Service" 규칙은 사설·루프백·링크 로컬 대역이 아닌 주소가 RDP 에 붙으면 경고합니다[21]. 이렇게 노출된 서버를 찾으면 이미 무작위 대입이나 원격 공격으로 뚫리지 않았는지부터 확인합니다[21]. 시도가 있었다는 것과 성공했다는 것은 따로 확인합니다.

## 보고서 문장 예

아래 값은 모두 만든 예시입니다.

> 2026-09-01 02:10:04 부터 02:31:47(UTC) 사이에 203.0.113.45 가 10.0.20.15 의 3389/tcp 로 TCP 연결을 53번 열었다는 기록이 Zeek conn.log 에 있습니다. 이 중 52번은 보낸 바이트 1392, 받은 바이트 1238 로 크기가 같았고, 02:31:47 에 시작한 1번은 보낸 바이트 3380, 받은 바이트 4870 으로 달랐습니다. 이 연결은 로그인에 성공한 연결일 가능성이 있습니다. 네트워크 기록만으로는 사용한 계정과 로그인 성공 여부를 확정할 수 없어서, 10.0.20.15 의 Windows 보안 이벤트 로그와 대조해야 합니다.

> 2026-09-01 09:00 부터 09:20(UTC) 사이에 10.0.30.77 이 도메인 컨트롤러 10.0.0.10 에 보낸 Kerberos AS 요청 가운데 `error_msg` 가 KDC_ERR_PREAUTH_FAILED 인 기록이 계정 41개에 대해 1~2번씩 있습니다. 한 출발지가 여러 계정에 적은 횟수씩 인증을 시도한 모양입니다.

## 함께 볼 페이지

- [악성 코드가 C2 서버와 통신했나](c2-communication.md), [내부에서 다른 PC 로 옮겨 갔나](lateral-movement.md), [웹 서버의 취약점을 노렸나](web-exploitation.md)
- [SMB와 원격 관리 프로토콜](../../01-foundations/protocols/remote-protocols.md), [TCP 연결과 흐름](../../01-foundations/protocols/tcp-sessions.md)
- [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md), [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md), [네트워크 타임라인](../../03-techniques/analysis/timeline.md)
- [Windows 계정 탈취와 측면 이동](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/incident/credential-theft-lateral-movement/)
- 클라우드 가상 머신이 대상이면 [AWS VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/aws/vpc-flow-logs.html)

## 참고 문헌

1. Zeek 스크립트 참조, "base/protocols/conn/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
2. Zeek 문서, "rdp.log". https://github.com/zeek/zeek-docs/blob/master/logs/rdp.rst
3. Zeek 스크립트 참조, "base/protocols/rdp/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/rdp/main.zeek.rst
4. Zeek 스크립트 참조, "base/protocols/ssh/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssh/main.zeek.rst
5. Zeek 문서, "ssh.log". https://github.com/zeek/zeek-docs/blob/master/logs/ssh.rst
6. Zeek 스크립트 참조, "policy/protocols/ssh/detect-bruteforcing.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/policy/protocols/ssh/detect-bruteforcing.zeek.rst
7. Zeek 소스, `scripts/policy/protocols/ssh/detect-bruteforcing.zeek`. https://github.com/zeek/zeek/blob/master/scripts/policy/protocols/ssh/detect-bruteforcing.zeek
8. Zeek 소스, `scripts/site/local.zeek`. https://github.com/zeek/zeek/blob/master/scripts/site/local.zeek
9. Zeek 소스, `scripts/policy/misc/loaded-scripts.zeek`. https://github.com/zeek/zeek/blob/master/scripts/policy/misc/loaded-scripts.zeek
10. Zeek 스크립트 참조, "base/protocols/ftp/info.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ftp/info.zeek.rst
11. Zeek 스크립트 참조, "base/protocols/ftp/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ftp/main.zeek.rst
12. Zeek NEWS. https://github.com/zeek/zeek/blob/master/NEWS
13. Zeek 스크립트 참조, "policy/protocols/ftp/detect-bruteforcing.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/policy/protocols/ftp/detect-bruteforcing.zeek.rst
14. Zeek 소스, `scripts/policy/protocols/ftp/detect-bruteforcing.zeek`. https://github.com/zeek/zeek/blob/master/scripts/policy/protocols/ftp/detect-bruteforcing.zeek
15. Zeek 스크립트 참조, "base/protocols/krb/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/krb/main.zeek.rst
16. Zeek 스크립트 참조, "base/protocols/krb/consts.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/krb/consts.zeek.rst
17. Zeek 소스, `scripts/base/protocols/krb/main.zeek`. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/krb/main.zeek
18. Zeek 스크립트 참조, "base/protocols/ntlm/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ntlm/main.zeek.rst
19. Suricata 사용자 안내서, "Thresholding Keywords". https://github.com/OISF/suricata/blob/main/doc/userguide/rules/thresholding.rst
20. nfdump 매뉴얼 `nfdump(1)`. https://github.com/phaag/nfdump/blob/master/man/nfdump.1
21. SigmaHQ, "Publicly Accessible RDP Service" (`zeek_rdp_public_listener.yml`). https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_rdp_public_listener.yml
22. Milan Cermak, Tatiana Fritzová, Vít Rusňák, Denisa Sramkova, "Using relational graphs for exploratory analysis of network traffic data", Forensic Science International: Digital Investigation, 2023. doi:10.1016/j.fsidi.2023.301563
23. Zeek 문서, "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
24. Zeek 스크립트 참조, "base/protocols/http/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/http/main.zeek.rst
