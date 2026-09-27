---
title: "시각을 조작했나"
parent: "시나리오 · 유출·은폐"
nav_order: 1110
---

# 시각을 조작했나 (Time Manipulation)

파일이나 기록의 시각이 실제로 일이 일어난 때와 다르게 찍혀 있는지, 다르다면 누가 어떤 방법으로 바꿨는지 묻는 조사를 다룹니다. 시간대·RTC 설정과 수집 순간의 시계 오차를 먼저 적고, 저널의 시각 변경·동기화 줄, 저널 머리의 seqnum·monotonic, 감사 로그, wtmp 로 시스템 시계를 바꾼 구간부터 찾습니다. 그 구간이 없는데 특정 파일이 의심되면 그 파일의 atime·mtime·ctime·생성 시각을 서로 비교하고, ext4 저널과 아이노드 체크섬, 같은 때의 셸 기록으로 좁힙니다.

## 조사 질문

어떤 파일이나 기록의 시각이 실제로 일이 일어난 때와 다르게 찍혀 있는지, 다르다면 누가 어떤 방법으로 바꿨는지를 묻습니다. 방법은 크게 둘로 나뉩니다. 하나는 **파일 시각만** 바꾼 경우(`touch`, `utimensat` 호출, 시각을 보존하는 복사)이고, 다른 하나는 **시스템 시계**를 바꾼 경우(`date`, `timedatectl`, NTP 보정)입니다. 파일 시각만 바꾸면 그 파일 하나의 값이 틀어지고, 시스템 시계를 바꾸면 그 사이에 찍힌 로그·파일 시각이 모두 같은 만큼 틀어집니다.

이 페이지는 조사 순서와 해석만 다룹니다. 시각 값의 저장 형식은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)과 [ext4 시각](../../01-foundations/filesystem/ext4/timestamps.md)에서, 저널의 필드 검색은 [journalctl](../../01-foundations/logging/systemd-journal/journalctl.md)에서 다룹니다. 로그 파일 자체를 지우거나 고친 흔적은 [흔적을 지웠나](anti-forensics.md)에서 다룹니다.

## 먼저 확인할 것

**시간대와 RTC 설정.** 하드웨어 시계 (RTC) 가 UTC 인지 현지 시각인지는 `/etc/adjtime` 셋째 줄의 `UTC` 또는 `LOCAL` 로 정하고, 이 파일이 없으면 UTC 로 봅니다[24]. `timedatectl set-local-rtc 1` 은 RTC 를 현지 시각으로 두는 설정입니다. 이 방식은 완전히 지원되지 않고, 시간대를 바꾸거나 일광 절약 시간을 조정할 때 여러 문제를 일으킵니다[18]. 시간대 파일 `/etc/localtime` 과 함께 [호스트 이름·시간대](../../02-artifacts/system-info/hostname-timezone.md)에서 확인합니다.

**시각 동기화 프로그램.** 어떤 프로그램이 시계를 맞추는지에 따라 남는 줄이 다릅니다.

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| systemd-timesyncd | systemd 패키징이 `systemd-timesyncd` 를 따로 설치하는 패키지로 만듭니다[25] | systemd 252 를 `-Dtimesyncd=false` 로 빌드해 timesyncd 가 없습니다[25] |
| 쓰이는 동기화 프로그램 | 분석 대상의 설치 패키지로 확인 | chrony 등 분석 대상의 설치 패키지로 확인 |
| 시계 하한 파일 | `/var/lib/systemd/timesync/clock` 의 수정 시각[14][15] | 해당 없음(timesyncd 없음) |

**수집 순간의 시계 오차.** 라이브 수집이면 `date`, `hwclock`, `timedatectl status` 결과를 가장 먼저 남깁니다. UAC 는 세 가지를 모두 라이브 응답 항목으로 모읍니다[26]. 수집 순간에 시스템 시계가 실제 시각과 얼마나 달랐는지가 이후 모든 판단의 기준점이 됩니다. 디스크 이미지만 있으면 마지막 저널 항목과 마지막 동기화 줄로 시계 상태를 추정합니다([라이브 응답 수집](../../03-techniques/acquisition/live-response.md)).

**사용자와 수집 범위.** 저널 파일 전체(회전된 파일 포함), 감사 로그, wtmp, 셸 명령 기록이 수집 범위에 있어야 합니다. 시계를 바꾼 사람은 시각 변경 줄에 남지 않아서, 같은 시각 근처의 셸 기록·sudo 기록으로 좁혀야 하기 때문입니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 시간대·RTC 설정 | 현지 시각과 UTC 중 어느 쪽으로 읽을지 | [호스트 이름·시간대](../../02-artifacts/system-info/hostname-timezone.md) |
| 2 | 저널의 시각 변경·동기화 줄 | 언제 시계·시간대를 바꿨나 | [journalctl](../../01-foundations/logging/systemd-journal/journalctl.md) |
| 3 | 저널 머리·seqnum·monotonic | 시스템 시계가 뒤로 간 구간 | [저널 파일 형식](../../01-foundations/logging/systemd-journal/file-format.md) |
| 4 | 감사 로그 | `time-change` 키 기록, 일련번호에 견준 시각 역행 | [감사 로그 형식](../../01-foundations/logging/auditd-format.md) |
| 5 | 파일 시각(atime·mtime·ctime·생성 시각) | 생성·변경 시각에 견준 접근·수정 시각 | [ext4 시각](../../01-foundations/filesystem/ext4/timestamps.md), [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) |
| 6 | ext4 저널 (jbd2) | 옛 아이노드 사본과 커밋 시각 | [ext4 저널](../../01-foundations/filesystem/ext4/journal-jbd2.md) |
| 7 | 부팅 기록 | 부팅 단위로 시계 구간 나누기 | [부팅과 종료 기록](../../02-artifacts/system-info/boot-shutdown.md) |
| 8 | 설치 날짜 | 설치 파일들의 시각 순서와 비교 | [설치 날짜 가늠하기](../../02-artifacts/system-info/install-date.md) |
| 9 | 타임라인 | 조작 구간 표시 | [타임라인 만들기](../../03-techniques/analysis/timeline.md) |

## 분석 흐름

### 시스템 시계를 바꾼 경우

시계 조작을 먼저 찾습니다. 시계를 바꾼 구간이 있으면 그 구간의 파일 시각은 모두 틀린 시계로 찍힌 값이라서, 파일 하나하나를 따지기 전에 구간부터 표시해야 합니다.

1. 수집 순간의 시계 오차를 적어 둡니다(위 "먼저 확인할 것").
2. 저널에서 아래 표의 줄을 MESSAGE_ID 와 문구로 뽑아 시간순으로 정렬합니다.

| 무엇을 했나 | 저널에 남는 줄 | 근거 |
|---|---|---|
| `timedatectl set-time` (timedated 를 거침) | `Changed local time to …` (INFO), MESSAGE_ID `c7a787079b354eaaa9e77b371893cd27`, 필드 `REALTIME=`(마이크로초) | [9][13] |
| 자동 동기화가 켜진 상태에서 set-time | 요청이 `Automatic time synchronization is enabled` 오류로 거부됩니다 | [9] |
| `timedatectl set-timezone` | `Changed time zone to '…' (…).`, MESSAGE_ID `45f82f4aef7a4bbf942ce861d1f20990`, 필드 `TIMEZONE=`, `TIMEZONE_SHORTNAME=`, `DAYLIGHT=` | [9][13] |
| PID 1 이 시계 변경을 알아챔 | `Time has been changed` (MESSAGE_ID `c7a78707…`), 두 판 모두 LOG_DEBUG | [10] |
| 시계가 뒤로 간 뒤 journald 가 기록 | `Time jumped backwards, rotating.` 뒤에 파일 회전과 정리 | [11][12] |
| 시스템 시계가 쓰던 저널 파일의 마지막 항목보다 이를 때 (upstream) | `…: Realtime clock jumped backwards relative to last journal entry, rotating.` | [11] |
| 쓰던 저널 파일이 미래 시각 (RHEL 9) | `…: Journal file is from the future, rotating.` (warning) | [12] |
| timesyncd 첫 동기화 | `Initial clock synchronization to ….`, MESSAGE_ID `7c8a41f37b764941a0e1780b1be2f037`, 필드 `MONOTONIC_USEC=`, `REALTIME_USEC=`, `BOOTTIME_USEC=` | [13][14] |
| timesyncd 가 시작할 때 시계를 앞으로 당김 | `System clock time advanced to recorded timestamp: …` 또는 `… built-in epoch: …`, MESSAGE_ID `7db73c8af0d94eeb822ae04323fe6ab6`, 필드 `DIRECTION=forwards` | [13][14] |
| chrony 가 큰 차이를 보정 | `System clock wrong by … seconds`, `System clock was stepped by … seconds` (warning) | [19] |

3. `journalctl --header` 로 저널 파일마다 머리의 첫·마지막 항목 시각과 seqnum 을 보고, 회전된 파일 이름과 맞춰 봅니다. 저널 항목은 seqnum 순서로 쓰이고, 같은 부팅 안에서는 monotonic 시각도 늘어나며, realtime 은 시계 보정에 따른 점프를 빼면 늘어납니다[16]. `--header` 는 잘못된 시각으로 부팅해 항목 순서가 어긋난 경우를 찾는 데 쓸모가 있습니다[17]. **seqnum 과 monotonic 은 늘어나는데 realtime 만 되돌아간 지점**이 시계 조작 후보입니다.
4. 감사 로그를 봅니다. 감사 규칙에 시각 변경 호출이 들어 있으면 `key=time-change` 레코드가 남습니다. 규칙 예시 파일은 `adjtimex`·`settimeofday` 호출, 첫 인자가 0(`CLOCK_REALTIME`)인 `clock_settime` 호출, `/etc/localtime` 쓰기를 모두 이 키로 묶습니다[20]. 커널이 시간을 보정하면 `TIME_INJOFFSET`(1332, 시간 오프셋 주입)과 `TIME_ADJNTPVAL`(1333, NTP 값 조정) 레코드가 남을 수 있습니다[21]. 규칙이 없어도 `audit(초.밀리초:일련번호)` 의 구조로 역행을 찾을 수 있습니다. 시각은 그 순간의 시스템 시계 값이고, 일련번호는 부팅 뒤 1 씩 오르는 카운터입니다[22]. 일련번호는 오르는데 시각이 뒤로 간 지점을 찾습니다. 재부팅하면 일련번호가 다시 작아지므로 부팅 단위로 나눠 봅니다.
5. wtmp 에 터미널 이름 `|` 와 `}` 로 된 레코드 쌍(ut_type `OLD_TIME` 4, `NEW_TIME` 3)이 있으면 시계를 바꾸기 전과 뒤의 시각입니다[23]. 레코드 형식은 [로그인 기록](../../02-artifacts/logins/wtmp-btmp-lastlog.md)에서 다룹니다.
6. timesyncd 를 쓰는 시스템(Ubuntu 등)에서는 `/var/lib/systemd/timesync/clock` 의 수정 시각을 봅니다. 이 파일은 NTP 동기화에 성공할 때마다, 또는 `SaveIntervalSec=` 간격마다 수정 시각이 갱신되고, systemd 와 timesyncd 는 이 수정 시각을 시계의 하한("epoch")으로 씁니다[15]. timesyncd 는 시작할 때 시계가 이 값보다 이르면 시계를 이 값 바로 뒤로 당깁니다[14][15]. timesyncd 는 시작할 때 이 파일을 읽은 뒤 수정 시각을 그때 시각보다 조금 뒤로 다시 쓰므로[14], 이 수정 시각은 마지막 동기화 시각이 아니라 마지막으로 timesyncd 가 시작한 시각일 수도 있습니다. 그래서 시계를 과거로 돌려 놓고 재부팅하면 위 표의 `System clock time advanced` 줄이 남을 가능성이 있습니다.
7. 찾은 구간 안에서 만들어지거나 바뀐 파일의 ctime·생성 시각을 "틀린 시계로 찍힌 값" 으로 표시하고, 역행 전후 두 줄의 차이로 보정량을 적습니다. 예를 들어 seqnum 이 이어지는 두 저널 항목이 16:00:05 와 한 달 전 09:00:00 이면, 그 뒤 값은 모두 그만큼 당겨서 읽어야 합니다(만든 예시).

### 파일 시각만 바꾼 경우

시계 조작 구간이 없는데 특정 파일의 시각이 의심되면 파일 하나의 시각 네 가지를 서로 비교합니다.

1. **ctime 과 생성 시각을 기준으로 삼습니다.** `touch` 는 접근 시각(atime)과 수정 시각(mtime)을 바꾸고, 상태 변경 시각(ctime)을 원하는 값으로 정할 수 없으며, 생성 시각(birth)은 아예 바꾸지 못합니다[1]. 커널의 시각 설정 경로는 요청과 상관없이 `ATTR_CTIME` 을 넣어 ctime 을 현재 시각으로 바꿉니다[2]. ctime 은 아이노드 정보를 설정할 때 바뀌는 값이고[3], `utimensat` 은 atime·mtime 두 값만 받습니다[4]. 그래서 mtime 을 과거로 돌리면 ctime 은 돌린 그 순간으로 찍힙니다. 생성 시각은 ext4·XFS·Btrfs 마다 필드가 다르고, statx 를 지원하는 `stat`, `debugfs`, TSK `istat` 으로 봅니다([Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)).
2. **있을 수 없는 순서를 찾습니다.** 접근·수정 시각이 생성 시각보다 앞서는 경우, 변경·수정 시각이 생성 뒤 겨우 몇 나노초인 경우를 봅니다[5]. 백업이 있으면 백업의 시각과 비교하고, 운영체제 파일이라면 같이 설치된 파일들의 시각 순서와 비교합니다[5]. Göbel 과 Baier 의 ext4 시험에서는 새로 만든 파일의 접근 시각과 생성 시각이 같았습니다[5].
3. **권한으로 사람을 좁힙니다.** 현재 시각이 아닌 값을 넣으려면 호출하는 프로세스가 파일 소유자이거나 해당 권한이 있어야 합니다[4]. 남의 파일 시각이 되돌려졌다면 root 또는 파일 소유자 계정으로 좁힐 수 있습니다.
4. **나노초 자리를 봅니다.** `touch -d` 의 시각 형식은 `yyyy-mm-ddThh:mm:ss[.frac][Z]` 로 소수 초가 선택 사항이라서[1], 소수 초를 주지 않으면 나노초가 0 인 시각이 됩니다. 나노초를 기록하는 파일 시스템에서 mtime 의 나노초만 0 이면 사람이 값을 넣었을 가능성을 보는 단서가 됩니다. 원본 형식이 초 단위였던 복사·압축 풀기에서도 0 이 되므로 단서로만 씁니다.
5. **ext4 저널을 봅니다.** jbd2 커밋 블록의 0x30 에 커밋 시각 초(`h_commit_sec`, 빅 엔디언 64비트), 0x38 에 나노초(`h_commit_nsec`, 빅 엔디언 32비트)가 있습니다[6]. 저널에 남은 옛 아이노드 블록 사본의 시각과 커밋 시각을 비교하면 "이 시점에는 다른 시각 값이었다" 를 보일 가능성이 있습니다. TSK `jls` 는 커밋 블록마다 `sec: 초.소수` 를 찍는데, 소수 부분을 `NSEC_PER_SEC / 10 * commit_nsec` 로 계산합니다[7]. 나노초 자리는 헥스로 따로 읽고, `jls` 출력은 초 단위만 씁니다. 읽는 법은 [ext4 저널](../../01-foundations/filesystem/ext4/journal-jbd2.md)에서 다룹니다.
6. **아이노드 체크섬을 봅니다.** ext4 는 아이노드마다 메타데이터 체크섬이 있어서, 아이노드의 시각 필드를 직접 고치면 체크섬이 맞지 않게 됩니다[5]. 체크섬이 틀린 아이노드는 직접 편집한 흔적일 가능성이 있습니다. 다만 체크섬을 다시 계산해 맞추면 이 흔적은 사라집니다. Göbel 과 Baier 의 시험에서는 체크섬이 틀린 아이노드가 여럿이면 `e2fsck` 가 그 항목을 지울지 물어서, 소스를 고친 `e2fsck` 로 체크섬을 다시 맞췄습니다[5]. 나노초 필드에 데이터를 숨기는 방법과 그 탐지는 [ext4 시각](../../01-foundations/filesystem/ext4/timestamps.md)에서 다룹니다.
7. 조작이 의심되는 시각과 같은 때의 셸 기록·감사 로그의 실행 기록에서 `touch`, `cp`, 압축 풀기 명령을 찾습니다([셸 명령 기록](../../02-artifacts/execution/shell-history/index.md), [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md)).

마지막으로 타임라인에 "시계 조작 구간" 과 "시각이 의심되는 파일" 을 따로 표시합니다([타임라인 만들기](../../03-techniques/analysis/timeline.md)).

## 흔한 오판

**"mtime 이 생성 시각보다 앞서면 시각 조작이다."** `cp -a`, `cp --preserve=timestamps` 는 원본의 접근·수정 시각을 복사본에 옮깁니다[1]. 그래서 복사본은 mtime 이 생성 시각보다 앞섭니다. 압축 풀기, 동기화 프로그램, sftp 의 시각 보존도 같은 모양을 만들고, sftp-server 는 로그 수준이 INFO 이상이면 `set "경로" modtime …` 줄을 남깁니다[8]([자료를 밖으로 옮겼나](data-exfiltration.md)). 이 경우 ctime 과 생성 시각은 복사한 순간 근처에 모입니다. 셸 기록이나 실행 기록에서 복사 명령을 확인하기 전에는 조작이라고 쓰지 않습니다.

**"ctime 은 바꿀 수 없으니 ctime 이 진짜 시각이다."** `touch` 나 `utimensat` 으로는 ctime 을 정할 수 없지만[1][2], 시스템 시계를 바꾼 뒤에 파일을 건드리면 ctime 도 틀린 시계로 찍힙니다. ctime 만 믿기 전에 시계 조작 구간부터 찾습니다.

**"저널 시각은 조작할 수 없다."** 저널 항목의 realtime 은 그 순간의 시스템 시계 값입니다[16]. 믿을 수 있는 것은 seqnum 과 monotonic 의 순서입니다.

**"`Time jumped backwards` 가 없으니 시계를 바꾸지 않았다."** 이 줄은 시계가 뒤로 갔을 때만 나옵니다[11]. 시계를 앞으로 돌린 경우는 나오지 않습니다. `date -s` 처럼 timedated 를 거치지 않은 변경은 `Changed local time to` 줄도 남기지 않으므로, 감사 규칙이 없으면 seqnum 에 견준 시각 역행 같은 간접 흔적으로 찾습니다.

**"`Time has been changed` 로 찾으면 된다."** PID 1 의 이 줄은 LOG_DEBUG 라서 기본 로그 수준에서는 보이지 않을 가능성이 높습니다[10]. 같은 MESSAGE_ID 를 timedated 가 INFO 로 쓰므로[9], MESSAGE_ID 로 찾으면 timedated 의 `Changed local time to` 줄이 나옵니다.

**시간대 변경을 시계 변경으로 읽음.** `Changed time zone to` 줄은 현지 시각 표시만 바꾼 기록입니다. UTC 기준 시스템 시계 값은 그대로이므로 UTC 로 저장된 기록의 순서는 바뀌지 않습니다. 반대로 연도와 시간대가 없는 전통 syslog 줄은 이 변경 전후로 해석이 달라집니다([syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)).

**`dmesg -T` 시각을 실제 시각으로 인용함.** `-T` 와 iso 형식으로 바꾼 시각은 절전·재개 뒤 부정확할 수 있습니다. 로그 시각의 기준이 절전·재개 뒤 갱신되지 않기 때문입니다[24]. 커널 로그 해석은 [커널 로그](../../02-artifacts/system-info/kernel-log.md)에서 다룹니다.

**wtmp 에 `|`·`}` 레코드가 없으니 시계를 바꾸지 않았다.** utmp 설명서는 `date` 가 시계를 바꿀 때 이 쌍을 남긴다고 적지만[23], coreutils 설명서의 `date` 시각 설정 절에는 wtmp 에 쓴다는 말이 없습니다[1]. 출처끼리 내용이 다르므로, 분석 대상에 이 레코드가 있으면 쓰고 없다고 해서 변경이 없었다고 보지 않습니다.

**판마다 다른 줄.** `Journal file is from the future, rotating.` 은 RHEL 9(systemd 252) 코드에만 있고, upstream 은 같은 상황을 `Realtime clock jumped backwards relative to last journal entry` 로 남깁니다[11][12]. `System clock time advanced` 의 MESSAGE_ID 는 RHEL 9 의 메시지 카탈로그에 없고, RHEL 9 에는 timesyncd 자체가 빌드되지 않습니다[13][25]. Ubuntu 24.04(systemd 255)에서 어느 문구가 나오는지는 실제 저널에서 확인합니다.

## 증명하는 것 / 증명하지 못하는 것

`Changed local time to …` 줄은 timedated 를 통해 시계를 그 값으로 바꾸라는 요청이 있었다는 기록입니다. 이 줄에는 요청한 사용자가 없으므로, 같은 시각 근처의 sudo 기록·셸 기록으로 좁힙니다([누가 그 명령을 실행했나](../attribution/user-attribution.md)). `Time jumped backwards` 줄은 journald 가 쓰려던 순간 시스템 시계가 앞 항목의 시각보다 이른 값이었다는 기록입니다. ctime 이 mtime 보다 한참 뒤라는 사실은 그 뒤에 아이노드 정보가 바뀌었다는 뜻이고, 원인은 시각 설정·권한 변경·이름 바꾸기 등 여럿입니다.

파일 시각 하나가 틀렸다는 것만으로는 사람이 조작했다고 증명하지 못합니다. 복사 보존, 압축 풀기, 동기화, RTC 오류, 가상 머신 스냅숏 복원도 같은 모양을 만듭니다.

## 보고서 문장 예

아래 값은 모두 만든 예시입니다.

- "저널에서 2025-03-04 16:00:05(UTC) 항목 다음 항목이 2025-02-01 09:00:00(UTC) 로 찍혀 있다. 두 항목의 seqnum 은 이어지고 같은 부팅의 monotonic 값도 늘어난다. 이 사이에 시스템 시계가 약 31일 뒤로 바뀐 것과 들어맞는다. 이 구간에 찍힌 파일 시각은 같은 만큼 보정해 읽었다."
- "파일 report.odt 의 수정 시각은 2024-01-10 이지만 생성 시각과 변경 시각(ctime)은 2025-03-04 16:12(UTC) 이다. 이 차이는 수정 시각을 나중에 설정했거나 시각을 보존하는 복사로 파일을 만든 경우에 생긴다. 같은 시각의 셸 기록에 `touch -d` 명령이 있어 앞의 경우로 판단했다."
- "2025-03-04 15:58:40(UTC) 에 timedated 가 `Changed local time to` 줄을 남겼다. 이 줄에는 요청한 계정이 없고, 같은 분의 sudo 기록에 계정 user1 이 `timedatectl` 을 실행한 기록이 있다."

## 함께 볼 페이지

- [흔적을 지웠나](anti-forensics.md) — 로그 파일을 지우거나 되돌린 흔적
- [자료를 밖으로 옮겼나](data-exfiltration.md) — sftp 의 수정 시각 보존 줄
- [타임라인 만들기](../../03-techniques/analysis/timeline.md) — 조작 구간을 표시하는 법
- [로그 분석](../../03-techniques/analysis/log-analysis.md)
- [Linux 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)
- 다른 판: [Windows 시각 값 형식](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.html), [Windows 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)

## 참고 문헌

1. GNU coreutils, doc/coreutils.texi (touch invocation, cp `--preserve`, Setting the time). https://github.com/coreutils/coreutils/blob/master/doc/coreutils.texi
2. Linux kernel, fs/utimes.c (`vfs_utimes`). https://github.com/torvalds/linux/blob/master/fs/utimes.c
3. Linux man-pages, inode.7. https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
4. Linux man-pages, utimensat.2. https://github.com/mkerrisk/man-pages/blob/master/man2/utimensat.2
5. Thomas Göbel, Harald Baier, "Anti-forensics in ext4: On secrecy and usability of timestamp-based data hiding", Digital Investigation 24 (2018) S111–S120, DFRWS 2018 Europe. https://doi.org/10.1016/j.diin.2018.01.014
6. Linux kernel, Documentation/filesystems/ext4/journal.rst (Commit Block). https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/journal.rst
7. The Sleuth Kit, tsk/fs/ext2fs_journal.cpp. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs_journal.cpp
8. OpenSSH portable, sftp-server.c. https://github.com/openssh/openssh-portable/blob/master/sftp-server.c
9. systemd, src/timedate/timedated.c; RHEL 9 source-git 같은 파일. https://github.com/systemd/systemd/blob/main/src/timedate/timedated.c , https://github.com/redhat-plumbers/systemd-rhel9/blob/main/src/timedate/timedated.c
10. systemd, src/core/manager.c; RHEL 9 source-git 같은 파일. https://github.com/systemd/systemd/blob/main/src/core/manager.c , https://github.com/redhat-plumbers/systemd-rhel9/blob/main/src/core/manager.c
11. systemd, src/journal/journald-manager.c. https://github.com/systemd/systemd/blob/main/src/journal/journald-manager.c
12. systemd RHEL 9 source-git, src/journal/journald-server.c. https://github.com/redhat-plumbers/systemd-rhel9/blob/main/src/journal/journald-server.c
13. systemd, src/systemd/sd-messages.h · catalog/systemd.catalog.in; RHEL 9 source-git catalog/systemd.catalog.in. https://github.com/systemd/systemd/blob/main/src/systemd/sd-messages.h , https://github.com/systemd/systemd/blob/main/catalog/systemd.catalog.in , https://github.com/redhat-plumbers/systemd-rhel9/blob/main/catalog/systemd.catalog.in
14. systemd, src/timesync/timesyncd.c · timesyncd-manager.c. https://github.com/systemd/systemd/tree/main/src/timesync
15. systemd, man/systemd-timesyncd.service.xml. https://github.com/systemd/systemd/blob/main/man/systemd-timesyncd.service.xml
16. systemd, docs/JOURNAL_FILE_FORMAT.md. https://github.com/systemd/systemd/blob/main/docs/JOURNAL_FILE_FORMAT.md
17. systemd, man/journalctl.xml (`--header`). https://github.com/systemd/systemd/blob/main/man/journalctl.xml
18. systemd, man/timedatectl.xml (`set-local-rtc`, `set-timezone`). https://github.com/systemd/systemd/blob/main/man/timedatectl.xml
19. chrony, reference.c · local.c. https://github.com/mlichvar/chrony/blob/master/reference.c , https://github.com/mlichvar/chrony/blob/master/local.c
20. linux-audit, audit-userspace rules/30-stig.rules. https://github.com/linux-audit/audit-userspace/tree/master/rules
21. linux-audit, audit-documentation specs/messages/message-dictionary.csv. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
22. Linux kernel, kernel/audit.c (`audit_serial`, `audit_get_stamp`). https://github.com/torvalds/linux/blob/master/kernel/audit.c
23. Linux man-pages, utmp.5. https://github.com/mkerrisk/man-pages/blob/master/man5/utmp.5
24. util-linux, sys-utils/adjtime_config.5.adoc · sys-utils/dmesg.1.adoc. https://github.com/util-linux/util-linux/blob/master/sys-utils/adjtime_config.5.adoc , https://github.com/util-linux/util-linux/blob/master/sys-utils/dmesg.1.adoc
25. CentOS Stream 9, systemd 패키지 systemd.spec; Ubuntu noble, systemd 패키지 debian/rules. https://gitlab.com/redhat/centos-stream/rpms/systemd/-/raw/c9s/systemd.spec , https://git.launchpad.net/~ubuntu-core-dev/ubuntu/+source/systemd/plain/debian/rules?h=ubuntu-noble
26. UAC, artifacts/live_response/system/date.yaml · hwclock.yaml · timedatectl.yaml. https://github.com/tclahr/uac/tree/main/artifacts/live_response/system
