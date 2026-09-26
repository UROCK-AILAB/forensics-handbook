---
title: "Linux 의 브라우저 프로필"
parent: "아티팩트 · 데스크톱 환경"
nav_order: 870
---

# Linux 의 브라우저 프로필 (Firefox·Chrome)

Linux 의 Chrome·Chromium·Firefox 는 Windows 와 같은 SQLite 데이터베이스를 쓰지만, 프로필 폴더가 설치 방식(배포판 패키지·Snap·Flatpak)과 환경 변수에 따라 여러 곳으로 갈라지고, Chrome 계열의 저장 비밀번호는 데스크톱 비밀번호 보관함에 기댑니다. 이 쪽은 Linux 에서 달라지는 경로·암호화·시각만 다룹니다. 테이블과 필드의 뜻은 다른 판의 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html)·[파이어폭스](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/firefox/index.html) 쪽을 봅니다.

## 무엇을 기록하나 · 왜 생기나

브라우저는 사용자 데이터 폴더 (user data directory) 아래 프로필마다 방문 기록·쿠키·다운로드·저장 비밀번호·확장 기능을 파일로 남깁니다. Chrome 계열은 `History`, `Cookies`, `Login Data`, `Web Data`, `Bookmarks`, `Preferences`, `Secure Preferences`, `Shortcuts`, `Top Sites`, `Visited Links`, `DownloadMetadata`, `Network Persistent State` 같은 파일과 `Extensions`, `Local Storage`, `IndexedDB`, `Sessions`, `File System` 폴더를 둡니다[12][13]. `Cookies` 와 `Login Data` 는 프로필 바로 아래나 `Network/` 폴더 아래에 있을 수 있어서, 수집 정의는 두 위치를 다 적습니다[12].

Firefox 는 프로필 폴더에 `places.sqlite`(방문 기록·북마크·다운로드), `cookies.sqlite`, `formhistory.sqlite`, `logins.json`·`key4.db`(저장 비밀번호), `extensions.json`, `permissions.sqlite`, `favicons.sqlite`, `prefs.js`, `sessionstore` 계열 파일, `bookmarkbackups` 폴더를 둡니다[15]. 다운로드는 `places.sqlite` 의 `moz_annos` 에 `downloads/destinationFileURI`·`downloads/metaData` 주석으로 남고[8], 옛 판이 쓰던 `downloads.sqlite` 도 수집 정의에 들어 있습니다[12][15].

이 기록은 모두 브라우저가 쓰는 동안 계속 바뀌는 데이터베이스라서, 운영체제와 상관없이 같은 원리로 생깁니다. Linux 에서 따로 알아야 할 것은 "어디에 있나" 와 "비밀번호를 무엇으로 잠갔나" 두 가지입니다.

## 위치와 버전별 차이

### Chrome·Chromium

기본 사용자 데이터 폴더는 `~/.config` 아래이고, 채널마다 폴더 이름이 다릅니다[1].

| 제품 | 사용자 데이터 폴더 |
|---|---|
| Chrome Stable | `~/.config/google-chrome` |
| Chrome Beta | `~/.config/google-chrome-beta` |
| Chrome Dev | `~/.config/google-chrome-unstable` |
| Chrome Canary | `~/.config/google-chrome-canary` |
| Chrome for Testing | `~/.config/google-chrome-for-testing` |
| Chromium | `~/.config/chromium` |

`~/.config` 부분은 `$CHROME_CONFIG_HOME`(M61 부터) 이나 `$XDG_CONFIG_HOME` 으로 바꿀 수 있습니다[1]. 프로필 폴더 이름은 `Default` 와 `Profile 1` 같은 `Profile*` 입니다[6].

캐시는 설정 폴더와 따로 둡니다. `$XDG_CACHE_HOME`(기본 `~/.cache`) 아래에 설정 폴더 기준 상대 경로를 이어 붙이므로 `~/.config/google-chrome/Default` 의 캐시는 `~/.cache/google-chrome/Default` 에 생깁니다[1]. 이 계산에서는 `$CHROME_CONFIG_HOME` 을 보지 않고, 프로필 폴더가 설정 폴더 아래에 있지 않으면 캐시는 프로필 폴더 안에 생깁니다[1].

원격 데스크톱 기능을 쓰면 `~/.config/chrome-remote-desktop/chrome-profile/` 과 `~/.config/chrome-remote-desktop/chrome-config/google-chrome/` 아래에도 프로필이 생깁니다[12].

### Firefox

Firefox 는 옛 위치 `~/.mozilla/firefox` 와 XDG 위치 `~/.config/mozilla/firefox` 중 하나를 씁니다. 코드는 옛 `~/.mozilla` 폴더가 이미 있거나 환경 변수 `MOZ_LEGACY_HOME` 이 `1` 이면 옛 위치를 쓰고, 아니면 `$XDG_CONFIG_HOME`(기본 `~/.config`) 아래를 씁니다[5]. dissect.target 은 146 이하가 옛 위치, 147 이상이 XDG 위치를 기본으로 쓴다고 적습니다[8]. 캐시는 `$XDG_CACHE_HOME`(기본 `~/.cache`) 아래 `mozilla/firefox/프로필 이름/cache2/` 에 생깁니다[5][12]. 네이티브 메시징 매니페스트만은 호환을 위해 계속 `~/.mozilla` 아래에 둡니다[5].

### 설치 방식별 경로

같은 배포판이라도 설치 방식에 따라 경로가 갈라집니다. 설치 방식은 [snap·flatpak](../packages/snap-flatpak.md)·[dpkg·apt 기록](../packages/dpkg-apt.md)·[rpm·dnf·yum 기록](../packages/rpm-dnf.md) 에서 먼저 확인합니다.

| 브라우저·방식 | 프로필 위치 | 캐시 위치 |
|---|---|---|
| Chrome (deb·rpm) | `~/.config/google-chrome/` | `~/.cache/google-chrome/`[1] |
| Chrome (Flatpak) | `~/.var/app/com.google.Chrome/config/google-chrome/`[6] | `~/.var/app/com.google.Chrome/cache/google-chrome`[16] |
| Chromium (배포판 패키지) | `~/.config/chromium/`[7][12] | `~/.cache/chromium/`[12] |
| Chromium (Snap) | `~/snap/chromium/common/chromium/`[7][12] | `~/snap/chromium/common/chromium/Default/Cache`[16] |
| Chromium (Flatpak) | `~/.var/app/org.chromium.Chromium/config/chromium/`[7] | `~/.var/app/org.chromium.Chromium/cache/chromium`[16] |
| Firefox (배포판 패키지) | `~/.mozilla/firefox/` 또는 `~/.config/mozilla/firefox/`[8] | `~/.cache/mozilla/firefox/`[16] |
| Firefox (Snap) | `~/snap/firefox/common/.mozilla/firefox/` 또는 `~/snap/firefox/common/.config/mozilla/firefox/`[8] | `~/snap/firefox/common/.cache/mozilla/firefox/`[16] |
| Firefox (Flatpak) | `~/.var/app/org.mozilla.firefox/.mozilla/firefox/` 또는 `~/.var/app/org.mozilla.firefox/.config/mozilla/firefox/`[8] | `~/.var/app/org.mozilla.firefox/cache/mozilla/firefox`[16] |

Ubuntu 24.04 와 RHEL 9 의 차이는 경로 규칙이 아니라 어떤 방식으로 설치했느냐에서 나옵니다. 두 배포판 모두 패키지 기록으로 설치 방식을 먼저 확인하고, Flatpak 경로(`~/.var/app/`)까지 함께 봅니다.

## 구조

데이터베이스 파일 형식은 다른 판의 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html) 쪽, `Local Storage`·`IndexedDB` 는 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html) 쪽과 같습니다. Linux 에서 달라지는 부분은 암호화된 값의 앞머리입니다.

### Chrome 계열의 암호화 값 앞머리

`Login Data` 의 `logins.password_value` 와 `Cookies` 의 `encrypted_value` 는 앞 3바이트에 어떤 키로 잠갔는지 알리는 태그가 붙습니다[7]. Linux 에서 비밀번호 보관함에서 받은 비밀로 키를 만들면 `v11`, 보관함을 쓰지 않는 `basic` 방식이면 `v10` 입니다[2][3].

| 앞 3바이트 | 헥스 | 뜻 |
|---|---|---|
| `v10` | `76 31 30` | `basic` 방식, 브라우저 안에 박힌 고정 키로 잠금[3] |
| `v11` | `76 31 31` | GNOME Keyring(libsecret) 또는 KWallet 에 둔 비밀로 만든 키로 잠금[2] |

어느 보관함을 쓸지는 명령줄 `--password-store=` 값(`basic`, `gnome-libsecret`, `kwallet`, `kwallet5`, `kwallet6`)으로 정하고, 값이 없으면 데스크톱 환경을 보고 고릅니다[2][4]. KDE 에서는 KWallet, GNOME·Cinnamon·Xfce·Unity 등에서는 libsecret 을 쓰고, 고른 보관함을 쓸 수 없으면 `basic` 으로 물러납니다[2][4]. 데스크톱 포털 (desktop portal) 로 비밀을 받는 방식도 있습니다[18]. 보관함 안에 남는 항목 이름(`Chrome Safe Storage`, `Chromium Safe Storage`)과 보관함 파일 구조는 [비밀번호 보관함](keyring.md) 에서 다룹니다.

### Firefox 의 저장 비밀번호

Firefox 는 프로필 안의 `logins.json` 과 `key4.db`(옛 판은 `key3.db`)에 비밀번호를 둡니다[8]. `logins.json` 의 항목에는 `hostname`, `encryptedUsername`, `encryptedPassword`, `timeCreated`, `timeLastUsed`, `timePasswordChanged` 가 있습니다[8]. Firefox 58 이후 판에서 기본 암호 (primary password) 를 걸지 않았으면 공개 도구가 값을 바로 풀어 보여 줍니다[8].

## 증거로서 의미

### 증명하는 것

- 특정 계정의 홈 폴더에 있는 프로필에 이 URL 을 이 시각에 방문한 기록이 있다는 것.
- 프로필이 어느 경로에 있는지로, 그 계정이 브라우저를 어떤 방식(배포판 패키지·Snap·Flatpak)으로 설치해 썼는지.
- Chrome 계열 암호문의 앞머리가 `v10` 인지 `v11` 인지로, 저장할 때 비밀번호 보관함을 썼는지 고정 키를 썼는지.
- Firefox `logins.json` 의 시각으로, 어떤 사이트의 비밀번호를 언제 저장하고 언제 마지막으로 썼는지.

### 증명하지 못하는 것

- 그 계정을 쓴 사람이 누구인지. 같은 계정으로 여러 사람이 로그인했을 수 있으므로 [로그인 기록](../logins/wtmp-btmp-lastlog.md) 과 맞춰 봐야 합니다.
- 기록이 없다는 것. 프로필이 여러 경로로 갈라지므로 표의 경로를 모두 뒤진 뒤에만 "기록이 없다" 고 쓸 수 있습니다.
- `v11` 값의 내용. 보관함이 잠겨 있으면 앞머리 말고는 알 수 없습니다.
- 페이지 내용을 사람이 실제로 읽었는지.

## 시각 해석

| 값 | 형식 | 기준 |
|---|---|---|
| Chrome `visits.visit_time`, 쿠키 `creation_utc`·`last_access_utc`, 다운로드 `start_time`·`end_time`, `logins.date_created`·`date_last_used`·`date_password_modified` | WebKit 시각: 1601-01-01 UTC 부터의 마이크로초[7][9] | UTC |
| Firefox `moz_historyvisits.visit_date`, 쿠키 `creationTime`·`lastAccessed`, `moz_annos.dateAdded`·`lastModified` | Unix 마이크로초: 1970-01-01 UTC 부터의 마이크로초[8][10] | UTC |
| Firefox `logins.json` 의 `timeCreated`·`timeLastUsed`·`timePasswordChanged`, `extensions.json` 의 `installDate`·`updateDate` | Unix 밀리초[8] | UTC |

데이터베이스 안의 시각은 모두 UTC 라서 검체의 시간대 설정과 상관없습니다. 보고서에 현지 시각으로 옮길 때는 [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md) 에서 확인한 시간대를 씁니다. 값을 바꾸는 법과 흔한 착오는 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 과 다른 판의 [시각 값 형식](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.html) 쪽을 봅니다.

데이터베이스 파일의 수정 시각은 파일이 마지막으로 바뀐 때를 보여 줄 뿐이라, 개별 방문의 시각으로 쓰지 않습니다. `-wal` 파일에는 본 파일에 아직 합쳐지지 않은 최근 기록이 있을 가능성이 있으므로 둘을 함께 봅니다.

## 함정과 한계

- **경로를 빠뜨리기 쉽습니다.** Firefox 만 해도 옛 위치·XDG 위치에 Snap·Flatpak 을 곱해 여섯 곳이 있습니다[8]. Firefox 는 옛 `~/.mozilla` 가 남아 있으면 계속 그곳을 쓰므로, 판을 올린 뒤에도 두 위치가 함께 있을 수 있습니다[5].
- **환경 변수로 위치가 바뀝니다.** `CHROME_CONFIG_HOME`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `MOZ_LEGACY_HOME` 을 설정한 계정은 기본 경로에 프로필이 없을 수 있습니다[1][5]. [셸 시작 파일](../persistence/shell-startup.md) 에서 이 변수를 찾아봅니다.
- **Chrome 캐시는 `~/.config` 가 아니라 `~/.cache` 에 있습니다[1].** 설정 폴더만 떠 오면 캐시가 빠집니다.
- **`-wal`·`-journal` 파일을 함께 모읍니다.** 마지막 기록이 아직 본 데이터베이스에 합쳐지지 않았을 수 있습니다. 수집 정의 가운데 UAC 는 `History*`·`places.sqlite*` 처럼 이름 뒤에 별표를 붙여, ForensicArtifacts 는 `History-journal`·`places.sqlite-wal` 처럼 이름을 하나씩 적어 함께 모읍니다[12][13][15].
- **수집 도구마다 빠지는 경로가 다릅니다.** UAC 의 Chromium 정의는 Snap·Flatpak 폴더만 모으고 `~/.config/chromium` 은 모으지 않습니다[14]. UAC 의 Firefox 정의는 `~/.mozilla/firefox` 와 Snap·Flatpak 폴더를 모으지만 네이티브 설치의 `~/.config/mozilla/firefox` 는 빠집니다[15]. ForensicArtifacts 의 Firefox 캐시 정의는 이름이 `*.default`·`*.default-*` 인 프로필만 봅니다[12]. Velociraptor 의 `Linux.Applications.Chrome.Extensions` 는 기본값이 `~/.config/google-chrome` 만 뒤집니다[17]. 도구 결과가 비었으면 표의 경로를 손으로 확인합니다.
- **UAC 의 Linux Chrome 캐시 항목에는 macOS 경로(`Library/Caches/Google/Chrome`)가 섞여 있습니다[16].** Linux 검체에 이 경로가 없어도 수집이 잘못된 것은 아닙니다.
- **문서와 코드가 `basic` 방식을 다르게 적습니다.** Chromium 문서는 `basic` 을 평문 저장이라고 적고[4], 코드는 고정 키로 `v10` 암호화를 합니다[3]. 키가 브라우저 안에 있으니 보호가 없다는 점은 같습니다.

## 직접 분석해 보기

### 헥스로 한 번: 암호화 값의 앞머리

`Login Data` 와 같은 이름의 `-wal`·`-journal` 파일을 함께 작업 폴더로 복사한 뒤, 복사본에서 암호문 앞 3바이트만 뽑습니다.

```
$ sqlite3 'Login Data' "SELECT origin_url, hex(substr(password_value,1,3)) FROM logins;"
https://login.example.com/|763131
https://intranet.example.org/|763131
```

위 출력은 만든 예시입니다. `76 31 31` 은 ASCII 로 `v11` 이므로, 이 계정은 비밀번호를 저장할 때 GNOME Keyring 이나 KWallet 에 둔 비밀을 썼다는 뜻입니다[2]. `763130` 이 나오면 `basic` 방식입니다[3]. 같은 프로필 안에 두 값이 섞여 있으면 저장 방식이 도중에 바뀌었을 가능성이 있으므로, 행마다 `date_created` 와 함께 봅니다.

### 공개 도구로 한 번

- dissect.target 의 `chrome`·`chromium`·`firefox` 플러그인은 Linux 경로(Snap·Flatpak 포함)를 스스로 찾아 방문 기록·쿠키·다운로드·확장·비밀번호 기록을 뽑습니다[6][7][8]. Chromium 계열의 `v11` 값은 풀지 않고 경고 로그만 남깁니다[7].
- plaso 의 `linux` 프리셋은 `webhist` 프리셋을 포함하고, `webhist` 에는 `sqlite/chrome_27_history`, `sqlite/chrome_66_cookies`, `chrome_cache`, `chrome_preferences`, `sqlite/firefox_history`, `sqlite/firefox_downloads`, `sqlite/firefox_10_cookies`, `firefox_cache` 등이 들어 있습니다[11]. 결과를 다른 흔적과 한 줄로 세우는 법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 에서 다룹니다.
- Velociraptor 의 `Linux.Applications.Chrome.Extensions` 는 `manifest.json` 을 읽고, `default_locale` 이 있으면 `_locales` 의 `messages.json` 에서 확장 이름을 풀어 줍니다[17].

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [비밀번호 보관함](keyring.md) | `v11` 이면 보관함에 `Chrome Safe Storage`·`Chromium Safe Storage` 항목이 있는가 |
| [최근 연 파일](../execution/recently-used.md) | 다운로드한 파일을 뒤에 열었는가 |
| [snap·flatpak](../packages/snap-flatpak.md) | 프로필 경로와 설치 방식이 맞는가, 설치·제거 시각 |
| [인증 로그](../logins/auth-log.md)·[로그인 기록](../logins/wtmp-btmp-lastlog.md) | 방문 시각에 그 계정이 로그인해 있었는가 |
| [GNOME 흔적](gnome.md)·[KDE 흔적](kde.md) | 같은 시간대의 데스크톱 활동 |
| [메모리 분석](../../03-techniques/analysis/memory-analysis.md) | 디스크에 아직 쓰지 않은 탭·세션 |

## 실습

NIST CFReDS 같은 공개 검체 모음에서 Linux 데스크톱 이미지를 골라 풀어 봅니다.

1. 홈 폴더마다 표의 경로를 모두 뒤졌을 때, 브라우저 프로필은 몇 개이고 각각 어떤 설치 방식의 경로인가?
2. Firefox 프로필이 `~/.mozilla/firefox` 와 `~/.config/mozilla/firefox` 에 함께 있다면, 두 `places.sqlite` 의 마지막 방문 시각은 어떻게 다른가?
3. Chrome 계열 `Login Data` 의 `password_value` 앞머리는 `v10` 인가 `v11` 인가, 그리고 그 결과가 설치된 데스크톱 환경과 맞는가?
4. `places.sqlite-wal` 이나 `History-journal` 을 빼고 열었을 때와 함께 열었을 때 방문 기록 수가 달라지는가?
5. 다운로드 기록의 저장 경로에 있던 파일이 지금도 있는가, 없다면 [휴지통](../file-activity/trash.md) 에 있는가?

## 참고 문헌

1. Chromium, docs/user_data_dir.md. https://github.com/chromium/chromium/blob/main/docs/user_data_dir.md
2. Chromium, components/os_crypt/async/browser/freedesktop_secret_key_provider.cc·.h. https://github.com/chromium/chromium/blob/main/components/os_crypt/async/browser/freedesktop_secret_key_provider.cc , https://github.com/chromium/chromium/blob/main/components/os_crypt/async/browser/freedesktop_secret_key_provider.h
3. Chromium, components/os_crypt/async/browser/posix_key_provider.cc. https://github.com/chromium/chromium/blob/main/components/os_crypt/async/browser/posix_key_provider.cc
4. Chromium, docs/linux/password_storage.md. https://github.com/chromium/chromium/blob/main/docs/linux/password_storage.md
5. Mozilla Firefox, toolkit/xre/nsXREDirProvider.cpp. https://github.com/mozilla-firefox/firefox/blob/main/toolkit/xre/nsXREDirProvider.cpp
6. fox-it dissect.target, dissect/target/plugins/apps/browser/chrome.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/browser/chrome.py
7. fox-it dissect.target, dissect/target/plugins/apps/browser/chromium.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/browser/chromium.py
8. fox-it dissect.target, dissect/target/plugins/apps/browser/firefox.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/browser/firefox.py
9. plaso, plaso/parsers/sqlite_plugins/chrome_history.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/sqlite_plugins/chrome_history.py
10. plaso, plaso/parsers/sqlite_plugins/firefox_history.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/sqlite_plugins/firefox_history.py
11. plaso, plaso/data/presets.yaml. https://github.com/log2timeline/plaso/blob/main/plaso/data/presets.yaml
12. ForensicArtifacts, artifacts/data/webbrowser.yaml. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/webbrowser.yaml
13. UAC, artifacts/files/browsers/chrome.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/browsers/chrome.yaml
14. UAC, artifacts/files/browsers/chromium.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/browsers/chromium.yaml
15. UAC, artifacts/files/browsers/firefox.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/browsers/firefox.yaml
16. UAC, artifacts/files/browsers/cache.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/browsers/cache.yaml
17. Velociraptor, artifacts/definitions/Linux/Applications/Chrome/Extensions.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Applications/Chrome/Extensions.yaml
18. Chromium, components/os_crypt/async/browser/secret_portal_key_provider.cc. https://github.com/chromium/chromium/blob/main/components/os_crypt/async/browser/secret_portal_key_provider.cc
