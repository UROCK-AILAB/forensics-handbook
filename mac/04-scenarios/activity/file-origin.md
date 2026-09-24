---
title: "이 파일은 어디서 왔나"
parent: "시나리오 · 행위 재구성"
nav_order: 2310
---

# 이 파일은 어디서 왔나 (File Origin)

## 조사 질문

이 맥에 있는 파일이 어디서 들어왔는지 묻습니다. 웹에서 받았는지, 메일·메시지 첨부였는지, 에어드롭으로 받았는지, 외장·네트워크 볼륨에서 가져왔는지를 가리고, 웹에서 받았다면 어느 URL 에서 어떤 앱으로 언제 받았는지까지 좁힙니다. 침해 사고에서는 악성 파일이 들어온 경로를, 유출·반입 조사에서는 문서가 외부에서 들어왔는지를 확인하는 데 씁니다.

인터넷에서 받은 파일에는 격리 속성 (quarantine)이 붙고, 사용자별 격리 이벤트 DB에도 같은 사건이 적힙니다. 브라우저는 여기에 더해 파일에 출처 URL 속성을 붙이고 자기 다운로드 기록을 따로 남깁니다. 그래서 파일 자체의 확장 속성, 격리 이벤트 DB, 브라우저 다운로드 기록 세 곳을 서로 이어 보는 방식으로 조사합니다. 각 기록의 구조는 아티팩트 페이지에서 다루고, 이 페이지는 이어 보는 순서와 판단만 다룹니다.

## 먼저 확인할 것

OS 버전은 [OS 버전과 설치 기록](../../02-artifacts/system-account/os-version-install-history.md)에서 확인합니다. 출처 흔적과 관련된 버전 차이는 다음과 같습니다.

| 항목 | 버전 |
|---|---|
| `kMDItemWhereFroms` 속성 | 10.4 부터(Apple 보관 문서) [7] |
| 공증을 기본으로 요구 | 10.15 Catalina [5] |
| 앱 번들의 `com.apple.provenance` 속성 | 13 Ventura 부터 [2] |
| 격리된 미공증 앱의 첫 실행 거부 | 15 Sequoia [6] |

시간대는 [시간대와 시계 설정](../../02-artifacts/system-account/time-zone.md)에서 확인합니다. 한 번 받은 파일 하나에 시각 기준이 여럿 섞여서 격리 속성은 유닉스 시각을 16진 문자열로, 격리 이벤트 DB는 맥 절대 시각으로, 크롬 계열 다운로드 기록은 1601-01-01 기준 마이크로초로, 파이어폭스는 1970 기준 마이크로초로 적습니다 [1][3][12][13]. 모두 한 기준으로 바꿔 적어 둡니다([맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md)).

격리 이벤트 DB와 브라우저 프로필은 사용자마다 따로 있어서, 파일이 있는 홈 폴더의 사용자부터 봅니다. 수집 범위에서는 파일의 확장 속성을 보존했는지가 가장 중요합니다. 확장 속성은 NFS 로 복사하면 모두 벗겨지고, FAT·exFAT 같은 맥 고유가 아닌 파일 시스템으로 복사하면 숨은 그림자 파일로 따로 떨어질 수 있어서 [11], 수집 과정에서 속성이 빠지지 않았는지 확인합니다([맥 증거 확보](../../03-techniques/process-acquisition/evidence-acquisition/index.md)).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 파일의 `com.apple.quarantine` 속성 | `플래그;16진 시각;앱 이름;UUID` | [격리 속성과 다운로드 기록](../../02-artifacts/filesystem/quarantine/index.md) |
| 2 | 격리 이벤트 DB `~/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2` 의 `LSQuarantineEvent` 표 | 받은 앱, DataURL, OriginURL, 보낸 사람, 격리 종류 | [격리 속성과 다운로드 기록](../../02-artifacts/filesystem/quarantine/index.md) |
| 3 | 파일의 `com.apple.metadata:kMDItemWhereFroms` 속성 | 출처 URL 배열(크롬은 원본 URL, referrer) | [다운로드 출처 속성](../../02-artifacts/filesystem/where-froms.md) |
| 4 | 사파리 `~/Library/Safari/Downloads.plist` | `DownloadEntryURL`, `DownloadEntryPath`, 추가·완료 시각 | [사파리](../../02-artifacts/browsers/safari/index.md) |
| 5 | 크롬 계열 `History` 의 `downloads`·`downloads_url_chains` 표 | `target_path`, `tab_url`, `referrer`, URL 연쇄 | [크롬·엣지·웨일](../../02-artifacts/browsers/chromium/index.md) |
| 6 | 파이어폭스 `places.sqlite` 의 `moz_historyvisits.visit_type = 7` | 다운로드 방문 | [파이어폭스](../../02-artifacts/browsers/firefox.md) |
| 7 | 메일 첨부 `~/Library/Containers/com.apple.mail/Data/Library/Mail Downloads/`, 메시지 첨부 `~/Library/Messages/Attachments/` | 메일·메시지로 받은 파일 | [애플 메일](../../02-artifacts/mail/apple-mail/index.md), [메시지](../../02-artifacts/messengers/imessage/index.md) |
| 8 | 에어드롭으로 받은 파일 | 기본 다운로드 폴더에 들어오고 격리 속성이 붙음 | [에어드롭](../../02-artifacts/external-devices/airdrop.md) |
| 9 | 최근 항목 북마크의 볼륨 이름·UUID | 외장·네트워크 볼륨에서 온 파일 | [최근 항목](../../02-artifacts/file-folder-usage/recent-items/index.md) |
| 10 | 앱 번들의 `com.apple.provenance` 와 ExecPolicy | 앱이 들어온 기록 | [실행 정책 평가 기록](../../02-artifacts/execution/execpolicy-gatekeeper.md) |
| 11 | 스포트라이트 색인 `.Spotlight-V100/Store-V2/` | 색인에 남은 `kMDItemWhereFroms` 등 속성 | [스포트라이트](../../02-artifacts/file-folder-usage/spotlight/index.md) |

1~3번은 파일과 붙어 다니는 기록이라 먼저 보고, 4~6번은 받은 앱이 정해진 뒤 그 브라우저에서 찾습니다. 파일에 속성이 없으면 7~11번으로 넘어갑니다. 메시지 첨부는 `chat.db` 의 `attachment` 표 `filename`·`transfer_name` 칸과 함께 봅니다 [17]. 스포트라이트 색인에서 지운 파일의 레코드가 남는지는 확인하지 못했습니다.

### 격리 기록을 이어 읽기

격리 속성의 마지막 칸 UUID 는 격리 이벤트 DB의 `LSQuarantineEventIdentifier` 와 같은 값이라서, 파일과 DB 행을 잇는 열쇠가 됩니다 [1][3]. 플래그 비트는 0x0001 DOWNLOAD, 0x0002 SANDBOX, 0x0004 HARD, 0x0040 USER_APPROVED 이고, 0x0080 의 뜻은 확인하지 못했습니다 [4]. 격리 종류는 WebDownload, OtherDownload, EmailAttachment, InstantMessageAttachment, CalendarEventAttachment, OtherAttachment 상수로 나뉘지만 DB의 `LSQuarantineTypeNumber` 숫자와 어떻게 대응하는지는 확인하지 못했습니다 [14].

크롬은 격리 속성의 DataURL 에 원본 URL 을, OriginURL 에 referrer 를 넣고, `kMDItemWhereFroms` 를 먼저 쓴 뒤 격리 속성을 씁니다. URL 이 http·https 면 WebDownload, 아니면 OtherDownload 로 적습니다 [8]. 압축 파일을 풀면 안에서 나온 파일에도 격리 속성이 이어져서 [1], 압축 파일과 풀린 파일을 같은 다운로드 사건으로 묶어 봅니다.

앱이라면 macOS 13 Ventura 이후 격리를 통과한 앱 번들에 `com.apple.provenance` 속성이 붙습니다. 이 속성은 보통 11바이트이고, 그 안의 8바이트 리틀엔디언 정수가 ExecPolicy 의 `provenance_tracking` 표 기본 키 `pk` 와 같습니다 [2].

### 속성이 파일을 따라가는지

copyfile 의 표를 보면 `com.apple.metadata:*` 속성에는 P·S 플래그가, `com.apple.quarantine` 에는 P·C·S 플래그가 붙어 있습니다 [9]. P 는 공유 의도로 복사할 때 보존하지 않는다는 뜻이라서 [9], 공유를 거쳐 넘어온 파일에는 두 속성이 없을 수 있습니다. 격리 속성은 시스템 무결성 보호 (SIP) 대상이 아니지만 `com.apple.provenance` 와 `com.apple.macl` 은 보호될 수 있고, 격리 속성은 코드 서명의 CDHash 계산에 들어가지 않습니다 [11]. 필자의 해석으로는 격리 속성을 지워도 서명 검증에서는 드러나지 않을 것으로 보여서, 속성이 없는 앱은 격리 이벤트 DB와 ExecPolicy 로 따로 확인합니다.

## 분석 흐름

1. 대상 파일의 확장 속성을 모두 뽑고, `com.apple.quarantine` 을 플래그·시각·앱 이름·UUID 로 나눕니다.
2. UUID 로 격리 이벤트 DB에서 같은 행을 찾아 DataURL·OriginURL·받은 앱·시각을 확인합니다.
3. `kMDItemWhereFroms` 의 URL 이 2단계의 URL 과 같은지 봅니다. 이 속성은 출처 문자열을 담은 bplist 배열이고, 크롬이라면 첫 값이 원본 URL, 둘째 값이 referrer 입니다 [8][10].
4. 받은 앱이 브라우저라면 그 브라우저 다운로드 기록에서 `DownloadEntryPath`·`target_path` 로 같은 파일을 찾고, 크롬 계열은 `downloads_url_chains` 로 리디렉션을 거친 URL 연쇄까지 봅니다.
5. 파일에 속성이 없으면 메일·메시지 첨부 폴더, 에어드롭 받은 폴더, 최근 항목 북마크의 볼륨 정보에서 같은 이름을 찾습니다.
6. 앱이라면 `com.apple.provenance` 로 ExecPolicy 행을 찾아 격리 기록과 맞춰 봅니다.
7. 1~6단계의 시각을 한 기준으로 바꿔 한 [타임라인](../../03-techniques/analysis/timeline/index.md)에 올리고, 같은 시각대에 브라우저 방문 기록이 있는지 [웹 사용 행위 재구성](web-activity.md)의 방법으로 확인합니다.

## 흔한 오판

- **속성이 없으면 인터넷에서 받지 않았다고 보는 경우.** 크롬 코드 주석에 따르면 시크릿 모드로 받은 파일은 URL 이 비어 있을 수 있고 크롬은 빈 URL 을 넣지 않아서, `kMDItemWhereFroms` 가 비거나 없을 수 있습니다(실물로 확인한 동작은 아님) [8]. 공유 의도로 복사하거나 NFS 를 거친 파일도 속성이 빠질 수 있고 [9][11], 로컬에서 빌드해 ad hoc 서명한 앱은 처음부터 격리되지 않습니다 [6].
- **명령줄 도구로 받은 파일에는 격리 속성이 없다고 단정하는 경우.** curl·scp 같은 도구로 받은 파일에 격리 속성이 붙는지는 이 핸드북이 확인하지 못했습니다. 테스트 기기에서 재현하기 전에는 근거로 쓰지 않습니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).
- **브라우저 기록을 지웠으니 다운로드 흔적이 없다고 보는 경우.** 사파리 "기록 지우기"는 다운로드 목록을 지우지만 받은 파일은 남기고, 개인 정보 보호 창에서 받은 파일도 목록에는 없지만 파일은 남습니다 [15][16]. 격리 이벤트 DB 행이 파일 삭제나 브라우저 기록 삭제 때 함께 지워지는지는 확인하지 못했습니다.
- **DataURL 과 OriginURL 을 바꿔 읽는 경우.** 크롬 기준으로 DataURL 이 파일을 실제로 받은 주소이고 OriginURL 은 그 링크가 있던 페이지입니다 [8].
- **풀린 파일을 따로 받은 파일로 세는 경우.** 압축을 풀면 격리 속성이 이어져서 [1], 풀린 파일의 격리 속성은 원래 압축 파일의 다운로드 사건을 가리킬 수 있습니다.

## 보고서 문장 예

> 파일 "○○.pkg" 의 격리 속성에는 받은 앱 "○○" 과 ○○○○년 ○월 ○일 ○시 ○분(UTC로 바꾼 시각)이 적혀 있고, 속성의 UUID 와 같은 값의 격리 이벤트 DB 행에는 DataURL "https://○○" 와 OriginURL "https://○○" 가 있습니다. 같은 파일의 `kMDItemWhereFroms` 속성에도 같은 URL 이 있습니다. 이 기록들로 파일을 받은 경로와 시각은 확인할 수 있지만, 사용자가 이 파일을 실행했는지는 이 기록만으로 정할 수 없습니다.

## 함께 볼 페이지

- [격리 속성과 다운로드 기록 (Quarantine)](../../02-artifacts/filesystem/quarantine/index.md) — 격리 속성과 DB의 구조
- [다운로드 출처 속성 (kMDItemWhereFroms)](../../02-artifacts/filesystem/where-froms.md) — 출처 URL 속성 읽는 법
- [웹 사용 행위 재구성 (Web Activity)](web-activity.md) — 받기 전후의 방문 기록
- [악성 코드는 어디서 들어왔나 (Initial Access)](../incident/initial-access.md) — 악성 파일이 들어온 경로
- [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../01-foundations/protection/codesign-notarization-sip.md) — 게이트키퍼와 공증

## 참고 문헌

1. Howard Oakley, "xattr: com.apple.quarantine, the quarantine flag" (2017-12-11) — https://eclecticlight.co/2017/12/11/xattr-com-apple-quarantine-the-quarantine-flag/
2. Howard Oakley, "Ventura has changed app quarantine with a new xattr" (2023-03-13) — https://eclecticlight.co/2023/03/13/ventura-has-changed-app-quarantine-with-a-new-xattr/
3. mac_apt 격리 플러그인 quarantine.py (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/quarantine.py
4. WebKit 소스 QuarantineSPI.h — https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/PAL/pal/spi/mac/QuarantineSPI.h
5. Apple Support, "Safely open apps on your Mac" (102445) — https://support.apple.com/en-us/102445
6. Howard Oakley, "Gatekeeper and notarization in Sequoia" (2024-08-10) — https://eclecticlight.co/2024/08/10/gatekeeper-and-notarization-in-sequoia/
7. Apple, Spotlight Metadata Attributes Reference — Common Attributes (2014-07-15) — https://developer.apple.com/library/archive/documentation/CoreServices/Reference/MetadataAttributesRef/Reference/CommonAttrs.html
8. Chromium 소스 quarantine_mac.mm — https://raw.githubusercontent.com/chromium/chromium/main/components/services/quarantine/quarantine_mac.mm
9. Apple 오픈소스 copyfile, xattr_flags.c·xattr_flags.h — https://raw.githubusercontent.com/apple-oss-distributions/copyfile/main/xattr_flags.c , https://raw.githubusercontent.com/apple-oss-distributions/copyfile/main/xattr_flags.h
10. Howard Oakley, "xattr: com.apple.metadata:kMDItemWhereFroms, origin of downloaded file" (2017-12-21) — https://eclecticlight.co/2017/12/21/xattr-com-apple-metadatakmditemwherefroms-origin-of-downloaded-file/
11. Howard Oakley, "The secret life of the xattr" (2026-04-24) — https://eclecticlight.co/2026/04/24/the-secret-life-of-the-xattr/
12. Chromium 소스 — components/history/core/browser/download_database.cc — https://chromium.googlesource.com/chromium/src/+/HEAD/components/history/core/browser/download_database.cc
13. Mozilla 소스 — toolkit/components/places/nsINavHistoryService.idl — https://searchfox.org/mozilla-central/source/toolkit/components/places/nsINavHistoryService.idl
14. Apple Developer Documentation, Launch Services — https://developer.apple.com/tutorials/data/documentation/coreservices/launch_services.json
15. Apple Support, "Clear your browsing history in Safari on Mac" — https://support.apple.com/guide/safari/clear-your-browsing-history-sfri47acf5d6/mac
16. Apple Support, "Browse privately in Safari on Mac" — https://support.apple.com/guide/safari/browse-privately-ibrw1069/mac
17. imessage_database, Attachment (docs.rs) — https://docs.rs/imessage-database/latest/imessage_database/tables/attachment/struct.Attachment.html
