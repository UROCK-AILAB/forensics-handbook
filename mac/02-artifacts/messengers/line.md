---
title: "라인"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1450
---

# 라인 (LINE)

맥 라인 앱이 대화를 어디에 어떤 형식으로 남기는지는 실제 기기에서 확인해야 합니다. 이 페이지는 후보 위치와 확인하는 순서를 정리합니다.

## 무엇을 기록하나 · 왜 생기나

라인은 대화 앱이라 맥에서도 대화·상대·첨부를 로컬에 어떤 식으로든 남길 것으로 보이고, 대화 DB의 이름, 암호화 여부, 표 구조는 컨테이너 안의 파일을 열어 확인합니다. ForensicArtifacts 의 메신저 정의 파일(`instant_messaging.yaml`)에는 라인 항목이 없습니다 [1]. 공개 수집 정의에 기대는 도구로는 라인 폴더가 수집 대상에서 빠질 수 있어서, 조사 대상에 라인이 있으면 수집 범위를 따로 정합니다.

알려진 사실이 적어서, 아래 절은 "무엇을 찾아야 하는지"와 "찾은 것을 어떻게 판단하는지"에 맞춰 씁니다. 저장 형식 설명은 기반 구조 페이지로 넘깁니다.

## 위치와 버전별 차이

아래 값은 후보라서 실제 기기에서 확인해야 합니다.

| 항목 | 후보 값 | 확인 정도 |
|---|---|---|
| 앱 번들 ID | `jp.naver.line.mac` | 실제 기기에서 확인 |
| 앱 컨테이너 | `~/Library/Containers/jp.naver.line.mac/` | 실제 기기에서 확인 |
| 대화 DB 이름·형식 | 알려진 후보 없음 | 실제 기기에서 확인 |

후보 번들 ID가 맞는지는 설치된 앱의 `Info.plist` 에서 먼저 확인하고, 방법은 [앱 번들 정보 (Info.plist·Code Signature)](../embedded-metadata/app-bundle.md)와 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)를 따릅니다. 번들 ID를 확인하면 같은 이름의 컨테이너 폴더와 그룹 컨테이너 폴더를 찾아볼 수 있습니다. macOS 10.15 Catalina 이후 맥 버전이나 라인 앱 버전이 다른 기기에서는 같은 방법으로 위치를 다시 확인합니다.

## 구조

대화 DB의 구조는 실제 파일로 확인합니다. 컨테이너 안에서 찾은 파일은 앞부분 바이트로 형식을 가르고, SQLite 이면 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md), 속성 목록이면 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md), LevelDB 이면 [LevelDB와 IndexedDB (LevelDB·IndexedDB)](../../01-foundations/data-formats/leveldb-indexeddb.md)의 방법으로 읽습니다. 어느 형식에도 맞지 않으면 암호화됐거나 압축됐을 수 있으니 [암호화된 증거 다루기 (Encrypted Evidence)](../../03-techniques/analysis/encrypted-evidence/index.md)의 판단 기준을 따릅니다.

> 그림 자리: 후보 컨테이너 안에서 찾은 파일을 앞부분 바이트로 SQLite·plist·LevelDB·알 수 없음으로 가르는 판단 흐름도

## 증거로서 의미

**증명하는 것.** 분석 대상에서 라인 컨테이너를 찾으면 그 계정에서 라인을 설치하고 실행한 정황이 되고, 그 안에서 읽을 수 있는 대화 기록을 찾으면 그 계정의 라인 앱이 그 내용을 로컬에 저장했다는 기록이 됩니다.

**증명하지 못하는 것.** 파일을 열지 못하면 대화 상대·내용·시각은 말할 수 없고, 파일이 바뀐 시각은 앱이 파일에 쓴 때일 뿐 특정 메시지를 보낸 때가 아닙니다. 맥에 남은 기록이 다른 기기에서 넘어온 것인지도 이 기록만으로는 가를 수 없습니다. 보고서에는 "라인으로 대화했다" 보다 "이 계정에 라인 컨테이너와 이런 파일이 있고, 마지막으로 바뀐 시각은 이렇다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

라인 파일 안의 시각 필드와 기준은 실제 파일에서 확인합니다. 읽을 수 있는 파일에서 시각으로 보이는 값을 찾으면 자릿수를 보고 유닉스 시각(초·밀리초)인지 맥 절대 시각인지 가르고, 기준끼리의 관계는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다. 현지 시각으로 옮길 때는 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)에서 확인한 시간대를 적용합니다.

## 함정과 한계

- **후보 값을 사실처럼 쓰는 경우.** 이 페이지의 번들 ID와 경로는 후보라서, 보고서에는 실제 기기에서 확인한 값만 씁니다.
- **수집 정의에 빠져 있는 경우.** ForensicArtifacts 메신저 정의에 라인이 없어서 [1], 정의만 믿고 수집하면 라인 컨테이너가 빠질 수 있습니다.
- **컨테이너만 보는 경우.** 앱에 따라 데이터를 `Containers` 가 아닌 `Group Containers` 나 `Application Support` 에 두기도 해서, 번들 ID로 찾을 수 있는 폴더를 모두 봅니다.
- **지우기와 조작.** 대화를 지웠거나 앱을 지운 정황은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)의 방법으로 판단합니다.

## 직접 분석해 보기

원본을 바로 열지 않고, 찾은 라인 폴더 전체를 작업 폴더로 복사한 뒤 사본에서 봅니다.

### 헥스로 한 번

컨테이너 안의 큰 파일부터 헥스 편집기로 열어 첫 줄을 봅니다. SQLite 파일 머리나 속성 목록 머리처럼 알려진 모양이 보이면 해당 기반 구조 페이지의 방법으로 넘어가고, 뜻을 알 수 없는 바이트가 처음부터 이어지면 암호화됐거나 압축됐을 수 있다고 적어 둡니다. 각 형식의 머리 모양은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)와 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에 있습니다.

### 공개 도구로 한 번

형식을 확인한 파일만 공개 도구로 엽니다. SQLite 는 `sqlite3` 명령줄 도구나 DB Browser for SQLite 로 열어 표 목록부터 보고, 속성 목록은 맥의 `plutil -p` 로 사람이 읽을 수 있게 풀어 봅니다.

```sql
-- 표 이름과 만든 문장을 먼저 본다
SELECT name, sql FROM sqlite_master WHERE type = 'table';
```

표 이름과 열 이름을 확인하기 전에는 열의 뜻을 추측으로 채우지 않고, 추측한 부분은 보고서에 추측이라고 적습니다.

## 교차 검증

- [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) — 라인이 설치돼 있었는지, 언제 들어왔는지 봅니다.
- [KnowledgeC (knowledgeC.db)](../execution/knowledgec/index.md), [바이옴 (Biome)](../execution/biome/index.md) — 앱을 쓴 시간대를 봅니다.
- [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) — 라인 폴더의 파일이 언제 바뀌었는지 봅니다.
- [앱별 네트워크 사용량 (netusage)](../network/netusage.md) — 그 시간대에 앱이 통신한 양을 봅니다.
- [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md) — 이 기록을 쓰는 조사 흐름입니다.

## 실습

NIST CFReDS 같은 공개 시험 이미지 가운데 라인을 쓴 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 설치된 라인 앱의 `Info.plist` 에 적힌 번들 ID는 무엇이고, 이 페이지의 후보와 같나요?
2. 그 번들 ID로 찾을 수 있는 폴더를 `Containers`, `Group Containers`, `Application Support` 에서 모두 찾아 목록으로 만들어 보세요.
3. 찾은 파일 가운데 대화가 들어 있을 만한 파일은 무엇이고, 앞부분 바이트로 본 형식은 무엇인가요?
4. 그 파일이 마지막으로 바뀐 시각과 앱 사용 기록의 시간대가 맞나요?

## 참고 문헌

1. ForensicArtifacts, instant_messaging.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/instant_messaging.yaml
