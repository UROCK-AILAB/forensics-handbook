---
title: "인증 모듈"
parent: "기반 · 사용자와 인증 구조"
nav_order: 170
---

# 인증 모듈 (PAM)

PAM (Pluggable Authentication Modules) 은 login·sshd·sudo 같은 프로그램이 사용자를 확인하고 세션을 여는 절차를 설정 파일과 모듈(`.so`)로 나눠 맡기는 구조이고, 그 설정 파일과 모듈이 남기는 로그 줄·감사 레코드·실패 기록 파일이 인증 흔적을 해석하는 기준이 됩니다.

## 이 형식을 쓰는 아티팩트

인증 로그(`auth.log`·`secure`)에 찍히는 `pam_unix(sshd:session): session opened ...` 같은 줄은 PAM 모듈이 syslog 로 보낸 것입니다[3][5]. 감사 로그의 `USER_AUTH`·`USER_START` 같은 레코드는 PAM 라이브러리(libpam)가 직접 씁니다[4][9]. 그래서 로그인 기록을 읽을 때는 그 서비스의 PAM 설정에 어떤 모듈이 어떤 옵션으로 들어 있었는지를 먼저 알아야, 줄이 있거나 없는 이유를 설명할 수 있습니다.

PAM 이 흔적을 남기는 곳은 다음과 같습니다.

| 흔적 | 누가 남기나 | 자세한 곳 |
|---|---|---|
| 인증 로그의 `모듈이름(서비스:동작):` 줄 | 각 모듈이 `pam_syslog` 로 보냄[3] | [인증 로그](../../02-artifacts/logins/auth-log.md) |
| 감사 로그의 `PAM:` 메시지 | libpam[4] | [감사 로그 형식](../logging/auditd-format.md) |
| `/var/run/faillock/사용자이름` | pam_faillock[7] | 이 페이지의 "pam_faillock 실패 기록 파일" 절 |
| `/etc/security/opasswd` | pam_unix 의 `remember=n`[5] | [계정 파일](passwd-shadow-group.md) |
| 감사 로그의 `auid` | pam_loginuid 가 정한 값[8] | [감사 로그 형식](../logging/auditd-format.md) |
| sudo·su 세션 줄 | sudo·su 가 부른 pam_unix | [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md) |

## 구조

### 설정 파일 위치와 우선순위

설정은 서비스마다 파일 하나이고, 파일 이름이 곧 서비스 이름(소문자)입니다. `/etc/pam.d/` 폴더가 있으면 옛 방식의 단일 파일 `/etc/pam.conf` 는 읽지 않습니다[1]. 배포판이 싣는 설정은 `/usr/lib/pam.d/` 나 빌드할 때 정한 vendor 폴더(`%vendordir%/pam.d`)에 둘 수 있고, `/etc/pam.d/` 에 같은 이름 파일이 있으면 그 파일이 이깁니다. vendor 폴더 파일은 `/etc/pam.d/` 와 `/usr/lib/pam.d/` 양쪽에 같은 이름이 없을 때만 씁니다[1][2]. 서비스 이름 `other` 는 설정이 없는 서비스에 쓰는 기본 규칙입니다[1].

| 항목 | Ubuntu 24.04 (pam 1.5.3) | RHEL 9 (pam 1.5.1) |
|---|---|---|
| 서비스 설정 | `/etc/pam.d/` | `/etc/pam.d/` |
| vendor 설정 폴더 | 빌드 규칙에 `--enable-vendordir` 없음[12] | `/usr/share/pam.d/`(`--enable-vendordir=%{_datadir}`)[11] |
| 여러 서비스가 끌어 쓰는 공통 파일 | `/etc/pam.d/common-auth`·`common-account`·`common-password`·`common-session`·`common-session-noninteractive`[12] | `/etc/pam.d/system-auth`·`password-auth`·`fingerprint-auth`·`smartcard-auth`·`postlogin`[11] |
| 공통 파일을 만드는 도구 | `/usr/sbin/pam-auth-update`, 원본 틀은 `/usr/share/pam/common-*`, 조각은 `/usr/share/pam-configs/`[12] | authselect(아래 표) |
| 모듈 폴더 | `/usr/lib/멀티아키텍처이름/security/`(amd64 는 `x86_64-linux-gnu`)[12] | `%{_libdir}/security`(64비트는 `/usr/lib64/security`)[11] |
| 모듈 옵션 파일 | `/etc/security/`[12] | `/etc/security/`(`faillock.conf`, `access.conf`, `limits.conf`, `pwhistory.conf` 등)[11] |
| 비밀번호 확인 보조 프로그램 | `/usr/sbin/unix_chkpwd`, 그룹 `shadow`, 권한 02755[12] | `/usr/sbin/unix_chkpwd`, 권한 4755 root[11] |

Ubuntu 패키지는 빌드할 때 `common-*` 틀 파일의 MD5 값이 `pam-auth-update` 안에 등록돼 있는지 검사합니다[12]. 분석 대상의 `/etc/pam.d/common-*` 가 `/usr/share/pam/` 의 틀과 다르면 `/usr/share/pam-configs/` 의 조각 파일과 [dpkg·apt 기록](../../02-artifacts/packages/dpkg-apt.md)을 함께 보고, 어느 조각이 더해졌는지와 직접 고친 줄이 있는지를 가려냅니다.

RHEL 계열에서 authselect 로 설정하면 authselect 가 공통 파일을 만듭니다. 실제 내용은 `/etc/authselect/` 에 있고, `/etc/pam.d/system-auth` 같은 파일은 그쪽을 가리키는 심볼릭 링크입니다[10].

| authselect 경로 | 담긴 것 |
|---|---|
| `/etc/authselect/system-auth` 등 | 생성된 PAM 설정 본문, `nsswitch.conf`, dconf 파일[10] |
| `/etc/pam.d/system-auth` 등, `/etc/nsswitch.conf` | 위 파일을 가리키는 심볼릭 링크[10] |
| `/usr/share/authselect/default`, `/usr/share/authselect/vendor` | 배포판이 싣는 프로필[10] |
| `/etc/authselect/custom` | 관리자가 만든 프로필[10] |
| `/usr/share/authselect/checksum`, `/var/lib/authselect/checksum` | 생성 파일의 체크섬 원본과 사본[10] |
| `/var/lib/authselect/backups/이름` | 설정을 바꾸기 전 백업(`-b` 면 이름은 그때 시각과 고유 문자열, `--backup=이름` 이면 지정한 이름)[10] |

### 한 줄의 모양

`/etc/pam.d/` 파일의 한 줄은 `type control module-path module-arguments` 이고, `/etc/pam.conf` 는 맨 앞에 서비스 이름이 하나 더 붙습니다. 앞 세 필드는 대소문자를 구분하지 않고, `#` 뒤는 주석이며, 줄 끝의 `\` 는 다음 줄로 잇습니다[1].

- **type**: `auth`(사용자 확인), `account`(계정 사용 허가), `password`(비밀번호 변경), `session`(세션 열기·닫기)입니다. 앞에 `-` 를 붙이면 모듈 파일이 없어 불러오지 못해도 syslog 에 남기지 않습니다[1].
- **control**: 단순형은 `required`, `requisite`, `sufficient`, `optional`, `include`, `substack` 이고, 대괄호형은 `[반환값=동작 ...]` 입니다. 동작은 `ignore`, `bad`, `die`, `ok`, `done`, `reset` 과 숫자 N(다음 N 개 모듈 건너뛰기)입니다[1].
- **module-path**: `/` 로 시작하면 전체 경로이고, 아니면 기본 모듈 폴더 기준의 상대 경로입니다[1].

단순형 네 가지는 대괄호형으로 이렇게 바꿔 읽을 수 있습니다[1].

| 단순형 | 대괄호형 | 뜻 |
|---|---|---|
| `required` | `[success=ok new_authtok_reqd=ok ignore=ignore default=bad]` | 실패해도 나머지를 다 돈 뒤 실패 |
| `requisite` | `[success=ok new_authtok_reqd=ok ignore=ignore default=die]` | 실패하면 그 자리에서 끝 |
| `sufficient` | `[success=done new_authtok_reqd=done default=ignore]` | 앞에 실패가 없고 이 모듈이 성공하면 그 자리에서 성공 |
| `optional` | `[success=ok new_authtok_reqd=ok default=ignore]` | 이 모듈만 있을 때만 결과에 영향 |

형식이 틀린 줄은 대개 인증을 실패시키는 쪽으로 동작하고 syslog 에 오류를 남깁니다[1].

### 로그 줄의 모양

모듈이 `pam_syslog` 로 남기는 줄은 모두 `모듈이름(서비스:동작):` 으로 시작하고, facility 는 `LOG_AUTHPRIV` 입니다. 동작 자리에는 `auth`, `setcred`, `account`, `session`, `chauthtok` 중 하나가 들어가고, 세션을 열 때와 닫을 때 모두 `session` 입니다[3]. pam_unix 가 남기는 주요 문구는 다음과 같습니다[5].

```
session opened for user %s(uid=%s) by %s(uid=%lu)
session closed for user %s
authentication failure; logname=%s uid=%d euid=%d tty=%s ruser=%s rhost=%s %s%s
%d more authentication failure%s; logname=%s uid=%d euid=%d tty=%s ruser=%s rhost=%s %s%s
check pass; user unknown
check pass; user (%s) unknown
bad username [%s]
user [%s] has blank password; authenticated without it
password changed for %s
```

세션 열기 줄의 `by` 뒤 이름은 로그인 이름이고 없으면 빈 문자열이며, 뒤의 uid 는 모듈을 부른 프로세스의 실제 UID 입니다. 앞쪽 `(uid=%s)` 는 계정 조회에 실패하면 `getpwnam error` 가 됩니다[5]. 인증 실패 줄의 마지막 `%s%s` 는 사용자 이름이 있을 때만 ` user=이름` 이 되므로, `rhost=` 값 뒤에 빈칸이 두 개 생깁니다[5]. `check pass; user (%s) unknown` 은 `audit` 옵션일 때만 입력된 이름을 적는데, 사용자가 이름 입력란에 비밀번호를 잘못 넣었으면 그 비밀번호가 로그에 남을 수 있습니다[5].

아래는 만든 예시입니다.

```
pam_unix(sudo:session): session opened for user root(uid=0) by alice(uid=1001)
pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=203.0.113.7  user=alice
```

`(uid=%s)` 를 세션 열기 줄에 넣은 커밋은 2019년 9월의 것이고, 그 전 판의 줄은 `session opened for user %s by %s(uid=%lu)` 입니다[6]. Ubuntu 24.04(1.5.3)와 RHEL 9(1.5.1)는 그 뒤 판입니다[11][12].

### 감사 로그에 남는 PAM 메시지

libpam 은 감사를 켜고 빌드했으면 PAM 단계마다 감사 레코드를 하나 씁니다. 메시지는 `PAM:동작 grantors=모듈,모듈` 모양이고, 계정·원격 호스트·터미널·성공 여부가 함께 들어갑니다[4]. RHEL 9 패키지는 감사를 켜고 빌드합니다[11]. 단계별 동작 문자열과 레코드 종류·번호는 다음과 같습니다[4][9].

| libpam 동작 | 메시지의 동작 문자열 | 감사 레코드 종류 |
|---|---|---|
| 인증 | `authentication` | `USER_AUTH` (1100) |
| 계정 확인 | `accounting` | `USER_ACCT` (1101) |
| 자격 설정 | `setcred` | `CRED_ACQ` (1103), `CRED_REFR` (1110), `CRED_DISP` (1104) |
| 세션 열기 | `session_open` | `USER_START` (1105) |
| 세션 닫기 | `session_close` | `USER_END` (1106) |
| 비밀번호 변경 | `chauthtok` | `USER_CHAUTHTOK` (1108) |

`grantors` 에는 결과를 허락한 모듈 이름이 쉼표로 이어지고, 실패했거나 허락한 모듈이 없으면 `?` 입니다. 사용자를 알 수 없으면 계정 자리도 `?` 입니다[4]. 레코드 필드의 뜻과 읽는 법은 [감사 로그 형식](../logging/auditd-format.md)에서 다룹니다.

### pam_faillock 실패 기록 파일

pam_faillock 은 사용자마다 실패 기록 파일을 하나 두고, 연속 실패가 기준을 넘으면 계정을 잠급니다[7]. 파일은 기본 폴더 `/var/run/faillock` 아래에 사용자 이름으로 만들고, 사용자 소유로 둡니다[7]. 설정은 `/etc/security/faillock.conf`(없으면 vendor 폴더의 같은 파일)에 두고, 기본값은 `deny=3`, `fail_interval=900`(15분), `unlock_time=600`(10분)입니다[7]. 배포판 파일에 어떤 값이 들어 있는지는 실제 시스템의 파일로 확인합니다.

파일은 64바이트 레코드를 이어 붙인 것입니다[7].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x00 | 52 | `source` | 원격 호스트, 없으면 터미널, 그것도 없으면 서비스 이름. NUL 로 끝난다는 보장이 없음 |
| 0x34 | 2 | `reserved` | 쓰지 않음 |
| 0x36 | 2 | `status` | `0x1` 유효, `0x2` source 가 원격 호스트, `0x4` source 가 터미널. 2·4 둘 다 없으면 서비스 이름 |
| 0x38 | 8 | `time` | 실패 시각, `time(NULL)` 로 얻은 epoch 초 |

코드는 구조체를 바이트 순서 변환 없이 그대로 읽고 씁니다[7]. 그래서 정수는 파일을 쓴 기계의 바이트 순서를 따르고, x86-64 기계면 리틀 엔디언으로 읽습니다. 레코드는 최대 1024 개까지 두고, 넘치면 파일 앞쪽의 레코드를 버립니다[7].

잠금과 관련된 줄은 `Consecutive login failures for user %s account temporarily locked`, `User %s is temporarily locked out due to %u consecutive failed login attempts` 모양이고, `audit` 옵션이면 없는 사용자 이름을 `User unknown: %s` 로 남깁니다[7]. 감사 로그에는 `ANOM_LOGIN_FAILURES`(2100), `RESP_ACCT_LOCK`(2207), `RESP_ACCT_UNLOCK_TIMED`(2206) 레코드가 남습니다[7][9].

## 읽는 법

### 헥스로 한 번

아래는 위 표대로 만든 레코드 하나입니다(명세로 만든 예시, 리틀 엔디언). 원격 호스트 `192.0.2.10` 에서 실패한 기록이라 `status` 가 `0x0003`(유효 + 원격 호스트)이고, 0x38 의 `80 3b b1 6a 00 00 00 00` 은 `0x6AB13B80` = 1790000000 초 = 2026-09-21 14:13:20 UTC 입니다.

```
00000000: 3139 322e 302e 322e 3130 0000 0000 0000  192.0.2.10......
00000010: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000030: 0000 0000 0000 0300 803b b16a 0000 0000  .........;.j....
```

`status` 에 `0x1` 이 빠진 레코드도 파일에 남아 있을 수 있습니다. 새 실패를 기록할 때 `fail_interval` 보다 오래된 레코드는 유효 비트만 지우고, 가장 오래된 레코드가 무효일 때만 그 레코드를 덮어쓰기 때문입니다[7]. 무효 레코드의 `source`·`time` 도 과거 실패의 흔적으로 읽을 수 있습니다.

### 순서대로 한 번

1. 판과 배포판을 확인합니다. `/etc/os-release` 와 패키지 기록에서 pam 판을 보고([배포판과 버전](../../02-artifacts/system-info/os-release.md)), 로그 줄 모양이 그 판과 맞는지 봅니다.
2. 조사할 서비스(예: `sshd`, `login`, `sudo`, `su`, 화면 잠금)의 파일을 `/etc/pam.d/` 에서 찾고, 없으면 `/usr/lib/pam.d/` 와 vendor 폴더에서 찾습니다. 그래도 없으면 `other` 가 쓰입니다[1].
3. `include`·`substack` 줄을 따라가 공통 파일(`common-*` 또는 `system-auth`·`password-auth`)을 펼쳐, type 별로 실제로 도는 모듈 순서를 한 목록으로 만듭니다[1]. RHEL 에서는 심볼릭 링크를 따라 `/etc/authselect/` 의 본문을 읽습니다[10].
4. 대괄호형 control 의 숫자 N 과 `sufficient`·`requisite` 를 반영해, 어떤 조건에서 어떤 모듈이 건너뛰어지는지 적습니다. 상류 authselect 프로필은 `session [success=1 default=ignore] pam_succeed_if.so service in crond quiet use_uid` 다음 줄에 `session required pam_unix.so` 를 두므로, 이 설정이면 crond 세션에는 pam_unix 세션 줄이 남지 않습니다[10].
5. 모듈 경로가 절대 경로인 줄, 표준 모듈 폴더 밖을 가리키는 줄, `pam_exec`·`pam_permit` 줄을 따로 뽑습니다(아래 함정).
6. 모듈 옵션 가운데 로그 양을 바꾸는 것(`quiet`, `debug`, `audit`, `no_log_info`)을 적어 둡니다. 이 목록이 "왜 이 줄이 없나" 에 대한 답이 됩니다[5][7].
7. 설정 파일과 모듈 파일이 패키지 원본과 같은지 확인합니다([패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md)). RHEL 라이브 시스템이면 `authselect check` 가 `Current authselect configuration is valid.`, `System was not configured with authselect.`, `No configuration detected.` 가운데 하나를 내고, 어긋나면 오류 목록을 냅니다[10].

## 포렌식에서 중요한 점

### 증명하는 것

- 수집 시점의 설정 파일은 그때 각 서비스가 어떤 모듈을 어떤 순서·옵션으로 부르게 돼 있었는지를 보여 줍니다[1].
- `pam_unix(서비스:session)` 열기·닫기 줄은 그 서비스가 그 계정으로 세션을 열고 닫았다는 기록입니다[5].
- 감사 로그의 `grantors` 는 그 단계에서 결과를 허락한 모듈 이름을 보여 줍니다[4]. 평소와 다른 모듈(예: `pam_permit`)이 허락했다면 설정을 다시 봅니다. pam_permit 은 아무것도 확인하지 않고 늘 허용하는 모듈이라, 인증 스택에 들어 있으면 그 자리는 무조건 통과합니다[8].
- faillock 레코드는 그 계정의 최근 인증 실패 시각과 출발지(원격 호스트·터미널·서비스)를 보여 줍니다[7].

### 증명하지 못하는 것

- 지금 설정 파일은 과거 어느 시점의 설정을 증명하지 않습니다. 파일 시각, 패키지 원본, authselect 백업, `pam-auth-update` 틀과 맞춰 봐야 합니다.
- 세션 줄만으로는 비밀번호로 들어왔는지 키로 들어왔는지 알 수 없습니다. sshd 자체의 줄과 함께 봅니다([SSH](../../02-artifacts/logins/ssh/index.md)).
- `grantors` 에 늘 보이던 모듈 이름만 있다고 해서 그 모듈 파일이 원본이라는 뜻은 아닙니다. 모듈 파일 변조는 파일 해시로 따로 확인합니다([PAM 모듈 변조](../../02-artifacts/persistence/pam-backdoor.md)).
- faillock 파일이 비어 있거나 없다고 실패가 없었던 것은 아닙니다. 인증에 성공해 `authsucc` 단계나 account 단계의 pam_faillock 을 지나면 파일을 0 바이트로 자르고, 기본 폴더가 메모리 파일 시스템이면 재부팅 때 사라집니다[7].

### 시각 해석

| 시각 | 무엇이 바뀔 때 바뀌나 | 기준 |
|---|---|---|
| 인증 로그 줄의 시각 | 모듈이 줄을 남길 때 | syslog 형식에 따름([인증 로그](../../02-artifacts/logins/auth-log.md), [syslog 형식과 rsyslog](../logging/syslog-rsyslog.md)) |
| 감사 레코드의 시각 | libpam 이 각 단계를 마칠 때 | epoch 초(UTC)([감사 로그 형식](../logging/auditd-format.md)) |
| faillock 레코드의 `time` | 인증 실패를 기록할 때 | epoch 초(UTC)[7]([Linux 의 시각 값](../value-decoding/time-values.md)) |
| faillock 파일의 mtime | 실패를 기록하거나 성공으로 파일을 자를 때 | 파일 시스템 시각 |
| `/etc/pam.d/` 파일의 mtime | 편집기·패키지·`pam-auth-update` 가 파일을 새로 쓸 때 | 파일 시스템 시각 |
| authselect 백업 폴더 이름 | 프로필·기능을 바꾸기 직전(`-b` 로 이름 없이 만들 때) | 이름에 그때 시각이 들어감[10] |

### 지운 데이터·손상

faillock 은 성공한 인증 뒤 파일을 0 바이트로 자르므로(`ftruncate`)[7], 지워진 레코드는 파일 안에서 찾을 수 없습니다. 기본 폴더가 디스크가 아니라 메모리에 있다면 전원을 끈 이미지에는 이 폴더가 비어 있으므로, 라이브 수집이나 메모리 분석에서 챙깁니다. 설정 파일은 평문이라 서명이 없고, 고친 사람을 파일 안에서 알 수 없습니다.

## 함정

- **include 를 펼치지 않으면 틀립니다.** 서비스 파일 하나만 보고 "이 서비스는 pam_unix 만 쓴다" 고 판단하면, 공통 파일에 들어 있는 다른 모듈을 놓칩니다[1].
- **줄 순서가 곧 실행 순서는 아닙니다.** 대괄호형의 숫자 N 은 다음 N 개 모듈을 건너뛰고, `sufficient` 성공이나 `requisite` 실패는 그 자리에서 스택을 끝냅니다[1].
- **`-` 가 붙은 줄은 조용합니다.** 모듈 파일이 없어도 로그가 남지 않으므로, 지정된 모듈이 실제로 있는지 모듈 폴더에서 확인합니다[1].
- **로그가 없는 이유가 설정일 수 있습니다.** pam_unix 에 `quiet` 가 있으면 세션 열기·닫기 줄을 남기지 않고[5], pam_faillock 에 `no_log_info` 가 있으면 알림 로그를 남기지 않습니다[7].
- **절대 경로 모듈을 따로 봅니다.** `/` 로 시작하는 module-path 는 표준 모듈 폴더 밖의 파일도 불러옵니다[1]. 흔적을 찾는 방법은 [PAM 모듈 변조](../../02-artifacts/persistence/pam-backdoor.md)에서 다룹니다.
- **pam_exec 줄은 인자에 답이 있습니다.** pam_exec 은 외부 명령을 실행하면서 `PAM_RHOST`, `PAM_RUSER`, `PAM_SERVICE`, `PAM_TTY`, `PAM_USER`, `PAM_TYPE` 을 환경 변수로 넘기고, `expose_authtok` 이 있으면 인증·비밀번호 변경 때 명령이 표준 입력으로 비밀번호를 받습니다. `log=파일` 이 있으면 명령 출력이 그 파일에 덧붙고, 없으면 출력은 `/dev/null` 로 갑니다[8]. 그래서 줄의 인자에서 실행 파일 경로와 출력 파일 경로를 읽고 그 파일들을 모읍니다.
- **pam_loginuid 가 없는 진입점은 로그인 UID 를 정하지 않습니다.** pam_loginuid 는 login, sshd, gdm, crond 같은 진입점에서 감사용 로그인 UID 를 정합니다. sudo·su 에 넣으면 로그인 UID 가 전환한 계정으로 바뀌어 버리므로 진입점에만 씁니다[8]. 감사 로그의 `auid` 를 사람과 잇기 전에 그 진입점 설정에 이 모듈이 있는지 봅니다.
- **pam_tty_audit 은 키 입력을 감사 로그에 남깁니다.** 설정된 사용자의 터미널 입력을 커널 감사로 보내고, `log_passwd` 가 있으면 비밀번호 입력 중의 키도 남깁니다[8]. 이 모듈이 켜진 시스템에서는 감사 로그에 사용자의 키 입력이 있을 수 있으니 다룰 때 주의합니다.
- **RHEL 의 공통 파일은 링크입니다.** 링크만 복사하는 수집은 본문이 빠지므로 `/etc/authselect/` 까지 모읍니다[10].
- **`/etc/pam.conf` 가 있다고 쓰이는 것은 아닙니다.** Ubuntu 패키지는 `/etc/pam.conf` 를 설치하지만[12], `/etc/pam.d/` 가 있으면 읽지 않습니다[1].

## 도구

- **수집**: ForensicArtifacts 의 `LinuxPamConfigs` 는 `/etc/pam.conf`, `/etc/pam.d`, `/etc/pam.d/*` 를 모으고[13], `/etc/security/`, `/usr/lib/pam.d`, `/usr/share/pam.d`, `/etc/authselect/`, 모듈 파일은 들어 있지 않으므로 따로 모읍니다. UAC 는 `/etc` 전체를 모으고 shadow 류만 뺍니다[14]. 모듈 폴더와 `/var/lib/authselect/` 는 어느 쪽이든 따로 챙깁니다.
- **로그 파싱**: dissect.target 의 인증 로그 플러그인은 pam_unix 세션 줄을 정규식으로 나눕니다[15]. 정규식의 `by` 부분은 `by (uid=숫자)` 처럼 이름이 빈 모양만 받고 줄 끝(`$`)까지 맞아야 하므로, `by alice(uid=1001)` 처럼 이름이 있는 줄은 정규식이 맞지 않아 사용자·uid 필드가 모두 비어 나옵니다. 이런 줄은 원문을 직접 읽습니다.
- **실패 기록**: 라이브 시스템에서는 `faillock` 명령으로 사용자별 기록을 보고, `--dir` 로 다른 폴더를 지정할 수 있습니다[7]. 이미지에서는 위 레코드 표대로 헥스 편집기나 짧은 스크립트로 읽습니다.
- **설정 확인**: RHEL 라이브 시스템에서는 `authselect check` 로 생성본과 지금 파일이 맞는지 봅니다[10]. 설정 파일은 평문이라 텍스트 도구로 읽습니다.
- 인증 로그 전체를 해석하는 방법은 [인증 로그](../../02-artifacts/logins/auth-log.md), sudo 설정은 [sudo 설정](sudoers.md), 계정 파일은 [계정 파일](passwd-shadow-group.md)에서 다룹니다.

## 참고 문헌

1. Linux-PAM, pam.conf(5) 원본 `doc/man/pam.conf-desc.xml`·`pam.conf-dir.xml`·`pam.conf-syntax.xml`·`pam.conf.5.xml`. https://github.com/linux-pam/linux-pam/tree/master/doc/man
2. Linux-PAM, pam(8) 원본 `doc/man/pam.8.xml`. https://github.com/linux-pam/linux-pam/blob/master/doc/man/pam.8.xml
3. Linux-PAM, `libpam/pam_syslog.c`. https://github.com/linux-pam/linux-pam/blob/master/libpam/pam_syslog.c
4. Linux-PAM, `libpam/pam_audit.c`. https://github.com/linux-pam/linux-pam/blob/master/libpam/pam_audit.c
5. Linux-PAM, `modules/pam_unix/`(`pam_unix.8.xml`, `pam_unix_sess.c`, `pam_unix_auth.c`, `support.c`, `passverify.c`). https://github.com/linux-pam/linux-pam/tree/master/modules/pam_unix
6. Linux-PAM, 커밋 71dafa6d49(2019-09-09, 세션 줄에 uid 추가). https://github.com/linux-pam/linux-pam/commit/71dafa6d49
7. Linux-PAM, `modules/pam_faillock/`(`pam_faillock.8.xml`, `faillock.conf.5.xml`, `faillock.8.xml`, `faillock.h`, `faillock.c`, `pam_faillock.c`). https://github.com/linux-pam/linux-pam/tree/master/modules/pam_faillock
8. Linux-PAM, `modules/pam_exec/pam_exec.8.xml`, `pam_permit/pam_permit.8.xml`, `pam_tty_audit/pam_tty_audit.8.xml`, `pam_loginuid/pam_loginuid.8.xml`. https://github.com/linux-pam/linux-pam/tree/master/modules
9. Linux Audit, `specs/messages/message-dictionary.csv`. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
10. authselect, `src/man/authselect.8.adoc`, `src/conf_macros.m4`, `src/lib/paths.h`, `profiles/local/system-auth`. https://github.com/authselect/authselect
11. CentOS Stream 9 pam 패키지, `pam.spec`. https://gitlab.com/redhat/centos-stream/rpms/pam/-/blob/c9s/pam.spec
12. Ubuntu 24.04(noble) pam 패키지, `debian/rules`, `libpam-modules.install`, `libpam-runtime.install`, `changelog`. https://git.launchpad.net/ubuntu/+source/pam/tree/debian?h=ubuntu/noble
13. ForensicArtifacts, `artifacts/data/linux.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
14. UAC, `artifacts/files/system/etc.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/files/system/etc.yaml
15. dissect.target, `plugins/os/unix/log/auth.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/auth.py
