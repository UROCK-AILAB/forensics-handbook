---
title: "라인"
parent: "아티팩트 · 메신저"
nav_order: 860
---

# 라인 (LINE)

라인 iOS 앱은 메시지 DB `Line.sqlite` 를 앱 그룹 컨테이너에, 첨부 파일과 첨부 정보 DB 를 앱 자체 데이터 컨테이너의 계정별 폴더에 두고, 첨부 파일 이름이 "메시지 ID + 확장자" 라서 파일만 보고도 메시지와 이을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

라인은 대화 목록과 메시지를 기기에 저장해 두고, 주고받은 사진·파일은 계정별 저장소 폴더에 따로 받아 둡니다. 메시지 DB 에는 메시지 본문·보낸 사람·시각·메시지 ID 와 대화 상대 이름이 남고, 첨부 정보 DB 에는 메시지 ID 와 파일 이름의 짝이 남습니다 [1].

## 위치와 버전별 차이

아래 이름은 공개 도구 iLEAPP 가 전체 파일 시스템 추출에서 찾는 것입니다 [1]. 앱 그룹과 앱 데이터 컨테이너의 차이는 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에서 다룹니다.

| 위치 | 파일 | 내용 |
|---|---|---|
| 앱 그룹 컨테이너 | `Line.sqlite` | 메시지와 사용자 [1] |
| 앱 데이터 컨테이너 | `Library/Application Support/PrivateStore/P_*/Messages/MessageAttachmentInfo.sqlite` | 메시지 ID 와 첨부 파일 이름 [1] |
| 앱 데이터 컨테이너 | `Library/Application Support/PrivateStore/P_*/Message Attachments/` | 첨부 파일 [1] |

`PrivateStore` 아래에는 계정마다 `P_` 로 시작하는 폴더가 따로 있습니다 [1]. `Line.sqlite` 는 한 기기에 여러 개 있을 수 있어서, 처음 찾은 파일 하나만 읽지 말고 모두 찾아 읽습니다 [1].

iLEAPP 시험 표본에서 앱 그룹 이름은 `group.com.linecorp.line` 이었습니다(iOS 13.3.1·14.3·15.3.1·17.3 표본) [1]. 번들 ID 와 로컬 백업의 도메인 이름은 이번 자료로 확인하지 못했습니다. 로컬 백업에서는 앱 그룹 공유 폴더가 `AppDomainGroup-` 으로 시작하는 도메인으로 따로 나뉘어 있었지만(확인 범위: iOS 27.0), 관찰한 백업은 다른 회사 앱의 도메인 이름을 가려 두어 라인 파일이 들어가는지는 확인하지 못했습니다([로컬 백업](../../01-foundations/backups/local-backup/index.md)). 라인 자체의 iCloud 대화 백업 형식도 확인하지 못했습니다.

| 항목 | 확인된 범위 |
|---|---|
| 앱 그룹 이름이 확인된 표본 | iOS 13.3.1, 14.3, 15.3.1, 17.3 [1] |
| 버전별 구조 차이 | 확인하지 못함 |

## 구조

`Line.sqlite` 에서 도구가 읽는 표와 칸은 다음과 같습니다 [1].

| 표 | 칸 |
|---|---|
| `ZMESSAGE` | `ZTIMESTAMP`, `ZSENDER`, `ZTEXT`, `ZID` |
| `ZUSER` | `Z_PK`, `ZNAME` |

`ZSENDER` 로 `ZUSER` 의 이름을 찾아 보낸 사람을 붙입니다. `ZSENDER` 가 비어 있으면 보낸 메시지로 보는데, 이 규칙은 iLEAPP 가 시험으로 정한 것입니다 [1]. 로그인한 계정 자신의 `ZUSER` 행은 시험 표본 어디에도 없었습니다 [1].

`MessageAttachmentInfo.sqlite` 의 `ZMESSAGEATTACHMENTINFO` 표에는 `ZMESSAGEID` 와 `ZFILENAME` 칸이 있습니다 [1]. `Message Attachments/` 아래 파일 이름이 "메시지 ID + 확장자" 이므로, 첨부 정보 DB 가 없어도 파일 이름에서 확장자를 떼면 `ZMESSAGE.ZID` 와 맞춰 볼 수 있습니다 [1].

사진을 보낸 메시지에는 본문 칸에 앱이 쓴 "사진을 보냈다" 는 뜻의 문구가 남아 있었습니다(시험 표본 10건 모두) [1]. 본문만 보면 사람이 쓴 문장처럼 보이니, 첨부 파일과 함께 확인합니다.

저장 형식은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에 있습니다.

## 증거로서 의미

**증명하는 것.** `ZMESSAGE` 행은 이 기기의 라인 데이터에 그 시각의 메시지가 남아 있다는 기록입니다 [1]. 첨부 파일이 계정별 `P_` 폴더 아래에 있으면 어느 계정의 대화에서 받거나 보낸 파일인지 폴더로 알 수 있고, 파일 이름의 메시지 ID 로 어느 메시지에 딸린 것인지도 알 수 있습니다 [1].

**증명하지 못하는 것.** "보낸 메시지" 판단은 `ZSENDER` 가 비었다는 사실에 기댄 시험 규칙이라서, 보고서에는 판단 근거를 함께 적습니다 [1]. 본문에 남은 "사진을 보냈다" 문구는 앱이 쓴 것이라서 사용자가 그 문장을 입력했다는 뜻이 아닙니다 [1]. `ZUSER` 에 이름이 있어도 그 사람과 대화했다는 뜻은 아니고, 메시지가 한 건이라도 있는지 따로 확인합니다.

## 시각 해석

`ZTIMESTAMP` 는 Unix 밀리초라서 1000 으로 나눈 뒤 Unix 초로 바꾸고, 결과는 UTC 입니다 [1]. 이 값이 메시지를 보낸 시각인지, 기기가 받은 시각인지는 이번 자료로 확인하지 못했습니다. 변환 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

## 함정과 한계

`Line.sqlite` 가 여러 개일 수 있는데 하나만 읽으면 대화 일부가 빠집니다 [1]. 찾은 파일마다 경로와 행 수를 적어 두고 어느 파일에서 나온 메시지인지 보고서에 남깁니다.

메시지 DB 와 첨부 파일이 서로 다른 컨테이너에 있어서 [1], 앱 그룹 컨테이너만 추출하면 첨부가 빠지고 앱 데이터 컨테이너만 추출하면 메시지가 빠집니다. 수집 범위를 먼저 확인합니다([모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md)).

iLEAPP 에는 `linePrivateStore.py` 라는 분석기도 따로 있지만 이번에 내용을 확인하지 못했습니다. 지운 메시지는 SQLite 파일의 빈 공간을 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 방법으로 따로 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래는 명세로 만든 예시이고 실제 검체에서 나온 값이 아닙니다. `ZTIMESTAMP` 에 정수 1,700,000,000,000 이 들어 있다면, SQLite 는 이 크기의 정수를 6바이트 빅엔디언(직렬 형식 5)으로 저장하므로 레코드 안에서 다음 바이트로 보입니다.

```
01 8B CF E5 68 00
```

1000 으로 나누면 Unix 1,700,000,000 초이고, UTC 2023-11-14 22:13:20 입니다. 밀리초 값을 그대로 초로 넣으면 먼 미래 날짜가 나오므로, 연도가 크게 튀면 단위부터 의심합니다.

**공개 도구로 한 번.** iLEAPP 의 라인 분석기로 보고서를 만들고 [1], 같은 DB 를 SQLite 뷰어로 열어 다음 질의 결과와 맞춰 봅니다.

```sql
SELECT datetime(m.ZTIMESTAMP / 1000, 'unixepoch') AS utc,
       m.ZID, u.ZNAME, m.ZTEXT
FROM ZMESSAGE m LEFT JOIN ZUSER u ON m.ZSENDER = u.Z_PK
ORDER BY m.ZTIMESTAMP;
```

도구가 "보낸 메시지" 로 분류하는 행은 `m.ZSENDER` 가 비어 있는 행입니다. `u.ZNAME` 은 `ZSENDER` 가 가리키는 `ZUSER` 행이 없을 때도 비므로, 이름 칸만 보고 나누지 않습니다.

## 교차 검증

- [알림 기록](../app-usage/notifications.md) — 받은 메시지가 알림으로도 남았는지 봅니다.
- [KnowledgeC](../app-usage/knowledgec/index.md), [바이옴](../app-usage/biome/index.md) — 메시지 시각에 앱을 쓰고 있었는지 봅니다.
- [사진 보관함](../media/photos/index.md), [카메라 사진과 메타데이터](../media/dcim-exif.md) — 보낸 사진이 기기에서 찍은 것인지 봅니다.
- [앱별 데이터 사용량](../network/data-usage.md) — 같은 시간대 앱의 송수신량을 봅니다.
- [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md)

## 실습

공개 검체(NIST CFReDS 등) 가운데 라인이 설치된 iOS 전체 파일 시스템 이미지를 골라 풀어 봅니다.

1. 이미지 안에 `Line.sqlite` 는 몇 개이고, 각각 어느 경로에 있습니까?
2. `PrivateStore` 아래 `P_` 폴더는 몇 개입니까?
3. `Message Attachments/` 의 파일 이름에서 메시지 ID 를 떼어 `ZMESSAGE.ZID` 와 맞춰 보고, 짝이 없는 파일이 있는지 확인하십시오.
4. `ZSENDER` 가 비어 있는 메시지 가운데 첨부가 있는 것의 시각을 UTC 로 적어 보십시오.

## 참고 문헌

1. iLEAPP, scripts/artifacts/line.py — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/line.py
