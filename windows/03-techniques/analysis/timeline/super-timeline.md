---
title: "여러 아티팩트 합친 타임라인"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 3290
---

# 여러 아티팩트 합친 타임라인 (Super Timeline)

상위 허브: [타임라인 작성 (Timeline)](index.md)

파일시스템·레지스트리·이벤트 로그·브라우저 기록처럼 출처가 다른 시각을 한 표에 모아 시간순으로 정렬한 것입니다. 표의 한 줄은 기록 하나이고, 줄마다 그 시각의 뜻과 출처를 함께 적습니다.

## 언제 쓰나

사건 시각 앞뒤에 PC 에서 무엇이 함께 일어났는지 넓게 볼 때, 아티팩트 하나로는 순서가 잡히지 않을 때, 한 아티팩트에서 찾은 시각을 다른 아티팩트로 확인할 때 씁니다.

줄 수가 아주 많아지므로 조사 질문과 시간 창을 먼저 정하고, 질문이 좁으면 해당 아티팩트 페이지부터 보는 편이 빠릅니다.

## 절차

1. **질문과 시간 창을 정합니다.** 예를 들어 "2024-03-15 09:00~11:00 UTC 에 어떤 파일이 생겼나" 처럼 정합니다.
2. **출처를 고릅니다.** 파일시스템([파일시스템 타임라인](filesystem-timeline-mft-usnjrnl-logfile.md)), 레지스트리([레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)), 이벤트 로그([이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md)), 실행 흔적([프리페치](../../../02-artifacts/execution/prefetch/index.md)), 브라우저([크롬 계열 브라우저](../../../02-artifacts/browsers/chrome-edge-whale/index.md))가 흔한 출처입니다. 수집 범위에 없는 출처는 따로 적어 둡니다.
3. **시간 기준을 맞춥니다.** 출처마다 시각을 저장하는 기준이 다릅니다. 합치기 전에 [시간대·시계 오차 보정](time-normalization.md)에 따라 한 기준으로 맞춥니다.
4. **시각을 뽑아 모읍니다.** 공개 도구 plaso 가 그 예입니다. plaso 에서는 psort 가 결과를 여러 형식으로 내보냅니다(참고 1).
5. **출력 형식과 필드를 고릅니다.** 아래 "출력 형식" 절을 봅니다.
6. **걸러 냅니다.** 시간 창, 출처 종류(source·sourcetype), 사용자, 키워드로 줄 수를 줄입니다.
7. **줄마다 시각의 뜻을 확인합니다.** timestamp_desc 필드나 l2t_csv 의 type 열을 읽습니다.
8. **중요한 줄은 원래 아티팩트로 돌아가 확인합니다.** 도구가 해석한 값과 원본 값을 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../reporting/tool-validation.md)을 봅니다.

## 출력 형식

### psort 가 내보내는 형식

plaso 문서에 나온 psort 출력 형식은 아래 열두 가지입니다(참고 1).

`dynamic`, `json`, `json_line`, `kml`, `l2tcsv`, `l2ttln`, `null`, `rawpy`, `opensearch`, `opensearch_ts`, `tln`, `xlsx`

dynamic 형식에서는 내보낼 필드를 고를 수 있으며(참고 1), 고를 수 있는 필드는 date, datetime, display_name, filename, hostname, inode, macb, message, message_short, source, source_long, tag, time, timestamp_desc, timezone, username 입니다(참고 1). timestamp_desc 필드는 그 이벤트 시각이 무엇을 뜻하는지 적는데, "Creation Time", "Program Execution Duration" 이 그 예입니다(참고 1). 출력 시각이 어느 시간대인지는 결과 파일의 timezone 필드로 확인합니다.

### l2t_csv 의 열 17개

l2t_csv 는 열 17개가 순서대로 고정된 CSV 형식입니다(참고 1, 참고 2).

| 순서 | 열 | 뜻 (참고 2) |
|---|---|---|
| 1 | date | 날짜. MM/DD/YYYY |
| 2 | time | 시각. 24시간제 HH:MM:SS |
| 3 | timezone | 출력 시간대 또는 입력 파일의 시간대 |
| 4 | MACB | 글자 뜻은 [파일 시각 네 가지와 변화 규칙](macb-timestamp-rules.md) |
| 5 | source | 큰 분류. LOG, WEBHIST, REG 등 |
| 6 | sourcetype | 자세한 출처. 예: "NTUSER.DAT Registry" |
| 7 | type | 시각 종류. 예: "Last Accessed", "Last Written" |
| 8 | user | — |
| 9 | host | — |
| 10 | short | 짧은 설명 |
| 11 | desc | 해석한 전체 내용 또는 로그 줄 원문 |
| 12 | version | 시각 객체 버전 (현재 2) |
| 13 | filename | — |
| 14 | inode | — |
| 15 | notes | — |
| 16 | format | 파일을 해석한 입력 모듈 이름 |
| 17 | extra | 나머지 해석 정보를 이어 붙인 열 |

- date 열은 월/일/연 순서입니다. 연-월-일 순서와 헷갈리지 않도록 옮겨 적을 때 주의합니다.
- 이 형식은 초 단위까지만 담기 때문에 정밀도가 떨어지고 MACB 묶음에도 영향을 줍니다(참고 2). 초 아래 자리가 필요한 분석이면 다른 출력 형식을 고릅니다.

## 함정과 한계

1. **시간 기준이 섞입니다.** 출처마다 UTC 로 적기도 하고 현지 시각으로 적기도 합니다. 맞추지 않고 합치면 순서가 뒤바뀝니다.
2. **같은 파일이 여러 줄로 나옵니다.** 한 파일의 $SI·$FN 시각과 USN 레코드가 모두 들어오기 때문입니다. 줄이 여러 개라고 같은 행동이 여러 번 있었다고 읽지 않습니다.
3. **해상도가 다른 출처가 섞입니다.** l2t_csv 는 초 단위입니다(참고 2). FAT 처럼 시각이 더 거친 출처도 있습니다([파일 시각 네 가지와 변화 규칙](macb-timestamp-rules.md)). 같은 초 안의 줄끼리는 순서를 단정할 수 없습니다.
4. **이웃한 줄을 원인과 결과로 읽습니다.** 시각이 가깝다는 사실로는 순서만 알 수 있습니다. 인과는 다른 근거로 보입니다.
5. **기록 시각을 행동 시각으로 읽습니다.** type 이 "Last Written" 이면 그 기록이 쓰인 때입니다. 사용자가 그때 무엇을 했다고 단정하지 않습니다.
6. **도구가 읽지 못한 출처는 빠집니다.** 표의 빈 구간이 "아무 일도 없었다" 는 뜻은 아닙니다. 어떤 출처를 넣었는지 보고서에 적습니다.
7. **시간대 표시를 확인하지 않습니다.** l2t_csv 의 timezone 열은 출력 시간대일 수도 있고 입력 파일의 시간대일 수도 있습니다(참고 2).
8. **조작된 시각도 그대로 들어옵니다.** 도구는 적힌 값을 정렬할 뿐입니다. 의심 가는 파일은 [시각 조작 탐지](timestomping.md)로 따로 봅니다.

## 결과를 어떻게 해석하나

표의 한 줄은 "이 출처에 이런 뜻의 시각이 이 값으로 적혀 있다" 는 사실입니다. 여러 출처가 같은 시간대에 같은 대상을 가리키면 해석을 뒷받침하고, 한 출처만 가리키면 그 출처의 한계를 함께 적습니다.

- 쓸 수 있는 문장(예): "2024-03-15 10:00 UTC 전후로 USN 저널의 파일 생성 기록과 레지스트리 키 변경 기록이 함께 있습니다."
- 쓰면 안 되는 문장(예): "사용자가 10:00 에 프로그램을 실행해 파일을 만들었습니다."
- 보고서에 타임라인을 싣는 방법은 [분석 보고서 작성](../../reporting/forensic-report.md)을 봅니다.

## 참고 문헌

1. Plaso documentation, "Output and formatting" — https://plaso.readthedocs.io/en/latest/sources/user/Output-and-formatting.html
2. Forensics Wiki, "L2T CSV" — https://forensics.wiki/l2t_csv/
