---
title: "계정 파일"
parent: "기반 · 사용자와 인증 구조"
nav_order: 150
---

# 계정 파일 (passwd·shadow·group)

`/etc/passwd`·`/etc/shadow`·`/etc/group`·`/etc/gshadow` 는 콜론으로 칸을 나눈 텍스트 파일이고, 로컬 계정의 이름·번호·홈·셸, 비밀번호 해시와 나이 정보, 그룹 구성원을 한 줄에 하나씩 담습니다.

## 이 형식을 쓰는 아티팩트

로컬 계정 목록은 이 네 파일에서 나옵니다. UID 를 사람 이름으로 바꾸는 일은 [UID·GID 와 사용자 이름 잇기](../value-decoding/uid-gid.md)에서, 계정을 만들고 바꾼 로그는 [계정 생성·변경 흔적](../../02-artifacts/logins/account-changes.md)에서 다룹니다. 로그인 기록([로그인 기록](../../02-artifacts/logins/wtmp-btmp-lastlog.md)), 인증 로그([인증 로그](../../02-artifacts/logins/auth-log.md)), sudo 권한([sudo 설정](sudoers.md))을 읽을 때도 사용자 이름과 그룹이 이 파일과 맞는지 먼저 봅니다.

| 파일 | 담는 것 | 읽을 수 있는 사람 |
|---|---|---|
| `/etc/passwd` | 계정마다 7칸: 이름, 비밀번호 자리, UID, 기본 GID, 설명(GECOS), 홈, 셸[1][4] | 모든 사용자. `ls` 같은 도구가 UID 를 이름으로 바꿀 때 씀[4] |
| `/etc/shadow` | 계정마다 9칸: 이름, 비밀번호 해시, 비밀번호 나이 정보, 계정 만료일[2] | 일반 사용자는 읽을 수 없어야 함[2] |
| `/etc/group` | 그룹마다 4칸: 이름, 비밀번호 자리, GID, 구성원 목록[5] | 검체에서 `ls -l` 로 권한을 확인 |
| `/etc/gshadow` | 그룹마다 4칸: 이름, 그룹 비밀번호 해시, 관리자 목록, 구성원 목록[3] | 일반 사용자는 읽을 수 없어야 함[3] |
| `/etc/passwd-`·`/etc/shadow-` 등 | 바로 앞 판의 백업. shadow 도구 모음은 쓰지만 모든 계정 관리 도구가 쓰지는 않음[1][2] | 원본과 같은 소유자·그룹으로 만들고, 권한은 원본 권한 중 `0664` 안쪽만 남김[9][10] |

계정 파일은 shadow 도구 모음(shadow-utils)의 `useradd`·`usermod`·`userdel`·`groupadd`·`chage`·`vipw` 등이 고치고, 비밀번호를 바꿀 때는 PAM 의 `pam_unix` 모듈이 `/etc/shadow` 를 직접 고치기도 합니다[8][11]. 두 경로가 파일을 쓰는 방식이 달라서 백업 파일이 생기는지가 달라집니다. 이 차이는 아래 "백업·임시·잠금 파일" 에서 다룹니다.

배포판마다 달라지는 값은 계정 생성 기본값을 적는 `/etc/login.defs` 에 모여 있습니다.

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| shadow 도구 패키지 | `passwd`(원본 패키지 이름은 shadow)[12] | `shadow-utils`, 4.9 판[13] |
| `ENCRYPT_METHOD` | `SHA512`[12] | `SHA512`[13] |
| `PASS_MAX_DAYS`·`PASS_MIN_DAYS`·`PASS_WARN_AGE` | 99999·0·7[12] | 99999·0·7[13] |
| `UID_MIN`·`UID_MAX` | 1000·60000[12] | 1000·60000[13] |
| `SYS_UID_MIN`·`SYS_UID_MAX` | 주석 처리되어 상류 기본값 101·`UID_MIN`-1 을 따름[7][12] | 201·999[13] |

shadow 도구는 `ENCRYPT_METHOD` 를 그룹 비밀번호를 만들 때만 쓰고, 사용자 비밀번호의 해시 방식은 PAM 설정이 정합니다[7]. `pam_unix` 는 모듈 인자로 해시 방식을 주지 않았을 때 login.defs 의 `ENCRYPT_METHOD` 를 읽고, 그것도 없으면 SHA512 를 씁니다[11]. 그래서 검체의 실제 해시 방식은 shadow 의 해시 앞머리와 [인증 모듈](pam.md)의 `pam_unix` 줄을 함께 보고 정합니다. `PASS_MAX_DAYS`·`PASS_WARN_AGE` 는 계정을 만들 때만 쓰이고, 값을 바꿔도 기존 계정에는 영향이 없습니다[7]. UID 범위의 뜻은 [UID·GID 와 사용자 이름 잇기](../value-decoding/uid-gid.md)에 있습니다.

## 구조

### /etc/passwd

한 줄의 모양은 `name:password:UID:GID:GECOS:directory:shell` 입니다[4].

| 칸 | 이름 | 뜻 |
|---|---|---|
| 1 | 로그인 이름 | 대문자를 넣지 않아야 함[4] |
| 2 | 비밀번호 | 보통 `x`. 아래 표 참고[1] |
| 3 | UID | 0 이 root(슈퍼유저)[4] |
| 4 | GID | 기본 그룹(primary group). 추가 그룹은 `/etc/group` 에 적음[4] |
| 5 | GECOS | 이름·설명. `&` 는 finger 같은 도구가 보여 줄 때 첫 글자를 대문자로 바꾼 로그인 이름으로 바뀜[1] |
| 6 | 홈 디렉터리 | 로그인 때 `$HOME` 이 됨[1] |
| 7 | 셸 | 로그인 때 실행할 프로그램, `$SHELL` 이 됨. 비어 있으면 `/bin/sh`[1][4] |

셸 칸에 없는 실행 파일을 적으면 `login(1)` 로는 로그인할 수 없습니다[4]. 다만 셸 칸만 바꿔 계정을 막으면 rlogin·rsh·cron·at·메일 필터로 프로세스를 돌리는 길과 `su` 는 그대로 남습니다[4].

### 비밀번호 칸에 올 수 있는 값

passwd 의 2번째 칸과 shadow 의 2번째 칸은 같은 규칙으로 읽습니다.

| 값 | 뜻 |
|---|---|
| `x` (passwd) | 해시는 `/etc/shadow` 에 있음. shadow 에 대응하는 줄이 없으면 그 계정은 무효[1] |
| 빈칸 | 비밀번호 없이 인증될 수 있음. 빈칸을 거부하는 프로그램도 있고, `pam_unix` 의 `nullok`·`nonull` 설정에 따라 달라짐[1][2][4] |
| `!` 로 시작 | 잠긴 비밀번호. `!` 뒤의 글자는 잠그기 전의 값[1][2] |
| `*` | 어떤 비밀번호로도 만들 수 없는 값이라 비밀번호 로그인이 막힘[2] |
| `*NP*` (passwd) | shadow 레코드를 NIS+ 서버에서 가져옴[4] |
| `$` 로 시작하는 문자열 등 | crypt(3) 해시. 아래 "해시 문자열" 참고[6] |

`!`·`*` 처럼 crypt(3) 결과가 될 수 없는 값이 있으면 유닉스 비밀번호로는 로그인할 수 없지만, 다른 수단으로 로그인할 수는 있습니다[1][2]. rlogin·rsh·cron·at·메일 필터가 그런 수단입니다[4].

### /etc/shadow

| 칸 | 이름 | 단위와 특수 값 |
|---|---|---|
| 1 | 로그인 이름 | 시스템에 있는 계정 이름이어야 함[2] |
| 2 | 비밀번호 해시 | 위 표와 같음 |
| 3 | 마지막 비밀번호 변경일 | 1970-01-01 00:00:00 UTC 부터 센 일수. `0` 은 다음 로그인 때 비밀번호를 바꿔야 함, 빈칸은 나이 기능 끔[2] |
| 4 | 최소 사용 기간 | 일수. 상류 최신 shadow(5) 는 "폐기, 비워 두며 무시" 로 적음[2] |
| 5 | 최대 사용 기간 | 일수. 지나면 다음 로그인 때 변경을 요구. 빈칸이면 최대 기간·경고·비활성 기간이 모두 없음[2] |
| 6 | 경고 기간 | 만료 전 경고하는 일수. 빈칸과 `0` 은 경고 없음[2] |
| 7 | 비활성 기간 | 만료 뒤에도 비밀번호를 받아 주는 일수. 지나면 로그인할 수 없음[2] |
| 8 | 계정 만료일 | 1970-01-01 부터 센 일수. 빈칸은 만료 없음. `0` 은 "만료 없음" 과 "1970-01-01 만료" 로 둘 다 읽힐 수 있어 쓰지 말라고 되어 있음[2] |
| 9 | 예약 | 앞으로 쓸 칸[2] |

계정 만료(8번째 칸)는 로그인 자체를 막고, 비밀번호 만료는 비밀번호 로그인만 막습니다[2]. `chage -d` 와 `chage -E` 는 날짜를 `YYYY-MM-DD` 나 일수로 받고, 날짜는 UTC 로 해석합니다[8].

4번째 칸은 출처끼리 다릅니다. 상류 최신 shadow(5) 는 이 칸을 무시한다고 적지만[2], `pam_unix` 코드는 이 값이 0보다 크면 마지막 변경일부터 그 일수가 지나기 전에는 비밀번호 변경을 막습니다[11]. 검체의 동작은 설치된 판의 man 페이지와 PAM 설정으로 확인합니다.

### 해시 문자열

crypt(5) 해시는 앞머리(prefix)·옵션·솔트·해시 네 부분으로 되어 있고, 부분 사이는 보통 `$` 로 나눕니다[6]. 해시 문자열은 늘 인쇄할 수 있는 ASCII 이고, 공백과 `:`·`;`·`*`·`!`·`\` 를 담지 않습니다[6]. 이 글자들은 passwd·shadow 의 구분 기호와 특수 표시로 쓰이기 때문입니다[6].

| 앞머리 | 방식 | 해석할 때 볼 점 |
|---|---|---|
| `$y$` | yescrypt | 새 해시에 권장[6] |
| `$gy$`·`$sm3y$` | gost-yescrypt·sm3-yescrypt | yescrypt 출력을 GOST R 34.11-2012·SM3 해시의 HMAC 에 한 번 더 넣음[6] |
| `$7$` | scrypt | [6] |
| `$2b$` | bcrypt | `$2y$` 는 `$2b$` 와 같고, `$2a$`·`$2x$` 는 옛 구현의 버그 호환용[6] |
| `$6$`·`$5$` | sha512crypt·sha256crypt | `rounds=N$` 옵션이 올 수 있고, 없으면 비용 5000[6] |
| `$1$` | md5crypt | [6] |
| `_` | bsdicrypt | [6] |
| (앞머리 없음, 13글자) | descrypt | 비밀번호를 8글자로 자름[6] |

같은 계정의 해시 앞머리가 백업 파일과 현재 파일에서 다르면, 그 사이에 비밀번호를 다시 설정했거나 설정한 도구·설정이 달랐다는 뜻입니다.

### /etc/group 과 /etc/gshadow

`/etc/group` 은 `group_name:password:GID:user_list` 모양이고, 구성원 목록은 쉼표로 나눈 사용자 이름입니다[5]. `/etc/gshadow` 는 그룹 이름, 그룹 비밀번호 해시, 관리자 목록, 구성원 목록을 콜론으로 나눕니다[3]. gshadow 의 비밀번호가 group 의 비밀번호보다 우선하고, 이 비밀번호는 구성원이 아닌 사용자가 `newgrp` 로 그룹 권한을 얻을 때 씁니다[3]. 관리자 목록에 든 사용자는 그룹 비밀번호와 구성원을 바꿀 수 있습니다[3].

기본 그룹은 passwd 의 4번째 칸이 정하고, group 의 구성원 목록은 추가 그룹을 정합니다[4]. 그래서 어떤 그룹(예: 관리자 그룹)의 구성원을 셀 때는 group 의 목록만 보지 않고, passwd 에서 그 GID 를 기본 그룹으로 둔 계정도 함께 셉니다.

### 백업·임시·잠금 파일

shadow 도구는 파일을 고칠 때 먼저 `파일이름.lock` 을 만들어 잠그고, libc 에 `lckpwdf()` 가 있으면 그것도 씁니다[9]. 그 뒤 기존 내용을 `파일이름-` 백업으로 복사하고, 새 내용을 임시 파일에 쓴 다음 `rename` 으로 원래 이름에 덮어씁니다[9][10]. 백업 파일에는 복사가 끝난 뒤 원본 파일의 접근 시각(atime)과 수정 시각(mtime)을 그대로 입힙니다[9][10].

| 판 | 임시 파일 | 백업 만드는 법 |
|---|---|---|
| 상류 2026년 1월 변경 전 (4.9·4.13 판 포함) | `파일이름+` (예: `/etc/passwd+`)[10] | `파일이름-` 를 쓰기 모드로 열어 그대로 덮어씀[10] |
| 상류 2026년 1월 변경 뒤 | `파일이름.cioXXXXXX`[9] | `.cioXXXXXX` 임시 파일에 쓴 뒤 `파일이름-` 로 이름을 바꿈[9] |

RHEL 9 의 shadow-utils 는 4.9 판이라 앞의 방식입니다[13]. Ubuntu 24.04 는 검체에서 `dpkg -s passwd` 로 판을 확인합니다. 옛 방식은 원래 이름이 심볼릭 링크이면 링크가 가리키는 실제 파일에 덮어씁니다[10].

`pam_unix` 가 비밀번호를 바꿀 때는 `/etc/.pam.shadowXXXXXX`(passwd 는 `/etc/.pam.passwdXXXXXX`) 임시 파일에 쓰고 `rename` 으로 `/etc/shadow` 에 덮으며, `shadow-` 백업은 만들지 않습니다[11]. 이때 3번째 칸(마지막 변경일)은 그 순간의 epoch 초를 86400 으로 나눈 값으로 채웁니다[11]. `remember=n` 을 켜면 이전 비밀번호의 MD5 해시가 `/etc/security/opasswd` 에 `user:uid:개수:해시,해시` 모양으로 쌓입니다[11]. 이 설정은 [인증 모듈](pam.md)에서 다룹니다.

`vipw`·`vigr` 는 passwd·group 을(`-s` 를 주면 shadow·gshadow 를) 잠근 뒤 `$VISUAL`, `$EDITOR`, `vi` 순서로 편집기를 엽니다[8]. 편집기로 파일을 직접 고치면 위의 백업 순서를 거치지 않을 수 있습니다.

### 함께 모을 파일

| 경로 | 담는 것 |
|---|---|
| `/etc/login.defs` | 계정 생성 기본값. libeconf 로 빌드하면 `/usr/etc/login.defs`, `/usr/lib/login.defs`, `/etc/login.defs.d/` 도 합쳐 읽음[7] |
| `/etc/default/useradd`, `/etc/skel/` | useradd 기본값, 새 홈에 복사할 파일[8] |
| `/etc/shadow-maint/useradd-pre.d/*`, `/etc/shadow-maint/useradd-post.d/*` | 계정 추가 전후에 실행하는 스크립트. 0이 아닌 값으로 끝나면 useradd 가 멈춤[8] |
| `/etc/subuid`, `/etc/subgid` | `이름또는UID:시작번호:개수` 3칸. 사용자 이름공간에서 쓸 하위 번호 범위[8] |
| `/etc/nsswitch.conf` | `passwd`·`group` 같은 이름 정보를 어떤 원천(`files`, `ldap` 등)에서 어떤 순서로 찾는지[14][18] |
| `/etc/passwd.cache` | nsscache 가 만드는 계정 캐시[14] |

`useradd-pre.d`·`useradd-post.d` 는 계정을 만들 때마다 실행되므로, 검체에 파일이 있으면 내용과 시각을 봅니다. 지속성 점검 전체는 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md)에서 다룹니다.

## 읽는 법

1. `/etc/passwd`, `/etc/passwd-`, `/etc/shadow`, `/etc/shadow-`, `/etc/group`, `/etc/group-`, `/etc/gshadow`, `/etc/gshadow-`, `/etc/login.defs`, `/etc/subuid`, `/etc/subgid` 를 모두 모읍니다. 수집 도구마다 빠지는 파일이 달라서 아래 "도구" 표를 보고 빈 곳을 채웁니다.
2. 파일마다 크기·mtime·ctime·아이노드 번호를 먼저 적습니다. 백업 파일의 mtime 은 해석에 쓰이므로 내용을 읽기 전에 기록합니다.
3. GECOS 칸에는 권한 없는 사용자도 C1 제어 문자를 포함한 비ASCII 문자를 쓸 수 있으므로, C 로캘로 읽어야 실제 내용이 보입니다[1]. `LC_ALL=C cat -v` 로 보면 제어 문자가 `M-` 나 `^` 표기로 드러납니다.
4. passwd 와 shadow 의 이름을 한 줄씩 맞춥니다. 한쪽에만 있는 이름, 비밀번호 칸에 `x` 대신 해시가 있는 passwd 줄, UID 가 0 인 줄을 따로 적습니다.
5. shadow 의 일수를 날짜로 바꿉니다. 일수에 86400 을 곱하면 UTC 기준 epoch 초이고, `0` 과 빈칸은 날짜로 바꾸지 않고 뜻대로 적습니다.
6. 그룹 구성원을 group 의 목록과 passwd 의 기본 GID 두 곳에서 모읍니다.
7. 현재 파일과 `-` 백업을 줄 단위로 비교해, 백업에만 있는 계정·그룹과 해시·UID·셸이 바뀐 줄을 찾습니다.

### 헥스로 한 번

텍스트 파일이라 헥스가 필요한 경우는 GECOS 에 숨은 글자를 볼 때입니다. 아래는 passwd(5) 형식으로 만든 예시 줄이고, GECOS 에 U+0085(C1 제어 문자, UTF-8 로 `C2 85`)를 넣었습니다.

```text
00000000: 7465 7374 6572 3a78 3a31 3030 313a 3130  tester:x:1001:10
00000010: 3031 3a54 6573 7465 72c2 852c 2c2c 3a2f  01:Tester..,,,:/
00000020: 686f 6d65 2f74 6573 7465 723a 2f62 696e  home/tester:/bin
00000030: 2f62 6173 680a                           /bash.
```

`3a` 가 콜론이므로 칸 경계는 `3a` 여섯 개로 나뉘고, 5번째 칸 안의 `c2 85` 는 UTF-8 로캘 터미널에서는 보이지 않을 수 있습니다. 칸 수가 7이 아니거나 `3a` 가 예상보다 많으면 줄이 깨졌거나 누군가 손으로 고쳤을 가능성이 있습니다.

shadow 의 일수는 다음처럼 바꿉니다(만든 예시).

```text
tester:$y$j9T$ABCDEFGHIJKLMNOP$0123456789abcdefghijklmnopqrstuvwxyzABCDEFG:20000:0:99999:7:::
```

3번째 칸 20000 에 86400 을 곱하면 1728000000 이고, `date -u -d @1728000000` 은 `2024-10-04 00:00:00 UTC` 입니다. 이 값은 "2024-10-04(UTC 기준 날짜) 에 마지막으로 비밀번호를 바꿨다" 까지만 말합니다.

### 명령으로 한 번

모은 사본에서 다음처럼 확인합니다. 모두 사본 경로를 인자로 주고, 분석 PC 의 `/etc` 를 건드리지 않습니다.

```sh
# UID 0 인 계정
awk -F: '$3 == 0 {print $1}' passwd

# passwd 에 해시가 직접 들어 있는 줄
awk -F: '$2 != "x" && $2 != "" {print $1, substr($2,1,4)}' passwd

# shadow: 이름, 비밀번호 칸 앞 6글자(잠금 표시 ! 포함), 마지막 변경일(UTC)
awk -F: '{d=($3 ~ /^[1-9][0-9]*$/) ? strftime("%F", $3*86400, 1) : $3; print $1, substr($2,1,6), d}' shadow

# 백업과 현재 파일 비교
diff passwd- passwd
```

`strftime` 의 세 번째 인자는 gawk 에서 UTC 로 찍으라는 뜻입니다. `pwck -r passwd shadow` 는 읽기 전용으로 칸 수, 이름 중복, UID·GID, 기본 그룹, 홈, 셸, passwd 와 shadow 의 대응, 미래의 마지막 변경일을 검사합니다[8]. 홈과 셸이 있는지는 분석 PC 에서 검사할 가능성이 있으니 그 경고는 걸러 읽습니다.

## 포렌식에서 중요한 점

### 증명하는 것

수집 시점에 어떤 계정·UID·그룹 구성이 로컬 파일에 있었는지, 어느 계정의 비밀번호가 잠겼는지(`!`), 어떤 해시 방식을 썼는지, shadow 기준으로 마지막 비밀번호 변경이 어느 날(UTC) 이었는지를 보여 줍니다. 백업 파일이 남아 있으면 바로 앞 판과 무엇이 달라졌는지도 보여 줍니다.

### 증명하지 못하는 것

누가 바꿨는지, 몇 시 몇 분에 바꿨는지는 이 파일만으로 알 수 없습니다. shadow 의 날짜는 일 단위라 시각이 없습니다. `*`·`!` 계정이라도 cron·at 처럼 비밀번호를 쓰지 않는 수단으로 쓰였을 수 있습니다[1][4]. `nsswitch.conf` 가 LDAP 같은 다른 원천을 쓰면[18] 로컬 파일에 없는 계정도 로그인할 수 있으므로, passwd 에 없다고 계정이 없었다고 쓰지 않습니다. 보고서에는 "수집 시점의 `/etc/shadow` 에서 이 계정의 마지막 비밀번호 변경일은 2024-10-04(UTC) 로 기록되어 있다" 처럼 기록이 말하는 만큼 씁니다(날짜는 만든 예시).

### 시각 해석

shadow 의 3번째·8번째 칸은 1970-01-01 UTC 부터 센 일수입니다[2]. 날짜의 경계도 UTC 자정이라, UTC+9 지역에서 오전 9시 전에 바꾼 비밀번호는 현지 날짜보다 하루 이른 날짜로 기록됩니다. `pam_unix` 도 epoch 초를 86400 으로 나눈 값을 씁니다[11]. 일수 계산과 다른 시각 값의 단위는 [Linux 의 시각 값](../value-decoding/time-values.md)에 모여 있습니다.

파일 자체의 시각은 쓰는 방식에 따라 뜻이 달라집니다.

- shadow 도구와 `pam_unix` 는 새 내용을 임시 파일에 쓰고 `rename` 으로 덮으므로, 고칠 때마다 원래 파일 이름이 새 아이노드를 가리킵니다[9][10][11]. 그래서 현재 파일의 mtime·ctime 은 마지막으로 이 방식으로 고친 시각에 가깝습니다.
- shadow 도구는 백업 파일에 원본의 atime·mtime 을 입히므로, `passwd-` 의 mtime 은 백업을 만든 시각이 아니라 그 직전에 원본이 고쳐진 시각입니다[9][10]. 백업의 ctime 은 `utime` 을 호출한 시각, 곧 새 판을 쓴 시각에 가깝습니다.
- `pam_unix` 로 비밀번호를 바꾸면 `shadow-` 백업이 갱신되지 않으므로[11], `shadow-` 는 마지막 shadow 도구 변경 직전의 판입니다. "백업은 바로 앞 판" 이라고 단정하지 않습니다.

아이노드 시각의 저장 방식은 [ext4 시각](../filesystem/ext4/timestamps.md)에서 다룹니다.

### 지운 계정과 조작 흔적

`/etc/passwd-`·`/etc/group-` 에만 있는 계정·그룹은 마지막 변경 때 지워졌을 가능성이 높습니다. 지운 계정의 UID 로 남은 파일은 [UID·GID 와 사용자 이름 잇기](../value-decoding/uid-gid.md)에서 찾습니다.

계정 파일을 편집기로 직접 고치면 편집기마다 저장 방식이 달라서, 백업이 생기지 않거나 아이노드가 그대로이거나 편집기 임시 파일이 남을 가능성이 있습니다. 이럴 때는 계정 변경 로그가 없는데 파일 mtime 만 바뀐 모양이 됩니다. `useradd`·`usermod` 가 남기는 로그 줄은 [계정 생성·변경 흔적](../../02-artifacts/logins/account-changes.md)에서 다룹니다.

`/etc/passwd+`·`/etc/shadow+`·`파일이름.cioXXXXXX`·`파일이름.lock`·`/etc/.pam.shadowXXXXXX` 가 남아 있으면 쓰기 도중 멈춘 흔적일 가능성이 있습니다[9][10][11]. 이런 파일에는 적용되지 못한 새 판이 들어 있을 수 있으므로 내용과 시각을 따로 적습니다. 원래 이름을 새 아이노드로 덮는 방식이라, 옛 판의 내용이 파일 시스템의 비할당 영역에 남아 있을 가능성도 있습니다. 지운 파일을 되살리는 방법은 [ext4 지운 파일](../filesystem/ext4/deleted-files.md)에서 다룹니다.

## 함정

- **마지막 변경일 `0`**: 1970-01-01 이 아니라 "다음 로그인 때 바꿔야 함" 입니다[2]. 날짜로 바꾸는 도구는 이 뜻을 잃기 쉽습니다.
- **계정 만료일 `0`**: "만료 없음" 과 "1970-01-01 만료" 로 해석이 갈립니다[2].
- **passwd 에 해시가 있는 줄**: `x` 대신 해시가 있으면 shadow 를 쓰지 않는 계정이고, 그 해시는 모든 사용자가 읽을 수 있습니다[1][4].
- **UID 중복**: `usermod -o` 로 이미 있는 UID 를 줄 수 있고[8], `pwck` 의 검사 항목에는 UID 중복이 없습니다[8]. UID 0 인 이름이 root 하나인지 직접 셉니다.
- **기본 그룹 누락**: group 의 구성원 목록만 보면 GID 를 기본 그룹으로 둔 계정을 빠뜨립니다[4].
- **백업이 늘 바로 앞 판은 아님**: shadow 도구 모음 밖의 도구는 백업을 쓰지 않을 수 있고, `pam_unix` 는 백업을 만들지 않습니다[1][11].
- **셸이 막혀 있어도 쓰인 계정**: `nologin`·`false` 셸이나 `*` 비밀번호 계정도 cron·at 등으로 프로세스를 돌릴 수 있습니다[4].
- **GECOS 의 제어 문자**: UTF-8 로캘로 보면 글자가 숨어 보일 수 있습니다[1].

## 도구

| 도구 | 하는 일 | 주의할 점 |
|---|---|---|
| ForensicArtifacts | `UnixPasswdFile`·`UnixShadowFile`·`UnixShadowBackupFile`·`UnixGroupsFile`, 묶음 `UnixUsersGroups`[14] | `/etc/passwd-`·`/etc/group-`·`/etc/gshadow`·`/etc/login.defs`·`/etc/subuid` 정의가 없음[14] |
| UAC | `/etc` 를 통째로 모음[15] | `shadow`·`shadow-`·`gshadow`·`gshadow-` 를 빼고 모으므로 기본 수집에 해시와 나이 정보가 없음[15] |
| Velociraptor | `Linux.Sys.Users` 가 passwd 를 7칸으로, `Linux.Sys.Groups` 가 group 을 4칸으로 나눔. `Linux.Users.InteractiveUsers` 는 셸이 `/usr/sbin/nologin`·`/bin/false`·`/sbin/nologin`·`/bin/sync` 가 아닌 계정[16] | `Linux.Sys.Users` 는 비밀번호 칸을 출력하지 않아 passwd 에 들어 있는 해시가 보이지 않음[16]. 기본 그룹 구성원은 `Linux.Sys.Groups` 에 나오지 않음[16] |
| dissect.target `users` | `/etc/passwd`·`/etc/passwd-`·`/etc/master.passwd` 를 읽고 이름·홈·셸이 같은 줄은 한 번만 냄. 레코드에 원천 파일(`source`)을 남김[17] | 백업에만 있는 계정도 함께 나오므로 `source` 로 가름 |
| dissect.target `passwords` | `/etc/shadow`·`/etc/shadow-` 를 읽고 이름과 해시가 같은 줄은 한 번만 냄. 날짜 칸을 UTC 날짜로 바꿈[17] | 아래 설명 참고 |

dissect.target 의 `passwords` 는 비밀번호 칸을 `$` 로 나눠 부분이 4개나 5개일 때만 해시로 보고, 해시가 없으면 레코드를 내지 않습니다[17]. 그래서 `*`·`!`·빈칸인 계정과 앞머리가 없는 descrypt 해시는 결과에 없고, `!` 뒤에 해시가 붙은 잠긴 계정은 나옵니다. 잠금 여부는 `crypt` 칸의 첫 글자로 봅니다. 레코드에 원천 파일 칸이 없어 shadow 와 `shadow-` 중 어디서 나온 줄인지 알 수 없습니다[17]. `min_age`·`max_age` 는 일수가 아니라 마지막 변경일에 그 일수를 더한 날짜이고, 마지막 변경일이 `0` 이면 날짜 칸이 비어 "다음 로그인 때 바꿔야 함" 이라는 뜻이 사라집니다[17]. 해시 이름표도 crypt(5) 와 다릅니다. dissect.target 은 `$2y$` 를 `eksbcrypt`, `$0$` 을 `des` 로 적지만[17], crypt(5) 에서 `$2y$` 는 `$2b$` 와 같은 bcrypt 이고 descrypt 는 앞머리가 없습니다[6].

수집 방법 전체는 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md)에서 다룹니다.

## 참고 문헌

1. shadow, passwd(5). https://github.com/shadow-maint/shadow/blob/master/man/passwd.5.xml
2. shadow, shadow(5). https://github.com/shadow-maint/shadow/blob/master/man/shadow.5.xml
3. shadow, gshadow(5). https://github.com/shadow-maint/shadow/blob/master/man/gshadow.5.xml
4. Linux man-pages, passwd(5). https://github.com/mkerrisk/man-pages/blob/master/man5/passwd.5
5. Linux man-pages, group(5). https://github.com/mkerrisk/man-pages/blob/master/man5/group.5
6. libxcrypt, crypt(5). https://github.com/besser82/libxcrypt/blob/develop/doc/crypt.5
7. shadow, login.defs(5) 와 `man/login.defs.d/`(`ENCRYPT_METHOD`·`UID_MAX`·`SYS_UID_MAX`·`PASS_MAX_DAYS`). https://github.com/shadow-maint/shadow/blob/master/man/login.defs.5.xml
8. shadow, useradd(8)·usermod(8)·chage(1)·pwck(8)·vipw(8)·subuid(5). https://github.com/shadow-maint/shadow/tree/master/man
9. shadow, `lib/commonio.c`(master) 와 커밋 f8732b17dd "lib/commonio.c: Use unpredictable temporary names". https://github.com/shadow-maint/shadow/blob/master/lib/commonio.c , https://github.com/shadow-maint/shadow/commit/f8732b17dd
10. shadow, `lib/commonio.c`(4.9·4.13 태그). https://github.com/shadow-maint/shadow/blob/4.9/lib/commonio.c , https://github.com/shadow-maint/shadow/blob/4.13/lib/commonio.c
11. Linux-PAM, `modules/pam_unix/passverify.c`·`passverify.h`·`pam_unix.8.xml`. https://github.com/linux-pam/linux-pam/tree/master/modules/pam_unix
12. Ubuntu 24.04(noble-updates) shadow 패키지, `debian/login.defs`·`debian/passwd.install`. https://git.launchpad.net/ubuntu/+source/shadow/tree/debian?h=ubuntu/noble-updates
13. CentOS Stream 9 shadow-utils 패키지, `shadow-utils.login.defs`·`shadow-utils.spec`. https://gitlab.com/redhat/centos-stream/rpms/shadow-utils/-/tree/c9s
14. ForensicArtifacts, `artifacts/data/unix_common.yaml`·`linux.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/unix_common.yaml
15. UAC, `artifacts/files/system/etc.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/files/system/etc.yaml
16. Velociraptor, `Linux/Sys/Users.yaml`·`Linux/Sys/Groups.yaml`·`Linux/Users/InteractiveUsers.yaml`. https://github.com/Velocidex/velociraptor/tree/master/artifacts/definitions/Linux
17. dissect.target, `plugins/os/unix/shadow.py`·`plugins/os/unix/_os.py`. https://github.com/fox-it/dissect.target/tree/main/dissect/target/plugins/os/unix
18. Linux man-pages, nsswitch.conf(5). https://github.com/mkerrisk/man-pages/blob/master/man5/nsswitch.conf.5
