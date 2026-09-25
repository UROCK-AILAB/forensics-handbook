---
title: "지갑과 Apple Pay"
parent: "아티팩트 · 건강·지갑·워치"
nav_order: 1050
---

# 지갑과 Apple Pay (Wallet)

지갑 앱이 남기는 결제 거래 기록·패스(탑승권·멤버십 카드 등)·설정 파일을 읽고, 실제 카드 번호는 어디에도 기대할 수 없다는 한계를 함께 정리합니다.

## 무엇을 기록하나 · 왜 생기나

지갑 앱은 Apple Pay 에 등록한 결제 카드, 교통 카드, 탑승권·입장권·멤버십 같은 패스를 한곳에서 보여 줍니다. 결제 거래 표에는 가맹점 이름, 금액, 통화, 결제한 곳의 위치, 거래 상태를 적는 칸이 있고[1](버전·국가에 따라 행이 비어 있을 수 있음, 아래 "버전별 차이" 참고), 패스를 추가하면 패스 본문 파일이 저장됩니다[2].

조사에서는 이 기록으로 "그 시각 무렵 어느 가맹점에서 이 기기로 결제한 기록이 있는가", "어떤 탑승권이나 입장권을 받아 두었는가" 를 확인할 수 있습니다. 반면 카드 번호 자체는 기기 파일에 남지 않으므로(아래 "함정과 한계" 참고), 카드 발급사나 결제 사업자 자료와 맞춰 보는 단서로 씁니다.

## 위치와 버전별 차이

### 파일

공개 도구 iLEAPP 는 아래 패턴으로 지갑 파일을 찾습니다.

| 파일 이름 패턴 | 담는 내용 |
|---|---|
| `*/mobile/Library/Passes/passes23.sqlite*` | 결제 거래 기록[1] |
| `*/Cards/*.pkpass/pass.json` | 패스 본문[2] |
| `*/nanopasses.sqlite3*` | iLEAPP 가 "Apple wallet Nano passes" 로 부르는 패스 데이터베이스[2] |

`nanopasses.sqlite3` 는 이름으로 보아 워치 쪽 패스 데이터베이스로 보입니다. 폰과 워치 가운데 어디에 있는 파일인지는 검체에서 확인합니다.

### 로컬 백업의 지갑 파일

암호화하지 않은 로컬 백업에는 `HomeDomain` 안에 아래 세 파일이 있고, 세 파일 모두 최상위 키 아래에 `groups` 와 `timestamp` 가 있습니다.

| 도메인 · 상대 경로 |
|---|
| `HomeDomain` · `Library/Passes/CatalogOfRecord.plist` |
| `HomeDomain` · `Library/Passes/NonUbiquitousCatalogOfRecord.plist` |
| `HomeDomain` · `Library/Mobile Documents/com~apple~shoebox/UbiquitousCards/CatalogOfRecord.plist` |

로컬 백업의 파일 목록에는 `passes23.sqlite` 가 들어 있지 않을 수 있습니다. 백업에 거래 데이터베이스가 없더라도 기기에 거래 기록이 없었다고 단정하지 않고, 획득 방식을 먼저 기록합니다. 백업 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md)에서 다룹니다.

로컬 백업에는 지갑과 관련된 이름의 도메인도 있습니다.

| 도메인 | 비고 |
|---|---|
| `AppDomain-com.apple.Passbook` | 항목 6개 |
| `AppDomain-com.apple.PassbookSecureUIService`, `AppDomain-com.apple.PassbookUISceneService`, `AppDomain-com.apple.PassbookUIService` | |
| `AppDomainPlugin-com.apple.PassKit.*` | `PassKitSpotlightIndexExtension` 등 |
| `AppDomainPlugin-com.apple.finhealth.FinHealthTransactionInsightsExtension` 등 | 공개 자료 없음 |

`com.apple.Passbook` 은 이름으로 보아 지갑 앱의 번들 ID 로 보입니다. 도메인 이름을 읽는 법은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md)을 봅니다.

### 버전별 차이

iLEAPP 시험 표본에서 거래 행이 나온 것은 iOS 18.3.2(10행)와 iOS 16.5(1행) 두 기기뿐이고 나머지는 0행이었습니다[1]. 버전·기기·국가에 따라 거래 기록이 아예 남지 않을 수 있습니다. 버전별로 표 구조가 어떻게 바뀌는지는 공개 자료가 없어 검체에서 확인합니다.

## 구조

### `passes23.sqlite` 의 거래 표

`payment_transaction` 표의 주요 칸은 아래와 같습니다[1].

| 칸 | 담는 내용 |
|---|---|
| `transaction_date` | 거래 시각 |
| `merchant_name`, `locality`, `administrative_area` | 가맹점 이름과 지역 |
| `amount`, `currency_code` | 금액과 통화 |
| `location_date`, `location_latitude`, `location_longitude`, `location_altitude` | 거래 위치와 그 위치를 잰 시각 |
| `peer_payment_counterpart_handle`, `peer_payment_memo` | 개인 간 송금의 상대와 메모 |
| `transaction_status`, `transaction_type` | 거래 상태와 종류(번호) |

`amount` 는 iLEAPP 가 10000 으로 나눠 보여 줍니다. 이 나눗수는 제조사 문서에 나온 값이 아니라 알려진 거래와 비교해서 얻은 값입니다[1]. `transaction_status` 와 `transaction_type` 의 번호 뜻은 공개 자료가 없어, 검체에서 알려진 거래와 맞춰 봐야 합니다.

### 패스

`pass.json` 은 패스 하나의 본문이고, iLEAPP 는 특정 키만 고르지 않고 키와 값을 모두 풀어 보여 줍니다[2].

`nanopasses.sqlite3` 의 `PASS` 표에는 아래 칸이 있습니다[2].

| 칸 | 담는 내용 |
|---|---|
| `UNIQUE_ID` | 패스 식별자 |
| `ORGANIZATION_NAME`, `LOCALIZED_DESCRIPTION` | 발급 기관과 패스 설명 |
| `TYPE_ID` | 패스 종류 |
| `INGESTED_DATE` | 패스를 받아 들인 시각 |
| `DELETE_PENDING` | 지우기를 기다리는 상태 표시 |
| `ENCODED_PASS`, `FRONT_FIELD_BUCKETS`, `BACK_FIELD_BUCKETS` | 패스 본문과 앞·뒷면 항목 |

### 설정 파일

로컬 백업의 `HomeDomain` 안 `Library/Preferences/` 에는 아래 파일과 키가 있습니다. 값의 뜻을 설명한 공개 자료는 없습니다. 형식은 [속성 목록 파일](../../01-foundations/data-formats/plist.md)에서 다룹니다.

| 파일 | 키 |
|---|---|
| `com.apple.passd.plist` | `PDLastLogDate`(날짜), `PDUpgradeTasksVersion`, `PDUpgradeTasksRetryCount`, `PDMigratedAvailableWhileLocked`, `PDAvailableWhileLockedPreviousSetting`, `PDSanitizedAvailableWhileUnlocked`, `PassesDirectoryFileProtectionFixed`, `PDSpotlightIndexNeedsIndexing`, `PDPaymentSetupFeaturesAreDirtyKey`, `PDDiscoveryVisitorID`, `PDDiscoveryVisitorIDCreationInterval`, `PDDiscoverySwipedCountDict`(`paymentWelcomeCard`), `PDTransitNotificationServiceSentNotifications`(`MarketGeoDCINotifications`), `AppTimeInterval`, `CKStartupTime`, `CKPerBootTasks`, `CC_OncePerBootBackingData` |
| `com.apple.Wallet.plist` | `PKDismissedEventIdentifiers`(목록), `PKLastProductCacheUpdateTimestampKey`(정수), `whatsnew.availableFeatures`(목록) |
| `com.apple.seserviced.contactlessCredential.settings.plist` | `defaultAppIdentifier`, `defaultAppLocalizedName`, `defaultAppCandidates`, `doubleClickEnabled`, `shouldShowContactlessPane`, `shouldShowContactlessTcc`, `shouldShowSecureElementTcc`, `shouldShowSECPane`, `version`, `domain` 등 |
| `com.apple.stockholm.wallet.presentation.plist` | `walletDoubleButtonPressedConsumerAvailable` |

`com.apple.seserviced.contactlessCredential.settings.plist` 는 키 이름으로 보아 기본 비접촉 결제 앱 설정으로 보입니다.

## 증거로서 의미

**증명하는 것**

- 거래 표에 적힌 시각·가맹점·금액·통화로 거래 기록이 이 기기에 저장되어 있다는 사실[1]
- 거래 행에 위치 칸이 채워져 있으면, 그 위치 값이 거래 기록과 함께 저장되었다는 사실[1]
- 특정 패스(탑승권·입장권 등)가 기기에 들어와 있었다는 사실과, `INGESTED_DATE` 가 있으면 받아 들인 시각[2]

**증명하지 못하는 것**

- 결제에 쓴 실제 카드 번호. Apple 은 Apple Pay 에 쓴 원래 카드 번호를 저장하지 않고, 은행이 만든 기기 계정 번호(Device Account Number)는 Secure Element 칩에 들어가서 Apple 이 복호화할 수 없으며 Apple 서버에도 iCloud 백업에도 들어가지 않습니다[3].
- 결제한 사람이 기기 주인이라는 사실. 기록은 기기가 결제했다는 것까지만 말합니다.
- 거래 표에 없는 결제가 없었다는 사실. 앞 절처럼 버전·국가에 따라 기록이 남지 않을 수 있습니다[1].

보고서에는 "피의자가 이 가맹점에서 샀다" 가 아니라 "이 기기의 지갑 거래 기록에 이 시각, 이 가맹점 이름, 이 금액의 거래가 있다" 처럼 씁니다.

## 시각 해석

`payment_transaction.transaction_date`, `location_date`, `PASS.INGESTED_DATE` 는 Mac 절대 시각(2001-01-01 00:00:00 UTC 부터 센 초)이고 iLEAPP 도 이 기준으로 바꿉니다[1][2]. 값은 UTC 기준이라서 현지 시각으로 옮길 때는 기기 시간대와 거래 위치를 함께 봅니다. `transaction_date` 는 거래 시각이고 `location_date` 는 위치를 잰 시각이라 두 값이 다를 수 있으며, 위치 기반 주장을 할 때는 `location_date` 를 씁니다. 바꾸는 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md)에 있습니다.

`com.apple.Wallet.plist` 의 `PKLastProductCacheUpdateTimestampKey` 는 정수로 저장되며, 어떤 기준의 시각인지는 공개 자료가 없어 검체에서 확인합니다.

## 함정과 한계

**Apple 쪽 기록에도 기대하기 어렵습니다.** Apple 은 매장 결제에서 개인을 알아볼 수 있는 거래 정보를 보관하지 않고, 앱·웹 결제는 대략의 금액, 개발자와 앱 이름, 대략의 시각, 성공 여부만 익명으로 보관합니다[3]. Apple Cash 의 계정 정보·잔액·금액·주고받은 상대는 Apple Payments Inc. 가 따로 보관합니다[3]. 실제 결제 내역은 카드 발급사나 결제 사업자에서 받는 자료와 맞춰 봐야 하고, 계정 쪽 자료 요청은 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md)에서 다룹니다.

**다른 기기의 거래가 섞일 수 있습니다.** iCloud 는 패스와 거래 정보 같은 지갑 데이터를 암호화해서 전송하고 저장합니다[3]. 그래서 같은 계정의 다른 기기에서 생긴 거래가 이 기기에 동기화되어 들어올 가능성이 있습니다.

**금액 나눗수는 검증된 규칙이 아닙니다.** `amount` 를 10000 으로 나누는 규칙은 경험으로 얻은 값이라[1], 보고서에 금액을 적기 전에 영수증이나 카드사 자료로 알려진 거래 하나를 맞춰 봅니다.

**지우기.** `PASS.DELETE_PENDING` 칸은 이름으로 보아 지우기를 기다리는 패스를 표시하는 것으로 보이며[2], 사용자가 패스를 지운 뒤 어떤 흔적이 얼마나 남는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. SQLite 에서 지운 행을 찾는 방법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)를 봅니다.

## 직접 분석해 보기

### 금액과 시각 한 번 손으로 바꾸기

아래는 명세로 만든 예시이고, 실제 검체의 값이 아닙니다. 거래 행에 `amount` 가 `45000000`, `currency_code` 가 `KRW`, `transaction_date` 가 `700000000` 이라고 하면, iLEAPP 방식으로 금액은 45000000 ÷ 10000 = 4,500원이고, 시각은 2001-01-01 00:00:00 UTC 에 700,000,000초를 더한 2023-03-08 20:26:40 UTC, 한국 시간으로 2023-03-09 05:26:40 입니다.

```sql
SELECT datetime(transaction_date + 978307200, 'unixepoch') AS tx_utc,
       merchant_name, locality, administrative_area,
       amount / 10000.0 AS amount_ileapp, currency_code,
       datetime(location_date + 978307200, 'unixepoch') AS loc_utc,
       location_latitude, location_longitude,
       transaction_status, transaction_type
FROM payment_transaction
ORDER BY transaction_date;
```

`978307200` 은 1970-01-01 과 2001-01-01 사이의 초이고, 이 값을 더하면 SQLite 의 `unixepoch` 변환을 쓸 수 있습니다.

### 공개 도구

iLEAPP 의 지갑 거래 모듈은 `payment_transaction` 을 읽어 금액을 10000 으로 나누고 시각을 UTC 로 바꿔 보여 주고[1], 패스 모듈은 `pass.json` 과 `nanopasses.sqlite3` 를 풀어 보여 줍니다[2]. 도구 결과 몇 행을 위 SQL 결과와 맞춰 보고, 어긋나면 원본 표를 기준으로 삼습니다. 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 내용 |
|---|---|
| [중요 위치](../location/significant-locations.md)·[위치 기록 데몬](../location/routined.md) | 거래 위치 무렵에 기기가 그 근처에 있었는지 |
| [알림 기록](../app-usage/notifications.md) | 결제 직후 결제 알림이 왔는지 |
| [메시지](../communications/messages/index.md) | 카드사 결제 문자와 거래 시각·금액이 맞는지 |
| [애플 워치 연결](apple-watch.md) | 워치로 결제했을 가능성과 워치 쪽 패스 |
| [KnowledgeC](../app-usage/knowledgec/index.md)·[바이옴](../app-usage/biome/index.md) | 같은 시각에 지갑 앱을 열었는지 |

여러 기록을 한 줄로 놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md)을, 위치를 따지는 흐름은 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md)를 봅니다.

## 실습

공개 검체(NIST CFReDS 등)에서 아이폰 이미지를 구해 아래 질문을 풀어 봅니다. 거래 기록은 버전과 국가에 따라 없을 수 있으므로, 없으면 없다는 사실과 검체의 iOS 버전을 함께 적습니다.

1. 검체에서 `passes23.sqlite` 를 찾고, `payment_transaction` 표에 행이 몇 개 있는지 셉니다.
2. 거래 하나를 골라 `transaction_date` 와 `location_date` 를 각각 UTC 로 바꾸고 둘의 차이를 적습니다.
3. 위치 칸이 채워진 거래가 있으면 중요 위치 기록과 같은 무렵 같은 지역인지 맞춰 봅니다.
4. `pass.json` 을 하나 열어 발급 기관과 패스 종류를 확인하고, iLEAPP 결과와 같은지 봅니다.
5. `com.apple.passd.plist` 의 `PDLastLogDate` 를 읽고, 다른 기록과 비교해 무엇이 바뀔 때 이 값이 바뀌는지 가설을 세워 봅니다.

## 참고 문헌

1. iLEAPP, `scripts/artifacts/appleWalletTransactions.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/appleWalletTransactions.py
2. iLEAPP, `scripts/artifacts/appleWalletPasses.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/appleWalletPasses.py
3. Apple Support, "Apple Pay security and privacy overview" — https://support.apple.com/en-us/101554
