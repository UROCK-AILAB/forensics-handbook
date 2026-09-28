---
title: "기기에서 지갑 흔적 찾기"
parent: "기법 · 조사 절차·수집"
nav_order: 270
---

# 기기에서 지갑 흔적 찾기 (Artifact Search)

지갑 프로그램은 앱마다 정해진 폴더에 지갑 파일·설정·로그를 남기고, 폴더를 모를 때도 파일 앞부분의 모양으로 지갑 파일을 골라낼 수 있습니다. 이 페이지는 데스크톱·브라우저 확장·모바일·하드웨어 지갑의 흔적을 어떤 순서로 찾고, 지갑 파일 밖에서 무엇을 함께 보는지 정리합니다. 여기서 찾은 흔적으로는 "이 기기에 이 지갑이 있었다" 까지 확인되고, 실제로 쓰고 자산을 가졌는지는 주소와 체인 기록으로 이어서 확인합니다.

## 언제 쓰나

압수하거나 수집한 PC·휴대폰 이미지에서 암호화폐 지갑을 썼는지 확인할 때 이 절차를 씁니다. 전체 흐름은 [이 기기로 지갑을 썼나](../../04-scenarios/device-use/wallet-use.md)에서, 악성 코드가 지갑 폴더를 노렸는지 보는 경우는 [악성 코드가 지갑을 노렸나](../../04-scenarios/device-use/wallet-stealer.md)에서 다룹니다.

수사 준비 단계에서 거래 해시나 주소를 이미 알고 있다면, 그 값을 검색어로 적어 두고 추출물 전체를 검색해 흔적이 어느 파일에 있는지 찾을 수도 있습니다[16]. 이때 문자열을 뽑아내는 방법은 [주소와 트랜잭션 ID 찾기](address-carving.md)에서 다룹니다. 수집 전 준비와 증거 보존 원칙은 [조사 절차](investigation-process.md)에서 다룹니다.

## 절차

### 1. 곁 파일까지 함께 수집하고, 증거 사본에서 지갑 앱을 실행하지 않는다

지갑 DB 는 본 파일 하나만 떠 오면 내용이 빠질 수 있습니다. BRD 를 시험한 Android 추출물에서는 `platform.db` 의 내용이 모두 WAL (Write-Ahead Log) 파일에만 있어서, WAL 없이 읽으면 표에 행이 하나도 없었습니다[14]. Bitcoin Core 의 `wallet.dat-journal` 은 `wallet.dat` 의 SQLite 롤백 저널이고, `wallet.dat` 만큼 안전하게 보관해야 하는 파일입니다[1]. 그래서 `-wal`·`-shm`·`-journal` 처럼 이름 뒤에 붙는 곁 파일은 폴더째 함께 수집합니다. 실행 중인 시스템에서 지갑 파일만 복사하면 복사 도중 파일이 바뀌어 손상될 수 있어서, Bitcoin Core 지갑은 `backupwallet` 호출로 복사해야 합니다[1]. 가능하면 디스크 이미지에서 파일을 읽고, 실행 중인 시스템에서 파일만 떠 왔다면 그 사실을 기록합니다.

Electrum 은 지갑을 저장할 때 `지갑 경로.tmp.프로세스 ID` 이름의 임시 파일에 먼저 쓴 뒤 본 파일과 바꿉니다[5]. 저장이 중간에 끊겼다면 이런 임시 파일이 남아 있을 수 있으므로, 지갑 폴더는 파일 이름을 고르지 말고 통째로 가져옵니다.

증거 사본에서 지갑 앱을 켜면 흔적이 바뀝니다. Ledger Live 데스크톱은 시작할 때 사용자 데이터 폴더에서 이름이 `app.json.` 으로 시작하는 파일(정규식 `^app\.json\..+$`)을 지웁니다[10]. Bitcoin Core 는 `-debug` 없이 시작하면 `debug.log` 가 11,000,000 바이트를 넘을 때 마지막 10,000,000 바이트만 남기고 앞부분을 잘라 냅니다[3]. 앱을 켜서 화면으로 확인하는 대신 파일을 복사해 읽고, 앱 실행이 꼭 필요하면 복제본에서만 합니다.

### 2. 데스크톱 지갑의 기본 폴더부터 본다

데스크톱 지갑은 운영체제의 사용자 앱 데이터 폴더 아래에 데이터를 둡니다. 아래 표는 공식 문서·소스 코드·공개 문서에서 확인되는 위치입니다. 앱별 파일 구조는 각 앱 페이지에서 다룹니다.

| 지갑 | 위치 | 근거 | 자세한 내용 |
|---|---|---|---|
| Bitcoin Core 데이터 폴더 | Linux `$HOME/.bitcoin/`, macOS `$HOME/Library/Application Support/Bitcoin/`, Windows `%LOCALAPPDATA%\Bitcoin\`. `-datadir` 옵션으로 바꿀 수 있고, 테스트넷·시그넷·리그테스트는 `testnet3/`·`testnet4/`·`signet/`·`regtest/` 하위 폴더에 따로 저장 | [1] | [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md) |
| Bitcoin Core 지갑 | 이름 있는 지갑은 `wallets/지갑 이름/wallet.dat`, 이름 없는 기본 지갑은 `wallets/` 안. `wallets/` 폴더가 없으면 데이터 폴더 바로 아래 | [1] | [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md) |
| Bitcoin Core 그 밖의 파일 | `debug.log`, `settings.json`, `mempool.dat`, `peers.dat`, `banlist.json`, `blocks/`, `chainstate/`, `indexes/txindex/`(`-txindex=1` 일 때만) | [1] | [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md) |
| Electrum | 환경 변수 `ELECTRUMDIR` 이 있으면 그 폴더, macOS·Linux 는 `~/.electrum`, Windows 는 `%APPDATA%\Electrum`(없으면 `%LOCALAPPDATA%\Electrum`). 지갑은 그 아래 `wallets\` 에 있고 처음 만든 지갑 이름은 보통 `default_wallet` | [4][6] | [Electrum](../../02-artifacts/desktop/electrum.md) |
| Coinomi (Windows) | `%localappdata%\Coinomi\Coinomi\wallets` | [6] | [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md) |
| Bither | `%appdata%\Bither`, 파일 이름은 보통 `address.db` | [6] | — |
| MultiBit Classic | 처음 설치할 때 만든 기본 지갑은 `%appdata%\MultiBit\multibit-data\key-backup\`, 다른 지갑의 `key-backup` 폴더는 지갑 파일 가까이에 있음. 파일 이름은 `지갑 이름-20140407200743.key` 처럼 지갑 이름 뒤에 날짜·시각이 붙는 모양 | [6] | — |
| MultiBit HD | `%appdata%\MultiBitHD` 아래 지갑 폴더의 `mbhd.wallet.aes` | [6] | — |
| mSIGNA | `%homedrive%%homepath%` 의 `.vault` 파일 | [6] | — |
| Monero CLI·GUI | 지갑 하나가 `지갑 이름.keys`(키 파일)와 확장자 없는 `지갑 이름`(캐시 파일) 두 파일로 이루어짐 | [18] | [믹서와 추적을 어렵게 하는 방법](../../01-foundations/ecosystem/mixers.md) |

Bitcoin Core 의 Windows 기본 폴더는 28.0 에서 `C:\Users\사용자\AppData\Roaming\Bitcoin` 에서 `C:\Users\사용자\AppData\Local\Bitcoin` 으로 바뀌었고, 옛 폴더가 있으면 그 폴더를 계속 씁니다[2]. 28.0 이전 버전을 설명한 자료는 `%appdata%\Bitcoin` 으로 안내하므로[6], Windows 에서는 두 폴더를 모두 확인합니다. Exodus 는 기본 폴더 대신 파일 모양으로 찾는 방법을 6단계에서 다룹니다.

### 3. 브라우저 확장 지갑은 프로필마다, 저장소마다 본다

Chromium 계열 브라우저의 확장 데이터는 프로필 폴더의 `Local Extension Settings\확장 ID\` 에 있습니다. Chrome 기본 프로필의 MetaMask 는 `%localappdata%\Google\Chrome\User Data\Default\Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn\` 이고, 같은 폴더 아래 Binance Wallet 은 `fhbohimaelbohpjbbldcngcnapndodjp`, Ronin Wallet 은 `fnjhmkhhmkbjkkabndcnnogagogbneec` 폴더를 씁니다[6]. Brave 같은 다른 Chromium 계열 브라우저는 앞부분 경로가 다르지만 마지막 확장 ID 폴더 이름은 같습니다[6]. 그래서 브라우저 종류와 프로필(`Default`, `Profile 1` 등)마다 같은 확장 ID 폴더를 모두 찾습니다. 프로필 구조와 LevelDB 저장 형식은 Windows 핸드북의 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/)와 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)에서 다룹니다.

MetaMask 는 `Local Extension Settings` 말고 IndexedDB 에도 데이터를 둡니다. IndexedDB 데이터베이스 `metamask-backup`(버전 1)에는 `KeyringController`·`AppMetadataController`·`MetaMetricsController`·`AnalyticsController` 상태와 `meta` 를 백업하고, 볼트는 이 중 `KeyringController` 안에 있습니다[7]. 이와 별도로 `metamask-storage-service`(버전 1) 데이터베이스도 있습니다[7]. Chrome 계열에서는 두 데이터베이스를 프로필의 `IndexedDB\chrome-extension_nkbihfbeogaeaoehlefnkodbefgpgknn_0.indexeddb.leveldb` 폴더에서 찾습니다([저장 위치와 구조](../../02-artifacts/browser/metamask/storage.md)). 사용자가 설정의 Privacy 메뉴에서 "Download state logs" 를 누르면 상태를 JSON 파일로 내려받을 수 있어서[8], 다운로드 폴더에 이런 파일이 남아 있는지도 봅니다. 확장별 필드와 볼트 모양은 [MetaMask](../../02-artifacts/browser/metamask/index.md)와 [다른 확장 지갑](../../02-artifacts/browser/other-extensions.md)에서 다룹니다.

### 4. 모바일은 앱 폴더와 공개 분석기 경로를 본다

휴대폰에서는 지갑 앱의 앱 데이터 폴더를 봅니다. 아래 경로는 iLEAPP·ALEAPP 분석기가 찾는 경로와 논문의 시험 결과입니다. `*` 는 추출물마다 달라지는 앞부분 경로입니다.

| 앱 | 경로 | 근거 | 자세한 내용 |
|---|---|---|---|
| MetaMask (iOS) | `*/mobile/Containers/Data/Application/*/Documents/persistStore/persist-root` | [11] | [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md) |
| Coinbase Wallet (iOS, 번들 ID `org.toshi.distribution`) | `*/mobile/Containers/Data/Application/*/Documents/default/wallet-rn-v2.sqlite*`, `*/mobile/Containers/Data/Application/*/Documents/mmkv/CBStore.plaintext` | [13] | [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md) |
| Coinbase 거래소 앱 (iOS) | `*/Documents/mmkv/CB_RRN_MMKV_STORAGE` | [12] | [거래소 앱](../../02-artifacts/mobile/exchange-apps.md) |
| BRD (Android) | `*/com.breadwallet/databases/platform.db*` | [14] | [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md) |
| Coinomi (Android) | 지갑 파일은 `data\data\com.coinomi.wallet\files\wallets` 의 `.wallet` 파일. 9.26.3 에서는 받은 거래마다 `cache/16자 헥스 이름 폴더/bitcoin.main/` 또는 `dogecoin.main/` 아래에 트랜잭션 해시를 이름으로 한 0 KB 파일이 생김 | [6][16] | [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md) |
| Atomic (Android 0.75.1) | 앱 WebView 쿠키 `io.atomicwallet/app_webview/Default/Cookies` | [16] | [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md) |
| Trust Wallet (iOS, 2019년 5월이 마지막 갱신인 보관 처리된 공개 저장소 기준) | `Documents` 아래 `keystore` 폴더, Realm 기본 폴더의 `shared.realm` 과 `계정.realm` | [15] | [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md) |

Android 논문의 시험에서는 루팅하지 않은 기기로 물리 추출을 시도하면 실패했고, 물리 추출이 없으면 빠지는 흔적이 있었습니다[16]. 추출 방식에 따라 앱 폴더 전체가 들어오지 않을 수 있으므로, 추출물에 위 폴더가 실제로 있는지 먼저 확인합니다. Trust Wallet 저장소는 2019년 5월 이후 갱신이 없어서[15] 지금 앱의 파일 구조와 다를 수 있습니다. 앱 폴더 구조의 일반 원리는 Android 핸드북의 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/app-data-layout.html)와 iOS 핸드북의 [앱 데이터 분석](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/analysis/app-data-analysis/)에서 다룹니다.

### 5. 하드웨어 지갑은 연동 앱과 메모리를 본다

하드웨어 지갑은 키를 장치 안에 두기 때문에, PC 에는 연동 앱의 데이터와 연결 기록이 남습니다. Ledger Live 데스크톱은 Electron 의 `userData` 폴더에 네임스페이스마다 `app.json` 같은 JSON 파일을 두고, 환경 변수 `LEDGER_CONFIG_DIRECTORY` 가 있으면 그 폴더를 씁니다[10]. 제품 이름은 "Ledger Wallet" 로 바뀌었지만 사용자 데이터 폴더 이름은 옛 이름 "Ledger Live" 를 계속 쓰고, 새 이름 폴더에 이미 `app.json` 이 있으면 그 폴더를 그대로 씁니다[10]. 그래서 두 이름의 폴더를 모두 찾습니다. Electron 앱의 폴더 구조는 Windows 핸드북의 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/)에서 다룹니다.

Trezor Bridge 는 사용자의 Application Data 폴더에 로그를 남기는데, 이 로그에는 Trezor 가 아닌 장치까지 포함해 USB 장치가 연결된 시각이 기록됩니다[17]. Bridge 가 실행 중인 동안에는 로그 파일이 열려 있어서, 실행 중인 시스템의 메모리 덤프에서 Volatility 의 `dumpfiles` 로 꺼낼 수 있습니다[17]. Ledger Live 1.18.2 시험에서는 앱을 잠그자 메모리 흔적 대부분이 곧 덮어써져, 6분 뒤에는 확장 공개 키 14개와 명령 흔적 1개만 남았습니다. 앱 프로세스를 끝낸 뒤에는 6분 안에 남은 흔적도 모두 덮어써졌습니다[17]. 메모리 수집 순서는 [조사 절차](investigation-process.md)를, 장치별 흔적은 [하드웨어 지갑과 연결 흔적](../../02-artifacts/hardware/hardware-wallets.md)을 봅니다.

### 6. 위치를 모르면 파일 모양으로 찾는다

사용자가 지갑 파일을 옮겼거나 이름을 바꿨다면 폴더 대신 파일 앞부분으로 찾습니다. 아래 모양은 형식 명세와 소스 코드에서 확인되는 것이고, 각 형식의 자세한 구조는 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md)에서 다룹니다.

| 찾을 모양 | 해당 지갑 | 근거 |
|---|---|---|
| 파일 맨 앞 4바이트가 `SECO` | Exodus 보안 컨테이너. 뒤따르는 머리에 `appName`·`appVersion` 문자열이 있어 어느 앱의 어느 버전이 썼는지 확인됨 | [9] |
| 텍스트 파일 전체가 `QklFM` 로 시작하는 base64 | Electrum 파일 전체 암호화(`BIE1`·`BIE2`) | [5] |
| JSON 에 `seed_version`·`wallet_type` 키 | Electrum 평문 지갑 | [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md) |
| SQLite 파일 중 표가 `main(key, value)` 하나뿐인 것 | Bitcoin Core descriptor 지갑 | [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md) |
| `이름.keys` 와 확장자 없는 `이름` 이 짝으로 있는 파일 | Monero 지갑(두 파일 모두 암호화돼 평문 검색으로는 내용이 안 보임) | [18] |
| 64자 헥스 이름의 0 KB 파일 | Coinomi(Android) 받은 거래 해시 | [16] |

SECO 파일은 머리 224바이트, 체크섬 32바이트, 암호화 설정 256바이트가 차례로 오고, 오프셋 512 에 본문 길이(UInt32 빅엔디언), 오프셋 516 부터 본문이 옵니다[9]. 이 길이는 secure-container 코드의 길이 상수로 계산한 값입니다. 파일 이름이 무엇이든 크기가 516바이트 이상이고 `SECO` 로 시작하면 Exodus 계열 컨테이너 후보로 봅니다.

### 7. 지갑 파일 밖의 흔적을 함께 본다

거래소 계정은 메일 흔적을 남깁니다. 2021년 Android 논문의 시험에서 Coinbase 는 `no-reply@coinbase.com` 에서 "You just received … BTC", "You just sent … BTC to 주소" 같은 제목의 메일을 보냈고, 제목에 금액과 상대 주소가 있었습니다[16]. 가입에 메일 주소가 필요 없는 Coinomi·Atomic 은 이런 메일이 없었습니다[16].

앱 안의 WebView 쿠키도 단서가 됩니다. 같은 시험에서 Atomic 은 Cloudflare 쿠키 `__cflb` 를 포함해 쿠키 16개를, Coinbase 는 `__cf_bm` 을 포함해 6개를 남겼습니다[16]. 쿠키 값에 사람을 곧바로 특정할 정보는 없었습니다. Atomic 의 `__cflb` 는 앱을 설치한 뒤, 거래보다 먼저 만들어졌고, 다른 쿠키 세 개의 값에는 사설 IP 주소와 포트가 있었습니다[16]. 이 생성 시각과 IP·포트는 Atomic 이나 Cloudflare 에 네트워크 기록을 적법하게 요청할 때 단서가 됩니다[16]. 루팅한 기기의 물리 추출로 얻은 비밀번호 파일 208개 가운데 185개는 Google 이 관리하는 OAuth 2.0 토큰이었고, 지갑 앱이 직접 만든 OAuth 토큰은 없었습니다[16].

복구 문구는 종이나 금속판에 적는 것 말고도 기기의 문서에 복사해 붙여 넣어 두는 경우가 있습니다[16]. 메모·문서·스크린샷에 복구 문구가 있을 수 있으므로 문서 폴더와 사진·스크린샷도 범위에 넣고, 찾으면 파일 위치와 존재만 기록하고 문구 자체는 보고서에 옮기지 않습니다. 스크린샷 위치는 Android·iOS 핸드북의 스크린샷 페이지([Android](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/media/screenshots.html), [iOS](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/media/screenshots.html))에서 다룹니다.

지갑 앱 안의 브라우저 기록도 봅니다. iOS MetaMask 의 `persist-root` 에는 앱 내장 브라우저의 방문 기록(`browser` 의 `history`, 이름과 URL)이 있어서[11], 방문한 DApp 과 블록 탐색기를 알 수 있습니다. 일반 브라우저의 방문 기록과 확장 설치 흔적은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) 같은 브라우저 페이지에서 다룹니다.

### 8. 찾은 파일에서 주소와 해시를 뽑아 다음 단계로 넘긴다

지갑 폴더·파일 목록을 정리했으면 그 안에서 주소·확장 공개 키·트랜잭션 해시를 뽑습니다. 문자열 모양과 검증 방법은 [주소와 트랜잭션 ID 찾기](address-carving.md)에서, 뽑은 주소로 체인 기록을 확인하는 방법은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)와 [비트코인 거래 따라가기](../analysis/bitcoin-tracing.md)에서 다룹니다.

## 도구

KAPE 에는 지갑 문자열을 찾는 모듈이 있습니다. 묶음 모듈 `bstrings_CryptoWallets` 는 Aeon·BitCoin·ByteCoin·DashCoin·DashCoin2·FantomCoin·Monero·SumoKoin 모듈을 차례로 돌리고, 목록에 자기 자신(`bstrings_CryptoWallets.mkape`)도 들어 있습니다[19]. 각 모듈은 `bstrings.exe -d %sourceDirectory% -o '%destinationDirectory%' --lr bitcoin` 처럼 bstrings 의 내장 정규식 하나로 수집 폴더를 검색합니다[19]. 내장 `bitcoin` 정규식은 `\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b` 이고 이더리움 주소용 정규식은 없어서[20], `bc1` 로 시작하는 주소와 이더리움 주소는 따로 찾아야 합니다. KapeFiles 저장소에서 지갑용으로 제공되는 것은 이 문자열 검색 모듈들이고, 지갑 폴더를 모아 오는 수집 대상(Target)은 위 2~5단계 표를 보고 직접 목록을 만듭니다.

iLEAPP 과 ALEAPP 은 MetaMask(iOS), Coinbase 거래소 앱(iOS), Coinbase Wallet(iOS), BRD(Android)를 자동으로 분석합니다[11][12][13][14]. 두 도구는 모바일 추출물을 폴더(`fs`)나 zip·tar·gz 압축 파일로 받습니다[21]. 목록에 없는 앱은 위 표의 폴더를 직접 열어 봅니다. 그 밖에 SQLite 파일은 SQLite 뷰어로([Windows](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/)·[Android](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/data-formats/sqlite/)·[iOS](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/data-formats/sqlite/) SQLite 페이지 참고), 브라우저 확장 데이터는 LevelDB·IndexedDB 를 읽는 도구로 보고, SECO 머리는 헥스 편집기로 직접 확인합니다.

## 함정과 한계

**한 프로필만 보고 끝내기.** 확장 데이터는 브라우저 종류와 프로필마다 따로 있습니다[6]. 기본 프로필에 MetaMask 폴더가 없어도 다른 프로필이나 다른 Chromium 계열 브라우저에 있을 수 있습니다.

**`Local Extension Settings` 만 보기.** MetaMask 는 볼트를 담은 `KeyringController` 를 IndexedDB `metamask-backup` 에 따로 백업합니다[7]. 확장 설정 폴더가 지워졌거나 손상됐어도 IndexedDB 쪽에 남아 있을 수 있습니다.

**디스크 전체 문자열 검색만 믿기.** LevelDB 파일 일부는 압축돼 있어서 원시 바이트 검색으로는 주소가 안 보일 수 있습니다. 압축 방식과 읽는 법은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)에서 다룹니다. Monero 지갑처럼 파일 전체가 암호화된 형식도 평문 검색에 걸리지 않습니다[18].

**폴더 이름이 바뀐 경우.** Bitcoin Core 는 28.0 전후로 Windows 기본 폴더가 다르고[2], Ledger Live 는 제품 이름과 폴더 이름이 다릅니다[10]. 문서에 적힌 폴더 하나만 확인하면 놓칩니다.

**시험 조건 밖의 버전.** 모바일 경로 중 Coinomi·Atomic 은 한 기기(Galaxy S9+, Android 8.0)와 특정 버전의 시험 결과입니다[16]. 같은 논문 안에서도 Coinomi 버전을 본문과 표 II 는 9.26.3 으로, 표 X 는 8.26.3 으로 적고 있어[16], 실제 데이터에서는 앱의 버전 정보부터 확인합니다. 그 시험에서 Coinomi 의 해시 파일은 받은 거래에만 생겼고, Coinbase·Atomic 은 파일 시스템에 트랜잭션 ID 를 남기지 않았습니다[16].

**복원한 지갑.** Monero 지갑을 복원하면 캐시 파일에는 복원 높이 이후의 거래만 들어가므로 그 이전 거래 기록이 없을 수 있습니다[18]. 다른 지갑도 복원·재설치 뒤에는 옛 기록이 기기에 없을 수 있어서, 기기 기록이 없다고 거래가 없었다고 판단하지 않습니다.

## 결과를 어떻게 해석하나

### 증명하는 것 / 증명하지 못하는 것

지갑 폴더·파일·확장 데이터가 있으면 그 지갑 프로그램이 이 기기의 이 사용자 프로필에 있었다는 것이 확인됩니다. SECO 머리의 `appName`·`appVersion` 처럼 파일 안에 쓴 앱과 버전이 적혀 있으면 그 파일을 만든 프로그램까지 확인되고[9], 파일 시스템 시각으로 생성·수정 시점을 알 수 있습니다.

설치 흔적이나 파일이 있다는 것만으로는 지갑을 실제로 썼거나 자산을 가졌다는 것까지 확인되지 않습니다. Coinbase Wallet 의 주소 표에는 앱이 이미 만들어 둔 주소가 들어 있어서, 주소가 있다고 그 주소를 쓰거나 입금받았다는 뜻은 아닙니다[13]. 거래소 앱은 키를 거래소가 보관하므로 기기에 키가 없고, 이 차이는 [지갑의 종류](../../01-foundations/wallets/wallet-types.md)에서 다룹니다. 메일과 쿠키는 계정과 서비스를 쓴 흔적이지 키를 가졌다는 증거는 아닙니다[16]. 사용 여부는 여기서 찾은 주소를 체인 기록과 [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md)에 대조해 확인합니다.

보고서에는 확인된 만큼만 씁니다. 예: "이 PC 의 사용자 A 프로필에 있는 Chrome `Profile 1` 폴더의 `Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn\` 에 MetaMask 확장 데이터가 있고, 폴더 안 파일의 마지막 수정 시각은 2026-03-02 14:05:11 (UTC) 입니다. (만든 예시)"

### 시각

지갑 흔적의 시각은 대부분 기기 시계로 기록한 파일 시스템 시각이고, 블록 시각과는 기준이 다릅니다. 둘의 차이는 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에서, 여러 시각을 합치는 방법은 [암호화폐 타임라인](../analysis/timeline.md)에서 다룹니다.

파일 이름이나 폴더가 만들어진 시점 자체가 사건을 알려 주는 경우가 있습니다. MultiBit Classic 은 지갑에 처음 암호를 걸 때와 그 뒤 받는 주소를 추가하거나 암호를 바꿀 때마다 `key-backup` 폴더에 백업 파일을 만들고, 파일 이름에 날짜·시각이 붙습니다[6]. 이 시각이 UTC 인지 현지 시각인지는 파일 시스템 시각과 비교해 확인합니다. Coinomi(Android 9.26.3)는 거래를 받을 때 해시 이름 파일을 만들어서[16], 그 파일의 생성 시각이 받은 시점의 단서가 됩니다.

시각을 적을 때는 기준을 함께 적습니다. Android 논문은 같은 Coinomi 수신 거래의 시각을 UTC 로 적은 표 V 에는 2021-06-14 03:14 로, 파일 경로를 보인 표 VI 에는 기준 없이 2021-06-13 23:15 로 적어 약 4시간이 다릅니다[16]. 어느 값이 블록 시각이고 어느 값이 기기 시각인지, 시간대가 무엇인지를 적지 않으면 이런 차이를 나중에 설명할 수 없습니다.

## 참고 문헌

1. Bitcoin Core, "Bitcoin Core file system" (doc/files.md). https://github.com/bitcoin/bitcoin/blob/master/doc/files.md
2. Bitcoin Core, "Bitcoin Core 28.0 release notes". https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-28.0.md
3. Bitcoin Core 소스 코드, src/logging.cpp, src/init/common.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/logging.cpp , https://github.com/bitcoin/bitcoin/blob/master/src/init/common.cpp
4. Electrum 소스 코드, electrum/util.py (`user_dir`). https://github.com/spesmilo/electrum/blob/master/electrum/util.py
5. Electrum 소스 코드, electrum/storage.py. https://github.com/spesmilo/electrum/blob/master/electrum/storage.py
6. btcrecover, "Extract Scripts" (docs/Extract_Scripts.md). https://github.com/3rdIteration/btcrecover/blob/master/docs/Extract_Scripts.md
7. MetaMask 확장 소스 코드, shared/lib/stores/persistence-manager.ts, indexeddb-storage-constants.ts. https://github.com/MetaMask/metamask-extension/blob/main/shared/lib/stores/persistence-manager.ts , https://github.com/MetaMask/metamask-extension/blob/main/shared/lib/stores/indexeddb-storage-constants.ts
8. MetaMask, "State dump" (docs/state_dump.md). https://github.com/MetaMask/metamask-extension/blob/main/docs/state_dump.md
9. Exodus, secure-container 소스 코드, src/header.js, src/file.js, src/metadata.js. https://github.com/ExodusMovement/secure-container/blob/master/src/header.js , https://github.com/ExodusMovement/secure-container/blob/master/src/file.js , https://github.com/ExodusMovement/secure-container/blob/master/src/metadata.js
10. Ledger Live 데스크톱 소스 코드, apps/ledger-live-desktop/src/main/index.ts, src/main/cleanupUserData.ts, package.json. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/main/index.ts
11. iLEAPP, scripts/artifacts/metamask.py. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
12. iLEAPP, scripts/artifacts/coinbase.py. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbase.py
13. iLEAPP, scripts/artifacts/coinbaseWallet.py. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
14. ALEAPP, scripts/artifacts/breadWallet.py. https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/breadWallet.py
15. Trust Wallet iOS 소스 코드(보관 처리된 저장소), Trust/Core/Types/TrustRealmConfiguration.swift, Trust/EtherClient/EtherKeystore.swift. https://github.com/trustwallet/trust-wallet-ios/blob/master/Trust/Core/Types/TrustRealmConfiguration.swift , https://github.com/trustwallet/trust-wallet-ios/blob/master/Trust/EtherClient/EtherKeystore.swift
16. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, "Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications", arXiv, 2022. doi:10.48550/arXiv.2205.14611
17. Tyler Thomas, Mathew Piscitelli, Ilya Shavrov, Ibrahim Baggili, "Memory FORESHADOW: Memory FOREnSics of HArDware CryptOcurrency wallets – A Tool and Visualization Framework", Forensic Science International: Digital Investigation 33, 2020. doi:10.1016/j.fsidi.2020.301002
18. Jeongin Lee, Geunyeong Choi, Jihyo Han, Jungheum Park, "Advanced Monero wallet forensics: Demystifying off-chain artifacts to trace privacy-preserving cryptocurrency transactions", Forensic Science International: Digital Investigation 54, 2025. doi:10.1016/j.fsidi.2025.301988
19. KapeFiles, Modules/Compound/bstrings_CryptoWallets.mkape, Modules/EZTools/bstrings/bstrings_BitCoinWallet.mkape. https://github.com/EricZimmerman/KapeFiles/blob/master/Modules/Compound/bstrings_CryptoWallets.mkape , https://github.com/EricZimmerman/KapeFiles/blob/master/Modules/EZTools/bstrings/bstrings_BitCoinWallet.mkape
20. bstrings 소스 코드, bstrings/Program.cs. https://github.com/EricZimmerman/bstrings/blob/master/bstrings/Program.cs
21. iLEAPP·ALEAPP README. https://github.com/abrignoni/iLEAPP/blob/main/README.md , https://github.com/abrignoni/ALEAPP/blob/main/README.md
