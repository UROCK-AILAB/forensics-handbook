---
title: 처음
nav_order: -100
permalink: /
---

# Linux 디지털 포렌식 핸드북

Linux 서버와 데스크톱에 어떤 흔적이 남는지, 그 흔적을 어떻게 찾고 읽고 해석하는지 정리한 한국어 핸드북입니다. 포렌식을 공부하는 사람과 현업에서 사건을 분석하는 사람을 위해 작성했습니다.

침해 사고는 Linux 서버에서 일어나는 경우가 많습니다. 그래서 로그인·명령 실행·지속성·로그를 중심에 두고, 파일 시스템(ext4·XFS)과 컨테이너까지 다룹니다. 배포판마다 경로가 다른 곳은 Debian·Ubuntu 계열과 RHEL·Fedora 계열로 나눠 적었습니다.

다른 OS 와 AI 서비스는 [Windows](https://urock-ailab.github.io/forensics-handbook-windows/)·[macOS](https://urock-ailab.github.io/forensics-handbook-mac/)·[Android](https://urock-ailab.github.io/forensics-handbook-android/)·[iOS](https://urock-ailab.github.io/forensics-handbook-ios/)·[AI 서비스](https://urock-ailab.github.io/forensics-handbook-ai/) 핸드북에서 다룹니다.

## 구성

핸드북은 네 갈래로 나뉩니다.

| 갈래 | 다루는 것 |
|---|---|
| **기반 구조** | ext4·XFS·Btrfs 파일 시스템, 파티션·LVM·LUKS, 계정·인증 구조, syslog·systemd 저널·auditd 로그 형식, 시각 값 |
| **아티팩트 사전** | 시스템 정보, 로그인과 SSH, 셸 기록과 실행 흔적, 지속성, 패키지, 파일 활동, 네트워크, 웹·DB·메일 서버, Docker 같은 컨테이너, 데스크톱, 외부 장치 |
| **분석 기법** | 라이브 응답·디스크 이미징·메모리 수집, 타임라인, 로그 분석, 지운 파일 되살리기, 메모리 분석, 루트킷 찾기 |
| **조사 시나리오** | "SSH 로 들어왔나", "웹 서버가 뚫렸나", "흔적을 지웠나" 같은 질문 하나에 여러 기록을 엮어 답하는 흐름 |

큰 주제는 허브 페이지에서 전체를 보여 주고, 하위 페이지에서 자세히 다룹니다.

## 페이지 구성

아티팩트 페이지는 대체로 아래 순서로 씁니다.

1. 무엇을 기록하고, 그 기록이 왜 생기는지
2. 저장 위치 — 배포판마다 다른 점
3. 구조 — 파일 형식, 로그 줄 모양, 설정 키
4. 증거로 쓸 때 — 증명할 수 있는 것과 없는 것
5. 시각 읽기 — 언제 바뀌는지, 어떤 기준 시각을 쓰는지
6. 함정과 한계 — 자주 하는 오해, 지웠을 때 남는 흔적
7. 직접 분석하기 — 파일을 직접 열어 한 번, 공개 도구로 한 번
8. 함께 볼 기록 — 다른 기록과 맞춰 보기
9. 실습 질문과 참고 자료

## 읽는 법

- 처음이라면 [디렉터리 구조와 주요 경로](01-foundations/filesystem/fhs-paths.md)와 [systemd 저널](01-foundations/logging/systemd-journal/index.md)부터 읽기를 권합니다.
- 사건을 앞에 두고 있다면 조사 시나리오에서 질문을 고르면 됩니다. 예: [SSH 로 들어왔나](04-scenarios/intrusion/ssh-intrusion.md), [웹 서버가 뚫렸나](04-scenarios/intrusion/web-compromise.md)
- 특정 기록만 궁금하다면 아래 목차에서 바로 찾으면 됩니다.

## 표기

- 명세나 공식 문서로 확인한 사실은 그대로 씁니다.
- 배포판은 Ubuntu 24.04 LTS 와 RHEL 9 계열을 기준으로 씁니다. 다른 판에서 달라지는 것은 그 자리에 판을 적습니다.
- 확인되지 않은 것은 쓰지 않습니다. 버전·배포판마다 다를 수 있는 것은 분석가가 직접 확인하는 방법을 적습니다.
- 헥스 예시는 명세를 보고 만든 예시입니다. 실제 검체에서 나온 값이 아닙니다.
- 특정 회사 제품을 편들지 않고 같은 기준으로 씁니다.
- 용어는 처음 나올 때 "한국어 (English)"로 한 번 적습니다.

# 목차


## 기반 구조

### 파일 시스템

- [ext4 (ext4)](01-foundations/filesystem/ext4/index.md)
  - [슈퍼블록과 블록 그룹 (Superblock·Block Group)](01-foundations/filesystem/ext4/superblock-block-group.md)
  - [아이노드와 익스텐트 (Inode·Extent)](01-foundations/filesystem/ext4/inode-extent.md)
  - [디렉터리 항목과 해시 트리 (Directory Entry·HTree)](01-foundations/filesystem/ext4/directory-htree.md)
  - [저널 (jbd2)](01-foundations/filesystem/ext4/journal-jbd2.md)
  - [시각 값 (atime·mtime·ctime·crtime)](01-foundations/filesystem/ext4/timestamps.md)
  - [지운 파일이 남기는 것 (Deleted Files)](01-foundations/filesystem/ext4/deleted-files.md)
- [XFS (XFS)](01-foundations/filesystem/xfs.md)
- [Btrfs (Btrfs)](01-foundations/filesystem/btrfs.md)
- [디렉터리 구조와 주요 경로 (FHS)](01-foundations/filesystem/fhs-paths.md)
- [권한·확장 속성·ACL·Capabilities (Permissions·xattr)](01-foundations/filesystem/permissions-xattr.md)

### 디스크와 볼륨

- [파티션 (MBR·GPT)](01-foundations/disk-volume/partitions.md)
- [LVM 논리 볼륨 (LVM)](01-foundations/disk-volume/lvm.md)
- [LUKS 디스크 암호화 (LUKS·dm-crypt)](01-foundations/disk-volume/luks.md)
- [스왑과 최대 절전 (Swap·Hibernation)](01-foundations/disk-volume/swap-hibernation.md)

### 사용자와 인증 구조

- [계정 파일 (passwd·shadow·group)](01-foundations/users-auth/passwd-shadow-group.md)
- [sudo 설정 (sudoers)](01-foundations/users-auth/sudoers.md)
- [인증 모듈 (PAM)](01-foundations/users-auth/pam.md)

### 로그 체계

- [syslog 형식과 rsyslog (syslog·rsyslog)](01-foundations/logging/syslog-rsyslog.md)
- [systemd 저널 (systemd Journal)](01-foundations/logging/systemd-journal/index.md)
  - [저널 파일 구조 (Journal File Format)](01-foundations/logging/systemd-journal/file-format.md)
  - [journalctl 로 읽기 (journalctl)](01-foundations/logging/systemd-journal/journalctl.md)
  - [손상·삭제된 저널 (Corrupted·Deleted Journals)](01-foundations/logging/systemd-journal/corruption.md)
- [감사 로그 형식 (auditd)](01-foundations/logging/auditd-format.md)
- [로그 순환 (logrotate)](01-foundations/logging/logrotate.md)
- [로그인 기록 파일 형식 (utmp·wtmp·btmp·lastlog)](01-foundations/logging/utmp-wtmp-format.md)

### 값 해석

- [Linux 의 시각 값 (epoch·나노초·마이크로초)](01-foundations/value-decoding/time-values.md)
- [UID·GID 와 사용자 이름 잇기 (UID·GID)](01-foundations/value-decoding/uid-gid.md)

## 아티팩트 사전

### 시스템 정보

- [배포판과 버전 (os-release)](02-artifacts/system-info/os-release.md)
- [호스트 이름·시간대·로캘 (Hostname·Timezone)](02-artifacts/system-info/hostname-timezone.md)
- [부팅과 종료 기록 (Boot·Shutdown)](02-artifacts/system-info/boot-shutdown.md)
- [설치 날짜 가늠하기 (Install Date)](02-artifacts/system-info/install-date.md)
- [커널 로그 (dmesg·kern.log)](02-artifacts/system-info/kernel-log.md)

### 로그인과 계정

- [로그인 기록 (wtmp·btmp·lastlog)](02-artifacts/logins/wtmp-btmp-lastlog.md)
- [인증 로그 (auth.log·secure)](02-artifacts/logins/auth-log.md)
- [SSH (SSH)](02-artifacts/logins/ssh/index.md)
  - [sshd 로그 (sshd Logs)](02-artifacts/logins/ssh/sshd-logs.md)
  - [authorized_keys (authorized_keys)](02-artifacts/logins/ssh/authorized-keys.md)
  - [known_hosts 와 클라이언트 설정 (known_hosts·ssh_config)](02-artifacts/logins/ssh/known-hosts.md)
  - [sshd 설정 (sshd_config)](02-artifacts/logins/ssh/sshd-config.md)
- [sudo·su 사용 기록 (sudo·su)](02-artifacts/logins/sudo-su.md)
- [계정 생성·변경 흔적 (useradd·usermod)](02-artifacts/logins/account-changes.md)

### 실행 흔적

- [셸 명령 기록 (Shell History)](02-artifacts/execution/shell-history/index.md)
  - [bash 기록 (.bash_history)](02-artifacts/execution/shell-history/bash.md)
  - [zsh·fish 기록 (zsh·fish)](02-artifacts/execution/shell-history/zsh-fish.md)
  - [기록 지우기와 끄기 (History Evasion)](02-artifacts/execution/shell-history/evasion.md)
- [감사 로그의 실행 기록 (auditd execve)](02-artifacts/execution/auditd-execve.md)
- [프로세스 회계 (acct·pacct)](02-artifacts/execution/process-accounting.md)
- [실행 중인 프로세스 (/proc)](02-artifacts/execution/proc.md)
- [최근 연 파일 (recently-used.xbel)](02-artifacts/execution/recently-used.md)

### 지속성

- [cron·anacron·at (cron)](02-artifacts/persistence/cron-at.md)
- [systemd 서비스와 타이머 (systemd Units·Timers)](02-artifacts/persistence/systemd-units.md)
- [init 스크립트와 rc.local (SysV init)](02-artifacts/persistence/sysv-init.md)
- [셸 시작 파일 (.bashrc·profile)](02-artifacts/persistence/shell-startup.md)
- [공유 라이브러리 가로채기 (LD_PRELOAD·ld.so.preload)](02-artifacts/persistence/ld-preload.md)
- [커널 모듈 (Kernel Modules)](02-artifacts/persistence/kernel-modules.md)
- [udev 규칙 (udev Rules)](02-artifacts/persistence/udev-rules.md)
- [PAM 모듈 변조 (PAM Backdoor)](02-artifacts/persistence/pam-backdoor.md)
- [데스크톱 자동 실행 (XDG Autostart)](02-artifacts/persistence/xdg-autostart.md)

### 패키지와 소프트웨어

- [dpkg·apt 기록 (Debian·Ubuntu)](02-artifacts/packages/dpkg-apt.md)
- [rpm·dnf·yum 기록 (RHEL·Fedora)](02-artifacts/packages/rpm-dnf.md)
- [snap·flatpak (snap·flatpak)](02-artifacts/packages/snap-flatpak.md)
- [언어 패키지 관리자 (pip·npm 등)](02-artifacts/packages/language-packages.md)
- [패키지 파일 변조 확인 (debsums·rpm -V)](02-artifacts/packages/package-verify.md)

### 파일 활동

- [임시 폴더와 메모리 파일 시스템 (/tmp·/dev/shm)](02-artifacts/file-activity/tmp-shm.md)
- [휴지통 (Trash)](02-artifacts/file-activity/trash.md)
- [썸네일 캐시 (Thumbnails)](02-artifacts/file-activity/thumbnails.md)
- [감사 로그의 파일 감시 (auditd Watches)](02-artifacts/file-activity/auditd-watches.md)
- [편집기 흔적 (vim·nano·less)](02-artifacts/file-activity/editor-artifacts.md)

### 네트워크

- [네트워크 설정 (NetworkManager·netplan)](02-artifacts/network/network-config.md)
- [방화벽 (iptables·nftables·ufw·firewalld)](02-artifacts/network/firewall.md)
- [이름 해석 (hosts·resolv.conf)](02-artifacts/network/name-resolution.md)
- [Wi-Fi 연결 기록 (Wi-Fi)](02-artifacts/network/wifi.md)
- [VPN (WireGuard·OpenVPN)](02-artifacts/network/vpn.md)

### 서버 애플리케이션

- [웹 서버 로그 (Apache·Nginx)](02-artifacts/servers/web-server-logs.md)
- [데이터베이스 서버 로그 (MySQL·PostgreSQL)](02-artifacts/servers/database-logs.md)
- [메일 서버 로그 (Postfix)](02-artifacts/servers/mail-server-logs.md)

### 컨테이너와 가상화

- [Docker (Docker)](02-artifacts/containers/docker/index.md)
  - [이미지와 레이어 (Images·Layers)](02-artifacts/containers/docker/images-layers.md)
  - [컨테이너 설정과 로그 (Container Config·Logs)](02-artifacts/containers/docker/container-logs.md)
  - [overlay 파일 시스템 (overlay2)](02-artifacts/containers/docker/overlay2.md)
- [containerd 와 Kubernetes 노드 (containerd·Kubernetes)](02-artifacts/containers/containerd-kubernetes.md)
- [Podman (Podman)](02-artifacts/containers/podman.md)
- [가상 머신 (KVM·libvirt)](02-artifacts/containers/kvm-libvirt.md)

### 데스크톱 환경

- [GNOME 흔적 (GNOME)](02-artifacts/desktop/gnome.md)
- [KDE 흔적 (KDE Plasma)](02-artifacts/desktop/kde.md)
- [비밀번호 보관함 (GNOME Keyring·KWallet)](02-artifacts/desktop/keyring.md)
- [Linux 의 브라우저 프로필 (Firefox·Chrome)](02-artifacts/desktop/browsers.md)

### 외부 장치

- [USB 장치 연결 기록 (USB)](02-artifacts/devices/usb.md)
- [마운트 기록 (Mount)](02-artifacts/devices/mounts.md)

## 분석 기법

### 조사 절차·증거 확보

- [조사 절차 (Investigation Process)](03-techniques/acquisition/investigation-process.md)
- [라이브 응답 수집 (Live Response)](03-techniques/acquisition/live-response.md)
- [디스크 이미징 (Disk Imaging)](03-techniques/acquisition/disk-imaging.md)
- [메모리 수집 (Memory Acquisition)](03-techniques/acquisition/memory-acquisition.md)
- [클라우드 가상 머신 수집 (Cloud VM)](03-techniques/acquisition/cloud-vm.md)
- [컨테이너 수집 (Container Acquisition)](03-techniques/acquisition/container-acquisition.md)

### 분석

- [타임라인 만들기 (Timeline)](03-techniques/analysis/timeline.md)
- [로그 분석 (Log Analysis)](03-techniques/analysis/log-analysis.md)
- [지운 파일 되살리기 (File Recovery)](03-techniques/analysis/file-recovery.md)
- [메모리 분석 (Volatility 3)](03-techniques/analysis/memory-analysis.md)
- [루트킷 찾기 (Rootkit Detection)](03-techniques/analysis/rootkit-detection.md)
- [알려진 파일 대조와 YARA (Hash·YARA)](03-techniques/analysis/hash-yara.md)

### 보고

- [Linux 포렌식 보고서 (Forensic Report)](03-techniques/reporting/forensic-report.md)

## 조사 시나리오

### 침해

- [SSH 로 들어왔나 (SSH Intrusion)](04-scenarios/intrusion/ssh-intrusion.md)
- [웹 서버가 뚫렸나 (Web Server Compromise)](04-scenarios/intrusion/web-compromise.md)
- [권한을 올렸나 (Privilege Escalation)](04-scenarios/intrusion/privilege-escalation.md)
- [채굴기가 돌았나 (Cryptominer)](04-scenarios/intrusion/cryptominer.md)
- [랜섬웨어가 돌았나 (Ransomware)](04-scenarios/intrusion/ransomware.md)
- [무엇이 계속 살아남게 했나 (Persistence Hunt)](04-scenarios/intrusion/persistence-hunt.md)

### 유출·은폐

- [자료를 밖으로 옮겼나 (Data Exfiltration)](04-scenarios/insider/data-exfiltration.md)
- [흔적을 지웠나 (Log·History Tampering)](04-scenarios/insider/anti-forensics.md)
- [시각을 조작했나 (Time Manipulation)](04-scenarios/insider/time-manipulation.md)

### 사용자

- [누가 그 명령을 실행했나 (User Attribution)](04-scenarios/attribution/user-attribution.md)
