---
title: "containerd 와 Kubernetes 노드"
parent: "아티팩트 · 컨테이너와 가상화"
nav_order: 810
---

# containerd 와 Kubernetes 노드 (containerd·Kubernetes)

Kubernetes 노드에서는 kubelet 이 컨테이너 런타임(containerd 또는 CRI-O)에 컨테이너를 맡기고, 런타임은 이미지와 컨테이너 파일 시스템을 자기 저장소에, 컨테이너 표준 출력은 `/var/log/pods` 아래 로그 파일에 남깁니다.

## 무엇을 기록하나 · 왜 생기나

containerd 는 이미지를 받고 풀어서 컨테이너를 실행하는 데몬입니다[4]. 영구 데이터는 `root` 폴더에, 재부팅하면 남으면 안 되는 소켓·pid·실행 상태·마운트 지점은 `state` 폴더에 둡니다[1]. containerd 자체는 영구 데이터가 없고, 불러온 플러그인이 저마다 `root` 아래에 자기 폴더를 만들어 이미지 내용·메타데이터·스냅숏을 나눠 담습니다[1].

kubelet 은 파드(pod)를 노드에서 실제로 돌리는 에이전트입니다. kubelet 이 로그 파일 경로를 정해 런타임에 넘기면 런타임이 컨테이너의 stdout·stderr 를 그 파일에 쓰고, 파일 회전은 kubelet 이 맡습니다[18]. 그래서 노드 디스크에는 "어느 네임스페이스의 어느 파드가, 어떤 이미지로, 몇 번째 재시작에서 무엇을 출력했나" 가 파일 경로와 로그 줄로 남습니다.

Docker Engine 29.0 부터 새로 설치한 호스트도 이미지와 컨테이너 스냅숏을 `/var/lib/containerd` 에 두므로[29][30], 이 페이지의 containerd 구조 설명은 그런 Docker 호스트에도 그대로 쓰입니다. Docker 쪽 설명은 [Docker](docker/index.md) 에 있습니다.

## 위치와 버전별 차이

### containerd

| 위치 | 담긴 것 |
|---|---|
| `/etc/containerd/config.toml` | 기본 설정 파일. `containerd --config` 로 바꿀 수 있고[1], `imports = [...]` 로 다른 toml 파일을 불러올 수 있습니다[2] |
| `/var/lib/containerd` (`root`) | 이미지 blob, 메타데이터 DB, 스냅숏[1][2] |
| `/run/containerd` (`state`) | 소켓 `containerd.sock`, 실행 중인 태스크의 상태[1][2] |

`root` 와 `state` 의 위치는 설정 파일의 `root`·`state` 키나 `--root`·`--state` 옵션으로 옮길 수 있습니다[1][2]. 그래서 분석 대상에서는 설정 파일과 서비스 단위 파일의 실행 줄을 먼저 읽어 실제 경로를 정합니다. 단위 파일 읽는 법은 [systemd 서비스와 타이머](../persistence/systemd-units.md) 에 있습니다.

### Kubernetes 런타임별 저장 위치

| 항목 | containerd | CRI-O |
|---|---|---|
| 이미지·컨테이너 저장소 | `/var/lib/containerd`[1] | `/var/lib/containers/storage`, 저장 드라이버 `overlay`. 기본값은 `/etc/containers/storage.conf` 에서 읽습니다[10] |
| 실행 상태 | `/run/containerd`[1] | `/var/run/containers/storage`[10] |
| 파드 로그 | kubelet 이 정한 `/var/log/pods` 아래[18] | kubelet 이 경로를 주지 않으면 `/var/log/crio/pods`[10] |
| 로그 줄 쓰는 곳 | containerd CRI 플러그인[9] | conmon[11] |

CRI-O 저장소는 Podman 과 같은 containers-storage 형식이라, 폴더 구조는 [Podman](podman.md) 에서 봅니다.

### kubelet (kubeadm 으로 설치한 노드 기준)

| 위치 | 담긴 것 |
|---|---|
| `/var/lib/kubelet` | kubelet 루트 폴더. `--root-dir` 로 바꿀 수 있습니다[17] |
| `/var/lib/kubelet/config.yaml` | kubelet 설정(KubeletConfiguration)[20] |
| `/var/lib/kubelet/instance-config.yaml` | kubeadm 이 찾은 CRI 소켓 경로 같은 노드별 설정[20] |
| `/var/lib/kubelet/kubeadm-flags.env` | kubeadm 이 만든 kubelet 실행 인자 `KUBELET_KUBEADM_ARGS`[20] |
| `/var/lib/kubelet/pki` | kubelet 인증서 폴더[17] |
| `/etc/kubernetes/kubelet.conf` | kubelet 이 API 서버에 접속할 때 쓰는 kubeconfig[20] |
| `/etc/kubernetes/bootstrap-kubelet.conf` | TLS 부트스트랩용 kubeconfig. 부트스트랩이 끝나면 kubeadm 이 지웁니다[20] |
| `/usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf` | kubeadm 패키지가 까는 kubelet 단위 드롭인[20] |
| `/etc/crictl.yaml` | `crictl` 이 붙을 런타임 소켓(`runtime-endpoint`)[25] |

사용자가 덧붙이는 kubelet 인자 `KUBELET_EXTRA_ARGS` 를 담는 파일만 패키지 형식에 따라 다릅니다[20].

| 배포판 계열 | kubelet 추가 인자 파일 |
|---|---|
| Debian·Ubuntu (DEB) | `/etc/default/kubelet` |
| RHEL·Fedora (RPM) | `/etc/sysconfig/kubelet` |

kubelet 설정 드롭인 폴더는 기본으로 쓰지 않고 `--config-dir` 을 줄 때만 읽으며, 그 폴더의 `.conf` 파일을 이름 순으로 겹쳐 적용합니다[22].

## 구조

### containerd `root` 폴더

```
/var/lib/containerd/
├── io.containerd.content.v1.content/
│   ├── blobs/sha256/          압축 레이어·매니페스트·이미지 설정 (파일 이름 = 내용의 sha256)
│   └── ingest/                받는 중인 내용
├── io.containerd.metadata.v1.bolt/
│   └── meta.db                이미지·컨테이너·스냅숏 메타데이터 (BoltDB)
├── io.containerd.runtime.v2.task/
│   └── 네임스페이스/
└── io.containerd.snapshotter.v1.overlayfs/
    ├── metadata.db
    └── snapshots/1/fs, 2/fs, …  레이어를 풀어 놓은 내용
```

`blobs/sha256` 에는 받은 원본(gzip 으로 묶은 tar 레이어 등)이 내용의 sha256 을 이름으로 들어 있고, `snapshots/번호/fs` 에는 레이어를 풀어 앞 층 위에 적용한 내용이 들어 있습니다[1][4]. 기본 스냅숏 저장기(snapshotter)는 `overlayfs` 이고, Docker 의 overlay2 와 비슷하지만 이름은 overlay2 가 아닙니다[4][5]. `btrfs`·`zfs` 같은 다른 저장기는 `io.containerd.snapshotter.v1.btrfs` 처럼 저장기 이름의 폴더를 따로 씁니다[5].

스냅숏 폴더 이름은 1, 2, 3 같은 번호입니다[4]. 스냅숏의 키(이름)는 레이어를 앞 층에 적용한 결과의 해시라서, blob 의 해시와 다르고 맨 아래 층을 빼면 압축을 푼 tar 의 해시와도 다릅니다[4]. 스냅숏마다 부모가 하나 있고 맨 아래 층만 부모가 없어 전체가 트리를 이룹니다[4]. 그래서 "이 레이어 해시가 어느 폴더인가" 는 폴더 이름으로 알 수 없고, 스냅숏 목록과 폴더 경로를 함께 보여 주는 도구(아래 container-explorer 의 `list snapshots -P`)로 이어 붙입니다. overlay 층이 겹치는 원리와 지운 파일 표시(whiteout)는 [overlay 파일 시스템](docker/overlay2.md) 설명과 같습니다.

### 네임스페이스

containerd 의 모든 API 호출에는 네임스페이스가 붙고, 이미지 이름과 메타데이터는 네임스페이스마다 따로 있으며 내용(blob)만 주소로 함께 씁니다[3]. Kubernetes CRI 는 `k8s.io` 네임스페이스를 씁니다[8]. Docker 가 containerd 이미지 저장소를 쓸 때의 네임스페이스는 `moby` 입니다([Docker](docker/index.md)). `ctr` 은 네임스페이스를 주지 않으면 `default` 만 보여 주므로[3], 라이브 호스트에서 `ctr containers ls` 가 비어 있어도 `ctr -n k8s.io containers ls` 에는 컨테이너가 나올 수 있습니다. 네임스페이스는 관리용 구분이고 보안 경계가 아닙니다[3].

### `state` 폴더

실행 중인 컨테이너마다 `/run/containerd/io.containerd.runtime.v2.task/네임스페이스/컨테이너ID/` 에 OCI 런타임 설정 `config.json`, `init.pid`, `log.json`, 컨테이너 루트 파일 시스템을 마운트한 `rootfs/` 가 있습니다[1]. 재부팅 뒤에 남지 않는 데이터를 두는 곳이라[1] 전원을 끈 뒤 뜬 디스크 이미지에는 없습니다.

### 파드 로그 경로

kubelet 은 파드마다 `네임스페이스_파드이름_파드UID` 폴더를 만들고, 그 아래 컨테이너 이름 폴더에 `재시작횟수.log` 로 로그를 둡니다[12].

```
/var/log/pods/default_web-7d9f_0f1e2d3c-4b5a-6978-8a9b-0c1d2e3f4a5b/nginx/0.log
/var/log/containers/web-7d9f_default_nginx-3a4b5c6d7e8f….log  →  위 파일로 가는 심볼릭 링크
```

위 경로는 만든 예시입니다. `/var/log/containers/` 의 링크 이름은 `파드이름_네임스페이스_컨테이너이름-컨테이너ID.log` 이고[13][14], ext4 파일 이름 한도를 넘지 않게 255자에서 자릅니다[13]. 옛 kubelet 은 파드 폴더를 `/var/log/pods/파드UID` 로만 만들었고, 지금 코드도 이 옛 이름을 읽어 들입니다[12].

### CRI 로그 줄 형식

한 줄은 `시각 스트림 태그 내용` 을 공백으로 이은 모양입니다[15].

```
2026-03-14T02:15:07.123456789Z stdout P 한 줄이 길어 앞부분만 먼저 쓴 조각
2026-03-14T02:15:07.123456789Z stdout F 조각의 나머지
2026-03-14T02:15:08.000000001Z stderr F error: connection refused
```

만든 예시입니다. 스트림은 `stdout` 이나 `stderr` 이고, 태그 `P` 는 긴 줄을 나눈 조각, `F` 는 줄의 끝입니다[15]. containerd 는 설정 `max_container_log_line_size`(기본 16384바이트)를 넘는 줄을 `P` 조각으로 나눠 씁니다[7][9]. kubelet 은 이 CRI 형식과 Docker 의 JSON 로그 형식을 둘 다 읽습니다[15].

### 로그 회전

kubelet 이 컨테이너 로그를 회전하고, 설정 `containerLogMaxSize`(기본 10Mi)와 `containerLogMaxFiles`(기본 5)로 크기와 파일 수를 정합니다[18]. 회전하면 현재 파일을 `0.log.20260314-021507` 처럼 `원래이름.날짜-시각` 으로 바꾸고, 그보다 오래된 회전 파일은 gzip 으로 압축해 `.gz` 를 붙이며, 압축 중에는 `.tmp` 임시 파일이 생깁니다[16]. 파일 수가 한도를 넘으면 가장 오래된 것부터 지웁니다[16].

### 정적 파드 매니페스트

kubelet 설정의 `staticPodPath`(옛 방식은 `--pod-manifest-path`) 폴더를 kubelet 이 주기적으로 살펴, 파일이 생기면 파드를 만들고 없어지면 지웁니다[21]. 점(.)으로 시작하지 않는 파일은 확장자와 관계없이 모두 읽으므로 `kube-apiserver.yaml.backup` 같은 백업 파일도 파드로 뜹니다[21]. 폴더는 예를 들어 `/etc/kubernetes/manifests` 로 정합니다[21].

### 컨테이너 체크포인트

kubelet API `POST /checkpoint/{namespace}/{pod}/{container}` 를 부르면 kubelet 이 런타임에 체크포인트를 요청하고, 결과를 kubelet 루트 아래 `checkpoints` 폴더(기본 `/var/lib/kubelet/checkpoints`)에 `checkpoint-파드풀네임-컨테이너이름-시각.tar` 로 저장합니다[24]. 이 tar 에는 보통 컨테이너 안 모든 프로세스의 메모리 페이지가 들어 있어 비밀 값이나 암호 키가 담길 수 있고, tar 안의 구성은 런타임마다 다릅니다[24]. 이 기능을 켜는 기능 게이트 `ContainerCheckpoint` 는 1.25~1.29 에서 알파(기본 꺼짐), 1.30 부터 베타(기본 켜짐)입니다[24].

## 증거로서 의미

### 증명하는 것

- 이 노드에서 특정 네임스페이스·파드·컨테이너가 돌았다는 것. 파드 로그 폴더 이름에 네임스페이스·파드 이름·파드 UID·컨테이너 이름이, 파일 이름에 재시작 횟수가 들어 있습니다[12].
- 컨테이너가 stdout·stderr 로 무엇을 내보냈고 런타임이 그 줄을 언제 받았는지.
- 어떤 이미지 내용이 노드의 containerd 저장소에 있었는지(`blobs/sha256`, `meta.db`).
- 정적 파드 폴더에 어떤 매니페스트가 있었는지. 여기 놓인 파일은 kubelet 이 폴더를 살펴보다가 곧바로 파드로 만듭니다[21].
- 노드에 체크포인트 tar 가 있으면, 그 시각 무렵에 누군가 kubelet 체크포인트 API 를 불렀다는 것[24].

### 증명하지 못하는 것

- 클러스터에서 누가 파드를 만들고 지웠는지. 이 기록은 API 서버 감사 로그에 있고, 감사 로그는 `kube-apiserver` 에 `--audit-policy-file` 을 주지 않으면 아예 남지 않습니다[23]. 감사 로그는 JSON Lines 형식이고 `--audit-log-path` 로 정한 파일(예: `/var/log/kubernetes/audit/audit.log`)에 쓰므로[23], API 서버가 도는 컨트롤 플레인 노드에서 찾습니다.
- 컨테이너 안에서 누가 무엇을 입력했는지. 표준 출력에 찍히지 않은 명령은 파드 로그에 없습니다.
- 파드가 퇴출(evict)된 뒤의 로그. 파드를 퇴출하면 그 컨테이너와 로그도 함께 사라지고, 재시작한 컨테이너는 종료된 것 하나와 그 로그만 남깁니다[18].
- 회전으로 지워진 로그 내용. 기본값이면 컨테이너 하나에 파일 다섯 개까지만 남습니다[18].

## 시각 해석

| 값 | 형식 | 시간대 | 바뀌는 때 |
|---|---|---|---|
| containerd 가 쓴 로그 줄 시각 | RFC3339Nano | 프로세스 시간대. UTC 로 도는 노드면 `Z` 로 끝납니다[9] | 런타임이 줄을 받은 순간(`time.Now()`)[9] |
| CRI-O(conmon)가 쓴 로그 줄 시각 | `2026-03-14T11:15:07.123456789+09:00` 형식, 나노초 9자리 | 현지 시각에 `±HH:MM` 오프셋. UTC 라도 `Z` 가 아니라 `+00:00` 입니다[11] | conmon 이 줄을 받은 순간[11] |
| 회전 파일 이름의 `날짜-시각` | Go 형식 `20060102-150405` | 시간대 표시 없음. kubelet 프로세스의 현지 시각입니다[16] | 회전한 순간 |
| 체크포인트 tar 이름의 시각 | 실제 파일 이름으로 확인 | 실제 데이터로 확인 | 체크포인트를 만든 순간[24] |

두 런타임 모두 로그 줄 시각은 애플리케이션이 찍은 시각이 아니라 런타임이 파이프에서 줄을 읽은 시각입니다. 애플리케이션이 내용 안에 자기 시각을 찍었다면 두 시각을 나란히 적습니다. 회전 파일 이름의 시각은 회전한 순간이라, 파일 안 마지막 줄 시각과 같거나 그보다 뒤입니다[16]. 시간대가 적히지 않은 값은 노드의 시간대 설정([호스트 이름·시간대·로캘](../system-info/hostname-timezone.md))으로 풀고, 시각 값 일반은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

## 함정과 한계

- **`/var/log/containers/*.log` 는 링크일 뿐입니다.** 링크만 복사하면 내용이 없으므로 `/var/log/pods` 를 함께 확보합니다. UAC 는 `/var/log` 를 파일과 심볼릭 링크 모두(`file_type: [f, l]`) 파일당 1GB 한도로 모읍니다[27].
- **`state` 는 전원을 끄면 사라집니다.** containerd 의 `/run/containerd` 는 재부팅 뒤에 남지 않는 자리이고[1], CRI-O 는 상태를 `runroot`(`/var/run/containers/storage`)에 둡니다[10]. 실행 중인 태스크의 `config.json`·`init.pid` 가 필요하면 라이브 상태에서 먼저 모읍니다([컨테이너 수집](../../03-techniques/acquisition/container-acquisition.md)).
- **CRI-O 는 재부팅 뒤 컨테이너를 지울 수 있습니다.** `version_file`(`/var/run/crio/version`)로 재부팅을 알아채면 컨테이너를 지우고, 정상 종료 표시 파일 `clean_shutdown_file`(`/var/lib/crio/clean.shutdown`)이 없으면 저장소를 지웁니다[10]. 전원 차단 뒤 켰다가 끈 노드라면 컨테이너 흔적이 이미 지워졌을 수 있습니다.
- **containerd 가비지 컬렉터가 쓰지 않는 자원을 지웁니다.** 쓰이지도 않고 리스(lease)에도 잡히지 않은 스냅숏·내용은 삭제 대상입니다[6]. 이미지를 지운 뒤 `blobs/sha256` 에 해당 blob 이 없다고 해서 받은 적이 없다고 볼 수 없습니다.
- **네임스페이스를 빼먹으면 컨테이너가 없는 것처럼 보입니다**[3].
- **라이브 호스트에서 containerd 폴더를 건드리면 탈이 납니다.** 외부 프로그램이 `root`·`state` 폴더를 읽거나 감시하다가 containerd 정리 작업에 `EBUSY` 나 stale file handle 오류를 일으킨 일이 있습니다[1]. 라이브 수집은 명령 출력(`crictl`, `ctr`)으로 하고, 폴더 자체는 디스크 이미지로 확보합니다.
- **도구가 containerd 를 다 읽지는 않습니다.** dissect.target 의 컨테이너 플러그인 폴더에는 Docker 와 Podman 플러그인만 있습니다[28]. containerd 저장소는 `meta.db` 를 직접 읽는 container-explorer 로 봅니다[26].
- **정적 파드 폴더는 지속성 흔적 점검 대상입니다.** 백업처럼 보이는 파일도 파드로 뜨므로[21], 확장자와 관계없이 폴더 안 파일을 모두 봅니다([무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md)).

## 직접 분석해 보기

### 헥스로 한 번

CRI 로그 줄은 문자열이라 헥스로 보면 구분자가 그대로 드러납니다. 아래는 명세[15]로 만든 한 줄 `2026-03-14T02:15:07.123456789Z stdout F hello` 입니다.

```
00000000  32 30 32 36 2d 30 33 2d  31 34 54 30 32 3a 31 35  |2026-03-14T02:15|
00000010  3a 30 37 2e 31 32 33 34  35 36 37 38 39 5a 20 73  |:07.123456789Z s|
00000020  74 64 6f 75 74 20 46 20  68 65 6c 6c 6f 0a        |tdout F hello.|
```

0x00~0x1D 가 시각이고 끝의 `5a`(Z)가 UTC 표시입니다. 0x1E 의 `20` 뒤 0x1F~0x24 가 스트림 `stdout`, 0x26 의 `46` 이 태그 `F`, 0x28 부터 내용, 마지막 `0a` 가 줄 끝입니다. CRI-O 노드라면 0x1D 자리에 `5a` 대신 `2b 30 30 3a 30 30`(`+00:00`) 같은 오프셋이 옵니다[11]. 태그가 `50`(P)인 줄은 다음 줄과 이어 붙여 읽습니다.

### 공개 도구로 한 번

오프라인 디스크 이미지를 `/mnt/disk1` 에 읽기 전용으로 붙였다면 container-explorer 로 containerd 저장소를 읽습니다[26].

```
ce --image-root /mnt/disk1 list namespaces
ce --image-root /mnt/disk1 list containers -s
ce --image-root /mnt/disk1 list images
ce --image-root /mnt/disk1 list snapshots -P
ce --image-root /mnt/disk1 inspect 컨테이너ID
```

`--image-root` 를 주면 `/var/lib/containerd` 를 그 아래에서 찾습니다[26]. `list containers` 는 기본으로 `pause` 같은 Kubernetes 보조 컨테이너를 숨기므로, 전부 보려면 `-s` 를 붙입니다[26]. `list snapshots -P` 는 스냅숏 번호 폴더의 전체 경로를 보여 줘서 레이어와 `snapshots/번호/fs` 를 잇는 데 씁니다[26]. `mount` 로 컨테이너 파일 시스템을 병합해 붙일 수 있고, 원본 이미지와 달라진 파일을 찾는 기능도 있습니다[26].

라이브 노드에서는 `crictl pods`, `crictl ps -a`, `crictl images`, `crictl logs 컨테이너ID` 로 런타임이 아는 파드·컨테이너·이미지·로그를 봅니다[25]. `crictl ps -a` 는 종료된(`Exited`) 컨테이너까지 보여 줍니다[25]. UAC 는 containerd 가 있으면 `containerd config dump` 출력을 모읍니다[27]. kubelet·런타임 자신의 로그는 systemd 노드에서 저널에 있어 `journalctl -u kubelet` 으로 봅니다[18][19]([systemd 저널](../../01-foundations/logging/systemd-journal/index.md)).

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) | kubelet·containerd 서비스의 시작·중지·오류 시각과 로그 줄 시각이 맞는지 |
| [셸 명령 기록](../execution/shell-history/index.md), [감사 로그의 실행 기록](../execution/auditd-execve.md) | 노드에서 `kubectl`·`crictl`·`ctr` 을 친 계정과 시각 |
| [systemd 서비스와 타이머](../persistence/systemd-units.md) | kubelet 드롭인·containerd 단위에 덧붙은 실행 인자 |
| [Docker](docker/index.md) | 같은 호스트의 Docker 가 containerd 저장소(`moby` 네임스페이스)를 함께 쓰는지 |
| [Podman](podman.md) | CRI-O 노드의 containers-storage 폴더 구조 |
| [메모리 분석](../../03-techniques/analysis/memory-analysis.md) | 체크포인트 tar 나 메모리 이미지에서 컨테이너 프로세스 확인 |
| [타임라인 만들기](../../03-techniques/analysis/timeline.md) | 파드 로그 줄, 회전 파일 이름, 스냅숏 폴더의 파일 시스템 시각을 한 줄로 늘어놓기 |

## 실습

kubeadm 으로 만든 Kubernetes 노드의 디스크 이미지(공개 증거물 이미지나 직접 만든 시험 노드)로 다음 질문을 풀어 봅니다.

1. `/etc/containerd/config.toml` 과 서비스 단위 파일에서 실제 `root`·`state` 경로를 찾고, 기본값과 다른지 확인합니다.
2. `/var/log/pods` 의 폴더 이름만으로 노드에서 돈 네임스페이스·파드·컨테이너 목록을 만들고, 재시작 횟수가 1 이상인 컨테이너를 고릅니다.
3. `/var/log/containers` 의 링크 가운데 가리키는 파일이 없는 것을 찾고, 그 파드가 퇴출·삭제되었을 가능성을 저널의 kubelet 줄과 맞춰 봅니다.
4. 한 컨테이너의 `0.log` 와 회전 파일(`0.log.날짜-시각`, `.gz`)을 시간 순으로 이어 붙이고, `P` 조각을 합친 뒤 첫 줄과 마지막 줄 시각을 적습니다.
5. 정적 파드 폴더에 점으로 시작하지 않는 파일이 몇 개 있는지, 그 가운데 `kube-system` 기본 구성 요소가 아닌 것이 있는지 봅니다.
6. `/var/lib/kubelet/checkpoints` 에 tar 가 있는지 보고, 있으면 파일 이름에서 파드·컨테이너를 읽습니다.

## 참고 문헌

1. containerd/containerd, `docs/ops.md`. https://github.com/containerd/containerd/blob/main/docs/ops.md
2. containerd/containerd, `docs/man/containerd-config.toml.5.md`. https://github.com/containerd/containerd/blob/main/docs/man/containerd-config.toml.5.md
3. containerd/containerd, `docs/namespaces.md`. https://github.com/containerd/containerd/blob/main/docs/namespaces.md
4. containerd/containerd, `docs/content-flow.md`. https://github.com/containerd/containerd/blob/main/docs/content-flow.md
5. containerd/containerd, `docs/snapshotters/README.md`. https://github.com/containerd/containerd/blob/main/docs/snapshotters/README.md
6. containerd/containerd, `docs/garbage-collection.md`. https://github.com/containerd/containerd/blob/main/docs/garbage-collection.md
7. containerd/containerd, `docs/cri/config.md`. https://github.com/containerd/containerd/blob/main/docs/cri/config.md
8. containerd/containerd, `internal/cri/constants/constants.go`. https://github.com/containerd/containerd/blob/main/internal/cri/constants/constants.go
9. containerd/containerd, `internal/cri/io/logger.go`. https://github.com/containerd/containerd/blob/main/internal/cri/io/logger.go
10. cri-o/cri-o, `docs/crio.conf.5.md`. https://github.com/cri-o/cri-o/blob/main/docs/crio.conf.5.md
11. containers/conmon, `src/ctr_logging.c`. https://github.com/containers/conmon/blob/main/src/ctr_logging.c
12. kubernetes/kubernetes, `pkg/kubelet/kuberuntime/helpers.go`. https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/kuberuntime/helpers.go
13. kubernetes/kubernetes, `pkg/kubelet/kuberuntime/legacy.go`. https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/kuberuntime/legacy.go
14. kubernetes/kubernetes, `pkg/kubelet/container/runtime.go`. https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/container/runtime.go
15. kubernetes/kubernetes, `staging/src/k8s.io/cri-client/pkg/logs/logs.go`. https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/cri-client/pkg/logs/logs.go
16. kubernetes/kubernetes, `pkg/kubelet/logs/container_log_manager.go`. https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/logs/container_log_manager.go
17. kubernetes/kubernetes, `cmd/kubelet/app/options/options.go`, `pkg/kubelet/kubeletconfig/defaults.go`, `pkg/kubelet/kubelet_getters.go`. https://github.com/kubernetes/kubernetes/tree/master
18. Kubernetes Documentation, "Logging Architecture" (`content/en/docs/concepts/cluster-administration/logging.md`). https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/cluster-administration/logging.md
19. Kubernetes Documentation, "System Logs" (`content/en/docs/concepts/cluster-administration/system-logs.md`). https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/cluster-administration/system-logs.md
20. Kubernetes Documentation, "Configuring each kubelet in your cluster using kubeadm" (`content/en/docs/setup/production-environment/tools/kubeadm/kubelet-integration.md`). https://github.com/kubernetes/website/blob/main/content/en/docs/setup/production-environment/tools/kubeadm/kubelet-integration.md
21. Kubernetes Documentation, "Create static Pods" (`content/en/docs/tasks/configure-pod-container/static-pod.md`). https://github.com/kubernetes/website/blob/main/content/en/docs/tasks/configure-pod-container/static-pod.md
22. Kubernetes Documentation, "Set Kubelet Parameters Via A Configuration File" (`content/en/docs/tasks/administer-cluster/kubelet-config-file.md`). https://github.com/kubernetes/website/blob/main/content/en/docs/tasks/administer-cluster/kubelet-config-file.md
23. Kubernetes Documentation, "Auditing" (`content/en/docs/tasks/debug/debug-cluster/audit.md`). https://github.com/kubernetes/website/blob/main/content/en/docs/tasks/debug/debug-cluster/audit.md
24. Kubernetes Documentation, "Kubelet Checkpoint API" (`content/en/docs/reference/node/kubelet-checkpoint-api.md`), feature gate `ContainerCheckpoint` (`content/en/docs/reference/command-line-tools-reference/feature-gates/ContainerCheckpoint.md`). https://github.com/kubernetes/website/tree/main/content/en/docs/reference
25. Kubernetes Documentation, "Debugging Kubernetes nodes with crictl" (`content/en/docs/tasks/debug/debug-cluster/crictl.md`). https://github.com/kubernetes/website/blob/main/content/en/docs/tasks/debug/debug-cluster/crictl.md
26. google/container-explorer, `README.md`. https://github.com/google/container-explorer/blob/main/README.md
27. tclahr/uac, `artifacts/live_response/containers/containerd.yaml`, `artifacts/files/logs/var_log.yaml`. https://github.com/tclahr/uac/tree/main/artifacts
28. fox-it/dissect.target, `dissect/target/plugins/apps/container/`. https://github.com/fox-it/dissect.target/tree/main/dissect/target/plugins/apps/container
29. Docker Docs, "containerd image store with Docker Engine" (`content/manuals/engine/storage/containerd.md`). https://github.com/docker/docs/blob/main/content/manuals/engine/storage/containerd.md
30. Docker Docs, "Docker daemon configuration overview" (`content/manuals/engine/daemon/_index.md`). https://github.com/docker/docs/blob/main/content/manuals/engine/daemon/_index.md
