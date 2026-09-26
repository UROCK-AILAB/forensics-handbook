---
title: "Podman"
parent: "아티팩트 · 컨테이너와 가상화"
nav_order: 820
---

# Podman (Podman)

Podman 은 데몬 없이 사용자 계정마다 따로 컨테이너 저장소를 두고, 컨테이너 설정·상태를 SQLite 파일 `db.sql` 에, 이미지·레이어·컨테이너 목록을 JSON 파일에, 컨테이너 동작 이벤트를 기본으로 systemd 저널에 남깁니다.

## 무엇을 기록하나 · 왜 생기나

Podman 은 컨테이너 저장 라이브러리(containers-storage)로 이미지와 레이어를 풀어 두고, libpod 가 컨테이너 설정과 상태를 상태 데이터베이스에 적습니다[1][4]. 컨테이너 프로세스의 표준 출력은 conmon 이라는 감시 프로세스가 받아 로그 드라이버로 넘깁니다[9]. 컨테이너를 만들고, 시작하고, `exec` 로 들어가고, 지울 때마다 Podman 은 이벤트 (event) 를 하나씩 기록합니다[11][12].

조사에서 Podman 이 Docker 와 가장 다른 점은 두 가지입니다. 첫째, root 가 아닌 일반 사용자도 자기 홈 폴더에 저장소를 따로 두고 컨테이너를 돌립니다(rootless)[1][3]. 그래서 저장소 경로만 보고도 어느 계정의 컨테이너인지 가릴 수 있고, 반대로 `/var/lib/containers` 만 보면 사용자 계정의 컨테이너를 통째로 놓칩니다. 둘째, 이벤트가 기본으로 저널에 남습니다[2][11]. Docker 의 이벤트는 메모리에만 있어 오프라인 분석에 쓸 수 없지만([Docker 허브](docker/index.md)), Podman 은 컨테이너를 지운 뒤에도 저널 보존 기간 안이라면 "언제 만들고, 시작하고, exec 하고, 지웠나" 를 되짚을 수 있습니다.

## 위치와 버전별 차이

### 저장소 경로

| 항목 | root 로 실행 | 일반 사용자(rootless) |
|---|---|---|
| 저장소 루트 (graphroot) | `/var/lib/containers/storage`[1][3] | `$XDG_DATA_HOME/containers/storage`, 변수가 없으면 `~/.local/share/containers/storage`[1][3] |
| 실행 상태 (runroot) | `/run/containers/storage`[1] | `$XDG_RUNTIME_DIR/containers`, 변수가 없으면 `/tmp/storage-run-$UID/containers`[1] |
| 상태 DB | 저장소 루트의 `db.sql`[4][5] | 같음 |
| 이름 있는 볼륨 | 저장소 루트의 `volumes/`[2][5] | 같음 |
| 부팅마다 지워지는 임시 폴더 (tmp_dir) | `/run/libpod` 아래[2][3] | `$XDG_RUNTIME_DIR/libpod/tmp`[3] |

runroot 와 tmp_dir 은 tmpfs 에 두는 폴더라 전원이 꺼지면 사라집니다[1][2]. 디스크 이미지에서 볼 수 있는 것은 저장소 루트와 설정 파일입니다.

상태 DB 의 경로는 다음 규칙으로 정해집니다[4]. 기본은 저장소 루트의 `db.sql` 이고, `containers.conf` 에 `static_dir` 을 직접 적었으면 그 폴더의 `db.sql`, transient store 모드면 runroot 의 `db.sql` 입니다. `static_dir` 기본값은 저장소 루트 아래 `libpod` 폴더(root 는 `/var/lib/containers/storage/libpod`)이지만[2], 설정에 값을 비워 두어 Podman 이 이 값을 채운 경우에는 DB 가 `libpod` 폴더가 아니라 저장소 루트에 놓입니다[4][5]. 검체에서는 두 위치를 모두 찾아봅니다. `db.sql` 의 `DBConfig` 표에는 이 DB 를 만들 때 쓴 `StaticDir`, `TmpDir`, `GraphRoot`, `RunRoot`, `GraphDriver`, `VolumeDir` 가 적혀 있어[4], 설정을 바꾼 호스트에서 실제 경로를 되짚을 때 씁니다.

### 설정 파일

저장소 설정 `storage.conf` 는 `/usr/share/containers/storage.conf` → `/etc/containers/storage.conf` → `~/.config/containers/storage.conf` 순으로 찾고, 각 위치의 `storage.conf.d/` 와 `/usr/share/containers/`·`/etc/containers/` 아래 root·rootless 전용 `storage.rootful.conf.d/`·`storage.rootless.conf.d/` 도 읽습니다[1]. 엔진 설정 `containers.conf` 는 사용자의 `~/.config/containers/containers.conf`, 없으면 `/etc/containers/containers.conf`, 그것도 없으면 `/usr/share/containers/containers.conf` 를 읽고, `containers.conf.d`·`containers.rootful.conf.d`·`containers.rootless.conf.d/$UID` 같은 드롭인 폴더의 `.conf` 파일을 이름 순으로 덧씌웁니다[2].

Ubuntu 24.04 와 RHEL 9 에서 기본 저장소 드라이버, 로그 드라이버, 이벤트 기록 방식은 배포판 패키지가 `/usr/share/containers/` 에 넣는 두 설정 파일이 정하므로, 검체에서는 이 파일과 `/etc/containers/`·사용자 홈의 덮어쓴 값을 차례로 읽습니다. 실행 중인 호스트에서는 `podman info` 출력의 `LogDriver`·`EventLogger` 값으로 확인합니다[2][10].

### 옛 상태 DB

옛 판 Podman 은 상태를 BoltDB 파일에 적었습니다[5][13]. Podman 6.0 에서 BoltDB 백엔드를 없앴고, BoltDB 파일이 남아 있으면 SQLite 로 옮기라는 오류를 냅니다[5]. 옛 판에서 쓰던 호스트라면 BoltDB 형식의 상태 파일과 `db.sql` 이 함께 있을 수 있습니다.

## 구조

### 저장소 루트

드라이버가 `overlay` 일 때 저장소 루트는 다음과 같이 생겼습니다[7][8][13].

| 파일·폴더 | 내용 |
|---|---|
| `db.sql` | libpod 상태 DB (SQLite) |
| `overlay-images/images.json` | 이미지 목록 |
| `overlay-layers/layers.json` | 레이어 목록 |
| `overlay-containers/containers.json` | 저장소 쪽 컨테이너 목록 |
| `overlay-containers/컨테이너ID/userdata/` | 컨테이너별 OCI 런타임 설정 `config.json`, k8s-file 로그 `ctr.log` |
| `overlay/레이어ID/` | 레이어 내용. `diff/`, `link`, `lower`, `work/`, `merged/` |
| `overlay/l/` | 짧은 이름 → 레이어 `diff/` 심볼릭 링크 |
| `volumes/볼륨이름/` | 이름 있는 볼륨 |

`overlay/` 의 구조와 커널 규칙(whiteout·opaque·copy_up)은 Docker 의 overlay2 와 같으므로 [overlay 파일 시스템](docker/overlay2.md) 을 따라 읽습니다. 다른 점만 적으면, 이 드라이버는 아래 층을 500개까지 허용하고, 새 판은 `l/` 링크를 거치지 않고 레이어 ID 를 곧바로 적은 `lower-layers` 파일을 더 씁니다(옛 도구를 위해 `lower` 도 계속 씁니다)[8]. rootless 로 커널 overlay 를 붙일 때는 `userxattr` 마운트 옵션을 켭니다[8]. 이 옵션에서는 삭제 표시가 `trusted.overlay.*` 대신 `user.overlay.*` 확장 속성에 남습니다([overlay 파일 시스템](docker/overlay2.md)). 커널 overlay 를 쓸 수 없는 환경에서는 fuse-overlayfs 를 대신 씁니다[8].

### db.sql — 컨테이너 설정과 상태

SQLite 파일이고, 조사에 쓰는 표는 다음과 같습니다[4].

| 표 | 열 | 내용 |
|---|---|---|
| `ContainerConfig` | `ID`, `Name`, `PodID`, `JSON` | 컨테이너를 만들 때 정한 설정 |
| `ContainerState` | `ID`, `State`, `ExitCode`, `JSON` | 현재 상태 |
| `ContainerExecSession` | `ID`, `ContainerID` | exec 세션 |
| `ContainerVolume` | `ContainerID`, `VolumeName` | 컨테이너와 볼륨 연결 |
| `ContainerExitCode` | `ID`, `Timestamp`, `ExitCode` | 끝난 컨테이너의 종료 코드와 기록 시각 |
| `PodConfig`, `PodState` | `ID`, `Name`, `JSON` 등 | 파드 설정과 상태 |
| `VolumeConfig`, `VolumeState` | `Name`, `JSON` 등 | 볼륨 설정과 상태 |
| `DBConfig` | `GraphRoot`, `RunRoot`, `StaticDir` 등 | 이 DB 를 만들 때의 경로 |

내용은 대부분 `JSON` 열에 들어 있습니다. `ContainerConfig.JSON` 에서 자주 보는 키는 `name`, `rootfsImageName`(이미지 이름), `rootfsImageID`, `command`, `entrypoint`, `createdTime`, `user`, `labels`, `newPortMappings`(포트 연결), `namedVolumes`, `userVolumes`, `logDriver`, `logPath`, `idMappingsOptions`, 그리고 OCI 런타임 명세 전체를 담은 `spec`(환경 변수는 `spec.process.env`, 바인드 마운트는 `spec.mounts`)입니다[6]. `ContainerState.JSON` 에는 `state`, `startedTime`, `finishedTime`, `exitCode`, `oomKilled`, `pid`, `restartCount`, `stoppedByUser`, `newExecSessions`, `checkpointedTime`·`restoredTime` 이 있습니다[6]. 이 상태 값은 재부팅 때 다시 만드는 값이라[6], 재부팅 뒤 처음 Podman 을 실행하면 `ContainerState.JSON` 이 새로 쓰입니다[4].

`ContainerState.State` 의 숫자는 1 configured, 2 created, 3 running, 4 stopped, 5 paused, 6 exited, 7 removing, 8 stopping 입니다[13].

### images.json · layers.json · containers.json

세 파일 모두 레코드의 배열이고, 저장소 라이브러리의 구조체를 그대로 JSON 으로 적습니다[7].

| 파일 | 주요 키 |
|---|---|
| `images.json` | `id`, `digest`, `names`, `names-history`(예전에 붙었던 이름, 최신이 앞), `layer`(맨 위 레이어), `metadata`, `big-data-names`, `created` |
| `layers.json` | `id`, `names`, `parent`, `created`, `compressed-diff-digest`, `diff-digest`, `compressed-size`, `diff-size`, `uidmap`, `gidmap` |
| `containers.json` | `id`, `names`, `image`(이미지 ID), `layer`(컨테이너 쓰기 레이어), `metadata`, `created`, `uidmap`, `gidmap` |

`containers.json` 의 `layer` 값이 곧 `overlay/` 아래 컨테이너 쓰기 층의 폴더 이름입니다[13]. 컨테이너가 만들고 바꾼 파일은 `overlay/layer값/diff/` 에서 봅니다. transient store 모드에서는 목록의 일부가 runroot 의 `volatile-containers.json`·`volatile-layers.json` 에 들어가 재부팅하면 사라집니다[1][7].

### 컨테이너 로그

로그 드라이버는 `k8s-file`, `journald`, `none`, `passthrough`, `passthrough-tty` 중 하나이고, `json-file` 은 `k8s-file` 의 다른 이름입니다[2][10]. 기본값은 systemd 저널을 읽고 쓸 수 있으면 `journald`, 아니면 `k8s-file` 입니다[2]. `json-file` 을 골라도 파일 내용은 JSON 이 아니라 k8s-file 형식입니다[13].

k8s-file 로그는 `overlay-containers/컨테이너ID/userdata/ctr.log` 에 쌓입니다[13]. `containers.conf` 의 `log_path` 를 정했으면 그 아래 `컨테이너ID/ctr.log` 입니다[2]. 한 줄은 `시각 스트림 태그 내용` 꼴이고, 태그 `P`·`F` 의 뜻은 CRI 로그와 같습니다([containerd 와 Kubernetes 노드](containerd-kubernetes.md)). 시각은 conmon 이 줄을 받은 순간의 **현지 시각**에 `+09:00` 같은 오프셋을 붙이고 나노초 9자리까지 적습니다[9]. 아래는 만든 예시입니다.

```text
2026-03-02T10:15:07.482913004+09:00 stdout F 192.0.2.44 - - "GET /login HTTP/1.1" 200 512
```

`log_size_max` 는 기본 -1(제한 없음)이고, 양수로 정하면 그 크기에서 파일을 비우고 다시 엽니다[2]. conmon 의 회전 옵션을 켠 경우에는 `ctr.log.1`, `ctr.log.2` … 로 뒤로 밀립니다[9].

journald 드라이버를 쓰면 줄마다 `CONTAINER_ID_FULL`, `CONTAINER_ID`(12자리), `CONTAINER_NAME`, 태그를 준 경우 `CONTAINER_TAG` 가 붙고, `SYSLOG_IDENTIFIER` 는 태그 → 이름 → 짧은 ID 순으로 먼저 있는 값을 씁니다[9]. 우선순위는 stdout 이 6(info), stderr 가 3(err)이고, 메시지 앞에 systemd 우선순위 접두어가 있으면 그 값을 씁니다[9].

### 이벤트

`containers.conf` 의 `events_logger` 가 기록 방식을 정하고, 값은 `journald`(기본), `file`, `none` 입니다[2][11]. `none` 이면 이벤트가 아예 남지 않습니다[11].

journald 로 기록하면 저널 항목마다 다음 필드가 붙습니다[12].

| 필드 | 뜻 |
|---|---|
| `SYSLOG_IDENTIFIER` | 항상 `podman` |
| `PODMAN_EVENT` | 상태. 예: `create`, `init`, `start`, `exec`, `exec_died`, `died`, `stop`, `remove`, `pull`, `commit` |
| `PODMAN_TYPE` | `container`, `image`, `pod`, `volume`, `network`, `system` 등 |
| `PODMAN_TIME` | 이벤트 시각, RFC3339Nano |
| `PODMAN_NAME`, `PODMAN_ID`, `PODMAN_IMAGE` | 대상 이름·ID, 컨테이너의 이미지 |
| `PODMAN_EXIT_CODE`, `PODMAN_OOM_KILLED` | 종료 코드, 메모리 부족 종료 여부 |
| `PODMAN_POD_ID`, `PODMAN_LABELS`, `PODMAN_NETWORK_NAME` | 파드 ID, 컨테이너 라벨(JSON), 네트워크 이름 |
| `PODMAN_HEALTH_STATUS` | 상태 점검 결과 |
| `PODMAN_CONTAINER_INSPECT_DATA` | `events_container_create_inspect_data=true` 일 때만 create 이벤트에 붙는 `podman inspect` 와 같은 JSON[2][11] |

컨테이너 이벤트의 상태 목록은 `podman-events` 설명서에 있고, attach, checkpoint, cleanup, commit, create, died, exec, exec_died, exited, export, init, kill, mount, pause, prune, remove, rename, restart, restore, start, stop, sync, unmount, unpause, update 등이 있습니다[11]. 이미지 이벤트에는 pull, push, save, tag, untag, remove 등이 있습니다[11].

`file` 로 기록하면 기본으로 tmp 폴더의 `events/events.log` 에 한 줄에 JSON 하나씩 적고[3][12], `events_logfile_path` 로 위치를 바꿀 수 있습니다[2]. 기본 위치가 tmpfs 라 재부팅하면 사라집니다[2]. 파일이 `events_logfile_max_size`(기본 `1m`)에 이르면 앞쪽 절반을 버리고 뒤쪽만 남기며, 그 앞뒤에 상태가 `log-rotation` 인 이벤트를 적어 둡니다[12]. 설명서에는 "옛 파일을 지운다" 고만 되어 있지만[2], 코드는 이렇게 절반을 남깁니다[12].

## 증거로서 의미

### 증명하는 것

- 어느 계정이 컨테이너를 썼는지. rootless 저장소는 그 사용자의 홈 폴더 아래에 있습니다[1].
- 컨테이너의 이름·이미지·명령·환경 변수·포트·마운트, 만든 시각(`createdTime`)과 마지막으로 시작·종료한 시각, 종료 코드[6].
- 이벤트가 남아 있으면, 컨테이너를 만들고·시작하고·`exec` 로 들어가고·멈추고·지운 순서와 시각, 이미지를 받은(pull) 시각[11][12]. 컨테이너가 지워진 뒤에도 저널 항목은 남습니다.
- k8s-file 또는 journald 로그에 남은 컨테이너의 표준 출력 내용과 conmon 이 받은 시각.

### 증명하지 못하는 것

- 컨테이너 안에서 입력한 명령. 표준 출력으로 나오지 않는 한 로그에 없고, `exec` 이벤트는 들어간 사실과 시각만 알려 줍니다.
- 이벤트 기록이 `none` 이거나 저널이 순환·삭제된 뒤의 과거 동작.
- rootless 컨테이너 안의 root 가 호스트에서 어느 UID 였는지. 이 대응은 `containers.json`·`layers.json` 의 `uidmap`·`gidmap` 과 `ContainerConfig.JSON` 의 `idMappingsOptions` 로 따로 풀어야 합니다[6][7].
- 이미지를 받은 시각을 `images.json` 의 `created` 만으로 말하는 것. 아래 "시각 해석" 을 봅니다.

보고서에는 "사용자 alice 의 Podman 저장소에 컨테이너 web01 의 설정이 있고, 저널에 2026-03-02 10:14:58(+09:00) 에 이 컨테이너의 create 이벤트가 있다" 처럼 기록이 말하는 만큼만 씁니다(만든 예시).

## 시각 해석

| 값 | 형식 | 시간대 | 바뀌는 때 |
|---|---|---|---|
| k8s-file 줄 머리 | `YYYY-MM-DDThh:mm:ss.나노초9자리±hh:mm` | conmon 프로세스의 현지 시각 + 오프셋[9] | conmon 이 줄을 받을 때 |
| `PODMAN_TIME` | RFC3339Nano 문자열[12] | 문자열의 오프셋을 그대로 읽음 | 이벤트가 일어날 때 |
| 저널 항목 자체의 시각 | 저널 형식 | [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 참고 | 저널이 항목을 받을 때 |
| `containers.json`·`layers.json` 의 `created` | JSON 시각 문자열 | UTC[7] | 이 저장소에 레코드를 만들 때 |
| `images.json` 의 `created` | JSON 시각 문자열 | 경우에 따라 다름 | 아래 설명 |
| `ContainerConfig.JSON` 의 `createdTime` | JSON 시각 문자열 | 문자열의 오프셋으로 확인 | 컨테이너를 만들 때 한 번 |
| `ContainerState.JSON` 의 `startedTime`·`finishedTime` | JSON 시각 문자열 | 같음 | 시작·종료할 때마다 덮어씀[6] |
| `ContainerExitCode.Timestamp` | 정수, 유닉스 초[4] | UTC | 종료 코드를 적을 때 |

`images.json` 의 `created` 는 이미지를 저장소에 넣을 때 호출한 쪽이 생성 시각을 넘겨주면 그 값을, 넘겨주지 않으면 그때의 UTC 시각을 적습니다[7]. 그래서 이 값이 이미지를 빌드한 시각인지 이 호스트로 받은 시각인지는 레코드마다 다를 수 있고, 받은 시각으로 읽으면 안 됩니다[7][13]. 받은 시각은 저널의 이미지 `pull` 이벤트를 먼저 보고, 없으면 그 이미지를 이루는 레이어의 `layers.json` `created`(저장소에 레이어를 만든 UTC 시각[7])를 후보로 씁니다.

Go 의 빈 시각 값 `0001-01-01T00:00:00Z` 가 `finishedTime` 에 있으면 아직 한 번도 끝나지 않은 컨테이너이고, 날짜로 읽지 않습니다. 시각 값 일반은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 을 봅니다.

## 함정과 한계

- **rootless 저장소를 빠뜨리기 쉽습니다.** 사용자마다 `~/.local/share/containers/storage` 가 따로 있습니다[1]. dissect.target 도 시스템 경로 `/var/lib/containers` 와 모든 사용자 홈의 `.local/share/containers` 를 함께 훑습니다[13]. 라이브 수집에서 root 로 `podman` 명령을 실행하면 root 의 저장소(`/var/lib/containers/storage`)만 보므로[3], UAC 의 `podman container ls --all` 같은 명령 결과[15]에도 사용자 컨테이너가 빠질 수 있습니다. 사용자 계정마다 저장소 폴더를 따로 모읍니다.
- **이벤트 조회도 사용자별입니다.** `podman events` 는 저널에서 `SYSLOG_IDENTIFIER=podman` 이면서 `_UID` 가 현재 사용자인 항목만 읽습니다[12]. 검체에서는 `_UID` 로 거르지 말고 `SYSLOG_IDENTIFIER=podman` 전체를 본 뒤 `_UID` 로 계정을 가립니다.
- **지운 컨테이너는 DB 와 폴더에서 사라집니다.** 컨테이너를 지우면 `IDNamespace`·`ContainerConfig`·`ContainerState`·`ContainerDependency`·`ContainerVolume`·`ContainerExecSession` 의 행을 지웁니다[4]. `ContainerExitCode` 행은 컨테이너가 지워진 뒤에도 남아 있다가, 기록 시각에서 5분이 지난 뒤 정리 작업이 돌 때 지워지고[4], 재부팅 뒤 상태를 새로 만들 때 `ContainerExitCode`·`ContainerExecSession` 표를 통째로 비웁니다[4]. 지운 행은 SQLite 빈 페이지에 남을 수 있으므로 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html) 의 복구 방법을 씁니다.
- **k8s-file 로그는 기본값이면 컨테이너와 함께 지워집니다.** `log_path` 를 비워 두면 로그가 컨테이너 저장소에 있다가 컨테이너를 지울 때 같이 지워집니다[2]. journald 드라이버라면 저널에 남습니다.
- **transient store 모드면 재부팅 뒤 기록이 없습니다.** 컨테이너 메타데이터와 `db.sql` 이 runroot 에만 있기 때문입니다[1][4]. 볼륨 데이터는 디스크에 남지만 DB 기록이 없어 `podman volume ls` 에 보이지 않습니다[3].
- **dissect.target 의 로그 정규식은 `+hh:mm` 오프셋만 받습니다.** conmon 은 UTC 보다 늦은 시간대에서 `-hh:mm` 을 씁니다[9]. dissect.target 의 `podman.logs` 는 `\+\d{2}\:\d{2}` 만 받으므로[13], 미주처럼 음수 오프셋을 쓰는 호스트의 줄은 경고만 내고 빠질 수 있습니다. 이런 검체는 로그 파일을 직접 읽습니다.
- **dissect.target 의 `podman.logs` 는 기본 위치의 k8s-file 만 읽습니다.** `overlay-containers/*/userdata/ctr.log*` 만 훑고 `log_path` 로 옮긴 로그는 읽지 않습니다[13]. 기본 로그 드라이버인 journald 로그는 저널에서 따로 봅니다.

## 직접 분석해 보기

### 헥스로 한 번 — k8s-file 한 줄

conmon 형식으로 만든 예시입니다[9]. `hello` 한 줄을 stdout 으로 받았을 때 `ctr.log` 에는 다음 51바이트가 적힙니다.

```text
00000000  32 30 32 36 2d 30 33 2d  30 32 54 31 30 3a 31 35  |2026-03-02T10:15|
00000010  3a 30 37 2e 34 38 32 39  31 33 30 30 34 2b 30 39  |:07.482913004+09|
00000020  3a 30 30 20 73 74 64 6f  75 74 20 46 20 68 65 6c  |:00 stdout F hel|
00000030  6c 6f 0a                                          |lo.|
```

| 오프셋 | 바이트 | 뜻 |
|---|---|---|
| 0x00 | `32 30 … 30 34` (29바이트) | 현지 시각, 나노초 9자리 |
| 0x1D | `2b 30 39 3a 30 30` | 오프셋 `+09:00`. 서쪽 시간대면 첫 바이트가 `2d`(`-`) |
| 0x23 | `20 73 74 64 6f 75 74 20` | 스트림 `stdout` |
| 0x2B | `46 20` | 태그 `F`. 줄이 나뉘었으면 `P` |
| 0x2D | `68 65 6c 6c 6f 0a` | 내용과 줄 바꿈 |

머리 시각에서 오프셋을 빼면 UTC 로 2026-03-02 01:15:07.482913004 이고, 유닉스 초로는 1772414107 입니다. 같은 컨테이너의 `ContainerExitCode.Timestamp` 나 저널 시각과 맞춰 볼 때 이렇게 UTC 로 바꿔 놓습니다.

### 공개 도구로 한 번

| 도구 | 쓰는 때 | 하는 일 |
|---|---|---|
| dissect.target | 오프라인 | `podman.images` 가 `images.json` 을, `podman.containers` 가 `db.sql` 의 `ContainerConfig`·`ContainerState` JSON 을 합쳐 ID·이미지·명령·생성·시작·종료 시각·포트·바인드 마운트·환경 변수를 뽑고, `podman.logs` 가 k8s-file 로그를 읽습니다[13]. `db.sql` 이 없는 옛 저장소는 `containers.json` 과 `userdata/config.json` 으로 대신합니다[13] |
| container-explorer | 오프라인 | `db.sql` 과 저장소 설정을 직접 읽고, overlay 층을 겹쳐 붙이거나 이미지 대비 바뀐 파일을 찾습니다[14] |
| UAC | 라이브 | `podman container ls --all --size`, `image ls --all`, `info`, `version`, 컨테이너마다 `logs`·`inspect`·`top`, 네트워크·볼륨 `inspect` 출력을 모읍니다[15] |
| sqlite3 | 오프라인 | `SELECT ID, Name, json_extract(JSON,'$.createdTime') FROM ContainerConfig;` 처럼 JSON 열을 풀어 읽습니다 |
| journalctl | 오프라인·라이브 | `journalctl --directory=저널폴더 SYSLOG_IDENTIFIER=podman -o json` 으로 이벤트 필드를 그대로 뽑습니다 |

수집 순서는 [컨테이너 수집](../../03-techniques/acquisition/container-acquisition.md) 을 따릅니다.

## 교차 검증

- [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) — `SYSLOG_IDENTIFIER=podman` 이벤트, journald 드라이버의 `CONTAINER_*` 필드, `_UID`
- [셸 명령 기록](../execution/shell-history/index.md) — `podman run`·`podman exec`·`podman cp` 를 입력한 계정
- [감사 로그의 실행 기록](../execution/auditd-execve.md) — `podman`·`conmon` 실행 시각과 계정
- [overlay 파일 시스템](docker/overlay2.md) — 컨테이너 쓰기 층 `diff/` 에서 바뀐 파일과 삭제 표시
- [권한·확장 속성·ACL·Capabilities](../../01-foundations/filesystem/permissions-xattr.md) — rootless 삭제 표시가 든 `user.overlay.*` 확장 속성
- [Docker](docker/index.md) — 같은 호스트에 Docker 도 있다면 저장소가 따로라 둘 다 봅니다

## 실습

공개 검체 대신 실험용 가상 머신에 Podman 을 설치해 따라 합니다.

1. 일반 사용자로 컨테이너 하나를 만들어 돌리고 멈춘 뒤, 그 사용자의 `db.sql` 에서 `createdTime`·`startedTime`·`finishedTime` 을, 저널에서 같은 컨테이너의 `create`·`start`·`died` 이벤트를 뽑아 나란히 놓으면 어떤 순서가 나오나?
2. root 로 `podman ps --all` 을 실행하면 1번 컨테이너가 보이나? 보이지 않는다면 어디를 봐야 하나?
3. 컨테이너에 `podman exec` 로 들어가 명령 하나를 친 뒤 지우면, `db.sql`·`overlay-containers/`·저널 가운데 어디에 무엇이 남나? 5분 뒤와 재부팅 뒤에는 무엇이 달라지나?
4. `--log-driver k8s-file` 로 만든 컨테이너의 `ctr.log` 를 헥스로 열어 오프셋을 확인하고, 시간대를 `America/New_York` 으로 바꿔 다시 돌리면 줄 머리가 어떻게 달라지나?

## 참고 문헌

1. containers/container-libs, `storage/docs/containers-storage.conf.5.md`. https://github.com/containers/container-libs/blob/main/storage/docs/containers-storage.conf.5.md
2. containers/container-libs, `common/docs/containers.conf.5.md`. https://github.com/containers/container-libs/blob/main/common/docs/containers.conf.5.md
3. containers/podman, `docs/source/markdown/podman.1.md`. https://github.com/containers/podman/blob/main/docs/source/markdown/podman.1.md
4. containers/podman, `libpod/sqlite_state.go`, `libpod/sqlite_state_internal.go`. https://github.com/containers/podman/tree/main/libpod
5. containers/podman, `libpod/runtime.go`. https://github.com/containers/podman/blob/main/libpod/runtime.go
6. containers/podman, `libpod/container.go`, `libpod/container_config.go`. https://github.com/containers/podman/blob/main/libpod/container.go , https://github.com/containers/podman/blob/main/libpod/container_config.go
7. containers/container-libs, `storage/images.go`, `storage/layers.go`, `storage/containers.go`. https://github.com/containers/container-libs/tree/main/storage
8. containers/container-libs, `storage/drivers/overlay/overlay.go`. https://github.com/containers/container-libs/blob/main/storage/drivers/overlay/overlay.go
9. containers/conmon, `src/ctr_logging.c`. https://github.com/containers/conmon/blob/main/src/ctr_logging.c
10. containers/podman, `docs/source/markdown/options/log-driver.md`. https://github.com/containers/podman/blob/main/docs/source/markdown/options/log-driver.md
11. containers/podman, `docs/source/markdown/podman-events.1.md`. https://github.com/containers/podman/blob/main/docs/source/markdown/podman-events.1.md
12. containers/podman, `libpod/events/journal_linux.go`, `libpod/events/logfile.go`, `libpod/events/config.go`. https://github.com/containers/podman/tree/main/libpod/events
13. fox-it/dissect.target, `dissect/target/plugins/apps/container/podman.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/container/podman.py
14. google/container-explorer, `README.md`. https://github.com/google/container-explorer/blob/main/README.md
15. tclahr/uac, `artifacts/live_response/containers/podman.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/live_response/containers/podman.yaml
