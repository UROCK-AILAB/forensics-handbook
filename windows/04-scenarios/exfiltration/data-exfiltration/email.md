---
title: "메일로 밖에 보냈나"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 3610
---

# 메일로 밖에 보냈나 (Email)

이 페이지는 PC 에 설치한 메일 프로그램으로 자료를 첨부해 보냈는지 확인하는 순서를 다룹니다. 브라우저로 웹메일에 들어가 보낸 경우는 [웹메일·웹하드로 올렸나 (Web Upload)](web-upload.md) 에서 다룹니다.

아래 폴더 구성은 새 Outlook 만 쓰고 클래식 Outlook 은 쓰지 않은 Windows 11 Home 25H2(빌드 26200.9457) 기준입니다.

## 조사 질문

- 이 PC 의 메일 프로그램으로 자료를 첨부해 밖으로 보냈습니까?
- 어느 계정으로, 누구에게, 언제, 어떤 첨부를 보냈습니까?
- PC 에 남은 것만으로 어디까지 말할 수 있고, 서버 쪽 자료가 더 필요합니까?

## 먼저 확인할 것

| 확인할 것 | 이유 |
|---|---|
| 메일 프로그램 | 프로그램마다 메일을 두는 곳이 다릅니다. [설치 프로그램](../../../02-artifacts/system-account/uninstall.md) 과 [스토어 앱 설치 목록](../../../02-artifacts/system-account/appx-staterepository.md) 에서 클래식 Outlook, 새 Outlook, 썬더버드, Windows 메일 앱이 있는지 봅니다. |
| 계정 종류 | POP·IMAP 계정은 모든 Outlook 정보를 .pst 에 둡니다[1]. 다른 계정 종류와 .ost 는 [아웃룩](../../../02-artifacts/mail/outlook/index.md) 에서 다룹니다. |
| 사용자 | 메일 데이터는 사용자 프로필 안에 있습니다. 사용자마다 따로 찾습니다. |
| 시간대 | 메일 시각과 PC 흔적 시각을 같은 기준으로 맞춥니다([시간대 설정](../../../02-artifacts/system-account/time-zone.md)). |
| 수집 범위 | .pst·.ost 파일, 새 Outlook 폴더, 사용자 프로필 전체를 확보합니다. PC 에 메일 본문이 없으면 서버 쪽 자료를 따로 확보해야 하는지 판단합니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | Outlook 데이터 파일 (.pst·.ost) | 보낸 메일, 받는 사람, 첨부, 연락처 | [아웃룩](../../../02-artifacts/mail/outlook/index.md) |
| 2 | 새 Outlook 폴더 | 새 Outlook 을 쓴 흔적, PC 에 남은 캐시 | [새 Outlook](../../../02-artifacts/mail/new-outlook.md) |
| 3 | 다른 메일 프로그램 | 썬더버드·Windows 메일 앱·옛 메일 프로그램의 메일함 | [썬더버드](../../../02-artifacts/mail/thunderbird.md), [Windows 메일 앱](../../../02-artifacts/mail/hxstore.md), [옛 윈도 메일 프로그램](../../../02-artifacts/mail/outlook-express-windows-live-mail.md) |
| 4 | 메일 헤더 | 실제로 보낸 시각과 거친 서버 | [메일 헤더 분석](../../../03-techniques/analysis/email-header-analysis.md) |
| 5 | 바로가기 파일·최근 문서 | 첨부하기 전에 원본 파일을 연 흔적 | [바로가기 파일](../../../02-artifacts/file-folder-usage/lnk.md), [최근 문서](../../../02-artifacts/file-folder-usage/recentdocs.md) |
| 6 | SRUM 네트워크 사용량 | 메일 프로그램이 그 시간대에 보낸 양 | [SRUM](../../../02-artifacts/execution/system-resource-usage-monitor/index.md) |

## 클래식 Outlook

### .pst 에 든 것

.pst 파일에는 Outlook 메시지와 연락처·약속·작업·메모·일지 같은 항목이 들어 있어서[1], 보낸 메일뿐 아니라 받는 사람의 연락처 항목도 함께 봅니다. 메시지 속성의 이름과 뜻은 [MAPI 속성](../../../01-foundations/app-mail-data/mapi-property.md) 에서 다룹니다.

### 보관 파일 (archive.pst) 기본 위치

| Outlook 판 | archive.pst 기본 위치 |
|---|---|
| Outlook 2016 이후 | `C:\Users\<사용자>\Documents\Outlook Files\archive.pst` |
| 그 전 판 | `C:\Users\<사용자>\AppData\Local\Microsoft\Outlook\archive.pst` |

(표는 [1]. 위치는 archive.pst 기준입니다.)

- 다른 .pst 가 이 두 폴더에만 있다고 가정하지 않습니다. 디스크 전체에서 .pst·.ost 확장자로 찾습니다.
- 외부 장치나 다른 폴더에 있던 .pst 를 연 흔적도 바로가기 파일에서 찾습니다. .pst 는 메일을 통째로 옮기는 수단이 될 수 있습니다.
- 클래식 Outlook 을 쓰지 않은 PC 에는 `%LOCALAPPDATA%\Microsoft\Outlook` 과 `Documents\Outlook Files` 폴더가 모두 없을 수 있습니다.

### 보낸 편지함과 지운 메일

보낸 편지함, 지운 메일, 첨부를 연 임시 폴더는 [아웃룩](../../../02-artifacts/mail/outlook/index.md) 허브와 그 하위 페이지에서 다룹니다. 이 페이지는 그 결과를 유출 판단에 쓰는 방법만 다룹니다.

## 새 Outlook

### .pst 지원

새 Outlook 은 .pst 지원이 제한적입니다[1]. .pst 파일 안에서 메일과 폴더를 옮기거나 복사하거나 지우는 일과 편지함과 .pst 사이의 끌어 놓기는 되고[1], 편지함의 메일·일정·연락처·작업을 .pst 로 내보내는 기능도 들어왔지만[1], .pst 를 편지함으로 한꺼번에 가져오는 기능은 아직 없고 앞으로 들어올 기능입니다[1]. 새 Outlook 을 쓰는 PC 에서도 메일을 .pst 로 옮길 수 있으므로 새 Outlook PC 에서도 .pst 파일을 찾습니다.

### PC 에 남는 폴더

- 새 Outlook 을 쓰는 PC 에는 새 Outlook 패키지 `Microsoft.OutlookForWindows_8wekyb3d8bbwe` 가 있습니다.
- `%LOCALAPPDATA%\Microsoft\Olk\` 아래에 `EBWebView`, `logs`, `UserSettings.json` 등이 있습니다.
- `Olk\EBWebView\Default` 는 WebView2 프로필 모양입니다. `History`, `Network\Cookies`, `Local Storage`, `Session Storage`, `Cache` 등이 있고, `IndexedDB` 는 없을 수 있습니다.
- WebView2 프로필 파일을 읽는 법은 [크롬 계열 앱 공통 구조](../../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에서 다룹니다.
- 새 Outlook 이 메일 본문과 첨부를 PC 어디에 얼마나 남기는지는 실제 기기에서 확인해야 합니다. 메일은 서버에 있고 PC 에는 캐시만 남을 수 있습니다. 자세한 내용은 [새 Outlook](../../../02-artifacts/mail/new-outlook.md) 을 봅니다.

## 분석 흐름

1. 사용자마다 어떤 메일 프로그램과 어떤 종류의 계정을 썼는지 정리합니다.
2. 디스크 전체에서 .pst·.ost 를 찾고, 위 기본 위치와 새 Outlook 폴더도 확인합니다.
3. 메일 파일은 사본으로 엽니다. 보낸 메일마다 보낸 시각, 받는 사람, 첨부 이름·크기를 표로 만듭니다. 지운 메일을 되살리는 법은 [아웃룩](../../../02-artifacts/mail/outlook/index.md) 을 따릅니다.
4. 첨부를 꺼내 PC 안의 원본 파일과 해시로 맞춥니다([해시셋 대조와 유사 해시](../../../03-techniques/analysis/hash-set-fuzzy-hash.md)).
5. 받는 쪽 사본이나 서버 사본을 확보했다면 헤더로 실제 보낸 시각과 거친 서버를 확인합니다([메일 헤더 분석](../../../03-techniques/analysis/email-header-analysis.md)).
6. 새 Outlook 만 쓴 PC 라면 PC 에 남은 캐시의 범위를 먼저 보고, 서버 쪽 자료가 필요한지 판단합니다.
7. 보내기 전후에 원본 파일을 연 흔적(바로가기 파일·최근 문서)과 SRUM 의 송신량을 보낸 시각 앞뒤로 맞춰 봅니다. SRUM 으로 알 수 있는 범위는 [웹메일·웹하드로 올렸나](web-upload.md) 에서 다룹니다.

## 흔한 오판

1. **보낸 편지함에 없으니 보내지 않았다고 봅니다.** 보낸 뒤 지웠거나, 서버에만 있거나, 다른 PC·웹메일로 보냈을 수 있습니다.
2. **.pst 안에 있으니 이 PC 에서 보냈다고 봅니다.** .pst 는 파일이라 다른 PC 에서 복사해 올 수 있습니다. 메일 헤더와 계정 설정을 함께 봅니다.
3. **첨부를 연 임시 폴더 흔적을 보낸 기록으로 씁니다.** 이 흔적의 뜻은 [아웃룩](../../../02-artifacts/mail/outlook/index.md) 에서 확인하고, 보낸 메일 자체와 따로 적습니다.
4. **새 Outlook PC 에 메일이 적으니 메일을 적게 썼다고 봅니다.** PC 에는 캐시만 남을 수 있습니다. PC 에 없는 것은 "PC 에서 찾지 못했다" 로만 적습니다.
5. **외부 주소로 보냈으니 유출이라고 단정합니다.** 받는 사람이 본인의 다른 주소인지, 업무 상대인지 따로 확인합니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 경쟁사에 메일로 기밀을 넘겼습니다."
- 쓸 문장: "사용자 ○○ 의 프로필에서 찾은 .pst 파일의 보낸 편지함에 ○○(UTC) 에 ○○ 주소로 보낸 메일이 있습니다. 이 메일의 첨부 ○○ 는 PC 안 ○○ 경로의 파일과 SHA-256 해시가 같습니다. 이 기록은 해당 파일이 첨부된 메일이 이 .pst 의 보낸 편지함에 있음을 보여 줍니다. 메일이 실제로 받는 사람에게 닿았는지는 서버 또는 받는 쪽 자료로 확인해야 합니다."

## 함께 볼 페이지

- [아웃룩](../../../02-artifacts/mail/outlook/index.md) — .pst·.ost 구조, 보낸 편지함, 지운 메일, 첨부 임시 폴더입니다.
- [새 Outlook](../../../02-artifacts/mail/new-outlook.md) · [크롬 계열 앱 공통 구조](../../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) — 새 Outlook 폴더를 읽는 법입니다.
- [썬더버드](../../../02-artifacts/mail/thunderbird.md) · [Windows 메일 앱](../../../02-artifacts/mail/hxstore.md) · [옛 윈도 메일 프로그램](../../../02-artifacts/mail/outlook-express-windows-live-mail.md) — 다른 메일 프로그램입니다.
- [인터넷 메일 형식](../../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) · [MAPI 속성](../../../01-foundations/app-mail-data/mapi-property.md) — 메일과 첨부의 저장 형식입니다.
- [메일 헤더 분석](../../../03-techniques/analysis/email-header-analysis.md) — 보낸 시각과 경로를 헤더에서 읽습니다.
- [웹메일·웹하드로 올렸나 (Web Upload)](web-upload.md) — 브라우저로 보낸 경우입니다.
- [누구와 연락을 주고받았나](../../activity/communication-reconstruction.md) — 메일 상대를 정리합니다.
- [개인정보 파일이 어디 있고 밖으로 나갔나](../pii-exposure.md) — 첨부가 개인정보 파일일 때 함께 봅니다.

## 참고 문헌

1. Microsoft 지원, "Introduction to Outlook Data Files (.pst and .ost)" — https://support.microsoft.com/en-us/office/introduction-to-outlook-data-files-pst-and-ost-222eaf92-a995-45d9-bde2-f331f60e2790
