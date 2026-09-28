---
title: "앱 사용 스트림"
parent: "바이옴"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 720
---

# 앱 사용 스트림 (App.InFocus)

`App.InFocus` 는 앱이 초점을 받거나 잃는 상태 변화를 번들 ID·상태 값·시작 시각과 함께 protobuf 기록으로 남기는 Biome 스트림이고, 앱을 언제 썼는지 볼 때 knowledgeC와 함께 확인하는 자료입니다 [1][3].

## 무엇을 기록하나 · 왜 생기나

이 사건은 앱이 초점을 받는 상태로 바뀌는 순간을 잡고, 번들 ID와 바뀐 이유를 함께 담습니다 [2]. 이 스트림이 knowledgeC 시절의 `_DKEvent.App.InFocus` 와 비슷하다는 해석이 있습니다 [2]. `_DK` 접두어는 Duet Knowledge(CoreDuet Knowledge)를 뜻하고 Apple의 비공개 CoreDuet 프레임워크와 관련됩니다 [2].

스트림 폴더 구조, SEGB 파일 안에서 기록과 상태 값을 찾는 법은 [저장 위치와 스트림 (Streams)](streams.md)에서 다루고, 이 페이지는 기록 안의 데이터와 그 해석을 다룹니다.

## 위치와 버전별 차이

스트림 파일은 아래 두 자리에 있습니다 [1].

```
.../Biome/streams/restricted/App.InFocus/local/*
.../Biome/streams/restricted/App.InFocus/remote/*
```

macOS 사용자 기준으로는 `~/Library/Biome/streams/restricted/App.InFocus/local/` 이 됩니다 [3]. 시스템 쪽(`/private/var/db/biome`)에도 이 스트림이 있는지는 실제 데이터로 확인합니다.

버전별 차이는 iLEAPP 표본 이미지(iOS)에서 아래처럼 나타납니다 [1].

| 대상 | App.InFocus | `_DKEvent.App.InFocus` |
|---|---|---|
| iOS 16.x (iLEAPP 표본 이미지 3개) | 0행 | 행 있음 |
| iOS 17 이후 (iLEAPP 표본) | 행 있음 | 자료 없음 |
| macOS | 실제 데이터로 행 수 확인 | 실제 데이터로 행 수 확인 |

iOS에서 기록은 28일 동안 남고 [2], 다른 스트림과의 비교는 [저장 위치와 스트림 (Streams)](streams.md)에 있습니다.

## 구조

기록 데이터는 protobuf이고, iLEAPP과 mac_apt는 정의 파일 없이 필드 번호로 풀어 저마다 이름을 붙입니다 [1][3]. 두 도구의 해석을 나란히 놓으면 아래와 같습니다.

| 필드 | 형식 | iLEAPP 해석 [1] | mac_apt 해석 [3] |
|---|---|---|---|
| 2 | int | 이름 없이 형식만 지정 | — |
| 3 | int | 상태. 1 = Foreground, 0 = Background | status. 0 = "Out of focus", 1 = "In focus", 그 밖 = Unknown(값) |
| 4 | double | 시작 시각 (Start Time), 맥 절대 시각 | — |
| 6 | str | 번들 ID | `product_name` |
| 9 | str | 이름 없이 형식만 지정 | CFBundleShortVersionString (앱 버전 문자열) |
| 10 | str | 이름 없이 형식만 지정 | CFBundleVersion (앱 버전 문자열) |

— 는 그 도구의 해석이 공개되지 않은 칸입니다. 필드 3의 이름 붙임은 두 도구가 비슷하지만, Foreground·Background라는 이름은 스트림 이름에서 나온 iLEAPP의 해석입니다 [1]. 이 값의 뜻을 밝힌 Apple 공식 자료는 없습니다. 필드 6은 iLEAPP이 번들 ID로, mac_apt가 `product_name` 으로 부르는 같은 필드라서, 두 도구의 결과를 합칠 때 필드 이름이 달라도 같은 값인지 확인합니다. 번들 ID를 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** `local` 폴더에 기록이 있으면, 이 기기의 App.InFocus 스트림에 그 번들 ID와 상태 값이 그 시각으로 기록됐다는 사실을 보여 줍니다. 필드 9·10이 채워져 있으면 mac_apt 해석으로 기록 당시 앱의 버전 문자열도 함께 볼 수 있습니다 [3].

**증명하지 못하는 것.** 상태 값 1이 "사용자가 앱을 앞에 띄웠다" 는 뜻인지는 도구 저자의 해석이라서 [1][3], macOS에서는 App.InFocus 기록만으로 앱 실행을 단정하지 않습니다. 기록이 사용자 폴더에 있어도 그 시각에 앱을 조작한 사람이 누구인지는 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)처럼 다른 자료로 따집니다. `remote` 폴더의 기록은 같은 계정의 다른 기기에서 일어난 사건이라서 이 맥에서 앱을 썼다는 근거가 되지 않습니다 [1].

보고서에는 기록으로 확인되는 만큼만 씁니다. 예를 들면 "사용자 폴더의 Biome App.InFocus 스트림 `local` 파일에, 번들 ID `com.example.app` 에 대해 상태 값 1(iLEAPP 해석 Foreground)인 기록이 있고, 기록 안의 시작 시각은 2024-09-02 19:59:50(UTC로 해석)이다" 처럼 씁니다. 날짜와 번들 ID는 아래 헥스 예시의 값입니다.

## 시각 해석

기록 하나에서 시각을 두 가지 읽을 수 있습니다 [1].

| 시각 | 자리 | iLEAPP 열 |
|---|---|---|
| SEGB 기록 시각 (쓰기 시각) | SEGB 파일의 기록 헤더(v1) 또는 트레일러(v2) | Timestamp |
| 시작 시각 | protobuf 필드 4 | Start Time |

두 값 모두 맥 절대 시각이고, iLEAPP은 978307200을 더해 유닉스 시각으로 바꾼 뒤 UTC로 표시합니다 [1]. 두 시각이 같은 순간이라고 단정할 수 없으므로, 타임라인에는 두 값을 따로 올리고 어느 쪽을 썼는지 적습니다. SEGB 쪽 시각의 자리와 시간대 처리는 [저장 위치와 스트림 (Streams)](streams.md), 맥 절대 시각을 푸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

## 함정과 한계

`remote` 기록이 결과의 대부분을 차지할 수 있습니다. iLEAPP 표본 가운데 iOS 17.6.1 이미지에서는 20368행 중 19852행이 `remote` 에서 왔습니다 [1]. iLEAPP은 이런 기록의 Sync Origin 열에 `Remote (<기기 id>)` 처럼 출처를 표시해서 [1], 이 열을 걸러 이 기기의 기록만 남긴 뒤 해석합니다. 출처 열이 없는 도구로 폴더를 통째로 읽었다면 결과를 다시 나눠야 합니다.

삭제 표시된 기록은 iLEAPP 결과에는 시각만 있는 행으로 나오고 mac_apt 결과에는 나오지 않아서, 같은 파일이라도 두 도구의 행 수가 다를 수 있습니다. 자세한 내용은 [저장 위치와 스트림 (Streams)](streams.md)의 "함정과 한계" 절에 있습니다.

위 버전 표처럼 iOS 16.x 표본에서는 App.InFocus가 0행이었지만 같은 이미지의 `_DKEvent.App.InFocus` 에는 행이 있었습니다 [1]. 한 스트림이 비었다고 앱 사용 기록이 없다고 단정하지 않고, 아래 교차 검증 자료를 함께 봅니다. macOS에서 knowledgeC의 `/app/inFocus` 와 어떻게 대응하는지는 같은 시간대의 두 기록을 나란히 놓고 비교해 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 실제 데이터가 아니라 iLEAPP의 필드 해석 [1]과 protobuf 부호화 규칙으로 만든 예시이고, SEGB 기록 헤더를 뺀 데이터 부분만 보여 줍니다. 실제 기록에 있는 필드 2·9·10은 뺐습니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
000000  18 01 21 00 00 20 5B 28 43 C6 41 32 0F 63 6F 6D   ..!.. [(C.A2.com
000010  2E 65 78 61 6D 70 6C 65 2E 61 70 70               .example.app
```

protobuf의 태그 바이트는 (필드 번호 × 8 + 자료형 번호)이고, 자료형 번호는 정수(varint) 0, 8바이트 값 1, 길이가 붙는 값 2입니다. 이 규칙으로 읽으면 다음과 같습니다.

1. 0x00의 `18` 은 필드 3, 정수입니다(3 × 8 + 0 = 0x18). 0x01의 `01` 이 값이라서 상태 1이고, iLEAPP은 Foreground, mac_apt는 "In focus" 로 표시합니다.
2. 0x02의 `21` 은 필드 4, 8바이트 값입니다(4 × 8 + 1 = 0x21). 0x03~0x0A의 `00 00 20 5B 28 43 C6 41` 을 LE double로 읽으면 746999990.25초이고, 978307200을 더한 유닉스 시각 1725307190.25는 2024-09-02 19:59:50.25(UTC로 읽을 때)입니다.
3. 0x0B의 `32` 는 필드 6, 길이가 붙는 값입니다(6 × 8 + 2 = 0x32). 0x0C의 `0F` 가 길이 15이고, 0x0D~0x1B의 15바이트가 번들 ID `com.example.app` 입니다.

SEGB 쪽 기록 시각은 이 데이터 바깥, v2 파일이라면 파일 끝 트레일러에 있습니다.

### 공개 도구로 한 번

iLEAPP의 App.InFocus 모듈은 결과를 Timestamp, Start Time, SEGB State, Bundle ID, Action, Sync Origin, Filename, Offset 열로 냅니다 [1]. Filename과 Offset 열이 있어서, 보고서에 올릴 행은 원본 파일의 그 자리를 헥스로 다시 열어 값을 확인할 수 있습니다. mac_apt BIOME 플러그인은 같은 스트림을 status, `product_name`, 앱 버전 문자열 필드로 해석합니다 [3]. 두 도구를 함께 돌려 행 수와 값이 맞는지 보면 해석 차이를 먼저 잡을 수 있습니다.

## 교차 검증

같은 앱 사용을 다른 스트림과 데이터베이스에서 확인합니다.

`_DKEvent.App.InFocus` 스트림을 iLEAPP은 아래처럼 풉니다 [1]. 시각은 모두 맥 절대 시각이고, 시작 시각과 종료 시각이 따로 있습니다.

| 필드 | 내용 |
|---|---|
| 1.1 | 활동 (문자열) |
| 2 | 시작 시각 (double) |
| 3 | 종료 시각 (double) |
| 4.3 | 번들 ID |
| 5 | 동작 GUID |
| 7.2.3 | 전환 (transition) |
| 8 | 쓰기 시각 (double) |

`ScreenTime.AppUsage` 스트림에도 앱 사용 흔적이 남습니다. mac_apt는 필드 1을 상태(0 = Out of focus, 1 = In focus), 필드 3을 번들 ID로 읽습니다 [3]. 이 스트림의 사건 코드 뜻은 문서화돼 있지 않고 기록 안의 시각 필드는 믿기 어려워서, iLEAPP은 저장된 값을 그대로 보고하고 SEGB 기록 시각을 씁니다 [1].

그 밖에 함께 볼 자료는 아래와 같습니다.

- [KnowledgeC (knowledgeC.db)](../knowledgec/index.md) — 같은 시간대의 앱 사용 기록
- [화면 사용 시간 (Screen Time)](../screen-time.md) — 앱별 사용 시간
- [통합 로그의 프로세스 실행 기록 (Process Events)](../unified-log-process.md) — 앱 프로세스가 실제로 떴는지
- [설치한 앱과 영수증 (Applications·Receipts)](../../system-account/installed-apps-receipts.md) — 번들 ID와 버전 문자열에 맞는 앱이 설치돼 있었는지
- [아이클라우드 계정 (iCloud Account)](../../cloud-apps/icloud-account.md) — `remote` 기록을 보낸 기기가 같은 계정에 묶여 있는지
- [어떤 앱을 언제 썼나 (App Usage)](../../../04-scenarios/activity/app-usage.md)

## 실습

Biome 폴더가 들어 있는 macOS 이미지(NIST CFReDS 같은 공개 시험 자료 목록에서 고른 이미지 등)로 아래 질문을 풀어 봅니다.

1. `~/Library/Biome/streams/restricted/App.InFocus/` 아래에 `local` 과 `remote` 폴더가 모두 있는가? `remote` 아래 기기 식별자 폴더는 몇 개인가?
2. `local` 파일 하나를 헥스로 열어 SEGB v1인지 v2인지 가르고, 첫 기록의 필드 3·4·6을 손으로 풀어 본다.
3. 같은 파일을 iLEAPP과 mac_apt로 돌려 행 수가 다른지 보고, 다르다면 SEGB State가 Deleted인 행 때문인지 확인한다.
4. 한 기록의 Timestamp와 Start Time은 얼마나 차이 나는가? 차이가 늘 같은 방향인가?
5. 같은 시간대의 knowledgeC 앱 사용 기록과 비교해 한쪽에만 있는 앱이 있는가?

## 참고 문헌

1. iLEAPP — scripts/artifacts/biomeInfocus.py, biomeDKInfocus.py, biomeStreams.py, scripts/ilapfuncs.py — https://github.com/abrignoni/iLEAPP
2. Mattia Epifani, "84 Streams Later, Part 2: Inside Apple Biome" (2026-07-27) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html
3. mac_apt (Yogesh Khatri), plugins/biome.py v1.1 — https://github.com/ydkhatri/mac_apt/blob/master/plugins/biome.py
