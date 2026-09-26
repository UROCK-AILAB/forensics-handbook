---
title: "카카오톡"
parent: "아티팩트 · 메신저"
nav_order: 790
has_children: true
has_toc: false
---

# 카카오톡 (KakaoTalk)

## 한 줄 요약

아이폰 카카오톡은 앱 데이터 컨테이너의 `Library/PrivateDocuments/` 아래 두 SQLite DB 에 메시지와 채팅방·사용자를 저장하고 받은 미디어는 채팅방별 폴더에 두며, 보낸 사람·채팅방·시각은 평문이지만 본문과 첨부 정보, 일부 전화번호는 열마다 암호화되어 있습니다.

## 왜 중요한가

국내 사건에서 누구와 언제 연락했는지를 물으면 카카오톡 기록을 빼놓기 어렵고, 기기에는 메시지 행과 채팅방, 친구 목록, 받은 사진·영상이 함께 남습니다. 본문이 암호화되어 있어도 보낸 사람·채팅방·종류·시각은 평문이라[1][2] 대화의 뼈대는 복호 전에도 잡을 수 있습니다. 본문을 푸는 방식은 공개 연구와 공개 도구로 알려져 있고[1][2][4], iLEAPP 에는 2026-09-22 에 iOS 카카오톡 분석기가 들어갔습니다[1]. 다만 공개 도구들이 시험한 iOS 버전과 앱 버전이 적혀 있지 않아서[2][3], 도구 결과를 그대로 옮기기보다 표를 직접 열어 맞춰 보는 편이 안전합니다.

## 한눈에 보기

카카오톡의 번들 ID 는 `com.iwilab.KakaoTalk` 이고, 로컬 백업에서는 `AppDomain-com.iwilab.KakaoTalk` 도메인에 들어갑니다[3]. 아래 위치는 모두 앱 데이터 컨테이너의 `Library/PrivateDocuments/` 기준입니다.

| 무엇 | 위치 | iOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 메시지 DB | `Message.sqlite`(`-wal`·`-shm` 포함)[2][3] | 공개 도구에 시험 버전이 적혀 있지 않음[2][3] | 채팅방, 보낸 사용자 ID, 메시지 종류, 보낸·읽은 시각, 암호화된 본문과 첨부 정보 |
| 채팅방·사용자 DB | `Talk.sqlite`[2][3] | 같음 | 채팅방 목록과 멤버 수, 채팅방 폴더, 앱이 아는 사용자, 연락처 동기화로 가져온 주소록 항목 |
| 받은 미디어 | `chat/`, `chatVideo/`, `chatAudio/` 아래 채팅방별 폴더[2] | 같음 | 받은 사진·영상·음성과 그 축소본 |

앱 설정 plist 와 앱 그룹 컨테이너, 로그인한 계정 정보가 어디 있는지는 실제 기기에서 확인합니다. 번들 ID 와 백업 도메인의 관계는 [번들 ID와 앱 그룹 (Bundle ID·App Group)](../../../01-foundations/value-decoding/bundle-id-app-group.md)에서 다룹니다.

> 그림 자리: 앱 데이터 컨테이너 안에서 `Message.sqlite`·`Talk.sqlite`·미디어 폴더가 채팅방 ID 와 사용자 ID 로 서로 이어지는 모습

## 읽는 순서

1. [저장 위치와 파일 (Paths·Files)](paths-files.md) — 기기와 로컬 백업에서 카카오톡 파일을 찾는 법, 흔한 이름의 DB 를 카카오톡 것으로 가려내는 법, WAL 을 빼면 생기는 누락을 다룹니다.
2. [대화 DB 구조와 암호화 (Chat DB)](chat-db.md) — `Message`·`ZCHAT` 표의 열과 열 단위 암호화, 한 표 안에 섞인 두 시각 기준을 다룹니다.
3. [받은 파일 (Received Files)](received-files.md) — 채팅방별 미디어 폴더와 축소본, 메시지와 파일을 잇는 법, 서버 쪽 파일 만료를 다룹니다.
4. [계정과 친구 목록 (Account·Friends)](account-friends.md) — `ZUSER`·`ZCONTACT` 표와 이름 열 세 개, 암호화된 전화번호, 내 계정 ID 를 정하는 방법의 한계를 다룹니다.

## 함께 볼 페이지

같은 상대와의 다른 연락은 [메시지 (iMessage·SMS)](../../communications/messages/index.md), [통화 기록 (CallHistory)](../../communications/call-history.md), [연락처 (AddressBook)](../../communications/contacts.md)에서 찾습니다. 앱을 언제 썼는지는 [KnowledgeC (knowledgeC.db)](../../app-usage/knowledgec/index.md), [바이옴 (Biome)](../../app-usage/biome/index.md), [알림 기록 (Notifications)](../../app-usage/notifications.md)에서 확인합니다. 다른 메신저는 [텔레그램 (Telegram)](../telegram.md), [라인 (LINE)](../line.md) 같은 메신저 분류의 페이지에서 다룹니다.

DB 와 값을 읽는 바탕은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md), [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md), [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)에 있고, 앱 데이터를 다루는 일반 절차는 [앱 데이터 분석 (App Data Analysis)](../../../03-techniques/analysis/app-data-analysis/index.md)에 있습니다.

조사 흐름은 [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md)와 [지운 대화와 사진 찾기 (Deleted Content)](../../../04-scenarios/activity/deleted-content.md)에서 이어집니다.

## 참고 문헌

1. abrignoni/iLEAPP, Pull Request #2249 "Add KakaoTalk support for iOS" (2026-09-22 병합) — https://github.com/abrignoni/iLEAPP/pull/2249
2. abrignoni/iLEAPP, `scripts/artifacts/kakaoTalk.py` — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/kakaoTalk.py
3. kim-do-hyeon/iOS-Forensic, `artifact_analyzer/messenger/kakaotalk/kakaotalk_analyzer.py` — https://github.com/kim-do-hyeon/iOS-Forensic/blob/main/artifact_analyzer/messenger/kakaotalk/kakaotalk_analyzer.py
4. 김도현·김병욱·양영욱·장홍준, 「iOS 환경에서 카카오톡 데이터 복호화 및 아티팩트 분석 연구」, 디지털콘텐츠학회논문지 26권 5호 1363-1373쪽, 2025, DOI 10.9728/dcs.2025.26.5.1363 — https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003204555
