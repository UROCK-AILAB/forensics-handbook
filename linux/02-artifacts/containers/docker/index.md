---
title: "Docker"
parent: "아티팩트 · 컨테이너와 가상화"
nav_order: 770
has_children: true
has_toc: false
---

# Docker (Docker)

Docker 데몬(dockerd)은 이미지·컨테이너 설정·표준 출력 로그·볼륨을 데이터 루트 폴더 하나에 모아 두고, Docker Engine 29.0 부터 새로 설치한 호스트에서는 이미지와 컨테이너 파일 시스템을 containerd 쪽 폴더에 따로 둡니다.

## 왜 중요한가

컨테이너 안에서 벌어진 일은 호스트의 일반 로그에 잘 남지 않습니다. 컨테이너가 표준 출력으로 내보낸 내용, 컨테이너를 만들 때 준 명령·환경 변수·마운트, 컨테이너가 새로 만들거나 바꾼 파일은 모두 Docker 데이터 루트 아래 파일로 남아 있어서, 호스트 디스크 이미지만 있어도 데몬 없이 읽을 수 있습니다. 웹 애플리케이션을 컨테이너로 돌리는 서버라면 침입 흔적의 상당 부분이 여기에 있습니다.

반대로 Docker 에는 "누가 어떤 명령을 쳤는가" 를 디스크에 남기는 기록이 없습니다. `docker events` 로 보는 데몬 이벤트는 메모리에 최근 256개만 보관하고 파일로 쓰지 않습니다[8]. 그래서 오프라인 분석 대상에서는 컨테이너를 만들고 지운 순서를 이벤트로 거슬러 올라가 확인할 수 없고, 설정 파일의 시각 필드와 파일 시스템 시각, 저널로 맞춰야 합니다.

### 증명하는 것과 증명하지 못하는 것

데이터 루트가 있으면 이 호스트에 Docker 가 설치되어 쓰였다는 것을, 그 안의 파일로 어떤 이미지가 저장소에 있었고 어떤 컨테이너를 어떤 설정으로 만들었는지를 말할 수 있습니다. 컨테이너를 지우면(`docker rm`) 데몬이 컨테이너의 쓰기 레이어를 풀고 설정·로그가 든 컨테이너 폴더를 통째로 지우므로[10], 지운 컨테이너는 이 목록에 나오지 않습니다.

Docker 파일만으로는 다음을 말할 수 없습니다.

- 누가 `docker` 명령을 실행했는지. 기본 소켓 `/var/run/docker.sock` 은 root 권한이나 docker 그룹 구성원이면 쓸 수 있고[18], 이벤트 기록은 메모리에만 있습니다[8]. 명령한 계정은 [셸 명령 기록](../../execution/shell-history/index.md) 과 [감사 로그의 실행 기록](../../execution/auditd-execve.md) 에서 찾습니다.
- 컨테이너 안에서 누가 무엇을 입력했는지. 표준 출력에 찍히지 않은 명령은 컨테이너 로그에 없습니다([컨테이너 설정과 로그](container-logs.md)).
- 이미지를 언제 받았는지. 이미지 설정의 `created` 는 빌드 시각입니다([이미지와 레이어](images-layers.md)).

## 한눈에 보기

| 위치 | 알려 주는 것 | 자세히 |
|---|---|---|
| `/var/lib/docker/image/overlay2/` (`repositories.json`, `imagedb/`, `layerdb/`) | 저장소에 있는 이미지의 이름·태그·레이어 관계 | [이미지와 레이어](images-layers.md) |
| `/var/lib/docker/containers/컨테이너ID/` | 컨테이너 설정·상태(`config.v2.json`, `hostconfig.json`)와 표준 출력 로그 | [컨테이너 설정과 로그](container-logs.md) |
| `/var/lib/docker/overlay2/` | 이미지 레이어 내용과 컨테이너가 바꾼 파일 | [overlay 파일 시스템](overlay2.md) |
| `/var/lib/containerd/` | containerd 이미지 저장소를 쓰는 경우의 이미지 내용과 컨테이너 스냅숏 | [containerd 와 Kubernetes 노드](../containerd-kubernetes.md) |
| `/var/lib/docker/volumes/볼륨이름/_data` | 볼륨에 쓴 실제 데이터. 옵션은 같은 폴더의 `opts.json`, 볼륨 목록은 BoltDB 파일 `volumes/metadata.db`[11] | 이 페이지 |
| `/etc/docker/daemon.json` | 데이터 루트(`data-root`), 기본 로그 드라이버, 저장 방식 같은 데몬 설정[3] | 이 페이지 |
| 저널의 `docker.service` 단위 | 데몬 시작·중지·오류[7] | [systemd 저널](../../../01-foundations/logging/systemd-journal/index.md) |
| `~/.docker/config.json` | 레지스트리 로그인 흔적. 자격 증명 저장소를 설정하지 않았으면 인증 정보가 base64 로 인코딩된 채 이 파일에 들어간다[9] | 이 페이지 |

### 데이터 루트와 설정 파일 위치

| 설치 방식 | 데이터 루트 | 설정 파일 |
|---|---|---|
| 일반(root 로 도는 데몬) | `/var/lib/docker`. 실행 상태는 `/var/run/docker`, PID 파일은 `/var/run/docker.pid`[1] | `/etc/docker/daemon.json`[3] |
| rootless 모드 | `$XDG_DATA_HOME/docker`(보통 `~/.local/share/docker`), 실행 상태는 `$XDG_RUNTIME_DIR/docker`[1] | `~/.config/docker/daemon.json`, `XDG_CONFIG_HOME` 이 있으면 `$XDG_CONFIG_HOME/docker/daemon.json`[3] |
| snap 패키지 | `/var/snap/docker/common/var-lib-docker`[12] | `/var/snap/docker/current/config/daemon.json`[12] |

`daemon.json` 의 `data-root` 키로 데이터 루트를 옮길 수 있고[2][3], `dockerd --config-file` 로 설정 파일 자체를 다른 곳에 둘 수도 있습니다[3]. 그래서 분석 대상에서는 설정 파일과 `docker.service` 단위 파일의 실행 줄을 먼저 읽고 실제 데이터 루트를 정합니다. snap 설치 흔적은 [snap·flatpak](../../packages/snap-flatpak.md) 에서 함께 봅니다.

데몬 로그는 저널의 `docker.service` 단위에 있고, 배포판에 따라 `/var/log/syslog` 나 `/var/log/messages` 에도 있습니다[7]. 어느 파일로 가는지는 [syslog 형식과 rsyslog](../../../01-foundations/logging/syslog-rsyslog.md) 에 배포판별로 나와 있습니다. 로그 수준 기본값은 `info` 이고, `daemon.json` 에 `"debug": true` 가 있으면 디버그 줄까지 남습니다[7].

### 이미지 저장 방식 두 가지

Docker 는 이미지와 컨테이너 파일 시스템을 두 방식 가운데 하나로 저장하고, 어느 방식이냐에 따라 볼 폴더가 달라집니다.

| 방식 | 쓰는 호스트 | 이미지·컨테이너 파일 시스템 위치 |
|---|---|---|
| 그래프 드라이버 overlay2 (graph driver) | 29.0 이전 판, 그리고 옛 판에서 올린 호스트[3][4] | 모두 `/var/lib/docker` 아래[3] |
| containerd 이미지 저장소 (containerd image store) | 2025-11-10 에 나온 29.0 부터 새로 설치한 호스트의 기본값[5] | 이미지 내용과 컨테이너 스냅숏은 `/var/lib/containerd`, 볼륨·설정 같은 나머지는 `/var/lib/docker`[3] |

`userns-remap` 을 켠 데몬에서는 containerd 이미지 저장소를 쓰지 않습니다[4][5]. 데몬 코드는 기본으로 containerd 저장소를 고르지만, 데이터 루트에 예전 그래프 드라이버의 흔적이 있으면 그래프 드라이버를 계속 쓰고, `daemon.json` 의 `"features": {"containerd-snapshotter": true}`(또는 `false`), `storage-driver` 설정, `DOCKER_DRIVER` 환경 변수가 있으면 그 설정을 따릅니다[6]. 실행 중인 호스트에서는 `docker info` 의 드라이버 상태(DriverStatus)에 `driver-type` 이 `io.containerd.snapshotter.v1` 으로 나오면 containerd 저장소입니다[4]. 오프라인 분석 대상에서는 `/var/lib/docker/image/overlay2/` 와 `/var/lib/containerd/` 가운데 어느 쪽에 내용이 차 있는지로 판별합니다.

containerd 저장소로 바꾸면 기존 overlay2 이미지와 컨테이너는 디스크에 그대로 남고 목록에서만 숨겨지며, 다시 overlay2 로 돌리면 보입니다[4]. 따라서 한 호스트에 두 방식의 흔적이 함께 있을 수 있고, `docker` 명령으로 본 목록이 디스크에 있는 전부가 아닐 수 있습니다. containerd 안에서 Docker 가 쓰는 네임스페이스 이름은 `moby` 이고, 플러그인용은 `plugins.moby` 입니다[2].

### 함정

- 컨테이너를 지우면 컨테이너 폴더(설정·json-file 로그 포함)가 함께 사라지고, 볼륨은 `docker rm -v` 처럼 볼륨 삭제를 요청했을 때만 지웁니다[10]. 그래서 컨테이너는 없어도 그 컨테이너가 쓰던 볼륨 데이터는 `volumes/` 에 남아 있을 수 있습니다.
- 공개 도구마다 읽는 범위가 다릅니다. dissect.target 의 docker 플러그인은 기본 경로 `/var/lib/docker`, snap 경로, `/etc/docker/daemon.json`·snap 설정·사용자 홈 `.docker/daemon.json` 의 `data-root` 를 찾아 이미지 목록을 `image/overlay2/repositories.json` 에서만 읽습니다[12]. 그래서 containerd 이미지 저장소를 쓰는 호스트에서는 이미지 목록이 비어 나올 가능성이 있고, rootless 데이터 루트(`~/.local/share/docker`)는 기본 경로 목록에 없습니다[12]. containerd 저장소는 `meta.db` 를 직접 읽는 container-explorer 로 봅니다[17].
- 라이브 수집 도구가 데이터 루트를 파일로 모으지 않을 수 있습니다. UAC 는 Docker 를 `docker container ls --all --size`, `docker inspect`, `docker container logs`, `docker diff` 같은 명령 출력으로만 모읍니다[14]. 지운 컨테이너의 흔적이나 `merged` 가 풀린 레이어를 보려면 [컨테이너 수집](../../../03-techniques/acquisition/container-acquisition.md) 에 따라 폴더 자체를 따로 확보합니다.

### 공개 도구

| 도구 | 쓰는 때 | 하는 일 |
|---|---|---|
| dissect.target | 오프라인 | `docker.images`, `docker.containers`, `docker.logs` 로 이미지·컨테이너·로그를 레코드로 뽑는다[12] |
| docker-explorer (`de.py`) | 오프라인 | 디스크 이미지의 Docker 폴더를 읽어 컨테이너 목록을 보고 컨테이너 파일 시스템을 마운트한다[16] |
| container-explorer (`ce`) | 오프라인 | containerd(`meta.db`)·Docker·Podman 저장소를 데몬 없이 읽는다[17] |
| ForensicArtifacts | 수집 정의 | `DockerContainerConfig`(`/var/lib/docker/containers/*/config.v2.json`, `config.json`), `DockerRootDirectory`(`/var/lib/docker/*`), `GKEDockerContainerLogs`(`/var/lib/docker/containers/*/*-json.log*`)[13] |
| UAC | 라이브 | `docker` 명령 출력(목록·inspect·logs·diff·top·stats·network·volume)을 모은다[14] |
| Velociraptor | 라이브 | `Linux.Applications.Docker.Info` 가 소켓 `/var/run/docker.sock` 으로 데몬 정보(컨테이너 수·이미지 수·드라이버·로그 드라이버)를 읽는다. 보통 root 권한이 필요하다[15] |

## 읽는 순서

1. [이미지와 레이어 (Images·Layers)](images-layers.md) — `repositories.json`, `imagedb`, `layerdb` 로 이미지 이름·태그·레이어를 잇고, 이미지 설정의 시각과 빌드 명령을 해석합니다.
2. [컨테이너 설정과 로그 (Container Config·Logs)](container-logs.md) — `config.v2.json` 의 생성·시작·종료 시각과 실행 명령, json-file·local·journald 로그 드라이버의 형식과 회전을 다룹니다.
3. [overlay 파일 시스템 (overlay2)](overlay2.md) — 레이어 폴더와 컨테이너 쓰기 층을 찾아 컨테이너가 만들고 바꾸고 지운 파일을 가려냅니다.

## 함께 볼 페이지

- [containerd 와 Kubernetes 노드](../containerd-kubernetes.md) — containerd 이미지 저장소의 폴더 구조와 `meta.db`
- [Podman](../podman.md) — 데몬 없이 도는 컨테이너 엔진의 흔적
- [컨테이너 수집](../../../03-techniques/acquisition/container-acquisition.md) — 실행 중인 호스트에서 컨테이너 흔적을 확보하는 순서
- [systemd 저널](../../../01-foundations/logging/systemd-journal/index.md) — `docker.service` 단위와 journald 로그 드라이버의 `CONTAINER_*` 필드
- [셸 명령 기록](../../execution/shell-history/index.md) — `docker run`·`docker exec`·`docker cp` 를 입력한 계정 찾기

## 참고 문헌

1. moby/moby, `daemon/config/config_linux.go`. https://github.com/moby/moby/blob/master/daemon/config/config_linux.go
2. moby/moby, `daemon/config/config.go`. https://github.com/moby/moby/blob/master/daemon/config/config.go
3. Docker Docs, "Docker daemon configuration overview" (`content/manuals/engine/daemon/_index.md`). https://github.com/docker/docs/blob/main/content/manuals/engine/daemon/_index.md
4. Docker Docs, "containerd image store with Docker Engine" (`content/manuals/engine/storage/containerd.md`). https://github.com/docker/docs/blob/main/content/manuals/engine/storage/containerd.md
5. Docker Docs, "Docker Engine version 29 release notes" (`content/manuals/engine/release-notes/29.md`). https://github.com/docker/docs/blob/main/content/manuals/engine/release-notes/29.md
6. moby/moby, `daemon/image_store_choice.go`. https://github.com/moby/moby/blob/master/daemon/image_store_choice.go
7. Docker Docs, "Read the daemon logs" (`content/manuals/engine/daemon/logs.md`). https://github.com/docker/docs/blob/main/content/manuals/engine/daemon/logs.md
8. moby/moby, `daemon/events/events.go`. https://github.com/moby/moby/blob/master/daemon/events/events.go
9. docker/cli, `docs/reference/commandline/login.md`. https://github.com/docker/cli/blob/master/docs/reference/commandline/login.md
10. moby/moby, `daemon/delete.go`. https://github.com/moby/moby/blob/master/daemon/delete.go
11. moby/moby, `daemon/volume/local/local.go`, `daemon/volume/service/store.go`. https://github.com/moby/moby/tree/master/daemon/volume
12. fox-it/dissect.target, `dissect/target/plugins/apps/container/docker.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/container/docker.py
13. ForensicArtifacts/artifacts, `artifacts/data/docker.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/docker.yaml
14. tclahr/uac, `artifacts/live_response/containers/docker.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/live_response/containers/docker.yaml
15. Velocidex/velociraptor, `artifacts/definitions/Linux/Applications/Docker/Info.yaml`. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Applications/Docker/Info.yaml
16. google/docker-explorer, `README.md`. https://github.com/google/docker-explorer
17. google/container-explorer, `README.md`. https://github.com/google/container-explorer/blob/main/README.md
18. docker/cli, `docs/reference/dockerd.md` (docker/docs 저장소 사본). https://github.com/docker/docs/blob/main/_vendor/github.com/docker/cli/docs/reference/dockerd.md
