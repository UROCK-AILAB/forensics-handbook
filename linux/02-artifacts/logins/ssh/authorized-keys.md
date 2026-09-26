---
title: "authorized_keys"
parent: "SSH"
grand_parent: "아티팩트 · 로그인과 계정"
nav_order: 370
---

# authorized_keys (authorized_keys)

`~/.ssh/authorized_keys` 는 그 계정에 공개 키 인증으로 들어올 수 있는 키를 한 줄에 하나씩 적은 파일이라서, 수집 시점에 "누가 이 계정의 문을 열 수 있게 돼 있었나" 를 보여 줍니다.

## 무엇을 기록하나 · 왜 생기나

공개 키 인증 (public key authentication) 에서 sshd 는 이 파일에 적힌 공개 키로만 그 계정에 로그인하게 해 줍니다[1]. 사용자가 자기 공개 키(`id_ed25519.pub` 같은 파일)를 서버의 이 파일에 붙여 넣으면 줄이 하나 늘어납니다[1]. 암호를 몰라도 키만 있으면 들어올 수 있으므로, 침입 사건에서는 누군가 다시 들어올 길로 이 파일에 키를 더했는지 살펴봅니다. 지속성 흔적을 모아 보는 흐름은 [무엇이 계속 살아남게 했나](../../../04-scenarios/intrusion/persistence-hunt.md)에서 다룹니다.

파일 줄마다 키를 쓸 조건(옵션)을 붙일 수 있어서, 어떤 키로 들어오면 정해진 명령만 돌게 하거나 특정 주소에서만 받게 할 수 있습니다[1]. 그래서 키가 있는지만 보지 않고 줄 앞의 옵션까지 읽어야 합니다.

## 위치와 버전별 차이

sshd 가 읽는 파일은 `AuthorizedKeysFile` 설정이 정합니다. 설정이 없을 때 기본값은 `.ssh/authorized_keys .ssh/authorized_keys2` 이고, 절대 경로가 아니면 사용자 홈 기준으로 풉니다[2]. 값에는 와일드카드와 토큰 `%%`, `%h`(홈), `%U`(숫자 UID), `%u`(사용자 이름)를 쓸 수 있고, `none` 이면 파일을 아예 보지 않습니다[2]. 이 파일은 실제로 있는 계정(유효 사용자)에게만 확인합니다[2]. root 도 같은 규칙이라 기본 위치는 `/root/.ssh/authorized_keys` 입니다.

기본값과 배포판이 싣는 설정 파일이 서로 다릅니다. OpenSSH 가 함께 싣는 `sshd_config` 는 `AuthorizedKeysFile	.ssh/authorized_keys` 로 기본값을 덮어써서 `authorized_keys2` 를 보지 않게 합니다[3]. Ubuntu 는 이 줄을 주석으로 바꿔 두었기 때문에 기본값이 살아나 `authorized_keys2` 도 읽습니다[4]. RHEL 9 의 패치는 이 줄을 건드리지 않습니다[5].

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| OpenSSH 판 | 9.6p1[4] | 9.9p1(CentOS Stream 9 기준, 초기 판은 8.7p1)[5] |
| `/etc/ssh/sshd_config` 의 설정 줄 | `#AuthorizedKeysFile	.ssh/authorized_keys .ssh/authorized_keys2` (주석)[4] | `AuthorizedKeysFile	.ssh/authorized_keys`[3][5] |
| 실제로 읽는 파일 | `~/.ssh/authorized_keys`, `~/.ssh/authorized_keys2` | `~/.ssh/authorized_keys` |
| 덧붙는 설정 폴더 | `/etc/ssh/sshd_config.d/*.conf`[4] | `/etc/ssh/sshd_config.d/*.conf`[5] |

위 표는 설치 직후의 모습입니다. `AuthorizedKeysFile` 은 `sshd_config.d` 의 파일에서도, `Match` 블록 안에서도 바꿀 수 있어서 사용자나 그룹마다 다른 경로를 쓰게 할 수 있습니다[2]. 검체에서는 먼저 설정 파일 전체에서 이 키워드를 찾습니다. 설정 파일을 읽는 순서와 `Match` 규칙은 [sshd 설정](sshd-config.md)에서 다룹니다.

파일 말고도 키를 받는 길이 있습니다. `AuthorizedKeysCommand` 에 지정한 프로그램은 파일을 본 다음에 돌고, 파일에서 맞는 키를 찾으면 돌지 않습니다[2]. 이 프로그램은 절대 경로여야 하고 root 소유에 그룹·기타 사용자가 쓸 수 없어야 합니다[2]. `TrustedUserCAKeys` 로 믿는 인증 기관 (CA) 이 서명한 인증서로도 들어올 수 있습니다[2]. 그래서 authorized_keys 에 키가 없다고 해서 공개 키로 들어올 수 없었다고 말할 수는 없습니다.

## 구조

authorized_keys 는 텍스트 파일입니다. 한 줄에 키 하나를 적고, 빈 줄과 `#` 으로 시작하는 줄은 주석으로 보고 건너뜁니다[1]. 한 줄은 공백으로 나뉜 네 필드로 이뤄집니다[1].

| 필드 | 필수 | 내용 |
|---|---|---|
| options | 아니오 | 쉼표로 나눈 옵션. 공백은 큰따옴표 안에서만 쓸 수 있고, 옵션 이름은 대소문자를 가리지 않는다[1] |
| keytype | 예 | `ssh-ed25519`, `ssh-rsa`, `ecdsa-sha2-nistp256`, `sk-ssh-ed25519@openssh.com` 등[1] |
| base64 키 | 예 | 공개 키 blob 을 base64 로 적은 값 |
| comment | 아니오 | 자유 문자열. sshd 는 이 값을 어디에도 쓰지 않는다[1] |

한 줄은 최대 8 KB 까지 됩니다[1]. 쓸 수 있는 keytype 목록은 OpenSSH 판마다 다르고, master 의 man 페이지에는 `ssh-mldsa44-ed25519` 도 있습니다[1].

base64 키를 풀면 4바이트 빅엔디언 길이와 문자열이 이어지는 모양이 나옵니다. 첫 문자열은 키 형식 이름이고, 그 뒤는 형식마다 다릅니다. Ed25519 는 32바이트 공개 키 하나가 같은 방식으로 붙습니다[9].

흔적을 해석할 때 눈여겨볼 옵션은 아래와 같습니다[1].

| 옵션 | 뜻 | 해석할 때 |
|---|---|---|
| `command="…"` | 이 키로 들어오면 늘 이 명령을 돌린다 | 클라이언트가 보낸 원래 명령은 `SSH_ORIGINAL_COMMAND` 환경 변수로 넘어간다. 원격 백업만 하게 하는 키 같은 정상 용도도 있다 |
| `from="pattern-list"` | 원격 호스트 이름이나 IP 가 목록에 맞아야 받는다. CIDR 도 쓸 수 있다 | 키를 쓸 수 있었던 출발지 범위 |
| `environment="NAME=value"` | 로그인할 때 환경 변수를 더한다 | `PermitUserEnvironment` 가 켜져 있어야 적용된다(기본 `no`)[2] |
| `expiry-time="timespec"` | 이 시각 뒤로는 키를 받지 않는다 | `YYYYMMDD[Z]` 또는 `YYYYMMDDHHMM[SS][Z]`. `Z` 가 붙으면 UTC, 없으면 시스템 시간대 |
| `cert-authority` | 이 줄의 키를 CA 로 믿는다 | 이 CA 가 서명한 인증서는 줄에 없어도 들어올 수 있다. `principals=` 로 받을 이름을 좁힌다 |
| `restrict` | 포워딩·pty·`~/.ssh/rc` 실행을 모두 막는다 | 뒤에 `pty`, `port-forwarding` 등을 붙이면 하나씩 다시 푼다 |
| `no-port-forwarding`, `permitopen=`, `permitlisten=`, `tunnel=` | 포트 포워딩·터널을 막거나 좁힌다 | 옆 기계로 옮겨 가는 통로로 쓸 수 있었는지 가늠한다 |
| `no-user-rc`, `user-rc` | `~/.ssh/rc` 실행을 막거나 푼다 | `~/.ssh/rc` 가 있으면 함께 본다 |

## 증거로서 의미

**증명하는 것**

- 수집 시점에 이 줄의 개인 키를 가진 사람은 이 계정으로 공개 키 인증을 할 수 있는 설정이었습니다. 단, `AuthorizedKeysFile` 이 이 파일을 가리키고 공개 키 인증이 켜져 있을 때에 한합니다.
- 줄 앞의 옵션은 그 키로 들어올 때의 조건(강제 명령, 출발지, 만료 시각, 포워딩 허용)을 보여 줍니다[1].
- 키 blob 의 지문은 로그의 지문과 맞출 수 있어서, 이 줄의 키로 실제 로그인한 때를 찾는 열쇠가 됩니다.

**증명하지 못하는 것**

- 키가 실제로 쓰였는지는 알 수 없습니다. 로그와 맞춰 봐야 합니다.
- 누가, 언제 줄을 넣었는지는 파일에 없습니다. 파일에는 시각 필드가 없고, 파일 시스템 시각은 마지막 변경만 알려 줍니다.
- comment 의 `user@host` 는 키를 만든 사람이 적은 자유 문자열이라 참이라는 보장이 없습니다[1].
- 개인 키를 누가 가졌는지는 이 파일로 알 수 없습니다. 같은 키가 여러 기계·사람에게 있을 수 있습니다.

보고서에는 "수집 시점에 alice 계정의 authorized_keys 3번째 줄에 지문이 SHA256:… 인 ED25519 키가 있다" 처럼 기록이 보여 주는 만큼만 씁니다.

## 시각 해석

파일 안에는 시각이 없습니다. 키를 넣은 때를 가늠하려면 파일과 `~/.ssh` 폴더의 파일 시스템 시각을 봅니다. 공개 도구도 이 파일을 읽을 때 수정 시각(mtime)과 변경 시각(ctime)을 함께 뽑습니다[11].

| 기록 | 바뀌는 때 | 해석 |
|---|---|---|
| 파일 mtime | 내용을 고쳐 쓸 때 | 마지막으로 줄을 더하거나 지운 때. 맨 처음 키를 넣은 때가 아니다 |
| 파일 ctime | 내용·권한·소유자가 바뀔 때 | `chmod`·`chown` 으로도 바뀐다 |
| 파일 생성 시각(ext4 crtime) | 파일을 새로 만들 때 | 편집기가 새 파일을 만들어 바꿔 쓰는 방식이면 고칠 때마다 새로 정해질 가능성이 있다 |
| `~/.ssh` 폴더 mtime | 폴더 안 파일을 만들거나 지울 때 | 파일을 새로 만든 때와 견준다 |
| `expiry-time` 옵션 | 사람이 적은 값 | `Z` 가 없으면 서버의 시스템 시간대로 읽는다[1] |

파일 시스템 시각을 읽는 법은 [ext4 의 시각](../../../01-foundations/filesystem/ext4/timestamps.md)과 [Linux 의 시각 값](../../../01-foundations/value-decoding/time-values.md)에서 다룹니다. 키를 처음 쓴 때는 이 파일이 아니라 로그의 `Accepted publickey` 줄에서 지문으로 찾습니다([sshd 로그](sshd-logs.md)).

## 함정과 한계

아래 공개 수집·분석 도구는 모두 정해진 경로만 보고 `AuthorizedKeysFile` 을 다른 경로로 바꾼 설정은 따라가지 않으므로, 설정 값을 먼저 확인하고 그 경로를 따로 모읍니다.

| 도구 | 보는 경로 | 주의할 점 |
|---|---|---|
| Velociraptor `Linux.Ssh.AuthorizedKeys` | `/home/*/.ssh/authorized_keys*`[11] | `/root` 가 빠진다. keytype 정규식 기본값(8종)에 없는 형식의 줄은 결과에서 빠진다 |
| dissect.target `openssh.authorized_keys` | 각 사용자 홈의 `.ssh/*authorized_keys*`[12] | keytype 이 `sk-`, `ssh-`, `ecdsa-` 로 시작하지 않는 줄은 경고만 남기고 건너뛴다 |
| UAC | `%user_home%/.ssh/authorized_keys*`[13] | 파일만 모은다 |
| ForensicArtifacts `SSHAuthorizedKeysFiles` | `%%users.homedir%%/.ssh/authorized_keys`, `authorized_keys2`[14] | 파일만 모은다 |

지문 표기가 도구마다 다릅니다. sshd 로그와 `ssh-keygen -l` 은 `SHA256:` 뒤에 base64 를 쓰고 끝의 `=` 를 떼지만[9], dissect.target 은 기본으로 SHA-1·SHA-256 을 16진 문자열로, MD5 도 16진 문자열로 내놓습니다[12]. 16진 값을 바이트로 되돌려 base64 로 적고 끝의 `=` 를 떼면 로그와 맞습니다.

파일이 있어도 sshd 가 쓰지 않았을 수 있습니다. `StrictModes` 가 기본값 `yes` 이면 파일이나 `~/.ssh`, 홈 폴더를 다른 사용자가 쓸 수 있을 때 sshd 는 이 파일을 쓰지 않습니다[1][2]. 이때 `Authentication refused: bad ownership or modes for file …` 이나 `… for directory …` 줄이 남습니다[6][7]. 파일이 일반 파일이 아니면 `User 'alice' authorized keys '…' is not a regular file` 모양의 줄이 남습니다(서식 `User '%s' %s '%s' is not a regular file`)[6]. 권한은 [권한·확장 속성·ACL](../../../01-foundations/filesystem/permissions-xattr.md)에서 읽는 법을 다룹니다.

로그에 남는 정도가 조건마다 다릅니다. 맞는 키를 찾은 파일과 줄 번호를 알려 주는 `Accepted key … found at 파일:줄` 은 `LogLevel VERBOSE` 에서만 남습니다[6]. `from=` 조건에 맞지 않아 거절하면 `파일:줄: Authentication tried for 이름 with correct key but not from a permitted host (…)` 줄이 기본 등급에서도 남지만, `expiry-time` 이 지나 거절한 것은 디버그 등급에만 남습니다[6]. 로그 등급과 줄 전체는 [sshd 로그](sshd-logs.md)에서 다룹니다.

`cert-authority` 줄로 들어온 로그인은 로그에 인증서 안 사용자 키의 지문이 찍히고[8][9], 이 키는 authorized_keys 의 어느 줄에도 없어서 바로 맞지 않습니다. 인증서로 들어온 줄 끝에는 `ID 키ID (serial N) CA 형식 CA지문` 이 붙으므로[8], CA 지문을 이 줄의 키 지문과 맞춥니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 만든 예시 줄입니다. 키 값은 OpenSSH 의 키 직렬화 방식[9]대로 지어낸 32바이트(`01`~`20`)로 만들었고, 주소는 문서용 대역입니다.

```
from="192.0.2.0/24",no-port-forwarding ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8g alice@ws01
```

세 번째 필드의 base64 를 풀면 아래 51바이트가 나옵니다.

```
00000000  00 00 00 0b 73 73 68 2d 65 64 32 35 35 31 39 00   ....ssh-ed25519.
00000010  00 00 20 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d   .. .............
00000020  0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d   ................
00000030  1e 1f 20                                          ..
```

`0x00` 의 `00 00 00 0b` 가 길이 11 이고 이어서 `ssh-ed25519` 가 옵니다. `0x0F` 의 `00 00 00 20` 이 길이 32 이고, 그 뒤 32바이트가 공개 키입니다. 이 51바이트 전체의 SHA-256 이 지문입니다[9].

| 표기 | 값 |
|---|---|
| sshd 로그·`ssh-keygen -l` | `SHA256:mKqU+0K8OhKmA8bBQi9Rz0Q5l7/g160hIP+rJYSTNj4` |
| 16진(dissect.target 의 sha256) | `98aa94fb42bc3a12a603c6c1422f51cf443997bfe0d7ad2120ffab258493363e` |
| MD5 16진 | `056d116faa827f17e4a29209cacf9d42` |

이 줄의 키로 들어온 로그인은 기본 설정에서 `Accepted publickey for alice from 192.0.2.10 port 50122 ssh2: ED25519 SHA256:mKqU+0K8OhKmA8bBQi9Rz0Q5l7/g160hIP+rJYSTNj4` 모양의 줄로 남습니다(만든 예시)[8]. 로그 줄 앞머리와 파일 위치는 [sshd 로그](sshd-logs.md)에서 다룹니다.

### 공개 도구로 한 번

`ssh-keygen -l -f` 는 authorized_keys 처럼 옵션이 붙은 줄도 읽고, 줄마다 `비트수 지문 comment (형식)` 을 한 줄씩 찍습니다[10]. 검체 사본에서 돌리면 되고, `-E md5` 로 MD5 표기를 고를 수 있습니다[10].

```
ssh-keygen -l -f ./home/alice/.ssh/authorized_keys
ssh-keygen -l -E md5 -f ./home/alice/.ssh/authorized_keys
```

위 예시 줄이면 `256 SHA256:mKqU+0K8OhKmA8bBQi9Rz0Q5l7/g160hIP+rJYSTNj4 alice@ws01 (ED25519)` 가 나옵니다.

이미지 전체에서 모을 때는 dissect.target 의 `openssh.authorized_keys` 가 사용자별로 옵션·형식·comment·지문(MD5·SHA-1·SHA-256)을 레코드로 내놓습니다[12]. 경로를 바꾼 설정이 있으면 먼저 그 경로를 찾아 따로 읽습니다.

```
grep -rn -i "AuthorizedKeysFile\|AuthorizedKeysCommand\|TrustedUserCAKeys" ./etc/ssh/sshd_config ./etc/ssh/sshd_config.d/
```

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [sshd 로그](sshd-logs.md) | 이 줄의 지문이 `Accepted publickey` 에 나오는가, 처음 나온 때는 언제인가 |
| [sshd 설정](sshd-config.md) | `AuthorizedKeysFile`·`AuthorizedKeysCommand`·`TrustedUserCAKeys`·`StrictModes`·`LogLevel` 값 |
| [로그인 기록](../wtmp-btmp-lastlog.md) | 로그 시각과 같은 때에 그 계정의 세션이 있는가 |
| [셸 명령 기록](../../execution/shell-history/index.md) | `ssh-copy-id`, `echo … >> ~/.ssh/authorized_keys` 같은 명령이 있는가 |
| [known_hosts 와 클라이언트 설정](known-hosts.md) | 다른 기계의 `~/.ssh/*.pub` 나 known_hosts 에서 같은 키·같은 호스트가 보이는가 |
| [계정 생성·변경 흔적](../account-changes.md) | 키가 든 계정을 언제 만들었는가 |

파일 시각은 쉽게 바꿀 수 있으므로, mtime 하나로 키를 넣은 때를 정하지 말고 로그와 셸 기록의 시각을 함께 놓고 봅니다. 흔적을 지운 정황을 보는 법은 [흔적을 지웠나](../../../04-scenarios/insider/anti-forensics.md)에서 다룹니다.

## 실습

Linux 서버 디스크 이미지(NIST CFReDS 등 공개 검체)나 직접 만든 가상 머신 이미지로 풀어 봅니다.

1. `/etc/ssh/sshd_config` 와 `sshd_config.d` 에서 `AuthorizedKeysFile` 은 어떤 값인가? 배포판 기본값과 같은가?
2. `/root` 를 포함한 모든 홈에서 `authorized_keys` 와 `authorized_keys2` 는 몇 개이고, 각각 몇 줄인가?
3. 옵션이 붙은 줄이 있는가? `command=`·`from=`·`cert-authority` 가 있다면 무엇을 허용하는가?
4. 각 줄의 SHA-256 지문을 구해 인증 로그의 `Accepted publickey` 줄과 맞추면, 처음 쓰인 때는 언제인가?
5. 파일 mtime·ctime 과 그 계정의 셸 기록 가운데 파일을 고친 명령의 순서가 맞는가?

## 참고 문헌

1. OpenSSH, sshd.8 (AUTHORIZED_KEYS FILE FORMAT, FILES) — https://github.com/openssh/openssh-portable/blob/master/sshd.8
2. OpenSSH, sshd_config.5 (AuthorizedKeysFile, AuthorizedKeysCommand, AuthorizedPrincipalsFile, PermitUserEnvironment, StrictModes, TOKENS, Match) — https://github.com/openssh/openssh-portable/blob/master/sshd_config.5
3. OpenSSH, sshd_config (master, V_9_9_P1) — https://github.com/openssh/openssh-portable/blob/master/sshd_config , https://github.com/openssh/openssh-portable/blob/V_9_9_P1/sshd_config
4. Ubuntu openssh 패키지(noble-updates), debian/changelog·debian/patches/restore-authorized_keys2.patch·debian-config.patch — https://git.launchpad.net/ubuntu/+source/openssh/tree/debian?h=ubuntu/noble-updates
5. CentOS Stream 9 openssh 패키지, openssh.spec·openssh-7.7p1-redhat.patch — https://gitlab.com/redhat/centos-stream/rpms/openssh/-/tree/c9s
6. OpenSSH, auth2-pubkeyfile.c — https://github.com/openssh/openssh-portable/blob/master/auth2-pubkeyfile.c
7. OpenSSH, misc.c — https://github.com/openssh/openssh-portable/blob/master/misc.c
8. OpenSSH, auth.c — https://github.com/openssh/openssh-portable/blob/master/auth.c
9. OpenSSH, sshkey.c·ssh-ed25519.c·sshbuf-getput-basic.c — https://github.com/openssh/openssh-portable/blob/master/sshkey.c , https://github.com/openssh/openssh-portable/blob/master/ssh-ed25519.c , https://github.com/openssh/openssh-portable/blob/master/sshbuf-getput-basic.c
10. OpenSSH, ssh-keygen.c·ssh-keygen.1 — https://github.com/openssh/openssh-portable/blob/master/ssh-keygen.c , https://github.com/openssh/openssh-portable/blob/master/ssh-keygen.1
11. Velociraptor, Linux.Ssh.AuthorizedKeys — https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Ssh/AuthorizedKeys.yaml
12. dissect.target, plugins/apps/ssh/openssh.py·ssh.py — https://github.com/fox-it/dissect.target/tree/main/dissect/target/plugins/apps/ssh
13. UAC, artifacts/files/ssh/authorized_keys.yaml — https://github.com/tclahr/uac/blob/main/artifacts/files/ssh/authorized_keys.yaml
14. ForensicArtifacts, artifacts/data/linux.yaml (SSHAuthorizedKeysFiles) — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
