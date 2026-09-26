---
title: "받은 파일"
parent: "카카오톡"
grand_parent: "아티팩트 · 메신저"
nav_order: 820
---

# 받은 파일 (Received Files)

카카오톡으로 받은 사진·영상·음성은 `Library/PrivateDocuments/` 아래 `chat`·`chatVideo`·`chatAudio` 폴더의 채팅방별 하위 폴더에 확장자 없이 저장되고, 복호한 첨부 정보 속 토큰이 파일 이름에 들어 있어 메시지와 파일을 이을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

채팅방에서 미디어를 받으면 앱이 파일을 기기에 내려받아 채팅방 폴더에 둡니다. 폴더 이름이 채팅방 ID 라서[2], 파일이 어느 채팅방에서 왔는지는 폴더만 보고도 알 수 있습니다. 앱은 화면에 보여 줄 축소본(썸네일)도 같은 곳에 만들고[2], 메시지 쪽에는 `Message.attachment` 열에 암호화된 첨부 정보가 남습니다[2]. `attachment` 열의 암호화는 [대화 DB 구조와 암호화 (Chat DB)](chat-db.md)에서 다룹니다.

## 위치와 버전별 차이

앱 데이터 컨테이너의 `Library/PrivateDocuments/` 아래에 미디어 종류별 폴더가 있고, 그 아래에 채팅방 ID 로 된 폴더가 있습니다[2].

```
Library/PrivateDocuments/chat/<채팅방ID>/
Library/PrivateDocuments/chatVideo/<채팅방ID>/
Library/PrivateDocuments/chatAudio/<채팅방ID>/
```

로컬 백업에서 이 폴더를 찾는 방법은 [저장 위치와 파일 (Paths·Files)](paths-files.md)에 있습니다. 시험한 iOS 버전과 앱 버전을 밝힌 공개 자료가 없어서, 폴더 구조가 버전에 따라 달라지는지는 실제 기기에서 확인합니다.

## 구조

파일에는 확장자가 없어서 형식은 파일 앞머리의 시그니처로 판단합니다[2]. 이름이 `_th_` 로 시작하거나 `-thum` 으로 끝나는 파일은 앱이 만든 축소본입니다[2]. 사진 메시지의 파일 이름은 아래 모양입니다[3].

```
chat/<채팅방ID>/_talkm_<조각1>_<조각2>_<조각3>
```

`<조각1>`~`<조각3>` 은 복호한 첨부 정보의 `k` 값을 `/` 로 나눈 뒤 끝 세 조각입니다[3]. 복호한 `attachment` 안의 토큰(`url`, `thumbnailUrl`, `key`)이 파일 이름에 들어 있어서, 같은 채팅방 폴더 안에서 메시지와 파일을 맞출 수 있습니다[2]. iLEAPP 시험(기기 한 대)에서는 미디어 메시지 6건 가운데 5건이 파일과 이어졌습니다[2].

iLEAPP 는 미디어 파일을 따로 풀지 않고 바로 그림으로 보여 줍니다[2]. 다만 미디어가 있던 시험 기기가 한 대뿐이라, 다른 기기와 버전에서는 앞머리 바이트로 파일이 암호화되어 있는지 확인합니다.

## 증거로서 의미

**증명하는 것.** 채팅방 폴더에 파일이 있으면 그 채팅방과 이어진 미디어가 수집 시점에 기기에 내려받아져 있었다는 사실을 보여 주고, 파일 내용도 직접 확인할 수 있습니다. 파일 이름의 토큰이 복호한 `attachment` 와 맞으면 그 파일을 특정 메시지와 이을 수 있습니다[2].

**증명하지 못하는 것.** 파일이 있다고 사용자가 그 파일을 열어 봤다고 말할 수 없고, 축소본만 있고 원본이 없다고 사용자가 원본을 지웠다고 볼 수도 없습니다. 파일 이름만으로는 보낸 사람을 알 수 없어서, 보낸 사람은 이어진 `Message` 행의 `userId` 로 찾습니다.

## 시각 해석

받은 파일의 시각을 따로 다룬 공개 자료는 없습니다. 메시지와 이어진 파일은 그 메시지의 `sentAt` 을 기준으로 삼고, 파일 시스템 시각은 무엇이 바뀔 때 바뀌는지 알려져 있지 않아 참고로만 씁니다. 메시지 시각을 바꾸는 법은 [대화 DB 구조와 암호화 (Chat DB)](chat-db.md)의 시각 해석 절에 있습니다.

## 함정과 한계

폴더에는 파일이 있는데 DB 에는 그 메시지가 없는 경우가 있었습니다[2]. 메시지가 지워져도 파일은 남을 수 있어서, 지운 대화를 찾을 때 미디어 폴더가 단서가 됩니다. 시험 기기에서는 채팅방 폴더 ID 7개 가운데 2개가 `ZCHAT` 에 없었고[2], 나간 방이나 지운 방일 가능성이 있지만 확인된 설명은 아닙니다. 이런 폴더는 "`ZCHAT` 에 없는 채팅방 ID 의 폴더에 파일이 있다" 로 기록으로 확인되는 만큼만 적습니다.

서버 쪽 보관은 기기와 따로 봅니다. 톡클라우드를 쓰더라도 톡클라우드에서 직접 지웠을 때, 용량이 모자라 자동 백업이 멈췄을 때, 채팅방 백업 설정에서 보관을 멈췄을 때, 백업하기 전에 이미 만료되었을 때는 사진·파일이 만료로 보입니다[4]. 서버가 기본으로 파일을 얼마나 보관하는지는 이 안내에 나와 있지 않습니다. 기기에 없는 파일을 서버 쪽에서 구하는 절차는 [클라우드 데이터 (iCloud·계정 데이터 요청)](../../../03-techniques/acquisition/cloud-data.md)에서 다룹니다.

받은 파일을 사진 앱에 저장했다면 사진 보관함에도 흔적이 남을 수 있어서 사진 보관함도 함께 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

확장자가 없으니 앞머리 바이트로 형식을 판별합니다. 아래는 각 형식 명세로 만든 예시이고 실제 기기에서 나온 값이 아닙니다.

```
JPEG  : FF D8 FF ...
PNG   : 89 50 4E 47 0D 0A 1A 0A
MP4   : ?? ?? ?? ?? 66 74 79 70 ...   (오프셋 4 부터 "ftyp")
```

앞머리가 어느 형식과도 맞지 않으면 암호화되었거나 다른 형식일 수 있으니, 그런 파일은 따로 모아 적어 둡니다.

### 메시지와 파일 맞추기

1. 채팅방 폴더마다 파일 목록을 뽑고, `_th_` 로 시작하거나 `-thum` 으로 끝나는 축소본을 따로 표시합니다[2].
2. 같은 `chatId` 의 메시지 가운데 `attachment` 가 있는 행을 고르고, 도구로 복호한 첨부 정보에서 `url`·`thumbnailUrl`·`key` 토큰을 꺼냅니다[2].
3. 토큰이 들어 있는 파일 이름을 같은 채팅방 폴더에서 찾아 짝을 짓습니다[2].
4. 짝이 없는 파일과 짝이 없는 메시지를 따로 목록으로 남기고, 폴더 이름이 `ZCHAT.ZID` 에 있는지도 확인합니다.

### 공개 도구로 한 번

iLEAPP 의 카카오톡 분석기는 위 폴더를 모아 Chat Media 보고서를 만듭니다[1][2]. 폴더에서 직접 센 파일 수와 보고서의 미디어 수를 맞춰 보면 이어지지 않은 파일이 드러납니다.

## 교차 검증

받은 사진이 사진 보관함에도 있는지는 [사진 보관함 (Photos Library)](../../media/photos/index.md)에서, 파일 안의 촬영 정보는 [카메라 사진과 메타데이터 (DCIM·EXIF·HEIC)](../../media/dcim-exif.md)에서 확인합니다. 지운 대화의 흔적으로 쓸 때는 [지운 대화와 사진 찾기 (Deleted Content)](../../../04-scenarios/activity/deleted-content.md)의 흐름을 따르고, 파일을 밖으로 보낸 정황을 따질 때는 [자료를 밖으로 보냈나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)를 봅니다.

## 실습

공개된 iOS 시험 이미지 가운데 카카오톡이 설치된 것으로 아래를 풀어 봅니다.

1. `chat` 아래 파일을 앞머리 바이트로 분류해 형식별 개수를 세어 봅니다.
2. 채팅방 폴더 이름 가운데 `ZCHAT.ZID` 에 없는 것을 찾아봅니다.
3. 축소본만 있고 원본이 없는 파일을 찾아, 이어진 메시지가 DB 에 있는지 확인해 봅니다.

## 참고 문헌

1. abrignoni/iLEAPP, Pull Request #2249 "Add KakaoTalk support for iOS" (2026-09-22 병합) — https://github.com/abrignoni/iLEAPP/pull/2249
2. abrignoni/iLEAPP, `scripts/artifacts/kakaoTalk.py` — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/kakaoTalk.py
3. kim-do-hyeon/iOS-Forensic, `artifact_analyzer/messenger/kakaotalk/kakaotalk_analyzer.py` — https://github.com/kim-do-hyeon/iOS-Forensic/blob/main/artifact_analyzer/messenger/kakaotalk/kakaotalk_analyzer.py
4. kakao 고객센터, 「톡클라우드를 구독중인데도 만료된 사진, 파일이 생겼어요.」 — https://cs.kakao.com/helps_html/1073206338?locale=ko
