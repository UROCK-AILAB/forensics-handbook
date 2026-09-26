---
title: "공유 라이브러리 가로채기"
parent: "아티팩트 · 지속성"
nav_order: 540
---

# 공유 라이브러리 가로채기 (LD_PRELOAD·ld.so.preload)

동적 링커가 프로그램보다 먼저 싣는 공유 라이브러리 목록은 환경 변수 `LD_PRELOAD` 와 파일 `/etc/ld.so.preload` 에 들어가고, 이 쪽은 그 목록이 어디에 남고 실제로 실렸는지를 어떻게 확인하는지 다룹니다.

## 무엇을 기록하나 · 왜 생기나

동적 링커 (dynamic linker) `ld-linux.so*` 는 프로그램이 쓰는 공유 객체 (shared object) 를 찾아 싣고 프로그램을 준비한 뒤 실행합니다[1]. 컴파일할 때 `-static` 을 주지 않은 Linux 바이너리는 모두 이 과정을 거칩니다[1]. 미리 싣기 (preload) 는 이 과정에서 다른 모든 공유 객체보다 먼저 지정한 객체를 싣는 기능이고, 다른 공유 객체의 함수를 골라서 덮어쓰는 데 쓸 수 있습니다[1].

미리 실을 객체를 정하는 방법은 세 가지이고, 동적 링커는 아래 순서로 처리합니다[1].

| 순서 | 방법 | 적용 범위 |
|---|---|---|
| 1 | 환경 변수 `LD_PRELOAD` | 그 변수를 물려받은 프로세스. 자식이 새 프로그램을 실행해도 이어짐 |
| 2 | 동적 링커를 직접 부를 때 `--preload` 옵션(glibc 2.30 부터) | 그 실행 파일 하나. 자식 프로세스에는 이어지지 않음 |
| 3 | 파일 `/etc/ld.so.preload` | 시스템에서 실행하는 모든 프로그램 |

`/etc/ld.so.preload` 는 시스템 전체에 적용되므로 보통은 쓰지 않고, 라이브러리 설정 문제를 임시로 피하는 급한 경우에만 씁니다[1]. 그래서 이 파일이 있으면 누가 언제 왜 만들었는지부터 확인합니다. `LD_PRELOAD` 루트킷이 이 파일을 숨기는 경우까지 대비해서, 수집 도구는 이 파일을 따로 모읍니다[4][5].

`LD_PRELOAD` 는 파일이 아니라 프로세스 환경이라 전원을 끄면 사라집니다. 디스크 이미지에서는 이 변수를 넣는 설정 자리를 찾아야 하고, 라이브 시스템과 메모리에서는 프로세스마다 남은 환경을 봅니다.

## 위치와 버전별 차이

| 흔적 | 위치 | 이미지·라이브 |
|---|---|---|
| 시스템 전체 목록 | `/etc/ld.so.preload`[1][4] | 둘 다 |
| 목록에 적힌 공유 객체 | 목록이 가리키는 `.so` 경로 | 둘 다 |
| 프로세스의 처음 환경 | `/proc/PID/environ`[2] | 라이브 |
| 프로세스에 실제로 매핑된 파일 | `/proc/PID/maps`[2] | 라이브 |
| 서비스에 넣은 환경 | 유닛 파일의 `Environment=`·`EnvironmentFile=`[10] | 둘 다 |
| systemd 관리자 환경 | `systemctl show-environment` 출력[11] | 라이브 |
| 로그인 때 넣는 환경 | `/etc/environment`, `/etc/security/pam_env.conf`, `$HOME/.pam_environment`(pam_env)[12] | 둘 다 |
| 셸이 읽는 시작 파일 | `.bashrc`·`/etc/profile` 등 | 둘 다 |

`$HOME/.pam_environment` 는 pam_env 의 `user_readenv` 옵션이 켜져 있을 때만 읽고, 이 옵션의 기본값은 꺼짐입니다[12]. pam_env 가 어느 PAM 스택에 들어 있는지는 [PAM 모듈 변조](pam-backdoor.md)에서, 셸이 파일을 읽는 순서는 [셸 시작 파일](shell-startup.md)에서, 유닛 파일 자리는 [systemd 서비스와 타이머](systemd-units.md)에서 다룹니다.

## 구조

`/etc/ld.so.preload` 는 ELF 공유 객체 경로를 공백(빈칸·줄바꿈)으로 나눠 적은 텍스트 파일입니다[1]. 머리 부분이나 시각 값 같은 구조는 따로 없습니다.

`LD_PRELOAD` 값은 공백이나 콜론으로 나눈 목록이고, 구분 문자를 이스케이프하는 방법은 없습니다[1]. 동적 링커는 목록을 왼쪽부터 찾아 싣고, 이름 안의 `$ORIGIN`·`$LIB`·`$PLATFORM` 토큰을 풀어 씁니다[1]. 두 방법을 함께 쓰면 `LD_PRELOAD` 의 객체를 먼저 싣습니다[1].

`/proc/PID/environ` 은 프로세스가 `execve` 로 시작할 때 받은 처음 환경을 담고, 항목마다 널 바이트(`00`)로 나눕니다[2]. 프로세스가 시작한 뒤 `putenv` 등으로 환경을 바꾸면 이 파일에는 반영되지 않습니다[2].

`/proc/PID/maps` 는 한 줄에 매핑 하나씩 `address perms offset dev inode pathname` 순서로 적습니다[2]. 파일에 기댄 매핑인데 그 파일이 지워졌으면 경로 끝에 ` (deleted)` 가 붙습니다[2].

보안 실행 모드 (secure-execution mode) 에서는 동적 링커가 일부 환경 변수를 무시하고 환경에서 지웁니다[1]. 보조 벡터의 `AT_SECURE` 값이 0 이 아니면 이 모드이고, set-user-ID·set-group-ID 프로그램처럼 실제 ID 와 유효 ID 가 다를 때, root 가 아닌 사용자가 권한(capabilities)을 주는 바이너리를 실행할 때, LSM 이 값을 정했을 때가 여기에 해당합니다[1]. 이 모드에서 `LD_PRELOAD` 의 슬래시가 든 경로는 무시하고, 표준 검색 디렉터리에 있으면서 set-user-ID 비트가 켜진 객체만 미리 싣습니다[1].

## 증거로서 의미

**증명하는 것**

- `/etc/ld.so.preload` 에 경로가 적혀 있으면, 그 파일이 있던 동안 시작한 동적 링크 프로그램은 그 객체를 먼저 싣도록 설정돼 있었습니다[1].
- `/proc/PID/environ` 이나 메모리의 환경에 `LD_PRELOAD=` 가 있으면, 그 프로세스가 시작할 때 이 값을 받았습니다[2][9].
- `/proc/PID/maps` 나 Volatility `linux.library_list` 에 그 경로가 보이면, 그 객체가 그 프로세스의 주소 공간에 실제로 실려 있었습니다[2][9].

**증명하지 못하는 것**

- 설정만으로는 모든 프로세스에 실렸다고 말할 수 없습니다. `-static` 바이너리는 동적 링커를 거치지 않고[1], 보안 실행 모드의 프로그램은 `LD_PRELOAD` 의 경로를 무시합니다[1].
- 라이브 시스템에서 `cat /etc/ld.so.preload` 가 아무것도 돌려주지 않아도 파일이 없다고 할 수 없습니다. 미리 실린 루트킷 라이브러리가 이 파일을 숨길 수 있어서, UAC 는 파일 시스템을 직접 읽는 방식으로 이 파일을 다시 꺼냅니다[5].
- 누가 파일을 만들었는지, 라이브러리가 무엇을 했는지는 이 흔적만으로 알 수 없습니다. 작성자는 감사 로그·인증 로그와, 동작은 라이브러리 파일 자체를 분석해서 따로 확인합니다.

보고서에는 "이 시각 이후 `/etc/ld.so.preload` 에 이 경로가 적혀 있었고, 수집 시점에 PID 1234 프로세스의 매핑에 같은 파일이 있었다" 처럼 기록이 말하는 만큼만 씁니다(만든 예시).

## 시각 해석

`/etc/ld.so.preload` 와 목록의 `.so` 파일에는 이 목록만의 시각 값이 없고, 파일 시스템의 아이노드 시각을 씁니다. mtime 은 내용을 쓸 때, ctime 은 내용을 쓰거나 소유자·권한·링크 수 같은 아이노드 정보를 바꿀 때 바뀌고, 생성 시각(btime)은 만들 때 정한 뒤 바뀌지 않습니다[3]. 이 값들은 UTC 기준 epoch 에서 센 값이라 시간대가 붙지 않습니다[3]. 생성 시각을 어디에 두는지는 [ext4](../../01-foundations/filesystem/ext4/index.md)·[XFS](../../01-foundations/filesystem/xfs.md) 쪽에서, 값 읽는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

dissect 의 `environ` 기록에 붙는 `ts` 는 procfs 의 `environ` 파일 수정 시각입니다[7]. procfs 가 내는 값이라서 환경 변수를 넣은 시각으로 읽지 않습니다. 프로세스가 언제 시작했는지는 [실행 중인 프로세스](../execution/proc.md)에서 다룹니다.

## 함정과 한계

- 라이브 수집 도구도 동적 링크 프로그램이면 `/etc/ld.so.preload` 의 영향을 받습니다. 라이브 결과는 디스크 이미지나 파일 시스템 직접 읽기 결과와 맞춰 봅니다[1][5].
- UAC 는 ext 계열이면 `debugfs`, XFS 면 `xfs_db` 로 장치를 직접 읽어 `/etc/ld.so.preload` 를 꺼내고, `stat` 결과를 따로 남깁니다[5]. 다른 파일 시스템에서는 이 방식이 돌지 않습니다[5].
- `/proc/PID/environ` 은 처음 환경만 보여 주므로, 프로세스가 시작한 뒤 넣거나 지운 변수는 나타나지 않습니다[2].
- Volatility `linux.envars` 는 프로세스 메모리 구조(`mm`)의 `env_start`~`env_end` 영역을 읽는데, 영역 크기가 0 이거나 8192바이트를 넘거나 읽을 수 없는(스왑된) 프로세스는 건너뛰고, `=` 가 없는 항목을 만나면 그 프로세스의 나머지를 읽지 않습니다[9].
- 미리 싣기만 라이브러리를 가로채는 길이 아닙니다. `LD_AUDIT` 도 다른 모든 객체보다 먼저 감사용 객체를 싣고[1], 패키지가 설치한 라이브러리를 바꿔치기할 수도 있습니다. 바꿔치기는 [패키지 파일 변조 확인](../packages/package-verify.md)으로 찾습니다.
- 목록의 `.so` 파일을 지우고 실행 중인 프로세스만 남겨 둘 수 있습니다. 이때 maps 경로 끝에 ` (deleted)` 가 붙습니다[2].

## 직접 분석해 보기

### 헥스로 한 번

`/etc/ld.so.preload` 는 텍스트라서 헥스로 보면 경로 바이트와 줄바꿈(`0a`)만 있습니다. 아래는 경로 하나를 적은 파일을 형식대로 만든 예시입니다.

```text
00000000: 2f75 7372 2f6c 6f63 616c 2f6c 6962 2f6c  /usr/local/lib/l
00000010: 6962 6578 616d 706c 652e 736f 0a         ibexample.so.
```

공백 대신 널 바이트나 보이지 않는 문자가 섞여 있으면 화면 출력과 실제 내용이 다를 수 있으므로, 목록을 판단할 때는 헥스로 봅니다.

`/proc/PID/environ` 을 그대로 떠서 보면 항목 사이에 `00` 이 있습니다[2]. 아래는 형식대로 만든 예시입니다.

```text
00000000: 484f 4d45 3d2f 726f 6f74 004c 445f 5052  HOME=/root.LD_PR
00000010: 454c 4f41 443d 2f75 7372 2f6c 6f63 616c  ELOAD=/usr/local
00000020: 2f6c 6962 2f6c 6962 6578 616d 706c 652e  /lib/libexample.
00000030: 736f 00                                  so.
```

`LD_PRELOAD=` 뒤부터 다음 `00` 까지가 값입니다. 이 값을 같은 프로세스의 maps 에서 찾아, 설정만 있었는지 실제로 실렸는지를 가릅니다.

### 공개 도구로 한 번

- ForensicArtifacts 의 `LinuxLoaderSystemPreloadFile` 은 `/etc/ld.so.preload` 하나를 가리키는 정의라서, 이 정의를 쓰는 수집 도구로 이미지에서 파일을 모읍니다[4].
- UAC 는 `chkrootkit/hidden_etc_ld_so_preload.yaml` 로 파일 시스템을 직접 읽은 `etc_ld_so_preload.txt` 와 `stat_etc_ld_so_preload.txt` 를 남기고[5], `live_response/process/procfs_information.yaml` 로 프로세스마다 `maps.txt` 와 `environ.txt` 를 `live_response/process/proc/PID/` 아래에 남깁니다[6].
- Velociraptor `Linux.Sys.Maps` 는 `/proc/PID/maps` 를 읽어 `Filename` 과 지워진 파일 여부 `Deleted` 를 줍니다[8].
- dissect `environ` 은 프로세스마다 `pid`·`variable`·`content` 를 내므로, `variable` 이 `LD_PRELOAD` 인 기록만 거르면 됩니다[7].
- 메모리 이미지에서는 Volatility 3 로 봅니다[9].

```text
vol -f memory.lime linux.envars
vol -f memory.lime linux.library_list --pids 1234
```

`linux.envars` 는 `PID`·`PPID`·`COMM`·`KEY`·`VALUE` 열을 내고, `linux.library_list` 는 ELF 링크 맵을 따라 `Name`·`Pid`·`LoadAddress`·`Path` 열을 냅니다[9]. 메모리 분석 절차는 [메모리 분석](../../03-techniques/analysis/memory-analysis.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 확인할 것 |
|---|---|
| [실행 중인 프로세스](../execution/proc.md) | 목록의 `.so` 가 어느 프로세스에 실렸고 그 프로세스가 언제 시작했는가 |
| [셸 시작 파일](shell-startup.md)·[systemd 서비스와 타이머](systemd-units.md)·[PAM 모듈 변조](pam-backdoor.md) | `LD_PRELOAD` 를 넣는 설정이 어디에 있는가 |
| [패키지 파일 변조 확인](../packages/package-verify.md) | `/etc/ld.so.preload`·`.so` 가 패키지 소속인가, 라이브러리가 바뀌었는가 |
| [감사 로그의 파일 감시](../file-activity/auditd-watches.md) | 파일을 쓴 계정과 프로세스가 남았는가 |
| [루트킷 찾기](../../03-techniques/analysis/rootkit-detection.md) | 숨김이 있는지 라이브·이미지 결과를 맞춰 보는 방법 |
| [라이브 응답 수집](../../03-techniques/acquisition/live-response.md) | 수집 도구 자신이 영향을 받지 않게 모으는 순서 |

지속성 흔적 전체를 한 번에 훑는 흐름은 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md)에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 Linux 침해 이미지나 메모리 이미지로 아래 질문을 풀어 봅니다.

1. `/etc/ld.so.preload` 가 있는가. 있다면 적힌 경로를 헥스로 보고, 공백이 아닌 구분 문자가 섞였는지 확인합니다.
2. 목록의 `.so` 파일과 `/etc/ld.so.preload` 의 mtime·ctime·생성 시각은 서로 어떤 순서인가. 같은 시간대에 다른 지속성 흔적이 생겼는가.
3. 목록의 `.so` 가 어느 패키지에도 속하지 않는가.
4. 메모리 이미지가 있으면 `linux.envars` 에서 `LD_PRELOAD` 를 받은 프로세스를 찾고, `linux.library_list` 에서 같은 경로가 실렸는지 봅니다.
5. `LD_PRELOAD` 값을 넣은 설정이 유닛 파일·pam_env 파일·셸 시작 파일 가운데 어디에 있는가.

## 참고 문헌

1. Linux man-pages, ld.so(8) — https://github.com/mkerrisk/man-pages/blob/master/man8/ld.so.8
2. Linux man-pages, proc(5) (/proc/[pid]/environ, /proc/[pid]/maps) — https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
3. Linux man-pages, inode(7) — https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
4. ForensicArtifacts, artifacts/data/linux.yaml (LinuxLoaderSystemPreloadFile) — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
5. UAC, artifacts/chkrootkit/hidden_etc_ld_so_preload.yaml·bin/linux/linux_dump_etc_ld_so_preload.sh — https://github.com/tclahr/uac/blob/main/artifacts/chkrootkit/hidden_etc_ld_so_preload.yaml , https://github.com/tclahr/uac/blob/main/bin/linux/linux_dump_etc_ld_so_preload.sh
6. UAC, artifacts/live_response/process/procfs_information.yaml — https://github.com/tclahr/uac/blob/main/artifacts/live_response/process/procfs_information.yaml
7. dissect.target, plugins/os/unix/linux/environ.py — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/environ.py
8. Velociraptor, artifacts/definitions/Linux/Sys/Maps.yaml — https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Sys/Maps.yaml
9. Volatility 3, plugins/linux/envars.py·library_list.py — https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/envars.py , https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/library_list.py
10. systemd, systemd.exec(5) (Environment=, EnvironmentFile=) — https://github.com/systemd/systemd/blob/main/man/systemd.exec.xml
11. systemd, systemctl(1) (show-environment) — https://github.com/systemd/systemd/blob/main/man/systemctl.xml
12. Linux-PAM, pam_env(8) — https://github.com/linux-pam/linux-pam/blob/master/modules/pam_env/pam_env.8.xml
