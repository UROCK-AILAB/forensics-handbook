---
title: "IP·사용자 에이전트·위치 정보"
parent: "기반 · 로그 체계"
nav_order: 120
---

# IP·사용자 에이전트·위치 정보 (IP·User Agent·Geo)

클라우드 로그의 IP 주소·사용자 에이전트(User Agent, UA)·위치 값이 서비스마다 어느 필드에 들어가고, 어떤 경우에 사용자 기기와 무관한 값이 되는지 정리합니다.

## 이 형식을 쓰는 아티팩트

로그인 로그와 관리·데이터 로그의 레코드에는 대부분 요청이 들어온 IP 주소가 있고, 많은 로그에 사용자 에이전트 문자열도 함께 남습니다. 일부 서비스는 기록할 때 IP 로 국가·도시·자율 시스템 번호(Autonomous System Number, ASN)·프록시 여부를 찾아 레코드에 넣어 줍니다. 흐름 로그는 연결의 양 끝 주소를 남깁니다. 로그 종류는 [로그의 종류](log-types.md)에서, 레코드 겉모양과 중첩 JSON 을 푸는 법은 [JSON 로그 읽기](json-logs.md)에서 다룹니다.

이 값을 주로 쓰는 곳은 [이상한 로그인 가려내기](../../03-techniques/analysis/suspicious-sign-ins.md)와 [탐지 규칙으로 로그 검색하기](../../03-techniques/analysis/detection-rules.md)입니다.

## 구조

### 서비스별 필드 이름

| 서비스·로그 | IP | 사용자 에이전트 | 서비스가 넣는 위치·네트워크 정보 |
|---|---|---|---|
| AWS CloudTrail | `sourceIPAddress` | `userAgent` | 없음 |
| AWS VPC 흐름 로그 | `srcaddr`·`dstaddr`, `pkt-srcaddr`·`pkt-dstaddr` | 없음 | 없음 |
| Azure 활동 로그 | `httpRequest.clientIpAddress`(저장소·이벤트 허브로 내보낸 스키마는 `callerIpAddress`), 토큰 클레임 `claims.ipaddr` | 없음 | 없음 |
| Entra ID 로그인(Graph v1.0) | `ipAddress` | 없음(`deviceDetail` 에 브라우저·운영체제) | `location`(도시·주·국가 코드) |
| Entra ID 로그인(Graph beta) | `ipAddress`, `ipAddressFromResourceProvider`, `globalSecureAccessIpAddress` | `userAgent` | `location`(도시·주·2글자 국가 코드), `autonomousSystemNumber`, `networkLocationDetails` |
| Entra ID 로그인(Log Analytics `SigninLogs`) | `IPAddress`, `IPAddressFromResourceProvider` | `UserAgent`, `DeviceDetail` | `Location`(2글자 국가 코드), `LocationDetails`(도시·주·국가·위도·경도), `AutonomousSystemNumber`, `NetworkLocationDetails` |
| Microsoft 365 통합 감사 로그 | `ClientIP`(공통 스키마), `ClientIPAddress`(Exchange 사서함), `ActorIpAddress`(Entra 스키마) | `UserAgent`(SharePoint 등), `ClientInfoString`(Exchange 사서함) | 없음 |
| Google Cloud 감사 로그 | `protoPayload.requestMetadata.callerIp` | `protoPayload.requestMetadata.callerSuppliedUserAgent` | 없음 |
| Google Cloud VPC 흐름 로그 | `connection.src_ip`·`connection.dest_ip` | 없음 | `src_location`·`dest_location`(`asn`, `city`, `continent`, `country`, `region`) |
| Google Workspace Reports API | `ipAddress` | 없음(공통 필드 기준) | `networkInfo`(`ipAsn[]`, `regionCode`, `subdivisionCode`) |
| Okta System Log | `client.ipAddress`, `request.ipChain[]` | `client.userAgent`(`rawUserAgent`, `browser`, `os`) | `client.geographicalContext`, `client.zone`, `securityContext`(`asNumber`, `asOrg`, `domain`, `isp`, `isProxy`) |
| Slack 액세스 로그 | `ip` | `user_agent` | `isp`, `country`, `region` |
| Slack 감사 로그 | `context.ip_address` | `context.ua` | 없음(`context.location` 은 지리 위치가 아님) |
| GitHub 감사 로그 | 표시 설정을 켜야 나타남 | `user_agent`(이벤트 필드 목록) | `actor_location.country_code` |
| Dropbox 팀 이벤트 | `GeoLocationLogInfo.ip_address` | 없음 | `city`, `region`, `country` |

근거: [1][2][4][5][6][7][10][11][12][13][14][15][17][18][19][20][30]

### 국가·지역 값의 형식

같은 "국가" 라도 서비스마다 표기 방식이 다르므로, 여러 로그를 한 표로 합칠 때는 형식을 먼저 맞춥니다.

| 서비스·필드 | 형식 |
|---|---|
| Entra `SigninLogs` 의 `Location` | 2글자 국가 코드[7] |
| Google Workspace `networkInfo.regionCode` | ISO 3166-1 alpha-2, 하위 지역 `subdivisionCode` 는 ISO 3166-2[13] |
| Google Cloud VPC 흐름 로그 `country` | ISO 3166-1 alpha-3(3글자)[12] |
| Okta `geographicalContext.country`·`state` | 국가·주 전체 이름(예: France, Ontario)[14] |
| Slack 액세스 로그 `country`·`region` | 예시 값이 2글자(`US`, `CA`)[15] |
| GitHub `actor_location.country_code` | 예시 값이 2글자(`US`)[18] |
| Dropbox `country` | 국가 코드[20] |

Google Workspace `networkInfo.ipAsn[]` 는 정수(integer) 배열이고[13], 이름으로 보면 ASN 목록일 가능성이 있습니다. Okta 의 `geolocation` 은 위도(`lat`)·경도(`lon`)를 ISO 6709 형식으로 담고, `postalCode` 로 우편 번호 단위까지 적습니다[14].

## 읽는 법

### IP 필드에 IP 가 아닌 값이 들어오는 경우

CloudTrail `sourceIPAddress` 는 AWS 서비스가 호출한 경우 서비스의 DNS 이름만 적고, AWS 가 만든 이벤트는 보통 `AWS Internal/#`(#은 내부 번호)을 적습니다[1]. AWS 가 만든 이벤트의 `userAgent` 는 CloudTrail 이 호출한 서비스를 알면 그 서비스의 이벤트 소스(예: `ec2.amazonaws.com`), 모르면 `AWS Internal/#` 입니다[1]. IP 형식만 거르는 필터를 쓰면 이런 레코드가 빠지므로, 문자열 값을 따로 모아 봅니다.

Google Cloud 감사 로그의 `callerIp` 는 Google 내부 망에서 서비스끼리 부른 호출이면 `private` 로 가려집니다[11]. 외부 IP 가 있는 Compute Engine VM 이 호출하면 VM 의 외부 IP 가 들어가고, 외부 IP 가 없는 VM 은 같은 조직(또는 프로젝트)이면 내부 IPv4 주소, 아니면 `gce-internal-ip` 가 들어갑니다[11].

아래는 두 경우를 나란히 보인 만든 예시입니다(값은 모두 지어낸 것).

```json
{"eventSource": "s3.amazonaws.com", "eventName": "GetObject",
 "sourceIPAddress": "203.0.113.25", "userAgent": "aws-cli/2.15.0 Python/3.11.6 Linux/6.1"}
{"eventSource": "kms.amazonaws.com", "eventName": "Decrypt",
 "sourceIPAddress": "AWS Internal/3", "userAgent": "AWS Internal/3"}
```

### IP 가 사용자 기기의 주소가 아닌 경우

| 로그 | 기록되는 주소 |
|---|---|
| CloudTrail | 서비스 콘솔에서 시작한 작업은 콘솔 웹 서버가 아니라 그 밑에 있는 고객 자원의 주소를 적습니다[1]. VPC 엔드포인트를 거친 요청에는 `vpcEndpointId` 가 붙습니다[1]. |
| 통합 감사 로그 `ClientIP` | 일부 서비스는 사용자를 대신해 호출한 신뢰 앱(예: 웹용 Office)의 IP 를 적고, Entra ID 관련 이벤트는 IP 를 기록하지 않아 null 입니다[10]. |
| Entra 비대화형 로그인 | 기밀 클라이언트(confidential client)가 한 비대화형 로그인은 새로 고침 토큰을 요청한 실제 출발지가 아니라 처음 토큰을 받을 때의 IP 를 보여 줍니다[8]. |
| Entra `ipAddressFromResourceProvider` | 사용자가 자원 제공자(예: Exchange Online)에 닿을 때 쓴 IP 이고 흔히 null 입니다[6][7]. |
| Google Workspace `ipAddress` | 프록시 서버나 VPN 의 주소일 수 있어 물리적 위치를 반영하지 않을 수 있습니다[13]. |
| AWS VPC 흐름 로그 | 보조 사설 IPv4 주소로 온 트래픽도 `dstaddr` 에는 주 사설 IPv4 주소가 적히고, 원래 목적지는 `pkt-dstaddr` 필드로 만든 흐름 로그에서만 보입니다[3]. NAT 게이트웨이나 EKS 파드처럼 중간 계층이 있으면 `srcaddr`·`pkt-srcaddr` 를 함께 봐야 원래 출발지를 가릴 수 있습니다[2]. |
| Okta `request.ipChain[]` | 프록시를 거친 요청이면 클라이언트 IP, 프록시 1, 프록시 2 순서로 주소가 쌓입니다[14]. HTTP 요청에서 나오지 않은 이벤트는 이 배열이 비어 있습니다[14]. |

비대화형 로그인의 IP 가 토큰 발급 당시 주소로 남는 문제는 [토큰과 세션](../identity/tokens-sessions.md)과 [토큰을 훔쳐 로그인했나](../../04-scenarios/account-compromise/token-theft.md)에서 이어서 다룹니다.

Azure 활동 로그의 `httpRequest` 는 원시 HTTP 요청 정보가 민감할 수 있어 Azure 포털의 이벤트 화면에는 나오지 않습니다[4]. 출발지 IP 가 필요하면 REST API 결과나 진단 설정으로 내보낸 레코드를 읽습니다.

### 표시 설정이 있어야 IP 가 남는 경우

GitHub 는 기본으로 감사 로그에 출발지 IP 를 표시하지 않습니다(2026년 9월 문서 기준)[19]. 기업 소유자가 표시를 켜면 새 이벤트와 이미 있던 이벤트 모두에 IP 가 나타나고, 조직 단위로 따로 켤 수도 있습니다[19]. 켜더라도 기업이나 그 조직이 소유한 자원과 상호 작용한 이벤트에만 IP 가 나오고, 저장소 맥락이 없는 `api.request` 이벤트, 기록된 행위자와 실제 수행 주체가 다른 일부 이벤트, 봇·자동화 시스템이 한 작업에는 IP 가 나오지 않습니다[19].

### 서비스가 넣어 주는 위치 값

IP 주소와 컴퓨터가 놓인 물리적 위치 사이에는 확정된 연결이 없습니다[9]. 이동 통신사와 VPN 은 기기와 먼 곳의 중앙 주소 풀에서 IP 를 나눠 주고, IP 를 위치로 바꾸는 일은 경로 추적·등록 정보·역방향 조회 같은 자료를 모은 최선의 추정입니다[9]. `SigninLogs` 의 `Location` 은 IP 에 따라 도시·지역 수준까지 풀리지 않을 수 있습니다[7]. Slack 액세스 로그의 `isp`·`country`·`region` 도 IP 로 짐작한 값입니다[15].

Okta 의 `geographicalContext` 는 `Transaction` 의 `type` 이 `WEB` 인 이벤트에만 들어가고 `JOB` 인 이벤트에는 없으며, 위치를 풀 수 없는 요청에서는 빠질 수 있습니다[14]. Okta `securityContext` 는 IP 평판 평가 정보이고, 그 안의 `isProxy` 는 알려진 프록시에서 온 요청인지를 표시합니다[14]. Google Cloud VPC 흐름 로그의 `src_location`·`dest_location` 은 상대가 VPC 네트워크 밖의 공인 IP 일 때만 채워집니다[12].

아래는 Okta 레코드 가운데 IP·위치 부분만 보인 만든 예시입니다.

```json
"client": {
  "ipAddress": "198.51.100.40",
  "userAgent": {"rawUserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "browser": "CHROME", "os": "Windows 10"},
  "geographicalContext": {"city": "Example City", "state": "Example State", "country": "Example Country",
                          "geolocation": {"lat": 0.0, "lon": 0.0} }
},
"request": {"ipChain": [{"ip": "198.51.100.40"}, {"ip": "192.0.2.10"}]},
"securityContext": {"asNumber": 64500, "asOrg": "example isp", "isp": "example isp", "domain": "example.com", "isProxy": false}
```

### 사용자 에이전트 읽기

사용자 에이전트는 클라이언트가 보내는 값입니다. 통합 감사 로그의 `UserAgent` 는 클라이언트나 브라우저가 제공하는 정보이고[10], Google Cloud 의 `callerSuppliedUserAgent` 는 인증되지 않은 값이라 그에 맞게 다뤄야 합니다[11]. CloudTrail `userAgent` 에는 `aws-cli/…`, `aws-sdk-java` 처럼 호출 수단이 드러나고, 1 KB 를 넘는 내용은 잘립니다[1].

UA 에 도구 이름이 남으면 공개 탐지 규칙으로 찾을 수 있습니다.

| 로그 | 조건(Sigma 규칙) | 가리키는 흔적 |
|---|---|---|
| CloudTrail | `userAgent` 가 `TruffleHog` | 비밀 정보 검색 도구 실행, 보안 팀의 정상 사용일 수 있음[23] |
| CloudTrail | `eventSource: iam.amazonaws.com`, `eventName` 이 `CreateUser`·`CreateAccessKey`, `userAgent` 에 `S3 Browser` 포함 | S3 Browser 로 IAM 사용자·액세스 키를 만듦[24] |
| CloudTrail | `userIdentity.arn` 이 `…:assumed-role/aws:…` 형태인데 `sourceIPAddress` 가 `AWS Internal` 이 아님(`ssm.amazonaws.com`·`RegisterManagedInstance` 제외) | 인스턴스 메타데이터 자격 증명을 AWS 밖에서 썼을 가능성[25] |
| Entra `SigninLogs` | `userAgent` 에 `azurehound` 포함, `ResultType: 0` | AzureHound 로 탐색함[26] |
| Entra `SigninLogs` | `AuthenticationRequirement: singleFactorAuthentication`, `ResultType: 0`, `NetworkLocationDetails: '[]'`, `DeviceDetail.deviceId` 빈 값 | 알 수 없는 기기에서 단일 요소 인증으로 로그인 성공[27] |
| Okta | `eventType: user.session.start`, `securityContext.isProxy: 'true'` | 익명화 프록시를 거쳐 세션 시작[28] |
| Okta | `debugContext.debugData.requestUri` 에 `admin` 포함, `securityContext.isProxy: 'true'` | 프록시를 거쳐 관리 기능에 접근[29] |

## 포렌식에서 중요한 점

### 증명하는 것

- 로그의 IP 는 그 서비스가 본 연결의 출발지, 또는 서비스가 정한 대체 값(`AWS Internal`, `private` 등)까지를 보여 줍니다[1][11].
- 같은 계정의 레코드에서 IP·ASN·UA 조합이 바뀐 시점은 접속 환경이 바뀐 시점의 단서가 됩니다.
- UA 에 도구 이름이 들어 있으면 그 도구, 또는 그 UA 를 흉내 낸 클라이언트로 호출했다는 강한 단서입니다.

### 증명하지 못하는 것

- IP 는 사람이 있던 위치나 기기의 소유자를 증명하지 못합니다. VPN·프록시·이동 통신망 주소일 수 있습니다[9][13].
- 국가·도시 값은 서비스가 기록할 때 붙인 추정값입니다. 같은 IP 를 나중에 다른 데이터베이스로 조회하면 결과가 다를 수 있습니다.
- UA 가 평범한 브라우저 문자열이라고 해서 사람이 브라우저로 작업했다는 증명이 되지는 않습니다. UA 는 호출하는 쪽이 정해서 보냅니다[11].

### 시각과 위치 값

로그에 들어 있는 위치·ASN·프록시 표시는 서비스가 요청을 받을 무렵 IP 로 판정한 값이라, 같은 IP 를 나중에 조회한 결과와 다를 수 있습니다. 도구로 붙인 위치는 조회한 날의 데이터베이스 결과이므로, 보고서에는 조회 날짜와 조회 수단을 함께 적고 로그 원본 값과 다른 열로 둡니다. 레코드의 시각 필드와 지연 시간은 [클라우드 로그의 시각](timestamps.md)에서 다룹니다.

### 지우기·조작

UA 는 호출하는 쪽이 마음대로 정할 수 있어 조작에 약합니다. 서비스가 판정한 IP·ASN·위치는 호출자가 직접 쓰는 값이 아니지만, VPN·프록시·클라우드 서버를 거치면 그 출구 주소가 남습니다. 그래서 IP 하나보다 ASN·`isProxy`·로그인 방식·기기 정보를 함께 봅니다. 보고서 문장은 "이 계정으로 이 IP 에서 로그인한 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다([클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)).

## 함정

- 통합 감사 로그의 Entra ID 관련 레코드는 `ClientIP` 가 null 이라, 로그인 IP 는 [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md)의 로그인 로그에서 봅니다[10].
- Entra 로그인 로그에서 같은 위치 정보가 경로마다 이름과 깊이가 다릅니다. Graph v1.0 `location` 은 도시·주·국가 코드이고, `SigninLogs` 는 `Location`(2글자 국가 코드)과 `LocationDetails`(위도·경도 포함)로 나뉩니다[5][7]. `userAgent`·`autonomousSystemNumber` 는 v1.0 에 없고 beta 와 `SigninLogs` 에만 있습니다[5][6][7].
- Slack 감사 로그의 `context.location` 은 이벤트가 일어난 엔터프라이즈나 워크스페이스를 가리키는 값이고(`type`, `id` 등) 지리 위치가 아닙니다[17].
- Slack 액세스 로그는 사용자·IP·UA 조합마다 `date_first`·`date_last`·`count` 로 묶여 있어, 접속 한 번마다의 목록이 아닙니다[15]. Enterprise 플랜의 워크스페이스 단위 액세스 로그에는 모바일 세션·웹 클라이언트 방문·서드파티 앱 동작이 다 나오지 않습니다[16]. 자세한 내용은 [Slack 감사 로그](../../02-artifacts/saas/slack.md)에 있습니다.
- Okta `request.ipChain[]` 안의 첫 주소와 `client.ipAddress` 를 함께 봐야 프록시를 거친 요청을 가릴 수 있습니다[14]. Okta 필드 전체는 [Okta 시스템 로그](../../02-artifacts/saas/okta.md)에서 다룹니다.
- 국가 코드 형식이 2글자·3글자·전체 이름으로 섞여 있어, 그대로 합쳐 세면 같은 나라가 다른 나라로 잡힙니다.
- VPC 흐름 로그는 만든 뒤 필드를 바꿀 수 없어, `pkt-srcaddr`·`pkt-dstaddr` 가 없는 흐름 로그에서는 중간 계층 뒤의 원래 주소를 알 수 없습니다[3]. 필드 목록은 [AWS VPC 흐름 로그](../../02-artifacts/aws/vpc-flow-logs.md)에 있습니다.

## 도구

- Hawk 의 `Get-HawkUserUALSignInLog -ResolveIPLocations` 는 통합 감사 로그의 로그인 레코드 IP 를 외부 위치 조회 서비스로 찾아 `CountryName`·`RegionCode`·`RegionName`·`City` 열을 붙이고, Microsoft 소유 IP 인지를 `KnownMicrosoftIP` 로 표시합니다[21]. 이 열은 조회 시점의 결과이므로 원본 값과 구분해 둡니다.
- Microsoft-Extractor-Suite 의 `Get-UALGraph` 는 Graph 감사 로그 검색 결과에서 `clientIp` 를 CSV 열로 뽑습니다[22].
- 위 표의 UA·프록시 조건은 SigmaHQ 규칙[23]~[29]에서 옮긴 것이라, 규칙을 그대로 로그를 검색하는 출발점으로 쓸 수 있습니다. 규칙을 로그에 적용하는 법은 [탐지 규칙으로 로그 검색하기](../../03-techniques/analysis/detection-rules.md)에 있습니다.
- 서비스마다 필드가 다른 레코드를 한 표로 모을 때는 IP·UA·국가 열을 이 페이지의 필드 표대로 이름을 맞춘 뒤 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)에 넣습니다.

## 참고 문헌

1. AWS, "CloudTrail record contents for management, data, and network activity events", https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
2. AWS, "Logging IP traffic using VPC Flow Logs — Flow log records", https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html
3. AWS, "Flow log limitations", https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-limitations.html
4. Microsoft, "Azure activity log event schema" (activity-log-schema.md, ms.date 2026-03-17), https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
5. Microsoft, "signIn resource type" (Microsoft Graph v1.0), https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-1.0
6. Microsoft, "signIn resource type" (Microsoft Graph beta), https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
7. Microsoft, "SigninLogs table" (Azure Monitor Logs reference), https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
8. Microsoft, "Non-interactive user sign-ins" (concept-noninteractive-sign-ins.md, ms.date 2026-02-09), https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-noninteractive-sign-ins.md
9. Microsoft, "Sign-in log activity details" (concept-sign-in-log-activity-details.md, ms.date 2026-03-04), https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
10. Microsoft, "Office 365 Management Activity API schema", https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
11. Google Cloud, "AuditLog" (Cloud Audit Logs type reference), https://cloud.google.com/logging/docs/reference/audit/auditlog/rest/Shared.Types/AuditLog
12. Google Cloud, "About VPC Flow Logs records", https://cloud.google.com/vpc/docs/about-flow-logs-records
13. Google, "Activities: list" (Admin SDK Reports API), https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
14. Okta, Management API OpenAPI 명세 2025.08.0(LogEvent·LogClient·LogGeographicalContext·LogRequest·LogSecurityContext·LogUserAgent), https://github.com/okta/okta-management-openapi-spec/blob/master/dist/2025.08.0/management-minimal.yaml
15. Slack, "team.accessLogs", https://api.slack.com/methods/team.accessLogs
16. Slack, "View access logs for your workspace", https://slack.com/help/articles/360002084807-View-access-logs-for-your-workspace
17. Slack, "Audit Logs API", https://api.slack.com/admins/audit-logs
18. GitHub, "Exporting audit log activity for your enterprise", https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/exporting-audit-log-activity-for-your-enterprise
19. GitHub, "Displaying IP addresses in the audit log for your enterprise", https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/displaying-ip-addresses-in-the-audit-log-for-your-enterprise
20. Dropbox, dropbox-api-spec `team_log.stone`(`GeoLocationLogInfo`), https://github.com/dropbox/dropbox-api-spec/blob/master/team_log.stone
21. T0pCyber, Hawk `Get-HawkUserUALSignInLog.ps1`, https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/User/Get-HawkUserUALSignInLog.ps1
22. Invictus IR, Microsoft-Extractor-Suite `Get-UALGraph.ps1`, https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-UALGraph.ps1
23. SigmaHQ, "PUA - AWS TruffleHog Execution", https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_pua_trufflehog.yml
24. SigmaHQ, "AWS IAM S3Browser User or AccessKey Creation", https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_iam_s3browser_user_or_accesskey_creation.yml
25. SigmaHQ, "Malicious Usage Of IMDS Credentials Outside Of AWS Infrastructure", https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_imds_malicious_usage.yml
26. SigmaHQ, "Discovery Using AzureHound", https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/signin_logs/azure_ad_azurehound_discovery.yml
27. SigmaHQ, "Sign-ins by Unknown Devices", https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/signin_logs/azure_ad_sign_ins_from_unknown_devices.yml
28. SigmaHQ, "Okta User Session Start Via An Anonymising Proxy Service", https://github.com/SigmaHQ/sigma/blob/master/rules/identity/okta/okta_user_session_start_via_anonymised_proxy.yml
29. SigmaHQ, "Okta Admin Functions Access Through Proxy", https://github.com/SigmaHQ/sigma/blob/master/rules/identity/okta/okta_admin_activity_from_proxy_query.yml
30. GitHub, "Audit log events for your enterprise", https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/audit-log-events-for-your-enterprise
