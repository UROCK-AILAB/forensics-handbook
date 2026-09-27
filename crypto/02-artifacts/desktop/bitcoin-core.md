---
title: "Bitcoin Core"
parent: "아티팩트 · 데스크톱 지갑"
nav_order: 120
---

# Bitcoin Core

Bitcoin Core 는 비트코인 노드와 지갑을 한 프로그램으로 묶은 소프트웨어라, 설치한 기기에는 지갑 파일 `wallet.dat` 뿐 아니라 로그 `debug.log`, 설정 파일, 블록 데이터가 한 데이터 폴더에 함께 남습니다. 지갑 파일은 암호를 걸어도 개인 키만 암호화되므로 트랜잭션 원문, 주소록과 라벨, 주소를 만드는 규칙(descriptor)과 그 생성 시각을 암호 없이 읽을 수 있습니다[2][5]. 이 페이지는 이 기록들이 어디에 어떤 모양으로 있고, 어떤 시각을 담고 있으며, 무엇까지 증명하는지를 다룹니다.

## 무엇을 기록하나 · 왜 생기나

Bitcoin Core 지갑은 자기 주소와 관련된 트랜잭션을 찾으면 그 트랜잭션을 통째로 지갑 파일에 저장합니다[5][6]. 사용자가 받는 주소에 붙인 라벨, 보낼 상대 주소를 주소록에 넣은 기록, 금액·메시지를 담은 받기 요청(receive request)도 같은 파일에 들어갑니다[5][11]. 라벨 같은 메타데이터는 블록체인을 다시 스캔해도 되살릴 수 없어서[2], 이 정보는 지갑 파일과 그 백업에서만 나옵니다.

노드 기능 때문에 생기는 파일도 있습니다. 프로그램은 데이터 폴더의 `debug.log` 에 지갑 불러오기와 닫기, 트랜잭션 추가, 지갑 암호화 같은 사건을 시각과 함께 적습니다[1][7]. 블록 파일(`blocks/`), 피어 목록(`peers.dat`), 메모리풀 덤프(`mempool.dat`)도 데이터 폴더에 쌓입니다[1]. 지갑 파일과 암호화 방식의 공통 요약은 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md)에 있고, 여기서는 Bitcoin Core 에만 해당하는 세부를 씁니다.

## 위치와 버전별 차이

데이터 폴더의 기본 위치는 Linux `$HOME/.bitcoin/`, macOS `$HOME/Library/Application Support/Bitcoin/`, Windows `%LOCALAPPDATA%\Bitcoin\` 입니다[1]. Windows 기본값은 28.0 에서 `AppData\Roaming\Bitcoin` 에서 `AppData\Local\Bitcoin` 으로 바뀌었고, 옛 Roaming 폴더가 있으면 그 폴더를 계속 씁니다[18]. 그래서 27.x 이하로 처음 설치한 PC 는 28.0 이후 버전을 써도 Roaming 에 데이터가 있을 수 있고, Windows 에서는 두 폴더를 모두 확인합니다.

`bitcoin.conf` 를 뺀 데이터 폴더 내용은 체인마다 따로 있습니다[1].

| 체인 | 데이터가 있는 곳 |
|---|---|
| 메인넷 | 데이터 폴더 바로 아래 |
| testnet3 | `testnet3/` |
| testnet4 | `testnet4/` |
| signet | `signet/`, 사용자 signet 은 `signet_XXXXXXXX/`(메시지 시작 바이트) |
| regtest | `regtest/` |

이름을 붙인 지갑은 `wallets/지갑이름/` 에 있고, 이름 없는 기본 지갑은 `wallets/` 에 있으며, `wallets/` 폴더가 없으면 데이터 폴더 바로 아래에 있습니다[1]. `-datadir`·`-walletdir`·`-wallet` 옵션으로 이 위치를 모두 바꿀 수 있습니다[1][2]. 0.21 부터는 기본 지갑을 자동으로 만들지 않고, 사용자가 `createwallet` 이나 GUI 메뉴로 이름을 정해 만듭니다[2]. 그래서 최근 버전에서는 폴더 이름이 곧 사용자가 정한 지갑 이름입니다.

지갑 파일의 형식은 버전에 따라 다릅니다.

| 버전 | 지갑 파일 |
|---|---|
| 0.13 이전 | HD 가 아닌 지갑. 키 100개를 쓸 때마다 새 백업이 필요했습니다[2] |
| 0.21.0 | descriptor 지갑 도입. descriptor 지갑은 SQLite, legacy 지갑은 Berkeley DB(BDB)[16] |
| 23.0 | 새 지갑의 기본 종류가 descriptor 지갑[17] |
| 30.0 | BDB legacy 지갑은 만들거나 열 수 없고 `migratewallet` 으로 옮기기만 합니다. `dumpwallet`·`importprivkey` 등 legacy 전용 명령이 빠집니다[19] |

같은 폴더에 함께 있는 파일도 형식마다 다릅니다. SQLite 지갑은 `wallet.dat` 와 롤백 저널 `wallet.dat-journal` 이고, 저널은 보통 시작할 때 생겼다가 종료할 때 지워집니다[1]. BDB 지갑은 `wallet.dat`, BDB 로그 폴더 `database/`(시작 때 생기고 종료 때 지움), BDB 오류 파일 `db.log`, BDB 지갑 잠금 파일 `.walletlock` 입니다[1].

데이터 폴더에서 지갑 말고 볼 파일은 아래와 같습니다[1].

| 파일 | 내용 |
|---|---|
| `debug.log` | bitcoind·bitcoin-qt 의 로그. `-debuglogfile` 로 위치를 바꿀 수 있습니다 |
| `settings.json` | GUI·RPC 로 바꾼 설정. 시작할 때 불러올 지갑 이름 목록 `wallet` 이 들어갑니다[7] |
| `bitcoin.conf` | 사용자가 직접 만드는 설정 파일. 프로그램은 이 파일에 쓰지 않습니다 |
| `peers.dat`, `banlist.json`, `anchors.dat` | 피어 주소, 차단 목록, 종료 때 만들고 시작 때 지우는 앵커 피어 |
| `mempool.dat` | 메모리풀 트랜잭션 덤프 |
| `.cookie`, `bitcoind.pid`, `.lock` | RPC 인증 쿠키와 프로세스 ID(둘 다 시작 때 만들고 종료 때 지움), 데이터 폴더 잠금 |
| `onion_v3_private_key`, `i2p_private_key` | Tor·I2P 로 접속할 때 쓰는 노드 자신의 키 |
| `blocks/blkNNNNN.dat`, `blocks/revNNNNN.dat`, `blocks/xor.dat` | 블록(파일당 128 MiB), 되돌리기 데이터, XOR 패턴 |
| `blocks/index/`, `chainstate/`, `indexes/txindex/` | LevelDB 블록 색인, UTXO 상태, 선택 항목인 트랜잭션 색인 |

GUI(bitcoin-qt)는 Qt 의 QSettings 로 설정을 저장합니다[1]. 조직 이름은 `Bitcoin`, 도메인은 `bitcoin.org`, 앱 이름은 `Bitcoin-Qt` 이고, 시험망은 `Bitcoin-Qt-testnet`·`Bitcoin-Qt-testnet4`·`Bitcoin-Qt-signet`·`Bitcoin-Qt-regtest` 입니다[15]. QSettings 규칙대로라면 Windows 는 레지스트리 `HKEY_CURRENT_USER\Software\Bitcoin\Bitcoin-Qt`, Linux 는 `$HOME/.config/Bitcoin/Bitcoin-Qt.conf` 에 저장되고, macOS 는 `$HOME/Library/Preferences/` 의 plist 에 도메인으로 정한 이름으로 저장됩니다[20]. 실제 기기에서 이 위치를 열어 확인합니다. 설정 키 `strDataDir` 에는 GUI 를 처음 실행할 때 고른 데이터 폴더가 들어가서[15], 데이터 폴더를 외장 드라이브 같은 기본값 밖으로 옮긴 경우 이 값으로 찾습니다.

## 구조

### 지갑 파일 판별

Bitcoin Core 는 파일 앞부분으로 지갑 형식을 판별합니다[10]. SQLite 지갑은 첫 16바이트가 `SQLite format 3` 과 0x00 이고, 오프셋 68 의 4바이트(SQLite 의 application_id)가 그 체인의 메시지 시작 바이트와 같아야 합니다[10][9]. BDB 지갑은 파일이 4,096바이트 이상이고 오프셋 12 의 4바이트가 `00 05 31 62` 또는 `62 31 05 00` 입니다[10]. SQLite 지갑의 `user_version` 은 0 입니다[9].

| 체인 | 메시지 시작 바이트(오프셋 68) |
|---|---|
| 메인넷 | `F9 BE B4 D9` |
| testnet3 | `0B 11 09 07` |
| testnet4 | `1C 16 3F 28` |
| regtest | `FA BF B5 DA` |
| signet | challenge 값에서 계산 |

메시지 시작 바이트는 체인마다 정해져 있어서[14], 오프셋 68 만 보면 메인넷 지갑인지 시험망 지갑인지 알 수 있습니다. 폴더 위치와 맞지 않는 지갑 파일을 골라낼 때 이 값을 씁니다.

### 레코드

SQLite 지갑에는 `main(key BLOB PRIMARY KEY NOT NULL, value BLOB NOT NULL)` 표 하나만 있고[9], BDB 지갑도 같은 키·값 레코드를 씁니다[5]. 키는 레코드 종류 문자열(길이 1바이트와 문자열) 뒤에 대상 식별자가 붙는 모양입니다[5]. 레코드 종류 전체 목록과 암호화 관련 레코드(`mkey`·`walletdescriptorckey` 등)는 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md)에 있습니다. 조사에서 자주 읽는 레코드는 아래와 같습니다.

| 레코드 | 키 | 값 |
|---|---|---|
| `name` | 주소 문자열 | 라벨 문자열[5] |
| `purpose` | 주소 문자열 | `receive`·`send`, 옛 지갑에만 있는 `refund`[5][11] |
| `destdata` | 주소, `used` | avoid_reuse 옵션을 켠 상태에서 이미 돈을 꺼내 쓴 자기 주소 표시[5] |
| `destdata` | 주소, `rr` 과 번호 | 이 지갑 주소로 만든 받기 요청. 금액·메시지 같은 BIP21 URI 정보가 들어 있습니다[5][11] |
| `tx` | 트랜잭션 ID | 트랜잭션 원문과 지갑 정보(아래 표)[5][6] |
| `wtxvariant` | 트랜잭션 ID, 위트니스 트랜잭션 ID | 같은 트랜잭션의 위트니스 변형 원문[5] |
| `lockedutxo` | 트랜잭션 ID, 출력 번호 | `'1'`. 사용자가 잠근 출력[5] |
| `walletdescriptor` | descriptor ID | descriptor 문자열, `creation_time`, `next_index`, `range_start`, `range_end`[5][8] |

`purpose` 는 지갑 동작에는 쓰이지 않고 RPC·GUI 에 보여 주려고 저장하는 값이라, 사실상 그 주소가 이 지갑의 주소인지와 같은 정보입니다[11]. 주소록 항목은 보내는 주소에서만 지우고, 거스름돈 주소가 아닌 받는 주소에는 항상 주소록 항목이 있어야 합니다[5]. 그래서 주소록에는 이 지갑의 받는 주소와 함께 사용자가 넣은 상대방 주소도 들어 있습니다.

`walletdescriptor` 의 descriptor 문자열은 공개형이라 확장 공개 키(xpub)가 평문으로 들어 있습니다[8]. 새 지갑이 만드는 descriptor 는 `pkh(xpub/44h/0h/0h/0/*)`, `sh(wpkh(xpub/49h/0h/0h/0/*))`, `wpkh(xpub/84h/0h/0h/0/*)`, `tr(xpub/86h/0h/0h/0/*)` 네 가지이고, 거스름돈용은 끝이 `/1/*`, 시험망은 코인 자리가 `1h` 입니다[8]. 여기서 xpub 는 지갑 마스터 키의 공개 키입니다[8]. 다른 곳에서 가져온(import) descriptor 에는 `[지문/경로]` 모양의 키 출처가 붙어 있을 수 있습니다[3]. `next_index` 는 다음에 만들 주소의 순번이라[8], 지갑이 이 descriptor 로 주소를 몇 개 내줬는지 알 수 있습니다. xpub 로 주소를 파생하는 방법은 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)에서 다룹니다.

### `tx` 레코드의 값

`tx` 레코드의 값은 아래 순서로 직렬화됩니다[6].

| 순서 | 필드 | 내용 |
|---|---|---|
| 1 | 트랜잭션 | 위트니스를 포함한 원문 |
| 2 | 블록 해시 | 32바이트 |
| 3 | 빈 벡터 | 옛 `vMerkleBranch` 자리 |
| 4 | 블록 안 위치 | int |
| 5 | 빈 벡터 | 옛 `vtxPrev` 자리 |
| 6 | 문자열 맵 (mapValue) | 아래 키 |
| 7 | 메시지·결제 요청 쌍 목록 | `Message`(BIP21 URI 메시지), `PaymentRequest`(BIP70, 옛 지갑) |
| 8 | uint32 0 | 옛 `fTimeReceivedIsTxTime` 자리 |
| 9 | `nTimeReceived` | uint32, 지갑에 들어온 시각 |
| 10 | bool 두 개 | 옛 `fFromMe`·`fSpent` 자리 |

블록 해시와 블록 안 위치의 조합으로 트랜잭션 상태를 알 수 있습니다[6].

| 블록 해시 | 위치 | 상태 |
|---|---|---|
| 0 | 0 | 비활성(미확정·메모리풀 등) |
| 1 | -1 | 사용자가 포기(abandon) |
| 실제 해시 | 0 이상 | 그 블록에서 확정 |
| 실제 해시 | -1 | 그 블록과 충돌 |

문자열 맵에는 `comment`·`to`(사용자가 적은 메모), `replaces_txid`·`replaced_by_txid`(수수료를 올려 바꾼 트랜잭션 관계), `n`(지갑에 들어온 순번), `timesmart`, 늘 빈 값인 `fromaccount` 가 들어갑니다[6]. 2011년 이전 GUI 가 쓰던 `from`·`message` 도 옛 지갑에서 옮겨 온 값이면 남아 있습니다[6].

### `debug.log`

로그 줄 앞에는 `YYYY-MM-DDThh:mm:ssZ` 형식의 UTC 시각이 붙고, 시각 붙이기는 기본으로 켜져 있습니다[12]. `-logtimemicros` 를 켜면 마이크로초까지 적힙니다[12]. 지갑이 적는 줄은 앞에 `[지갑이름]` 이 붙고, 이름 없는 기본 지갑은 `[default wallet]` 입니다[11]. 조사에 쓰는 지갑 로그 문구는 아래와 같습니다.

| 문구 | 뜻 |
|---|---|
| `AddToWallet 트랜잭션ID 상태 트랜잭션상태` | 지갑에 트랜잭션이 들어오거나 바뀜. 상태는 `new`·`update`·`new, update`·`no-change`[7] |
| `CommitTransaction:` 과 뒤따르는 트랜잭션 내용 | 이 지갑이 트랜잭션을 만들어 보냄[7] |
| `Encrypting Wallet with an nDeriveIterations of 숫자` | 지갑 암호화[7] |
| `Wallet passphrase changed to an nDeriveIterations of 숫자` | 지갑 암호 변경[7] |
| `Rescanning last 숫자 blocks (from block 숫자)...` | 재스캔 시작[7] |
| `setKeyPool.size()`, `mapWallet.size()`, `m_address_book.size()` | 지갑을 불러올 때의 키풀·트랜잭션·주소록 개수[11] |
| `Releasing wallet 지갑이름..` | 지갑 닫기[7] |

트랜잭션 상태 자리에는 `InMempool`, `Confirmed (block=블록해시, height=높이, index=위치)` 같은 값이 들어갑니다[6].

## 증거로서 의미

**증명하는 것.** 데이터 폴더와 지갑 폴더가 있으면 그 사용자 프로필에서 Bitcoin Core 로 해당 이름의 지갑을 만들거나 불러왔다는 것을 알 수 있습니다. `tx` 레코드는 이 지갑이 자기와 관련 있다고 판단해 저장한 트랜잭션이고, 원문과 확정 블록 해시가 함께 있습니다[5][6]. `walletdescriptor` 로는 이 지갑이 주소를 만드는 규칙, xpub, 만든 시각, 내준 주소 수를 알 수 있습니다[8]. `name`·`purpose` 는 사용자가 붙인 라벨과 주소록이고, `destdata` 의 `rr` 레코드는 사용자가 만든 받기 요청입니다[5][11]. `debug.log` 로는 지갑을 불러오고 닫은 시각, 트랜잭션이 지갑에 들어온 시각, 지갑을 암호화하거나 암호를 바꾼 시각을 알 수 있습니다[7].

**증명하지 못하는 것.** 지갑 파일만으로는 누가 키를 썼는지 알 수 없습니다. `tx` 에는 비활성·포기·충돌 상태의 트랜잭션도 남으므로[6], 실제로 블록체인에 확정됐는지는 블록 해시로 따로 확인합니다. 주소록의 `send` 주소는 그 주소로 돈을 보냈다는 뜻이 아니라 주소록에 넣었다는 뜻입니다. 개인 키가 암호화된 지갑에서는 파일만으로 개인 키를 쓸 수 있었는지를 증명하지 못합니다. `nTimeReceived`·`creation_time` 은 기기 시계로 적은 값이고 `timesmart` 도 기기 시계를 쓰는 경우가 있어서, 시계를 바꾸면 달라집니다[6][7][8].

보고서에는 "이 기기의 Bitcoin Core 지갑 `wallet-01` 에 이 트랜잭션 ID 의 레코드가 있고, 그 레코드의 블록 해시가 가리키는 블록에 이 트랜잭션이 들어 있다" 처럼 기록으로 확인되는 만큼만 씁니다(지갑 이름은 만든 예시).

## 시각 해석

| 값 | 어디에 | 기준 |
|---|---|---|
| `nTimeReceived` | `tx` 값 9번째 필드 | 지갑에 처음 넣을 때의 기기 시계, UNIX 초[7] |
| `timesmart` | `tx` 값의 문자열 맵 | 아래 규칙으로 조정한 값, UNIX 초[6][7] |
| `creation_time` | `walletdescriptor` 값 | descriptor 를 만들 때의 기기 시계, UNIX 초[8] |
| 로그 줄 앞 시각 | `debug.log` | 기기 시계를 UTC 로 적은 값[12] |
| `.legacy.bak` 파일 이름의 숫자 | 지갑 폴더 | legacy 지갑을 옮긴 순간의 기기 시계, UNIX 초[7] |

`timesmart` 는 지갑 안 순서와 시각 순서가 어긋나지 않게 맞춘 값입니다[6]. 보낸 트랜잭션과 블록 밖에서 받은 트랜잭션은 받은 시각을 쓰고, 재스캔 중에 찾은 트랜잭션은 그 블록까지의 블록 시각 중 가장 늦은 값을 씁니다[7]. 새 블록으로 받은 트랜잭션은 블록 시각과 받은 시각 중 이른 값을 쓰되, 5분 넘게 앞서지 않는 가장 최근 지갑 트랜잭션의 시각보다 이르면 그 시각으로 올립니다[7]. RPC 의 `time` 은 `timesmart` 가 있으면 그 값이고 없으면 `nTimeReceived` 이며, `timereceived` 는 `nTimeReceived`, `blocktime` 은 블록 시각입니다[13][6]. 그래서 GUI·RPC 에 보이는 거래 시각은 실시간으로 받은 거래면 기기 시계에 가깝고, 재스캔으로 찾은 거래면 블록 시각에 가깝습니다. 블록 시각과 기기 시각의 차이는 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에서 다룹니다.

지갑의 생성 시각(birth time)은 이보다 이른 트랜잭션 시각이 나오면 그 시각으로 당겨집니다[7]. 그래서 지갑을 언제 만들었는지는 `creation_time` 과 가장 이른 트랜잭션 시각을 따로 적어 둡니다.

## 함정과 한계

- **암호화 범위를 다르게 보고한 자료가 있습니다.** 공식 문서는 개인 키만 암호화되고 트랜잭션·공개 키·메타데이터는 보인다고 설명합니다[2]. Debono·Sultana 의 시험(Windows 10 22H2 가상 머신, Bitcoin Core v22.0.0)은 암호화한 BDB 지갑의 "모든 데이터가 암호화되어 읽을 수 없었다" 고 보고했습니다[21]. 이 논문은 레코드 단위로 해석한 결과를 싣지 않았으므로, 판단은 레코드를 직접 해석해 확인한 결과로 합니다.
- **지갑 파일이 여러 개일 수 있습니다.** `wallets/` 바로 아래나 데이터 폴더 바로 아래의 `wallet.dat` 는 이름 없는 기본 지갑이고, 이름 있는 지갑마다 폴더가 따로 있습니다[1]. legacy 지갑을 옮기면 `이름_watchonly`·`이름_solvables` 지갑과 `.legacy.bak` 백업이 새로 생길 수 있습니다[2][7]. 백업 파일 이름이 문서와 코드에서 다른 점은 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md)의 함정에 있습니다.
- **백업은 사용자가 정한 이름과 위치에 있습니다.** `backupwallet` 과 GUI 의 Backup Wallet 은 사용자가 고른 경로에 파일을 씁니다[2]. 지갑을 암호화하면 키풀을 비우고 새 HD 시드를 만들기 때문에[2], 암호화 전에 만든 백업과 현재 지갑은 주소 목록이 다릅니다.
- **실행 중에 복사하면 손상될 수 있습니다.** 복사하는 동안 지갑이 갱신되면 파일이 손상될 수 있어서, 지갑 복사와 백업은 `backupwallet` 으로 해야 합니다[1]. `wallet.dat-journal` 이나 `database/` 가 남아 있으면 비정상 종료했을 가능성이 있으므로 함께 수집합니다[1]. 수집 순서는 [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md)에 있습니다.
- **최신 버전으로 옛 지갑을 열면 안 됩니다.** 30.0 이상은 BDB 지갑을 열지 못하고 `migratewallet` 으로 파일을 바꾸게 되어 있습니다[19]. 원본은 읽기 전용 사본으로만 다룹니다.
- **`debug.log` 는 앞부분이 잘립니다.** `-debug` 없이 시작하면 파일이 11,000,000바이트를 넘을 때 마지막 10,000,000바이트만 남깁니다[12]. 잘린 앞부분은 비할당 영역에 남아 있을 가능성이 있고, 찾는 방법은 [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md)에 있습니다.
- **28.0 이후 블록 파일은 XOR 처리됩니다.** 블록 파일은 기본으로 blocksdir 의 키로 XOR 처리되고 그 패턴은 `blocks/xor.dat` 에 있어서[18][1], 블록 파일을 그대로 문자열 검색하면 트랜잭션이 나오지 않을 수 있습니다. 원시 블록을 읽는 방법은 [블록과 트랜잭션](../../01-foundations/blockchain/blocks-transactions.md)에 있습니다.
- **주소 정규식이 `bc1` 주소를 놓칩니다.** KAPE 가 쓰는 bstrings 의 `bitcoin` 정규식은 `\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b` 라서 `1`·`3` 으로 시작하는 주소만 찾습니다[23]. 새 지갑의 `wpkh`·`tr` descriptor 가 만드는 주소는 `bc1` 로 시작하므로([주소 형식](../../01-foundations/wallets/address-formats.md)) 따로 검색합니다.
- **제거해도 데이터 폴더는 남습니다.** Debono·Sultana 의 시험에서는 제어판으로 Bitcoin Core 를 제거한 뒤 설치 프로그램 목록과 Program Files 에서는 사라졌지만, Roaming 의 `Bitcoin\` 폴더(지갑 폴더와 이름, 피어·메모리풀 파일, 블록과 색인 폴더)는 남았습니다[21]. 같은 시험에서 제거 직후 재부팅 전의 메모리에서 지갑 암호가 나왔고, 재부팅 뒤에는 폴더 경로 이름만 나왔습니다[21]. 메모리 분석 방법은 [메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 위 판별 규칙대로 만든 메인넷 SQLite 지갑의 앞부분입니다(명세로 만든 예시). 설명과 관계없는 바이트는 `..` 로 줄였습니다.

```
00000000  53 51 4c 69 74 65 20 66  6f 72 6d 61 74 20 33 00  |SQLite format 3.|
...
00000040  .. .. .. ..  f9 be b4 d9  .. .. .. ..  .. .. .. ..  |....|
```

0x44(오프셋 68)의 `f9 be b4 d9` 가 메인넷 메시지 시작 바이트라 메인넷 지갑입니다[10][14]. 이 네 바이트가 `1c 16 3f 28` 이면 testnet4 지갑입니다.

다음은 `name` 레코드의 키와 값을 지갑의 직렬화 규칙대로 만든 예시입니다[5]. 주소는 BIP-173 에 실린 메인넷 P2WPKH 시험 벡터이고[24], 라벨 `exchange` 는 만든 예시입니다.

```
키:  04 6e 61 6d 65 2a 62 63 31 71 77 35 30 38 64 36 71 65 6a 78
     74 64 67 34 79 35 72 33 7a 61 72 76 61 72 79 30 63 35 78 77
     37 6b 76 38 66 33 74 34
값:  08 65 78 63 68 61 6e 67 65
```

키의 `04` 는 뒤따르는 `name` 의 길이, `2a`(42) 는 주소 `bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4` 의 길이입니다. 값의 `08` 은 라벨 길이이고 뒤 8바이트가 `exchange` 입니다. 같은 주소의 `purpose` 레코드는 키가 `07 70 75 72 70 6f 73 65 2a …` 로 시작하고, 상대방 주소면 값이 `04 73 65 6e 64`(`send`) 입니다. `tx` 레코드의 키는 `02 74 78` 뒤에 트랜잭션 ID 32바이트가 내부 바이트 순서로 붙으므로, 블록 탐색기에 넣을 때는 바이트를 뒤집습니다. 바이트 순서는 [블록과 트랜잭션](../../01-foundations/blockchain/blocks-transactions.md)에서 다룹니다.

### 공개 도구로 한 번

SQLite 지갑은 사본을 SQLite 명령줄 도구나 SQLite 뷰어로 열고 `main` 표를 16진으로 봅니다. `SELECT hex(key), hex(value) FROM main;` 으로 전체를 꺼낸 뒤 키 앞머리로 레코드 종류를 나누면 위 표대로 읽을 수 있습니다. SQLite 형식은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/)(macOS 는 [SQLite](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/data-formats/sqlite/))에서 다룹니다. BDB 지갑은 Berkeley DB 를 읽는 도구로 키·값 쌍을 꺼내면 같은 방식으로 읽힙니다. 설치본에 들어 있는 `bitcoin-wallet` 은 지갑 도구이지만[1], 증거 원본에는 쓰지 않고 사본에만 씁니다.

`debug.log` 는 텍스트라 `AddToWallet`·`CommitTransaction`·`Encrypting Wallet` 으로 검색하면 됩니다. 아래는 로그 형식대로 만든 예시 줄입니다(트랜잭션 ID·블록 해시·높이·지갑 이름·시각은 만든 예시).

```
2026-03-02T01:15:42Z [wallet-01] AddToWallet b39f0fba1ee0401ba294b87bd84925a751c11a880ce4834c1007abf700aaacb1 new InMempool
2026-03-02T01:24:07Z [wallet-01] AddToWallet b39f0fba1ee0401ba294b87bd84925a751c11a880ce4834c1007abf700aaacb1 update Confirmed (block=00000000000000000001d7798bab3372eac4715625819b4a0eb7b71749be51aa, height=940000, index=17)
```

첫 줄은 트랜잭션이 확정 전에 지갑에 들어온 시각이고, 둘째 줄은 블록에 들어간 것을 지갑이 알게 된 시각입니다. 둘 다 기기 시계를 UTC 로 적은 값이라, 블록 시각은 블록 해시로 따로 확인합니다.

## 교차 검증

- **블록체인:** `tx` 레코드와 로그의 트랜잭션 ID 로 블록 시각과 확정 여부를 확인합니다. 방법은 [블록 탐색기 기록 읽기](../records/block-explorers.md)와 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에 있습니다.
- **거래소:** 주소록의 `send` 주소와 보낸 트랜잭션의 출력 주소가 거래소 입금 주소인지는 [거래소로 들어갔나](../../04-scenarios/asset-flow/exchange-deposit.md)의 순서로 확인합니다.
- **거래 모양:** nVersion·nLockTime·RBF 같은 값의 기본 설정으로 어느 지갑 소프트웨어가 트랜잭션을 만들었는지 추정하는 연구가 있습니다[22]. Bitcoin Core 는 RPC 로 트랜잭션을 만들 때 다른 값을 쓴다는 보고도 있어서[22], 이 방법은 확률로만 판단합니다. 자세한 내용은 [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md)에 있습니다.
- **오프라인 서명:** 개인 키를 둔 오프라인 기기와 watch-only 지갑을 둔 온라인 기기를 나눠 쓰고, 부분 서명 트랜잭션(PSBT)과 지갑 파일을 USB 드라이브 같은 매체로 옮기는 사용법이 있습니다[4]. 온라인 PC 에 개인 키 없는 지갑만 있으면 다른 기기와 저장 매체를 찾습니다. 저장 매체 연결 흔적은 [USB 저장장치 흔적](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/external-devices/usb-storage-artifacts/)에서 다룹니다.
- **실행 흔적과 타임라인:** 설치·실행 흔적과 `debug.log`·레코드 시각을 합치는 방법은 [암호화폐 타임라인](../../03-techniques/analysis/timeline.md)과 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/)에 있습니다. 기기에서 지갑을 썼는지 판단하는 흐름은 [이 기기로 지갑을 썼나](../../04-scenarios/device-use/wallet-use.md)에 있습니다.

## 실습

signet 이나 regtest 로 시험 지갑을 만들면 실제 자산 없이 흔적을 만들어 볼 수 있습니다.

1. `-signet` 으로 이름 있는 지갑을 만들고 `signet/wallets/지갑이름/wallet.dat` 의 오프셋 68 네 바이트를 봅니다. `-regtest` 로 만든 지갑과 값이 어떻게 다른가요?
2. 받기 탭에서 라벨·금액·메시지를 넣어 결제 요청을 만든 뒤, `destdata` 의 `rr` 레코드와 `name` 레코드에 무엇이 남는지 확인합니다.
3. 시험 코인을 받은 뒤 `debug.log` 의 `[지갑이름] AddToWallet` 줄 시각과 `gettransaction` 의 `timereceived`·`time`·`blocktime` 을 비교합니다.
4. 지갑을 암호화한 뒤 `walletdescriptorkey` 레코드가 `walletdescriptorckey` 로 바뀌는지, `tx`·`name` 레코드는 그대로 읽히는지 확인합니다.
5. 기기 시계를 몇 시간 앞당긴 채 트랜잭션을 받고 다시 되돌린 뒤, `nTimeReceived`·`timesmart`·블록 시각이 어떻게 달라지는지 봅니다.

## 참고 문헌

1. Bitcoin Core, "Bitcoin Core file system" (doc/files.md). https://github.com/bitcoin/bitcoin/blob/master/doc/files.md
2. Bitcoin Core, "Managing the Wallet" (doc/managing-wallets.md). https://github.com/bitcoin/bitcoin/blob/master/doc/managing-wallets.md
3. Bitcoin Core, "Support for Output Descriptors in Bitcoin Core" (doc/descriptors.md). https://github.com/bitcoin/bitcoin/blob/master/doc/descriptors.md
4. Bitcoin Core, "Offline Signing Tutorial" (doc/offline-signing-tutorial.md). https://github.com/bitcoin/bitcoin/blob/master/doc/offline-signing-tutorial.md
5. Bitcoin Core, src/wallet/walletdb.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/walletdb.cpp
6. Bitcoin Core, src/wallet/transaction.h, src/wallet/transaction.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/transaction.h , https://github.com/bitcoin/bitcoin/blob/master/src/wallet/transaction.cpp
7. Bitcoin Core, src/wallet/wallet.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/wallet.cpp
8. Bitcoin Core, src/wallet/walletutil.h, src/wallet/walletutil.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/walletutil.h , https://github.com/bitcoin/bitcoin/blob/master/src/wallet/walletutil.cpp
9. Bitcoin Core, src/wallet/sqlite.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/sqlite.cpp
10. Bitcoin Core, src/wallet/db.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/db.cpp
11. Bitcoin Core, src/wallet/types.h, src/wallet/wallet.h. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/types.h , https://github.com/bitcoin/bitcoin/blob/master/src/wallet/wallet.h
12. Bitcoin Core, src/logging.cpp, src/logging.h, src/util/time.cpp, src/init/common.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/logging.cpp , https://github.com/bitcoin/bitcoin/blob/master/src/logging.h , https://github.com/bitcoin/bitcoin/blob/master/src/util/time.cpp , https://github.com/bitcoin/bitcoin/blob/master/src/init/common.cpp
13. Bitcoin Core, src/wallet/rpc/transactions.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/rpc/transactions.cpp
14. Bitcoin Core, src/kernel/chainparams.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/kernel/chainparams.cpp
15. Bitcoin Core, src/qt/guiconstants.h, src/qt/intro.cpp, src/qt/bitcoin.cpp, src/qt/networkstyle.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/qt/guiconstants.h , https://github.com/bitcoin/bitcoin/blob/master/src/qt/intro.cpp , https://github.com/bitcoin/bitcoin/blob/master/src/qt/bitcoin.cpp , https://github.com/bitcoin/bitcoin/blob/master/src/qt/networkstyle.cpp
16. Bitcoin Core 0.21.0 release notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-0.21.0.md
17. Bitcoin Core 23.0 release notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-23.0.md
18. Bitcoin Core 28.0 release notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-28.0.md
19. Bitcoin Core 30.0 release notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-30.0.md
20. Qt, "QSettings Class" (Qt 6 문서). https://doc.qt.io/qt-6/qsettings.html
21. David Debono, Aleandro Sultana, "Desktop Crypto Wallets: A Digital Forensic Investigation and Analysis of Remnants and Traces on end-User Machines", Proceedings of the 10th International Conference on Information Systems Security and Privacy (ICISSP 2024), pp. 350-357, 2024. doi:10.5220/0012313000003648
22. Jan Zavřel, Michal Koutenský, Daniel Dolejška, Vladimír Veselý, "Tumbling down the stairs: Exploiting a tumbler's attempt to hide with ordinary-looking transactions using wallet fingerprinting", Forensic Science International: Digital Investigation 52, 301869, 2025. doi:10.1016/j.fsidi.2025.301869
23. bstrings, bstrings/Program.cs; KapeFiles, Modules/EZTools/bstrings/bstrings_BitCoinWallet.mkape. https://github.com/EricZimmerman/bstrings/blob/master/bstrings/Program.cs , https://github.com/EricZimmerman/KapeFiles/blob/master/Modules/EZTools/bstrings/bstrings_BitCoinWallet.mkape
24. BIP-173, "Base32 address format for native v0-16 witness outputs". https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki
