---
title: "위험 탐지"
parent: "Entra ID 로그"
grand_parent: "아티팩트 · Microsoft 365"
nav_order: 200
---

# 위험 탐지 (Identity Protection)

Microsoft Entra ID 보호 (Microsoft Entra ID Protection) 가 로그인과 사용자에 대해 "위험하다" 고 판정한 기록이며, 판정 유형·수준·처리 상태와 함께 행위 시각과 탐지 시각이 따로 남습니다.

## 무엇을 기록하나 · 왜 생기나

Microsoft Entra ID 는 여러 신호와 기계 학습으로 로그인 위험과 사용자 위험을 계속 평가하고, 위험을 하나 찾을 때마다 위험 탐지 (risk detection) 한 건을 남깁니다[2][3]. 로그인 하나에 위험 탐지가 하나 이상 붙으면 그 로그인은 위험 로그인 (risky sign-in) 으로 보고됩니다[3]. 사용자에게 위험 로그인이 있거나 위험 탐지가 하나 이상 있으면 그 사용자는 위험 사용자 (risky user) 로 보고됩니다[3]. 로그인마다 실시간 탐지를 모두 돌려 로그인 세션 위험 수준을 만들고, 조건부 접근 (Conditional Access) 정책은 이 수준을 조건으로 씁니다[3].

탐지마다 계산 시점이 실시간 (real-time) 인지 오프라인 (offline) 인지 정해져 있고, 둘 다 가능한 탐지도 있습니다[1]. 실시간 로그인 탐지는 로그인할 때마다 모두 돌아갑니다[3]. 일부 탐지는 Microsoft Defender for Cloud Apps·Defender for Endpoint·Defender for Office 365 가 보낸 신호로 만들어지므로, 그 제품이 없는 조직에서는 생기지 않습니다[1][3].

관리자가 위험을 무시 (dismiss)·안전 확인 (confirm safe)·침해 확인 (confirm compromise) 하거나, 위험 기반 정책에서 사용자가 MFA·안전한 비밀번호 재설정을 마치면 위험 상태가 바뀝니다[3]. 그래서 이 기록에는 Microsoft 의 판정뿐만 아니라 관리자와 사용자가 그 판정에 어떻게 대응했는지까지 남습니다.

## 위치와 라이선스별 차이

위험 탐지는 Entra 관리 센터의 ID 보호 보고서 세 가지(위험 탐지·위험 로그인·위험 사용자)와 Microsoft Graph `identityProtection` 경로로 봅니다[3][6]. 통합 감사 로그 (Unified Audit Log) 에도 레코드 유형 294 `AadRiskDetection` 으로 들어오고, 필드는 "Microsoft Entra Risk Detection schema" 를 따릅니다[5]. 통합 감사 로그 검색과 보관은 [통합 감사 로그](../unified-audit-log/index.md) 페이지를 봅니다.

라이선스에 따라 보이는 범위가 크게 다릅니다(2026년 4월·2025년 10월 문서 기준)[1][3].

| 항목 | Entra ID Free·Microsoft 365 Apps | Entra ID P1 | Entra ID P2 |
|---|---|---|---|
| 위험 탐지 보고서 | 없음 | 제한됨(상세 창 없음) | 전체 |
| 위험 로그인 보고서 | 제한됨(위험 상세·수준 안 보임) | 제한됨(위험 상세·수준 안 보임) | 전체 |
| 위험 사용자 보고서 | 제한됨(중간·높음만, 상세 창·위험 이력 없음) | 제한됨(중간·높음만, 상세 창·위험 이력 없음) | 전체 |
| Microsoft Graph 위험 보고서 | 없음 | 없음 | 있음 |
| 프리미엄 탐지의 유형 이름 | `generic`("Additional risk detected") | `generic` | 원래 이름 |

P2 가 없는 테넌트에서는 프리미엄 탐지가 발동해도 "Additional risk detected" 라는 이름과 `riskEventType` 값 `generic` 으로만 보이고, 무엇을 탐지했는지는 나오지 않습니다[1][2]. Untitled Goose Tool 코드 주석은 위험 탐지 수집에 "최소 P1" 이 필요하다고 적어 두었고[8], ID 보호 문서 표는 Graph 위험 보고서를 P2 전용으로 적었습니다[3]. 테넌트에서 Graph 호출이 되는지 먼저 시험해 보고 수집 범위를 정하면 됩니다.

보관 기간은 위험 로그인이 Free 7일·P1 30일·P2 90일이고, 위험 사용자는 라이선스와 관계없이 기한이 없으며 위험이 해결될 때까지 지워지지 않습니다[4]. 위험 탐지 데이터도 이 보관 정책을 따릅니다[2]. 다른 Entra 로그와 함께 본 보관 표는 [Entra ID 로그](index.md) 허브에 있습니다. 더 오래 두려면 진단 설정 (diagnostic settings) 으로 Log Analytics 작업 영역·저장소 계정·Event Hubs 로 보냅니다[3].

## 구조

Graph `riskDetection` 리소스의 필드는 다음과 같습니다[2]. 통합 감사 로그의 `AadRiskDetection` 레코드에는 같은 내용이 `RiskId`, `RiskEventType`, `ActivityDateTime`, `DetectedDateTime`, `RequestId`, `CorrelationId` 처럼 첫 글자가 대문자인 이름으로 들어갑니다[5].

| 필드 | 뜻 |
|---|---|
| `id` | 위험 탐지 하나의 고유 ID |
| `riskEventType` | 탐지 유형. 프리미엄 탐지를 P2 없이 보면 `generic` |
| `riskLevel` | `low`, `medium`, `high`, `hidden`, `none` |
| `riskState` | `none`, `confirmedSafe`, `remediated`, `dismissed`, `atRisk`, `confirmedCompromised` |
| `riskDetail` | 탐지한 위험의 상세 |
| `detectionTimingType` | `realtime`, `nearRealtime`, `offline`, `notDefined` |
| `activity` | 탐지가 연결된 활동의 종류 |
| `activityDateTime` | 위험한 활동이 일어난 시각(UTC) |
| `detectedDateTime` | 위험을 탐지한 시각(UTC) |
| `lastUpdatedDateTime` | 이 탐지가 마지막으로 바뀐 시각(UTC) |
| `requestId`, `correlationId` | 연결된 로그인의 요청 ID·상관 ID. 로그인과 무관한 탐지면 null |
| `ipAddress`, `location` | 위험이 발생한 클라이언트 IP 와 위치 |
| `tokenIssuerType` | `AzureAD`, `ADFederationServices` |
| `source` | 탐지 출처(예: `activeDirectory`) |
| `userId`, `userPrincipalName`, `userDisplayName` | 대상 사용자 |
| `additionalInfo` | 키-값 목록을 담은 JSON 문자열 |

`additionalInfo` 는 JSON 객체가 아니라 JSON 을 담은 문자열이라서 한 번 더 풀어야 합니다. 들어갈 수 있는 키는 `userAgent`, `alertUrl`, `relatedEventTimeInUtc`, `relatedUserAgent`, `deviceInformation`, `relatedLocation`, `requestId`, `correlationId`, `lastActivityTimeInUtc`, `malwareName`, `clientLocation`, `clientIp`, `riskReasons` 입니다[2]. `riskReasons` 에는 `investigationsThreatIntelligence` 탐지의 근거로 `suspiciousIP`, `passwordSpray` 같은 값이 들어갑니다[2].

### 주요 탐지 유형

아래 표는 조사에서 자주 만나는 유형만 골랐습니다(2026년 4월 문서 기준). "Premium" 은 Entra ID P2 이상이 있어야 하는 탐지이고, "Nonpremium" 은 Entra ID Free 에서도 나오는 탐지입니다[1].

| 이름 | `riskEventType` | 대상 | 계산 시점 | 등급 |
|---|---|---|---|---|
| Anonymous IP address | `anonymizedIPAddress` | 로그인 | 실시간 | Nonpremium |
| Admin confirmed user compromised | `adminConfirmedUserCompromised` | 로그인 | 오프라인 | Nonpremium |
| Microsoft Entra threat intelligence | `investigationsThreatIntelligence` | 로그인·사용자 | 실시간 또는 오프라인 | Nonpremium |
| Leaked credentials | `leakedCredentials` | 사용자 | 오프라인 | Nonpremium |
| Unfamiliar sign-in properties | `unfamiliarFeatures` | 로그인 | 실시간 | Premium |
| Atypical travel | `unlikelyTravel` | 로그인 | 오프라인 | Premium |
| Impossible travel | `mcasImpossibleTravel` | 로그인 | 오프라인 | Premium(Defender for Cloud Apps 필요) |
| Password spray | `passwordSpray` | 로그인 | 실시간 또는 오프라인 | Premium |
| Anomalous Token | `anomalousToken` | 로그인·사용자 | 실시간 또는 오프라인 | Premium |
| Suspicious MFA authentication approval | `authenticatorPhishing` | 로그인 | 실시간 | Premium |
| Verified threat actor IP | `nationStateIP` | 로그인 | 실시간 | Premium |
| Suspicious inbox forwarding | `suspiciousInboxForwarding` | 로그인 | 오프라인 | Premium(Defender for Cloud Apps 필요) |
| Suspicious inbox manipulation rules | `mcasSuspiciousInboxManipulationRules` | 로그인 | 오프라인 | Premium(Defender for Cloud Apps 필요) |
| Mass Access to Sensitive Files | `mcasFinSuspiciousFileAccess` | 로그인 | 오프라인 | Premium(Defender for Cloud Apps 필요) |
| Token issuer anomaly | `tokenIssuerAnomaly` | 로그인 | 오프라인 | Premium |
| Attacker in the Middle | `attackerinTheMiddle` | 사용자 | 오프라인 | Premium(Microsoft 365 E5 + EMS E5) |
| Possible attempt to access PRT | `attemptedPrtAccess` | 사용자 | 오프라인 | Premium(Defender for Endpoint 배포 조직만) |
| Suspicious API Traffic | `suspiciousAPITraffic` | 사용자 | 오프라인 | Premium |
| User reported suspicious activity | `userReportedSuspiciousActivity` | 사용자 | 오프라인 | Premium("Report suspicious activity" 기능을 켜야 함) |

"Defender for Cloud Apps 필요" 는 P2 에 Defender for Cloud Apps 단독 라이선스를 더하거나, Microsoft 365 E5 와 EMS E5 를 함께 쓰는 경우입니다[1].

> 그림 자리: 한 로그인에 붙은 위험 탐지 두 건(실시간 1건, 오프라인 1건)이 위험 로그인과 위험 사용자로 모이는 관계와, 각 탐지의 activityDateTime·detectedDateTime 간격

## 증거로서 의미

**증명하는 것**

- Microsoft 가 이 시각에 이 사용자 또는 로그인에 대해 이 유형·수준의 위험을 판정했다는 사실[2].
- `requestId`·`correlationId` 가 채워져 있으면 판정이 걸린 로그인이 어느 것인지[2]. 그 로그인의 앱·클라이언트·조건부 접근 결과는 [로그인 로그](sign-in-logs.md)에서 이어 봅니다.
- `riskState` 가 `dismissed`, `confirmedSafe`, `confirmedCompromised` 이면 누군가 판정에 대응했다는 사실[2][3]. 누가 언제 대응했는지는 [감사 로그](audit-logs.md)의 ID 보호 활동(`DismissUser`, `DismissRisk`, `ConfirmCompromised`, `ConfirmSafe` 등)과 위험 사용자의 위험 이력 (risk history) 에서 찾습니다[1][10].
- `passwordSpray` 는 비밀번호 대입이 한 번이라도 맞았을 때만 생기므로, 이 탐지가 있으면 그 사용자의 비밀번호가 맞게 검증된 적이 있다는 뜻입니다[1].
- `leakedCredentials` 는 유출 자료에서 찾은 자격 증명이 테넌트의 현재 비밀번호 해시와 맞을 때만 생기므로, 그 시점에 유효한 비밀번호가 밖에 돌았다는 뜻입니다[1].

**증명하지 못하는 것**

- 계정이 실제로 침해되었다는 사실. 탐지는 판정일 뿐이고, `anomalousToken` 은 낮음·중간 수준에서 오탐일 가능성이 다른 탐지보다 높습니다[1].
- `passwordSpray` 가 있다고 해서 공격자가 자원에 접근한 것은 아닙니다. 비밀번호가 맞았다는 것까지만 뜻합니다[1].
- 탐지가 없다는 것이 안전하다는 뜻은 아닙니다. 라이선스가 없으면 탐지가 `generic` 으로 뭉개지거나 아예 생기지 않고[1][3], 오프라인 탐지는 늦게 들어올 가능성이 있으며, 새 사용자는 학습 기간이 끝나기 전까지 일부 탐지가 꺼져 있습니다(아래 "함정과 한계").
- 위험 이후에 무엇을 했는지. 메일·파일 작업은 [통합 감사 로그](../unified-audit-log/index.md)와 [Exchange Online](../exchange-online/index.md) 기록으로 따로 확인합니다.

## 시각 해석

한 탐지에 시각이 셋 있고, 모두 ISO 8601 형식의 UTC 입니다(예: `2014-01-01T00:00:00Z`)[2]. `activityDateTime` 은 위험한 활동, 곧 로그인 등이 일어난 시각이고, `detectedDateTime` 은 Microsoft 가 위험을 찾아낸 시각입니다[2]. 실시간 탐지는 두 값이 가까울 가능성이 높고, 오프라인 탐지는 `detectedDateTime` 이 `activityDateTime` 보다 늦을 가능성이 있습니다. 타임라인에 넣을 때는 "무슨 일이 언제 있었나" 에는 `activityDateTime` 을, "조직이 언제 알 수 있었나" 에는 `detectedDateTime` 을 씁니다.

`lastUpdatedDateTime` 은 탐지가 마지막으로 바뀐 시각이라[2], 관리자의 무시·확인이나 사용자의 자가 해결로 `riskState` 가 바뀌면 함께 바뀔 가능성이 있습니다. 이 값을 사건 발생 시각으로 쓰면 안 됩니다. `additionalInfo` 안의 `relatedEventTimeInUtc`·`lastActivityTimeInUtc` 도 이름대로 UTC 입니다[2]. 클라우드 로그 시각을 다루는 공통 원리는 [클라우드 로그의 시각](../../../01-foundations/logging/timestamps.md)을 봅니다.

## 함정과 한계

- **`generic` 은 "별일 없음" 이 아닙니다.** P2 가 없는 테넌트에서 프리미엄 탐지가 걸린 것이고, 무엇이 걸렸는지는 이 테넌트 기록만으로는 알 수 없습니다[1].
- **유형 이름이 출처마다 다릅니다.** 탐지 문서 표는 불가능한 이동을 `mcasImpossibleTravel` 로 적었지만, Graph 리소스 문서의 값 목록과 Sigma 규칙에는 `impossibleTravel` 이 있습니다[1][2][9]. Graph 문서 목록에는 `malwareInfectedIPAddress`, `suspiciousIPAddress` 도 있고 탐지 문서 표에는 없습니다[1][2]. 반대로 `authenticatorPhishing`, `nationStateIP`, `attemptedPrtAccess` 는 탐지 문서 표에만 있습니다[1][2]. 검색할 때는 두 이름을 모두 넣습니다.
- **학습 기간.** Unfamiliar sign-in properties 는 새 사용자에게 최소 5일의 학습 기간 동안 꺼져 있고, 오래 쓰지 않은 사용자도 다시 학습 기간으로 돌아갈 수 있습니다[1]. Atypical travel 은 14일 또는 로그인 10회 중 먼저 오는 시점까지 학습합니다[1]. 새로 만든 계정이나 오래 쉰 계정이 악용되면 이 탐지가 없을 수 있습니다.
- **비대화형 로그인.** Unfamiliar sign-in properties 는 비대화형 로그인에서도 걸리며, 이 경우 토큰 재사용 공격일 가능성이 있어 더 꼼꼼히 살펴봅니다[1]. 비대화형 로그인 기록은 [로그인 로그](sign-in-logs.md)에 있습니다.
- **레거시 인증.** 기본 인증(레거시 프로토콜) 로그인에는 클라이언트 ID 같은 속성이 없어 오탐을 걸러 낼 자료가 적습니다[1].
- **처리 상태가 바뀝니다.** 관리자가 무시하거나 사용자가 해결하면 `riskState` 가 `dismissed`·`remediated` 로 바뀌므로, 수집 시점의 상태가 사건 당시 상태와 다를 수 있습니다[2][3]. 상태 변화 이력은 위험 사용자의 `history` 에서 봅니다[8].
- **보관.** 위험 로그인은 Free 테넌트에서 7일이면 사라지므로 먼저 내보냅니다[4]. 수집 순서는 [로그부터 지키기](../../../03-techniques/acquisition/log-preservation.md)를 봅니다.

## 직접 분석해 보기

### 레코드 한 건 읽기

아래는 Graph `riskDetection` 형식[2]에 맞춰 만든 예시이며, ID·사용자·IP 는 모두 지어낸 값입니다.

```json
{
  "id": "example-risk-detection-0001",
  "requestId": "3c5a1f0e-1111-4a2b-9c3d-000000000001",
  "correlationId": "7d9e2b1c-2222-4b3c-8d4e-000000000002",
  "riskEventType": "unlikelyTravel",
  "riskState": "atRisk",
  "riskLevel": "medium",
  "source": "activeDirectory",
  "detectionTimingType": "offline",
  "tokenIssuerType": "AzureAD",
  "ipAddress": "203.0.113.45",
  "activityDateTime": "2026-03-02T01:14:07Z",
  "detectedDateTime": "2026-03-02T03:40:12Z",
  "lastUpdatedDateTime": "2026-03-02T03:41:30Z",
  "userId": "a1b2c3d4-0000-4000-8000-000000000001",
  "userDisplayName": "Kim Minsu",
  "userPrincipalName": "minsu.kim@contoso.com",
  "additionalInfo": "[{\"Key\":\"userAgent\",\"Value\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64)\"}]"
}
```

이 예시에서 활동은 UTC 01:14 이고 탐지는 03:40 이라, 오프라인 탐지가 약 2시간 반 뒤에 계산된 모양입니다. `requestId`·`correlationId` 가 있으므로 로그인 로그에서 같은 값을 찾아 그 로그인의 앱·클라이언트·조건부 접근 결과를 확인합니다. `additionalInfo` 는 따옴표가 이스케이프된 문자열이라, 파싱해야 `userAgent` 값을 꺼낼 수 있습니다.

### 공개 도구로 받기

Microsoft-Extractor-Suite 의 `Get-RiskyUsers` 와 `Get-RiskyDetections` 는 Graph `v1.0/identityProtection/riskyUsers` 와 `v1.0/identityProtection/riskDetections` 를 불러 CSV 로 저장하고, 권한 범위로 `IdentityRiskEvent.Read.All` 과 `IdentityRiskyUser.Read.All` 을 요구합니다[6]. Hawk 의 `Get-HawkTenantRiskDetections` 는 `Get-MgRiskDetection -All` 결과를 `Risk_Detections` 이름의 CSV·JSON 으로 저장하고, `riskState` 가 침해 확인인 탐지는 `_Investigate_Confirmed_Compromised_Risk_Detection` 파일로 따로 뺍니다[7]. Untitled Goose Tool 은 `identityProtection/riskDetections` 와 서비스 주체 위험 탐지, 위험 사용자와 그 `history` 까지 받습니다[8]. 도구별 설치와 인증은 [Microsoft 365 수집 도구](../../../03-techniques/acquisition/m365-collection.md)를 봅니다.

JSON 으로 받았다면 `jq` 로 시각 두 개와 연결 키만 뽑아 간격을 봅니다.

```bash
jq -r '.[] | [.userPrincipalName, .riskEventType, .riskLevel, .riskState,
             .detectionTimingType, .activityDateTime, .detectedDateTime,
             .correlationId] | @tsv' Risk_Detections.json
```

Sigma 의 `identity_protection` 규칙은 로그 출처를 `product: azure`, `service: riskdetection` 으로 두고 `riskEventType` 값 하나로 거릅니다[9]. 수집한 탐지에 규칙을 돌리는 방법은 [탐지 규칙으로 로그 검색하기](../../../03-techniques/analysis/detection-rules.md)를 봅니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 | 링크 |
|---|---|---|
| 로그인 로그 | `correlationId`·`requestId` 로 짝지은 로그인의 앱·IP·사용자 에이전트·조건부 접근 결과, 같은 IP 의 다른 로그인 | [로그인 로그](sign-in-logs.md) |
| 감사 로그 | 위험 무시·확인을 누가 했는지, 탐지 뒤 비밀번호 재설정·MFA 등록·역할 변경 | [감사 로그](audit-logs.md) |
| 통합 감사 로그 | `AadRiskDetection`(294) 레코드, 같은 시간대 메일·파일 작업 | [통합 감사 로그](../unified-audit-log/index.md) |
| Exchange Online | `suspiciousInboxForwarding` 등에 대응하는 받은편지함 규칙·전달 설정 | [Exchange Online](../exchange-online/index.md) |
| Defender XDR | 같은 사용자에 대한 경고와 증거 | [Defender 경고와 기록](../defender-xdr.md) |

로그인 이상 징후를 가려내는 전체 흐름은 [이상한 로그인 가려내기](../../../03-techniques/analysis/suspicious-sign-ins.md), 토큰 재사용이 의심될 때는 [토큰을 훔쳐 로그인했나](../../../04-scenarios/account-compromise/token-theft.md)를 봅니다.

## 실습

위 만든 예시 레코드와, 같은 사용자에 대해 스스로 지어낸 로그인 로그 몇 줄로 풀어 봅니다.

1. 예시 레코드에서 "사건 시각" 과 "탐지 시각" 은 각각 무엇이고, 한국 시간으로는 몇 시입니까?
2. 같은 테넌트가 P1 라이선스였다면 이 레코드의 `riskEventType` 과 `riskLevel` 은 어떻게 보였을 가능성이 있습니까?
3. `riskState` 가 이튿날 `dismissed` 로 바뀌었다면, 어느 필드가 바뀌고 누가 바꿨는지는 어느 로그에서 찾습니까?
4. 같은 사용자에게 `passwordSpray` 탐지가 있고 그 뒤 로그인 로그에 조건부 접근 실패만 있다면, 보고서에는 무엇까지 쓸 수 있습니까?

## 참고 문헌

1. Microsoft, "What are risk detections?" (갱신 2026-04-22). https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-risks
2. Microsoft, "riskDetection resource type" (Microsoft Graph, 갱신 2025-11-28). https://learn.microsoft.com/en-us/graph/api/resources/riskdetection
3. Microsoft, "What is Microsoft Entra ID Protection?" (갱신 2025-10-30). https://learn.microsoft.com/en-us/entra/id-protection/overview-identity-protection
4. Microsoft, "Microsoft Entra data retention" (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
5. Microsoft, "Office 365 Management Activity API schema" (갱신 2026-08-26). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
6. Invictus Incident Response, Microsoft-Extractor-Suite, `Scripts/Get-RiskyEvents.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite
7. T0pCyber, Hawk, `Get-HawkTenantRiskDetections.ps1`, `Get-HawkTenantRiskyUsers.ps1`. https://github.com/T0pCyber/hawk
8. CISA, Untitled Goose Tool, `goosey/entra_id_datadumper.py`. https://github.com/cisagov/untitledgoosetool
9. SigmaHQ, Sigma, `rules/cloud/azure/identity_protection/`. https://github.com/SigmaHQ/sigma
10. Microsoft, "Microsoft Entra audit log categories and activities" (entra-docs). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
