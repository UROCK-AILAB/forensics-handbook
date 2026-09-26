---
title: "네이버 밴드"
parent: "아티팩트 · 국내 생활 앱"
nav_order: 930
---

# 네이버 밴드 (BAND)

## 한 줄 요약

아이폰의 네이버 밴드 앱은 번들 ID 가 `com.nhncorp.m2app` 이고, 앱 안의 저장 구조를 적은 iOS 공개 자료가 아직 없어서 시스템 흔적으로 설치·사용 여부를 먼저 확인한 뒤 앱 데이터 컨테이너를 직접 열어 확인해야 합니다.

## 무엇을 기록하나 · 왜 생기나

밴드는 NAVER Corp. 가 내는 모임 앱이고, 한국 앱 스토어 이름은 "밴드-모임이 쉬워진다!" 입니다[1]. 글·댓글·채팅 같은 서비스 데이터는 서버에 원본이 있고, 기기에는 앱이 화면을 그리거나 빨리 열려고 내려받아 둔 사본이 남습니다. 기기에 무엇이 얼마나 남는지를 다룬 iOS 공개 자료는 없습니다.

iOS 는 앱을 설치할 때 앱마다 번들 컨테이너(앱 본체)와 데이터 컨테이너(앱과 사용자 데이터)를 따로 만듭니다[6]. 밴드 앱이 쓰는 DB·설정·캐시 파일은 모두 이 데이터 컨테이너 안에 생기고, 시스템 쪽에는 앱 설치·실행과 관련된 흔적이 앱과 상관없이 따로 쌓입니다. 시스템 흔적은 [설치된 앱](../app-usage/installed-apps.md)과 [알림 기록](../app-usage/notifications.md)에서 자세히 다룹니다.

밴드를 디지털 포렌식 관점에서 다룬 국내 논문이 한 편 있지만 **안드로이드만** 다뤘고, 루팅(root 권한)과 로그인 상태를 전제로 했습니다[5]. 논문에 나온 파일 이름과 표 이름을 iOS 경로로 옮겨 쓰면 안 됩니다.

## 위치와 버전별 차이

| 항목 | 값 |
|---|---|
| 번들 ID | `com.nhncorp.m2app` [1] |
| 로컬 백업 도메인(규칙상) | `AppDomain-com.nhncorp.m2app` |
| 조회 시점 앱 버전 | 30.1.1 (2026-09-09 배포, UTC) [1] |
| 최소 iOS | 17.0 (지금 앱 버전 기준) [1] |
| 조회일 | 2026-09-25, 한국 스토어 [1] |

번들 ID 에 band 라는 글자가 들어 있지 않습니다[1]. 이름으로 찾으면 놓치기 쉬운 부분이라 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md)을 함께 봅니다.

로컬 백업에서는 앱 데이터가 `AppDomain-` 뒤에 번들 ID 를 붙인 도메인으로 들어갑니다. Apple 앱 도메인(예: `AppDomain-com.apple.AAUIViewService`)도 이 규칙을 따르고, 로컬 백업에는 `AppDomainGroup-`, `AppDomainPlugin-` 으로 시작하는 도메인도 따로 있습니다. 위 표의 밴드 도메인 이름은 이 규칙에 따라 적은 것이고, 밴드가 앱 그룹이나 확장 도메인을 쓰는지는 실제 기기에서 확인합니다.

전체 파일시스템 추출에서는 데이터 컨테이너 폴더 이름이 번들 ID 가 아니라서, 번들 ID 와 컨테이너 경로를 먼저 이어야 합니다. 이 작업은 `applicationState.db` 로 하고, 방법은 [설치된 앱](../app-usage/installed-apps.md)에 있습니다.

지금 앱은 iOS 17.0 이상에서만 돌지만 옛 앱 버전은 더 낮은 iOS 에서도 돌았을 수 있고, iOS 버전이나 앱 버전에 따라 저장 구조가 어떻게 달랐는지는 공개 자료가 없습니다. 그래서 버전별 차이 표는 싣지 않습니다.

## 구조

iOS 밴드 앱의 DB 이름, 표와 열 이름, 첨부 파일 캐시 위치를 다룬 공개 자료는 없습니다. 공개 분석 도구 iLEAPP 의 분석기 452개 가운데에도 밴드 전용 분석기는 없고, 국내 앱 가운데 전용 분석기가 있는 앱은 카카오톡뿐입니다(2026-09 저장소 목록 기준)[2].

앱 데이터 컨테이너 안에서 무엇이 백업에 들어가는지는 앱과 상관없이 정해진 규칙이 있습니다. `Documents/` 와 `Library/` 는 백업되지만 `Library/Caches/` 와 `tmp/` 는 백업되지 않고, `Library/Application Support` 도 앱이 백업 제외 표시를 붙이면 빠집니다[6]. 그래서 이미지 캐시나 임시 파일은 로컬 백업에는 없고 전체 파일시스템 추출에서만 볼 수 있습니다. 이 규칙은 Apple 의 보관 문서에 나온 것이라[6], 최신 iOS 에서 바뀌었는지는 실제 기기에서 확인해야 합니다.

비교를 위해 안드로이드 쪽만 한 줄로 적으면, 사용자별 DB `[user_no].db` 에 `channel_user`·`chat_channel`·`chat_message` 표가 있습니다[5].

## 증거로서 의미

**증명하는 것**

로컬 백업의 `Manifest.db` 에 밴드 도메인 항목이 있으면, 백업을 만든 시점에 그 기기에 밴드 앱 데이터가 있었다는 뜻입니다. `applicationState.db` 에 번들 ID 가 있으면 시스템이 그 앱을 등록해 두었다는 뜻이고, 홈 화면 배치를 담은 `IconState.plist` 로 앱 아이콘이 어디에 놓였는지 볼 수 있습니다. 앱 안에서 대화나 글 파일을 찾아 연 경우에는 그 내용이 기기에 사본으로 있었다는 사실까지 말할 수 있습니다.

**증명하지 못하는 것**

앱이 설치돼 있었다는 사실만으로 그 사람이 어느 밴드에 가입했는지, 언제 무엇을 썼는지는 알 수 없습니다. `applicationState.db` 의 화면 스냅숏 목록에 있는 `creationDate` 는 스냅숏 개체가 만들어진 시각이고 `lastUsedDate` 가 언제 바뀌는지는 Apple 이 문서화하지 않았으며, 어느 쪽도 앱이 앞에 떠 있었다거나 사용자가 화면을 봤다는 증거가 아닙니다[3]. 기기에 없는 대화는 서버에 남아 있을 수 있으니, 기기 분석 결과만으로 "대화가 없었다" 고 쓰지 않습니다. 서버 쪽 자료는 사업자에게 요청할 대상이고 절차는 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md)를 봅니다.

## 시각 해석

밴드 앱 데이터 안의 시각이 어떤 기준으로 저장되는지는 iOS 쪽 자료가 없습니다. 안드로이드 앱은 캐시 파일 이름과 메시지 메타데이터 시각에 Unix 시각을 쓰지만[5], iOS 앱도 같은지는 실제 기기에서 확인합니다. 숫자 필드를 만나면 값의 자릿수와 범위로 Unix 초·밀리초인지, Mac 절대 시각인지를 구분해야 하고, 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md)에 있습니다.

앱을 지운 흔적인 `UninstalledApplications.plist` 의 날짜는 plist 날짜형이고 UTC 입니다[4].

## 함정과 한계

번들 ID 에 band 가 없어서 도메인이나 폴더를 "band" 로 검색하면 아무것도 나오지 않을 수 있습니다. 안드로이드 논문은 루팅된 기기와 로그인 상태를 전제로 했으니 그 결과를 iOS 에 그대로 옮기면 안 됩니다.

밴드에서 쓸 수 있는 안티포렌식 행위로는 같은 계정의 여러 프로필 쓰기, 밴드 숨기기, 채팅방 나가기, 메시지 삭제, 로그아웃이 있습니다[5]. 안드로이드에서는 삭제한 메시지가 상태 값 RECLAIM 으로 표시되고, 로그아웃하면 기기의 사용자 데이터가 모두 지워집니다[5]. iOS 에서도 같은지는 공개 자료가 없으니, 로그아웃이 의심되면 앱 데이터보다 시스템 흔적과 서버 자료에 기대야 합니다.

앱을 지웠다면 `UninstalledApplications.plist` 에 번들 ID 와 날짜가 남을 수 있습니다. 다만 번들 ID 하나에 날짜 하나만 남아서 여러 번 지우고 다시 깔아도 날짜는 하나이고, iLEAPP 시험 이미지 24개 가운데 2개에만 이 파일이 있었습니다[4]. 파일이 없다고 앱을 지우지 않았다는 뜻은 아닙니다. 로컬 백업의 `InstallDomain` 에는 이 파일 없이 `BackedUpState/BackupSystemAppInstallState.plist` 와 `SystemAppInstallState.plist` 만 있을 수 있습니다.

따로 지정하지 않은 서드파티 앱 데이터의 기본 보호 등급은 Class C(첫 잠금 해제 후 보호)이고[7], 밴드가 실제로 어떤 등급을 쓰는지는 실제 기기에서 확인합니다. 등급 설명은 [데이터 보호](../../01-foundations/storage/data-protection/index.md)에 있습니다.

## 직접 분석해 보기

**헥스로 한 번**

앱 데이터 컨테이너에서 확장자가 없거나 낯선 파일을 만나면 앞부분 몇 바이트로 형식을 판별합니다. 아래는 SQLite 파일 형식 명세로 만든 예시이고 실제 기기에서 뽑은 값이 아닙니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

`bplist00` 으로 시작하면 바이너리 plist 입니다. 형식별 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)와 [속성 목록 파일](../../01-foundations/data-formats/plist.md)을 봅니다.

**공개 도구로 한 번**

iLEAPP 에는 밴드 전용 분석기가 없어서[2], 설치·삭제 흔적은 applicationState 분석기와 uninstalledApplications 분석기 결과에서 번들 ID 로 찾습니다[3][4]. 로컬 백업이라면 sqlite3 로 `Manifest.db` 의 `Files` 표에서 도메인을 바로 찾을 수 있습니다. `Files` 표의 열은 `fileID`, `domain`, `relativePath`, `flags`, `file` 입니다.

```sql
SELECT fileID, relativePath, flags
FROM Files
WHERE domain = 'AppDomain-com.nhncorp.m2app'
ORDER BY relativePath;
```

결과가 비어 있으면 `domain LIKE '%nhncorp%'` 로 넓혀 앱 그룹이나 확장 도메인이 있는지 봅니다. 앱 그룹 이름에 번들 ID 앞부분이 꼭 들어간다는 보장은 없어서, 이 검색으로도 못 찾을 수 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [설치된 앱](../app-usage/installed-apps.md) | 번들 ID 와 데이터 컨테이너 연결, 앱 삭제 흔적 |
| [알림 기록](../app-usage/notifications.md) | 밴드 알림이 온 시각과 내용 일부 |
| [KnowledgeC](../app-usage/knowledgec/index.md) · [바이옴](../app-usage/biome/index.md) | 앱이 앞에 뜬 구간 |
| [화면 사용 시간](../app-usage/screen-time.md) | 앱별 사용 시간 |
| [앱별 데이터 사용량](../network/data-usage.md) | 앱이 주고받은 데이터 양 |
| [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) | 서버 쪽 자료 요청 |

다른 메신저와 비교해 보려면 [카카오톡](../messengers/kakaotalk/index.md)을, 앱 데이터를 처음 여는 순서는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md)을 봅니다.

## 실습

공개 iOS 시험 자료(NIST CFReDS 등)에는 밴드 앱이 없을 수 있으니, 확보한 증거물이나 직접 만든 시험 기기로 아래 질문을 풀어 봅니다.

1. `Manifest.db` 에서 `AppDomain-com.nhncorp.m2app` 도메인의 파일을 모두 뽑고, `Library/Caches` 아래 파일이 하나도 없는지 확인합니다.
2. `applicationState.db` 에서 `com.nhncorp.m2app` 을 찾아 데이터 컨테이너 경로를 확인합니다.
3. 컨테이너 안 파일마다 앞 16바이트를 보고 SQLite·plist·그 밖의 형식으로 나눕니다.
4. 시험 기기에서 로그아웃한 뒤 다시 백업해서, 로그아웃 전과 비교해 어떤 파일이 사라지는지 기록합니다.

## 참고 문헌

1. Apple iTunes Search API 조회 결과(한국 스토어, 2026-09-25 조회) — https://itunes.apple.com/lookup?id=542613198,1018769995,454434967,378084485,1445504255,543831532&country=kr
2. iLEAPP 저장소 scripts/artifacts 목록 — https://api.github.com/repos/abrignoni/iLEAPP/contents/scripts/artifacts
3. iLEAPP applicationStateDB.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/applicationStateDB.py
4. iLEAPP uninstalledApplications.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/uninstalledApplications.py
5. 안원석·박명서, 「디지털 포렌식 관점의 네이버 밴드 사용자 행위 수집 및 분석 연구」, 정보보호학회논문지 34(6), 1263-1272쪽, 2024, DOI 10.13089/JKIISC.2024.34.6.1263 — https://koreascience.kr/article/JAKO202404357602838.page
6. Apple, File System Programming Guide — File System Basics(보관 문서) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html
7. Apple Platform Security, Data Protection classes — https://support.apple.com/guide/security/data-protection-classes-secb010e978a/web
