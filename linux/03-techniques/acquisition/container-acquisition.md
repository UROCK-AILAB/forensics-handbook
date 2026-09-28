---
title: "컨테이너 수집"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 950
---

# 컨테이너 수집 (Container Acquisition)

컨테이너는 런타임이 실행 중일 때 런타임 명령으로 상태·로그·변경 목록을 먼저 뜨고, 디스크에서는 데이터 루트와 쓰기층(upperdir)을 통째로 확보하는 두 가지 방법으로 수집합니다.

## 언제 쓰나

Docker·Podman·LXC 같은 컨테이너 런타임이 돌던 호스트를 조사할 때 씁니다. 컨테이너 안의 파일 변경은 호스트 파일 시스템의 한 디렉터리에 모여 있고, 컨테이너가 표준 출력으로 낸 로그는 런타임이 따로 보관합니다. 그래서 호스트 디스크 이미지만 떠도 대부분이 남지만, 컨테이너 목록·실행 중 프로세스·네트워크 같은 상태는 런타임에 물어봐야 정확하게 얻습니다.

컨테이너를 지우거나 다시 만들면 쓰기층과 설정 파일이 함께 사라질 가능성이 있으므로, 운영 담당자가 컨테이너를 재배포하기 전에 수집을 끝내는 편이 좋습니다. 호스트 전체의 휘발성 정보를 뜨는 순서는 [조사 절차](investigation-process.md)와 [라이브 응답 수집](live-response.md)을 따르고, 이 페이지는 컨테이너에만 해당하는 부분을 다룹니다.

## 절차

1. **런타임과 데이터 위치를 확인합니다.** 어떤 런타임이 있는지(docker, podman, lxc, containerd)부터 봅니다. Docker 는 기본 데이터 루트가 `/var/lib/docker` 이고, snap 패키지로 설치했으면 `/var/snap/docker/common/var-lib-docker` 입니다[6]. `/etc/docker/daemon.json`, `/var/snap/docker/current/config/daemon.json`, 사용자 홈의 `~/.docker/daemon.json` 에 `data-root` 값이 있으면 그 경로가 실제 데이터 루트입니다[6]. Podman 은 시스템 쪽이 `/var/lib/containers` 이고, root 가 아닌 사용자가 돌린 컨테이너(rootless)는 사용자마다 `~/.local/share/containers` 아래에 있습니다[7].

2. **런타임 상태를 텍스트로 뜹니다.** 런타임이 동작할 때만 되는 단계라서 디스크 이미징보다 먼저 합니다. UAC 가 Docker 에서 모으는 명령은 아래 표와 같고, Podman 도 `podman` 으로 이름을 바꾼 거의 같은 목록을 씁니다(`podman stats` 에는 `--no-trunc` 가 없습니다)[1]. 결과는 UAC 출력의 `/live_response/containers` 폴더에 들어갑니다[1].

   | 명령 | 알려 주는 것 |
   |---|---|
   | `docker container ls --all --size` | 멈춘 것까지 모든 컨테이너, 쓰기층 크기 |
   | `docker image ls --all` | 이미지 목록 |
   | `docker info`, `docker version` | 저장 드라이버·로그 드라이버·데이터 루트·버전 |
   | `docker inspect ID` | 컨테이너 하나의 설정·상태 상세 |
   | `docker container logs ID` | 컨테이너가 표준 출력·표준 오류로 낸 로그 |
   | `docker top ID` | 컨테이너 안에서 도는 프로세스 |
   | `docker diff ID` | 컨테이너를 만든 뒤 바뀐 파일 목록 |
   | `docker stats --no-stream --no-trunc ID` | 자원 사용량 한 번 |
   | `docker network ls`, `docker network inspect` | 네트워크 목록과 상세 정보 |
   | `docker volume ls`, `docker volume inspect` | 볼륨 목록과 상세 정보 |

   containerd 만 있는 호스트에서는 UAC 가 `containerd config dump` 로 설정을 뜨고[1], LXC·LXD 에서는 `lxc list --all-projects --format compact`, 인스턴스마다 `lxc info 이름 --show-log`(마지막 로그 100줄 포함)와 `lxc config show`, 그리고 `lxc-ls -f`, `lxc-info -i -p -S -s` 를 씁니다[1]. Velociraptor 의 `Linux.Applications.Docker.Info` 는 `/var/run/docker.sock` 의 `/info` 에 물어 컨테이너 수(실행·일시 정지·정지), 이미지 수, `Driver`, `LoggingDriver`, `DockerRootDir`, `ServerVersion` 등을 뽑습니다[2]. 이 소켓에 붙으려면 보통 root 권한이 필요합니다[2].

3. **바뀐 파일 목록을 뜹니다.** `docker diff` 는 컨테이너를 만든 뒤 달라진 파일·디렉터리를 `A`(추가), `D`(삭제), `C`(변경) 기호로 보여 줍니다[3]. 아래는 만든 예시입니다.

   ```
   C /tmp
   A /tmp/.x
   C /etc
   C /etc/passwd
   D /usr/bin/wget
   ```

   이 목록은 어디를 먼저 볼지 정하는 데 쓰고, 파일 내용과 시각은 4·5단계에서 확보한 사본에서 봅니다.

4. **필요하면 메모리 상태를 체크포인트로 남깁니다.** 컨테이너 프로세스의 메모리만 따로 떠야 할 때 쓰는 방법이고, 호스트 전체 메모리 수집은 [메모리 수집](memory-acquisition.md)을 봅니다. 방법마다 컨테이너에 주는 영향이 달라서 옵션을 기록해 둡니다.
   - Podman: `podman container checkpoint` 는 CRIU 로 컨테이너의 모든 프로세스를 체크포인트하고, 기본으로는 끝난 뒤 컨테이너를 **멈춥니다**[4]. `--leave-running`(`-R`)을 주면 계속 돌지만, 메모리와 파일 시스템이 같은 시점을 담도록 체크포인트 동안 cgroup 을 얼렸다가 풉니다[4]. `--export`(`-e`)는 결과를 아카이브로 내보내고 루트 파일 시스템 변경분도 함께 담으며, `--ignore-rootfs`·`--ignore-volumes` 로 빼는 옵션이 따로 있습니다[4]. `--keep`(`-k`)은 CRIU 가 만든 로그·통계 파일을 남깁니다[4]. systemd 를 엔트리포인트로 쓰는 컨테이너는 체크포인트가 안 될 수 있습니다[4].
   - Docker: `docker checkpoint create` 에는 저장 위치를 바꾸는 `--checkpoint-dir` 와 체크포인트 뒤에도 계속 돌게 하는 `--leave-running` 이 있습니다[3].
   - Kubernetes: 기능 게이트 `ContainerCheckpoint` 가 켜진 노드에서 kubelet 에 `POST /checkpoint/NAMESPACE/POD/CONTAINER` 를 보내면, kubelet 루트 디렉터리 아래 `checkpoints`(기본 `/var/lib/kubelet/checkpoints`)에 `checkpoint-<podFullName>-<containerName>-<timestamp>.tar` 이름으로 tar 파일이 생깁니다[5]. 게이트가 꺼져 있으면 404 가 돌아옵니다[5]. `ContainerCheckpoint` 게이트는 1.25~1.29 에서 알파(기본 꺼짐)였고 1.30 부터 베타(기본 켜짐)입니다[11]. 쿼리 매개변수 `timeout` 으로 체크포인트 제한 시간(초)을 줄 수 있고, 0 이거나 주지 않으면 CRI 기본 제한 시간을 씁니다[5]. tar 안의 구성은 노드의 CRI 구현(containerd, CRI-O 등)마다 다릅니다[5].

5. **디스크에서 데이터 루트를 확보합니다.** 호스트를 [디스크 이미징](disk-imaging.md)으로 뜨면 데이터 루트가 함께 들어오고, 이미징이 어려우면 적어도 1단계에서 찾은 데이터 루트 전체와 볼륨 경로를 복사합니다. overlay2 저장 드라이버에서는 레이어마다 `/var/lib/docker/overlay2/ID/` 아래 `diff` 디렉터리가 있고, 컨테이너의 쓰기층도 이 `diff` 이며 overlay 마운트의 `upperdir` 로 걸립니다[9]. 컨테이너 설정은 `containers/ID/config.v2.json`, overlay2 컨테이너의 마운트 정보는 `image/overlay2/layerdb/mounts/ID` 에 있습니다[6]. Podman 은 `storage/overlay-containers/ID/userdata/config.json`, `storage/overlay/레이어ID`, 그리고 v4 이상이면 컨테이너 목록 SQLite 파일 `storage/db.sql` 을 함께 가져옵니다[7]. 각 파일의 필드 뜻은 [Docker](../../02-artifacts/containers/docker/index.md), [Podman](../../02-artifacts/containers/podman.md) 페이지에 있습니다.

6. **컨테이너 로그를 따로 챙깁니다.** Docker 의 json-file 로그 드라이버는 데이터 루트의 `containers` 아래에 `*-json.log*` 파일을 남기고, local 드라이버는 같은 곳에 protobuf 항목으로 된 파일(압축된 `.gz` 포함)을 남깁니다[6]. Podman 은 기본 로그 대상이 syslog 또는 journald 라서 `ctr.log` 파일은 k8s-file 드라이버(또는 그 별칭인 json-file)로 설정한 컨테이너에만 생깁니다[7]. 따라서 Podman 컨테이너 로그를 찾을 때는 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md)을 함께 확보합니다.

7. **해시를 계산하고 수집 기록을 남깁니다.** 명령 결과와 복사한 파일의 해시, 명령을 돌린 시각, 준 옵션(특히 일시 정지·정지를 일으키는 옵션)을 기록합니다.

## 도구

| 도구 | 쓰임 | 주의 |
|---|---|---|
| UAC (`live_response/containers`) | docker·podman·containerd·LXC 명령 결과를 한 번에 수집[1] | 해당 명령이 설치돼 있을 때만 돈다[1] |
| Velociraptor `Linux.Applications.Docker.Info` | Docker 데몬 요약 정보[2] | 컨테이너별 상세는 없다 |
| 런타임 CLI (`docker`, `podman`, `lxc`) | inspect·logs·diff·export·checkpoint[3][4] | 라이브 호스트에서만 쓸 수 있다 |
| kubelet 체크포인트 API | 파드 안 컨테이너의 체크포인트 tar[5] | 기능 게이트가 필요하다[5] |
| checkpointctl | 체크포인트 아카이브의 프로세스 트리·열린 파일·소켓·메모리 검색, 두 아카이브 비교[12] | `diff` 는 v1.6.0 부터 있다[12] |
| dissect.target `docker.*`, `podman.*` | 디스크 이미지에서 컨테이너·이미지·로그 파싱[6][7] | overlay2 가 아닌 저장 드라이버는 마운트 경로를 풀지 않는다[6] |

## 함정과 한계

**`docker export`·`docker commit` 은 볼륨을 빼먹습니다.** `docker export` 는 컨테이너 파일 시스템을 tar 로 내보내지만 볼륨 내용은 넣지 않고, 볼륨이 기존 디렉터리 위에 마운트돼 있으면 볼륨이 아니라 그 아래 원래 디렉터리 내용을 내보냅니다[3]. `docker commit` 도 마운트된 볼륨의 데이터를 담지 않습니다[3]. 볼륨은 `config.v2.json` 의 `MountPoints` 항목마다 적힌 `Source`(호스트 쪽 경로)를 찾아 따로 복사합니다[6].

**수집 명령이 컨테이너 상태를 바꿀 수 있습니다.** `docker commit` 은 기본으로 커밋하는 동안 컨테이너의 모든 프로세스를 일시 정지하고, `--no-pause` 로 이를 끕니다[3]. `docker pause` 는 Linux 에서 freezer cgroup 을 써서 프로세스가 멈춘 줄 모르게 멈춥니다[3]. Podman 체크포인트는 기본으로 컨테이너를 정지시킵니다[4]. 운영 중인 서비스라면 어떤 명령이 멈춤을 일으키는지 미리 알리고, 실제로 멈춘 시각을 기록합니다.

**`docker cp` 로 꺼낸 파일은 소유자가 바뀝니다.** 호스트로 복사한 파일은 `docker cp` 를 실행한 사용자의 UID·GID 로 만들어지고, `-a` 를 줘야 원래 소유자를 유지합니다[3]. 소유자가 증거가 되는 파일은 `-a` 를 주거나 쓰기층 디렉터리에서 직접 복사합니다.

**데이터 루트가 기본 경로에 없을 수 있습니다.** `daemon.json` 의 `data-root` 를 확인하지 않으면 `/var/lib/docker` 가 비어 있다고 오판합니다[6]. rootless Podman 은 사용자 홈 아래에 있어서 `/var/lib/containers` 만 보면 놓칩니다[7]. Docker Engine 29.0 이상을 새로 설치한 호스트는 containerd 이미지 저장소를 기본으로 쓰고, 이때 containerd 저장소는 Docker 데이터 디렉터리와 다른 경로에 있습니다[10]. `docker info` 의 드라이버 상태가 `io.containerd.snapshotter.v1` 이면 이 경우이므로 [containerd·Kubernetes](../../02-artifacts/containers/containerd-kubernetes.md) 페이지의 경로도 함께 확보합니다[10].

**지운 파일은 쓰기층에 흔적만 남습니다.** 컨테이너 안에서 아래층(이미지)에 있던 파일을 지우면 overlayfs 는 쓰기층에 같은 이름의 whiteout 을 만듭니다[8]. whiteout 은 장치 번호 0/0 인 문자 장치이거나, xattr `trusted.overlay.whiteout` 이 붙은 크기 0 인 일반 파일입니다[8]. 쓰기층 디렉터리에 xattr `trusted.overlay.opaque` 가 `y` 로 붙어 있으면 아래층에 있는 같은 이름 디렉터리의 내용은 가려집니다[8]. 복사 도구가 문자 장치나 `trusted.*` xattr 를 옮기지 못하면 이 흔적이 사라지므로, 쓰기층은 디스크 이미지에서 보거나 xattr 를 보존하는 방식으로 복사합니다. xattr 을 읽는 법은 [권한·확장 속성](../../01-foundations/filesystem/permissions-xattr.md)을 봅니다.

**체크포인트 파일은 민감 정보를 담습니다.** 체크포인트는 보통 컨테이너 모든 프로세스의 메모리 페이지를 담아 개인 정보나 암호 키가 들어 있을 수 있고, 런타임은 이 파일을 root 만 읽도록 만들어야 합니다[5]. 증거 보관소로 옮긴 뒤에도 같은 수준으로 접근을 막습니다.

## 결과를 어떻게 해석하나

**증명하는 것**

- `docker diff` 목록과 쓰기층 `diff` 디렉터리는 컨테이너를 만든 뒤 이미지 대비 추가·변경·삭제된 경로를 보여 줍니다[3][9].
- 쓰기층의 whiteout 이름은 컨테이너 안에서 그 경로의 아래층 파일이 지워졌다는 기록입니다[8].
- `config.v2.json` 의 `Created`, `State.StartedAt`, `State.FinishedAt` 은 컨테이너를 만든 시각과 시작·종료 시각입니다[6]. 이 값에는 `2022-12-19T13:37:00.123456789Z` 처럼 소수점 아래 나노초 9자리까지 붙는 경우가 있고, 끝의 `Z` 는 UTC 표기입니다[6]. 시각 값 읽는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)을 봅니다.
- 체크포인트 아카이브는 보통 체크포인트 시점에 컨테이너 모든 프로세스의 메모리 페이지를 담습니다[5].

**증명하지 못하는 것**

- `docker diff` 는 언제 바뀌었는지를 알려 주지 않습니다. 시각은 쓰기층 파일의 타임스탬프를 따로 봐야 하고, 그 값도 컨테이너 안 프로세스가 바꿀 수 있습니다.
- 컨테이너 로그(`docker container logs`, `*-json.log*`)에는 앱이 표준 출력·표준 오류로 낸 내용만 있습니다. 앱이 파일로 쓴 로그는 쓰기층이나 볼륨에 있습니다.
- whiteout 은 지운 파일의 이름만 남기고 내용은 남기지 않습니다[8]. 원래 내용은 아래층 이미지 레이어에서 찾을 수 있지만, 그 파일은 이미지에 있던 원본이지 지우기 직전의 내용이 아닐 수 있습니다.
- export·commit 결과에 볼륨이 없다고 해서 볼륨에 데이터가 없었다는 뜻은 아닙니다[3].
- 체크포인트 tar 의 내부 구성은 런타임마다 달라서, 한 런타임의 해석 방법을 다른 런타임 결과에 그대로 쓸 수 없습니다[5].

보고서에는 "컨테이너 ID ○○의 쓰기층에 `/usr/bin/wget` 에 대한 whiteout 이 있다" 처럼 기록으로 확인되는 만큼 씁니다. "침입자가 wget 을 지웠다" 는 누가 지웠는지를 다른 기록([실행 중인 프로세스](../../02-artifacts/execution/proc.md), 저널, 셸 기록)으로 뒷받침할 때만 씁니다.

## 체크포인트 아카이브 분석과 연속 스냅숏

kubelet 이 만든 체크포인트 아카이브는 tar 파일이라 `tar -tvf` 로 목록을 볼 수 있습니다[5]. Podman 의 `--export` 아카이브는 기본으로 zstd 로 압축되고, `--compress` 로 gzip 이나 압축 없음(none)을 고를 수 있습니다[4]. 먼저 원본의 해시를 계산하고, 분석은 사본에서 합니다. Podman·CRI-O·containerd 아카이브에서 볼 파일은 아래와 같고, 실제로 어떤 파일이 들어가는지는 런타임과 옵션마다 다릅니다[4][5][12].

| 파일 | 담긴 내용 |
|---|---|
| `config.dump` | 컨테이너 ID·이름·이미지·OCI 런타임, 만든 시각 `createdTime`, 체크포인트 시각 `checkpointedTime` (JSON)[12] |
| `spec.dump` | 컨테이너의 OCI 런타임 스펙과 주석(`annotations`) (JSON)[12] |
| `checkpoint/` | CRIU 이미지 파일[12] |
| `rootfs-diff.tar` | 루트 파일 시스템 변경분[4][12] |
| `deleted.files` | 지운 파일의 경로 목록 (JSON 문자열 배열)[12] |
| `devshm-checkpoint.tar` | 컨테이너의 `/dev/shm` 디렉터리 내용 (Podman)[19] |
| `network.status` | Podman 네트워크 인터페이스별 IP·MAC·게이트웨이 (JSON)[12] |
| `dump.log` | CRIU 덤프 로그[12] |
| `status` | containerd 가 만든 아카이브에만 있는 상태 파일 (`CreatedAt`, `StartedAt`, `FinishedAt`, `Pid` 등)[12] |

`checkpoint/` 안의 CRIU 이미지는 파일마다 맨 앞에 32비트 매직 값(파일 종류)이 오고 필요하면 두 번째 매직 값(하위 종류)이 더 붙으며, 그 뒤로 32비트 크기와 protobuf 항목이 이어지는 형식입니다[13]. CRIU 이미지를 사람이 읽는 형식으로 푸는 도구 CRIT 로 내용을 볼 수 있습니다[13]. 프로세스 트리는 `pstree.img`, 레지스터와 시그널 마스크는 `core-PID.img`, 주소 공간(VMA)은 `mm-PID.img` 에 있습니다[13]. 열린 파일 디스크립터는 `fdinfo-*.img`, IPv4·IPv6 소켓은 `inetsk-*.img` 에 있고, `tcp-stream-*.img` 에는 큐에 남아 있던 데이터까지 포함한 TCP 연결 상태가 들어 있습니다[13].

메모리는 두 파일로 나뉩니다. `pagemap-*.img` 의 항목은 가상 주소 `vaddr` 와 페이지 수 `nr_pages` 로 어느 주소에 몇 페이지가 들어가는지 적고, `pages-*.img` 는 4KB 페이지를 pagemap 항목 순서대로 이어 붙인 원시 데이터입니다[14]. 그래서 특정 가상 주소의 내용은 pagemap 항목의 페이지 수를 앞에서부터 더해 pages 파일 안의 위치를 계산해서 찾습니다[14]. CRIU 는 메모리에 올라와 있지 않은 페이지와, 파일을 매핑했지만 고치지 않아 파일과 내용이 같은 페이지는 덤프하지 않습니다[15]. 실행 파일이나 라이브러리 코드처럼 고치지 않은 파일 매핑 내용은 pages 파일에 없으므로 원본 파일에서 봅니다.

이미지를 직접 풀지 않고 내용을 보려면 checkpointctl 을 씁니다. `show` 는 이미지·엔진·만든 시각·체크포인트 크기·루트 파일 시스템 변경 크기를 한 줄로 보여 줍니다[12]. `inspect` 는 `--ps-tree-cmd`(명령줄을 포함한 프로세스 트리), `--ps-tree-env`(환경 변수), `--files`(열린 파일 디스크립터), `--sockets`, `--mounts`, `--metadata`, `--stats` 를 골라 출력하고, `--format json` 으로 JSON 을 냅니다[12]. `memparse` 는 프로세스별 메모리 크기를 보여 주고, `--pid` 로 프로세스를 정해 `--search`·`--search-regex` 로 메모리 페이지에서 문자열을 찾으며 `--context` 로 앞뒤 바이트를 함께 출력합니다(검색은 v1.3.0 부터)[12]. v1.6.0(2026-08) 부터는 `diff` 로 두 체크포인트의 프로세스 트리·파일 디스크립터·소켓·메모리 크기 변화를 비교할 수 있습니다[12]. `list` 는 기본으로 `/var/lib/kubelet/checkpoints/` 의 체크포인트를 나열합니다[12]. 환경 변수와 메모리 검색 결과에는 비밀번호·토큰·세션 키가 그대로 나올 수 있어서[18], 출력 파일도 아카이브와 같은 수준으로 접근을 막습니다.

**시각.** kubelet 은 런타임에 체크포인트를 요청하기 직전의 노드 시계 값을 `time.Now().Format(time.RFC3339)` 로 파일 이름에 붙입니다[16]. 그래서 이름의 시각은 초 단위이고 노드 현지 시간대의 오프셋이 붙으며, 노드가 UTC 이면 `Z` 로 끝납니다[16]. 예를 들어 `checkpoint-web_default-app-2026-09-01T11:15:30+09:00.tar`(만든 예시)는 한국 시간대 노드에서 만든 이름입니다. 컨테이너를 만든 시각은 파일 이름이 아니라 `config.dump` 의 `createdTime` 에서 따로 봅니다[12]. 시각 값 읽는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)을 봅니다.

**증분 덤프.** CRIU 는 `/proc/PID/clear_refs` 에 4 를 써서 추적을 켜고, 그 뒤 `/proc/PID/pagemap` 의 soft-dirty 비트로 바뀐 페이지를 찾습니다[17]. 이 기능은 Linux 3.11 에 들어가 3.18 까지 다듬어졌고, `criu check --feature mem_dirty_track` 로 지원 여부를 확인합니다[17]. `--track-mem` 은 추적 상태를 초기화하고, `--prev-images-dir` 에 이전 `dump`·`pre-dump` 이미지 경로를 주면 그 뒤 바뀐 페이지만 덤프합니다[17]. 이렇게 만든 이미지에서 pagemap 항목의 `in_parent` 가 켜져 있으면 그 페이지 내용은 부모 이미지에 있고, 부모 이미지도 다시 자기 부모를 가리킬 수 있습니다[14]. 증분 이미지 하나만으로는 프로세스 메모리 전체를 되살릴 수 없어서, 처음 전체 덤프까지 이어지는 이미지를 모두 확보합니다.

**연속 스냅숏(FSC).** 증분 체크포인트를 짧은 간격으로 이어 떠서 시간 순서가 있는 스냅숏 묶음을 만드는 방법으로 포렌식 스냅숏 체인 (Forensic Snapshot Chains, FSC) 이 있습니다[18]. 보안 경보가 울리면 컨테이너를 정해진 간격으로 체크포인트하되 soft-dirty 비트로 앞 스냅숏 뒤 바뀐 페이지만 저장하고, 스냅숏마다 SHA-256 해시를 계산해 앞 스냅숏의 해시와 함께 담아 사슬로 잇습니다[18]. 중간 스냅숏 하나를 고치면 그 뒤 해시가 모두 맞지 않게 됩니다[18]. 분석할 때는 이웃한 두 스냅숏을 비교해서, 뒤 스냅숏에만 있는 프로세스·소켓·메모리 내용은 앞 스냅숏 뒤에 생겼고 앞 스냅숏에만 있던 것은 뒤 스냅숏 전에 사라졌다고 순서를 정합니다[18]. Stoyanov 등(2026)은 노드 2대(각 52코어, 메모리 62GB, 디스크 3TB, Ubuntu 22.04)에 CRI-O v1.32.12 와 CRIU v4.2 로 구성한 Kubernetes 클러스터에서 2~3초 간격으로 스냅숏을 뜨고 각 실험을 10번 되풀이했습니다[18]. 이 조건에서 `at` 로 예약해 디스크에 쓰지 않고 메모리에서만 도는 파이썬 코드가 NGINX 워커 메모리를 읽는 경우, 43초 동안 뜬 스냅숏 19개(약 2.4초 간격)에서 `at` 작업, 잠깐 돌고 끝난 `python3` 프로세스, 디코딩된 코드, 밖으로 나간 HTTP 연결이 모두 확인됐고 이 흔적은 컨테이너 로그와 파일 시스템에는 없었습니다[18]. 한 번 떠서 전체를 담는 체크포인트와 비교하면 스냅숏 크기는 DSVW(취약점 실습용 웹 앱)가 8.6MB 에서 553KB 로, NGINX 가 217MB 에서 15MB 로 줄었습니다[18]. 프로세스가 멈춘 시간은 255.7ms 에서 240.3ms, 1271.6ms 에서 1194.9ms 로 약 6% 줄었고, 3초 간격으로 뜨면 시간당 DSVW 약 663MB, NGINX 약 18GB 가 쌓였습니다[18].

스냅숏 사이에 시작해서 끝난 행위는 프로세스나 소켓으로 남지 않을 수 있고, 간격을 좁히거나 무작위로 바꿔도 빈틈은 남습니다[18]. 그래서 두 스냅숏 사이에 나타난 흔적은 그 구간 안에서 생겼다는 것까지만 알 수 있고, 구간 안의 정확한 시각은 다른 기록으로 좁혀야 합니다. 이 방법은 호스트 커널·CRIU·컨테이너 런타임을 믿는다는 전제라서 커널 루트킷이 있거나 CRIU·체크포인트 메타데이터가 조작된 호스트에서 뜬 스냅숏은 믿기 어렵고, 스냅숏을 뜨기 전에 지워진 컨테이너는 분석할 수 없습니다[18]. 커널이 지원하지 않는 기능이나 GPU 같은 장치 때문에 체크포인트가 실패하면 일부만 담긴 스냅숏이 생기고[18], checkpointctl 의 메모리 분석은 문자열·바이트를 뽑는 수준이라 언어 런타임의 자료 구조는 따로 해석해야 합니다[18].

## 참고 문헌

1. tclahr, UAC — `artifacts/live_response/containers/docker.yaml`, `podman.yaml`, `containerd.yaml`, `lxc.yaml`. https://github.com/tclahr/uac/tree/main/artifacts/live_response/containers
2. Velocidex, Velociraptor — `Linux.Applications.Docker.Info`. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Applications/Docker/Info.yaml
3. Docker CLI reference — `container_diff.md`, `container_export.md`, `container_commit.md`, `container_pause.md`, `container_cp.md`, `checkpoint_create.md`. https://github.com/docker/cli/tree/master/docs/reference/commandline
4. Podman — podman-container-checkpoint(1). https://github.com/containers/podman/blob/main/docs/source/markdown/podman-container-checkpoint.1.md
5. Kubernetes — Kubelet Checkpoint API. https://github.com/kubernetes/website/blob/main/content/en/docs/reference/node/kubelet-checkpoint-api.md
6. Fox-IT, dissect.target — `plugins/apps/container/docker.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/container/docker.py
7. Fox-IT, dissect.target — `plugins/apps/container/podman.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/container/podman.py
8. Linux kernel — Overlay Filesystem (`Documentation/filesystems/overlayfs.rst`). https://github.com/torvalds/linux/blob/master/Documentation/filesystems/overlayfs.rst
9. Docker Docs — OverlayFS storage driver. https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/overlayfs-driver.md
10. Docker Docs — containerd image store with Docker Engine. https://github.com/docker/docs/blob/main/content/manuals/engine/storage/containerd.md
11. Kubernetes — Feature Gates (`ContainerCheckpoint`). https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/
12. checkpoint-restore, checkpointctl — `README.md`, `lib/metadata.go`, `docs/checkpointctl-*.adoc`, 릴리스 노트(v1.3.0, v1.6.0). https://github.com/checkpoint-restore/checkpointctl
13. CRIU — Images. https://criu.org/Images
14. CRIU — Memory dumps. https://criu.org/Memory_dumps
15. CRIU — Memory dumping and restoring. https://criu.org/Memory_dumping_and_restoring
16. Kubernetes — `pkg/kubelet/kubelet.go` (`CheckpointContainer`). https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/kubelet.go
17. CRIU — Memory changes tracking. https://criu.org/Memory_changes_tracking
18. Stoyanov, R., Goldoni, L., Reber, A., Hargreaves, C., Bruno, R. "Forensic analysis of container snapshot chains for post-event reconstruction." Forensic Science International: Digital Investigation 57 (Supplement), 302114, 2026 (DFRWS USA 2026). doi:10.1016/j.fsidi.2026.302114. https://www.dpss.inesc-id.pt/~rbruno/papers/rstoyanov-dfrws-usa26.pdf
19. Podman — `libpod/container_internal_common.go` (`/dev/shm` 체크포인트 처리). https://github.com/containers/podman/blob/main/libpod/container_internal_common.go
