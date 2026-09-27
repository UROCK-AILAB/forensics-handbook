---
title: "암호화폐 포렌식 보고서"
parent: "기법 · 보고"
nav_order: 340
---

# 암호화폐 포렌식 보고서 (Forensic Report)

암호화폐 사건 보고서는 기기에서 찾은 흔적, 블록체인 원장, 거래소가 낸 자료를 출처별로 따로 적고, 기록으로 확인한 것과 추정한 것을 나눠 씁니다. 원장을 어떤 수단으로 언제 어느 블록 기준으로 조회했는지, 금액 단위와 시각을 어떻게 바꿨는지까지 적어야 다른 분석가가 같은 결과를 다시 얻을 수 있습니다. 보고서의 일반 구성은 [Windows 핸드북의 보고서 페이지](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/reporting/forensic-report.html)와 같고, 이 페이지는 암호화폐 증거에서 더 적어야 할 것을 다룹니다.

## 언제 쓰나

- 감정 결과를 수사기관·법원·의뢰인에게 낼 때 씁니다. 증거와 도구, 기법은 법정에서 다툼 대상이 될 수 있어서 다른 사람이 과정과 결과를 재현할 수 있을 만큼 기록을 남겨야 합니다[1].
- 거래소에 자료를 요청하는 문서를 쓸 때도 같은 표를 씁니다. Binance.US 에 TXID 기준으로 요청할 때는 금액·입력 주소·출력 주소·UTC 시각을, 주소 기준으로 요청할 때는 TXID·UTC 시각·금액을 함께 적고, 옮겨 적다 틀리는 일을 줄이려고 편집할 수 있는 파일 형식으로 보냅니다[24].
- 이미 낸 보고서를 고칠 때는 새 보고서를 내고, 고친 곳과 이유를 밝히고, 원래 보고서를 참조합니다[1].

## 절차

1. **일반 정보와 의뢰를 적습니다.** 보고서 머리와 의뢰 부분에 넣을 항목은 SWGDE 보고서 요건[1]을 따르고, 항목 목록은 [macOS 포렌식 보고서](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/reporting/forensic-report.html)에 정리돼 있습니다. 약어는 처음 나올 때 풀어 쓰는데[1], 암호화폐 보고서에는 TXID·xpub·UTXO 처럼 일반인이 모르는 약어가 많아서 이 규칙을 지킬 곳이 많습니다.

2. **제출·수집한 물품을 하나씩 식별합니다.** 받거나 수집한 날짜, 전달·수집 방법, 제출자를 적고, 물품마다 제조사·모델·일련번호·표시·해시 값처럼 하나로 특정할 수 있는 정보를 목록으로 적습니다[1]. 감정하지 않은 물품도 목록에 넣습니다[1]. 하드웨어 지갑은 어떻게 다뤘는지 따로 적습니다. 일부 하드웨어 지갑은 쓰기 방지 장치 같은 읽기 전용 장치에 연결하면 초기화되고, USB 저장 매체처럼 이미징하면 이런 기능이 작동할 수 있습니다[2]. 그래서 연결했는지, 무엇에 연결했는지, 연결 전후 화면이 어땠는지를 남겨야 초기화 여부를 나중에 따질 수 있습니다. 켜진 채 발견한 기기는 켠 채로 잠기지 않게 두고, 수집하면서 한 조치는 모두 기록합니다[2]. 그래서 보고서에도 조치마다 시각과 순서를 적습니다. 현장 수집 순서는 [조사 절차](../acquisition/investigation-process.md), 하드웨어 지갑의 흔적은 [하드웨어 지갑과 연결 흔적](../../02-artifacts/hardware/hardware-wallets.md)에 있습니다.

3. **기기 흔적을 적습니다.** 어느 앱의 어느 파일(전체 경로와 해시)에서 어떤 주소·xpub·TXID 가 나왔는지를 적습니다. 현장에서는 암호화폐·암호화 관련 앱이 있는지, 눈에 띈 지갑 주소와 암호, 암호화 키, 지갑 설정·데이터 파일을 기록합니다[2]. 복구 문구와 개인 키는 자금을 옮기는 데 쓸 수 있어서 권한 없는 사람이 볼 수 없게 기록·보관해야 합니다[2]. 보고서는 여러 사람에게 전달되므로 본문에는 "복구 문구가 적힌 종이를 발견해 봉인 보관함" 처럼 존재와 보관 위치만 적고 값은 싣지 않습니다. 흔적 찾는 법은 [기기에서 지갑 흔적 찾기](../acquisition/artifact-search.md)에 있습니다.

4. **온체인 조회 방법을 적습니다.** 암호화폐 거래 조사 결과를 증거로 믿으려면 세 가지를 갖춰야 합니다[3]. 완전성은 공개 키나 주소 하나로 그 키·주소가 쓴 거래를 모두 찾는 것이고, 무결성은 조회한 원장이 네트워크가 지금 인정하는 원장과 같은 것이며, 기밀성은 어떤 거래를 조사하는지 의도치 않게 드러내지 않는 것입니다[3]. 제3자가 운영하는 블록 탐색기를 쓰면 조사 대상 계정이 운영자에게 드러나고, 믿을 수 없거나 침해된 조회 서비스는 수사기관 IP 와 조회한 지갑을 쉽게 연결할 수 있습니다[3]. 탐색기 응답은 틀리거나 빠지거나 오래됐을 수 있고, 이는 로컬 원장 사본으로만 확인할 수 있습니다[3]. 그래서 보고서에는 조회 수단(자체 노드와 색인기의 이름·버전, 또는 탐색기 이름과 주소), 조회 일시(UTC), 기준 블록(높이와 해시, 이더리움은 블록 번호나 `latest`·`safe`·`finalized` 같은 태그[10])를 적습니다. 자체 노드도 그 컴퓨터를 만질 수 있는 사람은 설정을 바꿔 최선 체인에 없는 트랜잭션이 여러 번 확인된 것처럼 보이게 할 수 있어서[8], 노드를 누가 관리했는지도 적습니다. 탐색기 화면을 읽는 법은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)에 있습니다.

5. **xpub 로 조회했다면 파생 범위를 적습니다.** 외부 체인은 받는 주소, 내부 체인은 잔돈 주소에 쓰여서 지갑의 입출금을 다 보려면 두 체인을 모두 파생해야 합니다[3]. BIP44 의 주소 간격 한도(gap limit)는 20 이고, 이 값을 가정하는 도구는 간격을 크게 벌려 만든 주소를 찾지 못합니다[3]. 경로 하나에서 나올 수 있는 자식 주소는 2^31 개라, 모든 주소를 찾았다고 확신하려면 전부 나열해야 합니다[3]. Ledger Nano X 와 Ledger Live 로 만든 거래, 그리고 주소 간격을 100 으로 둔 지갑으로 공개 조회 도구 7개를 시험했을 때 LedgerHQ/xpub-scan 만 모든 거래를 찾았고, 나머지는 Ledger Live 거래와 간격이 큰 주소를 하나도 찾지 못했습니다[3]. 7개 중 6개는 xpub 에서 SegWit 주소를 자동으로 파생하지 않았습니다[3]. 따라서 보고서에는 파생한 주소 형식(Legacy·Nested SegWit·Native SegWit), 조회한 체인(외부·내부), 몇 번째 주소까지 조회했는지를 적습니다. 파생 경로는 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md), 주소 형식은 [주소 형식](../../01-foundations/wallets/address-formats.md)에 있습니다.

6. **트랜잭션을 표로 정리합니다.** 아래 열을 두면 재현과 거래소 요청에 그대로 쓸 수 있습니다.

   | 열 | 적는 것 | 이유 |
   |---|---|---|
   | TXID | 전체 64자 | TXID 는 원시 트랜잭션을 SHA256(SHA256()) 한 값이고, 트랜잭션 안의 outpoint 에는 내부 바이트 순서로 들어가서[7] 헥스에서 찾은 값과 탐색기 표시 값의 순서가 다를 수 있습니다 |
   | 블록 높이·블록 해시 | 둘 다 | 포크가 생기면 같은 높이에 블록이 여럿일 수 있어 높이만으로는 블록을 특정하지 못합니다[5] |
   | 블록 시각 | UTC, 원래 Unix 값도 함께 | 아래 "시각 해석" 참고 |
   | 보낸 주소·받은 주소 | 원래 대소문자 그대로 | 아래 "주소를 옮겨 적을 때" 참고 |
   | 금액 | 원래 단위 값과 바꾼 값 | 비트코인 출력 값은 사토시 정수이고[7], 이더리움 `value` 는 wei 단위라 1 ETH = 10^18 wei 입니다[9]. 토큰은 `tokenDecimal` 만큼 10의 거듭제곱으로 나눕니다[12] |
   | 성공 여부 | 이더리움만 | 실패한 트랜잭션도 블록에 들어가 목록에 나옵니다. Etherscan 의 `isError` 는 0 이 성공, 1 이 실패이고, `txreceipt_status` 는 1 이 성공, 0 이 실패이며 Byzantium 이전 블록은 빈 값입니다[11] |
   | 확인 수와 조회 일시 | 함께 | `confirmations` 는 그 블록 뒤에 채굴된 블록 수라서[11] 조회할 때마다 늘어납니다 |
   | 출처 | 자체 노드·탐색기·거래소 자료 | 같은 트랜잭션이라도 출처마다 무결성 수준이 다릅니다[3] |

7. **거래소 자료는 원래 값과 변환 규칙을 함께 적습니다.** 거래소가 낸 시각에는 시간대가 빠져 있을 수 있고, 도구마다 이를 다르게 처리합니다. RLEAPP 의 Coinbase Compliance Report 분석기는 값에 오프셋(-0800, Z)이나 시간대 약어가 있을 때만 UTC 로 바꾸고, 약어는 북미 고정 오프셋(PST = UTC-8)으로 읽으며, 시간대가 없는 값은 바꾸지 않고 Time Basis 열에 그렇다고 남깁니다[13]. 같은 프로젝트의 Coinbase 아카이브 분석기는 시간대가 없는 ISO 시각을 UTC 로 간주합니다[14]. 이처럼 도구마다 결과가 다르므로 보고서에는 거래소가 낸 원래 시각, 바꾼 UTC 시각, 바꾼 규칙을 나란히 적습니다. Coinbase 자료에는 거래소 내부 ID(TRANSACTION ID)와 온체인 해시(TRANSACTION HASH)가 따로 있어서[13] 둘을 섞지 않습니다. 한 제출 자료에 같은 보고서가 여러 번 들어 있을 수 있어서, 행을 셀 때는 어느 파일에서 나온 행인지 비교합니다[13]. Binance.US 는 회신 자료의 정확성과 완전성을 보증하지 않고, 나중에 새 정보가 생겨도 회신을 고칠 의무가 없습니다[24]. 국내 가상자산사업자는 특정금융정보법상 의무이행 자료를 금융거래 관계가 끝난 때부터 5년간 보존하고[25], 2022년 3월 25일부터 사업자 사이에 100만원 상당 이상을 옮기면 송·수신인 정보를 주고받아 거래관계가 끝난 때부터 5년간 보존합니다[26]. 자료의 열과 읽는 법은 [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md)와 [거래소 자료 분석](../analysis/exchange-analysis.md)에 있습니다.

8. **추정 결과는 방법과 함께 따로 적습니다.** 주소 묶기, 잔돈 추정, 믹서 지문 같은 결과는 사용한 휴리스틱 이름, 도구와 버전, 분석 기준 블록 높이를 적고 "같은 주체로 추정" 처럼 추정이라고 씁니다. 근거와 한계는 아래 "결과를 어떻게 해석하나" 에 모았습니다.

9. **결론, 증거물 처리, 승인을 적습니다.** 과정·결과·의견·처분·승인에 넣을 항목도 SWGDE 보고서 요건[1]을 따르며, [macOS 포렌식 보고서](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/reporting/forensic-report.html)에 정리돼 있습니다. 도구가 자동으로 만든 보고서는 감정 전체 범위를 담지 않으므로 뒷받침 자료나 부록으로 붙입니다[1].

## 도구

- **Bitcoin Core 와 electrs:** 자체 풀 노드와 오픈소스 색인기를 묶으면 제3자 서버에 조회 내용을 보내지 않고 주소 기록을 찾을 수 있습니다. BlockQuery 가 이 조합으로 만들어졌습니다[3].
- **LedgerHQ/xpub-scan:** 오픈소스이고 xpub 하나로 세 주소 형식을 모두 파생하며 색인 범위를 조정할 수 있습니다. 다만 Ledger 서버로 조회해서 조회 내용이 밖으로 나갑니다[3].
- **BlockSci:** 잔돈 휴리스틱과 주소 묶기를 제공합니다[15][16]. 2020년 이후 갱신되지 않아 최근 트랜잭션 유형을 처리하는 데 한계가 있을 수 있습니다[21].
- **RLEAPP:** Coinbase 가 낸 자료를 표로 바꾸면서 원래 시각과 UTC 변환 근거를 나란히 남깁니다[13][14].
- **Esplora API:** `GET /tx/:txid/status` 가 `confirmed`·`block_height`·`block_hash` 를 돌려주고, 주소 기록은 확인된 것과 미확인(mempool) 것을 따로 조회합니다[27]. 자체 서버로 운영하지 않으면 4단계의 기밀성·무결성 문제가 그대로 남습니다.

## 함정과 한계

- **탐색기 결과를 원장 자체로 적는 것:** 탐색기 응답은 틀리거나 빠지거나 오래됐을 수 있습니다[3]. 출처 열에 탐색기라고 적고, 중요한 트랜잭션은 자체 노드로 다시 확인합니다.
- **xpub 조회 범위가 좁은 것:** 주소 형식 하나만 파생하거나, 간격 한도 20 까지만 보거나, 내부 체인을 빼면 거래가 빠집니다[3]. 조회 범위를 적지 않으면 "거래가 없다" 는 결론을 검증할 수 없습니다.
- **블록 높이만 적는 것:** 포크가 생기면 같은 높이에 블록이 여럿일 수 있습니다[5].
- **확인 수와 잔액을 시점 없이 적는 것:** 둘 다 조회할 때마다 바뀝니다[10][11].
- **실패한 이더리움 트랜잭션을 전송으로 적는 것:** 목록에 나와도 `isError` 가 1 이면 실행에 실패한 것입니다[11].
- **단위를 섞는 것:** 사토시와 BTC, wei·gwei·ETH(1 gwei = 10^-9 ETH[28]), 토큰 소수 자릿수를 섞으면 금액의 자릿수가 틀어집니다. 표에 원래 단위 값을 함께 적어 두면 읽는 사람이 다시 계산할 수 있습니다.
- **시간대 없는 거래소 시각을 도구 기본값대로 바꾸는 것:** 같은 자료라도 도구에 따라 그대로 두거나 UTC 로 간주합니다[13][14].
- **주소 대소문자를 바꾸는 것:** Bech32 주소는 인코더가 항상 소문자로 출력하고 디코더는 대소문자가 섞인 문자열을 받지 않습니다. QR 코드 안에서는 대문자를 쓰도록 권하므로[17] 대문자로 읽힌 값은 전부 소문자로 바꿔 적으면 같은 주소입니다. EIP-55 이더리움 주소는 대소문자에 체크섬이 들어 있어서, 잘못 옮긴 주소가 체크섬을 우연히 통과할 확률은 0.0247% 입니다[18]. 소문자로만 적으면 이 확인을 할 수 없습니다.
- **공개용 사본과 정식 보고서를 섞는 것:** 공개 문서에서는 주소·해시의 가운데 글자를 `*` 로 바꿔 적기도 합니다[23]. 정식 보고서에는 전체 값을 적어야 재현할 수 있습니다.
- **도구 자동 보고서로 감정 보고서를 대신하는 것:** 도구 보고서는 감정 전체 범위를 담지 않습니다[1].

## 결과를 어떻게 해석하나

### 증명하는 것 / 증명하지 못하는 것

기록으로 확인되는 것은 출처별로 셋입니다. 기기의 지갑 앱 데이터에 특정 주소·xpub·TXID 가 있다는 것, 그 TXID 의 트랜잭션이 특정 블록(높이와 해시)에 들어 있고 입출력 주소와 금액이 이렇다는 것, 거래소 자료에 이 계정과 입출금 기록이 있다는 것입니다. 세 가지는 따로 적고, 서로 이어지는 부분은 "이 기기의 지갑 앱 데이터에 이 주소가 있고, 이 주소에서 이 시각에 이 금액을 보낸 트랜잭션이 블록체인에 있다" 처럼 기록이 닿는 만큼만 잇습니다.

기록만으로 증명하지 못하는 것도 분명히 적습니다. 누가 서명했는지는 원장에 나오지 않습니다. 주소 묶기와 잔돈 추정은 확률적 추정입니다. BlockSci 의 잔돈 휴리스틱은 서로 모순될 때가 있어서 다듬지 않은 휴리스틱 하나만으로 주소를 묶으면 안 되고, 출력이 나중에 쓰이면 결과가 바뀌는 휴리스틱도 있습니다[15]. BlockSci 의 묶기 결과는 실제로 맞다고 가정하지 말아야 합니다[16]. 공통 입력 휴리스틱은 주소 수를 절반으로 줄이고 네 휴리스틱을 조합하면 블록 700,000 기준 주소 8억 7,400만 개가 약 2억 5,000만 묶음으로 70% 줄지만[19], 이 비율은 얼마나 묶였는지일 뿐 정확도가 아닙니다. 지갑 지문이 맞는 트랜잭션도 확률적으로만 그 서비스의 것이고, 확률을 보정하지 않으면 오탐이 많을 수 있습니다[20]. 미국 믹서 사건 3건(ChipMixer, Helix, Bitcoin Fog)에서도 운영자 식별은 주로 서버 IP, 호스팅 비용 결제 같은 블록체인 밖 정보로 했습니다[21]. 상용 분석 도구의 주체 라벨도 같은 문제를 안고 있습니다. 널리 쓰는 Elliptic 비트코인 데이터셋은 라벨과 실제 주체를 잇는 대응표를 공개하지 않아 라벨을 독립적으로 검증할 수 없습니다[22]. 그래서 도구의 라벨이나 위험 점수를 옮길 때는 도구 이름, 조회 일시, 라벨이라는 점을 함께 적습니다. 거래소·서비스 주소는 여러 사람이 함께 쓰므로 "이 주소 = 피의자" 로 적지 않습니다. 시험 거래에 쓰인 출력 주소 하나가 2021년 7월 기준 1,361번 거래하고 1억 달러 넘게 주고받은 주소였던 예가 있습니다[23]. 흐름을 따라가는 방법은 [비트코인 거래 따라가기](../analysis/bitcoin-tracing.md), [이더리움 거래 따라가기](../analysis/ethereum-tracing.md), 묶기의 한계는 [주소 묶기와 그 한계](../analysis/clustering.md), 믹서는 [믹서와 추적을 어렵게 하는 방법](../../01-foundations/ecosystem/mixers.md)에 있습니다.

### 시각 해석

보고서의 시각은 기준이 넷이라 열을 나눠 적습니다.

| 시각 | 무엇이 기록하나 | 해석할 때 |
|---|---|---|
| 블록 시각 | 비트코인 헤더 `time` 은 채굴자가 헤더 해싱을 시작한 시각을 채굴자 기준으로 적은 Unix epoch 값입니다[4]. Etherscan `timeStamp` 는 블록이 채굴된 시각을 초 단위 Unix 값으로 줍니다[11] | Unix 값이라 UTC 로 바꿔 적습니다. 비트코인 블록 시각은 앞선 11개 블록 시각의 중앙값보다 크기만 하면 되고, 실제 시각보다 최대 2시간 앞설 수 있습니다[4][6]. "블록 N 의 헤더 시각" 으로 적고 실제 전송 시각이라고 쓰지 않습니다 |
| 조회 시각 | 분석가 | 확인 수, 잔액, `latest` 기준 값은 조회할 때마다 바뀝니다[10][11]. 조회 일시를 UTC 로 적습니다 |
| 거래소 기록 시각 | 거래소 | 자료마다 형식이 다르고 시간대가 빠질 수 있습니다. 원래 값과 변환 규칙을 함께 적습니다[13][14] |
| 기기 시각 | 지갑 앱과 OS | 앱마다 저장 형식과 기준이 다릅니다. 각 지갑 페이지를 봅니다 |

미확인 트랜잭션은 아직 블록에 없어서 블록 시각이 없습니다[27]. 이더리움은 블록이 "justified" 를 거쳐 "finalized" 가 되면 막대한 비용이 드는 네트워크 수준 공격이 아니면 바뀌지 않으므로[9], 결론에 쓰는 트랜잭션은 finalized 블록에 있는지 확인해 적습니다. 블록 시각과 확정의 원리는 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md), 여러 출처 시각을 한 줄로 합치는 방법은 [암호화폐 타임라인](../analysis/timeline.md)에 있습니다.

### 보고서 문장 예

아래 값은 모두 만든 예시입니다.

- 확인 문장: "증거물 2번(노트북)의 Electrum 지갑 파일에 주소 `bc1qexample0000000000000000000000000000000`(만든 예시)가 있습니다. 이 주소에서 0.25000000 BTC(25,000,000 사토시)를 보낸 트랜잭션(TXID 전체 값은 별표 1)이 블록 850,123(블록 해시는 별표 1)에 들어 있고, 이 블록의 헤더 시각은 2024-07-01 03:12:45 UTC 입니다. 조회는 2026-09-20 10:00 UTC 에 분석실 자체 노드로 했습니다."
- 추정 문장: "위 트랜잭션의 두 번째 출력은 잔돈 주소일 가능성이 있습니다. 이는 BlockSci 의 잔돈 휴리스틱 결과이며, 이 휴리스틱은 같은 트랜잭션에 대해 다른 후보를 낼 수 있습니다."
- 거래소 문장: "거래소가 제출한 자료에 이 트랜잭션 해시와 같은 입금 기록이 있고, 자료의 시각 값은 `2024-06-30 20:15:02`(시간대 표시 없음, 만든 예시)입니다. 시간대가 적혀 있지 않아 UTC 로 바꾸지 않았습니다."

## 함께 볼 페이지

- [조사 절차](../acquisition/investigation-process.md)
- [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md)
- [거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md)
- [빼앗긴 자산은 어디로 갔나](../../04-scenarios/asset-flow/stolen-funds.md)
- [거래소로 들어갔나](../../04-scenarios/asset-flow/exchange-deposit.md)
- 다른 핸드북의 보고서 페이지: [Android](https://urock-ailab.github.io/forensics-handbook/android/03-techniques/reporting/forensic-report.html), [iOS](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/reporting/forensic-report.html), [클라우드](https://urock-ailab.github.io/forensics-handbook/cloud/03-techniques/reporting/forensic-report.html), [네트워크](https://urock-ailab.github.io/forensics-handbook/network/03-techniques/reporting/forensic-report.html)

## 참고 문헌

1. SWGDE, "SWGDE Requirements for Report Writing in Digital and Multimedia Forensics", 18-Q-002, Version 1.0, 2018-11-20. https://www.swgde.org/wp-content/uploads/2023/11/2018-11-20-SWGDE-Requirements-for-Report-Writin.pdf
2. SWGDE, "Tech Notes on Cryptocurrency", 23-F-006-1.1, Version 1.1, 2024-12-09. https://www.swgde.org/wp-content/uploads/2025/01/2024-12-09-Tech-Notes-on-Cryptocurrency-23-F-006-1.1.pdf
3. Tyler Thomas, Tiffanie Edwards, Ibrahim Baggili, "BlockQuery: Toward forensically sound cryptocurrency investigation", Forensic Science International: Digital Investigation 40, 2022. doi:10.1016/j.fsidi.2022.301340
4. Bitcoin Developer Reference, Block Chain. https://developer.bitcoin.org/reference/block_chain.html
5. Bitcoin Developer Guide, Block Chain. https://developer.bitcoin.org/devguide/block_chain.html
6. Bitcoin Developer Guide, Transactions. https://developer.bitcoin.org/devguide/transactions.html
7. Bitcoin Developer Reference, Transactions. https://developer.bitcoin.org/reference/transactions.html
8. Bitcoin Core, JSON-RPC Interface (Security). https://github.com/bitcoin/bitcoin/blob/master/doc/JSON-RPC-interface.md
9. ethereum.org, Transactions. https://ethereum.org/en/developers/docs/transactions/
10. ethereum.org, JSON-RPC API. https://ethereum.org/en/developers/docs/apis/json-rpc/
11. Etherscan API, Get Normal Transactions By Address (txlist). https://docs.etherscan.io/api-reference/endpoint/txlist.md
12. Etherscan API, Get ERC20 Token Transfer Events (tokentx). https://docs.etherscan.io/api-reference/endpoint/tokentx.md
13. RLEAPP, coinbaseComplianceReport.py. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseComplianceReport.py
14. RLEAPP, coinbaseArchive.py. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseArchive.py
15. BlockSci, Change address heuristics. https://github.com/citp/BlockSci/blob/master/docs/reference/heuristics/change.rst
16. BlockSci, Clustering. https://github.com/citp/BlockSci/blob/master/docs/reference/clustering/clustering.rst
17. BIP 173, Base32 address format for native v0-16 witness outputs. https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki
18. ERC-55, Mixed-case checksum address encoding. https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-55.md
19. Hugo Schnoering, Pierre Porthaux, Michalis Vazirgiannis, "Assessing the Efficacy of Heuristic-Based Address Clustering for Bitcoin", arXiv, 2024. doi:10.48550/arXiv.2403.00523
20. Jan Zavřel, Michal Koutenský, Daniel Dolejška, Vladimír Veselý, "Tumbling down the stairs: Exploiting a tumbler's attempt to hide with ordinary-looking transactions using wallet fingerprinting", Forensic Science International: Digital Investigation, 2025. doi:10.1016/j.fsidi.2025.301869
21. Pascal Tippe, Christoph Deckers, "Unmixing the mix: Patterns and challenges in Bitcoin mixer investigations", Forensic Science International: Digital Investigation 52, 2025. doi:10.1016/j.fsidi.2025.301876
22. Miroslav Šafář, Jan Pluskal, Vladimír Veselý, Ondřej Ryšavý, "The enemy of reproducibility is opacity: What's inside the Elliptic bitcoin dataset (and why it is wrong)", Forensic Science International: Digital Investigation, 2026. doi:10.1016/j.fsidi.2026.302124
23. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, "Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications", arXiv, 2022. doi:10.48550/arXiv.2205.14611
24. Binance.US, Law Enforcement Guide. https://support.binance.us/en/articles/9842980-binance-us-law-enforcement-guide
25. 특정 금융거래정보의 보고 및 이용 등에 관한 법률 제5조의4. https://www.law.go.kr/법령/특정금융거래정보의보고및이용등에관한법률
26. 금융위원회, 트래블룰 시행 보도자료(2022). https://www.fsc.go.kr/no010101/77579
27. Blockstream, Esplora HTTP REST API. https://github.com/Blockstream/esplora/blob/master/API.md
28. ethereum.org, Gas and fees. https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/gas/index.md
