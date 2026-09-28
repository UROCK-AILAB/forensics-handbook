---
title: "로그 지우기"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 2400
---

# 로그 지우기 (Log Clearing)

누군가 통합 로그 (Unified Log)를 지웠는지, 지웠다면 어느 구간과 어떤 종류의 로그가 비었는지를 묻는 조사를 다룹니다. `log stats` 와 `log show` 로 남은 이벤트의 분포와 끊긴 구간의 경계를 찾고, 가장 이른 로그 시각을 맥을 쓰기 시작한 시기와 비교합니다. 그다음 KnowledgeC·바이옴·전원 기록으로 공백 구간에도 맥을 쓴 흔적이 있는지 보고, 터미널 명령 기록과 파일 시스템 이벤트에서 지운 행위를 직접 가리키는 흔적을 찾습니다.

## 조사 질문

누군가 통합 로그 (Unified Log)를 지웠는지, 지웠다면 어느 구간과 어떤 종류의 로그가 비었는지, 그리고 그 공백을 다른 기록으로 얼마나 메울 수 있는지를 묻습니다. 로그가 비어 있다는 관찰과 누군가 일부러 지웠다는 판단 사이에는 거리가 있어서, 이 페이지는 공백을 찾는 순서와 함께 공백을 삭제로 단정하면 안 되는 경우를 다룹니다.

## 먼저 확인할 것

처음에 볼 것은 수집 범위입니다. 통합 로그는 저장소 폴더와 문자열 파일이 함께 있어야 읽을 수 있어서, 확보본에 두 쪽이 다 들어 있는지부터 확인합니다. 저장 위치와 파일 구성은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있고, 저장소를 빠짐없이 확보하는 순서는 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)에 있습니다.

그다음 macOS 버전과 시간대를 적어 둡니다. 로그 시각을 다른 기록과 맞춰 볼 때 시간대가 다르면 없는 공백이 생기거나 있는 공백이 가려지기 때문이고, 시간대를 읽는 법은 [시간대와 시계 설정 (Time Zone·NTP)](../../../02-artifacts/system-account/time-zone.md)에 있습니다. 시계 자체를 바꾼 흔적이 보이면 공백을 해석하기 전에 [시스템 시각 바꾸기 (Time Change)](time-change.md)를 먼저 확인합니다.

## `log erase` 가 지우는 범위

macOS 의 `log` 명령에는 시스템의 로그 데이터를 지우는 `erase` 동작이 있습니다 [1]. 인자에 따라 지우는 범위가 달라서, 비어 있는 로그의 모양을 보고 어떤 방식이 쓰였을 가능성이 있는지 추정할 때 아래 표를 씁니다.

| 인자 | 지우는 범위 [1] |
|---|---|
| 없음 | 주 로그 저장소 (main log datastore)와 inflight 로그 데이터 |
| `--all` | 주 로그 저장소, inflight 로그 데이터, TTL (time-to-live) 데이터, fault·error 내용 |
| `--ttl` | TTL 로그 내용만 |

옵션 설명대로라면 `--ttl` 만 쓴 경우 TTL 이 붙지 않은 주 저장소의 로그는 남고, 인자 없이 쓴 경우 TTL 데이터와 fault·error 내용은 대상에 들지 않습니다. 이 구분은 옵션 문구에서 끌어낸 해석이라, 보고서에는 "이 모양은 이런 방식과 들어맞는다" 수준으로만 씁니다.

`log erase` 를 실행하려면 루트 권한이 필요한지, 실행했다는 사실이 통합 로그나 다른 곳에 남는지는 실제 데이터로 확인해야 합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 통합 로그 저장소 | 남아 있는 가장 이른 시각, 구간별 이벤트 분포 | [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md) |
| 2 | `log stats` 출력 | 저장소나 아카이브에 든 이벤트의 분포 [1] | 아래 분석 흐름 |
| 3 | 터미널 명령 기록 | `log erase` 를 입력한 흔적이 남았는지 | [터미널 명령 기록 (zsh_history·bash_sessions)](../../../02-artifacts/execution/shell-history.md) |
| 4 | 파일 시스템 이벤트 | 로그 저장소 폴더의 파일이 한꺼번에 지워진 흔적이 있는지 | [파일 시스템 이벤트 (FSEvents)](../../../02-artifacts/filesystem/fsevents/index.md) |
| 5 | 예전 텍스트 로그 | 통합 로그 밖의 텍스트 로그가 남았는지 | [예전 시스템 로그 (ASL·syslog)](../../../01-foundations/data-formats/asl-syslog.md), [설치 로그 (install.log)](../../../02-artifacts/logs/install-log.md) |
| 6 | 로그 밖의 활동 기록 | 공백 구간에도 맥을 쓴 흔적이 있는지 | [KnowledgeC (knowledgeC.db)](../../../02-artifacts/execution/knowledgec/index.md), [바이옴 (Biome)](../../../02-artifacts/execution/biome/index.md), [전원·잠자기 기록 (pmset)](../../../02-artifacts/logs/power-events.md) |

3번과 4번은 흔적이 나오면 근거로 쓰고, 나오지 않아도 삭제가 없었다는 뜻으로 읽지 않습니다.

## 분석 흐름

1. 확보한 저장소를 원본과 따로 떼어 둔 사본에서 다루고, 저장소 폴더와 문자열 파일이 모두 있는지 확인합니다.
2. `log stats` 로 저장소 전체의 이벤트 분포를 봅니다. 출력 방식에는 `--overview`, `--per-book`, `--per-file`, `--sender`, `--process`, `--predicate` 가 있고 `--sort` 로 이벤트 수(events)나 바이트(bytes) 순으로 정렬할 수 있어서 [1], 파일별 분포를 보면 특정 시기의 파일만 빠진 곳이 드러납니다.
3. `log show` 에 `--start`·`--end`("YYYY-MM-DD HH:MM:SS" 형식)나 `--last` 를 주어 기간을 좁히고, 필요하면 `--predicate` 로 조건을 걸어 [1] 이벤트가 끊긴 구간의 앞뒤 경계를 찾습니다.
4. 남아 있는 가장 이른 로그 시각을 맥을 쓰기 시작한 시기와 비교합니다. 사용 시작 시기는 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../../02-artifacts/system-account/os-version-install-history.md)이나 사용자 계정 생성 기록으로 추정합니다.
5. 공백 구간에 로그 밖의 활동 기록이 있는지 확인합니다. 앱 사용·전원 기록이 이어지는데 통합 로그만 비어 있으면 로그만 따로 사라졌을 가능성이 커지고, 모든 기록이 함께 비어 있으면 맥이 꺼져 있었을 가능성도 함께 봅니다.
6. 명령 기록과 파일 시스템 이벤트에서 지운 행위를 직접 가리키는 흔적을 찾고, 찾은 흔적의 시각이 공백의 경계와 맞는지 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)으로 맞춰 봅니다.

## 흔한 오판

가장 흔한 오판은 오래된 로그가 없다는 사실만으로 삭제를 단정하는 경우입니다. 가장 이른 로그 시각이 기기 사용 기간보다 훨씬 늦거나 특정 구간만 비어 있으면 삭제를 의심할 만합니다. 다만 앞쪽이 비어 있는 모양만으로는 삭제와 보존 한계를 가려낼 수 없고, 가운데 한 구간만 비었는데 그 구간에 다른 활동 기록이 이어질 때 의심의 무게가 커집니다.

반대로 `log erase` 를 쓴 흔적이 보이지 않는다고 해서 지우지 않았다고 결론 내릴 수도 없습니다. 셸 기록처럼 실행 흔적이 남을 만한 곳도 사용자가 따로 지울 수 있습니다.

지운 방식에 따라 남는 로그의 종류가 다를 수 있다는 점도 놓치기 쉽습니다. 위 표대로라면 TTL 로그만 비었거나 fault·error 내용만 남은 모양이 나올 수 있어서, "로그가 일부 남아 있으니 지우지 않았다" 는 판단도 섣부릅니다.

## 보고서 문장 예

- "확보한 통합 로그 저장소에서 가장 이른 이벤트 시각은 YYYY-MM-DD HH:MM:SS (UTC)입니다. 같은 기간 KnowledgeC 에는 앱 사용 기록이 이어져 있어, 이 구간의 통합 로그만 남아 있지 않습니다."
- "명령 기록과 파일 시스템 이벤트에서 로그를 지운 행위를 직접 가리키는 기록은 찾지 못했습니다. 이 결과만으로 로그를 지우지 않았다고 판단할 수는 없습니다."

## 함께 볼 페이지

- [증거를 없애려 했나 (Anti-Forensics)](index.md) — 이 허브의 다른 수단과 전체 흐름
- [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events/index.md) — 공백 앞뒤에서 확인할 이벤트
- [초기화·재설치 (Erase·Reinstall)](erase-reinstall.md) — 로그만이 아니라 맥 전체를 지운 경우
- [삭제 도구 (Wiping Tools)](wiping-tools.md) — 지운 로그 파일 자리를 덮어썼는지 볼 때
- [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](../usage-time.md) — 공백 구간에 맥이 켜져 있었는지 추정할 때

## 참고 문헌

1. SS64 — macOS `log` 명령 — https://ss64.com/mac/log.html
