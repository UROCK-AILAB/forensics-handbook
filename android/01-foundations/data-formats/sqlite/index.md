---
title: "SQLite 데이터베이스"
parent: "기반 · 데이터 저장 형식"
nav_order: 150
has_children: true
has_toc: false
---

# SQLite 데이터베이스 (SQLite)

## 한 줄 요약

SQLite 데이터베이스는 표와 색인을 파일 하나에 담는 데이터베이스이고, 파일은 같은 크기의 페이지로 나뉘며 맨 앞 16바이트가 `SQLite format 3\000` 입니다 [1]. 이 허브는 SQLite 파일과 곁 파일에서 무엇을 읽을 수 있는지 정리하고, 구조·곁 파일·지운 레코드·암호화를 다루는 네 하위 페이지로 안내합니다.

## 왜 중요한가

앱과 시스템이 남긴 기록 가운데 SQLite 파일로 된 것을 읽을 때, 이 형식을 손으로 읽을 줄 알면 도구가 보여 준 행이 파일의 어디에서 나왔는지 확인하고 도구가 보여 주지 않는 자리까지 볼 수 있습니다. 어떤 파일이 SQLite 인지는 이름이 아니라 첫 16바이트로 가립니다.

분석에서 놓치기 쉬운 점은 두 가지입니다. 하나는 곁 파일입니다. 주 DB 파일 옆에는 롤백 저널(-journal), WAL(-wal), WAL 색인(-shm)이 붙을 수 있고 [1], 주 파일만 복사하고 -wal 과 -shm 을 빼면 WAL 에만 있던 커밋된 거래를 잃습니다 [2]. 다른 하나는 지운 데이터입니다. 지운 행은 빈 페이지 목록, 페이지 안의 빈 조각, WAL 의 옛 프레임, 롤백 저널의 원래 페이지 사본에 남을 수 있지만 [1], Android 플랫폼에 들어 있는 SQLite 라이브러리는 지운 내용을 0 으로 덮는 secure_delete 와 빈 페이지를 잘라내는 자동 정리를 켜고 빌드해서(현행 AOSP 기준) [3], 플랫폼 SQLite 를 쓰는 DB 에서는 되살릴 것이 적을 수 있습니다. 앱이 SQLCipher 같은 자기 라이브러리를 따로 넣어 쓰면 이 빌드 옵션을 따르지 않습니다.

앱 DB 를 찾을 폴더는 [앱 데이터 폴더 구조](../../storage/app-data-layout.md)에서 다룹니다. 삼성 One UI 가 SQLite 설정을 따로 바꾸는지도 확인하지 못했습니다.

## 한눈에 보기

| 위치 | Android 버전 | 알려 주는 것 |
|---|---|---|
| 주 DB 파일 | 현행 AOSP 의 플랫폼 SQLite 는 secure_delete 와 auto_vacuum=FULL 을 기본으로 빌드 [3]. 버전별 차이는 확인 못 함 | 마지막 체크포인트까지의 표·색인, 빈 페이지와 빈 조각에 남은 옛 레코드 |
| 같은 폴더의 `이름-journal` | 현행 AOSP 의 WAL 이 아닐 때 기본 저널 모드는 TRUNCATE [4] | 거래가 바꾸기 전의 원래 페이지 |
| 같은 폴더의 `이름-wal` | Android 9 에서 호환 WAL 도입 [5] | 커밋했지만 주 파일로 옮기지 않은 새 페이지, 같은 페이지의 옛 버전 프레임 |
| 같은 폴더의 `이름-shm` | WAL 과 함께 생김 | WAL 에서 페이지를 찾는 일시 색인. 영구 상태는 아님 [1] |
| settings global 의 `sqlite_compatibility_wal_flags` | Android 16 에서 키가 있음을 관찰, 값은 가려져 있어 모름 (확인 범위: SM-S937N, Android 16, One UI 8.5) | 호환 WAL 과 WAL 자르기 기준을 조정하는 설정 |

## 읽는 순서

1. [페이지와 레코드 (B-tree·Record)](b-tree-record.md) — 파일 머리 100바이트의 칸, B-tree 페이지 종류와 셀 짜임, 레코드의 직렬 타입, 헥스로 셀 하나를 푸는 법을 다룹니다.
2. [WAL과 저널 (WAL·Journal)](wal-journal.md) — 롤백 저널·WAL·WAL 색인의 구조와 저널 모드, 체크포인트, Android 의 기본 저널 설정과 호환 WAL, 곁 파일을 함께 확보하는 이유를 다룹니다.
3. [지운 레코드 되살리기 (Freelist·Freeblock)](freelist-freeblock.md) — 빈 페이지 목록과 페이지 안 빈 조각의 구조, 자동 정리와 secure_delete 가 결과에 주는 영향, 되살린 레코드를 해석하는 법을 다룹니다.
4. [암호화된 SQLite (SQLCipher)](sqlcipher.md) — 암호화된 DB 를 알아보는 법, 페이지마다 붙는 IV·HMAC, 버전마다 다른 기본 설정을 다룹니다.

> 그림 자리: 주 DB 파일과 -journal·-wal·-shm 이 한 폴더에 놓인 모습과, 각 파일이 담는 시점(바꾸기 전·마지막 체크포인트·마지막 커밋)

## 함께 볼 페이지

- [앱 데이터 폴더 구조 (/data/data·/data/user)](../../storage/app-data-layout.md) — DB 파일을 찾을 앱 폴더
- [설정 값 (Settings Global·Secure·System)](../../../02-artifacts/system-account/settings.md) — `sqlite_compatibility_wal_flags` 가 들어 있는 settings global
- [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md) — 주 파일과 곁 파일을 함께 확보하는 절차
- [앱 데이터 분석 (App Data Analysis)](../../../03-techniques/analysis/app-data-analysis/index.md), [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md) — DB 를 읽고 지운 행을 되살리는 분석 기법
- [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../value-decoding/time-values.md) — DB 칸에 적힌 시각 값을 바꾸는 법
- [지운 대화와 사진 찾기 (Deleted Content)](../../../04-scenarios/activity/deleted-content.md) — 이 형식을 쓰는 조사 시나리오

## 참고 문헌

1. Database File Format — SQLite, https://www.sqlite.org/fileformat2.html
2. Write-Ahead Logging — SQLite, https://www.sqlite.org/wal.html
3. Android.bp — AOSP external/sqlite dist (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_external_sqlite/main/dist/Android.bp
4. config.xml — AOSP frameworks/base core/res (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/res/res/values/config.xml
5. Compatibility write-ahead logging for apps — Android Open Source Project, https://source.android.com/docs/core/perf/compatibility-wal
