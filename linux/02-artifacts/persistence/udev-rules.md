---
title: "udev 규칙"
parent: "아티팩트 · 지속성"
nav_order: 560
---

# udev 규칙 (udev Rules)

udev 규칙은 장치가 붙거나 떨어지거나 상태가 바뀔 때마다 systemd-udevd 가 읽는 텍스트 파일이고, 규칙에 적힌 프로그램이 장치 이벤트마다 실행되므로 지속성 흔적을 찾을 때 규칙 디렉터리 넷을 모두 봐야 합니다.

## 무엇을 기록하나 · 왜 생기나

커널은 장치를 더하거나 빼거나 상태가 바뀔 때마다 장치 이벤트 (uevent) 를 보내고, udev 데몬인 systemd-udevd 가 이 이벤트를 받아 규칙과 대조합니다[1][3]. 규칙이 맞으면 장치 속성을 udev 데이터베이스에 쓰거나 `/dev/` 아래 링크를 만들거나 네트워크 인터페이스 이름을 바꾸고, 정해 둔 프로그램을 이벤트 처리의 한 단계로 실행하기도 합니다[1].

규칙 파일은 원래 패키지와 관리자가 장치 이름·권한을 맞추려고 두는 설정입니다. 규칙 하나로 "이런 장치가 붙으면 이 프로그램을 돌린다" 를 적을 수 있어서 지속성에도 쓰일 수 있습니다[6]. 규칙 파일은 설정이 남아 있다는 기록이고, 규칙이 실제로 돈 기록은 저널·커널 로그 같은 다른 곳에 남습니다.

udev 데이터베이스(`/run/udev/data/`)와 장치 연결 기록은 [USB 장치 연결 기록](../devices/usb.md) 에서 다룹니다. 이 쪽은 규칙 파일만 다룹니다.

## 위치와 버전별 차이

systemd-udevd 는 아래 네 디렉터리에서 규칙을 읽습니다[1].

| 디렉터리 | 성격 | 디스크 이미지에 남나 |
|---|---|---|
| `/usr/lib/udev/rules.d` | 시스템 규칙(패키지가 설치) | 남음 |
| `/usr/local/lib/udev/rules.d` | 시스템 규칙 | 남음 |
| `/run/udev/rules.d` | 휘발성 실행 시 디렉터리 | 남지 않음(휘발성 디렉터리)[1] |
| `/etc/udev/rules.d` | 관리자 규칙 | 남음 |

확장자가 `.rules` 인 파일만 읽고 다른 확장자는 무시합니다[1]. 네 디렉터리의 파일을 모두 모아 디렉터리와 상관없이 파일 이름 순으로 처리하고, 이름이 같은 파일은 하나만 씁니다[1]. 이름이 같으면 `/etc/` 의 파일이 가장 앞서고, `/run/` 의 파일이 `/usr/` 의 파일보다 앞섭니다[1]. `/etc/` 에 `/usr/lib/` 의 규칙 파일과 같은 이름으로 `/dev/null` 을 가리키는 링크를 두면 그 규칙 파일은 통째로 꺼집니다[1].

기준 배포판 두 곳은 규칙 디렉터리가 같고, systemd 판에 따라 쓸 수 있는 `udevadm` 명령이 다릅니다.

| 항목 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|
| systemd 판 | 255[9] | 252[10] |
| 배포판 규칙을 싣는 패키지 | `udev`, `/usr/lib/udev/rules.d/` 에 설치[9] | `systemd-udev`[10] |
| `udevadm verify`(systemd 254 부터)[4] | 있음 | 없음 |
| `udevadm cat`(systemd 258 부터)[4] | 없음 | 없음 |

규칙 디렉터리·우선순위와 `RUN` 동작은 systemd 252·255 와 최신 판이 같습니다[1].

## 구조

규칙 파일의 한 줄에는 키·연산자·값 식이 하나 이상 쉼표로 나뉘어 있고, 빈 줄과 `#` 로 시작하는 줄은 무시합니다[1]. systemd 가 싣는 규칙 파일처럼 줄 끝의 `\` 로 규칙 하나를 여러 줄에 나눠 쓰기도 합니다[5]. 키는 일치 키 (match key) 와 할당 키 (assignment key) 두 가지이고, 한 규칙의 일치 키가 모두 맞으면 할당 키가 적용됩니다[1].

| 연산자 | 뜻[1] |
|---|---|
| `==`, `!=` | 같음·다름 비교(일치 키) |
| `=` | 값을 넣음(목록이면 비우고 이 값 하나만) |
| `+=` | 목록에 더함 |
| `-=` | 목록에서 뺌 |
| `:=` | 마지막으로 넣고 뒤의 변경을 막음 |

일치 키에는 `ACTION`, `DEVPATH`, `KERNEL`·`KERNELS`, `SUBSYSTEM`·`SUBSYSTEMS`, `DRIVER`·`DRIVERS`, `ATTR{파일}`·`ATTRS{파일}`, `ENV{키}`, `TAG`·`TAGS`, `TEST`, `PROGRAM`, `RESULT` 가 있습니다[1]. 이름 끝에 `S` 가 붙은 키는 이벤트를 낸 장치뿐 아니라 sysfs 에서 부모 장치를 거슬러 올라가며 찾습니다[1]. 값에는 `*`, `?`, `[]`, `|` 패턴을 쓸 수 있습니다[1].

할당 키 가운데 조사에서 먼저 볼 것은 외부 프로그램을 부르는 키 셋입니다.

| 키 | 동작[1] |
|---|---|
| `RUN{program}` | 이벤트의 모든 규칙을 처리한 뒤 외부 프로그램을 실행합니다. 형식을 생략하면 `program` 입니다. 절대 경로가 아니면 `/usr/lib/udev` 에서 찾습니다. |
| `RUN{builtin}` | 외부 프로그램 대신 udev 내장 프로그램을 부릅니다. `program` 과 목록을 함께 쓰므로 `=`·`:=` 로 비우면 둘 다 지워집니다. |
| `PROGRAM` | 일치 여부를 가리려고 프로그램을 실행하고, 성공하면 참이 됩니다. 표준 출력은 `RESULT` 에 담깁니다. |
| `IMPORT{program}` | 프로그램을 실행하고 출력을 장치 속성으로 가져옵니다. `IMPORT{file}` 은 텍스트 파일을 읽어 가져옵니다. |

이 밖에 `NAME`(네트워크 인터페이스 이름), `SYMLINK`, `OWNER`·`GROUP`·`MODE`(장치 노드 권한), `ENV{키}`, `TAG`, `LABEL`·`GOTO`, `OPTIONS` 가 있습니다[1]. `RUN`·`PROGRAM`·`ENV`·`SYMLINK` 등의 값에는 `%k`(커널 장치 이름), `$devpath`, `$env{키}` 같은 치환을 쓸 수 있고, `RUN` 치환은 모든 규칙을 처리한 뒤 프로그램을 실행하기 직전에 이뤄집니다[1].

`RUN` 은 아주 짧게 끝나는 작업에만 쓰도록 정해져 있습니다[1]. systemd-udevd.service 의 기본 샌드박스 때문에 네트워크에 접속하거나 파일 시스템을 마운트·해제하는 프로그램은 규칙 안에서 돌 수 없고, 규칙에서 띄운 프로세스는 떼어 냈든 아니든 이벤트 처리가 끝나면 무조건 종료됩니다[1]. 오래 도는 프로세스는 서비스 유닛으로 만들고 장치 속성 `SYSTEMD_WANTS` 로 그 유닛을 끌어오면 됩니다[1]. 이벤트 하나를 기다리는 시간은 기본 180초이고, 넘으면 그 이벤트를 끝냅니다[3].

## 증거로서 의미

### 증명하는 것

- 규칙 파일이 있으면, 수집한 시점에 어떤 장치 이벤트(`ACTION`, `SUBSYSTEM`, `ATTRS{…}` 조건)에 어떤 프로그램을 걸어 두었는지가 드러납니다.
- 같은 이름의 파일이 여러 디렉터리에 있으면, 어느 파일이 실제로 쓰였는지를 우선순위 규칙으로 가릴 수 있습니다[1].
- `/etc/udev/rules.d` 에 `/dev/null` 링크가 있으면, 그 이름의 패키지 규칙을 누군가 끄도록 설정했다는 뜻입니다[1].
- 규칙 파일이 패키지 파일 목록에 없으면 패키지가 설치한 파일이 아니므로, 언제 누가 만들었는지를 따로 봐야 합니다. 패키지 파일 목록과 대조하는 방법은 [패키지 파일 변조 확인](../packages/package-verify.md) 에서 다룹니다.

### 증명하지 못하는 것

- 규칙이 실제로 실행됐는지는 규칙 파일만으로 알 수 없습니다. 조건에 맞는 장치 이벤트가 있었는지를 [USB 장치 연결 기록](../devices/usb.md)·[커널 로그](../system-info/kernel-log.md) 와 맞춰 봐야 합니다.
- `RUN` 으로 띄운 프로세스가 오래 살아 있었다고 볼 수 없습니다. 이벤트 처리가 끝나면 종료되기 때문입니다[1]. 오래 도는 프로그램이 있었다면 `SYSTEMD_WANTS` 로 끌어온 서비스 유닛을 [systemd 서비스와 타이머](systemd-units.md) 에서 찾습니다.
- 누가 규칙 파일을 만들었는지는 파일 속성만으로 가릴 수 없습니다. 셸 명령 기록·감사 로그와 시각을 맞춰 봐야 합니다.
- 디스크 이미지에서 `/run/udev/rules.d` 의 규칙이 없다고 해서 그런 규칙이 없었다고 말할 수 없습니다.

## 시각 해석

규칙 파일과 `RUN` 이 가리키는 프로그램 파일의 시각은 아이노드 시각입니다. mtime 은 파일 내용을 쓸 때 바뀌고, ctime 은 내용을 쓰거나 소유자·권한·링크 수 같은 아이노드 정보를 바꿀 때 바뀝니다[8]. 디렉터리의 mtime 은 그 안에 파일을 만들거나 지울 때 바뀌므로, `/etc/udev/rules.d` 자체의 mtime 은 마지막으로 파일이 생기거나 사라진 시각의 단서가 됩니다[8]. 값은 1970-01-01 00:00:00 UTC 부터 잰 시간이라 시간대가 따로 없습니다[8]. 시각 값을 읽는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

규칙을 바꾼 시각과 규칙이 처음 적용된 시각은 다릅니다. `udevadm control --reload` 로 규칙을 다시 읽어도 이미 붙어 있는 장치에는 바뀐 설정이 적용되지 않고 새 이벤트부터 적용됩니다[2]. 규칙이 돈 시각은 조건에 맞는 장치 이벤트의 시각, 곧 저널의 커널 항목이나 udev 관련 항목에서 찾습니다.

## 함정과 한계

- 수집 정의가 디렉터리 넷을 다 담지 않습니다. UAC 는 `/etc/udev/rules.d`, `/usr/lib/udev/rules.d`, `/run/udev/rules.d` 를 모으고[6], ForensicArtifacts 의 `LinuxUdevRules` 는 `/usr/lib/udev/rules.d/*` 와 `/etc/udev/rules.d/*` 만 정의합니다[7]. 둘 다 `/usr/local/lib/udev/rules.d` 는 없으므로 따로 모읍니다.
- 한 디렉터리만 보면 우선순위를 놓칩니다. `/usr/lib/udev/rules.d` 의 패키지 규칙 내용이 멀쩡해도, 같은 이름의 `/etc/` 파일이 그 규칙을 대신하고 있을 수 있습니다[1]. 네 디렉터리의 파일 이름을 모아 이름별로 비교합니다.
- 확장자가 `.rules` 가 아닌 파일은 읽지 않습니다[1]. 규칙 디렉터리에 다른 확장자의 파일이 있으면 설정으로는 쓰이지 않지만, 누가 왜 두었는지는 따로 봅니다.
- `RUN` 값이 상대 경로면 `/usr/lib/udev` 아래 프로그램이므로[1], 규칙 파일만이 아니라 그 디렉터리의 실행 파일도 패키지 목록과 대조합니다.
- 규칙이 부르는 프로그램이 셸 스크립트라면 실제 동작은 그 스크립트 안에 있습니다. 규칙 파일과 프로그램 파일을 한 묶음으로 수집합니다.
- systemd 가 싣는 규칙 파일에도 `PROGRAM` 과 `IMPORT{program}` 이 들어 있습니다[5]. 외부 프로그램을 부르는 키가 있다는 것만으로 의심하지 말고, 패키지 소속 여부와 프로그램 경로(예: 사용자 홈·`/tmp` 아래)를 함께 봅니다.

## 직접 분석해 보기

### 텍스트로 한 번: 규칙 줄 나눠 읽기

아래는 규칙 형식으로 만든 예시입니다. 파일 이름·장치 번호·프로그램 경로는 지어낸 것입니다.

```text
# /etc/udev/rules.d/99-example.rules (만든 예시)
ACTION=="add", SUBSYSTEM=="usb", ATTRS{idVendor}=="1234", RUN+="/usr/local/sbin/example-hook %k"
```

| 식 | 읽는 법 |
|---|---|
| `ACTION=="add"` | 장치가 더해질 때만 맞음 |
| `SUBSYSTEM=="usb"` | 이벤트를 낸 장치의 서브시스템이 `usb` 일 때 |
| `ATTRS{idVendor}=="1234"` | 부모 장치를 거슬러 올라가며 sysfs 속성 `idVendor` 가 `1234` 인 장치를 찾음 |
| `RUN+="/usr/local/sbin/example-hook %k"` | 규칙 처리가 끝난 뒤 프로그램을 실행 목록에 더하고, `%k` 는 커널 장치 이름으로 바뀜 |

이 줄은 "그 제조사 번호의 USB 장치가 붙을 때마다 `example-hook` 을 부르도록 설정돼 있었다" 는 것까지만 말합니다. 실행 여부는 그 제조사 번호의 장치가 연결된 기록과 `example-hook` 파일의 존재·내용으로 따로 확인합니다.

마운트한 이미지에서 네 디렉터리를 한꺼번에 보려면 파일 이름을 앞에 두고 이름순으로 정렬하면 됩니다. 이름이 같은 줄이 붙어 나오므로 덮어쓴 파일과 `/dev/null` 링크가 바로 보입니다. `/mnt/image` 는 이미지를 마운트한 위치입니다.

```sh
cd /mnt/image
find usr/lib/udev/rules.d usr/local/lib/udev/rules.d run/udev/rules.d etc/udev/rules.d \
  -maxdepth 1 \( -type f -o -type l \) \
  -printf '%f\t%h\t%y\t%l\t%TY-%Tm-%Td %TT\t%CY-%Cm-%Cd %CT\n' 2>/dev/null | sort
```

칸은 파일 이름, 디렉터리, 종류(`f` 파일·`l` 링크), 링크 대상, mtime, ctime 순입니다. `find` 가 찍는 시각은 분석 컴퓨터의 시간대로 바뀐 값이므로, 비교하기 전에 `TZ=UTC` 를 붙여 돌리면 됩니다.

### 공개 도구로 한 번

- UAC 의 `files/system/udev.yaml`, ForensicArtifacts 의 `LinuxUdevRules` 로 규칙 파일을 모읍니다[6][7]. 위 함정에 적은 대로 `/usr/local/lib/udev/rules.d` 는 따로 더합니다.
- systemd 254 이상이 깔린 분석 컴퓨터에서는 `udevadm verify --root=/mnt/image` 로 마운트한 이미지의 규칙 디렉터리 전체를 문법 검사할 수 있습니다[2][4]. `--root` 를 주면 그 아래의 `udev/rules.d` 디렉터리를 읽습니다[2]. 사용자·그룹 이름을 분석 컴퓨터 기준으로 풀지 않으려면 `--resolve-names=late` 를 함께 줍니다[2]. 문법 오류가 있는 규칙은 udevd 가 제대로 적용하지 못했을 가능성이 있다는 단서가 됩니다.
- 라이브 시스템에서는 `udevadm info --export-db` 로 장치 데이터베이스를 받고, 어느 장치에 어떤 속성이 붙었는지를 규칙과 맞춰 봅니다. 데이터베이스 형식은 [USB 장치 연결 기록](../devices/usb.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [USB 장치 연결 기록](../devices/usb.md) | 규칙 조건에 맞는 장치가 언제 붙었나 |
| [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) | 장치 이벤트 시각, systemd-udevd 항목에 규칙 파일이나 프로그램 이름이 나오는지 |
| [systemd 서비스와 타이머](systemd-units.md) | `SYSTEMD_WANTS` 로 끌어온 서비스 유닛 |
| [패키지 파일 변조 확인](../packages/package-verify.md), [dpkg·apt 기록](../packages/dpkg-apt.md), [rpm·dnf·yum 기록](../packages/rpm-dnf.md) | 규칙 파일과 `/usr/lib/udev` 아래 프로그램이 패키지 소속인지 |
| [셸 명령 기록](../execution/shell-history/index.md) | 규칙 파일을 만들거나 `udevadm control --reload` 를 실행한 명령 |
| [알려진 파일 대조와 YARA](../../03-techniques/analysis/hash-yara.md) | `RUN` 이 가리키는 프로그램의 해시와 내용 |

지속성 흔적을 한꺼번에 훑는 순서는 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md) 에서 다룹니다.

## 실습

공개된 Linux 디스크 이미지(NIST CFReDS 등)를 마운트해 풀어 봅니다.

1. 네 규칙 디렉터리에 있는 `.rules` 파일은 모두 몇 개이고, 이름이 겹치는 파일은 어느 디렉터리의 것이 쓰였는가?
2. `/etc/udev/rules.d` 에 있는 파일 가운데 패키지 파일 목록에 없는 것은 무엇인가?
3. `RUN` 이나 `PROGRAM` 이 절대 경로로 가리키는 프로그램 가운데 `/usr/lib/udev` 밖에 있는 것은 무엇이고, 그 파일은 지금 있는가?
4. `/etc/udev/rules.d` 디렉터리의 mtime 과 그 안 파일들의 ctime 은 설치 날짜와 얼마나 떨어져 있는가?
5. 규칙 조건에 맞는 장치가 저널에 연결된 기록이 있는가?

## 참고 문헌

1. systemd, man/udev.xml (udev(7)). https://github.com/systemd/systemd/blob/main/man/udev.xml , https://github.com/systemd/systemd/blob/v255/man/udev.xml , https://github.com/systemd/systemd/blob/v252/man/udev.xml
2. systemd, man/udevadm.xml (udevadm(8)). https://github.com/systemd/systemd/blob/main/man/udevadm.xml
3. systemd, man/systemd-udevd.service.xml (systemd-udevd.service(8)). https://github.com/systemd/systemd/blob/main/man/systemd-udevd.service.xml
4. systemd, NEWS ("CHANGES WITH 254", "CHANGES WITH 258"). https://github.com/systemd/systemd/blob/main/NEWS
5. systemd, rules.d/60-persistent-storage.rules.in. https://github.com/systemd/systemd/blob/main/rules.d/60-persistent-storage.rules.in
6. UAC, artifacts/files/system/udev.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/system/udev.yaml
7. ForensicArtifacts, artifacts/data/linux.yaml (LinuxUdevRules). https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
8. man-pages, man7/inode.7. https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
9. Ubuntu systemd 패키지, debian/rules·changelog (noble-updates, 255.4-1ubuntu8). https://git.launchpad.net/ubuntu/+source/systemd/tree/debian?h=ubuntu/noble-updates
10. CentOS Stream systemd 패키지, systemd.spec (c9s, 252). https://gitlab.com/redhat/centos-stream/rpms/systemd/-/blob/c9s/systemd.spec
