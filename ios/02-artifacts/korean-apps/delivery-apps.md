---
title: "배달 앱"
parent: "아티팩트 · 국내 생활 앱"
nav_order: 960
---

# 배달 앱 (배달의민족·쿠팡이츠·요기요)

## 한 줄 요약

아이폰의 배달의민족·쿠팡이츠·요기요 앱은 번들 ID 가 각각 `com.jawebs.baedal`·`com.coupang.coupang-eats`·`com.yogiyo.yogiyoapp` 이고, 주문·배달 주소·결제 흔적이 기기 안 어디에 남는지 적은 공개 iOS 자료가 없어서 시스템 흔적과 위치 흔적으로 앱 사용 구간을 먼저 좁혀야 합니다.

## 무엇을 기록하나 · 왜 생기나

세 앱은 손님이 음식점을 골라 주문하고 배달받는 앱이고, 주문·결제·배달 상태 같은 서비스 데이터는 서버에 원본이 있습니다. 기기에는 앱이 데이터 컨테이너에 내려받아 둔 사본과 설정이 남습니다[5]. 주문 내역, 배달 주소, 결제 흔적이 기기 안 어디에 어떤 형태로 남는지는 이번에 확인한 공개 자료로는 밝히지 못했습니다.

세 앱의 iOS 포렌식 공개 논문이나 도구 문서도 찾지 못했고, 공개 분석 도구 iLEAPP 에도 세 앱 전용 분석기가 없습니다[2]. 그래서 이 페이지는 세 앱을 찾아 구분하는 방법과 해석할 때 조심할 점을 중심으로 씁니다.

## 위치와 버전별 차이

| 앱 | 판매자 | 번들 ID | 조회 시점 앱 버전 | 최소 iOS |
|---|---|---|---|---|
| 배달의민족 | Woowa Bros Co., Ltd. | `com.jawebs.baedal` | 16.24.0 (2026-09-23) | 17.0 |
| 쿠팡이츠 | Coupang Corp. | `com.coupang.coupang-eats` | 1.15.0 (2026-09-22) | 15.0 |
| 요기요 | Wesang Co., Ltd. | `com.yogiyo.yogiyoapp` | 10.4.1 (2026-09-23) | 15.0 |

표의 값은 2026-09-25 한국 스토어 조회 결과이고, 배포일은 UTC 날짜라서 한국 시각으로는 하루 늦을 수 있고, 최소 iOS 는 지금 앱 버전 기준입니다[1]. 한국 스토어 이름은 "배달의민족 - 배달팁 무료 배민클럽", "쿠팡이츠 - 와우회원 배달비 0원", "요기요 - 배달할 때마다 포인트 적립" 입니다[1].

배달의민족 번들 ID 에는 woowa 나 baemin 이 아니라 jawebs 가 들어 있습니다[1]. 쿠팡이츠는 쿠팡 쇼핑 앱과 판매자가 같지만 번들 ID 가 다른 별개 앱이고[1], 쇼핑 앱은 [쿠팡](coupang.md)에서 다룹니다. 음식점 사장님용 앱과 배달 파트너용 앱도 손님용 앱과는 별개 앱이라서, 이 페이지의 번들 ID 로는 찾을 수 없습니다.

로컬 백업 도메인은 규칙상 `AppDomain-com.jawebs.baedal`, `AppDomain-com.coupang.coupang-eats`, `AppDomain-com.yogiyo.yogiyoapp` 입니다. 관찰한 백업은 다른 회사 앱 도메인 이름을 가려 두어서 세 도메인을 실물로 보지는 못했고, 이 규칙과 가려진 범위는 [네이버 밴드](band.md)에 적었습니다. 전체 파일시스템 추출에서 번들 ID 로 데이터 컨테이너 경로를 찾는 방법은 [설치된 앱](../app-usage/installed-apps.md)에 있습니다.

옛 앱 버전은 더 낮은 iOS 에서도 돌았을 수 있고, iOS 버전이나 앱 버전에 따라 저장 구조가 어떻게 달랐는지는 근거를 찾지 못해서 버전별 차이 표는 싣지 않습니다.

## 구조

세 앱의 DB 이름, 표와 칸, 가게·메뉴 이미지 캐시 위치는 이번에 연 공개 자료에 없었습니다. 컨테이너 안 파일을 형식별로 나눠 하나씩 열어야 하고, 여는 순서는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md)을 따릅니다. 컨테이너 안에서 `Library/Caches/` 와 `tmp/` 는 로컬 백업에 들어가지 않아서[5], 앱이 캐시에 둔 파일은 전체 파일시스템 추출에서만 볼 수 있습니다.

## 증거로서 의미

**증명하는 것**

로컬 백업의 `Manifest.db` 에 배달 앱 도메인 항목이 있으면 백업 시점에 그 기기에 그 앱 데이터가 있었다는 뜻입니다. 앱 안에서 주문 기록이나 저장된 배달 주소를 찾았다면 그 값이 기기에 있었다는 사실까지 쓸 수 있습니다.

**증명하지 못하는 것**

앱에 저장된 배달 주소는 사용자가 등록한 주소일 뿐, 주문한 사람이 그 주소에 있었다거나 그곳에 산다는 증거가 되지 않습니다. 주문 기록도 그 계정으로 로그인한 앱이 남긴 기록이라 폰을 쓴 사람은 따로 밝혀야 하고, 이 판단은 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)를 봅니다. 기기에 주문 기록이 없어도 주문하지 않았다는 뜻은 아니고, 주문 원본은 서버에 있어서 사업자에게 요청할 대상입니다. 요청 절차는 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md)를 봅니다. 앱 화면 스냅숏 목록의 시각이 사용 증거가 아니라는 점은 [설치된 앱](../app-usage/installed-apps.md)에 있습니다[3].

## 시각 해석

세 앱 데이터 안의 시각 형식은 공개 자료가 없습니다. 숫자 시각을 만나면 자릿수와 범위로 Unix 초·밀리초인지 Mac 절대 시각인지 가리고, 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md)을 봅니다. 주문 시각, 배달 완료 시각처럼 이름이 비슷한 값이 여럿 있을 수 있어서, 시험 기기에서 주문 단계마다 어떤 값이 바뀌는지 확인한 뒤에 보고서에 씁니다.

## 함정과 한계

배달의민족은 번들 ID 에 회사 이름이나 서비스 이름이 없어서 "baemin" 이나 "woowa" 로 검색하면 놓칩니다. 쿠팡이츠를 `LIKE '%coupang%'` 로 찾으면 쿠팡 쇼핑 앱 도메인도 함께 걸려서, 결과를 도메인별로 나눠 봐야 합니다.

배달 주소나 위치는 앱이 저장한 값이라 기기가 실제로 있던 곳과 다를 수 있고, 시스템 위치 흔적과 맞춰 봐야 합니다. 앱을 지웠을 때 남을 수 있는 `UninstalledApplications.plist` 와 그 한계는 [설치된 앱](../app-usage/installed-apps.md)을 봅니다[4]. 서드파티 앱 데이터의 기본 보호 등급은 Class C(첫 잠금 해제 후 보호)이고[6] 세 앱이 실제로 쓰는 등급은 확인하지 못했습니다.

## 직접 분석해 보기

**헥스로 한 번**

컨테이너 안에서 확장자가 없는 파일은 앞부분으로 형식을 가립니다. 아래 두 줄은 SQLite 와 바이너리 plist 형식 명세로 만든 예시이고 검체에서 뽑은 값이 아닙니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
00000000  62 70 6C 69 73 74 30 30                          bplist00
```

형식별 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)와 [속성 목록 파일](../../01-foundations/data-formats/plist.md)을 봅니다.

**공개 도구로 한 번**

iLEAPP 에 전용 분석기가 없어서[2] 설치·삭제 흔적은 applicationState 분석기와 uninstalledApplications 분석기 결과에서 번들 ID 로 찾습니다[3][4]. 로컬 백업이라면 sqlite3 로 `Manifest.db` 의 `Files` 표에서 세 앱 도메인을 한 번에 셉니다(칸 이름 확인 범위: iOS 27.0).

```sql
SELECT domain, COUNT(*) AS files
FROM Files
WHERE domain IN ('AppDomain-com.jawebs.baedal',
                 'AppDomain-com.coupang.coupang-eats',
                 'AppDomain-com.yogiyo.yogiyoapp')
GROUP BY domain;
```

도메인이 나오면 `relativePath` 를 뽑아 파일 목록을 보고, 나오지 않으면 `LIKE` 로 앱 그룹이나 확장 도메인을 넓게 찾습니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [중요 위치](../location/significant-locations.md) · [위치 기록 데몬](../location/routined.md) | 주문 시간대에 기기가 머문 위치 |
| [알림 기록](../app-usage/notifications.md) | 주문 접수·배달 알림이 온 시각 |
| [KnowledgeC](../app-usage/knowledgec/index.md) · [바이옴](../app-usage/biome/index.md) | 앱이 앞에 뜬 구간 |
| [지갑과 Apple Pay](../health-wallet/wallet.md) | 기기 쪽 결제 흔적 |
| [설치된 앱](../app-usage/installed-apps.md) | 번들 ID 와 데이터 컨테이너 연결, 앱 삭제 흔적 |
| [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) | 서버 쪽 주문 자료 요청 |

주문 시각의 위치를 맞춰 보는 흐름은 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md)를 봅니다.

## 실습

공개 iOS 검체(NIST CFReDS 등)에 세 앱이 들어 있는지는 확인하지 않았습니다. 확보한 검체나 직접 만든 시험 기기로 아래 질문을 풀어 봅니다.

1. `Manifest.db` 에서 세 앱 도메인을 찾고, 어느 앱이 백업에 들어 있는지 표로 정리합니다.
2. 시험 기기에서 배달 주소 하나를 등록하고 다시 백업해서, 어떤 파일이 바뀌는지 기록합니다.
3. 주문 알림 시각과 같은 시간대의 중요 위치 기록이 서로 맞는지 비교합니다.
4. 쿠팡 쇼핑 앱과 쿠팡이츠가 함께 깔린 기기에서 두 앱의 도메인과 데이터 컨테이너를 따로 구분해 냅니다.

## 참고 문헌

1. Apple iTunes Search API 조회 결과(한국 스토어, 2026-09-25 조회) — https://itunes.apple.com/lookup?id=542613198,1018769995,454434967,378084485,1445504255,543831532&country=kr
2. iLEAPP 저장소 scripts/artifacts 목록 — https://api.github.com/repos/abrignoni/iLEAPP/contents/scripts/artifacts
3. iLEAPP applicationStateDB.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/applicationStateDB.py
4. iLEAPP uninstalledApplications.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/uninstalledApplications.py
5. Apple, File System Programming Guide — File System Basics(보관 문서) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html
6. Apple Platform Security, Data Protection classes — https://support.apple.com/guide/security/data-protection-classes-secb010e978a/web
