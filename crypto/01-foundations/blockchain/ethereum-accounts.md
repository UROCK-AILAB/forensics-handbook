---
title: "이더리움의 계정과 로그"
parent: "기반 · 블록체인 기초"
nav_order: 20
---

# 이더리움의 계정과 로그 (Accounts·Logs)

이더리움은 비트코인처럼 쓰지 않은 출력을 하나씩 따라가지 않고, 주소마다 잔액과 순번을 담은 계정 상태를 둡니다. 트랜잭션은 계정이 순번(nonce)을 하나씩 올려 가며 보내는 서명된 명령이고, 컨트랙트가 실행 중에 남기는 로그(log)는 트랜잭션 영수증에 붙어 블록에 남습니다. 이 페이지는 계정의 필드와 두 종류의 계정, 트랜잭션·영수증에서 계정과 이어지는 필드, 로그의 토픽과 데이터 구조, 그리고 지갑 앱 기록을 체인 기록과 맞춰 볼 때 알아야 할 점을 다룹니다.

## 이 형식을 쓰는 아티팩트

이더리움 계열 지갑 앱과 블록 탐색기는 계정·트랜잭션·로그를 이 페이지의 필드 이름 그대로, 또는 조금 바꾼 이름으로 저장합니다. 앱 기록을 체인 기록과 맞춰 보려면 아래 필드가 체인의 어느 값에 해당하는지 알아야 합니다.

| 기록 | 이 페이지 개념과 이어지는 필드 | 자세히 |
|---|---|---|
| MetaMask 트랜잭션 기록 (`TransactionMeta`) | `txParams` 안의 `from`·`to`·`value`·`nonce`·`data`, `hash`, `status`, `txReceipt`, `replacedBy`[10] | [MetaMask](../../02-artifacts/browser/metamask/index.md) |
| iOS MetaMask 앱의 `persist-root` | `AccountTrackerController.accounts` 의 주소별 `balance`, `TransactionController.transactions` 의 트랜잭션[11] | [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md) |
| Trust Wallet 옛 iOS 공개 코드의 Realm 객체 | `from`·`to`·`value`·`nonce`·`blockNumber`·`gasUsed`, 고유 ID `uniqueID`(= `from` + `-` + `nonce`)[12] | [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md) |
| Etherscan API 조회 결과 | txlist 의 `nonce`·`methodId`·`txreceipt_status`·`isError`, txlistinternal 의 `type`·`traceId`, getLogs 의 `topics`·`data`[7][8][13] | [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md) |

## 구조

### 계정 두 종류

계정은 외부 소유 계정(Externally Owned Account, EOA)과 컨트랙트 계정(contract account) 두 종류입니다[1]. 둘 다 ETH 와 토큰을 받고 보관하고 보낼 수 있고, 배포된 컨트랙트를 호출할 수 있습니다. 두 계정의 차이는 아래 표와 같습니다[1].

| 구분 | 외부 소유 계정 (EOA) | 컨트랙트 계정 |
|---|---|---|
| 통제 | 개인 키를 가진 사람 | 컨트랙트 코드. 개인 키가 없음 |
| 트랜잭션 시작 | 할 수 있음 | 못 함. 받은 트랜잭션에 반응해서만 메시지를 보냄 |
| 만드는 비용 | 없음 | 있음(네트워크 저장 공간을 씀) |
| 주소 길이 | `0x` + 헥스 40자 = 42자 | 42자로 같음 |

계정과 지갑은 다른 개념입니다. 지갑은 계정을 다루는 앱이고, 자금은 늘 이더리움 장부에 있습니다[1]. 주소를 공개 키에서 만드는 방법, `CREATE`·`CREATE2` 로 컨트랙트 주소가 정해지는 방식, EIP-55 대소문자 체크섬은 [주소 형식](../wallets/address-formats.md)에서 다룹니다.

주소 모양으로는 EOA 와 컨트랙트를 구분할 수 없습니다. EOA 의 `codeHash` 는 빈 문자열의 해시라서[1], JSON-RPC `eth_getCode` 로 그 주소의 코드를 조회하면 컨트랙트인지 확인할 수 있습니다[4]. 다만 Pectra 업그레이드의 타입 4 트랜잭션(EIP-7702)으로 권한을 위임한 EOA 는 그 뒤 code 필드에 위임받은 컨트랙트 주소가 들어가므로[2], 코드가 있다는 것만으로 컨트랙트라고 단정하지 않습니다. 조회할 때는 블록 번호도 함께 지정합니다. 컨트랙트가 배포되기 전 블록을 기준으로 하면 코드가 없는 것으로 나옵니다.

### 계정 상태의 필드

계정 하나에는 필드가 네 개 있습니다[1].

| 필드 | 뜻 |
|---|---|
| `nonce` | EOA 는 보낸 트랜잭션 수, 컨트랙트 계정은 만든 컨트랙트 수. 한 계정에서 같은 nonce 의 트랜잭션은 하나만 실행되어, 서명된 트랜잭션을 다시 보내 되풀이 실행하는 공격을 막음 |
| `balance` | 이 주소의 잔액(wei 단위). 1 ETH = 10^18 wei |
| `codeHash` | 계정 코드의 해시. 다른 필드와 달리 코드는 바꿀 수 없고, EOA 는 빈 문자열의 해시. EIP-7702 위임은 위 문단 참고 |
| `storageRoot` | 계정 저장소를 담은 머클 패트리샤 트라이(Merkle Patricia Trie) 루트의 256비트 해시. 기본값은 빈 트라이 |

`balance` 는 ETH 잔액뿐입니다. 토큰 잔액은 계정 필드가 아니라 토큰 컨트랙트 안에 있어서 컨트랙트에 물어봐야 하고, 자세한 내용은 [토큰과 NFT](tokens.md)에서 다룹니다. 체인에 있는 것은 현재 상태이고 계정별 거래 목록은 따로 없어서, 거래 이력은 트랜잭션·영수증·로그를 모아 되살립니다.

### 트랜잭션에서 계정과 이어지는 필드

트랜잭션은 EOA 가 시작하고, `from`·`to`·`signature`·`nonce`·`value`·`input data`·가스 관련 필드를 담습니다[2]. 트랜잭션 형식과 타입 0~4 의 차이는 [블록과 트랜잭션](blocks-transactions.md)에서 다루고, 여기서는 계정과 이어지는 필드만 봅니다.

| 필드 | 뜻 | 해석할 때 볼 점 |
|---|---|---|
| `from` | 서명한 보낸 사람 주소 | 컨트랙트는 트랜잭션을 보내지 못하므로 EOA[2] |
| `to` | 받는 주소 | EOA 면 ETH 이동, 컨트랙트면 그 컨트랙트 코드 실행. 컨트랙트를 배포하는 트랜잭션에는 `to` 가 없음[2] |
| `nonce` | 보낸 계정의 트랜잭션 순번 | 한 계정 안에서 하나씩 늘어남[2] |
| `value` | 보내는 ETH, wei 단위 | 토큰 전송이면 보통 0 이고, 실제 금액은 입력 데이터나 로그에 있음 |
| `input` (`data`) | 입력 데이터 | 앞 4바이트가 호출할 함수의 선택자(selector), 나머지가 인자[2] |

`to` 가 비어 있는 배포 트랜잭션은 영수증의 `contractAddress` 에 새 컨트랙트 주소가 들어갑니다[4].

### 영수증

영수증(receipt)은 트랜잭션을 실행한 결과입니다. `eth_getTransactionReceipt` 가 돌려주는 필드는 아래와 같고, 아직 블록에 들어가지 않은 트랜잭션에는 영수증이 없습니다[4].

| 필드 | 뜻 |
|---|---|
| `transactionHash`·`transactionIndex`·`blockHash`·`blockNumber` | 이 트랜잭션과, 들어 있는 블록·블록 안 위치 |
| `from`·`to` | 보낸 주소·받는 주소. 컨트랙트 생성이면 `to` 는 null |
| `status` | `1` 성공, `0` 실패. Byzantium 업그레이드 이전 블록은 `status` 대신 상태 루트 `root` 를 줌 |
| `gasUsed`·`cumulativeGasUsed`·`effectiveGasPrice` | 이 트랜잭션이 쓴 가스, 블록 안에서 여기까지 쓴 가스 합계, 가스 단위당 낸 값(기본 수수료 + 우선 수수료) |
| `contractAddress` | 컨트랙트를 만들었으면 그 주소, 아니면 null |
| `logs` | 이 트랜잭션이 만든 로그 객체 배열 |
| `logsBloom` | 관련 로그를 빨리 찾기 위한 256바이트 블룸 필터 |
| `type` | 트랜잭션 타입(`0x0` 레거시, `0x1` 접근 목록, `0x2` 동적 수수료) |

블록에는 로그 전체가 아니라 영수증 트라이의 루트 해시(`receiptsRoot`, 실행 페이로드에서는 `receipts_root`)와 블록 전체 로그의 블룸 필터(`logsBloom`)가 들어갑니다[3][4].

### 로그

로그 항목은 로그를 남긴 컨트랙트 주소, 최대 네 개의 토픽(topic), 길이가 정해지지 않은 데이터(data)로 이루어집니다[5]. 컨트랙트 코드에서 이벤트(event)를 내보내면 이 로그가 생깁니다.

토픽은 32바이트 값의 배열입니다. 이벤트를 `anonymous` 로 선언하지 않았으면 `topics[0]` 은 이벤트 서명 문자열, 곧 `이벤트이름(타입1,타입2,…)` 의 Keccak-256 해시입니다[5]. 서명 문자열의 타입은 정규 타입 이름으로 씁니다. 예를 들어 `uint` 는 `uint256` 으로 바꿔 넣습니다[5]. 그 뒤 토픽에는 `indexed` 로 선언한 인자가 차례로 들어가는데, 익명이 아닌 이벤트는 최대 3개, 익명 이벤트는 최대 4개입니다[5]. `indexed` 가 아닌 인자는 모두 ABI 인코딩해 `data` 에 넣습니다[5].

토픽에 들어가는 값은 타입에 따라 모양이 다릅니다. 주소·정수처럼 32바이트 이하인 값은 32바이트로 채워 그대로 들어갑니다. 주소와 부호 없는 정수는 앞을 0 으로 채우고, 음수는 부호 확장(sign extension)으로 채우며, `bytes1`~`bytes32` 는 뒤를 채웁니다[5]. 문자열·바이트열·배열·구조체처럼 길이가 바뀌는 타입을 `indexed` 로 두면, 토픽에는 값 대신 인코딩한 값의 Keccak 해시만 들어갑니다[5]. 이런 토픽은 찾는 값을 미리 알면 해시를 계산해 맞춰 볼 수는 있지만, 토픽만으로 원래 값을 되살릴 수는 없습니다[5].

JSON-RPC 가 돌려주는 로그 객체의 필드는 아래와 같고, 영수증의 `logs` 배열에도 같은 모양으로 들어 있습니다[4].

| 필드 | 뜻 |
|---|---|
| `removed` | 체인 재구성(reorganization)으로 로그가 없어졌으면 `true`, 유효한 로그면 `false` |
| `logIndex` | 블록 안에서 이 로그의 위치 |
| `transactionIndex`·`transactionHash` | 이 로그를 만든 트랜잭션 |
| `blockHash`·`blockNumber` | 이 로그가 들어 있는 블록 |
| `address` | 로그를 남긴 주소 |
| `data` | `indexed` 가 아닌 인자. Solidity 컨트랙트면 32바이트 단위 값 0개 이상 |
| `topics` | 32바이트 값 0~4개 |

블록에 들어가지 않은 로그는 `logIndex`·`transactionIndex`·`transactionHash`·`blockHash`·`blockNumber` 가 null 입니다[4]. 로그 객체에는 시각 필드가 없습니다.

## 읽는 법

### 로그 한 건 풀기

아래는 ERC-20 토큰 전송 로그를 명세대로 만든 예시입니다(만든 예시). 주소와 해시는 지어낸 값이고, `topics[0]` 만 ERC-20 `Transfer` 이벤트 서명의 실제 해시이고, 같은 값이 Etherscan API 의 영수증 응답 예시에도 나옵니다[9].

```json
{
  "address": "0x3333333333333333333333333333333333333333",
  "topics": [
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
    "0x0000000000000000000000001111111111111111111111111111111111111111",
    "0x0000000000000000000000002222222222222222222222222222222222222222"
  ],
  "data": "0x0000000000000000000000000000000000000000000000000de0b6b3a7640000",
  "blockNumber": "0x12d687",
  "transactionHash": "0x5555555555555555555555555555555555555555555555555555555555555555",
  "logIndex": "0x0",
  "removed": false
}
```

`address` 는 로그를 남긴 토큰 컨트랙트입니다[4]. `topics[0]` 은 `Transfer(address,address,uint256)` 의 Keccak-256 해시이고, ERC-20 은 이 이벤트의 `_from` 과 `_to` 를 `indexed` 로, `_value` 를 일반 인자로 선언합니다[6]. 그래서 `topics[1]` 과 `topics[2]` 에는 보낸 주소와 받은 주소가 앞 12바이트(헥스 24자)를 0 으로 채운 32바이트 값으로 들어갑니다[5]. 앞의 0 을 떼고 남은 헥스 40자 앞에 `0x` 를 붙이면 주소가 됩니다. `data` 는 `_value` 한 개를 32바이트로 인코딩한 값이고, `0x0de0b6b3a7640000` 은 10진수로 1,000,000,000,000,000,000 입니다. 이 숫자는 토큰의 최소 단위라서 토큰의 `decimals` 로 나눠야 화면에 보이는 금액이 됩니다. `blockNumber` `0x12d687` 은 10진수로 1,234,567 입니다.

JSON-RPC 의 수량 값은 `0x` 를 붙인 헥스 문자열이라, 표나 보고서로 옮길 때 10진수로 바꿔 적습니다. ERC-721 의 `Transfer` 도 서명 문자열이 같아서 `topics[0]` 이 같고, 토큰 번호(`_tokenId`)까지 `indexed` 라서 토픽이 네 개입니다[15]. 둘을 구분하는 방법은 [토큰과 NFT](tokens.md)에서 다룹니다.

### 입력 데이터의 함수 선택자

컨트랙트를 호출하는 트랜잭션의 입력 데이터는 앞 4바이트가 함수 선택자이고, 나머지는 인자를 32바이트 단위로 이어 붙인 값입니다[2]. 주소 같은 정수형 인자는 32바이트에 맞춰 앞을 0 으로 채웁니다[2]. 예를 들어 선택자 `0xa9059cbb` 로 알려진 함수 서명은 여럿이고, 컨트랙트 소스 코드가 공개된 경우에 `transfer(address,uint256)` 로 확정할 수 있습니다[2]. 그래서 선택자만으로 함수를 단정하지 않고 컨트랙트 소스 코드나 ABI 로 확인합니다.

아래는 이 선택자로 만든 입력 데이터입니다(만든 예시).

```text
a9059cbb                                                          함수 선택자 transfer(address,uint256)
0000000000000000000000002222222222222222222222222222222222222222  첫째 인자: 받는 주소 0x2222…2222
0000000000000000000000000000000000000000000000000de0b6b3a7640000  둘째 인자: 금액(토큰 최소 단위)
```

이 트랜잭션의 `to` 는 토큰 컨트랙트이고 `value` 는 0 일 수 있습니다. 실제로 토큰을 받는 주소는 입력 데이터의 첫째 인자와 `Transfer` 로그의 `topics[2]` 에 있습니다. Etherscan 트랜잭션 목록은 앞 4바이트를 `methodId` 로, 검증된 컨트랙트면 해독한 함수 서명을 `functionName` 으로 따로 줍니다[7].

### 계정 상태를 블록 기준으로 조회하기

`eth_getBalance`(wei 잔액), `eth_getTransactionCount`(보낸 트랜잭션 수), `eth_getCode`(계정 코드)는 모두 주소와 함께 블록 파라미터를 받습니다[4]. 블록 파라미터에는 블록 번호나 `earliest`(첫 블록), `latest`(가장 최근 제안된 블록), `safe`(가장 최근 safe head 블록), `finalized`(가장 최근 확정된 블록), `pending` 을 넣습니다[4]. 같은 주소라도 어느 블록을 기준으로 물었는지에 따라 값이 달라지므로, 보고서에는 조회한 값과 함께 블록 번호를 적습니다. 특정 트랜잭션 직전·직후 블록으로 `eth_getTransactionCount` 를 물어보면 그 사이에 그 계정의 nonce 가 몇 늘었는지 확인할 수 있습니다.

## 포렌식에서 중요한 점

### 증명하는 것

- 영수증의 `from` 계정이 서명한 트랜잭션이 영수증의 블록 번호·블록 해시의 블록에 들어 있고, 그 실행 결과가 `status` 값이라는 것[4]. 트랜잭션 서명은 보낸 사람의 개인 키로 만들어서, 그 계정 키로 서명했다는 것을 보여 줍니다[1][2].
- 한 계정에서 같은 nonce 로 실행된 트랜잭션은 하나뿐이라는 것[1]. 앱 기록의 `from`·`nonce` 쌍으로 체인의 트랜잭션 하나를 특정할 수 있습니다.
- 로그의 `address` 에 있는 컨트랙트가 그 트랜잭션을 실행하는 동안 그 토픽과 데이터로 된 로그를 남겼다는 것[4][5].

### 증명하지 못하는 것

- 누가 개인 키를 쥐고 서명했는지, 어느 기기에서 서명했는지는 체인 기록에 없습니다. "이 기기의 지갑 앱 데이터에 이 주소와 이 nonce 의 트랜잭션 기록이 있고, 같은 주소·nonce 의 트랜잭션이 이 블록에 있다" 처럼 기록으로 확인되는 만큼만 씁니다.
- 로그는 컨트랙트 코드가 남기겠다고 정한 기록입니다. EIP-20 은 토큰을 옮길 때 `Transfer` 이벤트를 반드시 남기라고 요구하지만[6], 그 요구를 지키는지는 각 컨트랙트 코드에 달려 있습니다. 그래서 로그 내용이 실제 상태 변화와 같다는 것은 그 컨트랙트 코드를 확인해야 말할 수 있습니다.
- 컨트랙트 실행 중에 일어난 내부 호출로 ETH 가 옮겨지면 트랜잭션의 `value` 에 나오지 않습니다. Etherscan 은 이런 내부 호출을 txlistinternal 로 따로 주고, 각 항목에 호출 종류(`call`·`create`·`create2`·`self-destruct`)를 `type`, 트랜잭션 안 호출 위치를 `traceId` 로 적습니다[8].

### nonce 로 앱 기록과 체인 기록 맞추기

nonce 는 앱 기록과 체인 기록을 이어 주는 값입니다. Trust Wallet 의 옛 iOS 공개 코드는 트랜잭션마다 `uniqueID` 를 `from` 주소와 `nonce` 를 `-` 로 이어 만듭니다[12]. MetaMask 트랜잭션의 상태는 `unapproved` → `approved` → `signed` → `submitted` 순서로 바뀌고, 끝 상태로 `confirmed`·`failed`·`dropped`·`rejected` 를 씁니다[10]. `dropped` 는 다른 트랜잭션에 밀려 버려진 상태이고, 이때 `replacedBy` 에 대신 들어간 트랜잭션의 해시가 들어갑니다[10]. `cancelled` 는 더 이상 쓰지 않는 상태 값입니다[10].

앱 기록에 `dropped` 가 있으면 체인에는 같은 `from`·`nonce` 로 다른 트랜잭션이 들어 있을 가능성이 있습니다. 이때는 앱 기록의 `hash` 로 체인을 조회해 없다고 끝내지 말고, 같은 계정의 같은 nonce 트랜잭션을 찾아 `replacedBy` 값과 비교합니다. 앱의 `rejected` 는 사용자가 서명을 거절한 기록이라 체인에는 대응하는 트랜잭션이 없습니다[10].

### 체인 재구성과 실패한 트랜잭션

블록에 들어 있다고 실행이 성공한 것은 아닙니다. `status` 가 `0` 인 트랜잭션도 블록 번호와 영수증이 있습니다[4]. Etherscan 트랜잭션 목록에서는 `txreceipt_status`(1 성공, 0 실패, Byzantium 이전 블록은 빈 값)와 `isError`(0 성공, 1 실패)로 확인합니다[7]. 로그만 모아 흐름을 정리하면 로그를 남기지 않은 실패한 시도가 목록에서 빠질 수 있어서, 계정의 트랜잭션 목록과 `status` 를 함께 봅니다.

체인 재구성으로 블록이 바뀌면 그 블록의 로그는 `removed` 가 `true` 로 옵니다[4]. 최근 블록을 기준으로 받은 로그는 나중에 `finalized` 블록을 기준으로 다시 조회해 남아 있는지 확인합니다.

### 시각

계정 상태와 로그 객체에는 시각 필드가 없습니다[1][4]. 로그와 트랜잭션의 시각은 `blockNumber` 로 블록을 조회해 그 블록의 `timestamp` 를 쓰는데, 이 값은 블록이 만들어진 시각을 유닉스 초로 적은 것입니다[4]. Etherscan txlist·txlistinternal·getLogs 의 `timeStamp` 도 블록 시각이고, getLogs 는 이 값을 헥스 문자열로 줍니다[7][8][13].

지갑 앱은 기기 시계로 적은 시각을 따로 둡니다. MetaMask 의 `submittedTime` 은 트랜잭션을 네트워크에 보낸 시각을 유닉스 밀리초로 적고, `blockTimestamp` 는 블록이 만들어진 시각입니다[10]. `time` 은 트랜잭션에 붙은 시각을 숫자로 적은 값인데 단위와 기준이 정해져 있지 않아서[10], 실제 데이터에서 자릿수(초는 10자리, 밀리초는 13자리)와 블록 시각을 비교해 단위와 기준을 확인합니다. 블록 시각과 확정 개념은 [블록 시각과 확정](block-time.md), 여러 시각을 합쳐 정리하는 방법은 [암호화폐 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정

**`to` 가 받는 사람이 아닐 수 있습니다.** 컨트랙트를 호출하는 트랜잭션의 `to` 는 그 컨트랙트 주소입니다[2]. 토큰 전송이면 `to` 는 토큰 컨트랙트이고 `value` 는 0 일 수 있어서, 트랜잭션 목록만 보면 "컨트랙트로 0 ETH 를 보냈다" 로 잘못 읽습니다. 받는 주소와 금액은 입력 데이터 인자와 로그에서 읽습니다.

**앱이 저장한 잔액은 저장한 때의 값입니다.** iOS MetaMask 앱의 `AccountTrackerController.accounts` 에는 주소별 `balance` 가 있고, iLEAPP 는 이 헥스 값을 10^18 로 나눠 ETH 로 보여 줍니다[11]. 앱이 체인에서 받아 저장해 둔 값이라 분석하는 시점이나 특정 블록의 잔액과 다를 가능성이 있습니다. 체인의 잔액이 필요하면 블록 번호를 정해 `eth_getBalance` 로 다시 조회합니다[4]. 이 값에는 토큰 잔액이 들어 있지 않습니다[1].

**앱 버전마다 필드 이름이 다릅니다.** iLEAPP 의 iOS MetaMask 분석기는 `TransactionController.transactions` 항목의 `time`, `transaction` 안의 `from`·`to`·`value`, `transactionHash` 를 읽습니다[11]. 현재 MetaMask core 의 트랜잭션 기록은 같은 정보를 `txParams` 안의 `from`·`to`·`value` 와 `hash` 로 둡니다[10]. 실제 파일에서 키 이름부터 확인하고, 도구가 빈 값을 내면 키 이름이 다른 것은 아닌지 살펴봅니다. 또 iLEAPP 는 `value` 를 ETH 로만 바꿔서[11], 토큰 전송은 금액 0 으로 보일 수 있습니다.

**`indexed` 문자열은 해시만 남습니다.** 동적 타입을 `indexed` 로 둔 이벤트는 토픽에 해시만 있어서[5], 토픽만 보고 원래 문자열을 적을 수 없습니다. 같은 값을 `indexed` 가 아닌 인자로도 함께 남긴 컨트랙트라면 `data` 에서 읽을 수 있습니다[5].

**내부 호출은 표준 조회로 나오지 않습니다.** 이더리움 JSON-RPC 표준 메서드에는 트랜잭션 안의 내부 호출을 나열하는 메서드가 없습니다[4]. 컨트랙트가 ETH 를 나눠 보내는 흐름은 트랜잭션 목록과 로그만으로는 빠지므로, 내부 호출 목록을 따로 받아 합칩니다[8].

**주소 대소문자는 무시하고 비교합니다.** 같은 주소가 EIP-55 형식, 모두 소문자, 로그 토픽 안의 0 채운 소문자로 따로 나옵니다. 대소문자 규칙은 [주소 형식](../wallets/address-formats.md)에서 다룹니다.

## 도구

**이더리움 JSON-RPC.** `eth_getBalance`·`eth_getTransactionCount`·`eth_getCode` 로 블록 기준 계정 상태를, `eth_getTransactionReceipt` 로 영수증과 로그를 받습니다[4]. `eth_getLogs` 는 `fromBlock`·`toBlock`(기본값 `latest`), 로그를 남긴 `address`(하나 또는 목록), `topics` 로 거릅니다[4]. `topics` 필터는 자리 순서대로 맞추고, 한 자리에 배열을 넣으면 그 자리는 "이 중 하나" 로 맞춥니다[4]. 예를 들어 `[null, B]` 는 첫 토픽은 무엇이든, 둘째 토픽이 B 인 로그를 찾습니다[4]. 특정 주소가 받은 토큰 전송을 찾을 때는 그 주소를 32바이트로 0 채운 값을 받는 사람 토픽 자리에 넣습니다.

**Etherscan API.** txlist(주소의 트랜잭션 목록), txlistinternal(내부 호출 목록), getLogs(컨트랙트 주소와 블록 범위로 로그 조회)가 있습니다[7][8][13]. 제3자가 운영하는 조회 서비스는 어떤 주소를 조사하는지 운영자에게 드러내고, 조회 결과가 정확하고 빠짐없는지 조사하는 쪽에서 보장할 수 없습니다[14]. 그래서 조회한 시각과 기준 블록을 기록해 두고, 중요한 값은 직접 운영하는 노드로 다시 확인합니다[14]. 탐색기 자료를 읽는 방법은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md), 계정 사이 흐름을 따라가는 절차는 [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md)에서 다룹니다.

**함수 선택자 조회.** 4바이트 선택자에서 함수 서명 후보를 찾을 때는 4byte.directory 를 씁니다[2]. 결과는 후보라서 컨트랙트 ABI 로 확인합니다.

**iLEAPP.** iOS MetaMask 앱의 `persist-root` 에서 계정 잔액, 주소록, 트랜잭션, 앱 안 브라우저 기록을 뽑습니다[11].

## 참고 문헌

1. ethereum.org, "Ethereum accounts". https://ethereum.org/en/developers/docs/accounts/
2. ethereum.org, "Transactions". https://ethereum.org/en/developers/docs/transactions/
3. ethereum.org, "Blocks". https://ethereum.org/en/developers/docs/blocks/
4. ethereum.org, "JSON-RPC API". https://ethereum.org/en/developers/docs/apis/json-rpc/
5. Solidity documentation, "Contract ABI Specification — Events". https://docs.soliditylang.org/en/latest/abi-spec.html
6. EIP-20, "Token Standard". https://eips.ethereum.org/EIPS/eip-20
7. Etherscan API, "Get Normal Transactions By Address" (txlist). https://docs.etherscan.io/api-reference/endpoint/txlist.md
8. Etherscan API, "Get Internal Transactions by Address" (txlistinternal). https://docs.etherscan.io/api-reference/endpoint/txlistinternal.md
9. Etherscan API, "eth_getTransactionReceipt". https://docs.etherscan.io/api-reference/endpoint/ethgettransactionreceipt.md
10. MetaMask core, `packages/transaction-controller/src/types.ts`. https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/types.ts
11. iLEAPP, `scripts/artifacts/metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
12. Trust Wallet iOS, `Trust/Transactions/Storage/Transaction.swift`. https://github.com/trustwallet/trust-wallet-ios/blob/master/Trust/Transactions/Storage/Transaction.swift
13. Etherscan API, "Get Event Logs by Address" (getLogs). https://docs.etherscan.io/api-reference/endpoint/getlogs.md
14. Tyler Thomas, Tiffanie Edwards, Ibrahim Baggili, 「BlockQuery: Toward forensically sound cryptocurrency investigation」, Forensic Science International: Digital Investigation 40, 2022, doi:10.1016/j.fsidi.2022.301340
15. EIP-721, "Non-Fungible Token Standard". https://eips.ethereum.org/EIPS/eip-721
