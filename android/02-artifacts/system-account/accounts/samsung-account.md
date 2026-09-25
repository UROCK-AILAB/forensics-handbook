---
title: "삼성 계정 흔적"
parent: "계정"
grand_parent: "아티팩트 · 시스템·계정"
nav_order: 350
---

# 삼성 계정 흔적 (Samsung Account)

삼성 기기에서 삼성 계정과 관련해 시스템 쪽에 남는 흔적을 정리합니다. 계정 DB 의 표 구조는 [계정 DB 구조 (accounts_ce.db·accounts_de.db)](accounts-db.md) 에, 계정별 동기화 파일은 [구글 계정 흔적 (Google Account)](google-account.md) 에 있고, 이 페이지는 삼성 기기에서만 볼 수 있는 설정 키를 다룹니다.

## 한 줄 요약

삼성 계정도 AccountManager 에 등록하는 계정이라 AOSP 구조대로라면 계정 DB 의 `accounts` 표에 name·type 쌍으로 남고, 삼성 기기의 설정에는 삼성 계정·약관 동의·기기 이전과 관련된 이름의 키가 따로 남습니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

AccountManager 는 계정을 이름과 종류(type)의 쌍으로 구분하고 type 은 그 계정을 관리하는 인증기를 가리킵니다 [2]. 삼성 계정 앱의 패키지 이름과 type 이 `com.osp.app.signin` 이라는 이야기는 널리 알려져 있지만, 이 값을 밝힌 제조사 문서나 도구 문서는 공개되어 있지 않습니다. 그래서 삼성 계정 행을 가릴 때는 실물 DB 의 type 값과 설치된 앱 목록을 함께 보고 판단한 근거를 보고서에 적습니다.

라이브 기기의 `dumpsys account` 출력에는 type 이 패키지 이름 모양인 계정 줄과 그렇지 않은 줄이 섞여 나옵니다. 어느 줄이 삼성 계정인지는 type 값을 설치된 앱 목록과 맞춰 가립니다. 출력 모양은 [계정 DB 구조](accounts-db.md) 페이지의 dumpsys 절에 있습니다.

## 위치와 확인 상태

| 위치 | 담긴 것 | 비고 |
|---|---|---|
| `accounts_de.db`·`accounts_ce.db` | 계정 이름·종류 | AOSP 구조로 본 추정, 검체에서 확인 [1] |
| `/data/system/sync/` | 계정·동기화 대상별 설정 | 구조는 [구글 계정 흔적](google-account.md) 참고 |
| `settings` global·system·secure | 삼성 계정·동의·기기 이전 관련 키 | 키 이름만 알려짐, 값의 뜻은 검체에서 확인 |
| `/sdcard/Android/media/com.samsung.android.spay/` | 삼성 월렛·페이 앱 폴더 | 공용 저장 공간에 폴더가 생김 |
| 삼성 계정 앱 내부 폴더 | DB·설정 파일 | 공개 자료 없음 |
| 삼성 클라우드, 내 디바이스 찾기(SmartThings Find) 연동 | 연동 흔적 | 공개 자료 없음 |

## 구조 — 설정 키

Android 16 삼성 기기의 `settings` 세 영역에는 아래 이름의 키가 있습니다. 각 키가 무엇을 뜻하는지, 삼성 계정 가입과 어떤 관계인지는 공개된 자료가 없어 검체의 값으로 판단합니다.

| 영역 | 키 | 이름에 드러난 주제 |
|---|---|---|
| global | `first_launch_samsung_account_menu` | 삼성 계정 메뉴 |
| system | `samsung_eula_agree`, `samsung_eula_agree_hqm`, `samsung_pp_agree`, `samsung_errorlog_agree` | 약관·개인정보·오류 기록 동의 |
| secure | `fingerprint_samsungaccount_confirmed`, `fingerprint_used_samsungaccount` | 지문과 삼성 계정 |
| global | `dbsc_consent_tnc_agree_date`, `dbsc_consent_personal_ad_agree_date`, `dbsc_consent_customized_service_agree_date` (같은 머리의 `*_value` 키와 `dbsc_consent_tnc_country` 도 있음) | 동의 날짜 |
| global | `smartswitch_transfer_completed`, `smartswitch_transfer_start_in_oobe`, `quick_start_source_manufacturer` (같은 머리의 키가 몇 개 더 있음) | 기기 이전(Smart Switch)·빠른 시작 |

`fingerprint_*` 두 키는 지문으로 삼성 계정을 확인하는 기능과 관련된 설정으로 보입니다. 기기 이전 쪽 키는 계정이 처음 등록된 무렵을 해석할 때 참고할 수 있지만, 두 쪽 모두 뜻을 밝힌 공개 자료는 없습니다. 설정 값을 읽는 법과 세 영역의 차이는 [설정 값 (Settings Global·Secure·System)](../settings.md) 페이지에 있습니다.

## 증거로서 의미

| 기록 | 증명하는 것 | 증명하지 못하는 것 |
|---|---|---|
| 계정 DB 의 삼성 계정 행(찾은 경우) | 확보 시점에 그 사용자 공간에 이 계정이 등록되어 있었다는 것 | 언제 가입·추가했는지, 누가 썼는지 |
| 삼성 관련 설정 키 | 그 키가 설정에 있다는 것 | 사용자가 동의했다는 것, 삼성 계정에 로그인했다는 것 |
| `dbsc_consent_*_date` 값 | 그 칸에 날짜 값이 들어 있다는 것 | 무엇에 동의한 날짜인지(삼성 계정과의 관계는 알려져 있지 않음) |
| `com.samsung.android.spay` 폴더 | 이 앱이 공용 저장 공간에 폴더를 만들었다는 것 | 결제·카드 등록 여부, 계정 로그인 여부 |

보고서에는 "설정에 삼성 계정 관련 이름의 키가 있다" 까지만 쓰고, 키 이름만으로 "삼성 계정에 로그인했다" 고 쓰지 않습니다.

## 시각 해석

계정 DB 의 시각 칸과 변경 기록 시각은 [계정 DB 구조](accounts-db.md) 페이지의 "시각 해석" 절을 따릅니다. `dbsc_consent_*_date` 키의 값 형식(유닉스 밀리초인지 날짜 문자열인지)과 시간대는 알려져 있지 않으니, 실물 값을 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../../01-foundations/value-decoding/time-values.md) 페이지의 방법으로 여러 형식에 넣어 보고 다른 기록의 시각과 맞는 쪽을 고릅니다.

## 함정과 한계

`com.osp.app.signin` 같은 널리 알려진 값을 확인 없이 필터로 쓰면, 값이 다를 때 삼성 계정 행을 통째로 놓칩니다. 삼성 계정 앱 내부 파일과 삼성 클라우드 연동 흔적은 이 페이지에서 다루지 않으니, 이 페이지에 없다고 해서 그 기록이 기기에 없다고 보지 않습니다.

설정 키는 이름으로 뜻을 짐작할 수 있을 뿐 값과 쓰임이 알려져 있지 않아서, 키 하나로 결론을 내지 않고 계정 DB·설치된 앱·앱 사용 기록과 함께 봅니다. 시각이 이 기기의 사용 기간보다 앞서는 기록이 나오면 다른 기기에서 옮겨 온 데이터일 가능성도 함께 따져 봅니다.

## 직접 분석해 보기

계정 DB 를 헥스와 `sqlite3` 로 읽는 법은 [계정 DB 구조](accounts-db.md) 페이지에 있습니다. 삼성 계정을 찾을 때도 type 을 미리 정해 거르지 않고 전체를 먼저 봅니다.

```sql
SELECT _id, name, type FROM accounts ORDER BY type, name;
```

그다음 각 type 값이 설치된 앱 가운데 어느 패키지와 맞는지 [설치된 앱 (packages.xml)](../../app-usage/packages/index.md) 에서 확인합니다. 설정 키는 위 표의 이름으로 세 영역을 검색해 있는지와 값을 적습니다.

## 교차 검증

삼성 클라우드와 삼성 앱의 데이터는 [삼성 클라우드와 원드라이브 (Samsung Cloud·OneDrive)](../../mail-cloud/samsung-cloud-onedrive.md), [저장된 암호 (Google 비밀번호 관리자·Samsung Pass)](../../credentials-security/saved-passwords.md), [삼성 헬스 (Samsung Health)](../../samsung/samsung-health.md), [삼성 갤러리 (Samsung Gallery)](../../media/samsung-gallery.md) 에서 보고, 삼성 기기의 보안 구조는 [삼성 녹스 (Samsung Knox)](../../../01-foundations/security-model/samsung-knox.md) 와 [보안 폴더와 작업 프로필 (Secure Folder·Work Profile)](../../../01-foundations/security-model/secure-folder-work-profile.md) 에서 봅니다. `/sdcard/Android/media/` 아래 앱 폴더의 성격은 [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md) 페이지에 있습니다.

## 실습

삼성 기기에서 만든 공개 검체(NIST CFReDS 에 올라온 모바일 이미지 등)를 구해 다음을 풀어 봅니다.

1. 계정 DB 의 type 을 모두 뽑고, 설치된 앱 목록과 맞춰 삼성 계정으로 판단한 행과 그 근거를 적어 봅니다.
2. 위 표의 설정 키가 검체에 있는지 찾고, 값이 어떤 모양인지(숫자·날짜·참거짓) 적어 봅니다.
3. `dbsc_consent_*_date` 값이 있다면 시각 형식을 추정해 날짜로 바꾸고, 계정 DB 변경 기록의 시각과 가까운지 비교합니다.

## 참고 문헌

1. AccountsDb.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/accounts/AccountsDb.java
2. AccountManager — Android Developers API 참조, https://developer.android.com/reference/android/accounts/AccountManager
