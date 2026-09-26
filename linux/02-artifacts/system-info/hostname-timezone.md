---
title: "호스트 이름·시간대·로캘"
parent: "아티팩트 · 시스템 정보"
nav_order: 290
---

# 호스트 이름·시간대·로캘 (Hostname·Timezone)

`/etc/hostname`, `/etc/localtime`, `/etc/locale.conf` 같은 설정 파일에서 이 기계의 이름, 시각을 보여 줄 시간대, 언어 설정을 읽고, 그 값이 언제 바뀌었는지를 저널에서 찾습니다.

## 무엇을 기록하나 · 왜 생기나

호스트 이름 설정 파일은 부팅할 때 systemd 가 sethostname(2) 로 커널에 넣을 이름을 담습니다[1]. 시간대 설정은 프로그램이 시각을 사람에게 보여 줄 때 쓰는 시스템 전체 시간대이고[6], 로캘 설정은 모든 서비스와 사용자가 물려받는 언어·지역 설정입니다[9]. 셋 다 관리자가 `hostnamectl`, `timedatectl`, `localectl` 로 바꾸거나 파일을 직접 고칠 때 바뀝니다[1][6][9]. 부팅하지 않은 이미지에 값을 미리 넣을 때는 `systemd-firstboot` 를 쓰므로[1][6][9], 클라우드·가상 머신 이미지에서는 이미지를 만든 도구가 넣은 값일 수 있습니다.

조사에서 이 값들이 필요한 이유는 둘입니다. 하나는 식별로, 로그와 다른 기계의 기록에 찍힌 이름이 이 기기의 것인지 판별합니다. 다른 하나는 시각 해석으로, 전통 syslog 줄과 dpkg.log 처럼 현지 시각으로 적힌 기록을 UTC 로 옮기려면 그 기계의 시간대를 알아야 합니다([syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)).

## 위치와 버전별 차이

### 호스트 이름

systemd 는 호스트 이름을 세 가지로 나눕니다[2]. 정적 이름 (static hostname) 은 `/etc/hostname` 에 적힌 값이고, 임시 이름 (transient hostname) 은 DHCP 임대 정보처럼 실행 중에 네트워크 설정에서 받은 값이며[1], 보기용 이름 (pretty hostname) 은 `Lennart's Laptop` 처럼 특수 문자를 쓸 수 있는 이름입니다. 정적 이름이 유효하면 임시 이름은 쓰지 않습니다[2].

실제로 커널에 들어가는 이름은 다음 순서로 정합니다[1]. 커널 명령줄 `systemd.hostname=` 이 있으면 그 값을 쓰고, 없으면 `/etc/hostname` 을 쓰고, 그것도 없으면 NetworkManager 나 systemd-networkd 가 받아 온 임시 이름을 쓰며, 마지막에는 빌드할 때 정한 기본 이름을 씁니다. os-release 의 `DEFAULT_HOSTNAME=` 은 `/etc/hostname` 도 다른 설정도 없을 때 쓰는 이름입니다[4]([배포판과 버전](./os-release.md)). systemd 말고 다른 프로그램도 호스트 이름을 바꿀 수 있습니다[1].

| 경로 | 담는 것 | 비고 |
|---|---|---|
| `/etc/hostname` | 정적 호스트 이름 한 줄 | 이 형식은 Debian 에서 왔습니다[1] |
| `/etc/machine-info` | `PRETTY_HOSTNAME=`, `ICON_NAME=`, `CHASSIS=`, `DEPLOYMENT=`, `LOCATION=`, `TAGS=` 등 | 관리자가 정하는 값이라 없어도 정상입니다[3] |
| `/etc/HOSTNAME` | 호스트 이름 | dissect 가 `/etc/hostname` 다음으로 봅니다[19] |
| `/etc/sysconfig/network` | `HOSTNAME=` 줄 | 옛 Red Hat 계열 방식으로, dissect 가 읽습니다[19] |
| `/etc/hosts` | `localhost` 가 없는 127.0.0.1·::1 줄의 이름 | dissect 가 마지막 대안으로 씁니다[19]([이름 해석](../network/name-resolution.md)) |
| `/proc/sys/kernel/hostname`, `/proc/sys/kernel/domainname` | 실행 중 커널의 호스트 이름, NIS/YP 도메인 이름 | 라이브에서만 의미가 있고, domainname 은 DNS 도메인과 다릅니다[17][26] |

### 시간대

`/etc/localtime` 은 `/usr/share/zoneinfo/` 아래 tzfile 을 가리키는 절대 또는 상대 심볼릭 링크 (symbolic link) 입니다[6]. systemd 는 링크 대상 경로에서 `Europe/Berlin`, `Etc/UTC` 같은 시간대 이름을 뽑기 때문에 이 파일이 일반 파일이나 하드 링크여서는 안 된다고 정해 두었습니다[6]. 파일이 없으면 UTC 를 씁니다[6].

| 경로 | 담는 것 | 비고 |
|---|---|---|
| `/etc/localtime` | zoneinfo 파일로 가는 링크 | Ubuntu·RHEL 공통, systemd 표준[6] |
| `/etc/timezone` | IANA 시간대 이름 한 줄(예 `Europe/Zurich`) | Debian 계열이 쓰는 파일입니다[21]. 분석 대상에 있는지 확인합니다 |
| `/etc/adjtime` | 하드웨어 시계 (RTC) 가 UTC 인지 현지 시각인지 | 파일이 없으면 UTC 입니다[8] |

### 로캘과 키보드

`/etc/locale.conf` 가 systemd 표준 경로이고, 운영체제에 따라 다른 파일을 대안으로 볼 수 있습니다[9]. dissect 는 로캘을 `/etc/default/locale`, `/etc/locale.conf`, `/etc/sysconfig/i18n` 세 곳에서, 키보드를 `/etc/default/keyboard`, `/etc/vconsole.conf`, `/etc/X11/xorg.conf.d/*-keyboard.conf` 에서 찾습니다[20]. 어느 파일이 실제로 쓰이는지는 분석 대상에 파일이 있는지로 확인합니다.

### machine-id

호스트를 이름보다 확실하게 가리키는 값은 `/etc/machine-id` 입니다. 설치할 때나 첫 부팅 때 무작위로 만들고, 그 뒤 부팅에서는 그대로이며, 하드웨어를 바꾸거나 네트워크 설정을 바꿔도 달라지지 않습니다[5]. 커널 명령줄 `systemd.machine_id=` 가 있으면 그 값이 우선합니다[5]. 이 값은 기밀로 다뤄야 하므로[5], 보고서에는 값 전체를 싣지 않습니다.

## 구조

`/etc/hostname` 은 줄바꿈으로 끝나는 이름 한 줄입니다[1]. `#` 으로 시작하는 줄은 주석이고, 이름은 7비트 ASCII 소문자·숫자·하이픈으로 최대 64자이며, 점 없는 라벨 하나를 권합니다[1]. upstream systemd 에서는 이름에 `?` 가 있으면 machine-id 를 해시해 만든 16진 문자로 바꾸고, `$` 는 단어 목록 파일에서 고른 단어로 바꿉니다[1]. 이 치환은 부팅할 때마다 다시 계산합니다[1]. 분석 대상의 systemd 판이 이 기능을 지원하는지는 그 판의 `hostname(5)` 로 확인합니다.

`/etc/machine-info` 와 `/etc/locale.conf` 는 os-release 와 같은 `KEY=value` 대입 줄 형식이고, 주석과 빈 줄은 무시합니다[3][9]. `/etc/locale.conf` 에는 `LANG`, `LANGUAGE` 와 `LC_CTYPE`·`LC_TIME` 을 비롯한 `LC_*` 열두 개를 쓸 수 있고, `LC_ALL` 은 쓸 수 없습니다[9]. 커널 명령줄 `locale.LANG=` 같은 값이 부팅 때 이 파일을 덮습니다[9].

`/etc/machine-id` 는 소문자 16진수 32자와 줄바꿈이고, 풀면 128비트 값입니다[5].

`/etc/adjtime` 은 ASCII 세 줄입니다[8].

| 줄 | 값 |
|---|---|
| 1 | 하루당 드리프트(초), 마지막 보정 시각(1969년 UTC 기준 초), 0 |
| 2 | 마지막 교정 시각(1969년 UTC 기준 초, 교정한 적 없으면 0) |
| 3 | `UTC` 또는 `LOCAL` |

`timedatectl set-local-rtc` 가 바꾸는 것이 이 셋째 줄입니다[7]. systemd-timedated 는 결과가 `0.0 0 0` / `0` / `UTC` 세 줄과 같으면 파일을 지웁니다[14]. 따라서 `/etc/adjtime` 이 없다는 사실만으로는 이상한 점이 아닙니다.

## 증거로서 의미

**증명하는 것.** 수집 시점에 설정 파일에 적혀 있던 정적 호스트 이름, 시스템 시간대, 로캘 값입니다. 시간대는 현지 시각으로 적힌 로그를 UTC 로 옮길 때 기준이 됩니다. machine-id 는 저널 폴더 이름과 저널 항목의 `_MACHINE_ID=` 필드[10]와 대조해 그 저널이 이 기계에서 쓰였는지 판별하는 근거가 됩니다([systemd 저널](../../01-foundations/logging/systemd-journal/index.md)).

**증명하지 못하는 것.** 과거 어느 시점의 값은 알 수 없습니다. 설정은 언제든 바뀔 수 있고 파일 안에는 시각이 없습니다. DHCP 로 받은 임시 호스트 이름은 파일에 남지 않습니다[1][2]. 프로그램마다 `$TZ` 환경 변수로 시간대를 따로 덮을 수 있으므로[6], 특정 프로그램의 로그가 시스템 시간대로 적혔다고 단정할 수 없습니다. 보고서에는 "수집 시점 `/etc/localtime` 은 Asia/Seoul 을 가리킨다" 처럼 파일에 적힌 만큼만 씁니다.

## 시각 해석

설정 파일 안에는 시각 값이 없습니다. 값이 바뀐 시점은 저널과 파일 시스템 시각으로 추정합니다.

저널에는 값이 바뀐 흔적이 남을 수 있습니다. `timedatectl set-timezone` 으로 바꾸면 systemd-timedated 가 `MESSAGE_ID=45f82f4aef7a4bbf942ce861d1f20990` 항목을 남기고[12][14], upstream 코드 기준으로 이 항목에는 `TIMEZONE=`, `TIMEZONE_SHORTNAME=`, `DAYLIGHT=` 필드와 `Changed time zone to '...' (...).` 모양의 메시지가 들어 있습니다[14]. 같은 서비스가 시계를 바꾸면 `MESSAGE_ID=c7a787079b354eaaa9e77b371893cd27` 항목에 `REALTIME=` 을 남깁니다[12][14]. 두 MESSAGE_ID 는 RHEL 9 의 systemd 카탈로그에도 있습니다[13]. 반면 관리자가 링크를 직접 바꾸면 PID 1 이 바뀐 것을 알아채기는 하지만 디버그 등급 메시지만 남기고 MESSAGE_ID 는 붙이지 않습니다[25]. 이 경우에는 위 항목이 없을 가능성이 큽니다.

호스트 이름은 MESSAGE_ID 없이 문구로만 남습니다. upstream 코드 기준으로 부팅 때 PID 1 이 이름을 넣으면 `Hostname set to <web01>.` 처럼 이름을 꺾쇠로 감싼 줄을[16], systemd-hostnamed 가 이름을 바꾸면 `Hostname set to <web01> (static)` 처럼 출처(`static`, `transient`, `default`)를 붙인 줄을 남깁니다[15]. `web01` 은 만든 예시입니다. 보기용 이름이나 CHASSIS 같은 machine-info 값을 바꾸면 `Changed pretty hostname to '...'` 모양의 줄이 남습니다[15]. 판마다 문구가 조금씩 다를 수 있으므로 분석 대상 저널에서 `Hostname set` 과 `Changed` 로 먼저 찾아봅니다.

저널 항목마다 붙는 `_HOSTNAME=` 은 그 항목을 기록한 당시의 이름입니다[10]. `journalctl -F _HOSTNAME` 은 이 필드에 나온 모든 값을 보여 주므로[11], 값이 둘 이상이면 이름이 바뀐 적이 있다는 뜻이고, 각 값이 처음 나온 항목의 시각으로 바뀐 시점을 좁힙니다. 저널 시각은 UTC 기준 마이크로초라서 시간대 설정과 상관없습니다([Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)).

파일 시스템 시각도 단서입니다. systemd-timedated 는 `/etc/localtime` 링크를 원자적으로 새로 만들어 교체하고, 기본으로 상대 링크를 씁니다[14]. 그래서 링크 자체의 시각(lstat 로 본 시각)이 마지막으로 바꾼 무렵일 가능성이 있습니다. 링크가 가리키는 zoneinfo 파일의 시각은 tzdata 패키지를 갱신한 시각이라 시간대를 바꾼 시점과 관계가 없습니다. 도구가 링크를 따라가 대상 파일의 시각을 보여 주는지 확인합니다.

`/etc/adjtime` 셋째 줄이 `LOCAL` 이면 하드웨어 시계가 현지 시각으로 돌아갑니다[8]. 하드웨어 시계를 현지 시각으로 두는 방식은 제대로 지원되지 않고, 시간대를 바꾸거나 일광 절약 시간으로 넘어갈 때 여러 문제를 일으킵니다[7]. 이런 기계는 부팅 직후 시계를 맞추기 전에 남긴 기록이 시간대만큼 어긋날 가능성이 있습니다([부팅과 종료 기록](./boot-shutdown.md)).

## 함정과 한계

도구마다 시간대를 읽는 순서가 다릅니다. systemd 는 `/etc/localtime` 링크만 인정합니다[6]. dissect 는 `/etc/timezone` 을 먼저 보고, 없으면 `/etc/localtime` 이 심볼릭 링크일 때 대상 경로를, 하드 링크일 때 `/usr/share/zoneinfo` 안의 같은 파일을, 일반 파일일 때 크기와 SHA-1 이 같은 zoneinfo 파일을 찾습니다[20]. 이때 RHEL 의 `posix` 로 시작하는 파일은 건너뜁니다[20]. 끝내 못 찾으면 경고를 남기고 UTC 로 가정합니다[24]. plaso 는 `/etc/localtime` 이 링크면 `zoneinfo/` 뒤 경로를 이름으로 쓰고, 일반 파일이면 tzfile 을 읽어 2017년 1월 1일 기준 약어(예 `CET`)를 얻은 뒤, `/etc/timezone` 이 있으면 그 IANA 이름으로 덮어씁니다[21]. 따라서 `/etc/timezone` 과 `/etc/localtime` 이 서로 다른 시간대를 말하면 systemd 와 도구의 결과가 갈리고, 이때는 시스템이 실제로 쓴 값을 `/etc/localtime` 기준으로 판단합니다. 이 약어는 IANA 이름과 달리 어느 시간대인지 모호합니다[21].

dissect 는 시간대 이름을 경로의 마지막 두 부분으로 만들고 `zoneinfo`·`Etc` 는 뺍니다[20]. `Etc/UTC` 는 `UTC` 가 되고, 세 단계 경로인 `America/Argentina/Buenos_Aires` 는 `Argentina/Buenos_Aires` 가 됩니다. 도구 출력이 이상하면 링크 대상을 직접 읽습니다.

호스트 이름도 도구마다 다르게 읽습니다. plaso 는 `/etc/hostname` 의 첫 줄만 씁니다[21]. dissect 는 `/etc/hostname`, `/etc/HOSTNAME`, `/proc/sys/kernel/hostname`, `/etc/sysconfig/network`, `/etc/hosts` 순으로 처음 있는 파일을 읽는데, `/etc/hostname` 은 주석을 거르지 않고 파일 전체를 읽으며, 점이 있으면 첫 점 앞을 호스트 이름, 뒤를 도메인으로 나눕니다[19]. systemd 는 `#` 줄을 무시하므로[1], 주석이 든 `/etc/hostname` 은 도구 출력과 실제 이름이 다를 수 있습니다.

`/etc/hostname` 에 `?` 나 `$` 가 있으면 실제 이름은 machine-id 로 계산한 값이라[1], 파일 내용과 로그의 호스트 필드가 다르게 보입니다. 이때는 저널 `_HOSTNAME=` 값을 실제 이름으로 봅니다.

컨테이너나 chroot 안의 설정 파일을 호스트 것으로 읽지 않도록 주의합니다. 컨테이너 이미지에는 제 나름의 `/etc/hostname` 과 `/etc/localtime` 이 들어 있습니다([Docker](../containers/docker/index.md)).

설정 파일은 텍스트라 누구나 고칠 수 있습니다. 파일 값만 바꾸고 재부팅하지 않았다면 커널의 실행 중 이름과 파일이 다를 수 있으므로, 라이브 수집에서는 `hostname`, `hostnamectl`, `uname -n` 결과[23]와 파일을 나란히 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

ext4 에서 60바이트보다 짧은 심볼릭 링크는 대상 문자열을 아이노드의 `i_block` 필드(오프셋 0x28, 60바이트)에 그대로 담습니다[18]. 아이노드 오프셋 0x0 의 `i_mode` 에서 파일 종류 값이 0xA000 이면 심볼릭 링크이고, 오프셋 0x4 의 `i_size_lo` 가 대상 문자열 길이입니다[18]. 아래는 `/etc/localtime` 이 `../usr/share/zoneinfo/Asia/Seoul` 을 가리킬 때의 아이노드 앞부분을 명세로 만든 예시입니다.

```
0000: ff a1 00 00 20 00 00 00  .. .. .. ..  .. .. .. ..   i_mode=0xA1FF(링크, 0777), i_size_lo=0x20(32)
...
0028: 2e 2e 2f 75 73 72 2f 73  68 61 72 65 2f 7a 6f 6e   ../usr/share/zon
0038: 65 69 6e 66 6f 2f 41 73  69 61 2f 53 65 6f 75 6c   einfo/Asia/Seoul
```

오프셋 0x10 의 `i_mtime` 과 0x0C 의 `i_ctime` 은 링크 아이노드 자신의 시각입니다[18]. 아이노드를 찾는 방법과 시각 필드 전체는 [ext4](../../01-foundations/filesystem/ext4/index.md) 페이지를 봅니다.

### 공개 도구로 한 번

마운트한 이미지에서는 링크를 따라가지 않고 봅니다.

```
ls -l  /mnt/img/etc/localtime        # 링크 대상
stat   /mnt/img/etc/localtime        # 링크 자체의 시각(lstat)
cat    /mnt/img/etc/hostname /mnt/img/etc/machine-info /mnt/img/etc/adjtime
journalctl -D /mnt/img/var/log/journal -F _HOSTNAME
journalctl -D /mnt/img/var/log/journal MESSAGE_ID=45f82f4aef7a4bbf942ce861d1f20990
```

절대 경로 링크를 분석 PC 에서 따라가면 분석 PC 의 `/usr/share/zoneinfo` 를 읽게 되므로, 대상 경로 문자열만 봅니다. dissect 는 `hostname`, `domain`, `timezone`, `language` 속성과 `keyboard` 레코드로 같은 값을 뽑고[19][20], plaso 는 처리 시작 전 전처리 단계에서 호스트 이름과 시간대를 정합니다[21]. ForensicArtifacts 정의로는 `LinuxHostnameFile`, `LinuxLocalTime`, `LinuxTimezoneFile`, `UnixHostsFile` 을 모읍니다[22]. 라이브에서는 UAC 가 `hostname`, `hostname -f`, `hostnamectl`, `uname -n`, `timedatectl status` 결과를 받습니다[23]. `timedatectl status` 출력에는 `Local time`, `Universal time`, `RTC time`, `Time zone`, `System clock synchronized`, `NTP service`, `RTC in local TZ` 필드가 있습니다[7].

## 교차 검증

| 함께 볼 것 | 맞춰 볼 내용 |
|---|---|
| [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) | `_HOSTNAME=`, `_MACHINE_ID=` 값과 저널 폴더 이름, 시간대 변경 항목 |
| [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md) | 줄마다 적힌 호스트 필드, 시간대를 적용한 시각 |
| [로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md) | 시계를 바꾼 전후 레코드 |
| [네트워크 설정](../network/network-config.md) | DHCP 로 받은 임시 호스트 이름의 출처 |
| [설치 날짜 가늠하기](./install-date.md) | machine-id 생성 시각과 설치 흔적 |
| [시각을 조작했나](../../04-scenarios/insider/time-manipulation.md) | 시계 변경 항목과 시간대 변경 항목 구분 |

## 실습

공개 시험 데이터(NIST CFReDS 의 Linux 디스크 이미지 등)로 다음을 풀어 봅니다.

1. `/etc/localtime` 은 심볼릭 링크인가, 복사한 일반 파일인가? 링크라면 대상은 무엇이고 절대 경로인가 상대 경로인가?
2. `/etc/timezone` 이 있다면 `/etc/localtime` 과 같은 시간대를 가리키는가? dissect 나 plaso 가 내놓은 시간대와도 같은가?
3. `/var/log/syslog` 나 `/var/log/messages` 의 첫 줄 시각을 이 시간대로 UTC 로 옮기면, 같은 사건의 저널 항목 시각과 맞는가?
4. 저널 `_HOSTNAME=` 값은 몇 가지인가? 둘 이상이면 각 값이 처음 나온 시각은 언제인가?
5. `/etc/adjtime` 셋째 줄은 무엇인가? `LOCAL` 이라면 부팅 직후 항목의 시각을 어떻게 해석해야 하는가?

## 참고 문헌

1. systemd, `man/hostname.xml` — https://github.com/systemd/systemd/blob/main/man/hostname.xml
2. systemd, `man/hostnamectl.xml` — https://github.com/systemd/systemd/blob/main/man/hostnamectl.xml
3. systemd, `man/machine-info.xml` — https://github.com/systemd/systemd/blob/main/man/machine-info.xml
4. systemd, `man/os-release.xml` — https://github.com/systemd/systemd/blob/main/man/os-release.xml
5. systemd, `man/machine-id.xml` — https://github.com/systemd/systemd/blob/main/man/machine-id.xml
6. systemd, `man/localtime.xml` — https://github.com/systemd/systemd/blob/main/man/localtime.xml
7. systemd, `man/timedatectl.xml` — https://github.com/systemd/systemd/blob/main/man/timedatectl.xml
8. util-linux, `sys-utils/adjtime_config.5.adoc` — https://github.com/util-linux/util-linux/blob/master/sys-utils/adjtime_config.5.adoc
9. systemd, `man/locale.conf.xml` — https://github.com/systemd/systemd/blob/main/man/locale.conf.xml
10. systemd, `man/systemd.journal-fields.xml` — https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
11. systemd, `man/journalctl.xml` — https://github.com/systemd/systemd/blob/main/man/journalctl.xml
12. systemd, `catalog/systemd.catalog.in` — https://github.com/systemd/systemd/blob/main/catalog/systemd.catalog.in
13. systemd-rhel9 (RHEL 9 source-git), `catalog/systemd.catalog.in` — https://github.com/redhat-plumbers/systemd-rhel9/blob/main/catalog/systemd.catalog.in
14. systemd, `src/timedate/timedated.c` — https://github.com/systemd/systemd/blob/main/src/timedate/timedated.c
15. systemd, `src/hostname/hostnamed.c` — https://github.com/systemd/systemd/blob/main/src/hostname/hostnamed.c
16. systemd, `src/shared/hostname-setup.c` — https://github.com/systemd/systemd/blob/main/src/shared/hostname-setup.c
17. Linux kernel, `Documentation/admin-guide/sysctl/kernel.rst` — https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/sysctl/kernel.rst
18. Linux kernel, `Documentation/filesystems/ext4/inodes.rst`, `ifork.rst` — https://github.com/torvalds/linux/tree/master/Documentation/filesystems/ext4
19. dissect.target, `plugins/os/unix/_os.py` — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/_os.py
20. dissect.target, `plugins/os/unix/locale.py` — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/locale.py
21. plaso, `plaso/preprocessors/linux.py` — https://github.com/log2timeline/plaso/blob/main/plaso/preprocessors/linux.py
22. ForensicArtifacts, `artifacts/data/linux.yaml`, `unix_common.yaml` — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml , https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/unix_common.yaml
23. UAC, `artifacts/live_response/network/hostname.yaml`, `artifacts/live_response/system/timedatectl.yaml` — https://github.com/tclahr/uac/tree/main/artifacts/live_response
24. dissect.target, `plugins/os/unix/datetime.py` — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/datetime.py
25. systemd, `src/core/manager.c` — https://github.com/systemd/systemd/blob/main/src/core/manager.c
26. man-pages, `man5/proc.5` — https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
