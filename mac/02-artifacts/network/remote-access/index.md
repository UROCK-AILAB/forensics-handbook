---
title: "원격 접속"
parent: "아티팩트 · 네트워크"
nav_order: 1630
has_children: true
has_toc: false
---

# 원격 접속 (Remote Access)

맥에 원격으로 들어오거나 원격으로 다른 컴퓨터에 나가는 길은 화면 공유·원격 관리, SSH, 외부 원격 제어 앱 세 가지이고, 방식마다 흔적이 다른 파일에 남아서 공유 설정과 로그인 기록 파일을 먼저 보고 방식별 페이지로 들어갑니다.

## 왜 중요한가

원격 접속이 있었다면 그 맥에서 일어난 일을 맥 앞에 앉은 사람이 했다고 단정할 수 없어서, 사용자를 판별하는 조사와 침입 여부를 판단하는 조사 모두 원격 접속 흔적을 먼저 확인합니다. 맥에 들어 있는 원격 접속 서비스는 Apple 메뉴의 시스템 설정에서 일반, 공유 (Sharing) 순서로 들어간 한 화면에서 켜고 끕니다. macOS High Sierra부터 macOS 27 Golden Gate까지 이 화면에서 설정합니다 [1]. 공유 화면에서 켠 서비스가 어느 plist나 실행 항목에 남는지는 실제 기기에서 확인해야 합니다.

모든 원격 접속을 한 파일에 정리해 두는 기록은 알려진 것이 없어서, 방식마다 따로 흔적을 읽고 로그인 기록 파일과 통합 로그로 시간대를 맞춥니다.

## 한눈에 보기

| 흔적 | 위치 | macOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 공유 설정 화면 | 시스템 설정 → 일반 → 공유 [1] | High Sierra부터 macOS 27 Golden Gate까지 [1] | 원격 로그인 등 원격 접속 서비스를 켜는 곳 |
| 로그인 기록(utmpx) | `/private/var/run/utmpx` [2] | 실제 기기에서 확인 | 로그인 기록 [2] |
| 로그인 기록(lastlog) | `/private/var/log/lastlog` [2] | 실제 기기에서 확인 | 마지막 로그인 기록 [2] |
| 화면 공유 연결 기록 | 사용자 홈의 화면 공유 앱 컨테이너 | 실제 기기에서 확인 | 연결한 상대 주소·로그인 이름·마지막 연결 날짜 |
| 원격 관리(ARD) 파일 | `/private/var/db/RemoteManagement/` 아래 | 실제 기기에서 확인 | 관리하는 쪽·관리받는 쪽 DB와 캐시 |
| SSH 파일 | `~/.ssh/`, `/etc/ssh/` | 실제 기기에서 확인 | 로그인에 쓸 수 있는 키, 접속했던 호스트, 설정 |
| 외부 원격 제어 앱 | 앱마다 다름 | 앱 버전마다 확인 | 설치·자동 실행·권한·실행·통신 흔적 |

utmpx와 lastlog는 세 방식 모두에서 함께 볼 로그인 기록 파일이라 여기에 한 번만 적습니다. ForensicArtifacts 정의 이름은 `MacOSUtmpxFile`, `MacOSLastlogFile` 이고, `/var/run/utmpx`, `/var/log/lastlog` 형태의 경로도 함께 잡습니다 [2]. 도구가 풀어 준 결과를 그대로 쓰기 전에, 알려진 시각에 로그인해 보고 레코드 구조와 시각 기준, `last` 명령이 어느 파일을 읽는지, 최근 macOS에서 lastlog가 실제로 쓰이는지, SSH·화면 공유 세션이 이 파일에 각각 어떻게 남는지를 먼저 확인합니다. 그 방법은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)에 있습니다.

통합 로그에서 원격 접속을 찾는 프로세스·서브시스템 이름과 로그 문구는 실제 기기에서 확인한 뒤에 쓰고, 검색어를 정하는 법은 [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md)을 따릅니다.

## 읽는 순서

1. [화면 공유와 원격 관리 (Screen Sharing·ARD)](screen-sharing-ard.md) — 화면 공유 앱의 연결 기록 plist를 푸는 법, 원격 관리(ARD)의 관리하는 쪽·관리받는 쪽 파일, kickstart 실행 흔적을 찾을 때 쓸 이름을 다룹니다.
2. [SSH 접속 기록 (SSH)](ssh.md) — 원격 로그인 설정, 받는 쪽의 authorized_keys와 sshd 파일, 거는 쪽의 known_hosts와 설정 파일을 읽고, 무엇을 증명하지 못하는지 정리합니다.
3. [원격 제어 앱 (TeamViewer·AnyDesk)](third-party-tools.md) — 앱마다 흔적 경로가 다른 외부 원격 제어 앱을 설치·다운로드·자동 실행·권한·실행·통신 기록으로 찾아가는 순서를 다룹니다.

## 함께 볼 페이지

- [원격 접속 침입 확인 (Remote Intrusion)](../../../04-scenarios/incident/remote-intrusion.md) — 조사 시나리오
- [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md) — 조사 시나리오
- [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](../../../04-scenarios/activity/usage-time.md) — 로그인 기록을 사용 시간과 맞춰 볼 때
- [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md) — 접속 시간대 전후의 이벤트
- [SSH 키와 접속 목록 (SSH Keys·known_hosts)](../../credentials/ssh-keys.md) — SSH 키 파일의 형식
- [개인 정보 보호 권한 (TCC)](../../credentials/tcc/index.md) — 원격 제어 앱이 받은 권한
- [네트워크 인터페이스와 설정 (SystemConfiguration)](../network-interfaces.md) — 접속 당시의 네트워크
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) — 여러 흔적을 한 줄로 엮을 때

## 참고 문헌

1. Apple Support, macOS 사용 설명서 "Allow a remote computer to access your Mac" — https://support.apple.com/guide/mac-help/allow-a-remote-computer-to-access-your-mac-mchlp1066/mac
2. ForensicArtifacts, "artifacts/data/macos.yaml" — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
