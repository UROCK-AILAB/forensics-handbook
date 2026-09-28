---
title: "다운로드 출처 속성"
parent: "아티팩트 · 파일 시스템"
nav_order: 1000
---

# 다운로드 출처 속성 (kMDItemWhereFroms)

다운로드 출처 속성 (kMDItemWhereFroms)은 파일을 어디서 얻었는지 적어 두는 Spotlight 메타데이터 속성이고, 내려받은 파일이면 받은 주소가 문자열 배열로 들어 있어서 파일 하나만 보고도 출처 URL을 확인할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

이 속성은 항목을 얻은 곳을 나타내는 Spotlight 메타데이터 속성입니다 [1]. 내려받은 파일이면 URL을 담고, 메일로 받은 파일이면 보낸 사람의 이메일 주소나 메시지 제목 같은 값을 담을 수 있습니다 [1]. 메일 첨부파일의 배열 순서와 모양은 실제 데이터로 확인해야 합니다.

속성을 쓰는 쪽은 파일을 저장하는 앱입니다. Chromium(크롬 계열 브라우저)은 받은 파일을 격리 처리하는 `QuarantineFile` 안에서 `AddOriginMetadataToFile` 함수로 이 속성을 씁니다 [2]. 순서를 보면 먼저 파일이 있는지 확인하고, 원본 URL과 referrer URL을 `SanitizeUrlForQuarantine()` 으로 정리한 뒤 출처 속성을 쓰고, 그다음에 격리 속성을 씁니다 [2]. 원본 URL이 비어 있고 다운로드를 시작한 쪽의 출처(request initiator)를 알면 그 출처 주소를 원본 URL 자리에 대신 씁니다 [2]. 두 속성 쓰기는 모두 되면 좋고 안 돼도 그만인 동작(best-effort)이라서, 쓰기에 실패해도 다운로드는 그대로 끝납니다 [2].

이 속성이 있으면 원본 URL이나 referrer URL로 Spotlight를 검색해 내려받은 파일을 찾을 수 있습니다 [2]. Spotlight 쪽 색인은 [스포트라이트 (Spotlight)](../file-folder-usage/spotlight/index.md)에서 다룹니다.

Safari, AirDrop, 메시지, curl 같은 명령줄 도구가 이 속성을 쓰는지, 쓴다면 무엇을 넣는지는 실제 데이터로 확인해야 합니다. 아래 배열 해석은 Chromium 기준입니다.

## 위치와 버전별 차이

파일마다 붙는 확장 속성 (extended attribute, xattr)이라서 따로 정해진 경로가 없고, 속성 이름 `com.apple.metadata:kMDItemWhereFroms` 로 찾습니다 [2][3]. Finder의 정보 가져오기 창에서는 "추가 정보" 아래 "출처(Where from)"로 보입니다 [3]. 확장 속성이 볼륨에 어떻게 저장되는지는 [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md)에서 다룹니다.

| macOS 버전 | 내용 | 출처 |
|---|---|---|
| OS X 10.4 이후 | 속성이 있음. 근거 문서가 2014년 이후 고치지 않은 보관 문서라서 최신 macOS 동작은 알 수 없음 | [1] |
| macOS Sierra·High Sierra | `com.apple.metadata:kMDItemWhereFroms` 확장 속성으로 남음 | [3] |
| 버전 표시 없음 | 현재 Chromium이 이 속성을 씀 | [2] |

Catalina 이후 기기에서는 형식이 같다고 가정하지 말고, 아래 구조와 맞는지 한 번 확인한 뒤 해석합니다.

## 구조

값은 이진 속성 목록 파일 (binary plist)이고, 파일 앞머리는 `bplist00` 이며 Chromium 주석은 이 형식을 "binary1" 이라고 부릅니다 [2][3]. 이진 plist 자체를 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

plist 안에는 문자열 배열 하나가 들어 있습니다. 형식은 CFString 배열(NSArray 안에 NSString 하나 이상)이고, 내용은 대부분 UTF-8 텍스트입니다 [1][3].

Chromium이 쓴 배열에는 값이 두 개까지 들어갑니다 [2].

| 순서 | Chromium이 넣는 값 | 뜻 |
|---|---|---|
| 1 | 원본 URL (source URL) | 파일을 실제로 받아 온 주소. 원본 URL이 비어 있으면 다운로드를 시작한 쪽의 출처 주소가 들어갈 수 있음 |
| 2 | referrer URL | 그 다운로드 링크가 있던 페이지 |

Chromium은 빈 URL을 배열에 넣지 않습니다. 시크릿 모드로 받은 파일처럼 URL이 비어 있으면 배열이 비었거나 속성이 아예 없을 수 있습니다 [2].

값에는 시각이 들어 있지 않습니다. 들어 있는 것은 URL 같은 문자열 배열뿐입니다 [1][2].

## 증거로서 의미

**증명하는 것.** 속성이 붙어 있으면 누군가 이 파일에 출처로 적어 둔 문자열이 남아 있다는 뜻이고, 보통은 파일을 저장한 앱이 적습니다. Chromium 계열 브라우저가 쓴 속성이라면 첫째 값은 파일을 받아 온 주소이고 둘째 값은 그 링크가 있던 페이지라서, 받은 주소와 거쳐 온 페이지를 함께 알 수 있습니다 [2]. 이 속성은 파일에 오래 붙어 다니는 정보이고, copyfile 플래그로 보면 그냥 복사하거나 저장할 때는 속성이 따라가는 쪽이라서 다운로드 폴더 밖으로 옮긴 파일에서도 출처를 찾아볼 만합니다 [3][4][5].

**증명하지 못하는 것.** 값에 시각이 없어서 언제 받았는지는 이 속성만으로 알 수 없습니다. 어느 앱이 썼는지도 값에 적혀 있지 않아서 배열의 두 값을 원본 URL과 referrer로 읽는 해석은 Chromium이 썼다고 볼 근거가 있을 때만 씁니다. 사용자 계정도 들어 있지 않습니다. 반대로 속성이 없다고 해서 인터넷에서 받지 않았다고 결론 내리지 않습니다. 시크릿 모드 다운로드는 빈 배열이나 속성 없음으로 남을 수 있고, Chromium은 속성 쓰기에 실패해도 그냥 넘어가며, 남에게 넘겨주는 경로를 거친 파일은 속성이 빠질 수 있습니다(아래 함정 참고) [2][4][5].

보고서에는 "이 파일에 출처 속성이 있고, 첫째 값은 이 URL이고 둘째 값은 이 URL이다" 처럼 속성에 적힌 문자열만 옮기고, 받은 시각과 받은 사람은 다른 기록으로 따로 밝힙니다.

## 시각 해석

출처 속성에는 시각이 없으므로 받은 시각은 다른 기록에서 찾습니다. 먼저 볼 곳은 사용자별 격리 이벤트 DB `~/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2` 이고, 이 SQLite DB의 `LSQuarantineEvent` 표에 있는 `LSQuarantineTimeStamp` 가 이벤트 시각입니다 [6]. 이 값은 2001-01-01부터 센 초인 맥 절대 시각이라서 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에 따라 바꿉니다 [6]. DB의 나머지 열과 격리 속성은 [격리 속성과 다운로드 기록 (Quarantine)](quarantine/index.md)에서 다룹니다.

`kMDItemDownloadedDate` 라는 별도 속성은 Apple 속성 문서에 없어서 [1], 여기서 받은 시각을 찾을 수 있는지는 실제 데이터로 확인합니다.

## 함정과 한계

**쓰는 앱마다 다를 수 있습니다.** 배열 순서와 내용은 Chromium 소스로만 정해져 있어서, Safari와 메일이 쓴 속성은 실제 데이터로 확인합니다. 다른 앱이 쓴 속성에 Chromium 기준의 "첫째는 원본, 둘째는 referrer" 해석을 그대로 덧씌우지 않습니다.

**복사·공유 방식에 따라 남기도 하고 빠지기도 합니다.** Apple 오픈소스 copyfile의 기본 속성표에는 kMDItemWhereFroms만 따로 적은 항목이 없고, 대신 이름이 `com.apple.metadata:` 로 시작하는 속성 모두에 P와 S 플래그를 붙이는 접두사 규칙이 있어서 이 속성도 그 규칙을 따른다고 볼 수 있습니다 [4]. 플래그 글자의 뜻과 복사 의도 (intent)별 결과를 정리하면 아래와 같습니다 [4][5].

| 플래그 | 이름 | 설명 |
|---|---|---|
| P | `XATTR_FLAG_NO_EXPORT` | 내보내지 않는 속성이라서 SHARE 의도에서는 보존하지 않음 |
| S | `XATTR_FLAG_SYNCABLE` | SYNC 의도에서 동기화 대상 |
| C | `XATTR_FLAG_CONTENT_DEPENDENT` | 내용에 따라 달라지는 속성 |

| 의도 | 뜻 | `com.apple.metadata:*` (P, S) |
|---|---|---|
| COPY | `cp src dst` 처럼 그냥 복사 | 남음 |
| SAVE | 안전 저장 (safe save) | 남음 |
| SHARE | 다른 사람에게 넘겨줌 | 빠짐 |
| SYNC | 같은 사용자의 다른 저장소로 동기화 | 동기화 대상 |
| BACKUP | 백업 | 플래그 정의로는 판단하지 못함 |

이 표는 플래그 정의로 미루어 본 결과입니다. AirDrop, 메일 첨부, iCloud Drive, zip 압축, FAT·exFAT 매체로 옮길 때 실제로 무엇이 남는지는 시험 기기에서 재현해 확인합니다. 같은 표에서 격리 속성 `com.apple.quarantine` 은 `PCS` 라서 C 플래그가 더 붙어 있고, 두 속성이 같은 규칙으로 움직인다고 가정하지 않습니다 [4]. 이 플래그 API는 macOS 10.10부터 있습니다 [5].

**속성은 지우거나 고쳐 쓸 수 있습니다.** 확장 속성은 파일에 쓸 권한만 있으면 `xattr` 같은 명령줄 도구로 지우거나 다른 값으로 바꿔 쓸 수 있고, 값 안에는 누가 언제 썼는지 적혀 있지 않습니다. 그래서 속성의 URL은 격리 이벤트 DB나 브라우저 다운로드 기록처럼 따로 남는 기록과 맞춰 본 뒤에 믿습니다.

**Spotlight 색인과 속성은 다른 곳입니다.** Spotlight가 이 값을 색인해서 출처 URL로 파일을 찾을 수 있지만 [2], 색인 데이터베이스(`.Spotlight-V100`)에 이 값이 남는다고 단정할 수 없으므로, 파일에서 속성이 사라진 뒤에도 색인에서 찾을 수 있다고 기대하지 않습니다.

**URL이 원래 주소 그대로라고 단정하지 않습니다.** Chromium은 URL을 정리 함수에 한 번 통과시킨 뒤 기록하므로 [2], 속성의 URL은 원래 주소에서 일부가 빠졌을 수 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세를 바탕으로 만든 예시이고, 실제 기기에서 나온 값이 아닙니다. 속성 값을 꺼내 16진수로 보면 첫 8바이트에 `bplist00` 이 보이고, 그 뒤 어딘가에 URL 문자열이 UTF-8 글자 그대로 보입니다 [3].

```text
62 70 6C 69 73 74 30 30   bplist00        ← 이진 plist 앞머리
...
68 74 74 70 73 3A 2F 2F   https://        ← 배열 안 문자열(원본 URL)의 시작
...
68 74 74 70 73 3A 2F 2F   https://        ← 둘째 문자열(referrer)의 시작
...
```

URL이 눈으로 보인다고 해서 배열 순서까지 헥스에서 짐작하지 말고, 순서는 plist를 풀어 배열로 읽은 결과로 확인합니다. 실제 디스크 이미지 파일에서 뽑은, URL 두 개가 든 16진수 예시는 [3]에 있습니다.

### 공개 도구로 한 번

1. 실행 중인 시스템이나 마운트한 이미지에서 `xattr` 명령줄 도구나 xattred로 `com.apple.metadata:kMDItemWhereFroms` 값을 꺼냅니다 [3].
2. 꺼낸 값을 이진 plist로 풀어 문자열 배열을 읽습니다. 풀이 방법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)을 따릅니다.
3. Finder 정보 가져오기 창의 "출처"와 비교해 값이 같은지 봅니다 [3].
4. 같은 사용자의 격리 이벤트 DB를 mac_apt의 quarantine 플러그인 같은 도구로 읽어 같은 URL이 있는 행을 찾고 시각을 확인합니다 [6].

이미지를 만들고 다루는 절차는 [맥 증거 확보 (Acquisition)](../../03-techniques/process-acquisition/evidence-acquisition/index.md)에서 다룹니다.

## 교차 검증

Chromium은 출처 속성과 격리 속성을 한 함수 안에서 차례로 쓰고, 격리 속성의 `kLSQuarantineDataURLKey` 에는 원본 URL을, `kLSQuarantineOriginURLKey` 에는 referrer를 넣습니다 [2]. 그래서 Chromium이 받은 파일이라면 출처 배열의 두 값이 격리 이벤트 DB의 `LSQuarantineDataURLString`·`LSQuarantineOriginURLString` 과 맞는지 대 볼 수 있습니다 [2][6]. 격리 방식은 http·https 주소면 웹 다운로드 (`kLSQuarantineTypeWebDownload`), 그 밖이면 기타 다운로드 (`kLSQuarantineTypeOtherDownload`)로 적습니다 [2].

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [격리 속성과 다운로드 기록 (Quarantine)](quarantine/index.md) | 받은 시각, 받은 앱, 같은 URL |
| [크롬·엣지·웨일 (Chromium 계열)](../browsers/chromium/index.md) | 브라우저 쪽 다운로드 기록 |
| [사파리 (Safari)](../browsers/safari/index.md) | 사파리로 받았을 때의 브라우저 쪽 기록 |
| [애플 메일 (Apple Mail)](../mail/apple-mail/index.md) | 메일 첨부로 들어온 파일의 원래 메시지 |
| [스포트라이트 (Spotlight)](../file-folder-usage/spotlight/index.md) | 출처 URL로 파일을 찾는 색인 |
| [파일 시스템 이벤트 (FSEvents)](fsevents/index.md) | 파일이 만들어지고 옮겨진 흔적 |

파일의 출처를 처음부터 끝까지 따라가는 순서는 [이 파일은 어디서 왔나 (File Origin)](../../04-scenarios/activity/file-origin.md)에, 악성 파일이 들어온 경로를 찾는 흐름은 [악성 코드는 어디서 들어왔나 (Initial Access)](../../04-scenarios/incident/initial-access.md)에 정리했습니다.

## 실습

NIST CFReDS 같은 공개 자료 가운데 macOS 이미지를 골라 아래 질문을 풀어 봅니다.

1. 사용자의 다운로드 폴더에서 출처 속성이 붙은 파일과 붙지 않은 파일을 나눠 보고, 붙지 않은 파일이 왜 없는지 이 페이지의 함정 절에 비춰 설명할 수 있나요?
2. 출처 배열에 값이 두 개인 파일을 골라, 둘째 값의 페이지가 브라우저 방문 기록에도 있는지 확인할 수 있나요?
3. 같은 URL이 격리 이벤트 DB에 있다면, 그 행의 시각을 UTC와 그 기기의 현지 시각으로 각각 적을 수 있나요?
4. 이미지의 macOS 버전이 Catalina 이후라면, 속성 값이 이 페이지의 구조(이진 plist 안 문자열 배열)와 같은지 확인할 수 있나요?

## 참고 문헌

1. Apple, "Spotlight Metadata Attributes Reference" (Documentation Archive, 2014-07-15) — https://developer.apple.com/library/archive/documentation/CoreServices/Reference/MetadataAttributesRef/Reference/CommonAttrs.html
2. Chromium 소스, `components/services/quarantine/quarantine_mac.mm` — https://raw.githubusercontent.com/chromium/chromium/main/components/services/quarantine/quarantine_mac.mm
3. Howard Oakley, "xattr: com.apple.metadata:kMDItemWhereFroms, origin of downloaded file", The Eclectic Light Company, 2017 — https://eclecticlight.co/2017/12/21/xattr-com-apple-metadatakmditemwherefroms-origin-of-downloaded-file/
4. Apple 오픈소스 copyfile, `xattr_flags.c` — https://raw.githubusercontent.com/apple-oss-distributions/copyfile/main/xattr_flags.c
5. Apple 오픈소스 copyfile, `xattr_flags.h` — https://raw.githubusercontent.com/apple-oss-distributions/copyfile/main/xattr_flags.h
6. mac_apt quarantine 플러그인 (ydkhatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/quarantine.py
