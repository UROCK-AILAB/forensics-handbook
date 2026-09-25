---
title: "삭제 데이터 복구"
parent: "기법 · 분석"
nav_order: 1450
has_children: true
has_toc: false
---

# 삭제 데이터 복구 (Data Recovery)

## 한 줄 요약

Android 기기에서 지운 데이터가 어느 층에 남을 수 있는지, 그리고 파일 안의 잔재와 저장 장치의 블록을 되살리는 방법과 그 한계를 모은 묶음입니다.

## 왜 중요한가

지운 대화나 사진은 조사 질문의 중심에 자주 놓이지만, Android 에서는 되살릴 수 있는 범위가 좁습니다. 지운 데이터가 남을 수 있는 층은 크게 둘이고, 하나는 SQLite DB 파일의 빈 공간과 저널 파일처럼 살아 있는 파일 안, 다른 하나는 지운 파일의 블록이 덮이거나 TRIM 되기 전까지의 저장 장치입니다 [1][4].

두 층 모두 제약이 큽니다. 플랫폼 SQLite 는 지운 내용을 0 으로 덮고(`SQLITE_SECURE_DELETE`) 빈 페이지를 커밋마다 잘라 냅니다(`SQLITE_DEFAULT_AUTOVACUUM=1`, 현행 AOSP 기준) [2][3]. 저장 장치 층은 Android 10 이후 출시 기기에 의무인 파일 기반 암호화 (File-Based Encryption, FBE) 와 Android 11 이후 출시 기기에 의무인 메타데이터 암호화, 그리고 vold 의 유휴 유지보수가 보내는 주기적 TRIM 때문에 카빙이 어렵습니다 [5][6][7]. 그래서 실무에서 되살릴 수 있는 곳은 주로 파일 시스템 안에 아직 살아 있는 파일 안의 잔재이고, 예를 들면 앱이 자체 SQLite 를 쓰면서 secure_delete 를 켜지 않은 DB 나 WAL 파일에 남은 이전 페이지입니다 [1][2][3]. 어느 앱이 그런 설정을 쓰는지는 확인하지 못했습니다.

복구를 시도하기 전에 앱 자체의 휴지통도 확인할 곳입니다. 관찰한 폰의 `settings global` 에는 연락처 설정으로 보이는 `contact_setting_trash_bin_on` 키가 있었지만 키 이름만 봤고, 이 키의 뜻과 앱 휴지통에 지운 항목이 어떻게 남는지는 확인하지 못했습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5).

## 한눈에 보기

| 위치 | Android 버전 | 알려 주는 것 |
|---|---|---|
| SQLite DB 안의 빈 공간(freeblock·freelist·할당 안 된 공간) | 플랫폼 SQLite 는 secure_delete 와 auto_vacuum FULL 이 기본(현행 AOSP 기준, 도입 버전은 확인하지 못함) | 지운 레코드의 잔재 |
| 롤백 저널·WAL 파일 | 플랫폼 SQLite 는 1MiB 가 넘는 저널·WAL 을 1MiB 로 자름(현행 AOSP 기준). 롤백 저널이 남는지는 저널 모드에 따라 다름 | 고치기 전 페이지, 같은 페이지의 여러 판 |
| 논리 수집으로 얻은 파일 안(DB 의 BLOB, 캐시 파일) | 버전과 무관하게 파일 안을 찾음 | 파일 안에 든 다른 파일의 조각 |
| 암호화하지 않은 휴대용 SD 카드 | 휴대용 SD 카드의 암호화 여부는 확인하지 못함 | 카빙으로 되살린 파일(이름·시각 없음) |
| 내부 저장소 `/data` 물리 이미지 | Android 10 이후 출시 기기 FBE 의무, Android 11 이후 출시 기기 메타데이터 암호화 의무 | 키가 없으면 파일 내용과 파일 시스템 정보 모두 암호문 |

## 읽는 순서

1. [SQLite 레코드 되살리기](sqlite-records.md) — 살아 있는 DB 파일의 빈 공간·freelist·저널·WAL 에서 지운 레코드를 찾는 절차와, 플랫폼 SQLite 기본 설정이 흔적을 얼마나 지우는지 다룹니다.
2. [파일 카빙 (Carving)](carving.md) — 파일 서명으로 블록에서 파일을 잘라 내는 방법과, Android 에서 카빙이 쓸모 있는 곳과 없는 곳을 가립니다.
3. [TRIM과 암호화가 주는 한계](trim-encryption.md) — FBE·메타데이터 암호화·TRIM 이 저장 장치 층 복구를 어떻게 막는지와, 복구 전에 가능성을 가늠하는 순서를 정리합니다.

## 함께 볼 페이지

- [지운 대화와 사진 찾기](../../../04-scenarios/activity/deleted-content.md) — 이 묶음의 기법을 조사 질문에 맞춰 쓰는 흐름
- [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) — 지운 행위 자체를 가늠하는 시나리오
- [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) — SQLite 파일 형식
- [파일 시스템 (ext4·F2FS)](../../../01-foundations/storage/filesystems/index.md) — 블록과 파일 시스템 구조
- [저장 공간 암호화](../../../01-foundations/storage/encryption/index.md) — FBE 와 메타데이터 암호화 구조
- [모바일 증거 확보](../../acquisition/mobile-acquisition/index.md) — 논리 수집과 물리 수집의 차이
- [도구 검증](../../reporting/tool-validation.md) — 복구 도구의 결과를 확인하는 방법

## 참고 문헌

1. Database File Format (SQLite) — https://www.sqlite.org/fileformat2.html
2. Pragma statements supported by SQLite — https://www.sqlite.org/pragma.html
3. AOSP platform/external/sqlite, dist/Android.bp (main) — https://android.googlesource.com/platform/external/sqlite/+/refs/heads/main/dist/Android.bp
4. PhotoRec (CGSecurity wiki) — https://www.cgsecurity.org/wiki/PhotoRec
5. File-based encryption (Android Open Source Project) — https://source.android.com/docs/security/features/encryption/file-based
6. Metadata encryption (Android Open Source Project) — https://source.android.com/docs/security/features/encryption/metadata
7. AOSP platform/system/vold, IdleMaint.cpp (main) — https://android.googlesource.com/platform/system/vold/+/refs/heads/main/IdleMaint.cpp
