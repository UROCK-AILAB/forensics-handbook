---
title: "웹 서버 로그"
parent: "아티팩트 · 서버 애플리케이션"
nav_order: 740
---

# 웹 서버 로그 (Apache·Nginx)

Apache HTTP Server 와 Nginx 는 요청 하나가 끝날 때마다 접근 로그 (access log) 에 한 줄을 쓰고, 오류나 경고가 생기면 오류 로그 (error log) 에 따로 한 줄을 씁니다. 두 로그 모두 평문 텍스트이고, 배포판마다 파일 이름과 기본 형식이 조금씩 다릅니다.

## 무엇을 기록하나 · 왜 생기나

접근 로그는 서버가 받은 HTTP 요청을 기록합니다. 기본 형식에는 원격 주소, 인증 사용자 이름, 시각, 요청 첫 줄(방법·경로·HTTP 판), 상태 코드, 응답 크기, 그리고 combined 형식이면 Referer 와 User-Agent 헤더가 들어갑니다[7][15]. 접근 로그의 파일과 형식은 Apache 에서는 `CustomLog`, Nginx 에서는 `access_log` 지시어가 정합니다. Nginx 는 `access_log` 를 적지 않으면 기본값 `logs/access.log combined` 를 쓰고, 형식 이름 없이 적으면 미리 정의된 combined 형식을 씁니다[15].

오류 로그는 서버를 띄우거나 요청을 처리하다 생긴 오류와 진단 정보를 기록합니다[8]. Apache 는 `ErrorLog` 와 `LogLevel`, Nginx 는 `error_log` 지시어가 파일과 기록 수준을 정합니다[9][16]. Ubuntu 와 RHEL 의 Apache 기본 설정은 둘 다 `LogLevel warn` 입니다[10][11]. Apache 2.4 는 404 응답의 "File does not exist" 메시지를 info 수준으로 기록하므로, 기본값 `warn` 에서는 없는 파일을 찾은 요청이 오류 로그에 남지 않습니다[8].

웹 서버가 침입 경로가 된 사건에서는 이 두 로그가 공격자가 무엇을 요청했고 서버가 어떻게 답했는지를 보여 주는 첫 기록이 됩니다. 조사 흐름은 [웹 서버가 뚫렸나](../../04-scenarios/intrusion/web-compromise.md) 에서 다룹니다.

## 위치와 버전별 차이

Apache 는 Ubuntu 에서 패키지·프로세스 이름이 `apache2` 이고, RHEL 에서는 `httpd` 입니다. 기본 설정 파일이 정하는 로그 파일은 다음과 같습니다.

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| Apache 설정 | `/etc/apache2/apache2.conf`, `sites-available/000-default.conf`, `conf-available/other-vhosts-access-log.conf`[10] | `/etc/httpd/conf/httpd.conf`(`ServerRoot "/etc/httpd"`), `conf.d/*.conf`, `conf.modules.d/*.conf`[11] |
| Apache 로그 폴더 | `/var/log/apache2`(`/etc/apache2/envvars` 의 `APACHE_LOG_DIR`)[10] | `/var/log/httpd`(`/etc/httpd/logs` 가 이 폴더를 가리키는 심볼릭 링크)[11] |
| Apache 오류 로그 | `error.log`[10] | `error_log`[11] |
| Apache 접근 로그 | `access.log`(combined), 자체 로그가 없는 가상 호스트는 `other_vhosts_access.log`(vhost_combined)[10] | `access_log`(combined)[11] |
| Apache TLS 가상 호스트 | 기본으로 켜는 사이트는 `000-default` 뿐[10] | mod_ssl 의 `ssl.conf` 가 `ssl_error_log`, `ssl_access_log`, `ssl_request_log` 를 따로 씀[11] |
| Nginx 설정 | `/etc/nginx/nginx.conf`, `conf.d/*.conf`, `sites-enabled/*`[17] | `/etc/nginx/nginx.conf`, `conf.d/*.conf`, `default.d/*.conf`[18] |
| Nginx 로그 | `/var/log/nginx/access.log`(형식 이름 없음, 곧 combined), `/var/log/nginx/error.log`[17] | `/var/log/nginx/access.log`(`main` 형식), `/var/log/nginx/error.log`[18] |

RHEL 의 `httpd.conf` 는 로그 경로를 `logs/error_log` 처럼 `ServerRoot` 기준 상대 경로로 적습니다[11]. 실제 시스템에서 설정을 따라갈 때는 `/etc/httpd/logs` 링크가 `/var/log/httpd` 로 풀린다는 점을 기억하면 됩니다.

로그 순환 (log rotation) 설정도 배포판마다 다릅니다.

| 로그 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| Apache | `/var/log/apache2/*.log`: daily, rotate 14, compress, delaycompress, create 640 root adm[10] | `/var/log/httpd/*log`: missingok, notifempty, delaycompress, 주기·개수·압축은 적지 않아 전역 `/etc/logrotate.conf` 를 따름(weekly, rotate 4, dateext, `#compress`)[11][19][20] |
| Nginx | `/var/log/nginx/*.log`: daily, rotate 14, compress, delaycompress, create 0640 www-data adm[17] | `/var/log/nginx/*.log`: daily, rotate 10, compress, delaycompress, create 0640 nginx root[18] |

Ubuntu 에서는 `delaycompress` 때문에 가장 최근 회전본 하나는 평문으로 남고 그보다 오래된 회전본부터 gzip 으로 압축됩니다[10][17]. 회전본 이름에 날짜가 붙는지는 전역 `/etc/logrotate.conf` 의 `dateext` 가 정하므로 실제 시스템에서 확인합니다. RHEL 의 Apache 로그는 전역 설정의 `dateext` 를 따라 날짜가 붙은 이름으로 회전하고, 전역 설정에서 `compress` 가 주석 처리돼 있어 압축하지 않습니다[19][20]. 회전본 이름 규칙과 시각 변화는 [로그 순환](../../01-foundations/logging/logrotate.md) 에서 다룹니다.

RHEL 의 httpd 패키지에는 `CustomLog` 대상에 `journald:` 접두어를 쓰면 접근 로그를 파일 대신 systemd 저널로 보내는 패치가 들어 있습니다[11]. 이 설정을 쓴 서버는 `/var/log/httpd` 에 접근 로그 파일이 없을 수 있으므로 `CustomLog` 줄을 먼저 확인하고, 저널 읽는 법은 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 을 봅니다. Nginx 도 `access_log` 에 `syslog:` 접두어를 쓰면 syslog 로 보낼 수 있습니다[15]. 이 경우는 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md) 의 저장 위치를 따라갑니다.

## 구조

### Apache 접근 로그

형식은 `LogFormat` 지시어가 이름을 붙여 정의하고, `CustomLog` 가 그 이름을 골라 씁니다. 배포판 기본 설정의 combined 는 크기 필드 하나가 다릅니다.

```
# Ubuntu 24.04 apache2.conf
LogFormat "%v:%p %h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"" vhost_combined
LogFormat "%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"" combined
LogFormat "%h %l %u %t \"%r\" %>s %O" common

# RHEL 9 httpd.conf
LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
LogFormat "%h %l %u %t \"%r\" %>s %b" common
```

Ubuntu 는 `%b` 로는 중간에 끊긴 요청을 알아낼 수 없어서, `%b` 대신 헤더까지 포함해 실제로 보낸 바이트인 `%O` 를 씁니다[10]. RHEL 과 Apache 원본 예시 설정은 `%b` 를 쓰고, 원본 예시는 기본 `CustomLog` 로 common 을, RHEL 은 combined 를 고릅니다[6][11]. 같은 "combined" 라도 7번째 필드의 뜻이 달라진다는 말입니다.

각 항목의 뜻은 다음과 같습니다[7].

| 항목 | 뜻 |
|---|---|
| `%h` | 원격 호스트. `HostnameLookups` 가 기본값 `Off` 면 IP 주소 |
| `%l` | identd 가 알려 준 원격 로그인 이름. mod_ident 가 없으면 `-` |
| `%u` | 인증된 원격 사용자. 상태가 401 이면 가짜 값일 수 있음 |
| `%t` | 요청을 받은 시각. `[18/Sep/2011:19:18:28 -0400]` 모양이고 끝 숫자는 GMT 와의 차이 |
| `%r` | 요청 첫 줄 |
| `%s`, `%>s` | 상태 코드. 내부 리다이렉트된 요청에서 `%s` 는 원래 요청의 상태, `%>s` 는 최종 상태 |
| `%b` | 헤더를 뺀 응답 크기. 보낸 바이트가 없으면 0 대신 `-` |
| `%O` | 헤더를 포함해 보낸 바이트. 응답 전에 요청이 끊기면 0 일 수 있음. mod_logio 필요 |
| `%I` | 받은 바이트. mod_logio 필요 |
| `%v`, `%p` | 요청을 처리한 서버의 정식 `ServerName` 과 포트 |
| `%D`, `%T` | 요청 처리에 걸린 시간(마이크로초, 초) |
| `%L` | 오류 로그의 요청 로그 ID. 같은 요청의 오류 로그 줄을 찾는 데 씀 |

만든 예시(Ubuntu combined):

```
203.0.113.10 - - [12/Mar/2026:14:05:09 +0900] "GET /index.html HTTP/1.1" 200 3456 "-" "curl/8.5.0"
```

만든 예시(Ubuntu vhost_combined, `other_vhosts_access.log`):

```
www.example.com:443 203.0.113.10 - - [12/Mar/2026:14:05:09 +0900] "POST /login HTTP/1.1" 302 512 "https://www.example.com/" "Mozilla/5.0"
```

Apache 2.0.46 부터는 클라이언트가 보낸 문자열이 들어가는 항목(`%h`, `%l`, `%u`, `%r`, `%{...}i` 등)의 출력할 수 없는 바이트를 `\xhh` 로, `"` 와 `\` 는 앞에 `\` 를 붙여, 공백 문자는 `\n`, `\t` 처럼 C 표기로 적습니다. `%b`, `%s`, `%t`, `%T` 같은 숫자·내부 값은 이스케이프하지 않습니다[7].

### Apache 오류 로그

오류 로그의 줄 모양은 `ErrorLogFormat` 이 정하는데, Ubuntu 와 RHEL 기본 설정은 이 지시어를 두지 않아 기본 모양을 씁니다[10][11]. 스레드를 쓰는 MPM 의 기본 형식과 그 결과 줄은 다음과 같습니다[9].

```
ErrorLogFormat "[%{u}t] [%-m:%l] [pid %P:tid %T] %7F: %E: [client\ %a] %M% ,\ referer\ %{Referer}i"

[Thu May 12 08:28:57.652118 2011] [core:error] [pid 8777:tid 4326490112] [client ::1:58619] AH00124: Request exceeded the limit of 10 internal redirects due to probable configuration error
```

두 번째 필드는 `모듈:수준`, 세 번째 필드는 프로세스·스레드 번호이고, `[client …]` 에는 원격 IP 와 포트가 들어갑니다. 값이 없는 항목은 둘러싼 대괄호째 빠지므로 줄마다 필드 수가 다를 수 있습니다[9].

### Nginx 접근 로그

미리 정의된 combined 형식은 바꿀 수 없고, 다음과 같습니다[15].

```
log_format combined '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent"';
```

RHEL 의 `nginx.conf` 가 쓰는 `main` 형식은 combined 끝에 `"$http_x_forwarded_for"` 필드 하나를 더 붙입니다[18]. Ubuntu 는 형식 이름 없이 `access_log` 를 적어 combined 를 씁니다[17]. 시각·크기와 관련된 변수의 뜻은 다음과 같습니다[12][15].

| 변수 | 뜻 |
|---|---|
| `$time_local` | 공통 로그 형식 (Common Log Format) 의 현지 시각 |
| `$time_iso8601` | ISO 8601 형식의 현지 시각 |
| `$msec` | 로그를 쓰는 때의 시각(초, 밀리초 단위) |
| `$request_time` | 클라이언트에게서 첫 바이트를 읽은 때부터 마지막 바이트를 보낸 뒤 로그를 쓸 때까지 걸린 시간 |
| `$status` | 응답 상태 |
| `$body_bytes_sent`, `$bytes_sent` | 본문 바이트, 보낸 전체 바이트 |
| `$request_length` | 요청 줄·헤더·본문을 합한 길이 |

변수 값이 없으면 `-` 를 씁니다[15]. 기본 이스케이프(`escape=default`)는 `"`, `\`, 32 미만(0.7.0 부터)과 126 초과(1.1.6 부터) 문자를 `\xXX` 로 적고, `escape=json`(1.11.8 부터)은 JSON 문자열 규칙을 따르며, `escape=none`(1.13.10 부터)은 이스케이프하지 않습니다[15]. 소스는 16진 숫자를 대문자로 씁니다[12].

`access_log` 에 `buffer=` 나 `gzip` 을 붙이면 줄을 버퍼에 모았다가 다음 줄이 들어가지 않을 때, `flush=` 로 정한 시간이 지났을 때, 워커 프로세스가 로그를 다시 열거나 끝날 때 파일에 씁니다. `gzip` 을 쓰면 파일 자체가 압축된 채 기록되고 `zcat` 으로 읽습니다. `if=조건` 을 붙이면 조건이 거짓인 요청은 기록하지 않습니다[15].

### Nginx 오류 로그

한 줄은 시각, `[수준]`, `프로세스번호#스레드번호:`, 연결이 있을 때만 `*연결번호`, 메시지 순서로 이어집니다[13]. 수준은 debug, info, notice, warn, error, crit, alert, emerg 이고, 지시어를 적지 않았을 때의 기본값은 `logs/error.log error` 입니다[16].

만든 예시(메시지 부분의 실제 모양은 실제 로그로 확인합니다):

```
2026/03/12 14:05:09 [error] 1234#1234: *57 open() "/var/www/html/admin.php" failed (2: No such file or directory)
```

## 증거로서 의미

### 증명하는 것

- 서버 시계 기준으로 그 시각에, 그 원격 주소에서 온 연결이 그 요청 줄을 보냈고, 서버가 그 상태 코드로 답했다는 기록이 있다는 것.
- 인증이 걸린 경로라면 요청에 그 사용자 이름이 쓰였다는 것(`%u`, `$remote_user`). Apache 는 상태가 401 이면 이 값이 가짜일 수 있습니다[7].
- 응답 크기와 처리 시간(형식에 들어 있을 때). 같은 경로에 대한 요청의 크기가 갑자기 달라지면 그 사이에 파일 내용이 바뀌었을 가능성이 있습니다.
- 오류 로그에 남은 오류가 그 시각에 서버에서 일어났다는 것. 기록 수준(`LogLevel`, `error_log`)보다 낮은 메시지는 남지 않습니다[8][16].

### 증명하지 못하는 것

- 원격 주소 뒤의 실제 사람이나 기기. 프록시·NAT·로드 밸런서 뒤라면 로그의 주소는 중간 장비의 주소입니다. `X-Forwarded-For` 는 클라이언트가 보내는 헤더라 거짓으로 채울 수 있습니다. `%h` 대신 `%{X-Forwarded-For}i` 를 기록하는 방식은 권하지 않고 mod_remoteip 를 쓰는 방식을 권합니다[10].
- User-Agent 와 Referer 가 사실이라는 것. 둘 다 요청 헤더 내용을 그대로 옮긴 값입니다[7].
- POST 본문이나 업로드한 파일 내용. 기본 형식에는 들어가지 않습니다.
- 공격이 성공했다는 것. 200 응답도 오류를 알리는 페이지일 가능성이 있고, 성공 여부는 웹 루트의 파일 변화나 뒤이은 프로세스 실행으로 확인해야 합니다.
- 실제로 네트워크로 보낸 양. `%b` 는 응답 크기일 뿐이고 헤더를 포함한 전송량은 `%O` 가 기록합니다[7][10].
- 줄이 없다는 사실이 요청이 없었다는 뜻이라는 것. 조건부 기록(Nginx `if=`), 버퍼에 남아 있다가 비정상 종료로 사라진 줄, 가상 호스트마다 다른 파일, 저널이나 syslog 로 보낸 로그가 있을 수 있습니다[11][15].

보고서에는 "이 시간대에 이 주소에서 이 경로로 POST 요청이 들어왔고 서버가 200 으로 답한 기록이 있다" 처럼 로그로 확인되는 만큼만 씁니다.

## 시각 해석

접근 로그와 오류 로그는 시간대를 다루는 방식이 다릅니다.

| 로그 | 시각 모양 | 시간대 |
|---|---|---|
| Apache 접근 로그 `%t` | `[12/Mar/2026:14:05:09 +0900]` | 현지 시각과 GMT 와의 차이[7] |
| Apache 오류 로그 | `[Thu Mar 12 14:05:09.123456 2026]` | 현지 시각만, 차이 없음[4][9] |
| Nginx 접근 로그 `$time_local` | `12/Mar/2026:14:05:09 +0900` | 현지 시각과 UTC 와의 차이[14] |
| Nginx 오류 로그 | `2026/03/12 14:05:09` | 현지 시각만, 차이 없음[14] |

(표의 시각 값은 만든 예시입니다.) 오류 로그를 UTC 로 바꾸려면 서버의 시간대를 알아야 합니다. 시간대 설정은 [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md) 에서 확인합니다. Apache 2.4.58 부터는 `ErrorLogFormat` 에 시간대를 포함한 `%{cuz}t` 를 쓸 수 있지만 두 배포판의 기본 설정은 쓰지 않습니다[9][10][11].

두 서버는 한 줄에 적는 시각의 기준점도 다릅니다. Apache 의 `%t` 는 요청을 받은 시각이고, `%{end:형식}t` 로 바꿔야 로그를 쓰는 시각, 곧 요청 처리가 끝날 무렵이 됩니다[7]. 줄은 처리가 끝난 뒤에 쓰이므로, 오래 걸린 요청은 파일 안에서 뒤에 적힌 줄보다 이른 시각을 달고 있을 수 있습니다. Nginx 의 `$time_local` 은 로그를 쓰는 순간의 캐시된 시각을 그대로 복사하고[12], `$msec` 과 `$request_time` 도 로그를 쓰는 때를 기준으로 합니다[15]. 그래서 Nginx 접근 로그의 시각은 응답을 끝낸 때에 가깝습니다. Nginx 를 앞에 두고 Apache 를 뒤에 둔 구조에서 두 로그를 맞춰 볼 때는 이 차이와 `$request_time` 만큼의 간격을 감안합니다.

로그 파일 자체의 수정 시각은 마지막 줄을 쓴 때이고, 회전 뒤 새 파일의 생성 시각은 회전 시각입니다. 자세한 내용은 [로그 순환](../../01-foundations/logging/logrotate.md) 에서 다룹니다.

## 함정과 한계

- 파일 이름이 배포판마다 다릅니다(`access.log`·`error.log` 대 `access_log`·`error_log`). 수집 도구의 경로 목록도 서로 다릅니다. ForensicArtifacts 의 `ApacheErrorLogs` 는 `/var/log/httpd/error*` 로 넓게 잡지만 RHEL 의 `ssl_error_log`, `ssl_access_log`, `ssl_request_log` 는 Apache 접근·오류 로그 정의에 걸리지 않고, `ApacheConfigurationFolder` 의 `/etc/httpd/*.conf` 는 한 단계 아래의 `/etc/httpd/conf/httpd.conf` 를 잡지 않습니다[1]. dissect.target 은 기본 오류 로그 이름으로 `error.log` 만 찾으므로 RHEL 의 `error_log` 는 설정 파일의 `ErrorLog` 를 따라가야 찾습니다[4]. 수집 뒤에는 `/var/log/httpd`, `/var/log/apache2`, `/var/log/nginx` 폴더 전체 목록과 대조합니다.
- Ubuntu 는 자체 `CustomLog` 가 없는 가상 호스트의 요청을 `other_vhosts_access.log` 에 모읍니다. 설치 스크립트가 이 설정을 기본으로 켭니다[10].
- 형식이 기본과 다르면 파서가 줄을 놓칩니다. plaso 의 `apache_access` 파서는 common, combined, vhost_combined 세 문법만 알고 줄 끝까지 맞아야 하므로, RHEL Nginx 의 `main`(필드 하나 더)이나 `%D` 를 덧붙인 형식은 읽지 못합니다. 이 파서는 HTTP 방법도 CONNECT, DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT, TRACE 만 받아서, 그 밖의 방법이나 깨진 요청 줄은 건너뜁니다[5]. 스캐너가 남긴 이상한 요청은 바로 이런 줄이므로 파서 결과만 보지 말고 원문을 함께 검색합니다.
- 크기 필드의 뜻이 배포판마다 다릅니다. 숫자라서 파서는 똑같이 읽지만 Ubuntu 는 헤더 포함 전송량(`%O`), RHEL 은 본문 크기(`%b`)입니다[5][10][11].
- dissect.target 은 주석 처리된(`#`) `CustomLog`, `access_log` 지시어도 로그 경로 후보로 찾습니다[4]. 결과에 경로가 보인다고 그 설정이 켜져 있었다고 보면 안 됩니다.
- 순환 때문에 오래된 기록이 이미 지워졌을 수 있습니다. Ubuntu 기본값은 매일 회전해 14개, RHEL 의 Apache 는 매주 회전해 4개, RHEL 의 Nginx 는 매일 회전해 10개를 남깁니다[10][17][18][19]. 지운 회전본은 [지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md) 로 찾아봅니다.
- Nginx 로그의 소유자는 Ubuntu 에서 `www-data`, RHEL 에서 `nginx` 입니다[17][18]. 웹 서버 계정을 얻은 공격자가 로그를 고치거나 지웠을 가능성이 있으므로, 줄 사이 시각이 크게 비거나 파일 크기가 회전 주기에 비해 작으면 의심합니다. 흔적을 지운 사건의 조사는 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md) 를 봅니다.
- 로그에는 클라이언트가 보낸 값이 들어갑니다. 두 서버 모두 기본으로 제어 문자를 이스케이프하지만 Nginx `escape=none` 같은 설정에서는 원문 바이트가 그대로 남으므로, 원본 로그를 터미널에 바로 출력하지 않습니다[8][15].

## 직접 분석해 보기

### 원문과 헥스로 한 번

로그는 텍스트라서 대부분 원문으로 읽습니다. 헥스는 이스케이프된 바이트를 확인할 때 씁니다.

1. 이미지를 읽기 전용으로 붙이고 웹 서버 설정 파일에서 `CustomLog`, `ErrorLog`, `LogFormat`, `access_log`, `error_log`, `log_format` 줄을 모두 모아 실제 로그 경로와 형식을 정합니다. 가상 호스트 설정 파일(`sites-enabled`, `conf.d`)까지 봅니다.
2. 회전본을 포함해 로그를 시간 순서로 이어 붙입니다. `zcat -f` 는 압축 파일과 평문 파일을 함께 읽습니다.
3. 상태 코드, 방법, 경로별로 세어 보고 드문 값부터 봅니다. 웹 루트 아래 새로 생긴 스크립트 파일 이름을 접근 로그에서 검색하면 그 파일을 처음 요청한 주소와 시각이 나옵니다.
4. 오류 로그는 현지 시각이므로 서버 시간대로 UTC 로 바꾼 뒤 접근 로그와 맞춥니다.

Nginx 기본 이스케이프가 어떻게 남는지는 헥스로 보면 분명합니다. 클라이언트가 User-Agent 에 ESC 바이트(`0x1B`)를 넣어 보냈다면 파일에는 그 바이트가 아니라 네 글자 `\x1B` 가 적힙니다. 다음은 명세로 만든 예시입니다.

```
보낸 헤더 값  : 41 1B 42              A.B
로그 파일 내용: 41 5C 78 31 42 42     A\x1BB
```

로그에 `\x` 로 시작하는 네 글자가 보이면 원래 요청에 제어 문자나 비ASCII 바이트가 들어 있었다는 뜻입니다.

### 공개 도구로 한 번

- dissect.target 은 `apache.access`, `apache.error`, `nginx.access`, `nginx.error` 로 로그를 읽고, `webserver.logs` 로 설치된 웹 서버의 접근·오류 로그를 한꺼번에 내놓습니다. 설정 파일의 `ServerRoot`, `Include`, `CustomLog`, `ErrorLog`(Nginx 는 `access_log`, `error_log`, `include`)를 따라가 기본 경로가 아닌 로그도 찾고, 압축된 회전본도 풀어서 읽습니다. `apache.hosts`, `nginx.hosts` 는 가상 호스트의 서버 이름·포트·문서 루트·로그 경로·인증서 경로를, `apache.certificates`, `nginx.certificates` 는 인증서 내용을 내놓습니다[4].
- dissect.target 의 Apache 접근 로그 파서는 줄 모양으로 형식을 짐작합니다. 첫 필드에 `:` 와 `.` 이 함께 있으면 vhost_combined, 줄 끝이 `"` 면 combined, 숫자나 `-` 면 common 으로 봅니다. 오류 로그 시각에는 분석 대상 시스템의 시간대를 붙입니다[4].
- plaso 의 `apache_access` 파서는 접근 로그 줄을 타임라인 사건으로 바꾸고, 줄에 적힌 GMT 와의 차이를 반영합니다[5]. plaso 에는 Nginx 전용 파서가 없고, Nginx 의 combined 줄은 이 파서로 읽을 수 있습니다. 타임라인 만드는 법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 에서 다룹니다.
- UAC 는 `/var/log` 아래 `access_log*`, `access.log*`, `error_log*`, `error.log*` 이름의 파일(Nginx 정의는 앞에 다른 글자가 붙은 이름까지)과 `/var/log/apache`, `/var/log/apache2`, `/var/log/httpd`, `/var/log/nginx` 폴더를 파일당 1GB 한도로 모읍니다[2][3].

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 웹 루트와 임시 폴더의 파일 | 로그에 처음 나타난 스크립트 파일의 생성·수정 시각 | [임시 폴더와 메모리 파일 시스템](../file-activity/tmp-shm.md), [ext4](../../01-foundations/filesystem/ext4/index.md) |
| 감사 로그의 실행 기록 | 웹 서버 계정(`www-data`, `apache`, `nginx`)이 실행한 프로그램 | [감사 로그의 실행 기록](../execution/auditd-execve.md) |
| 셸 명령 기록 | 웹 서버 계정이나 관리자가 로그 파일을 건드린 명령 | [셸 명령 기록](../execution/shell-history/index.md) |
| 알려진 파일 대조 | 웹 루트에 올라온 파일이 알려진 웹셸인지 | [알려진 파일 대조와 YARA](../../03-techniques/analysis/hash-yara.md) |
| 데이터베이스 서버 로그 | 웹 요청과 같은 시각의 쿼리·접속 | [데이터베이스 서버 로그](database-logs.md) |
| 인증 로그 | 웹 요청 뒤에 이어진 SSH·sudo 사용 | [인증 로그](../logins/auth-log.md) |
| 방화벽 | 같은 원격 주소의 다른 포트 접속 | [방화벽](../network/firewall.md) |

기본 접근 로그에는 요청 하나가 어떤 다른 요청을 낳았는지 잇는 인과 정보가 없어서, 프록시와 뒤쪽 서버처럼 여러 애플리케이션의 로그를 서로 맞추기 어렵습니다[21]. 이럴 때는 시각과 주소를 기준으로 맞춰 보고, 맞춘 결과는 추정이라고 적습니다. Apache 의 `%L` 을 접근 로그와 오류 로그 형식에 함께 넣어 둔 서버라면 같은 요청의 두 줄을 그 값으로 이을 수 있습니다[7][9]. 여러 로그를 함께 보는 절차는 [로그 분석](../../03-techniques/analysis/log-analysis.md) 에서 다룹니다.

## 실습

NIST CFReDS 등에 공개된 Linux 웹 서버 이미지로 다음 질문을 풀어 봅니다.

1. 분석 대상 시스템에 설치된 웹 서버는 무엇이고, 설정 파일이 가리키는 접근 로그·오류 로그의 실제 경로와 형식 이름은 무엇인가?
2. 회전본을 포함해 가장 이른 줄과 가장 늦은 줄의 시각은 언제이고, 그 사이에 빠진 날이 있는가?
3. 가장 많이 요청한 원격 주소 다섯 개와, 404 를 가장 많이 받은 주소는 무엇인가?
4. 웹 루트 아래 확장자가 스크립트인 파일 가운데 설치 뒤에 생긴 것이 있다면, 그 파일을 처음 요청한 줄은 무엇인가?
5. 오류 로그의 시각을 UTC 로 바꾸면 접근 로그의 어느 줄과 맞는가?

## 참고 문헌

1. ForensicArtifacts, artifacts/data/webservers.yaml. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/webservers.yaml
2. UAC, artifacts/files/logs/apache.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/logs/apache.yaml
3. UAC, artifacts/files/logs/nginx.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/logs/nginx.yaml
4. fox-it dissect.target, dissect/target/plugins/apps/webserver (webserver.py, apache.py, nginx.py). https://github.com/fox-it/dissect.target/tree/main/dissect/target/plugins/apps/webserver
5. plaso, plaso/parsers/text_plugins/apache_access.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/apache_access.py
6. Apache HTTP Server 2.4, docs/conf/httpd.conf.in. https://github.com/apache/httpd/blob/2.4.x/docs/conf/httpd.conf.in
7. Apache HTTP Server 2.4, docs/manual/mod/mod_log_config.xml. https://github.com/apache/httpd/blob/2.4.x/docs/manual/mod/mod_log_config.xml
8. Apache HTTP Server 2.4, docs/manual/logs.xml. https://github.com/apache/httpd/blob/2.4.x/docs/manual/logs.xml
9. Apache HTTP Server 2.4, docs/manual/mod/core.xml (ErrorLogFormat). https://github.com/apache/httpd/blob/2.4.x/docs/manual/mod/core.xml
10. Ubuntu apache2 패키지(noble), debian/config-dir/apache2.conf.in·envvars·sites-available/000-default.conf·conf-available/other-vhosts-access-log.conf, debian/apache2.logrotate, debian/apache2.postinst. https://git.launchpad.net/ubuntu/+source/apache2/tree/debian?h=ubuntu/noble
11. CentOS Stream 9 httpd 패키지, httpd.conf·ssl.conf·httpd.logrotate·httpd.spec·httpd-2.4.43-logjournal.patch. https://gitlab.com/redhat/centos-stream/rpms/httpd/-/tree/c9s
12. nginx, src/http/modules/ngx_http_log_module.c. https://github.com/nginx/nginx/blob/master/src/http/modules/ngx_http_log_module.c
13. nginx, src/core/ngx_log.c. https://github.com/nginx/nginx/blob/master/src/core/ngx_log.c
14. nginx, src/core/ngx_times.c. https://github.com/nginx/nginx/blob/master/src/core/ngx_times.c
15. nginx.org, xml/en/docs/http/ngx_http_log_module.xml. https://github.com/nginx/nginx.org/blob/main/xml/en/docs/http/ngx_http_log_module.xml
16. nginx.org, xml/en/docs/ngx_core_module.xml (error_log). https://github.com/nginx/nginx.org/blob/main/xml/en/docs/ngx_core_module.xml
17. Ubuntu nginx 패키지(noble), debian/conf/nginx.conf, debian/nginx-common.nginx.logrotate. https://git.launchpad.net/ubuntu/+source/nginx/tree/debian?h=ubuntu/noble
18. CentOS Stream 9 nginx 패키지, nginx.conf·nginx.logrotate·nginx.spec. https://gitlab.com/redhat/centos-stream/rpms/nginx/-/tree/c9s
19. logrotate, examples/logrotate.conf. https://github.com/logrotate/logrotate/blob/main/examples/logrotate.conf
20. CentOS Stream 9 logrotate 패키지, logrotate.spec. https://gitlab.com/redhat/centos-stream/rpms/logrotate/-/blob/c9s/logrotate.spec
21. Johannes Olegård, Stefan Axelsson, Yuhong Li, "When is logging sufficient? — Tracking event causality for improved forensic analysis and correlation", Forensic Science International: Digital Investigation 52 (2025) 301877. https://doi.org/10.1016/j.fsidi.2025.301877
