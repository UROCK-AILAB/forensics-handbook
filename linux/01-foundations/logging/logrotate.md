---
title: "로그 순환"
parent: "기반 · 로그 체계"
nav_order: 240
---

# 로그 순환 (logrotate)

logrotate 는 정해진 주기나 크기에 따라 로그 파일의 이름을 바꾸고 압축하고 지우는 도구이고, 그 결과가 `/var/log` 의 회전본 이름과 상태 파일(state file)에 남습니다.

## 이 형식을 쓰는 아티팩트

rsyslog 가 쓰는 텍스트 로그는 대부분 logrotate 가 돌립니다. 인증 로그·시스템 로그·메일 로그·웹 서버 로그가 여기에 들고, wtmp·btmp 같은 이진 로그인 기록도 logrotate 설정으로 돌립니다[4][5]. 그래서 로그 한 종류를 모을 때는 지금 쓰고 있는 파일 하나가 아니라 회전본(`.1`, `.2.gz`, `-20260920` 같은 꼬리가 붙은 파일)까지 함께 모아야 기간이 이어집니다.

감사 로그와 systemd 저널은 logrotate 를 쓰지 않습니다. auditd 는 `audit.log.1`, `audit.log.2` 처럼 스스로 번호를 붙여 돌리고, journald 도 스스로 파일을 나누고 지웁니다. 두 형식의 회전 방식은 [감사 로그 형식](auditd-format.md)과 [systemd 저널](systemd-journal/index.md)에서 다룹니다.

logrotate 는 보통 하루에 한 번 cron 작업이나 systemd 타이머 `logrotate.timer` 로 실행됩니다[1]. logrotate 프로젝트가 예시로 싣는(upstream) 타이머는 `OnCalendar=daily`, `RandomizedDelaySec=1h`, `Persistent=true` 이고, 서비스는 `ExecStart=/usr/sbin/logrotate /etc/logrotate.conf` 한 줄로 설정 파일을 넘깁니다[4]. 예전 Red Hat 계열 패키지는 `/etc/cron.daily/logrotate` 로 돌렸고, 3.14.0-5 판부터 systemd 타이머로 바꿨습니다[5].

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| 전역 설정 | `/etc/logrotate.conf` (내용은 실제 시스템에서 확인) | `/etc/logrotate.conf`, upstream 예시 파일 그대로[5] |
| 패키지별 설정 | `/etc/logrotate.d/` | `/etc/logrotate.d/` (패키지가 `btmp`·`wtmp` 두 파일을 넣음)[5] |
| 상태 파일 | 실제 시스템에서 확인 (upstream 기본값은 `/var/lib/logrotate.status`)[3] | `/var/lib/logrotate/logrotate.status`, 권한 0640 root root[5] |
| 실행 방식 | 실제 시스템에서 확인 (타이머 또는 cron) | `logrotate.timer`·`logrotate.service`[5] |
| syslog 회전 대상 | `syslog`, `mail.log`, `kern.log`, `auth.log`, `user.log`, `cron.log`[7] | `cron`, `maillog`, `messages`, `secure`, `spooler`[6] |
| syslog 회전 설정 | `rotate 4`, `weekly`, `compress`, `delaycompress`, `notifempty`, `missingok`[7] | 주기·개수를 따로 적지 않아 전역 설정(`weekly`, `rotate 4`, `dateext`, 압축 없음)을 따름[4][5][6] |
| 회전본 이름 모양 | `auth.log.1`, `auth.log.2.gz` … (전역에 `dateext` 가 없을 때) | `secure-20260920` 처럼 날짜 꼬리, 압축 없음 (날짜는 만든 예시) |

Ubuntu 열의 syslog 회전 설정은 Ubuntu 24.04 rsyslog 패키지 소스의 `rsyslog.logrotate` 내용입니다[7]. 전역 설정에 `dateext` 가 켜져 있는지는 실제 시스템의 `/etc/logrotate.conf` 를 열어 확인합니다. 상태 파일 위치도 빌드할 때 정해지므로(`--with-state-file-path`)[3], 분석 대상의 `logrotate.service` 나 cron 스크립트에 `-s` 로 다른 경로를 넘기는지 먼저 봅니다[1]. rsyslog 가 어떤 로그를 어느 파일로 보내는지는 [syslog 형식과 rsyslog](syslog-rsyslog.md)에서 다룹니다.

## 구조

### 설정 파일

설정은 전역 지시어와 로그별 블록으로 나뉩니다. 로그별 블록은 경로(글로브 가능) 뒤에 중괄호를 열고 지시어를 적으며, 블록 안의 값이 전역 값을 덮어씁니다[1]. `include` 로 디렉터리를 주면 그 안의 파일을 알파벳 순서로 읽고, 이름이 `.dpkg-old`, `.rpmsave`, `.bak`, `~` 같은 금지 확장자(taboo extension)로 끝나는 파일은 건너뜁니다[1]. 전역 설정은 앞서 나온 `include` 에는 적용되지 않습니다[1][4].

증거 해석에 영향을 주는 지시어는 다음과 같습니다[1].

| 지시어 | 뜻 | 해석할 때 볼 점 |
|---|---|---|
| `rotate N` | 회전본을 N개까지 두고 넘치면 지움. 기본값 0 은 회전본을 남기지 않음 | 보관 기간의 상한 |
| `daily`·`weekly`·`monthly`·`yearly`·`hourly` | 회전 주기. `weekly` 는 요일 인자가 없으면 일요일(0) 기준 | 회전본 하나가 덮는 기간 |
| `size`·`minsize`·`maxsize` | 크기 기준. `size` 는 주기와 함께 쓰지 않음 | 크기 기준이면 회전본 기간이 들쭉날쭉함 |
| `maxage N` | N일보다 오래된 회전본을 지움. 회전이 일어날 때만 검사 | 회전이 멈추면 옛 파일이 남음 |
| `create mode owner group` | 회전 직후 같은 이름으로 빈 파일을 새로 만듦 | 지금 로그 파일이 회전 시각에 새로 생김 |
| `copytruncate` | 복사본을 만든 뒤 원본을 0으로 자름. 복사와 자르기 사이의 줄은 잃을 수 있음 | 원본 파일이 그대로 남아 계속 쓰임 |
| `copy` | 복사만 하고 원본은 건드리지 않음 | 같은 줄이 두 파일에 겹침 |
| `renamecopy` | 원본을 `.tmp` 를 붙인 이름으로 바꾼 뒤 복사하고 임시 파일을 지움 | |
| `compress`·`compresscmd`·`compressext` | 회전본 압축. 확장자는 gzip `.gz`, bzip2 `.bz2`, xz `.xz`, zstd `.zst`, compress `.Z`, zip `.zip` | 확장자로 압축 도구를 추정 |
| `delaycompress` | 바로 앞 회전본은 다음 주기까지 압축하지 않음 (`compress` 와 함께일 때만) | `.1` 만 평문, `.2` 부터 압축 |
| `dateext`·`dateformat`·`dateyesterday`·`datehourago` | 번호 대신 날짜 꼬리. 기본 형식은 `-%Y%m%d`, `hourly` 면 `-%Y%m%d%H` | 이름의 날짜가 뜻하는 날 |
| `olddir` | 회전본을 다른 디렉터리로 옮김 | 회전본이 `/var/log` 밖에 있을 수 있음 |
| `shred`·`shredcycles` | 지울 때 unlink 대신 `shred -u` 를 씀. 기본은 꺼짐 | 지운 회전본을 되살리기 어려움 |
| `prerotate`·`postrotate`·`firstaction`·`lastaction`·`preremove` | 회전 앞뒤에 `/bin/sh` 로 실행하는 스크립트 | 설정 파일 안에 명령이 들어 있음 |
| `missingok`·`notifempty` | 파일이 없어도 오류를 내지 않음, 빈 파일은 돌리지 않음 (기본은 `ifempty`) | |

### 회전본 이름

번호 방식에서는 회전할 때마다 기존 회전본의 번호를 하나씩 올리고, 지금 파일을 `.1` 로 이름을 바꿉니다[2]. 그래서 번호가 작을수록 새 파일이고, `start` 로 첫 번호를 바꿀 수 있습니다[1][2]. `extension` 이나 `addextension` 을 쓰면 번호가 확장자 앞에 들어가 `mylog.1.foo.gz` 같은 모양이 됩니다[1].

날짜 방식(`dateext`)에서는 `auth.log-20260920` 처럼 회전한 날의 날짜가 붙습니다[1]. `dateyesterday` 를 켜면 전날 날짜를, `datehourago` 를 켜면 한 시간 전 시각을 붙여 파일 안의 줄과 날짜를 맞춥니다[1]. 오래된 파일을 고를 때 logrotate 는 이름을 사전 순으로 정렬하므로, `dateformat` 은 연·월·일 순서로 정렬되는 형식만 써야 합니다[1].

| 설정 | 회전 세 번 뒤 모양 (만든 예시) |
|---|---|
| 번호, 압축 없음 | `auth.log`, `auth.log.1`, `auth.log.2`, `auth.log.3` |
| 번호, `compress` + `delaycompress` | `auth.log`, `auth.log.1`, `auth.log.2.gz`, `auth.log.3.gz` |
| `dateext`, 압축 없음 | `secure`, `secure-20260906`, `secure-20260913`, `secure-20260920` |
| `dateext` + `compress` | `secure`, `secure-20260906.gz`, `secure-20260913.gz`, `secure-20260920.gz` |

### 상태 파일

상태 파일은 로그 경로마다 마지막으로 회전한 시각을 적는 평문 파일입니다[2]. 첫 줄은 `logrotate state -- version 2` 이고, 이어지는 줄마다 큰따옴표로 감싼 경로와 공백, 시각이 옵니다[2]. 경로 안의 `"` 와 `\` 앞에는 `\` 를 붙이고, 줄바꿈은 `\n` 두 글자로 적습니다[2].

| 부분 | 형식 | 뜻 |
|---|---|---|
| 머리 줄 | `logrotate state -- version 2` | 읽을 때는 `version 1` 도 받음 |
| 경로 | `"/var/log/auth.log"` | 설정에서 글로브를 푼 실제 경로 |
| 시각 | `%d-%d-%d-%d:%d:%d` → 연-월-일-시:분:초 | 앞자리 0을 채우지 않음. 시스템 현지 시각이고 시간대 표시는 없음 |

시각은 `localtime_r` 로 만든 현지 시각이라서, 상태 파일만으로는 UTC 로 바꿀 수 없고 분석 대상의 시간대 설정이 필요합니다[2]. 읽을 때는 연도가 1970~2100 밖이거나(1900 은 예외로 받음) 월·일·시·분이 범위를 벗어나면 그 줄을 잘못된 줄로 보고 읽기를 멈춥니다[2].

처음 보는 로그는 실행한 그 시각을 마지막 회전 시각으로 적습니다[1]. 이때 코드는 연·월·일·시만 채우고 분과 초는 0으로 둡니다[2]. 실제로 회전하면 분과 초까지 그대로 적습니다[2]. 그래서 `2026-9-20-6:0:0` 처럼 분·초가 0인 줄은 "그 시각에 처음 설정에 잡혔고 아직 회전하지 않은 로그" 일 가능성이 있습니다(만든 예시).

로그 파일이 없어져도 상태 파일의 줄은 바로 지워지지 않습니다. 그 실행에서 다루지 않은 로그(파일이 없거나 설정에서 빠진 로그)의 줄은 마지막 회전 뒤 1년(31,556,926초)이 지나야 빠집니다[2]. 따라서 지금은 없는 로그 경로가 상태 파일에 남아 있을 수 있습니다.

logrotate 는 실행할 때마다(`-d` 디버그 실행 제외) 상태 파일 전체를 `logrotate.status.tmp` 처럼 `.tmp` 를 붙인 임시 파일에 새로 쓰고, fsync 한 뒤 원래 이름으로 바꿔 넣습니다[2]. 아무 로그도 돌리지 않은 실행이어도 상태 파일은 다시 쓰입니다[2]. `-s /dev/null` 로 실행하면 상태 파일을 잠그지도 쓰지도 않습니다[1][2].

## 읽는 법

### 헥스로 한 번

아래는 명세대로 만든 상태 파일 앞부분입니다(만든 예시). 머리 줄 28바이트 뒤에 `0a` 줄바꿈이 오고, 이어서 `22`(`"`)로 경로가 시작합니다. 날짜의 월 `9` 와 초 `3` 이 한 자리로 적힌 것이 보입니다.

```
00000000: 6c6f 6772 6f74 6174 6520 7374 6174 6520  logrotate state 
00000010: 2d2d 2076 6572 7369 6f6e 2032 0a22 2f76  -- version 2."/v
00000020: 6172 2f6c 6f67 2f61 7574 682e 6c6f 6722  ar/log/auth.log"
00000030: 2032 3032 362d 392d 3230 2d36 3a32 353a   2026-9-20-6:25:
00000040: 330a                                     3.
```

### 순서대로 한 번

1. 실행 방식과 상태 파일 경로를 찾습니다. `logrotate.service`·`logrotate.timer` 와 cron 디렉터리를 보고, `-s` 인자가 있으면 그 경로를 씁니다([systemd 서비스와 타이머](../../02-artifacts/persistence/systemd-units.md), [cron·anacron·at](../../02-artifacts/persistence/cron-at.md)).
2. `/etc/logrotate.conf` 와 `/etc/logrotate.d/` 의 파일을 읽어 로그마다 주기·개수·압축·이름 방식을 정리합니다. 블록 안 값이 전역 값을 덮어쓰고, 전역 설정은 그보다 앞서 나온 `include` 에 적용되지 않는다는 점을 함께 따집니다[1].
3. 상태 파일에서 로그마다 마지막 회전 시각을 읽고, 분석 대상의 시간대로 UTC 로 바꿉니다([호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md)).
4. 설정대로라면 있어야 할 회전본 목록(예: `rotate 4` + `weekly` 면 약 4주치)을 만들고 실제 파일과 맞춰 봅니다.
5. 압축본은 풀어서 읽되, 원본 이미지 안의 파일은 건드리지 않고 사본으로 작업합니다.

라이브 시스템에서는 `logrotate -d /etc/logrotate.conf` 로 지금 설정이 무엇을 돌릴지 볼 수 있습니다. 디버그 모드는 로그를 바꾸지 않고 상태 파일도 고치지 않습니다[1].

## 포렌식에서 중요한 점

### 증명하는 것

- 상태 파일의 줄은 logrotate 가 그 경로를 마지막으로 돌린 현지 시각을 보여 줍니다[2].
- 상태 파일에만 있고 디스크에는 없는 로그 경로는 1년 안에 그 로그가 설정에 잡혀 있었다는 흔적입니다[2].
- 설정 파일과 상태 파일을 합치면 어떤 회전본이 있어야 하는지 계산할 수 있고, 모자란 회전본이 정상적인 개수·기간 초과 때문에 지워졌는지 추정할 수 있습니다.
- 상태 파일의 mtime 은 마지막으로 logrotate 를 (디버그가 아닌 모드로) 실행한 때와 가깝습니다. 실행할 때마다 새로 쓰고 바꿔 넣기 때문입니다[2].

### 증명하지 못하는 것

- 회전본이 없다는 사실만으로는 사람이 지웠는지 정상 회전으로 지워졌는지 가를 수 없습니다. `rotate`, `maxage` 설정과 상태 파일의 시각을 맞춰 봐야 합니다[1].
- 상태 파일은 경로마다 마지막 회전 한 번만 적고 이력은 남기지 않습니다[2].
- 상태 파일은 평문이고 서명이 없어서, 누가 고쳐 썼는지는 이 파일로 알 수 없습니다.
- `copytruncate` 를 쓰는 로그는 복사와 자르기 사이의 줄을 잃을 수 있으므로, 회전 시각 근처의 빈 구간이 곧 지운 흔적은 아닙니다[1].

### 시각 해석

| 시각 | 무엇이 바뀔 때 바뀌나 | 기준 |
|---|---|---|
| 상태 파일 안의 시각 | 그 로그를 실제로 돌렸을 때, 또는 처음 설정에 잡혔을 때(분·초 0) | 현지 시각, 시간대 표시 없음[2] |
| 상태 파일의 mtime | 디버그가 아닌 logrotate 실행마다 | 파일 시스템 시각([Linux 의 시각 값](../value-decoding/time-values.md)) |
| 이름을 바꾼 회전본(`.1`, 날짜 꼬리)의 mtime | 회전 전 마지막으로 쓴 때. 이름만 바꾸므로 내용과 아이노드가 그대로입니다[2] | 파일 시스템 시각 |
| 압축본(`.gz` 등)의 mtime | 압축한 뒤 원래 파일의 atime·mtime 을 그대로 옮겨 적음[2] | 파일 시스템 시각 |
| `create` 로 새로 만든 지금 로그 파일의 생성 시각 | 회전 직후 새 파일을 만들 때[1] | 파일 시스템 시각 |
| `dateext` 이름의 날짜 | 회전한 날. `dateyesterday` 면 전날[1] | 현지 날짜 |

`dateext` 이름의 날짜는 파일이 덮는 기간이 아니라 회전한 날입니다. `weekly` 설정의 `secure-20260920` 은 9월 20일 회전 시각 직전까지 약 한 주 동안의 줄을 담고, 날짜는 그 기간의 마지막 날입니다(만든 예시). 상태 파일의 시각이 지금보다 25시간 넘게 미래이면 logrotate 는 `log %s last rotated in the future -- rotation forced` 오류를 내고 강제로 돌립니다[2]. 시계를 앞으로 돌렸다가 되돌린 흔적을 찾을 때 이 오류가 단서가 될 수 있고, systemd 서비스로 돌았다면 분석 대상의 저널에서 `logrotate.service` 단위의 메시지를 찾아봅니다([시각을 조작했나](../../04-scenarios/insider/time-manipulation.md)).

전통 syslog 형식은 줄에 연도가 없어서 도구가 파일의 mtime 으로 연도를 추정합니다. dissect.target 은 파일 mtime 을 시간대에 맞춰 바꾼 연도를 마지막 줄의 연도로 보고 거꾸로 읽어 가며 연도를 넘기고, 압축본도 풀어서 같은 방식으로 읽습니다[8]. 압축본은 원래 파일의 mtime 을 이어받으므로 이 추정이 맞아떨어지지만, 수집할 때 mtime 을 보존하지 않은 사본이면 연도가 틀어질 수 있습니다.

### 지운 데이터·손상

압축할 때 logrotate 는 압축본을 다 쓴 뒤 원래 평문 파일을 지웁니다[2]. `shred` 가 꺼져 있으면 unlink 만 하므로, 평문 회전본의 내용이 할당되지 않은 공간에 남아 있을 가능성이 있습니다([지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md)). `shred` 가 켜져 있으면 `shred -u` 로 덮어쓴 뒤 지우므로 되살리기 어렵습니다[1][2].

상태 파일은 임시 파일에 다 쓴 뒤 이름을 바꿔 넣으므로, 쓰는 도중 멈춰도 원래 파일은 그대로 남고 `.tmp` 파일만 남을 수 있습니다[2]. 다음 실행은 남은 `.tmp` 파일부터 지웁니다[2].

## 함정

- 파일 이름에 `*` 를 쓴 설정은 이미 돌린 회전본까지 다시 돌립니다[1]. 꼬리가 겹친 이상한 이름의 회전본은 설정 실수에서 나왔을 가능성이 있으니, 조작으로 보기 전에 설정의 글로브부터 확인합니다.
- `notifempty` 로그는 비어 있으면 돌지 않고, `minsize` 로그는 크기가 차지 않으면 주기가 지나도 돌지 않습니다[1]. upstream 예시의 wtmp 설정은 `monthly` 에 `minsize 1M` 이 붙어 있어 로그인이 적은 서버에서는 몇 달씩 돌지 않을 수 있습니다[4]. wtmp 형식은 [로그인 기록 파일 형식](utmp-wtmp-format.md)에서 다룹니다.
- `maxage` 는 회전이 일어날 때만 검사하므로, 회전이 멈춘 로그의 옛 회전본은 기간이 지나도 남습니다[1].
- 로그가 심볼릭 링크이면 돌리지 않고 건너뛰고, 하드 링크가 둘 이상이면 `allowhardlink` 가 없는 한 건너뜁니다[2]. 로그 경로가 링크로 바뀌어 회전이 멈췄다면 그 자체가 조사할 거리입니다.
- 설정의 `postrotate` 등 스크립트 블록은 `su` 지시어와 상관없이 logrotate 를 실행한 사용자(보통 root) 권한으로 도는 셸 명령입니다[1]. `/etc/logrotate.d/` 에 낯선 파일이나 낯선 스크립트 줄이 있으면 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md)의 관점으로 봅니다.
- 회전 설정이 주석으로만 들어 있는 패키지도 있습니다. MySQL 이 RPM 용으로 싣는 회전 설정은 블록 전체가 주석이라, 주석을 풀기 전에는 오류 로그가 돌지 않고 계속 커집니다[12]. 서버 로그별 기본 설정은 [웹 서버 로그](../../02-artifacts/servers/web-server-logs.md)와 [데이터베이스 서버 로그](../../02-artifacts/servers/database-logs.md)에서 다룹니다.
- upstream 예시 cron 스크립트는 logrotate 가 0이 아닌 값으로 끝나면 `logger -t logrotate "ALERT exited abnormally with [$EXITVALUE]"` 로 syslog 에 한 줄을 남깁니다[4]. cron 으로 도는 시스템에서는 이 줄로 실패한 날을 찾을 수 있습니다.

## 도구

- 분석 대상의 로그를 모을 때: ForensicArtifacts 정의는 `/var/log/auth*`, `/var/log/secure*`, `/var/log/messages*`, `/var/log/syslog*` 처럼 끝에 `*` 를 붙여 회전본까지 잡고[10], UAC 는 `/var/log` 전체를 모읍니다[11]. 상태 파일과 `/etc/logrotate.conf`, `/etc/logrotate.d/` 는 따로 모읍니다.
- dissect.target 의 인증 로그·syslog 플러그인은 `auth.log*`·`secure*`, `syslog*`·`messages*` 를 찾아 압축본까지 읽습니다[8][9].
- 상태 파일과 설정 파일은 평문이라 텍스트 편집기나 `grep` 으로 읽습니다. 압축본은 사본을 만든 뒤 `zcat` 같은 압축 해제 도구로 엽니다.
- 여러 회전본을 한 타임라인으로 합치는 방법은 [로그 분석](../../03-techniques/analysis/log-analysis.md)과 [타임라인 만들기](../../03-techniques/analysis/timeline.md)에서 다룹니다. 인증 로그를 읽는 방법은 [인증 로그](../../02-artifacts/logins/auth-log.md), 로그를 지운 흔적을 찾는 순서는 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md)에 있습니다.

## 참고 문헌

1. logrotate, logrotate(8). https://github.com/logrotate/logrotate/blob/main/logrotate.8.in
2. logrotate, `logrotate.c`. https://github.com/logrotate/logrotate/blob/main/logrotate.c
3. logrotate, `configure.ac`. https://github.com/logrotate/logrotate/blob/main/configure.ac
4. logrotate, `examples/logrotate.conf`·`logrotate.service`·`logrotate.timer`·`logrotate.cron`·`wtmp`·`btmp`. https://github.com/logrotate/logrotate/tree/main/examples
5. CentOS Stream 9 logrotate 패키지, `logrotate.spec`. https://gitlab.com/redhat/centos-stream/rpms/logrotate/-/blob/c9s/logrotate.spec
6. CentOS Stream 9 rsyslog 패키지, `rsyslog.log`. https://gitlab.com/redhat/centos-stream/rpms/rsyslog/-/blob/c9s/rsyslog.log
7. Ubuntu 24.04(noble) rsyslog 패키지, `debian/rsyslog.logrotate`. https://git.launchpad.net/ubuntu/+source/rsyslog/tree/debian?h=ubuntu/noble-updates
8. dissect.target, `helpers/utils.py`(`year_rollover_helper`)·`plugins/os/unix/log/messages.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/helpers/utils.py
9. dissect.target, `plugins/os/unix/log/auth.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/auth.py
10. ForensicArtifacts, `artifacts/data/linux.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
11. UAC, `artifacts/files/logs/var_log.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/files/logs/var_log.yaml
12. MySQL, `packaging/rpm-common/mysql.logrotate.in`. https://github.com/mysql/mysql-server/blob/8.0/packaging/rpm-common/mysql.logrotate.in
