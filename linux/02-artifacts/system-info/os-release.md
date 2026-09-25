---
title: "배포판과 버전"
parent: "아티팩트 · 시스템 정보"
nav_order: 280
---

# 배포판과 버전 (os-release)

`/etc/os-release` 는 설치된 배포판이 자기 이름과 판을 밝혀 두는 텍스트 파일이고, 분석을 시작할 때 "이 이미지가 어떤 배포판의 몇 판인가" 를 정하는 첫 근거입니다.

## 무엇을 기록하나 · 왜 생기나

os-release 파일에는 운영체제를 알아보는 데 쓰는 이름·식별자·판 번호가 들어 있습니다[1]. 이 값은 배포판을 만든 쪽(벤더)이 정하고, 관리자는 대개 고치지 않습니다[1]. 프로그램은 이 파일을 읽어 운영체제와 판을 가리고, 화면의 "이 시스템 정보" 같은 곳에 이름과 지원 링크를 보여 줍니다[1].

포렌식에서는 이 값으로 로그 파일 이름(`auth.log` 인지 `secure` 인지), 패키지 기록의 위치(dpkg 인지 rpm 인지), 기본 설정을 어느 쪽으로 읽을지 정합니다. 배포판을 잘못 잡으면 뒤따르는 해석이 모두 어긋나기 때문에 먼저 확인합니다.

## 위치와 버전별 차이

### 파일 두 곳과 우선순위

| 경로 | 역할 |
|---|---|
| `/usr/lib/os-release` | 벤더가 파일을 두는 권장 위치입니다[1]. |
| `/etc/os-release` | 이 파일이 있으면 이것만 읽고, 없을 때만 `/usr/lib/os-release` 를 읽습니다. 두 파일 내용을 섞지 않습니다[1]. |
| `/etc/initrd-release` | initrd(초기 램 디스크) 안에서 os-release 와 같은 역할을 하고, 이 파일이 있으면 initrd 단계라는 뜻입니다[1]. |
| `/usr/lib/extension-release.d/extension-release.IMAGE` | 확장 이미지가 자신을 밝히는 파일입니다. `IMAGE` 자리에는 확장 이미지 파일 이름에서 확장자를 뗀 부분이 들어가고, 확장 자신의 값은 `SYSEXT_ID=` 처럼 `SYSEXT_` 를 붙여 적습니다[1]. |
| `/run/host/os-release` | 컨테이너·샌드박스 관리자가 호스트의 os-release 를 이 경로로 넣어 줄 수 있습니다[1]. |

권장하는 모양은 `/etc/os-release` 가 `../usr/lib/os-release` 를 가리키는 상대 심볼릭 링크(symbolic link)입니다[1]. 절대 경로 링크는 chroot 나 initrd 환경에서 깨지기 때문에 상대 경로를 씁니다[1]. 두 파일은 부팅 초기부터 읽을 수 있어야 해서 루트 파일 시스템에 있어야 합니다[1].

### 배포판 계열마다 따로 있는 파일

os-release 는 두 계열에 공통이고, 그 밖에 계열마다 따로 쓰는 식별 파일이 있습니다. 아래 경로는 수집 도구가 모으는 목록에서 골랐습니다[2].

| 항목 | Debian·Ubuntu 계열 | RHEL·Fedora 계열 |
|---|---|---|
| os-release | `/etc/os-release`, `/usr/lib/os-release` | `/etc/os-release`, `/usr/lib/os-release` |
| 계열 전용 파일 | `/etc/debian_version` | `/etc/redhat-release`, `/etc/centos-release`, `/etc/rocky-release`, `/etc/oracle-release` |
| `ID_LIKE` 예 | `ID=ubuntu` 이면 `ID_LIKE=debian` | `ID=centos` 이면 `ID_LIKE="rhel fedora"` |

같은 수집 목록에는 계열을 가리지 않는 `/etc/lsb-release`(LSB 형식), `/etc/system-release`, `/etc/enterprise-release`, `/etc/SuSE-release` 도 들어 있습니다[2]. `ID_LIKE` 예는 명세가 든 예시이고[1], Ubuntu 24.04·RHEL 9 검체의 실제 값과 `/etc/os-release` 가 링크인지는 검체에서 `ls -l` 과 파일 내용으로 확인합니다. 로그인 전에 보여 주는 안내문 `/etc/issue`, `/etc/issue.net` 에도 배포판 이름이 들어 있을 수 있습니다[2].

## 구조

한 줄에 셸 변수 대입(`KEY=value`) 하나씩 적는 텍스트 파일이고, 인코딩은 UTF-8 입니다[1]. 셸 기능은 변수 대입만 쓸 수 있어서 `$VAR` 같은 변수 확장은 되지 않습니다[1]. 값에 공백이나 영문자·숫자 밖의 특수 문자가 있으면 큰따옴표나 작은따옴표로 감쌉니다[1]. `#` 으로 시작하는 줄은 주석이고, 빈 줄은 무시합니다[1]. 같은 키는 두 번 나오면 안 되지만, 나왔다면 뒤의 값을 씁니다[1]. 읽는 프로그램은 모르는 키를 무시해야 하고, 배포판이 새로 만든 키에는 `DEBIAN_BTS=` 처럼 배포판 이름을 앞에 붙이도록 권합니다[1].

주로 보는 키는 아래와 같습니다[1].

| 키 | 뜻 | 분석에서 쓰는 법 |
|---|---|---|
| `NAME` | 판 번호를 뺀 운영체제 이름. 없으면 `Linux` 로 봅니다. | 사람이 읽는 이름 |
| `ID` | 소문자 식별자. 없으면 `linux` 로 봅니다. | 계열 판단의 첫 기준 |
| `ID_LIKE` | 가까운 배포판의 `ID` 를 가까운 순서로 공백으로 나열 | `ID` 를 모를 때 계열 판단 |
| `PRETTY_NAME` | 화면에 보여 줄 이름. 판 번호가 들어갈 수도 있습니다. | 보고서에 옮길 이름 |
| `VERSION` / `VERSION_ID` | 사람이 읽는 판 / 스크립트용 판 번호 | 판 판단. 롤링 배포판은 둘 다 없을 수 있습니다. |
| `VERSION_CODENAME` | 판의 코드 이름 | 저장소 주소·설정과 맞춰 볼 때 |
| `VARIANT` / `VARIANT_ID` | 서버판·워크스테이션판 같은 갈래 | 기본 설정이 다를 수 있는 갈래 구분 |
| `BUILD_ID` | 처음 설치할 때 쓴 시스템 이미지의 식별자. 점진 업데이트로 `VERSION_ID` 가 바뀌어도 그대로일 수 있습니다. | 설치 기반 이미지 구분 |
| `IMAGE_ID` / `IMAGE_VERSION` | 통째로 만들어 배포하는 OS 이미지의 이름과 판 | 이미지 방식 배포 확인 |
| `RELEASE_TYPE` | `stable`, `lts`, `development`, `experiment` 가운데 하나. 없으면 `stable` 로 봅니다. | 장기 지원판인지 확인 |
| `SUPPORT_END` | 지원이 끝나는 첫날(`YYYY-MM-DD`) | 보안 업데이트가 끊긴 판인지 확인 |
| `CPE_NAME` | NIST CPE 형식 이름 | 취약점 자료와 맞춰 볼 때 |
| `DEFAULT_HOSTNAME` | `/etc/hostname` 이 없고 다른 설정도 없을 때 쓰는 호스트 이름 | 호스트 이름 판단의 마지막 후보 |
| `ARCHITECTURE` | 사용자 영역 프로그램이 요구하는 CPU 아키텍처. 하나만 지원할 때만 적습니다. | 아키텍처 판단 |

스크립트가 배포판과 판을 가릴 때는 `ID` 와 `VERSION_ID` 를 쓰고 `ID` 를 모르면 `ID_LIKE` 를 보며, 사람에게 보여 줄 때는 `PRETTY_NAME` 을 쓰도록 권합니다[1]. 분석에서도 같은 순서로 읽으면 됩니다.

아래는 명세의 형식에 맞춰 만든 예시입니다. 배포판 이름과 값은 지어낸 것입니다.

```
# 만든 예시
NAME="Example Linux"
VERSION="9.9 (Sample)"
ID=examplelinux
ID_LIKE="rhel fedora"
VERSION_ID="9.9"
PRETTY_NAME="Example Linux 9.9 (Sample)"
RELEASE_TYPE=lts
SUPPORT_END=2032-01-01
EXAMPLE_BUGZILLA_PRODUCT="Example Linux 9"
```

## 증거로서 의미

### 증명하는 것

- 이미지의 루트 파일 시스템에 설치된 배포판이 스스로를 무엇이라고 밝히는지 보여 줍니다.
- `SUPPORT_END` 가 있으면 그 판의 지원이 언제 끝나는지 알 수 있어서, 조사 시점에 보안 업데이트를 받던 판인지 따져 볼 수 있습니다[1].

### 증명하지 못하는 것

- 지금 실행 중인 커널의 판은 알려 주지 않습니다. 커널 판은 라이브 시스템의 `/proc/version` 과 `uname -a` 결과, 부팅 기록에서 확인합니다([실행 중인 프로세스 (/proc)](../execution/proc.md), [커널 로그](kernel-log.md)).
- 설치 날짜를 알려 주지 않습니다. 파일 안에 날짜가 없고, `BUILD_ID` 는 설치에 쓴 이미지의 식별자일 뿐입니다[1]. 설치 날짜는 [설치 날짜 가늠하기](install-date.md) 에서 여러 흔적으로 가늠합니다.
- 판을 언제 올렸는지 알려 주지 않습니다. 판을 올리면 파일이 새 판을 말하고 옛 판은 남지 않으므로, 과거 판은 [dpkg·apt 기록](../packages/dpkg-apt.md) 이나 [rpm·dnf·yum 기록](../packages/rpm-dnf.md) 에서 찾습니다.
- 내용이 참이라는 보장이 없습니다. 권한만 있으면 누구나 고칠 수 있는 텍스트 파일입니다.

보고서에는 "이 이미지의 `/etc/os-release` 는 배포판을 ○○, 판을 ○○으로 밝히고 있다" 처럼 파일이 말하는 만큼만 씁니다.

## 시각 해석

파일 안에는 사건 시각이 없습니다. `SUPPORT_END` 는 날짜 값이지만 지원 종료일일 뿐이고 어떤 일이 일어난 시각이 아닙니다[1].

시각은 파일 시스템의 타임스탬프에서 봅니다. 이 파일을 설치한 패키지가 갱신되면 파일을 새로 쓰면서 수정 시각(mtime)과 변경 시각(ctime)이 바뀔 가능성이 있습니다. 어느 패키지가 이 파일을 설치했는지는 검체의 패키지 기록에서 확인합니다. `/etc/os-release` 가 링크라면 링크 자체의 시각과 링크가 가리키는 `/usr/lib/os-release` 의 시각을 따로 봅니다. ext4 아이노드의 시각은 UTC 기준 epoch 초이고, 읽는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

## 함정과 한계

**도구가 여러 파일을 합쳐 읽습니다.** 명세는 한 파일만 쓰고 두 파일을 섞지 말라고 합니다[1]. 반면 dissect.target 은 `/etc/*-release` 에 걸리는 파일을 모두 열어 한 사전에 합치고, 나중에 읽은 파일의 같은 키가 앞의 값을 덮습니다[3]. `#` 으로 시작하는 줄은 건너뛰고, `=` 이 없는 줄(예 `/etc/redhat-release` 의 한 줄)은 `DISTRIB_DESCRIPTION` 키로 넣습니다[3]. 그래서 `/etc/os-release` 와 계열 전용 파일의 내용이 서로 다르면 도구 출력에 두 파일 값이 섞일 수 있습니다. 판 문자열은 `DISTRIB_DESCRIPTION` 과 `NAME`(없으면 `DISTRIB_ID`) + `VERSION`(없으면 `VERSION_ID`, `DISTRIB_RELEASE`) 가운데 긴 쪽을 씁니다[3]. plaso 도 os-release 의 `PRETTY_NAME`, lsb-release 의 `DISTRIB_DESCRIPTION`, 계열 전용 파일의 첫 줄, `Debian GNU/Linux ` 로 시작하는 issue 파일 첫 줄의 `\` 앞부분을 모두 같은 값 칸(`operating_system_product`)에 넣습니다[4]. 도구 출력 한 줄보다 파일 원문을 직접 봅니다.

**도구의 계열 판단은 os-release 를 보지 않을 수 있습니다.** dissect.target 은 `/etc/network/interfaces`, `/etc/debian_version`, `/etc/dpkg/` 가운데 하나가 있으면 Debian 계열로, `/etc/centos-release`, `/etc/fedora-release`, `/etc/redhat-release`, `/etc/sysconfig/network-scripts` 가운데 하나가 있으면 Red Hat 계열로 봅니다[3]. 이런 경로가 남아 있는 이미지는 os-release 내용과 다른 계열로 잡힐 수 있습니다.

**링크가 깨지면 읽지 못합니다.** dissect.target 은 `/etc/*-release` 만 찾기 때문에 `/usr/lib/os-release` 를 따로 보지 않습니다[3]. `/etc/os-release` 링크가 깨졌거나 지워졌다면 `/usr/lib/os-release` 를 직접 엽니다.

**절대 경로 링크는 분석 PC 를 가리킬 수 있습니다.** 이미지를 분석 PC 에 마운트하고 `/usr/lib/os-release` 같은 절대 경로 링크를 따라가면 분석 PC 자신의 파일이 열립니다. 명세가 상대 링크를 권하는 이유와 같은 문제입니다[1]. 링크 대상은 이미지 안에서 풀었는지 확인합니다.

**컨테이너·chroot·initrd 의 파일을 호스트 것으로 착각하기 쉽습니다.** 컨테이너 루트에서 보이는 `/etc/os-release` 는 컨테이너 이미지의 것이고, 호스트의 것은 `/run/host/os-release` 로 따로 들어올 수 있습니다[1]. initrd 안에서는 `/etc/initrd-release` 가 같은 역할입니다[1]. 컨테이너 수집은 [컨테이너 수집](../../03-techniques/acquisition/container-acquisition.md) 을 봅니다.

**수집본에 링크만 들어 있을 수 있습니다.** UAC 는 `/etc` 를 통째로 모으지만 `/usr/lib` 은 이 항목의 경로 밖입니다[5]. 수집본의 `/etc/os-release` 가 실제 내용인지 링크인지 먼저 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번 — 링크인지 파일인지

ext4 에서 링크 대상 문자열이 60바이트보다 짧으면 데이터 블록을 따로 쓰지 않고 아이노드의 `i_block` 칸(오프셋 0x28, 60바이트)에 그대로 적습니다[6]. `../usr/lib/os-release` 는 21바이트라서 아이노드만 보면 링크 대상을 알 수 있습니다. 아래는 ext4 명세로 만든 예시이고, `..` 는 생략한 바이트입니다.

```
# ext4 명세로 만든 예시 (아이노드 앞부분)
00000000  ff a1 00 00 15 00 00 00  .. .. .. .. .. .. .. ..
00000020  .. .. .. .. .. .. .. ..  2e 2e 2f 75 73 72 2f 6c   ../usr/l
00000030  69 62 2f 6f 73 2d 72 65  6c 65 61 73 65 00 00 00   ib/os-release...
```

1. 0x00 의 `ff a1` 은 리틀 엔디언 `i_mode` 0xA1FF 이고, 위 4비트 0xA000 이 심볼릭 링크(S_IFLNK)를 뜻합니다[6]. 일반 파일이면 0x8000(S_IFREG)입니다.
2. 0x04 의 `15 00 00 00` 은 `i_size_lo` 0x15 = 21바이트로, 링크 대상 문자열의 길이입니다[6].
3. 0x28 부터 21바이트가 링크 대상 `../usr/lib/os-release` 입니다. `.` 으로 시작하므로 상대 링크입니다.

일반 파일이면 내용이 데이터 블록에 있고, 그 블록을 텍스트로 읽으면 앞의 `KEY=value` 줄이 그대로 보입니다. ext4 구조는 [ext4](../../01-foundations/filesystem/ext4/index.md) 에 있습니다.

### 공개 도구로 한 번

이미지를 읽기 전용으로 마운트했다면 기본 명령으로 확인합니다. 마운트 위치는 `/mnt/evidence` 로 가정합니다.

```
ls -l /mnt/evidence/etc/os-release /mnt/evidence/usr/lib/os-release
readlink /mnt/evidence/etc/os-release
cat /mnt/evidence/usr/lib/os-release
ls -l /mnt/evidence/etc/*-release /mnt/evidence/etc/debian_version
```

`readlink` 결과가 `/` 로 시작하는 절대 경로라면 `cat /mnt/evidence/etc/os-release` 는 분석 PC 의 파일을 열 수 있으므로, 대상 경로 앞에 마운트 위치를 붙여 직접 엽니다. 계열 전용 파일과 os-release 의 값이 서로 맞는지도 같이 봅니다.

dissect.target 은 이 파일들로 `version` 속성을 만들고[3], 아키텍처는 `/bin/ls`(Red Hat 계열은 `/usr/bin/coreutils`, `/bin/sh`, `/bin/bash`) 의 ELF 머리에서 오프셋 4 의 EI_CLASS, 5 의 EI_DATA, 18 의 e_machine 을 읽어 정합니다[3]. plaso 는 전처리 단계에서 위의 파일들을 읽어 `operating_system_product` 값을 채웁니다[4]. 라이브 수집이라면 UAC 가 `uname -a` 결과를 함께 받습니다[5].

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 내용 |
|---|---|
| 계열 전용 파일(`/etc/debian_version`, `/etc/redhat-release` 등) | os-release 와 배포판·판이 맞는지[2] |
| [dpkg·apt 기록](../packages/dpkg-apt.md), [rpm·dnf·yum 기록](../packages/rpm-dnf.md) | 판 업그레이드 기록, 이 파일을 설치한 패키지 |
| [패키지 파일 변조 확인](../packages/package-verify.md) | 파일 내용이 패키지가 설치한 원본과 같은지 |
| `/proc/version`, `uname -a`([실행 중인 프로세스 (/proc)](../execution/proc.md)) | 실행 중 커널의 판. `/proc/version` 에는 `/proc/sys/kernel/ostype`, `osrelease`, `version` 의 내용이 들어 있습니다[7]. |
| [커널 로그](kernel-log.md), [부팅과 종료 기록](boot-shutdown.md) | 부팅 때 올라온 커널 판 |
| [호스트 이름·시간대·로캘](hostname-timezone.md) | `DEFAULT_HOSTNAME` 이 쓰였을 조건인지 |
| [설치 날짜 가늠하기](install-date.md) | `BUILD_ID` 와 설치 흔적 |

## 실습

공개 검체(NIST CFReDS 등의 Linux 디스크 이미지)를 하나 골라 아래 질문을 풀어 봅니다.

1. `/etc/os-release` 는 일반 파일인가, 링크인가? 링크라면 상대 경로인가?
2. `ID`, `ID_LIKE`, `VERSION_ID`, `PRETTY_NAME` 은 무엇인가? 계열 전용 파일의 내용과 맞는가?
3. dissect.target 이나 plaso 가 보여 주는 배포판 문자열은 파일 원문의 어느 키에서 왔는가?
4. 패키지 기록에 판을 올린 흔적이 있는가? 있다면 os-release 가 말하는 판과 맞는가?
5. 이미지 안에 컨테이너 이미지나 chroot 가 있다면, 그 안의 os-release 는 호스트의 것과 어떻게 다른가?

## 참고 문헌

1. systemd, os-release(5). https://github.com/systemd/systemd/blob/main/man/os-release.xml
2. ForensicArtifacts, `artifacts/data/linux.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
3. dissect.target, `plugins/os/unix/_os.py`·`linux/_os.py`·`linux/debian/_os.py`·`linux/redhat/_os.py`. https://github.com/fox-it/dissect.target/tree/main/dissect/target/plugins/os/unix
4. plaso, `preprocessors/linux.py`. https://github.com/log2timeline/plaso/blob/main/plaso/preprocessors/linux.py
5. UAC, `artifacts/files/system/etc.yaml`·`artifacts/live_response/system/uname.yaml`. https://github.com/tclahr/uac/tree/main/artifacts
6. Linux 커널 문서, ext4 `inodes.rst`·`ifork.rst`. https://github.com/torvalds/linux/tree/master/Documentation/filesystems/ext4
7. proc(5), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
