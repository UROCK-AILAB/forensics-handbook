---
title: "복구가 안 되는 이유"
parent: "삭제 데이터 복구"
grand_parent: "기법 · 분석"
nav_order: 1340
---

# 복구가 안 되는 이유 (Encryption·TRIM)

아이폰에서 지운 데이터가 돌아오지 않는 이유는 파일별 키 암호화, SQLite 의 정리 동작, 앱의 보관 기간, 수집 방식 네 가지로 나눠 설명할 수 있습니다. TRIM 이 지운 블록을 언제 비우는지는 Apple 이 밝히지 않았습니다.

## 언제 쓰나

복구 결과가 없거나 일부만 나왔을 때 그 이유를 설명하고 보고서에 적을 때 씁니다. 수집 전에 어떤 방식으로 확보해야 조각이 남을지 판단할 때도 이 페이지를 먼저 봅니다.

## 이유 1: 파일별 키 암호화

아이폰은 데이터 볼륨에 파일을 만들 때마다 256비트 파일별 키를 새로 만들고, 하드웨어 AES 엔진이 플래시에 쓰는 순간 그 키로 파일을 암호화합니다 [2]. 칩마다 쓰는 방식은 아래와 같습니다 [2].

| 칩 | 방식 |
|---|---|
| A14~A18, M1 이후 | AES-256 XTS |
| A9~A13, S5 이후 | AES-128 XTS |

APFS 는 키를 extent 단위로 더 나눌 수 있어서 한 파일 안에서도 부분마다 키가 다를 수 있고 [2], 파일을 복제(clone)하면 양쪽이 새 키를 받아 새로 쓰는 데이터를 새 키로 씁니다 [3]. 파일을 열 때는 파일 시스템 키가 메타데이터를 풀어 감싼 파일별 키와 보호 등급을 드러내고, 파일 시스템 키는 Effaceable Storage 의 지울 수 있는 키로 한 번 더 감싸거나 Secure Enclave 의 재생 방지 기능이 지키는 미디어 키 감싸기 키를 씁니다 [3]. 파일 메타데이터는 모두 OS 를 처음 설치할 때나 "모든 콘텐츠 및 설정 지우기" 를 할 때 만든 무작위 키로 암호화하고, 이 키를 감싸는 키는 Secure Enclave 만 알며 기기를 지울 때마다 바뀝니다. 이렇게 키를 지우면 모든 파일을 암호학적으로 열 수 없게 됩니다 [3].

파일 하나를 지울 때도 같은 원리가 작동합니다. 파일을 지우면 iOS 는 그 파일의 키를 파일 메타데이터에서 곧바로 지웁니다 [1]. 그래서 지운 파일이 차지하던 블록은 내용이 남아 있더라도 키 없이 암호문으로만 남습니다. 키 구조 전체는 [데이터 보호](../../../01-foundations/storage/data-protection/index.md), 기기 초기화 흔적은 [초기화와 복원 흔적](../../../02-artifacts/system-account/erase-restore.md) 에서 다룹니다.

## 이유 2: SQLite 가 지운 내용을 정리함

파일은 그대로 있어도 DB 안에서 지운 행은 SQLite 설정과 동작에 따라 사라집니다. 흔적이 사라지는 경로는 아래와 같습니다 [4][5].

| 설정·동작 | 하는 일 | 남는 흔적 |
|---|---|---|
| secure_delete 켬 | 지운 내용을 0 으로 덮음. 기본값은 컴파일 옵션 `SQLITE_SECURE_DELETE` 로 정하고 보통 꺼져 있음 | FTS3·FTS5 같은 가상 표의 그림자 표에는 남을 수 있음 |
| secure_delete=FAST | 입출력이 늘지 않을 때만 0 으로 덮음 | b-tree 페이지는 지워지고 freelist 페이지에는 남음 |
| auto_vacuum=NONE(기본) | 지워도 파일 크기가 그대로이고 빈 페이지는 freelist 로 감 | freelist 에 남을 수 있음 |
| auto_vacuum=FULL | 커밋마다 freelist 페이지를 파일 끝으로 옮겨 잘라냄. 페이지 안 조각 정리는 하지 않음 | 페이지 안 빈 조각에는 남을 수 있음 |
| auto_vacuum=INCREMENTAL | incremental_vacuum 을 불러야 freelist 를 잘라냄 | 부르기 전까지 freelist 에 남음 |
| VACUUM | 파일 전체를 다시 만듦. 지운 뒤 흔적을 없애는 방법으로 권장됨 | 사라짐 |
| WAL 체크포인트 | WAL 프레임을 본 DB 에 합친 뒤 WAL 을 다시 씀. 자동 체크포인트 기본값은 WAL 이 1000 페이지 이상일 때 | 다시 쓴 프레임의 옛 판은 사라짐 |

auto_vacuum 은 표를 만들기 전에만 켤 수 있고 나중에 바꾸려면 VACUUM 이 필요합니다 [5]. 개별 iOS DB 가 이 가운데 어떤 설정을 쓰는지는 DB 마다 `PRAGMA auto_vacuum` 으로 확인합니다. iOS 12 이후 시스템이 지운 레코드를 거의 곧바로 정리해서 되살릴 가능성이 매우 낮다는 업체 설명이 있고, 메시지, Safari 북마크·탭·방문 기록, 통화 기록, 연락처가 예로 나옵니다 [1]. 다만 업체 주장이고 DB 마다 다를 수 있으므로 실제 DB 에서 freelist 페이지 수와 WAL 을 직접 확인합니다. 확인 절차는 [SQLite 레코드 되살리기](sqlite-records.md) 에 있습니다.

## 이유 3: 앱의 보관 기간

사진·메시지의 "최근 삭제된 항목" 은 정해진 기간이 지나면 항목을 영구 삭제하고, 그 뒤에는 이 보관 경로로 되살릴 수 없습니다. 앱별 기간은 [삭제 데이터 복구](index.md) 의 "한눈에 보기" 에 모았습니다.

## 이유 4: 수집 방식

로컬 백업은 `Manifest.db` 의 `Files` 표(fileID, domain, relativePath, flags, file)가 보여 주듯 파일 단위로 담깁니다. 그래서 논리 백업에는 플래시의 빈 공간이 들어가지 않고, 복구는 백업에 든 파일 안쪽에서만 할 수 있습니다. 백업이 암호화됐는지는 `Manifest.plist` 의 `IsEncrypted` 키로 드러납니다. 백업 구조는 [로컬 백업](../../../01-foundations/backups/local-backup/index.md), 수집 방식 선택은 [모바일 증거 확보](../../acquisition/mobile-acquisition/index.md) 를 봅니다.

## TRIM 과 플래시 정리

TRIM 이나 NAND 가비지 컬렉션이 iOS 플래시에서 지운 블록을 언제 비우는지는 Apple 공식 문서에 나오지 않습니다. 따라서 "TRIM 때문에 지워졌다" 는 문장은 근거 없이 쓰지 않습니다. 이유 1 의 설명대로라면 블록이 비워지기 전이라도 파일별 키가 없으면 암호문만 남으므로, 복구가 안 된 이유는 TRIM 보다 키 삭제로 설명하는 편이 공개 자료와 맞습니다.

## 함정과 한계

- "복구되지 않았다" 는 "지운 적이 없다" 도 "그런 데이터가 없었다" 도 아닙니다. 확인한 자리와 방법만큼만 말합니다.
- ElcomSoft 의 수치와 버전 설명은 업체 블로그 주장입니다. 보고서에 인용할 때는 업체 자료라고 밝힙니다.
- 한 앱에서 조각이 없었다고 다른 앱 DB 도 같다고 보면 안 됩니다. 설정과 쓰기 양이 DB 마다 다릅니다.

## 결과를 어떻게 해석하나

복구가 안 된 결과는 원인을 나눠 적습니다. 예를 들어 "이 DB 사본의 freelist 페이지 수는 0 이었고 WAL 파일은 수집물에 없었다" 처럼 확인한 사실을 쓰고, 그 원인을 "SQLite 가 정리했다" 나 "사용자가 흔적을 없앴다" 로 단정하지 않습니다. 사용자가 일부러 흔적을 없앴는지 따지는 방법은 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md), 보고서 문장 쓰는 법은 [포렌식 보고서](../../reporting/forensic-report.md) 를 봅니다.

## 참고 문헌

1. The Five Ways to Recover iPhone Deleted Data — ElcomSoft blog (2021-11) — https://blog.elcomsoft.com/2021/11/the-five-ways-to-recover-iphone-deleted-data/
2. Data Protection overview — Apple Platform Security — https://support.apple.com/guide/security/data-protection-overview-secf6276da8a/web
3. Data Protection in Apple devices — Apple Platform Security — https://support.apple.com/guide/security/data-protection-sece8608431d/web
4. Database File Format — SQLite — https://www.sqlite.org/fileformat2.html
5. Pragma statements supported by SQLite — https://www.sqlite.org/pragma.html
