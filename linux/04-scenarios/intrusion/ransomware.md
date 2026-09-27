---
title: "랜섬웨어가 돌았나"
parent: "시나리오 · 침해"
nav_order: 1070
---

# 랜섬웨어가 돌았나 (Ransomware)

파일이 정말 암호화됐는지, 암호화가 언제 어디까지 번졌는지, 어느 계정과 프로세스가 실행했는지, 원본을 되살릴 수 있는지를 묻는 조사를 다룹니다. 암호화된 파일 하나와 폴더의 mtime·ctime 에서 시작해 파일 시스템 타임라인과 마운트 기록으로 범위를 잡고, 저널과 감사 로그에서 암호화 직전에 멈춘 서비스를 찾습니다. 그 시각 앞뒤의 셸 명령 기록·execve 레코드·인증 로그로 계정과 들어온 경로를 거슬러 올라간 뒤, 스냅숏·백업·ext4 저널과 메모리에서 되살릴 원본과 프로세스를 찾습니다.

## 조사 질문

파일이 정말 암호화됐는지부터 묻습니다. 그렇다면 암호화가 언제 시작해 언제 끝났는지, 어느 디렉터리와 어느 디스크·공유까지 번졌는지, 어느 계정과 프로세스가 실행했는지를 차례로 좁힙니다. 마지막 질문은 원본을 되살릴 수 있는지입니다.

이 페이지는 조사 순서와 해석만 다룹니다. 파일 시각의 구조는 [ext4](../../01-foundations/filesystem/ext4/index.md)와 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)에서, 들어온 경로는 [SSH 로 들어왔나](ssh-intrusion.md)와 [웹 서버가 뚫렸나](web-compromise.md)에서 다룹니다.

## 먼저 확인할 것

**전원을 끌지.** 시스템이 아직 켜져 있으면, 끄기 전에 메모리와 실행 중인 프로세스를 먼저 수집할지 정합니다. 암호화 프로그램이 아직 돌고 있거나 키가 메모리에 남아 있을 가능성이 있기 때문입니다. 절차는 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md)과 [메모리 수집](../../03-techniques/acquisition/memory-acquisition.md)에서 다룹니다.

**OS 와 시간대.** 파일 시각은 UTC 기준 epoch 값이라서[1] 타임라인 도구가 어느 시간대로 보여 주는지 정해야 합니다. 반면 로그는 배포판과 설정에 따라 시각 형식이 다릅니다. Ubuntu 24.04 의 rsyslog 기본 형식에는 연도와 UTC 오프셋이 있고, RHEL 의 전통 syslog 형식에는 연도와 시간대가 없으며, 저널은 UTC 로 저장합니다([인증 로그](../../02-artifacts/logins/auth-log.md), [systemd 저널](../../01-foundations/logging/systemd-journal/index.md)). 분석 대상의 시간대는 [호스트 이름과 시간대](../../02-artifacts/system-info/hostname-timezone.md)에서 확인합니다.

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| 인증 로그 파일 | `/var/log/auth.log` | `/var/log/secure` |
| 파일 로그의 시각 | 연도·UTC 오프셋 포함 | 연도·시간대 없음 |
| 패키지 기록 | [dpkg·apt](../../02-artifacts/packages/dpkg-apt.md) | [rpm·dnf](../../02-artifacts/packages/rpm-dnf.md) |

**사용자와 수집 범위.** 로그인할 수 있는 계정과 홈 디렉터리를 [계정 파일](../../01-foundations/users-auth/passwd-shadow-group.md)에서 뽑아 둡니다. 수집 범위에는 전체 파일 시스템의 시각 정보가 들어 있어야 합니다. UAC 의 `bodyfile` 수집은 `/` 아래 모든 파일의 stat 정보를 모으고 proc 파일 시스템만 뺍니다[5]. 마운트된 네트워크 공유나 다른 디스크, 가상 머신 디스크 파일, 스냅숏이 있는지도 이 단계에서 목록으로 만듭니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 파일 시스템 타임라인(바뀐 파일과 폴더의 mtime·ctime, 새로 생긴 파일 이름) | 암호화의 시작·끝 시각, 범위 | [타임라인 만들기](../../03-techniques/analysis/timeline.md), [ext4](../../01-foundations/filesystem/ext4/index.md) |
| 2 | 마운트 기록 | 네트워크 공유·다른 디스크까지 번졌는지 | [마운트 기록](../../02-artifacts/devices/mounts.md) |
| 3 | 저널·감사 로그의 서비스 중지, 데이터베이스 로그 | 암호화 직전에 서비스를 멈췄는지 | [systemd 저널](../../01-foundations/logging/systemd-journal/index.md), [감사 로그 형식](../../01-foundations/logging/auditd-format.md), [데이터베이스 서버 로그](../../02-artifacts/servers/database-logs.md) |
| 4 | 셸 명령 기록, 감사 로그의 execve, 프로세스 회계 | 실행한 명령과 계정 | [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md), [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md), [프로세스 회계](../../02-artifacts/execution/process-accounting.md) |
| 5 | 인증 로그, 로그인 기록, sudo·su 기록 | 들어온 경로와 root 를 얻은 경로 | [인증 로그](../../02-artifacts/logins/auth-log.md), [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md) |
| 6 | LVM·Btrfs 스냅숏, 가상 머신 디스크 | 되살릴 원본 | [LVM](../../01-foundations/disk-volume/lvm.md), [Btrfs](../../01-foundations/filesystem/btrfs.md), [가상 머신](../../02-artifacts/containers/kvm-libvirt.md) |
| 7 | 지운 파일, ext4 저널에 남은 옛 블록 | 원본의 일부 | [지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md) |
| 8 | 메모리(켜진 상태로 확보했다면) | 프로세스, 키 | [메모리 분석](../../03-techniques/analysis/memory-analysis.md) |

## 분석 흐름

1. **암호화된 파일 하나에서 시작합니다.** 파일 내용을 쓰면 그 파일의 mtime 과 ctime 이 바뀝니다[1]. 그래서 제자리에서 덮어쓴 파일은 mtime·ctime 이 암호화 시각을 가리킵니다. 같은 폴더에 새로 생긴 안내문 파일이 있으면 그 파일의 시각도 적습니다.

2. **폴더의 mtime 을 봅니다.** 디렉터리 안에 파일을 만들거나 지우면 그 디렉터리의 mtime 이 바뀝니다[1]. 폴더마다 안내문 파일을 새로 만들었거나, 암호화한 사본을 새로 쓰고 원본을 지웠다면 해당 폴더들의 mtime 이 한 시간대로 몰립니다. 파일 소유자·그룹·권한만 바뀐 경우에는 mtime 이 바뀌지 않고 ctime 만 바뀝니다[1].

3. **전체 범위를 잡습니다.** bodyfile 로 만든 타임라인에서 1·2단계의 시각대에 바뀐 파일과 폴더를 모아, 가장 이른 시각과 가장 늦은 시각, 영향을 받은 경로를 정리합니다. 마운트 기록과 맞춰 네트워크 공유나 다른 디스크에서도 같은 시각대에 바뀐 파일이 있는지 봅니다.

4. **암호화 직전에 멈춘 서비스를 봅니다.** systemd 는 서비스 단위가 시작을 마치면 `AUDIT_SERVICE_START`, 멈추면 `AUDIT_SERVICE_STOP` 감사 레코드를 보냅니다[6]. 메시지 번호는 각각 1130, 1131 입니다[7]. 멈출 때 단위가 정상적으로 비활성 상태가 되면 성공으로, 실패 상태로 끝나면 실패로 기록합니다[6]. 데이터베이스나 가상 머신 서비스를 암호화 직전에 멈췄다면 감사 로그와 저널 양쪽에 그 시각이 남을 수 있습니다. 단위가 멈출 때 systemd 는 쓴 자원을 적은 `Consumed … CPU time` 줄도 남기는데, CPU 시간이 1초를 넘는 등 쓴 자원이 기준을 넘을 때만 info 수준 이상으로 기록하고 그보다 적으면 디버그 수준으로 기록합니다[6]. 감사 기능이 꺼져 있으면 감사 쪽에는 남지 않습니다. 데이터베이스 서버 자체의 종료 기록은 [데이터베이스 서버 로그](../../02-artifacts/servers/database-logs.md)에서 확인합니다.

5. **실행한 명령과 계정을 찾습니다.** 3·4단계의 시각 앞뒤로 셸 명령 기록, 감사 로그의 execve 레코드, 프로세스 회계, sudo·su 줄을 시각순으로 붙입니다. 암호화 프로그램 파일을 찾았다면 해시를 구해 알려진 파일과 대조합니다([알려진 파일 대조와 YARA](../../03-techniques/analysis/hash-yara.md)).

6. **들어온 경로로 거슬러 올라갑니다.** 5단계에서 찾은 계정이 언제 어디서 로그인했는지 [SSH 로 들어왔나](ssh-intrusion.md), [웹 서버가 뚫렸나](web-compromise.md), [권한을 올렸나](privilege-escalation.md)의 순서로 따라갑니다. 공격자가 남겨 둔 서비스·cron 은 [무엇이 계속 살아남게 했나](persistence-hunt.md)에서 찾습니다.

7. **불변 속성이 붙은 파일을 봅니다.** `chattr +i` 가 붙은 파일은 지우거나 이름을 바꾸거나 쓰기로 열 수 없고, 이 속성은 root 나 `CAP_LINUX_IMMUTABLE` 권한이 있는 프로세스만 붙이거나 뗄 수 있습니다[3]. `+a` 가 붙은 파일은 덧붙이기로만 쓸 수 있습니다[3]. 그래서 암호화에서 빠진 파일이 있으면 이 속성이 이유일 가능성이 있고, 반대로 공격자가 자기 파일을 지키려고 붙였을 수도 있습니다. Velociraptor `Linux.Forensics.ImmutableFiles` 는 ext4 플래그에 `IMMUTABLE` 이 있는 파일을 찾고, 기본 검색 범위는 `/home/*` 입니다[4]. 속성의 구조는 [권한·확장 속성](../../01-foundations/filesystem/permissions-xattr.md)에서 다룹니다.

8. **원본을 되살릴 수 있는지 봅니다.** 스냅숏, 백업, 가상 머신 디스크의 옛 사본을 먼저 찾습니다. ext4 에서 지운 원본은 메타데이터로 되살리기 어렵습니다. debugfs 의 `lsdel` 은 ext3·ext4 에서 지운 파일에는 쓸모가 없는데, 아이노드를 풀 때 데이터 블록 정보가 사라지기 때문입니다[2]. 이때는 debugfs 로 ext4 저널(아이노드 8)을 따로 덤프한 뒤 ext4magic 에 그 저널을 넘겨 지운 파일을 되살리는 방법이 있습니다[9]. 카빙까지 포함한 절차는 [지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md)에서 다룹니다.

9. **메모리가 있으면 프로세스를 봅니다.** 켜진 상태로 메모리를 확보했다면 암호화 프로세스와 그 부모, 네트워크 연결을 [메모리 분석](../../03-techniques/analysis/memory-analysis.md)의 방법으로 봅니다. 한 연구에서는 오픈소스 Linux 랜섬웨어 3종(RAASNet, Ransom0, Ransomware-POC)을 무작위 내용 32 KB 파일 100개가 든 디렉터리에 돌려 시스템 콜을 추적했습니다[8]. 이 시험 조건에서 상위 10개 시스템 콜에는 파일 시스템 관련 시스템 콜이 나왔고, 디렉터리를 재귀로 돌며 파일을 읽은 뒤 암호화한 내용으로 덮어쓰는 동작과 맞았습니다[8]. RAASNet 과 Ransom0 은 실행 끝 무렵 네트워크·시간·동기화 시스템 콜을 썼는데, 피해자 정보와 키를 서버로 보내는 단계였습니다[8]. 실험 환경은 Ubuntu 20.04.3 LTS 게스트였고, 이 도구는 시스템 콜의 인수를 추적하지 않아 어떤 파일을 건드렸는지는 이 방법만으로 나오지 않습니다[8].

## 흔한 오판

- **"파일 mtime 이 한 시각대로 몰렸으니 그때 암호화했다."** mtime 은 `utime(2)` 같은 호출로 바꿀 수 있습니다[1]. ctime, 폴더 mtime, 로그의 시각과 함께 맞춰 봅니다. 시각 조작을 가려내는 방법은 [시각을 조작했나](../insider/time-manipulation.md)에서 다룹니다.
- **"mtime 이 그대로니 암호화되지 않았다."** 소유자·권한 변경은 ctime 만 바꿉니다[1]. 암호화 여부는 시각이 아니라 파일 내용으로 판단합니다.
- **"지운 원본은 debugfs `lsdel` 로 찾으면 된다."** ext4 에서는 지운 아이노드의 데이터 블록 정보가 남지 않아 쓸모가 없습니다[2]. 저널 잔재, 스냅숏, 백업을 봅니다.
- **"확장자와 안내문 이름을 보면 어느 계열인지 안다."** 파일 이름은 누구나 붙일 수 있습니다. 계열은 실행 파일의 해시와 내용으로 판단합니다.
- **"감사 로그에 서비스 중지가 없으니 서비스를 멈추지 않았다."** 감사 기능이 꺼져 있으면 감사 레코드는 남지 않습니다. 저널에서 같은 단위가 멈춘 줄을 따로 찾습니다.
- **"프로세스를 실행한 계정이 범인이다."** 기록은 계정을 보여 줄 뿐입니다. 계정과 사람을 잇는 방법은 [누가 그 명령을 실행했나](../attribution/user-attribution.md)에서 다룹니다.

## 보고서 문장 예

아래 값은 모두 만든 예시입니다.

- "`/srv/data` 아래 파일 4,210개의 mtime·ctime 이 2026-03-12 15:10:02 부터 15:48:37(+09:00) 사이에 있고, 같은 시각대에 이 경로의 폴더 212개의 mtime 이 바뀌었습니다. 이 파일들의 내용은 원래 형식의 머리 부분과 맞지 않습니다."
- "같은 날 15:08:44(+09:00)에 `postgresql.service` 가 멈춘 기록이 저널과 감사 로그(서비스 중지 레코드)에 있습니다."
- "이 기록은 해당 시각대에 파일이 바뀌고 서비스가 멈췄음을 보여 줄 뿐, 실행한 사람을 특정하지 않습니다."

## 함께 볼 페이지

- [타임라인 만들기](../../03-techniques/analysis/timeline.md) — bodyfile 로 타임라인을 만드는 법
- [지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md) — 저널 잔재와 카빙
- [SSH 로 들어왔나](ssh-intrusion.md) — 들어온 경로
- [권한을 올렸나](privilege-escalation.md) — root 를 얻은 경로
- [무엇이 계속 살아남게 했나](persistence-hunt.md) — 남겨 둔 서비스·cron
- [흔적을 지웠나](../insider/anti-forensics.md) — 로그를 지운 흔적
- [Linux 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) — 보고서 쓰는 법

## 참고 문헌

1. Linux man-pages, man7/inode.7 (mtime, ctime). https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
2. e2fsprogs, debugfs/debugfs.8.in (`list_deleted_inodes`, `lsdel`). https://github.com/tytso/e2fsprogs/blob/master/debugfs/debugfs.8.in
3. e2fsprogs, misc/chattr.1.in (ATTRIBUTES `a`, `i`). https://github.com/tytso/e2fsprogs/blob/master/misc/chattr.1.in
4. Velocidex velociraptor, artifacts/definitions/Linux/Forensics/ImmutableFiles.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Forensics/ImmutableFiles.yaml
5. tclahr uac, artifacts/bodyfile/bodyfile.yaml. https://github.com/tclahr/uac/blob/main/artifacts/bodyfile/bodyfile.yaml
6. systemd, src/core/service.c (`audit_start_message_type`, `audit_stop_message_type`) · src/core/unit.c (`unit_emit_audit_start`, `unit_emit_audit_stop`, `unit_log_resources`). https://github.com/systemd/systemd/blob/main/src/core/service.c , https://github.com/systemd/systemd/blob/main/src/core/unit.c
7. linux-audit, audit-documentation specs/messages/message-dictionary.csv. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
8. Thanh Nguyen, Meni Orenbach, Ahmad Atamli, "Live System Call Trace Reconstruction on Linux", Forensic Science International: Digital Investigation 42 (2022) 301398. https://doi.org/10.1016/j.fsidi.2022.301398
9. Ali Hadi, Mariam Khader, Thomas Claflin, "Learning Linux Forensic Analysis and Why it Matters", DFRWS 발표. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
