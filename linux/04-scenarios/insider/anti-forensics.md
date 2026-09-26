---
title: "흔적을 지웠나"
parent: "시나리오 · 유출·은폐"
nav_order: 1100
---

# 흔적을 지웠나 (Log·History Tampering)

## 조사 질문

로그나 셸 명령 기록이 비어 있거나 기간이 끊겨 있을 때, 누군가 일부러 지우거나 끄거나 고쳤는지를 묻습니다. 사람이 손댔다면 언제 어느 계정으로 무엇을 했는지, 손대기 전 기록이 다른 곳에 남아 있는지까지 따라갑니다.

이 페이지는 지우는 방법이 아니라 "지우거나 멈추면 어디에 무엇이 남는가" 를 다룹니다. 로그 형식과 필드 설명은 각 기반 구조·아티팩트 페이지에 있고, 여기서는 조사 순서와 판단 기준만 씁니다. 파일 시각이나 시스템 시계를 되돌린 경우는 [시각을 조작했나](time-manipulation.md) 에서, 자료를 밖으로 옮긴 뒤의 정리 흔적은 [자료를 밖으로 옮겼나](data-exfiltration.md) 와 함께 봅니다.

## 먼저 확인할 것

**로그가 몇 겹으로 쌓이는가.** 한 사건이 저널, rsyslog 텍스트 로그, 감사 로그 (auditd) 에 함께 남는 구조라면 한 곳을 지워도 다른 곳에 사본이 있습니다. journald 는 커널 감사 레코드도 받으므로, 감사 로그 파일이 없어도 저널에 같은 레코드가 있을 수 있습니다([systemd 저널](../../01-foundations/logging/systemd-journal/index.md)). 반대로 `Storage=volatile` 이면 저널은 `/run/log/journal` 에만 있어 재부팅하면 사라집니다. 분석 대상에 auditd 가 깔려 있는지, rsyslog 가 도는지는 패키지 기록과 설정 파일로 확인합니다.

**정상 삭제의 기준.** 로그는 사람이 지우지 않아도 사라집니다. logrotate 의 `rotate`·`maxage` 설정과 상태 파일([로그 순환](../../01-foundations/logging/logrotate.md)), journald 의 `SystemMaxUse=`·`MaxFileSec=` 같은 보존 한도([systemd 저널](../../01-foundations/logging/systemd-journal/index.md))를 먼저 읽고, "이 설정이면 무엇이 남아 있어야 정상인가" 를 정합니다. 이 기준 없이 빈 곳을 보면 자동 삭제를 사람의 삭제로 잘못 읽습니다.

**셸 기록의 배포판 기본값.** 셸 기록이 원래 무엇을 저장하지 않는지부터 알아야 "지웠다" 와 "원래 없다" 를 가릅니다.

| 항목 | Ubuntu 24.04 (`/etc/skel/.bashrc`) | RHEL 9 (`/etc/profile`, `/etc/bashrc`) |
|---|---|---|
| `HISTCONTROL` | `ignoreboth`: 공백으로 시작하는 줄과 바로 앞과 같은 줄을 저장하지 않음[25] | `ignoredups`, 미리 `ignorespace` 였으면 `ignoreboth`[26] |
| `HISTSIZE` | 1000[25] | 1000[26] |
| `HISTFILESIZE` | 2000[25] | 설정 없음(bash 가 `HISTSIZE` 값을 씀)[24] |
| 덧붙여 쓰기 | `shopt -s histappend`[25] | 대화형 셸에서 `shopt -s histappend` 와 `history -a`[26] |

**시각 기준.** 저널과 감사 로그의 시각은 UTC 기준 값이고, 전통 syslog 줄에는 연도와 시간대가 없습니다. 여러 로그를 한 줄로 세우기 전에 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 과 [호스트 이름·시간대](../../02-artifacts/system-info/hostname-timezone.md) 로 분석 대상의 시간대를 정해 둡니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 로그 설정(journald.conf, rsyslog, logrotate, 감사 규칙) | 무엇이 남아야 정상인가 | [로그 순환](../../01-foundations/logging/logrotate.md), [systemd 저널](../../01-foundations/logging/systemd-journal/index.md), [감사 로그 형식](../../01-foundations/logging/auditd-format.md) |
| 2 | 저널 파일 이름·머리·순번 | 빠진 파일, 회전 사유, 손상 | [저널 파일 형식](../../01-foundations/logging/systemd-journal/file-format.md), [손상·삭제된 저널](../../01-foundations/logging/systemd-journal/corruption.md) |
| 3 | journald 자신의 메시지 | 활성 파일 삭제, 회전 요청과 요청한 PID | [journalctl 로 읽기](../../01-foundations/logging/systemd-journal/journalctl.md) |
| 4 | 감사 로그의 CONFIG_CHANGE·DAEMON_* | 감사 끄기, 규칙 삭제, 데몬 종료와 신호를 보낸 쪽 | [감사 로그 형식](../../01-foundations/logging/auditd-format.md) |
| 5 | syslog 텍스트 로그, wtmp·btmp·lastlog | 빈 기간, 순서가 어긋난 레코드 | [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md), [로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md), [로그인 기록](../../02-artifacts/logins/wtmp-btmp-lastlog.md) |
| 6 | 셸 기록 파일의 상태 | 0 바이트 파일, 링크, 기록을 끄는 설정 줄 | [기록 지우기와 끄기](../../02-artifacts/execution/shell-history/evasion.md) |
| 7 | 명령 실행 흔적 | `rm`·`shred`·`truncate`·`journalctl`·`auditctl` 실행 | [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md), [프로세스 회계](../../02-artifacts/execution/process-accounting.md) |
| 8 | 지운 파일 조각 | 지운 로그·저널의 내용 | [지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md) |
| 9 | 메모리와 /proc | 열린 채 지운 파일, 셸의 기록 목록 | [실행 중인 프로세스](../../02-artifacts/execution/proc.md), [메모리 분석](../../03-techniques/analysis/memory-analysis.md) |
| 10 | 루트킷 | 로그 줄이나 파일을 가리는 라이브러리·모듈 | [루트킷 찾기](../../03-techniques/analysis/rootkit-detection.md), [공유 라이브러리 가로채기](../../02-artifacts/persistence/ld-preload.md) |

## 분석 흐름

1. **정상이면 남아야 할 기록의 범위를 적습니다.** 설정에서 뽑은 보존 기간·회전 횟수·크기 한도와 설치 시점을 기준으로, 로그 종류마다 "있어야 할 기간" 을 표로 만듭니다. 그 표와 실제로 남은 기간을 겹쳐 보면 빈 곳이 자동 삭제로 설명되는지 드러납니다.

2. **저널에서 journald 가 스스로 남긴 줄을 찾습니다.** journald 는 쓰고 있던 활성 파일이 지워진 것을 다음에 쓸 때 알아채고, `경로: Journal file has been deleted, rotating.` 를 남긴 뒤 새 파일을 만듭니다[1][2]. 그래서 저널 파일을 지운 사건 자체가 새 저널 파일에 남습니다. 이 줄의 수준은 RHEL 9(systemd 252) 에서 warning 이고[2], 현재 upstream 에서는 속도 제한이 붙은 info 입니다[1]. 손상 때는 `Journal file corrupted, rotating.`, 비정상 종료 때는 `Unclean shutdown, rotating.` 가 남습니다[1][2]. 회전 요청도 남는데, 클라이언트 요청이면 `Received client request to rotate journal, rotating.` 가 남고[2][3], SIGUSR2 신호로 요청하면 `Received SIGUSR2 signal from PID 번호, as request to rotate journal, rotating.` 처럼 신호를 보낸 PID 가 함께 남습니다[1][2].

3. **저널 파일 목록의 빈 곳을 봅니다.** `journalctl --vacuum-*` 은 journalctl 프로세스가 직접 보관 파일을 지우고[4], 지운 파일을 알리는 `Deleted archived journal …` 줄은 journalctl 의 출력일 뿐 journald 가 저널에 적는 줄이 아닙니다[5]. 그래서 vacuum 으로 지운 사실은 저널 안에 거의 남지 않고, `--rotate` 를 함께 썼다면 회전 요청 줄만 남습니다. 이때는 저널 파일 이름에 든 seqnum_id·첫 순번과 파일 안의 순번을 봅니다. 순번은 항목마다 1부터 하나씩 올라가고 같은 seqnum_id 를 쓰는 모든 파일에서 겹치지 않는데, 시스템 저널과 사용자별 저널이 같은 seqnum_id 를 씁니다[8]. 그래서 한 파일 안에서 순번이 건너뛰는 것은 정상이고, 같은 seqnum_id 의 파일을 모두 모아 순번을 합쳐 본 뒤에도 비는 번호가 있으면 항목이나 파일이 사라졌을 가능성이 있습니다. 파일째 사라진 경우 vacuum 의 삭제 순서와 맞는지는 [손상·삭제된 저널](../../01-foundations/logging/systemd-journal/corruption.md) 의 기준으로 따지고, vacuum 이 블록을 덮어쓰지 않고 해제만 하므로 여유 공간에서 저널 조각을 찾습니다.

4. **끼워 넣은 저널 항목을 가려냅니다.** 밑줄로 시작하는 필드(`_PID`, `_UID`, `_EXE`, `_COMM` 등)는 journald 가 붙이고 보내는 쪽이 바꿀 수 없습니다[6]. `MESSAGE` 와 `SYSLOG_IDENTIFIER` 는 보내는 쪽이 정하므로, 식별자가 `sshd` 인데 `_EXE` 가 셸이나 `logger` 라면 사람이 끼워 넣은 줄일 가능성이 있습니다. 저널 봉인 (Forward Secure Sealing, FSS) 으로 변조를 검증할 수 있는 것은 `--setup-keys` 로 키를 만든 뒤 쓴 파일에 한하고, 검증에는 `--verify` 와 `--verify-key=` 가 필요합니다[7]. 키를 만든 흔적이 없으면 봉인 검증은 할 수 없습니다.

5. **감사 로그에서 감사를 끄거나 멈춘 기록을 찾습니다.** 규칙을 넣거나 빼면 커널이 CONFIG_CHANGE(1305) 레코드에 `op=add_rule` 또는 `op=remove_rule`, 규칙 키, `list=`, `res=` 를 남깁니다[10][16]. `auditctl -e` 처럼 설정 값을 바꾸면 `op=set audit_enabled=새값 old=옛값` 과 요청한 세션의 `auid`·`ses`, `res=` 가 남습니다[9]. 이 레코드는 바꾸기 전에 감사가 켜져 있었을 때만 쓰므로, 감사를 끄는 순간의 레코드는 남고 그 뒤 활동은 남지 않습니다[9]. `-e 2` 로 잠근 상태에서는 설정을 바꿀 수 없고 시도는 `res=0` 으로 기록되며, 잠금을 풀려면 재부팅해야 합니다[9][14]. upstream 예시 규칙 `99-finalize.rules` 에는 `-e 2` 가 주석으로 들어 있어 잠금은 기본이 아닙니다[15].

    auditd 데몬이 멈춘 흔적은 DAEMON_END(1201) 레코드입니다[16]. auditd 는 끝나기 전에 커널에 마지막 신호를 보낸 쪽을 물어, 답을 받으면 `op=terminate auid=… uid=… ses=… pid=… res=success` 에 그 신호를 보낸 쪽의 `auid` 와 `pid` 를 적고, 못 받으면 `auid=-1 … pid=-1` 로 적습니다[11][12]. 시작은 DAEMON_START(1200) `op=start`, 오류로 멈추면 DAEMON_ABORT(1202) `op=error-halt`, 로그 회전 요청은 DAEMON_ROTATE(1205) 입니다[11][16]. upstream `auditd.service` 에는 `RefuseManualStop=yes` 가 있어 `systemctl stop` 으로는 멈추지 않으므로[13], 멈췄다면 신호를 직접 보냈거나 다른 경로였을 가능성이 있습니다. 배포판의 유닛 파일은 분석 대상에서 확인합니다. 감사 규칙에 upstream `30-stig.rules` 처럼 `auid>=1000` 사용자의 `unlink`·`unlinkat`·`rename`·`renameat` 를 `key=delete` 로 거는 규칙이 있으면[15], 로그 파일을 지운 계정과 경로가 SYSCALL·PATH 레코드로 남습니다.

6. **텍스트 로그와 로그인 기록의 빈 곳을 봅니다.** rsyslog 로그의 회전본이 모자라도 logrotate 가 지웠을 수 있으니 1단계의 표와 상태 파일의 마지막 회전 시각을 먼저 맞춰 봅니다([로그 순환](../../01-foundations/logging/logrotate.md)). wtmp 는 login·init·일부 getty 가 쓰지만 이 프로그램들은 파일을 새로 만들지 않아서, 파일이 지워지면 그 뒤로 기록이 멈춥니다[17]. 다만 systemd 의 tmpfiles 설정에는 `f /var/log/wtmp 0664 root utmp -` 줄이 있고, `f` 는 파일이 없을 때만 만드는 지시라서 부팅 때 systemd-tmpfiles 가 빈 wtmp 를 다시 만듭니다[29][30]. 그래서 wtmp 의 아이노드가 부팅 시각 무렵에 새로 생겼다면 그 전에 파일이 지워졌을 가능성이 있습니다. `utmpdump` 는 wtmp 를 텍스트로 풀고 `-r` 로 다시 이진 파일로 되돌릴 수 있는데, 이 기능은 손상된 항목을 고치는 디버깅 용도입니다[18]. 이렇게 되돌리면 파일 내용을 다시 쓰므로 mtime·ctime 이 그 시각으로 바뀌고, 레코드 시각 순서가 어긋날 가능성이 있습니다. ctime 형식으로 텍스트를 찍은 마지막 판은 util-linux 2.28 이고, 그 뒤 판의 텍스트 시각은 밀리초까지의 ISO-8601 UTC 입니다. 옛 ctime 형식 덤프를 되돌리면 시간대만큼 시각이 밀릴 수 있습니다[18]. 그래서 로그인 기록 전체가 시간대 차이만큼 어긋나 있다면 이런 변환을 거쳤는지 의심해 봅니다. UAC 는 로그 변조를 찾는 데 쓸 수 있다는 주석과 함께 `utmpdump` 결과를 모읍니다[20]. lastlog 는 `lastlog -C -u 사용자` 로 지우거나 `-S -u 사용자` 로 현재 시각을 넣을 수 있으므로[19], lastlog 값 하나로 마지막 로그인을 확정하지 않습니다.

7. **셸 기록의 상태를 봅니다.** `HISTFILE` 이 풀려 있으면 셸이 끝날 때 기록을 저장하지 않고, `HISTFILESIZE=0` 이면 기록 파일을 0 바이트로 자릅니다[24]. 기록 파일이 `/dev/null` 링크인지, 시작 파일에 이런 설정 줄이 있는지, 파일 크기와 시각이 어떤지는 [기록 지우기와 끄기](../../02-artifacts/execution/shell-history/evasion.md) 의 기준으로 봅니다. `history -c` 같은 셸 내장 명령은 새 프로세스를 띄우지 않아 실행 기록에 남지 않는다는 점도 그 페이지에서 다룹니다.

8. **지우는 명령이 실행된 흔적을 찾습니다.** 감사 로그의 execve 레코드와 프로세스 회계에서 `rm`, `shred`, `truncate`, `journalctl`, `auditctl`, `utmpdump`, `lastlog` 가 실행된 시각과 계정을 찾고, 2~6단계에서 찾은 시각과 맞춰 봅니다. `shred` 가 보여도 곧바로 복구를 포기하지 않습니다. `shred` 는 파일 시스템과 하드웨어가 제자리에 덮어쓴다는 가정에 기대고, ext3·ext4 의 `data=journal` 모드처럼 데이터까지 저널에 쓰도록 설정한 파일 시스템(Btrfs·XFS·ZFS 등), 스냅숏을 만드는 파일 시스템, 압축 파일 시스템, 웨어 레벨링을 하는 SSD 에서는 이 가정이 깨집니다[23]. ext3·ext4 기본인 `data=ordered` 와 `data=writeback` 에서는 `shred` 가 평소대로 동작합니다[23]. 저장 장치와 마운트 옵션을 확인한 뒤 [지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md) 로 조각을 찾습니다.

9. **실행 중인 시스템이면 열린 채 지운 파일을 봅니다.** 프로세스가 연 파일은 `/proc/PID/fd/` 아래에 그 파일을 가리키는 링크로 보이고[21], 파일이 지워져도 링크 끝에 `(deleted)` 가 붙은 채 남아 그 링크로 내용을 읽을 수 있습니다[22]. UAC 의 `deleted.yaml` 은 실행 파일이 지워진 프로세스의 fd 만 살펴보기 때문에[22], 실행 파일은 멀쩡한 데몬이 열어 둔 지운 로그는 이 항목에 잡히지 않습니다. 모든 프로세스의 fd 를 따로 봅니다([라이브 응답 수집](../../03-techniques/acquisition/live-response.md)).

10. **로그 파일의 시각을 봅니다.** 로그 파일의 mtime 을 되돌려도 커널이 시각을 바꾸는 순간 ctime 을 그 시각으로 고치므로[27][28], mtime 보다 ctime 이 뒤인 로그 파일은 시각을 되돌린 흔적일 수 있습니다. 자세한 판단은 [시각을 조작했나](time-manipulation.md) 에서 합니다.

### 증명하는 것과 증명하지 못하는 것

journald 의 `Journal file has been deleted`, `Received SIGUSR2 signal from PID …`, `Received client request to rotate journal` 줄은 그 시각에 그 동작이 있었다는 기록입니다. 감사 로그의 `op=remove_rule` 과 `op=set audit_enabled=0` 은 규칙 삭제·감사 끄기 요청과 요청한 세션(`auid`·`ses`)을 보여 주고, DAEMON_END 의 `auid`·`pid` 는 auditd 에 종료 신호를 보낸 쪽을 보여 줍니다.

반면 로그가 없다는 사실만으로는 사람이 지웠다고 말할 수 없습니다. 자동 회전, 크기 한도, 설치 전 기간, 메모리에만 쓰는 저장 설정이 모두 같은 빈 곳을 만듭니다. 셸 기록이 비었다는 것도 "지웠다" 를 뜻하지 않습니다. 공백으로 시작한 명령은 기본 설정에서 저장되지 않고, 비대화형 셸이나 강제 종료된 셸도 기록을 남기지 않습니다. `journalctl --vacuum-*` 은 저널에 줄을 거의 남기지 않으므로, 그 흔적이 없다고 실행이 없었다고 말할 수도 없습니다.

## 흔한 오판

- **"저널은 변조를 막는다."** 봉인은 키를 만든 시스템에만 있고, 기본 설치에는 없습니다[7].
- **"`.journal~` 파일이 있으니 누가 망가뜨렸다."** 전원이 끊기거나 비정상 종료해도 생깁니다([손상·삭제된 저널](../../01-foundations/logging/systemd-journal/corruption.md)).
- **"wtmp 가 작거나 없으니 지웠다."** wtmp 는 보통 logrotate 가 돌리므로 회전본(`wtmp.1`)과 logrotate 설정의 `create` 줄까지 봅니다([로그 순환](../../01-foundations/logging/logrotate.md)).
- **"감사 로그에 끈 기록이 없으니 안 껐다."** 이미 꺼진 상태에서 설정을 바꾸면 CONFIG_CHANGE 레코드가 남지 않습니다[9].
- **"기록에 없는 명령은 지운 것이다."** Ubuntu 24.04 기본 설정에서는 앞에 공백을 둔 명령이 처음부터 저장되지 않습니다[25].
- **"로그 줄이 있으니 그 프로그램이 썼다."** 저널의 `SYSLOG_IDENTIFIER` 와 syslog 줄의 태그는 보내는 쪽이 정합니다. 저널이면 `_EXE`·`_PID` 로 맞춰 봅니다[6].

## 보고서 문장 예

아래 값은 모두 만든 예시입니다.

- "2026-03-04 15:02:11(UTC)에 journald 가 `/var/log/journal/…/system.journal: Journal file has been deleted, rotating.` 를 남겼습니다. 이 시각에 활성 저널 파일이 지워졌다는 기록이며, 누가 지웠는지는 이 줄에 없습니다. 같은 시각 앞뒤의 감사 로그에서 계정 alice(auid=1000)가 `rm` 을 실행한 execve 레코드를 확인했습니다."
- "감사 로그에 `type=CONFIG_CHANGE … op=set audit_enabled=0 old=1 auid=1000 ses=4 … res=1` 레코드가 있습니다. 이 레코드 이후 감사 기록이 없는 것은 이 설정 변경과 들어맞습니다(필드 순서는 실제 레코드에서 확인합니다)."
- "`/var/log/wtmp` 의 레코드 중 2026-03-01 부터 2026-03-05 사이가 비어 있습니다. logrotate 설정과 상태 파일로는 이 빈 곳이 설명되지 않으며, 사람이 지웠는지는 이 기록만으로 판단할 수 없습니다."

## 함께 볼 페이지

- [자료를 밖으로 옮겼나](data-exfiltration.md) — 유출 뒤 정리한 흔적과 함께 봅니다
- [시각을 조작했나](time-manipulation.md) — 로그 파일과 시스템 시계를 되돌린 흔적
- [누가 그 명령을 실행했나](../attribution/user-attribution.md) — 지운 계정과 사람을 잇는 법
- [SSH 로 들어왔나](../intrusion/ssh-intrusion.md) — 침입 뒤 로그를 지운 경우
- [로그 분석](../../03-techniques/analysis/log-analysis.md), [타임라인 만들기](../../03-techniques/analysis/timeline.md) — 여러 로그를 시간순으로 합치는 법
- [Linux 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) — 기록으로 확인되는 만큼만 쓰는 법
- [타임라인 작성 (Windows 판)](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html) — 타임라인 공통 원리

## 참고 문헌

1. systemd, src/journal/journald-manager.c. https://github.com/systemd/systemd/blob/main/src/journal/journald-manager.c
2. systemd RHEL 9 source-git(systemd 252), src/journal/journald-server.c. https://github.com/redhat-plumbers/systemd-rhel9/blob/main/src/journal/journald-server.c
3. systemd, src/journal/journald-varlink.c. https://github.com/systemd/systemd/blob/main/src/journal/journald-varlink.c
4. systemd, src/journal/journalctl-varlink.c. https://github.com/systemd/systemd/blob/main/src/journal/journalctl-varlink.c
5. systemd, src/libsystemd/sd-journal/journal-vacuum.c. https://github.com/systemd/systemd/blob/main/src/libsystemd/sd-journal/journal-vacuum.c
6. systemd, man/systemd.journal-fields.xml. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
7. systemd, man/journalctl.xml (`--setup-keys`, `--verify`, `--verify-key=`). https://github.com/systemd/systemd/blob/main/man/journalctl.xml
8. systemd, docs/JOURNAL_FILE_FORMAT.md. https://github.com/systemd/systemd/blob/main/docs/JOURNAL_FILE_FORMAT.md
9. Linux kernel, kernel/audit.c (`audit_log_config_change`, `audit_do_config_change`). https://github.com/torvalds/linux/blob/master/kernel/audit.c
10. Linux kernel, kernel/auditfilter.c. https://github.com/torvalds/linux/blob/master/kernel/auditfilter.c
11. linux-audit, audit-userspace src/auditd.c. https://github.com/linux-audit/audit-userspace/blob/master/src/auditd.c
12. linux-audit, audit-userspace lib/libaudit.c (`audit_format_signal_info`). https://github.com/linux-audit/audit-userspace/blob/master/lib/libaudit.c
13. linux-audit, audit-userspace init.d/auditd.service.in. https://github.com/linux-audit/audit-userspace/blob/master/init.d/auditd.service.in
14. linux-audit, audit-userspace docs/auditctl.8. https://github.com/linux-audit/audit-userspace/blob/master/docs/auditctl.8
15. linux-audit, audit-userspace rules/30-stig.rules · 99-finalize.rules. https://github.com/linux-audit/audit-userspace/tree/master/rules
16. linux-audit, audit-documentation specs/messages/message-dictionary.csv. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
17. man-pages, man5/utmp.5. https://github.com/mkerrisk/man-pages/blob/master/man5/utmp.5
18. util-linux, login-utils/utmpdump.1.adoc. https://github.com/util-linux/util-linux/blob/master/login-utils/utmpdump.1.adoc
19. shadow, man/lastlog.8.xml. https://github.com/shadow-maint/shadow/blob/master/man/lastlog.8.xml
20. UAC, artifacts/live_response/system/utmpdump.yaml. https://github.com/tclahr/uac/blob/main/artifacts/live_response/system/utmpdump.yaml
21. man-pages, man5/proc.5. https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
22. UAC, artifacts/live_response/process/deleted.yaml. https://github.com/tclahr/uac/blob/main/artifacts/live_response/process/deleted.yaml
23. GNU coreutils, doc/coreutils.texi (shred invocation). https://github.com/coreutils/coreutils/blob/master/doc/coreutils.texi
24. GNU Bash 5.2, doc/bash.1 (`HISTFILE`, `HISTFILESIZE`, HISTORY). https://github.com/tianon/mirror-bash/blob/master/doc/bash.1
25. Ubuntu noble bash 패키지(5.2.21-2ubuntu4), debian/skel.bashrc. https://github.com/cpsource/bash-5.2.21/blob/master/debian/skel.bashrc
26. setup 2.13.7(CentOS Stream 9 setup 패키지 원본), profile · bashrc. https://releases.pagure.org/setup/setup-2.13.7.tar.bz2
27. Linux kernel, fs/utimes.c. https://github.com/torvalds/linux/blob/master/fs/utimes.c
28. man-pages, man7/inode.7. https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
29. systemd, tmpfiles.d/var.conf.in. https://github.com/systemd/systemd/blob/main/tmpfiles.d/var.conf.in
30. systemd, man/tmpfiles.d.xml · man/systemd-tmpfiles.xml. https://github.com/systemd/systemd/blob/main/man/tmpfiles.d.xml
