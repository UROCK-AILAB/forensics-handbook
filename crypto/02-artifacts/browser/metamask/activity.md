---
title: "거래 기록과 연결한 사이트"
parent: "MetaMask"
grand_parent: "아티팩트 · 브라우저 확장 지갑"
nav_order: 180
---

# 거래 기록과 연결한 사이트 (Activity·Connected Sites)

MetaMask 확장은 계정 목록, 주소록, 보낸 거래, 연결을 허락한 사이트를 볼트 밖의 평문 JSON 으로 저장해서, 지갑 비밀번호 없이도 이 설치본이 어떤 주소를 썼고 어느 사이트에 연결했는지 알 수 있습니다[1][3][7][9]. 이 페이지는 그 상태 가운데 계정·거래·연결 기록의 필드와 시각을 읽는 법, 그리고 디스크에 남지 않는 기록을 다룹니다. 상태가 저장되는 파일 위치와 형식은 [저장 위치와 구조](storage.md), 암호화된 부분은 [볼트와 암호화](vault.md)에 있습니다.

## 무엇을 기록하나 · 왜 생기나

MetaMask 는 기능마다 상태를 따로 두는 컨트롤러 (controller) 로 나뉘고, 저장소에는 컨트롤러 이름이 최상위 키로 들어갑니다. 컨트롤러마다 필드별로 디스크에 쓸지(`persist`)와 사용자가 내려받는 상태 로그에 넣을지(`includeInStateLogs`)를 정해 두는데, 이 페이지에서 다루는 필드 가운데 디스크에 남는 것은 모두 `persist: true` 입니다[1][2][3][7][9][10].

| 컨트롤러 | 필드 | 알려 주는 것 | 디스크 저장 |
|---|---|---|---|
| `AccountsController` | `internalAccounts` | 계정 주소·이름·키링 종류·들어온 시각·선택한 시각 | 저장[1] |
| `AddressBookController` | `addressBook` | 사용자가 저장한 상대 주소와 이름·메모 | 저장[2] |
| `TransactionController` | `transactions` | 지갑에서 만든 거래와 상태·해시·요청한 사이트 | 저장[3] |
| `TransactionController` | `submitHistory` | 네트워크로 보낸 거래와 보낸 RPC 주소 | 저장[3] |
| `TransactionController` | `methodData` | 호출 데이터 앞 4바이트별 함수 이름 | 저장[3] |
| `PermissionController` | `subjects` | 지금 권한이 있는 사이트와 권한 내용 | 저장[7] |
| `PermissionLogController` | `permissionHistory` | 사이트별 마지막 허락 시각, 주소별 마지막 노출 시각 | 저장[9] |
| `SubjectMetadataController` | `subjectMetadata` | 사이트 이름·아이콘 주소·종류 | 저장[10] |
| `PermissionLogController` | `permissionActivityLog` | 사이트 요청 하나하나의 요청·응답 시각 | 저장 안 함[9] |
| `SignatureController` | `signatureRequests` 등 | 서명 요청 | 저장 안 함[6] |

사이트와 지갑이 연결되는 흐름을 알면 이 기록이 생기는 순서를 알 수 있습니다. 사용자가 탈중앙 앱 (DApp) 의 "연결" 단추를 누르면 사이트가 지갑에 권한을 요청하고, 지갑이 팝업으로 사용자에게 묻고, 사용자가 허락하면 지갑 주소를 사이트에 돌려줍니다[16]. 이때 `subjects` 에 권한이, `permissionHistory` 에 허락 시각이 들어갑니다[7][9]. 그 뒤 사이트가 거래를 요청하면 `transactions` 에 그 사이트의 원점 (origin, `https://예시.com` 형식의 사이트 식별 문자열) 이 붙은 항목이 생기고, 사용자가 승인해 네트워크로 보내면 `submitHistory` 에도 한 줄이 더해집니다[3][4]. 서명은 지갑이 직접 하고, 블록 번호 조회 같은 요청은 RPC 제공자에게 넘깁니다[16].

## 위치와 버전별 차이

이 필드들은 모두 확장 상태 저장소 안에 있습니다. Chrome 계열은 프로필의 `Local Extension Settings` 아래 확장 ID 폴더(LevelDB), Firefox 는 확장 저장용 IndexedDB 에 있고, 옛 저장 방식(`data` 키 하나에 전체 상태)과 새 방식(컨트롤러마다 최상위 키)이 기기마다 다를 수 있습니다. 경로와 방식 판별은 [저장 위치와 구조](storage.md)를 봅니다.

필드 이름은 판과 제품에 따라 다릅니다. 현재 MetaMask 코어 코드는 계정을 `AccountsController.internalAccounts` 에, 거래의 보낸 주소를 `txParams.from` 에, 해시를 `hash` 에 둡니다[1][4]. iOS 앱을 읽는 iLEAPP 분석기는 `AccountTrackerController.accounts`, `PreferencesController.identities`, `transactions[].transaction.from`, `transactionHash` 를 읽습니다[15]. 그래서 도구가 빈 결과를 내면 필드 이름이 달라서일 수 있으니 원본 JSON 에서 최상위 키부터 직접 확인합니다. 모바일 앱의 저장 구조는 [iOS 지갑 앱](../../mobile/ios-wallets.md)에 있습니다.

사용자가 설정(Settings)의 개인 정보(Privacy) 메뉴에서 "상태 로그 다운로드 (Download state logs)" 를 누르면 JSON 파일 하나가 내려받아집니다[17]. 이 파일은 개발자가 버그를 재현하려고 사용자에게 요청하는 것이라 버그 보고(이슈)에 첨부되기도 하고, 사용자가 보내기 전에 계정 주소를 다른 주소로 바꿔 익명화했을 수 있습니다[17]. 컨트롤러 메타데이터는 상태 로그에 넣을 필드를 `includeInStateLogs` 로 표시하는데, 디스크에 저장하지 않는 `permissionActivityLog` 와 서명 요청 필드도 `includeInStateLogs: true` 입니다[6][9]. 그래서 다운로드 폴더나 버그 보고 첨부에서 이 파일을 찾으면 디스크 상태에 없는 요청 기록을 볼 수 있을 가능성이 있습니다.

## 구조

### 계정과 주소록

`internalAccounts` 는 `accounts`(계정 id 를 키로 한 객체)와 `selectedAccount`(지금 선택한 계정 id) 두 필드로 되어 있습니다[1]. 일반 계정의 id 는 주소에서 만든 UUID 라서, 같은 주소는 설치본이 달라도 id 가 같습니다[1].

| 필드 (`accounts[id].metadata`) | 뜻 | 값 |
|---|---|---|
| `name` | 계정 이름. 사용자가 바꾸지 않았으면 "키링 종류 이름 + 번호(1부터)" 형식 | 문자열[1] |
| `keyring.type` | 키링 종류(복구 문구, 가져온 개인 키, 하드웨어 등) | 문자열[1] |
| `importTime` | 이 계정이 이 설치본의 계정 목록에 처음 들어온 때 | 밀리초[1] |
| `lastSelected` | 사용자가 이 계정을 마지막으로 선택한 때. 선택한 적 없으면 `0` | 밀리초[1] |
| `nameLastUpdatedAt` | 이름을 바꾼 때. 바꾼 적 없으면 없음 | 밀리초[1] |

`keyring.type` 으로 볼트를 열지 않고도 그 주소가 복구 문구에서 나왔는지, 따로 가져온 개인 키인지, 하드웨어 지갑과 연동한 것인지를 구분할 수 있습니다. 키링 종류 문자열은 [볼트와 암호화](vault.md)에 있습니다.

주소록은 `addressBook` 아래 체인 ID → 주소 → 항목의 세 단계 객체이고, 항목에는 `address`, `name`, `chainId`, `memo`, `isEns`, `addressType`, `lastUpdatedAt` 이 있습니다[2]. `lastUpdatedAt` 은 항목을 추가하거나 고칠 때 `Date.now()` 로 쓰는 밀리초 값입니다[2]. 주소록 이름과 메모는 사용자가 직접 입력한 값이라 상대를 누구로 알고 있었는지 확인하는 데 씁니다.

### 거래 (`transactions`)

`transactions` 는 거래 메타데이터 (`TransactionMeta`) 객체의 배열입니다[3]. 분석에 쓰는 필드는 다음과 같습니다[4].

| 필드 | 뜻 |
|---|---|
| `id` | 지갑 안의 거래 식별자 |
| `chainId` | 체인 ID(16진 문자열) |
| `networkClientId` | 거래를 보낸 네트워크 설정의 식별자 |
| `origin` | 거래를 요청한 원점 |
| `status` | 거래 상태(아래 표) |
| `time` | 거래 항목을 만든 때 |
| `submittedTime` | 네트워크로 보낸 때 |
| `hash` | 트랜잭션 해시(16진 문자열) |
| `txParams` | 보낸 주소·받는 주소·금액·호출 데이터 등 거래 내용 |
| `rawTx` | 서명한 트랜잭션 원본(16진) |
| `type` | 거래 종류 |
| `blockNumber`, `blockTimestamp` | 포함된 블록 번호와 블록 시각(문자열) |
| `txReceipt` | 거래 영수증 |
| `deviceConfirmedOn` | 승인한 기기: `metamask_extension`, `metamask_mobile`, `other_device` |
| `isExternalSign` | 서명을 지갑 밖에서 했는지 |
| `replacedBy`, `replacedById` | 이 거래를 밀어낸 거래의 해시와 id |
| `error` | 처리 중 생긴 오류 |

`origin` 이 없는 거래는 승인 창에 `metamask` 를 출처로 표시합니다[3][18]. 따라서 `origin` 에 원점이 있으면 사이트가 요청한 거래이고, 비어 있거나 `metamask` 이면 지갑 화면에서 만든 거래일 가능성이 큽니다.

`txParams` 에는 `from`, `to`, `value`, `data`, `nonce`, `gas`·`gasLimit`, `gasPrice`, `maxFeePerGas`, `maxPriorityFeePerGas`, `chainId`, `type` 등이 들어갑니다[4]. `value` 는 wei 단위이고(1 ETH = 10^18 wei), `nonce` 는 보낸 계정의 거래 순번입니다[13]. 컨트랙트를 부르는 거래는 `data` 의 첫 4바이트가 부를 함수를 가리키고[13], 지갑은 이 4바이트별 함수 이름을 `methodData` 에 모아 둡니다[3]. 필드의 체인 쪽 뜻은 [이더리움의 계정과 로그](../../../01-foundations/blockchain/ethereum-accounts.md)와 [토큰과 NFT](../../../01-foundations/blockchain/tokens.md)에 있습니다.

`status` 값은 다음과 같습니다[4].

| 값 | 뜻 | 마지막 상태 |
|---|---|---|
| `unapproved` | 사용자 승인 전 | 아님 |
| `approved` | 승인했지만 아직 서명 전 | 아님 |
| `signed` | 서명해서 보내는 중 | 아님 |
| `submitted` | 네트워크로 보냈고 확정을 기다리는 중 | 아님 |
| `confirmed` | 체인에서 실행되어 확정됨 | 예 |
| `failed` | 체인에서 실행하다 실패함 | 예 |
| `dropped` | 다른 거래로 대체되어 버려짐 | 예 |
| `rejected` | 사용자가 거절함 | 예 |
| `cancelled` | 더는 쓰지 않는 값 | — |

`rejected` 항목은 사이트가 거래를 요청했지만 사용자가 거절한 흔적이라, 체인에는 없고 이 기기에만 남습니다.

### 보낸 기록 (`submitHistory`)

`submitHistory` 는 네트워크로 보낸 거래마다 한 줄씩 쌓는 목록이고, 항목 필드는 `chainId`, `hash`, `networkType`, `networkUrl`, `origin`, `rawTransaction`, `time`, `transaction`, `migration` 입니다[4]. `networkUrl` 은 거래를 보낸 RPC 주소이고, 옛 데이터를 옮기면서 만든 항목(`migration: true`)은 확정할 수 없어 후보 주소 배열이 들어갑니다[4]. 새 항목은 맨 앞에 넣고, 한도(기본 100건)에 닿으면 가장 오래된 항목을 뺍니다[3][5].

### 연결한 사이트

`PermissionController.subjects` 는 원점을 키로 하고, 그 안에 `origin` 과 권한 이름별 권한 객체(`permissions`)를 둡니다[7]. 권한 객체의 필드는 다음과 같습니다[8].

| 필드 | 뜻 |
|---|---|
| `id` | 권한 객체 식별자(무작위 문자열) |
| `parentCapability` | 권한 이름(JSON-RPC 메서드 이름 등) |
| `invoker` | 권한을 받은 원점 |
| `caveats` | 제약 목록 또는 `null`. 계정 제약(`restrictReturnedAccounts`)이면 사이트에 보여 줄 주소 목록이 값으로 들어감 |
| `date` | 권한을 만든 때(유닉스 기준 밀리초) |

권한 이름과 제약 모양은 판에 따라 달라질 수 있으므로, 실제 데이터에서 `parentCapability` 와 `caveats` 를 열어 어떤 주소가 허락됐는지 확인합니다.

`PermissionLogController.permissionHistory` 는 원점 → 권한 이름 → `{lastApproved, accounts}` 모양입니다[9]. `lastApproved` 는 그 권한을 마지막으로 허락한 때이고, `eth_accounts` 항목의 `accounts` 는 주소를 키로 "그 사이트에 이 주소를 마지막으로 보여 준 때" 를 값으로 둡니다[9]. 사용자가 계정을 바꿔 사이트에 새 계정이 알려질 때마다 확장이 주소별 시각을 `Date.now()` 로 고치지만 `lastApproved` 는 그대로 둡니다[9][12]. 새 기록은 기존 기록과 합쳐지고 컨트롤러 코드에는 이 기록을 지우는 부분이 없어서, 연결을 끊어 `subjects` 에서 사라진 원점도 `permissionHistory` 에는 남아 있을 가능성이 있습니다[9].

`SubjectMetadataController.subjectMetadata` 는 원점별로 `origin`, `name`, `iconUrl`, `extensionId`, `subjectType` 을 둡니다[10]. `subjectType` 은 `website`, `extension`, `internal`, `snap` 같은 값입니다[10]. 권한이 없는 원점은 확장이 시작할 때 잘라 내고, 실행 중에는 권한 없는 원점을 100개까지만 기억해서 넘치면 먼저 들어온 것부터 지웁니다[10][11]. 그래서 연결하지 않고 스쳐 간 사이트의 이름·아이콘은 오래 남지 않습니다.

## 증거로서 의미

### 증명하는 것

- `internalAccounts` 에 있는 주소는 이 브라우저 프로필의 MetaMask 설치본이 계정으로 관리한 주소입니다[1].
- `subjects` 또는 `permissionHistory` 에 있는 원점은 이 설치본에서 연결 권한을 허락한 적이 있는 사이트입니다[7][9].
- `transactions` 나 `submitHistory` 에 `hash` 가 있으면 그 거래를 이 설치본에서 만들었거나 네트워크로 보냈습니다[3][4]. `rawTx`·`rawTransaction` 은 서명한 원본이라 체인의 트랜잭션과 바이트 단위로 비교할 수 있습니다.
- `status: rejected` 항목은 사이트가 거래를 요청했고 사용자가 거절했다는 이 기기만의 기록입니다[4].

### 증명하지 못하는 것

- `status: submitted` 만으로는 체인에서 확정됐다고 할 수 없습니다. `hash` 로 블록 탐색기나 노드에서 확정 여부를 확인합니다.
- `origin` 은 요청을 보낸 사이트일 뿐이고, 사용자가 그 사이트를 믿었다거나 내용을 이해하고 승인했다는 뜻은 아닙니다.
- `importTime` 은 계정이 이 설치본에 들어온 시각이지 키를 처음 만든 시각이 아닙니다. 복구 문구로 다른 기기에 지갑을 되살리면 그 기기에서 새 시각이 들어갑니다[1].
- 로컬 거래 목록은 한도로 잘릴 수 있어서 이 지갑이 한 거래의 전부가 아닙니다[3][5].
- 누가 키보드 앞에 있었는지는 이 기록만으로 알 수 없습니다.

보고서에는 기록으로 확인되는 만큼 씁니다. 예: "이 프로필의 MetaMask 상태 `TransactionController.transactions` 에 `origin` 이 `https://예시.com`, `txParams.from` 이 0xAAAA…(만든 예시), `hash` 가 0xBBBB…(만든 예시) 인 항목이 있고, 이 해시의 트랜잭션은 블록 탐색기에서 2026-01-15 03:12:40 UTC(만든 예시) 블록에 포함된 것으로 확인된다."

## 시각 해석

로컬 시각은 모두 자바스크립트 `Date.now()` 나 `new Date().getTime()` 으로 만든 값이라, 1970-01-01 UTC 부터 흐른 밀리초이고 시간대 정보는 없습니다. 기기 시계를 그대로 쓰므로 기기 시계가 틀리면 이 값들도 함께 틀립니다.

| 필드 | 언제 기록하나 | 단위 | 근거 |
|---|---|---|---|
| `transactions[].time` | 거래 항목을 만들 때 | 밀리초, 기기 시계 | [3][4] |
| `transactions[].submittedTime` | 네트워크로 보낼 때 | 밀리초, 기기 시계 | [3][4] |
| `transactions[].blockTimestamp` | 블록이 만들어진 때 | 문자열(형식은 실제 데이터로 확인) | [4] |
| `submitHistory[].time` | 네트워크로 보낼 때 | 밀리초, 기기 시계 | [3][4] |
| `permissions.*.date` | 권한을 만들 때 | 밀리초, 기기 시계 | [8] |
| `permissionHistory.*.lastApproved` | 권한을 마지막으로 허락할 때 | 밀리초, 기기 시계 | [9] |
| `permissionHistory.eth_accounts.accounts` 의 값 | 그 주소를 사이트에 마지막으로 보여 줄 때 | 밀리초, 기기 시계 | [9] |
| `metadata.importTime`·`lastSelected`·`nameLastUpdatedAt` | 계정이 들어올 때·선택할 때·이름을 바꿀 때 | 밀리초, 기기 시계 | [1] |
| `addressBook` 항목 `lastUpdatedAt` | 주소록 항목을 추가·수정할 때 | 밀리초, 기기 시계 | [2] |
| 탐색기 API `timeStamp`(예: Etherscan) | 블록 시각 | 유닉스 초 | [14] |

`blockTimestamp` 와 탐색기의 블록 시각은 체인이 정한 값이라 기기 시계와 상관이 없습니다. 같은 거래의 `submittedTime` 과 블록 시각을 비교하면 보통 블록 시각이 조금 뒤에 오는데, 여러 거래에서 로컬 값이 블록 시각보다 한결같이 앞서거나 크게 뒤진다면 기기 시계가 어긋났을 가능성을 봅니다. 블록 시각의 성질은 [블록 시각과 확정](../../../01-foundations/blockchain/block-time.md)에 있습니다.

## 함정과 한계

**받은 거래가 없을 수 있습니다.** 현재 거래 컨트롤러 코드에는 받은 거래 (incoming transaction) 기능을 없앴다는 주석이 있고 관련 옵션을 무시합니다[3]. 거래 종류 값 `incoming` 은 남아 있어서[4] 옛 판 데이터에는 받은 거래가 섞여 있을 수 있습니다. 받은 자산은 주소로 블록 탐색기에서 따로 조회합니다.

**거래 목록은 잘립니다.** 거래 목록 한도는 기본 40이고 원격 기능 플래그로 바뀔 수 있으며, 기능 플래그 자체가 없으면 자르지 않습니다[3][5]. 자를 때는 `time` 역순으로 정렬해 `nonce`·체인 ID·날짜를 묶은 키 40개까지 남기고, 끝나지 않은 상태(`unapproved`·`submitted` 등)의 거래는 한도와 상관없이 남깁니다[3]. `submitHistory` 는 한도가 기본 100건이라 `transactions` 에서 빠진 거래가 이쪽에 남아 있을 가능성이 있습니다[3][5].

**서명 요청은 디스크에 남지 않습니다.** `personal_sign`·typed data 서명 요청을 담는 필드는 모두 `persist: false` 입니다[6]. 권한 요청 하나하나의 요청·응답 시각을 담는 `permissionActivityLog`(최대 100건)도 디스크에 쓰지 않습니다[9]. 그래서 피싱 사이트에서 서명만 하고 거래를 보내지 않았다면 디스크 상태에는 흔적이 없고, 서명의 결과는 체인 위에서 찾아야 합니다. 이런 사건의 흐름은 [피싱 사이트에 서명했나](../../../04-scenarios/fraud/wallet-drainer.md)에 있습니다. 실행 중인 브라우저의 메모리나 사용자가 내려받은 상태 로그 파일에는 이 필드가 있을 수 있습니다[6][9][17].

**연결한 사이트만 주소를 받는 것은 아닙니다.** 지갑이 웹 페이지에 넣는 지갑 객체는 그 페이지의 제3자 스크립트나 다른 확장도 읽을 수 있습니다[16]. 지갑 확장 100개의 통신을 가로채 분석한 2023년 연구에서는 13개가 사용자 주소를 제3자에게 보냈습니다[16]. `permissionHistory` 에 없는 곳의 서버 기록에서 주소가 나올 수 있다는 뜻입니다.

**도구의 필드 이름이 다릅니다.** 위치 절에 적은 것처럼 iLEAPP 의 MetaMask 분석기는 iOS 앱의 옛 필드 이름을 읽습니다[15]. 확장 상태에 그대로 쓰면 빈 결과가 나올 수 있습니다.

**지운 기록은 저장소 쪽에서 찾습니다.** 사용자가 활동 기록을 지우거나 계정을 없애면 상태 JSON 에서는 사라지지만, LevelDB 파일에 옛 값이 남아 있을 수 있습니다. 옛 레코드를 찾는 방법은 [저장 위치와 구조](storage.md)를 봅니다.

## 직접 분석해 보기

**원본 JSON 에서 한 번.** 먼저 [저장 위치와 구조](storage.md)의 방법으로 확장 저장소 사본에서 레코드를 꺼내, 새 방식이면 `TransactionController`·`PermissionController` 같은 최상위 키를, 옛 방식이면 `data` 키의 값을 JSON 으로 저장합니다. 헥스 편집기로 LevelDB 파일을 열어 `"submitHistory"` 나 `"permissionHistory"` 문자열을 찾으면 JSON 조각이 바로 보이기도 하지만, 레코드가 끊기거나 옛 값과 섞일 수 있으니 파서로 꺼낸 값과 비교합니다. 꺼낸 거래 항목 하나는 다음과 같은 모양입니다(만든 예시, 필드 이름은 [4] 의 타입 정의를 따름).

```json
{
  "id": "0f1e2d3c-0000-4000-8000-000000000001",
  "chainId": "0x1",
  "origin": "https://example-dapp.test",
  "status": "confirmed",
  "time": 1768446700000,
  "submittedTime": 1768446745000,
  "hash": "0x1111111111111111111111111111111111111111111111111111111111111111",
  "txParams": {
    "from": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "to": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "value": "0x2386f26fc10000",
    "nonce": "0x5"
  }
}
```

이 예시의 `value` 0x2386f26fc10000 은 10진수 10,000,000,000,000,000 wei, 곧 0.01 ETH 이고, `time` 1768446700000 은 2026-01-15 03:11:40 UTC 입니다(만든 예시로 계산한 값).

**공개 도구로 한 번.** iLEAPP 의 MetaMask 분석기는 iOS 앱 데이터만 읽으므로[15], 확장 상태는 LevelDB 파서로 JSON 을 꺼낸 뒤 jq 같은 JSON 도구로 필드를 뽑습니다. 예를 들어 거래 목록은 다음처럼 표로 만들 수 있습니다(파일 이름은 만든 예시).

```bash
jq -r '.TransactionController.transactions[]
  | [.time, .status, .origin, .txParams.from, .txParams.to, .txParams.value, .hash]
  | @tsv' TransactionController.json
```

연결 기록은 `.PermissionLogController.permissionHistory | to_entries[]` 로 원점별로 펼치고, `lastApproved` 와 주소별 시각을 사람이 읽는 UTC 시각으로 바꿔 타임라인에 넣습니다. 모바일 앱이면 iLEAPP 의 MetaMask 분석기가 계정·주소록·거래·브라우저 기록을 표로 만들어 줍니다[15].

## 교차 검증

- **블록 탐색기:** `hash` 로 트랜잭션이 체인에 있는지, 어느 블록에 언제 들어갔는지 확인합니다. `rawTx` 와 체인의 원본이 같은지도 비교합니다. → [블록 탐색기 기록 읽기](../../records/block-explorers.md), [이더리움 거래 따라가기](../../../03-techniques/analysis/ethereum-tracing.md)
- **브라우저 방문 기록:** `origin` 과 같은 원점을 방문 기록에서 찾아 연결·거래 시각 앞뒤로 방문했는지 봅니다. → [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/), [파이어폭스](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/firefox/)
- **RPC 제공자 기록:** `submitHistory[].networkUrl` 은 거래를 받은 RPC 서버라서, 수사 기관이 서버 쪽 기록을 요청할 곳이 됩니다. MetaMask 의 기본 제공자는 Infura 이고, Infura 는 2022년 11월 개인 정보 방침을 고쳐 사용자의 IP 주소와 지갑 주소를 수집합니다[16].
- **다른 지갑 흔적:** 같은 주소가 다른 확장·앱에도 있으면 [다른 확장 지갑](../other-extensions.md)과 비교합니다.
- **타임라인:** 로컬 시각과 블록 시각을 한 표에 합쳐 정렬합니다. → [암호화폐 타임라인](../../../03-techniques/analysis/timeline.md)

## 실습

테스트넷에 연결한 새 브라우저 프로필에서 MetaMask 를 설치하고 아래 순서로 움직인 뒤, 매 단계마다 프로필의 확장 저장소를 복사해 두면 기록이 쌓이는 모양을 볼 수 있습니다.

1. 테스트용 탈중앙 앱에 연결한 뒤 `subjects` 와 `permissionHistory` 에 어떤 원점과 시각이 생겼는지 확인합니다. 연결을 끊은 뒤에는 두 필드에서 원점이 각각 어떻게 바뀌나요?
2. 사이트가 요청한 거래 하나는 거절하고 하나는 승인합니다. 두 항목의 `status` 와 `origin` 은 어떻게 다르고, `submitHistory` 에는 어느 쪽만 생기나요?
3. 승인한 거래의 `submittedTime` 과 테스트넷 탐색기의 블록 시각은 몇 초 차이가 나나요?
4. 다른 계정에서 테스트넷 자산을 받은 뒤 받은 거래가 `transactions` 에 생기는지 확인합니다.
5. 사이트에서 메시지 서명만 한 뒤 저장소 사본에 서명 기록이 있는지, 상태 로그 다운로드 파일에는 있는지 비교합니다.

## 참고 문헌

1. MetaMask, `AccountsController.ts` (MetaMask/core). https://github.com/MetaMask/core/blob/main/packages/accounts-controller/src/AccountsController.ts
2. MetaMask, `AddressBookController.ts` (MetaMask/core). https://github.com/MetaMask/core/blob/main/packages/address-book-controller/src/AddressBookController.ts
3. MetaMask, `TransactionController.ts` (MetaMask/core). https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/TransactionController.ts
4. MetaMask, `types.ts` (transaction-controller, MetaMask/core). https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/types.ts
5. MetaMask, `feature-flags.ts` (transaction-controller, MetaMask/core). https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/utils/feature-flags.ts
6. MetaMask, `SignatureController.ts` (MetaMask/core). https://github.com/MetaMask/core/blob/main/packages/signature-controller/src/SignatureController.ts
7. MetaMask, `PermissionController.ts` (MetaMask/core). https://github.com/MetaMask/core/blob/main/packages/permission-controller/src/PermissionController.ts
8. MetaMask, `Permission.ts` (MetaMask/core). https://github.com/MetaMask/core/blob/main/packages/permission-controller/src/Permission.ts
9. MetaMask, `PermissionLogController.ts`, `enums.ts` (MetaMask/core). https://github.com/MetaMask/core/blob/main/packages/permission-log-controller/src/PermissionLogController.ts
10. MetaMask, `SubjectMetadataController.ts` (MetaMask/core). https://github.com/MetaMask/core/blob/main/packages/permission-controller/src/SubjectMetadataController.ts
11. MetaMask, `subject-metadata-controller-init.ts` (metamask-extension). https://github.com/MetaMask/metamask-extension/blob/main/app/scripts/messenger-client-init/subject-metadata-controller-init.ts
12. MetaMask, `metamask-controller.js` (metamask-extension). https://github.com/MetaMask/metamask-extension/blob/main/app/scripts/metamask-controller.js
13. ethereum.org, "Transactions". https://ethereum.org/en/developers/docs/transactions/
14. Etherscan, "Get Normal Transactions By Address" (API 문서). https://docs.etherscan.io/api-reference/endpoint/txlist.md
15. Alexis Brignoni 외, iLEAPP `metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
16. Christof Ferreira Torres, Fiona Willi, Shweta Shinde, "Is Your Wallet Snitching On You? An Analysis on the Privacy Implications of Web3", arXiv, 2023. doi:10.48550/arXiv.2306.08170
17. MetaMask, "How to take a State Dump" (metamask-extension 문서). https://github.com/MetaMask/metamask-extension/blob/main/docs/state_dump.md
18. MetaMask, `shared/constants/app.ts` (metamask-extension). https://github.com/MetaMask/metamask-extension/blob/main/shared/constants/app.ts
