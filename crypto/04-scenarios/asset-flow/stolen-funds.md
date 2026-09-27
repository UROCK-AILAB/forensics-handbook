---
title: "빼앗긴 자산은 어디로 갔나"
parent: "시나리오 · 자산 흐름"
nav_order: 350
---

# 빼앗긴 자산은 어디로 갔나 (Stolen Funds)

피해자의 지갑에서 암호화폐가 빠져나갔을 때, 피해자 기기에서 빠져나간 트랜잭션을 찾고 블록체인에서 그 돈이 어느 주소를 거쳐 어디에 닿았는지 따라가는 순서를 다룹니다. 트랜잭션으로 곧바로 이어진 이동은 블록체인으로 확인되지만, 잔돈 출력 판단이나 주소 묶기는 추정이라 보고서에서 둘을 나눠 적어야 합니다. 트랜잭션 한 건을 읽고 다음 출력으로 넘어가는 자세한 절차는 [비트코인 거래 따라가기](../../03-techniques/analysis/bitcoin-tracing.md)와 [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md)에 있고, 여기서는 피해 사건에서 무엇을 어떤 순서로 보고 어떻게 해석하는지를 씁니다.

## 조사 질문

- 피해자 지갑에서 빠져나간 트랜잭션은 무엇이고, 언제 블록에 들어갔는가.
- 빠져나간 돈은 어느 주소로 갔고, 그 뒤 어떤 트랜잭션을 거쳐 어디까지 이어지는가.
- 흐름이 끝나는 곳이 거래소·믹서 같은 서비스인가, 아직 쓰이지 않은 출력으로 남아 있는가.
- 이 가운데 블록체인 기록으로 확인되는 부분과 추정인 부분은 어디까지인가.

## 먼저 확인할 것

**체인과 자산.** 비트코인은 출력을 입력으로 쓰는 UTXO 방식이고, 이더리움은 계정끼리 주고받는 방식이라 따라가는 방법이 다릅니다. 이더리움 계열은 같은 주소 형식을 여러 체인이 함께 쓰므로 체인 ID 도 적어 둡니다. Etherscan API v2 는 요청마다 `chainid` 를 받고, 1 은 Ethereum, 42161 은 Arbitrum 입니다[13]. 토큰이 빠져나갔으면 토큰 컨트랙트 주소까지 확인합니다. 구조는 [비트코인의 UTXO](../../01-foundations/blockchain/utxo.md), [이더리움의 계정과 로그](../../01-foundations/blockchain/ethereum-accounts.md), [토큰과 NFT](../../01-foundations/blockchain/tokens.md)에 있습니다.

**피해자 기기에서 얻을 시작점.** 따라가기의 출발점은 트랜잭션 해시, 피해자 지갑의 주소, 확장 공개 키 (xpub) 셋입니다. 셋 중 트랜잭션 해시가 가장 좁고 확실한 출발점입니다. 기기의 시간대 설정과 지갑 앱 버전도 기록해 둡니다. 기기에서 지갑 데이터를 찾는 순서는 [이 기기로 지갑을 썼나](../device-use/wallet-use.md)에 있습니다.

**조회할 곳.** 제3자 블록 탐색기에 주소나 트랜잭션 ID 를 넣으면 어떤 주소를 조사하는지 운영자에게 드러납니다[22]. 조사 사실을 감추고 결과를 스스로 검증하려면 자체 전체 노드와 인덱서(electrs 등)를 씁니다[22]. Bitcoin Core RPC 에는 주소별 거래 목록을 돌려주는 기능이 없어 인덱서가 필요합니다[22]. 탐색기 결과를 읽는 법은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)에 있습니다.

**피해 방식.** 서명 사기로 토큰 권한이 넘어간 사건이면 [피싱 사이트에 서명했나](../fraud/wallet-drainer.md)를, 악성 코드가 지갑 파일을 가져간 사건이면 [악성 코드가 지갑을 노렸나](../device-use/wallet-stealer.md)를 함께 봅니다. 빠져나간 트랜잭션을 누가 만들었는지는 이 두 페이지의 흔적으로 판단합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 피해자 기기의 지갑 데이터 | 빠져나간 트랜잭션 해시, 보낸 주소·받는 주소, 앱이 기록한 시각, 주소록 | [MetaMask](../../02-artifacts/browser/metamask/index.md), [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md), [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md), [하드웨어 지갑과 연결 흔적](../../02-artifacts/hardware/hardware-wallets.md) |
| 2 | 지갑 앱 밖에 남은 주소·해시 문자열 | 메모·메신저·스크린샷에 적힌 주소와 트랜잭션 ID | [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md) |
| 3 | 확장 공개 키로 파생한 주소 | 피해자 지갑의 모든 주소와 잔돈 주소 | [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md), [주소 형식](../../01-foundations/wallets/address-formats.md) |
| 4 | 블록체인 트랜잭션과 영수증 | 입력·출력, 금액, 블록 높이·블록 시각, 성공 여부, 토큰 로그 | [비트코인 거래 따라가기](../../03-techniques/analysis/bitcoin-tracing.md), [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md) |
| 5 | 주소 묶기 결과와 외부 라벨 | 같은 주체일 가능성이 있는 주소 묶음, 서비스 이름 | [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md) |
| 6 | 서비스 쪽 기록 | 거래소 계정, 입금 기록 | [거래소로 들어갔나](exchange-deposit.md), [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md) |

## 분석 흐름

1. **피해자 기기에서 빠져나간 트랜잭션을 찾습니다.** iOS MetaMask 는 `Documents/persistStore/persist-root` JSON 의 `engine` → `backgroundState` → `TransactionController.transactions` 배열에 트랜잭션을 두고, iLEAPP 는 항목마다 `time`, `transaction.from`, `transaction.to`, `transaction.value`(16진 wei 를 ETH 로 바꿔 표시), `transactionHash` 를 읽습니다[1]. 주소록은 `AddressBookController.addressBook` 아래 체인 ID 별로 `name`·`address` 가 있습니다[1]. iOS Coinbase Wallet 은 `Documents/default/wallet-rn-v2.sqlite` 의 `tx_history_v2` 표(옛 버전은 `tx_history`)에 거래를 두고, `isSent`·`fromAddress`·`toAddress`·`amount`·`fee`·`txHash`·`createdAt`·`confirmedAt` 같은 열이 있습니다[2]. 금액과 수수료 열은 자산마다 가장 작은 단위 그대로 저장돼 있습니다[2]. iLEAPP 의 시험 이미지 두 개(iOS 16.5, 17.5.1)에는 받은 거래(`RECEIVE`)만 한 건씩 있었으므로[2], 보낸 거래 행이 어떤 모양인지는 실제 데이터로 확인합니다. 앱별 구조는 1번 표의 아티팩트 페이지에 있습니다.

2. **트랜잭션 한 건을 블록체인에서 확인합니다.** 비트코인은 Esplora API 의 `GET /tx/:txid` 가 `vin`(입력, 쓰인 이전 출력 `prevout` 포함), `vout`(출력별 `scriptpubkey_address`·`value`), `fee`, `status`(`confirmed`·`block_height`·`block_hash`·`block_time`)를 돌려줍니다[7]. 이더리움은 트랜잭션의 `from`·`to`·`value` 와 영수증의 `status`(1 성공, 0 실패)·`logs` 를 함께 봅니다[8][9]. `status` 가 0 이면 실패한 트랜잭션이므로 `status` 부터 봅니다[9]. 기기에 있던 해시·주소·금액이 블록체인 기록과 같은지 여기서 맞춥니다.

3. **이더리움 토큰은 받는 사람을 따로 찾습니다.** ERC-20 토큰을 보내는 트랜잭션은 `to` 가 토큰 컨트랙트이고, 받는 주소와 수량은 입력 데이터와 `Transfer` 이벤트 로그에 있습니다[8][10]. 명세의 서명으로 keccak256 을 계산하면 `Transfer(address,address,uint256)` 은 `ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef` 이고, `transfer(address,uint256)` 의 함수 선택자(해시 앞 4바이트)는 `a9059cbb` 입니다[10]. 로그의 `topics[0]` 이 이 해시이고, `topics[1]`·`topics[2]` 가 32바이트로 채운 보낸 주소·받는 주소입니다[10][14]. iLEAPP 의 MetaMask 트랜잭션 표는 `transaction.to` 와 `value` 를 보여 줄 뿐 입력 데이터는 읽지 않으므로[1], 토큰 전송 행은 받는 쪽이 토큰 컨트랙트로, 금액이 0 으로 보일 수 있습니다. 이런 행은 입력 데이터 앞 4바이트와 영수증 로그로 실제 받는 주소를 확인합니다.

4. **피해자 지갑의 주소를 빠짐없이 모읍니다.** 확장 공개 키가 있으면 받는 주소 체인(change=0)과 잔돈 주소 체인(change=1)을 둘 다 파생합니다[3][22]. BIP44 는 안 쓴 주소가 20개 이어지면 검색을 멈추는 주소 간격 한도 (gap limit) 20 을 정해 두었고[3], 이 한도를 넘겨 만든 주소는 한도 20을 가정하는 도구가 찾지 못합니다[22]. xpub·ypub·zpub 는 서로 바꿀 수 있어 어떤 표현을 얻었든 `1…`·`3…`·`bc1…` 세 형식을 모두 파생합니다[22]. 이렇게 모은 주소 목록이 있어야 "피해자 지갑 안에서 옮긴 것" 과 "밖으로 나간 것" 을 구분할 수 있습니다.

5. **다음 홉을 따라갑니다.** 비트코인은 받는 출력이 쓰였는지를 Esplora `GET /tx/:txid/outspend/:vout` 로 확인하고, 쓰였으면 그 출력을 쓴 트랜잭션의 `txid`·`vin` 이 나옵니다[7]. 트랜잭션 ID 는 가변성 때문에 바뀔 수 있어 흐름은 입력으로 쓰인 출력을 기준으로 잇습니다[4]. 주소 하나의 확정된 거래 전체는 `GET /address/:address/txs/chain` 으로 한 번에 25건씩, 최신 거래부터 받고, 마지막으로 본 `txid` 를 붙여 다음 페이지를 받습니다[7]. 이더리움은 주소의 일반 트랜잭션(`txlist`)[11], 컨트랙트 안에서 옮긴 ETH(`txlistinternal`)[12], 토큰 전송(`tokentx`)[13]을 따로 모아 합칩니다. `tokentx` 의 `from` 은 설명이 일반 트랜잭션과 같은 "Address that sent the transaction" 이라[11][13], 토큰을 보낸 주소인지 트랜잭션에 서명한 주소인지는 영수증 로그로 확인합니다.

6. **출력마다 받는 사람인지 잔돈인지 판단합니다.** 비트코인 트랜잭션은 대부분 받는 사람 출력과 잔돈 출력이 함께 있습니다[4]. 입력 주소 하나에 출력 주소 둘인 `<1:2>` 모양은 보통 단순 지불로 읽고, 입력과 같은 주소가 출력에 있으면 그 출력이 잔돈입니다[21]. `<1:1>` 은 자기 주소로 옮기거나 잔돈 없이 지불한 것이고, `<many:1>` 은 여러 주소의 돈을 모은 것이며, `<1:many>` 는 여러 사람에게 한꺼번에 보낸 묶음 지불(거래소 출금에 흔함)이거나 자기 주소들로 나눈 것입니다[21]. 잔돈 판단 규칙은 여러 가지이고 서로 결과가 어긋날 수 있어서, 규칙 이름과 결과를 함께 기록합니다[15]. 규칙 목록은 [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md)에 있습니다.

7. **벗겨내기 사슬을 알아봅니다.** 벗겨내기 사슬 (peeling chain) 은 한 주소에서 시작해 적은 금액을 거듭 떼어 보내고 나머지를 다음 주소로 넘기는 구조로, 믹서·세탁 서비스와 거래소가 씁니다[18]. 비트코인 전체 체인에서 이런 사슬 624,573개(거래 9,813,092건)를 골라낸 연구에서는 79.05% 가 하루 안에 만들어졌고, 떼어 낸 금액이 입력의 1% 미만인 거래가 71.19% 였습니다[18]. 사슬인지는 매개변수 하나로 판단하지 않고 거래 횟수·시간·블록 간격·떼는 금액을 함께 봅니다[18]. 거래가 2~3회인 짧은 사슬은 일반 사용자도 연달아 지불하면서 만들 수 있습니다[18]. 사슬의 거래는 출력이 둘이라 보통 사용자의 거래와 모양이 같습니다[20]. 떼어 낸 출력 하나하나가 새 갈림길이므로, 어느 출력을 먼저 따라갈지 기준을 기록해 둡니다.

8. **믹서를 만나면 체인 밖 자료로 넘어갑니다.** 믹서를 지나면 입금 주소와 지급 주소 사이에 직접 이어지는 트랜잭션이 없습니다[20]. 믹서 한 곳에 시험 거래를 보낸 연구에서 "입력 금액에서 수수료를 뺀 값" 과 같은 트랜잭션을 24시간 안에서 찾으면 2건(그중 1건이 실제 지급)이 나왔지만, 믹서가 매길 수 있는 수수료 범위 전체로 넓히면 4,453건, 0부터 최소 수수료 기준 금액까지 넓히면 461,140건이 나왔습니다[20]. 미국의 믹서 운영자 사건 세 건에서 수사기관이 시험 거래를 했지만 운영자 식별은 서버·호스팅 결제 같은 블록체인 밖 정보로 이뤄졌습니다[20]. 믹서의 구조와 코인조인 모양은 [믹서와 추적을 어렵게 하는 방법](../../01-foundations/ecosystem/mixers.md), 탈중앙 거래소·브리지로 체인을 바꾼 경우는 [탈중앙 거래소와 브리지](../../01-foundations/ecosystem/dex-bridge.md)에 있습니다.

9. **끝점을 확인합니다.** 흐름은 아직 쓰이지 않은 출력(이더리움은 잔액이 남은 주소), 거래소 같은 서비스 주소, 믹서에서 끝납니다. 거래가 수천 건인 주소는 여러 사용자가 함께 쓰는 서비스 지갑일 가능성이 있습니다[20]. 거래소로 들어갔는지 확인하는 순서는 [거래소로 들어갔나](exchange-deposit.md)에 있습니다.

10. **단계마다 근거를 기록합니다.** 홉마다 트랜잭션 ID, 출력 번호, 금액, 블록 높이, 조회한 곳과 조회 시각, 그리고 그 홉을 트랜잭션으로 이었는지 휴리스틱으로 이었는지를 적습니다. 이 기록이 있어야 보고서에서 확인한 이동과 추정한 이동을 나눌 수 있습니다. 시각을 합치는 방법은 [암호화폐 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

지갑 암호를 풀거나 복구 문구·개인 키를 꺼내는 일은 이 흐름에 넣지 않습니다.

## 증명하는 것과 증명하지 못하는 것

**증명하는 것.** 블록체인에 기록된 사실, 곧 이 트랜잭션이 어느 이전 출력을 썼고 어느 주소로 얼마를 보냈으며 어느 블록에 들어갔는지는 확인됩니다[7]. 이더리움은 트랜잭션 성공 여부와 로그의 보낸 주소·받는 주소·토큰 수량까지 확인됩니다[9][11]. 피해자 기기의 지갑 데이터에 같은 트랜잭션 해시와 주소가 있으면 "이 기기의 지갑 앱이 이 거래를 기록했다" 까지 쓸 수 있습니다[1][2].

**증명하지 못하는 것.** 블록체인만으로는 주소의 실제 소유자를 알 수 없습니다. 공통 입력 소유 휴리스틱과 잔돈 휴리스틱은 가정이고, 실제 소유자를 기록한 정답 데이터가 없어 오류율을 알 수 없습니다[18][19][23]. 블록 700,000 기준으로 네 가지 휴리스틱을 합치면 주소 8억 7,460만 개가 약 2억 5천만 묶음으로 약 70% 줄지만[19], 이 수치는 얼마나 줄었는지이지 맞게 묶였는지가 아닙니다. 묶기 결과는 단독 증거가 아니라 방향을 잡는 보조 도구로 쓰고 거래 행태와 체인 밖 자료로 보강합니다[23]. 상용 분석 서비스의 위험 점수는 데이터 출처와 방법이 공개되지 않고, 같은 주소를 한 서비스는 블랙리스트로, 다른 서비스는 26% 로 매긴 경우도 있습니다[20]. 빠져나간 트랜잭션에 누가 서명했는지도 블록체인으로는 알 수 없습니다.

## 시각 맞추기

| 값 | 기준 | 주의할 점 |
|---|---|---|
| 비트코인 블록 시각 | 채굴자가 헤더 해싱을 시작했다고 적은 UNIX 시각, UTC[5] | 앞 11개 블록 중앙값보다 크기만 하면 되고 노드는 2시간 넘게 앞선 블록만 거부합니다[5]. 그래서 블록 362941(2015-06-28 17:16:02 UTC)이 앞 블록 362940(17:18:34 UTC)보다 이른 경우가 있습니다[18] |
| Esplora `block_time` | 블록 시각, UNIX 초[7] | 확정된 트랜잭션만 값이 있고 미확정이면 `null` 입니다[7] |
| Etherscan `timeStamp` | 블록 시각, UNIX 초[11] | `getLogs` 결과는 16진 문자열입니다[14] |
| Etherscan `confirmations` | 조회 시점의 확정 수[11] | 조회할 때마다 늘어나므로 조회 시각과 함께 적습니다 |
| MetaMask `time`, Coinbase Wallet `createdAt`·`confirmedAt` | 앱이 기록한 값[1][2] | 기기 시계를 따르므로 블록 시각과 따로 적고 비교합니다 |

같은 높이에 블록 두 개가 동시에 나오면 짧은 쪽 블록은 버려지고[6], 이더리움은 체인 재구성으로 지워진 로그에 `removed: true` 가 붙습니다[9]. 그래서 보고서에는 블록 시각과 함께 조회 시점의 확정 수를 적습니다. 벗겨내기 사슬의 시간 간격은 연구마다 다릅니다. 전체 체인 연구에서는 사슬 대부분이 하루 안에 만들어졌지만[18], 믹서 시험에서는 사슬 거래 사이가 3~918블록, 4~118블록이었습니다[20]. 시간 간격만으로 사슬을 판단하지 않습니다. 블록 시각 전반은 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에 있습니다.

## 흔한 오판

- **잔돈 출력을 받는 사람으로 읽는다.** 출력 둘이 모두 지불일 수도 있어 잔돈 판단은 틀릴 수 있습니다[18]. `<1:2>` 거래가 얼마나 흔한지도 기준에 따라 다릅니다. 30일 이동 평균으로는 전체 거래의 약 75%[21], 창세기부터 2023-01-16(블록 772162)까지 전체로는 56.33% 였습니다[18].
- **입력이 여러 개면 한 사람이다.** 코인조인은 여러 사람이 한 트랜잭션의 입력을 나눠 내므로 공통 입력 소유 휴리스틱이 틀립니다[19][20]. 잔돈 주소까지 묶으면 묶음이 거대한 한 덩어리로 무너질 수 있어 BlockSci 는 기본값으로 잔돈 주소를 묶지 않습니다[16].
- **출력 주소가 곧 범인 지갑이다.** 한 트랜잭션의 출력 주소가 2021년 7월까지 1,361번 거래하고 1억 달러 넘게 주고받은 주소였던 사례가 있습니다[24]. 이런 주소는 거래소 같은 공유 지갑일 가능성이 큽니다[20].
- **xpub 조회 결과에 없으니 피해자 주소가 아니다.** 한 형식으로만 파생했거나 간격 20에서 멈췄거나 잔돈 체인을 빼먹었을 수 있습니다[3][22]. 공개 xpub 조회 도구 7개 중 6개가 xpub 에서 SegWit 주소를 자동으로 파생하지 않았습니다[22].
- **토큰이 일반 트랜잭션 목록에 없으니 옮겨지지 않았다.** 토큰 이동은 `tokentx` 와 로그에, 컨트랙트가 옮긴 ETH 는 `txlistinternal` 에 있습니다[11][12][13].
- **흐름이 끊겼다.** 도구가 새 주소 형식을 처리하지 못해 끊긴 것처럼 보일 수 있습니다. BlockSci 는 2020년 11월 이후 개발이 멈춰 WitnessUnknown 형식 주소를 문자열로 만들지 못하고[18], 2020년 이후 갱신되지 않은 주소 해석 라이브러리를 쓰는 btc-csv 는 Taproot 거래를 처리하지 못합니다[20]. 도구가 어떤 주소 형식까지 읽는지 먼저 확인합니다.
- **분석 서비스의 라벨·점수를 사실로 적는다.** 방법이 공개되지 않고 서비스마다 결과가 다릅니다[20][24]. GraphSense 의 라벨도 운영자가 TagStore 에 따로 넣은 태그 묶음(tagpack)에서 오는 외부 정보입니다[17].

## 보고서 문장 예

아래 주소·트랜잭션 ID·시각·금액은 모두 만든 예시입니다.

> 증거물 2(피해자 휴대폰)의 iOS MetaMask 데이터 `persist-root` 에 트랜잭션 해시 `0xaaaa…aaaa`(만든 예시)가 기록돼 있고, 앱이 기록한 시각은 2025-04-10 02:31:05 UTC 입니다. 이더리움 원장에서 이 트랜잭션은 블록 시각 2025-04-10 02:31:23 UTC 에 성공(`status` 1)했고, 피해자 주소 `0x1111…1111`(만든 예시)에서 `0x2222…2222`(만든 예시)로 1.2 ETH 를 옮겼습니다. `0x2222…2222` 는 같은 날 02:40:11 UTC 에 트랜잭션 `0xbbbb…bbbb`(만든 예시)로 1.19 ETH 를 `0x3333…3333`(만든 예시)으로 보냈습니다. 원장은 자체 노드로 2025-06-01 UTC 에 조회했습니다.

추정은 방법과 가정을 함께 씁니다.

> 비트코인 트랜잭션 `9f3c…e1`(만든 예시)의 출력 두 개 가운데 출력 1은 입력과 주소 형식이 같고 금액이 어떤 입력보다 작아, 잔돈 판단 규칙(주소 형식 일치·최적 잔돈)을 적용하면 보낸 사람의 잔돈일 가능성이 있습니다. 이 판단은 블록체인 기록이 아니라 추정입니다.

"A 에서 B 로 갔다" 는 트랜잭션으로 곧바로 이어질 때만 쓰고, 묶기·잔돈 판단·금액 일치로 이은 부분은 "가능성이 있다" 로 씁니다. 보고서 형식은 [암호화폐 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)에 있습니다.

## 함께 볼 페이지

- [거래소로 들어갔나](exchange-deposit.md) — 흐름이 거래소에 닿았을 때 계정 주인을 확인합니다.
- [피싱 사이트에 서명했나](../fraud/wallet-drainer.md) — 서명으로 권한을 넘긴 뒤 자산이 빠져나간 사건입니다.
- [악성 코드가 지갑을 노렸나](../device-use/wallet-stealer.md) — 지갑 파일이 유출된 뒤 자산이 빠져나간 사건입니다.
- [투자 사기의 흔적](../fraud/investment-scam.md) — 피해자가 직접 보낸 돈을 따라가는 사건입니다.
- [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md) — 묶기 규칙과 보고서에 쓸 수 있는 범위입니다.
- [거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md) — 흐름의 끝에서 만나는 서비스입니다.

## 참고 문헌

1. iLEAPP, `scripts/artifacts/metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
2. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
3. BIP-0044, Multi-Account Hierarchy for Deterministic Wallets. https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
4. Bitcoin Developer Guide, Transactions. https://developer.bitcoin.org/devguide/transactions.html
5. Bitcoin Developer Reference, Block Chain. https://developer.bitcoin.org/reference/block_chain.html
6. Bitcoin Developer Guide, Block Chain. https://developer.bitcoin.org/devguide/block_chain.html
7. Blockstream, Esplora HTTP API. https://github.com/Blockstream/esplora/blob/master/API.md
8. ethereum.org, Transactions. https://ethereum.org/en/developers/docs/transactions/
9. ethereum.org, JSON-RPC API. https://ethereum.org/en/developers/docs/apis/json-rpc/
10. ethereum.org, ERC-20 Token Standard. https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/standards/tokens/erc-20/index.md
11. Etherscan, Get Normal Transactions By Address (`txlist`). https://docs.etherscan.io/api-reference/endpoint/txlist.md
12. Etherscan, Get Internal Transactions by Address (`txlistinternal`). https://docs.etherscan.io/api-reference/endpoint/txlistinternal.md
13. Etherscan, Get ERC20 Token Transfers by Address (`tokentx`). https://docs.etherscan.io/api-reference/endpoint/tokentx.md
14. Etherscan, Get Event Logs (`getLogs`). https://docs.etherscan.io/api-reference/endpoint/getlogs.md
15. BlockSci, `docs/reference/heuristics/change.rst`. https://github.com/citp/BlockSci/blob/master/docs/reference/heuristics/change.rst
16. BlockSci, `docs/reference/clustering/cluster_manager.rst`. https://github.com/citp/BlockSci/blob/master/docs/reference/clustering/cluster_manager.rst
17. GraphSense, graphsense-lib `README.md`. https://github.com/graphsense/graphsense-lib/blob/master/README.md
18. Yanan Gong, Kam Pui Chow, Siu Ming Yiu, Hing Fung Ting, "Analyzing the peeling chain patterns on the Bitcoin blockchain", Forensic Science International: Digital Investigation 46, 2023. doi:10.1016/j.fsidi.2023.301614
19. Hugo Schnoering, Pierre Porthaux, Michalis Vazirgiannis, "Assessing the Efficacy of Heuristic-Based Address Clustering for Bitcoin", arXiv, 2024. doi:10.48550/arXiv.2403.00523
20. Pascal Tippe, Christoph Deckers, "Unmixing the mix: Patterns and challenges in Bitcoin mixer investigations", Forensic Science International: Digital Investigation 52, 2025. doi:10.1016/j.fsidi.2025.301876
21. Jan Zavřel, Michal Koutenský, Daniel Dolejška, Vladimír Veselý, "Tumbling down the stairs: Exploiting a tumbler's attempt to hide with ordinary-looking transactions using wallet fingerprinting", Forensic Science International: Digital Investigation 52, 2025. doi:10.1016/j.fsidi.2025.301869
22. Tyler Thomas, Tiffanie Edwards, Ibrahim Baggili, "BlockQuery: Toward forensically sound cryptocurrency investigation", Forensic Science International: Digital Investigation 40, 2022. doi:10.1016/j.fsidi.2022.301340
23. Yanan Gong, Kam Pui Chow, Siu Ming Yiu, "Improved Bitcoin simulation model and address heuristic method", Forensic Science International: Digital Investigation 53, 2025. doi:10.1016/j.fsidi.2025.301935
24. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, "Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications", arXiv, 2022. doi:10.48550/arXiv.2205.14611
