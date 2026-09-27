---
title: "믹서와 추적을 어렵게 하는 방법"
parent: "기반 · 거래 환경"
nav_order: 110
---

# 믹서와 추적을 어렵게 하는 방법 (Mixers·Privacy Coins)

믹서는 여러 사람의 돈을 섞은 뒤 다른 코인으로 돌려주어, 블록체인에서 보낸 주소와 받은 주소를 잇기 어렵게 만드는 서비스입니다. 비트코인에는 운영자가 돈을 맡는 수탁형 믹서와 여러 사람이 한 트랜잭션을 함께 만드는 코인조인이 있고, 이더리움에는 Tornado Cash 같은 믹서 컨트랙트가 있으며, Monero 는 체인 자체가 보낸 사람·받는 사람·금액을 감춥니다. 이 페이지는 이 방법들이 블록체인과 기기에 무엇을 남기고, 그 흔적으로 무엇까지 증명할 수 있는지를 다룹니다.

## 이 구분을 쓰는 아티팩트

믹서를 거친 자금은 체인만 따라가서는 끊기는 지점이 생깁니다. 그 지점에서 무엇을 찾을지는 방법마다 다릅니다. 수탁형 믹서와 코인조인은 비트코인 트랜잭션의 모양과 주소 종류로 알아보고, Tornado Cash 는 컨트랙트의 이벤트 로그로 찾으며, Monero 는 체인에서 볼 수 있는 것이 거의 없어 기기의 지갑 파일과 메모리를 봐야 합니다.

| 방법 | 체인에 남는 것 | 체인 밖에서 찾을 것 | 함께 볼 페이지 |
|---|---|---|---|
| 수탁형 믹서 (비트코인) | 믹서 입금 주소로 보낸 트랜잭션, 필링 체인으로 지급한 트랜잭션 | 보증서, 거래소 계정 기록, 서버·결제 기록 | [비트코인의 UTXO](../blockchain/utxo.md), [비트코인 거래 따라가기](../../03-techniques/analysis/bitcoin-tracing.md) |
| 코인조인 (비트코인) | 입력·출력이 많고 같은 금액 출력이 여러 개인 트랜잭션 | 코인조인 지갑 앱의 기록 | [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md) |
| Tornado Cash (이더리움) | 입금 이벤트 `Deposit`, 출금 이벤트 `Withdrawal` | 브라우저 확장 지갑의 트랜잭션 기록 | [이더리움의 계정과 로그](../blockchain/ethereum-accounts.md), [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md) |
| Monero | 일회용 주소와 링 서명, 숨긴 금액 | 암호화된 지갑 파일, 실행 중인 지갑의 메모리 | [주소 형식](../wallets/address-formats.md), [지갑 파일과 암호화](../wallets/wallet-files.md) |

빼앗긴 자산이 믹서로 들어간 사건을 처음부터 따라가는 순서는 [빼앗긴 자산은 어디로 갔나](../../04-scenarios/asset-flow/stolen-funds.md)에 있습니다.

## 구조

### 수탁형 믹서와 비수탁형 믹서

수탁형 믹서(custodial mixer)는 중앙 서비스입니다. 사용자가 비트코인을 믹서 주소로 보내면 믹서가 잠시 맡아 다른 사람의 돈과 섞고, 같은 가치의 다른 비트코인을 사용자가 알려 준 주소로 보냅니다[1]. 사용자는 믹서를 믿고 돈을 맡겨야 하므로 믹서가 돈을 들고 사라질 위험이 있습니다[1][2]. 입금과 출금은 원인과 결과로 이어지지만, 요즘 믹서는 대개 받은 코인이 아닌 다른 코인으로 출금해 줍니다[2].

비수탁형 믹서(non-custodial mixer)는 사용자가 돈을 맡기지 않는 방식이고, 대표적인 예가 코인조인(CoinJoin)입니다. 여러 사용자가 입력과 출력을 한 트랜잭션에 합쳐서 어느 입력이 어느 출력으로 갔는지 알기 어렵게 합니다[1].

포럼에서 찾은 운영 중인 수탁형 믹서 20곳의 기능은 아래와 같습니다[1].

| 항목 | 믹서 수 (20곳 중) |
|---|---|
| 가입·신원 확인 요구 | 0 |
| 입력 주소 여러 개 허용 | 1 |
| 출력 주소 2개 이상 허용 | 17 |
| 출금 지연 선택 가능 (광고한 지연: 즉시~168시간) | 10 |
| 인터넷 도메인 운영 (그중 Cloudflare 사용 13곳) | 19 |
| Tor 온니언 서비스 운영 | 19 |
| 보증서(letter of guarantee) 발급 | 15 |

보증서는 믹서가 서명해 사용자에게 주는 문서이고, 믹서가 약속을 지키지 않으면 사용자가 이 문서를 공개할 수 있습니다[1]. Anonymixer 의 보증서에는 출금 주소와 주소마다 보낼 금액·지연 시간, 새로 만든 입금 주소 10개가 들어 있습니다[2]. 사용자의 기기나 메일에서 이 보증서가 나오면, 사용자가 믹서에 알려 준 출금 주소를 체인 밖 자료로 확인할 수 있습니다.

### 필링 체인으로 지급하는 믹서

필링 체인(peeling chain)은 한 주소에서 시작해 트랜잭션마다 조금씩 떼어 보내고 나머지를 다음 트랜잭션으로 넘기는 사슬이고, 트랜잭션 하나는 보통 입력 1개·출력 2개입니다[1]. 이 모양은 일반 사용자의 송금과 같아서 믹서 거래만 골라내기 어렵습니다[1]. 필링 체인의 구조와 전체 트랜잭션 가운데 입력 1개·출력 2개 트랜잭션의 비율은 [비트코인의 UTXO](../blockchain/utxo.md)에서 다룹니다. 필링 체인은 믹서뿐 아니라 거래소도 씁니다[3].

두 믹서에 약 0.004 BTC 와 0.00038 BTC 를 보내 시험한 연구에서는 두 믹서 모두 필링 체인으로 지급했고, 지급으로 이어지는 트랜잭션은 한 가지 주소 종류만 썼습니다[1]. 믹서 1은 `bc1q` 로 시작하는 주소, 믹서 2는 `3` 으로 시작하는 주소였습니다[1]. 지갑마다 쓰는 주소 종류가 다를 수 있으므로, 주소 종류가 끝까지 같은 필링 체인을 찾으면 후보를 줄일 수 있습니다[1]. 믹서 2가 지급에 쓴 주소들은 두 상용 분석 서비스 모두 HTX 거래소 소유로 표시했고, 믹서 운영자가 거래소 계정으로 지급했을 가능성이 있습니다[1].

### 코인조인 트랜잭션의 모양

트랜잭션 모양(transaction shape)은 `<입력 주소 수:출력 주소 수>` 로 적습니다[2]. 아래 표는 모양별로 흔한 해석입니다. 논문에서 few 는 5 이하, many 는 6 이상입니다[2].

| 모양 | 흔한 해석 |
|---|---|
| `<few:2>` | 단순 지급 (받는 사람 1, 거스름돈 1) |
| `<1:1>` | 자기 주소로 옮기기, 거스름돈 없는 지급 |
| `<many:1>` | 여러 주소의 돈을 한 주소로 모으기(consolidation) |
| `<1:many>` | 일괄 지급(batch spend) 또는 흩뿌리기(spread) |

코인조인 지갑은 구현마다 트랜잭션 모양이 다릅니다[2].

| 구현 | 특징 |
|---|---|
| JoinMarket | 참여자(maker) N명이면 같은 금액 출력이 N+1개, 거스름돈 출력은 필요한 만큼, 입력은 N개 이상. N 은 기본값으로 8~10 사이에서 무작위로 고름. `nVersion` 2, `nLockTime` 0. 정해진 액면 금액이 없음 |
| Wasabi | 정해진 액면 금액 목록을 씀. 기본 입력 수 21개보다 적으면 실행하지 않음. 2024년 4월 수사기관이 Samourai 서비스를 압수한 뒤 자체 코디네이터 운영을 멈췄고, 다른 코디네이터로는 계속 쓸 수 있음 |
| Samourai | 2024년 4월 25일 공동 창업자 체포, 웹사이트 압수, 믹싱 서비스(Whirlpool) 종료 |

### Tornado Cash 컨트랙트

Tornado Cash 는 이더리움에서 동작하는 믹서입니다[6]. 미국 재무부 해외자산통제실(OFAC)은 2022년 8월 8일 Tornado Cash 를 제재 대상에 올렸습니다[6]. Tornado Cash 는 2019년에 나온 뒤 70억 달러가 넘는 가상자산을 세탁하는 데 쓰였고, 그 안에는 Lazarus 그룹이 빼앗은 4억 5,500만 달러 이상이 들어 있습니다[6]. 2022년 6월 24일 Harmony Bridge 탈취 자금 9,600만 달러 이상과 2022년 8월 2일 Nomad 탈취 자금 최소 780만 달러도 Tornado Cash 로 세탁됐습니다[6]. 재무부는 2025년 3월 21일 제재를 해제했고, 이 결정은 Van Loon v. Department of the Treasury 소송에 낸 서면에 반영됐습니다[7].

컨트랙트 인스턴스마다 한 번에 넣는 금액(`denomination`)이 정해져 있고, 입금액은 이 금액과 같아야 합니다[5]. 입금과 출금은 아래 함수와 이벤트로 남습니다[5].

| 동작 | 함수 | 이벤트 | 이벤트에 남는 값 |
|---|---|---|---|
| 입금 | `deposit(bytes32 _commitment)` | `Deposit(bytes32 indexed commitment, uint32 leafIndex, uint256 timestamp)` | 커밋먼트(토픽), 트리 안 위치, 블록 시각 |
| 출금 | `withdraw(_proof, _root, _nullifierHash, _recipient, _relayer, _fee, _refund)` | `Withdrawal(address to, bytes32 nullifierHash, address indexed relayer, uint256 fee)` | 받는 주소, 널리파이어 해시, 릴레이어 주소(토픽), 수수료 |

커밋먼트(commitment)는 입금자만 아는 두 값, 널리파이어(nullifier)와 비밀값(secret)을 이어 붙여 해시한 값입니다[5]. 출금할 때는 이 두 값 대신 증명(`_proof`)과 널리파이어 해시를 내며, 컨트랙트는 증명을 검증한 뒤 같은 널리파이어 해시로 두 번 출금하지 못하게 막습니다[5]. 그래서 입금한 주소와 출금 받는 주소는 각각 체인에 보이지만, 둘을 잇는 값은 체인에 없습니다. 받는 주소(`_recipient`)는 함수 인자라서 출금 트랜잭션을 보낸 계정과 다를 수 있고, 릴레이어를 쓰면 릴레이어 주소와 수수료가 이벤트에 남습니다[5].

### Monero

Monero 는 체인에서 거래 당사자와 금액을 감추는 방법 세 가지를 씁니다.

- 스텔스 주소(stealth address): 보내는 쪽이 거래마다 받는 사람 대신 일회용 주소를 만들어서, 체인 위 주소를 받는 사람의 공개 주소와 이을 수 없습니다[9].
- 링 서명(ring signature): 블록체인에서 감마 분포로 고른 다른 출력들을 함께 넣어 서명해서, 그중 누가 실제로 서명했는지 알 수 없습니다[10].
- 링CT(RingCT): 금액을 감춥니다. 블록 1,220,516(2017년 1월)에 도입했고 2017년 9월부터 모든 트랜잭션에 필수입니다[11].

계정마다 spend 키와 view 키 두 쌍이 있습니다[12]. 개인 view 키를 받으면 그 주소로 들어온 거래는 모두 볼 수 있지만, 나간 거래는 2017년 6월 기준으로 믿을 만하게 볼 수 없어서 view 키로 본 잔액은 믿으면 안 됩니다[12][9].

Monero 주소는 공개 spend 키와 공개 view 키를 이어 붙이고 앞에 네트워크 바이트(Monero 는 18), 뒤에 전체를 Keccak-256 으로 해시한 값의 앞 4바이트를 검사합으로 붙여 Base58 로 바꾼 값입니다[8]. 원래 주소는 `4` 나 `8` 로 시작하는 95자이고, 64비트 결제 ID 를 넣은 통합 주소(integrated address)는 106자입니다[8].

Monero CLI·GUI 지갑 하나는 파일 두 개로 저장됩니다[13]. `지갑이름.keys` 는 키 파일이고 네 가지 키가 들어 있으며, 확장자 없는 `지갑이름` 은 캐시 파일이고 받은 금액·보낸 금액·수수료·거스름돈·확정된 블록 높이 같은 거래 기록이 들어 있습니다[13]. 두 파일 모두 사용자가 정한 암호로 암호화되어 있어 평문으로 보이지 않습니다[13]. 이 내용은 Windows 11 24H2 에서 Monero CLI·GUI 0.18.3.4 로 만든 지갑 기준입니다[13].

## 읽는 법

비트코인에서 믹서 거래를 찾을 때는 트랜잭션 하나가 아니라 흐름을 봅니다. 먼저 의심 주소에서 나간 트랜잭션의 모양을 보고, 같은 금액 출력이 여러 개이고 입력이 많으면 코인조인 후보로, 입력 1개·출력 2개가 주소 종류를 바꾸지 않고 이어지면 필링 체인 후보로 분류합니다. JoinMarket 은 같은 금액 출력 N+1개와 `nVersion` 2·`nLockTime` 0 조합을, Wasabi 는 액면 금액 목록과 21개 이상 입력을 기준으로 봅니다[2]. 트랜잭션 버전·시퀀스 번호·잠금 시각의 구조는 [비트코인의 UTXO](../blockchain/utxo.md)에서 다룹니다.

지갑 지문(wallet fingerprint)은 `nVersion`·`nSequence`·`nLockTime` 의 드문 조합, 서명의 low-R 여부, 입력·출력 순서 같은 특징을 묶어 특정 지갑 소프트웨어가 만든 트랜잭션을 추정하는 방법입니다[2]. 블록 799,000~800,008(약 1주) 범위에서 `nVersion` 2, 입력의 `nSequence` 가 잠금 없음, 트랜잭션의 `nLockTime` 에 값이 있는 조합은 49건(0.002260%)뿐이었습니다[2]. 이렇게 드문 조합을 한 믹서가 자주 쓰면 그 믹서의 트랜잭션 후보를 좁힐 수 있습니다[2].

Anonymixer 라는 수탁형 믹서를 2023년 3월 20회, 2024년 9월 2회 이용해 본 연구에서 확인된 동작은 아래와 같습니다[2].

- 출력 주소는 최대 20개까지 받고, 믹싱 세션은 GUID 로 구분하며 72시간 유지됩니다.
- 입금 주소 10개(P2WPKH 8개, P2SH 1개, P2PKH 1개)를 보여 주고, 입금된 코인은 18블록 동안 다른 고객 출금에 쓰지 않는다고 광고합니다.
- 입금 주소마다 입금은 1번, 그 주소에서 나가는 트랜잭션은 많아야 1번이었고, 둘 사이는 102~2,231블록(평균 795.26블록)이었습니다.
- 고객에게 출금을 보낸 믹서 쪽 주소는 트랜잭션이 딱 2건이었고, 그 주소에 돈이 들어온 때부터 고객에게 보낼 때까지 66~8,979블록(평균 1,718블록)이 걸렸습니다.

이더리움에서는 Tornado Cash 컨트랙트 주소를 대상으로 `eth_getLogs` 로 로그를 받아 `Deposit`·`Withdrawal` 이벤트를 찾습니다. 로그의 첫 토픽은 이벤트 서명의 Keccak-256 해시이고, `indexed` 로 선언한 인자는 그 뒤 토픽으로, 나머지 인자는 `data` 로 들어갑니다[18]. 그래서 `Deposit` 은 커밋먼트가 토픽에, `Withdrawal` 은 릴레이어 주소가 토픽에 있고 받는 주소는 `data` 에 있습니다[5]. 입금 트랜잭션의 `from` 이 돈을 넣은 계정이고, 출금 이벤트의 `to` 가 돈을 받은 주소입니다. 이벤트 로그와 토픽의 구조는 [이더리움의 계정과 로그](../blockchain/ethereum-accounts.md)에서 다룹니다.

Monero 는 체인에서 볼 수 있는 것이 거의 없으므로 기기에서 시작합니다. 디스크에서 확장자가 `.keys` 인 파일과 이름이 같고 확장자가 없는 파일이 짝을 이루면 Monero CLI·GUI 지갑 후보입니다[13]. 주소 문자열은 95자·106자 길이와 시작 글자로 찾습니다[8]. 지갑 파일 일반과 암호화 방식은 [지갑 파일과 암호화](../wallets/wallet-files.md), 메모리 수집은 [Windows 메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/)에서 다룹니다.

## 포렌식에서 중요한 점

### 증명하는 것과 증명하지 못하는 것

믹서 입금 트랜잭션이 체인에 있으면 그 주소가 믹서에 돈을 넣었다는 것까지, 출금 트랜잭션이 있으면 그 주소가 믹서에서 돈을 받았다는 것까지 증명됩니다[5][1]. Tornado Cash 는 이벤트가 컨트랙트에서 나오므로 입금·출금 사실 자체는 분명합니다[5].

입금과 출금이 같은 사람의 것이라는 점은 체인만으로 증명하지 못합니다. 믹서 1은 입력 주소와 출력 주소 사이에 경로가 없었고, 두 달 뒤에도 입력 주소에 돈이 그대로 있었습니다[1]. 믹서 2는 믹싱 기간 안에는 직접 이어지지 않았지만, 최단 경로를 계산하면 연결이 나왔는데, 믹서가 예전 거래로 이미 이어진 주소를 다시 써서 생긴 경로입니다[1]. 그래서 이 경로는 입금한 사람과 출금 받은 사람이 같다는 근거가 되지 않습니다.

금액과 시간으로 연결하는 분석은 후보를 줄일 뿐입니다. 믹서 1에 넣은 금액에서 수수료를 뺀 금액으로 24시간 안의 트랜잭션을 찾으면 2건이 나왔고 그중 1건이 실제 지급이었지만, 수수료 범위를 넓히면 4,453건, 0부터 기대 금액까지로 넓히면 461,140건이 나왔습니다[1]. 출력 주소를 두 개로 받은 믹서 2는 같은 방법으로 1,422건과 391,998건이었고, 두 출력을 합한 금액과 같은 트랜잭션은 없었습니다[1]. 지갑 지문이 맞는 트랜잭션도 확률로만 그 믹서의 것이고, 일치한다고 믹서 소유가 확정되지 않습니다[2].

믹서를 썼다는 사실이 곧 불법 자금이라는 뜻도 아닙니다. 믹서는 개인과 기업의 정당한 프라이버시 목적으로도 쓰입니다[1].

미국에서 믹서 운영자를 특정한 사건 3건(ChipMixer, Helix, Bitcoin Fog)은 모두 시험 거래가 직접 운영자 특정으로 이어지지 않았고, 블록체인 밖 정보로 특정했습니다[1]. ChipMixer 는 Tor 온니언 서비스 서버의 IP 주소를 찾아서, Bitcoin Fog 는 호스팅 비용을 낸 비트코인을 따라가서 운영자를 찾았습니다[1]. ChipMixer 는 0.001 BTC 에 2의 거듭제곱을 곱한 0.001~4.096 BTC 짜리 "칩" 주소를 미리 채워 두는 방식이었습니다[1].

Monero 는 체인에서 보낸 사람·받는 사람·금액을 볼 수 없으므로, 기기의 지갑 파일이나 실행 중인 지갑의 메모리 같은 체인 밖 자료가 있어야 거래와 사람을 이을 수 있습니다[13][10][11]. 암호를 몰라도 지갑 파일 두 개가 기기에 있다는 것은 확인되고, 캐시 파일에는 입출금 기록이 들어 있으므로 복호하면 거래 내역을 볼 수 있습니다[13].

### 시각

Tornado Cash `Deposit` 이벤트의 `timestamp` 는 컨트랙트가 기록한 `block.timestamp`, 곧 입금 트랜잭션이 들어간 블록의 시각입니다[5]. `Withdrawal` 이벤트에는 시각 필드가 없어 로그가 들어간 블록의 시각을 씁니다. 블록 시각의 기준과 오차는 [블록 시각과 확정](../blockchain/block-time.md)에서 다룹니다.

수탁형 믹서 20곳이 광고한 출금 지연은 즉시~168시간이었지만[1], 실제 간격은 광고와 다를 수 있어 입금과 출금 트랜잭션의 블록 높이 차이로 확인합니다. Anonymixer 는 입금이 한 번 확인되면 출금 트랜잭션을 보내기 시작하지만, 입금 주소에 들어온 돈은 102~2,231블록 뒤에 그 주소에서 나갔습니다[2]. 그래서 입금 주소에서 돈이 나간 시각을 고객이 출금을 받은 시각으로 쓰지 않습니다.

Monero 캐시 파일의 입출금 기록에 있는 `m_timestamp` 는 기기 시각이 아니라 블록이 만들어진 시각입니다[13]. 복원한 지갑의 캐시 파일에는 복원할 때 지정한 블록 높이 이후의 거래만 들어 있어서, 그 전 거래가 없다고 거래가 없었던 것은 아닙니다[13].

### 주소 묶기

여러 입력을 한 소유자로 보는 공통 입력 규칙(common-input-ownership)은 코인조인이 깨뜨리려고 만든 것입니다[1][4]. BlockSci 는 다중 입력 규칙으로 묶을 때 코인조인 트랜잭션을 건너뛰려 하고, 묶음이 한데 뭉치는(cluster collapse) 위험 때문에 거스름돈 주소는 기본으로 묶지 않습니다[16]. GraphSense 는 한 트랜잭션의 입력을 공유한 주소를 합칩니다[17]. 코인조인으로 판정된 트랜잭션을 뺀 변형 규칙은 원래 규칙과 묶음 효과가 거의 같습니다[4]. 묶기의 방법과 한계는 [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md)에서 다룹니다.

## 함정

- **필링 체인과 입력 1개·출력 2개 모양은 믹서만 만드는 것이 아닙니다.** 일반 사용자와 거래소도 같은 모양을 만듭니다[3][1]. 이 모양만으로 믹서 거래라고 쓰지 않습니다.
- **입력 1개·출력 2개 비율은 기준에 따라 숫자가 다릅니다.** 30일 이동평균으로 약 75%라는 수치[2]와, 블록 772,162까지 누적해 56.33%라는 수치[3]는 기간과 정의가 다릅니다. 인용할 때 기준을 함께 적습니다.
- **위험 점수는 서비스마다 다릅니다.** 같은 믹서 입금 주소를 AMLBot 은 "blacklisted" 로, CrystalBlockchain 은 26%로 평가했고, 다른 주소 하나는 73%와 30%로 달랐습니다[1]. 점수를 옮길 때는 서비스 이름과 조회 날짜를 적습니다.
- **Tornado Cash 의 제재 상태는 시점마다 다릅니다.** 2022년 8월 8일 지정[6], 2025년 3월 21일 해제[7]입니다. 보고서에는 거래 시점의 상태를 적습니다.
- **Monero 주소 정규식이 `8` 로 시작하는 주소를 놓칩니다.** bstrings 의 `monero` 정규식은 `4[0-9AB][0-9a-zA-Z]{93}|4[0-9AB][0-9a-zA-Z]{104}` 라서 `4` 로 시작하는 95자·106자만 잡습니다[14]. 원래 주소는 `8` 로도 시작합니다[8].
- **Monero 지갑의 키는 프로그램이 끝나면 메모리에서 지워집니다.** Monero CLI 는 종료할 때 키가 든 객체를 0으로 덮어서, 종료 뒤에는 메모리에서 찾을 수 없습니다[13]. 실행 중인 기기라면 메모리를 먼저 수집합니다.
- **Feather 지갑의 시각 필드를 지갑 생성 시각으로 쓰면 안 됩니다.** 새로 만든 Feather 지갑을 실행한 메모리에서 찾은 계정 구조(`account_base`)의 시각 필드는 늘 `2014-06-07 15:00:00` 고정값입니다[13].
- **view 키로 본 Monero 잔액은 실제 잔액이 아닐 수 있습니다.** 나간 거래를 믿을 만하게 볼 수 없기 때문입니다[12].

## 도구

- **BlockSci:** 다중 입력 규칙으로 주소를 묶고 코인조인 트랜잭션을 건너뛸 수 있습니다[16].
- **GraphSense:** 다중 입력 규칙으로 주소를 묶습니다[17].
- **그래프 데이터베이스:** 비트코인 블록체인을 btc-csv 로 CSV 로 뽑아 Neo4j 에 넣고 Cypher 로 최단 경로와 금액 범위를 조회하는 방법이 연구에 쓰였고, 금액 범위 조회문 예시가 논문 부록에 있습니다[1]. btc-csv 는 2020년 이후 갱신되지 않은 주소 해석 라이브러리를 써서 탭루트 트랜잭션을 처리하지 못하므로 고쳐서 써야 합니다[1].
- **이더리움 JSON-RPC `eth_getLogs`:** 컨트랙트 주소와 토픽으로 Tornado Cash 이벤트를 찾습니다[18].
- **bstrings·KAPE:** KAPE 모듈 `bstrings_MoneroWallet` 은 bstrings 를 `--lr monero` 로 실행해 Monero 주소 문자열을 찾습니다[15]. `8` 로 시작하는 주소는 정규식을 따로 추가해 찾습니다.

## 참고 문헌

1. Pascal Tippe, Christoph Deckers, 「Unmixing the mix: Patterns and challenges in Bitcoin mixer investigations」, Forensic Science International: Digital Investigation 52, 2025, doi:10.1016/j.fsidi.2025.301876
2. Jan Zavřel, Michal Koutenský, Daniel Dolejška, Vladimír Veselý, 「Tumbling down the stairs: Exploiting a tumbler's attempt to hide with ordinary-looking transactions using wallet fingerprinting」, Forensic Science International: Digital Investigation 52, 2025, doi:10.1016/j.fsidi.2025.301869
3. Yanan Gong, Kam Pui Chow, Siu Ming Yiu, Hing Fung Ting, 「Analyzing the peeling chain patterns on the Bitcoin blockchain」, Forensic Science International: Digital Investigation 46, 2023, doi:10.1016/j.fsidi.2023.301614
4. Hugo Schnoering, Pierre Porthaux, Michalis Vazirgiannis, 「Assessing the Efficacy of Heuristic-Based Address Clustering for Bitcoin」, arXiv, 2024, doi:10.48550/arXiv.2403.00523
5. tornado-core, `contracts/Tornado.sol`. https://github.com/tornadocash/tornado-core/blob/master/contracts/Tornado.sol
6. U.S. Department of the Treasury, "U.S. Treasury Sanctions Notorious Virtual Currency Mixer Tornado Cash", 2022-08-08. https://home.treasury.gov/news/press-releases/jy0916
7. U.S. Department of the Treasury, "Tornado Cash Delisting", 2025-03-21. https://home.treasury.gov/news/press-releases/sb0057
8. Moneropedia, "Address". https://www.getmonero.org/resources/moneropedia/address.html
9. Moneropedia, "Stealth Address". https://www.getmonero.org/resources/moneropedia/stealthaddress.html
10. Moneropedia, "Ring Signature". https://www.getmonero.org/resources/moneropedia/ringsignatures.html
11. Moneropedia, "Ring CT". https://www.getmonero.org/resources/moneropedia/ringCT.html
12. Moneropedia, "View Key". https://www.getmonero.org/resources/moneropedia/viewkey.html
13. Jeongin Lee, Geunyeong Choi, Jihyo Han, Jungheum Park, 「Advanced Monero wallet forensics: Demystifying off-chain artifacts to trace privacy-preserving cryptocurrency transactions」, Forensic Science International: Digital Investigation 54, 2025, doi:10.1016/j.fsidi.2025.301988
14. bstrings, `bstrings/Program.cs`. https://github.com/EricZimmerman/bstrings/blob/master/bstrings/Program.cs
15. KapeFiles, `Modules/EZTools/bstrings/bstrings_MoneroWallet.mkape`. https://github.com/EricZimmerman/KapeFiles/blob/master/Modules/EZTools/bstrings/bstrings_MoneroWallet.mkape
16. BlockSci, `docs/reference/clustering/cluster_manager.rst`. https://github.com/citp/BlockSci/blob/master/docs/reference/clustering/cluster_manager.rst
17. graphsense-lib, `rust/gs_clustering/src/clustering.rs`. https://github.com/graphsense/graphsense-lib/blob/master/rust/gs_clustering/src/clustering.rs
18. ethereum.org, "JSON-RPC API". https://ethereum.org/en/developers/docs/apis/json-rpc/
