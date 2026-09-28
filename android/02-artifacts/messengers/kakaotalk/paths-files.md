---
title: "저장 위치와 파일"
parent: "카카오톡"
grand_parent: "아티팩트 · 메신저"
nav_order: 910
---

# 저장 위치와 파일 (Paths·Files)

카카오톡은 앱 내부 저장소의 `databases`·`shared_prefs`·`files` 폴더에 대화 DB 와 설정을 두고, 외부 저장소의 앱 전용 캐시 폴더에도 일부 파일을 남기며, 그중 여러 파일은 로그인한 뒤에야 생깁니다.

## 무엇을 기록하나 · 왜 생기나

앱이 쓰는 폴더는 Android 가 앱마다 나눠 주는 내부 저장소와 외부 저장소의 앱 전용 폴더입니다. 폴더 구조의 일반 원리는 [앱 데이터 폴더 구조](../../../01-foundations/storage/app-data-layout.md)에서 다루고, 이 페이지는 카카오톡이 그 안에 무엇을 만드는지만 적습니다.

아래 폴더와 파일 목록은 카카오톡 10.1.7 기준입니다[3]. 요청 헤더에 Android 11 과 `sdk_gphone_arm64`, `X-osv=30` 이 들어 있어 Android 11(API 30) 에뮬레이터 환경으로 보입니다. 설치 직후와 로그인 뒤의 파일을 비교하면 어떤 파일이 로그인과 함께 생기는지 알 수 있습니다[2].

## 위치와 버전별 차이

| 폴더 | 경로 (10.1.7 기준) |
|---|---|
| 앱 내부 저장소 | `/data/user/0/com.kakao.talk/` (`/data/data/com.kakao.talk/` 와 같음) |
| 캐시 | `/data/user/0/com.kakao.talk/cache` |
| 코드 캐시 | `/data/user/0/com.kakao.talk/code_cache` |
| 파일 | `/data/user/0/com.kakao.talk/files` |
| DB | `/data/user/0/com.kakao.talk/databases` |
| 외부 캐시 | `/storage/emulated/0/Android/data/com.kakao.talk/cache` |
| OBB | `/storage/emulated/0/Android/obb/com.kakao.talk` |
| 설치 파일 | `/data/app/com.kakao.talk-(무작위 문자열)==/base.apk` |

위 경로는 한 앱 버전, 에뮬레이터 기준입니다. 다른 앱 버전, 다른 Android 버전, 삼성 One UI 기기에서는 경로가 다를 수 있어 실제 기기에서 확인합니다. `/sdcard` 쪽에서 `Android/data/com.kakao.talk/cache` 말고 어떤 폴더를 쓰는지는 공용 저장 공간에서 이름에 `com.kakao.talk` 이 들어간 폴더를 찾아 확인합니다. Android 11 이후 다른 앱이나 adb 가 `Android/data` 아래를 어디까지 읽을 수 있는지는 [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md)에서 다룹니다.

## 구조

### databases 폴더

10.1.7 의 DB 와 설치 직후·로그인 뒤 차이는 다음과 같습니다[2][3].

| 파일 | 설치 직후 | 로그인 뒤 | 비고 |
|---|---|---|---|
| `KakaoTalk.db` | 있음 | `-wal`·`-shm` 이 바뀜 | 대화 기록. [대화 DB 구조와 암호화](chat-db.md) |
| `KakaoTalk2.db` | 없음 | 생김 | 친구 목록. [계정과 친구 목록](account-friends.md) |
| `calendar_database` | 없음 | 생김 | |
| `crypto_database` | 없음 | 생김 | 암호 걸림 |
| `kakao_talk_pass.db` | 없음 | 생김 | |
| `multi_profile_database.db` | 없음 | 생김 | |
| `com.google.android.datatransport.events` | 비교 기록에 없음 | 비교 기록에 없음 | 10.1.7 목록에만 있음 |
| `google_app_measurement_local.db` | 비교 기록에 없음 | 비교 기록에 없음 | 10.1.7 목록에만 있음 |

로그인 뒤에 생긴 DB 옆에는 각각 `-shm`·`-wal` 파일이 함께 생깁니다. DB 를 WAL 방식으로 쓰기 때문에 최근 기록이 본 파일이 아니라 `-wal` 파일에만 남아 있을 수 있고, WAL 의 구조는 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md)에서 설명합니다.

`crypto_database` 는 Android 키 저장소(KeyStore)의 키로 암호화돼 있어, 파일만으로는 내용을 열 수 없습니다[3]. 키 저장소의 다른 키는 `shared_prefs/zzng.xml` 안의 값을 암호화하는 데 쓰입니다[3].

### shared_prefs 폴더

10.1.7 에는 설정 파일이 30여 개 있고[3], 그 가운데 몇 가지는 다음과 같습니다. 형식은 [설정 XML과 SharedPreferences](../../../01-foundations/data-formats/shared-preferences.md)에서 다룹니다.

```
KakaoTalk.profile.preferences.xml       (로그인 뒤 생김)
KakaoTalk.multiprofile.preferences.xml  (로그인 뒤 생김)
KakaoTalk.fcm.xml                       (로그인 뒤 생김)
zzng.xml                                (로그인 뒤 생김)
KakaoTalk.locoLog.xml
KakaoTalk.notification.channel_revision.xml
KakaoTalk.plusfriend.preference.xml
KakaoTalk.search.preferences.xml
KakaoTalk.vox.perferences.xml
kakao.talk.openlink.preferences.xml
kakaotalk.cache.xml
talk_pass_preferences.xml
```

`KakaoTalk.vox.perferences.xml` 처럼 일부 파일 이름은 원래부터 "perferences" 로 철자가 틀려 있어서, 이름으로 검색할 때는 틀린 철자도 함께 넣어야 합니다. OAuth 토큰 같은 일부 값은 앱에 들어 있는 고정 키로 암호화돼 있어 XML 을 열어도 그대로 읽히지 않습니다[3]. 각 파일 안의 키 이름은 XML 을 직접 열어 확인하고, 키의 뜻은 이름만 보고 단정하지 않습니다.

### 그 밖의 폴더

| 위치 | 파일 | 설치 직후와 로그인 뒤 |
|---|---|---|
| `files/datastore/` | `LocalUser_DataStore.pref.preferences_pb` | 설치 직후 있고 로그인 뒤 바뀜 |
| `files/datastore/` | `Feature_DataStore.pref.preferences_pb` | 설치 직후 있고 로그인 뒤 바뀜 |
| `no_backup/` | `kakaoi.json`, `androidx.work.workdb-shm` | 설치 직후 있고 로그인 뒤 바뀜 |
| `app_webview/` | `Web Data`, `GPUCache` 등 | 로그인 뒤 생김 (`Cookies` 는 설치 직후 있고 로그인 뒤 바뀜) |
| `cache/` | `keywordEffects`, `WebView` | 로그인 뒤 생김 |
| `cache/media/` | 16진수 이름의 `.uid` 파일 | 설치 직후와 로그인 뒤 각각 생김 |
| 외부 캐시 | `MiniProfile`, `default`, `journal` | 로그인 뒤 생김 |

`.preferences_pb` 파일은 이름으로 보면 프로토콜 버퍼 형식으로 보이고, 형식은 [프로토콜 버퍼 (Protocol Buffers)](../../../01-foundations/data-formats/protobuf.md)에서 다룹니다. 외부 캐시 폴더는 비교 기록에서 `external_cache/com.kakao.talk/cache` 로 적혀 있고, 경로로 옮기면 `/storage/emulated/0/Android/data/com.kakao.talk/cache` 입니다.

## 증거로서 의미

**증명하는 것.** `KakaoTalk2.db`, `KakaoTalk.profile.preferences.xml`, `zzng.xml` 같은 파일은 10.1.7 에서 로그인한 뒤에만 생깁니다[2]. 그래서 이 파일들이 있으면 그 기기에서 카카오톡에 로그인한 적이 있다고 볼 근거가 하나 생깁니다.

**증명하지 못하는 것.** 파일이 있다는 사실만으로는 누가 언제 로그인했는지, 지금도 로그인 상태인지 알 수 없습니다. 이 차이는 한 버전 기준이라, 다른 버전에서도 같은 파일이 로그인과 함께 생기는지는 따로 확인해야 합니다.

## 함정과 한계

본 DB 파일만 꺼내면 `-wal` 에만 있는 최근 기록을 놓치므로 `-wal`, `-shm`, `-journal` 을 함께 확보합니다. CARPE 도 `KakaoTalk.db`·`KakaoTalk2.db` 를 꺼낼 때 이 세 파일을 함께 꺼냅니다.

폴더 목록은 카카오톡 10.1.7 한 버전 기준이라서, 요즘 버전에서는 파일 이름이 바뀌었거나 새 파일이 생겼을 수 있습니다. 목록에 없는 파일을 만나면 없는 것으로 넘기지 말고 새로 기록해 둡니다.

## 직접 분석해 보기

확보한 이미지나 앱 폴더 사본에서 먼저 `databases` 폴더를 열어 본 DB 와 `-wal`·`-shm` 이 함께 있는지, 위 표에서 로그인 뒤에 생기는 파일이 있는지 봅니다. 공개 도구 가운데 CARPE 는 이미지 안의 `root/data/com.kakao.talk/databases` 경로에서 이름이 `Kakaotalk.db` 또는 `Kakaotalk2.db` 인 파일을 대소문자 구분 없이 찾습니다. 도구가 이 경로와 이름으로만 찾으니, 확보 방식에 따라 폴더 경로가 다르면 도구가 파일을 놓칠 수 있습니다.

## 교차 검증

- [설치된 앱 (packages.xml)](../../app-usage/packages/index.md) — 앱이 언제 설치됐는지 보고, 앱 폴더의 파일이 생긴 시점과 맞춰 봅니다.
- [앱 사용 기록 (usagestats)](../../app-usage/usagestats/index.md) — 앱을 실제로 쓴 시간대를 확인합니다.
- [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md) — 앱 내부 저장소를 어떤 방법으로 확보할 수 있는지 다룹니다.

## 실습

카카오톡이 설치된 공개 시험 자료나 직접 만든 시험 기기 이미지로 다음 질문을 풀어 봅니다.

1. `databases` 폴더에 어떤 DB 가 있고, 각 DB 옆에 `-wal`·`-shm` 파일이 있습니까?
2. 위 표에서 로그인 뒤에 생기는 파일 가운데 무엇이 있습니까? 없다면 그 기기에서 로그인하지 않았다고 볼 수 있습니까, 아니면 앱 버전이 달라서입니까?
3. 표에 없는 파일이나 폴더가 있습니까? 있다면 앱 버전과 함께 적어 둡니다.

## 참고 문헌

1. dfrc-korea/carpe — modules/kakaotalk_mobile_decrypt_connector.py. https://github.com/dfrc-korea/carpe/blob/HEAD/modules/kakaotalk_mobile_decrypt_connector.py
2. stulle123/kakaotalk_analysis — recon/file_diff_before_and_after_login.txt (설치 직후와 로그인 뒤 파일 비교). https://github.com/stulle123/kakaotalk_analysis/blob/HEAD/recon/file_diff_before_and_after_login.txt
3. stulle123/kakaotalk_analysis — doc/RECON.md (카카오톡 10.1.7 조사 기록). https://github.com/stulle123/kakaotalk_analysis/blob/HEAD/doc/RECON.md
