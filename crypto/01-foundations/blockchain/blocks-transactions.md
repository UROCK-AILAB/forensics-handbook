---
title: "블록과 트랜잭션"
parent: "기반 · 블록체인 기초"
nav_order: 0
---

# 블록과 트랜잭션 (Blocks·Transactions)

블록체인은 트랜잭션을 블록 단위로 묶어 순서와 시각을 붙인 공개 장부이고, 블록마다 앞 블록의 해시가 들어 있어 한 블록을 고치면 뒤따르는 블록이 모두 어긋납니다[1][10]. 지갑 앱과 노드에 남은 트랜잭션 ID·블록 해시·원시 트랜잭션 헥스를 해석하려면 이 구조를 알아야 합니다. 이 페이지는 비트코인의 블록 헤더와 원시 트랜잭션 형식, 이더리움의 블록·트랜잭션·영수증 필드를 다루고, 명세 예시로 헥스를 한 번 따라갑니다.

## 이 형식을 쓰는 아티팩트

블록과 트랜잭션의 구조는 기기에서 나온 값을 블록체인 기록과 맞춰 볼 때 기준이 됩니다. 기기와 기록에는 아래 모양으로 남습니다.

- **풀 노드의 블록 파일.** Bitcoin Core 는 받은 블록을 네트워크 형식 그대로 `blocks/blkNNNNN.dat` 에 파일당 128MiB 씩 쌓고, 블록 인덱스는 `blocks/index/` LevelDB 에, 쓰지 않은 출력(UTXO) 집합은 `chainstate/` LevelDB 에 둡니다[6]. 아직 블록에 들어가지 않은 트랜잭션은 `mempool.dat` 에 덤프됩니다[6]. 폴더 위치와 버전별 차이는 [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md)에서, LevelDB 형식은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)에서 다룹니다.
- **지갑 앱의 트랜잭션 기록.** MetaMask 트랜잭션 컨트롤러의 트랜잭션 항목에는 트랜잭션 해시(`hash`), 원시 트랜잭션 헥스(`rawTx`), 트랜잭션 내용(`txParams`), 블록 번호(`blockNumber`)와 블록 시각(`blockTimestamp`), 영수증(`txReceipt`) 필드가 있습니다[15]. iOS Trust Wallet 의 옛 공개 코드는 트랜잭션마다 `from` 과 `nonce` 를 `-` 로 이어 붙인 값을 고유 ID(`uniqueID`)로 저장합니다[17]. 앱별 저장 위치는 [MetaMask](../../02-artifacts/browser/metamask/index.md), [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md)에서 다룹니다.
- **블록 탐색기와 노드 API 응답.** 탐색기·RPC 가 돌려주는 필드는 이 페이지에서 설명하는 블록·트랜잭션 필드를 그대로 옮기거나 계산해 붙인 값입니다. 읽는 법은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)에서 다룹니다.

주소 문자열의 구조는 [주소 형식](../wallets/address-formats.md)에서, 비트코인 출력이 어떻게 이어지는지는 [비트코인의 UTXO](utxo.md)에서, 이더리움 계정과 이벤트 로그는 [이더리움의 계정과 로그](ethereum-accounts.md)에서 다룹니다.

## 구조

### 비트코인 블록 헤더

비트코인 블록 헤더는 80바이트이고, 작업 증명(proof of work)으로 해시하는 대상이 이 80바이트입니다[2]. 해시 필드는 내부 바이트 순서(internal byte order)로, 나머지 정수는 리틀 엔디언으로 저장합니다[2].

| 오프셋 | 크기 | 필드 | 형식 | 내용 |
|---|---|---|---|---|
| 0 | 4 | version | int32_t | 따를 검증 규칙의 블록 버전[2] |
| 4 | 32 | previous block header hash | char[32] | 앞 블록 헤더를 SHA256 으로 두 번 해시한 값[2] |
| 36 | 32 | merkle root hash | char[32] | 블록 안 모든 트랜잭션 ID 로 만든 머클 루트[2] |
| 68 | 4 | time | uint32_t | 채굴자가 헤더 해시를 시작한 유닉스 시각, 채굴자가 적은 값[2] |
| 72 | 4 | nBits | uint32_t | 목표값(target)을 압축해 적은 값[2] |
| 76 | 4 | nonce | uint32_t | 채굴자가 해시를 바꾸려고 고치는 임의의 수[2] |

블록 버전은 2009년 제네시스 블록의 v1 에서 시작해, 코인베이스에 블록 높이를 넣는 v2(BIP34), 서명을 엄격한 DER 로 제한한 v3(BIP66), `OP_CHECKLOCKTIMEVERIFY` 를 쓰는 v4(BIP65, 2015년 12월 활성화)로 올라갔습니다[2].

블록은 보통 헤더의 해시로 부릅니다. 블록 높이(height)는 제네시스 블록부터 센 번호인데, 채굴자 둘이 거의 같은 때 블록을 만들면 같은 높이에 블록이 여럿 생겨서 높이만으로는 블록 하나를 특정할 수 없습니다[1].

### 비트코인 블록 본문과 머클 루트

직렬화한 블록은 80바이트 헤더 뒤에 트랜잭션 개수(compactSize)와 원시 트랜잭션들이 이어진 모양입니다[2]. 첫 트랜잭션은 반드시 코인베이스(coinbase) 트랜잭션이고, 블록 보조금과 그 블록에 들어간 트랜잭션들의 수수료를 받습니다[2]. 보조금은 50 BTC 에서 시작해 210,000블록마다 절반으로 줄어듭니다[2]. 포크로 블록이 버려지면 그 블록의 코인베이스 트랜잭션도 함께 사라지므로, 코인베이스 출력은 최소 100블록이 지나야 쓸 수 있습니다[1].

머클 루트는 트랜잭션 ID 를 둘씩 이어 SHA256 을 두 번 적용하는 일을 해시가 하나 남을 때까지 되풀이해 만듭니다[2]. 코인베이스의 ID 가 항상 맨 앞이고, 개수가 홀수면 마지막 해시를 자기 자신과 이어 해시합니다[2]. 블록 안 트랜잭션은 머클 트리 첫 줄의 순서대로 저장됩니다[2]. 블록 전체가 없어도 헤더의 머클 루트와 중간 해시 몇 개만 있으면 트랜잭션이 그 블록에 들어 있는지 확인할 수 있습니다[1]. 트랜잭션 5개짜리 블록에서 D 를 확인하려면 C·AB·EEEE 세 해시와 머클 루트만 있으면 됩니다[1].

### 비트코인 원시 트랜잭션

트랜잭션 ID(TXID)는 원시 트랜잭션(raw transaction)을 SHA256 으로 두 번 해시한 값입니다[4]. 원시 트랜잭션의 최상위 필드는 다음과 같습니다[4].

| 크기 | 필드 | 형식 | 내용 |
|---|---|---|---|
| 4 | version | int32_t | 트랜잭션 버전, 현재 1 또는 2(2 는 BIP68 적용) |
| 가변 | tx_in count | compactSize | 입력 개수 |
| 가변 | tx_in | txIn | 입력 |
| 가변 | tx_out count | compactSize | 출력 개수 |
| 가변 | tx_out | txOut | 출력 |
| 4 | lock_time | uint32_t | 유닉스 시각이나 블록 번호 |

입력 하나는 앞 트랜잭션의 출력을 가리키는 36바이트 outpoint(TXID 32바이트 + 출력 번호 4바이트), 서명 스크립트 길이, 서명 스크립트, 4바이트 sequence 로 이뤄집니다[4]. 출력 번호는 0 부터 세고, sequence 는 대부분의 프로그램이 `0xffffffff` 를 씁니다[4]. 출력 하나는 사토시 단위 금액(int64, 8바이트), 잠금 스크립트 길이, 잠금 스크립트입니다[4]. 입력에는 금액 필드가 없고 수수료 필드도 따로 없습니다[4]. 입력 금액과 수수료는 앞 트랜잭션의 출력을 찾아 계산하는데, 그 방법은 [비트코인의 UTXO](utxo.md)에서 다룹니다.

코인베이스 입력은 가리킬 앞 출력이 없어서 TXID 자리에 0 바이트 32개, 출력 번호 자리에 `0xffffffff` 가 들어갑니다[4]. 코인베이스 스크립트는 최대 100바이트이고, BIP34 이후에는 스크립트 맨 앞에 블록 높이가 리틀 엔디언으로 들어갑니다[4].

트랜잭션 개수와 스크립트 길이에 쓰는 compactSize 는 값의 크기에 따라 길이가 달라지는 정수입니다[4].

| 값 | 바이트 수 | 형식 |
|---|---|---|
| 0~252 | 1 | uint8_t |
| 253~0xffff | 3 | `0xfd` + uint16_t |
| 0x10000~0xffffffff | 5 | `0xfe` + uint32_t |
| 그보다 큰 값 | 9 | `0xff` + uint64_t |

명세 예시로 515 는 `fd 03 02` 입니다[4].

### 세그윗 트랜잭션과 두 가지 ID

세그윗(Segregated Witness, BIP141)을 쓰는 트랜잭션에는 ID 가 두 개 있습니다[5]. `txid` 는 예전처럼 `[nVersion][txins][txouts][nLockTime]` 을 SHA256 으로 두 번 해시한 값이고, `wtxid` 는 증인 데이터(witness)까지 넣은 `[nVersion][marker][flag][txins][txouts][witness][nLockTime]` 을 두 번 해시한 값입니다[5]. marker 는 `0x00`, flag 는 지금 `0x01` 로 정해져 있습니다[5]. 세그윗 입력이 하나도 없으면 `wtxid` 와 `txid` 가 같습니다[5]. 서명이 `txid` 계산에서 빠지므로, 세그윗 트랜잭션은 서명 방식이 바뀌어도 ID 가 의도치 않게 달라지지 않습니다[5].

블록 크기 규칙도 바뀌었습니다. 세그윗 뒤로는 블록 무게(block weight)를 "증인 데이터를 뺀 크기 × 3 + 전체 크기" 로 계산해 4,000,000 이하로 제한하고, 트랜잭션의 가상 크기(vsize)는 무게를 4 로 나눠 올림한 값입니다[5].

### 이더리움 블록

이더리움 블록도 트랜잭션 묶음에 앞 블록의 해시를 붙인 것입니다[10]. 지분 증명(proof of stake) 전환 뒤 블록의 최상위 필드는 `slot`, `proposer_index`, `parent_root`, `state_root`, `body` 이고, 트랜잭션은 `body` 안의 `execution_payload` 에 들어 있습니다[10]. `execution_payload` 필드는 `parent_hash`, `fee_recipient`, `state_root`, `receipts_root`, `logs_bloom`, `prev_randao`, `block_number`, `gas_limit`, `gas_used`, `timestamp`, `extra_data`, `base_fee_per_gas`, `block_hash`, `transactions`, `withdrawals` 입니다[10].

노드의 JSON-RPC 가 돌려주는 블록 객체(`eth_getBlockByHash`)는 모양이 조금 다릅니다[12].

| 필드 | 내용 |
|---|---|
| `number`, `hash`, `parentHash` | 블록 번호, 블록 해시(32바이트), 앞 블록 해시. 대기 중인 블록이면 번호와 해시가 `null`[12] |
| `nonce` | 8바이트. 지분 증명 블록(The Merge 이후)은 `0x0`[12] |
| `transactionsRoot`, `stateRoot`, `receiptsRoot` | 트랜잭션·상태·영수증 트라이의 루트[12] |
| `logsBloom` | 로그 블룸 필터, 256바이트[12] |
| `miner` | 블록 보상을 받은 주소[12] |
| `gasLimit`, `gasUsed` | 블록의 가스 한도와 실제로 쓴 가스[12] |
| `timestamp` | 블록을 만든 유닉스 시각[12] |
| `transactions` | 트랜잭션 객체나 32바이트 트랜잭션 해시의 배열[12] |

이더리움 블록 크기는 바이트가 아니라 가스로 제한합니다. 블록마다 목표는 3,000만 가스, 한도는 그 2배인 6,000만 가스이고[10], 검증자가 한도를 앞 블록보다 1/1024 씩 올리거나 내릴 수 있어서 한도는 시기마다 달라집니다[10].

### 이더리움 트랜잭션

이더리움 트랜잭션은 외부 소유 계정(externally owned account)이 서명해 보내는 명령입니다[11]. 보낼 때 담는 정보는 `from`, `to`, 서명, `nonce`(그 계정이 보낸 트랜잭션 순번), `value`(wei 단위, 1 ETH = 10^18 wei), 입력 데이터, `gasLimit`, `maxPriorityFeePerGas`, `maxFeePerGas` 입니다[11]. 입력 데이터의 첫 4바이트는 호출할 함수를 가리키는 함수 선택자(function selector)입니다[11].

트랜잭션 형식은 EIP-2718 에 따라 `TransactionType || TransactionPayload` 로 짜여 있고, 타입 값은 0~0x7f 입니다[11].

| 타입 | 도입 | 특징 |
|---|---|---|
| 0 (레거시) | 처음부터 | `RLP([nonce, gasPrice, gasLimit, to, value, data, v, r, s])`, 앞에 타입 바이트가 없음[11] |
| 1 | EIP-2930, Berlin | `accessList`, `yParity` 추가[11] |
| 2 | EIP-1559, London | `maxPriorityFeePerGas`·`maxFeePerGas`, 지금의 기본 형식[11] |
| 3 (blob) | EIP-4844, Dencun | `blobVersionedHashes`·`maxFeePerBlobGas`[11] |
| 4 | EIP-7702, Pectra | `authorization_list`, 외부 소유 계정이 스마트 컨트랙트에 권한을 위임[11] |

노드에서 트랜잭션을 조회하면(`eth_getTransactionByHash`) `blockHash`, `blockNumber`, `transactionIndex`, `from`, `gas`, `gasPrice`, `hash`, `input`, `nonce`, `to`, `value`, `v`·`r`·`s` 가 나옵니다[12]. 아직 블록에 들어가지 않은 트랜잭션은 블록 관련 세 필드가 `null` 이고, 컨트랙트를 만드는 트랜잭션은 `to` 가 `null` 입니다[12].

수수료는 쓴 가스에 기본 수수료와 우선 수수료를 더한 단가를 곱한 값입니다[13]. 기본 수수료는 소각되고 우선 수수료는 검증자가 받으며, 단순 ETH 이체는 가스 21,000 을 씁니다[13]. 쓰고 남은 가스는 돌려받습니다[11].

### 이더리움 영수증

실행 결과는 트랜잭션이 아니라 영수증(receipt)에 있습니다[12]. `eth_getTransactionReceipt` 는 `transactionHash`, `transactionIndex`, `blockHash`, `blockNumber`, `from`, `to`, `cumulativeGasUsed`, `effectiveGasPrice`, `gasUsed`, `contractAddress`, `logs`, `logsBloom`, `type`, `status` 를 돌려줍니다[12]. `status` 는 1 이 성공, 0 이 실패이고, Byzantium 업그레이드 이전 블록은 `status` 대신 `root` 가 들어 있습니다[12]. 대기 중인 트랜잭션에는 영수증이 없습니다[12]. `logs` 안 이벤트 로그의 구조는 [이더리움의 계정과 로그](ethereum-accounts.md)에서 다룹니다.

## 읽는 법

### 비트코인 블록 헤더를 헥스로 읽기

아래는 비트코인 개발자 문서에 실린 블록 헤더 예시 80바이트입니다[2].

```
02000000                                                          version
b6ff0b1b1680a2862a30ca44d346d9e8910d334beb48ca0c0000000000000000  previous block header hash
9d10aa52ee949386ca9385695f04ede270dda20810decd12bc9b048aaab31471  merkle root
24d95a54                                                          time
30c31b18                                                          nBits
fe9f0864                                                          nonce
```

`02000000` 을 리틀 엔디언으로 읽으면 버전 2 입니다[2]. `24d95a54` 는 1415239972 이고, 유닉스 시각으로 바꾸면 2014-11-06 02:12:52 UTC 입니다(명세 예시를 변환한 값)[2]. `30c31b18` 은 `0x181bc330` 이 되어, 목표값이 `0x1bc330 × 256^(0x18−3)` 이라는 뜻입니다[2].

앞 블록 해시는 헤더 안에서 `…0000000000000000` 으로 끝나지만, 바이트를 뒤집으면 `00000000000000000cca48eb4b330d91e8d946d344ca302a86a280161b0bffb6` 처럼 0 이 앞에 오는 모양이 됩니다(명세 예시를 변환한 값). 이 80바이트 전체를 SHA256 으로 두 번 해시한 뒤 뒤집으면 `000000000000000009a11b3972c8e532fe964de937c9e0096b43814e67af3728` 이 나오고, 이것이 이 블록의 해시입니다(명세 예시로 계산한 값). Bitcoin Core RPC 와 여러 블록 탐색기는 해시를 이렇게 뒤집은 순서(RPC byte order)로 보여 줍니다[19].

### 비트코인 트랜잭션을 헥스로 읽기

비트코인 개발자 문서의 원시 트랜잭션 예시는 158바이트이고, 오프셋별로 나누면 다음과 같습니다[4]. 오프셋은 명세 예시를 세어 붙인 값입니다.

| 오프셋 | 바이트 | 뜻 |
|---|---|---|
| 0 | `01000000` | 버전 1 |
| 4 | `01` | 입력 1개 |
| 5 | `7b1eabe0…98a14f3f` (32바이트) | 쓰는 출력이 있는 트랜잭션의 TXID, 내부 바이트 순서 |
| 37 | `00000000` | 그 트랜잭션의 0번 출력 |
| 41 | `49` | 서명 스크립트 73바이트 |
| 42 | `48 3045…5f01` | 서명 72바이트를 스택에 올리는 스크립트 |
| 115 | `ffffffff` | sequence |
| 119 | `01` | 출력 1개 |
| 120 | `f0ca052a01000000` | 4,999,990,000 사토시(49.9999 BTC) |
| 128 | `19` | 잠금 스크립트 25바이트 |
| 129 | `76 a9 14 cbc20a76…e7c6c772 88 ac` | P2PKH 잠금 스크립트(공개 키 해시 20바이트) |
| 154 | `00000000` | lock_time 0 |

outpoint 의 TXID `7b1eabe0…98a14f3f` 도 내부 바이트 순서라, 탐색기나 RPC 에서 찾을 때는 뒤집은 `3f4fa19803dec4d6…20e0ab1e7b` 로 찾습니다(명세 예시를 변환한 값). 버전 4바이트 바로 뒤가 `00 01` 이면 세그윗 marker 와 flag 이므로, 입력 개수는 그 다음 바이트부터 읽습니다[5].

코인베이스 예시에서는 입력의 TXID 자리가 0 바이트 32개, 출력 번호가 `ffffffff` 이고, 코인베이스 스크립트가 `03 4e0105` 로 시작합니다[4]. `03` 은 뒤따르는 3바이트를 올린다는 뜻이고, `4e0105` 를 리틀 엔디언으로 읽으면 블록 높이 328014 입니다[4]. 그래서 BIP34 이후 블록은 코인베이스 트랜잭션만 봐도 블록 높이를 알 수 있습니다.

### 이더리움 트랜잭션 첫 바이트로 종류 구분하기

서명된 이더리움 트랜잭션 헥스는 첫 바이트로 형식을 구분합니다. 타입 트랜잭션은 첫 바이트가 타입 값(`0x01`, `0x02`, `0x03`, `0x04`)이고[11], 레거시 트랜잭션은 RLP 리스트라 첫 바이트가 `0xc0` 이상입니다[14]. RLP 는 페이로드가 55바이트 이하인 리스트를 `0xc0`~`0xf7` 로, 그보다 긴 리스트를 `0xf8`~`0xff` 로 시작합니다[14]. 서명된 레거시 트랜잭션은 `r`·`s` 만으로도 55바이트를 넘으므로 `0xf8` 이상으로 시작하고, 페이로드가 256바이트 이상이면 길이를 2바이트로 적어서 `0xf9` 로 시작합니다(RLP 규칙으로 계산한 값)[14].

ethereum.org 트랜잭션 문서의 서명 응답 예시는 `f8 83` 으로 시작합니다[11]. `f8` 은 길이를 1바이트로 적은 긴 리스트라는 뜻이고, 다음 바이트 `0x83` 은 페이로드 131바이트라서 전체 133바이트가 됩니다(명세 예시로 계산한 값)[14].

노드 JSON-RPC 의 값은 두 가지로 인코딩합니다. 수량(QUANTITY)은 `0x` 뒤에 앞자리 0 없이 가장 짧게 쓰고 0 만 `0x0` 으로 쓰며, 바이트 데이터(DATA)는 `0x` 뒤에 바이트마다 헥스 두 자리를 씁니다[12]. 그래서 해시는 항상 `0x` 뒤 헥스 64자이지만, `value`·`nonce`·`blockNumber` 는 값에 따라 길이가 다릅니다. `value` 는 wei 단위 정수라 10^18 로 나눠야 ETH 가 됩니다[11]. iLEAPP 의 MetaMask 분석기도 헥스 `value` 를 정수로 바꾼 뒤 10^18 로 나눠 ETH 로 보여 줍니다[16].

## 포렌식에서 중요한 점

### 증명하는 것과 증명하지 못하는 것

블록체인 기록으로는 이 TXID(이더리움은 트랜잭션 해시)의 트랜잭션이 이 해시·높이의 블록에 들어 있고, 그 블록이 지금 체인에 있다는 것까지 확인됩니다. 비트코인은 머클 루트와 중간 해시로 포함 여부를 직접 검증할 수 있습니다[1]. 이더리움 트랜잭션에는 보낸 사람의 개인 키로 만든 서명이 들어 있어서, 그 개인 키로 이 트랜잭션에 서명했다는 것까지 확인됩니다[11].

누가 키를 쥐고 있었는지, 어느 기기에서 트랜잭션을 만들었는지는 블록체인에 나오지 않습니다. 그 연결은 기기의 지갑 앱 기록으로 따로 보여야 합니다. 이더리움에서 블록에 들어 있다는 것도 성공했다는 뜻이 아닙니다. 실패한 트랜잭션도 수수료를 내므로[13], 영수증의 `status` 가 1 인지 확인합니다[12].

### 시각

비트코인 헤더의 `time` 은 채굴자가 적은 값이라 트랜잭션을 보낸 시각이 아닙니다[2]. 이 값은 앞 11블록 시각의 중앙값보다 커야 하고, 풀 노드는 자기 시계보다 2시간 넘게 앞선 헤더를 받지 않습니다[2]. 그래서 블록 시각이 앞 블록보다 이를 수도 있습니다. 이더리움은 12초 슬롯마다 검증자 한 명이 블록을 제안하고, `timestamp` 는 그 블록의 시각입니다[10]. 두 체인 모두 UTC 기준 유닉스 초이고, 블록 시각은 트랜잭션을 보낸 시각이 아니라 블록이 만들어진 시각입니다. 블록 시각과 확정 수를 해석하는 법은 [블록 시각과 확정](block-time.md)에서 다룹니다.

### 블록에 들어가지 않은 트랜잭션

트랜잭션은 먼저 네트워크에 퍼져 대기열에 머물다가 블록에 들어갑니다. 비트코인에서는 이 대기열을 mempool[6], 이더리움에서는 트랜잭션 풀(transaction pool)[11]이라고 부릅니다. 지갑 앱에 기록된 트랜잭션 해시가 블록체인에서 조회되지 않으면, 아직 대기 중이거나 다른 트랜잭션으로 바뀌었거나 네트워크로 보내지 않은 것일 수 있습니다. Bitcoin Core 는 mempool 의 트랜잭션을 `mempool.dat` 에 덤프하므로[6], 블록에 들어가지 못한 트랜잭션의 흔적이 이 파일에 있을 수 있습니다.

### 포크로 버려진 블록

같은 높이에 블록이 둘 생기면 노드는 결국 작업량이 더 많은 체인을 따르고, 짧은 쪽의 블록(stale block)은 버립니다[1]. 버려진 블록의 코인베이스 트랜잭션은 함께 사라지고[1], 그 블록에만 있던 트랜잭션은 주 체인의 다른 블록에 들어가야 다시 확정됩니다. Bitcoin Core `getblock` 은 주 체인이 아닌 블록의 확정 수를 -1 로 돌려줍니다[8]. 특정 블록 해시를 근거로 쓸 때는 그 블록이 지금 주 체인에 있는지 함께 확인합니다.

## 함정

**해시 바이트 순서가 두 가지입니다.** 블록과 트랜잭션 안의 해시는 내부 바이트 순서이고, Bitcoin Core RPC 와 여러 블록 탐색기는 뒤집은 순서로 보여 줍니다[2][19]. 이미지에서 TXID 나 블록 해시를 검색할 때는 두 순서를 모두 검색합니다. 문자열 검색 절차는 [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md)에서 다룹니다.

**블록 높이는 블록 하나를 특정하지 못합니다.** 포크가 생기면 같은 높이에 블록이 여럿 있을 수 있습니다[1]. 보고서에는 높이와 블록 해시를 같이 적습니다.

**세그윗 이전 비트코인 트랜잭션은 ID 가 바뀔 수 있습니다.** 서명 스크립트는 서명 대상에 들어가지 않아서, 누군가 서명 스크립트를 고치면 트랜잭션은 그대로 유효한데 TXID 만 달라집니다[3]. 그러면 지갑이 기록한 TXID 가 네트워크에서 사라진 것처럼 보이므로, 트랜잭션은 TXID 대신 그 트랜잭션이 입력으로 쓰는 출력(UTXO)으로 따라갑니다[3]. 세그윗은 이런 의도치 않은 변형을 막습니다[5].

**블록 크기 설명이 문서마다 다릅니다.** 비트코인 개발자 문서는 직렬화한 블록이 1MB 이하여야 한다고 적었는데, 이는 세그윗 이전 규칙입니다[2]. 같은 문서의 보조금 설명도 "2017년 11월 기준 12.5 BTC" 로 멈춰 있습니다[2]. 블록 크기는 지금 BIP141 의 무게 4,000,000 규칙을 따릅니다[5].

**레거시 이더리움 트랜잭션이 모두 `0xf8` 로 시작하지는 않습니다.** ethereum.org 트랜잭션 문서는 레거시 트랜잭션이 `0xf8` 로 시작한다고 적었지만[11], RLP 규칙상 긴 리스트는 길이를 적는 바이트 수에 따라 `0xf8`~`0xff` 로 시작합니다[14]. 입력 데이터가 긴 레거시 트랜잭션은 `0xf9` 로 시작하므로, 첫 바이트가 `0xc0` 이상이면 레거시, `0x01`~`0x04` 면 타입 트랜잭션으로 구분합니다.

**Bitcoin Core 28.0 부터 블록 파일을 헥스로 바로 읽을 수 없습니다.** 28.0 부터 블록 파일은 기본으로 XOR 처리되고, 키는 블록 폴더의 `xor.dat` 에 있습니다[7][6]. 키로 XOR 을 풀기 전에는 원래 블록 바이트가 보이지 않습니다. 같은 버전에서 Windows 기본 데이터 폴더가 `%APPDATA%\Bitcoin`(Roaming)에서 `%LOCALAPPDATA%\Bitcoin`(Local)으로 바뀌었고, 옛 폴더가 있으면 그대로 씁니다[7].

## 도구

**Bitcoin Core RPC.** `getblock` 은 `verbosity` 가 0 이면 직렬화한 블록 헥스를, 1 이면 `hash`·`confirmations`·`height`·`version`·`merkleroot`·`tx`·`time`·`mediantime`·`nonce`·`bits`·`previousblockhash` 등이 든 JSON 을, 2 면 트랜잭션 내용까지 돌려줍니다[8]. 헥스를 직접 풀어 본 결과를 이 JSON 과 맞춰 보면 해석이 맞았는지 확인할 수 있습니다.

**Esplora API.** Blockstream 이 공개한 블록 탐색기 API 로, `GET /tx/:txid/hex` 는 원시 트랜잭션 헥스를, `GET /tx/:txid/merkle-proof` 는 머클 포함 증명을, `GET /block/:hash/header` 는 헤더 헥스를, `GET /block/:hash/txids` 는 블록 안 TXID 목록을 돌려줍니다[9].

**이더리움 JSON-RPC.** `eth_getBlockByHash`, `eth_getTransactionByHash`, `eth_getTransactionReceipt` 로 이 페이지의 필드를 노드에서 직접 받습니다[12].

**직접 운영하는 노드.** 제3자가 운영하는 탐색기에 주소와 TXID 를 조회하면, 운영자가 조회한 IP 와 조사 대상 주소를 연결할 수 있고 응답이 정확한지도 보장되지 않습니다[18]. BlockQuery 논문은 이런 이유로 풀 노드와 로컬 인덱서(electrs)를 조사 환경으로 제안합니다[18]. 탐색기 기록을 증거로 쓸 때 볼 점은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)에서, 흐름을 따라가는 방법은 [비트코인 거래 따라가기](../../03-techniques/analysis/bitcoin-tracing.md)와 [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md)에서 다룹니다.

## 참고 문헌

1. Bitcoin Developer Guide, "Block Chain". https://developer.bitcoin.org/devguide/block_chain.html
2. Bitcoin Developer Reference, "Block Chain". https://developer.bitcoin.org/reference/block_chain.html
3. Bitcoin Developer Guide, "Transactions — Transaction Malleability". https://developer.bitcoin.org/devguide/transactions.html
4. Bitcoin Developer Reference, "Transactions — Raw Transaction Format, CompactSize Unsigned Integers". https://developer.bitcoin.org/reference/transactions.html
5. BIP-141, "Segregated Witness (Consensus layer)". https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki
6. Bitcoin Core, `doc/files.md`. https://github.com/bitcoin/bitcoin/blob/master/doc/files.md
7. Bitcoin Core 28.0 Release Notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-28.0.md
8. Bitcoin Developer Reference, RPC "getblock". https://developer.bitcoin.org/reference/rpc/getblock.html
9. Blockstream, Esplora HTTP API. https://github.com/Blockstream/esplora/blob/master/API.md
10. ethereum.org, "Blocks". https://ethereum.org/en/developers/docs/blocks/
11. ethereum.org, "Transactions". https://ethereum.org/en/developers/docs/transactions/
12. ethereum.org, "JSON-RPC API". https://ethereum.org/en/developers/docs/apis/json-rpc/
13. ethereum.org, "Gas and fees". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/gas/index.md
14. ethereum.org, "Recursive-length prefix (RLP) serialization". https://ethereum.org/en/developers/docs/data-structures-and-encoding/rlp/
15. MetaMask core, `packages/transaction-controller/src/types.ts`. https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/types.ts
16. iLEAPP, `scripts/artifacts/metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
17. Trust Wallet iOS, `Trust/Transactions/Storage/Transaction.swift`. https://github.com/trustwallet/trust-wallet-ios/blob/master/Trust/Transactions/Storage/Transaction.swift
18. Tyler Thomas, Tiffanie Edwards, Ibrahim Baggili, 「BlockQuery: Toward forensically sound cryptocurrency investigation」, Forensic Science International: Digital Investigation 40, 2022, doi:10.1016/j.fsidi.2022.301340
19. Bitcoin Developer Glossary, "Internal byte order", "RPC byte order". https://developer.bitcoin.org/glossary.html
