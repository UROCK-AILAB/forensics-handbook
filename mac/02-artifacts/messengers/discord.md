---
title: "디스코드"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1430
---

# 디스코드 (Discord)

맥 디스코드 앱이 로컬에 무엇을 어디에 남기는지는 널리 알려진 후보 위치를 실제 데이터에서 하나씩 열어 확인합니다.

## 무엇을 기록하나 · 왜 생기나

디스코드는 대화 본문을 서버에 두고, 맥 쪽에는 앱이 화면을 그리려고 받아 둔 캐시(API 응답 JSON, 첨부 이미지)에만 대화가 조각으로 남는다는 설명이 널리 퍼져 있습니다. 이 설명을 보고서에 옮기기 전에 분석 대상에 실제로 어떤 파일이 있는지부터 봅니다.

디스코드 데스크톱이 일렉트론 (Electron) 앱이라면 크로미움 (Chromium) 기반이라서 캐시·Local Storage·Cookies 같은 크로미움 파일 구조를 그대로 쓸 가능성이 있습니다. 일렉트론 앱인지부터 실제 데이터로 확인합니다. 일렉트론 앱이 맥에서 암호화 키를 어디에 두는지는 [시그널 (Signal)](signal.md) 페이지에 있습니다.

공개 아티팩트 정의 모음인 ForensicArtifacts 의 메신저 정의 파일(`instant_messaging.yaml`)에는 디스코드 항목이 없습니다 [1]. 이 정의를 그대로 쓰는 수집 도구로는 디스코드 폴더가 수집 대상에 들어가지 않을 수 있어서, 수집 범위를 정할 때 따로 챙겨야 합니다.

## 위치와 버전별 차이

아래 경로는 모두 후보 위치라서, 분석 대상에 실제로 있는지 하나씩 확인합니다.

| 기록 | 후보 위치 | 확인 정도 |
|---|---|---|
| 사용자 데이터 폴더 | `~/Library/Application Support/discord/` | 실제 데이터로 확인 |
| 웹 캐시 | 위 폴더 아래 `Cache/Cache_Data/` | 실제 데이터로 확인 |
| Local Storage | 위 폴더 아래 `Local Storage/leveldb/` | 실제 데이터로 확인 |
| IndexedDB | 위 폴더 아래 `IndexedDB/` | 실제 데이터로 확인 |
| 쿠키 | 위 폴더 아래 `Cookies` | 실제 데이터로 확인 |
| 앱 설정 | 위 폴더 아래 `settings.json` | 실제 데이터로 확인 |
| 시험판 채널 폴더 | `discordptb`, `discordcanary` 라는 이름의 폴더 | 실제 데이터로 확인 |

시험판 채널이 따로 폴더를 쓴다면 한 계정에 디스코드 데이터 묶음이 여러 개 있을 수 있어서, 이름에 `discord` 가 들어간 폴더를 모두 찾아봅니다. macOS 10.15 Catalina 이후 맥 버전이나 디스코드 앱 버전에 따라 위치가 바뀌는지는 분석 대상마다 확인합니다.

## 구조

후보 폴더의 파일이 실제로 크로미움 구조라면 각 형식은 기반 구조 페이지의 설명을 따릅니다. `Local Storage/leveldb/` 와 `IndexedDB/` 는 [LevelDB와 IndexedDB (LevelDB·IndexedDB)](../../01-foundations/data-formats/leveldb-indexeddb.md)에서, `Cookies` 같은 SQLite 파일은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서, 캐시 폴더는 [크롬·엣지·웨일 (Chromium 계열)](../browsers/chromium/index.md)에서 다룹니다. 디스코드가 이 파일들 안에 어떤 키 이름과 값으로 대화·계정 정보를 적는지는 실제 데이터로 확인해야 합니다.

> 그림 자리: 후보 사용자 데이터 폴더 아래 캐시·Local Storage·IndexedDB·Cookies·settings.json 이 놓인 모양과, 각각을 설명하는 기반 구조 페이지를 잇는 길잡이 그림

## 증거로서 의미

**증명하는 것.** 분석 대상에서 디스코드 폴더를 찾고 그 안의 캐시 항목에 대화나 첨부 이미지가 들어 있다면, 그 계정의 디스코드 앱이 그 내용을 한 번은 받아 화면에 쓰려 했다는 정황이 됩니다. 폴더가 있다는 사실만으로도 그 계정에서 디스코드를 실행한 적이 있다는 정황이 되지만, 폴더를 누가 언제 만들었는지는 파일 시스템 기록과 함께 봐야 합니다.

**증명하지 못하는 것.** 캐시는 앱이 받아 둔 조각이라서 대화 전체가 아니고, 캐시에 없는 대화가 없었다는 뜻도 아닙니다. 캐시에 남은 메시지를 사용자가 직접 보냈는지, 받기만 했는지, 화면에서 읽었는지도 캐시 파일만으로는 말할 수 없습니다. 보고서에는 "디스코드로 대화했다" 보다 "이 계정의 디스코드 후보 폴더 캐시에 이런 내용의 항목이 남아 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

크로미움 캐시는 보통 1601-01-01 기준 마이크로초 시각을 쓰지만, 디스코드 캐시가 같은 기준을 쓰는지는 캐시 항목의 시각을 같은 파일의 파일 시스템 시각과 맞춰 보고 확인합니다. 캐시 형식과 시각은 [크롬·엣지·웨일 (Chromium 계열)](../browsers/chromium/index.md)의 설명을 따르고, 캐시 안의 API 응답 JSON에 들어 있는 시각 문자열이나 숫자는 기준을 따로 확인합니다. 기준끼리의 관계는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에 정리돼 있습니다.

캐시 항목의 시각은 앱이 그 응답을 받아 저장한 때에 가까울 뿐, 메시지를 보낸 때와 같다는 보장이 없습니다. 메시지를 보낸 시각은 캐시에 남은 응답 본문 안에 따로 적혀 있을 수 있으니, 두 시각을 섞지 않고 필드마다 뜻을 적어 둡니다.

## 함정과 한계

- **후보 경로를 사실처럼 쓰는 경우.** 위 경로는 모두 후보라서, 보고서에는 분석 대상에서 실제로 찾은 경로만 씁니다.
- **수집 정의에 빠져 있는 경우.** ForensicArtifacts 메신저 정의에 디스코드가 없어서 [1], 정의만 믿고 수집하면 디스코드 폴더가 통째로 빠질 수 있습니다.
- **시험판 채널 폴더를 놓치는 경우.** 이름이 다른 폴더를 쓰는 채널이 있다면, 한 폴더만 보고 결론을 내면 다른 묶음을 놓칩니다.
- **캐시의 한계.** 캐시는 일반적으로 앱이 비우고 다시 채우는 곳이라 오래된 대화는 남아 있지 않을 수 있습니다. 지운 캐시 파일을 되살리는 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)를 봅니다.
- **지우기와 조작.** 앱을 지우거나 폴더를 비운 정황은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)의 방법으로 다른 기록과 맞춰 판단합니다.

## 직접 분석해 보기

원본을 바로 열지 않고 후보 폴더 전체를 작업 폴더로 복사한 뒤 사본에서 봅니다.

### 헥스로 한 번

후보 폴더의 파일이 실제로 어떤 형식인지는 확장자가 아니라 파일 앞부분의 바이트로 판별합니다. 헥스 편집기로 `Cookies` 후보 파일의 첫 줄을 열어 SQLite 파일 머리인지 보고, `Local Storage/leveldb/` 안의 파일은 LevelDB 로그·테이블 파일 모양인지 봅니다. 각 형식의 머리 모양과 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)와 [LevelDB와 IndexedDB (LevelDB·IndexedDB)](../../01-foundations/data-formats/leveldb-indexeddb.md)를 따르고, 형식을 확인한 파일만 해당 도구로 엽니다. 형식이 어느 쪽에도 맞지 않으면 압축됐거나 암호화됐을 수 있으니 [압축 형식 (LZFSE·LZ4·zlib)](../../01-foundations/value-decoding/compression.md)과 [암호화된 증거 다루기 (Encrypted Evidence)](../../03-techniques/analysis/encrypted-evidence/index.md)를 봅니다.

### 공개 도구로 한 번

형식을 확인한 파일은 공개 도구로 엽니다. SQLite 파일은 `sqlite3` 명령줄 도구나 DB Browser for SQLite 로, LevelDB 폴더는 LevelDB를 읽는 공개 파서로 열고, 캐시 폴더는 크로미움 캐시를 읽는 공개 도구로 항목과 URL을 뽑습니다. 캐시에서 뽑은 JSON 응답은 텍스트로 저장해 두고 [콘텐츠 검색 (Content Search)](../../03-techniques/analysis/content-search.md)의 방법으로 사건 관련 낱말을 찾습니다.

## 교차 검증

- [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) — 디스코드 앱이 설치돼 있었는지, 언제 들어왔는지 봅니다.
- [KnowledgeC (knowledgeC.db)](../execution/knowledgec/index.md), [바이옴 (Biome)](../execution/biome/index.md) — 앱을 쓴 시간대를 따로 확인합니다.
- [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) — 후보 폴더의 파일이 언제 만들어지고 바뀌었는지 봅니다.
- [앱별 네트워크 사용량 (netusage)](../network/netusage.md) — 그 시간대에 앱이 통신한 양을 봅니다.
- [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) — 디스코드로 받은 파일에 다운로드 기록이 붙었는지 봅니다.
- [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md) — 이 기록을 쓰는 조사 흐름입니다.

## 실습

NIST CFReDS 같은 공개 시험 이미지 가운데 디스코드를 쓴 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 사용자 홈의 `Library/Application Support` 아래 이름에 `discord` 가 들어간 폴더가 있나요? 몇 개인가요?
2. 찾은 폴더 아래 파일마다 앞부분 바이트를 보고 SQLite·LevelDB·그 밖의 형식으로 나눠 보세요. 이 페이지의 후보 목록과 다른 점은 무엇인가요?
3. 캐시에서 대화 내용이 담긴 JSON 응답을 찾을 수 있나요? 찾았다면 응답 안의 시각 값과 캐시 항목의 시각이 서로 얼마나 떨어져 있나요?
4. 폴더가 처음 생긴 시각과 앱 설치 기록의 시각을 맞춰 보세요.

## 참고 문헌

1. ForensicArtifacts, instant_messaging.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/instant_messaging.yaml
