---
title: "Google Cloud VPC 흐름 로그"
parent: "아티팩트 · Google Cloud"
nav_order: 530
---

# VPC 흐름 로그 (VPC Flow Logs)

Google Cloud VPC 네트워크에서 표본으로 뽑은 패킷을 IP 연결별로 묶어 Cloud Logging 에 남기는 기록이고, 어느 시간 구간에 어떤 주소와 포트 사이에 패킷이 오갔는지를 보여 줍니다.

## 무엇을 기록하나 · 왜 생기나

VPC 흐름 로그는 VPC 네트워크 안의 패킷을 표본 추출(sampling)해서 5-튜플(출발지·목적지 IP, 출발지·목적지 포트, 프로토콜)마다 한 건의 흐름 기록을 만듭니다[1]. 표본을 뽑는 대상은 세 가지입니다. 가상 머신(VM)이 보내고 받는 패킷(GKE 노드로 쓰는 VM 포함), Direct VPC egress 로 설정한 Cloud Run·App Engine 자원이 보내고 받는 패킷, Cloud Interconnect 의 VLAN 연결과 Cloud VPN 터널을 지나는 패킷입니다[1].

기본으로 꺼져 있고, 서브넷을 새로 만들어도 따로 켜지 않으면 기록하지 않습니다[3]. 사고 전에 켜 두지 않았다면 그 시기의 흐름 기록은 없습니다. 켜 두었다면 사고 대응에서 "어느 IP 가 서로 언제 통신했는가", "침해된 VM 이 드나든 흐름이 무엇인가" 를 좇는 데 씁니다[1].

## 위치와 버전별 차이

### 켜는 단위

켜는 단위는 조직, VPC 네트워크, 서브넷, VLAN 연결, Cloud VPN 터널입니다[1]. 조직 단위로 켜면 조직 안 모든 VPC 네트워크의 서브넷·VLAN 연결·VPN 터널이 대상이 되고, 서브넷 단위로 켜면 그 서브넷 안의 VM 과 서버리스 자원 전부가 대상이 됩니다[1]. VM 에 네트워크 인터페이스가 여럿이면 인터페이스가 붙은 서브넷마다 켜야 합니다[1].

### 설정 방법에 따라 달라지는 로그 이름

설정 방법은 Network Management API(권장 방법)와 Compute Engine API 두 가지이고[3], 어느 쪽으로 켰는지에 따라 로그 이름과 자원 유형이 다릅니다[4].

| 설정 방법 | `logName` | `resource.type` | 설정을 가려내는 필드 |
|---|---|---|---|
| Network Management API | `projects/PROJECT_ID/logs/networkmanagement.googleapis.com%2Fvpc_flows` | `vpc_flow_logs_config` | `resource.labels.name`(설정 이름), `labels.target_resource_name`(보고한 네트워크·서브넷·VLAN 연결·터널, 조직 설정이면 비어 있음) |
| Compute Engine API | `projects/PROJECT_ID/logs/compute.googleapis.com%2Fvpc_flows` | `gce_subnetwork` | `resource.labels.subnetwork_name` |

Compute Engine API 쪽 로그는 서브넷에만 있고, Network Management API 쪽 로그는 VPC 네트워크·서브넷·VLAN 연결·VPN 터널을 모두 담습니다[4]. 한 조사에서 두 로그를 함께 찾으려면 두 이름을 `OR` 로 묶습니다[4].

### 쌓이는 곳과 보관 기간 (2026년 9월 문서 기준)

흐름 기록은 흐름을 보고한 VPC 네트워크가 속한 프로젝트의 Cloud Logging 으로 들어갑니다[1]. 공유 VPC(Shared VPC)라면 서비스 프로젝트가 아니라 호스트 프로젝트에 쌓이므로, 서비스 프로젝트에서 찾으면 한 건도 나오지 않습니다[1][4]. Logging 에는 기본으로 30일 보관하고, 더 오래 두려면 보관 기간을 따로 정하거나 다른 곳으로 내보내야 합니다[1]. 로그 버킷과 보관 기간 일반은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 와 [Cloud Audit Logs](cloud-audit-logs.md) 에서 다룹니다.

### 표본과 집계 설정

1차 표본 비율은 보고하는 자원이 올라간 물리 호스트의 부하에 따라 바뀌고 사용자가 바꿀 수 없으며, 패킷이 많은 연결일수록 잡힐 확률이 높습니다[1]. 그 뒤에 거르기(filter), 집계, 2차 표본, 메타데이터 붙이기를 거쳐 Logging 에 씁니다[1]. 설정 값은 아래와 같습니다.

| 항목 | Compute Engine API 설정 | Network Management API 설정 |
|---|---|---|
| 집계 간격 | 5초(기본)·30초·1분·5분·10분·15분 | 같음 |
| 2차 표본 비율 기본값 | 0.5(기록의 50% 남김) | 1.0(100% 남김) |
| 2차 표본 비율 범위 | 0.0~1.0 | 0.0 초과~1.0 |
| 메타데이터 기본값 | 콘솔은 전부 붙임, gcloud·API 는 `EXCLUDE_ALL_METADATA`(안 붙임). 2021년 3월 1일 전에 켠 적이 있고 따로 정하지 않은 서브넷은 `INCLUDE_ALL_METADATA`[3] | `INCLUDE_ALL_METADATA`(전부 붙임)[3] |
| 메타데이터 선택 | 전부·없음·골라 붙이기 | 같음 |
| 생성 필터 | CEL 식, 2,048자까지 | 같음 |

API 에서는 집계 간격을 `INTERVAL_5_SEC`, `INTERVAL_30_SEC`, `INTERVAL_1_MIN`, `INTERVAL_5_MIN`, `INTERVAL_10_MIN`, `INTERVAL_15_MIN` 으로 적습니다[3]. 생성 필터는 `rtt_msec`, `bytes_sent`, `packets_sent`, `start_time`, `end_time` 을 조건으로 쓸 수 없고, 필터에 맞지 않은 기록은 Logging 에 쓰기 전에 버립니다[2].

## 구조

로그 항목 하나는 Cloud Logging 의 LogEntry 이고, 흐름 내용은 `jsonPayload` 아래에 들어 있습니다[4][7]. LogEntry 공통 필드는 [JSON 로그 읽기](../../01-foundations/logging/json-logs.md) 에서 다룹니다. `jsonPayload` 필드는 늘 들어가는 기본 필드(base)와 설정에 따라 빠질 수 있는 메타데이터 필드(metadata)로 나뉩니다[2].

### 기본 필드

기본 필드는 패킷 헤더에서 곧바로 얻은 값입니다[2].

| 필드 | 형식 | 뜻 |
|---|---|---|
| `connection` | IpConnection(`src_ip`, `dest_ip`, `src_port`, `dest_port`, `protocol`) | 5-튜플입니다. 포트는 TCP·UDP 에서만 채우고, `protocol` 은 IANA 프로토콜 번호이며 RDMA 흐름에서는 비어 있습니다 |
| `reporter` | string | 흐름을 보고한 쪽입니다. VM·서버리스는 `SRC`·`DEST`, VLAN 연결·VPN 터널은 `SRC_GATEWAY`·`DEST_GATEWAY` 입니다 |
| `start_time` | string(RFC 3339) | 집계 간격 안에서 처음 관찰한 패킷의 시각입니다 |
| `end_time` | string(RFC 3339) | 집계 간격 안에서 마지막으로 관찰한 패킷의 시각입니다 |
| `bytes_sent` | int64 | 출발지에서 목적지로 보낸 사용자 페이로드 바이트의 추정치입니다. 페이로드 없는 패킷은 0 이지만, Falcon 트래픽을 출발지 VM 이 보고하면 헤더 바이트까지 더해 늘 0보다 큽니다 |
| `packets_sent` | int64 | 보낸 패킷 수의 추정치입니다 |
| `rtt_msec` | int64 | 왕복 시간(밀리초)입니다. TCP 이고 VM·서버리스가 보고할 때만 채웁니다 |
| `round_trip_time` | Latencies(`median_msec`) | 집계 간격 동안의 왕복 시간 중앙값입니다. VM·서버리스가 보고하는 TCP 트래픽과 Falcon 트래픽에서 채웁니다 |
| `disposition` | string | 패킷 드롭 기록에만 들어가고 값은 `DROPPED` 입니다 |
| `drop_reason` | string | 드롭 이유입니다(아래) |
| `bytes_dropped`, `packets_dropped` | int64 | 버린 바이트·패킷 수의 추정치입니다 |
| `throughput_inclusion` | string | 버린 양이 같은 보고자의 `bytes_sent`·`packets_sent` 에 들어갔는지(`INCLUDED`) 빠졌는지(`EXCLUDED`)를 나타냅니다 |

`bytes_sent`·`packets_sent`·`rtt_msec`·`round_trip_time` 은 드롭 기록(`disposition=DROPPED`)에는 없습니다[2].

### 메타데이터 필드

메타데이터 값은 실제 데이터 경로(data plane path)에서 얻은 값이 아닌 근사값이라 틀리거나 빠질 수 있습니다[2]. 조사에서 자주 보는 것은 아래와 같습니다[2].

| 필드 | 담는 것 |
|---|---|
| `src_instance`, `dest_instance` | VM 의 `project_id`, `region`, `zone`, `vm_name`, `managed_instance_group` |
| `src_vpc`, `dest_vpc` | `project_id`(공유 VPC 면 호스트 프로젝트), `vpc_name`, `subnetwork_name`, `subnetwork_region` |
| `src_location`, `dest_location` | VPC 밖 공인 IP 의 `asn`, `city`, `continent`, `country`(ISO 3166-1 alpha-3), `region` |
| `src_gke_details`, `dest_gke_details` | GKE 클러스터·Pod·Service 이름 |
| `src_google_service`, `dest_google_service` | Google 서비스 종류(`GOOGLE_API`·`GOOGLE_VPC_HOSTED_SERVICE`)와 `service_name`(예: `pubsub.googleapis.com`), 접근 방법(`connectivity`) |
| `src_gateway`, `dest_gateway` | 게이트웨이 `type`(`INTERCONNECT_ATTACHMENT`·`VPN_TUNNEL`)과 이름·위치 |
| `src_serverless_details`, `dest_serverless_details` | Cloud Run·App Engine 자원 이름 |
| `internet_routing_details` | 인터넷으로 나가는 흐름의 AS 경로(`egress_as_path`) |
| `load_balancing`, `psc`, `network_service`, `rdma_traffic_type` | 부하 분산기·Private Service Connect·DSCP·RDMA 정보 |

`dest_location` 같은 위치 정보를 어떻게 믿을지는 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md) 에서 다룹니다.

### 드롭 기록

드롭 기록은 일반 기록과 따로 만들고, 한 집계 간격 안에서 같은 흐름·같은 이유의 드롭을 한 건으로 묶습니다[2]. 나가는 쪽에서 버리면 출발지(`SRC`·`SRC_GATEWAY`)가 보고하고, 들어오는 쪽에서 버리면 목적지(`DEST`·`DEST_GATEWAY`)가 보고합니다[2]. 출발지가 보고하는 `drop_reason` 값은 `FIREWALL_DENY`, `NO_MATCHING_ROUTE`, `QUEUE_OVERFLOW`, `SPOOFED_SOURCE`, `TOO_MANY_CONNECTIONS` 이고, 목적지가 보고하는 값은 `FIREWALL_DENY`, `EARLY_DROPS_FULL_FAIR_QUEUE`, `INVALID_L4_CHECKSUM_INTERNET`, `INVALID_L4_CHECKSUM_INTERNAL`, `PSC_NAT_OUT_OF_CONNECTIONS`, `PSC_NAT_OUT_OF_PORTS`, `QUEUE_OVERFLOW`, `TOO_MANY_CONNECTIONS` 입니다[2]. `SPOOFED_SOURCE` 는 VM 네트워크 인터페이스에 속하지 않은 출발지 주소로 보내려다 IP 전달(IP forwarding)이 꺼져 있어 버린 경우입니다[2].

### 레코드 예

아래는 필드 정의로 만든 예시이고, 값은 모두 지어낸 것입니다. `timestamp`·`receiveTimestamp`·`insertId` 와 메타데이터 일부는 줄였습니다.

```json
{
  "logName": "projects/example-project/logs/networkmanagement.googleapis.com%2Fvpc_flows",
  "resource": { "type": "vpc_flow_logs_config", "labels": { "name": "example-config" } },
  "labels": { "target_resource_name": "projects/123456789012/regions/asia-northeast3/subnetworks/example-subnet" },
  "jsonPayload": {
    "connection": { "src_ip": "192.0.2.10", "src_port": 49822, "dest_ip": "203.0.113.40", "dest_port": 443, "protocol": 6 },
    "reporter": "SRC",
    "start_time": "2026-09-01T02:14:03.120Z",
    "end_time": "2026-09-01T02:14:07.880Z",
    "bytes_sent": 1843200,
    "packets_sent": 1320,
    "rtt_msec": 24,
    "src_instance": { "project_id": "example-project", "vm_name": "web-01", "zone": "asia-northeast3-a", "region": "asia-northeast3" },
    "src_vpc": { "project_id": "example-project", "vpc_name": "example-vpc", "subnetwork_name": "example-subnet", "subnetwork_region": "asia-northeast3" },
    "dest_location": { "asn": 64500, "country": "USA" }
  }
}
```

이 기록은 `web-01` 이 보고한(`reporter` 가 `SRC`) TCP(프로토콜 번호 6) 흐름이고, 5초가 채 안 되는 구간에 바깥 주소 203.0.113.40 의 443 포트로 약 1.8MB 를 보냈다고 추정한 값입니다. `dest_location` 은 목적지가 VPC 네트워크 밖 공인 IP 일 때 붙고, `dest_vpc` 가 없다는 점도 목적지가 VPC 밖이라는 단서입니다[2][4]. 다만 메타데이터를 끈 설정에서는 두 필드가 모두 없습니다[2].

## 증거로서 의미

**증명하는 것.** 기록된 `start_time`~`end_time` 구간에 두 주소·포트 사이에서 패킷이 오간 것을 표본으로 잡았다는 사실, 보낸 양의 대략적인 크기, 흐름을 보고한 VM·서브넷·VPC·게이트웨이, 그리고 드롭 기록이면 버려진 이유를 보여 줍니다[2]. 바깥으로 나간 흐름만 모으면 어느 VM 이 어느 외부 주소로 많이 보냈는지를 볼 수 있습니다[4].

**증명하지 못하는 것.** 흐름 로그는 패킷 방향만 알려 주고 어느 쪽이 연결을 먼저 열었는지는 알려 주지 않습니다[1]. 페이로드가 없으므로 무엇을 보냈는지도 알 수 없습니다. 표본이라 양이 아주 적은 흐름은 빠질 수 있고, 바이트·패킷 수는 추정치입니다[2][4]. 들어오는 쪽 방화벽이 막은 시도는 기록되지 않습니다[1]. 켜지 않은 서브넷, 필터로 버린 흐름, 2차 표본에서 떨어진 기록은 남지 않으므로 "기록이 없다" 가 "통신이 없었다" 를 뜻하지 않습니다. 사람 계정과 흐름을 잇는 필드는 없으므로, 누가 그 VM 을 조작했는지는 [Cloud Audit Logs](cloud-audit-logs.md) 와 VM 안의 기록으로 따로 밝혀야 합니다.

보고서에는 "2026-09-01 02:14:03~02:14:08 UTC 에 VM web-01 에서 203.0.113.40:443 으로 나가는 TCP 흐름이 표본으로 기록되어 있고, 추정 전송량은 약 1.8MB 이다" 처럼 기록으로 확인되는 만큼만 씁니다(만든 예시).

## 시각 해석

`start_time`·`end_time` 은 집계 간격 안에서 처음·마지막으로 관찰한 패킷의 시각이고 RFC 3339 문자열입니다[2]. 실제 통신은 이 구간보다 먼저 시작해 더 늦게 끝났을 수 있고, 집계 간격(5초~15분)이 곧 시간 해상도의 한계입니다[1][2]. 긴 연결은 여러 집계 간격에 걸쳐 여러 건으로 나뉘므로 한 흐름의 전체 기간과 전체 양은 같은 5-튜플의 기록을 이어 붙여 봅니다.

LogEntry 의 `timestamp`·`receiveTimestamp` 는 UTC(`Z`)로 정규화한 RFC 3339 값이고, `receiveTimestamp` 는 Logging 이 항목을 받은 시각입니다[7]. 흐름 기록의 `timestamp` 가 `start_time`·`end_time` 중 무엇과 같은지는 실제 데이터에서 몇 건을 비교해 확인하고, 통신 시각은 `jsonPayload.start_time`·`end_time` 을 기준으로 삼습니다. `gcloud logging read` 의 시각 조건은 `timestamp` 에 걸리므로 찾는 구간 앞뒤로 집계 간격만큼 넉넉하게 잡습니다[8]. 여러 로그의 시각을 맞추는 일반 원칙은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 에 있습니다.

## 함정과 한계

**같은 흐름이 여러 번 나옵니다.** 양쪽 VM 이 모두 흐름 로그를 켜 두었으면 같은 흐름을 `SRC` 와 `DEST` 가 각각 보고합니다[2]. 설정이 겹쳐도 중복이 생기는데, 조직 설정과 프로젝트 안 설정이 함께 있거나, 네트워크 설정과 서브넷 설정이 함께 있거나, 한 서브넷을 두 API 로 동시에 켰을 때 설정마다 따로 기록을 만듭니다[4]. 양을 더하기 전에 `reporter` 로 한쪽만 고르고, `resource.labels.name`·`labels.target_resource_name` 으로 설정 하나만 남깁니다[4].

**방화벽과 기록 순서가 방향마다 다릅니다.** 나가는 패킷은 이그레스 방화벽 규칙보다 먼저 표본을 뽑아서 규칙이 막은 패킷도 기록될 수 있고, 들어오는 패킷은 인그레스 규칙 뒤에 표본을 뽑아서 규칙이 막은 패킷은 기록되지 않습니다[1]. 나가는 쪽에서 버린 흐름은 출발지에 일반 기록과 드롭 기록이 함께 남고 목적지에는 아무것도 없으며, 들어오는 쪽에서 버린 흐름은 출발지에 일반 기록, 목적지에 드롭 기록만 남습니다[2]. 따라서 출발지의 일반 기록만 보고 "전달되었다" 고 쓰면 틀릴 수 있습니다.

**상대편 정보가 비어 있을 수 있습니다.** 공유 VPC·VPC 네트워크 피어링·Network Connectivity Center 를 지나 다른 프로젝트 자원과 오간 흐름에 양쪽 정보를 모두 붙이는 교차 프로젝트 주석(cross-project annotations)은 조직 단위 설정에서만 붙고, 기본으로 켜져 있지만 끌 수 있습니다[2]. 이 주석을 끄면 흐름을 보고한 쪽 정보만 남고, 프로젝트 단위로 켰다면 다른 프로젝트 자원과의 흐름에 이 주석이 붙지 않으므로 상대편 VM 정보가 비어 있을 수 있습니다[2].

**GKE 흐름은 일부가 빠지거나 노드 주소로 보입니다.** 같은 노드 위 Pod 끼리의 흐름은 클러스터에 노드 내 가시성(intranode visibility)을 켜야 기록됩니다[1]. Pod 에서 인터넷으로 나가는 패킷은 흐름 로그가 보기 전에 마스커레이드 에이전트가 노드 IP 로 바꾸므로 Pod 정보가 붙지 않습니다[2].

**지원 프로토콜 설명이 문서마다 다릅니다.** 개요 문서는 TCP·UDP·ICMP·ESP·GRE·RDMA 를 표본으로 뽑는다고 적고, 로그 조회 문서의 문제 해결 절은 TCP·UDP·ICMP·ESP·GRE 만 지원한다고 적습니다(둘 다 2026-09-18 갱신)[1][4]. RDMA 흐름이 쟁점이면 수집한 로그에 `rdma_traffic_type` 이 있는 기록이 있는지 먼저 봅니다. 레거시 네트워크와 프록시 전용 서브넷(`INTERNAL_HTTPS_LOAD_BALANCER`)은 흐름 로그를 지원하지 않습니다[1].

**서브넷 설정만 보고 꺼져 있다고 판단하면 안 됩니다.** Network Management API 로 만든 설정은 서브넷의 `enableFlowLogs`·`logConfig.enable` 필드를 채우지 않습니다[3]. 서브넷 목록에서 `logConfig.enable` 이 비어 있어도 네트워크·조직 단위 설정으로 기록이 쌓이고 있을 수 있으므로, 자원마다 실제로 걸린 설정을 `show-effective-flow-logs-configs` 로 확인합니다[3]. 반대로 설정이 있어도 필터 식이 `false` 이거나 Log Router 의 제외 필터가 흐름 로그를 버리면 기록이 없습니다[4].

**끄거나 줄인 흔적은 감사 로그에 남습니다.** Compute Engine API 로 서브넷 흐름 로그를 끄는 요청은 `logConfig.enable` 을 `false` 로 바꾸는 서브넷 `PATCH` 이고[3], 이 호출은 관리 활동 감사 로그에 `v1.compute.subnetworks.patch` 로 남습니다[5]. Network Management API 설정은 일시 중지(`--state=disabled`)·집계 간격·필터·표본 비율을 `vpcFlowLogsConfigs` 에 대한 `PATCH` 로 바꾸고, 설정을 지우면(`gcloud network-management vpc-flow-logs-configs delete`) 수집이 멈추고 설정도 사라집니다[3]. 이 쪽은 감사 로그에서 `protoPayload.serviceName="networkmanagement.googleapis.com"` 으로 거른 뒤 `methodName` 과 요청 본문을 실제 로그에서 확인합니다. 감사 로그 읽는 법은 [Cloud Audit Logs](cloud-audit-logs.md) 에 있습니다.

## 직접 분석해 보기

흐름 로그는 바이너리 파일이 아니라 JSON 로그 항목이므로 헥스 대신 원본 JSON 을 직접 읽습니다.

**원본 JSON 받아 읽기.** 보고한 VPC 네트워크의 프로젝트(공유 VPC 면 호스트 프로젝트)에서 두 로그 이름을 함께 걸어 받습니다[4][8]. 시각 조건을 넣으면 `--freshness` 기본값(1일)이 적용되지 않습니다[8].

```bash
gcloud logging read '
  resource.type=("vpc_flow_logs_config" OR "gce_subnetwork")
  logName=("projects/example-project/logs/networkmanagement.googleapis.com%2Fvpc_flows" OR
           "projects/example-project/logs/compute.googleapis.com%2Fvpc_flows")
  timestamp>="2026-09-01T00:00:00Z" AND timestamp<="2026-09-02T00:00:00Z"' \
  --project=example-project --order=asc --format=json > flows.json
```

받은 파일에서 먼저 설정별·보고자별 개수를 세어 중복의 크기를 봅니다.

```bash
jq -r '.[] | [.logName, (.resource.labels.name // "-"), .jsonPayload.reporter] | @tsv' flows.json | sort | uniq -c
```

그다음 한 VM 이 바깥으로 보낸 양을 목적지별로 더합니다. 숫자 필드가 문자열로 들어 있을 수도 있으므로 `tonumber` 로 맞춥니다.

```bash
jq -r '.[] | .jsonPayload
  | select(.reporter=="SRC" and .src_instance.vm_name=="web-01" and (.dest_vpc == null))
  | [.connection.dest_ip, ((.bytes_sent // 0) | tostring | tonumber)] | @tsv' flows.json \
  | awk '{b[$1]+=$2} END {for (d in b) print b[d], d}' | sort -rn | head
```

드롭 기록만 따로 보려면 `select(.disposition=="DROPPED")` 로 고르고 `drop_reason` 별로 셉니다.

**Logs Explorer 와 공개 도구로 읽기.** Logs Explorer 에서는 `jsonPayload.src_instance.vm_name="VM_NAME"`, `jsonPayload.connection.dest_port=PORT`, `ip_in_net(jsonPayload.connection.dest_ip, "SUBNET_RANGE")` 같은 조건으로 바로 거를 수 있고, 한 VPC 네트워크에서 VM 이 내보낸 흐름은 `jsonPayload.reporter="SRC"`, `jsonPayload.src_vpc.vpc_name="VPC_NAME"`, `(jsonPayload.dest_vpc.vpc_name!="VPC_NAME" OR NOT jsonPayload.dest_vpc:*)` 를 함께 걸어 찾습니다[4]. plaso 의 `gcp_log` 파서는 `logName`·`timestamp` 가 있는 JSON 줄을 받아 공통 필드와 `resource.labels` 를 뽑지만 흐름 필드(`connection`·`bytes_sent` 등)는 따로 풀지 않으므로[9], 흐름 분석은 위처럼 JSON 을 직접 다루거나 BigQuery 로 내보내 SQL 로 합니다. 로그를 지키고 받는 순서는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 와 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [Cloud Audit Logs](cloud-audit-logs.md) | 흐름 로그 설정을 끄거나 바꾼 호출(`v1.compute.subnetworks.patch`, `networkmanagement.googleapis.com`), 방화벽 규칙 변경(`v1.compute.firewalls.insert`·`patch`·`update`·`delete`)[5]. Sigma 규칙 `gcp_firewall_rule_modified_or_deleted.yml` 이 방화벽 변경을 잡습니다[11] |
| 방화벽 정책 규칙 로깅 | 규칙마다 켜는 별도 기록이고 TCP·UDP 연결만 남깁니다. 허용은 연결을 맺을 때 한 번, 거부는 고유 5-튜플마다 5초 간격으로 되풀이해 남기므로, 흐름 로그에 없는 인그레스 거부 시도를 여기서 봅니다[6] |
| 패킷 미러링(Packet Mirroring) | 모든 패킷이 필요할 때 쓰는 기능입니다[1]. 감사 로그의 `PacketMirrorings` 생성·변경·삭제·조회(`Insert`·`Patch`·`Delete`·`Get`·`List`·`aggregatedList`) 호출을 Sigma 규칙 `gcp_full_network_traffic_packet_capture.yml` 이 잡습니다[10] |
| [서비스 계정 키](iam-keys.md) | 흐름에 나온 VM 에 붙은 서비스 계정이 같은 시각에 무엇을 호출했는지 |
| VM 디스크 안의 기록 | 연결을 연 프로세스와 사용자. [Linux 클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html) 참고 |

AWS 와 Azure 의 같은 성격 기록은 [AWS VPC 흐름 로그](../aws/vpc-flow-logs.md) 와 [Azure 네트워크 흐름 로그](../azure/flow-logs.md) 에 있고, 여러 기록을 시간순으로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에서 다룹니다. 채굴 풀로 나가는 흐름을 찾는 절차는 [채굴용 자원을 만들었나](../../04-scenarios/infrastructure/cryptomining.md) 에 있습니다.

## 실습

공식 문서의 필드 정의[2]와 위의 만든 예시로 풀어 봅니다.

1. 위 만든 예시에서 연결을 먼저 연 쪽이 어느 주소라고 말할 수 있는지, 말할 수 없다면 무엇을 더 봐야 하는지 적어 봅니다.
2. 같은 5-튜플에 `reporter` 가 `SRC` 인 기록과 `DEST` 인 기록이 모두 있을 때 전송량을 어떻게 더해야 하는지 적어 봅니다.
3. 들어오는 SSH(22번 포트) 연결 시도가 인그레스 방화벽에 막혔다면 흐름 로그의 출발지와 목적지에 각각 어떤 기록이 남는지, 출발지가 VPC 밖일 때와 안일 때를 나눠 적어 봅니다[1][2].
4. 공유 VPC 의 서비스 프로젝트에 있는 VM 을 조사할 때 흐름 로그를 어느 프로젝트에서 받아야 하고, 그 기록의 `src_vpc.project_id` 에는 어느 프로젝트가 들어가는지 적어 봅니다[1][2].
5. 서브넷 목록에서 `logConfig.enable` 이 비어 있는데 흐름 로그가 쌓여 있다면 어떤 설정 때문인지, 무엇으로 확인하는지 적어 봅니다[3].
6. 실제 프로젝트가 있다면 `gcloud network-management vpc-flow-logs-configs list --location=global` 과 서브넷 목록으로 흐름 로그가 켜진 자원을 표로 만들고, 사고 시각에 기록이 있을 자원과 없을 자원을 나눠 봅니다[3].

## 참고 문헌

1. Google Cloud, "VPC Flow Logs", Virtual Private Cloud documentation. https://cloud.google.com/vpc/docs/flow-logs
2. Google Cloud, "About VPC Flow Logs records", Virtual Private Cloud documentation. https://cloud.google.com/vpc/docs/about-flow-logs-records
3. Google Cloud, "Configure VPC Flow Logs", Virtual Private Cloud documentation. https://cloud.google.com/vpc/docs/using-flow-logs
4. Google Cloud, "Access flow logs", Virtual Private Cloud documentation. https://cloud.google.com/vpc/docs/access-flow-logs
5. Google Cloud, "VPC audit logging", Virtual Private Cloud documentation. https://cloud.google.com/vpc/docs/audit-logging
6. Google Cloud, "Firewall policy rules logging overview", Cloud NGFW documentation. https://cloud.google.com/firewall/docs/firewall-rules-logging
7. Google Cloud, "LogEntry", Cloud Logging API reference. https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
8. Google Cloud, "gcloud logging read", Google Cloud SDK reference. https://cloud.google.com/sdk/gcloud/reference/logging/read
9. log2timeline, plaso (plaso/parsers/jsonl_plugins/gcp_log.py). https://github.com/log2timeline/plaso/blob/main/plaso/parsers/jsonl_plugins/gcp_log.py
10. SigmaHQ, gcp_full_network_traffic_packet_capture.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/audit/gcp_full_network_traffic_packet_capture.yml
11. SigmaHQ, gcp_firewall_rule_modified_or_deleted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/audit/gcp_firewall_rule_modified_or_deleted.yml
