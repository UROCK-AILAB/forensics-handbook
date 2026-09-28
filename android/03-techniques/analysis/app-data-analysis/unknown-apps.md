---
title: "처음 보는 앱 분석 순서"
parent: "앱 데이터 분석"
grand_parent: "기법 · 분석"
nav_order: 1380
---

# 처음 보는 앱 분석 순서 (Unknown Apps)

분석 도구가 해석해 주지 않는 앱을 만났을 때, 설치 기록으로 정체를 먼저 확인하고 매니페스트 속성과 앱 폴더의 파일 형식을 차례로 살핀 뒤 다른 시스템 기록과 맞춰 보는 순서입니다.

## 언제 쓰나

공개 도구에 전용 모듈이 없는 앱을 만났을 때 씁니다. 기기 한 대에도 시스템 앱이 수백 개, 사용자가 설치한 앱이 백 개 넘게 있을 수 있고(한 기기에서 각각 486개, 168개), 도구에 앱별 모듈이 없으면 분석가가 앱 폴더를 직접 열어 봐야 합니다. 이 페이지는 그런 앱 하나를 처음부터 따라가는 순서를 다룹니다. 캐시와 WebView 폴더는 [캐시와 웹뷰](cache-webview.md), 이미 지운 앱은 [지운 앱이 남긴 흔적](uninstalled-apps.md) 페이지에서 따로 다룹니다.

## 절차

1. **설치 기록으로 정체를 확인합니다.** 먼저 패키지 이름이 기기의 설치 기록에 있는지, 언제 설치·갱신됐는지, 무엇이 설치했는지를 봅니다. 공개 도구 ALEAPP 의 packageInfo 모듈은 `*/system/packages.xml` 을 읽어 `<package>` 요소의 `name`, `ft`, `it`, `ut`, `installOriginator`, `installer`, `codePath`, `publicFlags`, `privateFlags` 속성을 뽑고, `it` 를 설치 시각(Install Time), `ut` 를 갱신 시각(Update Time)으로 보여 줍니다 [2]. 이 도구는 `ft` 를 포함한 세 시각 속성을 모두 16진수 문자열로 적힌 유닉스 밀리초로 보고 UTC 로 바꾸며 [2], 밀리초 값을 옮기는 공식은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다. `ft` 의 뜻과 두 플래그 속성의 비트 뜻은 AOSP 소스에서 따로 확인합니다. 파일이 일반 XML 이 아니라 바이너리 XML 일 수 있어서 ALEAPP 도 먼저 형식을 검사한 뒤 읽고 [2], 형식 설명은 [안드로이드 바이너리 XML (ABX)](../../../01-foundations/data-formats/abx.md), 이 기록 자체의 해석은 [설치된 앱 (packages.xml)](../../../02-artifacts/app-usage/packages/index.md) 페이지에 있습니다.

2. **켜져 있는 기기라면 dumpsys package 로 한 번 더 봅니다.** `dumpsys package` 출력은 매우 길고(한 기기에서 약 192,000줄), 맨 앞의 "Database versions:" 절 뒤에 역할별 담당 패키지를 적은 "Known Packages:" 절과 공유 라이브러리를 `이름 -> (so|jar) 경로` 모양으로 적은 "Libraries:" 절이 이어집니다. "Known Packages:" 절의 값 가운데 설치 경로를 판별하는 데 쓸 만한 것은 아래와 같습니다.

   | 역할 | 패키지(한 기기의 예) |
   |---|---|
   | Installer | `com.google.android.packageinstaller` |
   | Uninstaller | (비어 있음) |
   | Verifier | `com.android.vending`, `com.samsung.android.sm.devicesecurity` |
   | Permission Controller | `com.google.android.permissioncontroller` |
   | Browser | `com.android.chrome` |

   1단계에서 얻은 `installer` 값을 이 표의 역할과 비교해 보면, 그 앱이 스토어를 거쳤는지 기기의 설치 관리자를 거쳤는지 추정할 단서가 됩니다. 패키지별 절에서 설치 시각 같은 필드의 이름은 출력에서 직접 찾아 확인하고, dumpsys 출력 전반은 [dumpsys 출력](../../../02-artifacts/logs/dumpsys.md) 페이지를 봅니다.

3. **APK 의 매니페스트 속성을 읽습니다.** 매니페스트의 `<application>` 요소에는 데이터가 어디로 복사될 수 있는지, 통신을 어떻게 하는지 알려 주는 속성이 있습니다 [3].

   | 속성 | 기본값 | 분석에서 보는 점 |
   |---|---|---|
   | `android:allowBackup` | `"true"` | `"false"` 면 백업·복원이 일어나지 않고 클라우드 백업과 기기 간 이전(D2D)도 막힙니다. Android 12(API 31) 이상을 대상으로 하는 앱은 일부 제조사 기기에서 D2D 이전을 끌 수 없습니다 |
   | `android:dataExtractionRules` | 없음 | 백업·이전 때 복사할 파일·폴더 규칙을 적은 XML 을 가리킵니다 |
   | `android:fullBackupContent` | 없음 | 자동 백업(Auto Backup) 규칙 XML 이고, 지정하지 않으면 자동 백업이 앱 파일 대부분을 담습니다 |
   | `android:usesCleartextTraffic` | API 27 이하 대상 `"true"`, API 28 이상 대상 `"false"` | 암호화하지 않은 통신을 허용하는지 봅니다 |
   | `android:requestLegacyExternalStorage` | 없음 | 범위 지정 저장소(scoped storage)에서 빠지겠다는 요청이고, 시스템이 받아들이지 않을 수도 있습니다 |
   | `android:debuggable` | `"false"` | 디버그용으로 빌드한 앱인지 봅니다 |
   | `android:hasFragileUserData` | `"false"` | 앱을 지울 때 데이터를 남길지 묻는 창과 관련 있고, [지운 앱이 남긴 흔적](uninstalled-apps.md) 에서 다룹니다 |

   백업이 허용된 앱이면 기기 밖에도 사본이 있을 수 있어서 [구글 백업 (Google Backup)](../../../02-artifacts/mail-cloud/google-backup.md) 쪽도 확인 대상에 넣습니다. 매니페스트와 서명을 읽는 법은 [APK 정보 (AndroidManifest·서명)](../../../02-artifacts/embedded-metadata/apk.md) 페이지에 있습니다.

4. **앱 폴더의 윤곽을 잡습니다.** 앱은 일반 파일을 `filesDir`, 캐시를 `cacheDir`, 따로 만든 하위 폴더를 `getDir()` 로 얻은 곳에 두고, 외부 저장소에는 `getExternalFilesDir()` 로 얻은 앱 전용 폴더를 씁니다 [1]. 이 폴더들의 성격과 Android 버전별 차이는 허브 [앱 데이터 분석](index.md) 의 표에 정리했고, 실제 경로 배치는 [앱 데이터 폴더 구조 (/data/data·/data/user)](../../../01-foundations/storage/app-data-layout.md) 페이지에 있습니다. 공용 저장소도 함께 봅니다. `/sdcard/Android` 아래에는 `data`, `media`, `obb` 세 폴더가 있고, `media` 아래에는 `com.google.android.gms`, `com.samsung.android.spay` 처럼 패키지 이름으로 된 폴더가 생깁니다. 공용 저장소 구조는 [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md) 페이지를 봅니다.

5. **파일 형식을 판별합니다.** 앱 폴더의 파일은 SQLite, 설정 XML, 프로토콜 버퍼, LevelDB 처럼 형식이 정해진 것이 많아서 형식부터 판별하면 읽을 방법이 정해집니다. SQLite 는 본 파일 옆에 `-wal`, `-journal` 같은 부속 파일이 붙고, ALEAPP 도 `library.db*`, `frosting.db*`, `History*` 처럼 별표 패턴으로 부속 파일까지 함께 찾습니다 [4][5][6]. 파일을 옮기거나 내보낼 때도 부속 파일을 같이 확보하고, 부속 파일의 역할은 SQLite 페이지를 봅니다. 형식별 읽는 법은 아래 페이지에 있습니다.

   | 형식 | 읽는 법 |
   |---|---|
   | SQLite 와 부속 파일 | [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) |
   | 설정 XML | [설정 XML과 SharedPreferences](../../../01-foundations/data-formats/shared-preferences.md) |
   | 프로토콜 버퍼 | [프로토콜 버퍼 (Protocol Buffers)](../../../01-foundations/data-formats/protobuf.md) |
   | LevelDB·IndexedDB | [LevelDB와 IndexedDB](../../../01-foundations/data-formats/leveldb-indexeddb.md) |

   ALEAPP 에는 Realm 저장소(`realmUndecodedStores.py`), MMKV(`mmkvCarved.py`), 프로토콜 버퍼(`sharedProto.py`), SQLite WAL 문자열(`walStrings.py`)을 다루는 모듈이 따로 있어서 [7], 형식은 알지만 앱 전용 모듈이 없을 때 참고할 수 있습니다.

6. **캐시와 WebView 폴더를 따로 봅니다.** 앱이 받은 콘텐츠나 앱 안에서 연 웹 페이지 흔적은 캐시와 WebView 폴더에 남을 수 있고, 이 부분은 [캐시와 웹뷰](cache-webview.md) 에서 다룹니다.

7. **시스템 기록과 맞춰 봅니다.** 앱 폴더 안의 기록은 앱이 스스로 적은 것이라서, 시스템이 적은 기록과 맞춰 봐야 믿을 수 있습니다. 앱을 언제 썼는지는 [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md), 알림은 [알림 기록 (Notification History)](../../../02-artifacts/app-usage/notification-history.md), 통신량은 [데이터 사용량 (netstats)](../../../02-artifacts/network/netstats.md), 오류로 멈춘 기록은 [앱 오류·종료 기록 (DropBox·tombstones·ANR)](../../../02-artifacts/app-usage/crash-records.md), 권한은 [앱 샌드박스와 권한 (Sandbox·Permissions)](../../../01-foundations/security-model/sandbox-permissions.md) 페이지에서 확인합니다. 여러 기록을 한 시간 축에 올리는 방법은 [타임라인 작성 (Timeline)](../timeline/index.md) 에 있습니다.

## 도구

ALEAPP 의 `scripts/artifacts` 폴더에는 앱별 모듈과 함께 `packageInfo.py`, `packageRestrictions.py`, `packageUserStates.py`, `installSessions.py`, `appops.py`, `runtimePerms.py`, `recentactivity.py`, `usagestats.py` 같은 시스템 모듈이 있습니다 [7]. 처음 보는 앱이라도 이런 시스템 모듈의 결과에서 패키지 이름으로 걸러 보면 앱 전용 모듈 없이 설치·권한·사용 흔적을 모을 수 있습니다. 각 모듈이 어떤 경로를 어떻게 읽는지는 모듈 코드에서 확인합니다. ALEAPP 는 packageInfo 결과를 "Installed Apps" 분류로 묶고, Magisk 미러 경로(`sbin/.magisk/mirror/...`)에 있는 packages.xml 은 중복으로 보고 건너뜁니다 [2].

도구는 결과를 빨리 모으는 데 쓰고, 처음 보는 앱의 해석은 원본 파일을 직접 열어 확인합니다. 도구 결과를 검증하는 방법은 [도구 검증](../../reporting/tool-validation.md) 페이지에 있습니다.

## 함정과 한계

packages.xml 이 일반 XML 도 바이너리 XML 도 아닌 경우가 있고(암호화됐거나 일부만 복구된 경우 등), 이때 ALEAPP 는 읽기 실패를 기록하고 넘어갑니다 [2]. 도구 결과에 설치 기록이 비어 있으면 앱이 없었다고 보기 전에 파일 상태부터 확인합니다.

Android 버전에 따라 앱 전용 저장소의 암호화와 접근 범위가 달라집니다(허브 [앱 데이터 분석](index.md) 의 표). 확보한 자료에 앱 폴더가 없으면 수집 방식이 그 영역에 닿지 못한 것인지부터 확인하고, 수집 방식별 범위는 [모바일 증거 확보 (Acquisition)](../../acquisition/mobile-acquisition/index.md), 암호화는 [저장 공간 암호화 (Encryption)](../../../01-foundations/storage/encryption/index.md) 페이지를 봅니다.

`settings global` 에는 `default_install_location`, `set_install_location`, `package_verifier_user_consent`, `verifier_timeout_samsung` 같은 키가, `settings secure` 에는 `install_non_market_apps`, `appprotection_permission_function_install_auto_scan_agreed` 같은 키가 있을 수 있습니다. 이름만 보면 설치 경로와 검증에 관련된 키로 보이지만 값의 뜻은 단정할 수 없어서, 뜻을 확인하기 전에는 판단 근거로 쓰지 않습니다. 설정 값을 읽는 법은 [설정 값 (Settings Global·Secure·System)](../../../02-artifacts/system-account/settings.md) 페이지에 있습니다.

앱 폴더의 하위 폴더 이름과 파일 이름은 앱이 정해서, 이름만 보고 내용을 짐작하지 않습니다. 앱 판이 바뀌면 DB 구조도 바뀔 수 있어서, 분석한 앱의 버전을 함께 적어 둡니다.

## 결과를 어떻게 해석하나

packages.xml 의 항목은 그 파일을 확보한 시점에 해당 패키지가 설치 기록에 있었다는 뜻이고, 사용자가 앱을 열어 썼다는 뜻은 아닙니다. `installer` 속성은 설치를 맡은 패키지로 기록된 이름이고, 사람이 누구였는지는 이 값으로 알 수 없습니다. 앱 폴더의 DB 내용은 앱이 적은 기록이라서 시스템 기록과 시각이 맞는지 확인한 만큼만 씁니다.

> packages.xml 에 `(패키지 이름)` 항목이 있고, 설치 시각(`it`)은 (시각) UTC, 설치 주체(`installer`)는 `(패키지 이름)` 으로 기록돼 있습니다. 같은 시간대의 앱 사용 기록에 이 패키지의 이벤트가 (건수) 건 있습니다.

보고서 전체의 틀은 [포렌식 보고서 (Forensic Report)](../../reporting/forensic-report.md) 페이지에 있습니다.

## 참고 문헌

1. Access app-specific files — Android Developers, https://developer.android.com/training/data-storage/app-specific
2. ALEAPP packageInfo.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/packageInfo.py
3. `<application>` 매니페스트 요소 — Android Developers, https://developer.android.com/guide/topics/manifest/application-element
4. ALEAPP frosting.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/frosting.py
5. ALEAPP installedappsLibrary.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/installedappsLibrary.py
6. ALEAPP chrome.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chrome.py
7. ALEAPP scripts/artifacts 폴더 목록(GitHub API) — https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
