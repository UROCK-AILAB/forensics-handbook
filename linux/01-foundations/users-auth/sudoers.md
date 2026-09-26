---
title: "sudo 설정"
parent: "기반 · 사용자와 인증 구조"
nav_order: 160
---

# sudo 설정 (sudoers)

sudo 는 `/etc/sudoers` 와 그 파일이 끌어오는 `/etc/sudoers.d/` 안의 규칙으로 "누가 어느 호스트에서 누구 권한으로 무엇을 실행할 수 있는지" 정하고, 같은 설정 파일에서 사용 기록을 어디에 어떤 모양으로 남길지도 정합니다.

이 페이지는 설정 파일의 위치, 줄 문법, 파일을 읽는 순서, 배포판 기본 파일, 기록을 좌우하는 설정 키까지 다룹니다. sudo 를 실제로 쓴 기록(허용·거부 줄, I/O 기록, 시간 기록 파일, 강의 파일)의 해석은 [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md)에 있습니다. sudoers 가 가리키는 사용자·그룹은 [계정 파일 (passwd·shadow·group)](passwd-shadow-group.md), sudo 가 인증을 맡기는 PAM 스택은 [인증 모듈 (PAM)](pam.md)에서 봅니다.

## 이 형식을 쓰는 아티팩트

sudoers 자체는 행위 기록이 아니지만, sudo 에서 나오는 흔적이 남을지 말지를 이 파일이 정합니다. 그래서 sudo 흔적을 해석하기 전에 먼저 읽습니다.

| 흔적 | 이 설정과의 관계 | 이어서 볼 페이지 |
|---|---|---|
| 인증 로그의 sudo 허용·거부 줄 | `logfile`, `log_format`, `log_allowed`·`log_denied`, syslog facility 가 기록 여부와 위치를 정함 | [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md), [인증 로그](../../02-artifacts/logins/auth-log.md) |
| 세션 입출력 기록 (I/O log) | `log_input`·`log_output` 이나 태그 `LOG_INPUT`·`LOG_OUTPUT` 이 켜졌을 때만 생김 | [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md) |
| 시간 기록 파일·강의 파일·admin 플래그 | `timestampdir`, `lecture`, `lecture_status_dir`, `admin_flag` | [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md) |
| PAM 세션 줄 (`pam_unix(sudo:session)`) | sudo 가 PAM 을 부를 때 생김 | [인증 모듈 (PAM)](pam.md) |
| 감사 로그의 명령 기록 | 두 기준 배포판의 sudo 는 Linux 감사 지원을 넣어 빌드함[8][9] | [감사 로그 형식](../logging/auditd-format.md) |
| 권한 상승 경로 | 누가 root 권한을 얻을 수 있었는지 | [권한을 올렸나](../../04-scenarios/intrusion/privilege-escalation.md) |

## 구조

### 관련 파일

| 경로 | 내용 |
|---|---|
| `/etc/sudoers` | 기본 정책 파일[1] |
| `/etc/sudoers.d/` | `@includedir` 로 끌어오는 추가 규칙 폴더[1][5] |
| `/etc/sudo.conf` | 어떤 정책·I/O·감사 플러그인을 불러올지 정하는 sudo 앞단 설정[3] |
| `/etc/nsswitch.conf` 의 `sudoers:` 줄 | 규칙을 파일에서 읽을지 LDAP·SSSD 에서 읽을지 정함. 줄이 없으면 `sudoers: files` 로 봄[4] |
| `/etc/sudo-ldap.conf` | LDAP 지원을 넣은 빌드(Ubuntu 는 `sudo-ldap` 패키지)가 LDAP 설정 파일로 쓰는 경로[8][9] |
| `/etc/sudoers.tmp` | visudo 가 편집할 때 쓰는 임시 파일. 편집 대상 파일 이름 뒤에 `.tmp` 를 붙임[2] |

sudoers 의 기본 권한은 0440(소유자와 그룹만 읽기, 아무도 쓰지 못함)이고 소유자는 uid 0 이어야 합니다[1]. RHEL 9 계열 패키지는 `/etc/sudoers` 를 0440·root:root 로, `/etc/sudoers.d/` 를 0750·root:root 로 설치합니다[9].

### 항목의 종류와 적용 순서

sudoers 에는 별칭 (alias) 과 사용자 명세 (user specification) 두 종류의 항목이 있습니다[1]. 한 사용자에게 여러 항목이 맞으면 차례대로 적용하고, 결국 **마지막으로 맞은 항목**이 쓰입니다. 가장 구체적인 항목이 이기는 방식이 아닙니다[1].

사용자 명세는 "누가 어디서 = (누구 권한으로) 무엇을" 모양입니다[1].

```
User_List Host_List = (Runas_User_List : Runas_Group_List) 태그: 명령
```

| 자리 | 읽는 법 |
|---|---|
| User_List | 사용자 이름, `#uid`, `%그룹`, `%#gid`, `+넷그룹`, `%:비유닉스그룹`, `User_Alias`. 앞에 `!` 가 홀수 개면 부정[1] |
| Host_List | 호스트 이름·주소·`Host_Alias`. `ALL` 이면 모든 호스트 |
| Runas | 괄호 안 앞쪽은 `-u` 로 고를 수 있는 대상 사용자, 콜론 뒤는 `-g` 로 고를 수 있는 그룹[1] |
| 태그 | `NOPASSWD`·`PASSWD`, `NOEXEC`·`EXEC`, `SETENV`·`NOSETENV`, `LOG_INPUT`·`NOLOG_INPUT`, `LOG_OUTPUT`·`NOLOG_OUTPUT`, `MAIL`·`NOMAIL`, `INTERCEPT`·`NOINTERCEPT`, `FOLLOW`·`NOFOLLOW`. 한 번 붙은 태그는 반대 태그가 나올 때까지 같은 목록의 뒤 명령에도 이어짐[1] |
| 명령 | 전체 경로나 `Cmnd_Alias`. `ALL` 이면 모든 명령[1] |

별칭 이름은 대문자로 시작하고 대문자·숫자·밑줄만 씁니다. 같은 별칭을 다시 정의하면 문법 오류입니다[1]. `ALL` 은 늘 맞는 내장 별칭이라 명령 자리에 쓰면 어떤 명령이든 실행할 수 있다는 뜻입니다[1].

규칙에 유효 기간을 붙이는 `NOTBEFORE`·`NOTAFTER` 옵션도 있습니다. 값은 `yyyymmddHHMMSSZ` 모양이고, `Z` 는 UTC, `-0500` 같은 꼬리는 UTC 와의 차이이며, 둘 다 없으면 현지 시각으로 읽습니다[1].

`#` 은 주석입니다. 다만 `#include`·`#includedir` 지시어와 사용자 자리의 `#숫자`(uid)는 주석이 아닙니다[1].

### Defaults 줄

`Defaults` 줄은 옵션을 바꿉니다. 적용 범위에 따라 다섯 가지로 씁니다[1].

| 모양 | 적용 범위 |
|---|---|
| `Defaults` | 전체 |
| `Defaults@호스트` | 그 호스트에서 |
| `Defaults:사용자` | 그 사용자에게 |
| `Defaults!명령` | 그 명령에 |
| `Defaults>대상사용자` | 그 사용자 권한으로 실행할 때 |

### 다른 파일 끌어오기

`@include` 는 파일 하나를, `@includedir` 는 폴더 안 파일을 끌어옵니다. 1.9.1 부터 쓰는 표기이고, 그 전 표기인 `#include`·`#includedir` 도 계속 인정합니다[1]. 상대 경로면 끌어온 쪽 sudoers 와 같은 폴더에서 찾고, 파일 이름의 `%h` 는 짧은 호스트 이름으로 바뀝니다. 중첩은 128단계까지입니다[1].

`@includedir` 는 폴더 안 파일을 **사전순**(숫자순이 아님)으로 읽고, 이름이 `~` 로 끝나거나 `.` 이 들어간 파일은 건너뜁니다[1]. 그래서 `1_x` 는 `10_y` 뒤에 읽히고, `90-admin.conf` 같은 이름(만든 예시)의 파일은 폴더에 있어도 규칙으로 쓰이지 않습니다.

### sudo.conf 의 플러그인 줄

`/etc/sudo.conf` 의 `Plugin` 줄은 `Plugin 심볼이름 경로 [인자...]` 모양이고, 경로가 상대 경로면 `plugin_dir` 기준입니다[3]. 파일이 없거나 `Plugin` 줄이 없으면 sudoers 플러그인을 정책·I/O 기록·감사에 씁니다[3]. 정책 플러그인은 하나만 둘 수 있습니다[3].

sudoers 플러그인 줄의 인자로 `sudoers_file=`(정책 파일 경로), `sudoers_uid=`·`sudoers_gid=`·`sudoers_mode=`(요구하는 소유·권한), `ignore_perms=`(소유·권한 검사 끄기), `error_recovery=`(문법 오류 복구)를 줄 수 있습니다[1]. 이 인자가 있으면 `/etc/sudoers` 가 아닌 파일이 실제 정책일 수 있으니, 정책을 읽기 전에 sudo.conf 를 먼저 봅니다.

### 기록을 정하는 설정 키

| 키 | 뜻 | 기본값 |
|---|---|---|
| `logfile` | 설정하면 syslog 말고 파일에도 씀 | 없음(syslog 만)[1] |
| `syslog` | syslog facility | 빌드 기본 `auth`, `LOG_AUTHPRIV` 가 있는 시스템이면 `authpriv`[7]. 두 기준 배포판은 `authpriv` 로 빌드[8][9] |
| `log_format` | `sudo`(줄 형식), `json`, `json_compact`, `json_pretty` | `sudo`[1] |
| `log_year`·`log_host`·`loglinelen` | 파일 기록의 연도·호스트 표시, 줄 바꿈 길이 | 끔·끔·80[1] |
| `log_input`·`log_output` | 세션 입출력 기록 | 끔[1] |
| `iolog_dir` | 입출력 기록 폴더 | `/var/log` 가 있으면 `/var/log/sudo-io`[6] |
| `log_subcmds`·`log_exit_status` | 셸 안 하위 명령, 종료 상태 기록(1.9.8 이상) | 끔[1] |
| `timestamp_timeout` | 비밀번호를 다시 묻기까지의 분 | 빌드 기본 5[7] |
| `lecture` | 첫 사용 때 안내문 표시 | 빌드 기본 `once`[7] |

줄 모양과 해석은 [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md)에 있습니다.

### 배포판 기본 파일

| 항목 | Ubuntu 24.04[8] | RHEL 9 계열[9] |
|---|---|---|
| 패키지 판 | 1.9.15p5-3ubuntu5.24.04.2[8] | 1.9.17p2(CentOS Stream 9)[9] |
| 관리자 규칙 | `%admin ALL=(ALL) ALL`, `%sudo ALL=(ALL:ALL) ALL` | `%wheel ALL=(ALL) ALL` |
| root 규칙 | `root ALL=(ALL:ALL) ALL` | `root ALL=(ALL) ALL` |
| 끌어오기 줄 | `@includedir /etc/sudoers.d` | `#includedir /etc/sudoers.d` |
| 눈에 띄는 Defaults | `env_reset`, `mail_badpass`, `secure_path`, `use_pty` | `!visiblepw`, `always_set_home`, `match_group_by_gid`, `always_query_group_plugin`, `env_reset`, `env_keep`, `secure_path` |
| `timestamp_timeout` | 15분(빌드 옵션) | 5분(빌드 기본) |
| 강의 | 끔(`--without-lecture`) | `once`, `/var/db/sudo/lectured` 설치 |
| admin 플래그 | 켬(`--enable-admin-flag`) | 빌드 옵션에 없음 |
| 시간 기록 폴더 | `/run/sudo/ts`(`--with-rundir=/run/sudo`) | 빌드 옵션에 없음. 빌드 기본 규칙은 `/run` 이 있으면 `/run/sudo`[6] |

RHEL 9 계열 열은 CentOS Stream 9 패키지 기준입니다[9]. RHEL 9 의 부 판(minor release)마다 sudo 판이 다를 수 있으니 분석 대상의 패키지 데이터베이스로 판을 확인합니다. 상류 기본 틀에서는 `%wheel`·`%sudo` 줄이 모두 주석 처리돼 있습니다[5].

## 읽는 법

아래는 이미지에서 "수집 시점에 누가 무엇을 sudo 로 할 수 있었나" 를 복원하는 순서입니다.

1. `/etc/nsswitch.conf` 의 `sudoers:` 줄을 봅니다. `ldap` 이나 `sss` 가 있으면 규칙 일부가 디렉터리 서버에 있어 이미지에 없을 수 있습니다[4]. 뒤에 나온 원천이 앞의 것보다 우선하고, `[SUCCESS=return]` 이 붙은 원천에서 사용자를 찾거나 `[NOTFOUND=return]` 이 붙은 원천에서 찾지 못하면 거기서 멈춥니다[4].
2. `/etc/sudo.conf` 에서 `Plugin` 줄과 `sudoers_file=`·`ignore_perms=` 같은 인자를 봅니다[1][3].
3. 정책 파일을 처음부터 읽으면서 `@include`·`@includedir`·`#include`·`#includedir` 를 만나는 자리에 그 파일 내용을 끼워 넣습니다. `sudoers.d` 는 사전순으로 넣고, `~` 로 끝나거나 `.` 이 든 파일은 뺍니다[1].
4. 별칭을 풀고, 대상 사용자가 속한 그룹(`%그룹`)은 [계정 파일](passwd-shadow-group.md)의 `/etc/group` 과 `/etc/passwd` 의 기본 GID 로 맞춥니다.
5. 사용자에게 맞는 항목을 모두 찾은 뒤 마지막으로 맞은 항목을 결과로 봅니다[1].
6. 기록 관련 `Defaults`(`logfile`, `log_input`, `log_output`, `iolog_dir`, `log_format`)를 모아 두고, 그 설정에 맞는 위치에서 사용 기록을 찾습니다.

라이브 시스템이면 `visudo -c` 로 정책 파일과 끌어온 파일을 문법·소유·권한까지 검사할 수 있습니다[2]. `-f` 로 이미지에서 꺼낸 사본을 검사할 수도 있지만, 파일 경로를 지정하면 소유·권한은 검사하지 않고 문법만 봅니다[2].

만든 예시(가공한 사용자 이름)로 적용 순서를 보면 이렇습니다.

```
# /etc/sudoers.d/10_ops
%ops    ALL=(ALL) ALL
# /etc/sudoers.d/20_deploy
deployer ALL=(root) NOPASSWD: /usr/bin/systemctl restart webapp
```

`deployer` 가 `ops` 그룹에도 속하면 두 항목이 모두 맞고, `20_deploy` 가 나중에 읽히므로 `systemctl restart webapp` 은 비밀번호 없이 허용됩니다. 다른 명령은 `%ops` 항목대로 비밀번호를 물은 뒤 허용됩니다.

## 포렌식에서 중요한 점

### 증명하는 것

- 수집 시점에 파일에 적혀 있던 권한 규칙과 기록 설정
- 수집 시점에 기록 설정이 꺼져 있었다면, 그 설정이 유지된 동안에는 특정 흔적(입출력 기록, 하위 명령 기록, 파일 기록)이 생기지 않았다는 점
- `NOPASSWD` 규칙이 있었다면 그 명령에 비밀번호 입력 흔적(PAM 인증 줄)이 없을 수 있다는 점

### 증명하지 못하는 것

- 그 규칙이 언제부터 있었는지, 누가 넣었는지. 파일 자체에는 시각이 없어서 파일 시스템 시각, 패키지 기록, 편집기 흔적, 감사 로그와 맞춰 봐야 합니다.
- 규칙이 실제로 쓰였는지. 사용 여부는 [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md)에서 확인합니다.
- LDAP·SSSD 에서 받아 온 규칙. 이미지 안 파일만으로는 알 수 없습니다[4].

### 시각

sudoers 에는 `NOTBEFORE`·`NOTAFTER` 말고 시각 값이 없습니다. 이 두 값은 `Z` 나 시차가 없으면 현지 시각으로 해석하므로[1], 규칙이 유효했던 기간을 따질 때 시스템 시간대를 함께 봅니다([호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md)). 파일 자체의 수정·변경 시각은 [ext4](../filesystem/ext4/index.md) 같은 파일 시스템 페이지와 [Linux 의 시각 값](../value-decoding/time-values.md) 페이지의 설명을 따릅니다.

### 바뀐 흔적과 남는 부스러기

- 배포판 패키지에 든 기본 파일[8][9]과 분석 대상의 `/etc/sudoers` 를 비교하면 로컬에서 바꾼 줄이 드러납니다. RHEL 9 계열 패키지는 이 파일을 설정 파일(`%config(noreplace)`)로 싣습니다[9]. 패키지 파일 비교는 [패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md)을 봅니다.
- `sudoers.d` 안에서 건너뛰는 이름(`~` 로 끝나는 편집기 백업, `.` 이 든 파일)도 지우지 말고 살핍니다. 규칙으로는 쓰이지 않지만 이전 판 내용이 남아 있을 가능성이 있습니다. 편집기 부스러기는 [편집기 흔적](../../02-artifacts/file-activity/editor-artifacts.md)에서 다룹니다.
- visudo 가 편집 중 끊기면 `/etc/sudoers.tmp`(또는 편집한 파일 이름 + `.tmp`)가 남아 있을 가능성이 있습니다[2].
- 문법 오류가 있는 파일은 `parse error in /etc/sudoers near line N` 같은 오류 기록을, 권한이 어긋난 파일은 `/etc/sudoers is owned by uid N, should be 0`·`/etc/sudoers is world writable` 같은 기록을 남깁니다[1]. visudo 를 거치지 않고 파일을 직접 고친 흔적일 가능성이 있습니다.
- 1.9.3 이상은 문법 오류가 난 줄에서 오류 자리부터 줄 끝까지를 버리고 나머지를 계속 읽는 것이 기본입니다[1]. 오류가 있는 파일도 일부 규칙은 효력이 있었을 수 있습니다.
- 감사 규칙으로 `/etc/sudoers`·`/etc/sudoers.d/` 를 감시했다면 누가 언제 썼는지 남습니다([감사 로그의 파일 감시](../../02-artifacts/file-activity/auditd-watches.md)).

## 함정

- "가장 구체적인 규칙" 이 아니라 "마지막으로 맞은 규칙" 이 적용됩니다[1]. 앞쪽의 좁은 규칙만 보고 권한을 판단하면 틀립니다.
- RHEL 계열 기본 파일 끝의 `#includedir /etc/sudoers.d` 는 주석처럼 보이지만 지시어입니다[1][9].
- `sudoers.d` 안 파일이 있다고 규칙이 적용된 것은 아닙니다. 이름에 `.` 이 있으면 무시됩니다[1].
- visudo 는 `@includedir` 폴더 안 파일에 문법 오류가 없으면 그 파일을 편집 대상으로 열지 않습니다[1]. 폴더 안 파일은 따로 읽어야 합니다.
- `/etc/sudoers` 만 수집하면 정책이 빠집니다. ForensicArtifacts 의 `UnixSudoersConfigurationFile` 은 `/etc/sudoers` 하나만 정의합니다[10]. UAC 는 `/etc` 전체를 모으므로 `sudoers.d`·`sudo.conf` 가 함께 들어옵니다[11].
- Ubuntu 는 `sudo` 와 `admin` 두 그룹이, RHEL 은 `wheel` 그룹이 기본 관리자 그룹입니다[8][9]. 한 그룹만 보고 관리자 목록을 만들면 빠집니다.
- 파일 기록(`logfile`)은 `loglinelen` 에서 줄을 바꿔 4칸 들여 쓰므로 한 줄 grep 으로는 명령 뒷부분을 놓칩니다[1].

## 도구

- `visudo -c`: 문법·소유·권한 검사, `visudo -c -f 파일`: 지정한 파일의 문법 검사[2]
- `sudo -l -U 사용자`: 라이브 시스템에서 그 사용자에게 적용되는 규칙 목록[12]. 이미지에서는 위 "읽는 법" 순서로 직접 합칩니다.
- ForensicArtifacts: `UnixSudoersConfigurationFile`(`/etc/sudoers`), `LinuxSudoReplayLogs`(`/var/log/sudo-io/**`)[10]
- UAC: `files/system/etc.yaml`(`/etc` 전체, shadow 류만 뺌), `live_response/system/sudo_lectured.yaml`(`/var/db/sudo/lectured`·`/var/lib/sudo/lectured` 의 파일 시각)[11]

## 참고 문헌

1. sudo, `docs/sudoers.man.in`. https://github.com/sudo-project/sudo/blob/main/docs/sudoers.man.in
2. sudo, `docs/visudo.man.in`. https://github.com/sudo-project/sudo/blob/main/docs/visudo.man.in
3. sudo, `docs/sudo.conf.man.in`. https://github.com/sudo-project/sudo/blob/main/docs/sudo.conf.man.in
4. sudo, `docs/sudoers.ldap.man.in`. https://github.com/sudo-project/sudo/blob/main/docs/sudoers.ldap.man.in
5. sudo, `plugins/sudoers/sudoers.in`. https://github.com/sudo-project/sudo/blob/main/plugins/sudoers/sudoers.in
6. sudo, `m4/sudo.m4`. https://github.com/sudo-project/sudo/blob/main/m4/sudo.m4
7. sudo, `configure.ac`. https://github.com/sudo-project/sudo/blob/main/configure.ac
8. Ubuntu, sudo 패키지 `debian/` (noble-updates, `sudoers`·`rules`·`changelog`). https://git.launchpad.net/ubuntu/+source/sudo/tree/debian?h=ubuntu/noble-updates
9. CentOS Stream 9, sudo 패키지 (`sudoers`·`sudo.spec`). https://gitlab.com/redhat/centos-stream/rpms/sudo/-/tree/c9s
10. ForensicArtifacts, `artifacts/data/unix_common.yaml`, `artifacts/data/linux.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/unix_common.yaml , https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
11. UAC, `artifacts/files/system/etc.yaml`, `artifacts/live_response/system/sudo_lectured.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/files/system/etc.yaml , https://github.com/tclahr/uac/blob/main/artifacts/live_response/system/sudo_lectured.yaml
12. sudo, `docs/sudo.man.in`. https://github.com/sudo-project/sudo/blob/main/docs/sudo.man.in
