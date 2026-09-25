---
title: "앱 데이터 분석"
parent: "기법 · 분석"
nav_order: 1370
has_children: true
has_toc: false
---

# 앱 데이터 분석 (App Data Analysis)

## 한 줄 요약

앱이 자기 전용 저장소와 공용 저장소에 남긴 파일을 찾아 형식을 가리고 읽는 방법을 모은 묶음이고, 처음 보는 앱·캐시와 WebView·지운 앱 세 갈래로 나눠 다룹니다.

## 왜 중요한가

Android 기기에서 대화·사진·방문 기록 같은 사용자 행위는 앱이 자기 폴더에 적은 파일에 남는 경우가 많습니다. 널리 쓰이는 앱은 이 핸드북 아티팩트 사전의 앱별 페이지와 공개 도구의 전용 모듈로 읽을 수 있지만, 전용 모듈이 없는 앱은 분석가가 폴더를 직접 열어야 합니다. 앱 폴더의 파일은 앱이 정한 방식으로 적히고 앱을 지우면 함께 사라지기도 해서, 어디에 무엇이 남고 언제 지워지는지부터 알아야 해석을 시작할 수 있습니다.

## 한눈에 보기

앱이 파일을 두는 곳은 Android 가 정한 API 로 얻고, 공식 문서가 밝힌 성격은 아래와 같습니다 [1]. 실제 절대 경로 배치는 [앱 데이터 폴더 구조 (/data/data·/data/user)](../../../01-foundations/storage/app-data-layout.md) 페이지에 있습니다.

| 위치 | Android 버전별 차이 | 알려 주는 것 |
|---|---|---|
| `filesDir` (`openFileOutput()` 도 여기에 씀) | Android 10(API 29) 이상에서 앱 전용 내부 저장소가 암호화됨 | 앱의 일반 파일과 DB. 읽는 순서는 [처음 보는 앱 분석 순서](unknown-apps.md) |
| `cacheDir` | 버전 차이는 확인하지 못함. 저장 공간이 부족하면 시스템이 지울 수 있음 | 앱이 받아 온 콘텐츠. [캐시와 웹뷰](cache-webview.md) |
| `getDir(이름, MODE_PRIVATE)` 로 만든 하위 폴더 | 버전 차이는 확인하지 못함. `ApplicationInfo.dataDir` 가 늘 조상 폴더 | 앱이 따로 나눈 데이터 |
| `getExternalFilesDir()`, `externalCacheDir` (외부 저장소의 앱 전용 폴더) | Android 4.4(API 19)부터 저장소 권한 없이 쓸 수 있음. Android 11(API 30) 이상에서는 앱이 외부 저장소에 자기 전용 폴더를 직접 만들 수 없음 | 앱이 외부 저장소에 둔 파일 |
| 다른 앱의 앱 전용 폴더 | Android 10(API 29) 이상을 대상으로 하는 앱은 범위 지정 저장소(scoped storage)가 기본으로 적용되어 접근할 수 없음 | 앱 사이의 격리. [앱 샌드박스와 권한 (Sandbox·Permissions)](../../../01-foundations/security-model/sandbox-permissions.md) |
| 앱을 지운 뒤 | 내부·외부의 앱 전용 폴더 파일이 지워짐 | 남는 흔적은 [지운 앱이 남긴 흔적](uninstalled-apps.md) |

앱 전용 폴더 밖의 공용 저장소도 함께 봅니다. 관찰한 폰의 `/sdcard` 최상위에는 Alarms, Android, Audiobooks, DCIM, Documents, Download, Movies, Music, Notifications, Pictures, Podcasts, Recordings, Ringtones 와 함께 표준이 아닌 폴더 8개가 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 공용 저장소의 구조는 [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md) 페이지에 있습니다.

공개 도구 ALEAPP 의 `scripts/artifacts` 폴더에는 WhatsApp.py, SamsungNotes.py, chrome.py 같은 앱별 모듈과 packageInfo.py, usagestats.py, appops.py 같은 시스템 모듈이 함께 있습니다 [2]. 앱 전용 모듈이 없는 앱은 시스템 모듈의 결과를 패키지 이름으로 걸러 보는 데서 시작하고, 자세한 순서는 아래 첫 번째 페이지에 있습니다.

## 읽는 순서

1. [처음 보는 앱 분석 순서 (Unknown Apps)](unknown-apps.md) — 설치 기록으로 앱의 정체를 확인하고, 매니페스트 속성과 앱 폴더의 파일 형식을 차례로 살피는 순서입니다.
2. [캐시와 웹뷰 (Cache·WebView)](cache-webview.md) — 앱의 캐시와 WebView 폴더에 남은 방문 기록·HTTP 캐시를 읽고, 캐시가 방문 기록이 아닌 이유를 다룹니다.
3. [지운 앱이 남긴 흔적 (Uninstalled Apps)](uninstalled-apps.md) — 앱을 지운 뒤에도 스토어 DB·시스템 기록·공용 저장소에 남을 수 있는 흔적으로 설치됐던 앱을 되짚습니다.

## 함께 볼 페이지

- [앱 데이터 폴더 구조 (/data/data·/data/user)](../../../01-foundations/storage/app-data-layout.md) — 앱 폴더의 실제 경로와 사용자별 배치
- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) — 앱 DB 대부분이 쓰는 형식
- [설치된 앱 (packages.xml)](../../../02-artifacts/app-usage/packages/index.md) — 앱의 설치·갱신 기록
- [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) — 앱 폴더의 기록과 맞춰 볼 시스템 기록
- [타임라인 작성 (Timeline)](../timeline/index.md) — 여러 앱의 기록을 한 시간 축에 올리는 방법
- [악성 앱 흔적 분석 (Malicious App Triage)](../malicious-app-triage/index.md) — 의심스러운 앱을 좁혀 가는 방법

## 참고 문헌

1. Access app-specific files — Android Developers, https://developer.android.com/training/data-storage/app-specific
2. ALEAPP scripts/artifacts 폴더 목록(GitHub API) — https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
