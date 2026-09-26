---
title: "시간대 설정"
parent: "아티팩트 · 시스템·계정"
nav_order: 630
---

# 시간대 설정 (Time Zone)

## 한 줄 요약

SYSTEM 하이브의 `TimeZoneInformation` 키에는 이 PC 에 설정된 시간대와 UTC 와의 차이가 있습니다. 차이는 분 단위이고, 부호 있는 정수로 읽어야 합니다. UTC 로 적힌 기록을 현지 시각으로 바꿀 때 이 값을 씁니다.

## 무엇을 기록하나 · 왜 생기나

윈도는 시계를 현지 시각으로 보여 주려고 시간대 설정을 SYSTEM 하이브에 둡니다. 레지스트리의 FILETIME 시각처럼 UTC 로 적힌 기록이 많습니다. 반면 보고서와 진술은 현지 시각으로 말할 때가 많습니다. 이 키는 두 시각을 잇는 값을 줍니다.

분석 PC 와 분석 대상 PC 의 시간대가 다를 수 있습니다. 그래서 도구가 보여 주는 현지 시각이 어느 시간대 기준인지 늘 확인합니다. 분석 대상 PC 의 시간대는 이 키에서 읽습니다.

## 위치와 버전별 차이

| 하이브 | 하이브 안의 키 경로 | 공개 도구가 읽는 값 |
|---|---|---|
| SYSTEM | `ControlSet00x\Control\TimeZoneInformation` | Bias, ActiveTimeBias, StandardName, DaylightName, TimeZoneKeyName |

- `ControlSet00x` 의 번호를 고르는 법은 [시스템 기본 정보](os-version-computer-name-install-date-shutdown-t.md)에서 다룹니다.
- 하이브 파일 위치는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.
- 이 페이지가 기댄 공개 도구 소스는 Windows 버전별 차이를 적지 않습니다. 값이 빠져 있으면 하이브에서 직접 확인합니다.

## 구조

| 값 이름 | 읽는 법 | 뜻 |
|---|---|---|
| Bias | REG_DWORD. 부호 있는 32비트 정수로 읽습니다. 단위는 분 | 표준시 기준 UTC 와의 차이 |
| ActiveTimeBias | 부호 있는 정수. 단위는 분 | 지금 실제로 적용 중인 차이. 표준시일 수도, 일광 절약 시간일 수도 있습니다 |
| StandardName | 글자 | 표준시의 표시용 이름 |
| DaylightName | 글자 | 일광 절약 시간의 표시용 이름 |
| TimeZoneKeyName | 글자 | 시간대 키 이름. 예: "Korea Standard Time" |

### 차이 값의 방향

두 차이 값은 다음 관계를 따릅니다.

- UTC = 현지 시각 + Bias(분)
- 현지 시각 = UTC − Bias(분)

그래서 UTC 보다 빠른 시간대는 Bias 가 음수입니다. UTC+9 인 한국은 Bias 가 −540 입니다. +540 이 아닙니다.

### 부호

Bias 는 REG_DWORD 로 저장하지만 부호 있는 32비트로 읽어야 합니다. −540 을 부호 없이 읽으면 4,294,966,756 이 됩니다(현장 관찰로 확인).

압수 이미지의 하이브에서 REG_DWORD 값을 글자로 받아 오는 도구는 부호 없는 10진으로 보여 주는 경우가 많습니다(현장 관찰로 확인). 부호에 뜻이 있는 Bias 같은 값은 원시 바이트로 확인합니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 하이브를 마지막으로 쓴 때 설정돼 있던 시간대 | 조사 대상 날짜의 시간대. 그사이 설정을 바꿨을 수 있습니다 |
| 그때 적용 중이던 차이 (ActiveTimeBias) | 과거의 어느 날짜에 일광 절약 시간이 적용됐는지 |
| 표준시 기준 차이 (Bias) | PC 시계가 맞았는지. 시간대와 시계의 정확도는 별개입니다 |
| | 사용자가 실제로 머문 지역 |

### 보고서 문장

아래 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "SYSTEM 하이브의 시간대 키 이름은 Korea Standard Time 이고, Bias 는 −540분입니다. 이 보고서의 현지 시각은 UTC+9 로 바꾼 값입니다."
- 쓰면 안 되는 문장: "사용자는 사건 당시 한국에 있었습니다."

## 시각 해석

이 키의 값은 시각이 아니라 시각을 바꾸는 데 쓰는 차이입니다. 현지 시각으로 바꾸는 순서는 다음과 같습니다.

1. 바꿀 기록이 UTC 로 적힌 것인지 확인합니다. 레지스트리의 FILETIME 값은 UTC 로 해석합니다([시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)).
2. 이 키에서 TimeZoneKeyName 과 Bias 를 읽습니다. 둘이 서로 맞는지 봅니다.
3. 바꿀 날짜에 일광 절약 시간이 적용되는지 정합니다. ActiveTimeBias 는 한 시점의 값이라, 날짜마다 다를 수 있습니다. 그 시간대의 규칙은 TimeZoneKeyName 으로 따로 확인합니다.
4. 현지 시각 = UTC − 적용할 차이(분) 로 계산합니다.
5. 보고서에는 UTC 와 현지 시각을 함께 적습니다. 어느 차이를 썼는지도 적습니다.

- 이미지에서 읽은 ActiveTimeBias 는 이 PC 가 마지막으로 이 값을 쓴 때의 상태이며, 수집한 날이나 사건 날짜의 상태가 아닐 수 있습니다.
- 키의 마지막 기록 시각(LastWrite)은 레지스트리 키마다 있는 값입니다([레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)). 무엇이 이 키의 LastWrite 를 바꾸는지는 이 페이지가 기댄 자료에 없습니다. 참고로만 봅니다.
- 여러 기록을 하나의 시간 축에 놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md)에서 다룹니다.

## 함정과 한계

1. **Bias 를 부호 없이 읽습니다.** −540 이 4,294,966,756 으로 나옵니다. 이 값을 분으로 계산하면 수천 년의 차이가 됩니다.
2. **부호의 방향을 거꾸로 씁니다.** Bias 는 현지 시각에 더하면 UTC 가 되는 값입니다. UTC 에 Bias 를 더하면 차이가 두 배로 벌어집니다.
3. **Bias 와 ActiveTimeBias 를 섞어 씁니다.** 일광 절약 시간을 쓰는 시간대에서는 두 값이 다를 수 있습니다. 어느 날짜의 시각을 바꾸는지에 따라 골라 씁니다.
4. **지금 설정을 모든 날짜에 씁니다.** 이 키는 마지막 상태만 보여 줍니다. 시간대를 바꾼 적이 있으면 그 전 기록은 다른 차이로 바꿔야 합니다.
5. **도구가 분석 PC 의 시간대로 바꿔 보여 줍니다.** 도구의 시간대 설정을 먼저 확인합니다. 가능하면 UTC 로 보게 설정합니다.
6. **도구가 Bias 를 부호 없는 10진으로 보여 줍니다.** 원시 바이트를 보고 다시 계산합니다.

### 지우기와 조작

- **시간대를 바꿉니다.** 현지 시각으로 보이는 값만 달라집니다. UTC 로 적힌 기록의 값은 그대로입니다. 현지 시각으로 적는 기록이 있다면 영향을 받습니다.
- **시스템 시각을 바꿉니다.** 시간대 변경과 다른 일입니다. 흔적은 [시간 변경](../event-logs/4616-kernel-general.md)에서 찾습니다.
- **옛 설정을 찾습니다.** [섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 속 SYSTEM 하이브에서 그 시점의 값을 읽을 수 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 값 형식을 보고 만든 예시입니다. 실제 데이터에서 뽑은 값이 아닙니다.

```
Bias             E4 FD FF FF
ActiveTimeBias   E4 FD FF FF
TimeZoneKeyName  "Korea Standard Time"
```

1. Bias 의 `E4 FD FF FF` 를 리틀 엔디언으로 읽으면 0xFFFFFDE4 입니다.
2. 부호 없이 읽으면 4,294,966,756 입니다.
3. 맨 윗자리 비트가 1 이라 음수입니다. 2의 32제곱(4,294,967,296)을 빼면 −540 입니다.
4. −540분은 −9시간입니다. 현지 시각 = UTC − (−540분) = UTC + 9시간 입니다.
5. TimeZoneKeyName 이 "Korea Standard Time" 이라 UTC+9 와 맞습니다.
6. ActiveTimeBias 도 같은 바이트입니다. 이 값을 쓴 때 적용 중이던 차이도 −540분입니다.
7. 이 차이로 2025-03-14 09:05:12 UTC 를 바꾸면 현지 시각은 2025-03-14 18:05:12 입니다.

> 그림 자리: `E4 FD FF FF` 를 부호 없이 읽은 값(4,294,966,756)과 부호 있게 읽은 값(−540)을 나란히 두고, UTC·현지 시각의 관계를 수직선으로 보여 주는 그림

### 공개 도구로 한 번

RegRipper 의 `timezone` 플러그인이 이 키의 값을 읽습니다. 레지스트리 뷰어로 값을 직접 봐도 됩니다. 도구를 쓸 때는 다음을 확인합니다.

- Bias 와 ActiveTimeBias 를 음수로 보여 주는지 확인합니다.
- 도구가 어느 ControlSet 을 읽었는지 확인합니다.
- 헥스로 계산한 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [시스템 기본 정보](os-version-computer-name-install-date-shutdown-t.md) | 설치·종료 시각을 현지 시각으로 바꿔 사용 시간과 맞는지 |
| [시간 변경](../event-logs/4616-kernel-general.md) | 시스템 시각을 바꾼 기록. 시간대만으로 설명되지 않는 시각 차이가 있는지 |
| [켜짐·꺼짐](../event-logs/power-on-off-events.md) | 이벤트 로그의 시각을 같은 차이로 바꿨을 때 다른 기록과 맞는지 |
| [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 예전 시점의 시간대 설정 |

시각을 맞춘 뒤 PC 사용 시간을 재구성하는 흐름은 [PC 사용 시간 재구성](../../04-scenarios/activity/system-usage-time.md)에서 다룹니다.

## 실습

**NIST CFReDS 같은 공개 시험 이미지**에서 SYSTEM 하이브를 꺼내 풀어 봅니다.

1. `TimeZoneInformation` 키의 TimeZoneKeyName 은 무엇입니까?
2. Bias 를 헥스로 읽어 부호 있는 값으로 바꿔 보십시오. 사용하는 도구는 이 값을 어떻게 보여 줍니까?
3. Bias 와 ActiveTimeBias 는 같습니까? 다르다면 이유를 적어 보십시오.
4. 이 이미지의 ShutdownTime 을 현지 시각으로 바꿔 보십시오. 그 날짜에 일광 절약 시간이 적용되는지도 확인하십시오.

**직접 만든 가상 머신**에서도 해 봅니다.

1. 시간대를 서울로 두고 Bias 를 헥스로 읽습니다.
2. 일광 절약 시간을 쓰는 시간대로 바꾸고 다시 읽습니다.
3. 두 경우의 Bias·ActiveTimeBias 를 비교합니다.
4. 같은 파일의 NTFS 시각을 도구로 볼 때, 표시 시각이 시간대 설정에 따라 바뀌는지 확인합니다.

## 참고 문헌

- keydet89, RegRipper3.0 `timezone.pl` (TimeZoneInformation, Bias, ActiveTimeBias) — https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/timezone.pl
