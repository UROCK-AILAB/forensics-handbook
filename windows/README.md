---
title: Windows 개요
nav_order: -100
permalink: /
---

# Windows 디지털 포렌식 핸드북

Windows 시스템에 남는 흔적을 어떻게 읽고 해석하는지 정리한 한국어 핸드북입니다.

## 구성

핸드북은 네 부분으로 나뉩니다.

| 부분 | 다루는 것 |
|---|---|
| **기반 구조** | NTFS·레지스트리 하이브·ESE·SQLite·EVTX 같은 저장 형식. 여러 아티팩트가 이 형식 위에 기록됩니다 |
| **아티팩트 사전** | 프리페치·AmCache·SRUM·셸백·USB·브라우저·메신저·이벤트 로그 등 아티팩트마다 한 페이지 |
| **분석 기법** | 증거 수집·라이브 대응·메모리 분석·타임라인·삭제 데이터 복구·암호화된 증거·해시와 YARA·Sigma·보고서 작성 |
| **조사 시나리오** | "자료를 밖으로 빼돌렸나" 같은 질문 하나에 여러 아티팩트를 엮어 답하는 흐름 |

큰 주제는 허브 페이지에서 전체를 보여 주고, 하위 페이지에서 하나씩 자세히 다룹니다.

## 페이지 구성

아티팩트 페이지는 대체로 아래 순서로 씁니다.

1. 무엇을 기록하고, 그 기록이 왜 생기는지
2. 파일 위치와 Windows 버전마다 다른 점
3. 구조 — 표와 열 이름, 오프셋
4. 증거로 쓸 때 — 증명할 수 있는 것과 없는 것
5. 시각 읽기 — 언제 바뀌는지, UTC인지 현지 시각인지
6. 함정과 한계 — 자주 하는 오해, 지우거나 조작했을 때 남는 흔적
7. 직접 분석하기 — 헥스로 한 번, 공개 도구로 한 번
8. 함께 볼 아티팩트 — 다른 기록과 맞춰 보기
9. 실습 질문과 참고 자료

## 읽는 법

- 처음이라면 기반 구조의 [NTFS](01-foundations/disk-volume/ntfs/index.md)와 [레지스트리 하이브](01-foundations/database-log-formats/registry-hive/index.md)부터 읽기를 권합니다.
- 사건을 앞에 두고 있다면 조사 시나리오에서 질문을 고르고, 거기서 필요한 아티팩트로 넘어가면 됩니다. 예: [어떤 프로그램을 언제 실행했나](04-scenarios/activity/program-execution.md), [자료를 밖으로 빼돌렸나](04-scenarios/exfiltration/data-exfiltration/index.md), [원격 데스크톱 침입 확인](04-scenarios/incident/rdp-intrusion.md)
- 특정 아티팩트만 궁금하다면 아래 목차에서 바로 찾으면 됩니다.

## 표기

- 명세나 공식 문서로 확인한 사실은 그대로 씁니다.
- 기기에서 본 내용은 Windows 11 25H2 기준입니다. 다른 판에서 달라지는 것은 그 자리에 판을 적습니다.
- 확인되지 않은 것은 쓰지 않습니다. 버전·기기마다 다를 수 있는 것은 분석가가 직접 확인하는 방법을 적습니다.
- 헥스 예시는 명세를 보고 만든 예시입니다. 실제 데이터에서 나온 값이 아닙니다.
- 용어는 처음 나올 때 "한국어 (English)"로 한 번 적습니다.

# 목차

## 기반 구조

### 디스크·볼륨

- [증거 이미지·가상 디스크 형식 (E01·RAW·AFF4·VHDX·VMDK)](01-foundations/disk-volume/e01-raw-aff4-vhdx-vmdk.md)
- [파티션 구조 (MBR·GPT)](01-foundations/disk-volume/mbr-gpt.md)
- [NTFS 구조 (NTFS)](01-foundations/disk-volume/ntfs/index.md)
  - [부트 섹터와 클러스터 (Boot Sector·Cluster)](01-foundations/disk-volume/ntfs/boot-sector-cluster.md)
  - [MFT 레코드와 속성 (FILE Record·Attribute)](01-foundations/disk-volume/ntfs/file-record-attribute.md)
  - [데이터 런과 상주·비상주 데이터 (Data Run·Resident·Non-resident)](01-foundations/disk-volume/ntfs/data-run-resident-non-resident.md)
  - [두 벌의 시각 ($STANDARD_INFORMATION·$FILE_NAME)](01-foundations/disk-volume/ntfs/standard-information-file-name.md)
  - [대체 데이터 스트림 (ADS)](01-foundations/disk-volume/ntfs/ads.md)
  - [압축·희소 파일 (Compressed·Sparse)](01-foundations/disk-volume/ntfs/compressed-sparse.md)
  - [링크와 리파스 포인트 (Hard Link·Junction·Reparse Point)](01-foundations/disk-volume/ntfs/hard-link-junction-reparse-point.md)
  - [NTFS 메타 파일 ($Bitmap·$Secure·$Extend)](01-foundations/disk-volume/ntfs/bitmap-secure-extend.md)
- [FAT·exFAT 구조 (FAT·exFAT)](01-foundations/disk-volume/fat-exfat.md)
- [볼륨 섀도 복사본 구조 (Volume Shadow Copy)](01-foundations/disk-volume/volume-shadow-copy.md)

### 데이터베이스·로그 형식

- [레지스트리 하이브 구조 (Registry Hive)](01-foundations/database-log-formats/registry-hive/index.md)
  - [하이브 파일 종류와 위치 (SYSTEM·SOFTWARE·SAM·SECURITY·NTUSER.DAT·UsrClass.dat)](01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md)
  - [하이브 내부 구조 (regf·hbin·Cell)](01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)
  - [키 마지막 기록 시각 (Last Write Time)](01-foundations/database-log-formats/registry-hive/last-write-time.md)
  - [트랜잭션 로그와 반영 안 된 변경 (.LOG1·.LOG2)](01-foundations/database-log-formats/registry-hive/log1-log2.md)
  - [지워진 키·값 복구 (Deleted Keys·Values)](01-foundations/database-log-formats/registry-hive/deleted-keys-values.md)
  - [컨트롤셋 고르기 (ControlSet·Select)](01-foundations/database-log-formats/registry-hive/controlset-select.md)
  - [MRU 목록 읽는 법 (MRUList·MRUListEx)](01-foundations/database-log-formats/registry-hive/mrulist-mrulistex.md)
- [ESE 데이터베이스 (Extensible Storage Engine)](01-foundations/database-log-formats/extensible-storage-engine/index.md)
  - [파일 구조 (Page·B+Tree·Catalog)](01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md)
  - [트랜잭션 로그와 비정상 종료 상태 (edb.log·Dirty Shutdown)](01-foundations/database-log-formats/extensible-storage-engine/edb-log-dirty-shutdown.md)
  - [긴 값과 압축 열 (Long Value·Compressed Column)](01-foundations/database-log-formats/extensible-storage-engine/long-value-compressed-column.md)
  - [파일 안에 남은 지운 레코드 (Deleted Records)](01-foundations/database-log-formats/extensible-storage-engine/deleted-records.md)
- [SQLite 데이터베이스 (SQLite)](01-foundations/database-log-formats/sqlite/index.md)
  - [파일·페이지 구조 (B-tree·Record Format)](01-foundations/database-log-formats/sqlite/b-tree-record-format.md)
  - [WAL과 롤백 저널 (-wal·-journal·-shm)](01-foundations/database-log-formats/sqlite/wal-journal-shm.md)
  - [파일 안에 남은 지운 레코드 (Freelist·Freeblock)](01-foundations/database-log-formats/sqlite/freelist-freeblock.md)
  - [암호화된 SQLite (SQLCipher)](01-foundations/database-log-formats/sqlite/sqlcipher.md)
- [LevelDB 저장소 (LevelDB)](01-foundations/database-log-formats/leveldb.md)
- [이벤트 로그 형식 (EVTX·EVT·ETL)](01-foundations/database-log-formats/evtx-evt-etl/index.md)
  - [EVTX 파일 구조 (File Header·Chunk·Record)](01-foundations/database-log-formats/evtx-evt-etl/file-header-chunk-record.md)
  - [이진 XML 해석 (Binary XML·Template)](01-foundations/database-log-formats/evtx-evt-etl/binary-xml-template.md)
  - [공급자와 메시지 파일 (Provider·Message Table)](01-foundations/database-log-formats/evtx-evt-etl/provider-message-table.md)
  - [구형 EVT 형식 (Windows XP·2003)](01-foundations/database-log-formats/evtx-evt-etl/windows-xp-2003.md)
  - [파일 안에 남은 지운·손상 레코드 (Chunk Slack·Corrupted EVTX)](01-foundations/database-log-formats/evtx-evt-etl/chunk-slack-corrupted-evtx.md)
  - [ETW 추적 로그 (ETL)](01-foundations/database-log-formats/evtx-evt-etl/etl.md)

### 셸·문서 형식

- [셸 아이템 (Shell Item·PIDL)](01-foundations/shell-document-formats/shell-item-pidl.md)
- [바로가기 형식 (Shell Link·LNK)](01-foundations/shell-document-formats/shell-link-lnk.md)
- [OLE 복합 파일 (Compound File Binary)](01-foundations/shell-document-formats/compound-file-binary.md)

### 앱·메일 데이터 구조

- [크롬 계열 앱 공통 구조 (Chromium·Electron·WebView2)](01-foundations/app-mail-data/chromium-electron-webview2/index.md)
  - [프로필 폴더와 계열 브라우저 구분 (User Data·Profile·Local State)](01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md)
  - [Electron·WebView2 앱 데이터 위치 (Teams·Discord·Slack 등)](01-foundations/app-mail-data/chromium-electron-webview2/teams-discord-slack.md)
  - [캐시 형식 (Blockfile·Simple Cache)](01-foundations/app-mail-data/chromium-electron-webview2/blockfile-simple-cache.md)
  - [쿠키·비밀번호 암호화 (DPAPI·App-Bound Encryption)](01-foundations/app-mail-data/chromium-electron-webview2/dpapi-app-bound-encryption.md)
- [UWP 앱 데이터 구조 (Packages 폴더·settings.dat)](01-foundations/app-mail-data/packages-settings-dat.md)
- [인터넷 메일 형식 (EML·MBOX·RFC 5322·MIME)](01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md)
- [MAPI 속성 (MAPI Property)](01-foundations/app-mail-data/mapi-property.md)

### 값 읽는 법

- [시각 값 형식 (FILETIME·Unix·WebKit·DOS·OLE)](01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)
- [윈도 식별자 형식 (SID·GUID·CLSID·Known Folder ID)](01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md)
- [문자 인코딩 (UTF-16LE·UTF-8·CP949)](01-foundations/value-decoding/utf-16le-utf-8-cp949.md)
- [윈도 압축 형식 (LZNT1·Xpress·Xpress Huffman)](01-foundations/value-decoding/lznt1-xpress-xpress-huffman.md)

### 암호 보호

- [DPAPI 구조 (Data Protection API)](01-foundations/protection/data-protection-api/index.md)
  - [DPAPI 동작 원리 (Protect·Unprotect)](01-foundations/protection/data-protection-api/protect-unprotect.md)
  - [DPAPI 블롭 구조 (DPAPI Blob)](01-foundations/protection/data-protection-api/dpapi-blob.md)
  - [마스터키 파일 (Master Key·Protect\SID)](01-foundations/protection/data-protection-api/master-key-protect-sid.md)
  - [비밀번호 변경 기록 (CREDHIST)](01-foundations/protection/data-protection-api/credhist.md)
  - [시스템 DPAPI 키 (DPAPI_SYSTEM)](01-foundations/protection/data-protection-api/dpapi-system.md)
  - [도메인 백업 키 (Domain Backup Key)](01-foundations/protection/data-protection-api/domain-backup-key.md)
  - [오프라인 복호 재료와 절차 (비밀번호·NT 해시·백업 키)](01-foundations/protection/data-protection-api/nt.md)

## 아티팩트 사전

### 시스템·계정

- [시스템 기본 정보 (OS Version·Computer Name·Install Date·Shutdown Time)](02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md)
- [시간대 설정 (Time Zone)](02-artifacts/system-account/time-zone.md)
- [사용자 계정 (SAM)](02-artifacts/system-account/sam.md)
- [사용자 프로필 목록 (ProfileList)](02-artifacts/system-account/profilelist.md)
- [설치 프로그램 (Uninstall)](02-artifacts/system-account/uninstall.md)
- [스토어 앱 설치 목록 (AppX·StateRepository)](02-artifacts/system-account/appx-staterepository.md)
- [윈도 업데이트 기록 (Windows Update·CBS Log)](02-artifacts/system-account/windows-update-cbs-log.md)

### 자동실행·지속성

- [로그온 자동실행 (Run·RunOnce·Startup Folder)](02-artifacts/persistence/run-runonce-startup-folder.md)
- [서비스·드라이버 (Services·Drivers)](02-artifacts/persistence/services-drivers.md)
- [예약 작업 (Scheduled Tasks)](02-artifacts/persistence/scheduled-tasks/index.md)
  - [작업 정의 파일 (System32\Tasks XML)](02-artifacts/persistence/scheduled-tasks/system32-tasks-xml.md)
  - [작업 캐시 레지스트리 (TaskCache Tree·Tasks)](02-artifacts/persistence/scheduled-tasks/taskcache-tree-tasks.md)
  - [옛 작업 파일 (.job·at)](02-artifacts/persistence/scheduled-tasks/job-at.md)
  - [숨긴 예약 작업 찾기 (SD 값 삭제)](02-artifacts/persistence/scheduled-tasks/sd.md)
- [WMI 영구 이벤트 구독 (WMI Event Subscription)](02-artifacts/persistence/wmi-event-subscription.md)
- [BITS 전송 작업 (BITS Jobs·qmgr.db)](02-artifacts/persistence/bits-jobs-qmgr-db.md)
- [기타 자동실행 위치 (Winlogon·IFEO·AppInit_DLLs)](02-artifacts/persistence/winlogon-ifeo-appinit-dlls.md)

### 프로그램 실행 흔적

- [프리페치 (Prefetch)](02-artifacts/execution/prefetch/index.md)
  - [파일 구조와 버전 (Format Versions·MAM)](02-artifacts/execution/prefetch/format-versions-mam.md)
  - [실행 횟수와 실행 시각 읽기 (Run Count·Last Run Times)](02-artifacts/execution/prefetch/run-count-last-run-times.md)
  - [참조 파일·폴더 목록 활용 (Referenced Files)](02-artifacts/execution/prefetch/referenced-files.md)
  - [경로 해시로 실행 위치 구분하기 (Path Hash)](02-artifacts/execution/prefetch/path-hash.md)
  - [프리페치 해석 함정 (꺼진 경우·보관 개수 한도·첫 실행 시각)](02-artifacts/execution/prefetch/pitfalls.md)
- [AmCache (Amcache.hve)](02-artifacts/execution/amcache-hve/index.md)
  - [구조와 버전별 차이 (Structure·Versions)](02-artifacts/execution/amcache-hve/structure-versions.md)
  - [실행 파일 항목 (InventoryApplicationFile)](02-artifacts/execution/amcache-hve/inventoryapplicationfile.md)
  - [설치 프로그램 항목 (InventoryApplication)](02-artifacts/execution/amcache-hve/inventoryapplication.md)
  - [드라이버 항목 (InventoryDriverBinary)](02-artifacts/execution/amcache-hve/inventorydriverbinary.md)
  - [바로가기 항목 (InventoryApplicationShortcut)](02-artifacts/execution/amcache-hve/inventoryapplicationshortcut.md)
  - [장치 항목 (InventoryDevicePnp)](02-artifacts/execution/amcache-hve/inventorydevicepnp.md)
  - [구버전 실행 기록 (RecentFileCache.bcf)](02-artifacts/execution/amcache-hve/recentfilecache-bcf.md)
  - [AmCache 해석 함정 (실행 증거가 아닌 경우·SHA1 계산 범위)](02-artifacts/execution/amcache-hve/sha1.md)
- [심캐시 (ShimCache·AppCompatCache)](02-artifacts/execution/shimcache-appcompatcache.md)
- [BAM·DAM (Background Activity Moderator)](02-artifacts/execution/background-activity-moderator.md)
- [UserAssist (UserAssist)](02-artifacts/execution/userassist.md)
- [SRUM (System Resource Usage Monitor)](02-artifacts/execution/system-resource-usage-monitor/index.md)
  - [구조와 ID 매핑 (SruDbIdMapTable)](02-artifacts/execution/system-resource-usage-monitor/srudbidmaptable.md)
  - [앱별 자원 사용 (Application Resource Usage)](02-artifacts/execution/system-resource-usage-monitor/application-resource-usage.md)
  - [네트워크 사용량 (Network Data Usage)](02-artifacts/execution/system-resource-usage-monitor/network-data-usage.md)
  - [네트워크 연결 기록 (Network Connectivity)](02-artifacts/execution/system-resource-usage-monitor/network-connectivity.md)
  - [전원·배터리 사용 (Energy Usage)](02-artifacts/execution/system-resource-usage-monitor/energy-usage.md)
  - [SRUM 해석 함정 (1시간 단위 기록·레지스트리 임시 저장)](02-artifacts/execution/system-resource-usage-monitor/1.md)
- [MUICache (MUICache)](02-artifacts/execution/muicache.md)
- [작업표시줄 사용 기록 (FeatureUsage)](02-artifacts/execution/featureusage.md)
- [프로그램 호환성 도우미 (PCA)](02-artifacts/execution/pca.md)
- [PowerShell 명령 기록 (ConsoleHost_history.txt)](02-artifacts/execution/consolehost-history-txt.md)
- [실행 창 명령 기록 (RunMRU)](02-artifacts/execution/runmru.md)
- [윈도 오류 보고 (WER)](02-artifacts/execution/wer.md)
- [윈도 알림 기록 (wpndatabase.db)](02-artifacts/execution/wpndatabase-db.md)
- [디펜더 검사 로그·격리 파일 (MPLog·DetectionHistory·Quarantine)](02-artifacts/execution/mplog-detectionhistory-quarantine.md)
- [카메라·마이크 사용 기록 (CapabilityAccessManager)](02-artifacts/execution/capabilityaccessmanager.md)

### 파일·폴더 사용 흔적

- [바로가기 파일 (LNK)](02-artifacts/file-folder-usage/lnk.md)
- [점프리스트 (Jump Lists)](02-artifacts/file-folder-usage/jump-lists.md)
- [셸백 (ShellBags)](02-artifacts/file-folder-usage/shellbags/index.md)
  - [저장 위치와 구조 (NTUSER·UsrClass·BagMRU·Bags)](02-artifacts/file-folder-usage/shellbags/ntuser-usrclass-bagmru-bags.md)
  - [셸백 시각 해석 (처음 연 때·마지막 바뀐 때)](02-artifacts/file-folder-usage/shellbags/timestamps.md)
  - [외부 장치·네트워크·압축 폴더 탐색 흔적](02-artifacts/file-folder-usage/shellbags/removable-network-zip.md)
  - [지운 폴더 흔적 찾기 (Deleted Folders)](02-artifacts/file-folder-usage/shellbags/deleted-folders.md)
  - [셸백 해석 함정 (Pitfalls)](02-artifacts/file-folder-usage/shellbags/pitfalls.md)
- [최근 문서 (RecentDocs)](02-artifacts/file-folder-usage/recentdocs.md)
- [열기·저장 대화상자 기록 (ComDlg32: OpenSavePidlMRU·LastVisitedPidlMRU·CIDSizeMRU)](02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md)
- [탐색기 입력 기록 (TypedPaths·WordWheelQuery)](02-artifacts/file-folder-usage/typedpaths-wordwheelquery.md)
- [휴지통 (Recycle Bin)](02-artifacts/file-folder-usage/recycle-bin.md)
- [썸네일 캐시 (thumbcache_*.db·Thumbs.db)](02-artifacts/file-folder-usage/thumbcache-db-thumbs-db.md)
- [윈도 검색 색인 DB (Windows Search)](02-artifacts/file-folder-usage/windows-search/index.md)
  - [위치와 형식 (Windows.edb·Windows.db)](02-artifacts/file-folder-usage/windows-search/windows-edb-windows-db.md)
  - [파일 속성 되살리기 (PropertyStore)](02-artifacts/file-folder-usage/windows-search/propertystore.md)
  - [수집 기록 (SystemIndex_Gthr)](02-artifacts/file-folder-usage/windows-search/systemindex-gthr.md)
  - [지운 파일·옛 파일 흔적 찾기](02-artifacts/file-folder-usage/windows-search/deleted-file-traces.md)
  - [색인 해석 함정 (색인 범위·재구성)](02-artifacts/file-folder-usage/windows-search/pitfalls.md)
- [윈도 타임라인 (ActivitiesCache.db)](02-artifacts/file-folder-usage/activitiescache-db.md)
- [오피스 사용 흔적 (Microsoft Office)](02-artifacts/file-folder-usage/microsoft-office/index.md)
  - [오피스 최근 파일 (File MRU·Place MRU)](02-artifacts/file-folder-usage/microsoft-office/file-mru-place-mru.md)
  - [신뢰 문서 기록 (Trust Records)](02-artifacts/file-folder-usage/microsoft-office/trust-records.md)
  - [읽던 위치 (Reading Locations)](02-artifacts/file-folder-usage/microsoft-office/reading-locations.md)
  - [백스테이지 캐시 (BackstageInAppNavCache)](02-artifacts/file-folder-usage/microsoft-office/backstageinappnavcache.md)
  - [자동 복구·저장 안 한 문서 (AutoRecover·UnsavedFiles)](02-artifacts/file-folder-usage/microsoft-office/autorecover-unsavedfiles.md)
  - [오피스 문서 캐시 (OfficeFileCache)](02-artifacts/file-folder-usage/microsoft-office/officefilecache.md)
- [메모장 탭 저장 파일 (Notepad TabState)](02-artifacts/file-folder-usage/notepad-tabstate.md)
- [압축 프로그램 사용 기록 (7-Zip·WinRAR·Bandizip)](02-artifacts/file-folder-usage/7-zip-winrar-bandizip.md)

### 파일시스템

- [마스터 파일 테이블 ($MFT)](02-artifacts/filesystem/mft.md)
- [NTFS 트랜잭션 로그 ($LogFile)](02-artifacts/filesystem/logfile.md)
- [USN 변경 저널 ($UsnJrnl)](02-artifacts/filesystem/usnjrnl.md)
- [폴더 인덱스와 슬랙 ($I30)](02-artifacts/filesystem/i30.md)
- [다운로드 출처 표시 (Zone.Identifier)](02-artifacts/filesystem/zone-identifier.md)

### 외부 장치

- [USB 저장장치 흔적 (USB Storage Artifacts)](02-artifacts/external-devices/usb-storage-artifacts/index.md)
  - [USB 저장장치 목록 (USBSTOR)](02-artifacts/external-devices/usb-storage-artifacts/usbstor.md)
  - [USB 장치 식별자 (Enum\USB VID·PID)](02-artifacts/external-devices/usb-storage-artifacts/enum-usb-vid-pid.md)
  - [연결·해제 시각 (DeviceClasses·Device Properties 0064·0066·0067)](02-artifacts/external-devices/usb-storage-artifacts/deviceclasses-device-properties-0064-0066-0067.md)
  - [드라이브 문자 매핑 (MountedDevices)](02-artifacts/external-devices/usb-storage-artifacts/mounteddevices.md)
  - [사용자별 장치 연결 (MountPoints2)](02-artifacts/external-devices/usb-storage-artifacts/mountpoints2.md)
  - [장치 설치 로그 (setupapi.dev.log)](02-artifacts/external-devices/usb-storage-artifacts/setupapi-dev-log.md)
  - [휴대용 장치·볼륨 이름 기록 (WPD·EMDMgmt)](02-artifacts/external-devices/usb-storage-artifacts/wpd-emdmgmt.md)
  - [USBSTOR 에 안 남는 장치 (UASP·SCSI·SD 카드)](02-artifacts/external-devices/usb-storage-artifacts/uasp-scsi-sd.md)
- [블루투스 장치 (BTHPORT)](02-artifacts/external-devices/bthport.md)
- [인쇄 흔적 (Print Spooler: SPL·SHD·프린터 목록)](02-artifacts/external-devices/print-spooler-spl-shd.md)
- [스마트폰 백업 파일 (iTunes·Smart Switch Backup)](02-artifacts/external-devices/itunes-smart-switch-backup.md)

### 인터넷·브라우저

- [크롬 계열 브라우저 (Chrome·Edge·Whale 등)](02-artifacts/browsers/chrome-edge-whale/index.md)
  - [방문·다운로드 기록 (History)](02-artifacts/browsers/chrome-edge-whale/history.md)
  - [쿠키 (Cookies)](02-artifacts/browsers/chrome-edge-whale/cookies.md)
  - [캐시 (Cache)](02-artifacts/browsers/chrome-edge-whale/cache.md)
  - [저장 비밀번호 (Login Data)](02-artifacts/browsers/chrome-edge-whale/login-data.md)
  - [세션·탭 복원 (Sessions)](02-artifacts/browsers/chrome-edge-whale/sessions.md)
  - [웹 저장소 (Local Storage·IndexedDB)](02-artifacts/browsers/chrome-edge-whale/local-storage-indexeddb.md)
  - [자동완성·폼 기록 (Web Data·Autofill)](02-artifacts/browsers/chrome-edge-whale/web-data-autofill.md)
  - [즐겨찾기 (Bookmarks)](02-artifacts/browsers/chrome-edge-whale/bookmarks.md)
  - [확장 프로그램 (Extensions)](02-artifacts/browsers/chrome-edge-whale/extensions.md)
- [파이어폭스 (Firefox)](02-artifacts/browsers/firefox/index.md)
  - [프로필 구조 (profiles.ini·prefs.js)](02-artifacts/browsers/firefox/profiles-ini-prefs-js.md)
  - [방문·다운로드·즐겨찾기 (places.sqlite)](02-artifacts/browsers/firefox/places-sqlite.md)
  - [쿠키 (cookies.sqlite)](02-artifacts/browsers/firefox/cookies-sqlite.md)
  - [캐시 (cache2)](02-artifacts/browsers/firefox/cache2.md)
  - [저장 비밀번호 (logins.json·key4.db)](02-artifacts/browsers/firefox/logins-json-key4-db.md)
  - [세션 복원 (sessionstore.jsonlz4)](02-artifacts/browsers/firefox/sessionstore-jsonlz4.md)
  - [웹 저장소 (storage 폴더)](02-artifacts/browsers/firefox/storage.md)
  - [양식 기록 (formhistory.sqlite)](02-artifacts/browsers/firefox/formhistory-sqlite.md)
  - [확장 프로그램 (extensions.json)](02-artifacts/browsers/firefox/extensions-json.md)
- [인터넷 익스플로러·옛 엣지 (IE·EdgeHTML)](02-artifacts/browsers/ie-edgehtml/index.md)
  - [웹캐시 DB (WebCacheV01.dat)](02-artifacts/browsers/ie-edgehtml/webcachev01-dat.md)
  - [옛 기록 파일 (index.dat)](02-artifacts/browsers/ie-edgehtml/index-dat.md)
  - [주소창 입력 주소 (TypedURLs·TypedURLsTime)](02-artifacts/browsers/ie-edgehtml/typedurls-typedurlstime.md)
  - [저장 비밀번호 (IntelliForms)](02-artifacts/browsers/ie-edgehtml/intelliforms.md)
  - [쿠키·캐시 폴더 (INetCookies·INetCache)](02-artifacts/browsers/ie-edgehtml/inetcookies-inetcache.md)
  - [즐겨찾기 (Favorites .url)](02-artifacts/browsers/ie-edgehtml/favorites-url.md)

### 메일

- [아웃룩 (Outlook)](02-artifacts/mail/outlook/index.md)
  - [데이터 파일 구조 (PST·OST)](02-artifacts/mail/outlook/pst-ost.md)
  - [PST와 OST 차이 (Cached Mode·Exchange)](02-artifacts/mail/outlook/cached-mode-exchange.md)
  - [지운 메시지 복구 (Recoverable Items·Free Blocks)](02-artifacts/mail/outlook/recoverable-items-free-blocks.md)
  - [개별 메시지 파일 (MSG)](02-artifacts/mail/outlook/msg.md)
  - [첨부 임시 폴더 (OLK·Content.Outlook)](02-artifacts/mail/outlook/olk-content-outlook.md)
  - [자동완성 목록 (NK2·Stream_Autocomplete)](02-artifacts/mail/outlook/nk2-stream-autocomplete.md)
  - [계정·프로필 레지스트리 (Outlook Profiles)](02-artifacts/mail/outlook/outlook-profiles.md)
- [새 Outlook (New Outlook)](02-artifacts/mail/new-outlook.md)
- [썬더버드 (Thunderbird)](02-artifacts/mail/thunderbird.md)
- [옛 윈도 메일 프로그램 (Outlook Express·Windows Live Mail)](02-artifacts/mail/outlook-express-windows-live-mail.md)
- [Windows 메일 앱 (HxStore)](02-artifacts/mail/hxstore.md)

### 메신저

- [카카오톡 PC (KakaoTalk PC)](02-artifacts/messengers/kakaotalk-pc/index.md)
  - [설치 위치와 파일 구성 (Install Paths·Files)](02-artifacts/messengers/kakaotalk-pc/install-paths-files.md)
  - [대화 DB 암호화와 버전별 차이 (Chat DB Encryption)](02-artifacts/messengers/kakaotalk-pc/chat-db-encryption.md)
  - [받은 파일·사진 폴더 (Received Files)](02-artifacts/messengers/kakaotalk-pc/received-files.md)
  - [계정·로그인 흔적 (Account·Login)](02-artifacts/messengers/kakaotalk-pc/account-login.md)
  - [대화 DB가 안 열릴 때 남는 단서 (메모리·캐시·이미지)](02-artifacts/messengers/kakaotalk-pc/when-db-wont-open.md)
- [왓츠앱 데스크톱 (WhatsApp Desktop)](02-artifacts/messengers/whatsapp-desktop.md)
- [스카이프 (Skype)](02-artifacts/messengers/skype.md)
- [마이크로소프트 팀즈 (Teams)](02-artifacts/messengers/teams.md)
- [텔레그램 (Telegram)](02-artifacts/messengers/telegram.md)
- [디스코드 (Discord)](02-artifacts/messengers/discord.md)
- [라인 (LINE)](02-artifacts/messengers/line.md)
- [슬랙 (Slack)](02-artifacts/messengers/slack.md)
- [시그널 (Signal)](02-artifacts/messengers/signal.md)
- [위챗 (WeChat)](02-artifacts/messengers/wechat.md)
- [네이트온 (NateOn)](02-artifacts/messengers/nateon.md)
- [줌 (Zoom)](02-artifacts/messengers/zoom.md)
- [휴대폰과 연결 (Phone Link)](02-artifacts/messengers/phone-link.md)

### 클라우드·노트

- [클라우드 동기화 공통 구조 (Cloud Files API·SyncRootManager)](02-artifacts/cloud-notes/cloud-files-api-syncrootmanager.md)
- [원드라이브 (OneDrive)](02-artifacts/cloud-notes/onedrive/index.md)
  - [계정·설정 레지스트리 (Accounts·Settings)](02-artifacts/cloud-notes/onedrive/accounts-settings.md)
  - [동기화 DB (SyncEngineDatabase.db)](02-artifacts/cloud-notes/onedrive/syncenginedatabase-db.md)
  - [로그 (ODL·ODLGZ)](02-artifacts/cloud-notes/onedrive/odl-odlgz.md)
  - [회사용 OneDrive와 SharePoint 동기화 (Business Tenant)](02-artifacts/cloud-notes/onedrive/business-tenant.md)
- [구글 드라이브 (DriveFS·Backup and Sync)](02-artifacts/cloud-notes/drivefs-backup-and-sync.md)
- [드롭박스 (Dropbox)](02-artifacts/cloud-notes/dropbox.md)
- [네이버 MYBOX (Naver MYBOX)](02-artifacts/cloud-notes/naver-mybox.md)
- [아이클라우드 (iCloud for Windows)](02-artifacts/cloud-notes/icloud-for-windows.md)
- [박스 드라이브 (Box Drive)](02-artifacts/cloud-notes/box-drive.md)
- [메가 (MEGA)](02-artifacts/cloud-notes/mega.md)
- [에버노트 (Evernote)](02-artifacts/cloud-notes/evernote.md)
- [노션 (Notion)](02-artifacts/cloud-notes/notion.md)
- [스티커 메모 (Sticky Notes)](02-artifacts/cloud-notes/sticky-notes.md)
- [원노트 (OneNote)](02-artifacts/cloud-notes/onenote.md)

### 네트워크

- [Wi-Fi 프로필 (WLAN Profiles)](02-artifacts/network/wlan-profiles.md)
- [네트워크 목록 (NetworkList)](02-artifacts/network/networklist.md)
- [네트워크 인터페이스 설정 (TCP/IP Interfaces)](02-artifacts/network/tcp-ip-interfaces.md)
- [원격 데스크톱 접속 기록 (RDP Client MRU)](02-artifacts/network/rdp-client-mru.md)
- [원격 데스크톱 비트맵 캐시 (RDP Bitmap Cache)](02-artifacts/network/rdp-bitmap-cache.md)
- [원격 제어 프로그램 (Remote Access Tools)](02-artifacts/network/remote-access-tools/index.md)
  - [팀뷰어 (TeamViewer)](02-artifacts/network/remote-access-tools/teamviewer.md)
  - [애니데스크 (AnyDesk)](02-artifacts/network/remote-access-tools/anydesk.md)
  - [스크린커넥트 (ScreenConnect)](02-artifacts/network/remote-access-tools/screenconnect.md)
  - [기타 원격 제어 도구 (RustDesk·Splashtop·Chrome Remote Desktop)](02-artifacts/network/remote-access-tools/rustdesk-splashtop-chrome-remote-desktop.md)
- [VPN 연결 기록 (VPN Connections)](02-artifacts/network/vpn-connections.md)
- [SSH·FTP 도구 흔적 (PuTTY·WinSCP·FileZilla·OpenSSH)](02-artifacts/network/putty-winscp-filezilla-openssh.md)
- [공유 폴더·네트워크 드라이브 (Network Shares·Mapped Drives)](02-artifacts/network/network-shares-mapped-drives.md)
- [윈도 방화벽 (Windows Firewall: 규칙·pfirewall.log)](02-artifacts/network/windows-firewall-pfirewall-log.md)
- [hosts 파일 (hosts)](02-artifacts/network/hosts.md)

### 이벤트 로그

- [감사 정책과 로그 설정 (Audit Policy·Log Settings)](02-artifacts/event-logs/audit-policy-log-settings.md)
- [로그온·로그오프 (Logon Events)](02-artifacts/event-logs/logon-events/index.md)
  - [로그온 유형 해석 (Logon Type)](02-artifacts/event-logs/logon-events/logon-type.md)
  - [로그온 실패와 실패 코드 (4625)](02-artifacts/event-logs/logon-events/4625.md)
  - [로그온 세션 잇기 (Logon ID·4624~4634·4647)](02-artifacts/event-logs/logon-events/logon-id-4624-4634-4647.md)
  - [화면 잠금·해제 (4800·4801)](02-artifacts/event-logs/logon-events/4800-4801.md)
  - [명시적 자격 증명·특수 권한 (4648·4672)](02-artifacts/event-logs/logon-events/4648-4672.md)
  - [도메인 인증 이벤트 (4768·4769·4776)](02-artifacts/event-logs/logon-events/4768-4769-4776.md)
  - [기록이 남는 위치 (로컬 PC와 도메인 컨트롤러)](02-artifacts/event-logs/logon-events/pc.md)
- [켜짐·꺼짐 (Power On·Off Events)](02-artifacts/event-logs/power-on-off-events.md)
- [원격 데스크톱 이벤트 (RDP Event Logs)](02-artifacts/event-logs/rdp-event-logs/index.md)
  - [들어온 접속: 인증 단계 (1149·4624 유형 10·4625)](02-artifacts/event-logs/rdp-event-logs/1149-4624-10-4625.md)
  - [들어온 접속: 세션 단계 (LocalSessionManager 21~25·4778·4779)](02-artifacts/event-logs/rdp-event-logs/localsessionmanager-21-25-4778-4779.md)
  - [나간 접속 (RDPClient 1024·1102)](02-artifacts/event-logs/rdp-event-logs/rdpclient-1024-1102.md)
  - [해석 함정 (1149의 뜻·NLA·유형 3과 10 구분)](02-artifacts/event-logs/rdp-event-logs/1149-nla-3-10.md)
- [PowerShell 실행 기록 (PowerShell Event Logs: 4103·4104)](02-artifacts/event-logs/powershell-event-logs-4103-4104.md)
- [원격 명령 실행 이벤트 (WinRM·WMI-Activity)](02-artifacts/event-logs/winrm-wmi-activity.md)
- [서비스 설치 (7045·4697)](02-artifacts/event-logs/7045-4697.md)
- [예약 작업 이벤트 (TaskScheduler·4698)](02-artifacts/event-logs/taskscheduler-4698.md)
- [프로세스 생성 (4688)](02-artifacts/event-logs/4688.md)
- [계정 생성·변경 (Account Management Events)](02-artifacts/event-logs/account-management-events.md)
- [이벤트 로그 삭제 (1102·104)](02-artifacts/event-logs/1102-104.md)
- [네트워크 연결 이벤트 (WLAN-AutoConfig·NetworkProfile)](02-artifacts/event-logs/wlan-autoconfig-networkprofile.md)
- [외부 장치 연결 이벤트 (Partition/Diagnostic·Kernel-PnP·DriverFrameworks)](02-artifacts/event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md)
- [시간 변경 (4616·Kernel-General)](02-artifacts/event-logs/4616-kernel-general.md)
- [Windows Defender 탐지 (1116·1117)](02-artifacts/event-logs/1116-1117.md)
- [오피스 경고 (OAlerts)](02-artifacts/event-logs/oalerts.md)
- [공유 폴더 접근 (5140·5145)](02-artifacts/event-logs/5140-5145.md)
- [파일 접근 감사 (4656·4663·4660)](02-artifacts/event-logs/4656-4663-4660.md)
- [프로그램 설치·삭제 이벤트 (MsiInstaller)](02-artifacts/event-logs/msiinstaller.md)
- [인쇄 이벤트 (PrintService 307)](02-artifacts/event-logs/printservice-307.md)
- [Sysmon 로그 (Sysmon)](02-artifacts/event-logs/sysmon/index.md)
  - [Sysmon 개념과 설정 확인 (Sysmon Config)](02-artifacts/event-logs/sysmon/sysmon-config.md)
  - [프로세스 생성 (이벤트 1)](02-artifacts/event-logs/sysmon/1.md)
  - [네트워크 연결·DNS 질의 (이벤트 3·22)](02-artifacts/event-logs/sysmon/3-22.md)
  - [파일 생성·삭제 (이벤트 11·23·26)](02-artifacts/event-logs/sysmon/11-23-26.md)
  - [레지스트리 변경 (이벤트 12·13·14)](02-artifacts/event-logs/sysmon/12-13-14.md)
  - [이미지 로드·프로세스 접근 (이벤트 7·8·10)](02-artifacts/event-logs/sysmon/7-8-10.md)

### 자격증명

- [자격 증명 관리자와 볼트 (Credential Manager·Windows Vault)](02-artifacts/credentials/credential-manager-windows-vault.md)
- [레지스트리 속 비밀번호 정보 (SAM·SECURITY)](02-artifacts/credentials/sam-security/index.md)
  - [부트키 구하기 (SYSTEM Boot Key)](02-artifacts/credentials/sam-security/system-boot-key.md)
  - [NTLM 비밀번호 해시 (NT Hash)](02-artifacts/credentials/sam-security/nt-hash.md)
  - [LSA 시크릿 (LSA Secrets, 자동 로그온 비밀번호 포함)](02-artifacts/credentials/sam-security/lsa-secrets.md)
  - [도메인 캐시 자격증명 (MSCache v2)](02-artifacts/credentials/sam-security/mscache-v2.md)
- [액티브 디렉터리 DB (NTDS.dit)](02-artifacts/credentials/ntds-dit.md)
- [공동인증서 (NPKI)](02-artifacts/credentials/npki.md)

### 파일 내장 메타데이터

- [문서 메타데이터 (Document Metadata)](02-artifacts/embedded-metadata/document-metadata/index.md)
  - [오피스 문서 속성 (OOXML docProps)](02-artifacts/embedded-metadata/document-metadata/ooxml-docprops.md)
  - [옛 오피스 문서 속성 (OLE SummaryInformation)](02-artifacts/embedded-metadata/document-metadata/ole-summaryinformation.md)
  - [편집 흔적 식별자 (RSID)](02-artifacts/embedded-metadata/document-metadata/rsid.md)
  - [PDF 정보 사전과 XMP (PDF Info·XMP)](02-artifacts/embedded-metadata/document-metadata/pdf-info-xmp.md)
  - [PDF 증분 저장과 이전 판 복원 (Incremental Update)](02-artifacts/embedded-metadata/document-metadata/incremental-update.md)
  - [한글 문서 (HWP·HWPX)](02-artifacts/embedded-metadata/document-metadata/hwp-hwpx.md)
- [사진 EXIF (EXIF)](02-artifacts/embedded-metadata/exif.md)
- [오피스 매크로 (VBA Macro)](02-artifacts/embedded-metadata/vba-macro.md)
- [실행 파일 메타데이터 (PE Header·Version Info·Digital Signature)](02-artifacts/embedded-metadata/pe-header-version-info-digital-signature.md)

## 분석 기법

### 조사 절차·증거 확보

- [포렌식 조사 절차 (Investigation Process)](03-techniques/process-acquisition/investigation-process.md)
- [증거 획득 (Evidence Acquisition)](03-techniques/process-acquisition/evidence-acquisition/index.md)
  - [디스크 이미징 (Disk Imaging)](03-techniques/process-acquisition/evidence-acquisition/disk-imaging.md)
  - [쓰기 방지 (Write Blocker)](03-techniques/process-acquisition/evidence-acquisition/write-blocker.md)
  - [해시로 무결성 검증 (Hash Verification)](03-techniques/process-acquisition/evidence-acquisition/hash-verification.md)
  - [선별 수집 (Triage Collection)](03-techniques/process-acquisition/evidence-acquisition/triage-collection.md)
  - [가상 머신·클라우드 디스크 확보 (VM·Cloud Disk)](03-techniques/process-acquisition/evidence-acquisition/vm-cloud-disk.md)
  - [증거 보관 연속성 (Chain of Custody)](03-techniques/process-acquisition/evidence-acquisition/chain-of-custody.md)
- [라이브 응답 (Live Response)](03-techniques/process-acquisition/live-response/index.md)
  - [수집 순서와 원칙 (Order of Volatility)](03-techniques/process-acquisition/live-response/order-of-volatility.md)
  - [프로세스·DLL·핸들 수집 (Processes·DLLs·Handles)](03-techniques/process-acquisition/live-response/processes-dlls-handles.md)
  - [네트워크 상태 수집 (Connections·DNS·ARP·Routes)](03-techniques/process-acquisition/live-response/connections-dns-arp-routes.md)
  - [로그온 세션·클립보드·화면 수집 (Sessions·Clipboard·Screen)](03-techniques/process-acquisition/live-response/sessions-clipboard-screen.md)
  - [실행 중 시스템 이미징 (Live Imaging)](03-techniques/process-acquisition/live-response/live-imaging.md)

### 분석

- [메모리 분석 (Memory Forensics)](03-techniques/analysis/memory-forensics/index.md)
  - [메모리 덤프 확보 (Memory Acquisition)](03-techniques/analysis/memory-forensics/memory-acquisition.md)
  - [프로세스와 DLL 분석 (Process Analysis)](03-techniques/analysis/memory-forensics/process-analysis.md)
  - [메모리 속 네트워크 흔적 (Network Artifacts)](03-techniques/analysis/memory-forensics/network-artifacts.md)
  - [코드 주입·숨긴 프로세스 탐지 (Injection·Rootkit)](03-techniques/analysis/memory-forensics/injection-rootkit.md)
  - [메모리 속 문자열·자격증명·암호 키 (Strings·Credentials·Keys)](03-techniques/analysis/memory-forensics/strings-credentials-keys.md)
  - [최대 절전 파일 (hiberfil.sys)](03-techniques/analysis/memory-forensics/hiberfil-sys.md)
  - [페이지 파일 (pagefile.sys·swapfile.sys)](03-techniques/analysis/memory-forensics/pagefile-sys-swapfile-sys.md)
  - [크래시 덤프 (MEMORY.DMP·Minidump)](03-techniques/analysis/memory-forensics/memory-dmp-minidump.md)
- [타임라인 작성 (Timeline)](03-techniques/analysis/timeline/index.md)
  - [파일 시각 네 가지와 변화 규칙 (MACB·Timestamp Rules)](03-techniques/analysis/timeline/macb-timestamp-rules.md)
  - [파일시스템 타임라인 (Filesystem Timeline: $MFT·$UsnJrnl·$LogFile)](03-techniques/analysis/timeline/filesystem-timeline-mft-usnjrnl-logfile.md)
  - [여러 아티팩트 합친 타임라인 (Super Timeline)](03-techniques/analysis/timeline/super-timeline.md)
  - [시간대·시계 오차 보정 (Time Normalization)](03-techniques/analysis/timeline/time-normalization.md)
  - [시각 조작 탐지 (Timestomping)](03-techniques/analysis/timeline/timestomping.md)
- [섀도 복사본 활용 (Volume Shadow Copy Analysis)](03-techniques/analysis/volume-shadow-copy-analysis.md)
- [삭제 데이터 복구 (Data Recovery)](03-techniques/analysis/data-recovery/index.md)
  - [파일시스템 기반 복구 (Undelete: NTFS·FAT)](03-techniques/analysis/data-recovery/undelete-ntfs-fat.md)
  - [비할당 영역과 슬랙 (Unallocated·Slack Space)](03-techniques/analysis/data-recovery/unallocated-slack-space.md)
  - [파일 카빙 (File Carving)](03-techniques/analysis/data-recovery/file-carving.md)
  - [레코드 카빙 (Record Carving)](03-techniques/analysis/data-recovery/record-carving.md)
  - [SSD TRIM과 복구 한계 (SSD·TRIM)](03-techniques/analysis/data-recovery/ssd-trim.md)
- [암호화 증거 다루기 (Encrypted Evidence)](03-techniques/analysis/encrypted-evidence/index.md)
  - [암호화 컨테이너 찾기 (Encrypted Container Detection)](03-techniques/analysis/encrypted-evidence/encrypted-container-detection.md)
  - [BitLocker 볼륨 구조와 풀기 (BitLocker)](03-techniques/analysis/encrypted-evidence/bitlocker.md)
  - [EFS 암호화 파일 (Encrypting File System)](03-techniques/analysis/encrypted-evidence/encrypting-file-system.md)
  - [암호 걸린 문서·압축 파일 (Password-Protected Files)](03-techniques/analysis/encrypted-evidence/password-protected-files.md)
  - [DRM 문서 판별 (Enterprise DRM)](03-techniques/analysis/encrypted-evidence/enterprise-drm.md)
  - [비밀번호 복구 (Password Recovery)](03-techniques/analysis/encrypted-evidence/password-recovery.md)
- [파일 내용 검색 (Content Search)](03-techniques/analysis/content-search/index.md)
  - [파일 형식 식별 (File Signature)](03-techniques/analysis/content-search/file-signature.md)
  - [압축·복합 파일 펼치기 (Archive Expansion)](03-techniques/analysis/content-search/archive-expansion.md)
  - [본문 추출과 글자 인식 (Text Extraction·OCR)](03-techniques/analysis/content-search/text-extraction-ocr.md)
  - [키워드 검색 (Keyword Search)](03-techniques/analysis/content-search/keyword-search.md)
  - [개인정보 탐지 (PII Detection)](03-techniques/analysis/content-search/pii-detection.md)
- [해시셋 대조와 유사 해시 (Hash Set·Fuzzy Hash)](03-techniques/analysis/hash-set-fuzzy-hash.md)
- [의심 실행 파일 선별 (Code Signing·YARA)](03-techniques/analysis/code-signing-yara.md)
- [이벤트 로그 규칙 검색 (Sigma Rules)](03-techniques/analysis/sigma-rules.md)
- [메일 헤더 분석 (Email Header Analysis)](03-techniques/analysis/email-header-analysis.md)

### 보고

- [도구 결과 교차 검증 (Tool Validation)](03-techniques/reporting/tool-validation.md)
- [분석 보고서 작성 (Forensic Report)](03-techniques/reporting/forensic-report.md)

## 조사 시나리오

### 정보 유출

- [자료를 밖으로 빼돌렸나 (Data Exfiltration)](04-scenarios/exfiltration/data-exfiltration/index.md)
  - [USB 로 무엇을 가져갔나 (USB)](04-scenarios/exfiltration/data-exfiltration/usb.md)
  - [스마트폰으로 옮겼나 (MTP·Phone Link)](04-scenarios/exfiltration/data-exfiltration/mtp-phone-link.md)
  - [메일로 밖에 보냈나 (Email)](04-scenarios/exfiltration/data-exfiltration/email.md)
  - [메신저로 파일을 보냈나 (Messenger)](04-scenarios/exfiltration/data-exfiltration/messenger.md)
  - [클라우드로 밖에 보냈나 (Cloud)](04-scenarios/exfiltration/data-exfiltration/cloud.md)
  - [웹메일·웹하드로 올렸나 (Web Upload)](04-scenarios/exfiltration/data-exfiltration/web-upload.md)
  - [인쇄해서 가져갔나 (Print)](04-scenarios/exfiltration/data-exfiltration/print.md)
  - [퇴사 전 자료를 모으고 압축했나 (Staging)](04-scenarios/exfiltration/data-exfiltration/staging.md)
- [개인정보 파일이 어디 있고 밖으로 나갔나 (PII Exposure)](04-scenarios/exfiltration/pii-exposure.md)

### 침해 사고

- [악성코드는 어디서 들어왔나 (Initial Access)](04-scenarios/incident/initial-access.md)
- [악성코드 지속성(자동실행) 찾기 (Persistence)](04-scenarios/incident/persistence.md)
- [원격 데스크톱 침입 확인 (RDP Intrusion)](04-scenarios/incident/rdp-intrusion.md)
- [원격 제어 프로그램으로 누가 조작했나 (Remote Access Tool Abuse)](04-scenarios/incident/remote-access-tool-abuse.md)
- [계정 탈취와 측면 이동 (Credential Theft·Lateral Movement)](04-scenarios/incident/credential-theft-lateral-movement/index.md)
  - [비밀번호 대입 공격이 있었나 (Brute Force)](04-scenarios/incident/credential-theft-lateral-movement/brute-force.md)
  - [자격 증명을 빼냈나 (Credential Dumping)](04-scenarios/incident/credential-theft-lateral-movement/credential-dumping.md)
  - [다른 PC 에서 원격 실행했나 (PsExec·WMI·WinRM)](04-scenarios/incident/credential-theft-lateral-movement/psexec-wmi-winrm.md)
  - [새 계정을 만들거나 권한을 올렸나 (Account·Privilege)](04-scenarios/incident/credential-theft-lateral-movement/account-privilege.md)
- [랜섬웨어는 언제 어떻게 퍼졌나 (Ransomware)](04-scenarios/incident/ransomware.md)

### 행위 재구성

- [어떤 프로그램을 언제 실행했나 (Program Execution)](04-scenarios/activity/program-execution.md)
- [이 파일을 누가 언제 열었나 (File Access)](04-scenarios/activity/file-access.md)
- [이 파일은 어디서 왔나 (File Origin)](04-scenarios/activity/file-origin.md)
- [지운 파일의 흔적 찾기 (Deleted File Traces)](04-scenarios/activity/deleted-file-traces.md)
- [웹 사용 행위 재구성 (Web Activity)](04-scenarios/activity/web-activity.md)
- [시크릿 모드로 무엇을 했나 (Private Browsing)](04-scenarios/activity/private-browsing.md)
- [누구와 연락을 주고받았나 (Communication Reconstruction)](04-scenarios/activity/communication-reconstruction.md)
- [PC 사용 시간 재구성 (켜짐·꺼짐·로그온) (System Usage Time)](04-scenarios/activity/system-usage-time.md)
- [그 시각에 PC 를 쓴 사람이 누구인가 (User Attribution)](04-scenarios/activity/user-attribution.md)
- [이 문서의 날짜를 믿을 수 있나 (Document Date Verification)](04-scenarios/activity/document-date-verification.md)
- [증거를 없애려 했나 (Anti-Forensics)](04-scenarios/activity/anti-forensics/index.md)
  - [이벤트 로그를 지웠나 (Log Clearing)](04-scenarios/activity/anti-forensics/log-clearing.md)
  - [완전삭제 도구를 썼나 (Wiping Tools)](04-scenarios/activity/anti-forensics/wiping-tools.md)
  - [PC 를 초기화하거나 윈도를 다시 깔았나 (Reset·Reinstall)](04-scenarios/activity/anti-forensics/reset-reinstall.md)
  - [시스템 시각을 바꿨나 (System Time Change)](04-scenarios/activity/anti-forensics/system-time-change.md)
  - [보안 프로그램을 끄거나 지웠나 (Defense Evasion)](04-scenarios/activity/anti-forensics/defense-evasion.md)

