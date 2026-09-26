---
title: "zsh·fish 기록"
parent: "셸 명령 기록"
grand_parent: "아티팩트 · 실행 흔적"
nav_order: 440
---

# zsh·fish 기록 (zsh·fish)

zsh 와 fish 는 bash 와 다른 파일 이름과 형식으로 명령 기록을 남깁니다. zsh 는 설정해야 파일이 생기고 시각은 선택 사항이며, fish 는 기본으로 파일을 만들고 항목마다 시각을 적습니다.

## 무엇을 기록하나 · 왜 생기나

두 셸 모두 대화형으로 입력한 명령 줄을 사용자 홈 아래 평문 파일에 저장합니다. 명령을 다시 불러 쓰려고 만든 기능이라서 운영체제 로그처럼 늘 남지는 않고, 사용자 설정에 따라 저장 여부와 시점이 바뀝니다. 셸 기록이 증명하는 것과 증명하지 못하는 것의 공통 원리는 [셸 명령 기록](index.md) 에 있고, 이 페이지는 zsh 와 fish 에서만 다른 점을 다룹니다.

**zsh** 는 `HISTFILE` 변수에 적힌 파일에 기록을 저장하고, 이 변수가 없으면 기록을 저장하지 않습니다[1]. 기본 파일 이름이 따로 없어서, 배포판이나 사용자 설정 파일이 `HISTFILE` 을 정해 주지 않으면 기록 파일이 아예 없습니다. 파일에 남기는 최대 항목 수는 `SAVEHIST`, 메모리 속 목록의 최대 항목 수는 `HISTSIZE` 가 정합니다[1]. 저장 시점은 옵션에 따라 넷으로 나뉩니다[2].

| 옵션 | 파일에 쓰는 때 |
|---|---|
| `APPEND_HISTORY` (모든 흉내 모드 (emulation) 에서 기본으로 켜짐) | 셸이 끝날 때 목록을 파일 끝에 덧붙임. 줄 수가 `SAVEHIST` 보다 20% 넘게 늘면 파일을 다시 써서 줄임 |
| `INC_APPEND_HISTORY` | 명령을 입력하자마자 덧붙임 |
| `INC_APPEND_HISTORY_TIME` | 명령이 끝난 뒤 덧붙여 걸린 시간을 바르게 적음 |
| `SHARE_HISTORY` | 입력하자마자 덧붙이고, 다른 세션이 쓴 줄을 읽어 들임. 시각을 `EXTENDED_HISTORY` 모양으로 붙여 씀 |

**fish** 는 설정하지 않아도 기록 파일을 만들고, 명령을 **실행하기 전에** 기록에 넣습니다[9]. 끝나지 않는 명령과 오래 도는 명령도 새 세션에서 바로 보이게 하려는 동작이라서, 기록에 있는 명령이 실제로 실행을 마쳤는지는 알 수 없습니다. fish 는 `history append` 로 실행하지 않은 명령을 기록에 넣을 수도 있습니다[7].

## 위치와 버전별 차이

계정이 어느 셸을 로그인 셸로 쓰는지는 `/etc/passwd` 의 마지막 필드([계정 파일](../../../01-foundations/users-auth/passwd-shadow-group.md))에서 확인하고, 로그인 셸이 bash 인 계정도 zsh·fish 를 따로 띄워 썼을 수 있으므로 기록 파일은 셸마다 모두 찾습니다.

| 셸 | 기록 파일 | 이름을 정하는 것 |
|---|---|---|
| zsh | 기본값 없음. 흔한 이름 `~/.zsh_history`, `~/.zhistory`[13][14]. 설정 파일이 없을 때 뜨는 초기 설정 도우미(zsh-newuser-install)는 `$ZDOTDIR` 또는 홈 아래 `.histfile` 을 제안[3] | 설정 파일의 `HISTFILE=` 줄 |
| fish | `~/.local/share/fish/fish_history`. `XDG_DATA_HOME` 이 있으면 `$XDG_DATA_HOME/fish/fish_history`[6][7] | `fish_history` 변수(세션 이름) |

zsh 초기 설정 도우미는 `HISTSIZE 1000`, `SAVEHIST 1000` 도 함께 제안합니다[3]. 기록 파일을 다시 쓸 때는 `HIST_SAVE_BY_COPY`(기본으로 켜짐) 때문에 `$HISTFILE.new` 를 만든 뒤 원래 파일 이름으로 바꿔 덮고[2][4], 쓰는 동안에는 기록 파일 이름 뒤에 `.LOCK` 을 붙인 잠금을 만듭니다. 심볼릭 링크를 쓸 수 있는 시스템에서는 `/pid-PID/host-호스트이름` 을 가리키는 심볼릭 링크로 만들고, 그렇지 않은 시스템에서는 `PID 호스트이름` 한 줄을 적은 파일로 만듭니다[4]. `HIST_FCNTL_LOCK` 을 켜면 `.LOCK` 없이 fcntl 잠금을 씁니다[2][4]. 비정상 종료 뒤에 `.new` 와 `.LOCK` 이 남아 있을 가능성이 있습니다.

fish 의 `fish_history` 변수는 파일 경로가 아니라 세션 이름입니다. 값이 없으면 `fish` 를 쓰고, `fun` 처럼 다른 값을 주면 `$XDG_DATA_HOME/fish/fun_history` 에 따로 기록합니다[7][8]. 그래서 `~/.local/share/fish/` 폴더에 `fish_history` 말고 다른 `*_history` 파일이 있는지 폴더째 봐야 합니다. 수집 도구마다 이 폴더와 zsh 기록 이름을 어디까지 모으는지는 [셸 명령 기록](index.md) 의 "수집 도구가 보는 범위" 표에 정리했고, 설정 파일 위치는 [셸 시작 파일](../../persistence/shell-startup.md) 에 있습니다.

fish 기록 형식은 판에 따라 다릅니다.

| 판 | 항목 모양 | `when` 의 뜻 |
|---|---|---|
| fish 3.7.0 (C++) | `- cmd:`, `when:`, 있으면 `paths:` 목록[10] | 같은 명령을 합칠 때 더 최근 시각으로 바뀜[10] |
| 최신 판 (Rust) | 위에 더해, 처음 넣은 시각이 마지막 시각과 다를 때만 `added_when:` 줄[12] | 마지막으로 넣은 시각. 처음 넣은 시각은 `added_when`[12] |

## 구조

### zsh

`EXTENDED_HISTORY` 가 꺼져 있으면 한 줄에 명령 하나만 적습니다. 켜져 있으면 각 줄 앞에 명령의 시작 시각(epoch 초)과 걸린 시간(초)을 붙여 `: 시작시각:걸린초;명령` 모양으로 씁니다[2]. 이 옵션은 csh 흉내 모드에서만 기본으로 켜지므로[2] 보통 zsh 에서는 설정 파일에서 켜야 합니다. 다만 `SHARE_HISTORY` 를 켜도 같은 모양으로 시각이 붙습니다[2].

```
: 1767225600:3;tar czf /tmp/a.tgz docs
: 1767225611:0;scp /tmp/a.tgz alice@198.51.100.7:
```

(만든 예시. `1767225600` 은 2026-01-01 00:00:00 UTC)

쓰는 코드는 다음 규칙을 따릅니다[4].

- 확장 형식이 아닐 때 명령이 `:` 로 시작하면 앞에 `\` 를 붙여 시각 줄과 헷갈리지 않게 합니다.
- 명령 안의 줄바꿈 앞에는 `\` 를 넣습니다. 그래서 여러 줄 명령은 `\` 로 끝나는 줄 여러 개로 보입니다.
- 명령이 역슬래시로 끝나면 공백 하나를 덧붙입니다.
- 끝난 시각이 없으면 걸린 시간을 `0` 으로 씁니다.

zsh 는 내부 문자열에서 NUL 과 0x83(Meta)~0xA2(Marker) 범위 바이트를 특별하게 다루려고, 그 바이트 대신 `0x83` 과 (원래 바이트 XOR 0x20) 두 바이트를 둡니다. 이것을 메타 처리 (metafy) 라고 합니다[5]. 기록 파일은 이 메타 처리된 모양 그대로 저장합니다[4]. UTF-8 한글은 이어짐 바이트가 0x80~0xBF 범위에 들어가므로, 파일 속 한글이나 다른 비ASCII 문자가 일반 텍스트 도구에서 깨져 보일 수 있습니다.

### fish

fish 기록은 YAML 과 비슷하지만 정식 YAML 은 아닌 형식입니다[12][15]. 항목 하나는 `- cmd:` 줄로 시작하고, 들여 쓴 `when:` 줄에 epoch 초를 적습니다[10].

```
- cmd: cd /srv/www
  when: 1767225600
- cmd: tar czf /tmp/site.tgz /srv/www
  when: 1767225642
  paths:
    - /srv/www
```

(만든 예시)

명령 안의 줄바꿈은 `\n` 두 글자로, 역슬래시는 `\\` 로 바꿔 한 줄에 씁니다[10]. `paths:` 목록에는 명령 인수 가운데 경로처럼 보이는 것을 넣는데, 입력 직후 따로 확인한 경로만 남깁니다[10]. 그래서 `paths:` 에 적힌 경로는 명령을 입력한 무렵 그 셸에서 찾아진 경로일 가능성이 있습니다. `exit`·`echo` 처럼 곧 끝나거나 경로를 받지 않는 명령은 이 확인을 건너뜁니다[10].

같은 명령을 여러 번 입력해도 항목은 하나로 합칩니다. 3.7.0 은 다시 쓸 때 같은 명령이 이미 있으면 시각만 더 최근 값으로 바꾸고, 합칠 때는 더 긴 `paths:` 목록을 택합니다[10]. 다시 쓸 때 남기는 항목은 최대 1024×256 개입니다[10].

## 증거로서 의미

### 증명하는 것

- 그 계정의 zsh·fish 기록에 해당 명령 줄이 들어갔다는 것.
- zsh 확장 형식이면 그 명령의 시작 시각과 걸린 초. 두 값을 더하면 끝난 시각을 잡을 수 있습니다.
- fish 는 그 명령을 마지막으로 입력한 시각. 최신 판에서 `added_when` 이 있으면 처음 입력한 시각도 알 수 있습니다[12].
- fish `paths:` 가 있으면, 입력 무렵 그 경로를 셸이 찾을 수 있었을 가능성.

### 증명하지 못하는 것

- 명령이 성공했는지, 끝까지 실행됐는지. fish 는 실행 전에 기록에 넣습니다[9].
- fish 에서 같은 명령을 몇 번 쳤는지. 합쳐진 항목에는 횟수가 없습니다[10].
- 확장 형식이 아닌 zsh 기록의 명령 시각.
- 공백으로 시작한 명령(zsh `HIST_IGNORE_SPACE`, fish 기본 동작)과 설정으로 뺀 명령. 이런 명령이 없었다는 뜻이 아닙니다.
- 계정 뒤에 있던 사람. 누가 그 계정으로 쳤는지는 로그인 기록과 맞춰 봐야 합니다.

## 시각 해석

두 셸 모두 epoch 초를 적으므로 시각 값 자체는 UTC 기준이고 시간대 정보가 없습니다. 사람이 읽는 시각으로 바꿀 때는 [시각 값](../../../01-foundations/value-decoding/time-values.md) 을 봅니다.

zsh 확장 시각은 명령을 시작한 시각입니다[2]. plaso 는 이 값을 `last_written_time`(마지막으로 기록한 시각)이라는 이름으로 내놓지만[16], zsh 문서와 쓰는 코드는 시작 시각(`stim`)이라고 정합니다[2][4]. 보고서에는 "시작 시각" 으로 씁니다. `INC_APPEND_HISTORY` 나 `SHARE_HISTORY` 처럼 입력하자마자 쓰는 설정에서는 명령이 끝나기 전에 줄을 쓰므로 걸린 시간이 `0` 으로 남을 가능성이 있습니다. 걸린 시간을 바르게 적으려면 `INC_APPEND_HISTORY_TIME` 이 켜져 있어야 합니다[2].

fish `when` 은 기록에 넣은 시각이라 실행 시작보다 조금 앞섭니다. 3.7.0 은 같은 명령을 합칠 때 더 최근 시각으로 바꾸고[10], 최신 판은 `when` 을 "마지막으로 넣은 시각" 으로 정해 둡니다[12]. 어느 판이든 오래된 명령의 첫 사용 시각이 `when` 에 남지 않을 수 있습니다.

## 함정과 한계

- **zsh 기록 파일이 없는 것은 정상일 수 있습니다.** `HISTFILE` 을 정하지 않으면 처음부터 저장하지 않습니다[1]. 파일이 없다는 사실만으로 지웠다고 보지 않고, 설정 파일에 `HISTFILE` 줄이 있었는지부터 봅니다.
- **zsh 파일의 줄 수와 명령 수가 다를 수 있습니다.** 여러 줄 명령은 `\` 로 이어진 여러 줄이고, `SAVEHIST` 를 넘으면 오래된 줄이 잘려 나갑니다[2].
- **메타 처리된 바이트.** 텍스트 도구나 파서가 이 처리를 되돌리지 않으면 한글 명령이 깨지거나 검색에 걸리지 않습니다. dissect.target 과 plaso 의 zsh 처리 코드에는 메타 처리를 되돌리는 부분이 없습니다[15][16].
- **fish 파일 안의 bash 명령.** fish 는 기본 세션(`fish`)의 기록이 비어 있으면 `HISTFILE` 또는 `~/.bash_history` 를 읽어 가져옵니다[11]. 이때 가져온 명령은 모두 가져온 순간의 시각 하나로 `when` 이 찍힙니다[10]. 여러 항목이 같은 `when` 을 공유하면 fish 가 처음 뜬 시각일 가능성이 있고, bash 로 그 명령을 친 시각이 아닙니다.
- **fish 의 다른 세션 파일.** `fish_history` 값을 바꾼 세션은 `fish_history` 가 아닌 다른 파일에 기록합니다[7]. `fish_history` 를 빈 값으로 두면 디스크에 저장하지 않습니다[8].
- **저장하지 않는 설정.** fish 는 `fish --private`(`-P`)로 띄우거나 `fish_private_mode` 가 비어 있지 않으면 디스크에 쓰지 않습니다[6]. `fish_should_add_to_history` 함수를 정의하면 이 함수가 저장 여부를 전부 정하고, 공백 규칙도 이 함수가 대신합니다[9]. zsh 의 `HIST_IGNORE_SPACE`, `HIST_NO_STORE`, `HISTORY_IGNORE` 도 줄을 뺍니다[1][2]. 이런 설정과 기록 지우기가 어디에 흔적을 남기는지는 [기록 지우기와 끄기](evasion.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

zsh 확장 형식 줄 하나를 헥스로 보면 아래와 같습니다. 명세로 만든 예시이고, 명령은 `ls 한` 입니다.

```
00000000: 3a20 3137 3637 3232 3536 3030 3a30 3b6c  : 1767225600:0;l
00000010: 7320 ed83 b583 bc0a                      s ......
```

`3a 20` 이 `: `, 이어지는 ASCII 숫자가 시작 시각, `3a 30 3b` 가 `:0;`(걸린 시간 0초)입니다. `한` 의 UTF-8 은 `ed 95 9c` 인데, `95` 와 `9c` 가 0x83~0xA2 범위라서 `83 b5`(0x95 XOR 0x20)와 `83 bc`(0x9c XOR 0x20)로 바뀌었습니다[5]. 실제 데이터에서는 기록 파일에 `83` 바이트가 있는지 먼저 보고, 있으면 `83` 을 지우고 다음 바이트를 0x20 과 XOR 해 원래 바이트로 돌린 뒤 UTF-8 로 읽습니다.

fish 기록은 평문이라 헥스로 볼 것이 적습니다. `- cmd: ` 로 시작하는 줄 수를 세면 항목 수가 되고, `when:` 값이 모두 같은 항목 묶음이 있는지 보면 bash 기록을 가져온 흔적을 가려낼 수 있습니다.

### 공개 도구로 한 번

- dissect.target 의 `commandhistory` 플러그인은 zsh 일반·확장 형식을 모두 읽고, 확장 형식이면 시작 시각을 `ts` 로 내놓습니다[15]. 확장 줄은 `: ` 뒤에 10자리 숫자가 올 때만 알아보고, 여러 줄 명령의 이어진 줄은 따로따로 항목으로 나옵니다[15]. fish 는 정규식으로 `- cmd:` 와 `when:` 만 뽑으므로 `added_when` 과 `paths:` 는 결과에 없습니다[15].
- plaso 의 `zsh_extended_history` 파서는 확장 형식만 읽습니다. 파일 앞부분이 `: 숫자:숫자;` 모양이어야 붙고, 이어진 줄은 공백으로 이어 한 명령으로 만듭니다[16]. 확장 형식이 아닌 zsh 기록은 plaso 타임라인에 들어가지 않습니다.
- 실행 중인 zsh 프로세스의 메모리에서는 파일에 없던 명령도 찾을 수 있습니다. Block·Dewald(2017)의 zsh 5.2 시험 환경에서 zsh 는 시각을 bash 처럼 `#숫자` 문자열이 아니라 4바이트 정수로 두어 문자열 검색으로는 찾을 수 없었고, x86 에서 56바이트, x64 에서 96바이트 힙 청크에 든 기록 항목 구조(`histent`)의 명령 포인터·시작 시각·끝 시각·명령 번호를 읽고 앞뒤 연결을 따라가 목록 전체를 복원했습니다[17]. 메모리 도구 쓰는 법은 [메모리 분석](../../../03-techniques/analysis/memory-analysis.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 것 | 맞춰 보는 것 |
|---|---|
| [bash 기록](bash.md) | 같은 계정이 bash 로 친 명령. fish 로 가져온 bash 명령의 원본 |
| [감사 로그의 실행 기록](../auditd-execve.md) | 외부 프로그램을 실행한 시각·인수. 셸 내장 명령은 남지 않음. 외부 프로그램인데 fish 기록에만 있으면 실행하지 않았을 가능성 |
| [프로세스 회계](../process-accounting.md) | 켜져 있으면 명령 이름과 끝난 시각. zsh 걸린 시간과 비교 |
| [실행 중인 프로세스](../proc.md) | 라이브에서 실행 중인 zsh·fish 프로세스와 그 사용자 |
| [로그인 기록](../../logins/wtmp-btmp-lastlog.md) | 기록 시각에 그 계정이 로그인해 있었는지 |

여러 기록을 시간순으로 합치는 방법은 [타임라인 만들기](../../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 실습

공개 시험 데이터(NIST CFReDS 의 Linux 디스크 이미지 등)로 아래 질문을 풀어 봅니다.

1. `/etc/passwd` 에서 로그인 셸이 zsh 나 fish 인 계정을 찾고, 설정 파일의 `HISTFILE` 값과 `EXTENDED_HISTORY`·`INC_APPEND_HISTORY`·`SHARE_HISTORY` 설정을 적습니다.
2. 각 홈의 `.local/share/fish/` 폴더에 `fish_history` 말고 다른 `*_history` 파일이 있는지 봅니다.
3. fish 기록에서 `when` 값이 같은 항목 묶음을 찾아, 같은 계정의 `.bash_history` 와 명령이 겹치는지 비교합니다.
4. zsh 확장 기록에서 걸린 시간이 긴 명령을 골라 시작·끝 시각을 UTC 로 적고, 감사 로그나 프로세스 회계의 시각과 맞춰 봅니다.
5. 기록 파일에 `0x83` 바이트가 있으면 메타 처리를 되돌려 명령을 다시 읽고, dissect 결과와 비교합니다.

## 참고 문헌

1. zsh, Doc/Zsh/params.yo (`HISTFILE`, `HISTSIZE`, `SAVEHIST`, `HISTORY_IGNORE`). https://github.com/zsh-users/zsh/blob/master/Doc/Zsh/params.yo
2. zsh, Doc/Zsh/options.yo (`APPEND_HISTORY`, `EXTENDED_HISTORY`, `HIST_IGNORE_SPACE`, `HIST_NO_STORE`, `HIST_SAVE_BY_COPY`, `INC_APPEND_HISTORY`, `INC_APPEND_HISTORY_TIME`, `SHARE_HISTORY`). https://github.com/zsh-users/zsh/blob/master/Doc/Zsh/options.yo
3. zsh, Functions/Newuser/zsh-newuser-install. https://github.com/zsh-users/zsh/blob/master/Functions/Newuser/zsh-newuser-install
4. zsh, Src/hist.c (기록 파일 쓰기·읽기, 잠금 파일). https://github.com/zsh-users/zsh/blob/master/Src/hist.c
5. zsh, Src/zsh.h (`Meta`, `Marker`), Src/utils.c (`IMETA`). https://github.com/zsh-users/zsh/tree/master/Src
6. fish-shell, doc_src/interactive.rst (기록 검색, 사설 모드). https://github.com/fish-shell/fish-shell/blob/master/doc_src/interactive.rst
7. fish-shell, doc_src/cmds/history.rst. https://github.com/fish-shell/fish-shell/blob/master/doc_src/cmds/history.rst
8. fish-shell, doc_src/language.rst (`fish_history`). https://github.com/fish-shell/fish-shell/blob/master/doc_src/language.rst
9. fish-shell, doc_src/cmds/fish_should_add_to_history.rst. https://github.com/fish-shell/fish-shell/blob/master/doc_src/cmds/fish_should_add_to_history.rst
10. fish-shell 3.7.0, src/history.cpp, src/history_file.cpp (`append_history_item_to_buffer`). https://github.com/fish-shell/fish-shell/tree/3.7.0/src
11. fish-shell 3.7.0, src/reader.cpp (`import_history_if_necessary`). https://github.com/fish-shell/fish-shell/blob/3.7.0/src/reader.cpp
12. fish-shell, src/history/yaml_backend.rs, src/history/file.rs. https://github.com/fish-shell/fish-shell/tree/master/src/history
13. tclahr UAC, artifacts/files/shell/zsh.yaml, fish.yaml. https://github.com/tclahr/uac/tree/main/artifacts/files/shell
14. ForensicArtifacts, artifacts/data/shell.yaml (`ZShellHistoryFile`, `FishShellHistoryFile`). https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/shell.yaml
15. dissect.target, dissect/target/plugins/os/unix/history.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/history.py
16. plaso, plaso/parsers/text_plugins/zsh_extended_history.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/zsh_extended_history.py
17. Frank Block, Andreas Dewald, "Linux memory forensics: Dissecting the user space process heap", Digital Investigation 22 (2017) S66–S75 (DFRWS 2017 USA). https://doi.org/10.1016/j.diin.2017.06.002
