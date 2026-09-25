---
title: "개인정보 파일이 어디 있고 밖으로 나갔나"
parent: "시나리오 · 정보 유출"
nav_order: 2530
---

# 개인정보 파일이 어디 있고 밖으로 나갔나 (PII Exposure)

## 조사 질문

이 맥에 개인정보 (PII, Personally Identifiable Information)가 담긴 파일이 어디에 얼마나 있고, 그중 무엇이 맥 밖으로 나갔을 수 있는지 묻습니다. 질문은 두 갈래라서, 먼저 개인정보가 있는 곳을 찾아 노출 범위를 정하고, 다음으로 그 파일이 나갈 수 있는 경로에 흔적이 있는지 봅니다. USB·에어드롭·클라우드·메일·메신저 같은 경로별 세부는 [자료를 밖으로 빼돌렸나](data-exfiltration/index.md) 허브와 그 하위 페이지에서 다루고, 이 페이지는 개인정보 파일을 찾는 방법과 두 갈래를 잇는 판단 흐름만 다룹니다.

개인정보는 문서 파일에만 있지 않고 메일·메시지·메모·아이폰 백업 안에도 들어 있습니다. 그래서 노출 범위를 셀 때는 사용자 문서 폴더와 함께 이런 앱 저장소도 목록에 넣습니다.

## 먼저 확인할 것

OS 버전과 시간대는 [OS 버전과 설치 기록](../../02-artifacts/system-account/os-version-install-history.md)과 [시간대와 시계 설정](../../02-artifacts/system-account/time-zone.md)에서 먼저 확인합니다. 스포트라이트 속성·메시지 DB·클라우드 DB는 시각을 적는 기준이 서로 달라서, 모든 시각을 한 기준으로 바꿔 적어 두어야 뒤에서 대조할 수 있습니다([맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md)).

사용자 범위는 누구의 홈 폴더를 볼지 정하는 일입니다. 아래에 나오는 저장소는 거의 모두 사용자 홈 아래에 있어서 계정마다 따로 봅니다([사용자 계정](../../02-artifacts/system-account/user-accounts/index.md)).

수집 범위에서는 켜져 있는 맥을 직접 조사하는지, 사본 이미지를 보는지를 먼저 정합니다. 스포트라이트 검색 명령 `mdfind`는 켜져 있는 맥에서 쓰는 방법이고, 사본 이미지에서는 색인 저장소를 공개 도구로 따로 읽습니다([라이브 대응](../../03-techniques/process-acquisition/live-response/index.md), [맥 증거 확보](../../03-techniques/process-acquisition/evidence-acquisition/index.md)). 기기를 잃어버렸거나 도난당한 사건이라면 저장 장치가 암호화돼 있었는지가 노출 판단의 출발점이 되고, 이 부분은 [파일볼트](../../01-foundations/protection/filevault/index.md) 페이지에서 확인합니다.

### 버전별 차이

macOS 10.15 이후에는 Documents·Downloads·Desktop·iCloud Drive·네트워크 볼륨이 보호 위치라서, 앱이 여기 있는 파일에 접근하려면 사용자가 동의해야 합니다. 이동식 볼륨도 사용자가 허락해야 앱이 접근할 수 있습니다 [2].

| 항목 | macOS 버전 | 출처 |
|---|---|---|
| Documents·Downloads·Desktop·iCloud Drive·네트워크 볼륨 접근에 사용자 동의 필요 | 10.15 이후 | [2] |
| 전체 디스크 접근 (Full Disk Access)이 필요한 앱은 사용자가 설정에서 직접 추가 | 10.13 이후 | [2] |
| 권한 설정 위치 "시스템 설정 → 개인정보 보호 및 보안 → 개인정보 보호" | 13 이후(그 전은 "시스템 환경설정") | [2] |
| 로그 가림 옵션을 쓰는 Swift `Logger`·`OSLogPrivacy` | 11 이후(그 전 버전은 `os_log()` 계열 함수) | [3][4] |

사용자가 준 동의의 기록 위치와 서비스 이름은 [개인 정보 보호 권한 (TCC)](../../02-artifacts/credentials/tcc/index.md) 페이지에서 다룹니다. TCC 기록으로는 어느 앱이 문서 폴더에 접근할 권한을 받았는지까지만 알 수 있고, 그 앱이 실제로 어떤 파일을 읽었는지는 알 수 없습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 사용자 문서 폴더(`~/Documents`·`~/Desktop`)와 휴지통(`~/.Trash`) | 개인정보 파일 원본이 있는 곳 | [휴지통](../../02-artifacts/file-folder-usage/trash.md) |
| 2 | 메일·메시지·메모·캘린더·아이폰 백업 | 파일 밖에 들어 있는 개인정보 | 아래 경로 표 |
| 3 | 스포트라이트 색인 | 이름·본문·메타데이터로 개인정보 파일 찾기 | [스포트라이트](../../02-artifacts/file-folder-usage/spotlight/index.md) |
| 4 | `kMDItemWhereFroms`와 격리 이벤트 DB | 파일을 어디서 받았나 | [다운로드 출처 속성](../../02-artifacts/filesystem/where-froms.md), [격리 속성과 다운로드 기록](../../02-artifacts/filesystem/quarantine/index.md) |
| 5 | 최근 항목·`kMDItemLastUsedDate`·FSEvents | 그 파일을 누가 언제 열거나 옮겼나 | [최근 항목](../../02-artifacts/file-folder-usage/recent-items/index.md), [파일 시스템 이벤트](../../02-artifacts/filesystem/fsevents/index.md) |
| 6 | TCC | 어느 앱이 보호 폴더에 접근할 권한을 받았나 | [개인 정보 보호 권한](../../02-artifacts/credentials/tcc/index.md) |
| 7 | 경로별 유출 흔적 | 같은 시간대에 열려 있던 나가는 경로 | [자료를 밖으로 빼돌렸나](data-exfiltration/index.md) |
| 8 | 통합 로그 | 시간대 보강(문자열 값은 가려질 수 있음) | [통합 로그에서 찾을 것](../../02-artifacts/logs/unified-log-events/index.md) |

사용자 파일의 수집 대상은 `~/Documents/*`(MacOSUserDocumentsDirectory), `~/Desktop/*`(MacOSUserDesktopDirectory), `~/.Trash/*`(MacOSUserTrashDirectory)입니다 [5]. 휴지통으로 옮긴 파일은 비우기 전이면 그대로 남아 있어서 휴지통도 찾는 범위에 넣습니다. ForensicArtifacts 정의에는 다운로드 폴더(`~/Downloads`) 항목이 없지만 [5], 다운로드 폴더도 10.15 이후 보호 위치라서 함께 봅니다.

### 개인정보가 들어 있는 앱 저장소

아래 표의 정의 이름은 ForensicArtifacts 수집 정의의 이름입니다 [5]. 각 저장소의 구조는 링크한 아티팩트 페이지에서 다룹니다.

| 저장소 | 경로 | 정의 이름 |
|---|---|---|
| 메시지 대화 | `~/Library/Messages/chat.db` | MacOSMessageChatSQLiteDatabaseFile |
| 메모 | `~/Library/Containers/com.apple.Notes/Data/Library/Notes/NotesV*.storedata` | MacOSNotesSQLiteDatabaseFile |
| 캘린더 캐시 | `~/Library/Calendars/Calendar Cache` | MacOSCalendarCacheSQLiteDatabaseFile |
| 메일 받는 사람 최근 목록 | `~/Library/Application Support/AddressBook/MailRecents-v4.abcdmr` | MacOSMailRecentContacts |
| 메일 첨부 저장 | `~/Library/Containers/com.apple.mail/Data/Library/Mail Downloads/*` | MacOSMailDownloadAttachments |
| 메일에서 연 첨부 | `~/Library/Mail/V[0-9]/MailData/OpenedAttachmentsV2.plist` | MacOSMailOpenedAttachments |
| 메일 목차 DB | `~/Library/Mail/V[0-9]/MailData/Envelope Index` | MacOSMailEnvelopIndex(정의의 철자 그대로) |
| 메일 IMAP·POP 사본 | `~/Library/Mail/V[0-9]/IMAP-*/*`, `~/Library/Mail/V[0-9]/POP-*/*` | MacOSMailIMAP, MacOSMailPOP |
| 사용자 키체인 | `~/Library/Keychains/*.keychain`, `~/Library/Keychains/*/keychain-2.db`, `~/Library/Keychains/*/user.db` | MacOSUserKeychainFile 등 |
| 아이폰 백업 | `~/Library/Application Support/MobileSync/Backup/*` | MacOSiOSBackup* |
| 아이클라우드 계정 | `~/Library/Application Support/iCloud/Accounts/*`, `~/Library/Preferences/MobileMeAccounts.plist` | MacOSiCloudAccounts, MacOSiCloudPreferences |

메일 폴더는 V2·V3·V5 가 알려져 있고, 정의의 `V[0-9]`는 한 자리 숫자만 맞는 패턴입니다 [5]. 그래서 이 패턴을 그대로 쓰는 수집 도구는 `V10` 같은 두 자리 폴더를 놓칠 수 있고, 수집 뒤에 `~/Library/Mail/` 아래 폴더 이름을 직접 확인합니다. 연락처 DB는 [연락처](../../02-artifacts/cloud-apps/contacts.md) 페이지를 봅니다. 각 저장소를 읽는 법은 [애플 메일](../../02-artifacts/mail/apple-mail/index.md), [메시지](../../02-artifacts/messengers/imessage/index.md), [메모](../../02-artifacts/cloud-apps/notes.md), [미리 알림과 캘린더](../../02-artifacts/cloud-apps/reminders-calendar.md), [아이폰·아이패드 연결](../../02-artifacts/external-devices/ios-devices/index.md), [키체인](../../01-foundations/protection/keychain/index.md), [아이클라우드 계정](../../02-artifacts/cloud-apps/icloud-account.md) 페이지에 있습니다.

### 스포트라이트로 찾기

켜져 있는 맥에서는 `mdfind`로 스포트라이트 메타데이터 값을 조회합니다 [1]. 검색 범위를 폴더로 좁히는 `-onlyin`, 경로 대신 개수만 내는 `-count`, 결과마다 NUL 문자를 붙여 `xargs -0`과 함께 쓰는 `-0`, 파일 이름만 찾는 `-name` 같은 옵션이 있습니다 [1]. 쿼리에서는 `==`·`!=`·`<`·`>=` 같은 비교와 `InRange()`, 값 뒤에 붙여 대소문자를 무시하는 `c`, 발음 구별 부호를 무시하는 `d`, `*` 와일드카드를 쓸 수 있고, 날짜에는 `$time.today(-3)` 같은 함수를 씁니다 [1].

아래는 [1]의 문법으로 만든 예라서, 실제 조사에 쓰기 전에 테스트 기기에서 결과를 확인합니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

```
# 문서 폴더에서 본문에 "고객"이 들어간 파일 개수
mdfind -onlyin ~/Documents -count 'kMDItemTextContent == "*고객*"c'

# 최근 사흘 동안 내용이 바뀐 파일을 경로 목록으로
mdfind -0 -onlyin ~/Desktop 'kMDItemFSContentChangeDate >= $time.today(-3)' | xargs -0 ls -l
```

본문 속성 `kMDItemTextContent`는 쿼리에는 쓸 수 있지만 값을 직접 읽어 낼 수는 없고, 자세한 성질은 [스포트라이트](../../02-artifacts/file-folder-usage/spotlight/index.md) 페이지에서 다룹니다. 이 밖에 `kMDItemKind`, `kMDItemAuthor`, `kMDItemCreator`, `kMDItemUserTags`도 쿼리에 쓸 수 있습니다 [1]. `mdfind`가 정규식을 지원하는지는 공개 자료에 나오지 않아서, 주민등록번호처럼 형식으로 찾아야 하는 개인정보는 사본 이미지에서 별도 도구로 검사합니다([콘텐츠 검색](../../03-techniques/analysis/content-search.md)).

스포트라이트는 색인된 파일만 찾을 수 있어서, 색인에서 뺀 폴더나 색인이 꺼진 볼륨, 암호를 건 문서의 본문은 결과에 나오지 않는다고 보는 편이 안전합니다. 볼륨의 색인 설정은 `/.Spotlight-V100/VolumeConfiguration.plist`와 `/.Spotlight-V100/Store-V1/VolumeConfig.plist`에 있고 [5], 그 안에서 제외 목록을 담는 키 이름은 검체에서 확인합니다.

### 파일마다 붙는 출처와 사용 흔적

개인정보 파일을 찾았으면 그 파일이 어디서 왔고 언제 열렸는지 봅니다. 확장 속성 `com.apple.metadata:kMDItemWhereFroms`에는 다운로드 URL이나 메일 첨부의 보낸 사람·제목이 남고, 인사·고객 관리 같은 사내 웹 시스템에서 내려받은 파일이라면 이 URL로 원천을 가려낼 수 있습니다([다운로드 출처 속성](../../02-artifacts/filesystem/where-froms.md)). 다운로드 격리 기록 DB는 `~/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2`이고, 예전 이름은 `com.apple.LaunchServices.QuarantineEvents`입니다 [5]. 최근 항목은 `~/Library/Preferences/com.apple.recentitems.plist`와 앱별 `~/Library/Preferences/*.LSSharedFileList.plist`에 남고 [5], 10.11 이후의 sfl 계열 파일은 [최근 항목](../../02-artifacts/file-folder-usage/recent-items/index.md) 페이지에서 다룹니다.

### 통합 로그의 가림 처리

통합 로그는 메시지에 끼워 넣은 값을 개인정보 보호 옵션에 따라 가리거나 보여 줍니다 [3][4]. 기본값으로는 정수·실수·불리언 값은 그대로 보이고, 동적 문자열과 복잡한 동적 객체는 가립니다 [4]. 가린 값은 `log show` 출력에 `<private>`로 나오는 것으로 알려져 있습니다. 개발자가 `%{public}s`로 표시하면 문자열도 보이고, `%{private}d`처럼 숫자를 가릴 수도 있습니다 [4]. 파일 이름·경로·계정 같은 값은 문자열이라서 로그에서 `<private>`로 나오는 경우가 많고, 유출된 파일 이름으로 통합 로그를 직접 검색하기 어려울 수 있습니다.

`mask.hash` 옵션을 쓰면 원래 값 대신 해시가 남아 같은 값이 나온 로그끼리 이어 볼 수 있지만, 해시는 프로세스마다 다릅니다 [4]. 그래서 해시를 비교해 같은 값이라고 말할 수 있는 범위는 한 프로세스 안입니다. 가린 값을 보이게 하는 설정이 이미 기록된 로그에도 적용되는지는 공개된 자료가 없어 검체로 확인해야 합니다. 로그 저장 형식은 [통합 로그 형식](../../01-foundations/data-formats/unified-log/index.md) 페이지에서 다룹니다.

## 분석 흐름

1. 사용자 문서 폴더·휴지통과 앱 저장소 표의 경로를 수집 범위에 넣고, 계정마다 개인정보가 있는 곳의 목록을 만듭니다.
2. 켜져 있는 맥이면 `mdfind`로, 사본 이미지면 색인 저장소와 별도 검색 도구로 개인정보 파일을 찾아 경로·이름·크기를 적습니다.
3. 찾은 파일마다 `kMDItemWhereFroms`와 격리 기록으로 원천을 확인하고, 최근 항목·`kMDItemLastUsedDate`·FSEvents로 누가 언제 열거나 옮겼는지 봅니다([이 파일을 누가 언제 열었나](../activity/file-access.md)).
4. 3단계의 시각 앞뒤로 USB 연결·클라우드 동기화·메일 첨부·에어드롭·인쇄 흔적을 찾습니다. 경로별로 볼 곳은 [자료를 밖으로 빼돌렸나](data-exfiltration/index.md) 허브에서 고릅니다.
5. 유출 경로 쪽에서 나온 파일 이름·크기·시각을 2단계 목록과 대조하고, 모두 한 [타임라인](../../03-techniques/analysis/timeline/index.md)에 올려 겹치는 시간대를 봅니다.
6. 파일을 지운 흔적이 보이면 [지운 파일의 흔적 찾기](../activity/deleted-file-traces.md)의 방법으로 이어서 봅니다.

흔적 하나로 "나갔다"를 증명하기는 어렵고, 나갈 수 있는 경로가 열려 있던 시간대에 그 파일을 열었다는 정황을 여러 흔적으로 묶어 판단합니다.

## 흔한 오판

- **TCC 권한을 파일을 읽은 증거로 보는 경우.** 권한 기록으로는 앱이 보호 폴더에 접근할 수 있었다는 사실까지만 알 수 있고, 어떤 파일을 읽었는지는 알 수 없습니다.
- **`mdfind` 결과를 전체 목록으로 보는 경우.** 색인에서 빠진 폴더·볼륨이나 암호를 건 문서는 결과에 나오지 않을 수 있어서, 사본 이미지에서 따로 검색한 결과와 맞춰 봅니다.
- **문서 폴더만 세는 경우.** 메일 첨부 저장 폴더·메시지·메모·아이폰 백업에도 개인정보가 있어서, 문서 폴더만 세면 노출 범위를 작게 잡게 됩니다.
- **통합 로그에 파일 이름이 없으면 그 파일을 다루지 않았다고 보는 경우.** 문자열 값은 기본으로 가려지기 때문에, 이름이 안 보인다는 사실만으로는 그 파일을 다뤘는지 말할 수 없습니다.
- **파일이 휴지통에 있으면 노출 범위에서 빼는 경우.** 비우기 전의 휴지통에는 파일이 그대로 남아 있습니다.

## 보고서 문장 예

> 사용자 ○○의 `~/Documents` 아래에서 고객 이름과 연락처가 적힌 "○○.xlsx" 파일을 찾았고, 이 파일의 `kMDItemWhereFroms`에는 사내 고객 관리 시스템 주소가 남아 있습니다. ○○○○년 ○월 ○일 ○시 ○분(UTC로 바꾼 시각)에 최근 항목에 이 파일을 연 기록이 있고, 같은 날 ○시 ○분에 외부 볼륨이 연결된 기록이 있습니다. 이 기록들만으로는 파일이 외부 볼륨으로 복사됐는지 정할 수 없습니다.

## 함께 볼 페이지

- [자료를 밖으로 빼돌렸나 (Data Exfiltration)](data-exfiltration/index.md) — 경로별 유출 흔적과 공통 판단 원칙
- [스포트라이트 (Spotlight)](../../02-artifacts/file-folder-usage/spotlight/index.md) — 색인 위치와 속성, 시각 기준
- [콘텐츠 검색 (Content Search)](../../03-techniques/analysis/content-search.md) — 사본 이미지에서 개인정보 형식을 찾는 방법
- [이 파일은 어디서 왔나 (File Origin)](../activity/file-origin.md) — 파일 원천을 가리는 흐름
- [개인 정보 보호 권한 (TCC)](../../02-artifacts/credentials/tcc/index.md) — 보호 폴더 접근 권한 기록

## 참고 문헌

1. SS64, "mdfind" — https://ss64.com/mac/mdfind.html
2. Apple Platform Security, "Controlling app access to files in macOS" — https://support.apple.com/guide/security/controlling-app-access-to-files-secddd1d86a6/web
3. Apple Developer Documentation, "OSLogPrivacy" — https://developer.apple.com/tutorials/data/documentation/os/oslogprivacy.json
4. Apple Developer Documentation, "Generating log messages from your code" — https://developer.apple.com/tutorials/data/documentation/os/generating-log-messages-from-your-code.json
5. ForensicArtifacts, "artifacts/data/macos.yaml" — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
