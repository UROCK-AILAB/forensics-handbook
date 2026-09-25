---
title: "셸 명령 기록"
parent: "아티팩트 · 실행 흔적"
nav_order: 420
has_children: true
has_toc: false
---

# 셸 명령 기록 (Shell History)

bash·zsh·fish 같은 대화형 셸이 사용자가 입력한 명령 줄을 계정 홈 폴더의 기록 파일에 저장해 둔 것이고, 셸과 설정에 따라 파일 이름·저장 시점·시각 유무가 달라집니다.

## 왜 중요한가

셸 기록은 계정이 터미널에서 무엇을 입력했는지를 명령 줄 그대로 보여 주는 드문 자료입니다. 로그인 기록이 "언제 들어왔는가" 를, 감사 로그와 프로세스 회계가 "어떤 프로그램이 실행됐는가" 를 알려 준다면, 셸 기록은 인수와 파이프·리디렉션까지 포함한 입력 줄을 남깁니다. 한 서버의 `.bash_history` 를 옆 서버의 `auth.log` 와 맞춰 보고, SSH 키로 옆 서버들에 들어간 경로를 찾은 사건 분석 사례도 있습니다[15].

다만 셸 기록은 운영체제가 남기는 로그가 아닙니다. 셸 프로그램이 사용자 설정에 따라 쓰는 평문 파일이라서, 사용자가 설정을 바꾸거나 파일을 지우면 그대로 사라집니다. bash 는 `HISTFILE` 이 풀려 있으면 셸이 끝날 때 기록을 저장하지 않고[1], zsh 는 `HISTFILE` 이 설정돼 있지 않으면 기록을 저장하지 않습니다[3]. 그래서 기록 파일을 읽기 전에 그 계정의 셸 설정 파일부터 확인해야 해석이 흔들리지 않습니다.

### 증명하는 것과 증명하지 못하는 것

기록 파일에 줄이 있으면 그 계정의 셸이 그 문자열을 기록 목록에 넣고 파일에 저장했다는 것까지 말할 수 있습니다. bash 는 명령 줄을 history 확장 뒤, 변수 확장 전의 모양으로 목록에 넣으므로[1] 기록에 `$VAR` 가 보이면 실제 값은 다른 자료로 확인합니다.

기록만으로는 다음을 말할 수 없습니다.

- 명령이 성공했는지, 무엇을 출력했는지. fish 는 명령을 실행하기 **전에** 기록에 넣으므로[5] 실행 여부도 기록만으로는 알 수 없습니다.
- 누가 키보드 앞에 있었는지. 기록 파일은 계정 단위로만 나뉩니다.
- 명령별 시각. bash 와 zsh 는 설정을 켜야 시각을 남깁니다(아래 표).
- 스크립트나 `ssh 호스트 명령` 처럼 비대화형으로 실행한 명령. bash 의 기록 기능은 대화형 셸에서만 기본으로 켜집니다[1].
- 아직 살아 있는 셸에서 입력한 명령. bash 는 셸이 끝날 때 목록을 파일에 씁니다[1]. 이 부분은 메모리에서 찾습니다(아래 "시각과 메모리").

## 한눈에 보기

| 셸 | 기본 기록 파일 | 명령별 시각 | 알려 주는 것 |
|---|---|---|---|
| bash | `~/.bash_history` (`HISTFILE` 기본값)[1] | `HISTTIMEFORMAT` 이 설정돼 있을 때만 `#` 뒤에 epoch 초가 붙은 줄을 명령 앞에 씀[1][2] | 대화형 셸에서 입력한 명령 줄 |
| zsh | 기본 파일 없음. `HISTFILE` 을 설정해야 저장[3]. 수집 도구가 기본으로 찾는 이름은 `~/.zsh_history`, `~/.zhistory`[9][10], 초기 설정 도우미가 제안하는 이름은 `~/.histfile`[4] | `EXTENDED_HISTORY` 를 켜면 `: 시작시각:걸린초;명령` 모양으로 저장[3] | 명령 줄. 켜면 시작 시각과 걸린 시간 |
| fish | `~/.local/share/fish/fish_history` (`XDG_DATA_HOME` 이 있으면 `$XDG_DATA_HOME/fish/fish_history`)[5] | 항목마다 `when:` 줄에 epoch 초[6] | 명령 줄과 입력 시각 |
| sh·ksh | `~/.sh_history`[9][10] | 하위 쪽에서 다루지 않음 | 명령 줄 |
| tcsh | `~/.history`[10] | 하위 쪽에서 다루지 않음 | 명령 줄 |

root 계정의 기록은 `/root` 아래에 따로 있습니다[9]. `sudo -i` 로 연 root 셸이 어느 파일에 쓰는지는 [sudo·su 사용 기록](../../logins/sudo-su.md) 과 [bash 기록](bash.md) 에서 다룹니다.

### 기준 배포판의 bash 기본 설정

Ubuntu 24.04 LTS 와 RHEL 계열의 기본 설정 파일에는 `HISTTIMEFORMAT` 이 없어서, 기본 상태의 bash 기록에는 명령별 시각이 없습니다[7][8]. `#` 과 숫자로 된 줄이 보이면 사용자·관리자·도구 가운데 누군가 `HISTTIMEFORMAT` 을 설정했다는 뜻입니다.

| 항목 | Ubuntu 24.04 LTS | RHEL 계열 |
|---|---|---|
| 설정이 들어 있는 파일 | `/etc/skel/.bashrc`(새 사용자의 `~/.bashrc` 원본). 대화형 셸일 때만 적용[7] | `/etc/profile`, `/etc/bashrc`[8] |
| `HISTCONTROL` | `ignoreboth` — 공백으로 시작하는 줄과 바로 앞과 같은 줄을 저장하지 않음[1][7] | `ignoredups`. 미리 `ignorespace` 였으면 `ignoreboth`[8] |
| `HISTTIMEFORMAT` | 설정 없음[7] | 설정 없음[8] |

크기 한도(`HISTSIZE`·`HISTFILESIZE`)와 덧붙이기 설정은 [bash 기록](bash.md) 에 정리했습니다.

### 시각과 메모리

기록 파일 속 시각은 모두 Unix epoch 초라서 UTC 기준입니다. bash 의 `#` 줄 숫자는 명령을 기록 목록에 넣은 순간의 `time()` 값이고[2], 파일에 쓴 시각이 아닙니다. 기록 파일 자체의 수정 시각(mtime)은 마지막으로 저장한 때(보통 셸 종료)를 가리킬 뿐이라 명령별 시각으로 쓰면 안 됩니다. epoch 값 읽는 법은 [Linux 의 시각 값](../../../01-foundations/value-decoding/time-values.md) 을 봅니다.

bash 는 `HISTTIMEFORMAT` 과 상관없이 목록에 넣는 항목마다 `#숫자` 시각 문자열을 만들어 둡니다[2]. 그래서 켜져 있는 시스템의 메모리에서는 파일에 없는 명령과 시각이 나올 수 있고, Volatility 3 의 `linux.bash` 플러그인은 프로세스 이름이 `bash`·`sh`·`dash` 인 프로세스의 힙에서 이 항목을 찾습니다[13]. 사용법은 [메모리 분석](../../../03-techniques/analysis/memory-analysis.md) 에서 다룹니다.

### 수집 도구가 보는 범위

도구마다 찾는 파일 목록이 달라서, 한 도구 결과에 기록이 없다고 기록 파일이 없는 것은 아닙니다.

| 도구 | 보는 파일 | 빠지는 것 |
|---|---|---|
| ForensicArtifacts `ShellHistoryFile`, `RootUserShellHistory` | 홈의 `.bash_history`, `.sh_history`, `.zhistory`, `.zsh_history`, `.local/share/fish/fish_history`. `/root` 는 `RootUserShellHistory` 로 따로 정의[9] | 백업·회전 사본, `HISTFILE` 로 바꾼 경로 |
| UAC | 위 파일과 함께 `.bash_history~`, `.bash_history.*`, `.zsh_history.*`, `.zhistory.*` 같은 사본, fish 폴더 전체, `.history`. 설정 파일에서 `HISTFILE=` 줄을 찾아 바뀐 경로도 모음[10] | `HISTFILE=` 문자열로 찾지 못하는 방식으로 정한 경로 |
| dissect.target `commandhistory` | `.bash_history`, `.zsh_history`, `.zsh_sessions/*.history`, `.local/share/fish/fish_history`, `.ash_history`와 `.mysql_history`·`.psql_history`·`.python_history`·`.sqlite_history`·`.dbshell`[11] | `.zhistory`, `.sh_history` |
| Velociraptor `Linux.Sys.BashHistory` | 기본 glob `/{root,home/*}/.*_history`[12] | fish 기록, `.zhistory`, `/home` 밖의 홈 폴더 |

zsh 초기 설정 도우미가 제안하는 `~/.histfile`[4] 은 위 네 도구의 기본 목록 어디에도 없습니다. 검체에서는 셸 설정 파일의 `HISTFILE` 값을 먼저 확인하고, 그 경로를 따로 모읍니다. 설정 파일 위치는 [셸 시작 파일](../../persistence/shell-startup.md) 을 봅니다.

Windows 의 WSL 배포판도 셸 기록을 남깁니다. ForensicArtifacts 는 Windows 쪽 경로 `%%users.localappdata%%\Packages\*\LocalState\rootfs\home\*\.bash_history` 를 따로 정의합니다[9]. `wsl.exe` 로 실행한 Linux 명령은 `~/.bash_history`·`~/.sh_history` 에 저장되지 않는다는 주장이 Matadar 의 DFRWS 2020 발표에 있습니다[14]. 어떤 조건에서 그런지는 발표에 나오지 않으므로, 검체의 프로세스 명령 줄 기록과 함께 확인합니다.

## 읽는 순서

1. [bash 기록 (.bash_history)](bash.md) — 저장 시점과 덮어쓰기 방식, 배포판 기본값, `#` 시각 줄 해석, 도구마다 다른 시각 줄 판별
2. [zsh·fish 기록 (zsh·fish)](zsh-fish.md) — zsh 확장 형식과 메타 문자, fish 의 YAML 비슷한 형식과 같은 명령 합치기
3. [기록 지우기와 끄기 (History Evasion)](evasion.md) — 기록이 남지 않게 되는 설정·명령과 그 흔적이 남는 곳

## 함께 볼 페이지

- [감사 로그의 실행 기록 (auditd execve)](../auditd-execve.md) — 셸 기록과 달리 실행된 프로그램과 인수를 커널이 남김
- [프로세스 회계 (acct·pacct)](../process-accounting.md) — 끝난 프로세스의 명령 이름과 시각
- [실행 중인 프로세스 (/proc)](../proc.md) — 살아 있는 셸과 그 명령 줄
- [셸 시작 파일 (.bashrc·profile)](../../persistence/shell-startup.md) — `HISTFILE`·`HISTCONTROL` 을 바꾸는 줄이 들어가는 곳
- [편집기 흔적 (vim·nano·less)](../../file-activity/editor-artifacts.md) — `.lesshst` 처럼 다른 프로그램이 남기는 기록 파일
- [sudo·su 사용 기록](../../logins/sudo-su.md), [SSH](../../logins/ssh/index.md)
- [타임라인 만들기](../../../03-techniques/analysis/timeline.md)
- [흔적을 지웠나](../../../04-scenarios/insider/anti-forensics.md), [누가 그 명령을 실행했나](../../../04-scenarios/attribution/user-attribution.md)

## 참고 문헌

1. GNU Bash 5.2, doc/bash.1 (HISTORY, Shell Variables, `set -o history`). https://github.com/tianon/mirror-bash/blob/bash-5.2/doc/bash.1
2. GNU Bash 5.2, lib/readline/history.c (`hist_inittime`, `add_history`). https://github.com/tianon/mirror-bash/blob/bash-5.2/lib/readline/history.c
3. zsh, Doc/Zsh/params.yo (`HISTFILE`), Doc/Zsh/options.yo (`EXTENDED_HISTORY`). https://github.com/zsh-users/zsh/tree/master/Doc/Zsh
4. zsh, Functions/Newuser/zsh-newuser-install. https://github.com/zsh-users/zsh/blob/master/Functions/Newuser/zsh-newuser-install
5. fish-shell, doc_src/cmds/history.rst, doc_src/interactive.rst, doc_src/cmds/fish_should_add_to_history.rst. https://github.com/fish-shell/fish-shell/tree/master/doc_src
6. fish-shell 3.7.0, src/history_file.cpp (`append_history_item_to_buffer`). https://github.com/fish-shell/fish-shell/blob/3.7.0/src/history_file.cpp
7. Ubuntu bash 5.2.21-2ubuntu4 (noble) 소스 패키지 사본, debian/skel.bashrc. https://github.com/cpsource/bash-5.2.21/tree/main/debian
8. Red Hat 계열 setup 패키지 profile·bashrc (setup 2.8.71, 2.15.0). https://github.com/ydirson/rh-setup , https://github.com/microsoft/azurelinux/tree/main/specs/s/setup
9. ForensicArtifacts, artifacts/data/shell.yaml. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/shell.yaml
10. tclahr UAC, artifacts/files/shell/bash.yaml, zsh.yaml, fish.yaml, ksh.yaml, tcsh.yaml, common.yaml. https://github.com/tclahr/uac/tree/main/artifacts/files/shell
11. fox-it dissect.target, dissect/target/plugins/os/unix/history.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/history.py
12. Velocidex velociraptor, artifacts/definitions/Linux/Sys/BashHistory.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Sys/BashHistory.yaml
13. Volatility 3, volatility3/framework/plugins/linux/bash.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/bash.py
14. Asif Matadar, "Investigating Windows Subsystem for Linux (WSL) Endpoints", DFRWS 2020 USA 발표 슬라이드. https://dfrws.org/presentation/investigating-windows-subsystem-for-linux-wsl-endpoints/
15. Ali Hadi, Mariam Khader, Thomas Claflin, "Learning Linux Forensic Analysis and Why it Matters", DFRWS 발표 슬라이드. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
