---
title: "컨테이너 설정과 로그"
parent: "Docker"
grand_parent: "아티팩트 · 컨테이너와 가상화"
nav_order: 790
---

# 컨테이너 설정과 로그 (Container Config·Logs)

Docker 컨테이너 하나마다 데이터 루트의 `containers/컨테이너ID/` 폴더에 설정·상태 파일과 표준 출력 로그가 쌓이고, 여기서 컨테이너를 만든 시각, 마지막으로 시작·종료한 시각, 실행한 명령, 컨테이너가 화면에 내보낸 내용을 읽습니다.

## 무엇을 기록하나 · 왜 생기나

`docker run` 이나 `docker create` 로 컨테이너를 만들면 데몬은 컨테이너 설정과 상태를 `config.v2.json` 에, 포트·마운트·로그 드라이버 같은 호스트 쪽 설정을 `hostconfig.json` 에 따로 적습니다[1]. 컨테이너가 표준 출력(stdout)과 표준 오류(stderr)로 내보낸 줄은 데몬이 받아서 로그 드라이버 (logging driver) 로 넘기고, 드라이버가 `json-file` 이나 `local` 이면 같은 폴더 안의 파일로 남습니다[1][11].

조사에서는 "이 컨테이너는 어떤 이미지로, 어떤 명령과 환경 변수로, 언제 만들어져 언제 돌았나", "웹 서버 컨테이너가 어떤 요청을 받았나" 를 이 파일들로 답합니다. 컨테이너를 만든 이미지 쪽 정보는 [이미지와 레이어](images-layers.md), 컨테이너가 바꾼 파일은 [overlay 파일 시스템](overlay2.md) 에서 봅니다.

## 위치와 버전별 차이

컨테이너 폴더는 데이터 루트 바로 아래 `containers/` 에 있습니다[5]. 기본 데이터 루트라면 `/var/lib/docker/containers/컨테이너ID/` 이고, rootless 모드·snap 설치·`data-root` 로 옮긴 경우의 데이터 루트는 [Docker 허브](index.md) 의 표를 따릅니다. Docker Engine 29.0 이상을 새로 설치해 containerd 이미지 저장소를 쓰는 호스트에서도 이미지와 컨테이너 파일 시스템만 `/var/lib/containerd` 로 가고, 이 컨테이너 폴더는 데이터 루트에 그대로 있습니다[5].

폴더 안에 어떤 로그 파일이 생기는지는 로그 드라이버가 정합니다.

| 로그 드라이버 | 로그가 남는 곳 | 회전 기본값 |
|---|---|---|
| `json-file` (기본값[11]) | `컨테이너ID-json.log`[1] | 회전 없음. `max-size` 기본 -1(무제한), `max-file` 기본 1, `compress` 기본 false[11][12] |
| `local` | `local-logs/container.log`[1] | 파일 하나 20MB, 5개까지, 회전한 파일은 압축[9][13] |
| `journald` | 호스트의 systemd 저널[14] | 저널 설정을 따름 |
| 읽기를 지원하지 않는 드라이버 | 드라이버가 보내는 곳, 그리고 이중 로깅 캐시 `container-cached.log`[1][15] | 캐시는 5개 × 20MB(압축 전)[15] |

기본 드라이버는 `/etc/docker/daemon.json` 의 `log-driver`·`log-opts` 로 바꾸고, 컨테이너마다 `docker run --log-driver` 로 따로 정할 수도 있습니다[11]. 기본 드라이버를 바꿔도 이미 만든 컨테이너는 만들 때의 드라이버와 옵션을 계속 씁니다[11]. 그래서 한 호스트 안에서도 컨테이너마다 로그 형식이 다를 수 있고, 컨테이너별 실제 설정은 `hostconfig.json` 의 `LogConfig` 에서 확인합니다[1][4]. 실행 중인 호스트에서는 `docker info` 의 LoggingDriver 값으로 데몬 기본값을 봅니다[11].

## 구조

### 컨테이너 폴더

| 파일·폴더 | 내용 |
|---|---|
| `config.v2.json` | 컨테이너 설정과 상태[1] |
| `hostconfig.json` | 호스트 쪽 설정. `config.v2.json` 에는 이 내용이 들어가지 않습니다[1] |
| `컨테이너ID-json.log`, `.1`, `.2` … | json-file 로그와 회전된 파일[1][8] |
| `local-logs/container.log` | local 드라이버 로그[1] |
| `container-cached.log` | 이중 로깅 캐시[1] |
| `checkpoints/`, `mounts/` | 체크포인트, 컨테이너 전용 마운트[1] |

hostname·hosts·resolv.conf 로 쓰는 파일의 경로는 `config.v2.json` 의 `HostnamePath`·`HostsPath`·`ResolvConfPath` 필드에 적혀 있습니다[1]. 파일 이름은 실제 데이터에서 이 필드로 확인합니다.

### config.v2.json

JSON 한 덩어리이고, 조사에 쓰는 필드는 다음과 같습니다[1][2][3].

| 필드 | 뜻 |
|---|---|
| `ID` | 64자리 컨테이너 ID. 폴더 이름과 같습니다 |
| `Name` | 컨테이너 이름. 앞에 `/` 가 붙습니다 |
| `Created` | 컨테이너를 만든 시각 |
| `Path`, `Args` | 컨테이너 안에서 처음 실행한 파일과 인자 |
| `Config` | `Image`(이미지 이름), `Env`(환경 변수), `Cmd`, `Hostname`, `Labels`, `ExposedPorts` 등 |
| `Image` | 이미지 ID. 코드의 필드 이름은 ImageID 이지만 JSON 키는 `Image` 입니다 |
| `NetworkSettings` | 네트워크와 실제 포트 연결(`Ports`) |
| `LogPath` | json-file 로그 경로. local 드라이버는 이 값을 채우지 않습니다 |
| `MountPoints` | 볼륨·바인드 마운트의 원본과 컨테이너 안 경로 |
| `Driver` | 저장소 드라이버 이름(예: `overlay2`) |
| `RestartCount`, `HasBeenStartedBefore`, `HasBeenManuallyStopped` | 재시작 횟수, 한 번이라도 시작했는지, 사용자가 직접 멈췄는지 |
| `AppArmorProfile`, `SeccompProfile`, `NoNewPrivileges` | 보안 옵션 |
| `State` | `Running`, `Paused`, `Restarting`, `OOMKilled`, `Dead`, `Pid`, `ExitCode`, `Error`, `StartedAt`, `FinishedAt`, `Health` |

`State` 의 `Running` 과 `Paused` 는 동시에 참일 수 있습니다. 일시 정지한 컨테이너는 프로세스를 끝내지 않은 채로 얼린 것이기 때문입니다[2]. 아래는 필드 일부만 추린 만든 예시입니다.

```json
{"ID":"4be1...(64자리)","Created":"2026-03-02T01:10:44.918273645Z","Path":"/docker-entrypoint.sh","Args":["nginx","-g","daemon off;"],
 "Config":{"Hostname":"4be1a0c3d2f9","Image":"example/web:1.0","Env":["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"]},
 "Image":"sha256:3f1c...(64자리)","Name":"/web01","Driver":"overlay2",
 "State":{"Running":false,"Paused":false,"Pid":0,"ExitCode":137,"StartedAt":"2026-03-02T01:10:45.201774310Z","FinishedAt":"2026-03-02T03:42:09.66810952Z"}}
```

### hostconfig.json

`docker run` 에 준 호스트 쪽 옵션이 들어 있습니다. 조사에서 자주 보는 키는 `Binds`(호스트 폴더 바인드), `Mounts`, `PortBindings`(호스트 포트 연결), `NetworkMode`, `PidMode`, `Privileged`, `CapAdd`, `RestartPolicy`, `AutoRemove`, `LogConfig`(로그 드라이버와 옵션)입니다[4]. `Binds` 로 호스트 폴더를 연결한 컨테이너는 그 폴더의 파일을 컨테이너 안에서 바꿀 수 있으므로, 컨테이너 쓰기 층뿐 아니라 연결된 호스트 폴더의 파일 시각도 함께 봅니다.

### json-file 로그

한 줄에 JSON 객체 하나가 있습니다[12]. 필드는 `log`(내보낸 줄, 줄 바꿈 포함), `stream`(`stdout` 또는 `stderr`), `time`, 그리고 `labels`·`env`·`tag` 로그 옵션을 켰을 때만 붙는 `attrs` 입니다[7]. `time` 은 RFC3339Nano 형식 문자열입니다[7]. 아래는 만든 예시입니다.

```json
{"log":"192.0.2.44 - - [02/Mar/2026:01:15:07 +0000] \"GET /login HTTP/1.1\" 200 512\n","stream":"stdout","time":"2026-03-02T01:15:07.482913004Z"}
```

`max-size` 를 정하면 파일이 그 크기에 이를 때 회전합니다. 현재 파일은 `컨테이너ID-json.log` 이고, 이전 파일은 `.1`, `.2` … 로 번호가 밀리며, `max-file` 개를 넘는 가장 오래된 파일은 지웁니다[8][12]. `compress` 를 켜면 회전된 파일이 `.1.gz` 처럼 gzip 으로 바뀌고, gzip 헤더의 Extra 필드에 `{"lastTime":"..."}` 로 그 파일 마지막 줄의 시각을 적습니다[8].

### local 로그

메시지마다 `[4바이트 빅엔디언 길이][protobuf 메시지][같은 4바이트 길이]` 순서로 붙어 있어 앞에서도 뒤에서도 읽을 수 있습니다[9]. protobuf 메시지 안에는 필드 1 `source`(`stdout`/`stderr`, 태그 바이트 `0x0a`), 필드 2 시각(varint, 태그 `0x10`), 필드 3 메시지(태그 `0x1a`)가 차례로 있습니다[16]. 시각은 나노초 단위 유닉스 시각입니다[16]. 회전과 압축 파일 이름 규칙은 json-file 과 같은 코드를 씁니다[8][9].

### journald 로그

journald 드라이버를 쓰면 로그가 컨테이너 폴더가 아니라 호스트 저널로 가고, 줄마다 다음 필드가 붙습니다[14].

| 필드 | 뜻 |
|---|---|
| `CONTAINER_ID` | 12자리로 자른 컨테이너 ID |
| `CONTAINER_ID_FULL` | 64자리 컨테이너 ID |
| `CONTAINER_NAME` | 시작할 때의 컨테이너 이름. 그 뒤 `docker rename` 으로 바꾼 이름은 반영되지 않습니다 |
| `CONTAINER_TAG`, `SYSLOG_IDENTIFIER` | 컨테이너 태그 |
| `CONTAINER_PARTIAL_MESSAGE` | 긴 줄이 나뉘었음을 표시 |
| `IMAGE_NAME` | 이미지 이름 |

`journalctl CONTAINER_NAME=web01` 처럼 필드로 거르면 됩니다[14]. 저널 파일의 형식과 보존 설정은 [systemd 저널](../../../01-foundations/logging/systemd-journal/index.md) 에서 다룹니다.

### 이중 로깅 캐시

데몬이 되읽을 수 없는 드라이버를 쓰면, 엔진이 local 드라이버를 캐시로 함께 켜서 `container-cached.log` 에 최근 로그를 남깁니다[1][15]. `json-file`·`local`·`journald` 는 스스로 읽기를 지원해서 캐시를 쓰지 않습니다[1][15]. 로그 옵션 `cache-disabled` 가 `"true"` 이면 캐시가 없습니다[15]. 원격 로그 서버로 보내던 컨테이너라도 이 캐시에 마지막 로그가 남아 있을 수 있습니다.

## 증거로서 의미

### 증명하는 것

- 이 ID·이름의 컨테이너를 이 이미지로 `Created` 시각에 만들었다는 것.
- 마지막으로 시작한 시각(`State.StartedAt`)과 마지막으로 끝난 시각(`State.FinishedAt`), 종료 코드(`ExitCode`), 메모리 부족으로 죽었는지(`OOMKilled`).
- 컨테이너에 준 명령·인자·환경 변수·마운트·포트·권한 옵션.
- 컨테이너가 stdout·stderr 로 내보낸 내용과, 데몬이 그 줄을 받은 시각.

### 증명하지 못하는 것

- 누가 `docker run` 을 실행했는지. 설정 파일에는 명령한 계정이 없습니다.
- 컨테이너 안에서 누가 무엇을 입력했는지. 셸 명령은 화면에 찍혀 stdout 으로 나오지 않는 한 로그에 없습니다.
- `docker exec` 로 컨테이너에 들어간 기록. exec 목록(`ExecCommands`)은 디스크에 저장하지 않습니다[1].
- 여러 번 재시작한 컨테이너의 이전 실행 시각. `StartedAt`·`FinishedAt` 은 값이 하나씩이라 시작·종료할 때마다 덮어씁니다[2].
- 애플리케이션이 파일에 따로 쓴 로그. 그런 로그는 컨테이너 쓰기 층이나 볼륨에 있습니다([overlay 파일 시스템](overlay2.md)).

보고서에는 "컨테이너 web01 의 표준 출력 로그에 2026-03-02 01:15:07(UTC) 에 데몬이 받은 요청 줄이 있다" 처럼 로그로 확인되는 만큼만 씁니다.

## 시각 해석

| 값 | 형식 | 시간대 | 바뀌는 때 |
|---|---|---|---|
| `config.v2.json` `Created` | RFC 3339 문자열, 소수점 아래 나노초까지[16] | UTC[3] | 컨테이너를 만들 때 한 번 |
| `State.StartedAt` | 같음 | UTC[2] | 시작할 때마다 덮어씀 |
| `State.FinishedAt` | 같음 | UTC[2] | 끝날 때마다 덮어씀 |
| json-file `time` | RFC3339Nano | UTC(`Z`)[6][7] | 데몬이 그 줄을 읽어 들일 때 |
| local 드라이버 시각 | 나노초 유닉스 시각 | UTC[6][16] | 같음 |
| 회전 gz 헤더 `lastTime` | JSON 시각 문자열 | UTC[6][8] | 회전해 압축할 때, 그 파일 마지막 줄의 시각 |

로그의 `time` 은 애플리케이션이 찍은 시각이 아니라 데몬이 컨테이너 출력에서 줄을 읽어 들인 순간의 시각입니다[6]. 그래서 로그 내용 안에 애플리케이션이 따로 찍은 시각이 있으면 두 값이 조금 다를 수 있고, 둘의 차이가 크면 애플리케이션의 시간대 설정이나 출력 버퍼를 의심합니다. 16KB(`16 * 1024` 바이트)를 넘는 줄은 여러 조각으로 나뉘어 기록되고, 조각들은 모두 첫 조각의 시각을 씁니다[6].

`FinishedAt` 이 `0001-01-01T00:00:00Z` 이면 이 컨테이너는 만든 뒤 한 번도 멈춘 적이 없습니다. 이 값은 Go 언어 시각의 빈 값(zero value)이라[2] 실제 날짜로 읽으면 안 되고, `StartedAt` 도 빈 값이면 만들기만 하고 시작하지 않은 컨테이너입니다[2]. plaso 는 이 값을 "아직 실행 중" 으로 해석하지만[17], 데몬은 컨테이너를 시작할 때 `FinishedAt` 을 비우지 않아서 다시 시작한 컨테이너는 실행 중에도 `FinishedAt` 에 지난번 종료 시각이 남아 있습니다[2]. 그래서 실행 여부는 `State.Running` 으로 판단하고, `FinishedAt` 이 `StartedAt` 보다 이르면 지난번 종료 시각으로 읽습니다. 시각 문자열의 소수점 아래 자릿수는 9자리로 고정되어 있지 않으므로 자릿수를 가정하지 않고 읽습니다[16]. 시각 값 일반은 [Linux 의 시각 값](../../../01-foundations/value-decoding/time-values.md) 을 봅니다.

## 함정과 한계

- **컨테이너를 지우면 폴더째 사라집니다.** `docker rm` 은 설정·json-file 로그·local 로그가 든 컨테이너 폴더를 통째로 지웁니다[10]. `hostconfig.json` 의 `AutoRemove` 가 `true` 인 컨테이너(`docker run --rm`)는 끝나는 즉시 이렇게 지워집니다[4]. 지운 뒤 남는 것은 저널(journald 드라이버를 썼다면), 볼륨, 셸 기록 정도이고, 볼륨이 남는 조건은 [Docker 허브](index.md) 에 정리했습니다.
- **회전으로 오래된 로그가 지워집니다.** `max-size`·`max-file` 을 정한 json-file 과 기본값의 local 드라이버는 가장 오래된 파일을 지웁니다[12][13]. 반대로 json-file 기본값(회전 없음)이면 파일 하나가 매우 커질 수 있습니다[11].
- **도구마다 "컨테이너 이름" 이 다릅니다.** dissect.target 은 `Name` 에서 앞의 `/` 를 뗀 값을 이름으로 쓰고[16], plaso 는 `Config.Hostname` 을 container_name 으로 씁니다[17]. 두 도구의 결과를 섞어 볼 때는 `ID` 로 맞춥니다.
- **dissect.target 의 `docker.logs` 가 폴더 이름으로 컨테이너 ID 를 정합니다.** `containers/` 아래 `*.log*` 를 모두 찾아, 파일 이름에 `-json.log` 가 있으면 바로 위 폴더를, 없으면 local 형식으로 읽고 두 단계 위 폴더를 컨테이너 ID 로 씁니다[16]. `local-logs/container.log` 에는 맞지만, 컨테이너 폴더 바로 아래 있는 `container-cached.log` 는 이 규칙대로면 ID 필드에 `containers` 가 들어가므로 `source` 경로로 컨테이너를 다시 확인합니다.
- **dissect.target 은 기본으로 로그를 손봅니다.** ANSI 이스케이프를 지우고 백스페이스를 `[BS]`, 탭을 `[TAB]` 으로 바꿉니다[16]. 원문 그대로가 필요하면 `--raw-messages` 를 줍니다[16].
- **ForensicArtifacts 의 로그 정의 이름이 GKE 용입니다.** `GKEDockerContainerLogs` 가 `/var/lib/docker/containers/*/*-json.log*` 를 모으는 정의이고[18], 일반 호스트에서도 같은 경로를 모으면 됩니다. `DockerContainerConfig` 는 `config.v2.json` 과 `config.json` 만 모으므로 `hostconfig.json` 과 local 드라이버 로그는 따로 챙깁니다[18].
- **실행 중인 호스트에서는 로그 파일을 직접 건드리지 않습니다.** json-file 로그는 데몬 혼자 쓰도록 만든 파일이라 다른 도구가 만지면 로깅이 어긋날 수 있습니다[12]. 사본을 떠서 분석합니다. 순서는 [컨테이너 수집](../../../03-techniques/acquisition/container-acquisition.md) 을 따릅니다.

## 직접 분석해 보기

### 헥스로 한 번 — local 드라이버 레코드

명세로 만든 예시입니다. stdout 으로 나온 `hello` 한 줄을 local 드라이버 형식으로 적으면 다음 34바이트가 됩니다.

```text
00000000  00 00 00 1a 0a 06 73 74  64 6f 75 74 10 95 9a 97  |......stdout....|
00000010  ec e3 9f e7 cb 17 1a 06  68 65 6c 6c 6f 0a 00 00  |........hello...|
00000020  00 1a                                             |..|
```

| 오프셋 | 바이트 | 뜻 |
|---|---|---|
| 0x00 | `00 00 00 1a` | 머리 길이 26 (빅엔디언) |
| 0x04 | `0a 06` + `73 74 64 6f 75 74` | 필드 1, 길이 6, `stdout` |
| 0x0C | `10` + `95 9a 97 ec e3 9f e7 cb 17` | 필드 2, varint 시각 1700000000123456789 ns |
| 0x16 | `1a 06` + `68 65 6c 6c 6f 0a` | 필드 3, 길이 6, `hello` 와 줄 바꿈 |
| 0x1E | `00 00 00 1a` | 꼬리 길이 26. 머리와 같아야 합니다 |

varint 는 바이트마다 아래 7비트를 낮은 자리부터 이어 붙이고, 맨 위 비트가 1 이면 다음 바이트가 이어집니다. 위 9바이트를 풀면 1700000000123456789 이고, 나노초 유닉스 시각이라 2023-11-14 22:13:20.123456789 UTC 입니다. 머리와 꼬리 길이가 다르면 파일 끝이 잘렸거나 레코드 경계를 잘못 잡은 것입니다.

### 공개 도구로 한 번

| 도구 | 쓰는 때 | 하는 일 |
|---|---|---|
| dissect.target | 오프라인 | `docker.containers` 가 `config.v2.json` 에서 ID·이미지·명령·생성·시작·종료 시각·포트·볼륨·환경 변수를, `docker.logs` 가 json-file 과 local 로그(압축본 포함)를 레코드로 뽑습니다[16] |
| plaso (jsonl 파서) | 오프라인 타임라인 | `docker_container_config` 가 `Created`·`StartedAt`·`FinishedAt` 을 세 이벤트로, `docker_container_log` 가 `log`·`stream`·`time` 세 키가 다 있고 `time` 이 ISO 8601 인 줄을 이벤트로 만듭니다[17] |
| UAC | 라이브 | 컨테이너마다 `docker inspect` 와 `docker container logs` 출력을 파일로 모읍니다[19] |

json-file 로그는 JSON Lines 라서 `jq -r '[.time, .stream, .log] | @tsv' 컨테이너ID-json.log` 처럼 줄 단위로 풀어 읽어도 됩니다. 압축본은 `zcat` 으로 풀어 같은 방법으로 읽습니다.

## 교차 검증

- [systemd 저널](../../../01-foundations/logging/systemd-journal/index.md) — `docker.service`·`containerd.service` 단위의 데몬 기록, journald 드라이버의 `CONTAINER_*` 필드
- [셸 명령 기록](../../execution/shell-history/index.md) — `docker run`·`docker exec`·`docker cp` 를 입력한 계정
- [감사 로그의 실행 기록](../../execution/auditd-execve.md) — `docker` 클라이언트 실행 시각과 계정
- [overlay 파일 시스템](overlay2.md) — 컨테이너 쓰기 층의 파일 시각으로 로그 사이의 빈틈 메우기
- [이미지와 레이어](images-layers.md) — `config.v2.json` 의 `Image` 로 이미지 이름과 빌드 이력 잇기

## 실습

공개 증거물 이미지 대신 실험용 가상 머신에 Docker 를 설치해 따라 합니다.

1. 기본 설정으로 nginx 컨테이너를 만들어 몇 번 요청을 보내고 멈춘 뒤, `config.v2.json` 의 `Created`·`StartedAt`·`FinishedAt` 과 json-file 로그 첫 줄·마지막 줄의 `time` 을 나란히 놓으면 어떤 순서가 나오나?
2. 같은 컨테이너를 두 번 더 시작·정지하면 `StartedAt`·`FinishedAt`·`RestartCount` 가 어떻게 바뀌나? 첫 실행의 시각은 어디에 남나?
3. `--log-driver local` 로 만든 컨테이너의 `local-logs/container.log` 를 헥스로 열어 첫 레코드의 머리·꼬리 길이와 시각을 손으로 풀 수 있나?
4. `docker run --rm` 으로 만든 컨테이너가 끝난 뒤 `containers/` 에 무엇이 남나? 저널과 셸 기록에서는 무엇을 찾을 수 있나?

## 참고 문헌

1. moby/moby, `daemon/container/container.go`. https://github.com/moby/moby/blob/master/daemon/container/container.go
2. moby/moby, `daemon/container/state.go`. https://github.com/moby/moby/blob/master/daemon/container/state.go
3. moby/moby, `daemon/container.go`. https://github.com/moby/moby/blob/master/daemon/container.go
4. moby/moby, `api/types/container/hostconfig.go`. https://github.com/moby/moby/blob/master/api/types/container/hostconfig.go
5. moby/moby, `daemon/daemon.go`. https://github.com/moby/moby/blob/master/daemon/daemon.go
6. moby/moby, `daemon/logger/copier.go`. https://github.com/moby/moby/blob/master/daemon/logger/copier.go
7. moby/moby, `daemon/logger/jsonfilelog/jsonlog/jsonlog.go`, `time_marshalling.go`. https://github.com/moby/moby/tree/master/daemon/logger/jsonfilelog
8. moby/moby, `daemon/logger/loggerutils/logfile.go`. https://github.com/moby/moby/blob/master/daemon/logger/loggerutils/logfile.go
9. moby/moby, `daemon/logger/local/doc.go`, `local.go`. https://github.com/moby/moby/tree/master/daemon/logger/local
10. moby/moby, `daemon/delete.go`. https://github.com/moby/moby/blob/master/daemon/delete.go
11. Docker Docs, "Configure logging drivers" (`content/manuals/engine/logging/configure.md`). https://github.com/docker/docs/blob/main/content/manuals/engine/logging/configure.md
12. Docker Docs, "JSON File logging driver" (`content/manuals/engine/logging/drivers/json-file.md`). https://github.com/docker/docs/blob/main/content/manuals/engine/logging/drivers/json-file.md
13. Docker Docs, "Local file logging driver" (`content/manuals/engine/logging/drivers/local.md`). https://github.com/docker/docs/blob/main/content/manuals/engine/logging/drivers/local.md
14. Docker Docs, "Journald logging driver" (`content/manuals/engine/logging/drivers/journald.md`). https://github.com/docker/docs/blob/main/content/manuals/engine/logging/drivers/journald.md
15. Docker Docs, "Dual logging" (`content/manuals/engine/logging/dual-logging.md`). https://github.com/docker/docs/blob/main/content/manuals/engine/logging/dual-logging.md
16. fox-it/dissect.target, `dissect/target/plugins/apps/container/docker.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/container/docker.py
17. log2timeline/plaso, `plaso/parsers/jsonl_plugins/docker_container_config.py`, `docker_container_log.py`. https://github.com/log2timeline/plaso/tree/main/plaso/parsers/jsonl_plugins
18. ForensicArtifacts/artifacts, `artifacts/data/docker.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/docker.yaml
19. tclahr/uac, `artifacts/live_response/containers/docker.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/live_response/containers/docker.yaml
