---
title: "저장된 암호"
parent: "아티팩트 · 자격 증명·권한"
nav_order: 1860
---

# 저장된 암호 (Passwords·iCloud Keychain)

사용자가 저장한 웹사이트·앱 암호와 패스키, 인증 코드는 데이터 보호 키체인에 들어 있고 macOS 15 Sequoia 무렵부터는 Passwords 앱에서 한곳에 모아 볼 수 있으며, iCloud 키체인을 켜 두었다면 같은 Apple 계정의 다른 기기와 종단 간 암호화로 동기화되어서, 맥에서 보이는 항목이 그 맥에서 저장한 것인지부터 구분해서 읽어야 합니다 [1][3].

## 무엇을 기록하나 · 왜 생기나

사용자가 Safari나 앱에서 로그인 정보를 저장하면 키체인에 항목이 생기고, Safari와 앱이 만들어 준 암호(generated passwords)도 키체인에 저장된 뒤 다른 기기로 동기화됩니다 [3]. Passwords 앱은 이렇게 쌓인 웹사이트·앱 암호, 패스키, 인증 코드(verification codes)를 보여 주고, Wi-Fi 암호와 iCloud 키체인 설정도 다룹니다 [1].

앱에서는 암호를 찾고 보고 만들고 바꾸고 지울 수 있고, 암호 기록(password history)을 보거나, AirDrop으로 한 사람에게 공유하거나, 그룹을 만들어 여러 사람과 공유하고 그룹 사람을 더하거나 뺄 수 있습니다 [1]. 보안 권장 사항(Recommendations)을 보거나 암호를 가져오고 내보낼 수도 있습니다 [1]. 이 기능들은 사용자의 행위를 보여 주는 흔적이 될 수 있고, 그 상태가 저장되는 파일·표는 실제 기기에서 확인해야 합니다.

iCloud 키체인은 iPad, iPhone, Mac, Apple Watch, Apple Vision Pro 사이에서 암호와 패스키를 동기화합니다 [3]. 항목은 Apple 서버를 거쳐 기기에서 기기로 옮겨지지만 종단 간 암호화되어 있어서 Apple도, 다른 기기도 내용을 읽을 수 없고, 사용자의 모든 기기에 접근할 수 없게 되어도 키체인 내용을 되찾을 수 있게 복구 절차가 따로 설계되어 있습니다 [3]. 어떤 항목이 동기화되고 어떤 항목이 기기에 묶여 남는지는 [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md)에서 다룹니다.

## 위치와 버전별 차이

Passwords 앱은 macOS 15 Sequoia부터 있는 것으로 보이고, 사용 설명서는 macOS 15 Sequoia, 26 Tahoe, 27 Golden Gate 판을 다룹니다 [1]. 공식 최소 버전은 따로 나와 있지 않습니다. 암호 기록 설명은 26 Tahoe와 27 Golden Gate 판에만 있어서 [2], 암호 기록 기능은 macOS 26부터로 보입니다.

| macOS | 내용 | 출처 |
|---|---|---|
| 10.15 Catalina ~ 14 Sonoma | 암호를 보던 곳(시스템 설정, Safari 설정, 키체인 접근 앱)은 실제 기기에서 확인 | — |
| 15 Sequoia | Passwords 앱이 있는 것으로 보임 | [1] |
| 26 Tahoe | 암호 기록(View password history) 페이지가 이 판부터 나옴 | [2] |
| 27 Golden Gate | Passwords 앱과 암호 기록 기능이 있음 | [1][2] |

디스크에서 이 항목들은 데이터 보호 키체인에 있습니다. 데이터 보호 키체인의 파일 위치, 키체인 접근 앱에서 어떤 이름으로 보이는지, 예전 Safari·앱 암호가 남는 파일 기반 login 키체인과 어떻게 다른지는 모두 [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md)에 있어서, 이 페이지는 Passwords 앱과 iCloud 키체인의 동작을 다룹니다.

## 구조

Passwords 앱에서 보이는 정보를 나누면 아래와 같습니다.

| 앱에서 보이는 정보 | 담긴 내용 | 출처 | 디스크 저장 위치 |
|---|---|---|---|
| 웹사이트·앱 암호 | 사이트·앱별로 저장한 암호 | [1] | 데이터 보호 키체인 |
| 패스키 | 사이트·앱별 패스키 | [1] | 데이터 보호 키체인 |
| 인증 코드 | 인증 코드(verification codes) | [1] | 공개 자료 없음 |
| Wi-Fi | Wi-Fi 암호 | [1] | 공개 자료 없음 |
| 암호 기록 | 웹사이트·앱 암호의 이전 판과 바뀐 날짜, AirDrop으로 공유한 일, 공유 그룹에 공유하거나 공유를 푼 일 | [2] | 공개 자료 없음 |
| 공유 그룹 | 그룹과 그룹 사람 | [1] | 공개 자료 없음 |
| 보안 권장 사항 | 권장 사항 목록 | [1] | 공개 자료 없음 |

데이터 보호 키체인 항목을 어떤 키로 암호화하고 무엇이 그 키를 보호하는지는 [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md)에 있습니다. 암호 기록이 iCloud 키체인으로 다른 기기와 동기화되는지, 어디에 저장되는지는 알려져 있지 않습니다.

## 증거로서 의미

### 증명하는 것

Passwords 앱이나 키체인에서 어떤 사이트·앱의 항목이 보이면, 수집 시점에 이 사용자의 키체인에 그 사이트·앱의 자격 증명이 저장되어 있었다고 말할 수 있습니다. 사이트 이름과 계정 이름만으로도 사용자가 어떤 서비스에 계정이 있었는지를 보여 주는 단서가 됩니다.

macOS 26 이후라면 암호 기록에서 한 항목의 이전 암호 판과 바뀐 날짜를 볼 수 있고, 그 암호를 AirDrop으로 공유했거나 공유 그룹에 넣고 뺀 일도 볼 수 있습니다 [2]. 그래서 계정을 빼앗긴 뒤 암호가 언제 바뀌었는지, 자격 증명이 다른 사람에게 건너간 적이 있는지를 따질 때 먼저 확인할 만한 기록입니다.

### 증명하지 못하는 것

iCloud 키체인은 같은 Apple 계정의 기기 사이에서 암호와 패스키를 동기화해서 [3], 맥에서 보이는 항목이 그 맥에서 저장된 것이 아니라 아이폰이나 다른 맥에서 저장된 뒤 넘어온 것일 수 있습니다. 항목마다 처음 저장한 기기를 적는 필드가 있는지는 알려져 있지 않아서, 동기화가 켜져 있던 계정이라면 "이 맥에서 저장했다" 고 쓰지 않습니다. 계정 상태는 [아이클라우드 계정 (iCloud Account)](../cloud-apps/icloud-account.md)에서 확인합니다.

Safari와 앱이 만든 암호도 키체인에 저장되어서 [3], 저장된 암호가 있다고 사용자가 그 암호를 직접 정했거나 기억하고 있었다고 볼 수는 없습니다. 저장된 암호는 로그인한 적이 있다는 기록도 아니라서, 실제 로그인 여부와 시각은 브라우저 방문 기록과 서비스 쪽 기록에서 따로 찾습니다.

보고서에는 "피의자가 이 계정 암호를 알고 있었다" 대신 "이 사용자의 Passwords 앱에 사이트 A의 계정 B 항목이 있고, 암호 기록에 날짜 D에 암호가 바뀐 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

암호 기록은 암호가 바뀐 날짜를 보여 줍니다 [2]. 이 날짜가 어떤 기준 시각으로 저장되는지, 동기화된 기기에서 바뀐 경우에도 같은 날짜가 보이는지는 알려져 있지 않습니다. 화면에서 읽은 날짜를 보고서에 옮길 때는 그 맥의 시간대 설정을 함께 적고, 시간대를 확인하는 방법은 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)에 있습니다.

## 함정과 한계

데이터 보호 키체인 항목은 암호화되어 있고, 암호화된 증거를 다루는 일반 절차는 [암호화된 증거 다루기 (Encrypted Evidence)](../../03-techniques/analysis/encrypted-evidence/index.md)를 따릅니다. 암호 기록, 공유 그룹, 보안 권장 사항 상태가 저장되는 파일은 알려져 있지 않아서, 이 정보는 실행 중인 맥의 앱 화면으로 확인합니다.

지운 암호가 "최근 삭제" 같은 목록에 얼마 동안 남는지는 알려져 있지 않아서, 목록에 없다고 저장한 적이 없다고 읽지 않습니다. Passwords 앱을 실행하거나 암호를 보려고 인증한 일이 통합 로그에 남는지, 남는다면 어떤 프로세스·서브시스템 이름으로 남는지도 실제 기기에서 확인해야 합니다.

Passwords 앱은 암호를 내보낼 수 있고 [1], 내보낸 파일의 형식과 기본 이름은 실제 기기에서 확인합니다. 내보내기를 한 적이 있다면 그 파일이 사용자 폴더나 [휴지통 (.Trash)](../file-folder-usage/trash.md)에 남아 있을 수 있어서, [콘텐츠 검색 (Content Search)](../../03-techniques/analysis/content-search.md)으로 사이트 이름이나 계정 이름을 넣어 찾아봅니다.

## 직접 분석해 보기

데이터 보호 키체인 항목은 암호화되어 있어서 이 페이지에서 헥스로 따라갈 평문 구조가 없고, 키체인 파일을 헥스로 읽는 방법은 [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md)에 있습니다. 이 페이지는 실행 중인 맥에서 앱 화면으로 확인하는 절차를 적습니다. 화면을 여는 일도 시스템을 건드리는 일이라서 조사 권한을 확인하고, 순서와 기록 방법은 [라이브 대응 (Live Response)](../../03-techniques/process-acquisition/live-response/index.md)을 따릅니다.

1. macOS 판을 먼저 확인합니다. 15 Sequoia 이상이면 Passwords 앱이 있을 것으로 보고, 26 Tahoe 이상이면 암호 기록까지 볼 수 있습니다 [1][2].
2. iCloud 키체인이 켜져 있는지 확인해서, 보이는 항목이 동기화된 것일 수 있는지를 먼저 적어 둡니다 [3].
3. 조사 대상 사이트·앱의 항목을 찾아 사이트 이름과 계정 이름을 기록하고, 암호 평문은 사건에 꼭 필요할 때만 확인하고 보고서에 옮기지 않습니다.
4. macOS 26 이상이면 그 항목의 암호 기록에서 바뀐 날짜와 공유 기록을 화면째 남깁니다 [2].
5. 공유 그룹과 보안 권장 사항 화면도 사건과 관계있는 항목이 있는지 봅니다 [1].

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md) | 데이터 보호 키체인과 login 키체인의 위치·구조, 동기화 대상 항목 |
| [아이클라우드 계정 (iCloud Account)](../cloud-apps/icloud-account.md) | 이 맥에 로그인한 Apple 계정과 동기화 여부 |
| [사파리 (Safari)](../browsers/safari/index.md) | 저장된 암호의 사이트를 실제로 방문한 기록 |
| [크롬·엣지·웨일 (Chromium 계열)](../browsers/chromium/index.md) | 다른 브라우저가 따로 저장한 암호 |
| [파이어폭스 (Firefox)](../browsers/firefox.md) | 다른 브라우저가 따로 저장한 암호 |
| [와이파이 기록 (Wi-Fi)](../network/wifi.md) | Passwords 앱의 Wi-Fi 항목과 실제 접속 기록 |
| [에어드롭 (AirDrop)](../external-devices/airdrop.md) | 암호 기록에 보이는 AirDrop 공유와 같은 시간대의 흔적 |

암호 저장소를 노리는 악성 코드의 흔적과 함께 볼 때는 [정보 탈취 악성 코드 (Infostealer)](../../04-scenarios/incident/infostealer.md)의 흐름을 따릅니다.

## 실습

macOS 공개 데이터셋(NIST CFReDS 등)에서 아래 질문을 풀어 봅니다. 디스크 이미지만 있다면 앱 화면 대신 버전과 계정 상태부터 확인합니다.

1. 분석 대상의 macOS 판은 무엇이고, 그 판에 Passwords 앱과 암호 기록 기능이 있는가?
2. 이 맥에 로그인한 Apple 계정이 있는가, 있다면 iCloud 키체인이 켜져 있었다고 볼 근거가 있는가?
3. 사용자 폴더와 휴지통에 암호를 내보낸 것으로 보이는 파일이 있는가?
4. 사파리 방문 기록에서 자주 보이는 사이트 가운데 키체인에 항목이 있는 사이트는 어디인가?

## 참고 문헌

1. Apple, Passwords User Guide for Mac (첫 페이지·목차) — https://support.apple.com/guide/passwords/welcome/mac
2. Apple, Passwords User Guide "View password history" — https://support.apple.com/guide/passwords/view-password-history-mchl4da98004/mac
3. Apple Platform Security, "iCloud Keychain security overview" — https://support.apple.com/guide/security/icloud-keychain-security-overview-sec1c89c6f3b/web
