---
title: "메모리 수집"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 930
---

# 메모리 수집 (Memory Acquisition)

켜져 있는 Linux 시스템의 물리 메모리를 파일로 떠내는 절차입니다. 커널 모듈(LiME)이나 사용자 공간 도구(AVML)로 뜨고, 커널 잠금 상태와 분석용 심볼 준비가 결과를 좌우합니다.

## 언제 쓰나

메모리에는 실행 중인 프로세스, 열린 네트워크 연결, 디스크에 쓰지 않은 데이터처럼 전원을 끄면 사라지는 정보가 있습니다. 시스템을 끄거나 디스크를 이미징하기 전에 메모리부터 뜨는 이유가 여기에 있습니다. 명령 출력으로 휘발성 정보를 모으는 방법은 [라이브 응답 수집](live-response.md) 에서, 떠낸 이미지를 읽는 방법은 [메모리 분석](../analysis/memory-analysis.md) 에서 다룹니다.

메모리 수집이 가능한지는 대상 커널이 정합니다. 물리 메모리를 읽는 통로는 `/proc/kcore`, `/dev/mem`, `/dev/crash` 같은 특수 파일과 커널 모듈 두 가지인데[4][26], 커널 설정과 커널 잠금 (Kernel Lockdown) 에 따라 통로가 닫혀 있을 수 있습니다[11][14][15]. 그래서 수집 도구를 고르기 전에 대상 커널의 상태부터 확인합니다.

## 절차

1. **대상 커널 확인.** `uname -r` 로 커널 판을, `cat /etc/os-release` 로 배포판과 판을 적습니다[3]. LiME 는 대상 커널에 맞춰 빌드한 모듈이 있어야 하므로 이 두 값으로 모듈을 고릅니다.
2. **커널 잠금 단계 확인.** securityfs 의 `lockdown` 파일을 읽습니다. systemd 는 securityfs 를 `/sys/kernel/security` 에 마운트하므로[20] 보통 `/sys/kernel/security/lockdown` 입니다. 파일 내용은 `none [integrity] confidentiality` 처럼 세 단계를 늘어놓고 지금 단계를 대괄호로 감쌉니다[16]. 파일이 없으면 커널 잠금 기능이 빠진 커널일 수 있습니다. 이 기능은 Linux 5.4 에서 들어왔고, `CONFIG_SECURITY_LOCKDOWN_LSM` 으로 빌드한 커널에서 부팅 인자 `lsm=`(없으면 `security=`, 그다음 `CONFIG_LSM` 값)에 `lockdown` 이 들어 있어야 켜집니다[11].
3. **모듈 적재 가능 여부 확인.** `/proc/sys/kernel/modules_disabled` 가 1 이면 모듈을 올리지도 내리지도 못하고 0 으로 되돌릴 수도 없습니다[19]. 이 경우 LiME 는 쓸 수 없습니다. 커널 잠금이 켜져 있으면 서명이 유효한 모듈만 올라갑니다[11].
4. **저장 위치 결정.** 대상 디스크에 덤프를 쓰면 그 디스크의 빈 공간을 덮고 메모리도 더 많이 바뀝니다. vCPU 4개·RAM 8GB 가상 머신을 멈추고 뜬 기준 이미지와 비교한 시험에서, 디스크로 저장한 덤프는 평균 약 230MB(메모리의 2.68%)가 달랐고 네트워크로 받은 덤프는 10MB 미만(0.2% 미만)이 달랐습니다[26]. 대신 네트워크 수집은 시간이 약 다섯 배 더 걸렸습니다[26]. 네트워크로 받을 수 있으면 그쪽을 쓰고, 디스크에 써야 하면 대상 디스크가 아닌 외장 매체에 씁니다.
5. **수집.** 아래 도구 절의 방식 가운데 대상에서 열리는 통로를 씁니다. 시작 시각과 끝 시각을 UTC 로 적고, 쓴 도구·판·옵션·명령줄을 그대로 기록합니다.
6. **분석 준비물 함께 수집.** 메모리 이미지만으로는 구조를 풀지 못하므로 같은 시스템의 `/boot/vmlinu*`, `/boot/System.map*`, `/boot/config*` 를 함께 모읍니다[21][24]. 커널 판 문자열과 패키지 이름도 적어 둡니다. 이유는 아래 함정과 한계 절에서 설명합니다.
7. **해시와 보관.** 받은 파일을 분석 장비에서 해시하고 보관 기록에 적습니다. LiME 의 `digest=` 해시는 수집 쪽이 계산한 값이라서 전송 뒤 해시와 맞춰 봅니다[1].

배포판별로 확인할 것은 다음과 같습니다.

| 항목 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|
| AVML 공식 시험 목록 | Ubuntu 는 22.04 까지 들어 있음[4] | RHEL 9.0 이 들어 있음[4] |
| LiME 외부 빌드용 커널 소스 | LiME 안내서의 기본 절차가 Ubuntu 기준[3] | CentOS 절차를 따라 커널 소스 RPM 을 받음[3] |
| 커널 잠금 단계 | 대상 시스템의 `/sys/kernel/security/lockdown` 으로 확인 | 같음 |
| `/dev/mem`·`/proc/kcore` 커널 설정 | 대상 시스템의 `/boot/config-*` 에서 `CONFIG_STRICT_DEVMEM`·`CONFIG_PROC_KCORE` 줄 확인 | 같음 |

## 도구

### LiME

LiME 는 적재형 커널 모듈 (Loadable Kernel Module, LKM) 로 동작하는 수집 도구입니다[1]. `insmod ./lime-$(uname -r).ko "path=... format=..."` 형태로 올리고, `path` 에는 파일 이름이나 `tcp:포트` 를 줍니다[1]. 네트워크로 받을 때는 받는 장비에서 `nc 대상IP 4444 > ram.lime` 처럼 연결하고, 수집이 끝나면 LiME 가 연결을 끊습니다[2].

`format` 은 반드시 정해야 하고 값은 셋입니다[1][2].

| 값 | 내용 | 분석 |
|---|---|---|
| `lime` | 메모리 범위마다 앞에 고정 크기 헤더를 붙임 | Volatility 3 가 바로 읽음[8] |
| `padded` | 물리 주소 0 부터 시작하고 System RAM 이 아닌 범위를 0 으로 채움 | 파일 오프셋이 곧 물리 주소 |
| `raw` | System RAM 범위만 이어 붙임 | 원래 위치 정보가 사라져 대부분 도구가 분석하지 못함. System RAM 이 물리 주소 0 부터 한 덩어리일 때만 예외 |

선택 인자는 다음과 같습니다[1][2]. `digest=` 는 커널 암호 라이브러리의 해시로 `ram.lime.sha256` 같은 옆 파일을 만들고, TCP 로 받을 때는 두 번째 연결로 해시 파일을 받습니다. `compress=1` 은 zlib 로 압축하고 약 24KB 의 커널 메모리를 더 씁니다. `timeout=` 은 메모리 한 페이지를 읽고 쓰는 데 허용하는 밀리초이고 기본값 1000 을 넘기면 그 범위의 나머지를 건너뜁니다. 0 이면 끄고, 2.6.35 이상 커널에서만 쓸 수 있습니다. 그 밖에 `dio`, `localhostonly` 가 있습니다.

LiME 모듈은 대상 커널과 판이 맞아야 올라갑니다. 커널은 모듈을 올릴 때 같은 판과 설정으로 빌드된 모듈인지 `vermagic` 으로 검사하고, `CONFIG_MODVERSIONS` 를 켠 커널이면 `__versions` 의 심볼 판도 검사합니다[27]. 대상에 컴파일러와 커널 헤더를 설치하지 않도록 다른 장비에서 대상 커널용으로 빌드하는 방법(외부 빌드, out of tree)이 있고, 대상의 `/boot/config-*` 를 가져와 빌드에 씁니다[3]. `make symbols` 로 빌드하면 심볼을 지우지 않은 모듈이 나옵니다[2].

### AVML

AVML 은 x86_64 용 사용자 공간 수집 도구이고 정적 바이너리로 배포합니다[4]. 대상 배포판이나 커널을 미리 알 필요가 없고 대상에서 컴파일하지 않습니다[4]. 메모리 원천은 `/dev/crash`, `/proc/kcore`, `/dev/mem` 셋이고, 원천을 정하지 않으면 차례로 시도합니다[4]. 파일로 저장할 때는 `/dev/crash` → `/proc/kcore` → `/dev/mem` 순서로 시도하고, 표준 출력이나 스트리밍으로 보낼 때는 `/proc/kcore` → `/dev/crash` → `/dev/mem` 순서로 한 번만 고릅니다[5]. 스트리밍 중에는 원천을 바꾸지 않습니다[4].

`/proc/kcore` 는 물리 메모리를 ELF 코어 파일 형식으로 보여 주는 파일입니다[13]. AVML 은 이 파일의 크기가 0x2000 보다 크고 열릴 때만 쓸 수 있는 원천으로 봅니다[5]. 수집할 범위는 `/proc/iomem` 에서 `System RAM` 으로 끝나는 줄만 골라 정하고, `/proc/iomem` 을 읽으려면 `CAP_SYS_ADMIN` 이 필요합니다[7].

하위 명령은 `acquire`, `convert`, `upload`, `stream` 입니다[4]. 압축하지 않으면 LiME 형식으로, `--compress` 를 주면 Snappy 로 페이지 단위 압축한 AVML 형식으로 저장합니다[4]. 압축본은 `avml convert` 로 LiME 형식으로 풉니다[4]. `stream tcp` 는 TLS 없이 보내고, 연결이 끊기면 이어 받지 못합니다[4].

### 덤프 파일 형식

LiME 형식은 범위마다 32바이트 헤더를 두고 그 뒤에 범위의 메모리를 그대로 붙입니다[2]. AVML 도 같은 32바이트 헤더를 쓰고 압축본만 매직과 판이 다릅니다[6].

| 오프셋 | 크기 | 필드 | 값 |
|---|---|---|---|
| 0x00 | 4 | `magic` | LiME `0x4C694D45`, AVML 압축본 `0x4C4D5641` |
| 0x04 | 4 | `version` | LiME 1, AVML 압축본 2 |
| 0x08 | 8 | `s_addr` | 범위 시작 물리 주소 |
| 0x10 | 8 | `e_addr` | 범위 끝 물리 주소(끝 바이트 포함) |
| 0x18 | 8 | `reserved` | 0 |

모든 값은 리틀 엔디언입니다[6][8]. 범위 길이는 `e_addr - s_addr + 1` 이고, 다음 헤더는 지금 헤더 끝에서 그 길이만큼 뒤에 있습니다[8]. AVML 은 `reserved` 가 0 이 아니면 잘못된 헤더로 봅니다[6]. AVML 은 범위를 최대 16MiB(`0x1000*0x1000`) 블록으로 나누고, 블록이 모두 0 이면 그 블록을 쓰지 않습니다[6].

아래는 헤더 명세로 만든 예시이고 실제 시스템의 값이 아닙니다.

```text
00000000  45 4d 69 4c 01 00 00 00  00 10 00 00 00 00 00 00  |EMiL............|
00000010  ff fb 09 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
```

1. 첫 4바이트 `45 4d 69 4c` 는 `0x4C694D45` 를 리틀 엔디언으로 쓴 것이라 문자로는 `EMiL` 로 보입니다.
2. 0x04 의 `01 00 00 00` 은 판 1 입니다.
3. `s_addr` 는 0x1000, `e_addr` 는 0x9FBFF 이므로 범위 길이는 0x9EC00 바이트입니다.
4. 다음 헤더는 파일 오프셋 0x20 + 0x9EC00 = 0x9EC20 에 있어야 합니다. 그 자리에서 다시 `45 4d 69 4c` 가 나오면 헤더를 제대로 따라간 것입니다.

같은 시스템의 `/proc/iomem` 에 `00001000-0009fbff : System RAM` 같은 줄(만든 예시)이 있으면 헤더의 범위와 맞춰 볼 수 있습니다. 헤더 범위를 모두 더한 값이 `/proc/iomem` 의 System RAM 합과 크게 다르면 빠진 범위가 있는지 봅니다. AVML 은 모두 0 인 블록을 쓰지 않으므로 그만큼은 합이 작아도 정상입니다[6].

### 그 밖의 도구

UAC 는 `avml acquire avml.lime` 을 부르고 `/boot/vmlinu*`, `/boot/System.map*` 을 함께 모읍니다[21]. `free` 출력의 `Mem:` 합계가 `avml_max_memory`(기본 270000000)보다 작을 때만 AVML 을 실행하고, 이 값은 `-D avml_max_memory=값` 으로 바꿉니다[21]. 전체 메모리 대신 프로세스 단위로 메모리를 뜨는 방법으로는 UAC 의 `linux_procmemdump.sh`[23]와, 고른 PID 하나의 메모리를 올리는 Velociraptor 의 `Linux.Triage.ProcessMemory`[25] 가 있습니다. 전체 메모리 대신 남아 있는 크래시 덤프를 모으는 방법도 있습니다. UAC 는 `/var/lib/systemd/coredump` 의 `core.*`, ABRT 의 `/var/spool/abrt`·`/var/spool/abrt-upload`·`/var/tmp/abrt`, Apport·kdump 의 `/var/crash` 를 모읍니다[22].

eBPF 로 물리 메모리를 읽는 LEMON 은 커널 잠금 integrity 단계에서도 수집할 수 있는 도구로 발표됐고, 덤프를 raw 나 LiME 형식으로 저장합니다[26]. 스왑과 최대 절전 파일에 남는 메모리 조각은 [스왑과 최대 절전](../../01-foundations/disk-volume/swap-hibernation.md) 에서 다룹니다.

## 함정과 한계

**커널 잠금이 통로를 닫습니다.** 커널 잠금에는 `none`, `integrity`, `confidentiality` 세 단계가 있습니다[16][17]. integrity 단계에서는 서명 없는 모듈 적재와 `/dev/mem,kmem,port` 가 막히고, confidentiality 단계에서는 여기에 더해 `/proc/kcore access` 와 `use of bpf to read kernel RAM` 이 막힙니다[17][18]. `/proc/kcore` 를 열 때 커널은 `CAP_SYS_RAWIO` 와 `LOCKDOWN_KCORE` 를 검사하고[14], `/dev/mem` 을 열 때는 `CAP_SYS_RAWIO` 와 `LOCKDOWN_DEV_MEM` 을 검사합니다[15]. EFI Secure Boot 로 부팅한 x86·arm64 장비에서는 커널 잠금이 자동으로 켜집니다[11]. 막힌 기능을 쓰면 커널 로그에 `Lockdown: 프로세스이름: 이유 is restricted; see man kernel_lockdown.7` 이 남습니다[16]. 이 줄은 [커널 로그](../../02-artifacts/system-info/kernel-log.md) 에서 찾습니다.

**출처끼리 서술이 다릅니다.** AVML 설명서는 커널 잠금이 켜져 있으면 AVML 로 수집할 수 없다고 적었습니다[4]. 커널 코드에서는 `/proc/kcore` 가 confidentiality 단계에서만 막히고 integrity 단계에서는 `/dev/mem` 만 막힙니다[17][18]. AVML 코드는 `LOCKDOWN_KCORE` 가 걸리면 `/proc/kcore` 가 있어도 열리지 않거나 일부만 읽힐 수 있다고 봅니다[5]. LEMON 논문은 Secure Boot 와 커널 잠금을 켠 시스템에서 LiME·AVML 이 동작하지 않는다고 평가했습니다[26]. 원인을 한쪽으로 단정하지 말고, 대상 시스템에서 잠금 단계와 `/proc/kcore` 가 열리는지를 직접 확인합니다.

**`/dev/mem` 은 RAM 을 다 보여 주지 않을 수 있습니다.** Linux 2.6.26 부터 `CONFIG_STRICT_DEVMEM` 이 `/dev/mem` 으로 접근할 수 있는 영역을 줄이고, 예를 들어 x86 에서는 RAM 은 막고 PCI 메모리 맵 영역은 허용합니다[12]. `/dev/kmem` 은 2.6.26 부터 `CONFIG_DEVKMEM` 을 켠 커널에만 있습니다[12].

**형식과 옵션.** `raw` 형식은 주소 정보를 잃습니다[1]. `compress=1` 결과는 gzip·zip 과 다른 zlib 형식이라 `unpigz` 처럼 zlib 을 다루는 도구로 풉니다[1]. 이때 해시 파일은 압축하지 않고, 해시 값은 압축 전 데이터 기준입니다[1]. `timeout` 기본값 때문에 느린 영역을 건너뛰면 덤프에 빠진 범위가 생깁니다[1].

**수집 도구도 메모리를 바꿉니다.** `digest` 와 `compress` 를 켜면 LiME 가 대상 메모리를 더 덮어씁니다[1]. 라이브 수집은 한순간의 스냅숏이 아니고 수집하는 동안 계속 바뀌는 메모리를 차례로 읽은 것입니다[26]. LiME 와 AVML 은 4KiB 페이지 단위로 읽습니다[26].

**LiME 는 커널에 흔적을 남깁니다.** 외부에서 빌드한 모듈을 올리면 `/proc/sys/kernel/tainted` 에 4096 `(O)` 비트가, 서명 없는 모듈이면 8192 `(E)` 비트가 설 수 있습니다[19]. 이 비트는 나중에 [커널 모듈](../../02-artifacts/persistence/kernel-modules.md) 을 조사하는 사람에게 수상한 모듈 흔적으로 보일 수 있으므로 수집 기록에 적어 둡니다.

**분석용 심볼을 못 구하면 해석이 막힙니다.** Volatility 3 의 Linux 심볼 표는 이미지 안의 커널 배너와 정확히 같아야 하고, 판 번호뿐 아니라 컴파일 시각과 gcc 판까지 맞아야 합니다[9]. 대부분 배포판 커널은 디버그 정보를 빼고 배포하고 디버그 정보가 든 커널은 따로 받아야 하는데, 배포판이 옛 판을 모두 보관하지는 않아서 맞는 심볼을 끝내 못 구할 수도 있습니다[9]. 커널 구조체 배치는 커널 판과 커널 설정 둘 다에 따라 달라집니다[28]. 수집할 때 `/boot` 아래 파일과 커널 패키지 판을 함께 남기는 이유가 여기에 있습니다.

## 결과를 어떻게 해석하나

**증명하는 것.** 덤프는 수집 시작부터 끝까지 그 시스템의 물리 메모리에 있던 내용을 담습니다. 해시 옆 파일과 전송 뒤 해시가 같으면 덤프 파일이 전송 중에 바뀌지 않았다는 뜻입니다.

**증명하지 못하는 것.** 덤프는 원자적 스냅숏이 아니라서 한 시점의 메모리 상태를 그대로 보여 주지 않습니다. 가상 머신을 멈추고 뜬 기준과 비교한 시험에서 디스크 저장 덤프는 메모리의 평균 2.68% 가 달랐습니다[26]. 서로 다른 범위의 값이 서로 다른 순간에 읽혔을 수 있으므로, 두 구조체의 값이 어긋나면 수집 도중 바뀐 것일 가능성도 따져 봅니다. 해시는 덤프 파일의 무결성만 보여 주고 원본 RAM 과 같다는 증명은 아닙니다. `timeout` 으로 건너뛴 범위나 원천이 막아 둔 범위의 내용은 덤프에 없으므로, 어떤 흔적이 덤프에 없다고 메모리에 없었다고 쓰지 않습니다.

**시각.** LiME·AVML 헤더에는 시각 필드가 없습니다[2][6]. 수집 시각은 수집자가 남긴 기록과 파일 시스템 시각에 기대므로 시작·끝 시각과 기준 시간대(UTC 권장)를 수집 기록에 적습니다. 이미지 안의 커널 부팅 시각이나 프로세스 시작 시각을 해석하는 방법은 [메모리 분석](../analysis/memory-analysis.md) 과 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다. Volatility 3 의 `linux.vmcoreinfo` 는 이미지 안의 VMCOREINFO ELF 노트에서 `SYMBOL(...)` 과 `KERNELOFFSET` 같은 키를 보여 주므로 이미지가 어느 커널에서 나왔는지 맞춰 보는 데 씁니다[10].

**보고서 문장 예.** "2026-03-14 02:10:05Z 부터 02:31:40Z 까지 AVML 로 대상 호스트의 물리 메모리를 LiME 형식으로 수집했고, 수집 직후 SHA-256 은 (값) 이다. 대상의 커널 잠금 단계는 `none` 이었다." (시각·단계는 만든 예시)

다른 운영체제의 메모리 분석은 [Windows 메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/index.html), [macOS 메모리 분석](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/memory-forensics/index.html) 에서 다룹니다.

## 참고 문헌

1. 504ensicsLabs, LiME README.md. https://github.com/504ensicsLabs/LiME/blob/master/README.md
2. 504ensicsLabs, LiME docs/README.md. https://github.com/504ensicsLabs/LiME/blob/master/docs/README.md
3. 504ensicsLabs, LiME docs/external_modules.md. https://github.com/504ensicsLabs/LiME/blob/master/docs/external_modules.md
4. Microsoft, AVML README.md. https://github.com/microsoft/avml/blob/main/README.md
5. Microsoft, AVML src/snapshot.rs. https://github.com/microsoft/avml/blob/main/src/snapshot.rs
6. Microsoft, AVML src/image.rs. https://github.com/microsoft/avml/blob/main/src/image.rs
7. Microsoft, AVML src/iomem.rs. https://github.com/microsoft/avml/blob/main/src/iomem.rs
8. Volatility Foundation, volatility3/framework/layers/lime.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/layers/lime.py
9. Volatility Foundation, doc/source/symbol-tables.rst. https://github.com/volatilityfoundation/volatility3/blob/develop/doc/source/symbol-tables.rst
10. Volatility Foundation, volatility3/framework/plugins/linux/vmcoreinfo.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/vmcoreinfo.py
11. Linux man-pages, man7/kernel_lockdown.7. https://github.com/mkerrisk/man-pages/blob/master/man7/kernel_lockdown.7
12. Linux man-pages, man4/mem.4. https://github.com/mkerrisk/man-pages/blob/master/man4/mem.4
13. Linux man-pages, man5/proc.5. https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
14. Linux kernel, fs/proc/kcore.c. https://github.com/torvalds/linux/blob/master/fs/proc/kcore.c
15. Linux kernel, drivers/char/mem.c. https://github.com/torvalds/linux/blob/master/drivers/char/mem.c
16. Linux kernel, security/lockdown/lockdown.c. https://github.com/torvalds/linux/blob/master/security/lockdown/lockdown.c
17. Linux kernel, include/linux/security.h. https://github.com/torvalds/linux/blob/master/include/linux/security.h
18. Linux kernel, security/security.c. https://github.com/torvalds/linux/blob/master/security/security.c
19. Linux kernel, Documentation/admin-guide/sysctl/kernel.rst. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/sysctl/kernel.rst
20. systemd, src/shared/mount-setup.c. https://github.com/systemd/systemd/blob/main/src/shared/mount-setup.c
21. UAC, artifacts/memory_dump/avml.yaml. https://github.com/tclahr/uac/blob/main/artifacts/memory_dump/avml.yaml
22. UAC, artifacts/memory_dump/coredump.yaml. https://github.com/tclahr/uac/blob/main/artifacts/memory_dump/coredump.yaml
23. UAC, artifacts/memory_dump/process_memory_sections_strings.yaml. https://github.com/tclahr/uac/blob/main/artifacts/memory_dump/process_memory_sections_strings.yaml
24. UAC, artifacts/files/system/boot.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/system/boot.yaml
25. Velociraptor, artifacts/definitions/Linux/Triage/ProcessMemory.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Triage/ProcessMemory.yaml
26. Oliveri, A., Cavenati, M., De Rosa, S., Lakshmi Narasimhan, S., Balzarotti, D. "LEMON: A universal eBPF-based volatile memory acquisition tool for modern android devices and hardened linux systems". Forensic Science International: Digital Investigation 56, 302045 (DFRWS EU 2026), 2026. https://doi.org/10.1016/j.fsidi.2026.302045
27. Stuettgen, J., Cohen, M. "Robust Linux Memory Acquisition with Minimal Target Impact". DFRWS EU 2014 발표 자료. https://dfrws.org/presentation/robust-linux-memory-acquisition-with-minimal-target-impact/
28. Socała, A., Cohen, M. "Automatic Profile generation for live Linux Memory analysis". DFRWS EU 2016 발표 자료. https://dfrws.org/presentation/automatic-profile-generation-for-live-linux-memory-analysis/
