---
title: "세션 복원"
parent: "파이어폭스"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1750
---

# 세션 복원 (sessionstore.jsonlz4)

## 한 줄 요약

파이어폭스는 다시 켤 때 전에 열려 있던 창과 탭을 되살리려고 세션 (session) 상태를 파일로 남깁니다. 정상 종료 때 쓰는 파일과 실행 중에 쓰는 파일이 따로 있고, 두 파일 모두 바로 앞 판을 하나씩 더 두므로 여러 판을 풀어 비교하면 서로 다른 시점에 열려 있던 탭을 볼 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

세션 복원 (Session Restore) 은 브라우저를 다시 켰을 때 전에 열려 있던 창과 탭을 되살리는 기능입니다. 파이어폭스는 세션 상태를 LZ4 로 압축해 파일에 쓰고 읽을 때 압축을 풉니다. 파일 확장자는 `.jsonlz4` 이고, 압축을 풀면 JSON 텍스트가 나옵니다.

탭마다 뒤로 가기·앞으로 가기 기록도 함께 저장하며, 몇 개까지 저장할지는 `browser.sessionstore.max_serialize_back`, `browser.sessionstore.max_serialize_forward` 설정이 정합니다. 실행 중에도 충돌이나 갑작스러운 종료 뒤에 탭을 되살리려고 세션을 따로 파일에 쓰고, 파이어폭스를 업그레이드할 때는 그 시점의 세션을 백업 파일로 남깁니다.

## 위치와 버전별 차이

- 세션 파일은 프로필 본 폴더와 그 아래 `sessionstore-backups` 폴더에 있습니다. 프로필 본 폴더를 찾는 법은 [프로필 구조 (profiles.ini·prefs.js)](profiles-ini-prefs-js.md) 에서 다룹니다.
- `sessionstore.jsonlz4` 는 프로필 본 폴더 바로 아래에 있습니다.
- `previous.jsonlz4`, `recovery.jsonlz4`, `recovery.baklz4`, `upgrade.jsonlz4-<빌드 ID>` 는 `sessionstore-backups` 안에 있습니다.
- 아래 파일 이름과 역할은 파이어폭스 소스의 개발 중인 최신 코드(main 가지, 2026-09-23)에서 확인한 것입니다. 예전 출시판의 동작은 이 자료로 알 수 없습니다.
- 소스에는 압축하지 않은 옛 파일(확장자 `.js`·`.bak`)을 읽는 코드도 남아 있습니다. 옛 검체에서는 이런 파일도 찾습니다.
- 몇 번 출시판부터 압축 파일로 바뀌었는지는 확인하지 못했습니다.

## 구조

### 파일과 쓰는 때

소스는 세션 파일 다섯 종류에 각각 이름을 붙여 다룹니다.

| 파일 | 소스 속 이름 | 쓰는 때와 담는 것 |
|---|---|---|
| `sessionstore.jsonlz4` | clean | 정상 종료 때 씁니다. 마지막으로 정상 종료한 세션입니다 |
| `previous.jsonlz4` | cleanBackup | clean 의 바로 앞 판입니다. clean 을 제대로 읽을 때마다 새로 씁니다 |
| `recovery.jsonlz4` | recovery | 실행 중에 씁니다. 충돌·갑작스러운 종료에 대비한 최신 세션입니다 |
| `recovery.baklz4` | recoveryBackup | recovery 의 바로 앞 판입니다. recovery 까지 깨질 만큼 큰 충돌에 대비합니다 |
| `upgrade.jsonlz4-<빌드 ID>` | upgradeBackup | 파이어폭스를 업그레이드할 때 만든 백업입니다 |

- 업그레이드 백업은 기본으로 3개까지 둡니다. 이 개수는 `browser.sessionstore.upgradeBackup.maxUpgradeBackups` 설정이 정합니다.
- 소스 주석은 업그레이드 백업에 clean 보다 민감한 정보가 없다고 적었습니다.
- 업그레이드 백업 파일 이름 끝에는 파이어폭스의 빌드 ID(`Services.appinfo.platformBuildID`)를 붙입니다. 마지막으로 백업한 빌드 ID 는 `browser.sessionstore.upgradeBackup.latestBuildID` 설정에 남습니다.

### 시작할 때 읽는 순서

파이어폭스는 시작할 때 아래 순서로 세션 파일을 찾습니다.

1. clean (`sessionstore.jsonlz4`)
2. recovery (`recovery.jsonlz4`)
3. recoveryBackup (`recovery.baklz4`)
4. cleanBackup (`previous.jsonlz4`)
5. upgradeBackup (`upgrade.jsonlz4-<빌드 ID>`) — 있을 때만 맨 끝에 더합니다

이 순서는 파이어폭스가 어느 파일로 복원할지 고르는 순서일 뿐이고, 분석할 때는 파일마다 다른 시점의 세션이 들어 있으므로 순서와 상관없이 모든 파일을 풉니다.

### 파일 안

- 압축을 풀면 창과 탭, 탭마다의 탐색 기록을 담은 JSON 이 나옵니다.
- 이번 조사에서 아래 항목은 확인하지 못했습니다. 이 페이지에는 그 값을 적지 않습니다.
  - 파일 머리의 바이트 배치
  - JSON 안의 키 이름과 층 구성
  - JSON 안 시각 칸의 단위
  - 닫은 창·닫은 탭 목록이 남는지
  - 실행 중에 recovery 파일을 몇 초마다 쓰는지
  - 사생활 보호 창 (Private Browsing) 의 탭이 세션 파일에 남는지

## 증거로서 의미

### 증명하는 것

- 세션 파일에 든 탭은 파이어폭스가 그 파일을 쓸 때 그 프로필에서 열려 있던 탭입니다.
- 탭마다 남은 뒤로·앞으로 가기 기록은 그 탭에서 거쳐 간 페이지를 보여 줍니다.
- 판이 여러 개면 서로 다른 시점의 탭 상태를 비교할 수 있습니다.
- `previous.jsonlz4` 는 앞선 정상 종료 때의 세션입니다. 업그레이드 백업은 업그레이드할 때의 세션입니다.

### 증명하지 못하는 것

- 탭이 열려 있었다는 것과 사용자가 그 페이지를 읽었다는 것은 다릅니다.
- 파일에는 쓴 순간의 상태만 남습니다. 두 번 쓰는 사이에 열었다 닫은 탭은 남지 않을 수 있습니다.
- 키보드 앞의 사람이 누구인지는 알 수 없습니다.
- 세션 파일이 없거나 탭이 적다고 브라우저를 쓰지 않았다고 단정하지 않습니다. 파일을 지웠거나 새 판으로 갈아 썼을 수 있습니다.

보고서에는 "이 사이트를 열어 두었다" 대신 "이 프로필의 `recovery.jsonlz4` 를 풀면 그 주소의 탭이 있고, 이 파일의 마지막 수정 시각은 X(UTC) 이다" 처럼 씁니다.

## 시각 해석

- 세션 파일 안 시각 칸의 단위는 확인하지 못했습니다. 안의 시각을 쓰려면 먼저 같은 주소의 방문 시각과 맞춰 단위를 확인합니다. 방문 시각의 단위는 [방문·다운로드·즐겨찾기 (places.sqlite)](places-sqlite.md) 에서 다룹니다.
- 파일 자체의 시각은 파일 시스템에서 읽습니다. [$MFT](../../filesystem/mft.md) 의 수정 시각은 파이어폭스가 그 파일을 마지막으로 쓴 때입니다.
- 파일마다 쓰는 때가 다르므로 수정 시각의 뜻도 다릅니다.

| 파일 | 수정 시각이 가리키는 때 |
|---|---|
| `sessionstore.jsonlz4` | 마지막 정상 종료 무렵입니다 |
| `recovery.jsonlz4` | 실행 중 마지막으로 세션을 쓴 무렵입니다 |
| `previous.jsonlz4` | 시작하면서 clean 을 읽은 무렵이거나, 앞선 정상 종료 무렵입니다. clean 을 옮겨 만드는지 새로 쓰는지 확인하지 못해 어느 쪽인지 단정하지 않습니다 |
| `upgrade.jsonlz4-<빌드 ID>` | 파이어폭스를 업그레이드한 무렵입니다. 파일 이름의 빌드 ID 로 어느 판으로 올렸는지 봅니다 |

- 위 표는 소스가 밝힌 파일 역할에서 끌어낸 해석입니다. 검체에서 다른 기록과 맞춰 확인합니다.
- `recovery.jsonlz4` 가 `sessionstore.jsonlz4` 보다 새것이면, 마지막 실행이 정상 종료로 끝나지 않았을 수 있습니다. 수집할 때까지 브라우저가 돌고 있었을 수도 있습니다. [켜짐·꺼짐](../../event-logs/power-on-off-events.md) 기록과 맞춰 봅니다.
- 여러 시각을 한 시간 축에 놓을 때는 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 을 따릅니다.

## 함정과 한계

- **원본 프로필로 브라우저를 켜지 않습니다.** 파이어폭스는 시작할 때 세션 파일을 읽고 `previous.jsonlz4` 를 새로 쓰므로 옛 판이 사라집니다. 해시를 기록한 사본으로 분석합니다.
- **한 파일만 보고 끝내지 않습니다.** 파일마다 다른 시점의 세션이 들어 있으므로 모든 판을 풀어 비교합니다.
- **두 폴더를 모두 봅니다.** `sessionstore.jsonlz4` 만 본 폴더에 있고 나머지 판은 `sessionstore-backups` 안에 있습니다. 한쪽만 뜨면 판을 놓칩니다.
- **압축된 채로 검색하지 않습니다.** 압축 파일 안의 주소는 원래 글자 그대로 드러나지 않을 수 있습니다. 키워드 검색 전에 압축을 먼저 풉니다. [파일 내용 검색](../../../03-techniques/analysis/content-search/index.md) 을 참고합니다.
- **옛 판은 압축하지 않은 파일을 씁니다.** 옛 검체에서 `.jsonlz4` 만 찾으면 `.js`·`.bak` 파일을 놓칩니다.
- **갈아 쓴 옛 판을 따로 찾습니다.** 세션 파일은 자주 새로 씁니다. 옛 판은 [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 과 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 로 찾습니다.
- **사생활 보호 창의 흔적은 따로 봅니다.** 사생활 보호 창의 탭이 세션 파일에 남는지 확인하지 못했습니다. [시크릿 모드로 무엇을 했나](../../../04-scenarios/activity/private-browsing.md) 를 참고합니다.

## 직접 분석해 보기

### 헥스로 한 번

- 이번 조사에서 파일 머리의 바이트 배치를 확인하지 못했습니다. 그래서 이 페이지에는 헥스 예시를 싣지 않습니다.
- 헥스 편집기로 각 세션 파일을 열어 머리 몇 바이트를 적어 둡니다. 같은 프로필의 다른 세션 파일과 머리가 같은지 봅니다.
- 압축하지 않은 옛 `.js`·`.bak` 파일은 헥스로 열면 JSON 텍스트가 바로 보입니다. 압축 파일과 옛 파일을 이렇게 가립니다.

### 공개 도구로 한 번

1. 프로필 본 폴더와 `sessionstore-backups` 폴더의 세션 파일을 모두 사본으로 뜹니다. 해시를 기록합니다.
2. 파이어폭스 세션 파일(`.jsonlz4`)을 푸는 공개 도구나 스크립트로 각 파일을 JSON 으로 풉니다.
3. JSON 뷰어로 풀린 파일을 열어 창·탭별 주소와 제목을 찾습니다. 키 이름은 풀린 JSON 에서 직접 확인합니다.
4. 파일마다 뽑은 탭 목록을 나란히 놓습니다. 어느 한 판에만 있는 탭을 표시합니다.
5. 도구가 시각을 보여 주면, 그 시각을 방문 기록의 같은 주소 시각과 맞춰 단위를 확인합니다.

- 도구 두 개로 같은 파일을 풀어 결과를 맞춰 봅니다. [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 참고합니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 방문·다운로드·즐겨찾기 | 탭 주소의 방문 시각과 방문 유형을 봅니다 | [places.sqlite](places-sqlite.md) |
| 캐시 | 탭에 열린 페이지의 자원을 실제로 받았는지 봅니다 | [캐시 (cache2)](cache2.md) |
| 양식 기록 | 같은 시간대에 입력란에 무엇을 쳤는지 봅니다 | [양식 기록 (formhistory.sqlite)](formhistory-sqlite.md) |
| $MFT·$UsnJrnl | 세션 파일을 쓰고 갈아 쓴 시각을 봅니다 | [$MFT](../../filesystem/mft.md), [$UsnJrnl](../../filesystem/usnjrnl.md) |
| 켜짐·꺼짐 | 비정상 종료 짐작을 시스템의 켜짐·꺼짐 기록과 맞춥니다 | [켜짐·꺼짐](../../event-logs/power-on-off-events.md) |
| 크롬 계열 세션 파일 | 같은 시간대에 다른 브라우저로 무엇을 열어 두었는지 봅니다 | [크롬 계열 브라우저](../chrome-edge-whale/index.md) |

웹 사용 전체를 재구성하는 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) 에 있습니다.

## 실습

파이어폭스를 쓴 공개 검체(NIST CFReDS 등)에서 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. 프로필 본 폴더와 `sessionstore-backups` 폴더에 어떤 세션 파일이 있습니까? 업그레이드 백업이 있으면 파일 이름의 빌드 ID 는 무엇입니까?
2. `sessionstore.jsonlz4` 와 `recovery.jsonlz4` 의 $MFT 수정 시각을 비교합니다. 마지막 실행이 정상 종료로 끝났다고 볼 수 있습니까?
3. `sessionstore.jsonlz4` 와 `previous.jsonlz4` 를 풀어 탭 목록을 비교합니다. 한쪽에만 있는 탭은 무엇입니까?
4. 탭 하나의 뒤로 가기 기록을 따라가며 `places.sqlite` 의 방문 기록과 맞춰 봅니다. 방문 기록에 없는 주소가 있습니까?

## 참고 문헌

1. Mozilla, *SessionFile.sys.mjs* (파이어폭스 소스, main 가지 — 세션 파일 이름·위치와 역할, 업그레이드 백업 이름의 빌드 ID, 시작할 때 읽는 순서, 압축, 업그레이드 백업 설정, 탐색 기록 개수 설정). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/browser/components/sessionstore/SessionFile.sys.mjs
