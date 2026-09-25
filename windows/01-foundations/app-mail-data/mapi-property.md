---
title: "MAPI 속성"
parent: "기반 · 앱·메일 데이터 구조"
nav_order: 490
---

# MAPI 속성 (MAPI Property)

## 한 줄 요약

MAPI (Messaging API) 를 쓰는 저장소는 메일·수신자·첨부를 속성 (Property) 묶음으로 저장합니다.
속성 하나는 16비트 식별자와 값 형식의 짝으로 가리고, 식별자가 어느 범위에 있느냐에 따라 누가 정한 속성인지가 나뉩니다.
0x8000 이상 식별자는 이름 붙은 속성입니다. 저장소 안의 대응표로 풀어야 뜻을 압니다.
시각 속성은 여러 개이고, 값 형식에 따라 세는 기준 날짜가 다릅니다.

속성 번호와 뜻은 Outlook 2013·Outlook 2016 기준입니다[1][8].
속성 이름은 libfmapi 가 쓰는 이름이라 공식 이름과 다를 수 있고, 다른 곳은 따로 표시했습니다.

## 이 형식을 쓰는 아티팩트

MAPI 를 쓰는 파일 형식은 아래와 같습니다[8].

| 파일 형식 | 다루는 페이지 |
|---|---|
| PFF (PST·OST·PAB) | [아웃룩](../../02-artifacts/mail/outlook/index.md) |
| NK2 | [아웃룩](../../02-artifacts/mail/outlook/index.md) |
| Exchange 의 EDB (ESE 기반) | [ESE 데이터베이스](../database-log-formats/extensible-storage-engine/index.md) |

- 이 페이지는 속성 번호와 값 형식만 다루고, 파일 안에서 속성을 찾아가는 구조는 각 형식의 페이지에서 다룹니다.
- 메일에 원래 붙어 있던 인터넷 헤더의 문법은 [인터넷 메일 형식](eml-mbox-rfc-5322-mime.md) 에서 다룹니다.

## 구조

> 그림 자리: 메시지 하나를 속성 목록(식별자 · 값 형식 · 값)으로 펼친 표와, 0x8000 이상 식별자가 대응표를 거쳐 GUID + 이름으로 풀리는 화살표

### 식별자와 값 형식

- 속성 식별자 (Property Identifier) 는 속성의 용도와 책임 주체를 나타내는 번호입니다[1].
- MAPI 는 번호를 범위로 나누어, 어느 범위에 있느냐로 용도와 소유가 정해집니다.
- 속성 식별자는 PidTag, ptag, PR_ 같은 이름으로도 부릅니다[8].
- 속성 형식은 항목 종류와 값 형식의 조합입니다[8]. 같은 식별자라도 값 형식이 다르면 다른 속성입니다.

| 식별자 | 값 형식 | 속성 (libfmapi) |
|---|---|---|
| 0x0E08 | Integer32 (0x0003) | PidTagMessageSize |
| 0x0E08 | Integer64 (0x0014) | PidTagMessageSizeExtended |
| 0x1013 | 문자열 | PidTagBodyHtml |
| 0x1013 | Binary (0x0102) | PidTagHtml |
| 0x3701 | Binary (0x0102) | PidTagAttachDataBinary |
| 0x3701 | Object (0x000D) | PidTagAttachDataObject |

- 식별자와 값 형식을 32비트 수 하나로 합친 것을 속성 태그 (Property Tag) 라고 합니다[2].
- 비트 16~31 에 식별자가, 비트 0~15 에 값 형식이 들어갑니다. 예를 들어 식별자 0x0037 과 값 형식 0x001F 를 합치면 `0x0037001F` 입니다.
- 도구마다 태그로 적기도 하고 식별자만 적기도 합니다. 도구 출력을 읽을 때는 식별자와 값 형식을 따로 확인합니다.

### 식별자 범위 (Microsoft 문서)

| 범위 | 이름 | 누가 정하나 |
|---|---|---|
| 0x0000 | 예약 | 쓰지 않습니다 |
| 0x0001~0x3FFF | MAPI 정의 속성 | MAPI |
| 0x4000~0x7FFF | 메시지·수신자 속성 | 클라이언트나 서비스 제공자 |
| 0x8000 이상 | 이름 붙은 속성 (Named Property) | 128비트 GUID 와 유니코드 문자열 또는 32비트 숫자로 이름을 짓습니다 |
| 0xFFFF | 예약 | 쓰지 않습니다 |

- 0x0001~0x7FFF 속성을 태그 속성 (Tagged Property) 이라고 부릅니다.
- 0x67F0~0x67FF 는 보안 프로필 속성입니다. 비밀번호처럼 더 보호해야 할 정보를 담습니다. 숨기거나 암호화할 수 있습니다.
- 전송되는 (Transmittable) 속성은 메시지와 함께 넘어가지만, 전송 안 되는 속성은 넘어가지 않습니다. 전송 안 되는 속성은 대개 현재 세션의 클라이언트나 서비스 제공자에게만 쓸모 있습니다.

### 세부 범위 (libfmapi)

| 범위 | 용도 |
|---|---|
| 0x0001–0x0BFF | 메시지 봉투 |
| 0x0C00–0x0DFF | 수신자 |
| 0x0E00–0x0FFF | 전송 안 되는 메시지 속성 |
| 0x1000–0x2FFF | 메시지 내용 |
| 0x3000–0x33FF | 여러 객체에 공통 |
| 0x3400–0x35FF | 메시지 저장소 |
| 0x3600–0x36FF | 폴더·주소록 컨테이너 |
| 0x3700–0x38FF | 첨부 |
| 0x3900–0x39FF | 주소록 |
| 0x3A00–0x3BFF | 메시징 사용자 |
| 0x3C00–0x3CFF | 배포 목록 |
| 0x3D00–0x3DFF | 프로필 |
| 0x3E00–0x3FFF | 상태 객체 |
| 0x4000–0x57FF | 전송 제공자가 정한 봉투 |
| 0x5800–0x5FFF | 전송·주소록 제공자가 정한 수신자 |
| 0x6000–0x65FF | 클라이언트가 정한 비전송 속성 |
| 0x6600–0x67FF | 서비스 제공자가 정한 비전송 속성 |
| 0x6800–0x7BFF | 사용자 정의 메시지 클래스의 내용 |
| 0x7C00–0x7FFF | 사용자 정의 메시지 클래스의 비전송 속성 |
| 0x8000–0xFFFE | 이름 붙은 속성 |
| 0xFFFF | PROP_ID_INVALID |

0x0001 부터 0x3FFF 까지가 MAPI 가 정한 범위입니다.

### 값 형식 (libfmapi)

| 번호 | 이름 | 다른 이름 | 값 |
|---|---|---|---|
| 0x0000 | Unspecified | | |
| 0x0001 | Null | | |
| 0x0002 | Integer16 | PT_SHORT, PT_I2 | 16비트 정수 |
| 0x0003 | Integer32 | PT_LONG, PT_I4 | 32비트 정수 |
| 0x0004 | Floating32 | PT_FLOAT | 32비트 실수 |
| 0x0005 | Floating64 | PT_DOUBLE | 64비트 실수 |
| 0x0006 | Currency | | 64비트 정수. 소수점 아래 네 자리로 봅니다. 327500 은 32.7500 입니다 |
| 0x0007 | FloatingTime | PT_APPTIME | double. 정수 부분은 1899-12-30 부터 센 날 수, 소수 부분은 하루 안의 시각 |
| 0x000A | ErrorCode | PT_ERROR | 32비트 SCODE |
| 0x000B | Boolean | | 0 은 거짓, 0 이 아니면 참. 일부 Microsoft 문서는 8비트 0/1 로 적습니다 |
| 0x000D | Object / EmbeddedTable | PT_OBJECT | 객체 |
| 0x0014 | Integer64 | PT_I8, PT_LONGLONG | 64비트 정수 |
| 0x001E | String8 | PT_STRING8 | 코드 페이지를 따르는 바이트 문자열. 끝 NUL 이 없을 때도 있습니다 |
| 0x001F | String | PT_UNICODE | UTF-16LE, BOM 없음. 끝 NUL 이 없을 때도 있습니다 |
| 0x0040 | Time | PT_SYSTIME | FILETIME. 1601-01-01 부터 센 100ns 단위 |
| 0x0048 | Guid | PT_CLSID | GUID |
| 0x00FB | ServerId | | |
| 0x00FD | Restriction | | |
| 0x00FE | RuleAction | | |
| 0x0102 | Binary | PT_BINARY | 바이트 열 |

- 0x1000 은 다중 값 (Multi-value) 표시입니다. 0x101F 는 유니코드 문자열 배열, 0x1102 는 바이너리 배열, 0x1040 은 시각 배열입니다.
- 0x2000 은 다중 인스턴스 (Multi instance) 표시입니다.
- 문자열·바이너리 배열은 `[개수 4바이트][요소 위치 4바이트 × 개수][요소 데이터]` 구조입니다.
- 요소 위치가 겹치면 그 요소는 빈 값입니다.
- 문자열 속성 이름 끝의 `_A` 는 ASCII, `_W` 는 와이드 문자열을 뜻합니다.

### 자주 보는 태그 속성 (libfmapi)

아래 이름은 libfmapi 가 쓰는 이름입니다[8].

**메시지 기본**

| 식별자 | 이름 | 내용 |
|---|---|---|
| 0x001A | PidTagMessageClass (PR_MESSAGE_CLASS) | 메시지 클래스 문자열 |
| 0x0037 | PidTagSubject (PR_SUBJECT) | 제목 전체 |
| 0x0070 | PidTagConversationTopic (PR_CONVERSATION_TOPIC) | 대화 주제 |
| 0x0E07 | PidTagMessageFlags | 상태 비트. 아래 표를 봅니다 |
| 0x0E08 | PidTagMessageSize | 메시지에 붙은 모든 속성 크기의 합(바이트) |
| 0x0E1B | PR_HASATTACH (Microsoft 문서 이름 PidTagHasAttachments) | Boolean. 첨부가 하나 이상이면 참. 저장소가 MessageFlags 의 HASATTACH 비트에서 옮겨 적습니다 (Microsoft 문서). libfmapi 설명은 "Unknown" |

**보낸이와 받는이**

| 식별자 | 이름 | 내용 |
|---|---|---|
| 0x0042 | PidTagSentRepresentingName | 보낸이가 대신한 사용자의 이름 |
| 0x0065 | PidTagSentRepresentingEmailAddress | 보낸이가 대신한 사용자의 주소 |
| 0x0C1A | PidTagSenderName | 보낸이 표시 이름 |
| 0x0C1F | PidTagSenderEmailAddress | 보낸이 주소 |
| 0x0C15 | PidTagRecipientType | 수신자 형식. 아래 표를 봅니다 |
| 0x0E02 | PidTagDisplayBcc | 숨은 참조 표시 |
| 0x0E03 | PidTagDisplayCc | 참조 표시 |
| 0x0E04 | PidTagDisplayTo | 받는이 표시 |
| 0x3001 | PidTagDisplayName | 표시 이름 |
| 0x3002 | PidTagAddressType (PR_ADDRTYPE) | 주소 형식 |
| 0x3003 | PidTagEmailAddress | 주소 |
| 0x39FE | PidTagSmtpAddress | SMTP 주소 |

**인터넷 헤더와 짝이 되는 속성**

| 식별자 | 이름 | 내용 |
|---|---|---|
| 0x007D | PidTagTransportMessageHeaders (PR_TRANSPORT_MESSAGE_HEADERS) | 전송 봉투 정보. SMTP 메일 헤더가 들어 있습니다 |
| 0x1035 | PidTagInternetMessageId | RFC 2822 메시지 식별자 (`Message-ID`) |
| 0x1039 | PR_INTERNET_REFERENCES (Microsoft 문서 이름 PidTagInternetReferences) | `References` 칸의 값 (Microsoft 문서). libfmapi 설명은 "Unknown" |
| 0x1042 | PR_IN_REPLY_TO_ID | `In-Reply-To` |

**본문**

| 식별자 | 이름 | 내용 |
|---|---|---|
| 0x1000 | PidTagBody | 일반 텍스트 본문 |
| 0x1009 | PidTagRtfCompressed | RTF 본문 (Binary). 보통 LZFu 로 압축돼 있습니다 |
| 0x1013 | PidTagBodyHtml / PidTagHtml | HTML 본문. 문자열이면 PidTagBodyHtml, 바이너리면 PidTagHtml |

**첨부**

| 식별자 | 이름 | 내용 |
|---|---|---|
| 0x3701 | PidTagAttachDataBinary / PidTagAttachDataObject | 바이너리면 첨부 데이터. Object(0x000D)면 OLE 저장소로 접근하는 첨부 객체 |
| 0x3704 | PidTagAttachFilename | 짧은 파일 이름 |
| 0x3707 | PidTagAttachLongFilename | 긴 파일 이름 |
| 0x3705 | PidTagAttachMethod | 첨부 방식. 아래 표를 봅니다 |

**시각**

| 식별자 | 이름 (libfmapi) | 형식 | 설명 (libfmapi) |
|---|---|---|---|
| 0x0039 | PidTagClientSubmitTime (PR_CLIENT_SUBMIT_TIME) | Filetime | 보낸이가 메시지를 제출한 날짜·시각 |
| 0x0055 | PR_ORIGINAL_DELIVERY_TIME | Filetime | "Unknown" |
| 0x0E06 | PidTagOriginalDeliveryTime (PR_MESSAGE_DELIVERY_TIME) | Filetime | "Message delivery time / Contains a copy of the original message's delivery date and time in a thread." |

두 속성의 공식 이름과 뜻은 아래와 같습니다[3][4].

| 식별자 | Microsoft 문서 이름 | 뜻 (Microsoft 문서) |
|---|---|---|
| 0x0E06 | PidTagMessageDeliveryTime (PR_MESSAGE_DELIVERY_TIME) | 메시지가 배달된 시각. 서버에 메시지가 저장된 시각이고, 전송 제공자가 서버에서 로컬 저장소로 내려받은 시각이 아닙니다 |
| 0x0055 | PidTagOriginalDeliveryTime (PR_ORIGINAL_DELIVERY_TIME) | 원래 메시지의 배달 시각 사본. 답장·전달할 때 원래 메시지의 0x0E06 값을 옮겨 적습니다 |
| 0x3007 | PidTagCreationTime | Filetime | 메시지를 만든 날짜·시각 |
| 0x3008 | PidTagLastModificationTime | Filetime | 객체나 하위 객체를 마지막으로 고친 날짜·시각 |

- libfmapi 표의 0x0E06 이름 칸과 설명에는 0x0055 의 이름과 설명이 섞여 있습니다.
- 두 속성은 Microsoft 문서 기준으로 읽습니다.

### 비트와 열거 값 (libfmapi)

**0x0E07 PidTagMessageFlags 비트**

| 비트 | 이름 |
|---|---|
| 0x1 | READ |
| 0x2 | UNMODIFIED |
| 0x4 | SUBMIT |
| 0x8 | UNSENT |
| 0x10 | HASATTACH |
| 0x20 | FROMME |
| 0x40 | ASSOCIATED |
| 0x80 | RESEND |
| 0x100 | RN_PENDING |
| 0x200 | NRN_PENDING |
| 0x1000 | ORIGIN_X400 |

**0x0C15 PidTagRecipientType 값**

| 값 | 이름 | 뜻 |
|---|---|---|
| 0 | ORIG | 보낸이 |
| 1 | TO | 받는이 |
| 2 | CC | 참조 |
| 3 | BCC | 숨은 참조 |
| 0x10000000 | P1 | 재전송 |
| 0x80000000 | SUBMITTED | 제출됨 |

**0x3705 PidTagAttachMethod 값**

| 값 | 이름 |
|---|---|
| 0 | 없음 |
| 1 | BY_VALUE |
| 2 | BY_REFERENCE |
| 3 | BY_REF_RESOLVE |
| 4 | BY_REF_ONLY |
| 5 | EMBEDDED_MSG |
| 6 | OLE |

### 이름 붙은 속성 (libfmapi)

속성에 이름을 짓는 방식은 셋입니다.

| 방식 | 부르는 이름 | 예 |
|---|---|---|
| 16비트 식별자 (태그 속성) | PR_, PidTag | PidTagSubject |
| 문자열 이름 | PidName | `X-Originating-IP` |
| 32비트 숫자 이름 | LID_, PidLid | — |

- PFF(PST·OST)는 이름 붙은 속성을 name-to-id map 으로 실제 번호에 대응시킵니다.
- 이름과 번호 사이의 변환은 `IMAPIProp::GetIDsFromNames`·`GetNamesFromIDs` 로 합니다.
- 이름 붙은 속성은 속성 집합 GUID 와 함께 이름을 짓습니다. 아래 GUID 는 모두 뒤가 `-0000-0000-c000-000000000046` 입니다.

| 속성 집합 | GUID 앞부분 |
|---|---|
| PS_MAPI | 00020328 |
| PS_PUBLIC_STRINGS | 00020329 |
| PS_INTERNET_HEADERS | 00020386 |
| PSETID_Appointment | 00062002 |
| PSETID_Task | 00062003 |
| PSETID_Address | 00062004 |
| PSETID_Common | 00062008 |
| PSETID_Log (업무 일지) | 0006200A |
| PSETID_Note (메모) | 0006200E |
| PSETID_Sharing | 00062040 |

- PS_INTERNET_HEADERS 집합에는 `Content-Type`·`Content-Transfer-Encoding`·`Accept-Language` 같은 인터넷 헤더 이름이 PidName 속성으로 들어 있습니다.
- 같은 이름 붙은 속성이 저장소마다 같은 번호를 받는다고 보지 않습니다. 0x8000 이상 속성은 번호가 아니라 GUID 와 이름으로 가립니다.
- GUID 표기는 [윈도 식별자 형식](../value-decoding/sid-guid-clsid-known-folder-id.md) 에서 다룹니다.

## 읽는 법

1. **저장소 형식부터 풉니다.** PST·OST·NK2 는 [아웃룩](../../02-artifacts/mail/outlook/index.md), Exchange EDB 는 [ESE 데이터베이스](../database-log-formats/extensible-storage-engine/index.md) 를 따라 속성 목록까지 갑니다.
2. **식별자와 값 형식을 따로 적습니다.** 둘을 짝으로 속성을 가립니다.
3. **범위로 성격을 봅니다.** MAPI 정의인지, 제공자가 정한 것인지, 전송 안 되는 속성인지 위 범위 표로 봅니다.
4. **0x8000 이상은 대응표로 풉니다.** 저장소의 name-to-id map 에서 GUID 와 이름(문자열이나 숫자)을 찾습니다.
5. **값 형식대로 풉니다.** 문자열은 끝 NUL 에 기대지 말고 저장소가 적은 길이로 자릅니다. String8 은 코드 페이지를 확인합니다.
6. **시각을 풉니다.** Time(0x0040)은 FILETIME, FloatingTime(0x0007)은 1899-12-30 기준 날 수입니다. FILETIME 은 [시각 값 형식](../value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
7. **본문 세 가지를 비교합니다.** 0x1000(텍스트), 0x1009(압축 RTF), 0x1013(HTML)이 모두 있으면 내용이 서로 맞는지 봅니다. RTF 는 LZFu 압축을 풀어서 읽습니다.
8. **원래 헤더와 대조합니다.** 0x007D 의 헤더를 [인터넷 메일 형식](eml-mbox-rfc-5322-mime.md) 대로 읽습니다. 그 안의 `Message-ID`·`In-Reply-To` 를 0x1035·0x1042·0x1039 와 맞춰 봅니다.

### 헥스로 한 번 따라가기

아래 값은 위 규칙대로 만든 예시이며 실제 저장소에서 옮긴 바이트가 아닙니다.

**같은 제목 `Re` 를 두 값 형식으로 적을 때**

```
String (0x001F, UTF-16LE)   52 00 65 00     R.e.
String8 (0x001E)            52 65           Re
```

- 끝 NUL 이 없을 때도 있으므로 둘 다 끝 NUL 이 없는 꼴로 적었습니다[8].
- String8 의 한글은 코드 페이지를 알아야 풉니다. [문자 인코딩](../value-decoding/utf-16le-utf-8-cp949.md) 을 봅니다.

**다중 값 문자열 (0x101F) 의 뼈대**

```
[개수: 4바이트][위치 1: 4바이트][위치 2: 4바이트][요소 1 데이터][요소 2 데이터]
```

- 요소가 둘이면 위치 칸도 둘이고, 두 위치가 겹치면 그 요소는 빈 값입니다. 파일이 깨진 것으로 보지 않습니다.

**FloatingTime (0x0007) 계산**

| double 값 | 정수 부분 | 소수 부분 | 풀이 |
|---|---|---|---|
| 0.0 | 0일 | 0 | 1899-12-30 00:00 |
| 1.5 | 1일 | 0.5일 | 1899-12-31 12:00 |

**Currency (0x0006) 계산**

- 정수 327500 은 327500 ÷ 10000 = 32.7500 입니다.

## 포렌식에서 중요한 점

### 시각 속성마다 뜻이 다릅니다

- 제출 시각(0x0039), 만든 시각(0x3007), 마지막으로 고친 시각(0x3008), 배달 시각(0x0E06)이 따로 있습니다.
- 0x0E06 은 서버에 저장된 시각입니다. PC 로 내려받은 시각으로 적지 않습니다[3].
- 0x3008 은 객체나 하위 객체를 마지막으로 고친 시각입니다[8]. 첨부 같은 하위 객체를 고쳐도 이 시각이 바뀔 수 있습니다.
- 0x3007 이 이 저장소에 사본을 만든 시각인지, 원래 메시지를 만든 시각인지는 공식 설명으로 가려지지 않습니다. 다른 시각과 대조한 뒤에 씁니다.
- 0x0055 는 이 메시지의 배달 시각이 아닙니다. 답장·전달한 원래 메시지의 배달 시각 사본입니다[4].
- 0x007D 에 원래 헤더가 있으면 그 안의 `Date`·`Received` 시각과 비교합니다. 헤더 시각의 뜻은 [인터넷 메일 형식](eml-mbox-rfc-5322-mime.md) 에서 다룹니다.
- 보고서에는 "0x0039 속성에 이 시각이 있다" 처럼 속성 번호를 붙여 씁니다.

### 전송 안 되는 속성은 이쪽 저장소의 상태입니다

- 0x0E00–0x0FFF 는 전송 안 되는 메시지 속성 범위이고, 0x0E07 PidTagMessageFlags 도 이 범위에 있습니다.
- 이 속성은 보낸 쪽과 받은 쪽에 모두 있고, 클라이언트나 저장소에 따라 값이 다릅니다[7].
- 그래서 READ 같은 비트는 이 저장소 쪽 상태로 읽습니다. 상대방에게 넘어간 값으로 읽지 않습니다.
- 받은 메시지의 READ 비트는 저장소가 처음에 끕니다. 그 뒤 클라이언트가 읽음 표시 함수로 켜거나 끌 수 있습니다[7].
- 따라서 READ 비트는 "읽음으로 표시된 상태" 까지만 말합니다. 사람이 내용을 읽었다는 뜻으로 적지 않습니다.

### 첨부 여부는 세 곳에서 봅니다

- MessageFlags 의 HASATTACH 비트(0x10)
- PR_HASATTACH(0x0E1B). 저장소가 HASATTACH 비트에서 옮겨 적는 값입니다[5]
- 실제 첨부 객체와 0x3705 첨부 방식

세 곳이 서로 다르면 그 차이를 보고서에 그대로 적습니다.

### Bcc

- 받은 쪽 헤더에서는 `Bcc` 줄이 빠질 수 있습니다. [인터넷 메일 형식](eml-mbox-rfc-5322-mime.md) 을 봅니다.
- MAPI 에는 숨은 참조를 담는 자리가 따로 있습니다. 0x0E02 PidTagDisplayBcc 와 수신자 형식 3(BCC)입니다.
- 숨은 수신자를 찾을 때는 보낸 쪽 저장소의 이 자리를 확인합니다.

### 크기

- 0x0E08 은 메시지에 붙은 속성 크기의 합이므로 보낸 원래 메일의 바이트 수와 같다고 보지 않습니다.

### 보호된 속성

- 0x67F0~0x67FF 보안 프로필 속성은 숨기거나 암호화할 수 있으므로, 값을 못 읽었다고 비어 있다고 적지 않습니다.

### 지운 메시지

- 속성 값은 저장소 형식 안에 들어 있고, 지운 항목과 빈 블록에서 속성을 되살리는 법은 [아웃룩](../../02-artifacts/mail/outlook/index.md) 과 [ESE 데이터베이스](../database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다.

## 함정

- **식별자만 보고 속성을 정합니다.** 0x0E08, 0x1013, 0x3701 처럼 값 형식에 따라 다른 속성이 됩니다.
- **문자열 끝 NUL 을 믿습니다.** String·String8 모두 끝 NUL 이 없을 때가 있습니다.
- **`_A` 속성을 UTF-16 으로 읽습니다.** `_A` 는 ASCII, `_W` 는 와이드 문자열입니다. String8 은 코드 페이지를 알아야 합니다.
- **Boolean 을 0/1 로만 봅니다.** 0 이 아니면 모두 참입니다.
- **FloatingTime 을 FILETIME 기준으로 풉니다.** FloatingTime 은 1899-12-30 부터 센 날 수입니다. FILETIME 은 1601-01-01 부터 센 100ns 단위입니다.
- **Currency 를 정수 그대로 적습니다.** 10000 으로 나눕니다.
- **0x8000 이상 번호를 고정 번호표로 풉니다.** 대응표에서 GUID 와 이름을 찾아 가립니다.
- **도구가 보여 준 이름을 공식 이름으로 씁니다.** 0x0E06 처럼 자료마다 이름이 어긋나는 속성이 있습니다. libfmapi 는 0x0E06 이름 칸에 0x0055 의 이름을 적습니다. 보고서에는 번호와 값 형식을 함께 적습니다.
- **"Unknown" 설명을 뜻 없음으로 봅니다.** 0x0055, 0x0E1B, 0x1039 는 libfmapi 설명이 "Unknown" 이지만 Microsoft 문서에는 뜻이 있습니다. 뜻은 공식 문서에서 찾습니다.
- **다중 값의 빈 요소를 손상으로 봅니다.** 위치가 겹치면 빈 값입니다.
- **압축 RTF 를 그대로 검색합니다.** 0x1009 는 보통 LZFu 로 압축돼 있습니다. 풀기 전에는 글자 검색에 걸리지 않습니다. [파일 내용 검색](../../03-techniques/analysis/content-search/index.md) 을 봅니다.

## 도구

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| libpff (pffexport 등) | PST·OST 안의 항목과 속성을 꺼냅니다 |
| libfmapi 문서 | 속성 번호·값 형식 번호표로 씁니다 |
| 헥스 편집기 | 문자열 인코딩, 다중 값 구조를 직접 봅니다 |

도구마다 속성 이름이나 시각이 다르면 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.
메일 주고받은 기록을 사람 단위로 묶는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 를 봅니다.

## 참고 문헌

1. Microsoft Learn, *MAPI Property Identifier Overview* (2014-11-16) — https://learn.microsoft.com/en-us/office/client-developer/outlook/mapi/mapi-property-identifier-overview
2. Microsoft Learn, *MAPI property tags* (2014-11-16) — https://learn.microsoft.com/en-us/office/client-developer/outlook/mapi/mapi-property-tags
3. Microsoft Learn, *PidTagMessageDeliveryTime Canonical Property* — https://learn.microsoft.com/en-us/office/client-developer/outlook/mapi/pidtagmessagedeliverytime-canonical-property
4. Microsoft Learn, *PidTagOriginalDeliveryTime Canonical Property* — https://learn.microsoft.com/en-us/office/client-developer/outlook/mapi/pidtagoriginaldeliverytime-canonical-property
5. Microsoft Learn, *PidTagHasAttachments Canonical Property* — https://learn.microsoft.com/en-us/office/client-developer/outlook/mapi/pidtaghasattachments-canonical-property
6. Microsoft Learn, *PidTagInternetReferences Canonical Property* — https://learn.microsoft.com/en-us/office/client-developer/outlook/mapi/pidtaginternetreferences-canonical-property
7. Microsoft Learn, *PidTagMessageFlags Canonical Property* — https://learn.microsoft.com/en-us/office/client-developer/outlook/mapi/pidtagmessageflags-canonical-property
8. libyal libfmapi, *Message API (MAPI) definitions* (문서 판 0.0.32, 2023-03) — https://raw.githubusercontent.com/libyal/libfmapi/main/documentation/MAPI%20definitions.asciidoc
