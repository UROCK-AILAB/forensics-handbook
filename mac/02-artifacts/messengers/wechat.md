---
title: "위챗"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1440
---

# 위챗 (WeChat)

맥 위챗은 대화를 로컬 DB 파일에 남긴다고 알려져 있지만 경로와 파일 이름은 이 페이지를 쓸 때 연 자료로 확인하지 못했고, 확인한 사실은 위챗 4.0 전후로 DB 구조가 바뀌었다는 정황과 공개 수집 정의에 위챗이 빠져 있다는 점뿐입니다.

## 무엇을 기록하나 · 왜 생기나

맥 위챗 앱은 대화와 연락처를 로컬 DB에 저장한다고 흔히 설명합니다. 이 설명과 아래 후보 경로는 이 페이지의 출처로 확인하지 못했으므로, 보고서에는 검체에서 실제로 찾은 파일만 씁니다.

확인한 사실은 두 가지입니다. 먼저 맥 arm64용 위챗 4.1의 DB를 다루는 공개 저장소가 있고, 그 저장소는 위챗 4.1.2.241 에서만 시험했으며 4.0 미만은 지원하지 않는다고 적어 두었습니다 [1]. 4.0 을 경계로 지원 여부를 나눈 것이라, 위챗이 4.0 전후로 DB 구조를 바꿨다는 정황으로 읽을 수 있습니다. 구체적으로 무엇이 달라졌는지는 확인하지 못했고, 그 저장소의 README 는 지금 본문이 지워지고 한 줄 문구만 남아 있습니다 [2]. 다음으로 ForensicArtifacts 의 메신저 정의 파일(`instant_messaging.yaml`)에는 위챗 항목이 없습니다 [3].

위 저장소의 제목에 "数据库解密(DB 복호화)"라는 말이 들어 있어서 DB가 암호화돼 있다고 짐작할 수 있지만 [1], 흔히 말하는 SQLCipher 방식인지를 비롯해 암호 방식은 확인하지 못했습니다. 이 핸드북은 암호를 푸는 절차를 다루지 않고, 암호화된 증거를 만났을 때의 판단은 [암호화된 증거 다루기 (Encrypted Evidence)](../../03-techniques/analysis/encrypted-evidence/index.md)를 따릅니다.

## 위치와 버전별 차이

아래 경로는 모두 조사 과정에서 후보로만 떠올린 값이고, 이 페이지의 출처로 확인하지 못했습니다.

| 기록 | 후보 위치 | 확인 정도 |
|---|---|---|
| 앱 컨테이너 | `~/Library/Containers/com.tencent.xinWeChat/` | 확인되지 않음 |
| 3.x 계열 대화 DB | 컨테이너 아래 `Data/Library/Application Support/com.tencent.xinWeChat/<버전 문자열>/<계정 해시>/Message/msg_*.db` | 확인되지 않음 |
| 4.x 계열 DB 폴더 | 컨테이너 아래 `Data/Documents/xwechat_files/<계정 폴더>/db_storage/` | 확인되지 않음 |

앱 버전에 따른 차이는 아래처럼 정리됩니다. macOS 10.15 Catalina 이후 맥 버전에 따라 위치가 바뀐다는 자료는 찾지 못했습니다.

| 위챗 버전 | 알려진 점 |
|---|---|
| 4.0 미만 | 공개 저장소가 지원하지 않는다고 적음 [1]. 3.x 계열 DB 위치는 위 표의 후보(확인되지 않음) |
| 4.0 이상 | 공개 저장소가 4.1.2.241 에서 시험했다고 적음 [1]. 4.x 계열 DB 위치는 위 표의 후보(확인되지 않음) |

후보 경로가 맞다면 버전 폴더나 계정 폴더 이름이 검체마다 달라서, 한 계정에서 위챗 계정을 여러 개 썼다면 계정 폴더도 여러 개일 수 있습니다. 앱 컨테이너와 번들 ID를 확인하는 방법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)를 봅니다.

## 구조

DB 파일의 표·칸 구조는 이번에 확인하지 못했습니다. 후보 DB 파일이 평문 SQLite 인지 암호화된 파일인지를 먼저 가르고, 평문이면 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)의 방법으로 표 목록부터 봅니다. 암호화돼 있으면 표 구조를 볼 수 없으니, DB 파일의 존재·크기·시각 같은 파일 시스템 수준의 기록만 증거로 씁니다.

> 그림 자리: 위챗 3.x 후보 경로와 4.x 후보 경로를 나란히 놓고, 컨테이너 아래에서 갈라지는 모양을 보여 주는 그림(두 경로 모두 확인되지 않음 표시)

## 증거로서 의미

**증명하는 것.** 검체에서 위챗 컨테이너와 DB 파일을 찾으면 그 계정에서 위챗을 설치하고 실행한 정황이 됩니다. DB 파일이 여러 계정 폴더에 나뉘어 있다면 위챗 계정을 여러 개 썼다는 정황이 되고, 버전 폴더 이름이 남아 있다면 어느 계열의 위챗을 썼는지 가늠하는 데 씁니다.

**증명하지 못하는 것.** DB를 열지 못하면 대화 상대·내용·시각은 말할 수 없고, DB 파일이 바뀐 시각은 앱이 파일에 쓴 때일 뿐 특정 메시지를 보낸 때가 아닙니다. 맥 DB에 있는 기록이 맥에서 쓴 것인지 다른 기기에서 넘어온 것인지도 이 페이지의 출처로는 가를 수 없고, 그런 구분이 DB 안에 남는지는 확인하지 못했습니다. 보고서에는 "위챗으로 대화했다" 보다 "이 계정에 위챗 컨테이너와 이 크기의 DB 파일이 있고, 마지막으로 바뀐 시각은 이렇다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

DB 안의 시각 칸 이름과 기준은 확인하지 못했습니다. 표를 열 수 있게 되면 시각으로 보이는 칸마다 자릿수를 보고 유닉스 시각(초·밀리초)인지 맥 절대 시각인지 가르고, 기준끼리의 관계는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다. DB 파일의 생성·수정 시각은 [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md)의 설명대로 읽고, 현지 시각으로 옮길 때는 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)에서 확인한 시간대를 적용합니다.

## 함정과 한계

- **후보 경로를 사실처럼 쓰는 경우.** 이 페이지의 경로는 모두 확인되지 않은 후보라서, 보고서에는 검체에서 실제로 찾은 경로만 씁니다.
- **버전을 섞는 경우.** 4.0 전후로 DB 구조가 바뀐 정황이 있어서 [1], 3.x 에 맞춘 분석 방법을 4.x 검체에 그대로 쓰면 파일을 못 찾거나 잘못 읽을 수 있습니다. 앱 버전은 [앱 번들 정보 (Info.plist·Code Signature)](../embedded-metadata/app-bundle.md)의 방법으로 먼저 확인합니다.
- **수집 정의에 빠져 있는 경우.** ForensicArtifacts 메신저 정의에 위챗이 없어서 [3], 정의만 믿고 수집하면 위챗 컨테이너가 빠질 수 있습니다.
- **공개 도구가 사라지는 경우.** 위챗 DB를 다루던 공개 저장소의 README 본문이 지워진 것처럼 [2], 특정 버전에 맞춘 공개 도구는 예고 없이 바뀌거나 사라집니다. 도구 결과는 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)의 방법으로 확인하고 씁니다.
- **지우기와 조작.** 대화를 지웠거나 앱을 지운 정황은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)의 방법으로 판단합니다.

## 직접 분석해 보기

원본을 바로 열지 않고 후보 컨테이너 폴더 전체를 작업 폴더로 복사한 뒤 사본에서 봅니다.

### 헥스로 한 번

후보 DB 파일을 헥스 편집기로 열어 첫 줄이 SQLite 파일 머리인지 봅니다. 머리 모양은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에 있고, 그 모양이 보이면 평문 SQLite 이고 첫 바이트부터 뜻을 알 수 없는 바이트가 이어지면 파일이 암호화됐거나 다른 형식일 수 있습니다. 같은 폴더에 짝 파일(`-wal`, `-shm` 으로 끝나는 파일)이 있는지도 함께 적어 둡니다. 암호화된 파일이라면 여기서 멈추고 파일 크기·시각·해시만 기록합니다.

### 공개 도구로 한 번

평문 SQLite 로 확인된 파일은 `sqlite3` 명령줄 도구나 DB Browser for SQLite 같은 공개 도구로 사본을 열고, 표 목록부터 봅니다.

```sql
-- 표 이름과 만든 문장을 먼저 본다
SELECT name, sql FROM sqlite_master WHERE type = 'table';
```

표 이름과 칸 이름을 확인한 뒤 시각으로 보이는 칸의 자릿수를 보고 기준을 정합니다. 확인되지 않은 칸 뜻을 추측으로 채우지 않고, 추측한 부분은 보고서에 추측이라고 적습니다.

## 교차 검증

- [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) — 위챗이 설치돼 있었는지, 언제 들어왔는지 봅니다.
- [앱 번들 정보 (Info.plist·Code Signature)](../embedded-metadata/app-bundle.md) — 설치된 위챗의 버전과 번들 ID를 봅니다.
- [KnowledgeC (knowledgeC.db)](../execution/knowledgec/index.md), [바이옴 (Biome)](../execution/biome/index.md) — 앱을 쓴 시간대를 봅니다.
- [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) — DB 파일이 언제 바뀌었는지 봅니다.
- [아이폰·아이패드 연결 (iOS Devices)](../external-devices/ios-devices/index.md) — 휴대폰 쪽 기록과 맞춰 볼 때 씁니다.
- [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md) — 이 기록을 쓰는 조사 흐름입니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 위챗을 쓴 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 사용자 홈의 `Library/Containers` 아래 위챗 컨테이너가 있나요? 폴더 이름은 무엇인가요?
2. 설치된 위챗의 버전은 4.0 이상인가요, 미만인가요? 이 페이지의 3.x·4.x 후보 경로 가운데 어느 쪽과 맞나요?
3. 찾은 DB 파일은 평문 SQLite 인가요, 암호화된 파일인가요? 앞부분 바이트로 판단한 근거를 적어 보세요.
4. DB 파일이 마지막으로 바뀐 시각을 UTC 와 현지 시각으로 적고, 같은 시각 무렵 앱 사용 기록이 있는지 맞춰 보세요.

## 참고 문헌

1. Thearas/wechat-db-decrypt-macos 저장소 첫 화면 — https://github.com/Thearas/wechat-db-decrypt-macos
2. Thearas/wechat-db-decrypt-macos README 원문 — https://raw.githubusercontent.com/Thearas/wechat-db-decrypt-macos/main/README.md
3. ForensicArtifacts, instant_messaging.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/instant_messaging.yaml
