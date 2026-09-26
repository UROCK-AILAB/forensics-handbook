---
title: "데이터베이스 서버 로그"
parent: "아티팩트 · 서버 애플리케이션"
nav_order: 750
---

# 데이터베이스 서버 로그 (MySQL·PostgreSQL)

MySQL 과 PostgreSQL 서버가 남기는 오류 로그·연결 기록·쿼리 기록·바이너리 로그와 클라이언트 기록 파일에서 누가 언제 어느 데이터베이스에 접속했고 무엇을 바꿨는지를 읽는 법을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

데이터베이스 서버의 로그는 운영자가 장애를 찾도록 남기는 기록입니다. 그래서 기본 설정에서 남는 것은 서버 시작·종료, 오류, 경고 정도이고, 누가 어떤 SQL 문을 실행했는지는 따로 켜야 남습니다. MySQL 8.0 은 일반 쿼리 로그(general query log)와 느린 쿼리 로그(slow query log)가 기본으로 꺼져 있습니다[1]. PostgreSQL 은 연결·연결 끊김 기록(`log_connections`, `log_disconnections`)이 꺼져 있고 문장 기록(`log_statement`)이 `none` 입니다[12][13].

기본값으로 켜져 있어 증거가 되는 기록도 있습니다. MySQL 8.0 은 바이너리 로그(binary log)가 기본으로 켜져 있어 데이터를 바꾼 사건이 행 단위로 쌓입니다[1][2]. PostgreSQL 은 비밀번호 인증 실패를 `FATAL` 수준으로 남기므로 연결 기록을 켜지 않아도 로그인 실패가 서버 로그에 남습니다[12][14].

서버 로그와 별개로, 사용자가 대화형 클라이언트(`mysql`, `psql`)를 쓰면 홈 디렉터리에 입력한 명령 기록 파일(`.mysql_history`, `.psql_history`)이 생깁니다[17][18].

## 위치와 버전별 차이

기준 판의 패키지는 Ubuntu 24.04 가 `mysql-8.0` 과 `postgresql-16`, RHEL 9 가 `mysql`(8.0)·`mariadb`(10.5) 와 `postgresql`(13) 입니다[9][10][11][15][16].

### MySQL

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| 서버 설정 | `/etc/mysql/mysql.conf.d/mysqld.cnf`[9] | `/etc/my.cnf.d/mysql-server.cnf`[10] |
| 오류 로그 | `/var/log/mysql/error.log` (`log_error` 로 지정)[9] | `/var/log/mysql/mysqld.log` (`log-error` 로 지정)[10] |
| 데이터 디렉터리 | `/var/lib/mysql` (설정 파일에는 주석으로만 있음)[9] | `/var/lib/mysql`, 소켓 `/var/lib/mysql/mysql.sock`[10] |
| 일반 쿼리 로그 | 꺼짐. 주석 예시 `/var/log/mysql/query.log`[9] | 꺼짐. 설정 없음[10] |
| 느린 쿼리 로그 | 꺼짐. 주석 예시 `/var/log/mysql/mysql-slow.log`, `long_query_time = 2`[9] | 꺼짐. 설정 없음[10] |
| 바이너리 로그 | 켜짐(서버 기본값). `max_binlog_size = 100M`[1][9] | 켜짐(서버 기본값)[1] |
| 로그 순환 | `/var/log/mysql.log`, `/var/log/mysql/*log` 를 `daily`, `rotate 7`, `compress`, `create 640 mysql adm` 으로 돌리고 끝나면 `mysqladmin flush-logs` 를 부름[9] | `/etc/logrotate.d/mysqld` 로 설치하는 upstream 파일은 모든 줄이 주석[8][10] |

RHEL 9 에서 MariaDB 를 쓰면 오류 로그는 `/var/log/mariadb/mariadb.log` 입니다[11]. MariaDB 의 로그 줄 모양은 이 페이지에서 설명하는 MySQL 8.0 형식과 다를 수 있으므로 실제 파일을 열어 형식부터 확인합니다.

일반 쿼리 로그와 느린 쿼리 로그를 켜면서 파일 이름을 주지 않으면, 데이터 디렉터리 안에 호스트 이름을 딴 `호스트이름.log` 와 `호스트이름-slow.log` 가 생깁니다[3][2]. `log_output` 이 `TABLE` 이면 두 로그는 파일이 아니라 `mysql` 스키마 안의 로그 테이블에 쌓입니다[1][3].

바이너리 로그 파일 이름의 기본 접두어는 `binlog` 이고[2], 설정에 경로가 없으면 데이터 디렉터리에 생깁니다[2]. Ubuntu 설정 파일의 `# log_bin = /var/log/mysql/mysql-bin.log` 는 주석이므로 이 경로에 파일이 없다고 바이너리 로그가 꺼진 것은 아닙니다[9].

### PostgreSQL

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| 데이터 디렉터리 | `/var/lib/postgresql/16/main` (기본 `/var/lib/postgresql/%v/%c`)[15] | `/var/lib/pgsql/data` (`PGDATA`)[16] |
| 설정 | `/etc/postgresql/16/main/postgresql.conf`[15] | `/var/lib/pgsql/data/postgresql.conf`[13][16] |
| 서버 로그 | `/var/log/postgresql/postgresql-16-main.log`[15] | `/var/lib/pgsql/data/log/postgresql-Mon.log` … `postgresql-Sun.log`[16][12] |
| 로그 줄 머리 | `log_line_prefix = '%m [%p] %q%u@%d '`[15] | 기본값 `'%m [%p] '`[12] |
| 로그 순환 | logrotate: `weekly`, `rotate 10`, `copytruncate`, `delaycompress`, `compress`[15] | 서버가 직접 돌림: 요일 이름 파일, `log_rotation_age = 1d`, `log_truncate_on_rotation = on`[16] |

Ubuntu 는 `pg_createcluster` 가 클러스터를 만들 때 `/var/log/postgresql/postgresql-판-클러스터이름.log` 파일을 만들고 권한을 0640 으로 둡니다[15]. `/var/log/postgresql` 디렉터리는 권한 01775, 소유자 root, 그룹 postgres 로 만듭니다[15].

RHEL 9 패키지는 로그 수집기(`logging_collector = on`)를 켜고 파일 이름을 `postgresql-%a.log` 로 바꿔 둡니다[16]. `log_directory` 기본값 `log` 는 데이터 디렉터리 기준 상대 경로라서 로그가 `/var/log` 밖에 쌓입니다[12].

### 클라이언트 기록 파일

| 클라이언트 | 파일 |
|---|---|
| `mysql` | `/.mysql_history`, `/root/.mysql_history`, 각 사용자 홈의 `.mysql_history`[17] |
| `psql` | `/.psql_history`, `/root/.psql_history`, `/var/lib/postgresql/.psql_history`, `/var/lib/pgsql/.psql_history`, 각 사용자 홈의 `.psql_history`[17] |

RHEL 9 에서 postgres 계정의 홈은 `/var/lib/pgsql` 이라서, `sudo -u postgres psql` 로 들어간 기록은 `/var/lib/pgsql/.psql_history` 에 남습니다[16][17]. Ubuntu 는 분석 대상의 `/etc/passwd` 에서 postgres 계정의 홈을 확인하고 그 아래를 봅니다. 셸 기록 파일과 같은 방식으로 읽는 점은 [셸 명령 기록](../execution/shell-history/index.md)에서 다룹니다.

## 구조

### MySQL 오류 로그

한 줄은 다음 모양이고, 오류 번호는 여섯 자리로 채웁니다[4].

```
시각 스레드ID [라벨] [MY-오류번호] [하위시스템] 메시지
```

시각은 `2026-03-12T05:05:09.123456Z` 처럼 마이크로초까지 적는 ISO 8601 형식이고, 끝은 UTC 면 `Z`, 현지 시각이면 `+09:00` 같은 차이입니다[5]. 날짜는 만든 예시입니다.

가동 구간은 시작·종료 메시지로 추정합니다. 시작 메시지는 `%s: ready for connections. Version: '%s'  socket: '%s'  port: %d  %s.`, 정상 종료 메시지는 `%s: Shutdown complete (mysqld %s)  %s.` 입니다[7].

로그인 실패는 오류 로그 상세 수준(`log_error_verbosity`)이 3 일 때만 오류 로그에 `Access denied for user '%-.48s'@'%-.64s' (using password: %s)` 로 남습니다[6][7]. 기본값은 2(오류와 경고)라서 기본 설정에서는 오류 로그에 로그인 실패가 없습니다[1].

### MySQL 일반 쿼리 로그

파일을 열 때 서버 이름·판과 함께 `started with:` 줄, `Tcp port: %d  Unix socket: %s` 줄, 그리고 `Time                 Id Command    Argument` 머리 줄을 씁니다[3]. 그 뒤 한 사건이 한 줄이고, 시각·탭·다섯 자리로 맞춘 스레드 ID·공백·명령 종류·탭·인자 순서입니다[3].

```
시각(탭)스레드ID 명령종류(탭)인자
```

접속 사건의 인자는 `사용자@호스트 on 데이터베이스 using 연결방식` 모양이고, 로그인한 이름과 실제로 인증된 계정이 다르면 `사용자@호스트 as 계정 on 데이터베이스 using 연결방식` 입니다[6]. 일반 쿼리 로그가 켜져 있으면 로그인 실패도 오류 로그 수준과 상관없이 접속 명령으로 접근 거부 메시지를 남깁니다[6]. 같은 스레드 ID 가 붙은 줄을 모으면 한 연결에서 실행한 문장을 차례로 볼 수 있습니다.

### MySQL 느린 쿼리 로그

한 사건은 `# Time: 시각`, `# User@Host: 사용자정보  Id: 스레드ID`, `# Query_time: … Lock_time: … Rows_sent: … Rows_examined: …` 세 줄 뒤에 SQL 문이 옵니다[3]. `log_slow_extra` 를 켜면 셋째 줄에 `Thread_id`, `Errno`, `Bytes_received`, `Bytes_sent`, `Start:`, `End:` 같은 필드가 더 붙습니다[1][3]. `long_query_time` 보다 오래 걸린 문장만 남으므로 전체 실행 기록이 아닙니다.

### MySQL 바이너리 로그

`log_bin` 기본값은 켜짐이고, 서버를 처음 초기화하는 동안에만 끕니다[1][2]. 기본 형식(`binlog_format`)은 바뀐 행을 이진 형식으로 적는 `ROW` 이고, `STATEMENT` 와 `MIXED` 도 고를 수 있습니다[1][2]. `binlog_expire_logs_seconds` 기본값은 2592000초(30일)이고, 지난 파일은 서버 시작 때와 바이너리 로그 파일이 바뀔 때 지웁니다[1]. 파일은 이진 형식이라 MySQL 이 함께 내는 `mysqlbinlog` 로 풀어 읽습니다[10].

### PostgreSQL 서버 로그

한 줄은 `log_line_prefix` 로 만든 머리 뒤에 `심각도:` 와 공백 두 칸, 메시지가 옵니다[14]. 여러 줄 메시지는 다음 머리가 나올 때까지 이어집니다[19]. 머리에 쓰는 주요 이스케이프는 다음과 같습니다(PostgreSQL 16 기준)[12].

| 이스케이프 | 뜻 |
|---|---|
| `%m` | 밀리초까지 적은 시각과 시간대 약어 |
| `%t` | 밀리초 없는 시각과 시간대 약어 |
| `%p` | 프로세스 ID |
| `%u` · `%d` | 사용자 이름 · 데이터베이스 이름 |
| `%r` · `%h` | 원격 호스트와 포트 · 원격 호스트 |
| `%a` | 애플리케이션 이름 |
| `%c` · `%l` | 세션 ID · 세션 안의 줄 번호 |
| `%q` | 세션이 아닌 프로세스는 여기서 머리를 끝냄 |

`%m` 은 `%Y-%m-%d %H:%M:%S` 뒤에 `.밀리초` 세 자리와 시간대 약어를 붙입니다[14]. Ubuntu 머리에는 `%q` 가 있어서 백그라운드 프로세스의 줄에는 `사용자@데이터베이스` 가 빠집니다[15][12].

연결 기록을 켜면 다음 메시지가 남습니다[14].

| 설정 | 메시지 |
|---|---|
| `log_connections` | `connection received: host=%s port=%s` |
| `log_connections` | `connection authorized: user=%s database=%s application_name=%s` (TLS 면 ` SSL enabled (protocol=%s, cipher=%s, bits=%d)` 가 붙음). 복제 연결은 `replication connection authorized: user=%s` |
| `log_disconnections` | `disconnection: session time: %d:%02d:%02d.%03d user=%s database=%s host=%s port=%s` |
| 항상(`FATAL`) | `password authentication failed for user "%s"` |
| 항상(`FATAL`) | `no pg_hba.conf entry for host "%s", user "%s", database "%s", %s` |

`log_statement` 는 `none`(기본)·`ddl`·`mod`·`all` 가운데 하나입니다[13]. `ddl` 은 `CREATE`·`ALTER`·`DROP` 같은 정의 문장을, `mod` 는 여기에 `INSERT`·`UPDATE`·`DELETE`·`TRUNCATE`·`COPY FROM` 을 더해 남깁니다[13]. 단순한 문법 오류가 있는 문장은 `all` 이어도 남지 않고, `log_min_error_statement`(기본 `error`)에 걸려 오류 메시지와 함께 남습니다[13][12].

로그 출력 방식(`log_destination`)은 기본이 `stderr` 이고, PostgreSQL 16 에서는 `csvlog`, `jsonlog`, `syslog` 도 고를 수 있습니다[12]. `syslog` 를 고르면 서버 로그가 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md) 쪽 파일로 갑니다.

## 증거로서 의미

### 증명하는 것

- PostgreSQL 의 `password authentication failed` 줄은 그 시각에 그 사용자 이름으로 비밀번호 인증을 시도해 실패한 기록입니다. 기본 설정에서도 남습니다[14][12].
- 연결 기록이 켜져 있으면 PostgreSQL 은 어느 호스트에서 어느 계정으로 어느 데이터베이스에 연결했는지와 세션 길이를 남깁니다[14]. MySQL 은 일반 쿼리 로그가 켜져 있을 때 같은 내용을 남깁니다[6].
- 시작·종료 메시지로 서버가 돌던 구간을 알 수 있습니다[7][14].
- 바이너리 로그에는 데이터를 바꾼 사건이 남아, 삭제·수정이 언제 있었는지 재구성하는 근거가 됩니다[1].
- `.mysql_history`, `.psql_history` 에 문장이 있으면 그 계정 홈에서 대화형 클라이언트를 쓴 적이 있다는 뜻입니다.

### 증명하지 못하는 것

- 기본 설정에서는 어느 계정이 어떤 SQL 문을 실행했는지 서버 로그에 없습니다[1][12]. 로그에 없다고 접속이나 조회가 없었다고 말할 수 없습니다.
- 바이너리 로그는 데이터를 바꾼 사건만 담으므로 데이터를 읽기만 한 흔적은 없습니다.
- 데이터베이스 계정 이름은 운영체제 계정이 아닙니다. 웹 애플리케이션이 공용 계정 하나로 접속하면 로그의 사용자 이름으로 사람을 가를 수 없습니다.
- 클라이언트 기록 파일에는 시각이 없고, 원격 애플리케이션이 드라이버로 접속한 경우는 남지 않습니다.

보고서에는 "2026-03-12 14:05 KST 에 `appuser` 계정으로 `shopdb` 에 연결한 기록이 있다" 처럼 로그로 확인되는 만큼만 씁니다(값은 만든 예시).

## 시각 해석

MySQL 파일 로그의 시각은 `log_timestamps` 로 정하고, 기본값 `UTC` 면 끝에 `Z` 가 붙습니다[1][2][5]. `SYSTEM` 으로 바꾸면 시스템 현지 시각에 `+hh:mm` 차이를 붙입니다[5]. 이 설정은 파일 로그에만 영향을 주고 로그 테이블에는 영향이 없습니다[1]. 오류 로그·일반 쿼리 로그·느린 쿼리 로그가 모두 같은 설정을 따릅니다[3][5].

PostgreSQL 로그의 시각은 `log_timezone` 기준 현지 시각이고, 시간대는 약어로만 적습니다[14][13]. 내장 기본값은 GMT 이지만 `initdb` 가 클러스터를 만들 때 시스템 시간대를 `postgresql.conf` 의 `timezone`·`log_timezone` 에 적어 둡니다[13][14]. 그래서 클러스터를 만든 뒤 시스템 시간대를 바꿨다면 로그 시간대가 옛 값일 가능성이 있습니다. 분석 대상의 `postgresql.conf` 에서 `log_timezone` 을 먼저 읽고, 시스템 시간대는 [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md)에서 확인합니다.

RHEL 9 의 요일 이름 파일은 이름에 날짜가 없습니다. `postgresql-Mon.log` 가 어느 날짜의 월요일인지는 파일 안 첫 줄과 마지막 줄의 시각으로 정합니다.

## 함정과 한계

- RHEL 9 의 PostgreSQL 로그는 요일마다 파일 하나라 최대 일주일치만 남습니다. 자르기는 시간 기준 회전 때만 일어나고, 같은 날 서버를 다시 시작하면 기존 파일에 이어 씁니다[16][12].
- RHEL 9 의 PostgreSQL 로그는 `/var/log` 밖에 있습니다. UAC 의 `/var/log` 수집 항목은 이 파일을 담지 못하므로 데이터 디렉터리의 `log` 폴더를 따로 모읍니다[20]. MySQL 바이너리 로그와 기본 이름의 일반·느린 쿼리 로그도 데이터 디렉터리에 있습니다.
- Ubuntu 의 PostgreSQL 로그는 `copytruncate` 로 돌리므로 복사와 자르기 사이의 줄을 잃을 수 있습니다[15]. 회전 방식은 [로그 순환](../../01-foundations/logging/logrotate.md)에서 다룹니다.
- Ubuntu 의 MySQL logrotate 파일에는 "The error log is obsolete, messages go to syslog now." 라는 주석이 있지만, 같은 패키지의 `mysqld.cnf` 는 `log_error = /var/log/mysql/error.log` 로 파일에 씁니다[9]. 로그가 어디로 가는지는 설정 파일로 판단합니다.
- RHEL 9 의 MySQL 오류 로그는 logrotate 파일이 upstream 판처럼 모두 주석이면 돌지 않아서, 오래된 기록이 한 파일에 남아 있을 수 있습니다[8][10]. 실제 시스템의 `/etc/logrotate.d/mysqld` 를 열어 주석이 풀렸는지 확인합니다. Ubuntu 는 7일치입니다[9].
- `log_output = TABLE` 이면 쿼리 로그가 데이터베이스 안에 있어서 파일만 모으면 빠집니다[1].
- PostgreSQL 은 문장 기록에 비밀번호가 평문으로 들어갈 수 있습니다[13]. 보고서에 로그를 옮길 때 가립니다.
- 시간대 약어는 겹칠 수 있습니다. plaso 의 PostgreSQL 플러그인은 `IST` 를 `Asia/Jerusalem` 으로 바꾸므로, 인도 표준시로 쓴 로그라면 변환 결과를 다시 봅니다[19].
- plaso 의 PostgreSQL 문법은 `사용자@데이터베이스` 를 영문자·숫자만으로 받습니다[19]. 이름에 `_`·`-` 가 있으면 그 줄을 제대로 읽지 못할 가능성이 있으므로 도구 결과와 원본 줄 수를 맞춰 봅니다.
- 설정은 운영 중에 바뀔 수 있습니다. 로그가 어느 날부터 나타나거나 사라졌다면 설정 파일의 변경 시각과 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md)의 관점으로 함께 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

MySQL 일반 쿼리 로그는 필드를 탭(`09`)으로 나누고 스레드 ID 를 공백으로 채웁니다[3]. 아래는 형식으로 만든 예시 줄의 앞부분입니다.

```
00000000: 3230 3236 2d30 332d 3132 5430 353a 3035  2026-03-12T05:05
00000010: 3a30 392e 3132 3334 3536 5a09 2020 2031  :09.123456Z.   1
00000020: 3220                                     2
```

`5a`(`Z`) 가 UTC 시각임을 뜻하고, 바로 뒤 `09` 가 첫 필드 구분자입니다. 그 뒤 `20 20 20 31 32 20` 은 다섯 자리로 맞춘 스레드 ID 12 와 공백입니다.

PostgreSQL 줄은 심각도 뒤에 공백이 두 칸입니다[14]. 아래도 형식으로 만든 예시입니다.

```
00000000: 3230 3236 2d30 332d 3132 2031 343a 3035  2026-03-12 14:05
00000010: 3a30 392e 3132 3320 4b53 5420 5b34 3332  :09.123 KST [432
00000020: 315d 2061 7070 7573 6572 4073 686f 7064  1] appuser@shopd
00000030: 6220 4c4f 473a 2020 636f 6e6e            b LOG:  conn
```

`4c 4f 47 3a 20 20` 이 `LOG:` 와 공백 두 칸입니다. 줄을 나눌 때 공백 한 칸을 기준으로 삼으면 메시지 앞에 빈 칸이 하나 남습니다.

### 공개 도구로 한 번

plaso 의 `postgresql` 텍스트 플러그인은 PostgreSQL 서버 로그를 읽어 시각·프로세스 ID·`사용자@데이터베이스`·심각도·메시지를 사건으로 만듭니다[19]. 시간대 약어가 `UTC` 가 아니면 현지 시각으로 표시하고 약어를 지역 이름으로 바꿔 둡니다[19]. dissect.target 의 명령 기록 플러그인은 사용자 홈의 `.mysql_history`, `.psql_history` 를 셸 기록과 함께 읽습니다[18]. MySQL 텍스트 로그는 `grep` 으로 `Access denied`, `ready for connections`, `Shutdown complete` 를 찾는 것부터 시작하면 됩니다.

## 교차 검증

- 웹 서버 로그의 요청 시각과 데이터베이스 로그의 오류 줄을 맞춰 보면, 웹 요청이 SQL 오류를 일으켰는지 추정할 수 있습니다. 웹 쪽 기록은 [웹 서버 로그](web-server-logs.md), 판단 흐름은 [웹 서버가 뚫렸나](../../04-scenarios/intrusion/web-compromise.md)에서 다룹니다.
- 로컬에서 `sudo -u postgres psql` 로 들어갔다면 [sudo·su 사용 기록](../logins/sudo-su.md)과 [인증 로그](../logins/auth-log.md)의 시각이 `.psql_history` 사용 시점과 맞는지 봅니다.
- 서버 시작·종료 시각은 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md)의 서비스 시작·정지 기록과 맞춰 봅니다.
- 여러 로그의 시각을 시간순으로 합치는 법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 실습

MySQL 이나 PostgreSQL 이 설치된 Linux 디스크 이미지(NIST CFReDS 등 공개 이미지)를 골라 다음 질문을 풀어 봅니다.

1. 이미지의 배포판을 확인하고, 이 페이지의 표에서 서버 설정 파일과 로그 경로를 찾습니다. 설정 파일의 로그 경로가 표와 다른가요?
2. MySQL 이라면 `log_timestamps`, `general_log`, `log_error_verbosity` 값은 무엇이고, 그 값으로 볼 때 오류 로그에 로그인 실패가 남을 수 있나요?
3. PostgreSQL 이라면 `log_timezone` 과 `log_line_prefix` 값은 무엇이고, 로그 첫 줄의 시각을 UTC 로 바꾸면 몇 시인가요?
4. 데이터 디렉터리에 `binlog.` 로 시작하는 파일이 있나요? 가장 오래된 파일의 첫 사건 시각은 언제이고, 30일 보관 기본값과 맞나요?
5. `.mysql_history` 나 `.psql_history` 가 있는 계정은 누구이고, 그 계정의 셸 기록과 겹치는 명령이 있나요?

## 참고 문헌

1. MySQL, `sql/sys_vars.cc` (8.0). https://github.com/mysql/mysql-server/blob/8.0/sql/sys_vars.cc
2. MySQL, `sql/mysqld.cc` (8.0). https://github.com/mysql/mysql-server/blob/8.0/sql/mysqld.cc
3. MySQL, `sql/log.cc` (8.0). https://github.com/mysql/mysql-server/blob/8.0/sql/log.cc
4. MySQL, `sql/server_component/log_sink_trad.cc` (8.0). https://github.com/mysql/mysql-server/blob/8.0/sql/server_component/log_sink_trad.cc
5. MySQL, `sql/server_component/log_builtins.cc` (8.0). https://github.com/mysql/mysql-server/blob/8.0/sql/server_component/log_builtins.cc
6. MySQL, `sql/auth/sql_authentication.cc` (8.0). https://github.com/mysql/mysql-server/blob/8.0/sql/auth/sql_authentication.cc
7. MySQL, `share/messages_to_error_log.txt` (8.0). https://github.com/mysql/mysql-server/blob/8.0/share/messages_to_error_log.txt
8. MySQL, `packaging/rpm-common/mysql.logrotate.in` (8.0). https://github.com/mysql/mysql-server/blob/8.0/packaging/rpm-common/mysql.logrotate.in
9. Ubuntu, mysql-8.0 패키지 (noble): `debian/additions/mysql.conf.d/mysqld.cnf`, `debian/mysql-server-8.0.mysql-server.logrotate`. https://git.launchpad.net/ubuntu/+source/mysql-8.0/tree/debian?h=ubuntu/noble
10. CentOS Stream 9, mysql 패키지: `mysql.spec`, `server.cnf.in`. https://gitlab.com/redhat/centos-stream/rpms/mysql/-/tree/c9s
11. CentOS Stream 9, mariadb 패키지: `mariadb.spec`. https://gitlab.com/redhat/centos-stream/rpms/mariadb/-/blob/c9s/mariadb.spec
12. PostgreSQL, `src/backend/utils/misc/postgresql.conf.sample` (REL_16_STABLE). https://github.com/postgres/postgres/blob/REL_16_STABLE/src/backend/utils/misc/postgresql.conf.sample
13. PostgreSQL, `doc/src/sgml/config.sgml` (REL_16_STABLE). https://github.com/postgres/postgres/blob/REL_16_STABLE/doc/src/sgml/config.sgml
14. PostgreSQL 소스 (REL_16_STABLE): `backend/utils/init/postinit.c`, `backend/postmaster/postmaster.c`, `backend/tcop/postgres.c`, `backend/libpq/auth.c`, `bin/initdb/initdb.c`, `backend/utils/error/elog.c`. https://github.com/postgres/postgres/tree/REL_16_STABLE/src
15. Ubuntu, postgresql-common 패키지 (noble): `pg_createcluster`, `createcluster.conf`, `debian/postgresql-common.logrotate`. https://git.launchpad.net/ubuntu/+source/postgresql-common/tree/?h=ubuntu/noble
16. CentOS Stream 9, postgresql 패키지: `postgresql.spec`, `postgresql-logging.patch`. https://gitlab.com/redhat/centos-stream/rpms/postgresql/-/tree/c9s
17. ForensicArtifacts, `artifacts/data/linux.yaml` (MySQLHistoryFile, PostgreSQLHistoryFile). https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
18. dissect.target, `dissect/target/plugins/os/unix/history.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/history.py
19. plaso, `plaso/parsers/text_plugins/postgresql.py`. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/postgresql.py
20. UAC, `artifacts/files/logs/var_log.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/files/logs/var_log.yaml
