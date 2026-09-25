---
title: "프로토콜 버퍼"
parent: "기반 · 데이터 저장 형식"
nav_order: 220
---

# 프로토콜 버퍼 (Protocol Buffers)

## 한 줄 요약

프로토콜 버퍼 (Protocol Buffers) 는 필드 번호와 형식 표시를 앞세운 레코드를 이어 붙인 바이너리 형식이고, 필드 이름이 파일에 없어서 메시지 정의 없이 풀면 번호와 형식만 보입니다.

## 이 형식을 쓰는 아티팩트

| 아티팩트 | 위치·파일 이름 | 비고 |
|---|---|---|
| Preferences DataStore | 앱 데이터의 `files/datastore/` 아래 `*.preferences_pb` | Google 이 SharedPreferences 대신 쓰라고 권하는 저장 방식 |
| Proto DataStore | 앱 데이터의 `files/datastore/` 아래, 이름은 개발자가 정함(예: `settings.pb`) | 메시지 정의(.proto)는 앱 소스의 `app/src/main/proto/` 에 둠 |
| 앱 사용 기록 (usagestats) | [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md) 참고 | 저장 버전에 따라 형식이 다름 |

Jetpack DataStore 는 SharedPreferences 를 대신하도록 만든 저장 방식이고, 옛 방식은 [설정 XML과 SharedPreferences](shared-preferences.md) 에서 다룹니다. Proto DataStore 는 메시지 정의를 앱 소스에 두고 빌드하기 때문에, 기기에는 .proto 파일이 남지 않는다고 보고 분석을 준비합니다. 이 판단은 개발 문서의 설명에서 끌어낸 해석입니다.

DataStore 파일은 기본으로 Android 자동 백업과 기기 간 전송 (device-to-device transfer, D2D) 에 들어가고, 앱이 백업 규칙(`data_extraction_rules.xml`)으로 뺄 수도 있습니다. 그래서 기기에서 지워진 설정이 백업이나 새 기기 쪽에 남아 있을 수 있고, 백업 쪽은 [구글 백업](../../02-artifacts/mail-cloud/google-backup.md) 에서 다룹니다.

그 밖에 어떤 시스템 파일이 프로토콜 버퍼로 저장되는지는 이 페이지의 출처로 목록을 확인하지 않았고, 각 아티팩트 페이지에서 다룹니다.

## 구조

### 태그와 wire type

메시지는 태그, (필요하면) 길이, 값으로 이루어진 레코드가 차례로 이어진 것이고, 파일 앞에 형식을 알리는 표시가 따로 없습니다. 태그는 `(field_number << 3) | wire_type` 이라서 아래 3비트가 값의 전송 형식 (wire type) 이고 나머지가 필드 번호입니다.

| wire type | 이름 | 쓰는 형식 |
|---|---|---|
| 0 | VARINT | int32, int64, uint32, uint64, sint32, sint64, bool, enum |
| 1 | I64 | fixed64, sfixed64, double |
| 2 | LEN | string, bytes, 내장 메시지, packed repeated |
| 3 | SGROUP | 그룹 시작 (폐기됨) |
| 4 | EGROUP | 그룹 끝 (폐기됨) |
| 5 | I32 | fixed32, sfixed32, float |

### varint

가변 길이 정수 (varint) 는 바이트마다 최상위 비트가 "다음 바이트가 더 있다" 는 표시이고, 아래 7비트가 값입니다. 7비트 묶음은 리틀 엔디언 순서로 붙습니다. 음수 int32·int64 는 2의 보수로 적기 때문에 늘 10바이트를 쓰고, sint32·sint64 는 지그재그 (ZigZag) 방식으로 양수 n 을 2n 으로, 음수 n 을 2|n|−1 로 바꿔 적습니다.

### LEN

LEN 은 varint 로 적은 길이 뒤에 그만큼의 내용이 옵니다. string 과 bytes 는 최대 2GB 까지 담습니다.

### 필드 순서와 중복

필드는 어떤 순서로도 나올 수 있고, 반복 필드가 아닌 필드가 두 번 나오면 마지막 값을 쓰고, 내장 메시지 필드라면 두 값을 합칩니다.

### 헥스로 따라가 보기

아래는 명세로 만든 예시이고, 특정 기기에서 꺼낸 바이트가 아닙니다.

```
08 96 01      필드 1, wire type 0(VARINT), 값 150
12 02 68 69   필드 2, wire type 2(LEN), 길이 2, 내용 68 69 ("hi")
```

`08` 은 `(1 << 3) | 0` 이라 필드 1 의 VARINT 입니다. `96` 은 2진수 `1001 0110` 이라 최상위 비트가 1 이어서 다음 바이트가 이어지고, 아래 7비트는 `0x16`(22) 입니다. 다음 `01` 은 최상위 비트가 0 이라 여기서 끝나고, 7비트 묶음을 리틀 엔디언으로 붙이면 22 + 1 × 128 = 150 입니다. `12` 는 `(2 << 3) | 2` 라서 필드 2 의 LEN 이고, 길이 `02` 뒤의 두 바이트가 내용입니다.

같은 VARINT `01` 이 sint32 필드라면 지그재그를 되돌려 −1 로 읽어야 하고, int32 로 읽으면 1 이 됩니다. 어느 쪽인지는 바이트만으로 알 수 없습니다.

## 읽는 법

1. 태그 varint 를 읽어 필드 번호와 wire type 을 나눕니다.
2. wire type 에 따라 값을 읽습니다. VARINT 는 varint 하나, I64 는 8바이트, I32 는 4바이트, LEN 은 길이 varint 뒤의 내용입니다.
3. LEN 내용은 내장 메시지로 한 번 더 풀어 봅니다. 끝까지 깔끔하게 풀리면 내장 메시지일 가능성이 있지만, 문자열이나 bytes 가 우연히 풀리는 경우도 있어 확정하지 않습니다.
4. 메시지 정의가 있으면 필드 번호를 이름과 선언된 형식에 맞춰 봅니다. 정의가 없으면 앱이 화면에 보여 주는 값과 맞춰 가며 필드의 뜻을 추정하고, 이 방법은 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md) 에서 다룹니다.

시각 필드에는 따로 정해진 형식이 없습니다. 같은 VARINT 라도 유닉스 밀리초인지 초인지, 어떤 기준 시각에서 센 상대값인지는 필드 정의를 봐야 알 수 있습니다. 예를 들어 앱 사용 기록은 파일 이름이 기준 시각이고 이벤트 시각은 그 기준에서 센 상대값이며, 자세한 내용은 [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md) 에 있습니다. 단위를 가리는 방법은 [시각 값](../value-decoding/time-values.md) 에서 다룹니다.

## 포렌식에서 중요한 점

인코딩 안에 필드 이름과 선언된 형식이 없기 때문에, 메시지 정의 없이 푼 결과는 "필드 3 은 아마 보낸 시각" 같은 추정을 거친 해석입니다. 보고서에는 필드 번호와 원래 바이트를 함께 적고, 어떤 근거로 뜻을 붙였는지 밝힙니다.

반복 필드가 아닌 필드가 한 메시지 안에 두 번 들어 있으면 파서는 마지막 값만 보여 주지만, 앞의 값도 바이트로는 파일 안에 남아 있습니다. 이런 파일을 만났다면 원시 해독 결과에서 앞의 값까지 살펴봅니다.

메시지는 레코드만 이어져 있어 파일 머리 표시가 없고, 비할당 영역에서 조각을 찾아 되살리기가 어렵습니다. 끝이 잘린 파일도 레코드가 앞에서부터 차례로 이어져 있어 잘린 곳 앞의 레코드까지는 풀 수 있고, 해독이 실패한 위치를 기록해 두면 어디까지 믿을 수 있는지 나눌 수 있습니다. 조각 복구는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

## 함정

LEN 하나가 문자열인지, bytes 인지, 내장 메시지인지는 바이트만으로 가려지지 않을 때가 있습니다. I64 도 fixed64, sfixed64, double 가운데 무엇인지 알 수 없어서, 정수로 읽어 말이 안 되는 값이면 double 로 다시 읽어 봅니다.

음수가 들어갈 수 있는 필드는 int32 로 적었는지 sint32 로 적었는지에 따라 같은 바이트의 뜻이 달라집니다. 10바이트짜리 varint 가 보이면 2의 보수로 적은 음수 int 일 수 있습니다.

Proto DataStore 는 파일 이름을 개발자가 정하기 때문에 `.pb` 같은 확장자만으로 찾으면 놓칠 수 있습니다. `files/datastore/` 폴더 안의 파일은 확장자와 상관없이 모두 봅니다.

## 도구

메시지 정의 없이 필드 번호와 wire type 만 풀어 주는 원시 해독 도구를 쓸 수 있지만, 이 페이지의 출처로는 특정 도구 이름을 확인하지 않았습니다. 도구마다 LEN 을 문자열로 볼지 내장 메시지로 볼지 정하는 방식이 달라서, 중요한 값은 위 헥스 예시처럼 바이트를 직접 따라가 확인합니다. 도구를 확인하는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 참고 문헌

1. Encoding — Protocol Buffers Documentation, https://protobuf.dev/programming-guides/encoding/
2. DataStore — Android Developers, https://developer.android.com/topic/libraries/architecture/datastore
