---
title: "거래소가 제공하는 자료"
parent: "아티팩트 · 거래소와 체인 기록"
nav_order: 240
---

# 거래소가 제공하는 자료 (Exchange Records)

수탁형 거래소는 고객의 키와 거래 기록을 서버에 두기 때문에, 계정 명의·입출금 주소·출금 해시·로그인 IP 같은 기록은 기기가 아니라 거래소가 수사기관 요청에 답해 보내는 회신 자료 (law enforcement return) 로 들어옵니다. 이 페이지는 회신 자료에 어떤 항목이 어떤 모양으로 들어 있는지, 시각을 어떻게 읽어야 하는지, 그리고 블록체인 기록과 무엇이 다른지를 다룹니다. 요청 절차와 분석 순서는 [거래소 자료 분석](../../03-techniques/analysis/exchange-analysis.md)에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

수탁형 지갑에서는 거래소가 키를 대신 보관하므로, 거래소 안에서 사고판 기록과 입출금 기록이 거래소 서버에만 있습니다([지갑의 종류](../../01-foundations/wallets/wallet-types.md)). 수사기관이 영장이나 소환장 같은 법적 요청을 보내면 거래소가 이 기록을 CSV·JSON·PDF 로 내보내 회신합니다[1][3][4][6]. Coinbase 는 형사 사건 소환장을 Kodex 포털로 받습니다[8].

국내에서는 법이 기록을 남기게 합니다. 가상자산사업자는 고객확인 자료, 의심거래 보고 관련 자료, 송금인·수취인 정보를 금융거래 관계가 끝난 때부터 5년간 보존해야 합니다[10]. 가상자산사업자에게 관계가 끝난 날은 "고객과 가상자산거래로 인한 채권채무관계를 정산한 날" 입니다[10]. 보존은 문서·마이크로필름·디스크·자기테이프나 그 밖의 전산정보처리조직으로 하고, 원칙적으로 주된 사무소 소재지에 둡니다[11]. 가상자산사업자는 고객별로 거래내역을 분리해 관리해야 하므로[10][11], 고객 한 명 단위로 거래내역을 뽑을 수 있습니다.

사업자 사이에 가상자산을 옮길 때 붙는 송·수신인 정보(트래블룰, Travel Rule)도 기록으로 남습니다. 제도 설명은 [거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md)에 있고, 여기서는 남는 기록만 봅니다. 보내는 사업자는 1백만원 상당 이상을 옮길 때 보내는 고객과 받는 고객의 성명과 가상자산주소를 받는 사업자에게 넘깁니다[11]. 이렇게 모은 정보는 거래관계가 끝난 때부터 5년간 보존합니다[12]. 트래블룰은 사업자 사이의 이전에만 적용되고, 개인지갑으로 보낼 때 주소를 미리 등록하게 하는 것은 업계가 스스로 하는 일입니다[12]. 그래서 개인지갑으로 나간 출금에는 상대방 성명이 법적 의무로 남지 않고, 거래소가 받아 둔 등록 정보가 있을 때만 남습니다[9].

## 위치와 버전별 차이

회신 자료는 거래소마다 구성이 다릅니다. 같은 거래소도 회신마다 들어 있는 섹션이 다르고, 연도에 따라 배치가 다를 수 있습니다[1]. 공개 도구가 다루는 회신은 아래와 같습니다.

| 거래소 | 파일 | 형식 |
|---|---|---|
| Coinbase | `compliance_report.csv` (IdvComplianceReport) | 섹션 여러 개가 들어 있는 CSV 한 개[1] |
| Coinbase | `coinbase_data.json` | 최상위 키 이름에 `Financial`·`Interaction`·`Personal` 이 들어간 JSON[3] |
| Robinhood | `crypto_account_transfers.csv`, `crypto_account_orders.csv`, `data_request_ip_timestamps_*.csv`, `*_1099_*.csv`, Account Master PDF, 계좌 명세서 PDF, `*_rhc_statement_*.pdf` | CSV 와 PDF 가 섞여 있음[4] |

국내 거래소는 회신 형식이 공개되어 있지 않아서, 개인정보처리방침에서 무엇을 모으고 얼마나 보유하는지 확인합니다. 아래 표는 각 회사가 공개한 문서의 내용입니다.

| 거래소 | 모으는 거래·접속 정보 | 보유 기간 |
|---|---|---|
| 업비트 (방침 V2.56, 2026-07-31 적용) | 디지털 자산 거래일시·수량·종류·자산명·원화 환산금액·입출금기록·잔고·입출금 지갑주소, 등록한 개인 지갑주소, 출금주소 등록 정보, 자금출처 확인 자료(입금일시·입금 TXID·자산의 출처 등), 기기정보(OS·모델명·통신사·ADID·IDFA·IDFV)·IP 주소·서비스 이용기록[9] | 디지털 자산 거래 내역 기록 15년, 고객 확인·의심거래 기록 5년, 로그인 기록 3개월 이상, 입출금 때 연계 데이터로 VerifyVASP Pte. Ltd.(싱가포르)에 보낸 송·수신자 이름·생년월일·디지털 자산 주소·자산명·수량 5년[9] |
| Coinbase | 보낸 사람·받는 사람 이름, 금액, 결제 수단, 날짜·시각, 기기·OS·브라우저, IP 주소, 연결한 Base App(이전 Coinbase Wallet)의 지갑 주소, 외부 입금·외부 출금의 상대방 정보(트래블룰)[7] | 국가와 법적 의무에 따라 내부 방침으로 정함(기간 숫자 없음)[7] |
| Binance.US | 회신에 담을 수 있는 자료: KYC 정보, 잔액, 은행 계좌, 거래 내역, 입금·출금 내역, IP 내역, 기기 내역, 고객과 주고받은 연락[6] | 문서에 기간 없음 |

법령도 시점에 따라 바뀝니다. 트래블룰은 2022년 3월 25일부터 본격 시행됐습니다[12]. 2026년 3월 30일 입법예고된 시행령 개정안은 트래블룰을 100만원 미만 이전까지 넓히고 받는 사업자에게도 정보를 확보할 의무를 지우는 내용입니다[13]. 2026년 8월 18일 공포된 시행령(대통령령 제36592호)은 제10조의10(가상자산이전 시 정보제공)과 제10조의20(가상자산사업자의 조치)의 개정규정을 공포 후 6개월이 지난 날부터 시행하도록 정했습니다[11]. 2027년 2월 19일 시행 본문의 제10조의10 은 금액 기준 없이 사업자가 다른 사업자에게 가상자산을 옮기는 모든 경우에 정보를 넘기게 합니다[11]. 그래서 100만원 미만 이전에 상대방 정보가 있는지는 이전 날짜가 이 시행일 전인지 뒤인지로 판단합니다.

## 구조

### Coinbase `compliance_report.csv`

CSV 한 파일에 섹션이 여러 개 들어 있습니다. 섹션은 셀 하나만 있는 행으로 시작하고, 그 글자는 `***` 로 끝납니다(예: `TRANSACTIONS ***`)[1]. 비어 있지 않은 첫 행이 `USER ATTRIBUTES ***` 여야 이 보고서로 봅니다[1]. `USER ATTRIBUTES`·`IDENTITY`·`PERSONAL DETAILS` 는 이름과 값이 한 행에 하나씩 있는 목록이고, `TOTALS` 같은 몇 섹션은 작은 격자이며, 나머지는 머리글 행이 있는 표입니다[1][2].

| 섹션 | 열 | 알 수 있는 것 |
|---|---|---|
| `USER ATTRIBUTES` | USER ID, NAME, EMAIL, CREATED 등 | 계정 식별자·이름·이메일 |
| `IDENTITY` | FIRST NAME, LAST NAME, SSN, ADDRESS1, CITY, STATE, ZIP, BIRTHDATE M/D/Y | 신원 정보 |
| `JUMIO PROFILES` | DATE, TYPE, ID NUMBER, STATUS, NAME, DOB, ADDRESS, UNIT NUMBER, CITY, STATE, ZIP, COUNTRY | 신분증 인증 기록 |
| `PHONE NUMBERS` | NUMBER, COUNTRY, VERIFIED | 전화번호 |
| `PREVIOUS EMAILS` | CHANGED FROM, CHANGED TO, CHANGED AT, CONFIRMED AT | 이메일 변경 이력 |
| `BANK ACCOUNTS` | CUSTOMER NAME, BANK NAME, ACCOUNT NUMBER, ROUTING NUMBER, ACCOUNT TYPE, VERIFIED, VERIFICATION METHOD | 연결 은행 계좌 |
| 자산 기호 + `ADDRESSES` (예: `BTC/ETH/USDC ADDRESSES`) | CREATED, ACCOUNT, NETWORK, ADDRESS, LABEL, CALLBACK URL | 계정에 딸린 암호화폐 주소와 네트워크 |
| `TRANSACTIONS` | TIMESTAMP, ACCOUNT NAME, TYPE, STATUS, BALANCE, AMOUNT, CURRENCY, TO, PRO TRANSFER, NOTES, EQUIV USD, TRANSACTION HASH, PAYMENT METHOD DETAILS, TRANSACTION ID, NETWORK | 매수·송금·수신 내역 |
| `EVENTS` | TIMESTAMP, ACTION, IP, FINGERPRINT, USER AGENT, LOCATION, SOURCE, DETAILS | 로그인 같은 계정 이벤트 |
| `MANUAL REVIEWS` | CREATED, UPDATED, STATUS, REASON, REASON VALUE | 거래소 내부 검토 |

이 밖에 `BILLING ADDRESSES`, 결제 수단 섹션(`PAYMENT CARDS`, `PAYMENT CARD (LEGACY) PAYMENT METHOD`, `PAYPAL ACCOUNTS`, `SEPA`·`FEDWIRE`·`SWIFT`·`UK`·`BANKWIRE`·`INTRABANK PAYMENT METHOD`), `EXCHANGE TRANSFERS`, `EXCHANGE TRANSACTIONS`, `TOTALS`, `EXCHANGE TOTALS` 가 있습니다[1]. `PAYMENT CARD (LEGACY)` 섹션 안에는 표가 두 개 있고, 두 번째 표는 `PAN` 으로 시작하는 머리글을 씁니다[1]. `TOTALS` 표는 첫 셀이 빈 행에 자산 이름과 `EQUIV USD` 가 있고, 그 아래 행에 BALANCE·BOUGHT·DEPOSITED 같은 지표가 있습니다[2]. 주소 섹션의 제목은 회신마다 자산 목록이 달라서, 제목이 `ADDRESSES` 로 끝나고(단 `BILLING ADDRESSES` 제외) `ADDRESS`·`NETWORK` 열이 있는지로 찾습니다[1].

`TRANSACTIONS` 의 모양은 아래와 같습니다(RLEAPP 합성 데이터 생성기의 모양을 따라 만든 예시).

```text
TRANSACTIONS ***
TIMESTAMP,ACCOUNT NAME,TYPE,STATUS,BALANCE,AMOUNT,CURRENCY,TO,...,TRANSACTION HASH,...,TRANSACTION ID,NETWORK
2021-03-14 01:59:59 -0800,BTC Wallet,Buy,Complete,0.01,0.01000000,BTC,,...,,...,EXTX0001,bitcoin
2021-03-14 03:00:00 -0700,ETH Wallet,Send,Complete,0,-1.23E-7,ETH,0x00…01,...,aaaa…aaaa,...,EXTX0002,ethereum
```

`Buy` 행은 `TO` 와 `TRANSACTION HASH` 가 비어 있고, `Send` 행은 상대 주소와 해시가 있으며 `AMOUNT` 가 음수입니다[2]. 거래소 안에서 사고판 기록은 블록체인에 올라가지 않으므로 해시가 없습니다.

### Coinbase `coinbase_data.json`

거래 내역 필드는 `Account_name`, `Amount`, `Balance`, `Coinbase_id`, `Crypto_hash`, `Currency`, `Instantly_exchanged`, `Notes`, `Timestamp`, `To`, `Transfer_id`, `Transfer_payment_method` 입니다[3]. 카드(`First6`, `Last4`, `Issuer` 등), 확인된 기기(`Confirmed`, `Ip_address`, `User_agent`), 사용 기기(`Accept_language`, `Platform`, `Timezone_string`, `User_agent` 등), 사이트 활동(`Action`, `Ip_address`, `Source`, `Time`), 제3자 권한(`Access_granted`, `Access_revoked`, `Name`) 목록도 있습니다[3]. `To` 값에 `@` 가 있으면 체인 주소가 아니라 이메일이고, 파서는 이 값을 사용자 목록에 따로 모읍니다[3].

### Robinhood 회신

암호화폐 전송 CSV 의 열은 `id`, `created_at`, `withdrawal_submitted_timestamp`, `currency_code`, `transfer_type`, `amount`, `network`, `network_fee`, `native_network_fee`, `usd_amount_at_request`, `fiat_amount_at_request`, `state`, `to_address`, `address_tag`, `blockchain_txn_id`, `blockchain_txn_state` 입니다[4][5]. 이 파일에는 계좌번호가 없어서, 어느 계정의 기록인지는 회신 묶음과 파일 경로로 확인합니다[4]. 주문 CSV 는 `Time Entered`, `UUID`, `Symbol`, `Side`, `Quantity`, `State`, `Order Type`, `Leaves Quantity`, `Entered Price`, `Average Price`, `Notional` 을 씁니다[4]. IP 로그 CSV 에는 `event_date_time`, `account_number`, `user__username`, `device_platform`, `user_agent`, `client_ip`, `geo_ip`, `geo_ip_timezone`, `geo_ip_city_name`, `geo_ip_country_name` 등이 있습니다[4]. Account Master PDF 는 거래소 내부 계정 화면을 브라우저로 인쇄한 것이고 수정 기록 표가 함께 있습니다[4].

## 증거로서 의미

회신 자료로 증명할 수 있는 것은 거래소가 자기 계정에 대해 기록한 사실입니다. 계정 명의와 KYC 정보, 신분증 인증 기록, 연결 은행 계좌와 카드, 로그인 이벤트의 IP·기기·user agent, 계정에 딸린 암호화폐 주소와 그 네트워크·생성 시각(`ADDRESSES` 의 `ADDRESS`·`NETWORK`·`CREATED`), 출금 요청의 상대 주소와 해시(`TO`·`TRANSACTION HASH`, `to_address`·`blockchain_txn_id`)가 여기에 들어갑니다[1][3][4].

증명하지 못하는 것도 분명합니다.

- 거래소 안에서 사고판 기록은 블록체인에 없습니다. 해시가 빈 행은 체인에서 찾을 수 없습니다[2][4].
- 출금 상대 주소가 누구 것인지는 회신만으로 알 수 없습니다. 개인지갑으로 나갔다면 트래블룰 대상이 아니므로 상대방 성명이 없습니다[12]. 상대가 다른 거래소나 서비스라면 그 주소로 여러 사람의 자금이 오갈 수 있습니다. Coinbase 에서 기기 지갑(Coinomi)으로 비트코인을 보낸 시험 트랜잭션에서, 보낸 쪽 주소는 2021년 7월 기준 1,361번 거래하고 1억 달러 넘게 주고받은 주소였습니다[14].
- 계정 주소로 코인을 보낸 사람이 누구인지는 트래블룰 정보가 없으면 회신에 없습니다.
- IP 와 기기 기록은 어느 접속 환경이었는지를 보여 줄 뿐, 그 순간 누가 조작했는지는 보여 주지 않습니다.
- 회신 내용의 정확성과 완전성을 보증하지 않는 거래소가 있습니다. Binance.US 는 정확성·완전성을 보증하지 않고, 회신 뒤에 새 정보가 생겨도 회신을 고치거나 보충할 의무가 없습니다[6].

보고서에는 "이 거래소 회신의 TRANSACTIONS 섹션에 이 계정이 이 주소로 이 금액을 보낸 행이 있고, 그 행의 해시와 같은 트랜잭션이 블록체인에 이 블록 시각으로 기록되어 있다" 처럼 두 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

거래소 기록의 시각은 거래소 서버가 요청이나 처리 시점에 남긴 시각이고, 블록 시각과 다릅니다([블록 시각과 확정](../../01-foundations/blockchain/block-time.md)). 2021년 6월 14일 Ledger 에서 Coinbase 로 비트코인을 보낸 시험에서, 블록체인 기록의 시각은 01:57 UTC 였고, Cellebrite Cloud Analyzer 로 가져온 Coinbase 기록은 출력 세 개가 01:57 UTC, 네 번째가 02:00 UTC 였으며 트랜잭션 해시는 들어 있지 않았습니다[14]. 거래소 시각과 체인 시각은 몇 분 차이 날 수 있으므로 시각만으로 행을 짝짓지 않고 해시·금액·주소를 함께 맞춥니다.

Coinbase 보고서 한 파일 안에서도 시각 표기가 섞여 있습니다[2].

| 표기 (만든 예시) | 시간대 정보 |
|---|---|
| `2021-02-01 10:00:00 -0800` | 숫자 오프셋 |
| `2021-01-05T12:00:00.123Z` | UTC, 밀리초 포함 |
| `January, 5 2021 04:28pm PST`, `March 9, 2025, 01:30am PST` | 북미 시간대 약어 |
| `2021-03-15 12:00:00` | 없음 |

RLEAPP 는 오프셋이나 약어가 적힌 값만 UTC 로 바꾸고, 시간대가 없는 값은 바꾸지 않은 채 "zone not stated" 로 표시합니다[1]. 약어는 적힌 그대로 고정 오프셋(PST=UTC-8, PDT=UTC-7 등)으로 읽으므로, 그날 서머타임이 적용됐는지와 약어가 어긋나도 약어를 따릅니다[1]. Robinhood 전송 CSV 의 `created_at` 에는 오프셋이 있어 UTC 로 바뀌지만, 주문의 `Time Entered` 와 IP 로그의 `event_date_time` 에는 시간대 표기가 없어 바뀌지 않습니다[4]. IP 로그에 `geo_ip_timezone` 열이 있어도 RLEAPP 는 이 값으로 `event_date_time` 을 바꾸지 않고, `geo_ip` 열들은 적힌 그대로 내놓습니다[4].

시간대가 없는 값을 다루는 방식은 도구마다 다릅니다. `compliance_report.csv` 와 Robinhood 파서는 이런 값을 바꾸지 않지만[1][4], `coinbase_data.json` 파서는 숫자만 있는 값은 Unix 초로, 시간대 없는 ISO 문자열은 UTC 로 보고 바꿉니다[3]. 시간대가 적히지 않은 값의 기준은 거래소에 문의하거나, 같은 거래의 해시로 블록 시각을 찾아 차이를 보고 판단합니다. 거래소에 요청서를 낼 때도 Binance.US 처럼 시각을 UTC 로 적으라고 요구하는 곳이 있습니다[6].

## 함정과 한계

- **같은 상표, 다른 법인.** Binance.US(BAM Trading Services)와 Binance(Binance Holdings)는 다른 회사라서, Binance.US 에는 Binance 의 기록이 없고 Binance 앞으로 온 요청에 답하지 않습니다[6]. Binance.US Web3 Wallet 기록은 BAM Technology Services Inc. 앞으로 따로 요청해야 합니다[6]. 해당 기록이 없으면 Binance.US 는 "no records" 라고 확인하는 회신을 보내는데[6], 이 회신은 그 법인에 기록이 없다는 뜻일 뿐입니다.
- **같은 보고서가 두 번.** 한 회신 안에 같은 보고서가 폴더만 달리해 바이트까지 같은 사본으로 들어 있는 경우가 있습니다[2]. 파서는 사본마다 행을 따로 내놓으므로, Source File 과 파일 해시를 비교한 뒤 행 수를 셉니다[1].
- **스프레드시트로 열면 값이 바뀔 수 있습니다.** 금액에 `-1.23E-7` 같은 지수 표기가 있고, 은행 이름처럼 셀 안에 줄바꿈이 있는 값이 있습니다[2]. 원본 파일은 텍스트로 읽고, 분석은 사본으로 합니다.
- **파일 끝의 안내 문장.** Robinhood CSV 끝에 레코드가 아닌 안내 문장 줄이 붙는 경우가 있습니다[4][5]. 행 수를 셀 때 뺍니다.
- **회신마다 다른 섹션과 열.** RLEAPP 파서는 합성 회신과 2025년 실제 회신 한 건의 배치에 맞춰 만들어서, 다른 연도의 회신은 배치가 다를 수 있습니다[1]. 모르는 열은 "Other Columns (as produced)" 에 JSON 으로, 모르는 섹션은 "Other Sections" 에 셀 그대로 남기므로[1], 이 두 결과가 비어 있는지 꼭 봅니다.
- **보유 기간.** 업비트의 로그인 기록 보유 기간은 3개월 이상입니다[9]. 요청이 늦으면 거래 기록은 있어도 IP 기록은 없을 수 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 회신 CSV 는 텍스트 파일이라 헥스로 볼 것이 많지 않지만, 문자 인코딩과 줄바꿈은 헥스로 확인합니다. RLEAPP 는 UTF-8(BOM 포함 허용), cp1252, latin-1 순서로 읽기를 시도합니다[1]. 파일이 `EF BB BF` 로 시작하면 BOM 이 붙은 UTF-8 입니다. 아래는 명세(파서가 요구하는 첫 행)로 만든 예시입니다.

```text
00000000  55 53 45 52 20 41 54 54 52 49 42 55 54 45 53 20   USER ATTRIBUTES
00000010  2A 2A 2A 0D 0A 55 53 45 52 20 49 44 2C 53 59 4E   ***..USER ID,SYN
00000020  54 48 55 53 45 52 30 31 0D 0A                     THUSER01..
```

`2A 2A 2A` 가 섹션 표시 `***` 이고 `0D 0A` 가 행 끝입니다. 섹션 제목 행에서 `2C`(쉼표)가 뒤따르면 빈 셀이 붙은 행이므로, 셀 개수가 아니라 비어 있지 않은 셀이 하나인지로 판단합니다[1].

**공개 도구로 한 번.** RLEAPP 의 `coinbaseComplianceReport` 는 `*compliance_report*.csv`, `coinbaseArchive` 는 `**/coinbase_data.json`, `robinhoodReturns` 는 `*crypto_account_transfers*.csv` 같은 경로 패턴으로 파일을 찾습니다[1][3][4]. 결과표의 UTC 열 옆에는 원래 값과 변환 근거(Time Basis) 열이 함께 나오므로[1], 보고서에는 원래 값을 함께 적습니다.

## 교차 검증

- 출금 행의 해시를 블록 탐색기나 자체 노드로 조회해 금액·주소·블록 시각을 맞춥니다([블록 탐색기 기록 읽기](block-explorers.md)).
- 기기에 남은 거래소 앱의 캐시와 계정 정보를 봅니다([거래소 앱](../mobile/exchange-apps.md)).
- 기기 지갑 앱에 있는 주소·해시가 회신의 계정 주소(`ADDRESSES`)나 출금 해시와 같은지 봅니다([Android 지갑 앱](../mobile/android-wallets.md), [iOS 지갑 앱](../mobile/ios-wallets.md), [Electrum](../desktop/electrum.md)).
- 거래소 시각, 블록 시각, 기기 시각을 한 표에 합칩니다([암호화폐 타임라인](../../03-techniques/analysis/timeline.md)).
- 거래소로 들어간 자금을 따라가는 순서는 [거래소로 들어갔나](../../04-scenarios/asset-flow/exchange-deposit.md)에 있습니다.

## 실습

RLEAPP 의 합성 데이터 생성 스크립트(`admin/test/scripts/gen_coinbase_compliance_synth.py`, `gen_robinhood_synth.py`)는 모든 값을 지어낸 회신 묶음을 만들어 줍니다[2][5]. 실제 개인정보 없이 구조를 연습할 수 있습니다.

1. Coinbase 합성 회신에서 `compliance_report.csv` 가 몇 개 나오는지 세고, 그중 내용이 같은 사본이 무엇인지 해시로 확인합니다. 보고서로 인정되지 않는 파일은 어느 것이고 왜 그런지 설명합니다.
2. `TRANSACTIONS` 에서 해시가 있는 행과 없는 행을 나누고, 그 차이가 거래 유형(`TYPE`)과 어떻게 연결되는지 설명합니다.
3. `2021-03-14 01:59:59 -0800` 과 `2021-03-14 03:00:00 -0700` 을 UTC 로 바꾸고, 두 값의 오프셋이 왜 다른지 미국의 2021년 서머타임 시작일과 비교해 설명합니다.
4. `Send` 행의 `TRANSACTION HASH` 를 이더리움 탐색기에서 조회하면 어떤 결과가 나올지 예상하고, 거래소 기록의 해시가 체인에 없을 때 보고서에 어떻게 쓸지 정리합니다.
5. Robinhood 합성 전송 CSV 에서 레코드가 아닌 줄을 찾아내고, `created_at` 과 IP 로그 `event_date_time` 중 어느 쪽을 UTC 로 바꿀 수 있는지 판단합니다.

## 참고 문헌

1. RLEAPP, `scripts/artifacts/coinbaseComplianceReport.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseComplianceReport.py
2. RLEAPP, `admin/test/scripts/gen_coinbase_compliance_synth.py`. https://github.com/abrignoni/RLEAPP/blob/main/admin/test/scripts/gen_coinbase_compliance_synth.py
3. RLEAPP, `scripts/artifacts/coinbaseArchive.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseArchive.py
4. RLEAPP, `scripts/artifacts/robinhoodReturns.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/robinhoodReturns.py
5. RLEAPP, `admin/test/scripts/gen_robinhood_synth.py`. https://github.com/abrignoni/RLEAPP/blob/main/admin/test/scripts/gen_robinhood_synth.py
6. Binance.US, "Binance.US Law Enforcement Guide". https://support.binance.us/en/articles/9842980-binance-us-law-enforcement-guide
7. Coinbase, "Coinbase Global Privacy Policy" (2026-05-27 갱신). https://www.coinbase.com/legal/privacy
8. Coinbase, "Legal and Privacy". https://www.coinbase.com/legal/us
9. 두나무(업비트), 개인정보처리방침 V2.56 (2026-07-31 적용). https://static.upbit.com/terms/private_data.html
10. 특정 금융거래정보의 보고 및 이용 등에 관한 법률 (시행 2026. 8. 20.) 제5조의4, 제8조. https://www.law.go.kr/법령/특정금융거래정보의보고및이용등에관한법률
11. 특정 금융거래정보의 보고 및 이용 등에 관한 법률 시행령 (대통령령 제36592호, 2026. 8. 18. 일부개정, 시행 2026. 8. 20. 본문과 2027. 2. 19. 시행 본문) 제10조의9, 제10조의10, 제10조의20, 부칙. https://www.law.go.kr/법령/특정금융거래정보의보고및이용등에관한법률시행령
12. 금융위원회, "3.25일 특정금융정보법상 트래블룰이 시행됩니다" 보도자료, 2022-03-25. https://www.fsc.go.kr/no010101/77579
13. 금융위원회, 「특정금융정보법」 시행령·감독규정 개정안 입법예고 보도자료, 2026-03-30. https://www.fsc.go.kr/no010101/86589
14. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, "Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications", arXiv, 2022. doi:10.48550/arXiv.2205.14611
