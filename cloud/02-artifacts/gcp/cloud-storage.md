---
title: "Cloud Storage 기록"
parent: "아티팩트 · Google Cloud"
nav_order: 540
---

# Cloud Storage 기록 (Cloud Storage)

Cloud Storage 버킷에서 일어난 일은 Cloud Audit Logs 의 감사 로그와 버킷마다 켜는 사용 로그 (usage logs) 두 곳에 남고, 지운 객체는 소프트 삭제 (soft delete) 와 객체 버전 관리 (Object Versioning) 로 한동안 되살릴 수 있어서 조사에서는 이 셋을 함께 봅니다[1][2][3].

## 무엇을 기록하나 · 왜 생기나

Cloud Storage 는 API 작업을 Cloud Audit Logs 에 남기고, 누가 자원에 접근했는지 추적하는 데는 사용 로그보다 감사 로그를 권장합니다[1][2]. 감사 로그는 관리 활동 (Admin Activity), 데이터 접근 (Data Access), 시스템 이벤트 (System Event) 로 나뉩니다[1]. 버킷 설정을 바꾸는 관리 활동 로그는 늘 남지만, 객체를 읽고 쓰는 데이터 접근 로그는 기본으로 꺼져 있어 따로 켜야 남습니다[1]. 감사 로그 전체의 종류·보관·수집 방법은 [Cloud Audit Logs](./cloud-audit-logs.md)에 있고, 이 쪽에서는 Cloud Storage 에만 해당하는 내용을 다룹니다.

사용 로그는 지정한 버킷에 들어온 요청을 시간마다 CSV 파일로 적은 기록이고, 저장 로그 (storage logs) 는 그 버킷이 전날 차지한 용량을 하루에 한 번 적은 기록입니다[2]. 두 로그 모두 버킷마다 켜야 생기고, 켜 두면 다른 버킷에 새 객체로 쌓입니다[2]. 감사 로그가 남기지 않는 공개 객체 접근과 객체 수명 주기 관리 (Object Lifecycle Management)·Autoclass 가 한 변경은 사용 로그에 남습니다[1][2].

두 로그에 모두 기록이 없더라도 지운 객체가 남아 있을 수 있습니다. 소프트 삭제는 지우거나 덮어쓴 객체와 지운 버킷을 정해진 기간 동안 복원할 수 있는 상태로 두고, 객체 버전 관리를 켠 버킷은 덮어쓰거나 지운 객체를 이전 버전 (noncurrent version) 으로 남깁니다[3][4].

## 위치와 버전별 차이

### 감사 로그

Cloud Storage 감사 로그의 서비스 이름은 `storage.googleapis.com` 이고, 자원 유형은 `gcs_bucket` 입니다[1]. Storage Insights 의 감사 로그는 서비스 이름이 `storageinsights.googleapis.com` 으로 따로 있습니다[1]. 로그 이름은 다른 서비스와 같이 `projects/PROJECT_ID/logs/cloudaudit.googleapis.com%2Factivity`, `...%2Fdata_access` 모양입니다[1].

| 로그 | 하위 유형 | 남는 작업(대략) | 기본 |
|---|---|---|---|
| 관리 활동 | ADMIN_WRITE | 버킷·관리 폴더 IAM 정책 설정, 객체 ACL 설정, 버킷 생성·삭제·재배치·메타데이터 변경, 소프트 삭제 버킷 복원, 태그 바인딩, 관리 폴더 생성·삭제, HMAC 키 생성·삭제·변경, Storage Insights 설정 | 늘 켜짐 |
| 데이터 접근 | ADMIN_READ | 버킷·관리 폴더 IAM 정책 읽기, 객체 ACL 읽기, 버킷 메타데이터 읽기, 버킷 목록, HMAC 키 조회·목록 | 꺼짐 |
| 데이터 접근 | DATA_READ | 객체 데이터·메타데이터 읽기, 객체 목록, 폴더 메타데이터·목록, 복사·합성, XML 멀티파트 업로드 목록 | 꺼짐 |
| 데이터 접근 | DATA_WRITE | 객체 생성·삭제, XML API 다중 삭제, 소프트 삭제 객체 복원, 이동, ACL 아닌 메타데이터 변경, 보존 (retention) 설정, 복사·합성, XML 멀티파트 업로드, 폴더 생성·삭제·이름 바꾸기 | 꺼짐 |
| 시스템 이벤트 | | 버킷 재배치의 시작과 끝 | 늘 켜짐 |

2026년 9월 문서 기준이고, 작업과 로그 종류의 대응은 대략입니다[1]. 객체를 만들 때 처음 거는 ACL 은 관리 활동 로그를 남기지 않습니다[1]. 데이터 접근 로그를 켜는 방법과 켠 범위를 확인하는 방법은 [Cloud Audit Logs](./cloud-audit-logs.md)에 있습니다.

### 사용 로그와 저장 로그

사용 로그를 켜려면 로그를 받을 버킷에서 `group:cloud-storage-analytics@google.com` 에 `roles/storage.objectCreator` 역할을 주고, 대상 버킷에 로그 버킷을 지정합니다[2]. 로그 버킷은 대상 버킷과 같은 조직(조직이 없으면 같은 프로젝트), 같은 위치에 있어야 하고, VPC 서비스 제어 (VPC Service Controls) 를 쓰면 같은 경계 안에 있어야 합니다[2].

```
gcloud storage buckets update gs://example-bucket --log-bucket=gs://example-logs-bucket
gcloud storage buckets describe gs://example-bucket --format="default(logging_config)"
```

두 번째 명령은 현재 설정을 보여 주고, 꺼져 있으면 `null` 을 돌려줍니다[2]. JSON API 로 보면 버킷 메타데이터의 `logging` 안 `logBucket`·`logObjectPrefix` 에 설정이 있고, 꺼져 있으면 빈 값이 옵니다[2]. 끌 때는 `--clear-log-bucket` 을 씁니다[2].

로그 객체 이름은 아래 모양이고, 접두사를 따로 정하지 않으면 대상 버킷 이름이 접두사가 됩니다[2].

```
OBJECT_PREFIX_usage_TIMESTAMP_ID_v0
OBJECT_PREFIX_storage_TIMESTAMP_ID_v0
example-bucket_usage_2022_06_18_14_00_00_1702e6_v0
```

세 번째 줄은 문서의 예시이고, 2022년 6월 18일 14:00 UTC 에 만든 사용 로그 객체입니다[2]. 사용 로그와 저장 로그는 로그 버킷의 일반 객체라서 요금도 일반 객체와 같게 매깁니다[2]. 그래서 얼마 동안 남는지는 로그 버킷에 걸린 수명 주기 규칙과 소프트 삭제 정책을 보고 판단합니다.

### 소프트 삭제와 객체 버전 관리

| 기능 | 기본 | 보존 기간 | 남는 것 | 읽기 |
|---|---|---|---|---|
| 소프트 삭제 | 지원하는 모든 버킷에서 켜짐 | 기본 7일, 7~90일로 바꿀 수 있고 0 이면 꺼짐 | 지우거나 덮어쓴 객체, 지운 버킷 | 읽기·수정 불가, 목록 보기와 복원만 가능 |
| 객체 버전 관리 | 꺼짐 | 사용자가 지울 때까지 | 덮어쓰거나 지운 객체의 이전 버전 | 읽을 수 있음 |

2026년 9월 문서 기준입니다[3][4]. 소프트 삭제 정책을 바꾸면 그 뒤에 지운 것에만 새 기간이 적용되고, 이미 지운 것은 지울 때의 기간을 따릅니다[3]. 소프트 삭제된 객체와 버킷은 목록에서 기본으로 숨겨져 있어서, 플래그나 필터를 명시해야 보입니다[3]. 객체 버전 관리는 버킷 삭제를 막지 못하고, 지운 버킷의 객체는 소프트 삭제가 켜져 있을 때만 되살릴 수 있습니다[4]. 프로젝트를 지우면 소프트 삭제가 켜진 버킷은 보존 기간과 프로젝트 복구 기간 가운데 짧은 쪽 동안 남고, 소프트 삭제가 꺼진 버킷은 바로 지워질 수 있습니다[3].

## 구조

### 감사 로그 레코드

LogEntry 와 AuditLog 의 필드는 [Cloud Audit Logs](./cloud-audit-logs.md)에서 설명합니다. Cloud Storage 에서 따로 볼 곳은 `protoPayload.metadata` 와 `protoPayload.authorizationInfo` 입니다.

`protoPayload.metadata` 에는 Cloud Storage 전용 정보가 들어갑니다[1]. 예를 들어 rewrite 작업에서 원본 객체를 읽은 기록의 metadata 에는 복사한 목적지 버킷을 적은 `destination` 이 있습니다[1]. 상세 감사 로깅 모드 (Detailed audit logging mode) 를 강제한 조직에서는 `request`·`response` 에도 Cloud Storage 정보가 더 들어갑니다[1].

요청에 `x-goog-custom-audit-KEY: VALUE` 헤더를 붙이면(XML API 는 같은 이름의 쿼리 파라미터도 됩니다) 그 값이 `protoPayload.metadata.audit_context.audit_info` 에 들어갑니다[1]. 키는 접두사를 포함해 64자, 값은 1,200자까지이고 요청마다 네 개까지 붙일 수 있습니다[1]. 아래는 문서 예시의 모양입니다.

```
protoPayload: {
 @type: "type.googleapis.com/google.cloud.audit.Auditlog",
 ...
 metadata: {
  audit_context: {
   app_context: "EXTERNAL",
   audit_info: {
    x-goog-custom-audit-job: "job name",
    x-goog-custom-audit-user: "test user"
   }
  }
 }
}
```

감사 로그는 요청을 처리하면서 검사한 IAM 권한을 기준으로 만들어지므로, 한 요청이 기록을 여러 건 남길 수 있습니다[1]. 검사한 권한은 `authorizationInfo[].permission` 에 들어가고, JSON API 메서드별로 검사하는 권한은 아래와 같습니다[5].

| JSON 메서드 | 검사하는 권한 |
|---|---|
| Buckets insert / delete | `storage.buckets.create` / `storage.buckets.delete` |
| Buckets list / get | `storage.buckets.list` / `storage.buckets.get` |
| Buckets patch·update, lockRetentionPolicy | `storage.buckets.update` |
| Buckets setIamPolicy / getIamPolicy | `storage.buckets.setIamPolicy` / `storage.buckets.getIamPolicy` |
| Objects get / list | `storage.objects.get` / `storage.objects.list` |
| Objects insert / delete | `storage.objects.create` / `storage.objects.delete` |
| Objects patch·update | `storage.objects.update` |
| Objects copy·rewrite | 원본 버킷 `storage.objects.get`, 목적지 버킷 `storage.objects.create`(덮어쓰면 `storage.objects.delete` 도) |
| Objects compose | `storage.objects.get`, `storage.objects.create` |
| Objects move | 원본 객체 `storage.objects.move`·`storage.objects.delete`·`storage.objects.get`, 목적지 객체 `storage.objects.create` |
| Objects restore | `storage.objects.create`, `storage.objects.restore` |
| Objects bulkRestore | `storage.buckets.restore`, `storage.objects.create`, `storage.objects.restore` |

버킷 IAM 정책을 바꾼 기록에서는 `protoPayload.serviceData` 를 봅니다. Cloud Storage 는 serviceData 에 `type.googleapis.com/google.iam.v1.logging.AuditData` 형식을 쓰고[9], plaso 의 `gcp_log` 파서는 이 부분의 `policyDelta.bindingDeltas` 에서 추가·제거된 구성원과 역할을 뽑습니다[14].

XML API 로 객체 여러 개를 한 요청에 지우면, 데이터 접근 로그가 켜져 있을 때 요청 전체의 부모 기록 한 건과 객체마다 자식 기록이 남습니다[1]. 자식 기록은 일반 삭제 기록과 모양이 같고, `parentRequestId` 로 부모 기록과 이어집니다[1]. 부모 기록에는 실패한 자식 요청의 오류만 들어가고 성공한 자식 요청은 들어가지 않습니다[1].

### 사용 로그 열

사용 로그는 CSV 이고 첫 줄이 열 이름입니다[2].

| 열 | 형식 | 뜻 |
|---|---|---|
| `time_micros` | 정수 | 요청을 마친 시각, 유닉스 에포크부터 마이크로초 |
| `c_ip` / `c_ip_type` | 문자열 / 정수 | 요청한 IP, 1 이면 IPv4·2 이면 IPv6 |
| `c_ip_region` | 문자열 | 나중을 위해 비워 둔 열 |
| `cs_method` | 문자열 | HTTP 메서드 |
| `cs_uri` | 문자열 | 요청 URI |
| `sc_status` | 정수 | 응답 HTTP 상태 코드 |
| `cs_bytes` / `sc_bytes` | 정수 | 요청으로 보낸 바이트 / 응답으로 보낸 바이트 |
| `time_taken_micros` | 정수 | 첫 바이트를 받은 때부터 응답을 보낼 때까지 걸린 마이크로초 |
| `cs_host` / `cs_referer` | 문자열 | 요청의 Host, HTTP Referer |
| `cs_user_agent` | 문자열 | User-Agent, 수명 주기 관리가 한 요청은 `GCS Lifecycle Management` |
| `s_request_id` | 문자열 | 요청 식별자 |
| `cs_operation` | 문자열 | Cloud Storage 작업 이름(예 `GET_Object`), 비어 있을 수 있음 |
| `cs_bucket` / `cs_object` | 문자열 | 요청한 버킷 / 객체(객체는 비어 있을 수 있음) |

저장 로그에는 `bucket` 과 `storage_byte_hours` 두 열이 있고, `storage_byte_hours` 를 24로 나누면 그날 버킷의 평균 크기가 나옵니다[2]. 두 로그의 끝에 새 열이 붙을 수 있으므로 열 개수를 고정하지 말고 첫 줄의 열 이름으로 읽습니다[2]. 사용 로그의 열에는 요청한 계정을 적는 칸이 없습니다[2].

### 서명된 URL

서명된 URL (signed URL) 은 쿼리 문자열에 서명을 담아, 계정이 없는 사람도 정해진 시간 동안 특정 객체를 읽거나 쓰게 하는 URL 입니다[6]. XML API 끝점에서만 쓰이고, URL 을 가진 사람은 누구나 만료 시각이나 서명 키 교체 전까지 쓸 수 있습니다[6].

| 쿼리 파라미터 | 뜻 |
|---|---|
| `X-Goog-Algorithm` | 서명 알고리즘(예 `GOOG4-RSA-SHA256`) |
| `X-Goog-Credential` | 서명한 계정과 날짜·리전 등, `계정/날짜/리전/storage/goog4_request` 모양을 URL 인코딩한 값 |
| `X-Goog-Date` | URL 을 쓸 수 있게 된 시각, ISO 8601 기본형 `YYYYMMDD'T'HHMMSS'Z'` |
| `X-Goog-Expires` | `X-Goog-Date` 부터 유효한 초, 가장 길게 604800초(7일) |
| `X-Goog-SignedHeaders` | 요청에 반드시 있어야 하는 헤더 |
| `X-Goog-Signature` | 서명 값 |

사용 로그는 전체 URL 경로와 모든 쿼리 파라미터를 남기므로[2], `cs_uri` 에 서명된 URL 의 파라미터가 있으면 `X-Goog-Credential` 에서 URL 을 서명한 계정과 서명 날짜를 읽을 수 있습니다[6].

## 증거로서 의미

**증명하는 것**

- 관리 활동 로그: 어느 주체가 언제 버킷을 만들거나 지웠고, 버킷 IAM 정책·객체 ACL·버킷 메타데이터(사용 로그 설정 포함)를 바꿨는지[1].
- 데이터 접근 로그(켜져 있을 때): 어느 주체가 어느 버킷의 어느 객체를 읽고, 만들고, 지우고, 복사했는지와 그때 검사한 권한[1][5].
- 사용 로그: 어느 IP·User-Agent 가 어느 객체에 어떤 HTTP 메서드로 요청했고, 응답 코드와 주고받은 바이트가 얼마였는지[2].
- 소프트 삭제 객체와 이전 버전: 그 객체가 지워지거나 덮어써졌다는 사실과 지워지기 전 내용[3][4].

**증명하지 못하는 것**

- 공개 객체 접근은 감사 로그에 남지 않고, `allUsers`·`allAuthenticatedUsers` 로 공개한 자원도 감사 로그를 만들지 않습니다[1][7]. 이런 접근은 사용 로그로만 볼 수 있습니다[2].
- 수명 주기 관리·Autoclass 가 한 변경은 감사 로그에 남지 않습니다[1].
- 사용 로그만으로는 요청한 계정을 알 수 없습니다[2].
- 데이터 접근 로그가 꺼져 있던 기간의 객체 읽기·쓰기는 감사 로그에 없습니다[1].
- Google Cloud 콘솔 밖에서 인증된 브라우저로 내려받은 기록은 데이터 접근 로그에서 `principalEmail`·`callerIp` 가 가려집니다[1].
- 서명된 URL 을 누가 받아서 썼는지는 기록이 말해 주지 않습니다. URL 을 가진 사람이면 누구나 쓸 수 있기 때문입니다[6].

보고서에는 "이 계정으로 이 시각에 이 객체를 읽는 요청이 기록되어 있다", "이 IP 에서 이 객체를 GET 으로 요청해 이만큼의 바이트를 응답으로 받은 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

감사 로그의 시각은 LogEntry 공통 규칙을 따르고 UTC 입니다. 자세한 규칙은 [Cloud Audit Logs](./cloud-audit-logs.md)와 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다. 감사 로그는 사건이 일어나고 몇 초 안에 전달됩니다[2].

사용 로그의 `time_micros` 는 요청을 마친 시각이고, 유닉스 에포크부터 센 마이크로초라서 시간대가 없는 UTC 값입니다[2]. 요청을 시작한 시각은 `time_micros` 에서 `time_taken_micros` 를 빼서 어림하는데, 이어 올리기 (resumable upload) 는 마지막 업로드 요청의 응답까지를 걸린 시간으로 칩니다[2]. 로그 객체 이름의 시각은 로그 객체를 만든 시각(UTC)이지 요청 시각이 아닙니다[2].

사용 로그는 보통 그 시간이 끝나고 15분쯤 뒤에 만들어지지만, 요청이 많은 버킷에서는 더 늦어질 수 있고 적어도 여섯 시간마다 만들어집니다[2]. 한 시간짜리 로그 객체에 앞 시간의 기록이 들어갈 수는 있지만 뒤 시간의 기록이 들어가지는 않고, 같은 시간에 객체가 여러 개 생길 수 있습니다[2]. 저장 로그는 하루에 한 번, 보통 태평양 표준시 오전 10시 전에 만들어집니다[2].

서명된 URL 의 `X-Goog-Date` 는 `Z` 가 붙은 UTC 시각이고, 만료 시각은 여기에 `X-Goog-Expires` 초를 더해 계산합니다[6].

## 함정과 한계

- 관리 활동 로그만 있으면 "객체를 읽었다" 를 말할 수 없습니다. 객체 읽기는 데이터 접근 로그에만 남고, 이 로그는 기본으로 꺼져 있습니다[1].
- 복사와 합성은 읽기와 쓰기를 함께 해서 기록이 두 건 남습니다[1]. 두 건을 서로 다른 작업으로 세지 않도록 합니다.
- 사용 로그는 전달 시각과 빠짐없음을 보장하지 않고, 같은 기록이 두 번 나올 수 있습니다[2]. 중복은 `s_request_id` 로 걸러 냅니다[2].
- 사용 로그를 켠 버킷의 로그를 로그 버킷에 쓰는 과정에서도 데이터 접근 로그가 생기고, 이 기록은 호출자 신원이 가려집니다[7]. 이 기록을 사람의 행동으로 읽지 않습니다.
- 데이터 접근 로그로 객체 접근을 기록하기 시작하면 `storage.cloud.google.com` 에서 쿠키로 인증한 브라우저 다운로드가 403 으로 실패할 수 있습니다[8]. 로그를 켠 뒤로 사용자의 내려받기 방식이 바뀌었을 수 있다는 점을 해석에 넣습니다.
- `x-goog-custom-audit-` 값은 요청한 쪽이 넣은 값이라 내용이 사실인지는 따로 확인해야 합니다[1].
- 사용 로그를 끄는 작업은 버킷 메타데이터 변경이라 관리 활동 로그에 남습니다[1][2]. 다만 바뀐 값이 `request` 에 얼마나 담기는지는 상세 감사 로깅 모드에 따라 달라질 수 있으므로[1], 기록과 함께 현재 `logging_config` 를 확인해 대조합니다.
- 로그 버킷에서 사용 로그 객체를 지워도 소프트 삭제가 켜져 있으면 보존 기간 동안 되살릴 수 있습니다[3]. 로그 객체 삭제 자체는 데이터 접근 로그의 DATA_WRITE 로 남습니다[1].
- 소프트 삭제된 객체를 복원하면 같은 버킷에 새 세대 (generation) 의 살아 있는 객체가 생기고, 원래의 소프트 삭제 객체는 보존 기간이 끝날 때까지 남으며, 복원한 객체는 원래 클래스와 관계없이 Standard 클래스로 씁니다[3]. 복원으로 생긴 객체의 생성 시각을 원래 업로드 시각으로 읽지 않습니다[4].
- 객체 버전 관리에서 메타데이터만 바꾸면 세대 번호는 그대로이고 메타세대 (metageneration) 번호만 올라갑니다[4]. 내용이 바뀌었는지는 세대 번호로 가립니다.
- 수명 주기 관리가 지운 객체도 소프트 삭제되지만, 이 삭제는 감사 로그에 남지 않습니다[1][3]. 사용 로그의 `cs_user_agent` 가 `GCS Lifecycle Management` 인 줄로 확인합니다[2].

## 직접 분석해 보기

### 로그 줄을 직접 읽기

사용 로그 한 줄을 열 이름과 짝지어 읽으면 됩니다. 아래는 만든 예시입니다.

| 열 | 값(만든 예시) |
|---|---|
| `time_micros` | `1790002745123456` |
| `c_ip` / `c_ip_type` | `203.0.113.25` / `1` |
| `cs_method` / `sc_status` | `GET` / `200` |
| `cs_uri` | `/example-bucket/reports/q3.xlsx` |
| `sc_bytes` | `5242880` |
| `cs_user_agent` | `curl/8.5.0` |
| `cs_operation` | `GET_Object` |
| `cs_bucket` / `cs_object` | `example-bucket` / `reports/q3.xlsx` |

`time_micros` 를 1,000,000 으로 나누면 유닉스 초 `1790002745` 가 되고, 이를 시각으로 바꾸면 2026-09-21 14:59:05 UTC 입니다. 이 요청은 14:00~15:00 사이 사용 로그 객체에 들어가고, 그 객체는 보통 15:15 UTC 무렵에 로그 버킷에 나타납니다[2]. `sc_bytes` 가 객체 크기와 비슷하면 객체 전체를 내려받았을 가능성이 있습니다. 같은 시간대 데이터 접근 로그에서 같은 객체에 `storage.objects.get` 권한을 검사한 기록을 찾아 계정을 붙입니다.

### 공개 도구로

감사 로그는 Logs Explorer 나 `gcloud logging read` 로 읽습니다. `log_id` 함수에는 URL 인코딩하지 않은 로그 ID 를 넣고, 배열 필드인 `authorizationInfo` 는 원소 가운데 하나라도 맞으면 걸립니다[10].

```
resource.type="gcs_bucket"
protoPayload.serviceName="storage.googleapis.com"
log_id("cloudaudit.googleapis.com/data_access")
protoPayload.authorizationInfo.permission="storage.objects.get"
protoPayload.resourceName:"example-bucket"
```

객체 작업은 권한 이름으로 거른 뒤 검체에서 실제 `methodName` 을 확인합니다. SigmaHQ 의 GCP 규칙은 `gcp.audit.method_name` 필드에서 버킷 목록 훑기를 `storage.buckets.list`·`storage.buckets.listChannels` 로[11], 버킷 변경·삭제를 `storage.buckets.delete`·`storage.buckets.insert`·`storage.buckets.update`·`storage.buckets.patch` 로 찾습니다[12]. 이 가운데 `storage.buckets.list`·`storage.buckets.delete`·`storage.buckets.update` 는 권한 이름과 같은 문자열이므로[5], 규칙을 적용하기 전에 검체의 `methodName` 이 이 모양인지 맞춰 봅니다.

사용 로그는 `gcloud storage cp` 로 내려받아 표 계산 도구에서 열 이름으로 읽거나, BigQuery 에 `bq load --skip_leading_rows=1` 로 올려 `cs_method` 별로 묶어 셉니다[2]. 내보낸 감사 로그 JSON 줄 파일은 plaso 의 `gcp_log` 파서로 타임라인에 올릴 수 있습니다[14]. 버킷과 객체의 현재 상태(객체 메타데이터, 버킷 ACL, 버킷 목록·객체 목록, 버킷 크기)는 cloud-forensics-utils(libcloudforensics) 의 `GoogleCloudStorage` 에 있는 `GetObjectMetadata`·`GetBucketACLs`·`ListBuckets`·`ListBucketObjects`·`GetBucketSize` 로 모을 수 있습니다[13].

## 교차 검증

- 누가 어떤 권한으로 요청했는지와 호출 IP·User-Agent 는 [Cloud Audit Logs](./cloud-audit-logs.md)에서 봅니다.
- 서비스 계정 키로 인증한 요청이면 `authenticationInfo.serviceAccountKeyName` 과 키 기록을 [IAM과 서비스 계정 키](./iam-keys.md)에서 이어 봅니다.
- 요청 IP 가 VPC 안의 VM 이면 같은 시간대 흐름을 [VPC 흐름 로그](./vpc-flow-logs.md)에서 찾습니다.
- 같은 종류의 기록을 다른 클라우드와 견줄 때는 [S3 접근 기록](../aws/s3-access-logs.md)과 [Storage 계정 기록](../azure/storage-logs.md)을 봅니다.
- 버킷을 공개로 바꾼 흐름은 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md), 자료를 빼 간 사건 전체의 흐름은 [클라우드 저장소에서 자료를 빼 갔나](../../04-scenarios/data-leak/storage-exfiltration.md), 여러 로그를 시간순으로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.
- 로그가 사라지기 전에 사용 로그 객체와 감사 로그를 확보하는 방법은 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)에 있습니다.

## 실습

Google Cloud 문서의 예시와 위의 만든 예시로 풀어 봅니다.

1. 문서 예시 객체 이름 `example-bucket_usage_2022_06_18_14_00_00_1702e6_v0` 에서 접두사, 로그 종류, 만든 시각을 나눠 적고, 이 객체에 담길 수 있는 요청의 시간 범위를 적어 봅니다[2].
2. 서명된 URL 문서의 예시 URL 에서 `X-Goog-Credential` 을 URL 디코딩해 서명한 계정과 날짜를 적고, `X-Goog-Date` 와 `X-Goog-Expires` 로 만료 시각을 UTC 로 계산해 봅니다[6].
3. 어떤 버킷의 데이터 접근 로그에 같은 시각의 기록이 두 건 있고, 한 건은 `storage.objects.get`, 다른 한 건은 `storage.objects.create` 를 검사했습니다. 어떤 작업일 가능성이 있는지, 목적지 버킷을 어디서 확인할지 적어 봅니다[1][5].
4. 공개 버킷에서 객체가 대량으로 내려받아진 정황이 있는데 감사 로그에는 아무 기록이 없습니다. 이 상황을 설명하는 이유와, 무엇을 먼저 확인해야 하는지 적어 봅니다[1][2].
5. 실제 검체에서는 조사 대상 버킷마다 `logging_config` 와 소프트 삭제 정책, 객체 버전 관리 설정을 모으고, 조사 기간 가운데 사용 로그·데이터 접근 로그·소프트 삭제 객체가 있어야 할 구간을 나눠 봅니다.

## 참고 문헌

1. Google Cloud, "Cloud Audit Logs with Cloud Storage", Cloud Storage documentation. https://cloud.google.com/storage/docs/audit-logging
2. Google Cloud, "Usage logs & storage logs", Cloud Storage documentation. https://cloud.google.com/storage/docs/access-logs
3. Google Cloud, "Soft delete overview", Cloud Storage documentation. https://cloud.google.com/storage/docs/soft-delete
4. Google Cloud, "Object Versioning", Cloud Storage documentation. https://cloud.google.com/storage/docs/object-versioning
5. Google Cloud, "IAM permissions for JSON methods", Cloud Storage documentation. https://cloud.google.com/storage/docs/access-control/iam-json
6. Google Cloud, "Signed URLs", Cloud Storage documentation. https://cloud.google.com/storage/docs/access-control/signed-urls
7. Google Cloud, "Cloud Audit Logs overview", Cloud Logging documentation. https://cloud.google.com/logging/docs/audit
8. Google Cloud, "Enable Data Access audit logs", Cloud Logging documentation. https://cloud.google.com/logging/docs/audit/configure-data-access
9. Google Cloud, "Understanding audit logs", Cloud Logging documentation. https://cloud.google.com/logging/docs/audit/understanding-audit-logs
10. Google Cloud, "Logging query language", Cloud Logging documentation. https://cloud.google.com/logging/docs/view/logging-query-language
11. SigmaHQ, gcp_bucket_enumeration.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/audit/gcp_bucket_enumeration.yml
12. SigmaHQ, gcp_bucket_modified_or_deleted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/audit/gcp_bucket_modified_or_deleted.yml
13. Google, cloud-forensics-utils, libcloudforensics/providers/gcp/internal/storage.py. https://github.com/google/cloud-forensics-utils/blob/main/libcloudforensics/providers/gcp/internal/storage.py
14. log2timeline, plaso, plaso/parsers/jsonl_plugins/gcp_log.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/jsonl_plugins/gcp_log.py
