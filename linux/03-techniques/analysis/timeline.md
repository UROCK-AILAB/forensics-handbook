---
title: "타임라인 만들기"
parent: "기법 · 분석"
nav_order: 960
---

# 타임라인 만들기 (Timeline)

파일 시스템 시각과 로그·기록의 시각을 한곳에 모아 시간 순서대로 정렬하고, 사건이 몰린 구간을 좁혀 보는 방법입니다.

## 언제 쓰나

타임라인 (timeline) 은 "그 시각 앞뒤로 무슨 일이 있었나" 를 물을 때 씁니다. 침입 시각을 좁히거나, 로그인 한 건 뒤에 어떤 파일이 생기고 바뀌었는지 보거나, 지운 파일이 언제쯤 사라졌는지 가늠할 때가 그렇습니다. 아티팩트 하나하나의 뜻은 각 아티팩트 쪽에서 풀고, 이 쪽은 그 시각들을 한 표에 모으는 절차와 도구가 시각을 어떻게 바꾸는지를 다룹니다.

재료는 크게 둘입니다. 하나는 파일 시스템 메타데이터(아이노드의 atime·mtime·ctime·crtime)이고, 다른 하나는 저널·syslog·로그인 기록·패키지 기록·셸 기록처럼 줄마다 시각이 붙은 기록입니다. 시각 값의 단위와 저장 형식은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md), ext4 네 시각이 바뀌는 조건은 [ext4 시각 값](../../01-foundations/filesystem/ext4/timestamps.md) 에 있습니다.

## 절차

1. **검체의 시간대와 시계 상태부터 확인합니다.** 시스템 시간대는 `/etc/localtime` 이 가리키는 zoneinfo 이름으로 정하고, plaso 의 Linux 전처리도 이 파일이 링크면 `zoneinfo/` 뒤 이름을, 일반 파일이면 그 안의 tzfile 을 읽어 시간대를 정합니다[8]. 위치와 판별 순서는 [호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md) 에 있습니다. 저널에서 시계를 바꾼 기록(`MESSAGE_ID=c7a787079b354eaaa9e77b371893cd27` "Time change")과 부팅 뒤 첫 NTP 동기화 기록(`7c8a41f37b764941a0e1780b1be2f037`)도 이때 찾아 둡니다[16][17]. 두 ID 의 해석은 [부팅과 종료 기록](../../02-artifacts/system-info/boot-shutdown.md) 에 있습니다.
2. **파일 시스템 시각을 bodyfile 로 뽑습니다.** 디스크 이미지라면 Sleuth Kit 의 `fls -r -m / 이미지 > body` 가 디렉터리에 이름이 남은 항목을 bodyfile 형식("time machine format")으로 냅니다[1]. `-m` 뒤의 문자열은 파일 이름 앞에 붙는 마운트 지점이고, `-o` 는 이미지 안에서 파일 시스템이 시작하는 섹터, `-d` 는 지운 항목만, `-u` 는 지우지 않은 항목만 냅니다[1]. 이름이 끊긴 아이노드는 `ils -m 이미지 >> body` 로 덧붙입니다. `ils` 는 기본으로 지운 파일의 아이노드만 내고, `-e` 는 전부, `-O` 는 지웠지만 아직 열려 있거나 실행 중인 것, `-p` 는 이름 없는 미할당 고아 아이노드를 냅니다[1].
3. **라이브 시스템이라면 UAC 의 bodyfile 을 씁니다.** UAC 의 `bodyfile` 아티팩트는 `/` 부터 `stat` 수집기로 훑어 `bodyfile/bodyfile.txt` 를 만들고 `proc` 파일 시스템은 뺍니다[11]. 이때 `statx` 명령이 되면 그것을 쓰고, 안 되면 GNU `stat` 을 씁니다[11]. 기본 설정은 `9p`·`cifs`·`fuse`·`nfs`·`nfs4`·`smbfs`·`sysfs` 같은 파일 시스템도 빼므로[11] 네트워크 마운트 아래 파일은 결과에 없습니다. 수집 순서는 [라이브 응답 수집](../acquisition/live-response.md) 에 있습니다.
4. **로그와 기록 시각을 뽑습니다.** plaso 의 `log2timeline.py --storage-file timeline.plaso 이미지` 가 이미지 전체를 훑어 이벤트를 저장합니다[5]. Linux 로 인식된 검체에는 Linux 파서 묶음(preset)이 걸리고, 여기에는 `filestat`·`systemd_journal`·`text/syslog`·`text/syslog_traditional`·`utmp`·`text/dpkg`·`text/apt_history`·`text/bash_history`·`text/zsh_extended_history`·`text/selinux`·`jsonl/docker_container_log` 등이 들어 있습니다[6]. bodyfile 파서는 이 묶음에 없으므로, 2~3단계에서 만든 bodyfile 을 plaso 로 넣으려면 `--parsers bodyfile` 처럼 파서를 따로 지정합니다[5][6]. 감사 로그 (audit log) 를 거르는 법은 [로그 분석](log-analysis.md) 에서 다룹니다.
5. **합치고 걸러 봅니다.** bodyfile 만 볼 때는 `mactime -b body -z 시간대 2025-03-14..2025-03-15` 처럼 날짜 범위를 주고, 시각까지 줄 때는 `yyyy-mm-ddThh:mm:ss` 꼴로 씁니다[1]. `-d` 는 쉼표 구분 출력, `-i day|hour 파일` 은 하루·한 시간 단위 요약 색인, `-p`·`-g` 에 검체의 passwd·group 파일을 주면 UID·GID 대신 이름을 보여 줍니다[1]. plaso 저장 파일은 `psort.py -o dynamic -w 결과.csv timeline.plaso` 로 풀고[5], 관심 시각이 있으면 `--slice "2025-03-14T09:26:40"` 로 앞뒤 5분만 보고 `--slice_size` 로 폭을 바꿉니다[5]. 필터와 `--slicer` 를 함께 주면 필터에 걸린 이벤트마다 앞뒤 이벤트(기본 다섯 개)까지 나옵니다[5]. 이미지 하나를 한 번에 처리할 때는 `psteal.py --source 이미지 -o dynamic -w 결과.csv` 를 씁니다[5].
6. **메모리 이미지가 있으면 메모리 쪽 시각도 붙입니다.** Volatility 3 의 `timeliner` 로 모이는 Linux 플러그인은 `linux.bash`(명령 기록 시각), `linux.boottime`(시간 이름공간별 부팅 시각), `linux.pslist`(프로세스 생성 시각), `linux.lsof`·`linux.pagecache`(열린 파일·캐시된 아이노드의 시각)입니다[15]. 쓰는 법은 [메모리 분석](memory-analysis.md) 에 있습니다.
7. **출력 시간대를 하나로 맞춥니다.** psort 는 기본이 UTC 이고 dynamic·l2tcsv 같은 일부 형식만 `--output-time-zone` 으로 바꿀 수 있습니다[5]. mactime 은 기본이 분석 PC 의 현지 시각입니다(아래 함정 참고)[2]. 보고서에 쓸 시간대를 정하고 모든 결과를 그 시간대로 다시 냅니다.

bodyfile 한 줄은 `|` 로 나눈 11칸이고 칸 순서는 `MD5|name|inode|mode_as_string|UID|GID|size|atime|mtime|ctime|crtime` 입니다[4]. 시각 네 칸은 1970-01-01 00:00:00 UTC 부터의 초이고, MD5 칸의 `0` 은 해시가 없다는 뜻입니다[4]. 아래는 만든 예시입니다.

```
0|/home/user1/.ssh|393217|d/drwx------|1000|1000|4096|1741944400|1741944400|1741944400|1741940000
```

TSK 의 권한 칸은 `d/drwx------` 같은 모양입니다[4]. UAC 가 GNU `stat -c "0|%N|%i|%A|%u|%g|%s|%X|%Y|%Z|%W"` 로 만든 줄은 이름 칸이 `%N`(기본 `shell-escape` 방식으로 따옴표를 친 이름)이고 권한 칸이 `%A`(`ls -ld` 와 비슷한 모양)라서[11][12], 같은 파일이라도 fls 출력과 칸 모양이 다릅니다. 도구에 넣기 전에 첫 몇 줄을 눈으로 확인합니다. mactime 을 `-d` 로 돌리면 머리줄이 `Date,Size,Type,Mode,UID,GID,Meta,File Name` 이고, Type 칸은 `m`·`a`·`c`·`b` 네 자리에 해당 없는 자리를 `.` 로 채운 `m.c.` 같은 모양입니다[2].

## 도구

| 도구 | 입력 | 시각 정밀도 | 기본 출력 시간대 |
|---|---|---|---|
| Sleuth Kit `fls -m`·`ils -m` | 디스크 이미지 | bodyfile 칸으로 넘김[1] | 해당 없음(epoch 값) |
| Sleuth Kit `mactime` | bodyfile | 정수 초[2] | 분석 PC 의 `TZ`, `-z` 로 지정, `-y` 면 UTC[2] |
| Sleuth Kit `istat` | 이미지의 아이노드 하나 | 나노초. 단 ext4 epoch 비트는 반영하지 않음[3][19] | 검체 출력으로 확인 |
| UAC `bodyfile` | 라이브 시스템 | GNU `stat` 경로면 초, 생성 시각을 모르면 `0`[11][12] | 해당 없음(epoch 초) |
| plaso `log2timeline`·`psort`·`psteal` | 이미지·디렉터리·bodyfile | 타임스탬프는 마이크로초, dynamic time 은 원본 정밀도를 유지[5] | UTC, `--output-time-zone` 으로 바꿈[5] |
| Volatility 3 `timeliner` | 메모리 이미지 | 플러그인마다 다름[15] | 검체 출력으로 확인 |

plaso 는 psort 출력 대상으로 `opensearch_ts`(Timesketch 용), `l2tcsv`(17칸 CSV), `tln`(5칸)·`l2ttln`(7칸), `json_line`, `xlsx` 등을 둡니다[5]. `filestat` 파서는 파일 항목의 접근·추가·백업·변경·생성·삭제·수정 시각을 이벤트로 만듭니다[21]. ext4 에서 삭제 시각이 채워지는지는 파일 시스템을 읽는 하부 라이브러리에 달렸으므로 검체 출력으로 확인합니다.

## 함정과 한계

**도구가 시각을 줄입니다.** mactime 은 시각을 정수 초로 다루고[2], GNU `stat` 의 `%X`·`%Y`·`%Z`·`%W` 는 epoch 초라서[12] GNU `stat` 으로 만든 UAC bodyfile 에는 소수부가 없습니다. plaso 의 타임스탬프는 1970-01-01 00:00:00 UTC 부터의 마이크로초 64비트 정수이고, 2021-05-11 부터는 원본에 저장된 정밀도를 dfDateTime 객체로 유지하는 dynamic time 도 씁니다[5]. 나노초가 출력에 남는지는 출력 형식마다 결과를 보고 확인합니다. 같은 초 안의 순서를 가려야 하면 `istat` 이나 `debugfs` 로 아이노드의 원래 값을 봅니다.

**출력 시간대가 도구마다 다릅니다.** mactime 은 `-y`(ISO 8601)를 주지 않으면 Perl 의 `localtime()` 으로 날짜를 만들고, 이 값은 분석 PC 의 `TZ` 나 `-z` 로 준 시간대를 따릅니다[2]. `-y` 를 주면 `gmtime()`, 즉 UTC 로 찍고 이때 `-z` 는 효과가 없습니다[1][2]. psort 는 기본이 UTC 입니다[5]. 같은 이미지로 두 도구를 돌리면 시간대 차이만큼 어긋나 보일 수 있습니다.

**시간대 표시가 없는 기록이 섞입니다.** plaso 는 전통 syslog 줄에 연도를 추정해 넣고 현지 시각 표시(`is_local_time`)를 붙입니다[9]. bodyfile 파서도 읽은 시각에 같은 표시를 붙입니다[4]. `log2timeline` 의 `-z`·`--timezone` 은 "시간대 표시 없이 저장된 시각" 의 시간대이고, 원본에서 정할 수 있으면 그것을, 아니면 UTC 를 씁니다[7]. bodyfile 의 epoch 초는 원래 UTC 기준이므로[13], UTC 가 아닌 시간대를 주면 bodyfile 시각이 그만큼 한 번 더 옮겨질 가능성이 있습니다. UTC 로 돌린 결과와 원래 epoch 값을 한 번 맞춰 봅니다. 전통 syslog 의 연도 추정 문제는 [로그 분석](log-analysis.md) 에서 다룹니다.

**저널 항목의 시각은 두 가지일 수 있습니다.** plaso 는 저널 항목의 `__REALTIME_TIMESTAMP`(journald 가 받은 시각)를 기록 시각(written_time)으로 담고, `_SOURCE_REALTIME_TIMESTAMP` 가 있으면 recorded_time 으로 따로 담습니다[10]. `systemd-journal-remote` 로 모은 저널이면 앞의 값은 중앙 서버가 받은 시각이라 두 값이 벌어집니다[10].

**시각이 없는 이벤트는 0으로 들어갑니다.** plaso 는 시각이 없는 이벤트에 타임스탬프 0 을 씁니다[5]. 결과 맨 앞의 1970-01-01 줄은 사건이 아니라 시각 없는 기록일 가능성이 큽니다. psort 는 기본으로 중복 이벤트를 합치므로 모두 보려면 `-a`(`--include_all`)를 줍니다[5].

**TSK 는 2038년 뒤 ext4 시각을 잘못 풉니다.** Sleuth Kit 의 `ext2fs.cpp` 는 `_extra` 칸에서 나노초만 꺼내고 epoch 확장 비트를 초에 더하지 않습니다[3]. TSK 4.4.2 로 시험한 논문도 `istat` 이 2038년 뒤 시각을 잘못 푼다고 보고했습니다[19]. 자세한 계산은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

**한 줄이 한 사건은 아닙니다.** plaso 는 원본 표현에 가장 가까운 수준(source-level)의 이벤트를 뽑고, 여러 이벤트를 묶은 시스템 수준·사용자 수준의 사건은 분석 플러그인으로 끌어냅니다[5]. mactime 은 같은 파일의 같은 초 시각을 한 줄로 합쳐 `macb` 처럼 보여 주므로[2], 파일 하나를 만든 일이 파일 시스템 쪽 한 줄과 저널·셸 기록 쪽 여러 줄로 나뉘어 보일 수 있습니다.

**시각을 맞춰 잇는 방식은 시계 동기화에 기댑니다.** 여러 기록을 시각으로 잇는 상관은 NTP 같은 시계 동기화에 크게 기댄다는 주장이 있습니다[20]. 호스트 여러 대를 한 타임라인에 넣을 때는 호스트마다 시계 어긋남을 먼저 잽니다. `fls`·`ils` 의 `-s 초` 는 원래 시스템의 시계 어긋남을 보정하는 값이고, 100초 느렸으면 `-100` 을 줍니다[1].

## 결과를 어떻게 해석하나

### 증명하는 것

- 수집 시점에 그 파일의 아이노드에 그 시각 값이 들어 있었다는 것.
- 저널·로그 한 줄이 그 줄을 쓴 시스템의 시계 기준으로 그 시각에 쓰였다는 것. 같은 `_BOOT_ID` 안에서는 `__MONOTONIC_TIMESTAMP` 로 순서를 확인할 수 있습니다[18].
- 여러 기록이 같은 구간에 몰려 있다는 것. 이 구간이 다음 분석의 범위가 됩니다.

### 증명하지 못하는 것

- "그 시각에 수정했다" 는 것. `utimensat()`·`futimens()` 로 atime 과 mtime 은 나노초까지 원하는 값을 넣을 수 있습니다[13]. mtime 은 "메타데이터가 그 시각을 가리킨다" 까지만 말해 줍니다.
- "마지막으로 읽은 시각" 이라는 것. Linux 2.6.30 부터 기본 동작은 relatime 이고, atime 이 mtime·ctime 보다 이르거나 같을 때나 하루보다 오래됐을 때만 atime 을 고칩니다[14].
- 그 전의 사건. 네 시각은 모두 "마지막" 값이라서 덮어쓴 이전 값은 남지 않습니다[13].
- 시계가 맞았다는 것. 시계를 바꾼 흔적이 있으면 그 앞뒤의 벽시계 시각은 따로 따져야 하고, 판단 절차는 [시각을 조작했나](../../04-scenarios/insider/time-manipulation.md) 에서 다룹니다.

### 시각 해석

bodyfile 과 plaso 저장 파일의 시각은 UTC 기준 epoch 값이고, 화면에 보이는 시간대는 출력 단계에서 정해집니다. 지운 파일의 ctime 은 "마지막 상태 변경" 이 아니라 지운 순간일 가능성이 있습니다. ext4 에서 파일을 지우는 시험에서는 ctime·mtime 의 나노초가 지운 순간의 값으로 바뀌고 atime·crtime 의 나노초는 그대로였습니다[19]. 지운 파일의 아이노드에 무엇이 남는지는 [지운 파일이 남기는 것](../../01-foundations/filesystem/ext4/deleted-files.md) 에 있습니다. ext4 dtime 칸의 작은 정수는 시각이 아니라 고아 목록의 다음 아이노드 번호일 수 있으니, 이것도 같은 쪽에서 확인합니다.

나노초 칸의 분포가 이상하면 따로 봅니다. atime·crtime 의 30비트 나노초 칸에 데이터를 숨기는 기법이 보고되었고, 파일 탐색기나 `ls -la` 는 나노초를 보여 주지 않아 눈에 띄지 않습니다[19].

### 보고서 문장

기록이 말하는 만큼만 씁니다. "공격자가 2025-03-14 09:26 에 authorized_keys 를 고쳤다" 가 아니라 "`/home/user1/.ssh/authorized_keys` 의 mtime 과 ctime 이 2025-03-14 09:26:40 UTC 를 가리키고, 같은 분에 저널에 계정 user1 의 SSH 로그인 기록이 있다(만든 예시)" 처럼 씁니다. 도구 이름과 판, 출력 시간대, 시각을 초나 마이크로초로 줄였는지를 함께 적습니다.

## 함께 볼 페이지

- [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) — 단위·저장 형식·시계 종류
- [ext4](../../01-foundations/filesystem/ext4/index.md) — 아이노드와 시각이 있는 곳
- [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) — 저널 시각 필드
- [로그 분석](log-analysis.md) — 로그 줄 거르기와 교차 확인
- [지운 파일 되살리기](file-recovery.md) — `fls -d`·`ils` 결과를 되살리는 절차
- 다른 판의 타임라인: [Windows](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html) · [macOS](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/timeline/index.html) · [Android](https://urock-ailab.github.io/forensics-handbook/android/03-techniques/analysis/timeline/index.html) · [iOS](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/analysis/timeline/index.html)

## 참고 문헌

1. The Sleuth Kit, man 페이지 `fls.1`·`ils.1`·`mactime.1`. https://github.com/sleuthkit/sleuthkit/tree/develop/man
2. The Sleuth Kit, `tools/timeline/mactime.base`. https://github.com/sleuthkit/sleuthkit/blob/develop/tools/timeline/mactime.base
3. The Sleuth Kit, `tsk/fs/ext2fs.cpp`. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs.cpp
4. plaso, `plaso/parsers/bodyfile.py`. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/bodyfile.py
5. plaso, 사용자 문서 `Creating-a-timeline.md`·`Using-log2timeline.md`·`Using-psort.md`·`Scribbles-about-events.md`. https://github.com/log2timeline/plaso/tree/main/docs/sources/user
6. plaso, `plaso/data/presets.yaml`. https://github.com/log2timeline/plaso/blob/main/plaso/data/presets.yaml
7. plaso, `plaso/cli/extraction_tool.py`. https://github.com/log2timeline/plaso/blob/main/plaso/cli/extraction_tool.py
8. plaso, `plaso/preprocessors/linux.py`. https://github.com/log2timeline/plaso/blob/main/plaso/preprocessors/linux.py
9. plaso, `plaso/parsers/text_plugins/syslog.py`. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/syslog.py
10. plaso, `plaso/parsers/systemd_journal.py`. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/systemd_journal.py
11. tclahr, UAC — `artifacts/bodyfile/bodyfile.yaml`, `lib/setup_tools.sh`, `config/uac.conf`. https://github.com/tclahr/uac/blob/main/artifacts/bodyfile/bodyfile.yaml , https://github.com/tclahr/uac/blob/main/lib/setup_tools.sh , https://github.com/tclahr/uac/blob/main/config/uac.conf
12. GNU coreutils, `doc/coreutils.texi` (`stat` 형식 지시자). https://github.com/coreutils/coreutils/blob/master/doc/coreutils.texi
13. Linux man-pages, `inode(7)`, `utimensat(2)`. https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7 , https://github.com/mkerrisk/man-pages/blob/master/man2/utimensat.2
14. util-linux, `sys-utils/mount.8.adoc`. https://github.com/util-linux/util-linux/blob/master/sys-utils/mount.8.adoc
15. Volatility 3, `volatility3/framework/plugins/linux/` (`bash.py`·`boottime.py`·`pslist.py`·`lsof.py`·`pagecache.py`). https://github.com/volatilityfoundation/volatility3/tree/develop/volatility3/framework/plugins/linux
16. systemd, `catalog/systemd.catalog.in`. https://github.com/systemd/systemd/blob/main/catalog/systemd.catalog.in
17. Red Hat, systemd-rhel9 source-git, `catalog/systemd.catalog.in`. https://github.com/redhat-plumbers/systemd-rhel9/blob/main/catalog/systemd.catalog.in
18. systemd, `man/systemd.journal-fields.xml`. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
19. Thomas Göbel, Harald Baier, "Anti-forensics in ext4: On secrecy and usability of timestamp-based data hiding", Digital Investigation 24 (2018) S111–S120, DFRWS 2018 Europe. https://doi.org/10.1016/j.diin.2018.01.014
20. Johannes Olegård, Stefan Axelsson, Yuhong Li, "When is logging sufficient? — Tracking event causality for improved forensic analysis and correlation", Forensic Science International: Digital Investigation 52 (2025) 301877, DFRWS EU 2025. https://doi.org/10.1016/j.fsidi.2025.301877
21. plaso, `plaso/parsers/filestat.py`. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/filestat.py
