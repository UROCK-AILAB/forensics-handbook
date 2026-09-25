---
title: "삭제 데이터 복구"
parent: "기법 · 분석"
nav_order: 1310
has_children: true
has_toc: false
---

# 삭제 데이터 복구 (Data Recovery)

아이폰에서 지운 데이터는 앱의 "최근 삭제됨" 보관, SQLite 파일 안에 남은 조각, 지우기 전에 만든 백업, 동기화된 클라우드 사본에서 찾고, 저장 공간 전체를 훑는 카빙은 거의 통하지 않습니다.

## 왜 중요한가

조사에서 가장 자주 나오는 질문 가운데 하나가 "지운 대화나 사진을 되살릴 수 있느냐" 입니다. PC 하드디스크라면 지운 파일의 블록을 훑어 되살리는 방법이 먼저 떠오르지만, 아이폰에서는 이 길이 거의 막혀 있습니다. ElcomSoft(2021)는 지운 데이터를 찾는 길을 다섯 가지로 정리하면서, 지운 파일 자체를 카빙으로 되살리는 도구는 없다고 적었습니다 [1]. 그래서 아이폰의 복구 작업은 "어디에 사본이나 조각이 아직 남아 있나" 를 차례로 따지는 일이 됩니다.

지운 항목이 DB 안에 행으로 그대로 남아 있는 경우도 많습니다. 사진·메시지·메모·미리 알림 같은 Apple 앱의 DB 에는 휴지통 상태나 지운 시각을 담는 칸이 따로 있어서, 사용자 화면에서는 사라진 항목이 일반 쿼리로 보이기도 합니다. 이 칸의 목록은 [SQLite 레코드 되살리기](sqlite-records.md) 에 모았습니다.

## 한눈에 보기

| 찾는 길 | 어디를 보나 | iOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 앱의 "최근 삭제됨" 보관 | 사진 "최근 삭제된 항목", 메시지 "최근 삭제된 항목" | 메시지는 iOS 16·iPadOS 16.1 부터 [2] | 사용자가 지웠지만 아직 영구 삭제되지 않은 항목 |
| SQLite 파일 안의 조각 | freelist 페이지, 페이지 안의 빈 조각, WAL 프레임 | 파일 구조는 SQLite 명세를 따르고, 남는 정도는 DB 설정마다 다름 | 지우기 전 행의 전부 또는 일부 |
| 지우기 전에 만든 백업 | 로컬 백업, 아이클라우드 백업 | 백업 시점에 따라 다름 | 백업을 만든 때에 있던 데이터 |
| 동기화된 클라우드 사본 | 아이클라우드 쪽 데이터 | 계정 설정에 따라 다름 | 기기에서 지운 뒤에도 서버에 남은 항목 |

Apple 안내에 따르면 사진 앱은 "최근 삭제된 항목" 에 든 사진을 30일 동안 보관한 뒤 영구 삭제하고, 이 앨범은 iPhone·iPad 에서 Face ID·Touch ID 나 암호로 잠깁니다 [3]. 잠금이 어느 iOS 버전부터인지는 이 안내에 나오지 않습니다. 사진 보관 기간과 관련해 로컬 백업의 `CameraRollDomain :: Media/PhotoData/CPL/cloudphotos-#.#.plist` 안 `configuration` 에 `max.days.inRecentlyDeleted` 키가 있지만, 값은 읽지 않았습니다(확인 범위: iPhone 13 mini, iOS 27.0). 메시지는 iOS 16·iPadOS 16.1 부터 "최근 삭제된 항목" 에서 되살릴 수 있고, 지운 지 30~40일 안의 것만 됩니다 [2]. 메모 앱의 보관 기간은 확인한 자료에 나오지 않습니다.

백업과 클라우드 쪽은 업체 주장이 대부분이라 그대로 인용하지 말고 검체로 확인합니다. ElcomSoft 는 Apple 이 최근 아이클라우드 백업 두 개를 보관한다고 적었고, 키체인·건강·홈·아이클라우드 사진과 동기화 설정에 따른 메시지는 아이클라우드 백업에 들어가지 않으며 iOS 13 부터는 통화 기록과 Safari 방문 기록도 빠진다고 적었습니다 [1]. 또 사진·메모 같은 일부 항목은 "삭제됨" 폴더에서 비운 뒤에도 아이클라우드 쪽에 보통 2~3주 남고, 지운 뒤 기기가 온라인에 연결되지 않았다면 동기화 항목을 되살릴 여지가 있다고 주장합니다 [1].

## 읽는 순서

1. [SQLite 레코드 되살리기 (SQLite)](sqlite-records.md) — 지움 표시가 붙은 채 남은 행을 먼저 보고, freelist·빈 조각·WAL 프레임에서 지운 행을 읽는 절차를 다룹니다.
2. [카빙 (Carving)](carving.md) — 저장 공간 카빙이 왜 통하지 않는지 짚고, 풀린 파일 안쪽을 레코드 구조로 훑는 방법을 다룹니다.
3. [복구가 안 되는 이유 (Encryption·TRIM)](limits.md) — 파일별 키 암호화, SQLite 정리 설정, 수집 방식 때문에 흔적이 사라지는 경로를 정리합니다.

## 함께 볼 페이지

- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) — 파일 형식 전체
- [데이터 보호 (Data Protection)](../../../01-foundations/storage/data-protection/index.md) — 파일별 키와 보호 등급
- [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md), [아이클라우드 백업 (iCloud Backup)](../../../01-foundations/backups/icloud-backup.md) — 지우기 전 사본
- [클라우드 데이터 (iCloud·계정 데이터 요청)](../../acquisition/cloud-data.md) — 서버에 남은 사본 확보
- [메시지 (iMessage·SMS)](../../../02-artifacts/communications/messages/index.md), [사진 보관함 (Photos Library)](../../../02-artifacts/media/photos/index.md) — 지움 표시가 남는 대표 DB
- [지운 대화와 사진 찾기 (Deleted Content)](../../../04-scenarios/activity/deleted-content.md), [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md) — 이 기법을 쓰는 조사 시나리오

## 참고 문헌

1. The Five Ways to Recover iPhone Deleted Data — ElcomSoft blog (2021-11) — https://blog.elcomsoft.com/2021/11/the-five-ways-to-recover-iphone-deleted-data/
2. Recover deleted text messages on your iPhone or iPad — Apple Support — https://support.apple.com/en-us/102615
3. How to recover deleted photos on your iPhone, iPad, Mac, or Apple Vision Pro — Apple Support — https://support.apple.com/en-us/124460
