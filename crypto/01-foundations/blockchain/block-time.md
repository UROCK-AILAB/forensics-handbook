---
title: "블록 시각과 확정"
parent: "기반 · 블록체인 기초"
nav_order: 40
---

# 블록 시각과 확정 (Block Time·Confirmations)

블록 시각은 블록을 만든 채굴자나 검증자가 블록에 적은 유닉스 시각이라, 트랜잭션이 블록에 들어간 때는 알 수 있어도 사용자가 트랜잭션을 보낸 때는 알 수 없습니다. 확정 수는 그 블록 위에 블록이 몇 개 더 쌓였는지를 조회하는 순간 계산한 값이라 시간이 지나면 늘어납니다. 비트코인과 이더리움의 블록 시각·확정 규칙뿐 아니라 지갑 앱·블록 탐색기 기록에 섞여 있는 여러 시각 필드를 구분해 읽는 법까지 다룹니다.

## 이 형식을 쓰는 아티팩트

블록 시각과 확정 수는 블록체인 안에만 있지 않고, 블록체인을 옮겨 적은 기록 여러 곳에 다시 나옵니다. Bitcoin Core 지갑은 트랜잭션마다 블록 시각과 지갑이 적은 시각을 함께 돌려주고[5], 블록 탐색기 API는 트랜잭션 목록에 블록 시각과 확정 수를 붙여 줍니다[7][14]. 지갑 앱 데이터에는 기기 시계로 적은 시각과 블록 시각이 한 레코드에 같이 들어 있기도 합니다[17][19].

- 데스크톱 지갑: [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md)
- 브라우저 확장 지갑: [MetaMask](../../02-artifacts/browser/metamask/index.md)
- 모바일: [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md), [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md), [거래소 앱](../../02-artifacts/mobile/exchange-apps.md)
- 기록: [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md), [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md)

블록 헤더의 다른 필드는 [블록과 트랜잭션](blocks-transactions.md)에서, 잠금 시각(lock_time)은 [비트코인의 UTXO](utxo.md)에서, 이더리움 로그는 [이더리움의 계정과 로그](ethereum-accounts.md)에서 다룹니다.

## 구조

### 비트코인 블록 시각

비트코인 블록 헤더에는 4바이트 부호 없는 정수 time 필드가 있습니다. 채굴자가 헤더를 해시하기 시작한 시각을 채굴자 스스로 적은 값이고, 1970-01-01 00:00 UTC 부터 지난 초를 세는 유닉스 시각입니다[1]. 헤더는 버전 4바이트, 이전 블록 해시 32바이트, 머클 루트 32바이트 순서라서 time 필드는 헤더 시작에서 68(0x44)바이트 뒤에 리틀 엔디언으로 들어 있습니다[1].

합의 규칙이 이 값에 거는 제한은 두 가지입니다. 앞 11블록 시각의 중앙값보다 커야 하고, 풀 노드는 자기 시계보다 2시간 넘게 앞선 헤더를 받지 않습니다[1]. 중앙값보다만 크면 되므로 바로 앞 블록보다 이른 시각이 적힌 블록도 규칙에 맞고, 블록 시각이 높이 순서대로 늘어난다는 보장은 없습니다. 실제 시각보다 2시간까지 앞선 블록 시각도 네트워크가 받아들입니다[3].

블록 간격도 정해져 있지 않습니다. 네트워크는 2,016블록마다 난이도를 조정해 그 2,016블록이 1,209,600초(2주)에 만들어지도록 맞추므로[2], 평균이 600초(10분)가 될 뿐입니다. 수수료를 충분히 낸 트랜잭션이 첫 확정을 받기까지 평균 10분이 걸립니다[4].

노드와 탐색기는 블록 시각을 아래 필드로 돌려줍니다.

| 필드 | 돌려주는 곳 | 뜻 |
|---|---|---|
| `time` | Bitcoin Core `getblock` | 블록 시각, 유닉스 초[6] |
| `mediantime` | Bitcoin Core `getblock` | 중앙값 시각, 유닉스 초[6] |
| `blocktime` | Bitcoin Core `gettransaction` | 트랜잭션이 들어간 블록의 시각, 유닉스 초[5] |
| `timestamp` | Esplora 블록 | 블록 시각[7] |
| `mediantime` | Esplora 블록 | 중앙값 시각(median time-past)[7] |
| `status.block_time` | Esplora 트랜잭션 | 확정된 트랜잭션에만 값이 있고 미확정이면 `null`[7] |

### 비트코인 확정 수

트랜잭션이 블록에 들어가면 확정 (confirmation) 하나를 얻고, 그 위에 블록이 하나 쌓일 때마다 확정이 하나씩 늘어납니다[4]. 블록을 바꾸려면 그 위의 블록까지 모두 다시 만들어야 해서, 확정 수가 클수록 트랜잭션이 바뀌기 어렵습니다[4].

| 확정 수 | 뜻 |
|---|---|
| 0 | 전파됐지만 어느 블록에도 들어가지 않은 미확정 트랜잭션[4] |
| 1 | 최신 블록에 들어갔습니다. 최신 블록은 가끔 우연히 다른 블록으로 바뀌므로 이중 지불이 아직 가능합니다[4] |
| 2 | 트랜잭션이 든 블록 위에 블록 하나가 더 이어졌습니다[4] |
| 6 | 약 1시간 분량의 블록이 쌓였습니다. 고액 거래는 최소 6 확정을 기다리라고 권하며, 이 숫자는 다소 임의로 정한 값입니다[4] |

같은 입력을 쓰는 트랜잭션 두 개를 이중 지불 (double spend) 이라 하고, 둘 중 하나만 블록에 들어갑니다[4]. 같은 높이에 블록이 둘 생기는 포크 (fork) 에서는 노드가 작업량이 더 많은 체인을 따르고 짧은 체인의 블록을 버립니다[2]. 버려진 블록은 스테일 블록 (stale block) 이라 하고 흔히 고아 블록 (orphan block) 이라고도 부르는데, 고아 블록은 부모 블록을 모르는 블록을 가리킬 때도 씁니다[2]. 코인베이스 출력을 100블록 동안 쓰지 못하게 한 규칙도 블록이 이렇게 버려질 수 있어서 생겼습니다[2].

Bitcoin Core 지갑의 `gettransaction` 결과에는 확정과 시각에 관한 필드가 여럿 있습니다[5].

| 필드 | 뜻 |
|---|---|
| `confirmations` | 확정 수. 음수면 그 수만큼 전 블록에서 충돌한 트랜잭션입니다[5] |
| `blockhash`·`blockheight`·`blockindex` | 트랜잭션이 든 블록의 해시와 높이, 블록 안에서의 순번[5] |
| `blocktime` | 블록 시각, 유닉스 초[5] |
| `time` | 트랜잭션 시각(transaction time), 유닉스 초[5] |
| `timereceived` | 받은 시각(time received), 유닉스 초[5] |
| `walletconflicts` | 충돌하는 트랜잭션 ID 목록[5] |
| `bip125-replaceable` | BIP-125 교체 가능 여부(`yes`·`no`·`unknown`)[5] |
| `details[].category` | `send`, `receive`, `generate`(확정 100 초과 코인베이스), `immature`(확정 100 이하 코인베이스), `orphan`(버려진 블록의 코인베이스)[5] |
| `abandoned` | 지갑에서 버린 트랜잭션인지, `send` 에만 있음[5] |

블록 단위로는 `getblock` 의 `confirmations` 가 주 체인에 없는 블록에서 -1 이 되고[6], Esplora 블록 상태의 `in_best_chain` 은 고아 블록이면 `false` 입니다[7].

확정 전에는 트랜잭션이 바뀔 수 있습니다. 입력 하나라도 nSequence 가 0xfffffffe 보다 작으면 교체를 허용한다는 BIP-125 신호이고, 받는 사람은 이런 트랜잭션을 확정 전까지 결제로 보지 않을 수 있습니다[8]. Bitcoin Core 28.0 에서는 `-mempoolfullrbf` 기본값이 0 에서 1 로 바뀌었으므로[9], 교체 신호가 없다는 사실만으로 확정 전에 교체되지 않았다고 판단하지 않습니다.

### 이더리움 블록 시각

이더리움은 2022년 9월 작업 증명에서 지분 증명(proof-of-stake)으로 바뀌었습니다[10]. 작업 증명 시절에는 채굴 난이도에 따라 블록 간격이 정해졌고, 지분 증명 이후에는 시간을 12초 슬롯 (slot) 으로 나누고 32슬롯을 한 에폭 (epoch) 으로 묶습니다[10]. 에폭 하나는 12초 × 32 = 384초(6.4분)입니다.

슬롯마다 검증자 한 명이 뽑혀 블록을 제안합니다[10][11]. 뽑힌 검증자가 오프라인이면 그 슬롯은 비므로[11], 이어진 두 블록의 간격은 12초가 아니라 24초·36초처럼 12초의 배수가 될 수 있습니다. 블록의 `timestamp` 는 실행 페이로드(execution payload) 안에 있는 블록 시각이고[11], JSON-RPC 블록 객체에서는 블록을 모은(collated) 유닉스 시각을 `0x` 로 시작하는 16진수로 돌려줍니다[12]. 지분 증명 블록은 JSON-RPC 의 `nonce` 가 `0x0` 이라서 전환 전후 블록을 구분하는 단서가 됩니다[12].

### 이더리움 확정

이더리움 지분 증명에서는 많은 ETH 를 소각하지 않고는 바꿀 수 없는 블록에 트랜잭션이 들어가면 최종 확정성 (finality) 을 얻습니다[10]. 각 에폭의 첫 블록이 체크포인트 (checkpoint) 이고, 검증자가 체크포인트 두 개를 짝지어 투표합니다[10]. 전체 스테이크의 2/3 이상이 한 짝에 표를 던지면 나중 체크포인트는 justified, 앞 체크포인트는 finalized 가 됩니다[10]. finalized 블록을 되돌리려면 전체 스테이크의 1/3 이상을 잃어야 하고, 네 에폭 넘게 확정이 안 되면 비활성 누출(inactivity leak)이 작동합니다[10].

트랜잭션은 블록에 들어간 뒤 justified, finalized 순서로 올라갑니다[13]. 체크포인트가 에폭마다 하나라서 정상 상태에서 finalized 까지는 약 두 에폭(384초 × 2 = 768초, 약 12.8분으로 계산한 값)이 걸립니다. 노드에 물을 때는 블록 태그로 기준을 고릅니다. `latest` 는 최신 제안 블록, `safe` 는 최신 safe head 블록, `finalized` 는 최신 확정 블록, `pending` 은 대기 중 상태, `earliest` 는 제네시스 블록입니다[12].

### 앱과 탐색기의 시각 필드

지갑 앱과 탐색기는 블록 시각과 기기 시각을 서로 다른 필드에 담습니다. 같은 제공자 안에서도 API 마다 진법이 다를 수 있습니다.

| 기록 | 필드 | 기준 | 단위·형식 |
|---|---|---|---|
| Etherscan `txlist`·`tokentx` | `timeStamp` | 블록이 채굴된 시각 | 유닉스 초, 10진 문자열[14][15] |
| Etherscan `getLogs` | `timeStamp` | 블록이 채굴된 시각 | 유닉스 초, 16진 문자열[16] |
| Etherscan `txlist`·`tokentx` | `confirmations` | 트랜잭션이 든 블록 뒤에 채굴된 블록 수 | 10진 문자열[14][15] |
| MetaMask 트랜잭션 상태 | `time` | 이 트랜잭션에 연결된 시각 | 단위 설명 없음[17] |
| MetaMask 트랜잭션 상태 | `submittedTime` | 네트워크에 제출한 시각 | 유닉스 밀리초[17] |
| MetaMask 트랜잭션 상태 | `blockTimestamp` | 블록을 모은 시각 | 문자열[17] |
| Coinbase Wallet (iOS) `tx_history_v2` | `createdAt`·`confirmedAt` | 앱이 적은 시각 | 시간대 표시 없는 `YYYY-MM-DD HH:MM:SS` 문자열[19] |
| Trust Wallet (iOS, 옛 공개 코드) | `date`·`blockNumber` | 서버가 준 `timeStamp` 를 유닉스 초로 변환 | 날짜 객체[20] |

iLEAPP 의 MetaMask 분석기는 `time` 을 UTC 로 바꿔 Timestamp 열에 보여 줍니다[18]. iLEAPP 의 Coinbase Wallet 분석기는 시간대 표시가 없는 `createdAt`·`confirmedAt` 을 UTC 로 읽습니다[19]. 같은 앱의 MMKV 저장소에는 `Z`(UTC 표시)를 붙여 적은 마이그레이션 시각이 있고, iLEAPP 시험 이미지 두 개에서 이 값은 계정 레코드의 생성 시각보다 11초·108초 앞선 같은 날 같은 시였습니다[19]. 현지 시각으로 읽으면 두 값이 몇 시간씩 벌어지므로, 이 앱은 시간대 표시 없는 시각도 UTC 로 적는 것으로 보입니다.

## 읽는 법

### 헥스로 블록 시각 읽기

비트코인 개발자 문서의 헤더 예시에서 오프셋 0x44 의 4바이트는 `24 d9 5a 54` 입니다[1]. 리틀 엔디언이라 바이트를 거꾸로 읽으면 0x545AD924 이고, 10진수로 1,415,239,972 입니다[1]. 유닉스 시각으로 바꾸면 2014-11-06 02:12:52 UTC 가 됩니다(명세 예시를 변환한 값).

Bitcoin Core 28.0 부터 블록 파일(`blk*.dat`)은 blocksdir 에 둔 키로 XOR 처리되는 것이 기본이라[9], 원시 블록 파일을 헥스 편집기로 열면 헤더 값이 그대로 보이지 않을 수 있습니다. 데이터 폴더 구조는 [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md)에서 다룹니다.

### 단위와 진법 구분하기

같은 순간도 기록마다 모양이 다릅니다. 아래는 모두 2023-11-14 22:13:20 UTC 를 나타내는 만든 예시입니다.

| 모양 | 값 (만든 예시) | 어디서 나오나 |
|---|---|---|
| 10진 10자리, 초 | `1700000000` | Bitcoin Core, Etherscan `txlist`[5][14] |
| 16진, 초 | `0x6553f100` | 이더리움 JSON-RPC, Etherscan `getLogs`[12][16] |
| 10진 13자리, 밀리초 | `1700000000123` | MetaMask `submittedTime`[17] |
| 시간대 없는 날짜 문자열 | `2023-11-14 22:13:20` | Coinbase Wallet (iOS)[19] |

13자리 값을 초로 읽으면 수만 년 뒤 날짜가 나오고, 16진 문자열을 10진수로 읽으면 전혀 다른 날짜가 나옵니다. 변환 결과가 그 체인이 있던 기간 밖이면 단위와 진법부터 다시 확인합니다.

### 확정 수 다시 계산하기

기록에 남은 확정 수는 조회한 순간의 값이라 그대로 옮기지 않고, 트랜잭션이 든 블록 높이와 현재 최고 높이로 다시 계산합니다. 비트코인은 트랜잭션이 든 블록을 1 확정으로 보므로[4] 확정 수는 "최고 높이 − 포함 높이 + 1" 이고, 최고 높이는 Esplora `GET /blocks/tip/height` 로 얻습니다[7]. Etherscan `confirmations` 는 포함 블록 뒤에 채굴된 블록 수라[14] "최고 높이 − 포함 높이" 입니다. 보고서에는 확정 수와 함께 포함 블록의 높이·해시, 조회한 시각을 적습니다.

## 포렌식에서 중요한 점

### 증명하는 것 / 증명하지 못하는 것

블록 시각과 확정 수로는 이 트랜잭션이 이 높이·해시의 블록에 들어갔고, 그 블록에 이 시각이 적혀 있으며, 조회한 순간 그 블록 위에 블록이 몇 개 쌓여 있었는지까지 증명할 수 있습니다[1][4][11].

사용자가 트랜잭션을 만들거나 보낸 시각은 블록 시각으로 증명되지 않습니다. 트랜잭션은 미확정 상태로 기다린 뒤 블록에 들어가므로 보낸 시각은 블록 시각보다 이르고, 그 시각은 앱이 적은 `submittedTime`(MetaMask)[17], `timereceived`(Bitcoin Core)[5], `createdAt`(Coinbase Wallet)[19] 같은 기기 기록으로 보완합니다. 비트코인 블록 시각은 규칙상 실제 시각보다 2시간까지 앞설 수 있어서[3] 분 단위로 정확한 시각이라고 주장할 수 없습니다. 확정 수가 커도 누가 보냈는지는 알 수 없습니다.

### 시각 해석

| 값 | 누가 적나 | 기준 |
|---|---|---|
| 비트코인 헤더 time | 채굴자 | 유닉스 초(UTC), 앞 11블록 중앙값보다 크고 노드 시계보다 2시간 넘게 앞서지 않음[1] |
| `mediantime` | 노드가 계산 | 블록 시각의 중앙값(median time-past)[6][7] |
| 이더리움 `timestamp` | 블록 제안자 | 유닉스 초, 지분 증명 이후 12초 슬롯[11][12] |
| Bitcoin Core `time`·`timereceived` | Bitcoin Core 지갑 | 유닉스 초[5] |
| MetaMask `submittedTime` | 확장·앱 | 유닉스 밀리초[17] |
| Etherscan `timeStamp` | 탐색기가 블록 시각을 옮김 | 유닉스 초, API 따라 10진·16진[14][16] |

유닉스 시각은 시간대가 없는 값이라 UTC 로 바꾼 뒤 현지 시각을 따로 적습니다. 시간대 표시 없이 날짜 문자열로 저장한 앱 기록은 그 앱이 UTC 로 적는지 현지 시각으로 적는지를 같은 기기의 다른 기록과 비교해 확인합니다[19]. 앱이 적은 제출 시각이 그 트랜잭션의 블록 시각보다 한참 늦으면 기기 시계가 틀렸거나 시간대를 잘못 읽었을 가능성이 있습니다. 여러 기록을 한 줄로 합치는 방법은 [암호화폐 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

### 체인 재구성과 버려진 블록

체인이 재구성되면 이미 블록에 들어갔던 트랜잭션이 다시 미확정으로 돌아가거나 다른 트랜잭션으로 바뀔 수 있습니다. 이더리움 로그는 재구성으로 빠지면 `removed` 가 `true` 가 되고[12], Esplora 는 버려진 블록의 `in_best_chain` 을 `false` 로 돌려줍니다[7]. Bitcoin Core 지갑에서는 음수 `confirmations`, `walletconflicts` 목록, `orphan` 분류로 남습니다[5]. 앱이나 탐색기 화면을 캡처한 시점에는 확정됐던 트랜잭션이 나중에 체인에서 사라질 수 있으니, 짧은 확정 수로 캡처한 기록은 현재 체인에서 다시 조회합니다.

## 함정

**확정 수를 세는 방식이 도구마다 다릅니다.** 비트코인 개발자 문서는 트랜잭션이 든 블록을 1 확정으로 보고[4], Etherscan 은 그 블록 뒤에 채굴된 블록 수를 확정 수로 적습니다[14]. 같은 순간에 조회해도 1 차이가 날 수 있으니 도구마다 정의를 확인합니다.

**블록 시각이 높이 순서대로 늘어나지 않습니다.** 비트코인 블록 시각은 앞 11블록 중앙값보다만 크면 되므로[1], 높은 블록의 시각이 낮은 블록보다 이를 수 있습니다. 순서는 블록 높이로 정하고 블록 시각은 대략의 시각으로 씁니다.

**잠금 시각은 블록 시각이 아닙니다.** 트랜잭션의 lock_time 은 "이보다 이르게 블록에 넣을 수 없다" 는 조건이고, 5억보다 작으면 블록 높이, 크거나 같으면 유닉스 시각으로 읽습니다[3]. 트랜잭션을 만든 시각이나 블록에 들어간 시각으로 읽으면 안 됩니다.

**이더리움 블록 간격이 늘 12초는 아닙니다.** 2022년 9월 이전 작업 증명 블록은 채굴 난이도에 따라 간격이 달랐고[10], 이후에도 빈 슬롯이 있으면 간격이 12초의 배수로 늘어납니다[11].

**같은 탐색기에서도 진법이 바뀝니다.** Etherscan `txlist` 의 `timeStamp` 는 10진 문자열이고 `getLogs` 의 `timeStamp` 는 16진 문자열입니다[14][16]. 한 스크립트로 여러 API 결과를 합칠 때 진법을 따로 처리합니다.

**MetaMask 의 `time` 은 단위 설명이 없습니다.** `submittedTime` 은 단위가 밀리초로 정해져 있지만 `time` 에는 단위 설명이 없습니다[17]. 실제 값의 자릿수로 초인지 밀리초인지 확인하고, 앱 버전에 따라 필드 이름이 다를 수 있으니 실제 파일에서 키 이름부터 봅니다. 저장 위치는 [MetaMask](../../02-artifacts/browser/metamask/index.md)에서 다룹니다.

**"고아 블록" 은 두 가지 뜻으로 씁니다.** 포크에서 버려진 스테일 블록과 부모를 모르는 블록을 모두 고아 블록이라 부릅니다[2]. 보고서에는 어느 뜻인지 적습니다.

## 도구

**Bitcoin Core RPC.** `getblock` 으로 블록의 `time`·`mediantime`·`confirmations` 를[6], `gettransaction` 으로 지갑 트랜잭션의 `blocktime`·`time`·`timereceived`·`confirmations` 를 얻습니다[5].

**Esplora API.** `GET /tx/:txid/status` 는 확정 여부와 블록 높이·해시를[7], `GET /block/:hash/status` 는 `in_best_chain`·`next_best` 를[7], `GET /blocks/tip/height` 는 현재 최고 높이를 돌려줍니다[7].

**이더리움 JSON-RPC.** `eth_getBlockByNumber` 에 `"finalized"` 나 `"safe"` 태그를 넣으면 그 시점의 확정 블록과 safe 블록을 얻고[12], 트랜잭션의 블록 번호와 비교해 finalized 여부를 확인할 수 있습니다.

**Etherscan API.** `txlist`·`tokentx`·`getLogs` 결과의 `timeStamp` 와 `confirmations` 를 씁니다[14][15][16]. 블록 탐색기 기록을 증거로 다루는 법은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)에서 다룹니다.

**iLEAPP.** iOS 이미지에서 MetaMask 와 Coinbase Wallet 트랜잭션 시각을 UTC 로 읽어 보여 줍니다[18][19]. 원래 저장된 값과 변환 결과를 함께 확인합니다.

## 참고 문헌

1. Bitcoin Developer Reference, "Block Chain — Block Headers". https://developer.bitcoin.org/reference/block_chain.html
2. Bitcoin Developer Guide, "Block Chain — Proof of Work, Block Height and Forking". https://developer.bitcoin.org/devguide/block_chain.html
3. Bitcoin Developer Guide, "Transactions — Locktime and Sequence Number". https://developer.bitcoin.org/devguide/transactions.html
4. Bitcoin Developer Guide, "Payment Processing — Verifying Payment". https://developer.bitcoin.org/devguide/payment_processing.html
5. Bitcoin Core RPC Reference, "gettransaction". https://developer.bitcoin.org/reference/rpc/gettransaction.html
6. Bitcoin Core RPC Reference, "getblock". https://developer.bitcoin.org/reference/rpc/getblock.html
7. Blockstream Esplora, "HTTP REST API". https://github.com/Blockstream/esplora/blob/master/API.md
8. BIP-125, "Opt-in Full Replace-by-Fee Signaling". https://github.com/bitcoin/bips/blob/master/bip-0125.mediawiki
9. Bitcoin Core 28.0 Release Notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-28.0.md
10. ethereum.org, "Proof-of-stake (PoS)". https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/
11. ethereum.org, "Blocks". https://ethereum.org/en/developers/docs/blocks/
12. ethereum.org, "JSON-RPC API". https://ethereum.org/en/developers/docs/apis/json-rpc/
13. ethereum.org, "Transactions". https://ethereum.org/en/developers/docs/transactions/
14. Etherscan API, "Get a list of 'Normal' Transactions By Address (txlist)". https://docs.etherscan.io/api-reference/endpoint/txlist.md
15. Etherscan API, "Get a list of 'ERC20 - Token Transfer Events' by Address (tokentx)". https://docs.etherscan.io/api-reference/endpoint/tokentx.md
16. Etherscan API, "Get Event Logs (getLogs)". https://docs.etherscan.io/api-reference/endpoint/getlogs.md
17. MetaMask core, `packages/transaction-controller/src/types.ts`. https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/types.ts
18. iLEAPP, `scripts/artifacts/metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
19. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
20. Trust Wallet iOS, `Trust/Transactions/Storage/Transaction.swift`. https://github.com/trustwallet/trust-wallet-ios/blob/master/Trust/Transactions/Storage/Transaction.swift
