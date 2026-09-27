---
title: "이더리움 거래 따라가기"
parent: "기법 · 분석"
nav_order: 300
---

# 이더리움 거래 따라가기 (Ethereum Tracing)

이더리움은 입력과 출력을 잇는 방식이 아니라 계정끼리 주고받는 방식이라, 자산을 따라가려면 한 주소의 일반 트랜잭션, 컨트랙트 안에서 생긴 내부 이동, 토큰 이벤트 로그를 따로 모아 한 표로 합쳐야 합니다. 이 페이지는 기기나 거래소 자료에서 찾은 주소·트랜잭션 해시에서 시작해 이동을 한 건씩 확인하고 다음 주소로 넘어가는 절차, 그리고 그 결과를 증거로 읽을 때 넘지 말아야 할 선을 다룹니다. 계정·영수증·로그의 필드 구조는 [이더리움의 계정과 로그](../../01-foundations/blockchain/ethereum-accounts.md), 토큰 이벤트의 모양은 [토큰과 NFT](../../01-foundations/blockchain/tokens.md)에서 다룹니다.

## 언제 쓰나

지갑 앱 데이터나 거래소 자료에서 이더리움 계열 주소나 트랜잭션 해시가 나왔고, 그 자산이 어디서 왔고 어디로 갔는지 확인해야 할 때 씁니다. 빼앗긴 자산의 행방을 찾는 조사, 피의자 주소에서 거래소 입금 주소까지 이어지는지 확인하는 조사, 기기의 거래 기록이 실제로 체인에 반영됐는지 대조하는 조사가 여기에 해당합니다.

이더리움 계정의 필드는 순번(`nonce`)·잔액(`balance`)·`codeHash`·`storageRoot` 네 가지이고, 계정별 거래 목록을 담는 필드는 없습니다[3]. 그래서 이동 내역은 트랜잭션·영수증·로그를 모아 다시 만듭니다. 비트코인의 출력 단위 추적은 [비트코인 거래 따라가기](bitcoin-tracing.md), 여러 주소를 한 사람으로 묶는 판단은 [주소 묶기와 그 한계](clustering.md)에서 다룹니다.

## 절차

### 1. 체인과 시작점을 확정합니다

시작점은 트랜잭션 해시나 주소 하나입니다. 먼저 어느 체인의 값인지 정합니다. 같은 주소 형식을 이더리움 메인넷과 다른 EVM 호환 체인이 함께 쓰고, Etherscan API v2 는 `chainid`(1 은 이더리움, 42161 은 Arbitrum)로 여러 체인을 한 API 에서 조회합니다[9]. MetaMask 트랜잭션 기록에도 `chainId` 필드가 있어서[14] 기기 기록에서 시작했다면 이 값으로 체인을 정합니다. 체인을 정하지 않고 주소만으로 조회하면 다른 체인의 무관한 기록이 섞일 수 있습니다.

주소는 대소문자를 섞은 EIP-55 표기, 모두 소문자, 로그 토픽 안의 0 채운 값처럼 여러 모양으로 나옵니다. 비교하기 전에 모두 소문자 헥스 40자로 맞춥니다. 표기 규칙은 [주소 형식](../../01-foundations/wallets/address-formats.md)에서 다룹니다.

### 2. 시작 트랜잭션 한 건을 확인합니다

트랜잭션 해시로 `eth_getTransactionByHash` 와 `eth_getTransactionReceipt` 를 조회합니다[2]. 확인할 값은 다음 순서입니다.

- `blockNumber` 가 null 이면 아직 블록에 들어가지 않은 대기 트랜잭션이고, 영수증도 없습니다[2].
- 영수증 `status` 가 `1` 이면 성공, `0` 이면 실패입니다[2]. 실패한 트랜잭션도 블록에 들어가고, 실패했으면 ETH 와 토큰은 옮겨지지 않았다고 보고 수수료만 따로 계산합니다.
- `to` 가 null 이면 컨트랙트를 배포한 트랜잭션이고, 새 주소는 영수증 `contractAddress` 에 나옵니다[1][2].
- `to` 가 컨트랙트면 `input` 앞 4바이트 함수 선택자로 무엇을 호출했는지 봅니다[1]. 토큰 전송이면 `to` 는 토큰 컨트랙트이고, 실제 받는 사람과 금액은 로그에 있습니다.
- 영수증 `logs` 에서 토큰 이벤트를 풉니다. 푸는 방법은 [토큰과 NFT](../../01-foundations/blockchain/tokens.md)에 있습니다.

이 한 건이 "누가 누구에게 무엇을 얼마나" 옮겼는지 정리되면 그 이동의 받는 주소가 다음 조사 대상이 됩니다.

### 3. 주소 하나의 이동을 빠짐없이 모읍니다

주소 하나의 이동은 목록 여러 개로 흩어져 있습니다. Etherscan 을 쓰면 아래 목록을 모두 받습니다.

| 목록 | 담긴 이동 | 조회 |
|---|---|---|
| 일반 트랜잭션 | EOA 가 서명해 보낸 트랜잭션과 그 `value`(ETH) | `txlist`[9] |
| 내부 이동 | 컨트랙트 실행 중 생긴 호출과 ETH 이동. `type` 은 `call`·`create`·`create2`·`self-destruct` 같은 값 | `txlistinternal`[10] |
| ERC-20 전송 | 토큰 `Transfer` 이벤트 | `tokentx`[11] |
| ERC-721 전송 | NFT `Transfer` 이벤트, 금액 대신 `tokenID` | `tokennfttx`[12] |
| 그 밖의 이벤트 | ERC-1155 의 `TransferSingle`·`TransferBatch` 처럼 위 목록에 없는 이벤트 | `getLogs`, 로그를 낸 컨트랙트 주소로 조회[13] |

컨트랙트가 실행 중에 보낸 ETH 는 내부 이동 목록으로 따로 받습니다[10]. `getLogs` 는 조사 대상 주소가 아니라 로그를 낸 컨트랙트 주소와 블록 범위를 넣어 조회하므로[13], 조사 대상 주소가 관여한 토큰 컨트랙트를 먼저 정하고 그 컨트랙트의 로그에서 대상 주소가 든 것을 골라냅니다. 이더리움 JSON-RPC 표준 메서드에는 내부 이동을 나열하는 메서드가 없어서[2], 노드만 쓴다면 실행 추적을 지원하는 노드와 도구가 따로 필요합니다. ERC-1155 이벤트는 서명이 `TransferSingle(address,address,address,uint256,uint256)`·`TransferBatch(address,address,address,uint256[],uint256[])` 로 `Transfer` 와 달라서[6], ERC-20·ERC-721 전송 목록이나 `Transfer` 서명 해시로 거른 로그에는 나오지 않습니다. 두 이벤트 모두 `_operator`·`_from`·`_to` 를 색인하므로[6] 토픽이 네 개이고, 조사 대상 주소는 `topics[2]`(보낸 쪽)나 `topics[3]`(받는 쪽) 자리에 들어갑니다.

목록은 `page`·`offset` 으로 나뉘고 `startblock`·`endblock` 으로 범위를 정합니다[9]. 첫 페이지만 받으면 이동이 빠지므로 결과가 끝날 때까지 받거나, 블록 범위를 나눠 받습니다.

보낸 트랜잭션이 빠지지 않았는지는 nonce 로 확인합니다. EOA 의 nonce 는 그 계정이 보낸 트랜잭션 수라서[3], 조사 기준 블록에서 `eth_getTransactionCount` 로 얻은 값이 N 이면[2] 그 주소가 보낸 트랜잭션의 nonce 는 0 부터 N−1 까지 빈 번호 없이 있어야 합니다. 목록에 빈 번호가 있으면 받은 목록이 모자란 것입니다.

### 4. 이동을 한 표로 합칩니다

목록마다 필드와 표기가 달라서 그대로 이어 붙이면 틀립니다. 이동 한 건을 한 행으로 두고 아래 열을 맞춥니다.

| 열 | 채우는 값 | 맞출 점 |
|---|---|---|
| 체인 | `chainid` | 1단계에서 정한 값 |
| 블록 번호·블록 시각 | `blockNumber`, `timeStamp` | Etherscan `txlist` 는 10진, `getLogs` 는 16진 문자열이고[9][13], JSON-RPC 수량 값은 `0x` 로 시작하는 16진입니다[2] |
| 트랜잭션 해시 | `hash` | 한 트랜잭션에 이동이 여러 건일 수 있음 |
| 위치 | 로그는 `logIndex`(블록 안 위치), 내부 이동은 `traceId`(트랜잭션 실행 추적 안 위치) | 트랜잭션 해시와 함께 한 건을 특정하는 값[2][10][13] |
| 자산 | ETH, 또는 토큰 컨트랙트 주소 | 토큰은 이름·심볼이 아니라 컨트랙트 주소로 적음 |
| 보낸 주소·받는 주소 | 소문자로 맞춘 주소 | 토큰은 트랜잭션 `from`·`to` 가 아니라 이벤트의 보낸 쪽·받는 쪽 |
| 금액 | 원래 정수와 환산한 값을 함께 | ETH 는 wei(10^18 으로 나눔)[3], 토큰은 `value / 10^tokenDecimal`[11] |
| 결과 | 영수증 `status`, 내부 이동 `isError` | 실패한 이동은 표에 남기되 금액 합계에서 뺌 |

같은 이동이 두 목록에 함께 나올 수 있어서, 트랜잭션 해시와 위치 값을 묶어 중복을 지웁니다.

> 그림 자리: 주소 A 의 txlist·txlistinternal·tokentx·getLogs 결과가 한 표로 합쳐지고, 받는 주소 B·C 로 가지가 뻗는 흐름도

### 5. 금액을 수수료까지 맞춥니다

보낸 계정의 ETH 는 `value` 에 수수료를 더한 만큼 줄어듭니다. 수수료는 영수증의 `gasUsed` 에 가스 단위당 낸 값 `effectiveGasPrice`(기본 수수료 + 우선 수수료)를 곱해 계산합니다[2]. 단순 송금은 가스 21000 을 쓰고, 기본 수수료 190 gwei 에 우선 수수료 10 gwei 면 수수료는 (190 + 10) × 21000 = 4,200,000 gwei, 곧 0.0042 ETH 입니다[1]. 이 가운데 기본 수수료는 소각되고 우선 수수료만 검증자가 받습니다[1]. 이 예에서 1 ETH 를 보냈다면 보낸 계정은 1.0042 ETH 가 줄어듭니다[1].

실패한 트랜잭션도 수수료를 계산합니다. 금액이 맞지 않으면 빠진 내부 이동이나 토큰 이동이 있는지 3단계로 돌아가 확인합니다. 계정 잔액을 직접 비교하려면 `eth_getBalance` 에 블록 번호를 넣어 조회합니다[2]. 같은 블록에 그 계정의 트랜잭션이 여럿 있으면 블록 사이 잔액 차이는 모두를 더한 값이라는 점을 함께 봅니다.

### 6. 받는 주소가 무엇인지 확인하고 다음으로 넘어갑니다

받는 주소마다 EOA 인지 컨트랙트인지 먼저 확인합니다. 조사 대상 블록을 넣어 `eth_getCode` 로 코드를 조회하면 되는데, 자세한 조건은 [이더리움의 계정과 로그](../../01-foundations/blockchain/ethereum-accounts.md)에 있습니다. Pectra 업그레이드의 타입 4 트랜잭션(EIP-7702)을 보낸 EOA 는 code 필드에 위임한 컨트랙트 주소가 들어가므로[1], 코드가 있다고 바로 컨트랙트로 단정하지 않습니다.

받는 주소가 EOA 면 3단계부터 다시 합니다. 컨트랙트면 그 컨트랙트가 무엇인지에 따라 다음 방법이 달라집니다.

- 토큰 컨트랙트: 이동은 이벤트로 읽고, 7단계에서 실제 잔액으로 확인합니다.
- 탈중앙 거래소·브리지: 스왑으로 자산 종류가 바뀌거나 다른 체인으로 넘어갑니다. 이벤트를 읽고 체인 사이를 잇는 방법은 [탈중앙 거래소와 브리지](../../01-foundations/ecosystem/dex-bridge.md)에서 다룹니다.
- 거래소 입금 주소: 이 뒤는 체인이 아니라 거래소 장부입니다. [거래소 자료 분석](exchange-analysis.md)으로 넘어갑니다.
- 여러 사람의 자산을 섞는 컨트랙트: 들어간 금액과 나온 금액을 일대일로 잇는 값이 체인에 없습니다. [믹서와 추적을 어렵게 하는 방법](../../01-foundations/ecosystem/mixers.md)을 봅니다.

컨트랙트 계정은 개인 키가 없고 받은 트랜잭션에 반응해서만 움직이므로[3], 컨트랙트가 옮긴 이동은 그 컨트랙트를 호출한 EOA 의 트랜잭션까지 거슬러 올라가 누가 시작했는지 적습니다.

### 7. 토큰 이동은 잔액으로 다시 확인합니다

토큰 이벤트는 컨트랙트 코드가 쓰는 대로 나옵니다. 사기 토큰 wARB 에는 잔액을 옮기지 않고 `Transfer` 이벤트만 내보내는 함수(`dropNewTokens`)가 있었고, 컨트랙트 주인이 보낸 토큰은 이벤트의 보낸 쪽이 다른 주소(deployer)로 바뀌어 기록됐습니다[7]. 이벤트만 읽는 오프체인 앱은 이런 이벤트에 속습니다[7].

그래서 결론에 쓰는 토큰 이동은 두 가지를 더 확인합니다. 하나는 이동 직전 블록과 직후 블록에서 토큰 컨트랙트의 `balanceOf` 로 보낸 쪽·받는 쪽 잔액을 조회해 이벤트 금액만큼 바뀌었는지 보는 것입니다. 다른 하나는 로그의 `address` 가 조사 대상 토큰의 실제 컨트랙트 주소인지 토큰 발행처 문서로 확인하는 것입니다. 탐색기에서 소스 코드가 검증됐다는 것은 올린 소스가 배포된 코드와 같다는 뜻일 뿐 정상 토큰이라는 뜻은 아닙니다[7].

### 8. 기기 기록과 맞춥니다

기기의 지갑 기록이 있으면 표의 각 행과 맞춰 봅니다. MetaMask 의 트랜잭션 기록(`TransactionMeta`)에는 `chainId`, 요청한 사이트 `origin`, `hash`, `status`, `txParams`(`from`·`to`·`value`·`nonce` 등), `type` 이 있습니다[14]. 파일 위치와 읽는 법은 [MetaMask](../../02-artifacts/browser/metamask/index.md)에서 다룹니다.

맞춰 볼 때는 해시보다 `from`·`nonce` 쌍을 기준으로 삼습니다. 사용자가 대기 중인 트랜잭션을 가속하면 MetaMask 는 같은 nonce 로 가스 수수료를 올린 새 트랜잭션을 만들고 `type` 을 `retry` 로 둡니다[14]. MetaMask 는 같은 계정·같은 nonce 의 다른 트랜잭션이 `confirmed` 가 되면 기존 트랜잭션을 `dropped` 로 바꿉니다[15]. 또 네트워크의 다음 nonce 가 이 트랜잭션의 nonce 를 넘었는데 영수증이 없으면, 동기화가 늦은 노드일 수 있어 3블록을 기다린 뒤 `dropped` 로 바꿉니다[15]. `dropped` 기록에는 대신 들어간 트랜잭션의 해시가 `replacedBy` 에 들어갑니다[14]. 그래서 기기에는 체인에 없는 `dropped` 원본과 체인에 있는 교체본이 함께 남을 가능성이 있고, 원본 해시로 체인을 조회해 없다고 끝내지 않습니다.

### 9. 확정됐는지 확인합니다

최근 블록의 이동은 체인 재구성으로 빠질 수 있습니다. 재구성으로 빠진 로그는 JSON-RPC 에서 `removed` 가 `true` 로 오고[2], `finalized` 블록 태그로 조회하면 확정된 블록까지만 기준으로 삼습니다[2]. 확정된 블록을 되돌리려면 스테이킹된 ETH 의 1/3 이상이 소각돼야 합니다[4]. 확정 조건과 걸리는 시간은 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에서 다룹니다. 보고서에 쓰는 이동은 확정된 블록에 있는 것만 씁니다.

## 도구

**이더리움 JSON-RPC.** 직접 운영하는 노드에 `eth_getTransactionByHash`·`eth_getTransactionReceipt`·`eth_getBlockByNumber`·`eth_getLogs`·`eth_getTransactionCount`·`eth_getBalance`·`eth_getCode` 를 묻습니다[2]. 조회할 때마다 기준 블록을 지정할 수 있어서 결과를 다시 만들 수 있습니다. 표준 메서드에는 내부 이동 목록이 없습니다[2].

**Etherscan API v2.** `txlist`·`txlistinternal`·`tokentx`·`tokennfttx`·`getLogs` 로 3단계의 목록을 받고, API 키가 필요합니다[9][10][11][12][13]. 응답 `status` 가 `0` 이면 오류일 수도 있고 결과가 없을 수도 있어서 `message` 를 함께 봅니다[9]. 필드를 읽는 법은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)에서 다룹니다.

**오픈소스 블록 탐색기.** Blockscout·Otterscan·lazy-etherscan 은 소스가 공개된 이더리움 탐색기입니다[8]. Etherscan 결과를 다른 탐색기로 한 번 더 조회해 두 결과가 같은지 확인할 때 씁니다.

**iLEAPP.** iOS MetaMask 앱의 `persist-root` 에서 `TransactionController.transactions` 의 시각, 보낸 주소, 받는 주소, 금액, 트랜잭션 해시를 뽑습니다[16]. 8단계의 기기 기록으로 씁니다.

## 함정과 한계

**트랜잭션의 `to`·`value` 를 받는 사람·금액으로 읽기.** 토큰 전송과 컨트랙트 호출은 `to` 가 컨트랙트이고 `value` 가 0 일 수 있습니다. 일반 트랜잭션 목록만 보면 이동이 통째로 빠지거나 "컨트랙트로 0 ETH" 로 잘못 읽습니다.

**ERC-20 과 ERC-721 이벤트 섞기.** 두 표준의 `Transfer` 는 서명 문자열이 같아 `topics[0]` 도 같습니다[5][13]. 토픽 개수를 보지 않으면 NFT 번호를 토큰 금액으로 읽습니다. 구분하는 법은 [토큰과 NFT](../../01-foundations/blockchain/tokens.md)에 있습니다.

**권한 부여와 대리 이동.** `Approval` 은 옮길 권한을 준 기록이라 이동이 아닙니다. 권한을 받은 주소가 나중에 옮기면 이벤트의 보낸 쪽은 피해자 주소인데 트랜잭션을 서명한 계정은 권한을 받은 쪽입니다. 이 흐름은 [피싱 사이트에 서명했나](../../04-scenarios/fraud/wallet-drainer.md)에서 다룹니다.

**탐색기 결과를 그대로 믿기.** 탐색기는 중앙에서 운영하는 서비스라 조작되거나 해킹될 수 있어서, 중요한 이벤트는 직접 확인하는 방법을 씁니다[7]. 내부 이동 목록도 표준 JSON-RPC 에 없는 탐색기 자체 자료라서[2][10], 보고서에 어느 서비스에서 언제 받은 목록인지 적습니다.

**함수 선택자로 함수를 단정하기.** 같은 4바이트 선택자를 쓰는 함수 서명이 여럿일 수 있어서, 검증된 소스나 ABI 로 확인합니다[1].

**색인된 동적 값.** 문자열·배열을 `indexed` 로 둔 이벤트는 토픽에 해시만 있어서 원래 값을 되살릴 수 없습니다[5].

**흐름이 합쳐지는 지점.** 풀·브리지·거래소 입금 주소처럼 여러 사람의 자산이 한 주소에 모이면, 들어간 이동과 나온 이동을 체인 데이터만으로 짝지을 수 없습니다. 이 지점부터는 금액·시각이 비슷하다는 것을 근거로 한 추정이 되므로 보고서에 추정이라고 밝히고, 거래소 자료나 기기 기록처럼 체인 밖 자료로 잇습니다.

## 결과를 어떻게 해석하나

### 증명하는 것

- 특정 EOA 의 키로 서명된 트랜잭션이 특정 블록에 들어갔다는 것, 그 트랜잭션의 nonce 와 실행 결과(`status`), 옮긴 ETH 금액[1][2][3].
- 토큰 컨트랙트가 그 트랜잭션에서 그 내용의 이벤트를 남겼다는 것[2][5]. 이벤트 내용과 실제 잔액 변화가 같은지는 7단계로 따로 확인한 만큼만 말할 수 있습니다[7].

### 증명하지 못하는 것

- EOA 를 쥔 사람의 신원. 체인에는 주소와 서명만 있습니다. 컨트랙트 계정은 개인 키가 없어서[3] 컨트랙트 주소 뒤에 특정 소유자가 있다고 말할 수도 없습니다.
- 서명한 사람의 의도. 컨트랙트 호출은 EOA 가 시작하지만 내부 이동은 컨트랙트 코드가 합니다[3][10]. 서명한 사람이 그 결과를 알고 서명했는지는 체인 기록으로 확인되지 않습니다.
- 실패한 트랜잭션의 이동. `status` 가 `0` 이면 블록에 들어갔어도 옮겨졌다고 쓰지 않습니다.
- 흐름이 합쳐지는 지점 뒤의 연결. 6단계의 풀·브리지·거래소를 지난 뒤의 연결은 체인 밖 자료로 확인하기 전까지 추정입니다.

### 시각

표의 시각은 블록 시각입니다. 블록의 `timestamp` 는 블록을 만든 시각을 유닉스 초로 적은 값이라 UTC 기준이고[2], Etherscan 목록의 `timeStamp` 도 블록 시각입니다[9][13]. JSON-RPC 로그 객체에는 시각 필드가 없어서 로그가 든 블록의 시각을 씁니다[2]. 지갑 앱 기록의 시각은 기기 시계로 적은 값이라 블록 시각과 다를 수 있습니다. MetaMask 의 `submittedTime` 은 네트워크에 보낸 시각(유닉스 밀리초)이고 `blockTimestamp` 는 블록 시각입니다[14]. 여러 시각을 한 줄로 정리하는 방법은 [암호화폐 타임라인](timeline.md)에서 다룹니다.

### 체인 밖에 남는 기록

지갑과 DApp 은 조회하는 동안 주소를 제3자에게 보낼 수 있습니다. 2023년 시험에서 DApp 웹사이트 1,572개 가운데 지갑 자동 연결에 성공한 616개 중 211개(35%)와 지갑 확장 100개 중 13개가 사용자 지갑 주소를 블록체인 제공자나 분석 서비스 같은 제3자에게 보냈습니다[17]. 2023년 무렵 MetaMask 의 기본 블록체인 제공자인 Infura 의 개인정보 방침에는 IP 주소와 지갑 주소를 수집한다는 내용이 들어 있었습니다[17]. 체인에는 주소와 사람을 잇는 값이 없지만, 이런 제공자 기록이 주소와 IP 주소를 함께 담고 있을 가능성이 있어서, 체인 밖에서 주소의 사용자를 확인하는 자료가 될 수 있습니다.

### 보고서 문장 예

아래 주소·해시·금액은 모두 지어낸 값입니다(만든 예시).

> 이 기기의 MetaMask 기록에 주소 0x1111…1111 의 nonce 7 트랜잭션(`status` `confirmed`)이 있습니다. 이더리움 메인넷(chainid 1)의 블록 19,000,000(블록 시각 2024-01-01 00:00:11 UTC, 확정된 블록)에 같은 주소·같은 nonce 의 트랜잭션 0xaaaa…aaaa 가 있고, 영수증 `status` 는 1 입니다. 이 트랜잭션에서 토큰 컨트랙트 0x3333…3333 이 0x1111…1111 에서 0x2222…2222 로 1,000 토큰의 `Transfer` 이벤트를 남겼고, 직전·직후 블록의 `balanceOf` 조회에서 두 주소의 잔액이 같은 양만큼 바뀌었습니다. 0x2222…2222 를 누가 통제하는지는 체인 기록으로 확인되지 않습니다.

보고서 전체 구성은 [암호화폐 포렌식 보고서](../reporting/forensic-report.md)에서 다룹니다.

## 참고 문헌

1. ethereum.org, "Transactions". https://ethereum.org/en/developers/docs/transactions/
2. ethereum.org, "JSON-RPC API". https://ethereum.org/en/developers/docs/apis/json-rpc/
3. ethereum.org, "Ethereum accounts". https://ethereum.org/en/developers/docs/accounts/
4. ethereum.org, "Proof-of-stake (PoS)". https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/
5. Solidity documentation, "Contract ABI Specification". https://docs.soliditylang.org/en/latest/abi-spec.html
6. ERC-1155, "Multi Token Standard". https://github.com/ethereum/ERCs/blob/master/ERCS/erc-1155.md
7. ethereum.org, "Some tricks used by scam tokens and how to detect them". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/tutorials/scam-token-tricks/index.md
8. ethereum.org, "Block explorers". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/data-and-analytics/block-explorers/index.md
9. Etherscan API, "Get Normal Transactions By Address" (txlist). https://docs.etherscan.io/api-reference/endpoint/txlist.md
10. Etherscan API, "Get Internal Transactions by Address" (txlistinternal). https://docs.etherscan.io/api-reference/endpoint/txlistinternal.md
11. Etherscan API, "Get ERC20 Token Transfers by Address" (tokentx). https://docs.etherscan.io/api-reference/endpoint/tokentx.md
12. Etherscan API, "Get ERC721 Token Transfers by Address" (tokennfttx). https://docs.etherscan.io/api-reference/endpoint/tokennfttx.md
13. Etherscan API, "Get Event Logs by Address" (getLogs). https://docs.etherscan.io/api-reference/endpoint/getlogs.md
14. MetaMask core, `packages/transaction-controller/src/types.ts`. https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/types.ts
15. MetaMask core, `packages/transaction-controller/src/helpers/PendingTransactionTracker.ts`. https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/helpers/PendingTransactionTracker.ts
16. iLEAPP, `scripts/artifacts/metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
17. Christof Ferreira Torres, Fiona Willi, Shweta Shinde, 「Is Your Wallet Snitching On You? An Analysis on the Privacy Implications of Web3」, arXiv, 2023, doi:10.48550/arXiv.2306.08170
