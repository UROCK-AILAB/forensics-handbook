---
title: "Defender 경고와 기록"
parent: "아티팩트 · Microsoft 365"
nav_order: 280
---

# Defender 경고와 기록 (Microsoft Defender XDR)

Microsoft Defender XDR 은 메일·클라우드 앱·계정·단말의 보안 이벤트를 고급 헌팅 (advanced hunting) 테이블에 쌓고 그 위에서 경고 (alert) 를 만들며, 원시 이벤트는 최대 30일, 포털 데이터는 180일 동안 볼 수 있습니다[1][2].

## 무엇을 기록하나 · 왜 생기나

Defender XDR 에는 성격이 다른 기록 두 가지가 있습니다. 하나는 메일 처리, 클라우드 앱 활동, 로그인처럼 일어난 일을 그대로 적은 이벤트 테이블이고, 다른 하나는 탐지 엔진이 그 이벤트를 판정해 만든 경고입니다. 경고는 개별 증거 조각이고, Defender XDR 이 서로 관련된 경고를 묶어 인시던트 (incident) 를 만듭니다[8].

이벤트 테이블은 조직이 켠 Defender 서비스가 채웁니다. 이 페이지에서 다루는 Microsoft 365 쪽 테이블은 아래와 같습니다[3].

| 테이블 | 담는 내용 |
|---|---|
| `EmailEvents` | 메일 배달·차단 등 메일 처리 이벤트[3] |
| `EmailAttachmentInfo` · `EmailUrlInfo` | 메일에 붙은 파일과 본문 URL 정보[3] |
| `EmailPostDeliveryEvents` | 받은편지함에 배달한 뒤에 일어난 보안 이벤트[3] |
| `UrlClickEvents` | 메일·Teams·Office 앱에서 Safe Links 를 거친 클릭[3] |
| `CloudAppEvents` | Office 365 와 다른 클라우드 앱의 계정·개체 이벤트[3] |
| `EntraIdSignInEvents` · `AADSignInEventsBeta` | Entra 대화형·비대화형 로그인[3] |
| `IdentityLogonEvents` · `IdentityInfo` | Active Directory 와 Microsoft 온라인 서비스 인증, 계정 정보[3] |
| `AlertInfo` · `AlertEvidence` | Defender for Endpoint·Office 365·Cloud Apps·Identity 경고의 메타데이터와 경고에 엮인 파일·IP·URL·사용자·장치[3][6] |

`EmailEvents` 는 Defender for Office 365 를 배포하지 않은 조직에서는 결과를 돌려주지 않습니다[5]. `CloudAppEvents` 는 Defender for Cloud Apps 가 채우고, 포털의 설정 > Cloud apps > App connectors 에서 Microsoft 365 activities 를 선택해야 Microsoft 365 활동이 들어옵니다[4]. 그래서 테이블이 비어 있으면 활동이 없었다고 보기 전에 서비스 배포와 커넥터 설정부터 확인합니다.

## 위치와 버전별 차이

기록을 보는 경로는 넷입니다. 포털의 사건 및 경고 (Incidents & alerts) 화면, 고급 헌팅 쿼리, Microsoft Graph 보안 API 의 경고 리소스 `alerts_v2`, 그리고 통합 감사 로그 (Unified Audit Log) 에 남는 경고 레코드입니다[7][8][9].

| 구분 | 보관·조회 범위 (2026년 9월 문서 기준) |
|---|---|
| Defender 포털 데이터 | 180일 보관하고 그동안 포털에서 보입니다. 사례 (Cases) 는 지우지 않습니다[2] |
| 고급 헌팅 원시 데이터 | 쿼리마다 최근 30일까지만 조회합니다[1][2] |
| Microsoft Sentinel 작업 영역을 연결한 경우 | 작업 영역에 설정한 분석 계층 (analytics-tier) 보존 기간만큼 조회합니다. Sentinel 데이터 레이크에만 있는 데이터는 고급 헌팅에서 보이지 않습니다[1] |
| 스트리밍 API 로 외부로 보낸 경우 | 스트리밍을 켠 날부터 쌓입니다[1] |
| 계약 종료·만료 | 유예·정지 기간 동안은 남고, 종료 뒤 늦어도 180일 안에 지워져 복구할 수 없습니다[2] |

고급 헌팅 쿼리 하나는 최대 100,000행, 결과 64 MB, 실행 10분까지 돌려줍니다[1]. 결과가 64 MB 를 넘으면 포털은 잘린 결과를 보여 주고 일부라는 안내를 띄우므로, 넓은 기간은 나눠서 내보냅니다[1]. 보관 기간 전반은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에서 다룹니다.

통합 감사 로그에는 Defender 관련 레코드 종류가 따로 있습니다[9].

| RecordType | 이름 | 내용 |
|---|---|---|
| 28 | `ThreatIntelligence` | 클라우드 메일함의 피싱·악성코드 이벤트[9] |
| 40 | `SecurityComplianceAlerts` | 보안·규정 준수 경고 신호[9] |
| 64 | `AirInvestigation` | 자동 조사 및 대응 (AIR) 이벤트[9] |
| 78 | `WDATPAlerts` | Defender for Endpoint 경고 이벤트[9] |
| 98 | `MCASAlerts` | Microsoft Cloud App Security 경고 이벤트[9] |

`SecurityComplianceAlerts` 레코드는 `UserId` 와 `UserKey` 가 늘 `SecurityComplianceAlerts` 이고, `Operation` 값은 새 경고가 생긴 `AlertTriggered`, 경고에 엔터티가 붙은 `AlertEntityGenerated`, 상태가 바뀌거나 댓글이 달린 `AlertUpdated` 셋 중 하나입니다[9]. 레코드 공통 구조는 [레코드 구조](unified-audit-log/record-structure.md)에서 설명합니다.

## 구조

### 경고 — alerts_v2 리소스

Graph 로 받은 경고 한 건에서 조사에 쓰는 속성은 아래와 같습니다[7].

| 속성 | 뜻 |
|---|---|
| `id` · `providerAlertId` · `incidentId` | 경고 ID, 원래 서비스의 경고 ID, 묶인 인시던트 ID |
| `title` · `severity` · `categories` · `mitreTechniques` | 경고 이름, 심각도(`informational`·`low`·`medium`·`high` 등), 분류, MITRE ATT&CK 기법 |
| `serviceSource` · `detectionSource` · `detectorId` · `alertPolicyId` | 경고를 만든 서비스, 탐지 기술, 탐지기와 정책 ID |
| `status` · `classification` · `determination` | 처리 상태, 참·거짓 판정(`truePositive`·`falsePositive`·`informationalExpectedActivity` 등), 조사 결론(`compromisedAccount`·`phishing`·`securityTesting` 등) |
| `evidence` | 경고에 엮인 증거 엔터티 |
| `createdDateTime` · `firstActivityDateTime` · `lastActivityDateTime` · `lastUpdateDateTime` · `resolvedDateTime` | 시각 다섯 개(아래 "시각 해석") |
| `assignedTo` · `comments` · `customDetails` · `systemTags` | 담당자, 댓글, 사용자 정의 값, 시스템 태그 |

### AlertInfo 와 AlertEvidence

`AlertInfo` 에는 경고 한 건의 메타데이터가, `AlertEvidence` 에는 그 경고에 엮인 엔터티가 한 행씩 들어가고, 두 테이블은 `AlertId` 로 이어 붙입니다[6]. `AlertEvidence` 의 `EntityType` 은 파일·프로세스·장치·사용자 같은 엔터티 종류이고, `EvidenceRole` 은 그 엔터티가 영향을 받았는지 단지 관련만 있는지를 나타냅니다[6]. 메일 엔터티는 `NetworkMessageId`·`EmailSubject`, 계정은 `AccountUpn`·`AccountObjectId`, OAuth 앱은 `OAuthApplicationId`, 네트워크는 `RemoteIP`·`RemoteUrl` 로 남습니다[6].

### EmailEvents

메일 한 통은 `NetworkMessageId`(Microsoft 365 가 만든 ID)와 `InternetMessageId`(보낸 메일 시스템이 붙인 ID)로 식별합니다[5]. 봉투 발신자는 `SenderMailFromAddress`, 받는 사람 화면에 보이는 발신자는 `SenderFromAddress` 에 따로 남기 때문에 둘이 다르면 발신자 위장을 의심해 볼 수 있습니다[5]. `DeliveryAction` 은 `Delivered`·`Junked`·`Blocked`·`Replaced`, `EmailDirection` 은 `Inbound`·`Outbound`·`Intra-org` 중 하나이고, `AuthenticationDetails` 에 DMARC·DKIM·SPF 판정이 들어갑니다[5]. `ForwardingInformation` 은 전달한 사용자와 전달 유형을 담은 JSON 배열이고, `ExchangeTransportRule` 은 전송 중에 작동한 메일 흐름 규칙입니다[5]. 판정이 배달 뒤에 바뀐 경우를 보려고 배달 당시 값인 `OriginalThreatTypes`·`OriginalDetectionMethods` 와 마지막 상태인 `LatestDeliveryLocation`·`LatestDeliveryAction` 이 따로 있습니다[5]. 받은편지함 규칙과 전달 흔적은 [받은편지함 규칙과 전달](exchange-online/inbox-rules.md), 메일 경로는 [메시지 추적](exchange-online/message-trace.md)에서 다룹니다.

### CloudAppEvents

`ActionType` 과 `ActivityType` 이 활동 종류, `ObjectName`·`ObjectType`·`ObjectId` 가 대상 개체, `AccountObjectId`·`AccountId`·`AccountDisplayName` 이 행위 계정, `IPAddress`·`CountryCode`·`City`·`Isp`·`UserAgent` 가 접속 환경입니다[4]. `RawEventData` 에는 원래 앱·서비스가 만든 원시 이벤트가 JSON 으로 들어갑니다[4]. Microsoft 365 활동이면 통합 감사 로그의 같은 활동 `AuditData` 와 필드별로 맞춰 봅니다. `IsImpersonated` 는 다른 사용자를 대신해 한 활동인지, `IsAnonymousProxy` 는 IP 가 알려진 익명 프록시인지를 나타냅니다[4]. `LastSeenForUser` 는 속성별로 마지막으로 본 뒤 지난 일수(0 은 오늘, 음수는 처음 봄)이고, `UncommonForUser` 는 그 사용자에게 드문 속성 목록입니다[4].

### Safe Links 로 감싼 URL

Safe Links 는 메일 속 URL 을 `*.safelinks.protection.outlook.com` 주소로 바꿔 써 두고, 사용자가 누를 때 목적지를 검사합니다[12]. 바꿔 쓴 주소의 `url` 매개변수에는 원래 목적지가, `data` 매개변수에는 `|` 로 나눈 값 목록이 들어갑니다[13]. `data` 형식은 Microsoft 가 문서로 공개하지 않았고 실제 주소를 모아 거꾸로 풀어낸 것이라, 형식 버전마다 필드 수가 다릅니다[12][13]. `data` 를 `|` 로 나눠 0부터 세면 0번은 형식 버전(`01`~`05`), 2번은 받는 사람 메일 주소, 3번은 메시지별 GUID 로 보이는 값, 4번은 테넌트 GUID 로 보이는 값, 7번은 시각, 8번은 검사 결과(`Unknown`·`Bad`), 9번은 base64 로 인코딩한 검사 정보이고, unfurl 로 이 값들을 풀 수 있습니다[12][13]. 시각은 v02 부터, 검사 결과와 검사 정보는 v03 부터 들어갑니다[13]. v05 는 Office 데스크톱·Teams·Office 웹 앱에서 누를 때 검사한 경우 11~13번에 Teams 대화·메시지 ID 나 세션·문서 GUID 로 보이는 값을 넣고, 그 밖에는 비워 둡니다[13]. 9번을 base64 로 풀면 `Mailflow`·`ThreatIntel`·`OfficeClient`·`Teams`·`WAC` 같은 Defender 구성 요소 이름 뒤에 `|` 와 JSON 이 이어집니다[13]. 7번 값은 .NET DateTime 틱 (ticks), 곧 0001-01-01 00:00 부터 센 100나노초 단위 수이고, unfurl 은 여기서 621355968000000000 을 빼 1970-01-01 기준 초로 바꾼 뒤 UTC 로 보여 줍니다[14]. 풀어 낸 날짜는 대개 검사 시각이나 만료 시각으로 볼 만하지만 어느 쪽인지 정해진 뜻이 없으므로, 보고서에는 클릭 시각이 아니라 "`data` 안의 시각" 으로 적습니다[13]. 메일 본문이나 브라우저 기록에서 이런 주소를 찾으면 Safe Links 가 그 링크를 바꿔 썼다는 점을 알 수 있고, 2번이 채워져 있으면 누구 앞으로 바꿔 썼는지, 4번 값으로 어느 테넌트였는지 짐작할 수 있습니다[13]. 반면 메일 본문의 주소는 아무도 누르지 않아도 남고 2번 받는 사람은 비어 있는 경우가 많아서, 이 주소만으로는 누가 언제 눌렀는지 증명하지 못합니다[12][13]. 클릭은 브라우저 기록의 방문 시각과 `UrlClickEvents` 로 따로 확인합니다[3].

## 증거로서 의미

**증명하는 것**

- 경고 한 건은 탐지 엔진이 특정 시각에 특정 엔터티를 특정 규칙으로 판정했다는 사실입니다[7]. `serviceSource`·`detectionSource`·`alertPolicyId` 로 어느 규칙이 판정했는지 보여 줍니다.
- `EmailEvents` 한 행은 해당 메일을 Microsoft 365 가 그 시각에 어떤 판정으로 어디에 배달했는지를 보여 줍니다[5].
- `status`·`classification`·`determination`·`comments`·`assignedTo` 는 보안 담당자가 경고를 어떻게 처리했는지 남깁니다[7]. 통합 감사 로그의 `AlertUpdated` 도 상태 변경과 댓글을 기록합니다[9].

**증명하지 못하는 것**

- 경고는 침해가 일어났다는 확정이 아닙니다. `classification` 이 `falsePositive` 이거나 `determination` 이 `securityTesting` 일 수 있으므로 처리 결과를 함께 적습니다[7].
- 경고가 없다고 해서 활동이 없었던 것은 아닙니다. 서비스를 배포하지 않았거나 커넥터를 켜지 않았으면 테이블 자체가 비어 있습니다[4][5].
- 고급 헌팅 30일 창 밖의 원시 이벤트는 조회되지 않으므로, 오래된 기간의 "결과 없음" 은 부재의 증거가 되지 못합니다[1].

보고서에는 "2026-09-01 02:14 UTC 에 Defender for Office 365 가 이 메일을 피싱으로 판정해 격리했다는 경고가 있다" 처럼 기록으로 확인되는 만큼만 씁니다(만든 예시).

## 시각 해석

고급 헌팅은 모든 데이터를 UTC 로 저장하고 쿼리도 UTC 로 씁니다[1]. 다만 포털은 결과를 사용자가 설정한 시간대로 바꿔 보여 주므로, 화면에서 옮겨 적은 시각과 내보낸 파일의 시각이 다를 수 있습니다[1]. 각 테이블의 `Timestamp` 는 이벤트를 기록한 시각입니다[4][5][6].

경고에는 시각이 다섯 개 있습니다[7]. `createdDateTime` 은 Defender 가 경고를 만든 시각이고, `firstActivityDateTime` 은 경고와 관련된 가장 이른 활동, `lastUpdateDateTime` 은 경고를 마지막으로 고친 시각, `resolvedDateTime` 은 해결한 시각입니다. 활동은 경고를 만들기 전에 일어나므로 `firstActivityDateTime` 이 `createdDateTime` 보다 앞서는 것이 정상입니다. `lastActivityDateTime` 은 이름으로는 가장 늦은 활동이지만 설명 문구가 "The oldest activity associated with the alert" 로 되어 있어 이름과 어긋나므로, 실제 데이터에서 `firstActivityDateTime` 과 비교해 어느 쪽이 늦은지 확인한 뒤 해석합니다[7]. Graph 값의 시간대는 값 끝의 오프셋 표기로 확인합니다.

`EmailEvents` 를 스트리밍 API 로 받은 경우 판정이나 배달 위치가 바뀔 때마다 새 레코드가 생기므로, 같은 메일·수신자에 행이 여러 개 있으면 시간 순서대로 판정이 바뀐 과정입니다[5]. 로그 시각 전반은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에서 다룹니다.

## 함정과 한계

- 포털 경고 큐는 기본으로 최근 7일의 새 경고와 진행 중인 경고만 보여 줍니다[8]. 필터를 풀지 않으면 해결된 경고와 오래된 경고를 놓칩니다.
- 경고 조정 (alert tuning) 규칙의 "Hide alert" 는 경고를 숨기고 인시던트를 만들지 않지만, 숨긴 경고도 `AlertInfo`·`AlertEvidence` 테이블에는 남습니다[8]. 이 동작은 Defender for Endpoint 경고에만 적용됩니다[8]. "Set as behavior" 로 바꾼 신호는 경고 큐에 나오지 않고 `BehaviorInfo`·`BehaviorEntities` 테이블에 남습니다[8]. 따라서 큐에 없는 경고는 헌팅 테이블에서 다시 찾습니다.
- `EmailEvents` 의 `ReportId` 는 반복되는 카운터로 만든 이벤트 ID 라서 단독으로는 고유하지 않습니다[5]. 메일과 수신자별로 행을 묶을 때는 `NetworkMessageId`·`RecipientEmailAddress` 를 함께 씁니다[5].
- `LatestDeliveryLocation`·`LatestDeliveryAction` 은 스트리밍 API 로 받은 데이터에는 없습니다[5]. 배달 뒤 이동·삭제는 스트리밍으로 받은 여러 행을 이어서 봐야 합니다.
- `AlertEvidence` 의 `SHA256` 은 대개 비어 있으므로 파일은 `SHA1` 로 찾습니다[6].
- 30일이 지나면 원시 이벤트를 고급 헌팅으로 다시 뽑을 수 없습니다[1][2]. 사건을 인지하면 바로 내보냅니다. 절차는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)에 있습니다.

## 직접 분석해 보기

### 원본 레코드 한 건 읽기

Graph 로 내보낸 경고 한 건은 아래와 같은 모양입니다. 모든 값은 만든 예시입니다.

```json
{
  "id": "ca00000000-0000-0000-0000-000000000000",
  "incidentId": "1234",
  "title": "Suspicious inbox forwarding",
  "severity": "medium",
  "classification": "truePositive",
  "determination": "compromisedAccount",
  "createdDateTime": "2026-09-01T02:20:11Z",
  "firstActivityDateTime": "2026-09-01T02:14:05Z",
  "lastUpdateDateTime": "2026-09-02T08:00:00Z",
  "resolvedDateTime": "2026-09-02T08:00:00Z"
}
```

이 레코드는 활동이 02:14 UTC 에 있었고 Defender 가 6분 뒤 경고를 만들었으며, 담당자가 다음 날 계정 침해로 결론짓고 닫았다는 뜻입니다. `Suspicious inbox forwarding` 은 Microsoft Cloud App Security 가 의심스러운 메일 전달 규칙을 알리는 경고 이름이고, SigmaHQ 규칙은 `eventSource` 가 `SecurityComplianceCenter` 이고 `eventName` 이 이 이름인 이벤트를 찾습니다[11].

### 공개 도구와 쿼리

Microsoft-Extractor-Suite 의 `Get-SecurityAlerts` 는 `SecurityEvents.Read.All` 권한으로 Graph 경고를 받아 CSV 로 저장하고, 애플리케이션 인증이면 `Get-MgSecurityAlertV2`, 위임 인증이면 `Get-MgSecurityAlert` 를 씁니다[10]. 두 cmdlet 은 받는 경고 리소스가 다르므로 어느 쪽으로 받았는지 수집 기록에 적습니다. 도구 전반은 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)에서 다룹니다.

고급 헌팅에서는 경고와 증거를 이어 붙여 봅니다. 사용자 주소는 만든 예시입니다.

```kusto
AlertInfo
| where Timestamp between (datetime(2026-09-01) .. datetime(2026-09-03))
| join kind=inner AlertEvidence on AlertId
| where AccountUpn =~ "user1@contoso.com" or isnotempty(NetworkMessageId)
| project Timestamp, AlertId, Title, ServiceSource, EntityType, EvidenceRole,
          AccountUpn, NetworkMessageId, RemoteIP
```

같은 메일을 `EmailEvents` 에서 찾아 판정과 배달 위치, 전달 정보를 봅니다.

```kusto
EmailEvents
| where NetworkMessageId == "00000000-0000-0000-0000-000000000000"
| project Timestamp, SenderMailFromAddress, SenderFromAddress, RecipientEmailAddress,
          DeliveryAction, DeliveryLocation, ThreatTypes, OriginalThreatTypes,
          AuthenticationDetails, ForwardingInformation
```

## 교차 검증

| 함께 볼 기록 | 잇는 값 | 확인하는 것 |
|---|---|---|
| [통합 감사 로그](unified-audit-log/index.md) | `CloudAppEvents.RawEventData` 와 `AuditData`, RecordType 40 의 `AlertId` | 경고의 원인 활동과 경고 처리 이력[4][9] |
| [메시지 추적](exchange-online/message-trace.md) | `NetworkMessageId`, `InternetMessageId` | 메일이 실제로 거친 경로와 배달 상태 |
| [받은편지함 규칙과 전달](exchange-online/inbox-rules.md) | `ForwardingInformation`, 계정 | 전달을 만든 규칙과 만든 시각 |
| [로그인 로그](entra-logs/sign-in-logs.md) | `AccountObjectId`, IP | 경고 전후의 로그인 위치·방식 |
| [위험 탐지](entra-logs/identity-protection.md) | 계정, 시각 | 같은 계정에 대한 Identity Protection 판정 |

## 실습

만든 테넌트나 공개 교육용 데이터로 다음 질문을 풀어 봅니다.

1. 경고 한 건의 `firstActivityDateTime`·`createdDateTime`·`lastActivityDateTime` 을 비교해 탐지까지 걸린 시간과 두 활동 시각의 앞뒤를 구합니다.
2. 경고 큐에서 보이지 않는 경고가 `AlertInfo` 에는 있는지 찾아보고, 숨긴 경고인지 behavior 로 바뀐 신호인지 구분합니다.
3. `EmailEvents` 에서 `SenderMailFromAddress` 와 `SenderFromAddress` 가 다른 메일을 찾아 `AuthenticationDetails` 판정과 함께 정리합니다.
4. `CloudAppEvents.RawEventData` 한 건을 통합 감사 로그에서 같은 활동의 `AuditData` 와 필드별로 비교합니다.

## 참고 문헌

1. Microsoft, "Proactively hunt for threats with advanced hunting in Microsoft Defender XDR", Microsoft Learn, 2026-08-07 갱신. https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-overview
2. Microsoft, "Data security and retention in Microsoft Defender XDR", Microsoft Learn, 2025-10-01 갱신. https://learn.microsoft.com/en-us/defender-xdr/data-privacy
3. Microsoft, "Understand the advanced hunting schema", Microsoft Learn, 2026-07-27 갱신. https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-schema-tables
4. Microsoft, "CloudAppEvents", Microsoft Learn, 2025-05-15 갱신. https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-cloudappevents-table
5. Microsoft, "EmailEvents", Microsoft Learn, 2026-09-02 갱신. https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-emailevents-table
6. Microsoft, "AlertEvidence", Microsoft Learn, 2026-08-07 갱신. https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-alertevidence-table
7. Microsoft, "alert resource type (security)", Microsoft Graph, Microsoft Learn, 2026-01-08 갱신. https://learn.microsoft.com/en-us/graph/api/resources/security-alert
8. Microsoft, "Investigate alerts in Microsoft Defender XDR", Microsoft Learn, 2026-09-10 갱신. https://learn.microsoft.com/en-us/defender-xdr/investigate-alerts
9. Microsoft, "Office 365 Management Activity API schema", Microsoft Learn, 2026-08-26 갱신. https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
10. Invictus Incident Response, Microsoft-Extractor-Suite, `Scripts/Get-SecurityAlerts.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite
11. SigmaHQ, sigma, `rules/cloud/m365/threat_management/microsoft365_susp_inbox_forwarding.yml`. https://github.com/SigmaHQ/sigma
12. Ryan Benson, "Parsers for Gmail, Outlook Safe Links, Social Media IDs added in Unfurl", Hindsight Foundry, 2026-09-25. https://hindsig.ht/blog/unfurl-parses-gmail-safe-links-and-social-media-ids/
13. Ryan Benson, unfurl v2026.09, `unfurl/parsers/parse_safelinks.py`. https://github.com/RyanDFIR/unfurl/blob/main/unfurl/parsers/parse_safelinks.py
14. Ryan Benson, unfurl v2026.09, `unfurl/parsers/parse_timestamp.py` (`decode_datetime_ticks`). https://github.com/RyanDFIR/unfurl/blob/main/unfurl/parsers/parse_timestamp.py
