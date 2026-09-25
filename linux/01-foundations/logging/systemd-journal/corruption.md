---
title: "손상·삭제된 저널"
parent: "systemd 저널"
grand_parent: "기반 · 로그 체계"
nav_order: 220
---

# 손상·삭제된 저널 (Corrupted·Deleted Journals)

journald 가 손상이나 비정상 종료를 감지하면 파일을 `.journal~` 로 치우고 새 파일에 쓰며, 크기·개수 한도를 넘으면 오래된 보관 파일을 스스로 지웁니다. 이 쪽에서는 두 경우에 무엇이 남는지와 그 흔적을 어떻게 읽는지를 다룹니다.

## 이 형식을 쓰는 아티팩트

`.journal~` 파일은 내용이 보통 저널 파일과 같은 구조라서 머리·객체를 읽는 방법은 [저널 파일 구조](file-format.md) 를 따릅니다. 파일이 생기는 폴더(`/var/log/journal/MACHINE_ID/`, `/run/log/journal/MACHINE_ID/`)는 [systemd 저널](index.md) 에서 다룹니다. 수집 도구가 `.journal~` 를 함께 모으는지는 도구마다 다릅니다.

| 수집 정의 | `.journal~` | `/run/log/journal` |
|---|---|---|
| ForensicArtifacts `LinuxSystemdJournalLogs` | `/var/log/journal/*/*.journal~` 포함[13] | 없음[13] |
| UAC `journal.yaml` | `/var/log` 아래 `*.journal~` 포함[14] | `run_log.yaml` 이 따로 모음[14] |
| Velociraptor `Linux.Forensics.Journal` | 기본 glob `/{run,var}/log/journal/*/*.journal{,~}`[12] | 포함[12] |

## 구조

### .journal~ 가 생기는 조건

journald 는 활성 파일(`system.journal`, `user-UID.journal`)을 쓰기로 열다가 아래 오류 가운데 하나를 만나면 "corrupted or uncleanly shut down, renaming and replacing" 경고를 남기고, 파일 이름을 바꾼 뒤 새 파일을 만듭니다[3].

| 오류 | 뜻 |
|---|---|
| EBADMSG | 손상 |
| EADDRNOTAVAIL | 가리키는 객체 오프셋이 파일 범위 밖 |
| ENODATA | 잘린 파일 |
| EHOSTDOWN | 다른 기계의 파일(머리 `machine_id` 가 현재 기계와 다름) |
| EPROTONOSUPPORT | 호환되지 않는 기능(모르는 기능 플래그, 머리 크기가 현재 판과 다름 등) |
| EBUSY | 비정상 종료(머리 `state` 가 ONLINE) |
| ESHUTDOWN | 이미 ARCHIVED 인 파일 |
| EIO | 입출력 오류(mmap 의 SIGBUS 포함) |
| EIDRM | 지워진 파일 |

`state` 가 ONLINE 인 파일을 만나면 journald 는 "already online. Assuming unclean closing" 으로 판단하고, OFFLINE 도 ARCHIVED 도 아닌 값이면 알 수 없는 상태로 보고 같은 오류를 냅니다[2]. `state` 값의 뜻과 바뀌는 때는 [저널 파일 구조](file-format.md) 에 있습니다.

이름을 바꾸기 전에 journald 는 옛 파일을 읽기 전용으로 열어 일련번호 (seqnum) 와 그 ID 를 새 파일이 이어받게 합니다[3]. 옛 파일을 읽을 수 없으면 이어받기를 건너뜁니다[3].

### 이름 바꾸기가 파일에 하는 일

이름 바꾸기는 파일 내용을 들여다보지도 고치지도 않습니다[2]. 새 이름은 `원래이름@치운시각(16진 16자리)-무작위값(16진 16자리).journal~` 이고, 치운 시각은 이름을 바꾸는 순간의 벽시계 시각 (CLOCK_REALTIME) 입니다[2]. 그래서 `.journal~` 안의 머리와 항목은 마지막으로 쓴 모습 그대로 남고, 머리의 `state` 도 치우게 된 이유에 따라 ONLINE(비정상 종료) 이나 ARCHIVED 로 남아 있을 가능성이 있습니다.

### 자동 삭제 (vacuum)

journald 는 디스크 사용량을 줄이려고 가장 오래된 보관 파일부터 지우고[6], `journalctl --vacuum-size=`·`--vacuum-time=`·`--vacuum-files=` 도 같은 일을 합니다[8]. 두 경우 모두 활성 파일은 남기고 보관 파일만 지웁니다[7][8]. 지우는 대상은 이름이 `@…-…-….journal` 꼴인 회전 파일과 `@…-….journal~` 꼴인 치운 파일이고, 이 꼴에 맞지 않는 이름은 활성 파일로 셈하거나 아예 건드리지 않습니다[4].

지울 순서는 이름으로 정합니다. 일련번호 ID 가 같은 회전 파일끼리는 이름의 첫 항목 일련번호 순서를 따르고, 나머지는 이름에서 읽은 시각 순서를 따릅니다[4]. 이 시각은 회전 파일이면 이름의 첫 항목 시각, 치운 파일이면 이름의 치운 시각이고, 파일의 ctime·atime·mtime 이나 읽을 수 있는 만든 시각 가운데 더 이른 값이 있으면 그 값으로 바꿉니다[4]. 항목이 하나도 없거나 머리보다 작은 보관 파일은 순서와 한도에 상관없이 지웁니다[4].

기본 설정에서는 크기 한도(`SystemMaxUse=` 등)와 개수 한도(`SystemMaxFiles=`, 기본 100)가 켜져 있고, 기간 한도 `MaxRetentionSec=` 는 기본 0 이라 꺼져 있습니다[7]. `MaxFileSec=`(기본 한 달)은 삭제가 아니라 회전 주기입니다[7].

파일을 지울 때 systemd 는 `unlinkat_deallocate` 로 파일을 연 채 unlink 하고, 다른 링크가 없으면 `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE` 로 블록을 해제하며 이것이 안 되면 파일을 잘라 냅니다[5]. 내용을 무작위 값으로 덮어쓰는 동작은 `UNLINK_ERASE` 플래그가 있을 때만 하는데, vacuum 은 이 플래그 없이 부릅니다[4][5].

## 읽는 법

1. 저널 폴더의 파일 목록을 이름별로 나눕니다. 이름에 `@` 가 없는 `.journal` 은 활성 파일, `@` 와 세 칸이 있는 `.journal` 은 회전 파일, `.journal~` 는 치운 파일입니다[2][4].
2. `.journal~` 이름의 첫 16진 칸을 마이크로초 UTC 시각으로 바꿔 치운 시각을 얻습니다[2].
3. `journalctl --header --file=파일` 로 `State`, `Machine ID`, `Head realtime timestamp`, `Tail realtime timestamp` 를 봅니다[2][8]. 마지막 항목 시각은 파일이 멈춘 무렵을 가리킵니다.
4. `journalctl --verify --file=파일` 로 내부 일관성을 검사합니다[8]. 봉인 (Forward Secure Sealing) 한 파일이고 검증 키가 있으면 `--verify-key=` 로 진위까지 확인합니다[8].
5. `journalctl -D 폴더` 로 활성·회전·치운 파일을 한 흐름으로 읽습니다. journalctl 은 이름이 `.journal`·`.journal~` 로 끝나지 않는 파일을 무시하고[7], 리더는 손상 파일을 회전 파일과 끼워 한 흐름으로 보여 주고 손상된 부분은 건너뛰며 주변을 최대한 읽도록 되어 있습니다[1].

읽는 방법 전반은 [journalctl 로 읽기](journalctl.md) 에서 다룹니다.

### 직접 따라가 보기

아래 이름은 명세에 맞춰 만든 예시입니다.

```text
system@000648ce7396f600-5a5a5a5a5a5a5a5a.journal~
```

첫 칸 `000648ce7396f600` 은 1768901400000000 마이크로초, 곧 2026-01-20 09:30:00 UTC 이고, 이 시각에 journald 가 파일을 치웠다는 뜻입니다. 둘째 칸은 무작위 값이라 뜻이 없습니다[2]. 이 파일의 머리를 헥스로 열어 0x10 바이트가 `01` 이면 ONLINE 상태로 멈춘 파일이고, 이때 머리의 `tail_entry_realtime` 이 파일에 쓴 마지막 항목의 시각입니다[1]. 머리 오프셋과 헥스 예시는 [저널 파일 구조](file-format.md) 에 있습니다.

## 포렌식에서 중요한 점

### 증명하는 것

- `.journal~` 가 있으면 journald 가 그 파일을 쓰려고 열다가 손상·비정상 종료·다른 기계의 파일 같은 이상을 감지해 치웠다는 뜻입니다[3][6].
- 이름의 16진 시각은 치운 시각입니다[2].
- 머리 `state` 가 ONLINE 이면 쓰는 도중에 멈췄다가 다음에 열릴 때 치워진 파일일 가능성이 높고, 머리 `machine_id` 가 폴더 이름의 기계 ID 와 다르면 다른 기계에서 온 파일일 가능성이 있습니다[2].
- 치운 파일의 새 대체 파일은 옛 파일의 일련번호를 이어받으므로[3], 두 파일의 일련번호가 이어지면 같은 흐름의 앞뒤 조각입니다.

### 증명하지 못하는 것

- 치운 원인이 전원 차단인지, 사람이 파일을 고친 것인지는 `.journal~` 만으로 가려낼 수 없습니다. 오류 종류는 파일에 기록되지 않고, journald 의 경고 문장에 남을 뿐입니다[3].
- 보관 파일이 없다고 해서 사람이 지웠다고 볼 수 없습니다. 크기·개수 한도에 따른 자동 삭제가 기본으로 켜져 있습니다[7].
- 비정상 종료가 있었어도 `.journal~` 가 생기지 않을 수 있습니다. journald 는 동기화한 뒤 파일을 OFFLINE 으로 바꾸므로[7], 마지막 동기화 뒤 새 항목이 없던 상태에서 멈췄다면 다음 부팅 때 그 파일에 그대로 이어 쓸 가능성이 있습니다.

### 시각 해석

`.journal~` 이름의 시각은 다음에 journald 가 그 파일을 열려고 한 순간이라서, 멈춘 시각이 아니라 그 뒤의 시각입니다[2]. 멈춘 무렵은 파일 머리의 `tail_entry_realtime` 이나 마지막 항목의 시각으로 봅니다. 이름 시각과 머리 시각 모두 UTC 기준 마이크로초이고[1][2], 이름 시각은 그 순간의 시스템 시계를 그대로 쓰므로 부팅 초기에 시계가 틀려 있었다면 이름 시각도 틀릴 수 있습니다. 회전 파일 이름의 시각은 첫 항목 시각이라서 뜻이 다릅니다[2]. 16진 시각을 날짜로 바꾸는 방법은 [Linux 의 시각 값](../../value-decoding/time-values.md) 에 있습니다.

### 지운 파일

vacuum 으로 지운 파일은 블록을 해제할 뿐 덮어쓰지 않으므로[5], 해제된 영역에 `LPKSHHRH` 머리나 객체가 남아 있을 가능성이 있습니다. 이런 조각을 찾는 방법은 [지운 파일 되살리기](../../../03-techniques/analysis/file-recovery.md) 에서 다룹니다. `/run/log/journal` 은 메모리 기반 파일 시스템이라[7] 여기서 지운 파일은 디스크 이미지에 남지 않습니다.

vacuum 은 오래된 파일부터 지우므로[4][6], 같은 폴더에서 더 오래된 보관 파일은 남아 있는데 중간 시기 파일만 없다면 자동 삭제의 순서와 맞지 않습니다. 다만 항목이 없는 보관 파일은 순서와 상관없이 지워지므로[4], 빠진 파일에 항목이 있었을지도 함께 따집니다. 이때는 사람이 지웠을 가능성을 두고 셸 기록 등 다른 흔적을 찾습니다. `--vacuum-*`·`--rotate` 실행 흔적은 [셸 명령 기록](../../../02-artifacts/execution/shell-history/index.md) 에서 찾습니다. 로그를 지운 흔적을 모아 보는 흐름은 [흔적을 지웠나](../../../04-scenarios/insider/anti-forensics.md) 에서 다룹니다.

## 함정

- 동시성 규칙이 느슨해서 쓰는 중인 파일은 구조가 잠시 어긋나 보였다가 나중에 맞춰질 수 있습니다[1]. 라이브로 복사한 활성 파일이 ONLINE 이고 끝부분 연결이 덜 되어 있어도 손상으로 단정하지 않습니다.
- 일반적으로 활성·보관 파일은 읽거나 복사해도 안전하고, 끝까지 쓴 항목은 모두 읽을 수 있어야 합니다[6].
- `SyncIntervalSec=` 기본값은 5분이고, CRIT·ALERT·EMERG 는 즉시 동기화하지만 ERR 이하 메시지는 그 사이 디스크에 늦게 반영됩니다[7]. 비정상 종료 직전 몇 분의 항목은 파일에 없을 수 있습니다.
- 봉인한 파일이라도 TAG 의 HMAC 은 나중에 바뀔 수 있는 연결 오프셋 같은 필드를 빼고 계산하므로, 검증할 때 구조 일관성을 따로 봐야 합니다[1].
- 저널이 손상되면 rsyslog `imjournal` 이 같은 데이터를 되풀이해 받아 syslog 파일에 같은 줄이 대량으로 생길 수 있습니다[15]. syslog 파일의 중복 줄은 [syslog 형식과 rsyslog](../syslog-rsyslog.md) 와 함께 봅니다.

## 도구

도구마다 항목을 찾는 방식이 달라서 손상 파일에서는 결과가 크게 벌어질 수 있습니다.

| 도구 | 읽는 방식 | 손상·연결 안 된 항목 |
|---|---|---|
| journalctl (sd-journal) | 색인과 ENTRY_ARRAY | 손상 부분을 건너뛰고 주변을 최대한 읽도록 설계[1] |
| plaso `systemd_journal` | 머리 `entry_array_offset` 부터 ENTRY_ARRAY 사슬[9] | 항목 하나를 못 읽으면 경고를 내고 다음 항목으로 넘어감. ENTRY_ARRAY 사슬을 읽다 실패하면 그 파일 전체가 실패할 수 있음[9] |
| dissect.target journal 플러그인 | ENTRY_ARRAY 사슬[10] | 사슬이 UNUSED 객체를 가리키면 경고 후 멈추고, 다른 종류면 ValueError[10] |
| Velociraptor `parse_journald`(go-journalctl) | `header_size` 부터 객체를 차례로 훑어 ENTRY 를 모두 냄[11] | 색인에 연결되지 않은 ENTRY 도 낼 수 있음. 크기 0 객체를 만나면 멈춤[11] |

쓰는 도중에 끊겨 색인에 연결되지 않은 ENTRY 는 객체를 차례로 훑는 방식에서만 보입니다. go-journalctl 은 훑기 반복 조건이 `i <= arena_size` 라서[11] 파일의 마지막 `header_size` 바이트 구간을 훑지 않을 가능성이 있습니다. 같은 파일을 두 방식으로 읽어 항목 수를 비교하면 연결되지 않은 항목이 있는지 가늠할 수 있습니다.

## 참고 문헌

1. systemd, "Journal File Format" (docs/JOURNAL_FILE_FORMAT.md). https://github.com/systemd/systemd/blob/main/docs/JOURNAL_FILE_FORMAT.md
2. systemd, src/libsystemd/sd-journal/journal-file.c (`journal_file_dispose`, `journal_file_archive`, `journal_file_print_header`). https://github.com/systemd/systemd/blob/main/src/libsystemd/sd-journal/journal-file.c
3. systemd, src/shared/journal-file-util.c (`journal_file_open_reliably`). https://github.com/systemd/systemd/blob/main/src/shared/journal-file-util.c
4. systemd, src/libsystemd/sd-journal/journal-vacuum.c. https://github.com/systemd/systemd/blob/main/src/libsystemd/sd-journal/journal-vacuum.c
5. systemd, src/basic/fs-util.c (`unlinkat_deallocate`). https://github.com/systemd/systemd/blob/main/src/basic/fs-util.c
6. systemd, man/systemd-journald.service.xml. https://github.com/systemd/systemd/blob/main/man/systemd-journald.service.xml
7. systemd, man/journald.conf.xml. https://github.com/systemd/systemd/blob/main/man/journald.conf.xml
8. systemd, man/journalctl.xml. https://github.com/systemd/systemd/blob/main/man/journalctl.xml
9. log2timeline plaso, plaso/parsers/systemd_journal.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/systemd_journal.py
10. fox-it dissect.target, dissect/target/plugins/os/unix/log/journal.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/journal.py
11. Velocidex go-journalctl, parser/open.go. https://github.com/Velocidex/go-journalctl/blob/master/parser/open.go
12. Velocidex velociraptor, artifacts/definitions/Linux/Forensics/Journal.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Forensics/Journal.yaml
13. ForensicArtifacts, artifacts/data/linux.yaml. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
14. tclahr UAC, artifacts/files/logs/journal.yaml, run_log.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/logs/journal.yaml , https://github.com/tclahr/uac/blob/main/artifacts/files/logs/run_log.yaml
15. rsyslog, rsyslog-doc imjournal.rst. https://github.com/rsyslog/rsyslog-doc/blob/main/source/configuration/modules/imjournal.rst
