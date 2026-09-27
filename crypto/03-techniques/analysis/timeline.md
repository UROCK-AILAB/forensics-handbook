---
title: "암호화폐 타임라인"
parent: "기법 · 분석"
nav_order: 330
---

# 암호화폐 타임라인 (Timeline)

암호화폐 사건의 시각은 기기의 지갑 앱, 블록체인, 거래소 자료 세 곳에서 나오고, 곳마다 시각을 적는 주체와 단위와 시간대가 다릅니다. 이 페이지는 세 출처의 시각을 트랜잭션 ID 로 묶어 한 줄로 합치는 절차와, 합친 결과에서 순서와 시각을 어디까지 주장할 수 있는지를 다룹니다. 각 시각 필드의 정의와 블록 시각·확정의 원리는 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에서 다루고, 여기서는 그 값을 합치는 방법만 씁니다.

## 언제 쓰나

"언제 지갑을 만들고, 언제 보냈고, 언제 거래소에 들어갔나" 를 한 표로 보여 줘야 할 때 씁니다. 지갑 앱의 거래 목록은 사용자가 트랜잭션을 만들고 제출한 시각을 보여 주고, 블록체인은 트랜잭션이 어느 블록에 들어갔는지를 보여 주며, 거래소 자료는 계정에서 출금을 요청하고 처리한 시각을 보여 줍니다. 한 출처만 보면 사건의 일부만 보이므로 세 출처를 합쳐야 앞뒤가 이어집니다.

운영체제 전체의 사용 흔적(파일 시스템·레지스트리·로그)을 합치는 방법은 [Windows 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/), [macOS 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/timeline/), [Linux 타임라인 만들기](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html), [Android 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/android/03-techniques/analysis/timeline/), [iOS 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/analysis/timeline/)에서 다룹니다. 이 페이지의 결과는 그 타임라인에 트랜잭션 줄을 더하는 식으로 합칩니다.

## 절차

### 1. 출처마다 시각 필드를 모으고 원래 값을 그대로 둔다

먼저 출처별로 시각 필드를 뽑되, 바꾼 값과 함께 원래 값·원래 단위·시간대 표시 유무를 같은 줄에 남깁니다. 그래야 나중에 변환 규칙이 틀린 것이 드러나도 원래 값에서 다시 계산할 수 있습니다. 합친 표에는 아래 열을 두면 됩니다.

| 열 | 넣을 값 |
|---|---|
| UTC 시각 | 아래 2단계에서 바꾼 값 |
| 원래 값 | 파일·API 에 적힌 그대로의 값 |
| 시각 종류 | 기기 시각, 블록 시각, 거래소 기록 시각 중 하나 |
| 시간대 근거 | 오프셋 명시, 약어 명시, 유닉스 시각, 시간대 없음 중 하나 |
| 사건 | 생성·제출·블록 포함·출금 요청 등 |
| 체인·TXID | 체인 이름(이더리움은 체인 ID 까지)과 트랜잭션 ID |
| 블록 높이·블록 안 순번 | 체인에서 조회한 값 |
| 출처 | 파일 경로나 API 요청, 쓴 도구와 버전 |

기기 쪽에서는 한 트랜잭션에 시각이 여러 개 있을 수 있습니다. MetaMask 는 트랜잭션 기록을 처음 만들 때(상태 `unapproved`) `time` 에 `Date.now()` 값을 넣고[9], 네트워크에 제출하는 순간 `submittedTime` 에 밀리초 시각을 넣으며[8][9], 영수증과 블록 해시가 확인되면 그 블록을 조회해 블록의 `timestamp` 를 `blockTimestamp` 에 옮겨 적습니다[10]. 그래서 MetaMask 트랜잭션 하나에서 "만든 시각 → 제출한 시각 → 블록 시각" 세 줄을 뽑을 수 있습니다. Bitcoin Core 지갑은 `gettransaction` 에서 `time`·`timereceived`·`blocktime` 을 유닉스 초로 돌려줍니다[3]. 기기 파일에 시각이 없어도 트랜잭션 ID 가 남으면 체인에서 시각을 얻을 수 있습니다. Android Coinomi 9.26.3 은 받은 비트코인 거래마다 `com.coinomi.wallet/cache/16자 헥스 폴더/bitcoin.main/` 아래에 트랜잭션 해시를 이름으로 한 파일을 남깁니다[19]. 앱별 저장 위치는 [기기에서 지갑 흔적 찾기](../acquisition/artifact-search.md)에서 다룹니다.

체인 쪽 시각은 노드나 탐색기에 트랜잭션 ID 로 물어 얻습니다. 비트코인은 Esplora `GET /tx/:txid/status` 의 `block_height`·`block_hash`·`block_time`[4], 이더리움은 `eth_getTransactionByHash` 의 `blockNumber`·`transactionIndex` 와 그 블록의 `timestamp` 를 씁니다[5]. 거래소 쪽은 제출 자료의 시각 열을 그대로 옮깁니다. 거래소 자료의 열 구성은 [거래소 자료 분석](exchange-analysis.md)에서 다룹니다.

### 2. 단위·진법·시간대를 맞춰 UTC 로 바꾼다

값의 모양만 보고 단위를 짐작하지 않고, 필드 정의에서 단위를 확인한 뒤 바꿉니다. MetaMask `submittedTime` 은 정의상 밀리초이고[8], `time` 은 `Date.now()` 로 채우므로 밀리초입니다[9]. `blockTimestamp` 는 블록 조회 결과를 문자열로 옮긴 값이고[8][10] 이더리움 JSON-RPC 는 블록 `timestamp` 를 `0x` 로 시작하는 16진수로 돌려주므로[5], 실제 값이 16진인지 먼저 봅니다. Etherscan 은 `txlist` 의 `timeStamp` 를 10진 문자열로[6], `getLogs` 의 `timeStamp` 를 16진 문자열로 돌려줍니다[7].

도구가 단위를 대신 판단하는 경우도 있습니다. iLEAPP 의 MetaMask 분석기는 `time` 을 `convert_unix_ts_to_utc` 로 바꾸는데[11], 이 함수는 값의 크기(10¹⁰ 이상이면 밀리초, 10¹³ 이상이면 마이크로초, 10¹⁶ 이상이면 나노초)로 단위를 정합니다[12]. 1970-01-01 앞뒤 약 4개월 안의 값은 크기만으로 단위를 구분할 수 없어서, 단위를 알면 이 함수에 맡기지 말고 직접 바꿔야 합니다[12]. 암호화폐 기록에서 이 범위의 값이 나올 일은 드물지만, 결과가 1970년 근처로 나오면 원래 값을 다시 봅니다.

시간대는 값에 표시가 있을 때만 확정합니다. 유닉스 시각은 UTC 기준이라 그대로 바꾸면 되고, 문제는 거래소 자료와 앱이 적은 날짜 문자열입니다. 시간대 표시가 없는 값은 원래 값과 "시간대 없음" 을 함께 적고, 같은 기기나 같은 제출 자료 안에서 시간대가 적힌 다른 값과 비교해 기준을 정합니다. 예를 들어 Coinbase Wallet(iOS)의 `wallet-rn-v2.sqlite` 에 저장된 `createdAt`·`confirmedAt` 에는 시간대 표시가 없습니다. 같은 앱의 MMKV 저장소(`Documents/mmkv/CBStore.plaintext`)에는 `Z` 를 붙여 적은 시각이 있고, iOS 16.5·17.5.1 시험 이미지 두 개에서 이 시각은 계정 행의 `createdAt` 보다 11초·108초 앞선 같은 날 같은 시였습니다[13]. 저장된 값이 현지 시각이었다면 몇 시간씩 벌어졌을 것이라 iLEAPP 는 이 값들을 UTC 로 읽습니다[13]. 이렇게 근거를 적어 두어야 보고서에서 변환을 설명할 수 있습니다. 거래소 자료의 시간대 처리는 4단계에서 다룹니다.

### 3. 트랜잭션 ID 로 세 출처를 잇는다

세 출처는 트랜잭션 ID 로 잇습니다. 기기의 거래 목록(MetaMask `hash`[8], Bitcoin Core 지갑의 `txid`[3], Coinomi 캐시 파일 이름[19])과 거래소 자료의 해시 열(Coinbase 컴플라이언스 보고서 `TRANSACTION HASH`[14], Robinhood `blockchain_txn_id`[16])을 체인에서 조회한 트랜잭션과 맞춥니다. Coinbase 보고서의 TRANSACTIONS 섹션에는 `TRANSACTION HASH` 열과 따로 `TRANSACTION ID` 열도 있으므로[14], 어느 열의 값이 체인에서 조회되는지 실제 값으로 확인한 뒤 씁니다. 트랜잭션 ID 를 검색할 때 바이트 순서와 표기 차이는 [비트코인 거래 따라가기](bitcoin-tracing.md)와 [이더리움 거래 따라가기](ethereum-tracing.md)에서 다룹니다.

트랜잭션 ID 가 맞으면 금액과 주소도 함께 비교합니다. 트랜잭션 ID 만 같고 금액이나 받는 주소가 다르면 체인을 잘못 골랐거나(같은 해시 모양을 쓰는 다른 체인), 기록을 잘못 읽었을 가능성이 있습니다. 이더리움 계열은 체인 ID 를 먼저 정하고 조회합니다. MetaMask 기록에는 `chainId` 필드가 있고[8], Etherscan API 는 `chainid` 로 조회할 체인을 고릅니다[6].

### 4. 거래소 기록 시각은 원래 표기와 변환 규칙을 함께 옮긴다

거래소 자료는 열마다 시간대 표기가 다를 수 있습니다. Robinhood 자료에서 `crypto_account_transfers.csv` 의 `created_at` 에는 오프셋이 있지만, 주문 파일의 `Time Entered` 와 접속 기록의 `event_date_time` 에는 시간대가 없고, PDF 명세서의 시각은 인쇄된 약어(EST = UTC-5)로 읽어야 합니다[16]. Coinbase 컴플라이언스 보고서도 오프셋(-0800, Z)이나 시간대 약어가 붙은 값과 붙지 않은 값이 섞여 있습니다[14].

같은 도구 모음 안에서도 시간대 없는 값을 다루는 방식이 다릅니다. RLEAPP 의 Coinbase 컴플라이언스 보고서 분석기와 Robinhood 분석기는 시간대가 없는 값을 바꾸지 않고 "zone not stated" 로 남기고[14][16], 같은 RLEAPP 의 Coinbase 아카이브 분석기와 Cash App 분석기는 시간대가 없는 값을 UTC 로 간주해 붙입니다[15][17]. 그래서 도구의 UTC 열을 그대로 쓰지 말고, 원래 값과 도구가 적은 근거 열(Time Basis 등)을 함께 옮깁니다. 거래소에 자료를 요청할 때부터 UTC 로 달라고 하면 이 문제가 줄어듭니다. Binance.US 는 트랜잭션 ID 로 요청할 때 금액·입출력 주소·UTC 시각을 함께 적으라고 안내합니다[18].

Robinhood 출금 한 건에서는 요청 시각(`created_at`), 제출 시각(`withdrawal_submitted_timestamp`), 체인 쪽 상태(`blockchain_txn_state`)를 얻을 수 있습니다[16]. 이 세 값과 체인의 블록 시각을 한 줄씩 넣으면 거래소 안에서 출금을 처리한 시간과 블록에 들어가기까지 걸린 시간이 구분됩니다.

### 5. 순서는 블록 높이로, 시각은 블록 시각으로 정렬한다

체인 사건끼리의 순서는 블록 시각이 아니라 블록 높이와 블록 안 순번으로 정합니다. 비트코인 블록 시각은 앞 11블록 시각의 중앙값보다만 크면 되므로[1], 높은 블록의 시각이 바로 앞 블록보다 이를 수 있습니다. 실제로 블록 362940 의 시각은 2015-06-28 17:18:34 UTC 이고 다음 블록 362941 의 시각은 17:16:02 UTC 라서 순서가 거꾸로이고, 블록 655042 와 655043 은 시각이 같습니다[2]. 블록 안 순번은 Bitcoin Core 지갑 `gettransaction` 의 `blockindex`[3], 이더리움 `transactionIndex` 와 로그의 `logIndex` 로 얻습니다[5].

그래서 합친 표는 두 가지 정렬을 함께 씁니다. 체인 사건은 "블록 높이 → 블록 안 순번" 으로 순서를 정하고, 기기·거래소 사건은 UTC 시각으로 그 사이에 끼워 넣습니다. 두 정렬이 부딪히는 곳, 예를 들어 기기의 제출 시각이 그 트랜잭션의 블록 시각보다 늦은 곳은 지우지 말고 표시해 6단계에서 봅니다.

### 6. 앞뒤가 맞는지 확인한다

한 트랜잭션의 시각은 "만듦 → 제출 → 블록 포함 → 확정" 순서가 정상입니다[8][9][10]. 이 순서가 깨지면 원인을 찾아 적습니다.

- 이더리움에서 기기의 제출 시각이 블록 시각보다 늦으면 기기 시계가 틀렸거나 시간대를 잘못 읽었을 가능성이 있습니다.
- 비트코인은 노드가 자기 시계보다 2시간 이내로 앞선 블록 시각을 받아들이므로[1], 제출 시각이 블록 시각보다 조금 늦은 것만으로 기기 시계가 틀렸다고 판단하지 않습니다.
- 기기 목록에는 있는데 체인에 없는 트랜잭션은 교체·취소·실패를 먼저 의심합니다(아래 "함정과 한계").
- 확정 단계는 조회 시점에 다시 확인합니다. 비트코인은 `getblock` 의 `confirmations` 가 -1 이면 그 블록이 주 체인에 없고[21], 이더리움은 `finalized` 태그로 조회한 블록과 높이가 같거나 낮은 블록이면 확정(finalized)된 것으로 봅니다[5][20].

### 7. 만든 예시로 본 합친 표

아래는 한 사람의 MetaMask 송금과 거래소 입금을 합친 표를 보여 주려고 만든 예시입니다. 시각·원래 값·블록 높이는 모두 지어낸 값입니다.

| UTC 시각 (만든 예시) | 시각 종류 | 사건 | 원래 값 (만든 예시) | 블록 높이·순번 |
|---|---|---|---|---|
| 2025-03-02 01:14:05 | 기기 | MetaMask 트랜잭션 생성(`time`) | `1740878045123` (밀리초) | — |
| 2025-03-02 01:14:31 | 기기 | MetaMask 제출(`submittedTime`) | `1740878071480` (밀리초) | — |
| 2025-03-02 01:14:47 | 블록 | 블록 포함(`timestamp`) | `0x67c3b107` (16진 초) | 21,950,000 · 17 |
| 2025-03-02 01:15:10 | 거래소 | 입금 기록 | `2025-03-02 10:15:10` (시간대 없음, UTC+9 로 판단한 근거를 따로 적음) | — |

마지막 줄은 원래 값에 시간대가 없어서, 같은 제출 자료 안의 오프셋이 붙은 다른 값과 비교해 UTC+9 로 읽었다는 근거를 표 밖에 적어 둡니다. 근거가 없으면 그 줄은 "시간대 없음" 으로 남기고 다른 줄과 순서를 주장하지 않습니다.

## 도구

**Esplora API.** `GET /tx/:txid/status` 로 비트코인 트랜잭션의 확정 여부·블록 높이·블록 해시·블록 시각을, `GET /block/:hash/status` 로 그 블록이 주 체인에 있는지(`in_best_chain`)를 얻습니다[4].

**Bitcoin Core RPC.** `gettransaction` 으로 지갑 트랜잭션의 `time`·`timereceived`·`blocktime`·`blockindex`·`confirmations`·`walletconflicts` 를[3], `getblock` 으로 블록의 `time`·`mediantime`·`confirmations` 를 얻습니다[21].

**이더리움 JSON-RPC.** `eth_getTransactionByHash` 로 블록 번호와 블록 안 순번을, `eth_getBlockByNumber` 로 블록 `timestamp` 를, `eth_getLogs` 로 로그의 `logIndex`·`removed` 를 얻습니다[5]. 값은 16진수입니다[5].

**Etherscan API.** `txlist`·`getLogs` 로 주소나 컨트랙트 기준 목록을 한 번에 받습니다. 진법이 API 마다 다르니 따로 바꿉니다[6][7].

**iLEAPP·RLEAPP.** iLEAPP 는 iOS 이미지의 MetaMask·Coinbase Wallet 거래 시각을 UTC 로 바꿔 보여 주고[11][13], Coinbase Wallet 분석기 일부는 결과를 타임라인 형식으로도 냅니다[13]. RLEAPP 는 Coinbase·Robinhood·Cash App 제출 자료를 읽습니다[14][15][16][17]. 두 도구 모두 변환 규칙이 분석기마다 달라서, 결과 표의 UTC 열과 원래 값 열을 함께 옮깁니다.

## 함정과 한계

**기기 목록의 트랜잭션이 체인에 없을 수 있습니다.** MetaMask 는 같은 계정의 다음 nonce 가 이 트랜잭션의 nonce 보다 커졌는데 영수증이 없으면, 노드가 뒤처져 있을 수 있어서 3블록을 더 기다린 뒤 `dropped` 로 바꿉니다[9][10]. 같은 nonce 로 가속·취소한 트랜잭션이 대신 들어갔다면 기기 목록에는 `dropped` 원본과 체인에 들어간 교체본이 함께 남을 가능성이 있습니다. 비트코인도 BIP-125 교체 신호가 있는 미확정 트랜잭션은 같은 입력을 쓰는 새 트랜잭션으로 바뀔 수 있고[22], Bitcoin Core 지갑은 이런 충돌을 `walletconflicts` 와 음수 `confirmations` 로 남깁니다[3]. 이런 줄은 지우지 말고 "체인에 없음" 으로 표시해 둡니다. 교체된 트랜잭션을 따라가는 법은 [비트코인 거래 따라가기](bitcoin-tracing.md)에서 다룹니다.

**미확정 기록에는 블록 시각이 없습니다.** 이더리움 트랜잭션은 대기 중이면 `blockNumber`·`blockHash`·`transactionIndex` 가 `null` 이고[5], Esplora 는 미확정 트랜잭션의 `block_height`·`block_hash`·`block_time` 을 `null` 로 둡니다[4]. 체인이 재구성되면 이더리움 로그의 `removed` 가 `true` 가 됩니다[5]. 수집 당시 탐색기 화면에 있던 블록 정보는 현재 체인에서 다시 조회해 확인합니다.

**탐색기 화면 시각의 시간대를 확인해야 합니다.** Android 지갑 논문에서는 같은 비트코인 트랜잭션이 논문 표(UTC 명시)에는 2021-06-14 03:14 로, blockchain.com 화면 기록에는 시간대 표시 없이 2021-06-13 23:15 로 적혀 약 4시간 차이가 납니다[19]. 화면 캡처의 시각은 탐색기가 어느 시간대로 보여 주는지 확인한 뒤 쓰고, 가능하면 API 가 돌려주는 유닉스 시각으로 바꿔 씁니다. 탐색기 기록을 증거로 다루는 법은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)에서 다룹니다.

**거래소 내부 이동은 체인에 없습니다.** 같은 거래소 안의 이체나 매매는 거래소 기록에만 있으므로, 체인 줄과 이어지지 않는다고 기록이 틀린 것은 아닙니다. Binance.US 운영사처럼 제출 기록의 정확성과 완전성을 보증하지 않는다고 밝힌 거래소도 있으므로[18], 체인과 맞출 수 있는 줄은 맞춰 보고 결과를 적습니다.

**도구 결과의 UTC 열이 도구의 가정일 수 있습니다.** 4단계에서 본 것처럼 같은 RLEAPP 안에서도 시간대 없는 값을 UTC 로 간주하는 분석기가 있습니다[15][17]. 도구가 적은 변환 근거를 확인하지 않고 UTC 열만 옮기면 몇 시간씩 어긋난 표가 됩니다.

## 결과를 어떻게 해석하나

### 증명하는 것

체인 줄은 트랜잭션이 어느 높이·해시의 블록에 몇 번째로 들어갔는지를 보여 주고, 이 순서는 블록 시각보다 확실합니다[1][3][5]. 트랜잭션이 블록에 들어갔으면 늦어도 그 블록이 만들어질 무렵에는 트랜잭션이 있었습니다. 기기 줄은 그 기기의 지갑 앱이 이 트랜잭션을 만들고 제출했다고 기록했다는 것을 보여 주고, 트랜잭션 ID 가 같으면 기기 기록과 체인 기록이 같은 트랜잭션을 가리킨다는 것까지 확인됩니다. 거래소 줄은 거래소 시스템에 그 계정의 요청·처리 기록이 있다는 것을 보여 줍니다.

### 증명하지 못하는 것

블록 시각은 사용자가 보내기를 누른 시각이 아닙니다. 서명과 제출은 블록 포함보다 먼저 일어나고, 그 시각은 기기 기록에만 있습니다[8][9]. 비트코인 블록 시각은 채굴자가 적은 값이라 초 단위로 정확하다고 주장할 수 없고, 블록끼리 시각 순서가 뒤집힐 수 있습니다[1][2]. 시간대 표시가 없는 기기·거래소 시각은 근거를 찾기 전까지 UTC 라고 주장할 수 없습니다[13][14][16]. 기기 시각은 기기 시계를 따르므로, 기기 시계가 틀렸다면 체인 줄과 몇 분·몇 시간씩 어긋납니다.

### 시각 해석과 보고서 문장

합친 표의 시각은 세 종류라서 보고서에도 종류를 밝혀 씁니다. 블록 시각은 블록을 만든 쪽이 적은 유닉스 시각(UTC), 기기 시각은 기기 시계로 앱이 적은 시각, 거래소 기록 시각은 거래소 시스템이 적은 시각입니다. 보고서 문장은 "2025-03-02 01:14:31 UTC(기기 시각)에 이 기기의 MetaMask 기록에 이 트랜잭션의 제출 시각이 있고, 이 트랜잭션은 블록 21,950,000(블록 시각 01:14:47 UTC)에 들어갔다(만든 예시)" 처럼 시각마다 출처를 붙입니다. 보고서 전체의 작성 원칙은 [암호화폐 포렌식 보고서](../reporting/forensic-report.md)에서 다룹니다.

## 참고 문헌

1. Bitcoin Developer Reference, "Block Chain — Block Headers". https://developer.bitcoin.org/reference/block_chain.html
2. Yanan Gong, Kam Pui Chow, Siu Ming Yiu, Hing Fung Ting, "Analyzing the peeling chain patterns on the Bitcoin blockchain", Forensic Science International: Digital Investigation 46, 2023. doi:10.1016/j.fsidi.2023.301614
3. Bitcoin Core RPC Reference, "gettransaction". https://developer.bitcoin.org/reference/rpc/gettransaction.html
4. Blockstream Esplora, "HTTP REST API". https://github.com/Blockstream/esplora/blob/master/API.md
5. ethereum.org, "JSON-RPC API". https://ethereum.org/en/developers/docs/apis/json-rpc/
6. Etherscan API, "Get a list of 'Normal' Transactions By Address (txlist)". https://docs.etherscan.io/api-reference/endpoint/txlist.md
7. Etherscan API, "Get Event Logs (getLogs)". https://docs.etherscan.io/api-reference/endpoint/getlogs.md
8. MetaMask core, `packages/transaction-controller/src/types.ts`. https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/types.ts
9. MetaMask core, `packages/transaction-controller/src/TransactionController.ts`. https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/TransactionController.ts
10. MetaMask core, `packages/transaction-controller/src/helpers/PendingTransactionTracker.ts`. https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/helpers/PendingTransactionTracker.ts
11. iLEAPP, `scripts/artifacts/metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
12. iLEAPP, `scripts/ilapfuncs.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/ilapfuncs.py
13. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
14. RLEAPP, `scripts/artifacts/coinbaseComplianceReport.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseComplianceReport.py
15. RLEAPP, `scripts/artifacts/coinbaseArchive.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseArchive.py
16. RLEAPP, `scripts/artifacts/robinhoodReturns.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/robinhoodReturns.py
17. RLEAPP, `scripts/artifacts/cashappReturns.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/cashappReturns.py
18. Binance.US, "Binance.US Law Enforcement Guide". https://support.binance.us/en/articles/9842980-binance-us-law-enforcement-guide
19. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, "Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications", arXiv, 2022. doi:10.48550/arXiv.2205.14611
20. ethereum.org, "Proof-of-stake (PoS)". https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/
21. Bitcoin Core RPC Reference, "getblock". https://developer.bitcoin.org/reference/rpc/getblock.html
22. BIP-125, "Opt-in Full Replace-by-Fee Signaling". https://github.com/bitcoin/bips/blob/master/bip-0125.mediawiki
