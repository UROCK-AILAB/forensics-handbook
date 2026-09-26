---
title: "조사 절차"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 1290
---

# 조사 절차 (Investigation Process)

Android 기기를 손에 넣은 때부터 보고서를 낼 때까지의 흐름을 한 장에 정리합니다. 뼈대는 NIST SP 800-101 Rev.1 의 네 단계를 따르고, 각 단계의 세부 조치는 따로 정리한 페이지로 이어집니다.

## 한 줄 요약

Android 기기 조사는 보존, 수집, 검사와 분석, 보고의 네 단계로 나눠 진행하고, 단계마다 한 일을 나중에 처음부터 다시 해 볼 수 있을 만큼 기록합니다.

## 언제 쓰나

사건에 휴대전화가 걸려 있을 때 조사 전체의 순서를 잡는 데 씁니다. 모바일 포렌식 절차는 보존(Preservation), 수집(Acquisition), 검사와 분석(Examination and Analysis), 보고(Reporting) 의 네 단계로 나뉘고 [1], 이 페이지도 같은 순서를 따릅니다.

NIST SP 800-101 Rev.1 은 2014년 문서라서 Android 10 부터 의무가 된 파일 단위 암호화(File-Based Encryption, FBE) 가 나오기 전에 쓰였습니다. Android 10 이후 기기에 맞춘 내용은 따로 출처를 달았습니다.

## 절차

### 1단계: 보존

보존은 기기와 이동식 매체의 데이터를 바꾸지 않고 보관하는 과정이고, 디지털 증거를 확보하는 첫 단계입니다 [1]. 수색, 식별, 기록, 수집이 모두 여기에 들어가며, 원래 상태로 보존하지 못하면 조사 전체가 흔들릴 수 있습니다 [1]. 보존 단계는 아래 순서로 진행합니다 [1].

1. **현장 확보와 평가.** 증거는 기기뿐 아니라 UICC(SIM 카드) 와 딸린 매체까지 포함하고, 주변기기·케이블·전원 어댑터·액세서리도 챙깁니다 [1]. 이동식 매체나 UICC, 개인 컴퓨터가 기기 자체보다 쓸모 있을 때도 있습니다 [1]. 기기를 잘못 다루면 디지털 데이터를 잃을 수 있고, 기기와 사용자를 잇는 데 지문·DNA 같은 전통적인 감식이 필요할 수도 있습니다 [1]. 설명서·포장·청구서 같은 종이 자료에서도 기기 기능이나 통신사, 계정 정보를 알아낼 수 있습니다 [1]. 액체에 잠기거나 부서진 기기는 기관 절차에 따라 실험실로 보내고, 겉이 부서져도 데이터를 꺼내지 못한다고 단정하지 않습니다 [1].
2. **현장 기록.** 모든 기기를 주변기기·케이블·전원·연결 상태와 함께 사진으로 찍되, 찍으면서 기기를 만지거나 오염시키지 않습니다 [1]. 화면이 보이면 화면도 찍고, 필요하면 시각, 서비스 상태, 배터리 잔량, 떠 있는 아이콘을 손으로 적습니다 [1].
3. **통신 차단 (Isolation).** 많은 기기에 공장 초기화 기능이 있고 원격으로도 실행할 수 있어서, 망과 떼어 놓는 예방 조치가 필요합니다 [1]. 차단 방법과 각각의 단점은 [압수와 보관](mobile-acquisition/seizure-handling.md) 페이지에 있습니다.
4. **포장·운반·보관.** 알맞은 용기에 넣어 봉하고 기관 기준에 따라 표시합니다 [1]. 배터리로 돌아가는 기기를 하루 넘게 두면 전원이 떨어져 데이터를 잃을 위험이 있으니, 곧바로 실험실에 넘기고 전원 문제는 증거 관리자와 상의합니다 [1]. 보관 장소는 서늘하고 건조한 출입 통제 구역이고, 봉인한 용기째 둡니다 [1].
5. **현장 선별 (Triage).** 현장에서 수동 또는 논리 수집을 한 뒤 곧바로 예비 분석을 하는 과정입니다 [1]. 증거가 있을 가능성이 큰 매체, 더 깊이 검사할 사건, 급히 조사할 자료를 이때 가려냅니다 [1].

Android 처럼 암호화를 지원하는 기기가 잠금이 풀린 채 발견되면 가능한 한 현장에서 선별 처리합니다. 화면이 잠기거나 배터리가 떨어지면 데이터를 더는 쓰지 못할 수 있기 때문입니다 [1]. Android 10 이상으로 출시한 기기는 FBE 를 써야 하고, 사용자 인증 뒤에만 쓸 수 있는 저장 영역(Credential Encrypted, CE) 은 사용자가 잠금을 푼 뒤에만 열립니다 [3]. 그래서 켜져 있고 잠금이 풀린 기기를 끄거나 잠기게 두는 판단이 수집 범위를 크게 바꿀 수 있습니다. 암호화 구조는 [저장 공간 암호화](../../01-foundations/storage/encryption/index.md) 페이지를 봅니다.

현장 선별을 할지 말지 정할 때 따지는 항목은 아래와 같습니다 [1]. 기관마다 선별 우선순위를 매기는 점수 방식을 두고 계속 고쳐 갑니다 [1].

| 판단 항목 | 따지는 내용 |
|---|---|
| 기기 상태 | 잠금이 풀려 있고 손상이 없는가 |
| 긴급성 | 사건이 급한가 |
| 거리 | 실험실까지 2시간 안에 갈 수 있는가 |
| 준비 | 현장에 맞는 도구와 교육을 받은 사람이 있는가, 전문가에게 연락할 수 있는가 |
| 전원 | 배터리가 50% 를 넘는가 |
| 필요 | 추가 자료가 필요한가 |

### 2단계: 수집

수집은 기기를 식별하는 데서 시작합니다. 기기 종류와 운영체제에 따라 사본을 만드는 경로와 도구가 정해지기 때문입니다 [1]. 제조사, 모델, 통신사로 식별하고, 알 수 없으면 앞·뒤·옆을 사진으로 찍어 두면 나중에 모델과 당시 상태(화면 잠금 여부 등)를 알아내는 데 도움이 됩니다 [1]. 제조사 라벨을 떼거나 운영체제·앱을 바꿔 정체를 숨긴 기기도 있으니 사례마다 따로 봅니다 [1].

수집 도구를 연결하기 전에는 기기의 지금 상태를 먼저 적어 둡니다. 조사자가 비행기 모드를 켜거나 개발자 옵션을 여는 순간 설정 값에 조사자의 조작이 섞이니, 수집 전 상태를 남겨 두어야 원래 상태와 조사자가 바꾼 부분을 나눌 수 있습니다. adb 일반 셸 권한으로 읽어 기록지에 옮길 만한 칸은 아래와 같습니다(삼성 One UI 8.5 기준). 각 값의 정확한 뜻을 밝힌 공개 자료는 없으니, 이름만 보고 값을 해석하지 않습니다.

| 기록할 것 | 어디서 읽나 | 칸·키 이름 |
|---|---|---|
| 빌드 | `dumpsys package` 의 Database versions 절 | `sdkVersion`, `sdkVersionFull`, `databaseVersion`, `buildFingerprint`, `fingerprint` |
| 사용자와 잠금 상태 | `dumpsys user` | 사용자마다 `State:`(값 예: `RUNNING_UNLOCKED`), `Created:`, `Last logged in:`, `Start time:`, `Unlock time:`, `Last entered foreground:` |
| 통신 상태 | settings global, `dumpsys wifi`, `dumpsys bluetooth_manager` | `airplane_mode_on`, `AirplaneModeOn` 줄, `Wi-Fi is enabled` 줄, `enabled:`·`state: ON` 줄 |
| 디버깅 설정 | settings global | `adb_enabled`, `adb_wifi_enabled`, `development_settings_enabled`, `stay_on_while_plugged_in` |
| 시각 설정 | settings global | `auto_time`, `auto_time_zone` |
| 식별자 | settings secure | `android_id` |
| 원격 잠금·도난 방지·기기 찾기 | settings secure | `remote_lock_setting`, `theft_detection_lock_supported`, `theft_protection_default_on`, `fmm_offline_find_support`, `fmm_community_finding`, `lock_screen_lock_after_timeout` |

`dumpsys user` 에는 주 사용자(`isPrimary=true`) 말고 `isPrimary=false` 이고 `parentId` 가 붙은 두 번째 사용자가 나올 수 있습니다. 사용자가 여럿이면 상태를 사용자마다 따로 적습니다. 여러 사용자와 보안 폴더는 [사용자와 프로필](../../02-artifacts/system-account/users-profiles.md) 과 [보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md) 페이지를 봅니다.

`dumpsys usagestats` 의 이벤트 목록은 `Last ## hour events` 라는 제목 아래 최근 몇 시간 치만 나옵니다. 이런 메모리 쪽 상태는 시간이 지나면 바뀌니 먼저 떠 둡니다.

상태를 적은 뒤에는 사건에 맞는 수집 방식을 고릅니다. 방식별 차이는 [수집 방식 비교](mobile-acquisition/methods.md), adb 를 쓰는 조건과 켤 때 남는 흔적은 [ADB로 볼 수 있는 것](mobile-acquisition/adb.md), 결과물 해시와 수집 날짜·시간대 기록은 [결과물 형식과 해시](mobile-acquisition/formats-hash.md) 페이지에 있습니다. 서버에만 있는 데이터는 [클라우드 데이터](cloud-data.md) 페이지를 봅니다.

### 3단계: 검사와 분석

검사는 숨겨지거나 가려진 것까지 포함해 디지털 증거를 찾아내는 과정이고, 과학적 방법을 써서 데이터의 내용·상태·출처·의미를 빠짐없이 적습니다 [1]. 분석은 검사 결과가 사건에 어떤 의미가 있고 얼마나 증명하는지 따지는 과정이라서, 검사는 전문가가 하지만 분석은 수사관 같은 다른 사람도 할 수 있습니다 [1].

검사는 원본 기기가 아니라 기기에서 수집한 사본으로 시작합니다 [1]. 조사관은 어떤 정보를 찾는지 알려 주고 검사관은 그것을 찾을 수단을 대는데, 찾을 데이터의 종류와 검색어는 사건을 이해하는 데서 나옵니다 [1]. 도구마다 사건 파일 형식이 달라서 수집에 쓴 도구를 검사·분석에도 그대로 쓰는 일이 많습니다 [1].

분석 방법은 [타임라인 작성](../analysis/timeline/index.md), [앱 데이터 분석](../analysis/app-data-analysis/index.md), [콘텐츠 검색](../analysis/content-search.md), [삭제 데이터 복구](../analysis/data-recovery/index.md) 페이지에서 다룹니다.

### 4단계: 보고

보고는 조사에서 한 모든 단계와 결론을 자세히 정리하는 과정이고, 모든 조치와 관찰을 꼼꼼히 적은 기록, 시험 결과, 데이터에서 끌어낸 추론의 설명이 바탕이 됩니다 [1]. 도구가 만든 보고서는 전체 보고서의 일부일 뿐이라서, 최종 보고서의 내용이 도구 화면과 맞는지 반드시 대조합니다 [1]. 도구가 가져오지 못한 데이터를 손으로 확인했다면 그 과정을 영상이나 사진으로 남겨 보고서에 넣을 수 있습니다 [1].

보고서에 넣을 항목은 아래와 같습니다 [1].

| 구분 | 항목 |
|---|---|
| 사건 정보 | 보고 기관, 사건 번호, 담당 수사관, 의뢰자, 증거 접수일, 보고일 |
| 검사 대상 | 검사한 물건 목록(일련번호·제조사·모델) |
| 검사 내용 | 검사자 이름과 서명, 쓴 장비와 설정, 검사 단계 요약 |
| 보조 자료 | 증거 사본, 연계 보관(chain of custody) 기록 |
| 결과 | 발견 내용, 결론 |

발견 내용에는 요청과 관련된 파일, 삭제된 파일, 검색어 결과, 인터넷 관련 증거, 소유를 보여 주는 흔적, 암호화 같은 데이터 숨김 기법 등이 들어갑니다 [1]. 증거와 도구·기법은 법정에서 다툼이 될 수 있으니 처음부터 끝까지 다시 해 볼 수 있을 만큼 기록하고, 직접 만든 도구를 썼다면 그 소프트웨어 사본을 결과와 함께 보관합니다 [1]. 보고서 쓰는 법은 [포렌식 보고서](../reporting/forensic-report.md), 도구 결과를 믿어도 되는지 확인하는 법은 [도구 검증](../reporting/tool-validation.md) 페이지에 있습니다.

## 버전과 제조사에 따른 차이

절차 자체는 버전과 상관없이 같지만, 몇몇 변화가 보존과 수집 단계의 판단을 바꿉니다.

| 버전·제조사 | 달라지는 점 | 자세히 |
|---|---|---|
| Android 10 이상 출시 기기 | FBE 가 필수이고, CE 영역은 사용자가 잠금을 푼 뒤에만 쓸 수 있습니다 [3] | [저장 공간 암호화](../../01-foundations/storage/encryption/index.md) |
| adb 쓰는 기기 전반 | USB 디버깅은 개발자 옵션에서 켜고, 잠금을 푼 상태에서 컴퓨터의 RSA 키를 허용해야 합니다. 무선 디버깅은 Android 11 이상에서 됩니다 [4] | [ADB로 볼 수 있는 것](mobile-acquisition/adb.md) |
| Android 12 이상을 대상으로 만든 앱 | adb backup 에 앱 데이터가 빠지고, 매니페스트에 `android:debuggable=true` 를 둔 앱만 예외입니다 [5] | [백업으로 수집](mobile-acquisition/backups.md) |
| Android 17 기기 | Google Play 서비스 v26.19(2026년 5월)부터 원격 잠금(Remote Lock) 과 도난 감지 잠금(Theft Detection Lock) 이 기본으로 켜집니다 [2] | [압수와 보관](mobile-acquisition/seizure-handling.md) |
| Google Play 서비스 v26.22(2026년 6월) | 기기 초기 설정에 Find Hub 설정이 들어가 원격으로 기기 위치를 찾을 수 있습니다 [2] | [압수와 보관](mobile-acquisition/seizure-handling.md) |
| 삼성 One UI 8.5 | settings secure 에 원격 잠금·도난 방지·기기 찾기와 이름이 닿는 키가 있고, `dumpsys user` 에 두 번째 사용자가 나올 수 있습니다 | [설정 값](../../02-artifacts/system-account/settings.md) |

원격 잠금과 도난 방지 기능이 기본으로 켜지는 흐름은, 원격 공장 초기화에 대비해 통신을 끊는 조치 [1] 와 함께 봐야 합니다. 삼성 One UI 에만 있는 절차상 차이(보안 폴더, Knox 등) 는 이 페이지에서 다루지 않습니다.

## 도구

절차에는 특정 도구가 정해져 있지 않고, 도구마다 사건 파일 형식이 다릅니다 [1]. 수집 전 상태를 적는 `dumpsys` 와 `settings` 출력은 adb 일반 셸 권한으로 읽을 수 있고, 읽는 조건은 [ADB로 볼 수 있는 것](mobile-acquisition/adb.md), 출력 모양은 [dumpsys 출력](../../02-artifacts/logs/dumpsys.md) 과 [설정 값](../../02-artifacts/system-account/settings.md) 페이지를 봅니다. 어떤 도구를 쓰든 결과를 믿기 전에 [도구 검증](../reporting/tool-validation.md) 을 거칩니다.

## 함정과 한계

NIST SP 800-101 Rev.1 은 FBE 이전 문서라서, 켜진 기기를 끄는 판단처럼 Android 10 이후 기기에서 무게가 달라진 부분은 이 문서만으로 정할 수 없습니다. 원격 잠금·도난 방지 기능도 2026년에 새로 기본값이 바뀌고 있어 [2], 기기를 확보한 시점의 Google Play 서비스 버전과 설정을 함께 적어 두어야 나중에 설명할 수 있습니다.

settings 키는 이름만 보고 뜻을 짐작하기 쉽습니다. `remote_lock_setting` 이나 `theft_protection_default_on` 같은 키는 값이 무엇을 뜻하는지 알려져 있지 않으니, 보고서에는 "키가 있고 값이 이러했다" 까지만 씁니다. `android_id` 도 값이 앱별·사용자별로 달라질 수 있으니 [기기 식별자](../../01-foundations/value-decoding/device-identifiers.md) 페이지와 맞춰 본 뒤에 식별자로 씁니다.

`dumpsys` 출력은 읽는 순간의 상태라서 시간이 지나면 같은 명령이라도 다른 값이 나옵니다. 조사자의 연결과 조작도 이 상태를 바꿀 수 있으니, 언제 무엇을 했는지 시각과 함께 적은 기록이 없으면 원래 상태와 조사자가 만든 변화를 나누지 못합니다.

## 결과를 어떻게 해석하나

보존 단계의 사진과 기록, 수집 전 상태 기록, 수집 결과물의 해시가 한 줄로 이어져야 결과물이 그 기기에서 나왔고 그 뒤로 바뀌지 않았다고 말할 수 있습니다. 같은 기기를 두 번 수집하면 결과물 전체의 해시는 달라도 항목별 해시는 대체로 같다는 점은 [결과물 형식과 해시](mobile-acquisition/formats-hash.md) 페이지에 정리했습니다.

보고서에는 기록이 말하는 만큼만 씁니다. 예를 들어 "기기를 확보할 때 잠금이 풀려 있었다" 가 아니라 "수집 직전 `dumpsys user` 의 주 사용자 `State:` 칸 값이 `RUNNING_UNLOCKED` 였고, 이는 조사자가 기기를 조작하기 전 사진 기록의 화면 상태와 맞는다" 처럼 어느 기록에서 무엇을 읽었는지를 적습니다. 도구가 보여 준 결과를 손으로 확인했다면 그 과정의 사진·영상을 함께 붙입니다 [1].

## 참고 문헌

1. NIST SP 800-101 Rev.1, Guidelines on Mobile Device Forensics (Ayers, Brothers, Jansen, 2014). https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-101r1.pdf
2. Google System Services release notes — Google Help. https://support.google.com/product-documentation/answer/14343500?hl=en
3. File-based encryption — Android Open Source Project. https://source.android.com/docs/security/features/encryption/file-based
4. Android Debug Bridge (adb) — Android Developers. https://developer.android.com/tools/adb
5. Behavior changes: apps targeting Android 12 — Android Developers. https://developer.android.com/about/versions/12/behavior-changes-12
