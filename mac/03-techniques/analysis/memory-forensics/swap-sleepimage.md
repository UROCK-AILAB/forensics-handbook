---
title: "스왑과 잠자기 이미지"
parent: "메모리 분석"
grand_parent: "기법 · 분석"
nav_order: 2100
---

# 스왑과 잠자기 이미지 (swapfile·sleepimage)

메모리 내용 일부가 디스크로 내려와 남는 두 가지 파일이고, 둘 다 암호화를 전제로 설계되어 있어서 내용보다 파일의 존재와 크기, 시각을 먼저 봅니다.

## 언제 쓰나

메모리를 확보하지 못했거나 이미 꺼진 맥의 디스크 이미지만 있을 때, 메모리에서 디스크로 내려온 흔적을 확인하려고 봅니다. 윈도우의 pagefile.sys·hiberfil.sys와 비슷한 자리에 있는 파일이지만, macOS 쪽은 xnu 소스에 스왑 암호화 코드가 있고 잠자기 이미지 헤더에도 암호화 필드가 있습니다[7][3]. 실행 중인 메모리를 떠내는 방법은 [메모리 확보 (Acquisition)](memory-acquisition.md)에서 다룹니다.

## 스왑 파일 (swapfile)

### 위치와 버전

macOS 10.15 Catalina부터 시동용 APFS 컨테이너에는 볼륨이 최소 다섯 개 있고, 그중 VM 볼륨은 암호화하지 않은 볼륨이고, macOS는 이 볼륨에 암호화된 스왑 파일을 둡니다[1]. 볼륨이 나뉘는 구조는 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../../01-foundations/disk-volume/volume-group-firmlinks.md)와 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md)에서 설명합니다.

현재 xnu 소스(main)는 macOS용 빌드(`XNU_TARGET_OS_OSX`)에서 스왑 파일 이름을 아래처럼 정합니다[8].

```c
SWAP_VOLUME_NAME  "/System/Volumes"
SWAP_FILE_NAME    SWAP_VOLUME_NAME "/VM/swapfile"
```

| 대상 | 스왑 파일 경로 |
|---|---|
| macOS | `/System/Volumes/VM/swapfile` 뒤에 번호 |
| xnu의 그 밖의 대상 OS | `/private/var/vm/swapfile` 뒤에 번호 |

스왑 파일 이름은 기본 이름 뒤에 파일 번호를 붙인(`"%s%d"`) swapfile0, swapfile1 형태입니다[7]. 위 표는 현재 소스 기준이라, 10.15 이전 macOS에서 쓰던 경로는 실제 기기에서 확인합니다.

### 크기와 개수

| 항목 | macOS | 그 밖의 대상 OS | 출처 |
|---|---|---|---|
| 최소 크기 (`MIN_SWAP_FILE_SIZE`) | 256MB | 64MB | [8] |
| 최대 크기 (`MAX_SWAP_FILE_SIZE`) | 1GB | 128MB | [8] |
| 파일 개수 상한 (`VM_MAX_SWAP_FILE_NUM`) | 100 | 5 | [7] |

새 스왑 파일은 최대 크기로 먼저 잡고, 미리 할당하지 못하면 크기를 반씩 줄여 가며 최소 크기까지 다시 시도합니다[7]. 그래서 macOS에서는 1GB가 아닌 스왑 파일이 있어도 미리 할당에 실패했던 때에 만든 파일일 수 있고, 크기만으로 이상하다고 보지 않습니다.

### 암호화

스왑 암호화는 xnu 소스에서 `#if ENCRYPTED_SWAP` 으로 켜지는 코드이고, AES-XTS(`libkern/crypto/aesxts.h`)를 씁니다. 페이지를 내보낼 때(swapout) `vm_swap_encrypt()` 로 암호화하고 다시 읽을 때(swapin) `vm_swap_decrypt()` 로 복호화합니다[7]. 암호화 키는 스왑 암호화를 초기화할 때 `cc_rand_generate()` 로 무작위로 만들고, 같은 소스에는 이 키를 디스크에 저장하는 코드가 없습니다[7]. 어떤 빌드에서 `ENCRYPTED_SWAP` 이 켜지는지와 재부팅할 때 스왑 파일을 지우는지는 소스만으로 알 수 없어 실제 기기에서 확인해야 합니다. 스왑 코드가 든 소스 파일 이름은 `vm_compressor_backing_store` 이지만[7][8], 스왑 안의 페이지가 메모리 압축기(compressor)로 압축된 형태인지는 공개된 설명이 없습니다.

## 잠자기 이미지 (sleepimage)

### 언제 생기나

잠자기 이미지 (hibernation image)는 잠자기에 들어갈 때 메모리 사본을 디스크에 쓴 파일입니다. 이미지를 쓸지는 `pmset` 의 `hibernatemode` 값이 정합니다[2].

| `hibernatemode` | 동작 | 기본값 |
|---|---|---|
| 0 | 메모리를 저장 장치에 백업하지 않음 | 데스크톱 기본 |
| 3 | 메모리 사본을 디스크에 쓰고, 잠자는 동안 메모리에 전원을 유지 | 휴대용 기본 |
| 25 | 메모리 사본을 디스크에 쓰고, 메모리 전원을 끊음 | `pmset` 으로만 설정 가능 |

이미지가 실제로 쓰이는지는 `standby` 와 `autopoweroff` 값에도 달려 있습니다[2]. `standby` 는 일정 시간 잠든 뒤 자동으로 hibernate 하는 설정이고, `standbydelayhigh`·`standbydelaylow` 는 이미지를 쓰고 메모리 전원을 끄기까지의 지연(초)입니다. `autopoweroff` 는 `autopoweroffdelay` 초 동안 잠든 뒤 이미지를 쓰고 더 낮은 전력 상태로 가는 설정입니다[2]. `destroyfvkeyonstandby` 를 켜면 standby로 갈 때 FileVault 키를 지우고, 기본값은 키를 유지합니다[2]. FileVault 키를 다루는 방법은 [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md)를 봅니다.

이미지 파일의 위치는 `hibernatefile` 설정이 가리키고, 루트 볼륨 위의 파일만 가리킬 수 있습니다[2]. 기본 경로와, Apple 실리콘 맥에서 `hibernatemode` 25나 잠자기 이미지를 쓰는지는 조사 대상 맥의 `pmset` 설정으로 확인합니다. 잠자기에 들고 깬 기록은 [전원·잠자기 기록 (pmset)](../../../02-artifacts/logs/power-events.md)에서 다룹니다.

### 헤더 구조

이미지 헤더는 xnu의 `iokit/IOKit/IOHibernatePrivate.h` 에 `IOHibernateImageHeader` 구조체로 정의되어 있습니다[3]. 시그니처 필드 `signature`(uint32)에 들어가는 값은 네 가지입니다.

| 상수 | 값 |
|---|---|
| `kIOHibernateHeaderSignature` | `0x73696d65` |
| `kIOHibernateHeaderInvalidSignature` | `0x7a7a7a7a` |
| `kIOHibernateHeaderOpenSignature` | `0xf1e0be9d` |
| `kIOHibernateHeaderDebugDataSignature` | `0xfcddfcdd` |

암호화와 관련된 필드로 `encryptStart`·`encryptEnd`(uint64)가 있고, 모드 플래그 `kIOHibernateModeEncrypt` 의 값은 `0x00000004` 입니다[3]. 그 밖에 `imageSize`, `image1Size`, `pageCount`, `sleepTime`(uint64), `compression`, `machineSignature`, `kernelSlide` 같은 필드가 있고, arm64 빌드(`#if defined(__arm64__)`)에만 `imageHeaderHMAC`, `handoffHMAC`, `image1PagesHMAC`, `image2PagesHMAC` 같은 HMAC 필드(크기 `HIBERNATE_HMAC_SIZE`)이 더 있습니다[3]. 구조체 앞쪽 필드의 순서는 `imageSize`(u64), `image1Size`(u64), `restore1CodePhysPage`(u32), `reserved1`(u32), `restore1CodeVirt`(u64)로 시작하고, 필드별 바이트 오프셋은 실제 데이터로 확인합니다. `sleepTime` 은 맥 절대 시각일 수도 유닉스 시각일 수도 있으므로, 값을 읽으면 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)의 기준들을 모두 대입해 보고 파일 시각과 맞춰 봅니다.

아래는 명세의 시그니처 값을 바이트로 풀어 쓴 예시이고, 실제 데이터에서 읽은 값이 아닙니다. 파일 안에서는 어느 바이트 순서로도 보일 수 있어 두 순서를 모두 적습니다.

```
kIOHibernateHeaderSignature = 0x73696d65
큰 쪽부터(빅엔디언)      73 69 6d 65   ASCII "sime"
작은 쪽부터(리틀엔디언)  65 6d 69 73   ASCII "emis"
```

## 절차

1. **스왑 파일 목록을 적습니다.** 디스크 이미지의 VM 볼륨에서 스왑 파일마다 이름과 크기, 파일 시스템 시각을 기록합니다.
2. **잠자기 설정을 확인합니다.** `hibernatemode`, `standby`, `autopoweroff`, `hibernatefile` 값으로 이 맥이 이미지를 쓰는 설정이었는지, 이미지 파일이 어디 있어야 하는지 정합니다.
3. **잠자기 이미지 헤더를 확인합니다.** `hibernatefile` 이 가리키는 파일에서 위 시그니처 값을 두 바이트 순서로 모두 찾아보고, 찾은 위치와 값을 기록합니다.
4. **파일 시각을 타임라인에 넣습니다.** 스왑 파일과 잠자기 이미지의 시각을 [타임라인 작성 (Timeline)](../timeline/index.md)에 넣고 전원·잠자기 기록과 나란히 봅니다.

## 결과를 어떻게 해석하나

**증명하는 것.** 스왑 파일이 있으면 시스템이 그 파일을 만든 적이 있다는 뜻이고, 개수와 크기는 그 무렵 시스템이 스왑 공간을 얼마나 잡았는지 보여 줍니다. 잠자기 이미지의 존재와 크기, 수정 시각은 마지막으로 hibernate 한 시점의 단서가 될 수 있습니다[3].

**증명하지 못하는 것.** 스왑은 암호화 코드를 거쳐 기록되고, 이미지 헤더에도 암호화 범위 필드와 암호화 모드 플래그가 있습니다. 그래서 두 파일 모두 본문을 그대로 문자열 검색해서 문서 내용이나 암호를 얻기는 어렵고, 볼 수 있는 것은 파일의 존재와 개수, 크기, 시각 수준입니다[7][1][3]. `kIOHibernateHeaderInvalidSignature` 는 이름으로 보면 유효하지 않은 헤더를 뜻하지만 어떤 때 이 값이 들어가는지는 공개된 설명이 없으므로, 이 값만으로 이미지가 복원에 쓰였다거나 지워지려 했다고 쓰지 않습니다. Volatility 같은 도구로 잠자기 이미지를 곧바로 분석할 수 있는지는 도구 문서와 실제 데이터로 확인합니다.

보고서에는 "VM 볼륨에 스왑 파일이 몇 개 있었고 가장 최근 수정 시각은 이때이다", "`hibernatefile` 이 가리키는 파일의 헤더 시그니처가 이 값이고 수정 시각은 이때이다" 처럼 파일로 확인되는 만큼만 씁니다.

## 함정과 한계

xnu 소스의 경로와 크기 값은 현재 main 기준이라서, 조사 대상 macOS 버전의 소스와 다를 수 있습니다. 스왑 파일을 재부팅 때 지우는지 알려져 있지 않으므로 스왑 파일이 없다는 사실만으로 누군가 지웠다고 판단하지 않고, 잠자기 이미지가 없을 때도 `hibernatemode` 가 0인 데스크톱이었는지부터 확인합니다. 암호화를 푸는 방법은 이 페이지에서 다루지 않고, 암호화된 증거 전반은 [암호화된 증거 다루기 (Encrypted Evidence)](../encrypted-evidence/index.md)에서 다룹니다.

## 참고 문헌

1. Apple, Apple Platform Security (2026년 8월 판, PDF) — https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf (APFS "Multiple volumes" 절)
2. pmset(1) man page (Xcode man page 미러, keith.github.io — Apple 호스팅 아님) — https://keith.github.io/xcode-man-pages/pmset.1.html
3. Apple xnu iokit/IOKit/IOHibernatePrivate.h — https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/iokit/IOKit/IOHibernatePrivate.h
7. Apple xnu osfmk/vm/vm_compressor_backing_store.c — https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/osfmk/vm/vm_compressor_backing_store.c
8. Apple xnu osfmk/vm/vm_compressor_backing_store_internal.h — https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/osfmk/vm/vm_compressor_backing_store_internal.h
