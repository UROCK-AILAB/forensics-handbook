---
title: "GNOME 흔적"
parent: "아티팩트 · 데스크톱 환경"
nav_order: 840
---

# GNOME 흔적 (GNOME)

GNOME 데스크톱은 사용자 홈 아래에 앱을 얼마나 오래 앞에 띄워 썼는지, 어떤 설정을 켜고 껐는지, 파일 관리자가 어떤 경로에 메타데이터를 붙였는지를 파일로 남기고, 이 파일들로 그 계정의 데스크톱 사용 모습과 "왜 다른 기록이 비어 있는지" 를 함께 읽을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

Ubuntu 24.04 와 Rocky 9.5(RHEL 9 재빌드판)를 기본 설치한 조건에서 두 배포판 모두 기본 데스크톱이 GNOME 이고 디스플레이 서버는 Wayland 와 XWayland, 오디오 서버는 PipeWire 였습니다[10]. 그래서 두 기준 배포판의 데스크톱 사용자 조사는 대개 GNOME 흔적에서 시작합니다.

이 페이지에서 다루는 흔적은 GNOME 구성 요소가 각자 제 일을 하려고 쓰는 파일입니다.

- **앱 사용 점수 (application_state)**: gnome-shell 이 앱 창에 포커스가 머문 시간을 세어 자주 쓰는 앱 순서를 정하려고 씁니다[1].
- **설정 데이터베이스 (dconf)**: GNOME 앱이 GSettings 로 저장한 사용자 설정이 바이너리 파일 하나에 모입니다[4].
- **파일 메타데이터 (gvfs-metadata)**: 파일 관리자 같은 GIO 클라이언트가 경로에 붙인 속성을 gvfsd-metadata 데몬이 대신 써 줍니다[6].
- **검색 색인 (Tracker)**: 파일 색인기가 캐시 폴더에 색인 데이터베이스를 둡니다[7][8].
- **로그인 화면 설정 (GDM)**: 자동 로그인·원격 로그인 같은 로그인 관리자 설정 키입니다[9].

최근 연 파일 목록, 휴지통, 썸네일, 자동 실행 항목도 GNOME 에서 쓰지만 데스크톱 환경에 묶이지 않은 freedesktop 규약이라 따로 다룹니다. [최근 연 파일](../execution/recently-used.md), [휴지통](../file-activity/trash.md), [썸네일 캐시](../file-activity/thumbnails.md), [데스크톱 자동 실행](../persistence/xdg-autostart.md) 을 봅니다. 로그인 때 키링이 풀리는 기록과 키링 파일은 [비밀번호 보관함](keyring.md) 에서 다룹니다.

## 위치와 버전별 차이

아래 경로는 XDG 기본 폴더를 따르므로 두 기준 배포판에서 같습니다. `$XDG_CONFIG_HOME` 은 보통 `~/.config`, `$XDG_DATA_HOME` 은 보통 `~/.local/share` 입니다.

| 흔적 | 경로 | 형식 |
|---|---|---|
| 앱 사용 점수 | `~/.local/share/gnome-shell/application_state`[2] | XML[1] |
| 사용자 설정 | `$XDG_CONFIG_HOME/dconf/user`, 프로필이 `service-db` 이면 `$XDG_CONFIG_HOME/dconf/user.txt`[4] | GVDB 바이너리[5], `user.txt` 는 텍스트 키파일[4] |
| 시스템 설정 | `/etc/dconf/profile/`(프로필), `/etc/dconf/db/`(시스템 DB), `/etc/dconf/db/local.d/`·`/etc/dconf/db/local.d/locks/`(시스템 DB 이름이 `local` 일 때의 키파일과 잠금)[4] | 프로필·키파일은 텍스트, DB 는 GVDB |
| 파일 메타데이터 | `~/.local/share/gvfs-metadata/`[6][7] | 트리 파일과 저널 파일, 빅엔디언 바이너리[6] |
| 검색 색인(Tracker 3) | `~/.cache/tracker3/files/` 의 `*Audio.db*`·`*Documents.db*`·`*FileSystem.db*`·`*Pictures.db*`·`*Software.db*`·`*Video.db*`·`meta.db*`[7] | 파일 이름으로 보면 SQLite 일 가능성이 있음 |
| 검색 색인(tracker 폴더) | `~/.cache/tracker/`, `~/.local/share/tracker/data/`[2] | 실제 데이터로 확인 |
| GNOME Text Editor 최근 파일 | `~/.local/share` 아래 `session.gvariant`, Flatpak·Snap 판은 `~/.var/app`·`~/snap` 아래[7] | 실제 데이터로 확인 |
| gedit 최근 파일 | `~/.local/share` 아래 `gedit-metadata.xml`, Flatpak·Snap 판은 `~/.var/app`·`~/snap` 아래[7] | 실제 데이터로 확인 |
| X 세션 오류 기록 | `~/.xsession-errors`[7] | 텍스트 |
| 사용자 D-Bus 설정 | `~/.local/share/dbus-1`, 시스템은 `/etc/dbus-1`·`/usr/share/dbus-1`[7] | 텍스트 |
| 설치된 앱 목록 | `/usr/share/applications/`, `/usr/local/share/applications/`, `/var/lib/snapd/desktop/applications/`, `/var/lib/flatpak/exports/share/applications/`, `~/.local/share/applications/` 의 `*.desktop`[12] | 텍스트 |

Tracker 경로는 수집 도구마다 다릅니다. ForensicArtifacts 정의는 `~/.cache/tracker/` 와 `~/.local/share/tracker/data/` 를 적고[2], UAC 는 `~/.cache/tracker3/files/` 를 적습니다[7]. Tracker 3 색인기(지금 이름 localsearch)는 저장소를 캐시 폴더에 두므로[8], 두 경로를 다 확인합니다.

GDM 설정 키 목록은 판마다 다릅니다. GDM 46.0 에는 `daemon/WaylandEnable`·`daemon/PreferredDisplayServer`·`security/AllowRemoteAutoLogin`·`xdmcp/Enable` 이 있고 `ShowLocalGreeter` 가 `xdmcp/` 아래에 있지만, 최신 개발판에는 이 키들이 없고 `daemon/ShowLocalGreeter`·`daemon/FallbackSession` 이 있습니다[9]. 분석 대상의 GDM 판과 설정 파일 위치는 [dpkg·apt 기록](../packages/dpkg-apt.md) 이나 [rpm·dnf·yum 기록](../packages/rpm-dnf.md) 의 패키지 파일 목록에서 확인합니다.

## 구조

### application_state

gnome-shell 은 아래 모양의 XML 을 통째로 다시 씁니다[1]. 값은 만든 예시입니다.

```xml
<?xml version="1.0"?>
<application-state>
  <context id="">
    <application id="org.gnome.Nautilus.desktop" score="24.5" last-seen="1719664640"/>
    <application id="firefox.desktop" score="3" last-seen="1719661000"/>
  </context>
</application-state>
```

| 속성 | 뜻 |
|---|---|
| `id` | 앱 ID(`.desktop` 파일 이름)[1] |
| `score` | 포커스 7초마다 1 씩 오르는 실수 점수[1] |
| `last-seen` | gnome-shell 이 그 앱을 마지막으로 본 시각, Unix epoch 초[1] |

점수 규칙은 코드 상수로 정해져 있습니다[1].

- 포커스가 다른 창으로 옮겨 갈 때 그동안 머문 시간을 7초로 나눈 몫만큼 점수를 더하고, 7초가 안 되면 더하지 않습니다.
- 어느 앱 점수가 `SCORE_MAX`(3600×50÷7, 정수로 25714)를 넘으면 모든 앱 점수를 반으로 나눕니다.
- 세션이 유휴 상태로 바뀌면 포커스 시작부터 30초만 센 것으로 칩니다.
- 점수가 오르면 300초 뒤 저장을 예약하고, 예약이 걸려 있는 동안 생긴 변경은 그 한 번의 저장에 함께 들어갑니다.
- 파일을 읽어 들일 때, 점수가 `SCORE_MIN`(25714를 오른쪽으로 3비트 민 값, 3214) 미만이고 `last-seen` 이 7일보다 오래된 앱을 지웁니다.
- 저장할 때 지금 시스템에서 찾을 수 없는 앱 ID 는 건너뜁니다.

`org.gnome.desktop.privacy` 의 `remember-app-usage` 가 false 이면 새 점수 수집과 저장 예약을 멈추고, 이미 저장된 데이터는 그대로 둡니다[1][3].

### dconf 사용자 DB

dconf 는 프로필에 적힌 데이터베이스들을 차례로 봅니다[4]. 환경 변수 `DCONF_PROFILE` 이 있으면 그 프로필을, 없으면 `/etc/dconf/profile/user` 를 열고, 그것도 없으면 `user-db:user` 한 줄만 있는 것처럼 동작합니다[4]. 프로필 첫 줄이 쓰기용 DB 이고 나머지 줄이 읽기 전용 시스템 DB 입니다[4]. `user-db:user` 이면 `$XDG_CONFIG_HOME/dconf/user` 가 바이너리 DB 이고, `service-db:keyfile/user` 이면 바이너리는 `XDG_RUNTIME_DIR` 에 두고 `$XDG_CONFIG_HOME/dconf/user.txt` 텍스트 파일과 양방향으로 맞춥니다[4].

바이너리 DB 는 GVDB 형식이고 머리는 24바이트입니다[5].

| 오프셋 | 크기 | 필드 | 값 |
|---|---|---|---|
| 0x00 | 8 | `signature` | ASCII `GVariant`(리틀엔디언 정수 1918981703, 1953390953)[5] |
| 0x08 | 4 | `version` | 0 이어야 읽음[5] |
| 0x0C | 4 | `options` | 옵션 |
| 0x10 | 8 | `root` | 루트 해시 표의 시작·끝 오프셋(각 4바이트 리틀엔디언)[5] |

서명이 바이트 순서가 뒤집힌 모양이면 읽는 코드는 빅엔디언 파일로 보고 값을 뒤집어 읽습니다[5]. 해시 표의 항목은 해시 값·부모 번호·키 위치(각 4바이트), 키 길이(2바이트), 종류(1바이트), 빈 자리(1바이트), 값 자리(8바이트)로 되어 있고[5], 값 자체는 GVariant 로 직렬화되어 있습니다. 파일 안에는 키마다 바뀐 시각을 적는 필드가 없습니다[5].

스키마 경로 `org.gnome.desktop.privacy` 는 dconf 경로 `/org/gnome/desktop/privacy/` 에 대응합니다[3]. 조사에 쓸 만한 키와 기본값은 아래와 같습니다[3].

| 키 | 기본값 | 뜻 |
|---|---|---|
| `remember-recent-files` | true | false 이면 앱이 최근 파일을 기억하지 않음 |
| `recent-files-max-age` | -1 | 최근 파일을 기억하는 날 수, 0 이면 기억 안 함, -1 이면 무기한 |
| `remember-app-usage` | true | false 이면 앱 사용을 기록하지 않음 |
| `remove-old-trash-files` | false | true 이면 `old-files-age` 일보다 오래된 휴지통 파일을 자동 삭제 |
| `remove-old-temp-files` | false | true 이면 오래된 임시 파일을 자동 삭제 |
| `old-files-age` | 30 | 휴지통·임시 파일을 오래됐다고 보는 날 수 |
| `usb-protection` | true | USBGuard 가 있으면 `usb-protection-level` 대로 USB 장치를 막음 |
| `usb-protection-level` | `'lockscreen'` | `lockscreen` 은 잠금 화면일 때만, `always` 는 늘 새 USB 장치를 거부 |
| `disable-camera`, `disable-microphone` | false | true 이면 앱이 카메라·마이크를 쓰지 않아야 함 |

DB 파일에는 기본값과 다른 값만 들어 있을 가능성이 있으므로, 키가 없으면 스키마 기본값으로 읽습니다.

### gvfs-metadata

트리 파일은 경로별 메타데이터의 안정본이고, 저널 파일은 그 뒤에 생긴 변경을 차례로 적은 기록입니다[6]. 홈 폴더 아래 경로는 `home` 트리에, 장치별 트리가 없는 경로는 `root` 트리에 들어가며, 이동식 볼륨의 `uuid-`·`label-` 트리 이름은 [USB 장치 연결 기록](../devices/usb.md) 에서 다룹니다. 저널 파일 이름은 트리 파일 이름 뒤에 `-`, 트리 머리의 `random_tag` 를 16진수 8자리로 쓴 값, `.log` 를 붙인 형식입니다(예: `home-0a1b2c3d.log`)[6]. 트리 파일이 NFS 위에 있으면 저널은 `XDG_RUNTIME_DIR` 아래 `gvfs-metadata` 폴더에 둡니다[6].

트리 파일 머리는 32바이트이고 정수는 모두 빅엔디언입니다[6].

| 오프셋 | 크기 | 필드 |
|---|---|---|
| 0x00 | 6 | 매직 `DA 1A 6D 65 74 61`(`\xda\x1ameta`) |
| 0x06 | 1·1 | 판 번호 major 1, minor 0 |
| 0x08 | 4 | `rotated`, 0 이 아니면 새 트리로 바뀐 옛 파일 |
| 0x0C | 4 | `random_tag`, 짝이 되는 저널 이름에 쓰임 |
| 0x10 | 4 | 루트 디렉터리 항목 오프셋 |
| 0x14 | 4 | 키 이름 목록 오프셋 |
| 0x18 | 8 | `time_t_base`, 다른 시각 값의 기준 |

디렉터리 항목마다 이름·자식·메타데이터 오프셋과 `last_changed` 가 있고, `last_changed` 는 `time_t_base` 에서 몇 초 뒤인지를 4바이트로 적습니다[6]. 0 은 "정해지지 않음" 이라 기준은 쓰인 시각 중 가장 이른 값에서 1을 뺀 값으로 잡습니다[6]. 메타데이터 블록은 키 번호와 값 오프셋 쌍의 배열이고, 키 번호의 최상위 비트가 켜져 있으면 값이 문자열 목록입니다[6].

저널 파일은 매직 `\xda\x1ajour`, 판 번호, `random_tag`, 파일 크기, 항목 수로 시작하고, 새로 만들 때 크기는 32KiB 입니다[6]. 항목은 아래 순서로 이어집니다[6].

| 필드 | 크기 |
|---|---|
| `entry_size` | 4 |
| `crc32`(뒤따르는 데이터 전체) | 4 |
| `mtime` | 8 |
| 연산 종류 | 1 |
| 경로(NUL 로 끝남, 복사·이동이면 대상 경로) | 가변 |
| 연산별 데이터(키·값, 복사면 원본 경로) | 가변 |
| `entry_size` 되풀이 | 4 |

연산 종류 값은 형식 설명 문서와 코드가 다릅니다. 형식 설명 문서는 0 설정, 1 목록 설정, 2 해제, 3 이동, 4 복사로 적었지만, 코드의 열거형은 0 `SET_KEY`, 1 `SETV_KEY`, 2 `UNSET_KEY`, 3 `COPY_PATH`, 4 `REMOVE_PATH` 이고 읽고 쓰는 코드는 이 값을 씁니다[6]. 읽는 쪽은 체크섬이 처음 맞지 않는 항목 앞까지만 믿습니다[6].

### GDM 설정 키

최신 개발판 GDM 이 읽는 키는 `daemon/AutomaticLoginEnable`, `daemon/AutomaticLogin`, `daemon/TimedLoginEnable`, `daemon/TimedLogin`, `daemon/TimedLoginDelay`, `daemon/InitialSetupEnable`, `daemon/XorgEnable`, `daemon/RemoteLoginEnable`, `daemon/ShowLocalGreeter`, `daemon/FallbackSession`, `debug/Enable`, `security/DisallowTCP` 입니다[9]. 판에 따른 차이는 위 "위치와 버전별 차이" 절에 적었습니다. 조사에서는 자동 로그인과 시간 제한 로그인이 켜져 있는지, 어느 계정으로 되어 있는지를 먼저 봅니다.

## 증거로서 의미

### 증명하는 것

- application_state 에 앱 ID 가 있으면, 이 계정의 GNOME 세션에서 그 앱이 실행 상태가 되었거나 창에 포커스가 머문 적이 있다는 뜻입니다[1]. 점수는 포커스를 받은 시간의 상대적 크기를 보여 주고, `last-seen` 은 gnome-shell 이 그 앱을 마지막으로 본 시각입니다.
- dconf 사용자 DB 의 privacy 키는 기록이 왜 비었는지를 설명하는 근거가 됩니다. 예를 들어 `remember-recent-files` 가 false 이면 [최근 연 파일](../execution/recently-used.md) 이 비어 있어도 이상하지 않고, `remove-old-trash-files` 가 true 이면 [휴지통](../file-activity/trash.md) 에서 오래된 파일이 자동으로 사라졌을 수 있습니다[3].
- gvfs-metadata 에 경로가 있으면, 그 경로에 이 계정의 GIO 클라이언트(예: Nautilus 파일 관리자)가 메타데이터를 쓴 적이 있다는 뜻입니다[6]. 트리의 `last_changed` 와 저널의 `mtime` 은 그 메타데이터가 바뀐 시각입니다.
- GDM 자동 로그인 키가 켜져 있으면 비밀번호 입력 없이 그 계정으로 세션이 열릴 수 있는 구성이었다는 뜻입니다[9].

### 증명하지 못하는 것

- application_state 는 앱이 어떤 파일을 열었는지, 몇 번 실행됐는지, 언제 처음 실행됐는지를 알려 주지 않습니다. 7초 미만의 포커스는 점수에 들어가지 않습니다[1].
- `remember-app-usage` 가 false 이면 기록이 멈추므로, 파일에 없는 앱을 "쓰지 않았다" 고 볼 수 없습니다[1].
- dconf 사용자 DB 에는 값을 언제 바꿨는지 나와 있지 않습니다. 파일 수정 시각은 어떤 키든 마지막으로 쓴 때만 가리킵니다[4][5].
- gvfs-metadata 는 파일 내용이나 사용자가 파일을 열어 읽었는지를 보여 주지 않습니다. 메타데이터를 쓴 행위만 남습니다.
- `.xsession-errors` 와 Tracker 색인은 사용자의 조작 하나하나를 기록하는 장치가 아닙니다. 앱 오류 줄이나 색인된 파일 목록으로 보조 근거만 됩니다.

## 시각 해석

| 값 | 형식 | 무엇이 바뀔 때 바뀌나 |
|---|---|---|
| application_state `last-seen` | Unix epoch 초, UTC | 앱이 실행 상태로 바뀔 때, 포커스가 다른 창으로 옮겨 갈 때, 세션이 유휴 상태로 바뀔 때[1] |
| application_state 파일 수정 시각 | 파일 시스템 시각 | 점수가 오른 뒤 최대 300초 지나 파일을 통째로 다시 쓸 때[1] |
| dconf `user` 파일 수정 시각 | 파일 시스템 시각 | dconf-service 가 새 파일을 써서 옛 파일 위로 이름을 바꿀 때[4] |
| gvfs 트리 `last_changed` | `time_t_base` + 초, UTC | 그 경로의 메타데이터가 바뀔 때[6] |
| gvfs 저널 `mtime` | Unix epoch 초(8바이트), UTC | 데몬이 연산을 받을 때, `time(NULL)` 값[6] |

유휴 상태로 넘어가면 `last-seen` 은 실제 유휴 시작 시각이 아니라 포커스 시작에서 30초 뒤로 적힙니다[1]. application_state 의 파일 수정 시각은 파일 안 가장 늦은 `last-seen` 보다 몇 분 늦을 수 있습니다. 시각 값 변환은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 을 봅니다.

## 함정과 한계

- **오래된 앱 정리**: 점수가 3214 미만이고 7일 넘게 안 보인 앱은 gnome-shell 이 파일을 읽을 때 지워집니다[1]. 점수 3214 는 반으로 나눈 적이 없을 때 포커스 약 6시간 15분에 해당하므로, 가끔 쓴 앱은 일주일 뒤 새 세션에서 사라질 가능성이 큽니다.
- **지운 앱**: 저장할 때 시스템에서 찾을 수 없는 앱 ID 는 빠지므로, 앱을 지운 뒤 다음 저장에서 그 앱 줄이 사라집니다[1].
- **점수 반감**: 한 앱이 `SCORE_MAX` 를 넘을 때마다 모든 점수가 반이 되므로, 점수×7 을 사용 시간 초로 바로 바꾸면 안 됩니다[1].
- **dconf 프로필**: 프로필이 `service-db` 이면 `~/.config/dconf/user` 가 없고 `user.txt` 에 값이 있습니다[4]. `DCONF_PROFILE` 로 홈 안의 다른 프로필을 가리킬 수도 있으므로[4] 세션 환경 변수를 설정한 시작 파일도 봅니다.
- **dconf 를 문자열로 검색**: 바이너리 DB 를 `strings` 로 살펴보면 키 이름은 보이지만 값은 GVariant 직렬화라 형식을 알아야 바르게 읽습니다.
- **시스템 잠금**: `/etc/dconf/db/` 의 `locks` 폴더에 잠긴 키는 사용자가 바꿀 수 없습니다[4]. 사용자 DB 의 값과 실제로 적용된 값이 다를 수 있습니다.
- **gvfs 저널**: 최근 변경은 트리보다 저널에 먼저 들어갑니다[6]. 트리만 읽으면 최근 변경을 놓칩니다. 저널이 차면 새 트리를 쓰고 옛 저널을 지우므로[6] 연산별 기록은 사라지고 경로별 `last_changed` 만 남습니다.
- **Tracker 경로**: 수집 도구마다 `tracker` 와 `tracker3` 폴더 중 한쪽만 적으므로, 도구 하나의 수집본만 보면 색인을 놓칠 수 있습니다[2][7].
- **캐시 폴더**: Tracker 색인은 `~/.cache` 아래라 사용자가 캐시를 비우면 함께 사라집니다[7][8].

## 직접 분석해 보기

### 헥스로 한 번: dconf 와 gvfs 트리 머리

아래는 명세로 만든 예시입니다. 서명과 판 번호 밖의 값은 지어낸 값입니다.

dconf `user` 파일 첫 24바이트입니다.

```
00000000  47 56 61 72 69 61 6e 74  00 00 00 00 00 00 00 00  |GVariant........|
00000010  18 00 00 00 a0 00 00 00                           |........|
```

1. 0x00 의 8바이트가 `GVariant` 이면 GVDB 파일입니다[5].
2. 0x08 의 `00 00 00 00` 은 판 번호 0 입니다. 0 이 아니면 읽는 코드가 거부합니다[5].
3. 0x10 의 `18 00 00 00` 은 루트 해시 표가 오프셋 0x18 에서 시작한다는 뜻이고, 0x14 의 `a0 00 00 00` 은 0xA0 에서 끝난다는 뜻입니다.

gvfs-metadata 의 `home` 트리 첫 32바이트입니다.

```
00000000  da 1a 6d 65 74 61 01 00  00 00 00 00 0a 1b 2c 3d
00000010  00 00 00 40 00 00 00 20  00 00 00 00 66 80 00 00
```

1. 0x00 의 `da 1a 6d 65 74 61` 이 매직이고, 0x06 의 `01 00` 은 판 1.0 입니다[6].
2. 0x08 의 `rotated` 가 0 이라 지금 쓰이는 트리입니다.
3. 0x0C 의 `random_tag` 가 0x0a1b2c3d 이므로 짝이 되는 저널은 `home-0a1b2c3d.log` 입니다[6]. 저널 머리의 `random_tag` 도 같아야 합니다[6].
4. 0x18 의 `time_t_base` 는 0x66800000 = 1719664640, 곧 2024-06-29 12:37:20 UTC 입니다. 어떤 디렉터리 항목의 `last_changed` 가 0x00000E11(3601)이면 그 경로의 메타데이터는 2024-06-29 13:37:21 UTC 에 바뀐 것입니다.

같은 머리를 Python 표준 라이브러리로 읽으면 아래와 같습니다.

```python
import struct, datetime as dt
h = open("home", "rb").read(32)
magic, major, minor, rotated, tag, root, attrs, base = struct.unpack(">6sBBIIIIq", h)
print(magic, major, minor, rotated, f"home-{tag:08x}.log",
      dt.datetime.fromtimestamp(base, dt.timezone.utc))
```

### 공개 도구로 한 번

UAC 는 `gvfs-metadata` 폴더, Tracker 3 색인, `.xsession-errors`, GNOME Text Editor·gedit 최근 파일, 사용자 홈의 `*.desktop`(깊이 6까지), D-Bus 설정 폴더를 모읍니다[7]. ForensicArtifacts 에는 `GnomeApplicationState` 와 `GnomeTracker` 정의가 있습니다[2]. dissect.target 의 applications 플러그인은 위 표의 앱 폴더에서 `.desktop` 파일을 읽어 설치된 GUI 앱 목록과 `Exec` 줄을 보여 줍니다[12]. plaso 의 linux 프리셋 파서 목록에는 application_state·dconf·gvfs-metadata 를 읽는 파서가 없고 zeitgeist 활동 DB 파서는 있으며, zeitgeist `event` 테이블의 `timestamp` 는 Java 시각(밀리초)으로 읽습니다[11].

application_state 는 XML 이라 표준 라이브러리로 바로 읽고, 시각을 UTC 로 바꿔 타임라인에 넣습니다.

```python
import xml.etree.ElementTree as ET, datetime as dt
for a in ET.parse("application_state").iter("application"):
    t = dt.datetime.fromtimestamp(int(a.get("last-seen")), dt.timezone.utc)
    print(a.get("id"), a.get("score"), t.isoformat())
```

Tracker 파일은 머리 16바이트가 `SQLite format 3` 과 NUL 인지 먼저 보고, 맞으면 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html) 의 방법으로 사본을 엽니다.

## 교차 검증

| 함께 볼 흔적 | 확인할 것 |
|---|---|
| application_state `last-seen` ↔ [로그인 기록](../logins/wtmp-btmp-lastlog.md)·[인증 로그](../logins/auth-log.md) | 그 시각에 이 계정의 그래픽 세션이 열려 있었는지 |
| application_state 앱 ID ↔ [dpkg·apt 기록](../packages/dpkg-apt.md)·[rpm·dnf·yum 기록](../packages/rpm-dnf.md)·[snap·flatpak](../packages/snap-flatpak.md) | 앱이 언제 설치됐고 지금도 있는지 |
| dconf privacy 키 ↔ [최근 연 파일](../execution/recently-used.md)·[휴지통](../file-activity/trash.md) | 기록이 비어 있는 이유가 설정 때문인지 |
| gvfs `uuid-` 트리 ↔ [USB 장치 연결 기록](../devices/usb.md)·[마운트 기록](../devices/mounts.md) | 이동식 볼륨 위 파일을 GNOME 에서 다뤘는지 |
| gvfs 경로 ↔ [썸네일 캐시](../file-activity/thumbnails.md) | 같은 경로의 파일을 파일 관리자에서 보았는지 |
| `~/.local/share/dbus-1`·`*.desktop` ↔ [데스크톱 자동 실행](../persistence/xdg-autostart.md) | 세션 시작 때 도는 항목이 끼어 있는지 |
| GNOME 세션 ↔ [메모리 분석](../../03-techniques/analysis/memory-analysis.md) | XWayland 로 도는 앱에 X11 방식의 키 입력·화면 캡처 흔적이 있는지 |

XWayland 는 Wayland 를 지원하지 않는 앱에 X 프로토콜을 제공하므로 그런 앱은 X11 방식의 키 입력 가로채기·화면 캡처에 노출됩니다[10]. Chromium 과 Electron 앱이 여기에 해당했고, GNOME 은 D-Bus 서비스로 앱이 화면 녹화·스크린샷을 요청하도록 허용합니다[10]. 데스크톱 감시 악성 코드를 의심하면 디스크 흔적과 함께 메모리에서 이 경로를 확인합니다.

KDE 를 쓰는 시스템은 [KDE 흔적](kde.md), 브라우저는 [Linux 의 브라우저 프로필](browsers.md) 을 봅니다.

## 실습

GNOME 데스크톱이 깔린 공개 시험 데이터(NIST CFReDS 등)나 직접 만든 시험 가상 머신의 디스크 이미지로 풀어 봅니다.

1. 사용자 홈의 `application_state` 에서 점수가 가장 높은 앱 세 개와 각 `last-seen` 의 UTC 시각은?
2. 파일 수정 시각과 가장 늦은 `last-seen` 사이는 몇 초인가? 300초를 넘는다면 무엇 때문일 수 있는가?
3. `~/.config/dconf/user` 가 있는가, 아니면 `user.txt` 가 있는가? `/etc/dconf/profile/` 에는 어떤 프로필이 있는가?
4. dconf 에서 `remember-recent-files`·`remember-app-usage`·`remove-old-trash-files` 값은? 기본값과 다르다면 그 계정의 최근 파일·휴지통 기록과 어떻게 들어맞는가?
5. `gvfs-metadata` 폴더에 어떤 트리와 저널이 있고, 각 트리의 `random_tag` 와 저널 이름이 짝을 이루는가?
6. `home` 트리에서 `last_changed` 가 가장 늦은 경로는 무엇이고, 같은 경로의 썸네일이 있는가?
7. GDM 자동 로그인 키가 켜져 있다면 어느 계정이고, 로그인 기록과 맞는가?

## 참고 문헌

1. GNOME gnome-shell, src/shell-app-usage.c. https://github.com/GNOME/gnome-shell/blob/main/src/shell-app-usage.c
2. ForensicArtifacts, artifacts/data/linux.yaml(GnomeApplicationState·GnomeTracker). https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
3. GNOME gsettings-desktop-schemas, schemas/org.gnome.desktop.privacy.gschema.xml.in. https://github.com/GNOME/gsettings-desktop-schemas/blob/master/schemas/org.gnome.desktop.privacy.gschema.xml.in
4. GNOME dconf, docs/dconf-overview.xml(dconf(7)). https://github.com/GNOME/dconf/blob/main/docs/dconf-overview.xml
5. GNOME gvdb, gvdb/gvdb-format.h·gvdb-reader.c. https://github.com/GNOME/gvdb/blob/main/gvdb/gvdb-format.h , https://github.com/GNOME/gvdb/blob/main/gvdb/gvdb-reader.c
6. GNOME gvfs, metadata/file-format.txt·metatree.c·metabuilder.c, man/gvfsd-metadata.xml. https://github.com/GNOME/gvfs/tree/master/metadata , https://github.com/GNOME/gvfs/blob/master/man/gvfsd-metadata.xml
7. UAC, artifacts/files(system/gvfs_metadata.yaml·tracker.yaml·xsession_errors.yaml·desktop.yaml·dbus.yaml, applications/gnome_text_editor.yaml·gedit.yaml). https://github.com/tclahr/uac/tree/main/artifacts/files
8. GNOME localsearch, src/indexer/tracker-application.c. https://github.com/GNOME/localsearch/blob/main/src/indexer/tracker-application.c
9. GNOME gdm, common/gdm-settings-keys.h(main 과 46.0). https://github.com/GNOME/gdm/blob/main/common/gdm-settings-keys.h , https://github.com/GNOME/gdm/blob/46.0/common/gdm-settings-keys.h
10. Lukas Schmidt, Sebastian Strasda, Sebastian Schinzel, "Uncovering linux desktop espionage", Forensic Science International: Digital Investigation 53 (2025) 301921. https://doi.org/10.1016/j.fsidi.2025.301921
11. plaso, plaso/data/presets.yaml·plaso/parsers/sqlite_plugins/zeitgeist.py. https://github.com/log2timeline/plaso/blob/main/plaso/data/presets.yaml , https://github.com/log2timeline/plaso/blob/main/plaso/parsers/sqlite_plugins/zeitgeist.py
12. fox-it dissect.target, dissect/target/plugins/os/unix/applications.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/applications.py
