---
title: "페더레이션과 SSO"
parent: "기반 · 계정과 인증"
nav_order: 70
---

# 페더레이션과 SSO (Federation·SSO)

페더레이션 (federation) 은 로그인 판단을 외부 ID 공급자 (identity provider, IdP) 에 맡기는 설정이라, 비밀번호와 다단계 인증 결과는 IdP 쪽 로그에 남고 클라우드 쪽에는 "IdP 가 준 어설션 (assertion)·토큰을 받아 세션을 만들었다" 는 기록과 "누가 신뢰 설정을 바꿨다" 는 기록이 남습니다.

## 이 형식을 쓰는 아티팩트

이 페이지는 파일 형식이 아니라 두 조직 사이의 신뢰 관계를 다룹니다. 싱글 사인온 (single sign-on, SSO) 으로 들어온 로그인 한 건은 두 곳에 흔적을 남깁니다. 하나는 사용자를 실제로 확인한 IdP 의 로그이고, 다른 하나는 어설션을 받아들인 서비스 공급자 (service provider, SP) 의 로그입니다. 여기에 신뢰 설정 자체를 만들고 바꾼 관리 기록이 더해집니다. 신뢰 설정이 바뀌면 클라우드는 그 IdP 가 서명한 어설션을 누구의 것이든 받아들이므로, 조사에서는 로그인 기록보다 설정 변경 기록을 먼저 확인합니다.

| 서비스 | 신뢰 설정을 바꾼 기록 | 페더레이션 로그인을 받아들인 기록 | 자세히 |
|---|---|---|---|
| Microsoft 365·Entra ID | Entra 감사 로그 Core Directory `DirectoryManagement` 범주, 통합 감사 로그 | Entra 로그인 로그의 토큰 발급자·들어온 토큰 종류 필드 | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md) |
| AWS | CloudTrail 의 IAM SAML 공급자 변경, IAM Identity Center 외부 IdP 변경 | CloudTrail `AssumeRoleWithSAML`·`AssumeRoleWithWebIdentity`, 콘솔 `ConsoleLogin` | [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md) |
| Google Cloud | IAM 감사 로그의 Workforce·Workload Identity 풀 메서드 | Cloud Audit Logs 의 `principalSubject` | [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md) |
| Google Workspace | 관리 감사의 `TOGGLE_SSO_ENABLED`·`CHANGE_SSO_SETTINGS` | 로그인 감사 `login_type` 값 `saml`, SAML 감사(`applicationName=saml`) | [로그인 기록](../../02-artifacts/google-workspace/login-audit.md), [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md) |
| Okta (IdP 쪽) | `system.idp.lifecycle.*`, `application.lifecycle.*` | `user.authentication.sso`, `user.authentication.auth_via_IDP` | [Okta 시스템 로그](../../02-artifacts/saas/okta.md) |

토큰 수명과 세션 무효화는 [토큰과 세션](tokens-sessions.md), 다단계 인증 결과 필드와 조건부 접근은 [다단계 인증과 조건부 접근](mfa-conditional-access.md), 다른 테넌트의 사용자가 홈 IdP 로 인증하고 들어오는 경계 필드는 [테넌트·구독·계정·프로젝트](../model/tenancy.md)에서 다룹니다.

## 구조

### Microsoft Entra ID — 도메인 페더레이션

Entra ID 에서는 도메인 단위로 인증 방식을 정합니다. 관리형 도메인은 Entra ID 가 직접 비밀번호를 확인하고, 페더레이션 도메인은 AD FS 같은 외부 IdP 로 사용자를 보냅니다. 이 설정을 바꾸면 Entra 감사 로그에 아래 작업이 남고, 따로 적지 않은 작업은 Core Directory 서비스의 `DirectoryManagement` 범주입니다[1].

| 작업 이름(Entra 감사 로그) | 뜻 |
|---|---|
| `Set domain authentication` | 도메인의 인증 방식(관리형·페더레이션)을 바꿈 |
| `Set federation settings on domain` | 도메인의 페더레이션 설정을 바꿈 |
| `Add unverified domain`, `Add verified domain`, `Verify domain` | 도메인을 추가하고 소유를 확인함 |
| `Update domain`, `Update Domain` | 도메인 속성을 바꿈 |
| `Remove unverified domain`, `Remove verified domain`, `Soft Delete Domain`, `Hard Delete Domain` | 도메인을 지움 |
| `Set DirSyncEnabled flag` | 디렉터리 동기화 사용 여부를 바꿈 |
| `Enable Desktop Sso for a specific domain`, `Disable Desktop Sso for a specific domain` (Application proxy 서비스, `DirectoryManagement` 범주) | 도메인의 데스크톱 SSO 를 켜거나 끔 |
| `Convert federated user to managed` (Core Directory 서비스, `UserManagement` 범주) | 페더레이션 사용자를 관리형으로 바꿈 |

통합 감사 로그 (Unified Audit Log) 에는 같은 작업이 끝에 마침표가 붙은 이름으로 남습니다. `Set domain authentication.`, `Set federation settings on domain.`, `Verify domain.`, `Update domain.`, `Set DirSyncEnabled flag.` 처럼 검색하면 됩니다[2].

Azure AD Hybrid Health 의 AD FS 서비스를 바꾼 흔적은 Azure 활동 로그의 `Administrative` 범주에 남습니다. 리소스 공급자 `Microsoft.ADHybridHealthService`, 리소스 ID 에 `AdFederationService` 가 들어간 레코드 가운데 작업 이름 `Microsoft.ADHybridHealthService/services/servicemembers/action` 은 AD FS 서비스의 서버 인스턴스를 만들거나 바꾼 것이고, `Microsoft.ADHybridHealthService/services/delete` 는 AD FS 서비스 인스턴스를 지운 것입니다[25]. 이 두 작업은 온프레미스 AD FS 서버 없이 가짜 서버 인스턴스를 등록해 AD FS 로그인 기록을 꾸민 흔적일 수 있어서 따로 찾습니다[25]. 활동 로그 자체는 [활동 로그](../../02-artifacts/azure/activity-log.md)에서 다룹니다.

### Microsoft Entra ID — 로그인 로그의 페더레이션 필드

| 필드(Graph `signIn` / Log Analytics `SigninLogs`) | 값과 뜻 |
|---|---|
| `tokenIssuerType` / `TokenIssuerType` | 토큰을 발급한 IdP 종류. `AzureAD`, `ADFederationServices`, `AzureADBackupAuth`, `ADFederationServicesMFAAdapter`, `NPSExtension`[3][4] |
| `tokenIssuerName` / `TokenIssuerName` | IdP 이름[3][4] |
| `incomingTokenType` / `IncomingTokenType` | Entra ID 에 제시된 토큰 종류. Graph 값은 `none`, `primaryRefreshToken`, `saml11`, `saml20`, `remoteDesktopToken`, `refreshToken` 등[3] |
| `authenticationProtocol` / `AuthenticationProtocol` | 인증 프로토콜. `wsFederation`, `saml20`, `oAuth2` 등[3][4] |
| `authenticationProcessingDetails` / `AuthenticationProcessingDetails` | 추가 처리 정보. PTA·PHS 면 에이전트 이름, 페더레이션 인증이면 서버·팜 이름[3][4] |
| `authenticationDetails[].authenticationMethodDetail` | 비밀번호 단계라면 비밀번호를 확인한 곳(cloud, AD FS, PTA, PHS)[5] |

액세스 토큰의 `idp` 클레임은 토큰 주체를 인증한 IdP 를 적습니다. 사용자가 발급자와 같은 테넌트에 있으면 `iss` 와 같은 값이고, 게스트처럼 다른 테넌트의 사용자면 다른 값이 들어갑니다[6]. 이 클레임은 게스트가 낀 페더레이션 도메인 시나리오에서 나오고, 관리형 도메인 시나리오에서는 늘 붙으며, 클레임이 없으면 `iss` 값을 쓰면 됩니다[6].

### AWS — IAM SAML·OIDC 공급자와 IAM Identity Center

AWS 계정 하나에 직접 페더레이션하면 IAM 에 SAML 공급자나 OIDC 공급자를 만들고, 사용자는 STS 의 `AssumeRoleWithSAML`·`AssumeRoleWithWebIdentity` 로 역할을 넘겨받습니다. 이때 CloudTrail 레코드의 `userIdentity.type` 은 아래처럼 남습니다[10][11].

| `userIdentity.type` | `principalId` | `userName` | `identityProvider` |
|---|---|---|---|
| `SAMLUser` | `saml:namequalifier` 와 `saml:sub` 를 이은 값 | `saml:sub` | `saml:namequalifier` |
| `WebIdentityUser` | 발급자, 애플리케이션 ID, 사용자 ID 를 이은 값 | 사용자 ID | 발급자 이름(예: `cognito-identity.amazon.com`, `www.amazon.com`, `accounts.google.com`, `graph.facebook.com`[10], IAM OIDC 공급자면 `arn:aws:iam::123456789012:oidc-provider/...`[11]) |

이렇게 만든 세션으로 이후에 호출한 API 는 역할 신원만 담고 사용자 신원은 담지 않습니다[11]. 그래서 사람을 좁히려면 `AssumeRoleWithSAML` 레코드의 `sourceIdentity`, `roleSessionName`, 응답의 `subject` 를 이어서 봐야 합니다.

신뢰 설정 변경은 IAM 쪽 `UpdateSAMLProvider`, `DeleteSAMLProvider`(이벤트 소스 `iam.amazonaws.com`)와 IAM Identity Center 쪽 `AssociateDirectory`, `DisassociateDirectory`, `EnableExternalIdPConfigurationForDirectory`, `DisableExternalIdPConfigurationForDirectory`(이벤트 소스 `sso-directory.amazonaws.com`·`sso.amazonaws.com`)로 찾습니다[25].

IAM Identity Center 는 CloudTrail 이벤트를 여러 이벤트 소스로 나눠 남깁니다. 권한 세트·애플리케이션·할당 관리는 `sso.amazonaws.com`, 사용자·그룹 관리는 `sso-directory.amazonaws.com`·`identitystore.amazonaws.com`, CLI·IDE 로그인에 쓰는 OIDC 는 `sso.amazonaws.com`·`sso-oauth.amazonaws.com`, 외부 IdP 가 사용자를 밀어 넣는 SCIM 프로비저닝은 `identitystore-scim.amazonaws.com` 입니다[13]. Identity Center 사용자의 로그인 자체는 공개 API 가 없는 Sign-in 이벤트로 남습니다[13]. Identity Center 사용자가 한 API 호출에는 `userIdentity.type` 이 `IdentityCenterUser` 이고 `onBehalfOf.userId`, `onBehalfOf.identityStoreArn`, `credentialId` 가 들어갑니다[10].

### Google Cloud — Workforce·Workload Identity Federation

외부 IdP 의 신원(서드파티 신원)이 호출하면 감사 로그의 `authenticationInfo.principalEmail` 대신 `principalSubject` 가 채워집니다[14]. 서비스 계정 위임 이력(`serviceAccountDelegationInfo[]`)의 `principalSubject` 는 대부분 `principal://iam.googleapis.com/{identity pool name}/subject/{subject}` 형식이고, 일부 GKE 신원(GKE_WORKLOAD, FREEFORM, GKE_HUB_WORKLOAD)은 옛 형식 `serviceAccount:{identity pool name}[{subject}]` 로 남습니다[14]. 외부 신원이 서비스 계정을 가장했다면 `serviceAccountDelegationInfo[]` 에 `thirdPartyPrincipal` 이, Google 신원이 가장했다면 `firstPartyPrincipal.principalEmail` 이 남습니다[14]. Workload Identity Federation 을 쓰는 외부 앱은 자격 증명 구성 파일로 자기 환경의 자격 증명을 짧은 수명의 서비스 계정 자격 증명으로 바꿔 씁니다[16].

풀과 공급자를 만들고 바꾸는 호출은 ADMIN_WRITE 권한이 필요해 관리 활동 (Admin Activity) 감사 로그에 남습니다[15]. 메서드 이름은 `google.iam.admin.v1.WorkforcePools.CreateWorkforcePool`, `CreateWorkforcePoolProvider`, `CreateWorkforcePoolProviderKey`, `UpdateWorkforcePoolProvider`, `DeleteWorkforcePool`, `DeleteWorkforcePoolProvider`, `SetIamPolicy` 와 `google.iam.v1.WorkloadIdentityPools.CreateWorkloadIdentityPool`, `CreateWorkloadIdentityPoolProvider`, `UpdateWorkloadIdentityPoolProvider`, `DeleteWorkloadIdentityPoolProvider` 같은 형식입니다[15]. (LRO) 표시가 붙은 메서드는 대개 시작과 끝에 한 건씩, 모두 두 건 남습니다[15].

### Google Workspace — SP 일 때와 IdP 일 때

Workspace 는 외부 IdP 를 믿는 SP 가 될 수도 있고, 다른 SaaS 앱에 어설션을 주는 IdP 가 될 수도 있어서 기록이 두 종류입니다.

| 방향 | 기록 | 이벤트·매개변수 |
|---|---|---|
| Workspace 가 SP(외부 IdP 로 로그인) | 로그인 감사(`applicationName=login`) | `login_type` 값 `saml`: SAML IdP 의 어설션을 냄[17] |
| Workspace 가 SP, 설정 변경 | 관리 감사(`applicationName=admin`) | `TOGGLE_SSO_ENABLED`(메시지 `Enable SSO changed to {NEW_VALUE} for {DOMAIN_NAME}`), `CHANGE_SSO_SETTINGS`(메시지 `SSO settings changed for {DOMAIN_NAME}`)[18] |
| Workspace 가 IdP(SAML 앱으로 로그인) | SAML 감사(`applicationName=saml`) | `login_success`, `login_failure`. 매개변수 `application_name`, `initiated_by`(`idp`·`sp`), `device_id`, `orgunit_path`, `saml_status_code`, `saml_second_level_status_code`, `failure_type`[19] |

`failure_type` 값은 `failure_app_not_configured_for_user`, `failure_app_not_enabled_for_user`, `failure_invalid_sp_id`, `failure_invalid_user_id_mapping`, `failure_malformed_request`, `failure_no_passive`, `failure_request_denied`, `failure_unknown`, `failure_user_id_mapping_unavailable` 입니다[19]. 로그인 활동 보고서에는 명시적 비밀번호 로그인과 SAML 기반 SSO 로그인만 남습니다[21].

### Okta — IdP 쪽 기록

Okta 가 IdP 라면 사용자가 앱으로 SSO 한 기록은 `user.authentication.sso` 로 남고 클라이언트 정보가 함께 들어가며, 이 이벤트는 SSO 가 실패해도 남습니다[22]. Okta 가 다시 외부 IdP 로 사용자를 인증했다면 `user.authentication.auth_via_IDP`, Okta 로그인 세션 시작은 `user.session.start` 입니다[22]. IdP 설정 변경은 `system.idp.lifecycle.create`, `update`, `activate`, `deactivate`, `delete` 로, 앱 설정과 앱 로그인 정책 변경은 `application.lifecycle.update`·`delete`, `application.policy.sign_on.update` 로 찾습니다[22][26].

## 읽는 법

페더레이션 로그인 한 건은 "IdP 가 확인 → 어설션 발급 → SP 가 검증하고 세션 발급" 순서로 흐르므로, SP 쪽 레코드에서 IdP 를 가리키는 필드를 먼저 찾고 그 값으로 IdP 로그를 찾아갑니다.

Entra 로그인 로그에서는 `tokenIssuerType` 이 `ADFederationServices` 인지, `incomingTokenType` 이 `saml11`·`saml20` 인지, `authenticationProtocol` 이 `wsFederation`·`saml20` 인지를 봅니다[3]. `authenticationProcessingDetails` 에 AD FS 서버·팜 이름이 있으면 그 서버의 이벤트 로그로 넘어갑니다[3].

AWS 에서는 아래 같은 `AssumeRoleWithSAML` 레코드가 출발점입니다. 아래는 AWS 문서 예시의 필드 구성을 따라 만든 예시이고, 값은 모두 지어낸 것입니다.

```json
{
  "eventVersion": "1.08",
  "userIdentity": {
    "type": "SAMLUser",
    "principalId": "ExampleQualifier0000=:user01",
    "userName": "user01",
    "identityProvider": "ExampleQualifier0000="
  },
  "eventTime": "2026-03-02T01:20:00Z",
  "eventSource": "sts.amazonaws.com",
  "eventName": "AssumeRoleWithSAML",
  "sourceIPAddress": "AWS Internal",
  "requestParameters": {
    "sAMLAssertionID": "_example0000assertion",
    "roleSessionName": "user01@example.com",
    "sourceIdentity": "user01",
    "roleArn": "arn:aws:iam::123456789012:role/ExampleFederatedRole",
    "principalArn": "arn:aws:iam::123456789012:saml-provider/ExampleIdP",
    "durationSeconds": 3600
  },
  "responseElements": {
    "credentials": {
      "accessKeyId": "ASIAIOSFODNN7EXAMPLE",
      "sessionToken": "(생략)",
      "expiration": "Mar 2, 2026, 2:20:00 AM"
    },
    "assumedRoleUser": {
      "assumedRoleId": "AROAEXAMPLEID0000000:user01@example.com",
      "arn": "arn:aws:sts::123456789012:assumed-role/ExampleFederatedRole/user01@example.com"
    },
    "subject": "user01",
    "subjectType": "transient",
    "issuer": "https://idp.example.com/saml",
    "audience": "https://signin.aws.amazon.com/saml",
    "nameQualifier": "ExampleQualifier0000=",
    "sourceIdentity": "user01"
  },
  "readOnly": true
}
```

`requestParameters.principalArn` 은 어느 SAML 공급자를 믿고 들어왔는지, `responseElements.issuer` 는 어설션을 낸 IdP 주소, `subject` 는 IdP 가 적은 사용자, `sAMLAssertionID` 는 IdP 로그에서 같은 어설션을 찾을 때 쓸 값입니다[11]. 이 호출은 읽기 전용(`readOnly: true`)으로 기록되지만, `AssumeRole`·`AssumeRoleWithSAML`·`AssumeRoleWithWebIdentity` 는 `secretAccessKey` 를 뺀 `responseElements` 전체를 남깁니다[11]. 그래서 응답의 `accessKeyId`(`ASIA` 로 시작)와 `assumedRoleUser.arn` 으로 이 세션이 뒤에 한 API 호출을 이어 찾을 수 있습니다. `AssumeRoleWithWebIdentity` 레코드에는 `additionalEventData.identityProviderConnectionVerificationMethod` 가 붙고, 값 `IAMTrustStore` 는 AWS 가 신뢰하는 루트 인증 기관 목록으로 OIDC IdP 연결을 확인했다는 뜻, `Thumbprint` 는 IdP 설정에 넣은 인증서 지문으로 확인했다는 뜻입니다[11]. `AssumeRoleWithSAML` 레코드의 `sourceIPAddress` 는 `AWS Internal` 로 남을 수 있으므로[11], 이 레코드 하나로 사용자 IP 를 알 수 있다고 가정하지 않습니다.

Google Cloud 에서는 `principalSubject` 의 `{identity pool name}` 으로 어느 풀·공급자를 거쳤는지 알고, 그 풀의 생성·변경 기록을 IAM 감사 로그에서 찾습니다[14][15]. Workspace 에서는 로그인 감사의 `login_type` 이 `saml` 인 레코드를 찾고, 같은 시각대의 외부 IdP 로그를 봅니다[17].

## 포렌식에서 중요한 점

### 증명하는 것

- 클라우드가 어느 IdP(`tokenIssuerName`, `identityProvider`, `issuer`, `principalSubject` 의 풀 이름)의 어설션·토큰을 받아 어떤 세션을 만들었는지[3][10][14].
- 신뢰 설정(도메인 인증 방식, SAML 공급자, Identity Center 외부 IdP, Workforce·Workload 풀, Workspace SSO)을 어느 계정이 언제 바꿨는지[1][15][18][25].
- Workspace 가 IdP 라면, 어느 사용자가 어느 SAML 앱으로 로그인을 시도했고 왜 실패했는지[19].

### 증명하지 못하는 것

- 페더레이션 사용자의 비밀번호·다단계 인증 판단은 IdP 에서 일어나므로 클라우드 쪽 기록만으로는 알 수 없습니다. AWS 콘솔 로그인 레코드는 페더레이션 사용자에게 `MFAUsed` 를 `No`, `mfaAuthenticated` 를 `false` 로 적고, 이 값은 IAM 사용자나 루트 사용자가 MFA 를 썼을 때만 참이 됩니다[12].
- 클라우드 쪽 기록만으로는 IdP 가 정말 그 사람을 확인했는지, 어설션이 위조됐는지를 가릴 수 없습니다. Entra ID 의 위험 탐지 "Token issuer anomaly"(`tokenIssuerAnomaly`)는 SAML 토큰 발급자가 손상됐을 가능성을 알리는 단서이고, 오프라인으로 계산되며 Entra ID P2 라이선스가 필요합니다[7].
- AWS 에서 페더레이션 세션이 한 이후의 API 호출은 역할 신원만 담으므로, `sourceIdentity`·세션 이름·SAML `subject` 를 이어 붙이지 않으면 사람을 특정할 수 없습니다[11].

### 시각

Entra 로그인 로그의 `createdDateTime` 은 로그인이 시작된 시각이고 늘 UTC 입니다[3]. CloudTrail 의 `eventTime` 은 `2023-08-28T18:30:58Z` 처럼 끝에 `Z` 가 붙은 UTC 입니다[11]. STS 응답의 `expiration` 은 `Aug 28, 2023, 7:00:58 PM` 처럼 ISO 8601 이 아닌 문자열이고 시간대 표시가 없습니다[11]. 같은 레코드의 `eventTime` `2023-08-28T18:30:58Z` 에 `durationSeconds` 1800 을 더하면 이 값과 맞으므로 UTC 로 읽으면 됩니다[11].

Okta 시스템 로그를 폴링으로 받으면 결과는 로그에 실제로 기록된 순서로 오고, 이벤트가 일어난 `published` 시각 순서와 다를 수 있습니다[23]. Workspace SAML 로그 이벤트는 거의 실시간으로, 몇 분 안에 들어옵니다[20]. IdP 로그의 시간대는 제품마다 달라서, 클라우드 쪽 UTC 시각과 나란히 놓기 전에 [클라우드 로그의 시각](../logging/timestamps.md)에서 형식을 확인합니다. 로그별 보관 기간은 [보관 기간과 라이선스](../logging/retention-licensing.md)에 모았습니다.

## 함정

- **페더레이션이면 클라우드 쪽 신호가 줄어듭니다.** 비밀번호 해시 동기화(PHS)를 쓰는 관리형 인증이면 페더레이션보다 Entra ID 쪽에서 얻는 신호가 많고, 페더레이션 환경에서는 공격 IP 를 Entra ID 가 아니라 AD FS 앞 방화벽에서 막습니다[8]. 페더레이션 테넌트라면 AD FS 등 IdP 로그를 수집 범위에 넣어야 합니다.
- **"All Federated Users" 신뢰 IP 설정.** Entra 다단계 인증의 신뢰 IP 에서 이 옵션을 켜면, 회사 내부에서 로그인한 페더레이션 사용자는 AD FS 가 발급한 `insidecorporatenetwork` 클레임으로 다단계 인증을 건너뜁니다[9]. 이 옵션을 켜면 조건부 접근도 이 클레임이 있는 요청을 신뢰 위치로 봅니다[9]. 로그인 로그에 다단계 인증이 없다고 바로 이상하게 보지 말고 이 설정부터 확인합니다.
- **작업 이름이 두 계열입니다.** Entra 감사 로그의 도메인 작업 이름은 `Set domain authentication`·`Set federation settings on domain` 이지만[1], Hawk 는 통합 감사 로그의 `AzureActiveDirectory` 레코드에서 `Set-AcceptedDomain`·`Add-FederatedDomain` 같은 Exchange cmdlet 모양 이름도 함께 찾고[27], Sigma 는 `Add-FederatedDomain` 을 Exchange 이벤트로 봅니다[25]. 두 계열을 모두 검색합니다.
- **Purview 설명문을 이름대로 읽지 않습니다.** Purview 감사 활동 표는 `Set federation settings on domain.` 을 "Changed the federation (external sharing) settings" 로 설명하지만[2], Entra 에서 이 작업은 도메인 페더레이션을 다루는 `DirectoryManagement` 범주 작업입니다[1]. 외부 공유 설정 변경으로만 읽으면 IdP 신뢰 변경을 놓칩니다.
- **같은 흐름이 단계마다 다른 type 으로 남습니다.** AWS STS 호출 레코드는 `SAMLUser`·`WebIdentityUser` 로 남고[10], 페더레이션 사용자의 콘솔 로그인 레코드는 `AssumedRole` 로 남습니다[12]. `SAMLUser` 만 검색하면 콘솔 로그인을 놓칩니다.
- **이벤트 소스 표기가 문서마다 다릅니다.** IAM Identity Center 문서 표는 Sign-in 이벤트 소스를 `signin.amazon.com` 으로 적고[13], CloudTrail 콘솔 로그인 예시는 `signin.amazonaws.com` 으로 적습니다[12]. 실제 로그에서 값을 확인하고 검색합니다.
- **방향이 반대인 두 Workspace 로그.** 로그인 감사의 `login_type` `saml` 은 외부 IdP 로 Workspace 에 들어온 기록이고[17], SAML 감사(`applicationName=saml`)는 Workspace 가 IdP 가 되어 다른 앱으로 보낸 기록입니다[19].
- **도메인 전환 기록.** 페더레이션 도메인을 관리형으로 돌리는 작업(`Set domain authentication`)과 사용자 단위 전환(`Convert federated user to managed`)은 따로 남습니다[1]. 사고 대응 중에 관리자가 한 전환과 공격자가 한 변경을 시각·수행 계정으로 구분합니다.

## 도구

| 도구 | 이 주제에서 하는 일 |
|---|---|
| Hawk `Get-HawkTenantDomainActivity` | 통합 감사 로그에서 `Set-AcceptedDomain`, `Add-FederatedDomain`, `Update Domain`, `Add verified domain`, `Add unverified domain`, `remove unverified domain` 을 뽑아 `Domain_Changes_Audit` CSV·JSON 으로 저장[27] |
| Untitled Goose Tool `entra_id_datadumper.py` | Graph 에서 `domains`, `domains/{id}/federationConfiguration`, `directory/federationConfigurations/graph.samlOrWsFedExternalDomainFederation`, `identity/identityProviders`, `policies/homeRealmDiscoveryPolicies`, `policies/claimsMappingPolicies` 등을 받아 현재 페더레이션 설정을 저장[28] |
| Microsoft-Extractor-Suite `Get-UsersInfo.ps1` | 사용자 목록의 `IdentityProvider` 열에 `Identities` 중 `SignInType` 이 `federated` 인 항목의 `Issuer` 를 적음[29] |
| Sigma 규칙 | `azure_federation_modified`, `microsoft365_new_federated_domain_added_audit`·`_exchange`, `azure_aadhybridhealth_adfs_new_server`·`_service_delete`, `aws_susp_saml_activity`, `aws_delete_saml_provider`, `aws_sso_idp_change`, `okta_identity_provider_created`[25][26] |
| Okta System Log API | `eventType eq "user.authentication.sso"` 같은 필터로 앱 SSO 기록을 뽑음. 관리 콘솔 Reports > System Log 는 기본으로 최근 7일을 보여 주고 CSV 로 내려받을 수 있음[23][24] |

현재 설정 스냅숏(Goose)과 변경 기록(Hawk, 감사 로그)을 함께 받아야, 보관 기간이 지나 변경 기록이 사라진 설정도 놓치지 않습니다. 로그인 기록을 걸러 이상한 것을 찾는 절차는 [이상한 로그인 가려내기](../../03-techniques/analysis/suspicious-sign-ins.md), 토큰을 훔쳐 쓴 사건의 조사 순서는 [토큰을 훔쳐 로그인했나](../../04-scenarios/account-compromise/token-theft.md)에서 다룹니다.

## 참고 문헌

1. Microsoft, "Microsoft Entra audit log categories and activities"(reference-audit-activities.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
2. Microsoft, "Audit log activities"(Purview). https://learn.microsoft.com/en-us/purview/audit-log-activities
3. Microsoft, "signIn resource type"(Microsoft Graph beta). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
4. Microsoft, "SigninLogs"(Azure Monitor 테이블 참조). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
5. Microsoft, "authenticationDetail resource type"(Microsoft Graph beta). https://learn.microsoft.com/en-us/graph/api/resources/authenticationdetail?view=graph-rest-beta
6. Microsoft, "Access token claims reference". https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference
7. Microsoft, "What are risk detections?"(ID Protection). https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-risks
8. Microsoft, "Token theft playbook". https://learn.microsoft.com/en-us/security/operations/token-theft-playbook
9. Microsoft, "Configure Microsoft Entra multifactor authentication settings". https://learn.microsoft.com/en-us/entra/identity/authentication/howto-mfa-mfasettings
10. AWS, "CloudTrail userIdentity element". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
11. AWS, "Logging IAM and AWS STS API calls with AWS CloudTrail". https://docs.aws.amazon.com/IAM/latest/UserGuide/cloudtrail-integration.html
12. AWS, "AWS Management Console sign-in events". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-aws-console-sign-in-events.html
13. AWS, "Logging IAM Identity Center API calls with AWS CloudTrail". https://docs.aws.amazon.com/singlesignon/latest/userguide/logging-using-cloudtrail.html
14. Google Cloud, "AuditLog"(Cloud Logging 참조). https://cloud.google.com/logging/docs/reference/audit/auditlog/rest/Shared.Types/AuditLog
15. Google Cloud, "IAM audit logging". https://cloud.google.com/iam/docs/audit-logging
16. Google Cloud, "Service account impersonation". https://cloud.google.com/iam/docs/service-account-impersonation
17. Google, "Login Audit Activity Events"(Admin SDK Reports API). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
18. Google, "Admin Domain Settings Activity Events"(Admin SDK Reports API). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-domain-settings
19. Google, "SAML Audit Activity Events"(Admin SDK Reports API). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/saml
20. Google Workspace 관리자 고객센터, "Data retention and lag times". https://support.google.com/a/answer/7061566
21. Google, "Login Audit Reports"(Admin SDK Reports API 안내). https://developers.google.com/workspace/admin/reports/v1/guides/manage-audit-login
22. Okta, "Event types" 목록(okta-event-types.csv). https://developer.okta.com/docs/okta-event-types.csv
23. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
24. Okta, "System Log"(도움말). https://help.okta.com/en-us/content/topics/reports/reports_syslog.htm
25. SigmaHQ, 클라우드 규칙(azure/audit_logs/azure_federation_modified.yml, azure/activity_logs/azure_aadhybridhealth_adfs_new_server.yml·azure_aadhybridhealth_adfs_service_delete.yml, m365/audit/microsoft365_new_federated_domain_added_audit.yml, m365/exchange/microsoft365_new_federated_domain_added_exchange.yml, aws/cloudtrail/aws_susp_saml_activity.yml·aws_delete_saml_provider.yml·aws_sso_idp_change.yml). https://github.com/SigmaHQ/sigma/tree/master/rules/cloud
26. SigmaHQ, Okta 규칙(okta_identity_provider_created.yml, okta_application_modified_or_deleted.yml, okta_application_sign_on_policy_modified_or_deleted.yml). https://github.com/SigmaHQ/sigma/tree/master/rules/identity/okta
27. T0pCyber, Hawk(Get-HawkTenantDomainActivity.ps1). https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Get-HawkTenantDomainActivity.ps1
28. CISA, Untitled Goose Tool(goosey/entra_id_datadumper.py). https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/entra_id_datadumper.py
29. Invictus Incident Response, Microsoft-Extractor-Suite(Scripts/Get-UsersInfo.ps1). https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-UsersInfo.ps1
