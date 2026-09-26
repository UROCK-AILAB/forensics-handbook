---
title: "조사 절차"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 900
---

# 조사 절차 (Investigation Process)

Linux 분석 대상을 다룰 때 무엇을 어떤 순서로 뜨는지, 뜨는 동안 시스템을 얼마나 바꾸는지, 받은 이미지를 원본을 건드리지 않고 여는 방법을 한 흐름으로 정리합니다. 도구별로 자세히 뜨는 방법은 이 분류의 하위 페이지에 두고, 이 페이지에서는 순서와 기록을 다룹니다.

## 언제 쓰나

켜져 있는 서버나 PC 에서 침해 대응을 시작할 때, 전원이 꺼진 디스크나 이미지를 받았을 때, 클라우드 가상 머신이나 컨테이너를 조사할 때 모두 이 흐름을 씁니다. 상황마다 먼저 할 일과 자세한 페이지는 다음과 같습니다.

| 상황 | 먼저 할 일 | 자세한 페이지 |
|---|---|---|
| 켜져 있는 시스템 | 프로세스·네트워크 같은 휘발성 정보부터 뜬다 | [라이브 응답 수집](./live-response.md) |
| 메모리가 필요한 사건 | 메모리를 따로 뜬다 | [메모리 수집](./memory-acquisition.md) |
| 꺼진 디스크·받은 이미지 | 원본을 쓰지 않게 이미지를 만들고 사본으로 연다 | [디스크 이미징](./disk-imaging.md) |
| 클라우드 가상 머신 | 스냅숏과 게스트 안 수집을 나눈다 | [클라우드 가상 머신 수집](./cloud-vm.md) |
| 컨테이너 | 컨테이너를 멈추기 전에 뜰 것을 정한다 | [컨테이너 수집](./container-acquisition.md) |

절차 자체는 Ubuntu 24.04 LTS 와 RHEL 9 에서 같습니다. 배포판마다 달라지는 것은 로그 파일 이름과 경로이고, 그 차이는 각 아티팩트 페이지에 있습니다.

## 절차

1. **사건 정보와 기준 시각을 먼저 남깁니다.** 대상 기계의 현재 시각과 시간대, 시계 동기화 상태를 가장 먼저 적어 두면 뒤에 나오는 모든 시각을 이 값에 맞춰 볼 수 있습니다. UAC (Unix-like Artifacts Collector) 는 `date` 와 `timedatectl status` 의 출력을 `live_response/system` 아래 `date.txt`, `timedatectl_status.txt` 로 남깁니다[6]. 시간대 설정 파일을 읽는 법은 [호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md) 페이지에 있습니다. UAC 에 `--case-number`, `--evidence-number`, `--description`, `--examiner`, `--notes` 를 주면 그 값이 수집 로그에 함께 들어갑니다[5][10].

2. **휘발성이 큰 것부터 뜹니다.** UAC 는 휘발성 순서 (order of volatility) 에 따라 수집하고[1], 사고 대응용 `ir_triage` 프로필과 `full` 프로필의 순서도 그렇게 짜여 있습니다[2]. 두 프로필은 시스템을 바꾸는 `live_response/modifiers` 를 맨 앞에 두고, 그 뒤로 프로세스(`ps`, `lsof`, `top`, `/proc` 정보, 실행 중인 프로세스의 해시와 문자열), 네트워크, 파일 메타데이터(bodyfile), 시스템·하드웨어·패키지·저장 장치·컨테이너·가상 머신 정보, 실행 파일 해시를 거쳐 마지막에 로그와 설정 파일 사본을 모읍니다[2]. 두 프로필에는 메모리 덤프 아티팩트(`memory_dump`)가 들어 있지 않으므로[2] 메모리는 따로 뜹니다([메모리 수집](./memory-acquisition.md)).

3. **파일을 복사하기 전에 파일 시스템 메타데이터를 뜹니다.** UAC 의 bodyfile 아티팩트는 `/` 부터 파일 시스템 전체의 stat 정보를 모아 `bodyfile/bodyfile.txt` 로 남기고, `proc` 과 `procfs` 는 건너뜁니다[3]. 프로필에서 이 단계가 파일 사본 수집보다 앞에 있으므로[2] 파일을 읽어 접근 시각 (atime) 이 바뀌기 전의 시각이 먼저 남습니다. Linux 2.6.30 부터 커널 기본 동작은 `relatime` 인데, 이 규칙에서는 이전 atime 이 mtime 이나 ctime 보다 이르거나 같을 때 atime 을 고치고, atime 이 하루보다 오래됐으면 읽을 때마다 고칩니다[7]. 그래서 수집하면서 파일을 연 것만으로도 atime 이 바뀔 수 있습니다. bodyfile 로 타임라인을 만드는 법은 [타임라인 만들기](../analysis/timeline.md) 페이지에 있습니다.

4. **라이브 검색 전에 atime 갱신을 막을지 정합니다.** 켜진 시스템에서 `find` 로 파일을 찾는 작업도 증거를 건드릴 수 있으므로, 검색 전에 atime 갱신을 막는 방법이 두 가지 있습니다[11]. 하나는 루트 파일 시스템을 `mount -o remount,noatime` 으로 다시 붙이는 것이고, 다른 하나는 `mount --bind / $rootvol` 로 루트를 다른 자리에 붙인 뒤 `mount -o remount,ro $rootvol` 로 그 자리만 읽기 전용으로 바꾸는 것입니다. `noatime` 은 디렉터리를 포함한 모든 아이노드 종류의 atime 갱신을 끕니다[7]. 읽기 전용 바인드는 그 마운트 지점만 읽기 전용이고 원래 파일 시스템의 슈퍼블록은 여전히 쓸 수 있습니다[7]. 전통적인 mount(2) 호출로는 `-o rbind,ro` 처럼 하위 마운트까지 읽기 전용을 한꺼번에 걸 수 없고, util-linux 2.39 부터 `ro=recursive` 로 걸 수 있습니다[7]. 두 방법 모두 대상 시스템의 마운트 상태를 바꾸므로, 쓴 경우에는 시각과 명령을 기록합니다.

5. **시스템을 바꾸는 수집은 켰을 때만 돌고, 켰다면 기록합니다.** UAC 는 기본으로 root 권한인지 확인하고, `-u`(`--run-as-non-root`)로 이 확인을 끄면 수집이 제한될 수 있습니다[5]. 시스템 상태를 바꾸는 아티팩트는 `modifier: true` 로 표시되어 있고 `--enable-modifiers` 를 줄 때만 돕니다(기본값 false)[5][9]. 이런 아티팩트는 바꾸기 전 상태를 먼저 남깁니다[4]. ftrace 를 끄는 아티팩트는 `sysctl -a` 를 저장한 뒤 `sysctl kernel.ftrace_enabled=0` 을 실행하고, `/proc/PID` 에 바인드 마운트된 디렉터리를 푸는 아티팩트는 `mount` 와 `ps` 결과, `ps` 에 보이지 않는 `/proc` PID 목록을 저장한 뒤 `umount` 를 실행합니다[4]. 숨긴 프로세스를 해석하는 법은 [루트킷 찾기](../analysis/rootkit-detection.md) 페이지에 있습니다.

6. **수집 범위에서 빠지는 것을 확인합니다.** UAC 는 기본 설정에서 `9p`, `afs`, `autofs`, `cifs`, `davfs`, `fuse`, `kernfs`, `nfs`, `nfs4`, `rpc_pipefs`, `smbfs`, `sysfs` 파일 시스템을 건너뜁니다[8]. 네트워크 공유에 증거가 있을 가능성이 있다면 따로 뜰지 정합니다. `--start-date`, `--end-date` 로 날짜를 거르면 기본 설정에서는 mtime 과 ctime 만 보고 atime 은 보지 않습니다(`enable_find_mtime: true`, `enable_find_atime: false`, `enable_find_ctime: true`)[5][8].

7. **결과물에 해시를 남기고 수집 로그를 보관합니다.** UAC 는 결과물 옆에 같은 이름의 `.log` 파일을 만듭니다[9]. 결과물 기본 이름은 `uac-%hostname%-%os%-%timestamp%` 이고, `%timestamp%` 자리에는 `date "+%Y%m%d%H%M%S"` 값이 들어갑니다[9]. 형식은 `none`, `tar`, `zip` 중에서 고르고 기본은 `tar` 이며, gzip 이 있으면 압축합니다[5]. 결과물 해시는 설정의 `hash_algorithm` 을 따르고 기본은 MD5 와 SHA1 입니다[8]. `-H`(`--hash-collected`)를 주면 모은 파일마다 `hash_algorithm` 에 적힌 알고리즘으로 해시를 계산해 `hash_list.md5` 처럼 알고리즘 이름이 붙은 파일에 남기므로, 기본 설정에서는 `hash_list.md5` 와 `hash_list.sha1` 이 생깁니다[5][9][15]. 수집 로그는 다음 모양입니다[10](값은 만든 예시입니다).

   ```
   Created by UAC (Unix-like Artifacts Collector) 3.0.0

   [Case Information]
   Case Number: 2026-0001
   Evidence Number: E01
   Description: web server triage
   Examiner: examiner1
   Notes:

   [System Information]
   Operating System: linux
   System Architecture: x86_64
   Hostname: web01

   [Acquisition Information]
   Mount Point: /
   Acquisition Started: Sat Sep 26 14:02:11 2026 +0900
   Acquisition Finished: Sat Sep 26 14:19:47 2026 +0900

   [Output Information]
   File: uac-web01-linux-20260926140209.tar.gz
   Format: tar

   [Computed Hashes]
   MD5 checksum: 00112233445566778899aabbccddeeff
   SHA1 checksum: 00112233445566778899aabbccddeeff00112233
   ```

   시작·종료 시각은 `date "+%a %b %d %H:%M:%S %Y %z"` 로 적으므로 시간대 오프셋이 붙습니다[9]. 형식을 `none` 으로 고르면 `[Output Information]` 에 `Directory:` 가 적히고 `[Computed Hashes]` 절은 생기지 않습니다[10].

8. **이미지나 디스크는 사본을 원본을 쓰지 않게 마운트해서 봅니다.** 마운트하기 전에 The Sleuth Kit 의 `mmls` 로 파티션을, `fsstat` 으로 파일 시스템을 먼저 확인합니다[11]. ext4 는 읽기 전용(`ro`)으로 마운트해도 저널을 재생하면서 파티션에 쓰므로, 쓰지 않으려면 `ro,noload` 로 마운트합니다[12]. `noload`(`norecovery`)는 저널을 싣지 않는 옵션이라, 깨끗이 내려가지 않은 파일 시스템이면 앞뒤가 맞지 않는 상태로 보일 수 있습니다[12]. XFS 는 `norecovery` 로 로그 복구를 건너뛰고, 이 옵션은 읽기 전용 마운트에서만 받아들입니다[13]. `nouuid` 는 파일 시스템 UUID 로 이중 마운트를 검사하지 않게 하는 옵션이라, LVM 스냅숏 볼륨을 읽기 전용으로 붙일 때 `norecovery` 와 함께 씁니다[13]. 이미지를 만드는 법은 [디스크 이미징](./disk-imaging.md), 볼륨 구조는 [LVM 논리 볼륨](../../01-foundations/disk-volume/lvm.md) 페이지에 있습니다.

9. **마운트한 이미지에서도 같은 수집을 돌릴 수 있습니다.** UAC 의 `offline` 프로필은 라이브 항목 없이 bodyfile, chkrootkit, 실행 파일 해시, 시스템·SSH·패키지 정보, 파일 사본만 모으고[2], `-m`(`--mount-point`)로 마운트한 이미지의 위치를 대상으로 줍니다(기본값 `/`)[5]. dissect 의 `acquire` 는 디스크 이미지와 라이브 시스템 양쪽에서 모듈 단위로 모으는데, 라이브에서는 운영체제의 파일 접근 대신 원시 디스크를 읽으려고 관리자 권한을 요구하고, `--fallback`, `--force-fallback` 을 주면 운영체제를 거쳐 읽습니다[14].

10. **기준 시각을 잡고 타임라인으로 확인합니다.** 한 워크숍 사례는 로그인 기록을 기준으로 삼아 `find rootvol/ -type f -newercm rootvol/var/log/lastlog` 로 그 뒤에 생긴 파일을 찾고, 지운 파일은 ext4 저널(아이노드 8)을 `debugfs -R 'dump <8> ./journal'` 로 뽑아 ext4magic 으로 되살리기를 시도한 뒤, 결론은 타임라인으로 확인합니다[11]. 사례 하나의 흐름이므로 순서의 예로만 봅니다. 로그인 기록은 [로그인 기록](../../02-artifacts/logins/wtmp-btmp-lastlog.md), 지운 파일은 [지운 파일 되살리기](../analysis/file-recovery.md), ext4 저널은 [ext4](../../01-foundations/filesystem/ext4/index.md) 페이지에 있습니다.

## 도구

| 도구 | 쓰는 곳 | 이 페이지에서 쓰는 기능 |
|---|---|---|
| UAC | 라이브·마운트한 이미지 | 프로필(`ir_triage`, `full`, `offline`), bodyfile, 수집 로그와 해시[2][3][9][10] |
| dissect `acquire` | 라이브·디스크 이미지 | 원시 디스크를 읽어 모듈 단위로 수집[14] |
| The Sleuth Kit | 이미지 | 마운트 전 `mmls`, `fsstat` 로 구조 확인[11] |
| util-linux `mount` | 라이브·이미지 | `noatime`, 읽기 전용 바인드, `ro,noload`, `norecovery`[7][12][13] |
| debugfs, ext4magic | ext4 이미지 | 저널 뽑기와 지운 파일 되살리기 시도[11] |

## 함정과 한계

- **읽기 전용 마운트가 곧 무변경은 아닙니다.** ext4 는 `ro` 로도 저널을 재생해 파티션에 쓰고[12], 읽기 전용 바인드도 원래 파일 시스템 슈퍼블록은 쓸 수 있습니다[7]. 그래서 원본이 아닌 사본에서 작업합니다.
- **수집 도구 자신의 흔적은 결과물에 보이지 않습니다.** UAC 는 자기 폴더, `/uac-data.tmp/`, 결과물 이름과 맞는 경로를 수집한 파일 목록에서 뺍니다[9]. 결과물에 수집 도구의 파일이 없다고 해서 대상 시스템에 흔적이 남지 않았다는 뜻은 아닙니다.
- **날짜 필터는 atime 을 보지 않습니다.** 기본 설정에서는 mtime 과 ctime 만 보므로[8], 읽기만 한 파일은 날짜 필터로 걸러질 수 있습니다.
- **네트워크 파일 시스템은 기본으로 빠집니다.** NFS·CIFS·FUSE 같은 파일 시스템은 기본 제외 목록에 있습니다[8].
- **시스템을 바꾸는 조치는 보고서에 적어야 합니다.** `--enable-modifiers` 로 켠 아티팩트와 `remount,noatime` 같은 마운트 변경은 수집 뒤 상태를 바꿉니다[4][5][11].

## 결과를 어떻게 해석하나

수집 로그와 해시가 보여 주는 것은 "이 시각부터 이 시각까지 이 도구로 이 파일을 떴고, 그 결과물의 해시가 이 값이었다" 까지입니다. 수집을 시작하기 전에 이미 바뀐 것은 가려내지 못하고, 수집 도구를 올리고 실행하면서 생긴 흔적도 따로 떼어 내지 못합니다. 그래서 수집에 쓴 명령과 켠 옵션, 시작·종료 시각을 함께 남겨 두어야 뒤에 나온 흔적이 수집 과정에서 생긴 것인지 구분할 수 있습니다.

시각은 두 가지를 구분해서 읽습니다. 수집 로그의 `Acquisition Started`·`Acquisition Finished` 는 `%z` 오프셋이 붙어 있어 UTC 로 바꿀 수 있습니다[9]. 결과물 이름의 타임스탬프는 대상 시스템 시계의 현지 시각이고 시간대 표시가 없어서[9], 대상 시계가 틀렸다면 이름의 시각도 같이 틀립니다. 1단계에서 남긴 `date`, `timedatectl status` 출력과 조사자 쪽 시계를 대조해 차이를 적어 둡니다.

atime 은 "마지막으로 읽은 시각" 이 아니라 `relatime` 규칙에 따라 고쳐진 시각입니다[7]. atime 이 mtime·ctime 보다 늦고 하루가 지나지 않았다면 그 사이에 다시 읽어도 atime 은 그대로이므로, atime 하나로 파일을 읽은 횟수나 마지막 열람 시각을 단정하지 않습니다. 시각 값 자체를 읽는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

보고서에는 기록으로 확인되는 만큼만 씁니다. 예를 들면 "2026-09-26 14:02:11 +0900 부터 14:19:47 +0900 까지 UAC `ir_triage` 프로필로 web01 에서 수집했고, 시스템을 바꾸는 아티팩트는 켜지 않았으며, 결과물의 SHA1 값은 수집 로그에 적힌 값과 같다" 처럼 씁니다(만든 예시).

## 함께 볼 페이지

- [라이브 응답 수집](./live-response.md) — 켜진 시스템에서 무엇을 어떤 명령으로 뜨는지
- [디스크 이미징](./disk-imaging.md) — 디스크 이미지를 만들고 검증하는 법
- [타임라인 만들기](../analysis/timeline.md) — bodyfile 과 로그를 시간순으로 합치는 법
- [Linux 포렌식 보고서](../reporting/forensic-report.md) — 수집 과정을 보고서에 적는 법
- 다른 판의 조사 절차: [Windows](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/investigation-process.html), [macOS](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/process-acquisition/investigation-process.html), [Android](https://urock-ailab.github.io/forensics-handbook/android/03-techniques/acquisition/investigation-process.html), [iOS](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/acquisition/investigation-process.html), [AI](https://urock-ailab.github.io/forensics-handbook/ai/03-techniques/acquisition/investigation-process.html)

## 참고 문헌

1. UAC, README.md. https://github.com/tclahr/uac/blob/main/README.md
2. UAC, profiles/ir_triage.yaml·full.yaml·offline.yaml. https://github.com/tclahr/uac/tree/main/profiles
3. UAC, artifacts/bodyfile/bodyfile.yaml. https://github.com/tclahr/uac/blob/main/artifacts/bodyfile/bodyfile.yaml
4. UAC, artifacts/live_response/modifiers/disable_ftrace.yaml·revel_hidden_processes.yaml. https://github.com/tclahr/uac/tree/main/artifacts/live_response/modifiers
5. UAC, lib/usage.sh. https://github.com/tclahr/uac/blob/main/lib/usage.sh
6. UAC, artifacts/live_response/system/date.yaml·timedatectl.yaml. https://github.com/tclahr/uac/tree/main/artifacts/live_response/system
7. util-linux, mount(8). https://github.com/util-linux/util-linux/blob/master/sys-utils/mount.8.adoc
8. UAC, config/uac.conf. https://github.com/tclahr/uac/blob/main/config/uac.conf
9. UAC, uac(주 스크립트). https://github.com/tclahr/uac/blob/main/uac
10. UAC, lib/create_acquisition_log.sh. https://github.com/tclahr/uac/blob/main/lib/create_acquisition_log.sh
11. Hadi, A., Khader, M., Claflin, T. "Learning Linux Forensic Analysis and Why it Matters". DFRWS 워크숍 발표 자료. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
12. Linux kernel, Documentation/admin-guide/ext4.rst. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/ext4.rst
13. Linux kernel, Documentation/admin-guide/xfs.rst. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/xfs.rst
14. fox-it acquire, README.md. https://github.com/fox-it/acquire/blob/main/README.md
15. UAC, lib/find_based_collector.sh. https://github.com/tclahr/uac/blob/main/lib/find_based_collector.sh
