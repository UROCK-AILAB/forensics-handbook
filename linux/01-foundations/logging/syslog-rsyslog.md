---
title: "syslog 형식과 rsyslog"
parent: "기반 · 로그 체계"
nav_order: 180
---

# syslog 형식과 rsyslog (syslog·rsyslog)

syslog 는 프로그램이 한 줄 메시지에 "어느 분야(facility)" 와 "얼마나 중요한가(severity)" 를 붙여 보내는 약속이고, rsyslog 는 그 메시지를 받아 설정 규칙대로 `/var/log` 아래 텍스트 파일에 나눠 쓰는 데몬입니다.

## 이 형식을 쓰는 아티팩트

Ubuntu 24.04 와 RHEL 9 계열은 둘 다 rsyslog 를 쓰지만, 메시지를 받는 길과 파일 이름과 시각 서식이 다릅니다. Ubuntu 는 로컬 소켓으로 메시지를 받는 imuxsock 모듈을 쓰고[7], RHEL 9 계열은 로컬 소켓 수신을 끄고 imjournal 모듈로 systemd 저널을 읽어 옵니다[8]. 아래 표는 두 배포판 패키지에 들어 있는 기본 규칙이고, RHEL 9 계열 값은 CentOS Stream 9 패키지 기준입니다.

| 파일 | Ubuntu 24.04 규칙 | RHEL 9 계열 규칙 | 담기는 것 |
|---|---|---|---|
| `/var/log/syslog` | `*.*;auth,authpriv.none -/var/log/syslog` | 없음 | 인증을 뺀 모든 메시지 |
| `/var/log/messages` | 없음 | `*.info;mail.none;authpriv.none;cron.none` | info 이상, 메일·authpriv·cron 제외 |
| `/var/log/auth.log` | `auth,authpriv.*` | 없음 | 인증 |
| `/var/log/secure` | 없음 | `authpriv.*` | authpriv(인증) |
| `/var/log/kern.log` | `kern.*` | 없음 | 커널 |
| `/var/log/mail.log`, `/var/log/mail.err` | `mail.*`, `mail.err` | 없음 | 메일 |
| `/var/log/maillog` | 없음 | `mail.*` (`sync="on"`) | 메일 |
| `/var/log/cron` | 없음(`/var/log/cron.log` 규칙은 주석) | `cron.*` | cron |
| `/var/log/spooler` | 없음 | `uucp,news.crit` | UUCP·뉴스 오류 |
| `/var/log/boot.log` | 없음 | `local7.*` | local7 로 보낸 부팅 메시지 |

Ubuntu 는 `/etc/rsyslog.conf` 에 모듈과 전역 설정만 두고, 규칙은 `/etc/rsyslog.d/50-default.conf` 에 둡니다[7]. 패키지는 원본을 `/usr/share/rsyslog/50-default.conf` 에 설치하고, 설치 스크립트가 ucf 로 `/etc/rsyslog.d/50-default.conf` 에 반영합니다[7]. RHEL 9 계열은 규칙을 `/etc/rsyslog.conf` 에 직접 쓰고 `/etc/rsyslog.d/*.conf` 를 함께 읽습니다[8]. 두 쪽 모두 다른 패키지나 관리자가 `/etc/rsyslog.d/` 에 규칙 파일을 더할 수 있으므로, 표는 출발점일 뿐이고 실제 시스템의 설정 파일을 먼저 읽어야 합니다.

Ubuntu 는 로그 파일을 `syslog` 사용자 권한으로 씁니다. `/etc/rsyslog.conf` 에 `$FileOwner syslog`, `$FileGroup adm`, `$FileCreateMode 0640`, `$PrivDropToUser syslog` 가 있고, tmpfiles 설정이 `/var/log` 를 0775 root:syslog 로, `auth.log`·`syslog`·`kern.log`·`mail.log`·`mail.err` 를 0640 syslog:adm 으로 맞춥니다[7].

각 파일이 조사에서 무엇을 알려 주는지는 [인증 로그](../../02-artifacts/logins/auth-log.md), [커널 로그](../../02-artifacts/system-info/kernel-log.md), [메일 서버 로그](../../02-artifacts/servers/mail-server-logs.md)에서 다룹니다.

## 구조

### 우선순위 값 (PRI)

메시지의 우선순위 값(PRI)은 facility 번호에 8을 곱하고 severity 번호를 더한 수입니다. 아래 3비트가 severity 이고, 3비트 오른쪽으로 민 나머지가 facility 입니다[9][13].

| 번호 | severity | 번호 | facility | 번호 | facility |
|---|---|---|---|---|---|
| 0 | emerg | 0 | kern | 8 | uucp |
| 1 | alert | 1 | user | 9 | cron |
| 2 | crit | 2 | mail | 10 | authpriv |
| 3 | err | 3 | daemon | 11 | ftp |
| 4 | warning | 4 | auth | 12~15 | 이름 없음(draft-23 은 NTP·log audit·log alert·clock) |
| 5 | notice | 5 | syslog | 16~23 | local0~local7 |
| 6 | info | 6 | lpr | | |
| 7 | debug | 7 | news | | |

facility 번호와 이름은 glibc 의 `syslog.h` 를 따르고[9], 12~15 의 뜻은 syslog protocol 초안 23 의 표입니다[13]. 설정 파일의 `security` 는 `auth` 의 옛 이름이고 폐기 예정이며, `mark` 는 rsyslog 내부용입니다[1].

PRI 는 원격 전송이나 `RSYSLOG_SyslogProtocol23Format` 처럼 서식에 `%PRI%` 가 들어갈 때만 줄에 찍힙니다[2]. 두 배포판의 기본 파일 서식에는 PRI 가 없어서, 줄만 보고는 facility 와 severity 를 알 수 없습니다. 그 줄이 어느 파일에 들어갔는지와 설정 규칙을 맞춰 보면 범위를 좁힐 수 있습니다.

### 선택자 문법

규칙 한 줄은 선택자와 동작으로 되어 있고, 선택자는 `facility.priority` 모양입니다[1]. priority 를 적으면 그 등급과 그보다 높은 등급을 모두 고릅니다[1]. `*` 는 전부를, `none` 은 그 facility 를 하나도 고르지 않음을 뜻합니다[1]. `,` 로 facility 를 여럿 묶고, `;` 로 선택자를 여럿 이으며, `;` 로 이은 선택자는 왼쪽부터 처리해 뒤의 것이 앞의 것을 덮습니다[1]. priority 앞의 `=` 는 그 등급 하나만, `!` 는 그 등급 이상을 빼라는 뜻입니다[1].

그래서 RHEL 의 `*.info;mail.none;authpriv.none;cron.none` 은 "모든 facility 의 info 이상을 고르되 메일·authpriv·cron 은 뺀다" 로 읽습니다. debug 등급은 `/var/log/messages` 에 들어가지 않고, authpriv 기록은 `/var/log/secure` 에만 있으며, auth facility 의 info 이상은 `/var/log/messages` 에 들어갑니다[8]. Ubuntu 의 `*.*` 는 debug 까지 고르고 auth·authpriv 만 뺍니다[7]. 경로 앞의 `-` 는 sysklogd 가 원래 BSD 문법에 더한 수정자이고[1], 파일 이름의 일부가 아닙니다.

### 줄 서식 (template)

rsyslog 는 서식(template)으로 파일에 쓸 줄의 모양을 정합니다. 미리 정의된 서식 가운데 이 페이지에서 다루는 것은 다음 셋입니다[2].

| 서식 이름 | 정의 | 시각 모양 |
|---|---|---|
| `RSYSLOG_TraditionalFileFormat` | `%TIMESTAMP% %HOSTNAME% %syslogtag%%msg:::sp-if-no-1st-sp%%msg:::drop-last-lf%` | 낮은 정밀도, 연도·시간대 없음 |
| `RSYSLOG_FileFormat` | `timereported`(RFC 3339) + 호스트 이름 + `syslogtag` + `msg` | 고정밀, 시간대 정보 포함 |
| `RSYSLOG_SyslogProtocol23Format` | `<%PRI%>1 %TIMESTAMP:::date-rfc3339% %HOSTNAME% %APP-NAME% %PROCID% %MSGID% %STRUCTURED-DATA% %msg%` | RFC 3339 |

파일 출력 모듈 omfile 의 기본 서식은 `RSYSLOG_FileFormat` 입니다[4]. RHEL 9 계열은 `module(load="builtin:omfile" Template="RSYSLOG_TraditionalFileFormat")` 로 옛 서식을 고르고[8], Ubuntu 24.04 는 서식을 따로 정하지 않아 `RSYSLOG_FileFormat` 을 씁니다[7][4]. 같은 메시지가 두 배포판에서 이렇게 찍힙니다(만든 예시).

```
Ubuntu 24.04:  2026-03-12T09:15:27.104233+09:00 web01 backupd[3120]: job nightly started
RHEL 9 계열:   Mar 12 09:15:27 web01 backupd[3120]: job nightly started
```

`syslogtag` 는 보통 프로그램 이름과 대괄호 안 PID, 콜론으로 이루어집니다. 도구들도 태그를 "이름, 선택적인 `[PID]`, 콜론" 으로 나눠 읽습니다[13][15].

### 메시지가 들어오는 길

systemd 를 쓰는 시스템에서는 journald 가 `/dev/log`, `/run/systemd/journal/dev-log`, `/run/systemd/journal/socket`, `/run/systemd/journal/stdout` 을 엽니다[11]. 그래서 프로그램이 syslog(3) 로 보낸 메시지는 저널에 먼저 들어가고, rsyslog 는 두 방법 가운데 하나로 받습니다. 하나는 journald 가 `ForwardToSyslog=` 설정에 따라 `/run/systemd/journal/syslog` 소켓으로 바로 넘겨 주는 방법이고, 다른 하나는 rsyslog 가 저널 파일을 직접 읽는 방법입니다[10]. upstream 기본값은 wall 전달만 켜져 있고[10], RHEL 9 의 systemd 소스에 든 `journald.conf` 에도 `#ForwardToSyslog=no` 가 주석으로 있습니다[12].

Ubuntu 의 `rsyslog.service` 는 `Requires=syslog.socket` 이고[7], imuxsock 은 systemd 시스템에서 `syslog.socket` 이 마련한 `/run/systemd/journal/syslog` 로 메시지를 받습니다[5]. 커널 메시지는 `module(load="imklog" permitnonkernelfacility="on")` 으로 따로 읽습니다[7]. 분석 대상의 `/etc/systemd/journald.conf` 와 `journald.conf.d/` 에서 `ForwardToSyslog=` 값을 확인하면 어느 길이 쓰였는지 알 수 있습니다.

RHEL 9 계열은 `imuxsock` 을 `SysSock.Use="off"` 로 불러 로컬 소켓을 듣지 않고, `imjournal` 을 `UsePid="system"`, `StateFile="imjournal.state"` 로 불러 저널을 읽습니다[8]. 작업 폴더가 `global(workDirectory="/var/lib/rsyslog")` 이고 상대 경로의 상태 파일은 작업 폴더 안에 만들므로[6][8], 읽은 위치는 `/var/lib/rsyslog/imjournal.state` 에 남습니다. 커널 메시지도 저널에서 오기 때문에 imklog 는 주석 처리되어 있습니다[8]. 저널 쪽 구조는 [systemd 저널](systemd-journal/index.md)에서 다룹니다.

## 읽는 법

1. 설정부터 읽습니다. `/etc/rsyslog.conf` 와 `/etc/rsyslog.d/*.conf` 에서 어떤 규칙이 어느 파일로 보내는지, 어떤 서식을 쓰는지, `imudp`·`imtcp`(514번 포트 수신)나 `omfwd`(원격 전송)가 켜져 있는지 봅니다. 두 배포판 모두 `imudp`·`imtcp` 는 기본으로 주석 처리되어 있습니다[7][8]. Ubuntu 는 `/etc/rsyslog.d/50-default.conf` 를 패키지 원본 `/usr/share/rsyslog/50-default.conf` 와 비교하면 규칙을 바꿨는지 알 수 있습니다[7].
2. 서식을 구분합니다. 줄이 네 자리 연도로 시작하면 RFC 3339 서식이고, 영어 달 이름으로 시작하면 옛 서식이며, `<` 로 시작하면 PRI 가 든 전송 서식입니다[2][13].
3. PRI 가 있으면 풉니다. 만든 예시 `<86>1 2026-03-12T00:15:27.104233+00:00 web01 backupd 3120 - - job nightly started` 에서 86 = 10 × 8 + 6 이므로 authpriv.info 입니다[9].
4. 호스트 이름과 태그를 나눕니다. 원격에서 받은 줄이 섞인 파일은 호스트 이름 필드로 출처를 구분합니다.
5. 시각을 UTC 로 바꿉니다. RFC 3339 서식은 줄에 적힌 오프셋을 빼면 되고, 옛 서식은 아래 "시각 해석" 대로 연도와 시간대를 붙입니다.

Ubuntu 는 한 세대 늦게 압축하므로 순환된 파일이 `syslog.1`, `syslog.2.gz` 처럼 섞여 있고[7], `zcat -f` 로 압축 여부와 상관없이 한꺼번에 읽을 수 있습니다.

## 포렌식에서 중요한 점

### 증명하는 것

한 줄은 "그 시각에(연도·시간대를 해석한 조건에서) 그 호스트 이름과 태그를 단 메시지가 rsyslog 로 들어와 이 파일에 쓰였다" 는 기록입니다. 어느 파일에 들어갔는지는 설정 규칙과 맞춰 facility·severity 의 범위를 알려 줍니다.

### 증명하지 못하는 것

태그와 facility 는 보낸 쪽이 정합니다. 대부분의 경우 누구나 어떤 facility 로든 메시지를 보낼 수 있고, glibc 의 `syslog()` 로는 kern facility 만 쓸 수 없습니다[1]. imuxsock 은 PID 를 소켓에서 얻는 `SysSock.UsePIDFromSystem` 이 기본으로 꺼져 있어서[5], Ubuntu 의 로컬 메시지에서 태그의 PID 는 보낸 프로그램이 적은 값입니다. RHEL 9 계열은 `UsePid="system"` 이라 journald 가 붙인 `_PID` 를 씁니다[6][8]. 어느 쪽이든 로컬 사용자가 다른 프로그램 이름을 단 줄을 남길 수 있으므로, 실제로 어떤 프로세스가 보냈는지는 저널의 신뢰 필드로 확인합니다([systemd 저널](systemd-journal/index.md)).

기록이 빠짐없이 남았다는 뜻도 아닙니다. journald 는 서비스마다 기본으로 30초에 10000건을 넘는 메시지를 버리고 버린 개수만 남기며, 이 한도에 디스크 여유 공간에 따른 배수를 곱합니다[10]. imjournal 도 기본으로 10분에 20000건을 넘으면 버리고 버린 개수를 남깁니다[6]. 저널은 바쁠 때 syslog 소켓으로 넘기지 않고 메시지를 버리는 경향이 있습니다[5]. 규칙에서 뺀 등급·facility(RHEL 의 debug 등)는 처음부터 파일에 없습니다[8].

### 시각 해석

rsyslog 에는 시각 속성이 둘 있습니다. `timereported` 는 메시지 머리에 담긴 시각으로 보낸 쪽 시각에 가깝고 대개 초 단위이며, `timegenerated` 는 로컬 시스템이 받은 시각이고 늘 고정밀입니다[3]. `%TIMESTAMP%` 는 `timereported` 의 다른 이름이고, 두 값은 시스템 사이의 시계·시간대 설정 차이로 크게 다를 수 있습니다[3]. 로컬 소켓으로 들어온 메시지는 imuxsock 이 기본으로 메시지 안의 시각을 무시하고(`SysSock.IgnoreTimestamp` on) 시스템이 준 시각을 쓰므로(`SysSock.UseSysTimeStamp` on)[5], Ubuntu 의 로컬 줄 시각은 받은 시각입니다. 원격에서 받은 줄은 보낸 기계의 시계를 따릅니다[3].

RFC 3339 서식은 연도·마이크로초·UTC 오프셋이 있어서 그대로 UTC 로 바꿀 수 있습니다[2][13]. 옛 서식에는 연도와 시간대가 없고 초까지만 있어서, 도구는 기록한 시스템의 현지 시각으로 보고 연도를 추정합니다. plaso 는 파일의 변경·생성·수정 시각 가운데 가장 이른 날짜의 연도에서 시작하고, 달이 두 달 이상 거꾸로 가면 해를 넘긴 것으로 봅니다[14]. 한 달 되돌아가는 것은 `RepeatedMsgReduction` 때문에 생길 수 있는 순서 뒤섞임으로 보고 넘깁니다[14]. dissect 는 파일 수정 시각(mtime)의 연도를 대상 시스템 시간대로 바꿔 시작하고, 파일 끝에서 거꾸로 읽으며 달이 커지면 연도를 하나 줄입니다[16]. 그래서 dissect 출력은 시간순이 아닐 수 있습니다[15]. 파일을 복사하거나 압축하면서 mtime 이 바뀌었다면 두 도구가 붙인 연도가 틀릴 가능성이 있습니다.

시간대는 [호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md)에서 확인하고, 시각 값을 다루는 일반 원리는 [Linux 의 시각 값](../value-decoding/time-values.md)에 있습니다. 시계를 바꾼 흔적을 찾는 방법은 [시각을 조작했나](../../04-scenarios/insider/time-manipulation.md)에서 다룹니다.

### 지운 데이터·손상

syslog 파일은 색인이나 일련번호가 없는 텍스트라서, 줄을 지우거나 고쳐도 파일 안에 자국이 남지 않습니다. 같은 메시지가 저널에도 들어가므로(Ubuntu 는 journald 가 `/dev/log` 를 먼저 받고, RHEL 은 rsyslog 가 저널을 읽어 옵니다) 저널과 줄 단위로 맞춰 보면 빠진 줄을 찾을 수 있습니다[5][8][11]. 흔적을 지웠는지 판단하는 흐름은 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md)에서 다룹니다.

omfile 은 파일 동기화(`sync`)가 기본으로 꺼져 있습니다[4]. RHEL 9 계열은 `/var/log/maillog` 에만 `sync="on"` 을 켭니다[8]. 비정상 종료 직전의 줄은 다른 파일에서 빠져 있을 가능성이 있습니다.

일부 systemd 판에서는 저널이 손상되면 같은 데이터를 끝없이 돌려주어, imjournal 을 거친 메시지가 대량으로 중복될 수 있습니다[6]. RHEL 계열 `/var/log/messages` 에 오래된 줄이 되풀이되어 있으면 이 경우일 가능성이 있습니다.

## 함정

- 순환 주기와 보관 개수가 배포판마다 다릅니다. Ubuntu 는 `syslog`·`mail.log`·`kern.log`·`auth.log`·`user.log`·`cron.log` 를 매주 순환하고 4세대를 남기며, 한 세대 늦게 압축합니다(`delaycompress`)[7]. RHEL 9 계열의 `/etc/logrotate.d/rsyslog` 는 `cron`·`maillog`·`messages`·`secure`·`spooler` 를 대상으로 하되 주기와 개수를 적지 않아 전역 설정을 따릅니다[8]([로그 순환](logrotate.md)).
- dissect 는 첫 세 줄 가운데 한 줄이라도 `\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}` 에 맞아야 ISO 서식으로 봅니다[15]. 오프셋이 `-05:00` 처럼 음수이거나 소수 자리가 6자리가 아닌 파일은 옛 서식 경로로 가서, 달 이름이 없는 줄을 건너뜁니다[15][16].
- Velociraptor `Linux.Syslog.SSHLogin` 의 기본 Grok 은 옛 서식 시각(`SYSLOGTIMESTAMP`)만 받고 `program` 이 `sshd` 인 줄만 고릅니다[17]. OpenSSH 9.8 부터는 인증 메시지를 `sshd-session` 이 씁니다[13]. Ubuntu 24.04 의 RFC 3339 줄이나 `sshd-session` 줄은 이 기본값으로 잡히지 않을 가능성이 있습니다.
- ForensicArtifacts 의 `linux.yaml` 정의에는 cron 로그가 `/var/log/cron.log*` 만 있고, RHEL 의 `/var/log/cron`·`/var/log/maillog`·`/var/log/spooler`·`/var/log/boot.log` 경로는 없습니다[18]. 이 정의로만 수집하면 빠지므로 `/var/log` 를 통째로 받습니다[19].
- `$RepeatedMsgReduction on`(Ubuntu)은 같은 메시지가 이어지면 줄여서 적는 설정입니다[7]. 줄 수로 사건 횟수를 세면 적게 셀 수 있습니다.
- 휘발성 저장만 쓰는 시스템에서도 syslog 파일은 `/var/log` 에 남으므로, 저널이 비어 있을 때 syslog 파일이 유일한 기록일 수 있습니다.

## 도구

| 도구 | 읽는 파일 | 참고 |
|---|---|---|
| plaso `syslog`·`syslog_traditional` 파서 | syslog 서식 텍스트 | RFC 3339·protocol 23·옛 서식을 읽고, 옛 서식은 현지 시각으로 표시하고 연도를 추정[13][14] |
| dissect.target `messages`(별칭 `syslog`) | `/var/log/`, `/var/log/installer/` 의 `syslog*`·`messages*`·`cloud-init.log*` | 압축본도 열고, ISO 서식이 아니면 연도 추정[15][16] |
| dissect.target `authlog`(별칭 `securelog`) | `/var/log/auth.log*`, `/var/log/secure*` | CentOS·Debian·Ubuntu 24.04 서식을 가림[15] |
| Velociraptor `Linux.Syslog.SSHLogin` | `/var/log/{auth.log,secure}*` | Grok 으로 sshd 로그인 줄만 뽑음[17] |
| ForensicArtifacts | `/var/log/syslog*`, `/var/log/messages*`, `/var/log/auth*`, `/var/log/secure*`, `/var/log/kern*`, `/var/log/daemon*`, `/var/log/cron.log*`, `/etc/rsyslog.conf`, `/etc/rsyslog.d/*` | 수집 경로 정의[18] |
| UAC | `/var/log` 전체(파일당 1GB 까지), `/run/log` | 라이브 수집[19] |

여러 로그를 엮어 읽는 방법은 [로그 분석](../../03-techniques/analysis/log-analysis.md)과 [타임라인 만들기](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 참고 문헌

1. rsyslog, sysklogd format(`sysklogd_format.rst`). https://github.com/rsyslog/rsyslog-doc/blob/main/source/configuration/sysklogd_format.rst
2. rsyslog, Templates(`templates.rst`). https://github.com/rsyslog/rsyslog-doc/blob/main/source/configuration/templates.rst
3. rsyslog, Properties(`properties.rst`). https://github.com/rsyslog/rsyslog-doc/blob/main/source/configuration/properties.rst
4. rsyslog, omfile(`omfile.rst`). https://github.com/rsyslog/rsyslog-doc/blob/main/source/configuration/modules/omfile.rst
5. rsyslog, imuxsock(`imuxsock.rst`). https://github.com/rsyslog/rsyslog-doc/blob/main/source/configuration/modules/imuxsock.rst
6. rsyslog, imjournal(`imjournal.rst`). https://github.com/rsyslog/rsyslog-doc/blob/main/source/configuration/modules/imjournal.rst
7. Ubuntu 24.04(noble) rsyslog 패키지 8.2312.0-3ubuntu9, `debian/rsyslog.conf`·`50-default.conf`·`00rsyslog.conf`·`rsyslog.install`·`rsyslog.postinst`·`rsyslog.service`·`rsyslog.logrotate`. https://git.launchpad.net/ubuntu/+source/rsyslog/tree/debian?h=ubuntu/noble
8. CentOS Stream 9 rsyslog 패키지, `rsyslog.conf`·`rsyslog.log`. https://gitlab.com/redhat/centos-stream/rpms/rsyslog/-/tree/c9s
9. glibc, `misc/sys/syslog.h`. https://github.com/bminor/glibc/blob/master/misc/sys/syslog.h
10. systemd, journald.conf(5). https://github.com/systemd/systemd/blob/main/man/journald.conf.xml
11. systemd, systemd-journald.service(8). https://github.com/systemd/systemd/blob/main/man/systemd-journald.service.xml
12. RHEL 9 systemd source-git(252), `src/journal/journald.conf`. https://github.com/redhat-plumbers/systemd-rhel9
13. plaso, `parsers/text_plugins/syslog.py`. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/syslog.py
14. plaso, `lib/dateless_helper.py`. https://github.com/log2timeline/plaso/blob/main/plaso/lib/dateless_helper.py
15. dissect.target, `plugins/os/unix/log/messages.py`·`auth.py`·`helpers.py`. https://github.com/fox-it/dissect.target/tree/main/dissect/target/plugins/os/unix/log
16. dissect.target, `helpers/utils.py`(`year_rollover_helper`). https://github.com/fox-it/dissect.target/blob/main/dissect/target/helpers/utils.py
17. Velociraptor, `Linux/Syslog/SSHLogin.yaml`. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Syslog/SSHLogin.yaml
18. ForensicArtifacts, `artifacts/data/linux.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
19. UAC, `artifacts/files/logs/var_log.yaml`·`run_log.yaml`. https://github.com/tclahr/uac/tree/main/artifacts
