---
title: "비트코인 거래 따라가기"
parent: "기법 · 분석"
nav_order: 290
---

# 비트코인 거래 따라가기 (Bitcoin Tracing)

비트코인은 지갑에서 지갑으로가 아니라 트랜잭션에서 트랜잭션으로 옮겨 가서, 돈의 흐름은 "어느 트랜잭션의 몇 번째 출력을 어느 트랜잭션이 썼는가" 를 한 단계씩 이어 붙여 되살립니다[2]. 이 페이지는 기기에서 찾은 트랜잭션 ID·주소·확장 공개 키에서 출발해 앞뒤로 흐름을 따라가는 절차와, 그 결과 가운데 블록체인으로 확인되는 부분과 추정인 부분을 나누는 방법을 다룹니다. 출력과 입력의 구조는 [비트코인의 UTXO](../../01-foundations/blockchain/utxo.md)에서, 원시 트랜잭션의 전체 형식은 [블록과 트랜잭션](../../01-foundations/blockchain/blocks-transactions.md)에서 다룹니다.

## 언제 쓰나

기기나 거래소 자료에서 비트코인 트랜잭션 ID(TXID)나 주소가 나왔고, 그 돈이 어디서 왔는지 또는 어디로 갔는지 알아야 할 때 씁니다. 흔한 경우는 다음과 같습니다.

- 피해자 지갑에서 나간 돈이 어느 주소를 거쳐 어디에 이르렀는지 확인할 때
- 피의자 기기의 지갑 기록에 있는 입금이 어디서 왔는지 거슬러 올라갈 때
- 기기에서 확장 공개 키(extended public key, xpub)를 찾아 그 지갑이 주고받은 거래 전체를 모을 때
- 흐름의 끝이 거래소 입금 주소인지 확인해 거래소에 자료를 요청할 근거를 만들 때

이더리움처럼 계정 잔액을 기록하는 체인은 따라가는 방법이 달라서 [이더리움 거래 따라가기](ethereum-tracing.md)에서 다룹니다.

## 절차

### 1. 시작점을 정리합니다

기기에서 나온 값을 TXID, 주소, 확장 공개 키 세 종류로 나눕니다. 메모리·파일에서 주소와 TXID 문자열을 찾는 방법은 [주소와 트랜잭션 ID 찾기](../acquisition/address-carving.md)에서, 지갑 파일과 앱 데이터에서 확장 공개 키와 파생 경로를 찾는 곳은 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)와 [하드웨어 지갑과 연결 흔적](../../02-artifacts/hardware/hardware-wallets.md)에서 다룹니다.

추적의 단위는 주소가 아니라 출력입니다. 입력은 앞 트랜잭션의 TXID 와 출력 번호(vout, 첫 출력이 0)로 쓸 출력 하나를 가리키므로[1][3], 시작점도 `TXID:vout` 형식으로 적어 둡니다. 주소 하나에는 여러 출력이 걸려 있을 수 있어서 주소만 적으면 어느 돈을 따라가는지가 흐려집니다.

### 2. 조회할 곳을 정합니다

Bitcoin Core 에는 주소 하나가 관여한 거래 전체를 돌려주는 API 가 없어서, 주소 단위로 조회하려면 인덱서(indexer)를 함께 돌려야 합니다[12]. electrs 는 Bitcoin Core 노드와 동기화해 과거 거래를 조회해 주는 인덱서로, 제3자 서버와 통신하지 않습니다[12]. Esplora API 는 blockstream.info 공개 서버 말고도 직접 설치해 운영할 수 있습니다[5].

제3자 탐색기에 주소를 넣으면 운영자가 조회한 IP 와 주소를 이어 볼 수 있어 수사 대상이 드러날 수 있고, 돌아온 결과가 빠짐없고 정확한지는 직접 가진 원장 사본과 비교해야만 확인할 수 있습니다[12]. 그래서 민감한 사건은 직접 운영하는 노드와 인덱서로 조회합니다. 탐색기 응답을 보존하는 방법은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)에서 다룹니다.

Bitcoin Core RPC 는 그 컴퓨터에 접근할 수 있는 사람이 설정을 바꿔, 가장 긴 체인에 없는 트랜잭션을 여러 번 확정된 것처럼 보이게 할 수 있습니다[11]. 조사용 노드는 조사하는 쪽만 쓰는 시스템에 둡니다.

### 3. 트랜잭션 한 건을 확인합니다

Esplora 에서 `GET /tx/:txid` 로 트랜잭션을 받으면 `vin[]`(입력), `vout[]`(출력), `fee`, `status` 필드가 나오고, 금액은 모두 사토시 단위입니다[5]. 원시 트랜잭션은 `GET /tx/:txid/hex` 로 받아 따로 보존합니다[5]. 헥스에서 버전 4바이트 바로 뒤가 `00 01` 이면 증인 데이터가 붙은 세그윗(SegWit) 직렬화이고, 이때도 TXID 는 증인을 뺀 전통 직렬화의 해시라서[4] 탐색기 조회에는 `wtxid` 가 아니라 `txid` 를 씁니다[5].

트랜잭션이 블록에 들어갔는지는 `status` 의 `confirmed`·`block_height`·`block_hash`·`block_time` 으로 확인합니다[5]. 같은 높이에 블록이 여럿 생길 수 있어서 블록은 높이가 아니라 해시로 기록합니다[2]. 그 블록이 지금 가장 긴 체인에 있는지는 Esplora `GET /block/:hash/status` 의 `in_best_chain` 으로 보고(버려진 블록이면 false)[5], Bitcoin Core 에서는 `getblock` 의 `confirmations` 가 -1 이면 메인 체인 밖 블록입니다[9]. 블록 포함 증명이 필요하면 `GET /tx/:txid/merkle-proof` 로 머클 증명을 받아 둡니다[5]. 확정 수를 몇으로 볼지는 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에서 다룹니다.

### 4. 뒤로 따라갑니다 (돈이 어디서 왔나)

입력마다 `vin[].txid` 와 `vin[].vout` 이 앞 출력을 가리킵니다[5]. 원시 트랜잭션의 입력에는 금액과 주소가 없고[3], Esplora 응답에서는 앞 출력 전체가 `prevout` 에 붙어 나옵니다[5]. 그 TXID 로 다시 3단계를 되풀이하면 한 단계 앞으로 올라갑니다.

`is_coinbase` 가 true 인 입력은 앞 출력이 없는 코인베이스 입력이라서[3][5] 거기서 거슬러 올라가기가 끝납니다. 코인베이스 입력의 모양은 [비트코인의 UTXO](../../01-foundations/blockchain/utxo.md)에서 다룹니다. 입력이 여러 개면 따라갈 경로가 입력 수만큼 늘어나므로, 금액이 큰 입력부터 따라가거나 조사 질문과 관계있는 입력만 고릅니다.

### 5. 앞으로 따라갑니다 (돈이 어디로 갔나)

출력 하나가 쓰였는지는 `GET /tx/:txid/outspend/:vout` 로 확인합니다. `spent` 가 true 면 `txid` 와 `vin` 이 그 출력을 쓴 트랜잭션과 입력 번호입니다[5]. 한 트랜잭션의 모든 출력은 `GET /tx/:txid/outspends` 로 한 번에 봅니다[5]. `spent` 가 false 면 그 출력은 조회한 시점에 아직 쓰이지 않은 출력(UTXO)이라서 거기서 멈추고, 조회 시각을 함께 적습니다.

OP_RETURN 출력(Null Data)은 쓸 수 없는 출력이라서[1] 따라갈 곳이 아니라 데이터 기록으로 봅니다. OP_RETURN 출력에는 올바른 비트코인 주소가 없고, 0.00000001 BTC 처럼 금액이 붙은 OP_RETURN 출력도 있으므로[14] 금액이 0 이 아니라는 것만으로 따라갈 출력으로 보지 않습니다.

### 6. 주소 단위로 넓힙니다

한 주소에 들어오고 나간 거래 전체는 `GET /address/:address/txs` 로 받습니다. 최신 거래부터 미확정 최대 50건과 확정 25건이 나오고, 그 뒤는 `GET /address/:address/txs/chain/:last_seen_txid` 로 마지막으로 본 TXID 를 넘겨 25건씩 이어 받습니다[5]. 첫 응답만 보고 거래가 25건뿐이라고 판단하지 않습니다.

주소를 넓히면 그 주소의 다른 출력까지 끌려 들어옵니다. 따라가던 출력과 관계없는 입출금이 섞이므로, 단계마다 어느 출력에서 왔는지(`TXID:vout`)를 기록에 남겨 흐름을 구분합니다.

### 7. 확장 공개 키로 지갑의 주소를 모읍니다

확장 공개 키가 있으면 그 계정 아래 주소를 다시 계산해 거래를 모을 수 있습니다. BIP-44 경로는 `m / purpose' / coin_type' / account' / change / address_index` 이고, change 0 은 받는 주소(외부 체인), 1 은 거스름돈 주소(내부 체인)입니다[6]. 거스름돈 주소는 확장 키 없이는 보낸 주소와 이을 수 없어서, 지갑의 입출금을 빠짐없이 보려면 두 체인을 모두 계산합니다[12].

지갑이 복구할 때 쓰는 규칙은 연속 20개가 비면 멈추고(gap limit 20) 외부 체인만 살피는 것이라서[6], 도구도 이 규칙만 따르면 거스름돈 주소와 멀리 떨어진 주소를 놓칩니다. 표준을 벗어나 20보다 큰 간격으로 주소를 만들 수도 있고, 빠짐없이 확인하려면 한 경로의 자식 주소 2^31 개를 모두 살펴야 합니다[12]. 실무에서는 간격을 넓혀 계산하고, 넓힌 범위를 기록에 적습니다.

`xpub`·`ypub`·`zpub` 은 각각 P2PKH(1…)·P2SH 로 감싼 세그윗(3…)·네이티브 세그윗(bc1…) 주소에 대응하고 서로 바꿀 수 있어서, 키 하나로 세 형식을 모두 계산해 봐야 합니다[12]. Ledger Nano X 와 Ledger Live 로 만든 거래와 주소 간격을 100 으로 벌린 지갑으로 공개 조회 도구 7개를 시험한 연구에서, 6개는 xpub 에서 세그윗 주소를 스스로 계산하지 못했고 몇몇은 ypub·zpub 을 줘도 세그윗 거래를 찾지 못했습니다[12]. 모든 거래를 찾은 도구는 Ledger 의 xpub-scan 하나였고, 이 도구는 Ledger 서버로 조회합니다[12].

Bitcoin Core 디스크립터 지갑에서는 `listdescriptors` 로 지갑의 확장 공개 키를 꺼낼 수 있습니다[7]. 디스크립터의 `/*` 범위는 따로 정하지 않으면 `0-1000` 이고, `/<0;1>/*` 처럼 적힌 다중 경로는 받는 주소(/0)와 거스름돈 주소(/1)를 함께 가리킵니다[7]. 경로 표기를 읽는 법은 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)에서 다룹니다.

### 8. 다음에 따라갈 출력을 고릅니다

출력이 둘 이상이면 어느 출력이 받는 사람 몫이고 어느 출력이 거스름돈인지 골라야 다음 단계로 갈 수 있습니다. 프로토콜에는 거스름돈 표시가 없어서 이 선택은 추정입니다. 트랜잭션 모양(`<입력 주소 수:출력 주소 수>`, few 는 5개 이하, many 는 6개 이상)은 판단의 출발점으로 쓰기 좋습니다[13].

`<few:2>`(흔히 `<1:2>`)는 보통 받는 사람 1명과 거스름돈 1개로 해석하고, 입력 주소가 출력에도 나오면 그 출력을 거스름돈으로 봅니다[13]. `<1:1>` 은 같은 사람이 자기 주소로 옮긴 것일 수도, 금액이 딱 맞아 거스름돈 없이 남에게 보낸 것일 수도 있습니다[13]. `<1:many>` 는 거래소 출금처럼 여러 사람에게 한꺼번에 보낸 일괄 지급으로 볼 수도, 한 사람이 여러 주소로 흩뿌린 것으로 볼 수도 있습니다[13]. 코인조인(CoinJoin) 구현별 모양은 [믹서와 추적을 어렵게 하는 방법](../../01-foundations/ecosystem/mixers.md)에서 다룹니다.

필링 체인(peeling chain)은 주로 `<1:2>` 트랜잭션이 이어지면서 큰 금액을 조금씩 떼어 여러 주소로 보내는 사슬이고, 참여한 주소 하나를 찾으면 앞뒤로 따라갈 수 있습니다[13]. 믹서 시험 거래에서는 거스름돈 쪽 출력이 다시 `<1:2>` 로 쓰이면 사슬이 이어지고, `<1:1>` 로 쓰이면 사슬이 끝나고, `<many:1>` 로 다른 출력과 합쳐지면 사슬이 새로 시작됐습니다[13]. 거스름돈 추정의 종류와 주소를 사용자 단위로 묶는 방법은 [주소 묶기와 그 한계](clustering.md)에서 다룹니다.

기기에 지갑 앱 데이터가 있으면 이 추정을 기록으로 바꿀 수 있습니다. BIP-44 를 따르는 지갑은 거스름돈 주소를 내부 체인(change 1)에서 만들므로[6], 지갑 데이터에서 그 주소의 파생 경로를 확인하면 체인만 보고 한 추정보다 강한 근거가 됩니다. 앱별 예는 [비트코인의 UTXO](../../01-foundations/blockchain/utxo.md)의 "기기에 남은 지갑 기록과 함께 보기" 에 있습니다.

### 9. 끝점을 확인합니다

흐름은 대개 아래 가운데 하나에서 멈춥니다.

| 끝점 | 체인에서 보이는 모양 | 다음 할 일 |
|---|---|---|
| 아직 쓰지 않은 출력 | `outspend` 의 `spent` 가 false[5] | 조회 시각과 함께 잔액으로 기록 |
| 채굴 보상 | 입력의 `is_coinbase` 가 true[5] | 거슬러 올라가기 종료 |
| 데이터 기록 | OP_RETURN 출력[1] | 따라가지 않음 |
| 거래소 입금 | 다른 고객의 거래와 섞인 주소 | [거래소 자료 분석](exchange-analysis.md)으로 넘어감 |
| 믹서·코인조인 | 같은 금액 출력 여럿, 필링 체인 | [믹서와 추적을 어렵게 하는 방법](../../01-foundations/ecosystem/mixers.md) 참고 |

거래소 같은 서비스의 주소 하나에는 여러 고객의 거래가 섞일 수 있습니다. 안드로이드 지갑 시험 거래 한 건에 나온 주소가 2021년 7월 기준 1,361번 거래하고 1억 달러 넘게 주고받은 주소라서, 시험 기기의 지갑만 쓰는 주소가 아니었던 사례가 있습니다[16]. 이 지점부터 누가 입금했는지는 체인이 아니라 거래소가 가진 자료로 확인합니다. 거래소에 무엇을 요청할 수 있는지는 [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md)와 [거래소로 들어갔나](../../04-scenarios/asset-flow/exchange-deposit.md)에서 다룹니다.

### 10. 단계마다 기록을 남깁니다

따라간 단계마다 체인에서 확인되는 값과 판단이 섞이지 않게 적습니다. 아래는 기록 표의 예이고, 값은 모두 만든 예시입니다.

| 단계 | 쓴 출력 | 쓴 트랜잭션·입력 | 금액(사토시) | 블록 해시·높이 | 블록 시각(UTC) | 다음 출력을 고른 근거 |
|---|---|---|---|---|---|---|
| 1 | `aa11…:0` | `bb22…` 의 0번 입력 | 5,000,000 | `0000…c3d4`, 800,100 | 2023-07-25 04:10:12 | 기기의 지갑 기록 |
| 2 | `bb22…:1` | `cc33…` 의 0번 입력 | 1,990,000 | `0000…e5f6`, 800,115 | 2023-07-25 06:41:50 | 추정: 입력과 같은 주소 종류 |

"쓴 출력" 부터 "블록 시각" 까지는 누가 조회해도 같은 값이 나오는 체인 데이터이고, 마지막 열은 조사하는 쪽의 판단입니다. 판단 열에 추정이라고 적힌 단계 뒤의 흐름은 모두 그 추정에 기댄 것이므로 보고서에서도 구분해 씁니다. 보고서에 옮기는 방법은 [암호화폐 포렌식 보고서](../reporting/forensic-report.md)에서 다룹니다.

## 도구

**Esplora API.** 트랜잭션·출력 상태·주소 거래 목록·머클 증명을 조회하고 직접 운영할 수 있습니다[5]. 필드 목록은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)에서 다룹니다.

**Bitcoin Core 와 electrs.** Bitcoin Core 노드에 electrs 인덱서를 붙이면 제3자 서버 없이 주소별 거래를 조회할 수 있습니다[12]. 지갑 파일이 있으면 `gettransaction` 으로 충돌한 트랜잭션 목록(`walletconflicts`)과 교체 가능 여부(`bip125-replaceable`)를 볼 수 있습니다[8].

**BlockQuery.** 확장 공개 키로 세 주소 형식과 두 체인을 모두 계산하고, 탐색 깊이를 정할 수 있고, 로컬 electrs 만 조회하는 오픈소스 개념 증명 도구입니다[12].

**xpub 조회 도구.** LedgerHQ/xpub-scan, dan-da/hd-wallet-addrs, mewald55/Blockpath 가 있습니다[12]. xpub-scan 은 세 주소 형식을 모두 계산하고 범위를 조절할 수 있지만 Ledger 서버로 조회하고, Blockpath 는 간격 한도를 20 대신 150 으로 씁니다[12].

**그래프 분석.** BlockSci 는 거스름돈 추정과 주소 묶기를 코드로 조합할 수 있지만 2020년 11월 이후 개발이 멈췄습니다[14]. Neo4j 그래프 데이터베이스에 체인 데이터를 넣어 최단 경로 같은 질의로 흐름을 찾는 방법도 쓰입니다[15].

## 함정과 한계

**TXID 바이트 순서.** 원시 트랜잭션 안의 TXID 는 내부 바이트 순서이고[3], Bitcoin Core RPC 와 많은 블록 탐색기는 해시를 바이트를 뒤집은 순서로 보여 줍니다[2][19]. 헥스에서 잘라 낸 값을 그대로 넣으면 검색되지 않으므로 뒤집은 값으로도 조회합니다.

**사라진 것처럼 보이는 TXID.** 서명 스크립트는 서명으로 보호되지 않아서 세그윗을 쓰지 않는 트랜잭션은 내용을 바꾸지 않고도 TXID 가 바뀔 수 있고, 그러면 트랜잭션이 네트워크에서 사라진 것처럼 보입니다[1]. BIP-125 교체 신호가 있는 미확정 트랜잭션은 같은 입력을 쓰는 다른 트랜잭션으로 바뀔 수 있습니다[10]. 그래서 트랜잭션은 TXID 가 아니라 입력으로 쓰는 출력으로 추적하는 것이 권장 방법입니다[1]. 지갑 기록의 TXID 가 체인에 없으면 같은 `TXID:vout` 을 쓴 트랜잭션을 `outspend` 로 찾습니다.

**도구가 새 주소 형식을 못 읽는 경우.** BlockSci 는 `WitnessUnknownAddress` 형식 출력의 주소 문자열을 만들지 못합니다[14]. btc-csv 는 2020년에 마지막으로 갱신된 옛 주소 해독 라이브러리를 써서 탭루트(Taproot) 트랜잭션을 처리하지 못합니다[15]. 도구 결과에 주소가 비어 있으면 거래가 없는 것인지 도구가 못 읽은 것인지 원시 트랜잭션으로 확인합니다.

**주소 모양 목록만 믿는 경우.** SWGDE 기술 노트(2024-12)는 비트코인 주소를 "1 또는 3 으로 시작하는 25~36자" 로만 적었습니다[17]. 이 목록만으로 기기에서 주소를 찾으면 `bc1` 로 시작하는 주소를 놓칩니다. 주소 형식 전체는 [주소 형식](../../01-foundations/wallets/address-formats.md)에서 다룹니다.

**짧은 필링 체인.** 거래 2~3회로 끝나는 짧은 사슬은 일반 사용자의 연속 지급에서도 생기고, 2023년 1월까지의 블록에서 뽑은 필링 체인 후보 가운데 68.99% 가 이 길이였습니다[14]. 입력 1개·출력 2개가 두세 번 이어졌다는 것만으로 믹서나 세탁 흐름이라고 쓰지 않습니다.

**단일 기준 판정.** 거스름돈 판단은 추정이 여럿이고 서로 어긋날 수 있습니다. 한 기준만 맞는다고 거스름돈으로 판정하면 흐름 전체가 엉뚱한 쪽으로 이어집니다. 판단 근거를 단계마다 기록하고, 결론이 한 추정에만 기대면 그 사실을 보고서에 적습니다.

**상용 위험 점수.** 믹서 시험 거래에서 같은 입금 주소를 AMLBot 은 "blacklisted" 로, CrystalBlockchain 은 26% 로 평가했고, 다른 주소 하나는 73% 와 30% 로 달랐습니다[15]. CrystalBlockchain 은 점수의 근거 데이터와 방법을 자세히 밝히지 않습니다[15]. 점수를 옮길 때는 서비스 이름과 조회 날짜를 적고, 체인에서 확인한 흐름과 따로 씁니다.

**조회 결과가 빠질 수 있음.** 확장 공개 키 조회 도구와 제3자 탐색기는 계산하는 주소 범위와 서버 데이터에 따라 결과가 빠질 수 있습니다[12]. "이 지갑의 거래는 N건" 이라고 쓸 때는 어떤 경로·주소 형식·간격으로 계산했는지 함께 적습니다.

## 결과를 어떻게 해석하나

**증명하는 것.** 출력은 블록체인 전체에서 한 번만 입력으로 쓸 수 있어서[1], 어떤 입력이 한 출력을 가리키면 그 출력의 금액이 이 트랜잭션으로 넘어갔다는 연결은 하나로 정해집니다. 출력의 금액과 잠금 스크립트(곧 주소), 트랜잭션이 들어간 블록의 해시·높이·블록 시각도 체인에 그대로 있어[2][3], 누가 조회해도 같은 값이 나옵니다. 입력의 서명이 그 출력을 잠근 키로 만들어졌다는 것도 확인됩니다[1].

**증명하지 못하는 것.** 출력 가운데 어느 것이 거스름돈인지는 추정입니다. 그래서 3~5단계처럼 출력 번호로 곧바로 이어지는 연결은 사실이고, 8단계처럼 다음 출력을 고른 연결은 판단입니다. 서명이 확인되어도 키를 누가 가졌는지는 체인에 없고, 주소 주인의 신원은 거래소 기록 같은 체인 밖 자료로 확인합니다[16]. 믹서의 입금 주소와 출금 주소 사이에 최단 경로가 나와도, 믹서가 앞 거래에서 이미 이어진 주소를 다시 쓰면서 생긴 연결일 수 있습니다[15]. 믹서 추적 결과의 해석은 [믹서와 추적을 어렵게 하는 방법](../../01-foundations/ecosystem/mixers.md)에서 다룹니다.

**시각.** 흐름의 각 단계에 붙는 시각은 트랜잭션이 들어간 블록의 헤더 시각이고, Esplora `status.block_time` 은 확정 전에는 비어 있습니다[5]. 이 시각은 채굴자가 헤더 해싱을 시작했다고 적은 유닉스 시각(UTC 기준 초)이고[18], 사용자가 트랜잭션을 만들거나 보낸 시각이 아닙니다. 블록 시각은 앞 11개 블록 시각의 중앙값보다 크기만 하면 되므로[18] 바로 앞 블록보다 이를 수도 있어서, 단계의 순서는 블록 높이와 출력이 쓰인 관계로 정하고 시각은 참고로 씁니다. 블록 시각의 기준과 오차는 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에서, 기기 시각과 합치는 방법은 [암호화폐 타임라인](timeline.md)에서 다룹니다.

**보고서 문장.** "A 가 B 에게 보냈다" 가 아니라 체인에서 확인되는 만큼만 씁니다. 예: "이 기기의 지갑 앱 데이터에 TXID aa11…(만든 예시)이 있고, 이 트랜잭션의 0번 출력(5,000,000 사토시)을 TXID bb22…(만든 예시)의 0번 입력이 썼으며, bb22… 는 블록 800,100(해시 0000…c3d4, 만든 예시)에 들어 있다. bb22… 의 1번 출력을 거스름돈으로 본 근거는 입력과 주소 종류가 같다는 추정이다."

## 참고 문헌

1. Bitcoin Developer Guide, "Transactions". https://developer.bitcoin.org/devguide/transactions.html
2. Bitcoin Developer Guide, "Block Chain". https://developer.bitcoin.org/devguide/block_chain.html
3. Bitcoin Developer Reference, "Transactions". https://developer.bitcoin.org/reference/transactions.html
4. BIP-141, "Segregated Witness (Consensus layer)". https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki
5. Blockstream Esplora, "Esplora HTTP API" (`API.md`). https://github.com/Blockstream/esplora/blob/master/API.md
6. BIP-44, "Multi-Account Hierarchy for Deterministic Wallets". https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
7. Bitcoin Core, `doc/descriptors.md`. https://github.com/bitcoin/bitcoin/blob/master/doc/descriptors.md
8. Bitcoin Core RPC, "gettransaction". https://developer.bitcoin.org/reference/rpc/gettransaction.html
9. Bitcoin Core RPC, "getblock". https://developer.bitcoin.org/reference/rpc/getblock.html
10. BIP-125, "Opt-in Full Replace-by-Fee Signaling". https://github.com/bitcoin/bips/blob/master/bip-0125.mediawiki
11. Bitcoin Core, `doc/JSON-RPC-interface.md`. https://github.com/bitcoin/bitcoin/blob/master/doc/JSON-RPC-interface.md
12. Tyler Thomas, Tiffanie Edwards, Ibrahim Baggili, 「BlockQuery: Toward forensically sound cryptocurrency investigation」, Forensic Science International: Digital Investigation 40, 2022, doi:10.1016/j.fsidi.2022.301340
13. Jan Zavřel, Michal Koutenský, Daniel Dolejška, Vladimír Veselý, 「Tumbling down the stairs: Exploiting a tumbler's attempt to hide with ordinary-looking transactions using wallet fingerprinting」, Forensic Science International: Digital Investigation 52, 2025, doi:10.1016/j.fsidi.2025.301869
14. Yanan Gong, Kam Pui Chow, Siu Ming Yiu, Hing Fung Ting, 「Analyzing the peeling chain patterns on the Bitcoin blockchain」, Forensic Science International: Digital Investigation 46, 2023, doi:10.1016/j.fsidi.2023.301614
15. Pascal Tippe, Christoph Deckers, 「Unmixing the mix: Patterns and challenges in Bitcoin mixer investigations」, Forensic Science International: Digital Investigation 52, 2025, doi:10.1016/j.fsidi.2025.301876
16. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, 「Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications」, arXiv, 2022, doi:10.48550/arXiv.2205.14611
17. SWGDE, "Technical Notes on Cryptocurrency" (23-F-006-1.1), 2024-12-09. https://www.swgde.org/wp-content/uploads/2025/01/2024-12-09-Tech-Notes-on-Cryptocurrency-23-F-006-1.1.pdf
18. Bitcoin Developer Reference, "Block Chain". https://developer.bitcoin.org/reference/block_chain.html
19. Bitcoin Developer Glossary, "RPC Byte Order". https://developer.bitcoin.org/glossary.html
