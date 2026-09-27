---
title: "토큰과 NFT"
parent: "기반 · 블록체인 기초"
nav_order: 30
---

# 토큰과 NFT (ERC-20·ERC-721)

이더리움의 토큰은 계정 잔액이 아니라 토큰 컨트랙트 안에 저장되는 숫자이고, 토큰이 옮겨지면 컨트랙트가 `Transfer` 이벤트 로그를 남깁니다. 그래서 토큰 거래는 트랜잭션의 `to`·`value` 가 아니라 영수증의 로그를 읽어야 보낸 주소·받은 주소·금액이 나옵니다. 이 페이지는 대체 가능 토큰 표준(ERC-20)과 대체 불가 토큰 표준(ERC-721)의 함수와 이벤트, 로그를 읽는 방법, 해석할 때 틀리기 쉬운 점을 다룹니다.

## 이 형식을 쓰는 아티팩트

토큰 흔적은 블록체인과 기기 양쪽에 남습니다. 블록체인에서는 토큰 컨트랙트가 남긴 이벤트 로그가 트랜잭션 영수증에 들어 있고, 로그 필드의 일반 구조는 [이더리움의 계정과 로그](ethereum-accounts.md)에서 다룹니다. 블록 탐색기는 이 로그를 모아 주소별 토큰 전송 목록으로 보여 줍니다([블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)).

기기에서는 지갑 앱이 토큰 목록·잔액·전송 기록을 자기 DB 에 저장합니다. iOS 용 Coinbase Wallet 은 `Documents/default/wallet-rn-v2.sqlite` 의 `tx_history_v2` 표에 전송 기록을 두고, 여기에 `tokenName`·`tokenDecimal`·`contractAddress`·`amount` 열이 있습니다[14]. 같은 DB 의 자산별 `wallet` 표는 토큰이면 `contractAddress` 가 채워지고 체인 기본 자산이면 비어 있습니다[14]. 앱별 저장 위치는 [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md), [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md), [MetaMask](../../02-artifacts/browser/metamask/index.md) 페이지에서 다룹니다.

## 구조

### ERC-20 — 대체 가능 토큰

ERC-20 은 2015년 11월 19일에 작성된 EIP-20 이 정한 표준이고, 상태는 Final 입니다[1]. 토큰 하나하나가 서로 같은 가치로 취급되는 토큰(대체 가능 토큰, fungible token)에 씁니다[3]. 컨트랙트가 갖춰야 하는 함수는 아래와 같습니다[1].

| 함수 | 하는 일 |
|---|---|
| `name()` | 토큰 이름을 돌려줍니다. 선택 항목입니다. |
| `symbol()` | 심볼을 돌려줍니다. 선택 항목입니다. |
| `decimals()` | 표시용 소수 자릿수를 돌려줍니다. 선택 항목입니다. |
| `totalSupply()` | 전체 발행량을 돌려줍니다. |
| `balanceOf(address _owner)` | 주소의 잔액을 돌려줍니다. |
| `transfer(address _to, uint256 _value)` | 호출한 계정에서 `_to` 로 보내고 `Transfer` 이벤트를 남깁니다. |
| `transferFrom(address _from, address _to, uint256 _value)` | 허락받은 호출자가 `_from` 의 토큰을 `_to` 로 옮기고 `Transfer` 이벤트를 남깁니다. |
| `approve(address _spender, uint256 _value)` | `_spender` 가 `_value` 까지 여러 번 꺼내 가도록 허락합니다. 다시 부르면 허락 금액을 덮어씁니다. |
| `allowance(address _owner, address _spender)` | 남은 허락 금액을 돌려줍니다. |

`decimals` 는 화면에 보일 금액을 만들 때만 씁니다. 값이 8 이면 저장된 정수를 100,000,000 으로 나눠 표시합니다[1]. 컨트랙트에 저장되는 금액은 언제나 최소 단위의 정수입니다.

이벤트는 두 가지입니다[1].

| 이벤트 | 인자 | 언제 남나 |
|---|---|---|
| `Transfer` | `address indexed _from`, `address indexed _to`, `uint256 _value` | 토큰이 옮겨질 때 반드시 남깁니다. 금액이 0 인 전송도 포함합니다. 새 토큰을 만들 때는 `_from` 을 0x0 으로 둔 `Transfer` 를 남기도록 권장합니다(SHOULD). |
| `Approval` | `address indexed _owner`, `address indexed _spender`, `uint256 _value` | `approve` 호출이 성공할 때마다 남깁니다. |

토큰 소각(burn)은 EIP-20 에 규정이 없습니다[1]. 소각을 어떤 이벤트로 남기는지는 컨트랙트마다 다릅니다.

### ERC-721 — 대체 불가 토큰(NFT)

ERC-721 은 2018년 1월 24일에 작성된 EIP-721 이 정한 표준이고, 상태는 Final 입니다[2]. 컨트랙트 안에서 NFT 하나하나는 `uint256` 번호(`tokenId`)로 구분하고, (컨트랙트 주소, `tokenId`) 쌍이 이더리움 체인 전체에서 그 자산을 유일하게 가리키는 식별자가 됩니다[2]. `tokenId` 는 컨트랙트가 있는 동안 바뀌지 않지만, 0 부터 하나씩 늘어난다는 식의 번호 규칙을 가정하면 안 됩니다[2].

| 이벤트 | 인자 | 언제 남나 |
|---|---|---|
| `Transfer` | `_from`, `_to`, `_tokenId` (셋 다 indexed) | 어떤 방식이든 소유자가 바뀔 때 남깁니다. 발행은 `_from` 이 0, 소각은 `_to` 가 0 입니다. 단, 컨트랙트를 만드는 도중에는 이벤트 없이 NFT 를 몇 개든 만들 수 있습니다. |
| `Approval` | `_owner`, `_approved`, `_tokenId` (셋 다 indexed) | NFT 하나를 옮길 수 있는 주소를 정하거나 다시 확인할 때 남깁니다. `_approved` 가 0 주소면 허락된 주소가 없다는 뜻입니다. |
| `ApprovalForAll` | `address indexed _owner`, `address indexed _operator`, `bool _approved` | 소유자의 NFT 전부를 다룰 운영자(operator)를 켜거나 끌 때 남깁니다. |

함수는 `balanceOf`·`ownerOf`·`safeTransferFrom`(인자 구성이 다른 두 가지)·`transferFrom`·`approve`·`setApprovalForAll`·`getApproved`·`isApprovedForAll` 입니다[2]. NFT 를 옮길 수 있는 주체는 소유자, 그 NFT 에 허락받은 주소, 소유자가 지정한 운영자 셋입니다[2]. 발행(minting)과 소각(burning) 함수는 표준에 들어 있지 않아 컨트랙트마다 이름과 방식이 다릅니다[2].

컨트랙트가 ERC-721 을 구현하는지는 ERC-165 인터페이스 ID `0x80ac58cd` 로 확인하고, 메타데이터 확장은 `0x5b5e139f` 입니다[2]. 메타데이터 확장의 `tokenURI(tokenId)` 는 NFT 마다 다른 URI 를 돌려주고, 이 URI 는 "ERC721 Metadata JSON Schema" 를 따르는 JSON 파일을 가리킬 수 있습니다[2]. 이 스키마에는 `name`·`description`·`image` 필드가 있습니다[2]. 이 URI 는 바뀔 수 있습니다(MAY be mutable)[2].

NFT 가 모두 ERC-721 인 것은 아닙니다. ERC-1155 컨트랙트 하나에는 대체 가능 토큰과 대체 불가 토큰을 여러 종류 함께 담을 수 있고, `safeBatchTransferFrom` 으로 여러 토큰을 한 번에 옮기며, 공급량이 1 인 토큰은 NFT 처럼 다룹니다[5]. 조사 대상 NFT 가 어떤 표준인지는 컨트랙트부터 확인합니다.

### 로그에 들어가는 모양

이벤트 로그는 컨트랙트 주소, 최대 4개의 토픽(topic), 길이가 정해지지 않은 `data` 로 이뤄집니다[6]. `topics[0]` 은 이벤트 이름과 인자 타입을 이은 문자열의 Keccak-256 해시이고, 그 뒤 토픽에는 `indexed` 인자가 순서대로 들어갑니다[6]. 주소처럼 32바이트보다 짧은 값은 앞을 0 으로 채워 32바이트로 들어가고, `indexed` 가 아닌 인자는 `data` 에 ABI 인코딩으로 들어갑니다[6].

ERC-20 과 ERC-721 의 `Transfer` 는 이벤트 서명 문자열이 둘 다 `Transfer(address,address,uint256)` 입니다[1][2][4]. 그래서 `topics[0]` 도 `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef` 로 같고[12][13], 둘은 `indexed` 인자 개수로 구분합니다.

| 항목 | ERC-20 `Transfer` | ERC-721 `Transfer` |
|---|---|---|
| 로그의 `address` | 토큰 컨트랙트 | NFT 컨트랙트 |
| `topics[0]` | `0xddf252ad…b3ef` | 같은 값 |
| `topics[1]` | 보낸 주소(`_from`) | 보낸 주소(`_from`) |
| `topics[2]` | 받는 주소(`_to`) | 받는 주소(`_to`) |
| `topics[3]` | 없음 | `tokenId` |
| `data` | 금액(`_value`), 32바이트 | 비어 있음(`0x`) |

## 읽는 법

토큰 전송은 영수증의 `logs` 배열에서 읽습니다. 아래는 `eth_getTransactionReceipt` 응답 형식[7][13]에 맞춰 만든 예시입니다. `topics[0]` 만 표준 이벤트 서명 해시이고, 주소·금액은 모두 지어낸 값입니다(만든 예시).

```json
{
  "status": "0x1",
  "to": "0x5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e",
  "logs": [
    {
      "address": "0x5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e",
      "topics": [
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
        "0x000000000000000000000000a1b2c3d4e5f60718293a4b5c6d7e8f9012345678",
        "0x0000000000000000000000000badc0de0badc0de0badc0de0badc0de0badc0de"
      ],
      "data": "0x000000000000000000000000000000000000000000000000000000003b9aca00",
      "logIndex": "0x3",
      "removed": false
    }
  ]
}
```

`topics[0]` 이 `Transfer` 서명 해시이고 토픽이 3개라서 ERC-20 전송입니다. `topics[1]` 과 `topics[2]` 의 마지막 20바이트를 떼면 보낸 주소 `0xa1b2…5678` 과 받는 주소 `0x0bad…c0de` 가 나옵니다. `data` 의 `0x3b9aca00` 은 10진수로 1,000,000,000 인 최소 단위 금액입니다. 로그의 `address` 에 있는 컨트랙트의 `decimals()` 가 6 이면 화면에 보일 금액은 1,000 토큰입니다. 트랜잭션의 `to` 는 받는 사람이 아니라 토큰 컨트랙트라는 점도 이 예시로 확인할 수 있습니다[13].

같은 형식에서 토픽이 4개이고 `topics[1]` 이 `0x0000…0000`(64자리 모두 0), `topics[3]` 이 `0x…002a`, `data` 가 `0x` 라면(만든 예시) ERC-721 NFT 발행이고 `tokenId` 는 42 입니다. Etherscan `getLogs` 문서의 응답 예시도 토픽 4개·두 번째 토픽 0·`data` 가 `0x` 인 발행 로그 모양입니다[12].

로그가 아니라 트랜잭션 입력값(input data)에서도 전송 의도를 읽을 수 있습니다. 입력값의 첫 4바이트는 호출한 함수를 나타내는 함수 선택자이고, `0xa9059cbb` 는 `transfer(address,uint256)` 의 선택자입니다[8]. 나머지 인자는 32바이트씩 앞을 0 으로 채워 이어집니다[6][8]. 아래는 명세로 만든 예시입니다.

```text
a9059cbb                                                          함수 선택자 transfer(address,uint256)
0000000000000000000000000badc0de0badc0de0badc0de0badc0de0badc0de  _to
000000000000000000000000000000000000000000000000000000003b9aca00  _value
```

입력값은 "이 함수를 이 인자로 불렀다" 는 기록일 뿐입니다. 실행이 실패한 트랜잭션도 블록에 들어가므로, 실제로 옮겨졌는지는 영수증의 `status` 와 로그로 확인합니다([이더리움의 계정과 로그](ethereum-accounts.md)).

## 포렌식에서 중요한 점

**증명하는 것:** 로그의 `address` 에 있는 컨트랙트가 이 블록·이 트랜잭션에서 `_from` → `_to` 로 이 금액 또는 이 `tokenId` 의 `Transfer` 이벤트를 남겼다는 사실입니다[1][2][6]. 이벤트가 `Approval` 이면 그 시점에 누가 누구에게 얼마까지(또는 어떤 NFT 를) 옮길 권한을 줬는지가 확인됩니다.

**증명하지 못하는 것:** 로그의 토큰 이름·심볼이 진짜 그 자산이라는 사실은 증명하지 못합니다. `name`·`symbol` 은 컨트랙트가 스스로 돌려주는 선택 항목이고[1], 어떤 컨트랙트든 다른 컨트랙트와 같은 이름·심볼을 쓸 수 있습니다[2]. 토큰은 이름이 아니라 컨트랙트 주소로 특정합니다. 컨트랙트가 표준대로 이벤트를 남겼는지도 로그만으로는 알 수 없습니다. 표준은 이벤트를 요구하지만 실제로 남기는 것은 컨트랙트 코드이고, ERC-721 은 컨트랙트를 만드는 도중의 발행에 이벤트를 생략해도 됩니다[1][2]. NFT 의 그림과 설명은 `tokenURI` 가 가리키는 바깥 데이터라서 바뀔 수 있고, 발행 당시의 내용이라는 보장이 없습니다[2].

**잔액의 위치:** 이더리움 계정의 `balance` 필드는 ETH 를 wei 단위로 담을 뿐이고[9], 토큰 잔액은 토큰 컨트랙트의 `balanceOf` 로 조회합니다[1][3]. 계정 잔액이 0 이어도 토큰은 남아 있을 수 있으므로 토큰 컨트랙트마다 따로 조회합니다.

**시각:** 로그에는 시각 필드가 없고, 로그가 들어간 블록의 시각을 씁니다. Etherscan `tokentx` 의 `timeStamp` 는 블록이 채굴된 시각을 유닉스 초로 적은 값입니다[10]. 블록 시각의 기준과 오차는 [블록 시각과 확정](block-time.md)에서 다룹니다. 지갑 앱 DB 의 시각은 앱이 기록을 저장한 시각일 수 있으므로 블록 시각과 따로 봅니다.

**지운 데이터·재구성:** 지갑 앱에서 토큰을 숨기거나 앱을 지워도 블록에 들어간 로그는 노드나 블록 탐색기에서 다시 조회할 수 있습니다. 반대로 체인 재구성(reorg)으로 빠진 로그는 JSON-RPC 응답에서 `removed` 가 `true` 로 나옵니다[7]. 확정 전 블록의 로그를 근거로 쓸 때는 이 필드를 확인합니다.

## 함정

- **트랜잭션 `to`·`value` 를 받는 사람·금액으로 읽는 실수.** 토큰 전송 트랜잭션의 `to` 는 토큰 컨트랙트이고[13], `value` 는 함께 보낸 ETH 양입니다[8]. 실제 수신자와 금액은 로그의 토픽과 `data`, 또는 입력값의 인자에 있습니다.
- **소수 자릿수를 빼먹는 실수.** 로그와 API 의 금액은 최소 단위 정수라서 `10^decimals` 로 나눠야 합니다[1][10]. 지갑 앱도 변환하지 않고 저장할 수 있습니다. Coinbase Wallet 은 금액·수수료·가스를 자산별 최소 단위 그대로 저장하고 자릿수는 `tokenDecimal` 열에 따로 둡니다[14].
- **ERC-20 과 ERC-721 을 섞는 실수.** `topics[0]` 이 같으므로 `topics[0]` 만으로 걸러 내면 두 표준의 전송이 함께 나옵니다. 토픽 개수와 `data` 길이로 구분합니다.
- **권한 부여를 이동으로 읽는 실수.** `Approval` 과 `ApprovalForAll` 은 옮길 권한을 준 기록이지 이동이 아닙니다[1][2]. 반대로 권한을 받은 주소가 나중에 `transferFrom` 으로 옮기면 `Transfer` 로그의 `_from` 은 피해자 주소인데 트랜잭션을 보낸 계정은 권한을 받은 쪽입니다. 이 흐름은 [피싱 사이트에 서명했나](../../04-scenarios/fraud/wallet-drainer.md)에서 이어 다룹니다.
- **탐색기 목록의 `from` 뜻.** Etherscan `tokentx` 결과의 `from` 은 "트랜잭션을 보낸 주소" 로 정의돼 있어서[10], 트랜잭션 발신자인지 `Transfer` 이벤트의 `_from` 인지 이 정의로는 구분되지 않습니다. 결론에 쓰기 전에 영수증의 `topics[1]` 과 맞춰 봅니다.
- **NFT 목록의 모양 차이.** Etherscan `tokennfttx` 는 금액 대신 `tokenID` 를 돌려주고, 응답 예시의 `tokenDecimal` 은 `"0"` 입니다[11].
- **함수 선택자의 중복.** 4바이트 선택자 하나에 이름이 다른 함수 여러 개가 대응할 수 있습니다[8]. 선택자로 함수 이름을 추정했다면 검증된 컨트랙트 소스나 로그로 다시 확인합니다.
- **토큰 컨트랙트 주소로 보낸 전송.** ERC-20 에는 받는 컨트랙트에 알리는 장치가 없어서, 토큰을 처리하지 못하는 컨트랙트(토큰 컨트랙트 자신 포함)로 보낸 토큰은 꺼낼 수 없게 될 수 있습니다[3]. `_to` 가 컨트랙트 주소인 전송은 실수로 보낸 것일 가능성도 함께 봅니다.

## 도구

- **JSON-RPC:** `eth_getTransactionReceipt` 로 영수증의 로그를, `eth_getLogs` 로 여러 블록의 로그를 가져옵니다. `eth_getLogs` 의 `topics` 필터는 자리 순서대로 맞추고, 한 자리에 여러 값을 배열로 넣으면 그중 하나와 맞는 로그를 돌려줍니다[7]. `topics` 첫 자리에 `Transfer` 서명 해시를 넣고 둘째 자리에 조사 주소(32바이트로 채운 값)를 넣으면 그 주소가 보낸 전송만, 셋째 자리에 넣으면(둘째 자리는 `null`) 받은 전송만 추립니다[7].
- **Etherscan API:** `tokentx`(ERC-20 전송), `tokennfttx`(ERC-721 전송), `getLogs`(주소별 이벤트 로그)[10][11][12]. `tokentx` 결과에는 `contractAddress`·`value`·`tokenName`·`tokenSymbol`·`tokenDecimal`·`blockNumber`·`timeStamp`·`hash` 등이 있습니다[10].
- **web3.py 예제:** ethereum.org 의 ERC-20·ERC-721 문서에 `decimals()`·`balanceOf()` 호출과 `Transfer(address,address,uint256)` 해시로 로그를 거르는 예제가 있습니다[3][4].
- **함수 선택자 조회:** 4byte.directory 에서 선택자에 대응하는 함수 이름 후보를 찾습니다[8].
- **기기 쪽:** iLEAPP 의 Coinbase Wallet 분석기는 `tx_history_v2` 의 금액·토큰 이름·자릿수·컨트랙트 주소를 단위 변환 없이 저장된 그대로 보여 줍니다[14].

로그로 자금 흐름을 여러 단계 따라가는 방법은 [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md), 주소 문자열의 형식과 체크섬은 [주소 형식](../wallets/address-formats.md)에서 다룹니다.

## 참고 문헌

1. Fabian Vogelsteller, Vitalik Buterin, "ERC-20: Token Standard", EIP-20. https://eips.ethereum.org/EIPS/eip-20
2. William Entriken, Dieter Shirley, Jacob Evans, Nastassia Sachs, "ERC-721: Non-Fungible Token Standard", EIP-721. https://eips.ethereum.org/EIPS/eip-721
3. ethereum.org, "ERC-20 Token Standard". https://ethereum.org/en/developers/docs/standards/tokens/erc-20/
4. ethereum.org, "ERC-721 Non-Fungible Token Standard". https://ethereum.org/en/developers/docs/standards/tokens/erc-721/
5. ethereum.org, "ERC-1155 Multi-Token Standard". https://ethereum.org/en/developers/docs/standards/tokens/erc-1155/
6. Solidity 문서, "Contract ABI Specification" (Events 절). https://docs.soliditylang.org/en/latest/abi-spec.html
7. ethereum.org, "JSON-RPC API". https://ethereum.org/en/developers/docs/apis/json-rpc/
8. ethereum.org, "Transactions" (The data field 절). https://ethereum.org/en/developers/docs/transactions/
9. ethereum.org, "Ethereum Accounts". https://ethereum.org/en/developers/docs/accounts/
10. Etherscan API 문서, "Get ERC20 Token Transfers by Address" (tokentx). https://docs.etherscan.io/api-reference/endpoint/tokentx.md
11. Etherscan API 문서, "Get ERC721 Token Transfers by Address" (tokennfttx). https://docs.etherscan.io/api-reference/endpoint/tokennfttx.md
12. Etherscan API 문서, "Get Event Logs by Address" (getLogs). https://docs.etherscan.io/api-reference/endpoint/getlogs.md
13. Etherscan API 문서, "eth_getTransactionReceipt". https://docs.etherscan.io/api-reference/endpoint/ethgettransactionreceipt.md
14. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
