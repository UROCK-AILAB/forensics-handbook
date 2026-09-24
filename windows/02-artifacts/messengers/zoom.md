# 줌 (Zoom)

## 한 줄 요약

줌 (Zoom) PC 앱은 사용자 프로필의 `%APPDATA%\Zoom` 에 설정 파일·로그·SQLite 데이터베이스를 남깁니다[1][2]. 로컬 녹화 파일은 이와 따로 `문서\Zoom` 폴더에 둡니다[1][2]. 관찰한 최신 버전에서는 `data` 폴더의 DB 대부분이 파일 전체가 암호화돼 있었습니다. 그래서 키 없이 바로 읽을 수 있는 것은 설정 파일, 폴더 이름, 평문 DB 세 개뿐이었습니다(확인 범위: Windows 11 PC 한 대, 줌 7.1.5.43453).

## 무엇을 기록하나 · 왜 생기나

- 줌은 화상 회의와 채팅을 하는 앱입니다.
- 앱은 설정과 사용 기록을 사용자 프로필 안에 저장합니다. 그래서 사용자마다 흔적이 따로 생깁니다.
- 사용자가 회의를 로컬 녹화하면 녹화 파일이 `문서\Zoom` 에 생깁니다[1][2].

2021년에 나온 업체 블로그는 줌 아티팩트를 SQLite DB 로 설명합니다[2]. 이 블로그는 표마다 사용자 행동 정보가 있다고 적었고, 다음 항목을 들었습니다[2].

| 항목 | 블로그가 적은 내용 |
|---|---|
| 채팅 | 대화 메시지, 주고받은 파일, 세션(대화방), 검색어 |
| 사람 | 연락처, 그룹, 친구 요청 |
| 통화·회의 | 통화 기록, 회의 기록, 회의 중 메시지 |
| 계정 | 사용자 계정, 로그인 기기 |
| 그 밖 | 행동 로그, 설정 |

(표는 [2])

- 회의 기록에는 호스트 ID·회의 번호·주제·참가 시각·회의 길이·녹화 경로가 들어 있다고 적었습니다[2].
- 회의 중 메시지, 사용자 계정, 로그인 기기의 비밀번호 칸은 "암호화됨" 으로 표시했습니다[2].
- 이 블로그는 DB 파일 이름, 표 이름, 암호 방식, 대상 버전을 적지 않았습니다[2]. 그래서 아래 관찰 결과와 항목을 하나씩 맞춰 볼 수 없습니다.

## 위치와 버전별 차이

### 위치

| 흔적 | 위치 | 근거 |
|---|---|---|
| 데이터 폴더 (Windows 7·10) | `C:\Users\<사용자>\AppData\Roaming\Zoom` 과 그 아래 `data\` | [2] |
| 데이터 폴더 (Windows XP) | `C:\Documents and Settings\<사용자>\Application Data\Zoom` 과 그 아래 `data` | [2]. [1] 은 이 폴더를 통째로 모읍니다 |
| 로그 | `C:\Users\<사용자>\AppData\Roaming\Zoom\logs` | [1] |
| 로컬 녹화 | `C:\Users\<사용자>\Documents\Zoom` | [1][2] |
| Outlook 플러그인 설정 | `C:\Users\<사용자>\AppData\Roaming\Zoom Plugin\*.json` | [1] |

- 최신 버전에서도 로컬 녹화 기본 위치가 `문서\Zoom` 인지는 확인하지 못했습니다.
- 사용자가 녹화 위치를 바꾸면 그 위치가 어디에 적히는지도 확인하지 못했습니다.
- 관리자용 설치본(MSI)이 `Program Files` 에 깔리는지, 그때 데이터 폴더가 달라지는지는 확인하지 못했습니다.

### 관찰한 설치본

이 절은 Windows 11 PC 한 대에서 본 것입니다(확인 범위: Windows 11 PC 한 대, 줌 7.1.5.43453 사용자별 설치본).

- 사용자별 설치였습니다. 실행 파일이 `%APPDATA%\Zoom\bin\Zoom.exe` 에 있었습니다.
- `bin` 폴더에는 파일이 228개 있었습니다.
- 사용자 하이브에 `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\ZoomUMX` 키가 있었습니다.
- 이 키의 `InstallLocation` 값은 `C:\Users\<사용자>\AppData\Roaming\Zoom\bin` 이었습니다.
- `HKCU\Software\Zoom` 아래에는 `SystemInfo`, `WMI` 두 하위 키가 있었습니다. 값은 보지 않았습니다.
- 제거 프로그램은 `%APPDATA%\Zoom\uninstall\Installer.exe` 에 있었습니다.
- `logs` 폴더에는 `zoom_feedback` 폴더 하나만 있었습니다.
- `%LOCALAPPDATA%\Zoom\data` 에는 이모지 자료(`emoji.json`, `Emojis\` 아래 png·svg)만 있었습니다.
- `%LOCALAPPDATA%\Zoom\plugin` 폴더도 있었습니다.
- `문서\Zoom` 폴더는 없었습니다. 이 PC 에서는 로컬 녹화를 하지 않았습니다.

## 구조

### data 폴더의 파일

`data\` 바로 아래 파일입니다(확인 범위: 위와 같음). 크기 단위는 바이트입니다.

| 파일 | 크기 | 첫 16바이트 |
|---|---|---|
| `zoomus.enc.db` | 482,304 | 암호화 |
| `zoommeeting.enc.db` | 10,240 | 암호화 |
| `zoomus.tmp.enc.db` | 2,048 | 암호화 |
| `zoomus.zmdb.kvs.enc.db` | 118,784 | 암호화 |
| `3dCustomAvatar.enc.db` | 104,448 | 암호화 |
| `zoom_conf_local_asr.enc.db` | 5,120 | 암호화 |
| `telemetrydata.db` | 720,896 | 암호화 |
| `local_dns_cache.db` | 13,312 | 암호화 |
| `in_progress_infos.db` | 9,216 | SQLite 머리 |
| `process_monitoring.db` | 6,144 | SQLite 머리 |
| `zoomus.zmdb.default.noenc.rlock.db` | 163,840 | SQLite 머리 |

- "SQLite 머리" 는 첫 16바이트가 `SQLite format 3\0` 인 파일입니다.
- 나머지 DB 는 첫 바이트부터 규칙 없는 값이었습니다. 파일 전체를 암호화한 모양입니다.
- 이름에 `enc` 가 없는 `telemetrydata.db`, `local_dns_cache.db` 도 암호화돼 있었습니다.
- 암호 방식은 확인한 자료에 없습니다. SQLite 파일을 통째로 암호화하는 대표 방식은 [암호화된 SQLite (SQLCipher)](../../01-foundations/database-log-formats/sqlite/sqlcipher.md) 에서 다룹니다.
- 모든 DB 옆에 크기가 0 인 `-journal` 파일이 있었습니다. `-wal`·`-shm` 은 없었습니다.
- 그래서 롤백 저널 (rollback journal) 방식으로 봅니다. 저널 파일의 뜻은 [WAL과 롤백 저널](../../01-foundations/database-log-formats/sqlite/wal-journal-shm.md) 에서 다룹니다.
- 설정 파일 `Zoom.us.ini`, `client.config`, `viper.ini`, `transcoding.ini`, `SSBAvatarCacheIndex.ini` 도 같은 폴더에 있었습니다.

### 평문 DB 세 개의 표

스키마만 봤고 행 내용은 보지 않았습니다(확인 범위: 위와 같음).

| DB | 표 | 칸 이름으로 본 성격 |
|---|---|---|
| `in_progress_infos.db` | `meta`, `InProgressInfos`, `UploadInfos` | 내려받기·올리기 진행 기록으로 보이는 구조 |
| `process_monitoring.db` | `process_metrics`, `meta`, `sqlite_sequence` | 프로세스별 메모리·CPU 사용량 기록으로 보이는 구조 |
| `zoomus.zmdb.default.noenc.rlock.db` | `TZDesc`, `TZZoom`, `TZJAVA`, `TZSelectFiles_`, `TZSelectFiles_en`, `experiment`, `feature_toggle_kvs`, `perf_summary` | 시간대 목록과 기능 설정 위주 |

- `InProgressInfos` 앞쪽 칸: `guid`, `url`, `url_chain`, `fetch_error_body`, `etag`, `last_modified`, `total_bytes`, `mime_type`, `original_mime_type`, `current_path`, `target_path`, `received_bytes`, `start_time`, `end_time`. 그 뒤 칸은 보지 않았습니다.
- `UploadInfos` 앞쪽 칸: `guid`, `state`, `interrupt_reason`, `file_path`, `file_size_at_start`, `file_mtime_at_start`, `sent_bytes`, `uploadid`, `uploadid_enc_`, `upload_path`, `upload_path_enc_`, `upload_metadata`. 그 뒤 칸은 보지 않았습니다.
- `process_metrics` 칸: `id`, `process_name`, `metry_time`, `process_id`, `memory_usage`, `cpu_usage`, `is_in_meeting`.
- `is_in_meeting` 은 이름만 보면 "그 시각에 회의 중이었나" 를 가리키는 듯합니다. 뜻은 검증하지 않았습니다.
- 이 표들에 실제로 어떤 행이 남는지, 행이 얼마나 오래 남는지는 확인하지 못했습니다.

### 계정 폴더

`data\` 아래 계정 관련 폴더입니다(확인 범위: 위와 같음). 계정 식별자는 `<JID>`·`<ID>` 로 가렸습니다.

- `data\<JID>@xmpp.zoom.us\` 폴더가 3개 있었습니다.
- 그 가운데 하나에만 파일이 있었고, 나머지 둘은 비어 있었습니다. 빈 폴더가 예전에 로그인한 다른 계정인지는 확인하지 못했습니다.
- `<JID>` 는 영문·숫자·밑줄로 된 22자 문자열이었습니다.
- 폴더 이름에서는 이 문자열이 소문자로 바뀌어 있었습니다.
- 이 값을 줌 계정 식별자로 보는 것은 이름 모양으로 한 추정입니다.

파일이 있던 계정 폴더의 DB 입니다.

| 파일 | 크기 |
|---|---|
| `<JID>@xmpp.zoom.us.asyn.encks.db` | 491,520 |
| `<JID>@xmpp.zoom.us.common.idx.encks.db` | 69,632 |
| `<JID>@xmpp.zoom.us.contacts.encks.db` | 40,960 |
| `<JID>@xmpp.zoom.us.encks.db` | 36,864 |
| `<JID>@xmpp.zoom.us.msg.idx.encks.db` | 36,864 |
| `<JID>@xmpp.zoom.us.msg_ext.encks.db` | 20,480 |
| `<JID>@xmpp.zoom.us.sync.encks.db` | 0 |

- 크기가 0 이 아닌 파일은 모두 첫 16바이트가 SQLite 머리가 아니었습니다. 모두 암호화돼 있었습니다.
- 같은 폴더에 `client.config` 가 있었습니다.
- 같은 폴더에 이름이 64자 16진수 + `_small` 인 파일이 20개 있었습니다. 프로필 사진 축소본인지는 확인하지 못했습니다.

그 밖의 폴더입니다.

| 폴더 | 본 것 |
|---|---|
| `data\<ID>\calendar\` | 대소문자를 살린 같은 ID 이름의 폴더입니다. `auto-call.enc.db`, `calendar-file.enc.db`, `calendar-history-meeting.enc.db` 가 있었고 모두 암호화돼 있었습니다. |
| `data\users\<ID>\` | `data.db` 가 있었습니다. 이름과 달리 암호화돼 있었습니다. |
| `data\ConfAvatar\` | `conf_avatar_<32자 16진수>_<숫자>` 파일이 438개 있었습니다. 회의 참가자 사진 캐시인지는 확인하지 못했습니다. |
| `data\VirtualBkgnd_Default`, `VirtualBkgnd_Custom`, `VirtualBkgnd_Video` | 가상 배경 폴더입니다. 사용자가 올린 배경은 `VirtualBkgnd_Custom` 에 들어갈 것으로 보이나, 관찰 PC 에서는 비어 있어 확인하지 못했습니다. |
| `data\VideoFilter`, `PSWallpaper`, `WaitingRoom` 등 | 이름만 확인했습니다. |

> 그림 자리: `%APPDATA%\Zoom\data` 폴더 트리 — 평문 DB, 암호화 DB, 계정 폴더, 설정 파일을 색으로 나눠 표시

### 설정 파일

모두 평문 텍스트였습니다(확인 범위: 위와 같음).

| 파일 | 본 내용 | 쓸모 |
|---|---|---|
| `Zoom.us.ini` | `[ZoomChat]` 절의 `win_osencrypt_key`, 언어 설정 `com.zoom.client.langid=1033`, `[zSafeChecker]` 절의 `LastRunTime` | DB 키를 무엇으로 보호하는지 알 수 있습니다 |
| `client.config` | INI 형식입니다. 절 이름에 계정 JID 가 들어간 `[emoji.recent.<jid>]` 절과, 창 위치·마지막으로 연 채팅 화면이 든 `[zoom_new_im]` 절이 있었습니다 | 이 파일만으로도 로그인한 계정 JID 를 알 수 있습니다 |
| `viper.ini` | `[APE]` 절에 16진수로 적은 ASCII 문자열(제조사·모델)과 장치 번호가 있었습니다 | 카메라인지 오디오 장치인지는 확인하지 못했습니다 |
| `transcoding.ini` | `[All]` 절에 `SaveAllTempRecordFiles=0` 이 있었습니다 | — |

- `LastRunTime` 의 단위는 확인하지 못했습니다.

### DB 키 보호 — win_osencrypt_key

이 절의 값도 관찰 PC 에서 본 것입니다(확인 범위: 위와 같음).

- `Zoom.us.ini` `[ZoomChat]` 절의 `win_osencrypt_key` 값은 `ZWOSKEY` 로 시작했습니다.
- `ZWOSKEY` 뒤는 Base64 였습니다. 값 전체 길이는 359자였습니다.
- Base64 부분을 풀면 첫 20바이트가 `01 00 00 00 D0 8C 9D DF 01 15 D1 11 8C 7A 00 C0 4F C2 97 EB` 였습니다.
- 이 20바이트는 DPAPI 블롭 머리(버전 1 + 제공자 GUID)와 모양이 같습니다. 머리 구조는 [DPAPI 블롭 구조](../../01-foundations/protection/data-protection-api/dpapi-blob.md) 에서 다룹니다.
- 그래서 줌 로컬 DB 의 키 재료를 그 Windows 사용자의 데이터 보호 API (Data Protection API, DPAPI) 로 보호한다고 봅니다. 관찰한 값을 해석한 것입니다.
- 디스크 이미지만으로 이 값을 풀려면 그 사용자의 DPAPI 마스터키를 풀 재료(사용자 암호 등)가 필요할 것으로 봅니다. DPAPI 일반 원리에서 추론한 것이고, 줌 쪽 자료로는 확인하지 않았습니다.
- DPAPI 일반 원리는 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 에서 다룹니다.
- 이 값에서 DB 키를 만드는 방법과 암호 설정값은 확인하지 못했습니다. 이 페이지는 키를 꺼내 DB 를 여는 절차를 다루지 않습니다.

## 증거로서 의미

### 증명하는 것

- 그 사용자 프로필에 줌이 설치되고 실행된 적이 있습니다. 근거는 `%APPDATA%\Zoom` 폴더와 Uninstall `ZoomUMX` 키입니다(관찰).
- 계정 폴더 이름과 `client.config` 로 로그인한 계정의 식별자로 보이는 값(JID)을 알 수 있습니다(관찰).
- 로컬 녹화 파일이 있으면 녹화한 회의의 내용 자체가 남습니다[1][2].
- 업체 블로그에 따르면 회의 기록(호스트·회의 번호·주제·참가 시각·길이)과 채팅이 DB 에 남을 수 있습니다[2].
- 다만 관찰한 버전에서 평문으로 열리는 DB 는 세 개뿐이었습니다. 그 세 DB 에는 채팅·회의 기록으로 보이는 표가 없었습니다(관찰). 나머지 DB 는 키 없이 읽지 못합니다.

### 증명하지 못하는 것

- 회의에서 오간 말과 화면 내용: 이 페이지에서 확인한 흔적 가운데 이것을 담은 것은 로컬 녹화 파일뿐입니다.
- 클라우드 녹화 내용: PC 에 남는지 확인하지 못했습니다.
- 웹 브라우저로만 참가한 회의: 이 폴더에 남는지 확인하지 못했습니다. 브라우저 기록을 따로 봅니다([크롬 계열 브라우저](../browsers/chrome-edge-whale/index.md)).
- 평문 DB 행의 뜻: 칸 이름만 봤고 행 내용과 칸의 뜻은 검증하지 않았습니다.
- 회의 시각: DB 파일 수정 시각만으로는 말할 수 없습니다(아래 "시각 해석").

### 보고서 문장

- 쓸 수 있는 문장: "`C:\Users\<사용자>\AppData\Roaming\Zoom\data` 에 `<JID>@xmpp.zoom.us` 폴더가 있습니다. 같은 폴더의 `client.config` 에도 같은 JID 가 적혀 있습니다. 이 사용자 프로필에서 이 JID 로 줌에 로그인한 흔적이 있습니다."
- 피할 문장: "사용자는 이 날짜에 줌 회의를 했다." 폴더와 DB 수정 시각만으로는 회의를 했는지, 언제 했는지 말할 수 없습니다.

## 시각 해석

- 업체 블로그는 회의 참가 시각·메시지 보낸 시각 같은 칸이 있다고 적었습니다[2]. 시각 형식(단위·시간대)은 적지 않았습니다[2].
- 평문 DB 의 `start_time`·`end_time`·`metry_time`·`file_mtime_at_start` 형식은 확인하지 못했습니다.
- `Zoom.us.ini` `LastRunTime` 의 단위도 확인하지 못했습니다.
- 형식을 모르는 값은 자릿수로 초·밀리초·FILETIME 가운데 무엇인지 먼저 가려 봅니다. 형식별 읽는 법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- 가린 결과는 프리페치의 실행 시각 같은 다른 기록과 맞춰 검증합니다.

파일 시스템 시각은 파일마다 달랐습니다(관찰).

| 파일 | 수정 시각 (관찰) |
|---|---|
| `zoomus.enc.db`, `Zoom.us.ini` | 마지막 실행 즈음 |
| `telemetrydata.db`, `zoomus.zmdb.kvs.enc.db` | 조사 당일 (더 최근) |

- 그래서 DB 파일 수정 시각을 "회의한 시각" 으로 읽지 않습니다.
- 수정 시각은 "그 파일을 마지막으로 고친 시각" 까지만 말해 줍니다.

## 함정과 한계

- 이름에 `enc` 가 없어도 암호화된 DB 가 있습니다. `telemetrydata.db`, `local_dns_cache.db`, `users\<ID>\data.db` 가 그랬습니다(관찰). 파일 이름이 아니라 첫 16바이트로 판단합니다.
- 업체 블로그[2]의 표·칸 설명은 2021년 무렵 자료입니다. 이 블로그는 대상 버전을 밝히지 않았습니다. 요즘 버전과 다를 수 있습니다.
- 계정 폴더 이름은 소문자였고, `data\<ID>\calendar`·`data\users\<ID>` 는 대소문자를 살린 이름이었습니다(관찰). 두 폴더를 짝지을 때는 대소문자를 무시하고 비교합니다.
- 공개 수집 목록[1]은 Windows 7 이후 경로에서는 `%APPDATA%\Zoom\logs` 만 모읍니다. 줌 폴더를 통째로 모으는 항목은 Windows XP 경로뿐입니다. 그 밖에 녹화 폴더와 플러그인 json 을 모읍니다[1].
- 그래서 이 목록만 쓰면 Windows 7 이후 PC 에서는 `data` 폴더와 설정 파일이 빠집니다. `%APPDATA%\Zoom` 을 따로 통째로 확보합니다.
- 이 목록은 필요 없는 DLL·EXE 도 함께 모은다고 스스로 적었습니다[1].
- 원본 말고 사본에서 작업합니다. SQLite 파일은 `-journal` 까지 함께 복사한 사본을 엽니다.

### 지우기와 제거

- 줌을 제거한 뒤 `data` 폴더가 남는지는 확인하지 못했습니다.
- 폴더가 없어도 설치·실행 흔적은 [설치 프로그램](../system-account/uninstall.md), [프리페치](../execution/prefetch/index.md), [AmCache](../execution/amcache-hve/index.md) 에서 따로 찾습니다.
- 사용자가 채팅을 지우면 DB 에 무엇이 남는지는 확인하지 못했습니다.
- 파일 전체가 암호화돼 있으면 DB 의 빈 공간도 키 없이는 읽지 못합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 두 예시는 SQLite 명세와 DPAPI 블롭 머리 모양으로 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

**1. DB 가 평문인지 가리기**

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

1. `data\` 와 계정 폴더 아래 `.db` 파일마다 첫 16바이트를 봅니다.
2. 위와 같으면 평문 SQLite 입니다. 사본을 일반 SQLite 도구로 엽니다.
3. 첫 바이트부터 규칙 없는 값이면 파일 전체가 암호화된 것으로 봅니다. 파일 이름에 `enc` 가 있는지와 관계없이 이 결과를 따릅니다.

**2. win_osencrypt_key 가 DPAPI 블롭인지 가리기**

```
ZWOSKEYAQAAANCMnd8BFdERjHoAwE/C…
```

4. 값 앞의 7글자 `ZWOSKEY` 를 떼어 냅니다.
5. 나머지를 Base64 로 풉니다.
6. 풀어 낸 바이트의 앞 20바이트를 봅니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    01 00 00 00 D0 8C 9D DF 01 15 D1 11 8C 7A 00 C0
0x10    4F C2 97 EB
```

7. 0x00 의 4바이트 `01 00 00 00` 은 버전 1 입니다.
8. 0x04 부터 16바이트는 제공자 GUID (provider GUID) 입니다. GUID 를 읽는 법과 그 뒤 칸은 [DPAPI 블롭 구조](../../01-foundations/protection/data-protection-api/dpapi-blob.md) 를 봅니다.
9. 이 머리를 Base64 로 쓰면 앞 24글자가 늘 `AQAAANCMnd8BFdERjHoAwE/C` 입니다. 다른 앱의 설정 파일에서도 이 글자열로 DPAPI 블롭을 찾을 수 있습니다.

### 공개 도구로 한 번

- 평문 DB 세 개는 사본을 sqlite3 명령줄 도구 같은 공개 SQLite 도구로 엽니다.
- `.tables` 와 `.schema` 로 표와 칸이 위 표와 같은지 확인합니다. 버전이 다르면 표 구성이 다를 수 있습니다.
- 예를 들어 `process_metrics` 는 다음처럼 읽습니다.

```sql
SELECT process_name, metry_time, memory_usage, cpu_usage, is_in_meeting
FROM process_metrics
ORDER BY metry_time;
```

- `metry_time` 의 단위는 확인하지 못했습니다. 값을 그대로 적고, 해석은 따로 검증합니다.
- `client.config`, `Zoom.us.ini` 는 텍스트 편집기로 엽니다. `[emoji.recent.` 로 시작하는 절 이름에서 JID 를 읽습니다.
- 암호화된 DB 는 일반 SQLite 도구로 열리지 않습니다. 암호화된 증거를 다루는 일반 방법은 [암호화 증거 다루기](../../03-techniques/analysis/encrypted-evidence/index.md) 에서 다룹니다.
- 도구 결과는 몇 건이라도 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [설치 프로그램](../system-account/uninstall.md) | 사용자 하이브의 Uninstall `ZoomUMX` 키와 `InstallLocation` |
| [프리페치](../execution/prefetch/index.md) | `Zoom.exe` 를 실행한 시각 |
| [AmCache](../execution/amcache-hve/index.md) | `%APPDATA%\Zoom\bin\Zoom.exe` 가 기록됐는지 |
| [SRUM](../execution/system-resource-usage-monitor/index.md) | 줌이 쓴 네트워크 양과 그 시간대 |
| [카메라·마이크 사용 기록](../execution/capabilityaccessmanager.md) | 회의 중 카메라·마이크를 쓴 시각. 줌 항목이 여기 남는지는 확인하지 못했습니다 |
| [윈도 알림 기록](../execution/wpndatabase-db.md) | 채팅·회의 초대 알림. 줌 알림이 여기 남는지는 확인하지 못했습니다 |
| [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) | `win_osencrypt_key` 를 보호하는 방식 |
| [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) | 평문 DB 의 형식 |
| [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) | 평문 DB 시각 칸의 형식 |

여러 연락 기록을 합쳐 읽는 순서는 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 에서 다룹니다. `UploadInfos` 처럼 파일을 올린 흔적을 볼 때는 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 도 함께 봅니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 줌이 설치된 Windows 이미지를 고릅니다. 없으면 실험용 가상 머신에 줌을 설치해 씁니다.

1. 사용자마다 `%APPDATA%\Zoom\data` 가 있습니까? 사용자별 설치입니까, 다른 위치에 설치했습니까?
2. `data\` 와 계정 폴더 아래 `.db` 파일의 첫 16바이트를 모두 확인합니다. 평문과 암호화 파일은 각각 몇 개입니까? 이름에 `enc` 가 없는데 암호화된 파일이 있습니까?
3. 계정 폴더 `<JID>@xmpp.zoom.us` 는 몇 개입니까? `client.config` 절 이름의 JID 와 같습니까?
4. `win_osencrypt_key` 값을 Base64 로 풀어 앞 20바이트가 DPAPI 블롭 머리인지 확인합니다.
5. `문서\Zoom` 에 녹화 폴더가 있습니까? 있다면 녹화 파일의 파일 시스템 시각을 프리페치의 `Zoom.exe` 실행 시각과 맞춰 봅니다.
6. 가상 머신에서 회의를 한 번 열고 닫습니다. 그 앞뒤로 `data` 폴더를 떠서 수정 시각이 바뀐 파일을 비교합니다. 결과에는 Windows 버전과 줌 버전을 함께 적습니다.

## 참고 문헌

1. Ryan McVicar, KapeFiles 수집 목록 "Zoom.tkape" (v1.0) — https://raw.githubusercontent.com/EricZimmerman/KapeFiles/master/Targets/Apps/Zoom.tkape
2. Forensafe, "Zoom" (2021-06-25) — https://www.forensafe.com/blogs/zoom.html
