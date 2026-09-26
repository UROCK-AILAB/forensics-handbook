---
title: "Vault와 Takeout"
parent: "아티팩트 · Google Workspace"
nav_order: 340
---

# Vault와 Takeout (Vault·Takeout)

Google Vault 와 Google Takeout 은 Workspace 자료의 사본을 만드는 기능이고, 조사에서는 두 가지로 쓰입니다. 하나는 조사자가 Vault 로 메일·파일을 보존하고 내보내 증거 사본을 얻는 것이고, 다른 하나는 누가 Vault 나 Takeout 으로 자료를 꺼내 갔는지를 Vault 로그 이벤트와 Takeout 로그 이벤트로 밝히는 것입니다.

## 무엇을 기록하나 · 왜 생기나

Google Vault 는 Workspace 의 정보 관리·전자 증거 개시 (eDiscovery) 도구로, 사용자 자료를 보존하고 보류 (hold) 하고 검색하고 내보냅니다[1]. 대상은 Gmail 메시지, Drive 파일, Calendar 일정, 대화 기록을 켠 Chat 메시지, Meet 녹화와 채팅·Q&A·설문 로그, Groups 메시지, Voice(애드온 구독만), Sites, Gemini 앱 메시지입니다[1][8]. Vault 는 별도 보관소가 아니라 각 서비스의 데이터에 규칙을 직접 적용하는 방식이라[1][2], 보존 규칙이나 보류를 걸기 전에는 아무것도 붙잡지 않습니다. 규칙을 만들기 전에는 사용자가 자료를 지울 수 있고 서비스는 제 절차대로 자료를 없앱니다[1].

Vault 안에서 한 일은 Vault 로그 이벤트로 남습니다. 보존 규칙을 만들거나 고친 일, 검색한 일, 내보낸 일, 내보낸 파일을 내려받은 일, 문서를 열어 본 일이 여기에 들어가고[1][11], 이 감사 기록은 편집할 수 없습니다[1]. Vault 로 자료를 꺼내 가는 것도 조직 자료를 빼내는 한 경로라서, 관리자 계정 침해나 내부자 조사에서는 이 기록을 함께 봅니다.

Google Takeout 은 사용자가 자기 계정 자료의 사본을 받는 기능입니다[15]. 사용자가 제품을 고르고 전달 방법(메일로 받는 다운로드 링크, Drive, Dropbox, OneDrive, Box)과 형식(zip·tgz), 한 번 또는 예약 내보내기를 정하면 보관 파일 (archive) 을 만듭니다[15]. Workspace 계정의 Takeout 사용은 Takeout 로그 이벤트로 남고, 시작·완료·다운로드·예약이 따로 기록됩니다[12][13]. 퇴사자가 나가기 전에 자기 메일과 Drive 를 통째로 받아 간 일이 있는지 볼 때 먼저 찾는 기록입니다.

관리자용으로는 이 밖에 데이터 내보내기 도구 (Data Export tool) 가 있습니다. 최고 관리자가 조직 자료를 Google Cloud Storage 로 내보내는 기능이고, Takeout 과 같은 자료에 더해 Vault 가 붙잡아 둔 지운 자료와 관리 격리 메일 같은 조직 소유 자료까지 담깁니다[16].

## 위치와 버전별 차이

### 어디서 보나

| 무엇 | 관리 콘솔 | 보고서 API (Reports API) | 보관(2026년 9월 문서 기준) | 들어오는 지연 |
|---|---|---|---|---|
| Vault 로그 이벤트 | Security > Security center > Investigation tool 에서 데이터 원천 Vault log events[11] | `applicationName=vault`[10] | 무기한(Indefinite)[17] | 거의 실시간(몇 분)[17] |
| Takeout 로그 이벤트 | Reporting > Audit and investigation > Takeout log events, 또는 보안 조사 도구의 Takeout log events[13] | `applicationName=takeout`[12] | 보관 표에 따로 없음. 표에 없는 로그는 대체로 6개월[17] | 시작 이벤트는 거의 실시간, 끝 이벤트는 자료 크기에 따라 며칠까지[17] |

보고서 API 요청 모양과 레코드 공통 구조, 관리 콘솔 검색 기본 범위(최근 7일)와 내보내기 행 수 한도는 [관리 콘솔 감사 로그](admin-audit.md) 에서 다룹니다. 관리자는 로그 이벤트를 지우거나 보관 기간을 바꿀 수 없습니다[17]. Workspace 로그 보관 기간 전체 비교는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에 있습니다.

### 에디션·라이선스(2026년 9월 문서 기준)

| 기능 | 조건 |
|---|---|
| Vault 사용 | 2025년 11월 1일부터 관리자도 Vault 라이선스가 있어야 씁니다. Vault 가 포함된 에디션은 Frontline Standard·Plus, Business Plus, Enterprise Standard·Plus, 모든 Education 에디션, Enterprise Essentials·Essentials Plus(도메인 인증한 경우만), G Suite Business 이고, 그 밖은 애드온 라이선스를 삽니다. 사용자도 라이선스가 있어야 검색·보존 대상이 됩니다[1] |
| 보안 조사 도구의 Vault log events | Frontline Standard·Plus, Business Plus, Enterprise Standard·Plus, Education Fundamentals·Standard·Plus, Enterprise Essentials·Essentials Plus, G Suite Business[11] |
| Takeout log events(감사 및 조사 페이지) | 검색 대상 사용자의 에디션과 관계없이 검색할 수 있고, Audit & Investigation 관리자 권한이 필요합니다[13] |
| Takeout log events(보안 조사 도구) | Frontline Standard·Plus, Enterprise Standard·Plus, Education Standard·Plus, Enterprise Essentials Plus, Cloud Identity Premium[13] |
| Takeout 허용 여부 | Data > Data import & export > Google Takeout 에서 조직 단위·그룹별로 정합니다. 기본값은 Workspace 가 Allowed, Education K-12 는 공유 제어가 Not Allowed 이고, 바꾼 설정은 반영까지 최대 24시간 걸립니다[14] |
| 데이터 내보내기 도구 | 만든 지 30일이 지난 최고 관리자 계정(조직 계정이 30일 안에 만들어졌으면 예외)과 2단계 인증이 필요합니다. 사용자·조직 단위·그룹을 골라 내보내는 기능은 에디션에 따라 다릅니다[16] |

Takeout 허용 설정에는 Drive·Gmail·Calendar·Contacts 같은 서비스를 한꺼번에 정하는 공유 제어와, Blogger·Books·Maps·Pay·Photos·Play·Play Console·Location History·YouTube 를 하나씩 정하는 개별 제어가 있습니다[14]. 사건 당시 Takeout 이 막혀 있었는지는 이 화면의 현재 값만으로는 알 수 없으므로, [관리 콘솔 감사 로그](admin-audit.md) 에서 Takeout 설정 이름으로 변경 기록을 검색해 확인합니다.

## 구조

### Vault 로그 이벤트

Vault 로그 이벤트의 `events[].type` 은 모두 `user_action` 이고, 이벤트 이름은 87종입니다[10]. 많은 작업이 시작(`_begin`)과 끝(`_end`) 두 이벤트로 나뉘어 남습니다[10]. 모든 이벤트에 같은 매개변수 일곱 개가 붙습니다[10].

| 매개변수 | 뜻 | 관리 콘솔 속성 이름[11] |
|---|---|---|
| `additional_details` | 부가 정보(보존 기간·조건 등) | Additional details |
| `matter_id` | 사건 (matter) ID. 사건과 관련된 이벤트에만 있음 | Matter ID |
| `organizational_unit_name` | 작업이 적용된 조직 단위 | Organizational unit name |
| `query` | 검색·내보내기에 입력한 검색 조건 | Query |
| `resource_name` | 보류 이름, 저장한 검색 이름 같은 대상 이름 | Resource name |
| `resource_url` | 열어 본 문서의 URL | Resource URL |
| `target_user` | 대상 사용자(보류를 건 사용자 등) | Target user |

이벤트 이름에서 `investigation` 은 Vault 화면의 사건을 가리킵니다. `view_investigation` 의 콘솔 문구가 "User viewed a matter" 입니다[10]. 조사에 자주 쓰는 이벤트는 아래와 같습니다[10].

| 묶음 | 이벤트 이름 | 콘솔 문구 |
|---|---|---|
| 내보내기 | `create_export_begin`·`create_export_end`, `export` | Export creation began/ended, User performed an export |
| 내려받기 | `export_file_download`, `legacy_export_download`, `download_count_per_account_csv` | User downloaded an export file, User downloaded a legacy export, User downloaded count CSV results |
| 내보내기 삭제 | `delete_export_begin`·`delete_export_end`·`delete_export_fail` | Export deletion began/ended/failed |
| 검색·열람 | `search`, `search_count`, `get_count_operation`, `view_document`, `view_document_information`, `view_external_document` | User performed a search, User ran a count search, User viewed a document 등 |
| 보류 | `add_litigation_hold_begin`·`_end`, `remove_litigation_hold_begin`·`_end` | Litigation hold addition/removal began/ended |
| 보존 규칙 | `add_retention_rule_*`, `update_retention_rule_*`, `delete_retention_rule_*`, `modify_default_retention_period_*`, `update_retention_settings` | Retention rule addition/update/deletion began/ended, User updated retention settings |
| 빠른 삭제 | `create_accelerated_deletion_*`, `cancel_accelerated_deletion_*`, `deletion_search` | Accelerated deletion request creation began 등, User performed a deletion search |
| 사건 관리 | `create_investigation_*`, `close_investigation_*`, `delete_investigation_*`, `reopen_investigation_*`, `add_collaborator_*`, `remove_collaborator_*` | Investigation creation began 등, Collaborator addition began 등 |
| 감사 기록 열람 | `view_system_audit_log`, `view_matter_audit_log` | User viewed the system's log events, User viewed a matter's log events |

### Takeout 로그 이벤트

Takeout 로그 이벤트의 `events[].type` 은 `USER_TAKEOUT` 이고 이벤트는 네 가지입니다[12].

| 이벤트 이름 | 콘솔 문구 | 매개변수 |
|---|---|---|
| `STARTED_USER_TAKEOUT` | `{actor} performed a user takeout` | INITIATED_BY, PRODUCTS_REQUESTED, START_TIME, TAKEOUT_DESTINATION, TAKEOUT_ID, USER_EMAIL |
| `COMPLETED_USER_TAKEOUT` | `{actor} user takeout {TAKEOUT_STATUS}` | COMPLETION_TIME, INITIATED_BY, PRODUCTS_REQUESTED, TAKEOUT_DESTINATION, TAKEOUT_ID, TAKEOUT_STATUS, USER_EMAIL |
| `DOWNLOADED_USER_TAKEOUT` | `{actor} downloaded a user takeout` | DOWNLOAD_TIME(다운로드 시작 시각), PRODUCTS_REQUESTED, TAKEOUT_ID, USER_EMAIL |
| `SCHEDULED_USER_TAKEOUT` | `{actor} scheduled user takeout(s)` | PRODUCTS_REQUESTED, SCHEDULED_TAKEOUT_EXPIRATION, TAKEOUT_DESTINATION, TAKEOUT_INTERVAL_UNITS, TAKEOUT_INTERVAL_VALUE, TAKEOUT_STATUS, USER_EMAIL |

`TAKEOUT_DESTINATION` 값은 `BOX`, `DRIVE`, `DROPBOX`, `EMAIL`, `ONEDRIVE`, `UNKNOWN` 이고, `EMAIL` 은 메일로 받은 다운로드 링크로 로컬 저장소에 받았다는 뜻입니다[12]. `TAKEOUT_STATUS` 는 `CANCELED`, `COMPLETED`, `FAILED`, `IN_PROGRESS` 가운데 하나이고, `TAKEOUT_INTERVAL_UNITS` 는 `DAY`, `WEEK`, `MONTH` 가운데 하나입니다[12]. 관리 콘솔에서 `INITIATED_BY` 는 Takeout initiator 로 보이고 값은 `USER` 또는 `TAKEOUT_SCHEDULER` 이며, `USER_EMAIL` 은 Target(자료를 내보낸 사용자), `TAKEOUT_ID` 는 Takeout job ID 로 보입니다[13]. `START_TIME`·`COMPLETION_TIME`·`DOWNLOAD_TIME`·`SCHEDULED_TAKEOUT_EXPIRATION` 은 정수형이고[12], 단위는 검체에서 확인합니다(아래 시각 해석).

아래는 보고서 API 가 돌려주는 Takeout 시작 활동을 문서의 레코드 모양대로 만든 예시입니다. 메일 주소·IP·ID 는 모두 만든 예시 값입니다.

```json
{
  "kind": "audit#activity",
  "id": {
    "time": "2026-03-02T01:15:42.118Z",
    "uniqueQualifier": "-1234567890123456789",
    "applicationName": "takeout",
    "customerId": "C03az79cb"
  },
  "actor": { "callerType": "USER", "email": "user@example.com" },
  "ipAddress": "203.0.113.25",
  "events": [{
    "type": "USER_TAKEOUT",
    "name": "STARTED_USER_TAKEOUT",
    "parameters": [
      { "name": "INITIATED_BY", "value": "USER" },
      { "name": "TAKEOUT_DESTINATION", "value": "DROPBOX" },
      { "name": "TAKEOUT_ID", "value": "example-takeout-job-0001" },
      { "name": "USER_EMAIL", "value": "user@example.com" }
    ]
  }]
}
```

### Vault 내보내기 파일

Vault 내보내기는 검색 조건에 맞는 자료의 사본, 그 자료를 사용자와 잇는 메타데이터, 서버의 자료와 같다는 것을 보이는 확인 정보를 함께 담습니다[7]. 서비스마다 파일 구성이 다르고, 모든 서비스에 내보낸 파일 전부의 MD5 목록(File checksums)이 들어갑니다[7].

| 서비스 | 주요 파일 | 알아 둘 점 |
|---|---|---|
| Gmail | `export_name-N.zip`(안에 `export_name-account-randomstring.mbox` 또는 `.pst`), `export_name-metadata.csv`·`.xml`, `export_name-result-counts.csv`, `export_name-errors.xml`, `export_name-drive-links.csv`(옵션), `export_name-conversion_errors-N.zip` | 계정의 메시지가 PST 1GB·mbox 10GB 를 넘으면 zip 여러 개로 나뉩니다. `errors.xml` 은 오류가 없어도 늘 들어 있고, PST 로 바꾸지 못한 메시지는 Message-ID 헤더 값을 이름으로 한 EML 로 따로 담깁니다[7] |
| Groups·Chat | `export_name-N.zip`, `export_name-group-membership.csv`, `export_name-metadata.xml`·`.csv`, `export_name-results-count.csv`, 오류가 있을 때만 `export_name-error.csv` | Chat 메시지에는 보낸 사람이 고치거나 지운 정보가 들어 있고, 구성원 CSV 에는 가입 시각과 역할(MEMBER·MANAGER·OWNER)이 있습니다[7] |
| Drive | `export_name_N.zip`(10GB 단위), `export_name-metadata.xml`, `export_name-custodian-docid.csv`, 오류가 있을 때만 `export_name-error.csv`·`export_name-incomplete-accounts.csv` | 파일 이름은 원래 이름 뒤에 `_` 와 Drive 파일 ID 가 붙습니다. Docs 는 DOCX, Sheets 는 XLSX, Slides 는 PPTX, Forms 는 ZIP(HTML·CSV), Drawings 는 PDF 로 바뀌고, 클라이언트 측 암호화 파일은 `.gcse` 로 암호화된 채 나옵니다[7] |

Gmail 메타데이터의 열은 아래와 같습니다[7].

| 열 | 뜻 |
|---|---|
| Rfc822MessageId | 보낸 쪽과 받은 쪽이 같은 메시지 ID. mbox 의 메시지와 맞출 때 씀(CSV 만) |
| GmailMessageId / DocId | Gmail 안의 고유 메시지 ID(GmailMessageId 는 CSV, DocId 는 XML) |
| Account | 그 메시지를 가진 계정. 그룹 주소로 받은 메일이면 To 는 그룹 주소이고 Account 는 구성원 계정 |
| From, To, CC, BCC, Subject, Labels | 보낸 사람, 받는 사람, 참조, 숨은 참조, 제목, 라벨 |
| DateSent | 보낸 시각(UTC). 형식 `yyyy-MM-dd'T'HH:mm:ssZZZZ` |
| DateReceived | 받은 시각. 형식 `yyyy-MM-dd'T'HH:mm:ssZZZZ` |
| LabelName | Gmail 분류 라벨(XML 만) |

`result-counts.csv` 에는 계정별 AccountStatus(`Success`, `PartialAccountError`, `AccountError`), SuccessCount, MessageErrorCount 가 있고 첫 줄은 합계입니다[7]. Drive 메타데이터에는 DocID, #Author(소유자, 공유 드라이브면 드라이브 이름), Collaborators, Viewers, Others, #DateCreated, #DateModified, #Title, DocumentType, SharedDriveID, LabelName, SourceHash, FileName, FileSize, Hash(MD5), ClientSideEncrypted, Reviews 가 있습니다[7]. SourceHash 는 파일의 판마다 다른 해시로, 중복을 걸러 내거나 내보낸 파일이 원본과 같은지 확인할 때 쓰고 Docs·Sheets·Slides 에만 있습니다[7]. Drive 와 Groups·Chat 메타데이터에는 내보내기 전체의 UserQuery(검색 조건), TimeZone(날짜 검색에 쓴 시간대), Custodians(검색한 계정)도 들어 있습니다[7].

Vault API 로 내보내기를 조회하면 `matters.exports` 자원에 `id`, `matterId`, `name`, `requester`(`email`, `displayName`), `query`, `exportOptions`, `createTime`, `status`(`COMPLETED`, `FAILED`, `IN_PROGRESS`), `stats`(`exportedArtifactCount`, `totalArtifactCount`, `sizeInBytes`), `cloudStorageSink.files[]`(`bucketName`, `objectName`, `size`, `md5Hash`)가 들어 있습니다[9]. `requester` 로 내보내기를 만든 계정을, `query` 로 무엇을 찾았는지를 Vault 로그와 따로 맞춰 볼 수 있습니다.

### Takeout 보관 파일

Takeout 보관 파일은 고른 최대 크기를 넘으면 여러 파일로 나뉘고, 안에 파일 형식과 여는 법을 설명하는 `archive_browser.html` 이 들어 있습니다[15]. Gmail 메일을 내보내면 각 메시지의 라벨이 `X-Gmail-Labels` 헤더에 담깁니다[15]. 보관 파일은 약 7일 뒤 만료되고 한 보관 파일은 5번까지만 내려받을 수 있습니다(2026년 9월 문서 기준)[15].

## 증거로서 의미

**증명하는 것**

- Vault 로그: 어느 계정이 언제 어느 사건에서 어떤 검색 조건으로 검색했고, 무엇을 내보내고 내려받았는지, 어떤 보류·보존 규칙을 만들거나 고치거나 지웠는지를 보여 줍니다[10][11]. `resource_url` 로 Vault 안에서 열어 본 문서를 알 수 있습니다[11].
- Takeout 로그: 어떤 사용자의 자료를, 어떤 제품 범위로, 어디로(Drive·Dropbox·OneDrive·Box·메일 링크) 내보내기 시작했고 끝났는지, 보관 파일을 내려받기 시작했는지, 예약 내보내기를 걸었는지를 보여 줍니다[12][13]. `TAKEOUT_ID` 로 시작·완료·다운로드 이벤트를 한 작업으로 묶습니다.
- Vault 내보내기 사본: 내보낸 시점에 Google 서버에 있던 메시지·파일과 그 메타데이터를 담고, MD5 목록으로 받은 뒤 사본이 바뀌지 않았음을 보일 수 있습니다[7].

**증명하지 못하는 것**

- Takeout 로그에는 요청한 제품 이름만 있고 보관 파일에 실제로 어떤 메일·파일이 들어갔는지는 없습니다[12]. 지우는 중인 자료는 보관 파일에 들어가지 않고, 요청한 뒤 보관 파일이 만들어지기 전의 변경은 빠질 수 있습니다[15].
- 받은 보관 파일을 그 뒤 어디로 옮겼는지는 Takeout 로그로 알 수 없습니다. Dropbox·OneDrive·Box 로 보냈다면 그 뒤는 그 서비스의 기록을 봐야 합니다.
- 기록된 IP 는 사용자의 실제 위치가 아니라 프록시나 VPN 주소일 수 있습니다[13].
- Vault 는 보존 규칙이나 보류가 없던 기간에 사용자가 지우고 휴지통까지 비운 Drive 항목, 규칙이 끝나기 30일 넘게 전에 지운 Gmail 메시지를 되살리지 못합니다. 앞의 것은 곧바로 Vault 에서 보이지 않고, 뒤의 것은 보존 기간이 끝나는 즉시 지워집니다[2].
- 외부에서 받은 기밀 모드 메일은 헤더와 제목만 보존·검색·내보내기되고 본문과 첨부는 없습니다[8]. AMP 동적 메일은 HTML·평문·AMP 마크업만 보존되고, 사용자가 열 때 받아 온 동적 내용은 보존되지 않습니다[8].

보고서에는 "2026-03-02 01:15 UTC 에 user@example.com 계정으로 Takeout 내보내기를 시작한 기록이 있고, 전달 대상은 Dropbox 로 기록되어 있다" 처럼 기록이 말하는 만큼만 씁니다. 보고서 문장 전반은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 를 봅니다.

## 시각 해석

- 보고서 API 레코드의 `id.time` 은 문서 설명과 예시가 서로 다르므로, 검체 값의 모양을 보고 판단합니다. 자세한 내용은 [관리 콘솔 감사 로그](admin-audit.md) 에 있습니다.
- Takeout 이벤트의 `START_TIME`·`COMPLETION_TIME`·`DOWNLOAD_TIME` 은 정수형입니다[12]. 같은 레코드의 `id.time` 과 나란히 놓고 초·밀리초·마이크로초 가운데 어느 것으로 풀어야 두 값이 가까워지는지 검체에서 확인합니다. `DOWNLOAD_TIME` 은 다운로드를 시작한 시각이고 끝난 시각이 아닙니다[12].
- 관리 콘솔의 Date 는 브라우저 기본 시간대로 표시되고, 보안 조사 도구는 최고 관리자가 조사 시간대를 바꿀 수 있습니다[11][13]. 화면에서 옮겨 적은 시각은 어느 시간대였는지 함께 적어 둡니다.
- Takeout 완료 이벤트는 자료 크기에 따라 며칠 늦게 들어올 수 있습니다[17]. 시작 이벤트만 있고 완료 이벤트가 없다고 해서 내보내기가 실패했다고 보지 않습니다. 드물게 이벤트가 더 늦거나 아예 보고되지 않을 수도 있습니다[17].
- Vault 내보내기의 Gmail 메타데이터 DateSent 는 UTC 이고, DateReceived 는 시간대 설명 없이 형식만 정해져 있습니다[7]. 두 형식 모두 끝의 `ZZZZ` 자리에 시간대 표기가 붙으므로 값 끝의 시간대 표기를 보고 판단합니다. Groups 메타데이터 CSV 는 두 값 모두 UTC 입니다[7].
- Vault API 의 `createTime` 은 `Z` 로 끝나는 RFC 3339 UTC 문자열입니다[9].
- Drive 메타데이터의 #DateCreated 는 Google 형식이 아닌 파일이면 보통 Drive 에 올린 날짜이지 원래 파일을 만든 날짜가 아닙니다[7].
- 여러 시각 원천을 한 줄로 세우는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 과 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 함정과 한계

- **Takeout 다운로드는 Drive 로그에 없습니다.** Drive 로그 이벤트는 Takeout 다운로드를 기록하지 않으므로 Takeout 로그 이벤트를 따로 검색해야 합니다[18]. Drive 로그에 대량 다운로드가 없다고 해서 자료를 받아 가지 않았다고 볼 수 없습니다. Drive 로그는 [Drive 기록](drive-audit.md) 에서 다룹니다.
- **Takeout 로그는 대체로 6개월만 남습니다.** 보관 기간 표에 Takeout 항목이 따로 없고, 표에 없는 로그의 보관 기간은 대체로 6개월입니다[17]. 퇴사 뒤 한참 지나 조사를 시작하면 이미 사라졌을 수 있으므로 먼저 받아 둡니다. 절차는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 에 있습니다.
- **Vault 내보내기 파일은 15일 뒤 사라집니다.** 내보내기를 시작하고 15일이 지나면 파일과 링크가 지워지고 다시 만들어야 합니다[5][6]. 데이터 내보내기 도구가 Google 제공 버킷에 담은 자료는 시작 60일 뒤 자동으로 지워지고, 자료가 여러 날에 걸쳐 조각으로 들어가므로 일부 조각은 더 일찍 지워질 수 있습니다[16]. 받는 즉시 MD5 목록과 함께 보관합니다.
- **보류를 풀거나 사용자를 지우면 자료가 곧바로 사라질 수 있습니다.** 보류를 지우거나, 관리 대상 (custodian) 에서 빼거나, 사용자의 Vault 라이선스가 없어지거나, 파일 공유가 풀리면 그 자료는 곧바로 보존 규칙을 따르고, 30일 넘게 전에 지운 자료는 즉시 없어질 수 있습니다[3]. 지운 계정은 20일 안에 복구할 수 있지만 삭제 표시된 자료는 보존·보류 보호를 잃고 계정을 되살려도 돌아오지 않습니다[4]. 퇴사자 계정은 지우기 전에 보류부터 겁니다.
- **보존 규칙은 자료를 지우기도 합니다.** 보존 기간이 끝난 자료는 사용자가 지우지 않았어도 서비스에서 삭제되고[2], 규칙을 잘못 바꾸면 보호받지 않던 자료가 즉시 없어질 수 있습니다[2]. 그래서 `delete_retention_rule_*`, `modify_default_retention_period_*`, `create_accelerated_deletion_*`, `remove_litigation_hold_*` 은 자료 파괴 시도의 흔적으로도 읽습니다. 흔적 지우기 조사는 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md) 에서 다룹니다.
- **보류 중이면 계정을 지울 수 없습니다.** 조직 최상위 조직 단위에 보류를 걸면 관리자가 어떤 사용자도 지울 수 없게 됩니다[3].
- **Vault 검색은 색인된 부분만 찾습니다.** Gmail 은 메시지마다 약 1MB(약 250쪽)까지만 색인하고 색인된 부분만 검색되지만, 내보내기에는 메시지 전체가 들어갑니다[8]. 영상·음성·이미지·바이너리 첨부는 파일 이름 같은 메타데이터만 색인됩니다[8]. 메일 본문의 Drive 링크 파일은 보존·보류·검색 대상이 아니고, 내보낼 때 옵션으로만 함께 받을 수 있습니다[8].
- **메타데이터의 ID 는 서비스의 ID 와 다릅니다.** Drive 메타데이터의 DocID 는 Drive 파일 ID 가 아니고, Drive 파일 ID 는 zip 안 파일 이름 뒤에 붙어 있습니다[7]. Drive 로그의 문서 ID 와 맞출 때는 파일 이름 쪽 ID 를 씁니다.
- **내보내기 건수 파일은 PST 변환 실패를 성공으로 셉니다.** `result-counts.csv` 의 성공 수에는 PST 로 바꾸지 못한 메시지도 들어 있으므로 `conversion_errors` 파일을 함께 봅니다[7].
- **다중 관리자 승인은 API 내보내기에는 걸리지 않습니다.** 다중 관리자 승인 (Multi-party approval) 을 켜면 Vault 화면에서 한 내보내기에는 두 번째 관리자의 승인이 필요하지만, Vault API 로 한 내보내기에는 적용되지 않습니다[5]. 승인 기록이 없는 내보내기가 있으면 API 로 만든 것인지 확인합니다.
- **내보낸 사람과 내려받은 사람이 다를 수 있습니다.** 권한이 있으면 다른 사람이 만든 내보내기를 내려받을 수 있으므로[6], `create_export_*` 와 `export_file_download` 의 행위자를 따로 봅니다.
- **사용자 이름을 바꾸면 옛 이름으로 검색되지 않습니다.** Vault·Takeout 로그 모두 이름을 바꾼 사용자는 옛 주소로 검색해도 결과가 나오지 않습니다[11][13].
- **조사자 자신의 활동도 섞입니다.** 조사자가 Vault 에서 검색·내보내기·내려받기를 하면 그 역시 Vault 로그에 남습니다[1]. 조사에 쓴 계정과 시간을 적어 두면 걸러 낼 수 있습니다.

## 직접 분석해 보기

### 원자료로 한 번

1. 보고서 API 에 `applicationName=takeout` 으로 조사 기간을 요청합니다. 요청 주소 모양은 `GET https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/takeout` 이고, 권한 범위는 `https://www.googleapis.com/auth/admin.reports.audit.readonly` 입니다[19]. 특정 이벤트만 보려면 `eventName=STARTED_USER_TAKEOUT` 처럼 붙입니다[12].
2. 활동마다 `events[].parameters[]` 에서 `TAKEOUT_ID` 를 꺼내 같은 작업의 시작·완료·다운로드를 묶습니다. 위 예시라면 `example-takeout-job-0001` 로 `COMPLETED_USER_TAKEOUT` 과 `DOWNLOADED_USER_TAKEOUT` 을 찾습니다.
3. 묶은 작업마다 `actor.email` 과 `USER_EMAIL` 이 같은지 봅니다. 관리 콘솔에서 Actor 는 작업한 사람, Target 은 자료를 내보낸 사용자로 따로 표시됩니다[13].
4. `TAKEOUT_DESTINATION` 이 `DROPBOX`·`ONEDRIVE`·`BOX` 이면 조직 밖 저장소로 간 것이고, `DRIVE` 면 같은 계정의 Drive 에 보관 파일이 생겼을 가능성이 있으므로 [Drive 기록](drive-audit.md) 에서 같은 시간대의 활동을 찾아봅니다.
5. `applicationName=vault` 로 같은 기간을 요청해 `create_export_*`, `export_file_download`, `search` 의 `query`·`matter_id`·`target_user` 를 표로 만듭니다.

### 공개 도구로 한 번

ALFA 는 보고서 API 로 Workspace 감사 로그를 받아 한 줄에 활동 하나인 JSON 파일로 저장합니다[20]. 기본 수집 목록(`config.yml` 의 `logs`)에 `vault` 는 들어 있지만 `takeout` 은 없으므로[20], Takeout 로그는 로그 종류를 지정해 따로 받습니다.

```text
alfa acquire --logtype=takeout --start-time 2026-03-01T00:00:00Z --end-time 2026-03-31T23:59:59Z
alfa acquire --logtype=vault --start-time 2026-03-01T00:00:00Z --end-time 2026-03-31T23:59:59Z
```

`--start-time`·`--end-time` 에 시간대를 적지 않으면 UTC 로 봅니다[20]. ALFA 의 분석 기능은 기본으로 무해하다고 본 활동을 걸러 내므로(`--no-filter` 로 끔)[20], 원자료 보존에는 `acquire` 로 받은 JSON 파일을 씁니다. 수집 도구 설정은 [관리 콘솔 감사 로그](admin-audit.md) 에서 다룹니다.

Vault 내보내기 사본은 먼저 File checksums 의 MD5 값과 받은 파일의 해시를 맞춰 봅니다. 그다음 Gmail 이면 `metadata.csv` 의 Rfc822MessageId 로 mbox 안 메시지를 찾고, Drive 면 메타데이터의 FileName 으로 zip 안 파일을 찾고, 파일 이름 뒤에 붙은 Drive 파일 ID 를 읽습니다[7].

## 교차 검증

- [관리 콘솔 감사 로그](admin-audit.md) — Takeout 허용 설정이나 Vault 권한을 바꾼 관리자 활동, 관리자 권한 부여 기록을 봅니다.
- [Drive 기록](drive-audit.md) — Takeout 이 Drive 로 보낸 보관 파일과, Takeout 이 아닌 경로로 한 다운로드를 찾습니다.
- [Gmail 기록과 메일 검색](gmail.md) — Takeout 다운로드 링크 메일이 온 시각, 보관 파일을 밖으로 보낸 메일을 찾습니다.
- [로그인 기록](login-audit.md) — Takeout 을 시작한 세션의 로그인 IP·시각이 평소와 같은지 봅니다.
- [OAuth 토큰 기록](token-audit.md) — 외부 앱이 Workspace 자료에 접근하도록 권한을 준 기록을 봅니다. Takeout 을 Dropbox·OneDrive·Box 로 보낼 때의 연결 승인은 Google 쪽이 아니라 그 서비스의 연결된 앱 목록에 "Google Download Your Data" 로 남습니다[15].
- [Purview eDiscovery와 보존](../m365/purview-ediscovery.md) — Microsoft 365 에서 같은 역할을 하는 보존·내보내기 기능입니다.
- [퇴사자가 자료를 가져갔나](../../04-scenarios/data-leak/departing-employee.md), [외부 공유 링크로 새어 나갔나](../../04-scenarios/data-leak/external-sharing.md) — 이 쪽의 기록을 조사 흐름으로 묶습니다.
- [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) — 보관 기간이 지난 기록이나 조직 밖 계정 자료가 필요할 때 봅니다.

## 실습

Vault·Takeout 기록은 공개 검체가 드물어서, 조사용이 아닌 시험용 Workspace 조직에서 만들어 풀어 봅니다.

1. 시험 사용자로 Gmail 과 Drive 만 골라 Takeout 을 한 번 실행하고, 전달 방법을 메일 링크로 정합니다. Takeout 로그 이벤트에서 시작·완료·다운로드 세 이벤트를 찾아 `TAKEOUT_ID` 로 묶어 봅니다.
2. 같은 레코드의 `START_TIME` 과 `id.time` 을 나란히 놓고 정수 시각의 단위를 알아내 봅니다. 완료 이벤트가 시작 이벤트보다 몇 분 늦게 들어왔는지도 적어 봅니다.
3. 같은 시간대의 Drive 로그 이벤트에 Takeout 다운로드가 보이는지 확인하고, 보이지 않는 이유를 설명해 봅니다.
4. Vault 에서 사건을 만들고 시험 사용자를 검색해 Gmail 을 mbox 로 내보낸 뒤 내려받습니다. Vault 로그 이벤트에서 `create_investigation_*`, `search`, `create_export_*`, `export_file_download` 을 순서대로 찾아 `matter_id` 와 `query` 를 적어 봅니다.
5. 내보낸 `metadata.csv` 의 DateSent 값 끝에 붙은 시간대 표기를 확인하고, 같은 메시지의 mbox `Date:` 헤더와 비교해 봅니다.
6. File checksums 의 MD5 값과 직접 계산한 해시가 모두 같은지 확인하고, `result-counts.csv` 의 SuccessCount 와 mbox 안 메시지 수가 맞는지 세어 봅니다.

## 참고 문헌

1. Google, "Google Vault", Google Workspace Help. https://support.google.com/vault/answer/2462365
2. Google, "How retention works", Google Vault Help. https://knowledge.workspace.google.com/vault/retention/how-retention-works
3. Google, "Get started with holds in Google Vault", Google Vault Help. https://knowledge.workspace.google.com/vault/holds/get-started-with-holds-in-google-vault
4. Google, "Delete a user with data on hold", Google Vault Help. https://knowledge.workspace.google.com/vault/holds/delete-a-user-with-data-on-hold
5. Google, "Export data from Vault", Google Vault Help. https://knowledge.workspace.google.com/vault/exports/export-data-from-vault
6. Google, "Download an export from Vault", Google Vault Help. https://knowledge.workspace.google.com/vault/exports/download-an-export-from-vault
7. Google, "Vault export contents", Google Vault Help. https://knowledge.workspace.google.com/vault/exports/vault-export-contents
8. Google, "Supported services and data types", Google Vault Help. https://knowledge.workspace.google.com/vault/getting-started/supported-services-and-data-types
9. Google, "REST Resource: matters.exports", Google Vault API. https://developers.google.com/workspace/vault/reference/rest/v1/matters.exports
10. Google, "Vault Audit Activity Events", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/vault
11. Google, "Vault log events", Google Workspace Admin Help. https://knowledge.workspace.google.com/admin/vault/vault-log-events
12. Google, "Takeout Audit Activity Events", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/takeout
13. Google, "Takeout log events", Google Workspace Admin Help. https://knowledge.workspace.google.com/admin/reports/takeout-log-events
14. Google, "Allow or block Google Takeout", Google Workspace Admin Help. https://knowledge.workspace.google.com/admin/users/advanced/allow-or-block-google-takeout
15. Google, "How to download your Google data", Google Account Help. https://support.google.com/accounts/answer/3024190
16. Google, "Export all your organization's data", Google Workspace Admin Help. https://support.google.com/a/answer/100458
17. Google, "Data retention and lag times", Google Workspace Admin Help. https://support.google.com/a/answer/7061566
18. Google, "Drive log events", Google Workspace Admin Help. https://support.google.com/a/answer/4579696
19. Google, "Method: activities.list", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
20. Invictus Incident Response, ALFA (README.md, alfa/cmdline.py, alfa/main/collector.py, alfa/config/config.yml). https://github.com/invictus-ir/ALFA
