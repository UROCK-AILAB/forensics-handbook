---
title: "dpkg·apt 기록"
parent: "아티팩트 · 패키지와 소프트웨어"
nav_order: 590
---

# dpkg·apt 기록 (Debian·Ubuntu)

Debian·Ubuntu 계열에서 패키지를 설치·갱신·제거하면 dpkg 가 `/var/log/dpkg.log` 에 한 줄씩, apt 가 `/var/log/apt/history.log` 에 실행 한 번마다 한 묶음씩 기록을 남기고, 지금 설치된 목록은 `/var/lib/dpkg/status` 에 남습니다.

## 무엇을 기록하나 · 왜 생기나

Debian 계열의 패키지 관리는 두 층으로 나뉩니다. 아래층의 dpkg 는 `.deb` 파일을 풀고 설정하고 지우는 일을 하고, 위층의 apt(`apt`, `apt-get`)는 저장소에서 패키지를 받아 의존성을 맞춘 뒤 dpkg 를 부릅니다. 그래서 apt 로 설치하면 두 층의 기록이 함께 남고, `dpkg -i 파일.deb` 로 직접 설치하면 dpkg 의 기록만 남습니다. apt 의 history.log 는 apt 가 dpkg 를 부르기 직전에 열고 끝난 뒤 닫는 기록이라, dpkg 를 직접 부른 작업은 여기에 없습니다[7].

dpkg 는 기본 설정 파일 `/etc/dpkg/dpkg.cfg` 의 `log /var/log/dpkg.log` 줄 때문에 상태가 바뀔 때와 동작할 때마다 로그를 씁니다[3]. apt 는 명령줄, 요청한 사용자, 설치·갱신·제거한 패키지 목록을 history.log 에 적고, dpkg 가 터미널에 낸 출력 원문은 term.log 에 따로 적습니다[7][8].

침해 조사에서 이 기록은 공격자가 도구(스캐너, 컴파일러, 원격 접속 도구)를 설치했는지, 보안 패키지를 지웠는지, 패키지 관리자 설정에 명령을 심었는지를 확인하는 출발점이 됩니다.

## 위치와 버전별 차이

이 페이지는 Ubuntu 24.04 LTS 등 Debian 계열에 해당합니다. RHEL 9 에는 dpkg·apt 가 없고, 같은 역할의 기록은 [rpm·dnf·yum 기록](rpm-dnf.md)에서 다룹니다. snap 과 flatpak 은 [snap·flatpak](snap-flatpak.md)을 봅니다.

| 경로 | 내용 |
|---|---|
| `/var/log/dpkg.log`, `.1`, `.2.gz` … | dpkg 가 상태 변화와 동작을 한 줄씩 기록합니다[1][3] |
| `/var/log/apt/history.log`, `.N.gz` | apt 실행 한 번마다 `Start-Date`~`End-Date` 한 묶음[7][8] |
| `/var/log/apt/term.log`, `.N.gz` | dpkg 가 터미널에 낸 출력 원문[7][8] |
| `/var/log/apt/eipp.log.xz` | 설치 계획(planner) 기록. 내용 구조는 실제 파일로 확인합니다[8] |
| `/var/lib/dpkg/status` | 패키지마다 한 블록, 지금 상태와 버전[1][18] |
| `/var/lib/dpkg/available` | 사용 가능한 패키지 목록[1] |
| `/var/lib/dpkg/info/패키지[:아키텍처].list`, `.md5sums` | 패키지가 설치한 파일 목록과 MD5[6][19] |
| `/var/backups/dpkg.status.0` … | dpkg 데이터베이스를 매일 복사해 둔 사본[4] |
| `/var/lib/apt/extended_states` | 자동 설치(의존성) 표시[8][12] |
| `/var/lib/apt/lists/` | 저장소 색인과 `Release`·`InRelease`[8][18] |
| `/var/cache/apt/archives/` | 받아 둔 `.deb` 파일[8] |
| `/etc/apt/sources.list`, `sources.list.d/*.list`, `*.sources` | 저장소 설정(한 줄 형식과 deb822 형식)[16][18] |
| `/etc/apt/apt.conf.d/` | apt 설정 조각[8][17] |
| `/etc/apt/trusted.gpg`, `trusted.gpg.d/*.gpg`, `/usr/share/keyrings/*.gpg` | 저장소 서명 키[16] |
| `/var/log/aptitude*` | aptitude 를 쓴 경우의 기록[16] |
| `/var/log/unattended-upgrades/unattended-upgrades.log`, `unattended-upgrades-dpkg.log` | 자동 업데이트 기록[15] |
| `/var/lib/apt/periodic/unattended-upgrades-stamp` | 자동 업데이트가 돈 때를 mtime 으로 남기는 빈 파일[15] |

판 차이가 알려진 곳은 셋입니다. history.log 의 `Comment:` 줄은 2024년 11월 apt 개발 저장소에 들어간 기능이라, 그보다 앞선 apt 에는 없습니다[14]. `.md5sums` 가 없는 패키지를 풀 때 dpkg 가 목록을 만들어 주는 동작은 dpkg 1.16.3 부터이고[6], `dpkg-query` 의 `db-fsys:Last-Modified` 필드는 dpkg 1.19.3 부터입니다[5].

## 구조

### dpkg.log

한 줄은 `YYYY-MM-DD HH:MM:SS` 시각 뒤에 네 가지 모양 중 하나가 옵니다[1][2].

| 줄 모양 | 뜻 |
|---|---|
| `시각 startup 유형 명령` | dpkg 를 한 번 부를 때. 유형 `archives`(명령 `unpack`·`install`) 또는 `packages`(명령 `configure`·`triggers-only`·`remove`·`purge`) |
| `시각 status 상태 패키지 설치된버전` | 상태가 바뀔 때 |
| `시각 동작 패키지 설치된버전 새버전` | 동작 `install`·`upgrade`·`configure`·`trigproc`·`disappear`·`remove`·`purge` |
| `시각 conffile 파일이름 결정` | 설정 파일 처리. 결정은 `install` 또는 `keep` |

버전이 없는 자리에는 `<none>` 이 들어갑니다[19]. 아래는 새 패키지 하나를 설치할 때 생기는 줄의 모양을 만든 예시입니다.

```
2024-07-24 16:48:58 startup archives unpack
2024-07-24 16:48:58 install htop:amd64 <none> 3.3.0-4build1
2024-07-24 16:48:58 status half-installed htop:amd64 3.3.0-4build1
2024-07-24 16:48:58 status unpacked htop:amd64 3.3.0-4build1
2024-07-24 16:48:59 startup packages configure
2024-07-24 16:48:59 configure htop:amd64 3.3.0-4build1 <none>
2024-07-24 16:48:59 status half-configured htop:amd64 3.3.0-4build1
2024-07-24 16:48:59 status installed htop:amd64 3.3.0-4build1
```

dpkg 는 로그 파일을 덧붙이기(`O_APPEND`) 모드, 권한 0644 로 엽니다[2]. logrotate 설정은 매월 돌리고 12개를 남기며, 바로 앞 회차(`.1`)는 압축하지 않고 그 전 것부터 압축하며, 비어 있는 달에는 돌리지 않습니다(`notifempty`)[3]. 순환 일반은 [로그 순환](../../01-foundations/logging/logrotate.md)을 봅니다.

### status 파일과 상태 값

`/var/lib/dpkg/status` 는 패키지마다 `Package:`, `Status:`, `Version:` 같은 필드로 이루어진 블록이 빈 줄로 나뉘어 이어지는 텍스트 파일입니다[1][18]. `Status:` 줄은 `선택상태 플래그 상태` 순서의 세 단어입니다[18].

| 자리 | 값 |
|---|---|
| 선택 상태 (selection) | `install`, `hold`, `deinstall`, `purge`, `unknown`[1][18] |
| 플래그 | `ok`, `reinstreq`[18] |
| 상태 (state) | `not-installed`, `config-files`, `half-installed`, `unpacked`, `half-configured`, `triggers-awaited`, `triggers-pending`, `installed`[1] |

`remove` 는 설정 파일(conffiles)을 남기고 나머지를 지우므로 상태가 `config-files` 로 남고, `purge` 는 설정 파일까지 지웁니다[1]. 지운 뒤 purge 한 패키지는 `not-installed` 로 남을 수 있고, 한 번도 설치하지 않은 패키지는 항목이 아예 없습니다[18].

dpkg 는 매일 한 번 `status`, `arch`, `diversions`, `statoverride` 를 `/var/backups` 에 `dpkg.status.0` 같은 이름으로 복사합니다[4]. 네 파일 중 하나라도 바뀌었을 때만 복사하고, `savelog` 로 7회차까지 돌려 가며 남기며, 복사는 `cp -p` 라서 원본의 수정 시각을 그대로 옮깁니다[4]. 실행 주체는 systemd 가 있으면 `dpkg-db-backup.timer`(매일)이고, systemd 가 없을 때만 매일 도는 cron 작업이 같은 스크립트를 부릅니다[4].

### info 디렉터리

`/var/lib/dpkg/info/` 에는 패키지마다 설치한 파일 목록(`.list`)과 MD5 목록(`.md5sums`)이 있습니다[19]. `.md5sums` 는 32자리 16진 MD5, 공백 두 칸, 경로를 한 줄에 하나씩 적고, 예시에서는 경로 앞의 `/` 가 없습니다(`53c0d4af…  usr/bin/dpkg` 모양)[6]. 이 목록으로 파일이 바뀌었는지 검사하는 방법은 [패키지 파일 변조 확인](package-verify.md)에서 다룹니다.

dpkg 는 풀 때 새 파일을 `경로.dpkg-new` 로 풀었다가 원래 이름으로 바꾸고, 예전 파일은 `경로.dpkg-tmp` 로 백업했다가 설치가 끝나면 지웁니다[1]. 설정 파일을 처리할 때는 새 판을 설치하면 예전 수정본을 `경로.dpkg-old` 로, 예전 판을 유지하면 새 원본을 `경로.dpkg-dist` 로 남길 수 있습니다[1]. `/etc` 아래의 `.dpkg-old` 파일은 관리자가 고친 설정이 있었다는 흔적입니다.

### history.log 묶음

apt 는 로그를 열 때 빈 줄 하나와 `Start-Date:` 줄을 쓰고, 이어서 아래 순서로 값이 있는 줄만 씁니다[7].

1. `Commandline:` — apt 가 받은 인자
2. `Requested-By:` — `사용자이름 (UID)`
3. `Comment:` — 최신 apt 에서 `APT::History::Comment` 가 있을 때
4. `Install:`, `Reinstall:`, `Upgrade:`, `Downgrade:`, `Remove:`, `Purge:`

닫을 때는 사라진 패키지가 있으면 `Disappeared:`, dpkg 오류가 있으면 `Error:`, 마지막으로 `End-Date:` 를 씁니다[7]. 빈 값의 태그는 줄 자체를 쓰지 않습니다[7].

패키지 항목은 `이름:아키텍처 (버전)` 모양이고 `, ` 로 이어집니다. `Install:` 은 `(설치할버전)` 이고 의존성으로 딸려 온 패키지에만 `, automatic` 이 붙습니다. `Upgrade:`·`Downgrade:` 는 `(현재버전, 새버전)`, `Remove:`·`Purge:` 는 `(현재버전)` 입니다[7]. 아래는 만든 예시입니다.

```

Start-Date: 2024-07-24  16:48:56
Commandline: apt install htop
Requested-By: alice (1000)
Install: libnl-genl-3-200:amd64 (3.7.0-0.3build1, automatic), htop:amd64 (3.3.0-4build1)
End-Date: 2024-07-24  16:49:01
```

`Requested-By:` 는 환경 변수 `SUDO_UID`, `PKEXEC_UID`, `PACKAGEKIT_CALLER_UID` 를 이 순서로 보고, 값이 0보다 큰 첫 UID 를 계정 이름과 함께 적습니다[7]. 그래서 sudo 로 실행하면 sudo 를 부른 사용자가 적히고, root 로 바로 로그인해 실행하면 이 줄이 없습니다.

`Commandline:` 은 apt 가 받은 인자(`argv`)를 공백으로 이어 붙인 값입니다. 이때 작은따옴표·큰따옴표·줄바꿈 문자는 빼고, 인자 수에 비례한 크기의 버퍼를 넘는 부분은 잘립니다[9]. 자동 업데이트는 자기 명령줄(`/usr/bin/unattended-upgrade`)을 이 값으로 넣어 같은 파일에 묶음을 남깁니다[15][19].

term.log 는 `Log started: 시각` 으로 시작해 `Log ended: 시각` 으로 끝나고, 그사이에 dpkg 출력이 그대로 들어갑니다[7]. history.log 는 권한을 0644 로 맞춥니다. term.log 는 권한을 0640 으로 맞추고, root 로 실행할 때는 소유를 `root:adm` 으로 바꿉니다[7]. 두 파일 모두 매월 돌리고 12개를 남기며 압축합니다[10].

### 설정 파일에서 볼 것

`/etc/apt/apt.conf.d/` 의 `DPkg::Pre-Invoke`, `DPkg::Post-Invoke`, `DPkg::Pre-Install-Pkgs` 는 dpkg 를 부르기 전후에 `/bin/sh` 로 실행할 명령 목록입니다[11]. 패키지를 설치할 때마다 명령이 돌기 때문에 지속성 흔적을 찾을 때 이 폴더를 통째로 봅니다[17]. 지속성 전반은 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md)를 봅니다.

apt 는 이름이 `~`, `.disabled`, `.bak`, `.dpkg-` 뒤 소문자, `.ucf-` 뒤 소문자, `.save`, `.orig`, `.distUpgrade` 로 끝나는 설정 조각을 경고 없이 건너뜁니다[8]. 이런 이름의 파일은 적용되지 않은 설정입니다. 저장소 설정에서 `Trusted` 옵션을 켠 저장소는 서명 검증을 거치지 않으므로 따로 표시해 둡니다[18].

## 증거로서 의미

**증명하는 것**

- dpkg.log 는 그 시각(현지)에 어떤 패키지의 어떤 버전이 풀리고, 설정되고, 지워졌는지를 보여 줍니다. apt 를 거쳤든 `dpkg -i` 로 직접 설치했든 남습니다.
- history.log 는 apt 실행 한 번에 어떤 명령줄로 어떤 패키지를 설치·갱신·제거했는지, 의존성으로 딸려 왔는지(`automatic`), dpkg 오류가 있었는지를 보여 줍니다.
- `Requested-By:` 가 있으면 sudo·pkexec·PackageKit 을 거쳐 요청한 계정의 UID 를 보여 줍니다.
- status 파일은 수집 시점에 설치되어 있거나 설정 파일만 남은 패키지 목록을 보여 주고, `/var/backups/dpkg.status.N` 은 과거 날짜의 목록을 보여 줍니다.

**증명하지 못하는 것**

- 누가 로그인해 실행했는지는 history.log 만으로 알 수 없습니다. root 로 바로 실행했다면 `Requested-By:` 가 없습니다.
- `dpkg -i` 로 직접 설치한 패키지는 history.log 에 없고, dpkg.log 에도 `.deb` 파일을 어디서 가져왔는지는 없습니다.
- `Commandline:` 은 apt 가 받은 인자입니다. 사람이 직접 친 명령인지, 스크립트나 자동 업데이트가 부른 것인지는 따로 확인합니다.
- 패키지를 설치했다는 것은 그 프로그램을 실행했다는 뜻이 아닙니다. 실행 흔적은 [셸 명령 기록](../execution/shell-history/index.md)이나 [감사 로그의 실행 기록](../execution/auditd-execve.md)에서 찾습니다.
- 로그는 평문 파일이고 root 가 고칠 수 있습니다.

보고서에는 "2024-07-24 16:48:56(현지 시각, 시간대는 Asia/Seoul)에 apt 가 htop 을 설치한 기록이 있고, 요청한 계정은 UID 1000(alice)으로 기록되어 있다"처럼 기록으로 확인되는 만큼만 씁니다(만든 예시).

## 시각 해석

dpkg.log, history.log, term.log 의 시각은 모두 현지 시각이고 시간대 표시가 없습니다. dpkg 는 `localtime_r` 과 `%Y-%m-%d %H:%M:%S` 로[2], apt 는 `localtime_r` 과 `%F  %T` 로 시각을 만듭니다[7]. 연도는 있으므로 syslog 전통 형식처럼 연도를 추정할 필요는 없지만, 시간대는 대상 시스템의 `/etc/localtime` 으로 정해야 합니다. 시간대 확인은 [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md)을 봅니다. 쓰는 도중에 시간대를 바꾼 시스템이라면 바꾸기 전 줄은 예전 시간대 기준입니다.

history.log 의 `Start-Date` 는 apt 가 dpkg 작업 단계에 들어가 `DPkg::Pre-Invoke` 명령을 돌린 뒤 로그를 연 시각이고, `End-Date` 는 `DPkg::Post-Invoke` 명령을 돌리기 전에 로그를 닫은 시각입니다[7]. 두 시각은 명령을 친 시각이 아니라 dpkg 작업이 시작·끝난 때에 가깝습니다.

`info/패키지.list` 의 수정 시각은 그 패키지의 파일 목록이 마지막으로 바뀐 때, 곧 마지막 설치나 업그레이드 시각입니다[5]. 처음 설치한 시각이 아니라는 점에 주의합니다. `db-fsys:Last-Modified` 와 dissect.target 의 패키지 시각이 모두 이 값입니다[5][19]. 파일 시스템 시각의 해석은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)을 봅니다.

`/var/lib/apt/lists/` 의 `Release`·`InRelease` 파일 수정 시각은 저장소 목록을 마지막으로 받은 때를 추정하는 데 쓸 수 있습니다[18]. `unattended-upgrades-stamp` 의 수정 시각은 자동 업데이트가 마지막으로 돈 때입니다[15].

## 함정과 한계

- **순환으로 사라지는 기록.** dpkg.log 와 apt 로그는 매월 돌리고 12개를 남기므로 오래된 기록은 사라집니다. 비어 있는 달에는 돌리지 않으므로(`notifempty`) 남는 기간이 1년보다 길 수 있습니다[3][10]. 운영체제 설치 무렵의 흔적은 [설치 날짜 가늠하기](../system-info/install-date.md)를 함께 봅니다.
- **수집 목록의 차이.** UAC 의 dpkg 수집 정의는 `/var/log/dpkg.log` 와 `/var/lib/dpkg/status` 만 가져오고, 회전본과 `/var/log/apt` 는 `/var/log` 전체를 가져오는 로그 수집 정의에 들어 있습니다[17]. ForensicArtifacts 정의는 `dpkg.log*`, `apt/history.log*`, `apt/term.log*` 까지 포함합니다[16]. 패키지 정의만 골라 수집했다면 회전본과 `/var/log/apt`, `/var/backups/dpkg.status.*`, `info/*.list` 를 따로 챙깁니다.
- **plaso 가 모르는 태그.** plaso `apt_history` 가 아는 본문 태그는 `Commandline`·`Downgrade`·`Error`·`Install`·`Purge`·`Remove`·`Requested-By`·`Upgrade` 뿐입니다[20]. `Reinstall:`, `Comment:`, `Disappeared:` 가 들어 있는 묶음은 빠지거나 읽기 오류가 날 가능성이 있으니 원문과 대조합니다.
- **plaso 가 덮어쓰는 값.** plaso 는 한 묶음 안에서 태그 줄마다 명령과 패키지 값을 덮어쓰므로, `Install:` 과 `Upgrade:` 가 함께 있는 묶음은 마지막 줄 값만 남습니다[20]. dissect.target 은 패키지마다 레코드를 따로 만듭니다[19].
- **dissect.target 이 건너뛰는 dpkg.log 줄.** 공백으로 나눠 여섯 조각인 줄만 읽고, 그중 `status`·`install`·`upgrade`·`remove`·`trigproc` 만 레코드로 냅니다[19]. `startup`·`conffile` 줄은 물론 `configure`·`purge`·`disappear` 줄도 결과에 없습니다. plaso `dpkg` 는 네 가지 줄 모양을 모두 읽습니다[20].
- **dissect.target 이 버리는 status 항목.** `Status:` 에 `installed` 라는 글자가 없는 항목(`config-files`, `unpacked` 등)을 건너뛰고, `-old` 로 끝나는 사본 파일도 읽지 않습니다[19]. 지운 패키지의 흔적은 status 원문을 직접 봅니다.
- **남지 않는 `.deb`.** `apt` 명령은 받은 `.deb` 를 설치 뒤 지우는 설정(`APT::Keep-Downloaded-Packages` false)으로 동작합니다[13]. `/var/cache/apt/archives/` 에 파일이 없다고 설치가 없었던 것은 아닙니다.
- **흔적 지우기.** 로그 한 줄을 지우거나 파일을 비울 수 있고, status 파일도 텍스트라 고칠 수 있습니다. dpkg.log, history.log, term.log, status, `/var/backups` 사본, `info/*.list` 수정 시각은 서로 다른 곳에 남으므로, 하나만 비어 있거나 어긋나면 조작을 의심할 근거가 됩니다. 방법은 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

history.log 앞부분을 헥스로 보면 아래 모양이 됩니다. apt 코드의 출력 형식에 맞춰 만든 예시입니다.

```
00000000  0a 53 74 61 72 74 2d 44  61 74 65 3a 20 32 30 32  |.Start-Date: 202|
00000010  34 2d 30 37 2d 32 34 20  20 31 36 3a 34 38 3a 35  |4-07-24  16:48:5|
00000020  36 0a 43 6f 6d 6d 61 6e  64 6c 69 6e 65 3a 20 61  |6.Commandline: a|
00000030  70 74 20 69 6e 73 74 61  6c 6c 20 68 74 6f 70 0a  |pt install htop.|
```

1. 0x00 의 `0a` 는 묶음 앞에 apt 가 넣는 빈 줄입니다. 파일 중간에서는 앞 묶음의 `End-Date` 줄 바로 뒤에 이 빈 줄이 옵니다.
2. 0x17~0x18 의 `20 20` 은 날짜와 시각 사이의 공백 두 칸입니다(`%F  %T`). 검색식이나 파서를 직접 짤 때 공백 하나로 잡으면 맞지 않습니다.
3. 시각 문자열 끝에 시간대가 없습니다. 이 값을 UTC 로 옮기려면 대상 시스템의 시간대를 따로 정합니다.

### 공개 도구로 한 번

- **plaso**: `apt_history` 와 `dpkg` 텍스트 플러그인이 두 로그를 읽고, 시각을 현지 시각으로 표시해 두었다가 분석 때 정한 시간대로 바꿉니다[20].
- **dissect.target**: `apt.logs` 는 `/var/log/apt/history.*` 를, `dpkg.logs` 는 `/var/log/dpkg.log*` 를 읽고, 대상 시스템의 시간대를 붙입니다[19]. `dpkg.packages --output-files` 는 `.list` 와 `.md5sums` 로 파일별 레코드를 냅니다[19]. 앞의 함정을 함께 봅니다.
- **Velociraptor**: `Linux.Debian.Packages` 는 status 파일을 파싱하고, `Linux.Debian.AptSources` 는 `*.list`·`*.sources` 를 읽어 `Release` 파일 시각과 함께 보여 줍니다[18].
- **UAC**: 라이브 수집에서 `dpkg -l`, `dpkg -V` 결과를 받습니다[17].
- **명령**: 마운트한 이미지에서는 `grep -h " install \| remove \| purge " dpkg.log*` 처럼 로그를 직접 읽거나, 라이브 시스템에서 `dpkg-query -W -f='${Package} ${db-fsys:Last-Modified}\n'` 로 패키지마다 `.list` 수정 시각을 뽑습니다(만든 예시 명령)[5].

여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md)를 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [sudo·su 사용 기록](../logins/sudo-su.md) | `Requested-By:` 의 계정이 같은 시각에 `apt` 를 sudo 로 실행했는지 |
| [셸 명령 기록](../execution/shell-history/index.md) | `apt install`, `dpkg -i` 명령과 `.deb` 파일 경로 |
| [UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md) | `Requested-By:` 의 UID 가 지금도 같은 계정인지 |
| [패키지 파일 변조 확인](package-verify.md) | 설치된 파일이 `.md5sums` 와 맞는지 |
| [systemd 서비스와 타이머](../persistence/systemd-units.md) | 설치된 패키지가 등록한 서비스, 자동 업데이트 타이머 |
| [cron·anacron·at](../persistence/cron-at.md) | `/etc/cron.daily` 의 패키지 관련 작업(popularity-contest 는 `/etc/cron.daily/popularity-contest`[21]) |
| popularity-contest 기록 | 설치되어 있다면 패키지마다 가장 최근에 쓴 프로그램과 그 파일의 atime·ctime(UTC epoch 초)[21] |

popularity-contest 의 ctime 은 패키지를 새 판으로 올리면 다시 정해지므로 처음 설치한 시각으로 단정하지 않습니다[21]. atime 은 마운트 옵션에 따라 갱신이 줄어들 수 있습니다. plaso 는 이 기록에서 atime 으로만 이벤트를 만듭니다[21].

## 실습

공개 Linux 디스크 이미지(NIST CFReDS 등)나 직접 만든 Ubuntu 가상 머신 이미지로 아래 질문을 풀어 봅니다.

1. history.log 에서 `Requested-By:` 가 없는 묶음은 무엇이고, 같은 시각의 인증 로그에서 root 로그인이나 자동 업데이트 흔적을 찾을 수 있는가?
2. dpkg.log 에는 있지만 history.log 에는 없는 `install` 줄이 있는가? 있다면 `.deb` 파일은 어디서 왔을 가능성이 있는가?
3. status 에서 `config-files` 상태인 패키지는 무엇이고, 언제 지웠는지 dpkg.log 에서 찾을 수 있는가?
4. `/var/backups/dpkg.status.0` 과 지금 status 를 비교하면 어떤 패키지가 늘거나 줄었는가? 두 파일의 수정 시각은 언제인가?
5. `/etc/apt/apt.conf.d/` 에 `Pre-Invoke`·`Post-Invoke` 를 쓰는 파일이 있는가? 그 파일은 어느 패키지 소속인가(`info/*.list` 에 있는가)?

## 참고 문헌

1. dpkg, dpkg(1) man 페이지 — https://github.com/guillemj/dpkg/blob/main/man/dpkg.pod
2. dpkg, lib/dpkg/log.c — https://github.com/guillemj/dpkg/blob/main/lib/dpkg/log.c
3. dpkg, debian/dpkg.cfg·debian/dpkg.logrotate — https://github.com/guillemj/dpkg/blob/main/debian/dpkg.cfg , https://github.com/guillemj/dpkg/blob/main/debian/dpkg.logrotate
4. dpkg, src/dpkg-db-backup.sh·debian/dpkg.dpkg-db-backup.timer·debian/dpkg.cron.daily — https://github.com/guillemj/dpkg/blob/main/src/dpkg-db-backup.sh , https://github.com/guillemj/dpkg/tree/main/debian
5. dpkg, dpkg-query(1) man 페이지·lib/dpkg/pkg-format.c — https://github.com/guillemj/dpkg/blob/main/man/dpkg-query.pod , https://github.com/guillemj/dpkg/blob/main/lib/dpkg/pkg-format.c
6. dpkg, deb-md5sums(5) man 페이지 — https://github.com/guillemj/dpkg/blob/main/man/deb-md5sums.pod
7. APT, apt-pkg/deb/dpkgpm.cc — https://github.com/Debian/apt/blob/main/apt-pkg/deb/dpkgpm.cc
8. APT, apt-pkg/init.cc·CMakeLists.txt — https://github.com/Debian/apt/blob/main/apt-pkg/init.cc , https://github.com/Debian/apt/blob/main/CMakeLists.txt
9. APT, apt-pkg/contrib/cmndline.cc — https://github.com/Debian/apt/blob/main/apt-pkg/contrib/cmndline.cc
10. APT, debian/apt.logrotate — https://github.com/Debian/apt/blob/main/debian/apt.logrotate
11. APT, apt.conf(5) — https://github.com/Debian/apt/blob/main/doc/apt.conf.5.xml
12. APT, apt-mark(8) — https://github.com/Debian/apt/blob/main/doc/apt-mark.8.xml
13. APT, apt-private/private-cmndline.cc — https://github.com/Debian/apt/blob/main/apt-private/private-cmndline.cc
14. APT, 커밋 "Add a --comment option to record Comment: in history"(2024-11-18) — https://github.com/Debian/apt/commit/1c4fa81cc398e21868ad237509f1ea8e772d76de
15. unattended-upgrades, unattended-upgrade — https://github.com/mvo5/unattended-upgrades/blob/master/unattended-upgrade
16. ForensicArtifacts, artifacts/data/linux.yaml — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
17. UAC, artifacts/files/packages/·artifacts/files/logs/var_log.yaml·artifacts/live_response/packages/ — https://github.com/tclahr/uac/tree/main/artifacts/files/packages , https://github.com/tclahr/uac/blob/main/artifacts/files/logs/var_log.yaml , https://github.com/tclahr/uac/tree/main/artifacts/live_response/packages
18. Velociraptor, Linux.Debian.Packages·Linux.Debian.AptSources — https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Debian/Packages.yaml , https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Debian/AptSources.yaml
19. dissect.target, plugins/os/unix/linux/debian/apt.py·dpkg.py — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/debian/apt.py , https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/debian/dpkg.py
20. plaso, parsers/text_plugins/apt_history.py·dpkg.py — https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/apt_history.py , https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/dpkg.py
21. plaso, parsers/text_plugins/popcontest.py — https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/popcontest.py
