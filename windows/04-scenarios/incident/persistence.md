---
title: "악성코드 지속성(자동실행) 찾기"
parent: "시나리오 · 침해 사고"
nav_order: 3690
---

# 악성코드 지속성(자동실행) 찾기 (Persistence)

이 페이지는 PC 를 다시 켜거나 다시 로그온해도 악성코드가 다시 실행되도록 남긴 자동실행 항목을 찾는 순서를 다룹니다. 이렇게 계속 머무르려고 남긴 장치를 지속성 (Persistence) 이라고 부릅니다. 자동실행 위치를 종류별로 훑고, 등록한 시각과 실제로 실행됐는지를 따로 확인합니다. 위치마다의 키·폴더·칸은 각 아티팩트 페이지에 있습니다. 이 페이지는 어떤 순서로 보고 어떻게 판단하는지를 다룹니다.

## 조사 질문

- 재부팅이나 로그온 때 자동으로 실행되도록 등록된 의심 항목이 있습니까?
- 그 항목은 언제, 어느 계정으로, 어떤 방법으로 등록됐습니까?
- 항목이 가리키는 프로그램이 실제로 실행됐습니까?
- 지금은 없지만 예전에 있다가 지워진 항목이 있습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | 버전과 빌드를 [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 먼저 적습니다. |
| 시간대 | 이벤트 로그와 레지스트리 시각을 한 기준으로 맞춥니다. [시간대 설정](../../02-artifacts/system-account/time-zone.md) 을 읽습니다. Bias 값을 부호 있는 수로 읽는 법은 [이 파일을 누가 언제 열었나](../activity/file-access.md) 의 "먼저 확인할 것" 에 있습니다. |
| 사용자 | 자동실행 항목에는 사용자마다 따로 있는 것이 있습니다[1]. [사용자 프로필 목록](../../02-artifacts/system-account/profilelist.md) 으로 모든 프로필을 찾아 둡니다. |
| 수집 범위 | SYSTEM·SOFTWARE 하이브, 모든 사용자의 NTUSER.DAT·UsrClass.dat, System32\Tasks 폴더, WMI 저장소, 이벤트 로그를 확보합니다. 한 곳이라도 빠지면 그 위치의 항목은 볼 수 없습니다. |
| 감사 정책·Sysmon | 이벤트 기록은 감사 정책과 Sysmon 설정에 따라 남기도 하고 안 남기도 합니다. 기록이 없다고 해서 등록이 없었다고 읽지 않습니다. [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 확인합니다. |
| 섀도 복사본 | 지워진 항목은 예전 시점의 하이브에서 찾을 수 있습니다. 섀도 복사본이 있는지 먼저 봅니다([섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md)). |

## 자동실행 위치 종류

Microsoft Sysinternals 의 Autoruns 문서는 자동실행 위치로 시작 프로그램 폴더, Run·RunOnce 와 그 밖의 레지스트리 키, 탐색기 셸 확장, 툴바, 브라우저 도우미 개체 (Browser Helper Object, BHO), Winlogon 알림, 자동 시작 서비스를 듭니다[1]. 같은 문서는 AppInit DLL, 이미지 하이재크 (Image Hijacks), 부트 실행 이미지, Winsock 계층 서비스 공급자, 미디어 코덱도 듭니다[1].

아래 표는 이 위키가 위치를 종류별로 묶은 것입니다. 오른쪽 열의 페이지에 위치마다의 키·폴더·칸이 있습니다.

| 위치 종류 | 예 | 링크 |
|---|---|---|
| 로그온 자동실행 | Run·RunOnce 키, 시작 프로그램 폴더 | [로그온 자동실행](../../02-artifacts/persistence/run-runonce-startup-folder.md) |
| 서비스·드라이버 | 자동 시작 서비스, 드라이버 | [서비스·드라이버](../../02-artifacts/persistence/services-drivers.md) · [서비스 설치](../../02-artifacts/event-logs/7045-4697.md) |
| 예약 작업 | 작업 스케줄러에 등록한 작업 | [예약 작업](../../02-artifacts/persistence/scheduled-tasks/index.md) · [숨긴 예약 작업 찾기](../../02-artifacts/persistence/scheduled-tasks/sd.md) · [예약 작업 이벤트](../../02-artifacts/event-logs/taskscheduler-4698.md) |
| WMI 항목 | WMI 영구 이벤트 구독 | [WMI 영구 이벤트 구독](../../02-artifacts/persistence/wmi-event-subscription.md) |
| BITS 작업 | BITS 전송 작업 | [BITS 전송 작업](../../02-artifacts/persistence/bits-jobs-qmgr-db.md) |
| Winlogon·이미지 하이재크·AppInit DLL | Winlogon 항목, 이미지 하이재크, AppInit DLL | [기타 자동실행 위치](../../02-artifacts/persistence/winlogon-ifeo-appinit-dlls.md) |
| 그 밖의 위치 | 탐색기 추가 기능, IE 추가 기능, 부트 실행, Known DLLs, Winsock·네트워크 공급자, LSA 보안 공급자, 프린터 모니터 DLL, 코덱 | — |

"그 밖의 위치" 줄은 Autoruns 명령줄판이 나누는 범주에서 옮긴 것입니다[1].

**공개 도구로 한 번에 훑기.** Autoruns 는 자동실행 위치를 한 번에 훑는 공개 도구의 한 예입니다.

- 서명된 Microsoft 항목을 숨기는 선택이 있습니다[1].
- 명령줄판에는 디지털 서명 확인(-s), 파일 해시(-h), 오프라인 Windows 시스템 검사(-z) 선택지가 있습니다[1].
- 사용자별 항목을 볼 수 있습니다[1]. 사용자 자리에 '*' 를 주면 모든 프로필을 봅니다[1].
- 명령줄판의 -a 선택지로 범주를 고릅니다[1]. 예를 들어 로그온 시작은 l(기본값), 자동 시작 서비스와 꺼지지 않은 드라이버는 s, 예약 작업은 t, WMI 항목은 m, Winlogon 항목은 w 입니다[1].
- 서명 확인과 Microsoft 항목 숨기기는 살펴볼 항목을 줄이는 방법입니다. 악성 여부를 정하지는 않습니다. 아래 사례처럼 정상 서명된 원격 관리 프로그램도 서비스로 자동 실행됩니다.

## 공개 사례에서 본 지속성

The DFIR Report 사례에서는 원격 관리 프로그램 ScreenConnect 가 자동 시작 서비스로 남았고, 이 설치는 System 로그의 7045("A service was installed in the system")와 Sysmon 이벤트 13(레지스트리 값 설정)에 흔적을 남겼습니다[2]. 같은 사례에서 다른 원격 관리 프로그램(Atera)도 자동 시작 서비스로 등록됐고, 이 등록도 7045 에 남았습니다[2]. MITRE 는 원격 접속 도구의 설치 과정이 흔히 Windows 서비스로 지속성을 만든다고 적습니다[3]. 이 사례의 서비스 종류·시작 방식·실행 경로는 [스크린커넥트](../../02-artifacts/network/remote-access-tools/screenconnect.md) 에 있습니다.

## 등록 시각과 실행 여부

**등록 시각.**

- 서비스는 설치 이벤트 7045 로 설치 시각을 잡습니다[2]. 칸은 [서비스 설치](../../02-artifacts/event-logs/7045-4697.md) 에 있습니다.
- 예약 작업은 [예약 작업 이벤트](../../02-artifacts/event-logs/taskscheduler-4698.md) 로 등록 시각을 잡습니다.
- Sysmon 이 있으면 레지스트리 값 설정(이벤트 13)으로 자동실행 값을 쓴 시각을 봅니다. 칸은 [레지스트리 변경 (Sysmon 12·13·14)](../../02-artifacts/event-logs/sysmon/12-13-14.md) 에 있습니다.
- 레지스트리 키의 마지막 기록 시각을 쓸 때는 그 시각이 무엇을 알려 주고 무엇을 알려 주지 않는지 먼저 확인합니다. [키 마지막 기록 시각](../../01-foundations/database-log-formats/registry-hive/last-write-time.md) 에 정리돼 있습니다.

**가리키는 파일.**

- 항목이 가리키는 실행 파일의 경로, 서명, 해시를 봅니다. 읽는 법은 [실행 파일 메타데이터](../../02-artifacts/embedded-metadata/pe-header-version-info-digital-signature.md) 와 [의심 실행 파일 선별](../../03-techniques/analysis/code-signing-yara.md) 에 있습니다.
- 사용자가 쓸 수 있는 폴더(AppData·Temp·ProgramData)를 가리키는 항목을 먼저 봅니다.

**실행 여부.**

- 등록과 실행은 다른 일이라서 가리키는 파일이 실제로 실행됐는지는 프리페치·AmCache·4688·Sysmon 1 같은 실행 흔적으로 따로 확인합니다. 순서는 [어떤 프로그램을 언제 실행했나](../activity/program-execution.md) 에 있습니다.

## 분석 흐름

1. 수집 범위를 확인합니다. SYSTEM·SOFTWARE 하이브, 모든 사용자의 NTUSER.DAT·UsrClass.dat, System32\Tasks, WMI 저장소, 이벤트 로그가 모두 있는지 봅니다.
2. 위치 종류별로 목록을 뽑습니다. 로그온 자동실행, 서비스, 예약 작업, WMI 구독, BITS, Winlogon·이미지 하이재크·AppInit 을 빠짐없이 봅니다.
3. 항목이 가리키는 실행 파일의 경로·서명·해시를 봅니다. 사용자가 쓸 수 있는 폴더를 가리키는 항목부터 봅니다.
4. 의심 항목의 등록 시각을 이벤트로 잡습니다. 서비스는 7045, 예약 작업은 예약 작업 이벤트, 레지스트리 값은 Sysmon 13 을 봅니다.
5. 그 실행 파일이 실제로 실행됐는지 실행 흔적으로 확인합니다.
6. 등록 직전·직후를 [타임라인](../../03-techniques/analysis/timeline/index.md) 으로 묶습니다. 어느 계정과 어느 프로세스가 등록했는지 찾습니다.
7. 지금 목록에 없는 항목은 섀도 복사본의 예전 하이브와 [지워진 키·값 복구](../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md) 로 찾습니다.
8. 등록한 프로그램이 처음 들어온 길은 [악성코드는 어디서 들어왔나](initial-access.md) 로 이어 갑니다. 원격 관리 프로그램이면 [원격 제어 프로그램으로 누가 조작했나](remote-access-tool-abuse.md) 로 이어 갑니다.

## 흔한 오판

1. **자동실행 항목이 있으니 실행됐다고 봅니다.** 등록과 실행은 다릅니다. 실행은 실행 흔적으로 따로 확인합니다.
2. **정상 서명 프로그램이니 문제없다고 봅니다.** 공개 사례에서는 정상 원격 관리 프로그램이 서비스로 등록돼 공격자의 접속 통로가 됐습니다[2][3].
3. **지금 목록에 없으니 지속성이 없었다고 봅니다.** 공격자가 흔적을 지웠을 수 있습니다. 공개 사례에서도 파일 삭제 흔적(Sysmon 23, del 명령)이 있었습니다[2]. 이벤트, 섀도 복사본, 지워진 키 복구로 과거 상태를 봅니다.
4. **키 마지막 기록 시각을 특정 값을 쓴 시각으로 씁니다.** 그 시각이 어디까지 말해 주는지는 [키 마지막 기록 시각](../../01-foundations/database-log-formats/registry-hive/last-write-time.md) 에서 확인하고 씁니다.
5. **도구 하나의 목록만 보고 끝냅니다.** 도구마다 보는 범위가 정해져 있습니다. 위 표의 위치 종류를 하나씩 지워 가며 확인합니다.

## 보고서 문장 예

- 쓰지 않을 문장: "공격자가 ○○ 에 악성 서비스를 만들어 지속성을 확보했습니다."
- 쓸 문장: "System 로그에 ○○(UTC) 의 7045 이벤트가 있습니다. 서비스 이름은 ○○ 이고, 시작 방식은 자동 시작이며, 실행 경로는 `○○` 입니다. 이 경로의 파일에는 ○○ 의 디지털 서명이 있습니다. 이 파일의 프리페치 기록에 ○○(UTC) 의 실행 흔적이 있습니다. 이 기록은 이 시각에 이 서비스가 설치됐고, 그 뒤 이 파일이 실행됐음을 보여 줍니다. 서비스를 설치한 사람은 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [로그온 자동실행](../../02-artifacts/persistence/run-runonce-startup-folder.md) · [서비스·드라이버](../../02-artifacts/persistence/services-drivers.md) · [예약 작업](../../02-artifacts/persistence/scheduled-tasks/index.md) · [숨긴 예약 작업 찾기](../../02-artifacts/persistence/scheduled-tasks/sd.md) — 자주 쓰는 자동실행 위치입니다.
- [WMI 영구 이벤트 구독](../../02-artifacts/persistence/wmi-event-subscription.md) · [BITS 전송 작업](../../02-artifacts/persistence/bits-jobs-qmgr-db.md) · [기타 자동실행 위치](../../02-artifacts/persistence/winlogon-ifeo-appinit-dlls.md) — 덜 드러나는 자동실행 위치입니다.
- [서비스 설치](../../02-artifacts/event-logs/7045-4697.md) · [예약 작업 이벤트](../../02-artifacts/event-logs/taskscheduler-4698.md) · [레지스트리 변경 (Sysmon 12·13·14)](../../02-artifacts/event-logs/sysmon/12-13-14.md) — 등록 시각을 잡는 이벤트입니다.
- [실행 파일 메타데이터](../../02-artifacts/embedded-metadata/pe-header-version-info-digital-signature.md) · [의심 실행 파일 선별](../../03-techniques/analysis/code-signing-yara.md) — 가리키는 파일을 가립니다.
- [키 마지막 기록 시각](../../01-foundations/database-log-formats/registry-hive/last-write-time.md) · [지워진 키·값 복구](../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md) · [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 시각과 지워진 항목을 봅니다.
- [어떤 프로그램을 언제 실행했나](../activity/program-execution.md) — 등록한 프로그램이 실행됐는지 확인합니다.
- [원격 제어 프로그램으로 누가 조작했나](remote-access-tool-abuse.md) — 서비스로 남은 원격 관리 프로그램을 이어서 봅니다.

## 참고 문헌

1. Microsoft Learn (Sysinternals), "Autoruns" (2026-06-17 게시) — https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns
2. The DFIR Report, "From ScreenConnect to Hive Ransomware in 61 hours" (2023-09-25) — https://thedfirreport.com/2023/09/25/from-screenconnect-to-hive-ransomware-in-61-hours/
3. MITRE ATT&CK, "Remote Access Tools, Technique T1219" (v3.0, 2026-05-12 수정) — https://attack.mitre.org/techniques/T1219/
