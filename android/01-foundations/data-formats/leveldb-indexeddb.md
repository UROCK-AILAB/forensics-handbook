---
title: "LevelDB와 IndexedDB"
parent: "기반 · 데이터 저장 형식"
nav_order: 230
---

# LevelDB와 IndexedDB (LevelDB·IndexedDB)

## 한 줄 요약

LevelDB 는 최근 변경을 덧붙여 적는 로그와 키로 정렬된 테이블 파일로 이루어진 키-값 저장소이고, Chrome 과 Chromium 계열 브라우저는 웹 페이지가 쓰는 IndexedDB 를 이 위에 저장합니다.

## 이 형식을 쓰는 아티팩트

IndexedDB 는 웹 개발자가 브라우저 안에 데이터를 저장할 때 쓰는 API 이고, Chrome 과 Chromium 계열 브라우저는 IndexedDB 데이터를 LevelDB 폴더에 저장합니다. 그래서 웹 서비스가 브라우저에 넣어 둔 데이터가 이 폴더에 남을 수 있습니다.

Android 기기에서 브라우저나 앱이 이 폴더를 어느 경로에 두는지, 폴더 이름을 어떻게 짓는지는 이 페이지의 출처로 확인하지 않았습니다. 브라우저별 위치는 [크롬](../../02-artifacts/browsers/chrome/index.md) 과 [그 밖의 브라우저](../../02-artifacts/browsers/other-browsers.md) 에서 다루고, 앱 데이터 폴더의 짜임은 [앱 데이터 폴더 구조](../storage/app-data-layout.md) 에서 다룹니다.

## 구조

### 폴더 안의 파일

LevelDB 데이터베이스 하나는 폴더 하나이고, 그 안에 다음 파일이 있습니다.

| 파일 | 내용 |
|---|---|
| `*.log` | 최근 변경을 차례로 덧붙인 기록. 약 4MB 가 되면 정렬된 테이블로 바뀝니다 |
| `*.ldb` | 키로 정렬된 항목(값 또는 삭제 표시)을 담은 정렬 테이블 |
| `MANIFEST-######` | 각 레벨을 이루는 정렬 테이블 목록과 키 범위 같은 메타데이터 |
| `CURRENT` | 최신 MANIFEST 파일 이름을 적은 텍스트 파일 |
| `LOG`, `LOG.old` | 동작 중에 남긴 안내 메시지 |
| `LOCK`, `*.dbtmp` | 그 밖의 용도 |

현재 `.log` 의 내용은 메모리 안의 표 (memtable) 에도 사본이 있고, 읽을 때마다 이 사본을 확인합니다.

### 레벨과 압축

정렬 테이블은 레벨로 나뉩니다. level-0 파일은 서로 키 범위가 겹칠 수 있고, 4개가 모이면 level-1 과 합칩니다. level-L(L 은 1 이상)은 전체 크기가 10^L MB(10MB, 100MB, ...)를 넘으면 다음 레벨과 합치고, 합칠 때 새 파일은 약 2MB 마다 만듭니다. 이렇게 합치는 일을 압축 (compaction) 이라고 부르고, 압축이 끝날 때와 복구가 끝날 때 `RemoveObsoleteFiles()` 가 어느 레벨에서도 쓰지 않는 로그와 테이블 파일을 지웁니다.

> 그림 자리: `.log` 가 level-0 테이블이 되고, level-0 네 개가 level-1 로 합쳐지며, 쓰지 않게 된 파일이 지워지는 흐름

### 키 끝의 메타데이터

| 위치 | 크기 | 내용 |
|---|---|---|
| 키 앞부분 | 가변 | 앱이 정한 키 |
| 키 끝 | 8바이트 | 56비트 순번 (sequence number) 과 상태 |

상태 값은 0 이면 삭제, 1 이면 유효한 값이고, 순번이 있어서 한 키가 어떤 순서로 바뀌었는지 알 수 있습니다. 이 짜임은 정렬 테이블(`.ldb`) 안의 키에 해당하고, `.log` 에서는 쓰기 묶음 (write batch) 머리에 첫 순번과 레코드 개수가 한 번 적히고, 레코드마다 상태 1바이트가 키 앞에 옵니다.

### 압축된 데이터

`.ldb` 안의 데이터는 Snappy 로 압축될 수 있습니다. 압축을 풀지 않은 채 문자열을 찾거나 조각을 카빙하면 값이 잘 걸리지 않습니다.

## 읽는 법

1. `CURRENT` 를 열어 최신 MANIFEST 파일 이름을 읽습니다.
2. MANIFEST 에서 지금 쓰는 정렬 테이블 목록을 확인하고, 폴더에 있는 `.ldb` 와 맞춰 봅니다. 목록에 없는 파일이 남아 있으면 따로 표시해 둡니다(아래 "포렌식에서 중요한 점").
3. `.log` 의 레코드와 `.ldb` 의 항목을 모두 읽고, `.ldb` 는 Snappy 압축을 풀고 읽습니다.
4. 키마다 순번 순서로 늘어놓습니다. 상태가 0 인 항목은 삭제 표시이고, 그보다 순번이 작은 같은 키의 항목이 지워지기 전 값입니다.
5. IndexedDB 라면 키와 값을 브라우저의 직렬화 형식으로 한 번 더 풀어야 합니다. 이 직렬화 형식과 키 인코딩은 이 페이지에서 다루지 않고, 도구 결과를 알려진 데이터로 확인해 씁니다.

원본 폴더를 LevelDB 라이브러리로 바로 열면 복구나 압축이 돌면서 쓰지 않는 파일을 지울 수 있습니다. 원본은 해시로 고정해 두고 사본에서 엽니다.

## 포렌식에서 중요한 점

LevelDB 는 값을 지울 때 그 키에 삭제 표시를 남기고, 삭제 표시는 옛 테이블에 남은 이전 값을 가리려고 계속 유지합니다. 그래서 삭제 표시가 있어도 이전 값이 다른 `.log` 나 `.ldb` 파일에 아직 남아 있을 수 있고, 순번을 따라가면 지워진 키를 되살릴 수 있습니다.

이전 값이 남는 기간은 압축 시점에 달려 있습니다. 압축이나 복구가 끝나면 쓰지 않는 파일을 지우고, 그 뒤로는 파일 시스템 수준의 복구로 넘어갑니다. 이 부분은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다. 폴더에 남아 있지만 현재 MANIFEST 에 없는 파일은 정리되기 전에 남은 옛 파일일 수 있어 따로 살펴볼 만합니다.

현재 `.log` 에는 아직 정렬 테이블로 바뀌지 않은 최근 변경이 들어 있습니다. 앱이 비정상으로 끝났거나 기기가 꺼진 직후 확보했다면 마지막 변경이 `.log` 에만 있을 수 있으니, `.ldb` 만 읽고 끝내지 않습니다.

LevelDB 레코드에는 시각 필드가 없고 순번만 있습니다. 순번은 변경의 앞뒤를 알려 주지만 언제 바뀌었는지는 알려 주지 않으며, 값 안에 든 시각의 형식은 그 값을 쓴 웹 서비스나 앱이 정합니다. 단위는 [시각 값](../value-decoding/time-values.md) 에서 확인합니다.

## 함정

`*.log` 와 `LOG` 는 이름이 비슷하지만 전혀 다른 파일입니다. `*.log` 는 데이터 변경 기록이고, `LOG` 와 `LOG.old` 는 동작 안내 메시지입니다.

삭제 표시가 있다고 해서 값이 사라졌다고 결론 내리면 안 되고, 반대로 옛 값이 보인다고 해서 그 값이 현재 값이라고 보고해서도 안 됩니다. 순번과 상태를 함께 적어 "지우기 전에 있던 값" 인지 "현재 값" 인지 나눠 씁니다.

`.ldb` 가 Snappy 로 압축될 수 있어서, 이미지 전체를 키워드로 찾았을 때 결과가 없어도 값이 없다는 뜻은 아닙니다. 검색 방법은 [콘텐츠 검색](../../03-techniques/analysis/content-search.md) 에서 다룹니다.

순번을 시각처럼 쓰면 안 됩니다. 순번이 큰 항목이 나중에 쓰였다는 것만 알 수 있고, 두 항목 사이의 시간 간격은 알 수 없습니다.

## 도구

LevelDB 폴더를 읽어 유효한 항목과 삭제 표시, 옛 값을 순번과 함께 뽑아 주는 도구를 씁니다. 이 페이지는 특정 도구를 정하지 않고, 어떤 도구를 쓰든 `.log` 까지 읽는지, 삭제 표시와 옛 값을 보여 주는지, Snappy 압축을 푸는지 알려진 데이터로 확인합니다. 확인 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 참고 문헌

1. LevelDB Implementation notes (doc/impl.md) — google/leveldb, https://raw.githubusercontent.com/google/leveldb/main/doc/impl.md
2. Hang on! That's not SQLite! Chrome, Electron, and LevelDB — CCL Solutions Group (Alex Caithness), https://www.cclsolutionsgroup.com/post/hang-on-thats-not-sqlite-chrome-electron-and-leveldb
3. write_batch.cc — google/leveldb, https://raw.githubusercontent.com/google/leveldb/main/db/write_batch.cc
