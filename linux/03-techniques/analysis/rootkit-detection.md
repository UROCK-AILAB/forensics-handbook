---
title: "루트킷 찾기"
parent: "기법 · 분석"
nav_order: 1000
---

# 루트킷 찾기 (Rootkit Detection)

같은 대상(모듈·프로세스·파일)을 서로 다른 출처에서 따로 뽑아 맞춰 보고, 어느 한 출처에서만 빠진 항목을 숨김의 흔적으로 읽는 절차입니다.

## 언제 쓰나

라이브 응답 결과에 `ps` 에 없는 PID 가 있거나, taint 값이 0 이 아니거나, `/etc/ld.so.preload` 가 있거나, 지워진 실행 파일로 도는 프로세스가 있으면 이 절차로 넘어옵니다. 침해 조사에서 로그와 명령 기록이 비어 있는데 네트워크 쪽 증거는 뚜렷할 때도 커널 수준 은닉을 한 번 확인해 둡니다.

루트킷은 어디서 도는지에 따라 두 갈래로 나뉩니다. 사용자 공간 루트킷 (user-space rootkit) 은 관리 도구를 바꿔치기하거나 라이브러리 함수를 가로채서 사용자와 관리자에게서 숨지만, 메모리 이미지를 보는 분석가에게서는 숨지 못합니다[1]. 커널 공간 루트킷 (kernel-space rootkit) 은 대부분 적재 가능한 커널 모듈 (Loadable Kernel Module, LKM) 로 심고, 숨는 방법은 다시 둘로 갈립니다[1].

- **함수 후킹 (function hooking)** — 커널 함수를 공격자의 코드로 바꿔 돌게 합니다. 예를 들어 `read` 시스템 호출을 가로채 `/proc/modules` 를 읽을 때 자기 줄을 빼는 식입니다[1].
- **커널 객체 직접 조작 (Direct Kernel Object Manipulation, DKOM)** — 커널 메모리의 자료 구조를 직접 고칩니다. 모듈 목록은 `/proc/modules` 의 내용을 채우는 목록이라, 여기서 자기 항목을 빼면 `/proc/modules` 를 비롯해 이 목록에 기대는 모든 곳에서 사라집니다[1].

eBPF 로 커널 모듈 없이 후킹과 비슷한 기능을 만드는 흐름도 있습니다[1]. 이 경우는 모듈을 비교해서는 드러나지 않으므로 따로 봅니다.

교차 비교 (cross-view) 는 같은 대상을 여러 출처에서 모아 서로 어긋나는 곳을 찾는 방법이고, DKOM 을 잘 잡습니다[1]. 대신 숨기지 않은 자원은 찾지 못하고, 검사하는 모든 출처에서 지운 자원도 찾지 못합니다[1]. 그래서 이 절차는 층마다 비교할 출처를 바꿔 가며 되풀이합니다.

| 숨는 층 | 숨는 방법 | 드러내는 비교 | 자세한 쪽 |
|---|---|---|---|
| 사용자 공간 | 바꾼 `ps`, `/etc/ld.so.preload` 로 미리 실은 라이브러리 | 커널이 준 값(`/proc`) ↔ 도구 출력, 파일 시스템 직접 읽기 ↔ 일반 읽기 | [실행 중인 프로세스](../../02-artifacts/execution/proc.md), [공유 라이브러리 가로채기](../../02-artifacts/persistence/ld-preload.md) |
| 커널, 함수 후킹 | 시스템 호출·ftrace·tracepoint 가로채기 | 호출 표와 콜백 주소 ↔ 커널 심볼 | 이 쪽 절차 6 |
| 커널, DKOM | 모듈 목록·kset 에서 자기 항목 빼기 | 메모리의 모듈 출처끼리 | 이 쪽 절차 5, [커널 모듈](../../02-artifacts/persistence/kernel-modules.md) |
| eBPF | 모듈 없이 커널에 프로그램 싣기 | eBPF 프로그램 목록 ↔ 고정 파일·성능 이벤트 | 이 쪽 절차 7 |

## 절차

1. **상태를 바꾸지 않는 수집을 먼저 끝냅니다.** 라이브 응답과 메모리 수집 순서는 [라이브 응답 수집](../acquisition/live-response.md) 과 [메모리 수집](../acquisition/memory-acquisition.md) 을 따릅니다. UAC 의 수정자 (modifier) 두 개는 시스템 상태를 바꿉니다[5]. `revel_hidden_processes` 는 `mount`, `ps`, `ps auxwww`, `ps auxwwwf`, `ps -ef` 결과를 먼저 남긴 뒤 `/proc/PID` 에 바인드 마운트된 디렉터리를 `umount` 하고, `disable_ftrace` 는 `sysctl -a` 를 남긴 뒤 `sysctl kernel.ftrace_enabled=0` 으로 ftrace 를 끕니다[5]. 목적은 가려진 프로세스를 드러내고 LKM 루트킷의 시스템 호출 후킹을 막는 것입니다[5]. 이 둘을 쓴다면 메모리를 먼저 뜨고, 수행한 명령과 시각을 기록에 남깁니다.

2. **taint 값을 봅니다.** UAC 는 `cat /proc/sys/kernel/tainted`, `dmesg | grep -i taint`, `grep "(.*)" /proc/modules` 를 받습니다[5]. 값이 0 이 아니면 비트마다 뜻을 풀고, 비트 표는 [커널 로그](../../02-artifacts/system-info/kernel-log.md) 에, 모듈과 관련된 비트와 적재 메시지는 [커널 모듈](../../02-artifacts/persistence/kernel-modules.md) 에 있습니다. 원인이 된 모듈을 빼도 taint 는 남습니다[6]. 이 값은 까닭별 비트를 모은 값이라 "그 부팅 동안 그런 종류의 일이 있었다" 는 신호일 뿐이고 어느 모듈인지는 알려 주지 않습니다[6]. 모듈 때문에 걸린 taint 는 `/proc/modules` 의 그 모듈 줄에 괄호 표시로 붙으므로, 위의 `grep` 결과로 모듈을 좁힙니다[5].

3. **라이브에서 두 목록을 맞춰 봅니다.** `revel_hidden_processes` 수정자를 켜면 UAC 는 `/proc` 아래 숫자 디렉터리를 하나씩 `ps ax` 결과와 견주어, `ps` 에 없는 PID 를 `hidden_pids_for_ps_command.txt` 에 적습니다[5]. 같은 수정자가 남긴 `mount.txt` 에 `/proc/숫자` 에 바인드 마운트한 줄이 있으면 프로세스 디렉터리를 가린 흔적일 가능성이 있습니다[5]. 모듈은 `ls -la /sys/module` 결과를 `/proc/modules`·`lsmod` 와 맞춰 봅니다[5]. `/proc/modules` 는 모듈 목록 (module list) 을, `/sys/module` 의 폴더는 `module_kset` 을 따라 만듭니다[1]. 그래서 이 비교는 모듈 목록에서만 빠진 모듈을 드러낼 수 있지만, kset 까지 고친 루트킷은 두 곳에서 함께 사라집니다[1].

4. **파일은 파일 시스템을 직접 읽어 확인합니다.** 미리 실린 루트킷 라이브러리는 파일 읽기 함수를 가로채 `/etc/ld.so.preload` 를 숨길 수 있어서, UAC 는 ext 계열이면 `debugfs`, XFS 면 `xfs_db` 로 이 파일을 직접 꺼내고 `stat` 결과도 따로 남깁니다[5]. 일반 `cat` 결과와 이 결과가 다르면 사용자 공간 가로채기가 있다는 뜻입니다. 디스크 이미지를 분석 PC 에서 읽으면 대상 시스템의 가로채기를 거치지 않으므로, 이미지 쪽 파일 목록과 라이브 목록을 맞춰 보는 것도 같은 비교가 됩니다. 이 파일의 해석은 [공유 라이브러리 가로채기](../../02-artifacts/persistence/ld-preload.md) 에서 다룹니다.

5. **메모리에서 모듈 출처를 맞춰 봅니다.** Volatility 3 의 `linux.lsmod` 는 모듈 목록을 읽습니다[4]. `linux.malware.check_modules` 는 sysfs(kset) 에는 있는데 모듈 목록에는 없는 모듈을 냅니다[2]. `linux.malware.hidden_modules` 는 메모리를 긁어 모듈 구조체를 찾습니다[2]. `linux.malware.modxview` 는 모듈 목록, kset 의 모든 모듈, 거르지 않은 메모리 검색 결과를 모듈 주소 기준으로 합쳐 `Name`, `Address`, `In procfs`, `In sysfs`, `In scan`, `Taints` 칸으로 보여 줍니다[2]. 읽는 법은 아래 "결과를 어떻게 해석하나" 의 표에 있습니다.

    ```
    vol -f memory.lime linux.malware.modxview
    vol -f memory.lime linux.malware.check_modules --dump
    vol -f memory.lime linux.malware.hidden_modules --dump
    ```

6. **가로채기(후킹)를 점검합니다.** 함수 후킹으로만 숨는 모듈은 출처 사이에 어긋남을 만들지 않고 목록에 그대로 보이므로[1], 가로챈 자리를 따로 봅니다.

    | 플러그인 | 보는 곳 | 눈여겨볼 값 |
    |---|---|---|
    | `linux.malware.check_syscall` | `sys_call_table`, 있으면 `ia32_sys_call_table` 도[2] | `Handler Symbol` 이 `UNKNOWN`(커널 심볼로 풀리지 않는 주소)[2] |
    | `linux.malware.check_idt` | 인터럽트 서술자 표 (IDT) 변경[2] | `Module`·`Symbol` |
    | `linux.malware.check_afinfo` | 네트워크 프로토콜의 함수 포인터[2] | `Symbol Name`·`Member`·`Handler Address` |
    | `linux.malware.tty_check` | tty 장치의 후킹[2] | `Module`·`Symbol` |
    | `linux.malware.keyboard_notifiers` | 키보드 알림 호출 사슬[2] | `Module`·`Symbol` |
    | `linux.malware.netfilter` | Netfilter 후킹[2] | `Module`·`Is Hooked` |
    | `linux.tracing.ftrace` | ftrace 로 건 후킹 콜백[3] | `Callback`·`Hooked symbols`·`Module` |
    | `linux.tracing.tracepoints` | tracepoint 에 붙은 프로브[3] | `Probe`·`Module` |
    | `linux.malware.check_creds` | 프로세스끼리 자격 증명(cred) 구조를 함께 쓰는지[2] | `CredVAddr`·`PIDs` |

    아래는 `check_syscall` 출력 줄을 칸 이름에 맞춰 만든 예시입니다. 두 번째 줄처럼 `UNKNOWN` 이 나온 항목은 커널 심볼로 풀리지 않는 주소를 가리키는 표 항목입니다[2].

    ```
    Table Address   Table Name  Index  Handler Address     Handler Symbol
    0xffffffff82000300  64bit   0      0xffffffff81400010  __x64_sys_read
    0xffffffff82000300  64bit   217    0xffffffffc0a01230  UNKNOWN
    ```

7. **eBPF 프로그램을 봅니다.** 라이브에서는 UAC 가 `ls -la /sys/fs/bpf` 로 고정된 (pinned) 프로그램을, `bpftool prog list` 로 실린 프로그램을 받고, 고정된 것마다 `bpftool prog show`, `prog dump xlated`, `prog dump jited` 을 남깁니다[5]. UAC 는 고정 파일 이름의 앞 8글자를 프로그램 이름으로 넘기므로[5], 이름이 맞지 않는 프로그램은 덤프가 비어 있을 가능성이 있고 `prog list` 전체 목록과 맞춰 봅니다. 메모리에서는 `linux.ebpf` 가 `prog_idr` 를 따라 eBPF 프로그램을 늘어놓고[4], `linux.tracing.perf_events` 는 프로세스마다 성능 이벤트와 붙은 프로그램을 보여 주며 eBPF 기반 악성 코드를 찾는 플러그인 가운데 하나입니다[3].

8. **숨은 프로세스를 맞춰 봅니다.** 메모리에서 `linux.pslist`(작업 목록), `linux.psscan`(메모리 검색), `linux.pidhashtable`(PID 해시 표) 결과를 PID 기준으로 합쳐, 어느 한 결과에서만 빠진 프로세스를 찾습니다[4]. `psscan` 에는 `EXIT_STATE` 칸이 있어 `EXIT_ZOMBIE`·`EXIT_DEAD` 처럼 이미 끝난 작업도 나오므로, `psscan` 에만 있는 항목은 이 칸을 먼저 봅니다[4]. 플러그인 준비와 일반 순서는 [메모리 분석](memory-analysis.md) 에서 다룹니다.

9. **찾은 것을 꺼내 따로 판단합니다.** 모듈은 `--dump` 나 `linux.module_extract`(주어진 주소에서 ELF 파일을 다시 만듦)로 꺼냅니다[2][4]. 모듈을 다 실은 뒤에는 원래 파일의 일부를 커널이 버리므로 메모리에서는 일부만 다시 만들 수 있고, 가능하면 모듈 파일을 파일 시스템 캐시에서 되살립니다[1]. 꺼낸 파일은 [알려진 파일 대조와 YARA](hash-yara.md) 로 넘깁니다. 모듈에 든 `srcversion` 해시는 모듈을 빌드한 소스 파일로 계산한 값이라서, 소스가 공개된 루트킷이면 여러 판을 빌드해 이 값과 맞춰 공격자가 쓴 판을 좁힐 수 있습니다[1].

## 도구

| 도구 | 쓰는 곳 | 비고 |
|---|---|---|
| Volatility 3 `linux.malware.*`, `linux.tracing.*`, `linux.ebpf`, `linux.lsmod`, `linux.module_extract` | 메모리 이미지 | `malware` 가 빠진 옛 이름은 폐기 예정([커널 모듈](../../02-artifacts/persistence/kernel-modules.md))[2][3][4] |
| ModXRef | 메모리 이미지 | 모듈 목록·kset·모듈 배치 트리·vmap 목록·vmap 트리·버그 목록·ftrace 모듈 맵의 7개 출처를 비교하는 연구용 Volatility 플러그인, https://github.com/CrySyS/ModXRef [1] |
| UAC | 라이브 | 숨은 PID 비교, `/sys/module` 목록, taint, eBPF, `/etc/ld.so.preload` 직접 읽기, 상태를 바꾸는 수정자 두 개[5] |
| Velociraptor `Linux.Proc.Modules` | 라이브 | `/proc/modules` 를 `Name`, `Size`, `UseCount`, `UsedBy`, `Status`, `Address` 칸으로 나눔[7] |
| bpftool | 라이브 | 실린 eBPF 프로그램 목록과 덤프[5] |
| chkrootkit | 라이브·마운트한 이미지 | 설치돼 있으면 UAC 가 `chkrootkit -n -r 마운트지점` 과 `-n -x -r`(확장 검사)로 부름[5]. 판정 기준은 도구 문서를 따릅니다 |

## 함정과 한계

- **라이브 비교는 커널이 정직하다는 전제 위에 있습니다.** `ps`, `/proc`, `/proc/modules`, `/sys/module` 은 모두 대상 커널이 돌려준 값이라, 커널 루트킷은 양쪽을 함께 고칠 수 있습니다[1]. 라이브 비교에서 어긋남이 없으면 메모리 비교로 넘어갑니다.
- **수정자는 증거를 바꿉니다.** `umount` 와 `sysctl` 은 대상 시스템의 상태를 바꾸므로[5], 켠 경우 수행 사실과 시각을 보고서에 적습니다. 메모리 수집 도구를 커널 모듈로 실으면 taint 비트가 켜질 수 있다는 점도 수집 기록과 맞춥니다([커널 모듈](../../02-artifacts/persistence/kernel-modules.md)).
- **`check_modules` 는 한쪽만 고친 경우를 잡습니다.** 이 플러그인은 kset 에 있고 모듈 목록에 없는 모듈만 내므로[2], 모듈 목록과 kset 을 함께 고친 루트킷은 놓칩니다. Nagy(2025)의 시험(Vagrant·VirtualBox 가상 머신, `VBoxManage debugvm dumpvmcore` 로 뜬 ELF 덤프)에서 `linux.check_modules` 는 오픈소스 루트킷 35개 중 13개, VirusTotal 에서 모은 20개 중 모듈 목록만 고친 10개를 찾았고, 7개 출처를 비교한 논문 플러그인은 55개를 모두 찾았습니다[1]. 같은 시험에서 DKOM 을 쓴 루트킷은 모두 모듈 목록에서 자기를 뺐고, 모듈 배치 트리·버그 목록·ftrace 모듈 맵에서 숨은 것은 없었습니다[1].
- **커널 판에 따라 쓸 수 있는 출처가 다릅니다.** kset 은 2.6.25, vmap 관련 구조는 2.6.28, 모듈 배치 트리는 4.2, ftrace 모듈 맵은 4.15 부터 있고, 6.9 에서는 `vmap_area_list`·`vmap_area_root` 대신 `vmap_nodes` 가 쓰입니다[1]. 검체의 `uname -r` 로 판을 확인하고 어떤 출처가 비교에 들어갔는지 기록합니다.
- **`hidden_modules` 의 빠른 검색은 4.2 이상을 가정합니다.** 4.2 부터 모듈 구조체가 L1 캐시 줄 크기(i386·amd64·arm64 에서 보통 64바이트)에 맞춰 놓이는 점을 이용하고, 그보다 옛 커널은 정렬이 보장되지 않습니다[2].
- **eBPF 는 모듈 비교로 드러나지 않습니다.** eBPF 는 커널 모듈을 쓰지 않으므로 모듈 교차 비교로 찾을 수 없습니다[1]. 절차 7 을 따로 거칩니다.
- **드러나 있는 루트킷도 있습니다.** 숨기지 않은 모듈은 모든 출처에 똑같이 보여 교차 비교로 걸리지 않습니다[1]. 트리 밖 모듈, 서명 없는 모듈, 패키지에 속하지 않는 `.ko` 파일, 알 수 없는 심볼 이름을 따로 훑습니다. 논문의 사례에서는 모듈 기호 이름(`pidhider_init`, `my_hide_module` 같은 것)이 악성 여부를 가르는 단서가 됐습니다[1].
- **이미지 품질이 결과를 좌우합니다.** 불완전하거나 일관되지 않은 덤프에서는 숨은 모듈을 찾지 못할 수 있습니다[1]. 라이브로 뜬 메모리는 한순간의 스냅숏이 아니므로, 출처 사이 어긋남이 수집 중 변화에서 왔을 가능성도 따져 봅니다([메모리 수집](../acquisition/memory-acquisition.md)).
- **UAC 의 숨은 PID 목록에는 수집 중 끝난 프로세스가 섞일 수 있습니다.** `/proc` 목록을 읽은 뒤 `ps ax` 를 돌리는 사이에 끝난 프로세스는 `ps` 에 없으므로[5], 같은 PID 가 `ps_auxwww.txt` 같은 다른 결과나 메모리에 있는지 맞춰 봅니다.

## 결과를 어떻게 해석하나

### 모듈 비교 표 읽기

`modxview` 의 세 칸은 각각 모듈 목록(`In procfs`), kset(`In sysfs`), 메모리 검색(`In scan`)에서 그 모듈을 찾았는지를 뜻합니다[2]. 아래 해석은 각 칸이 어느 자료 구조에서 나왔는지에서 끌어낸 것입니다.

| In procfs | In sysfs | In scan | 뜻 |
|---|---|---|---|
| True | True | True | 세 출처가 일치합니다. 숨지 않았거나 함수 후킹으로만 숨는 모듈이고, 모듈 정보를 따로 판단합니다[1] |
| False | True | True | 모듈 목록에서만 빠졌습니다. `check_modules` 도 잡는 경우입니다[2] |
| False | False | True | 모듈 목록과 kset 에서 함께 빠지고 메모리 검색에만 걸렸습니다. DKOM 을 강하게 가리킵니다[1] |
| True | False | 무관 | kset 쪽만 어긋납니다. Nagy(2025) 시험에서 DKOM 을 쓴 루트킷은 모두 모듈 목록에서 빠졌으므로[1] 드문 조합이고, 같은 주소의 모듈 정보를 따로 봅니다 |

### 증명하는 것

메모리 이미지에서 출처끼리 모듈이 어긋나면 누군가 커널 자료 구조를 고쳤다는 강한 지표입니다[1]. `check_syscall` 의 `UNKNOWN` 항목은 수집 순간 시스템 호출 표의 그 칸이 커널 심볼로 풀리지 않는 주소를 가리켰다는 뜻입니다[2]. 파일 시스템을 직접 읽은 `/etc/ld.so.preload` 가 일반 읽기 결과와 다르면 수집 순간 파일 읽기를 가로채는 무언가가 돌고 있었습니다.

### 증명하지 못하는 것

어긋남이 없다고 루트킷이 없다고 할 수 없습니다. 함수 후킹만 쓰는 모듈, 모든 출처에서 지운 모듈, eBPF 프로그램은 모듈 비교에 드러나지 않습니다[1]. `/proc/sys/kernel/tainted` 값은 어느 모듈 때문인지 말하지 않습니다[6]. chkrootkit 같은 도구의 판정은 그 도구의 검사 결과일 뿐이고, 판정이 나온 근거 파일을 직접 열어 확인하기 전에는 사실로 쓰지 않습니다. 루트킷을 누가 언제 심었는지는 이 절차만으로 알 수 없고, [타임라인](timeline.md) 과 [커널 로그](../../02-artifacts/system-info/kernel-log.md), 명령 기록으로 좁힙니다.

### 시각 해석

메모리 이미지의 결과는 수집을 시작해 끝낸 사이의 상태이고, 자체로는 루트킷이 언제 실렸는지를 알려 주지 않습니다. taint 값은 원인을 되돌려도 남는 비트 값이라[6], 부팅 뒤 언제 켜졌는지는 이 값만으로 알 수 없습니다. UAC 결과 파일의 시각은 수집한 때입니다. 적재 시각은 커널 메시지와 모듈 파일의 시각으로 좁히고, 그 해석은 [커널 모듈](../../02-artifacts/persistence/kernel-modules.md) 의 시각 절을 따릅니다.

### 보고서 문장

"이 시스템에 루트킷이 있었다" 가 아니라 기록이 말하는 만큼만 씁니다.

- "메모리 이미지에서 `xyzmod` 라는 이름의 모듈 구조체가 메모리 검색으로는 발견됐으나 커널 모듈 목록과 sysfs 에는 없었다." (만든 예시)
- "시스템 호출 표 217번 칸이 커널 심볼로 풀리지 않는 주소 `0xffffffffc0a01230` 을 가리켰다." (만든 예시)
- "수집 중 UAC 의 `disable_ftrace` 수정자로 `kernel.ftrace_enabled` 를 0 으로 바꿨다." (만든 예시)

지속성 흔적 전체를 훑는 흐름은 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md), 채굴기 조사에서 숨은 프로세스를 다루는 흐름은 [채굴기가 돌았나](../../04-scenarios/intrusion/cryptominer.md) 에 있습니다.

## 참고 문헌

1. Roland Nagy, "Detecting hidden kernel modules in memory snapshots", Forensic Science International: Digital Investigation 53 (2025) 301928 (DFRWS USA 2025). https://doi.org/10.1016/j.fsidi.2025.301928
2. Volatility 3, framework/plugins/linux/malware (check_modules, hidden_modules, modxview, check_syscall, check_idt, check_afinfo, tty_check, keyboard_notifiers, netfilter, check_creds), framework/symbols/linux/utilities/modules.py. https://github.com/volatilityfoundation/volatility3/tree/develop/volatility3/framework/plugins/linux/malware , https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/symbols/linux/utilities/modules.py
3. Volatility 3, framework/plugins/linux/tracing (ftrace, perf_events, tracepoints). https://github.com/volatilityfoundation/volatility3/tree/develop/volatility3/framework/plugins/linux/tracing
4. Volatility 3, framework/plugins/linux (lsmod, module_extract, ebpf, pslist, psscan, pidhashtable). https://github.com/volatilityfoundation/volatility3/tree/develop/volatility3/framework/plugins/linux
5. UAC, artifacts (live_response/modifiers/revel_hidden_processes·disable_ftrace, live_response/system/kernel_modules·lsmod·kernel_tainted_state·ebpf·bpftool, chkrootkit/chkrootkit·hidden_etc_ld_so_preload). https://github.com/tclahr/uac/tree/main/artifacts
6. Linux kernel, Documentation/admin-guide/tainted-kernels.rst. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/tainted-kernels.rst
7. Velociraptor, Linux.Proc.Modules. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Proc/Modules.yaml
