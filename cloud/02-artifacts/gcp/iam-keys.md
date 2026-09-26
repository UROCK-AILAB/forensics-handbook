---
title: "IAM과 서비스 계정 키"
parent: "아티팩트 · Google Cloud"
nav_order: 550
---

# IAM과 서비스 계정 키 (IAM·Service Account Keys)

Google Cloud 에서 서비스 계정 키가 언제 누구 손으로 만들어지고 꺼지고 지워졌는지는 IAM 관리 활동 감사 로그에 남고, 그 키로 인증한 호출은 다른 서비스의 감사 로그에 키 이름과 함께 남으며, 키의 현재 상태와 마지막 사용 날짜는 키 목록과 Activity Analyzer 로 따로 확인합니다[1][2][3][4][5][7].

## 무엇을 기록하나 · 왜 생기나

서비스 계정 (service account) 은 사람이 아닌 작업 부하가 쓰는 계정이고, 종류가 셋입니다[8]. 사용자 관리 서비스 계정 (user-managed service account) 은 사용자가 만들고 관리하며, 기본 서비스 계정 (default service account) 은 특정 서비스를 켤 때 자동으로 생기지만 관리 책임은 사용자에게 있고, 서비스 에이전트 (service agent) 는 Google Cloud 가 만들고 관리합니다[8]. IAM 정책에서는 `serviceAccount:my-service-account@my-project.iam.gserviceaccount.com` 처럼 적습니다[8]. 계정·역할의 일반 개념은 [클라우드 계정과 역할](../../01-foundations/identity/users-roles.md)에 있습니다.

서비스 계정으로 인증하는 길은 둘입니다[8]. 하나는 짧은 수명 자격 증명 (short-lived credentials) 을 받는 길로, 자원에 붙인 서비스 계정이나 gcloud 의 `--impersonate-service-account` 가 이 방식을 씁니다[8][9]. 다른 하나는 서비스 계정 키로 JWT (JSON Web Token) 에 서명하고 이를 액세스 토큰으로 바꾸는 길입니다[8]. 키는 파일이라 쉽게 복사해 옮길 수 있으므로, 유출을 조사할 때 먼저 살펴볼 대상입니다[6]. 토큰 일반은 [토큰과 세션](../../01-foundations/identity/tokens-sessions.md)에 있습니다.

키에는 두 가지가 있습니다[2]. 사용자 관리 키 (`USER_MANAGED`) 는 사용자가 만들고 지우며, Google 은 공개 키만 보관하고 개인 키는 보관하지 않습니다[2]. 시스템 관리 키 (`SYSTEM_MANAGED`) 는 Google 이 주기적으로 교체하고 개인 키를 밖으로 내주지 않습니다[2]. 시스템 관리 키는 개인 키가 밖으로 나가지 않으므로, 키 파일 유출을 조사할 때 보는 키는 사용자 관리 키입니다[2].

## 위치와 버전별 차이

서비스 계정 키의 흔적은 다섯 곳에 나뉘어 있습니다.

| 어디 | 무엇이 남나 | 기본 | 근거 |
|---|---|---|---|
| IAM 관리 활동 로그 (`iam.googleapis.com`) | 서비스 계정·키 생성, 업로드, 끄기, 켜기, 삭제, 서비스 계정 IAM 정책 변경 | 늘 켜짐 | [4] |
| IAM 데이터 접근 로그 | 키 조회·목록(`ADMIN_READ`), 짧은 수명 토큰 발급(`iamcredentials.googleapis.com`) | 꺼짐 | [4][5][12] |
| 다른 서비스의 감사 로그 | 키로 인증한 호출의 `serviceAccountKeyName`, 가장한 사람의 `serviceAccountDelegationInfo` | 그 서비스의 로그 설정을 따름 | [5][10] |
| 키 메타데이터(IAM API) | 만든 시각, 만료, 꺼짐 여부와 이유, 노출 표시 | 키가 남아 있는 동안 | [2][3] |
| Activity Analyzer(미리보기) | 서비스 계정·키의 마지막 인증 날짜 | Policy Analyzer API 를 켜야 조회 | [7] |

관리 활동 로그는 `_Required` 버킷에 400일 보관되고 이 기간은 바꿀 수 없으며, 데이터 접근 로그는 BigQuery 를 빼고 기본으로 꺼져 있습니다(2026년 9월 문서 기준)[12][13]. 버킷별 보관, 데이터 접근 로그를 켜는 방법, 수집 방법은 [Cloud Audit Logs](./cloud-audit-logs.md)에 있습니다.

키 생성을 막는 조직 정책 제약 `iam.disableServiceAccountKeyCreation` 과 키 업로드를 막는 "Disable service account key upload" 제약은 2024년 5월 3일 이후에 만든 조직에 기본으로 적용됩니다[1][6]. 그러므로 새 조직에서 키 생성 기록이 나왔다면 그 전에 이 제약을 풀어 준 기록도 찾아볼 만합니다. 유출된 키를 자동으로 끄려면 "Service Account Key Exposure Response" 제약을 `DISABLE_KEY` 로 두고, 이렇게 꺼진 키에는 노출 표시가 붙습니다[6].

한 서비스 계정에는 키를 10개까지 둘 수 있고, 키는 기본으로 만료되지 않으며, 조직 정책으로 새로 만드는 키에만 만료 시간을 걸 수 있습니다[1][6]. 지운 키는 되살릴 수 없습니다[1].

## 구조

### 키 파일

콘솔이나 gcloud 로 JSON 키를 만들면 아래 모양의 파일이 한 번 내려받아지고, 같은 파일을 다시 받을 수는 없습니다[1]. P12(PKCS#12) 형식도 만들 수 있고, 이때 파일 비밀번호는 `notasecret` 입니다[1][2].

```json
{
 "type": "service_account",
 "project_id": "PROJECT_ID",
 "private_key_id": "KEY_ID",
 "private_key": "-----BEGIN PRIVATE KEY-----\nPRIVATE_KEY\n-----END PRIVATE KEY-----\n",
 "client_email": "SERVICE_ACCOUNT_EMAIL",
 "client_id": "CLIENT_ID",
 "auth_uri": "https://accounts.google.com/o/oauth2/auth",
 "token_uri": "https://oauth2.googleapis.com/token",
 "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
 "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/SERVICE_ACCOUNT_EMAIL"
}
```

`private_key_id` 가 키 ID 이고, 감사 로그의 `serviceAccountKeyName` 끝부분과 키 목록의 `KEY_ID` 도 이 값입니다[1][3][5]. 파일은 옮기거나 이름을 바꿔도 되므로 정해진 경로가 없습니다[1]. gcloud 로 만들 때 출력 경로는 사용자가 정하고(`~/sa-private-key.json` 같은 식), 디스크에서는 이름이 아니라 내용으로 찾습니다[1].

### 키 메타데이터

IAM API 의 ServiceAccountKey 에 들어 있는 필드는 아래와 같습니다[2].

| 필드 | 뜻 |
|---|---|
| `name` | `projects/{PROJECT_ID}/serviceAccounts/{ACCOUNT}/keys/{key}` |
| `privateKeyType` | `TYPE_GOOGLE_CREDENTIALS_FILE`(JSON) 또는 `TYPE_PKCS12_FILE`. 만들 때 응답에만 있음 |
| `keyAlgorithm` | `KEY_ALG_RSA_1024`, `KEY_ALG_RSA_2048` |
| `privateKeyData` | 개인 키. 만들 때 응답에만 있음 |
| `publicKeyData` | 공개 키. 키 하나를 조회(get)할 때만 있음 |
| `validAfterTime` / `validBeforeTime` | 쓸 수 있는 시작·끝 시각 |
| `keyOrigin` | `GOOGLE_PROVIDED`(Google 이 만든 키) 또는 `USER_PROVIDED`(업로드한 키) |
| `keyType` | `USER_MANAGED` 또는 `SYSTEM_MANAGED` |
| `disabled` / `disableReason` | 꺼짐 여부와 이유: `..._USER_INITIATED`, `..._EXPOSED`, `..._COMPROMISE_DETECTED` |
| `extendedStatus[]` | `SERVICE_ACCOUNT_KEY_EXTENDED_STATUS_KEY_EXPOSED`, `..._KEY_COMPROMISE_DETECTED` 와 설명 값 |

`extendedStatus` 는 키가 유효한 동안 계속 남고, 노출 표시는 키를 다시 켜도 지워지지 않습니다[2][6]. `gcloud iam service-accounts keys list` 는 `KEY_ID`, `CREATED_AT`, `EXPIRES_AT`, `DISABLED`, `DISABLE_REASON`, `EXTENDED_STATUS` 열을 보여 주고[3], 유출로 꺼진 키의 메타데이터에는 `extended_status_message` 에 키가 발견된 곳의 링크가 들어갈 수 있습니다[3][6].

### 감사 로그의 작업 이름

IAM 감사 로그의 서비스 이름은 `iam.googleapis.com` 입니다[4]. 키와 서비스 계정에 관련된 작업은 아래와 같습니다[4].

| 로그 | 권한 유형 | 작업(`methodName`) |
|---|---|---|
| 관리 활동 | `ADMIN_WRITE` | `google.iam.admin.v1.CreateServiceAccountKey`, `UploadServiceAccountKey`, `DisableServiceAccountKey`, `EnableServiceAccountKey`, `DeleteServiceAccountKey`, `CreateServiceAccount`, `PatchServiceAccount`, `UpdateServiceAccount`, `DisableServiceAccount`, `EnableServiceAccount`, `DeleteServiceAccount`, `UndeleteServiceAccount`, `SetIAMPolicy` |
| 데이터 접근 | `ADMIN_READ` | `google.iam.admin.v1.GetServiceAccountKey`, `ListServiceAccountKeys`, `GetServiceAccount`, `ListServiceAccounts`, `GetIAMPolicy` |
| 기록 안 함 | | `google.iam.admin.v1.IAM.SignBlob`, `IAM.SignJwt`, `IAM.LintPolicy`, `IAM.QueryAuditableServices`, `IAM.QueryTestablePermissions` |

각 칸의 두 번째 이름부터는 `google.iam.admin.v1.` 접두사를 뺐습니다. 키 생성에 필요한 권한은 `iam.serviceAccountKeys.create`, 삭제는 `iam.serviceAccountKeys.delete` 입니다[4].

키 생성 기록은 아래 모양입니다. 값은 만든 예시입니다.

```json
{
 "logName": "projects/example-project/logs/cloudaudit.googleapis.com%2Factivity",
 "protoPayload": {
  "@type": "type.googleapis.com/google.cloud.audit.AuditLog",
  "authenticationInfo": { "principalEmail": "analyst@example.com" },
  "requestMetadata": { "callerIp": "203.0.113.25" },
  "serviceName": "iam.googleapis.com",
  "methodName": "google.iam.admin.v1.CreateServiceAccountKey",
  "request": {
   "@type": "type.googleapis.com/google.iam.admin.v1.CreateServiceAccountKeyRequest",
   "name": "projects/-/serviceAccounts/app-sync@example-project.iam.gserviceaccount.com"
  },
  "resourceName": "projects/-/serviceAccounts/112233445566778899001"
 },
 "resource": { "type": "service_account" },
 "timestamp": "2026-08-14T02:31:07.412953000Z",
 "receiveTimestamp": "2026-08-14T02:31:07.829114000Z"
}
```

`request.name` 에는 서비스 계정 이메일이, `resourceName` 에는 서비스 계정의 숫자 ID 가 들어갑니다[5]. 새 키의 ID 가 어느 필드에 들어가는지는 실제 로그로 확인해야 합니다. `response` 를 열어 키 이름이 있는지 보고, 없으면 키 목록에서 `validAfterTime` 이 그 시각 근처인 키를 찾아 맞춥니다.

### 키로 인증한 호출과 가장

키로 받은 토큰으로 다른 서비스를 호출하면, 그 서비스의 감사 로그에서 `authenticationInfo.principalEmail` 은 서비스 계정이 되고 `authenticationInfo.serviceAccountKeyName` 은 `//iam.googleapis.com/projects/PROJECT_ID/serviceAccounts/SA_EMAIL/keys/KEY_ID` 가 됩니다[5][10]. App Engine·Compute Engine 처럼 키 이름을 기록하지 않는 서비스도 있습니다[5].

가장 (impersonation) 은 두 기록으로 나뉩니다. 짧은 수명 토큰을 만드는 순간은 `serviceName` 이 `iamcredentials.googleapis.com`, `methodName` 이 `GenerateAccessToken` 인 데이터 접근 로그로 남고, `principalEmail` 은 토큰을 만든 주체, `resource.labels.email_id` 는 대상 서비스 계정입니다[5]. 이 기록은 IAM 데이터 접근 로그를 켜야 생깁니다[5]. 그 토큰으로 호출한 서비스의 로그에는 `principalEmail` 에 서비스 계정이, `serviceAccountDelegationInfo[].firstPartyPrincipal.principalEmail` 에 실제로 가장한 사람이 적힙니다[5][10]. App Engine·GKE 는 가장한 사람을 적지 않습니다[5]. 콘솔에서는 가장을 쓸 수 없으므로, 가장 흔적은 gcloud·클라이언트 라이브러리·API 호출에서 나옵니다[9]. 가장에 쓰는 권한은 `iam.serviceAccounts.getAccessToken` 이고, 서비스 계정 토큰 생성자 역할 (`roles/iam.serviceAccountTokenCreator`) 에 들어 있습니다[9].

서비스 계정을 VM 같은 자원에 붙일 때는 `methodName` 이 `iam.serviceAccounts.actAs` 이고 `authorizationInfo[].permission` 이 `iam.serviceAccounts.actAs` 인 관리 활동 기록이 `resource.type` `audited_resource` 로 남습니다[5]. VM 생성 기록 `v1.compute.instances.insert` 에서는 `protoPayload.request.serviceAccounts[0].email` 에 붙인 서비스 계정이 들어갑니다[5].

서비스 계정에 대한 역할 부여(서비스 계정 사용자 `roles/iam.serviceAccountUser`, 토큰 생성자)는 `google.iam.admin.v1.SetIAMPolicy` 로, 프로젝트에 대한 역할 부여는 `serviceName` `cloudresourcemanager.googleapis.com` 의 `SetIamPolicy` 로 남습니다[5]. `service-agent-manager@system.gserviceaccount.com` 이 서비스 에이전트에 역할을 주는 기록은 정상 동작입니다[5]. 권한 변화를 시간 순으로 따라가는 방법은 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md)에 있습니다.

## 증거로서 의미

**증명하는 것**

- 어느 주체가 어느 시각에 어느 서비스 계정에 키를 만들고, 올리고, 끄고, 켜고, 지웠는지(관리 활동 로그가 보관 기간 안에 있을 때)[4][5].
- 키 이름을 기록하는 서비스에서, 특정 키로 받은 토큰이 어떤 작업을 호출했는지[5][10].
- 가장한 사람이 기록된 서비스에서, 서비스 계정으로 한 작업 뒤에 있던 사람[5].
- 지금 남아 있는 키의 만든 시각, 만료, 꺼진 이유, Google 이 노출이나 침해를 감지했다는 표시[2][3].
- 서비스 계정·키가 마지막으로 인증에 쓰인 날짜(Activity Analyzer 의 관찰 기간 안)[7].

**증명하지 못하는 것**

- 키 파일이 어디로 복사됐는지. 파일 시스템의 접근·권한 변경은 대개 감사 로그에 남지 않습니다[6].
- 키를 쓴 사람이 누구인지. `principalEmail` 은 서비스 계정만 가리키고, 키 하나를 여러 앱이나 기계가 나눠 쓰면 기록만으로 구분하기 어렵습니다[6].
- 데이터 접근 로그가 꺼져 있던 기간의 토큰 발급과 키 조회[4][5].
- `SignBlob`·`SignJwt` 사용. 이 작업은 감사 로그를 만들지 않습니다[4].
- 이미 지운 키의 공개 키 내용. 지운 키는 되살릴 수 없습니다[1].

보고서에는 "이 시각에 이 계정이 이 서비스 계정에 키를 만든 기록이 있다", "이 키 ID 로 인증한 요청이 이 작업을 호출한 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

감사 로그의 `timestamp` 는 사건이 일어난 시각이고 `receiveTimestamp` 는 Cloud Logging 이 받은 시각이며, 둘 다 `Z` 로 끝나는 UTC 입니다[11]. 두 값의 차이가 기록이 늦게 들어온 정도입니다. 로그 시각 전반은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다.

키 메타데이터의 `validAfterTime` 은 키를 쓸 수 있게 된 시각입니다[2]. `validBeforeTime` 은 쓸 수 있는 마지막 시각이고, 만료가 없는 키는 `9999-12-31T23:59:59Z` 입니다[3]. 두 값 모두 RFC 3339 형식의 UTC 입니다[2]. 시스템 관리 키의 `validBeforeTime` 은 서명을 멈추는 시각이고, 공개 키는 그 뒤로 몇 시간 더 검증에 쓰일 수 있습니다[2]. 키를 만든 뒤 60초 이상 지나야 그 키로 다른 작업을 할 수 있는 경우가 있으므로, 생성 기록과 첫 사용 기록 사이에 1분 남짓 간격이 있어도 이상 징후가 아닙니다[1].

Activity Analyzer 의 `lastAuthenticatedTime` 과 `observationPeriod` 는 실제 인증 시각과 관계없이 시각 부분이 고정값(`T07:00:00Z`)이라 날짜만 알려 줍니다[7]. 예시 출력에는 `T08:00:00Z` 인 값도 있으므로, 시각 부분은 읽지 말고 날짜만 씁니다[7]. 아주 최근의 인증은 결과에 빠질 수 있습니다[7].

## 함정과 한계

키를 지워도 그 키로 이미 받은 짧은 수명 자격 증명은 취소되지 않고, 취소하려면 서비스 계정을 끄거나 지워야 합니다[1]. 그러므로 키 삭제 시각 뒤에도 같은 서비스 계정의 호출이 이어질 수 있습니다.

`serviceAccountKeyName` 이 없다고 키를 쓰지 않았다고 볼 수 없습니다. 서비스에 따라 키 이름을 기록하지 않습니다[5].

작업 이름의 모양이 로그마다 다릅니다. 서비스 계정 정책 변경은 `google.iam.admin.v1.SetIAMPolicy`(IAM 이 대문자)이고 프로젝트 정책 변경은 `SetIamPolicy` 입니다[4][5]. Logging 쿼리 언어의 `:` 연산자는 부분 일치이고 문자열 비교는 대소문자를 구분하지 않으므로, `protoPayload.methodName:"SetIamPolicy"` 로 찾으면 두 모양을 함께 잡을 수 있습니다[4][17].

Sigma 의 GCP 서비스 계정 규칙은 `gcp.audit.method_name` 이 `.serviceAccounts.disable`, `.serviceAccounts.delete`, `.serviceAccounts.create` 같은 값으로 끝난다고 보고 찾습니다[14][15]. 문서가 적은 작업 이름은 `google.iam.admin.v1.DisableServiceAccount` 모양이라 이 조건과 맞지 않으므로, 규칙을 쓰기 전에 실제 로그의 `methodName` 값과 맞춰 봅니다[4][14]. 키 생성과 삭제는 아래의 IAM 문서 쿼리로 찾습니다.

Activity Analyzer 의 키 결과에는 꺼진 키가 빠지고, 만료되거나 지운 키는 들어갈 수 있습니다[7]. 서비스 계정에 묶인 API 키로 인증한 요청은 서비스 계정 사용 지표에 기록되지 않습니다[7]. Google Workspace API 에 대한 도메인 전체 위임 (domain-wide delegation) 처럼 Google Cloud 밖의 Google API 에 인증한 기록은 Activity Analyzer 가 잡지 않으므로, Cloud Monitoring 의 서비스 계정 사용 지표와 대조합니다[7].

키 파일의 `token_uri` 값으로는 `https://accounts.google.com/o/oauth2/token` 과 `https://oauth2.googleapis.com/token` 이 모두 나오므로, 이 값으로 파일의 진위나 만든 방법을 판별하지 않습니다[1]. 밖에서 받은 키 파일은 `type` 이 `service_account` 인지부터 확인합니다[6].

## 직접 분석해 보기

### 디스크에서 키 파일 찾기

키 파일은 이름과 위치가 정해져 있지 않으므로 내용으로 찾습니다[1]. JSON 키 파일에는 늘 `"private_key_id"` 와 `"service_account"` 문자열이 들어 있고, 바이트로는 아래와 같습니다(명세로 만든 예시).

```text
22 70 72 69 76 61 74 65 5f 6b 65 79 5f 69 64 22   "private_key_id"
22 73 65 72 76 69 63 65 5f 61 63 63 6f 75 6e 74 22 "service_account"
```

디스크 이미지나 비할당 영역에서 이 바이트열을 찾은 뒤, 가까이 있는 `"private_key_id": "` 다음 40자리 16진수(키 ID)와 `"client_email"` 값을 적습니다. 키 ID 예시는 모두 40자리 16진수입니다[1][3][5]. 찾은 키 ID 를 키 목록과 감사 로그의 `serviceAccountKeyName` 에 대조하면, 이 기계에 있던 키가 언제 만들어졌고 어떤 호출에 쓰였는지 이어 볼 수 있습니다. 가상 머신 디스크를 확보하는 방법은 [[linux] 클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html)에 있습니다.

### 명령과 쿼리로

키의 현재 상태는 아래 명령으로 봅니다[3].

```text
gcloud iam service-accounts keys list --iam-account=SA_NAME@PROJECT_ID.iam.gserviceaccount.com
```

키 생성 기록은 IAM 문서의 쿼리를 Logs Explorer 에 그대로 넣어 찾습니다. 삭제는 `CreateServiceAccountKey` 를 `DeleteServiceAccountKey` 로 바꿉니다[4].

```text
resource.type = "service_account"
protoPayload.serviceName = "iam.googleapis.com"
protoPayload.methodName:"CreateServiceAccountKey"
log_id("cloudaudit.googleapis.com/activity")
resource.labels.email_id:"SERVICE_ACCOUNT_EMAIL"
```

키로 인증한 호출은 `protoPayload.authenticationInfo.serviceAccountKeyName:"KEY_ID"` 로, 가장은 `protoPayload.authenticationInfo.serviceAccountDelegationInfo` 가 있는 기록으로 좁힙니다[5][10]. 키와 서비스 계정의 마지막 인증 날짜는 아래 명령으로 봅니다(서비스 계정은 `serviceAccountLastAuthentication`)[7]. 이 명령에는 활동 분석 조회자 역할 (`roles/policyanalyzer.activityAnalysisViewer`) 이 필요합니다[7].

```text
gcloud policy-intelligence query-activity --activity-type=serviceAccountKeyLastAuthentication --project=PROJECT_ID
```

내보낸 감사 로그 JSON 줄 파일은 plaso 의 `gcp_log` 파서로 타임라인에 넣을 수 있습니다[16]. 이 파서는 `serviceAccountKeyName` 을 키 이름으로, `serviceAccountDelegationInfo[].firstPartyPrincipal` 을 `a->b` 모양의 위임 사슬로, `callerSuppliedUserAgent` 안의 `command/` 부분을 gcloud 명령으로 뽑고, VM 생성 기록에서는 붙인 서비스 계정과 범위를 뽑습니다[16]. 로그를 모으는 방법은 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md)과 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)에 있습니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [Cloud Audit Logs](./cloud-audit-logs.md) | 감사 로그 구조, `callerIp`·UA 해석, 보관과 수집 |
| [Cloud Storage 기록](./cloud-storage.md) | 서비스 계정으로 객체를 읽거나 쓴 기록 |
| [VPC 흐름 로그](./vpc-flow-logs.md) | 서비스 계정이 붙은 VM 의 외부 통신 |
| [AWS IAM](../aws/iam.md) | 액세스 키를 쓰는 AWS 쪽의 같은 문제 |
| [클라우드 타임라인](../../03-techniques/analysis/timeline.md) | 키 생성·사용·삭제를 한 줄로 늘어놓기 |
| [액세스 키가 새어 나갔나](../../04-scenarios/infrastructure/leaked-keys.md) | 키 유출 조사 흐름 |
| [권한을 올렸나](../../04-scenarios/infrastructure/privilege-escalation.md) | 가장·역할 부여로 권한을 넓힌 흐름 |

## 실습

1. Google Cloud 문서의 키 목록 예시에서 `9999-12-31T23:59:59Z` 인 키와 `DISABLE_REASON` 이 `EXPOSED` 인 키를 골라, 각 키가 조사에서 어떤 뜻인지 적어 봅니다[3].
2. 위의 만든 예시 키 생성 기록에서 누가, 어느 IP 에서, 어느 서비스 계정에 키를 만들었는지 적고, 이 기록만으로 새 키 ID 를 알 수 있는지 판단해 봅니다.
3. 어떤 서비스 계정의 키를 지운 뒤에도 30분 동안 그 서비스 계정 이름으로 Pub/Sub 호출이 이어졌습니다. 가능한 이유와 다음에 볼 필드를 적어 봅니다[1][5].
4. Activity Analyzer 결과에서 어느 키의 `lastAuthenticatedTime` 이 비어 있습니다. 이 키가 쓰인 적이 없다고 말할 수 있는지, 무엇을 함께 확인해야 하는지 적어 봅니다[7].
5. 실제 사건에서는 조사 대상 프로젝트의 서비스 계정마다 키 목록을 내려받고, 조사 기간의 `CreateServiceAccountKey`·`DeleteServiceAccountKey` 기록과 키 ID 를 한 표로 맞춰 봅니다.

## 참고 문헌

1. Google Cloud, "Create and delete service account keys", IAM documentation. https://cloud.google.com/iam/docs/keys-create-delete
2. Google Cloud, "REST Resource: projects.serviceAccounts.keys", IAM API reference. https://cloud.google.com/iam/docs/reference/rest/v1/projects.serviceAccounts.keys
3. Google Cloud, "List and get service account keys", IAM documentation. https://cloud.google.com/iam/docs/keys-list-get
4. Google Cloud, "Identity and Access Management audit logging", IAM documentation. https://cloud.google.com/iam/docs/audit-logging
5. Google Cloud, "Example logs for service accounts", IAM documentation. https://cloud.google.com/iam/docs/audit-logging/examples-service-accounts
6. Google Cloud, "Best practices for managing service account keys", IAM documentation. https://cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys
7. Google Cloud, "View recent usage for service accounts and keys", Policy Intelligence documentation. https://cloud.google.com/policy-intelligence/docs/activity-analyzer-service-account-authentication
8. Google Cloud, "Service accounts overview", IAM documentation. https://cloud.google.com/iam/docs/service-account-overview
9. Google Cloud, "Service account impersonation", IAM documentation. https://cloud.google.com/iam/docs/service-account-impersonation
10. Google Cloud, "AuditLog", Cloud Audit Logs reference. https://cloud.google.com/logging/docs/reference/audit/auditlog/rest/Shared.Types/AuditLog
11. Google Cloud, "LogEntry", Cloud Logging API reference. https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
12. Google Cloud, "Cloud Audit Logs overview", Cloud Logging documentation. https://cloud.google.com/logging/docs/audit
13. Google Cloud, "Quotas and limits", Cloud Logging documentation. https://cloud.google.com/logging/quotas
14. SigmaHQ, gcp_service_account_disabled_or_deleted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/audit/gcp_service_account_disabled_or_deleted.yml
15. SigmaHQ, gcp_service_account_modified.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/audit/gcp_service_account_modified.yml
16. log2timeline, plaso, plaso/parsers/jsonl_plugins/gcp_log.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/jsonl_plugins/gcp_log.py
17. Google Cloud, "Logging query language", Cloud Logging documentation. https://cloud.google.com/logging/docs/view/logging-query-language
