---
title: 변경 기록
layout: minimal
nav_exclude: true
---

# 변경 기록

새로 추가되거나 변경된 페이지 기록입니다.

[첫 화면으로 돌아가기](index.md)

## 2026-10-02

- macOS: [셸 시작 파일](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/persistence/shell-startup-files.html)에 컴파일된 zsh 시작 파일 (.zwc) 내용을, [터미널 명령 기록](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/execution/shell-history.html)에 zsh 모듈로 한 작업의 흔적 내용을 추가했습니다.
- Cloud: [감사 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/m365/entra-logs/audit-logs.html)에 Entra ID 외부 인증 방법 등록·변경 흔적 내용을, [Defender 경고와 기록](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/m365/defender-xdr.html)에 Safe Links 주소에서 받는 사람·시각을 꺼내는 내용을 추가했습니다.
- Windows·Cloud·AI: MITRE ATT&CK v19 에 맞춰 전술 이름(Stealth, Defense Impairment)을 고쳤습니다.

## 2026-10-01

- Windows: [저장 비밀번호 (Login Data)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/login-data.html)에 동기화된 패스키 내용을, [WMI 영구 이벤트 구독](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/persistence/wmi-event-subscription.html)에 시각 조건으로 실행되는 구독 내용을, [랜섬웨어는 언제 어떻게 퍼졌나](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/incident/ransomware.html)에 관리용 PC 의 SSHFS-Win·WinFsp 흔적 내용을 추가했습니다.
- Linux: [랜섬웨어가 돌았나](https://urock-ailab.github.io/forensics-handbook/linux/04-scenarios/intrusion/ransomware.html)에 ESXi 데이터스토어가 암호화됐을 때의 조사 흐름을, [VMware ESXi 로그](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/servers/esxi-logs.html)에 SSH 켜짐·SFTP 데이터스토어 탐색 로그 예시를 추가했습니다.
- Android: [디지털 웰빙](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/app-usage/digital-wellbeing.html)에 삼성 디지털 웰빙의 시간대 변경 기록 내용을 추가했습니다.

## 2026-09-30

- Windows: Windows 11 26H2 에 맞춰 [사용자 프로필 목록](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/system-account/profilelist.html)에 관리자 보호 내용을, [섀도 복사본 활용](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/volume-shadow-copy-analysis.html)에 특정 시점 복원 내용을, [윈도 검색 색인 DB](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/file-folder-usage/windows-search/index.html)에 자주 쓰는 폴더 자동 색인 내용을, [드라이버 항목](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/execution/amcache-hve/inventorydriverbinary.html)에 교차 서명 드라이버 신뢰 제거 내용을, [다른 PC 에서 원격 실행했나](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/incident/credential-theft-lateral-movement/psexec-wmi-winrm.html)에 WMIC 제거 내용을 추가했습니다.
- Linux: [VMware ESXi 로그](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/servers/esxi-logs.html) 페이지를 새로 만들었습니다.
- macOS: [저장 위치와 스트림](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/execution/biome/streams.html)에 메뉴 선택 스트림 (App.MenuItem) 내용을, [보관 기간과 로그 수준](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/data-formats/unified-log/retention-levels.html)에 통합 로그가 실제로 남는 기간 내용을 추가했습니다.
- Android: [처음 보는 앱 분석 순서](https://urock-ailab.github.io/forensics-handbook/android/03-techniques/analysis/app-data-analysis/unknown-apps.html)에 제3자 SDK 저장소와 HTTP 캐시 확인 내용을 추가했습니다.

## 2026-09-29

- Windows: [빠른 지원](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/remote-access-tools/quick-assist.html), [사용자 접근 로그 (UAL)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/user-access-logging.html), [테일스케일](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/tailscale.html) 페이지를 새로 만들고, [프로세스와 DLL 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/process-analysis.html)에 MemProcFS 포렌식 모드 내용을 추가했습니다.
- Android: [침입 로깅](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/logs/intrusion-logging.html) 페이지를 새로 만들었습니다.
- Linux: [루트킷 찾기](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/rootkit-detection.html)에 io_uring 과 시스템 호출 감시의 사각지대 내용을, [컨테이너 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/container-acquisition.html)에 체크포인트 아카이브 분석과 연속 스냅숏 내용을 추가했습니다.
- macOS: [VPN 구성](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/network/vpn.html)에 Tailscale 흔적(통합 로그) 내용을, [잠금·잠금 해제·잠자기](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/logs/unified-log-events/lock-sleep.html)에 잠금 해제 방식(Touch ID·암호) 구분 내용을 추가했습니다.
- AI: [메모리에서 AI 흔적 찾기](https://urock-ailab.github.io/forensics-handbook/ai/03-techniques/analysis/memory-analysis.html)에 메모리에서 MCP 활동을 복원하는 논문의 시험 조건과 결과를 추가했습니다.

## 2026-09-28

- AI: [OpenAI API 플랫폼 기록](https://urock-ailab.github.io/forensics-handbook/ai/02-artifacts/network-enterprise/openai-api-platform.html) 페이지를 새로 만들고, [ChatGPT 기업용 감사 기록](https://urock-ailab.github.io/forensics-handbook/ai/02-artifacts/network-enterprise/chatgpt-enterprise.html)에 내용을 추가했습니다.
- macOS: [애플더블 파일](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/appledouble.html), [알림 센터 DB](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/messengers/notification-center.html) 페이지를 새로 만들었습니다.
- iOS: [앱 화면 스냅숏](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/app-usage/app-snapshots.html), [스포트라이트 검색 색인](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/input-assistant/spotlight.html), [locationd 위치 캐시](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/location/locationd-cache.html), [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/logs/fsevents.html), [음성 메모](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/media/voice-memos.html) 페이지를 새로 만들었습니다.
- Android: [권한 사용 기록](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/app-usage/packages/permission-usage.html), [캘린더](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/communications/calendar.html), [원격 제어 앱](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/credentials-security/remote-control-apps.html), [숨김·볼트·앱 잠금 앱](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/credentials-security/vault-apps.html), [구글 Keep](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/google-services/keep.html), [티맵](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/location/tmap.html), [삼성 전원·재부팅·초기화 로그](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/samsung/power-reset-logs.html), [삼성 노트](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/samsung/samsung-notes.html) 페이지를 새로 만들었습니다.

## 2026-09-27

- [Network 핸드북](https://urock-ailab.github.io/forensics-handbook/network/)과 [Crypto 핸드북](https://urock-ailab.github.io/forensics-handbook/crypto/)을 새로 열었습니다.

## 2026-09-25

- 디지털 포렌식 핸드북을 열었습니다.
