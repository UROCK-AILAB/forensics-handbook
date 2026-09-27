---
title: "이 기기로 지갑을 썼나"
parent: "시나리오 · 기기 사용"
nav_order: 370
---

# 이 기기로 지갑을 썼나 (Wallet Use)

압수한 컴퓨터나 휴대폰에서 암호화폐 지갑을 설치하고 썼는지, 그 지갑이 어떤 주소를 관리했는지, 언제부터 언제까지 썼는지를 확인하는 순서를 다룹니다. 기기에서 찾은 지갑 데이터는 "이 계정에 이 지갑이 있었고 이 주소를 관리했다" 까지만 알려 주므로, 실제 거래는 블록체인과 거래소 기록으로 따로 확인해서 합칩니다. 파일 하나하나의 구조는 아티팩트 페이지로 링크하고, 여기서는 무엇을 어떤 순서로 보고 어떻게 해석하는지를 씁니다.

## 조사 질문

- 이 기기의 어느 사용자 계정·브라우저 프로필에 어떤 지갑 소프트웨어가 설치되거나 실행된 흔적이 있는가.
- 그 지갑이 관리한 주소, 확장 공개 키 (xpub), 트랜잭션은 무엇인가.
- 언제 설치했고 마지막으로 언제 썼으며, 거래는 언제 있었는가.
- 기기에서 찾은 주소·시각이 블록체인과 거래소 기록과 맞는가.

## 먼저 확인할 것

**OS 와 사용자 계정, 브라우저 프로필.** 지갑 데이터는 사용자 폴더마다, 브라우저 프로필마다 따로 생깁니다. Chrome 기본 프로필의 MetaMask 저장소는 `%localappdata%\Google\Chrome\User Data\Default\Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn\` 이고, Brave 같은 다른 Chromium 계열 브라우저는 앞부분 경로만 다르고 마지막 폴더 이름(확장 ID)은 같습니다[15]. 그래서 `Default` 뿐 아니라 `Profile 1` 같은 다른 프로필과 설치된 브라우저를 모두 봅니다. 브라우저 프로필 구조는 [Windows 핸드북의 크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) 페이지에 있습니다.

**앱 버전에 따라 바뀐 기본 경로.** Bitcoin Core 28.0 부터 Windows 의 기본 데이터 폴더가 `AppData\Roaming\Bitcoin` 에서 `AppData\Local\Bitcoin` 으로 바뀌었습니다. 다만 옛 폴더가 있으면 그 폴더를 계속 씁니다[3]. 따라서 두 위치를 모두 확인합니다.

**시간대.** 앱마다 시각을 UTC 로 저장하는지, 기기 시계 값을 그대로 쓰는지가 다릅니다(아래 "시각을 읽을 때" 참고). 기기의 시간대 설정을 먼저 기록해 둡니다.

**수집 범위.** Windows 는 사용자 폴더의 `AppData\Roaming`·`AppData\Local` 과 브라우저 프로필 전체를 수집합니다. Android 는 루팅한 기기에서만 물리 추출을 할 수 있었고, 루팅하지 않은 기기는 물리 추출에 실패해 일부 흔적을 얻지 못한 시험 결과가 있습니다[24]. Android 앱 데이터 폴더 구조는 [Android 핸드북의 앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/app-data-layout.html)에 있습니다. 하드웨어 지갑 앱을 쓰는 중이었다면 메모리도 수집합니다. Ledger Live 는 앱을 잠그면 메모리 흔적 대부분이 곧바로 덮어써지고, 프로세스를 끝내면 6분 안에 남은 흔적도 모두 덮어써집니다[23].

**SQLite 보조 파일.** 데이터베이스 파일과 함께 `-wal`·`-journal` 파일을 같이 수집합니다. Android BRD 지갑의 `platform.db` 는 데이터가 모두 WAL 파일에만 있을 수 있고, 그러면 WAL 없이 읽을 때 표에 행이 하나도 나오지 않습니다[20]. Bitcoin Core 의 SQLite 지갑 옆에 생기는 `wallet.dat-journal` 도 `wallet.dat` 와 똑같이 안전하게 보관해야 하는 파일입니다[2]. SQLite 의 WAL 과 저널은 [Windows 핸드북의 SQLite](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/) 페이지에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 설치된 앱·브라우저 확장 목록 | 어느 지갑이 있었는지, 확장을 처음 설치한 시각과 마지막으로 설치·업데이트한 시각 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/), [iOS 설치된 앱](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/app-usage/installed-apps.html) |
| 2 | 데스크톱 지갑 폴더 | 지갑 파일 이름, 시작할 때 불러오는 지갑, 최근 연 지갑 | [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md), [Electrum](../../02-artifacts/desktop/electrum.md), [Exodus](../../02-artifacts/desktop/exodus.md) |
| 3 | 브라우저 확장 지갑 저장소 | 볼트가 있는지, 처음 설치한 버전과 시각, 볼트를 다시 만든 흔적 | [MetaMask](../../02-artifacts/browser/metamask/index.md), [다른 확장 지갑](../../02-artifacts/browser/other-extensions.md) |
| 4 | 모바일 지갑·거래소 앱 데이터 | 계정·주소·파생 경로·트랜잭션·앱 안 브라우저 방문 기록 | [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md), [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md), [거래소 앱](../../02-artifacts/mobile/exchange-apps.md) |
| 5 | 하드웨어 지갑 연결 흔적 | 하드웨어 지갑 앱 데이터, USB 연결 시각, 메모리의 xpub | [하드웨어 지갑과 연결 흔적](../../02-artifacts/hardware/hardware-wallets.md), [USB 저장장치 흔적](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/external-devices/usb-storage-artifacts/) |
| 6 | 메일·알림 | 거래소 알림 메일 제목에 적힌 금액과 주소 | [거래소 앱](../../02-artifacts/mobile/exchange-apps.md) |
| 7 | 주소·TXID 문자열 검색 | 지갑 앱 밖(문서·메모·메모리 잔재)에 남은 주소 | [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md), [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md) |
| 8 | 블록체인·거래소 기록 | 찾은 주소와 xpub 로 실제 거래가 있었는지 | [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md), [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md) |

## 분석 흐름

1. **어느 지갑이 있었는지 목록을 만듭니다.** Chromium 계열 브라우저는 확장마다 설정 항목에 `first_install_time` 과 `last_update_time` 을 기록합니다[1]. `first_install_time` 은 확장을 설치할 때 만들어지고 업데이트해도 바뀌지 않으며, 확장을 지우면 그 확장의 설정 항목과 함께 삭제됩니다[1]. 두 값은 1601-01-01 UTC 부터 흐른 마이크로초를 숫자 문자열로 저장합니다[1]. 확장 ID 로 지갑을 구분하는데, Chrome 에 설치한 MetaMask 는 `nkbihfbeogaeaoehlefnkodbefgpgknn`, Binance Wallet 은 `fhbohimaelbohpjbbldcngcnapndodjp`, Ronin Wallet 은 `fnjhmkhhmkbjkkabndcnnogagogbneec` 입니다[15]. 데스크톱 지갑은 아래 2단계의 폴더가 있는지로 목록에 넣습니다. 목록을 빠짐없이 만드는 방법은 [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md)에 있습니다.

2. **데스크톱 지갑에서 어느 지갑 파일을 썼는지 확인합니다.**
   - Bitcoin Core 의 데이터 폴더는 Linux `$HOME/.bitcoin/`, macOS `$HOME/Library/Application Support/Bitcoin/`, Windows `%LOCALAPPDATA%\Bitcoin\` 이고, 테스트넷 등 다른 체인은 `testnet3/`·`testnet4/`·`signet/`·`regtest/` 하위 폴더를 씁니다[2]. 이름을 붙인 지갑은 `wallets/` 아래 지갑 이름 폴더에, 이름 없는 기본 지갑은 `wallets/` 에 있고, `wallets/` 가 없으면 데이터 폴더에 있습니다[2]. `-walletdir` 옵션으로 다른 곳을 지정할 수도 있습니다[2]. `settings.json` 은 GUI 나 RPC 로 바꾼 설정을 저장하는 파일이고[2], 지갑을 "시작할 때 불러오기" 로 지정하면 `wallet` 설정 배열에 지갑 이름을 넣고 해제하면 뺍니다[4]. 그래서 이 배열에 있는 이름은 시작할 때 불러오도록 지정된 지갑입니다. `bitcoind.pid` 와 `.cookie` 는 실행할 때 만들어지고 종료할 때 지워지므로[2], 디스크 이미지에 남아 있으면 비정상 종료했거나 실행 중에 수집했을 가능성이 있습니다.
   - Electrum 의 사용자 폴더는 `ELECTRUMDIR` 환경 변수가 있으면 그 경로이고, 없으면 Linux·macOS 는 `~/.electrum`, Windows 는 `%APPDATA%\Electrum` 입니다[5]. 기본 지갑은 사용자 폴더의 `wallets/default_wallet` 이고[6], 설정은 사용자 폴더 바로 아래 `config` 라는 JSON 파일에 저장됩니다[6]. 이 파일의 `current_wallet` 은 지금 쓰는 지갑 경로이고, `recently_open` 은 최근 연 지갑 경로 목록입니다[6]. `recently_open` 은 지갑을 열 때마다 그 경로를 맨 앞에 넣고, 그 시점에 존재하는 경로만 남기고, 5개까지만 둡니다[7]. 파일 이름이 `.` 으로 시작하는 지갑은 두 필드 모두에 저장하지 않습니다[6][7].
   - Exodus 의 암호화 컨테이너 파일은 `SECO` 로 시작하고 헤더에 파일을 만든 앱 이름(`appName`)과 앱 버전(`appVersion`)이 평문으로 들어 있습니다[17].
   - Ledger Live 데스크톱은 데이터 폴더의 `app.json` 에 `accounts`·`settings`·`knownDevices`·`wallet`·`trustchain` 같은 최상위 키를 둡니다[16]. 암호 잠금을 켜면 `accounts`·`trustchain`·`wallet` 만 암호화하므로[16] `settings` 와 `knownDevices` 는 잠금과 상관없이 평문입니다. `knownDevices` 안의 필드는 실제 파일을 열어 확인합니다.

   지갑 파일에서 무엇이 평문으로 보이는지는 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md)에 있습니다.

3. **브라우저 확장 지갑의 저장소를 봅니다.** MetaMask 볼트는 `data`·`iv`·`salt` 필드를 가진 JSON 이고, 새 형식은 키 파생 설정을 담은 `keyMetadata` 가 더 있습니다[12]. 볼트가 있으면 이 프로필에서 MetaMask 지갑을 만들었거나 복원했다는 뜻입니다. 같은 LevelDB 에서 지금 볼트와 덮어쓰기 전 옛 볼트가 함께 나오는 경우가 있어서[15], 두 개가 나오면 지갑을 다시 만들었거나 복원했을 가능성을 봅니다. `AppMetadataController` 의 `firstTimeInfo` 는 처음 설치할 때의 MetaMask 버전(`version`)과 시각(`date`, 밀리초 UNIX 시각)이고, 한 번 정하면 바뀌지 않습니다[9]. 같은 곳의 `currentAppVersion` 과 `previousAppVersion` 으로 업데이트 전후 버전을 알 수 있습니다[9]. 마이그레이션 190 이전 상태는 `firstTimeInfo` 가 상태 최상위에 있습니다[11]. 새 저장 방식은 IndexedDB 데이터베이스 `metamask-storage-service` 를 쓰고, Firefox 사생활 보호 창처럼 IndexedDB 를 쓸 수 없으면 `browser.storage.local` 을 씁니다[13]. 그래서 LevelDB 와 IndexedDB 를 모두 봅니다. 사용자는 설정 → Privacy → Download state logs 로 상태 JSON 을 내려받을 수 있고[14] `firstTimeInfo` 도 여기에 들어가므로[9], 다운로드 폴더의 JSON 파일도 확인합니다. 저장소를 읽는 법은 [MetaMask](../../02-artifacts/browser/metamask/index.md) 페이지와 [Windows 핸드북의 LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html) 페이지에 있습니다.

4. **모바일 지갑과 거래소 앱을 봅니다.** iOS MetaMask 는 `Documents/persistStore/persist-root` 의 `engine` → `backgroundState` 에 계정 이름과 `importTime`, 잔액, 주소록, 트랜잭션(`time`, 보낸 주소·받은 주소·금액, `transactionHash`)을 두고, `browser` 에 앱 안 브라우저 방문 기록을 둡니다[18]. iOS Coinbase Wallet(번들 ID `org.toshi.distribution`)은 `Documents/default/wallet-rn-v2.sqlite` 와 `Documents/mmkv/CBStore.plaintext` 에 계정과 주소를 저장하고, 거래소 앱인 Coinbase 와는 저장소가 따로입니다[19]. Android 의 Coinomi 9.26.3 은 받은 트랜잭션의 해시를 `cache` 아래 16자리 헥스 이름 폴더의 `bitcoin.main/`·`dogecoin.main/` 아래에 이름으로 남겼습니다[24]. 거래소 Coinbase 는 계정 메일로 거래 알림을 보내는데, 받은 알림 제목("You just received … BTC")에는 금액이, 보낸 알림 제목("You just sent … BTC to" 뒤에 주소)에는 금액과 받는 주소가 들어 있습니다[24]. 앱별 경로와 표는 [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md), [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md), [거래소 앱](../../02-artifacts/mobile/exchange-apps.md)에 있습니다.

5. **하드웨어 지갑을 연결한 흔적을 봅니다.** Trezor Wallet 이 실행 중일 때 Trezor Bridge 는 연결된 USB 장치 목록을 계속 확인하고, 사용자의 Application Data 폴더에 USB 장치 연결 시각을 로그로 남깁니다[23]. Trezor 가 아닌 장치의 연결도 기록합니다[23]. Ledger Live 가 실행 중일 때 메모리에서는 xpub, 거래 내역, 장치 정보가 나오고, 이것으로 하드웨어 지갑을 썼는지, 어떤 거래가 있었는지, 어느 장치를 이 컴퓨터에 연결했는지 확인할 수 있습니다[23]. 디스크의 흔적과 OS 의 USB 기록은 [하드웨어 지갑과 연결 흔적](../../02-artifacts/hardware/hardware-wallets.md)에 있습니다.

6. **지갑 앱 밖에 남은 주소를 찾습니다.** 문서·메모·메모리 잔재에서 주소 문자열을 검색합니다. bstrings 의 `bitcoin` 정규식은 `\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b` 이고[21], KAPE 의 `bstrings_CryptoWallets` 모듈은 이런 bstrings 정규식 검색을 묶은 것입니다[22]. 이 정규식은 1 이나 3 으로 시작하는 주소만 잡으므로 `bc1` 로 시작하는 주소와 이더리움 `0x` 주소는 따로 검색합니다. 주소 형식별 검색은 [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md), 주소 형식은 [주소 형식](../../01-foundations/wallets/address-formats.md)에 있습니다.

7. **찾은 주소와 xpub 를 블록체인에서 확인합니다.** xpub 를 조회할 때는 주소 형식(Legacy·Nested SegWit·Native SegWit)과 받는 주소·잔돈 주소 체인을 모두 파생합니다. 공개 xpub 조회 도구 7개를 Ledger Nano X 와 Ledger Live 로 만든 거래로 시험했을 때 모든 거래를 찾은 도구는 LedgerHQ/xpub-scan 하나였고, 7개 중 6개는 xpub 에서 SegWit 주소를 자동으로 파생하지 않았습니다[26]. BIP44 의 주소 간격 한도(gap limit) 20 을 가정하는 도구는 간격을 크게 벌려 만든 주소를 찾지 못합니다[26]. 제3자 블록 탐색기에 조회하면 조사 대상 주소가 운영자에게 드러나므로 자체 노드로 조회하는 편이 낫습니다[26]. 조회 방법은 [비트코인 거래 따라가기](../../03-techniques/analysis/bitcoin-tracing.md)와 [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md), 파생 경로는 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)에 있습니다.

8. **시각을 한 타임라인으로 합칩니다.** 확장 설치 시각, 지갑 파일 시각, 앱 안 트랜잭션 시각, 블록 시각을 모두 UTC 로 바꿔 합칩니다. 합치는 방법은 [암호화폐 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

지갑 암호를 풀거나 복구 문구·개인 키를 꺼내는 일은 이 흐름에 넣지 않습니다. 볼트와 지갑 파일은 어디에 어떤 모양으로 있는지까지만 확인합니다.

## 시각을 읽을 때

| 값 | 기준 | 주의할 점 |
|---|---|---|
| Chromium 확장 `first_install_time`·`last_update_time` | 1601-01-01 UTC 부터 마이크로초, 숫자 문자열[1] | 처음 설치 시각은 업데이트해도 그대로이고, 확장을 지우면 값도 사라집니다[1] |
| MetaMask `firstTimeInfo.date` | `Date.now()` 밀리초 UNIX 시각[9] | 버전이 `3.12.0` 이면 설치 시각이 아닐 수 있습니다(아래 "흔한 오판") |
| Bitcoin Core 트랜잭션 수신 시각(`nTimeReceived`) | 지갑에 트랜잭션을 처음 넣을 때의 기기 시계, UNIX 초[4] | 기기 시계가 틀리면 같이 틀리므로 블록 시각과 따로 비교합니다 |
| Electrum 로그 파일 이름 | UTC, `YYYYMMDDTHHMMSSZ` 형식[8] | 로그 기록은 기본값이 꺼져 있어서 보통 파일이 없습니다[6][8] |
| iOS MetaMask `importTime`·`time` | UNIX 시각, iLEAPP 는 UTC 로 바꿔 표시합니다[18] | — |
| iOS Coinbase Wallet 계정 생성 시각 | 시간대 표시가 없습니다[19] | iLEAPP 는 옆 MMKV 저장소에 UTC(`Z`)로 적힌 시각과 11초·108초 차이였던 시험 이미지 두 개를 근거로 UTC 로 읽습니다[19] |
| 블록 시각 | 블록 헤더의 시각 | 기기 시각과 기준이 다릅니다. [블록 시각과 확정](../../01-foundations/blockchain/block-time.md) 참고 |

Electrum 에서 파일 로그(`log_to_file`)를 켜면 사용자 폴더의 `logs/` 에 `electrum_log_` 뒤에 UTC 시각과 프로세스 ID 가 붙은 이름으로 로그가 생기고, 기본 설정에서는 앱을 시작할 때 파일이 30개를 넘거나 전체 크기가 200,000,000바이트 이상이면 오래된 파일부터 지웁니다[6][8].

## 증명하는 것과 증명하지 못하는 것

**증명하는 것.** 지갑 앱이나 확장의 데이터가 있으면 그 계정·프로필에 지갑이 설치됐고 데이터를 만들었다는 뜻입니다. 볼트나 지갑 파일이 있으면 그 지갑을 만들었거나 복원했다는 뜻입니다. 앱 데이터 안의 주소와 xpub 는 그 지갑이 관리한 주소입니다. Electrum `recently_open` 에 있는 경로는 적어도 한 번 열었고 목록을 갱신할 때 존재했던 지갑이고[7], Bitcoin Core `settings.json` 의 `wallet` 배열에 있는 이름은 시작할 때 불러오도록 지정한 지갑입니다[4].

**증명하지 못하는 것.** 주소가 앱 데이터에 있다고 그 주소를 쓰거나 입금받았다는 뜻은 아닙니다. iOS Coinbase Wallet 의 주소 표에 행이 있다는 것만으로는 그 주소를 쓰거나 입금받았다고 볼 수 없고, iLEAPP 시험 이미지 두 개에서 이 표의 파생 인덱스는 0~19 였습니다[19]. 지갑 데이터만으로는 계정을 누가 썼는지 알 수 없고, 수탁형 거래소 앱은 기기에 키가 없어서 기기만으로 자산 통제를 판단할 수 없습니다. 지갑 앱이 없다는 것도 지갑을 쓰지 않았다는 뜻이 아닙니다. 다른 기기나 웹 지갑, 하드웨어 지갑을 썼거나 앱을 지웠을 수 있습니다.

## 흔한 오판

- **폴더가 없으니 쓰지 않았다.** 다른 브라우저 프로필, 다른 브라우저, Bitcoin Core 의 옛 경로(`AppData\Roaming\Bitcoin`), `-walletdir` 로 지정한 다른 폴더에 있을 수 있습니다[2][3][15]. 지운 확장은 브라우저 확장 목록에서도 사라집니다[1].
- **`firstTimeInfo.date` 는 설치 시각이다.** 마이그레이션 20 은 `firstTimeInfo` 가 없던 옛 설치본에 `version: '3.12.0'` 과 마이그레이션을 실행한 시각을 넣습니다[10]. 버전이 `3.12.0` 이면 `date` 는 그 버전으로 올라간 시각일 수 있습니다.
- **`recently_open` 에 없으니 연 적이 없다.** 이 목록은 5개까지만 두고, 갱신할 때 없어진 경로를 빼고, `.` 으로 시작하는 지갑은 넣지 않습니다[7].
- **`bitcoin` 정규식 검색 결과가 없으니 비트코인 주소가 없다.** `bc1` 주소는 이 정규식에 걸리지 않습니다[21]. KAPE 모듈 이름에 "Wallets" 가 들어 있어도 찾는 것은 지갑 파일이 아니라 주소 문자열입니다[21][22].
- **주소 목록은 사용한 주소다.** 주소 행이 있는 것과 그 주소를 쓴 것은 다릅니다[19]. 블록체인에서 거래를 확인한 주소만 사용한 주소로 씁니다.
- **xpub 조회 결과가 0건이니 거래가 없다.** 조회 도구가 주소 형식이나 간격 한도를 좁게 잡으면 거래를 놓칩니다[26].
- **DApp·거래소 사이트를 방문했으니 지갑을 연결했다.** 상위 10만 개 웹사이트 중 1,325개가 방문자에게 지갑이 설치됐는지 스크립트로 확인했습니다[25]. MetaMask 는 DApp 이 아닌 사이트에도 `window.ethereum` 객체를 넣고, `isMetaMask` 같은 값은 권한 없이 읽히지만 주소(`selectedAddress`)는 사용자가 허락해야 넘어갑니다[25]. 방문 기록만으로는 연결이나 서명을 증명할 수 없습니다. 서명 흔적은 [피싱 사이트에 서명했나](../fraud/wallet-drainer.md)에서 다룹니다.
- **메모리에 하드웨어 지갑 흔적이 없으니 쓰지 않았다.** Ledger Live 는 잠그거나 종료하면 몇 분 안에 흔적이 덮어써집니다[23].

## 보고서 문장 예

아래 주소·시각·금액은 모두 만든 예시입니다.

> 증거물 1(노트북) 사용자 계정 kim 의 Chrome `Profile 1` 확장 저장소에 MetaMask(확장 ID `nkbihfbeogaeaoehlefnkodbefgpgknn`) 볼트가 있고, 같은 프로필의 확장 설정에 이 확장의 `first_install_time` 이 2025-03-02 01:14:07 UTC 로 기록돼 있습니다. 같은 저장소에 이더리움 주소 `0x1111…1111`(만든 예시)이 계정으로 등록돼 있습니다. 이 주소에서 블록 시각 2025-03-05 10:22:31 UTC 에 0.5 ETH 를 보낸 트랜잭션이 이더리움 원장에 있으며, 원장은 자체 노드로 2025-06-01 UTC 에 블록 번호 22,000,000(만든 예시) 기준으로 조회했습니다.

"피의자가 MetaMask 로 0.5 ETH 를 보냈다" 처럼 사람과 행위를 단정하는 문장은 계정 사용자 확인, 서명 흔적처럼 다른 증거가 있을 때만 씁니다. 보고서 형식은 [암호화폐 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)에 있습니다.

## 함께 볼 페이지

- [악성 코드가 지갑을 노렸나](wallet-stealer.md) — 지갑이 있던 기기에서 탈취 악성 코드가 실행됐는지 확인합니다.
- [지갑의 종류](../../01-foundations/wallets/wallet-types.md) — 수탁형·비수탁형·하드웨어 지갑의 차이입니다.
- [조사 절차](../../03-techniques/acquisition/investigation-process.md) — 현장에서 무엇을 먼저 수집하는지 다룹니다.
- [거래소로 들어갔나](../asset-flow/exchange-deposit.md) — 찾은 주소의 자금이 거래소로 갔는지 확인합니다.
- [빼앗긴 자산은 어디로 갔나](../asset-flow/stolen-funds.md) — 자금 흐름을 따라갑니다.
- [Windows 핸드북의 메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/) — 지갑 앱이 실행 중일 때 메모리를 다룹니다.

## 참고 문헌

1. Chromium, `extensions/browser/extension_prefs.cc`, `extensions/browser/extension_pref_names.h`. https://github.com/chromium/chromium/blob/main/extensions/browser/extension_prefs.cc , https://github.com/chromium/chromium/blob/main/extensions/browser/extension_pref_names.h
2. Bitcoin Core, `doc/files.md`. https://github.com/bitcoin/bitcoin/blob/master/doc/files.md
3. Bitcoin Core, Release notes 28.0. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-28.0.md
4. Bitcoin Core, `src/wallet/wallet.cpp`. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/wallet.cpp
5. Electrum, `electrum/util.py`. https://github.com/spesmilo/electrum/blob/master/electrum/util.py
6. Electrum, `electrum/simple_config.py`. https://github.com/spesmilo/electrum/blob/master/electrum/simple_config.py
7. Electrum, `electrum/daemon.py`. https://github.com/spesmilo/electrum/blob/master/electrum/daemon.py
8. Electrum, `electrum/logging.py`. https://github.com/spesmilo/electrum/blob/master/electrum/logging.py
9. MetaMask, `app/scripts/controllers/app-metadata.ts`. https://github.com/MetaMask/metamask-extension/blob/main/app/scripts/controllers/app-metadata.ts
10. MetaMask, `app/scripts/migrations/020.ts`. https://github.com/MetaMask/metamask-extension/blob/main/app/scripts/migrations/020.ts
11. MetaMask, `app/scripts/lib/startup/load-state-from-persistence.ts`. https://github.com/MetaMask/metamask-extension/blob/main/app/scripts/lib/startup/load-state-from-persistence.ts
12. MetaMask, browser-passworder `src/index.ts`. https://github.com/MetaMask/browser-passworder/blob/main/src/index.ts
13. MetaMask, `shared/lib/stores/indexeddb-storage-adapter.ts`, `indexeddb-storage-constants.ts`. https://github.com/MetaMask/metamask-extension/blob/main/shared/lib/stores/indexeddb-storage-adapter.ts
14. MetaMask, `docs/state_dump.md`. https://github.com/MetaMask/metamask-extension/blob/main/docs/state_dump.md
15. btcrecover, `docs/Extract_Scripts.md`. https://github.com/3rdIteration/btcrecover/blob/master/docs/Extract_Scripts.md
16. Ledger Live, `apps/ledger-live-desktop/src/main/db/index.ts`. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/main/db/index.ts
17. Exodus, secure-container `src/header.js`. https://github.com/ExodusMovement/secure-container/blob/master/src/header.js
18. iLEAPP, `scripts/artifacts/metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
19. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
20. ALEAPP, `scripts/artifacts/breadWallet.py`. https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/breadWallet.py
21. Eric Zimmerman, bstrings `bstrings/Program.cs`. https://github.com/EricZimmerman/bstrings/blob/master/bstrings/Program.cs
22. Eric Zimmerman, KapeFiles `Modules/Compound/bstrings_CryptoWallets.mkape`. https://github.com/EricZimmerman/KapeFiles/blob/master/Modules/Compound/bstrings_CryptoWallets.mkape
23. Tyler Thomas, Mathew Piscitelli, Ilya Shavrov, Ibrahim Baggili, "Memory FORESHADOW: Memory FOREnSics of HArDware CryptOcurrency wallets – A Tool and Visualization Framework", Forensic Science International: Digital Investigation, 2020. doi:10.1016/j.fsidi.2020.301002
24. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, "Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications", arXiv, 2022. doi:10.48550/arXiv.2205.14611
25. Christof Ferreira Torres, Fiona Willi, Shweta Shinde, "Is Your Wallet Snitching On You? An Analysis on the Privacy Implications of Web3", arXiv, 2023. doi:10.48550/arXiv.2306.08170
26. Tyler Thomas, Tiffanie Edwards, Ibrahim Baggili, "BlockQuery: Toward forensically sound cryptocurrency investigation", Forensic Science International: Digital Investigation, 2022. doi:10.1016/j.fsidi.2022.301340
