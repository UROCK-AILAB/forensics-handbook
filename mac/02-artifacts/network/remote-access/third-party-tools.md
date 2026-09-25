---
title: "원격 제어 앱"
parent: "원격 접속"
grand_parent: "아티팩트 · 네트워크"
nav_order: 1660
---

# 원격 제어 앱 (TeamViewer·AnyDesk)

TeamViewer·AnyDesk 같은 외부 원격 제어 앱은 macOS에 들어 있는 기능이 아니라서 흔적이 앱마다 다르고 두 앱의 맥 흔적 경로를 정리한 공개 자료가 없어서, 이 페이지는 앱 고유 경로 대신 어느 앱에나 남을 수 있는 설치·실행 흔적으로 찾아가는 순서를 다룹니다.

## 무엇을 기록하나 · 왜 생기나

맥에 기본으로 들어 있는 원격 접속은 [화면 공유와 원격 관리 (Screen Sharing·ARD)](screen-sharing-ard.md)와 [SSH 접속 기록 (SSH)](ssh.md)에서 다루고, 이 페이지는 사용자가 따로 설치하는 원격 제어 앱을 다룹니다. 이런 앱은 제작사가 로그와 설정 파일의 위치와 형식을 정하고 버전마다 바꿀 수도 있어서, 앱 자체 기록은 검체와 앱 버전마다 확인해야 합니다.

공개 아티팩트 정의 모음인 ForensicArtifacts 의 macOS 정의 파일 `macos.yaml` 에는 TeamViewer·AnyDesk·VNC 항목이 없고 [1], 앱 정의 파일 `applications.yaml` 에도 AnyDesk·TeamViewer·Chrome Remote Desktop·VNC·Splashtop·LogMeIn·ScreenConnect 항목이 없습니다 [2]. 이 정의에 기대어 수집 대상을 고르는 도구를 쓰면 이런 앱의 파일은 따로 수집되지 않을 수 있어서, 수집 범위를 정할 때 사람이 직접 더해야 합니다.

인터넷에는 두 앱의 맥 로그·설정 경로라며 도는 목록이 있지만 근거가 밝혀진 목록이 없어서, 이 페이지에는 앱 고유 경로를 적지 않습니다. 윈도우판에서 알려진 들어온 연결 목록 파일에 해당하는 파일이 맥판에도 있는지는 검체에서 확인합니다.

## 찾아가는 순서

앱 이름을 몰라도, 또는 앱이 이미 지워졌어도 아래 순서로 다가갈 수 있습니다. 각 단계의 자세한 위치와 해석은 링크한 페이지에 있습니다.

1. **설치 여부** — [설치한 앱과 영수증 (Applications·Receipts)](../../system-account/installed-apps-receipts.md)에서 원격 제어 앱으로 보이는 앱 번들과 설치 기록을 찾고, 번들 ID를 적어 둡니다. 번들 ID는 뒤 단계에서 검색어가 되고, 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다.
2. **들어온 경로** — 설치 파일을 내려받았다면 [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md)과 [다운로드 출처 속성 (kMDItemWhereFroms)](../../filesystem/where-froms.md)에서 언제 어디서 받았는지 찾습니다.
3. **자동 실행** — 앱이 로그인이나 부팅 때 스스로 뜨도록 등록한 항목이 있는지 [실행 에이전트·데몬 (LaunchAgents·LaunchDaemons)](../../persistence/launchd/index.md)과 [로그인 항목 (Login Items)](../../persistence/login-items.md)에서 번들 ID와 앱 이름으로 찾습니다.
4. **권한** — 화면을 내보내거나 원격 입력으로 조작하는 앱이라면 화면 녹화나 손쉬운 사용 권한을 받은 기록이 있는지 [개인 정보 보호 권한 (TCC)](../../credentials/tcc/index.md)에서 번들 ID로 찾습니다.
5. **실행과 통신** — 앱이 앞에 나와 있던 구간은 [KnowledgeC (knowledgeC.db)](../../execution/knowledgec/index.md)와 [바이옴 (Biome)](../../execution/biome/index.md)에서, 실행된 프로세스는 [통합 로그의 프로세스 실행 기록 (Process Events)](../../execution/unified-log-process.md)에서, 앱이 주고받은 데이터 양은 [앱별 네트워크 사용량 (netusage)](../netusage.md)에서 찾습니다.
6. **앱 자체 기록** — 앞 단계에서 얻은 번들 ID와 앱 이름으로 사용자 홈의 `~/Library` 와 시스템의 `/Library` 아래를 검색해 로그·설정 파일을 찾습니다. 찾은 경로는 검체의 macOS 버전, 앱 버전과 함께 적어 두고, 파일 안의 칸이나 문구를 해석할 때는 같은 버전의 앱으로 알려진 동작을 해 보고 기록이 어떻게 남는지 먼저 확인합니다.

## 증거로서 의미

### 증명하는 것

위 순서에서 찾은 기록은 원격 제어 앱이 이 맥에 설치되었는지, 언제 어디서 받았는지, 자동으로 뜨게 등록되었는지, 화면 관련 권한을 받았는지, 언제 실행되어 얼마나 통신했는지를 보여 줍니다. 앱마다 다른 로그를 해석하기 전에도 이 사실들은 macOS 공통 기록으로 세울 수 있어서, 보고서의 뼈대가 됩니다.

### 증명하지 못하는 것

공통 기록만으로는 누가 어디서 이 맥에 들어왔는지, 들어온 연결인지 이 맥에서 건 연결인지, 연결한 뒤 무엇을 했는지 알 수 없습니다. 그 내용은 앱 자체 로그에 기대야 하고, 그 형식은 앱과 버전마다 검체에서 확인합니다. 통신량이 있다는 것도 그 앱이 데이터를 주고받았다는 기록이지 원격 세션이 열렸다는 기록이 아닙니다.

보고서에는 "외부인이 원격 제어 앱으로 접속했다" 대신 "이 번들 ID의 앱이 설치되어 있고, 이 시간대에 실행되어 이만큼 송신한 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

앱 자체 로그의 시각이 UTC인지 현지 시각인지는 앱마다 다를 수 있습니다. 로그 시각을 쓰기 전에 같은 사건이 남은 macOS 공통 기록(프로세스 실행 시각, 네트워크 사용량 시각)과 맞춰 시차를 확인하고, 시간대 설정은 [시간대와 시계 설정 (Time Zone·NTP)](../../system-account/time-zone.md)과 함께 봅니다.

## 함정과 한계

인터넷에 도는 경로 목록은 윈도우판 경로가 섞여 있거나 예전 앱 버전 기준일 수 있어서, 검체에서 그 경로가 비어 있다고 앱을 쓰지 않았다고 읽지 않습니다. 설치하지 않고 실행하는 형태로 앱을 썼다면 설치 기록 없이 실행과 통신 기록만 남을 수 있어서, 1단계에서 아무것도 찾지 못해도 5단계까지 봅니다.

앱을 지웠다면 앱 번들과 앱 자체 로그는 사라져도 다운로드 기록, 권한 기록, 실행과 통신 기록 같은 공통 기록은 남아 있을 수 있습니다. 지운 시점과 방법은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)와 [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md)에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [설치한 앱과 영수증 (Applications·Receipts)](../../system-account/installed-apps-receipts.md) | 앱 번들과 설치 기록 |
| [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md) | 설치 파일을 받은 시각과 출처 |
| [개인 정보 보호 권한 (TCC)](../../credentials/tcc/index.md) | 화면 녹화·손쉬운 사용 권한 |
| [앱별 네트워크 사용량 (netusage)](../netusage.md) | 앱이 주고받은 데이터 양 |
| [원격 접속 (Remote Access)](index.md) | 같은 시간대의 로그인 기록 파일(utmpx·lastlog) |

여러 기록을 엮어 침입 여부를 판단하는 흐름은 [원격 접속 침입 확인 (Remote Intrusion)](../../../04-scenarios/incident/remote-intrusion.md)에서, 자료가 밖으로 나갔는지 판단하는 흐름은 [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)에서 다룹니다.

## 실습

macOS 공개 검체(NIST CFReDS 등)에서 아래 질문을 풀어 봅니다.

1. 설치된 앱 가운데 원격 제어 앱으로 보이는 것이 있는가, 번들 ID는 무엇인가?
2. 그 앱의 설치 파일을 언제 어디서 받았다는 기록이 있는가?
3. 그 번들 ID로 등록된 자동 실행 항목이나 TCC 권한 항목이 있는가?
4. 그 앱이 가장 많이 통신한 날은 언제이고, 그날 앞에 나와 있던 구간은 어떻게 되는가?

## 참고 문헌

1. ForensicArtifacts, "artifacts/data/macos.yaml" — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. ForensicArtifacts, "artifacts/data/applications.yaml" — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/applications.yaml
