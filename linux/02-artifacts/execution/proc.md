---
title: "실행 중인 프로세스"
parent: "아티팩트 · 실행 흔적"
nav_order: 480
---

# 실행 중인 프로세스 (/proc)

`/proc/PID/` 아래 파일은 수집하는 그 순간 돌고 있는 프로세스의 실행 파일·명령줄·열린 파일·메모리 배치를 보여 주고, 라이브 수집에서만 얻을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

proc 파일 시스템 (procfs) 은 커널 자료 구조를 파일 모양으로 보여 주는 가상 파일 시스템이고, 보통 `/proc` 에 마운트됩니다[1]. 돌고 있는 프로세스마다 PID 이름의 폴더가 하나씩 있고, 그 안의 파일이 그 프로세스의 정보를 보여 줍니다[1]. 디스크에 저장되는 기록이 아니라서 전원을 끈 뒤 만든 디스크 이미지의 `/proc` 에는 내용이 없습니다. dissect.target 도 `/proc` 이 없거나 비어 있으면 `proc` 기능을 쓸 수 없다고 판단합니다[4].

그래서 이 아티팩트는 "기록" 이 아니라 "수집 순간의 사진" 입니다. 이미 끝난 프로세스는 보이지 않고, 끝난 프로세스의 실행 기록은 [감사 로그의 실행 기록](auditd-execve.md)이나 [프로세스 회계](process-accounting.md)에서 찾습니다. 수집 순서와 방법은 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md)에서 다룹니다.

## 위치와 버전별 차이

`/proc` 은 커널이 만드는 인터페이스라서 Ubuntu 24.04 LTS 와 RHEL 9 에서 경로와 파일 이름이 같습니다. 차이는 커널 판과 마운트 옵션에서 생깁니다.

| 항목 | 차이 |
|---|---|
| `/proc/PID/comm` | Linux 2.6.33 부터 있습니다[1] |
| `/proc/PID/map_files/` | Linux 3.3 부터 있고, 4.3 전에는 커널 설정 `CONFIG_CHECKPOINT_RESTORE` 가 켜져 있어야 보였습니다[1] |
| `map_files` 링크 읽기 | Linux 5.9 전에는 초기 사용자 네임스페이스의 `CAP_SYS_ADMIN`, 5.9 부터는 `CAP_SYS_ADMIN` 이나 `CAP_CHECKPOINT_RESTORE` 가 있어야 합니다[1] |
| `maps` 의 `[stack:TID]` | Linux 3.4 ~ 4.4 에만 있고 4.5 에서 빠졌습니다[1] |
| `stat` 의 `starttime` 단위 | Linux 2.6 전에는 jiffies, 2.6 부터는 클록 틱 (clock tick) 입니다[1] |
| 마운트 옵션 `hidepid=` | Linux 3.3 부터 있습니다[1]. 값은 아래 "함정과 한계" 에서 다룹니다 |

실제로 어떤 옵션으로 마운트됐는지는 수집한 `/proc/mounts` 의 `proc` 줄(예: `proc /proc proc rw,relatime,hidepid=2 0 0`)에서 확인합니다[2]. 예전 procfs 는 같은 PID 네임스페이스 안의 마운트가 옵션을 함께 썼지만, 지금 procfs 는 마운트할 때마다 따로 인스턴스를 만들어 마운트마다 옵션이 다를 수 있습니다[2]. 그래서 `proc` 줄이 여럿이면 줄마다 옵션을 봅니다.

## 구조

수집에서 자주 쓰는 파일은 아래와 같습니다.

| 파일 | 담긴 것 | 형식과 주의 |
|---|---|---|
| `/proc/PID/exe` | 실행 파일 경로 | 심볼릭 링크입니다. 실행 파일이 지워지면 경로 뒤에 ` (deleted)` 가 붙고, 링크를 열면 실행 파일 자체가 열립니다[1] |
| `/proc/PID/cmdline` | 명령줄 전체 | 인수 사이와 마지막 인수 뒤에 NUL(0x00) 이 있습니다. 좀비 프로세스면 비어 있습니다[1] |
| `/proc/PID/comm` | 명령 이름 | NUL 을 포함해 16바이트(`TASK_COMM_LEN`)를 넘으면 조용히 잘립니다. 스레드가 스스로 바꿀 수 있습니다[1] |
| `/proc/PID/cwd` | 작업 폴더 | 심볼릭 링크[1] |
| `/proc/PID/root` | 프로세스의 루트 폴더 | chroot 로 정한 루트를 가리키고, 네임스페이스와 마운트까지 프로세스와 같은 시야를 보여 줍니다[1] |
| `/proc/PID/environ` | 시작할 때의 환경 변수 | NUL 로 구분합니다. `execve` 뒤에 `putenv` 등으로 바꾼 값은 반영되지 않습니다[1] |
| `/proc/PID/fd/` | 열린 파일 디스크립터 | 번호마다 링크가 있고, 파이프·소켓은 `type:[inode]`(예: `socket:[2248868]`), 아이노드 없는 것은 `anon_inode:` 모양입니다[1] |
| `/proc/PID/maps` | 메모리 배치 | `address perms offset dev inode pathname` 순서입니다. 아이노드 0 은 파일과 이어지지 않은 영역이고, `[heap]`·`[stack]`·`[vdso]` 같은 가짜 경로가 있으며, 지워진 파일이면 ` (deleted)` 가 붙습니다[1] |
| `/proc/PID/map_files/` | 매핑된 파일 링크 | 이름이 "시작주소-끝주소" 인 링크입니다[1] |
| `/proc/PID/stat` | 상태 한 줄 | 공백으로 구분한 필드이고, 2번째 필드 `comm` 은 괄호로 싸여 있으며, 22번째 필드가 `starttime` 입니다[1] |
| `/proc/PID/status` | 사람이 읽기 쉬운 상태 | `Name`, `State`, `PPid`, `Uid`, `Gid` 등. `Uid`·`Gid` 는 real·effective·saved·filesystem 네 값입니다[1] |
| `/proc/stat` 의 `btime` | 부팅 시각 | 1970 epoch 초, UTC[1] |
| `/proc/uptime` | 가동 시간 | 첫 값은 잠자기를 포함한 가동 시간(초)입니다[1] |

`cwd`·`exe`·`environ`·`maps`·`map_files` 는 ptrace 접근 검사(`PTRACE_MODE_READ_FSCREDS`)를 통과해야 읽힙니다[1]. `stat` 의 일부 필드도 같은 검사에 걸리면 0 으로 나옵니다[1]. 그래서 수집은 root 로 해야 빠지는 값이 없습니다. 스레드가 여럿인 프로세스에서 주 스레드가 먼저 끝났으면 `cwd`·`exe`·`fd/`·`root` 내용을 볼 수 없습니다[1].

`/proc/PID` 아래 파일의 소유자는 보통 그 프로세스의 실효(effective) UID·GID 이고, 프로세스의 dumpable 속성이 1 이 아니면 `root:root` 입니다[1]. `/proc/PID` 폴더에 `stat` 을 하면 프로세스의 UID·GID 를 알 수 있어서, `hidepid=2` 는 남의 폴더를 아예 숨깁니다[1]. UID 를 사용자 이름으로 바꾸는 법은 [UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md)에서 다룹니다.

## 증거로서 의미

### 증명하는 것

- 수집 순간 이 PID 의 프로세스가 돌고 있었고, 그 실행 파일 경로(`exe`)와 부모(`PPid`), 계정(`Uid`)이 무엇이었는지.
- 실행 파일이 이미 지워졌는지(`exe` 의 ` (deleted)`)와, 그 경우에도 프로세스가 도는 동안에는 `exe` 를 열어 파일 내용을 떠 올 수 있다는 것[1][3].
- 수집 순간 열려 있던 파일·소켓·파이프(`fd/`)와 메모리에 올라온 라이브러리·파일(`maps`).
- 부팅 뒤 언제 시작했는지(`starttime`)와, 부팅 시각을 더한 시작 시각.

### 증명하지 못하는 것

- 이미 끝난 프로세스, 수집 전의 상태, 수집 전에 열었다 닫은 파일.
- `cmdline` 의 진실성. 프로세스가 `execve` 뒤에 `argv` 문자열을 고치면 고친 값이 보이고, `prctl` 의 `PR_SET_MM_ARG_START` 로 가리키는 메모리 위치 자체를 바꿀 수도 있어서, 이 파일은 "프로세스가 보여 주고 싶은 명령줄" 입니다[1].
- `comm`·`Name` 의 진실성. 스레드가 스스로 바꿀 수 있습니다[1].
- 지금의 환경 변수. `environ` 은 시작할 때 값만 보여 줍니다[1].
- 누가 왜 실행 파일을 지웠는지. ` (deleted)` 는 경로가 끊겼다는 뜻일 뿐입니다[1].
- `/proc` 이 속지 않았다는 것. 커널을 건드린 루트킷이 `/proc` 결과를 가릴 가능성이 있으므로 메모리 이미지와 대조합니다. 대조 방법은 [루트킷 찾기](../../03-techniques/analysis/rootkit-detection.md)와 [메모리 분석](../../03-techniques/analysis/memory-analysis.md)에서 다룹니다.

보고서에는 "수집 시각 기준으로 PID 4242 가 UID 1001 로 돌고 있었고 실행 파일 경로는 `/tmp/.cache/kworker (deleted)` 였다" 처럼 수집 순간의 상태만 씁니다(만든 예시).

## 시각 해석

`/proc` 에서 날짜로 바꿀 수 있는 값은 프로세스 시작 시각 하나입니다. `stat` 의 22번째 필드 `starttime` 은 부팅 뒤 프로세스가 시작할 때까지의 클록 틱 수이고, `sysconf(_SC_CLK_TCK)` 로 나눠야 초가 됩니다[1]. 여기에 `/proc/stat` 의 `btime`(부팅 시각, UTC epoch 초)을 더하면 시작 시각이 UTC 로 나옵니다[1]. 이 계산과 단위 이야기는 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

클록 틱 값(USER_HZ)은 대부분의 아키텍처에서 100 이지만 모든 시스템에서 같지는 않습니다[1]. dissect.target 은 100 으로 나눠 시작 시각을 계산하고, 실제 값은 `getconf CLK_TCK` 로 얻습니다[4]. 그래서 수집할 때 `getconf CLK_TCK` 출력도 함께 남깁니다.

`btime` 은 초 단위라서 시작 시각은 초보다 정밀하지 않습니다. 부팅 뒤에 시스템 시계를 크게 바꾸면 `btime` 과 실제 부팅 순간이 어긋날 가능성이 있으므로, [부팅과 종료 기록](../system-info/boot-shutdown.md)의 부팅 시각과 맞춰 봅니다.

수집 시각은 `btime` 에 `/proc/uptime` 첫 값을 더해 구할 수 있고, dissect.target 도 이 방법으로 수집 시점을 정합니다[4].

## 함정과 한계

**hidepid 로 목록이 빠진다.** `hidepid=` 옵션에 따라 다른 사용자의 프로세스가 보이는 정도가 달라집니다[2].

| 값 | 뜻 |
|---|---|
| `0` 또는 `off` | 누구나 모든 `/proc/PID` 에 접근합니다. 기본값입니다 |
| `1` 또는 `noaccess` | 자기 것이 아닌 `/proc/PID` 안의 파일을 읽지 못합니다. 폴더는 보입니다 |
| `2` 또는 `invisible` | `1` 에 더해 남의 `/proc/PID` 폴더가 아예 보이지 않습니다 |
| `4` 또는 `ptraceable` | ptrace 할 수 있는 프로세스의 폴더만 보입니다 |

`gid=` 로 정한 그룹은 이 제한에서 빠집니다[2]. 일반 계정으로 수집하면 이 옵션 때문에 프로세스가 통째로 빠질 수 있습니다.

**`/proc/PID` 위에 다른 폴더를 마운트해 가릴 수 있다.** UAC 의 `revel_hidden_processes` 수정 항목은 먼저 `mount` 와 여러 `ps` 출력을 남긴 뒤, `/proc/숫자` 에 바인드 마운트된 폴더를 `umount` 해서 가려진 프로세스를 드러냅니다[3]. 그래서 `mount` 출력에 `/proc/숫자` 를 대상으로 하는 줄이 있으면 프로세스를 숨기려 한 흔적으로 보고, 가려진 PID 를 따로 조사합니다. 이 수정 항목은 시스템 상태를 바꾸므로, 쓰기 전과 뒤의 출력을 모두 보존합니다.

**` (deleted)` 를 곧바로 악성으로 읽지 않는다.** 이 표시는 실행 파일의 경로가 끊겼다는 뜻일 뿐이라서[1], 실행 중인 파일을 패키지 업데이트로 바꿔 끼운 경우에도 붙을 가능성이 있습니다. [dpkg·apt 기록](../packages/dpkg-apt.md)이나 [rpm·dnf·yum 기록](../packages/rpm-dnf.md)과 파일 시스템 시각을 함께 봅니다.

**이름만 보고 판단하지 않는다.** `comm` 은 16바이트에서 잘리고 바꿀 수도 있어서[1], 커널 스레드처럼 보이는 이름이라도 `exe` 와 `cmdline` 을 봐야 합니다. Volatility 3 의 `linux.psaux` 는 사용자 영역 메모리(`mm`)가 없는 커널 스레드를 `[이름]` 처럼 대괄호로 보여 주므로, 커널 스레드 이름을 쓰면서 인수가 대괄호 없이 나오는 프로세스는 사용자 프로세스입니다[6].

**수집 도구 자신이 프로세스를 만든다.** `ps`, `ls`, `cat`, `strings` 같은 수집 명령도 수집 목록에 나오므로 수집 도구의 PID 를 따로 적어 둡니다.

**도구 필드 이름을 확인한다.**

- dissect.target 의 `processes` 는 `runtime` 필드에 경과 시간(`timedelta`)의 `.seconds` 값을 넣습니다[4]. 파이썬의 이 값은 하루 미만의 나머지 초라서, 하루 넘게 돈 프로세스는 날짜 수가 빠집니다. 시작 시각 `ts` 로 경과 시간을 다시 계산합니다.
- Velociraptor 의 `Linux.Sys.Maps` 는 `maps` 줄을 정규식으로 나누면서 `offset` 필드를 `Size` 로, `inode` 필드를 `PermInt` 로 이름 붙입니다[5]. 크기는 `EndHex − StartHex` 로 따로 구합니다.
- `stat` 의 `comm` 필드에는 공백과 괄호가 들어갈 수 있습니다. dissect.target 은 첫 `(` 와 마지막 `)` 사이를 이름으로 잘라 이 문제를 피합니다[4]. 직접 나눌 때도 같은 방법을 씁니다.

## 직접 분석해 보기

### 헥스로 한 번

`cmdline` 은 NUL 구분이라 `cat` 으로 보면 인수가 붙어 보입니다. `xxd` 로 보면 경계가 드러납니다. 아래는 명세대로 만든 예시이고, 경로는 지어낸 값입니다.

```
$ xxd -g1 /proc/4242/cmdline
00000000: 2f 74 6d 70 2f 2e 63 61 63 68 65 2f 6b 77 6f 72  /tmp/.cache/kwor
00000010: 6b 65 72 00 2d 63 00 2f 74 6d 70 2f 2e 63 61 63  ker.-c./tmp/.cac
00000020: 68 65 2f 63 66 67 00                             he/cfg.
```

0x13 과 0x16 의 `00` 이 인수 경계이고, 0x26 의 마지막 `00` 은 끝 표시입니다[1]. 인수는 `/tmp/.cache/kworker`, `-c`, `/tmp/.cache/cfg` 세 개입니다. 같은 프로세스의 나머지 파일도 만든 예시로 이어 보면 아래와 같습니다.

```
$ readlink /proc/4242/exe
/tmp/.cache/kworker (deleted)
$ cat /proc/4242/stat
4242 (kworker) S 1 4241 4241 0 -1 4194560 1520 0 3 0 812 95 0 0 20 0 1 0 361200 ...
$ grep btime /proc/stat
btime 1735689600
$ grep ' (deleted)' /proc/4242/maps
5610a2c00000-5610a2c21000 r-xp 00001000 fd:01 1311820   /tmp/.cache/kworker (deleted)
```

`stat` 의 22번째 필드는 361200 이고, 클록 틱이 100 이면 3612초입니다. `btime` 1735689600 은 2025-01-01 00:00:00 UTC 이므로 시작 시각은 2025-01-01 01:00:12 UTC 입니다. 4번째 필드 1 이 부모 PID 입니다[1]. `maps` 줄은 앞에서부터 주소 범위, 권한 `r-xp`, 파일 안 오프셋, 장치 `fd:01`, 아이노드 1311820, 경로이고, 경로 뒤의 ` (deleted)` 는 매핑한 파일이 지워졌다는 표시입니다[1].

`environ` 도 NUL 구분이라 `tr '\000' '\n' < /proc/PID/environ` 처럼 줄을 바꿔 봅니다[1].

### 공개 도구로 한 번

- **UAC** — `live_response/process/procfs_information` 은 `ls -l /proc/[0-9]*`, 모든 프로세스의 `exe`·`cwd` 링크 목록을 모으고, PID 마다 `fd`·`map_files` 목록과 `task/PID/children`, `comm`, `maps`, `mounts`, `stack`, `stat`, `status`, `net/unix` 를 받으며, `cmdline`·`environ` 은 `strings` 로 받습니다[3]. `/proc` 에는 있는데 `ps ax` 출력에 없는 PID 는 `hidden_pids_for_ps_command.txt` 에 적습니다[3]. `live_response/process/deleted` 는 `exe` 가 ` (deleted)` 인 프로세스의 실행 파일을 `dd ... bs=1024 count=20000` 으로 앞부분(약 20MB)만 `recovered_exe` 로 떠 오고, 그 프로세스의 메모리 영역과 지워진 파일을 가리키는 fd 도 모읍니다[3]. memfd 와 `/dev/shm` 쪽은 [임시 폴더와 메모리 파일 시스템](../file-activity/tmp-shm.md)에서 다룹니다.
- **Velociraptor** — `Linux.Sys.Pslist` 는 `Pid`, `Ppid`, `Name`, `CommandLine`, `Exe`, 실행 파일 해시, `Username`, `CreateTime`, `RSS` 를 보여 주고, `Exe` 가 `(deleted)` 로 끝나면 `Deleted` 를 참으로 둡니다[5]. `Linux.Sys.Maps` 는 `/proc/PID/maps` 를 줄마다 나눠 보여 줍니다[5].
- **dissect.target** — 수집본에 `/proc` 이 들어 있으면 `processes` 가 시작 시각(`ts`), 이름, 상태, PID, 경과 시간, 부모 PID, 부모 이름을 레코드로 냅니다[4].
- **Volatility 3** — 메모리 이미지에서 `linux.pslist`(PID, TID, PPID, COMM, UID, GID, EUID, EGID, CREATION TIME), `linux.psaux`(ARGS), `linux.envars`(KEY, VALUE), `linux.pstree`, `linux.psscan`(메모리를 검색해 찾은 프로세스와 EXIT_STATE)을 봅니다[6]. `linux.psaux` 는 사용자 영역의 인수 영역(`arg_start`~`arg_end`)을 읽고, `/proc/PID/cmdline` 도 이 영역을 보여 주므로, 프로세스가 고친 명령줄은 메모리에서도 고친 값으로 나옵니다[1][6]. 이 영역이 4096바이트를 넘으면 읽지 않습니다[6].

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [감사 로그의 실행 기록](auditd-execve.md) | 같은 PID·PPID 의 `execve` 기록에 남은 원래 인수와 경로 |
| [프로세스 회계](process-accounting.md) | 수집 전에 끝난 프로세스의 이름과 시각 |
| [셸 명령 기록](shell-history/index.md) | 프로세스를 띄운 명령 |
| [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) | 항목의 `_PID`, `_COMM`, `_EXE`, `_CMDLINE` 필드[7] |
| [임시 폴더와 메모리 파일 시스템](../file-activity/tmp-shm.md) | `fd` 가 가리키는 `/dev/shm`·`memfd:` 파일 |
| [마운트 기록](../devices/mounts.md) | `/proc/숫자` 를 가리는 마운트, `/proc` 의 `hidepid` |
| [메모리 분석](../../03-techniques/analysis/memory-analysis.md) | `/proc` 목록과 메모리 프로세스 목록의 차이 |

## 실습

공개 시험 데이터는 대부분 디스크 이미지라서 `/proc` 내용이 없습니다. 연습용 가상 머신에서 UAC 로 라이브 수집을 한 번 만든 뒤 아래 질문을 풀어 봅니다.

1. `hidden_pids_for_ps_command.txt` 에 PID 가 있다면, 수집 도중에 끝난 프로세스인지 `ps` 에서 숨은 프로세스인지 무엇으로 가릴까요?
2. `running_processes_full_paths.txt` 에서 ` (deleted)` 로 끝나는 줄을 찾고, 그 경로가 패키지 업데이트로 바뀐 파일인지 패키지 기록으로 확인해 봅니다.
3. 아무 프로세스나 골라 `stat` 의 `starttime` 과 `/proc/stat` 의 `btime` 으로 시작 시각을 UTC 로 계산하고, Velociraptor 의 `CreateTime` 이나 dissect.target 의 `ts` 와 비교해 봅니다.
4. 같은 프로세스의 `comm`, `cmdline` 첫 인수, `exe` 링크가 서로 다른 경우를 찾아 어느 값을 보고서에 쓸지 정해 봅니다.
5. 소켓 fd 의 `socket:[inode]` 아이노드를 `/proc/net/tcp` 나 `net/unix` 에서 찾아 연결 상대를 잇습니다.

## 참고 문헌

1. Linux man-pages, proc(5) — https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
2. Linux kernel, Documentation/filesystems/proc.rst (4.1 Mount options) — https://github.com/torvalds/linux/blob/master/Documentation/filesystems/proc.rst
3. UAC, artifacts/live_response/process/procfs_information.yaml·process/deleted.yaml·modifiers/revel_hidden_processes.yaml — https://github.com/tclahr/uac/blob/main/artifacts/live_response/process/procfs_information.yaml , https://github.com/tclahr/uac/blob/main/artifacts/live_response/process/deleted.yaml , https://github.com/tclahr/uac/blob/main/artifacts/live_response/modifiers/revel_hidden_processes.yaml
4. dissect.target, plugins/os/unix/linux/proc.py·processes.py — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/proc.py , https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/processes.py
5. Velociraptor, artifacts/definitions/Linux/Sys/Pslist.yaml·Maps.yaml — https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Sys/Pslist.yaml , https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Sys/Maps.yaml
6. Volatility 3, framework/plugins/linux/pslist.py·psaux.py·psscan.py·envars.py·pstree.py — https://github.com/volatilityfoundation/volatility3/tree/develop/volatility3/framework/plugins/linux
7. systemd, man/systemd.journal-fields.xml — https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
