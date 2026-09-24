---
title: "전원·배터리 사용"
parent: "SRUM"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 1020
---

# 전원·배터리 사용 (Energy Usage)

> 상위 허브: [SRUM (System Resource Usage Monitor)](index.md)

## 한 줄 요약

SRUM 의 에너지 사용 표에는 노트북이 전원에 꽂혀 있었는지, 켜져 있었는지 대기 중이었는지, 배터리가 얼마나 남았는지가 시각과 함께 남습니다. 앱별 기록이 아니라 기기 전체의 기록입니다. 기본 표는 상태가 바뀔 때마다 행을 쓰고, 장기 표는 한 주 단위로 합계를 씁니다.

## 무엇을 기록하나 · 왜 생기나

에너지 사용 공급자 (Energy Usage Provider)는 SRUM 확장 가운데 하나이고, 파일은 `%SystemRoot%\System32\energyprov.dll` 입니다. 확장 목록은 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SRUM\Extensions` 아래에 있으며, 이 공급자의 GUID 가 그대로 표 이름이 됩니다.

| 표 이름 | 이 글에서 부르는 이름 | 남는 것 |
|---|---|---|
| `{FEE4E14F-02A9-4550-B5CE-5FA2DA202E37}` | 기본 표 | 전원·대기 상태가 바뀐 순간과 그때의 배터리 잔량 |
| `{FEE4E14F-02A9-4550-B5CE-5FA2DA202E37}LT` | 장기 표 (Long Term) | 한 주 동안 전원 연결·배터리·대기로 보낸 시간과 쓴 에너지 |

배터리 열의 이름(DesignedCapacity·FullChargedCapacity·CycleCount)은 배터리 드라이버가 돌려주는 `BATTERY_INFORMATION` 구조의 멤버 이름과 같습니다. Microsoft 문서는 이 구조의 용량 단위를 mWh 로 적습니다. 배터리가 상대 단위(BATTERY_CAPACITY_RELATIVE)로 보고하면 단위가 없습니다.

이름이 비슷한 에너지 추정 공급자 (Energy Estimation Provider, `eeprov.dll`)도 있습니다. 이 공급자는 앱별 에너지 추정값을 `{DA73FB89-2BEA-4DDC-86B8-6E048C6DA477}` 표의 이진 열(BinaryData)에 넣는데, 이 이진 값의 구조는 공개 명세에 없습니다. 이 페이지는 에너지 사용 공급자의 두 표만 다룹니다.

## 위치와 버전별 차이

파일은 `C:\Windows\System32\sru\SRUDB.dat` 이고, 형식은 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md)입니다. SRUM 공통 구조와 ID 풀이는 [구조와 ID 매핑](srudbidmaptable.md)을 봅니다.

| Windows | 두 표 | 근거 |
|---|---|---|
| 8·8.1 | 확인하지 못했습니다 | 공개 명세의 Windows 8 부분이 비어 있습니다 |
| 10 | 있습니다. 열은 아래 구조 표와 같습니다 | libyal 명세 |
| 11 25H2 (빌드 26200) | 있습니다. 두 표 모두 끝에 `BatteryCount`·`BatteryChargeLimited` 열이 더 있습니다 | 관찰 |
| Server 2019 | 새로 설치한 한 대에서 두 표가 없었습니다 | Harrison 의 시험 |

이 글의 "관찰" 은 모던 대기 (Modern Standby)를 쓰는 Windows 11 25H2 노트북 한 대에서 얻었습니다. 실행 중인 시스템에서 VSS 로 SRUDB.dat 사본을 만들어 읽었습니다. 아래에서는 이 범위를 "(확인 범위: 관찰한 노트북)" 으로 줄여 씁니다. 배터리가 없는 데스크톱에서 두 표에 무엇이 남는지는 확인하지 못했습니다.

## 구조

### 기본 표

열 이름과 형식은 libyal 명세를 따랐습니다.

| 열 | 형식 | 뜻 |
|---|---|---|
| AutoIncId | 32비트 정수 | 행 번호. 행을 넣을 때마다 커집니다 |
| TimeStamp | OLE 자동화 날짜 (8바이트 실수) | SRUM 이 행을 DB 에 쓴 시각 |
| AppId·UserId | 32비트 정수 | SruDbIdMapTable 의 번호 |
| EventTimestamp | 64비트 정수 (FILETIME) | 상태가 바뀐 시각 |
| StateTransition | 32비트 정수 | 이전 상태와 지금 상태 (아래 "상태 전환 값 읽기") |
| DesignedCapacity | 32비트 정수 | 배터리 설계 용량 (mWh) |
| FullChargedCapacity | 32비트 정수 | 지금 가득 충전했을 때의 용량 (mWh) |
| ChargeLevel | 32비트 정수 | 그 순간 남은 용량 (mWh) |
| CycleCount | 32비트 정수 | 충방전 횟수. 배터리가 세지 않으면 0 |
| ConfigurationHash | 64비트 정수 | 뜻이 공개 문서에 없습니다 |
| BatteryCount·BatteryChargeLimited | 32비트 정수 | Windows 11 에서 보인 열. 관찰한 노트북에서는 1 과 0 이었습니다 |

libyal 명세는 EventTimestamp 를 64비트 정수로만 적습니다. 공개 도구들은 이 값을 FILETIME 으로 읽습니다. 관찰한 노트북에서도 FILETIME 으로 푼 값이 같은 순간의 이벤트 로그 시각과 1초 안팎으로 맞았습니다.

ChargeLevel 의 단위도 명세에 없습니다. 관찰한 노트북에서는 ChargeLevel 이 FullChargedCapacity 를 넘은 적이 없었습니다. 전원 공급이 바뀐 순간의 이벤트 로그 70건과 견주면 완충 용량은 68건이 같았습니다. 남은 용량은 49건이 같았고, 나머지도 수백 mWh 안에서 가까웠습니다. 그래서 ChargeLevel 도 mWh 로 봅니다. (확인 범위: 관찰한 노트북)

관찰한 노트북에서는 모든 행의 AppId 가 한 값, UserId 도 한 값이었습니다. 이 표의 행은 앱별·사용자별 기록으로 읽지 않습니다.

### 장기 표

AutoIncId·TimeStamp·AppId·UserId 와 배터리 열(DesignedCapacity·FullChargedCapacity·CycleCount·ConfigurationHash)은 기본 표와 같습니다. 나머지 열은 모두 32비트 정수입니다.

| 열 | 뜻 |
|---|---|
| ActiveAcTime | 전원에 꽂힌 채 켜져 있던 시간 |
| CsAcTime | 전원에 꽂힌 채 대기하던 시간 |
| ActiveDcTime | 배터리로 켜져 있던 시간 |
| CsDcTime | 배터리로 대기하던 시간 |
| ActiveDischargeTime·CsDischargeTime | 관찰한 12행 모두에서 각각 ActiveDcTime·CsDcTime 과 같았습니다 |
| ActiveEnergy·CsEnergy | 쓴 에너지로 보입니다. 단위를 확인하지 못했습니다 |

열 이름의 Cs 는 연결 대기 (Connected Standby)를 줄인 것으로 보입니다. 공개 문서에 풀이는 없습니다.

관찰한 노트북에서 장기 표 행은 약 7일 간격이었습니다. 네 시간 열을 더하면 행 간격을 초로 센 값과 거의 같았습니다. 그래서 시간 열의 단위를 초로 봅니다. 두 주 간격으로 떨어진 한 행은 합이 간격보다 컸습니다. ActiveEnergy 를 mWh 로 보고 ActiveDcTime 으로 나누면 평균 10~24 W 가 나왔습니다. 같은 계산을 CsEnergy 에 하면 0.3~63 W 로 크게 흩어졌습니다. 그래서 두 에너지 열의 단위는 정하지 않습니다. (확인 범위: 관찰한 노트북)

### 상태 전환 값 읽기

StateTransition 의 뜻은 공개 명세에 없습니다. 아래 해석은 관찰한 노트북에서 이벤트 로그와 맞춰 얻은 것입니다. 결론 문장에 쓰기 전에 같은 검체의 이벤트 로그로 다시 확인합니다.

값은 두 바이트로 읽습니다. 낮은 바이트(파일에서 첫 바이트)가 이전 상태이고, 둘째 바이트가 지금 상태입니다.

| 상태 번호 | 뜻 (관찰) |
|---|---|
| 1 | 전원 연결, 켜짐 |
| 2 | 배터리, 켜짐 |
| 3 | 전원 연결, 대기 |
| 4 | 배터리, 대기 |
| 0 | 뜻을 가려내지 못했습니다 |

예를 들어 `0x0201` 은 1 에서 2 로 바뀐 것입니다. 켜진 채로 전원이 빠진 순간입니다. `0x0301` 은 전원에 꽂힌 채 대기로 들어간 순간이고, `0x0103` 은 거기서 깨어난 순간입니다.

`0x0101`·`0x0303` 처럼 두 바이트가 같은 값은 상태가 그대로라는 뜻입니다. 이런 행은 정해진 때마다 적는 기록으로 보입니다. 관찰한 노트북에서 이런 행의 절반쯤은 EventTimestamp 가 TimeStamp 와 같았습니다. 나머지는 대부분 앞선 쓰기의 5~6분 뒤 시각이었습니다.

근거는 두 가지입니다. (확인 범위: 관찰한 노트북)

- 시스템 로그의 Kernel-Power 이벤트 105("Power source change")에는 AcOnline 값이 있습니다. 기본 표 기간 안의 105 이벤트 73건 가운데 66건이 해석과 맞는 행(`0x0201`·`0x0102`·`0x0403`·`0x0304`)과 짝을 이뤘습니다. 시각 차이의 가운데값은 약 1초였습니다.
- Kernel-Power 이벤트 506("entering Modern Standby")·507("exiting Modern Standby") 401건 가운데 342건이 `0x0301`·`0x0402`(대기로 들어감)나 `0x0103`·`0x0204`(깨어남) 행과 짝을 이뤘습니다. 시각 차이의 가운데값은 약 0.2초였습니다.

S3 절전을 쓰는 노트북에서 이 값이 어떻게 나오는지는 확인하지 못했습니다.

> 그림 자리: 하루 동안의 기본 표 행을 시간축에 놓고, 상태 1~4 구간을 색으로 칠하고 ChargeLevel 을 선으로 겹친 그림

## 시각 해석

| 열 | 형식 | 기준 | 바뀌는 때 |
|---|---|---|---|
| EventTimestamp | FILETIME | UTC | 전원·대기 상태가 바뀐 순간 |
| TimeStamp | OLE 자동화 날짜 | UTC | SRUM 이 모아 둔 행을 DB 에 쓴 순간 |

두 형식의 계산은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다.

사건 시각은 EventTimestamp 로 씁니다. TimeStamp 는 "이때 DB 에 들어갔다" 는 뜻입니다. SRUM 이 약 1시간마다 DB 에 쓰는 규칙은 [SRUM 해석 함정](1.md)을 봅니다.

관찰한 노트북의 기본 표에는 행 3,210개에 TimeStamp 값이 1,415가지뿐이었습니다. 여러 행이 한 TimeStamp 를 나눠 씁니다. 두 시각의 차이는 가운데값이 약 27분이었고, 15시간 넘게 벌어진 행도 있었습니다. 두 값이 1초 안에서 같은 행은 1,351개였습니다. 형식이 다른 두 값이 이만큼 겹치므로 TimeStamp 도 UTC 로 봅니다. (확인 범위: 관찰한 노트북)

시계 조작을 볼 때는 AutoIncId 순서와 EventTimestamp 순서를 견줍니다. 관찰한 노트북에서는 AutoIncId 순으로 놓은 이웃 행 3,209쌍 가운데 EventTimestamp 가 거꾸로 간 곳이 없었습니다. 거꾸로 가는 곳이 있으면 [시간 변경](../../event-logs/4616-kernel-general.md) 이벤트를 확인합니다. 현지 시각으로 바꾸는 방법은 [시간대·시계 오차 보정](../../../03-techniques/analysis/timeline/time-normalization.md)을 봅니다.

## 증거로서 의미

### 증명하는 것

- EventTimestamp 시각에 기기가 켜져 있거나 대기 중이었습니다.
- 그 시각에 전원 연결과 배터리 사이, 켜짐과 대기 사이의 전환이 있었습니다 (관찰한 해석 기준).
- 그 순간 배터리에 남은 용량과, 기간에 걸친 완충 용량의 변화를 알 수 있습니다.
- 한 주 동안 전원 연결·배터리·대기로 보낸 시간의 합계를 알 수 있습니다.

### 증명하지 못하는 것

- 누가 썼는지. UserId 는 한 값이고 사람을 가리키지 않습니다.
- 어떤 앱을 썼는지.
- 사람이 기기 앞에 있었는지. "켜짐" 은 대기 상태가 아니었다는 뜻일 뿐입니다.
- 기기가 어디에 있었는지. 배터리 상태는 외부 전원이 끊겼다는 뜻일 뿐입니다. 케이블을 뽑았는지, 정전인지, 어댑터가 고장 났는지는 가리지 못합니다.
- 기록이 빈 기간에 기기가 꺼져 있었다는 것. 꺼짐, 최대 절전, 쓰기 전 멈춤, DB 손상이 모두 같은 공백을 만듭니다.

보고서 문장은 기록이 말하는 만큼만 씁니다. 아래 값은 헥스 예시의 값입니다.

> 이 노트북의 SRUM 에너지 사용 기록에는 2024-03-15 08:23:41 UTC 에 전원 연결 상태에서 배터리 상태로 바뀐 것으로 해석되는 행이 있습니다. 그때 남은 용량은 41,250 mWh, 완충 용량은 50,000 mWh 로 적혀 있습니다.

## 함정과 한계

- **상태 해석은 관찰입니다.** 검체마다 이벤트 로그와 맞춰 봅니다.
- **TimeStamp 는 사건 시각이 아닙니다.** 사건보다 수십 분에서 수 시간 늦을 수 있습니다.
- **두 표를 합치는 도구가 있습니다.** SrumECmd 소스는 장기 표와 기본 표를 한 목록으로 합칩니다. 번호가 겹치면 기본 표 행의 번호를 바꿉니다. 결과의 번호를 원래 AutoIncId 로 믿지 말고 어느 표의 행인지 확인합니다.
- **새 열을 빠뜨리는 도구가 있습니다.** BatteryCount·BatteryChargeLimited 는 libyal 명세와 SrumECmd 소스(2026년 9월 master)에 없습니다. 열 이름을 정해 두고 읽는 도구는 새 열을 내놓지 않습니다.
- **빈 번호를 삭제로 단정하지 않습니다.** 관찰한 노트북의 기본 표는 AutoIncId 가 1,408 부터 시작했고, 그 뒤로도 빈 번호가 220군데 있었습니다. 장기 표는 홀수 번호만 있었습니다. (확인 범위: 관찰한 노트북)
- **보관 기간이 짧습니다.** 관찰한 노트북에서는 기본 표에 약 60일, 장기 표에 약 13주 치가 남아 있었습니다. 보관 기간은 공식 문서에 없습니다. WithSecure 발표 자료는 기본 설정으로 계산하면 기본 표가 60일, 장기 표가 1,820일(7일 × 260)이라고 적습니다. 관찰한 노트북의 장기 표가 13주 치뿐이었던 까닭은 확인하지 못했습니다. 오래된 사건은 장기 표의 주간 합계로만 남을 수 있습니다.
- **압수 이미지의 SRUDB.dat 는 대부분 비정상 종료 상태입니다.** 이미지 안의 로그가 끊겨 복구가 안 되는 경우가 있습니다. 손상 DB 는 도구마다 행 수가 달라서, 같은 표에서 1,612행과 1,742행이 나온 사례가 있습니다. 사본에서 작업하고 두 가지 이상 방식으로 열어 비교합니다. (확인 범위: 현장 관찰) [트랜잭션 로그와 비정상 종료 상태](../../../01-foundations/database-log-formats/extensible-storage-engine/edb-log-dirty-shutdown.md)와 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 명세의 형식에 맞춰 만든 예시이며, 실제 검체의 값이 아닙니다. 열 값만 하나씩 떼어 보였습니다. 이 값들이 레코드 안 어디에 놓이는지는 [파일 구조 (Page·B+Tree·Catalog)](../../../01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md)를 봅니다.

| 열 | 바이트 (리틀 엔디언) | 값 | 풀이 |
|---|---|---|---|
| TimeStamp | `00 00 00 00 CC 26 E6 40` | 실수 45366.375 | 1899-12-30 에서 45,366일 뒤는 2024-03-15 이고, 0.375일은 9시간입니다. 2024-03-15 09:00:00 UTC |
| EventTimestamp | `80 E4 39 16 B2 76 DA 01` | 0x01DA76B21639E480 | 1601-01-01 부터 센 100ns 단위 값입니다. 2024-03-15 08:23:41 UTC |
| StateTransition | `01 02 00 00` | 0x00000201 | 첫 바이트 1(이전: 전원 연결, 켜짐), 둘째 바이트 2(지금: 배터리, 켜짐) |
| ChargeLevel | `22 A1 00 00` | 41,250 | 남은 용량 41,250 mWh |
| FullChargedCapacity | `50 C3 00 00` | 50,000 | 완충 용량 50,000 mWh |
| DesignedCapacity | `20 CB 00 00` | 52,000 | 설계 용량 52,000 mWh |

잔량 비율은 41,250 ÷ 50,000 = 82.5 % 입니다. 설계 대비 완충 용량은 50,000 ÷ 52,000 ≈ 96.2 % 입니다. 이 행의 TimeStamp 는 EventTimestamp 보다 약 36분 늦습니다. 사건 시각은 08:23:41 이고, 09:00 은 DB 에 쓴 시각입니다.

### 공개 도구로 한 번

- libyal libesedb 의 `esedbexport` 로 두 표를 내보내면 원시 열 값을 볼 수 있습니다.
- SrumECmd 는 두 표를 합쳐 CSV 로 내고 EventTimestamp 를 UTC 시각으로 바꿉니다. 위 함정의 번호 바꿈과 새 열 누락을 염두에 둡니다.
- 파이썬 ESE 라이브러리(예: dissect.esedb)로 직접 읽으면 늘어난 열까지 볼 수 있습니다. 이 글의 관찰은 이 방식으로 얻었습니다.

실행 중인 시스템에서는 Windows 의 `powercfg /batteryreport` 가 배터리 사용 보고서를 만듭니다. `powercfg /srumutil` 은 SRUM 의 에너지 추정 자료를 CSV·XML 로 내보냅니다. Microsoft 블로그는 이 결과가 앱별 에너지 추정값이라고 설명합니다. 두 명령은 대상 시스템에 파일을 만듭니다. 쓴다면 [라이브 응답](../../../03-techniques/process-acquisition/live-response/index.md) 기록에 남깁니다.

## 교차 검증

| 함께 볼 것 | 맞춰 볼 내용 |
|---|---|
| [켜짐·꺼짐](../../event-logs/power-on-off-events.md) 이벤트 | Kernel-Power 105·506·507 과 전환 행의 시각이 맞는지, 기록이 빈 기간이 실제로 꺼진 때인지 |
| [앱별 자원 사용](application-resource-usage.md) | 켜짐 구간에 어떤 앱이 돌았는지 |
| [네트워크 연결 기록](network-connectivity.md) | 같은 시간대에 어느 네트워크에 붙어 있었는지 |
| [로그온·로그오프](../../event-logs/logon-events/index.md), [화면 잠금·해제](../../event-logs/logon-events/4800-4801.md) | 켜짐 구간에 누가 로그온해 있었는지 |
| [시간 변경](../../event-logs/4616-kernel-general.md) | EventTimestamp 가 거꾸로 간 곳이 시계 조작인지 |

조사 흐름은 [PC 사용 시간 재구성](../../../04-scenarios/activity/system-usage-time.md)과 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md)를 봅니다.

## 실습

공개 검체(NIST CFReDS 등)에서 노트북 이미지를 골라 풉니다. 데스크톱·가상 머신 이미지에는 두 표가 없거나 비어 있을 수 있습니다. 자기 노트북의 SRUDB.dat 사본으로도 해 볼 수 있습니다.

1. 두 표가 있습니까? 각 표의 행 수와 기간은 얼마입니까?
2. StateTransition 값을 세어 보십시오. 가장 많은 값은 무엇입니까?
3. `0x0201` 행의 시각을 시스템 로그의 Kernel-Power 105 이벤트와 맞춰 보십시오. 몇 초 차이입니까?
4. FullChargedCapacity 는 기간 동안 얼마나 줄었습니까? DesignedCapacity 대비 몇 % 입니까?
5. 도구 두 개로 같은 표를 열어 행 수와 열 목록이 같은지 비교하십시오.

## 참고 문헌

1. Joachim Metz, "System Resource Usage Monitor (SRUM) database", libyal esedb-kb. https://github.com/libyal/esedb-kb/blob/main/documentation/System%20Resource%20Usage%20Monitor%20(SRUM).asciidoc
2. Microsoft Learn, "Powercfg command-line options". https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options
3. Microsoft Learn, "BATTERY_INFORMATION structure (Poclass.h)". https://learn.microsoft.com/en-us/windows/win32/power/battery-information-str
4. Scott Chamberlin, "Measuring Your Application Power and Carbon Impact (Part 1)", Microsoft Sustainable Software 블로그, 2020-09-14. https://devblogs.microsoft.com/sustainable-software/measuring-your-application-power-and-carbon-impact-part-1/
5. Adam Harrison, "Testing of SRUM on Windows Server 2019 (continued)", 2019-01-11. https://blog.1234n6.com/testing-of-srum-on-windows-server-2019-continued/
6. Eric Zimmerman, SrumECmd 소스 `SrumData/Srum.cs`. https://github.com/EricZimmerman/Srum/blob/master/SrumData/Srum.cs
7. Catarina de Faria Cristas·Lucas Echard·Diego Fuschini (WithSecure), "Exploring the depths of SRUM for incident response", SANS DFIR Summit Europe 2023 발표 자료. https://github.com/ReversecLabs/slide-decks/blob/main/2023-SANS_DFIR_Summit_Europe/Exploring_the_depths_of_SRUM_for_incident_response.pdf
