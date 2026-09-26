---
title: "Drive 기록"
parent: "아티팩트 · Google Workspace"
nav_order: 310
---

# Drive 기록 (Drive Audit)

Google Workspace 사용자가 Drive·Docs·Sheets·Slides 파일을 만들고, 열고, 내려받고, 공유한 일을 파일 단위로 남기는 감사 로그입니다.

## 무엇을 기록하나 · 왜 생기나

Drive 로그 이벤트 (Drive log events) 는 사용자가 Docs·Sheets·Slides 같은 Google 앱으로 만든 파일과 Drive 에 올린 PDF·Word 파일에서 일어난 동작을 기록합니다[4]. 보고서 API (Reports API) 에서는 `applicationName=drive` 로 가져오고, 이벤트는 크게 파일에 손을 댄 `access` 유형과 공유 권한이 바뀐 `acl_change` 유형으로 나뉩니다[1]. 유출 조사에서 "누가 언제 어느 파일을 내려받았나", "누가 언제 공유 범위를 밖으로 열었나" 를 답하는 기본 자료가 이 로그입니다.

조사에 자주 쓰는 이벤트는 다음과 같습니다[1][4].

| 유형 | 이벤트 이름 | 뜻 |
|---|---|---|
| `access` | `create`, `upload`, `edit`, `rename`, `move` | 만들기, 올리기, 고치기, 이름 바꾸기(`old_value`·`new_value`), 폴더 옮기기(`source_folder_title`·`destination_folder_title`) |
| `access` | `view`, `preview`, `download`, `print` | 보기, 미리 보기, 내려받기, 인쇄 |
| `access` | `copy`, `source_copy` | 사본 쪽 기록과 원본 쪽 기록(`copy_type` 이 `internal`·`external`) |
| `access` | `trash`, `untrash`, `delete` | 휴지통 넣기, 복원, 완전 삭제(`deletion_reason`) |
| `access` | `access_item_content`, `sync_item_content`, `prefetch_item_content` | 앱이 사용자 대신 내용 읽기(`api_method`), 기기로 동기화, 미리 받아 두기 |
| `access` | `search`, `access_url`, `email_as_attachment` | 검색(`user_query`·`parsed_query`), Apps Script 의 URL 접근(`accessed_url`·`script_id`), 메일 첨부로 보내기 |
| `access` | `pause_sync_client`, `resume_sync_client` | 랜섬웨어가 의심되어 동기화를 멈춘 일과 다시 켠 일 |
| `acl_change` | `change_user_access` | 사용자·그룹·도메인 하나의 권한 변경(`target_user`, `old_value`, `new_value`) |
| `acl_change` | `change_document_visibility`, `change_document_access_scope` | 링크 공유 범위와 링크 권한 변경(`target_domain`) |
| `acl_change` | `change_owner`, `publish_change` | 소유자 변경(`new_owner`), 웹 게시 상태 변경 |
| `acl_change` | `shared_drive_membership_change` | 공유 드라이브 구성원 추가·역할 변경·제거(`membership_change_type`) |

관리자가 관리 콘솔에서 파일 소유권을 넘기거나(`TRANSFER_DOCUMENT_OWNERSHIP`) Drive 자료 복원을 시작한 일(`DRIVE_DATA_RESTORE`)은 Drive 로그가 아니라 관리 로그의 `DOCS_SETTINGS` 유형에 남습니다[9]. 이 부분은 [관리 콘솔 감사 로그](admin-audit.md)에서 다룹니다.

## 위치와 버전별 차이

같은 기록을 네 곳에서 볼 수 있고, 곳마다 에디션 조건이 다릅니다(2026년 9월 문서 기준).

| 보는 곳 | 형태 | 조건 |
|---|---|---|
| 관리 콘솔 Reporting > Audit and investigation > Drive log events | 필터 검색, 기본 최근 7일, Sheets·CSV 내보내기 최대 10만 행 | Audit & Investigation 관리자 권한. 검색 대상 사용자의 에디션과 무관하게 검색할 수 있음[4] |
| Security > Security center > Investigation tool | 조건 검색, 조사 저장, 내보내기 최대 3천만 행 | Frontline Standard·Plus, Enterprise Standard·Plus, Education Standard·Plus, Enterprise Essentials Plus, Cloud Identity Premium[4] |
| 보고서 API `activities.list` | JSON, 최근 180일까지 | Business·Enterprise 고객만, 라이선스가 할당된 계정에서만 사용[2][3] |
| BigQuery 내보내기 | 일별 활동 표 | Drive 로그는 개별 사용자 단위로 내보내고, Cloud Identity Premium·Frontline Plus·Enterprise 에디션 등이 있는 도메인은 모든 사용자를 내보냄[7] |

기록 자체에도 에디션 조건이 붙습니다. Drive 감사 이벤트는 대부분 지원 에디션 사용자가 소유한 파일에 대해서만 남고, URL Accessed 이벤트만 스크립트를 실행한 사용자가 조직 안에 있고 지원 에디션이면 남습니다[4]. 그래서 조직 안에 에디션이 섞여 있으면 같은 동작도 파일 소유자에 따라 기록이 있고 없을 수 있습니다.

Drive 로그 이벤트는 6개월 보관하고, 관리자가 지우거나 보관 기간을 바꿀 수 없습니다(2026년 9월 문서 기준)[6]. Google Cloud 조직으로 공유하는 Workspace 감사 로그 목록은 Admin·Enterprise Groups·Login·OAuth Token·SAML·Access Transparency 이고 Drive 는 들어 있지 않습니다[8]. 따라서 Cloud Logging 에서는 Drive 기록을 찾을 수 없고, 6개월이 지나기 전에 API 나 BigQuery 로 따로 받아 두어야 합니다. 보관 기간 비교는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md), 보존 절차는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)를 봅니다.

## 구조

보고서 API 레코드 하나는 활동 (activity) 하나이고, 그 안의 `events[]` 에 이벤트가 하나 이상 들어갑니다. `id`·`actor`·`ipAddress` 같은 공통 필드는 [관리 콘솔 감사 로그](admin-audit.md)에 정리했습니다. Drive 이벤트의 `parameters[]` 에는 거의 모든 이벤트에 공통으로 붙는 매개변수가 있습니다[1].

| 매개변수 | 형식 | 뜻 |
|---|---|---|
| `doc_id` | string | 파일 ID. 관리 콘솔의 Document ID 이고 파일 URL 에 들어 있는 값[1][4] |
| `doc_title` | string | 이벤트 당시 파일 제목 |
| `doc_type` | string | `document`, `spreadsheet`, `presentation`, `folder`, `pdf`, `msword`, `shared_drive` 등 |
| `owner` | string | 소유자 메일 주소. 공유 드라이브 안 파일이면 공유 드라이브 이름 |
| `owner_is_shared_drive`, `shared_drive_id` | boolean, string | 공유 드라이브 소속 여부와 ID |
| `visibility` | string | 파일의 공유 상태 |
| `primary_event` | boolean | 사용자 동작의 주 이벤트인지 여부 |
| `originating_app_id` | string | 동작을 수행한 앱의 Google Cloud 프로젝트 번호 |
| `is_encrypted` | boolean | 클라이언트 측 암호화 파일인지 여부 |
| `actor_is_collaborator_account` | boolean | 행위자가 협업자 계정인지 여부 |

`visibility`·`old_visibility` 값은 `people_with_link`(링크가 있는 누구나), `people_within_domain_with_link`(대상 범위 (audience) 안에서 링크가 있는 누구나), `private`, `public_in_the_domain`, `public_on_the_web`, `shared_externally`(도메인 밖 사용자·그룹과 직접 공유), `shared_internally`(도메인 안 사용자·그룹과 직접 공유), `unknown` 입니다[1]. 권한 변경 이벤트에는 `visibility_change` 가 붙어 전체 공개 범위가 안에서 밖으로 바뀌었으면 `external`, 밖에서 안으로 바뀌었으면 `internal`, 바뀌지 않았으면 `none` 이 됩니다[1]. `change_user_access` 의 `old_value`·`new_value` 는 `can_comment`, `can_edit`, `can_respond`, `can_view`, `can_view_published`, `none`, `organizer`, `owner` 가운데 하나입니다[1]. `delete` 의 `deletion_reason` 은 `empty_trash`, `individual_delete`, `owning_shared_drive_delete`, `subscription_canceled`, `tos_violation`, `trash_auto_delete`, `user_account_delete` 가운데 하나입니다[1].

아래는 사용자가 스프레드시트를 외부 주소 하나에 보기 권한으로 공유한 모양을 만든 예시입니다. 필드 이름과 값의 종류는 문서를 따랐고, 주소·ID·IP 는 지어낸 값입니다.

```json
{
  "kind": "audit#activity",
  "id": {"time": "2026-03-02T01:14:07.512Z", "uniqueQualifier": "-4817253309182736451",
         "applicationName": "drive", "customerId": "C03az79cb"},
  "actor": {"callerType": "USER", "email": "user@example.com", "profileId": "100000000000000000001"},
  "ipAddress": "203.0.113.25",
  "events": [{
    "type": "acl_change", "name": "change_user_access",
    "parameters": [
      {"name": "primary_event", "boolValue": true},
      {"name": "doc_id", "value": "1AbCdEfGhIjKlMnOpQrStUvWxYz0123456789abcdEfG"},
      {"name": "doc_title", "value": "2026 영업 계획"},
      {"name": "doc_type", "value": "spreadsheet"},
      {"name": "owner", "value": "user@example.com"},
      {"name": "target_user", "value": "someone@contoso.com"},
      {"name": "old_value", "value": "none"},
      {"name": "new_value", "value": "can_view"},
      {"name": "old_visibility", "value": "private"},
      {"name": "visibility", "value": "shared_externally"},
      {"name": "visibility_change", "value": "external"}
    ]
  }]
}
```

관리 콘솔은 같은 이벤트를 `{actor} changed sharing permissions for {target_user} from {old_value} to {new_value}` 모양의 문장으로 보여 줍니다[1]. 보고서에는 문장이 아니라 이벤트 이름과 매개변수를 인용합니다.

## 증거로서 의미

**증명하는 것**

- 어느 계정(`actor.email`)이 언제(`id.time`) 어느 파일(`doc_id`·`doc_title`·`owner`)에 어떤 동작을 했는지[1].
- 공유 범위가 어떻게 바뀌었는지. `change_user_access` 의 `target_user`·`old_value`·`new_value` 와 `old_visibility`·`visibility`·`visibility_change` 가 바뀌기 전후를 함께 보여 줍니다[1].
- 파일 사본이 조직 밖으로 나갔는지. 외부 사용자가 우리 파일을 조직 밖으로 복사하면 우리 쪽에는 원본의 `source_copy`(`copy_type` 이 `external`)만 남습니다[4].
- 앱이 사용자 대신 파일 내용을 읽었는지. Drive API·Sheets API 를 쓰는 앱의 접근은 `download`·`view` 가 아니라 `access_item_content` 로만 남고, 관리 콘솔에서는 API method(예: `drive.files.export`)·App ID·App name 속성으로 보입니다[4]. 도메인 전체 위임으로 대신 수행했으면 Impersonation 이 True 입니다[4].
- 우리 파일에 대한 외부 사용자의 보기·편집·내려받기·인쇄·삭제. 이 기록은 우리 조직 쪽에만 남습니다[4].

**증명하지 못하는 것**

- 파일 내용과 무엇을 고쳤는지. 로그에는 동작과 파일 정보만 있습니다.
- 외부 사용자가 누구인지. 개인이나 특정 그룹으로 명시 공유한 경우가 아니면 도메인 밖 사용자는 anonymous 로 보입니다[4].
- 링크를 받은 사람이 실제로 누구였는지. 링크 공유 변경은 `change_document_visibility` 로 남지만 그 뒤 열람은 anonymous 로 남을 수 있습니다[1][4].
- 내려받은 파일을 그 뒤 어디로 보냈는지. 기기 쪽 흔적은 해당 OS 판의 아티팩트로 따로 봅니다.
- Google 형식 파일(Docs·Sheets·Slides·Drawings·Forms)을 인쇄했는지. 이 인쇄는 기록되지 않습니다[4].
- 기록된 IP 가 사용자의 실제 위치인지. 프록시·VPN 주소일 수 있고, 외부 사용자가 시작한 이벤트나 공유 드라이브 이름 바꾸기·삭제에는 IP 가 남지 않습니다[4]. 해석은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md)를 봅니다.

보고서 문장은 "이 계정으로 이 시각에 이 파일 ID 에 `download` 이벤트가 기록되어 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

- 보고서 API 의 `id.time` 은 문서 예시에서 `2014-03-17T15:39:18.460Z` 처럼 `Z` 로 끝나는 UTC 문자열입니다[2]. 그런데 activities.list 의 필드 설명에는 "UNIX epoch time in seconds" 로 적혀 있어[3] 설명과 예시가 서로 다르므로, 검체의 값 모양을 보고 판단합니다. 자세한 내용은 [관리 콘솔 감사 로그](admin-audit.md)에 있습니다.
- 관리 콘솔과 보안 조사 도구의 Date 는 브라우저 기본 시간대로 표시됩니다[4]. 보안 조사 도구는 최고 관리자가 조사 시간대를 바꿀 수 있고, 그 시간대가 검색 조건과 결과에 함께 적용됩니다[4]. 콘솔 화면이나 내보낸 CSV 를 받으면 어느 시간대로 표시된 값인지 먼저 적어 둡니다.
- 대부분의 이벤트는 동작이 끝났을 때 기록되며, 큰 파일 올리기는 기록이 늦어질 수 있습니다[4]. Drive 뷰어의 `print` 는 12시간 이상 늦게 기록될 수 있습니다[4].
- 로그가 콘솔에 들어오기까지 걸리는 시간은 "거의 실시간(몇 분)" 입니다(2026년 9월 문서 기준)[6]. 사건 직후 조회에서 보이지 않는 이벤트는 나중에 다시 조회합니다.
- `delete_revision`·`pin_revision` 등의 `revision_create_timestamp` 는 판이 처음 만들어진 시각이고 단위는 epoch 마이크로초입니다[1]. 이벤트 시각(`id.time`)과는 다른 시각입니다.
- `sync_item_content` 는 2024년 7월 1일 이후 활동부터 기록됩니다[4]. 그 전 기간에는 이 이벤트가 없는 것이 정상입니다.

여러 로그의 시각을 한 줄로 맞추는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)과 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)을 봅니다.

## 함정과 한계

- **이벤트 수를 동작 수로 세면 부풀려집니다.** 사용자 동작 하나가 이벤트 여러 개를 만들고 그중 일부만 `primary_event=true` 입니다. 문서를 만들면 `create` 만 true 이고, 한 번에 여러 사람에게 공유하면 받는 사람마다 true 인 권한 변경 이벤트가 하나씩 생깁니다[1].
- **`download` 가 곧 "파일을 PC 에 저장했다" 는 뜻은 아닙니다.** 모바일 Drive 앱에서 미리 보기, Google 앱으로 바로 못 여는 PDF 등의 미리 보기, Docs 에서 메일 첨부로 보내기도 `download` 로 남습니다[4]. Drive for desktop 으로 오간 파일은 `download` 와 `sync_item_content` 가 함께 남습니다[4].
- **`download` 가 없다고 내려받지 않은 것도 아닙니다.** Google Takeout 으로 받은 것(Takeout 로그에 남음), 오프라인 브라우저 캐시, Google Photos, Gmail 에서 첨부로 보낸 Drive 항목은 Drive 로그에 내려받기로 남지 않습니다[4]. Takeout 은 [Vault와 Takeout](vault-takeout.md)을 봅니다.
- **`prefetch_item_content` 는 사용자가 연 기록이 아닙니다.** Google 앱이 내용을 미리 받아 두기만 하고 바로 보여 주지 않았다는 뜻이고, 파일 하나를 미리 보면 근처 파일이 함께 prefetch 될 수 있습니다[4].
- **`shared_externally` 표시가 실제 외부 노출을 뜻하지 않을 수 있습니다.** 외부 공유를 꺼 둔 상태에서 외부 사용자를 허용하는 그룹과 공유하면, 그 그룹에 외부 사용자가 없어도 Shared externally 로 표시되고 외부 사용자는 실제로 접근할 수 없습니다[4].
- **링크 클릭은 남지 않습니다.** `access_url` 은 Apps Script 가 URL 에 접근한 기록이고, 사용자가 파일 안의 링크를 누른 일은 기록되지 않습니다[4].
- **주소가 바뀝니다.** 별칭 주소로 공유해도 기본 주소가 기록되고[4], `target_user` 에도 공유에 쓴 주소가 아니라 표시 주소가 적힙니다[1]. 사용자 이름을 바꾸면 옛 이름으로는 검색 결과가 나오지 않습니다[4].
- **계정 삭제가 파일 삭제로 보입니다.** 사용자 계정을 지우면 그 사용자 파일이 `deletion_reason=user_account_delete` 로 삭제 기록됩니다[1]. 사람이 지운 것과 구분하려면 이 값을 먼저 봅니다.
- **6개월이 지나면 사라집니다.** Drive 로그는 Cloud Logging 공유 대상이 아니라서[8] 보관 기간 뒤에는 미리 받아 둔 사본만 남습니다.

## 직접 분석해 보기

**원자료를 한 번 직접 읽기.** 보고서 API 로 받은 JSON 을 한 줄에 활동 하나씩 저장했다면, 주 이벤트만 골라 시각·행위자·이벤트·파일 ID 를 뽑아 봅니다. `jq` 로는 다음과 같습니다.

```sh
jq -r '.events[] as $e
  | select(any($e.parameters[]; .name=="primary_event" and .boolValue==true))
  | [ .id.time, (.actor.email // "anonymous"), $e.name,
      (first($e.parameters[] | select(.name=="doc_id") | .value) // ""),
      (first($e.parameters[] | select(.name=="visibility") | .value) // "") ]
  | @tsv' drive.json
```

외부 공유만 보려면 `$e.name=="change_user_access"` 이고 `visibility_change` 가 `external` 인 줄을, 조직 밖 사본은 `source_copy` 이고 `copy_type` 이 `external` 인 줄을 고릅니다. 같은 `doc_id` 로 `view`·`download`·`source_copy` 를 이어 보면 파일 하나의 흐름이 나옵니다.

**API 로 범위를 좁혀 받기.** 보고서 API 는 이벤트 이름과 매개변수로 거를 수 있습니다[2][3].

```
GET https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/drive?eventName=create
GET https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/drive?eventName=shared_drive_membership_change&filters=membership_change_type==add_to_shared_drive
GET https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/drive?eventName=edit&filters=doc_id==12345
```

**공개 도구.** ALFA 는 보고서 API 로 Workspace 감사 로그를 받는 공개 도구이고, `alfa acquire --logtype=drive --start-time=2026-03-01T00:00:00Z --end-time=2026-03-08T00:00:00Z` 처럼 쓰면 저장 폴더에 `drive.json` 을 한 줄에 활동 하나씩 씁니다[10]. 시간 인자는 RFC 3339 형식입니다[10]. ALFA 의 MITRE ATT&CK 매핑은 `download` 를 수집(Collection) 단계에, `change_user_access` 를 권한 상승(Privilege Escalation) 단계에 넣어 두었습니다[10].

**관리 콘솔.** 보안 조사 도구에서 외부 공유를 찾을 때는 Data source 를 Drive log events 로 고르고, Visibility change 조건을 External, Actor 조건에 조사 대상 계정, Date 조건을 After 로 두고 검색합니다[5]. 결과 표에는 시각, 문서 ID, 문서 종류, 공유 상태, 제목, 이벤트 종류, 행위자, 소유자가 나옵니다[5]. 보안 조사 도구가 없는 에디션은 Audit and investigation 의 Drive log events 에서 Visibility 필터를 Shared externally 로 둡니다[4].

## 교차 검증

| 함께 볼 기록 | 확인할 것 | 링크 |
|---|---|---|
| 로그인 기록 | 파일 동작 직전 그 계정의 로그인 시각·IP·로그인 방식 | [로그인 기록](login-audit.md) |
| OAuth 토큰 기록 | `originating_app_id`·App ID 로 나온 앱에 누가 언제 권한을 줬는지 | [OAuth 토큰 기록](token-audit.md), [OAuth 앱과 동의](../../01-foundations/identity/oauth-consent.md) |
| 관리 로그 | 공유 설정 변경, 소유권 이전(`TRANSFER_DOCUMENT_OWNERSHIP`), Drive 자료 복원 | [관리 콘솔 감사 로그](admin-audit.md) |
| Gmail 기록 | 파일을 메일 첨부나 링크로 내보낸 흔적 | [Gmail 기록과 메일 검색](gmail.md) |
| Takeout 로그 | Drive 로그에 남지 않는 Takeout 내려받기 | [Vault와 Takeout](vault-takeout.md) |
| Microsoft 365 대응 기록 | 같은 조직이 두 서비스를 함께 쓸 때 파일 동작 비교 | [SharePoint·OneDrive](../m365/sharepoint-onedrive.md) |

권한 흐름을 이어 붙이는 절차는 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md), 사건 흐름은 [외부 공유 링크로 새어 나갔나](../../04-scenarios/data-leak/external-sharing.md)와 [퇴사자가 자료를 가져갔나](../../04-scenarios/data-leak/departing-employee.md)를 봅니다.

## 실습

위 구조 절의 만든 예시 레코드와 직접 만든 시험 레코드로 풀어 봅니다.

1. 예시 레코드에서 공유 전후 상태를 한 문장으로 적어 봅니다. `old_visibility`, `visibility`, `visibility_change` 세 값이 각각 무엇을 말하는지 나눠 씁니다.
2. 같은 파일을 세 사람에게 한 번에 공유한 활동이 있다면 `primary_event=true` 인 `change_user_access` 이벤트는 몇 개가 나와야 하는지 답해 봅니다.
3. 한 사용자의 기록에 `download` 는 없고 `access_item_content` 만 여러 번 있습니다. 어떤 필드와 속성을 보면 어느 앱이 읽었는지 알 수 있는지 적어 봅니다.
4. `delete` 이벤트 수십 건이 같은 시각에 `deletion_reason=user_account_delete` 로 나옵니다. 사용자가 파일을 지웠다고 쓸 수 있는지, 어느 로그를 더 봐야 하는지 적어 봅니다.
5. 관리 콘솔에서 내보낸 CSV 의 Date 와 API 로 받은 `id.time` 이 9시간 차이 납니다. 원인과 보고서에 적을 기준 시각을 정해 봅니다.

## 참고 문헌

1. Google, "Drive Audit Activity Events", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/drive
2. Google, "Reports API: Drive Activity Report". https://developers.google.com/workspace/admin/reports/v1/guides/manage-audit-drive
3. Google, "Method: activities.list", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
4. Google Workspace Admin Help, "Drive log events". https://support.google.com/a/answer/4579696
5. Google Workspace Admin Help, "Investigate file sharing". https://knowledge.workspace.google.com/admin/security/investigate-file-sharing
6. Google Workspace Admin Help, "Data retention and lag times". https://support.google.com/a/answer/7061566
7. Google Workspace Admin Help, "About reporting logs and BigQuery". https://knowledge.workspace.google.com/admin/reports/about-reporting-logs-and-bigquery
8. Google Cloud, "Audit logs for Google Workspace", Cloud Logging. https://cloud.google.com/logging/docs/audit/gsuite-audit-logging
9. Google, "Admin Audit Activity Events - Drive Settings", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-docs-settings
10. Invictus Incident Response, ALFA (Automated Audit Log Forensic Analysis for Google Workspace), README.md·alfa/main/collector.py·alfa/utils/mappings.yml. https://github.com/invictus-ir/ALFA
