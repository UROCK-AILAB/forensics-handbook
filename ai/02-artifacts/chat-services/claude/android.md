---
title: "Claude Android 앱"
parent: "Claude"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 180
---

# Android 앱 (Android)

Android 의 Claude 앱은 패키지 ID `com.anthropic.claude` 로 설치되고, 대화 원본은 계정 서버에 있습니다. 앱 데이터 폴더 안에 어떤 파일이 남는지는 확인하지 못해서, 이 페이지는 설치 흔적을 찾는 기준과 스토어의 데이터 보안 표기를 정리합니다.

> 확인 날짜: 2026-09. Google Play 의 앱 주소와 데이터 보안 페이지, 공식 도움말(2026-09-25 열람)만 근거로 썼습니다. Android 기기는 직접 관찰하지 않았고, 현재 앱 버전과 지원하는 최소 Android 버전은 Play 상세 페이지 본문을 읽지 못해 확인하지 못했습니다.

## 무엇이 남나 · 왜 생기나

Google Play 에서 앱 이름은 "Claude by Anthropic", 개발자는 Anthropic PBC 이고, Play 주소에 붙은 패키지 ID 는 `com.anthropic.claude` 입니다[1][2]. 앱은 claude.ai 와 같은 계정으로 로그인해 쓰고 대화는 서버에 저장되며, 지운 대화의 서버 쪽 처리는 [Claude](index.md) 허브에 정리해 두었습니다. 기기에는 설치한 패키지와 앱 데이터 폴더(`/data/data/com.anthropic.claude/`)가 생기지만, 그 안의 데이터베이스·설정 파일 이름과 대화 본문을 기기에 두는지는 확인하지 못했습니다.

Android 앱에서는 계정 데이터를 내보낼 수 없고, 내보내기는 웹이나 데스크톱 앱에서만 됩니다[3]. 대화 내용이 필요하면 [계정 데이터 내보내기](export.md)를 웹이나 PC 에서 받거나 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 검토합니다.

## 위치

| 흔적 | 위치 | 근거 |
|---|---|---|
| 설치한 패키지 | 패키지 ID `com.anthropic.claude` | [1][2] |
| 앱 데이터 폴더 | `/data/data/com.anthropic.claude/` | 앱 데이터 폴더 공통 구조(안의 파일 이름은 확인하지 못함) |
| 대화 원본 | 계정 서버 | 허브 참고 |

앱 데이터 폴더가 어디에 있고 어떤 하위 폴더로 나뉘는지는 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html)에서, 기기 암호화 때문에 무엇을 언제 읽을 수 있는지는 [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html)에서 다룹니다. 폴더 안에서 데이터베이스나 설정 파일을 찾으면 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html), [설정 XML과 SharedPreferences](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/shared-preferences.html), [LevelDB와 IndexedDB](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/leveldb-indexeddb.html)의 방법으로 읽습니다.

## 스토어의 데이터 보안 표기

Play 의 데이터 보안 페이지는 앱이 모으는 데이터와 다른 곳과 나누는 데이터를 다음처럼 적고 있습니다[2]. 괄호 안 "선택"은 사용자가 고를 수 있다고 표기한 항목입니다.

| 구분 | 표기한 데이터 |
|---|---|
| 수집 | 이름·이메일·사용자 ID·전화번호, 사진(선택), 기기 ID, 파일·문서(선택), 앱 상호작용·사용자 생성 콘텐츠, 비정상 종료 로그·진단·성능, 대략적 위치·정확한 위치(정확한 위치는 선택) |
| 공유 | 이메일·사용자 ID·전화번호, 앱 상호작용, 비정상 종료 로그·진단·성능, 대략적 위치 |

같은 페이지는 전송 중에 데이터를 암호화하고 사용자가 데이터 삭제를 요청할 수 있다고 적었습니다[2]. 이 표기는 서비스가 어떤 종류의 데이터를 다루는지 알려 주지만, 기기 안 어느 파일에 무엇이 남는지는 알려 주지 않습니다. 서비스 회사에 자료를 요청할 때 어떤 항목이 있을 수 있는지 가늠하는 데 씁니다.

## 증거로서 의미

**증명하는 것.** 기기에 `com.anthropic.claude` 패키지나 그 앱 데이터 폴더가 있으면 이 기기의 그 사용자 공간에 앱이 설치된 적이 있다고 쓸 수 있습니다.

**증명하지 못하는 것.** 앱 데이터 폴더의 내용을 확인하지 못해서, 폴더가 있다는 사실만으로 어떤 대화를 했는지나 언제 마지막으로 썼는지는 말할 수 없습니다. 앱이 없어도 휴대폰 브라우저로 claude.ai 를 썼을 수 있어서 [웹 브라우저](web.md)와 [크롬 (Chrome for Android)](https://urock-ailab.github.io/forensics-handbook-android/02-artifacts/browsers/chrome/index.html)도 봅니다. 누가 기기를 쥐고 있었는지는 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 좁힙니다.

## 시각 해석

앱 데이터 폴더 안의 시각 칸은 확인하지 못했습니다. 설치·업데이트 시각이나 앱 폴더의 파일 시스템 시각은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-android/03-techniques/analysis/timeline/index.html)의 방법으로 읽고, 대화마다의 시각은 계정 데이터 내보내기 자료에서 얻습니다. 기기 시각과 서버 자료의 시각을 맞추는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

Play 에서 다른 개발자가 올린 비슷한 이름의 앱이 있을 수 있어서, 앱 이름이 아니라 패키지 ID 로 가립니다. 수집 방법에 따라 `/data/data` 아래를 읽을 수 없는 경우가 많아서, 앱 데이터 폴더를 얻지 못했다고 앱에 흔적이 없다고 쓰지 않습니다. 앱이 자주 바뀌어서, 앱 데이터 폴더를 얻었다면 그 기기에 깔린 앱 버전을 함께 적고 이 페이지의 내용과 어긋나는 점을 따로 기록합니다.

## 직접 분석해 보기

앱 데이터 폴더의 파일을 확인하지 못해서 헥스 예시는 싣지 않습니다. 앱 데이터 폴더 사본을 얻었다면 다음 순서로 봅니다.

1. 폴더 이름이 `com.anthropic.claude` 인지 확인하고, 하위 폴더 목록을 적습니다.
2. 파일 첫 바이트로 형식을 가립니다. SQLite 는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html) 페이지의 파일 머리로, 설정 XML 은 `<?xml` 로 시작하는지로 봅니다.
3. 찾은 데이터베이스는 SQLite 도구(예: DB Browser for SQLite)로 표 이름부터 적고, 시각으로 보이는 칸의 단위를 자릿수로 가립니다.
4. 찾은 내용은 확인한 앱 버전·날짜와 함께 기록합니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [웹 브라우저](web.md) | 휴대폰 브라우저로 쓴 흔적 |
| [계정 데이터 내보내기](export.md) | 대화 본문과 시각 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 회사 네트워크에서 접속한 기록 |
| [iOS 앱](ios.md) | 같은 사람이 다른 휴대폰에서 쓴 경우 |

## 실습

직접 만든 시험용 Android 기기나 공개 검체(NIST CFReDS 등)의 Android 이미지로 다음을 풀어 봅니다.

1. 설치한 앱 목록에 `com.anthropic.claude` 가 있는가, 있다면 처음 설치한 시각과 마지막 업데이트 시각은 언제인가?
2. 앱 데이터 폴더를 얻을 수 있었다면 어떤 하위 폴더와 파일 형식이 있는가?
3. 크롬 방문 기록의 claude.ai 방문과 앱 설치 시각 가운데 어느 쪽이 먼저인가?

## 참고 문헌

1. Claude by Anthropic — Google Play 상세(본문 못 읽음, 주소의 id 만) — https://play.google.com/store/apps/details?id=com.anthropic.claude
2. Claude by Anthropic — Google Play 데이터 보안 — https://play.google.com/store/apps/datasafety?id=com.anthropic.claude
3. How can I export my Claude data? (Claude Help Center) — https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data
