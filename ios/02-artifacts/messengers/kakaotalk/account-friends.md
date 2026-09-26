---
title: "계정과 친구 목록"
parent: "카카오톡"
grand_parent: "아티팩트 · 메신저"
nav_order: 830
---

# 계정과 친구 목록 (Account·Friends)

카카오톡의 `Talk.sqlite` 에는 앱이 아는 카카오톡 사용자를 담은 `ZUSER` 표와 기기 주소록에서 가져온 항목을 담은 `ZCONTACT` 표가 따로 있고, 이름은 평문이지만 전화번호 열은 암호화되어 있습니다.

## 무엇을 기록하나 · 왜 생기나

`ZUSER` 의 한 행은 앱이 아는 사용자 한 명이고, 친구뿐만 아니라 함께 있는 채팅방의 멤버와 공식 계정까지 섞여 있습니다[2]. 메시지의 보낸 사람 이름은 이 표에서 찾습니다[2][3]. `ZCONTACT` 는 연락처 동기화를 켰을 때 기기 주소록에서 가져온 항목이라서, 한 행이 카카오톡 계정이 아니라 기기 주소록의 항목 하나입니다[2]. 파일 위치는 [저장 위치와 파일 (Paths·Files)](paths-files.md)에 있습니다.

## 위치와 버전별 차이

두 표 모두 `Library/PrivateDocuments/Talk.sqlite` 안에 있습니다[2]. `ZCONTACT` 의 `ZRAWPHONENUMBER`·`ZCONTACTID` 열은 오래된 스키마에는 없어서[2], 앱 버전에 따라 열 구성이 다릅니다. 아래 표의 "새 스키마"·"오래된 스키마" 는 iLEAPP 가 본 두 표본을 가리킵니다[2]. 어느 앱 버전부터 이 열이 생겼는지와 iOS 버전별 차이는 실제 데이터로 확인합니다.

| 열 | 새 스키마 | 오래된 스키마 |
|---|---|---|
| `ZRAWPHONENUMBER` | 있음[2] | 없음[2] |
| `ZCONTACTID` | 있음[2] | 없음[2] |

## 구조

### `ZUSER` 표

```
ZID, ZACCOUNTID, ZNAME, ZNICKNAME, ZCUSTOMNAME, ZSTATUSMESSAGE, ZEMAIL,
ZPHONENUMBER, ZFRIENDTYPE, ZBLOCKTYPE, ZUSERTYPE, ZHIDDEN, ZFAVORITE, ZPHOTOURL
```

| 열 | 읽는 법 |
|---|---|
| `ZID` | 사용자 ID 이고, `Message.userId` 와 잇는 값입니다[2][3] |
| `ZNAME`, `ZNICKNAME`, `ZCUSTOMNAME` | 이름이 세 열에 따로 저장되고 값이 서로 다를 수 있습니다. 셋을 모두 봅니다[2] |
| `ZPHONENUMBER` | 암호문이고, 그 행 자신의 `ZID` 로 만든 키로 풀립니다[2] |
| `ZFRIENDTYPE`, `ZBLOCKTYPE`, `ZUSERTYPE` | 정수이지만 값의 뜻은 공개되지 않았습니다[2] |
| `ZSTATUSMESSAGE`, `ZEMAIL` | 시험 기기 두 대에서는 비어 있었습니다[2] |
| `ZHIDDEN`, `ZFAVORITE` | 시험 기기 두 대에서는 0 이었습니다[2] |
| `ZPHOTOURL` | 프로필 사진의 원격 주소이고, 도구는 이 주소를 열지 않습니다[2] |
| `ZACCOUNTID` | 값의 뜻을 설명한 공개 자료가 없습니다 |

`ZPHONENUMBER` 는 시험 기기 두 대 모두 값이 있는 6행이 전부 풀렸습니다[2]. 암호화 방식은 메시지 본문과 같은 계열이고, 방식은 [대화 DB 구조와 암호화 (Chat DB)](chat-db.md)에서 다룹니다.

### `ZCONTACT` 표

```
ZNAME, ZPHONENUMBER, ZORIGINALPHONENUMBER, ZRAWPHONENUMBER, ZCONTACTID, ZUSER
```

이름(`ZNAME`)은 평문이고 번호 열은 base64 암호문입니다[2]. iLEAPP 개발 기록에는 이 번호가 메시지 본문과 다른 키를 쓰고 그 키를 찾지 못해 저장된 값 그대로 둔다고 적혀 있지만[1], 같은 도구의 설명문에는 본문과 같은 방식으로 암호화되어 있다고 적혀 있어서[2] 키가 무엇인지는 확인되지 않았습니다. `ZUSER` 열에는 앱이 이 주소록 항목과 짝이 되는 카카오톡 사용자를 찾았을 때만 그 사용자 ID 가 들어갑니다[2]. `ZORIGINALPHONENUMBER` 는 시험 기기 두 대에서 정규화된 번호와 값이 같았습니다[2].

### 내 계정 ID

기기 주인의 카카오톡 ID 를 어디서 정하는지는 출처끼리 어긋납니다. 한 공개 도구는 `ZFRIENDTYPE = 1` 인 행의 `ZID` 를 내 ID 로 쓰고[3], 그 ID 와 `Message.userId` 가 같으면 보낸 메시지로 봅니다[3]. iLEAPP 는 `ZFRIENDTYPE` 의 뜻이 밝혀지지 않았다고 적습니다[2]. 그래서 이 방법은 한 도구의 가정으로만 다루고, 보고서에 쓸 때는 다른 근거와 함께 씁니다. 로그인한 카카오 계정(이메일)이나 기기 등록 정보가 plist·키체인 가운데 어디에 있는지는 실제 기기에서 확인합니다. 키체인 자체는 [키체인 (iOS Keychain)](../../../01-foundations/storage/keychain.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `ZUSER` 행은 이 기기의 카카오톡이 그 사용자 ID 와 이름을 알고 있었다는 사실을 보여 줍니다. `ZCONTACT` 행은 연락처 동기화로 기기 주소록의 그 항목을 앱이 가져간 적이 있다는 사실을 보여 주고, `ZUSER` 열이 채워져 있으면 앱이 그 번호를 카카오톡 사용자와 이었다는 사실까지 보여 줍니다[2].

**증명하지 못하는 것.** `ZUSER` 에 행이 있다고 그 사람과 대화했다는 뜻은 아니어서[2], 대화 여부는 `Message.userId` 로 따로 확인합니다. 행이 친구인지 채팅방 멤버인지 공식 계정인지도 `ZFRIENDTYPE`·`ZUSERTYPE` 의 뜻이 공개되지 않아[2] 숫자만으로 구분하지 않습니다. `ZCONTACT` 의 이름은 기기 주소록에 적힌 이름이라서, 카카오톡 계정 주인의 실명이라고 볼 수 없습니다.

## 시각 해석

`ZUSER`·`ZCONTACT` 에는 공개 자료로 알려진 시각 열이 없습니다. 사용자가 언제 친구가 되었는지는 이 두 표만으로 알 수 없고, 그 사용자와 처음 주고받은 메시지 시각을 [대화 DB 구조와 암호화 (Chat DB)](chat-db.md)에서 찾아 봅니다.

## 함정과 한계

이름 열이 셋이라서 도구가 어느 열을 보고서에 썼는지 확인해야 합니다. 같은 사람이 도구마다 다른 이름으로 나올 수 있고, 열마다 누가 정한 이름인지는 공개된 설명이 없어서 보고서에는 열 이름을 함께 적습니다.

시험 기기 두 대에서는 `ZSTATUSMESSAGE`·`ZEMAIL` 이 비어 있고 `ZHIDDEN`·`ZFAVORITE` 가 0 이었지만[2], 다른 기기에서 값이 있다면 그 뜻은 새로 확인합니다. `ZPHOTOURL` 은 원격 주소라서 열면 서버에 접속 기록이 남을 수 있으니, 사건 기록 없이 열지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

`ZPHONENUMBER` 가 암호문인지 확인하는 방법은 메시지 본문과 같습니다. base64 를 풀어 길이가 16의 배수인지 보는 예시는 [대화 DB 구조와 암호화 (Chat DB)](chat-db.md)의 "직접 분석해 보기" 에 있습니다. `ZCONTACT.ZNAME` 은 평문이라서 헥스로 보면 UTF-8 글자가 그대로 보입니다.

### 질의로 한 번

```sql
-- Talk.sqlite 에서 실행한다
SELECT u.ZID, u.ZNAME, u.ZNICKNAME, u.ZCUSTOMNAME,
       u.ZFRIENDTYPE, u.ZUSERTYPE, u.ZBLOCKTYPE,
       length(u.ZPHONENUMBER) AS phone_b64_len
FROM ZUSER u
ORDER BY u.ZID;

SELECT c.ZNAME, c.ZUSER, u.ZNAME AS kakao_name
FROM ZCONTACT c
LEFT JOIN ZUSER u ON u.ZID = c.ZUSER;
```

`ZCONTACT.ZUSER` 에는 사용자 ID 가 들어가므로[2], 두 번째 질의는 이 열을 `ZUSER.ZID` 와 잇습니다. 짝이 맞지 않으면 두 열의 값 형식을 먼저 비교합니다.

### 공개 도구로 한 번

iLEAPP 의 카카오톡 분석기는 `ZUSER` 로 Users 보고서를, `ZCONTACT` 로 Address Book Matches 보고서를 만듭니다[1][2]. 보고서에 나온 이름이 세 이름 열 가운데 어느 것인지 위 질의 결과와 맞춰 봅니다.

## 교차 검증

`ZCONTACT` 의 이름과 번호는 기기의 [연락처 (AddressBook)](../../communications/contacts.md)와 맞춰 보고, 같은 상대와의 다른 연락은 [통화 기록 (CallHistory)](../../communications/call-history.md)과 [메시지 (iMessage·SMS)](../../communications/messages/index.md)에서 찾습니다. 기기를 쓴 사람이 계정 주인인지 따지는 흐름은 [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)에 있습니다.

## 실습

공개된 iOS 시험 이미지 가운데 카카오톡이 설치된 것으로 아래를 풀어 봅니다.

1. `ZUSER` 에서 `ZNAME`·`ZNICKNAME`·`ZCUSTOMNAME` 이 서로 다른 행을 찾아봅니다.
2. `ZUSER` 행 가운데 `Message.userId` 에 한 번도 나오지 않는 사용자를 세어 봅니다.
3. `ZCONTACT` 에서 `ZUSER` 가 빈 행과 채워진 행의 수를 비교해 봅니다.

## 참고 문헌

1. abrignoni/iLEAPP, Pull Request #2249 "Add KakaoTalk support for iOS" (2026-09-22 병합) — https://github.com/abrignoni/iLEAPP/pull/2249
2. abrignoni/iLEAPP, `scripts/artifacts/kakaoTalk.py` — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/kakaoTalk.py
3. kim-do-hyeon/iOS-Forensic, `artifact_analyzer/messenger/kakaotalk/kakaotalk_analyzer.py` — https://github.com/kim-do-hyeon/iOS-Forensic/blob/main/artifact_analyzer/messenger/kakaotalk/kakaotalk_analyzer.py
