---
title: "투자 사기의 흔적"
parent: "시나리오 · 사기"
nav_order: 390
---

# 투자 사기의 흔적 (Investment Scam)

암호화폐 투자 사기는 SNS·데이팅 앱·문자로 접근한 사람이 대화를 메신저로 옮기고, 피해자가 가짜 투자 사이트나 앱에 암호화폐를 보내게 한 뒤 출금을 막는 순서로 흘러갑니다. 이 페이지는 피해자 기기의 대화·방문·설치 흔적에서 안내받은 사이트와 주소를 뽑고, 지갑 앱과 거래소 기록에서 실제로 보낸 주소와 트랜잭션 ID(TXID)를 찾아 블록체인 기록과 맞추는 순서를 다룹니다. 누가 권유했는지는 대화 기록으로, 얼마가 어디로 나갔는지는 거래소 기록과 블록체인으로 확인하므로 두 가지를 따로 판단합니다.

## 조사 질문

- 피해자는 누구의 권유로, 어떤 사이트나 앱에 가입했는가.
- 피해자는 어느 주소로, 언제, 얼마를 보냈는가.
- 보낸 자산은 그 뒤 어디로 갔는가.
- 피해자 기기의 기록, 거래소 기록, 블록체인 기록이 서로 맞는가.

## 사기가 흘러가는 순서

미국 FBI 인터넷범죄신고센터(IC3)에 2025년 접수된 암호화폐 투자 사기는 61,559건, 피해액 72.28억 달러로, 2024년보다 신고 건수가 48%, 피해액이 25% 늘었습니다[1]. 2024년은 41,557건, 58억 달러였습니다[2]. 2025년 연령대별로는 60세 이상이 13,685건, 27.64억 달러로 가장 많았습니다[1]. 이 숫자는 신고된 사건만 센 것이라 신고하지 않은 피해는 들어 있지 않습니다.

미국 기관과 금융감독원이 알리는 수법은 흐름이 같습니다. 사기범은 문자, SNS, 광고, 데이팅 앱으로 처음 접근하고 곧 대화를 메신저로 옮깁니다[1][3]. 업계 전문가를 자처하는 "투자 그룹"을 소개하고 가짜 투자 플랫폼이나 앱에 암호화폐를 보내게 한 뒤, 가짜 수익을 보여 주고 대출까지 권해 투자금을 늘리게 합니다[1]. 이 수법을 "pig butchering" 이라고도 부릅니다[2]. 국내에서는 투자방 참여형(코인 리딩방), 온라인 친분 이용형(로맨스 스캠), 유명 거래소 사칭형으로 나뉘고, 사기범은 SNS·채팅방에서 특정 거래 사이트나 앱을 설치하게 하거나 위조한 해외 유명 거래소를 소개합니다[4]. "교수"를 자처하며 약 4개월 동안 무료 재테크 강의를 하고 출석만으로 현금이나 가짜 코인을 준 뒤, 텔레그램 등으로 가짜 거래소 홈페이지 가입을 유도한 사례도 있습니다. 이때 가짜 증명서와 허위 인터넷 기사까지 씁니다[6]. "AI 차익거래로 매일 1.8~4.6% 수익을 코인으로 준다" 며 업체 웹사이트·앱으로 코인을 예치받고 다단계로 사람을 모으는 방식도 있습니다[7].

돈을 빼앗는 단계도 비슷합니다. 처음에는 소액으로 수익을 경험하게 하고, 거액이 들어온 뒤에는 출금을 거절합니다[4]. 출금하려고 하면 세금이나 수수료를 내라고 한 뒤 사라지거나[1], 높은 수수료를 내야만 출금된다고 합니다[3]. 피해자는 이어서 잃은 돈을 찾아 준다는 회수 사기(recovery scam)의 표적이 됩니다[1]. 2025년 IC3 의 회수 사기 신고는 10,516건, 14억 달러이고, 이 피해액에는 회수 업체에 연락하게 된 앞선 사기의 피해가 섞여 있을 수 있습니다[1]. 국내에서도 리딩방 피해를 보상해 준다며 "피해보상 대상자"에게만 코인을 싸게 판다고 속이는 사례가 있습니다[5].

이 흐름 가운데 블록체인에는 피해자가 실제로 보낸 트랜잭션만 남습니다. 가짜 플랫폼이 보여 주는 잔액과 수익은 그 사이트 운영자가 화면에 띄운 숫자라서 블록체인 기록으로 확인되지 않습니다. 블록체인에는 금액, 보낸 주소, 받은 주소가 공개 기록으로 남고, 암호화폐 지급은 보통 되돌릴 수 없습니다[3].

## 먼저 확인할 것

피해자 진술로 사건 기간, 사용한 기기, 거래소 계정, 지갑 앱, 안내받은 사이트와 주소를 표로 정리합니다. 기기마다 OS 버전과 시간대를 기록해 둡니다. 대화·방문·설치 시각은 기기 시계를 따르고 송금은 블록 시각으로 남아서 둘을 같은 기준으로 맞춰야 합니다.

수집 범위는 지갑 앱에 맞춰 정합니다. iPhone 의 MetaMask Mobile 은 상태 파일에 백업 제외 표시를 붙여서 백업으로 만든 논리 추출에는 들어가지 않을 수 있습니다. 자세한 내용은 [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md)에 있습니다.

피해자가 안내받은 거래소가 신고된 사업자인지 확인합니다. 가상자산사업자는 금융정보분석원장에게 신고해야 하고(특정금융정보법 제7조 제1항), 신고하지 않고 가상자산거래를 영업으로 하면 5년 이하 징역 또는 5천만원 이하 벌금에 처합니다(제17조 제1항)[9]. 금융정보분석원에 신고하지 않은 사업자는 가짜 거래소일 가능성이 높습니다[6]. 신고 사업자 목록은 금융정보분석원 누리집에서 확인하고, 대화에 나온 거래소 이름·도메인·앱 이름과 비교합니다. 제도 설명은 [거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md)에 있습니다.

자료를 요청할 기관과 회사도 이때 정리합니다. 금융감독원의 가상자산 불공정거래 및 투자사기 신고센터는 신고를 받지만, 불공정거래가 아닌 일반 투자사기는 금융감독원이 직접 조사하고 조치할 권한이 없어서 피해구제가 필요하면 검찰·경찰에 신고해야 합니다[8]. 해외 거래소는 회사 구분을 확인합니다. Binance.US 를 운영하는 BAM Trading 과 Binance Holdings 는 별개 회사라 BAM Trading 에는 Binance 의 기록이 없고, Binance.US 는 주소를 기준으로 요청할 때 TXID, UTC 시각, 금액을 함께 적으라고 요구합니다[12]. 피해자의 돈이 신고 사업자 사이에서 옮겨 갔다면 보내는 사업자가 100만원 상당 이상 이전에 송·수신인 정보를 넘기고 거래관계가 끝난 때부터 5년간 보존하므로[10], 그 정보도 함께 요청합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 메신저 대화·첨부·링크 | 누가 언제 접근했나, 안내한 사이트 주소·앱 이름·입금 주소 | [Android 카카오톡](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/messengers/kakaotalk/), [Android 텔레그램](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/messengers/telegram.html), [iOS 카카오톡](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/messengers/kakaotalk/), [iOS 텔레그램](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/messengers/telegram.html) |
| 2 | 스크린샷·알림 기록 | 피해자가 본 가짜 수익 화면, 입금 안내, 앱 알림 | [Android 스크린샷](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/media/screenshots.html), [iOS 스크린샷](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/media/screenshots.html), [Android 알림 기록](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/app-usage/notification-history.html), [iOS 알림 기록](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/app-usage/notifications.html) |
| 3 | 브라우저 방문 기록 | 가짜 거래소 홈페이지를 방문·가입한 시각 | [Android 크롬](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/browsers/chrome/), [iOS 사파리](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/browsers/safari/), [Windows 크롬 계열](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) |
| 4 | 설치된 앱 | 설치를 유도받은 거래 앱·전자지갑 | [iOS 설치된 앱](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/app-usage/installed-apps.html), [Android 앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/app-data-layout.html) |
| 5 | 지갑 앱 데이터 | 보낸 트랜잭션, 주소록, 앱 안 브라우저 기록 | [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md), [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md), [MetaMask](../../02-artifacts/browser/metamask/index.md) |
| 6 | 거래소 앱·거래소 회신 | 원화 입금, 코인 매수, 출금 주소와 TXID | [거래소 앱](../../02-artifacts/mobile/exchange-apps.md), [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md) |
| 7 | 블록체인 | 출금 트랜잭션의 블록 시각·금액·받는 주소, 그 뒤 흐름 | [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md), [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md), [비트코인 거래 따라가기](../../03-techniques/analysis/bitcoin-tracing.md) |

## 분석 흐름

1. **대화에서 안내받은 것을 목록으로 만듭니다.** 사기범 계정, 처음 접근한 시각, 대화가 메신저로 옮겨 간 시각, 안내한 사이트 도메인과 앱 이름, 입금하라고 준 주소, 요구한 금액을 뽑습니다. 주소는 대화 본문뿐 아니라 첨부 이미지, QR 코드, 스크린샷에도 있을 수 있습니다. 텍스트와 파일에서 주소 형식의 문자열을 찾는 방법은 [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md)에 있습니다.

2. **가짜 사이트와 앱을 쓴 흔적을 찾습니다.** 브라우저 기록에서 안내받은 도메인을 처음 방문한 시각과 가입·로그인 페이지 방문을 찾고, 설치된 앱 목록에서 안내받은 거래 앱을 찾습니다. 자체 개발했다는 전자지갑을 설치하게 하거나 메일로 전자지갑을 연결하게 한 뒤 가상자산을 빼낸 사례도 있습니다[8]. 사이트에 지갑을 연결하고 서명한 흔적은 [피싱 사이트에 서명했나](wallet-drainer.md)에서 다룹니다.

3. **돈이 나간 경로를 정합니다.** 경로는 크게 둘입니다. 피해자가 국내 거래소에서 원화로 코인을 사서 바로 사기범 주소로 출금했다면 거래소 기록에 출금 주소와 TXID 가 남습니다. 업비트는 디지털 자산의 거래일시, 수량, 종류, 원화 환산금액, 입출금기록, 입출금 지갑주소를 거래 정보로 모읍니다[11]. Coinbase 처럼 회신을 섹션 여러 개가 든 CSV 한 개로 주는 거래소도 있고, RLEAPP 는 이 파일(`compliance_report.csv`)에서 `TRANSACTIONS` 섹션, 제목이 자산 기호를 늘어놓고 `ADDRESSES` 로 끝나는 주소 섹션, `EVENTS` 섹션을 표로 읽습니다[14]. 피해자가 개인 지갑을 거쳐 보냈다면 지갑 앱에 보낸 트랜잭션이 남습니다. iPhone 의 MetaMask Mobile 에서 iLEAPP 는 `persistStore/persist-root` 의 `engine` → `backgroundState` 아래 `TransactionController.transactions` 에서 시각·보낸 주소·받는 주소·금액·해시를, `AddressBookController.addressBook` 에서 주소록 이름과 주소를, 최상위 `browser` 의 `history` 에서 앱 안 브라우저의 이름과 URL 을 읽습니다[13]. 주소록에 사기범 주소가 어떤 이름으로 저장됐는지, 앱 안 브라우저 기록에 가짜 거래소 도메인이 있는지 확인합니다. 앱 버전에 따른 파일 구조 차이는 [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md)에 있습니다.

4. **블록체인에서 송금을 확인합니다.** 거래소 기록이나 지갑 앱에서 얻은 TXID 로 트랜잭션을 조회합니다. 이더리움 계열에서 Etherscan 의 `txlist` 결과는 `timeStamp`(블록이 채굴된 시각, UNIX 초), `from`, `to`, `value`(wei 단위), `txreceipt_status`(1 성공, 0 실패)를 돌려줍니다[16]. 실패한 트랜잭션은 자산을 옮기지 않았으므로 피해액에서 뺍니다. ERC-20 토큰으로 보냈다면 `tokentx` 결과의 `contractAddress`, `tokenSymbol`, `tokenDecimal`, `value` 를 봅니다. `value` 를 10의 `tokenDecimal` 제곱으로 나누면 토큰 수량이 됩니다[17]. 토큰의 기본 구조는 [토큰과 NFT](../../01-foundations/blockchain/tokens.md)에 있습니다.

5. **받는 주소 뒤의 흐름을 따라갑니다.** 받는 주소에서 자산이 어디로 나갔는지는 [빼앗긴 자산은 어디로 갔나](../asset-flow/stolen-funds.md)의 순서로 따라가고, 거래소 입금 주소에 닿으면 [거래소로 들어갔나](../asset-flow/exchange-deposit.md)의 방법으로 그 거래소에 자료를 요청합니다.

6. **"보상"으로 받은 코인이 진짜 자산인지 확인합니다.** 출석 지원금이나 피해 보상 명목으로 받은 코인은 가짜일 수 있습니다[5][6]. ERC-20 에서는 토큰을 옮길 때 `Transfer` 이벤트를 반드시 내야 하지만[18], 사기 토큰 중에는 실제로 옮기지 않고 `Transfer` 이벤트만 내는 함수(wARB 의 `dropNewTokens`)를 둔 것이 있습니다[19]. 그래서 받은 토큰의 컨트랙트 주소를 발행 조직이 공개한 주소와 비교합니다. 정상적인 ERC-20 컨트랙트로 아무 가치 없는 토큰을 만들 수도 있어서 자동 탐지는 놓칠 수 있고, 믿을 만한 출처에서 컨트랙트 주소를 얻어 비교해야 합니다[19].

7. **회수 사기를 따로 나눕니다.** 첫 피해 뒤 "피해금을 찾아 준다"는 연락과 추가 송금이 있으면 시각, 연락한 계정, 받는 주소를 따로 정리합니다. 두 사건의 송금을 한 줄로 합치면 피해액과 받는 주소의 관계가 흐려집니다.

## 증명하는 것과 증명하지 못하는 것

거래소 기록이나 지갑 앱의 출금 주소·TXID 가 블록체인의 트랜잭션과 맞으면 "이 계정(또는 이 기기의 지갑)에서 이 주소로 이 블록 시각에 이 금액이 나갔다"는 것이 확인됩니다. 메신저와 브라우저 기록은 누가 어떤 사이트와 주소를 안내했는지를 뒷받침합니다.

받는 주소의 주인은 블록체인만으로 특정할 수 없습니다. 받는 주소가 거래소 입금 주소라면 그 거래소의 고객 기록이 있어야 계정 주인을 알 수 있습니다. 가짜 플랫폼이 보여 준 잔액과 수익은 블록체인에 없어서, 피해액은 피해자가 실제로 보낸 트랜잭션의 합으로 계산합니다. 속여서 투자하게 했다는 사실은 대화 기록으로만 뒷받침됩니다.

블록 탐색기 값을 증거로 쓸 때는 한계도 적습니다. 제3자가 운영하는 탐색기에 조회하면 어떤 주소를 조사하는지가 운영자에게 드러날 수 있고, 조사자가 응답 값의 무결성을 보장할 수 없습니다[20]. 보고서에 쓸 핵심 값은 직접 운영하는 노드로 한 번 더 확인합니다.

## 시각 맞추기

기록마다 시각의 기준이 다릅니다.

| 기록 | 시각 기준 | 주의할 점 |
|---|---|---|
| 메신저·브라우저·스크린샷 | 기기 시계 | 기기 시간대와 시계 오차를 확인합니다 |
| MetaMask 트랜잭션 `time` | 기기 시계, `Date.now()` 밀리초[15] | iLEAPP 는 UTC 로 바꿔 보여 줍니다[13]. 앱이 트랜잭션 항목을 만들 때 기록한 시각이라 블록에 들어간 시각과 다릅니다 |
| 거래소 회신 | 거래소 서버 시각 | 시간대가 적히지 않은 값이 있습니다([거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md)) |
| 블록체인 | 블록 시각, UNIX 초[16] | 성질은 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에 있습니다 |

모두 UTC 로 바꾼 뒤 "안내 메시지 → 사이트 방문 → 거래소 매수 → 출금 요청 → 블록 포함" 순서가 맞는지 봅니다. 순서가 어긋나면 시간대 변환이나 짝지은 트랜잭션이 틀렸을 가능성이 있습니다. 합치는 방법은 [암호화폐 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 흔한 오판

- **가짜 거래소 화면의 잔액을 피해자의 자산으로 적는다.** 그 숫자는 사이트가 보여 준 값이고 블록체인에 없습니다. 피해액은 실제로 보낸 트랜잭션으로 계산합니다.
- **보상 코인을 받은 기록이 있으니 진짜 수익을 받았다.** 가짜 토큰일 수 있고, `Transfer` 이벤트만으로 이동을 단정할 수 없습니다[19].
- **iLEAPP 결과가 비어 있으니 지갑 앱으로 보내지 않았다.** 출처끼리 키 이름이 다릅니다. iLEAPP 는 트랜잭션 항목의 `transaction` 키에서 주소와 금액을, `transactionHash` 키에서 해시를 읽는데[13], MetaMask core 의 현재 `TransactionMeta` 는 트랜잭션 인자를 `txParams` 에, 해시를 `hash` 에 둡니다[15]. 앱 버전에 따라 키 이름과 파일 구조가 다를 수 있으므로 원본 JSON 을 직접 봅니다.
- **받는 주소를 사기범 개인의 주소로 적는다.** 거래소 입금 주소라면 여러 사람이 쓰는 주소일 수 있습니다([거래소로 들어갔나](../asset-flow/exchange-deposit.md)).
- **첫 피해와 회수 사기 송금을 합쳐 계산한다.** 회수 사기 신고의 피해액에는 앞선 사기의 피해가 섞일 수 있습니다[1]. 사건별로 따로 정리합니다.
- **금융감독원에 신고했으니 수사가 시작됐다.** 일반 투자사기는 금융감독원이 직접 조사할 권한이 없어서 수사기관 신고가 따로 필요합니다[8].

## 보고서 문장 예

아래 시각·주소·금액·도메인은 모두 만든 예시입니다.

- "피해자 휴대폰의 텔레그램 대화에서 계정 A 가 2026-02-10 09:12 KST 에 도메인 `example-exchange.test` 가입을 안내하고, 2026-02-14 13:05 KST 에 이더리움 주소 B 로 입금하라고 보낸 메시지가 확인된다. (만든 예시)"
- "피해자의 국내 거래소 회신에는 2026-02-14 04:20:11 UTC 에 주소 B 로 1.5 ETH 를 출금한 기록과 TXID C 가 있고, 이더리움 블록체인에는 TXID C 가 블록 시각 2026-02-14 04:20:35 UTC 에 성공 상태로 들어 있다. (만든 예시)"
- "주소 B 의 주인은 블록체인 기록만으로 확인되지 않는다. 가짜 거래소 화면에 표시된 잔액 12 ETH 는 블록체인에서 확인되지 않는다. (만든 예시)"

보고서 전체 구성은 [암호화폐 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)에 있습니다.

## 함께 볼 페이지

- [피싱 사이트에 서명했나](wallet-drainer.md) — 가짜 사이트에 지갑을 연결하고 서명한 경우
- [빼앗긴 자산은 어디로 갔나](../asset-flow/stolen-funds.md), [거래소로 들어갔나](../asset-flow/exchange-deposit.md) — 받는 주소 뒤의 흐름
- [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md), [거래소 자료 분석](../../03-techniques/analysis/exchange-analysis.md) — 거래소 회신의 구조와 읽는 법
- [이 기기로 지갑을 썼나](../device-use/wallet-use.md) — 피해자 기기의 지갑 목록 만들기
- [피싱 링크를 눌렀나](https://urock-ailab.github.io/forensics-handbook/network/04-scenarios/user-activity/phishing-click.html) — 네트워크 기록에서 링크 접속 확인
- [AI로 피싱·사기 문구를 만들었나](https://urock-ailab.github.io/forensics-handbook/ai/04-scenarios/misuse/phishing.html) — 사기 문구를 만든 쪽의 흔적

## 참고 문헌

1. FBI, 2025 IC3 Annual Report. https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf
2. FBI, 2024 IC3 Annual Report. https://www.ic3.gov/AnnualReport/Reports/2024_IC3Report.pdf
3. FTC, What To Know About Cryptocurrency and Scams, 2022-05. https://consumer.ftc.gov/articles/what-know-about-cryptocurrency-and-scams
4. 금융감독원, 소비자경보 2024-12호 "내가 쓰는 코인 거래소는 안전할까?" 가짜 거래소를 이용한 가상자산 투자사기, 2024-03-26. https://www.fss.or.kr/fss/bbs/B0000175/view.do?nttId=134974&menuNo=200204
5. 금융감독원, 소비자경보 2024-16호 리딩방·로또 환불을 빙자한 코인 매수 제안을 조심하세요!, 2024-04-08. https://www.fss.or.kr/fss/bbs/B0000175/view.do?nttId=135253&menuNo=200204
6. 금융감독원, 소비자경보 2025-14호 무료 재테크 교육 및 출석 지원금 등으로 접근한 후 가짜 가상자산거래소로 유인하는 사기, 2025-06-02. https://www.fss.or.kr/fss/bbs/B0000175/view.do?nttId=194480&menuNo=200204
7. 금융감독원, 소비자경보 2025-6호 가상자산 차익거래 등으로 수익을 낸다며 투자를 유도하는 불법 가상자산사업자, 2025-03-11. https://www.fss.or.kr/fss/bbs/B0000175/view.do?nttId=191833&menuNo=200204
8. 금융감독원, 가상자산 불공정거래 및 투자사기 신고 이용안내. https://www.fss.or.kr/fss/main/contents.do?menuNo=201129
9. 특정 금융거래정보의 보고 및 이용 등에 관한 법률 제7조, 제17조. https://www.law.go.kr/법령/특정금융거래정보의보고및이용등에관한법률
10. 금융위원회, 보도자료 "3.25일 특정금융정보법상 트래블룰이 시행됩니다", 2022-03-24. https://www.fsc.go.kr/no010101/77579
11. 업비트, 개인정보처리방침. https://static.upbit.com/terms/private_data.html
12. Binance.US, Binance.US Law Enforcement Guide. https://support.binance.us/en/articles/9842980-binance-us-law-enforcement-guide
13. iLEAPP, scripts/artifacts/metamask.py. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
14. RLEAPP, scripts/artifacts/coinbaseComplianceReport.py. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseComplianceReport.py
15. MetaMask core, packages/transaction-controller/src/types.ts, TransactionController.ts. https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/types.ts
16. Etherscan, Get Normal Transactions By Address (txlist). https://docs.etherscan.io/api-reference/endpoint/txlist.md
17. Etherscan, Get ERC20 Token Transfer Events By Address (tokentx). https://docs.etherscan.io/api-reference/endpoint/tokentx.md
18. ERC-20: Token Standard. https://eips.ethereum.org/EIPS/eip-20
19. Ori Pomerantz, Some tricks used by scam tokens and how to detect them, ethereum.org, 2023-09-15. https://ethereum.org/en/developers/tutorials/scam-token-tricks/
20. Tyler Thomas, Tiffanie Edwards, Ibrahim Baggili, "BlockQuery: Toward forensically sound cryptocurrency investigation", Forensic Science International: Digital Investigation 40 (2022) 301340. doi:10.1016/j.fsidi.2022.301340
