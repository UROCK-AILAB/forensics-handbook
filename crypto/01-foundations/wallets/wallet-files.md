---
title: "지갑 파일과 암호화"
parent: "기반 · 지갑과 키"
nav_order: 80
---

# 지갑 파일과 암호화 (Wallet Files)

지갑 프로그램은 키와 주소, 거래 내역을 기기의 파일에 저장하고, 암호를 걸면 그 파일의 일부나 전체를 암호화합니다. Bitcoin Core 와 키스토어 암호만 건 Electrum 은 개인 키 같은 비밀 부분만 암호화해서 주소·거래·라벨이 평문으로 남고, 이더리움 keystore 도 개인 키만 암호화합니다. Electrum 의 파일 전체 암호화나 Exodus 의 보안 컨테이너처럼 본문을 통째로 암호화하는 형식도 머리 부분은 평문이라, 형식과 만든 앱 정도는 암호 없이 확인할 수 있습니다. 이 페이지는 지갑 파일별로 어디에 있고, 어떤 모양이며, 무엇이 평문으로 보이는지를 정리합니다.

## 이 형식을 쓰는 아티팩트

| 지갑 | 파일과 위치 | 형식 | 평문으로 보이는 것 | 암호화되는 것 | 자세히 |
|---|---|---|---|---|---|
| Bitcoin Core (descriptor 지갑, 0.21 부터) | 데이터 폴더의 `wallets/이름/wallet.dat`, `wallet.dat-journal` | SQLite, 표 `main` 하나 | 거래, 주소 라벨, descriptor, 메타데이터 | 개인 키만 | [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md) |
| Bitcoin Core (legacy 지갑) | `wallet.dat`, `database/`, `db.log`, `.walletlock` | Berkeley DB | 위와 같음 | 개인 키만 | [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md) |
| Electrum | 사용자 폴더의 `wallets/default_wallet` 등 | JSON 텍스트, 파일 전체 암호화 시 base64 덩어리 | 파일 암호화가 없으면 JSON 전체(주소·거래·라벨·xpub) | 시드·xprv·가져온 키, 또는 파일 전체 | [Electrum](../../02-artifacts/desktop/electrum.md) |
| 이더리움 keystore (Web3 Secret Storage v3) | `keystore` 폴더의 JSON 파일 | JSON | `id`, `version`, KDF·암호 알고리즘 설정, 구현에 따라 `address` | 개인 키(`ciphertext`) | [이더리움의 계정과 로그](../blockchain/ethereum-accounts.md) |
| MetaMask (브라우저 확장) | 브라우저 확장 저장소(Chrome 은 LevelDB) | 볼트 JSON 문자열 `data`·`iv`·`salt` | 볼트 밖의 상태 | 키링 배열 전체 | [MetaMask](../../02-artifacts/browser/metamask/index.md) |
| Exodus | 보안 컨테이너(SECO) 파일 | 이진 컨테이너 | 머리(매직·앱 이름·앱 버전), 암호화 설정 | 본문 | [Exodus](../../02-artifacts/desktop/exodus.md) |
| Ledger Live 데스크톱 | DB 폴더의 `app.json` 등 | JSON `{ "data": … }` | settings, knownDevices 등 | 암호 잠금을 켜면 `accounts`·`trustchain`·`wallet` | [하드웨어 지갑](../../02-artifacts/hardware/hardware-wallets.md) |

지갑 종류(수탁형·비수탁형·하드웨어)의 차이는 [지갑의 종류](wallet-types.md)에서, 파일에 들어 있는 xpub·파생 경로를 해석하는 방법은 [복구 문구와 파생 경로](seed-derivation.md)에서 다룹니다.

## 구조

### Bitcoin Core `wallet.dat`

데이터 폴더의 기본 위치는 Linux `$HOME/.bitcoin/`, macOS `$HOME/Library/Application Support/Bitcoin/`, Windows `%LOCALAPPDATA%\Bitcoin\` 입니다[1]. 테스트넷·시그넷 등은 데이터 폴더 아래 `testnet3/`·`testnet4/`·`signet/`·`regtest/` 하위 폴더를 따로 씁니다[1]. 이름을 붙인 지갑은 `wallets/지갑이름/` 에, 이름 없는 기본 지갑은 `wallets/` 에 있고, `wallets/` 폴더가 없으면 데이터 폴더에 바로 있습니다[1]. `-walletdir`·`-wallet` 옵션으로 위치를 바꿀 수 있어서 `bitcoin.conf`·`settings.json` 도 함께 확인합니다[1].

버전에 따라 형식과 위치가 달라집니다.

| 버전 | 바뀐 점 |
|---|---|
| 0.13 | HD 지갑 도입. 그 전 지갑은 HD 가 아닙니다[2] |
| 0.21.0 | descriptor 지갑 도입. descriptor 지갑은 SQLite, legacy 지갑은 Berkeley DB 를 씁니다[3] |
| 23.0 | 새 지갑의 기본 종류가 descriptor 지갑으로 바뀝니다[4] |
| 28.0 | Windows 기본 데이터 폴더가 `AppData\Roaming\Bitcoin` 에서 `AppData\Local\Bitcoin` 으로 바뀝니다. 옛 폴더가 있으면 그 폴더를 계속 씁니다[5] |
| 30.0 | Berkeley DB legacy 지갑은 만들거나 열 수 없고 `migratewallet` 으로 옮기기만 합니다. `dumpprivkey`·`dumpwallet` 등 legacy 전용 명령이 빠집니다[6] |

SQLite 지갑에는 `CREATE TABLE main(key BLOB PRIMARY KEY NOT NULL, value BLOB NOT NULL)` 표 하나만 있습니다[7]. PRAGMA `application_id` 에는 네트워크 매직 값이 들어가서 메인넷과 테스트넷 지갑이 구분되고, `user_version` 은 0 입니다[7]. 모든 레코드는 이 표의 키·값 한 쌍이고, 키 앞머리에 레코드 종류를 나타내는 문자열이 길이 바이트와 함께 붙습니다. 예를 들어 마스터 키 레코드의 키는 `\x04mkey\x01\x00\x00\x00` 입니다[24].

| 레코드 종류 | 내용 |
|---|---|
| `tx` | 지갑과 관련된 트랜잭션. 키에 트랜잭션 ID 가 붙습니다[8] |
| `name`, `purpose` | 주소별 라벨과 용도. 키에 주소 문자열이 붙습니다[8] |
| `walletdescriptor` | descriptor 문자열과 `creation_time`·`next_index`·`range_start`·`range_end`[8][10] |
| `walletdescriptorcache`, `walletdescriptorlhcache` | descriptor 에서 파생한 확장 공개 키 캐시[8] |
| `activeexternalspk`, `activeinternalspk` | 받는 주소용·거스름돈용으로 쓰는 descriptor[8] |
| `walletdescriptorkey` / `walletdescriptorckey` | descriptor 의 개인 키. 암호화하면 `ckey` 가 붙은 레코드로 바뀌고 평문 레코드는 지워집니다[8] |
| `mkey` | 암호화한 마스터 키. 지갑을 암호화했을 때만 있습니다[8][9] |
| `bestblock`, `lockedutxo`, `flags`, `version`, `minversion` | 마지막으로 동기화한 블록, 잠근 출력, 지갑 플래그와 버전[8] |
| `key`, `ckey`, `keymeta`, `hdchain`, `pool`, `watchs`, `cscript` 등 | legacy 지갑 전용 레코드[8] |

암호화는 두 단계입니다. 사용자 암호에서 SHA-512 를 반복해 키를 만들고, 이 키로 무작위 마스터 키를 AES-256-CBC 로 암호화해 `mkey` 에 저장합니다[9]. 개인 키는 이 마스터 키로 다시 AES-256-CBC 암호화합니다[9]. `mkey` 값에는 `vchCryptedKey`·`vchSalt`(8바이트)·`nDerivationMethod`·`nDeriveIterations` 필드가 있고[9], 반복 횟수는 최소 25,000회이고, 암호화하거나 암호를 바꿀 때 그 컴퓨터에서 약 0.1초가 걸리도록 늘어납니다[9][11]. 암호화되는 것은 개인 키뿐이라 거래, 공개 키, 메타데이터는 그대로 보입니다[2].

### Electrum 지갑 파일

사용자 폴더는 환경 변수 `ELECTRUMDIR` 이 있으면 그 경로, Android 이면 앱 데이터 폴더, Linux·macOS 같은 POSIX 계열은 `~/.electrum`, Windows 는 `%APPDATA%\Electrum`(없으면 `%LOCALAPPDATA%\Electrum`) 입니다[12]. 지갑은 그 아래 `wallets/` 에 있고 기본 이름은 `default_wallet` 입니다[13]. 테스트넷 같은 다른 체인을 고르면 체인별 하위 폴더를 따로 씁니다[13].

파일은 세 모양 중 하나입니다. 파일 내용을 base64 로 풀어 앞 4바이트가 `BIE1` 이면 사용자 암호로 파일 전체를 암호화한 것이고, `BIE2` 이면 하드웨어 장치의 키로 파일 전체를 암호화한 것입니다[14]. 둘 다 아니면 평문 JSON 입니다[14]. 파일 전체를 암호화할 때는 zlib 으로 압축한 뒤 ECIES 로 암호화합니다[14].

평문 JSON 의 주요 필드는 아래와 같습니다[15][16].

| 필드 | 내용 |
|---|---|
| `seed_version` | 파일 형식 버전. 현재 코드의 최종 값은 73 입니다[15] |
| `wallet_type` | `standard`, `imported`, `2fa`, 멀티시그 종류 등[15] |
| `keystore` | `type`(`bip32`·`imported`·`old`·`hardware`), `xpub`, `xprv`, `seed`, `derivation`, `root_fingerprint`. 하드웨어 지갑이면 `hw_type`·`label`·`soft_device_id`[16] |
| `use_encryption` | 키스토어 암호를 걸었는지[15] |
| `addresses` | 받는 주소·거스름돈 주소 목록[15] |
| `transactions`, `txi`, `txo`, `spent_outpoints` | 원본 트랜잭션과 입출력 관계[15] |
| `addr_history` | 주소별 (txid, 높이) 목록[15] |
| `verified_tx3` | txid 별 (블록 높이, 블록 시각, 블록 안 위치, 블록 해시)[12][15] |
| `labels` | 사용자가 붙인 라벨[15] |

키스토어 암호만 걸린 파일은 `seed`·`passphrase`·`xprv`·가져온 개인 키 값만 암호문으로 바뀌고 나머지 JSON 은 평문 그대로입니다[16]. Electrum 시드와 BIP-39 복구 문구의 차이는 [복구 문구와 파생 경로](seed-derivation.md)에서 다룹니다.

### 이더리움 keystore (Web3 Secret Storage v3)

명세의 기본 위치는 유닉스 계열 `~/.web3/keystore`, Windows `~/AppData/Web3/keystore` 이고, 파일 이름은 `UUID.json` 을 권합니다[17]. geth 와 함께 배포되는 clef 는 `keystore/UTC--2022-10-28T15-19-08.000825927Z--5e97870f263700f46aa00d967821199b9bc5a120` 처럼 파일 이름에 생성 시각과 주소를 넣습니다[18].

JSON 필드는 `crypto`(`cipher`, `cipherparams.iv`, `ciphertext`, `kdf`, `kdfparams`, `mac`), `id`(UUID), `version`(3) 입니다[17]. `kdf` 는 `pbkdf2` 또는 `scrypt` 이고, `kdfparams` 에는 KDF 매개변수(PBKDF2 는 `prf`·반복 횟수 `c`, scrypt 는 `n`·`r`·`p`)와 솔트·키 길이가 평문으로 들어갑니다[17]. 암호 알고리즘은 최소 `aes-128-ctr` 을 지원해야 합니다[17]. v1 에 있던 `address` 필드는 필요 없고 개인정보를 해친다는 이유로 명세에서 빠졌지만[17], 구현에 따라 주소를 넣습니다. 옛 Trust Wallet iOS 라이브러리(trust-keystore)는 `address`, `type`(`mnemonic` 이면 HD 지갑), `id`, `crypto`(대문자 `Crypto` 도 읽음), `activeAccounts`, `version`, `coin` 필드를 쓰고, `activeAccounts` 에 계정별 `derivationPath`·`extendedPublicKey`·`addressData` 를 저장합니다[19].

### Exodus 보안 컨테이너 (SECO)

Exodus 가 만든 secure-container 라이브러리의 파일은 고정 길이 영역이 차례로 놓인 이진 형식입니다[20].

| 오프셋 | 길이 | 내용 |
|---|---|---|
| 0x000 | 224 | 머리. 남는 부분은 0 으로 채웁니다 |
| 0x0E0 | 32 | 체크섬(메타데이터·본문 길이·본문의 SHA-256) |
| 0x100 | 256 | 메타데이터: scrypt `salt`(32)·`n`·`r`·`p`, 암호 이름(`aes-256-gcm`), 본문 키의 IV·인증 태그·암호화된 키, 본문의 IV·인증 태그 |
| 0x200 | 4 | 본문 길이(UInt32 빅엔디언) |
| 0x204 | 가변 | 암호화된 본문 |

머리는 매직 `SECO`(4바이트), `version`(UInt32 빅엔디언, 0), `reserved`(UInt32 빅엔디언, 0), 그 뒤로 1바이트 길이를 앞에 붙인 문자열 세 개 `versionTag`(`seco-v0-scrypt-aes`)·`appName`·`appVersion` 입니다[20]. 그래서 머리만 읽어도 어떤 앱의 어떤 버전이 이 파일을 썼는지 확인됩니다.

### MetaMask 볼트

MetaMask 는 키링 배열을 직렬화해 암호화한 문자열을 KeyringController 상태의 `vault` 에 저장합니다[23]. 암호화 결과는 base64 필드 `data`·`iv`·`salt` 로 이루어진 JSON 이고, 새 형식에는 `keyMetadata`(`algorithm`: `PBKDF2`, `params.iterations`)가 더 붙습니다[22]. 알고리즘은 AES-GCM 이고, PBKDF2 반복 횟수 기본값은 900,000회, 옛 기본값은 10,000회입니다[22]. `keyMetadata` 가 없으면 옛 형식입니다. KeyringController 상태 가운데 `vault` 는 저장소에 기록되고, `encryptionKey`·`encryptionSalt` 는 기록되지 않는 메모리 상태입니다(`persist: false`)[23]. `encryptionKey` 는 `cacheEncryptionKey` 옵션을 켰을 때만 상태에 들어갑니다[23]. Chrome 에서의 위치는 `%localappdata%\Google\Chrome\User Data\Default\Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn\` 이고, 다른 Chromium 계열 브라우저도 마지막 폴더 이름이 같습니다[24]. 키링 종류와 볼트 밖 상태는 [MetaMask](../../02-artifacts/browser/metamask/index.md) 페이지에서 다룹니다.

### Ledger Live 데스크톱

Ledger Live 는 네임스페이스마다 `네임스페이스.json` 파일을 두고, 내용은 `{ "data": … }` 모양의 JSON 입니다[21]. `app.json` 의 최상위 키는 `accounts`, `countervalues`, `settings`, `trustchain`, `wallet`, `market`, `knownDevices`, `cryptoAssets`, `identities`, `featureFlags`, `discover`, `ptx`, `history` 등입니다[21]. 암호 잠금을 켜면 `accounts`·`trustchain`·`wallet` 세 키의 값만 암호화하고, 나머지는 평문입니다[21]. 암호는 AES-256-CBC 이고 키는 PBKDF2-SHA512 10,000회로 만듭니다[21]. 암호화한 값은 IV 16바이트, `:`, 암호문을 이어 붙여 base64 로 인코딩한 문자열이라, base64 를 푼 데이터의 17번째 바이트가 `:` 가 아니면 옛 방식으로 암호화한 값입니다[21].

## 읽는 법

파일 형식은 앞부분 몇 바이트로 구분합니다. 확장자가 없거나 바뀐 파일도 이 방법으로 찾을 수 있습니다.

| 파일 앞부분 | 판단 |
|---|---|
| SQLite 파일 머리, 표 `main(key, value)` 하나 | Bitcoin Core descriptor 지갑[7] |
| `SECO` | Exodus 보안 컨테이너[20] |
| `QklFM` 로 시작하는 base64 텍스트 | Electrum 파일 전체 암호화. `BIE1`·`BIE2` 는 base64 로 `QklFMQ`·`QklFMg` 가 됩니다[14] |
| `{` 로 시작하고 `seed_version`·`wallet_type` 필드 | Electrum 평문 JSON[15] |
| `{` 로 시작하고 `crypto`·`version: 3` 필드 | 이더리움 keystore[17] |
| `{"data":` 로 시작하고 `iv`·`salt` 필드 | MetaMask 볼트 형식[22] |
| `{"data":{` 로 시작하고 `settings`·`accounts` 같은 키 | Ledger Live 네임스페이스 파일(`app.json` 등)[21] |

아래는 secure-container 코드의 머리 구조대로 만든 SECO 파일 앞부분입니다. `ExampleApp`·`1.0.0` 은 만든 예시 값입니다.

```
00000000  53 45 43 4f 00 00 00 00  00 00 00 00 12 73 65 63  |SECO.........sec|
00000010  6f 2d 76 30 2d 73 63 72  79 70 74 2d 61 65 73 0a  |o-v0-scrypt-aes.|
00000020  45 78 61 6d 70 6c 65 41  70 70 05 31 2e 30 2e 30  |ExampleApp.1.0.0|
00000030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
```

0x0C 의 `12` 는 뒤따르는 `seco-v0-scrypt-aes` 의 길이(18바이트)이고, 0x1F 의 `0a` 와 0x2A 의 `05` 가 각각 앱 이름과 앱 버전의 길이입니다.

Bitcoin Core SQLite 지갑은 사본을 SQLite 도구로 열고 `main` 표의 키를 16진으로 봅니다. 첫 바이트가 레코드 종류 문자열의 길이이므로, 그 길이만큼 읽으면 `tx`·`name`·`walletdescriptor` 같은 종류가 나오고 나머지가 레코드별 식별자입니다. `name` 레코드의 키에는 주소 문자열이, 값에는 라벨이 들어 있어 사용자가 붙인 이름을 바로 읽을 수 있습니다[8]. 비트코인 해시는 16진으로 표시할 때 흔히 바이트 순서를 뒤집으므로[25], 키에서 읽은 트랜잭션 ID 를 블록 탐색기 값과 대조할 때는 두 순서를 모두 확인합니다. SQLite 형식 자체는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/) 페이지에서 다룹니다.

MetaMask 볼트는 LevelDB 안의 값이라 LevelDB 를 읽는 도구로 먼저 꺼내야 합니다. LevelDB 구조는 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)와 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) 페이지에서 다룹니다.

## 포렌식에서 중요한 점

### 증명하는 것 / 증명하지 못하는 것

지갑 파일로 증명할 수 있는 것은 그 기기에 특정 지갑 프로그램의 지갑이 있었다는 사실과 그 형식·버전입니다. SECO 머리의 `appName`·`appVersion`, Electrum 의 `seed_version`, Bitcoin Core 의 레코드 종류로 형식과 대략의 버전을 확인할 수 있습니다. 평문 부분의 주소·xpub·거래·라벨로는 그 지갑이 관리한 주소 목록을 얻고, 이 주소를 블록체인과 대조할 수 있습니다.

증명하지 못하는 것도 분명합니다. 암호화된 부분을 열지 않은 상태로는 파일에 개인 키가 실제로 들어 있는지, 누가 암호를 알았는지를 증명할 수 없습니다. 주소가 파일에 있다고 그 주소로 돈이 오갔다는 뜻도 아니므로, 사용 여부는 블록체인 기록으로 따로 확인합니다. 파일의 수정 시각은 거래 시각이 아닙니다.

### 시각 해석

| 값 | 기준 |
|---|---|
| Bitcoin Core descriptor 의 `creation_time` | descriptor 를 만들 때의 기기 시스템 시계, UNIX 초[10][11] |
| Bitcoin Core 트랜잭션의 `nTimeReceived` | 지갑이 트랜잭션을 처음 넣은 순간의 기기 시스템 시계[11]. 블록 시각과 다릅니다 |
| Electrum `verified_tx3` 의 시각 | 트랜잭션이 담긴 블록의 시각이고 기기 시각이 아닙니다[12][15] |
| geth·clef keystore 파일 이름 | `Z` 가 붙은 UTC 시각[18] |
| trust-keystore 파일 이름 | 기기 시간대 기준. 아래 함정 참고[19] |
| Bitcoin Core 이전 백업 파일 이름 | 이전한 순간의 UNIX 초[11] |

블록 시각과 기기 시각의 차이는 [블록 시각과 확정](../blockchain/block-time.md)에서 다룹니다.

### 지운 데이터·손상·비정상 종료

지갑 파일 옆에 남는 파일이 지갑 본체만큼 중요합니다. Bitcoin Core SQLite 지갑의 `wallet.dat-journal` 은 보통 실행할 때 생기고 종료할 때 지워지므로, 이 파일이 남아 있으면 프로그램이 비정상 종료했을 가능성이 있습니다[1]. Berkeley DB 지갑은 `database/` 폴더의 로그 파일이 같은 역할을 합니다[1]. 지갑 파일은 `backupwallet` 호출로 복사해야 하고, 실행 중에 그냥 복사하면 복사하는 동안 바뀐 내용 때문에 복사본이 손상될 수 있습니다[1]. 실행 중인 시스템에서 수집할 때는 이 점을 기록해 둡니다.

지갑을 legacy 에서 descriptor 로 옮기면 지갑 디렉터리(보통 `wallets/`)에 이전 전 백업이 남고, `이름_watchonly`·`이름_solvables` 지갑이 새로 생길 수 있습니다[2]. 백업 파일에는 이전 전 레코드가 그대로 들어 있습니다. Electrum 은 저장할 때 `원래경로.tmp.프로세스ID` 임시 파일에 먼저 쓰고 원래 파일과 바꾸므로, 저장 도중 끊겼다면 임시 파일이 남을 수 있습니다[14]. MetaMask 의 LevelDB 에서는 덮어쓴 옛 볼트가 함께 나오는 경우가 있어서, 한 확장 폴더에서 볼트가 여러 개 나오면 과거에 다른 지갑을 썼을 가능성을 봅니다[24].

Bitcoin Core 는 지갑을 암호화하면 키풀을 비우고 새 HD 시드를 만듭니다[2]. 그래서 암호화 전에 만든 백업과 현재 지갑이 파생하는 주소가 다르고, 두 파일을 비교하면 암호화 시점 전후의 주소를 나눠 볼 수 있습니다.

## 함정

- **"암호화된 지갑이라 볼 것이 없다" 는 틀린 판단입니다.** Bitcoin Core 와 키스토어 암호만 건 Electrum 은 비밀 부분만 암호화해서 주소·거래·라벨이 평문으로 남습니다[2][16]. 이더리움 keystore 도 개인 키만 암호화하고[17], Ledger Live 는 암호 잠금을 켜도 `accounts`·`trustchain`·`wallet` 밖의 `settings`·`knownDevices` 같은 키가 평문입니다[21].
- **Windows 의 Bitcoin Core 데이터 폴더는 두 곳입니다.** 28.0 부터 기본값이 `AppData\Local\Bitcoin` 이지만 옛 `AppData\Roaming\Bitcoin` 이 있으면 그 폴더를 계속 씁니다[5]. 그래서 두 폴더를 모두 확인합니다.
- **legacy 이전 백업 파일 이름은 문서와 코드가 다릅니다.** 문서에는 `이름-타임스탬프.legacy.bak` 으로 나와 있지만[2], 코드는 `%s_%d.legacy.bak`(밑줄, UNIX 초) 형식으로 만듭니다[11]. 실제 파일은 `*.legacy.bak` 으로 찾습니다.
- **keystore 파일 이름의 `UTC--` 가 UTC 를 보장하지 않습니다.** trust-keystore 는 코드 주석에는 "UTC ISO8601" 로 나와 있지만 실제로는 기기 시간대로 시각을 만들고, UTC 가 아니면 끝에 분 단위 오프셋 뒤에 `00` 을 붙인 숫자를 씁니다[19]. 코드대로라면 한국 표준시(+540분)에서는 `54000` 이 붙습니다.
- **주소 필드는 있을 수도 없을 수도 있습니다.** v3 명세 keystore 에는 주소가 없고[17], geth·clef 는 파일 이름에, trust-keystore 는 JSON 에 주소를 넣습니다[18][19]. 주소가 없는 keystore 는 앱의 다른 데이터에서 주소를 찾습니다.
- **Electrum 파일은 두 방식의 암호화가 따로 있습니다.** 키스토어 암호만 건 파일은 JSON 이 그대로 보이고, 파일 전체를 암호화하면 base64 덩어리만 보입니다[14][16].
- **30.0 이상 Bitcoin Core 로는 Berkeley DB 지갑을 열 수 없습니다.** legacy 지갑은 그보다 낮은 버전이나 Berkeley DB 를 읽는 도구로 엽니다. `migratewallet` 은 지갑을 새 형식으로 옮기는 명령이라 증거물 원본에는 쓰지 않습니다[2][6].

## 도구

형식 확인에는 헥스 편집기, JSON 뷰어, SQLite 를 읽는 도구로 충분합니다. SECO 매직, base64 `QklFM`, SQLite 파일 머리처럼 앞부분만 보면 형식이 구분됩니다. MetaMask 볼트는 LevelDB 를 읽는 도구로 값을 꺼낸 뒤 JSON 으로 봅니다. 기기에서 지갑 파일을 찾는 순서는 [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md)에서 다룹니다.

## 참고 문헌

1. Bitcoin Core, "Bitcoin Core file system" (doc/files.md). https://github.com/bitcoin/bitcoin/blob/master/doc/files.md
2. Bitcoin Core, "Managing the Wallet" (doc/managing-wallets.md). https://github.com/bitcoin/bitcoin/blob/master/doc/managing-wallets.md
3. Bitcoin Core 0.21.0 release notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-0.21.0.md
4. Bitcoin Core 23.0 release notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-23.0.md
5. Bitcoin Core 28.0 release notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-28.0.md
6. Bitcoin Core 30.0 release notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-30.0.md
7. Bitcoin Core, src/wallet/sqlite.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/sqlite.cpp
8. Bitcoin Core, src/wallet/walletdb.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/walletdb.cpp
9. Bitcoin Core, src/wallet/crypter.h. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/crypter.h
10. Bitcoin Core, src/wallet/walletutil.h. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/walletutil.h
11. Bitcoin Core, src/wallet/wallet.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/wallet.cpp
12. Electrum, electrum/util.py (`user_dir`). https://github.com/spesmilo/electrum/blob/master/electrum/util.py
13. Electrum, electrum/simple_config.py. https://github.com/spesmilo/electrum/blob/master/electrum/simple_config.py
14. Electrum, electrum/storage.py. https://github.com/spesmilo/electrum/blob/master/electrum/storage.py
15. Electrum, electrum/wallet_db.py. https://github.com/spesmilo/electrum/blob/master/electrum/wallet_db.py
16. Electrum, electrum/keystore.py. https://github.com/spesmilo/electrum/blob/master/electrum/keystore.py
17. ethereum.org, "Web3 secret storage definition". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/data-structures-and-encoding/web3-secret-storage/index.md
18. ethereum.org, "Ethereum accounts". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/accounts/index.md
19. Trust Wallet, trust-keystore (Sources/KeyStore.swift, KeystoreKey.swift, Account.swift). https://github.com/trustwallet/trust-keystore/blob/master/Sources/KeyStore.swift
20. Exodus, secure-container (src/header.js, src/file.js, src/metadata.js). https://github.com/ExodusMovement/secure-container/blob/master/src/header.js
21. Ledger, ledger-live-desktop (src/main/db/index.ts, crypto.ts). https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/main/db/index.ts
22. MetaMask, browser-passworder (src/index.ts). https://github.com/MetaMask/browser-passworder/blob/main/src/index.ts
23. MetaMask, KeyringController.ts. https://github.com/MetaMask/core/blob/main/packages/keyring-controller/src/KeyringController.ts
24. btcrecover, "Extract Scripts" (docs/Extract_Scripts.md). https://github.com/3rdIteration/btcrecover/blob/master/docs/Extract_Scripts.md
25. Bitcoin Developer Guide, "Block Chain". https://developer.bitcoin.org/devguide/block_chain.html
