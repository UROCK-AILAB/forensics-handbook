---
title: "지갑의 종류"
parent: "기반 · 지갑과 키"
nav_order: 50
---

# 지갑의 종류 (Custodial·Non-custodial·Hardware)

지갑은 개인 키를 누가 쥐는지, 서명을 어느 기기에서 하는지에 따라 종류가 나뉩니다. 거래소가 키를 관리하는 수탁형은 기록 대부분이 거래소에 있고, 사용자가 키를 쥐는 비수탁형은 주소·확장 공개 키·파생 경로가 기기에 남습니다. 하드웨어 지갑은 개인 키가 장치 밖으로 나오지 않아서, 연결한 PC·휴대폰에는 공개 키와 거래 내역만 남습니다.

## 이 구분을 쓰는 아티팩트

지갑 종류에 따라 기기에서 찾을 것과 기기 밖에 요청할 기록이 달라서, 지갑 흔적을 해석하기 전에 앱이 어느 종류인지부터 판단합니다. 아티팩트 사전의 앱 페이지는 모두 이 구분을 전제로 씁니다.

| 종류 | 앱의 예 | 자세히 다루는 페이지 |
|---|---|---|
| 거래소 앱 (수탁형) | Coinbase 앱, 국내 거래소 앱 | [거래소 앱](../../02-artifacts/mobile/exchange-apps.md), [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md) |
| 모바일 지갑 앱 (비수탁형) | Coinbase Wallet, MetaMask 모바일, BRD, Coinomi | [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md), [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md) |
| 브라우저 확장 지갑 (비수탁형) | MetaMask | [MetaMask](../../02-artifacts/browser/metamask/index.md), [다른 확장 지갑](../../02-artifacts/browser/other-extensions.md) |
| 데스크톱 지갑 (비수탁형) | Bitcoin Core, Electrum, Exodus | [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md), [Electrum](../../02-artifacts/desktop/electrum.md), [Exodus](../../02-artifacts/desktop/exodus.md) |
| 하드웨어 지갑과 연동 프로그램 | Ledger Live, Trezor Wallet·Trezor Bridge | [하드웨어 지갑과 연결 흔적](../../02-artifacts/hardware/hardware-wallets.md) |

## 구조

### 지갑 프로그램과 지갑 파일

"지갑" 이라는 말은 두 가지를 가리킵니다. 지갑 프로그램 (wallet program)은 공개 키를 만들어 돈을 받고, 그 공개 키에 맞는 개인 키로 서명해서 돈을 씁니다. 지갑 파일 (wallet file)은 개인 키를 저장하고, 필요하면 거래 관련 정보도 함께 저장합니다[1]. 지갑 파일의 형식과 암호화는 [지갑 파일과 암호화](wallet-files.md)에서 다룹니다.

이더리움에서는 계정과 지갑을 따로 봅니다. 계정은 개인 키로 통제하는 외부 소유 계정 (Externally Owned Account, EOA)과, 개인 키 없이 코드로 통제하는 컨트랙트 계정으로 나뉩니다. 지갑은 이 계정을 다루게 해 주는 화면이나 앱이고 계정 자체는 아닙니다[2]. 그래서 지갑 앱을 지운 기기에서도 계정 주소를 찾으면 그 계정의 거래를 체인에서 따로 조회할 수 있습니다. 계정 구조는 [이더리움의 계정과 로그](../blockchain/ethereum-accounts.md)에서 다룹니다.

### 누가 개인 키를 쥐나: 수탁형과 비수탁형

수탁형 (custodial) 서비스에서는 거래소가 키를 관리하고, 사용자는 거래소 계정에 로그인해 잔액과 거래를 봅니다. 기기에는 앱이 받아 둔 계정·잔액 캐시가 남고, 본인 확인 (Know Your Customer, KYC) 정보·입출금 내역·접속 IP 같은 기록은 거래소에 있습니다[10]. Coinbase iOS 앱은 `*/Documents/mmkv/CB_RRN_MMKV_STORAGE` 라는 MMKV 저장소에 상태를 두고, 그 안의 `@GraphqlOfflineCache.store` 값에 계정 레코드와 잔액 참조가 들어 있습니다[3]. Galaxy S9+(Android 8.0)에서 Coinbase 1.22.3·Coinomi 9.26.3·Atomic 0.75.1 을 비교한 시험에서는 이메일·전화번호를 요구한 앱이 거래소를 겸하는 Coinbase 뿐이었고, 파일 시스템에 거래 해시가 평문으로 남은 앱은 Coinomi 하나였습니다[15]. 수탁형 앱을 쓴 기기에서 거래 흔적이 적게 나오면, 그 거래 기록은 거래소에 요청해야 합니다.

비수탁형 (non-custodial) 지갑은 사용자 기기의 앱이 키를 만들고 보관합니다. 이런 앱의 저장소에는 앱이 만든 주소 목록, 파생 경로, 확장 공개 키 (extended public key, xpub), 거래 기록이 남습니다. 예를 들어 Coinbase Wallet iOS 앱(번들 ID `org.toshi.distribution`)은 `Documents/default/wallet-rn-v2.sqlite` 의 `account`·`address`·`wallet`·`tx_history_v2` 표에 계정·주소·자산별 잔액·거래를 저장하고, `Documents/mmkv/CBStore.plaintext` 의 `BIP44XpubKey` 항목에 확장 공개 키를 저장합니다[4]. 확장 공개 키 하나로 그 아래의 일반(강화하지 않은) 자식 공개 키를 모두 계산할 수 있어서, 개인 키 없이도 그 계정의 입출금 전체를 확인할 수 있습니다[17]. 파생 규칙은 [복구 문구와 파생 경로](seed-derivation.md)에서 다룹니다.

같은 회사가 두 종류를 함께 내놓는 일이 흔합니다. Coinbase 거래소 앱과 Coinbase Wallet 앱은 저장소가 서로 다르고, 한 앱의 데이터에는 다른 앱의 기록이 들어 있지 않습니다[3][4]. 비수탁 지갑이라도 거래소 계정과 연결하면 거래소가 그 주소를 받습니다. Coinbase 는 Base App(이전 이름 Coinbase Wallet)을 Coinbase 계정에 연결하면 지갑 주소를 수집합니다[11]. 업비트는 "개인 지갑주소 등록" 항목으로 본인 디지털 자산 주소를 수집하고, NFT 개인지갑주소 등록도 따로 둡니다[12].

### 서명을 어디서 하나: 전체 기능 지갑·서명 전용 지갑·배포 전용 지갑

지갑 시스템은 공개 키를 나눠 주는 부분, 서명하는 부분, 네트워크에 연결하는 부분으로 나눌 수 있고, 이 셋을 어떻게 묶느냐에 따라 지갑 종류가 달라집니다[1].

전체 기능 지갑 (full-service wallet)은 세 부분을 한 프로그램이 다 합니다. 개인 키가 인터넷에 연결된 기기에 있어서, 많은 지갑 프로그램이 지갑 파일 암호화를 선택 기능으로 둡니다. 널리 쓰는 지갑은 거의 모두 전체 기능 지갑으로 쓸 수 있습니다[1].

서명 전용 지갑 (signing-only wallet)은 부모 개인 키를 만들어 보관하고, 부모 공개 키만 네트워크 쪽 지갑에 넘깁니다. 네트워크 쪽 지갑이 자식 공개 키로 주소를 만들고 서명하지 않은 트랜잭션을 만들어 넘기면, 서명 전용 지갑이 서명해서 돌려줍니다[1]. 서명 전용 지갑의 흔한 형태는 오프라인 지갑과 하드웨어 지갑입니다[1].

- 오프라인 지갑 (offline wallet): 네트워크에 연결하지 않는 기기에서 키를 만들고 서명합니다. 온라인 기기의 지갑은 부모 공개 키만 받는 감시 전용 지갑 (watching-only wallet)이 되고, 두 기기 사이의 데이터는 보통 USB 드라이브 같은 이동식 매체로 옮깁니다[1].
- 하드웨어 지갑 (hardware wallet): 서명 전용 지갑을 돌리는 전용 장치입니다. 장치 화면에서 거래 내용을 확인하고, 장치에 따라 PIN 이나 암호를 묻습니다[1]. 개인 키는 장치 안의 보안 요소 (secure element)에 격리되어 있고, PC·휴대폰의 연동 프로그램이 USB 나 블루투스로 장치와 통신합니다. Ledger Live 는 Electron 기반 데스크톱 앱이고, Trezor Wallet 은 PC 에 설치한 Trezor Bridge 프로그램을 거쳐 장치와 통신하는 웹 앱입니다[14].

배포 전용 지갑 (distributing-only wallet)은 웹 서버처럼 보안을 지키기 어려운 환경에서 공개 키나 주소만 나눠 줍니다. 미리 만든 주소를 DB 에 넣어 두거나, 부모 공개 키로 자식 주소를 계속 만듭니다[1]. 결제를 받는 웹 서버에서 주소 목록이 나와도 그 서버에는 개인 키가 없을 수 있습니다.

### 종류별로 남는 것

| 종류 | 개인 키가 있는 곳 | 분석 대상 기기에 남는 것 | 기기 밖에서 구할 기록 |
|---|---|---|---|
| 수탁형 (거래소 계정) | 거래소 | 거래소 앱의 계정·잔액 캐시[3] | 거래소의 KYC 정보, 잔액, 은행 계좌, 거래·입금·출금 내역, IP·기기 내역[10] |
| 비수탁형 전체 기능 지갑 | 그 기기의 지갑 파일 | 주소, 파생 경로, 확장 공개 키, 거래 기록[4] | 블록체인의 거래, RPC 제공자의 접속 기록[16] |
| 오프라인 지갑 | 네트워크에 연결하지 않는 다른 기기 | 온라인 기기: 부모 공개 키, 주소, 서명 전후 트랜잭션, 이동식 매체 사용 흔적[1] | 오프라인 기기 자체 |
| 하드웨어 지갑 | 장치 안 보안 요소 | 연동 프로그램의 장치 정보, 확장 공개 키, 거래 내역[14] | 장치 자체 |

### 한 앱 안에 여러 종류가 섞이는 경우

브라우저 확장 지갑 하나에 소프트웨어 키, 하드웨어 지갑 연동, 수탁 서비스 연동이 함께 들어갈 수 있습니다. MetaMask 는 키 묶음을 키링 (keyring) 단위로 관리하고, 키링마다 아래 형식 문자열이 붙습니다[7][8].

| 키링 형식 문자열 | 뜻 |
|---|---|
| `HD Key Tree` | 복구 문구에서 파생한 계정 |
| `Simple Key Pair` | 개인 키를 직접 가져온 계정 (코드 이름 `imported`) |
| `Ledger Hardware`, `Trezor Hardware`, `OneKey Hardware`, `Lattice Hardware`, `QR Hardware Wallet Device` | 하드웨어 지갑 연동 계정 |
| `Snap Keyring`, `Money Keyring` | 그 밖의 키링 |
| `Custody` 로 시작하는 문자열 | 수탁 서비스 연동 계정 |

키링 목록은 암호화된 볼트 (vault) 안에 들어 있어서 디스크에서는 평문으로 보이지 않습니다. KeyringController 상태 중 디스크에 저장하는 것은 `vault` 뿐이고, 키링 형식과 주소를 담은 `keyrings` 는 저장하지 않지만 상태 로그에는 넣습니다[7]. 사용자가 설정의 Privacy 메뉴에서 "Download state logs" 로 상태 로그 JSON 을 내려받은 적이 있으면, 기기에 남은 이 파일에서 키링 형식을 평문으로 볼 수 있습니다[7][18]. Ledger 연동 키링은 `hdPath`, `accounts`, `deviceId`, `accountDetails`(주소별 `index`·`bip44`·`hdPath`), `implementFullBIP44` 를 저장하고 개인 키는 저장하지 않습니다[9].

## 읽는 법

기기에서 나온 지갑 흔적이 어느 종류인지는 아래 순서로 판단합니다. 자세한 수집 방법은 [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md)에서 다룹니다.

1. 패키지 이름·번들 ID·설치 폴더로 앱을 먼저 확인합니다. 같은 브랜드에 거래소 앱과 지갑 앱이 따로 있으므로, "Coinbase" 라는 이름만으로 판단하지 않습니다[3][4].
2. 앱 저장소에 무엇이 있는지 봅니다. 주소 목록·파생 경로·확장 공개 키가 있으면 비수탁형이고, 계정·잔액 캐시만 있으면 수탁형일 가능성이 큽니다. 하드웨어 지갑 연동 프로그램에도 확장 공개 키가 남으므로, 확장 공개 키만으로 그 기기에 개인 키가 있다고 보지 않습니다[14].
3. 하드웨어 지갑 연동 흔적을 찾습니다. 연동 프로그램(Ledger Live, Trezor Bridge) 설치 흔적, 키링 형식 문자열, USB 장치 연결 기록을 함께 봅니다. Trezor Bridge 는 사용자 Application Data 폴더에 로그를 남기고, 이 로그에는 Trezor 가 아닌 USB 장치까지 연결 시각이 기록됩니다[14]. USB 연결 기록은 [USB 저장장치 흔적](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/external-devices/usb-storage-artifacts/)에서 다룹니다.
4. 비수탁 지갑이 거래소 계정과 연결됐는지 확인합니다. 연결했거나 거래소에 개인 지갑 주소를 등록했다면 거래소 기록에도 그 주소가 있습니다[11][12].

## 포렌식에서 중요한 점

### 증명하는 것과 증명하지 못하는 것

비수탁 지갑 앱의 데이터에 주소·확장 공개 키·파생 경로가 있으면, 그 기기의 지갑이 그 주소를 만들었거나 가져왔다는 것을 알 수 있습니다. 확장 공개 키가 있으면 앱에 남은 주소보다 더 많은 주소를 계산해 블록체인과 대조할 수 있습니다[4][17]. 거래소 앱의 캐시로는 그 기기에서 거래소 계정에 접속했다는 것과, 캐시를 저장한 시점의 계정 상태를 알 수 있습니다.

앱 데이터에 주소가 있다고 그 주소를 쓰거나 입금받았다는 뜻은 아닙니다. Coinbase Wallet 의 `address` 표는 앱이 미리 파생한 주소를 담고, 앱 자체의 사용 여부 표시는 시험 이미지 하나에서 491행 중 203행만 참이었습니다[4]. 수탁형 앱은 기기에 키가 없어서, 앱 데이터로 특정 온체인 주소를 사용자와 묶을 수 없습니다. 앱이 보여 주는 잔액도 캐시를 저장한 시점의 값입니다. 하드웨어 지갑을 쓴 PC 에서 개인 키가 나오지 않는 것은 정상이고, 지갑을 쓰지 않았다는 증거가 되지 않습니다.

보고서에는 "피의자가 이 지갑의 주인이다" 가 아니라 "이 기기의 Coinbase Wallet 데이터에 이 주소와 이 확장 공개 키가 있고, 이 주소로 받은 트랜잭션이 블록체인에 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

### 시각

시각의 기준은 기록을 남긴 곳마다 다릅니다. 앱 캐시의 시각은 기기 시계 기준이고, 시간대 표시가 없을 수 있습니다. Coinbase Wallet 의 `account` 표 시각에는 시간대 표시가 없는데, iLEAPP 는 같은 폴더의 MMKV 저장소에 `Z`(UTC) 표시와 함께 기록된 시각이 시험 이미지 두 개에서 계정 행보다 11초·108초 앞선 것을 근거로 UTC 로 읽습니다[4]. 거래소 기록은 거래소가 정한 기준을 따르는데, Binance.US 는 주소나 TXID 로 기록을 요청할 때 UTC 시각을 함께 적으라고 요구합니다[10]. 트랜잭션이 블록에 들어간 시각은 이 둘과 따로 봅니다([블록 시각과 확정](../blockchain/block-time.md)).

### 기기 밖에 남는 기록

수탁형 계정의 기록은 거래소에 있습니다. Binance.US 가 수사기관 요청에 낼 수 있는 기록은 KYC 정보, 잔액, 은행 계좌, 거래·입금·출금 내역, IP 내역, 기기 내역, 고객과 주고받은 연락입니다[10]. 국내에서는 2022년 3월 25일부터 가상자산사업자가 다른 사업자에게 100만 원 상당 이상을 옮길 때 보내는 사람과 받는 사람의 성명·가상자산 주소를 넘기고, 그 정보를 거래관계가 끝난 뒤 5년간 보존합니다. 개인 지갑으로 옮길 때 쓰는 사전 등록제는 법 의무가 아니고 업계가 자율로 운영합니다[13]. 자세한 내용은 [거래소와 가상자산사업자](../ecosystem/exchanges.md)에서 다룹니다.

비수탁 지갑도 기기 밖에 기록을 남깁니다. 지갑은 블록체인 정보를 가져오려고 보통 중앙 RPC 제공자를 기본으로 쓰는데, MetaMask 의 기본 제공자인 Infura 는 개인정보 방침에서 IP 주소와 지갑 주소를 수집한다고 밝혔습니다[16]. 지갑 100개를 조사한 2023년 연구에서는 13개가 사용자 지갑 주소를 제3자에게 넘겼습니다[16].

## 함정

- **같은 브랜드의 두 앱**: Coinbase 거래소 앱과 Coinbase Wallet 은 키를 쥐는 쪽과 저장소가 다릅니다[3][4]. 기록을 가진 법인도 다를 수 있습니다. Binance.US 는 Binance Holdings 와 다른 회사라 Binance 기록을 내지 못하고, Binance.US Web3 Wallet 기록은 BAM Technology Services Inc. 앞으로 따로 요청해야 합니다[10].
- **앱 라벨을 사실로 읽는 것**: Coinbase Wallet 의 Account Type 값 `mnemonic` 은 앱이 붙인 라벨이고, 키를 어떻게 만들었는지 보여 주는 값이 아닙니다[4].
- **거래소 주소를 개인 주소로 보는 것**: Android 지갑 앱을 시험한 논문에서는 시험 거래의 받는 주소 하나가 2021년 7월 기준 1,361번 거래하고 1억 달러 넘게 주고받은 주소였고, 그 거래를 추적 도구로 거슬러 올라가면 보낸 쪽이 Coinbase 로 나왔습니다[15]. 이런 주소는 한 사람의 것이 아닐 수 있어서, 사람을 특정하려면 거래소에 KYC 기록을 요청합니다[15]. 주소를 묶는 방법의 한계는 [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md)에서 다룹니다.
- **연동 프로그램의 메모리 흔적은 오래 남지 않습니다**: Windows 7 SP1 과 Ledger Live 1.18.2 로 시험한 결과, 앱을 잠그고 6분 뒤 메모리에는 확장 공개 키 14개와 명령 이벤트 1개만 남았습니다(최대일 때 각각 1,700개 넘게, 40개). 프로세스를 끝내고 6분 안에 나머지도 모두 덮어써졌습니다[14]. 메모리 분석은 [메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/)과 [하드웨어 지갑과 연결 흔적](../../02-artifacts/hardware/hardware-wallets.md)에서 다룹니다.
- **보조 파일을 빼고 읽는 것**: BRD(BreadWallet) Android 앱의 `platform.db` 는 ALEAPP 시험 자료에서 모든 데이터가 WAL 파일에만 있었고, WAL 없이 읽으면 `kvStoreTable` 에 행이 하나도 없었습니다[6]. 앱 DB 는 `-wal`·`-journal` 파일과 함께 수집합니다([SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/data-formats/sqlite/)).

## 도구

- iLEAPP: `coinbase.py`(Coinbase 거래소 앱), `coinbaseWallet.py`(Coinbase Wallet), `metamask.py`(MetaMask 모바일의 `Documents/persistStore/persist-root`)[3][4][5]
- ALEAPP: `breadWallet.py`(BRD)[6]
- RLEAPP: `coinbaseComplianceReport.py`, `coinbaseArchive.py`(거래소가 수사기관에 낸 자료)[19]
- Memory FORESHADOW: Ledger Live·Trezor Wallet 메모리 흔적을 읽는 Volatility 플러그인[14]

## 참고 문헌

1. Bitcoin Developer Guide, "Wallets". https://developer.bitcoin.org/devguide/wallets.html
2. ethereum.org, "Ethereum accounts". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/accounts/index.md
3. iLEAPP, `scripts/artifacts/coinbase.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbase.py
4. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
5. iLEAPP, `scripts/artifacts/metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
6. ALEAPP, `scripts/artifacts/breadWallet.py`. https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/breadWallet.py
7. MetaMask core, `packages/keyring-controller/src/KeyringController.ts`. https://github.com/MetaMask/core/blob/main/packages/keyring-controller/src/KeyringController.ts
8. MetaMask extension, `shared/constants/keyring.ts`. https://github.com/MetaMask/metamask-extension/blob/main/shared/constants/keyring.ts
9. MetaMask accounts, `packages/keyring-eth-ledger-bridge/src/ledger-keyring.ts`. https://github.com/MetaMask/accounts/blob/main/packages/keyring-eth-ledger-bridge/src/ledger-keyring.ts
10. Binance.US, "Binance.US Law Enforcement Guide". https://support.binance.us/en/articles/9842980-binance-us-law-enforcement-guide
11. Coinbase, "Privacy Policy". https://www.coinbase.com/legal/privacy
12. 두나무, "업비트 개인정보 처리방침". https://static.upbit.com/terms/private_data.html
13. 금융위원회 보도자료, "3.25일 특정금융정보법상 트래블룰이 시행됩니다", 2022-03-24. https://www.fsc.go.kr/no010101/77579
14. Tyler Thomas, Mathew Piscitelli, Ilya Shavrov, Ibrahim Baggili, "Memory FORESHADOW: Memory FOREnSics of HArDware CryptOcurrency wallets – A Tool and Visualization Framework", Forensic Science International: Digital Investigation, 2020. doi:10.1016/j.fsidi.2020.301002
15. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, "Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications", arXiv, 2022. doi:10.48550/arXiv.2205.14611
16. Christof Ferreira Torres, Fiona Willi, Shweta Shinde, "Is Your Wallet Snitching On You? An Analysis on the Privacy Implications of Web3", arXiv, 2023. doi:10.48550/arXiv.2306.08170
17. BIP-32, "Hierarchical Deterministic Wallets". https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
18. MetaMask extension, `docs/state_dump.md`. https://github.com/MetaMask/metamask-extension/blob/main/docs/state_dump.md
19. RLEAPP, `scripts/artifacts/coinbaseComplianceReport.py`, `scripts/artifacts/coinbaseArchive.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseComplianceReport.py , https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseArchive.py
