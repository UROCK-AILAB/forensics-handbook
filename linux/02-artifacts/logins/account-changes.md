---
title: "계정 생성·변경 흔적"
parent: "아티팩트 · 로그인과 계정"
nav_order: 410
---

# 계정 생성·변경 흔적 (useradd·usermod)

`useradd`·`usermod`·`userdel` 같은 shadow 도구는 계정을 만들고 고칠 때마다 인증 로그에 한 줄씩 남기고, 계정 파일의 백업·마지막 비밀번호 변경일·lastlog 칸 같은 곳에도 흔적을 남깁니다.

## 무엇을 기록하나 · 왜 생기나

shadow 도구 모음(shadow-utils)은 syslog 를 `LOG_AUTHPRIV` 분야(facility)와 `LOG_PID` 옵션으로 엽니다[1]. 그래서 줄은 인증 로그로 가고, 태그에는 `useradd[5120]` 처럼 PID 가 붙습니다. RHEL 9 가 쓰는 4.9 판도 같은 값이고, 로그 문구도 4.9 판과 최신 판이 같습니다[4].

useradd 는 도중에 문제가 생겨도 무엇을 하려 했는지 남도록, 계정 파일을 고치기 전에 먼저 `new user:` 줄을 남깁니다[2]. 그래서 이 줄은 "계정을 만들었다" 가 아니라 "만들려고 했다" 를 뜻하고, 실패하면 뒤에 `failed adding user` 줄이 붙습니다[2][4].

계정 파일(`/etc/passwd`·`/etc/shadow`·`/etc/group`·`/etc/gshadow`) 자체의 구조와 백업 파일이 생기는 순서는 [계정 파일 (passwd·shadow·group)](../../01-foundations/users-auth/passwd-shadow-group.md)에서 다룹니다. 이 쪽은 도구가 남기는 로그 줄과, 계정을 만들고 고칠 때 덩달아 바뀌는 곳을 다룹니다.

## 위치와 버전별 차이

| 항목 | Ubuntu 24.04 LTS | RHEL 9 계열 |
|---|---|---|
| shadow 도구 줄이 가는 파일 | `/var/log/auth.log`(`auth,authpriv.*`)[5] | `/var/log/secure`(`authpriv.*`)[6] |
| 계정 추가에 흔히 쓰는 명령 | `adduser`(펄 스크립트)가 `useradd` 를 부름[7] | `useradd`. `adduser` 는 `useradd` 를 가리키는 심볼릭 링크[8] |
| adduser 자신의 로그 | `logger` 로 `user` 분야에 보냄 → `/var/log/syslog`[7][5] | 해당 없음(useradd 가 남김) |
| shadow 도구 패키지 | `passwd`(소스 패키지 이름은 shadow), `passwd` 명령 포함[9] | `shadow-utils` 4.9. `--with-audit`, `--without-libpam` 로 빌드하고 `passwd` 명령은 지움[8] |
| 저널 | 모든 줄이 함께 들어감 | 같음. rsyslog 는 저널에서 가져옴(imjournal)[6] |

Ubuntu 에서 `adduser` 로 계정을 하나 만들면, adduser 자신의 줄은 `/var/log/syslog` 에, adduser 가 부른 useradd 의 `new user:` 줄은 `/var/log/auth.log` 에 나뉘어 남습니다[5][7]. 두 파일을 시각으로 맞춰 읽으면 됩니다. 두 배포판의 rsyslog 규칙과 줄 서식 차이는 [인증 로그 (auth.log·secure)](auth-log.md)에서 다룹니다.

RHEL 9 의 `passwd` 명령은 shadow-utils 가 아닌 다른 패키지에서 오므로[8], 비밀번호 변경 줄의 모양은 검체에서 `rpm -qf /usr/bin/passwd` 로 패키지를 확인한 뒤 실제 줄로 봅니다.

계정 생성 기본값도 배포판마다 다릅니다.

| 키 | Ubuntu 24.04 [9] | RHEL 9 [8] |
|---|---|---|
| `UID_MIN` / `UID_MAX` | 1000 / 60000 | 1000 / 60000 |
| `SYS_UID_MIN` / `SYS_UID_MAX` | 파일에 없음 → shadow 기본값 101 / `UID_MIN`-1[10] | 201 / 999 |
| `CREATE_HOME` | 없음 | `yes` |
| `HOME_MODE` | 0750 | 0700 |
| `USERGROUPS_ENAB` | `yes` | `yes` |
| `/etc/default/useradd` | `SHELL=/bin/sh` | `GROUP=100`, `HOME=/home`, `INACTIVE=-1`, `SHELL=/bin/bash`, `SKEL=/etc/skel`, `CREATE_MAIL_SPOOL=yes` |

`CREATE_HOME` 이 켜져 있지 않으면 `-m` 없이 부른 useradd 는 홈 폴더를 만들지 않습니다[10]. 그래서 Ubuntu 에서 useradd 를 직접 썼다면 홈 폴더가 없을 가능성이 있고, adduser 는 홈 폴더를 스스로 만들고 skel 을 복사합니다[7]. UID 범위로 사람 계정과 시스템 계정을 가르는 방법은 [UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md)에서 다룹니다. RHEL 의 시스템 UID 가 201 부터 시작하는 점은 Ubuntu 와 다릅니다.

## 구조

### 로그 줄

아래 서식은 프로그램이 쓰는 문자열 그대로이고, `%s`·`%u`·`%d` 자리에 값이 들어갑니다.

| 명령 | 줄 서식 | 뜻 |
|---|---|---|
| useradd | `new user: name=%s, UID=%u, GID=%u, home=%s, shell=%s, from=%s` | 계정을 만들려 함. `from` 은 표준 입력의 터미널 이름, 없으면 `none`[2] |
| useradd | `new group: name=%s, GID=%u` | 사용자 이름과 같은 그룹을 만듦[2] |
| useradd | `add '%s' to group '%s'`, `add '%s' to shadow group '%s'` | 보조 그룹에 넣음[2] |
| useradd | `failed adding user '%s', exit code: %d` | 만들기 실패[2] |
| usermod | `lock user '%s' password`, `unlock user '%s' password`, `change user '%s' password` | 비밀번호 잠금·풂·교체[3] |
| usermod | `change user name '%s' to '%s'` | 이름 바꿈[3] |
| usermod | `change user '%s' UID from '%d' to '%d'`, `… GID from '%d' to '%d'` | 번호 바꿈[3] |
| usermod | `change user '%s' home from '%s' to '%s'`, `… shell from '%s' to '%s'` | 홈·셸 바꿈[3] |
| usermod | `change user '%s' inactive from '%ld' to '%ld'`, `… expiration from '%s' to '%s'` | 비활성 기간·만료일 바꿈[3] |
| usermod | `add '%s' to group '%s'`, `delete '%s' from group '%s'` (shadow group 판도 있음) | 그룹 넣고 뺌[3] |
| userdel | `delete user '%s'`, `delete '%s' from group '%s'`, `removed group '%s' owned by '%s'` | 계정·그룹 지움[3] |
| groupadd | `group added to %s: name=%s, GID=%u`, `new group: name=%s, GID=%u` | 그룹 만듦[3] |
| groupmod | `group changed in %s (%s)` | 그룹 고침[3] |
| gpasswd | `user %s added by %s to group %s%s`, `user %s removed by %s from group %s%s`, `members of group %s set by %s to %s%s` | 그룹 구성원을 바꿈. 두 번째 `%s` 가 명령을 친 사용자[3] |
| chage | `changed password expiry for %s` | 비밀번호 나이 정보 바꿈[3] |
| passwd (shadow) | `password for '%s' changed by '%s'` | 비밀번호 바꿈[3] |

shadow 의 `passwd` 를 PAM 으로 빌드했다면 `-l`·`-e` 같은 선택 사항이 없는 일반 비밀번호 변경은 PAM 에 맡기고 곧바로 끝나므로, 위 줄 대신 `pam_unix(passwd:chauthtok): password changed for 이름` 이 남습니다[3][11]. `passwd` 가 남기는 `password locked for '%s'` 는 root 가 아닌 사용자가 잠겼거나(비밀번호 칸이 `!` 로 시작) 만료된 계정의 비밀번호를 바꾸려다 거절당했다는 뜻이고, 잠금을 건 기록이 아닙니다[3].

Ubuntu 24.04 의 auth.log 에서 useradd 줄은 이런 모양입니다(만든 예시).

```
2025-03-04T10:20:33.000001+09:00 web01 useradd[5120]: new user: name=svcbackup, UID=1002, GID=1002, home=/home/svcbackup, shell=/bin/bash, from=/dev/pts/1
```

`from=` 에는 `ttyname()` 이 돌려준 전체 경로가 들어가므로 `/dev/pts/1` 모양이 됩니다[2]. 스크립트나 cron 처럼 터미널 없이 실행하면 `from=none` 입니다[2].

### 감사 로그

shadow 도구를 감사(audit) 지원으로 빌드하면 syslog 줄과 따로 감사 레코드도 남깁니다. useradd 는 `ADD_USER`·`ADD_GROUP`, userdel 은 `DEL_USER`·`DEL_GROUP`, usermod 는 주로 `USER_MGMT` 와 `GRP_MGMT` 를 쓰고, 비밀번호를 잠그거나 풀거나 바꿀 때(`-L`·`-U`·`-p`)는 `USER_CHAUTHTOK` 을 씁니다[2][3].

| 레코드 종류 | 번호 | 뜻[12] |
|---|---|---|
| `USER_MGMT` | 1102 | 계정 속성 바뀜 |
| `USER_CHAUTHTOK` | 1108 | 비밀번호 바뀜 |
| `ADD_USER` / `DEL_USER` | 1114 / 1115 | 계정 추가 / 삭제 |
| `ADD_GROUP` / `DEL_GROUP` | 1116 / 1117 | 그룹 추가 / 삭제 |
| `GRP_MGMT` | 1132 | 그룹 속성 바뀜 |

RHEL 9 의 shadow-utils 는 `--with-audit` 로 빌드하고 감사 문구를 바꾸는 패치(`shadow-4.9-audit-update.patch`)를 덧댑니다[8]. 그래서 레코드 안의 `op` 문구는 최신 shadow 코드와 다를 수 있으니 검체의 `audit.log` 로 확인합니다. 레코드 필드를 읽는 법은 [감사 로그 형식 (auditd)](../../01-foundations/logging/auditd-format.md)에서 다룹니다.

### 계정을 만들 때 함께 바뀌는 곳

| 곳 | 바뀌는 내용 |
|---|---|
| `/etc/passwd`·`/etc/shadow`·`/etc/group`·`/etc/gshadow` | 새 내용을 임시 파일에 쓴 뒤 이름을 바꿔 덮고, 직전 판을 `파일이름-` 로 남김. 자세한 순서는 [계정 파일](../../01-foundations/users-auth/passwd-shadow-group.md) |
| shadow 3번째 칸(마지막 비밀번호 변경일) | useradd 가 그 순간의 epoch 초를 하루(86400초)로 나눈 값으로 채움. 결과가 0 이면 -1[2] |
| `/var/log/lastlog`·`/var/log/faillog` | 새 UID 의 칸을 0으로 지움(아래 설명)[2] |
| 홈 폴더 | `-m` 이거나 `CREATE_HOME` 이 켜져 있으면 만들고 skel 폴더의 파일을 복사. `-r`(시스템 계정)은 `-m` 없이는 만들지 않음[10] |
| `/etc/subuid`·`/etc/subgid` | 하위 번호 범위를 추가. `-r` 이면 `-F` 없이는 추가하지 않음[10] |
| `/etc/shadow-maint/useradd-pre.d/*`, `useradd-post.d/*` | 최신 shadow 에서 계정 추가 전후에 실행하는 스크립트[10] |

lastlog 를 지우는 조건은 셋입니다. `-l`(`--no-log-init`)을 주지 않았고, `/etc/default/useradd` 의 `LOG_INIT` 가 `no` 가 아니고(이 키는 4.13 판에는 있고 RHEL 9 의 4.9 판에는 없습니다[4]), 그 UID 를 쓰는 계정이 아직 없어야 합니다[2][10]. 목적은 예전에 지운 계정이 같은 UID 로 남긴 기록을 새 계정이 물려받지 않게 하는 것입니다[10]. useradd 는 `sizeof(struct lastlog) × UID` 오프셋에 빈 레코드를 덮어씁니다[2]. 4.13 판(Ubuntu 24.04)과 최신 판은 파일 크기가 그 오프셋 이하이면 아무것도 하지 않고, RHEL 9 의 4.9 판은 크기를 보지 않고 그 오프셋에 씁니다[2][4].

## 증거로서 의미

### 증명하는 것

- `new user:` 줄은 그 시각에 useradd 가 그 이름·UID·GID·홈·셸로 계정을 만들려 했다는 기록입니다[2]. `from=` 은 명령을 실행한 터미널입니다.
- usermod·userdel·gpasswd 줄은 그 시각에 그 도구가 그 항목을 바꾸려 했다는 기록입니다. gpasswd 줄에는 명령을 친 사용자 이름도 들어 있습니다[3].
- 감사 레코드가 있으면 `auid`(로그인할 때 정해진 사용자 번호)로 어느 로그인 세션에서 실행했는지 이을 수 있습니다[12].
- shadow 3번째 칸은 useradd 로 만든 뒤 비밀번호를 바꾸거나 `chage -d` 로 고치지 않은 계정이라면 계정을 만든 날(UTC)과 같습니다[2].

보고서에는 "2025-03-04 10:20:33(UTC+9)에 useradd 가 /dev/pts/1 에서 svcbackup(UID 1002) 계정 생성을 기록했다" 처럼 기록이 말하는 만큼 씁니다(값은 만든 예시).

### 증명하지 못하는 것

- `new user:` 줄에는 실행한 사용자가 없습니다[2]. 같은 시각의 sudo 줄([sudo·su 사용 기록](sudo-su.md))이나 감사 `auid` 로 따로 잇습니다.
- 줄이 있다고 계정이 만들어졌다고 단정하지 못합니다. 쓰기 전에 남기는 줄이라[2], `failed adding user` 줄과 현재 `/etc/passwd` 를 함께 봅니다.
- 줄이 없다고 계정 변경이 없었다고 하지 못합니다. 편집기나 `vipw`, 스크립트로 `/etc/passwd` 를 직접 고치면 shadow 도구 코드를 거치지 않으므로 이 줄들이 생기지 않습니다. 이럴 때 남는 모양은 [계정 파일](../../01-foundations/users-auth/passwd-shadow-group.md)의 "지운 계정과 조작 흔적" 에서 다룹니다.
- 로컬 사용자도 `logger` 로 아무 태그와 분야를 붙인 줄을 쓸 수 있으므로, 태그가 `useradd` 라는 사실만으로 진짜 useradd 가 썼다고 할 수는 없습니다. 저널의 `_COMM`·`_EXE` 같은 신뢰 필드와 맞춰 봅니다([systemd 저널](../../01-foundations/logging/systemd-journal/index.md)).

## 시각 해석

| 값 | 언제 바뀌나 | 기준 |
|---|---|---|
| auth.log 줄 시각(Ubuntu 24.04) | 줄을 쓸 때 | RFC 3339, UTC 오프셋 포함([syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)) |
| secure 줄 시각(RHEL 9) | 줄을 쓸 때 | 전통 서식, 연도·시간대 없는 현지 시각[6] |
| 감사 레코드 `msg=audit(초.밀리초:번호)` | 레코드를 만들 때 | epoch, UTC([감사 로그 형식](../../01-foundations/logging/auditd-format.md)) |
| shadow 3번째 칸 | useradd, 비밀번호 변경, `chage -d` | 1970-01-01 UTC 부터 센 일수[10][19] |
| `/etc/passwd-` 의 mtime | 백업을 만들 때 원본의 mtime 을 옮겨 붙임[1] | 직전 변경 시각 |
| 홈 폴더·skel 복사본의 아이노드 시각 | 홈을 만들 때 | 파일 시스템 시각 |

전통 서식 줄의 연도를 가늠하는 방법은 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)에서, shadow 일수를 날짜로 바꾸는 계산은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다. shadow 칸은 날짜 경계가 UTC 자정이라, UTC+9 에서 오전 9시 전에 만든 계정은 현지 날짜보다 하루 이른 날로 기록됩니다.

useradd 는 이 날짜를 시계 대신 환경 변수 `SOURCE_DATE_EPOCH` 에서 가져오기도 합니다. 이 변수는 현재 시각 이하의 값만 받으므로, 변수를 준 채 실행하면 shadow 칸의 날짜가 실제보다 이르게 기록될 수 있습니다[1][4]. shadow 칸 날짜가 로그 줄 시각보다 이르면 이 가능성을 봅니다.

## 함정과 한계

- **UID 재사용이 lastlog 를 지운다**: 지운 계정과 같은 UID 로 새 계정을 만들면, 옛 계정의 마지막 로그인 기록이 lastlog 에서 0 으로 덮입니다[2]. 이 기록은 useradd 전에 확보한 사본이나 wtmp 에서 찾습니다([로그인 기록 (wtmp·btmp·lastlog)](wtmp-btmp-lastlog.md)).
- **Ubuntu 는 두 파일에 나뉜다**: adduser 줄은 syslog, useradd 줄은 auth.log 에 있습니다[5][7].
- **`password locked for` 는 잠금이 아니다**: 잠겼거나 만료된 계정의 비밀번호 변경을 거절했다는 뜻입니다[3]. 잠금을 건 기록은 `lock user '%s' password`(usermod)입니다.
- **수집 도구의 빈틈**: UAC 는 `/etc` 를 모을 때 `shadow`·`shadow-`·`gshadow`·`gshadow-` 를 뺍니다[17]. ForensicArtifacts 의 백업 정의는 `/etc/shadow-` 하나뿐입니다[18]. Velociraptor `Linux.Sys.Users` 는 `/etc/passwd` 만 읽습니다[16]. 계정 파일과 백업은 따로 모읍니다.
- **dissect.target `passwords` 가 건너뛰는 계정**: `$` 로 나뉜 해시가 없는 줄(`!`·`*`·빈칸 등)은 레코드를 내지 않아[15], 비밀번호 없이 만든 계정의 마지막 변경일이 결과에서 빠집니다. adduser 가 비밀번호 없이 만든 계정은 비밀번호 칸이 `!` 입니다[7].
- **로그 순환**: 오래된 계정 생성 줄은 `auth.log.2.gz`, `secure-YYYYMMDD` 같은 순환본에 있습니다([로그 순환 (logrotate)](../../01-foundations/logging/logrotate.md)).

## 직접 분석해 보기

### 헥스로 한 번 — lastlog 칸이 지워졌는지

lastlog 레코드는 UID 번째 칸에 292바이트씩 놓입니다([로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md)). UID 1002 의 칸은 292 × 1002 = 292584(0x476E8) 바이트에서 시작합니다.

```
$ xxd -s 292584 -l 292 var/log/lastlog | head -3
000476e8: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000476f8: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00047708: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

위 출력은 명세로 만든 예시입니다. 그 UID 로 로그인한 적이 없거나 useradd 가 칸을 지웠으면 이렇게 전부 0 입니다. 파일 크기가 292584 바이트 이하이면 그 칸은 아직 없는 것이고, 4.13 이후 판의 useradd 는 이때 손대지 않습니다[2]. RHEL 9 의 4.9 판은 크기를 보지 않고 그 오프셋에 쓰므로 파일이 그만큼 늘어납니다[4].

shadow 3번째 칸은 텍스트이므로 날짜로 바로 바꿉니다. 예를 들어 `20151` 일은 `date -u -d @$((20151*86400))` 로 2025-03-04 가 됩니다(만든 예시).

### 공개 도구로 한 번

```
# 인증 로그에서 계정 관련 줄 (순환본 포함)
zgrep -hE ' (useradd|usermod|userdel|groupadd|groupmod|gpasswd|chage|passwd)\[' var/log/auth.log* var/log/secure* 2>/dev/null

# 저널에서 같은 줄 (수집한 저널 폴더를 지정)
journalctl -D var/log/journal --utc -o short-iso SYSLOG_IDENTIFIER=useradd

# 감사 로그에서 계정 추가·삭제·변경 레코드
ausearch -if var/log/audit -m ADD_USER,DEL_USER,USER_MGMT,ADD_GROUP,DEL_GROUP,GRP_MGMT,USER_CHAUTHTOK -i

# 백업과 현재 계정 파일 비교
diff etc/passwd- etc/passwd
```

`journalctl` 의 `-D` 는 다른 기계에서 가져온 저널 폴더를 읽고, `--utc` 는 시각을 UTC 로 보여 줍니다[14]. `ausearch` 의 `-m` 은 쉼표로 여러 종류를 받고, `-if` 로 수집한 로그 폴더를 지정합니다[13]. `-i` 는 UID 를 이름으로 바꾸는데, 분석하는 기계의 계정으로 바꾸므로 로그에 보충 정보가 없으면 틀린 이름이 나올 수 있습니다[13].

dissect.target 의 `passwords` 는 `/etc/shadow` 와 `/etc/shadow-` 를 함께 읽어 마지막 변경일을 날짜로 바꿔 줍니다[15]. Velociraptor `Linux.Users.InteractiveUsers` 는 셸이 `/usr/sbin/nologin`, `/bin/false`, `/sbin/nologin`, `/bin/sync` 가 아닌 계정을 골라 줍니다[16].

## 교차 검증

| 함께 볼 것 | 맞춰 볼 내용 |
|---|---|
| [sudo·su 사용 기록](sudo-su.md) | 같은 시각 `COMMAND=/usr/sbin/useradd …` 줄로 누가 실행했는지 |
| [셸 명령 기록](../execution/shell-history/index.md) | 같은 사용자의 기록에 `useradd`·`usermod` 명령이 있는지 |
| [계정 파일](../../01-foundations/users-auth/passwd-shadow-group.md) | 줄의 이름·UID 가 현재 파일과 `-` 백업에 있는지, shadow 3번째 칸 날짜가 줄 날짜와 맞는지 |
| [로그인 기록 (wtmp·btmp·lastlog)](wtmp-btmp-lastlog.md) | 새 계정이 언제 처음 로그인했는지 |
| [SSH](ssh/index.md) | 새 계정에 `authorized_keys` 가 생겼는지 |
| 홈 폴더 | 홈과 skel 복사본의 생성 시각이 `new user:` 줄 시각과 맞는지 |

새 계정을 만든 뒤 `sudo` 그룹이나 `wheel` 그룹에 넣은 흐름은 [권한을 올렸나](../../04-scenarios/intrusion/privilege-escalation.md)에서, 로그를 지운 흔적은 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md)에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 Linux 검체로 다음 질문을 풀어 봅니다.

1. 인증 로그와 저널에서 `new user:` 줄을 모두 찾고, 각 계정이 지금 `/etc/passwd` 에 있는지 확인합니다.
2. UID 가 `UID_MIN` 이상인 계정마다 shadow 3번째 칸을 날짜로 바꾸고, `new user:` 줄 날짜(UTC)와 맞는지 봅니다.
3. `/etc/passwd` 와 `/etc/passwd-` 를 비교해 마지막 변경에서 무엇이 달라졌는지 찾고, 그 변경에 해당하는 로그 줄이 있는지 봅니다.
4. 계정 생성 줄 바로 앞뒤에 같은 터미널(`from=`)의 sudo 줄이 있는지 찾아 실행한 사용자를 잇습니다.
5. `sudo`·`wheel`·`adm` 그룹에 들어간 기록(`add '…' to group '…'`, `user … added by … to group …`)이 있는지 찾습니다.

## 참고 문헌

1. shadow, lib/io/syslog.h·lib/gettime.c·lib/commonio.c. https://github.com/shadow-maint/shadow/tree/master/lib
2. shadow, src/useradd.c. https://github.com/shadow-maint/shadow/blob/master/src/useradd.c
3. shadow, src/usermod.c·userdel.c·groupadd.c·groupmod.c·gpasswd.c·passwd.c·chage.c. https://github.com/shadow-maint/shadow/tree/master/src
4. shadow 4.9, src/useradd.c·src/usermod.c·libmisc/gettime.c·lib/defines.h. https://github.com/shadow-maint/shadow/tree/4.9 · shadow 4.13, src/useradd.c. https://github.com/shadow-maint/shadow/blob/4.13/src/useradd.c
5. Ubuntu rsyslog 패키지(noble-updates), debian/50-default.conf. https://git.launchpad.net/ubuntu/+source/rsyslog/tree/debian?h=ubuntu/noble-updates
6. CentOS Stream 9 rsyslog 패키지, rsyslog.conf. https://gitlab.com/redhat/centos-stream/rpms/rsyslog/-/tree/c9s
7. Ubuntu adduser 패키지(noble), adduser·AdduserLogging.pm. https://git.launchpad.net/ubuntu/+source/adduser/tree/?h=ubuntu/noble
8. CentOS Stream 9 shadow-utils 패키지, shadow-utils.spec·shadow-utils.login.defs·shadow-utils.useradd. https://gitlab.com/redhat/centos-stream/rpms/shadow-utils/-/tree/c9s
9. Ubuntu shadow 패키지(noble-updates), debian/login.defs·debian/default/useradd·debian/passwd.install. https://git.launchpad.net/ubuntu/+source/shadow/tree/debian?h=ubuntu/noble-updates
10. shadow, man/useradd.8.xml·usermod.8.xml·shadow.5.xml·login.defs.d/SYS_UID_MAX.xml. https://github.com/shadow-maint/shadow/tree/master/man
11. Linux-PAM, modules/pam_unix/passverify.c. https://github.com/linux-pam/linux-pam/tree/master/modules/pam_unix
12. linux-audit, audit-documentation specs/messages/message-dictionary.csv·specs/fields/field-dictionary.csv. https://github.com/linux-audit/audit-documentation/tree/main/specs
13. linux-audit, audit-userspace docs/ausearch.8. https://github.com/linux-audit/audit-userspace/tree/master/docs
14. systemd, man/journalctl.xml. https://github.com/systemd/systemd/blob/main/man/journalctl.xml
15. fox-it dissect.target, dissect/target/plugins/os/unix/shadow.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/shadow.py
16. Velociraptor, artifacts/definitions/Linux/Sys/Users.yaml·Linux/Users/InteractiveUsers.yaml. https://github.com/Velocidex/velociraptor/tree/master/artifacts/definitions/Linux
17. UAC, artifacts/files/system/etc.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/system/etc.yaml
18. ForensicArtifacts, artifacts/data/unix_common.yaml. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/unix_common.yaml
19. shadow, man/chage.1.xml. https://github.com/shadow-maint/shadow/blob/master/man/chage.1.xml
