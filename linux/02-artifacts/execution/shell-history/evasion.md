---
title: "기록 지우기와 끄기"
parent: "셸 명령 기록"
grand_parent: "아티팩트 · 실행 흔적"
nav_order: 450
---

# 기록 지우기와 끄기 (History Evasion)

셸 기록이 비었거나 줄었을 때 어떤 설정과 명령이 그렇게 만들 수 있는지, 그리고 그 조작이 어디에 흔적을 남기는지 정리합니다.

## 무엇이 기록을 없애거나 줄이나

셸 기록은 셸 스스로 쓰는 파일이라서 사용자가 셸 변수나 내장 명령으로 저장 방식을 바꿀 수 있습니다. 조사에서 빈 기록 파일을 만났을 때 먼저 떠올릴 조건은 아래와 같습니다. 각 셸의 기본 저장 규칙과 파일 형식은 [bash 기록](bash.md)과 [zsh·fish 기록](zsh-fish.md)에 있습니다.

| 셸 | 조건 | 기록에 미치는 효과 |
|---|---|---|
| bash | `HISTFILE` 을 풀어 버림(unset) | 셸이 끝날 때 기록을 저장하지 않음[1] |
| bash | `HISTSIZE=0` | 명령이 기록 목록에 들어가지 않음[1] |
| bash | `HISTFILESIZE=0` | 기록 파일을 0 바이트로 자름[1] |
| bash | `history` 셸 옵션을 끔(`set +o history`) | 기록 기능이 꺼짐. 이 옵션은 대화형 셸에서만 기본으로 켜짐[1] |
| bash | `HISTCONTROL` 에 `ignorespace`·`ignoreboth` 가 있고 명령 앞에 공백 | 그 줄을 목록에 넣지 않음[1] |
| bash | `history -c` / `history -d` / `history -w` | 목록 전체 삭제 / 항목 삭제 / 현재 목록으로 파일 덮어쓰기[1] |
| bash | 셸이 SIGKILL 로 끝남 | 종료 때 저장하는 코드가 돌지 않음[2][3] |
| bash | 기록 파일이 `/dev/null` 을 가리키는 심볼릭 링크 | 저장한 내용이 바로 사라짐[2] |
| zsh | `HISTFILE` 이 설정되지 않음, `SAVEHIST` 가 작음 | 저장하지 않음, 적게 저장함[4] |
| zsh | `HIST_IGNORE_SPACE` 옵션, `HISTORY_IGNORE` 패턴 | 해당 줄을 저장하지 않음[4] |
| fish | `fish_history` 를 빈 문자열로 둠, `fish --private`(`-P`), `$fish_private_mode` 가 비어 있지 않음 | 디스크에 저장하지 않음[5] |
| fish | `fish_should_add_to_history` 함수 정의 | 이 함수가 저장 여부를 모두 결정함[5] |
| fish | `history clear` / `history clear-session` / `history delete` | 파일 비움 / 현재 세션 기록만 지움 / 항목 삭제[5] |

bash 는 SIGHUP·SIGTERM 으로 끝나는 대화형 셸에서는 기록을 저장합니다[2]. SIGKILL 은 프로세스가 잡을 수 없는 신호라서[3] 이 경로를 타지 않고, 이런 세션의 명령은 파일에 없을 수 있습니다. 조작이 아니어도 기록이 빌 수 있다는 점은 아래 "증명하지 못하는 것" 에서 다룹니다.

## 흔적이 남는 곳

### 설정 파일

기록을 끄는 설정을 오래 두려면 셸 시작 파일에 적어야 합니다. `~/.bashrc`, `~/.bash_profile`, `~/.profile`, `/etc/bash.bashrc`, `/etc/profile`, `/etc/profile.d/*`, zsh 의 `~/.zshrc`·`/etc/zshrc` 등, fish 의 `~/.config/fish/config.fish`·`/etc/fish/config.fish` 에서 `HISTFILE`, `HISTSIZE`, `HISTFILESIZE`, `HISTCONTROL`, `SAVEHIST`, `fish_history`, `fish_private_mode` 를 바꾸는 줄을 찾습니다. UAC 는 이 파일들을 모으고 `HISTFILE=` 줄을 grep 해서 경로를 바꾼 기록 파일도 함께 모읍니다[7]. 시작 파일 자체를 해석하는 법은 [셸 시작 파일](../../persistence/shell-startup.md)에 있습니다.

### 기록 파일 자체

기록 파일에서는 네 가지 상태를 봅니다.

- **크기 0**: `HISTFILESIZE=0`, fish `history clear`, 외부 명령으로 비운 경우에 생깁니다.
- **심볼릭 링크**: bash 는 기록 파일(심볼릭 링크면 링크가 가리키는 대상)이 일반 파일이 아니면 임시 파일을 거치지 않고 그 경로를 바로 열어 씁니다[2]. `/dev/null` 을 가리키는 링크는 남아 있고 내용만 사라집니다.
- **불변 속성 (immutable)**: ext4 아이노드의 `i_flags` 에 `EXT4_IMMUTABLE_FL`(0x10)이 켜진 파일은 바꿀 수 없습니다[9]. Velociraptor `Linux.Forensics.ImmutableFiles` 는 ext4 를 직접 읽어 이 플래그가 있는 파일을 찾습니다[8]. 속성 일반은 [권한·확장 속성](../../../01-foundations/filesystem/permissions-xattr.md)을 봅니다.
- **사본**: UAC 는 `.bash_history~`, `.bash_history.*`, `.zsh_history.*`, `.zhistory~`, `fish_history.*` 같은 백업·회전 사본까지 모읍니다[7]. 원본을 지운 뒤에도 사본이 남아 있을 수 있습니다.

bash 가 파일을 덮어쓸 때는 같은 폴더에 `원래이름-PID.tmp` 임시 파일을 만든 뒤 이름을 바꿔 덮습니다[2]. 쓰기에 실패하면 임시 파일을 지우므로[2] 보통은 남지 않습니다. 덮어쓰기 때문에 옛 내용이 할당이 풀린 블록에 남을 가능성은 [bash 기록](bash.md)과 [지운 파일 되살리기](../../../03-techniques/analysis/file-recovery.md)를 봅니다.

### 실행 기록 — 내장 명령과 외부 명령의 차이

bash 는 명령 이름이 함수나 내장 명령과 맞으면 그 자리에서 처리하고, 둘 다 아닐 때만 `PATH` 에서 프로그램을 찾아 실행합니다[1]. 그래서 `history -c`, `unset HISTFILE`, `set +o history`, `shopt`, `export` 는 새 프로세스를 만들지 않고, [감사 로그의 실행 기록](../auditd-execve.md)이나 [프로세스 회계](../process-accounting.md)에 남지 않습니다. 반대로 `rm`, `shred`, `truncate`, `ln`, `chattr`, `cat` 같은 외부 명령은 execve 를 거치므로 규칙이나 회계가 켜져 있으면 남습니다.

리디렉션(`>`)은 셸이 처리합니다[1]. `cat /dev/null > ~/.bash_history` 에서 EXECVE 인수에는 `cat /dev/null` 만 들어가고 기록 파일 이름은 들어가지 않습니다. 파일 이름이 인수에 있어야 걸리는 규칙은 이런 형태를 놓칩니다.

공개 탐지 규칙은 이런 문자열을 봅니다[6]. 기록 파일·감사 로그·메모리에서 찾을 검색어로도 쓸 수 있습니다.

| 규칙 | 보는 곳 | 찾는 문자열 |
|---|---|---|
| Sigma `lnx_shell_clear_cmd_history` | 로그 전체 키워드 | `history -c`, `history -w`, `export HISTFILESIZE=0`, `shopt -ou history`, `ln -sf /dev/null *sh_history`, `rm *sh_history`, `shred *sh_history`, `truncate -s0 *sh_history`, `chattr +i*sh_history`, `cat /dev/null >*sh_history` 등. `unset HISTFILE` 은 오탐이 많아 주석으로 빠져 있음 |
| Sigma `lnx_auditd_susp_histfile_operations` | auditd `EXECVE` | 레코드 안에 `.bash_history`, `.zsh_history`, `.zhistory`, `.history`, `.sh_history`, `fish_history` |
| Sigma `proc_creation_lnx_susp_history_delete` | 프로세스 생성 | 실행 파일이 `/rm`·`/unlink`·`/shred` 로 끝나고, 명령줄에 `/.bash_history`·`/.zsh_history` 가 들어 있거나 명령줄이 `_history`·`.history`·`zhistory` 로 끝남 |

### TTY 감사

`pam_tty_audit` 로 TTY 감사를 켠 계정은 커널이 TTY 입력을 감사 로그에 남깁니다[10]. 키 입력 자체라서 내장 명령도 기록됩니다. 기본값은 어떤 TTY 도 감사하지 않는 것이라[10] PAM 설정에 이 모듈이 있을 때만 기대할 수 있습니다. 레코드 형식은 `TTY`(1319, 커널, 관리용 TTY 입력)와 `USER_TTY`(1124)입니다[11]. `aureport --tty` 나 `ausearch -m TTY -i` 로 봅니다[10][12]. 비밀번호 입력은 `log_passwd` 옵션이 없으면 남지 않지만, ssh 세션 안에서 원격 호스트에 치는 비밀번호는 남을 수 있습니다[10]. 감사 로그 파일 위치와 줄 모양은 [감사 로그 형식](../../../01-foundations/logging/auditd-format.md)을 봅니다.

### 메모리

bash 는 명령을 먼저 기록 목록에 넣고 파일 저장은 셸이 끝날 때 합니다[1]. 기록 파일을 지우거나 `HISTFILE` 을 풀어도 셸 프로세스가 살아 있으면 목록이 메모리에 있고, Volatility 3 `linux.bash` 가 프로세스 이름이 `bash`, `sh`, `dash` 인 태스크의 힙에서 이 목록을 찾습니다[13]. `history -c` 뒤에는 해제된 힙 영역에 문자열이 남아 있을 가능성만 있습니다. 메모리 분석 절차는 [메모리 분석](../../../03-techniques/analysis/memory-analysis.md)에 있습니다.

## 증거로서 의미

**증명하는 것**: 설정 줄, `/dev/null` 링크, 불변 플래그, 0 바이트 파일은 "그 계정의 기록이 남지 않도록 된 상태" 를 보여 줍니다. 외부 명령으로 기록 파일을 지웠거나 비웠다면 execve 규칙이나 프로세스 회계가 켜진 시스템에서 그 실행 기록이 남습니다. TTY 감사가 켜진 계정이면 내장 명령 입력까지 남습니다.

**증명하지 못하는 것**: 빈 기록만으로 "지웠다" 고 단정하지 못합니다. 스크립트나 `ssh 호스트 명령` 처럼 비대화형 셸만 썼으면 bash 는 기본으로 기록하지 않고[1], zsh 는 `HISTFILE` 을 설정하지 않으면 애초에 저장하지 않으며[4], SIGKILL 로 끝난 세션도 저장되지 않습니다[2][3]. 설정 줄이 있다는 사실만으로 누가 언제 그 줄을 넣었는지도 알 수 없습니다. 보고서에는 "이 계정의 `~/.bash_history` 는 `/dev/null` 을 가리키는 심볼릭 링크였고, `~/.bashrc` 에 `HISTFILESIZE=0` 줄이 있다" 처럼 상태까지만 씁니다.

## 시각 해석

ext4 아이노드의 시각은 epoch 초이고 UTC 기준입니다[9]. `i_mtime`(0x10)은 내용이 바뀐 시각, `i_ctime`(0x0C)은 아이노드가 바뀐 시각입니다[9]. 설정 파일에 줄을 넣으면 그 파일의 mtime 이 바뀝니다. 불변 속성을 켜는 것도 아이노드를 바꾸는 일이라 기록 파일의 ctime 이 그 시각으로 바뀌었을 가능성이 있습니다. 심볼릭 링크는 새 아이노드이므로 링크 아이노드의 시각이 링크를 만든 때를 가리킵니다. 시각 값 읽는 법은 [Linux 의 시각 값](../../../01-foundations/value-decoding/time-values.md)을 봅니다.

## 함정과 한계

- 기록 파일 하나만 보고 끝내지 않습니다. `/root`, 다른 사용자, zsh·fish 기록은 따로 남습니다. `sudo -i` 로 연 root 셸의 기록 위치는 [bash 기록](bash.md)과 [sudo·su 사용 기록](../../logins/sudo-su.md)을 봅니다.
- `HISTFILE` 을 다른 경로로 바꾼 경우 기본 경로 파일만 모으는 도구는 그 파일을 놓칩니다. 시작 파일의 `HISTFILE=` 줄을 먼저 봅니다[7].
- Ubuntu 기본 `~/.bashrc` 는 `HISTCONTROL=ignoreboth` 라서 앞에 공백을 붙인 명령이 기본 설정만으로도 빠집니다([bash 기록](bash.md)의 배포판 기본값 표). 이 설정 줄은 조작 흔적이 아닙니다.
- 탐지 규칙이 찾는 문자열은 정상 관리 작업이나 기록 파일을 정리하는 프로그램에서도 나옵니다[6].

## 직접 분석해 보기

**헥스로 한 번.** ext4 아이노드에서 `i_mode`(0x00, 2바이트), `i_size_lo`(0x04), `i_flags`(0x20), `i_block`(0x28, 60바이트)을 봅니다[9]. 60 바이트보다 짧은 심볼릭 링크 대상은 `i_block` 안에 바로 들어갑니다[9]. 아래는 명세로 만든 예시입니다.

```text
만든 예시 1 — /dev/null 을 가리키는 심볼릭 링크인 기록 파일의 아이노드
0x00: FF A1                 i_mode = 0xA1FF  → 0xA000(심볼릭 링크) + 0777
0x04: 09 00 00 00           i_size_lo = 9    → 대상 문자열 길이
0x28: 2F 64 65 76 2F 6E 75 6C 6C             → "/dev/null"

만든 예시 2 — 불변 속성이 켜진 기록 파일의 아이노드
0x00: 80 81                 i_mode = 0x8180  → 0x8000(일반 파일) + 0600
0x20: 10 00 08 00           i_flags = 0x00080010 → 0x80000(익스텐트 사용) + 0x10(불변)
```

**공개 도구로 한 번.** Velociraptor `Linux.Forensics.ImmutableFiles` 는 `SearchFilesGlob`(기본값 `/home/*`)에 맞는 경로 가운데 플래그에 `IMMUTABLE` 이 있는 파일을 돌려주고, 결과에 `CTime` 이 함께 나옵니다[8]. 기본값은 홈 폴더 한 단계만 보므로 기록 파일을 보려면 이 값을 `/home/*/.*history` 처럼 기록 파일 경로로 바꿔 돌립니다. 수집 단계에서는 UAC 로 기록 파일·사본·시작 파일을 함께 모읍니다[7]. ext4 구조 일반은 [ext4](../../../01-foundations/filesystem/ext4/index.md)를 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [감사 로그의 실행 기록](../auditd-execve.md) | 기록 파일을 지우거나 비운 외부 명령의 실행과 인수 |
| [프로세스 회계](../process-accounting.md) | `rm`·`shred` 같은 외부 명령이 실행된 사실 |
| [셸 시작 파일](../../persistence/shell-startup.md) | 기록을 끄는 설정 줄과 그 파일의 변경 시각 |
| [메모리 분석](../../../03-techniques/analysis/memory-analysis.md) | 살아 있는 셸의 기록 목록 |
| [타임라인 만들기](../../../03-techniques/analysis/timeline.md) | 설정 파일 mtime, 기록 파일 ctime, 로그인 기록을 한 줄로 맞추기 |

흔적 지우기 전체를 판단하는 흐름은 [흔적을 지웠나](../../../04-scenarios/insider/anti-forensics.md)에 있습니다.

## 실습

Linux 디스크 이미지가 들어 있는 공개 검체(예: NIST CFReDS)로 풀어 봅니다.

1. 사용자마다 기록 파일의 형식(일반 파일·심볼릭 링크)과 크기를 표로 만듭니다. 0 바이트이거나 링크인 파일이 있습니까?
2. 그 사용자의 시작 파일에 `HISTFILE`, `HISTSIZE`, `HISTFILESIZE`, `HISTCONTROL` 줄이 있습니까? 배포판 기본값과 다른 값은 무엇입니까?
3. 기록 파일 아이노드의 `i_flags` 에 0x10 이 켜져 있습니까? 켜져 있다면 ctime 은 언제이고, 그 무렵 로그인 기록에 누가 있습니까?
4. 감사 로그가 있다면 기록 파일 이름이 인수에 들어간 `EXECVE` 레코드가 있습니까? 없다면 그것이 "지우지 않았다" 는 뜻인지, 규칙이 없었다는 뜻인지 무엇으로 가립니까?

## 참고 문헌

1. GNU Bash 5.2 매뉴얼 페이지 `doc/bash.1`(HISTORY, 셸 변수, `history`·`set` 내장 명령, COMMAND EXECUTION, REDIRECTION). https://github.com/tianon/mirror-bash/blob/bash-5.2/doc/bash.1
2. GNU Bash 5.2 소스 `lib/readline/histfile.c`(`history_tempfile`, `history_do_write`), `sig.c`(`termsig_handler`). https://github.com/tianon/mirror-bash/tree/bash-5.2
3. Linux man-pages `signal(7)`. https://github.com/mkerrisk/man-pages/blob/master/man7/signal.7
4. zsh 문서 `Doc/Zsh/params.yo`(`HISTFILE`, `SAVEHIST`, `HISTORY_IGNORE`), `Doc/Zsh/options.yo`(`HIST_IGNORE_SPACE`). https://github.com/zsh-users/zsh/tree/master/Doc/Zsh
5. fish 문서 `doc_src/interactive.rst`, `doc_src/language.rst`, `doc_src/cmds/history.rst`, `doc_src/cmds/fish_should_add_to_history.rst`. https://github.com/fish-shell/fish-shell/tree/master/doc_src
6. SigmaHQ 규칙 `rules/linux/builtin/lnx_shell_clear_cmd_history.yml`, `rules/linux/auditd/execve/lnx_auditd_susp_histfile_operations.yml`, `rules/linux/process_creation/proc_creation_lnx_susp_history_delete.yml`. https://github.com/SigmaHQ/sigma/tree/master/rules/linux
7. UAC `artifacts/files/shell/bash.yaml`, `zsh.yaml`, `fish.yaml`, `common.yaml`. https://github.com/tclahr/uac/tree/main/artifacts/files/shell
8. Velociraptor `Linux.Forensics.ImmutableFiles`. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Forensics/ImmutableFiles.yaml
9. Linux 커널 문서 ext4 `inodes.rst`, `ifork.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/inodes.rst , https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/ifork.rst
10. Linux-PAM `pam_tty_audit(8)`. https://github.com/linux-pam/linux-pam/blob/master/modules/pam_tty_audit/pam_tty_audit.8.xml
11. linux-audit 메시지 사전 `specs/messages/message-dictionary.csv`. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
12. linux-audit `aureport(8)`, `ausearch(8)`. https://github.com/linux-audit/audit-userspace/tree/master/docs
13. Volatility 3 `plugins/linux/bash.py`. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/bash.py
