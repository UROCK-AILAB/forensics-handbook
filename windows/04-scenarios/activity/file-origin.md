# 이 파일은 어디서 왔나 (File Origin)

파일 하나를 두고 "이 파일이 어떤 길로 이 PC 에 들어왔나" 를 묻는 조사를 다룹니다. 인터넷에서 받았는지, 메일이나 메신저로 왔는지, USB 나 공유 폴더에서 옮겨 왔는지를 가립니다. 이 페이지는 출처를 알려 주는 기록을 어떤 순서로 보는지, 그 기록으로 어디까지 말할 수 있는지를 정리합니다. 아티팩트마다의 구조는 각 아티팩트 페이지에 있습니다.

"(관찰)" 을 붙인 내용은 Windows 11 Home 25H2(빌드 26200, 시간대 Korea Standard Time) PC 한 대에서 직접 본 것입니다(확인 범위: Win11 25H2 한 대). 다른 빌드나 다른 PC 에서는 다를 수 있습니다.

## 조사 질문

- 이 파일은 인터넷에서 받은 것입니까?
- 받았다면 어느 주소에서, 어느 브라우저로, 언제 받았습니까?
- 인터넷이 아니라면 메일 첨부·메신저·USB·공유 폴더 가운데 어디서 왔습니까?
- 지금 디스크에 있는 파일과 기록에 남은 파일이 같은 파일입니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | 이 페이지의 관찰은 Windows 11 한 대에서 본 것입니다. 검체의 버전과 빌드를 [시스템 기본 정보](/02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 먼저 적습니다. |
| 시간대 | 브라우저 기록·이벤트 로그·파일 시스템의 시각 기준이 서로 다릅니다. [시간대 설정](/02-artifacts/system-account/time-zone.md) 을 읽습니다. Bias 값을 부호 있는 수로 읽는 법은 [이 파일을 누가 언제 열었나](/04-scenarios/activity/file-access.md) 의 "먼저 확인할 것" 에 있습니다. |
| 사용자 | 브라우저 기록과 바로가기 파일은 사용자 프로필마다 따로 남습니다. [사용자 프로필 목록](/02-artifacts/system-account/profilelist.md) 으로 SID 와 프로필 폴더를 짝지어 둡니다. |
| 파일 시스템 | 출처 표시는 NTFS 의 이름 있는 스트림에 남습니다. 파일이 지금 있는 볼륨과 거쳐 온 저장 장치의 파일 시스템을 적어 둡니다. |
| Sysmon | 설치돼 있으면 이벤트 11·15 로 파일 생성과 스트림 생성을 볼 수 있습니다. 설치 여부부터 봅니다. |
| 수집 범위 | 대상 파일과 그 스트림, $MFT, $UsnJrnl:$J, 사용자 프로필의 브라우저 폴더, 최근 항목 폴더, 메일·메신저 데이터를 함께 확보합니다. |

**스트림까지 확보합니다.** NTFS 가 아닌 파일 시스템으로 파일을 옮기면 이름 있는 스트림이 없어집니다([대체 데이터 스트림](/01-foundations/disk-volume/ntfs/ads.md)). 대상 파일을 FAT·exFAT 저장 장치로 복사해 가져오면 출처 표시가 함께 사라집니다. 이미지에서 스트림째 읽거나, 스트림 내용을 따로 떠 둡니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 출처 표시 (Zone.Identifier) | 영역 번호, 받은 주소(HostUrl), 참조 주소(ReferrerUrl) | [다운로드 출처 표시](/02-artifacts/filesystem/zone-identifier.md) |
| 2 | 브라우저 다운로드 기록 | 저장 경로, 시작·끝 시각, 주소 사슬, 해시 | [크롬 계열 브라우저](/02-artifacts/browsers/chrome-edge-whale/index.md) · [파이어폭스](/02-artifacts/browsers/firefox/index.md) · [인터넷 익스플로러·옛 엣지](/02-artifacts/browsers/ie-edgehtml/index.md) |
| 3 | $UsnJrnl | 파일이 생긴 시각, 스트림이 붙은 시각의 단서 | [USN 변경 저널](/02-artifacts/filesystem/usnjrnl.md) |
| 4 | $MFT | 파일 이름, 시각, 스트림 목록 | [마스터 파일 테이블](/02-artifacts/filesystem/mft.md) |
| 5 | 메일·메신저 데이터 | 첨부 파일과 받은 파일 | [아웃룩](/02-artifacts/mail/outlook/index.md) · [카카오톡 PC](/02-artifacts/messengers/kakaotalk-pc/index.md) |
| 6 | 바로가기 파일 | 파일을 열었을 때의 볼륨 정보, 네트워크 위치 | [바로가기 파일](/02-artifacts/file-folder-usage/lnk.md) |
| 7 | USB 저장장치 흔적 | 장치를 연결한 시각 | [USB 저장장치 흔적](/02-artifacts/external-devices/usb-storage-artifacts/index.md) |
| 8 | 공유 폴더 기록 | 네트워크 드라이브, 파일 서버의 접근 이벤트 | [공유 폴더·네트워크 드라이브](/02-artifacts/network/network-shares-mapped-drives.md) · [공유 폴더 접근](/02-artifacts/event-logs/5140-5145.md) |
| 9 | Sysmon 11·15·2 | 파일 생성, 스트림 생성과 해시, 생성 시각 변경 | [Sysmon 로그](/02-artifacts/event-logs/sysmon/index.md) |
| 10 | 해시 | 같은 파일인지 가림 | [AmCache](/02-artifacts/execution/amcache-hve/index.md) · [해시셋 대조와 유사 해시](/03-techniques/analysis/hash-set-fuzzy-hash.md) |

출처 표시와 브라우저 기록(1~2)을 먼저 봅니다. 둘 다 없으면 5~8 에서 다른 길을 찾습니다. 3·4·9 는 시각을 맞추는 데 씁니다.

## 출처 표시 (Zone.Identifier)

첨부 파일 관리자 (Attachment Manager) 는 파일을 열기 전에 경고를 띄울지 정합니다[1]. 이때 "웹 표시 (Mark of the Web, MOTW)" 라고 부르는 보안 정보를 봅니다[1]. 문서의 적용 대상은 Windows 11·Windows 10 입니다[1].

- 파일이 차단돼 있는지는 탐색기의 파일 속성 → 일반 탭 아래쪽 보안 메시지로 봅니다[1].
- 차단돼 있으면 "차단 해제 (Unblock)" 를 고를 수 있습니다[1].
- 차단 해제가 Zone.Identifier 스트림을 지우는지는 확인하지 못했습니다.
- Sysmon 문서는 브라우저가 붙이는 `Zone.Identifier` 스트림을 "mark of the web" 이라고 부릅니다[2].

**ZoneId 값.** ZoneId 번호는 URLZONE 열거와 같은 번호로 알려져 있습니다.

| ZoneId | URLZONE 이름 | 뜻 |
|---|---|---|
| 0 | URLZONE_LOCAL_MACHINE | 로컬 컴퓨터 |
| 1 | URLZONE_INTRANET | 인트라넷 |
| 2 | URLZONE_TRUSTED | 신뢰 영역 |
| 3 | URLZONE_INTERNET | 인터넷 |
| 4 | URLZONE_UNTRUSTED | 신뢰하지 않는 영역 |

- -1 은 URLZONE_INVALID(IE7)이고, 1000~10000 은 사용자 정의 영역입니다[3].
- URLZONE 문서는 Zone.Identifier 를 언급하지 않습니다[3]. ZoneId 와 URLZONE 이 같은 번호라는 것은 알려진 해석입니다.
- 아래 관찰에서 Downloads 폴더 파일의 ZoneId 는 모두 3 이었습니다. 이 해석과 맞습니다.

**이 PC 에서 본 값.**

- 사용자 Downloads 폴더의 파일 262개 가운데 211개에 Zone.Identifier 스트림이 있었습니다(관찰).
- 211개 모두 `[ZoneTransfer]` 절과 ZoneId 줄이 있었습니다(관찰). ZoneId 는 모두 3 이었습니다(관찰).
- HostUrl 줄은 206개, ReferrerUrl 줄은 179개에 있었습니다(관찰). 그 밖의 키는 없었습니다(관찰).
- HostUrl 은 https 주소가 195개, http 주소가 8개, `about:internet` 이 3개였습니다(관찰).
- 그래서 HostUrl 이 늘 실제 주소인 것은 아닙니다.
- 스트림은 `[ZoneTransfer]` 와 줄바꿈(CRLF)으로 시작하는 ASCII 글자였습니다(관찰). 한 예의 크기는 192바이트였습니다(관찰).
- 이 PC 에서 본 스트림에는 시각을 적은 키가 없었습니다(관찰).

아래는 관찰한 절 이름과 키 이름으로 만든 예시입니다. 실제 검체에서 떼어 온 내용이 아닙니다. 주소는 예시 주소이고, 줄 순서도 예시입니다.

```
[ZoneTransfer]
ZoneId=3
ReferrerUrl=https://example.com/download
HostUrl=https://example.com/files/sample.zip
```

같은 예시의 앞부분을 바이트로 보면 이렇습니다.

```
오프셋      바이트                                              글자
00000000   5B 5A 6F 6E 65 54 72 61 6E 73 66 65 72 5D 0D 0A   [ZoneTransfer]..
00000010   5A 6F 6E 65 49 64 3D 33 0D 0A                     ZoneId=3..
```

**스트림이 붙은 시각은 저널로 좁힙니다.**

- 이름 있는 스트림이 더해지거나 없어지면 $UsnJrnl 에 USN_REASON_STREAM_CHANGE(0x00200000)가 남습니다[4].
- 이름 있는 스트림에 데이터가 늘면 USN_REASON_NAMED_DATA_EXTEND(0x00000020)가 남습니다[4].
- 스트림 안에 시각이 없으므로, 저널이 남아 있으면 이 두 값이 켜진 레코드로 스트림이 붙은 시각을 좁힙니다.
- 저널 레코드의 다른 칸과 추출 방법은 [지운 파일의 흔적 찾기](/04-scenarios/activity/deleted-file-traces.md) 의 "$UsnJrnl" 절에 있습니다.

**NTFS 밖을 거친 파일.**

- FAT 처럼 NTFS 가 아닌 파일 시스템으로 옮기면 이름 있는 스트림이 없어집니다.
- 그래서 FAT·exFAT 로 포맷한 USB 를 거친 파일에는 출처 표시가 없을 수 있습니다.
- 압축 파일을 풀 때 풀린 파일에도 출처 표시가 붙는지는 확인하지 못했습니다. 압축 파일 자체의 출처 표시와 [압축 프로그램 사용 기록](/02-artifacts/file-folder-usage/7-zip-winrar-bandizip.md) 을 함께 봅니다.

## 브라우저 다운로드 기록

크롬 계열 (Chrome·Edge·Whale) 브라우저는 사용자 프로필의 History 파일에 다운로드를 남깁니다. 표 구조는 [크롬 계열 브라우저](/02-artifacts/browsers/chrome-edge-whale/index.md) 에 있습니다. 아래는 출처 조사에 쓰는 칸만 추린 것입니다.

| 묻는 것 | `downloads` 표의 칸 |
|---|---|
| 어디에 저장했나 | target_path, current_path |
| 언제 받았나 | 시작 시각, 끝 시각 |
| 다 받았나 | 받은 크기, 상태 |
| 어디서 받았나 | referrer, tab_url, tab_referrer_url |
| 브라우저가 위험하다고 봤나 | danger_type |
| 브라우저 안에서 연 적이 있나 | opened |
| 확장 프로그램과 관계있나 | by_ext_id, by_ext_name |
| 어떤 형식인가 | mime_type, original_mime_type |
| 같은 파일인가 | hash (원시 32바이트) |

- `downloads_url_chains` 표에서 chain_index 0 은 처음 요청한 주소입니다.
- 가장 큰 chain_index 가 실제로 받은 주소입니다.
- `hash` 는 16진으로 바꿔 디스크 파일의 해시와 비교합니다.
- 다운로드 목록만 지우면 받은 파일은 디스크에 남아 있을 수 있습니다. 이때는 출처 표시와 $MFT 로 파일을 찾습니다.
- 파이어폭스와 옛 IE·Edge 의 다운로드 기록은 [파이어폭스](/02-artifacts/browsers/firefox/index.md) 와 [인터넷 익스플로러·옛 엣지](/02-artifacts/browsers/ie-edgehtml/index.md) 에서 봅니다.
- 받기 전후에 어떤 사이트를 불러왔는지는 [웹 사용 행위 재구성](/04-scenarios/activity/web-activity.md) 을 따라 봅니다.

## 다른 길로 들어온 파일

**메일 첨부.** 아웃룩 첨부는 PST·OST 안과 첨부 임시 폴더(OLK·Content.Outlook)에서 찾습니다. 이 페이지에서는 세부를 다루지 않습니다. 위치와 해석은 [아웃룩](/02-artifacts/mail/outlook/index.md) 에서 봅니다.

**메신저.** 카카오톡 PC 는 받은 파일 폴더를 따로 둡니다. 세부는 [카카오톡 PC](/02-artifacts/messengers/kakaotalk-pc/index.md) 에 있습니다. 다른 메신저는 [누구와 연락을 주고받았나](/04-scenarios/activity/communication-reconstruction.md) 에서 고릅니다.

**USB·외부 장치.**

- 파일을 USB 에서 열었다면 그때 생긴 바로가기 파일에 볼륨 정보가 남습니다.
- 볼륨 정보에는 드라이브 종류와 볼륨 시리얼이 있습니다. 드라이브 종류 2 는 이동식입니다.
- 이 값으로 파일을 연 장치를 좁힙니다. 장치를 연결한 시각은 [USB 저장장치 흔적](/02-artifacts/external-devices/usb-storage-artifacts/index.md) 에서 봅니다.
- 바로가기 파일의 구조는 [바로가기 파일](/02-artifacts/file-folder-usage/lnk.md) 에 있습니다.

**공유 폴더.** 바로가기 파일에 네트워크 위치가 남을 수 있습니다. 파일 서버가 있으면 서버의 [공유 폴더 접근](/02-artifacts/event-logs/5140-5145.md) 이벤트를 봅니다.

**같은 파일인지 가리기.**

- AmCache 에는 파일의 SHA-1 이 남습니다([AmCache](/02-artifacts/execution/amcache-hve/index.md)).
- 크롬 계열 다운로드 기록의 `hash` 도 비교에 씁니다.
- 알려진 파일 목록과 맞추는 법은 [해시셋 대조와 유사 해시](/03-techniques/analysis/hash-set-fuzzy-hash.md) 에 있습니다.

**Sysmon 이 설치돼 있을 때.**

| 이벤트 | 남는 때 |
|---|---|
| 11 FileCreate | 파일이 만들어지거나 덮어써질 때입니다. 문서는 다운로드 폴더와 임시 폴더를 감시하는 데 쓸모 있다고 적었습니다. |
| 15 FileCreateStreamHash | 이름 있는 스트림이 생길 때입니다. 기본 스트림과 이름 있는 스트림 내용의 해시를 남깁니다. |
| 2 | 프로세스가 파일 생성 시각을 바꿨을 때입니다. |

(표는 [2] 에서 옮겼습니다.) Sysmon 의 설치 조건과 시각 기준은 [어떤 프로그램을 언제 실행했나](/04-scenarios/activity/program-execution.md) 의 "Sysmon 이벤트 1" 절에 있습니다. 파일 시각을 조작한 흔적은 [타임라인 작성](/03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 분석 흐름

1. Windows 버전·시간대·사용자 SID 를 정리합니다. Sysmon 설치 여부도 적습니다.
2. 대상 파일의 이름 있는 스트림 목록을 봅니다. Zone.Identifier 가 있으면 내용을 그대로 떠 둡니다.
3. ZoneId·HostUrl·ReferrerUrl 을 적습니다. HostUrl 이 `about:internet` 처럼 주소가 아니면 브라우저 기록에서 주소를 찾습니다.
4. 사용자마다 브라우저 다운로드 기록에서 저장 경로가 대상 파일과 같은 항목을 찾습니다. 받은 뒤 이름을 바꿨을 수 있으므로 크기와 해시로도 찾습니다.
5. 다운로드 기록의 `hash` 와 디스크 파일의 해시를 비교합니다. 주소 사슬에서 처음 요청한 주소와 실제로 받은 주소를 나눠 적습니다.
6. $UsnJrnl 에서 대상 파일의 파일 참조로 레코드를 찾습니다. 파일이 생긴 레코드와 스트림이 붙은 레코드의 시각을 브라우저 기록의 시각과 맞춥니다.
7. 출처 표시도 다운로드 기록도 없으면 메일·메신저·USB·공유 폴더 기록에서 같은 이름·크기·해시를 찾습니다.
8. 바로가기 파일의 볼륨 정보로 파일을 연 장치의 종류와 시리얼을 확인합니다. 그 장치의 연결 시각과 맞춥니다.
9. 모든 시각을 UTC 하나로 맞춰 [타임라인](/03-techniques/analysis/timeline/index.md) 에 올립니다. 시각 값의 형식은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 확인합니다.
10. 대상이 악성 파일이면 [악성코드는 어디서 들어왔나](/04-scenarios/incident/initial-access.md) 로 이어 갑니다. 받은 파일을 실행했는지는 [어떤 프로그램을 언제 실행했나](/04-scenarios/activity/program-execution.md) 에서 봅니다.

## 흔한 오판

1. **ZoneId 3 으로 받은 사이트를 말합니다.** ZoneId 3 은 인터넷 영역이라는 뜻으로 알려진 값입니다. 어느 브라우저로 어느 사이트에서 받았는지는 HostUrl 과 브라우저 기록으로 따로 봅니다. HostUrl 이 `about:internet` 인 경우도 있었습니다(관찰).
2. **출처 표시가 없으니 인터넷에서 오지 않았다고 봅니다.** NTFS 가 아닌 파일 시스템을 거치면 스트림이 없어집니다. 사용자가 차단 해제를 했을 수도 있습니다[1].
3. **처음 요청한 주소를 받은 주소로 씁니다.** 주소 사슬의 chain_index 0 은 처음 요청한 주소입니다. 실제로 받은 주소는 가장 큰 번호입니다.
4. **다운로드 목록이 비어 있으니 받지 않았다고 봅니다.** 목록만 지워도 파일은 남을 수 있습니다. 시크릿 창을 썼을 수도 있습니다([시크릿 모드로 무엇을 했나](/04-scenarios/activity/private-browsing.md)).
5. **$MFT 의 생성 시각을 문서를 처음 만든 시각으로 씁니다.** 두 시각은 다를 수 있습니다. 파일 시스템 시각이 언제 바뀌는지는 [타임라인 작성](/03-techniques/analysis/timeline/index.md) 에서, 문서 안의 날짜는 [이 문서의 날짜를 믿을 수 있나](/04-scenarios/activity/document-date-verification.md) 에서 확인합니다.
6. **출처 기록을 사람의 행위로 씁니다.** 기록은 어느 계정의 세션에서 어느 프로그램이 파일을 받았는지를 보여 줍니다. 그 계정을 누가 썼는지는 다른 기록으로 좁힙니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 ○○ 에 ○○ 사이트에서 invoice.zip 을 내려받았습니다."
- 쓸 문장: "`○○\Downloads\invoice.zip` 에 Zone.Identifier 스트림이 있습니다. 스트림의 ZoneId 는 3 이고, HostUrl 은 `https://○○` 입니다. 사용자 ○○ 프로필의 ○○ 브라우저 다운로드 기록에도 같은 저장 경로의 항목이 있습니다. 이 항목의 끝 시각은 ○○(UTC) 입니다. 항목에 적힌 해시는 디스크 파일의 해시와 같습니다. 이 기록은 이 계정의 세션에서 이 브라우저가 이 주소로부터 파일을 받았음을 보여 줍니다. 화면 앞에 있던 사람은 이 기록만으로 정할 수 없습니다."
- 출처 표시만 있을 때: "`○○\invoice.zip` 에 Zone.Identifier 스트림이 있고 ZoneId 는 3 입니다. 이 값은 인터넷 영역을 뜻하는 값으로 알려져 있습니다. 어느 프로그램이 언제 이 스트림을 붙였는지는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [다운로드 출처 표시](/02-artifacts/filesystem/zone-identifier.md) — Zone.Identifier 스트림의 구조입니다.
- [대체 데이터 스트림](/01-foundations/disk-volume/ntfs/ads.md) — 이름 있는 스트림이 저장되는 방식입니다.
- [크롬 계열 브라우저](/02-artifacts/browsers/chrome-edge-whale/index.md) · [파이어폭스](/02-artifacts/browsers/firefox/index.md) · [인터넷 익스플로러·옛 엣지](/02-artifacts/browsers/ie-edgehtml/index.md) — 다운로드 기록의 구조입니다.
- [USN 변경 저널](/02-artifacts/filesystem/usnjrnl.md) — 파일과 스트림이 생긴 시각의 단서입니다.
- [USB 저장장치 흔적](/02-artifacts/external-devices/usb-storage-artifacts/index.md) · [바로가기 파일](/02-artifacts/file-folder-usage/lnk.md) — 외부 장치에서 온 파일을 가립니다.
- [웹 사용 행위 재구성](/04-scenarios/activity/web-activity.md) — 받기 전후의 웹 사용을 봅니다.
- [악성코드는 어디서 들어왔나](/04-scenarios/incident/initial-access.md) — 악성 파일의 유입 경로를 봅니다.
- [그 시각에 PC 를 쓴 사람이 누구인가](/04-scenarios/activity/user-attribution.md) — 계정에서 사람으로 좁힙니다.

## 참고 문헌

1. Microsoft Support, "Information about the Attachment Manager in Microsoft Windows" — https://support.microsoft.com/en-us/topic/information-about-the-attachment-manager-in-microsoft-windows-c48a4dcd-8de5-2af5-ee9b-cd795ae42738
2. Microsoft Learn, "Sysmon - Sysinternals" (2026-09-10 판) — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
3. Microsoft Learn, "URLZONE enumeration" (IE 보관 문서) — https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/ms537175(v=vs.85)
4. Microsoft Learn, "USN_RECORD_V2 structure" — https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-usn_record_v2
