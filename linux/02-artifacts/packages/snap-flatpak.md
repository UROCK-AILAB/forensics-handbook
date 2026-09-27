---
title: "snap·flatpak"
parent: "아티팩트 · 패키지와 소프트웨어"
nav_order: 610
---

# snap·flatpak

snap 과 flatpak 은 배포판 패키지 관리자와 따로 움직이는 앱 설치 체계라서, dpkg·rpm 기록만 보면 이쪽으로 설치한 앱이 통째로 빠집니다.

## 무엇을 기록하나 · 왜 생기나

snap 은 snapd 데몬이 관리합니다. 앱마다 SquashFS 이미지 한 개(`.snap` 파일)를 받아 리비전(revision) 단위로 보관하고, 이 이미지를 마운트해서 실행합니다[1][2]. snapd 는 설치 목록과 작업 이력을 `state.json` 한 파일에 적고[1][3], 앱을 지울 때 사용자 데이터를 자동 스냅샷(automatic snapshot)으로 떼어 둡니다[5][6].

flatpak 은 앱과 런타임을 OSTree 저장소에 받아 두고, 거기서 꺼낸 사본(checkout)을 설치 폴더에 배포합니다[7]. 설치·갱신·제거·원격 저장소 변경은 systemd 저널에 전용 메시지로 남습니다[10][11].

두 체계 모두 앱의 사용자 데이터를 일반 경로(`~/.config` 등)가 아닌 전용 폴더에 둡니다. 같은 앱도 설치 방식에 따라 데이터 위치가 달라서, 예를 들어 Discord 데이터는 snap 판이면 `~/snap/discord`, flatpak 판이면 `~/.var/app/com.discordapp.Discord`, 그 밖에는 `~/.config/discord` 에 있습니다[16].

## 위치와 버전별 차이

### snap

| 경로 | 내용 |
|---|---|
| `/var/lib/snapd/snaps/이름_리비전.snap` | 설치된 snap 이미지(SquashFS)[1][2] |
| `/var/lib/snapd/state.json` | snapd 상태: 설치 목록, 작업(change) 이력, 설정[1][3] |
| `/var/lib/snapd/sequence/이름.json` | snap 별 순서(sequence) 파일[1][2] |
| `/var/lib/snapd/snapshots/` | 스냅샷(자동·수동)[1] |
| `/var/lib/snapd/desktop/applications/*.desktop` | 메뉴 항목[1][13] |
| `/var/lib/snapd/assertions`, `/var/lib/snapd/seed`, `/var/lib/snapd/cache`, `/var/cache/snapd` | 서명 문서(assertion), 초기 설치 묶음(seed), 내려받기 캐시, 이름·명령 목록·아이콘 캐시[1] |
| `/var/snap/이름/리비전`, `/var/snap/이름/common` | 시스템 쪽 앱 데이터[1][2] |
| `~/snap/이름/리비전`, `~/snap/이름/common` | 사용자 쪽 앱 데이터[1][2] |
| `/run/snapd.socket` | snapd API 소켓(라이브에서만)[1][14] |

사용자 쪽 데이터는 실험 옵션(hidden snap data dir)을 켜면 `~/snap` 대신 `~/.snap/data` 아래로 갑니다[1][2]. 두 곳을 다 봅니다.

마운트 위치는 배포판이 snapd 를 어떻게 꾸렸는지에 따라 다릅니다. snapd 는 `/snap` 이 실제 폴더면 그곳을 쓰고, `/snap` 이 없거나 `/var/lib/snapd/snap` 을 가리키는 심볼릭 링크면 `/var/lib/snapd/snap` 을 씁니다[1].

| 분석 대상의 `/snap` | 마운트 위치 |
|---|---|
| 실제 폴더 | `/snap/이름/리비전` |
| 없거나 `/var/lib/snapd/snap` 을 가리키는 심볼릭 링크 | `/var/lib/snapd/snap/이름/리비전` |

마운트 위치 아래 내용은 `.snap` 이미지를 펼쳐 보인 것이라서, 디스크 이미지에서는 `/var/lib/snapd/snaps` 의 이미지를 직접 엽니다.

### flatpak

| 경로 | 내용 |
|---|---|
| `/var/lib/flatpak/` | 시스템 설치(기본)[7] |
| `~/.local/share/flatpak/` | 사용자 설치[7] |
| `/etc/flatpak/installations.d/*.conf` | 추가 시스템 설치 위치. `[Installation "이름"]` 묶음에 `Path`(필수), `DisplayName`, `Priority`, `StorageType`[7][8] |
| `/etc/flatpak/remotes.d/`, `/usr/share/flatpak/remotes.d/` | 미리 넣어 둔 원격 저장소 정의. 같은 이름이면 `/etc` 쪽이 이깁니다[7] |
| 설치 폴더`/repo` | OSTree 저장소[7][11] |
| 설치 폴더`/app/`, `/runtime/` | 배포된 앱·런타임[7][11] |
| 설치 폴더`/exports/share/applications/*.desktop` | 메뉴 항목[11][13] |
| 설치 폴더`/.removed` | 지우거나 교체한 배포를 잠시 옮겨 두는 곳[11] |
| 설치 폴더`/sideload-repos` | 오프라인 설치 원본(사이드로드 저장소)을 가리키는 링크[7] |
| `~/.var/app/앱ID/` | 앱별 사용자 데이터(설정·캐시·데이터)[9] |

시스템 설치 경로는 빌드 설정과 환경 변수 `FLATPAK_SYSTEM_DIR` 로 바꿀 수 있고 기본값은 `/var/lib/flatpak` 입니다[7]. 그래서 분석 대상에 `/var/lib/flatpak` 이 없으면 `installations.d` 설정과 다른 위치의 `repo` 폴더를 함께 찾습니다.

## 구조

### snap: 이미지와 state.json

`.snap` 파일 이름은 `이름_리비전.snap` 입니다[2]. 이미지 안의 `meta/snap.yaml` 에 이름(`name`)과 버전(`version`)이 있습니다[12]. 파일 이름에는 리비전만 있어서, 사람이 읽는 버전은 `snap.yaml` 에서 봅니다.

`state.json` 최상위에는 `data`, `changes`, `tasks`, `warnings`, `notices`, `last-change-id`, `last-task-id`, `last-lane-id`, `last-notice-id`, `last-notice-timestamp` 가 있습니다[3]. 설치·갱신·제거 같은 작업 하나가 `changes` 안의 change 항목 하나이고, 필드는 다음과 같습니다[3].

| 필드 | 뜻 |
|---|---|
| `id` | change 번호(문자열) |
| `kind` | 작업 종류 |
| `summary` | 사람이 읽는 요약 |
| `status` | 상태 번호(0 기본, 1 Hold, 2 Do, 3 Doing, 4 Done, 5 Abort, 6 Undo, 7 Undoing, 8 Undone, 9 Error, 10 Wait) |
| `clean` | 정리 끝 여부 |
| `data` | 작업별 추가 값 |
| `task-ids` | 딸린 task 번호 |
| `spawn-time` | 작업을 만든 시각 |
| `ready-time` | 작업이 끝난 시각(끝나지 않았으면 없음) |

snapd 는 이 이력을 10분마다 정리합니다. 끝난 change 는 24시간이 지나면 지우고, 3일이 넘도록 끝나지 않은 작업은 중단하며, 끝난 change 가 500개를 넘으면 24시간이 안 됐어도 오래된 것부터 지웁니다[3][4]. 그래서 `state.json` 의 작업 이력은 대개 최근 하루 치만 남습니다.

### snap: 자동 스냅샷

앱 종류 snap 의 모든 리비전을 지우면서 `--purge` 를 주지 않으면, snapd 는 지우기 전에 데이터를 자동 스냅샷으로 남깁니다[6]. 보관 기간은 설정 `snapshots.automatic.retention` 에 Go 기간 문자열(예: `720h`)로 정하고, 값이 `no` 면 끄며, 설정이 없으면 31일입니다[5]. Ubuntu Core 처럼 classic 이 아닌 시스템에서는 설정이 없을 때 자동 스냅샷을 만들지 않습니다[5]. 스냅샷은 `/var/lib/snapd/snapshots/` 에 쌓입니다[1].

### flatpak: 배포 폴더

배포 폴더는 설치 폴더 아래 ref 경로(`app/앱ID/아키텍처/브랜치`, 런타임은 `runtime/...`)이고, 그 안에 커밋 번호 이름의 폴더와 지금 쓰는 커밋을 가리키는 심볼릭 링크 `active` 가 있습니다[11]. 커밋 폴더의 `deploy` 파일에는 배포 정보가 들어 있고, 그중 `timestamp` 는 OSTree 커밋의 시각입니다[11].

앱을 지우거나 새 커밋으로 바꾸면 이전 커밋 폴더를 `.removed` 로 옮기고, 그 안 `files` 에 표시 파일 `.removed`(제거) 또는 `.updated`(갱신)를 만듭니다[11]. 옮긴 폴더는 곧바로 지우지만, 실행 중인 앱이 `files/.ref` 에 잠금을 걸고 있으면 남겨 두었다가 다음 설치·갱신·제거 때 다시 정리합니다[11].

### flatpak: 저널 메시지

flatpak 은 설치 변경마다 `MESSAGE_ID=c7b39b1e006b464599465e105b361485` 인 저널 항목을 씁니다[10][11]. 필드는 다음과 같습니다[11].

| 필드 | 값 |
|---|---|
| `PRIORITY` | `5` |
| `SUBJECT` | polkit 주체(시스템 도우미를 거친 경우), 없으면 `(none)` |
| `CODE_FILE`, `CODE_LINE`, `CODE_FUNC` | 기록한 코드 위치 |
| `MESSAGE` | `설치이름: 설명` 모양. 설치 이름은 `user`, `system`, `system (ID)` |
| `FLATPAK_VERSION` | flatpak 판 |
| `INSTALLATION` | 설치 이름 |
| `OPERATION` | `pull`, `pull local`, `deploy install`, `deploy update`, `uninstall`, `add remote`, `modify remote`, `remove remote` |
| `REMOTE`, `REF`, `COMMIT`, `OLD_COMMIT`, `URL` | 원격 이름, ref, 새 커밋, 이전 커밋, 원격 주소(해당 없으면 빈 값) |

`MESSAGE` 설명은 작업에 따라 `Installed ... from ...`, `Updated ... from ...`, `Uninstalled ...`, `Added remote ... to ...` 같은 모양입니다[11]. libsystemd 없이 빌드한 flatpak 은 이 항목을 쓰지 않습니다[11]. `flatpak history` 명령은 이 저널 항목을 읽어 보여 주고, `user`·`tool` 열은 시스템 도우미가 root 로 작업했을 때 그 작업을 요청한 사용자와 도구까지 보여 줍니다[10].

## 증거로서 의미

**증명하는 것**

- `/var/lib/snapd/snaps` 의 이미지 파일: 지금 그 snap 의 그 리비전이 설치되어 있다는 사실. 파일이 여러 개면 이전 리비전도 남아 있다는 뜻입니다[1][2].
- `state.json` 의 change: 최근 하루 안팎에 어떤 설치·갱신·제거 작업이 언제 시작되고 끝났는지[3][4].
- 자동 스냅샷: 보관 기간 안에 지운 snap 앱과 그 앱의 데이터[5][6].
- flatpak 저널 항목: 저널이 남아 있는 기간의 설치·갱신·제거·원격 추가, 그 설치 위치(`user`·`system`), 커밋, 원격 주소[10][11].
- `~/snap/이름`, `~/.var/app/앱ID`: 그 사용자 홈에 해당 앱의 데이터 폴더가 생겼다는 사실. 그 계정으로 앱을 쓴 적이 있을 가능성이 있습니다.

**증명하지 못하는 것**

- 앱을 실제로 실행했는지, 얼마나 썼는지. 사용자 데이터 폴더 안 파일의 내용과 시각으로 따로 봅니다.
- 오래전 snap 설치 시각. `state.json` 이력은 하루 안팎이면 사라집니다[4]. 저널·syslog 의 snapd 기록[12]과 셸 기록으로 보강합니다.
- 누가 snap 을 설치했는지. `state.json` change 의 고정 필드에는 요청한 사용자 필드가 없습니다[3].
- 저널을 지웠거나 저널이 휘발성 저장(메모리)만 쓰던 시스템의 flatpak 이력. 이때는 저널 항목이 없습니다([systemd 저널](../../01-foundations/logging/systemd-journal/index.md)).

## 시각 해석

| 값 | 바뀌는 때 | 기준 |
|---|---|---|
| `state.json` 의 `spawn-time`, `ready-time` | 작업을 만들 때, 끝날 때 | Go `time.Time` 값을 JSON 문자열로 적은 것이라 실제 데이터에서 표기와 시간대 오프셋을 확인합니다[3] |
| snapd API 의 `install-date` | 설치 때 | 라이브에서만 얻습니다[14] |
| `.snap` 파일, `~/snap/이름`, 배포 폴더의 파일 시스템 시각 | 파일·폴더를 만들거나 바꿀 때 | 파일 시스템 시각([시각 값](../../01-foundations/value-decoding/time-values.md)) |
| `meta/snap.yaml` 의 mtime | `.snap` 이미지 안에 들어 있는 값 | 이미지(SquashFS) 안 파일의 시각이라 설치 시각과 다를 수 있습니다[12] |
| flatpak `deploy` 의 `timestamp` | OSTree 커밋을 만들 때 | 커밋 시각이라 설치 시각이 아닙니다[11] |
| flatpak 저널 항목 시각 | 작업을 기록할 때 | 저널 시각([systemd 저널](../../01-foundations/logging/systemd-journal/index.md)) |

## 함정과 한계

- snap 마운트 위치가 배포판마다 다릅니다(`/snap`, `/var/lib/snapd/snap`)[1]. 한쪽만 찾으면 snap 이 없다고 잘못 판단합니다.
- flatpak 은 시스템 설치와 사용자 설치가 따로 있고, `installations.d` 로 추가 설치 위치도 둘 수 있습니다[7][8]. 모든 사용자 홈의 `~/.local/share/flatpak` 까지 봐야 빠지지 않습니다.
- 도구가 보여 주는 snap 시각은 설치 시각이 아닐 수 있습니다. dissect.target `snap` 플러그인은 이미지 안 `meta/snap.yaml` 의 mtime 을 시각으로 내놓습니다[12].
- dissect.target `applications` 플러그인은 `.desktop` 파일의 생성 시각(`st_btime`)을 설치 시각으로 씁니다[13]. 파일 시스템이 생성 시각을 저장하지 않으면 값이 비고([ext4](../../01-foundations/filesystem/ext4/index.md)), 메뉴 항목을 다시 만들면 그때 시각으로 바뀝니다.
- `.removed` 안 폴더는 제거·갱신 때 그 앱이 실행 중이었을 때만 남습니다[11]. 폴더가 없다고 제거가 없었다는 뜻은 아닙니다.
- snap 을 `--purge` 로 지우면 자동 스냅샷이 없습니다[6]. 스냅샷이 없다는 사실만으로 앱이 없었다고 볼 수 없습니다.
- 메모리만으로는 설치 흔적이 적습니다. Ubuntu 20.04.3 에서 `snap install` 로 Discord·Slack 을 설치한 직후 메모리 덤프를 조사한 연구에서는 snap 설치를 가리키는 참조만 나왔습니다[17]. 디스크 쪽 경로를 먼저 봅니다([메모리 분석](../../03-techniques/analysis/memory-analysis.md)).

## 직접 분석해 보기

### 파일로 한 번

디스크 이미지를 읽기 전용으로 마운트한 뒤 snap 이미지 목록과 `state.json` 의 change 를 봅니다. 아래 경로의 `/mnt/evidence` 는 마운트 위치입니다.

```sh
ls -l --time-style=full-iso /mnt/evidence/var/lib/snapd/snaps/
jq -r '.changes[] | [.id, .kind, .status, ."spawn-time", ."ready-time", .summary] | @tsv' \
   /mnt/evidence/var/lib/snapd/state.json
```

change 항목 하나는 이런 모양입니다(필드 이름은 명세대로이고, 값은 만든 예시입니다).

```json
"1234": {
  "id": "1234",
  "kind": "install-snap",
  "summary": "Install \"example-app\" snap",
  "status": 4,
  "clean": true,
  "task-ids": ["5001", "5002"],
  "spawn-time": "2026-01-15T09:12:03.123456789+09:00",
  "ready-time": "2026-01-15T09:12:41.987654321+09:00"
}
```

`status` 4 는 Done 입니다[3]. `kind`·`summary` 문구와 시각 표기도 만든 예시라서, 실제 값은 분석 대상에서 확인합니다.

flatpak 이력은 이미지의 저널 폴더를 지정해 전용 메시지만 뽑습니다.

```sh
journalctl -D /mnt/evidence/var/log/journal -o verbose \
   MESSAGE_ID=c7b39b1e006b464599465e105b361485
```

항목 하나는 이런 모양입니다(필드는 코드대로이고, 값은 만든 예시입니다).

```text
    MESSAGE_ID=c7b39b1e006b464599465e105b361485
    PRIORITY=5
    SUBJECT=(none)
    MESSAGE=user: Installed app/org.example.Viewer/x86_64/stable from example-remote
    INSTALLATION=user
    OPERATION=deploy install
    REMOTE=example-remote
    REF=app/org.example.Viewer/x86_64/stable
    COMMIT=3f2a...(만든 예시)
    OLD_COMMIT=
    URL=
```

### 공개 도구로 한 번

- dissect.target: `snap` 플러그인이 `/var/lib/snapd/snaps/*.snap` 을 열어 이름·버전·경로를 내놓고, `applications` 플러그인이 snap·flatpak 메뉴 항목을 읽습니다[12][13].
- Velociraptor `Linux.Debian.Packages`: 라이브 시스템에서 `/run/snapd.socket` 의 `/v2/snaps` 를 불러 이름, 상태, 설치 크기, 게시자, 설치 시각(`install-date`), 버전, 채널을 받습니다[14].
- UAC: 라이브 수집에서 `snap list`, `snap list --all`, `flatpak list` 결과를 저장합니다[15].
- `flatpak history --columns=all`: 라이브 시스템에서 저널 항목을 표로 봅니다[10].

라이브 수집 순서는 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md)을 봅니다.

## 교차 검증

- [dpkg·apt 기록](dpkg-apt.md), [rpm·dnf·yum 기록](rpm-dnf.md): 같은 앱을 배포판 패키지로도 설치했는지 봅니다.
- [셸 명령 기록](../execution/shell-history/index.md): `snap install`, `flatpak install` 명령과 옵션(`--purge`, `--user` 등)을 찾습니다.
- [sudo·su 사용 기록](../logins/sudo-su.md): 누가 sudo 로 snap·flatpak 명령을 실행했는지 봅니다.
- [systemd 저널](../../01-foundations/logging/systemd-journal/index.md): snapd 서비스 기록과 flatpak 전용 메시지를 봅니다.
- [데스크톱 자동 실행](../persistence/xdg-autostart.md): snap·flatpak 앱이 로그인 때 자동으로 뜨게 등록됐는지 봅니다.
- [타임라인 만들기](../../03-techniques/analysis/timeline.md): 위 시각들을 한 줄로 늘어놓습니다.

## 실습

NIST CFReDS 등에서 받은 Ubuntu 데스크톱 공개 이미지로 다음 질문을 풀어 봅니다.

1. `/var/lib/snapd/snaps` 에 있는 snap 과 리비전을 모두 적고, 같은 이름에 리비전이 둘 이상인 snap 을 찾습니다.
2. `state.json` 에 남은 change 중 가장 오래된 `spawn-time` 은 언제이고, 이미지를 만든 시각과 얼마나 떨어져 있습니까?
3. 각 사용자 홈의 `~/snap` 아래 폴더 이름을 `/var/lib/snapd/snaps` 목록과 맞춰 보고, 이미지는 없는데 데이터 폴더만 남은 앱이 있는지 봅니다.
4. `/var/lib/snapd/snapshots` 에 자동 스냅샷이 있다면 어떤 앱의 것이고, 그 앱을 지운 흔적이 저널이나 셸 기록에 있습니까?
5. 저널에서 flatpak 전용 메시지를 뽑아 `OPERATION` 별로 세고, `INSTALLATION` 이 `user` 인 항목의 앱이 어느 사용자 홈에 있는지 찾습니다.

## 참고 문헌

1. canonical/snapd, `dirs/dirs.go`. https://github.com/canonical/snapd/blob/master/dirs/dirs.go
2. canonical/snapd, `snap/info.go`. https://github.com/canonical/snapd/blob/master/snap/info.go
3. canonical/snapd, `overlord/state/change.go`, `overlord/state/state.go`. https://github.com/canonical/snapd/tree/master/overlord/state
4. canonical/snapd, `overlord/overlord.go`. https://github.com/canonical/snapd/blob/master/overlord/overlord.go
5. canonical/snapd, `overlord/snapshotstate/snapshotstate.go`. https://github.com/canonical/snapd/blob/master/overlord/snapshotstate/snapshotstate.go
6. canonical/snapd, `overlord/snapstate/snapstate.go`. https://github.com/canonical/snapd/blob/master/overlord/snapstate/snapstate.go
7. flatpak/flatpak, `doc/flatpak.xml` (flatpak(1)). https://github.com/flatpak/flatpak/blob/main/doc/flatpak.xml
8. flatpak/flatpak, `doc/flatpak-installation.xml` (flatpak-installation(5)). https://github.com/flatpak/flatpak/blob/main/doc/flatpak-installation.xml
9. flatpak/flatpak, `doc/flatpak-run.xml` (flatpak-run(1)). https://github.com/flatpak/flatpak/blob/main/doc/flatpak-run.xml
10. flatpak/flatpak, `doc/flatpak-history.xml` (flatpak-history(1)). https://github.com/flatpak/flatpak/blob/main/doc/flatpak-history.xml
11. flatpak/flatpak, `common/flatpak-dir.c`. https://github.com/flatpak/flatpak/blob/main/common/flatpak-dir.c
12. fox-it/dissect.target, `plugins/os/unix/linux/debian/snap.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/debian/snap.py
13. fox-it/dissect.target, `plugins/os/unix/applications.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/applications.py
14. Velocidex/velociraptor, `artifacts/definitions/Linux/Debian/Packages.yaml`. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Debian/Packages.yaml
15. tclahr/uac, `artifacts/live_response/packages/snap.yaml`, `flatpak.yaml`. https://github.com/tclahr/uac/tree/main/artifacts/live_response/packages
16. tclahr/uac, `artifacts/files/applications/discord.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/files/applications/discord.yaml
17. Megan Davis, Bridget McInnes, Irfan Ahmed, "Forensic investigation of instant messaging services on linux OS: Discord and Slack as case studies", Forensic Science International: Digital Investigation 42 (2022) 301401 (DFRWS USA 2022). https://doi.org/10.1016/j.fsidi.2022.301401
