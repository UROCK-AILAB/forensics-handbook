---
title: "이미지와 레이어"
parent: "Docker"
grand_parent: "아티팩트 · 컨테이너와 가상화"
nav_order: 780
---

# 이미지와 레이어 (Images·Layers)

Docker 가 받아 둔 이미지의 이름·태그, 이미지 설정, 레이어 사이의 관계를 `/var/lib/docker/image/overlay2/` 아래 파일들에서 읽는 방법을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

`docker pull` 이나 `docker build` 로 이미지가 생기면 Docker 는 세 가지를 따로 저장합니다. 이미지 이름·태그와 이미지 ID 의 짝, 이미지 설정 JSON, 그리고 레이어 하나하나의 메타데이터입니다[1][2][5]. 레이어의 실제 파일 내용은 저장소 드라이버 폴더(`/var/lib/docker/overlay2/`)에 따로 있고, 이 쪽에서 다루는 메타데이터가 둘을 이어 줍니다. 레이어 내용을 겹쳐 읽는 방법은 [overlay 파일 시스템 (overlay2)](overlay2.md) 에서 다룹니다.

조사에서는 "이 호스트에 어떤 이미지가 있었나", "그 이미지는 어떤 명령으로 만들어졌나", "컨테이너는 어느 레이어 위에서 돌았나" 를 이 파일들로 답합니다.

## 위치와 버전별 차이

Docker 에는 이미지 저장 방식이 두 가지 있습니다. 어느 방식을 쓰는 호스트인지는 [Docker 허브](index.md) 의 판별 방법을 따르면 됩니다.

| 저장 방식 | 쓰는 경우 | 이미지 메타데이터 | 레이어 내용 |
|---|---|---|---|
| 그래프 드라이버 (overlay2) | Docker Engine 29.0 전 판을 쓰거나, 그 판에서 29.0 이상으로 올린 호스트 | `/var/lib/docker/image/overlay2/` | `/var/lib/docker/overlay2/` |
| containerd 이미지 저장소 (containerd image store) | Docker Engine 29.0 이상을 새로 설치한 호스트 | `/var/lib/containerd/io.containerd.metadata.v1.bolt/meta.db` | `/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/` |

containerd 저장소는 Docker Engine 29.0 이상을 새로 설치할 때 기본값이고, 옛 판에서 올린 데몬은 containerd 저장소를 켜기 전까지 overlay2 를 계속 씁니다[11]. containerd 저장소를 켜면 overlay2 쪽 이미지와 컨테이너는 디스크에 남은 채 숨겨지므로[11], 한 호스트에 두 방식의 흔적이 함께 있을 수 있습니다. 데이터 루트를 `daemon.json` 의 `data-root` 로 옮긴 호스트라면 위 표의 `/var/lib/docker` 를 그 경로로 바꿔 읽습니다(허브 참고).

containerd 저장소에서는 압축된 레이어 blob·매니페스트·설정이 `io.containerd.content.v1.content/blobs/sha256/` 에, 풀어낸 레이어가 `snapshots/번호/fs` 에 있습니다[12][13]. 스냅숏 폴더 이름은 1, 2, 3 같은 순번이고, 스냅숏 이름도 콘텐츠 저장소의 blob 해시와 다릅니다[13]. containerd 저장소는 압축본과 풀어낸 것을 둘 다 보관해 디스크를 더 씁니다[11]. `meta.db` 구조와 containerd 쪽 분석은 [containerd 와 Kubernetes 노드](../containerd-kubernetes.md) 에서 다룹니다. 이 아래는 overlay2 방식 이야기입니다.

## 구조

이미지 루트는 `데이터루트/image/드라이버이름` 이고, overlay2 라면 `/var/lib/docker/image/overlay2/` 입니다[1]. 그 아래 구성은 다음과 같습니다.

| 경로 | 내용 |
|---|---|
| `repositories.json` | 이미지 이름·태그와 이미지 ID 의 짝[1][7] |
| `imagedb/content/sha256/` | 이미지 설정 JSON. 파일 이름이 이미지 ID 입니다[1][2] |
| `imagedb/metadata/sha256/이미지ID/` | `parent`, `lastUpdated` 같은 이미지별 부가 정보[2][3] |
| `layerdb/sha256/체인ID/` | 레이어별 메타데이터[5][6] |
| `layerdb/mounts/컨테이너ID/` | 컨테이너 쓰기 레이어와 이미지 레이어의 연결[5] |
| `distribution/` | 레지스트리에서 받을 때 쓰는 배포 메타데이터[1] |

### repositories.json

최상위 `Repositories` 객체 아래에 저장소 이름이 키로 있고, 그 값은 다시 "저장소 이름을 포함한 참조 문자열(태그 또는 다이제스트) → 이미지 ID" 의 짝입니다[7][14]. 아래는 만든 예시입니다.

```json
{"Repositories":{"example/web":{"example/web:1.0":"sha256:3f1c...(64자리)","example/web@sha256:9ab2...":"sha256:3f1c...(64자리)"}}}
```

값에 있는 `sha256:` 뒤 64자리가 `imagedb/content/sha256/` 의 파일 이름입니다[14]. dissect 는 이 64자리의 앞 12자리를 짧은 이미지 ID 로 씁니다[14].

### imagedb — 이미지 설정

`imagedb/content/sha256/64자리헥스` 파일 하나가 이미지 설정 JSON 하나이고, 파일 이름은 그 내용의 sha256 입니다[2]. 설정 JSON 에서 조사에 쓰는 필드는 다음과 같습니다[8].

| 필드 | 뜻 |
|---|---|
| `created` | 이미지를 만든 시각(RFC 3339) |
| `rootfs.diff_ids` | 레이어 내용 해시(DiffID) 목록. 아래 레이어부터 위 레이어 순서 |
| `history[].created` | 그 단계를 만든 시각 |
| `history[].created_by` | 그 단계를 만든 명령. 예: `/bin/sh -c apk add curl` |
| `history[].comment` | 만들 때 붙인 설명 |
| `history[].empty_layer` | `true` 면 파일 시스템 변화가 없는 단계(예: Dockerfile 의 `ENV`) |

`history` 는 `rootfs.diff_ids` 와 개수가 맞지 않을 수 있습니다. `empty_layer` 가 `true` 인 단계는 레이어를 만들지 않기 때문입니다[8].

`imagedb/metadata/sha256/이미지ID/` 폴더에는 키마다 파일이 하나씩 있습니다. `parent` 에는 부모 이미지 ID 가 들어가고[3], `lastUpdated` 에는 이미지에 태그를 붙일 때(`TagImage`) 그때의 시각을 RFC3339Nano 문자열로 적습니다[3][4].

### layerdb — 레이어 메타데이터

`layerdb/sha256/` 아래 폴더 이름은 체인 ID (ChainID) 입니다. 체인 ID 는 맨 아래 레이어라면 그 레이어의 DiffID 와 같고, 그 위로는 "아래까지의 체인 ID + 공백 + 이번 DiffID" 를 다시 해시한 값입니다[8]. 그래서 같은 내용의 레이어라도 아래에 무엇이 깔렸느냐에 따라 체인 ID 가 달라집니다.

각 체인 ID 폴더에 있는 파일은 다음과 같습니다[5].

| 파일 | 내용 |
|---|---|
| `diff` | 이 레이어의 DiffID (`sha256:...`) |
| `parent` | 아래 레이어의 체인 ID |
| `size` | 레이어 크기(10진수 문자열) |
| `cache-id` | `/var/lib/docker/overlay2/` 아래 폴더 이름 |
| `descriptor.json` | 레지스트리 기술자(descriptor) |
| `tar-split.json.gz` | 레이어 tar 를 풀 때 함께 적어 둔 tar 구성 정보(gzip 압축)[6] |

`cache-id` 는 레이어를 만들 때 무작위로 새로 만든 ID 입니다[6]. 따라서 체인 ID 와 `overlay2/` 폴더 이름은 서로 다르고, 레이어 내용을 찾으려면 반드시 `cache-id` 를 거쳐야 합니다[5][10].

컨테이너마다 `layerdb/mounts/컨테이너ID/` 폴더가 생기고, 그 안의 `mount-id` 에는 컨테이너 쓰기 레이어의 `overlay2/` 폴더 이름이, `init-id` 에는 초기화 레이어 이름이, `parent` 에는 컨테이너가 올라탄 이미지 맨 위 레이어의 체인 ID 가 들어갑니다[5]. 쓰기 레이어 폴더의 내용은 [overlay 파일 시스템 (overlay2)](overlay2.md) 에서 봅니다.

> 그림 자리: `repositories.json` → 이미지 ID → `imagedb` 설정 JSON 의 `rootfs.diff_ids` → 체인 ID → `layerdb/sha256/체인ID/cache-id` → `overlay2/폴더` 로 이어지는 흐름, 그리고 `layerdb/mounts/컨테이너ID/mount-id` 가 쓰기 레이어 폴더를 가리키는 모습

### 레이어 tar 안의 삭제 표시

이미지 레이어 tar 안에서는 아래 레이어의 파일을 지웠다는 표시가 `.wh.` 에 원래 이름을 붙인 빈 파일입니다[9]. 폴더 안 전부를 가리는 표시는 `.wh..wh..opq` 라는 이름의 파일입니다[9]. overlay2 드라이버는 레이어를 풀 때 이 표시를 커널 overlayfs 방식으로 바꿔 씁니다[18]. 그래서 디스크의 `overlay2/` 폴더에서는 다른 모양으로 보이고, 그 모양은 [overlay2 쪽](overlay2.md) 에서 다룹니다.

## 증거로서 의미

증명하는 것은 다음과 같습니다.

- `repositories.json` 과 `imagedb` 에 남아 있는 이미지는 수집 시점에 이 호스트의 이미지 저장소에 있었습니다.
- 그 이미지에 어떤 이름·태그가 붙어 있었는지, 어떤 레이어가 어떤 순서로 쌓였는지를 보여 줍니다.
- 빌드 도구가 `history` 를 채웠다면 각 레이어를 만든 명령을 보여 줍니다. 공격자가 호스트에서 직접 빌드한 이미지라면 여기에 설치 명령이 남을 수 있습니다.
- `layerdb/mounts/컨테이너ID/` 로 컨테이너와 이미지 레이어, 쓰기 레이어 폴더를 이어 붙일 수 있습니다.

증명하지 못하는 것은 다음과 같습니다.

- 설정 JSON 의 `created` 는 이미지를 만든 시각이고, 이 호스트로 받은 시각이 아닙니다. 공개 이미지라면 받은 날보다 한참 이른 시각이 나올 수 있습니다.
- 누가 이미지를 받았는지는 여기에 없습니다. `docker` 명령을 친 사람은 [셸 명령 기록](../../execution/shell-history/index.md) 이나 [systemd 저널](../../../01-foundations/logging/systemd-journal/index.md) 에서 따로 찾아야 합니다.
- 이미지를 받은 뒤 실행했는지는 여기서 알 수 없습니다. 실행 흔적은 [컨테이너 설정과 로그](container-logs.md) 에서 봅니다.

## 시각 해석

| 값 | 바뀌는 때 | 시간대 |
|---|---|---|
| 설정 JSON `created`, `history[].created` | 이미지를 빌드할 때. 받은 뒤에는 바뀌지 않습니다 | RFC 3339 문자열이라 끝에 `Z` 나 `+09:00` 같은 오프셋이 붙습니다[8]. 빌드한 쪽 시계 기준입니다 |
| `imagedb/metadata/.../lastUpdated` | 이미지에 태그를 붙일 때[4] | 데몬이 `time.Now()` 를 RFC3339Nano 로 적어 데몬 호스트의 현지 시간대 오프셋이 붙습니다[3] |
| `layerdb`·`overlay2` 폴더와 파일의 파일 시스템 시각 | 레이어를 풀어 저장할 때 폴더가 생깁니다 | 하위 파일 시스템의 inode 시각이라 UTC 기준 값입니다([ext4](../../../01-foundations/filesystem/ext4/index.md), [XFS](../../../01-foundations/filesystem/xfs.md)) |

이미지를 받은 시각은 `lastUpdated` 와 해당 체인 ID 폴더·`cache-id` 폴더의 생성 시각으로 좁힙니다. 이 값들도 "그 시각 전후에 저장소에 생겼다" 까지만 말합니다. 여러 이미지가 같은 아래 레이어를 공유하면 레이어는 체인 ID 하나로 한 번만 저장되므로, 공유 레이어 폴더의 시각은 그 레이어를 처음 받은 이미지 쪽 시각일 가능성이 있습니다.

## 함정과 한계

- 체인 ID, DiffID, `cache-id`, 레지스트리 blob 해시는 모두 다른 값입니다. 체인 ID 로 `overlay2/` 폴더를 찾으면 나오지 않습니다[5][10]. 레지스트리의 압축 blob 해시도 풀어낸 레이어 해시와 다릅니다[13].
- 레이어를 지울 때 Docker 는 먼저 `layerdb/sha256/체인ID` 폴더 이름을 `체인ID-무작위ID-removing` 으로 바꾸고, `overlay2/` 쪽 폴더를 지운 뒤, 이름을 바꾼 폴더를 지웁니다[6]. 레이어는 참조가 모두 풀려야 지워집니다[6]. 그래서 이름이 `-removing` 으로 끝나는 폴더가 남아 있다면 레이어 삭제가 중간에 멈춘 것이고, Docker 는 이런 폴더를 고아 레이어(orphan layer)로 찾아 정리합니다[5][6]. 이 폴더 안의 `diff`·`cache-id` 로 지우려던 레이어를 알 수 있습니다.
- 지워진 이미지의 설정 JSON 과 레이어는 파일 시스템 수준에서 되살려야 합니다. 방법은 [지운 파일 되살리기](../../../03-techniques/analysis/file-recovery.md) 를 봅니다.
- plaso 의 `docker_layer_config` 플러그인은 JSON 에 `container_config` 와 `docker_version` 이 둘 다 있을 때만 처리합니다[15]. OCI 명세의 설정 JSON 에는 두 키가 없으므로[8], 두 키가 없는 설정 JSON 은 이 플러그인 결과에서 빠집니다. 이 플러그인은 파일 경로의 끝에서 두 번째 칸을 레이어 ID 로 쓰므로[15], `imagedb/content/sha256/이미지ID` 파일을 넣으면 레이어 ID 칸에 `sha256` 이 들어갑니다.
- dissect 의 `docker.images` 는 `image/overlay2/repositories.json` 에서 이미지 목록을 읽습니다[14]. containerd 저장소를 쓰는 호스트라면 이 결과가 비어 있어도 이미지가 없다는 뜻이 아닙니다.

## 직접 분석해 보기

모든 메타데이터가 짧은 텍스트나 JSON 이라 헥스 편집기 대신 `cat` 과 `jq` 로 따라가면 됩니다. 검체를 `/mnt/root` 에 읽기 전용으로 붙였다고 가정합니다.

1. 이미지 목록을 뽑습니다.
   ```
   jq -r '.Repositories | to_entries[] | .value | to_entries[] | "\(.key)\t\(.value)"' /mnt/root/var/lib/docker/image/overlay2/repositories.json
   ```
2. 이미지 ID 의 64자리로 설정 JSON 을 열고 빌드 시각과 명령을 봅니다.
   ```
   jq '{created, diff_ids: .rootfs.diff_ids, history}' /mnt/root/var/lib/docker/image/overlay2/imagedb/content/sha256/이미지ID
   cat /mnt/root/var/lib/docker/image/overlay2/imagedb/metadata/sha256/이미지ID/lastUpdated
   ```
3. 레이어마다 `diff` 를 대조해 체인 ID 폴더를 찾고, `cache-id` 로 레이어 내용 폴더를 찾습니다.
   ```
   cd /mnt/root/var/lib/docker/image/overlay2/layerdb/sha256
   for d in */; do printf '%s\t%s\t%s\n' "${d%/}" "$(cat "$d/diff")" "$(cat "$d/cache-id")"; done
   ```
4. 컨테이너가 어느 레이어에 올라탔는지 봅니다.
   ```
   cd /mnt/root/var/lib/docker/image/overlay2/layerdb/mounts
   for d in */; do printf '%s\t%s\t%s\n' "${d%/}" "$(cat "$d/mount-id")" "$(cat "$d/parent")"; done
   ```
5. `find /mnt/root/var/lib/docker/image/overlay2/layerdb -maxdepth 2 -name '*-removing'` 로 삭제가 멈춘 레이어가 있는지 봅니다.

공개 도구로는 다음을 씁니다.

- dissect.target `docker.images`: 이미지마다 name, tag, image_id(앞 12자리), hash, created, source 를 냅니다[14].
- docker-explorer: `de.py -r /mnt/root/var/lib/docker history 컨테이너ID` 로 컨테이너가 쓰는 이미지의 단계별 명령·시각·크기를 봅니다[16].
- plaso `docker_layer_config` 플러그인: `container_config` 와 `docker_version` 이 있는 설정 JSON 에서 `created` 와 `container_config.Cmd` 를 타임라인 사건으로 냅니다[15].
- 라이브 호스트라면 UAC 의 Docker 수집 목록이 `docker image ls --all` 결과를 남깁니다[17]. 라이브 수집 절차는 [컨테이너 수집](../../../03-techniques/acquisition/container-acquisition.md) 을 봅니다.

## 교차 검증

- [컨테이너 설정과 로그](container-logs.md): 컨테이너가 어느 이미지로 만들어졌고 언제 시작했는지. 이미지 ID 를 여기 결과와 맞춰 봅니다.
- [overlay 파일 시스템 (overlay2)](overlay2.md): `cache-id`·`mount-id` 가 가리키는 폴더의 실제 내용과 컨테이너가 바꾼 파일.
- [셸 명령 기록](../../execution/shell-history/index.md): `docker pull`, `docker build`, `docker load` 명령과 그 순서.
- [systemd 저널](../../../01-foundations/logging/systemd-journal/index.md): `docker.service` 단위의 데몬 기록.
- [타임라인 만들기](../../../03-techniques/analysis/timeline.md): `lastUpdated`, 레이어 폴더 생성 시각, 셸 기록을 한 줄로 세웁니다.

## 실습

직접 만든 실험용 가상 머신에 overlay2 방식 Docker 를 두고, 이미지를 두 개 받고 하나를 지운 뒤 디스크 이미지를 떠서 풀어 봅니다.

1. `repositories.json` 에 남은 이미지와 `imagedb/content/sha256/` 에 남은 설정 파일 개수가 맞습니까? 맞지 않는다면 어느 쪽에 무엇이 남았습니까?
2. 받은 이미지의 `created` 와 `lastUpdated` 는 얼마나 차이 납니까? 어느 값이 받은 시각에 가깝습니까?
3. 두 이미지가 공유하는 레이어를 체인 ID 로 찾을 수 있습니까? 한 이미지를 지운 뒤에도 그 레이어의 `cache-id` 폴더가 남아 있습니까?
4. 실행 중인 컨테이너 하나를 골라 `layerdb/mounts/컨테이너ID/parent` 에서 시작해 이미지 이름까지 거꾸로 따라갈 수 있습니까?

## 참고 문헌

1. moby/moby, `daemon/daemon.go` — https://github.com/moby/moby/blob/master/daemon/daemon.go
2. moby/moby, `daemon/internal/image/fs.go` — https://github.com/moby/moby/blob/master/daemon/internal/image/fs.go
3. moby/moby, `daemon/internal/image/store.go` — https://github.com/moby/moby/blob/master/daemon/internal/image/store.go
4. moby/moby, `daemon/images/image_tag.go` — https://github.com/moby/moby/blob/master/daemon/images/image_tag.go
5. moby/moby, `daemon/internal/layer/filestore.go` — https://github.com/moby/moby/blob/master/daemon/internal/layer/filestore.go
6. moby/moby, `daemon/internal/layer/layer_store.go` — https://github.com/moby/moby/blob/master/daemon/internal/layer/layer_store.go
7. moby/moby, `daemon/internal/refstore/store.go` — https://github.com/moby/moby/blob/master/daemon/internal/refstore/store.go
8. Open Container Initiative, Image Format Specification `config.md`(Layer ChainID 포함) — https://github.com/opencontainers/image-spec/blob/main/config.md
9. Open Container Initiative, Image Format Specification `layer.md` — https://github.com/opencontainers/image-spec/blob/main/layer.md
10. Docker 공식 문서, OverlayFS storage driver — https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/overlayfs-driver.md
11. Docker 공식 문서, containerd image store — https://github.com/docker/docs/blob/main/content/manuals/engine/storage/containerd.md
12. containerd, `docs/ops.md` — https://github.com/containerd/containerd/blob/main/docs/ops.md
13. containerd, `docs/content-flow.md` — https://github.com/containerd/containerd/blob/main/docs/content-flow.md
14. fox-it/dissect.target, `dissect/target/plugins/apps/container/docker.py` — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/container/docker.py
15. log2timeline/plaso, `plaso/parsers/jsonl_plugins/docker_layer_config.py` — https://github.com/log2timeline/plaso/blob/main/plaso/parsers/jsonl_plugins/docker_layer_config.py
16. google/docker-explorer, `README.md` — https://github.com/google/docker-explorer
17. tclahr/uac, `artifacts/live_response/containers/docker.yaml` — https://github.com/tclahr/uac/blob/main/artifacts/live_response/containers/docker.yaml
18. moby/moby, `daemon/graphdriver/overlay2/overlay.go` — https://github.com/moby/moby/blob/master/daemon/graphdriver/overlay2/overlay.go
