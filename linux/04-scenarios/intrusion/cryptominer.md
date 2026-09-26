---
title: "채굴기가 돌았나"
parent: "시나리오 · 침해"
nav_order: 1060
---

# 채굴기가 돌았나 (Cryptominer)

어떤 프로세스가 CPU 를 오래 썼는지 찾고, 그 프로세스를 띄운 장치와 들어온 경로까지 되짚는 조사입니다. 지금 도는 프로세스는 `/proc` 에서 바로 보이지만, 이미 멈춘 채굴기의 CPU 사용량은 그것을 따로 남기는 기록이 있을 때만 남습니다.

## 조사 질문

이 조사는 다섯 가지 질문으로 나뉩니다. 어떤 프로세스가 CPU 를 오래 썼는지, 언제부터 돌았는지, 무엇이 그 프로세스를 띄웠는지, 어디로 연결했는지, 재부팅이나 종료 뒤에도 다시 떴는지입니다.

앞의 두 질문은 CPU 시간 기록으로, 세 번째는 부모 프로세스와 서비스 단위(unit)로, 네 번째는 소켓 정보로, 다섯 번째는 지속성 장치로 답합니다. 채굴 풀의 주소나 포트로 채굴기임을 가리는 방법은 이 쪽에서 다루지 않고, 실행 파일은 해시와 YARA 로 가립니다([알려진 파일 대조와 YARA](../../03-techniques/analysis/hash-yara.md)).

## 먼저 확인할 것

**라이브인지 이미지인지.** 지금 도는 프로세스의 CPU 시간·실행 파일·연결은 `/proc` 에만 있고, `/proc` 는 전원을 끄면 사라지는 가상 파일 시스템입니다([실행 중인 프로세스 (/proc)](../../02-artifacts/execution/proc.md)). 켜져 있는 시스템이면 끄기 전에 라이브 수집과 메모리 수집부터 합니다([라이브 응답 수집](../../03-techniques/acquisition/live-response.md), [메모리 수집](../../03-techniques/acquisition/memory-acquisition.md)).

**배포판과 systemd 판.** 서비스 단위가 멈출 때 남는 CPU 사용량 줄은 systemd 판에 따라 문장이 다릅니다. Ubuntu 24.04 LTS 는 systemd 255, RHEL 9 는 systemd 252 를 씁니다[6].

**과거 CPU 사용량을 남기는 장치가 있었는지.** 이미 멈춘 프로세스의 CPU 시간은 아래 세 곳에 남습니다. atop 과 프로세스 회계는 설치하고 켜 두었는지를 검체에서 확인합니다.

| 장치 | 검체에서 확인할 것 | 남는 것 |
|---|---|---|
| systemd 단위 자원 기록 | 저널을 디스크에 영구 저장했는지([systemd 저널](../../01-foundations/logging/systemd-journal/index.md)) | 멈춘 단위가 쓴 CPU 시간 |
| atop | `/var/log/atop/atop_*` 파일이 있는지 | 수집 간격마다의 프로세스 목록 |
| 프로세스 회계 | 회계 파일이 있는지([프로세스 회계](../../02-artifacts/execution/process-accounting.md)) | 끝난 프로세스마다 이름과 CPU 시간 |

**시간대와 수집 범위.** 시스템 시간대를 먼저 정합니다([호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md)). UAC 로 수집한 자료라면 `/tmp` 와 `/dev/shm` 은 10MB 이하 파일만 모으고[3], 지워진 실행 파일은 앞 약 20MB 만 떠 온다는 점을 적어 둡니다[3]. 큰 채굴 바이너리는 이 제한에 걸릴 수 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `/proc`(프로세스·CPU 시간·`exe`·`cmdline`·소켓) | 지금 도는 것과 그 실행 파일 | [실행 중인 프로세스 (/proc)](../../02-artifacts/execution/proc.md), [라이브 응답 수집](../../03-techniques/acquisition/live-response.md) |
| 2 | 메모리 이미지 | 숨은 프로세스, 지워진 실행 파일 | [메모리 분석](../../03-techniques/analysis/memory-analysis.md), [루트킷 찾기](../../03-techniques/analysis/rootkit-detection.md) |
| 3 | 저널(단위 시작·중지·CPU 사용량) | 서비스로 돌렸는지, 쓴 CPU 시간 | [systemd 저널](../../01-foundations/logging/systemd-journal/index.md), [systemd 서비스와 타이머](../../02-artifacts/persistence/systemd-units.md) |
| 4 | atop 기록, 프로세스 회계 | 과거에 돈 프로세스와 CPU 시간 | [프로세스 회계](../../02-artifacts/execution/process-accounting.md) |
| 5 | cron·systemd 타이머·셸 시작 파일 | 다시 띄우는 장치 | [무엇이 계속 살아남게 했나](persistence-hunt.md) |
| 6 | `/tmp`·`/dev/shm`·`/var/tmp`, 홈의 숨김 폴더 | 바이너리와 설정 파일 | [임시 폴더와 메모리 파일 시스템](../../02-artifacts/file-activity/tmp-shm.md) |
| 7 | 셸 기록·웹 로그·인증 로그 | 어떻게 들어와 내려받았나 | [SSH 로 들어왔나](ssh-intrusion.md), [웹 서버가 뚫렸나](web-compromise.md) |
| 8 | 컨테이너 | 컨테이너 안에서 돈 경우 | [Docker](../../02-artifacts/containers/docker/index.md) |
| 9 | 해시·YARA | 알려진 채굴기인지 | [알려진 파일 대조와 YARA](../../03-techniques/analysis/hash-yara.md) |

### CPU 사용이 남는 곳

CPU 시간을 남기는 기록은 여러 곳에 있지만, 기록마다 다루는 범위와 남는 시점이 다릅니다.

| 기록 | 범위 | 남는 때 | 단위 |
|---|---|---|---|
| `/proc/PID/stat` 14·15번째 칸 `utime`·`stime` | 프로세스 하나 | 프로세스가 도는 동안 | 클록 틱(`sysconf(_SC_CLK_TCK)` 로 나눔)[2] |
| `/proc/PID/stat` 16·17번째 칸 `cutime`·`cstime` | 그 프로세스가 기다려 준 자식들 | 프로세스가 도는 동안 | 클록 틱[2] |
| `/proc/stat` 의 `cpu`·`cpuN` 줄 | 시스템 전체·CPU 하나 | 시스템이 도는 동안 | USER_HZ, 대부분 1/100초[2] |
| systemd 단위 자원 기록 | 서비스 단위 하나 | 단위가 멈추거나 실패할 때 | 나노초(`CPU_USAGE_NSEC=`)[1] |
| atop 기록 | 프로세스 하나 | atop 이 기록할 때마다 | 틱(`utime`·`stime`)[5] |
| 프로세스 회계 | 프로세스 하나 | 프로세스가 끝날 때 | 클록 틱(`ac_utime`·`ac_stime`)[2] |

`/proc/stat` 은 CPU 가 얼마나 바빴는지만 알려 주고 어느 프로세스가 썼는지는 알려 주지 않습니다. Velociraptor `Linux.Sys.CPUTime` 은 이 파일을 `user`·`nice`·`system`·`idle`·`iowait` 등의 칸으로 나눠 보여 줍니다[4]. 지금 도는 프로세스의 CPU 비율은 UAC 가 `ps -eo user,pid,ppid,pcpu,pmem,tty,stat,lstart,args` 와 `etime` 판, `top -b -n1` 으로 남깁니다[3].

**systemd 단위 자원 기록.** 서비스 단위가 `dead` 나 `failed` 상태로 들어가면 systemd 는 그 단위가 쓴 자원을 저널에 한 줄로 남깁니다[1]. 이 줄의 `MESSAGE_ID` 는 `ae8f7b866b0347b9af31fe1c80b127c0` 이고, 카탈로그 제목은 "Resources consumed by unit runtime" 입니다[1]. RHEL 9 의 systemd 소스 카탈로그에도 같은 항목이 있습니다[1]. 구조 필드로 `CPU_USAGE_NSEC=`, 단위 이름(시스템 단위는 `UNIT=`, 사용자 단위는 `USER_UNIT=`), 실행 ID(`INVOCATION_ID=` 또는 `USER_INVOCATION_ID=`)가 들어갑니다[1].

| systemd 판 | 메시지 모양 |
|---|---|
| 252(RHEL 9), 255(Ubuntu 24.04) | `이름.service: Consumed 5h 12min 3.418s CPU time.`[1] |
| 상류 main | 시작·끝 시각이 모두 있으면 `Consumed … CPU time over … wall clock time`, 없으면 `Consumed … CPU time`[1] |

메시지의 CPU 시간 뒤에는 집계가 켜진 다른 자원이 쉼표로 이어집니다. 255 판은 메모리 최대 사용량(`memory peak`)과 스왑 최대 사용량(`memory swap peak`)을, 252·255 판 모두 디스크 읽기·쓰기(`read … from disk`, `written … to disk`)와 IP 트래픽(`received … IP traffic`, `sent … IP traffic`)을 붙이고, 집계는 켜져 있지만 값이 0 이면 `no IO`, `no IP traffic` 으로 적습니다[1]. 줄의 수준은 기본 DEBUG 이고, 252·255 판은 CPU 시간이 1초를 넘거나 디스크 읽기·쓰기가 1MB 를 넘거나 IP 트래픽이 조금이라도 있으면 INFO, CPU 시간이 10분을 넘거나 디스크 읽기·쓰기가 10MB 를 넘거나 IP 트래픽이 128MB 를 넘으면 NOTICE 로 올립니다[1]. 상류 main 은 메모리 최대 사용량 기준(64MB, 512MB)을 더합니다[1]. 집계된 값이 하나도 없으면 줄을 남기지 않습니다[1].

```
# 만든 예시 (journalctl -o verbose 출력 가운데 이 줄의 필드 일부)
MESSAGE=cache-helper.service: Consumed 5h 12min 3.418s CPU time.
MESSAGE_ID=ae8f7b866b0347b9af31fe1c80b127c0
UNIT=cache-helper.service
CPU_USAGE_NSEC=18723418000000
```

저널에서는 `journalctl MESSAGE_ID=ae8f7b866b0347b9af31fe1c80b127c0` 로 이 줄만 모아 CPU 시간이 큰 단위를 찾습니다[7]. 저널은 항목을 받은 시각을 UTC 기준 epoch 뒤 마이크로초(`__REALTIME_TIMESTAMP=`)로 저장하고, `journalctl --utc` 로 UTC 로 볼 수 있습니다[7]. 이 줄의 시각은 단위가 `dead`·`failed` 상태로 들어간 때입니다. 상류 main 판의 `wall clock time` 은 단위가 비활성 상태를 벗어난 때부터 다시 들어간 때까지의 길이라서[1], 줄 시각에서 이 값을 빼면 시작 시각을 어림할 수 있습니다. 252·255 판에는 이 값이 없으므로 같은 단위의 시작 줄을 따로 찾습니다.

**atop 기록.** atop 이 설치돼 돌았다면 `/var/log/atop/atop_*` 파일에 프로세스 목록이 쌓입니다. dissect.target 의 `atop` 플러그인은 파일 첫 4바이트가 마법 수 `0xFEEDBEEF` 이고 판이 `2.6`·`2.7` 인 파일만 읽고, 그 밖의 판은 경고를 남기고 건너뜁니다[5]. 출력에는 프로세스 이름·`cmdline`·`pid`·`ppid`·`ruid`·`euid`·상태·종료 코드·경과 시간(`elaps`)·Docker 컨테이너 ID(`container`)가 들어가고, 레코드 시각 `ts` 는 프로세스 시작 시각(`btime`)입니다[5]. 파일 구조체에는 `utime`·`stime` 이 있지만 이 플러그인의 출력 레코드에는 들어가지 않습니다[5]. CPU 시간이 필요하면 atop 자체로 파일을 다시 읽습니다.

## 분석 흐름

1. **라이브이면 프로세스와 연결부터 뜹니다.** 프로세스 목록, `/proc` 정보, 소켓 목록을 수집하고 메모리를 뜹니다. 순서와 명령은 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md)을 따릅니다.

2. **CPU 시간이 큰 프로세스를 적습니다.** `ps` 의 `pcpu`, `/proc/PID/stat` 의 `utime`·`stime` 과 시작 시각으로 오래 CPU 를 쓴 프로세스를 고르고, `exe`·`cmdline`·`environ`·`cwd`·부모 PID 를 함께 적습니다. `exe` 가 ` (deleted)` 로 끝나면 실행 파일이 이미 지워졌다는 뜻이고, 프로세스가 도는 동안에는 `exe` 를 열어 파일을 건질 수 있습니다([실행 중인 프로세스 (/proc)](../../02-artifacts/execution/proc.md)). UAC 는 이런 프로세스의 실행 파일을 `recovered_exe` 로 떠 오고, 그 프로세스가 연 지워진 파일(`/dev/shm` 을 가리키는 것 포함)과 모든 프로세스에서 memfd 로 숨긴 지워진 파일도 목록을 만들어 앞 약 20MB 씩 떠 옵니다[3].

3. **연결 상대를 잇습니다.** 프로세스의 소켓 fd 를 `/proc/net/tcp` 등의 아이노드와 맞춥니다. Velociraptor `Linux.Network.Netstat` 은 `/proc/*/fd/*` 에서 소켓 아이노드를 모아 `/proc/net/tcp`·`/proc/net/tcp6` 의 연결과 잇고, 기본으로 상태 이름이 `LISTEN|ESTAB` 에 맞는 연결(Listening·Established)만 보여 줍니다[4].

4. **무엇이 띄웠는지 부모 사슬을 따라갑니다.** 부모가 cron, systemd, 웹 서버 계정의 프로세스, SSH 세션 가운데 무엇인지 봅니다. UAC 의 `ps -eo user,pid,ppid,cgroup` 출력은 프로세스가 속한 cgroup 을 보여 주므로[3] 서비스 단위나 컨테이너 소속을 가리는 데 씁니다. 단위 이름이 나오면 저널에서 그 단위의 시작·중지 줄과 `Consumed … CPU time` 줄을 찾습니다. 단위 파일의 위치와 만든 사람을 가리는 법은 [systemd 서비스와 타이머](../../02-artifacts/persistence/systemd-units.md)에 있습니다.

5. **이미 멈춘 채굴기를 찾습니다.** 라이브 증거가 없거나 지금 CPU 사용이 낮으면 저널의 단위 자원 기록, atop 기록, 프로세스 회계에서 과거에 CPU 를 많이 쓴 프로세스와 단위를 찾습니다. 파일 쪽에서는 `/tmp`·`/dev/shm`·`/var/tmp` 와 홈의 숨김 폴더를 봅니다([임시 폴더와 메모리 파일 시스템](../../02-artifacts/file-activity/tmp-shm.md)).

6. **실행 파일을 가립니다.** 건진 실행 파일과 실행 비트가 있는 파일의 해시를 대조하고, 프로세스 메모리에 YARA 를 돌립니다([알려진 파일 대조와 YARA](../../03-techniques/analysis/hash-yara.md)). Velociraptor `Linux.Detection.Yara.Process` 의 기본 규칙은 `velociraptor` 문자열을 찾는 예시일 뿐이라[4], 채굴기용 규칙을 따로 넣어야 합니다.

7. **다시 뜨는 장치를 찾습니다.** cron, systemd 타이머와 단위, 셸 시작 파일, `/etc/ld.so.preload` 를 봅니다([무엇이 계속 살아남게 했나](persistence-hunt.md)).

8. **들어온 경로를 찾습니다.** 채굴 바이너리가 처음 생긴 시각 앞뒤의 인증 로그, 웹 로그, 셸 기록을 봅니다([SSH 로 들어왔나](ssh-intrusion.md), [웹 서버가 뚫렸나](web-compromise.md)). 권한을 올린 흔적은 [권한을 올렸나](privilege-escalation.md)에서 다룹니다.

## 흔한 오판

- **지금 CPU 가 낮으니 채굴기가 없었다고 봅니다.** 채굴기를 멈췄거나 컨테이너로 옮겼을 수 있습니다. 과거 사용량은 단위 자원 기록, atop 기록, 프로세스 회계에 남고, 셋 다 조건이 맞아야 남습니다.
- **`Consumed … CPU time` 줄이 없으니 서비스로 돌리지 않았다고 봅니다.** 이 줄은 단위가 멈추거나 실패할 때만 남고, 집계 값이 없으면 남지 않으며, 어느 자원도 문턱을 넘지 않으면 DEBUG 수준이라 systemd 의 로그 수준 설정에 따라 남지 않을 수 있습니다[1]. 단위가 아직 돌고 있으면 줄이 아직 없습니다.
- **`ps` 에 안 보이니 없다고 봅니다.** `/etc/ld.so.preload` 로 사용자 공간 도구를 속이거나, `/proc/PID` 위에 다른 폴더를 마운트하거나, 커널 모듈로 숨길 수 있습니다([공유 라이브러리 가로채기](../../02-artifacts/persistence/ld-preload.md), [커널 모듈](../../02-artifacts/persistence/kernel-modules.md), [루트킷 찾기](../../03-techniques/analysis/rootkit-detection.md)). 메모리 이미지와 원시 파일 시스템 읽기로 교차 확인합니다.
- **`comm`·`cmdline` 의 이름을 그대로 믿습니다.** 프로세스는 자기 이름과 인수를 바꿀 수 있어서, 커널 스레드처럼 보이는 이름도 `exe` 가 가리키는 파일과 부모를 함께 봐야 합니다([실행 중인 프로세스 (/proc)](../../02-artifacts/execution/proc.md)).
- **` (deleted)` 를 곧바로 악성으로 봅니다.** 패키지 업데이트로 실행 파일을 바꿔 끼운 경우에도 붙습니다. 패키지 기록과 함께 봅니다.
- **`/proc/stat` 의 CPU 시간을 프로세스 하나의 것으로 읽습니다.** 이 값은 시스템 전체 또는 CPU 하나가 상태별로 쓴 시간입니다[2].
- **도구의 검색 범위를 확인하지 않습니다.** Velociraptor `Linux.Detection.AnomalousFiles` 의 기본 경로 `tmp/**` 는 앞에 `/` 가 없어서[4] 결과에 `/tmp` 가 빠졌을 가능성이 있습니다([임시 폴더와 메모리 파일 시스템](../../02-artifacts/file-activity/tmp-shm.md)).

## 보고서 문장 예

아래 값은 모두 만든 예시입니다(호스트 web01, 단위 `cache-helper.service`, 사용자 alice, 주소 198.51.100.40).

- "web01 의 저널에 2026-03-12 09:41:07 UTC, `cache-helper.service` 단위가 멈추면서 CPU 시간 5시간 12분 3.418초를 쓴 것으로 적힌 기록이 있습니다."
- "수집 시각 기준으로 PID 4242 가 UID 1001(alice)로 돌고 있었고, 실행 파일 경로는 `/dev/shm/.x/cache-helper (deleted)` 였으며, 198.51.100.40 과 연결된 소켓이 열려 있었습니다."
- "건져 낸 실행 파일의 SHA-256 은 `…` 이고, 이 값은 ○○ 해시 목록의 채굴 프로그램 항목과 같습니다." (실제로 대조했을 때만)

기록은 CPU 를 쓴 프로세스와 단위, 연결 상대, 실행 파일의 해시까지 보여 주지만, 채굴로 얻은 수익이나 채굴 풀 계정의 주인은 보여 주지 않습니다. "공격자가 채굴로 이익을 얻었다" 같은 문장은 시스템 밖의 증거 없이 쓰지 않습니다. 보고서 전체 구성은 [Linux 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)를 따릅니다.

## 함께 볼 페이지

- [실행 중인 프로세스 (/proc)](../../02-artifacts/execution/proc.md) — `stat`·`exe`·`maps` 구조와 ` (deleted)`
- [프로세스 회계](../../02-artifacts/execution/process-accounting.md) — 끝난 프로세스의 CPU 시간
- [systemd 서비스와 타이머](../../02-artifacts/persistence/systemd-units.md) — 서비스 단위 파일 위치
- [임시 폴더와 메모리 파일 시스템](../../02-artifacts/file-activity/tmp-shm.md) — `/tmp`·`/dev/shm`·memfd
- [무엇이 계속 살아남게 했나](persistence-hunt.md) — 다시 띄우는 장치 찾기
- [메모리 분석](../../03-techniques/analysis/memory-analysis.md)
- [타임라인 만들기](../../03-techniques/analysis/timeline.md)

## 참고 문헌

1. systemd, src/core/unit.c (main·v252·v255), src/systemd/sd-messages.h, catalog/systemd.catalog.in; systemd-rhel9 catalog/systemd.catalog.in. https://github.com/systemd/systemd/blob/main/src/core/unit.c , https://github.com/systemd/systemd/blob/v252/src/core/unit.c , https://github.com/systemd/systemd/blob/v255/src/core/unit.c , https://github.com/systemd/systemd/blob/main/src/systemd/sd-messages.h , https://github.com/systemd/systemd/blob/main/catalog/systemd.catalog.in , https://github.com/redhat-plumbers/systemd-rhel9/blob/main/catalog/systemd.catalog.in
2. man-pages, man5/proc.5, man5/acct.5. https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5 , https://github.com/mkerrisk/man-pages/blob/master/man5/acct.5
3. UAC, artifacts/live_response/process/ps.yaml·top.yaml·deleted.yaml, artifacts/files/system/tmp.yaml·dev_shm.yaml. https://github.com/tclahr/uac/blob/main/artifacts/live_response/process/ps.yaml , https://github.com/tclahr/uac/blob/main/artifacts/live_response/process/top.yaml , https://github.com/tclahr/uac/blob/main/artifacts/live_response/process/deleted.yaml , https://github.com/tclahr/uac/blob/main/artifacts/files/system/tmp.yaml , https://github.com/tclahr/uac/blob/main/artifacts/files/system/dev_shm.yaml
4. Velociraptor, Linux/Sys/CPUTime.yaml·Network/Netstat.yaml·Detection/Yara/Process.yaml·Detection/AnomalousFiles.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Sys/CPUTime.yaml , https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Network/Netstat.yaml , https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Detection/Yara/Process.yaml , https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Detection/AnomalousFiles.yaml
5. dissect.target, plugins/os/unix/log/atop.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/atop.py
6. CentOS Stream 9 systemd 패키지 systemd.spec, Ubuntu systemd 패키지(noble-updates) debian/changelog. https://gitlab.com/redhat/centos-stream/rpms/systemd/-/tree/c9s , https://git.launchpad.net/ubuntu/+source/systemd/tree/debian?h=ubuntu/noble-updates
7. systemd, man/systemd.journal-fields.xml, man/journalctl.xml. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml , https://github.com/systemd/systemd/blob/main/man/journalctl.xml
