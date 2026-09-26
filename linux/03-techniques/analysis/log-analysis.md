---
title: "로그 분석"
parent: "기법 · 분석"
nav_order: 970
---

# 로그 분석 (Log Analysis)

조사 질문을 먼저 정하고, 저널·텍스트 로그·감사 로그 가운데 그 질문에 답하는 기록을 골라 거른 뒤, 세션 번호와 시각으로 서로 이어 붙이는 방법입니다.

각 로그의 파일 형식과 필드 뜻은 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md), [systemd 저널](../../01-foundations/logging/systemd-journal/index.md), [감사 로그 형식 (auditd)](../../01-foundations/logging/auditd-format.md), [로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md) 에서 다룹니다. 이 쪽은 "어떤 질문에 어느 로그를 어떻게 거르고, 결과를 어디까지 말할 수 있나" 만 다룹니다.

## 언제 쓰나

- 원격 로그인이 있었는지, 어느 주소에서 어느 계정으로 들어왔는지를 확인할 때
- 누가 언제 root 권한으로 명령을 실행했는지를 볼 때
- 계정을 만들거나 바꾼 시점을 찾을 때
- 특정 시간대에 서비스·커널·감사 체계에서 무슨 일이 있었는지를 좁혀 볼 때
- 로그가 빠진 구간이 있는지, 즉 지우기나 기록 중단의 흔적을 찾을 때

여러 기록을 한 줄의 시간축에 세우는 일은 [타임라인 만들기](timeline.md) 에서 다루고, 이 쪽의 결과는 그 타임라인에 넣을 재료가 됩니다.

## 절차

1. **어떤 로그가 있는지부터 적습니다.** 검체에 영구 저널(`/var/log/journal`)이 있는지, rsyslog 가 쓰는 텍스트 파일(Ubuntu 의 `auth.log`·`syslog`, RHEL 의 `secure`·`messages`)이 있는지, `/var/log/audit/` 가 있는지, `wtmp`·`btmp` 가 있는지를 확인합니다. 배포판별 파일 이름과 rsyslog 규칙은 [인증 로그 (auth.log·secure)](../../02-artifacts/logins/auth-log.md) 의 표를, 순환본 이름과 순서는 [로그 순환 (logrotate)](../../01-foundations/logging/logrotate.md) 을 봅니다. 순환본과 압축본까지 모두 모아야 기간이 이어집니다.

2. **로그마다 덮는 기간을 잽니다.** 저널은 `journalctl --list-boots` 로 부팅 번호·부팅 ID·그 부팅의 첫 메시지와 마지막 메시지 시각을 뽑습니다[1]. 감사 로그는 `aureport -t` 가 로그 파일마다 시작 시각과 끝 시각을 냅니다[4]. 텍스트 로그는 파일마다 첫 줄과 마지막 줄의 시각을 봅니다. 이 기간을 나란히 놓으면 한쪽에만 빈 곳이 드러나고, 그 빈 곳이 순환·삭제·전원 꺼짐 가운데 무엇인지를 [부팅과 종료 기록](../../02-artifacts/system-info/boot-shutdown.md) 과 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md) 로 가립니다.

3. **질문에 맞는 기록만 거릅니다.** 질문별 출발점은 아래와 같습니다.

   | 질문 | 먼저 볼 기록 | 거르는 기준 | 자세한 쪽 |
   |---|---|---|---|
   | 원격 로그인 | 인증 로그, 저널 | 보고자 `sshd`·`sshd-session` 의 `Accepted`·`Failed` 줄[6] | [SSH](../../02-artifacts/logins/ssh/index.md) |
   | 로그인 세션 | 인증 로그, 저널 | pam_unix 의 `session opened`·`session closed`, systemd-logind 의 `New session`·`Removed session`[5] | [인증 로그](../../02-artifacts/logins/auth-log.md) |
   | 권한 상승 | 인증 로그, 감사 로그 | sudo 줄의 `COMMAND=`, su 줄, pkexec 의 `Executing command`[5] | [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md) |
   | 계정 변경 | 감사 로그, 인증 로그 | `aureport -m`(계정 변경 보고서)[4] | [계정 생성·변경 흔적](../../02-artifacts/logins/account-changes.md) |
   | 명령 실행 | 감사 로그 | `ausearch -m EXECVE`, 규칙 키 `-k`[3] | [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md) |
   | 서비스·커널 동작 | 저널, 커널 로그 | `-u` 유닛, `-k` 커널 메시지[1] | [커널 로그](../../02-artifacts/system-info/kernel-log.md) |

   저널은 명령 끝에 `필드=값` 을 붙여 거르고, 서로 다른 필드는 AND, 같은 필드를 여럿 주면 OR 로 묶입니다[1]. 감사 로그의 `ausearch` 는 옵션마다 AND 로 묶고, `-m` 과 `-n` 만 값을 여럿 받아 어느 하나라도 맞으면 고릅니다[3]. 아래는 마운트한 검체에서 쓰는 만든 예시입니다.

   ```text
   # 저널: sshd 와 sshd-session 이 보낸 항목 (같은 필드 두 값은 OR)
   journalctl -D /mnt/evidence/var/log/journal --utc -o short-iso-precise \
     SYSLOG_IDENTIFIER=sshd SYSLOG_IDENTIFIER=sshd-session

   # 감사 로그: 옮겨 온 로그 폴더에서 로그인 레코드를 CSV 로
   ausearch -if /mnt/evidence/var/log/audit -m USER_LOGIN --format csv > user_login.csv

   # 감사 로그: 실패한 인증 시도만 요약
   aureport -if /mnt/evidence/var/log/audit -au --failed
   ```

   `-if` 는 다른 기계로 옮긴 로그나 일부만 남은 로그를 읽을 때 쓰는 옵션입니다[3][4]. 저널 옵션 전체와 검체를 여는 방법은 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 의 하위 쪽에서 다룹니다.

4. **한 로그인에서 나온 기록을 세션으로 묶습니다.** 감사 로그의 `ses` 필드([감사 로그 형식](../../01-foundations/logging/auditd-format.md) 참고)에 담기는 로그인 세션 번호는 사용자가 로그인할 때 정해져 그 로그인에서 나온 프로세스를 하나로 묶고, `ausearch --session 번호` 로 그 세션의 이벤트만 고를 수 있습니다[3]. 저널 항목에는 보낸 프로세스의 감사 세션과 로그인 UID 가 `_AUDIT_SESSION`·`_AUDIT_LOGINUID` 로, systemd 세션 ID 가 `_SYSTEMD_SESSION` 으로 붙습니다[2]. 그래서 감사 로그의 `ses`·`auid` 값으로 저널을 거르면 같은 로그인에서 나온 서비스 메시지를 함께 볼 수 있습니다. logind 의 `New session N of user 이름.` 줄[5]의 N 과 `_SYSTEMD_SESSION` 값, sshd 줄의 PID 는 검체에서 서로 맞대어 이어 붙입니다.

5. **같은 사건을 두 곳 이상에서 확인합니다.** 원격 로그인 하나는 sshd 의 `Accepted` 줄, pam_unix 의 세션 열림 줄, 감사 로그의 `USER_LOGIN` 레코드, `wtmp` 의 로그인 레코드에 각각 남을 수 있습니다. 네 곳의 시각과 계정·주소가 맞으면 보고서에 쓸 수 있고, 한 곳에만 있으면 그 기록이 어떻게 생겼는지를 먼저 따집니다. 맞춰 볼 항목은 [인증 로그](../../02-artifacts/logins/auth-log.md) 와 [로그인 기록 (wtmp·btmp·lastlog)](../../02-artifacts/logins/wtmp-btmp-lastlog.md) 의 교차 검증 표에 있습니다.

6. **시각을 UTC 로 맞춘 뒤 타임라인에 넣습니다.** 저널의 `__REALTIME_TIMESTAMP` 는 journald 가 항목을 받은 순간의 시각이고 UTC 기준 마이크로초입니다[2]. 감사 로그 줄의 `msg=audit(…)` 안 시각 값도 epoch 기준입니다([감사 로그 형식](../../01-foundations/logging/auditd-format.md) 참고). Ubuntu 24.04 의 인증 로그 줄은 `2024-01-12T13:37:00.000000+02:00` 처럼 UTC 오프셋이 붙은 시각으로 시작하고, CentOS 계열 줄은 `Jan 12 13:37:00` 처럼 연도와 시간대 없이 시작합니다[5]. 연도와 시간대가 없는 줄은 기록한 시스템의 현지 시각으로 보고 연도를 따로 정합니다. 형식별 해석은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 과 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md) 의 "시각 해석" 을, 검체의 시간대는 [호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md) 을 봅니다.

## 도구

| 도구 | 하는 일 | 쓸 때 볼 점 |
|---|---|---|
| `journalctl` | 저널 폴더·파일·디스크 이미지를 읽고 필드로 거름, `--list-boots` 로 부팅별 기간[1] | root 와 `systemd-journal`·`adm`·`wheel` 그룹 구성원은 모든 저널 파일을 읽을 수 있습니다[1]. 옵션마다 처음 들어간 systemd 판이 있어서(`short-iso-precise` 는 234판) 분석 PC 의 journalctl 판에 따라 쓸 수 있는 옵션이 다릅니다[1] |
| `ausearch` (audit-userspace) | 조건으로 감사 이벤트 검색, `-if` 로 옮긴 로그 읽기, `--format csv`·`text` 출력[3] | 한 시스템 콜이 커널에 들어갔다 나오는 동안 생긴 레코드는 같은 이벤트 ID 로 묶이므로 PATH 같은 보조 레코드도 함께 나옵니다[3] |
| `aureport` (audit-userspace) | 인증(`-au`)·로그인(`-l`)·계정 변경(`-m`)·규칙 키(`-k`)·실행 파일(`-x`)·이상 징후(`-n`)·로그 파일별 기간(`-t`) 보고서[4] | 요약 보고서가 아니면 이벤트 번호가 나오므로 `ausearch -a 번호` 로 원래 이벤트를 봅니다[4]. `-nc` 는 CONFIG_CHANGE 를 빼서 키 보고서의 오탐을 줄입니다[4] |
| plaso `syslog` 파서 | syslog 줄을 이벤트로 바꾸고, sshd 의 실패·성공·연결 줄과 cron 줄을 필드로 나눔[6] | 보고자 `sshd` 와 `sshd-session` 을 모두 sshd 로 읽습니다[6] |
| dissect.target `authlog` 플러그인 | 인증 로그 줄을 sudo·sshd·systemd-logind·su·pkexec·PAM 별 필드로 나눔[5] | 정규식 한계는 [인증 로그](../../02-artifacts/logins/auth-log.md) 의 함정을 봅니다 |
| Velociraptor `Linux.Events.SSHBruteforce` | 한 시간 안에 비밀번호 실패가 쌓인 뒤 이어진 비밀번호 성공을 알림[7] | 아래 함정 참고 |
| Sigma 규칙 | 로그 종류(`logsource`)와 찾을 문자열·필드를 적은 탐지 조건[8] | 규칙에 오탐 원인을 적는 칸(`falsepositives`)이 있습니다[8] |

## 함정과 한계

- **도구마다 알아보는 줄이 다릅니다.** Velociraptor `Linux.Events.SSHBruteforce` 는 Grok 식이 `SYSLOGTIMESTAMP` 로 시작하고 프로그램 이름이 `sshd` 인 줄만 고르며, 기본 경로가 `/var/log/auth.log` 입니다[7]. 그래서 RFC 3339 시각으로 시작하는 Ubuntu 24.04 의 줄이나 `sshd-session` 이 남긴 줄, RHEL 의 `/var/log/secure` 는 기본 설정으로는 빠질 가능성이 있습니다. plaso 는 `sshd-session` 도 읽습니다[6]. 한 도구가 0건을 냈다면 같은 조건을 `grep` 이나 `journalctl` 로 한 번 더 확인합니다.
- **SSHBruteforce 의 조건은 좁습니다.** 실패와 성공 모두 방식이 `password` 여야 하고, 실패와 성공은 원격 주소가 아니라 사용자 이름으로만 짝짓습니다[7]. 최근 3600초 안의 실패를 최대 50줄까지 들고 있다가, 같은 사용자의 실패가 `MinimumFailedLogins`(기본 2)보다 많으면, 즉 기본값으로는 세 번 이상이면 알립니다[7]. 이 아티팩트는 살아 있는 시스템에서 파일에 새로 붙는 줄을 지켜보는 이벤트형(`CLIENT_EVENT`)이라서[7] 수집한 검체의 지난 기록을 훑는 용도와는 다릅니다.
- **인증 방식 분류가 도구마다 다릅니다.** dissect.target 은 sshd 줄에 `password` 가 없으면 publickey 로 분류하고[5], plaso 는 `password` 와 `publickey` 두 낱말만 문법으로 받습니다[6]. `keyboard-interactive` 로 들어온 로그인은 두 도구의 결과가 어긋날 수 있으므로 원래 줄을 봅니다.
- **`-i` 풀이는 분석 기계를 기준으로 할 수 있습니다.** `ausearch -i` 는 보강되지 않은 로그면 검색하는 기계의 계정 정보로 uid 를 이름으로 바꾸고, 보강된(ENRICHED) 로그면 기록 안의 보충 정보를 씁니다[3]. `aureport -i` 는 늘 실행하는 기계의 자원으로 바꿉니다[4]. 검체의 계정과 다르면 이름이 틀리므로, 숫자 그대로 뽑은 뒤 [UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md) 로 검체의 계정 파일과 맞춥니다.
- **상대 시각 낱말은 분석 PC 를 기준으로 풀립니다.** `ausearch -ts` 의 `boot`·`today`·`recent` 같은 낱말은 실행하는 순간과 그 기계의 마지막 부팅을 기준으로 하고, 날짜 형식은 로캘(`date '+%x'`)을 따릅니다[3]. `journalctl --since` 도 `yesterday`·`today`·`now` 를 받습니다[1]. 검체에서는 절대 시각을 주고, 경계 근처 항목은 `-o short-unix` 의 epoch 값으로 한 번 더 확인합니다.
- **감사 레코드마다 담는 필드가 다릅니다.** PATH 레코드에는 호스트 이름이나 로그인 UID 가 없어서[3], 레코드 종류 하나로 거르면 계정 조건이 걸리지 않습니다. 이벤트 단위로 묶어서 SYSCALL 레코드의 필드로 거릅니다.
- **`auid` 로 찾을 때는 PAM 설정이 전제입니다.** 로그인 UID 로 정확히 찾으려면 PAM 을 쓰는 로그인 프로그램마다 세션 단계에 `pam_loginuid` 가 `required` 로 걸려 있어야 합니다[3].
- **로그끼리 잇는 근거는 대개 시각뿐입니다.** 보통의 로그에는 어느 사건이 어느 사건을 일으켰는지가 빠져 있고, 여러 로그를 잇는 일은 시각에 기댄 느슨한 연결이라서 NTP 같은 시계 동기화에 크게 좌우된다는 연구가 있습니다[9]. 이 연구는 인과 정보를 따로 남기는 새 기록 방식을 제안하고 Nginx 와 eBPF 로 만든 시제품으로 시험한 것이라서, 지금 배포판의 로그에 들어 있는 기능은 아닙니다[9]. 세션 번호·PID 처럼 기록 안에 있는 연결 고리를 먼저 쓰고, 시각만으로 이은 부분은 보고서에서 따로 밝힙니다.

## 결과를 어떻게 해석하나

한 줄이 증명하는 것은 "그 시각에 그 태그나 프로세스가 이 문구를 로그 체계에 보냈고 그것이 저장되었다" 까지입니다. 저널에서 이름이 밑줄로 시작하는 필드는 journald 가 스스로 붙이는 값이라 보낸 프로그램이 바꿀 수 없으므로[2], 누가 보냈는지는 `SYSLOG_IDENTIFIER` 가 아니라 `_PID`·`_UID`·`_EXE` 로 판단합니다. `__REALTIME_TIMESTAMP` 는 journald 가 항목을 받은 시각이고 `_SOURCE_REALTIME_TIMESTAMP` 는 받은 시각과 다를 때만 붙는 가장 이른 신뢰 시각이라서[2], 원격으로 모은 저널처럼 받은 곳과 생긴 곳이 다른 기록은 두 값을 함께 봅니다.

기록이 없다는 결과는 사건이 없었다는 뜻이 아닙니다. 감사 로그는 규칙을 걸지 않은 시스템 콜을 적지 않고, 저널과 rsyslog 는 속도 제한을 넘은 메시지를 버리며, 순환으로 오래된 파일이 사라집니다. 이 조건은 [감사 로그 형식](../../01-foundations/logging/auditd-format.md), [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md), [로그 순환](../../01-foundations/logging/logrotate.md) 에서 확인합니다. 절차 2단계에서 잰 기간 밖의 일은 "기록이 없다" 가 아니라 "그 기간의 기록이 남아 있지 않다" 로 씁니다.

탐지 규칙이나 도구의 알림에 걸렸다는 것도 악의를 증명하지 않습니다. 예를 들어 Sigma 의 `lnx_auditd_susp_histfile_operations` 는 auditd `EXECVE` 레코드에 `.bash_history`·`.zsh_history` 같은 문자열이 들어 있으면 걸리고, 오탐 원인으로 정상 관리 작업과 기록 파일을 정리하는 정상 프로그램을 적어 둡니다[8]. 규칙에 걸린 줄은 조사할 출발점으로 삼고, 셸 기록 쪽 해석은 [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md) 에서 이어 갑니다.

보고서 문장은 "`203.0.113.10` 에서 `alice` 계정으로 SSH 공개 키 인증에 성공했다는 sshd 기록과, 같은 시각 pam_unix 의 세션 열림 기록이 있다" 처럼 어느 로그의 어느 줄이 무엇을 말하는지만 씁니다(만든 예시). "공격자가 침입했다" 처럼 원인과 사람을 단정하는 문장은 로그만으로 쓸 수 없고, 문장 고르는 법은 [Linux 포렌식 보고서](../reporting/forensic-report.md) 에서 다룹니다. 이 절차를 SSH 침입과 사용자 특정에 적용한 흐름은 [SSH 로 들어왔나](../../04-scenarios/intrusion/ssh-intrusion.md) 와 [누가 그 명령을 실행했나](../../04-scenarios/attribution/user-attribution.md) 를 봅니다.

## 참고 문헌

1. systemd, man/journalctl.xml. https://github.com/systemd/systemd/blob/main/man/journalctl.xml
2. systemd, man/systemd.journal-fields.xml. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
3. linux-audit, audit-userspace, `ausearch(8)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/ausearch.8
4. linux-audit, audit-userspace, `aureport(8)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/aureport.8
5. fox-it dissect.target, dissect/target/plugins/os/unix/log/auth.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/auth.py
6. log2timeline plaso, plaso/parsers/text_plugins/syslog.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/syslog.py
7. Velocidex velociraptor, artifacts/definitions/Linux/Events/SSHBruteforce.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Events/SSHBruteforce.yaml
8. SigmaHQ sigma, rules/linux/auditd/execve/lnx_auditd_susp_histfile_operations.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/linux/auditd/execve/lnx_auditd_susp_histfile_operations.yml
9. Johannes Olegård, Stefan Axelsson, Yuhong Li, "When is logging sufficient? — Tracking event causality for improved forensic analysis and correlation", Forensic Science International: Digital Investigation 52 (2025) 301877 (DFRWS EU 2025). https://doi.org/10.1016/j.fsidi.2025.301877
