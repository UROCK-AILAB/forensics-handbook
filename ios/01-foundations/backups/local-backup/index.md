---
title: "로컬 백업"
parent: "기반 · 백업 형식"
nav_order: 210
has_children: true
has_toc: false
---

# 로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)

아이폰을 맥이나 Windows 컴퓨터에 연결해 만든 로컬 백업이 어디에 생기고, 폴더 안이 어떻게 짜여 있으며, 암호를 걸었을 때 무엇이 달라지는지를 다룹니다.

## 왜 중요한가

로컬 백업은 기기 안 파일 가운데 백업 대상인 것을 도메인과 경로 단위로 컴퓨터에 옮겨 둔 사본이라, 기기를 직접 다루지 않고도 메시지·사진·앱 데이터 같은 아티팩트를 살펴볼 수 있습니다. 스파이웨어 흔적을 검사하는 MVT(Mobile Verification Toolkit) 도 로컬 백업을 검사 대상으로 씁니다 [3].

백업이 증거가 되는 경우도 있습니다. 피조사자의 컴퓨터에서 백업 폴더가 나오면 그 폴더 자체가 어떤 기기를 언제 이 컴퓨터에 백업했는지를 알려 주고, 기기를 잃거나 초기화한 뒤에도 백업 시점의 데이터가 남아 있습니다.

컴퓨터 쪽 프로그램은 운영체제와 버전에 따라 다릅니다. 맥은 macOS 10.15 이후 Finder 가, macOS 10.14 이하는 iTunes 가 백업을 만들고 [2], Windows 는 Apple 기기 앱이나 iTunes 가 만듭니다 [1].

## 한눈에 보기

### 백업 폴더 위치

| 컴퓨터 | 위치 |
|---|---|
| 맥 | `~/Library/Application Support/MobileSync/Backup/` [1] |
| Windows, Apple 기기 앱 또는 Microsoft Store 판 iTunes | `%USERPROFILE%\Apple\MobileSync\` [3] |
| Windows, Apple 웹사이트에서 받은 iTunes | `%USERPROFILE%\AppData\Roaming\Apple Computer\MobileSync\` [3] |

Apple 문서 [1] 는 Windows 에서 앞쪽은 `%USERPROFILE%`, 뒤쪽은 `%AppData%` 에서 찾기 시작하라고만 적고, 전체 경로는 MVT 문서 [3] 에 있습니다. Apple 은 백업 폴더를 직접 만지기보다 Finder·Apple 기기 앱의 백업 관리 화면에서 지우거나 보관하도록 안내합니다 [1]. 조사할 때는 폴더를 통째로 사본으로 떠서 작업합니다.

### 무엇을 알려 주나

| 자리 | iOS 버전 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| Info.plist | 형식 버전과 상관없이 있음 [4] | 어떤 기기의 백업인지(기종·iOS 버전·식별자), 설치한 앱 | [백업 폴더 구조](structure.md) |
| Status.plist | 형식 버전과 상관없이 있음 [4] | 백업 형식 버전, 백업이 끝났는지, 백업 날짜 | [백업 폴더 구조](structure.md) |
| Manifest.plist | 형식 버전과 상관없이 있음 [4] | 암호를 걸었는지, 앱 목록, 백업 키백 | [암호 건 백업](encrypted-backup.md) |
| Manifest.db | iOS 10 기기부터(iOS 9 기기는 Manifest.mbdb) [4] | 백업 안 모든 파일의 도메인·경로·파일 이름 | [백업 폴더 구조](structure.md) |
| fileID 로 이름 붙인 파일 | iOS 10 기기부터 두 글자 하위 폴더 [4] | 기기에서 옮겨 온 파일 내용 | [도메인과 파일 이름](domains-fileid.md) |

실제 백업 하나에서 본 도메인은 모두 1428개였고, 그중 Apple 기본 영역이 1267개, 설치한 앱 등 나머지가 161개였습니다(확인 범위: iPhone 13 mini, iOS 27.0). 기기 안에도 백업과 관련된 설정 파일이 남아 백업에 함께 들어오며, 이 파일은 [백업 폴더 구조](structure.md) 에서 다룹니다.

암호를 걸었는지에 따라 들어가는 데이터와 볼 수 있는 범위가 크게 달라집니다. 저장된 암호나 통화 기록처럼 암호 건 백업에만 들어가는 데이터가 있고, iOS 10.2 베타 때 보고된 뒤로는 암호 건 백업의 파일 목록(Manifest.db)까지 암호화됩니다. 자세한 내용은 [암호 건 백업](encrypted-backup.md) 에 있습니다.

## 읽는 순서

1. [백업 폴더 구조 (Manifest.db·Info.plist·Status.plist)](structure.md) — 백업 폴더 맨 위의 plist 세 개와 Manifest.db 의 표·칸, 기기 안에 남는 백업 설정 파일을 봅니다.
2. [도메인과 파일 이름 (Domain·fileID)](domains-fileid.md) — 도메인 이름의 짜임과 fileID 를 만드는 규칙으로 백업 폴더 안 실제 파일을 찾습니다.
3. [암호 건 백업 (Encrypted Backup)](encrypted-backup.md) — 암호를 걸면 무엇이 더 들어가고 무엇이 암호화되는지, 암호 여부를 어떻게 판단하는지를 봅니다.

## 함께 볼 페이지

- [아이클라우드 백업](../icloud-backup.md) — 기기가 아이클라우드에 올리는 백업
- [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md) — 로컬 백업을 다른 확보 방법과 견주어 보기
- [데이터 보호](../../storage/data-protection/index.md) — 키백과 보호 등급
- [키체인](../../storage/keychain.md) — 백업에 들어가는 키체인 항목
- [SQLite 데이터베이스](../../data-formats/sqlite/index.md), [속성 목록 파일](../../data-formats/plist.md) — Manifest.db 와 plist 를 읽는 법
- [기기 식별자](../../value-decoding/device-identifiers.md) — Info.plist 의 식별자 읽기
- [초기화와 복원 흔적](../../../02-artifacts/system-account/erase-restore.md) — 백업에서 복원한 기기의 흔적
- [악성 코드·스파이웨어 흔적](../../../03-techniques/analysis/spyware-triage/index.md) — 로컬 백업으로 하는 검사

## 참고 문헌

1. Apple Support — Locate backups of your iPhone, iPad, and iPod touch (108809) — https://support.apple.com/en-us/108809
2. Apple Platform Security Guide — Keybags for Data Protection — https://support.apple.com/guide/security/keybags-for-data-protection-sec6483d5760/web
3. MVT (Mobile Verification Toolkit) 문서 — Backup with iTunes app — https://docs.mvt.re/en/latest/ios/backup/itunes/
4. Rich Infante — Reverse Engineering the iOS Backup (2017-03-16) — https://www.richinfante.com/2017/3/16/reverse-engineering-the-ios-backup
