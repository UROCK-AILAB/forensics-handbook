---
title: "휘발성 순서"
parent: "라이브 대응"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1980
---

# 휘발성 순서 (Order of Volatility)

켜져 있는 맥에서 증거를 모을 때는 금방 사라지는 것부터 모으고, 그 순서는 RFC 3227이 정한 휘발성 순서를 맥의 명령과 저장 위치에 맞춰 옮겨 씁니다.

## 언제 쓰나

켜진 맥을 현장에서 만나 전원을 끄거나 디스크 이미지를 뜨기 전에 무엇부터 모을지 정할 때 씁니다. 수집 절차에는 휘발성 순서를 정하는 단계가 따로 있고, 바깥에서 시스템을 바꿀 수 있는 경로를 없앤 다음 정한 순서대로 모읍니다 [1]. 수집 전체의 원칙과 기록 방법은 [라이브 대응 (Live Response)](index.md)에 있고, 이 페이지는 순서를 정하는 일만 다룹니다.

## RFC 3227의 순서와 맥에서 보는 곳

RFC 3227 2.1절의 휘발성 순서는 아래 일곱 단계이고, 위에 있을수록 휘발성이 큽니다 [1]. 둘째 열은 원문 그대로이고, 셋째 열은 RFC에 없는 내용으로 이 핸드북이 맥에 맞춰 붙인 대응입니다.

| 단계 | RFC 3227 원문 [1] | 맥에서 보는 곳 (이 핸드북의 대응) |
|---|---|---|
| 1 | registers, cache | 명령 한 줄로 따로 뜨지 않고, 메모리 수집의 몫으로 봅니다. [메모리 분석 (Memory Forensics)](../../analysis/memory-forensics/index.md) |
| 2 | routing table, arp cache, process table, kernel statistics, memory | 프로세스 목록과 열린 파일, 네트워크 연결과 라우팅 테이블, 물리 메모리 |
| 3 | temporary file systems | 재부팅하면 사라질 수 있는 임시 파일 |
| 4 | disk | 디스크 전체. [맥 증거 확보 (Acquisition)](../evidence-acquisition/index.md) |
| 5 | remote logging and monitoring data that is relevant to the system in question | MDM·EDR처럼 밖에서 이 맥의 기록을 모으는 시스템 |
| 6 | physical configuration, network topology | 장비 연결 상태와 네트워크 구성 |
| 7 | archival media | 따로 보관해 둔 백업 매체 |

2단계는 명령 출력으로 남기는 항목이 가장 많은 단계라서 맥에서는 대부분 이 페이지의 형제 페이지로 이어집니다. 프로세스 목록은 [프로세스와 열린 파일 (ps·lsof)](processes-open-files.md)에서, 연결과 라우팅 테이블은 [네트워크 연결 (Connections)](connections.md)에서 다룹니다. 3단계의 임시 파일은 재부팅 전에는 남아 있다고 보고 디스크 수집 범위에 넣어 둡니다.

## 통합 로그는 몇 단계인가

통합 로그 (Unified Log)는 디스크에 파일로 남아서 RFC 분류로는 4단계에 들어가지만, 보관 기간이 정해진 저장소라 시간이 지나면 오래된 항목이 빠집니다. 이 핸드북은 디스크 이미지를 뜨기 전에 `log collect` 로 통합 로그를 먼저 떠 두는 쪽을 권하고, 방법은 [통합 로그 수집 (log collect)](log-collect.md)에, 보관 기간과 저장 형식은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있습니다.

## 절차

아래 순서는 RFC 순서를 맥의 명령에 맞춰 늘어놓은 예입니다. 같은 2단계 안에서 무엇을 먼저 할지는 사건마다 정하고, 정한 순서와 이유를 수집 기록에 남깁니다.

1. 수집 도구와 도구를 띄울 앱에 [전체 디스크 접근 권한 (Full Disk Access)](full-disk-access.md)이 있는지 확인하고, 권한을 새로 주었다면 그 시각을 적습니다.
2. 프로세스 목록과 열린 파일을 모읍니다. [프로세스와 열린 파일 (ps·lsof)](processes-open-files.md)
3. 네트워크 연결, 라우팅 테이블, 인터페이스 통계를 모읍니다. [네트워크 연결 (Connections)](connections.md)
4. 통합 로그를 모읍니다. [통합 로그 수집 (log collect)](log-collect.md)
5. 디스크를 뜹니다. [맥 증거 확보 (Acquisition)](../evidence-acquisition/index.md)
6. 물리 메모리는 미리 설치해 둔 수집 에이전트가 있을 때만 뜹니다. 메모리를 뜨다 커널 패닉이 나면 남은 수집을 못 할 수 있으니, 다른 수집을 모두 마친 뒤 마지막에 뜹니다. [메모리 확보 (Acquisition)](../../analysis/memory-forensics/memory-acquisition.md)
7. MDM·EDR 같은 원격 기록은 맥을 다 뜬 뒤 관리 서버 쪽에서 따로 요청합니다.

## 함정과 한계

RFC 3227은 2002년에 나온 일반 지침이라 맥의 명령이나 경로를 적지 않았고, 위 표의 셋째 열과 절차는 이 핸드북이 옮겨 붙인 대응입니다 [1]. 원문은 목록 순서를 정해 두었지만 현장에서는 네트워크를 끊을지, 메모리를 뜰 수 있는지 같은 사정에 따라 순서가 바뀌기도 하고, 바꾸었다면 그 결정을 기록해 두어야 뒤에 설명할 수 있습니다.

모으는 명령도 시스템 위에서 돌아가는 프로세스라서 수집할수록 원래 상태가 조금씩 바뀝니다. 그래서 데이터 변경은 최소로 하고, 시스템 전체의 접근 시각을 바꾸는 도구는 피합니다 [1]. 나중에 수집 명령이 남긴 흔적과 원래 있던 흔적을 가를 때는 한 일을 시각과 함께 적어 둔 기록을 보고, 기록 방법은 [라이브 대응 (Live Response)](index.md)에 있습니다.

## 결과를 어떻게 해석하나

2단계에서 모은 출력은 명령을 실행한 순간의 상태를 보여 주고, 그 전에 끝난 프로세스나 닫힌 연결은 들어 있지 않습니다. 그래서 휘발성 자료는 "수집 시각에 이 상태였다" 까지만 말하고, 그 전의 일은 디스크와 통합 로그에서 따로 찾아 [타임라인 작성 (Timeline)](../../analysis/timeline/index.md)으로 잇습니다. 각 출력 파일에 수집 시각을 함께 적어 두지 않으면 이 타임라인에 올릴 기준이 없어집니다.

## 참고 문헌

1. RFC 3227 / BCP 55, Guidelines for Evidence Collection and Archiving (D. Brezinski, T. Killalea, 2002-02) — https://www.rfc-editor.org/rfc/rfc3227
