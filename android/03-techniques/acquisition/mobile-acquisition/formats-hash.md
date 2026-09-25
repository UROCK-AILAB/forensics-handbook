---
title: "결과물 형식과 해시"
parent: "모바일 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1350
---

# 결과물 형식과 해시 (Extraction Formats·Hash)

수집으로 얻은 결과물이 어떤 형식으로 나오는지, 분석 도구가 어떤 형식을 받는지, 결과물이 바뀌지 않았다는 것을 해시로 어떻게 보여 주는지 정리합니다. adb backup 파일 형식은 현행 AOSP 소스(frameworks/base 의 main 가지) 기준이라 이전 버전의 파일과 다를 수 있습니다.

## 한 줄 요약

모바일 결과물은 adb backup 파일, 버그 리포트 zip, 복사한 폴더, 디스크 이미지처럼 형식이 제각각이라 형식마다 머리를 확인해 읽고, 켜져 있는 기기는 수집할 때마다 전체 해시가 달라지니 결과물 파일의 해시를 기록해 두고 재수집 결과와는 항목별로 대조합니다.

## 결과물의 종류

| 결과물 | 만드는 경로 | 이 페이지에서 다루는 것 |
|---|---|---|
| adb backup 파일(.ab) | adb backup | 파일 머리와 버전 |
| 버그 리포트 zip | `adb bugreport` | 구성은 [ADB로 볼 수 있는 것](adb.md) 페이지 |
| 폴더 | `adb pull` 등 | 도구에 넣는 방법 |
| zip·tar·디스크 이미지 | 수집 도구 | 도구에 넣는 방법 |

## adb backup 파일(.ab)

adb backup 파일은 글자로 된 머리 몇 줄로 시작하고, 그 뒤에 백업 데이터가 이어집니다 [1][2].

| 순서 | 값 | 뜻 |
|---|---|---|
| 1번째 줄 | `ANDROID BACKUP` | 파일 머리 표시(`BACKUP_FILE_HEADER_MAGIC`) [1] |
| 2번째 줄 | 형식 버전. 현행 값 `5` | `BACKUP_FILE_VERSION` [1] |
| 3번째 줄 | `1` 또는 `0` | 압축 여부. `1` 이면 Deflater(`BEST_COMPRESSION`)로 deflate 압축 [2] |
| 4번째 줄 | 암호화하지 않으면 `none`, 암호화하면 `AES-256` | 암호화하면 이 자리부터 salt, checksum salt, PBKDF2 반복 횟수, IV, 암호화된 키 덩어리를 담은 AES 머리가 옴 [2] |

형식 버전마다 바뀐 점은 아래와 같아서, 2번째 줄로 그 파일을 만든 쪽의 형식 세대를 짐작할 수 있습니다 [1].

| 버전 | 바뀐 점 |
|---|---|
| 1 | 첫 출시 |
| 2 | PBKDF2 버전 차이를 알아보려고 번호만 올림 |
| 3 | `_meta` 메타데이터 파일 추가 |
| 4 | 기기 암호화(DE) 저장 위치 지원 |
| 5 | key-value 패키지 지원 |

아래는 형식 버전 5, 압축함, 암호화하지 않음으로 가정하고 명세대로 만든 파일 머리 예시이고, 실제 검체에서 뽑은 값이 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000000  41 4E 44 52 4F 49 44 20 42 41 43 4B 55 50 0A 35  ANDROID BACKUP.5
00000010  0A 31 0A 6E 6F 6E 65 0A                          .1.none.
```

줄 끝은 `0A` 이고, 이 예시에서는 머리가 0x18 바이트에서 끝나 그 뒤부터 압축한 데이터가 옵니다. 아카이브 안에는 앱별 `_manifest`(`BACKUP_MANIFEST_VERSION = 1`)와 `_meta`(`BACKUP_METADATA_VERSION = 1`) 파일이 들어가고, 위젯 메타데이터 표시로 `0x01FFED01`, 패키지 관리자 정보 자리표시로 `@pm@` 을 씁니다 [1]. 압축을 푼 안쪽은 tar 스트림이고, 끝에는 tar 의 끝 표시인 0으로 채운 512바이트 블록 두 개가 붙습니다 [2]. Android 12 이후 adb backup 에 앱 데이터가 빠지는 조건은 [ADB로 볼 수 있는 것](adb.md) 페이지에 있습니다.

## 분석 도구가 받는 형식

공개 도구 ALEAPP(Android Logs Events And Protobuf Parser)를 예로 들면, 입력 형식은 `-t` 로 고르고 `-i` 로 입력 경로, `-o` 로 보고서를 쓸 폴더를 줍니다 [3].

| `-t` 값 | 받는 것 |
|---|---|
| `zip` | zip 파일 [3] |
| `tar` | tar 파일. `.tar.xz` 도 읽고, `.tar.gz` 는 보고서 폴더에 임시로 풀어서 읽음 [3] |
| `gz` | gz 파일 [3] |
| `fs` | 폴더 [3] |
| `raw` | 디스크 이미지(`.img`, `.dd`, `.bin`, 분할 `.001`)와 EnCase/EWF(`.E01`)를 마운트나 관리자 권한 없이 읽고, 이미지 안에서 ext2/3/4, F2FS, FAT32, exFAT, NTFS 등의 파일 시스템을 찾음 [3] |

`.tar.gz` 를 넣으면 보고서 폴더에 풀린 사본이 생기니, 보고서 폴더의 크기와 사본의 해시를 원본과 따로 관리합니다. ALEAPP 설명서에는 해시를 계산하는 기능이나 시간대 옵션이 없고, 시험 때 `TZ=UTC` 를 쓴다는 내용만 있습니다 [3]. 이미지 안의 파일 시스템 구조는 [파일 시스템](../../../01-foundations/storage/filesystems/index.md) 페이지에 있습니다.

## 해시로 무결성 지키기

법과학 도구는 무결성을 두 가지로 지켜야 하는데, 원본 기기로 가는 쓰기 요청은 막거나 없애고, 추출한 데이터는 결과 파일의 암호학적 해시를 계산해 파일이 쓰이는 동안 계속 같은지 확인합니다 [4]. 법과학 도구가 아닌 도구로 수집했다면 sha1sum 같은 도구로 해시를 만들어 보관하고, 법과학 도구 중에도 해시를 계산하지 않는 것이 있으니 그때는 따로 계산합니다 [4].

1. 결과물 파일마다 해시를 계산해 기록합니다 [4]. 나중에 어느 파일의 값인지 헷갈리지 않도록 파일 이름·크기와 해시 알고리즘 이름도 함께 적습니다.
2. 결과물을 쓰는 동안과 분석을 마친 뒤에 해시를 다시 계산해 처음 값과 같은지 확인합니다 [4].
3. 같은 기기를 다시 수집했다면 전체 해시가 아니라 파일·디렉터리 같은 항목별 해시를 서로 대조합니다 [4].
4. 증거를 누가 언제 어디로 옮겼는지 연계 보관(chain of custody) 기록에 남깁니다 [4].

모바일 기기는 늘 켜져 기기 시계 같은 정보를 계속 갱신해서, 같은 기기를 연달아 두 번 수집해도 전체 데이터의 해시는 다르게 나오고 개별 파일·디렉터리의 해시는 대체로 같게 나옵니다 [4]. 해시가 어긋나면 항목을 하나씩 대조해 무결성을 확인해야 할 수 있고, 도구마다 보고 형식이 달라 여러 도구 사이의 해시 대조는 어렵습니다 [4]. 도구 결과를 서로 맞춰 보는 방법은 [도구 검증](../../reporting/tool-validation.md) 페이지에 있습니다.

## 수집 당시 상태 기록

결과물과 함께 수집 당시 기기가 어떤 빌드였는지와 수집 날짜·시간대를 적어 둡니다. `dumpsys package` 출력의 Database versions 절에는 `buildFingerprint`, `fingerprint`, `sdkVersion` 칸이 있어서 수집 당시 빌드를 기록할 때 쓸 수 있습니다. 빌드 정보를 읽는 법은 [기기 정보와 빌드](../../../02-artifacts/system-account/device-build.md) 페이지에 있습니다.

logcat 시각에는 연도가 없으니, logcat 을 결과물에 넣을 때는 수집한 날짜와 시간대를 따로 적어 둡니다. 기기 시각은 기준 시계와 비교해 기록해 둡니다 [4]. 화면 시각을 기록하는 절차는 [압수와 보관](seizure-handling.md) 페이지에 있습니다. 시각 값을 바꾸는 법은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다.

## 함정과 한계

재수집한 결과의 전체 해시가 처음 결과와 다르다고 해서 조작이나 손상이라고 단정하지 않습니다 [4]. .ab 파일 형식은 현행 소스 기준이라 오래된 기기에서 만든 파일은 2번째 줄의 버전부터 확인합니다. 도구가 결과물을 풀거나 옮기면서 만든 사본은 원본 결과물과 해시가 다를 수 있으니, 어느 파일의 해시인지 이름과 경로까지 함께 적습니다.

## 결과를 어떻게 해석하나

해시가 말해 주는 범위는 "이 파일이 기록한 때 이후로 바뀌지 않았다" 이고, 수집 과정에서 기기가 바뀌지 않았다는 것까지 보여 주지는 않습니다. 보고서에는 아래처럼 씁니다.

> (날짜·시각) 에 받은 결과물 (파일 이름) 의 (알고리즘) 해시는 (값) 이고, 분석을 마친 (날짜·시각) 에 다시 계산한 값도 같습니다. 같은 기기를 (날짜) 에 다시 수집한 결과와는 전체 해시가 다르지만, 이 보고서에 인용한 파일들의 항목별 해시는 두 결과에서 같습니다.

형식 전반의 보고서 작성은 [포렌식 보고서](../../reporting/forensic-report.md) 페이지에 있습니다.

## 참고 문헌

1. UserBackupManagerService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/backup/java/com/android/server/backup/UserBackupManagerService.java
2. PerformAdbBackupTask.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/backup/java/com/android/server/backup/fullbackup/PerformAdbBackupTask.java
3. ALEAPP — abrignoni/ALEAPP (GitHub README), https://github.com/abrignoni/ALEAPP
4. NIST SP 800-101 Rev.1, Guidelines on Mobile Device Forensics (Ayers, Brothers, Jansen, 2014), https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-101r1.pdf
