---
title: "쿠팡"
parent: "아티팩트 · 국내 생활 앱"
nav_order: 950
---

# 쿠팡 (Coupang)

## 한 줄 요약

아이폰의 쿠팡 쇼핑 앱은 번들 ID 가 대문자 C 가 섞인 `com.coupang.Coupang` 이고, 같은 회사의 쿠팡이츠와는 다른 앱이며, 주문·검색 기록이 기기에 어떻게 남는지 적은 공개 iOS 자료가 없어서 시스템 흔적으로 설치·사용 여부부터 확인해야 합니다.

## 무엇을 기록하나 · 왜 생기나

쿠팡은 Coupang Corp. 가 내는 쇼핑 앱이고, 한국 앱 스토어 이름은 "쿠팡(Coupang)-모바일 쇼핑" 입니다[1]. 주문·결제·배송 같은 서비스 데이터는 서버에 원본이 있고, 기기에는 앱이 데이터 컨테이너에 내려받아 둔 사본과 설정이 남습니다[5]. 주문 내역, 검색 기록, 장바구니가 기기에 어떤 형태로 남는지는 알려져 있지 않아 실제 기기로 확인해야 합니다.

쿠팡 iOS 앱을 다룬 공개 포렌식 논문이나 도구 문서가 없고, 공개 분석 도구 iLEAPP 에도 쿠팡 전용 분석기가 없습니다[2]. 그래서 앱을 찾는 방법과 해석할 때 조심할 점부터 봅니다.

## 위치와 버전별 차이

| 항목 | 값 |
|---|---|
| 번들 ID | `com.coupang.Coupang` [1] |
| 로컬 백업 도메인(규칙상) | `AppDomain-com.coupang.Coupang` |
| 조회 시점 앱 버전 | 9.3.9 (2026-09-25 배포, UTC) [1] |
| 최소 iOS | 15.1 (지금 앱 버전 기준) [1] |
| 조회일 | 2026-09-25, 한국 스토어 [1] |

같은 판매자의 쿠팡이츠는 번들 ID 가 `com.coupang.coupang-eats` 인 별개 앱이고[1], 따로 [배달 앱](delivery-apps.md)에서 다룹니다.

백업 도메인 이름은 `AppDomain-` 뒤에 번들 ID 를 붙이는 규칙을 따릅니다. 이 규칙은 [네이버 밴드](band.md)에 있습니다. 전체 파일시스템 추출에서 번들 ID 로 데이터 컨테이너 경로를 찾는 방법은 [설치된 앱](../app-usage/installed-apps.md)에 있습니다.

옛 앱 버전은 더 낮은 iOS 에서도 돌았을 수 있고, iOS 버전이나 앱 버전에 따라 저장 구조가 어떻게 달랐는지는 공개 자료가 없습니다.

## 구조

iOS 쿠팡 앱의 DB 이름, 표와 열, 상품 이미지 캐시 위치는 공개 자료가 없습니다. 컨테이너 안 파일을 형식별로 나눠 하나씩 열어야 하고, 여는 순서는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md)을 따릅니다.

컨테이너 안에서 `Library/Caches/` 와 `tmp/` 는 로컬 백업에 들어가지 않습니다[5]. 쿠팡 앱이 상품 이미지를 캐시에 둔다면 로컬 백업에서는 보이지 않고 전체 파일시스템 추출에서만 볼 수 있습니다.

## 증거로서 의미

**증명하는 것**

로컬 백업의 `Manifest.db` 에 쿠팡 도메인 항목이 있으면 백업 시점에 그 기기에 쿠팡 앱 데이터가 있었다는 뜻입니다. 앱 안에서 주문이나 검색 기록 사본을 찾았다면, 그 기록이 기기에 있었고 앱이 적은 시각이 그렇다는 사실까지 쓸 수 있습니다.

**증명하지 못하는 것**

앱에 남은 검색어나 본 상품은 그 계정으로 로그인한 앱이 남긴 기록이라, 그 시각에 폰을 누가 들고 있었는지는 따로 밝혀야 합니다. 이 판단은 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)를 봅니다. 기기에 주문 기록이 없다고 해서 주문하지 않았다는 뜻도 아니고, 주문 내역의 원본은 서버에 있어서 사업자에게 요청할 대상입니다. 요청 절차는 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md)를 봅니다. 앱 화면 스냅숏 목록의 시각이 사용 증거가 아니라는 점은 [설치된 앱](../app-usage/installed-apps.md)에 있습니다[3].

## 시각 해석

쿠팡 앱 데이터 안의 시각 형식은 공개 자료가 없습니다. 숫자 시각을 만나면 자릿수와 범위로 Unix 초·밀리초인지 Mac 절대 시각인지 구분하고, 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md)을 봅니다. 주문 시각이라면 기기가 적은 시각인지 서버가 내려 준 시각인지에 따라 뜻이 달라서, 시험 기기에서 주문 화면을 열 때 값이 바뀌는지 확인한 뒤에 씁니다.

## 함정과 한계

번들 ID 의 마지막 `Coupang` 은 대문자 C 로 시작합니다[1]. SQLite 에서 `=` 비교는 대소문자를 구분해서 `'AppDomain-com.coupang.coupang'` 으로 찾으면 아무것도 나오지 않습니다. 반대로 `LIKE '%coupang%'` 는 영문 대소문자를 구분하지 않아서 쿠팡과 쿠팡이츠 도메인이 함께 걸리니, 결과를 도메인별로 나눠 봐야 합니다.

알림 기록에 쿠팡 항목이 있다는 사실은 앱이 알림을 보냈다는 뜻이고, 사용자가 앱을 열었다는 뜻은 아닙니다. 앱을 지웠을 때 남을 수 있는 `UninstalledApplications.plist` 와 그 한계는 [설치된 앱](../app-usage/installed-apps.md)을 봅니다[4]. 서드파티 앱 데이터의 기본 보호 등급은 Class C(첫 잠금 해제 후 보호)이고[6] 쿠팡이 실제로 쓰는 등급은 실제 기기에서 확인합니다.

## 직접 분석해 보기

**헥스로 한 번**

컨테이너 안에서 확장자가 없는 파일은 앞부분으로 형식을 판별합니다. 아래는 SQLite 파일 형식 명세로 만든 예시이고 실제 기기에서 뽑은 값이 아닙니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

SQLite 파일을 여는 법과 함께 복사할 파일은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)를 봅니다.

**공개 도구로 한 번**

iLEAPP 에 전용 분석기가 없어서[2] 설치·삭제 흔적은 applicationState 분석기와 uninstalledApplications 분석기 결과에서 번들 ID 로 찾습니다[3][4]. 로컬 백업이라면 sqlite3 로 `Manifest.db` 의 `Files` 표를 봅니다.

```sql
SELECT domain, COUNT(*) AS files
FROM Files
WHERE domain LIKE '%coupang%'
GROUP BY domain;
```

이 결과에서 쿠팡 쇼핑 앱 도메인만 골라 `relativePath` 를 뽑습니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [설치된 앱](../app-usage/installed-apps.md) | 번들 ID 와 데이터 컨테이너 연결, 앱 삭제 흔적 |
| [알림 기록](../app-usage/notifications.md) | 주문·배송 알림이 온 시각 |
| [KnowledgeC](../app-usage/knowledgec/index.md) · [바이옴](../app-usage/biome/index.md) | 앱이 앞에 뜬 구간 |
| [화면 사용 시간](../app-usage/screen-time.md) | 앱별 사용 시간 |
| [지갑과 Apple Pay](../health-wallet/wallet.md) | 기기 쪽 결제 흔적 |
| [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) | 서버 쪽 주문 자료 요청 |

## 실습

확보한 증거물이나 직접 만든 시험 기기로 아래 질문을 풀어 봅니다.

1. `Manifest.db` 에서 `coupang` 이 들어간 도메인을 모두 뽑고, 쇼핑 앱과 쿠팡이츠 도메인을 나눕니다.
2. 시험 기기에서 상품 하나를 검색하고 다시 백업해서, 어떤 파일이 바뀌는지 기록합니다.
3. 같은 검색을 한 뒤 전체 파일시스템 추출을 해서, 로컬 백업에 없던 캐시 파일이 무엇인지 비교합니다.
4. 주문 알림 시각과 앱이 앞에 뜬 구간이 서로 맞는지 비교합니다.

## 참고 문헌

1. Apple iTunes Search API 조회 결과(한국 스토어, 2026-09-25 조회) — https://itunes.apple.com/lookup?id=542613198,1018769995,454434967,378084485,1445504255,543831532&country=kr
2. iLEAPP 저장소 scripts/artifacts 목록 — https://api.github.com/repos/abrignoni/iLEAPP/contents/scripts/artifacts
3. iLEAPP applicationStateDB.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/applicationStateDB.py
4. iLEAPP uninstalledApplications.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/uninstalledApplications.py
5. Apple, File System Programming Guide — File System Basics(보관 문서) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html
6. Apple Platform Security, Data Protection classes — https://support.apple.com/guide/security/data-protection-classes-secb010e978a/web
