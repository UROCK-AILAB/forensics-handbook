---
title: "처음 보는 앱 분석 순서"
parent: "앱 데이터 분석"
grand_parent: "기법 · 분석"
nav_order: 1240
---

# 처음 보는 앱 분석 순서 (Unknown Apps)

아티팩트 사전에 없는 앱을 만나면 번들 ID 를 먼저 확정하고 설치 상태를 확인한 다음, 앱 컨테이너 안의 파일과 앱 밖의 시스템 기록을 차례로 봅니다.

## 언제 쓰나

사건과 관련된 앱인데 이 핸드북에 따로 정리한 페이지가 없을 때, 설치 앱 목록에서 이름을 모르는 앱이 나왔을 때 이 순서를 씁니다. 스파이웨어가 의심되어 낯선 앱을 하나씩 걸러야 할 때도 같은 순서로 시작하고, 그 뒤의 판단은 [악성 코드·스파이웨어 흔적](../spyware-triage/index.md) 에서 이어 갑니다.

앱이 이미 지워졌다면 설치 상태를 확인하는 2단계에서 갈림길이 생기고, 그 뒤는 [지운 앱이 남긴 흔적](uninstalled-apps.md) 을 따릅니다.

## 먼저 알아 둘 구조

서드파티 앱은 모두 샌드박스 (sandbox) 안에서 돌고, 다른 앱의 정보를 모으거나 바꾸지 못하게 설계되어 있습니다. 앱마다 홈 디렉터리가 따로 있고, 이 디렉터리 이름은 설치할 때 무작위로 정해집니다[8]. 앱 샌드박스는 앱 번들이 들어가는 번들 컨테이너 (bundle container) 와 앱·사용자 데이터가 들어가는 데이터 컨테이너 (data container) 로 나뉘고, iCloud 컨테이너는 앱이 실행 중에 따로 요청합니다[1]. 여러 앱과 앱 확장이 함께 쓰는 앱 그룹 (App Group) 공유 폴더도 따로 있으며, 앱 그룹 ID 를 읽는 법은 [번들 ID와 앱 그룹](../../../01-foundations/value-decoding/bundle-id-app-group.md) 에 있습니다.

전체 파일 시스템 추출에서는 세 곳이 다음 경로에 있습니다[7].

| 구분 | 경로 |
|---|---|
| 번들 컨테이너 | `/private/var/containers/Bundle/Application/<GUID>` |
| 데이터 컨테이너 | `/private/var/mobile/Containers/Data/Application/<GUID>` |
| 앱 그룹 공유 폴더 | `/private/var/mobile/Containers/Shared/AppGroup/<GUID>` |

로컬 백업에서는 GUID 폴더 대신 도메인 이름으로 나뉩니다. 앱 데이터는 `AppDomain-<번들 ID>`, 앱 그룹 공유 폴더는 `AppDomainGroup-<그룹 ID>`, 앱 확장은 `AppDomainPlugin-<번들 ID>` 도메인에 들어갑니다. 백업 폴더 자체의 구조는 [로컬 백업](../../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

데이터 컨테이너 안의 표준 하위 폴더와 백업 포함 여부는 다음과 같습니다[1]. 근거가 보관 (archive) 문서라서 최신 iOS 에서도 규칙이 그대로인지는 검체에서 확인합니다.

| 폴더 | 담는 것 | 백업 |
|---|---|---|
| `Documents/` | 사용자가 만든 콘텐츠 | 들어감 |
| `Documents/Inbox` | 메일 첨부처럼 다른 앱이 열라고 넘긴 파일. 앱은 읽고 지울 수만 있음 | 들어감 |
| `Library/Application Support` | 앱이 만든 데이터 파일과 설정 | 들어감 |
| `Library/Preferences` | NSUserDefaults 설정 파일 | 들어감 |
| `Library/Caches` | 다시 만들 수 있는 파일 | 안 들어감 ([캐시와 웹뷰](cache-webkit.md) 참고) |
| `tmp/` | 임시 파일. 앱이 실행 중이 아닐 때 시스템이 비울 수 있음 | 안 들어감 |

## 절차

1. **번들 ID 를 확정합니다.** 앱 이름은 바뀌거나 겹칠 수 있지만 번들 ID 는 삭제한 앱까지 포함해 모든 DB 에서 앱 흔적을 찾는 기준 키입니다[3]. 로컬 백업이라면 최상위 `Info.plist` 에 `Applications`, `Installed Applications` 키가 있고, `Manifest.plist` 에도 `Applications` 키가 있습니다. MVT 의 Applications 모듈은 백업에서는 `Info.plist` 를, 파일 시스템 덤프에서는 `iTunesMetadata.plist` 를 읽어 설치 앱 목록과 설치 출처를 뽑고, App Store 가 아닌 곳에서 온 앱을 따로 표시합니다[2]. 앱 번들 안의 정보는 [앱 번들 정보](../../../02-artifacts/embedded-metadata/app-bundle.md) 에서 봅니다.

2. **지금 설치되어 있는지 확인합니다.** 설치 상태에 따라 볼 아티팩트가 달라서 이 단계를 먼저 합니다[7]. 설치 확인에는 Mobile Installation 로그, `applicationState.db`, `containers3.sqlite` 를 씁니다[7]. `applicationState.db` 는 기기에서 `/private/var/mobile/Library/FrontBoard/applicationState.db` 에 있고[3][6], 로컬 백업에서는 `HomeDomain :: Library/FrontBoard/applicationState.db` 로 들어 있습니다. 표는 `application_identifier_tab(id, application_identifier)`, `key_tab(id, key)`, `kvs(id, application_identifier, key, value)`, `schema(version)` 네 개입니다. `application_identifier_tab` 이 번들 ID 를 번호에 잇고, `key_tab` 이 key 번호를 이름에 이으며, `kvs` 가 앱과 데이터 경로를 잇습니다[6]. 이 DB 로 설치와 삭제를 가르는 방법은 [지운 앱이 남긴 흔적](uninstalled-apps.md) 에, 설치 앱 목록 자체의 해석은 [설치된 앱](../../../02-artifacts/app-usage/installed-apps.md) 에 있습니다.

   ```sql
   -- 앱마다 어떤 key 가 붙어 있는지 이름으로 풀어 봅니다
   SELECT a.application_identifier, k.key, length(v.value) AS value_bytes
   FROM kvs v
   JOIN application_identifier_tab a ON a.id = v.application_identifier
   JOIN key_tab k ON k.id = v.key
   ORDER BY a.application_identifier, k.key;
   ```

3. **앱 컨테이너를 엽니다.** 로컬 백업에서는 `Manifest.db` 의 `Files(fileID, domain, relativePath, flags, file)` 표에서 도메인과 상대 경로로 파일을 찾습니다. 앱 하나의 파일 목록은 도메인 이름으로 거르면 나옵니다.

   ```sql
   SELECT domain, relativePath
   FROM Files
   WHERE domain IN ('AppDomain-com.example.app', 'AppDomainPlugin-com.example.app.widget')
      OR domain LIKE 'AppDomainGroup-group.com.example%'
   ORDER BY domain, relativePath;
   ```

   위 번들 ID 는 설명용 예시입니다. 전체 파일 시스템 추출이라면 2단계에서 찾은 데이터 경로로 바로 들어갑니다.

4. **컨테이너 안을 정해진 순서로 봅니다.** 설정 파일부터 열면 앱이 무엇을 저장하는지 감이 잡힙니다. 앱 설정 파일은 백업에서 `AppDomain-<번들 ID> :: Library/Preferences/<번들 ID>.plist` 모양으로 있고(예: `AppDomain-com.apple.mobilesafari :: Library/Preferences/com.apple.mobilesafari.plist`), 읽는 법은 [속성 목록 파일](../../../01-foundations/data-formats/plist.md) 에 있습니다. 그다음 `Library/Application Support` 와 `Documents` 에서 SQLite 파일을 찾아 표 이름과 칸 이름으로 무엇을 기록하는지 가늠합니다. 이때 `-wal`, `-shm` 파일을 함께 가져와야 하고, 지운 행을 찾는 법까지 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다. 앱 그룹 공유 폴더와 앱 확장 도메인에도 본체와 다른 DB 가 있을 수 있어서 함께 봅니다. HTTP 캐시와 웹뷰 데이터는 [캐시와 웹뷰](cache-webkit.md) 에서 이어 봅니다.

5. **앱 밖의 시스템 기록을 봅니다.** 앱 자신의 파일이 비어 있거나 암호화되어 있어도, 시스템이 남긴 기록에서 앱을 언제 설치하고 얼마나 썼는지가 드러납니다. 앱 사용 흔적을 찾을 기록은 다음과 같습니다[7].

   | 기록 | 알려 주는 것 | 자세히 |
   |---|---|---|
   | Mobile Installation 로그 | 설치 시각 | [지운 앱이 남긴 흔적](uninstalled-apps.md) |
   | knowledgeC.db, InteractionC.db | 앱 사용 기록 | [KnowledgeC](../../../02-artifacts/app-usage/knowledgec/index.md) |
   | Biome(알림, 텍스트 입력 세션) | 앱 알림과 입력 | [바이옴](../../../02-artifacts/app-usage/biome/index.md) |
   | Power Log(Application State, Process Data Usage, App Usage) | 앱 상태와 데이터 사용 | [전원 로그](../../../02-artifacts/app-usage/powerlog.md) |
   | RMAdminStore-Local.sqlite | 스크린 타임 | [화면 사용 시간](../../../02-artifacts/app-usage/screen-time.md) |
   | netusage, DataUsage | 앱별 통신량 | [앱별 데이터 사용량](../../../02-artifacts/network/data-usage.md) |
   | TCC.db | 앱에 준 권한 | 아래 설명 |
   | storeUser.db | 여러 기기에 걸친 구매 기록 | [앱 스토어 기록](../../../02-artifacts/app-usage/app-store.md) |
   | 알림 DB | 앱이 띄운 알림 | [알림 기록](../../../02-artifacts/app-usage/notifications.md) |
   | SMS | 가입 문자, 2단계 인증 코드 | [메시지](../../../02-artifacts/communications/messages/index.md) |
   | 카메라 롤 | 앱 화면을 찍은 스크린숏 | [스크린샷과 화면 녹화](../../../02-artifacts/media/screenshots.md) |

   이 가운데 Biome, KnowledgeC, 스크린 타임, netusage, Power Log 는 전체 파일 시스템 추출에서만 얻습니다[7]. TCC.db 도 여기에 넣는 정리가 있지만[7], 암호화하지 않은 로컬 백업에도 `HomeDomain :: Library/TCC/TCC.db` 가 들어 있을 수 있습니다. 백업에 든 TCC.db 의 `access` 표에는 `service`, `client`, `client_type`, `auth_value`, `auth_reason`, `auth_version`, `csreq`, `policy_id`, `indirect_object_identifier_type`, `indirect_object_identifier`, `indirect_object_code_identity`, `flags`, `last_modified`, `pid`, `pid_version`, `boot_uuid`, `last_reminded`, `one_time_reprompt_eligible`, `reminder_count` 칸이 있고, `expired` 표에는 `expired_at` 칸이 있습니다. 앱별 통신량은 백업에서 `WirelessDomain :: Library/Databases/DataUsage.sqlite` 의 `ZPROCESS` 표(`ZBUNDLENAME`, `ZPROCNAME`, `ZFIRSTTIMESTAMP`, `ZTIMESTAMP` 등)로 볼 수 있습니다. 구매 쪽은 `HomeDomain :: Library/com.apple.itunesstored/` 아래 `purchase_intents.sqlitedb` 의 `purchase_intents_table(product_identifier, app_bundle_id, timestamp, pid, product_name, app_name)` 처럼 번들 ID 칸이 있는 표가 있습니다. 각 칸의 뜻과 시각 기준은 공개된 분석 자료가 없어 검체에서 확인해야 합니다.

6. **시간순으로 모읍니다.** 앞에서 얻은 시각을 한 표에 모으면 설치, 첫 사용, 권한 허용, 통신, 삭제의 순서가 보입니다. Apple 기록은 대부분 Mac 절대 시각(2001-01-01 부터 센 초)을 쓰지만[7] 칸마다 기준이 다를 수 있어서, 변환은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 에서 칸별로 확인하고 모으는 법은 [타임라인 작성](../timeline/index.md) 을 따릅니다.

## 도구

MVT 는 백업과 파일 시스템 덤프에서 설치 앱 목록, `DataUsage.sqlite`·`netusage.sqlite` 의 프로세스별 통신량 같은 기록을 뽑아 줍니다. 올바른 번들 ID 가 없는 프로세스는 눈여겨볼 대상입니다[2]. 표 구조를 직접 확인할 때는 `sqlite3` 명령줄 도구나 SQLite 브라우저로 `.schema` 부터 보고, plist 는 바이너리 plist 를 XML 로 바꿔 주는 도구로 엽니다. 도구 결과는 한 번은 원본 DB 에 직접 질의해서 맞춰 봅니다.

## 함정과 한계

`key_tab` 의 번호는 기기와 버전마다 같다는 보장이 없어서 번호가 아니라 key 이름으로 조인해야 하고[6], 위 질의도 이름으로 조인합니다. 컨테이너 폴더 이름은 설치할 때 무작위로 정해지는 값이라[8], 앱은 GUID 가 아니라 번들 ID 로 알아봅니다.

로컬 백업에 들어가는 범위는 폴더마다 다르고 그 규칙의 근거가 보관 문서라서[1], 백업에 없는 파일을 "기기에 없었다" 로 쓰지 않습니다. 반대로 전체 파일 시스템 추출에서만 얻는다고 알려진 TCC.db 가 로컬 백업에 들어 있기도 하듯이[7], 어떤 파일이 어느 수집 방법에 들어가는지는 버전과 백업 암호화 여부에 따라 달라질 수 있어서 검체에서 확인합니다.

번들 ID 없는 프로세스라도[2] 그것만으로 악성이라고 단정하지 않고, [악성 코드·스파이웨어 흔적](../spyware-triage/index.md) 의 다른 기록과 함께 판단합니다.

## 결과를 어떻게 해석하나

컨테이너와 `applicationState.db` 항목은 앱이 수집 시점에 설치되어 있었음을 보여 주고, 시스템 기록은 그 앱이 언제 설치되고 쓰였는지를 보여 줍니다. 앱 안의 DB 에 행이 있다는 사실이 곧 사용자가 그 내용을 보거나 입력했다는 뜻은 아니며, 동기화나 서버가 내려보낸 데이터일 수도 있습니다. 보고서에는 "이 앱으로 대화했다" 대신 "번들 ID `com.example.app` 의 데이터 컨테이너 안 DB 에 이 시각 범위의 메시지 행이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 참고 문헌

- [1] Apple Developer, File System Programming Guide — File System Basics (보관 문서) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html
- [2] MVT 문서, iOS Records — https://docs.mvt.re/en/latest/ios/records/
- [3] D20 Forensics, "iOS - Tracking Traces of Deleted Applications" (2019-09) — https://blog.d204n6.com/2019/09/ios-tracking-traces-of-deleted.html
- [6] Alexis Brignoni, "Identifying installed and uninstalled apps in iOS" (2018-12) — https://abrignoni.blogspot.com/2018/12/identifying-installed-and-uninstalled.html
- [7] digital-forensics.it, "Has the user ever used the XYZ application? aka traces of application execution on mobile devices" (2023-12) — https://blog.digital-forensics.it/2023/12/has-user-ever-used-xyz-application-aka.html
- [8] Apple Platform Security, "Security of runtime process in iOS, iPadOS, and visionOS" (2024-12-19) — https://support.apple.com/guide/security/security-of-runtime-process-sec15bfe098e/web
