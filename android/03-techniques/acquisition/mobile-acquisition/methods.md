---
title: "수집 방식 비교"
parent: "모바일 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1310
---

# 수집 방식 비교 (논리·파일 시스템·물리)

모바일 기기에서 데이터를 뽑는 방식을 NIST 분류로 나누어 보고, Android 10 이후 기기에서 파일 단위 암호화 때문에 무엇이 달라지는지 정리합니다. 압수 직후 기기를 다루는 법은 [압수와 보관](seizure-handling.md), adb 로 할 수 있는 일은 [ADB로 볼 수 있는 것](adb.md), 백업을 거치는 방법은 [백업으로 수집](backups.md) 페이지에 있습니다.

## 한 줄 요약

수집 방식은 운영체제를 거쳐 파일을 복사하는 논리 수집과 저장 칩을 그대로 뜨는 물리 수집으로 크게 갈리고, Android 10 이후 기기에서는 어느 방식을 고르든 사용자가 잠금을 풀었는지에 따라 읽을 수 있는 범위가 달라집니다.

## NIST 의 다섯 단계

NIST SP 800-101 Rev.1 은 수집 도구를 다섯 단계로 나눕니다. 위 단계로 갈수록 더 기술적이고 기기를 더 건드리며 시간과 비용이 더 듭니다 [3].

| 단계 | 이름 | 하는 일 | 필요한 교육 |
|---|---|---|---|
| 1 | 수동 추출 (Manual Extraction) | 기기 화면을 사용자 화면(UI)으로 하나씩 띄워 기록합니다 | 따로 정해져 있지 않음 |
| 2 | 논리 추출 (Logical Extraction) | 파일 시스템 파티션 같은 논리 저장소 위의 디렉터리·파일을 복사합니다. 지금 가장 많이 쓰는 방법입니다 | 약간의 기술과 초급 교육 |
| 3 | 헥스 덤프·JTAG (Hex Dumping/JTAG) | 메모리를 기기 안에 그대로 둔 채 물리 수집을 합니다 | 고급 교육 |
| 4 | 칩 오프 (Chip-Off) | 메모리를 기기에서 떼어 내 읽습니다 | 전자공학과 파일 시스템 포렌식 교육이 많이 필요 |
| 5 | 마이크로 리드 (Micro Read) | 고배율 현미경으로 게이트의 물리 상태를 봅니다. 가장 침습적이고 비쌉니다 | 따로 정해져 있지 않음 |

2단계는 논리 객체를 복사하고 3~5단계는 메모리 칩 같은 물리 저장소의 복사본이나 이미지를 뜹니다 [3]. 두 쪽의 차이는 운영체제를 거쳐 본 메모리(논리 보기)와 하드웨어가 본 원시 메모리(물리 보기)의 차이에서 옵니다 [3]. 물리 방식은 삭제된 객체와 미할당 영역의 잔재까지 볼 수 있지만 뽑은 이미지를 직접 파싱·복호·해석해야 하고, 논리 방식은 범위가 좁은 대신 시스템 자료 구조를 높은 수준에서 보기 때문에 도구가 뽑아서 보여 주기 쉽습니다 [3]. 지운 데이터를 되살리는 방법은 [삭제 데이터 복구](../../analysis/data-recovery/index.md) 페이지에 있습니다.

현업에서는 "파일 시스템 수집(full file system)" 이라는 말도 흔히 쓰지만, NIST 분류에는 따로 이름이 없고, 디렉터리·파일 같은 논리 객체를 복사한다는 점에서 2단계 설명과 겹칩니다 [3]. 도구 보고서에 이 이름이 적혀 있으면 이름보다 실제로 어떤 경로가 결과물에 들어 있는지를 먼저 확인합니다.

## Android 10 이후: 파일 단위 암호화와 수집 범위

Android 10 이상으로 출시되는 기기는 모두 파일 단위 암호화 (File-Based Encryption, FBE) 를 써야 하고, FBE 자체는 Android 7.0 부터 지원합니다 [1]. FBE 는 저장소를 두 종류로 나눕니다 [1].

| 저장소 | 쓸 수 있는 때 | 경로 |
|---|---|---|
| CE (Credential Encrypted) | 사용자가 기기 잠금을 푼 뒤에만. 기본 저장 위치입니다 | `/data/data`(`/data/user/0` 의 별칭), `/data/user/${user_id}`, `/data/misc_ce/${user_id}`, `/data/system_ce/${user_id}`, `/data/vendor_ce/${user_id}`, `/data/media/${user_id}` |
| DE (Device Encrypted) | 다이렉트 부트 모드에서도, 잠금 해제 뒤에도 | `/data/misc_de/${user_id}`, `/data/system_de/${user_id}`, `/data/user_de/${user_id}`, `/data/vendor_de/${user_id}` |

다이렉트 부트 (Direct Boot) 는 암호화된 기기가 부팅 뒤 곧바로 잠금 화면까지 올라오게 하는 기능이고, 사용자가 자격 증명을 넣기 전에도 앱 일부가 돌 수 있습니다 [1]. 사진·다운로드 같은 공유 저장소의 실제 자리인 `/data/media/${user_id}` 도 CE 쪽에 들어 있어서, 잠금을 풀기 전에는 공유 저장소도 읽을 수 없다고 봐야 합니다 [1]. 폴더 배치는 [앱 데이터 폴더 구조](../../../01-foundations/storage/app-data-layout.md)와 [공용 저장 공간](../../../01-foundations/storage/shared-storage.md), 암호화 구조는 [저장 공간 암호화](../../../01-foundations/storage/encryption/index.md) 페이지에 있습니다.

| Android 버전 | 수집 범위와 관련된 변화 |
|---|---|
| 7.0 | FBE 지원 시작 [1] |
| 9 | FBE 와 외장 저장소를 내부 저장소처럼 쓰는 기능(adoptable storage)을 함께 쓸 수 있고, 메타데이터 암호화도 지원 [1] |
| 10 이후 출시 기기 | FBE 의무 [1] |

현업에서 흔히 쓰는 "첫 잠금 해제 전·후(BFU·AFU)" 는 여기서 "잠금을 풀어 CE 를 쓸 수 있는 상태" 와 "그렇지 않은 상태" 로 나눠 봅니다. 켜 둔 기기를 끄거나 다시 켜면 이 상태가 어떻게 바뀌는지는 [압수와 보관](seizure-handling.md) 페이지에 정리했습니다.

NIST SP 800-101 Rev.1 은 2014년 문서라서 FBE 가 의무가 되기 전에 나왔고, 다섯 단계 분류에도 FBE 로 생기는 제약은 들어 있지 않습니다 [3][1]. 물리 수집이 더 많은 것을 보여 준다는 설명은 이 점을 감안해서 읽습니다.

## 논리 수집 경로의 예

adb 의 `adb pull` 은 기기의 파일·디렉터리를 하위 폴더까지 컴퓨터로 복사하지만 [2], 어떤 경로를 읽을 수 있는지는 셸 권한에 달려 있습니다. 루팅하지 않은 폰에서도 adb 일반 셸 권한(UID 2000)으로 `/sdcard` 최상위 폴더 목록과 DCIM·Pictures·Download·Documents·Android 아래 항목 수를 읽을 수 있고, `/sdcard/Android` 아래에는 data, media, obb 세 폴더가 있습니다. 같은 권한으로 `/sdcard/Android/data` 안의 앱별 폴더나 `/data/data`, `/data/system_ce` 아래 파일을 읽을 수 있는지는 기기에서 확인합니다.

| 경로 | 얻는 것 | 자세히 |
|---|---|---|
| `adb pull` | 셸 권한으로 읽을 수 있는 파일과 폴더 | [ADB로 볼 수 있는 것](adb.md) |
| adb backup | 백업 대상인 앱의 데이터. Android 12 이후 제약이 있음 | [ADB로 볼 수 있는 것](adb.md) |
| bugreport·dumpsys | 수집하는 순간의 시스템 상태와 로그 | [ADB로 볼 수 있는 것](adb.md) |
| Google 계정 백업·기기 간 전송 | 백업 규칙이 허락한 앱 데이터와 통화 기록·연락처·문자 등 | [백업으로 수집](backups.md) |

## 삼성 One UI 에서 볼 점

삼성 기기에서 수집 방식마다 무엇이 달라지는지(보안 폴더, 녹스 등)는 실제 기기로 확인해야 합니다. 삼성 폰의 `dumpsys user` 출력에는 주 사용자(`isPrimary=true`) 말고도 사용자 번호가 세 자리인 두 번째 사용자(`isPrimary=false parentId=#`)가 나올 수 있습니다. 이 사용자가 보안 폴더인지 다른 프로필인지는 실제 기기에서 확인합니다. 다만 사용자나 프로필이 여럿이면 `${user_id}` 마다 CE·DE 경로가 따로 있어서 [1], 주 사용자 경로만 수집하면 다른 프로필의 데이터가 빠집니다. 프로필 구조는 [보안 폴더와 작업 프로필](../../../01-foundations/security-model/secure-folder-work-profile.md)과 [사용자와 프로필](../../../02-artifacts/system-account/users-profiles.md) 페이지를 봅니다.

## 함정과 한계

한 단계를 쓰고 나면 다른 단계를 쓸 수 없게 될 수 있고, 칩 오프를 한 뒤에는 그보다 아래 단계의 도구를 물리적으로 쓸 수 없는 것이 그 예입니다 [3]. 단계가 올라갈수록 데이터가 바뀌거나 망가질 위험도 커져서 [3], 덜 침습적인 방법으로 얻을 수 있는 것을 먼저 얻고 나서 다음 단계를 정합니다.

논리 수집은 운영체제가 보여 주는 파일만 담기 때문에 삭제된 객체와 미할당 영역은 들어가지 않습니다 [3]. 논리 수집 결과에서 무언가를 찾지 못했다면 그 사실이 곧 지워졌다는 뜻도, 처음부터 없었다는 뜻도 아닙니다.

## 결과를 어떻게 해석하나

보고서에는 어떤 방식으로 수집했는지와 함께, 수집할 때 기기가 잠금 해제 상태였는지를 적습니다. 잠금을 풀지 않은 상태에서 얻은 결과에 사진이나 앱 데이터베이스가 없다면, 데이터가 없었던 것이 아니라 CE 영역이라 읽지 못했을 수 있습니다 [1]. 같은 기기를 다른 방식으로 다시 수집하면 결과가 달라질 수 있으니, 결과물 사이의 비교는 [결과물 형식과 해시](formats-hash.md) 페이지의 해시 대조 방법을 따릅니다.

## 참고 문헌

1. File-based encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/file-based
2. Android Debug Bridge (adb) — Android Developers, https://developer.android.com/tools/adb
3. NIST SP 800-101 Rev.1, Guidelines on Mobile Device Forensics (Ayers, Brothers, Jansen, 2014), https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-101r1.pdf
