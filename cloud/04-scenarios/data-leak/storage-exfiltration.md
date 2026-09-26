---
title: "클라우드 저장소에서 자료를 빼 갔나"
parent: "시나리오 · 자료 유출"
nav_order: 810
---

# 클라우드 저장소에서 자료를 빼 갔나 (Storage Exfiltration)

S3 버킷, Azure Blob 컨테이너, Google Cloud Storage 버킷, SharePoint 사이트·OneDrive, Google Drive 처럼 조직의 자료를 담아 두는 클라우드 저장소에서 누군가 자료를 대량으로 읽어 가거나, 저장소 설정을 바꿔 밖에서 읽을 수 있게 열었는지를 로그로 가려내는 순서를 다룹니다. 링크를 만들어 파일을 나눠 준 경우는 [외부 공유 링크로 새어 나갔나](external-sharing.md) 에서, 퇴사 전후 한 사람의 행동을 좇는 경우는 [퇴사자가 자료를 가져갔나](departing-employee.md) 에서 다룹니다.

## 조사 질문

- 이 기간에 이 저장소(버킷·컨테이너·사이트·드라이브)에서 누가, 어디서, 어떤 객체를 읽어 갔나?
- 평소보다 많이 읽었나? 응답으로 나간 바이트는 얼마인가?
- 사람을 가려낼 수 있는 인증(IAM 사용자·역할, Entra ID, Google 계정)으로 읽었나, 아니면 미리 서명한 URL·SAS·공유 키·익명 접근처럼 사람을 가려내기 어려운 방법으로 읽었나?
- 버킷 정책·ACL·공개 접근 차단·스냅숏 권한·복제 설정을 바꿔 저장소를 밖으로 열거나 다른 곳으로 자료가 흘러가게 했나?

로그가 답하는 것은 "이 주체가 이 시각에 이 객체를 읽는 요청을 했고 서비스가 이렇게 응답했다" 까지입니다. 받은 쪽 기기에 파일이 지금도 있는지, 그 계정 뒤에 누가 앉아 있었는지는 저장소 로그 밖의 질문입니다.

## 먼저 확인할 것

**읽기 기록이 애초에 남는 설정이었는지부터 봅니다.** 저장소 서비스는 대부분 설정 변경(관리 이벤트)은 기본으로 남기지만 객체를 읽은 기록(데이터 이벤트)은 따로 켜야 남깁니다. 읽기 기록이 없다는 사실은 "안 읽었다" 가 아니라 "기록 설정이 없었다" 는 뜻일 수 있으므로, 서비스마다 그 기간에 무엇이 켜져 있었는지를 먼저 적어 둡니다.

| 서비스 | 객체를 읽은 기록 | 기본으로 남나 | 설정 확인 |
|---|---|---|---|
| AWS S3 | CloudTrail 데이터 이벤트 `GetObject` 등(자원 유형 `AWS::S3::Object`) | 남지 않음. 트레일과 이벤트 데이터 저장소는 기본으로 데이터 이벤트를 기록하지 않고, 추가 요금이 붙습니다[1]. 콘솔의 이벤트 기록 (Event history) 에는 관리 이벤트만 보입니다[10] | 트레일의 이벤트 선택자. 데이터 이벤트가 없으면 `"DataResources": []` 로 나옵니다[1] |
| AWS S3 | 서버 접근 로그 (server access logging) | 버킷마다 켜야 남음. 최선 노력 (best-effort) 전달이라 빠짐없이·제때 온다는 보장이 없습니다[5] | 버킷의 로깅 설정([S3 접근 기록](../../02-artifacts/aws/s3-access-logs.md)) |
| Azure Blob Storage | 리소스 로그 `StorageBlobLogs` | 남지 않음. 리소스마다 진단 설정을 만들어야 수집됩니다[12] | 저장소 계정의 진단 설정([리소스 로그와 진단 설정](../../02-artifacts/azure/resource-logs.md)) |
| Google Cloud Storage | 데이터 접근 감사 로그 `DATA_READ` | 남지 않음. 명시적으로 켜야 남습니다. 관리 활동 감사 로그는 기본으로 켜져 있고 끌 수 없습니다[17] | IAM 정책의 감사 설정([Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md)) |
| Google Cloud Storage | 사용 로그 (usage logs) | 버킷마다 설정. 매시간 CSV 객체로 쌓입니다[18] | 버킷의 로깅 설정([Cloud Storage 기록](../../02-artifacts/gcp/cloud-storage.md)) |
| SharePoint·OneDrive | 통합 감사 로그 `FileAccessed`·`FileDownloaded`·`FileSyncDownloadedFull` | 감사는 기본으로 켜져 있고, 꺼진 테넌트에는 남지 않음[21] | Exchange Online PowerShell 에서 `UnifiedAuditLogIngestionEnabled` 가 `True` 인지 확인[23]([통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md)) |
| Google Drive | Drive 로그 이벤트 `download`·`sync_item_content`·`access_item_content` | 대부분의 Drive 감사 이벤트는 지원 에디션 사용자가 소유한 파일에만 남음[25] | [Drive 기록](../../02-artifacts/google-workspace/drive-audit.md) |

S3 는 켜 두었더라도 일부만 남을 수 있습니다. 트레일에서 읽기 (Read) 와 쓰기 (Write) 를 따로 고를 수 있고 `GetObject` 는 읽기 데이터 이벤트라서, 쓰기만 켠 트레일에는 남지 않습니다[1]. 버킷과 접두사 (prefix) 를 지정해 켠 경우에는 다른 접두사 아래 객체의 요청이 남지 않습니다[1].

**보관 기간을 확인합니다.** 아래는 2026년 9월 문서 기준이고, 서비스별 전체 표는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에 있습니다. 로그부터 확보하는 방법은 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 에 있습니다.

| 기록 | 기본 보관 |
|---|---|
| CloudTrail 이벤트 기록(관리 이벤트) | 최근 90일[10]. 트레일로 받은 로그는 전달한 S3 버킷의 설정을 따름 |
| S3 서버 접근 로그, GCS 사용 로그, Azure 리소스 로그 | 보낸 곳(버킷·Log Analytics 작업 영역·저장소 계정)의 설정을 따름 |
| Microsoft 365 감사 로그 | Audit (Standard) 180일(2023년 10월 17일 이전에 생긴 기록은 90일). Audit (Premium) 기본 정책 1년은 활동한 사용자에게 E5 등의 라이선스가 있을 때만[24] |
| Google Workspace Drive 로그 이벤트 | 6개월[27] |

**시각의 기준을 맞춥니다.** CloudTrail 의 `eventTime` 은 `2019-02-01T03:18:19Z` 처럼 끝에 Z 가 붙은 UTC 입니다[6]. S3 서버 접근 로그의 시각은 `[06/Feb/2019:00:00:38 +0000]` 모양으로, 요청을 받은 시각을 UTC 로 적습니다[4]. GCS 사용 로그의 `time_micros` 는 요청이 끝난 시각을 Unix epoch 마이크로초로 적고[18], 감사 로그의 `timestamp` 는 작업 시각입니다[17]. `StorageBlobLogs` 의 `TimeGenerated` 는 표 문서에서는 "스토리지가 요청을 받은 UTC 시각"[13], 모니터링 문서에서는 "로그 항목이 기록된 때"[14] 로 설명이 서로 다릅니다. 통합 감사 로그의 `CreationTime` 은 UTC 입니다[22]. 시간대를 맞추는 일반 원리는 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 에 있습니다.

**늦게 들어오는 기록을 셈에 넣습니다.** CloudTrail 은 데이터 이벤트를 5분마다, 관리 이벤트를 15분마다 전달하고, S3 서버 접근 로그는 몇 시간 안에 전달합니다[3]. GCS 사용 로그는 보통 정시가 지나고 15분 뒤에 만들어지지만 요청이 많은 버킷에서는 늦어지고, 적어도 6시간마다는 만들어집니다[18]. Microsoft 365 의 SharePoint·OneDrive 감사 기록은 보통 60~90분 뒤에 검색되고, 이 시간은 보장되지 않습니다[23]. 사건 직후에 수집했다면 마지막 한두 시간이 빠졌을 수 있습니다.

**조사자 자신의 흔적을 구분할 준비를 합니다.** Azure 포털에서 저장소 계정을 보기만 해도 포털이 부른 작업이 저장소 로그에 남습니다[14]. 수집을 시작한 시각과 조사자 계정·IP 를 적어 두면 뒤에서 걸러 낼 수 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 기록 설정 이력: CloudTrail 이벤트 선택자, S3 `PutBucketLogging`, Azure 진단 설정, GCP 감사 설정 | 조사 기간에 읽기 기록이 남는 상태였는지, 중간에 누가 껐는지 | [로그를 끄거나 지웠나](../infrastructure/log-tampering.md) |
| 2 | 공급자의 탐지 결과: GuardDuty S3 결과, Defender for Cloud Apps 경고 | 공급자가 이상한 읽기·공개 설정을 감지했는지 | [GuardDuty](../../02-artifacts/aws/guardduty.md), [Defender 경고와 기록](../../02-artifacts/m365/defender-xdr.md) |
| 3 | 저장소를 여는 설정 변경: S3 버킷 정책·ACL·공개 접근 차단, EBS 스냅숏 권한, GCS 버킷 IAM 정책, Azure 계정 키 조회 | 저장소를 밖에서 읽을 수 있게 만든 때와 주체 | [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md), [EC2 인스턴스와 스냅숏](../../02-artifacts/aws/ec2-ebs.md), [활동 로그](../../02-artifacts/azure/activity-log.md), [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md) |
| 4 | 객체 읽기 기록: S3 데이터 이벤트·서버 접근 로그, `StorageBlobLogs`, GCS `DATA_READ`·사용 로그 | 누가 어떤 객체를 몇 번, 얼마만큼 읽었나 | [S3 접근 기록](../../02-artifacts/aws/s3-access-logs.md), [Storage 계정 기록](../../02-artifacts/azure/storage-logs.md), [Cloud Storage 기록](../../02-artifacts/gcp/cloud-storage.md) |
| 5 | 업무 저장소 읽기 기록: 통합 감사 로그 파일 작업, Drive 로그 이벤트 | 누가 어떤 파일을 내려받거나 동기화했나 | [SharePoint·OneDrive](../../02-artifacts/m365/sharepoint-onedrive.md), [Drive 기록](../../02-artifacts/google-workspace/drive-audit.md) |
| 6 | 읽은 주체의 인증 기록: 로그인 로그, 역할 넘겨받기, 액세스 키 사용 | 읽기에 쓴 자격 증명이 어디서 왔나 | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [IAM](../../02-artifacts/aws/iam.md), [액세스 키가 새어 나갔나](../infrastructure/leaked-keys.md) |
| 7 | 네트워크 흐름: VPC 흐름 로그 | 인스턴스에서 밖으로 나간 트래픽의 양과 상대 주소 | [VPC 흐름 로그](../../02-artifacts/aws/vpc-flow-logs.md) |

## 분석 흐름

1. **기간과 대상 저장소를 정하고, 그 기간의 기록 설정을 표로 만듭니다.** 앞 절의 표를 서비스마다 채우고, 조사 기간 안에서 설정이 바뀐 시각이 있으면 그 시각을 경계로 구간을 나눕니다. S3 에서 버킷 로깅 설정 변경 `PutBucketLogging` 은 웹 사이트·암호화·수명 주기·복제 설정 변경과 함께 Sigma 규칙 "AWS S3 Data Management Tampering" 이 잡는 이벤트입니다[11]. 이 규칙은 `eventSource` 가 `s3.amazonaws.com` 이고 `eventName` 이 `PutBucketLogging`, `PutBucketWebsite`, `PutEncryptionConfiguration`, `PutLifecycleConfiguration`, `PutReplicationConfiguration`, `ReplicateObject`, `RestoreObject` 중 하나인 기록을 잡습니다[11].

2. **공급자의 탐지 결과를 모읍니다.** GuardDuty 의 `Exfiltration:S3/AnomalousBehavior`·`Exfiltration:S3/MaliciousIPCaller`·`Discovery:S3/AnomalousBehavior` 는 데이터 원천이 S3 용 CloudTrail 데이터 이벤트이고 결과 유형 표에서 보호 플랜 쪽으로 묶이므로, S3 보호 (S3 Protection) 를 켠 계정에서 나옵니다[9]. 버킷을 공개로 연 설정에는 관리 이벤트로 만드는 `Policy:S3/BucketPublicAccessGranted`, `Policy:S3/BucketAnonymousAccessGranted`, `Policy:S3/BucketBlockPublicAccessDisabled`, `Policy:S3/AccountBlockPublicAccessDisabled` 가 있습니다[9]. Microsoft 365 에서는 Microsoft Cloud App Security 가 알리는 경고 `Suspicious OAuth app file download activities`(앱이 SharePoint·OneDrive 에서 평소와 달리 파일을 여럿 내려받음), `Data exfiltration to unsanctioned apps`(허가하지 않은 앱으로 자료를 빼내려는 듯한 활동)를 Sigma 규칙이 `eventSource` `SecurityComplianceCenter` 와 경고 이름으로 잡습니다[28][29]. 결과가 없다고 유출이 없었던 것은 아니므로 다음 단계를 건너뛰지 않습니다.

3. **저장소를 여는 설정 변경을 찾습니다.** 이 변경은 관리 이벤트라서 데이터 이벤트를 켜지 않았어도 남습니다.
   - **S3**: CloudTrail 은 `CreateBucket`, `DeleteBucket`, `PutBucketPolicy`, `PutBucketLifecycle` 같은 버킷 수준 호출을 기본으로 남깁니다[2]. 이벤트 이름이 API 이름과 다른 경우가 있어서, `PutBucketLifecycleConfiguration` 은 `PutBucketLifecycle` 로, `DeletePublicAccessBlock` 은 `DeleteAccountPublicAccessBlock` 으로 찾습니다[2]. `PutBucketVersioning` 의 `requestParameters` 에 `Suspended` 가 들어 있으면 버전 관리를 멈춘 기록입니다[11]. 다른 계정이 이메일 주소로 권한을 주는 객체 ACL 을 설정하면 교차 계정 (cross-account) 기록이 되고, 버킷 소유자가 받는 로그에는 그 계정이 ACL 호출을 했다는 사실만 있고 받는 사람의 이메일 주소와 권한 내용은 없습니다[2]. 버킷 목록 조회 `ListBuckets` 도 앞 단계의 정찰로 볼 수 있고, Sigma 규칙은 `userIdentity.type` 이 `AssumedRole` 인 기록을 뺍니다[11].
   - **EBS 스냅숏**: 디스크 스냅숏을 다른 계정이나 모두에게 여는 작업은 `ec2.amazonaws.com` 의 `ModifySnapshotAttribute` 이고[11], 속성은 `createVolumePermission`, 공개할 때 그룹 이름은 `all` 입니다[8]. 기본 AWS 관리형 키로 암호화한 스냅숏은 공유할 수 없고, 공개 공유는 암호화하지 않은 스냅숏만 됩니다[8]. 공유한 스냅숏을 누가 복사하거나 볼륨으로 만들면 `SharedSnapshotCopyInitiated`, `SharedSnapshotVolumeCreated` 가 CloudTrail 에 남습니다[8]. 인스턴스를 통째 내보내는 `CreateInstanceExportTask` 도 함께 봅니다. Sigma 규칙 "AWS EC2 VM Export Failure" 는 이 이벤트를 잡되 `errorMessage`·`errorCode` 가 있거나 `responseElements` 에 `Failure` 가 든 기록은 뺍니다[11].
   - **Google Cloud Storage**: 버킷 IAM 정책 설정과 객체 ACL 설정은 관리 활동 감사 로그에 남지만, 객체를 만들 때 처음 붙인 ACL 은 남지 않습니다[17]. 권한 이름으로는 `storage.buckets.setIamPolicy` 를 찾습니다[20]. 버킷 목록 조회(`storage.buckets.list`·`listChannels`)와 버킷 생성·변경·삭제(`storage.buckets.insert`·`update`·`patch`·`delete`)는 Sigma 규칙이 `gcp.audit.method_name` 으로 잡습니다[30].
   - **Azure Storage**: 계정 키를 받는 권한은 `Microsoft.Storage/storageAccounts/listkeys/action`, 계정 SAS 를 만드는 권한은 `Microsoft.Storage/storageAccounts/listAccountSas/action` 입니다[16]. 이 권한에 해당하는 작업을 [활동 로그](../../02-artifacts/azure/activity-log.md) 에서 찾되, 실제 작업 이름 문자열은 실제 로그에서 확인합니다. SAS 토큰을 만든 일 자체는 감사할 수 없습니다[15].

4. **객체 읽기 기록을 주체·IP·객체별로 묶습니다.** 서비스마다 보는 필드가 다릅니다.
   - **S3 CloudTrail**: `eventName` 이 `GetObject` 인 레코드를 `requestParameters` 의 `bucketName`·`key`, `userIdentity.arn`, `sourceIPAddress`, `userAgent` 로 묶습니다[7]. 익명 요청은 `userIdentity.accountId` 가 `anonymous` 입니다[7]. 객체 수준 로그는 요청한 계정에 항상 가고, 객체 소유자가 달라도 버킷 소유자에게도 갑니다[2]. 아래는 만든 예시입니다.

     ```json
     {
       "eventTime": "2026-09-01T02:14:07Z",
       "eventSource": "s3.amazonaws.com",
       "eventName": "GetObject",
       "userIdentity": {
         "type": "IAMUser",
         "accountId": "123456789012",
         "arn": "arn:aws:iam::123456789012:user/example-user",
         "accessKeyId": "AKIAIOSFODNN7EXAMPLE"
       },
       "sourceIPAddress": "203.0.113.25",
       "requestParameters": {
         "bucketName": "example-bucket",
         "key": "finance/2026-q2.xlsx"
       },
       "additionalEventData": {
         "SignatureVersion": "SigV4",
         "AuthenticationMethod": "AuthHeader"
       }
     }
     ```

     `additionalEventData.AuthenticationMethod` 에는 `AuthHeader` 나 `QueryString` 이 들어갑니다[6]. 서버 접근 로그의 인증 방식에서 `QueryString` 은 미리 서명한 URL (presigned URL) 을 뜻하므로[4], CloudTrail 에서 `QueryString` 이 보이면 미리 서명한 URL 로 읽었을 가능성이 있습니다.
   - **S3 서버 접근 로그**: 한 줄이 공백으로 나뉜 필드이고, 요청자 (Requester), 원격 IP, 작업 (Operation), 키 (Key), HTTP 상태, 보낸 바이트 (Bytes Sent), 인증 방식 (Authentication Type) 이 들어 있습니다[4]. 요청자는 요청한 쪽의 정식 사용자 ID (canonical user ID) 이고, IAM 사용자면 사용자 이름과 계정, 넘겨받은 역할이면 그 역할(`arn:aws:sts::123456789012:assumed-role/...` 모양)이 들어가며, 인증하지 않은 요청이면 `-` 입니다[4]. 인증 방식은 `AuthHeader`, `QueryString`, `-`(인증 없음) 중 하나입니다[4]. 보낸 바이트가 있어서 "얼마나 나갔나" 를 셀 때 이 로그를 씁니다. 필드 순서와 줄 모양은 [S3 접근 기록](../../02-artifacts/aws/s3-access-logs.md) 에 있습니다.
   - **Azure Blob**: `OperationName` 이 `GetBlob` 인 줄을 모으고, 응답 크기 `ResponseBodySize` 를 컨테이너별로 더하면 읽은 양을 셀 수 있습니다[14]. Entra ID 로 인증한 요청이면 `RequesterObjectId` 가 주체를 가장 확실하게 가려냅니다[14]. 공유 키 (Shared Key) 와 SAS 인증은 개인을 가려낼 수단이 없어서 `CallerIpAddress`·`UserAgentHeader` 만 단서로 남습니다[14]. SAS 토큰 자체는 로그에 남지 않고 서명의 SHA-256 해시가 `AuthenticationHash` 에 남으므로, 배포한 토큰의 서명을 같은 방법으로 해시해 대조합니다[14]. 인증 방식의 철자는 Log Analytics 쿼리 예시에서는 `SAS`[14], 로그 속성 설명에서는 `SAS Key`[34] 로 다르게 나오므로, 실제 로그에서 값별 개수를 먼저 세어 보고 거릅니다.
   - **Google Cloud Storage**: 데이터 접근 감사 로그의 `DATA_READ` 에는 객체 데이터·메타데이터 읽기와 객체 목록이 들어가고, 복사와 합치기는 읽기와 쓰기 두 건으로 남습니다[17]. 다른 버킷으로 다시 쓰기 (rewrite) 를 하면 원본 쪽 GET 기록의 `protoPayload.metadata` 에 복사한 대상 버킷이 `destination` 으로 들어갑니다[17]. 사용 로그에는 사용자 신원 열이 없고 `c_ip`, `cs_operation`(예 `GET_Object`), `cs_object`, `sc_status`, 응답 바이트 `sc_bytes` 가 있습니다[18]. 서명된 URL (signed URL) 은 최대 604800초(7일)까지 유효하고, `X-Goog-Credential` 에 서명한 자격 증명 정보가 들어가며, 유효 기간 안에는 URL 을 가진 사람이면 누구나 쓸 수 있습니다[19].
   - **SharePoint·OneDrive**: 사이트에서 내려받으면 `FileDownloaded`, OneDrive 동기화 앱(OneDrive.exe)으로 컴퓨터에 내려받으면 `FileSyncDownloadedFull` 이 남습니다[21]. `FileAccessed` 는 같은 사용자·같은 파일이면 5분 동안 다시 남지 않고, 같은 사람이 계속 접근하면 최대 3시간 단위로 `FileAccessedExtended` 가 남습니다[21]. 동기화 요청이면 `MachineId`·`MachineDomainInfo` 로 어느 기기인지 좁힐 수 있고, 회사 도메인 밖 컴퓨터가 동기화하려다 막히면 `UnmanagedSyncClientBlocked` 가 남습니다[21][22].
   - **Google Drive**: `download`, `sync_item_content`, `access_item_content`, `copy`·`source_copy` 가 유출 판단에 쓰는 이벤트입니다[26]. Drive for desktop 으로 동기화하면 Download 와 Item content synced 가 함께 남고, Item content synced 는 2024년 7월 1일 이후 활동부터 있습니다[25]. 앱이 Google Workspace API 로 가져간 파일은 Download·View 가 아니라 Item content accessed 로만 남습니다[25]. 조직 밖 사용자가 조직 파일을 외부로 복사하면 우리 쪽에는 Create·Copy 가 없고 원본에 Copy Type 이 External 인 Source Copy 만 남습니다[25].

5. **평소와 비교해 양과 모양을 봅니다.** 주체마다 하루·시간당 요청 수, 서로 다른 객체 수, 보낸 바이트를 세고 조사 기간 전의 같은 길이 기간과 나란히 놓습니다. 평소 쓰지 않던 IP·사용자 에이전트, 객체 목록 조회(S3 `ListObjects`, GCS 객체 목록) 바로 뒤에 이어지는 연속 읽기, 한밤중 몰아 읽기가 눈여겨볼 모양입니다. 비교를 타임라인으로 엮는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다.

6. **읽은 주체의 자격 증명을 거슬러 올라갑니다.** IAM 역할이면 역할을 넘겨받은 `AssumeRole` 기록으로, 액세스 키면 그 키의 다른 사용 기록으로, Entra ID 주체면 로그인 기록으로 이어 갑니다. 키가 원래 쓰던 곳 밖에서 쓰였다면 [액세스 키가 새어 나갔나](../infrastructure/leaked-keys.md) 의 순서를, 사용자 동의를 받은 앱이 읽었다면 [악성 OAuth 앱에 동의했나](../account-compromise/illicit-consent.md) 의 순서를 따릅니다.

7. **엔드포인트 쪽 흔적을 요청합니다.** 동기화·복사 도구를 쓴 기기가 조사 범위 안에 있으면 그 기기의 흔적으로 클라우드 로그를 뒷받침합니다. rclone 은 인증 정보를 설정 파일 `rclone.conf` 한 곳에 두고, 기본 위치는 Windows 에서 `%AppData%/rclone/rclone.conf`, 그 밖의 시스템에서 `~/.config/rclone/rclone.conf` 이며, 다른 위치는 환경 변수 `RCLONE_CONFIG` 로 정할 수 있습니다[31]. 설정 파일의 비밀번호는 평문이 아니라 난독화 (obscure) 해서 저장합니다[31]. rclone 1.56.1 로 시험한 결과에서는 파일의 시각은 보존했지만 폴더의 시각은 모두 복사를 실행한 시각이 되었고, 네트워크 캡처로 rclone 연결을 가려내는 일은 SSH/SFTP 말고는 거의 불가능했습니다[31]. 기기 분석은 [[windows] 포렌식 조사 절차](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/investigation-process.html) 를, 클라우드 가상 머신 안을 볼 때는 [[linux] 클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html) 을 따릅니다.

## 기록이 증명하는 것과 증명하지 못하는 것

**증명하는 것.** 해당 시각(UTC)에 해당 주체(ARN·UPN·`RequesterObjectId`·`principalEmail`)가 해당 객체에 읽기 요청을 했고 서비스가 어떤 상태 코드로 응답했는지를 증명합니다. S3 서버 접근 로그의 보낸 바이트, `StorageBlobLogs` 의 `ResponseBodySize`, GCS 사용 로그의 `sc_bytes` 는 응답으로 나간 크기를 보여 줍니다[4][13][18]. 설정 변경 기록은 저장소를 연 때와 연 주체를 보여 줍니다.

**증명하지 못하는 것.** 받은 쪽 기기에 파일이 저장되었는지, 지금도 남아 있는지는 보여 주지 않습니다. Azure 의 SAS·공유 키 인증은 개인을 가려낼 수단이 없어 IP 와 사용자 에이전트만 단서로 남습니다[14]. GCS 서명된 URL 은 URL 을 가진 누구나 쓸 수 있어서, 서명한 자격 증명이 곧 읽은 사람을 뜻하지 않습니다[19]. 기록 설정이 꺼져 있던 구간은 읽었는지 안 읽었는지 판단할 수 없습니다. GCS 에서 콘솔 밖의 인증된 브라우저 다운로드는 데이터 접근 로그의 `principalEmail`·`callerIp` 가 가려지고, 공개 객체에 대한 접근은 감사 로그가 아예 추적하지 않아 사용 로그로만 볼 수 있습니다[17]. SharePoint 의 `FilePreviewed` 와 `FileAccessed` 구분은 사용자의 의도를 보장하지 않고, 브라우저 미리 가져오기로도 기록이 생깁니다[21].

## 흔한 오판

- **읽기 기록이 없으니 안 빼 갔다고 봅니다.** 데이터 이벤트·데이터 접근 감사 로그·진단 설정이 꺼져 있었으면 기록이 없는 것이 정상입니다. S3 는 읽기·쓰기 선택과 접두사 선택 때문에 일부만 남을 수도 있습니다[1].
- **서버 접근 로그·사용 로그·Blob 로그를 빠짐없는 기록으로 봅니다.** 세 로그 모두 최선 노력으로 기록·전달해서 빠지거나 늦을 수 있고, S3 서버 접근 로그와 GCS 사용 로그는 같은 기록이 두 번 나오기도 합니다[5][14][18]. GCS 사용 로그에서 같은 기록이 두 번 나오면 `s_request_id` 로 겹친 줄을 지웁니다[18].
- **CloudTrail 에 실패한 요청이 모두 남는다고 봅니다.** CloudTrail 은 권한 거부 (AccessDenied) 와 익명 요청은 남기지만, 자격 증명이 틀린 인증 실패와 301 리디렉션 실패는 남기지 않습니다[3]. 버킷을 판별할 수 없는 잘못된 요청은 서버 접근 로그에도 남지 않습니다[4]. VPC 엔드포인트 정책이 막은 요청은 두 로그 모두 요청자와 버킷 소유자에게 전달되지 않습니다[3].
- **Azure 익명 요청 기록을 전체로 봅니다.** 익명 요청은 성공, 서버 오류, 시간 초과, 304 로 실패한 GET 만 남고 나머지 실패한 익명 요청은 남지 않습니다[14].
- **`app@sharepoint` 나 시스템 계정의 대량 `FileAccessed` 를 사람의 행동으로 읽습니다.** `app@sharepoint` 는 SharePoint App-Only 권한을 받은 앱이고, 보존 정책을 적용하면서 검색과 파일 접근을 대량으로 만듭니다[21]. Insider Risk Management 에서 사례를 만들고 Content Explorer 를 켜도 `FileAccessed` 가 생기며, 이 기록은 `ApplicationId` 로 가려냅니다[21].
- **`ClientIP` 를 사용자 기기의 IP 로 단정합니다.** 웹용 Office 처럼 사용자를 대신해 서비스를 부른 신뢰된 앱의 IP 일 수 있습니다[22].
- **Drive 다운로드만 보고 끝냅니다.** Takeout 다운로드, 오프라인 브라우저 캐시, Gmail 에서 첨부로 보낸 Drive 항목은 Download 로 남지 않습니다[25]. Takeout 은 [퇴사자가 자료를 가져갔나](departing-employee.md) 에서 다룹니다.
- **수집 도구의 기본 목록을 전체로 믿습니다.** DFIR-O365RC 의 `Get-O365Light` 가 SharePoint·OneDrive 에서 모으는 관심 작업 목록에는 `AnonymousLinkCreated`·`UnmanagedSyncClientBlocked` 등은 있지만 `FileDownloaded`·`FileSyncDownloadedFull` 은 없습니다[33]. 내려받기를 조사하려면 `Get-O365Full` 을 쓰거나 레코드 유형을 지정해 받습니다[33]. Microsoft-Extractor-Suite 의 `Get-UAL -Group Sharepoint` 는 `SharePointFileOperation`·`SharePointSharingOperation` 등 SharePoint 레코드 유형을 묶어 받습니다[32]. 수집 도구는 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md) 와 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md) 에 있습니다.

## 보고서 문장 예

- "2026년 9월 1일 02:14(UTC)부터 03:40(UTC)까지 IAM 사용자 example-user 의 액세스 키 AKIAIOSFODNN7EXAMPLE 로 서명한 `GetObject` 요청 1,284건이 버킷 example-bucket 에 대해 CloudTrail 데이터 이벤트로 남아 있다. 요청의 출발지 IP 는 모두 203.0.113.25 이다." (만든 예시)
- "같은 시간대 S3 서버 접근 로그에서 이 요청자의 `REST.GET.OBJECT` 줄의 보낸 바이트를 더하면 약 4.2GB 이다. 서버 접근 로그는 최선 노력으로 전달되므로 이 값은 기록된 요청만의 합계이다." (만든 예시)
- "2026년 8월 20일 이전에는 이 버킷에 데이터 이벤트와 서버 접근 로깅이 모두 설정되어 있지 않아, 그 이전의 객체 읽기 여부는 판단할 수 없다." (만든 예시)
- 쓰지 않을 문장: "직원 A 가 고객 자료를 외부로 빼돌렸다." 로그는 어떤 자격 증명으로 서명한 읽기 요청이 있었다는 것까지 보여 주고, 그 자격 증명을 누가 썼는지와 받은 자료를 어디에 두었는지는 보여 주지 않습니다. 문장을 다듬는 방법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 같은 분류: [퇴사자가 자료를 가져갔나](departing-employee.md), [외부 공유 링크로 새어 나갔나](external-sharing.md)
- 자격 증명에서 이어지는 경우: [액세스 키가 새어 나갔나](../infrastructure/leaked-keys.md), [악성 OAuth 앱에 동의했나](../account-compromise/illicit-consent.md), [로그를 끄거나 지웠나](../infrastructure/log-tampering.md)
- 개념: [로그의 종류](../../01-foundations/logging/log-types.md), [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md), [탐지 규칙으로 로그 검색하기](../../03-techniques/analysis/detection-rules.md)
- 다른 판: [[windows] 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html), [[ai] 보안 제품이 남기는 AI 사용 기록 (DLP·CASB)](https://urock-ailab.github.io/forensics-handbook/ai/02-artifacts/network-enterprise/dlp-casb.html)

## 참고 문헌

1. AWS, "Logging data events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html
2. AWS, "Amazon S3 CloudTrail events", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudtrail-logging-s3-info.html
3. AWS, "Logging options for Amazon S3", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/logging-with-S3.html
4. AWS, "Amazon S3 server access log format", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/LogFormat.html
5. AWS, "Logging requests with server access logging", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html
6. AWS, "CloudTrail log file entries for Amazon S3 and S3 on Outposts", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudtrail-logging-understanding-s3-entries.html
7. AWS, "Identifying Amazon S3 requests using CloudTrail", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudtrail-request-identification.html
8. AWS, "Share an Amazon EBS snapshot with other AWS accounts", Amazon EBS User Guide. https://docs.aws.amazon.com/ebs/latest/userguide/ebs-modifying-snapshot-permissions.html
9. AWS, "GuardDuty finding types", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-active.html
10. AWS, "Working with CloudTrail event history", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
11. SigmaHQ, aws_s3_data_management_tampering.yml, aws_disable_bucket_versioning.yml, aws_snapshot_backup_exfiltration.yml, aws_ec2_vm_export_failure.yml, aws_enum_buckets.yml. https://github.com/SigmaHQ/sigma/tree/master/rules/cloud/aws/cloudtrail
12. Microsoft, "Resource logs in Azure Monitor" (resource-logs.md). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
13. Microsoft, "StorageBlobLogs", Azure Monitor table reference. https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/storagebloblogs
14. Microsoft, "Best practices for monitoring Azure Blob Storage" (blob-storage-monitoring-scenarios.md) 와 "Monitor Azure Blob Storage" (monitor-blob-storage.md). https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/storage/blobs/blob-storage-monitoring-scenarios.md , https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/storage/blobs/monitor-blob-storage.md
15. Microsoft, "Grant limited access to Azure Storage resources using shared access signatures (SAS)". https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview
16. Microsoft, "Azure permissions for Storage". https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/storage
17. Google Cloud, "Cloud Audit Logs with Cloud Storage". https://cloud.google.com/storage/docs/audit-logging
18. Google Cloud, "Usage logs & storage logs". https://cloud.google.com/storage/docs/access-logs
19. Google Cloud, "Signed URLs". https://cloud.google.com/storage/docs/access-control/signed-urls
20. Google Cloud, "IAM permissions for JSON methods". https://cloud.google.com/storage/docs/access-control/iam-json
21. Microsoft, "Audit log activities", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-log-activities
22. Microsoft, "Office 365 Management Activity API schema". https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
23. Microsoft, "Search the audit log", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-search
24. Microsoft, "Manage audit log retention policies", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
25. Google, "Drive log events", Google Workspace Admin Help. https://support.google.com/a/answer/4579696
26. Google, "Drive Audit Activity Events", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/drive
27. Google, "Data retention and lag times", Google Workspace Admin Help. https://support.google.com/a/answer/7061566
28. SigmaHQ, microsoft365_susp_oauth_app_file_download_activities.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_susp_oauth_app_file_download_activities.yml
29. SigmaHQ, microsoft365_data_exfiltration_to_unsanctioned_app.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_data_exfiltration_to_unsanctioned_app.yml
30. SigmaHQ, gcp_bucket_enumeration.yml, gcp_bucket_modified_or_deleted.yml. https://github.com/SigmaHQ/sigma/tree/master/rules/cloud/gcp/audit
31. Frank Breitinger, Xiaolu Zhang, Darren Quick. "A forensic analysis of rclone and rclone's prospects for digital forensic investigations of cloud storage". Forensic Science International: Digital Investigation 43 (2022) 301443. https://doi.org/10.1016/j.fsidi.2022.301443
32. Invictus Incident Response, Microsoft-Extractor-Suite, Scripts/Get-UAL.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-UAL.ps1
33. ANSSI-FR, DFIR-O365RC, DFIR-O365RC/Get-O365.ps1. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-O365.ps1
34. Microsoft, "Azure Blob Storage monitoring data reference". https://learn.microsoft.com/en-us/azure/storage/blobs/monitor-blob-storage-reference
