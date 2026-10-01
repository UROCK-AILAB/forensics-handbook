---
title: "VMware ESXi 로그"
parent: "아티팩트 · 서버 애플리케이션"
nav_order: 770
---

# VMware ESXi 로그 (hostd·auth·shell·vobd)

VMware ESXi 호스트는 관리 서비스, 인증, ESXi Shell, VMkernel 이 한 일을 여러 텍스트 로그 파일에 나눠 남기고, 이 로그로 누가 언제 호스트에 로그인해 셸을 켜고 어떤 명령을 입력했는지 확인합니다. ESXi 는 리눅스가 아니라 VMware 의 하이퍼바이저이지만, 리눅스 서버처럼 셸·SSH·syslog 로 조사하므로 이 핸드북에서 다룹니다. 로그는 기본으로 scratch 볼륨이나 램디스크에 짧은 기간만 남기 때문에 원격 syslog 서버의 사본과 지원 번들 (support bundle) 을 함께 확인합니다.

## 무엇을 기록하나 · 왜 생기나

ESXi 는 호스트에서 일어난 일을 syslog 기능으로 로그 파일에 기록하고[1], 로그를 만든 구성 요소별로 파일을 나눕니다[2]. 파일마다 공식 문서가 적은 용도와, 침해 조사에서 그 파일로 찾는 기록은 다음과 같습니다.

| 파일 | 공식 문서의 용도 | 침해 조사에서 찾는 기록 |
|---|---|---|
| `auth.log` | 로컬 시스템 인증과 관련된 모든 사건[1], ESXi Shell 인증 성공·실패[2] | 로그인 성공·실패, 비밀번호 변경[8][9] |
| `hostd.log` | 호스트와 가상 머신을 관리·설정하는 에이전트(hostd)의 기록, 가상 머신과 호스트의 작업·이벤트[1][2] | SSH·콘솔·웹 콘솔 로그인, 계정 생성, 비밀번호 변경, 데이터스토어 파일 올리기·내려받기·지우기[8][9] |
| `shell.log` | ESXi Shell 에 입력한 모든 명령과 셸을 켠 때 같은 셸 사건[1][2] | 셸에서 실행한 명령[8][9], SSH 켜기·끄기[11] |
| `syslog.log` | 일반 로그 메시지, 관리 서비스 초기화, watchdog, 예약 작업, DCUI 사용[1][2] | DCUI(호스트 콘솔 화면) 로그인, SFTP 로 연 파일과 폴더[8][9] |
| `vobd.log` | VMkernel 관찰 사건 (VMkernel Observation, VOB)[2] | SSH 세션 열기·닫기, 셸·SSH 켜기·끄기, 재부팅, 비밀번호 변경[8][9] |
| `vmkernel.log` | 장치 탐색, 스토리지, 네트워크를 포함한 VMkernel 핵심 기록[2] | 받아들인 원격 연결, 설치 패키지에 없는 파일의 실행 거부[8][9] |
| `vmksummary.log` | 호스트 시작·종료 요약과 한 시간마다 남기는 heartbeat[2] | 재부팅 시각, 기록이 끊긴 구간 |
| `rhttpproxy.log` | 다른 ESXi 웹 서비스를 대신해 중계한 HTTP 연결[2] | 접속을 시도한 원격 주소[8][9] |
| `vmauthd.log` | — | 접속을 시도한 원격 주소[8][9] |
| `vpxa.log` | vCenter Server 와 통신하는 에이전트(vpxa)의 기록[1][2] | vCenter 가 이 호스트에 보낸 작업 |
| `esxupdate.log` | 패치·업데이트 설치 기록[2] | 설치한 패키지 |
| `vmsyslogd-dropped.log` | syslog 서비스가 메시지를 버린 기록[2] | 로그가 빠졌을 수 있는 구간 |
| `vmware.log` | 가상 머신 설정 파일과 같은 폴더에 생기고, 전원 사건·장애·가상 하드웨어 변경·vMotion·복제를 기록[1] | 가상 머신을 끄고 켠 시각 |

## 위치와 버전별 차이

공식 문서끼리 경로를 적는 방식이 다릅니다. vSphere 8.0 보안 문서는 `/var/log/auth.log` 처럼 `/var/log` 아래로 적고[1], Broadcom 지원 문서는 로그가 `/var/run/log` 에 모여 있다고 적습니다[2]. 지원 번들에서 로그 파일은 `/var/run/log` 아래에 들어갑니다[10]. 실제 호스트나 번들에서는 두 폴더와 뒤에 나올 `/scratch/log` 를 모두 확인합니다.

로그가 재부팅 뒤에도 남는지는 저장 위치에 달려 있습니다. ESXi 는 기본으로 로그를 로컬 scratch 볼륨이나 램디스크에 두고, scratch 가 정의돼 있으면 기본 로그 폴더는 `/scratch/log` 입니다[5]. 로컬 파일 시스템에서 재부팅 뒤에도 남는 곳은 `/scratch` 뿐입니다[4]. 그래서 조사할 때는 먼저 로그 설정부터 확인합니다.

| 설정 | 뜻 |
|---|---|
| `Syslog.global.logDir` | 로그 폴더. NFS·VMFS 볼륨도 되고 `[datastorename]path` 형식으로 적음[4] |
| `Syslog.global.logDirUnique` | 켜면 `logDir` 뒤에 호스트 이름 폴더를 붙임. 여러 호스트가 같은 NFS 폴더를 쓸 때 씀[4] |
| `Syslog.global.logHost` | 로그를 보낼 원격 syslog 서버 목록. 비어 있으면 보내지 않음[5]. `udp://`·`tcp://` 기본 포트 514, `ssl://` 기본 포트 1514, 기본 formatter RFC_3164[4] |
| `Syslog.global.defaultSize` | 파일이 이 크기(KiB)에 이르면 새 파일을 만듦[4] |
| `Syslog.global.defaultRotate` | 남길 이전 로그 파일 수[4] |

설정 값은 `esxcli system syslog config get` 으로 보고[5], 로그 종류별 순환 크기와 개수는 `esxcli system syslog config logger list` 로 봅니다[6]. 이전 파일은 `vmkernel.0.gz` 처럼 번호가 붙은 gzip 파일로 남습니다[6]. 순환 값은 자료마다 다르게 나옵니다. Broadcom 지원 문서 318939 는 `defaultSize` 기본값을 1024 KB, `defaultRotate` 기본값을 8 로 적고[5], 지원 문서 411497 의 예시 출력에서 `vmkernel` 은 10240 KiB 씩 11개이며[6], LevelBlue 글의 표는 `hostd.log` 10 MB 10개, `vmkernel.log` 10 MB 8개, `auth.log`·`shell.log`·`syslog.log`·`vobd.log` 등은 1 MB 8개로 적습니다[8]. 실제 값은 분석 대상 호스트의 설정으로 확인합니다.

ESXi 7.0 Update 1 부터는 syslog 와 별도로 감사 기록 (audit record) 을 호스트에 저장하는 설정이 있습니다. `esxcli system auditrecords local enable` 로 켜고, 저장 폴더를 따로 정하지 않으면 `/scratch/auditLog` 를 씁니다[4]. 켜져 있는 호스트라면 이 폴더도 수집합니다.

표준 포트(TCP·UDP 514, SSL 1514)로 원격 전송을 하려면 `syslog` 방화벽 규칙을 켜야 하고, ESXi 8.0 U2b 부터는 비표준 포트의 원격 서버를 설정하면 vmsyslogd 가 방화벽 규칙을 자동으로 만듭니다[5]. `logHost` 가 적혀 있어도 방화벽 규칙이 꺼져 있었다면 원격 서버에 사본이 없을 수 있으므로 호스트의 방화벽 규칙 상태도 함께 봅니다.

## 구조

### 한 줄의 모양

ESXi 8.0 부터 로그 형식이 ABNF 로 표준화됐고, vmsyslogd 가 쓰는 모든 로그에 심각도 (severity), 프로그램 이름, 프로세스 번호 필드가 더해졌습니다[3]. 같은 메시지가 7.0 과 8.0 에서 어떻게 다른지는 Broadcom 지원 문서의 예시로 알 수 있습니다[3]. 아래 예시에서 `MM-DD`, `hh:mm:ss` 는 날짜·시각 자리이고, `…` 는 사용자·주소가 들어가는 자리입니다.

```
# vobd.log, 7.0
2025-MM-DDThh:mm:ss.483Z: [UserLevelCorrelator] 1019369886505us: [vob.user.ssh.session.opened] SSH session was opened for '…'.
# vobd.log, 8.0
2025-MM-DDThh:mm:ss.737Z In(14) vobd[2097521]:  [UserLevelCorrelator] 1012726884193us: [vob.user.ssh.session.closed] SSH session was closed for '…'.

# hostd.log, 7.0
2025-MM-DDThh:mm:ss.266Z error hostd[265267] [Originator@6876 sub=Default] IpmiIfcOpenIpmiOpen: open(/dev/ipmi0, RDWR) failed 2 m
# hostd.log, 8.0
2025-MM-DDThh:mm:ss.073Z Er(163) Hostd[2098450]: [Originator@6876 sub=Default] IpmiIfcOpenIpmiOpen: open(/dev/ipmi0, RDWR) failed 2 m

# vmkernel.log, 7.0
2025-MM-DDThh:mm:ss.630Z cpu0:262792)Jumpstart plugin swapobjd activated.
# vmkernel.log, 8.0
2025-MM-DDThh:mm:ss.810Z In(182) vmkernel: cpu0:2098001)Jumpstart plugin swapobjd activated.
```

8.0 줄의 `In(14)` 에서 두 글자는 심각도이고 괄호 안 숫자는 심각도와 시설 (facility) 코드로 계산한 값입니다[3]. 심각도는 `Em`(Emergency), `Al`(Alert), `Cr`(Critical), `Er`(Error), `Wa`(Warning), `No`(Notice), `In`(Informational), `Db`(Debug) 여덟 가지입니다[3]. `vobd[2097521]` 은 프로그램 이름과 프로세스 번호이고, `vmkernel:` 처럼 프로세스 번호는 빠질 수 있습니다[3]. 7.0 의 `error hostd` 가 8.0 에서 `Er(163) Hostd` 로 바뀌듯 프로그램 이름의 대소문자도 달라지므로, 두 버전의 로그를 함께 검색할 때는 대소문자를 구분하지 않습니다.

### 찾을 메시지

아래 표는 QELP 가 로그 종류마다 찾는 메시지의 앞부분입니다[9]. `...` 자리에는 사용자 이름이나 경로가 들어가고, 오른쪽 열은 QELP 가 붙이는 분류입니다.

| 로그 | 메시지 앞부분 | QELP 분류 |
|---|---|---|
| `hostd.log` | `Accepted password for user`, `User ...@(IPv4 주소) logged in`, `SSH session was opened` | Logon |
| `hostd.log` | `User ...@(IPv4 주소) logged out`, `SSH session was closed` | Logoff |
| `hostd.log` | `SSH login has failed` | Failed-Logon |
| `hostd.log` | `SSH access has been`, `The ESXi command line shell`, `Account ... was created`, `Login password for user ... has been changed`, `Password was changed for account` | User_activity |
| `hostd.log` | `File upload to path`, `File download from path`, `Deletion of file or directory`, `file delete`, `DatastoreBrowserImpl::SearchInt ... dsPath:`, `Create requested for`, `Got HTTP` | User_activity |
| `syslog.log`(프로그램 이름 `sftp-server`, `DCUI`) | `User ... logged in`, `User ... logged out`, `password changed for`, `Login password for user` | Logon, Logoff, User_activity |
| `syslog.log`(프로그램 이름 `sftp-server`) | `opendir`, `closedir`, `open "`, `close "`, `sent status` | User_activity(타임라인에는 넣지 않음) |
| `auth.log` | `user ... login`, `Accepted keyboard-interactive`, `Connection from`, `Session opened for` | Logon |
| `auth.log` | `Session closed for`, `Connection closed by`, `Disconnected from` | Logoff |
| `auth.log` | `authentication failure;`, `error [login` | Failed-Logon |
| `auth.log` | `password changed`, `User ... running command` | User_activity |
| `vobd.log` | `SSH session was opened`, `SSH session was closed`, `Authentication of user ... has` | Logon, Logoff |
| `vobd.log` | `The ESX command line shell has been`, `Administrator access to the host has been`, `SSH access has been`, `Login password for user` | User_activity |
| `vmkernel.log` | `Accepted connection from`, `Error reading from pending connection:` | Remote_access |
| `vmkernel.log` | `sh: exec denied` | Execution_denied |
| `vmauthd.log` | `Connect from remote socket` | Remote_access |
| `rhttpproxy.log` | `New proxy client` | Remote_access |
| `shell.log`, `esxcli.log` | 모든 줄 | Bash_activity, User_activity |

`vmkernel.log` 의 실행 거부 기록은 설치된 VIB (vSphere Installation Bundle) 에 들어 있지 않은 파일을 실행하려 할 때 남고, `execInstalledOnly` 설정이 켜져 있을 때만 생깁니다[8].

SSH 를 켜고 들어가 SFTP 로 데이터스토어를 연 흐름은 `shell.log`, `auth.log`, `syslog.log` 에 다음 같은 줄로 남습니다[11]. 줄 모양은 침해 사고 사례의 로그를 따랐고, 시각·주소·계정·프로세스 번호는 만든 예시입니다.

```
# shell.log: SSH 를 끄고 켠 줄
2026-03-02T09:10:05Z SSH: SSH login disabled
2026-05-12T00:51:21Z SSH: SSH login enabled

# auth.log: SSH 접속과 로그인
2026-05-12T01:45:34Z sshd[5200101]: Connection from 192.0.2.25 port 50122
2026-05-12T01:45:34Z sshd[5200101]: Accepted keyboard-interactive/pam for opsuser from 192.0.2.25 port 50122 ssh2
2026-05-12T01:45:34Z sshd[5200101]: pam_unix(sshd:session): session opened for user opsuser by (uid=0)

# syslog.log: SFTP 로 /vmfs 를 조회한 줄
2026-05-12T01:56:42Z sftp-server[5200105]: statvfs "vmfs"
2026-05-12T01:56:47Z sftp-server[5200105]: opendir "vmfs"
```

`shell.log` 에서 `SSH login disabled` 줄 뒤에 나온 `SSH login enabled` 줄을 찾으면, 꺼 두었던 SSH 를 언제 다시 켰는지 알 수 있습니다[11]. 평소 SSH 를 꺼 두고 운영했는지는 관리 담당자에게 확인합니다[11]. `auth.log` 의 세 줄은 sshd 프로세스 번호가 같아서 한 접속으로 묶이고, 원격 주소와 포트, 인증 방식(`keyboard-interactive/pam`), 로그인한 계정이 남습니다[11]. `sftp-server` 줄은 sshd 와 다른 프로세스 번호로 남을 수 있어서 시각 순서로 SSH 세션과 이어 봅니다[11]. `statvfs "vmfs"` 와 `opendir "vmfs"` 는 SFTP 로 `/vmfs` 를 조회한 줄이고, 뒤따르는 `open`·`close` 줄에는 연 파일 경로와 읽고 쓴 바이트 수가 남습니다[11]. ESXi 에서 랜섬웨어를 실행하지 않고, Windows PC 에서 SSHFS 로 ESXi 파일 시스템을 드라이브처럼 연결해 암호화한 사례에서도 파일을 읽고 다시 쓰고 이름을 바꾼 기록이 이 `sftp-server` 줄로 남았습니다[11].

## 증거로서 의미

### 증명하는 것

- 호스트 시계 기준으로 그 시각에 그 계정의 로그인·로그아웃·로그인 실패가 기록됐다는 것(`auth.log`, `hostd.log`, `vobd.log`). `hostd.log` 의 `User ...@(IPv4 주소) logged in` 메시지에는 원격 주소도 함께 남습니다[9].
- SSH 나 ESXi Shell 을 켜고 끈 시각(`vobd.log`, `hostd.log`), 셸에 입력한 명령(`shell.log`)[1][9]. SSH 를 켜고 끈 사건은 `shell.log` 에도 `SSH: SSH login enabled`·`SSH: SSH login disabled` 줄로 남습니다[11].
- 계정을 만들거나 비밀번호를 바꾼 사건, 웹 콘솔이나 데이터스토어 브라우저로 파일을 올리고 내려받고 지운 사건(`hostd.log`)[8][9].
- SFTP 로 연 폴더와 파일(`syslog.log` 의 `sftp-server` 줄)[9].
- 호스트가 켜지고 꺼진 시각과, 한 시간마다의 heartbeat 가 끊긴 구간(`vmksummary.log`)[2].

### 증명하지 못하는 것

- `shell.log` 에 명령이 없다는 사실이 명령을 실행하지 않았다는 뜻이라는 것. 램디스크의 로그는 재부팅하면 사라지고[4][5], 순환으로 오래된 파일이 지워지며, syslog 서비스가 메시지를 버렸을 수도 있습니다[2].
- 명령이 성공했다는 것. `shell.log` 는 입력한 명령을 적을 뿐이므로 결과는 데이터스토어의 파일 변화나 `vmware.log` 의 전원 사건으로 확인합니다.
- 계정 뒤의 실제 사람. `root` 처럼 여러 사람이 함께 쓰는 계정은 로그인한 사람을 특정하지 못하고, vCenter 를 거친 작업은 vCenter 의 기록과 맞춰 봐야 합니다.
- 파일 내용. `hostd.log` 와 `syslog.log` 에는 올리고 내려받은 경로가 남을 뿐 내용은 남지 않습니다.

보고서에는 "이 시각(UTC)에 이 주소에서 root 계정으로 SSH 로그인한 기록과, 이어서 ESXi Shell 에 입력한 명령 기록이 있다" 처럼 로그로 확인되는 만큼만 씁니다.

## 시각 해석

로그 줄 맨 앞의 시각은 7.0 과 8.0 모두 `YYYY-MM-DDThh:mm:ss.sssZ` 형식입니다[3]. 끝의 `Z` 는 ISO 8601 표기로 UTC 를 뜻하므로 이 시각은 UTC 로 읽습니다. QELP 도 줄 앞의 `Z` 로 끝나는 시각만 읽고 이 값으로 타임라인을 정렬합니다[9]. `vobd.log` 줄 가운데의 `1019369886505us` 같은 값은 마이크로초 단위 숫자라서, 사건 시각으로는 줄 앞의 UTC 시각을 씁니다.

시각은 호스트 시계 기준이므로, 여러 호스트나 Windows 서버의 로그와 맞출 때는 각 호스트의 NTP 설정과 시계 오차를 먼저 확인합니다. 원격 syslog 서버에 쌓인 사본은 모양이 다를 수 있습니다. ESXi 8.0 은 밖으로 보내는 메시지를 RFC 3164 나 RFC 5424 형식으로 감싸고, 머리 부분과 시각 모양이 7.0 과 조금 다르며, 이 차이는 설정으로 7.0 과 똑같이 되돌릴 수 없습니다[3]. 원격 서버의 사본을 읽을 때는 서버가 붙인 수신 시각과 메시지 안의 시각을 구분합니다. 원격 서버 쪽 저장 형식은 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md) 에서 다룹니다.

## 함정과 한계

- 로그가 짧게 남습니다. 램디스크에 있는 로그는 재부팅하면 사라지고, 로컬에서 재부팅 뒤에도 남는 곳은 `/scratch` 뿐입니다[4][5]. 호스트를 재부팅하거나 다시 설치하기 전에 지원 번들을 받고, `logHost` 로 지정된 원격 서버의 사본을 함께 확보합니다.
- 조사자의 작업도 로그에 남습니다. 수집하려고 SSH 나 셸을 켜면 공격자가 켠 때와 같은 메시지가 남으므로, 조사자가 켠 시각과 사용한 주소를 기록해 둡니다.
- QELP 는 표에 적은 메시지만 골라 냅니다. 로그 종류별 CSV 에는 맞은 줄이 모두 들어가지만 `Timeline.csv` 에는 타임라인용으로 표시한 줄만 들어갑니다[9]. `vmkernel.log` 는 `Accepted connection from` 이나 `Error reading from pending connection:` 으로 시작하는 부분만 설명으로 잡으므로, 실행 거부(`sh: exec denied`) 분류는 한 줄에 이 문구와 앞의 두 문구 가운데 하나가 함께 있을 때만 결과에 나옵니다[9]. `vobd.log` 의 `Authentication of user ... has` 줄은 Logon 과 Logoff 에 한 번씩, 두 번 나옵니다[9]. 도구 결과만 보지 말고 원문을 함께 검색합니다.
- QELP 는 tar·tgz 를 풀 때 폴더 경로를 버리고 파일 이름만 남깁니다[9]. 한 번들 안에 같은 이름의 파일이 여러 폴더(예: `/var/run/log` 와 `/scratch/log`)에 있으면 나중에 푼 파일이 앞의 파일을 덮어씁니다. 번들 목록을 먼저 보고, 폴더가 여럿이면 폴더별로 따로 풀어 분석합니다.
- DFIR4vSphere 의 `Start-ESXi_Investigation` 은 `-ESXBundle` 없이 실행하면 로그 가운데 `hostd` 만 받아 `ESXi_(호스트 이름)_Hostd.log` 로 저장합니다. `shell.log` 나 `auth.log` 가 필요하면 지원 번들을 만들어야 합니다[10]. 이 스크립트는 `esxcli system syslog config get` 결과를 `_System_Guestrepo.csv` 에 쓰기 때문에 앞에서 저장한 guest store 저장소 설정을 덮어씁니다[10]. syslog 설정은 이 파일에서 읽되, guest store 설정이 필요하면 따로 확인합니다.
- 7.0 과 8.0 은 줄 모양이 다르고[3], 원격 서버로 보낸 사본은 머리 부분이 또 다릅니다. 한 가지 줄 모양만 가정한 정규식은 다른 버전의 줄을 놓칩니다.
- 호스트의 root 권한을 얻은 공격자는 로컬 로그를 지우거나 고칠 수 있습니다. 로컬 로그의 첫 줄 시각, 순환 파일 수, `vmksummary.log` 의 heartbeat 간격을 원격 사본과 비교하고, `vmsyslogd-dropped.log` 에 버린 메시지 기록이 있는지 봅니다[2]. 흔적을 지운 사건의 조사는 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md) 를 봅니다.

## 직접 분석해 보기

### 원문으로 한 번

ESXi 로그는 텍스트라서 원문으로 읽습니다.

1. 지원 번들을 받습니다. ESXi 콘솔이나 SSH 에서 `vm-support` 를 실행하면 .tgz 파일이 생기고, `-w` 를 주지 않으면 `/var/tmp/`, `/var/log/`, 현재 폴더, VMFS·VFFS 파티션 가운데 한 곳에 저장됩니다[7]. `vm-support -w /vmfs/volumes/DATASTORE_NAME` 으로 데이터스토어를 지정하거나, 조사 PC 에서 `ssh root@ESXHostnameOrIPAddress vm-support -s > vm-support-Hostname.tgz` 로 표준 출력을 받아 바로 저장할 수 있습니다[7]. vSphere Client 나 `https://ESXHostnameOrIPAddress/cgi-bin/vm-support.cgi` 로도 받습니다[7].
2. 번들을 풀기 전에 `tar -tzvf` 로 목록을 보고 `var/run/log`, `scratch/log` 아래 파일과 크기·수정 시각을 기록합니다.
3. 로그 종류마다 회전본을 포함해 오래된 순서로 이어 붙입니다. `zcat -f vobd.*.gz vobd.log` 처럼 쓰면 압축 파일과 평문 파일을 함께 읽습니다. 회전본을 잇는 순서는 파일마다 첫 줄과 마지막 줄의 시각을 보고 정합니다.
4. 위 표의 메시지 앞부분을 대소문자 구분 없이 검색합니다. 예를 들어 `grep -i -E "SSH access has been|command line shell has been|SSH session was opened" vobd.log hostd.log` 로 SSH·셸을 켠 시각과 세션을 뽑고, `grep "SSH: SSH login" shell.log` 로 `shell.log` 에 남은 SSH 켜기·끄기 줄도 함께 봅니다. 그 시각 전후의 `shell.log` 와 `auth.log` 줄을 봅니다.
5. `vmksummary.log` 에서 heartbeat 가 한 시간 넘게 빈 구간과 호스트 시작·종료 기록을 찾아, 그 구간에 다른 로그도 비어 있는지 비교합니다.

### 공개 도구로 한 번

- QELP 는 지원 번들이나 로그 압축 파일(zip, tar, gz, tgz)이 든 폴더를 받아 `uv run qelp (입력 폴더) (출력 폴더)` 로 실행합니다[9]. 압축 파일마다 `(파일 이름)_results` 폴더가 생기고, 그 안의 `Extracted_logs` 폴더에 푼 로그가, 그 옆에 `hostd.csv` 같은 로그 종류별 CSV 와 `Timeline.csv` 가 생깁니다[9]. `Timeline.csv` 의 필드는 `Timestamp`, `Description`, `Access Type`, `Source CSV` 입니다[9]. 읽는 로그는 `hostd`, `syslog`, `shell`, `auth`, `vmauthd`, `vmkernel`, `vobd`, `esxcli`, `rhttpproxy` 로 시작하는 파일과 그 회전본(`hostd.0.gz` 등)입니다[9].
- DFIR4vSphere 는 VMware PowerCLI 를 쓰는 PowerShell 모듈입니다. vCenter 에 연결한 뒤 `Get-VMHost | Start-ESXi_Investigation` 을 실행하면 호스트마다 폴더를 만들고 실행 중인 프로세스, 서비스, 네트워크 연결, 로컬 계정, 권한, VIB 서명 검사 결과, 설정 값 등을 CSV 로 저장하며, `-ESXBundle` 을 주면 지원 번들도 받습니다[10]. 로컬 계정 목록(`_System_accounts.csv`)과 VIB 서명 검사 결과(`_Software_VIBSigCheck.csv`)는 로그에 나온 계정 생성, 설치되지 않은 파일의 실행 기록과 비교할 때 씁니다.
- 같은 모듈의 `Start-VC_Investigation` 은 vCenter 에 기록된 vSphere API 호출 기록인 VI 이벤트를 JSON 으로 받습니다. VI 이벤트의 기본 보존 기간은 30일이고, JSON 의 `CreatedTime` 필드를 시각으로 씁니다[10].

여러 로그를 합친 타임라인은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 에서, 로그를 함께 보는 절차는 [로그 분석](../../03-techniques/analysis/log-analysis.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 원격 syslog 서버의 사본 | 로컬 로그가 순환·재부팅·삭제로 사라진 구간의 기록 | [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md) |
| vCenter 의 VI 이벤트 | vCenter 를 거친 로그인과 호스트·가상 머신 작업. 기본 30일 보존[10] | — |
| 가상 머신 폴더의 `vmware.log` | 가상 머신 전원 사건과 가상 하드웨어 변경 시각[1] | — |
| 리눅스 서버의 인증 로그 | ESXi 에 접속한 관리 서버나 점프 서버에서 나간 SSH 접속 | [인증 로그](../logins/auth-log.md) |
| 리눅스 서버의 랜섬웨어 흔적 | 같은 사건에서 리눅스 서버에 남은 실행·암호화 흔적 | [랜섬웨어가 돌았나](../../04-scenarios/intrusion/ransomware.md) |
| 접속 출발지인 관리용 PC | 다른 PC 에서 SSH·SFTP 로 데이터스토어를 암호화했을 때 PC 와 ESXi 를 오가며 보는 순서 | [랜섬웨어가 돌았나](../../04-scenarios/intrusion/ransomware.md) |
| 다른 하이퍼바이저 | KVM 호스트에서 같은 질문을 풀 때 볼 로그 | [가상 머신 (KVM·libvirt)](../containers/kvm-libvirt.md) |

## 실습

시험용 ESXi 호스트나 공개된 ESXi 지원 번들로 다음 질문을 풀어 봅니다.

1. `Syslog.global.logDir` 와 `Syslog.global.logHost` 값은 무엇이고, 로그는 재부팅 뒤에도 남는 곳에 있었는가?
2. 로그 종류마다 가장 이른 줄의 시각은 언제이고, 순환 설정으로 계산한 보존 기간과 맞는가?
3. SSH 를 켠 시각과 끈 시각, 그 사이에 열린 SSH 세션의 사용자와 원격 주소는 무엇인가?
4. 그 세션 동안 `shell.log` 에 남은 명령은 무엇이고, 같은 시각의 `hostd.log` 에 파일 올리기·지우기 기록이 있는가?
5. QELP 의 `Timeline.csv` 에 없는데 원문 검색으로는 나오는 사건이 있는가?

## 참고 문헌

1. Broadcom TechDocs, vSphere 8.0 보안, "ESXi Log File Locations". https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/8-0/vsphere-security/securing-esxi-hosts/managing-esxi-log-files/esxi-log-file-locations.html
2. Broadcom 지원 문서 306962, "Location and Contents of ESXi log files". https://knowledge.broadcom.com/external/article/306962/location-and-contents-of-esxi-log-files.html
3. Broadcom 지원 문서 421596, "ESXi Log File Formats introduced from vSphere ESXi 8.0". https://knowledge.broadcom.com/external/article/421596/esxi-log-file-formats-introduced-from-vs.html
4. Broadcom TechDocs, vSphere 8.0 ESXi 설치와 설정, "ESXi Syslog Options". https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/8-0/esx-installation-and-setup/installing-and-setting-up-esxi-install/setting-up-esxi-install/configuring-system-logging-install/esxi-syslog-options-install.html
5. Broadcom 지원 문서 318939, "Configuring syslog on ESXi". https://knowledge.broadcom.com/external/article/318939/configuring-syslog-on-esxi.html
6. Broadcom 지원 문서 411497, "How to change the Parameters for saving & rotating of ESXi Host Logs". https://knowledge.broadcom.com/external/article/411497/how-to-change-esxi-log-rotation-paramete.html
7. Broadcom 지원 문서 313542, "Collecting diagnostic information for VMware ESX/ESXi using vm-support command". https://knowledge.broadcom.com/external/article/313542
8. Phalgun Kulkarni, "Parsing ESXi Logs for Incident Response", LevelBlue SpiderLabs Blog (2025-02-10). https://www.levelblue.com/blogs/spiderlabs-blog/parsing-esxi-logs-for-incident-response
9. Stroz Friedberg, QELP, README.md·src/qelp/esxi_to_csv.py·src/qelp/support.py. https://github.com/strozfriedberg/qelp
10. ANSSI, DFIR4vSphere, README.md·dfir4vsphere/Start-ESXi_Investigation.ps1·Start-VC_Investigation.ps1. https://github.com/ANSSI-FR/DFIR4vSphere
11. KISA, "2026년 상반기 침해사고 원인분석 및 대응조치 서비스 동향보고서 - 가상화 인프라 타겟 공격과 대응방안" (2026-08-21). https://www.boho.or.kr/kr/bbs/view.do?bbsId=B0000127&menuNo=205021&nttId=72167
