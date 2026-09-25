---
title: 처음
nav_order: -100
permalink: /
---

# macOS 디지털 포렌식 핸드북

macOS 시스템에 남는 흔적을 어떻게 읽고 해석하는지 정리한 한국어 핸드북입니다. 포렌식을 공부하는 사람과 현업에서 사건을 분석하는 사람을 위해 작성했습니다.

아티팩트가 어디에 있는지뿐만 아니라 그 기록이 왜 생기는지, 무엇을 증명하고 무엇은 증명하지 못하는지까지 설명합니다. 보고서에 어떻게 쓸 수 있는지도 함께 다룹니다.

## 구성

핸드북은 네 갈래로 나뉩니다.

| 갈래 | 다루는 것 |
|---|---|
| **기반 구조** | APFS·plist·SQLite·통합 로그·키체인 같은 저장 형식. 여러 아티팩트가 이 형식 위에 기록됩니다 |
| **아티팩트 사전** | FSEvents·KnowledgeC·바이옴·스포트라이트·격리 속성·TCC·사파리·메시지 등 아티팩트마다 한 페이지 |
| **분석 기법** | 증거 확보·라이브 대응·타임라인·메모리 분석·삭제 데이터 복구·암호화된 증거·악성 코드 흔적·보고서 작성 |
| **조사 시나리오** | "자료를 밖으로 빼돌렸나" 같은 질문 하나에 여러 아티팩트를 엮어 답하는 흐름 |

큰 주제는 허브 페이지에서 전체를 보여 주고, 하위 페이지에서 하나씩 자세히 다룹니다.

## 페이지 구성

아티팩트 페이지는 대체로 아래 순서로 씁니다.

1. 무엇을 기록하고, 그 기록이 왜 생기는지
2. 파일 위치와 macOS 버전마다 다른 점
3. 구조 — 표와 칸 이름, plist 키
4. 증거로 쓸 때 — 증명할 수 있는 것과 없는 것
5. 시각 읽기 — 언제 바뀌는지, 어떤 기준 시각을 쓰는지
6. 함정과 한계 — 자주 하는 오해, 지우거나 조작했을 때 남는 흔적
7. 직접 분석하기 — 파일을 직접 열어 한 번, 공개 도구로 한 번
8. 함께 볼 아티팩트 — 다른 기록과 맞춰 보기
9. 실습 질문과 참고 자료

## 읽는 법

- 처음이라면 기반 구조의 [APFS](01-foundations/disk-volume/apfs/index.md)와 [속성 목록 파일](01-foundations/data-formats/plist/index.md)부터 읽기를 권합니다.
- 사건을 앞에 두고 있다면 조사 시나리오에서 질문을 고르고, 거기서 필요한 아티팩트로 넘어가면 됩니다. 예: [어떤 앱을 언제 썼나](04-scenarios/activity/app-usage.md), [자료를 밖으로 빼돌렸나](04-scenarios/exfiltration/data-exfiltration/index.md), [원격 접속 침입 확인](04-scenarios/incident/remote-intrusion.md)
- 특정 아티팩트만 궁금하다면 아래 목차에서 바로 찾으면 됩니다.

## 표기

- 명세나 공식 문서로 확인한 사실은 그대로 씁니다.
- 판에 따라 달라지는 것은 그 자리에 판을 적습니다.
- 확인되지 않은 것은 쓰지 않습니다. 버전·기기마다 다를 수 있는 것은 분석가가 직접 확인하는 방법을 적습니다.
- 헥스 예시는 명세를 보고 만든 예시입니다. 실제 검체에서 나온 값이 아닙니다.
- 용어는 처음 나올 때 "한국어 (English)"로 한 번 적습니다.

# 목차


## 기반 구조

### 디스크·볼륨

- [APFS 구조 (APFS)](01-foundations/disk-volume/apfs/index.md)
  - [컨테이너와 볼륨 (Container·Volume)](01-foundations/disk-volume/apfs/container-volume.md)
  - [객체와 체크포인트 (Object·Checkpoint)](01-foundations/disk-volume/apfs/object-checkpoint.md)
  - [파일 시스템 트리와 아이노드 (FS Tree·Inode)](01-foundations/disk-volume/apfs/fs-tree-inode.md)
  - [APFS의 시각 네 가지 (Create·Modify·Change·Access)](01-foundations/disk-volume/apfs/timestamps.md)
  - [확장 속성 (Extended Attributes)](01-foundations/disk-volume/apfs/extended-attributes.md)
  - [스냅숏 (Snapshots)](01-foundations/disk-volume/apfs/snapshots.md)
  - [복제·희소·압축 파일 (Clone·Sparse·Compression)](01-foundations/disk-volume/apfs/clone-sparse-compression.md)
  - [지운 파일과 옛 체크포인트 (Deleted Files·Old Checkpoints)](01-foundations/disk-volume/apfs/deleted-files.md)
- [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](01-foundations/disk-volume/volume-group-firmlinks.md)
- [HFS+ 구조 (HFS+)](01-foundations/disk-volume/hfs-plus.md)
- [파티션 구조 (GPT·APFS 파티션)](01-foundations/disk-volume/gpt-partitions.md)
- [디스크 이미지 형식 (DMG·Sparsebundle)](01-foundations/disk-volume/dmg-sparsebundle.md)

### 데이터 저장 형식

- [속성 목록 파일 (Property List)](01-foundations/data-formats/plist/index.md)
  - [XML·바이너리 plist (XML·bplist00)](01-foundations/data-formats/plist/xml-binary.md)
  - [NSKeyedArchiver 풀기 (NSKeyedArchiver)](01-foundations/data-formats/plist/nskeyedarchiver.md)
  - [기본 설정 도메인과 캐시 (Defaults·cfprefsd)](01-foundations/data-formats/plist/defaults-cfprefsd.md)
- [SQLite 데이터베이스 (SQLite)](01-foundations/data-formats/sqlite/index.md)
  - [페이지와 레코드 (B-tree·Record)](01-foundations/data-formats/sqlite/b-tree-record.md)
  - [WAL과 저널 (WAL·Journal)](01-foundations/data-formats/sqlite/wal-journal.md)
  - [지운 레코드 되살리기 (Freelist·Freeblock)](01-foundations/data-formats/sqlite/freelist-freeblock.md)
  - [Core Data 저장소 (Core Data)](01-foundations/data-formats/sqlite/core-data.md)
- [통합 로그 형식 (Unified Log)](01-foundations/data-formats/unified-log/index.md)
  - [tracev3 파일 구조 (tracev3)](01-foundations/data-formats/unified-log/tracev3.md)
  - [UUID 텍스트와 공유 캐시 (uuidtext·dsc)](01-foundations/data-formats/unified-log/uuidtext-dsc.md)
  - [보관 기간과 로그 수준 (Persist·Info·Debug)](01-foundations/data-formats/unified-log/retention-levels.md)
  - [로그 아카이브 만들고 읽기 (logarchive)](01-foundations/data-formats/unified-log/logarchive.md)
- [예전 시스템 로그 (ASL·syslog)](01-foundations/data-formats/asl-syslog.md)
- [SEGB 형식 (SEGB)](01-foundations/data-formats/segb.md)
- [LevelDB와 IndexedDB (LevelDB·IndexedDB)](01-foundations/data-formats/leveldb-indexeddb.md)

### 값 읽는 법

- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](01-foundations/value-decoding/mac-time-values.md)
- [식별자 읽기 (UUID·UID·GUID)](01-foundations/value-decoding/uuid-uid.md)
- [번들 ID와 팀 ID (Bundle ID·Team ID)](01-foundations/value-decoding/bundle-team-id.md)
- [파일 참조 데이터 (Alias·Bookmark)](01-foundations/value-decoding/alias-bookmark.md)
- [유니코드 정규화 (NFD·NFC)](01-foundations/value-decoding/unicode-normalization.md)
- [압축 형식 (LZFSE·LZ4·zlib)](01-foundations/value-decoding/compression.md)

### 보안·보호

- [파일볼트 (FileVault)](01-foundations/protection/filevault/index.md)
  - [키 계층 (VEK·KEK)](01-foundations/protection/filevault/key-hierarchy.md)
  - [복구 키 (Recovery Key)](01-foundations/protection/filevault/recovery-key.md)
  - [보안 칩과 데이터 보호 (T2·Apple Silicon·Secure Enclave)](01-foundations/protection/filevault/secure-enclave.md)
- [키체인 (Keychain)](01-foundations/protection/keychain/index.md)
  - [로그인 키체인 파일 (login.keychain-db)](01-foundations/protection/keychain/login-keychain.md)
  - [시스템·로컬 항목 키체인 (System·Local Items)](01-foundations/protection/keychain/system-local-items.md)
  - [항목과 접근 제어 (Items·ACL)](01-foundations/protection/keychain/items-acl.md)
- [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](01-foundations/protection/codesign-notarization-sip.md)

## 아티팩트 사전

### 시스템·계정

- [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](02-artifacts/system-account/os-version-install-history.md)
- [컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](02-artifacts/system-account/computer-name-hardware.md)
- [시간대와 시계 설정 (Time Zone·NTP)](02-artifacts/system-account/time-zone.md)
- [사용자 계정 (Local Accounts)](02-artifacts/system-account/user-accounts/index.md)
  - [계정 plist 구조 (dslocal)](02-artifacts/system-account/user-accounts/dslocal-plist.md)
  - [암호 해시 (ShadowHashData)](02-artifacts/system-account/user-accounts/shadowhashdata.md)
  - [관리자와 그룹 소속 (admin·Groups)](02-artifacts/system-account/user-accounts/admin-groups.md)
  - [지운 계정의 흔적 (Deleted Accounts)](02-artifacts/system-account/user-accounts/deleted-accounts.md)
- [로그인 창 설정 (loginwindow)](02-artifacts/system-account/loginwindow.md)
- [설치한 앱과 영수증 (Applications·Receipts)](02-artifacts/system-account/installed-apps-receipts.md)
- [소프트웨어 업데이트 기록 (Software Update)](02-artifacts/system-account/software-update.md)

### 자동 실행·지속성

- [실행 에이전트·데몬 (LaunchAgents·LaunchDaemons)](02-artifacts/persistence/launchd/index.md)
  - [위치와 적용 범위 (Locations)](02-artifacts/persistence/launchd/locations.md)
  - [plist 키 해석 (ProgramArguments·RunAtLoad·KeepAlive)](02-artifacts/persistence/launchd/plist-keys.md)
  - [백그라운드 작업 관리 (BTM·Background Items)](02-artifacts/persistence/launchd/background-task-management.md)
- [로그인 항목 (Login Items)](02-artifacts/persistence/login-items.md)
- [예약 작업 (cron·periodic)](02-artifacts/persistence/cron-periodic.md)
- [셸 시작 파일 (zshrc·bash_profile)](02-artifacts/persistence/shell-startup-files.md)
- [커널·시스템 확장 (KEXT·System Extension)](02-artifacts/persistence/kext-system-extension.md)
- [구성 프로파일 (Configuration Profiles·MDM)](02-artifacts/persistence/configuration-profiles.md)
- [그 밖의 지속성 위치 (Login Hook·Authorization Plugin·Emond)](02-artifacts/persistence/other-persistence.md)

### 프로그램 실행 흔적

- [KnowledgeC (knowledgeC.db)](02-artifacts/execution/knowledgec/index.md)
  - [표와 스트림 구조 (ZOBJECT·Stream)](02-artifacts/execution/knowledgec/structure.md)
  - [앱 사용 기록 (App Usage)](02-artifacts/execution/knowledgec/app-usage.md)
  - [화면·잠금 상태 (Display·Device Lock)](02-artifacts/execution/knowledgec/device-state.md)
- [바이옴 (Biome)](02-artifacts/execution/biome/index.md)
  - [저장 위치와 스트림 (Streams)](02-artifacts/execution/biome/streams.md)
  - [앱 사용 스트림 (App.InFocus)](02-artifacts/execution/biome/app-infocus.md)
- [화면 사용 시간 (Screen Time)](02-artifacts/execution/screen-time.md)
- [실행 정책 평가 기록 (ExecPolicy·Gatekeeper)](02-artifacts/execution/execpolicy-gatekeeper.md)
- [충돌·진단 보고서 (DiagnosticReports)](02-artifacts/execution/diagnostic-reports.md)
- [전원 로그 (PowerLog)](02-artifacts/execution/powerlog.md)
- [터미널 명령 기록 (zsh_history·bash_sessions)](02-artifacts/execution/shell-history.md)
- [통합 로그의 프로세스 실행 기록 (Process Events)](02-artifacts/execution/unified-log-process.md)

### 파일·폴더 사용 흔적

- [최근 항목 (Shared File Lists)](02-artifacts/file-folder-usage/recent-items/index.md)
  - [파일 형식 (SFL2·SFL3)](02-artifacts/file-folder-usage/recent-items/sfl-format.md)
  - [앱별 최근 문서 (Recent Documents)](02-artifacts/file-folder-usage/recent-items/app-recent-documents.md)
  - [최근 앱·서버·폴더 (Recent Apps·Servers)](02-artifacts/file-folder-usage/recent-items/recent-apps-servers.md)
- [스포트라이트 (Spotlight)](02-artifacts/file-folder-usage/spotlight/index.md)
  - [색인 저장소 구조 (.Spotlight-V100·store.db)](02-artifacts/file-folder-usage/spotlight/store-structure.md)
  - [메타데이터 속성 (kMDItem)](02-artifacts/file-folder-usage/spotlight/metadata-attributes.md)
  - [검색 기록 (Spotlight Shortcuts)](02-artifacts/file-folder-usage/spotlight/search-history.md)
- [파인더 설정과 기록 (Finder plist)](02-artifacts/file-folder-usage/finder-plist.md)
- [폴더 보기 파일 (.DS_Store)](02-artifacts/file-folder-usage/ds-store.md)
- [휴지통 (.Trash)](02-artifacts/file-folder-usage/trash.md)
- [문서 버전 (DocumentRevisions-V100)](02-artifacts/file-folder-usage/document-revisions.md)
- [앱 저장 상태 (Saved Application State)](02-artifacts/file-folder-usage/saved-application-state.md)
- [빠른 보기 섬네일 캐시 (QuickLook)](02-artifacts/file-folder-usage/quicklook-thumbnails.md)

### 파일 시스템

- [파일 시스템 이벤트 (FSEvents)](02-artifacts/filesystem/fsevents/index.md)
  - [파일 형식 (.fseventsd)](02-artifacts/filesystem/fsevents/format.md)
  - [이벤트 플래그 읽기 (Flags)](02-artifacts/filesystem/fsevents/flags.md)
  - [해석 함정 (Pitfalls)](02-artifacts/filesystem/fsevents/pitfalls.md)
- [격리 속성과 다운로드 기록 (Quarantine)](02-artifacts/filesystem/quarantine/index.md)
  - [격리 확장 속성 (com.apple.quarantine)](02-artifacts/filesystem/quarantine/quarantine-xattr.md)
  - [격리 이벤트 DB (QuarantineEventsV2)](02-artifacts/filesystem/quarantine/quarantine-events-db.md)
- [다운로드 출처 속성 (kMDItemWhereFroms)](02-artifacts/filesystem/where-froms.md)
- [타임 머신 (Time Machine)](02-artifacts/filesystem/time-machine/index.md)
  - [백업 저장소 구조 (Backup Store)](02-artifacts/filesystem/time-machine/backup-store.md)
  - [백업 설정과 기록 (Settings·Logs)](02-artifacts/filesystem/time-machine/settings-logs.md)

### 외부 장치

- [USB 저장 장치 (USB Storage)](02-artifacts/external-devices/usb/index.md)
  - [통합 로그의 연결 기록 (Unified Log)](02-artifacts/external-devices/usb/unified-log.md)
  - [마운트 기록 (DiskArbitration)](02-artifacts/external-devices/usb/mount-records.md)
  - [볼륨 UUID로 장치 잇기 (Volume UUID)](02-artifacts/external-devices/usb/volume-uuid.md)
- [블루투스 장치 (Bluetooth)](02-artifacts/external-devices/bluetooth.md)
- [아이폰·아이패드 연결 (iOS Devices)](02-artifacts/external-devices/ios-devices/index.md)
  - [페어링 기록 (Lockdown)](02-artifacts/external-devices/ios-devices/lockdown.md)
  - [기기 백업 (MobileSync)](02-artifacts/external-devices/ios-devices/mobilesync.md)
- [에어드롭 (AirDrop)](02-artifacts/external-devices/airdrop.md)
- [인쇄 기록 (CUPS)](02-artifacts/external-devices/cups-printing.md)

### 인터넷·브라우저

- [사파리 (Safari)](02-artifacts/browsers/safari/index.md)
  - [방문 기록 (History.db)](02-artifacts/browsers/safari/history.md)
  - [다운로드 (Downloads.plist)](02-artifacts/browsers/safari/downloads.md)
  - [북마크와 읽기 목록 (Bookmarks·Reading List)](02-artifacts/browsers/safari/bookmarks.md)
  - [탭과 세션 (Tabs·Sessions)](02-artifacts/browsers/safari/tabs-sessions.md)
  - [캐시와 웹 데이터 (Cache·WebKit)](02-artifacts/browsers/safari/cache-webkit.md)
  - [확장 (Safari Extensions)](02-artifacts/browsers/safari/extensions.md)
  - [개인 정보 보호 브라우징 (Private Browsing)](02-artifacts/browsers/safari/private-browsing.md)
- [크롬·엣지·웨일 (Chromium 계열)](02-artifacts/browsers/chromium/index.md)
  - [맥에서의 위치와 프로필 (Profiles)](02-artifacts/browsers/chromium/profiles.md)
  - [방문·다운로드 기록 (History)](02-artifacts/browsers/chromium/history-downloads.md)
  - [쿠키와 저장된 암호 (Cookies·Login Data)](02-artifacts/browsers/chromium/cookies-login-data.md)
  - [확장 (Extensions)](02-artifacts/browsers/chromium/extensions.md)
- [파이어폭스 (Firefox)](02-artifacts/browsers/firefox.md)

### 메일

- [애플 메일 (Apple Mail)](02-artifacts/mail/apple-mail/index.md)
  - [저장 구조 (emlx·V10)](02-artifacts/mail/apple-mail/storage.md)
  - [메일 색인 DB (Envelope Index)](02-artifacts/mail/apple-mail/envelope-index.md)
  - [첨부 파일 (Attachments)](02-artifacts/mail/apple-mail/attachments.md)
- [아웃룩 (Outlook for Mac)](02-artifacts/mail/outlook.md)
- [썬더버드 (Thunderbird)](02-artifacts/mail/thunderbird.md)

### 메시지·메신저

- [메시지 (iMessage·SMS)](02-artifacts/messengers/imessage/index.md)
  - [대화 DB (chat.db)](02-artifacts/messengers/imessage/chat-db.md)
  - [첨부 파일 (Attachments)](02-artifacts/messengers/imessage/attachments.md)
  - [지운 메시지의 흔적 (Deleted Messages)](02-artifacts/messengers/imessage/deleted-messages.md)
- [페이스타임과 통화 기록 (FaceTime·CallHistory)](02-artifacts/messengers/facetime-callhistory.md)
- [카카오톡 맥 (KakaoTalk)](02-artifacts/messengers/kakaotalk.md)
- [텔레그램 (Telegram)](02-artifacts/messengers/telegram.md)
- [슬랙 (Slack)](02-artifacts/messengers/slack.md)
- [팀즈 (Microsoft Teams)](02-artifacts/messengers/teams.md)
- [디스코드 (Discord)](02-artifacts/messengers/discord.md)
- [위챗 (WeChat)](02-artifacts/messengers/wechat.md)
- [라인 (LINE)](02-artifacts/messengers/line.md)
- [왓츠앱 (WhatsApp)](02-artifacts/messengers/whatsapp.md)
- [시그널 (Signal)](02-artifacts/messengers/signal.md)
- [줌 (Zoom)](02-artifacts/messengers/zoom.md)

### 클라우드·애플 앱

- [아이클라우드 계정 (iCloud Account)](02-artifacts/cloud-apps/icloud-account.md)
- [아이클라우드 드라이브 (iCloud Drive·CloudDocs)](02-artifacts/cloud-apps/icloud-drive.md)
- [파일 공급자 (File Provider)](02-artifacts/cloud-apps/file-provider.md)
- [연속성과 유니버설 클립보드 (Continuity·Handoff)](02-artifacts/cloud-apps/continuity.md)
- [드롭박스 (Dropbox)](02-artifacts/cloud-apps/dropbox.md)
- [원드라이브 (OneDrive)](02-artifacts/cloud-apps/onedrive.md)
- [구글 드라이브 (Google Drive)](02-artifacts/cloud-apps/google-drive.md)
- [메모 (Notes)](02-artifacts/cloud-apps/notes.md)
- [미리 알림과 캘린더 (Reminders·Calendar)](02-artifacts/cloud-apps/reminders-calendar.md)
- [연락처 (Contacts)](02-artifacts/cloud-apps/contacts.md)
- [사진 보관함 (Photos Library)](02-artifacts/cloud-apps/photos-library.md)

### 네트워크

- [와이파이 기록 (Wi-Fi)](02-artifacts/network/wifi.md)
- [네트워크 인터페이스와 설정 (SystemConfiguration)](02-artifacts/network/network-interfaces.md)
- [앱별 네트워크 사용량 (netusage)](02-artifacts/network/netusage.md)
- [원격 접속 (Remote Access)](02-artifacts/network/remote-access/index.md)
  - [화면 공유와 원격 관리 (Screen Sharing·ARD)](02-artifacts/network/remote-access/screen-sharing-ard.md)
  - [SSH 접속 기록 (SSH)](02-artifacts/network/remote-access/ssh.md)
  - [원격 제어 앱 (TeamViewer·AnyDesk)](02-artifacts/network/remote-access/third-party-tools.md)
- [방화벽 (Application Firewall)](02-artifacts/network/application-firewall.md)
- [VPN 구성 (VPN)](02-artifacts/network/vpn.md)
- [공유 폴더 연결 기록 (SMB·AFP)](02-artifacts/network/network-shares.md)
- [hosts와 DNS 설정 (hosts·DNS)](02-artifacts/network/hosts-dns.md)

### 로그

- [통합 로그에서 찾을 것 (Unified Log Events)](02-artifacts/logs/unified-log-events/index.md)
  - [로그인·로그아웃 (Login·Logout)](02-artifacts/logs/unified-log-events/login-logout.md)
  - [잠금·잠금 해제·잠자기 (Lock·Sleep)](02-artifacts/logs/unified-log-events/lock-sleep.md)
  - [관리자 권한 사용 (sudo·Authorization)](02-artifacts/logs/unified-log-events/sudo-authorization.md)
  - [원격 로그인 (Remote Login)](02-artifacts/logs/unified-log-events/remote-login.md)
  - [자주 쓰는 검색 조건 (Predicates)](02-artifacts/logs/unified-log-events/predicates.md)
- [설치 로그 (install.log)](02-artifacts/logs/install-log.md)
- [감사 로그 (OpenBSM Audit)](02-artifacts/logs/openbsm-audit.md)
- [전원·잠자기 기록 (pmset)](02-artifacts/logs/power-events.md)
- [보안 도구 기록 (XProtect)](02-artifacts/logs/xprotect.md)

### 자격 증명·권한

- [개인 정보 보호 권한 (TCC)](02-artifacts/credentials/tcc/index.md)
  - [권한 DB 구조 (TCC.db)](02-artifacts/credentials/tcc/tcc-db.md)
  - [권한 기록 해석 (Services·auth_value)](02-artifacts/credentials/tcc/interpretation.md)
  - [권한 변경 흔적 (Changes)](02-artifacts/credentials/tcc/changes.md)
- [SSH 키와 접속 목록 (SSH Keys·known_hosts)](02-artifacts/credentials/ssh-keys.md)
- [저장된 암호 (Passwords·iCloud Keychain)](02-artifacts/credentials/saved-passwords.md)

### 파일 내장 메타데이터

- [사진 메타데이터 (EXIF·HEIC)](02-artifacts/embedded-metadata/exif-heic.md)
- [문서 메타데이터 (iWork·Office)](02-artifacts/embedded-metadata/iwork-office.md)
- [앱 번들 정보 (Info.plist·Code Signature)](02-artifacts/embedded-metadata/app-bundle.md)

## 분석 기법

### 조사 절차·증거 확보

- [조사 절차 (Investigation Process)](03-techniques/process-acquisition/investigation-process.md)
- [맥 증거 확보 (Acquisition)](03-techniques/process-acquisition/evidence-acquisition/index.md)
  - [확보 방법 고르기 (T2·Apple Silicon)](03-techniques/process-acquisition/evidence-acquisition/choosing-method.md)
  - [논리 수집 (Logical Collection)](03-techniques/process-acquisition/evidence-acquisition/logical-collection.md)
  - [공유 모드와 대상 디스크 모드 (Share Disk·Target Disk Mode)](03-techniques/process-acquisition/evidence-acquisition/share-disk-target-disk.md)
  - [라이브 이미징 (Live Imaging)](03-techniques/process-acquisition/evidence-acquisition/live-imaging.md)
  - [해시와 증거 보관 (Hash·Chain of Custody)](03-techniques/process-acquisition/evidence-acquisition/hash-chain-of-custody.md)
- [라이브 대응 (Live Response)](03-techniques/process-acquisition/live-response/index.md)
  - [휘발성 순서 (Order of Volatility)](03-techniques/process-acquisition/live-response/order-of-volatility.md)
  - [프로세스와 열린 파일 (ps·lsof)](03-techniques/process-acquisition/live-response/processes-open-files.md)
  - [네트워크 연결 (Connections)](03-techniques/process-acquisition/live-response/connections.md)
  - [통합 로그 수집 (log collect)](03-techniques/process-acquisition/live-response/log-collect.md)
  - [전체 디스크 접근 권한 (Full Disk Access)](03-techniques/process-acquisition/live-response/full-disk-access.md)

### 분석

- [타임라인 작성 (Timeline)](03-techniques/analysis/timeline/index.md)
  - [파일 시스템 타임라인 (APFS·FSEvents)](03-techniques/analysis/timeline/filesystem-timeline.md)
  - [통합 로그 타임라인 (Unified Log)](03-techniques/analysis/timeline/unified-log-timeline.md)
  - [시각 정규화 (Time Normalization)](03-techniques/analysis/timeline/time-normalization.md)
  - [시각 조작 흔적 (Timestomping)](03-techniques/analysis/timeline/timestomping.md)
- [메모리 분석 (Memory Forensics)](03-techniques/analysis/memory-forensics/index.md)
  - [메모리 확보 (Acquisition)](03-techniques/analysis/memory-forensics/memory-acquisition.md)
  - [스왑과 잠자기 이미지 (swapfile·sleepimage)](03-techniques/analysis/memory-forensics/swap-sleepimage.md)
  - [분석 도구와 한계 (Tools·Limits)](03-techniques/analysis/memory-forensics/tools-limits.md)
- [삭제 데이터 복구 (Data Recovery)](03-techniques/analysis/data-recovery/index.md)
  - [APFS에서 지운 파일 (APFS)](03-techniques/analysis/data-recovery/apfs-deleted-files.md)
  - [SQLite 레코드 되살리기 (SQLite)](03-techniques/analysis/data-recovery/sqlite-records.md)
  - [카빙 (Carving)](03-techniques/analysis/data-recovery/carving.md)
  - [트림과 복구 한계 (TRIM)](03-techniques/analysis/data-recovery/trim.md)
- [암호화된 증거 다루기 (Encrypted Evidence)](03-techniques/analysis/encrypted-evidence/index.md)
  - [파일볼트 이미지 열기 (FileVault)](03-techniques/analysis/encrypted-evidence/filevault-images.md)
  - [암호 걸린 디스크 이미지 (Encrypted DMG)](03-techniques/analysis/encrypted-evidence/encrypted-dmg.md)
  - [키체인 풀기 (Keychain)](03-techniques/analysis/encrypted-evidence/keychain-decryption.md)
- [악성 코드 흔적 분석 (Malware Triage)](03-techniques/analysis/malware-triage/index.md)
  - [서명과 공증 확인 (codesign·spctl)](03-techniques/analysis/malware-triage/codesign-check.md)
  - [지속성 전수 조사 (Persistence Sweep)](03-techniques/analysis/malware-triage/persistence-sweep.md)
  - [규칙으로 찾기 (YARA·XProtect)](03-techniques/analysis/malware-triage/yara-xprotect.md)
- [콘텐츠 검색 (Content Search)](03-techniques/analysis/content-search.md)
- [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](03-techniques/analysis/snapshot-diff.md)

### 보고

- [포렌식 보고서 (Forensic Report)](03-techniques/reporting/forensic-report.md)
- [도구 검증 (Tool Validation)](03-techniques/reporting/tool-validation.md)

## 조사 시나리오

### 행위 재구성

- [어떤 앱을 언제 썼나 (App Usage)](04-scenarios/activity/app-usage.md)
- [이 파일을 누가 언제 열었나 (File Access)](04-scenarios/activity/file-access.md)
- [이 파일은 어디서 왔나 (File Origin)](04-scenarios/activity/file-origin.md)
- [지운 파일의 흔적 찾기 (Deleted File Traces)](04-scenarios/activity/deleted-file-traces.md)
- [웹 사용 행위 재구성 (Web Activity)](04-scenarios/activity/web-activity.md)
- [개인 정보 보호 브라우징으로 무엇을 했나 (Private Browsing)](04-scenarios/activity/private-browsing.md)
- [누구와 연락을 주고받았나 (Communication)](04-scenarios/activity/communication.md)
- [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](04-scenarios/activity/usage-time.md)
- [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](04-scenarios/activity/user-attribution.md)
- [이 문서의 날짜를 믿을 수 있나 (Document Date)](04-scenarios/activity/document-date.md)
- [증거를 없애려 했나 (Anti-Forensics)](04-scenarios/activity/anti-forensics/index.md)
  - [로그 지우기 (Log Clearing)](04-scenarios/activity/anti-forensics/log-clearing.md)
  - [시스템 시각 바꾸기 (Time Change)](04-scenarios/activity/anti-forensics/time-change.md)
  - [초기화·재설치 (Erase·Reinstall)](04-scenarios/activity/anti-forensics/erase-reinstall.md)
  - [삭제 도구 (Wiping Tools)](04-scenarios/activity/anti-forensics/wiping-tools.md)

### 정보 유출

- [자료를 밖으로 빼돌렸나 (Data Exfiltration)](04-scenarios/exfiltration/data-exfiltration/index.md)
  - [USB 저장 장치로 (USB)](04-scenarios/exfiltration/data-exfiltration/usb.md)
  - [에어드롭으로 (AirDrop)](04-scenarios/exfiltration/data-exfiltration/airdrop.md)
  - [클라우드로 (Cloud)](04-scenarios/exfiltration/data-exfiltration/cloud.md)
  - [메일로 (Email)](04-scenarios/exfiltration/data-exfiltration/email.md)
  - [메신저로 (Messenger)](04-scenarios/exfiltration/data-exfiltration/messenger.md)
  - [웹 업로드로 (Web Upload)](04-scenarios/exfiltration/data-exfiltration/web-upload.md)
  - [아이폰으로 (iPhone)](04-scenarios/exfiltration/data-exfiltration/iphone.md)
  - [인쇄로 (Print)](04-scenarios/exfiltration/data-exfiltration/print.md)
- [개인정보 파일이 어디 있고 밖으로 나갔나 (PII Exposure)](04-scenarios/exfiltration/pii-exposure.md)

### 침해 사고

- [악성 코드는 어디서 들어왔나 (Initial Access)](04-scenarios/incident/initial-access.md)
- [악성 코드 지속성 찾기 (Persistence)](04-scenarios/incident/persistence.md)
- [원격 접속 침입 확인 (Remote Intrusion)](04-scenarios/incident/remote-intrusion.md)
- [정보 탈취 악성 코드 (Infostealer)](04-scenarios/incident/infostealer.md)
- [권한 상승과 TCC 우회 흔적 (Privilege·TCC Bypass)](04-scenarios/incident/privilege-tcc-bypass.md)
