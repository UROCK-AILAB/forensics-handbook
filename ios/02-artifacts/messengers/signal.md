---
title: "시그널"
parent: "아티팩트 · 메신저"
nav_order: 870
---

# 시그널 (Signal)

시그널 iOS 앱은 메시지 DB `signal.sqlite` 를 SQLCipher 로 암호화해 앱 그룹 공유 폴더에 두고 키는 iOS 키체인에 보관하지만, 첨부 파일은 같은 공유 폴더의 `Attachments/` 에 평문으로 둡니다.

## 무엇을 기록하나 · 왜 생기나

시그널은 대화·상대·첨부 정보를 기기 안 DB 에 저장하고, 이 DB 를 통째로 암호화합니다 [1]. DB 에는 메시지 본문과 시각 여러 개, 보낸 사람 번호와 UUID, 읽음 여부와 함께, 사라지는 메시지 타이머·한 번 보기·상대가 모두에게서 삭제한 표시까지 남습니다 [1].

## 위치와 버전별 차이

아래 이름은 공개 도구 iLEAPP 가 전체 파일 시스템 추출에서 찾는 것이고, 모두 앱 그룹 공유 폴더 아래에 있습니다 [1]. 앱 그룹 개념은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 을 봅니다.

| 경로 | 내용 |
|---|---|
| `grdb*/signal.sqlite` | 메시지 DB(SQLCipher 암호화) [1] |
| `Attachments/` | 첨부 파일(평문) [1] |

DB 를 여는 키는 iOS 키체인에 있습니다 [1]. 그래서 파일 시스템 추출만으로는 DB 를 읽을 수 없고, 같은 기기의 키체인을 따로 확보해야 도구가 복호해 읽습니다 [1]. 키체인의 구조와 보호 방식은 [키체인](../../01-foundations/storage/keychain.md) 에서 다룹니다.

번들 ID·앱 그룹 ID 와 로컬 백업의 도메인 이름은 이번 자료로 확인하지 못했고, 시그널 대화가 로컬 백업이나 iCloud 백업에 들어가는지도 확인하지 못했습니다. 로컬 백업에서는 앱 그룹 공유 폴더가 `AppDomainGroup-` 으로 시작하는 도메인으로 따로 나뉘어 있었지만(확인 범위: iOS 27.0), 관찰한 백업은 다른 회사 앱의 도메인 이름을 가려 두어 시그널 쪽은 알 수 없었습니다([로컬 백업](../../01-foundations/backups/local-backup/index.md)).

iLEAPP 시험 표본은 이름(abe_ios16, iphone11_ios17, dexter_ios18 등)으로 보아 iOS 16~18 기기에서 만든 것이지만, 표본의 시그널 앱 버전은 적어 두지 않았습니다 [1].

| 항목 | 확인된 범위 |
|---|---|
| iOS | 16~18(표본 이름 기준) [1] |
| 시그널 앱 | 기록 없음 |
| 버전별 구조 차이 | 확인하지 못함 |

## 구조

복호한 `signal.sqlite` 에서 도구가 읽는 표와 칸은 다음과 같습니다(주요 칸만) [1].

| 표 | 칸 |
|---|---|
| `model_TSInteraction` | `timestamp`, `receivedAtTimestamp`, `serverTimestamp`, `recordType`, `body`, `authorPhoneNumber`, `authorUUID`, `uniqueThreadId`, `read`, `isVoiceMessage`, `isViewOnceMessage`, `wasRemotelyDeleted`, `expiresInSeconds`, `attachmentIds`, `id`, `uniqueId` |
| `model_TSThread` | `uniqueId`, `contactPhoneNumber`, `contactUUID`, `creationDate` 등 |
| `model_SignalRecipient` | `recipientPhoneNumber`, `recipientUUID`, `pni` 등 |
| `model_TSAttachment` | `albumMessageId`, `localRelativeFilePath`, `sourceFilename`, `contentType` |

`recordType` 19 는 받은 메시지, 21 은 보낸 메시지이고, iLEAPP 는 시그널 iOS 공개 소스(SDSRecordType.swift)로 이 값을 확인했습니다 [1]. 보낸 메시지는 작성자 칸 대신 로그인한 계정을 작성자로 보고 표시합니다 [1].

`model_TSInteraction` 의 다음 세 칸은 대화에서 사라진 내용을 설명할 때 씁니다 [1].

| 칸 | 뜻 |
|---|---|
| `wasRemotelyDeleted` | 상대가 모두에게서 삭제한 메시지 |
| `expiresInSeconds` | 사라지는 메시지 타이머 |
| `isViewOnceMessage` | 한 번 보기 메시지 |

첨부 파일은 `model_TSAttachment.localRelativeFilePath` 로 `Attachments/` 아래 실제 파일과 이어지고, `sourceFilename` 에는 원래 파일 이름이, `contentType` 에는 파일 종류가 남습니다 [1].

`signal.sqlite` 는 파일 앞부분 일부를 평문으로 남겨 두어 암호화된 상태에서도 SQLite 파일로 식별됩니다 [1]. SQLite 형식 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 복호한 `model_TSInteraction` 행은 이 기기의 시그널 데이터에 그 메시지가 남아 있다는 기록이고, `recordType` 으로 보낸 것과 받은 것을 나눕니다 [1]. `wasRemotelyDeleted` 가 켜진 행은 상대가 모두에게서 삭제한 메시지가 있었다는 기록이라서, 본문이 없어도 메시지가 오갔다는 사실은 남습니다 [1]. `expiresInSeconds` 가 있으면 그 대화에 사라지는 메시지 타이머가 걸려 있었다는 기록입니다 [1].

DB 를 복호하지 못해도 `Attachments/` 의 파일은 평문으로 읽을 수 있어서, 이 기기의 시그널 데이터에 이 파일이 있다는 사실까지는 말할 수 있습니다 [1].

**증명하지 못하는 것.** DB 를 복호하지 못한 상태에서는 첨부 파일을 누가 보냈는지, 언제 오갔는지 알 수 없습니다. 첨부와 메시지를 잇는 정보가 암호화된 DB 안에 있기 때문입니다 [1]. 사라지는 메시지 타이머 칸은 타이머가 걸려 있었다는 사실만 보여 주고, 사용자가 일부러 메시지를 지웠다는 증거는 아닙니다.

## 시각 해석

`model_TSInteraction` 에는 `timestamp`, `receivedAtTimestamp`, `serverTimestamp` 세 시각이 있고, 도구는 모두 Unix 시각으로 바꿉니다 [1]. 칸 이름으로 보면 각각 메시지 자체의 시각, 이 기기가 받은 시각, 서버 시각이지만, 단위가 밀리초인지와 각 칸이 정확히 언제 쓰이는지는 이번 자료로 확인하지 못했습니다. 한 행에서 세 값을 나란히 놓고 크기를 비교해 단위를 정하고, 보고서에는 어느 칸의 값인지 적습니다. 변환 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

## 함정과 한계

키체인이 다른 기기 것이면 복호가 되지 않습니다 [1]. 추출 이미지와 키체인이 같은 기기에서 나왔는지 먼저 확인하고, 복호가 실패하면 DB 가 손상됐다고 단정하지 않습니다.

iOS 는 안드로이드와 키 보관 방식이 다르고, 첨부를 평문으로 둔다는 점도 다릅니다 [1]. 안드로이드 시그널 분석 경험을 그대로 옮기지 않습니다.

첨부가 평문이라는 점과 위 표·칸 이름은 iLEAPP 시험 표본(iOS 16~18) 범위에서 확인된 것입니다 [1]. 시그널 앱이 업데이트되면 첨부 저장 방식이나 표 구성이 달라질 수 있으니, 새 버전 기기에서는 `Attachments/` 파일이 실제로 평문인지 헥스로 먼저 확인합니다.

`Attachments/` 의 파일만 보고 "시그널로 받았다" 고 쓰면 기록보다 앞서 나간 것입니다. 복호하지 못했다면 "시그널 앱 공유 폴더의 `Attachments/` 에 이 파일이 있다" 까지만 씁니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래는 SQLite 명세로 만든 예시이고 실제 검체에서 나온 값이 아닙니다. 평범한 SQLite 파일의 첫 16바이트는 다음 머리글 문자열입니다.

```
53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

`signal.sqlite` 를 헥스 편집기로 열어 앞부분에서 SQLite 파일임을 알아볼 수 있는지 보고, 그 뒤로 이어지는 바이트가 뜻 없는 값으로만 채워져 있는지 확인합니다. 평문 SQLite 라면 페이지 안에 표 이름 같은 글자가 보이지만, 암호화된 부분에서는 보이지 않습니다.

**공개 도구로 한 번.** iLEAPP 의 시그널 분석기는 같은 기기의 키체인이 함께 있을 때 DB 를 복호해 메시지·상대·첨부 보고서를 만듭니다 [1]. 키체인 없이 돌리면 DB 쪽 보고서는 나오지 않으니, 그때는 `Attachments/` 폴더를 직접 훑어 파일 목록과 종류를 정리합니다.

## 교차 검증

- [키체인](../../01-foundations/storage/keychain.md) — DB 키를 보관하는 곳입니다.
- [알림 기록](../app-usage/notifications.md) — 사라진 메시지가 알림에 남았는지 봅니다.
- [KnowledgeC](../app-usage/knowledgec/index.md), [바이옴](../app-usage/biome/index.md) — 메시지 시각에 앱을 쓰고 있었는지 봅니다.
- [앱별 데이터 사용량](../network/data-usage.md) — DB 를 읽지 못했을 때 앱의 송수신 시간대를 봅니다.
- [사진 보관함](../media/photos/index.md) — `Attachments/` 의 사진이 사진 보관함에도 있는지 봅니다.
- [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md), [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md)

## 실습

공개 검체(NIST CFReDS 등) 가운데 시그널이 설치된 iOS 전체 파일 시스템 이미지와 같은 기기의 키체인이 함께 있는 것을 골라 풀어 봅니다.

1. `signal.sqlite` 를 헥스로 열어 앞부분과 그 뒤 바이트가 어떻게 다른지 적어 보십시오.
2. 복호한 뒤 `recordType` 19 와 21 인 행은 각각 몇 건입니까?
3. `wasRemotelyDeleted` 가 켜진 행이 있다면, 그 행의 대화 상대와 시각을 적어 보십시오.
4. `Attachments/` 의 파일 가운데 `model_TSAttachment` 에 짝이 없는 파일이 있습니까?
5. 한 메시지 행의 `timestamp`, `receivedAtTimestamp`, `serverTimestamp` 를 나란히 놓고 차이를 설명해 보십시오.

## 참고 문헌

1. iLEAPP, scripts/artifacts/signalIOS.py — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/signalIOS.py
