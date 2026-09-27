---
title: "거래소로 들어갔나"
parent: "시나리오 · 자산 흐름"
nav_order: 360
---

# 거래소로 들어갔나 (Exchange Deposit)

추적하던 자금이 거래소로 들어갔는지 확인하고, 들어갔다면 어느 거래소의 어느 계정 앞으로 들어갔는지까지 잇는 순서를 다룹니다. 블록체인에는 주소와 금액만 남아서, 받는 주소가 거래소 것인지와 그 주소가 누구 계정에 딸려 있는지는 체인만으로 확정할 수 없습니다. 그래서 기기 흔적과 트랜잭션 모양으로 후보를 좁히고, 확정은 거래소가 낸 회신 자료와 한 행씩 맞춰서 합니다.

## 조사 질문

- 추적하던 트랜잭션의 받는 주소가 거래소가 고객에게 내준 입금 주소인가, 아니면 개인 지갑이나 다른 서비스의 주소인가.
- 입금 주소라면 어느 사업자(법인)의 어느 계정 앞으로 들어갔고, 그 계정의 명의자는 누구인가.
- 입금 뒤 그 계정에서 자금이 어디로 나갔는가.
- 기기 기록, 블록체인 기록, 거래소 기록의 금액·주소·시각이 서로 맞는가.

## 먼저 확인할 것

출발점이 되는 값부터 한 표로 정리합니다. 트랜잭션 ID (TXID), 보낸 주소, 받는 주소, 체인과 네트워크, 금액, 그리고 그 값이 어디서 나왔는지(피해자 신고, 압수한 기기의 지갑 데이터, 앞 단계의 추적)를 적습니다. 거래소 회신에도 주소와 거래마다 네트워크 열(`NETWORK`, `network`)이 따로 있어서[4][5], 처음부터 체인과 네트워크를 함께 적어 두어야 나중에 행을 맞출 수 있습니다. 추적이 피해자 지갑에서 시작한다면 거래소 앞까지 오는 과정은 [빼앗긴 자산은 어디로 갔나](stolen-funds.md)에서 다룹니다.

시각의 기준도 정리합니다. 기기의 지갑 앱은 기기 시계로, 블록체인은 블록 시각으로, 거래소는 거래소 서버 시각으로 기록해서 세 값은 기준이 다릅니다. 거래소에 기록을 요청할 때 UTC 로 시각을 적으라고 하는 곳이 있으므로[8], 조사 표의 시각도 처음부터 UTC 로 바꾸고 원래 값을 옆에 남깁니다.

거래 시점과 보존 기간을 비교합니다. 국내 사업자의 고객확인 자료와 트래블룰 정보는 5년, 가상자산거래기록은 15년 보존 대상이고([거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md)), 업비트의 로그인 기록 보유 기간은 3개월 이상입니다[9]. 요청이 늦으면 거래 기록은 남아 있어도 접속 기록은 없을 수 있습니다.

마지막으로 주소를 어떻게 조회할지 정합니다. 제3자 블록 탐색기에 주소나 TXID 를 넣으면 무엇을 조사하는지가 그 운영자에게 드러날 수 있어서, 수사 중인 사건은 자체 노드나 로컬 조회 도구를 먼저 검토합니다([블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 기기 지갑의 보낸 거래·주소록 | 보낸 TXID, 받는 주소, 사용자가 주소에 붙인 이름 | [MetaMask](../../02-artifacts/browser/metamask/index.md), [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md), [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md), [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md), [Electrum](../../02-artifacts/desktop/electrum.md) |
| 2 | 기기의 거래소 앱 | 거래소 계정 식별자, 통화별 잔액 캐시 | [거래소 앱](../../02-artifacts/mobile/exchange-apps.md) |
| 3 | 트랜잭션 조회 결과 | 받는 주소, 금액, 블록 시각, 성공 여부 | [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md), [비트코인 거래 따라가기](../../03-techniques/analysis/bitcoin-tracing.md), [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md) |
| 4 | 받는 주소 이후의 트랜잭션 | 입금 주소처럼 다른 입금과 함께 한 주소로 모였는지 | [거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md), [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md) |
| 5 | 탐색기·분석 도구의 주소 라벨 | 운영자가 붙인 거래소 이름(블록체인 밖 정보) | [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md) |
| 6 | 거래소 회신 자료 | 계정 명의, 계정에 딸린 입금 주소, 입출금 행, 접속 기록 | [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md), [거래소 자료 분석](../../03-techniques/analysis/exchange-analysis.md) |
| 7 | 사업자 간 이전의 트래블룰 정보 | 보내는 고객과 받는 고객의 성명·가상자산주소 | [거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md) |

## 분석 흐름

1. **기기에서 보낸 거래와 상대 주소를 모읍니다.** iOS MetaMask 에서 iLEAPP 는 `TransactionController.transactions` 의 항목마다 `time`, `transaction.from`, `transaction.to`, `transaction.value`, `transactionHash` 를 읽고, 주소록은 `AddressBookController.addressBook` 아래 체인 ID 별 항목의 `name`·`address` 를 읽습니다[1]. iOS Coinbase Wallet 의 `Documents/default/wallet-rn-v2.sqlite` 에서는 `tx_history_v2` 의 `toAddress`, `toDomain`, `txHash` 를 봅니다. `toDomain` 은 앱이 받는 주소를 이름으로 풀어 낸 값이 들어가는 열이고[2], 보낸 거래 행에 어떤 값이 들어가는지는 공개된 자료가 없어서 실제 데이터로 확인합니다. 저장 위치와 구조는 위 표 1번 행의 아티팩트 페이지에 있습니다.

   이더리움 토큰을 거래소로 보냈다면 트랜잭션의 `to` 는 받는 사람이 아니라 토큰 컨트랙트입니다. 받는 사람은 입력 데이터와 `Transfer` 로그에 있으므로, `to`·`value` 만 보여 주는 결과표에서는 받는 주소가 컨트랙트로, 금액이 0 으로 보일 수 있습니다([토큰과 NFT](../../01-foundations/blockchain/tokens.md), [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md)).

2. **트랜잭션을 조회해 받는 주소와 금액을 확정합니다.** 기기에서 나온 TXID 로 트랜잭션을 조회해 받는 주소, 금액, 블록 높이, 블록 시각, 성공 여부를 기기 기록 옆에 적습니다. 기기 기록과 체인 기록이 다르면 체인 값을 기준으로 삼고 차이를 따로 적습니다.

3. **받는 주소가 입금 주소처럼 움직였는지 봅니다.** 거래소·도박·마켓 같은 서비스는 고객마다 전용 입금 주소를 만들고, 들어온 돈을 주기적으로 핫월렛(hot wallet)이나 콜드월렛(cold wallet)으로 옮깁니다[10]. 수수료를 아끼려고 여러 입금 주소의 돈을 입력 여러 개·출력 1개인 트랜잭션 하나로 옮기고, 서비스 하나가 이런 주소를 수천 개, 큰 곳은 수백만 개 관리합니다[10]. 그래서 받는 주소의 돈이 입력이 많고 출력이 하나인 트랜잭션으로 빠져나갔다면 서비스 입금 주소일 가능성이 있습니다. 이 모양으로 입금 주소를 묶는 방법은 입력 주소들이 같은 주체라고 보는 공통 입력 휴리스틱 (common-input-ownership heuristic)의 특수한 경우라서, 입력 주소들이 한 서비스에 속한다는 것만 알려 주고 어느 서비스인지는 알려 주지 않습니다[10]. 이 방법을 시험한 연구는 입력 25개 이상·출력 1개를 기준으로 삼았습니다[10]. 비트코인에서 모으기·일괄 지급 트랜잭션의 모양은 [거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md)에, 이더리움 입금 주소가 본 주소로 돈을 넘기는 모양은 [거래소 자료 분석](../../03-techniques/analysis/exchange-analysis.md)에 있습니다.

4. **라벨을 확인하고, 누가 붙였는지 함께 적습니다.** 탐색기가 주소 옆에 보여 주는 거래소 이름은 운영자가 붙인 라벨입니다. Etherscan 의 주소 메타데이터 API(`getaddresstag`)는 Pro Plus 요금제에서만 쓸 수 있고 초당 2회로 제한되며, 응답에 `address`, `nametag`, `internal_nametag`, `url`, `shortdescription`, `notes_1`, `notes_2`, `labels`, `labels_slug`, `reputation`, `other_attributes`, `lastupdatedtimestamp`(Unix 초) 필드가 있습니다[6]. 같은 데이터셋이 Etherscan 계열 탐색기의 주소 태그에 쓰이고 계속 갱신됩니다[7]. 라벨은 바뀔 수 있으므로 응답 원본을 조회 시각(UTC)과 함께 저장합니다. 상용 추적 도구가 트랜잭션의 출처를 거래소로 표시해도 판정 근거를 보여 주지 않는 경우가 있어서[13], 라벨과 도구 표시는 요청할 거래소를 정하는 단서로만 씁니다.

5. **요청할 법인을 정합니다.** 같은 상표라도 법인이 다르면 기록을 가진 회사가 다릅니다. Binance.US 를 운영하는 BAM Trading Services 는 Binance Holdings 와 다른 회사라 Binance 의 기록이 없고, Binance.US Web3 Wallet 기록은 BAM Technology Services Inc. 앞으로 따로 요청합니다[8]. 국내 사업자가 신고된 사업자인지는 금융정보분석원 공개 목록으로 확인합니다([거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md)).

6. **요청서에 체인 기록을 붙입니다.** Binance.US 에 트랜잭션 해시로 요청할 때는 금액, 입력·출력 주소, UTC 시각을 적고, 지갑 주소로 요청할 때는 TXID, UTC 시각, 금액을 적습니다[8]. 계정의 자금이 몰수 대상이라고 믿을 근거가 있으면 동결 요청을 따로 보낼 수 있고, Binance.US 는 검토 뒤 계정을 2주 동안 동결할 수 있습니다[8]. 국내 거래소는 입금과 관련해 고객에게서 받는 자료가 있어서 요청 항목을 정할 때 참고합니다. 업비트는 입금신청 때 TXID·송금 거래소 이름·송금 거래소의 회원정보와 출금 내역 화면을, 자금출처 확인 때 입금일시·자산 종류·입금 TXID·자산의 출처·입금 사유를, 반환 신청 때 TXID 와 from 지갑주소를 받습니다[9]. 금융사기로 거래가 정지된 계정의 정지를 풀 때는 피해금 이동 경로가 확인되는 입출금 내역도 받습니다[9].

7. **회신과 체인 기록을 한 행씩 맞춥니다.** 입금은 체인에서 본 받는 주소가 회신의 계정 주소 목록에 있는지로 확인합니다. Coinbase 보고서의 주소 섹션에는 `CREATED`, `ACCOUNT`, `NETWORK`, `ADDRESS`, `LABEL`, `CALLBACK URL` 열이 있고, 거래 섹션에는 `TRANSACTION HASH`·`TO`·`AMOUNT`·`CURRENCY`·`NETWORK` 열이 있습니다[4]. Robinhood 의 전송 파일에는 `blockchain_txn_id`, `to_address`, `network` 가 있지만 계좌번호는 없어서[5], 어느 계정의 기록인지는 회신 묶음으로 확인합니다. 회신 파일의 중복 확인, 빠진 열 확인, 행 대조 방법은 [거래소 자료 분석](../../03-techniques/analysis/exchange-analysis.md)에 있습니다.

8. **입금 뒤 흐름을 이어 갑니다.** 계정에서 나간 출금은 회신의 출금 행(해시·상대 주소)으로 찾습니다. 거래소는 여러 고객의 출금을 입력 1개·출력 여러 개인 트랜잭션 하나로 한꺼번에 처리하기도 하므로[11], 출금 트랜잭션의 다른 출력은 그 계정과 관계없는 고객의 출금일 수 있습니다. 출금 상대 주소가 다른 거래소의 입금 주소처럼 보이면 3단계부터 다시 밟습니다.

9. **세 기록의 시각을 한 표에 합칩니다.** 기기 시각, 블록 시각, 거래소 시각을 UTC 로 맞추고 원래 값을 함께 둡니다([암호화폐 타임라인](../../03-techniques/analysis/timeline.md)).

> 그림 자리: 기기의 보낸 거래(TXID·받는 주소) → 체인 조회(금액·블록 시각) → 입금 주소에서 모으기 트랜잭션으로 빠져나간 흐름 → 라벨로 거래소 후보 → 거래소 회신의 주소 목록·거래 행과 대조 → 계정 명의로 이어지는 순서

## 증명하는 것과 증명하지 못하는 것

**증명하는 것.** 블록체인으로는 이 주소에서 이 주소로 이 금액을 보낸 트랜잭션이 이 블록에 들어 있다는 사실을 확인합니다. 체인에서 본 받는 주소가 거래소 회신의 계정 주소 목록에 있거나, 회신의 거래 행에 같은 TXID 가 있으면 "이 거래소가 이 계정에 이 TXID 의 입금을 기록했다" 고 쓸 수 있습니다[4][5][8]. 규제받는 거래소와 거래한 주소는 그 거래소가 보관한 신원 정보가 신원을 찾는 출발점이 됩니다[12].

**증명하지 못하는 것.** 블록체인만으로는 받는 주소가 거래소 것인지 알 수 없습니다. 탐색기 라벨은 운영자가 붙이고 갱신하는 블록체인 밖 정보이고[6][7], 상용 도구는 판정 근거를 보여 주지 않는 경우가 있습니다[13]. 입력이 많고 출력이 하나인 모양은 입금 주소들이 같은 서비스라는 추정일 뿐 어느 서비스인지는 알려 주지 않고[10], 한 사람이 자기 주소 여러 개의 돈을 모을 때도 같은 모양이 나옵니다[11]. 핫월렛이나 모으기 주소처럼 여러 고객의 돈이 지나가는 주소는 한 사람의 것이 아닙니다[12][13]. 기기 주소록에 적힌 거래소 이름은 사용자가 붙인 이름이라[1] 그 주소가 거래소 것이라는 근거가 되지 않습니다. 트래블룰 정보는 사업자 간 이전에만 있고 개인 지갑과의 이전에는 없습니다[14][15].

## 시각 맞추기

체인 쪽 시각은 트랜잭션이 들어간 블록의 시각이고, 비트코인에서는 채굴자가 헤더에 적은 값이라 앞 블록보다 이를 수도 있습니다([블록 시각과 확정](../../01-foundations/blockchain/block-time.md)). 거래소 기록의 시각은 거래소 시스템이 남긴 값이라 블록 시각과 같다는 보장이 없습니다. 같은 TXID 로 짝을 지은 뒤 두 시각이 다르면 둘 다 적고, 시각만으로 행을 짝짓지 않습니다.

거래소 회신 안에서도 시간대 표기가 섞입니다. RLEAPP 의 Coinbase 보고서 분석기는 `-0800`·`Z` 같은 오프셋이나 시간대 약어가 적힌 값만 UTC 로 바꾸고, 약어는 적힌 그대로 고정 오프셋(PST = UTC-8)으로 읽으며, 시간대가 없는 값은 바꾸지 않습니다[4]. Robinhood 주문 파일의 `Time Entered` 는 시간대가 적혀 있지 않아 RLEAPP 도 변환하지 않습니다[5]. 표기별 예와 도구마다 다른 가정은 [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md)에 있습니다.

## 흔한 오판

- **탐색기 라벨을 계정 소유의 근거로 쓰는 것.** "Exchange" 라벨은 그 주소를 거래소가 관리한다는 운영자의 판단이지, 피의자가 그 거래소 회원이라는 기록이 아닙니다. 라벨에는 갱신 시각 필드가 있어 조회 시점마다 달라질 수 있습니다[6].
- **핫월렛·모으기 주소를 입금 주소로 읽는 것.** 거래소는 고객별 입금 주소와, 그 돈을 모아 두는 핫월렛·콜드월렛을 따로 씁니다[10]. 모으기 트랜잭션 뒤의 주소로는 특정 고객을 가리킬 수 없습니다.
- **거래소에서 나온 돈을 그 계정 주인의 돈으로 보는 것.** 한 믹서는 이용자에게 돌려줄 비트코인을 자금세탁 방지 (AML) 분석 서비스 두 곳이 HTX 거래소로 표시한 주소에서 보냈고, 여러 주소가 한 트랜잭션으로 보낸 모양은 믹서가 아니라 거래소가 고객에게 지급하는 모양일 가능성이 높았습니다[12]. 거래소 주소에서 나온 돈은 그 거래소의 어느 계정에서 나갔는지 회신으로 확인합니다.
- **같은 상표의 다른 법인에 요청하는 것.** Binance.US 는 Binance 의 기록이 없고, 기록이 없으면 "no records" 로 답하며, 요청받은 사실을 이용자에게 알리지 않습니다[8]. "no records" 는 그 법인에 기록이 없다는 뜻일 뿐입니다.
- **거래소 앱에서 입금 내역을 찾는 것.** iOS Coinbase 앱을 읽는 iLEAPP 분석기는 MMKV 파일(`CB_RRN_MMKV_STORAGE`)에서 계정 식별자·로그인 상태·앱 버전 같은 계정 정보와 지갑별 잔액만 내놓습니다[3]. 입금 주소와 입금 내역은 거래소 회신으로 확인합니다([거래소 앱](../../02-artifacts/mobile/exchange-apps.md)).
- **개인 지갑으로의 이전이나 소액 이전에서 트래블룰 정보를 기대하는 것.** 트래블룰은 사업자 간 이전에 적용되고 개인 지갑 사전 등록제는 업계 자율입니다[14]. 2027년 2월 18일까지는 100만 원 이상에 상당하는 사업자 간 이전에만 정보를 넘기므로[15], 그보다 적은 이전에는 정보가 없을 수 있습니다. 2027년 2월 19일부터의 이전은 그때 시행 중인 조문으로 판단합니다([거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md)).
- **시간대가 없는 거래소 시각을 UTC 로 가정하는 것.** 도구마다 가정이 다르므로 원래 값과 변환 근거를 함께 봅니다[4][5].

## 보고서 문장 예

아래 주소·해시·시각·계정 번호는 모두 만든 예시입니다.

- 체인만 확인한 경우: "피해자 휴대전화의 MetaMask 데이터에 트랜잭션 0x5a1c…e07b 가 있고, 이 트랜잭션은 이더리움 블록 21,000,000(블록 시각 2025-04-02 06:31:11 UTC)에 성공 상태로 들어 있으며, 주소 0x3f2a…91cd 로 1.2 ETH 를 보냈다. 이 주소의 잔액은 17분 뒤 다른 주소로 옮겨졌다. Etherscan 주소 메타데이터 API 는 2025-04-10 02:00 UTC 조회 때 이 주소에 라벨을 붙이지 않았다."
- 입금 주소 모양만 확인한 경우: "주소 bc1q…7h2k 가 받은 0.4 BTC 는 입력 38개·출력 1개인 트랜잭션 9c3e…a410 으로 다른 입금과 함께 한 주소로 옮겨졌다. 이 모양은 서비스가 여러 입금 주소의 돈을 모으는 모양과 같지만, 어느 서비스인지와 계정 명의자는 이 기록만으로 알 수 없다."
- 거래소 회신까지 확인한 경우: "○○ 거래소 회신(파일 SHA-256 7d41…c0e2)의 주소 섹션에 주소 bc1q…7h2k 가 계정 U-2041 의 BTC 주소로 2024-11-03 에 생성되었다고 기록되어 있고, 같은 회신의 거래 섹션에 이 계정이 트랜잭션 4be0…19fa 로 0.4 BTC 를 받은 행이 있다. 이 트랜잭션은 비트코인 블록 880,000 에 들어 있고 블록 시각은 2025-01-20 08:14:55 UTC 이며, 회신의 시각은 UTC 로 바꾸면 08:31:02 로 16분 7초 늦다."

## 함께 볼 페이지

- [빼앗긴 자산은 어디로 갔나](stolen-funds.md) — 거래소 앞까지 자금을 따라가는 순서
- [거래소 자료 분석](../../03-techniques/analysis/exchange-analysis.md) — 회신 자료 보존·파싱·체인 대조 절차
- [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md) — 회신 파일의 섹션·열·시각 표기
- [거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md) — 보존 기간, 트래블룰, 모으기·일괄 지급 트랜잭션
- [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md) — 입금 주소 휴리스틱과 오류
- [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md) — 조회 기밀과 라벨
- [투자 사기의 흔적](../fraud/investment-scam.md), [피싱 사이트에 서명했나](../fraud/wallet-drainer.md) — 피해금이 거래소로 들어가는 사건
- [암호화폐 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)

## 참고 문헌

1. iLEAPP, `scripts/artifacts/metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
2. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
3. iLEAPP, `scripts/artifacts/coinbase.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbase.py
4. RLEAPP, `scripts/artifacts/coinbaseComplianceReport.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseComplianceReport.py
5. RLEAPP, `scripts/artifacts/robinhoodReturns.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/robinhoodReturns.py
6. Etherscan, "Get Metadata for an Address" (`getaddresstag`). https://docs.etherscan.io/api-reference/endpoint/getaddresstag.md
7. Etherscan, "Etherscan Metadata: Introduction". https://docs.etherscan.io/metadata/introduction.md
8. Binance.US, "Binance.US law enforcement guide". https://support.binance.us/en/articles/9842980-binance-us-law-enforcement-guide
9. 두나무, "업비트 개인정보 처리방침" V2.56 (2026-07-31 적용). https://static.upbit.com/terms/private_data.html
10. Hugo Schnoering, Pierre Porthaux, Michalis Vazirgiannis, "Assessing the Efficacy of Heuristic-Based Address Clustering for Bitcoin", arXiv, 2024. doi:10.48550/arXiv.2403.00523
11. Jan Zavřel, Michal Koutenský, Daniel Dolejška, Vladimír Veselý, "Tumbling down the stairs: Exploiting a tumbler's attempt to hide with ordinary-looking transactions using wallet fingerprinting", Forensic Science International: Digital Investigation 52, 2025. doi:10.1016/j.fsidi.2025.301869
12. Pascal Tippe, Christoph Deckers, "Unmixing the mix: Patterns and challenges in Bitcoin mixer investigations", Forensic Science International: Digital Investigation 52, 2025. doi:10.1016/j.fsidi.2025.301876
13. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, "Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications", arXiv, 2022. doi:10.48550/arXiv.2205.14611
14. 금융위원회 보도자료, "3.25일 특정금융정보법상 트래블룰이 시행됩니다", 2022-03-24. https://www.fsc.go.kr/no010101/77579
15. 특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령 (대통령령 제36592호, 2026. 8. 20. 시행 본문과 부칙). https://www.law.go.kr/법령/특정금융거래정보의보고및이용등에관한법률시행령
