---
title: "하드웨어 지갑과 연결 흔적"
parent: "아티팩트 · 하드웨어 지갑"
nav_order: 230
---

# 하드웨어 지갑과 연결 흔적 (Ledger·Trezor)

하드웨어 지갑은 개인 키를 장치 안에 두고 서명만 장치에서 하기 때문에, 장치를 연결한 PC 에는 개인 키 대신 관리 앱의 데이터·로그, 운영체제의 USB 장치 기록, 하드웨어 지갑을 연동한 다른 지갑의 설정이 남습니다. Ledger Live 의 `app.json` 은 암호 잠금을 켜도 연결한 장치의 모델·펌웨어 버전이 평문으로 남고, 잠금이 없으면 확장 공개 키와 거래 내역까지 보입니다. 이 흔적으로는 "이 PC 에서 어느 모델의 하드웨어 지갑을 관리했고 어떤 계정을 보고 있었다" 까지 확인되고, 실제 송금은 블록체인 기록으로 따로 확인합니다.

## 무엇을 기록하나 · 왜 생기나

하드웨어 지갑은 서명 전용 지갑 (signing-only wallet)을 돌리는 전용 장치입니다. 장치가 부모 공개 키를 PC 쪽 프로그램에 넘기면, PC 쪽 프로그램이 주소를 만들고 서명하지 않은 트랜잭션을 만들어 장치로 보냅니다. 사용자가 장치 화면에서 내용을 확인하고 장치에 따라 암호나 PIN 을 넣으면 장치가 서명해 돌려주고, PC 쪽 프로그램이 이 트랜잭션을 네트워크에 방송합니다[1]. 개인 키는 장치 안의 보안 요소 (secure element) 밖으로 나오지 않습니다[52]. 지갑 종류별로 키가 어디에 있는지는 [지갑의 종류](../../01-foundations/wallets/wallet-types.md)에서 다룹니다.

PC 쪽 프로그램은 주소를 만들고 잔액을 보여 주려고 확장 공개 키 (extended public key, xpub)와 거래 내역을 받아 두고, 장치 연결을 관리하려고 장치 정보를 저장합니다. 그래서 흔적은 다섯 곳에서 찾습니다.

- **관리 앱의 데이터.** Ledger Live 는 JSON 파일 `app.json` 에, Trezor Suite 는 IndexedDB 데이터베이스 `trezor-suite` 에 계정·거래·장치 정보를 저장합니다[5][23].
- **관리 앱과 연결 프로그램의 로그.** Ledger Live 가 내보낸 로그 파일, Trezor Suite 로그 파일, Trezor Bridge 로그 파일입니다. 셋 다 사용자가 내보내거나 실행 인자를 줬을 때만 파일이 생깁니다[20][27][31].
- **운영체제의 USB 장치 기록.** 장치를 꽂으면 제조사 ID (Vendor ID, VID)와 제품 ID (Product ID, PID)가 장치 설치 로그와 레지스트리에 남습니다[38][39].
- **하드웨어 지갑을 연동한 다른 지갑.** MetaMask 와 Electrum 은 하드웨어 지갑으로 서명하는 계정을 따로 표시해 저장합니다[44][45].
- **메모리.** 관리 앱이 실행 중일 때 프로세스 메모리에 확장 공개 키·거래 내역·장치 정보가 있을 수 있습니다[52].

## 위치와 버전별 차이

Ledger Live 의 데이터 폴더는 환경 변수 `LEDGER_CONFIG_DIRECTORY` 가 있으면 그 값이고, 없으면 Electron 의 `userData` 폴더입니다[2]. Electron 의 `userData` 는 기본적으로 `appData` 폴더 아래 앱 이름 폴더이고, `appData` 는 Windows 에서 `%APPDATA%`, macOS 에서 `~/Library/Application Support`, Linux 에서 `$XDG_CONFIG_HOME` 또는 `~/.config` 입니다[3]. 앱의 제품 이름은 현재 "Ledger Wallet" 이지만(`package.json` 의 `productName`, 4.21.1 기준)[4], 앱은 시작할 때 `userData` 폴더 이름의 "Ledger Wallet" 을 "Ledger Live" 로 바꿔 씁니다. 다만 `LEDGER_CONFIG_DIRECTORY` 가 있거나, 기본 폴더 이름이 앱 이름으로 끝나지 않거나, 기본 폴더(`Ledger Wallet`)에 이미 `app.json` 이 있으면 바꾸지 않습니다[2]. 그래서 `Ledger Live` 폴더와 `Ledger Wallet` 폴더를 모두 확인합니다. Electron 앱 폴더의 공통 구조는 Windows 핸드북의 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/)에서 다룹니다.

Trezor Suite 데스크톱의 `userData` 폴더 이름은 서명된 배포판이 `@trezor/suite-desktop`, 개발 빌드가 `@trezor/suite-desktop-dev`, 로컬 개발판이 `@trezor/suite-desktop-local` 입니다. 이 이름은 이미 설치된 앱의 디스크 위치라서 옛 패키지 이름을 그대로 씁니다[26]. IndexedDB 는 이 폴더 아래의 Chromium 저장소에 있으므로 하위 폴더 이름은 실제 데이터로 확인합니다. 웹판 Trezor Suite 는 브라우저 프로필의 IndexedDB 에 같은 데이터베이스를 만듭니다[23].

| 프로그램 | 위치 | 조건과 버전 |
|---|---|---|
| Ledger Live 데스크톱 | Windows `%APPDATA%\Ledger Live\app.json`, macOS `~/Library/Application Support/Ledger Live/app.json`, Linux `~/.config/Ledger Live/app.json` | `Ledger Wallet` 폴더와 `LEDGER_CONFIG_DIRECTORY` 도 확인[2][3] |
| Ledger Live 내보낸 로그 | 사용자가 저장한 위치의 `ledgerwallet-logs-*.txt` | 사용자가 "로그 내보내기" 를 눌렀을 때만[20] |
| Trezor Suite 데스크톱 | Windows `%APPDATA%\@trezor\suite-desktop\` 아래 IndexedDB `trezor-suite` | macOS·Linux 는 위 `appData` 폴더 아래 같은 이름[3][23][26] |
| Trezor Suite 웹 | 브라우저 프로필의 IndexedDB `trezor-suite` | 해당 사이트 출처 폴더[23] |
| Trezor Suite 로그 | `userData` 아래 `logs\trezor-suite-log-*.txt` | 실행 인자 `--log-write` 가 있을 때만[27] |
| Trezor Bridge (Windows) | `%APPDATA%\TREZOR Bridge\trezord.log`, 같은 폴더 `wdi-log.txt` | 로그 파일은 버전·실행 방식에 따라 없음[32][33] |
| Trezor Bridge (macOS) | `/Library/LaunchAgents/com.bitcointrezor.trezorBridge.trezord.plist`, 실행 파일 `/Applications/Utilities/TREZOR Bridge/trezord` | [34] |
| Trezor Bridge (Linux) | systemd `trezord.service`, 실행 파일 `/usr/bin/trezord`, 사용자 `trezord` | [35] |
| Windows USB 기록 | `%SystemRoot%\inf\SetupAPI.dev.log`, SYSTEM 하이브의 `CurrentControlSet\Enum` | [38][39][40] |

버전에 따라 달라지는 점은 아래와 같습니다.

- **Ledger Live.** 제품 이름이 Ledger Wallet 으로 바뀌었고 데이터 폴더 이름은 위 조건에 따라 달라집니다[2][4]. 계정 ID 형식은 2018-10-10 에 바뀌었고, 앱은 옛 형식(`libcore`·`ethereumjs`·`ripplejs`)의 계정을 읽을 때 새 형식으로 옮깁니다[12]. 메모리 연구는 Ledger Live 1.18.2 로 시험했습니다[52].
- **Trezor.** 메모리 연구에 쓰인 Trezor Wallet 1.8.3 은 Trezor Bridge 를 거쳐 장치와 통신하는 웹 앱이고[52], 이 페이지에서 다루는 Trezor Suite 와는 다른 앱입니다. Trezor Bridge 는 2.0.31(2021-03-12)부터 변경 기록에 "in Trezor Suite" 로 표시되고, 마지막 판은 2.0.33(2023-04-19)입니다[36].
- **Trezor Suite 데이터베이스.** 스키마 버전이 13 보다 낮은 옛 데이터베이스는 통째로 지우고 새로 만듭니다[23]. 코드의 스키마 정의는 최신판 기준이고, 실제 IndexedDB 에는 마이그레이션에서 지우지 않은 옛 값이 남아 있을 수 있습니다[23].

## 구조

### Ledger Live 의 `app.json`

Ledger Live 는 저장 공간(네임스페이스)마다 `이름.json` 파일을 하나씩 만들고, 파일 내용은 `{"data": {...}}` 한 겹으로 감싼 JSON 입니다[5]. 앱 데이터는 `app.json` 에 들어 있고, 불러올 때 받아들이는 최상위 키는 아래 목록뿐이며 목록에 없는 키는 버립니다[5].

`accounts`, `countervalues`, `postOnboarding`, `settings`, `trustchain`, `wallet`, `market`, `marketBanner`, `largeScreenUpsellModal`, `payCard`, `knownDevices`, `cryptoAssets`, `identities`, `featureFlags`, `coinConfigOverrides`, `discover`, `ptx`, `history`, `PLAYWRIGHT_RUN`

옛 키 `user` 는 이를 대신하는 `identities` 가 저장될 때까지 남습니다[5]. 앱은 값이 바뀌면 500ms 동안 더 바뀌는 것이 없을 때 파일 전체를 다시 쓰고[5], 쓸 때는 임시 파일에 먼저 쓰고 바꿔치는 `write-file-atomic` 을 씁니다[5]. 시작할 때는 데이터 폴더에서 정규식 `^app\.json\..+$` 에 맞는 파일, 곧 쓰다 남은 임시 파일을 지웁니다[2][7].

사용자가 앱에 암호 잠금을 켜면 `accounts`·`trustchain`·`wallet` 세 키만 암호화된 문자열이 되고 나머지 키는 평문 JSON 그대로입니다[5]. 암호화된 값은 base64 문자열이고, 이 문자열을 base64 로 풀면 앞 16바이트 뒤 17번째 바이트가 `:`(0x3A)입니다. 17번째 바이트가 `:` 가 아니면 옛 방식으로 암호화한 값입니다[6]. 그래서 `accounts` 가 배열이면 잠금이 없는 상태, 문자열이면 잠금 상태로 읽습니다. `trustchain` 에는 이 PC 에만 저장하는 멤버 자격 증명(`memberCredentials`)과 서버에서 받은 트러스트체인(`trustchain`)이 들어갑니다[21].

### 계정 ID

계정 ID 는 `type:version:currencyId:xpubOrAddress:derivationMode` 를 콜론으로 이은 문자열이고, 뒤에 `customData` 가 더 붙을 수 있습니다[9]. `xpubOrAddress` 안의 `::` 는 `~!colons!~` 로 바꿔 저장하고, 토큰 계정의 ID 는 부모 계정 ID 뒤에 `+` 와 인코딩한 토큰 ID 를 붙입니다[9]. 비트코인 계정 ID 에는 통화 ID, xpub, 파생 방식(`legacy`, `segwit`, `native_segwit`, `taproot`)이 들어 있습니다[10]. 이더리움 계정은 `xpubOrAddress` 자리에 주소가 오고 파생 방식이 빈 문자열일 수 있습니다[22].

```text
js:2:bitcoin:xpub68Gmy5EdvgibQVfPdqkBBCHxA5htiqg55crXYuXoQRKfDBFA1WEjWgP6LHhwBZeNK1VTsfTFUHCdrfp1bgwQ9xv5ski8PX9rL2dZXvgGDnw:native_segwit
js:2:ethereum:0xAbC0000000000000000000000000000000000123:
```

위 두 줄은 형식만 보여 주려고 만든 예시입니다. 첫 줄의 xpub 은 BIP-32 명세의 시험 벡터 1 에 실린 `m/0H` 확장 공개 키이고[49], 둘째 줄의 주소는 지어낸 값입니다. 계정 ID 만으로 xpub 이나 이더리움 주소가 평문으로 드러나므로, 잠금 상태라도 계정 ID 가 들어 있는 다른 곳(아래 `starredAccountIds`, 내보낸 로그)을 찾아봅니다.

파생 방식 값은 BIP 목적 번호와 연결됩니다. `taproot` 은 purpose 86, `native_segwit` 은 84, `segwit` 은 49 이고, 빈 문자열은 기본 경로입니다. 이더리움 계열에는 `ethM`(`44'/60'/0'/계정`), `ethMM`(`44'/60'/0'/0/계정`), `etcM` 같은 값이 있습니다[11]. 경로의 뜻은 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)에서 다룹니다.

### 계정과 거래 레코드

잠금이 없을 때 `accounts` 에는 계정마다 레코드가 하나씩 들어 있고, 계정 데이터(AccountRaw)의 필드는 아래와 같습니다[8]. 레코드를 감싸는 모양은 앱 버전에 따라 다를 수 있어서 실제 파일로 확인합니다.

| 필드 | 내용 |
|---|---|
| `id` | 위 형식의 계정 ID |
| `seedIdentifier` | 복구 문구를 구분하는 값 |
| `xpub` | 확장 공개 키(있을 때만) |
| `derivationMode`, `index` | 파생 방식과 계정 번호 |
| `freshAddress`, `freshAddressPath` | 다음에 받을 주소와 그 경로 |
| `name`, `starred`, `used` | 사용자가 붙인 이름, 즐겨찾기, 사용 여부 |
| `balance`, `spendableBalance`, `blockHeight` | 앱이 마지막으로 받은 잔액과 블록 높이 |
| `creationDate`, `operationsCount` | 계정의 가장 오래된 거래 날짜(빈 계정은 앱이 계정을 만든 시각), 거래 수 |
| `currencyId`, `feesCurrencyId` | 통화, 수수료 통화 |
| `operations`, `pendingOperations` | 거래 목록, 확정 전 거래 목록 |
| `subAccounts`, `nfts`, `swapHistory` | 토큰 계정, NFT, 교환 내역 |

거래(OperationRaw)에는 `id`, `hash`, `type`, `value`, `fee`, `senders`, `recipients`, `blockHeight`, `blockHash`, `accountId`, `hasFailed`, `date`, `extra` 필드가 있고, 토큰·NFT 거래는 `subOperations`, `internalOperations`, `nftOperations` 에 따로 들어갑니다[8]. 앱은 저장할 때 거래 목록에서 앞에서부터 500개 안에 들거나 366일이 지나지 않은 거래만 남깁니다[12]. 그래서 `app.json` 의 거래 목록은 계정의 전체 거래 내역이 아닙니다.

### 장치 정보: `settings` 와 `knownDevices`

`settings` 와 `knownDevices` 는 잠금과 관계없이 평문입니다[5]. `settings` 에서 장치와 관련된 필드는 아래와 같습니다[14].

| 필드 | 내용 |
|---|---|
| `lastSeenDevice` | 마지막으로 본 장치의 모델 ID, 장치 정보, 설치된 앱 목록 |
| `devicesModelList` | 연결된 적이 있는 모델 ID 목록(중복 없음) |
| `latestFirmware` | 마지막으로 확인한 펌웨어 업데이트 정보 |
| `lastOnboardedDevice` | 마지막으로 초기 설정을 마친 장치 |
| `preferredDeviceModel` | 선호 모델 |
| `hasCompletedOnboarding`, `hasInstalledApps` | 초기 설정 완료, 앱 설치 여부 |
| `lastUsedVersion` | 마지막으로 쓴 앱 버전 |
| `starredAccountIds` | 즐겨찾기한 계정 ID 목록 |
| `language`, `locale`, `counterValue` | 언어, 지역 형식, 환산 통화 |

`lastSeenDevice` 는 `modelId`, `deviceInfo`, `apps`(앱마다 `name`·`version`)로 이뤄집니다. `deviceInfo` 에는 `version`, `mcuVersion`, `seVersion`, `bootloaderVersion`, `hardwareVersion`, `targetId`, `isBootloader`, `onboarded`, `languageId`, `providerName` 같은 필드가 있고, 장치 일련번호 필드는 없습니다[15]. 앱이 장치 정보를 새로 읽으면 `lastSeenDevice` 와 `latestFirmware` 를 바꾸고, 새 모델이 연결되면 `devicesModelList` 에 더합니다[14].

`knownDevices` 는 `{"knownDevices": [...]}` 모양이고, 항목마다 `transport`, `deviceModelId`, `id`, `name` 이 있습니다[16]. 데스크톱은 WebHID 로 장치에 연결하는데 WebHID 가 장치마다 고정된 식별자를 주지 않아서, 앱은 `transport` 를 `webhid`, `id` 를 빈 문자열로 두고 `deviceModelId` 로만 장치를 구분합니다[16]. 같은 모델은 한 항목으로 합치고, 새 정보에 이름이 없으면 예전 이름을 남깁니다[16]. `name` 에는 장치 이름(`deviceName`)이 들어갈 수 있습니다[16].

```json
{"data":{
  "settings":{"devicesModelList":["nanoX"],
    "lastSeenDevice":{"modelId":"nanoX",
      "deviceInfo":{"version":"2.2.3","seVersion":"2.2.3","isBootloader":false,"onboarded":true},
      "apps":[{"name":"Bitcoin","version":"2.1.0"},{"name":"Ethereum","version":"1.10.3"}]},
    "starredAccountIds":["js:2:bitcoin:xpub6C…:native_segwit"]},
  "knownDevices":{"knownDevices":[{"transport":"webhid","deviceModelId":"nanoX","id":"","name":"My Nano"}]},
  "accounts":"nyE4cW0v…(base64 문자열)"
}}
```

위 JSON 은 필드 모양만 보여 주려고 만든 예시이고, 실제 파일에는 다른 키가 더 있습니다. 모델 ID 문자열은 `blue`, `nanoS`, `nanoSP`(Nano S Plus), `nanoX`, `stax`, `europa`(Ledger Flex), `apex`(Ledger Nano Gen5)입니다[17].

### Ledger Live 의 내보낸 로그

Ledger Live 는 앱 로그를 정해진 개수(`EXPORT_MAX_LOGS`)까지 메모리에만 쌓아 두고 디스크에 쓰지 않습니다[19]. 사용자가 로그를 내보내면 저장 창의 기본 파일 이름이 `ledgerwallet-logs-<날짜>-<git 리비전>.txt` 이고, 내보내기 직전에 `exportLogsMeta` 항목으로 앱 버전, userAgent, 환경 변수, 계정 ID 목록(`accountsIds`)을 남깁니다[20]. 내보낸 파일은 JSON 항목의 목록이고, 항목마다 `logIndex`, `timestamp`, `pname`(`electron-renderer`, `electron-internal` 등), `type`, `level`, `id`, `message`, `data`, `context` 순서로 키가 있습니다[19]. 옛 버전의 기본 파일 이름은 다를 수 있으므로 `ledger*-logs-*` 로 넓게 찾습니다.

### Trezor Suite 의 IndexedDB

Trezor Suite 는 IndexedDB 데이터베이스 `trezor-suite` 에 저장소(object store)를 여러 개 만듭니다[23]. 조사에 쓸 만한 저장소는 아래와 같습니다.

| 저장소 | 내용 |
|---|---|
| `devices` | 기억한 기기의 객체. 저장할 때 연결 경로 `path` 만 빈 문자열로 바꿉니다[25] |
| `accounts` | 계정. 인덱스 `deviceState`[23] |
| `txs` | 거래. 인덱스 `accountKey`(descriptor·symbol·deviceState), `txid`, `deviceState`, `order`, `blockTime`[23] |
| `walletSettings`, `suiteSettings`, `backendSettings` | 지갑·앱·백엔드 설정[23] |
| `historicRates`, `graph` | 시세와 잔액 그래프 캐시[23] |
| `sendFormDrafts`, `formDrafts` | 보내기 화면 등에 쓰다 만 입력값[23] |
| `tradingTrades` | 매매 기능의 거래 기록[23] |
| `metadata` | 메타데이터 설정[23] |
| `firmware`, `persistentDeviceData` | 펌웨어·기기 관련 데이터[23] |
| `connect` | 앱 권한[23] |
| `bluetooth` | Bluetooth 로 연결한 적이 있는 장치 목록(`knownDevices`)[23] |

표의 설명은 저장소 이름과 코드의 타입 정의로 정리한 것이므로 값의 실제 모양은 실제 데이터로 확인합니다.

나머지 저장소 이름은 `bioAuth`, `phishing`, `phishingMetadata`, `explorer`, `earnOnboarding`, `receive`, `thp`, `tokenManagement`, `coinjoinAccounts`, `coinjoinDebugSettings`, `analytics`, `suiteSyncSettings`, `suiteSyncOwners`, `suiteSyncQuotaManager`, `messageSystem`, `featureFeedback`, `discreetMode`, `debug` 입니다[23].

Trezor Suite 는 계정·거래처럼 기기에 딸린 데이터를 "기억한 기기 (remembered device)" 일 때만 저장합니다[24]. 새로 연결한 기기의 기본값은 `remember: false` 이고, 사용자가 기억하기를 켜면 저장하고 기기를 잊으면 지웁니다[24][25]. 그래서 기억하지 않은 기기로만 쓴 경우 IndexedDB 에 계정과 거래가 없을 수 있습니다.

기기 객체에는 `remember`, `connected`, `instance`, `ts`, `firstConnectedTimestamp`, `walletNumber`, `metadata` 같은 필드가 있습니다[25]. `ts` 는 기기를 연결할 때와 앱이 기기 시각을 갱신할 때마다 현재 시각으로 바뀌고, `firstConnectedTimestamp` 는 처음 한 번만 채웁니다[25]. 앱은 장치가 잠겨 있어도 이전에 받은 장치 정보(features)를 계속 기억하도록 만들어져 있어서[25], 기기 객체에 장치가 보고한 Features 필드가 함께 들어 있을 가능성이 있습니다. Features 에는 `device_id`(장치 고유 식별자), `label`(사용자가 붙인 장치 이름), `model`, `internal_model`, 펌웨어 버전(`major_version`·`minor_version`·`patch_version`), `bootloader_hash`, `pin_protection`, `passphrase_protection`, `unit_btconly` 같은 필드가 있습니다[29]. 저장소 형식은 Windows 핸드북의 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)와 Mac 핸드북의 [LevelDB와 IndexedDB](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/data-formats/leveldb-indexeddb.html)에서 다룹니다.

### Trezor Suite 와 Trezor Bridge 의 로그

Trezor Suite 데스크톱은 기본적으로 로그를 디스크에 쓰지 않고, 실행 인자 `--log-write` 가 있을 때만 파일을 만듭니다[27]. 파일 이름 기본값은 `trezor-suite-log-%tt.txt`, 위치 기본값은 `userData` 아래 `logs` 이고, `--log-file`·`--log-path` 로 바꿀 수 있습니다[27]. `%tt` 는 ISO 8601 시각에서 밀리초를 떼고 `:` 를 `-` 로 바꾼 값이고, 줄 형식은 `%dt - %lvl(%top): %rep%msg` 이며 `%dt` 는 UTC ISO 8601 시각입니다[27].

Trezor Bridge(`trezord`)는 웹 페이지가 Trezor 와 통신하도록 `http://localhost:21325` 에서 동작하는 작은 HTTP 서버이고, trezor.io 하위 도메인의 요청만 받습니다[30]. Firefox 가 WebUSB 를 허용하지 않고 2018년까지 나온 펌웨어는 HID 만 지원해서 Bridge 가 필요했습니다[30]. Bridge 는 `-l` 인자로 파일 이름을 주면 그 파일에 로그를 쓰고 20MB 마다 파일을 돌려 백업 3개를 남기며, 인자가 없으면 표준 오류로만 씁니다[31]. 시작할 때 `trezord v버전 (rev 해시) is starting on port 포트` 줄을 남깁니다[31].

Windows 판 Bridge 의 상태 페이지는 `%AppData%\TREZOR Bridge\trezord.log`(이전 로그), 같은 폴더의 `wdi-log.txt`(USB 드라이버 재설치 로그), `%SystemRoot%\inf\SetupAPI.dev.log` 를 읽어 보여 줍니다[32]. 현재 Windows 설치 스크립트는 시작 메뉴 `TREZOR Bridge` 폴더와 모든 사용자의 시작프로그램 폴더에 `TREZOR Bridge.lnk` 를 만들고, 이 바로 가기는 `-l` 인자 없이 `trezord.exe` 를 실행합니다[33]. 설치 폴더는 레지스트리 `HKLM\Software\TREZOR\Bridge` 의 `InstallDir` 값에서 읽습니다[33]. `-l` 없이 실행하면 로그 파일이 생기지 않으므로, `trezord.log` 가 있는지는 버전과 실행 방식에 따라 다릅니다. 실제 데이터에서 `%AppData%\TREZOR Bridge\` 폴더를 확인합니다.

Bridge 2.0.27 과 Trezor Wallet 으로 시험한 연구에서는, Bridge 가 Trezor Wallet 이 실행되는 동안 연결된 USB 장치 목록을 계속 확인하면서 사용자 Application Data 폴더의 로그에 USB 장치 연결 시각을 남겼고, Trezor 가 아닌 장치도 기록했습니다[52].

### USB 장치 식별자

Windows 는 USB 장치를 `USB\VID_v(4)&PID_d(4)&REV_r(4)` 형식의 ID 로, 기능이 여러 개인 복합 장치의 인터페이스는 `USB\VID_v(4)&PID_d(4)&MI_z(2)` 형식으로 부릅니다. VID·PID 는 장치 디스크립터의 `idVendor`·`idProduct` 에서 온 4자리 16진수입니다[38]. 이 ID 는 `SetupAPI.dev.log` 와 SYSTEM 하이브의 `Enum` 아래에 남습니다[39][40].

| 장치 | VID | PID |
|---|---|---|
| Ledger HW.1·Nano(옛 장치) | `2581` | `1B7C`, `2B7C`, `3B7C`, `4B7C`[18] |
| Ledger Blue·Nano S 이후 모델 | `2C97` | 아래 규칙[17][18] |
| Trezor One (HID) | `534C` | `0001`[28] |
| Trezor (WebUSB, 부트로더) | `1209` | `53C0`[28] |
| Trezor (WebUSB, 펌웨어) | `1209` | `53C1`[28] |

Ledger 의 PID 는 `MMII` 형식입니다. 앞 바이트 MM 이 모델이고(Blue `00`, Nano S `10`, Nano X `40`, Nano S Plus `50`, Stax `60`, Flex `70`, Nano Gen5 `80`), 뒤 바이트 II 는 지원하는 인터페이스를 비트로 표시합니다(일반 HID `01`, 키보드 HID `02`, U2F `04`, CCID `08`, WebUSB `10`)[17]. 옛 펌웨어가 쓰는 PID 는 Nano S `0001`, Nano X `0004`, Nano S Plus `0005`, Stax `0006`, Flex `0007`, Nano Gen5 `0008` 입니다[17]. Ledger 코드는 PID 가 옛 PID 목록에 있으면 그것으로, 아니면 PID 를 오른쪽으로 8비트 밀어 모델을 찾습니다[17]. 예를 들어 `USB\VID_2C97&PID_4015` 는 모델 `40`(Nano X)에 인터페이스 `15`(WebUSB `10` + U2F `04` + 일반 HID `01`)로 읽습니다(명세로 만든 예시).

Ledger·Trezor 의 인터페이스 목록에는 대용량 저장 장치가 없습니다[17][28]. Windows 에서 HID 장치는 HID 클래스 드라이버(hidclass.sys)가 맡습니다[41]. 그래서 하드웨어 지갑은 USB 저장 장치 기록(`USBSTOR`)이 아니라 일반 USB·HID 장치 기록으로 찾습니다. USB 기록 읽는 법은 Windows 핸드북의 [USB 저장장치 흔적](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/external-devices/usb-storage-artifacts/), Mac 핸드북의 [USB 저장 장치](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/external-devices/usb/), Linux 핸드북의 [USB 장치 연결 기록](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/devices/usb.html)에서 다룹니다.

### 다른 지갑에 남는 연동 기록

**MetaMask.** MetaMask 는 하드웨어 지갑 계정을 키링 형식 `Ledger Hardware`, `Trezor Hardware` 로 관리합니다[42][43]. 키링의 세부 값(`hdPath`, `accounts`, Ledger 의 `deviceId` 등)은 암호화된 볼트 안에 있습니다[42][43]. 볼트를 풀지 않아도, 디스크에 저장되는 AccountsController 의 `internalAccounts` 에서 계정마다 `metadata.keyring.type` 과 계정을 추가한 시각 `importTime`, 마지막으로 고른 시각 `lastSelected` 를 볼 수 있습니다[44]. `keyring.type` 이 `Ledger Hardware` 나 `Trezor Hardware` 인 계정은 하드웨어 지갑으로 서명하는 계정입니다. 저장 위치와 읽는 법은 [MetaMask](../browser/metamask/index.md), 키링 형식 문자열 전체는 [지갑의 종류](../../01-foundations/wallets/wallet-types.md)에서 다룹니다.

**Electrum.** Electrum 은 하드웨어 지갑 키스토어를 `type` 이 `hardware` 인 값으로 저장하고, 여기에 `hw_type`, `xpub`, `derivation`, `root_fingerprint`, `label`, `soft_device_id` 를 넣습니다[45]. `soft_device_id` 는 같은 종류의 장치가 여러 대일 때 한 대를 구분하는 값입니다[46]. Trezor 플러그인은 장치 Features 의 `device_id` 를, Ledger 플러그인은 마스터 키 지문(fingerprint)을 16진수로 이 필드에 씁니다[47][48]. Electrum 은 장치를 고를 때 `soft_device_id` 가 같은 장치, `label` 이 같은 장치, 저장된 `label`·`soft_device_id` 가 없고 연결된 장치가 한 대뿐인 경우 순서로 자동 선택합니다[46]. 하드웨어 키스토어에는 암호가 걸리지 않습니다(`may_have_password` 가 False)[45].

```json
{"type":"hardware","hw_type":"trezor","xpub":"zpub6r…","derivation":"m/84'/0'/0'",
 "root_fingerprint":"1a2b3c4d","label":"My Trezor","soft_device_id":"8F3A1C0E5B7D9A2E4C6B1D3F"}
```

위 값은 필드 모양만 보여 주려고 만든 예시입니다. `root_fingerprint` 는 루트 키 식별자의 앞 32비트이고, 다른 키와 우연히 같을 수 있습니다[49]. 지갑 파일 전체 구조와 파일 암호화 여부는 [Electrum](../desktop/electrum.md)에서 다룹니다.

### 메모리

Memory FORESHADOW 연구는 Windows 7 SP1 64비트 가상 머신에서 Ledger Nano X(펌웨어 1.2.4)와 Ledger Live 1.18.2, Trezor One(펌웨어 1.8.3)과 Trezor Wallet 1.8.3·Trezor Bridge 2.0.27 을 쓰면서 60초 간격으로 메모리를 떠서 Volatility 2.6 과 YARA 로 분석했습니다[52]. 이 조건에서 나온 결과는 아래와 같습니다.

- **Ledger Live.** 메모리에 모델 ID, 언어, 지역, 앱 버전, 장치 USB ID, OS 와 OS 버전, 동기화된 확장 공개 키, 거래 내역·잔액·파생 경로·새 주소가 있었습니다[52]. 앱 내부 명령·IPC 메시지·API 요청 URL 에도 공개 키·거래 내역·지갑 주소가 들어 있었습니다[52]. 앱 잠금 암호는 메모리에서 나오지 않았습니다[52].
- **Trezor Wallet.** Firefox·Chrome 모두에서 장치 고유 ID, 펌웨어·부트로더 버전, 부트로더 해시, 백업 여부, 모델 ID, 동기화된 확장 공개 키가 든 JSON 이 나왔습니다[52]. Chrome 에서는 사용자가 설정한 암호(passphrase)도 평문으로 남아 있었고 Firefox 에서는 나오지 않았습니다[52]. 메모리 이미지는 이런 비밀 값을 담을 수 있으므로 증거물로 다룰 때 접근을 제한합니다.
- **Trezor Bridge.** 실행 중에는 로그 파일이 열려 있어서 Volatility 의 `dumpfiles` 로 메모리 이미지에서 파일을 꺼낼 수 있었습니다[52].

연구의 결론은 메모리만으로 하드웨어 지갑 사용을 확인하고, 거래 내역을 뽑고, 특정 장치를 그 PC 와 연결할 수 있다는 것입니다[52]. 이 연구가 공개한 저장소(현재 `BiTLab-BaggiliTruthLab/FORESHADOW`)에는 README 와 시각화 스크립트만 있고 Volatility 플러그인 코드는 없습니다[55]. 메모리 수집과 분석 절차는 Windows 핸드북의 [메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/)에서 다룹니다.

## 증거로서 의미

### 증명하는 것

- **Ledger Live 로 관리한 계정.** 잠금이 없는 `app.json` 의 `accounts` 로, 이 PC 의 Ledger Live 가 관리한 계정의 xpub·주소·파생 방식과 저장된 거래의 해시·금액·날짜를 알 수 있습니다[8][9]. 잠금 상태에서도 `starredAccountIds` 와 내보낸 로그의 `accountsIds` 에 계정 ID 가 있으면 그 계정의 xpub 이나 주소를 알 수 있습니다[14][20].
- **연결된 적이 있는 Ledger 모델.** 잠금과 관계없이 `settings.lastSeenDevice`(모델·펌웨어 버전·설치된 앱 목록), `devicesModelList`, `knownDevices` 로 "어느 모델의 Ledger 가 이 앱에 연결된 적이 있다" 를 확인합니다[14][15][16].
- **Trezor Suite 로 관리한 기기와 계정.** 기억한 기기라면 `devices` 에 기기 객체와 처음 연결한 시각·마지막 갱신 시각이, `accounts`·`txs` 에 계정과 거래가 있습니다[23][24][25].
- **다른 지갑과의 연동.** MetaMask 의 `keyring.type`, Electrum 의 `hw_type`·`soft_device_id` 로 하드웨어 지갑으로 서명하는 계정이 그 지갑에 등록됐다는 것을 확인합니다[44][45]. Electrum 의 Trezor 키스토어는 `soft_device_id` 로 장치 한 대까지 연결할 수 있습니다[47].
- **USB 연결.** VID·PID 로 Ledger 나 Trezor 장치가 이 PC 에 연결된 적이 있다는 것과 모델 계열을 확인합니다[17][28][38].

### 증명하지 못하는 것

- **개인 키가 이 PC 에 있었다는 것.** 키는 장치 안에 있습니다[52]. 이 PC 에서 개인 키가 나오지 않는 것도 정상이고, 하드웨어 지갑을 쓰지 않았다는 증거가 아닙니다.
- **특정 장치 한 대.** Ledger Live 는 모델만 저장하고 `knownDevices` 의 `id` 는 빈 문자열이라서, 같은 모델 여러 대를 구분할 수 없습니다[16]. 장치 일련번호 필드도 없습니다[15].
- **누가 장치를 조작해 서명했는지.** 서명은 장치 화면 확인과 장치에 따른 암호·PIN 입력으로 이뤄지므로[1], PC 의 기록만으로는 사람을 특정할 수 없습니다.
- **전체 거래 내역.** `app.json` 의 거래 목록은 500개·366일 규칙으로 잘려 있습니다[12].
- **송금 사실.** 연결 흔적과 앱 데이터만으로 송금을 단정하지 않습니다. 찾은 주소와 트랜잭션 해시를 [블록 탐색기 기록 읽기](../records/block-explorers.md)로 확인합니다.
- **잠긴 계정 목록.** 잠금이 걸린 `accounts` 는 풀지 않는 한 계정 목록을 보여 주지 않습니다[5][6].

보고서에는 "이 PC 의 Ledger Live 데이터(`app.json`)에 Nano X 모델이 연결된 기록과 계정 ID 에 든 xpub 이 있고, 이 xpub 에서 파생한 주소에서 이 시각에 이 금액을 보낸 트랜잭션이 블록체인에 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

| 값 | 기준과 형식 | 언제 바뀌나 |
|---|---|---|
| Ledger 거래 `date` | ISO 8601 UTC 문자열(`Z` 로 끝남)[13] | 거래의 시각. 블록 시각인지 앱이 받은 시각인지는 같은 거래의 `blockHeight`·`blockHash` 로 블록 시각과 비교해 확인합니다[8] |
| Ledger 계정 `creationDate` | ISO 8601 UTC 문자열[13] | 계정의 가장 오래된 거래 날짜이고, 빈 계정은 앱이 계정을 만든 시각입니다[8]. 값이 없는 옛 데이터를 읽으면 읽는 순간의 시각(`Date.now()`)으로 채웁니다[13] |
| Ledger 계정 `lastSyncDate` | 저장하지 않음. 옛 데이터를 읽을 때만 씁니다[8][13] | — |
| Ledger 내보낸 로그 `timestamp` | ISO 8601 문자열[19] | 로그 항목이 생길 때 |
| `app.json` 파일 수정 시각 | 파일 시스템 시각 | 설정·계정·시세가 바뀌어 파일을 다시 쓸 때(500ms 모아서)[5]. 장치 연결 시각이 아닙니다 |
| Trezor Suite `ts`, `firstConnectedTimestamp` | Unix epoch 밀리초, PC 시스템 시계 기준[25] | `ts` 는 연결할 때와 앱이 기기 시각을 갱신할 때마다, `firstConnectedTimestamp` 는 처음 한 번 |
| Trezor Suite 로그 파일 이름·줄 시각 | UTC ISO 8601[27] | 로그를 쓸 때 |
| Trezor Bridge 로그 | 로컬 시간대 `YYYY/MM/DD HH:MM:SS`, 시간대 표시 없음[31][37] | 로그를 쓸 때. PC 시간대 설정과 함께 해석합니다 |
| MetaMask `importTime`, `lastSelected` | Unix epoch 밀리초[44] | 계정을 추가할 때, 계정을 고를 때 |
| `SetupAPI.dev.log` 섹션 | 장치 설치 한 번이 한 섹션[39]. 섹션의 시각 읽는 법은 [USB 저장장치 흔적](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/external-devices/usb-storage-artifacts/) | 장치를 설치할 때 |

여러 시각을 한 줄로 합칠 때는 [암호화폐 타임라인](../../03-techniques/analysis/timeline.md)을, 블록 시각의 뜻은 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)을 봅니다.

## 함정과 한계

- **폴더 이름이 둘입니다.** 제품 이름은 Ledger Wallet 이지만 데이터 폴더는 조건에 따라 `Ledger Live` 로 남습니다[2][4]. 두 폴더와 `LEDGER_CONFIG_DIRECTORY` 를 모두 확인합니다.
- **잠금이 걸려도 장치 정보는 평문입니다.** 반대로 `accounts` 가 문자열이면 잠금 상태이고, 이때 계정 목록은 `starredAccountIds` 나 내보낸 로그에서만 일부 얻을 수 있습니다[5][14][20].
- **xpub 접두사를 그대로 믿지 않습니다.** Ledger 의 계정 ID 는 `native_segwit` 계정이어도 키를 `xpub` 접두사로 적습니다[10]. BIP-49 는 `ypub`, BIP-84 는 `zpub` 버전 바이트를 쓰는데[51], xpub 을 넣으면 레거시 주소만 만드는 조회 도구는 SegWit 거래를 놓칩니다[53]. Ledger Nano X 와 Ledger Live 로 만든 거래로 공개 조회 도구 7개를 시험한 연구에서 모든 거래를 찾은 도구는 xpub-scan 하나였고, 7개 중 6개는 xpub 에서 SegWit 주소를 자동으로 파생하지 않았습니다[53]. 계정 ID 의 파생 방식(`derivationMode`)을 보고 주소 형식을 맞춥니다.
- **주소 간격 한도.** BIP-44 는 주소 간격 한도(gap limit)를 20 으로 정합니다[50]. 사용자가 주소를 건너뛰어 만들었다면 한도를 20 으로 두는 도구는 뒤쪽 주소를 찾지 못합니다[53].
- **조회하면 주소가 밖으로 나갑니다.** xpub-scan 은 xpub 자체는 보내지 않고 파생한 주소만 외부 조회 서비스로 보낸다고 밝히지만[54], BlockQuery 연구는 사용자 지정 공급자를 써도 정보 노출을 막을 방법이 없다고 봤습니다[53]. 둘 다 조사 대상 주소가 외부 서비스에 드러난다는 점은 같습니다. Ledger Live 자체도 Ledger 의 탐색기 API 로 주소를 조회합니다[10].
- **Trezor Suite 는 기억하지 않은 기기의 데이터를 남기지 않습니다**[24][25]. IndexedDB 에 계정이 없다고 Trezor 를 쓰지 않았다고 보지 않습니다.
- **로그 파일은 기본으로 생기지 않습니다.** Trezor Suite 는 `--log-write`, Bridge 는 `-l` 이 있어야 파일을 만들고[27][31], Ledger Live 는 사용자가 내보낼 때만 파일이 생깁니다[20].
- **USB 저장 장치 기록에는 나오지 않습니다.** 하드웨어 지갑은 HID·WebUSB 장치로 잡힙니다[17][28][41]. Trezor 는 VID 가 `534C` 와 `1209` 두 가지이고 Trezor 코드는 VID·PID 쌍으로 장치를 판정하므로[28], `1209` 는 PID `53C0`·`53C1` 과 함께 찾습니다. 옛 Ledger 는 VID `2581` 입니다[18].
- **Bluetooth 연결.** Nano X, Stax, Flex, Nano Gen5 는 Bluetooth 도 지원합니다[17]. Bluetooth 로만 연결했다면 PC 의 USB 기록이 없을 수 있습니다.
- **메모리 흔적은 오래가지 않습니다.** Ledger Live 1.18.2 시험에서 앱을 잠그고 6분 뒤 메모리에는 확장 공개 키 14개와 명령 이벤트 1개만 남았고(최대일 때 각각 1,700개 넘게, 40개), 프로세스를 끝낸 뒤 6분 안에 나머지도 모두 덮어써졌습니다[52].
- **연구 결과를 현재 앱에 그대로 옮기지 않습니다.** 메모리 연구의 Trezor Wallet 은 옛 웹 앱이고 Ledger Live 도 1.18.2 입니다[52]. 현재 Trezor Suite 와 Ledger Live 에서는 결과가 다를 수 있으므로 버전을 함께 적습니다.
- **증거 사본에서 앱을 켜지 않습니다.** Ledger Live 는 시작할 때 `app.json.` 으로 시작하는 임시 파일을 지우고[7], 켜는 순간 `app.json` 을 다시 쓸 수 있습니다[5].

## 직접 분석해 보기

### 헥스로 한 번

`app.json` 사본을 헥스 편집기로 열면 첫 바이트부터 `7B 22 64 61 74 61 22 3A 7B`(`{"data":{`)로 시작하는 JSON 텍스트입니다[5]. `"accounts":` 뒤가 `[` 이면 잠금이 없는 상태, `"` 이면 잠금 상태입니다[5]. 잠금 상태의 base64 문자열을 풀면 아래처럼 17번째 바이트(오프셋 0x10)가 `3A` 입니다[6].

```text
00000000  8c 1f 4e a2 07 d9 33 b5  61 0e f4 29 9a c7 52 18   ..N...3.a..)..R.   IV 16바이트
00000010  3a 5d e0 71 b4 2c 96 0f  ...                       :].q.,..           ':' 뒤부터 암호문
```

위 바이트는 Ledger 의 저장 코드로 만든 예시입니다. 아래 파이썬 코드는 `app.json` 을 읽기만 하고, 잠금 여부와 평문 장치 정보, 계정 ID 의 구성 요소를 출력합니다.

```python
import base64, json, sys

d = json.load(open(sys.argv[1], encoding="utf-8"))["data"]
for k in ("accounts", "trustchain", "wallet"):
    v = d.get(k)
    if isinstance(v, str):
        raw = base64.b64decode(v)
        print(k, "잠금", len(raw), "바이트, 17번째 바이트 ':' =", raw[16:17] == b":")
    else:
        print(k, "평문" if v is not None else "없음")
s = d.get("settings", {})
last = s.get("lastSeenDevice") or {}
print("lastSeenDevice", last.get("modelId"), (last.get("deviceInfo") or {}).get("version"),
      [a.get("name") for a in last.get("apps", [])])
print("devicesModelList", s.get("devicesModelList"))
print("knownDevices", (d.get("knownDevices") or {}).get("knownDevices"))
for acc_id in s.get("starredAccountIds", []):
    base = acc_id.split("+")[0]           # 토큰 계정이면 부모 계정 ID
    t, ver, cur, key, mode, *rest = base.split(":")
    print(cur, mode or "(기본)", key.replace("~!colons!~", "::"))
```

Windows 이미지에서는 `SetupAPI.dev.log` 와 SYSTEM 하이브에서 VID 문자열을 찾습니다. 로그 사본에서는 PowerShell 로 아래처럼 찾을 수 있습니다.

```powershell
Select-String -Path .\setupapi.dev.log -Pattern 'VID_2C97','VID_2581','VID_534C','VID_1209&PID_53C[01]'
```

찾은 줄이 속한 섹션이 그 장치를 설치한 기록이고[39], 같은 장치 ID 를 SYSTEM 하이브의 `Enum\USB` 아래에서 찾아 비교합니다. `Enum` 트리는 운영체제용이라 구조가 바뀔 수 있으므로[40], 해석은 [USB 저장장치 흔적](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/external-devices/usb-storage-artifacts/)의 방법을 따릅니다.

### 공개 도구로 한 번

Ledger·Trezor 관리 앱 전용 분석기는 ALEAPP·iLEAPP·KAPE 에 없어서, `app.json` 은 `jq` 같은 JSON 도구로, Trezor Suite 의 IndexedDB 는 크롬 계열 IndexedDB 를 읽는 도구로 직접 읽습니다. 예를 들어 `jq '.data.settings | {lastSeenDevice, devicesModelList, starredAccountIds}' app.json` 으로 장치 정보를 뽑습니다. xpub 으로 거래를 조회할 때는 Legacy·Nested SegWit·Native SegWit 주소를 모두 파생하고 인덱스 범위를 바꿀 수 있는 xpub-scan 을 쓸 수 있습니다[53][54]. 시작 인덱스를 정해 검사할 때 xpub-scan 은 기본값으로 계정마다 주소 2,000개를 미리 파생합니다[54]. 이때 파생한 주소가 외부 조회 서비스로 나간다는 점을 보고서에 적습니다. 메모리에서는 Volatility 와 YARA 규칙으로 xpub·JSON 구조를 찾는 방식을 씁니다[52]. 문자열 검색으로 주소와 xpub 을 찾는 방법은 [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md)에서 다룹니다.

## 교차 검증

- **블록체인.** 계정 ID 의 xpub·주소와 거래 해시를 블록 탐색기나 자체 노드로 조회해 거래가 실제로 있었는지, `date` 가 블록 시각과 맞는지 확인합니다([블록 탐색기 기록 읽기](../records/block-explorers.md), [비트코인 거래 따라가기](../../03-techniques/analysis/bitcoin-tracing.md), [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md)).
- **주소 형식과 파생 경로.** `derivationMode` 와 xpub 접두사를 [주소 형식](../../01-foundations/wallets/address-formats.md), [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)와 맞춰 봅니다.
- **OS 의 USB 기록.** `lastSeenDevice` 의 모델과 USB PID 의 모델 바이트가 같은지, 첫 연결 시각이 앱 설치 시각 뒤인지 비교합니다.
- **다른 지갑.** 같은 PC 의 [MetaMask](../browser/metamask/index.md) 에 `Ledger Hardware`·`Trezor Hardware` 계정이 있는지, [Electrum](../desktop/electrum.md) 지갑에 하드웨어 키스토어가 있는지 봅니다. Electrum 의 `xpub` 이 Ledger Live·Trezor Suite 계정의 xpub 과 같으면 같은 장치·복구 문구의 계정일 가능성이 큽니다.
- **메모리.** 실행 중인 시스템이면 메모리의 xpub 과 디스크의 계정 ID 를 비교합니다([메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/)).
- **거래소 기록.** 하드웨어 지갑 주소로 입출금한 거래소 기록이 있으면 [거래소가 제공하는 자료](../records/exchange-records.md)로 사람과 연결합니다.

조사 순서 전체는 [이 기기로 지갑을 썼나](../../04-scenarios/device-use/wallet-use.md)와 [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md)를 봅니다.

## 실습

하드웨어 지갑 장치가 없어도 풀 수 있는 질문과, 장치가 있을 때 풀 질문으로 나눴습니다. 실제 자산은 넣지 않습니다.

1. 위 "만든 예시" 계정 ID 두 줄을 파이썬 코드로 나눠 통화·키·파생 방식을 뽑아 봅니다. 첫 줄의 xpub 을 `native_segwit` 으로 읽을 때와 레거시로 읽을 때 만들어지는 첫 주소는 어떻게 다른가?
2. 가상 머신에 Ledger Live 를 설치하고 장치 없이 실행한 뒤 데이터 폴더 이름이 `Ledger Live` 인지 `Ledger Wallet` 인지, `app.json` 에 어떤 최상위 키가 생기는지 확인합니다.
3. Electrum 을 테스트넷 모드로 실행해 하드웨어 지갑 키스토어로 지갑을 만들면(장치가 있을 때), 지갑 파일에 `hw_type`·`soft_device_id`·`root_fingerprint` 가 어떤 값으로 들어가는가?
4. MetaMask 의 Trezor 연동에서 테스트넷 경로 `m/44'/1'/0'/0` 을 고를 수 있는지 확인하고[43], 연동 뒤 `internalAccounts` 의 `keyring.type` 과 `importTime` 을 읽어 봅니다.
5. 장치를 꽂기 전과 뒤에 `SetupAPI.dev.log` 와 `Enum\USB` 를 비교해, 새로 생긴 VID·PID 와 인터페이스(`MI_xx`) 항목이 무엇인지 적습니다. PID 의 모델 바이트는 앱 `settings` 의 `lastSeenDevice.modelId` 와 맞는가?
6. Ledger Live 에 암호 잠금을 켠 뒤 `app.json` 에서 어떤 키가 문자열로 바뀌고 어떤 키가 평문으로 남는가?

## 참고 문헌

1. Bitcoin Developer Documentation, Wallets — Hardware Wallets. https://developer.bitcoin.org/devguide/wallets.html
2. LedgerHQ, ledger-live `apps/ledger-live-desktop/src/main/index.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/main/index.ts
3. Electron 문서, app (`app.getPath`, `app.getName`). https://github.com/electron/electron/blob/main/docs/api/app.md
4. LedgerHQ, ledger-live `apps/ledger-live-desktop/package.json`, `README.md`. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/package.json , https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/README.md
5. LedgerHQ, ledger-live `apps/ledger-live-desktop/src/main/db/index.ts`, `index.test.ts`, `fsHelper.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/main/db/index.ts
6. LedgerHQ, ledger-live `apps/ledger-live-desktop/src/main/db/crypto.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/main/db/crypto.ts
7. LedgerHQ, ledger-live `apps/ledger-live-desktop/src/main/cleanupUserData.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/main/cleanupUserData.ts
8. LedgerHQ, ledger-live `libs/types-live/src/account.ts`, `operation.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/libs/types-live/src/account.ts
9. LedgerHQ, ledger-live `libs/ledger-wallet-framework/src/account/accountId.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/libs/ledger-wallet-framework/src/account/accountId.ts
10. LedgerHQ, ledger-live `libs/ledger-live-common/src/families/bitcoin/docs/Troubleshooting.md`. https://github.com/LedgerHQ/ledger-live/blob/develop/libs/ledger-live-common/src/families/bitcoin/docs/Troubleshooting.md
11. LedgerHQ, ledger-live `libs/ledger-wallet-framework/src/derivation.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/libs/ledger-wallet-framework/src/derivation.ts
12. LedgerHQ, ledger-live `apps/ledger-live-desktop/src/helpers/accountModel.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/helpers/accountModel.ts
13. LedgerHQ, ledger-live `libs/ledger-wallet-framework/src/serialization/operation.ts`, `account.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/libs/ledger-wallet-framework/src/serialization/operation.ts
14. LedgerHQ, ledger-live `apps/ledger-live-desktop/src/renderer/reducers/settings.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/renderer/reducers/settings.ts
15. LedgerHQ, ledger-live `libs/types-live/src/manager.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/libs/types-live/src/manager.ts
16. LedgerHQ, ledger-live `apps/ledger-live-desktop/src/renderer/reducers/knownDevices.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/renderer/reducers/knownDevices.ts
17. LedgerHQ, ts-libs `libs/devices/src/index.ts`. https://github.com/LedgerHQ/ts-libs/blob/develop/libs/devices/src/index.ts
18. LedgerHQ, udev-rules `20-hw1.rules`. https://github.com/LedgerHQ/udev-rules/blob/master/20-hw1.rules
19. LedgerHQ, ledger-live `apps/ledger-live-desktop/src/main/logger.ts`, `mergeAllLogs.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/main/mergeAllLogs.ts
20. LedgerHQ, ledger-live `apps/ledger-live-desktop/src/mvvm/hooks/useExportLogs.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/mvvm/hooks/useExportLogs.ts
21. LedgerHQ, ledger-live `libs/ledger-key-ring-protocol/src/store.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/libs/ledger-key-ring-protocol/src/store.ts
22. LedgerHQ, ledger-live `domain/entity/account/README.md`. https://github.com/LedgerHQ/ledger-live/blob/develop/domain/entity/account/README.md
23. Trezor, trezor-suite `packages/suite/src/storage/definitions.ts`, `createDb.ts`. https://github.com/trezor/trezor-suite/blob/develop/packages/suite/src/storage/definitions.ts
24. Trezor, trezor-suite `packages/suite/src/middlewares/wallet/storageMiddleware.ts`. https://github.com/trezor/trezor-suite/blob/develop/packages/suite/src/middlewares/wallet/storageMiddleware.ts
25. Trezor, trezor-suite `suite-common/suite-types/src/device.ts`, `suite-common/device/src/deviceReducer.ts`. https://github.com/trezor/trezor-suite/blob/develop/suite-common/suite-types/src/device.ts
26. Trezor, trezor-suite `suite/desktop-app-main/src/libs/user-data.ts`. https://github.com/trezor/trezor-suite/blob/develop/suite/desktop-app-main/src/libs/user-data.ts
27. Trezor, trezor-suite `suite/desktop-app-main/src/libs/logger.ts`. https://github.com/trezor/trezor-suite/blob/develop/suite/desktop-app-main/src/libs/logger.ts
28. Trezor, trezor-suite `packages/transport-common/src/constants.ts`. https://github.com/trezor/trezor-suite/blob/develop/packages/transport-common/src/constants.ts
29. Trezor, trezor-firmware `common/protob/messages-management.proto` (Features 메시지). https://github.com/trezor/trezor-firmware/blob/main/common/protob/messages-management.proto
30. Trezor, trezord-go `README.md`. https://github.com/trezor/trezord-go/blob/master/README.md
31. Trezor, trezord-go `trezord.go`. https://github.com/trezor/trezord-go/blob/master/trezord.go
32. Trezor, trezord-go `server/status/windows.go`. https://github.com/trezor/trezord-go/blob/master/server/status/windows.go
33. Trezor, trezord-go `release/windows/trezord.nsis`. https://github.com/trezor/trezord-go/blob/master/release/windows/trezord.nsis
34. Trezor, trezord-go `release/macos/.../com.bitcointrezor.trezorBridge.trezord.plist`. https://github.com/trezor/trezord-go/blob/master/release/macos/flat-install/install.pkg/payload/Library/LaunchAgents/com.bitcointrezor.trezorBridge.trezord.plist
35. Trezor, trezord-go `release/linux/trezord.service`, `trezor.rules`. https://github.com/trezor/trezord-go/blob/master/release/linux/trezor.rules
36. Trezor, trezord-go `CHANGELOG.md`. https://github.com/trezor/trezord-go/blob/master/CHANGELOG.md
37. Go 문서, package log (`LstdFlags`). https://pkg.go.dev/log
38. Microsoft Learn, Standard USB Identifiers. https://learn.microsoft.com/en-us/windows-hardware/drivers/install/standard-usb-identifiers
39. Microsoft Learn, SetupAPI Text Logs. https://learn.microsoft.com/en-us/windows-hardware/drivers/install/setupapi-text-logs
40. Microsoft Learn, HKLM\SYSTEM\CurrentControlSet\Enum Registry Tree. https://learn.microsoft.com/en-us/windows-hardware/drivers/install/hklm-system-currentcontrolset-enum-registry-tree
41. Microsoft Learn, HID Architecture. https://learn.microsoft.com/en-us/windows-hardware/drivers/hid/hid-architecture
42. MetaMask, accounts `packages/keyring-eth-ledger-bridge/src/ledger-keyring.ts`. https://github.com/MetaMask/accounts/blob/main/packages/keyring-eth-ledger-bridge/src/ledger-keyring.ts
43. MetaMask, accounts `packages/keyring-eth-trezor/src/trezor-keyring.ts`. https://github.com/MetaMask/accounts/blob/main/packages/keyring-eth-trezor/src/trezor-keyring.ts
44. MetaMask, core `packages/accounts-controller/src/AccountsController.ts`. https://github.com/MetaMask/core/blob/main/packages/accounts-controller/src/AccountsController.ts
45. Electrum, `electrum/keystore.py` (Hardware_KeyStore). https://github.com/spesmilo/electrum/blob/master/electrum/keystore.py
46. Electrum, `electrum/plugin.py` (DeviceInfo, select_device). https://github.com/spesmilo/electrum/blob/master/electrum/plugin.py
47. Electrum, `electrum/plugins/trezor/clientbase.py`. https://github.com/spesmilo/electrum/blob/master/electrum/plugins/trezor/clientbase.py
48. Electrum, `electrum/plugins/ledger/ledger.py`. https://github.com/spesmilo/electrum/blob/master/electrum/plugins/ledger/ledger.py
49. BIP-32, Hierarchical Deterministic Wallets (Key identifiers). https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
50. BIP-44, Multi-Account Hierarchy for Deterministic Wallets. https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
51. BIP-49, BIP-84 (확장 키 버전 바이트). https://github.com/bitcoin/bips/blob/master/bip-0049.mediawiki , https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki
52. Tyler Thomas, Mathew Piscitelli, Ilya Shavrov, Ibrahim Baggili, "Memory FORESHADOW: Memory FOREnSics of HArDware CryptOcurrency wallets – A Tool and Visualization Framework", Forensic Science International: Digital Investigation 33, 2020. doi:10.1016/j.fsidi.2020.301002
53. Tyler Thomas, Tiffanie Edwards, Ibrahim Baggili, "BlockQuery: Toward forensically sound cryptocurrency investigation", Forensic Science International: Digital Investigation 40, 2022. doi:10.1016/j.fsidi.2022.301340
54. LedgerHQ, xpub-scan `README.md`. https://github.com/LedgerHQ/xpub-scan/blob/main/README.md
55. BiTLab-BaggiliTruthLab, FORESHADOW 저장소(옛 주소 UNHcFREG/FORESHADOW). https://github.com/BiTLab-BaggiliTruthLab/FORESHADOW
