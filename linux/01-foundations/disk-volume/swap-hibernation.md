---
title: "스왑과 최대 절전"
parent: "기반 · 디스크와 볼륨"
nav_order: 140
---

# 스왑과 최대 절전 (Swap·Hibernation)

스왑 영역은 첫 페이지 끝의 서명으로 알아보고, 최대 절전 이미지를 쓴 뒤 되살리지도 그 스왑을 다시 켜지도 않았다면 그 서명이 `S1SUSPEND` 로 바뀌어 있습니다.

## 이 형식을 쓰는 아티팩트

스왑 (swap) 은 메모리가 모자랄 때 커널이 페이지를 내보내는 디스크 영역입니다. 디스크 파티션이나 LVM 논리 볼륨 같은 블록 장치와 파일 시스템 안의 파일이 스왑이 될 수 있고, 어느 경우든 영역의 첫 페이지에 같은 머리글이 있습니다[1][3]. 최대 절전 (hibernation) 은 커널의 swsusp 가 기기 상태를 활성 스왑에 저장한 뒤 재부팅하거나 전원을 끄는 기능이라서, 최대 절전 이미지도 이 스왑 영역 안에 들어갑니다[7].

이 구조와 엮인 흔적은 아래와 같습니다.

| 흔적 | 위치 | 알려 주는 것 |
|---|---|---|
| 스왑 머리글 | 스왑 영역 첫 페이지 | 스왑 판, 크기, UUID, 라벨, 최대 절전 서명 |
| 스왑 설정 | `/etc/fstab` 의 형식 `swap` 줄 | 부팅 때 켜는 스왑 장치나 파일[4] |
| 암호화 스왑 설정 | `/etc/crypttab` 의 `swap` 옵션 | 부팅마다 새로 만드는 암호화 스왑[19] |
| 현재 스왑 | `/proc/swaps`, `/proc/meminfo` 의 `SwapTotal`·`SwapFree`·`SwapCached` | 라이브 시스템에서 쓰는 스왑과 사용량[11] |
| 되살릴 장치 지정 | 커널 명령줄(`/proc/cmdline`)의 `resume=`·`resume_offset=` | 최대 절전 이미지를 읽을 장치와 위치[6][11] |
| 최대 절전 동작 설정 | `/etc/systemd/sleep.conf`, `/run/systemd/sleep.conf`, `/usr/lib/systemd/sleep.conf` 와 각 `sleep.conf.d/*.conf` | 허용한 절전 방식과 모드[12] |
| 되살릴 위치 기록 | EFI 변수 `HibernateLocation` | EFI 로 부팅한 기기에서 최대 절전할 때 systemd 가 적은 스왑 위치[13] |
| 잠들기·깨어나기 기록 | systemd 저널, 커널 로그 | 절전 방식과 시각, 이미지 크기[5][6][13] |
| 잠들기 전후 훅 | `/usr/lib/systemd/system-sleep/` | 잠들 때와 깰 때 실행되는 프로그램[16] |

### 배포판 기본 배치

| 항목 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|
| 설치기 기본 스왑 | 스왑 파일 `/swap.img`[21] | 기본 배치에 `swap` 이 들어 있고 `swap_is_recommended = True`[22] |
| fstab 에 들어가는 줄 | `/swap.img none swap sw 0 0` (탭으로 구분)[21] | LVM 자동 배치면 스왑 LV 이름이 `swap` 이므로 `/dev/mapper/` 아래 `-swap` 으로 끝나는 장치[23] |
| 파일 권한과 속성 | `umask 0066` 으로 만들고 `chattr +C` 를 시도[21] | 해당 없음(블록 장치) |

설치기 표는 설치기 코드 기준이고, 실제 배포판에 실린 판과 세부가 다를 수 있습니다. 검체에서는 `/etc/fstab` 의 `swap` 줄과 [LVM 백업 파일](lvm.md)로 실제 배치를 확인합니다. Ubuntu 설치기는 권장 크기가 0 이면 스왑 파일을 만들지 않으므로 `/swap.img` 가 없는 설치도 있습니다[21].

메모리 안에서만 도는 스왑도 있습니다. zram 은 RAM 에 압축 블록 장치 `/dev/zramN` 을 만들고 이것을 스왑으로 쓸 수 있습니다[10]. zswap 은 스왑으로 나갈 페이지를 RAM 풀에 압축해 두었다가 풀이 차면 LRU 순서로 실제 스왑 장치에 내보냅니다[9]. zram 도 `CONFIG_ZRAM_WRITEBACK` 과 `backing_dev` 를 설정하면 한동안 쓰지 않은 페이지나 압축되지 않는 페이지를 뒤쪽 저장 장치(파티션)에 씁니다[10].

## 구조

### 스왑 머리글

머리글은 스왑 영역의 첫 페이지 한 장입니다. 페이지 끝 10바이트에 서명이 있고, 1024바이트 뒤부터 정보 칸이 이어집니다[1]. 커널은 첫 페이지를 늘 불량 페이지로 표시해 스왑 데이터 자리로 쓰지 않습니다[1].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x000 | 1024 | `bootbits` | 디스크 라벨이나 부트 로더 자리. 머리글은 이 자리를 쓰지 않지만, mkswap 은 이전 파일 시스템을 가리려고 첫 블록을 지웁니다(디스크 라벨이 있으면 거부)[3] |
| 0x400 | 4 | `version` | 1 |
| 0x404 | 4 | `last_page` | 마지막 페이지. libblkid 는 이 값에 페이지 크기를 곱해 스왑 크기로 알립니다[2] |
| 0x408 | 4 | `nr_badpages` | 불량 페이지 수 |
| 0x40C | 16 | `sws_uuid` | UUID |
| 0x41C | 16 | `sws_volume` | 라벨 |
| 0x42C | 468 | `padding[117]` | 빈 칸 |
| 0x600 | 4×n | `badpages[]` | 불량 페이지 목록 |
| 페이지 끝 − 10 | 10 | `magic` | `SWAPSPACE2` (옛 형식은 `SWAP-SPACE`) |

서명 자리는 페이지 크기를 따라 움직입니다. 4KiB 페이지면 0xFF6 이고, libblkid 는 0xFF6, 0x1FF6, 0x3FF6, 0x7FF6, 0xFFF6 다섯 곳(페이지 4KiB~64KiB)을 차례로 봅니다[2]. libblkid 는 `version` 이 1 도 아니고 바이트 순서를 바꿔도 1 이 아니면, 또는 `last_page` 가 0 이면 스왑으로 인정하지 않습니다[2]. 옛 `SWAP-SPACE` 형식에는 LABEL 과 UUID 가 없습니다[2].

머리글에는 시각 칸이 없습니다. mkswap 은 기본으로 UUID 를 새로 만들고, `-U random`·`-U time` 으로 무작위 UUID 나 시각 기반 UUID 를 고를 수 있습니다[3].

### 최대 절전 머리글 (swsusp_header)

최대 절전 이미지를 저장할 때 커널은 스왑 머리글 페이지를 읽어 서명이 `SWAP-SPACE` 나 `SWAPSPACE2` 인지 봅니다. 맞으면 원래 서명을 `orig_sig` 로 옮기고 `sig` 에 `S1SUSPEND` 를 쓴 뒤, 이미지 시작 섹터와 플래그를 채워 다시 씁니다[5]. 서명이 없으면 커널 로그에 `PM: Swap header not found!` 를 남기고 저장하지 않습니다[5].

`swsusp_header` 는 페이지 끝에 붙은 구조체라서 오프셋은 페이지 끝에서 거꾸로 셉니다. 아래 표는 4KiB 페이지와 8바이트 `sector_t`(64비트 커널)로 계산한 값입니다[5].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0xFD8 | 4 | `hw_sig` | 하드웨어 서명. 플래그 `SF_HW_SIG` 가 있을 때만 씁니다 |
| 0xFDC | 4 | `crc32` | 이미지 CRC. 플래그 `SF_CRC32_MODE` 일 때만 씁니다 |
| 0xFE0 | 8 | `image` | 이미지가 시작하는 섹터 |
| 0xFE8 | 4 | `flags` | 되살리는 커널에 넘길 플래그 |
| 0xFEC | 10 | `orig_sig` | 원래 스왑 서명 |
| 0xFF6 | 10 | `sig` | `S1SUSPEND` |

`sig` 가 스왑 서명과 같은 자리에 있으므로, libblkid 는 이 자리에서 `S1SUSPEND` 를 보면 형식을 `swsuspend` 로 알립니다. 이 자리의 `S2SUSPEND`, `ULSUSPEND`, `LINHIB0001` 과 영역 맨 앞의 TuxOnIce 서명도 `swsuspend` 로 알립니다[2].

이미지는 기본으로 압축해서 저장합니다. 기본 압축기는 커널 설정 `CONFIG_HIBERNATION_DEF_COMP` 이 정하고, 커널이 아는 이름은 `lzo` 와 `lz4` 입니다[6]. 커널 명령줄에 `hibernate=nocompress` 가 있으면 압축하지 않습니다[7].

## 읽는 법

### 헥스로 한 번

스왑 파티션이면 파티션 시작에서, 스왑 파일이면 이미지에서 꺼낸 파일의 처음에서 0x400 과 0xFD0~0xFFF 를 봅니다. 아래는 4KiB 페이지로 가정하고 구조체에서 만든 예시입니다. UUID 는 지어낸 값입니다.

```
평소 스왑 (만든 예시)
00000400  01 00 00 00 ff ff 03 00  00 00 00 00 5a 1c 3e 7b  ............Z.>{
00000410  2d 94 4f 0a 81 6e c2 d7  39 a0 14 5b 00 00 00 00  -.O..n..9..[....
...
00000ff0  00 00 00 00 00 00 53 57  41 50 53 50 41 43 45 32  ......SWAPSPACE2
```

`version` 은 1, `last_page` 는 0x3FFFF(262143)입니다. 라벨 칸(0x41C)이 비어 있으므로 라벨 없이 만든 스왑입니다.

```
최대 절전 뒤 되살리지 않은 스왑 (만든 예시)
00000fd0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................
00000fe0  40 1a 00 00 00 00 00 00  00 00 00 00 53 57 41 50  @...........SWAP
00000ff0  53 50 41 43 45 32 53 31  53 55 53 50 45 4e 44 00  SPACE2S1SUSPEND.
```

0xFE0 의 `image` 는 0x1A40 섹터, 0xFEC 의 `orig_sig` 는 `SWAPSPACE2`, 0xFF6 의 `sig` 는 `S1SUSPEND` 입니다. 이 예시에서 `hw_sig`·`crc32`·`flags` 는 0 으로 두었고, 실제 검체에서는 플래그 값에 따라 채워져 있을 수 있습니다.

```
xxd -s 0x400 -l 64 swap.img
xxd -s 0xfd0 -l 48 swap.img
```

### 설정과 기록으로 한 번

1. `/etc/fstab` 에서 형식이 `swap` 인 줄을 찾습니다. `noauto` 가 붙은 줄은 `swapon -a` 가 건너뛰고, `pri=` 는 0~32767 우선순위, `discard` 계열은 SSD 에 버림 명령을 보내는 설정입니다[4]. fstab 해석은 [마운트 기록](../../02-artifacts/devices/mounts.md)에서 다룹니다.
2. `/etc/crypttab` 에 `swap` 옵션이 붙은 줄은 부팅마다 그 장치를 plain 모드로 암호화한 뒤 mkswap 으로 새로 포맷하는 설정입니다. 키 파일 칸에 `/dev/urandom` 을 쓰면 키가 매번 무작위로 바뀝니다[19][20]. LUKS 머리글과 crypttab 은 [LUKS 디스크 암호화](luks.md)에서 다룹니다.
3. 커널 명령줄에서 `resume=`, `resume_offset=`, `noresume`, `hibernate=`, `nohibernate` 를 찾습니다[6]. 스왑 파일로 최대 절전하려면 `resume=` 과 함께 `resume_offset=` 이나 `/sys/power/resume_offset` 으로 장치 안에서 스왑이 시작하는 페이지 위치를 알려 줘야 합니다[7][15].
4. `sleep.conf` 의 `[Sleep]` 절에서 `AllowHibernation=`, `AllowHybridSleep=`, `AllowSuspendThenHibernate=`, `HibernateMode=`, `HibernateDelaySec=` 를 봅니다[12]. `HibernateMode=` 값은 `/sys/power/disk` 에 쓰는 문자열이고, 커널이 받는 값은 `platform`, `shutdown`, `reboot`, `suspend`, `test_resume` 입니다[8][12]. suspend-then-hibernate 에서 배터리가 없으면 `HibernateDelaySec=` 기본값 2h 가 지난 뒤 최대 절전으로 넘어갑니다[12].
5. EFI 변수 `HibernateLocation` 을 봅니다. EFI 로 부팅한 기기에서 최대 절전할 때 systemd-sleep 이 고른 스왑을 JSON 으로 적은 값이고(`resume=` 이 없으면 이 변수가 꼭 있어야 합니다), 필드는 `uuid`, `offset` 과 경우에 따라 `autoSwap`, `kernelVersion`, `osReleaseId`, `osReleaseImageId`, `osReleaseVersionId`, `osReleaseImageVersion` 입니다[13]. 되살린 뒤에는 보통 systemd-hibernate-resume.service 가 이 변수를 지우고, 남은 변수는 systemd-hibernate-clear.service 가 지웁니다[14].
6. 저널과 커널 로그에서 잠들기·깨어나기 기록을 찾습니다(아래 "기록" 절).

### 기록

systemd-sleep 은 잠들기 직전에 `Performing sleep operation '%s'...` 를, 깨어난 뒤에 `System returned from sleep operation '%s'.` 를 저널에 남깁니다. 잠들기에 실패하면 끝 기록 대신 `Failed to put system to sleep. System resumed again: %m` 을 깨어남과 같은 MESSAGE_ID 로 남깁니다. 세 기록 모두 `SLEEP=` 필드에 절전 방식 이름이 들어 있습니다[13].

| 기록 | MESSAGE_ID | 카탈로그 제목 |
|---|---|---|
| 잠들기 시작 (`SD_MESSAGE_SLEEP_START`) | `6bbd95ee977941e497c48be27c254128` | System sleep state @SLEEP@ entered |
| 깨어남 (`SD_MESSAGE_SLEEP_STOP`) | `8811e6df2a8e40f58a94cea26f8ebf14` | System sleep state @SLEEP@ left |

MESSAGE_ID 와 필드를 읽는 법은 [systemd 저널](../logging/systemd-journal/index.md)에서 다룹니다[17][18].

커널은 최대 절전 코드 쪽 줄 앞에 `PM: hibernation: ` 을, 스왑에 이미지를 쓰고 읽는 코드 쪽 줄 앞에 `PM: ` 을 붙입니다[5][6]. 찾을 줄은 아래와 같습니다.

| 줄 | 뜻 |
|---|---|
| `PM: hibernation: hibernation entry` | 최대 절전 시작[6] |
| `PM: Using %u thread(s) for %s compression` | 압축 스레드 수와 압축기 이름[5] |
| `PM: Compressing and saving image data (%u pages)...` | 압축 저장 시작과 페이지 수[5] |
| `PM: Image size after compression: %lld kbytes` | 압축 뒤 이미지 크기[5] |
| `PM: hibernation: Wrote %u kbytes in %u.%02u seconds (%u.%02u MB/s)` | 쓴 양과 걸린 시간[5][6] |
| `PM: Image saving done` | 저장 끝[5] |
| `PM: hibernation: resume from hibernation` | 되살리기 시작[6] |
| `PM: Loading and decompressing image data (%u pages)...` | 압축 이미지 읽기[5] |
| `PM: hibernation: Read %u kbytes in %u.%02u seconds (%u.%02u MB/s)` | 읽은 양과 걸린 시간[5][6] |
| `PM: hibernation: resume failed (%d)` | 되살리기 실패[6] |
| `PM: hibernation: hibernation exit` | 최대 절전 코드에서 나옴[6] |
| `PM: Suspend image hardware signature mismatch (%08x now %08x); aborting resume.` | 하드웨어 서명이 달라 되살리기 중단[5] |

압축하지 않은 이미지면 `PM: Saving image data pages (%u pages)...` 와 `PM: Loading image data pages (%u pages)...` 가 대신 나옵니다[5]. 커널 로그 줄의 모양과 보관 위치는 [커널 로그](../../02-artifacts/system-info/kernel-log.md)에서 다룹니다.

## 포렌식에서 중요한 점

### 서명이 알려 주는 상태

최대 절전 이미지를 읽는 커널은 `S1SUSPEND` 를 보는 즉시 `orig_sig` 를 `sig` 자리로 되돌려 디스크에 다시 씁니다[5]. 하이브리드 절전에서 RAM 상태로 깨어난 경우에도 커널은 서명을 되돌립니다[5][6]. swapon 도 스왑을 켤 때 `S1SUSPEND`·`S2SUSPEND` 같은 옛 절전 서명을 보면 스왑 서명으로 다시 씁니다[4]. 그래서 전원이 꺼진 검체의 스왑에 `S1SUSPEND` 가 남아 있으면, 최대 절전 이미지를 쓴 뒤 되살리지도 그 스왑을 다시 켜지도 않은 상태입니다. 이 경우 스왑 안에 최대 절전 시점의 메모리 상태가 들어 있을 가능성이 크고, 기본 설정이면 압축돼 있습니다[6][7].

서명을 되돌리는 시점은 하드웨어 서명 비교보다 앞섭니다. 그래서 다른 기기에서 이미지를 되살리려다 `hw_sig` 가 달라 중단된 경우에도 서명은 이미 원래 서명(`orig_sig`)으로 돌아가 있고, 커널 로그의 mismatch 줄이 남습니다[5].

### 되살린 뒤 남는 것

되살린 뒤 서명은 평소 스왑과 구별되지 않습니다. 되살릴 때 커널은 서명만 되돌려 다시 쓰고, 하이브리드 절전에서 RAM 으로 깨어난 경우에는 이미지가 쓰였던 스왑 페이지를 해제합니다[5]. 이미지 조각이 남았는지는 서명만으로 알 수 없으므로 스왑 영역 전체를 살펴 확인합니다. swapon 에 `discard` 나 `discard=pages` 가 걸려 있으면 해제된 스왑 페이지에 SSD 버림 명령을 보내므로 잔재가 더 빨리 사라질 수 있습니다[4].

### 증명하는 것

- 스왑이 어디에 있는지(파티션·파일·LV·zram)와 부팅 때 켜지게 설정됐는지(fstab, crypttab), 라이브 시스템이라면 지금 켜져 있는지(`/proc/swaps`).
- 스왑 서명이 `S1SUSPEND` 면 최대 절전 이미지를 쓴 뒤 되살리지도 그 스왑을 다시 켜지도 않은 상태라는 것.
- 저널의 두 MESSAGE_ID 로 잠든 시각과 깨어난 시각, `SLEEP=` 로 절전 방식.
- 커널 로그 줄로 최대 절전 시작·끝, 이미지 크기, 되살리기 실패.
- EFI 변수 `HibernateLocation` 이 남아 있으면 systemd 가 최대 절전 위치를 적은 뒤 되살리면서 지우지 않았다는 것. 되살리지 못한 최대 절전의 단서일 가능성이 있습니다[13][14].

### 증명하지 못하는 것

- 스왑 안의 페이지가 어느 프로세스, 어느 시각의 것인지. 머리글에 그런 칸이 없습니다[1].
- 어떤 데이터가 스왑에 없었다는 것. zram·zswap 을 쓰면 페이지가 디스크에 닿지 않을 수 있고, 부팅마다 무작위 키로 새로 만드는 암호화 스왑은 전원이 꺼진 뒤 내용을 풀 수 없을 가능성이 큽니다[9][10][19][20].
- 최대 절전 기록이 없다는 것만으로 최대 절전을 한 적이 없다는 것. 되살리거나 swapon 으로 다시 켜면 서명은 평소와 같아집니다[4][5].

## 시각 해석

스왑 머리글과 `swsusp_header` 에는 시각 칸이 없습니다[1][5]. 스왑 파일의 파일 시스템 시각은 파일 시스템 규칙을 따르지만, 커널은 스왑 파일을 파일 시스템을 거치지 않고 직접 쓰므로[4] 파일 시각이 스왑을 마지막으로 쓴 시각을 반영하지 않을 가능성이 있습니다.

잠들기·깨어나기 시각은 저널 기록에서 얻습니다. 저널 시각은 UTC 기준으로 저장되며 읽는 법은 [systemd 저널](../logging/systemd-journal/index.md)에서 다룹니다. 잠들기 시작 기록은 잠들기 직전에, 깨어남 기록은 돌아온 뒤에 남으므로 두 기록 사이가 잠들어 있던 구간입니다[13]. 커널 링 버퍼 줄의 시각은 부팅 뒤 흐른 시간이므로 벽시계 시각으로 바꾸려면 저널이나 syslog 쪽 시각과 맞춰야 합니다([커널 로그](../../02-artifacts/system-info/kernel-log.md)).

## 함정

- 최대 절전은 늘 쓸 수 있는 기능이 아닙니다. `nohibernate` 가 있거나, 커널 잠금(lockdown)이 최대 절전을 막거나, secretmem·CXL 메모리를 쓰는 중이면 커널이 최대 절전을 거부합니다[6]. 검체의 커널 명령줄과 커널 로그로 먼저 확인합니다.
- `resume=` 이 없고 EFI 변수 `HibernateLocation` 으로도 위치를 넘길 수 없으면(EFI 부팅이 아닐 때 등) systemd-sleep 은 `No valid 'resume=' option found, refusing to hibernate.` 를 남기고 최대 절전을 하지 않습니다[13].
- 되살릴 이미지가 없으면 systemd-hibernate-resume 은 오류 없이 평소처럼 부팅을 이어 갑니다[14]. 되살리기 서비스가 돌았다는 것만으로 최대 절전을 했다고 볼 수 없습니다.
- 스왑 파일은 구멍이 없어야 합니다. cp·truncate 로 만든 파일은 swapon 이 거부하고, Btrfs 에서는 Linux 5.0 부터 nocow 속성이 붙은 파일만 스왑으로 씁니다[4]. 스왑 파일로 적혀 있는데 켜진 기록이 없다면 이 조건을 봅니다.
- 서명 자리 0xFF6 은 4KiB 페이지일 때입니다. 64KiB 페이지 커널이면 0xFFF6 을 봐야 합니다[2]. `swsusp_header` 오프셋도 페이지 크기와 `sector_t` 크기에 따라 달라집니다[5].
- dissect.target 의 fstab 파서는 형식이 `swap` 인 줄을 건너뜁니다[24]. 이 결과에 스왑 항목이 없다고 스왑이 없었던 것은 아닙니다.
- 최대 절전 이미지는 기본으로 압축해 저장하므로[6] 스왑을 평문 문자열로 검색하면 이미지 안의 내용을 다 찾지 못할 가능성이 있습니다.
- Block·Dewald(2017)가 만든 사용자 공간 힙 분석 플러그인은 힙 데이터가 든 페이지가 스왑으로 나가 있으면 힙 청크를 온전히 뽑지 못할 가능성이 크고, 두 저자는 스왑 공간을 지원하지 않는 점을 가장 중요한 한계로 꼽았습니다[26]. 메모리 덤프만 보고 "없다" 고 말하기 전에 스왑을 함께 봅니다.
- `/usr/lib/systemd/system-sleep/` 의 실행 파일은 잠들 때 `pre`, 깰 때 `post` 와 절전 방식 이름을 인자로 받아 실행되고, 환경 변수 `SYSTEMD_SLEEP_ACTION` 을 받습니다[13][16]. 절전·깨어남 때마다 실행되는 위치라서 지속성 흔적을 찾을 때 이 폴더를 봅니다([무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md)).

## 도구

- **blkid**: 형식을 `swap` 이나 `swsuspend` 로 알리고, 판(VERSION)에 `1`, `0`, `s1suspend` 같은 값을 넣습니다. `SWAPSPACE2` 면 `padding` 칸 일부가 0 일 때 UUID 와 라벨도 읽습니다[2].
- **swapon --show**, `/proc/swaps`: 라이브 시스템에서 켜진 스왑을 봅니다[4][11].
- **UAC**: Linux 에서 `free` 출력을 `free.txt` 로 모읍니다[25].
- **헥스 편집기**: 0x400 정보 칸과 0xFD8~0xFFF 를 직접 읽습니다.

메모리 수집과 분석 전반은 [메모리 수집](../../03-techniques/acquisition/memory-acquisition.md), [메모리 분석](../../03-techniques/analysis/memory-analysis.md)에서 다룹니다. 스왑을 담은 볼륨은 [LVM 논리 볼륨](lvm.md), [LUKS 디스크 암호화](luks.md), [파티션](partitions.md)을 함께 봅니다.

## 참고 문헌

1. Linux kernel, `include/linux/swap.h`. https://github.com/torvalds/linux/blob/master/include/linux/swap.h
2. util-linux, `libblkid/src/superblocks/swap.c`. https://github.com/util-linux/util-linux/blob/master/libblkid/src/superblocks/swap.c
3. util-linux, `mkswap(8)`. https://github.com/util-linux/util-linux/blob/master/disk-utils/mkswap.8.adoc
4. util-linux, `swapon(8)`. https://github.com/util-linux/util-linux/blob/master/sys-utils/swapon.8.adoc
5. Linux kernel, `kernel/power/swap.c`. https://github.com/torvalds/linux/blob/master/kernel/power/swap.c
6. Linux kernel, `kernel/power/hibernate.c`. https://github.com/torvalds/linux/blob/master/kernel/power/hibernate.c
7. Linux kernel, `Documentation/power/swsusp.rst`. https://github.com/torvalds/linux/blob/master/Documentation/power/swsusp.rst
8. Linux kernel, `Documentation/admin-guide/pm/sleep-states.rst`. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/pm/sleep-states.rst
9. Linux kernel, `Documentation/admin-guide/mm/zswap.rst`. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/mm/zswap.rst
10. Linux kernel, `Documentation/admin-guide/blockdev/zram.rst`. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/blockdev/zram.rst
11. Linux kernel, `Documentation/filesystems/proc.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/proc.rst
12. systemd, `systemd-sleep.conf(5)`. https://github.com/systemd/systemd/blob/main/man/systemd-sleep.conf.xml
13. systemd, `src/sleep/sleep.c`. https://github.com/systemd/systemd/blob/main/src/sleep/sleep.c
14. systemd, `systemd-hibernate-resume.service(8)`. https://github.com/systemd/systemd/blob/main/man/systemd-hibernate-resume.service.xml
15. systemd, `systemd-hibernate-resume-generator(8)`. https://github.com/systemd/systemd/blob/main/man/systemd-hibernate-resume-generator.xml
16. systemd, `systemd-suspend.service(8)`. https://github.com/systemd/systemd/blob/main/man/systemd-suspend.service.xml
17. systemd, `src/systemd/sd-messages.h`. https://github.com/systemd/systemd/blob/main/src/systemd/sd-messages.h
18. systemd, `catalog/systemd.catalog.in`. https://github.com/systemd/systemd/blob/main/catalog/systemd.catalog.in
19. systemd, `crypttab(5)`. https://github.com/systemd/systemd/blob/main/man/crypttab.xml
20. cryptsetup, `FAQ.md` 2.3 "How do I set up encrypted swap?". https://github.com/mbroz/cryptsetup/blob/main/FAQ.md
21. Canonical curtin, `curtin/swap.py`, `curtin/commands/swap.py`. https://github.com/canonical/curtin/blob/main/curtin/swap.py , https://github.com/canonical/curtin/blob/main/curtin/commands/swap.py
22. Anaconda, `data/profile.d/rhel.conf`. https://github.com/rhinstaller/anaconda/blob/main/data/profile.d/rhel.conf
23. blivet, `blivet/blivet.py` (`suggest_device_name`). https://github.com/storaged-project/blivet/blob/main/blivet/blivet.py
24. dissect.target, `dissect/target/plugins/os/unix/_os.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/_os.py
25. UAC, `artifacts/live_response/system/free.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/live_response/system/free.yaml
26. Frank Block, Andreas Dewald, "Linux memory forensics: Dissecting the user space process heap", Digital Investigation 22 (2017) S66–S75 (DFRWS 2017 USA). DOI 10.1016/j.diin.2017.06.002
