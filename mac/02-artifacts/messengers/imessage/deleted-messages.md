---
title: "지운 메시지의 흔적"
parent: "메시지"
grand_parent: "아티팩트 · 메시지·메신저"
nav_order: 1370
---

# 지운 메시지의 흔적 (Deleted Messages)

메시지 앱에서 지운 메시지는 최대 30일 동안 최근 삭제 폴더(Recently Deleted)에 남아 `chat.db` 의 `chat_recoverable_message_join` 표에서 보이고, 그 뒤에도 SQLite의 빈 페이지와 WAL 파일, 상대 기기와 백업에 흔적이 남을 수 있습니다 [1][2][4].

## 무엇을 기록하나 · 왜 생기나

지운 메시지와 첨부는 최근 삭제 폴더에 최대 30일 동안 남고, 그 안에는 되살릴 수 있습니다 [1]. 사용자는 30일이 되기 전에 그 폴더에서 영구 삭제할 수도 있습니다 [1]. 30일이 지나면 모든 기기에서 지워지고, 40일이 지나면 iCloud에서도 영구 삭제됩니다 [1].

Messages in iCloud를 켜 두면 한 기기에서 지우거나 되살린 것이 이 기능을 켠 모든 기기에 반영됩니다 [1]. 그래서 맥 한 대의 `chat.db` 에서 메시지가 사라졌다고 해서 이 맥에서 지웠다고 단정하지 않고, 같은 계정의 다른 기기에서 지운 것이 동기화됐을 가능성을 함께 따집니다. Messages in iCloud를 켰는지가 남는 파일과 키는 실제 데이터로 확인해야 합니다. 반대로 내가 지워도 받는 사람 화면에는 영향이 없어서 [1], 상대 기기와 그 백업은 지운 쪽과 별개인 증거원이 됩니다.

사용자가 지우지 않아도 메시지가 사라질 수 있습니다. 메시지 앱의 Messages 메뉴에서 Settings를 열고 General에 있는 "Keep messages" 를 Forever가 아닌 값으로 두면, 정한 기간이 지난 대화를 첨부까지 함께 자동으로 지웁니다 [1]. 선택지의 정확한 이름과 이 설정이 저장되는 plist 파일·키는 실제 데이터로 확인해야 합니다.

보내기 취소와 편집이 남기는 흔적은 [대화 DB (chat.db)](chat-db.md)의 편집·보내기 취소 절에서 다룹니다.

## 위치와 버전별 차이

지운 메시지를 찾을 곳을 층으로 나누면 아래와 같습니다.

| 층 | 자리 | 남는 기간 |
|---|---|---|
| 최근 삭제 폴더 | `chat.db` 의 `chat_recoverable_message_join` 표 [2] | 최대 30일 [1] |
| iCloud | Messages in iCloud를 쓸 때의 서버 쪽 | 40일이 지나면 영구 삭제 [1] |
| SQLite 빈 공간 | `chat.db` 의 freelist 페이지와 b-tree 페이지 안 freeblock [4] | 다른 데이터로 덮일 때까지 |
| WAL | `chat.db-wal` 의 옛 프레임 [4] | 체크포인트와 파일 재사용에 따라 다름 |
| 상대 기기·백업 | 받는 사람의 기기, iOS 백업 | 지운 쪽의 동작과 무관 [1] |

iOS 백업 안 메시지 DB의 파일 이름은 [대화 DB (chat.db)](chat-db.md)의 위치 절에 있습니다.

맥에 최근 삭제 폴더가 처음 들어온 버전은 흔히 macOS 13 Ventura로 알려져 있지만, Apple 설명서는 macOS Catalina 10.15 이후 여러 버전을 한 페이지로 다루고 도입 버전을 적지 않습니다 [1]. 분석 대상의 macOS 버전을 먼저 확인하고, `chat_recoverable_message_join` 표가 있는지를 사본에서 직접 봅니다.

## 구조

### 최근 삭제 표

`chat_recoverable_message_join` 은 최근 삭제된 메시지를 담는 표입니다 [2]. 이 표에서 메시지를 지운 대화의 `rowid` 를 얻을 수 있고, imessage-database는 이 값을 `deleted_from` 으로 보여 줍니다. 30일 안이면 되살릴 수 있습니다 [3]. 도구가 메시지마다 `deleted_from` 을 붙여 보여 주므로, 최근 삭제 폴더에 있는 동안 메시지 행이 남아 있는 것으로 보입니다. `deleted_from` 은 도구가 붙인 이름이라서 표의 열 이름으로 옮기지 않습니다. 이 표의 실제 열 이름과 삭제 시각 열이 있는지, 있다면 어떤 기준의 시각인지는 사본에서 표 정의부터 보고 확인합니다.

### SQLite 빈 공간과 WAL

행을 지워 비게 된 페이지는 freelist로 관리합니다 [4]. DB 헤더에서 필요한 필드는 아래와 같습니다.

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 16 | 2바이트 | 페이지 크기. 512~32768 사이의 2의 거듭제곱이고, 값 1은 65536을 뜻합니다 [4] |
| 32 | 4바이트 | 첫 freelist trunk 페이지 번호. 없으면 0 [4] |
| 36 | 4바이트 | freelist 페이지 총수 [4] |

trunk 페이지는 4바이트 빅엔디언 정수의 배열이고, 첫 값은 다음 trunk 페이지 번호(마지막이면 0), 둘째 값은 그 뒤에 이어지는 leaf 페이지 번호의 개수입니다 [4]. freelist leaf 페이지는 정보를 담지 않는 페이지로 다루고, SQLite는 입출력을 줄이려고 leaf 페이지를 읽지도 쓰지도 않으려 합니다 [4]. 그래서 leaf 페이지에는 지우기 전 내용이 덮이지 않고 남을 수 있습니다. 다만 지운 내용을 0으로 덮는 `secure_delete` 같은 설정에 따라 달라지므로, `chat.db` 의 `secure_delete`·`auto_vacuum` 설정값을 실제 데이터로 확인합니다.

페이지 전체가 비지 않고 페이지 안 일부만 빈 경우에는 freeblock 체인으로 관리합니다 [4]. b-tree 페이지 머리의 두 번째 필드가 첫 freeblock의 오프셋이고, freeblock의 앞 2바이트는 다음 freeblock 오프셋(빅엔디언, 마지막이면 0), 다음 2바이트는 4바이트 머리를 포함한 크기입니다 [4].

WAL 파일은 DB와 같은 폴더에 DB 이름 뒤에 `-wal` 을 붙여 생기고, 32바이트 머리 뒤에 프레임이 이어집니다 [4]. 프레임 하나는 24바이트 프레임 머리와 페이지 크기만큼의 데이터로 이루어지고, 한 페이지의 바뀐 내용을 담습니다 [4]. 같은 페이지의 판이 여러 개 있으면 커밋된 마지막 판을 읽고 [4], 그 앞의 옛 판에는 지우기 전 내용이 남아 있을 수 있습니다. 체크포인트 때는 WAL의 유효한 내용이 DB 파일로 옮겨지고 [4], 옛 판은 `-wal` 파일 안에만 있어서 수집할 때 이 파일을 빠뜨리면 함께 잃습니다. 프레임 머리의 필드와 페이지 번호로 파일 안 위치를 찾는 법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** `chat_recoverable_message_join` 에 행이 있으면, 수집 시점에 그 메시지가 최근 삭제 폴더에 있었다는 사실, 곧 지운 지 30일이 지나지 않아 되살릴 수 있는 상태였다는 사실을 보여 줍니다 [1][2][3]. freelist 페이지나 WAL의 옛 프레임에서 메시지 행을 되살리면, 그 내용이 한때 이 DB에 기록되어 있었다는 사실을 보여 줍니다.

**증명하지 못하는 것.** 어느 기기에서 지웠는지는 Messages in iCloud 동기화 때문에 맥 한 대의 기록만으로 판별하기 어렵고 [1], 누가 지웠는지도 이 표로는 알 수 없습니다. 이 표로는 삭제 시각을 정할 수 없으니 지운 시각은 적지 않습니다. 메시지가 DB에 없다는 사실만으로 사용자가 지웠다고 말할 수도 없는데, "Keep messages" 설정이 기간 지난 대화를 자동으로 지우기 때문입니다 [1]. 빈 공간에서 되살린 조각은 어느 표의 어느 행이었는지 문맥이 빠져 있을 수 있어서, 조각 안의 GUID나 시각 값으로 남은 행과 이어지는지 확인한 만큼만 씁니다.

보고서에는 "`chat.db` 의 `chat_recoverable_message_join` 표에 메시지 rowid ○○ 행과 이어진 기록이 있고, 이는 수집 시점에 이 메시지가 최근 삭제 폴더에 있었음을 뜻한다" 처럼 씁니다.

## 시각 해석

최근 삭제 표에서 삭제 시각을 읽을 수 있는지는 분석 대상의 표 정의로 확인합니다. 빈 공간이나 WAL에서 되살린 메시지 행에 `date` 값이 온전히 남아 있으면 [대화 DB (chat.db)](chat-db.md)의 시각 해석 절에 따라 풀고, 그 값은 메시지를 기록한 시각이지 지운 시각이 아니라는 점을 보고서에 밝힙니다. 옛 판이 언제 쓰였는지는 되살린 행 안의 값으로만 짐작합니다.

## 함정과 한계

사용자는 최근 삭제 폴더에서 30일이 되기 전에 영구 삭제할 수 있고 [1], "Keep messages" 기간을 짧게 두면 오래된 대화가 스스로 사라집니다 [1]. 두 경우 모두 앱 쪽에는 흔적이 적게 남아서, 빈 공간과 WAL, 상대 기기, 백업을 함께 봅니다. 증거를 없애려 한 정황을 따지는 흐름은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에 있습니다.

메시지 삭제를 기록하는 통합 로그 서브시스템과, 알림 기록이나 Spotlight, Time Machine에 메시지 내용이 남는지와 그 경로는 분석 대상에서 직접 찾아봅니다. 이런 곳을 뒤질 때는 무엇을 찾았는지와 함께 확인 범위를 보고서에 적습니다.

옛 판이 남은 WAL 프레임은 되살릴 대상이라서, 원본은 열지 않고 `chat.db` 와 `-wal` 파일을 함께 뜬 사본에서 분석합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시이고, 실제 데이터에서 나온 값이 아닙니다. 먼저 DB 헤더의 오프셋 16과 32~39를 봅니다(`..` 는 여기서 쓰지 않는 바이트입니다).

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000010  10 00 .. .. .. .. .. .. .. .. .. .. .. .. .. ..
00000020  00 00 00 05 00 00 00 03 .. .. .. .. .. .. .. ..
```

오프셋 16의 `10 00` 은 페이지 크기 4096이고, 오프셋 32의 `00 00 00 05` 는 첫 trunk 페이지가 5번이라는 뜻, 오프셋 36의 `00 00 00 03` 은 freelist 페이지가 모두 세 개라는 뜻입니다. 5번 페이지의 앞부분이 아래와 같다면,

```
00 00 00 00  00 00 00 02  00 00 00 07  00 00 00 09
```

다음 trunk 페이지는 없고(0), 뒤에 leaf 페이지 번호 두 개가 이어지며, 그 번호가 7과 9입니다. trunk 한 장과 leaf 두 장을 더한 세 장이 헤더의 freelist 총수와 맞고, 7번과 9번 페이지를 통째로 떠서 메시지 GUID나 본문 문자열을 찾습니다.

페이지 안 빈 공간도 같은 식으로 봅니다. b-tree 페이지 머리의 두 번째 필드 값이 `0F 80` 이라면 그 페이지 안 0x0F80 자리에서 첫 freeblock이 시작합니다.

```
0F80  00 00 00 28 ...
```

앞 2바이트 `00 00` 은 다음 freeblock이 없다는 뜻이고, 다음 2바이트 `00 28` 은 머리 4바이트를 포함한 크기 40바이트라서, 그 뒤 36바이트에 지운 행의 조각이 남아 있을 수 있습니다.

WAL 파일에서는 32바이트 머리 뒤로 프레임이 24바이트 머리와 페이지 데이터 묶음으로 이어지고, 페이지 크기가 4096이면 프레임 하나가 4120바이트라서 첫 프레임은 오프셋 0x20, 둘째 프레임은 0x1038에서 시작합니다 [4].

### 공개 도구로 한 번

sqlite3로 사본을 열고 `.schema chat_recoverable_message_join` 으로 표 정의를 먼저 본 뒤 행 수를 셉니다. 같은 사본을 imessage-exporter 계열 도구로 읽으면 최근 삭제 폴더에 있는 메시지에 `deleted_from` 이 붙어 나오므로 [3], SQL로 센 행 수와 맞춰 봅니다. 빈 페이지와 WAL을 되살리는 일반 절차는 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)에 있습니다.

## 교차 검증

| 함께 볼 자료 | 확인할 것 |
|---|---|
| [대화 DB (chat.db)](chat-db.md) | 남은 메시지 행, 편집·보내기 취소 기록, iOS 백업 안 DB 이름 |
| [첨부 파일 (Attachments)](attachments.md) | 메시지와 함께 지워졌거나 따로 지운 첨부 |
| [아이폰·아이패드 연결 (iOS Devices)](../../external-devices/ios-devices/index.md) | 맥에 남은 iOS 백업 안의 메시지 DB |
| [타임 머신 (Time Machine)](../../filesystem/time-machine/index.md) | 지우기 전 시점의 사본이 백업에 있는지 |
| [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) | 페이지·WAL 구조 |
| [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md) | 지운 첨부 파일의 파일 시스템 흔적 |
| [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md) | 지운 대화를 포함한 연락 재구성 |

## 실습

공개 시험 이미지(NIST CFReDS 등) 가운데 맥 사용자 폴더와 메시지 기록이 들어 있는 이미지를 골라 아래 질문을 풀어 봅니다.

1. 이미지의 macOS 버전에서 `chat_recoverable_message_join` 표가 있는가, 있다면 행은 몇 개인가?
2. `chat.db` 헤더의 첫 freelist trunk 페이지 번호와 freelist 페이지 총수는 얼마인가?
3. freelist leaf 페이지에서 메시지 GUID나 본문으로 보이는 문자열이 나오는가, 나온다면 그 GUID가 `message` 표에 아직 있는가?
4. `chat.db-wal` 이 있다면 같은 페이지의 판이 몇 개 들어 있고, 옛 판에만 있는 메시지가 있는가?

## 참고 문헌

1. Apple 지원, "Delete messages and conversations" (Messages 사용 설명서, macOS Catalina 10.15 이후) — https://support.apple.com/guide/messages/delete-messages-and-conversations-icht1035/mac
2. imessage_database table.rs 소스 (docs.rs) — https://docs.rs/imessage-database/latest/src/imessage_database/tables/table.rs.html
3. imessage_database::tables::messages::message::Message (docs.rs) — https://docs.rs/imessage-database/latest/imessage_database/tables/messages/message/struct.Message.html
4. SQLite Database File Format (sqlite.org) — https://www.sqlite.org/fileformat2.html
