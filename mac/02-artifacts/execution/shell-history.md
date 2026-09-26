---
title: "터미널 명령 기록"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 770
---

# 터미널 명령 기록 (zsh_history·bash_sessions)

macOS 10.15 Catalina 부터 새 계정의 기본 셸은 zsh 이고, 시스템 설정 파일 `/etc/zshrc` 가 명령 기록 파일을 홈 폴더의 `.zsh_history` 로 정해서, 사용자가 터미널에 친 명령이 평범한 텍스트로 남습니다. 다만 기본 설정에서는 명령마다 시각이 남지 않고, 어떤 셸 옵션이 켜져 있었는지에 따라 남는 명령과 형식이 달라집니다.

## 무엇을 기록하나 · 왜 생기나

셸은 사용자가 입력한 명령을 기록 (history) 으로 모아 두었다가 파일에 쓰고, 다음 세션에서 다시 불러 씁니다. macOS 10.15 부터 zsh 가 기본 로그인 셸이자 기본 대화형 셸이고, 새로 만든 사용자 계정은 모두 zsh 를 씁니다 [1]. macOS 10.14 이하에서는 bash 가 기본이었습니다 [1].

Apple 이 공개한 zsh 소스의 `zshrc`(곧 `/etc/zshrc`)는 기록에 관해 아래 값을 정합니다 [2].

```
HISTFILE=${ZDOTDIR:-$HOME}/.zsh_history
HISTSIZE=2000
SAVEHIST=1000
```

기록 파일은 기본으로 홈 폴더의 `.zsh_history` 이고, `ZDOTDIR` 을 설정하면 그 폴더의 `.zsh_history` 로 바뀝니다 [2]. 셸은 메모리에 2000줄, 파일에 1000줄까지 기록을 둡니다 [2]. 같은 파일은 `setopt` 으로 `COMBINING_CHARS` 와 `BEEP` 만 켜고 `EXTENDED_HISTORY` 는 켜지 않아서 [2], 기본 설정의 `.zsh_history` 에는 명령마다 시각이 없는 것으로 보입니다. 사용자의 `~/.zshrc` 나 터미널 앱용 설정에서 옵션을 켜면 시각이 남을 수 있습니다.

`/etc/zshrc` 는 마지막 줄에서 `/etc/zshrc_$TERM_PROGRAM` 이 있으면 읽고, macOS 의 터미널 앱에서는 이 이름이 `/etc/zshrc_Apple_Terminal` 이 됩니다 [2]. 이 파일은 Apple 공개 zsh 저장소에 없어서 [2], 세션별 기록을 따로 두는지 같은 내용은 실제 파일을 열어 확인합니다. 셸 내장 `log` 명령을 끄는 `disable log` 줄도 있어서 [2], 기록에 남은 `log` 는 `/usr/bin/log` 를 부른 명령으로 읽습니다.

## 위치와 버전별 차이

| macOS 버전 | 기본 셸 [1] | 기록 파일 |
|---|---|---|
| 10.14 Mojave 이하 | bash | 실제 기기에서 확인 |
| 10.15 Catalina 이후 | zsh (새로 만든 계정) | `${ZDOTDIR:-$HOME}/.zsh_history` [2] |

셸은 `chsh -s` 로 바꾸고, 쓸 수 있는 셸은 `/etc/shells` 에 적힌 `/bin/zsh`, `/bin/bash`, `/bin/csh`, `/bin/dash`, `/bin/ksh`, `/bin/sh`, `/bin/tcsh` 입니다 [1]. 업그레이드한 계정이나 셸을 바꾼 계정이 있을 수 있으므로, 계정마다 실제 로그인 셸을 먼저 확인하고, 그 셸의 기록 파일을 찾습니다. 계정의 셸 설정은 [사용자 계정 (Local Accounts)](../system-account/user-accounts/index.md)에서 다룹니다. zsh 가 기본인 맥에서 bash 를 띄우면 "기본 대화형 셸이 이제 zsh" 라는 안내가 나오고, `BASH_SILENCE_DEPRECATION_WARNING=1` 을 내보내면 이 안내가 꺼집니다 [1]. 사용자 설정 파일에서 이 변수를 찾으면 그 사용자가 bash 를 계속 썼다는 단서가 됩니다.

제목의 bash_sessions 는 터미널 앱이 bash 세션마다 기록을 따로 두는 폴더(`~/.bash_sessions/`)로 알려져 있습니다. 그 동작과 파일 이름, 이를 정하는 `/etc/bashrc_Apple_Terminal` 의 내용을 설명한 공개 자료는 없고, zsh 쪽의 세션별 기록 폴더도 마찬가지입니다. 실제 기기에서 이런 폴더가 보이면 파일을 열어 형식을 직접 확인합니다.

## 구조

기록 파일은 한 줄에 명령 하나를 적는 텍스트 파일로 읽습니다. `EXTENDED_HISTORY` 가 켜져 있으면 줄마다 명령의 시작 시각(유닉스 시각, 초)과 걸린 시간(초)이 앞에 붙습니다 [3].

```
: <시작 시각>:<걸린 초>;<명령>
```

어떤 명령이 파일에 남는지는 zsh 기록 옵션이 정합니다 [3].

| 옵션 | 켜면 [3] | 기록에 미치는 영향 |
|---|---|---|
| `EXTENDED_HISTORY` | 명령마다 시작 시각과 걸린 시간을 저장 | 줄 앞에 시각이 붙음 |
| `APPEND_HISTORY` | 파일을 덮어쓰지 않고 뒤에 붙임. zsh 기본값으로 켜져 있음 | 여러 세션의 기록이 한 파일에 쌓임 |
| `INC_APPEND_HISTORY` | 셸이 끝날 때까지 기다리지 않고 입력하는 즉시 파일에 붙임 | 세션이 비정상으로 끝나도 명령이 남음 |
| `INC_APPEND_HISTORY_TIME` | 명령이 끝난 뒤 기록을 씀 | 걸린 시간이 정확히 남음 |
| `SHARE_HISTORY` | 파일에서 새 명령을 읽어 오고 입력한 명령을 파일에 붙임. 시각도 남김 | 여러 창의 명령이 섞여 쌓임 |
| `HIST_IGNORE_SPACE` | 첫 글자가 공백인 명령 줄을 뺌 | 공백으로 시작한 명령이 없을 수 있음 |
| `HIST_IGNORE_DUPS` | 바로 앞 명령과 같으면 넣지 않음 | 연달아 친 같은 명령이 한 줄로 남음 |
| `HIST_NO_STORE` | `history`(`fc -l`) 명령 자체를 뺌 | 기록을 조회한 흔적이 없음 |
| `HIST_SAVE_NO_DUPS` | 파일에 쓸 때 새 명령과 겹치는 옛 명령을 뺌 | 같은 명령의 옛 줄과 옛 시각이 사라짐 |

`/etc/zshrc` 는 이 가운데 어느 것도 켜지 않고 zsh 가 기본으로 켜 두는 것은 `APPEND_HISTORY` 뿐이라서 [2][3], 분석할 때는 사용자의 `~/.zshrc`, `ZDOTDIR` 아래 설정 파일, `/etc/zshrc_Apple_Terminal` 의 `setopt` 줄을 먼저 모아 그 계정에 켜져 있던 옵션을 정리합니다. 설정 파일 자체는 [셸 시작 파일 (zshrc·bash_profile)](../persistence/shell-startup-files.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 기록 파일에 줄이 있으면 그 계정의 셸 기록에 이 명령 문자열이 들어갔다는 뜻입니다. `EXTENDED_HISTORY` 형식의 줄이면 그 명령이 이 시각에 시작해 이만큼 걸렸다는 기록이 함께 있습니다 [3]. 명령에는 대상 경로, 접속한 호스트, 인자가 그대로 적혀서, `ssh`·`log erase`·`rm` 같은 명령을 찾을 때 다른 기록보다 먼저 봅니다.

**증명하지 못하는 것.** 기록에 남은 명령이 성공했는지는 알 수 없습니다. 파일은 계정 기준이라서 그 계정으로 로그인한 다른 사람이 친 명령일 수 있고, 붙여 넣은 명령과 직접 친 명령도 구별되지 않습니다. 시각이 없는 형식이면 줄 순서만 알 수 있고, 그 순서도 여러 세션이 섞이면 실제 입력 순서와 다를 수 있습니다. 기록에 없다는 사실은 명령을 치지 않았다는 증거가 되지 못하는데, 옵션과 세션 종료 방식, 사용자의 삭제에 따라 빠질 수 있어서입니다.

보고서에는 "이 계정의 `.zsh_history` 에 이 명령 줄이 있고, 줄 앞의 값으로는 2023-11-14 22:13:20 UTC 에 시작한 기록이다" 처럼 파일·줄·시각 형식을 함께 씁니다.

## 시각 해석

`EXTENDED_HISTORY` 형식의 시작 시각은 유닉스 시각(1970-01-01 UTC 기준 초)이라서 [3] UTC 로 바꾼 뒤, 현지 시각은 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)을 보고 바꿉니다. 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에서 다룹니다. 걸린 시간 값은 `INC_APPEND_HISTORY_TIME` 이 켜져 있을 때 정확히 남습니다 [3].

시각이 없는 형식이면 파일의 수정 시각이 마지막으로 기록을 쓴 때를 대략 알려 줄 수 있습니다. 옵션을 켜지 않은 zsh 는 셸이 끝날 때 기록을 파일에 쓰므로 [3], 수정 시각은 마지막 세션이 끝난 무렵일 가능성이 있습니다.

## 함정과 한계

- **공백으로 시작한 명령.** `HIST_IGNORE_SPACE` 가 켜져 있으면 공백으로 시작한 명령은 파일에 없을 수 있습니다 [3].
- **줄 수 한도.** 기본 `SAVEHIST=1000` 이라서 [2] 파일에는 최근 1000줄 안팎만 남는다고 보고, 오래된 명령은 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md)로 지난 파일을 찾아 봅니다.
- **셸 종료 때 쓰기.** `INC_APPEND_HISTORY`·`SHARE_HISTORY` 가 꺼져 있으면 셸이 끝날 때 파일에 써서 [3], 창을 강제로 닫거나 셸이 비정상으로 끝난 세션의 명령은 파일에 없을 수 있습니다.
- **옛 줄이 사라짐.** `HIST_SAVE_NO_DUPS` 가 켜져 있으면 같은 명령의 옛 줄이 빠져서 [3], 처음 친 시각을 이 파일로 알 수 없습니다.
- **파일 위치 이동.** `ZDOTDIR` 을 설정하면 기록 파일이 홈 폴더가 아닌 곳에 생깁니다 [2]. 홈 폴더에 `.zsh_history` 가 없으면 설정 파일에서 `ZDOTDIR`·`HISTFILE` 을 먼저 찾습니다.
- **지우거나 고치기 쉬움.** 기록 파일은 사용자가 지우거나 고칠 수 있는 텍스트 파일입니다. 파일이 비어 있거나 없으면 그 자체를 조사 거리로 보고, 지운 흔적은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)의 순서로 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

명세로 만든 예시로, `EXTENDED_HISTORY` 형식의 줄 `: 1700000000:0;ls` 는 아래 바이트입니다.

```
3a 20 31 37 30 30 30 30 30 30 30 30 3a 30 3b 6c 73 0a
:     1  7  0  0  0  0  0  0  0  0  :  0  ;  l  s  \n
```

`3a 20`(콜론과 공백)으로 시작하면 `EXTENDED_HISTORY` 형식이고, 다음 `3a` 까지가 시작 시각, `3b`(세미콜론)까지가 걸린 초, 그 뒤부터 줄바꿈 `0a` 까지가 명령입니다 [3]. 이 예의 1700000000 은 2023-11-14 22:13:20 UTC 입니다. 줄이 `3a 20` 으로 시작하지 않으면 시각 없는 형식으로 봅니다.

### 공개 도구로 한 번

사본에서 `sed` 로 시각·걸린 초·명령을 나누고, 시각을 UTC 로 바꿉니다. 아래 `date -u -r` 은 macOS 의 `date` 기준이고, GNU `date` 에서는 `date -u -d @"$ts"` 로 바꿉니다.

```sh
LC_ALL=C sed -n 's/^: \([0-9]*\):\([0-9]*\);\(.*\)$/\1 \2 \3/p' zsh_history.copy |
while read -r ts dur cmd; do
  printf '%s UTC  %ss  %s\n' "$(date -u -r "$ts" '+%F %T')" "$dur" "$cmd"
done

grep -h 'setopt\|HISTFILE\|ZDOTDIR\|SAVEHIST' zshrc.copy zshrc_Apple_Terminal.copy
```

첫 명령은 시각이 붙은 줄만 뽑습니다. 결과 줄 수가 파일 전체 줄 수와 다르면 시각 없는 줄이 섞여 있을 수 있으니, 나머지 줄을 따로 열어 봅니다. 둘째 명령으로 옵션과 기록 파일 설정을 모아 위 표와 맞춰 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [통합 로그의 프로세스 실행 기록 (Process Events)](unified-log-process.md) | 기록에 있는 명령이 실제로 실행된 시각 |
| [감사 로그 (OpenBSM Audit)](../logs/openbsm-audit.md) | 같은 명령의 실행 기록과 사용자 |
| [KnowledgeC (knowledgeC.db)](knowledgec/index.md) | 터미널 앱이 앞에 있던 구간 |
| [셸 시작 파일 (zshrc·bash_profile)](../persistence/shell-startup-files.md) | 기록 옵션과 `HISTFILE` 설정, 시작 파일에 넣은 명령 |
| [SSH 키와 접속 목록 (SSH Keys·known_hosts)](../credentials/ssh-keys.md) | `ssh` 명령의 상대가 접속 목록에 있는지 |
| [원격 접속 (Remote Access)](../network/remote-access/index.md) | 원격으로 들어와 친 명령인지 |
| [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md) | `log erase` 같은 지우기 명령 |

## 실습

공개 시험 자료(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 계정마다 로그인 셸이 무엇인지 확인하고, 그 셸의 기록 파일을 찾아 보세요.
2. `.zsh_history` 의 전체 줄 수와 `: ` 로 시작하는 줄 수를 세어 `EXTENDED_HISTORY` 가 켜져 있었는지 판단해 보세요.
3. `/etc/zshrc`, `~/.zshrc`, `/etc/zshrc_Apple_Terminal` 에서 `setopt` 줄을 모아 켜져 있던 기록 옵션을 적어 보세요.
4. 기록에 있는 `ssh` 명령의 상대 호스트를 뽑아 `known_hosts` 와 맞춰 보세요.

## 참고 문헌

1. Apple Support, "Use zsh as the default shell on your Mac" (102360) — https://support.apple.com/en-us/102360
2. Apple 공개 소스 apple-oss-distributions/zsh — `zshrc`(= /etc/zshrc) 원문과 저장소 파일 목록 — https://raw.githubusercontent.com/apple-oss-distributions/zsh/main/zshrc , https://api.github.com/repos/apple-oss-distributions/zsh/git/trees/main?recursive=1
3. zsh 공식 문서, "16 Options" (History 옵션) — https://zsh.sourceforge.io/Doc/Release/Options.html
