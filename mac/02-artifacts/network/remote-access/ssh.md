---
title: "SSH 접속 기록"
parent: "원격 접속"
grand_parent: "아티팩트 · 네트워크"
nav_order: 1650
---

# SSH 접속 기록 (SSH)

맥은 시스템 설정의 원격 로그인 (Remote Login)을 켜면 SSH 접속을 받고, 받는 쪽 흔적은 `~/.ssh/authorized_keys` 와 `/etc/ssh/` 아래의 설정·호스트 키에, 거는 쪽 흔적은 `~/.ssh/known_hosts` 와 `~/.ssh/config` 에 남습니다.

## 무엇을 기록하나 · 왜 생기나

공유 화면에서 원격 로그인을 켜면 다른 컴퓨터가 SSH와 SFTP로 이 맥에 접속할 수 있고, 접속 형식은 `ssh username@hostname` (예: `ssh steve@10.1.2.3`)입니다 [1]. 원격 로그인에는 원격 사용자에게 전체 디스크 접근 권한을 줄지 정하는 "Allow full disk access for remote users" 토글과, 접속을 "All users" 에게 열지 "Only these users" 로 좁힐지 고르는 설정이 있습니다 [1]. 원격 로그인을 켜면 맥의 보안이 약해질 수 있습니다 [1]. 이 선택들이 어느 파일에 저장되는지는 실제 기기에서 확인해야 합니다. 공유 화면의 위치는 [원격 접속 (Remote Access)](index.md) 허브에 있습니다.

이 페이지의 파일은 접속마다 한 줄씩 쌓이는 로그가 아니라, SSH 서버(sshd)와 클라이언트(ssh)가 인증과 설정에 읽는 파일입니다. 그래서 대부분은 "누가 들어올 수 있게 준비되어 있었나" 와 "이 사용자가 어디에 접속한 적이 있나" 를 보여 주고, 접속 한 건 한 건의 시각은 다른 기록에서 찾아야 합니다.

## 위치

### 받는 쪽(sshd)

| 경로 | 매뉴얼 설명 | 근거 |
|---|---|---|
| `~/.ssh/` | 사용자별 설정과 인증 정보가 기본으로 모이는 곳. 사용자만 읽기·쓰기·실행할 수 있게 두기를 권함 | [2] |
| `~/.ssh/authorized_keys` | 이 사용자로 로그인할 때 쓸 수 있는 공개 키(ECDSA, Ed25519, RSA) 목록. 사용자만 읽고 쓰고 다른 사람은 접근하지 못하게 두기를 권함 | [2] |
| `/etc/ssh/sshd_config` | sshd 설정 | [2] |
| `/etc/ssh/ssh_host_rsa_key`, `/etc/ssh/ssh_host_ecdsa_key`, `/etc/ssh/ssh_host_ed25519_key` | 호스트 개인 키. root 소유이고 root만 읽을 수 있음 | [2] |
| `/etc/nologin` | 이 파일이 있으면 root가 아닌 사용자의 로그인을 거부함 | [2] |
| `~/.ssh/rc`, `/etc/ssh/sshrc` | 로그인할 때 실행되는 초기화 스크립트. `/etc/ssh/sshrc` 는 시스템 전체용 | [2] |

### 거는 쪽(ssh 클라이언트)

| 경로 | 매뉴얼 설명 | 근거 |
|---|---|---|
| `~/.ssh/known_hosts` | 사용자가 로그인한 적이 있는 호스트 가운데 시스템 전체 목록에 없는 호스트의 호스트 키 목록 | [3] |
| `/etc/ssh/ssh_known_hosts` | 관리자가 준비하는 시스템 전체 호스트 키 목록 | [3] |
| `~/.ssh/config` | 사용자별 설정 파일(형식은 ssh_config(5)) | [3] |
| `~/.ssh/id_ecdsa`, `~/.ssh/id_ed25519`, `~/.ssh/id_rsa` 등 | 사용자 개인 키. 사용자만 읽을 수 있어야 함 | [3] |

위 경로는 OpenSSH 매뉴얼 기준입니다. 맥에서 `/etc` 가 실제로 어느 폴더를 가리키는지, `/etc/ssh/sshd_config.d/` 같은 하위 설정 폴더를 쓰는지, macOS 버전마다 OpenSSH 버전이 어떻게 다른지는 실제 기기에서 확인하고 macOS 버전과 함께 적습니다.

## 구조

키 파일 한 줄의 형식과 known_hosts 읽는 법은 [SSH 키와 접속 목록 (SSH Keys·known_hosts)](../../credentials/ssh-keys.md)에서 다루고, 여기서는 접속 흔적을 해석할 때 눈여겨볼 authorized_keys 줄 옵션만 적습니다 [2].

| 옵션 | 동작 | 분석할 때 볼 점 |
|---|---|---|
| `from="pattern-list"` | 이 키의 인증을 지정한 출발지 주소·호스트에서 온 접속으로 제한 | 적힌 주소가 사건에 나온 주소와 맞는지 |
| `command="command"` | 이 키로 인증하면 지정한 명령을 강제로 실행 | 어떤 명령이 걸려 있는지, 그 명령 파일이 어디 있는지 |
| `restrict` | 포트·에이전트·X11 포워딩, PTY 할당, `~/.ssh/rc` 실행을 모두 끔 | 키를 쓸 수 있는 범위를 좁혀 두었는지 |

## 증거로서 의미

### 증명하는 것

authorized_keys에 공개 키 줄이 있으면 그 공개 키와 짝이 되는 개인 키로 이 계정에 로그인할 수 있게 준비되어 있었다고 말할 수 있고, `from=` 이나 `command=` 가 붙어 있으면 어디서 오는 접속을 받게 했는지, 인증 뒤 무엇을 실행하게 했는지까지 알 수 있습니다 [2]. `~/.ssh/rc` 나 `/etc/ssh/sshrc` 가 있으면 로그인할 때마다 실행되는 내용이 있다는 뜻이라서 [2], 안에 적힌 명령을 그대로 기록합니다. `/etc/nologin` 이 있으면 그 파일이 있는 동안에는 root가 아닌 사용자의 로그인을 sshd가 거부하게 되어 있습니다 [2].

매뉴얼은 known_hosts를 사용자가 로그인한 적이 있는 호스트의 키 목록이라고 설명하지만 [3], 클라이언트는 사용자 인증 전에 상대의 호스트 키를 확인하고 저장합니다. 그래서 known_hosts의 줄은 그 호스트에 접속해 호스트 키를 받아들인 적이 있다는 흔적이고, 로그인에 성공했다는 증거로는 쓰지 않습니다. `~/.ssh/config` 에 적힌 호스트 설정은 사용자가 접속하려고 설정해 둔 상대를 보여 줍니다.

### 증명하지 못하는 것

authorized_keys 줄은 로그인할 수 있게 준비되어 있었다는 기록이지, 실제로 로그인했다는 기록이 아닙니다. known_hosts도 언제, 몇 번 접속했는지는 알려 주지 않고, `/etc/ssh/ssh_known_hosts` 의 항목은 관리자가 넣어 둔 것이라서 사용자가 그 호스트에 접속했다는 뜻이 아닙니다 [3]. 인증에 성공했는지 실패했는지, 접속한 뒤 무엇을 했는지도 이 파일들로는 알 수 없습니다.

known_hosts에 호스트 이름을 해시로 저장하게 하는 `HashKnownHosts` 설정이 있고, macOS의 기본값은 실제 기기에서 확인합니다. 해시로 저장된 줄이라면 파일만 보고 상대 호스트 이름을 읽을 수 없어서, 후보 호스트 이름을 넣어 맞춰 보는 방식이 필요합니다.

보고서에는 "외부에서 이 키로 침입했다" 대신 "이 계정의 authorized_keys에 `from=` 조건 없이 공개 키 한 줄이 있고, 파일의 마지막 수정 시각은 D이다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

이 파일들은 줄마다 시각을 적지 않아서, 시각은 파일 시스템의 생성·수정 시각에 기대게 됩니다. 수정 시각은 파일 어딘가가 마지막으로 바뀐 때라서 어느 줄이 그때 더해졌는지는 알려 주지 않고, 줄이 늘어난 시점을 좁히려면 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md)로 예전 사본과 비교하거나 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)에서 파일이 바뀐 시점을 찾아봅니다. 파일 시스템 시각의 기준은 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md)에 있습니다.

ssh 클라이언트는 `-E log_file` 옵션으로 디버그 로그를 표준 오류 대신 파일에 덧붙일 수 있고, `-v` 는 세 번까지 겹쳐 쓸 수 있습니다 [3]. 셸 기록에서 `-E` 뒤에 적힌 로그 파일 경로가 보이면 그 파일도 수집합니다.

## 함정과 한계

sshd가 로그인 성공·실패를 어떤 로그 수준으로 어디에 남기는지, 통합 로그에서 어떤 프로세스 이름과 문구로 찾아야 하는지는 공개된 자료가 없습니다. 널리 알려진 로그 문구를 그대로 검색어로 쓰기 전에 실제 기기에서 문구를 먼저 확인하고, 찾는 방법은 [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md)을 따릅니다. 세션이 로그인 기록 파일(utmpx·lastlog)에 어떻게 남는지도 알려진 자료가 없어서, 그 파일은 [원격 접속 (Remote Access)](index.md) 허브에 적은 범위에서만 씁니다.

`~/.ssh/` 와 authorized_keys 는 사용자만 읽고 쓰고 다른 사람은 접근하지 못하게 두는 것이 권장값이라서 [2], 권한이 이와 다르게 바뀌어 있다면 누가 언제 바꿨는지 따로 확인할 만합니다.

authorized_keys와 known_hosts는 평범한 텍스트 파일이라 줄을 지우거나 파일째 지우기 쉽고, 셸 기록도 지울 수 있습니다. 줄이 없다고 접속하지 않았다고 읽지 말고 예전 사본과 삭제 흔적을 함께 찾으며, 지우기 흔적을 보는 법은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에 있습니다.

## 직접 분석해 보기

텍스트 파일이라 헥스로 볼 부분은 적고, 아래 순서로 사본을 읽습니다.

1. 사용자 홈마다 `~/.ssh/` 폴더를 통째로 복사하고, `/etc/ssh/`, `/etc/nologin`, `/etc/ssh/sshrc` 가 있으면 함께 복사합니다. 폴더와 파일의 권한·소유자도 기록합니다.
2. authorized_keys에서 옵션이 붙은 줄을 찾아 옵션과 키 종류를 표로 정리합니다.

   ```sh
   grep -nE '(^|,)(from=|command=|restrict)' ./copy/Users/USER/.ssh/authorized_keys
   ```

3. known_hosts의 줄 수와 해시로 저장된 줄이 있는지 확인하고, 읽을 수 있는 호스트 이름과 주소를 뽑습니다.
4. `~/.ssh/config` 에서 호스트 설정을 확인합니다.
5. `~/.ssh/rc` 와 `/etc/ssh/sshrc` 가 있으면 내용을 그대로 옮겨 적습니다.
6. 셸 기록에서 `ssh` 명령과 `-E` 로 남긴 로그 파일 경로를 찾아 known_hosts의 상대와 맞춰 봅니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [SSH 키와 접속 목록 (SSH Keys·known_hosts)](../../credentials/ssh-keys.md) | 키 파일과 known_hosts 한 줄의 형식 |
| [원격 접속 (Remote Access)](index.md) | 로그인 기록 파일(utmpx·lastlog) |
| [터미널 명령 기록 (zsh_history·bash_sessions)](../../execution/shell-history.md) | 이 맥에서 친 ssh 명령과 상대 |
| [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md) | 접속 시간대 전후의 sshd 관련 이벤트 |
| [사용자 계정 (Local Accounts)](../../system-account/user-accounts/index.md) | authorized_keys가 있는 계정이 어떤 계정인지 |
| [화면 공유와 원격 관리 (Screen Sharing·ARD)](screen-sharing-ard.md) | 같은 상대와 화면 공유로도 오갔는지 |

여러 기록을 엮어 침입 여부를 판단하는 흐름은 [원격 접속 침입 확인 (Remote Intrusion)](../../../04-scenarios/incident/remote-intrusion.md)에서 다룹니다.

## 실습

macOS 공개 시험 데이터(NIST CFReDS 등)로 아래 질문을 풀어 봅니다.

1. authorized_keys가 있는 계정은 어느 것이고, 옵션이 붙은 줄이 있는가?
2. known_hosts에 해시로 저장된 줄이 있는가, 읽을 수 있는 줄에는 어떤 호스트가 있는가?
3. `~/.ssh/rc`, `/etc/ssh/sshrc`, `/etc/nologin` 가운데 있는 파일은 무엇인가?
4. authorized_keys의 마지막 수정 시각 전후로 셸 기록과 통합 로그에는 무엇이 남아 있는가?

## 참고 문헌

1. Apple Support, macOS 사용 설명서 "Allow a remote computer to access your Mac" — https://support.apple.com/guide/mac-help/allow-a-remote-computer-to-access-your-mac-mchlp1066/mac
2. sshd(8) man page (Xcode man page 모음) — https://keith.github.io/xcode-man-pages/sshd.8.html
3. ssh(1) man page (Xcode man page 모음) — https://keith.github.io/xcode-man-pages/ssh.1.html
