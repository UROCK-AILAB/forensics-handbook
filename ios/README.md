---
title: iOS 개요
nav_order: -100
permalink: /
---

# iOS 디지털 포렌식 핸드북

iPhone에 남는 흔적을 어떻게 읽고 해석하는지 정리한 한국어 핸드북입니다.

## 구성

핸드북은 네 부분으로 나뉩니다.

| 부분 | 다루는 것 |
|---|---|
| **기반 구조** | iOS 파일 시스템·데이터 보호 등급·키체인·SQLite·plist·로컬 백업 같은 저장 구조와 형식. 여러 아티팩트가 이 형식 위에 기록됩니다 |
| **아티팩트 사전** | KnowledgeC·바이옴·메시지·통화 기록·사진 보관함·중요 위치·사파리·카카오톡·건강 데이터 등 아티팩트마다 한 페이지 |
| **분석 기법** | 수집 방식 비교·백업 수집·sysdiagnose·앱 데이터 분석·타임라인·삭제 데이터 복구·스파이웨어 흔적·보고서 작성 |
| **조사 시나리오** | "누구와 연락을 주고받았나" 같은 질문 하나에 여러 아티팩트를 엮어 답하는 흐름 |

큰 주제는 허브 페이지에서 전체를 보여 주고, 하위 페이지에서 하나씩 자세히 다룹니다.

## 페이지 구성

아티팩트 페이지는 대체로 아래 순서로 씁니다.

1. 무엇을 기록하고, 그 기록이 왜 생기는지
2. 파일 위치와 iOS 버전마다 다른 점
3. 구조 — 표와 열 이름, plist 키
4. 증거로 쓸 때 — 증명할 수 있는 것과 없는 것
5. 시각 읽기 — 언제 바뀌는지, 어떤 기준 시각을 쓰는지
6. 함정과 한계 — 자주 하는 오해, 지우거나 조작했을 때 남는 흔적
7. 직접 분석하기 — 파일을 직접 열어 한 번, 공개 도구로 한 번
8. 함께 볼 아티팩트 — 다른 기록과 맞춰 보기
9. 실습 질문과 참고 자료

## 읽는 법

- 처음이라면 기반 구조의 [데이터 보호](01-foundations/storage/data-protection/index.md)와 [로컬 백업](01-foundations/backups/local-backup/index.md)부터 읽기를 권합니다.
- 사건을 앞에 두고 있다면 조사 시나리오에서 질문을 고르고, 거기서 필요한 아티팩트로 넘어가면 됩니다. 예: [누구와 연락을 주고받았나](04-scenarios/activity/communication.md), [자료를 밖으로 보냈나](04-scenarios/exfiltration/data-exfiltration/index.md), [스파이웨어 감염 흔적](04-scenarios/incident/spyware.md)
- 특정 아티팩트만 궁금하다면 아래 목차에서 바로 찾으면 됩니다.

## 표기

- 명세나 공식 문서로 확인한 사실은 그대로 씁니다.
- 기기에서 본 내용은 iOS 27.0 기준입니다. 다른 판에서 달라지는 것은 그 자리에 판을 적습니다.
- 확인되지 않은 것은 쓰지 않습니다. 버전·기기마다 다를 수 있는 것은 분석가가 직접 확인하는 방법을 적습니다.
- 헥스 예시는 명세를 보고 만든 예시입니다. 실제 기기에서 나온 값이 아닙니다.
- 용어는 처음 나올 때 "한국어 (English)"로 한 번 적습니다.
- 잠금을 풀거나 보안 허점을 이용하는 방법은 다루지 않습니다. 수집 방식마다 무엇을 얻고 무엇을 못 얻는지만 씁니다.

# 목차


## 기반 구조

### 저장 구조

- [iOS의 파일 시스템 (APFS on iOS)](01-foundations/storage/filesystem/index.md)
  - [볼륨 구성 (System·Data·Preboot)](01-foundations/storage/filesystem/volumes.md)
  - [앱 컨테이너 (Bundle·Data·App Group)](01-foundations/storage/filesystem/app-containers.md)
  - [시스템 스냅숏과 업데이트 (Snapshots·Updates)](01-foundations/storage/filesystem/snapshots-updates.md)
- [데이터 보호 (Data Protection)](01-foundations/storage/data-protection/index.md)
  - [보호 등급 (Protection Classes)](01-foundations/storage/data-protection/protection-classes.md)
  - [잠금 해제 전·후 (BFU·AFU)](01-foundations/storage/data-protection/bfu-afu.md)
  - [보안 칩과 키 가방 (Secure Enclave·Keybag)](01-foundations/storage/data-protection/secure-enclave-keybag.md)
- [키체인 (iOS Keychain)](01-foundations/storage/keychain.md)

### 데이터 저장 형식

- [SQLite 데이터베이스 (SQLite)](01-foundations/data-formats/sqlite/index.md)
  - [페이지와 레코드 (B-tree·Record)](01-foundations/data-formats/sqlite/b-tree-record.md)
  - [WAL과 저널 (WAL·Journal)](01-foundations/data-formats/sqlite/wal-journal.md)
  - [지운 레코드 되살리기 (Freelist·Freeblock)](01-foundations/data-formats/sqlite/freelist-freeblock.md)
  - [Core Data 저장소 (Core Data)](01-foundations/data-formats/sqlite/core-data.md)
- [속성 목록 파일 (plist·NSKeyedArchiver)](01-foundations/data-formats/plist.md)
- [SEGB 형식 (SEGB)](01-foundations/data-formats/segb.md)
- [통합 로그 형식 (Unified Log·tracev3)](01-foundations/data-formats/unified-log.md)
- [프로토콜 버퍼 (Protocol Buffers)](01-foundations/data-formats/protobuf.md)

### 값 읽는 법

- [시각 값 (Mac 절대 시각·Unix·기타)](01-foundations/value-decoding/time-values.md)
- [번들 ID와 앱 그룹 (Bundle ID·App Group)](01-foundations/value-decoding/bundle-id-app-group.md)
- [기기 식별자 (UDID·ECID·일련번호)](01-foundations/value-decoding/device-identifiers.md)

### 백업 형식

- [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](01-foundations/backups/local-backup/index.md)
  - [백업 폴더 구조 (Manifest.db·Info.plist·Status.plist)](01-foundations/backups/local-backup/structure.md)
  - [도메인과 파일 이름 (Domain·fileID)](01-foundations/backups/local-backup/domains-fileid.md)
  - [암호 건 백업 (Encrypted Backup)](01-foundations/backups/local-backup/encrypted-backup.md)
- [아이클라우드 백업 (iCloud Backup)](01-foundations/backups/icloud-backup.md)
- [sysdiagnose 묶음 (sysdiagnose)](01-foundations/backups/sysdiagnose.md)

## 아티팩트 사전

### 시스템·계정

- [기기 정보 (Device Info·Lockdown)](02-artifacts/system-account/device-info.md)
- [애플 계정 (Apple Account)](02-artifacts/system-account/apple-account.md)
- [설정 값 (Preferences)](02-artifacts/system-account/preferences.md)
- [시간대와 시각 설정 (Time Zone)](02-artifacts/system-account/time-zone.md)
- [암호와 Face ID 설정 흔적 (Passcode·Biometrics)](02-artifacts/system-account/passcode-biometrics.md)
- [초기화와 복원 흔적 (Erase·Restore)](02-artifacts/system-account/erase-restore.md)

### 앱 설치·사용 흔적

- [KnowledgeC (knowledgeC.db)](02-artifacts/app-usage/knowledgec/index.md)
  - [표와 스트림 구조 (ZOBJECT·Stream)](02-artifacts/app-usage/knowledgec/structure.md)
  - [앱 사용 기록 (App Usage)](02-artifacts/app-usage/knowledgec/app-usage.md)
  - [화면·잠금 상태 (Display·Device Lock)](02-artifacts/app-usage/knowledgec/device-state.md)
- [바이옴 (Biome)](02-artifacts/app-usage/biome/index.md)
  - [저장 위치와 스트림 (Streams)](02-artifacts/app-usage/biome/streams.md)
  - [앱 사용 스트림 (App.InFocus)](02-artifacts/app-usage/biome/app-infocus.md)
- [화면 사용 시간 (Screen Time)](02-artifacts/app-usage/screen-time.md)
- [설치된 앱 (Installed Apps·applicationState.db)](02-artifacts/app-usage/installed-apps.md)
- [앱 스토어 기록 (App Store)](02-artifacts/app-usage/app-store.md)
- [알림 기록 (Notifications)](02-artifacts/app-usage/notifications.md)
- [충돌·진단 기록 (Analytics·Crash Logs)](02-artifacts/app-usage/diagnostics.md)
- [전원 로그 (PowerLog)](02-artifacts/app-usage/powerlog.md)

### 통화·메시지·연락처

- [메시지 (iMessage·SMS)](02-artifacts/communications/messages/index.md)
  - [대화 DB 구조 (sms.db)](02-artifacts/communications/messages/sms-db.md)
  - [첨부 파일 (Attachments)](02-artifacts/communications/messages/attachments.md)
  - [지운 메시지의 흔적 (Deleted Messages)](02-artifacts/communications/messages/deleted-messages.md)
- [통화 기록 (CallHistory)](02-artifacts/communications/call-history.md)
- [연락처 (AddressBook)](02-artifacts/communications/contacts.md)
- [음성 사서함과 통화 녹음 (Voicemail·Call Recording)](02-artifacts/communications/voicemail-recording.md)
- [페이스타임 (FaceTime)](02-artifacts/communications/facetime.md)

### 사진·미디어

- [사진 보관함 (Photos Library)](02-artifacts/media/photos/index.md)
  - [사진 DB 구조 (Photos.sqlite)](02-artifacts/media/photos/photos-sqlite.md)
  - [앨범과 공유 앨범 (Albums·Shared Albums)](02-artifacts/media/photos/albums-shared.md)
  - [최근 삭제된 항목 (Recently Deleted)](02-artifacts/media/photos/recently-deleted.md)
- [카메라 사진과 메타데이터 (DCIM·EXIF·HEIC)](02-artifacts/media/dcim-exif.md)
- [스크린샷과 화면 녹화 (Screenshots·Screen Recording)](02-artifacts/media/screenshots.md)

### 위치

- [중요 위치 (Significant Locations)](02-artifacts/location/significant-locations.md)
- [위치 기록 데몬 (routined)](02-artifacts/location/routined.md)
- [나의 찾기 (Find My)](02-artifacts/location/find-my.md)
- [Apple 지도 (Apple Maps)](02-artifacts/location/apple-maps.md)
- [네이버 지도 (NAVER Map)](02-artifacts/location/naver-map.md)
- [카카오맵 (KakaoMap)](02-artifacts/location/kakaomap.md)

### 네트워크·연결

- [와이파이 기록 (Wi-Fi)](02-artifacts/network/wifi.md)
- [블루투스 장치 (Bluetooth)](02-artifacts/network/bluetooth.md)
- [앱별 데이터 사용량 (DataUsage.sqlite)](02-artifacts/network/data-usage.md)
- [VPN 설정 (VPN)](02-artifacts/network/vpn.md)
- [에어드롭 (AirDrop)](02-artifacts/network/airdrop.md)
- [개인용 핫스폿 (Personal Hotspot)](02-artifacts/network/hotspot.md)

### 인터넷·브라우저

- [사파리 (Safari)](02-artifacts/browsers/safari/index.md)
  - [방문 기록 (History.db)](02-artifacts/browsers/safari/history.md)
  - [탭과 세션 (Tabs)](02-artifacts/browsers/safari/tabs.md)
  - [북마크와 읽기 목록 (Bookmarks·Reading List)](02-artifacts/browsers/safari/bookmarks-reading-list.md)
  - [개인 정보 보호 브라우징 (Private Browsing)](02-artifacts/browsers/safari/private-browsing.md)
- [크롬 (Chrome for iOS)](02-artifacts/browsers/chrome.md)
- [네이버 앱 (NAVER)](02-artifacts/browsers/naver.md)

### 메신저

- [카카오톡 (KakaoTalk)](02-artifacts/messengers/kakaotalk/index.md)
  - [저장 위치와 파일 (Paths·Files)](02-artifacts/messengers/kakaotalk/paths-files.md)
  - [대화 DB 구조와 암호화 (Chat DB)](02-artifacts/messengers/kakaotalk/chat-db.md)
  - [받은 파일 (Received Files)](02-artifacts/messengers/kakaotalk/received-files.md)
  - [계정과 친구 목록 (Account·Friends)](02-artifacts/messengers/kakaotalk/account-friends.md)
- [텔레그램 (Telegram)](02-artifacts/messengers/telegram.md)
- [왓츠앱 (WhatsApp)](02-artifacts/messengers/whatsapp.md)
- [라인 (LINE)](02-artifacts/messengers/line.md)
- [시그널 (Signal)](02-artifacts/messengers/signal.md)
- [페이스북 메신저 (Messenger)](02-artifacts/messengers/facebook-messenger.md)
- [인스타그램 (Instagram)](02-artifacts/messengers/instagram.md)
- [디스코드 (Discord)](02-artifacts/messengers/discord.md)
- [위챗 (WeChat)](02-artifacts/messengers/wechat.md)
- [슬랙과 팀즈 (Slack·Teams)](02-artifacts/messengers/slack-teams.md)

### 국내 생활 앱

- [네이버 밴드 (BAND)](02-artifacts/korean-apps/band.md)
- [당근 (Karrot)](02-artifacts/korean-apps/karrot.md)
- [쿠팡 (Coupang)](02-artifacts/korean-apps/coupang.md)
- [배달 앱 (배달의민족·쿠팡이츠·요기요)](02-artifacts/korean-apps/delivery-apps.md)

### 메일·클라우드·애플 앱

- [메일 앱 (Apple Mail)](02-artifacts/mail-cloud/apple-mail.md)
- [지메일 (Gmail)](02-artifacts/mail-cloud/gmail.md)
- [아이클라우드 드라이브 (iCloud Drive)](02-artifacts/mail-cloud/icloud-drive.md)
- [메모 (Notes)](02-artifacts/mail-cloud/notes.md)
- [미리 알림과 캘린더 (Reminders·Calendar)](02-artifacts/mail-cloud/reminders-calendar.md)
- [구글 드라이브 (Google Drive)](02-artifacts/mail-cloud/google-drive.md)
- [네이버 MYBOX (MYBOX)](02-artifacts/mail-cloud/mybox.md)

### 건강·지갑·워치

- [건강 데이터 (Health)](02-artifacts/health-wallet/health.md)
- [지갑과 Apple Pay (Wallet)](02-artifacts/health-wallet/wallet.md)
- [애플 워치 연결 (Apple Watch)](02-artifacts/health-wallet/apple-watch.md)

### 입력·음성 비서

- [키보드 입력 기록 (Keyboard)](02-artifacts/input-assistant/keyboard.md)
- [시리 (Siri)](02-artifacts/input-assistant/siri.md)

### 로그

- [통합 로그에서 찾을 것 (Unified Log Events)](02-artifacts/logs/unified-log-events.md)
- [sysdiagnose 안의 로그 (sysdiagnose Logs)](02-artifacts/logs/sysdiagnose-logs.md)

### 자격 증명·보안 설정

- [저장된 암호 (Passwords·iCloud Keychain)](02-artifacts/credentials-security/saved-passwords.md)
- [구성 프로파일과 MDM (Configuration Profiles·MDM)](02-artifacts/credentials-security/configuration-profiles.md)

### 파일 내장 메타데이터

- [앱 번들 정보 (IPA·Info.plist)](02-artifacts/embedded-metadata/app-bundle.md)
- [문서 메타데이터 (PDF·Office·iWork)](02-artifacts/embedded-metadata/documents.md)

## 분석 기법

### 조사 절차·증거 확보

- [조사 절차 (Investigation Process)](03-techniques/acquisition/investigation-process.md)
- [모바일 증거 확보 (Acquisition)](03-techniques/acquisition/mobile-acquisition/index.md)
  - [수집 방식 비교 (백업·파일 시스템·클라우드)](03-techniques/acquisition/mobile-acquisition/methods.md)
  - [압수와 보관 (전원·통신 차단·USB 제한 모드)](03-techniques/acquisition/mobile-acquisition/seizure-handling.md)
  - [백업으로 수집 (Backup Acquisition)](03-techniques/acquisition/mobile-acquisition/backup-acquisition.md)
  - [sysdiagnose로 수집 (sysdiagnose Collection)](03-techniques/acquisition/mobile-acquisition/sysdiagnose-collection.md)
  - [결과물 형식과 해시 (Extraction Formats·Hash)](03-techniques/acquisition/mobile-acquisition/formats-hash.md)
- [클라우드 데이터 (iCloud·계정 데이터 요청)](03-techniques/acquisition/cloud-data.md)

### 분석

- [앱 데이터 분석 (App Data Analysis)](03-techniques/analysis/app-data-analysis/index.md)
  - [처음 보는 앱 분석 순서 (Unknown Apps)](03-techniques/analysis/app-data-analysis/unknown-apps.md)
  - [캐시와 웹뷰 (Cache·WebKit)](03-techniques/analysis/app-data-analysis/cache-webkit.md)
  - [지운 앱이 남긴 흔적 (Uninstalled Apps)](03-techniques/analysis/app-data-analysis/uninstalled-apps.md)
- [타임라인 작성 (Timeline)](03-techniques/analysis/timeline/index.md)
  - [시각 정규화 (Time Normalization)](03-techniques/analysis/timeline/time-normalization.md)
  - [여러 기록 엮기 (Correlation)](03-techniques/analysis/timeline/correlation.md)
  - [시각 조작 흔적 (Time Manipulation)](03-techniques/analysis/timeline/time-manipulation.md)
- [삭제 데이터 복구 (Data Recovery)](03-techniques/analysis/data-recovery/index.md)
  - [SQLite 레코드 되살리기 (SQLite)](03-techniques/analysis/data-recovery/sqlite-records.md)
  - [카빙 (Carving)](03-techniques/analysis/data-recovery/carving.md)
  - [복구가 안 되는 이유 (Encryption·TRIM)](03-techniques/analysis/data-recovery/limits.md)
- [악성 코드·스파이웨어 흔적 (Malware·Spyware Triage)](03-techniques/analysis/spyware-triage/index.md)
  - [구성 프로파일과 설정으로 찾기 (Profiles·Settings)](03-techniques/analysis/spyware-triage/profiles-settings.md)
  - [스파이웨어 흔적 찾기 (MVT)](03-techniques/analysis/spyware-triage/spyware-mvt.md)
  - [감시 앱 흔적 (Stalkerware)](03-techniques/analysis/spyware-triage/stalkerware.md)
- [콘텐츠 검색 (Content Search)](03-techniques/analysis/content-search.md)

### 보고

- [포렌식 보고서 (Forensic Report)](03-techniques/reporting/forensic-report.md)
- [도구 검증 (Tool Validation)](03-techniques/reporting/tool-validation.md)

## 조사 시나리오

### 행위 재구성

- [누구와 연락을 주고받았나 (Communication)](04-scenarios/activity/communication.md)
- [어떤 앱을 언제 썼나 (App Usage)](04-scenarios/activity/app-usage.md)
- [이 사진은 언제 어디서 찍었나 (Photo Origin)](04-scenarios/activity/photo-origin.md)
- [그 시각에 어디 있었나 (Location)](04-scenarios/activity/location.md)
- [웹 사용 행위 재구성 (Web Activity)](04-scenarios/activity/web-activity.md)
- [폰 사용 시간 재구성 (Usage Time)](04-scenarios/activity/usage-time.md)
- [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](04-scenarios/activity/user-attribution.md)
- [지운 대화와 사진 찾기 (Deleted Content)](04-scenarios/activity/deleted-content.md)
- [증거를 없애려 했나 (Anti-Forensics)](04-scenarios/activity/anti-forensics/index.md)
  - [초기화 (Erase All Content)](04-scenarios/activity/anti-forensics/erase-reset.md)
  - [앱 지우기 (App Removal)](04-scenarios/activity/anti-forensics/app-removal.md)
  - [메시지·사진 지우기 (Content Deletion)](04-scenarios/activity/anti-forensics/content-deletion.md)
  - [시각 바꾸기 (Time Change)](04-scenarios/activity/anti-forensics/time-change.md)

### 정보 유출

- [자료를 밖으로 보냈나 (Data Exfiltration)](04-scenarios/exfiltration/data-exfiltration/index.md)
  - [메신저로 (Messenger)](04-scenarios/exfiltration/data-exfiltration/messenger.md)
  - [클라우드로 (Cloud)](04-scenarios/exfiltration/data-exfiltration/cloud.md)
  - [메일로 (Email)](04-scenarios/exfiltration/data-exfiltration/email.md)
  - [에어드롭으로 (AirDrop)](04-scenarios/exfiltration/data-exfiltration/airdrop.md)
  - [PC 동기화로 (PC Sync)](04-scenarios/exfiltration/data-exfiltration/pc-sync.md)

### 침해 사고

- [악성 코드는 어디서 들어왔나 (Initial Access)](04-scenarios/incident/initial-access.md)
- [스파이웨어 감염 흔적 (Spyware)](04-scenarios/incident/spyware.md)
- [스미싱 흔적 (Smishing)](04-scenarios/incident/smishing.md)
- [계정 탈취 흔적 (Account Takeover)](04-scenarios/incident/account-takeover.md)
