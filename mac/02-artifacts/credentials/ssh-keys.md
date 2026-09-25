---
title: "SSH 키와 접속 목록"
parent: "아티팩트 · 자격 증명·권한"
nav_order: 1850
---

# SSH 키와 접속 목록 (SSH Keys·known_hosts)

사용자 홈의 `~/.ssh/` 폴더에는 이 맥에서 밖으로 접속할 때 쓰는 개인 키와 설정 파일, 접속했던 서버의 호스트 키 목록(known_hosts)이 남고, 이 계정으로 들어올 수 있는 공개 키 목록(authorized_keys)도 같은 폴더에 있어서, 파일 몇 개로 이 계정이 어느 상대와 SSH로 이어져 있었는지를 읽을 수 있습니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

SSH 클라이언트(ssh)는 접속할 때 사용자 설정 파일과 시스템 설정 파일을 읽고, 처음 보는 서버의 호스트 키를 사용자 호스트 키 목록에 더합니다. 더하기 전에 사용자에게 물을지는 `StrictHostKeyChecking` 설정이 정하고, 기본값 `ask` 에서는 물어본 뒤에 더합니다 [1]. `~/.ssh/known_hosts` 에는 사용자가 로그인한 적 있는 호스트 가운데 시스템 목록에 없는 호스트의 호스트 키가 모입니다 [2]. 개인 키 파일은 사용자가 키를 만들거나 다른 곳에서 복사해 둘 때 생기고, ssh는 설정에서 따로 지정하지 않으면 정해진 이름의 키 파일을 찾아 씁니다 [1].

Apple이 넣은 OpenSSH에는 키의 암호문구(passphrase)를 키체인에 저장하는 기능이 덧붙어 있어서, 암호문구의 흔적이 `~/.ssh/` 밖의 키체인에 남을 수 있습니다 [1][3][4].

이 맥으로 들어오는 접속 쪽(sshd 설정, 호스트 개인 키, authorized_keys 옵션의 뜻)과 로그인 흔적의 해석은 [SSH 접속 기록 (SSH)](../network/remote-access/ssh.md)에서 다루고, 이 페이지는 키 파일과 설정, 그리고 known_hosts·authorized_keys 한 줄을 읽는 법을 다룹니다.

## 위치와 버전별 차이

| 구분 | 경로 | 내용 | 출처 |
|---|---|---|---|
| 사용자 설정 | `~/.ssh/config` | 호스트별 접속 설정. 사용자만 읽고 쓸 수 있고 다른 사람은 쓸 수 없어야 함 | [1] |
| 시스템 설정 | `/etc/ssh/ssh_config` | 모든 사용자에게 걸리는 기본 설정. 누구나 읽을 수 있어야 함 | [1] |
| 사용자 호스트 키 목록 | `~/.ssh/known_hosts`, `~/.ssh/known_hosts2` | `UserKnownHostsFile` 의 기본값 | [1][2] |
| 시스템 호스트 키 목록 | `/etc/ssh/ssh_known_hosts`, `/etc/ssh/ssh_known_hosts2` | `GlobalKnownHostsFile` 의 기본값. 관리자가 조직 안 모든 호스트의 공개 키를 넣어 두는 파일 | [1][2] |
| 개인 키 | `~/.ssh/id_rsa`, `~/.ssh/id_ecdsa`, `~/.ssh/id_ecdsa_sk`, `~/.ssh/id_ed25519`, `~/.ssh/id_ed25519_sk`, `~/.ssh/id_mldsa44_ed25519` | `IdentityFile` 의 기본값. ssh-add를 인자 없이 실행해도 이 6개 파일을 에이전트에 넣으려 함 | [1][3] |
| 들어오는 쪽 공개 키 | `~/.ssh/authorized_keys` | 이 사용자로 로그인할 때 쓸 수 있는 공개 키(ECDSA, Ed25519, RSA) 목록 | [2] |

이름이 `_sk` 로 끝나는 키는 보안 키(FIDO 인증 장치)에 기반한 ECDSA·Ed25519 키입니다 [1]. 위 기본값은 기본 키 파일 목록에 `id_mldsa44_ed25519` 가 들어 있는 최근 OpenSSH 기준으로 보입니다. 오래된 macOS에서는 기본값이 이 표와 다를 수 있어서 검체의 OpenSSH 판에 맞춰 다시 확인합니다.

macOS 판에 따라 키체인과 ssh-agent 동작이 아래처럼 바뀌었습니다.

| macOS | 바뀐 점 | 출처 |
|---|---|---|
| 10.12 Sierra | 암호문구를 키체인에 저장할지 묻던 창이 없어지고 `UseKeychain` 옵션이 새로 생겼으며, 이 판에서는 기본으로 켜져 있어 모든 암호문구가 키체인에 저장됨 | [4] |
| 10.12.2 | OpenSSH 7.3p1. 의도한 기본값이 아니었던 `UseKeychain` 이 꺼지고, 저장하려면 `UseKeychain yes` 를 직접 써야 함. 키를 ssh-agent에 저절로 넣지 않게 바뀌었고(upstream과 같은 동작), 다시 켜려면 `AddKeysToAgent yes` | [4] |
| 그 뒤 판 | ssh-add의 키체인 옵션이 `--apple-use-keychain`·`--apple-load-keychain` 이라는 이름으로 있고, `-K` 는 FIDO 인증 장치의 상주 키(resident key)를 불러오는 옵션으로 뜻이 달라짐 | [3] |

두 키체인 옵션이 처음 나온 macOS 판과 10.15 Catalina 이후 판마다 들어 있는 OpenSSH 판은 공개 자료가 없어 검체에서 확인합니다.

## 구조

### known_hosts 한 줄

known_hosts는 한 줄에 호스트 키 하나를 적는 텍스트 파일이고, 칸은 공백으로 나뉩니다 [2].

| 순서 | 칸 | 내용 |
|---|---|---|
| 1 | 표시 (marker) | 없어도 됨. `@cert-authority` 는 인증 기관 키, `@revoked` 는 취소된 키라서 받아들이면 안 되는 키 |
| 2 | 호스트 이름들 | 쉼표로 나눈 패턴 목록. `*`·`?` 와일드카드를 쓰고, 앞에 `!` 를 붙이면 부정(맞으면 거부) |
| 3 | 키 종류 | 예: `ssh-ed25519`, `ssh-rsa` |
| 4 | 키 | base64로 적은 공개 키 |
| 5 | 주석 | 없어도 됨 |

표준이 아닌 포트로 접속한 서버는 호스트 이름 칸에 `[호스트]:포트` 처럼 대괄호로 감싼 뒤 콜론과 포트를 붙여 적습니다 [2]. 호스트 이름을 해시로 저장한 줄은 이름과 주소를 숨기고 `|` 문자로 시작하고, 한 줄에 해시된 이름은 하나만 올 수 있으며 와일드카드와 부정(`!`)을 쓸 수 없습니다 [2].

### known_hosts가 채워지는 방식을 정하는 설정

known_hosts에 어떤 줄이 어떻게 생기는지는 클라이언트 설정에 따라 달라서, 줄을 해석하기 전에 설정 파일부터 읽습니다 [1].

| 설정 | 기본값 | 동작 | 해석할 때 볼 점 |
|---|---|---|---|
| `HashKnownHosts` | `no` | known_hosts에 넣을 때 호스트 이름·주소를 해시할지 정함. 이미 있는 줄은 저절로 바뀌지 않고 ssh-keygen으로 손수 해시할 수 있음 | 해시된 줄과 평문 줄이 섞여 있으면 설정을 도중에 바꿨거나 손수 해시했을 수 있음 |
| `StrictHostKeyChecking` | `ask` | `ask` 는 더하기 전에 물음, `yes` 는 자동으로 더하지 않음, `accept-new` 는 새 키를 자동으로 더하고 바뀐 키는 거부, `no` 는 바뀐 키도 허용 | `accept-new`·`no` 면 사용자가 확인하지 않아도 줄이 생길 수 있음 |
| `UpdateHostKeys` | `yes` (`UserKnownHostsFile` 을 바꾸지 않았고 `VerifyHostKeyDNS` 를 켜지 않았을 때) | 인증 뒤 서버가 알려 주는 다른 호스트 키도 받아 넣음 | 한 호스트에 키 종류별 줄이 한꺼번에 여럿 생길 수 있음 |
| `CheckHostIP` | `no` | `yes` 면 known_hosts에서 호스트 IP 주소도 확인 | 기본값에서는 IP 주소 줄이 따로 생기지 않을 수 있음 |

macOS의 `/etc/ssh/ssh_config` 가 이 값들을 기본값과 다르게 켜 두었을 수 있어서, 검체의 시스템 설정 파일을 직접 읽어 봅니다.

### config 파일

`Host` 와 `Match` 는 뒤따르는 설정을 맞는 호스트나 조건에만 적용하고, `Host *` 는 모든 호스트에 걸리는 기본값입니다 [1]. `Include` 는 다른 설정 파일을 불러오고 glob 와일드카드와 환경 변수를 쓸 수 있어서 [1], config를 볼 때는 불러온 파일까지 모두 모아 읽습니다.

키체인과 에이전트에 관한 설정은 두 가지입니다. `UseKeychain` 은 macOS에서 키를 쓸 때 사용자 키체인에서 암호문구를 찾을지를 정하고, 기본값은 `no` 이며 `PKCS11Provider` 와 함께 쓸 수 없습니다 [1]. `AddKeysToAgent` 는 `yes`, `ask`, `confirm`, `no` 가운데 하나나 시간 간격을 값으로 받고 기본값은 `no` 입니다 [1]. 호스트 하나에 키 파일과 키체인 사용을 지정하면 아래 블록처럼 되고, 호환을 위해 `IgnoreUnknown UseKeychain` 을 먼저 적은 뒤 `UseKeychain yes` 를 쓰기도 합니다 [4].
```
Host server.example.com
    IdentityFile ~/.ssh/id_rsa
    UseKeychain yes
```

### authorized_keys 한 줄

authorized_keys는 한 줄에 공개 키 하나를 적고, 칸은 옵션, 키 종류, base64 키, 주석 순서로 공백으로 나뉩니다 [2]. 받아들이는 키 종류는 아래와 같습니다 [2].

```
sk-ecdsa-sha2-nistp256@openssh.com
ecdsa-sha2-nistp256   ecdsa-sha2-nistp384   ecdsa-sha2-nistp521
sk-ssh-ed25519@openssh.com
ssh-ed25519
ssh-mldsa44-ed25519@openssh.com
ssh-rsa
```

옵션 칸에는 `from=`, `command=`, `environment=`, `expiry-time=`, `no-port-forwarding`, `permitopen=`, `no-pty`, `restrict`, `cert-authority`, `principals=`, `agent-forwarding`, `port-forwarding`, `pty`, `user-rc`, `X11-forwarding`, `tunnel=`, `permitlisten=`, `no-agent-forwarding`, `no-X11-forwarding`, `no-user-rc`, `no-touch-required`, `verify-required` 가 올 수 있습니다 [2]. 침입을 판단할 때 눈여겨볼 `from=`·`command=`·`restrict` 의 뜻은 [SSH 접속 기록 (SSH)](../network/remote-access/ssh.md)에 있습니다. 주석만 보고 키를 만든 사람이나 기기를 단정하지 않습니다.

### ssh-agent와 키체인

ssh-add는 에이전트에 키를 넣고 빼는 명령이고, Apple 판에는 키체인과 이어지는 옵션이 있습니다 [3]. `--apple-use-keychain` 은 키를 넣을 때 암호문구를 사용자 키체인에도 저장하고, 이 옵션과 `-d` 로 키를 뺄 때는 키체인에서도 지웁니다. `--apple-load-keychain` 은 키체인에 저장된 암호문구로 키를 에이전트에 넣습니다. 환경 변수 `APPLE_SSH_ADD_BEHAVIOR` 는 `-A`·`-K` 의 예전 macOS 동작을 정하는데, `openssh` 면 표준 OpenSSH 동작을 따르고 `macos` 면 폐기 경고를 숨깁니다 [3].

에이전트와는 `SSH_AUTH_SOCK` 에 적힌 UNIX 도메인 소켓 경로로 통하고, `-l` 은 에이전트에 든 키의 지문 목록을, `-L` 은 공개 키 목록을 보여 줍니다 [3]. `-D` 는 모두 지우고, `-t` 는 에이전트에 넣는 키의 최대 수명을 정하고, `-c` 는 키를 쓸 때마다 확인을 받게 합니다 [3].

키체인에 저장된 SSH 암호문구가 어떤 종류의 항목으로, 어떤 서비스·계정 이름으로 남는지, 파일 기반 login 키체인과 데이터 보호 키체인 가운데 어디에 들어가는지는 공개 자료가 없어 검체에서 확인합니다. 두 키체인의 구조는 [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md)에 있습니다.

## 증거로서 의미

### 증명하는 것

개인 키 파일이 있으면 그 계정에 그 키로 SSH 인증을 할 수단이 수집 시점에 있었다고 말할 수 있고, config의 `Host` 블록과 `IdentityFile` 을 맞춰 보면 사용자가 어느 상대에 어느 키를 쓰도록 설정해 두었는지까지 알 수 있습니다 [1]. 이름이 `_sk` 로 끝나는 키는 보안 키 장치에 기반한 키라서 [1], 그런 장치를 이 맥에 연결한 흔적을 함께 찾아볼 단서가 됩니다.

known_hosts의 평문 줄에서는 상대 호스트 이름이나 주소, 표준이 아닌 포트, 키 종류를 읽을 수 있습니다 [2]. `@revoked` 가 붙은 줄은 그 키를 받아들이지 않도록 표시해 둔 것이고, `@cert-authority` 가 붙은 줄은 그 키를 인증 기관 키로 표시해 둔 것이라서 [2], 표시가 붙은 줄이 있으면 누가 어떤 경위로 넣었는지를 따로 확인합니다.

config나 시스템 설정에 `UseKeychain yes` 가 있거나 셸 기록에 `--apple-use-keychain` 이 보이면, 암호문구를 키체인에 저장하도록 한 기록이라서 키체인에서 해당 항목을 찾아볼 근거가 됩니다 [1][3]. 10.12 Sierra에서는 설정이 없어도 암호문구가 모두 키체인에 저장됐고 [4], 그 시기부터 쓰던 키라면 설정 줄이 없어도 키체인 항목이 남아 있을 수 있습니다.

### 증명하지 못하는 것

known_hosts 줄 형식에는 시각 칸도 횟수 칸도 없어서 [2], 줄 하나로는 언제, 몇 번 접속했는지, 인증에 성공했는지를 알 수 없습니다. `StrictHostKeyChecking` 이 `accept-new`·`no` 면 사용자 확인 없이 줄이 생길 수 있고, `UpdateHostKeys` 가 켜져 있으면 접속 한 번에 줄이 여럿 생길 수 있어서 [1], 줄 수를 접속 수로 읽지 않습니다. `/etc/ssh/ssh_known_hosts` 의 항목은 관리자가 넣어 두는 목록이라 [2] 사용자가 그 호스트에 접속했다는 뜻이 아닙니다.

개인 키 파일이 있어도 실제로 쓴 적이 있는지, 그 공개 키가 어느 서버의 authorized_keys에 등록되어 있는지는 이 맥의 파일만으로는 알 수 없습니다. 해시된 known_hosts 줄은 호스트 이름을 알고 있어야 맞춰 볼 수 있어서, 후보가 없으면 상대가 누구인지 읽지 못합니다.

보고서에는 "이 사용자가 서버 X에 침입했다" 대신 "이 계정의 known_hosts에 `[X]:2222` 로 시작하는 ed25519 호스트 키 줄이 있고, config의 `Host X` 블록이 `~/.ssh/id_ed25519` 를 지정한다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

이 페이지의 파일들은 줄마다 시각을 적지 않아서, 시각은 파일 시스템의 생성·수정 시각에 기대게 됩니다. 수정 시각이 어느 줄의 변화인지 알려 주지 않는다는 점과 줄이 늘어난 시점을 좁히는 방법은 [SSH 접속 기록 (SSH)](../network/remote-access/ssh.md)의 시각 해석에 있고, 파일 시각이 무엇을 뜻하는지는 [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md)에 있습니다.

개인 키 파일의 생성 시각을 키를 만든 시각으로 곧바로 읽지 않습니다. 키 파일은 다른 기기에서 복사하거나 백업에서 되살릴 수도 있어서, 파일 시각은 "이 맥의 이 경로에 파일이 생긴 시각" 으로만 적고 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)와 셸 기록으로 그 전후를 맞춰 봅니다.

## 함정과 한계

OpenSSH 기본값은 판마다 달라질 수 있고, 이 페이지의 기본값은 최근 OpenSSH 기준으로 보입니다. 그래서 기본값을 근거로 판단하기 전에 검체의 `/etc/ssh/ssh_config` 와 `~/.ssh/config`, 그리고 `Include` 로 불러온 파일을 모두 읽고 실제로 적힌 값을 먼저 봅니다 [1].

셸 기록에서 `ssh-add -K` 를 보면 판에 따라 뜻이 다르다는 점에 주의합니다. 최근 판에서는 FIDO 장치의 상주 키를 불러오는 옵션이지만 예전 macOS의 `-K` 와는 뜻이 달라서 [3], 명령을 친 시점의 macOS 판을 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../system-account/os-version-install-history.md)에서 확인한 뒤에 해석합니다.

ssh 클라이언트 접속이 통합 로그에 남는지, 남는다면 어떤 서브시스템 이름으로 남는지는 공개 자료가 없어 검체에서 확인합니다. known_hosts·authorized_keys·config는 평범한 텍스트 파일이라 줄을 지우거나 파일째 지우기 쉬워서, 줄이 없다고 접속하지 않았다고 읽지 않고 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)의 방법으로 예전 사본과 삭제 흔적을 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 known_hosts 형식 설명 [2]에 맞춰 만든 예시이고, 실제 검체에서 나온 값이 아닙니다. 키 칸은 `AAAA` 로 줄였고, 셋째 줄은 첫 글자만 넣었습니다.

```
00000000: 5b68 6f73 742e 6578 616d 706c 655d 3a32  [host.example]:2
00000010: 3232 3220 7373 682d 6564 3235 3531 3920  222 ssh-ed25519
00000020: 4141 4141 0a40 7265 766f 6b65 6420 2a20  AAAA.@revoked *
00000030: 7373 682d 7273 6120 4141 4141 0a7c       ssh-rsa AAAA.|
```

1. 첫 바이트 `0x5B`(`[`)로 시작해 `0x5D 0x3A`(`]:`) 뒤에 `2222` 가 오면, 표준이 아닌 포트 2222로 접속한 호스트의 줄입니다.
2. `0x20`(공백) 다음 칸이 키 종류 `ssh-ed25519`, 그다음 칸이 base64 키이고, `0x0A` 에서 줄이 끝납니다.
3. 둘째 줄은 `0x40`(`@`)으로 시작하는 표시 칸 `@revoked` 가 먼저 오고, 호스트 이름 칸이 `*` 이라서 모든 호스트에 대해 이 키를 거부하라는 줄입니다.
4. 셋째 줄 첫 바이트가 `0x7C`(`|`)이면 호스트 이름을 해시로 저장한 줄이라 이름을 바로 읽을 수 없습니다.

### 명령으로 한 번

원본이 아니라 사본을 열고, `USER` 는 조사하는 계정 이름으로 바꿉니다.

```sh
# 폴더의 파일과 권한, 시각을 먼저 기록
ls -la ./copy/Users/USER/.ssh/

# known_hosts: 표시가 붙은 줄, 해시된 줄, 표준이 아닌 포트 줄
grep -nE '^@' ./copy/Users/USER/.ssh/known_hosts
grep -c '^|' ./copy/Users/USER/.ssh/known_hosts
grep -n '^\[' ./copy/Users/USER/.ssh/known_hosts

# config와 시스템 설정: 해석에 영향을 주는 설정 줄
grep -niE '^\s*(Host|Match|Include|IdentityFile|UseKeychain|AddKeysToAgent|StrictHostKeyChecking|HashKnownHosts|UpdateHostKeys|CheckHostIP)\b' \
  ./copy/Users/USER/.ssh/config ./copy/etc/ssh/ssh_config
```

살아 있는 맥에서는 `ssh-add -l` 과 `ssh-add -L` 로 지금 에이전트에 든 키를 볼 수 있습니다 [3]. 명령을 실행하는 것도 시스템을 건드리는 일이라서, 실행 순서와 기록 방법은 [라이브 대응 (Live Response)](../../03-techniques/process-acquisition/live-response/index.md)을 따릅니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [SSH 접속 기록 (SSH)](../network/remote-access/ssh.md) | authorized_keys 옵션의 뜻, 들어온 접속의 흔적 |
| [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md) | `UseKeychain` 으로 저장된 암호문구가 들어갔을 키체인의 구조 |
| [터미널 명령 기록 (zsh_history·bash_sessions)](../execution/shell-history.md) | ssh·scp·ssh-add·ssh-keygen 명령과 상대, 옵션 |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | `~/.ssh/` 안 파일이 생기거나 바뀐 시점 |
| [USB 저장 장치 (USB Storage)](../external-devices/usb/index.md) | `_sk` 키가 있을 때 장치를 연결한 흔적 |
| [사용자 계정 (Local Accounts)](../system-account/user-accounts/index.md) | `~/.ssh/` 가 있는 홈이 어느 계정인지 |

여러 기록을 엮어 침입 여부를 판단하는 흐름은 [원격 접속 침입 확인 (Remote Intrusion)](../../04-scenarios/incident/remote-intrusion.md)에서 다룹니다.

## 실습

macOS 공개 검체(NIST CFReDS 등)에서 아래 질문을 풀어 봅니다.

1. 어느 계정의 홈에 `~/.ssh/` 가 있고, 그 안에 개인 키 파일은 몇 개이며 이름이 `_sk` 로 끝나는 키가 있는가?
2. known_hosts에 해시된 줄과 평문 줄이 섞여 있는가, 평문 줄의 호스트 가운데 표준이 아닌 포트로 적힌 것이 있는가?
3. config와 `/etc/ssh/ssh_config` 에서 `StrictHostKeyChecking`·`HashKnownHosts`·`UseKeychain` 은 어떤 값인가, `Include` 로 불러온 파일이 있는가?
4. 셸 기록에 ssh-add를 실행한 줄이 있다면 어떤 옵션을 썼고, 그때 macOS 판에서 그 옵션은 무슨 뜻인가?

## 참고 문헌

1. ssh_config(5) man page (Xcode man page 모음) — https://keith.github.io/xcode-man-pages/ssh_config.5.html
2. sshd(8) man page (Xcode man page 모음) — https://keith.github.io/xcode-man-pages/sshd.8.html
3. ssh-add(1) man page (Xcode man page 모음) — https://keith.github.io/xcode-man-pages/ssh-add.1.html
4. Apple, Technical Note TN2449 "OpenSSH updates in macOS 10.12.2" (2016-12-20) — https://developer.apple.com/library/archive/technotes/tn2449/_index.html
