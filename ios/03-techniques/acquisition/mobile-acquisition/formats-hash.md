---
title: "결과물 형식과 해시"
parent: "모바일 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1210
---

# 결과물 형식과 해시 (Extraction Formats·Hash)

아이폰 수집 결과물이 어떤 모양으로 나오는지와, 그 결과물이 보관하는 동안 바뀌지 않았음을 보이려고 해시를 언제 어떻게 남기는지를 다룹니다.

## 언제 쓰나

로컬 백업이나 sysdiagnose 를 얻은 직후, 그리고 결과물을 옮기거나 분석하기 전에 이 페이지를 봅니다. 같은 기기를 두 번 수집했는데 해시가 다를 때, 도구마다 결과가 다를 때도 여기서 해석합니다.

## 결과물 형식

| 수집 방식 | 결과물 모양 | 자세히 |
|---|---|---|
| 로컬 백업 | 폴더 하나. 최상위에 plist 와 `Manifest.db`, 그 아래 해시 이름의 하위 폴더 | [백업으로 수집](backup-acquisition.md) |
| sysdiagnose | `.tar.gz` 파일 하나 | [sysdiagnose로 수집](sysdiagnose-collection.md) |
| 파일 시스템 추출 | 이번에 연 자료로 확인하지 못함 | 이 페이지 "함정과 한계" |

관찰한 백업도 최상위 plist 와 `Manifest.db`, `Manifest.db-shm`, `Manifest.db-wal` 이 있는 폴더 모양이었습니다. (확인 범위: iOS 27.0) 로컬 백업은 파일이 많이 들어 있는 폴더라서, 폴더 전체를 zip·tar 같은 묶음 하나로 만든 뒤 해시할지, 파일마다 해시 목록을 만들지 정해야 합니다. 이번에 연 출처에서는 둘 중 하나를 권하는 내용을 찾지 못해서, 어느 쪽을 골랐는지와 그 방법을 수집 기록에 적어 두면 뒤에서 다른 사람이 같은 값을 다시 계산할 수 있습니다.

## 절차

1. 결과물을 증거 저장소에 옮긴 직후, 분석 도구로 열기 전에 해시를 계산합니다.
2. 쓴 도구가 해시를 계산해 주지 않으면(포렌식용이라는 이름이 붙은 도구라도) `sha1sum` 같은 도구로 따로 해시를 만듭니다.
3. 계산한 해시와 방법(묶음 해시인지 파일별 목록인지, 알고리즘)을 수집 기록에 적습니다.
4. 분석은 해시를 남긴 원본이 아니라 사본으로 합니다.
5. 보관 기간 중 결과물을 옮기거나 제출할 때마다 해시를 다시 계산해 처음 값과 맞춰 봅니다.

NIST SP 800-101 Rev.1 은 포렌식 도구가 기기에 쓰기를 막아 원본을 지키고, 만든 증거 파일에 암호학적 해시를 계산해 보관 기간 내내 값이 그대로인지 다시 확인한다고 적습니다. 위 절차는 이 원칙을 아이폰 결과물에 옮긴 것입니다.

## 해시를 계산하는 예

아래는 해시를 남기는 방법의 예시이고, 결과 값은 검체마다 다릅니다.

```
# sysdiagnose 처럼 파일 하나인 결과물
sha256sum sysdiagnose_....tar.gz > sysdiagnose.sha256

# 로컬 백업 폴더를 파일별 해시 목록으로 남기는 경우
cd <백업 폴더>
find . -type f -print0 | sort -z | xargs -0 sha256sum > ../backup-files.sha256

# 나중에 다시 맞춰 볼 때
sha256sum -c ../backup-files.sha256
```

## 함정과 한계

**같은 기기를 두 번 수집해도 전체 해시는 다릅니다.** 모바일 기기는 켜져 있는 동안 시계 같은 자료를 계속 바꾸므로, 연달아 두 번 수집해도 결과물 전체의 해시는 달라집니다. 개별 파일·폴더 단위 해시는 대체로 같게 나오니, 해시가 어긋나면 항목 단위로 비교해 무엇이 달라졌는지 확인합니다. 도구마다 보고 형식이 달라 도구끼리 해시를 대조하기는 어렵고, 도구 자체를 검증하려면 여러 도구의 결과를 견줘 봅니다. 그 방법은 [도구 검증](../../reporting/tool-validation.md)에서 다룹니다.

**백업 안 파일 이름은 무결성 해시가 아닙니다.** 로컬 백업 안의 파일 이름(`fileID`)은 SHA‑1 값처럼 보이지만, 파일 내용이 아니라 도메인과 상대 경로를 이어 계산한 값입니다. 파일 내용이 바뀌어도 이름은 그대로라서, 이 값을 증거 무결성 해시로 보고서에 쓰지 않습니다. 계산식은 [백업으로 수집](backup-acquisition.md)에 있습니다.

**`Manifest.db` 는 열기만 해도 바뀔 수 있습니다.** 관찰한 백업에는 `Manifest.db` 옆에 `-wal`, `-shm` 파일이 붙어 있었습니다. (확인 범위: iOS 27.0) SQLite 는 WAL 파일이 있는 DB 를 열 때 WAL 내용을 본 파일에 옮겨 적을 수 있어서, 해시를 남긴 원본을 바로 열면 값이 바뀔 수 있습니다. WAL 동작은 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

**파일 시스템 추출 결과물은 따로 해시를 남깁니다.** tar·zip 이나 도구 고유 형식 같은 결과물의 구조는 이번에 연 자료로 확인하지 못해서 여기서 다루지 않습니다. 이런 결과물을 받으면 도구가 계산한 해시와 별개로, 받은 파일 그대로의 해시를 따로 남깁니다.

## 시각 표기

결과물에 붙은 시각은 기준이 서로 달라서 수집 기록에 옮길 때 기준을 함께 적습니다. sysdiagnose 파일 이름의 시각은 현지 시각에 UTC 와의 차이(예: `+0200`)를 붙인 값입니다. 백업 plist 의 `Date`·`Last Backup Date` 값이 어떤 시간대로 적히는지는 이번 자료로 확인하지 못했고, plist 날짜 형식의 일반 원리는 [시각 값](../../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

## 결과를 어떻게 해석하나

해시가 일치하면 "해시를 계산한 뒤로 결과물이 바뀌지 않았다" 는 것까지만 말할 수 있고, 수집 과정에서 기기 자료가 바뀌지 않았다는 뜻은 아닙니다. 두 번 수집한 결과의 전체 해시가 다르면 먼저 파일 단위로 비교하고, 달라진 파일이 시계·로그처럼 기기가 늘 바꾸는 자료인지 확인한 뒤 보고서에 그 사실을 적습니다. 해시 값과 방법을 보고서에 싣는 형식은 [포렌식 보고서](../../reporting/forensic-report.md)에서 다룹니다.

## 참고 문헌

- NIST SP 800-101 Rev.1, Guidelines on Mobile Device Forensics — https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-101r1.pdf
- Reverse Engineering the iOS Backup — Rich Infante (2017) — https://www.richinfante.com/2017/3/16/reverse-engineering-the-ios-backup
- Extracting and Analyzing Apple sysdiagnose Logs — ElcomSoft blog (2025-06) — https://blog.elcomsoft.com/2025/06/extracting-and-analyzing-apple-unified-logs/
