# 메신저로 파일을 보냈나 (Messenger)

> 상위 허브: [자료를 밖으로 빼돌렸나 (Data Exfiltration)](/04-scenarios/exfiltration/data-exfiltration/index.md)

이 페이지는 PC 용 메신저로 자료 파일을 보냈는지 확인하는 순서를 다룹니다. 메신저마다 대화 DB 의 위치·구조·암호화가 다르므로, 메신저별 내용은 각 메신저 페이지에서 다룹니다. 여기서는 어느 메신저에나 쓰는 조사 순서와, PC 한 대에서 본 메신저 폴더 위치를 다룹니다.

이 페이지에서 "(관찰)" 을 붙인 내용은 Windows 11 Home 25H2(빌드 26200.9457) PC 한 대에서 직접 본 것입니다(확인 범위: Win11 25H2 한 대). 메신저 판이나 설치 방식이 다르면 위치가 다를 수 있습니다.

## 조사 질문

- 이 PC 에서 어떤 메신저를 어느 계정으로 썼습니까?
- 그 메신저로 자료 파일을 보냈습니까? 누구에게, 언제, 어떤 파일을 보냈습니까?
- 대화 기록을 읽을 수 없을 때 어디까지 말할 수 있습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| 설치된 메신저 | [설치 프로그램](/02-artifacts/system-account/uninstall.md) 과 [스토어 앱 설치 목록](/02-artifacts/system-account/appx-staterepository.md) 에서 메신저를 찾습니다. 설치 목록에 없어도 사용자 프로필 안의 앱 폴더를 봅니다. |
| 사용자·계정 | 메신저 데이터는 사용자 프로필 안에 있습니다. 한 사용자가 여러 메신저 계정을 썼을 수 있습니다. |
| 대화 DB 암호화 | 대화 DB 가 암호화돼 있으면 파일 전송 기록을 바로 읽지 못합니다. 이때 [암호화 증거 다루기](/03-techniques/analysis/encrypted-evidence/index.md) 를 봅니다. |
| 시간대 | 메신저 기록 시각과 PC 흔적 시각을 같은 기준으로 맞춥니다([시간대 설정](/02-artifacts/system-account/time-zone.md)). |
| 수집 범위 | 사용자 프로필의 메신저 폴더 전체, 사용자 하이브(NTUSER.DAT), SRUDB.dat 를 확보합니다. |

## 이 PC 에서 본 메신저 폴더

아래는 관찰한 PC 에 있던 폴더와 키입니다(관찰). 기본 위치라고 확정한 목록이 아닙니다.

| 메신저 | 이 PC 에서 본 위치 | 함께 본 것 |
|---|---|---|
| 텔레그램 데스크톱 | `%APPDATA%\Telegram Desktop\tdata`, `%USERPROFILE%\Downloads\Telegram Desktop` | `Downloads\Telegram Desktop` 이 받은 파일의 기본 저장 폴더인지는 확인하지 못했습니다. |
| 새 Teams | `%LOCALAPPDATA%\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams\` | 그 아래 `EBWebView\WV2Profile_tfw` 가 WebView2 프로필이었습니다. `IndexedDB`·`History`·`Network\Cookies`·`Service Worker` 가 있었습니다. |
| 클래식 Teams | `%APPDATA%\Microsoft\Teams` | 이 PC 에는 없었습니다. |
| 카카오톡 PC | `%LOCALAPPDATA%\Kakao\KakaoTalk` | 그 아래 `users`, `global`, `OpenLinkPreset` 폴더가 있었습니다. |
| 카카오톡 PC (레지스트리) | `HKCU\Software\Kakao\KakaoTalk` | 그 아래 `DeviceInfo`, `UserAccounts`, `Update` 등 하위 키가 있었습니다. |

- 이 PC 에는 카카오톡이 있었지만 `Documents\카카오톡 받은 파일` 폴더는 없었습니다(관찰).
- 카카오톡이 받은 파일을 어디에 두는지는 [카카오톡 PC](/02-artifacts/messengers/kakaotalk-pc/index.md) 에서 확인합니다.
- 새 Teams 폴더의 `History`·`Cookies` 는 브라우저가 아니라 Teams 가 쓰는 WebView2 프로필의 파일입니다. 읽는 법은 [크롬 계열 앱 공통 구조](/01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에서 다룹니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 메신저별 대화 DB | 보낸 메시지와 파일 전송 기록 (남는 모양은 메신저마다 다름) | 아래 "함께 볼 페이지" 의 메신저 페이지 |
| 2 | 메신저 폴더 안에 저장된 파일 | 주고받은 파일이 남아 있는지 | 메신저 페이지 |
| 3 | SRUM 네트워크 사용량 | 메신저 앱이 그 시간대에 보낸 바이트 수 | [SRUM](/02-artifacts/execution/system-resource-usage-monitor/index.md) |
| 4 | 바로가기 파일·점프리스트·최근 문서 | 보내기 전에 원본 파일을 연 흔적 | [바로가기 파일](/02-artifacts/file-folder-usage/lnk.md), [점프리스트](/02-artifacts/file-folder-usage/jump-lists.md), [최근 문서](/02-artifacts/file-folder-usage/recentdocs.md) |
| 5 | 열기·저장 대화상자 기록 | 파일을 고른 대화상자 흔적 | [열기·저장 대화상자 기록](/02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) |

## 분석 흐름

1. 사용자마다 설치된 메신저와 프로필 안 메신저 폴더를 정리합니다.
2. 메신저 폴더를 통째로 사본으로 확보합니다. 원본은 열지 않고 사본에서 작업합니다.
3. 대화 DB 를 읽을 수 있으면 조사 기간의 파일 전송 메시지를 찾습니다. 보낸 파일이 DB 에 어떤 모양으로 남는지는 메신저마다 다르므로 각 메신저 페이지를 따릅니다.
4. 대화 DB 가 암호화돼 있으면 먼저 [암호화 증거 다루기](/03-techniques/analysis/encrypted-evidence/index.md) 로 풀 수 있는지 봅니다.
5. 풀지 못하면 SRUM 네트워크 사용량에서 그 메신저 앱이 보낸 바이트 수(BytesSent)를 시간대별로 뽑습니다[1]. 표를 읽는 법은 [웹메일·웹하드로 올렸나](/04-scenarios/exfiltration/data-exfiltration/web-upload.md) 에서 다룹니다.
6. 송신량이 많은 시간대 앞뒤로 원본 파일을 연 흔적(바로가기 파일·점프리스트·최근 문서)이 있는지 맞춰 봅니다.
7. 브라우저에서 웹판 메신저를 썼다면 [웹메일·웹하드로 올렸나](/04-scenarios/exfiltration/data-exfiltration/web-upload.md) 순서로 봅니다.
8. 대화 상대 목록은 [누구와 연락을 주고받았나](/04-scenarios/activity/communication-reconstruction.md) 에서 정리합니다.

## 흔한 오판

1. **받은 파일 폴더에 있는 파일을 보낸 파일로 봅니다.** 받은 파일 폴더는 받은 쪽 흔적입니다. 보낸 기록은 대화 DB 에서 찾습니다.
2. **받은 파일 폴더가 없으니 메신저로 파일을 주고받지 않았다고 봅니다.** 관찰한 PC 에는 카카오톡이 있었지만 `Documents\카카오톡 받은 파일` 폴더가 없었습니다(관찰). 폴더가 없다는 것만으로 결론을 내리지 않습니다.
3. **SRUM 송신량을 파일 전송 증거로 씁니다.** SRUM 네트워크 사용량 표에는 목적지 주소나 파일 이름 칸이 없습니다[1]. 송신량은 그 앱이 그 시간대에 보낸 양일 뿐입니다.
4. **클래식 Teams 폴더만 보고 Teams 를 안 썼다고 봅니다.** 관찰한 PC 의 새 Teams 는 `Packages\MSTeams_8wekyb3d8bbwe` 아래에 있었습니다(관찰).
5. **대화 DB 를 못 읽었으니 보낸 기록이 없다고 적습니다.** 읽지 못한 것과 기록이 없는 것은 다릅니다. 보고서에는 "암호화로 읽지 못했다" 고 적습니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 카카오톡으로 고객 명단을 외부에 보냈습니다."
- 쓸 문장: "사용자 ○○ 의 프로필에 카카오톡 데이터 폴더가 있습니다. 대화 DB 는 암호화돼 있어 이번 분석에서 내용을 읽지 못했습니다. SRUDB.dat 네트워크 사용량 표에는 ○○(UTC) 에 기록된 행에 카카오톡 앱이 ○○ 바이트를 보냈다고 적혀 있습니다. 같은 시간대에 사용자 ○○ 가 ○○ 파일을 연 바로가기 파일이 있습니다. 이 기록만으로 무엇을 누구에게 보냈는지는 정할 수 없습니다."

## 함께 볼 페이지

- [카카오톡 PC](/02-artifacts/messengers/kakaotalk-pc/index.md) · [네이트온](/02-artifacts/messengers/nateon.md) · [라인](/02-artifacts/messengers/line.md) · [마이크로소프트 팀즈](/02-artifacts/messengers/teams.md) · [슬랙](/02-artifacts/messengers/slack.md) · [줌](/02-artifacts/messengers/zoom.md) — 메신저별 저장 위치와 대화 DB 입니다.
- [텔레그램](/02-artifacts/messengers/telegram.md) · [왓츠앱 데스크톱](/02-artifacts/messengers/whatsapp-desktop.md) · [디스코드](/02-artifacts/messengers/discord.md) · [시그널](/02-artifacts/messengers/signal.md) · [위챗](/02-artifacts/messengers/wechat.md) · [스카이프](/02-artifacts/messengers/skype.md) — 같은 내용을 다루는 다른 메신저 페이지입니다.
- [크롬 계열 앱 공통 구조](/01-foundations/app-mail-data/chromium-electron-webview2/index.md) · [SQLite 데이터베이스](/01-foundations/database-log-formats/sqlite/index.md) · [LevelDB 저장소](/01-foundations/database-log-formats/leveldb.md) — 대화 DB 를 열 때 함께 보는 저장 형식 페이지입니다.
- [암호화 증거 다루기](/03-techniques/analysis/encrypted-evidence/index.md) — 암호화된 대화 DB 를 다룹니다.
- [SRUM](/02-artifacts/execution/system-resource-usage-monitor/index.md) · [웹메일·웹하드로 올렸나 (Web Upload)](/04-scenarios/exfiltration/data-exfiltration/web-upload.md) — 앱별 송신량을 읽는 법입니다.
- [스마트폰으로 옮겼나 (MTP·Phone Link)](/04-scenarios/exfiltration/data-exfiltration/mtp-phone-link.md) — 파일을 휴대폰으로 옮긴 경우입니다.

## 참고 문헌

1. libyal esedb-kb, "System Resource Usage Monitor (SRUM)" — https://raw.githubusercontent.com/libyal/esedb-kb/main/documentation/System%20Resource%20Usage%20Monitor%20(SRUM).asciidoc
