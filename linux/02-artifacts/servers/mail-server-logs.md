---
title: "메일 서버 로그"
parent: "아티팩트 · 서버 애플리케이션"
nav_order: 760
---

# 메일 서버 로그 (Postfix)

Postfix 는 메일을 받고 넘길 때마다 큐 ID 를 앞에 붙인 줄을 syslog 로 남기고, 이 줄들을 큐 ID 로 묶으면 메시지 하나가 언제 누구에게서 들어와 어디로 나갔는지 따라갈 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

Postfix 는 한 프로그램이 아니라 여러 데몬이 메시지를 차례로 넘기는 구조이고, 데몬마다 자기가 한 일을 한 줄씩 남깁니다. SMTP 연결을 받는 `smtpd` 는 연결과 끊김, 받은 메시지의 보낸 곳을 적고, `cleanup` 은 메시지 머리의 Message-ID 를 적습니다[3][4]. 큐 관리자 `qmgr` 는 봉투 발신자와 크기, 수신자 수를 적고 처리가 끝나면 큐에서 지웠다고 적습니다[5]. 실제로 넘기는 `smtp`·`local` 같은 전달 에이전트는 수신자마다 전달 결과와 걸린 시간을 적습니다[6].

로그는 기본으로 syslog 의 `mail` 시설(facility)로 나가고, 프로그램 이름 앞에는 `syslog_name` 이 붙어 `postfix/smtpd` 처럼 찍힙니다[1]. 두 값을 바꾸면 바꾼 값이 적용되는 것은 프로세스가 초기화를 마친 뒤부터이고, 명령줄 인자나 `main.cf` 를 읽다 난 오류는 기본 시설·기본 이름으로 남습니다[1].

Postfix 3.4 부터는 syslog 대신 `postlogd` 서비스가 파일에 직접 쓰게 할 수도 있습니다[2]. 이 방식은 `maillog_file` 에 파일 이름을 넣고 `master.cf` 에 `postlog` 서비스 줄을 두어야 켜지고, `maillog_file` 이 비어 있으면(기본값) syslog 로 보냅니다[1][2].

## 위치와 버전별 차이

기준 배포판의 기본 설정은 아래와 같습니다.

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| Postfix 판 | 3.8[8] | 3.5[9] |
| 로그 파일 | `/var/log/mail.log`(`mail.*`), `/var/log/mail.err`(`mail.err`)[10] | `/var/log/maillog`(`mail.*`), `/var/log/messages` 에서는 `mail.none` 으로 뺌[11] |
| rsyslog 가 줄을 받는 길 | 로컬 소켓(imuxsock)과, Postfix 패키지가 `/etc/rsyslog.d/postfix.conf` 로 더하는 `/var/spool/postfix/dev/log` 소켓[10][8] | 로컬 소켓 수신을 끄고 imjournal 로 저널에서 읽음[11] |
| 줄 머리 시각 | RFC 3339(연도·마이크로초·UTC 오프셋) | 옛 서식 `Mmm dd HH:MM:SS`(연도·시간대 없음)[11] |
| 순환 | 매주, 4세대, 한 세대 늦게 압축. `mail.err` 는 순환 목록에 없음[10] | rsyslog 패키지의 순환 설정에 주기가 없어 전역 설정(매주, 4세대, 날짜 접미사, 압축 없음)을 따름 → `maillog-YYYYMMDD`[11][12] |
| 설정 파일 | `/etc/postfix/main.cf`, `master.cf`[8] | `/etc/postfix/main.cf`, `master.cf`[9] |
| 큐 폴더 | `/var/spool/postfix`(패키지가 이 안에 `dev/log` 소켓을 둠)[8] | `/var/spool/postfix`[9] |

두 배포판의 rsyslog 규칙과 줄 서식 차이는 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md), 순환 규칙은 [로그 순환](../../01-foundations/logging/logrotate.md)에서 자세히 다룹니다.

관리자가 `maillog_file` 을 켰다면 로그 파일은 위 표와 다른 곳에 있습니다. 파일 이름은 `maillog_file_prefixes`(기본 `/var, /dev/stdout`)에 든 접두어로 시작해야 하므로 보통 `/var` 아래에 있습니다[1][2]. 이 파일은 `postfix logrotate` 명령으로 순환하는데, 이름 뒤에 `maillog_file_rotate_suffix`(기본 `%Y%m%d-%H%M%S`)로 만든 날짜·시각을 붙이고 `maillog_file_compressor`(기본 `gzip`)로 압축합니다[1][2]. 새 파일의 권한을 정하는 `maillog_file_permissions`(기본 0600)는 3.9 부터 있는 설정입니다[1].

수집 도구 가운데 UAC 는 `/var/log`(파일 하나에 1GB 까지)와 `/var/spool` 을 폴더째 모으므로 로그 파일과 큐 폴더가 함께 들어갑니다[13].

## 구조

### 메시지 하나의 흐름

메시지 하나가 들어와 밖으로 나가면 대개 아래 순서로 줄이 남습니다. 아래는 RHEL 옛 서식으로 만든 예시이고, 호스트·주소·ID 는 모두 지어낸 값입니다.

```
Mar 12 14:05:09 mx1 postfix/smtpd[2101]: connect from mail.example.org[203.0.113.25]
Mar 12 14:05:10 mx1 postfix/smtpd[2101]: 4A1B2C3D4E: client=mail.example.org[203.0.113.25], sasl_method=PLAIN, sasl_username=alice
Mar 12 14:05:10 mx1 postfix/cleanup[2104]: 4A1B2C3D4E: message-id=<20260312050510.4A1B2C3D4E@mx1.example.com>
Mar 12 14:05:10 mx1 postfix/qmgr[900]: 4A1B2C3D4E: from=<alice@example.com>, size=2048, nrcpt=1 (queue active)
Mar 12 14:05:11 mx1 postfix/smtp[2106]: 4A1B2C3D4E: to=<bob@example.net>, relay=…, delay=1.2, delays=0.1/0.01/0.5/0.6, dsn=2.0.0, status=sent (…)
Mar 12 14:05:11 mx1 postfix/qmgr[900]: 4A1B2C3D4E: removed
Mar 12 14:05:12 mx1 postfix/smtpd[2101]: disconnect from mail.example.org[203.0.113.25] …
```

Ubuntu 24.04 에서는 줄 머리만 `2026-03-12T14:05:09.104233+09:00 mx1 postfix/smtpd[2101]: …` 처럼 바뀌고 뒷부분은 같습니다(만든 예시). `relay=` 값과 끊김 줄 뒤의 명령 통계는 모양을 실제 로그로 확인합니다.

### 줄별 필드

| 프로그램 | 줄 모양 | 뜻 |
|---|---|---|
| `smtpd` | `connect from host[address]` | SMTP 클라이언트가 연결함. `smtpd_client_port_logging = yes` 이면 `host[address]:port`(기본 no)[1][3] |
| `smtpd` | `QUEUEID: client=host[address]` 와 선택 필드 `sasl_method=`, `sasl_username=`, `sasl_sender=`, `orig_queue_id=`, `orig_client=` | 메시지를 받아 큐 ID 를 붙임. SASL 로 인증했으면 인증 방법과 사용자 이름이 붙음. 큐 ID 가 없으면 `NOQUEUE`[3] |
| `smtpd` | `host[address]: SASL 방법 authentication failed: 이유, sasl_username=이름` | SASL 인증 실패(경고). 사용자 이름을 모르면 `(unavailable)`. 도중에 멈추면 `authentication aborted`[3] |
| `cleanup` | `QUEUEID: message-id=값`, `QUEUEID: resent-message-id=값` | 메시지 머리의 Message-ID. 머리에 없고 Postfix 도 붙이지 않았으면 `message-id=<>`[4] |
| `qmgr` | `QUEUEID: from=<봉투 발신자>, size=바이트, nrcpt=수신자 수 (queue 큐 이름)` | 큐 관리자가 메시지를 열어 전달 대상으로 삼음[5] |
| 전달 에이전트 | `QUEUEID: to=<수신자>, orig_to=<원래 수신자>, relay=넘긴 곳, conn_use=, delay=, delays=a/b/c/d, dsn=, status=상태 (이유)` | 수신자 하나의 전달 결과. `orig_to=`·`conn_use=` 는 있을 때만[6] |
| `qmgr` | `QUEUEID: removed` | 큐에서 메시지를 지움(처리 끝). 관리자가 `postsuper` 로 지울 때도 같은 모양[5] |
| `smtpd` | `disconnect from host[address]` 와 명령 통계 | 연결이 끝남[3] |

`status=` 에는 `sent`·`deferred`·`bounced` 같은 값이 들어가고, `dsn=` 은 전달 상태 코드입니다[6]. `delay=` 는 메시지가 도착한 때부터 전달이 끝난 때까지 걸린 전체 시간(초)입니다[6]. `delays=a/b/c/d` 는 이 시간을 넷으로 나눈 값이고, a 는 도착부터 활성 큐에 마지막으로 들어갈 때까지, b 는 그때부터 연결 준비를 시작할 때까지, c 는 연결 준비(SMTP 새 연결이라면 DNS 조회·TCP·EHLO·STARTTLS), d 는 메시지 전송에 걸린 시간입니다[1]. 100초 이상은 정수 초로, 그보다 작으면 유효 숫자 두 자리로 적고, 소수점 아래 자릿수 상한은 `delay_logging_resolution_limit`(기본 2)입니다[1]. 개발 판 소스에는 `delays=` 뒤에 `tls=` 필드가 더 있지만, Ubuntu 24.04(3.8)와 RHEL 9(3.5)의 판에는 없습니다[6].

주소는 3.5 부터 `info_log_address_format = external`(기본)이라, 로컬 부분에 공백 같은 특수 문자가 있으면 `from=<"name with spaces"@example.com>` 처럼 따옴표로 감싸 적습니다[1]. 그 전 판은 따옴표 없이 적었습니다[1].

### 큐 ID

큐 ID 는 큐 파일 이름이고, 메시지 하나에 딸린 줄을 묶는 열쇠입니다. 기본값인 `enable_long_queue_ids = no` 에서는 `C3CD21F3E90` 처럼 0~9·A~F 로 된 짧은 ID 를 쓰는데, 앞 5자는 마이크로초 단위 시각이고 나머지는 큐 파일의 아이노드 번호입니다[1]. `yes` 로 바꾸면 `3Pt2mN2VXxznjll` 처럼 모음을 뺀 52자 알파벳으로 된 긴 ID 를 쓰고, 앞 6자 이상은 초 단위 시각, 이어지는 4자는 마이크로초, 그 뒤 `z` 다음이 아이노드 번호입니다[1]. 긴 ID 는 겹치지 않는 이름이고[1], Postfix 는 큐 ID 가 1초 안에서만 겹치지 않도록 보장합니다[4].

Postfix 가 Message-ID 를 직접 붙일 때는 모양이 큐 ID 설정을 따릅니다. 짧은 ID 에서는 `YYYYMMDDHHMMSS.큐ID@myhostname`, 긴 ID 에서는 `큐ID@myhostname` 입니다[1]. 앞의 날짜·시각은 큐 파일을 만든 시각을 UTC 로 바꾼 값입니다[4].

## 증거로서 의미

**증명하는 것**

- 이 시각에 이 주소의 클라이언트가 SMTP 로 연결했고, 인증했다면 어떤 SASL 사용자 이름을 썼는지.
- 그 연결로 들어온 메시지의 봉투 발신자(`from=`), 수신자(`to=`), 크기, Message-ID.
- 이 메시지를 어디로 넘기려 했고 결과가 `sent`·`deferred`·`bounced` 가운데 무엇이었는지. `status=sent` 는 다음 서버가 받았다고 답했다는 데까지입니다.
- SASL 인증에 실패한 시도와 그때 쓴 사용자 이름.

**증명하지 못하는 것**

- 제목·본문·첨부. 로그에는 없고, 큐 폴더(`/var/spool/postfix`)에 아직 큐 파일이 남아 있을 때만 볼 수 있습니다.
- 편지 머리의 `From:` 에 적힌 보낸 사람. `from=` 은 SMTP 봉투의 발신자라서 머리의 `From:` 과 다를 수 있습니다.
- 받는 사람이 메일을 읽었는지.
- Message-ID 를 누가 만들었는지. `cleanup` 은 메시지 머리에 있는 값을 그대로 적고[4], 머리에 없고 클라이언트가 `local_header_rewrite_clients` 에 들거나 `always_add_missing_headers = yes` 일 때만 새로 만들어 붙이므로[1][4], 보낸 쪽 프로그램이 넣은 값은 지어낸 값일 수 있습니다.

보고서에는 "이 시각에 이 주소에서 `alice` 로 인증한 SMTP 세션이 `bob@example.net` 앞으로 메시지를 넘겼고 다음 서버가 받았다고 답한 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

줄 머리 시각은 로그를 받은 rsyslog 가 붙이고, 서식은 배포판마다 다릅니다. Ubuntu 24.04 의 `mail.log` 는 RFC 3339 서식이라 UTC 오프셋이 줄에 있고, RHEL 9 의 `maillog` 는 연도와 시간대가 없는 현지 시각입니다[11]. `postlogd` 가 쓰는 `maillog_file` 도 `%b %d %H:%M:%S` 로 현지 시각을 적고 연도·시간대가 없습니다[7]. 연도와 시간대를 붙이는 방법은 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)의 시각 해석을, 호스트의 시간대 설정은 [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md)을 봅니다.

RHEL 9 는 rsyslog 가 저널에서 줄을 읽어 오므로 같은 줄이 저널에도 있고, 저널 쪽은 UTC 마이크로초 시각이 붙습니다([systemd 저널](../../01-foundations/logging/systemd-journal/index.md)). Ubuntu 는 Postfix 패키지가 rsyslog 에 `/var/spool/postfix/dev/log` 소켓을 따로 열어 chroot 안의 Postfix 데몬 로그를 직접 받으므로[8], 이 길로 들어온 줄은 저널에 없을 가능성이 있습니다. Ubuntu 에서는 `mail.log` 를 먼저 봅니다.

시각을 보정할 단서가 로그 안에도 있습니다. Postfix 가 붙인 Message-ID 의 `YYYYMMDDHHMMSS` 는 UTC 이므로[4], 같은 큐 ID 의 `cleanup` 줄 시각(현지 시각)과 비교하면 서버가 쓰던 시간대를 추정할 수 있습니다. 위 예시에서 줄 시각 14:05:10 과 Message-ID 의 05:05:10 은 9시간 차이입니다. 또 `delay=` 는 도착부터 전달 완료까지의 시간이라[6], 전달 줄 시각에서 `delay` 를 빼면 메시지가 도착한 때와 거의 맞습니다. 메시지가 오래 `deferred` 로 머물렀다면 같은 큐 ID 의 전달 줄이 여러 번 나오고 `delay` 가 점점 커집니다.

## 함정과 한계

- 짧은 큐 ID 는 오래 쓰면 같은 ID 가 다른 메시지에 다시 붙을 수 있습니다. 큐 ID 로 묶을 때는 시각 범위를 함께 좁힙니다[1][4].
- `syslog_name` 을 바꾼 서버(여러 인스턴스를 돌리는 서버 등)는 `postfix/` 대신 다른 접두어가 붙으므로, `postfix/` 로만 검색하면 줄을 놓칩니다[1].
- `maillog_file` 을 켠 서버라도 일부 줄은 syslog 에 남습니다. 데몬이 아닌 프로그램은 설정을 읽기 전의 오류를 syslog 로 보내고, Postfix 가 꺼져 있을 때 `postfix`·`postsuper`·`postmulti`·`postlog` 는 `maillog_file` 에 직접 씁니다[2]. 두 곳을 다 봅니다.
- `postfix logrotate` 는 옛 파일을 지우지 않습니다[2]. 반대로 syslog 쪽 `mail.log`·`maillog` 는 기본 4세대만 남기므로 한 달쯤 지난 기록은 순환으로 사라졌을 가능성이 있습니다[10][11][12].
- Ubuntu 의 `mail.err` 는 rsyslog 순환 목록에 없습니다[10]. 실제 시스템에 다른 순환 설정이 있는지 봅니다.
- 3.5 이전 판의 로그는 주소를 따옴표 없이 적으므로, 공백이 든 주소는 판에 따라 모양이 다릅니다[1].
- 여러 서버를 거친 메시지를 Message-ID 로 이을 수는 있지만, Message-ID 는 보통 메시지를 처음 제출받은 쪽이 한 번 정하고 뒤의 서버들은 그대로 넘기므로 중간 서버가 언제 넘겼는지는 드러나지 않는다는 지적이 있습니다[14]. 서버마다 큐 ID 와 시각을 따로 확인해 이어 붙입니다.
- syslog 파일은 텍스트라서 줄을 지워도 자국이 남지 않습니다. RHEL 은 저널과, 두 배포판 모두 받는 쪽·보내는 쪽 서버 로그와 맞춰 봅니다([흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md)).

## 직접 분석해 보기

텍스트 로그라서 헥스로 볼 구조는 없고, 줄을 큐 ID 로 묶는 것이 첫 단계입니다.

1. 압축된 옛 파일까지 모아 시간순으로 이어 붙입니다. Ubuntu 는 `mail.log`, `mail.log.1`, `mail.log.2.gz` …, RHEL 은 `maillog`, `maillog-YYYYMMDD` 입니다.
2. 관심 있는 주소·사용자 이름으로 `client=` 줄이나 `from=`·`to=` 줄을 찾아 큐 ID 를 얻습니다.

   ```
   zgrep -h 'sasl_username=alice' /var/log/mail.log*
   zgrep -h ': 4A1B2C3D4E: ' /var/log/mail.log*
   ```

3. 큐 ID 로 모은 줄에서 `smtpd` 의 프로세스 번호(예시의 `2101`)를 얻고, 같은 번호의 `connect from`·`disconnect from` 줄로 연결 전체를 봅니다. 한 연결에서 메시지를 여러 통 보냈다면 큐 ID 가 여럿 나옵니다.
4. 인증 실패는 `authentication failed` 로 찾아 주소별·사용자 이름별로 셉니다.

공개 도구로는 로그 요약 보고서를 만드는 pflogsumm 이 있고, RHEL 9 에서는 `postfix-perl-scripts` 패키지에 들어 있습니다[9]. plaso 에는 Postfix 전용 파서가 없어 일반 syslog 파서로 줄을 읽으므로[15], 큐 ID 로 묶는 일은 따로 해야 합니다. 로그 전반을 다루는 절차는 [로그 분석](../../03-techniques/analysis/log-analysis.md)에 있습니다.

## 교차 검증

- [인증 로그 (auth.log·secure)](../logins/auth-log.md): SASL 인증을 다른 서비스가 맡는 서버라면 그쪽 인증 기록과 사용자 이름·시각을 맞춥니다.
- [방화벽](../network/firewall.md): 같은 주소의 25·587번 포트 연결 기록.
- [웹 서버 로그 (Apache·Nginx)](web-server-logs.md): 웹 메일이나 웹 폼에서 보낸 메일은 로컬에서 제출되므로, 웹 요청 시각과 로컬 제출 줄의 시각을 맞춰 봅니다.
- 큐 폴더 `/var/spool/postfix`: 아직 나가지 못한 메시지의 큐 파일이 남아 있을 수 있습니다. 로컬 편지함 위치는 `mail_spool_directory` 로 정해지고 기본값은 시스템마다 다르며, 이름이 `/` 로 끝나면 maildir 형식입니다[1].
- [타임라인 만들기](../../03-techniques/analysis/timeline.md): 전달 줄과 로그인·웹 기록을 한 시간축에 놓습니다.

## 실습

Postfix 를 설치한 시험용 가상 머신이나 메일 서버가 들어 있는 공개 디스크 이미지로 풀어 봅니다.

1. 메일 로그 파일이 어디에 있고 줄 머리 서식이 무엇인가? `maillog_file` 을 켰는가?
2. 가장 많이 인증에 실패한 주소와 그 주소가 시도한 사용자 이름은 무엇인가?
3. 특정 SASL 사용자가 보낸 메시지의 큐 ID 를 모두 찾고, 각 메시지의 수신자와 전달 결과를 표로 만든다.
4. Postfix 가 붙인 Message-ID 가 있다면, 그 UTC 시각과 `cleanup` 줄 시각을 비교해 서버 시간대를 구한다.
5. `deferred` 로 오래 머문 메시지가 있는가? `delay` 로 도착 시각을 거꾸로 구해 `client=` 줄 시각과 맞는지 본다.

## 참고 문헌

1. Postfix 소스(GitHub 사본), `postfix/proto/postconf.proto`. https://github.com/vdukhovni/postfix/blob/master/postfix/proto/postconf.proto
2. Postfix 소스(GitHub 사본), `postfix/proto/MAILLOG_README.html`. https://github.com/vdukhovni/postfix/blob/master/postfix/proto/MAILLOG_README.html
3. Postfix 소스(GitHub 사본), `src/smtpd/smtpd.c`·`smtpd_sasl_glue.c`(v3.5.25·v3.8.6 태그도 같은 형식). https://github.com/vdukhovni/postfix/tree/master/postfix/src/smtpd
4. Postfix 소스(GitHub 사본), `src/cleanup/cleanup_message.c`. https://github.com/vdukhovni/postfix/blob/master/postfix/src/cleanup/cleanup_message.c
5. Postfix 소스(GitHub 사본), `src/qmgr/qmgr_active.c`·`qmgr_message.c`, `src/global/opened.c`. https://github.com/vdukhovni/postfix/tree/master/postfix/src
6. Postfix 소스(GitHub 사본), `src/global/log_adhoc.c`(v3.5.25·v3.8.6 태그에는 `tls=` 없음). https://github.com/vdukhovni/postfix/blob/master/postfix/src/global/log_adhoc.c
7. Postfix 소스(GitHub 사본), `src/util/msg_logger.c`. https://github.com/vdukhovni/postfix/blob/master/postfix/src/util/msg_logger.c
8. Ubuntu 24.04(noble) postfix 패키지, `debian/rsyslog.conf`·`main.cf.in`·`rules`. https://git.launchpad.net/ubuntu/+source/postfix/tree/debian?h=ubuntu/noble
9. CentOS Stream 9 postfix 패키지, `postfix.spec`. https://gitlab.com/redhat/centos-stream/rpms/postfix/-/blob/c9s/postfix.spec
10. rsyslog 패키징 저장소(rsyslog-pkg-ubuntu), noble `rsyslog.conf`·`50-default.conf`·`rsyslog.logrotate`. https://github.com/rsyslog/rsyslog-pkg-ubuntu/tree/master/rsyslog/noble/v8-stable/debian
11. CentOS Stream 9 rsyslog 패키지, `rsyslog.conf`·`rsyslog.log`. https://gitlab.com/redhat/centos-stream/rpms/rsyslog/-/tree/c9s
12. logrotate, `examples/logrotate.conf`. https://github.com/logrotate/logrotate/blob/main/examples/logrotate.conf ; CentOS Stream 9 logrotate 패키지, `logrotate.spec`. https://gitlab.com/redhat/centos-stream/rpms/logrotate/-/blob/c9s/logrotate.spec
13. UAC, `artifacts/files/logs/var_log.yaml`·`artifacts/files/system/var_spool.yaml`. https://github.com/tclahr/uac/tree/main/artifacts/files
14. Johannes Olegård, Stefan Axelsson, Yuhong Li, "When is logging sufficient? — Tracking event causality for improved forensic analysis and correlation", Forensic Science International: Digital Investigation 52 (2025) 301877. https://doi.org/10.1016/j.fsidi.2025.301877
15. plaso, `plaso/parsers/text_plugins/`(`syslog.py`). https://github.com/log2timeline/plaso/tree/main/plaso/parsers/text_plugins
