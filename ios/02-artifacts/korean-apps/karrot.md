---
title: "당근"
parent: "아티팩트 · 국내 생활 앱"
nav_order: 940
---

# 당근 (Karrot)

## 한 줄 요약

아이폰의 당근 앱은 번들 ID 가 옛 회사 이름이 들어간 `com.towneers.www` 이고, 중고거래 앱 연구가 사용자 정보·마지막 사용 일시·위치·채팅을 핵심 흔적으로 꼽았지만 iOS 안의 구체 경로는 공개 자료로 확인되지 않아서 시스템 흔적과 위치 흔적을 함께 봐야 합니다.

## 무엇을 기록하나 · 왜 생기나

당근은 Danggeun Market Inc. 가 내는 중고거래 앱이고, 한국 앱 스토어 이름은 "당근" 입니다[1]. 2022 년 논문이 나올 때 이름은 "당근마켓" 이었습니다[1][5]. 거래 글과 채팅 같은 서비스 데이터는 서버에 원본이 있고, 기기에는 앱이 데이터 컨테이너에 내려받아 둔 사본과 설정이 남습니다[6]. 기기에 무엇이 얼마나 남는지는 이번에 확인한 공개 자료로는 밝히지 못했습니다.

이성현·조민호·손태식(아주대)은 당근마켓·번개장터·중고나라를 안드로이드와 iOS 둘 다에서 분석했고, 핵심 아티팩트로 사용자 정보, 마지막 사용 일시, 위치 정보, 채팅 정보를 꼽았습니다[5]. 연구 배경으로는 사기·마약 유통·성희롱·강력범죄 수사를 들었습니다[5]. 다만 공개된 초록에는 파일 경로, DB 이름, 표와 칸, 시각 형식이 없고 유료 본문은 열지 못해서, 이 페이지에는 논문의 구체 경로를 싣지 않습니다.

## 위치와 버전별 차이

| 항목 | 값 |
|---|---|
| 번들 ID | `com.towneers.www` [1] |
| 로컬 백업 도메인(규칙상) | `AppDomain-com.towneers.www` |
| 조회 시점 앱 버전 | 26.39.0 (2026-09-23 배포, UTC) [1] |
| 최소 iOS | 17.0 (지금 앱 버전 기준) [1] |
| 조회일 | 2026-09-25, 한국 스토어 [1] |

번들 ID 에 danggeun 이나 karrot 이 아니라 옛 회사 이름 towneers 가 들어 있습니다[1]. 백업 도메인 이름은 `AppDomain-` 뒤에 번들 ID 를 붙이는 규칙으로 적은 것이고, 관찰한 백업은 다른 회사 앱 도메인 이름을 가려 두어서 당근 도메인을 실물로 보지는 못했습니다. 이 규칙과 가려진 범위는 [네이버 밴드](band.md)에 자세히 적었습니다.

전체 파일시스템 추출에서 번들 ID 로 데이터 컨테이너 경로를 찾는 방법은 [설치된 앱](../app-usage/installed-apps.md)에 있습니다. 옛 앱 버전은 더 낮은 iOS 에서도 돌았을 수 있고, iOS 버전이나 앱 버전에 따라 저장 구조가 어떻게 달랐는지는 근거를 찾지 못해서 버전별 차이 표는 싣지 않습니다.

## 구조

iOS 당근 앱의 DB 이름, 표와 칸, 채팅 사진 캐시 위치는 이번에 연 공개 자료에 없었고, 공개 분석 도구 iLEAPP 에도 당근 전용 분석기가 없습니다[2]. 논문이 꼽은 네 가지(사용자 정보·마지막 사용 일시·위치·채팅)를 찾을 목표로 삼고, 컨테이너 안 파일을 형식별로 나눠 하나씩 여는 수밖에 없습니다. 여는 순서는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md)을 따릅니다.

컨테이너 안에서 `Library/Caches/` 와 `tmp/` 는 로컬 백업에 들어가지 않습니다[6]. 채팅에 오간 사진이 캐시로만 남는다면 로컬 백업에서는 보이지 않고 전체 파일시스템 추출에서만 볼 수 있지만, 당근이 사진을 어디에 두는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것**

로컬 백업의 `Manifest.db` 에 당근 도메인 항목이 있으면 백업 시점에 그 기기에 당근 앱 데이터가 있었다는 뜻입니다. 앱 안에서 채팅이나 거래 글 사본을 찾았다면 그 내용이 기기에 있었다는 사실까지 말할 수 있고, 거래 상대와 주고받은 시각을 앱 기록이 보여 주는 만큼 쓸 수 있습니다.

**증명하지 못하는 것**

앱 안의 동네 정보나 위치 값은 앱이 저장한 값일 뿐, 그 시각에 기기가 그 자리에 있었다는 증거가 되지는 않습니다. 동네 인증 위치가 앱 안에 남는지 시스템 위치 흔적에 남는지도 확인하지 못했습니다. 실제 거래가 이뤄졌는지, 돈이 오갔는지는 채팅만으로 말할 수 없고 결제·송금 기록을 따로 봐야 합니다. 앱 화면 스냅숏 목록의 시각이 사용 증거가 아니라는 점은 [설치된 앱](../app-usage/installed-apps.md)에 있습니다[3].

## 시각 해석

논문은 마지막 사용 일시를 핵심 흔적으로 꼽았지만 공개된 초록에는 시각 형식이 없습니다[5]. 앱 안에서 숫자 시각을 만나면 자릿수와 범위로 Unix 초·밀리초인지 Mac 절대 시각인지 가리고, 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md)을 봅니다. 앱 안의 "마지막 사용 일시" 가 앱을 연 시각인지, 서버와 마지막으로 맞춘 시각인지는 값이 바뀌는 조건을 시험 기기로 확인한 뒤에 보고서에 씁니다.

## 함정과 한계

번들 ID 에 당근을 뜻하는 영어 단어가 없어서 "karrot" 이나 "danggeun" 으로 검색하면 놓칩니다. 논문은 2022 년 앱을 대상으로 해서 지금 앱과 저장 구조가 다를 수 있고, 이 점도 확인하지 못했습니다.

거래 상대가 채팅방을 나가거나 글을 지우면 기기 쪽 사본이 어떻게 바뀌는지는 공개 자료가 없습니다. 앱을 지웠을 때 남을 수 있는 `UninstalledApplications.plist` 와 그 한계는 [설치된 앱](../app-usage/installed-apps.md)을 봅니다[4]. 서드파티 앱 데이터의 기본 보호 등급은 Class C(첫 잠금 해제 후 보호)이고[7] 당근이 실제로 쓰는 등급은 확인하지 못했습니다.

## 직접 분석해 보기

**헥스로 한 번**

설정이나 상태를 담은 plist 는 바이너리 형식이면 앞 8바이트가 아래와 같습니다. plist 형식 명세로 만든 예시이고 검체에서 뽑은 값이 아닙니다.

```
00000000  62 70 6C 69 73 74 30 30                          bplist00
```

뒤쪽 구조를 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md)에 있습니다.

**공개 도구로 한 번**

iLEAPP 에 전용 분석기가 없어서[2] 설치·삭제 흔적은 applicationState 분석기와 uninstalledApplications 분석기 결과에서 번들 ID 로 찾습니다[3][4]. 로컬 백업이라면 sqlite3 로 `Manifest.db` 의 `Files` 표를 봅니다.

```sql
SELECT fileID, relativePath, flags
FROM Files
WHERE domain LIKE '%towneers%'
ORDER BY domain, relativePath;
```

`LIKE` 로 찾으면 앱 그룹이나 확장 도메인에 towneers 가 들어 있을 때 함께 걸리지만, 앱 그룹 이름에 이 글자가 꼭 들어간다는 보장은 없습니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [중요 위치](../location/significant-locations.md) · [위치 기록 데몬](../location/routined.md) | 앱 밖에서 기기가 머문 위치 |
| [사진 보관함](../media/photos/index.md) · [카메라 사진과 메타데이터](../media/dcim-exif.md) | 거래 글에 올린 사진의 원본과 촬영 정보 |
| [알림 기록](../app-usage/notifications.md) | 채팅 알림이 온 시각 |
| [KnowledgeC](../app-usage/knowledgec/index.md) · [바이옴](../app-usage/biome/index.md) | 앱이 앞에 뜬 구간 |
| [설치된 앱](../app-usage/installed-apps.md) | 번들 ID 와 데이터 컨테이너 연결, 앱 삭제 흔적 |
| [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) | 서버 쪽 자료 요청 |

거래 장소와 시각을 맞춰 보는 흐름은 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md)를 봅니다.

## 실습

공개 iOS 검체(NIST CFReDS 등)에 당근 앱이 들어 있는지는 확인하지 않았습니다. 확보한 검체나 직접 만든 시험 기기로 아래 질문을 풀어 봅니다.

1. `Manifest.db` 에서 `towneers` 가 들어간 도메인을 모두 뽑고 도메인마다 파일 수를 셉니다.
2. 컨테이너 안에서 사용자 정보·마지막 사용 일시·위치·채팅에 해당하는 파일을 하나씩 찾아 표로 정리합니다.
3. 시험 기기에서 채팅 하나를 보내고 다시 백업해서, 어떤 파일의 수정 시각과 내용이 바뀌는지 기록합니다.
4. 앱이 남긴 위치 값과 같은 시간대의 중요 위치 기록이 서로 맞는지 비교합니다.

## 참고 문헌

1. Apple iTunes Search API 조회 결과(한국 스토어, 2026-09-25 조회) — https://itunes.apple.com/lookup?id=542613198,1018769995,454434967,378084485,1445504255,543831532&country=kr
2. iLEAPP 저장소 scripts/artifacts 목록 — https://api.github.com/repos/abrignoni/iLEAPP/contents/scripts/artifacts
3. iLEAPP applicationStateDB.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/applicationStateDB.py
4. iLEAPP uninstalledApplications.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/uninstalledApplications.py
5. 이성현·조민호·손태식, 「중고거래 어플리케이션에서의 아티팩트 수집 및 분석」, 디지털포렌식연구 16(1), 37-53쪽, 2022, UCI I410-ECN-0101-2022-036-001147564 (DBpia 초록) — https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE11052959
6. Apple, File System Programming Guide — File System Basics(보관 문서) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html
7. Apple Platform Security, Data Protection classes — https://support.apple.com/guide/security/data-protection-classes-secb010e978a/web
