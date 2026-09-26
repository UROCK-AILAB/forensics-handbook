---
title: "커널 모듈"
parent: "아티팩트 · 지속성"
nav_order: 550
---

# 커널 모듈 (Kernel Modules)

부팅 때 모듈을 싣게 하는 설정 파일, 지금 실린 모듈 목록, 커널의 taint 값과 적재 메시지를 맞춰 보면 어떤 모듈이 언제부터 커널 안에 있었는지, 목록에서 숨은 모듈이 있는지를 가릴 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

적재 가능한 커널 모듈 (Loadable Kernel Module, LKM) 은 커널이 돌고 있는 중에 끼워 넣는 코드입니다. 모듈은 대부분 장치를 인식할 때 자동으로 실리지만, 부팅 때마다 특정 모듈을 싣도록 적어 두는 설정 파일도 있습니다[1]. 커널 안에서 돌기 때문에 LKM 은 Linux 커널 루트킷을 심는 사실상 표준 수단이고, 루트킷은 대개 자기 모듈을 목록에서 지워 숨습니다[21].

그래서 흔적은 세 층에 나뉘어 남습니다. 디스크에는 모듈을 부르는 설정 파일과 모듈 파일(`.ko`)이 남고, 로그에는 적재할 때 커널과 systemd 가 낸 메시지가 남고, 메모리에는 지금 실린 모듈의 커널 자료 구조가 남습니다. 디스크 이미지만 있으면 앞의 둘만 볼 수 있고, 지금 무엇이 실려 있는지는 라이브 수집이나 메모리 이미지가 있어야 알 수 있습니다.

## 위치와 버전별 차이

### 부팅 때 싣는 목록

`systemd-modules-load.service` 는 부팅 초기에 도는 서비스로, 아래 디렉터리의 `*.conf` 파일에 적힌 모듈을 싣습니다[1][2].

- `/etc/modules-load.d/`
- `/run/modules-load.d/`
- `/usr/local/lib/modules-load.d/`
- `/usr/lib/modules-load.d/`

한 줄에 모듈 이름을 하나씩 적고, 빈 줄과 공백을 뺀 첫 글자가 `#` 나 `;` 인 줄은 건너뜁니다[1]. 앞 디렉터리일수록 우선하고, 같은 이름의 파일이 있으면 `/etc/` 의 파일이 나머지를 가립니다[3]. 파일은 디렉터리와 상관없이 이름 순서로 읽고, 벤더 파일과 같은 이름으로 `/etc/` 에 `/dev/null` 을 가리키는 링크를 두면 그 벤더 파일은 꺼집니다[3]. systemd 252 와 255 의 man 페이지 요약에는 `/usr/local/lib/` 가 빠져 있지만, 같은 판의 우선순위 설명과 서비스 코드는 네 곳을 모두 읽습니다[3][4].

커널 명령줄의 `modules_load=` 에 쉼표로 적은 모듈도 싣고, `rd.modules_load=` 는 initrd 안에서만 읽습니다[2]. `/etc/` 의 `/dev/null` 링크로 끈 벤더 파일이 initrd 이미지에도 들어 있으면 이미지를 다시 만들어야 합니다[3]. ForensicArtifacts 는 `/boot/initramfs*`, `/boot/initrd*` 를 부팅 때 실행되는 파일로 따로 모읍니다[15].

### modprobe 설정

`modprobe` 는 아래 순서로 `*.conf` 를 읽고, 같은 이름이면 앞 디렉터리의 파일만 씁니다[7].

- `/etc/modprobe.d/`
- `/run/modprobe.d/`
- `/usr/local/lib/modprobe.d/`
- 배포판 디렉터리(빌드할 때 정하는 경로)
- `/lib/modprobe.d/`

이 설정에는 `alias`, `blacklist`, `options`, `softdep`, `weakdep` 말고도 `install 모듈 명령` 과 `remove 모듈 명령` 이 있습니다[7]. `install` 은 모듈을 넣는 대신 적힌 셸 명령을 돌리고, `remove` 는 `modprobe -r` 때 명령을 돌립니다[7]. `modprobe` 는 커널 명령줄의 `모듈.옵션` 과 `modprobe.blacklist=` 도 읽습니다[8].

커널이 모듈을 스스로 요청할 때 실행하는 도우미 경로는 `/proc/sys/kernel/modprobe` 에 있고 기본값은 `/sbin/modprobe` 입니다[10][14]. 이 값이 빈 문자열이면 자동 적재가 꺼지고, 커널을 `CONFIG_STATIC_USERMODEHELPER=y` 로 빌드했으면 빈 문자열 말고는 이 값이 무시됩니다[10]. `/proc/sys/kernel/modules_disabled` 가 1 이 되면 그 뒤로는 모듈을 싣지도 빼지도 못하고 0 으로 되돌릴 수도 없습니다[10][14].

### 배포판별 차이

| 항목 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|
| systemd 판 | 255 | 252 |
| 부팅 적재 목록 | 위 네 디렉터리[1][3] | 같음[3][4] |
| `/etc/modules` | `/etc/modules-load.d/modules.conf` 가 이 파일을 가리키는 링크[5]. kmod 설치 때 파일이 없으면 "obsolete" 주석 네 줄만 든 파일을 만든다[6] | 실제 시스템에서 확인 |
| `kmod.service` | `systemd-modules-load.service` 의 별칭 링크[5] | 실제 시스템에서 확인 |
| modprobe 설정 | kmod 패키지가 `/etc/modprobe.d/` 와 `/usr/lib/modprobe.d/` 를 만든다[6] | 실제 시스템에서 배포판 디렉터리 확인 |
| 명령 파일 | `lsmod`·`modprobe`·`insmod`·`rmmod`·`modinfo`·`depmod` 가 모두 `/usr/bin/kmod` 로 가는 링크[6] | 실제 시스템에서 확인 |

Ubuntu 의 `/etc/modules` 에 주석 말고 모듈 이름이 적혀 있으면 패키지가 만든 기본 상태에서 바뀐 것이고, 이 파일도 `modules.conf` 링크를 거쳐 부팅 때 읽힙니다[5][6].

### 모듈 파일

`modprobe` 와 `modinfo` 는 모듈 디렉터리 아래 `uname -r` 이름의 폴더에서 모듈과 `modules.dep.bin` 을 찾습니다[8][9]. 모듈 디렉터리는 kmod 를 빌드할 때 정하는 값이라, 실제 시스템에서 `modules.dep.bin` 이 있는 폴더를 찾아 확인합니다. `modprobe` 는 모듈 이름 대신 파일 경로(상대 경로면 `./` 로 시작)를 받아 그 파일을 바로 실을 수도 있어서[8], 모듈 파일이 이 폴더 밖에 있을 수 있습니다.

## 구조

### 라이브에서 보는 적재 상태

| 위치 | 내용 |
|---|---|
| `/proc/modules` | 커널의 모듈 목록(module list)을 돌며 만든 적재 모듈 목록[14][21]. `lsmod` 는 이 파일을 보기 좋게 찍는다[9] |
| `/sys/module/이름/` | 모듈마다 폴더가 하나이고 `module_kset` 을 따라 만든다[21]. `initstate`, `coresize`, `refcnt`, `holders/`, `parameters/` 가 있다[16][18] |
| `/proc/sys/kernel/tainted` | 커널 taint 비트 값[10] |
| `/proc/sys/kernel/modprobe` | 자동 적재 도우미 경로[10] |
| `/proc/sys/kernel/modules_disabled` | 1 이면 적재·제거 잠김[10] |

Velociraptor 는 `/proc/modules` 한 줄을 공백으로 나눠 `Name`, `Size`, `UseCount`, `UsedBy`, `Status`, `Address` 필드로 읽습니다[17]. 모듈 때문에 taint 가 걸렸으면 그 줄에 괄호 표시가 붙고, UAC 는 `grep "(.*)" /proc/modules` 로 이런 줄만 따로 뽑습니다[16].

### taint 비트와 모듈

taint 값의 비트 표는 [커널 로그](../system-info/kernel-log.md) 에 있습니다. 모듈과 관련된 비트는 1 `P`(독점 라이선스 모듈), 2 `F`(강제 적재), 8 `R`(강제 제거), 1024 `C`(staging 드라이버), 4096 `O`(트리 밖에서 빌드한 모듈), 8192 `E`(서명 없는 모듈)입니다[10][11]. taint 를 일으킨 모듈을 빼도 taint 는 남습니다[11].

커널은 모듈을 실을 때 모듈의 `.modinfo` 부분에서 태그를 읽어 taint 를 겁니다[12]. `intree` 태그가 없으면 `O`, `staging` 태그가 있으면 `C`, `license` 가 GPL 호환이 아니면 `P` 를 겁니다[12]. 이때 커널 로그에 남는 메시지의 형식 문자열은 다음과 같습니다[12].

```
%s: loading out-of-tree module taints kernel.
%s: module verification failed: signature and/or required key missing - tainting kernel
%s: module license '%s' taints kernel.
%s: module is from the staging directory, the quality is unknown, you have been warned.
%s: loading test module taints kernel.
Loading of %s is rejected
```

`%s` 첫 자리는 모듈 이름입니다. 마지막 줄은 서명 검사를 강제하는 커널이 모듈을 거절할 때 나오고, `%s` 자리에는 `unsigned module`, `module with unsupported crypto`, `module with unavailable key` 가 들어갑니다[12].

### 모듈 서명

서명한 `.ko` 파일은 파일 끝에 서명 정보가 붙어 있고, 맨 끝 28바이트는 표지 문자열 `~Module signature appended~` 와 줄바꿈입니다[13]. 표지 바로 앞 12바이트가 서명 정보 블록이고, 그 앞에 `sig_len` 바이트의 PKCS#7 서명이 있습니다[12][13].

| 블록 안 오프셋 | 크기 | 필드 | 뜻[13] |
|---|---|---|---|
| 0x00 | 1 | `algo` | 공개키 알고리즘, PKCS#7 에서는 0 |
| 0x01 | 1 | `hash` | 다이제스트 알고리즘, PKCS#7 에서는 0 |
| 0x02 | 1 | `id_type` | 키 식별자 종류, PKCS#7 은 2 |
| 0x03 | 1 | `signer_len` | 서명자 이름 길이, PKCS#7 에서는 0 |
| 0x04 | 1 | `key_id_len` | 키 식별자 길이, PKCS#7 에서는 0 |
| 0x05 | 3 | `__pad` | 채움 |
| 0x08 | 4 | `sig_len` | 서명 데이터 길이, 빅 엔디언 |

커널은 적재할 때 이 표지를 찾아 서명을 검사하고, 버전 정보 검사를 끄고 강제로 실은 모듈은 서명이 있어도 검사하지 않습니다[12]. 서명이 없거나, 지원하지 않는 암호 방식이거나, 검증할 키가 없는 모듈은 서명 강제가 꺼져 있으면 그대로 실리면서 `E` taint 가 걸리고, 검사를 건너뛴 강제 적재 모듈에도 `E` 가 걸립니다[12]. 서명이 틀린 경우처럼 그 밖의 검사 오류가 나면 모듈은 실리지 않습니다[12].

### 감사 로그

감사 레코드 종류에 `KERN_MODULE`(1330, 커널 모듈 이벤트)이 있습니다[20]. 이 레코드가 남는지는 분석 대상 시스템의 감사 설정에 달려 있으므로 [감사 로그 형식](../../01-foundations/logging/auditd-format.md) 과 [감사 로그의 실행 기록](../execution/auditd-execve.md) 에서 규칙을 먼저 확인합니다.

## 증거로서 의미

### 증명하는 것

`modules-load.d`·`/etc/modules` 에 모듈 이름이 있으면 부팅할 때마다 그 모듈을 싣도록 설정돼 있었다는 뜻이고, `modprobe.d` 의 `install`·`remove` 줄은 그 모듈을 싣거나 뺄 때마다 적힌 명령이 돌도록 설정돼 있었다는 뜻입니다[1][7]. 저널에 `systemd-modules-load` 의 "Inserted module" 줄이 있으면 그 부팅에서 이 서비스가 해당 모듈을 실었습니다[4]. taint 값에 `O` 나 `E` 가 켜져 있으면 이번 부팅 동안 트리 밖 모듈이나 서명 없는 모듈이 한 번 이상 실렸습니다[11]. 메모리 이미지에서 모듈 목록과 다른 자료 구조가 서로 어긋나면 모듈을 숨기려고 커널 자료를 고친 흔적입니다[21].

보고서에는 "이 부팅에서 이 이름의 트리 밖 모듈이 적재됐다는 커널 메시지가 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

### 증명하지 못하는 것

설정 파일은 싣도록 적어 둔 것일 뿐 실제로 실렸다는 증거가 아니고, 적재에 실패하거나 차단 목록에 걸렸을 수 있습니다[4]. 반대로 `insmod` 나 `modprobe` 로 손수 실은 모듈은 설정 파일을 남기지 않으므로, 설정 파일이 없다고 모듈이 없었다고 할 수 없습니다. taint 비트로는 어느 모듈 때문인지 알 수 없고, `O`·`P` 메시지는 그 비트가 처음 켜질 때만, 서명 메시지는 부팅당 한 번만 찍히므로 두 번째 모듈부터는 메시지가 없습니다[12]. 전원을 끈 뒤 만든 디스크 이미지에는 `/proc` 과 `/sys` 가 없어서 적재 상태를 볼 수 없습니다. 누가 모듈을 실었는지는 이 기록들만으로 알 수 없고 명령 기록과 감사 로그로 좁혀야 합니다.

## 시각 해석

| 값 | 기준 | 바뀌는 때 |
|---|---|---|
| 설정 파일·`.ko` 파일의 mtime·ctime | 파일 시스템 시각, 저장은 UTC 기준 | 파일 내용·속성을 바꿀 때 |
| 저널의 "Inserted module" 항목 | `__REALTIME_TIMESTAMP` 는 UTC 마이크로초 | 부팅 초기에 `systemd-modules-load` 가 모듈을 실을 때 |
| 커널 taint·거절 메시지 | kmsg 는 부팅 뒤 경과 시간, 저널로 옮긴 항목은 UTC | 모듈을 싣는 순간(메시지가 찍히는 경우만) |
| `/proc/sys/kernel/tainted` | 시각 없음 | 부팅 뒤 누적, 재부팅 때만 초기화 |

`O` 메시지와 서명 메시지가 부팅당 처음 한 번만 찍힌다는 점은 시각 해석에도 걸립니다[12]. 이 메시지의 시각은 "이 부팅에서 처음으로 그런 모듈이 실린 때" 이지, 문제의 모듈이 실린 때라는 보장이 없습니다. 같은 부팅에서 정상 드라이버가 먼저 `O` 를 켰다면 뒤에 실린 모듈은 로그에 흔적이 없습니다.

파일 시각의 뜻은 [ext4 시각](../../01-foundations/filesystem/ext4/timestamps.md), 커널 메시지의 경과 시간을 실제 시각으로 바꾸는 법은 [커널 로그](../system-info/kernel-log.md) 와 [부팅과 종료 기록](../system-info/boot-shutdown.md), 값 변환은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

- **수집 정의가 경로를 다 덮지 않습니다.** ForensicArtifacts 의 `KernelModules` 는 `/etc/modules.conf` 와 `/etc/modprobe.d/*` 만 정의하고 `modules-load.d` 는 정의하지 않습니다[15]. 이 정의에만 기대면 부팅 적재 목록과 `/usr/lib/`·`/usr/local/lib/`·`/run/` 쪽 파일을 놓치므로, 위의 디렉터리를 모두 따로 모읍니다.
- **`install` 줄은 모듈이 아니라 명령입니다.** 적재된 모듈 목록만 보면 `install` 로 걸어 둔 명령은 보이지 않습니다[7]. `modprobe.d` 파일을 모두 열어 `install`·`remove` 줄을 따로 봅니다.
- **같은 이름의 파일과 `/dev/null` 링크.** `/etc/` 에 벤더 파일과 같은 이름의 파일이 있으면 벤더 파일은 읽히지 않습니다[3][7]. 디렉터리를 하나씩 보지 말고 이름 기준으로 합쳐서 실제로 읽히는 파일을 구분합니다.
- **라이브의 두 목록 비교는 사용자 공간까지만 잡습니다.** `/proc/modules` 와 `/sys/module` 은 둘 다 커널 안에서 만드는 값이라, 커널 안의 루트킷은 둘 다 속일 수 있습니다[21]. `lsmod` 출력과 `/proc/modules` 를 비교하는 방식은 사용자 공간 조작만 잡습니다[21]. 숨은 모듈은 메모리 이미지에서 찾습니다.
- **dissect `sysmodules` 는 `initstate` 파일이 있는 폴더만 모듈로 봅니다**[18]. 이 파일이 없는 `/sys/module` 폴더는 결과에서 빠질 가능성이 있으므로 원래 목록과 폴더 수를 맞춰 봅니다.
- **수집 도구가 taint 를 켤 수 있습니다.** 메모리 수집 도구를 커널 모듈로 실으면 `O`·`E` 가 켜질 수 있으니, 수집 기록과 대조합니다([메모리 수집](../../03-techniques/acquisition/memory-acquisition.md)).
- **eBPF 는 모듈이 아닙니다.** eBPF 로 만든 루트킷은 커널 모듈을 쓰지 않아 모듈 교차 비교로 찾을 수 없습니다[21]. eBPF 흔적 수집은 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md) 에서 다룹니다.
- 논문은 폴더 이름을 `/sys/modules` 로 적었지만[21] 도구 코드는 `/sys/module` 을 읽습니다[16][18].

## 직접 분석해 보기

### 헥스로 한 번: 서명한 모듈 파일의 끝

아래는 명세로 만든 예시로, 서명한 `.ko` 파일의 마지막 40바이트입니다(`tail -c 40 모듈.ko | xxd`).

```
00000000: 0000 0200 0000 0000 0000 029d 7e4d 6f64  ............~Mod
00000010: 756c 6520 7369 676e 6174 7572 6520 6170  ule signature ap
00000020: 7065 6e64 6564 7e0a                      pended~.
```

1. 0x0C 부터 끝까지 28바이트가 `~Module signature appended~` 와 줄바꿈(`0a`)입니다. 이 표지가 없으면 파일에 서명이 붙어 있지 않습니다[12][13].
2. 앞 12바이트(0x00~0x0B)가 서명 정보 블록입니다. 0x02 의 `02` 는 PKCS#7 이고, 나머지 한 바이트 필드는 PKCS#7 이라 0 입니다[13].
3. 0x08 의 `00 00 02 9d` 를 빅 엔디언으로 읽으면 `sig_len` 은 0x29D, 곧 669바이트입니다[13]. 파일 끝에서 40+669바이트 앞부터 이 블록 앞까지가 PKCS#7 서명입니다.
4. 서명이 있다고 커널이 그 서명을 믿었다는 뜻은 아닙니다. 검증할 키가 없거나 강제로 실었으면 서명 메시지와 `E` taint 가 남으므로[12], 파일의 서명 유무와 커널 로그를 함께 봅니다.

### 공개 도구로 한 번

디스크 이미지에서는 설정 파일을 모아 읽습니다.

```
ls -la /mnt/evidence/etc/modules-load.d /mnt/evidence/run/modules-load.d /mnt/evidence/usr/local/lib/modules-load.d /mnt/evidence/usr/lib/modules-load.d
grep -rnE '^[[:space:]]*(install|remove)[[:space:]]' /mnt/evidence/etc/modprobe.d /mnt/evidence/usr/lib/modprobe.d /mnt/evidence/lib/modprobe.d
modinfo -b /mnt/evidence -k 커널판 모듈이름
modinfo -F intree /mnt/evidence/경로/모듈.ko
journalctl -D /mnt/evidence/var/log/journal -u systemd-modules-load.service -o short-iso-precise
journalctl -D /mnt/evidence/var/log/journal -k -b -1 -g 'taint|verification failed|rejected'
```

`modinfo` 는 모듈의 속성을 `필드: 값` 으로 찍고, `-b` 로 모듈을 찾을 뿌리 디렉터리를, `-k` 로 커널 판을 정합니다[9]. `-F intree` 결과가 비어 있으면 그 모듈은 트리 밖 모듈로 적재돼 `O` taint 를 켭니다[12]. 저널 읽기 옵션은 [journalctl 로 읽기](../../01-foundations/logging/systemd-journal/journalctl.md) 에 있습니다.

라이브 시스템에서는 UAC 가 `lsmod`, `ls -la /sys/module`, 모듈별 `parameters` 목록, 모듈별 `modinfo`, `/proc/sys/kernel/tainted`, `dmesg | grep -i taint`, `grep "(.*)" /proc/modules` 를 받습니다[16]. ForensicArtifacts 의 `LoadedKernelModules` 는 `/sbin/lsmod` 를 실행하고[15], Velociraptor 는 `Linux.Proc.Modules` 로 `/proc/modules` 를 필드별로 나눕니다[17]. 효력이 있는 modprobe 설정 전체는 `modprobe -c` 로 찍습니다[8].

메모리 이미지에서는 Volatility 3 을 씁니다[19].

```
vol -f memory.lime linux.lsmod
vol -f memory.lime linux.malware.modxview
vol -f memory.lime linux.module_extract --base 0x주소
```

`linux.lsmod` 는 모듈 목록을 읽고, `linux.malware.check_modules` 는 모듈 목록과 sysfs 정보를 비교하고, `linux.malware.hidden_modules` 는 메모리를 긁어 숨은 모듈을 찾습니다[19]. `linux.malware.modxview` 는 세 결과를 모아 모듈마다 `In procfs`, `In sysfs`, `In scan`, `Taints` 열로 보여 주고, `linux.module_extract` 는 주어진 주소에서 ELF 파일을 다시 만듭니다[19]. `malware` 가 빠진 옛 이름(`linux.check_modules`·`linux.hidden_modules`·`linux.modxview`)은 폐기 예정으로 표시돼 있고 제거 날짜는 2026-06-07 로 적혀 있습니다[19]. 메모리 분석의 일반 절차는 [메모리 분석](../../03-techniques/analysis/memory-analysis.md), 루트킷 판단 흐름은 [루트킷 찾기](../../03-techniques/analysis/rootkit-detection.md) 에서 다룹니다.

교차 비교 도구의 탐지율은 시험 조건에 따라 다릅니다. Nagy(2025)는 커널 27개 판, 루트킷 55개(오픈소스 35개, VirusTotal 수집 20개)로 시험했습니다[21]. 오픈소스 35개 가운데 31개는 커널 객체 직접 조작 (Direct Kernel Object Manipulation, DKOM) 으로 모두 모듈 목록에서 자기를 뺐고, 4개는 함수 후킹으로 숨었습니다[21]. 이 조건에서 `linux.check_modules` 는 오픈소스 35개 중 13개, 수집한 20개 중 모듈 목록만 고친 10개를 찾았고, 모듈 목록·kset·모듈 트리·vmap 목록과 트리·버그 목록·ftrace 모듈 맵까지 7개 출처를 비교한 논문의 플러그인은 55개를 모두 찾았습니다[21]. 함수 후킹으로 숨는 모듈은 출처 사이에 어긋남을 만들지 않고 목록에 그대로 보입니다[21].

## 교차 검증

| 맞춰 볼 기록 | 확인할 것 |
|---|---|
| 설정 파일 ↔ [패키지 파일 변조 확인](../packages/package-verify.md)·[dpkg·apt 기록](../packages/dpkg-apt.md)·[rpm·dnf·yum 기록](../packages/rpm-dnf.md) | 설정 파일과 `.ko` 가 패키지가 깐 것인지, 사람이 만들거나 고친 것인지 |
| 설정 파일 시각 ↔ [셸 명령 기록](../execution/shell-history/index.md)·[감사 로그의 실행 기록](../execution/auditd-execve.md) | 파일을 바꾼 시점에 `insmod`·`modprobe`·편집기를 실행한 계정 |
| taint 메시지 ↔ [커널 로그](../system-info/kernel-log.md)·[부팅과 종료 기록](../system-info/boot-shutdown.md) | 어느 부팅에서 처음 트리 밖·서명 없는 모듈이 실렸는지 |
| `systemd-modules-load` 항목 ↔ [systemd 서비스와 타이머](systemd-units.md) | 같은 부팅에 함께 켜진 수상한 서비스 |
| 메모리의 모듈 목록 ↔ 라이브 `lsmod`·`/proc/modules` | 메모리에만 있는 모듈, 라이브 목록에서 빠진 모듈 |
| 모듈 자동 적재 ↔ [udev 규칙](udev-rules.md) | 장치 이벤트로 모듈이나 명령이 불렸는지 |

지속성 흔적 전체를 차례로 살펴보는 흐름은 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md) 에서 다룹니다.

## 실습

NIST CFReDS 등에 공개된 Linux 디스크·메모리 이미지로 다음 질문을 풀어 봅니다.

1. 네 곳의 `modules-load.d` 와 Ubuntu 의 `/etc/modules` 에 적힌 모듈을 모두 모으면 몇 개이고, 그 가운데 어느 패키지에도 속하지 않는 파일에 적힌 것은 무엇인가?
2. `modprobe.d` 설정에 `install`·`remove` 줄이 있는가? 있다면 어떤 명령을 부르고, 그 파일은 언제 바뀌었는가?
3. 저널에서 부팅마다 `systemd-modules-load` 가 실은 모듈 목록이 달라진 부팅이 있는가?
4. 커널 로그에 `loading out-of-tree module` 이나 `module verification failed` 줄이 있는가? 있다면 처음 나온 부팅과 모듈 이름은 무엇인가?
5. 메모리 이미지가 있다면 `linux.malware.modxview` 에서 `In procfs`·`In sysfs`·`In scan` 가운데 하나라도 거짓인 모듈이 있는가?

## 참고 문헌

1. systemd, modules-load.d(5). https://github.com/systemd/systemd/blob/main/man/modules-load.d.xml
2. systemd, systemd-modules-load.service(8). https://github.com/systemd/systemd/blob/main/man/systemd-modules-load.service.xml
3. systemd v255·v252, man/standard-conf.xml, man/modules-load.d.xml. https://github.com/systemd/systemd/blob/v255/man/standard-conf.xml , https://github.com/systemd/systemd/blob/v252/man/standard-conf.xml
4. systemd v255·v252, src/modules-load/modules-load.c, src/shared/module-util.c, src/basic/constants.h(v255)·def.h(v252). https://github.com/systemd/systemd/blob/v255/src/modules-load/modules-load.c , https://github.com/systemd/systemd/blob/v255/src/shared/module-util.c , https://github.com/systemd/systemd/blob/v255/src/basic/constants.h , https://github.com/systemd/systemd/blob/v252/src/modules-load/modules-load.c , https://github.com/systemd/systemd/blob/v252/src/shared/module-util.c , https://github.com/systemd/systemd/blob/v252/src/basic/def.h
5. Ubuntu systemd 패키지(noble-updates), debian/systemd.links. https://git.launchpad.net/ubuntu/+source/systemd/tree/debian?h=ubuntu/noble-updates
6. Ubuntu kmod 패키지(noble), debian/kmod.postinst, kmod.dirs, kmod.links. https://git.launchpad.net/ubuntu/+source/kmod/tree/debian?h=ubuntu/noble
7. kmod, modprobe.d(5). https://github.com/kmod-project/kmod/blob/master/man/modprobe.d.5.scd
8. kmod, modprobe(8). https://github.com/kmod-project/kmod/blob/master/man/modprobe.8.scd
9. kmod, lsmod(8), modinfo(8). https://github.com/kmod-project/kmod/tree/master/man
10. Linux kernel, Documentation/admin-guide/sysctl/kernel.rst. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/sysctl/kernel.rst
11. Linux kernel, Documentation/admin-guide/tainted-kernels.rst. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/tainted-kernels.rst
12. Linux kernel, kernel/module/main.c, kernel/module/signing.c. https://github.com/torvalds/linux/blob/master/kernel/module/main.c , https://github.com/torvalds/linux/blob/master/kernel/module/signing.c
13. Linux kernel, include/uapi/linux/module_signature.h. https://github.com/torvalds/linux/blob/master/include/uapi/linux/module_signature.h
14. proc(5), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
15. ForensicArtifacts, artifacts/data/linux.yaml (KernelModules, LoadedKernelModules, LinuxInitrdFiles). https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
16. UAC, artifacts/live_response/system (kernel_modules, kernel_tainted_state, lsmod, modinfo). https://github.com/tclahr/uac/tree/main/artifacts/live_response/system
17. Velociraptor, Linux.Proc.Modules. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Proc/Modules.yaml
18. dissect.target, plugins/os/unix/linux/modules.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/modules.py
19. Volatility 3, framework/plugins/linux (lsmod, module_extract, malware/check_modules, malware/hidden_modules, malware/modxview). https://github.com/volatilityfoundation/volatility3/tree/develop/volatility3/framework/plugins/linux
20. Linux Audit, audit-documentation, specs/messages/message-dictionary.csv. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
21. Roland Nagy, "Detecting hidden kernel modules in memory snapshots", Forensic Science International: Digital Investigation 53 (2025) 301928 (DFRWS USA 2025). https://doi.org/10.1016/j.fsidi.2025.301928
