---
title: "비밀번호 보관함"
parent: "아티팩트 · 데스크톱 환경"
nav_order: 860
---

# 비밀번호 보관함 (GNOME Keyring·KWallet)

Linux 데스크톱의 비밀번호 보관함은 GNOME 에서는 `~/.local/share/keyrings/*.keyring`, KDE 에서는 `~/.local/share/kwalletd/*.kwl` 에 있고, 암호 없이도 보관함 이름·시각·항목 수와 속성의 해시 값이 보여서 "이 계정에 어떤 앱의 비밀이 저장돼 있었는가" 까지는 확인할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

데스크톱 앱은 저장한 암호나 브라우저가 쿠키·저장 비밀번호를 암호화할 때 쓰는 키 같은 비밀을 직접 파일에 두지 않고 보관함 데몬에 맡깁니다. GNOME 에서는 gnome-keyring 데몬이, KDE 에서는 KWallet 이 이 일을 합니다. 데몬은 비밀을 보관함 (keyring, wallet) 파일 하나에 모아 사용자 암호로 암호화해 둡니다[5][10].

GNOME 에서는 로그인할 때 PAM 모듈 pam_gnome_keyring 이 로그인 암호를 데몬에 넘기고, 데몬은 식별자가 `login` 인 로그인 키링 (login keyring) 을 그 암호로 엽니다[3][7]. 로그인 키링이 없으면 이때 새로 만듭니다[3]. 그래서 GNOME 에 한 번이라도 로그인한 계정에는 보통 `login.keyring` 이 생깁니다. PAM 모듈은 잠금 해제의 성공·실패를 syslog 에 남깁니다[7].

KWallet 도 PAM 과 이어질 수 있습니다. `ksecretd` 는 환경 변수 `PAM_KWALLET5_LOGIN` 이 있으면 `--pam-login` 인자로 받은 파이프에서 암호 해시를, 소켓에서 환경 변수를 받고, 그 해시로 지갑을 엽니다[13]. PAM 설정 파일을 읽는 법은 [인증 모듈](../../01-foundations/users-auth/pam.md)에서 다룹니다.

Chromium 계열 브라우저는 Linux 에서 쿠키·저장 비밀번호를 암호화하는 키를 이 보관함에 둡니다[14][16]. 보관함에 Chrome 항목이 있는지, 브라우저 DB 의 암호문이 어느 방식으로 암호화됐는지가 서로 맞물리므로, 이 페이지와 [Linux 의 브라우저 프로필](browsers.md)을 함께 봅니다.

## 위치와 버전별 차이

| 보관함 | 위치 | 비고 |
|---|---|---|
| GNOME Keyring | `~/.local/share/keyrings/*.keyring` (`$XDG_DATA_HOME/keyrings`) | 폴더는 소유자만 읽고 쓰는 권한(0700)으로 만든다[1] |
| GNOME Keyring 옛 위치 | `~/.gnome2/keyrings/` | 새 위치가 없고 옛 위치만 있을 때 데몬이 옛 위치를 쓴다[1] |
| libsecret 파일 백엔드 | `$XDG_DATA_HOME/keyrings/default.keyring` | Flatpak·Snap 안에서는 포털 (`org.freedesktop.portal.Secret`) 에서 받은 비밀로 연다[8] |
| KWallet 지갑 | `~/.local/share/kwalletd/지갑이름.kwl` | 기본 지갑 이름은 `kdewallet`[10][12] |
| KWallet PAM 소금 | `~/.local/share/kwalletd/지갑이름.salt` | PBKDF2-SHA512 해시에 쓰는 소금. 지갑 암호를 정할 때 없으면 만든다[10] |
| KWallet 설정 | `kwalletrc` | 기본 지갑·잠금 설정·이관 기록[12] |

GNOME Keyring 파일 이름은 키링 식별자에 `.keyring` 을 붙인 것이고, 같은 이름이 이미 있으면 `이름_1.keyring` 처럼 숫자를 붙입니다[2]. 파일은 소유자만 읽고 쓰는 권한(0600)으로 만듭니다[2]. KWallet 파일 이름은 지갑 이름이고, 허용되지 않는 문자는 `;` 뒤에 16진수를 붙이는 방식으로 바꿔 적습니다[10].

libsecret 파일 백엔드는 gnome-keyring 데몬이 아니라 libsecret 라이브러리가 직접 쓰는 형식입니다. Flatpak(`/.flatpak-info` 가 있을 때)이나 Snap(환경 변수 `SNAP_NAME` 이 있을 때) 안에서는 포털에서 받은 비밀로 파일을 열고, TPM 을 켜고 빌드한 libsecret 은 같은 폴더의 `default.keyring.tpm2` 에서 비밀을 꺼냅니다[8]. 그래서 이 형식의 `default.keyring` 은 샌드박스 안에서 돈 앱의 흔적일 가능성이 있습니다.

KWallet 은 최근 구조가 바뀌었습니다. 지금의 kwallet 프레임워크에서 `kwalletd` 는 KWallet API 를 받아 Secret Service 로 넘기기만 하고, 예전 kwalletd 코드였던 `ksecretd` 가 Secret Service API 를 제공하며 비밀을 저장합니다[9]. `kwalletrc` 에 `[KSecretD] Enabled=false` 가 있으면 다른 Secret Service 제공자를 쓰고, 여기에 `[Migration] MigrateTo3rdParty=true` 까지 있으면 기존 지갑 내용을 그 제공자로 옮깁니다[9][20]. 옮긴 지갑 이름은 `[Migration]` 그룹의 `WalletsMigratedToSecretService` 에 남습니다[12][20].

배포판에 따른 차이는 파일 위치보다 로그 파일 이름에서 납니다. 보관함 경로는 Ubuntu 24.04 와 RHEL 9 에서 같고, 쓰는 데스크톱에 따라 GNOME Keyring 과 KWallet 중 어느 쪽이 있는지가 갈립니다.

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| gkr-pam 줄이 남는 파일 | `/var/log/auth.log` | `/var/log/secure` |
| PAM 설정 | `/etc/pam.d/` 아래 파일 | `/etc/pam.d/` 아래 파일 |

pam_gnome_keyring 이 어느 서비스에 걸려 있는지는 분석 대상의 `/etc/pam.d/` 에서 `pam_gnome_keyring` 이 들어간 줄을 찾아 확인합니다. 로그 파일 위치와 줄 형식은 [인증 로그](../logins/auth-log.md)에서 다룹니다.

## 구조

### GNOME Keyring 파일

파일은 16바이트 머리 `GnomeKeyring\n\r\0\n` 으로 시작하고, 이어서 주 버전·부 버전·암호 방식·해시 방식이 1바이트씩 옵니다[5]. gnome-keyring 데몬이 쓰는 형식은 네 값이 모두 0 이고, 암호 방식 0 은 AES, 해시 방식 0 은 MD5 입니다[5]. 정수는 빅엔디언 uint32 이고, 문자열은 uint32 길이 뒤에 바이트가 오며 NULL 은 길이 `0xffffffff` 로 적습니다[4]. 시각은 64비트 Unix 초를 상위 uint32·하위 uint32 두 개로 나눠 적습니다[5].

머리 뒤는 암호 없이 읽히는 평문 부분과 암호화된 부분으로 나뉩니다[4][5].

| 순서 | 필드 | 크기 | 뜻 |
|---|---|---|---|
| 1 | 키링 이름 | 문자열 | 보관함 레이블 |
| 2 | 시각 1 | 8바이트 | 수정·생성 시각 중 하나(아래 "함정" 참고) |
| 3 | 시각 2 | 8바이트 | 수정·생성 시각 중 나머지 하나 |
| 4 | flags | uint32 | 1 = 쉬면 잠금, 2 = 일정 시간 뒤 잠금 |
| 5 | lock_timeout | uint32 | 잠금까지의 시간 |
| 6 | hash_iterations | uint32 | 저장할 때마다 1000~4095 사이에서 새로 뽑는 값 |
| 7 | salt | 8바이트 | 저장할 때마다 새로 만드는 값 |
| 8 | 예약 | uint32 × 4 | 0 |
| 9 | 항목 수 | uint32 | 저장된 비밀 개수 |
| 10 | 항목마다 | 가변 | id, type, 속성 수, 속성마다 이름·형식·**해시한 값** |
| 11 | 암호문 길이 | uint32 | 16의 배수 |
| 12 | 암호문 | 가변 | 복호 확인용 MD5 16바이트, 항목별 표시 이름, 비밀 값, 생성·수정 시각, 평문 속성, ACL |

속성 이름은 평문이고, 속성 값은 해시로 바꿔 적습니다. 문자열 값은 MD5 를 소문자 16진수 32글자로 적고, 정수 값은 `0x18273645 ^ x ^ (x << 16 | x >> 16)` 으로 바꿉니다[6]. 암호화 부분은 사용자 암호와 salt 로 SHA-256 을 hash_iterations 번 돌려 만든 키로 AES-128-CBC 암호화합니다[5].

### libsecret 파일 백엔드

libsecret 파일 백엔드도 같은 16바이트 머리를 쓰지만 그 뒤 두 바이트가 주 버전 1, 부 버전 0 입니다[8]. 나머지는 GVariant 형식 `(uayutua(a{say}ay))` 으로, salt 크기·salt·반복 횟수·수정 시각·사용 횟수·항목 배열이 차례로 옵니다[8]. 수정 시각은 uint64 리틀엔디언 Unix 초이고, 암호 없이 읽힙니다[8]. 항목의 속성 이름은 평문이지만 값은 MD5 가 아니라 키를 넣은 MAC 이라서, 암호 없이는 알려진 값과 견줄 수 없습니다[8].

### KWallet 지갑 파일 (.kwl)

`.kwl` 은 12바이트 매직 `KWALLET\n\r\0\r\n` 으로 시작하고 이어서 4바이트가 옵니다[10].

| 바이트 | 뜻 | 값 |
|---|---|---|
| 0 | 주 버전 | 0 |
| 1 | 부 버전 | 0 또는 1. 1 이면 새 해시 방식(4.13 이후) |
| 2 | 암호 방식 | 0 Blowfish ECB(옛 방식), 1 3DES(지원 안 함), 2 GPG, 3 Blowfish CBC |
| 3 | 해시 방식 | 0 SHA1, 1 MD5(지원 안 함), 2 PBKDF2-SHA512(PAM 연동 또는 4.13 이후) |

그 뒤에는 암호 없이 읽히는 해시 목록이 옵니다. 폴더 수(빅엔디언 quint32) 다음에, 폴더마다 폴더 이름의 MD5 16바이트와 항목 수, 항목 키 이름의 MD5 16바이트가 차례로 옵니다[11]. 해시 목록 다음이 암호화 블록입니다[11]. 60바이트보다 작은 `.kwl` 은 KWallet 이 지갑으로 보지 않습니다[10].

## 증거로서 의미

**증명하는 것**

- 보관함 파일이 있으면 그 계정에서 보관함 데몬이 돌았고 보관함이 만들어졌다는 뜻입니다. `login.keyring` 은 GNOME 로그인으로 로그인 키링을 만든 흔적입니다[3].
- 평문 부분의 항목 수와 속성 이름으로 비밀이 몇 개 있고 어떤 종류의 속성을 쓰는지 알 수 있습니다[5].
- GNOME Keyring 의 문자열 속성 값은 MD5 라서, 알려진 값의 MD5 와 비교하면 그 값이 있는지 암호 없이 확인할 수 있습니다[6]. 예를 들어 Chromium 계열은 `application` 속성에 브랜드판이면 `chrome`, 오픈 소스판이면 `chromium` 을 넣습니다[14]. `chrome` 의 MD5 는 `554838a8451ac36cb977e719e9d6623c` 이므로, `application` 속성 값이 이 문자열이면 Chrome 이 이 키링에 키를 둔 적이 있다는 뜻입니다.
- `.kwl` 의 폴더 해시도 같은 방식으로 견줄 수 있습니다. Chrome 은 KWallet 에 `Chrome Keys` 폴더와 `Chrome Safe Storage` 키를, Chromium 은 `Chromium Keys` 폴더와 `Chromium Safe Storage` 키를 씁니다[14].
- gkr-pam 줄은 로그인 때 로그인 키링을 풀었는지, 풀지 못했는지를 보여 줍니다[7]. `the password for the login keyring was invalid.` 는 로그인 암호와 로그인 키링 암호가 달랐다는 뜻이라서, 관리자가 암호를 재설정한 기록과 맞춰 볼 단서가 됩니다.

**증명하지 못하는 것**

- 비밀 값, 항목별 표시 이름, 항목별 생성·수정 시각은 암호화 부분에 있어서 암호 없이는 알 수 없습니다[5][11].
- 보관함에는 누가 언제 비밀을 꺼내 썼는지 적는 필드가 없습니다[4][11]. 보관함 파일로는 "이 비밀을 사용했다" 를 말할 수 없습니다.
- `.kwl` 해시 목록은 폴더·키 이름의 존재만 알려 주고, 그 안의 값은 알려 주지 않습니다[11].
- 암호가 다르다는 gkr-pam 줄은 누가 암호를 바꿨는지 알려 주지 않습니다[7].

보고서에는 "이 계정의 login.keyring 에 application 속성 값이 chrome 의 MD5 와 같은 항목이 있다" 처럼 기록이 보여 주는 만큼만 씁니다.

## 시각 해석

| 기록 | 시각 형식 | 바뀌는 때 |
|---|---|---|
| GNOME Keyring 머리의 시각 2개 | 64비트 Unix 초, 빅엔디언(UTC) | 보관함을 저장할 때 그때의 생성·수정 시각을 적는다[5] |
| GNOME Keyring 항목 시각 | 64비트 Unix 초(UTC) | 암호화 부분 안에 있어 암호 없이는 볼 수 없다[5] |
| libsecret 파일의 수정 시각 | uint64 리틀엔디언 Unix 초(UTC) | 항목을 넣거나 바꿀 때 그 시각으로 바뀌고, 사용 횟수도 1 늘어난다[8] |
| `.kwl` | 파일 안에 시각 필드가 없다[10][11] | 파일 시스템 시각만 쓸 수 있다 |
| gkr-pam 줄 | 로그 파일의 시각 형식을 따른다 | 로그인할 때, 로그인 암호를 바꿀 때 |

Unix 초 값을 읽는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다. 전통 syslog 줄에는 연도와 시간대가 없으므로, gkr-pam 줄의 시각은 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)의 설명에 따라 연도와 시간대를 따로 정해야 합니다.

## 함정과 한계

GNOME Keyring 머리의 두 시각은 순서가 엇갈립니다. 형식 문서와 읽는 코드는 생성 시각 다음에 수정 시각이 온다고 보지만, 쓰는 코드는 수정 시각을 먼저, 생성 시각을 나중에 적습니다[4][5]. 항목 안쪽 시각은 읽을 때와 쓸 때 모두 생성 다음 수정 순서입니다[5]. 머리의 두 값은 어느 쪽이 생성 시각인지 단정하지 말고 둘 다 기록한 뒤 파일 시스템 시각과 비교합니다.

형식 문서와 코드가 다른 곳이 하나 더 있습니다. 형식 문서는 정수 속성 해시에 `0xdeadbeef` 를 쓴다고 적었지만, 코드는 `0x18273645` 를 씁니다[4][6]. 정수 값을 견줄 때는 코드의 식을 따르면 됩니다.

gnome-keyring 형식과 libsecret 파일 백엔드는 머리 16바이트가 같습니다[5][8]. 17번째·18번째 바이트가 `00 00` 인지 `01 00` 인지로 두 형식을 가른 뒤 읽어야 합니다.

hash_iterations 와 salt 는 저장할 때마다 새로 정해지므로, 같은 키링이라도 사본마다 값이 다릅니다[5]. 두 사본의 이 값이 다르다고 다른 키링이라고 볼 수는 없습니다.

KWallet 은 Secret Service 로 이관됐을 수 있습니다. `kwalletrc` 의 `WalletsMigratedToSecretService` 에 지갑 이름이 있으면 `.kwl` 이 최신 내용이 아닐 가능성이 있으므로, `.kwl` 만 보고 끝내지 않습니다[9][12]. 옛 Blowfish ECB 지갑은 다음 저장 때 CBC 로 바뀌므로, 암호 방식 바이트가 0 인 지갑은 그 방식으로 저장한 뒤로 다시 저장된 적이 없다는 뜻입니다[11].

UAC 와 ForensicArtifacts 의 `linux.yaml` 에는 `~/.local/share/keyrings` 나 `~/.local/share/kwalletd` 를 모으는 항목이 없습니다[18][19]. 이 두 폴더와 `kwalletrc` 는 따로 모아야 합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 gnome-keyring 형식 명세로 만든 예시입니다. 레이블 `Login`, 시각, salt 는 지어낸 값입니다.

```
00000000  47 6e 6f 6d 65 4b 65 79 72 69 6e 67 0a 0d 00 0a   GnomeKeyring....
00000010  00 00 00 00 00 00 00 05 4c 6f 67 69 6e 00 00 00   ........Login...
00000020  00 66 a1 b2 c3 00 00 00 00 66 5f 3a 80 00 00 00   .f.......f_:....
00000030  00 00 00 00 00 00 00 07 d3 11 22 33 44 55 66 77   .........."3DUfw
00000040  88 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ................
00000050  00 00 00 00 01                                    .....
```

`0x00`~`0x0F` 가 머리이고, `0x10`~`0x13` 의 `00 00 00 00` 이 버전·암호 방식·해시 방식이라서 gnome-keyring 데몬 형식입니다. `0x14` 의 `00 00 00 05` 는 레이블 길이이고 이어서 `Login` 이 옵니다. `0x1D` 부터 8바이트(`0x66A1B2C3` = 2024-07-25 02:04:51 UTC)가 첫째 시각, 다음 8바이트(`0x665F3A80` = 2024-06-04 16:02:08 UTC)가 둘째 시각입니다. 데몬이 쓴 파일이면 첫째가 수정, 둘째가 생성 시각입니다. 이어서 flags 0, lock_timeout 0, hash_iterations `0x7D3`(2003), salt 8바이트, 예약 16바이트가 오고, `0x51` 의 `00 00 00 01` 이 항목 수 1 입니다.

아래는 KWallet 형식 명세로 만든 예시입니다. Chrome 키 하나만 든 지갑을 가정했고, 해시 목록 뒤의 암호화 블록은 생략했습니다.

```
00000000  4b 57 41 4c 4c 45 54 0a 0d 00 0d 0a 00 01 03 02   KWALLET.........
00000010  00 00 00 01 41 f2 55 a6 16 e2 2e e4 76 71 66 66   ....A.U.....vqff
00000020  7c 82 24 ea 00 00 00 01 0c ed 84 f5 2e f6 ef 8e   |.$.............
00000030  15 2c 85 cc f9 f1 c1 bd                           .,......
```

`0x0C`~`0x0F` 의 `00 01 03 02` 는 주 버전 0, 부 버전 1, Blowfish CBC, PBKDF2-SHA512 입니다. `0x10` 의 `00 00 00 01` 이 폴더 수이고, 이어지는 16바이트 `41f255a616e22ee4767166667c8224ea` 는 `Chrome Keys` 의 MD5 입니다. 다음 `00 00 00 01` 이 그 폴더의 항목 수이고, 마지막 16바이트 `0ced84f52ef6ef8e152c85ccf9f1c1bd` 는 `Chrome Safe Storage` 의 MD5 입니다. Chromium 이면 폴더 해시가 `Chromium Keys` 의 MD5 인 `e8463316d20bad7a467dcdf13e90501b` 로 나옵니다.

### 공개 도구로 한 번

보관함 파일의 평문 부분은 위 표대로 헥스 편집기나 짧은 스크립트로 읽습니다. 로그는 문자열로 찾으면 됩니다.

```
grep -h "gkr-pam" /var/log/auth.log*      # Ubuntu
grep -h "gkr-pam" /var/log/secure*        # RHEL
journalctl --file=system.journal -g "gkr-pam"
```

gkr-pam 이 남기는 줄 본문은 아래와 같습니다[7].

| 줄 본문 | 수준 | 뜻 |
|---|---|---|
| `gkr-pam: unlocked login keyring` | INFO | 로그인 키링을 풀었다 |
| `gkr-pam: the password for the login keyring was invalid.` | ERR | 로그인 암호로 로그인 키링을 풀지 못했다 |
| `gkr-pam: couldn't unlock the login keyring.` | ERR | 로그인 키링을 풀지 못했다 |
| `gkr-pam: gnome-keyring-daemon started properly and unlocked keyring` | INFO | 데몬을 띄우고 키링을 풀었다 |
| `gkr-pam: gnome-keyring-daemon started properly` | INFO | 데몬을 띄웠다 |
| `gkr-pam: stashed password to try later in open session` | INFO | 인증 단계에서 암호를 받아 두고 세션 시작 때 쓴다 |
| `gkr-pam: changed password for login keyring` | NOTICE | 로그인 암호를 바꿀 때 로그인 키링 암호도 바꿨다 |
| `gkr-pam: couldn't change password for the login keyring: the passwords didn't match.` | ERR | 옛 암호가 키링 암호와 달라 바꾸지 못했다 |
| `gkr-pam: stopped the daemon` | NOTICE | 암호를 바꾸려고 잠시 띄운 데몬을 멈췄다 |
| `gkr-pam: no password is available for user` | WARN | 넘길 암호가 없었다 |

아래는 만든 예시 줄입니다. 호스트 이름, 프로그램 이름, PID 는 지어낸 값입니다.

```
Jul 25 11:04:51 ws01 example-login[2210]: gkr-pam: unlocked login keyring
```

Chromium 계열 암호문의 복호는 dissect.target 의 chromium 플러그인이 다루지만, 보관함 키를 쓰는 `v11` 암호문은 구현돼 있지 않고 고정 키를 쓰는 `v10` 만 다룹니다[17]. 브라우저 DB 쪽 해석은 [Linux 의 브라우저 프로필](browsers.md)에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [인증 로그](../logins/auth-log.md) | gkr-pam 줄의 시각과 같은 때에 로그인 성공 줄이 있는가 |
| [계정 파일](../../01-foundations/users-auth/passwd-shadow-group.md)·[계정 생성·변경 흔적](../logins/account-changes.md) | `password for the login keyring was invalid` 앞에 계정 암호를 바꾼 기록이 있는가 |
| [Linux 의 브라우저 프로필](browsers.md) | 브라우저 DB 암호문 앞 3바이트가 `v11` 인가 `v10` 인가. `v11` 이면 보관함에서 받은 키를 썼고, `v10` 이면 보관함을 쓰지 않았다[14][15] |
| [GNOME 흔적](gnome.md)·[KDE 흔적](kde.md) | 그 계정이 실제로 쓴 데스크톱이 무엇인가 |
| 보관함 파일의 파일 시스템 시각 | 머리 시각·libsecret 수정 시각과 맞는가 |

Chromium 은 `--password-store=` 로 `basic`, `gnome-libsecret`, `kwallet`, `kwallet5`, `kwallet6` 중 하나를 고를 수 있고, 지정하지 않으면 데스크톱 환경에 따라 KDE 에서는 KWallet, GNOME·Cinnamon·Xfce·Unity 등에서는 libsecret 을 고릅니다[14][16]. 쓸 수 없으면 `basic` 으로 돌아갑니다[16]. 그래서 KDE 계정인데 Chrome 항목이 GNOME Keyring 에 있거나 보관함에 Chrome 항목이 전혀 없다면, 실행 명령줄에서 `--password-store=` 를 지정했을 가능성을 살펴봅니다. `basic` 저장소를 문서는 평문 저장이라고 적지만, 코드는 고정 키로 암호화하고 `v10` 을 붙입니다[15][16]. 어느 쪽이든 사용자 암호로 보호되지 않는다는 점은 같습니다.

## 실습

GNOME 데스크톱이 들어 있는 Linux 디스크 이미지(NIST CFReDS 등 공개 시험 데이터)나 직접 만든 가상 머신 이미지로 풀어 봅니다.

1. 각 사용자 홈의 `.local/share/keyrings/` 에 어떤 파일이 있는가? 각 파일의 17·18번째 바이트로 형식을 가르면 무엇인가?
2. `login.keyring` 머리의 두 시각은 언제이고, 파일 시스템의 생성·수정 시각과 어떻게 맞는가?
3. 항목마다 `application` 속성이 있는가? 그 값이 `chrome` 이나 `chromium` 의 MD5 와 같은 항목이 있는가?
4. 인증 로그에서 `gkr-pam` 줄을 모으면, `unlocked login keyring` 과 `was invalid` 가 각각 언제 나오는가?
5. KDE 계정이라면 `kwalletrc` 에 `WalletsMigratedToSecretService` 가 있는가? `.kwl` 의 폴더 해시 중 `Chrome Keys` 의 MD5 가 있는가?

## 참고 문헌

1. gnome-keyring, pkcs11/gkm/gkm-util.c — https://github.com/GNOME/gnome-keyring/blob/main/pkcs11/gkm/gkm-util.c
2. gnome-keyring, pkcs11/secret-store/gkm-secret-module.c — https://github.com/GNOME/gnome-keyring/blob/main/pkcs11/secret-store/gkm-secret-module.c
3. gnome-keyring, daemon/login/gkd-login.c — https://github.com/GNOME/gnome-keyring/blob/main/daemon/login/gkd-login.c
4. gnome-keyring, pkcs11/secret-store/file-format.txt — https://github.com/GNOME/gnome-keyring/blob/main/pkcs11/secret-store/file-format.txt
5. gnome-keyring, pkcs11/secret-store/gkm-secret-binary.c — https://github.com/GNOME/gnome-keyring/blob/main/pkcs11/secret-store/gkm-secret-binary.c
6. gnome-keyring, pkcs11/secret-store/gkm-secret-fields.c — https://github.com/GNOME/gnome-keyring/blob/main/pkcs11/secret-store/gkm-secret-fields.c
7. gnome-keyring, pam/gkr-pam-module.c·gkr-pam.h — https://github.com/GNOME/gnome-keyring/blob/main/pam/gkr-pam-module.c , https://github.com/GNOME/gnome-keyring/blob/main/pam/gkr-pam.h
8. libsecret, libsecret/secret-file-collection.c·secret-file-backend.c·secret-types.h — https://github.com/GNOME/libsecret/blob/main/libsecret/secret-file-collection.c , https://github.com/GNOME/libsecret/blob/main/libsecret/secret-file-backend.c , https://github.com/GNOME/libsecret/blob/main/libsecret/secret-types.h
9. KWallet, README.md — https://github.com/KDE/kwallet/blob/master/README.md
10. KWallet, src/runtime/kwalletbackend/kwalletbackend.cc — https://github.com/KDE/kwallet/blob/master/src/runtime/kwalletbackend/kwalletbackend.cc
11. KWallet, src/runtime/kwalletbackend/backendpersisthandler.cpp — https://github.com/KDE/kwallet/blob/master/src/runtime/kwalletbackend/backendpersisthandler.cpp
12. KWallet, src/kwalletsettings.kcfg — https://github.com/KDE/kwallet/blob/master/src/kwalletsettings.kcfg
13. KWallet, src/runtime/ksecretd/main.cpp — https://github.com/KDE/kwallet/blob/master/src/runtime/ksecretd/main.cpp
14. Chromium, components/os_crypt/async/browser/freedesktop_secret_key_provider.cc·.h — https://github.com/chromium/chromium/blob/main/components/os_crypt/async/browser/freedesktop_secret_key_provider.cc , https://github.com/chromium/chromium/blob/main/components/os_crypt/async/browser/freedesktop_secret_key_provider.h
15. Chromium, components/os_crypt/async/browser/posix_key_provider.cc — https://github.com/chromium/chromium/blob/main/components/os_crypt/async/browser/posix_key_provider.cc
16. Chromium, docs/linux/password_storage.md — https://github.com/chromium/chromium/blob/main/docs/linux/password_storage.md
17. dissect.target, plugins/apps/browser/chromium.py — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/browser/chromium.py
18. UAC, artifacts — https://github.com/tclahr/uac/tree/main/artifacts
19. ForensicArtifacts, artifacts/data/linux.yaml — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
20. KWallet, src/runtime/kwalletd/kwalletd.cpp — https://github.com/KDE/kwallet/blob/master/src/runtime/kwalletd/kwalletd.cpp
