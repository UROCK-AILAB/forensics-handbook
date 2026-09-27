---
title: "iOS 지갑 앱"
parent: "아티팩트 · 모바일 지갑과 거래소 앱"
nav_order: 210
---

# iOS 지갑 앱 (iOS Wallets)

iPhone 에 설치한 자기 보관 지갑 앱은 앱 데이터 컨테이너에 계정 주소, 캐시한 잔액, 트랜잭션 목록, 주소록을 JSON·SQLite·MMKV·Realm 파일로 남깁니다. 이 페이지는 공개 도구 코드와 앱 소스로 구조를 확인할 수 있는 MetaMask Mobile, Coinbase Wallet(현재 이름 Base App), 2018~2019년 공개 소스의 Trust Wallet 을 다루고, 여러 앱이 함께 쓰는 MMKV 형식도 설명합니다. 개인 키와 복구 문구는 암호화된 볼트·키 파일이나 키체인에 있어서 평문으로 보이지 않으므로, 평문으로 남는 주소와 트랜잭션 해시를 블록체인 기록과 대조해 해석합니다.

## 무엇을 기록하나 · 왜 생기나

자기 보관 지갑 (non-custodial wallet)은 키를 기기에 두고, 화면에 보여 줄 계정·잔액·거래 목록을 앱 데이터에 따로 저장합니다([지갑의 종류](../../01-foundations/wallets/wallet-types.md)). 그래서 앱을 열지 않아도 어떤 주소를 만들었거나 가져왔는지, 앱이 어떤 거래를 받아 적었는지를 파일에서 확인할 수 있습니다. 반대로 키 자체는 암호화된 볼트나 키 파일, 또는 키체인 항목으로만 남습니다.

| 앱 | `Documents` 아래 위치 | 형식 | 주로 남는 것 |
|---|---|---|---|
| MetaMask Mobile | `persistStore/` | JSON 파일 | 계정 주소·이름·가져온 시각, 캐시 잔액, 주소록, 트랜잭션, 앱 내 브라우저 기록, 암호화된 볼트[1][3][10] |
| Coinbase Wallet (Base App) | `default/wallet-rn-v2.sqlite`, `mmkv/CBStore.plaintext` | SQLite, MMKV | 계정, 파생 주소와 파생 경로, 자산별 잔액, 거래 내역, 확장 공개 키[13] |
| Trust Wallet (2018~2019 공개 소스) | `keystore/`, Realm 기본 파일과 같은 폴더의 `*.realm` | 키 파일 JSON, Realm | 암호화된 키 파일, 감시 전용 주소, 트랜잭션, DApp 브라우저 기록[20][21] |

## 위치와 버전별 차이

앱 데이터는 `mobile/Containers/Data/Application/` 아래 앱마다 하나씩 있는 UUID 폴더에 있고, iLEAPP 분석기도 `*/mobile/Containers/Data/Application/*/Documents/...` 형식의 경로로 찾습니다[1][13]. UUID 폴더 이름은 앱 이름을 알려 주지 않아서, 번들 ID 와 UUID 의 대응은 [설치된 앱 (applicationState.db)](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/app-usage/installed-apps.html) 에서 확인합니다. Coinbase Wallet 의 번들 ID 는 `org.toshi.distribution` 입니다[13]. MetaMask Mobile 은 프로젝트 설정에 번들 ID 가 `io.metamask.$(PRODUCT_NAME:rfc1034identifier)` 로 적혀 있어서 `io.metamask` 로 시작하는 값이 되고, 완성된 값은 실제 데이터로 확인합니다[12].

### MetaMask Mobile: v7.60.0 을 경계로 저장 방식이 바뀜

MetaMask Mobile 은 상태를 `redux-persist-filesystem-storage` 로 저장하고, 이 라이브러리는 `DocumentDir/persistStore` 폴더에 키 하나당 파일 하나를 씁니다[6]. 파일 이름은 키의 콜론(`:`)을 하이픈(`-`)으로 바꾼 것이라 키 `persist:root` 는 `persist-root` 파일이 됩니다[6]. iOS 에서 `DocumentDir` 은 앱 컨테이너의 `Documents` 폴더입니다[7].

계정·트랜잭션 같은 컨트롤러 상태가 어느 파일에 있는지는 앱 버전에 따라 다릅니다. v7.59.0 까지는 저장 제외 목록(blacklist)에 `engine` 이 없어서 컨트롤러 상태 전체가 `persist-root` 안 `engine` 키에 들어갑니다[4]. v7.60.0 부터는 제외 목록에 `engine` 이 들어가고, 컨트롤러마다 `persist:컨트롤러이름` 키로 파일을 따로 씁니다[3][4]. 2025-10-10 에 병합된 변경(PR #17685)이 이 구조를 도입했고, 2026년 9월 기준 main 브랜치(8.15.0)도 같은 구조입니다[3][5].

| 앱 버전 | 컨트롤러 상태 위치 | iLEAPP `metamask.py` |
|---|---|---|
| v7.59.0 까지 | `persist-root` 의 `engine` → `backgroundState` | 읽음[1] |
| v7.60.0 부터 | `persist-KeyringController`, `persist-TransactionController` 처럼 컨트롤러마다 한 파일 | `engine` 키가 없으면 결과를 내지 않음[1] |

표의 파일 이름은 이름 규칙으로 만든 예이므로, 실제 `persistStore` 폴더 목록으로 확인합니다. 새 구조에서도 제외 목록에 없는 `browser` 같은 다른 상태는 계속 `persist-root` 에 저장됩니다[3].

MetaMask 는 이 라이브러리에 패치를 걸어 iOS 에서 파일을 쓸 때마다 `ReactNativeBlobUtil.ios.excludeFromBackupKey` 를 부릅니다[8]. 그래서 `persistStore` 파일에는 백업 제외 표시가 붙고, iTunes·Finder 백업으로 만든 논리 추출에는 들어가지 않을 수 있습니다. 이 앱을 조사하려면 전체 파일 시스템 추출이 필요합니다([조사 절차](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/acquisition/investigation-process.html)).

### Coinbase Wallet: 앱 버전에 따라 열이 늘어남

Coinbase Wallet 은 현재 Base App 이라는 이름으로 배포됩니다[14]. 같은 회사의 Coinbase 거래소 앱과는 저장소가 다르고, 거래소 앱은 [거래소 앱](exchange-apps.md) 에서 다룹니다[13]. iLEAPP 분석기가 쓴 시험 이미지 두 개(iOS 16.5, iOS 17.5.1) 중 옛 저장소에는 `account` 표의 `mpcConversionState`·`isDeleted`·`hasCompletedBackupFlow` 열과 `wallet` 표의 `isSpam`·`isWhitelist` 열이 없습니다[13]. 거래 내역도 옛 저장소에는 `tx_history` 표가 따로 있고, 새 저장소는 `tx_history_v2` 를 씁니다[13]. SQL 로 직접 읽을 때는 열이 있는지부터 확인합니다.

### Trust Wallet: 공개 소스는 2019년에 멈춤

`trustwallet/trust-wallet-ios` 저장소는 보관(archived) 상태이고 마지막 커밋이 2018-12-10, 키 파일 라이브러리 `trust-keystore` 도 2018-11-25 에 마지막으로 푸시됐습니다[20][21]. 아래 Trust Wallet 구조는 이 시기 앱의 구조이며, 현재 배포되는 앱은 실제 데이터로 폴더와 파일을 확인해야 합니다.

## 구조

### MetaMask Mobile 의 persist-root

`persist-root` 는 JSON 이고, 최상위 키 `engine`·`browser` 의 값이 다시 JSON 문자열입니다[1]. v7.59.0 까지의 구조에서 `engine` 값을 한 번 더 풀면 `backgroundState` 아래에 컨트롤러별 상태가 있습니다[1].

| 위치 | 필드 | 내용 |
|---|---|---|
| `AccountTrackerController.accounts` | 주소별 `balance` | 16진 문자열 wei 잔액. iLEAPP 는 10^18 로 나눠 ETH 로 표시합니다[1] |
| `PreferencesController.identities` | 주소별 `name`, `importTime` | 계정 이름, 가져온 시각[1] |
| `AddressBookController.addressBook` | 체인 ID 아래 `name`, `address` | 사용자가 등록한 주소록[1] |
| `TransactionController.transactions` | `time`, `transaction.from`, `transaction.to`, `transaction.value`, `transactionHash` | 트랜잭션. `value` 는 16진 wei[1] |
| `browser` (최상위 키) | `history[].name`, `history[].url` | 앱 내 브라우저 방문 기록[1] |

v7.60.0 부터는 컨트롤러 파일 하나가 위 표의 컨트롤러 하나에 해당합니다. 앱은 파일을 읽을 때 `_persist` 필드를 빼고 나머지를 그 컨트롤러 상태로 쓰며, 상태가 바뀌면 200ms 디바운스를 거쳐 파일을 다시 씁니다[3]. 새 파일 안의 필드 이름이 위 표와 같은지는 실제 파일로 확인합니다.

### MetaMask Mobile 의 볼트와 키체인

`KeyringController` 상태의 `vault` 필드가 암호화된 볼트 문자열입니다[10]. 모바일 앱은 볼트를 `cipher`, `iv`, `salt`, `lib`, `keyMetadata` 필드가 든 JSON 문자열로 만듭니다[11]. 이 중 `keyMetadata` 에는 키 유도 방식 `PBKDF2` 와 반복 횟수가 들어가고, 반복 횟수는 5,000(`Legacy5000`), 600,000(`OWASP2023Minimum`), 900,000(`OWASP2023Default`) 중 하나입니다[9]. `lib` 는 `original`·`forked`·`quick-crypto` 중 하나이고, 이 태그가 없으면 `forked` 라이브러리로 만든 볼트입니다[9]. 두 값으로 어떤 설정에서 만든 볼트인지 구분할 수 있습니다. 볼트 필드의 공통 형식은 [MetaMask](../browser/metamask/index.md) 페이지에 있습니다.

앱은 이 볼트를 키체인에도 백업합니다. react-native-keychain 의 인터넷 자격 증명으로 서버 이름 `VAULT_BACKUP`, 임시본은 `VAULT_BACKUP_TEMP` 를 쓰고, 접근 속성은 `WHEN_UNLOCKED_THIS_DEVICE_ONLY` 입니다[10]. 앱 비밀번호 관련 항목은 service `com.metamask` 로 같은 접근 속성을 씁니다[15]. 이 접근 속성의 항목은 새 기기로 옮겨지지 않습니다[15]. 키체인 구조와 추출은 [키체인](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/keychain.html) 에서 다룹니다.

### Coinbase Wallet 의 wallet-rn-v2.sqlite

| 표 | 주요 열 | 내용 |
|---|---|---|
| `account` | `id`, `createdAt`, `type`, `primaryAddressChain`, `primaryAddress`, `nickname` | 계정 한 개당 한 행. `type` 은 시험 이미지 두 개 모두 `mnemonic`[13] |
| `wallet_group` | `id`, `accountId`, `createdAt`, `nickname`, `walletIndex`, `isHidden`, `hardwareDerivationPath` | 계정과 이어지는 지갑 묶음[13] |
| `address` | `address`, `indexStr`, `currencyCodeStr`, `networkStr`, `typeStr`, `blockchainStr`, `derivationPath`, `isUsedStr`, `isChangeAddressStr`, `balanceStr`, `contractAddress`, `accountId` | 앱이 파생한 주소와 경로[13] |
| `wallet` | `displayName`, `currencyCodeStr`, `blockchainStr`, `balanceStr`, `decimalsStr`, `primaryAddress`, `contractAddress`, `lastBalanceUpdateTxHash`, `isSpam`, `isWhitelist` | 자산마다 한 행, 잔액은 자산 기본 단위 문자열[13] |
| `tx_history_v2` | `createdAt`, `confirmedAt`, `type`, `state`, `isSent`, `fromAddress`, `toAddress`, `amount`, `fee`, `txHash`, `nonce`, `gasLimit`, `maxFeePerGas`, `walletId` 등 | 거래 내역. 방향은 `isSent` 로 판단[13] |
| `ethereum_signed_tx`, `solana_signed_tx`, `utxo_signed_tx`, `xlm_signed_tx`, `xrp_signed_tx` | 체인마다 다름 | 시험 이미지 두 개 모두 비어 있어 열의 뜻이 확인되지 않은 표[13] |

`address` 표의 파생 인덱스는 시험 이미지 두 개 모두 0~19 였고, 경로는 BIP-44 의 `m / purpose' / coin_type' / account' / change / address_index` 형식입니다[13][17]. 한 주소가 여러 자산 아래에 중복되어서 행 수가 고유 주소 수보다 많습니다(491행에 고유 주소 270개, 406행에 226개)[13]. `typeStr` 에는 `BitcoinSegWit`, `BitcoinLegacy` 같은 앱 자체 라벨이 들어가므로, 주소 형식은 [주소 형식](../../01-foundations/wallets/address-formats.md) 기준으로 다시 판별합니다[13]. 파생 경로의 뜻은 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md) 에 있습니다.

`mmkv/CBStore.plaintext` 는 이름대로 암호화하지 않은 MMKV 저장소라서 키 없이 읽힙니다[13]. 여기에는 `deviceId`, `activeWalletGroupId`, 세션 접근 토큰, 인증 상태 데이터와 함께 `BIP44XpubKey_` 가 들어 있는 키의 확장 공개 키 (extended public key, xpub) 가 있습니다[13]. xpub 키 문자열 안에는 통화, 주소 형식, 계정 주 주소가 쉼표로 이어져 있고, 주 주소는 앱이 대문자로 바꿔 저장합니다[13]. 시험 이미지에는 xpub 항목이 11개와 8개 있었습니다[13]. 확장 공개 키로는 강화되지 않은(non-hardened) 하위 공개 키를 모두 만들 수 있지만 서명은 할 수 없어서, 앱이 이미 만든 20개보다 넓은 주소 범위를 확인하는 데 씁니다[13][16].

### Trust Wallet (2018~2019 공개 소스)

키 파일은 `Documents/keystore/` 폴더에 있고, 파일 이름은 `UTC--시각--식별자` 형식입니다[20][21]. 식별자는 새로 만든 UUID 이고, 시각은 `2019-01-31T09-30-00.000000000Z`(만든 예시) 처럼 쓰는데 오프셋 표기가 표준과 다릅니다(아래 시각 해석)[21]. 파일 내용은 Web3 Secret Storage 형식의 JSON(`crypto` 아래 `ciphertext`, `cipher`, `cipherparams`, `kdf`, `kdfparams`, `mac`, 그리고 `id`, `address`, `version`)이고, 기본값은 `cipher` 가 `aes-128-ctr`, `kdf` 가 `scrypt` 입니다[21][22]. Trust 는 여기에 `type`(`private-key` 또는 `mnemonic`), `coin`, `activeAccounts` 필드를 더하고, 복구 문구 지갑도 같은 JSON 에 암호화해 넣습니다[21]. 키 파일 형식 일반은 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md) 에 있습니다.

키 파일 비밀번호는 지갑마다 키체인에 저장하고, 가져온 지갑에는 앱이 무작위로 만든 비밀번호를 씁니다[20]. 키체인 키는 지갑 식별자, 접근 속성은 `accessibleWhenUnlockedThisDeviceOnly`, iCloud 키체인 동기화는 꺼져 있습니다(`synchronizable = false`)[20]. 최근 사용한 지갑과 주소도 키체인 키 `recentlyUsedWallet`, `recentlyUsedAddress` 로 남깁니다[20].

나머지 데이터는 Realm 데이터베이스에 있습니다. 공유 설정은 `shared.realm`, 지갑별 데이터는 Realm 기본 파일과 같은 폴더에 지갑 정보의 `description` 값을 이름으로 쓴 `.realm` 파일입니다[20]. 키 없이 주소만 등록한 감시 전용 주소 (watch address) 는 `WalletAddress` 객체(`id`, `addressString`, `rawCoin` 필드)로 저장됩니다[20]. `Transaction` 객체에는 `id`, `uniqueID`(보낸 주소와 nonce 를 `-` 로 이은 기본 키), `blockNumber`, `from`, `to`, `value`, `gas`, `gasPrice`, `gasUsed`, `nonce`, `date` 필드가 있습니다[20]. 앱 내 DApp 브라우저는 방문 기록 `History`(`url`, `title`, `createdAt`)와 북마크를 남기지만, 브라우저 기본 주소는 기록하지 않습니다[20].

### MMKV 저장소 형식

MMKV 는 Tencent 가 만든 mmap 기반 키-값 저장소로, iOS 앱이 NSUserDefaults 대신 씁니다[18]. Coinbase Wallet 의 `CBStore.plaintext` 가 이 형식이고, [거래소 앱](exchange-apps.md) 에서 다루는 Coinbase 앱도 같은 형식을 씁니다. Android 에서 쓰는 모습은 [Android 지갑 앱](android-wallets.md) 에 있습니다.

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 데이터 영역의 실제 크기(uint32, 리틀 엔디언)[18] |
| 4 | 1~4 | 뒤따르는 항목 전체 크기(varint)[18] |
| 이어서 | 가변 | 항목의 반복: varint 키 길이, UTF-8 키, varint 값 길이, 값[18] |
| 기록 크기 뒤 | 나머지 | 0 으로 채운 공간, 또는 예전 항목의 흔적[18] |

값의 자료형은 파일에 적혀 있지 않고 앱 코드가 정합니다[18]. MMKV 는 값을 고칠 때 기존 항목을 덮어쓰지 않고 뒤에 새 항목을 붙이므로, 바뀐 키가 여러 번 남고 마지막 항목이 앱이 읽는 값입니다[18]. 값 길이가 0 인 항목은 빈 문자열이 아니라 삭제 표시입니다[18]. 같은 이름에 `.crc` 가 붙은 메타 파일에도 크기 사본(28~32 바이트)이 있고, MMKV 는 메타 버전 3 부터 이 값을 읽습니다[18]. 암호화(AES-CFB) 저장소는 키가 있어야 읽히고, 키는 두 파일 어디에도 없습니다[18].

## 증거로서 의미

**증명하는 것.** 앱 데이터에 주소·xpub·파생 경로가 있으면, 이 기기의 앱이 그 계정을 만들었거나 가져왔다는 것을 알 수 있습니다[13][20]. 트랜잭션 목록의 해시는 블록체인에서 조회해 주소·금액·블록 시각을 확인할 수 있습니다([블록 탐색기 기록 읽기](../records/block-explorers.md)). MetaMask 의 주소록과 앱 내 브라우저 기록은 사용자가 주소를 등록하고 사이트를 방문한 흔적입니다[1]. 키체인에 앱 항목이 있으면 이 앱이 이 기기에서 비밀 값을 저장한 적이 있다는 뜻이고, `THIS_DEVICE_ONLY` 속성 때문에 다른 기기에서 옮겨 온 항목일 가능성은 낮습니다[10][15][20].

**증명하지 못하는 것.** 주소가 있다고 그 주소를 쓰거나 입금받았다는 뜻은 아닙니다[13]. iLEAPP 시험 이미지에서도 `isUsedStr` 가 참인 행은 491행 중 203행, 406행 중 200행이었습니다[13]. Trust Wallet 의 감시 전용 주소처럼 키 없이 주소만 등록한 지갑도 있어서, 지갑 목록에 있다고 키를 가졌다고 볼 수 없습니다[20]. 캐시된 잔액은 앱이 마지막으로 받아 적은 값이고 현재 잔액이 아닙니다[1][13]. `account.type` 의 `mnemonic` 은 앱 라벨이라 키를 어떻게 만들었는지 단정할 근거가 되지 않습니다[13].

보고서에는 "이 기기의 MetaMask 앱 데이터에 주소 0x… 가 계정으로 있고, 이 주소에서 이 시각에 이 금액을 보낸 트랜잭션이 블록체인에 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

| 앱 | 필드 | 형식과 기준 |
|---|---|---|
| MetaMask Mobile | `importTime`, `transactions[].time` | Unix epoch 숫자. 단위가 적혀 있지 않아 iLEAPP 는 값의 크기로 초·밀리초를 판별해 UTC 로 바꿉니다[1][2] |
| Coinbase Wallet | `createdAt`, `confirmedAt` 등 | `YYYY-MM-DD HH:MM:SS[.fff]` 문자열, 시간대 표시 없음. iLEAPP 는 UTC 로 읽습니다[13] |
| Trust Wallet (옛 소스) | `Transaction.date` | 서버 응답의 `timeStamp`(Unix 초)로 만든 값[20] |
| Trust Wallet (옛 소스) | 키 파일 이름의 시각 | 기기 현지 시간대로 쓴 시각[21] |
| MMKV | 없음 | 항목에 시각이 없고, 붙은 순서만 알 수 있습니다[18] |

iLEAPP 의 크기 판별은 epoch 앞뒤 약 4개월 안의 값을 잘못 판별할 수 있어서, 단위를 알면 직접 바꾸는 편이 안전합니다[2]. Coinbase Wallet 을 UTC 로 읽는 근거는 iLEAPP 시험 이미지에서 나온 결과입니다. 같은 MMKV 에 명시적인 `Z` 가 붙은 마이그레이션 시각이 있고, 이 값이 두 이미지에서 `account` 행보다 11초, 108초 앞선 같은 날짜·같은 시였습니다[13]. 현지 시각이었다면 몇 시간 차이가 났을 것입니다. `confirmedAt` 이 블록 시각인지 앱이 확정을 받은 시각인지는 공개 근거가 없으므로 블록 시각과 대조합니다([블록 시각과 확정](../../01-foundations/blockchain/block-time.md)).

Trust Wallet 키 파일 이름은 `UTC--` 로 시작하지만, 코드는 기기 현지 시간대로 시각을 쓰고 오프셋이 0 이 아니면 `String(format: "%03d00", offset/60)` 로 붙입니다[21]. 오프셋이 +9시간이면 32400초를 60 으로 나눈 540 뒤에 `00` 이 붙어 `54000` 이 됩니다(코드로 계산한 만든 예시). 오프셋이 0 일 때만 `Z` 가 붙습니다[21].

## 함정과 한계

- **iLEAPP 결과가 비어 있어도 MetaMask 데이터가 없는 것은 아닙니다.** `metamask.py` 는 `persist-root` 에 `engine` 키가 있을 때만 결과를 내므로[1], v7.60.0 이후 앱에서는 계정·트랜잭션뿐 아니라 `browser` 기록까지 결과에 나오지 않습니다. `persistStore` 폴더 목록을 보고 컨트롤러 파일을 직접 엽니다.
- **백업 추출에 MetaMask 파일이 없다고 앱을 안 썼다고 판단하면 안 됩니다.** `persistStore` 는 백업 제외 표시가 붙습니다[8].
- **Coinbase Wallet 과 Coinbase 거래소 앱은 다른 앱입니다.** 저장소가 달라서 iLEAPP 도 `coinbaseWallet.py` 와 `coinbase.py` 로 따로 읽습니다[13].
- **MMKV 키의 주소는 대문자입니다.** 다른 표의 같은 주소와 대소문자가 달라서, 문자열로 대조할 때 대소문자를 무시하고 비교합니다[13].
- **SQLite 는 `-wal`·`-shm` 까지 함께 수집합니다.** iLEAPP 도 `wallet-rn-v2.sqlite*` 패턴으로 WAL 파일까지 가져옵니다[13]. WAL 동작은 [SQLite](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/data-formats/sqlite/) 에 있습니다.
- **Trust Wallet 구조는 옛 공개 소스 기준입니다.** 현재 앱에 그대로 적용하지 않습니다[20][21].
- **Realm 파일을 도구가 못 읽을 수 있습니다.** iLEAPP `realmUndecodedStores` 는 번들 파서가 읽지 못한 `.realm` 파일을 따로 알려 주지만, 머리를 읽지 못한 파일이 암호화된 것인지 손상된 것인지는 판단하지 않습니다[19].
- **이름이 비슷한 다른 앱.** Cash App 은 송금 앱이고, 고객 레코드의 "Customer Bitcoin Display Units" 는 비트코인 표시 단위 설정일 뿐 결제 금액 단위가 아닙니다[23]. Apple Wallet 의 `passes23.sqlite` 는 Apple Pay 결제 거래 기록을 담고, iLEAPP 는 카드 정보를 지갑 앱 캐시 `Cache.db` 에서 따로 읽습니다[24]. 둘 다 암호화폐 지갑과 관계가 없으며, 자세한 내용은 iOS 핸드북의 [지갑과 Apple Pay](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/health-wallet/wallet.html) 에 있습니다.
- **MMKV 여유 공간에서 되살린 항목은 추정입니다.** MMKV 는 압축할 때 남아 있는 항목을 앞으로 옮기고 기록 크기만 줄여서, 기록 크기 뒤에 예전 항목이 남습니다[18]. iLEAPP `mmkvCarved` 가 이 공간을 읽지만 되살린 행 일부는 틀릴 수 있고, 그 항목이 덮어써진 것인지 지워진 것인지, 언제 그랬는지는 파일로 알 수 없습니다[25]. 반대로 저장소를 비우거나(`clearAll`) CRC 검사에 실패하면 크기만 0 으로 기록되고 항목은 그대로 남아서, 구조대로 다시 읽을 수 있습니다[18].

## 직접 분석해 보기

### 헥스로 MMKV 한 번 따라가기

아래는 키 `deviceId`, 값 `abc` 인 항목 하나를 MMKV 명세대로 만든 예시입니다(만든 예시, 전체 다시 쓰기로 저장된 경우의 모양).

```
00000000  0F 00 00 00 0E 08 64 65  76 69 63 65 49 64 04 03  |......deviceId..|
00000010  61 62 63 00 00 00 00 00  00 00 00 00 00 00 00 00  |abc.............|
```

1. `0F 00 00 00` 은 리틀 엔디언 15 로, 데이터 영역이 오프셋 4 부터 15바이트입니다.
2. `0E` 는 뒤따르는 항목 전체 크기 14 입니다.
3. `08` 은 키 길이 8, 이어지는 `64 65 76 69 63 65 49 64` 가 `deviceId` 입니다.
4. `04` 는 값 길이 4 이고, 값 `03 61 62 63` 은 다시 "길이 3 + `abc`" 입니다. MMKV 는 문자열을 이 모양으로 씁니다[18].
5. 오프셋 19 부터는 0 입니다. 여기에 0 이 아닌 바이트가 있으면 예전 항목이 남은 것일 수 있습니다.

실제 `CBStore.plaintext` 에서 같은 키가 여러 번 나오면, 파일에서 뒤에 있는 항목이 현재 값이고 앞의 것은 예전 값입니다.

### 공개 도구와 SQL 로 한 번

iLEAPP 를 파일 시스템 추출에 돌리면 `metamask.py`(MetaMask v7.59.0 까지), `coinbaseWallet.py`, `mmkvCarved.py`, `realmUndecodedStores.py` 결과를 한 번에 볼 수 있습니다[1][13][19][25]. 도구 결과와 별개로 원본을 직접 확인합니다.

1. MetaMask 는 `persistStore` 폴더 목록을 봅니다. `persist-root` 안에 `engine` 키가 있으면 옛 구조, `persist-TransactionController` 같은 파일이 있으면 새 구조입니다[1][3].
2. Coinbase Wallet 은 `wallet-rn-v2.sqlite` 를 `-wal`·`-shm` 과 함께 복사한 뒤 복사본에서 읽습니다.

```sql
SELECT address, derivationPath, isUsedStr, typeStr FROM address;
SELECT createdAt, confirmedAt, isSent, fromAddress, toAddress, amount, txHash FROM tx_history_v2;
```

3. 나온 주소와 해시를 블록 탐색기에서 조회하고, 입출금 여부와 블록 시각을 확인합니다([블록 탐색기 기록 읽기](../records/block-explorers.md)).

공개 분석기가 없는 지갑 앱은 [설치된 앱](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/app-usage/installed-apps.html) 으로 앱 폴더를 찾은 뒤 주소·트랜잭션 ID 문자열로 검색합니다([기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md), [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md)). 앱 데이터 분석 일반은 [앱 데이터 분석](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/analysis/app-data-analysis/) 에 있습니다.

## 교차 검증

| 함께 볼 것 | 확인하는 것 |
|---|---|
| [설치된 앱](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/app-usage/installed-apps.html) | UUID 폴더와 번들 ID, 설치 여부 |
| [키체인](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/keychain.html) | 볼트 백업·비밀번호 항목이 있는지 |
| [블록 탐색기 기록 읽기](../records/block-explorers.md) | 해시의 주소·금액·블록 시각, 주소의 실제 사용 여부 |
| [알림 기록](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/app-usage/notifications.html) | 입금·전송 알림이 뜬 시각 |
| [스크린샷과 화면 녹화](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/media/screenshots.html) | 주소·복구 문구 화면을 찍은 이미지 |
| [MetaMask](../browser/metamask/index.md) | 같은 사람이 PC 확장으로도 같은 주소를 썼는지 |
| [거래소 앱](exchange-apps.md), [거래소가 제공하는 자료](../records/exchange-records.md) | 지갑 주소와 거래소 입출금 기록이 이어지는지 |
| [암호화폐 타임라인](../../03-techniques/analysis/timeline.md), [iOS 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/analysis/timeline/) | 앱 기록 시각·블록 시각·기기 사건을 한 줄로 정렬 |

조사 질문 단위의 흐름은 [이 기기로 지갑을 썼나](../../04-scenarios/device-use/wallet-use.md) 에 있습니다.

## 실습

테스트넷을 지원하는 지갑 앱으로 테스트 기기에 직접 데이터를 만들어 풀어 봅니다.

1. 테스트 기기에 지갑 앱을 설치하고 새 계정을 만든 뒤, 전체 파일 시스템을 추출합니다. 앱의 UUID 폴더를 찾고, 계정 주소가 어느 파일에 평문으로 있는지 확인합니다.
2. 테스트넷에서 주소로 코인을 받고 한 번 보낸 뒤 다시 추출합니다. 앱 데이터에 두 트랜잭션 해시가 모두 있는지, 앱에 기록된 시각과 블록 탐색기의 블록 시각이 얼마나 차이 나는지 비교합니다.
3. 같은 기기를 iTunes·Finder 백업으로도 받아, 전체 파일 시스템 추출과 비교해 어떤 파일이 빠졌는지 확인합니다.
4. MMKV 파일이 있으면 설정을 몇 번 바꾼 뒤 헥스로 열어, 같은 키가 몇 번 나오는지와 기록 크기 뒤에 무엇이 남았는지 봅니다.

## 참고 문헌

1. iLEAPP, `scripts/artifacts/metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
2. iLEAPP, `scripts/ilapfuncs.py` (`convert_unix_ts_to_utc`, `convert_unix_ts_in_seconds`). https://github.com/abrignoni/iLEAPP/blob/main/scripts/ilapfuncs.py
3. MetaMask Mobile, `app/store/persistConfig/index.ts`. https://github.com/MetaMask/metamask-mobile/blob/main/app/store/persistConfig/index.ts
4. MetaMask Mobile, v7.59.0 `app/store/persistConfig.ts`, v7.60.0 `app/store/persistConfig/index.ts`. https://github.com/MetaMask/metamask-mobile/blob/v7.59.0/app/store/persistConfig.ts , https://github.com/MetaMask/metamask-mobile/blob/v7.60.0/app/store/persistConfig/index.ts
5. MetaMask Mobile, 커밋 c013e4ea6d (PR #17685 "Replace redux-persist with barebones JS persist system using FileSystemStorage", 2025-10-10). https://github.com/MetaMask/metamask-mobile/commit/c013e4ea6d
6. redux-persist-filesystem-storage, `index.js`. https://github.com/robwalkerco/redux-persist-filesystem-storage/blob/master/index.js
7. react-native-blob-util, `ios/ReactNativeBlobUtilFS.swift`. https://github.com/RonRadtke/react-native-blob-util/blob/master/ios/ReactNativeBlobUtilFS.swift
8. MetaMask Mobile, `.yarn/patches/redux-persist-filesystem-storage-npm-4.2.0-3a6fff24ab.patch`. https://github.com/MetaMask/metamask-mobile/blob/main/.yarn/patches/redux-persist-filesystem-storage-npm-4.2.0-3a6fff24ab.patch
9. MetaMask Mobile, `app/core/Encryptor/constants.ts`. https://github.com/MetaMask/metamask-mobile/blob/main/app/core/Encryptor/constants.ts
10. MetaMask Mobile, `app/core/BackupVault/backupVault.ts`, `constants.ts`. https://github.com/MetaMask/metamask-mobile/blob/main/app/core/BackupVault/backupVault.ts
11. MetaMask Mobile, `app/core/Encryptor/Encryptor.ts`. https://github.com/MetaMask/metamask-mobile/blob/main/app/core/Encryptor/Encryptor.ts
12. MetaMask Mobile, `ios/MetaMask.xcodeproj/project.pbxproj` (`PRODUCT_BUNDLE_IDENTIFIER`). https://github.com/MetaMask/metamask-mobile/blob/main/ios/MetaMask.xcodeproj/project.pbxproj
13. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
14. Coinbase, Privacy Policy. https://www.coinbase.com/legal/privacy
15. MetaMask Mobile, `app/core/SecureKeychain.ts`. https://github.com/MetaMask/metamask-mobile/blob/main/app/core/SecureKeychain.ts
16. BIP-32, Hierarchical Deterministic Wallets. https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
17. BIP-44, Multi-Account Hierarchy for Deterministic Wallets. https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
18. iLEAPP, `scripts/mmkv_parser.py` (mmkv-parser 커밋 05deada3d8f93000c85f4bc399b6c6f463c13e68 를 그대로 넣은 파일). https://github.com/abrignoni/iLEAPP/blob/main/scripts/mmkv_parser.py
19. iLEAPP, `scripts/artifacts/realmUndecodedStores.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/realmUndecodedStores.py
20. Trust Wallet, `trust-wallet-ios` (보관 저장소: `EtherKeystore.swift`, `TrustRealmConfiguration.swift`, `Transaction.swift`, `WalletStorage.swift`, `WalletAddress.swift`, `HistoryStore.swift`, `BookmarksStore.swift`). https://github.com/trustwallet/trust-wallet-ios
21. Trust Wallet, `trust-keystore` (보관 저장소: `KeyStore.swift`, `KeystoreKey.swift`, `KeystoreKeyHeader.swift`). https://github.com/trustwallet/trust-keystore
22. ethereum.org, Web3 Secret Storage Definition. https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/data-structures-and-encoding/web3-secret-storage/index.md
23. iLEAPP, `scripts/artifacts/cashApp.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/cashApp.py
24. iLEAPP, `scripts/artifacts/appleWalletTransactions.py`, `appleWalletCards.py`, `biomeWalletTransaction.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appleWalletTransactions.py
25. iLEAPP, `scripts/artifacts/mmkvCarved.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/mmkvCarved.py
