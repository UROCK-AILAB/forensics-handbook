---
title: "Gemini iOS 앱"
parent: "Gemini"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 310
---

# iOS 앱 (iOS)

iOS 에서는 App Store 의 별도 앱 "Google Gemini" 로 Gemini 를 쓰고 대화 원본은 계정의 서버 활동 기록에 있어서, 기기에서는 앱 설치·권한·화면 전환 기록으로 언제 이 앱을 쓸 수 있었는지를 찾고 대화 내용은 계정 쪽에서 확인합니다.

## 무엇을 기록하나 · 왜 생기나

Android 에서는 Google 앱이 Gemini 를 실행하지만([Android 앱](android.md)), iOS 에는 Gemini 를 쓰는 별도 앱이 있습니다 [2][3]. 대화는 활동 저장 (Keep Activity) 설정에 따라 계정 쪽 Gemini 앱 활동에 저장되고, 보관 기간과 삭제 규칙은 [Gemini](index.md) 허브에 정리했습니다 [1]. 서버와 기기 가운데 어디에 무엇이 남는지의 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다.

Android·iOS 의 ChatGPT·Copilot·Gemini 앱을 비교하면, ChatGPT·Copilot 은 대화를 기기에 평문으로 저장하지만 Gemini 는 대화·브라우저 데이터·이미지를 모두 클라우드에 두고 이를 Google Takeout 으로 받을 수 있습니다 [4]. 2025년 논문의 시험에서는 iOS 기기의 위치 설정을 꺼 둔 상태에서도 Gemini 와 ChatGPT 에서 반경 0.5마일(약 800m) 안의 위치 데이터를 얻을 수 있었습니다 [4]. 이 위치 데이터가 기기의 어느 파일에 있었는지, 클라우드 쪽 자료였는지는 실제 기기로 확인합니다.

App Store 의 개인정보 라벨은 앱이 무엇을 모아 사용자와 연결하는지 판매자가 스스로 밝힌 목록이고, 기기 안에 무엇이 남는지와는 다른 이야기입니다. 그래도 어떤 종류의 데이터를 찾아볼지 정하는 데는 쓸 수 있습니다. 2026-09-25 라벨이 "나와 연결된 데이터" 로 적은 항목은 구매, 정확한·대략 위치, 연락처 정보, 사용자 콘텐츠(사진·영상·음성·이메일), 검색·방문 기록, 식별자, 사용 데이터, 민감 정보, 진단이고, 용도는 개발자의 광고·마케팅, 분석, 개인화, 앱 기능, 기타입니다 [3]. 위치가 라벨에 들어 있는 것은 위 시험 결과와 맞지만, 라벨은 수집 종류만 밝히고 저장 위치는 밝히지 않습니다.

## 위치와 버전별 차이

| 항목 | 내용 | 근거 |
|---|---|---|
| App Store 이름 | Google Gemini (판매자 Google LLC) | App Store 페이지 [3] |
| App Store ID | 6477489729 | App Store 페이지 [3] |
| 2026-09-25 버전 | 1.2026.3770306 (2026-09-24 출시) | App Store 페이지 [3] |
| 요구 사항 | iOS 17.4 이상, iPadOS 17.4 이상 | App Store 페이지 [3] |
| 크기 | 364.3 MB | App Store 페이지 [3] |
| 번들 ID, 컨테이너 안 경로·DB | 실제 기기로 확인 | 아래 "구조" 참고 |
| 위젯·Siri·Live Activities 연동 흔적 | 실제 기기로 확인 | — |

앱은 자주 새 버전이 나와서 위 버전은 2026-09-25 의 값이고, 분석할 기기의 설치 버전은 따로 확인합니다. App Store ID 는 앱 스토어 안의 번호이고 기기의 앱 컨테이너를 찾는 번들 ID 와 다릅니다. 공개 코드 가운데에는 Gemini 의 번들 ID 를 짐작으로 적은 목록도 있어서, 번들 ID 는 기기의 설치 앱 기록에서 읽은 값만 씁니다.

앱 컨테이너 안의 파일은 기기 잠금 상태에 따라 보호 등급이 달라서 [데이터 보호](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/data-protection/index.html)를 먼저 확인하고, 로그인 정보가 들어가는 곳은 [키체인](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/keychain.html) 페이지에서 다룹니다. 로컬 백업으로 수집할 때는 [로컬 백업](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/backups/local-backup/index.html)을 봅니다. Gemini 앱 데이터가 백업에 들어가는지는 백업 목록에 이 앱의 도메인이 있는지로 확인합니다.

## 구조

Gemini 앱 컨테이너 안의 파일 구조는 실제 기기로 확인합니다. 먼저 iOS 가 모든 앱에 대해 남기는 기록으로 앱을 찾고, 그다음 컨테이너 안을 직접 열어 봅니다. 아래 표의 경로와 열 이름은 iLEAPP 분석기 코드에 적힌 그대로입니다.

| 기록 | 경로 (iLEAPP 검색 패턴) | 알려 주는 것 | 근거 |
|---|---|---|---|
| 앱 상태 DB | `*/mobile/Library/FrontBoard/applicationState.db*` | 앱마다 Bundle ID, Bundle Path, Sandbox Path(데이터 컨테이너 경로) | [6] |
| 같은 DB 의 화면 스냅샷 기록 | 위와 같음 | 앱 전환 화면 스냅샷의 Creation Date, Last Used Date, Bundle ID | [6] |
| 앱 권한 DB | `*/mobile/Library/TCC/TCC.db*` | `access` 표의 client(번들 ID), service, 허용 여부, 있을 때 last_modified | [7] |

앱 상태 DB 의 Bundle ID·Bundle Path 목록에서 Gemini 앱에 해당하는 행을 고르면, 같은 행의 Sandbox Path 가 이 앱의 데이터 컨테이너입니다 [6]. 이 분석기는 compatibilityInfo 값을 읽지 못한 앱을 표에서 빼기 때문에, 표에 없다고 설치된 적이 없다고 보지 않습니다 [6]. 컨테이너에서 설정 파일이나 DB 를 찾았다면 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/data-formats/plist.html)과 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/data-formats/sqlite/index.html)의 읽는 법을 씁니다.

## 증거로서 의미

**증명하는 것.** 앱 상태 DB 에 Gemini 앱의 번들 ID 가 있으면 수집 시점에 그 기기에 앱이 설치돼 있었다고 쓸 수 있습니다. TCC.db 에 이 앱의 권한 행이 있으면 해당 권한을 허용하거나 거부한 기록이 있다고 쓸 수 있습니다 [7]. 기기 사진 가운데 Gemini 로 만든 이미지가 있으면 C2PA 정보가 이미지 생성 도구를 밝히는지 볼 수 있고, iLEAPP 의 C2PA 분석기는 실제 Google·Gemini 이미지(JPEG)로 시험된 분석기입니다 [8]. 이 정보의 해석은 [AI 생성물의 출처 정보](../../../01-foundations/concepts/c2pa-provenance.md)에서 다룹니다.

**증명하지 못하는 것.** 설치 사실만으로는 대화했는지, 무엇을 물었는지 알 수 없고 대화 내용은 서버 활동 기록에서 확인해야 합니다 [4]. 개인정보 라벨에 적힌 항목이 기기에 남아 있다고 볼 수도 없는데, 라벨은 모으는 데이터의 종류를 밝힌 것이기 때문입니다. 화면 스냅샷의 생성 시각은 스냅샷을 만든 시각이라서, 이것만으로 앱을 앞에 띄워 썼다거나 사용자가 화면을 봤다고 증명할 수 없습니다 [6]. C2PA 서명자 정보도 iLEAPP 가 서명을 검증하지 않고 적힌 그대로 읽으므로 출처의 단서로만 씁니다 [8].

## 시각 해석

Gemini 대화 시각을 담은 기기 쪽 파일은 실제 기기에서 찾아 확인합니다. 메시지 단위 시각은 서버 활동 기록에 있어서 [계정 데이터 내보내기](export.md)로 받아 맞춰 봅니다. 기기 쪽에서는 TCC.db 의 last_modified 를 iLEAPP 가 Unix 시각으로 보고 UTC 로 바꿔 보여 주고 [7], 화면 스냅샷은 Creation Date 와 Last Used Date 를 따로 보여 줍니다 [6]. 설치·실행 시각을 다른 iOS 기록과 시간순으로 합치는 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/analysis/timeline/index.html)에서 다룹니다.

## 함정과 한계

iOS 에서도 Gemini 를 앱이 아니라 사파리나 크롬으로 열 수 있어서, 앱이 없다고 쓰지 않았다고 볼 수 없습니다. 이 경우 흔적은 [웹 브라우저](web.md)에서 다룬 브라우저 기록 쪽에 남고, iOS 판의 [사파리](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/browsers/safari/index.html)와 [크롬](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/browsers/chrome.html) 페이지에서 읽는 법을 다룹니다.

iLEAPP 에는 AI 대화 앱 분석기로 ChatGPT 용 `chatgpt.py` 와 Claude 용 `iOSclaude.py` 가 있지만, Gemini 전용 분석기는 없습니다(2026-09-23 main 기준) [5]. ChatGPT 분석기는 앱 1.2024.178 까지 다루고, 두 분석기는 [ChatGPT iOS 앱](../chatgpt/ios.md)과 [Claude iOS 앱](../claude/ios.md)에서 다룹니다. 지금 판의 도구는 다를 수 있으니 쓰기 전에 저장소 목록을 다시 봅니다.

위 논문의 결과는 논문이 시험한 앱 판과 iOS 판에 따른 것이고, 2026-09 의 앱이 같은 동작을 하는지는 실제 기기로 확인합니다 [4].

## 직접 분석해 보기

**헥스로 한 번.** Gemini 앱의 Sandbox Path 아래에서 찾은 파일을 헥스 편집기로 열어 앞 16바이트를 봅니다. `53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00`(`SQLite format 3` 과 NUL) 이면 SQLite 이고, `62 70 6C 69 73 74 30 30`(`bplist00`) 이면 이진 속성 목록 파일입니다. 이 두 값은 각 형식의 명세에 정해진 머리 값이고, 형식마다 이어서 읽는 법은 위에 링크한 SQLite·속성 목록 파일 페이지에 있습니다.

**공개 도구로 한 번.** iLEAPP 로 전체 파일 시스템 추출본을 처리한 뒤 "Application State" 보고서에서 Gemini 앱의 Bundle ID 와 Sandbox Path 를 찾고, "Application Permissions" 보고서에서 같은 Bundle ID 의 권한 행을 봅니다(iLEAPP 2026-09-23 main 기준) [6][7].

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 계정 데이터 내보내기 | 대화 내용과 메시지 시각 | [계정 데이터 내보내기](export.md) |
| 사파리·크롬 방문 기록 | 앱 대신 웹 판을 쓴 흔적 | [웹 브라우저](web.md) |
| 음성 대화 기능 | Gemini Live 같은 음성 사용 | [음성 대화 기능](../../generative-media/voice-mode.md) |
| 생성 이미지의 C2PA 정보 | 사진 속 이미지가 AI 로 만든 것이라고 적힌 기록 | [AI 생성물의 출처 정보](../../../01-foundations/concepts/c2pa-provenance.md) |
| 서비스 회사 자료 | 서버에 남은 대화 원본 | [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md) |

## 실습

시험용 기기와 계정으로 아래 질문을 풀어 봅니다.

1. 앱을 설치하고 한 번 대화한 뒤 로컬 백업을 만들면, 백업 목록에 Gemini 앱의 파일이 들어갑니까?
2. 앱 상태 DB 에서 찾은 Sandbox Path 아래에 대화 문장이 담긴 파일이 있습니까, 아니면 위 논문의 결과대로 대화가 클라우드에만 있습니까?
3. 위치 설정을 끈 상태로 대화한 뒤 계정 데이터 내보내기를 받으면, 위치 정보가 어떤 정밀도로 남습니까?
4. 기기 쪽 흔적으로 알아낸 사용 시각이 계정 데이터 내보내기의 시각과 맞습니까?

## 참고 문헌

1. Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961 (2026-09-25 열람)
2. Get started with the Gemini mobile app — https://support.google.com/gemini/answer/14554984?co=GENIE.Platform%3DAndroid&oco=0 (2026-09-25 열람)
3. Google Gemini — App Store — https://apps.apple.com/us/app/google-gemini/id6477489729 (2026-09-25 열람)
4. Sonali Tyagi, Yufeng Gong, Umit Karabiyik, "Forensic analysis and privacy implications of LLM mobile apps: A case study of ChatGPT, Copilot, and Gemini", Forensic Science International: Digital Investigation, 54 (2025), 301974. https://doi.org/10.1016/j.fsidi.2025.301974 (초록)
5. iLEAPP 저장소 `scripts/artifacts/` 파일 목록(2026-09-23 main) — https://github.com/abrignoni/iLEAPP/tree/main/scripts/artifacts, 그 가운데 `chatgpt.py`(2026-08-21 갱신), `iOSclaude.py`(2026-08-09 갱신)
6. iLEAPP `scripts/artifacts/applicationStateDB.py`(Application State 2026-08-25 갱신, Application Snapshot 2026-09-12 갱신) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/applicationStateDB.py
7. iLEAPP `scripts/artifacts/tcc.py`(2026-07-31 갱신) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/tcc.py
8. iLEAPP `scripts/artifacts/c2paProvenance.py`(2026-07-31 갱신) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/c2paProvenance.py
