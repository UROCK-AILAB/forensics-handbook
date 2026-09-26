---
title: "bash 기록"
parent: "셸 명령 기록"
grand_parent: "아티팩트 · 실행 흔적"
nav_order: 430
---

# bash 기록 (.bash_history)

bash 는 대화형 셸에서 친 명령을 메모리 속 기록 목록에 넣었다가 셸이 끝날 때 `~/.bash_history` 에 한 줄에 한 명령씩 평문으로 저장합니다.

## 무엇을 기록하나 · 왜 생기나

bash 의 명령 기록 (command history) 은 `set -o history` 가 켜져 있을 때 동작하고, 이 설정은 대화형 셸에서 기본으로 켜집니다[1]. 셸 파서가 읽은 줄은 기록 목록 (history list) 에 들어가는데, 이때 넣는 문자열은 매개변수·변수 확장 전이고 기록 확장 (history expansion) 뒤의 모습입니다[1]. 그래서 파일에는 `$HOME` 같은 변수가 풀리지 않은 채로 남습니다.

목록이 파일로 가는 때는 셸이 끝날 때입니다. 기록이 켜진 셸이 끝나면 목록의 마지막 `$HISTSIZE` 줄을 `$HISTFILE` 에 옮기는데, `histappend` 셸 옵션이 켜져 있으면 파일 끝에 덧붙이고 꺼져 있으면 파일을 덮어씁니다[1]. 대화형 셸이 SIGHUP 이나 SIGTERM 을 받아 끝날 때도 기록을 저장하는 코드가 돌기 때문에[4], 터미널 창을 닫아도 보통은 저장됩니다. 셸 안에서 `history -a` 를 치면 현재 세션에서 새로 친 줄 가운데 아직 파일에 없는 줄을 그 자리에서 덧붙이고, `history -w` 를 치면 현재 목록으로 파일을 덮어씁니다[1].

저장 여부를 가르는 변수는 아래와 같습니다[1].

| 변수 | 하는 일 |
|---|---|
| `HISTFILE` | 기록 파일 이름. 기본값 `~/.bash_history`. 풀려(unset) 있으면 끝날 때 저장하지 않음 |
| `HISTSIZE` | 목록에 기억할 명령 수. 시작 파일을 읽은 뒤 기본 500. 0 이면 목록에 넣지 않고, 음수면 제한 없음 |
| `HISTFILESIZE` | 파일의 최대 줄 수. 값을 넣을 때와 셸이 끝나 저장한 뒤 오래된 줄부터 잘라 냄. 0 이면 파일을 0 바이트로 만듦. 숫자가 아니거나 음수면 자르지 않음. 기본값은 `HISTSIZE` 값 |
| `HISTCONTROL` | `ignorespace`(공백으로 시작하는 줄 빼기), `ignoredups`(바로 앞과 같은 줄 빼기), `ignoreboth`(둘 다), `erasedups`(같은 줄을 목록에서 모두 지우고 새로 넣기) |
| `HISTIGNORE` | 콜론으로 나눈 패턴. 줄 전체가 맞으면 빼고, `&` 는 바로 앞 기록 줄 |
| `HISTTIMEFORMAT` | 설정돼 있으면 명령마다 시각을 파일에 함께 씀 |

`HISTCONTROL` 과 `HISTIGNORE` 는 여러 줄짜리 복합 명령의 둘째 줄부터는 검사하지 않고 그대로 넣습니다[1]. 기록을 끄거나 줄이는 설정이 어떤 흔적을 남기는지는 [기록 지우기와 끄기](evasion.md) 에서 다룹니다.

## 위치와 버전별 차이

파일은 사용자 홈마다 하나씩 있습니다. root 는 `/root/.bash_history` 이고, 일반 사용자는 `/home/사용자이름/.bash_history` 입니다. 설정에서 `HISTFILE` 을 바꾸면 다른 곳에 쌓이므로 수집할 때는 `~/.bashrc`, `~/.bash_profile`, `~/.profile`, `/etc/bash.bashrc` 에서 `HISTFILE=` 줄을 함께 찾습니다[12].

`sudo -i` 나 `sudo -s` 로 연 root 셸의 기록은 root 홈에 쌓일 가능성이 높습니다. sudoers 의 `env_reset` 이 기본으로 켜져 있으면 sudo 는 `HOME` 을 대상 사용자 기준으로 다시 정하고[8], bash 는 그 `HOME` 아래 `~/.bash_history` 를 쓰기 때문입니다[1]. sudo 자체가 남기는 기록은 [sudo·su 사용 기록](../../logins/sudo-su.md) 에서 다룹니다.

두 기준 배포판의 기본 설정은 아래와 같습니다. Ubuntu 는 새 사용자를 만들 때 `/etc/skel/.bashrc` 를 홈에 복사하고[6], RHEL 은 `/etc/profile` 과 `/etc/bashrc` 에서 정합니다[7].

| 항목 | Ubuntu 24.04 (`~/.bashrc`) | RHEL 9 (`/etc/profile`, `/etc/bashrc`) |
|---|---|---|
| `HISTCONTROL` | `ignoreboth` | `ignoredups` (미리 `ignorespace` 였으면 `ignoreboth`) |
| `HISTSIZE` | 1000 | 1000 |
| `HISTFILESIZE` | 2000 | 설정 없음 → `HISTSIZE` 값 |
| `histappend` | 켬 | 켬 |
| `history -a` 줄 | 없음 | `/etc/bashrc` 대화형 부분에 있음 |
| `HISTTIMEFORMAT` | 설정 없음 | 설정 없음 |

Ubuntu 의 `~/.bashrc` 는 비대화형 셸이면 곧바로 끝나므로 위 값은 대화형 셸에만 적용됩니다[6]. `/root/.bashrc` 의 내용은 분석 대상에서 직접 확인합니다.

두 배포판 모두 `HISTTIMEFORMAT` 을 기본으로 설정하지 않습니다[6][7]. 그래서 기본 상태의 `.bash_history` 에는 명령별 시각이 없고, `#` 뒤에 숫자가 붙은 줄이 보이면 사용자나 관리자, 설정 관리 도구가 이 변수를 설정했을 가능성이 높습니다.

## 구조

파일은 줄바꿈이 LF 인 평문이고, 한 줄에 명령 하나가 들어갑니다. 여러 줄 명령은 `cmdhist` 옵션이 켜져 있으면 세미콜론을 넣어 한 항목으로 합치고, `lithist` 까지 켜져 있으면 세미콜론 대신 줄바꿈을 그대로 둡니다[1].

`HISTTIMEFORMAT` 이 설정돼 있으면 명령 줄 바로 앞에 시각 줄이 붙습니다. 시각 줄은 기록 주석 문자 (history comment character, 기본 `#`) 뒤에 Unix 초를 10진수로 쓴 모양입니다[1][2]. bash 는 파일을 읽을 때 주석 문자 바로 뒤에 숫자가 오는 줄을 다음 명령의 시각으로 봅니다[1][3].

아래는 시각 줄이 있는 파일의 만든 예시입니다.

```
#1712345678
ls -la /tmp
#1712345702
cat /etc/passwd
```

bash 는 명령을 목록에 넣을 때마다 시각 문자열을 함께 만듭니다[2]. 파일에 시각 줄을 쓸지는 저장할 때 정하고, `HISTTIMEFORMAT` 이 없으면 메모리에 있는 시각은 쓰지 않고 명령 줄만 씁니다[1][3].

파일을 덮어쓰는 방식도 알아 둘 만합니다. `histappend` 가 꺼진 채 끝나거나 `history -w` 를 쓸 때, 그리고 `HISTFILESIZE` 로 잘라 낼 때 bash 는 같은 폴더에 `원래이름-PID.tmp` 임시 파일을 만들어 쓴 뒤 원래 이름으로 rename 합니다[3]. PID 자리는 PID 의 아래 다섯 자리를 0 으로 채워 씁니다[3]. 원래 파일이 심볼릭 링크면 링크 대상 쪽 폴더에 임시 파일을 만들고, 일반 파일이 아니면 임시 파일 없이 그대로 엽니다[3]. 새로 만든 파일은 원래 파일의 소유자·그룹으로 되돌립니다[3]. 덧붙일 때는 원래 파일을 `O_APPEND` 로 열어 끝에 씁니다[3].

## 증거로서 의미

### 증명하는 것

이 계정의 bash 세션이 이 문자열을 기록 목록에 넣었고, 그 목록을 파일에 저장했다는 것까지 보여 줍니다. 시각 줄이 있으면 그 명령을 목록에 넣은 시각, 곧 사용자가 줄을 입력한 시각을 초 단위로 알 수 있습니다[2]. 기록 파일이 있는 홈이 누구 것인지로 어느 계정의 셸이었는지 좁힐 수 있습니다.

### 증명하지 못하는 것

명령이 성공했는지, 무엇을 출력했는지는 남지 않습니다. 기록은 계정 단위라서 같은 계정을 여러 사람이 썼다면 누가 쳤는지 가릴 수 없습니다. 시각 줄이 없는 기본 상태에서는 명령별 시각을 알 수 없고, 파일의 줄 순서만 남습니다.

비대화형 셸의 명령은 기본으로 기록되지 않으므로[1] 스크립트 안의 명령이나 `ssh 호스트 명령` 처럼 원격에서 바로 실행한 명령은 이 파일에 없을 가능성이 높습니다. `ignorespace` 나 `ignoreboth` 설정 아래에서 공백으로 시작한 줄은 목록에 들어가지 않아 흔적이 없습니다[1]. 파일에 없다는 사실만으로 그 명령을 실행하지 않았다고 말할 수 없습니다.

## 시각 해석

시각 줄의 숫자는 1970-01-01 00:00:00 UTC 부터 센 초이고[2], 시간대 정보는 없습니다. 위 만든 예시의 `1712345678` 은 2024-04-05 19:34:38 UTC 입니다. `history` 내장 명령은 `HISTTIMEFORMAT` 값을 strftime(3) 형식 문자열로 써서 시각을 보여 줄 뿐이라[1] 표시된 값은 그 기계의 시간대 설정을 따를 가능성이 있으므로, `history` 로 읽은 값을 그대로 옮기지 말고 숫자를 UTC 로 바꿔 적습니다. Unix 시각을 읽는 일반 방법은 [Linux 의 시각 값](../../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

이 시각은 명령을 목록에 넣는 순간 `time()` 으로 만든 값이고[2], 파일에 쓴 시각이 아닙니다. 명령이 끝난 시각도 아닙니다.

파일 자체의 시각으로는 다른 것을 알 수 있습니다. mtime 은 마지막으로 파일에 쓴 때, 곧 보통은 마지막 셸이 끝난 때나 `history -a`·`-w` 를 친 때입니다. 덮어쓰기나 잘라 내기는 새 파일을 만들어 rename 하므로[3] ext4 의 생성 시각 (crtime) 도 그때로 바뀔 가능성이 높습니다. 기본 설정인 `histappend` 아래에서도 `HISTFILESIZE` 를 넘으면 잘라 내기가 일어나므로 crtime 을 계정을 만든 때로 읽으면 안 됩니다.

## 함정과 한계

- 셸이 아직 실행 중인 동안 친 명령은 파일에 없습니다. 라이브 시스템이면 메모리에서 찾고, 디스크 이미지만 있으면 마지막 세션의 명령이 빠져 있을 수 있습니다. SIGKILL 은 잡을 수 없는 신호라서[5] 셸이 SIGKILL 로 끝나면 저장 코드가 돌지 않습니다[4].
- 여러 셸을 동시에 열었다면 셸이 끝나는 순서대로 파일에 덧붙으므로, 파일의 줄 순서가 명령을 친 순서와 다를 수 있습니다. `histappend` 가 꺼져 있으면 마지막에 끝난 셸이 파일을 덮어써 먼저 끝난 셸의 줄이 사라질 수 있습니다[1].
- 덮어쓰기와 잘라 내기는 rename 방식이라 옛 내용이 지운 블록으로 남을 가능성이 있습니다[3]. 되살리는 방법은 [지운 파일 되살리기](../../../03-techniques/analysis/file-recovery.md) 에서 다룹니다.
- 도구마다 시각 줄을 알아보는 조건이 다릅니다. bash 는 주석 문자 뒤에 숫자가 하나라도 오면 시각 줄로 보지만[3], plaso 는 첫 자리가 0 이 아닌 9~10 자리 숫자만[9], dissect 는 정확히 10 자리 숫자만[10] 시각 줄로 봅니다. 2001-09-09 이전 시각처럼 9 자리인 값은 dissect 가 명령으로 읽습니다.
- plaso 는 이 시각을 `written_time` 이라는 이름으로 내놓지만[9] 실제 뜻은 명령을 목록에 넣은 시각입니다[2]. 이름만 보고 파일에 쓴 시각으로 해석하지 않습니다.
- 수집 도구가 설정 파일에서 `HISTFILE=` 줄을 찾아 바뀐 경로를 따라가더라도[12], 조건문 안에서 정하거나 셸 안에서 나중에 바꾼 경로는 놓칠 가능성이 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

위 만든 예시를 헥스로 보면 아래와 같습니다(명세로 만든 예시).

```
00000000: 2331 3731 3233 3435 3637 380a 6c73 202d  #1712345678.ls -
00000010: 6c61 202f 746d 700a 2331 3731 3233 3435  la /tmp.#1712345
00000020: 3730 320a 6361 7420 2f65 7463 2f70 6173  702.cat /etc/pas
00000030: 7377 640a                                swd.
```

`23` 이 `#` 이고 그 뒤 `31 37 31 32 33 34 35 36 37 38` 이 ASCII 숫자 `1712345678` 이며, `0a` 가 줄바꿈입니다. 시각 줄과 명령 줄 사이에 따로 구분 바이트는 없고, 줄이 `23` 다음 숫자 바이트(`30`~`39`)로 시작하는지로만 가릅니다[3]. 시각 줄이 없는 기본 파일은 명령 줄과 `0a` 만 이어집니다.

### 공개 도구로 한 번

- dissect.target 의 `commandhistory` 플러그인(별칭 `bashhistory`)은 사용자 홈마다 `.bash_history` 를 찾아 명령마다 시각(`ts`)과 파일 안 순서(`order`)를 내놓고, 시각 줄이 없으면 `ts` 를 비웁니다[10].
- plaso 의 `bash_history` 파서는 시각 줄을 기준으로 항목을 나누고, 시각 줄 사이의 여러 줄은 공백으로 이어 한 명령으로 만듭니다[9]. 파일 앞머리가 시각 줄과 명령 줄로 시작하거나 명령 줄·시각 줄·명령 줄로 시작해야 이 파서가 붙으므로[9], 시각 줄이 없는 기본 파일은 plaso 타임라인에 들어가지 않습니다.
- Velociraptor 의 `Linux.Sys.BashHistory` 는 기본으로 `/{root,home/*}/.*_history` 를 찾아 줄 단위로 정규식 검색을 합니다[11].
- 메모리에서는 Volatility 3 의 `linux.bash` 가 프로세스 이름이 `bash`, `sh`, `dash` 인 태스크의 힙에서 `#` 바이트를 찾고, 그 주소를 가리키는 포인터로 기록 항목 구조를 짜 맞춰 명령과 시각을 복원합니다[13]. 시각 문자열이 `#` 로 시작하고 10 자 이상인 항목만 인정하며, 결과를 시각 순으로 정렬해 PID, Process, CommandTime, Command 열로 보여 줍니다[13]. bash 는 `HISTTIMEFORMAT` 과 상관없이 모든 항목에 시각 문자열을 만들어 두므로[2] 메모리에서는 파일에 없던 시각도 나옵니다. 힙에서 `#` 뒤에 Unix 시각이 문자열로 붙은 값(예: `#1471572423`)을 찾는 방식은 Rekall 의 bash 플러그인도 같습니다[14]. 플러그인 쓰는 법은 [메모리 분석](../../../03-techniques/analysis/memory-analysis.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 것 | 맞춰 보는 것 |
|---|---|
| [감사 로그의 실행 기록](../auditd-execve.md) | 외부 프로그램을 실행한 시각·인수. 셸 내장 명령은 남지 않음 |
| [프로세스 회계](../process-accounting.md) | 켜져 있으면 명령 이름과 끝난 시각 |
| [실행 중인 프로세스](../proc.md) | 라이브에서 실행 중인 bash 프로세스와 그 사용자 |
| [로그인 기록](../../logins/wtmp-btmp-lastlog.md) | 기록을 남긴 계정이 그 시간대에 로그인해 있었는지 |
| [sudo·su 사용 기록](../../logins/sudo-su.md) | root 기록 파일의 명령을 누가 sudo 로 올라가 쳤는지 |
| [zsh·fish 기록](zsh-fish.md) | 같은 계정이 다른 셸로 친 명령 |

시각 줄이 없는 파일은 위 기록의 시각에 명령 순서를 맞춰 대략의 시간대를 잡습니다. 여러 기록을 시간순으로 합치는 방법은 [타임라인 만들기](../../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 실습

공개 시험 데이터(NIST CFReDS 의 Linux 디스크 이미지 등)로 아래 질문을 풀어 봅니다.

1. 모든 사용자 홈과 `/root` 에서 `.bash_history` 를 찾고, 설정 파일에서 `HISTFILE`·`HISTTIMEFORMAT`·`HISTCONTROL` 을 바꾼 줄이 있는지 확인합니다.
2. 시각 줄이 있으면 첫 명령과 마지막 명령의 시각을 UTC 로 적고, 파일 mtime 과 얼마나 차이 나는지 봅니다.
3. root 기록 파일의 명령 가운데 sudo 로그와 시각·명령이 맞는 것을 찾습니다.
4. 같은 명령을 dissect 와 plaso 로 각각 읽어 항목 수와 시각이 같은지 비교합니다.

## 참고 문헌

1. GNU Bash 5.2, doc/bash.1 (HISTORY, Shell Variables, `history` 내장 명령). https://github.com/tianon/mirror-bash/blob/bash-5.2/doc/bash.1
2. GNU Bash 5.2, lib/readline/history.c (`hist_inittime`, `add_history`). https://github.com/tianon/mirror-bash/blob/bash-5.2/lib/readline/history.c
3. GNU Bash 5.2, lib/readline/histfile.c (`HIST_TIMESTAMP_START`, `history_tempfile`, `history_do_write`, `history_truncate_file`). https://github.com/tianon/mirror-bash/blob/bash-5.2/lib/readline/histfile.c
4. GNU Bash 5.2, sig.c (SIGHUP·SIGTERM 때 기록 저장). https://github.com/tianon/mirror-bash/blob/bash-5.2/sig.c
5. Linux man-pages, signal(7). https://github.com/mkerrisk/man-pages/blob/master/man7/signal.7
6. Ubuntu 24.04 bash 5.2.21-2ubuntu4 소스 패키지, debian/skel.bashrc·etc.bash.bashrc. https://github.com/cpsource/bash-5.2.21/tree/main/debian
7. setup 2.13.7 (CentOS Stream 9 setup.spec 의 원본), profile·bashrc. https://releases.pagure.org/setup/setup-2.13.7.tar.bz2 , https://gitlab.com/redhat/centos-stream/rpms/setup/-/blob/c9s/setup.spec
8. sudo, docs/sudoers.man.in (`env_reset`). https://github.com/sudo-project/sudo/blob/main/docs/sudoers.man.in
9. plaso, plaso/parsers/text_plugins/bash_history.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/bash_history.py
10. dissect.target, dissect/target/plugins/os/unix/history.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/history.py
11. Velociraptor, artifacts/definitions/Linux/Sys/BashHistory.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Sys/BashHistory.yaml
12. UAC, artifacts/files/shell/bash.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/shell/bash.yaml
13. Volatility 3, volatility3/framework/plugins/linux/bash.py, symbols/linux/extensions/bash.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/bash.py , https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/symbols/linux/extensions/bash.py
14. Frank Block, Andreas Dewald, "Linux memory forensics: Dissecting the user space process heap", Digital Investigation 22 (2017) S66–S75. https://doi.org/10.1016/j.diin.2017.06.002
