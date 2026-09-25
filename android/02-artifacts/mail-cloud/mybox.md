---
title: "네이버 MYBOX"
parent: "아티팩트 · 메일·클라우드"
nav_order: 1120
---

# 네이버 MYBOX (MYBOX)

## 한 줄 요약

네이버 MYBOX 는 국내에서 쓰는 클라우드 저장 앱이지만 이번에 연 공개 자료에서는 패키지 이름·DB·캐시 경로·업로드 기록을 하나도 확인하지 못해서, 이 페이지는 확인된 사실이 없다는 점과 앱을 직접 조사하는 방법, 그동안 시스템 기록으로 볼 수 있는 것을 정리합니다.

## 무엇을 기록하나 · 왜 생기나

클라우드 저장 앱은 계정의 파일 목록을 기기에 받아 두고, 사용자가 연 파일을 캐시하며, 올린 파일의 기록을 남기는 것이 보통입니다. 구글 드라이브나 원드라이브 앱에서 이런 기록이 확인되었지만 ([구글 드라이브 (Google Drive)](google-drive.md), [삼성 클라우드와 원드라이브 (Samsung Cloud·OneDrive)](samsung-cloud-onedrive.md)), MYBOX 앱이 무엇을 어디에 남기는지 적은 공개 포렌식 자료는 이번에 찾지 못했습니다.

공개 도구 ALEAPP 의 모듈 목록에도 MYBOX 나 네이버 관련 모듈은 없었습니다 [1]. 파일 이름에 naver, ndrive, mybox 가 들어간 모듈이 하나도 없었습니다 [1].

## 위치와 버전별 차이

패키지 이름을 확인하지 못해서 경로도 적지 않습니다. 검체에서는 [설치된 앱 (packages.xml)](../app-usage/packages/index.md) 기록으로 패키지 이름부터 확정하고, 그 이름으로 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 페이지에서 설명하는 앱 데이터 폴더와 [공용 저장 공간 (Shared Storage·/sdcard)](../../01-foundations/storage/shared-storage.md) 의 앱 폴더를 찾습니다. 패키지 이름과 UID 를 맞춰 보는 법은 [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md) 페이지에 있습니다.

Android 버전이나 One UI 버전에 따른 차이, 앱 버전에 따른 차이도 확인한 자료가 없습니다. 관찰 기기에서도 이 앱이 설치되어 있었는지는 확인하지 못했습니다.

## 증거로서 의미

앱 내부 기록을 모르는 동안에도 시스템 기록으로 말할 수 있는 것은 있습니다. 설치된 앱 기록은 MYBOX 앱이 기기에 설치되어 있었다는 사실을, 앱 사용 기록은 그 앱을 언제 앞에 띄웠는지를, 데이터 사용량 기록은 그 앱이 어느 시간대에 데이터를 얼마나 주고받았는지를 보여 줍니다. 이 기록들을 합쳐도 "그 시간대에 MYBOX 앱을 쓰고 데이터를 주고받은 기록이 있다" 까지이고, 어떤 파일을 올렸거나 내려받았는지는 앱 내부 기록 없이 말할 수 없습니다. 보고서에는 기록이 말하는 만큼만 적는 방법을 [포렌식 보고서 (Forensic Report)](../../03-techniques/reporting/forensic-report.md) 페이지에서 다룹니다.

## 함정과 한계

첫째, 관찰 기기의 설정 값에는 네이버 이름이 들어간 키로 `naver_sports_state`, `support_nowbar_naver_sports`, `key_now_bar_com_nhn_android_search` 가 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 이 키들은 MYBOX 와 관계가 없고, 마지막 키는 네이버 검색 앱의 패키지 이름이 키에 들어간 모양입니다. 설정에 네이버 키가 있다고 MYBOX 를 썼다는 근거로 삼으면 안 됩니다.

둘째, 다른 자료나 도구가 MYBOX 의 경로나 표를 보여 주더라도 검체에서 직접 확인하고 쓰고, 도구 출력은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 방법으로 원본과 맞춰 봅니다.

셋째, 앱 내부 기록이 없으면 무엇을 올렸는지는 기기보다 계정 쪽 데이터에서 찾아야 할 수 있고, 계정 데이터를 받는 일반 절차는 [클라우드 데이터 (Google Takeout 등)](../../03-techniques/acquisition/cloud-data.md) 페이지에서 다룹니다. MYBOX 계정 데이터를 내려받는 기능이 있는지는 확인하지 못했습니다.

## 직접 분석해 보기

### 앱을 직접 조사하기

공개 자료가 없으니 시험 기기에 앱을 설치해 조사하는 방법이 맞습니다. 순서는 아래처럼 잡을 수 있습니다.

1. 시험 기기에 MYBOX 앱을 설치하고, 설치 직후 앱 데이터 폴더와 공용 저장 공간의 파일 목록을 떠 둡니다.
2. 로그인, 파일 하나 올리기, 파일 하나 내려받기, 파일 하나 지우기를 시각을 적어 가며 한 가지씩 합니다.
3. 동작마다 폴더를 다시 떠서 새로 생기거나 바뀐 파일을 찾습니다.
4. 바뀐 SQLite·XML 파일을 열어 적어 둔 시각과 파일 이름이 어느 표·칸에 들어갔는지 맞춥니다.

이 절차의 일반 방법은 [앱 데이터 분석 (App Data Analysis)](../../03-techniques/analysis/app-data-analysis/index.md) 페이지에서 다루고, 파일을 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 와 [설정 XML과 SharedPreferences](../../01-foundations/data-formats/shared-preferences.md) 페이지에 있습니다. 찾아낸 시각 값을 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

### 공개 도구로 한 번

ALEAPP 에는 MYBOX 모듈이 없어서 [1], 설치된 앱·앱 사용 기록·데이터 사용량처럼 시스템 쪽 모듈로 MYBOX 패키지의 기록을 걸러 보는 것이 공개 도구로 할 수 있는 일입니다. 앱 내부 파일은 SQLite 뷰어 같은 일반 도구로 직접 엽니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [설치된 앱 (packages.xml)](../app-usage/packages/index.md) | MYBOX 앱의 패키지 이름과 설치·업데이트 시점 |
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | 앱을 앞에 띄운 시각 |
| [데이터 사용량 (netstats)](../network/netstats.md) | 그 시간대에 앱이 주고받은 데이터 양 |
| [계정 (Accounts)](../system-account/accounts/index.md) | 네이버 계정을 기기에 넣고 뺀 기록 |
| [알림 기록 (Notification History)](../app-usage/notification-history.md) | 업로드·동기화 알림이 남았는지 |

클라우드로 자료를 내보냈는지 따지는 흐름은 [자료를 밖으로 보냈나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에 있습니다.

## 실습

공개 안드로이드 검체(NIST CFReDS 등)나 직접 만든 시험 기기로 아래 질문을 풀어 봅니다.

1. 설치된 앱 기록에서 MYBOX 에 해당하는 패키지를 찾을 수 있습니까? 그 근거는 무엇입니까?
2. 시험 기기에서 파일 하나를 올린 뒤, 앱 데이터 폴더에서 그 파일 이름이 처음 나타나는 파일은 어디입니까?
3. 파일을 지운 뒤에도 그 이름이 남아 있는 파일이 있습니까?
4. 올린 시각에 데이터 사용량 기록에서 그 앱의 송신량이 늘었습니까?

## 참고 문헌

1. ALEAPP 저장소 파일 목록 (GitHub API, git trees, recursive) — https://api.github.com/repos/abrignoni/ALEAPP/git/trees/main?recursive=1
