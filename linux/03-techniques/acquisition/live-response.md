---
title: "라이브 응답 수집"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 910
---

# 라이브 응답 수집 (Live Response)

전원이 켜진 Linux 에서 끄면 사라지는 상태(프로세스·연결·마운트·커널 모듈)를 명령 결과와 `/proc` 사본으로 떠 두는 방법입니다.

## 언제 쓰나

라이브 응답 수집 (live response) 은 시스템을 끄거나 디스크를 떼기 전에 씁니다. 돌고 있는 프로세스, 열린 네트워크 연결, 지워졌지만 아직 실행 중인 실행 파일은 디스크 이미지에 남지 않고, 전원을 끄면 되살릴 수 없습니다. 서버를 멈출 수 없어 디스크 이미징을 뒤로 미뤄야 할 때도 라이브 응답 결과가 첫 판단 자료가 됩니다.

전체 조사 순서와 수집 전에 정할 일(권한, 기록, 휘발성 순서)은 [조사 절차](investigation-process.md)에 있습니다. 물리 메모리 덤프는 [메모리 수집](memory-acquisition.md)에서, 컨테이너 런타임 명령은 [컨테이너 수집](container-acquisition.md)에서, 클라우드 인스턴스는 [클라우드 가상 머신 수집](cloud-vm.md)에서 다룹니다. 이 쪽은 셸 명령과 `/proc` 로 뜨는 휘발성 상태만 다룹니다.

## 절차

아래 단계는 공개 수집 도구 UAC (Unix-like Artifacts Collector) 가 뜨는 항목을 대상별로 묶은 것입니다. UAC 는 휘발성 순서 (order of volatility) 대로 모으도록 짜여 있고[2], 실제 실행 순서는 `ir_triage` 프로필을 따릅니다. 이 프로필은 프로세스와 네트워크를 먼저 뜨고, 그다음 파일 메타데이터(bodyfile), 시스템 정보, 저장 장치, 로그·설정 파일 사본 순으로 넘어갑니다[2].

1. **결과를 둘 곳과 권한을 정합니다.** UAC 는 root 로 실행하는지 먼저 검사하고, `-u` (`--run-as-non-root`) 로 이 검사를 끄면 수집이 제한될 수 있습니다[2]. UAC 는 임시 디렉터리 `uac-data.tmp` 를 결과 목적지 아래에 만들고, `--temp-dir` 을 주면 그 아래에 만듭니다[2]. 목적지를 대상 시스템의 디스크로 잡으면 수집 과정이 그 디스크에 파일을 씁니다. 사건 정보는 `--case-number`, `--evidence-number`, `--description`, `--examiner`, `--notes` 로 넣습니다[2].

2. **시각 기준을 떠 둡니다.** 뒤에서 상대 시각을 벽시계 시각으로 바꾸려면 수집 시점의 시계 값이 필요합니다. UAC 는 `date`, `timedatectl status`, `hwclock`, `uptime`, `uptime -s` 결과를 `/live_response/system` 에 남깁니다[1]. `uptime -s` 는 시스템이 켜져 있던 기간을 시작 시각 하나로 보여 주고, 모양은 `yyyy-mm-dd HH:MM:SS` 입니다[1].

3. **프로세스를 뜹니다.** 목록은 `ps` 를 여러 형식으로 뜹니다. 시작 시각이 붙는 `ps -eo user,pid,ppid,pcpu,pmem,tty,stat,lstart,args`, 경과 시간이 붙는 `...,etime,args`, `ps auxwww`, `ps -ef`, 컨트롤 그룹(cgroup)이 붙는 `ps -eo user,pid,ppid,cgroup` 가 있습니다[1]. PID 마다 `/proc/PID/` 의 `cmdline`, `environ`, `comm`, `maps`, `mounts`, `stack`, `stat`, `status`, `net/unix`, `task/PID/children` 을 읽고 `fd`, `map_files` 목록을 뜹니다[1]. 실행 파일 경로는 `ls -l /proc/[0-9]*/exe` 로 뜨고, 같은 경로의 해시도 계산합니다[1]. 결과는 `/live_response/process` 와 PID 별 `/live_response/process/proc/PID/` 에 들어갑니다[1].

4. **ps 에 안 보이는 PID 를 찾습니다.** UAC 는 `/proc` 아래 숫자 디렉터리를 하나씩 `ps ax` 결과와 맞춰 보고, `ps` 에 없는 PID 를 `hidden_pids_for_ps_command.txt` 에 적습니다[1]. `ps ax` 가 없는 시스템(busybox 등)에서는 `ps` 로 대신 비교합니다[1].

5. **지워진 채 돌고 있는 실행 파일을 건집니다.** `/proc/PID/exe` 가 가리키는 파일이 지워졌으면 원래 경로 끝에 `(deleted)` 문자열이 붙습니다[3]. UAC 는 이런 PID 마다 `dd if=/proc/PID/exe of=recovered_exe bs=1024 count=20000` 으로 실행 파일을 복사합니다[1]. 이 프로세스가 열어 둔 지워진 파일과 `/dev/shm` 에 있던 지워진 파일도 `/proc/PID/fd/N` 에서 같은 방식으로 복사합니다[1]. memfd 에 숨은 지워진 파일은 실행 파일이 지워졌는지와 상관없이 모든 프로세스에서 찾아 복사합니다[1].

6. **열린 파일과 네트워크를 뜹니다.** 열린 파일은 `lsof -nPl`, `lsof -nPli`, `lsof -U` 로 뜹니다[1]. 소켓은 `ss -anp`, `ss -tanp`, `ss -uanp`, `ss -tlnp`, `ss -0bp` 등으로, 주소·라우팅·이웃은 `ip addr show`, `ip link show`, `ip route show`, `ip neighbor show` 로 뜹니다[1]. 도구 출력과 따로 `/proc/net/tcp`, `tcp6`, `udp`, `udp6` 원본도 복사합니다[1]. 방화벽 규칙은 `iptables -L -v -n`, `iptables -t nat -L -v -n`, `nft list ruleset` 으로 남깁니다[1]. 규칙 파일의 뜻은 [방화벽](../../02-artifacts/network/firewall.md)에서 다룹니다.

7. **커널 상태를 뜹니다.** `uname -a`, `lsmod`, `/proc/modules` 를 뜨고, 커널 오염 상태 (tainted) 는 `cat /proc/sys/kernel/tainted`, `dmesg | grep -i taint`, `grep "(.*)" /proc/modules` 로 확인합니다[1]. eBPF 는 `ls -la /sys/fs/bpf` 와 `bpftool prog list`, 프로그램별 `bpftool prog dump xlated`·`jited` 로 뜹니다[1]. 모듈 흔적의 해석은 [커널 모듈](../../02-artifacts/persistence/kernel-modules.md)에 있습니다.

8. **로그인·서비스·저장 장치를 뜹니다.** `who -T`, `journalctl --list-boots`, `systemctl list-units`, `systemctl list-timers --all`, `systemctl list-unit-files` 로 로그인 세션과 부팅 목록, 유닛 상태를 남깁니다[1]. 저장 장치는 `lsblk`(`-f`, `-J`, `-l`), `findmnt --ascii`, `findmnt -J`, `blkid`, `lvs` 로 뜹니다[1]. 이 결과는 뒤에 [디스크 이미징](disk-imaging.md)에서 어느 장치를 뜰지 정하는 근거가 됩니다.

9. **파일 메타데이터를 뜬 다음 파일을 복사합니다.** bodyfile 은 `/` 전체를 `stat` 으로 훑고 `proc` 파일 시스템은 뺍니다. 결과는 `/bodyfile/bodyfile.txt` 입니다[1]. 로그·설정 파일 사본은 그 뒤에 뜹니다[2]. 이 순서를 지키는 이유(파일을 읽는 동작이 접근 시각을 바꿀 수 있다는 점)는 [조사 절차](investigation-process.md)에 있습니다.

10. **결과물을 닫고 기록합니다.** UAC 는 결과물 옆에 `기본이름.log` 수집 기록을 만들고 `[Case Information]`, `[System Information]`, `[Acquisition Information]`, `[Output Information]`, `[Computed Hashes]` 절을 씁니다[2]. 기본 해시는 MD5 와 SHA1 이고[2], `-H` 를 주면 수집한 파일마다 해시 목록을 만듭니다[2]. 결과물 기본 이름은 `uac-%hostname%-%os%-%timestamp%` 입니다[2].

## 도구

| 도구 | 방식 | 참고 |
|---|---|---|
| UAC | 셸 스크립트, 설치 없이 실행, YAML 로 정의한 아티팩트를 프로필로 묶어 실행 | 결과는 tar(gzip 이 있으면 압축)·zip·none 중 고름[2] |
| Velociraptor `Linux.Sys.Pslist` | 에이전트가 프로세스 목록을 표로 반환 | Pid, Ppid, Name, CommandLine, Exe, Exe 해시, Username, CreateTime, RSS 를 주고, Exe 가 `(deleted)` 로 끝나면 Deleted 로 표시[5] |
| Velociraptor `Linux.Network.Netstat` | `/proc/net` 파일을 읽어 소켓 상태와 프로세스를 잇는 방식 | 기본으로 LISTEN 과 ESTAB 상태만 보여 줌[5] |
| Velociraptor `Linux.Triage.ProcessMemory` | 지정한 PID 의 프로세스 메모리를 서버로 올림 | 프로세스 하나 단위[5] |
| acquire (dissect) | 디스크 이미지나 라이브 시스템에서 모듈 단위로 수집 | OS 파일 읽기 대신 원시 디스크를 읽으려면 관리자 권한이 필요하고, `--fallback`·`--force-fallback` 으로 OS 읽기를 씀[6] |

UAC 의 `--start-date`·`--end-date` 는 수정·접근·변경 시각으로 파일을 거릅니다[2]. 기본 설정에서는 `find` 의 mtime·ctime 조건만 켜져 있고 atime 조건은 꺼져 있습니다[2].

## 함정과 한계

**복사 크기에 상한이 있습니다.** UAC 는 지워진 실행 파일과 지워진 열린 파일을 `bs=1024 count=20000` 로 복사하므로 앞쪽 20,480,000바이트까지만 남깁니다[1]. 이 상한은 `dd` 가 `/dev/null` 같은 잘못된 파일 설명자를 읽어 결과 파일이 끝없이 커지는 일을 막으려는 것입니다[1]. `/var/log` 사본도 파일 하나가 1GB(`max_file_size: 1073741824`)를 넘으면 빠집니다[1]. 결과에서 파일 크기가 이 값과 같거나 로그가 빠져 있으면 원본에서 다시 확인합니다.

**수집 도구도 흔적을 남깁니다.** UAC 는 결과 목록에서 자기 경로(`uac-data.tmp`, UAC 배포 디렉터리, `uac-호스트-…` 결과물)를 걸러 냅니다[2]. 걸러 낸 것은 결과 목록이고, 대상 시스템에는 도구 실행으로 생긴 프로세스·파일·로그가 남습니다. 이 흔적은 [타임라인](../analysis/timeline.md)에서 수집 시각대의 항목으로 따로 표시합니다.

**상태를 바꾸는 항목은 기본으로 꺼져 있습니다.** UAC 에서 `modifier: true` 로 표시한 아티팩트는 `--enable-modifiers` 를 줄 때만 돕니다[2]. 하나는 `sysctl -a` 를 저장한 뒤 `sysctl kernel.ftrace_enabled=0` 으로 ftrace 를 끄고, 목적은 LKM 루트킷이 시스템 호출을 가로채지 못하게 하는 것입니다[1]. 다른 하나(`revel_hidden_processes`)는 `mount`·`ps` 결과와 숨은 PID 목록을 먼저 저장한 뒤 `/proc/PID` 에 바인드 마운트된 디렉터리를 `umount` 해서, `/proc/PID` 를 가려 숨긴 프로세스를 드러냅니다[1]. `ps` 에 안 보이는 PID 가 있으면 `/live_response/modifiers/mount.txt` 나 `findmnt` 결과에서 `/proc/숫자` 위 마운트를 먼저 찾아볼 수 있습니다. 이 옵션을 켰다면 보고서에 적습니다.

**거짓 결과를 가려내는 범위가 좁습니다.** `ps`, `/proc`, `ss` 는 모두 대상 커널이 돌려준 값입니다. UAC 의 숨은 PID 비교는 `/proc` 목록을 믿고 `ps` 출력과 견주는 방식이라 사용자 공간 도구 쪽 은닉만 드러냅니다[1]. 커널 수준에서 `/proc` 자체를 가리는 경우는 이 비교로 드러나지 않을 가능성이 있고, [메모리 분석](../analysis/memory-analysis.md)이나 [루트킷 찾기](../analysis/rootkit-detection.md)로 넘겨 확인합니다.

**권한과 커널 설정에 따라 결과가 비기도 합니다.** `dmesg_restrict` 가 1 이면 `CAP_SYSLOG` 가 없는 사용자는 `dmesg` 를 읽지 못합니다[4]. 이런 시스템에서 root 가 아닌 계정으로 뜨면 `dmesg | grep -i taint` 결과가 비어 있어도 오염 기록이 없다는 뜻이 아닙니다. `/proc/PID/exe` 링크를 읽는 권한은 ptrace 접근 검사(`PTRACE_MODE_READ_FSCREDS`)를 따릅니다[3].

**결과물 이름의 시각에는 시간대가 없습니다.** 결과물 이름의 `%timestamp%` 는 `date "+%Y%m%d%H%M%S"` 값이라 대상 시스템의 현지 시각이고 시간대 표시가 없습니다[2]. 수집 기록의 `Acquisition Started`·`Acquisition Finished` 는 `date "+%a %b %d %H:%M:%S %Y %z"` 형식이라 UTC 와의 차이가 붙습니다[2]. 수집 시각은 수집 기록 쪽 값을 씁니다.

**zip 암호가 수집 기록에 남습니다.** zip 형식에 `-P` 로 암호를 주면 UAC 는 그 암호를 수집 기록의 `[Output Information]` 절에 `Password:` 줄로 적습니다[2]. 결과물과 수집 기록을 같은 곳에 두면 암호를 건 의미가 사라집니다.

## 결과를 어떻게 해석하나

### 증명하는 것

- 수집한 시점에 돌던 프로세스, 열려 있던 소켓과 파일, 마운트, 올라가 있던 커널 모듈과 eBPF 프로그램의 목록입니다.
- `/proc/PID/exe` 끝의 `(deleted)` 는 그 프로세스가 실행한 파일의 경로가 수집 시점에 파일 시스템에서 지워져 있었다는 뜻입니다[3]. 복사한 `recovered_exe` 는 지워진 파일의 내용을 담습니다.
- `tainted` 값은 0 이 아니면 커널이 오염되었다는 뜻이고, 오염 이유를 비트로 알려 줍니다. 모듈과 관련된 비트로 4096 (O) 은 트리 밖에서 빌드한 모듈, 8192 (E) 는 서명 없는 모듈, 2 (F) 는 강제로 올린 모듈, 1 (P) 은 독점 모듈입니다[4]. 값은 여러 비트를 더한 것이라, 예를 들어 12288(만든 예시)은 4096 + 8192 로 O 와 E 가 함께 선 상태입니다.

### 증명하지 못하는 것

- 수집 전에 끝난 프로세스와 닫힌 연결은 결과에 없습니다. 이것들은 로그와 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 같은 디스크 기록에서 찾습니다.
- `/proc/PID/environ` 은 프로그램이 `execve` 로 시작할 때 정해진 처음 환경 변수입니다. 실행 중에 프로세스가 환경을 바꿨으면 그 변경은 이 파일에 없습니다[3].
- `(deleted)` 는 누가 언제 파일을 지웠는지 알려 주지 않습니다. 지운 시각은 bodyfile 의 부모 디렉터리 시각과 파일 시스템 기록으로 좁힙니다.
- `tainted` 비트는 오염 이유의 종류만 알려 주고, 모듈 이름과 시각은 알려 주지 않습니다. 이름은 `grep "(.*)" /proc/modules` 결과와 [커널 로그](../../02-artifacts/system-info/kernel-log.md)에서 찾습니다.

### 시각 해석

`/proc/PID/stat` 의 22번째 필드 `starttime` 은 부팅 뒤 프로세스가 시작하기까지 걸린 시간이고, Linux 2.6 부터는 클럭 틱 단위라 `sysconf(_SC_CLK_TCK)` 값으로 나눠 초로 바꿉니다[3]. `/proc/uptime` 의 첫 값은 부팅 뒤 흐른 초(서스펜드 시간 포함)입니다[3]. 둘 다 상대 시각이라, 벽시계 시각으로 바꾸려면 같은 수집에서 뜬 `date` 결과가 있어야 합니다.

아래는 만든 예시입니다. `date` 가 2026-03-10 09:00:00 +0900 이고 `/proc/uptime` 첫 값이 86400.00 이면 부팅 시각은 2026-03-09 09:00:00 +0900 입니다. 어떤 프로세스의 `starttime` 이 360000 이고 클럭 틱이 100 이면 부팅 뒤 3600초에 시작했으므로 시작 시각은 2026-03-09 10:00:00 +0900 입니다. `date` 와 `/proc/uptime` 은 서로 다른 순간에 읽으므로 이렇게 구한 값은 두 명령 사이의 간격만큼 어긋날 수 있습니다. `uptime -s` 결과와 견줘 부팅 시각이 맞는지 확인합니다.

대상 시스템의 시계가 틀렸으면 `date`, `ps` 의 `lstart`, `uptime -s` 가 모두 같은 만큼 틀립니다. `hwclock` 과 `timedatectl status` 결과를 함께 보고, 수집하는 쪽 기록(작업 일지의 시각)과 차이를 적어 둡니다. 시각 전반의 정리는 [타임라인](../analysis/timeline.md)에 있습니다.

### 보고서 문장

기록이 말하는 만큼만 씁니다. "악성 프로세스가 실행되었다" 가 아니라 "2026-03-10 09:00 +0900 에 수집한 프로세스 목록에서 PID 4242 의 실행 파일 경로가 `/tmp/.cache/x (deleted)` 로 표시되었다(만든 예시)" 처럼 씁니다. 복사한 파일은 해시와 함께 "처음 20,480,000바이트까지 복사했다" 는 한계를 붙여 적습니다.

`/proc` 각 파일의 형식과 필드는 [실행 중인 프로세스 (/proc)](../../02-artifacts/execution/proc.md)에서 다룹니다. 다른 운영체제의 수집 절차는 [Windows 조사 절차](https://urock-ailab.github.io/forensics-handbook-windows/03-techniques/process-acquisition/investigation-process.html)와 [macOS 조사 절차](https://urock-ailab.github.io/forensics-handbook-mac/03-techniques/process-acquisition/investigation-process.html)에 있습니다.

## 참고 문헌

1. tclahr, UAC — 아티팩트 정의 `artifacts/live_response/` (process, network, system, storage, modifiers), `artifacts/bodyfile/bodyfile.yaml`, `artifacts/files/logs/var_log.yaml`. https://github.com/tclahr/uac/tree/main/artifacts
2. tclahr, UAC — `README.md`, `profiles/ir_triage.yaml`, `config/uac.conf`, `uac` 스크립트, `lib/usage.sh`, `lib/create_acquisition_log.sh`. https://github.com/tclahr/uac
3. Linux man-pages, `proc(5)` (`/proc/[pid]/environ`, `/proc/[pid]/exe`, `/proc/[pid]/stat`, `/proc/uptime`). https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
4. Linux kernel, `Documentation/admin-guide/sysctl/kernel.rst` (`dmesg_restrict`, `tainted`). https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/sysctl/kernel.rst
5. Velociraptor, `Linux.Sys.Pslist`, `Linux.Network.Netstat`, `Linux.Triage.ProcessMemory` 아티팩트 정의. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Sys/Pslist.yaml , https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Network/Netstat.yaml , https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Triage/ProcessMemory.yaml
6. Fox-IT, acquire `README.md`. https://github.com/fox-it/acquire/blob/main/README.md
