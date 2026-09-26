---
title: "PAM 모듈 변조"
parent: "아티팩트 · 지속성"
nav_order: 570
---

# PAM 모듈 변조 (PAM Backdoor)

PAM 설정 줄을 바꾸거나 모듈 파일(`.so`)을 바꿔치기하면 로그인·sudo 같은 인증 과정에 끼어들 수 있으므로, `/etc/pam.d/` 의 줄과 모듈 폴더의 파일을 패키지 원본·로그와 맞춰 봐서 변조 흔적을 찾습니다.

## 무엇을 기록하나 · 왜 생기나

PAM (Pluggable Authentication Modules) 은 login·sshd·sudo 같은 프로그램이 인증과 세션 처리를 설정 파일에 적힌 모듈에 맡기는 구조입니다. 설정 파일의 한 줄 모양, 공통 파일, 로그 줄은 [인증 모듈 (PAM)](../../01-foundations/users-auth/pam.md)에서 다루고, 이 쪽은 그 구조가 지속성 수단으로 바뀌었을 때 남는 흔적만 다룹니다.

libpam 은 PAM 처리를 시작할 때마다(핸들마다) 설정 파일을 읽고, 줄에 적힌 모듈 파일을 불러와 그 안의 `pam_sm_authenticate`, `pam_sm_open_session` 같은 함수를 부릅니다[2]. 그래서 설정 줄 하나나 모듈 파일 하나만 바꿔도 그 서비스로 로그인할 때마다 바뀐 코드가 돌고, 따로 실행 흔적을 남기는 데몬이 없습니다. 변조는 크게 세 모양으로 나뉩니다.

| 모양 | 바뀌는 곳 | 먼저 볼 것 |
|---|---|---|
| 설정 줄 추가·수정 | `/etc/pam.d/서비스이름`, 공통 파일 | 늘 성공하는 모듈, 외부 명령을 부르는 모듈, 표준 폴더 밖 경로 |
| 모듈 파일 교체 | 모듈 폴더의 기존 `.so` | 패키지 기준값과 해시 대조 |
| 모듈 파일 추가 | 모듈 폴더나 다른 폴더의 새 `.so` | 어느 패키지에도 속하지 않는 파일 |

## 위치와 버전별 차이

서비스 설정은 `/etc/pam.d/` 에 서비스마다 한 파일로 있고, 배포판이 싣는 기본 파일은 `/usr/lib/pam.d/` 나 빌드할 때 정한 폴더(RHEL 9 는 `/usr/share/pam.d/`)에 있을 수 있으며, 같은 이름이면 `/etc/pam.d/` 쪽이 이깁니다[1][6]. 설정 줄의 모듈 경로가 `/` 로 시작하지 않으면 기본 모듈 폴더에서 찾습니다. 문서의 기본값은 `/lib/security/` 나 `/lib64/security/` 이지만, 배포판은 빌드할 때 정한 폴더를 씁니다[1][5][6].

| 항목 | Ubuntu 24.04 (pam 1.5.3) | RHEL 9 (pam 1.5.1) |
|---|---|---|
| 모듈 폴더 | `/usr/lib/멀티아키텍처이름/security/`(amd64 는 `x86_64-linux-gnu`)[5] | `/usr/lib64/security/`(`%{_libdir}/security`)[6] |
| 기본 모듈의 소속 패키지 | libpam-modules(`usr/lib/*/security/*.so`)[5] | pam(파일 목록에 모듈을 하나씩 적음)[6] |
| 모듈 폴더의 정상 심볼릭 링크 | 검체에서 확인 | `pam_unix_auth.so`·`pam_unix_acct.so`·`pam_unix_passwd.so`·`pam_unix_session.so` → `pam_unix.so`[6] |
| 공통 파일을 끌어오는 줄 | `@include common-auth` 모양[7] | `auth substack password-auth`, `account include password-auth` 모양[8] |
| sshd 의 사용자 환경 파일 | `pam_env.so user_readenv=1 envfile=/etc/default/locale` 줄이 있어 `$HOME/.pam_environment` 를 읽음[4][7] | sshd 파일에 pam_env 줄이 없음. 끌어오는 공통 파일에 있는지 검체에서 확인[8] |

pam 패키지 밖의 프로그램도 모듈을 싣습니다. 예를 들어 gnome-keyring 은 `pam_sm_authenticate`·`pam_sm_open_session` 이 들어 있는 자체 모듈을 만듭니다[13]. 그래서 모듈 폴더의 파일이 pam 패키지 소속이 아니라는 사실만으로는 이상하다고 할 수 없고, 설치된 모든 패키지의 파일 목록과 맞춰 봐야 합니다.

pam_env 는 `/etc/security/pam_env.conf`, `/etc/environment` 와 옵션에 따라 사용자 홈의 `.pam_environment` 를 읽어 로그인 환경 변수를 넣습니다[4]. 이 경로로 들어간 변수가 무엇을 바꾸는지는 [공유 라이브러리 가로채기](ld-preload.md)와 [셸 시작 파일](shell-startup.md)에서 다룹니다.

## 구조

### 눈여겨볼 설정 줄

아래 줄 모양이 보이면 그 줄이 배포판 원본에 있던 것인지부터 확인합니다. 줄은 모두 만든 예시입니다.

| 줄 모양(만든 예시) | 눈여겨보는 까닭 |
|---|---|
| `auth sufficient pam_permit.so` | pam_permit 은 아무것도 확인하지 않고 늘 `PAM_SUCCESS` 를 돌려줍니다[4]. `sufficient` 는 앞의 required 모듈이 실패하지 않았고 이 모듈이 성공하면 그 자리에서 스택을 성공으로 끝냅니다[1]. auth 스택 앞쪽에 이 조합이 있으면 뒤의 비밀번호 확인까지 가지 않습니다 |
| `pam_exec.so` 줄에 `expose_authtok` 이나 `log=` 인자가 있음 | pam_exec 은 외부 명령을 실행하고, `expose_authtok` 이 있으면 인증·비밀번호 변경 때 그 명령이 표준 입력으로 비밀번호를 읽습니다. `log=` 파일에는 명령 출력이 덧붙습니다[4] |
| `session optional /opt/lib/pam_unix.so` | `/` 로 시작하는 모듈 경로는 기본 모듈 폴더 밖의 파일을 불러옵니다[1] |
| `-auth optional pam_foo.so` | type 앞의 `-` 는 모듈 파일을 불러오지 못해도 syslog 에 남기지 않게 합니다[1][2] |

pam_exec 명령은 기본으로 부른 프로세스의 실제 UID 로 돌고, `seteuid` 가 있으면 유효 UID 로 돕니다. `log=` 도 `stdout` 도 없으면 출력은 `/dev/null` 로 갑니다[4]. 따라서 pam_exec 줄에서는 명령 경로와 `log=` 경로를 뽑아 두 파일을 모두 모읍니다.

### 모듈 이름과 실제 파일

libpam 은 모듈 경로에서 마지막 `/` 뒤를 떼고, 마지막 `.` 앞까지를 모듈 이름으로 씁니다[2]. 로그 줄 앞머리 `모듈이름(서비스:동작):` 와 감사 레코드의 `grantors=` 가 모두 이 이름을 씁니다[2][3]. 그래서 `/opt/lib/pam_unix.so` 를 부르는 줄도 로그와 감사 레코드에는 표준 모듈과 똑같이 `pam_unix` 로 찍힙니다. 이름만 보고 표준 모듈이 돌았다고 판단하지 말고, 설정 줄의 경로와 그 경로 파일의 해시를 확인합니다.

### 로그에 남는 흔적

감사를 켜고 빌드한 libpam 은 단계마다 `PAM:동작 grantors=모듈,모듈` 모양의 감사 메시지를 남기고, `grantors` 에는 결과를 허락한 모듈 이름이 쉼표로 이어집니다. 실패했거나 허락한 모듈이 없으면 `?` 입니다[3]. 평소 `pam_unix` 가 있던 자리에 `pam_permit` 이나 처음 보는 이름이 나오면 그 시점의 설정을 의심할 근거가 됩니다. 레코드 종류와 필드는 [인증 모듈 (PAM)](../../01-foundations/users-auth/pam.md)과 [감사 로그 형식](../../01-foundations/logging/auditd-format.md)에서 다룹니다.

모듈 파일을 불러올 수 없거나 모듈 안에 필요한 함수가 없으면 libpam 이 syslog 에 다음 문구를 남깁니다[2].

```
unable to dlopen(%s): %s
adding faulty module: %s
unable to resolve symbol: %s
```

첫 두 줄의 `%s` 는 불러오려던 모듈의 전체 경로(상대 경로면 기본 모듈 폴더를 앞에 붙인 경로)이고, type 앞에 `-` 가 있는 줄이면 불러오지 못해도 이 두 줄을 남기지 않습니다[2]. 변조 도중 잘못 만든 모듈이나 지운 모듈이 이 줄로 드러날 수 있으므로 인증 로그에서 이 문구를 찾아봅니다([인증 로그](../logins/auth-log.md)).

## 증거로서 의미

### 증명하는 것

- 수집 시점의 설정 파일은 그때 각 서비스가 어떤 모듈 경로를 어떤 control 과 인자로 부르게 돼 있었는지를 보여 줍니다[1].
- 패키지 기준값과 해시가 다른 모듈 파일은 설치된 뒤에 내용이 바뀐 것입니다. 대조 방법은 [패키지 파일 변조 확인](../packages/package-verify.md)에서 다룹니다.
- 감사 레코드의 `grantors` 는 그 단계를 허락한 모듈 이름을 보여 줍니다[3].
- `unable to dlopen` 줄은 그 시각에 설정이 그 경로의 모듈을 부르고 있었다는 기록입니다[2].

### 증명하지 못하는 것

- 지금 설정은 과거 어느 시점의 설정을 증명하지 않습니다. 설정 파일은 관리자가 바꾸는 것이 보통이라, 바뀌었다는 사실만으로 악성이라고 할 수 없습니다.
- 어느 패키지에도 속하지 않은 새 `.so` 는 `dpkg -V`·`rpm -V` 결과에 나오지 않습니다. 모듈 폴더의 파일 목록을 패키지 파일 목록과 따로 맞춰 봐야 합니다([패키지 파일 변조 확인](../packages/package-verify.md)).
- `grantors` 에 늘 보던 이름만 있다고 그 파일이 원본이라는 뜻은 아닙니다. 이름은 경로의 파일 이름에서 나오기 때문입니다[2].
- 설정 줄이 있다고 그 서비스로 실제 로그인이 있었다는 뜻은 아닙니다. 실행 여부는 로그·감사 레코드로 따로 확인합니다.
- pam_exec 로 비밀번호가 넘어갔다고 해도 설정 줄만으로는 넘어간 값이 어디에 남았는지 알 수 없습니다. `log=` 파일과 명령이 쓰는 파일을 따로 찾습니다.

## 시각 해석

| 시각 | 무엇이 바뀔 때 바뀌나 | 기준 |
|---|---|---|
| `/etc/pam.d/` 파일의 mtime | 편집기·패키지·`pam-auth-update`·authselect 가 내용을 새로 쓸 때 | 파일 시스템 시각(epoch, UTC 로 저장) |
| 모듈 `.so` 의 mtime | 내용을 쓸 때, 그리고 `utime` 류 호출로 임의 값으로 바꿀 때[11] | 같음 |
| 모듈 `.so` 의 ctime | 내용을 쓰거나 소유자·권한·링크 수를 바꿀 때[11] | 같음 |
| 모듈 폴더의 mtime | 폴더 안에 파일을 만들거나 지울 때[11] | 같음 |
| 감사 레코드 시각 | libpam 이 각 단계를 마칠 때 | epoch 초, UTC([감사 로그 형식](../../01-foundations/logging/auditd-format.md)) |
| syslog 줄 시각 | 줄을 남길 때 | 전통 형식은 연도·시간대가 없음([syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)) |

바꿔치기한 모듈의 mtime 을 원본과 같게 맞춰 두어도 ctime 은 그때 시각으로 바뀝니다[11]. 그래서 mtime 은 원본 패키지 설치 무렵인데 ctime 만 늦은 모듈 파일을 먼저 봅니다. RHEL 이면 rpm 헤더에 적힌 원래 mtime 과도 견줄 수 있습니다([패키지 파일 변조 확인](../packages/package-verify.md)). 파일 시스템 시각을 읽는 법은 [ext4](../../01-foundations/filesystem/ext4/index.md)와 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)을 봅니다.

## 함정과 한계

- **서비스 파일 하나만 보면 놓칩니다.** `@include`·`include`·`substack` 으로 공통 파일이 끼어들기 때문에[1][7][8], 변조는 서비스 파일이 아니라 `common-auth` 나 `password-auth` 에 있을 수 있습니다. RHEL 의 공통 파일은 `/etc/authselect/` 를 가리키는 링크라 본문도 따로 모읍니다([인증 모듈 (PAM)](../../01-foundations/users-auth/pam.md)).
- **이름이 같다고 같은 파일이 아닙니다.** 앞의 "모듈 이름과 실제 파일" 절에서 본 것처럼, 표준 모듈과 이름이 같은 다른 경로의 파일도 로그에는 같은 이름으로 찍힙니다[2].
- **`-` 줄은 조용합니다.** 모듈을 지우거나 이름을 바꿔도 로그가 남지 않습니다[1][2].
- **수집 목록에 모듈 폴더가 없습니다.** ForensicArtifacts 의 `LinuxPamConfigs` 는 `/etc/pam.conf`, `/etc/pam.d`, `/etc/pam.d/common-password`, `/etc/pam.d/*` 만 정의하고[9], UAC 는 `/etc` 와 `/usr/local/etc` 를 모으므로 모듈 폴더와 배포판 기본 설정 폴더(`/usr/lib/pam.d`, `/usr/share/pam.d`)는 들어 있지 않습니다[10]. 모듈 폴더, pam_exec 이 부르는 파일, `log=` 파일, 사용자 홈의 `.pam_environment` 는 따로 모읍니다.
- **라이브 시스템의 검사 도구를 믿지 않습니다.** `dpkg`, `rpm`, `md5sum` 이 쓰는 라이브러리부터 바뀌었을 수 있으므로 이미지를 분석 PC 에 마운트해 검사합니다.
- **지운 모듈은 메모리에 남을 수 있습니다.** 모듈을 불러온 프로세스가 살아 있는 동안 `/proc/PID/maps` 에 그 파일 경로가 보이고, 파일이 지워졌으면 경로 뒤에 ` (deleted)` 가 붙습니다[12]. libpam 은 `pam_end` 로 핸들을 닫을 때 불러온 모듈을 `dlclose` 로 내려놓으므로[2] 세션이 끝난 뒤에는 보이지 않을 가능성이 있습니다. 메모리 분석은 [메모리 분석](../../03-techniques/analysis/memory-analysis.md)을 봅니다.

## 직접 분석해 보기

### 손으로 한 번

검체를 `/mnt/evidence` 에 읽기 전용으로 마운트했다고 둡니다. 먼저 모든 설정 파일에서 모듈 경로를 뽑아, 절대 경로와 눈여겨볼 모듈을 골라냅니다.

```
$ grep -HnE '^[[:space:]]*-?[a-z]+[[:space:]]' /mnt/evidence/etc/pam.d/* \
    | grep -E 'pam_permit|pam_exec|[[:space:]]/[^[:space:]]+\.so'
/mnt/evidence/etc/pam.d/common-auth:17:auth optional /opt/lib/pam_unix.so
```

위 출력은 만든 예시입니다. 다음으로 그 파일이 ELF 파일이고 PAM 진입 함수 이름이 들어 있는지 봅니다. ELF 파일은 첫 4바이트가 `7f 45 4c 46`(`\x7fELF`)이고, 다섯째 바이트 `02` 는 64비트, 여섯째 바이트 `01` 은 리틀 엔디언입니다[14][15]. 헥스 덤프로 이 값을 확인한 뒤 문자열에서 `pam_sm_` 로 시작하는 함수 이름을 찾습니다. libpam 이 모듈에서 찾는 함수 이름이 이것들입니다[2].

```
$ xxd -l 16 /mnt/evidence/opt/lib/pam_unix.so
00000000: 7f45 4c46 0201 0100 0000 0000 0000 0000  .ELF............
$ strings /mnt/evidence/opt/lib/pam_unix.so | grep '^pam_sm_'
pam_sm_authenticate
pam_sm_setcred
```

위 출력은 ELF 머리 규칙으로 만든 예시입니다. 표준 폴더의 같은 이름 파일과 해시를 견주고, `stat` 으로 mtime·ctime 을 읽어 앞의 시각 표와 맞춥니다.

### 공개 도구로 한 번

- `dpkg --root=/mnt/evidence -V` 또는 `rpm --root /mnt/evidence -Va --noscripts` 로 모듈 폴더와 `/etc/pam.d/` 가 결과에 나오는지 봅니다. 결과 읽는 법과 주의점은 [패키지 파일 변조 확인](../packages/package-verify.md)에 있습니다.
- 모듈 폴더의 파일마다 `dpkg -S` 나 `rpm -q -f` 로 소속 패키지를 찾고, 소속이 없는 파일을 따로 적습니다. Debian 계열은 `/var/lib/dpkg/info/*.list` 를 직접 grep 해도 됩니다([dpkg·apt 기록](../packages/dpkg-apt.md)).
- 소속이 없는 파일이나 해시가 다른 파일은 [알려진 파일 대조와 YARA](../../03-techniques/analysis/hash-yara.md)로 넘깁니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [패키지 파일 변조 확인](../packages/package-verify.md) | 설정·모듈 파일이 패키지 기준값과 같은가 |
| [dpkg·apt 기록](../packages/dpkg-apt.md)·[rpm·dnf·yum 기록](../packages/rpm-dnf.md) | 바뀐 파일의 시각이 마지막 pam 패키지 설치·업그레이드 뒤인가 |
| [인증 로그](../logins/auth-log.md) | `unable to dlopen` 줄, 변조 시각 앞뒤의 로그인 성공·실패 |
| [감사 로그 형식](../../01-foundations/logging/auditd-format.md) | `grantors` 에 평소와 다른 모듈 이름이 나오는가 |
| [셸 명령 기록](../execution/shell-history/index.md) | 설정 파일 편집, 모듈 폴더로 복사, `touch` 로 시각을 맞춘 명령 |
| [공유 라이브러리 가로채기](ld-preload.md) | `.pam_environment`·pam_env 설정으로 넣은 환경 변수 |
| [타임라인 만들기](../../03-techniques/analysis/timeline.md) | 설정·모듈 파일의 ctime 앞뒤로 무엇이 있었는가 |

지속성 전반의 순서는 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md)에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 검체 모음에서 Ubuntu 나 RHEL 계열 서버 이미지를 골라 풀어 봅니다.

1. sshd 가 실제로 도는 auth 스택을 `include` 를 모두 펼쳐 한 목록으로 적으면 모듈이 몇 개이고, 그중 절대 경로로 불리는 모듈이 있는가?
2. 모듈 폴더의 파일 가운데 어느 패키지에도 속하지 않는 파일이 있는가?
3. 모듈 파일 가운데 ctime 이 mtime 보다 한참 늦은 파일이 있는가, 그 ctime 은 pam 패키지의 마지막 설치 시각보다 뒤인가?
4. 감사 로그가 있다면 `USER_AUTH` 레코드의 `grantors` 값은 몇 가지이고, 드물게 나온 값은 언제 처음 나타나는가?
5. 인증 로그에 `unable to dlopen` 이나 `adding faulty module` 줄이 있는가, 있다면 그 경로의 파일은 지금 검체에 있는가?

## 참고 문헌

1. Linux-PAM, pam.conf(5) 원본 `doc/man/pam.conf-syntax.xml`·`pam.conf-dir.xml`. https://github.com/linux-pam/linux-pam/tree/master/doc/man
2. Linux-PAM, `libpam/pam_handlers.c`, `pam_syslog.c`, `pam_dispatch.c`, `pam_start.c`, `pam_end.c`. https://github.com/linux-pam/linux-pam/tree/master/libpam
3. Linux-PAM, `libpam/pam_audit.c`. https://github.com/linux-pam/linux-pam/blob/master/libpam/pam_audit.c
4. Linux-PAM, `modules/pam_permit/pam_permit.8.xml`, `pam_exec/pam_exec.8.xml`, `pam_env/pam_env.8.xml`. https://github.com/linux-pam/linux-pam/tree/master/modules
5. Ubuntu 24.04(noble) pam 패키지, `debian/rules`, `libpam-modules.install`, `changelog`. https://git.launchpad.net/ubuntu/+source/pam/tree/debian?h=ubuntu/noble
6. CentOS Stream 9 pam 패키지, `pam.spec`. https://gitlab.com/redhat/centos-stream/rpms/pam/-/blob/c9s/pam.spec
7. Ubuntu 24.04(noble) openssh 패키지, `debian/openssh-server.sshd.pam.in`. https://git.launchpad.net/ubuntu/+source/openssh/tree/debian?h=ubuntu/noble-updates
8. CentOS Stream 9 openssh 패키지, `sshd.pam`. https://gitlab.com/redhat/centos-stream/rpms/openssh/-/tree/c9s
9. ForensicArtifacts, `artifacts/data/linux.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
10. UAC, `artifacts/files/system/etc.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/files/system/etc.yaml
11. Linux man-pages, inode(7). https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
12. Linux man-pages, proc(5). https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
13. gnome-keyring, `pam/gkr-pam-module.c`. https://github.com/GNOME/gnome-keyring/blob/main/pam/gkr-pam-module.c
14. Linux man-pages, elf(5). https://github.com/mkerrisk/man-pages/blob/master/man5/elf.5
15. Linux 커널, `include/uapi/linux/elf.h`. https://github.com/torvalds/linux/blob/master/include/uapi/linux/elf.h
