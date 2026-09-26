---
title: "액세스 키가 새어 나갔나"
parent: "시나리오 · 인프라 침해"
nav_order: 770
---

# 액세스 키가 새어 나갔나 (Leaked Access Keys)

AWS 액세스 키, Microsoft Entra 앱 비밀·인증서, Azure Storage 계정 키·SAS, Google Cloud 서비스 계정 키처럼 사람 대신 프로그램이 쓰는 자격 증명이 원래 주인 밖에서 쓰였는지를 로그로 가려내는 순서를 다룹니다.

## 조사 질문

- 이 키(또는 서비스 계정 키·앱 비밀)가 원래 쓰던 시스템 밖에서 쓰였나?
- 처음 쓰인 때는 언제이고, 마지막으로 쓰인 때는 언제인가?
- 어느 IP·사용자 에이전트 (User Agent) 에서 어떤 API 를 불렀나?
- 그 키로 새 키·새 사용자·새 자격 증명을 만들어 발판을 넓혔나?
- 서비스 공급자가 노출이나 오용을 감지해 표시하거나 키를 막았나?

키가 어디서 새어 나갔는지(개발자 PC, 코드 저장소, CI 설정 파일)는 클라우드 로그 밖의 질문입니다. 로그가 답하는 것은 "이 키로 서명한 요청이 언제 어디서 무엇을 불렀나" 까지입니다.

## 먼저 확인할 것

**키의 정체부터 정합니다.** AWS 액세스 키 ID 가 `AKIA` 로 시작하면 IAM 사용자나 루트 사용자의 장기 자격 증명이고, `ASIA` 로 시작하면 STS 가 만든 임시 자격 증명입니다[1][2]. 키 ID 하나만 있으면 STS 의 `GetAccessKeyInfo` API 로 그 키가 속한 AWS 계정 ID 를 알 수 있지만, 이 API 는 키가 활성인지·비활성인지·삭제됐는지는 알려 주지 않고, 삭제된 키에는 "없다" 는 오류를 돌려줄 수 있습니다[2]. 계정이 조사 대상 조직의 것이면 자격 증명 보고서 (credential report) 로 어느 IAM 사용자의 키인지 찾고, `ASIA` 키는 CloudTrail 의 STS 이벤트로 누가 요청했는지 찾습니다[2]. Google Cloud 서비스 계정 키는 키 ID 와 서비스 계정 이메일을, Entra 앱은 애플리케이션 ID 와 자격 증명의 키 ID 를 먼저 적어 둡니다. 키 파일과 키 메타데이터의 모양은 [IAM과 서비스 계정 키](../../02-artifacts/gcp/iam-keys.md) 에 있습니다.

**기록이 남는 기간과 켜진 로그를 확인합니다.** 키 유출은 알아챈 날보다 훨씬 전에 시작된 경우가 많아서, 보관 기간이 먼저 끝나 버리면 처음 쓰인 때를 잃습니다. 로그부터 확보하는 방법은 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 에 있습니다. 아래 표는 2026년 9월 문서 기준입니다(서비스별 전체 표는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)).

| 서비스 | 키 사용을 보여 주는 기록 | 기본으로 남나 | 기본 보관 |
|---|---|---|---|
| AWS | CloudTrail 관리 이벤트 | 이벤트 기록 (Event history) 에 남음. 트레일·이벤트 데이터 저장소는 기본으로 관리 이벤트만 담고 데이터 이벤트는 따로 켜야 함[17] | 이벤트 기록 90일[16] |
| Microsoft Entra | 감사 로그, 서비스 주체 로그인 | 남음 | Free 7일, P1·P2 30일. 라이선스를 올려도 지난 기록이 되살아나지 않음[21] |
| Azure Storage | 블롭 등 데이터 평면 요청 기록 | 진단 설정을 켜야 남음([Storage 계정 기록](../../02-artifacts/azure/storage-logs.md)) | 보낸 곳의 설정을 따름 |
| Google Cloud | 관리 활동 감사 로그, 데이터 접근 감사 로그 | 관리 활동은 남음. 데이터 접근 감사 로그는 일부 BigQuery 서비스 말고는 기본으로 꺼져 있음[31] | 로그 버킷 설정을 따름([Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md)) |
| GitHub | 조직·엔터프라이즈 감사 로그 | 남음 | 최근 180일, Git 이벤트는 7일[32] |
| Okta | 시스템 로그 | 남음 | 90일이 넘은 기록은 API 가 돌려주지 않음[35] |

**대응 조치가 이미 있었는지 묻습니다.** 키를 끄거나, 세션을 끊거나, 거부 정책을 붙인 조치도 같은 로그에 남습니다. 대응자가 언제 무엇을 했는지 먼저 받아 두어야 타임라인에서 공격자의 호출과 대응자의 호출을 나눌 수 있습니다. 로그의 시각은 대부분 UTC 이고 서비스마다 늦게 들어오는 정도가 다르므로 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 을 함께 봅니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 공급자의 유출 표시: GuardDuty 결과, Entra 워크로드 ID 위험 검색, Google Cloud 키의 `disableReason`·`extendedStatus`, SCC 결과 | 공급자가 노출이나 오용을 감지했는지, 감지한 시각과 쓰인 키 | [GuardDuty](../../02-artifacts/aws/guardduty.md), [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [IAM과 서비스 계정 키](../../02-artifacts/gcp/iam-keys.md) |
| 2 | 키의 요약 정보: AWS 자격 증명 보고서·`GetAccessKeyLastUsed`, Google Cloud Activity Analyzer | 키가 아직 유효한지, 마지막으로 쓰인 날짜와 서비스·리전 | [IAM](../../02-artifacts/aws/iam.md), [IAM과 서비스 계정 키](../../02-artifacts/gcp/iam-keys.md) |
| 3 | 키 ID 로 거른 호출 기록: CloudTrail `userIdentity.accessKeyId`, Entra 로그인의 `servicePrincipalCredentialKeyId`, Google Cloud `serviceAccountKeyName`, Storage 로그의 키 해시 | 이 키로 서명한 요청이 언제·어디서·무엇을 불렀나 | [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md), [Storage 계정 기록](../../02-artifacts/azure/storage-logs.md), [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md) |
| 4 | 키로 만든 다른 자격 증명: STS `AssumeRole`·`GetSessionToken` 응답, `CreateAccessKey`, 서비스 주체 자격 증명 추가, `CreateServiceAccountKey`, `GenerateAccessToken` | 새어 나간 키에서 이어진 두 번째·세 번째 키 | [토큰과 세션](../../01-foundations/identity/tokens-sessions.md), [권한을 올렸나](privilege-escalation.md) |
| 5 | 키를 쓴 뒤의 자원 변화: 인스턴스·함수 생성, 로그 설정 변경 | 키로 한 일의 결과 | [채굴용 자원을 만들었나](cryptomining.md), [로그를 끄거나 지웠나](log-tampering.md) |
| 6 | 키가 새는 곳의 기록: GitHub 감사 로그, Okta 시스템 로그 | 비밀 검사를 끄거나 우회했는지, SaaS API 토큰을 만들었는지 | [GitHub 감사 로그](../../02-artifacts/saas/github.md), [Okta 시스템 로그](../../02-artifacts/saas/okta.md) |

## 분석 흐름

1. **공급자의 표시를 먼저 모읍니다.** AWS 에서는 GuardDuty 의 `CredentialAccess:IAMUser/CompromisedCredentials` 가 Amazon 위협 인텔리전스가 유출 가능성을 식별한 IAM 액세스 키가 API 호출에 쓰였다는 결과이고, 결과 상세에 호출한 API 목록과 호출별 횟수·시각, 쓰인 액세스 키, 출발지 IP 가 들어 있습니다[10]. EC2 인스턴스 역할용 임시 자격 증명이 AWS 밖 IP 에서 쓰이면 `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS`, 다른 AWS 계정의 IP 나 VPC 엔드포인트에서 쓰이면 `...InsideAWS` 가 나오고, 뒤의 것은 `remoteAccountDetails.Affiliated` 필드로 같은 관리자 계정에 묶인 계정인지를 알려 줍니다[10]. 결과의 Resource 부분에서 User Type·User name·Access key ID 를 적고, 역할이면 CloudTrail 의 `sessionIssuer` 로 그 키를 어떻게 받았는지 봅니다[11]. Entra 에서는 워크로드 ID 위험 검색의 `Leaked Credentials`(`riskEventType` 값 `leakedCredentials`)가 GitHub 공개 코드·다크 웹·붙여넣기 사이트 등에서 얻은 자격 증명이 Entra ID 의 현재 유효한 자격 증명과 일치한다는 뜻이고, 전체 상세는 Workload Identities Premium 라이선스가 있어야 보입니다[20]. Google Cloud 에서는 조직 정책 `iam.serviceAccountKeyExposureResponse` 가 `DISABLE_KEY` 이면 노출된 키를 자동으로 끄고 감사 로그 이벤트를 만들며, 2024년 6월 16일부터는 값을 정하지 않아도 이렇게 동작합니다[27]. 이때 감사 로그에서 키를 끈 주체는 `gcp-compromised-key-response@system.gserviceaccount.com` 이고, 키의 `extendedStatus.value` 에 유출을 감지한 위치가 적힙니다[27]. 키 메타데이터의 `disableReason` 이 `SERVICE_ACCOUNT_KEY_DISABLE_REASON_EXPOSED` 이면 노출 감지로, `..._COMPROMISE_DETECTED` 이면 공격자가 쓴 것을 감지해서 꺼진 키입니다[28]. Security Command Center 의 Event Threat Detection 결과 `Account_Has_Leaked_Credentials` 는 서비스 계정 키가 GitHub 에 새어 나갔다는 결과입니다[30].

2. **AWS 격리 정책이 붙었는지 봅니다.** 관리형 정책 `AWSCompromisedKeyQuarantineV3` 은 IAM 사용자 자격 증명이 유출되었거나 공개적으로 노출되었을 때 AWS 가 붙이는 거부 정책이고, 설명에는 이 정책을 지우지 말고 AWS 가 연 지원 사례 (support case) 의 안내를 따르라고 적혀 있습니다[9]. 이 정책은 `ec2:RunInstances`, `iam:CreateAccessKey`, `iam:CreateUser`, `iam:PassRole`, `lambda:CreateFunction`, `organizations:CreateAccount`, `s3:GetObject`, `sts:GetSessionToken`, `cloudtrail:LookupEvents` 같은 동작을 막습니다(버전 v3, 2026년 3월 16일 수정)[9]. 사용자·그룹·역할에 이 정책이 붙어 있으면 AWS 가 노출을 감지해 붙였을 가능성이 있으므로 지원 사례를 확인하고, 붙은 시각을 CloudTrail 에서 `AttachUserPolicy` 같은 정책 연결 이벤트로 찾습니다.

3. **요약 정보로 범위를 잡습니다.** IAM `GetAccessKeyLastUsed` 는 키가 마지막으로 쓰인 날짜·시각과 그 요청의 서비스 이름·리전, 키 주인의 사용자 이름을 돌려줍니다[3]. 자격 증명 보고서의 `access_key_N_active`, `access_key_N_last_rotated`, `access_key_N_last_used_date`, `access_key_N_last_used_region`, `access_key_N_last_used_service` 도 같은 요약을 사용자 전체에 대해 보여 줍니다[4]. Google Cloud 에서는 Activity Analyzer 의 `serviceAccountKeyLastAuthentication` 으로 키별 마지막 인증 시각(`lastAuthenticatedTime`)을 봅니다. 서비스 계정에 묶인 API 키로 인증한 요청은 서비스 계정 사용 기록에 남지 않고, Workspace API 도메인 전체 위임처럼 Google Cloud 밖에서 Google API 에 인증한 활동은 Activity Analyzer 가 추적하지 않습니다[29]. 두 요약 모두 마지막 한 번만 보여 주므로 처음 쓰인 때와 횟수는 다음 단계의 호출 기록에서 셉니다. 요약 필드의 세부(갱신 주기, 추적 시작 날짜)는 [IAM](../../02-artifacts/aws/iam.md) 과 [IAM과 서비스 계정 키](../../02-artifacts/gcp/iam-keys.md) 에 있습니다.

4. **키 ID 로 호출 기록을 거릅니다.** CloudTrail 의 `userIdentity.accessKeyId` 는 요청 서명에 쓴 키 ID 이고, 임시 자격 증명으로 한 요청이면 임시 키 ID 가 들어갑니다[5]. 거른 결과를 `eventTime` 순으로 늘어놓고 `sourceIPAddress`, `userAgent`, `eventSource`, `eventName`, `errorCode` 를 봅니다. 평소 그 키를 쓰던 서버의 IP·사용자 에이전트와 다른 줄이 처음 나타난 시각이 "원래 주인 밖에서 쓰인" 첫 기록 후보입니다. IP 와 사용자 에이전트를 읽는 법은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md) 에 있습니다. 아래는 만든 예시 레코드(필드만 남김)입니다.

   ```json
   {
     "eventTime": "2026-09-01T03:12:45Z",
     "eventSource": "sts.amazonaws.com",
     "eventName": "GetCallerIdentity",
     "sourceIPAddress": "203.0.113.25",
     "userAgent": "example-scanner/1.0",
     "userIdentity": {
       "type": "IAMUser",
       "accountId": "123456789012",
       "userName": "build-bot",
       "accessKeyId": "AKIAIOSFODNN7EXAMPLE"
     }
   }
   ```

   `sts:GetCallerIdentity` 는 권한이 없어도 부를 수 있고, 명시적 거부 정책이 붙어 있어도 부를 수 있습니다[6]. 그래서 새어 나간 키가 아직 유효한지 확인하는 첫 호출로 이 이벤트가 나올 수 있습니다. Sigma 규칙 `aws_sts_getcalleridentity_trufflehog` 는 `eventSource` 가 `sts.amazonaws.com`, `eventName` 이 `GetCallerIdentity` 이고 `userAgent` 에 `TruffleHog` 가 들어간 레코드를 찾고, `aws_cloudtrail_pua_trufflehog` 는 `userAgent` 가 `TruffleHog` 인 레코드를 찾습니다(두 규칙 모두 experimental)[12][13]. Entra 에서는 서비스 주체 로그인의 `servicePrincipalCredentialKeyId`(인증에 쓴 키 자격 증명 ID)와 `servicePrincipalCredentialThumbprint`(인증서 지문), `clientCredentialType`(`clientSecret`, `certificate`, `clientAssertion` 등)으로 어느 비밀·인증서가 쓰였는지 좁힙니다[19]. Google Cloud 에서는 대상 서비스 감사 로그의 `authenticationInfo.serviceAccountKeyName` 이 `//iam.googleapis.com/projects/PROJECT/serviceAccounts/EMAIL/keys/KEY_ID` 모양으로 키를 가리킵니다[26]. Azure Storage 에서는 요청 기록의 인증 방식이 계정 키일 때 토큰 해시가 `key1(SHA-256)` 이나 `key2(...)` 모양이라 어느 계정 키였는지 드러나고, SAS 면 `key1(...),SasSignature(...)` 모양으로 SAS 서명의 해시가 함께 남습니다[24]. 세부 필드와 쿼리는 [Storage 계정 기록](../../02-artifacts/azure/storage-logs.md) 에 있습니다.

5. **새어 나간 키에서 이어진 자격 증명을 따라갑니다.** AWS 에서 장기 키로 `AssumeRole`·`GetSessionToken` 을 부르면 응답의 `responseElements.credentials.accessKeyId` 에 `ASIA` 로 시작하는 임시 키가 나오고, 그 뒤의 호출은 이 임시 키로 찍힙니다[5][38]. 두 API 모두 CloudTrail 레코드에 응답 요소가 들어가고, `AssumeRole` 은 `secretAccessKey` 만 빼고 남깁니다[38]. 그러니 임시 키 ID 를 다시 검색어로 넣어 호출 기록을 이어 붙입니다. 다른 사용자에게 새 액세스 키를 만든 흔적은 `iam.amazonaws.com` 의 `CreateAccessKey` 이벤트에서 `userIdentity.arn` 이 `responseElements.accessKey.userName` 을 포함하지 않는 레코드로 찾습니다(Sigma `aws_iam_backdoor_users_keys`)[14]. Entra 에서는 감사 로그 범주 ApplicationManagement 의 `Add service principal credentials`, `Update application - Certificates and secrets management` 가 앱·서비스 주체에 비밀이나 인증서를 더한 기록입니다[18][36]. Google Cloud 에서는 관리 활동 로그의 `google.iam.admin.v1.CreateServiceAccountKey` 가 키 생성이고, `authenticationInfo.principalEmail` 이 만든 주체입니다[26]. 서비스 계정 가장 (impersonation) 으로 받은 단기 토큰은 `iamcredentials.googleapis.com` 의 `GenerateAccessToken` 으로 데이터 접근 로그에 남는데, IAM 데이터 접근 로그를 켜 두었을 때만 남습니다[26]. 권한이 바뀐 기록을 읽는 법은 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md) 에 있습니다.

6. **키로 한 일의 결과를 봅니다.** 인스턴스·함수를 만들었으면 [채굴용 자원을 만들었나](cryptomining.md), 트레일·진단 설정을 건드렸으면 [로그를 끄거나 지웠나](log-tampering.md), 저장소에서 객체를 읽었으면 [클라우드 저장소에서 자료를 빼 갔나](../data-leak/storage-exfiltration.md) 로 넘어갑니다. 키가 가상 머신 안의 파일에서 새어 나간 것으로 보이면 그 디스크를 확보해 키 파일과 셸 기록을 봅니다([[linux] 클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html)).

7. **키가 새는 곳과 SaaS 토큰을 확인합니다.** GitHub 감사 로그에서 action 에 `secret_scanning_push_protection.bypass` 가 들어간 이벤트는 비밀이 들어간 푸시가 푸시 보호를 우회한 기록이고, `secret_scanning.disable`·`repository_secret_scanning.disable`·`business_secret_scanning.disable`·`secret_scanning_new_repos.disable` 은 비밀 검사를 끈 기록입니다[33][34]. 두 Sigma 규칙은 감사 로그 스트리밍으로 받은 로그를 대상으로 합니다[33][34]. Okta 에서는 `system.api_token.create` 가 API 토큰 생성, `system.api_token.revoke` 가 취소, `system.api_token.request_outside_allowed_range` 가 허용한 네트워크 영역 밖 IP 에서 API 토큰으로 요청한 기록입니다[37].

8. **대응자의 조치를 표시하고 타임라인을 닫습니다.** IAM 콘솔에서 역할의 세션을 끊으면 `AWSRevokeOlderSessions` 인라인 정책이 붙고, 이 정책은 `aws:TokenIssueTime` 이 지정 시각(약 30초 뒤까지 포함)보다 이른 세션을 모두 거부합니다[8]. 이 조치는 역할에 인라인 정책을 넣는 것이라 `PutRolePolicy` 권한이 필요하므로[8], CloudTrail 에서 `PutRolePolicy` 이벤트로 찾으면 됩니다. 대응자가 만든 이런 레코드와 격리 정책 연결 레코드를 표시해 두고, 그 뒤에 `AccessDenied` 로 실패한 공격자 호출이 이어지는지 봅니다. 여러 로그를 한 줄로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다.

## 흔한 오판

- **"키를 지웠으니 그 뒤 기록은 공격자가 아니다."** 장기 키를 끄거나 지워도, 그 키로 이미 받은 임시 자격 증명은 만료 때까지 쓸 수 있습니다. 임시 자격 증명의 수명은 900초에서 129,600초(36시간) 사이이고 기본값은 43,200초(12시간)이며, 쓰임을 멈추려면 사용자나 역할의 권한을 바꿔야 합니다[7]. 루트 사용자로 로그인해 `GetFederationToken`·`GetSessionToken` 으로 받은 자격 증명은 권한을 바꿀 수도 없습니다[7].
- **"`AKIA` 키로 검색했더니 수상한 호출이 몇 건 없다."** 임시 키는 세션마다 ID 가 달라서, 장기 키에서 `AssumeRole`·`GetSessionToken` 으로 넘어간 뒤의 호출은 `AKIA` 로 검색하면 빠집니다[5][38]. `accessKeyId` 는 보안상 비어 있거나 빈 문자열로 찍힐 수도 있으므로, 키 ID 로 걸리지 않는 레코드는 `userIdentity.arn`·`sessionContext` 로 한 번 더 찾습니다[5].
- **"GuardDuty 결과가 없으니 유출은 없었다."** 인스턴스 자격 증명 유출 결과는 같은 원격 계정(`InsideAWS`)이나 원격 호스트(`OutsideAWS`)에서 활동이 계속되면 머신 러닝 모델이 정상으로 학습해 더는 그 계정·호스트에 대한 결과를 만들지 않습니다[10]. GuardDuty 를 켜기 전의 호출에는 당연히 결과가 없습니다.
- **"`serviceAccountKeyName` 이 없으니 그 키는 쓰이지 않았다."** App Engine·Compute Engine 처럼 키 이름을 기록하지 않는 서비스가 있습니다[26]. 단기 토큰 생성도 IAM 데이터 접근 로그를 켜지 않았으면 남지 않습니다[26].
- **"Entra 로그인 기록에 서비스 주체 로그인이 없다."** Graph 로그인 API 는 필터를 주지 않으면 대화형 로그인만 돌려주고, 사용자 로그인과 서비스 주체 로그인을 한 필터로 함께 받는 것도 지원하지 않습니다[19]. Microsoft-Extractor-Suite 의 `Get-GraphEntraSignInLogs` 는 `servicePrincipal` 을 따로 골라 받을 수 있습니다[22].
- **"SAS 발급 기록을 찾으면 누가 받았는지 안다."** SAS 토큰은 클라이언트 쪽에서 만드는 문자열이라 Azure Storage 가 발급을 추적하지 않고, 몇 개를 만들었는지 알려 주는 API 도 없습니다[25]. 활동 로그에 남는 것은 계정 키를 받아 간 `Microsoft.Storage/storageAccounts/listkeys/action` 같은 제어 평면 작업이고[23], 새어 나간 SAS 는 가진 사람 누구나 씁니다.
- **"탐지 도구 결과가 서로 같다."** 같은 이름의 규칙도 도구마다 번역이 다릅니다. Sigma `aws_iam_backdoor_users_keys` 는 두 필드의 값을 비교(`fieldref`)하지만[14], Invictus-AWS 의 같은 이름 쿼리는 `userIdentity.arn LIKE '%userName%'` 로 번역되어 글자 `userName` 을 찾습니다[15]. 규칙을 쓰기 전에 실제 조건을 열어 봅니다([탐지 규칙으로 로그 검색하기](../../03-techniques/analysis/detection-rules.md)).

## 보고서 문장 예

- "2026년 9월 1일 03:12:45(UTC)에 액세스 키 ID AKIAIOSFODNN7EXAMPLE 로 서명한 `GetCallerIdentity` 요청이 IP 203.0.113.25 에서 들어온 기록이 CloudTrail 에 있다. 같은 키가 그 전 30일 동안 쓰인 IP 에는 이 주소가 없다." (만든 예시)
- "이 키로 부른 `AssumeRole` 의 응답에서 임시 키 ASIAIOSFODNN7EXAMPLE 이 발급되었고, 이 임시 키로 서명한 요청이 같은 날 04:05(UTC)까지 이어진 기록이 있다." (만든 예시)
- "GuardDuty 결과 `CredentialAccess:IAMUser/CompromisedCredentials` 가 이 키에 대해 생성되어 있다. 이 결과는 AWS 가 유출 가능성을 식별한 키가 API 호출에 쓰였다는 뜻이며, 키가 새어 나간 경로는 알려 주지 않는다."
- 쓰지 않을 문장: "공격자가 키를 훔쳐 자료를 가져갔다." 로그는 키로 서명한 요청이 있었다는 것까지 보여 주고, 누가 어떤 경로로 키를 얻었는지와 데이터 이벤트를 켜지 않은 서비스에서 무엇을 읽었는지는 보여 주지 않습니다.

## 함께 볼 페이지

- 같은 분류: [권한을 올렸나](privilege-escalation.md), [채굴용 자원을 만들었나](cryptomining.md), [로그를 끄거나 지웠나](log-tampering.md)
- 사람 계정의 토큰이 새어 나간 경우: [토큰을 훔쳐 로그인했나](../account-compromise/token-theft.md), [악성 OAuth 앱에 동의했나](../account-compromise/illicit-consent.md)
- 개념: [클라우드 계정과 역할](../../01-foundations/identity/users-roles.md), [토큰과 세션](../../01-foundations/identity/tokens-sessions.md)
- 수집: [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md), [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)
- 다른 판: [[linux] 타임라인 만들기](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html)

## 참고 문헌

1. AWS, "IAM identifiers", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html
2. AWS, "GetAccessKeyInfo", AWS Security Token Service API Reference. https://docs.aws.amazon.com/STS/latest/APIReference/API_GetAccessKeyInfo.html
3. AWS, "GetAccessKeyLastUsed", IAM API Reference. https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetAccessKeyLastUsed.html
4. AWS, "Generate credential reports for your AWS account", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_getting-report.html
5. AWS, "CloudTrail userIdentity element", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
6. AWS, "GetCallerIdentity", AWS Security Token Service API Reference. https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html
7. AWS, "Disabling permissions for temporary security credentials", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_control-access_disable-perms.html
8. AWS, "Revoke IAM role temporary security credentials", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_revoke-sessions.html
9. AWS, "AWSCompromisedKeyQuarantineV3", AWS Managed Policy Reference. https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSCompromisedKeyQuarantineV3.html
10. AWS, "GuardDuty IAM finding types", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-iam.html
11. AWS, "Remediating potentially compromised AWS credentials", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/compromised-creds.html
12. SigmaHQ, aws_sts_getcalleridentity_trufflehog.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_sts_getcalleridentity_trufflehog.yml
13. SigmaHQ, aws_cloudtrail_pua_trufflehog.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_pua_trufflehog.yml
14. SigmaHQ, aws_iam_backdoor_users_keys.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_iam_backdoor_users_keys.yml
15. Invictus Incident Response, Invictus-AWS, source/files/queries.yaml. https://github.com/invictus-ir/Invictus-AWS
16. AWS, "Working with CloudTrail event history", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
17. AWS, "Logging management events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-management-events-with-cloudtrail.html
18. Microsoft, "Microsoft Entra audit log activity reference" (reference-audit-activities.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
19. Microsoft, "signIn resource type" (Microsoft Graph beta). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
20. Microsoft, "Securing workload identities". https://learn.microsoft.com/en-us/entra/id-protection/concept-workload-identity-risk
21. Microsoft, "Microsoft Entra data retention" (reference-reports-data-retention.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
22. Invictus Incident Response, Microsoft-Extractor-Suite, Scripts/Get-AzureEntraGraphLogs.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureEntraGraphLogs.ps1
23. Microsoft, "Azure permissions for Storage". https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/storage
24. Microsoft, "Azure Blob Storage monitoring data reference". https://learn.microsoft.com/en-us/azure/storage/blobs/monitor-blob-storage-reference
25. Microsoft, "Grant limited access to Azure Storage resources using shared access signatures (SAS)". https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview
26. Google Cloud, "Example logs for service accounts". https://cloud.google.com/iam/docs/audit-logging/examples-service-accounts
27. Google Cloud, "Restrict IAM service account usage". https://cloud.google.com/resource-manager/docs/organization-policy/restricting-service-accounts
28. Google Cloud, "REST Resource: projects.serviceAccounts.keys". https://cloud.google.com/iam/docs/reference/rest/v1/projects.serviceAccounts.keys
29. Google Cloud, "View recent usage for service accounts and keys" (Activity Analyzer). https://cloud.google.com/policy-intelligence/docs/activity-analyzer-service-account-authentication
30. Google Cloud, "Cryptomining detection best practices", Security Command Center. https://cloud.google.com/security-command-center/docs/cryptomining-detection-best-practices
31. Google Cloud, "Enable Data Access audit logs". https://cloud.google.com/logging/docs/audit/configure-data-access
32. GitHub, "About the audit log for your enterprise". https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/about-the-audit-log-for-your-enterprise
33. SigmaHQ, github_push_protection_bypass_detected.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/application/github/audit/github_push_protection_bypass_detected.yml
34. SigmaHQ, github_secret_scanning_feature_disabled.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/application/github/audit/github_secret_scanning_feature_disabled.yml
35. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
36. SigmaHQ, azure_app_credential_added.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/audit_logs/azure_app_credential_added.yml
37. Okta, "Event types" (okta-event-types.csv). https://developer.okta.com/docs/okta-event-types.csv
38. AWS, "Logging IAM and AWS STS API calls with AWS CloudTrail", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/cloudtrail-integration.html
