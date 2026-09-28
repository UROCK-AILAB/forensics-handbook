---
title: "Android 지갑 앱"
parent: "아티팩트 · 모바일 지갑과 거래소 앱"
nav_order: 200
---

# Android 지갑 앱 (Android Wallets)

Android 의 지갑 앱은 패키지 이름 폴더 아래의 SQLite DB, XML 설정 파일, 캐시 파일에 트랜잭션 해시·계정 식별자·시세 캐시 같은 흔적을 남깁니다. 공개 도구 코드와 논문으로 저장 구조가 확인된 앱은 BRD, Coinomi, Atomic, MetaMask Mobile 이고, 다른 앱은 앱 폴더에서 주소·트랜잭션 ID 문자열을 찾는 방법으로 봅니다. 앱이 값을 암호화해 두는 경우가 많아서 기기만으로는 "이 해시에 대한 기록이 언제 있었다" 까지 확인되는 일이 많고, 금액과 상대방은 블록체인과 거래소 기록으로 채웁니다.

## 무엇을 기록하나 · 왜 생기나

비수탁형 지갑 앱은 키를 기기에서 만들고 보관하기 때문에, 계정과 거래 상태도 기기 안의 앱 폴더에 저장합니다. 거래소 앱은 키를 거래소가 쥐고 있어서 남는 것이 다릅니다. 이 구분은 [지갑의 종류](../../01-foundations/wallets/wallet-types.md)에서, 거래소 앱은 [거래소 앱](exchange-apps.md)에서 다룹니다.

남는 흔적의 모양은 앱마다 다릅니다. BRD (BreadWallet)는 키-값 저장소 DB 에 트랜잭션 해시를 키로 하는 메타데이터 레코드를 두고, 설정 파일에는 계정 식별자와 앱 상태를, 다른 DB 에는 시세 캐시를 저장합니다[1]. Coinomi 는 받은 거래의 해시를 캐시 폴더의 파일 이름으로 남기고, Atomic 은 앱 안의 WebView 가 받은 쿠키를 남깁니다[2]. MetaMask Mobile 은 앱 상태를 JSON 파일로 저장합니다[3][5].

## 위치와 버전별 차이

Android 앱 데이터는 `/data/data/` 아래 패키지 이름 폴더에 있고, 폴더 구조의 일반 원리는 Android 핸드북의 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/app-data-layout.html)에서 다룹니다. 물리 추출 이미지에서는 userdata 파티션을 기준으로 경로가 보여서, 같은 폴더가 `userdata(ExtX)/Root/data/com.coinomi.wallet/...` 처럼 나타납니다[2].

| 앱 | 패키지 이름 | 흔적이 있는 파일 (앱 폴더 기준) | 확인 근거와 조건 |
|---|---|---|---|
| BRD | `com.breadwallet` | `databases/platform.db`(`-wal`·`-shm` 포함), `databases/breadwallet.db`, `shared_prefs/MyPrefsFile.xml` | ALEAPP 분석기, Android 10 이미지 한 대[1] |
| Coinomi 9.26.3 | `com.coinomi.wallet` | `cache/` 아래 16자 헥스 이름 폴더의 `bitcoin.main/`, `dogecoin.main/` | Galaxy S9+·Android 8.0 시험[2] |
| Atomic 0.75.1 | `io.atomicwallet` | `app_webview/Default/Cookies` | 같은 시험[2] |
| MetaMask Mobile | `io.metamask` | `files/persistStore/` | 앱 소스(main 브랜치, versionName 8.15.0)[3][5][6][7] |

BRD 분석기에는 앱 버전이 적혀 있지 않고, Coinomi·Atomic 은 위 표의 버전에서만 시험한 결과입니다. 다른 버전에서는 파일 이름과 폴더가 다를 수 있으므로 실제 데이터로 폴더 목록부터 확인합니다.

MetaMask Mobile 의 저장 경로는 앱 소스 코드에서 정해집니다. 앱은 `redux-persist-filesystem-storage` 라이브러리로 상태를 저장하고, 이 라이브러리는 `DocumentDir/persistStore` 폴더에 키마다 파일 하나를 만듭니다. 파일 이름은 키의 `:` 를 `-` 로 바꾼 것이라서 `persist:root` 키는 `persist-root` 파일이 됩니다[5]. `DocumentDir` 은 Android 에서 앱의 `getFilesDir()` 폴더이므로[6], 파일은 `/data/data/io.metamask/files/persistStore/` 아래에 생깁니다. 실제 이미지에서는 이 폴더가 있는지 먼저 확인합니다.

MetaMask Mobile 은 v7.60.0 부터 저장 방식이 바뀌었습니다. v7.59.0 까지는 컨트롤러 상태(`engine`)가 `persist-root` 한 파일 안에 들어 있었고, v7.60.0 부터는 `engine` 을 `persist-root` 에서 빼고 컨트롤러마다 `persist:컨트롤러 이름` 키로 따로 저장합니다[3][4]. Android 와 iOS 가 같은 코드를 쓰므로, 컨트롤러 파일의 필드와 버전 판별 방법은 [iOS 지갑 앱](ios-wallets.md)에서 한 번에 다룹니다.

## 구조

### BRD: `platform.db` 의 `kvStoreTable`

`kvStoreTable` 은 앱이 쓰는 키-값 저장소이고 열은 아래와 같습니다[1].

| 열 | 내용 |
|---|---|
| `key` | 레코드 이름. 평문으로 저장됩니다. |
| `version` | 같은 키의 버전 번호 |
| `remote_version` | 원격 버전 번호 |
| `thetime` | 기록 시각. Unix epoch 밀리초 |
| `deleted` | 삭제 표시 |
| `value` | 암호화된 값 |

시험 이미지에서 나온 키는 `wallet-info`, `asset-index`, `plat-vuex-` 로 시작하는 앱 상태 키, `txn2-` 로 시작하는 트랜잭션 메타데이터 키였습니다. `wallet-info` 와 `asset-index` 는 이름만 보고 뜻을 단정하지 않습니다[1].

`txn2-` 뒤의 문자열은 트랜잭션 해시이고, 시험 이미지에서는 헥스 64자였습니다. 이렇게 읽는 근거는 앱 APK 안의 코드입니다. APK 에 상수 이름 `TX_META_DATA_KEY_PREFIX`, 이 키를 만드는 메서드 `getTxMetaDataKey`, 레코드를 읽는 클래스 `com.breadwallet.platform.entities.TxMetaData`, 쿼리 `...where key like 'txn2-%'`, 이벤트 문자열 `OnTransactionMetaDataUpdated(transactionHash=` 가 들어 있습니다[1].

`value` 는 모든 행이 같은 머리 바이트로 시작하고 그 뒤가 무작위처럼 보이는 바이트라서 암호문으로 봅니다. 추출물 안에서 이 값을 풀 키가 나오지 않았으므로, TxMetaData 레코드에 들어갈 수 있는 금액·상대방·사용자 메모는 복구되지 않습니다[1].

같은 키가 버전을 달리해 여러 행으로 남습니다. 그래서 버전이 가장 낮은 행의 `thetime` 을 처음 기록한 시각으로, 가장 높은 행의 `thetime` 을 마지막으로 기록한 시각으로 읽습니다[1].

### BRD: `shared_prefs/MyPrefsFile.xml`

앱 설정 파일이고, 이름별로 아래 값이 들어 있습니다[1].

| 이름 | 값의 형식 | 뜻 |
|---|---|---|
| `userId` | UUID | BRD 계정 식별자 |
| `walletRewardId` | 네 단어 값 | 지갑 리워드 식별자 |
| `phraseWritten` | 불리언 | 이름은 복구 문구를 적었는지와 관련 있지만, 어떤 사용자 동작이 이 값을 켜는지는 시험 기기에서 재현해 확인합니다. |
| `rewardsAnimationShown` | 불리언 | 앱 상태 값 |
| `appForegroundedCount` | 정수 | 앱 상태 값 |
| `secureTime` | Unix epoch 밀리초 | 시각 값 |
| `fcmToken` | 문자열 | 푸시 메시지 등록 토큰. 지갑 키가 아닙니다. |

이 파일에는 복구 문구·개인 키·시드가 없습니다. 같은 폴더의 `crypto_shared_prefs.xml` 은 androidx.security 로 암호화한 설정과 Tink 키셋을 담은 별도 파일이고, 분석기는 이 파일을 읽지 않습니다[1].

### BRD: `breadwallet.db` 의 `currencyTable_v2`

앱이 받아 둔 시세 캐시이고 열은 `code`, `name`, `rate`, `iso` 입니다. `iso` 를 암호화폐, `code` 를 법정화폐로 읽으면 값이 맞아떨어집니다. 시험 이미지에서 BTC/USD 행은 55506, BCH/USD 행은 913.48 이었습니다[1]. 이 표에는 시각 열이 없어서 시세를 언제 받았는지 알 수 없습니다[1].

### Coinomi: 캐시 폴더의 해시 이름 파일

Coinomi 는 거래를 받으면 `cache/` 아래에 16자 헥스 이름의 폴더를 만들고, 그 안의 `bitcoin.main/`, `dogecoin.main/` 폴더에 트랜잭션 해시를 이름으로 한 파일을 둡니다. 파일 크기는 0KB 라서 정보는 파일 이름에만 있습니다[2]. 이 파일은 고급 논리 추출, 파일 시스템 추출, 물리 추출 세 가지 모두에서 나왔습니다[2].

시험에서 Coinomi 는 받은 거래 두 건(BTC 1건, DOGE 1건)의 해시를 이렇게 남겼지만, 보낸 거래(BTC·DOGE 각 1건)에 대한 파일은 나오지 않았습니다[2]. Coinbase 와 Atomic 은 캐시 폴더에 트랜잭션 ID 를 남기지 않았습니다[2].

### Atomic: WebView 쿠키

Atomic 은 앱 안의 WebView 쿠키 파일 `app_webview/Default/Cookies` 에 쿠키 16개를 남겼습니다[2]. 그중 `__cflb` 는 Cloudflare 부하 분산 쿠키로 만료 시각이 있습니다. 다른 쿠키 3개는 값에 사설 IP 주소와 포트가 들어 있고, 도메인이 `nano.atomicwallet.io`, `zeus.atomicwallet.io`, `solana.atomicwallet.io` 이며 만료 시각이 없습니다[2]. 이 쿠키들에는 사람을 특정할 만한 값이 없고, 쿠키를 만든 시각과 만료 시각 정도를 알 수 있습니다[2]. Coinomi 에서는 쿠키가 나오지 않았습니다[2].

같은 시험의 물리 추출에서는 비밀번호 파일 208개가 나왔는데, 이를 얻으려면 루팅이 필요했습니다. 그중 185개는 Google 이 관리하는 OAuth 2.0 파일이었고, 지갑 앱이 쓰는 OAuth 토큰은 없었습니다[2].

### MetaMask Mobile

`persistStore` 폴더의 파일 구조, 컨트롤러별 필드, 볼트의 모양은 Android 와 iOS 가 같으므로 [iOS 지갑 앱](ios-wallets.md)과 [MetaMask](../browser/metamask/index.md)에서 다룹니다.

Android 앱 매니페스트에는 `android:allowBackup="false"` 가 설정되어 있습니다[7]. 앱이 Android 백업 기능에 데이터를 내주지 않도록 한 설정이라서, 백업을 이용하는 추출 방식에서는 MetaMask 데이터가 나오지 않을 수 있습니다. 추출 방식별 차이는 Android 핸드북의 [조사 절차](https://urock-ailab.github.io/forensics-handbook/android/03-techniques/acquisition/investigation-process.html)에서 다룹니다.

앱의 일반 설정은 `react-native-mmkv` 의 MMKV 저장소에 저장합니다[8]. MMKV 파일 형식은 [iOS 지갑 앱](ios-wallets.md)에서 다룹니다. ALEAPP 는 MMKV 저장소를 `*/mmkv/*`, `*/mmkv_private/*` 경로 패턴으로 찾습니다[9].

## 증거로서 의미

### 증명하는 것

- BRD `kvStoreTable` 에 `txn2-` 키가 있으면, 이 기기의 BRD 앱이 그 트랜잭션 해시에 대한 메타데이터 레코드를 만들었고 `thetime` 의 시각에 기록했다는 것을 알 수 있습니다[1].
- Coinomi 캐시 폴더에 해시 이름 파일이 있으면, 이 기기의 Coinomi 가 그 해시의 거래를 받았다고 볼 수 있습니다. 이 해석은 Coinomi 9.26.3 시험에서 받은 거래에만 파일이 생긴 결과에 기댑니다[2].
- 찾은 해시를 블록 탐색기에서 조회하면 주소와 거래 시각을 확인할 수 있습니다[2]. 조회 방법은 [블록 탐색기 기록 읽기](../records/block-explorers.md)에서 다룹니다.
- BRD 설정 파일의 `userId` 는 이 기기의 앱 계정 식별자입니다[1].

### 증명하지 못하는 것

- BRD 의 암호화된 `value` 안에 있는 금액·상대방·메모는 알 수 없습니다[1].
- `phraseWritten` 이 참이라고 해서 사용자가 복구 문구를 종이에 적었다는 행동까지 말할 수는 없습니다[1].
- 시세 표는 앱이 받아 둔 시세일 뿐이고, 그 시세로 거래했다는 증거가 아닙니다[1].
- 블록 탐색기에서 본 상대 주소만으로 사람을 특정하지 못합니다. 시험에서 Coinbase 가 Coinomi 로 보낸 거래의 보내는 주소는 2021년 7월 기준 1,361번 거래했고 1억 달러 넘게 오간 주소였습니다[2]. 거래소 주소는 여러 고객이 함께 씁니다.
- 쿠키로는 사람을 특정하지 못하고, 쿠키를 만든 시각과 만료 시각 정도만 알 수 있습니다[2].

보고서에는 "이 기기의 `/data/data/com.breadwallet/databases/platform.db` 에 트랜잭션 해시 `3f9a…c21e`(만든 예시)를 키로 한 메타데이터 레코드가 있고, 처음 기록 시각은 2021-06-14 03:06:40 UTC(만든 예시)입니다. 같은 해시의 트랜잭션이 비트코인 블록체인에 있습니다." 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

BRD 의 `thetime` 과 `secureTime` 은 Unix epoch 밀리초입니다. ALEAPP 는 이 값을 1000 으로 나눠 초로 바꾼 뒤 UTC 로 표시합니다[1]. 예를 들어 `1623640000000`(만든 예시)은 2021-06-14 03:06:40 UTC 입니다. 이 값이 기기 시계로 쓴 것인지 서버가 준 것인지는 같은 해시의 블록 시각과 비교해서 판단합니다. 블록 시각의 성질은 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에서 다룹니다.

Coinomi 의 해시 이름 파일에는 시각 정보가 들어 있지 않습니다. 거래 시각은 해시로 블록 탐색기를 조회해서 블록 시각으로 확인합니다[2].

Atomic 쿠키의 만든 시각과 만료 시각은 UTC+0 기준 값입니다[2]. 쿠키 시각은 쿠키를 만들고 끝내는 시각이지 거래 시각이 아닙니다.

도구 화면의 시각이 UTC 인지 기기 현지 시각인지는 매번 확인합니다. Chang 외(2022) 논문에서는 Coinbase 가 Coinomi 로 보낸 같은 BTC 거래가 거래 표(Table V)에는 2021년 6월 14일 03:14 UTC 로, 파일 경로 표(Table VI)에는 2021년 6월 13일 23:15 로 적혀 있어 4시간 차이가 나고, 시간대 설명이 없습니다[2]. 여러 도구의 시각을 합칠 때는 [암호화폐 타임라인](../../03-techniques/analysis/timeline.md)의 방법으로 기준 시간대를 먼저 맞춥니다.

## 함정과 한계

- BRD `platform.db` 는 시험 이미지에서 내용 전체가 WAL 파일에만 있었습니다. `-wal` 파일 없이 열면 `kvStoreTable` 에 행이 하나도 없는 빈 DB 로 보입니다[1]. DB 를 수집할 때는 `-wal`·`-shm` 파일을 같이 가져옵니다. WAL 의 원리는 Android 핸드북의 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/data-formats/sqlite/)에서 다룹니다.
- 같은 키가 여러 버전으로 남으므로, 한 행만 보고 처음 기록 시각을 판단하지 않습니다[1].
- 추출 방식에 따라 보이는 흔적이 다릅니다. 시험에서 물리 추출을 하려면 부트로더 잠금을 풀고 커스텀 리커버리를 설치해야 했고, 루팅하지 않은 기기에서는 물리 추출이 되지 않았으며, 물리 추출이 없으면 일부 흔적이 빠졌습니다[2]. 흔적이 없다는 결과를 쓸 때는 어떤 추출 방식이었는지 함께 적습니다.
- MetaMask Mobile 은 백업을 막아 두었으므로[7], 백업 기반 추출에서 MetaMask 데이터가 없다고 앱을 쓰지 않았다고 판단하지 않습니다.
- 같은 거래를 두고 입력 주소와 출력 주소가 뒤바뀌어 적히는 일이 있습니다. Chang 외(2022) 논문 본문은 Coinomi 가 받은 BTC 거래에서 받는 주소를 "input address", 보내는 주소를 "output address" 이면서 "1 of the 33 inputs" 라고 적었습니다. 같은 논문의 거래 표는 보내는 주소를 From, 받는 주소를 To 로 두고 "1 of 33 outputs" 라고 적었습니다[2]. 주소의 방향은 블록 탐색기에서 직접 확인합니다.
- 같은 논문은 비트코인 주소를 "26~35자의 16진 문자열" 로 설명하지만[2], 비트코인 주소는 Base58Check 나 Bech32 로 인코딩합니다. 주소 형식은 [주소 형식](../../01-foundations/wallets/address-formats.md)의 기준으로 판단합니다.
- ALEAPP 의 Cash App 분석기는 `com.squareup.cash/databases/cash_money.db` 의 송금 거래를 읽는 분석기이고[11], Samsung Wallet 분석기는 Samsung Wallet(옛 Samsung Pay)에 등록한 카드를 읽는 분석기입니다[12]. 둘 다 암호화폐 지갑 분석기가 아닙니다.
- 공개 분석기가 없는 지갑 앱(현행 Trust Wallet, Exodus 모바일 등)은 파일 위치를 짐작하지 말고, 설치된 패키지 이름으로 앱 폴더를 찾은 뒤 그 안에서 주소·트랜잭션 ID 문자열을 검색합니다. 검색 방법은 [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md)와 [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스와 SQL 로 한 번

BRD `platform.db` 는 원본을 바꾸지 않도록 `platform.db`, `platform.db-wal`, `platform.db-shm` 세 파일을 같은 폴더에 복사한 뒤 복사본을 엽니다. 트랜잭션 메타데이터 레코드는 ALEAPP 와 같은 조건으로 뽑습니다[1].

```sql
SELECT key, version, thetime, deleted, length(value)
FROM kvStoreTable
WHERE key LIKE 'txn2-%'
ORDER BY key, version;
```

`value` 가 암호문인지 보려면 앞부분을 헥스로 봅니다. 모든 행이 같은 바이트로 시작하고 그 뒤가 무작위처럼 보이면 암호화된 값으로 봅니다[1]. 이 값은 풀려고 하지 않고, 크기와 머리 바이트만 기록합니다.

```sql
SELECT key, hex(substr(value, 1, 16)) FROM kvStoreTable ORDER BY key LIMIT 20;
```

Coinomi 캐시 폴더에서는 크기가 0 이고 이름이 헥스 64자인 파일을 찾습니다[2]. 추출한 앱 폴더에서 아래처럼 찾을 수 있습니다.

```sh
find com.coinomi.wallet/cache -type f -size 0 -regextype posix-extended -regex '.*/[0-9a-f]{64}'
```

### 공개 도구로 한 번

ALEAPP 의 `breadWallet.py` 는 BRD 흔적을 네 가지 보고서로 만듭니다. 트랜잭션 메타데이터 레코드(해시별 처음·마지막 기록 시각과 버전 수), 키-값 저장소 전체, 앱 상태 설정, 시세 캐시입니다. Android 10 시험 이미지에서 각각 3행, 38행, 11행, 443행이 나왔습니다[1].

ALEAPP 의 `mmkvCarved.py` 는 MMKV 저장소의 기록 크기 뒤 여유 공간에서 예전 레코드를 추정해서 꺼냅니다. 추정이라 틀린 행이 섞일 수 있습니다[9]. 시험 추출물 78개의 MMKV 저장소 1,840개(`.crc` 짝이 있는 파일 기준) 가운데 암호화되지 않은 1,710개 중 290개에서 기록 크기 뒤에 0 이 아닌 데이터가 있었습니다[9].

ALEAPP 의 `realmUndecodedStores.py` 는 `*.realm` 파일 가운데 번들 파서가 읽지 못한 것만 보여 줍니다. 여기에 나온 파일은 다른 도구로 열어 봐야 한다는 뜻이고, 앱이 어떤 데이터를 가졌다는 증거는 아닙니다[10].

## 교차 검증

- 블록체인: 앱에서 찾은 해시와 주소를 [블록 탐색기 기록 읽기](../records/block-explorers.md)의 방법으로 조회해서 금액·방향·블록 시각을 확인합니다.
- 거래소 앱과 메일: 지갑 앱과 거래소 계정 사이에 오간 거래는 거래소 알림 메일에도 남을 수 있습니다. 시험에서 Coinbase 가 보낸 메일 제목에는 받은 금액, 또는 보낸 금액과 받는 주소가 들어 있었습니다[2]. 자세한 내용은 [거래소 앱](exchange-apps.md)에서 다룹니다.
- 기기 공통 흔적: 지갑 앱의 알림은 Android 핸드북의 [알림 기록](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/app-usage/notification-history.html)에, 주소·QR 코드 화면은 [스크린샷과 화면 녹화](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/media/screenshots.html)에 남을 수 있습니다.
- 파생 주소: 앱에서 확장 공개 키나 파생 경로가 나오면 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)의 규칙으로 같은 지갑의 다른 주소를 확인합니다.
- 전체 흐름은 [이 기기로 지갑을 썼나](../../04-scenarios/device-use/wallet-use.md) 시나리오에서 다룹니다.

## 실습

테스트넷을 지원하는 지갑 앱을 시험용 Android 기기에 설치하고, 테스트넷 주소로 코인을 받은 뒤 한 번 보내고 나서 앱 폴더를 추출해 아래 질문을 풀어 봅니다.

1. 앱 폴더에서 받은 거래와 보낸 거래의 트랜잭션 ID 가 각각 어느 파일에, 평문과 암호문 중 어떤 모양으로 남는가?
2. DB 를 `-wal` 파일과 함께 열 때와 빼고 열 때 행 수가 어떻게 다른가?
3. 앱에 남은 시각과 블록 탐색기의 블록 시각은 몇 초 차이가 나고, 어느 쪽이 먼저인가?
4. 파일 시스템 추출과 백업 기반 추출에서 보이는 파일이 어떻게 다른가?

## 참고 문헌

1. ALEAPP, `scripts/artifacts/breadWallet.py`. https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/breadWallet.py
2. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, "Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications", arXiv, 2022. doi:10.48550/arXiv.2205.14611
3. MetaMask Mobile, `app/store/persistConfig/index.ts`. https://github.com/MetaMask/metamask-mobile/blob/main/app/store/persistConfig/index.ts
4. MetaMask Mobile, v7.59.0 `app/store/persistConfig.ts` 와 v7.60.0 `app/store/persistConfig/index.ts`. https://github.com/MetaMask/metamask-mobile/blob/v7.59.0/app/store/persistConfig.ts , https://github.com/MetaMask/metamask-mobile/blob/v7.60.0/app/store/persistConfig/index.ts
5. redux-persist-filesystem-storage, `index.js`. https://github.com/robwalkerco/redux-persist-filesystem-storage/blob/master/index.js
6. react-native-blob-util, `ReactNativeBlobUtilFS.java`(0.19.9)·`ReactNativeBlobUtilFS.kt`(master). https://github.com/RonRadtke/react-native-blob-util/blob/0.19.9/android/src/main/java/com/ReactNativeBlobUtil/ReactNativeBlobUtilFS.java , https://github.com/RonRadtke/react-native-blob-util/blob/master/android/src/main/java/com/ReactNativeBlobUtil/ReactNativeBlobUtilFS.kt
7. MetaMask Mobile, `android/app/build.gradle`, `android/app/src/main/AndroidManifest.xml`. https://github.com/MetaMask/metamask-mobile/blob/main/android/app/build.gradle , https://github.com/MetaMask/metamask-mobile/blob/main/android/app/src/main/AndroidManifest.xml
8. MetaMask Mobile, `app/store/storage-wrapper.ts`. https://github.com/MetaMask/metamask-mobile/blob/main/app/store/storage-wrapper.ts
9. ALEAPP, `scripts/artifacts/mmkvCarved.py`. https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/mmkvCarved.py
10. ALEAPP, `scripts/artifacts/realmUndecodedStores.py`. https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/realmUndecodedStores.py
11. ALEAPP, `scripts/artifacts/cashApp.py`. https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/cashApp.py
12. ALEAPP, `scripts/artifacts/Samsungwallet.py`. https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/Samsungwallet.py
