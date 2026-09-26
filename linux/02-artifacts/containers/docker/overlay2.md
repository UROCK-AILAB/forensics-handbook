---
title: "overlay 파일 시스템"
parent: "Docker"
grand_parent: "아티팩트 · 컨테이너와 가상화"
nav_order: 800
---

# overlay 파일 시스템 (overlay2)

`/var/lib/docker/overlay2/` 의 레이어 폴더에서 컨테이너가 만들고 바꾸고 지운 파일을 가려내는 방법을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

overlay 파일 시스템 (OverlayFS) 은 읽기 전용 아래 층(lowerdir)과 쓰기용 위 층(upperdir)을 한 폴더(merged)에 겹쳐 보여 주는 커널 기능입니다[1]. Docker 의 overlay2 저장소 드라이버는 이미지 레이어를 아래 층으로, 컨테이너마다 새로 만든 폴더를 위 층으로 써서 컨테이너의 루트 파일 시스템을 만듭니다[5]. 아래 층은 바뀌지 않으므로 컨테이너가 파일을 새로 만들거나 고치거나 지우면 그 결과가 모두 위 층에 쌓입니다[1][5].

그래서 컨테이너 쓰기 층의 `diff/` 폴더는 "컨테이너가 살아 있는 동안 이미지와 달라진 것" 의 목록 구실을 합니다. 컨테이너 안에서 받은 도구, 고친 설정 파일, 앱이 파일로 따로 쓴 로그도 여기서 찾습니다. 이미지 이름·레이어 관계는 [이미지와 레이어](images-layers.md), 표준 출력 로그는 [컨테이너 설정과 로그](container-logs.md) 에서 다룹니다.

## 위치와 버전별 차이

| 저장 방식 | 레이어 내용 위치 | 이 쪽과의 관계 |
|---|---|---|
| overlay2 드라이버 | `/var/lib/docker/overlay2/` [2][5] | 이 쪽의 대상입니다 |
| 옛 overlay 드라이버 | `/var/lib/docker/overlay/` 아래 폴더마다 `root/`(이미지 층) 또는 `lower-id`·`upper/`·`work/`·`merged/`(컨테이너 층)[5] | 폴더 이름만 다르고 커널 규칙은 같습니다 |
| containerd 이미지 저장소 (Docker Engine 29.0 이상 새 설치) | `/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/번호/fs` | [containerd 와 Kubernetes 노드](../containerd-kubernetes.md) 에서 다룹니다 |
| Podman | containers-storage 의 overlay 드라이버 | [Podman](../podman.md) 에서 다룹니다 |

어느 저장 방식을 쓰는 호스트인지는 [Docker 허브](index.md) 의 판별 방법을 따르고, 데이터 루트를 옮긴 호스트라면 `/var/lib/docker` 를 그 경로로 바꿔 읽습니다.

overlay2 는 커널 4.0 이상, RHEL·CentOS 는 3.10.0-514 이상 커널에서 쓸 수 있습니다[5]. 하위 파일 시스템이 XFS 라면 `ftype=1`(d_type) 로 만든 파일 시스템이어야 합니다[2][5]. 실행 중인 호스트에서는 `docker info` 의 드라이버 상태에 `Backing Filesystem`, `Supports d_type`, `Using metacopy`, `userxattr` 값이 나오므로[2] 아래에서 설명할 표시 방식을 미리 가늠할 수 있습니다.

## 구조

### 레이어 폴더

`/var/lib/docker/overlay2/` 아래 폴더 하나가 레이어 하나입니다. 폴더 이름은 무작위로 만든 ID 라서 레이어의 체인 ID 와도, 컨테이너 ID 와도 다르고[3][5], `layerdb` 의 `cache-id`·`mount-id` 로 이어 붙입니다([이미지와 레이어](images-layers.md) 참고).

| 이름 | 있는 곳 | 내용 |
|---|---|---|
| `diff/` | 모든 층 | 그 층의 파일 내용. 컨테이너 층에서는 위 층(upperdir)입니다[2] |
| `link` | 모든 층 | 26자 짧은 ID 한 줄[2] |
| `lower` | 부모가 있는 층 | 아래 층들의 짧은 링크를 `:` 로 이은 한 줄. 위층부터 아래층 순서입니다[2][5]. 만든 예시: `l/AAAAAAAAAAAAAAAAAAAAAAAAA2:l/BBBBBBBBBBBBBBBBBBBBBBBBB7` |
| `work/` | 부모가 있는 층 | overlay 가 안에서 쓰는 폴더[2][5] |
| `merged/` | 부모가 있는 층 | 마운트 지점. 마운트를 풀 때 지웁니다[2] |
| `committed` | 자식 층이 생긴 층 | 빈 파일. 있으면 그 층은 읽기 전용으로 마운트합니다[2] |

`/var/lib/docker/overlay2/l/` 에는 짧은 ID 이름의 심볼릭 링크가 있고, 각각 `../레이어폴더/diff` 를 가리킵니다[2][5]. 마운트 명령의 인자가 한 페이지 크기를 넘지 않도록 짧은 이름을 쓰는 것이고, 쌓을 수 있는 아래 층은 128개까지입니다[2].

컨테이너 하나에는 폴더가 두 개 생깁니다. 쓰기 층 폴더와 그 바로 아래 `쓰기층이름-init` 폴더입니다[3]. 쓰기 층 폴더 이름은 `image/overlay2/layerdb/mounts/컨테이너ID/mount-id` 에, 초기화 층 이름은 같은 폴더의 `init-id` 에 적혀 있습니다[4]. 따라서 컨테이너가 바꾼 파일은 `overlay2/mount-id값/diff/` 에서 봅니다.

> 그림 자리: 컨테이너 ID → `layerdb/mounts/ID/mount-id` → `overlay2/폴더/diff`(위 층), 그리고 그 폴더의 `lower` 가 `l/짧은ID` 를 거쳐 `-init` 층과 이미지 층들의 `diff` 를 가리키는 모습

### 위 층에 남는 표시

위 층에는 일반 파일 말고도 커널이 남기는 표시가 있습니다. 이미지 tar 안의 `.wh.` 표시와는 모양이 다르고, tar 쪽 표시는 [이미지와 레이어](images-layers.md) 에서 다룹니다.

| 표시 | 모양 | 뜻 |
|---|---|---|
| 삭제 표시 (whiteout) | 장치 번호 0/0 인 문자 장치, 또는 크기 0 인 일반 파일에 확장 속성 `trusted.overlay.whiteout`[1] | 같은 이름의 아래 층 파일을 지웠습니다 |
| 불투명 폴더 (opaque directory) | 폴더에 확장 속성 `trusted.overlay.opaque` = `y`[1] | 같은 이름의 아래 층 폴더 내용을 모두 가립니다. 컨테이너 안에서 폴더를 지우면 생깁니다[5] |
| `trusted.overlay.opaque` = `x` | 병합 폴더 자체에 붙습니다[1] | 그 안에 확장 속성 방식 whiteout 이 있다는 표시 |
| `trusted.overlay.origin` | 위 층 파일의 확장 속성 | copy_up 할 때 아래 층 inode 의 NFS 파일 핸들과 아래 파일 시스템 UUID 를 적습니다[1] |
| `trusted.overlay.redirect` | 폴더의 확장 속성 | `redirect_dir` 기능이 켜진 상태에서 아래 층 폴더 이름을 바꾸면 원래 경로를 적습니다[1] |
| `trusted.overlay.metacopy` | 위 층 파일의 확장 속성 | `metacopy` 기능이 켜진 상태에서 메타데이터만 올린 파일. 데이터는 아직 아래 층에 있습니다[1] |

`-o userxattr` 로 마운트했다면 이름공간이 `trusted.overlay.` 대신 `user.overlay.` 입니다[1]. Docker 는 필요하다고 판단하면 이 옵션을 붙이는데[2], rootless 모드 호스트에서 이 이름을 만날 가능성이 있습니다.

### copy_up

아래 층 파일을 쓰기용으로 열거나 소유자·권한 같은 메타데이터를 바꾸면(하드 링크를 만들 때 포함) 커널이 먼저 파일 전체를 위 층으로 복사합니다. 이것이 copy_up 입니다[1]. 복사할 때는 소유자·모드·mtime·심볼릭 링크 대상 같은 메타데이터를 같게 만들고, 내용을 복사한 뒤, 확장 속성을 복사합니다[1]. 읽기·쓰기로 열기만 하고 내용을 바꾸지 않아도 copy_up 이 일어날 수 있습니다[1].

아래 층 폴더 이름을 바꾸는 요청은 기본으로 `EXDEV` 오류가 되고, `mv` 같은 프로그램은 복사한 뒤 원래 것을 지우는 방식으로 처리합니다[1][5]. 그러면 위 층에는 새 이름의 폴더 전체와 옛 이름의 삭제 표시가 함께 남습니다.

## 증거로서 의미

증명하는 것은 다음과 같습니다.

- 컨테이너 쓰기 층 `diff/` 에 있는 일반 파일은 컨테이너가 새로 만들었거나, 이미지에 있던 파일을 쓰기용으로 열거나 메타데이터를 바꾼 결과입니다[1].
- 삭제 표시와 불투명 폴더는 컨테이너 안에서 그 이름을 지웠다는 기록입니다. 이미지 쪽 원본은 아래 층에 그대로 남아 있습니다[5].
- `trusted.overlay.origin` 이 붙은 파일은 아래 층에서 올라온 파일입니다[1]. 이미지에 있던 파일을 건드린 것인지, 새로 만든 것인지를 나누는 단서입니다.
- 초기화 층과 이미지 층의 `diff/` 는 컨테이너가 시작할 때 본 파일들입니다. 쓰기 층과 견주면 무엇이 달라졌는지 알 수 있습니다.

증명하지 못하는 것은 다음과 같습니다.

- 삭제 표시만으로는 지운 파일의 내용을 알 수 없습니다. 아래 층에 원본이 있으면 이미지 시점의 내용만 보이고, 컨테이너가 고친 뒤 지운 내용은 위 층에서 사라졌습니다. 이 내용은 하위 파일 시스템에서 되살려야 합니다([지운 파일 되살리기](../../../03-techniques/analysis/file-recovery.md)).
- copy_up 된 파일의 mtime 은 아래 층 값을 그대로 옮긴 것이라[1] "컨테이너 안에서 바꾼 시각" 이 아닙니다.
- `diff/` 에 있다는 사실만으로 누가 그 파일을 만들었는지는 알 수 없습니다. 컨테이너 안의 프로세스, `docker cp`, 호스트에서 `diff/` 를 직접 고친 경우를 이 폴더만으로는 가릴 수 없고, [셸 명령 기록](../../execution/shell-history/index.md) 이나 [감사 로그의 실행 기록](../../execution/auditd-execve.md) 으로 좁혀야 합니다.
- 볼륨과 바인드 마운트에 쓴 파일은 overlay 를 거치지 않으므로 `diff/` 에 없습니다. 볼륨 위치는 [Docker 허브](index.md) 에서 봅니다.

## 시각 해석

`diff/` 안 파일의 시각은 하위 파일 시스템 inode 의 시각이고, 저장 값은 UTC 기준입니다. 필드별 뜻은 [ext4](../../../01-foundations/filesystem/ext4/index.md) 와 [XFS](../../../01-foundations/filesystem/xfs.md) 를 봅니다.

| 대상 | 읽는 법 |
|---|---|
| 컨테이너가 새로 만든 파일 | 네 시각 모두 컨테이너 안에서 일어난 일을 가리킵니다 |
| copy_up 된 파일의 mtime | 아래 층에서 복사한 값입니다[1]. 이미지 시점의 mtime 이 나올 수 있습니다 |
| copy_up 된 파일의 ctime·생성 시각 | 위 층에 파일을 새로 만든 시각일 가능성이 있습니다. 같은 경로의 아래 층 파일과 견줘 확인합니다 |
| 삭제 표시 파일의 시각 | 삭제 표시를 만든 시각, 곧 컨테이너 안에서 지운 시각의 후보입니다 |
| 쓰기 층 폴더와 `-init` 폴더의 생성 시각 | 컨테이너를 만든 시각 근처입니다. `config.v2.json` 의 `Created` 와 맞춰 봅니다([컨테이너 설정과 로그](container-logs.md)) |

## 함정과 한계

- `merged/` 는 마운트 지점일 뿐입니다. 멈춘 컨테이너는 마운트를 풀면서 `merged/` 를 지우고[2], 디스크 이미지에서는 실행 중이던 컨테이너의 `merged/` 도 빈 폴더로 보입니다. `merged/` 가 비었다고 컨테이너가 비어 있는 것이 아니고, `diff/` 와 `lower` 로 다시 쌓아야 합니다.
- 확장 속성을 버리는 방식으로 복사하면 확장 속성 방식 삭제 표시와 불투명 폴더 표시가 사라집니다. 문자 장치 삭제 표시도 수집 방식에 따라 빠질 수 있으므로, 파일 시스템 이미지로 떠서 분석합니다([컨테이너 수집](../../../03-techniques/acquisition/container-acquisition.md), [권한·확장 속성](../../../01-foundations/filesystem/permissions-xattr.md)).
- `metacopy` 가 켜진 호스트라면 위 층 파일에 데이터가 없을 수 있습니다[1]. 내용은 아래 층 파일에서 읽어야 하고, Docker 가 이 기능을 쓰는지는 드라이버 상태의 `Using metacopy` 로 봅니다[2].
- `trusted.overlay.origin` 이 없다고 새로 만든 파일이라고 단정하지 않습니다. 같은 경로가 아래 층들의 `diff/` 에 있는지로 확인합니다.
- 마운트하지 않은 상태에서 위 층을 바꾸는 것은 overlay 규칙상 허용됩니다[1]. 따라서 호스트 권한이 있는 사람이 `diff/` 를 직접 고쳐도 overlay 쪽에는 이상 표시가 남지 않습니다.
- 라이브 호스트에서 `merged/` 를 복사하면 실행 중인 컨테이너가 쓰는 도중의 파일이 섞일 수 있습니다. `/var/lib/docker/` 안의 파일은 Docker 가 관리하므로 직접 고치지 않고[5] 복사본으로 분석합니다.

## 직접 분석해 보기

### 헥스로 한 번

ext4 에서 문자 장치 삭제 표시는 디렉터리 항목의 `file_type` 이 `0x3`(문자 장치)으로 보이고[6], 그 inode 의 `i_mode` 파일 종류 값은 `0x2000`(S_IFCHR) 입니다[7]. 아래는 명세로 만든 예시로, 쓰기 층 `diff/etc/` 폴더 블록 안의 디렉터리 항목 하나입니다.

```
51 3a 0c 00  14 00  0a  03  72 65 70 6f 72 74 2e 74 78 74  00 00
|inode      |rec_len|len|type|"report.txt"                  |채움
```

`inode` 는 0x000C3A51, `rec_len` 은 20바이트, 이름 길이는 10, `file_type` 이 `0x3` 입니다[6]. 컨테이너 쓰기 층 안에 문자 장치 항목이 있으면 삭제 표시 후보로 보고, inode 의 장치 번호가 0/0 인지 확인합니다[1].

확장 속성 표시는 root 권한으로 마운트한 검체에서 `getfattr -d -m '^trusted.overlay' -e hex 경로` 처럼 16진수로 읽습니다. 불투명 폴더라면 `trusted.overlay.opaque` 의 값이 `0x79`(문자 `y`)로 나옵니다[1].

### 공개 도구로 한 번

1. 검체를 읽기 전용으로 붙이고 `layerdb/mounts/컨테이너ID/mount-id` 로 쓰기 층 폴더를 찾습니다.
2. `find 쓰기층/diff -type c` 로 문자 장치 삭제 표시를, 크기 0 인 파일과 폴더의 확장 속성으로 나머지 표시를 찾습니다.
3. 컨테이너가 본 파일 시스템 전체가 필요하면 docker-explorer 의 `de.py -r 루트 mount 컨테이너ID 대상` 을 씁니다[8]. 이 도구는 위 층을 두지 않고 `ro,lowerdir=쓰기층diff:아래층들` 로 컨테이너 층을 맨 위 아래 층으로 올려 읽기 전용으로 붙이고, 볼륨과 바인드 마운트를 붙이는 명령도 함께 만듭니다[8]. 아래 층의 일반 삭제 표시는 overlay 가 늘 처리하므로[1] 이렇게 붙인 보기에서는 지운 파일이 보이지 않습니다. 지운 흔적은 2단계처럼 `diff/` 에서 따로 찾습니다.
4. container-explorer 는 lowerdir·upperdir 로 병합 보기를 만들고, 원본 이미지 대비 추가·수정·삭제된 파일과 새 실행 파일을 찾는 drift 명령을 제공합니다[9].
5. dissect.target 의 `docker.containers` 는 컨테이너마다 `image/overlay2/layerdb/mounts/컨테이너ID` 를 `mount_path` 로 알려 줍니다[10].

라이브 호스트라면 UAC 가 컨테이너마다 `docker diff` 결과를 모읍니다[12]. 메모리 이미지만 있다면 Volatility 3 의 `linux.mountinfo` 로 마운트 이름공간별 마운트 목록을 뽑고(`--mntns` 로 좁힘), 파일 시스템 종류가 `overlay` 인 줄을 찾습니다[11]. 이 플러그인의 옵션 칸에는 `ro`·`rw` 같은 공통 플래그만 나오고 `lowerdir`·`upperdir` 는 나오지 않으므로[11], 마운트 지점 `overlay2/레이어폴더/merged` 에서 쓰기 층 폴더 이름을 읽습니다[2]. 자세한 절차는 [메모리 분석](../../../03-techniques/analysis/memory-analysis.md) 을 봅니다.

## 교차 검증

- [이미지와 레이어](images-layers.md): `cache-id`·`mount-id` 로 폴더와 이미지·컨테이너를 잇습니다.
- [컨테이너 설정과 로그](container-logs.md): `Created`·`StartedAt` 과 쓰기 층 파일 시각을 맞춥니다. 표준 출력에 찍힌 명령과 `diff/` 에 생긴 파일을 견줍니다.
- [셸 명령 기록](../../execution/shell-history/index.md): 호스트의 `docker cp`·`docker exec` 명령과, 컨테이너 쓰기 층 `diff/root/` 등에 남은 셸 기록 파일을 함께 봅니다.
- [마운트 기록](../../devices/mounts.md): 수집 당시 overlay 마운트 목록이 남아 있다면 실행 중이던 컨테이너를 가려냅니다.
- [타임라인 만들기](../../../03-techniques/analysis/timeline.md): 쓰기 층 파일 시각을 호스트 로그와 시간순으로 합칩니다.

## 실습

직접 만든 실험용 가상 머신에 overlay2 방식 Docker 를 두고 컨테이너 하나를 띄웁니다. 컨테이너 안에서 파일을 하나 만들고, 이미지에 있던 설정 파일 하나를 고치고, 이미지에 있던 폴더 하나를 지운 뒤 디스크 이미지를 떠서 풀어 봅니다.

1. `layerdb/mounts/컨테이너ID/mount-id` 에서 시작해 쓰기 층 폴더와 `-init` 폴더를 찾을 수 있습니까?
2. 고친 설정 파일의 mtime 과 ctime 은 각각 무엇을 가리킵니까? 같은 경로의 아래 층 파일 mtime 과 견주면 어떻습니까?
3. 지운 폴더는 쓰기 층에 어떤 모양으로 남았습니까? 문자 장치입니까, 불투명 폴더입니까?
4. 새로 만든 파일과 고친 파일 가운데 `trusted.overlay.origin` 이 붙은 쪽은 어느 것입니까?
5. docker-explorer 로 컨테이너를 붙였을 때 지운 폴더가 보입니까? 보이지 않는다면 흔적을 어디서 찾습니까?

## 참고 문헌

1. Linux kernel, `Documentation/filesystems/overlayfs.rst` — https://github.com/torvalds/linux/blob/master/Documentation/filesystems/overlayfs.rst
2. moby/moby, `daemon/graphdriver/overlay2/overlay.go` — https://github.com/moby/moby/blob/master/daemon/graphdriver/overlay2/overlay.go
3. moby/moby, `daemon/internal/layer/layer_store.go` — https://github.com/moby/moby/blob/master/daemon/internal/layer/layer_store.go
4. moby/moby, `daemon/internal/layer/filestore.go` — https://github.com/moby/moby/blob/master/daemon/internal/layer/filestore.go
5. Docker 공식 문서, OverlayFS storage driver — https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/overlayfs-driver.md
6. Linux kernel, `Documentation/filesystems/ext4/directory.rst` — https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/directory.rst
7. Linux kernel, `Documentation/filesystems/ext4/inodes.rst` — https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/inodes.rst
8. google/docker-explorer, `README.md`, `docker_explorer/storage.py` — https://github.com/google/docker-explorer
9. google/container-explorer, `README.md` — https://github.com/google/container-explorer/blob/main/README.md
10. fox-it/dissect.target, `dissect/target/plugins/apps/container/docker.py` — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/container/docker.py
11. volatilityfoundation/volatility3, `volatility3/framework/plugins/linux/mountinfo.py` — https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/mountinfo.py
12. tclahr/uac, `artifacts/live_response/containers/docker.yaml` — https://github.com/tclahr/uac/blob/main/artifacts/live_response/containers/docker.yaml
