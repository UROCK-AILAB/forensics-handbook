---
title: "감사 로그의 파일 감시"
parent: "아티팩트 · 파일 활동"
nav_order: 670
---

# 감사 로그의 파일 감시 (auditd Watches)

관리자가 감사 규칙으로 지정한 파일이나 폴더에 쓰기·읽기·실행·속성 변경을 하는 시스템 콜이 일어나면, 커널이 누가 어떤 프로그램으로 어느 경로에 무엇을 했는지를 감사 로그에 남깁니다[1][2].

## 무엇을 기록하나 · 왜 생기나

리눅스 감사 체계 (Linux Audit) 의 파일 시스템 규칙을 흔히 감시 (watch) 라고 부릅니다[2]. 감시는 기본으로 켜져 있는 기록이 아니라 관리자가 규칙을 넣어야 생기는 기록이라서, 분석 대상에 어떤 규칙이 있었는지가 곧 무엇이 기록될 수 있었는지를 정합니다. audit-userspace 가 싣는 규칙 예시 묶음에는 보안 기준(STIG)에 맞춰 `/etc/passwd`·`/etc/shadow`·`/etc/sudoers` 같은 설정 파일을 감시하는 규칙이 들어 있습니다[4].

규칙이 하나도 없어도 로그인·인증처럼 규정상 반드시 남겨야 하는 사건(1100~1299, 1326, 1328, 1331 이상 번호)은 감사 로그에 올 수 있습니다[2]. 파일 감시 레코드는 이와 달리 규칙이 있을 때만 생깁니다. 감사 로그의 줄 모양, 이벤트와 레코드의 관계, 회전, 필드 뜻은 [감사 로그 형식](../../01-foundations/logging/auditd-format.md) 에서 다루고, 이 페이지는 감시 규칙과 그 결과를 읽는 법만 다룹니다.

## 위치와 버전별 차이

| 무엇 | 경로 | 비고 |
|---|---|---|
| 감사 로그 | `/var/log/audit/audit.log`, 회전 파일 `audit.log.1` … | `auditd.conf` 의 `log_file` 로 바뀔 수 있음([감사 로그 형식](../../01-foundations/logging/auditd-format.md)). 수집 정의는 `/var/log/audit/*`[17] |
| 규칙 조각 | `/etc/audit/rules.d/*.rules` | 확장자가 `.rules` 인 파일만 씀[3] |
| 합친 규칙 | `/etc/audit/audit.rules` | augenrules 가 만듦[3] |
| 커널에 들어간 규칙 | `auditctl -l` 출력 | 라이브 시스템에서만 확인 가능[16] |

augenrules 는 `rules.d` 의 파일을 자연 정렬 순서(`ls -v`)로 이어 붙이고 빈 줄과 주석 줄을 뺀 뒤, 결과가 기존 `audit.rules` 와 다를 때만 덮어씁니다[3]. 이때 옵션 없는 `-D` 는 첫 줄, `-b` 는 둘째 줄, `-f` 는 셋째 줄, `-e` 는 마지막 줄로 옮깁니다[3]. 그래서 `audit.rules` 의 줄 순서는 조각 파일의 순서와 다를 수 있고, 어느 조각에서 규칙이 왔는지는 `rules.d` 를 직접 봐야 압니다.

Ubuntu 24.04 와 RHEL 9 모두 auditd 가 깔려 있어야 이 경로가 생기며, 배포판이 기본으로 어떤 감시 규칙을 넣는지는 분석 대상의 `rules.d` 와 패키지 기록([dpkg·apt 기록](../packages/dpkg-apt.md), [rpm·dnf·yum 기록](../packages/rpm-dnf.md))으로 확인합니다. audit-userspace 의 예시 묶음은 파일 이름 앞 번호로 역할을 나눕니다(10 커널·auditctl 설정, 20 예외, 30 주 규칙, 40 선택, 50 서버용, 70 로컬, 90 마무리)[4]. 이 묶음은 한꺼번에 쓰라고 만든 것이 아니라 필요한 조각을 골라 `rules.d` 에 복사해 쓰는 것이라서[4], 시스템마다 들어 있는 조각이 다릅니다.

## 구조

### 규칙의 두 가지 표기

감시 규칙은 두 가지로 적습니다. 지금 권장하는 표기는 시스템 콜 규칙 형식이고, 옛 `-w` 형식은 하위 호환용으로만 남아 있고, 성능이 나빠 더는 권장하지 않습니다(deprecated)[1][2].

```text
# 시스템 콜 규칙 꼴 (권장)
-a always,exit -F arch=b64 -F path=/etc/shadow -F perm=wa -F key=identity
-a always,exit -F arch=b64 -F dir=/etc/sudoers.d/ -F perm=wa -F key=actions

# 옛 꼴 (deprecated)
-w /etc/shadow -p wa -k identity
```

`-w 경로` 는 대상이 파일이면 `-F path=` 와, 폴더면 `-F dir=` 와 거의 같고, 함께 쓸 수 있는 옵션은 `-p`(권한)와 `-k`(키)뿐입니다[1]. `path` 는 파일 하나를 가리키고, `dir` 는 그 폴더 아래 전체를 감시합니다[1][2]. `dir` 감시는 아래에 다른 마운트 지점이 있으면 거기서 멈추고, `-q` 규칙으로 그 마운트를 감시 폴더와 같은 것으로 묶을 수 있습니다[1][2]. 최상위 폴더 `/` 에는 감시를 걸 수 없고 와일드카드도 쓸 수 없으며, `path`·`dir`·`perm` 은 exit 목록에서만 쓸 수 있습니다[1].

`key` 는 규칙에 붙이는 자유로운 이름입니다[2]. 관련 규칙에 같은 키를 붙여 두면 조사 때 그 키로 결과를 한꺼번에 고를 수 있습니다[2]. 예시 묶음 `30-stig.rules` 에서 감시 규칙에 쓰는 키는 다음과 같습니다[4].

| 키 | 감시 대상 |
|---|---|
| `time-change` | `/etc/localtime` |
| `identity` | `/etc/group`, `/etc/passwd`, `/etc/gshadow`, `/etc/shadow`, `/etc/security/opasswd` |
| `system-locale` | `/etc/issue`, `/etc/issue.net`, `/etc/hosts`, `/etc/hostname`, `/etc/NetworkManager/` 아래 |
| `MAC-policy` | `/etc/selinux/` 아래 |
| `actions` | `/etc/sudoers`, `/etc/sudoers.d/` 아래 |
| `maybe-escalation` | `/usr/bin/systemd-run`, `/usr/bin/pkexec` (실행 `x`) |
| `logins`, `session` | `/var/log/tallylog`·`/var/run/faillock`·`/var/log/lastlog`, `/var/run/utmp`·`/var/log/btmp`·`/var/log/wtmp` (예시에서는 주석 처리) |

### 권한 문자와 시스템 콜

`perm` 의 `r`·`w`·`x`·`a` 는 파일 권한 비트가 아니라 "그런 일을 하는 시스템 콜의 종류" 입니다[1]. 로그가 넘치지 않도록 `read`·`write` 시스템 콜 자체는 빼고, 파일을 열 때 요청한 접근 모드로 읽기·쓰기를 판단합니다[1]. `arch` 를 주면 auditctl 이 각 문자에 해당하는 시스템 콜을 규칙에 넣고[6], `arch` 를 빼면 모든 시스템 콜을 평가해서 느려집니다[1][2]. 현재 audit-userspace 와 커널 코드의 분류는 다음과 같습니다[5][11].

| 문자 | 들어가는 시스템 콜 |
|---|---|
| `w` 쓰기 | `open`·`openat`·`openat2`(쓰기 모드일 때), `creat`, `truncate`, `ftruncate`, `fallocate`, `rename`, `renameat`, `renameat2`, `unlink`, `unlinkat`, `mkdir`, `mkdirat`, `rmdir`, `link`, `linkat`, `symlink`, `symlinkat`, `mknod`, `mknodat`, `acct`, `swapon`, `quotactl`, `quotactl_fd`, `bind` |
| `r` 읽기 | `open`·`openat`·`openat2`(읽기 모드일 때), `readlink`, `readlinkat`, `stat`, `lstat`, `fstat`, `newfstatat`, `statx`, `getxattr` 계열, `listxattr` 계열, `file_getattr`, `quotactl`, `quotactl_fd` |
| `a` 속성 | `chmod`, `fchmod`, `fchmodat`, `fchmodat2`, `chown`, `fchown`, `lchown`, `fchownat`, `setxattr` 계열, `removexattr` 계열, `file_setattr`, `link`, `linkat` |
| `x` 실행 | `execve`, `execveat` |

커널은 `open`·`openat`·`openat2` 를 열기 플래그의 접근 모드(`ACC_MODE`)로 판정하고, `execve` 는 `x` 로, 나머지는 위 분류표로 판정합니다[8]. 그래서 `O_RDWR` 로 연 파일은 `r` 규칙과 `w` 규칙 둘 다에 걸릴 수 있습니다.

### 커널이 감시를 붙드는 방법

커널은 감시 대상 파일이 아니라 그 부모 폴더에 fsnotify 표시를 달고, 파일은 이름으로 따라갑니다[7]. 규칙을 넣을 때 파일이 있으면 그 파일의 장치 번호와 아이노드 번호를 규칙에 묶고, 없으면 규칙만 넣어 둡니다[7]. 이후 부모 폴더에서 일어나는 일에 따라 커널은 다음처럼 규칙을 고칩니다[7].

| 부모 폴더에서 일어난 일 | 커널의 처리 | 로그 |
|---|---|---|
| 감시 이름으로 파일이 새로 생기거나 옮겨 옴 | 새 아이노드·장치 번호로 규칙을 다시 묶음 | 설정 변경 레코드 없음 |
| 감시 이름의 파일이 지워지거나 옮겨 나감 | 아이노드를 "미설정" 으로 두고 규칙은 유지 | 설정 변경 레코드 없음 |
| 부모 폴더 자체가 지워지거나 옮겨지거나 마운트가 풀림 | 그 폴더에 걸린 감시 규칙을 모두 지움 | `CONFIG_CHANGE` `op=remove_rule` |

감시 규칙에 맞는지는 이벤트에 딸린 파일의 아이노드·장치 번호가 규칙에 묶인 값과 같은지로 판정합니다[7].

### 남는 레코드

감시 규칙에 걸린 시스템 콜 하나는 같은 일련번호를 쓰는 SYSCALL(1300), CWD(1307), PATH(1302), PROCTITLE(1327) 레코드 묶음으로 남습니다[8][15]. SYSCALL 레코드 끝의 `key=` 에 규칙의 키가 적혀서 어느 규칙에 걸렸는지 알 수 있습니다[8][15]. 규칙을 넣고 뺄 때는 CONFIG_CHANGE(1305) 레코드가 남습니다[9].

PATH 레코드는 이벤트가 건드린 경로마다 한 줄씩 생기고, 커널은 다음 순서로 필드를 적습니다[8].

| 필드 | 뜻 |
|---|---|
| `item` | 이 이벤트에서 몇 번째 경로인지 (0부터) |
| `name` | 경로 이름. 프로그램이 넘긴 이름 그대로일 수 있어 상대 경로일 수 있고, 부모 폴더 항목은 폴더 부분만 적힘 |
| `inode`, `dev` | 아이노드 번호, 장치 번호 (16진 주번호:부번호) |
| `mode` | 파일 종류와 권한 (8진, 예: `0100644`) |
| `ouid`, `ogid` | 파일 소유자 uid·gid |
| `rdev` | 장치 파일이면 장치 번호 |
| `nametype` | `NORMAL`, `PARENT`(부모 폴더), `CREATE`(새로 만든 항목), `DELETE`(지운 항목), `UNKNOWN` |

아이노드를 알 수 없는 항목에는 `inode` 부터 `rdev` 까지가 빠집니다[8]. `nametype` 앞에는 보안 모듈 문맥이, 뒤에는 파일 capability 값이 붙을 수 있습니다[8]. `nametype` 은 "참조한 파일 작업의 종류" 를 나타내서[15], `rename` 한 번에 원래 이름의 `DELETE` 와 새 이름의 `CREATE` 가 함께 보일 수 있습니다.

규칙을 넣고 뺄 때의 CONFIG_CHANGE 레코드에는 `auid`, `ses`, (보안 모듈 문맥), `op=add_rule` 또는 `op=remove_rule`, `key`, `list`, `res` 가 적힙니다[9][10]. exit 목록의 번호가 `0x04` 라서 감시 규칙은 `list=4` 로 적힙니다[12]. 키가 없는 규칙은 `key=(null)` 로 적힙니다[10]. 부모 폴더가 사라져 커널이 감시를 지울 때는 `op=remove_rule path=감시경로 key=… list=… res=1` 모양으로 경로가 함께 적힙니다[7].

아래는 명세로 만든 예시입니다. 모든 값은 지어낸 것이고, SYSCALL 레코드의 나머지 필드는 `…` 로 줄였습니다(전체 필드는 [감사 로그 형식](../../01-foundations/logging/auditd-format.md) 참고).

```text
type=CONFIG_CHANGE msg=audit(1767225600.123:101): auid=1000 ses=3 op=add_rule key="identity" list=4 res=1
type=SYSCALL msg=audit(1767225700.456:202): arch=c000003e syscall=257 success=yes exit=3 … auid=1000 uid=0 … comm="vi" exe="/usr/bin/vim" key="identity"
type=CWD msg=audit(1767225700.456:202): cwd="/root"
type=PATH msg=audit(1767225700.456:202): item=0 name="/etc/" inode=131073 dev=fd:00 mode=040755 ouid=0 ogid=0 rdev=00:00 nametype=PARENT
type=PATH msg=audit(1767225700.456:202): item=1 name="/etc/passwd" inode=131990 dev=fd:00 mode=0100644 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
type=PROCTITLE msg=audit(1767225700.456:202): proctitle=…
```

x86_64 에서 `syscall=257` 은 `openat` 입니다[18].

## 증거로서 의미

### 증명하는 것

감시 레코드는 규칙에 걸린 시스템 콜이 그 시각에 그 `auid`·`uid`·`pid`·`exe` 로, 그 경로와 아이노드에 대해 일어났고 성공했는지 실패했는지(`success`·`exit`)를 커널이 적은 기록입니다[15]. `auid` 는 `sudo`·`su` 뒤에도 처음 로그인한 계정을 가리키므로, root 로 파일을 고친 경우에도 누가 로그인해서 한 일인지 좁힐 수 있습니다([감사 로그 형식](../../01-foundations/logging/auditd-format.md)). PATH 의 `inode`·`ouid`·`mode` 는 시스템 콜 당시의 값이라서, 나중에 파일이 바뀌거나 지워져도 당시 어떤 파일이었는지를 보여 줍니다[8]. 키는 조사할 이벤트를 고르는 손잡이가 됩니다.

### 증명하지 못하는 것

`w` 에 걸린 기록은 "쓰기 모드로 열었다" 거나 이름 바꾸기·지우기·자르기 같은 시스템 콜을 불렀다는 뜻입니다. `read`·`write` 시스템 콜은 감시하지 않으므로[1], 실제로 몇 바이트를 썼는지, 무엇을 읽었는지, 쓰기 모드로 열고 아무것도 쓰지 않았는지는 알 수 없습니다. 판정이 여는 순간에 이뤄지므로[8], 규칙을 넣기 전에 이미 열어 둔 파일 기술자로 한 쓰기는 기록되지 않을 가능성이 있습니다.

규칙에 없던 경로와 권한 문자는 처음부터 기록되지 않습니다. `dir` 감시도 아래의 다른 마운트 지점에서는 멈춥니다[2]. 그래서 감시 기록이 없다는 사실은 "그 시각에 그 규칙이 있었다" 는 것까지 확인한 뒤에야 "접근이 없었다" 는 근거가 됩니다. 키 이름도 관리자가 붙인 이름일 뿐이라서[2], `identity` 라는 키가 곧 계정 변경을 뜻하지는 않습니다. 규칙의 실제 대상은 `audit.rules` 나 `auditctl -l` 로 봅니다.

## 시각 해석

이벤트 시각은 `msg=audit(초.밀리초:일련번호)` 의 Unix epoch 값이라서 UTC 기준이고 시간대 정보가 없습니다([감사 로그 형식](../../01-foundations/logging/auditd-format.md), [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)). 이 시각은 시스템 콜에 들어간 때이지, 파일 내용이 디스크에 내려간 때가 아닙니다[8].

감시가 언제부터 있었는지는 `op=add_rule` 인 CONFIG_CHANGE 레코드의 시각으로 알 수 있습니다[9]. 이 레코드는 규칙을 커널에 넣을 때마다 생기므로[9], 부팅 때 규칙을 다시 넣으면 그때마다 새로 한 무리가 생깁니다. 이 시각보다 앞선 파일 활동은 그 규칙으로 기록될 수 없습니다. 반대로 `op=remove_rule` 뒤에는 그 규칙에 걸리는 기록이 끊깁니다.

PATH 레코드의 아이노드 번호로 [ext4](../../01-foundations/filesystem/ext4/index.md) 아이노드의 수정·변경 시각을 찾아 감사 시각과 맞춰 볼 수 있습니다. 아이노드 시각은 그 뒤 활동으로 덮이지만 감사 레코드는 활동마다 따로 남는다는 차이가 있습니다.

## 함정과 한계

- **옛 형식과 새 형식이 섞여 있을 수 있습니다.** `rules.d` 에 `-w` 형식이 남아 있어도 커널에 들어간 모습은 `auditctl -l` 로 봐야 정확합니다[1][16]. 이미지 분석이라면 `audit.rules` 가 augenrules 로 다시 만들어졌는지 `rules.d` 와 비교해 봅니다[3].
- **`r` 에 `stat` 계열이 들어 있습니다.** 현재 코드 기준으로 `ls -l` 처럼 속성만 읽어도 `r` 규칙에 걸릴 수 있습니다[5][11]. `r` 기록을 "파일 내용을 읽었다" 로 옮기지 않습니다. 이 분류는 판에 따라 달라질 가능성이 있으니 분석 대상의 audit·커널 판을 함께 적어 둡니다.
- **편집기 저장이 `write` 가 아니라 `rename` 으로 보일 수 있습니다.** 새 파일에 쓰고 원래 이름으로 바꾸는 방식으로 저장하는 편집기는 아이노드를 바꾸지만, 커널이 부모 폴더에서 이름으로 규칙을 다시 묶으므로 이후에도 감시가 이어집니다[7]. 그 이벤트에는 `openat` 대신 `rename` 과 `nametype=CREATE`·`DELETE` PATH 가 보일 수 있습니다. 편집기가 남기는 다른 흔적은 [편집기 흔적](editor-artifacts.md) 을 봅니다.
- **부모 폴더를 지우거나 옮기면 감시가 조용히 사라집니다.** 이때 남는 것은 `op=remove_rule` 한 줄뿐입니다[7]. 이 레코드의 `auid`·`ses` 는 그 순간 커널에서 돌던 프로세스, 곧 폴더를 옮기거나 지운 프로세스의 값일 가능성이 높습니다. 현재 커널 코드대로라면 이 경로에서는 `ses` 값과 `op=` 사이에 공백이 없어 `ses=3op=remove_rule` 처럼 붙어서 적힙니다[7][10]. 공백으로 필드를 나누는 도구가 이 줄을 잘못 읽을 수 있으니 `remove_rule` 문자열로 따로 찾습니다.
- **`-e 2` 이면 재부팅 전에는 규칙을 바꿀 수 없습니다.** 바꾸려는 시도는 감사되고 거부됩니다[1]. 예시 묶음의 `99-finalize.rules` 에는 이 줄이 주석으로 들어 있어[4], 켜져 있는지는 실제 파일에서 확인합니다.
- **경로가 16진으로 적힐 수 있습니다.** `name`·`cwd`·`key` 값에 공백, 큰따옴표, 0x21 보다 작거나 0x7E 보다 큰 바이트가 있으면 따옴표 없는 16진 문자열이 됩니다[10]([감사 로그 형식](../../01-foundations/logging/auditd-format.md)). 한글 파일 이름은 늘 16진으로 적힙니다.
- **상대 경로를 그대로 읽지 않습니다.** `name` 이 상대 경로이면 같은 이벤트의 CWD 레코드를 앞에 붙여 읽습니다[8].
- **규칙은 시기마다 달랐을 수 있습니다.** `arch` 없는 규칙은 모든 시스템 콜을 평가해 느려지므로[1][2], 운영 중에 규칙을 줄이거나 바꿨을 가능성이 있습니다. 그래서 감사 로그 안의 CONFIG_CHANGE 로 규칙이 바뀐 시점을 찾아 둡니다.

## 직접 분석해 보기

### 헥스로 한 번

`name` 에 공백이 든 PATH 레코드를 명세로 만든 예시입니다. 경로 `/srv/share/q3 report.ods` 에 공백(0x20)이 있어 커널은 이 값을 따옴표 없이 16진으로 적습니다.

```text
type=PATH msg=audit(1767226000.789:305): item=1 name=2F7372762F73686172652F7133207265706F72742E6F6473 inode=262401 dev=fd:02 mode=0100640 ouid=1001 ogid=1001 rdev=00:00 nametype=NORMAL
```

16진 문자열을 두 자리씩 끊어 바이트로 읽으면 다음과 같습니다.

```text
2F 73 72 76 2F 73 68 61 72 65 2F 71 33 20 72 65 70 6F 72 74 2E 6F 64 73
 /  s  r  v  /  s  h  a  r  e  /  q  3     r  e  p  o  r  t  .  o  d  s
```

값에 큰따옴표가 없으면 16진으로 적힌 값이라는 뜻이고, 길이는 늘 짝수입니다. `echo 2F73…6473 | xxd -r -p` 처럼 풀면 원래 경로가 나옵니다. `dev=fd:02` 는 16진 주번호 0xfd, 부번호 0x02 이고, `mode=0100640` 은 8진수로 일반 파일(0100000)에 권한 640 을 더한 값입니다[8].

### 공개 도구로 한 번

audit-userspace 의 `ausearch`·`aureport` 는 옮겨 온 로그도 읽습니다[13][14].

```text
ausearch -if /case/var/log/audit/ -k identity -i
ausearch -if /case/var/log/audit/ -f /etc/sudoers -i
aureport -if /case/var/log/audit/ -f -i
aureport -if /case/var/log/audit/ -k --summary
ausearch -if /case/var/log/audit/ -m CONFIG_CHANGE -i
```

`-k` 는 규칙 키로, `-f` 는 파일 이름으로 이벤트를 찾고(`-f` 는 일반 파일과 af_unix 소켓 모두에 맞음)[13], `aureport -f` 는 파일 보고서, `-k` 는 키 보고서를 만듭니다[14]. `-i` 는 uid 를 이름으로 바꾸는데, 로그가 보강 형식(ENRICHED)이 아니면 분석하는 기계의 계정 정보를 쓰므로[13] 이름은 분석 대상의 계정 파일로 다시 확인합니다([감사 로그 형식](../../01-foundations/logging/auditd-format.md)). 규칙은 이미지에서 `/etc/audit/rules.d/*.rules` 와 `/etc/audit/audit.rules` 를 읽고, 라이브 시스템이면 UAC 처럼 `auditctl -l`·`auditctl -s` 결과를 함께 남깁니다[16]([라이브 응답 수집](../../03-techniques/acquisition/live-response.md)).

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 점 | 페이지 |
|---|---|---|
| 감사 로그의 실행 기록 | 같은 `ses`·`pid` 에서 앞뒤로 실행한 명령 | [감사 로그의 실행 기록](../execution/auditd-execve.md) |
| 계정 파일 변경 | `identity` 키 이벤트와 `passwd`·`shadow` 내용 변화 | [계정 생성·변경 흔적](../logins/account-changes.md), [계정 파일](../../01-foundations/users-auth/passwd-shadow-group.md) |
| sudo 설정·사용 | `actions` 키 이벤트와 `sudoers` 변경, sudo 사용 기록 | [sudo 설정](../../01-foundations/users-auth/sudoers.md), [sudo·su 사용 기록](../logins/sudo-su.md) |
| 편집기 흔적 | 같은 시각 편집한 파일 목록 | [편집기 흔적](editor-artifacts.md) |
| 파일 시스템 | PATH 의 아이노드 번호로 찾은 아이노드 시각 | [ext4](../../01-foundations/filesystem/ext4/index.md) |
| 시간대 설정 | `time-change` 키 이벤트와 `/etc/localtime` | [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md) |

여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 와 [로그 분석](../../03-techniques/analysis/log-analysis.md) 을, 감사 기록을 멈추거나 지운 흔적은 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md) 를 봅니다.

## 실습

auditd 가 깔린 공개 Linux 시험 데이터(NIST CFReDS 등)나 직접 만든 가상 머신 이미지로 풀어 봅니다.

1. `/etc/audit/rules.d/` 에 어떤 조각 파일이 있고, 합친 `audit.rules` 와 내용이 같은가? `-w` 형식과 `-F path` 형식 중 어느 쪽으로 적혀 있는가?
2. 감시 규칙마다 키를 정리하고, 감사 로그에서 키별 이벤트 수를 세어 보자. 규칙은 있는데 이벤트가 하나도 없는 키가 있는가?
3. 가장 이른 `op=add_rule` 레코드와 가장 늦은 `op=remove_rule` 레코드는 언제인가? 그 사이에 부팅이 몇 번 있었는가?
4. `identity` 키 이벤트 하나를 골라 `auid`, `exe`, PATH 의 `name`·`nametype`·`inode` 를 읽어 보자. 이 이벤트는 파일을 연 것인가, 이름을 바꾼 것인가?
5. PATH 의 `name` 이 16진으로 적힌 레코드가 있는가? 풀면 어떤 경로인가?

## 참고 문헌

1. linux-audit, audit-userspace, `auditctl(8)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/auditctl.8
2. linux-audit, audit-userspace, `audit.rules(7)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/audit.rules.7
3. linux-audit, audit-userspace, `augenrules(8)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/augenrules.8
4. linux-audit, audit-userspace, `rules/10-base-config.rules`, `rules/30-stig.rules`, `rules/99-finalize.rules`, `rules/README-rules`. https://github.com/linux-audit/audit-userspace/tree/master/rules
5. linux-audit, audit-userspace, `lib/permtab.h`. https://github.com/linux-audit/audit-userspace/blob/master/lib/permtab.h
6. linux-audit, audit-userspace, `lib/libaudit.c` (`audit_add_perm_syscalls`). https://github.com/linux-audit/audit-userspace/blob/master/lib/libaudit.c
7. Linux 커널, `kernel/audit_watch.c`. https://github.com/torvalds/linux/blob/master/kernel/audit_watch.c
8. Linux 커널, `kernel/auditsc.c` (`audit_match_perm`, `audit_log_name`). https://github.com/torvalds/linux/blob/master/kernel/auditsc.c
9. Linux 커널, `kernel/auditfilter.c` (`audit_log_rule_change`). https://github.com/torvalds/linux/blob/master/kernel/auditfilter.c
10. Linux 커널, `kernel/audit.c` (`audit_log_session_info`, `audit_log_key`). https://github.com/torvalds/linux/blob/master/kernel/audit.c
11. Linux 커널, `include/asm-generic/audit_dir_write.h`, `audit_write.h`, `audit_change_attr.h`, `audit_read.h`. https://github.com/torvalds/linux/tree/master/include/asm-generic
12. Linux 커널, `include/uapi/linux/audit.h`. https://github.com/torvalds/linux/blob/master/include/uapi/linux/audit.h
13. linux-audit, audit-userspace, `ausearch(8)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/ausearch.8
14. linux-audit, audit-userspace, `aureport(8)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/aureport.8
15. linux-audit, audit-documentation, `field-dictionary.csv`, `message-dictionary.csv`. https://github.com/linux-audit/audit-documentation/tree/main/specs
16. tclahr, UAC, `artifacts/live_response/system/auditctl.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/live_response/system/auditctl.yaml
17. ForensicArtifacts, artifacts, `linux.yaml` (`LinuxAuditLogs`). https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
18. Linux 커널, `arch/x86/entry/syscalls/syscall_64.tbl`. https://github.com/torvalds/linux/blob/master/arch/x86/entry/syscalls/syscall_64.tbl
