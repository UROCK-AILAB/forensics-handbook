---
title: "거래소 자료 분석"
parent: "기법 · 분석"
nav_order: 320
---

# 거래소 자료 분석 (Exchange Data Analysis)

블록체인에는 주소와 금액만 남고 이름은 남지 않아서, 자금을 사람과 잇는 기록은 대개 거래소가 보관한 계정 명의·입출금·접속 기록입니다. 이 페이지는 기기와 블록체인에서 거래소로 이어지는 단서를 모으고, 거래소에 기록을 요청하고, 받은 회신 자료를 블록체인 기록과 한 행씩 맞춰 보는 순서를 다룹니다. 회신 파일의 형식은 [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md), 제도와 보존 기간은 [거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md)에서 다룹니다.

## 언제 쓰나

추적하던 자금이 거래소 주소로 들어가거나 거래소 주소에서 나왔을 때 이 절차를 씁니다. 공개 블록 탐색기는 주소를 사람이나 회사에 연결해 주지 않습니다. Android 지갑 앱을 시험한 연구에서도 블록 탐색기로는 상대가 누구인지 알 수 없었고, 상용 추적 도구가 보낸 쪽을 Coinbase 로 표시한 뒤에야 Coinbase 에 KYC (Know Your Customer, 본인 확인) 기록을 요청하는 영장으로 이어질 수 있었습니다[6]. 미국의 믹서 사건 세 건(ChipMixer·Helix·Bitcoin Fog)에서도 수사기관이 넣어 본 시험 거래로는 운영자를 바로 특정하지 못했고, 믹서 거래 밖의 정보로 운영자를 찾았습니다. ChipMixer 는 서버의 IP 주소를 찾아서, Bitcoin Fog 는 호스팅 대금으로 낸 비트코인을 따라가서 운영자를 특정했습니다[8].

기기에서 거래소 앱이나 거래소 알림 메일이 나왔을 때도 씁니다. 기기에 남은 캐시는 계정이 있었다는 단서일 뿐이고, 입출금 내역과 잔액은 거래소 기록으로 확인합니다([거래소 앱](../../02-artifacts/mobile/exchange-apps.md)).

## 절차

1. **거래소로 이어지는 단서를 모읍니다.** 기기의 지갑 앱·거래소 앱·메일에서 나온 트랜잭션 해시(TXID), 상대 주소, 금액, 시각을 한 표로 정리합니다. 블록체인에서는 입금 주소로 보이는 주소를 찾습니다. 거래소는 고객마다 입금 주소를 따로 만들고, 입금 주소에 들어온 돈을 본 주소로 옮깁니다[7]. 이더리움에서 이렇게 옮겨지는 금액은 수수료만큼 조금 적은 경우가 많고, 토큰은 대개 받은 수량 그대로 옮겨집니다[7]. 받은 금액이 작으면 거래소가 다른 입금이 모일 때까지 옮기지 않고 기다리기도 합니다[7]. 비트코인에서 입금 주소를 모으는 트랜잭션과 일괄 지급 트랜잭션의 모양은 [거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md)에, 주소를 묶는 방법의 한계는 [주소 묶기와 그 한계](clustering.md)에 있습니다.

2. **요청할 법인과 기록을 정합니다.** 같은 상표라도 법인이 다르면 기록을 가진 회사가 다릅니다. Binance.US 를 운영하는 BAM Trading Services 는 Binance Holdings 와 다른 회사라 Binance 기록이 없고, Binance.US Web3 Wallet 기록은 BAM Technology Services Inc. 앞으로 따로 요청합니다[1]. 거래 시점과 법정 보존 기간을 비교해 어떤 기록이 남아 있을지 먼저 판단합니다. 국내 가상자산사업자의 고객확인 자료와 송금인·수취인 정보는 고객과 가상자산거래로 생긴 채권채무관계를 정산한 날부터 5년간 보존 대상입니다[9]. 기록 종류별 보존 기간은 [거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md)의 표에 있습니다.

3. **요청서에 체인 기록을 붙입니다.** Binance.US 에 트랜잭션 해시로 요청할 때는 금액·입력 주소·출력 주소·UTC 시각을 함께 적고, 지갑 주소로 요청할 때는 TXID·UTC 시각·금액을 함께 적습니다[1]. 요청서는 옮겨 적다 생기는 오류를 줄이려고 편집할 수 있는 형식으로 보냅니다[1]. 이렇게 보낸 값은 나중에 회신과 맞춰 볼 기준이 되므로 요청서 사본을 사건 기록에 남깁니다.

4. **회신 원본을 보존하고 중복을 확인합니다.** 회신 파일마다 해시를 구하고 분석은 사본으로 합니다. 한 회신 안에 같은 보고서가 여러 번 들어 있을 수 있고, RLEAPP 는 사본마다 행을 따로 내놓습니다[2][4]. 행 수를 세기 전에 Source File 열과 파일 해시를 비교해 같은 파일을 한 번만 셉니다. 스프레드시트 프로그램으로 원본을 열면 지수 표기 금액이나 셀 안의 줄바꿈이 바뀔 수 있으니 텍스트로 읽습니다([거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md)).

5. **파싱하고 빠진 값이 없는지 봅니다.** 회신의 섹션과 열은 회신마다 다릅니다. RLEAPP 의 Coinbase·Robinhood 분석기는 합성 회신과 2025년 실제 회신 한 건의 파일 구성에 맞춰 만들어서 다른 해의 회신은 구성이 다를 수 있고, 모르는 열은 "Other Columns (as produced)" 에 JSON 으로 남깁니다[2][4]. Coinbase 보고서에서 모르는 섹션은 "Other Sections" 에 셀 그대로 남습니다[2]. Robinhood PDF 와 CSV 에서 분석기가 레코드로 넣지 못한 글자는 "Robinhood - Parsing Notes" 에 모입니다[4]. 이 결과들이 비어 있지 않으면 해당 값을 원본에서 직접 읽습니다. Robinhood 의 암호화폐 전송·주문 CSV 에는 계좌번호가 없어서, 어느 계정의 기록인지는 회신 묶음과 파일 경로로 확인합니다[4].

6. **시각을 원래 값과 함께 UTC 로 맞춥니다.** 거래소 기록의 시각은 거래소가 남긴 값이라 블록 시각과 다르고, 한 보고서 안에서도 오프셋이 붙은 값, 시간대 약어가 붙은 값, 시간대가 없는 값이 섞일 수 있습니다[2]. RLEAPP 의 Coinbase compliance 보고서 분석기는 오프셋(`-0800`, `Z`)이나 시간대 약어가 있는 값만 UTC 로 바꾸고, 원래 값과 변환 근거를 "(as produced)" 열과 "Time Basis" 열에 함께 남깁니다[2]. 시간대가 없는 값은 바꾸지 않고 "zone not stated" 로 둡니다[2][4]. 표기별 예와 해석은 [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md), 블록 시각·기기 시각과 합치는 방법은 [암호화폐 타임라인](timeline.md)에 있습니다.

7. **체인에 남는 행과 남지 않는 행을 나눕니다.** 해시 열이 채워진 행만 블록체인에서 찾을 수 있고, 거래소 안에서 사고판 행은 해시가 비어 있습니다([거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md)). 회신 파일에서 해시가 들어 있는 열은 아래와 같습니다.

   | 회신 파일 | 해시 | 상대 주소 | 금액·자산 | 시각 | 네트워크·상태 |
   |---|---|---|---|---|---|
   | Coinbase `compliance_report.csv` 의 `TRANSACTIONS` | `TRANSACTION HASH` | `TO` | `AMOUNT`, `CURRENCY` | `TIMESTAMP` | `NETWORK`, `STATUS`[2] |
   | Coinbase `coinbase_data.json` | `Crypto_hash` | `To` | `Amount`, `Currency` | `Timestamp` | —[3] |
   | Robinhood `crypto_account_transfers.csv` | `blockchain_txn_id` | `to_address`, `address_tag` | `amount`, `currency_code`, `network_fee` | `created_at` | `network`, `state`, `blockchain_txn_state`[4] |

   입금 쪽은 거래소가 계정에 만들어 준 주소 목록으로 봅니다. Coinbase 보고서의 주소 섹션에는 `CREATED`, `ACCOUNT`, `NETWORK`, `ADDRESS`, `LABEL`, `CALLBACK URL` 열이 있습니다[2].

8. **해시로 체인 기록을 조회해 한 행씩 맞춥니다.** 조회한 트랜잭션의 금액, 받는 주소, 블록 시각, 확정 여부를 회신 행 옆에 적습니다. 거래소는 고객에게 보낼 돈을 거래소 주소에서 보내므로[8], 출금이 어느 계정에서 나갔는지는 회신 행으로만 알 수 있습니다. 입금은 체인에서 본 받는 주소가 회신의 주소 목록에 있는지로 확인합니다. 조회 방법에 따라 어떤 주소를 조사하는지가 탐색기 운영자에게 드러날 수 있으므로 조회 도구는 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)를 보고 고릅니다. 비트코인과 이더리움에서 트랜잭션을 따라가는 방법은 [비트코인 거래 따라가기](bitcoin-tracing.md), [이더리움 거래 따라가기](ethereum-tracing.md)에 있습니다.

9. **맞지 않는 행을 따로 표시합니다.** 해시가 체인에 없거나, 금액·주소·네트워크가 다르거나, 시각 차이가 설명되지 않는 행은 결과표에서 따로 표시하고 이유를 적습니다. Binance.US 처럼 회신 자료의 정확성과 완전성을 보증하지 않는 거래소가 있어서[1], 대조를 통과한 행과 거래소 기록에만 있는 행을 나눠 보고합니다.

10. **접속 기록을 기기 기록과 잇습니다.** 회신의 로그인 이벤트(IP, 기기 지문, user agent)[2]를 기기에서 나온 접속 흔적·네트워크 기록과 같은 시간축에 놓고 비교합니다([암호화폐 타임라인](timeline.md)).

> 그림 자리: 기기 단서(TXID·주소) → 요청서 → 회신 행(해시·주소·시각) → 체인 조회 결과(블록 시각·금액) → 일치·불일치 표시로 이어지는 대조 흐름

## 도구

- **RLEAPP** 는 수사기관에 온 회신 자료를 읽는 공개 도구입니다. `coinbaseComplianceReport.py` 는 `*compliance_report*.csv`[2], `coinbaseArchive.py` 는 `**/coinbase_data.json`[3], `robinhoodReturns.py` 는 Robinhood 의 CSV·PDF[4], `cashappReturns.py` 는 `*-for-subject-SQ_CASH-*.xlsx` 형식의 Cash App 회신[5]을 읽습니다.
- **기기 쪽 분석기** 로는 iOS Coinbase 앱 캐시를 읽는 iLEAPP `coinbase.py` 가 있습니다([거래소 앱](../../02-artifacts/mobile/exchange-apps.md)).
- **체인 조회** 는 블록 탐색기나 자체 노드로 합니다([블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)).
- **표 도구**: 회신 행과 체인 조회 결과를 해시 기준으로 합치는 일은 스프레드시트나 SQLite 로 할 수 있습니다. 원본 파일이 아니라 사본을 불러옵니다.

## 함정과 한계

- **도구마다 시간대 가정이 다릅니다.** 같은 RLEAPP 안에서도 Coinbase compliance 보고서와 Robinhood 분석기는 시간대 없는 값을 바꾸지 않지만[2][4], `coinbase_data.json` 분석기와 Cash App 분석기는 시간대 없는 ISO 값을 UTC 로 보고 바꿉니다[3][5]. 도구가 내놓은 UTC 열만 보고 시각을 비교하지 말고, 원래 값과 변환 근거를 함께 봅니다.
- **거래소 시각과 블록 시각은 다릅니다.** 출금은 고객 요청 → 거래소 처리 → 블록 포함 순서로 일어나서 몇 분 차이가 날 수 있습니다. 시각만으로 행을 짝짓지 않고 해시·금액·주소를 먼저 맞춥니다([거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md)).
- **입금 주소와 본 주소를 섞지 않습니다.** 입금 주소는 고객마다 다르지만, 거기서 옮겨 간 본 주소에는 여러 고객의 돈이 섞입니다[7]. 본 주소나 핫월렛 주소만 보고 특정 고객을 가리킬 수 없습니다.
- **같은 입금 주소로 보낸 주소들은 같은 사람일 가능성이 높을 뿐입니다.** 여러 주소가 같은 입금 주소로 돈을 보내면 같은 주체일 가능성이 높습니다[7]. 다만 거래소끼리 주고받은 돈이 이 모양에 섞일 수 있어서, 알려진 거래소 주소를 빼고 본 주소 하나로만 옮기는 입금 주소만 골라야 큰 거래소들이 한 주체로 잘못 묶이지 않습니다[7]. 확정은 거래소 회신으로 합니다.
- **추적 도구의 거래소 표시는 근거가 드러나지 않을 수 있습니다.** 상용 추적 도구가 트랜잭션을 거래소와 연결해도 어떻게 그 결론을 냈는지 보여 주지 않는 경우가 있어서, 영장 청구서에 그 정확성을 설명하기 어려울 수 있습니다[6]. 도구의 표시는 요청할 곳을 정하는 단서로 쓰고, 사실 확인은 회신과 체인 대조로 합니다.
- **믹서가 거래소 계정을 거치면 모양이 섞입니다.** 한 믹서는 이용자에게 돌려줄 돈을 거래소(HTX) 주소에서 보냈는데, 여러 주소가 한 트랜잭션으로 보낸 모양은 믹서의 특징이 아니라 거래소가 고객에게 지급하는 모양일 가능성이 높았습니다[8]. 같은 믹서가 모은 돈도 여러 주소를 거쳐 거래소로 들어가서, 그 계정의 명의자를 찾는 단서가 될 수 있습니다[8].
- **"no records" 회신은 그 법인에 기록이 없다는 뜻입니다.** Binance.US 는 해당 기록이 없으면 "no records" 로 답하고, 회신 뒤에 새 정보가 생겨도 회신을 고치거나 보충할 의무가 없습니다[1].

## 결과를 어떻게 해석하나

**증명하는 것.** 거래소 회신으로는 거래소가 그 계정에 대해 기록한 사실을 확인합니다. 계정 명의와 KYC 정보, 로그인 IP·기기, 입금 주소 목록, 입출금 요청 기록이 여기에 들어갑니다[1][2][4]. 회신의 출금 행에 있는 해시로 조회한 트랜잭션이 금액·받는 주소·네트워크까지 맞으면, 그 트랜잭션이 그 계정의 출금 요청으로 나갔다고 두 기록을 근거로 쓸 수 있습니다. 체인에서 본 받는 주소가 회신의 주소 목록에 있으면, 그 입금이 그 계정 앞으로 들어갔다고 쓸 수 있습니다.

**증명하지 못하는 것.** 거래소 안에서 사고판 기록은 체인으로 확인할 수 없고 거래소 기록에만 있습니다. 출금 상대 주소가 누구 것인지는 회신만으로 알 수 없고, 그 주소가 다른 거래소 주소라면 그 거래소에 다시 요청해야 합니다. 로그인 IP 와 기기 기록으로는 어느 접속 환경이었는지만 알 수 있고, 그 순간 누가 조작했는지는 다른 기록과 함께 판단합니다. 거래소가 보증하지 않은 값은 체인과 대조한 만큼만 확정할 수 있습니다[1].

**보고서 문장 예 (만든 예시).** "○○ 거래소 회신(파일 SHA-256 aa11…ff99)의 TRANSACTIONS 섹션 12번째 행에는 계정 U-1001 이 2025-03-02 04:10:00 -0800 에 주소 bc1q…xyz 로 0.05 BTC 를 보낸 기록이 있고, 행의 해시 3f9a…c21d 로 조회한 트랜잭션은 같은 주소로 0.05 BTC 를 보냈으며 2025-03-02 12:14:37 UTC 블록에 포함되어 있습니다. 회신 시각을 UTC 로 바꾸면 12:10:00 이고 블록 시각과 4분 37초 차이가 납니다."

## 참고 문헌

1. Binance.US, "Binance.US law enforcement guide", 2026-07-28. https://support.binance.us/en/articles/9842980-binance-us-law-enforcement-guide
2. RLEAPP, `scripts/artifacts/coinbaseComplianceReport.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseComplianceReport.py
3. RLEAPP, `scripts/artifacts/coinbaseArchive.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseArchive.py
4. RLEAPP, `scripts/artifacts/robinhoodReturns.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/robinhoodReturns.py
5. RLEAPP, `scripts/artifacts/cashappReturns.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/cashappReturns.py
6. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, "Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications", arXiv, 2022. doi:10.48550/arXiv.2205.14611
7. Friedhelm Victor, "Address Clustering Heuristics for Ethereum", Financial Cryptography and Data Security (FC 2020), LNCS, Springer, 2020. doi:10.1007/978-3-030-51280-4_33
8. Pascal Tippe, Christoph Deckers, "Unmixing the mix: Patterns and challenges in Bitcoin mixer investigations", Forensic Science International: Digital Investigation 52, 2025. doi:10.1016/j.fsidi.2025.301876
9. 특정 금융거래정보의 보고 및 이용 등에 관한 법률 (시행 2026. 8. 20.) 제5조의4. https://www.law.go.kr/법령/특정금융거래정보의보고및이용등에관한법률
