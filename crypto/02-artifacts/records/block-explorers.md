---
title: "블록 탐색기 기록 읽기"
parent: "아티팩트 · 거래소와 체인 기록"
nav_order: 250
---

# 블록 탐색기 기록 읽기 (Block Explorers)

블록 탐색기 (block explorer) 는 블록·트랜잭션·주소·컨트랙트 데이터를 웹 화면과 API 로 보여 주는 서비스입니다. 기기나 거래소 자료에서 찾은 트랜잭션 ID 와 주소가 실제로 체인에 있는지, 언제 어느 블록에 들어갔는지 확인할 때 가장 먼저 쓰지만, 화면에 나오는 값 가운데 일부는 체인 데이터가 아니라 운영자가 만든 색인과 이름표입니다. 이 페이지는 이더리움·비트코인 탐색기의 화면·API 필드를 읽는 법, 그중 무엇이 체인으로 다시 확인되는 값인지, 기기에 남는 탐색기 사용 흔적을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

블록체인의 블록과 트랜잭션은 누구나 받아 볼 수 있지만, 노드 소프트웨어가 주는 기본 조회 기능만으로는 "이 주소가 관여한 거래 전부" 같은 질문에 답하기 어렵습니다. Bitcoin Core 에는 주소 하나가 관여한 트랜잭션을 모두 돌려주는 API 가 없어서, 주소별로 조회하려면 electrs 같은 색인기 (indexer) 를 따로 돌려야 합니다[31]. 탐색기는 노드에 있는 체인 데이터에 운영자가 만든 색인(주소별 거래 목록, 토큰 전송 목록)과 이름표(라벨)를 더해서 보여 줍니다. 그래서 탐색기 화면의 "주소별 거래 목록" 은 체인 원본을 운영자가 한 번 가공한 결과입니다.

탐색기는 조사에서 두 가지 모습으로 나옵니다. 하나는 분석가가 기기에서 찾은 트랜잭션 ID·주소를 조회하는 도구이고[30], 다른 하나는 용의자나 피해자가 탐색기를 쓴 흔적입니다. 후자는 브라우저 방문 기록의 탐색기 주소, 지갑 앱 설정에 들어 있는 탐색기 이름, 네트워크 기록의 탐색기 도메인으로 남습니다[28][29][32].

이더리움 탐색기로는 오픈소스인 3xpl, Beaconcha.in, Blockscout, lazy-etherscan, Otterscan 과 서비스인 Blockchair, Chainlens, DexGuru, Etherchain, Etherscan, Ethplorer, Ethseer, EthVM, OKLink 가 있습니다[1]. 비트코인은 Blockstream 의 Esplora 처럼 API 서버를 직접 운영할 수 있는 탐색기가 있고[12], Electrum 처럼 지갑 앱 코드 안에 탐색기 목록을 넣어 둔 경우도 있습니다[28].

## 위치와 버전별 차이

탐색기 기록은 두 곳에서 얻습니다. 하나는 탐색기 서비스 자체(웹 화면과 API 응답)이고, 다른 하나는 분석 대상 기기에 남은 탐색기 사용 흔적입니다.

| 어디서 | 무엇이 남나 | 읽는 법 |
|---|---|---|
| 탐색기 API 응답 | 트랜잭션·블록·주소·로그 필드(JSON) | 이 페이지의 "구조" 절 |
| 브라우저 방문 기록 | `/tx/`·`/address/`·`/transaction/` 이 들어간 탐색기 URL | 브라우저별 방문 기록 페이지 |
| Electrum 설정 | `block_explorer`, `block_explorer_custom` 설정 값[29] | [Electrum](../desktop/electrum.md) |
| 네트워크·DNS 기록 | 탐색기 도메인에 보낸 요청 | 이 페이지의 "증거로서 의미" 절 |

방문 기록의 저장 형식은 브라우저마다 다르므로 다른 핸드북을 봅니다. Windows 는 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/)·[파이어폭스](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/firefox/), macOS 는 [사파리](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/browsers/safari/)·[크롬·엣지·웨일](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/browsers/chromium/), Android 는 [크롬](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/browsers/chrome/)·[삼성 인터넷](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/browsers/samsung-internet.html), iOS 는 [사파리](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/browsers/safari/) 페이지에 있습니다.

### 탐색기 URL 모양

Electrum 은 탐색기 주소 뒤에 종류 경로(트랜잭션이면 `tx/`, 주소면 `address/` 등)와 값을 이어 붙여 URL 을 만듭니다[28]. 이 표가 코드에 들어 있어서, 방문 기록에서 탐색기 URL 을 찾으면 경로 뒷부분에서 트랜잭션 ID 나 주소를 뽑을 수 있습니다.

| 탐색기 (Electrum 표의 이름) | 기본 주소 | 트랜잭션 경로 | 주소 경로 |
|---|---|---|---|
| Blockstream.info (Electrum 기본값) | `https://blockstream.info/` | `tx/` | `address/` |
| mempool.space | `https://mempool.space/` | `tx/` | `address/` |
| Blockchain.info | `https://blockchain.com/btc/` | `tx/` | `address/` |
| Blockchair.com | `https://blockchair.com/bitcoin/` | `transaction/` | `address/` |
| 3xpl.com | `https://3xpl.com/bitcoin/` | `transaction/` | `address/` |
| OXT.me | `https://oxt.me/` | `transaction/` | `address/` |
| Chain.so | `https://www.chain.so/` | `tx/BTC/` | `address/BTC/` |
| BlockCypher.com | `https://live.blockcypher.com/btc/` | `tx/` | `address/` |
| Bitaps.com, BTC.com | `https://btc.bitaps.com/`, `https://btc.com/` | 경로 없이 값 | 경로 없이 값 |

테스트넷·testnet4·시그넷 (signet) 은 표가 따로 있어서 `https://mempool.space/testnet/`, `https://mempool.space/testnet4/`, `https://mempool.space/signet/` 처럼 경로가 다릅니다[28]. Esplora 공개 API 도 메인넷은 `https://blockstream.info/api/`, 테스트넷은 `/testnet/api/`, 시그넷은 `/signet/api/` 로 나뉩니다[12]. URL 에 이런 경로가 있으면 실제 가치가 있는 자산의 거래가 아닙니다.

Electrum 의 `block_explorer` 설정은 "웹 브라우저를 여는 기능에 쓸 온라인 탐색기" 이고 기본값은 `Blockstream.info` 입니다[29]. 사용자가 `block_explorer_custom` 에 문자열을 넣으면 Electrum 은 그 주소에 기본 경로 `tx/`·`address/` 를 붙여 씁니다[28]. 설정 값이 기본값과 다르면 사용자가 탐색기를 직접 골랐을 가능성이 있습니다.

### API 버전

Etherscan API 는 v2 에서 주소가 `https://api.etherscan.io/v2/api` 이고, 체인을 고르는 `chainid` 매개변수(1 = 이더리움, 42161 = Arbitrum 등)와 API 키를 받습니다[2]. 무료 요금제는 초당 3회, 하루 10만 회까지이고 일부 체인만 조회됩니다[9]. 같은 주소를 조회해도 `chainid` 가 다르면 다른 체인의 기록이 나오므로, 결과를 저장할 때 요청 URL 전체를 함께 남깁니다.

## 구조

이더리움 쪽은 Etherscan API, 비트코인 쪽은 Esplora API 를 기준으로 필드를 정리합니다. 다른 탐색기도 화면에 보여 주는 항목은 거의 같지만 필드 이름과 단위가 다르므로, 그 탐색기의 API 문서로 한 번 더 맞춰 봅니다. 블록·트랜잭션 자체의 구조는 [블록과 트랜잭션](../../01-foundations/blockchain/blocks-transactions.md)에서, 계정과 로그는 [이더리움의 계정과 로그](../../01-foundations/blockchain/ethereum-accounts.md)에서 다룹니다.

### 이더리움 트랜잭션 화면

탐색기의 트랜잭션 화면에는 트랜잭션 해시, 상태(대기·실패·성공), 블록, 시각, 보낸 주소(From), 받는 주소 또는 호출한 컨트랙트(To), 옮긴 토큰, 금액(ETH), 수수료(가스 가격 × 사용한 가스)가 나옵니다[1]. 더 펼치면 가스 한도, 사용한 가스, 가스 가격, 논스 (nonce), 입력 데이터가 나옵니다[1]. 논스는 보낸 주소가 보낸 트랜잭션의 번호이고 0부터 세므로, 논스 100 은 그 주소의 101번째 트랜잭션입니다[1].

### Etherscan 거래 목록 세 가지

컨트랙트가 옮긴 ETH 는 내부 거래 (internal transaction) 목록에, 토큰 이동은 토큰 전송 목록에 따로 나옵니다[2][3][4]. 그래서 주소 하나의 거래를 모으려면 목록을 따로따로 받아야 합니다.

| 요청 (`module=account`) | 담는 것 | 주요 필드 |
|---|---|---|
| `action=txlist` | 주소가 보내거나 받은 일반 트랜잭션 | `blockNumber`, `blockHash`, `timeStamp`, `hash`, `nonce`, `transactionIndex`, `from`, `to`, `value`, `gas`, `gasPrice`, `input`, `methodId`, `functionName`, `contractAddress`, `cumulativeGasUsed`, `txreceipt_status`, `gasUsed`, `confirmations`, `isError`[2] |
| `action=txlistinternal` | 컨트랙트 실행 중에 생긴 내부 호출 | `type`(call, create, create2, self-destruct), `traceId`, `isError`, `errCode`[3] |
| `action=tokentx` | ERC-20 토큰 전송 | `contractAddress`, `value`, `tokenName`, `tokenSymbol`, `tokenDecimal`[4] |
| `action=tokennfttx` | ERC-721 토큰 전송 | 위 필드에 `tokenID` 가 더해짐[5] |

필드마다 읽는 법이 정해져 있습니다. `value` 와 `gasPrice` 는 wei 단위입니다[2]. `to` 가 비어 있으면 컨트랙트를 만든 트랜잭션이고, 그때 만들어진 주소는 `contractAddress` 에 나옵니다[2]. `txreceipt_status` 는 1 이 성공, 0 이 실패이고 비잔티움 (Byzantium) 이전 블록은 비어 있습니다[2]. `methodId` 는 입력 데이터의 앞 4바이트이고, `functionName` 은 대상 컨트랙트의 소스가 검증된 경우에만 해독해서 채웁니다[2]. 토큰 `value` 는 토큰의 최소 단위라서 10 의 `tokenDecimal` 제곱으로 나눠야 화면의 수량이 됩니다[4]. 응답 전체의 `status` 가 0 이면 오류일 수도 있고 결과가 없을 수도 있어서, `message` 필드를 함께 봅니다[2].

목록은 `page`·`offset` 으로 나뉘고 `startblock`·`endblock` 으로 블록 범위를 정하며, `sort` 는 `asc`(오래된 것부터)나 `desc`(최신부터)입니다[2]. 첫 페이지만 받으면 오래된 거래가 빠집니다.

### 이벤트 로그

`module=logs&action=getLogs` 는 컨트랙트가 낸 이벤트 로그를 돌려줍니다. `address` 는 로그를 낸 컨트랙트, `topics` 는 색인된 인자의 배열이고 첫 topic 은 이벤트 서명의 해시입니다[6]. 로그의 topic 은 0~4개이고, anonymous 로 선언한 이벤트는 첫 topic 에 서명 해시가 없습니다[15].

ERC-20 의 `Transfer(address indexed _from, address indexed _to, uint256 _value)` 와 ERC-721 의 `Transfer(address indexed _from, address indexed _to, uint256 indexed _tokenId)` 는 서명 문자열이 `Transfer(address,address,uint256)` 로 같아서 첫 topic 도 `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef` 로 같습니다[16][17][6]. ERC-721 은 토큰 번호까지 색인되어 topic 이 4개이고, ERC-20 은 금액이 `data` 에 들어가 topic 이 3개입니다[16][17]. 첫 topic 만 보고 둘을 구분할 수 없으므로 topic 개수를 확인합니다.

getLogs 응답에서는 `blockNumber`, `timeStamp`, `logIndex`, `transactionIndex`, `gasPrice`, `gasUsed` 가 16진수 문자열입니다[6]. txlist 의 `timeStamp` 는 10진수 문자열이라서[2], 같은 탐색기 안에서도 요청 종류에 따라 표기가 다릅니다.

노드에 직접 조회하는 JSON-RPC 의 로그에는 `removed` 필드가 있고, 체인 재구성 (reorganization) 으로 로그가 빠지면 `true` 가 됩니다[15].

### 비트코인 트랜잭션·주소·블록 (Esplora)

Esplora API 의 금액은 모두 사토시 단위입니다[12].

| 요청 | 주요 필드 |
|---|---|
| `GET /tx/:txid` | `txid`, `version`, `locktime`, `size`, `weight`, `fee`, `vin[]`(`txid`, `vout`, `is_coinbase`, `scriptsig`, `witness[]`, `prevout` 등), `vout[]`(`scriptpubkey`, `scriptpubkey_type`, `scriptpubkey_address`, `value`), `status`(`confirmed`, `block_height`, `block_hash`, `block_time`)[12] |
| `GET /tx/:txid/outspend/:vout` | 그 출력이 쓰였는지(`spent`), 쓴 트랜잭션의 `txid`·`vin`·`status`[12] |
| `GET /tx/:txid/merkle-proof` | 블록 포함 증명(머클 증명)[12] |
| `GET /address/:address` | `chain_stats`·`mempool_stats` 안의 `tx_count`, `funded_txo_count`, `funded_txo_sum`, `spent_txo_count`, `spent_txo_sum`[12] |
| `GET /address/:address/txs` | 최신순. 미확정 최대 50건과 확정 첫 25건[12] |
| `GET /address/:address/txs/chain/:last_seen_txid` | 확정 거래를 25건씩 이어서[12] |
| `GET /block/:hash` | `id`, `height`, `version`, `timestamp`, `mediantime`, `bits`, `nonce`, `merkle_root`, `tx_count`, `size`, `weight`, `previousblockhash`[12] |
| `GET /block/:hash/status` | `in_best_chain`(고아 블록이면 false), `next_best`[12] |

비트코인 잔액은 쓰이지 않은 출력 (UTXO) 의 합입니다[27]. Esplora 에서는 주소가 받은 출력의 합(`funded_txo_sum`)에서 쓴 출력의 합(`spent_txo_sum`)을 빼면 남은 UTXO 의 합, 곧 잔액이 됩니다[12]. UTXO 는 [비트코인의 UTXO](../../01-foundations/blockchain/utxo.md) 페이지에서 다룹니다.

### 라벨

탐색기 화면에서 주소 옆에 붙는 "Binance" 같은 이름은 운영자가 붙인 라벨입니다. Etherscan 은 라벨을 붙인 주소 목록을 Enterprise 요금제 고객에게만 내보내고[10], 내보낸 CSV 에는 `address`, `nametag`, `internal_nametag`, `url`, `shortdescription`, `notes_1`, `notes_2`, `labels`, `labels_slug`, `reputation`, `other_attributes`, `lastupdatedtimestamp` 열이 있습니다[10]. 라벨 분류에는 거래소 이름(`binance`)뿐 아니라 `phish-hack`, `ofac-sanctioned` 같은 것도 있습니다[10][11]. `lastupdatedtimestamp` 열이 있다는 데서 알 수 있듯이, 라벨은 체인 데이터가 아니라 운영자가 고치고 갱신하는 메타데이터입니다.

## 증거로서 의미

### 증명하는 것

체인 데이터로 다시 계산하거나 다른 노드에서 똑같이 받아 볼 수 있는 값은 증거로 씁니다. 트랜잭션이 있다는 사실, 들어간 블록의 해시와 높이, 입력·출력 주소와 금액, 수수료, 성공·실패 상태, 블록 시각이 여기에 들어갑니다[1][2][12]. 비트코인은 머클 증명으로 트랜잭션이 블록에 들어 있는지 탐색기와 따로 확인할 수 있습니다[12].

기기 쪽 흔적으로는, 브라우저 방문 기록에 남은 `/tx/`·`/address/` URL 이 사람이 주소창이나 링크로 연 페이지라는 것을 보여 줍니다. 경로 뒤의 값이 기기의 지갑 데이터에 있는 트랜잭션 ID·주소와 같으면 두 기록을 이어 볼 수 있습니다.

### 증명하지 못하는 것

주소 주인이 누구인지는 탐색기로 증명하지 못합니다. 라벨은 운영자의 판단이고 평판·갱신 시각 필드가 달린 추정입니다[10][11]. 주소 하나가 한 사람만의 것이 아닐 수도 있습니다. 2021년 6월의 한 시험 거래에서 상대 주소는 2021년 7월 blockchain.com 기록으로 1,361번 거래하고 1억 달러 넘게 주고받은 주소였습니다[30]. 입력 주소 여럿이 한 사람의 것이라는 추정은 [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md)에서 다룹니다.

토큰 전송 목록도 실제 잔액 이동을 보장하지 않습니다. 이벤트는 컨트랙트 코드가 쓰는 대로 나오는데, 사기 토큰 wARB 는 컨트랙트 주인이 보낸 토큰의 `Transfer` 이벤트에 보낸 사람을 다른 주소(deployer)로 바꿔 넣었습니다[18]. 탐색기에 "X 에서 받았다" 고 나와도 X 가 실제로 보냈다고 쓸 수 없습니다. 외부 소유 계정 (EOA) 의 지출을 승인하는 `Approval` 이벤트는 그 계정이 토큰 컨트랙트에 직접 보낸 트랜잭션에서만 정상적으로 생기므로, 그 밖의 경로로 생긴 승인은 의심해 봅니다[18].

탐색기 결과가 빠짐없다는 것도 증명하지 못합니다. 확장 공개 키 (xpub) 로 거래를 찾는 공개 조회 도구 7개를 시험한 연구에서, 6개는 xpub 에서 세그윗 주소를 스스로 만들어 내지 못했고 일부는 ypub·zpub 을 줘도 세그윗 거래가 나오지 않았습니다[31]. 주소 간격을 100 으로 벌려 만든 주소의 거래는 Ledger 의 xpub-scan 을 뺀 나머지 도구에서 나오지 않았습니다[31]. 파생 경로와 간격 한도는 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)에서 다룹니다.

탐색기 서버의 응답은 프로그램 오류나 악의로 틀리거나 늦을 수 있고, 로컬에 둔 원장과 비교해야만 맞는지 확인됩니다[31]. 소스 검증 표시는 제출된 소스를 탐색기가 따로 컴파일해 배포된 바이트코드와 같은지 확인했다는 뜻일 뿐[18], 그 컨트랙트가 정상이라는 뜻은 아닙니다.

네트워크 기록의 탐색기 도메인은 사람이 직접 조회했다는 증거가 아닙니다. 브라우저 지갑 확장 100개를 시험한 연구에서 13개가 사용자 지갑 주소를 제3자 24곳 가운데 하나 이상에 보냈고, Coinbase Wallet 확장은 etherscan.io, bscscan.com, polygonscan.com, arbiscan.io, blockscout.com 을 포함한 10곳에 보냈습니다[32]. 같은 연구에서 DApp 8곳은 JSON-RPC 제공자인 Etherscan 에 지갑 주소를 보냈습니다[32]. 지갑 앱이 잔액을 가져오려고 탐색기 API 를 부른 기록일 가능성이 있으므로, 사람이 연 페이지인지는 브라우저 방문 기록으로 따로 확인합니다.

### 보고서 문장

보고서에는 기록으로 확인되는 만큼만 씁니다. 예: "이 기기의 지갑 앱 데이터에 트랜잭션 ID A 가 있고, 이 트랜잭션은 비트코인 블록 N(해시 B)에 들어 있으며 블록 시각은 2024-05-01 03:12:45 UTC 이다(A·B·N 은 실제 값으로 바꾸고, 시각은 만든 예시)." 탐색기 라벨을 쓸 때는 "Etherscan 이 이 주소에 'X' 라벨을 붙여 두었다(내려받은 시각 …)" 처럼 누가 붙인 이름인지 밝힙니다.

## 시각 해석

탐색기가 보여 주는 트랜잭션 시각은 그 트랜잭션이 들어간 블록의 시각입니다. 사용자가 트랜잭션을 만들거나 서명한 시각이 아니어서, 트랜잭션이 대기열에 오래 머물렀다면 두 시각의 차이가 커집니다. 블록 시각이 정해지는 원리와 확정 수는 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에서 다루고, 여기서는 탐색기 필드가 무엇을 가리키는지만 정리합니다.

| 필드 | 무엇의 시각인가 | 표기 |
|---|---|---|
| 이더리움 화면 Timestamp | 트랜잭션이 들어간 블록이 제안된 시각[1] | 화면마다 다름 |
| Etherscan txlist `timeStamp` | 블록이 만들어진 시각[2] | UNIX 초, 10진수 문자열 |
| Etherscan getLogs `timeStamp` | 블록이 만들어진 시각[6] | UNIX 초, 16진수 문자열 |
| JSON-RPC 블록 `timestamp` | 블록을 모은(collated) 시각[15] | UNIX 초, 16진수 |
| Esplora `status.block_time` | 들어간 블록의 시각[12] | UNIX 초, 확정 전에는 null |
| Esplora 블록 `timestamp`, `mediantime` | 블록 헤더 시각, 앞선 블록들의 중앙값[12] | UNIX 초 |
| Bitcoin Core `gettransaction` 의 `time`, `timereceived`, `blocktime` | 지갑의 트랜잭션 시각, 지갑이 받은 시각, 블록 시각[23] | UNIX 초 |

UNIX 초는 UTC 기준이라 한국 시각으로 바꿀 때는 9시간을 더합니다. 문서에 실린 공식 예시로 바꿔 보면, Etherscan txlist 의 `"timeStamp": "1759129619"` 는 2025-09-29 07:06:59 UTC(16:06:59 KST)이고[2], getLogs 의 `"timeStamp": "0x60f9ce56"` 은 10진수 1626984022 로 바꾼 뒤 2021-07-22 20:00:22 UTC 가 됩니다[6]. 웹 화면은 탐색기에 따라 현지 시각으로 바꿔 보여 주기도 하므로, 화면 값을 옮길 때는 그 화면이 어느 시간대로 보여 주는지 먼저 확인하고 되도록 API 의 UNIX 초를 씁니다.

비트코인 블록 헤더 시각은 채굴자가 헤더를 해싱하기 시작한 시각이고 채굴자가 적은 값입니다[19]. 이 값은 앞선 11개 블록 시각의 중앙값보다 커야 하고, 노드는 자기 시계보다 2시간 넘게 앞선 헤더의 블록을 받지 않습니다[19]. 그래서 블록 시각은 실제 시각과 어긋날 수 있고, 높이가 큰 블록의 시각이 앞 블록보다 이를 수도 있습니다. 이더리움은 12초 슬롯마다 블록이 하나씩 제안되지만 제안자가 차례를 놓치면 그 슬롯은 비어 있습니다[14].

Bitcoin Core 지갑의 `gettransaction` 은 트랜잭션 시각, 지갑이 받은 시각, 블록 시각을 따로 돌려줍니다[23]. 지갑 앱이 보여 주는 시각과 탐색기의 블록 시각이 다르면 이 차이부터 확인합니다.

확정 전 트랜잭션은 블록과 시각이 비어 있습니다. Etherscan 의 `eth_getTransactionByHash` 는 대기 중이면 `blockHash`·`blockNumber`·`transactionIndex` 가 null 이고[7], Esplora 의 `block_height`·`block_hash`·`block_time` 도 확정 전에는 null 입니다[12].

## 함정과 한계

**단위와 진법.** 이더리움 금액은 wei, 비트코인 금액은 사토시, 토큰 수량은 최소 단위로 나옵니다[2][4][12]. 같은 Etherscan 안에서도 txlist 는 10진수, getLogs 는 16진수입니다[2][6].

**목록 나눔.** Esplora 주소 거래 목록은 25건씩 나오고[12], Etherscan 은 `page`·`offset` 으로 나뉩니다[2]. 일반 거래·내부 거래·토큰 전송 목록을 셋 다 받지 않으면 ETH 이동과 토큰 이동이 빠집니다[2][3][4].

**비트코인 해시의 바이트 순서.** 직렬화된 블록·트랜잭션 안의 해시는 내부 바이트 순서 (internal byte order) 로 들어 있고, Bitcoin Core RPC 와 많은 탐색기는 바이트를 뒤집은 RPC 바이트 순서로 보여 줍니다[22]. 원시 데이터에서 잘라 낸 32바이트를 그대로 탐색기에 넣으면 결과가 나오지 않으므로, 뒤집은 값으로도 조회합니다. 블록도 흔히 헤더 해시를 뒤집어 16진수로 적은 값으로 부릅니다[20].

**트랜잭션 ID 가 바뀌는 경우.** BIP-125 의 교체 가능 표시를 단 미확정 트랜잭션은 노드가 대기열에서 다른 트랜잭션으로 바꿀 수 있습니다[25]. 탐색기에서 본 미확정 트랜잭션 ID 가 끝내 확정되지 않고 다른 ID 의 트랜잭션이 확정될 수 있습니다. 세그윗 (BIP-141) 에서 `txid` 는 증인 데이터를 뺀 직렬화의 해시로 그대로 두고, 증인까지 포함한 해시는 `wtxid` 로 따로 부릅니다[26]. 탐색기 검색창에는 `txid` 를 넣습니다.

**블록이 버려지는 경우.** 같은 높이에 블록 두 개가 생기는 분기는 흔하고, 짧은 쪽 블록은 버려집니다[20]. 그래서 블록 높이는 전역 고유 식별자가 아니며 블록은 해시로 부릅니다[20]. 확정 1회는 최신 블록에 들어갔다는 뜻이지만 최신 블록은 꽤 자주 교체되고, 고액 거래는 최소 6회 확정을 기다리라고 권합니다[21]. Bitcoin Core `gettransaction` 의 `confirmations` 가 음수면 그만큼 앞선 블록에서 충돌이 있었다는 뜻이고, `getblock` 의 `confirmations` 가 -1 이면 메인 체인 밖의 블록입니다[23][24]. Esplora 에서는 `in_best_chain` 이 false 입니다[12]. 이더리움 블록은 시간이 지나면 justified, finalized 로 올라가고, finalized 된 블록은 네트워크 수준의 공격 없이는 바뀌지 않습니다[13].

**함수 이름 해독.** 입력 데이터의 앞 4바이트는 함수 선택자 (function selector) 입니다[13]. 선택자 `0xa9059cbb` 와 같은 값을 쓰는 알려진 함수가 여럿 있어서, 이 선택자가 `transfer(address,uint256)` 인지는 컨트랙트 소스가 탐색기에 올라와 있을 때 확정됩니다[13]. `functionName` 이 비어 있거나 소스가 검증되지 않은 컨트랙트라면 선택자만 기록합니다[2].

**탐색기마다 다른 표시.** WalletExplorer 는 코인베이스 트랜잭션의 입력 수를 0 으로 보여 줍니다[33]. 같은 트랜잭션도 탐색기마다 입력 수나 금액 표시가 다를 수 있어서, 보고서에는 어느 탐색기의 어떤 필드인지 적습니다.

**출처끼리 다른 설명.** BlockQuery 논문은 "주소에서 비트코인을 보내려면 그 주소의 비트코인 전부를 보내야 한다" 고 설명하지만[31], 비트코인 개발자 문서는 입력 하나가 이전 출력(UTXO) 하나를 통째로 쓴다고 설명합니다[27]. 주소가 아니라 UTXO 단위로 쓰인다고 보고 해석합니다.

**조회가 남기는 흔적.** 제3자 탐색기에 조회하면 운영자는 조회한 IP 와 조회한 주소를 이어 볼 수 있습니다[31]. BlockQuery 연구에서 시험한 조회 도구 7개 가운데 로컬 체인을 조회하게 해 주는 것은 2개였습니다[31]. Esplora 는 API 서버를 직접 운영할 수 있고[12], electrs 는 제3자 서버와 통신하지 않는 색인기입니다[31]. 민감한 사건이면 직접 운영하는 노드와 색인기로 조회합니다.

**재현성.** 탐색기 화면은 라벨이 바뀌고 체인이 재구성되면 달라집니다. 화면 캡처만 남기지 말고 API 원시 응답(JSON)을 요청 URL, 받은 시각(UTC)과 함께 저장하고 파일 해시값을 기록합니다.

## 직접 분석해 보기

### 헥스로 한 번: ERC-20 Transfer 로그 읽기

아래는 ERC-20 명세의 `Transfer` 이벤트 구조대로 만든 예시 로그입니다(주소와 금액은 만든 예시).

```text
topics[0] 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
topics[1] 0x000000000000000000000000000000000000000000000000000000000000a11c
topics[2] 0x000000000000000000000000000000000000000000000000000000000000b0b0
data      0x00000000000000000000000000000000000000000000000014d1120d7b160000
```

첫 topic 이 `Transfer(address,address,uint256)` 의 서명 해시라서 전송 이벤트이고[6][16], topic 이 3개라서 ERC-721 이 아니라 ERC-20 입니다[16][17]. 두 번째와 세 번째 topic 은 20바이트 주소 앞을 0으로 채운 32바이트 값이라서, 뒤 20바이트가 보낸 주소와 받은 주소입니다[6][13]. `data` 의 금액 `0x14d1120d7b160000` 은 10진수 1500000000000000000 이고, 토큰의 `tokenDecimal` 이 18 이면 1.5 개입니다[4]. 이 로그를 낸 컨트랙트 주소(`address`)가 조사 대상 토큰의 컨트랙트와 같은지도 확인합니다. wARB 처럼 진짜 토큰(ARB)과 같은 것인 척하는 가짜 토큰이 있어서, 진짜 컨트랙트 주소는 토큰을 낸 단체의 문서로 확인합니다[18].

### 헥스로 한 번 더: 비트코인 트랜잭션 ID 뒤집기

원시 데이터에서 입력이 가리키는 이전 트랜잭션 해시 32바이트를 잘라 냈다고 합시다(만든 예시).

```text
내부 바이트 순서 000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
RPC 바이트 순서  1f1e1d1c1b1a191817161514131211100f0e0d0c0b0a09080706050403020100
```

탐색기와 Bitcoin Core RPC 는 아래 줄처럼 뒤집은 값을 씁니다[22]. 파이썬이라면 `bytes.fromhex(s)[::-1].hex()` 로 바꿉니다.

### 공개 도구로 한 번

Esplora 공개 API 는 문서의 예시처럼 `curl` 로 바로 부를 수 있습니다[12]. 테스트넷 트랜잭션 하나로 연습하면 실제 사건 정보를 제3자에게 보내지 않아도 됩니다.

```text
curl https://blockstream.info/testnet/api/tx/TXID
curl https://blockstream.info/testnet/api/tx/TXID/merkle-proof
curl https://blockstream.info/testnet/api/block/BLOCKHASH/status
```

`TXID`·`BLOCKHASH` 자리에 값을 넣습니다. 첫 응답의 `status.block_hash` 로 세 번째 요청을 보내 `in_best_chain` 이 true 인지 보고, 머클 증명이 그 블록의 `merkle_root` 와 맞는지 확인합니다[12]. 이더리움은 Etherscan v2 의 txlist·txlistinternal·tokentx 를 같은 주소로 세 번 부르고, 셋을 `hash` 로 합쳐 한 표로 정리합니다[2][3][4]. 성공·실패는 `eth_getTransactionReceipt` 의 `status`(1 성공, 0 실패)로 한 번 더 봅니다[8]. 같은 요청을 직접 운영하는 노드의 JSON-RPC 로 보내고 블록 태그 `finalized` 로 확정 여부를 보면, 탐색기 응답과 체인 원본이 같은지 확인할 수 있습니다[15].

## 교차 검증

탐색기 기록은 혼자 쓰지 않고 기기와 거래소 자료에 이어서 씁니다. 기기의 지갑 데이터에 있는 트랜잭션 ID·주소는 [Electrum](../desktop/electrum.md), [MetaMask](../browser/metamask/index.md), [Android 지갑 앱](../mobile/android-wallets.md), [iOS 지갑 앱](../mobile/ios-wallets.md) 페이지에서, 거래소가 내준 입출금 기록의 트랜잭션 해시는 [거래소가 제공하는 자료](exchange-records.md)에서 다룹니다. 메모리나 클립보드에서 찾은 문자열이 주소나 트랜잭션 ID 인지는 [주소 형식](../../01-foundations/wallets/address-formats.md)과 [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md)로 확인합니다.

거래를 여러 단계 따라가는 절차는 [비트코인 거래 따라가기](../../03-techniques/analysis/bitcoin-tracing.md)와 [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md)에서, 기기 시각·블록 시각·거래소 시각을 한 줄로 합치는 방법은 [암호화폐 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 실습

비트코인 테스트넷·시그넷과 이더리움 테스트넷은 실제 가치가 없어서 연습에 씁니다. 테스트넷 탐색기 경로는 위 "탐색기 URL 모양" 표 아래에 있습니다[28][12].

1. 테스트넷 트랜잭션 하나를 Esplora API 와 mempool.space 화면으로 각각 조회하고, 금액(사토시)·수수료·블록 시각이 같은지 비교합니다. 화면의 시각이 어느 시간대인지도 적습니다.
2. 같은 트랜잭션의 원시 헥스(`GET /tx/:txid/hex`)에서 입력이 가리키는 이전 트랜잭션 해시를 잘라 내고, 바이트를 뒤집어야 탐색기에서 찾히는지 확인합니다[12][22].
3. Etherscan 문서의 txlist·getLogs 공식 예시 응답에서 `timeStamp` 를 UTC 와 KST 로 바꿔 봅니다[2][6].
4. 이더리움 테스트넷 주소 하나에 대해 txlist, txlistinternal, tokentx 를 모두 받고, 한 목록에만 나오는 거래가 있는지 찾습니다[2][3][4].
5. 브라우저 방문 기록에서 탐색기 URL 을 모두 뽑고, 경로가 `/testnet/`·`/signet/` 인 것과 메인넷인 것을 나눕니다[28].

## 참고 문헌

1. ethereum.org, "Block explorers". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/data-and-analytics/block-explorers/index.md
2. Etherscan API, "Get Normal Transactions By Address (txlist)". https://docs.etherscan.io/api-reference/endpoint/txlist.md
3. Etherscan API, "Get Internal Transactions by Address (txlistinternal)". https://docs.etherscan.io/api-reference/endpoint/txlistinternal.md
4. Etherscan API, "Get ERC20 Token Transfers by Address (tokentx)". https://docs.etherscan.io/api-reference/endpoint/tokentx.md
5. Etherscan API, "Get ERC721 Token Transfers by Address (tokennfttx)". https://docs.etherscan.io/api-reference/endpoint/tokennfttx.md
6. Etherscan API, "Get Event Logs by Address (getLogs)". https://docs.etherscan.io/api-reference/endpoint/getlogs.md
7. Etherscan API, "eth_getTransactionByHash". https://docs.etherscan.io/api-reference/endpoint/ethgettransactionbyhash.md
8. Etherscan API, "eth_getTransactionReceipt". https://docs.etherscan.io/api-reference/endpoint/ethgettransactionreceipt.md
9. Etherscan API, "Rate Limits". https://docs.etherscan.io/rate-limits.md
10. Etherscan API, "Export Address Tags". https://docs.etherscan.io/api-reference/endpoint/exportaddresstags-v2.md
11. Etherscan API, "Export Label Master List". https://docs.etherscan.io/api-reference/endpoint/getlabelmasterlist-v2.md
12. Blockstream, "Esplora HTTP API". https://github.com/Blockstream/esplora/blob/master/API.md
13. ethereum.org, "Transactions". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/transactions/index.md
14. ethereum.org, "Blocks". https://ethereum.org/en/developers/docs/blocks/
15. ethereum.org, "JSON-RPC API". https://ethereum.org/en/developers/docs/apis/json-rpc/
16. ethereum.org, "ERC-20 Token Standard". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/standards/tokens/erc-20/index.md
17. ethereum.org, "ERC-721 Non-Fungible Token Standard". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/standards/tokens/erc-721/index.md
18. ethereum.org, "Scam token tricks". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/tutorials/scam-token-tricks/index.md
19. Bitcoin Developer Reference, "Block Chain — Block Headers". https://developer.bitcoin.org/reference/block_chain.html
20. Bitcoin Developer Guide, "Block Chain". https://developer.bitcoin.org/devguide/block_chain.html
21. Bitcoin Developer Guide, "Payment Processing". https://developer.bitcoin.org/devguide/payment_processing.html
22. Bitcoin Developer Glossary, "Internal byte order", "RPC byte order". https://developer.bitcoin.org/glossary.html
23. Bitcoin Core RPC, "gettransaction". https://developer.bitcoin.org/reference/rpc/gettransaction.html
24. Bitcoin Core RPC, "getblock". https://developer.bitcoin.org/reference/rpc/getblock.html
25. BIP-125, "Opt-in Full Replace-by-Fee Signaling". https://github.com/bitcoin/bips/blob/master/bip-0125.mediawiki
26. BIP-141, "Segregated Witness (Consensus layer)". https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki
27. Bitcoin Developer Guide, "Transactions". https://developer.bitcoin.org/devguide/transactions.html
28. Electrum, `electrum/util.py`. https://github.com/spesmilo/electrum/blob/master/electrum/util.py
29. Electrum, `electrum/simple_config.py`. https://github.com/spesmilo/electrum/blob/master/electrum/simple_config.py
30. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, 「Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications」, arXiv, 2022, doi:10.48550/arXiv.2205.14611
31. Tyler Thomas, Tiffanie Edwards, Ibrahim Baggili, 「BlockQuery: Toward forensically sound cryptocurrency investigation」, Forensic Science International: Digital Investigation 40, 2022, doi:10.1016/j.fsidi.2022.301340
32. Christof Ferreira Torres, Fiona Willi, Shweta Shinde, 「Is Your Wallet Snitching On You? An Analysis on the Privacy Implications of Web3」, arXiv, 2023, doi:10.48550/arXiv.2306.08170
33. Yanan Gong, Kam Pui Chow, Siu Ming Yiu, Hing Fung Ting, 「Analyzing the peeling chain patterns on the Bitcoin blockchain」, Forensic Science International: Digital Investigation, 2023, doi:10.1016/j.fsidi.2023.301614
