# 누구와 연락을 주고받았나 (Communication Reconstruction)

PC 한 대를 두고 "이 사용자가 누구와, 언제, 무엇을 주고받았나" 를 묻는 조사를 다룹니다. 연락 수단은 메일 프로그램, 메신저, 브라우저로 쓰는 웹메일까지 여러 가지이고 수단마다 데이터가 남는 곳이 다릅니다. 이 페이지는 어떤 연락 수단을 썼는지부터 가리고, 수단마다 어디를 보는지, 그 기록으로 어디까지 말할 수 있는지를 정리합니다.

프로그램마다의 파일 구조는 각 아티팩트 페이지에 있습니다. 이 페이지에서는 Outlook 데이터 파일의 위치만 Microsoft 문서로 확인해 적었습니다. 다른 프로그램의 위치와 형식은 링크한 페이지에서 확인합니다.

## 조사 질문

- 이 PC 에서 어떤 연락 수단을 썼습니까?
- 누구와 주고받았습니까? 언제부터 언제까지입니까?
- 본문과 첨부 파일은 무엇이었습니까?
- 지운 메일이나 대화가 있습니까?
- 이 연락 기록을 남긴 계정을 쓴 사람이 피조사자입니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | 옛 Windows 와 Windows 10·11 은 Outlook 데이터 파일의 기본 위치가 다릅니다[1]. [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 버전을 먼저 적습니다. |
| 시간대 | 메일 헤더, 프로그램 DB, 파일 시스템의 시각을 한 줄로 세우려면 시간대가 필요합니다. [시간대 설정](../../02-artifacts/system-account/time-zone.md) 을 읽습니다. Bias 값을 부호 있는 수로 읽는 법은 [이 파일을 누가 언제 열었나](file-access.md) 의 "먼저 확인할 것" 에 있습니다. |
| 사용자 | 메일·메신저 데이터는 사용자 프로필마다 따로 있습니다. [사용자 프로필 목록](../../02-artifacts/system-account/profilelist.md) 으로 SID 와 프로필 폴더를 짝지어 둡니다. |
| 설치된 연락 프로그램 | 어떤 프로그램을 설치했는지부터 봅니다. [설치 프로그램](../../02-artifacts/system-account/uninstall.md) 과 [스토어 앱 설치 목록](../../02-artifacts/system-account/appx-staterepository.md) 을 함께 봅니다. |
| 메일 계정 종류 | Outlook 은 계정 종류에 따라 쓰는 데이터 파일이 다릅니다. 아래 "Outlook 데이터 파일" 을 봅니다. |
| 수집 범위 | 사용자 프로필 폴더 전체(`Documents`, `AppData\Local`, `AppData\Roaming`)를 확보합니다. 지난 시점의 파일은 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 봅니다. 서버와 클라우드에만 있는 데이터는 PC 밖에서 따로 확보해야 합니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 설치 프로그램·실행 흔적 | 어떤 연락 수단을 썼는지 | [설치 프로그램](../../02-artifacts/system-account/uninstall.md) · [어떤 프로그램을 언제 실행했나](program-execution.md) |
| 2 | Outlook 데이터 파일(.pst·.ost) | 메일 본문·첨부·주고받은 상대 | [아웃룩](../../02-artifacts/mail/outlook/index.md) |
| 3 | 다른 메일 프로그램의 저장소 | 같은 내용 | [새 Outlook](../../02-artifacts/mail/new-outlook.md) · [썬더버드](../../02-artifacts/mail/thunderbird.md) · [Windows 메일 앱](../../02-artifacts/mail/hxstore.md) · [옛 윈도 메일 프로그램](../../02-artifacts/mail/outlook-express-windows-live-mail.md) |
| 4 | 따로 저장한 메일 파일 | 사용자가 꺼내 저장한 메일 | [인터넷 메일 형식](../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) · [MAPI 속성](../../01-foundations/app-mail-data/mapi-property.md) |
| 5 | 메신저 대화 저장소 | 대화 상대·메시지·주고받은 파일 | 아래 "메신저" 의 링크 |
| 6 | 휴대폰과 연결 앱 | 휴대폰 쪽 연락의 흔적 | [휴대폰과 연결](../../02-artifacts/messengers/phone-link.md) |
| 7 | 브라우저 기록·캐시 | 웹메일·웹 메신저를 쓴 흔적 | [웹 사용 행위 재구성](web-activity.md) · [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) |
| 8 | 받은 첨부 파일 | 연락으로 들어온 파일 | [이 파일은 어디서 왔나](file-origin.md) |

연락 수단 목록(1)을 먼저 만듭니다. 목록에 오른 프로그램의 저장소(2~6)를 보고, 브라우저(7)로 웹 쪽 연락을 채웁니다.

## Outlook 데이터 파일

Microsoft 문서가 적은 위치와 동작입니다.

| 파일 | 쓰는 계정 | 위치 |
|---|---|---|
| 개인 폴더 파일 (.pst) | POP 계정은 모든 정보를 이 파일에 저장합니다[1]. | Windows 10·11: `drive:\Users\<username>\Documents\Outlook Files` [1] |
| | | 옛 Windows: `drive:\Documents and Settings\<user>\Local Settings\Application Data\Microsoft\Outlook` [1] |
| 오프라인 폴더 파일 (.ost) | Exchange·Microsoft 365·Outlook.com 계정은 이 파일을 쓸 수 있습니다[1]. | `AppData\Local\Microsoft\Outlook` [1] |

.ost 는 다른 컴퓨터로 옮길 수 없고[1], 계정을 다시 추가하면 Outlook 이 .ost 를 새로 만듭니다[1]. 서명·서식 파일·사전 같은 다른 설정은 `AppData\Roaming\Microsoft\` 아래 폴더에 있습니다[1]. 이 문서는 새 Outlook for Windows 를 다루지 않으므로[1], 새 Outlook 은 [새 Outlook](../../02-artifacts/mail/new-outlook.md) 에서 따로 봅니다.

**조사에서 뜻하는 것.**

- Exchange 계정을 쓰는 PC 라도 `Documents\Outlook Files` 를 함께 봅니다. 이런 계정에 .pst 가 없다고 적은 원문은 찾지 못했습니다.
- .ost 는 계정을 다시 추가할 때 새로 생기므로 .ost 파일의 만든 시각은 계정을 처음 추가한 시각이 아닐 수 있습니다.
- .ost 를 다른 PC 의 Outlook 에 붙여 여는 방법은 쓸 수 없고, 파일을 직접 읽는 방법은 [아웃룩](../../02-artifacts/mail/outlook/index.md) 에서 봅니다.
- 서버와 동기화할 때 .ost 에서 무엇이 바뀌는지와 지운 항목을 되살리는 방법도 [아웃룩](../../02-artifacts/mail/outlook/index.md) 에서 다룹니다.
- 받는 사람 자동 완성 목록의 위치와 형식은 이번 자료로 확인하지 못했습니다. [아웃룩](../../02-artifacts/mail/outlook/index.md) 에서 확인합니다.

**메일 한 통에서 읽을 것.** 보낸 사람·받는 사람·날짜는 메일 헤더에서 읽습니다. 헤더를 읽는 법은 [메일 헤더 분석](../../03-techniques/analysis/email-header-analysis.md) 에 있습니다. Outlook 이 저장한 항목의 속성은 [MAPI 속성](../../01-foundations/app-mail-data/mapi-property.md) 에서 봅니다.

## 메신저

메신저 대화 저장소의 위치와 암호화 여부는 이번에 연 자료로 확인하지 못했습니다. 앱마다 따로 페이지가 있습니다.

- [카카오톡 PC](../../02-artifacts/messengers/kakaotalk-pc/index.md) · [네이트온](../../02-artifacts/messengers/nateon.md) · [라인](../../02-artifacts/messengers/line.md)
- [마이크로소프트 팀즈](../../02-artifacts/messengers/teams.md) · [슬랙](../../02-artifacts/messengers/slack.md) · [줌](../../02-artifacts/messengers/zoom.md) · [스카이프](../../02-artifacts/messengers/skype.md)
- [텔레그램](../../02-artifacts/messengers/telegram.md) · [시그널](../../02-artifacts/messengers/signal.md) · [왓츠앱 데스크톱](../../02-artifacts/messengers/whatsapp-desktop.md) · [위챗](../../02-artifacts/messengers/wechat.md) · [디스코드](../../02-artifacts/messengers/discord.md)

앱 페이지를 읽을 때 함께 볼 기반 구조입니다.

- 크롬 계열 엔진 위에 만든 앱은 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 를 먼저 봅니다.
- 대화를 SQLite 파일에 두는 앱은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 지운 행을 찾는 법을 봅니다.
- 저장소가 암호화돼 있으면 [암호화 증거 다루기](../../03-techniques/analysis/encrypted-evidence/index.md) 와 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 를 봅니다.

휴대폰 문자가 PC 에 남는지는 이번 자료로 확인하지 못했습니다. [휴대폰과 연결](../../02-artifacts/messengers/phone-link.md) 에서 확인합니다.

## 웹메일과 웹 메신저

브라우저로 쓴 연락은 메일 프로그램의 저장소에 없으므로 브라우저 방문 기록과 캐시에서 흔적을 찾습니다. PC 에서 본문을 얼마나 되살릴 수 있는지는 이번 자료로 확인하지 못했습니다. [웹 사용 행위 재구성](web-activity.md) 과 [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) 에서 봅니다. 시크릿 창으로 썼다면 [시크릿 모드로 무엇을 했나](private-browsing.md) 를 봅니다.

## 분석 흐름

1. Windows 버전·시간대·사용자를 정리합니다.
2. 설치 프로그램과 실행 흔적으로 연락 수단 목록을 만듭니다.
3. Outlook 을 썼다면 `Documents\Outlook Files` 와 `AppData\Local\Microsoft\Outlook` 을 둘 다 봅니다. 다른 위치에 둔 .pst 가 있는지 파일 시스템 전체에서 확장자로 찾습니다.
4. 데이터 파일은 사본으로 엽니다. 조사 대상 상대의 주소와 이름으로 메일을 찾습니다.
5. 지운 메일은 [아웃룩](../../02-artifacts/mail/outlook/index.md) 에 적힌 방법으로 찾습니다.
6. 목록에 오른 메신저마다 대화 저장소를 찾습니다. 앱 페이지를 따라 읽습니다.
7. 브라우저 기록에서 웹메일·웹 메신저 접속을 찾습니다.
8. 받은 첨부 파일이 디스크에 저장됐는지 찾습니다. 저장된 파일은 [이 파일은 어디서 왔나](file-origin.md) 를 따라 출처를 확인합니다.
9. 기록마다 시각이 UTC 인지 현지 시각인지 확인합니다. 모든 시각을 UTC 로 맞춰 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다.
10. 파일을 밖으로 보냈는지는 [자료를 밖으로 빼돌렸나](../exfiltration/data-exfiltration/index.md) 를 따라 따로 봅니다.
11. 그 시각에 계정을 쓴 사람은 [그 시각에 PC 를 쓴 사람이 누구인가](user-attribution.md) 를 따라 좁힙니다.

## 흔한 오판

1. **메일 계정 주소를 피조사자 본인으로 봅니다.** 기록은 어느 계정이 주고받았는지를 보여 줍니다. 그 계정을 누가 썼는지는 다른 기록으로 좁힙니다.
2. **.ost 의 만든 시각을 계정을 처음 쓴 시각으로 봅니다.** 계정을 다시 추가하면 Outlook 이 .ost 를 새로 만듭니다[1].
3. **Exchange 계정이면 .pst 는 없다고 봅니다.** 그렇게 적은 원문을 찾지 못했습니다. .pst 위치도 함께 봅니다.
4. **.ost 를 다른 PC 의 Outlook 에 붙여 보려 합니다.** Microsoft 는 .ost 를 다른 컴퓨터로 옮길 수 없다고 적었습니다[1].
5. **새 Outlook 을 기존 Outlook 의 위치에서 찾습니다.** 위치를 적은 Microsoft 문서는 새 Outlook 을 다루지 않습니다[1].
6. **PC 에 대화 기록이 없으니 연락하지 않았다고 봅니다.** 웹메일, 웹 메신저, 휴대폰, 서버에만 남은 기록은 PC 저장소에 없습니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 ○○ 와 ○월 ○일에 메일을 주고받았습니다."
- 쓸 문장: "사용자 ○○ 프로필의 `Documents\Outlook Files\○○.pst` 에서 ○○@○○ 주소와 주고받은 메일 ○통을 찾았습니다. 가장 이른 메일의 헤더 날짜는 ○○(UTC)이고 가장 늦은 메일은 ○○(UTC)입니다. 이 기록은 이 PC 의 Outlook 에 설정된 계정이 해당 주소와 메일을 주고받았음을 보여 줍니다. 이 계정을 쓴 사람은 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [아웃룩](../../02-artifacts/mail/outlook/index.md) · [새 Outlook](../../02-artifacts/mail/new-outlook.md) — Outlook 데이터 파일의 구조와 지운 항목입니다.
- [인터넷 메일 형식](../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) · [메일 헤더 분석](../../03-techniques/analysis/email-header-analysis.md) — 메일 한 통을 읽는 법입니다.
- [카카오톡 PC](../../02-artifacts/messengers/kakaotalk-pc/index.md) · [마이크로소프트 팀즈](../../02-artifacts/messengers/teams.md) · [텔레그램](../../02-artifacts/messengers/telegram.md) — 자주 만나는 메신저입니다. 나머지 앱은 "메신저" 절에 있습니다.
- [웹 사용 행위 재구성](web-activity.md) — 웹메일과 웹 메신저의 흔적입니다.
- [자료를 밖으로 빼돌렸나](../exfiltration/data-exfiltration/index.md) — 메일·메신저로 파일을 내보냈는지 봅니다.
- [그 시각에 PC 를 쓴 사람이 누구인가](user-attribution.md) — 계정에서 사람으로 좁힙니다.

## 참고 문헌

1. Microsoft 지원, "Find and transfer Outlook data files from one computer to another" (날짜 표시 없음) — https://support.microsoft.com/en-us/office/find-and-transfer-outlook-data-files-from-one-computer-to-another-0996ece3-57c6-49bc-977b-0d1892e2aacc
