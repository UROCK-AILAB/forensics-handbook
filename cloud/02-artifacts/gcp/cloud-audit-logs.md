---
title: "Cloud Audit Logs"
parent: "아티팩트 · Google Cloud"
nav_order: 520
---

# Cloud Audit Logs (Cloud Audit Logs)

Cloud Audit Logs 는 Google Cloud 의 프로젝트·폴더·조직·결제 계정에서 누가 어느 API 를 어느 자원에 불렀는지 남기는 기록이고, 관리 작업 기록은 끌 수 없이 400일 동안 남습니다[1][8].

## 무엇을 기록하나 · 왜 생기나

Google Cloud 서비스의 API 를 부르면 서비스가 감사 로그 항목을 Cloud Logging 에 씁니다. 감사 로그는 종류가 넷이고, 종류마다 무엇이 남는지, 끌 수 있는지, 요금이 붙는지가 다릅니다[1].

| 종류 | 로그 이름 끝 | 무엇이 남나 | 켜고 끄기 | 기본 저장 버킷 |
|---|---|---|---|---|
| 관리 활동 (Admin Activity) | `cloudaudit.googleapis.com%2Factivity` | 자원의 설정·메타데이터를 바꾸는 API 호출. VM 을 만들거나 IAM 권한을 바꾼 일 | 늘 기록되고 끄거나 제외할 수 없음. Cloud Logging API 를 꺼도 생김 | `_Required` |
| 데이터 접근 (Data Access) | `cloudaudit.googleapis.com%2Fdata_access` | 자원 설정·메타데이터를 읽은 호출, 사용자가 올린 데이터를 만들고 바꾸고 읽은 호출 | BigQuery 말고는 기본으로 꺼져 있어 따로 켜야 함. 켜면 요금이 붙을 수 있음 | `_Default` |
| 시스템 이벤트 (System Event) | `cloudaudit.googleapis.com%2Fsystem_event` | 사람이 아니라 Google 시스템·관리형 서비스 에이전트가 자원 설정을 바꾼 일. 자동 확장으로 관리형 인스턴스 그룹에 VM 이 늘고 준 일 | 늘 기록되고 끌 수 없음 | `_Required` |
| 정책 거부 (Policy Denied) | `cloudaudit.googleapis.com%2Fpolicy` | 보안 정책 위반으로 사용자·서비스 계정의 접근을 거부한 일 | 기본으로 생기고 끌 수 없지만, 제외 필터로 저장하지 않게 할 수 있음. 저장 요금이 붙음 | `_Default` |

근거: 네 종류의 정의와 켜고 끄기[1], 저장 버킷[1][6].

Cloud Audit Logs 가 쓴 항목은 바꿀 수 없습니다(immutable)[1]. 조사에서 먼저 보는 것은 관리 활동 로그입니다. 권한을 바꾸고, 서비스 계정 키를 만들고, 로그 설정을 고친 일이 모두 여기에 남고, 사용자가 끌 방법이 없기 때문입니다. 반대로 "파일을 읽었다", "테이블을 조회했다" 같은 데이터 쪽 질문은 데이터 접근 로그가 켜져 있었을 때만 답할 수 있습니다. 관리·데이터 로그의 일반 구분은 [로그의 종류](../../01-foundations/logging/log-types.md)에 있습니다.

`allUsers`·`allAuthenticatedUsers` 에게 공개한 자원, 로그인 없이 접근할 수 있는 자원은 감사 로그를 만들지 않습니다[1]. Access Transparency 로그는 감사 로그와 별도 로그이고, 이름은 `cloudaudit.googleapis.com/access_transparency` 입니다[6]. Google Workspace 의 관리 콘솔 감사 로그는 Cloud Audit Logs 와 다른 체계라서 [관리 콘솔 감사 로그](../google-workspace/admin-audit.md)에서 다룹니다.

### 데이터 접근 로그를 켜는 단위

데이터 접근 로그는 IAM 권한 유형 (permission type) 별로 켭니다. 한 API 메서드가 어느 권한을 검사하느냐에 따라 어느 로그로 가는지가 정해집니다[3].

| 권한 유형 | 검사하는 호출 | 가는 로그 |
|---|---|---|
| `ADMIN_READ` | 메타데이터·설정 읽기 | 데이터 접근 |
| `DATA_READ` | 사용자 데이터 읽기 | 데이터 접근 |
| `DATA_WRITE` | 사용자 데이터 쓰기 | 데이터 접근 |
| `ADMIN_WRITE` | 메타데이터·설정 쓰기 | 관리 활동(늘 켜짐) |

한 메서드가 `ADMIN_WRITE` 권한과 데이터 접근 권한을 함께 검사하면 관리 활동 로그가 남습니다[3].

설정은 프로젝트·폴더·조직·결제 계정의 IAM 정책 안 `auditConfigs` 부분에 들어 있습니다[3]. 다음은 모든 서비스에 세 유형을 켜고 한 사용자를 `DATA_WRITE` 에서 빼는 설정을 가정해 만든 예시입니다(사용자 이름은 지어낸 값).

```json
"auditConfigs": [
  {
    "service": "allServices",
    "auditLogConfigs": [
      { "logType": "ADMIN_READ" },
      { "logType": "DATA_READ" },
      { "logType": "DATA_WRITE", "exemptedMembers": [ "user:batch-admin@example.com" ] }
    ]
  }
]
```

`service` 에는 `allServices` 나 `cloudsql.googleapis.com` 같은 서비스 이름이 들어갑니다. 목록에서 빠진 `logType` 은 꺼진 것이고, `auditConfigs` 가 아예 없으면 그 자원의 데이터 접근 로그는 꺼져 있습니다[3]. `exemptedMembers` 에 든 주체의 호출은 그 유형의 로그가 남지 않습니다[3].

설정은 위에서 아래로 합쳐집니다. 조직이나 폴더에서 켠 로그는 그 아래 프로젝트에서 끌 수 없고, 위에서 넣은 예외 주체도 아래에서 뺄 수 없습니다[3]. `allServices` 설정과 서비스별 설정이 함께 있으면 둘을 합친 결과가 적용됩니다[3]. BigQuery 의 데이터 접근 로그는 끌 수 없습니다[3].

설정을 읽는 명령은 `gcloud projects get-iam-policy`, `gcloud resource-manager folders get-iam-policy`, `gcloud organizations get-iam-policy` 입니다. `projects.getIamPolicy` 는 그 프로젝트에 직접 건 정책만 돌려주고 조직·폴더에서 물려받은 설정은 보여 주지 않습니다[3]. 콘솔(IAM & Admin > Audit Logs)도 상위 자원의 `getIamPolicy` 권한이 없으면 상위 설정을 보여 주지 않지만, 그 설정은 그대로 적용됩니다[3]. 그래서 "데이터 접근 로그가 켜져 있었나" 는 프로젝트, 그 위 폴더, 조직의 정책을 모두 읽어 합쳐 봐야 답할 수 있습니다. 자원 계층은 [테넌트·구독·계정·프로젝트](../../01-foundations/model/tenancy.md)에 있습니다.

## 위치와 버전별 차이

### 로그 이름

감사 로그 이름은 자원 식별자, 문자열 `cloudaudit.googleapis.com`, 종류를 나타내는 문자열로 이루어집니다[1]. 로그 ID 안의 슬래시는 `logName` 안에서 `%2F` 로 URL 인코딩해야 합니다[4].

```text
projects/PROJECT_ID/logs/cloudaudit.googleapis.com%2Factivity
folders/FOLDER_ID/logs/cloudaudit.googleapis.com%2Fdata_access
organizations/ORGANIZATION_ID/logs/cloudaudit.googleapis.com%2Fsystem_event
billingAccounts/BILLING_ACCOUNT_ID/logs/cloudaudit.googleapis.com%2Fpolicy
```

네 가지 자원(프로젝트·폴더·조직·결제 계정) 각각에 네 종류가 있어 이름은 모두 16가지입니다[1]. 데이터 접근 로그는 데이터가 접근된 프로젝트에 쓰입니다[1]. 폴더나 조직 수준에서 한 작업은 그 폴더·조직의 로그에 남으므로, 프로젝트만 조회하면 조직 정책 변경 같은 기록을 놓칩니다.

### 저장 버킷과 보관 기간 (2026년 9월 문서 기준)

Cloud Logging 은 프로젝트·폴더·조직·결제 계정마다 `_Required` 와 `_Default` 두 로그 버킷과 같은 이름의 싱크 (sink) 를 자동으로 만듭니다[1].

| 버킷 | 자원 | 기본 보관 | 바꾸기 | 들어가는 것 |
|---|---|---|---|---|
| `_Required` | 프로젝트·폴더·조직 | 400일 | 바꿀 수 없음 | 관리 활동, 시스템 이벤트, Access Transparency |
| `_Default` | 프로젝트 | 30일 | 1~3650일 | 나머지 전부(데이터 접근, 정책 거부 등) |
| `_Default` | 폴더·조직 | 30일 | 바꿀 수 없음 | 〃 |
| 사용자 정의 | 프로젝트 | 30일 | 1~3650일 | 싱크가 보낸 것 |

근거: 보관 기간[8], 버킷별 내용[6]. 2023년 4월 1일부터 `_Default` 와 사용자 정의 버킷에서 기본 기간을 넘겨 보관하는 몫에는 보관 요금이 붙습니다[8]. 폴더·조직의 로그를 30일보다 오래 두려면 싱크로 프로젝트의 버킷에 보내야 합니다[8].

`_Required` 싱크의 포함 필터는 다음과 같고, 이 싱크는 바꾸거나 지울 수 없습니다[6].

```text
LOG_ID("cloudaudit.googleapis.com/activity") OR
LOG_ID("externalaudit.googleapis.com/activity") OR
LOG_ID("cloudaudit.googleapis.com/system_event") OR
LOG_ID("externalaudit.googleapis.com/system_event") OR
LOG_ID("cloudaudit.googleapis.com/access_transparency") OR
LOG_ID("externalaudit.googleapis.com/access_transparency")
```

`_Default` 싱크는 같은 목록을 `NOT` 으로 빼고 나머지를 모두 받으며, 이 싱크는 바꾸거나 끌 수 있습니다[6]. 그래서 데이터 접근·정책 거부 로그는 누군가 `_Default` 싱크를 고치거나 제외 필터를 넣으면 저장되지 않을 수 있지만, 관리 활동·시스템 이벤트 로그는 항상 원래 자원의 `_Required` 버킷에 남습니다. 가로채기 집계 싱크 (intercepting aggregated sink) 가 로그를 다른 곳으로 보내도 원래 자원의 `_Required` 싱크로는 늘 갑니다[6].

`_Required` 싱크는 그 자원에서 생긴 로그만 받습니다. 관리 활동 로그를 다른 프로젝트로 보내면 목적지 프로젝트의 `_Required`·`_Default` 싱크를 거치지 않으므로, 목적지에 싱크를 따로 만들어야 저장됩니다[1][6]. 중앙 로그 프로젝트를 두는 조직이라면 원래 프로젝트와 중앙 프로젝트 양쪽을 다 확인합니다.

보관 기간이 지난 로그는 되살릴 수 없습니다. 기간을 줄이면 7일 동안은 만료 로그를 지우지 않지만 조회도 보기도 안 되고, 그 7일 안에 기간을 다시 늘리면 되살아납니다. 기간을 늘려도 앞으로만 적용되고 이미 지나간 로그에는 소급하지 않습니다[7]. 싱크도 소급해서 보내지 못하므로, 싱크를 만들기 전 로그는 로그 복사 (Copy logs) 로 Cloud Storage 에 옮겨야 합니다[6]. 로그를 지키는 순서는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)에, 서비스별 보관 기간 비교는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에 있습니다.

### 싱크로 내보낸 사본의 모양

조직이 싱크로 감사 로그를 밖에 쌓아 두었다면 보관 기간이 지난 기록도 거기에 남아 있을 수 있습니다.

Cloud Storage 로 보내면 로그 ID 와 날짜로 폴더를 나누고 한 시간 단위 파일을 씁니다[9]. 로그 ID 에 슬래시가 들어 있으면 폴더가 한 단계 더 생깁니다(`appengine.googleapis.com/request_log/YYYY/MM/DD/` 예)[9]. 감사 로그라면 다음 모양이 됩니다.

```text
BUCKET/cloudaudit.googleapis.com/activity/2026/09/14/08:00:00_08:59:59_S0.json
BUCKET/cloudaudit.googleapis.com/activity/2026/09/14/08:00:00_08:59:59_A0:1789377300.json
```

위 경로의 날짜와 유닉스 시각은 만든 예시입니다. 파일 이름의 시간 구간은 UTC 이고, `timestamp` 와 `receiveTimestamp` 가 같은 60분 창에 들면 본 파일(`_Sn.json`)에, 다른 창이면 부록 파일(`_An:유닉스시각.json`)에 들어갑니다[9]. 부록 파일 이름의 유닉스 시각은 그 파일을 Cloud Storage 로 보낸 시각입니다[9]. 한 시간 묶음은 처음 나타나기까지 2~3시간 걸릴 수 있고, 파일 하나는 최대 3.5 GiB, 파일 안 순서는 보장되지 않습니다. 필터가 겹치는 싱크가 여럿이면 같은 항목이 여러 번 쓰일 수 있습니다[9]. 한 시간 구간의 기록을 다 보려면 그 구간의 `S`·`A` 파일을 모두 읽습니다[9].

BigQuery 로 보내면 테이블 이름은 로그 이름의 `.`·`/`·`-` 를 `_` 로 바꾼 모양이고, 날짜 분할 (date-sharded) 테이블이 기본이라 UTC 날짜 `_YYYYMMDD` 가 붙습니다(예: `compute_googleapis_com_activity_log_20171231`)[10]. 감사 로그 필드 이름도 바뀝니다[10].

| 로그 항목 필드 | BigQuery 필드 |
|---|---|
| `protoPayload` | `protopayload_auditlog` |
| `protoPayload.request` | `protopayload_auditlog.requestJson` |
| `protoPayload.response` | `protopayload_auditlog.responseJson` |
| `protoPayload.metadata` | `protopayload_auditlog.metadataJson` |
| `protoPayload.status.code` | `protoPayload_auditlog.statuscode` |

## 구조

감사 로그 항목은 Cloud Logging 의 일반 레코드인 LogEntry 이고, `protoPayload` 에 AuditLog 객체가 들어 있다는 점이 다른 로그와 다릅니다[1]. `protoPayload.@type` 이 `type.googleapis.com/google.cloud.audit.AuditLog` 이거나 `logName` 에 `cloudaudit.googleapis.com` 이 있으면 감사 로그입니다[2]. JSON 을 읽는 일반 원칙은 [JSON 로그 읽기](../../01-foundations/logging/json-logs.md)에 있습니다.

### 만든 예시 레코드

다음은 사용자가 프로젝트 IAM 정책에 서비스 계정 역할을 추가한 관리 활동 기록을 가정해 만든 예시입니다. 필드 구성은 문서의 프로젝트 정책 변경 예시와 AuditLog 형식을 따랐고[2][5][15], 프로젝트 ID·메일 주소·IP·insertId 는 모두 지어낸 값입니다. 사용자 에이전트는 문서 예시 값을 그대로 썼습니다[5].

```json
{
  "protoPayload": {
    "@type": "type.googleapis.com/google.cloud.audit.AuditLog",
    "status": {},
    "authenticationInfo": {
      "principalEmail": "admin@example.com"
    },
    "requestMetadata": {
      "callerIp": "203.0.113.25",
      "callerSuppliedUserAgent": "Cloud SDK Command Line Tool apitools-client/1.0 gcloud/0.9.62",
      "requestAttributes": {},
      "destinationAttributes": {}
    },
    "serviceName": "cloudresourcemanager.googleapis.com",
    "methodName": "SetIamPolicy",
    "authorizationInfo": [
      {
        "resource": "projects/example-project",
        "permission": "resourcemanager.projects.setIamPolicy",
        "granted": true
      }
    ],
    "resourceName": "projects/example-project",
    "request": {
      "@type": "type.googleapis.com/google.iam.v1.SetIamPolicyRequest",
      "resource": "example-project"
    },
    "response": {
      "@type": "type.googleapis.com/google.iam.v1.Policy",
      "bindings": [
        {
          "role": "roles/editor",
          "members": [ "serviceAccount:my-service-account@example-project.iam.gserviceaccount.com" ]
        }
      ]
    }
  },
  "insertId": "1a2b3c4d5e6f",
  "resource": {
    "type": "project",
    "labels": { "project_id": "example-project" }
  },
  "timestamp": "2026-09-14T08:12:45.482913Z",
  "severity": "NOTICE",
  "logName": "projects/example-project/logs/cloudaudit.googleapis.com%2Factivity",
  "receiveTimestamp": "2026-09-14T08:12:46.104377219Z"
}
```

### LogEntry 쪽 필드

| 필드 | 뜻 |
|---|---|
| `logName` | 로그 이름. 로그 ID 는 `%2F` 로 인코딩됨 |
| `resource` | 기록을 낸 모니터링 자원. `type`(예: `project`, `gae_app`, `audited_resource`)과 `labels` |
| `timestamp` | 기록이 설명하는 사건이 일어난 시각 |
| `receiveTimestamp` | Cloud Logging 이 받은 시각. 출력 전용 |
| `severity` | 심각도. `DEFAULT`, `DEBUG`, `INFO`, `NOTICE`, `WARNING`, `ERROR`, `CRITICAL`, `ALERT`, `EMERGENCY` |
| `insertId` | 항목의 고유 식별자 |
| `operation` | 장기 실행 작업의 `id`, `producer`, `first`, `last` |
| `protoPayload` | AuditLog 객체. `textPayload`·`jsonPayload` 와 함께 쓰이지 않음 |

근거: [4], `resource.type` 의 예는 [2][15]. 문서의 관리 활동 예시들은 `severity` 가 `NOTICE` 입니다[2][15].

장기 실행 작업 (long-running operation) 과 스트리밍 API 는 기록을 두 건 남깁니다. 호출해 작업이 시작될 때 한 건, 끝날 때 한 건이고, 두 건은 `operation.id` 와 `operation.producer` 가 같습니다. 첫 건은 `operation.first=true`, 끝 건은 `operation.last=true` 이고, 바로 끝나거나 실패하면 둘 다 `true` 인 한 건만 남습니다. 실패할 때 `operation` 을 채우지 않는 서비스도 있습니다[2]. 스트리밍 API 는 연결이 열려 있는 동안 `first`·`last` 가 모두 없는 중간 기록을 남길 수 있습니다[2].

### AuditLog(protoPayload) 필드

| 필드 | 뜻 |
|---|---|
| `serviceName` | API 서비스 이름. 예: `compute.googleapis.com` |
| `methodName` | 호출한 메서드. 예: `google.logging.v2.ConfigServiceV2.CreateSink` |
| `resourceName` | 대상 자원이나 컬렉션 |
| `resourceLocation` | 작업 뒤·앞의 위치(`currentLocations`, `originalLocations`) |
| `resourceOriginalState` | 바꾸기 전 상태. 자원을 실제로 바꾼 작업에만 있음 |
| `numResponseItems` | List·Query 메서드가 돌려준 항목 수 |
| `status` | 작업 전체의 결과. 오류 코드(`code`)·오류 메시지(`message`)·세부 정보(`details`) |
| `authenticationInfo` | 호출자. `principalEmail`, `principalSubject`, `serviceAccountKeyName`, `serviceAccountDelegationInfo`, `thirdPartyPrincipal`, `authoritySelector` |
| `authorizationInfo[]` | 검사한 자원·권한 짝마다 하나. `resource`, `permission`, `granted`, `resourceAttributes` |
| `policyViolationInfo` | 조직 정책 위반 정보 |
| `requestMetadata` | `callerIp`, `callerSuppliedUserAgent`, `callerNetwork`, `requestAttributes`, `destinationAttributes` |
| `request` / `response` | 요청과 응답. 너무 크거나 민감하거나 중복되는 값은 빠질 수 있고, 파일 내용 같은 사용자 데이터는 넣지 않음 |
| `metadata` | 서비스별 추가 정보 |
| `serviceData` | 옛 서비스별 정보. App Engine·BigQuery·IAM·Cloud Storage 가 씀 |

근거: 필드 정의[5], `serviceData` 를 쓰는 서비스와 형식[2].

`serviceAccountKeyName` 은 서비스 계정 인증용 자격 증명을 만들거나 교환하는 데 쓴 서비스 계정 키의 전체 자원 이름이고, 모양은 `//iam.googleapis.com/projects/{PROJECT_ID}/serviceAccounts/{ACCOUNT}/keys/{key}` 입니다[5]. 이 필드로 호출을 특정 키에 묶을 수 있고, 키를 만들고 지운 기록은 [IAM과 서비스 계정 키](./iam-keys.md)에서 다룹니다. `serviceAccountDelegationInfo` 는 서비스 계정을 거쳐 위임한 실제 주체의 이력이고, 위임이 여럿이면 원래 위임 순서대로 들어 있습니다[5].

### 호출자 신원과 IP 가 가려지는 경우

성공한 접근과 모든 쓰기 작업에서는 `principalEmail` 을 가리지 않습니다. 권한 거부로 실패한 읽기 작업은 호출자가 서비스 계정이 아니면 메일 주소가 가려질 수 있습니다[1]. 서비스별 예외도 있습니다[1].

| 서비스 | 가리는 방식 |
|---|---|
| 레거시 App Engine API | 신원을 모으지 않음 |
| BigQuery | 조건에 따라 호출자 신원·IP·일부 자원 이름을 가림 |
| Cloud Storage | 사용 로그 (usage logs) 를 켜 두면, 사용 로그를 버킷에 쓰면서 생긴 데이터 접근 로그의 호출자 신원을 가림 |
| Firestore | JWT 로 제3자 인증을 하면 `thirdPartyPrincipal` 에 토큰의 헤더와 페이로드가 들어감 |
| VPC 서비스 제어 (VPC Service Controls) | 정책 거부 로그에서 메일 주소 일부를 `...` 로, 일부 google.com 주소를 `google-internal` 로 바꿈 |
| Organization Policy | 메일 주소 일부를 `...` 로 바꿈 |

`callerIp` 는 호출 경로에 따라 값이 달라집니다[1][5].

| 호출 경로 | `callerIp` |
|---|---|
| 인터넷 | 공인 IPv4·IPv6 주소 |
| Google 내부에서 서비스끼리 부른 호출(사용자가 시작했어도 서비스 에이전트가 부른 호출 포함) | `private` |
| 외부 IP 가 있는 Compute Engine VM(GKE 노드 포함) | VM 의 외부 IP |
| 외부 IP 가 없는 VM, 접근한 자원과 같은 조직·프로젝트 | VM 의 내부 IPv4 |
| 외부 IP 가 없는 VM, 다른 조직·프로젝트 | `gce-internal-ip` |

여러 서비스를 거치는 흐름에서는 직전 호출자의 출발지가 전해지므로 `private` 대신 외부 주소가 보일 수 있습니다[1]. IP 를 해석하는 일반 원칙은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md)에 있습니다.

## 증거로서 의미

### 증명하는 것

- 어느 주체(`principalEmail` 또는 `principalSubject`)가 어느 서비스(`serviceName`)의 어느 메서드(`methodName`)를 어느 자원(`resourceName`)에 불렀는지[5].
- 권한 검사를 통과했는지(`authorizationInfo[].granted`)와 호출 결과(`status`)[5]. 권한 거부로 막힌 시도도 기록으로 남습니다.
- 서비스 계정 키로 인증했는지와 어느 키였는지(`serviceAccountKeyName`), 누가 서비스 계정을 거쳐 위임했는지(`serviceAccountDelegationInfo`)[5].
- 위 가림 규칙 안에서, 호출이 들어온 IP 와 호출자가 보낸 사용자 에이전트[1][5].
- 바꾸기 전 상태(`resourceOriginalState`)가 남은 작업에서는 무엇이 무엇으로 바뀌었는지[5].

### 증명하지 못하는 것

- 데이터 접근 로그가 꺼져 있던 기간의 데이터 읽기·쓰기. 객체를 내려받거나 테이블을 조회한 일은 관리 활동 로그에 남지 않습니다[1].
- 공개(`allUsers`·`allAuthenticatedUsers`) 자원이나 로그인 없이 쓸 수 있는 자원에 대한 접근[1].
- 요청·응답에 담긴 실제 데이터. `request`·`response` 에는 파일 내용 같은 사용자 데이터를 넣지 않습니다[5].
- 사용자 에이전트의 진위. `callerSuppliedUserAgent` 는 인증되지 않은 값입니다[5].
- `callerIp` 가 `private` 이나 `gce-internal-ip` 일 때 실제 출발지[1].
- 키보드 앞에 누가 있었는지. 여러 사람이 같은 서비스 계정 키를 나눠 쓰면 `principalEmail` 은 모두 같은 서비스 계정입니다.

보고서에는 "이 시각에 이 계정이 이 IP 에서 이 프로젝트의 IAM 정책을 바꾼 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다. 문장 짜는 법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)에 있습니다.

## 시각 해석

| 필드 | 무엇이 일어날 때의 시각 | 형식 |
|---|---|---|
| `timestamp` | 기록이 설명하는 사건이 일어난 시각. 보관 기간 계산에도 쓰임. 쓰는 쪽이 비워 두면 Cloud Logging 이 받은 때의 현재 시각을 넣음 | RFC 3339, 출력은 늘 `Z`(UTC), 소수점 0·3·6·9 자리 |
| `receiveTimestamp` | Cloud Logging 이 항목을 받은 시각 | 같음 |
| `protoPayload.requestMetadata.requestAttributes.time` | 대상 서비스가 요청의 마지막 바이트를 받은 시각 | RFC 3339 UTC, 최대 소수점 9자리 |

근거: `timestamp`·`receiveTimestamp`[4], `requestAttributes.time`[5].

내보낸 JSON 의 시각은 모두 UTC 입니다. Logs Explorer 화면은 시각 표시 형식을 고를 수 있어서("Date and time" 기본, "Date, time, and timezone"·"Time only" 선택 가능)[13], 화면에서 옮겨 적은 시각보다 내보낸 JSON 의 `timestamp` 를 기준으로 삼습니다.

`receiveTimestamp` 에서 `timestamp` 를 빼면 기록이 얼마나 늦게 들어왔는지 알 수 있습니다. Cloud Storage 싱크에서는 두 값이 서로 다른 60분 창에 들면 그 항목이 부록 파일로 가고, 싱크 사본은 처음 나타나기까지 2~3시간이 걸릴 수 있습니다[9]. 들어오는 항목 가운데 `timestamp` 가 보관 기간보다 오래되었거나 24시간 넘게 미래인 것은 버려집니다[6].

장기 실행 작업은 시작 기록과 끝 기록의 `timestamp` 가 다르므로, `operation.first` 기록의 시각을 "요청한 시각", `operation.last` 기록의 시각을 "끝난 시각" 으로 나눠 씁니다[2]. 서비스마다 다른 시각 표기의 비교는 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다.

## 함정과 한계

- **관리 활동 로그만으로 "읽었다" 를 말할 수 없습니다.** 데이터 접근 로그는 BigQuery 말고는 기본으로 꺼져 있습니다[1]. 먼저 조직·폴더·프로젝트의 `auditConfigs` 를 모두 읽어 사건 당시 켜져 있었는지 확인합니다[3].
- **보기 권한에 따라 데이터 접근 로그가 안 보입니다.** 로그 뷰어 (Logs Viewer, `roles/logging.viewer`) 역할로는 `_Default` 버킷의 데이터 접근 로그를 볼 수 없고, 비공개 로그 뷰어 (Private Logs Viewer, `roles/logging.privateLogViewer`) 역할이 필요합니다[1]. 조회 결과가 비었다고 기록이 없다고 판단하기 전에 조회한 계정의 역할을 확인합니다.
- **`gcloud logging read` 는 기본으로 하루치만 읽습니다.** `--freshness` 기본값이 `1d` 이므로, 더 오래된 기록은 `--freshness` 를 늘리거나 `timestamp` 조건을 필터에 넣어야 합니다[11]. `--freshness` 는 내림차순 조회이면서 필터에 시각 조건이 없을 때만 적용됩니다[11].
- **Logs Explorer 다운로드는 10,000건까지입니다**[6]. 기간 전체를 가져올 때는 gcloud·API 나 로그 복사를 씁니다.
- **결제 계정의 감사 로그는 콘솔에서 볼 수 없습니다.** gcloud 나 Logging API 로만 읽습니다[1].
- **폴더·조직의 `_Default` 버킷은 30일 고정입니다**[8]. 조직 수준 데이터 접근 로그는 사고를 늦게 알면 이미 사라졌을 가능성이 있습니다.
- **한 요청이 권한을 여럿 검사하면 `authorizationInfo` 가 여러 개입니다**[5]. `granted` 는 짝마다 따로 봅니다.
- **중복이 생길 수 있습니다.** 같은 프로젝트·`timestamp`·`insertId` 인 항목은 한 조회 결과 안에서 중복으로 빠지지만 내보낸 사본에서는 보장되지 않고[4], 겹치는 싱크는 같은 항목을 여러 번 씁니다[9]. 여러 사본을 합칠 때는 `insertId` 와 `timestamp` 로 중복을 걸러 냅니다.
- **메서드 이름 모양이 서비스마다 다릅니다.** 프로젝트 정책 변경은 `SetIamPolicy`(Resource Manager)이고 IAM 서비스의 정책 변경은 `google.iam.admin.v1.SetIAMPolicy` 입니다[15]. Logging 쿼리 언어는 정규식과 논리 연산자 말고는 대소문자를 구분하지 않고, `:` 는 부분 일치라서[12] `protoPayload.methodName:"SetIamPolicy"` 로 두 모양을 함께 찾을 수 있습니다.
- **로그 이름의 인코딩이 수집 경로마다 다를 수 있습니다.** 원래 `logName` 은 `%2F` 를 쓰지만[4], SIEM 으로 옮긴 사본을 겨냥한 Sigma 규칙 가운데는 `cloudaudit.googleapis.com/activity` 와 `cloudaudit.googleapis.com%2Factivity` 를 둘 다 찾는 것이 있습니다[18]. 검색어에 두 모양을 모두 넣습니다.

### 로그를 끄거나 지운 흔적

감사 로그 자체는 바꿀 수 없지만, 앞으로 저장될 기록을 줄이거나 버킷을 지우는 설정 변경은 가능합니다. 이런 변경은 모두 `ADMIN_WRITE` 권한을 검사하므로 관리 활동 로그에 남습니다[14].

| 작업 | `methodName` |
|---|---|
| 싱크 지우기·바꾸기 | `google.logging.v2.ConfigServiceV2.DeleteSink`, `UpdateSink` |
| 제외 필터 만들기·바꾸기·지우기 | `google.logging.v2.ConfigServiceV2.CreateExclusion`, `UpdateExclusion`, `DeleteExclusion` |
| 버킷 지우기·바꾸기·되살리기 | `google.logging.v2.ConfigServiceV2.DeleteBucket`, `UpdateBucket`, `UpdateBucketAsync`(장기 실행), `UndeleteBucket` |
| 로그 지우기 | `google.logging.v2.LoggingServiceV2.DeleteLog` (권한 `logging.logs.delete`) |
| 설정 바꾸기 | `google.logging.v2.ConfigServiceV2.UpdateSettings`, `UpdateCmekSettings` |

근거: [14]. 표에서 쉼표 뒤의 이름은 앞부분을 줄여 적었고, 로그에는 `google.logging.v2.ConfigServiceV2.` 가 붙은 전체 이름으로 남습니다.

로그를 읽거나 복사한 일(`google.logging.v2.LoggingServiceV2.ListLogEntries`, `google.logging.v2.ConfigServiceV2.CopyLogEntries`)은 `DATA_READ` 라서 Logging 의 데이터 접근 로그가 켜져 있을 때만 남습니다[14].

데이터 접근 로그를 끈 일은 프로젝트·폴더·조직의 IAM 정책 변경(`SetIamPolicy`)으로 남습니다. 모든 데이터 접근 로그를 끄려면 빈 `auditConfigs` 를 넣은 정책을 써야 하고, `auditConfigs` 부분을 아예 빼고 정책을 쓰면 기존 설정은 그대로 남습니다[3]. 그래서 `SetIamPolicy` 기록이 보이면 앞뒤 정책을 견줘 `auditConfigs` 가 바뀌었는지 확인합니다. 예외 주체를 추가하면 그 로그 유형이 켜진다는 점도 함께 봅니다[3]. 버킷을 지우면 `DELETE_REQUESTED` 상태로 7일 머문 뒤 지워지고, 그동안은 되살릴 수 있습니다[7]. 잠근 (locked) 버킷은 모든 항목이 보관 기간을 채우기 전까지 지울 수 없고, 잠금은 되돌릴 수 없습니다[7]. 조사 흐름은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)에 있습니다.

## 직접 분석해 보기

### 원문 JSON 을 한 번 따라가기

위의 만든 예시 레코드를 순서대로 읽으면 다음과 같습니다.

1. `logName` 끝이 `cloudaudit.googleapis.com%2Factivity` 라서 관리 활동 로그이고, `projects/example-project` 로 시작하므로 프로젝트 수준 기록입니다.
2. `protoPayload.serviceName` 이 `cloudresourcemanager.googleapis.com`, `methodName` 이 `SetIamPolicy`, `resource.type` 이 `project` 이므로 프로젝트 IAM 정책을 바꾼 호출입니다[15].
3. `status` 가 비어 있어 오류 코드가 없고, `authorizationInfo[0].granted` 가 `true` 이므로 권한 검사를 통과한 호출입니다[5].
4. `authenticationInfo.principalEmail` 이 사람 계정이고 `serviceAccountKeyName` 이 없으므로 서비스 계정 키로 인증한 호출이 아닙니다.
5. `requestMetadata.callerIp` 가 공인 주소이므로 인터넷에서 들어온 호출입니다. 사용자 에이전트는 gcloud 를 가리키지만 호출자가 보낸 값입니다[5].
6. `response.bindings` 에서 새 정책의 역할과 구성원을 봅니다. 이 레코드만으로는 무엇이 추가됐는지 알 수 없으므로, 같은 자원의 바로 앞 `SetIamPolicy` 기록이나 `serviceData.policyDelta` 가 있는 서비스라면 그 값과 비교합니다[2].
7. `timestamp` 와 `receiveTimestamp` 가 1초 안이므로 늦게 들어온 기록이 아닙니다.

### 공개 도구

**gcloud.** 프로젝트의 감사 로그 전체를 JSON 으로 받는 명령은 다음과 같습니다. 폴더는 `--folder`, 조직은 `--organization`, 결제 계정은 `--billing-account` 로 바꿉니다[1][11].

```bash
gcloud logging read \
  'logName:"cloudaudit.googleapis.com" AND timestamp>="2026-09-01T00:00:00Z"' \
  --project=example-project --order=asc --format=json > audit.json
```

버킷을 직접 지정할 수도 있습니다. 예: `gcloud logging read "" --bucket=_Required --location=global --view=_Default`[11]. 콘솔 Logs Explorer 에서는 `logName:"cloudaudit.googleapis.com"` 또는 `protoPayload."@type"="type.googleapis.com/google.cloud.audit.AuditLog"` 로 전체 감사 로그를 찾고, Log name 에서 `activity`·`data_access`·`system_event`·`policy` 를 골라 종류를 좁힙니다[1]. 수집 방법 전체는 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md)에 있습니다.

**libcloudforensics.** Google 의 cloud-forensics-utils 에 든 `GoogleCloudLog` 은 `ListLogs` 로 프로젝트의 로그 이름 목록을 모으고, `ExecuteQuery` 로 Logging API `entries.list` 를 `resourceNames`·`filter`·`orderBy: timestamp desc` 로 불러 항목을 받습니다[17].

**plaso.** plaso 의 JSON-L 파서 플러그인 `gcp_log` 는 한 줄에 LogEntry 하나가 든 파일을 읽어 타임라인 이벤트로 바꿉니다. `logName` 과 ISO 8601 `timestamp` 가 있는 줄을 GCP 로그로 봅니다[16]. 뽑는 값은 `methodName`·`serviceName`·`resourceName`, `principalEmail`·`principalSubject`·`serviceAccountKeyName`, `serviceAccountDelegationInfo` 의 위임 사슬(`a->b` 모양), `authorizationInfo[].permission`, `callerIp`, 사용자 에이전트, `status`, `serviceData.policyDelta.bindingDeltas`(`ACTION member with role` 모양) 등입니다[16]. 사용자 에이전트에 `command/` 가 있으면 그 뒤 값을 gcloud 명령 일부로(점을 공백으로 바꿔), `invocation-id/` 가 있으면 그 뒤 값을 gcloud 호출 식별자로 뽑습니다[16]. `gcloud logging read --format=json` 결과는 JSON 배열이므로, 한 줄에 항목 하나가 되도록 풀어 넣습니다. 여러 로그를 시간순으로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)과 [Linux 판의 타임라인 만들기](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html)에 있습니다.

**Sigma.** SigmaHQ 의 GCP 규칙은 `logsource` 가 `product: gcp`, `service: gcp.audit` 이고, 대부분 `gcp.audit.method_name` 필드로 메서드 이름을 봅니다. 예를 들어 버킷 규칙은 `storage.buckets.delete`·`insert`·`update`·`patch` 를[19], 서비스 계정 규칙은 `.serviceAccounts.disable`·`.serviceAccounts.delete` 로 끝나는 이름을 찾습니다[20]. 일부 규칙은 `data.protoPayload.methodName`·`data.protoPayload.logName` 처럼 원래 필드 경로를 씁니다[18]. 필드 이름은 로그를 옮긴 SIEM 의 매핑에 따라 달라지므로, 규칙을 쓰기 전에 가져온 사본의 필드 이름과 맞는지 봅니다. 규칙 활용은 [탐지 규칙으로 로그 검색하기](../../03-techniques/analysis/detection-rules.md)에 있습니다.

## 교차 검증

- **권한과 키.** `SetIamPolicy`, 서비스 계정·키 생성과 `serviceAccountKeyName` 을 따라가는 법은 [IAM과 서비스 계정 키](./iam-keys.md)와 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md)에 있습니다.
- **데이터 쪽 기록.** 버킷·객체 접근은 [Cloud Storage 기록](./cloud-storage.md)에서 데이터 접근 로그와 사용 로그를 함께 봅니다.
- **네트워크.** 방화벽 규칙이나 서브넷 설정을 바꾼 시각 전후의 실제 트래픽은 [VPC 흐름 로그](./vpc-flow-logs.md)에 남습니다. 감사 로그의 `callerIp` 가 VM 의 IP 라면 그 VM 의 흐름 로그와 VM 내부 기록을 함께 봅니다. VM 디스크는 [클라우드 가상 머신 수집](../../03-techniques/acquisition/vm-acquisition.md)과 [Linux 판의 클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html)을 봅니다.
- **다른 클라우드와 비교하기.** AWS 의 대응 기록은 [CloudTrail](../aws/cloudtrail/index.md), Azure 는 [활동 로그](../azure/activity-log.md)입니다.
- **시나리오.** [액세스 키가 새어 나갔나](../../04-scenarios/infrastructure/leaked-keys.md), [권한을 올렸나](../../04-scenarios/infrastructure/privilege-escalation.md), [채굴용 자원을 만들었나](../../04-scenarios/infrastructure/cryptomining.md), [클라우드 저장소에서 자료를 빼 갔나](../../04-scenarios/data-leak/storage-exfiltration.md)에서 이 로그를 어느 순서로 보는지 다룹니다.

## 실습

시험용 프로젝트를 하나 만들어 아래 작업을 한 뒤 감사 로그를 받아 풀어 봅니다.

1. 프로젝트 IAM 정책에 역할을 하나 추가하고 지웁니다. 두 `SetIamPolicy` 기록의 `response.bindings` 를 견줘 무엇이 바뀌었는지 찾을 수 있나요?
2. Cloud Storage 버킷에 객체를 올리고 내려받습니다. 데이터 접근 로그를 켜기 전과 켠 뒤에 각각 어떤 기록이 남나요?
3. `roles/logging.viewer` 만 있는 계정과 `roles/logging.privateLogViewer` 가 있는 계정으로 같은 쿼리를 돌려 봅니다. 결과 건수가 다른가요?
4. 서비스 계정 키를 만들어 그 키로 API 를 한 번 부릅니다. `authenticationInfo.serviceAccountKeyName` 의 키 ID 가 키 목록의 ID 와 같은가요?
5. 감사 로그를 Cloud Storage 로 보내는 싱크를 만들고 몇 시간 기다립니다. `_S0.json` 과 `_A0:...json` 파일이 생기나요? 부록 파일의 항목은 `timestamp` 와 `receiveTimestamp` 가 어떻게 다른가요?
6. 제외 필터를 하나 만들고 지운 뒤, 관리 활동 로그에서 `CreateExclusion`·`DeleteExclusion` 기록을 찾아 봅니다.

## 참고 문헌

1. Google Cloud, "Cloud Audit Logs overview", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/docs/audit
2. Google Cloud, "Understand audit logs", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/docs/audit/understanding-audit-logs
3. Google Cloud, "Enable Data Access audit logs", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/docs/audit/configure-data-access
4. Google Cloud, "LogEntry", Cloud Logging API 참조 (Last updated 2026-09-04). https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
5. Google Cloud, "AuditLog", Cloud Audit Logs 참조 (Last updated 2025-07-21). https://cloud.google.com/logging/docs/reference/audit/auditlog/rest/Shared.Types/AuditLog
6. Google Cloud, "Routing and storage overview", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/docs/routing/overview
7. Google Cloud, "Configure log buckets", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/docs/buckets
8. Google Cloud, "Quotas and limits", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/quotas
9. Google Cloud, "View logs routed to Cloud Storage", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/docs/export/storage
10. Google Cloud, "View logs routed to BigQuery", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/docs/export/bigquery
11. Google Cloud, "gcloud logging read", Google Cloud SDK 참조 (Last updated 2026-09-15). https://cloud.google.com/sdk/gcloud/reference/logging/read
12. Google Cloud, "Logging query language", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/docs/view/logging-query-language
13. Google Cloud, "Logs Explorer interface", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/docs/view/logs-explorer-interface
14. Google Cloud, "Cloud Logging audit logging", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/docs/audit-logging
15. Google Cloud, "Examples of audit logs for service accounts", IAM 문서 (Last updated 2026-09-24). https://cloud.google.com/iam/docs/audit-logging/examples-service-accounts , 및 "IAM audit logging" (Last updated 2026-09-24). https://cloud.google.com/iam/docs/audit-logging
16. log2timeline, plaso, gcp_log.py (JSON-L 파서 플러그인). https://github.com/log2timeline/plaso/blob/main/plaso/parsers/jsonl_plugins/gcp_log.py
17. Google, cloud-forensics-utils, libcloudforensics/providers/gcp/internal/log.py. https://github.com/google/cloud-forensics-utils/blob/main/libcloudforensics/providers/gcp/internal/log.py
18. SigmaHQ, gcp_breakglass_container_workload_deployed.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/audit/gcp_breakglass_container_workload_deployed.yml
19. SigmaHQ, gcp_bucket_modified_or_deleted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/audit/gcp_bucket_modified_or_deleted.yml
20. SigmaHQ, gcp_service_account_disabled_or_deleted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/audit/gcp_service_account_disabled_or_deleted.yml
