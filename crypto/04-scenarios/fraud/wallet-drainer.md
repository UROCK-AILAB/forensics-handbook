---
title: "피싱 사이트에 서명했나"
parent: "시나리오 · 사기"
nav_order: 400
---

# 피싱 사이트에 서명했나 (Wallet Drainer)

지갑 드레이너(wallet drainer)는 가짜 dApp 사이트가 사용자에게 서명을 받아 내고, 그 서명으로 얻은 권한으로 나중에 토큰과 NFT 를 옮겨 가는 사기입니다. 개인 키가 새지 않아도 피해가 나고, 서명한 시각과 자산이 빠져나간 시각이 몇 주씩 벌어질 수 있습니다. 이 페이지는 피해자 기기의 지갑 기록에서 사이트와 서명 종류를 찾고, 블록체인에서 권한이 넘어간 기록과 실제로 자산을 옮긴 트랜잭션을 찾아 서로 맞추는 순서를 다룹니다.

## 조사 질문

- 피해자가 어느 사이트(origin)에 지갑을 연결했고, 그 사이트에서 무엇에 서명했는가. 체인에 올라간 트랜잭션인가, 체인 밖에서 만든 서명(오프체인 서명)인가.
- 그 결과 누구에게(spender·operator) 어떤 권한이 넘어갔는가.
- 언제, 누가 그 권한으로 자산을 옮겼는가.

## 먼저 확인할 것

피해 계정이 어느 지갑에 있었는지부터 정리합니다. 브라우저 확장 지갑이면 브라우저와 프로필, 모바일 지갑이면 앱과 OS 버전, 하드웨어 지갑을 연결해 썼는지를 적습니다. MetaMask 에 연결한 Ledger·Trezor 계정은 데이터 서명을 `personal_sign` 으로만 할 수 있어서[16], 같은 MetaMask 안에서도 계정마다 받을 수 있는 서명 요청이 다릅니다.

다음으로 피해 주소와 체인을 확정합니다. 드레이너는 토큰 컨트랙트마다 따로 권한을 받으므로, 피해 주소가 어느 체인에서 어떤 토큰과 NFT 를 갖고 있었는지 목록이 있어야 뒤 단계에서 빠진 것 없이 찾을 수 있습니다. Permit2 서명은 서명한 계정에만 적용되므로[17], 같은 지갑의 다른 계정은 따로 판단합니다.

시간대와 시계 오차도 기록합니다. 지갑 앱의 시각은 기기 시계로 남고 블록체인 기록은 블록 시각으로 남아서, 둘을 한 타임라인에 올리려면 기준을 맞춰야 합니다. 마지막으로 피해자가 받은 링크(메신저·메일·SNS 광고)와 피해 뒤 한 조치(연결 끊기, 승인 철회, 지갑 재설치)를 물어 둡니다. 재설치나 초기화를 했다면 기기 쪽 기록이 사라졌을 수 있습니다.

## 권한을 넘기는 방식 네 가지

드레이너가 받아 내는 서명은 체인에 남는 방식과 남지 않는 방식으로 나뉘고, 이에 따라 찾을 곳이 달라집니다.

**온체인 승인 트랜잭션.** ERC-20 `approve(address _spender, uint256 _value)` 는 `_spender` 가 `_value` 까지 여러 번 꺼내 가도록 허락하고, 성공하면 반드시 `Approval` 이벤트를 남깁니다[1]. NFT 는 `setApprovalForAll(address _operator, bool _approved)` 로 소유자의 NFT 전부를 다룰 운영자를 지정하고 `ApprovalForAll` 이벤트를 남기는데, ERC-721 과 ERC-1155 가 같은 이름과 인자를 씁니다[2][3]. 피해자가 직접 서명해 보낸 트랜잭션이라 `from` 이 피해자 주소입니다. 함수와 이벤트의 모양은 [토큰과 NFT](../../01-foundations/blockchain/tokens.md)에 있습니다. 승인은 흔히 무제한으로 요청되고, 철회도 온체인 트랜잭션이라 가스가 듭니다[18].

**EIP-2612 permit 서명.** 토큰이 `permit` 을 지원하면 사용자는 트랜잭션 대신 EIP-712 구조화 데이터[4] 형식의 `Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)` 메시지에 서명합니다[5]. 누군가 이 서명을 `permit(owner, spender, value, deadline, v, r, s)` 로 제출하면 허용량이 `value` 로 바뀌고 `nonces[owner]` 가 1 늘며 `Approval` 이벤트가 나옵니다[5]. 명세가 `msg.sender` 를 보지 않아 제출자는 아무 주소나 될 수 있으므로[5], permit 트랜잭션의 `from` 은 피해자가 아닐 수 있습니다. `deadline` 을 `uint(-1)` 로 두면 사실상 만료되지 않고, DAI 식 permit 은 `value` 대신 bool `allowed`, `deadline` 대신 `expiry` 를 서명합니다[5].

**Uniswap Permit2 서명.** Permit2 를 쓰려면 사용자가 토큰마다 한 번 Permit2 컨트랙트에 ERC-20 승인을 해 둬야 하고, 이 승인은 흔히 최대값입니다[14]. 그 뒤 dApp 은 오프체인 서명만 받습니다. Permit2 주소는 zkSync 를 뺀 Uniswap 지원 체인 모두에서 `0x000000000022D473030F116dDEE9F6B43aC78BA3` 입니다[14]. 기능은 두 가지입니다. AllowanceTransfer 는 금액과 만료 시각이 있는 허용량을 Permit2 안에 저장하고, spender 는 다 쓰거나 만료될 때까지 여러 번 꺼내 갑니다[14]. SignatureTransfer 는 서명 하나로 한 번만 옮기고 허용량을 남기지 않습니다[14]. EIP-712 domain 은 `EIP712Domain(string name,uint256 chainId,address verifyingContract)` 이고 name 은 `Permit2` 입니다[15]. 서명 메시지의 최상위 타입은 AllowanceTransfer 가 `PermitSingle`·`PermitBatch`, SignatureTransfer 가 `PermitTransferFrom`·`PermitBatchTransferFrom`·`PermitWitnessTransferFrom`·`PermitBatchWitnessTransferFrom` 입니다[15].

**EIP-7702 위임.** 트랜잭션 유형 `0x04` 는 `authorization_list` 에 담긴 서명으로 계정 코드를 `0xef0100` 뒤에 위임 대상 컨트랙트 주소를 붙인 값(위임 표시)으로 바꿉니다[7]. 위임 대상 주소가 0 이면 위임을 지웁니다[7]. 잘못 만든 위임 컨트랙트는 악의적인 사람이 서명자 계정을 거의 완전히 장악하게 할 수 있습니다[7]. 이 권한은 토큰 허용량이 아니라 계정 코드에 남으므로 허용량 조회로는 보이지 않고, 계정 코드를 따로 봐야 합니다.

서명 형식은 앞 바이트로 구분합니다. EIP-191 서명 데이터는 `0x19` 로 시작하고, 다음 한 바이트가 `0x00`(검증자 지정), `0x01`(EIP-712 구조화 데이터), `0x45`(`personal_sign`)입니다[6]. `0x19` 로 시작하는 값은 하나의 RLP 구조가 될 수 없어서, EIP-191 서명 데이터는 이더리움 트랜잭션이 될 수 없습니다[6]. MetaMask 는 `eth_signTypedData_v4`(EIP-712)와 `personal_sign` 을 지원하고 `eth_sign` 은 폐지했습니다[16]. NFT 마켓의 일괄 등록 서명도 같은 방식으로 악용됩니다. 가짜 Blur 사이트가 일괄 등록용 'Root' 메시지 서명을 받아 NFT 전부를 옮겨 간 사례가 있습니다[17].

아래 선택자와 `topics[0]` 은 명세의 함수·이벤트 서명 문자열을 Keccak-256 으로 계산한 값입니다. 트랜잭션 입력 데이터의 앞 4바이트와 로그의 첫 토픽을 이 값과 대조합니다.

| 이름 | 종류 | 값 |
|---|---|---|
| `approve(address,uint256)` | 함수 선택자 | `0x095ea7b3` |
| `increaseAllowance(address,uint256)` | 함수 선택자 | `0x39509351` |
| `setApprovalForAll(address,bool)` | 함수 선택자 | `0xa22cb465` |
| `transferFrom(address,address,uint256)` | 함수 선택자 | `0x23b872dd` |
| `safeTransferFrom(address,address,uint256)` | 함수 선택자 | `0x42842e0e` |
| `permit(address,address,uint256,uint256,uint8,bytes32,bytes32)` (EIP-2612) | 함수 선택자 | `0xd505accf` |
| Permit2 `permit(address,((address,uint160,uint48,uint48),address,uint256),bytes)` | 함수 선택자 | `0x2b67b570` |
| Permit2 `permitTransferFrom(((address,uint256),uint256,uint256),(address,uint256),address,bytes)` | 함수 선택자 | `0x30f28b7a` |
| Permit2 `transferFrom(address,address,uint160,address)` | 함수 선택자 | `0x36c78516` |
| `Approval(address,address,uint256)` | 이벤트 `topics[0]` | `0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925` |
| `ApprovalForAll(address,address,bool)` | 이벤트 `topics[0]` | `0x17307eab39ab6107e8899845ad3d59bd9653f200f220920489ca2b5937696c31` |
| `Transfer(address,address,uint256)` | 이벤트 `topics[0]` | `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef` |
| Permit2 `Permit(address,address,address,uint160,uint48,uint48)` | 이벤트 `topics[0]` | `0xc6a377bfc4eb120024a8ac08eef205be16b817020812c73223e81d1bdb9708ec` |
| Permit2 `Approval(address,address,address,uint160,uint48)` | 이벤트 `topics[0]` | `0xda9fa7c1b00402c17d0161b249b1ab8bbec047c5a52207b9c112deffd817036b` |
| Permit2 `Lockdown(address,address,address)` | 이벤트 `topics[0]` | `0x89b1add15eff56b3dfe299ad94e01f2b52fbcb80ae1a3baea6ae8c04cb2b98a4` |

Permit2 의 `Approval` 은 인자가 5개라서 ERC-20 `Approval` 과 `topics[0]` 이 다릅니다. Permit2 의 `Permit`·`Approval`·`Lockdown` 은 AllowanceTransfer 쪽 이벤트이고, SignatureTransfer 에는 nonce 무효화 이벤트만 있어서 전송 자체는 토큰 컨트랙트의 `Transfer` 이벤트로만 남습니다[15][1]. 선택자는 함수 이름과 인자 타입으로만 정해지므로 같은 선택자를 가진 다른 함수가 있을 수 있고, 검증된 소스와 비교해 확인해야 합니다[8].

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 피해자가 받은 링크 | 메신저·메일·SNS 로 받은 피싱 사이트 주소와 받은 시각 | [피싱 링크를 눌렀나](https://urock-ailab.github.io/forensics-handbook/network/04-scenarios/user-activity/phishing-click.html), [카카오톡 (Android)](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/messengers/kakaotalk/), [텔레그램 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/messengers/telegram.html) |
| 2 | 브라우저 방문 기록 | 피싱 사이트에 들어간 시각과 주소 | [크롬 계열 브라우저 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/), [사파리 (iOS)](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/browsers/safari/) |
| 3 | MetaMask 권한 기록 | 지갑을 연결한 사이트, 계정을 보여 준 시각 | 아래 "피해자 기기의 기록", [MetaMask](../../02-artifacts/browser/metamask/index.md) |
| 4 | MetaMask 피싱 경고 예외 목록 | 경고를 보고도 들어간 사이트 | 아래 "피해자 기기의 기록" |
| 5 | MetaMask 트랜잭션 기록 | 사이트가 요청한 승인 트랜잭션, 요청 금액과 최종 금액 | 아래 "피해자 기기의 기록" |
| 6 | 모바일 지갑의 앱 안 브라우저 기록 | 지갑 앱 안에서 연 dApp 주소 | [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md), [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md) |
| 7 | 블록체인의 승인 기록 | 누구에게 얼마까지 권한이 넘어갔나 | [이더리움의 계정과 로그](../../01-foundations/blockchain/ethereum-accounts.md), [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md) |
| 8 | 블록체인의 이동 기록 | 누가 언제 무엇을 어디로 옮겼나 | [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md) |
| 9 | 거래소 입금 기록 | 옮겨 간 자산이 들어간 거래소 | [거래소로 들어갔나](../asset-flow/exchange-deposit.md) |

## 피해자 기기의 기록

MetaMask 확장은 각 컨트롤러 상태 가운데 메타데이터가 `persist: true` 인 필드만 디스크에 씁니다[25]. 드레이너 조사에 쓰는 필드를 이 기준으로 나누면 아래와 같습니다. 저장 위치와 LevelDB 형식은 [MetaMask](../../02-artifacts/browser/metamask/index.md) 페이지에 있습니다.

| 컨트롤러와 필드 | 디스크에 남나 | 내용 |
|---|---|---|
| TransactionController `transactions` | 예 | 트랜잭션 기록(TransactionMeta) 목록[19] |
| TransactionController `submitHistory` | 예 | 네트워크에 제출한 트랜잭션 기록[19] |
| SignatureController `signatureRequests`·`unapprovedPersonalMsgs`·`unapprovedTypedMessages` | 아니오 | `personal_sign`·`eth_signTypedData` 서명 요청[20] |
| PermissionController `subjects` | 예 | 사이트별 현재 권한[22] |
| PermissionLogController `permissionHistory` | 예 | 사이트별 마지막 승인 시각과 보여 준 계정[21] |
| PermissionLogController `permissionActivityLog` | 아니오 | 권한 요청·응답 활동 로그(최대 100건)[21] |
| PhishingController `whitelist`·`whitelistPaths` | 예 | 피싱 경고를 넘기고 들어간 호스트[23] |

**트랜잭션 기록.** TransactionMeta 의 `origin` 은 이 트랜잭션을 요청한 사이트이고, `type` 은 `approve`·`setapprovalforall`·`increaseAllowance`·`transferfrom`·`safetransferfrom` 처럼 호출한 토큰 함수를 나타냅니다[19]. 특별히 분류하지 않은 컨트랙트 호출은 `contractInteraction`, EIP-7702 일괄 실행은 `batch`, 위임 제거는 `revokeDelegation` 입니다[19]. 승인 트랜잭션이면 사이트가 처음 제안한 금액이 `originalApprovalAmount` 에, 사용자가 고친 뒤 확정한 금액이 `finalApprovalAmount` 에 들어갑니다[19]. 이 밖에 보안 검사 결과 `securityAlertResponse`(`reason`·`result_type` 등), 처음 거래하는 상대인지 나타내는 `isFirstTimeInteraction`, EIP-7702 위임 주소 `delegationAddress` 가 있습니다[19]. `status` 가 `rejected` 이면 사용자가 거절한 요청입니다[19].

아래는 필드 이름을 MetaMask/core 코드[19]에 맞춰 만든 예시입니다. 값은 모두 지어낸 것입니다(만든 예시).

```json
{
  "id": "0f3c9e10-1111-4a2b-9c3d-000000000001",
  "chainId": "0x1",
  "origin": "https://claim-airdrop.example",
  "time": 1772418847000,
  "status": "confirmed",
  "type": "approve",
  "txParams": {
    "from": "0x1111111111111111111111111111111111111111",
    "to": "0x2222222222222222222222222222222222222222",
    "data": "0x095ea7b30000000000000000000000003333333333333333333333333333333333333333ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
  },
  "hash": "0xaaaa000000000000000000000000000000000000000000000000000000000001",
  "originalApprovalAmount": "115792089237316195423570985008687907853269984665640564039457584007913129639935",
  "finalApprovalAmount": "115792089237316195423570985008687907853269984665640564039457584007913129639935"
}
```

`txParams.data` 는 명세로 만든 헥스입니다. 앞 4바이트 `0x095ea7b3` 이 `approve` 선택자이고, 다음 32바이트는 앞을 0 으로 채운 spender 주소 `0x3333…3333`, 마지막 32바이트는 모든 비트가 1 인 값, 곧 uint256 최대값입니다[8]. `to` 는 받는 사람이 아니라 토큰 컨트랙트입니다.

트랜잭션 기록은 무한히 쌓이지 않습니다. 기능 플래그 정보가 있으면 보관 한도를 적용하는데, 한도 값이 따로 없으면 40 입니다[19]. 한도를 넘으면 오래된 끝 상태(`confirmed`·`failed`·`dropped`·`rejected`) 트랜잭션부터 빠지고, 같은 nonce·같은 체인·같은 날짜 묶음은 함께 남으며, 승인 전이거나 처리 중인 트랜잭션은 빠지지 않습니다[19]. 기능 플래그 정보가 없으면 목록을 자르지 않습니다[19]. `submitHistory` 의 기본 한도는 100건입니다[19]. 한도를 넘은 뒤라면 몇 주 전 승인 트랜잭션이 목록에 없을 수 있습니다.

**서명 요청은 디스크에 남지 않습니다.** SignatureController 상태 필드는 모두 `persist: false` 라서[20], permit·Permit2·`personal_sign` 서명 요청의 사이트와 내용은 확장 저장소에 쓰이지 않습니다. 이 필드들은 `includeInStateLogs: true` 라서[20], 브라우저를 끄기 전에 사용자가 Settings → Privacy → Download state logs 로 상태 로그 JSON 파일을 내려받았다면 그 파일에는 메모리에 있던 서명 요청이 들어갈 수 있습니다[26]. 이 파일은 MetaMask 개발자가 버그를 재현하려고 사용자에게 요청하는 파일이라[26], 피해 뒤 문의 과정에서 만들었을 수 있으므로 다운로드 폴더를 확인합니다. 서명 요청에는 `messageParams`(`from`·`origin`·`data`), `status`, 예상 자산 변화를 담은 `decodingData.stateChanges` 가 있습니다[20].

**권한 기록.** `permissionHistory` 는 사이트별로 권한 이름 아래 `lastApproved` 와 계정별 시각을 기록합니다[21].

```json
{
  "https://claim-airdrop.example": {
    "eth_accounts": {
      "lastApproved": 1772418790000,
      "accounts": {
        "0x1111111111111111111111111111111111111111": 1772418790000
      }
    }
  }
}
```

위 값은 지어낸 것입니다(만든 예시). `eth_requestAccounts` 요청이 성공하면 `lastApproved` 와 계정별 시각이 함께 기록되고, 이후 계정 목록을 갱신할 때는 계정별 "마지막으로 본 시각" 만 바뀝니다[21]. 이 컨트롤러 코드에는 `permissionHistory` 를 지우는 경로가 없습니다[21]. 반면 PermissionController 의 `subjects` 는 권한을 철회하면 그 권한을 지우고, 남은 권한이 없으면 사이트 항목 자체를 지웁니다[22]. 그래서 피해자가 연결을 끊은 뒤에는 `subjects` 에 없는 사이트가 `permissionHistory` 에는 남아 있을 수 있습니다. `subjects` 의 권한마다 있는 `date` 는 권한을 만든 시각입니다[22].

**피싱 경고 예외 목록.** MetaMask 피싱 경고 페이지에서 사용자가 경고를 넘기고 계속 들어가면 `phishingController.bypass(origin)` 이 불리고, 호스트 이름이 퓨니코드(punycode)로 바뀌어 `whitelist` 배열에 들어갑니다[23][24]. 경로 단위로 차단된 주소였다면 `whitelistPaths` 에 들어갑니다[23]. 이 목록에는 시각 필드가 없어서, 언제 넘겼는지는 브라우저 방문 기록과 맞춰 추정합니다.

**모바일 지갑.** iLEAPP 는 iOS MetaMask 의 `Documents/persistStore/persist-root` 파일에서 앱 안 브라우저 방문 기록(`name`·`url`)을 읽습니다[27]. Trust Wallet iOS 의 옛 공개 코드는 dApp 브라우저 방문 기록을 Realm 에 `History(url, title)` 로 저장하고 `createdAt` 으로 정렬하며, 사용자가 개별 항목이나 전체를 지울 수 있습니다[28]. 공개 코드는 옛 버전이라 현재 앱과 다를 수 있습니다.

## 분석 흐름

1. **사이트를 특정합니다.** 받은 링크, 브라우저 방문 기록, `permissionHistory`·`subjects`, `whitelist`, 트랜잭션 기록의 `origin` 을 사이트 주소 기준으로 한 표에 모읍니다. 네 곳에 같은 사이트가 나오면 "링크를 받았다 → 들어갔다 → 계정을 보여 줬다 → 승인을 요청받았다" 순서가 기록으로 이어집니다. 연결만 해도 주소가 제3자에게 넘어갈 수 있습니다. 2023년 논문의 측정에서는 지갑을 연결한 dApp 616개 가운데 211개가 사용자 지갑 주소를 제3자에게 보냈습니다[29].

2. **기기에 남은 승인 트랜잭션을 찾습니다.** 트랜잭션 기록에서 그 `origin` 의 `approve`·`setapprovalforall`·`increaseAllowance` 와, `contractInteraction` 가운데 입력 데이터 앞 4바이트가 위 표의 승인 선택자인 것을 뽑습니다. `hash` 로 블록체인의 트랜잭션과 영수증을 조회해 `Approval`·`ApprovalForAll` 로그의 spender·operator 를 확인합니다.

3. **체인에서 승인 기록을 피해 주소 기준으로 모읍니다.** JSON-RPC `eth_getLogs` 는 `topics` 를 자리 순서대로 맞춰 거릅니다[9]. `topics` 를 `["0x8c5be1e5…c3b925", "0x000000000000000000000000" + 피해 주소 40자]` 로 주면 피해 주소가 owner 인 ERC-20·ERC-721 `Approval` 로그가, `topics[0]` 을 `ApprovalForAll` 값으로 바꾸면 운영자 지정 로그가 나옵니다. 피해 주소를 32바이트로 채우는 방법은 [이더리움의 계정과 로그](../../01-foundations/blockchain/ethereum-accounts.md)에 있습니다. Etherscan `getLogs` 는 로그를 남긴 컨트랙트 주소와 블록 범위로 거르므로[11], 피해 주소가 가졌던 토큰 컨트랙트마다 조회합니다.

4. **승인 로그를 만든 트랜잭션의 발신자를 봅니다.** 트랜잭션 `from` 이 피해 주소이고 `to` 가 토큰 컨트랙트이면 피해자가 직접 보낸 승인입니다. `from` 이 다른 주소인데 피해 주소가 owner 인 `Approval` 이 나오면 permit 서명이 제출된 흔적일 가능성이 있습니다. 이때 입력 데이터가 `0xd505accf` 로 시작하는지, 또는 다른 컨트랙트 호출 안에서 permit 이 불렸는지 확인합니다. Permit2 를 거쳤다면 Permit2 주소가 남긴 `Permit`·`Approval` 로그를 `topics[1]` 에 피해 주소를 넣어 찾습니다.

5. **자산을 옮긴 트랜잭션을 찾습니다.** 피해 주소가 `_from` 인 `Transfer` 로그를 모으고, 각 로그를 만든 트랜잭션의 `from`·`to`·선택자를 봅니다. 드레이너 경로면 트랜잭션 `from` 은 spender 나 그 운영 주소이고, `to` 는 토큰 컨트랙트(`transferFrom`)나 Permit2(`transferFrom`·`permitTransferFrom`) 또는 드레이너 컨트랙트입니다. Etherscan `tokentx` 로 피해 주소의 ERC-20 이동을 한 번에 뽑을 수도 있지만[13], 결론에 쓰기 전에 영수증의 로그와 맞춥니다([토큰과 NFT](../../01-foundations/blockchain/tokens.md)의 함정 참고).

6. **남은 권한과 위임을 확인합니다.** ERC-20 `allowance(owner, spender)`, NFT `isApprovedForAll(owner, operator)`, Permit2 `allowance(user, token, spender)` 로 조사 시점에 남은 권한을 조회합니다[1][2][15]. 블록 탐색기의 토큰 승인 확인 기능이나 Revoke(revoke.cash) 같은 도구로도 볼 수 있습니다[17][18]. EIP-7702 위임은 `eth_getCode` 로 피해 주소의 코드를 받아[9] `0xef0100` 으로 시작하는지 봅니다[7]. 블록 번호를 지정해 피해 전후 코드를 비교할 수 있습니다.

7. **키 유출과 구분합니다.** 피해 주소가 `from` 인 일반 전송(`transfer`, ETH 송금)으로 자산이 빠졌고 그 앞에 승인·permit 흔적이 없다면, 서명 피싱보다 개인 키나 복구 문구 유출을 먼저 의심합니다. 이 경우는 [악성 코드가 지갑을 노렸나](../device-use/wallet-stealer.md)로 넘어갑니다.

8. **옮겨 간 자산을 따라갑니다.** 받은 주소부터의 흐름은 [빼앗긴 자산은 어디로 갔나](../asset-flow/stolen-funds.md)와 [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md)에서 이어 갑니다.

## 증명하는 것과 증명하지 못하는 것

기기 기록과 체인 기록을 맞추면 증명할 수 있는 것이 있습니다. 트랜잭션 기록에 피싱 사이트 `origin` 과 `approve`·`setapprovalforall` 유형이 있고 그 `hash` 가 체인의 `Approval` 로그와 맞으면, 이 기기의 지갑이 그 사이트의 요청으로 그 spender 에게 승인 트랜잭션을 보냈다는 것이 확인됩니다. `permissionHistory` 에 그 사이트가 있으면 그 사이트에 계정을 보여 준 시각이, `whitelist` 에 있으면 피싱 경고를 넘기고 들어갔다는 사실이 확인됩니다. 체인의 이동 트랜잭션으로는 어느 주소가 언제 무엇을 어디로 옮겼는지 알 수 있습니다.

증명하지 못하는 것도 분명히 적습니다. 오프체인 서명(permit·Permit2·NFT 마켓 서명)을 했다는 사실은 MetaMask 확장의 디스크 상태에 남지 않으므로[20], 기록이 없다고 서명하지 않았다고 할 수 없습니다. 서명 행위는 체인에도 기록되지 않아서[17], 체인에는 공격자가 나중에 제출한 트랜잭션만 있고 서명한 시각은 나오지 않습니다. 서명 메시지의 `deadline`·`sigDeadline` 은 서명을 제출할 수 있는 마지막 시각이고, Permit2 `expiration` 은 허용량이 끝나는 시각일 뿐입니다[5][14][15]. `whitelist` 에는 시각이 없어서 경고를 넘긴 시각은 다른 기록으로 추정해야 합니다[23]. 옮겨 간 자산을 받은 주소가 누구의 것인지도 체인 기록만으로는 알 수 없습니다.

## 시각 맞추기

MetaMask 의 `time`·`submittedTime`, `permissionHistory` 의 시각, 권한 `date` 는 모두 기기 시계 기준 Unix 밀리초입니다[19][21][22]. TransactionMeta 의 `blockTimestamp` 는 블록이 만들어진 시각입니다[19]. Etherscan 은 `txlist` 에서 블록 시각을 10진 Unix 초로, `getLogs` 에서 16진 Unix 초로 줍니다[12][11]. 밀리초와 초, 10진과 16진을 섞지 않도록 UTC 로 바꾼 뒤 한 표에 올립니다. 블록 시각의 성질은 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md), 전체 타임라인 만드는 법은 [암호화폐 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

permit 의 `deadline` 은 블록 시각과 비교하는 값이라[5] 기기 시계와 상관이 없습니다. Permit2 서명은 몇 주 동안 유효하게 만들 수 있고, 그 사이 피해자가 수백 개 사이트를 거치면 원인 사이트를 찾기 어려워집니다[17]. 그래서 이동 트랜잭션 바로 앞의 방문 기록만 보지 말고, 그 서명의 유효 기간이 시작될 수 있는 범위까지 방문 기록과 권한 기록을 넓혀 봅니다.

## 흔한 오판

- **MetaMask 에 서명 기록이 없으니 서명하지 않았다.** 서명 요청은 디스크에 저장되지 않습니다[20].
- **연결을 끊었으니 안전하다.** 연결 끊기는 사이트가 주소와 잔액을 보는 권한 같은 연결 권한을 없애는 것이고, 컨트랙트가 토큰을 옮기는 승인은 온체인 철회 트랜잭션을 보내야 없어집니다[18].
- **permit 트랜잭션의 `from` 이 피해자가 아니니 피해자와 무관하다.** permit 은 누구나 제출할 수 있습니다[5]. 피해자가 보내지 않은 트랜잭션에서 나온 `Approval` 은 탐지 도구에서 의심 항목으로 분류되는데[10], permit 이 바로 이런 모양입니다.
- **`Transfer` 로그의 `_from` 이 피해자이니 피해자가 보냈다.** `transferFrom` 으로 옮기면 `_from` 은 피해자지만 트랜잭션을 보낸 쪽은 권한을 받은 주소입니다. 반대로 사기 토큰은 실제 이동 없이 `Transfer` 이벤트를 낼 수 있습니다[10].
- **Permit2 로그가 없으니 Permit2 는 관련 없다.** SignatureTransfer 로 옮기면 Permit2 고유 이벤트 없이 토큰 `Transfer` 만 남습니다[15].
- **승인 목록 도구에 아무것도 없으니 남은 권한이 없다.** EIP-7702 위임은 계정 코드에 남으므로 계정 코드로 따로 확인합니다[7].
- **트랜잭션 기록에 옛 승인이 없으니 승인한 적이 없다.** 한도를 넘으면 오래된 끝 상태 트랜잭션이 빠집니다[19].
- **선택자만 보고 함수를 단정한다.** 같은 선택자의 다른 함수가 있을 수 있고, Etherscan 의 `functionName` 은 검증된 컨트랙트일 때만 채워집니다[8][12].

## 보고서 문장 예

아래 시각·주소·사이트 주소는 모두 만든 예시입니다.

- "피해자 PC 의 Chrome 기본 프로필 MetaMask 저장소의 `permissionHistory` 에 `https://claim-airdrop.example` 항목이 있고, 계정 A 의 `lastApproved` 값은 2026-03-02 02:33:10 UTC 에 해당한다. (만든 예시)"
- "같은 저장소의 트랜잭션 기록에 `origin` 이 위 사이트이고 `type` 이 `approve` 인 항목이 있으며, 그 `hash` 의 트랜잭션은 이더리움 메인넷 블록 시각 2026-03-02 02:34:23 UTC 에 포함됐다. 영수증의 `Approval` 로그에서 owner 는 계정 A, spender 는 주소 B, 허용량은 uint256 최대값이다. (만든 예시)"
- "주소 B 가 보낸 트랜잭션에서 계정 A 를 `_from` 으로 하는 토큰 `Transfer` 로그가 블록 시각 2026-03-19 11:02:47 UTC 에 있다. 이 기록으로 주소 B 가 계정 A 의 승인을 써서 토큰을 옮겼다는 것은 확인되지만, 주소 B 를 누가 쓰는지는 확인되지 않는다. (만든 예시)"
- "계정 A 가 owner 인 `Approval` 로그 가운데 계정 A 가 보내지 않은 트랜잭션에서 나온 것이 1건 있다. 이는 permit 서명이 제출된 흔적일 가능성이 있으나, 서명한 시각과 서명한 사이트는 기기와 체인 기록으로 확인되지 않는다. (만든 예시)"

보고서 전체 구성은 [암호화폐 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)에 있습니다.

## 함께 볼 페이지

- [투자 사기의 흔적](investment-scam.md) — 사기 사이트로 직접 송금한 경우
- [악성 코드가 지갑을 노렸나](../device-use/wallet-stealer.md) — 개인 키나 볼트가 샌 경우
- [빼앗긴 자산은 어디로 갔나](../asset-flow/stolen-funds.md), [거래소로 들어갔나](../asset-flow/exchange-deposit.md) — 옮겨 간 자산 추적
- [토큰과 NFT](../../01-foundations/blockchain/tokens.md), [이더리움의 계정과 로그](../../01-foundations/blockchain/ethereum-accounts.md) — 승인 함수와 로그 구조
- [MetaMask](../../02-artifacts/browser/metamask/index.md), [다른 확장 지갑](../../02-artifacts/browser/other-extensions.md) — 확장 저장소 위치와 형식
- [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md) — 탐색기 목록을 해석할 때
- [피싱 링크를 눌렀나](https://urock-ailab.github.io/forensics-handbook/network/04-scenarios/user-activity/phishing-click.html), [AI로 피싱·사기 문구를 만들었나](https://urock-ailab.github.io/forensics-handbook/ai/04-scenarios/misuse/phishing.html)

## 참고 문헌

1. ERC-20: Token Standard. https://eips.ethereum.org/EIPS/eip-20
2. ERC-721: Non-Fungible Token Standard. https://eips.ethereum.org/EIPS/eip-721
3. ERC-1155: Multi Token Standard. https://eips.ethereum.org/EIPS/eip-1155
4. EIP-712: Typed structured data hashing and signing. https://eips.ethereum.org/EIPS/eip-712
5. ERC-2612: Permit Extension for EIP-20 Signed Approvals. https://eips.ethereum.org/EIPS/eip-2612
6. ERC-191: Signed Data Standard. https://eips.ethereum.org/EIPS/eip-191
7. EIP-7702: Set Code for EOAs. https://eips.ethereum.org/EIPS/eip-7702
8. ethereum.org, Transactions. https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/transactions/index.md
9. ethereum.org, JSON-RPC API. https://ethereum.org/en/developers/docs/apis/json-rpc/
10. Ori Pomerantz, Some tricks used by scam tokens and how to detect them, ethereum.org, 2023-09-15. https://ethereum.org/en/developers/tutorials/scam-token-tricks/
11. Etherscan, Get Event Logs by Address. https://docs.etherscan.io/api-reference/endpoint/getlogs.md
12. Etherscan, Get Normal Transactions By Address. https://docs.etherscan.io/api-reference/endpoint/txlist.md
13. Etherscan, Get ERC20 Token Transfers by Address. https://docs.etherscan.io/api-reference/endpoint/tokentx.md
14. Uniswap, Permit2 Overview. https://docs.uniswap.org/contracts/permit2/overview
15. Uniswap, permit2 소스 코드 (commit cc56ad0f): src/interfaces/IAllowanceTransfer.sol, src/interfaces/ISignatureTransfer.sol, src/EIP712.sol, src/libraries/PermitHash.sol. https://github.com/Uniswap/permit2/tree/main/src
16. MetaMask, Signing methods. https://docs.metamask.io/wallet/concepts/signing-methods/
17. MetaMask Support, Signature phishing. https://support.metamask.io/stay-safe/protect-yourself/wallet-and-hardware/signature-phishing/
18. MetaMask Support, How to revoke smart contract allowances / token approvals. https://support.metamask.io/more-web3/learn/how-to-revoke-smart-contract-allowances-token-approvals/
19. MetaMask/core, transaction-controller (commit 3f27e120): src/types.ts, src/TransactionController.ts, src/utils/feature-flags.ts. https://github.com/MetaMask/core/tree/main/packages/transaction-controller/src
20. MetaMask/core, signature-controller: src/SignatureController.ts, src/types.ts. https://github.com/MetaMask/core/tree/main/packages/signature-controller/src
21. MetaMask/core, permission-log-controller: src/PermissionLogController.ts, src/enums.ts. https://github.com/MetaMask/core/tree/main/packages/permission-log-controller/src
22. MetaMask/core, permission-controller: src/PermissionController.ts, src/Permission.ts. https://github.com/MetaMask/core/tree/main/packages/permission-controller/src
23. MetaMask/core, phishing-controller: src/PhishingController.ts. https://github.com/MetaMask/core/blob/main/packages/phishing-controller/src/PhishingController.ts
24. MetaMask, metamask-extension app/scripts/metamask-controller.js (commit 74db23ae). https://github.com/MetaMask/metamask-extension/blob/main/app/scripts/metamask-controller.js
25. MetaMask, metamask-extension app/scripts/lib/startup/wire-state-persistence.ts. https://github.com/MetaMask/metamask-extension/blob/main/app/scripts/lib/startup/wire-state-persistence.ts
26. MetaMask, metamask-extension docs/state_dump.md. https://github.com/MetaMask/metamask-extension/blob/main/docs/state_dump.md
27. iLEAPP, scripts/artifacts/metamask.py. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
28. Trust Wallet iOS, Trust/Browser/Storage/HistoryStore.swift, Trust/Core/Types/TrustRealmConfiguration.swift. https://github.com/trustwallet/trust-wallet-ios/blob/master/Trust/Browser/Storage/HistoryStore.swift
29. Christof Ferreira Torres, Fiona Willi, Shweta Shinde, "Is Your Wallet Snitching On You? An Analysis on the Privacy Implications of Web3", arXiv, 2023. doi:10.48550/arXiv.2306.08170
