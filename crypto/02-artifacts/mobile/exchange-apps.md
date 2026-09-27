---
title: "거래소 앱"
parent: "아티팩트 · 모바일 지갑과 거래소 앱"
nav_order: 220
---

# 거래소 앱 (Exchange Apps)

거래소 앱은 수탁형 거래소 계정에 로그인해 쓰는 앱이라, 키와 거래 원장은 거래소 서버에 있고 기기에는 계정 식별자·앱 캐시·앱 설정이 남습니다. 이 페이지는 공개 분석기가 있는 Coinbase iOS 앱의 저장소를 예로, 기기에 남는 값과 그 값으로 확인되는 범위, 그리고 거래소 회신 자료와 맞춰 보는 방법을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

전용 지갑 앱은 기기에 키를 두고 주소와 트랜잭션을 직접 다루지만, 거래소 앱은 거래소 서버에 있는 계정을 보여 주는 창에 가깝습니다. 그래서 분석할 때 전용 지갑 앱과 거래소 앱을 먼저 구분해야 합니다[4]. 수탁형과 비수탁형의 차이는 [지갑의 종류](../../01-foundations/wallets/wallet-types.md)에 있습니다.

거래소 앱은 이용자에게 이메일·전화번호·이름을 받고, 때로는 개인 서류 사본까지 받습니다[4]. Android 에서 Coinomi·Atomic·Coinbase 세 앱을 비교한 시험에서는 Coinbase 만 이메일과 전화번호를 요구했습니다[4]. 이렇게 받은 고객 확인(KYC, Know Your Customer) 정보는 거래소가 보관합니다[4]. 기기의 앱 저장소에는 오프라인 GraphQL 캐시와 로그인 상태 키, 푸시 알림 설정 같은 값이 남습니다[1].

같은 이유로 거래소 앱 데이터에서는 블록체인 주소나 트랜잭션 해시가 잘 보이지 않습니다. 같은 시험에서 Coinomi 는 받은 거래의 해시를 캐시 폴더에 파일 이름으로 남겼지만, Coinbase Android 앱(1.22.3)은 파일 시스템에 그런 흔적을 남기지 않았습니다[4]. 앱 밖에서는 거래 알림 메일이 남습니다. Coinbase 는 `no-reply@coinbase.com` 에서 알림 메일을 보내고, 제목에 받은 금액이나 보낸 금액과 받는 주소가 들어 있습니다[4].

## 위치와 버전별 차이

| 앱 | 플랫폼 | 위치 | 공개 분석기 |
|---|---|---|---|
| Coinbase (거래소 앱) | iOS | 앱 데이터 컨테이너 아래 `Documents/mmkv/CB_RRN_MMKV_STORAGE` | iLEAPP `coinbase.py`[1] |
| Coinbase (거래소 앱) | Android | 공개된 저장 경로 없음. Android 8.0·앱 1.22.3 시험에서 파일 시스템에 트랜잭션 ID 흔적이 없었고 쿠키는 6개[4] | 없음 |
| 국내 거래소 앱(업비트·빗썸 등) | Android·iOS | 공개된 저장 구조 없음 | 없음 |

Coinbase iOS 앱은 React Native 로 만든 앱이고, 상태를 MMKV 저장소에 둡니다[1]. iLEAPP 경로 패턴은 `*/Documents/mmkv/CB_RRN_MMKV_STORAGE` 입니다[1]. 앱 데이터 컨테이너의 UUID 폴더가 어느 앱 것인지는 [설치된 앱 (Installed Apps·applicationState.db)](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/app-usage/installed-apps.html)에서 확인합니다.

이 분석기의 필드 대응은 비공개 샘플 하나로 맞췄고 공개 시험 데이터가 없습니다[1]. 분석기에는 어느 앱 버전·iOS 버전에서 확인한 구조인지가 적혀 있지 않습니다. 다른 버전의 앱이라면 아래 키 이름이 그대로인지 파일에서 먼저 확인합니다.

Coinbase 에는 앱이 둘 있습니다. 자기 보관 지갑 앱 Coinbase Wallet(번들 ID `org.toshi.distribution`, 지금 이름 Base App)은 거래소 앱과 저장소가 다르고, iLEAPP 도 두 앱을 다른 분석기로 읽습니다[6][10]. 지갑 앱 쪽은 [iOS 지갑 앱](ios-wallets.md)에서 다룹니다.

공개 분석기가 없는 앱은 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/app-data-layout.html)를 따라 앱 폴더를 찾은 뒤, 거래소 회신에 나온 계정 식별자·입금 주소·출금 해시를 문자열로 검색합니다. 검색 방법은 [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md)와 [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md)에 있습니다.

## 구조

### MMKV 최상위 키

`CB_RRN_MMKV_STORAGE` 는 키와 값이 이어 붙은 MMKV 파일입니다. 파일 형식은 [iOS 지갑 앱](ios-wallets.md)에서 설명하고, 여기서는 키만 봅니다. iLEAPP 가 읽는 최상위 키는 아래와 같습니다[1].

| 키 | 값 | 알 수 있는 것 |
|---|---|---|
| `@walletlink.user_id` | 문자열 | 앱이 기록한 계정 식별자 |
| `@OAUTH.IS_EXPECTED_TO_BE_LOGGED_IN` | 저장된 값 그대로 | 키 이름은 로그인 상태를 가리키지만 뜻은 밝혀지지 않았음 |
| `@UserVersion.version` | 문자열 | 저장소에 기록된 앱 버전 |
| `@notifications.push_permissions_set_status` | 문자열 | 푸시 알림 권한 설정 상태 |
| `@NotificationRegistrar.PushTokenCache` | JSON, 안에 `token` 필드 | 푸시 등록 토큰 |
| `@cds_preferences.appearance` | 문자열 | 화면 모양 설정 |
| `@GraphqlOfflineCache.store` | JSON | 오프라인 GraphQL 캐시(아래) |

문자열 값은 따옴표까지 저장되어 있어서, iLEAPP 는 앞뒤 따옴표를 떼고 보여 줍니다[1].

### 오프라인 GraphQL 캐시

`@GraphqlOfflineCache.store` 값은 Apollo GraphQL 클라이언트가 정규화해 저장한 캐시이고, 레코드는 `recordMap` 아래에 있습니다[1]. 레코드마다 `__typename` 이 있고, 다른 레코드를 가리킬 때는 `{"__ref": "레코드 키"}` 모양의 참조를 씁니다[1].

지갑 하나는 `__typename` 이 `Account` 인 레코드입니다. 필드는 아래와 같습니다[1].

| 필드 | 내용 |
|---|---|
| `id` | 계정 식별자, base64 로 인코딩되어 있어 디코딩해서 읽음 |
| `uuid`, `type`, `primary`, `isSanctioned`, `platform` | 저장된 값 그대로 |
| `totalBalance`, `availableBalance` | 지갑 통화 기준 잔액. 금액 레코드를 가리키는 참조 |
| `totalBalanceInNativeCurrency` | 같은 잔액을 계정의 표시 통화로 바꾼 값. 금액 레코드 참조 |

참조를 따라간 금액 레코드에는 `value` 와 `currency` 가 있습니다[1]. 아래는 이 구조를 따라 만든 예시입니다(만든 예시, 레코드 키와 값은 지어낸 것).

```json
{
  "recordMap": {
    "Account:QUJDMTIz": {
      "__typename": "Account",
      "id": "QUJDMTIz",
      "type": "WALLET",
      "primary": true,
      "totalBalance": {"__ref": "Amount:1"},
      "availableBalance": {"__ref": "Amount:2"}
    },
    "Amount:1": {"value": "0", "currency": "BTC"},
    "Amount:2": {"value": "0", "currency": "BTC"}
  }
}
```

캐시에는 앱이 보여 줄 수 있는 통화마다 `Account` 레코드가 들어 있습니다[1]. 그래서 iLEAPP 는 `totalBalance` 참조가 `value` 가 있는 금액 레코드로 풀리는 것만 이 계정의 지갑으로 봅니다[1]. 시험 기기에서는 `Account` 레코드 429개 가운데 5개만 잔액으로 풀렸고, 나머지 레코드가 무엇인지는 밝혀지지 않았습니다[1]. 이 5개는 모두 잔액이 0 이었는데, 값을 못 읽은 것이 아니라 지갑이 있었고 비어 있었다는 기록입니다[1].

iLEAPP 가 읽는 필드에는 블록체인 주소와 트랜잭션 해시가 없습니다[1]. 캐시의 다른 레코드에 그런 값이 있는지는 `recordMap` 전체를 주소·해시 모양 문자열로 검색해 확인합니다.

## 증거로서 의미

**증명하는 것**

- 앱 저장소에 `@walletlink.user_id` 와 잔액이 풀리는 `Account` 레코드가 있으면, 이 기기에 그 계정으로 쓰던 거래소 앱 데이터가 있었습니다[1]. 계정 식별자는 거래소 회신 자료의 계정과 맞춰 보는 데 씁니다.
- 풀리는 `Account` 레코드의 통화와 잔액은 캐시가 저장될 때 그 계정에 그 통화 지갑이 있었고 잔액이 얼마였는지를 보여 줍니다[1].
- `@UserVersion.version` 은 저장소에 기록된 앱 버전이라, 거래소 회신의 기기 기록(`Platform_version`, `User_agent` 등)과 비교할 수 있습니다[1][8].
- 거래 알림 메일 제목의 금액과 주소는 그 계정이 받거나 보낸 거래를 가리킵니다[4].

**증명하지 못하는 것**

- 기기에 개인 키가 없으므로, 거래소 앱 데이터만으로는 이 사람이 어떤 온체인 주소를 통제했는지 알 수 없습니다. 거래소가 거래에 쓰는 주소는 여러 고객이 함께 씁니다. 한 시험에서 Coinbase 에서 기기 지갑으로 보낸 거래의 보내는 쪽 주소 하나는 2021년 7월 기준 1,361번 거래하고 1억 달러 넘게 주고받은 주소였습니다[4]. 블록 탐색기에서 이 주소를 봐도 사람은 특정되지 않습니다.
- `Account` 레코드 수는 보유 지갑 수가 아닙니다. 시험 기기에서는 429개 중 5개만 잔액으로 풀렸습니다[1].
- 캐시 잔액은 캐시를 저장한 때의 값이고 지금 잔액이 아닙니다.
- 로그인 상태 키(`@OAUTH.IS_EXPECTED_TO_BE_LOGGED_IN`)의 값으로 "지금 로그인되어 있었다" 고 단정하지 않습니다. 키 이름 이상의 뜻이 밝혀지지 않았습니다[1].
- 쿠키로는 사람을 특정하지 못합니다. 시험에서 Coinbase Android 앱의 쿠키 6개는 Cloudflare `__cf_bm`(봇 관리) 등이었고, 사람이 읽을 수 있는 귀속 정보 없이 생성·만료 시각 정도만 알 수 있었습니다[4].

보고서에는 "이 기기의 Coinbase 앱 저장소에 계정 식별자 X 와 BTC 지갑 레코드가 있고, 거래소 회신의 같은 계정 기록에 이 주소로 보낸 출금이 있다" 처럼 두 기록으로 확인되는 만큼만 씁니다. 계정과 사람을 잇는 KYC·IP·기기 기록은 거래소 회신에서 나옵니다([거래소가 제공하는 자료](../records/exchange-records.md)).

## 시각 해석

iLEAPP 가 읽는 `Account` 레코드와 최상위 키에는 시각 필드가 없습니다[1]. 캐시가 언제 저장됐는지는 파일 시스템 시각과 MMKV 안의 기록 순서로 판단합니다. MMKV 는 값을 바꿀 때 기존 항목을 고치지 않고 뒤에 새 항목을 붙이므로, 같은 키가 여러 번 있으면 뒤에 있는 것이 나중 값입니다[2]. 다만 항목에 시각이 붙지 않아서 순서만 알 수 있고 절대 시각은 알 수 없습니다.

거래 시각은 기기보다 거래소 회신과 블록체인에서 찾습니다. 거래소 회신 시각은 거래소 서버가 요청이나 처리 시점에 남긴 값이고, 블록 시각과 다릅니다([블록 시각과 확정](../../01-foundations/blockchain/block-time.md)). Coinbase 회신 자료 `coinbase_data.json` 의 사용 기기 목록(Devices Used)에는 `Timezone_string`·`Timezone_locale` 열이 따로 있어서[8], 기기의 시간대 설정과 회신에 남은 시간대를 맞춰 볼 수 있습니다. 회신 시각 표기와 UTC 변환은 [거래소가 제공하는 자료](../records/exchange-records.md)에서 다룹니다.

Android 앱 시험에서 쿠키 시각은 UTC+0 으로 표기됐습니다[4]. 도구 화면의 시각이 UTC 인지 기기 현지 시각인지는 도구 설정에서 먼저 확인합니다.

## 함정과 한계

- **같은 회사의 다른 앱.** Coinbase 거래소 앱과 Coinbase Wallet(Base App)은 저장소가 다르고 증거로서 의미도 다릅니다[10]. 거래소 앱은 수탁형 계정, 지갑 앱은 기기에 키가 있는 자기 보관 지갑입니다.
- **같은 상표의 다른 법인.** Binance.US(BAM Trading Services)와 Binance(Binance Holdings)는 별개 회사이고, Binance.US Web3 Wallet 기록은 BAM Technology Services Inc. 앞으로 따로 요청합니다[7]. 앱 이름만 보고 요청 대상을 정하지 않고, 앱 폴더 이름과 번들 ID 로 어느 앱인지 확인합니다.
- **캐시 레코드를 전부 지갑으로 세기.** 잔액 참조가 풀리지 않는 `Account` 레코드까지 세면 지갑 수가 수백 개로 부풀어 보입니다[1].
- **도구가 최신 값만 보여 줌.** iLEAPP 는 MMKV 에서 키마다 마지막 값만 읽습니다[1][2]. 같은 파일에 예전 `@GraphqlOfflineCache.store` 값이 남아 있을 수 있으므로, 예전 잔액이나 지갑 목록이 필요하면 모든 항목을 파일 순서대로 읽습니다[2]. 기록 크기 뒤 여유 공간에서 추출한 예전 항목은 추정이라 틀린 행이 섞일 수 있습니다[3].
- **거래소 주소를 사용자 주소로 오인.** 거래소에서 나간 거래의 보내는 주소는 거래소가 여러 고객을 위해 쓰는 주소일 수 있습니다[4].
- **공개 시험 데이터 없음.** Coinbase 분석기는 비공개 샘플 하나로 필드를 맞췄습니다[1]. 앱 버전이 다르면 키나 레코드 구조가 다를 수 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** MMKV 파일은 앞 4바이트가 데이터 영역 크기(little-endian)이고, 그 뒤에 항목 전체 크기 varint, 키 길이 varint, 키, 값 길이 varint, 값이 이어집니다[2]. 문자열 값은 값 안에서 다시 길이 varint 와 바이트로 저장됩니다[2]. 아래는 이 형식으로 만든 예시이고, 앱 버전 키 하나만 들어 있습니다(만든 예시).

```text
00000000  1F 00 00 00 1E 14 40 55 73 65 72 56 65 72 73 69   ......@UserVersi
00000010  6F 6E 2E 76 65 72 73 69 6F 6E 08 07 22 39 2E 39   on.version.."9.9
00000020  2E 39 22 00 00 00 00 00 00 00 00 00               .9".........
```

`1F 00 00 00` 은 데이터 영역이 31바이트라는 뜻이고, `1E` 는 그 뒤 항목들이 30바이트라는 뜻입니다. `14` 는 키 길이 20바이트이고, 이어서 `@UserVersion.version` 이 나옵니다. `08` 은 값 길이 8바이트, 그 안의 `07` 은 문자열 길이 7바이트이고, 문자열은 따옴표까지 포함한 `"9.9.9"` 입니다. 실제 파일에서도 같은 순서로 `@walletlink.user_id` 나 `@GraphqlOfflineCache.store` 를 찾아갈 수 있습니다.

**공개 도구로 한 번.** 전체 파일 시스템 추출물에 iLEAPP 를 돌리면 "Coinbase - Account and Device" 와 "Coinbase - Wallets and Balances" 두 결과가 나옵니다[1]. 앞의 결과에는 계정 식별자·앱 버전·푸시 토큰·보유 지갑 수가, 뒤의 결과에는 풀리는 지갑마다 통화와 잔액이 나옵니다[1]. 두 결과의 지갑 수는 같은 캐시에서 세므로 늘 일치합니다[1]. 예전 항목까지 보려면 iLEAPP 의 "MMKV - Recovered Records" 결과를 함께 봅니다[3].

## 교차 검증

- 앱의 계정 식별자·지갑 통화를 거래소 회신의 계정·입금 주소 섹션과 맞춥니다([거래소가 제공하는 자료](../records/exchange-records.md), [거래소 자료 분석](../../03-techniques/analysis/exchange-analysis.md)).
- 앱 버전·OS·시간대를 거래소 회신의 기기 기록과 비교합니다. Coinbase 회신 자료 가운데 `coinbase_data.json` 의 사용 기기 목록에는 `Platform`, `Platform_version`, `Timezone_string`, `User_agent` 등이 있고[8], `compliance_report` CSV 의 `EVENTS` 섹션에는 `IP`, `FINGERPRINT`, `USER AGENT`, `LOCATION` 이 있습니다[9]. 업비트는 서비스를 쓰는 동안 기기정보(OS, 모델명, 통신사, 회사가 부여한 기기관리번호, 언어정보, ADID, IDFA, IDFV)와 IP 주소를 모으고[5], Binance.US 가 제공할 수 있는 기록에는 기기 내역과 IP 내역이 있습니다[7].
- 업비트는 금융사고를 막으려고 휴대폰에 설치된 원격제어앱·악성앱 탐지 정보를 모읍니다[5]. 원격 조종이 의심되는 사건이면 이 기록을 요청할 수 있습니다. 생체인증(지문·얼굴)은 기기에 등록된 정보와 대조한 결과만 쓰고 서버로 보내지 않으므로[5], 거래소 쪽에는 생체 정보 자체가 없습니다.
- 거래 알림 메일과 푸시 알림을 봅니다. 알림 기록은 [Android 알림 기록](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/app-usage/notification-history.html), [iOS 알림 기록](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/app-usage/notifications.html)에서 다룹니다.
- 알림 메일이나 회신에 나온 해시·주소를 블록체인에서 조회해 금액과 블록 시각을 맞춥니다([블록 탐색기 기록 읽기](../records/block-explorers.md)).
- 같은 기기의 지갑 앱에 거래소로 보낸 거래가 있으면 해시로 이어 붙입니다([Android 지갑 앱](android-wallets.md), [iOS 지갑 앱](ios-wallets.md), [거래소로 들어갔나](../../04-scenarios/asset-flow/exchange-deposit.md)).
- 기기 시각, 거래소 시각, 블록 시각을 한 표에 합칩니다([암호화폐 타임라인](../../03-techniques/analysis/timeline.md)).

## 실습

1. 위 헥스 예시를 파일로 만들고 iLEAPP 의 `scripts/mmkv_parser.py` 로 읽어, 키와 값이 헥스로 따라간 결과와 같은지 확인합니다. 같은 키를 값만 바꿔 한 번 더 붙였을 때 도구가 어느 값을 보여 주는지도 확인합니다.
2. 구조 절의 JSON 예시에 `totalBalance` 참조가 없는 `Account` 레코드를 몇 개 더 넣고, iLEAPP 와 같은 기준(잔액 참조가 `value` 로 풀리는가)으로 지갑 수를 세어 봅니다.
3. 테스트넷을 지원하는 지갑 앱에서 거래를 한 번 보낸 뒤 기기 추출물의 거래소 앱·지갑 앱 폴더를 해시 문자열로 검색하고, 블록 탐색기의 블록 시각과 기기 파일 시각의 차이를 표로 정리합니다.
4. 거래 알림 메일 제목에 금액과 주소만 있을 때, 보고서에 "보냈다" 를 누구 기준으로 어떻게 쓸지 한 문장으로 적어 봅니다.

## 참고 문헌

1. iLEAPP, `scripts/artifacts/coinbase.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbase.py
2. iLEAPP, `scripts/mmkv_parser.py`(원본 https://github.com/abrignoni/mmkv-parser 커밋 05deada3d8f93000c85f4bc399b6c6f463c13e68). https://github.com/abrignoni/iLEAPP/blob/main/scripts/mmkv_parser.py
3. iLEAPP, `scripts/artifacts/mmkvCarved.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/mmkvCarved.py
4. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, "Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications", arXiv, 2022. doi:10.48550/arXiv.2205.14611. https://arxiv.org/abs/2205.14611
5. 두나무, 업비트 개인정보 처리방침. https://static.upbit.com/terms/private_data.html
6. Coinbase, Privacy Policy. https://www.coinbase.com/legal/privacy
7. Binance.US, Law Enforcement Guide. https://support.binance.us/en/articles/9842980-binance-us-law-enforcement-guide
8. RLEAPP, `scripts/artifacts/coinbaseArchive.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseArchive.py
9. RLEAPP, `scripts/artifacts/coinbaseComplianceReport.py`. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseComplianceReport.py
10. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
