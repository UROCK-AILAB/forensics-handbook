---
title: "라이브 대응"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 1970
has_children: true
has_toc: false
---

# 라이브 대응 (Live Response)

켜져 있는 맥에서 전원을 끄기 전에 프로세스·열린 파일·네트워크 연결·통합 로그처럼 사라지거나 바뀌기 쉬운 증거를 휘발성이 큰 순서대로 모으는 방법과, 그 과정에서 걸리는 전체 디스크 접근 권한 문제를 묶어 안내합니다.

## 왜 중요한가

증거 수집 지침인 RFC 3227 은 수집을 마치기 전에 시스템을 끄지 말고, 휘발성이 큰 것부터 모으며, 수집과 분석 가운데 하나를 골라야 하면 수집을 먼저 하라고 권합니다 [1]. 같은 문서는 네트워크만 끊어도 공격자가 심어 둔 "데드맨 스위치 (dead man switch)" 가 증거를 지울 수 있다고 경고합니다 [1].

RFC 3227 은 또 파일 접근 시각 같은 데이터 변경을 최소로 하고, 시스템 전체의 접근 시각을 바꾸는 도구는 피하라고 합니다 [1]. 침해된 시스템에 들어 있는 프로그램도 믿지 않고, 외부 라이브러리 없이 돌아가는 정적 링크 프로그램을 읽기 전용 매체에 준비해 두라고 권합니다 [1]. 한 일은 시각과 함께 자세히 기록하고, 시스템 시계가 UTC 와 얼마나 어긋나는지(clock drift)도 적어 둡니다 [1].

RFC 3227 3.2절은 수집 절차를 관련 시스템 확인, 관련 증거 결정, 시스템마다 휘발성 순서 정하기, 외부에서 시스템을 바꿀 수 있는 경로 없애기, 정한 순서대로 수집, 시스템 시계 차이 기록 순서로 적습니다 [1]. 수집하는 동안 무엇이 더 증거가 될지 계속 따지고, 단계마다 기록하며, 그 자리에 누가 있었는지도 적어 두라고 덧붙입니다 [1]. 수집한 데이터에 체크섬과 암호 서명을 만들어 두는 일은 할 수 있으면 고려하라고 따로 권합니다 [1].

맥에서는 여기에 권한 문제가 하나 더 붙습니다. macOS 10.15 부터 앱이 문서·다운로드·데스크탑 폴더, iCloud Drive, 네트워크 볼륨의 파일에 접근하려면 사용자 동의가 필요하고 [3], 공개 수집 도구인 Jamf Aftermath 도 root 권한과 전체 디스크 접근 권한을 함께 요구합니다 [2]. Aftermath 설명서는 이 권한을 도구를 띄우는 터미널 앱에 주면 된다고 적습니다 [2].

## 한눈에 보기

| 영역 | 보는 방법·위치 | 조건·버전 | 알려 주는 것 |
|---|---|---|---|
| 휘발성 순서 | RFC 3227 2.1절 목록 | 버전과 무관 | 무엇을 먼저 모을지 |
| 프로세스와 열린 파일 | `ps`, `lsof` | 모든 프로세스의 파일을 보려면 root | 실행 중인 프로세스, 부모 관계, 시작 시각, 명령줄, 프로세스가 연 파일 |
| 네트워크 연결 | `netstat`, `lsof -i -nP` | 다른 사용자 프로세스의 소켓은 root | 로컬·원격 주소와 그 소켓을 연 프로세스 |
| 통합 로그 | `log collect` 로 만든 `.logarchive`, 저장소 `/var/db/diagnostics` [4] | 시스템 전체를 모으려면 root [4] | 시스템과 앱이 남긴 이벤트 기록 |
| 전체 디스크 접근 권한 | TCC 데이터베이스, 시스템 설정 | 10.15 부터 사용자 동의 필요, 설정 화면은 13 이상 시스템 설정·12 이하 시스템 환경설정 [3] | 수집 도구가 보호 영역을 읽을 수 있는지, 어떤 앱에 권한을 주었는지 |

여러 영역을 한 번에 모으는 공개 도구의 예로 Jamf Aftermath 가 있습니다. Swift 로 만든 오픈소스(MIT 라이선스) 사고 대응 도구이고 macOS 12.0 이상에서 돌아가며, 이번에 확인한 릴리스는 2.2.1 입니다 [2]. 프로세스, 네트워크 연결과 airport 설정, 조건식으로 고른 통합 로그, TCC·격리(quarantine) 데이터베이스, 구성 프로파일, 셸 기록, 브라우저 기록, launch agent·daemon·cron·로그인 항목 같은 지속성 위치, 시스템 정보, 파일 시각과 메타데이터를 zip 아카이브 하나로 모읍니다 [2]. 결과의 기본 위치가 조사 대상 맥의 `/tmp` 라서, 데이터 변경을 줄이라는 원칙 [1] 에 맞추려면 `-o` 로 저장 위치를 따로 지정할지 먼저 정합니다 [2]. 도구 하나에 기대지 않도록, 도구가 모은 결과는 아래 하위 페이지의 명령으로 직접 확인할 수 있는 만큼 확인합니다.

## 읽는 순서

1. [휘발성 순서 (Order of Volatility)](order-of-volatility.md) — RFC 3227 의 휘발성 목록을 맥의 명령과 위치에 대응시켜 무엇을 먼저 모을지 정합니다.
2. [프로세스와 열린 파일 (ps·lsof)](processes-open-files.md) — `ps` 로 프로세스 목록과 명령줄을, `lsof` 로 프로세스가 연 파일과 지워졌지만 아직 열려 있는 파일을 모읍니다.
3. [네트워크 연결 (Connections)](connections.md) — `netstat` 로 소켓 상태와 라우팅 테이블을 보고, `lsof -i` 로 연결과 프로세스를 잇습니다.
4. [통합 로그 수집 (log collect)](log-collect.md) — `log collect` 로 `.logarchive` 를 만들고 기간·조건식으로 범위를 정하는 방법과 읽는 방법을 봅니다.
5. [전체 디스크 접근 권한 (Full Disk Access)](full-disk-access.md) — 수집 도구에 권한을 주는 방법과 TCC 데이터베이스·MDM 프로필에 남는 권한 기록을 다룹니다.

실제 현장에서는 5번으로 권한부터 확인하고, 1번으로 순서를 정한 뒤 2·3·4번 순서로 모읍니다. 처음 공부하는 사람은 1번부터 차례로 읽으면 됩니다.

## 함께 볼 페이지

라이브 대응이 전체 조사에서 어디에 놓이는지는 [조사 절차 (Investigation Process)](../investigation-process.md) 에, 라이브 대응을 마친 뒤 디스크 이미지를 뜨는 방법은 [맥 증거 확보 (Acquisition)](../evidence-acquisition/index.md) 에, 메모리를 다루는 방법은 [메모리 분석 (Memory Forensics)](../../analysis/memory-forensics/index.md) 에 있습니다. 시스템 시계와 시간대 설정은 [시간대와 시계 설정 (Time Zone·NTP)](../../../02-artifacts/system-account/time-zone.md) 에서 봅니다.

모은 통합 로그의 저장 형식은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md) 에, 로그에서 찾을 이벤트는 [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events/index.md) 에 있습니다. 권한 기록 자체의 해석은 [개인 정보 보호 권한 (TCC)](../../../02-artifacts/credentials/tcc/index.md) 을 봅니다.

모은 결과로 사건을 풀어 가려면 [악성 코드 흔적 분석 (Malware Triage)](../../analysis/malware-triage/index.md), [악성 코드 지속성 찾기 (Persistence)](../../../04-scenarios/incident/persistence.md), [타임라인 작성 (Timeline)](../../analysis/timeline/index.md) 으로 넘어가고, 수집에 쓴 도구와 기록을 보고서에 남기는 방법은 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md) 과 [포렌식 보고서 (Forensic Report)](../../reporting/forensic-report.md) 에서 봅니다.

## 참고 문헌

1. D. Brezinski, T. Killalea, RFC 3227 / BCP 55, Guidelines for Evidence Collection and Archiving (2002-02) — https://www.rfc-editor.org/rfc/rfc3227
2. Jamf, Aftermath README (GitHub) — https://github.com/jamf/aftermath
3. Apple, Apple Platform Security — Controlling app access to files — https://support.apple.com/guide/security/controlling-app-access-to-files-secddd1d86a6/web
4. log(1) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/log.1.html
