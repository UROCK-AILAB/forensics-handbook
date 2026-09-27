---
title: "비트코인의 UTXO"
parent: "기반 · 블록체인 기초"
nav_order: 10
---

# 비트코인의 UTXO (UTXO Model)

비트코인에는 계좌마다 잔액을 적어 두는 필드가 없습니다. 트랜잭션의 출력 하나하나에 금액과 잠금 조건이 들어 있고, 다음 트랜잭션의 입력이 그 출력을 통째로 쓰는 방식으로 돈이 옮겨 가서, 모든 출력은 아직 쓰지 않은 출력(UTXO)이거나 이미 쓴 출력입니다[1]. 이 페이지는 입력이 앞 출력을 가리키는 구조, 수수료와 거스름돈이 생기는 원리, 출력이 쓰였는지 확인하는 방법, 그리고 이 구조로 증명할 수 있는 것과 없는 것을 다룹니다.

## 이 형식을 쓰는 아티팩트

UTXO 는 비트코인 블록체인의 데이터 모델이라서 비트코인 금액이 나오는 기록은 모두 이 구조 위에 있습니다. 풀 노드는 쓰지 않은 출력을 따로 모아 두는데, Bitcoin Core 는 데이터 폴더의 `chainstate/` LevelDB 에 현재 쓰지 않은 출력 전체와 그 출력이 나온 트랜잭션의 메타데이터를 저장합니다[4]. 0.8.0 이전에는 `coins/` 가 이 역할을 했습니다[4]. 지갑은 자기 주소로 들어온 출력 가운데 쓸 수 있는 것을 더해 잔액으로 보여 주고[2], 블록 탐색기는 트랜잭션 ID 와 출력 번호로 출력 하나를 가리킵니다[7].

- 데스크톱 지갑: [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md), [Electrum](../../02-artifacts/desktop/electrum.md), [Exodus](../../02-artifacts/desktop/exodus.md)
- 모바일: [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md), [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md)
- 기록: [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md), [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md)

`chainstate/` 의 저장 방식은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)에서, 원시 트랜잭션 전체 형식과 블록 안 배치는 [블록과 트랜잭션](blocks-transactions.md)에서 다룹니다.

## 구조

### 트랜잭션에서 트랜잭션으로

지갑 화면은 지갑에서 지갑으로 돈을 보내는 것처럼 보여 주지만, 비트코인은 실제로 트랜잭션에서 트랜잭션으로 옮겨 갑니다[1]. 트랜잭션마다 입력과 출력이 하나 이상 있고, 입력은 앞 트랜잭션이 만든 출력 하나를 씁니다[2]. 출력 하나는 블록체인 전체에서 입력으로 한 번만 쓸 수 있고, 같은 출력을 다시 쓰려는 시도는 이중 지불(double spend)로 거부됩니다[1]. 그래서 출력은 쓰지 않은 출력(Unspent Transaction Output, UTXO)과 쓴 출력 두 상태뿐이고, 유효한 트랜잭션은 UTXO 만 입력으로 씁니다[1]. 지갑에 잔액 10,000 사토시가 보이면 하나 이상의 UTXO 에 든 사토시를 더한 값이 10,000 이라는 뜻입니다[2].

> 그림 자리: 트랜잭션 A 의 출력 0·1 이 각각 트랜잭션 B·C 의 입력으로 이어지고, 아직 어떤 입력도 가리키지 않은 출력이 UTXO 로 남는 모습

### 입력이 출력을 가리키는 방법

입력은 트랜잭션 ID(TXID)와 출력 번호로 쓸 출력 하나를 짚습니다[2]. 이 두 값을 묶은 것을 아웃포인트(outpoint)라 하고, 원시 트랜잭션 안에서 36바이트를 차지합니다[3]. 출력 번호는 흔히 vout 이라 부르며 첫 출력이 0 입니다[2][3].

| 크기(바이트) | 필드 | 형식 | 내용 |
|---|---|---|---|
| 32 | hash | char[32] | 쓸 출력이 들어 있는 트랜잭션의 TXID, 내부 바이트 순서 |
| 4 | index | uint32_t | 그 트랜잭션의 몇 번째 출력인지. 첫 출력은 `0x00000000` |

아웃포인트 뒤에는 서명 스크립트 길이, 서명 스크립트, 4바이트 시퀀스 번호가 이어지고, 입력에는 금액 필드가 없습니다[3]. 입력이 쓰는 금액과 주소는 아웃포인트가 가리키는 앞 트랜잭션의 출력을 찾아야 알 수 있습니다.

출력에는 금액과 잠금 조건이 들어 있습니다[3].

| 크기(바이트) | 필드 | 형식 | 내용 |
|---|---|---|---|
| 8 | value | int64_t | 사토시 단위 금액, 0 도 허용 |
| 1 이상 | pk_script bytes | compactSize uint | 잠금 스크립트 길이, 최대 10,000바이트 |
| 가변 | pk_script | char[] | 이 출력을 쓰려면 충족해야 하는 조건 |

출력 금액의 합은 입력이 쓰는 앞 출력 금액의 합을 넘을 수 없습니다. 예외는 블록 보조금과 수수료를 받는 코인베이스 트랜잭션뿐입니다[3].

### 잠금 스크립트 종류

출력의 종류는 잠금 스크립트(pubkey script, scriptPubKey)의 모양으로 구분합니다. Bitcoin Core 0.9 기준 표준 종류는 P2PKH, P2SH, 다중 서명(Multisig), 공개 키(Pubkey), 데이터 기록(Null Data) 다섯 가지이고[2], 세그윗(SegWit)이 P2WPKH·P2WSH 를 더했습니다[5].

| 종류 | 잠금 스크립트 모양 | 비고 |
|---|---|---|
| P2PKH | `76 a9 14` + 공개 키 해시 20바이트 + `88 ac` | OP_DUP OP_HASH160 (20바이트) OP_EQUALVERIFY OP_CHECKSIG[3] |
| P2SH | OP_HASH160 (스크립트 해시 20바이트) OP_EQUAL | [2]. P2SH 로 감싼 세그윗 출력도 이 모양[5] |
| P2WPKH (세그윗 v0) | `00 14` + 공개 키 해시 20바이트 | [5] |
| P2WSH (세그윗 v0) | `00 20` + 스크립트 해시 32바이트 | [5] |
| 세그윗 v1 이상 (탭루트 등) | 증인 버전 1~16 의 증인 프로그램 | 주소는 Bech32m 으로 인코딩[6] |
| Null Data | OP_RETURN (데이터) | 쓸 수 없는 출력[2] |

잠금 스크립트 안의 해시가 주소 문자열로 바뀌는 규칙은 [주소 형식](../wallets/address-formats.md)에서 다룹니다.

### 수수료

트랜잭션에는 수수료 필드가 따로 없습니다[3]. 입력이 쓰는 금액의 합에서 출력 금액의 합을 뺀 나머지를 그 트랜잭션을 블록에 넣은 채굴자가 수수료로 가져가고, 출력 합이 입력 합보다 크면 트랜잭션이 거부됩니다(코인베이스 제외)[1]. 그래서 수수료를 알려면 입력마다 앞 출력의 금액을 찾아 더해야 합니다. Esplora 같은 블록 탐색기 API 는 이 계산을 끝낸 값을 `fee` 필드로 주고[7], Bitcoin Core 지갑의 `gettransaction` 은 보낸 트랜잭션에 한해 음수 `fee` 를 보여 줍니다[8].

### 거스름돈 출력

UTXO 는 쓸 때 통째로 써야 해서, 보낼 금액과 딱 맞는 UTXO 가 없으면 남는 금액을 자기에게 돌려보내는 출력을 하나 더 만듭니다. 이 출력이 거스름돈 출력(change output)이고, 대부분의 트랜잭션에 들어 있습니다[2]. 거스름돈은 입력과 같은 공개 키 해시나 스크립트 해시로 돌려보낼 수도 있습니다. 다만 같은 공개 키를 거듭 쓰면 다른 사람이 그 사람의 받고 쓴 내역을 쉽게 따라갈 수 있어서, 거스름돈도 새 주소로 받으라고 권합니다[2].

프로토콜에는 어느 출력이 거스름돈인지 표시하는 필드가 없습니다. HD 지갑이 거스름돈 주소를 받는 주소와 따로 파생하는 내부 체인은 [복구 문구와 파생 경로](../wallets/seed-derivation.md)에서 다룹니다.

### 코인베이스 출력

블록의 첫 트랜잭션인 코인베이스 트랜잭션은 앞 출력을 쓰지 않고 블록 보상을 받습니다[1]. 입력의 아웃포인트는 32바이트 0 해시와 출력 번호 `0xffffffff` 로 채워서 실제 출력을 가리키지 않습니다[3]. 체인이 갈라져 그 블록이 나중에 버려질 수 있어서, 코인베이스가 만든 출력은 최소 100블록 동안 쓸 수 없습니다[1]. Bitcoin Core 지갑은 이런 입금을 확정 100 이하일 때 `immature`, 100 을 넘으면 `generate` 로 분류합니다[8].

### 잠금 시각과 시퀀스 번호

트랜잭션 끝 4바이트의 잠금 시각(locktime, nLockTime)은 이 트랜잭션을 블록에 넣을 수 있는 가장 이른 때를 정합니다[2]. 값이 5억보다 작으면 블록 높이로, 5억 이상이면 유닉스 시각으로 읽습니다[2]. 5억을 유닉스 시각으로 바꾸면 1985-11-05 00:53:20 UTC 입니다(명세 값으로 계산한 값). 모든 입력의 시퀀스 번호가 `0xffffffff` 면 잠금 시각이 적용되지 않습니다[2].

입력 가운데 하나라도 시퀀스 번호가 `0xfffffffe` 보다 작으면, 이 트랜잭션을 다른 트랜잭션으로 바꿔도 된다는 신호(BIP-125, replace-by-fee)가 됩니다[9]. 바꾸는 트랜잭션은 원래 트랜잭션이 낸 수수료 합 이상을 내고, 자기 크기에 해당하는 최소 중계 수수료를 그 위에 더 내야 합니다[9]. Bitcoin Core 28.0 부터 `-mempoolfullrbf` 기본값이 0 에서 1 로 바뀌어, 이 신호가 없는 트랜잭션도 교체를 받아들입니다[10][11].

### 쓸 수 없는 출력과 너무 작은 출력

Null Data 출력(OP_RETURN)은 쓸 수 없다는 것이 스크립트로 드러나는 출력이라서, 풀 노드가 UTXO 데이터베이스에 저장하지 않아도 됩니다[2]. Bitcoin Core 가 기본 설정으로 중계·채굴하는 크기는 버전마다 다릅니다.

| Bitcoin Core 버전 | 기본 한도 |
|---|---|
| 0.9.x~0.10.x | 데이터 푸시 하나에 40바이트, Null Data 출력 1개, 금액 0 사토시[2] |
| 0.11.x | 80바이트, 나머지 규칙은 같음[2] |
| 0.12.0~29.x | 83바이트, 데이터 푸시 수 제한 없음, 출력 1개, 금액 0 사토시[2][11] |
| 30.0 부터 | `-datacarriersize` 기본값 100,000(사실상 한도 없음), 한 트랜잭션에 여러 개 허용, 한도는 모든 OP_RETURN 출력의 합에 적용[11] |

출력 금액이 그 출력을 입력으로 쓰는 데 드는 비용의 1/3 에 못 미치면 더스트(dust)로 보고 비표준으로 처리합니다[2]. 개발자 문서 시점의 기본 중계 수수료에서는 P2PKH·P2SH 출력 546 사토시가 이 경계입니다[2].

## 읽는 법

### 헥스에서 아웃포인트와 금액 찾기

아래는 비트코인 개발자 문서에 실린 원시 트랜잭션 예시입니다[3]. 오른쪽 설명은 이 페이지에서 붙였습니다.

```
01000000                                   버전
01                                         입력 개수
7b1eabe0209b1fe794124575ef807057
c77ada2138ae4fa8d6c4de0398a14f3f           아웃포인트 TXID (내부 바이트 순서)
00000000                                   아웃포인트 출력 번호 = 0
49                                         서명 스크립트 길이 = 73바이트
4830450221...ff866a5f01                    72바이트 푸시(48) + 서명 (줄임)
ffffffff                                   시퀀스 번호
01                                         출력 개수
f0ca052a01000000                           금액 (리틀 엔디언 int64)
19                                         잠금 스크립트 길이 = 25바이트
76a914cbc20a7664f2f69e5355aa427045bc15
e7c6c77288ac                               P2PKH 잠금 스크립트
00000000                                   잠금 시각 = 0 (블록 높이)
```

금액 `f0ca052a01000000` 을 리틀 엔디언 64비트 정수로 읽으면 4,999,990,000 사토시, 곧 49.9999 BTC 입니다[3]. 입력에는 금액이 없어서 이 트랜잭션의 수수료를 알려면 아웃포인트 TXID 의 트랜잭션을 찾아 0번 출력의 금액을 읽어야 합니다. 원시 데이터 안의 TXID 는 내부 바이트 순서이고[3], 블록 해시를 흔히 바이트 순서를 뒤집어 표시하듯[1] 화면에 나온 TXID 와 헥스 안의 TXID 는 순서가 다를 수 있습니다. 헥스 덤프에서 TXID 를 찾을 때는 두 순서를 모두 검색합니다.

### 수수료와 거스름돈 계산

(만든 예시) 트랜잭션 B 의 입력 하나가 트랜잭션 A 의 1번 출력(5,000,000 사토시)을 쓰고, B 의 출력이 0번 3,000,000 사토시와 1번 1,990,000 사토시라면 수수료는 5,000,000 − (3,000,000 + 1,990,000) = 10,000 사토시입니다. 이 숫자만으로는 두 출력 가운데 어느 것이 받는 사람 몫이고 어느 것이 거스름돈인지 알 수 없습니다. 이 구분은 뒤에 나오는 추정이나 기기에 남은 지갑 기록으로 판단합니다.

### 탐색기 API 로 출력 상태 확인하기

Esplora API 로 트랜잭션을 조회하면(`GET /tx/:txid`) `txid`·`version`·`locktime`·`size`·`weight`·`fee`·`vin`·`vout`·`status` 필드가 나옵니다[7]. `vin` 의 입력마다 `txid`·`vout`·`is_coinbase`·`sequence` 와 함께 앞 출력 전체를 담은 `prevout` 이 붙고, `vout` 의 출력마다 `value`·`scriptpubkey_type`·`scriptpubkey_address` 가 나옵니다[7]. `prevout` 은 원시 트랜잭션에 없는 값을 탐색기가 앞 트랜잭션에서 찾아 붙인 것입니다.

출력이 쓰였는지는 `GET /tx/:txid/outspend/:vout` 로 확인합니다. 결과의 `spent` 가 true 면 `txid` 와 `vin` 이 그 출력을 쓴 트랜잭션과 입력 번호를 알려 주고, `status` 에 쓴 트랜잭션의 확정 상태가 나옵니다[7]. 한 트랜잭션의 모든 출력은 `GET /tx/:txid/outspends` 로 한 번에 봅니다[7]. 주소 하나에 걸린 쓰지 않은 출력 목록은 `GET /address/:address/utxo` 로 조회하고, 결과에는 `txid`·`vout`·`value`·`status` 가 있습니다[7].

Bitcoin Core 에서는 `listunspent` 가 지갑이 쓸 수 있는 출력과 각각의 확정 수를 돌려주고[12], `gettransaction` 의 `details` 에는 출력마다 주소·분류·금액·`vout` 이 나옵니다[8].

## 포렌식에서 중요한 점

### 증명하는 것과 증명하지 못하는 것

출력은 한 번만 쓰이므로, 어떤 입력의 아웃포인트가 한 출력을 가리키면 그 출력의 금액이 이 트랜잭션으로 넘어갔다는 연결은 하나로 정해집니다[1][3]. 출력의 금액과 잠금 스크립트(곧 주소)도 블록체인에 그대로 남아 있습니다[3]. 보고서에는 "TXID A 의 1번 출력(5,000,000 사토시)을 TXID B 의 0번 입력이 썼다" 처럼 체인에서 확인되는 연결만 씁니다.

블록체인만으로 증명하지 못하는 것은 다음과 같습니다.

- 출력 가운데 어느 것이 받는 사람 몫이고 어느 것이 거스름돈인지. 프로토콜에 표시가 없어 추정만 할 수 있습니다[2][13].
- 한 트랜잭션의 입력들이 모두 한 사람 것인지. 코인조인(CoinJoin)은 여러 사용자의 입력을 한 트랜잭션에 모읍니다[15].
- 주소와 출력을 누가 통제했는지. 주소는 사람이 아니고, 사람과 잇는 근거는 기기·거래소 기록에서 찾습니다.

### 거스름돈과 공통 입력 추정

블록체인만 보고 주소를 사용자 단위로 묶을 때는 두 가지 추정을 많이 씁니다. 공통 입력 소유 추정(common-input-ownership, C-I-O)은 입력이 둘 이상인 트랜잭션의 입력을 한 사용자 것으로 보고, 거스름돈 추정은 출력 하나를 거스름돈으로 골라 입력과 같은 사용자 것으로 봅니다[15]. 거스름돈 추정은 알려진 변형만 20가지가 넘습니다[15]. BlockSci 는 주소 재사용(`address_reuse`), 입력과 같은 주소 종류(`address_type`), 입력보다 작은 출력(`optimal_change`), 10의 거듭제곱의 배수인 금액 제외(`power_of_ten_value`), 처음 쓰는 주소(`client_change_address_behavior`), 잠금 시각(`locktime`), 필링 체인(`peeling_chain`) 같은 추정을 제공합니다[13]. 이 추정들은 서로 어긋날 수 있어서 하나를 그대로 묶는 데 쓰면 안 되고[13], 묶은 결과가 실제 소유 관계와 맞는다는 보장도 없습니다[14].

추정의 효과는 연구 조건에 따라 달라서 출처와 함께 봅니다. 블록 700,000 까지 분석한 Schnoering 등의 연구에서 C-I-O 계열 추정은 분석할 개체 수를 약 절반으로 줄였고, 거스름돈 주소 추정은 약 15% 줄였으며, 네 추정을 합치면 8억 7,400만 개가 약 2억 5,000만 개로 약 70% 줄었습니다[15]. 이 숫자는 개체 수가 줄어든 비율이지 묶은 결과가 맞은 비율이 아닙니다.

필링 체인(peeling chain)은 한 주소에서 시작해 적은 금액을 거듭 떼어 보내는 사슬입니다[16]. 사슬에 든 트랜잭션의 출력 수는 연구마다 2~5개로 다르게 잡고, Gong 등의 연구는 입력 1개·출력 2개인 트랜잭션이 이어지면서 한 출력으로 일부를 떼어 보내고 다른 출력으로 나머지를 거스름돈으로 받는 사슬로 봅니다[16]. 블록 772,162(2023-01-16 UTC)까지 전체 트랜잭션 796,564,036건을 분석한 Gong 등의 연구에서는 입력 1개인 트랜잭션이 73.15%, 출력 2개인 트랜잭션이 73.97%, 입력 1개·출력 2개인 트랜잭션이 448,723,821건(56.33%)이었습니다[16]. 2022년의 입력 1개·출력 2개 트랜잭션 가운데 거스름돈을 입력과 같은 주소로 돌려보낸 것은 33.36% 였습니다[16]. 출력 2개인 트랜잭션이 거스름돈 없이 받는 사람 둘에게 보낸 것일 수도 있어서, 한 출력이 조건에 맞는다는 이유만으로 거스름돈으로 판정하면 틀린 결과가 나옵니다[16].

트랜잭션의 버전(nVersion), 입력의 시퀀스 번호(nSequence), 잠금 시각(nLockTime) 조합은 그 트랜잭션을 만든 지갑 소프트웨어를 추정하는 지문으로 쓰입니다[17]. 블록 799,000~800,008(약 1주) 전체 트랜잭션을 집계한 Zavřel 등의 연구에서는 버전 1·시퀀스 `0xffffffff`·잠금 시각 0 이 30.03%, 버전 2·시퀀스 `0xffffffff`·잠금 시각 0 이 22.39%, 버전 1·교체 신호·잠금 시각 0 이 21.59% 였고, 버전 2·시퀀스 `0xffffffff`·잠금 시각 값 있음은 0.0023% 였습니다[17]. 지문이 맞는다고 그 트랜잭션이 특정 주체의 것이 되지는 않고, 확률로만 판단합니다[17].

추정을 적용하는 절차는 [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md)와 [비트코인 거래 따라가기](../../03-techniques/analysis/bitcoin-tracing.md)에서 다룹니다.

### 기기에 남은 지갑 기록과 함께 보기

블록체인에는 거스름돈 표시가 없지만, 지갑 앱은 자기가 만든 주소가 거스름돈용인지 알고 기록해 둘 수 있습니다. iOS 용 Coinbase Wallet 은 앱 데이터 폴더의 `Documents/default/wallet-rn-v2.sqlite` 에 있는 `address` 테이블에 주소마다 `isChangeAddressStr` 열을 두고, iLEAPP 는 이 값을 저장된 그대로 보여 줍니다[18]. 앱이 직접 남긴 값이라 체인만 보고 한 추정보다 강한 근거가 될 수 있습니다. 앱별 위치는 [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md)에서, Bitcoin Core 지갑이 잠가 둔 출력(`lockedutxo`) 같은 지갑 파일 기록은 [지갑 파일과 암호화](../wallets/wallet-files.md)에서 다룹니다.

### 시각

UTXO 구조에는 시각 필드가 없습니다. 출력이 언제 생겼고 언제 쓰였는지는 그 출력을 만든 트랜잭션과 쓴 트랜잭션이 들어간 블록의 시각으로 판단합니다. Esplora 의 `status.block_time` 은 확정된 트랜잭션에만 값이 있고 대기 중이면 null 이며[7], Bitcoin Core `gettransaction` 은 블록 시각 `blocktime` 과 지갑이 기록한 `time`·`timereceived` 를 모두 유닉스 시각으로 줍니다[8]. 잠금 시각은 이 시각 이후에 블록에 넣을 수 있다는 하한이지 트랜잭션을 만든 시각이 아닙니다[2]. 블록 시각을 어떻게 믿고 해석할지는 [블록 시각과 확정](block-time.md)에서 다룹니다.

## 함정

**잔액은 저장된 값이 아닙니다.** 잔액은 UTXO 를 더한 값이라서[2], 탐색기나 앱이 보여 주는 잔액은 조회한 시점의 합입니다. 보고서에 잔액을 쓸 때는 조회 시각을 함께 적습니다.

**입력 금액과 주소는 트랜잭션 원문에 없습니다.** 원시 트랜잭션의 입력에는 아웃포인트만 있어서[3], 금액과 주소는 앞 트랜잭션을 찾아야 나옵니다. 탐색기 결과의 `prevout` 과 `fee` 는 탐색기가 계산해 붙인 값입니다[7].

**트랜잭션이 사라질 수 있습니다.** 세그윗을 쓰지 않는 트랜잭션은 서명 스크립트가 바뀌면 TXID 도 바뀔 수 있어서(트랜잭션 가변성, malleability), 대기 중인 트랜잭션은 TXID 가 아니라 그 트랜잭션이 입력으로 쓰는 UTXO 로 추적하는 것이 권장 방법입니다[2]. 교체(RBF)로 같은 입력을 쓰는 다른 트랜잭션이 확정되어도 원래 트랜잭션은 체인에 남지 않습니다. Bitcoin Core 지갑은 같은 입력을 두고 충돌한 트랜잭션 ID 를 `walletconflicts` 에, 교체 가능 여부를 `bip125-replaceable` 에 보여 주고, 확정 수가 음수면 그만큼 앞 블록에서 충돌했다는 뜻입니다[8]. 지갑 기록에 있는 TXID 가 체인에 없으면 같은 아웃포인트를 쓴 트랜잭션을 찾아봅니다.

**코인베이스 입력은 따라가지 않습니다.** 0 해시와 `0xffffffff` 는 앞 트랜잭션을 가리키는 값이 아닙니다[3].

**일부만 담은 데이터로 흐름을 해석할 때 조심합니다.** 시간 구간별로 잘라 만든 데이터셋에서는 코인베이스가 아닌 트랜잭션도 입력이 하나도 없어 보이거나 일부 입력만 남습니다. 공개 연구용 데이터인 Elliptic 비트코인 데이터셋이 이런 구조입니다[19]. 입력이 없는 것처럼 보이면 전체 체인에서 앞 출력을 다시 찾습니다.

**확장 공개 키로 찾은 UTXO 목록은 빠질 수 있습니다.** 2022년 Thomas 등의 연구에서 시험한 도구 7개 가운데 6개는 xpub 만 주면 세그윗 주소를 스스로 계산하지 못했고, 모든 거래를 찾은 도구는 Ledger 의 xpub-scan 하나였습니다[20]. 도구가 계산한 주소 범위 밖의 UTXO 는 목록에서 빠지므로, 주소 탐색 범위(gap limit)는 [복구 문구와 파생 경로](../wallets/seed-derivation.md)를 보고 넓혀 계산합니다.

**"비표준" 은 "무효" 가 아닙니다.** OP_RETURN 크기, 더스트 경계(546 사토시), 교체 정책은 Bitcoin Core 버전과 노드 설정마다 달라지는 중계 정책입니다. 기본 설정이 아닌 노드는 비표준 트랜잭션을 받아들일 수 있고, 블록에 들어간 비표준 트랜잭션은 그대로 처리됩니다[2].

## 도구

**Esplora API.** `GET /tx/:txid`, `GET /tx/:txid/outspend/:vout`, `GET /tx/:txid/outspends`, `GET /address/:address/utxo` 로 출력의 금액·주소 종류와 쓰였는지를 확인합니다[7]. 제3자 서버에 조회하면 수사 대상 주소가 그 서버에 알려지므로[20], 자체 노드와 인덱서를 쓰는 방법은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)를 봅니다.

**Bitcoin Core RPC.** `listunspent` 로 지갑의 쓸 수 있는 출력과 확정 수를[12], `gettransaction` 으로 분류(`send`·`receive`·`generate`·`immature`·`orphan`), 수수료, 충돌 트랜잭션, 교체 가능 여부를 봅니다[8]. 노드 전체의 UTXO 집합은 `chainstate/` 에 있고[4], 데이터 폴더 위치와 버전별 차이는 [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md)에서 다룹니다.

**BlockSci.** 거스름돈 추정과 주소 묶기를 코드로 조합할 수 있는 분석 도구입니다[13][14]. 묶은 결과가 실제와 맞는다는 보장이 없으므로 결과는 조사 단서로만 씁니다[14].

## 참고 문헌

1. Bitcoin Developer Guide, "Block Chain". https://developer.bitcoin.org/devguide/block_chain.html
2. Bitcoin Developer Guide, "Transactions". https://developer.bitcoin.org/devguide/transactions.html
3. Bitcoin Developer Reference, "Transactions — Raw Transaction Format, TxIn, Outpoint, TxOut". https://developer.bitcoin.org/reference/transactions.html
4. Bitcoin Core, `doc/files.md`. https://github.com/bitcoin/bitcoin/blob/master/doc/files.md
5. BIP-141, "Segregated Witness (Consensus layer)". https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki
6. BIP-350, "Bech32m format for v1+ witness addresses". https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki
7. Blockstream Esplora, "Esplora HTTP API" (`API.md`). https://github.com/Blockstream/esplora/blob/master/API.md
8. Bitcoin Core RPC, "gettransaction". https://developer.bitcoin.org/reference/rpc/gettransaction.html
9. BIP-125, "Opt-in Full Replace-by-Fee Signaling". https://github.com/bitcoin/bips/blob/master/bip-0125.mediawiki
10. Bitcoin Core 28.0 Release Notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-28.0.md
11. Bitcoin Core 30.0 Release Notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-30.0.md
12. Bitcoin Developer Guide, "Payment Processing". https://developer.bitcoin.org/devguide/payment_processing.html
13. BlockSci, "Change Address Heuristics" (`docs/reference/heuristics/change.rst`). https://github.com/citp/BlockSci/blob/master/docs/reference/heuristics/change.rst
14. BlockSci, "Clustering" (`docs/reference/clustering/clustering.rst`). https://github.com/citp/BlockSci/blob/master/docs/reference/clustering/clustering.rst
15. Hugo Schnoering, Pierre Porthaux, Michalis Vazirgiannis, 「Assessing the Efficacy of Heuristic-Based Address Clustering for Bitcoin」, arXiv, 2024, doi:10.48550/arXiv.2403.00523
16. Yanan Gong, Kam Pui Chow, Siu Ming Yiu, Hing Fung Ting, 「Analyzing the peeling chain patterns on the Bitcoin blockchain」, Forensic Science International: Digital Investigation 46, 2023, doi:10.1016/j.fsidi.2023.301614
17. Jan Zavřel, Michal Koutenský, Daniel Dolejška, Vladimír Veselý, 「Tumbling down the stairs: Exploiting a tumbler's attempt to hide with ordinary-looking transactions using wallet fingerprinting」, Forensic Science International: Digital Investigation 52, 2025, doi:10.1016/j.fsidi.2025.301869
18. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
19. Miroslav Šafář, Jan Pluskal, Vladimír Veselý, Ondřej Ryšavý, 「The enemy of reproducibility is opacity: What's inside the Elliptic bitcoin dataset (and why it is wrong)」, Forensic Science International: Digital Investigation, 2026, doi:10.1016/j.fsidi.2026.302124
20. Tyler Thomas, Tiffanie Edwards, Ibrahim Baggili, 「BlockQuery: Toward forensically sound cryptocurrency investigation」, Forensic Science International: Digital Investigation 40, 2022, doi:10.1016/j.fsidi.2022.301340
