---
title: "KDE 흔적"
parent: "아티팩트 · 데스크톱 환경"
nav_order: 850
---

# KDE 흔적 (KDE Plasma)

KDE Plasma 데스크톱은 활동 관리자 데이터베이스, 최근 문서 목록, 클립보드 기록, 파일 색인, 로그인 화면 상태 파일에 사용자가 무엇을 열고 복사했는지와 누가 마지막으로 로그인했는지를 남깁니다.

## 무엇을 기록하나 · 왜 생기나

KDE 의 활동 관리자 (kactivitymanagerd) 는 앱이 파일을 열고 닫을 때 보내는 알림을 받아 "어느 활동에서 어느 앱이 어느 파일을 썼는지" 를 SQLite 데이터베이스에 쌓습니다[1][3]. 이 기록으로 파일마다 점수를 계산해 따로 저장하고[1][4], 기본 설정이 모든 앱을 기록하는 것이라 사용자가 따로 켜지 않아도 기록이 쌓입니다[3].

KIO 라이브러리의 최근 문서 기능 (KRecentDocument) 은 KDE 앱이 연 파일을 `recently-used.xbel` 에 적고[5], Klipper 는 클립보드에 들어간 내용을 다음 로그인 때도 볼 수 있도록 파일에 저장합니다[6][7]. Baloo 는 홈 폴더의 파일을 검색용으로 색인하고 설정에 따라 파일 내용까지 색인하며[9][13], 로그인 화면 SDDM 은 다음 로그인 때 미리 골라 둘 사용자와 세션을 상태 파일에 적습니다[14].

KWallet 비밀번호 보관함은 [비밀번호 보관함](keyring.md), GNOME 쪽 대응 흔적은 [GNOME 흔적](gnome.md) 에서 다룹니다.

## 위치와 버전별 차이

아래 경로는 모두 사용자 홈 기준이고, 경로 앞부분 `~/.local/share` 는 Qt 의 사용자 데이터 위치 (GenericDataLocation) 입니다.

| 흔적 | 경로 | 비고 |
|---|---|---|
| 활동 관리자 DB | `~/.local/share/kactivitymanagerd/resources/database` | 확장자 없는 파일 이름 `database`, 옆에 `database-wal`·`database-shm`[1][2] |
| 활동 관리자 설정 | `kactivitymanagerd-pluginsrc` (사용자 설정 폴더) | 기록 범위·보존 기간[3] |
| 최근 문서 | `~/.local/share/recently-used.xbel` | GTK 앱과 같은 파일, 잠금 파일 `recently-used.xbel.lock`[5] |
| 옛 최근 문서 | `~/.local/share/RecentDocuments/` | UAC 가 모으는 위치[16] |
| 클립보드 기록 (현재판) | `~/.local/share/klipper/history3.sqlite`, 부가 데이터 `~/.local/share/klipper/data/` | 환경 변수 `KLIPPER_DATABASE` 로 바뀜[6] |
| 클립보드 기록 (Plasma 5.27.11) | `~/.local/share/klipper/history2.lst` | [8] |
| 클립보드 설정 | `klipperrc` | [7] |
| 파일 색인 | `~/.local/share/baloo/index` | 환경 변수 `BALOO_DB_PATH` 로 바뀜[10][11] |
| 색인 설정 | `baloofilerc` | [13] |
| 로그인 화면 상태 | `sddm` 계정 홈 아래 `state.conf` | 계정이 없으면 빌드할 때 정한 폴더[14] |

배포판마다 기본 데스크톱과 기본 설정으로 설치한 시험 조건에서 Ubuntu 24.04 와 Rocky 9.5(RHEL 9 재빌드판)는 GNOME 이었고, KDE 는 Kubuntu 24.04 에서 Wayland/XWayland 로 돌았습니다[21]. 그래서 Ubuntu 계열에서는 Kubuntu 설치본이나 KDE 를 따로 깐 시스템에서 이 쪽의 흔적이 나옵니다.

| 항목 | Ubuntu 24.04 계열 | RHEL 9 계열 |
|---|---|---|
| 기본 데스크톱 | Ubuntu 는 GNOME, Kubuntu 24.04 는 KDE[21] | GNOME (Rocky 9.5 시험 조건)[21] |
| Klipper 파일 | 검체의 Plasma 판에 따라 `history2.lst` 또는 `history3.sqlite`[6][8] | 같음 |

Klipper 파일 이름은 Plasma 판에 따라 다르므로, 검체의 `klipper` 폴더에 어느 파일이 있는지부터 봅니다.

앱별로는 UAC 가 다음 파일을 모읍니다. Konqueror 를 뺀 나머지는 Flatpak(`~/.var/app`)·Snap(`~/snap`) 판 경로도 따로 모읍니다[18].

| 앱 | 파일 | 담긴 것 |
|---|---|---|
| Dolphin 파일 관리자 | `~/.config` 아래 `dolphin_dolphin_dolphin` | 열린 폴더와 마지막 위치[18] |
| Okular 문서 보기 | `~/.local/share` 아래 `*/okular/docdata/*`, `~/.config/okularrc` | 연 문서의 메타데이터[18] |
| Gwenview 이미지 보기 | `~/.config/gwenviewrc` | 최근 본 이미지 경로[18] |
| Ark 압축 관리자 | `~/.local/share` 아래 `ark_recentfiles` | 최근 연 압축 파일[18] |
| Kate·KWrite 편집기 | `~/.local/share` 아래 `anonymous.katesession` | 최근 연 파일[18] |
| Konqueror 브라우저 | `~/.local/share/konqueror` (`konq_history*`, `bookmarks.xml`, `cookies*` 등), 옛 경로 `~/.kde/share/apps/konqueror`, `~/.kde/share/apps/kcookiejar` | 방문 기록·북마크·쿠키[19] |

KDE 는 XDG 표준에 없는 자동 실행 폴더 `~/.config/autostart-scripts` 도 씁니다[20]. 자동 실행 흔적은 [XDG 자동 실행](../persistence/xdg-autostart.md) 에서 다룹니다.

## 구조

### 활동 관리자 DB

SQLite 파일이고, 쓰기 앞 기록 (WAL) 모드로 열며 WAL 이 100쪽을 넘으면 본 파일로 옮겨 씁니다[2]. 스키마 판은 `SchemaInfo` 테이블의 `version` 키에 `2015.02.09` 로 들어갑니다[1]. 열 이름 `targettedResource` 는 원래 철자가 이렇습니다.

| 테이블 | 열 | 뜻 |
|---|---|---|
| `SchemaInfo` | `key`, `value` | 스키마 판[1] |
| `ResourceEvent` | `usedActivity`, `initiatingAgent`, `targettedResource`, `start`, `end` | 파일 열기·닫기 한 쌍[1] |
| `ResourceScoreCache` | `usedActivity`, `initiatingAgent`, `targettedResource`, `scoreType`, `cachedScore`, `firstUpdate`, `lastUpdate` | 이벤트로 계산한 파일별 점수[1][4] |
| `ResourceLink` | `usedActivity`, `initiatingAgent`, `targettedResource` | 활동에 연결된 파일[1] |
| `ResourceInfo` | `targettedResource`, `title`, `mimetype`, `autoTitle`, `autoMimetype` | 파일 제목과 MIME 형식[1] |

`usedActivity` 는 그때의 활동, `initiatingAgent` 는 알림을 보낸 앱, `targettedResource` 는 파일입니다[3]. 앱이 `file://` 주소로 알리면 로컬 경로로 바꾸고, `/` 로 시작하는 경로는 실제 경로 (canonical path) 로 풀어 적습니다[3]. 앱이 "열었다" 고 알리면 `end` 를 비운 줄을 넣고, "닫았다" 고 알리면 같은 활동·앱·파일의 `end` 가 빈 줄에 닫은 시각을 채웁니다[3]. "접근했다" 는 알림 한 번이면 `start` 와 `end` 에 같은 시각이 들어갑니다[3]. 창 포커스가 바뀌는 일은 파일 크기와 디스크 쓰기를 줄이려고 저장하지 않습니다[1].

`ResourceInfo` 의 제목과 MIME 형식을 활동 관리자가 스스로 채우는 것은 로컬 파일이 그 순간 있을 때뿐이고, 이때 `autoTitle`·`autoMimetype` 이 `1` 입니다[1][3]. 앱이 제목이나 MIME 형식을 따로 알려 오면 그 값으로 바꿔 적습니다[1][3].

기록 범위는 `kactivitymanagerd-pluginsrc` 의 `[Plugin-org.kde.ActivityManager.Resources.Scoring]` 그룹이 정합니다[3].

| 키 | 기본값 | 뜻 |
|---|---|---|
| `what-to-remember` | 모든 앱 | 모든 앱·고른 앱·기록 안 함 중 하나[3] |
| `blocked-by-default` | `false` | 고른 앱 모드에서 목록이 허용 목록인지 차단 목록인지[3] |
| `allowed-applications`, `blocked-applications` | 없음 | 앱 목록[3] |
| `url-filters` | `about:*`, `*/.*`, `/`, `/tmp/*` | 이 무늬에 맞는 주소는 기록하지 않음[3] |
| `off-the-record-activities` | 없음 | 기록하지 않는 활동[3] |
| `keep-history-for` | `4` | 이 개월 수보다 오래된 기록을 지움, `0` 이면 지우지 않음[3] |

### 최근 문서

형식은 GTK 와 같은 `recently-used.xbel` 이라 [최근 연 파일](../execution/recently-used.md) 에서 다룹니다. KDE 쪽 동작은 파일을 적는 앱이 기본 설정에서 읽는 `[RecentDocuments]` 그룹이 정합니다[5].

| 키 | 기본값 | 뜻 |
|---|---|---|
| `UseRecent` | `true` | `false` 면 다음 기록 때 xbel 파일을 통째로 지움[5] |
| `MaxEntries` | `300` | 남길 항목 수, `0` 이면 파일을 지움[5] |
| `IgnoreHidden` | `true` | 경로에 `/.` 가 든 숨김 파일은 적지 않음[5] |

임시 폴더 아래 파일도 적지 않습니다[5].

### 클립보드 기록 (Klipper)

현재판 `history3.sqlite` 도 WAL 모드로 엽니다[6]. 테이블은 셋이고 `version` 테이블의 `db_version` 은 `3` 입니다[6].

| 테이블 | 열 | 뜻 |
|---|---|---|
| `main` | `uuid`, `added_time`, `last_used_time`, `mimetypes`, `text`, `starred` | 항목마다 한 줄, 텍스트는 `text` 에 평문으로 들어감[6] |
| `aux` | `uuid`, `mimetype`, `data_uuid` | 텍스트가 아닌 데이터의 색인[6] |
| `version` | `db_version` | 형식 판[6] |

이미지 같은 부가 데이터는 `data/` 아래 항목 `uuid` 이름 폴더에 `data_uuid` 이름 파일로 들어갑니다[6]. 설정 파일 `klipperrc` 의 `[General]` 그룹에서 `KeepClipboardContents`(기본 `true`, 다음 로그인 때까지 기록 유지), `MaxClipItems`(기본 20), `SaveImages`(기본 `false`), `SaveSelection`(기본 `false`, 마우스로 고르기만 한 글자도 저장) 을 봅니다[7]. `KeepClipboardContents` 가 `false` 면 Klipper 가 끝날 때 DB 파일과 `data/` 폴더를 지우고, 다시 열 때도 `main`·`aux` 를 비웁니다[6].

### 파일 색인 (Baloo)

`index` 는 하위 폴더 없이 파일 하나로 여는 LMDB 데이터베이스이고, 64비트에서 최대 크기 한도를 256GB 로 잡습니다[10]. 안에는 `docterms`, `docfilenameterms`, `docxatrrterms`(원래 철자), `indexingleveldb`, `failediddb` 같은 이름 붙은 데이터베이스와 경로 트리·파일 이름·문서 시각·mtime 데이터베이스가 있습니다[10]. 문서 시각 값은 파일 내용 수정 시각 (mTime) 과 메타데이터 변경 시각 (cTime) 을 32비트 정수 두 개로 담습니다[12].

`baloofilerc` 의 설정은 다음과 같습니다[13].

| 그룹 | 키 | 기본값 |
|---|---|---|
| `Basic Settings` | `Indexing-Enabled` | `true` |
| `General` | `index hidden folders` | `false` |
| `General` | `only basic indexing` | `false` |
| `General` | `folders` | 홈 폴더 |
| `General` | `exclude folders` | 빈 목록 |
| `General` | `exclude filters`, `exclude mimetypes` | Baloo 에 들어 있는 기본 제외 목록 |

Baloo 가 지원하는 파일 시스템은 ext3/4, Btrfs, XFS 입니다[9].

### 로그인 화면 상태 (SDDM)

`state.conf` 는 INI 꼴이고 `[Last]` 그룹의 `User=` 에 마지막으로 로그인한 사용자, `Session=` 에 그 사용자의 세션 이름이 들어갑니다[14]. 다음 로그인 화면에서 이 둘을 미리 골라 둡니다[14]. 주 설정의 `[Users]` 그룹 `RememberLastUser`·`RememberLastSession`(기본 `true`) 이 이 기록을 켜고, `[Autologin]` 그룹의 `User=`, `Session=`, `Relogin=`(기본 `false`) 은 자동 로그인을 정합니다[14]. 주 설정 파일 경로는 빌드할 때 정해지므로 검체의 SDDM 패키지 파일 목록에서 찾습니다. 세션 로그 기본값은 X11 에서 `.local/share/sddm/xorg-session.log`, Wayland 에서 `.local/share/sddm/wayland-session.log` 입니다[14].

## 증거로서 의미

### 증명하는 것

- `ResourceEvent` 한 줄은 이 계정의 KDE 세션에서 `initiatingAgent` 앱이 `targettedResource` 파일을 `start` 에 열었고, `end` 가 차 있으면 그 시각에 닫았다는 활동 관리자 기록입니다[3].
- 로컬 경로가 적힌 줄은 그 시각에 그 경로에 파일이 있었다는 뜻입니다. 없는 파일은 경로가 비워져 기록되지 않습니다[3].
- Klipper `main` 의 `text` 는 클립보드에 들어간 글자 그대로이고, `last_used_time` 은 그 항목이 마지막으로 맨 위에 올라온 시각입니다[6].
- Baloo 색인에 파일 이름이나 단어가 있으면, 색인할 때 그 경로에 그 파일이 있었다는 뜻입니다.
- `state.conf` 의 `User=` 는 이 기기에서 SDDM 으로 마지막에 로그인한 계정 이름입니다[14].

### 증명하지 못하는 것

- `ResourceEvent` 는 파일 내용, 복사, 전송을 말하지 않습니다. 앱이 알림을 보내지 않으면 기록이 없고, 숨김 경로·`/tmp`·제외 앱·기록 안 하는 활동도 빠지며, 기본 4개월이 지나면 지워지므로 줄이 없다고 "열지 않았다" 고 할 수 없습니다[3].
- Klipper 기록은 복사한 글자를 어디에 붙여넣었는지 말하지 않습니다.
- Baloo 는 스스로 색인하므로 색인에 있다는 사실만으로 사용자가 파일을 열었다고 할 수 없습니다.
- `state.conf` 에는 로그인 시각이 없습니다. 시각은 [로그인 기록](../logins/wtmp-btmp-lastlog.md) 과 [인증 로그](../logins/auth-log.md) 에서 찾습니다.

## 시각 해석

| 값 | 단위 | 바뀌는 때 |
|---|---|---|
| `ResourceEvent.start` | Unix 초 (UTC) | 앱이 파일을 열었다고 알릴 때[3] |
| `ResourceEvent.end` | Unix 초 (UTC), 닫기 전에는 빈 값 | 앱이 파일을 닫았다고 알릴 때[3] |
| `ResourceScoreCache.firstUpdate`, `lastUpdate` | Unix 초 (UTC) | 점수를 처음 매길 때, 다시 계산할 때[4] |
| Klipper `last_used_time` | 소수점 있는 Unix 초 (UTC) | 항목이 다시 맨 위로 올라올 때[6] |
| Baloo `mTime`, `cTime` | 32비트 Unix 초 (UTC) | 파일 자체의 수정·메타데이터 변경 시각을 옮겨 적은 값[12] |
| `state.conf` 파일 수정 시각 | 파일 시스템 시각 | SDDM 이 파일을 다시 쓸 때 |

Klipper `added_time` 도 같은 단위일 가능성이 있지만, 검체에서 `last_used_time` 과 나란히 놓고 값의 크기를 먼저 봅니다. Baloo 의 시각은 색인한 때가 아니라 파일의 시각입니다. 활동 관리자는 설정을 읽을 때와 12시간마다 `keep-history-for` 개월보다 오래된 줄을 지우므로, 남은 가장 오래된 `start` 는 사용 시작 시점이 아니라 보존 기간의 끝일 가능성이 있습니다[3]. Unix 초를 읽는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

- 활동 관리자 DB 와 Klipper DB 는 WAL 모드라서 `database` 나 `history3.sqlite` 만 복사하면 최근 기록을 놓칩니다. `-wal`·`-shm` 파일을 함께 모읍니다[2][6].
- 사용자가 "최근 기록 지우기" 를 하면 `ResourceInfo`·`ResourceEvent`·`ResourceScoreCache` 에서 해당 줄을 DELETE 합니다[3]. 지운 줄은 SQLite 빈 페이지나 WAL 에 남을 수 있으므로 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html) 의 복구 방법을 씁니다.
- Klipper 기록을 비우면 `main`·`aux` 를 지우고 `data/` 아래 항목 폴더도 지웁니다. 별표 (`starred`) 가 붙은 항목만 남기는 비우기도 있습니다[6].
- `UseRecent=false` 나 `MaxEntries=0` 이면 KDE 앱이 `recently-used.xbel` 을 통째로 지우므로 GTK 앱 기록까지 함께 사라집니다[5].
- UAC 의 `kde_mru` 는 옛 `RecentDocuments` 폴더만 모읍니다[16]. 현재 KIO 는 `recently-used.xbel` 에 쓰므로 `linux_mru` 처럼 xbel 을 모으는 항목을 같이 돌립니다[5][17].
- `KLIPPER_DATABASE`, `BALOO_DB_PATH` 환경 변수를 쓰면 기본 위치가 비어 있을 수 있습니다[6][11]. 사용자의 셸 설정·자동 실행 파일에서 이 변수를 찾아봅니다.
- 활동 관리자 기록은 앱이 알림을 보내야 생기므로[3], 알림을 보내지 않는 앱으로 연 파일은 기록이 없을 가능성이 있습니다.

## 직접 분석해 보기

### 헥스로 한 번: SDDM state.conf

아래는 SDDM 설정 정의에 맞춰 만든 예시이고, 사용자 이름과 세션 이름은 지어낸 값입니다.

```
00000000: 5b4c 6173 745d 0a53 6573 7369 6f6e 3d70  [Last].Session=p
00000010: 6c61 736d 612e 6465 736b 746f 700a 5573  lasma.desktop.Us
00000020: 6572 3d61 6c69 6365 0a                   er=alice.
```

1. 0x00 의 `5b ... 5d` 가 그룹 이름 `[Last]` 이고 0x06 의 `0a` 로 줄이 끝납니다[14].
2. 0x07 의 `Session=` 뒤 0x0F 부터 0x1D 의 `0a` 앞까지가 마지막 세션 이름입니다. 값이 세션 파일 이름인지 다른 꼴인지는 검체에서 봅니다.
3. 0x1E 의 `User=` 뒤 0x23 부터가 마지막 로그인 사용자 `alice` 입니다[14].

### 공개 도구로 한 번

전용 파서 대신 SQLite 도구로 사본을 직접 읽습니다. WAL 파일을 같은 폴더에 둔 채 사본을 엽니다.

```
sqlite3 database "SELECT datetime(start,'unixepoch'), datetime(end,'unixepoch'), initiatingAgent, targettedResource, usedActivity FROM ResourceEvent ORDER BY start;"
sqlite3 database "SELECT targettedResource, title, mimetype FROM ResourceInfo;"
sqlite3 database "SELECT initiatingAgent, targettedResource, datetime(firstUpdate,'unixepoch'), datetime(lastUpdate,'unixepoch'), cachedScore FROM ResourceScoreCache ORDER BY lastUpdate;"
sqlite3 history3.sqlite "SELECT uuid, datetime(added_time,'unixepoch'), datetime(last_used_time,'unixepoch'), mimetypes, starred, text FROM main;"
```

`ResourceEvent` 와 `ResourceScoreCache` 를 같이 보면, 이벤트가 지워졌어도 점수 줄이 남은 파일을 찾을 수 있습니다. 둘은 지우는 기준 열이 달라서 (`start` 와 `lastUpdate`) 남는 기간이 다릅니다[3]. Baloo `index` 는 LMDB 형식이므로 LMDB 를 읽는 도구로 이름 붙은 데이터베이스를 뽑습니다[10]. 수집은 UAC 의 `kactivitymanagerd`, `kde_mru`, `linux_mru`, 앱별 항목으로 할 수 있습니다[15][16][17][18][19].

## 교차 검증

| 함께 볼 것 | 맞춰 볼 점 |
|---|---|
| [최근 연 파일](../execution/recently-used.md) | `ResourceEvent` 의 파일과 앱이 xbel 항목에도 있는지 |
| [썸네일 캐시](../file-activity/thumbnails.md) | Dolphin·Gwenview 로 본 이미지의 미리보기가 남았는지 |
| [휴지통](../file-activity/trash.md) | 연 파일이 뒤에 휴지통으로 갔는지 |
| [로그인 기록](../logins/wtmp-btmp-lastlog.md), [인증 로그](../logins/auth-log.md) | `state.conf` 의 사용자가 로그인한 시각 |
| [비밀번호 보관함](keyring.md) | KWallet 이 열린 흔적과 로그인 시각 |
| [Linux 의 브라우저 프로필](browsers.md) | Klipper 에 복사된 주소와 브라우저 방문 기록 |
| [타임라인 만들기](../../03-techniques/analysis/timeline.md) | 위 시각을 한 줄로 합치기 |

## 실습

KDE 데스크톱이 깔린 공개 Linux 검체(NIST CFReDS 등)를 찾아 다음 질문을 풀어 봅니다.

1. `database` 와 `database-wal` 을 함께 열 때와 `database` 만 열 때 `ResourceEvent` 줄 수가 다른가?
2. `end` 가 빈 줄이 있다면, 그 파일을 연 앱이 수집 시점에 아직 떠 있었는지 다른 흔적으로 맞춰 볼 수 있는가?
3. `ResourceScoreCache` 에만 있고 `ResourceEvent` 에는 없는 파일이 있는가? 그 파일의 `lastUpdate` 는 언제인가?
4. `klipper` 폴더에 있는 것이 `history2.lst` 인가 `history3.sqlite` 인가? `main.text` 에 경로나 주소가 있다면 그 파일·주소가 다른 흔적에도 나오는가?
5. `state.conf` 의 `User=` 와 wtmp 의 마지막 그래픽 로그인 사용자가 같은가?

## 참고 문헌

1. KDE kactivitymanagerd, src/common/database/schema/ResourcesDatabaseSchema.cpp. https://github.com/KDE/kactivitymanagerd/blob/master/src/common/database/schema/ResourcesDatabaseSchema.cpp
2. KDE kactivitymanagerd, src/common/database/Database.cpp. https://github.com/KDE/kactivitymanagerd/blob/master/src/common/database/Database.cpp
3. KDE kactivitymanagerd, src/service/plugins/sqlite/StatsPlugin.cpp. https://github.com/KDE/kactivitymanagerd/blob/master/src/service/plugins/sqlite/StatsPlugin.cpp
4. KDE kactivitymanagerd, src/service/plugins/sqlite/ResourceScoreCache.cpp. https://github.com/KDE/kactivitymanagerd/blob/master/src/service/plugins/sqlite/ResourceScoreCache.cpp
5. KDE KIO, src/core/krecentdocument.cpp. https://github.com/KDE/kio/blob/master/src/core/krecentdocument.cpp
6. KDE plasma-workspace, klipper/historymodel.cpp. https://github.com/KDE/plasma-workspace/blob/master/klipper/historymodel.cpp
7. KDE plasma-workspace, klipper/klipper.kcfg. https://github.com/KDE/plasma-workspace/blob/master/klipper/klipper.kcfg
8. KDE plasma-workspace v5.27.11, klipper/klipper.cpp. https://github.com/KDE/plasma-workspace/blob/v5.27.11/klipper/klipper.cpp
9. KDE Baloo, README.md. https://github.com/KDE/baloo/blob/master/README.md
10. KDE Baloo, src/engine/database.cpp. https://github.com/KDE/baloo/blob/master/src/engine/database.cpp
11. KDE Baloo, src/engine/global.cpp. https://github.com/KDE/baloo/blob/master/src/engine/global.cpp
12. KDE Baloo, src/engine/documenttimedb.h. https://github.com/KDE/baloo/blob/master/src/engine/documenttimedb.h
13. KDE Baloo, src/lib/baloosettings.kcfg. https://github.com/KDE/baloo/blob/master/src/lib/baloosettings.kcfg
14. SDDM, src/common/Configuration.h. https://github.com/sddm/sddm/blob/develop/src/common/Configuration.h
15. UAC, artifacts/files/system/kactivitymanagerd.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/system/kactivitymanagerd.yaml
16. UAC, artifacts/files/applications/kde_mru.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/applications/kde_mru.yaml
17. UAC, artifacts/files/system/linux_mru.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/system/linux_mru.yaml
18. UAC, artifacts/files/applications/dolphin.yaml·okular.yaml·gwenview.yaml·ark.yaml·katesession.yaml. https://github.com/tclahr/uac/tree/main/artifacts/files/applications
19. UAC, artifacts/files/browsers/konqueror.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/browsers/konqueror.yaml
20. UAC, artifacts/files/system/xdg_autostart.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/system/xdg_autostart.yaml
21. Lukas Schmidt, Sebastian Strasda, Sebastian Schinzel, "Uncovering linux desktop espionage", Forensic Science International: Digital Investigation 53 (2025) 301921. https://doi.org/10.1016/j.fsidi.2025.301921
