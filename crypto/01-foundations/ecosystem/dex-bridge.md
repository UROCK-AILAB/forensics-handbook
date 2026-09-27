---
title: "탈중앙 거래소와 브리지"
parent: "기반 · 거래 환경"
nav_order: 100
---

# 탈중앙 거래소와 브리지 (DEX·Bridge)

탈중앙 거래소와 브리지는 운영 회사의 장부가 아니라 스마트 컨트랙트로 돌아가서, 거래 흔적이 트랜잭션과 이벤트 로그로 블록체인에 남습니다. 대신 자산을 맡아 계정을 관리하는 거래소가 없어서 누가 거래했는지는 체인 밖의 자료, 특히 지갑 앱에 남은 스왑·브리지 기록으로 이어야 합니다. 이 페이지는 스왑과 브리지가 체인과 지갑에 남기는 모양, 읽는 법, 해석할 때 틀리기 쉬운 점을 다룹니다.

## 이 형식을 쓰는 아티팩트

탈중앙 거래소 (Decentralized Exchange, DEX) 는 토큰끼리 바꿔 주는 서비스이고, 사용자는 거래하는 동안에도 자산 통제권을 넘기지 않습니다[1]. 중앙화 거래소는 거래 전에 자산을 맡겨야 한다는 점이 다릅니다[1]. 그래서 DEX 거래는 거래소가 따로 적은 입출금 장부가 없고, 기록은 체인과 이용자의 기기에 나뉘어 남습니다. 중앙화 거래소의 기록은 [거래소와 가상자산사업자](exchanges.md)에서 다룹니다.

브리지 (Bridge) 는 블록체인 사이에서 토큰·메시지·데이터·컨트랙트 호출을 옮깁니다[2]. 한 번 옮기면 출발 체인과 도착 체인에 트랜잭션이 하나씩 생기고, 두 트랜잭션을 잇는 정보는 브리지 운영 쪽이나 지갑이 받아 둔 상태 기록에 있습니다.

| 아티팩트 | 남는 것 | 다루는 페이지 |
|---|---|---|
| 블록체인의 트랜잭션·영수증 | 스왑을 요청한 계정(`from`), 호출한 컨트랙트(`to`), 이벤트 로그 | [이더리움의 계정과 로그](../blockchain/ethereum-accounts.md) |
| DEX 풀·토큰 컨트랙트의 이벤트 로그 | `Swap`·`Sync`·`Mint`·`Burn`, 토큰 `Transfer`·`Approval`[6][7] | 이 페이지, [토큰과 NFT](../blockchain/tokens.md) |
| MetaMask 트랜잭션 기록 (`TransactionMeta`) | 트랜잭션 종류 `swap`·`bridge`·`swapApproval`·`bridgeApproval`, 주고받은 토큰, 도착 체인[8] | [MetaMask](../../02-artifacts/browser/metamask/index.md) |
| MetaMask 브리지 상태 기록 (`txHistory`) | 출발·도착 체인의 트랜잭션 해시, 쓴 브리지, 시작·완료 시각[10][12] | [MetaMask](../../02-artifacts/browser/metamask/index.md) |
| 블록 탐색기 조회 결과 | 토큰 전송 목록, 내부 호출 목록, 로그[14][15][16] | [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md) |

## 구조

### DEX 풀의 이벤트

DEX 는 두 토큰을 담아 둔 풀 (pool) 컨트랙트가 교환을 처리하고, 교환할 때마다 풀이 이벤트를 남깁니다. 로그의 기본 구조, 곧 `topics[0]` 이 이벤트 서명의 Keccak-256 해시이고 `indexed` 인자가 뒤 토픽에, 나머지 인자가 `data` 에 들어간다는 규칙은 [이더리움의 계정과 로그](../blockchain/ethereum-accounts.md)에서 설명합니다. 여기서는 Uniswap v2·v3 의 인터페이스 코드에 선언된 이벤트를 예로 듭니다.

Uniswap v2 의 페어 (pair) 컨트랙트는 다음 이벤트를 선언합니다[6].

| 이벤트 | 인자 | 뜻 |
|---|---|---|
| `Swap` | `address indexed sender`, `uint amount0In`, `uint amount1In`, `uint amount0Out`, `uint amount1Out`, `address indexed to` | 교환. 들어온 양과 나간 양을 토큰마다 따로 적습니다. |
| `Sync` | `uint112 reserve0`, `uint112 reserve1` | 풀에 남은 두 토큰의 양 |
| `Mint` | `address indexed sender`, `uint amount0`, `uint amount1` | 유동성 공급 |
| `Burn` | `address indexed sender`, `uint amount0`, `uint amount1`, `address indexed to` | 유동성 회수 |

v2 페어는 그 자체로 ERC-20 토큰이기도 해서 `Transfer`·`Approval` 도 남깁니다[6]. 이벤트의 0번·1번 토큰이 무엇인지는 페어의 `token0()`·`token1()` 함수로 확인합니다[6].

Uniswap v3 의 풀은 `Swap` 을 다른 모양으로 남깁니다[7].

```solidity
event Swap(
    address indexed sender,     // 스왑을 호출하고 콜백을 받은 주소
    address indexed recipient,  // 스왑 결과를 받은 주소
    int256 amount0,             // 풀의 token0 잔액 변화량
    int256 amount1,             // 풀의 token1 잔액 변화량
    uint160 sqrtPriceX96,       // 스왑 뒤 가격의 제곱근 (Q64.96)
    uint128 liquidity,          // 스왑 뒤 유동성
    int24 tick                  // 스왑 뒤 가격의 로그 값
);
```

v2 는 들어온 양과 나간 양을 네 필드로 나눠 적고, v3 는 풀 기준 잔액 변화량을 부호 있는 정수 두 개로 적습니다[6][7]. v3 에서 양수는 풀에 들어온 양, 곧 사용자가 낸 토큰이고, 음수는 풀에서 나간 양, 곧 사용자가 받은 토큰입니다. v3 의 유동성 이벤트 `Mint`·`Burn` 은 v2 와 인자가 달라서 가격 구간(`tickLower`·`tickUpper`)과 포지션 소유자(`owner`)를 함께 적습니다[7].

### WETH

ETH 는 ERC-20 표준보다 먼저 나와서 ERC-20 규격을 따르지 않습니다[4]. 그래서 많은 DApp 은 ETH 대신 WETH 를 다룹니다. WETH 컨트랙트에 ETH 를 넣으면 같은 양의 WETH 가 새로 발행되고, WETH 를 되돌리면 그 WETH 를 소각하고 같은 양의 ETH 를 돌려줍니다[4]. 이더리움 메인넷의 정식 WETH 주소는 `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` 이고, 다른 체인에는 다른 주소의 WETH 가 있으며, 이름만 같은 다른 WETH 토큰도 있습니다[4]. ETH 로 토큰을 산 스왑을 따라가면 중간에 ETH 가 WETH 로 바뀌는 단계가 끼어 있습니다.

### 브리지의 자산 이동 방식과 종류

브리지가 자산을 옮기는 방식은 세 가지로 나눕니다[2].

| 방식 | 출발 체인 | 도착 체인 |
|---|---|---|
| 잠그고 발행 (lock and mint) | 자산을 컨트랙트에 잠급니다 | 같은 양의 자산을 새로 발행합니다 |
| 소각하고 발행 (burn and mint) | 자산을 소각합니다 | 자산을 새로 발행합니다 |
| 원자적 교환 (atomic swap) | 다른 당사자와 자산을 교환합니다 | 교환 상대가 도착 체인의 자산을 넘깁니다 |

많은 브리지가 도착 체인에 래핑 자산 (wrapped asset) 을 발행합니다[2]. 예를 들어 WBTC 는 이더리움의 ERC-20 토큰이고, 비트코인 블록체인의 BTC 자체가 아닙니다[3].

브리지는 구성에 따라 네이티브 브리지(Arbitrum Bridge, Polygon PoS Bridge, Optimism Gateway 등), 외부 검증자나 오라클에 기대는 브리지(Multichain, Across 등), 자산과 함께 메시지·데이터를 옮기는 일반 메시지 전달 브리지(Axelar, LayerZero, Nomad 등), 원자적 교환으로 자산을 옮기는 유동성 네트워크(Connext, Hop 등)로 나눕니다[2].

검증 방식으로는 신뢰형 (trusted) 과 비신뢰형 (trustless) 으로 나눕니다[2]. 신뢰형은 다중 서명 연합·오라클 같은 외부 검증자가 체인 사이 전송을 확인하고, 사용자는 자산 통제권을 넘깁니다[2][3]. 이때 운영자가 전송을 막거나(검열) 자금을 가져갈(수탁) 위험이 있습니다[3]. 비신뢰형은 연결한 체인의 검증자에게 기대고, 스마트 컨트랙트로 사용자가 자산 통제권을 유지합니다[2][3]. 신뢰형 브리지는 운영자 쪽 검증자가 체인 사이 전송을 확인하므로, 출발·도착 전송을 잇는 기록이 운영자에게 있을 가능성이 있습니다.

### 지갑에 남는 스왑·브리지 기록

MetaMask 는 트랜잭션마다 `TransactionMeta` 를 저장하고, 이 상태(`transactions`)는 컨트롤러 설정에서 `persist: true` 라 디스크에 남습니다[8][9]. 스왑·브리지와 관련된 트랜잭션 종류(`type`) 값은 다음과 같습니다[8].

| `type` 값 | 뜻 |
|---|---|
| `swap` | MetaMask 스왑으로 토큰을 바꾼 트랜잭션 |
| `swapAndSend` | 바꾼 토큰을 다른 받는 사람에게 보낸 트랜잭션 |
| `swapApproval` | 스왑 컨트랙트가 토큰을 꺼내 쓰도록 허락한 트랜잭션. 토큰마다 첫 스왑에 함께 생깁니다 |
| `bridge` | MetaMask 브리지로 다른 체인에 토큰을 옮긴 트랜잭션 |
| `bridgeApproval` | 브리지 컨트랙트에 토큰 사용을 허락한 트랜잭션. 토큰마다 첫 브리지에 함께 생깁니다 |
| `approve` | 일반 ERC-20 사용 허락 |

`TransactionMeta` 에서 스왑·브리지를 해석할 때 쓰는 필드는 이렇습니다[8].

| 필드 | 뜻 |
|---|---|
| `hash`·`chainId`·`status` | 트랜잭션 해시, 체인 ID(EIP-155, 헥스 문자열), 상태 |
| `origin` | 트랜잭션을 요청한 출처 |
| `time` | 트랜잭션에 붙은 시각 |
| `submittedTime` | 네트워크에 제출한 시각, 유닉스 밀리초 |
| `blockTimestamp` | 트랜잭션이 들어간 블록의 시각 |
| `sourceTokenAddress`·`sourceTokenAmount`·`sourceTokenSymbol` | 스왑에서 낸 토큰 |
| `destinationTokenAddress`·`destinationTokenAmount` | 스왑에서 받은 토큰 |
| `swapAndSendRecipient` | 바꾼 토큰을 받은 주소 |
| `approvalTxId` | 이 스왑에 앞서 사용을 허락한 트랜잭션의 ID |
| `preTxBalance`·`postTxBalance` | 트랜잭션 앞뒤 잔액 |
| `destinationChainId` | 브리지의 도착 체인 ID |

브리지는 이것과 별도로 `BridgeStatusController` 의 `txHistory` 에 기록이 남고, 이 상태도 활동 목록에 보여 주려고 `persist: true` 로 저장합니다[13]. `txHistory` 는 출발 체인 트랜잭션의 ID를 키로 한 기록 항목(`BridgeHistoryItem`) 모음입니다[10].

| 필드 | 뜻 |
|---|---|
| `txMetaId` | 출발 트랜잭션의 `TransactionMeta` ID. 제출 전이나 동기화에 실패하면 없습니다 |
| `quote`·`quoteId` | 브리지 견적. `quoteId` 는 이 필드가 생기기 전에 저장한 항목에는 없습니다 |
| `status` | 브리지 상태 응답(아래) |
| `startTime`·`completionTime` | 시작·완료 시각, 밀리초 |
| `estimatedProcessingTimeInSeconds` | 예상 처리 시간, 초 |
| `slippagePercentage` | 허용한 가격 변동 비율 |
| `pricingData.amountSent` | 사용자가 보낸 양 |
| `account` | 브리지를 요청한 계정 |
| `hasApprovalTx`·`approvalTxId` | 사용 허락 트랜잭션이 있었는지와 그 ID |
| `targetContractAddress` | 호출한 컨트랙트 주소 |

`status` 에는 진행 상태(`status`)와 `srcChain`·`destChain` 이 있고, `srcChain`·`destChain` 은 각각 `chainId`·`txHash`·`amount`·`token` 필드로 출발·도착 체인의 트랜잭션을 적습니다[12]. `destChain` 은 없어도 되는 필드라서 브리지가 끝나기 전 기록에는 빠져 있을 수 있습니다[12]. 브리지를 나타내는 문자열은 `bridge` 필드에 들어갑니다[12]. 코드에 정의된 브리지 식별자는 `hop`·`celer`·`celercircle`·`connext`·`polygon`·`avalanche`·`multichain`·`axelar`·`across`·`stargate`·`relay`·`mayan` 입니다[10]. MetaMask 는 이 상태를 기본값으로 브리지 API(`https://bridge.api.cx.metamask.io`)에서 받아 옵니다[11][13].

이 필드들은 2026년 9월 기준 MetaMask/core 저장소 main 브랜치의 코드입니다. 옛 버전에는 없는 필드가 있을 수 있으니 실제 데이터에서 필드 이름을 먼저 확인합니다. 저장 위치와 여는 방법은 [MetaMask](../../02-artifacts/browser/metamask/index.md) 페이지에서 다룹니다.

## 읽는 법

### 스왑 로그 한 건 풀기

아래는 Uniswap v3 `Swap` 이벤트 선언[7]과 로그 인코딩 규칙[5]으로 만든 예시이고, 주소와 금액은 모두 지어낸 값입니다(만든 예시).

```text
address   : 0x5555555555555555555555555555555555555555      (풀 컨트랙트)
topics[0] : Swap(address,address,int256,int256,uint160,uint128,int24) 의 Keccak-256 해시
topics[1] : 0x0000000000000000000000001111111111111111111111111111111111111111   (sender)
topics[2] : 0x0000000000000000000000002222222222222222222222222222222222222222   (recipient)
data      :
  word 0  : 0x0000000000000000000000000000000000000000000000000de0b6b3a7640000   (amount0)
  word 1  : 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffff88ca6c00   (amount1)
  word 2~4: sqrtPriceX96, liquidity, tick
```

`sender` 와 `recipient` 는 `indexed` 라서 토픽에 들어가고, 나머지 다섯 인자가 32바이트씩 `data` 에 들어갑니다[5][7]. word 0 은 양수 1,000,000,000,000,000,000 이라 풀이 token0 을 그만큼 받았고, 사용자가 token0 을 낸 것입니다. word 1 은 맨 앞 비트가 1 인 2의 보수라 음수이고, 값은 -2,000,000,000 입니다. 풀에서 token1 이 그만큼 나가 `recipient` 에게 갔다는 뜻입니다. 금액은 토큰의 최소 단위라서 token0 의 `decimals` 가 18 이면 1 개, token1 의 `decimals` 가 6 이면 2,000 개가 됩니다(만든 예시). 어떤 토큰이 token0·token1 인지는 풀 주소로 컨트랙트를 조회해 확인합니다.

`sender` 는 스왑을 호출한 주소라서 사용자 계정이 아니라 라우터 컨트랙트일 수 있습니다[7]. 스왑을 요청한 계정은 이 로그를 만든 트랜잭션의 `from` 으로 확인합니다. 같은 트랜잭션의 다른 로그에는 토큰 컨트랙트가 남긴 `Transfer` 가 있어서, 토큰이 사용자 계정에서 풀로, 풀에서 `recipient` 로 옮겨진 것을 한 번 더 맞춰 볼 수 있습니다. `Transfer` 를 읽는 방법은 [토큰과 NFT](../blockchain/tokens.md)에서 다룹니다.

### 브리지 한 건 잇기

브리지 한 번은 체인 두 개에 트랜잭션 두 개로 남습니다. 출발 체인에서는 사용자 계정이 브리지 컨트랙트를 호출하는 트랜잭션이 보이고, 도착 체인에서는 브리지 쪽이 받는 주소로 자산을 보내거나 발행하는 트랜잭션이 보입니다. 두 트랜잭션은 서로 다른 체인에 있어서, 한 체인의 트랜잭션만 보고는 다른 체인의 짝을 바로 알기 어렵습니다.

지갑에 `txHistory` 기록이 있으면 순서는 다음과 같습니다.

1. `TransactionMeta` 에서 `type` 이 `bridge` 인 항목을 찾아 `hash`·`chainId`·`destinationChainId` 를 적습니다[8].
2. 같은 ID를 키로 한 `txHistory` 항목에서 `status.srcChain.txHash` 와 `status.destChain.txHash` 를 읽습니다[10][12].
3. 출발 체인과 도착 체인의 블록 탐색기나 노드에서 두 해시를 각각 조회해 금액·받는 주소·블록 시각을 확인합니다.
4. `status.srcChain.amount` 는 수수료를 뺀 보낸 양, `status.destChain.amount` 는 받은 양이고 둘 다 토큰의 최소 단위라서[12], 두 값이 다른 것은 정상입니다.

두 해시가 지갑 기록에 함께 있으면 두 트랜잭션을 한 번의 브리지로 잇는 근거가 됩니다. 지갑 기록이 없으면 브리지 운영 쪽 자료나 금액·시각 비교로 후보를 찾는 수밖에 없습니다.

## 포렌식에서 중요한 점

### 증명하는 것

- 트랜잭션의 `from` 은 스왑이나 브리지를 요청해 서명한 계정입니다. 같은 트랜잭션의 `Swap`·`Transfer` 로그로 어떤 토큰이 얼마나 어느 주소로 갔는지 알 수 있습니다[5][6][7].
- 기기의 MetaMask 기록에 `type` 이 `swap`·`bridge` 인 항목이 있으면, 이 지갑에서 그 스왑·브리지를 요청했다는 사실이 확인됩니다[8].
- `txHistory` 에 출발·도착 해시가 함께 있으면 두 체인의 트랜잭션이 한 번의 브리지라는 연결 근거가 됩니다[10][12].

### 증명하지 못하는 것

- `Swap` 의 `sender` 가 사용자라는 것은 증명하지 못합니다. 라우터 컨트랙트일 수 있습니다[7].
- 출발·도착 트랜잭션이 같은 사람의 것이라는 사실은 체인 데이터만으로 확인하기 어렵습니다. 지갑 기록이나 브리지 운영 쪽 자료로 이어야 합니다[2][12].
- DEX 는 사용자가 자산을 맡기지 않고 자산 통제권을 유지하는 구조라[1] 중앙화 거래소 같은 계정 기록이 따로 없습니다. 누가 거래했는지는 기기·거래소 입출금 등 다른 자료로 확인합니다.
- 토큰 기호가 같다고 같은 자산은 아닙니다. 토큰은 컨트랙트 주소로 특정합니다[4].

### 기기 밖에 남는 흔적

DApp 과 지갑이 사용자의 지갑 주소를 분석·추적 업체 같은 제3자에게 보내기도 합니다. DApp 616개와 지갑 100개의 통신을 조사한 연구에서 DApp 211개가 2,000건 넘게, 지갑 13개가 300건 넘게 지갑 주소를 제3자에게 보냈습니다[17]. 같은 연구에서 DappRadar 분류 기준으로 DeFi DApp 93개(45%), 거래소 DApp 19개(59%)가 주소를 보냈고, 주소를 받은 상위 제3자 20곳의 개인정보 처리방침 중 95%가 IP 주소를 수집한다고 적었습니다[17]. 그래서 이런 업체의 기록에 지갑 주소와 IP 주소가 함께 있을 가능성이 있습니다.

### 시각

이벤트 로그에는 시각 필드가 없고, 로그를 만든 트랜잭션이 들어간 블록의 시각을 씁니다[5]. 블록 시각을 읽는 방법은 [블록 시각과 확정](../blockchain/block-time.md)에서 다룹니다. MetaMask 는 `submittedTime` 을 트랜잭션을 제출할 때의 기기 시각(유닉스 밀리초)으로 적습니다[8][9]. 브리지 기록의 `startTime` 은 브리지를 시작할 때, `completionTime` 은 브리지 API 에서 완료·실패 상태를 받았을 때의 기기 시각(`Date.now()`, 밀리초)입니다[10][13]. 그래서 `completionTime` 은 도착 트랜잭션의 블록 시각보다 늦을 수 있고, 기기 시계가 틀리면 함께 틀립니다. 두 값은 블록 시각과 비교해 차이를 확인합니다. 브리지는 출발·도착 체인의 블록 시각이 따로 있고, 둘 사이 간격은 `estimatedProcessingTimeInSeconds`(예상 처리 시간)와 비교해 볼 수 있습니다[10].

Etherscan 의 `timeStamp` 는 블록이 채굴된 시각인데, tokentx·txlistinternal 은 10진수 초로, getLogs 는 헥스 문자열로 줍니다[14][15][16]. 같은 이름의 필드라도 조회한 API 에 따라 변환 방법이 다릅니다.

### 해킹 자금과 브리지

DeFi 에서 피해가 가장 컸던 해킹 상위 세 건이 브리지에서 일어났습니다[2]. Wormhole 브리지 해킹에서는 wETH 12만 개(3억 2,500만 달러)를 빼앗겼습니다[3]. 2022년 6월 24일 Harmony Bridge 해킹 자금 9,600만 달러 이상과 2022년 8월 2일 Nomad 해킹 자금 최소 780만 달러가 Tornado Cash 로 세탁됐고, 미국 재무부 해외자산통제실 (OFAC) 은 2022년 8월 8일 Tornado Cash 를 제재 대상에 올렸습니다[18]. 브리지 해킹 자금이 믹서로 가는 흐름은 [믹서와 추적을 어렵게 하는 방법](mixers.md)에서 이어서 다룹니다.

## 함정

**한 번의 스왑이 여러 건으로 보입니다.** 첫 스왑의 사용 허락 트랜잭션(`swapApproval`), ETH 와 WETH 사이 전환, 라우터 컨트랙트의 내부 호출이 끼어서 스왑 하나가 트랜잭션 두 건과 로그 여러 개로 나타납니다[4][8]. 허락한 금액이 남아 있으면 스왑이 끝난 뒤에도 그 컨트랙트가 토큰을 꺼낼 수 있습니다([토큰과 NFT](../blockchain/tokens.md)). 악성 허락이 의심되면 [피싱 사이트에 서명했나](../../04-scenarios/fraud/wallet-drainer.md)를 봅니다.

**이름이 같은 토큰이 여럿입니다.** 이름만 같은 다른 WETH 가 있고, 체인마다 정식 WETH 주소가 다릅니다[4]. 토큰은 기호가 아니라 컨트랙트 주소와 체인으로 적습니다. Etherscan 토큰 전송 목록도 `contractAddress` 를 함께 줍니다[15].

**v2 와 v3 의 금액 필드 뜻이 다릅니다.** v2 는 `amount0In`·`amount0Out` 처럼 들어온 양과 나간 양이 따로이고, v3 는 부호 있는 변화량 하나입니다[6][7]. v3 금액을 부호 없이 읽으면 낸 토큰과 받은 토큰이 뒤바뀝니다.

**체인 ID 표기가 기록마다 다릅니다.** `TransactionMeta` 의 `chainId` 는 헥스 문자열이고[8], 브리지 상태 응답의 `chainId` 는 숫자입니다[12]. 같은 체인이 다르게 보이므로 10진수로 맞춰 비교합니다.

**출발 해시가 비어 있을 수 있습니다.** 스마트 트랜잭션 (Smart Transaction) 으로 보낸 브리지는 `srcChain.txHash` 가 없을 수 있습니다[12]. 이때는 `TransactionMeta` 의 `hash` 나 체인 조회로 출발 트랜잭션을 찾습니다.

**브리지 목록은 시점에 따라 바뀝니다.** 문서와 코드에 실린 브리지 이름은 그때의 예시이고[2][10], 서비스가 운영 중인지, 어느 체인을 잇는지는 조사 시점에 따로 확인합니다.

**Swap 이벤트 토픽 값은 직접 계산합니다.** `topics[0]` 은 이벤트 서명의 Keccak-256 해시라서[5] v2 와 v3 의 `Swap` 은 서명이 달라 토픽 값도 다릅니다. 서명 문자열을 만드는 규칙, 예를 들어 v2 선언의 `uint` 를 `uint256` 으로 바꿔 넣는 규칙은 [이더리움의 계정과 로그](../blockchain/ethereum-accounts.md)에서 다룹니다.

## 도구

- **이더리움 JSON-RPC.** `eth_getTransactionReceipt` 로 영수증과 로그를, `eth_getLogs` 로 컨트랙트 주소·토픽·블록 범위를 정해 로그를 받습니다[5].
- **Etherscan API.** tokentx(주소의 ERC-20 전송, `contractAddress`·`tokenSymbol`·`tokenDecimal`·`value` 포함), txlistinternal(컨트랙트가 일으킨 내부 호출, `type`·`traceId`·`isError` 포함), getLogs(로그 조회)를 씁니다[14][15][16]. 제3자 조회 서비스를 쓸 때 주의할 점은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)에서 다룹니다.
- **브리지 요약 사이트.** L2BEAT 는 브리지별 종류·도착 체인·위험 분석을, DefiLlama 는 이더리움 계열 네트워크의 브리지 거래량을 요약합니다[3]. 어떤 브리지가 어떤 방식인지 확인할 때 씁니다.

계정 사이 흐름을 따라가는 절차는 [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md)에서 다룹니다.

## 참고 문헌

1. ethereum.org, "Decentralized finance (DeFi)". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/defi/index.md
2. ethereum.org, "Bridges" (developers docs). https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/bridges/index.md
3. ethereum.org, "Blockchain bridges". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/bridges/index.md
4. ethereum.org, "Wrapped ether (WETH)". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/wrapped-eth/index.md
5. ethereum.org, "JSON-RPC API". https://ethereum.org/en/developers/docs/apis/json-rpc/
6. Uniswap v2-core, `contracts/interfaces/IUniswapV2Pair.sol`. https://github.com/Uniswap/v2-core/blob/master/contracts/interfaces/IUniswapV2Pair.sol
7. Uniswap v3-core, `contracts/interfaces/pool/IUniswapV3PoolEvents.sol`. https://github.com/Uniswap/v3-core/blob/main/contracts/interfaces/pool/IUniswapV3PoolEvents.sol
8. MetaMask core, `packages/transaction-controller/src/types.ts`. https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/types.ts
9. MetaMask core, `packages/transaction-controller/src/TransactionController.ts`. https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/TransactionController.ts
10. MetaMask core, `packages/bridge-status-controller/src/types.ts`. https://github.com/MetaMask/core/blob/main/packages/bridge-status-controller/src/types.ts
11. MetaMask core, `packages/bridge-status-controller/src/constants.ts`. https://github.com/MetaMask/core/blob/main/packages/bridge-status-controller/src/constants.ts
12. MetaMask core, `packages/bridge-status-controller/src/utils/validators.ts`. https://github.com/MetaMask/core/blob/main/packages/bridge-status-controller/src/utils/validators.ts
13. MetaMask core, `packages/bridge-status-controller/src/bridge-status-controller.ts`. https://github.com/MetaMask/core/blob/main/packages/bridge-status-controller/src/bridge-status-controller.ts
14. Etherscan API, "Get Event Logs by Address" (getLogs). https://docs.etherscan.io/api-reference/endpoint/getlogs.md
15. Etherscan API, "Get ERC20 Token Transfers by Address" (tokentx). https://docs.etherscan.io/api-reference/endpoint/tokentx.md
16. Etherscan API, "Get Internal Transactions by Address" (txlistinternal). https://docs.etherscan.io/api-reference/endpoint/txlistinternal.md
17. Christof Ferreira Torres, Fiona Willi, Shweta Shinde, 「Is Your Wallet Snitching On You? An Analysis on the Privacy Implications of Web3」, arXiv, 2023, doi:10.48550/arXiv.2306.08170
18. U.S. Department of the Treasury, "U.S. Treasury Sanctions Notorious Virtual Currency Mixer Tornado Cash" (2022년 8월 8일). https://home.treasury.gov/news/press-releases/jy0916
