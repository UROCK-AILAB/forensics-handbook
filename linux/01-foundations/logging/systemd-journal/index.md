---
title: "systemd 저널"
parent: "기반 · 로그 체계"
nav_order: 190
has_children: true
has_toc: false
---

# systemd 저널 (systemd Journal)

systemd-journald 가 커널·서비스·syslog 메시지를 모아 이진 파일로 저장하는 로그 체계이고, 메시지마다 보낸 프로세스의 PID·UID·실행 파일 같은 정보를 journald 가 직접 붙여 둡니다.

## 왜 중요한가

systemd 를 쓰는 배포판에서는 journald 가 로그를 가장 먼저 받습니다. 커널 메시지 (kmsg), `syslog(3)` 호출, 저널 고유 API, 서비스의 표준 출력·표준 오류, 커널 감사 (audit) 레코드가 모두 journald 로 들어옵니다[1]. 그래서 `/var/log/syslog`·`/var/log/messages` 같은 텍스트 로그가 없거나 지워진 시스템에서도 같은 사건이 저널에 남아 있을 수 있습니다. 반대로 `Storage=none` 이면 저널에는 아무것도 저장하지 않고 syslog 소켓 같은 다른 곳으로 넘기기만 하므로, 기록이 텍스트 로그에만 남습니다[2]. journald 가 syslog 데몬으로 넘기는 방식은 [syslog 형식과 rsyslog](../syslog-rsyslog.md) 에서 다룹니다.

텍스트 로그와 달리 저널에는 신뢰 필드 (trusted field) 가 있습니다. 이름이 밑줄로 시작하는 필드(`_PID`, `_UID`, `_EXE`, `_SYSTEMD_UNIT` 등)는 journald 가 스스로 붙이고 메시지를 보낸 프로그램이 바꿀 수 없습니다[3]. 반면 밑줄이 없는 필드(`MESSAGE`, `SYSLOG_IDENTIFIER`, `PRIORITY` 등)는 journald 가 값을 검사하지 않으므로, 보낸 쪽이 적은 그대로입니다[3]. 서비스의 표준 출력으로 들어온 기록은 `_PID`·`_UID`·`_GID` 가 그 줄을 쓴 자식 프로세스가 아니라 journald 에 처음 연결한 부모 프로세스의 값입니다[3]. 필드가 어느 경로로 들어왔는지는 `_TRANSPORT` 값(audit, driver, syslog, journal, stdout, kernel)으로 구분합니다[3].

저장 위치는 설정에 따라 디스크와 메모리 중 하나가 됩니다. `Storage=` 가 `volatile` 이면 `/run/log/journal` 아래에만 쓰고 재부팅하면 사라지며, `auto` 는 `/var/log/journal` 폴더가 있으면 디스크에, 없으면 메모리에 씁니다[2]. 기본값은 빌드할 때 정해지므로[2] 시스템마다 폴더와 설정 파일을 직접 봐야 합니다. 디스크에 쓰는 시스템도 부팅 초기에는 `/run` 에 쓰다가, systemd-journal-flush.service 가 `journalctl --flush` 로 `/var` 로 옮깁니다[1][2].

## 한눈에 보기

| 위치 | 생기는 조건 | 알려 주는 것 |
|---|---|---|
| `/var/log/journal/MACHINE_ID/system.journal` | 디스크 저장 | 시스템·커널·서비스 로그와 신뢰 필드[1][3][11] |
| `/var/log/journal/MACHINE_ID/system@….journal` | 회전한 보관 파일 | 같은 내용의 과거분. 이름에 첫 항목 시각이 들어 있음([저널 파일 구조](file-format.md)) |
| `/var/log/journal/MACHINE_ID/user-UID.journal` | 디스크 저장이고 `SplitMode=uid`(기본) | 시스템 계정 범위 밖 UID 사용자의 로그[1][2][11] |
| `/run/log/journal/MACHINE_ID/` | 메모리 저장이거나 `/var` 로 옮기기 전 | 켜져 있는 시스템에서만 확보됨[1][2] |
| `….journal~` | 비정상 종료·손상을 journald 가 감지 | 이름을 바꿔 떼어 둔 파일. 그때까지 쓴 내용이 남음([손상·삭제된 저널](corruption.md))[1] |
| `/var/log/journal/MACHINE_ID.NAMESPACE/` | 저널 네임스페이스 (namespace) 사용 | 따로 떨어진 서비스 묶음의 로그[1] |
| `/etc/systemd/journald.conf` 와 `journald.conf.d/*.conf` | 설정 | 저장 방식·보존 한도·전달 설정[2] |

폴더 이름 `MACHINE_ID` 는 그 시스템의 기계 ID 입니다[1]. 설정은 `/etc/systemd/journald.conf` 말고도 `/run/systemd/`, `/usr/local/lib/systemd/`, `/usr/lib/systemd/` 아래의 `journald.conf` 와 각 `journald.conf.d/*.conf` 드롭인에서 읽고, 네임스페이스마다 `journald@NAMESPACE.conf` 를 따로 씁니다[2]. 파일은 기본으로 `systemd-journal` 그룹이 읽을 수 있고, `adm`·`wheel` 그룹 구성원도 모든 저널 파일을 읽을 수 있습니다[1][4]. 사용자별 파일은 그 사용자가 소유하지 않고, ACL 로 읽기만 허용합니다[1].

### 배포판별 기준 값

| 항목 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|
| systemd 판 | 255.4(패키지 `255.4-1ubuntu8.17`)[6] | 252[5] |
| 기본 `Storage=` | 빌드 값이라 분석 대상의 `/var/log/journal` 유무와 설정 파일로 확인 | 설정 파일 주석 `#Storage=auto`[5] → `/var/log/journal` 이 있으면 디스크 저장 |
| 배포판이 바꾼 설정 | 분석 대상의 `/etc/systemd/journald.conf`·드롭인으로 확인 | `journald.conf` 에 주석이 아닌 `Audit=` 줄이 들어 있음[5] |

### 보존 한도 기본값

journald 는 크기·개수·기간 한도에 맞춰 오래된 보관 파일을 스스로 지웁니다[2]. 사라진 보관 파일이 사람의 삭제 흔적인지 판단하기 전에 아래 한도부터 봅니다.

| 설정 | 기본값 | 뜻 |
|---|---|---|
| `SystemMaxUse=` / `RuntimeMaxUse=` | 파일 시스템의 10%, 최대 4G | 저널 전체가 쓸 공간[2] |
| `SystemKeepFree=` / `RuntimeKeepFree=` | 파일 시스템의 15%, 최대 4G | 남겨 둘 여유 공간[2] |
| `SystemMaxFileSize=` | `MaxUse` 의 8분의 1, 최대 128M | 파일 하나 크기. 보통 보관 파일 7개가 남음[2] |
| `SystemMaxFiles=` | 100 | 보관 파일 개수[2] |
| `MaxFileSec=` | 1달 | 한 파일에 쓰는 기간[2] |
| `MaxRetentionSec=` | 0(끔) | 보존 기간[2] |
| `SyncIntervalSec=` | 5분 | 디스크 동기화 간격. CRIT·ALERT·EMERG 는 즉시[2] |
| `RateLimitIntervalSec=` / `RateLimitBurst=` | 30초에 10000건 | 서비스별 초과분은 버리고 버린 개수를 메시지로 남김[2] |

한도를 맞출 때 지우는 대상은 보관 파일뿐이고, 쓰고 있는 파일은 남깁니다[2].

### 도구가 모으는 범위

| 도구 | 모으는 경로 |
|---|---|
| ForensicArtifacts `LinuxSystemdJournalLogs` | `/var/log/journal/*/*.journal`, `/var/log/journal/*/*.journal~` (설정은 `/etc/systemd/journald.conf` 하나)[7] |
| UAC | `/var/log` 아래 `*.journal`·`*.journal~`, `/run/log` 전체, 라이브 명령 `journalctl --list-boots`[8] |
| Velociraptor `Linux.Forensics.Journal` | `/{run,var}/log/journal/*/*.journal{,~}`[9] |
| dissect.target `journal` | `/var/log/journal` 만[10] |

ForensicArtifacts 와 dissect.target 은 `/run/log/journal` 을 보지 않습니다[7][10]. 메모리에만 저널을 쓰는 시스템은 전원을 끄기 전에 [라이브 응답 수집](../../../03-techniques/acquisition/live-response.md) 으로 `/run/log/journal` 을 따로 확보해야 합니다. ForensicArtifacts 는 드롭인 폴더(`journald.conf.d`)를 모으지 않으므로 설정 판단에 쓰려면 함께 챙깁니다.

## 읽는 순서

1. [저널 파일 구조 (Journal File Format)](file-format.md) — 파일 머리·객체·해시 표 오프셋, 보관 파일 이름 규칙, 헥스로 항목 하나 따라가기
2. [journalctl 로 읽기 (journalctl)](journalctl.md) — 떼어 낸 폴더·이미지를 여는 옵션, 거르기·출력 형식, 시각을 UTC 로 보는 법
3. [손상·삭제된 저널 (Corrupted·Deleted Journals)](corruption.md) — `.journal~` 가 생기는 조건, 자동 삭제 방식, 도구마다 다른 복구 결과

## 함께 볼 페이지

- [syslog 형식과 rsyslog](../syslog-rsyslog.md) — journald 가 넘긴 메시지가 텍스트 로그에 남는 모양
- [감사 로그 형식 (auditd)](../auditd-format.md) — journald 도 `_TRANSPORT=audit` 로 감사 레코드를 모음
- [로그 순환 (logrotate)](../logrotate.md) — 텍스트 로그의 회전. 저널은 journald 가 직접 회전함
- [Linux 의 시각 값](../../value-decoding/time-values.md) — 저널의 마이크로초 epoch 시각
- [부팅과 종료 기록](../../../02-artifacts/system-info/boot-shutdown.md) — 부팅 ID 로 나눈 저널 기록 활용
- [커널 로그 (dmesg·kern.log)](../../../02-artifacts/system-info/kernel-log.md)
- [인증 로그 (auth.log·secure)](../../../02-artifacts/logins/auth-log.md)
- [로그 분석](../../../03-techniques/analysis/log-analysis.md), [타임라인 만들기](../../../03-techniques/analysis/timeline.md)
- [흔적을 지웠나](../../../04-scenarios/insider/anti-forensics.md) — 저널 삭제·회전 흔적 해석

## 참고 문헌

1. systemd, man/systemd-journald.service.xml. https://github.com/systemd/systemd/blob/main/man/systemd-journald.service.xml
2. systemd, man/journald.conf.xml. https://github.com/systemd/systemd/blob/main/man/journald.conf.xml
3. systemd, man/systemd.journal-fields.xml. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
4. systemd, man/journalctl.xml. https://github.com/systemd/systemd/blob/main/man/journalctl.xml
5. Red Hat, systemd-rhel9 source-git (meson.build `version : '252'`, src/journal/journald.conf). https://github.com/redhat-plumbers/systemd-rhel9
6. Ubuntu, systemd 패키지 debian/changelog (ubuntu-noble). https://git.launchpad.net/~ubuntu-core-dev/ubuntu/+source/systemd/plain/debian/changelog?h=ubuntu-noble
7. ForensicArtifacts, artifacts/data/linux.yaml. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
8. tclahr UAC, artifacts/files/logs/journal.yaml, artifacts/files/logs/run_log.yaml, artifacts/live_response/system/journalctl.yaml. https://github.com/tclahr/uac/tree/main/artifacts
9. Velocidex velociraptor, artifacts/definitions/Linux/Forensics/Journal.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Forensics/Journal.yaml
10. fox-it dissect.target, dissect/target/plugins/os/unix/log/journal.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/journal.py
11. systemd, src/journal/journald-manager.c. https://github.com/systemd/systemd/blob/main/src/journal/journald-manager.c
