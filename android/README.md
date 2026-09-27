---
title: 처음
nav_order: -100
permalink: /
---

# Android 디지털 포렌식 핸드북

Android 기기에 남는 흔적을 어떻게 읽고 해석하는지 정리한 한국어 핸드북입니다.

## 구성

핸드북은 네 부분으로 나뉩니다.

| 부분 | 다루는 것 |
|---|---|
| **기반 구조** | 파티션·ext4·F2FS·파일 단위 암호화·SQLite·ABX 같은 저장 구조와 형식. 여러 아티팩트가 이 형식 위에 기록됩니다 |
| **아티팩트 사전** | 계정·설치된 앱·usagestats·통화와 문자·미디어·위치·와이파이·크롬·카카오톡 등 아티팩트마다 한 페이지 |
| **분석 기법** | 수집 방식 비교·ADB·백업 수집·앱 데이터 분석·타임라인·삭제 데이터 복구·악성 앱 흔적·보고서 작성 |
| **조사 시나리오** | "누구와 연락을 주고받았나" 같은 질문 하나에 여러 아티팩트를 엮어 답하는 흐름 |

큰 주제는 허브 페이지에서 전체를 보여 주고, 하위 페이지에서 하나씩 자세히 다룹니다.

## 페이지 구성

아티팩트 페이지는 대체로 아래 순서로 씁니다.

1. 무엇을 기록하고, 그 기록이 왜 생기는지
2. 파일 위치와 Android 버전·제조사마다 다른 점
3. 구조 — 표와 열 이름, 설정 키
4. 증거로 쓸 때 — 증명할 수 있는 것과 없는 것
5. 시각 읽기 — 언제 바뀌는지, 어떤 기준 시각을 쓰는지
6. 함정과 한계 — 자주 하는 오해, 지우거나 조작했을 때 남는 흔적
7. 직접 분석하기 — 파일을 직접 열어 한 번, 공개 도구로 한 번
8. 함께 볼 아티팩트 — 다른 기록과 맞춰 보기
9. 실습 질문과 참고 자료

## 읽는 법

- 처음이라면 기반 구조의 [저장 공간 암호화](01-foundations/storage/encryption/index.md)와 [SQLite 데이터베이스](01-foundations/data-formats/sqlite/index.md)부터 읽기를 권합니다.
- 사건을 앞에 두고 있다면 조사 시나리오에서 질문을 고르고, 거기서 필요한 아티팩트로 넘어가면 됩니다. 예: [누구와 연락을 주고받았나](04-scenarios/activity/communication.md), [자료를 밖으로 보냈나](04-scenarios/exfiltration/data-exfiltration/index.md), [몰래 설치된 감시 앱](04-scenarios/incident/stalkerware.md)
- 특정 아티팩트만 궁금하다면 아래 목차에서 바로 찾으면 됩니다.

## 표기

- 명세나 공식 문서로 확인한 사실은 그대로 씁니다.
- 기기에서 본 내용은 Android 16(One UI 8.5) 기준입니다. 다른 판에서 달라지는 것은 그 자리에 판을 적습니다.
- 확인되지 않은 것은 쓰지 않습니다. 버전·기기마다 다를 수 있는 것은 분석가가 직접 확인하는 방법을 적습니다.
- 헥스 예시는 명세를 보고 만든 예시입니다. 실제 기기에서 나온 값이 아닙니다.
- 용어는 처음 나올 때 "한국어 (English)"로 한 번 적습니다.
- 잠금을 풀거나 보안 허점을 이용하는 방법은 다루지 않습니다. 수집 방식마다 무엇을 얻고 무엇을 못 얻는지만 씁니다.

# 목차


## 기반 구조

### 저장 구조

- [파티션과 저장 영역 (Partitions)](01-foundations/storage/partitions/index.md)
  - [파티션 배치 (boot·system·vendor·userdata)](01-foundations/storage/partitions/partition-layout.md)
  - [동적 파티션 (super)](01-foundations/storage/partitions/super-partition.md)
  - [A/B 슬롯 (A/B Slots)](01-foundations/storage/partitions/ab-slots.md)
- [파일 시스템 (ext4·F2FS)](01-foundations/storage/filesystems/index.md)
  - [ext4 구조 (ext4)](01-foundations/storage/filesystems/ext4.md)
  - [F2FS 구조 (F2FS)](01-foundations/storage/filesystems/f2fs.md)
  - [지운 파일과 저널 (Deleted Files·Journal)](01-foundations/storage/filesystems/deleted-files-journal.md)
- [저장 공간 암호화 (Encryption)](01-foundations/storage/encryption/index.md)
  - [파일 단위 암호화 (FBE)](01-foundations/storage/encryption/fbe.md)
  - [잠금 해제 전·후 (BFU·AFU)](01-foundations/storage/encryption/bfu-afu.md)
  - [CE 영역과 DE 영역 (Credential·Device Encrypted Storage)](01-foundations/storage/encryption/ce-de-storage.md)
  - [키 저장소와 보안 하드웨어 (Keystore·TEE·StrongBox)](01-foundations/storage/encryption/keystore-tee.md)
- [앱 데이터 폴더 구조 (/data/data·/data/user)](01-foundations/storage/app-data-layout.md)
- [공용 저장 공간 (Shared Storage·/sdcard)](01-foundations/storage/shared-storage.md)

### 데이터 저장 형식

- [SQLite 데이터베이스 (SQLite)](01-foundations/data-formats/sqlite/index.md)
  - [페이지와 레코드 (B-tree·Record)](01-foundations/data-formats/sqlite/b-tree-record.md)
  - [WAL과 저널 (WAL·Journal)](01-foundations/data-formats/sqlite/wal-journal.md)
  - [지운 레코드 되살리기 (Freelist·Freeblock)](01-foundations/data-formats/sqlite/freelist-freeblock.md)
  - [암호화된 SQLite (SQLCipher)](01-foundations/data-formats/sqlite/sqlcipher.md)
- [설정 XML과 SharedPreferences (XML·SharedPreferences)](01-foundations/data-formats/shared-preferences.md)
- [안드로이드 바이너리 XML (ABX)](01-foundations/data-formats/abx.md)
- [프로토콜 버퍼 (Protocol Buffers)](01-foundations/data-formats/protobuf.md)
- [LevelDB와 IndexedDB (LevelDB·IndexedDB)](01-foundations/data-formats/leveldb-indexeddb.md)

### 값 읽는 법

- [시각 값 (Unix 밀리초·Chrome 시각·기타)](01-foundations/value-decoding/time-values.md)
- [패키지 이름과 UID (Package Name·UID)](01-foundations/value-decoding/package-uid.md)
- [기기 식별자 (Android ID·IMEI·광고 ID)](01-foundations/value-decoding/device-identifiers.md)

### 보안 구조

- [앱 샌드박스와 권한 (Sandbox·Permissions)](01-foundations/security-model/sandbox-permissions.md)
- [부트로더와 검증 부팅 (Bootloader·Verified Boot)](01-foundations/security-model/verified-boot.md)
- [삼성 녹스 (Samsung Knox)](01-foundations/security-model/samsung-knox.md)
- [보안 폴더와 작업 프로필 (Secure Folder·Work Profile)](01-foundations/security-model/secure-folder-work-profile.md)

## 아티팩트 사전

### 시스템·계정

- [기기 정보와 빌드 (build.prop·Build)](02-artifacts/system-account/device-build.md)
- [계정 (Accounts)](02-artifacts/system-account/accounts/index.md)
  - [계정 DB 구조 (accounts_ce.db·accounts_de.db)](02-artifacts/system-account/accounts/accounts-db.md)
  - [구글 계정 흔적 (Google Account)](02-artifacts/system-account/accounts/google-account.md)
  - [삼성 계정 흔적 (Samsung Account)](02-artifacts/system-account/accounts/samsung-account.md)
- [사용자와 프로필 (Multi-user·users)](02-artifacts/system-account/users-profiles.md)
- [설정 값 (Settings Global·Secure·System)](02-artifacts/system-account/settings.md)
- [시간대와 시각 설정 (Time Zone)](02-artifacts/system-account/time-zone.md)
- [잠금 화면 설정 (Lock Settings)](02-artifacts/system-account/lock-settings.md)
- [초기화 흔적 (Factory Reset)](02-artifacts/system-account/factory-reset.md)

### 앱 설치·사용 흔적

- [설치된 앱 (packages.xml)](02-artifacts/app-usage/packages/index.md)
  - [패키지 목록 구조 (packages.xml·packages.list)](02-artifacts/app-usage/packages/packages-xml.md)
  - [설치 출처와 설치 시각 (Installer·Install Time)](02-artifacts/app-usage/packages/install-source-time.md)
  - [앱 권한 부여 기록 (Runtime Permissions)](02-artifacts/app-usage/packages/runtime-permissions.md)
- [앱 사용 기록 (usagestats)](02-artifacts/app-usage/usagestats/index.md)
  - [파일 구조 (usagestats)](02-artifacts/app-usage/usagestats/structure.md)
  - [이벤트 종류 (Event Types)](02-artifacts/app-usage/usagestats/event-types.md)
  - [해석 함정 (Pitfalls)](02-artifacts/app-usage/usagestats/pitfalls.md)
- [디지털 웰빙 (Digital Wellbeing)](02-artifacts/app-usage/digital-wellbeing.md)
- [배터리 사용 기록 (batterystats)](02-artifacts/app-usage/batterystats.md)
- [최근 앱 화면 (Recents·Snapshots)](02-artifacts/app-usage/recents-snapshots.md)
- [알림 기록 (Notification History)](02-artifacts/app-usage/notification-history.md)
- [앱 오류·종료 기록 (DropBox·tombstones·ANR)](02-artifacts/app-usage/crash-records.md)
- [구글 플레이 기록 (Play Store)](02-artifacts/app-usage/play-store.md)

### 통화·문자·연락처

- [통화 기록 (calllog.db)](02-artifacts/communications/call-log.md)
- [문자 (SMS·MMS·RCS)](02-artifacts/communications/messages/index.md)
  - [문자 DB 구조 (mmssms.db)](02-artifacts/communications/messages/mmssms-db.md)
  - [RCS 메시지 (RCS)](02-artifacts/communications/messages/rcs.md)
  - [삼성 메시지 앱 (Samsung Messages)](02-artifacts/communications/messages/samsung-messages.md)
- [연락처 (contacts2.db)](02-artifacts/communications/contacts.md)
- [통화 녹음과 음성 사서함 (Call Recording·Voicemail)](02-artifacts/communications/call-recording-voicemail.md)

### 사진·미디어

- [미디어 저장소 (MediaStore)](02-artifacts/media/mediastore/index.md)
  - [미디어 DB 구조 (external.db)](02-artifacts/media/mediastore/external-db.md)
  - [지운 사진의 흔적 (Deleted Media)](02-artifacts/media/mediastore/deleted-media.md)
- [카메라 사진과 메타데이터 (DCIM·EXIF)](02-artifacts/media/dcim-exif.md)
- [섬네일 캐시 (Thumbnails)](02-artifacts/media/thumbnails.md)
- [구글 포토 (Google Photos)](02-artifacts/media/google-photos.md)
- [삼성 갤러리 (Samsung Gallery)](02-artifacts/media/samsung-gallery.md)
- [스크린샷과 화면 녹화 (Screenshots·Screen Recording)](02-artifacts/media/screenshots.md)

### 위치

- [구글 위치 기록과 타임라인 (Timeline)](02-artifacts/location/google-timeline.md)
- [위치 캐시 (Cached Locations)](02-artifacts/location/cached-locations.md)
- [구글 지도 (Google Maps)](02-artifacts/location/google-maps.md)
- [네이버 지도 (NAVER Map)](02-artifacts/location/naver-map.md)
- [카카오맵 (KakaoMap)](02-artifacts/location/kakaomap.md)

### 네트워크·연결

- [와이파이 설정과 접속 기록 (WifiConfigStore)](02-artifacts/network/wifi.md)
- [블루투스 장치 (Bluetooth)](02-artifacts/network/bluetooth.md)
- [데이터 사용량 (netstats)](02-artifacts/network/netstats.md)
- [테더링과 핫스폿 (Tethering·Hotspot)](02-artifacts/network/tethering-hotspot.md)
- [VPN 설정 (VPN)](02-artifacts/network/vpn.md)
- [USB 연결 기록 (USB)](02-artifacts/network/usb.md)
- [파일 공유 (Quick Share·Nearby Share)](02-artifacts/network/quick-share.md)

### 인터넷·브라우저

- [크롬 (Chrome for Android)](02-artifacts/browsers/chrome/index.md)
  - [방문 기록 (History)](02-artifacts/browsers/chrome/history.md)
  - [탭과 세션 (Tabs·Sessions)](02-artifacts/browsers/chrome/tabs-sessions.md)
  - [다운로드 (Downloads)](02-artifacts/browsers/chrome/downloads.md)
  - [쿠키와 자동 완성 (Cookies·Autofill)](02-artifacts/browsers/chrome/cookies-autofill.md)
- [삼성 인터넷 (Samsung Internet)](02-artifacts/browsers/samsung-internet.md)
- [네이버 앱 (NAVER)](02-artifacts/browsers/naver.md)
- [그 밖의 브라우저 (웨일·파이어폭스)](02-artifacts/browsers/other-browsers.md)

### 메신저

- [카카오톡 (KakaoTalk)](02-artifacts/messengers/kakaotalk/index.md)
  - [저장 위치와 파일 (Paths·Files)](02-artifacts/messengers/kakaotalk/paths-files.md)
  - [대화 DB 구조와 암호화 (KakaoTalk.db)](02-artifacts/messengers/kakaotalk/chat-db.md)
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

### 메일·클라우드

- [지메일 (Gmail)](02-artifacts/mail-cloud/gmail.md)
- [삼성 이메일 (Samsung Email)](02-artifacts/mail-cloud/samsung-email.md)
- [구글 드라이브 (Google Drive)](02-artifacts/mail-cloud/google-drive.md)
- [삼성 클라우드와 원드라이브 (Samsung Cloud·OneDrive)](02-artifacts/mail-cloud/samsung-cloud-onedrive.md)
- [네이버 MYBOX (MYBOX)](02-artifacts/mail-cloud/mybox.md)
- [구글 백업 (Google Backup)](02-artifacts/mail-cloud/google-backup.md)

### 삼성 기기 전용

- [삼성 헬스 (Samsung Health)](02-artifacts/samsung/samsung-health.md)
- [빅스비 (Bixby)](02-artifacts/samsung/bixby.md)
- [엣지 패널 (Edge Panel)](02-artifacts/samsung/edge-panel.md)
- [삼성 키보드 입력 기록 (Samsung Keyboard)](02-artifacts/samsung/samsung-keyboard.md)

### 구글 입력·음성 비서

- [지보드 입력 기록 (Gboard)](02-artifacts/google-services/gboard.md)
- [구글 어시스턴트 기록 (Google Assistant)](02-artifacts/google-services/google-assistant.md)

### 로그

- [logcat (logcat)](02-artifacts/logs/logcat.md)
- [이벤트 로그 버퍼 (events)](02-artifacts/logs/events-buffer.md)
- [버그 리포트 (bugreport)](02-artifacts/logs/bugreport.md)
- [dumpsys 출력 (dumpsys)](02-artifacts/logs/dumpsys.md)

### 자격 증명·보안 설정

- [저장된 암호 (Google 비밀번호 관리자·Samsung Pass)](02-artifacts/credentials-security/saved-passwords.md)
- [기기 관리자와 접근성 권한 (Device Admin·Accessibility)](02-artifacts/credentials-security/device-admin-accessibility.md)
- [설치된 인증서 (User Certificates)](02-artifacts/credentials-security/user-certificates.md)

### 파일 내장 메타데이터

- [APK 정보 (AndroidManifest·서명)](02-artifacts/embedded-metadata/apk.md)
- [문서 메타데이터 (PDF·Office)](02-artifacts/embedded-metadata/documents.md)

## 분석 기법

### 조사 절차·증거 확보

- [조사 절차 (Investigation Process)](03-techniques/acquisition/investigation-process.md)
- [모바일 증거 확보 (Acquisition)](03-techniques/acquisition/mobile-acquisition/index.md)
  - [수집 방식 비교 (논리·파일 시스템·물리)](03-techniques/acquisition/mobile-acquisition/methods.md)
  - [압수와 보관 (전원·통신 차단)](03-techniques/acquisition/mobile-acquisition/seizure-handling.md)
  - [ADB로 볼 수 있는 것 (ADB)](03-techniques/acquisition/mobile-acquisition/adb.md)
  - [백업으로 수집 (Google 백업·Smart Switch)](03-techniques/acquisition/mobile-acquisition/backups.md)
  - [결과물 형식과 해시 (Extraction Formats·Hash)](03-techniques/acquisition/mobile-acquisition/formats-hash.md)
- [클라우드 데이터 (Google Takeout 등)](03-techniques/acquisition/cloud-data.md)

### 분석

- [앱 데이터 분석 (App Data Analysis)](03-techniques/analysis/app-data-analysis/index.md)
  - [처음 보는 앱 분석 순서 (Unknown Apps)](03-techniques/analysis/app-data-analysis/unknown-apps.md)
  - [캐시와 웹뷰 (Cache·WebView)](03-techniques/analysis/app-data-analysis/cache-webview.md)
  - [지운 앱이 남긴 흔적 (Uninstalled Apps)](03-techniques/analysis/app-data-analysis/uninstalled-apps.md)
- [타임라인 작성 (Timeline)](03-techniques/analysis/timeline/index.md)
  - [시각 정규화 (Time Normalization)](03-techniques/analysis/timeline/time-normalization.md)
  - [여러 기록 엮기 (Correlation)](03-techniques/analysis/timeline/correlation.md)
  - [시각 조작 흔적 (Time Manipulation)](03-techniques/analysis/timeline/time-manipulation.md)
- [삭제 데이터 복구 (Data Recovery)](03-techniques/analysis/data-recovery/index.md)
  - [SQLite 레코드 되살리기 (SQLite)](03-techniques/analysis/data-recovery/sqlite-records.md)
  - [파일 카빙 (Carving)](03-techniques/analysis/data-recovery/carving.md)
  - [TRIM과 암호화가 주는 한계 (TRIM·Encryption)](03-techniques/analysis/data-recovery/trim-encryption.md)
- [악성 앱 흔적 분석 (Malicious App Triage)](03-techniques/analysis/malicious-app-triage/index.md)
  - [권한과 설정으로 찾기 (Permissions·Settings)](03-techniques/analysis/malicious-app-triage/permissions-settings.md)
  - [감시 앱 흔적 (Stalkerware)](03-techniques/analysis/malicious-app-triage/stalkerware.md)
  - [APK 확인 (APK Check)](03-techniques/analysis/malicious-app-triage/apk-check.md)
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
  - [초기화 (Factory Reset)](04-scenarios/activity/anti-forensics/factory-reset.md)
  - [앱 지우기 (App Removal)](04-scenarios/activity/anti-forensics/app-removal.md)
  - [메시지·사진 지우기 (Content Deletion)](04-scenarios/activity/anti-forensics/content-deletion.md)
  - [시각 바꾸기 (Time Change)](04-scenarios/activity/anti-forensics/time-change.md)

### 정보 유출

- [자료를 밖으로 보냈나 (Data Exfiltration)](04-scenarios/exfiltration/data-exfiltration/index.md)
  - [메신저로 (Messenger)](04-scenarios/exfiltration/data-exfiltration/messenger.md)
  - [클라우드로 (Cloud)](04-scenarios/exfiltration/data-exfiltration/cloud.md)
  - [메일로 (Email)](04-scenarios/exfiltration/data-exfiltration/email.md)
  - [PC 연결로 (USB·PC)](04-scenarios/exfiltration/data-exfiltration/usb-pc.md)
  - [근거리 공유로 (Quick Share·Bluetooth)](04-scenarios/exfiltration/data-exfiltration/nearby-share.md)

### 침해 사고

- [악성 앱은 어디서 들어왔나 (Initial Access)](04-scenarios/incident/initial-access.md)
- [몰래 설치된 감시 앱 (Stalkerware)](04-scenarios/incident/stalkerware.md)
- [스미싱 흔적 (Smishing)](04-scenarios/incident/smishing.md)
- [계정 탈취 흔적 (Account Takeover)](04-scenarios/incident/account-takeover.md)
