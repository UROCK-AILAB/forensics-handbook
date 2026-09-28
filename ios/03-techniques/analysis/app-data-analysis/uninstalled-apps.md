---
title: "지운 앱이 남긴 흔적"
parent: "앱 데이터 분석"
grand_parent: "기법 · 분석"
nav_order: 1260
---

# 지운 앱이 남긴 흔적 (Uninstalled Apps)

앱을 지운 뒤에도 번들 ID 를 열쇠로 삼아 설치 상태 DB, 설치 로그, 구매 기록, 사용 기록에서 그 앱이 있었고 쓰였다는 흔적을 찾습니다.

## 언제 쓰나

수집한 기기에는 없는 앱을 사건 관계자가 썼다고 의심될 때, 또는 [처음 보는 앱 분석 순서](unknown-apps.md) 의 2단계에서 앱이 지금 설치되어 있지 않다고 나왔을 때 이 절차로 넘어옵니다. 앱 삭제가 증거를 없애려던 행동인지 판단하는 흐름은 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) 에서 이어 갑니다.

## 기준 환경

이 페이지의 내용은 서로 다른 iOS 버전을 기준으로 합니다. 오래된 버전 기준도 있어서, 최신 기기에 그대로 적용하기 전에 같은 파일이 있는지부터 봅니다.

| 내용 | 기준 환경 |
|---|---|
| `applicationState.db` 로 설치·삭제 가르기 | iOS 11.2.1, iPhone SE, 탈옥 기기에서 SSH 로 추출[6] |
| `UninstalledApplications.plist`, `IconState.plist`, Mobile Installation 로그, `DAAP.sqlitedb` | 2019년 기준[3]. `DAAP.sqlitedb` 는 iOS 12 에서 추가 |
| Biome `_DKEvent.App.Install`, `AppLaunch` 스트림 | iOS 16[4] |
| 삭제 뒤 남는 기록 목록 | 2023년 기준[7] |
| 백업에 있는 파일과 표 이름 | iOS 27.0 로컬 백업, 암호화 안 함 |

## 절차

1. **찾을 번들 ID 를 모읍니다.** 앱을 지워도 번들 ID 를 기준으로 여러 DB 에서 흔적을 찾을 수 있어서[3], 먼저 사용 기록에 나오는 번들 ID 를 모아 지금 설치된 앱 목록과 비교합니다. 예를 들어 로컬 백업의 `WirelessDomain :: Library/Databases/DataUsage.sqlite` 의 `ZPROCESS` 표에는 `ZBUNDLENAME` 열이 있어서 지금은 없는 번들 ID 가 나오는지 볼 수 있습니다. 다만 앱을 지운 뒤에도 이 표의 행이 남는지는 실제 데이터로 확인해야 합니다.

   ```sql
   SELECT DISTINCT ZBUNDLENAME, ZPROCNAME
   FROM ZPROCESS
   WHERE ZBUNDLENAME IS NOT NULL
   ORDER BY ZBUNDLENAME;
   ```

2. **`applicationState.db` 로 설치 상태를 가릅니다.** 이 DB 는 앱의 설치 컨테이너와 데이터 위치를 보여 줍니다[3]. 표 구조와 위치는 [처음 보는 앱 분석 순서](unknown-apps.md) 에 있습니다. iOS 11.2.1 에서는 `kvs` 에 key 번호 1(`compatibilityInfo`)이 있으면 앱 폴더가 있는 설치 앱이고, 없으면 지운 앱입니다. 지운 앱 일부는 key 13(`_UninstallDate`)에 삭제 시각을 담은 바이너리 plist 를 남기지만 모든 앱이 그런 것은 아닙니다[6]. 이 번호는 기기와 버전마다 같다는 보장이 없어서 번호 대신 key 이름으로 조인합니다[6].

   ```sql
   -- 삭제 시각 key 가 남은 앱을 key 이름으로 찾습니다
   SELECT a.application_identifier, v.value
   FROM kvs v
   JOIN application_identifier_tab a ON a.id = v.application_identifier
   JOIN key_tab k ON k.id = v.key
   WHERE k.key = '_UninstallDate';
   ```

   `value` 열의 바이너리 plist 는 [속성 목록 파일](../../../01-foundations/data-formats/plist.md) 의 방법으로 풀고, 안의 시각은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 에서 기준을 확인합니다. iOS 27.0 백업에서도 네 표의 이름과 열은 같습니다. `_UninstallDate` key 가 최신 버전에서도 쓰이는지는 실제 데이터로 확인합니다.

3. **오프로드와 삭제를 나눕니다.** 앱을 오프로드 (offload) 하면 `applicationState.db` 의 항목이 지워집니다[3]. 그래서 이 DB 에 항목이 없다는 사실만으로는 삭제와 오프로드를 가를 수 없고, `IconState.plist` 를 함께 봅니다. 이 파일에는 있는데 `applicationState.db` 에는 없는 번들 ID 는 오프로드한 앱으로 봅니다[3]. `IconState.plist` 는 로컬 백업에 없을 수 있고, 비슷한 이름의 `HomeDomain :: Library/ControlCenter/ControlsIconState.plist` 는 제어 센터용 다른 파일입니다.

4. **설치 로그를 봅니다.** Mobile Installation 로그는 컨테이너를 만들고 지운 기록을 담고, 보통 `0.log`, `1.log` 두 개만 남습니다[3]. 이 로그는 설치 시각을 보여 주고, 앱을 지운 지 6일이 넘어도 남는 흔적에 들어갑니다[7]. 로그 파일의 정확한 경로와 로그 문장의 모양, 시각 형식은 실제 데이터로 확인해야 합니다. 로컬 백업에는 `SysSharedContainerDomain-systemgroup.com.apple.mobile.installationhelperlogs` 도메인이 들어 있으니 이 도메인의 파일도 함께 엽니다.

5. **`UninstalledApplications.plist` 를 봅니다.** 이 파일은 `private/var/installd/Library/MobileInstallation/` 에 있고 번들 ID 와 마지막으로 삭제한 날짜를 담습니다. 이 파일은 적어도 9개월 동안 남고, 유료 앱을 사거나 App Store 에 결제 수단을 연결한 뒤에만 채워지는 것으로 보입니다[3].

6. **구매 기록을 봅니다.** 구매 기록은 설치 여부가 아니라 구매 사실을 보여 줍니다. `DAAP.sqlitedb` 는 `private/var/mobile/Library/Caches/com.apple.appstored/` 에 있고 iOS 12 에서 추가되었으며, 설치한 앱이 아니라 구매한 앱을 Apple ID·가족 구매까지 포함해 기록합니다[3]. 예전 iOS 버전에서는 `private/var/mobile/Library/Caches/com.apple.storeservices/AppPurchaseHistory.6.sqlitedb` 를 봅니다[3]. `storeUser.db` 는 여러 기기에 걸친 구매 기록을 담고 앱을 지운 뒤에도 남습니다[7]. 로컬 백업의 `HomeDomain :: Library/com.apple.itunesstored/` 아래 `purchase_intents.sqlitedb` 에도 `app_bundle_id` 열이 있는 표가 있고, 열의 뜻은 실제 데이터로 확인해야 합니다. 구매 기록 전체는 [앱 스토어 기록](../../../02-artifacts/app-usage/app-store.md) 에서 다룹니다.

7. **사용 기록에서 앱을 찾습니다.** 설치·구매 기록으로 앱이 있었다는 것을 확인했으면, 사용 기록으로 언제 썼는지를 봅니다. 볼 기록은 다음과 같습니다.

   | 기록 | 삭제 뒤 상태 | 자세히 |
   |---|---|---|
   | knowledgeC.db, InteractionC.db | knowledgeC.db 에서는 앱을 지우면 그 번들의 항목이 지워짐. InteractionC.db 에서는 지운 행을 되살린 사례가 있음[7] | [KnowledgeC](../../../02-artifacts/app-usage/knowledgec/index.md), [삭제 데이터 복구](../data-recovery/index.md) |
   | Biome `_DKEvent.App.Install` | 번들 ID 와 설치 시작·끝 시각. 보존 기간(maxAge) 28일[4]. 삭제를 기록하는지는 시험 기기에서 앱을 지워 보고 확인 | [바이옴](../../../02-artifacts/app-usage/biome/index.md) |
   | Biome `AppLaunch` | 앱을 연 경로(idleTimer, homescreen, appswitcher, spotlight 등)와 앱 정보. 28일[4] | [바이옴](../../../02-artifacts/app-usage/biome/index.md) |
   | Biome(알림, 텍스트 입력 세션) | 삭제 6일 뒤에도 남음[7] | [바이옴](../../../02-artifacts/app-usage/biome/index.md) |
   | 알림, SMS | 삭제 6일 뒤에도 남음[7] | [알림 기록](../../../02-artifacts/app-usage/notifications.md), [메시지](../../../02-artifacts/communications/messages/index.md) |
   | Power Log | 백업된 경우 삭제 6일 뒤에도 남음[7] | [전원 로그](../../../02-artifacts/app-usage/powerlog.md) |
   | TCC.db | 일부 앱의 권한 항목이 남음[7] | [처음 보는 앱 분석 순서](unknown-apps.md) |
   | Screen Time, DataUsage.sqlite, netusage.sqlite | 보조 흔적[3] | [화면 사용 시간](../../../02-artifacts/app-usage/screen-time.md), [앱별 데이터 사용량](../../../02-artifacts/network/data-usage.md) |
   | CallHistory.storedata | 앱으로 건 통화 항목[3] | [통화 기록](../../../02-artifacts/communications/call-history.md) |

   Biome 두 스트림의 경로는 `private/var/mobile/Library/Biome/streams/restricted/_DKEvent.App.Install/` 와 `private/var/mobile/Library/Biome/streams/public/AppLaunch/` 입니다. 파일은 SEGB 형식이고 레코드는 protobuf 이며, 시각은 Apple 시각이고 분 단위로 반올림된 것으로 보입니다[4]. 형식은 [SEGB 형식](../../../01-foundations/data-formats/segb.md) 과 [프로토콜 버퍼](../../../01-foundations/data-formats/protobuf.md) 에서 다룹니다.

8. **시간순으로 잇습니다.** 설치 로그와 Biome 의 설치 시각, 사용 기록의 첫 시각과 마지막 시각, `_UninstallDate` 나 `UninstalledApplications.plist` 의 삭제 날짜를 한 표에 모읍니다. 모으는 법은 [타임라인 작성](../timeline/index.md) 을 따릅니다.

## 도구

`applicationState.db`, `DataUsage.sqlite` 처럼 SQLite 로 된 기록은 `sqlite3` 명령줄 도구나 SQLite 브라우저로 직접 질의합니다. MVT 는 설치 앱 목록과 설치 출처, `DataUsage.sqlite`·`netusage.sqlite` 의 프로세스별 통신량을 뽑아 줍니다[2]. 나머지 기록은 각 아티팩트 페이지의 방법으로 하나씩 엽니다. knowledgeC.db·InteractionC.db 의 지운 행은 [삭제 데이터 복구](../data-recovery/index.md) 의 방법으로 찾습니다.

## 함정과 한계

`key_tab` 의 번호와 `_UninstallDate` 는 iOS 11.2.1 에서 시험한 결과이고[6] 모든 지운 앱에 삭제 시각이 남지도 않습니다. `UninstalledApplications.plist` 도 유료 구매나 결제 수단 연결 뒤에만 채워지는 것으로 보이므로[3], 이 파일에 앱이 없다고 해서 그 앱을 지운 적이 없다고 쓰지 않습니다.

iOS 27.0 로컬 백업의 `HomeDomain :: Library/Preferences/com.apple.mobile.installation.plist` 에는 `ExtensionDataContainerParentIDUpdateVersion` 키 하나만 있고 앱 목록은 없습니다. `HomeDomain :: Library/Preferences/com.apple.MobileStore.appremoval.plist` 는 파일이 있어도 키가 비어 있을 수 있습니다. 이름만 보고 삭제 기록으로 해석하지 않습니다.

Biome 의 두 스트림은 보존 기간이 28일이라[4] 오래전에 지운 앱은 Biome 에 흔적이 없을 수 있습니다. 앱을 지우면 앱의 데이터 컨테이너도 함께 지워진다고 흔히 말하지만, Apple 공식 문서에 적힌 내용은 아닙니다. 그래서 컨테이너가 없다는 것은 수집 시점에 없었다는 사실로만 씁니다.

## 결과를 어떻게 해석하나

구매 기록은 계정이 그 앱을 얻은 사실을 보여 줄 뿐 이 기기에 설치했다는 증명은 아니고, `storeUser.db` 는 여러 기기에 걸친 기록이라서[7] 다른 기기에서 받은 앱일 수도 있습니다. 설치 로그나 Biome 설치 기록은 이 기기에 설치된 시각을, 사용 기록은 그 앱이 화면에 올라오거나 통신한 시각을 보여 주지만, 그 시각에 누가 폰을 들고 있었는지는 [그 시각에 폰을 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 에서 따로 따집니다. 삭제 시각이 남아 있어도 삭제한 이유까지 알려 주지는 않습니다.

보고서에는 "이 앱을 지워 증거를 없앴다" 대신 "번들 ID `com.example.app` 의 설치 기록이 이 시각에 있고, `applicationState.db` 에 이 시각의 삭제 기록이 있으며, 수집 시점에 이 앱의 컨테이너는 없었다" 처럼 기록마다 확인되는 만큼만 씁니다.

## 참고 문헌

- [2] MVT 문서, iOS Records — https://docs.mvt.re/en/latest/ios/records/
- [3] D20 Forensics, "iOS - Tracking Traces of Deleted Applications" (2019-09) — https://blog.d204n6.com/2019/09/ios-tracking-traces-of-deleted.html
- [4] D20 Forensics, "iOS 16 Breaking Down the Biomes Part 2 - AppInstalls, AppLaunch, & AppIntents" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-breaking-down-biomes-part-2.html
- [6] Alexis Brignoni, "Identifying installed and uninstalled apps in iOS" (2018-12) — https://abrignoni.blogspot.com/2018/12/identifying-installed-and-uninstalled.html
- [7] digital-forensics.it, "Has the user ever used the XYZ application? aka traces of application execution on mobile devices" (2023-12) — https://blog.digital-forensics.it/2023/12/has-user-ever-used-xyz-application-aka.html
