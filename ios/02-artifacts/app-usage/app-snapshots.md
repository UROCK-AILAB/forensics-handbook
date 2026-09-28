---
title: "앱 화면 스냅숏"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 460
---

# 앱 화면 스냅숏 (App Snapshots·KTX)

앱이 백그라운드로 들어갈 때 iOS 는 그 순간의 앱 화면을 이미지로 찍어 앱 전환기 (app switcher) 에 보여 주고, 이 이미지는 주로 `SplashBoard/Snapshots` 아래에 KTX 파일로 남습니다. 앱 DB 에서 지워진 대화나 지도 화면이 스냅숏에 그대로 남아 있을 수 있고, 찍은 시각은 `applicationState.db` 의 스냅숏 목록과 파일 시각으로 읽습니다.

## 무엇을 기록하나 · 왜 생기나

앱이 백그라운드로 들어가고 앱이 이 전환을 처리하는 메서드를 마치면 UIKit 이 앱의 현재 화면을 찍습니다[1]. 시스템은 이 이미지를 앱 전환기에 보여 주고, 앱을 다시 앞으로 불러올 때도 잠깐 보여 줍니다[1]. 화면을 쓸어 올려 앱을 벗어나거나, 홈 버튼을 누르거나, 앱을 쓰는 도중에 전화가 와도 스냅숏이 생깁니다[2].

그래서 스냅숏에는 앱을 벗어나기 직전 화면에 떠 있던 내용이 담깁니다. 메신저 대화, 지도 위치, 메모, 검색 화면이 이렇게 남고, 앱 DB 의 기록이 지워진 뒤에도 스냅숏에 대화 화면이 남아 사건 해결에 쓰인 사례가 있습니다[10]. 반대로 Apple 은 암호나 카드 번호 같은 민감한 정보를 스냅숏 전에 화면에서 치우라고 개발자에게 안내하고 있어서[1], 앱에 따라서는 가림 화면이나 실행 화면이 찍혀 있습니다[4].

이미지 파일과 따로, 시스템은 앱마다 스냅숏 목록을 `applicationState.db` 의 `XBApplicationSnapshotManifest` 값에 적어 둡니다[2][3][5]. 이 목록에 파일 이름과 만든 시각이 있어서, 이미지와 목록을 파일 이름으로 이으면 어느 앱의 어느 화면을 언제 찍었는지 알 수 있습니다[4].

## 위치와 버전별 차이

스냅숏은 iOS 10 부터 KTX 파일로 저장됩니다[2]. KTX 는 Khronos 그룹이 정한 텍스처 이미지 형식으로, 텍스처나 이미지 여러 장을 한 파일에 담을 수 있습니다[2]. 경로는 두 가지가 알려져 있습니다.

```
# iOS 11·12 를 다룬 글에 나온 경로 [2]
/private/var/mobile/Library/Caches/Snapshots/<번들 ID>/<번들 ID>/
/private/var/mobile/Containers/Data/Application/<앱 UUID>/Library/Caches/Snapshots/<번들 ID>/

# SplashBoard 아래 경로 [6]
/private/var/mobile/Library/SplashBoard/Snapshots/<번들 ID>/sceneID:<번들 ID>-default/<이름>@3x.ktx
/private/var/mobile/Containers/Data/Application/<앱 UUID>/Library/SplashBoard/Snapshots/sceneID:<번들 ID>-default/<이름>@3x.ktx
```

iLEAPP 는 두 경로의 `.ktx` 와 `.jpeg` 를 모두 찾습니다[4]. iLEAPP 시험 데이터 세 개(iOS 15 이미지 하나 포함)에서는 `Library/Caches/Snapshots` 에 맞는 파일이 0개이고, 파일은 모두 `SplashBoard/Snapshots` 아래에 있습니다[7]. 두 경로를 다 검색하고, 실제로 파일이 나온 경로를 보고서에 적습니다.

| 폴더·이름 | 뜻 | 근거 |
|---|---|---|
| `sceneID:번들ID-default` | 앱 장면 (scene) 하나의 폴더. 끝이 `-default` 대신 UUID 인 폴더도 있음 | [4][6] |
| `downscaled` | 장면 폴더 아래 작은 크기 이미지를 담는 하위 폴더 | [4][6] |
| `@3x`, `@2x` | 파일 이름 끝의 화면 배율 표시 | [3][6] |
| `sceneID_` | 콜론을 쓸 수 없는 곳으로 파일을 옮기면 `sceneID:` 가 이렇게 바뀌어 있을 수 있음 | [4] |

한 화면에 대해 라이트 모드용과 다크 모드용 두 장이 만들어집니다[10]. 앱 스냅숏과 별개로 배경화면, PosterBoard 스냅숏, 아바타 같은 시스템 화면 이미지는 `.atx` 텍스처 파일로도 남고, iLEAPP 는 이를 따로 풉니다[9]. `.atx` 의 구조는 실제 파일에서 알아낸 것이고 Apple 이 문서로 밝힌 형식이 아닙니다[9].

이미지 파일이 없는 논리 추출에서도 `applicationState.db` 만 있으면 스냅숏 목록과 시각을 읽을 수 있습니다[5]. 로컬 백업에 이 DB 가 들어 있는지는 [설치된 앱](installed-apps.md) 에서 다룹니다. 이미지 자체는 파일 시스템 추출에서 얻고, 수집 방식 차이는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

## 구조

### KTX 파일

iOS 가 만든 KTX 는 텍스처 형식 `glInternalFormat` 이 `0x93B0`(ASTC 4x4)이고, 텍스처 데이터는 Apple 의 압축 방식 LZFSE 로 한 번 더 압축되어 있습니다[8]. ASTC (Adaptive Scalable Texture Compression) 는 4x4 픽셀 블록 단위로 줄이는 손실 압축입니다[8]. 머리글은 0x40 바이트이고, 주요 필드의 위치는 다음과 같습니다[11].

| 오프셋 | 크기 | 필드 |
|---|---|---|
| `0x00` | 12 | 식별자 `«KTX 11»\r\n\x1A\n` |
| `0x0C` | 4 | 바이트 순서 표시. `01 02 03 04` 면 리틀 엔디언 |
| `0x1C` | 4 | `glInternalFormat`. iOS 스냅숏은 `0x93B0` |
| `0x24` | 4 | `pixelWidth` |
| `0x28` | 4 | `pixelHeight` |
| `0x3C` | 4 | `bytesOfKeyValueData`. 머리글 뒤 키-값 영역의 길이 |

키-값 영역에 `Compression_APPLE` 문자열이 있으면 데이터가 압축된 것이고, 그 뒤 데이터의 13번째 바이트(오프셋 12)부터 `bvx` 로 시작하는 LZFSE 블록이 옵니다[11]. 확장자는 `.ktx` 인데 머리글이 `AAPL\r\n\x1A\n` 인 파일도 있습니다[8]. 이 파일은 4바이트 길이와 4바이트 이름표로 된 조각이 이어지고, `HEAD` 조각에 너비·높이가, `LZFS` 조각에 압축된 데이터가, `astc`·`ASTC` 조각에 압축하지 않은 데이터가 들어 있습니다[11].

### 스냅숏 목록

`applicationState.db` 의 `kvs` 표 값 가운데, `key_tab` 의 `key` 가 `XBApplicationSnapshotManifest` 인 값이 스냅숏 목록입니다[5]. 값은 NSKeyedArchiver 로 저장한 이진 plist 이고[5], 이진 plist 안에 이진 plist 가 한 번 더 들어 있습니다[2][3]. iLEAPP 는 `version` 값이 3 인 목록을 기준으로 만들었습니다[5]. 풀어 보면 `identifier` 가 장면 폴더 이름과 같은 묶음마다 `snapshots` 목록이 있고, 스냅숏 하나에 다음 필드가 있습니다[5].

| 필드 | 뜻 |
|---|---|
| `creationDate` | 스냅숏 개체를 만든 시각 |
| `lastUsedDate` | 뜻이 문서화되지 않은 시각. 값이 없는 스냅숏이 많음 |
| `expirationDate` | 도구가 날짜로 보여 주는 값. 뜻은 문서화되지 않음 |
| `relativePath` | 이미지 파일 이름. 이 이름으로 KTX 파일과 잇습니다[4] |
| `identifier`, `groupID`, `name`, `launchInterfaceIdentifier` | 스냅숏과 묶음의 식별 값 |
| `imageScale`, `referenceSize`, `interfaceOrientation`, `fullScreen`, `imageOpaque`, `backgroundStyle`, `contentType`, `fileLocation`, `requiredOSVersion` | 이미지 크기·방향·표시 방식·저장 위치 등 |

`creationDate` 와 `lastUsedDate` 라는 이름은 SplashBoard 의 `XBApplicationSnapshot` 속성 이름이고, Apple 은 두 값의 뜻을 문서로 밝히지 않았습니다[5]. plist 푸는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 스냅숏 이미지는 그 앱이 백그라운드로 들어가던 순간에 앱 화면에 무엇이 그려져 있었는지를 보여 줍니다[1]. 폴더 이름과 스냅숏 목록으로 어느 번들 ID 의 화면인지 알 수 있고[4][6], 앱 DB 에 없는 대화·위치·검색어가 화면에 찍혀 있으면 그 내용이 한때 이 기기의 그 앱 화면에 있었다는 근거가 됩니다[10]. 번들 ID 읽는 법은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에서 다룹니다.

**증명하지 못하는 것.** 스냅숏이 있다고 사용자가 그 화면을 봤다고 말할 수 없습니다[4][5]. 앱이 민감한 내용을 스냅숏 전에 가리거나 바꿀 수 있어서, 이미지가 실행 화면이나 가림 화면일 수 있습니다[1][4]. `creationDate` 는 스냅숏 개체를 만든 시각이고, 이 값만으로 앱이 그 시각에 앞 화면에 있었다고 말할 수 없습니다[5]. 누가 기기를 들고 있었는지도 알려 주지 않아서, 그 판단은 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 를 따릅니다.

보고서에는 "피의자가 이 대화를 봤다" 대신 "`com.example.app` 의 스냅숏 파일 `이름@3x.ktx` 를 PNG 로 바꾼 이미지에 이 대화가 보이고, 스냅숏 목록의 `creationDate` 는 이 값이다" 처럼 파일 경로와 원래 값을 함께 씁니다(`com.example.app` 과 파일 이름은 만든 예시).

## 시각 해석

스냅숏에는 시각이 세 가지 붙습니다. iLEAPP 는 이를 `File Modified Date`, `Manifest Creation Date`, `Manifest Last Used Date` 열로 나눠 보여 줍니다[4].

| 시각 | 어디서 | 해석 |
|---|---|---|
| 파일 수정 시각 | 파일 시스템 메타데이터 | 이미지 파일이 마지막으로 쓰인 시각. iLEAPP 는 UTC 로 바꿔 보여 줍니다[4] |
| `creationDate` | 스냅숏 목록 | 스냅숏 개체를 만든 시각. iLEAPP 개발자가 시험한 iOS 18·26 추출에서는 해당 이미지 파일의 UTC 수정 시각과 추출 ZIP 이 담을 수 있는 정밀도 안에서 같았습니다[5] |
| `lastUsedDate` | 스냅숏 목록 | 값이 있는 스냅숏이 적고, `creationDate` 보다 한참 뒤에 바뀌기도 합니다. 언제 바뀌는지는 문서화되지 않았습니다[5] |

스냅숏은 앱이 백그라운드로 들어간 뒤에 찍히므로[1], `creationDate` 는 그 무렵 앱이 앞 화면에서 벗어났을 가능성을 살펴보는 단서로 쓸 수 있습니다. 다만 앞 화면에 있던 구간은 [KnowledgeC](knowledgec/index.md) 나 [바이옴](biome/index.md) 에서 따로 확인합니다. iLEAPP 는 스냅숏 목록의 시각을 날짜 열로 풀어 보여 주고[5], 시각 기준은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

**작은 KTX 는 도구가 건너뜁니다.** iLEAPP 는 2500바이트보다 작은 KTX 파일을 결과에 넣지 않습니다[4]. 도구 결과의 개수와 폴더 안 파일 개수가 다르면 이 조건부터 봅니다.

**모든 KTX 가 스냅숏은 아닙니다.** 앱이 번들에 넣어 배포한 KTX 가운데는 ASTC 4x4 가 아닌 형식이 있어서 같은 방법으로 풀리지 않습니다[8]. 스냅숏 폴더 밖의 KTX 는 스냅숏으로 다루지 않습니다.

**이미지 내용을 그대로 믿지 않습니다.** 앱이 가림 화면을 찍게 했거나 실행 화면이 남았을 수 있습니다[1][4]. 화면 속 대화·위치는 앱 DB, 알림, 스크린샷 같은 다른 기록과 맞춰 봅니다.

**경로 이름이 바뀌어 있을 수 있습니다.** 추출 결과를 옮기는 과정에서 `sceneID:` 가 `sceneID_` 로 바뀌면 경로 검색에서 빠질 수 있어서[4], 두 모양을 모두 찾습니다.

**지우기와 조작.** 앱 안에서 대화를 지워도 그 전에 찍힌 스냅숏은 남을 수 있습니다[10]. 반대로 스냅숏이 없다고 그 앱을 쓰지 않았다고 말할 수 없고, 증거 인멸 판단은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름을 따릅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 너비 1170(`0x492`), 높이 2532(`0x9E4`)인 리틀 엔디언 KTX 의 머리글입니다(만든 예시).

```
00000000  AB 4B 54 58 20 31 31 BB 0D 0A 1A 0A 01 02 03 04  «KTX 11»....
00000010  .. .. .. .. .. .. .. .. .. .. .. .. B0 93 00 00  glInternalFormat 0x93B0
00000020  .. .. .. .. 92 04 00 00 E4 09 00 00 .. .. .. ..  pixelWidth, pixelHeight
00000030  .. .. .. .. .. .. .. .. .. .. .. .. xx xx xx xx  bytesOfKeyValueData
```

`0x1C` 가 `B0 93 00 00` 이면 iOS 가 만든 ASTC 4x4 텍스처이고[8][11], `0x3C` 값만큼 머리글 뒤를 건너뛴 곳에서 텍스처 데이터가 시작합니다[11]. 첫 8바이트가 `41 41 50 4C 0D 0A 1A 0A`(`AAPL....`)이면 조각 구조의 변형 파일입니다[8][11].

### SQL 로 스냅숏 목록 찾기

`applicationState.db` 사본에서, 스냅숏 목록이 있는 앱과 값 길이를 뽑습니다.

```sql
SELECT a.application_identifier, length(v.value) AS manifest_len
FROM kvs v
JOIN application_identifier_tab a ON a.id = v.application_identifier
JOIN key_tab k ON k.id = v.key
WHERE k.key = 'XBApplicationSnapshotManifest'
ORDER BY a.application_identifier;
```

`value` 를 파일로 꺼내 NSKeyedArchiver 를 푸는 도구로 열면 `relativePath` 와 `creationDate` 를 볼 수 있습니다[5]. 표 관계는 [설치된 앱](installed-apps.md) 에서 다룹니다.

### 공개 도구로 한 번

KTX 한 장은 Yogesh Khatri 의 `ios_ktx2png.py` 로 PNG 로 바꿉니다. `pyliblzfse`, `astc_decomp`, `pillow` 가 필요하고, 결과는 같은 폴더에 원래 이름 뒤에 `.png` 를 붙인 파일(`SAMPLE.KTX.png`)로 생깁니다[11]. Windows 실행 파일도 함께 공개되어 있습니다[8].

```
python3 ios_ktx2png.py SAMPLE.KTX
```

기기 전체는 iLEAPP 의 App Snapshots 가 KTX 를 PNG 로 바꾸고 `applicationState.db` 의 스냅숏 목록과 이어 번들 ID·장면 폴더·시각을 한 표로 보여 줍니다[4]. 이미지 없이 목록만 볼 때는 iLEAPP 의 Application Snapshot 과 Application Snapshot lastUsedDate 결과를 씁니다[5]. 도구가 바꾼 PNG 는 원본 KTX 의 경로와 해시를 함께 기록해 두고, 도구 검증은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

스냅숏의 `creationDate` 앞뒤에 그 앱이 앞 화면에 있었는지는 iOS 15 이하는 [KnowledgeC](knowledgec/index.md), iOS 16 이후는 [바이옴](biome/index.md) 에서 봅니다. 사용자가 직접 찍은 화면은 스냅숏이 아니라 사진 보관함에 들어가서 [스크린샷과 화면 녹화](../media/screenshots.md) 에서 따로 찾습니다. 번들 ID 가 지금 설치된 앱인지는 [설치된 앱](installed-apps.md), 앱을 쓴 시간 흐름 전체는 [어떤 앱을 언제 썼나](../../04-scenarios/activity/app-usage.md) 에서 맞춥니다.

## 실습

공개 시험 데이터(NIST CFReDS 등의 iOS 파일 시스템 이미지)로 다음 질문을 풀어 봅니다.

1. `SplashBoard/Snapshots` 와 `Library/Caches/Snapshots` 아래 KTX 파일은 각각 몇 개입니까?
2. 머리글 `0x1C` 가 `0x93B0` 이 아닌 KTX 가 있습니까? 있다면 어느 폴더에 있습니까?
3. `downscaled` 폴더가 있는 장면 폴더는 어느 번들 ID 의 것입니까?
4. `XBApplicationSnapshotManifest` 의 `relativePath` 와 이름이 같은 파일이 없는 스냅숏이 있습니까?
5. `creationDate` 와 이미지 파일의 수정 시각이 다른 스냅숏이 있다면 몇 초 차이입니까?

## 참고 문헌

- [1] Preparing your UI to run in the background — Apple Developer Documentation — https://developer.apple.com/documentation/uikit/preparing-your-ui-to-run-in-the-background
- [2] A "Quick Look" into iOS Snapshots — Geri, 4n6 Ninja (2019-09-29) — https://gforce4n6.blogspot.com/2019/09/a-quick-look-into-ios-snapshots.html
- [3] iOS Snapshots Triage Parser & working with KTX files — Alexis Brignoni (2019-09-29) — https://abrignoni.blogspot.com/2019/09/ios-snapshots-triage-parser-working.html
- [4] iLEAPP, `scripts/artifacts/appSnapshots.py` — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appSnapshots.py
- [5] iLEAPP, `scripts/artifacts/applicationStateDB.py` — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/applicationStateDB.py
- [6] iLEAPP, `admin/test/scripts/test_app_snapshots.py` — https://github.com/abrignoni/iLEAPP/blob/main/admin/test/scripts/test_app_snapshots.py
- [7] iLEAPP, `admin/data/generated/filepath_results.csv` — https://github.com/abrignoni/iLEAPP/blob/main/admin/data/generated/filepath_results.csv
- [8] KTX to PNG in Python for iOS snapshots — Yogesh Khatri, Swift Forensics (2020-07) — https://swiftforensics.com/2020/07/ktx-to-png-in-python-for-ios-snapshots.html
- [9] iLEAPP, `scripts/artifacts/apple_atx_images.py` — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/apple_atx_images.py
- [10] That One Artifact: Snapshot to justice — Magnet Forensics (2025-05-21) — https://www.magnetforensics.com/blog/that-one-artifact-snapshot-to-justice/
- [11] iLEAPP, `scripts/ktx/ios_ktx2png.py` (Yogesh Khatri) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/ktx/ios_ktx2png.py
