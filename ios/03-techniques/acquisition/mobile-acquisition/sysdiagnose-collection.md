---
title: "sysdiagnose로 수집"
parent: "모바일 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1200
---

# sysdiagnose로 수집 (sysdiagnose Collection)

아이폰에서 버튼 조합으로 진단 묶음 sysdiagnose 를 만들고 기기 밖으로 꺼내는 방법을 다룹니다. 이 묶음에는 로컬 백업에 담기지 않는 통합 로그 스냅숏과 여러 진단 로그가 들어 있습니다.

## 언제 쓰나

통합 로그, 프로세스 목록, 종료·재시동 기록, 앱 설치 로그처럼 시스템 쪽 기록이 조사에 필요할 때 씁니다. 스파이웨어 감염을 점검하는 흐름은 [악성 코드·스파이웨어 흔적](../../analysis/spyware-triage/index.md)에서 다룹니다. 통합 로그 항목은 짧게는 몇 분 만에 사라지기도 해서(아래 "담기는 기간"), 필요하다고 판단하면 수집 초기에 만듭니다. 다른 수집 방식과의 비교는 [수집 방식 비교](methods.md)에 있습니다.

## 절차

1. 볼륨 버튼 두 개와 측면(또는 상단) 버튼을 동시에 눌렀다가 뗍니다(약 250밀리초). 아이폰은 스크린숏을 찍을 때와 같은 화면 효과와 짧은 진동으로 알려 주고, 아이패드는 진동이 없습니다. 수집은 버튼을 뗄 때 시작합니다.
2. 버튼 조합이 어려우면 손쉬운 사용 → 터치 → AssistiveTouch 에서 메뉴에 "분석(Analytics)" 을 넣고 그 메뉴로 실행합니다.
3. 누른 시각과 방법을 수집 기록에 적고, 완료까지 약 10분 기다립니다.
4. 결과물은 기기 안 아래 위치에 gzip 으로 압축한 tar 파일 하나로 생깁니다.

   ```
   /private/var/mobile/Library/Logs/CrashReporter/DiagnosticLogs/sysdiagnose
   ```

5. 결과물을 컴퓨터로 꺼냅니다. 출처에서 설명한 도구 방식으로 꺼내려면 기기가 잠금 해제돼 있고 컴퓨터와 페어링돼 있어야 하며, Windows 에서는 Apple 기기 앱(예전 iTunes)이 필요하고 30분 넘게 걸릴 수 있습니다. 잠긴 기기의 데이터 연결 제한은 [압수와 보관](seizure-handling.md)의 USB 제한 모드 절을 봅니다.
6. 꺼낸 파일의 해시를 남깁니다([결과물 형식과 해시](formats-hash.md)).

## 파일 이름 읽기

출처에 실린 예시 이름은 다음과 같고, 날짜·시각·UTC 와의 차이·OS·기종·빌드 순으로 붙습니다.

```
sysdiagnose_2025.06.24_11-01-29+0200_iPhone-OS_iPhone_22F76.tar.gz
            날짜       시각     UTC차 OS         기종   빌드
```

이름 속 시각은 기기의 현지 시각이고 뒤에 UTC 와의 차이가 붙어서, 만든 시각을 UTC 로 바로 바꿀 수 있습니다. 이 시각은 수집 기록에 적은 시각과 맞춰 봅니다.

## 담기는 것

sysdiagnose 에는 통합 로그 스냅숏(`system_logs.logarchive`), 크래시 보고서, 프로세스 목록(`ps.txt`), 메모리 사용 정보, 커널 로그, Wi‑Fi 연결 로그, Mobile Installation 로그, 프로세스와 재시동을 남기는 Shutdown Log 가 들어 있습니다. 묶음 안의 파일 구조는 [sysdiagnose 묶음](../../../01-foundations/backups/sysdiagnose.md)에서, 각 로그에서 무엇을 찾는지는 [sysdiagnose 안의 로그](../../../02-artifacts/logs/sysdiagnose-logs.md)에서 다룹니다.

## 담기는 기간

통합 로그 항목은 보존 기간(TTL)이 짧아 몇 분이나 몇 시간 만에 사라지는 것도 있어서, 스냅숏에는 대개 만든 날 정도의 기록만 담깁니다. 반면 출처의 시험 기기에서 Wi‑Fi 로그는 몇 년 치가 남아 있었고 종료 기록(Shutdown Log)은 기기를 처음 개통한 때까지 거슬러 올라갔지만, Mobile Installation 로그는 열흘 치뿐이었습니다. 그래서 같은 sysdiagnose 안에서도 로그마다 거슬러 볼 수 있는 기간이 다르고, 통합 로그에 사건 시각의 기록이 없다고 해서 그때 아무 일도 없었다고 볼 수는 없습니다. 통합 로그 형식은 [통합 로그 형식](../../../01-foundations/data-formats/unified-log.md)에서 다룹니다.

## 도구

공개 도구 iLEAPP 는 sysdiagnose 묶음을 입력으로 받습니다(`-t tar` 또는 `-t gz`). 다만 `system_logs.logarchive` 는 JSON 으로 바꾸지 않으면 iLEAPP 가 제대로 처리하지 못해서, 통합 로그는 따로 변환해 봅니다. 여러 도구로 결과를 견줘 보는 방법은 [도구 검증](../../reporting/tool-validation.md)에서 다룹니다.

## 백업에 남는 진단 흔적

sysdiagnose 결과물 자체가 로컬 백업에 들어가는지는 확인하지 못했지만, 관찰한 백업에는 진단 기능과 관련된 도메인과 설정 파일이 있었습니다. (확인 범위: iPhone 13 mini, iOS 27.0)

```
AppDomainPlugin-com.apple.DiagnosticExtensions.sysdiagnose   (항목 4개)
AppDomainPlugin-com.apple.DiagnosticExtensions.CrashLogs
SysSharedContainerDomain-systemgroup.com.apple.osanalytics
RootDomain :: Library/Preferences/com.apple.CrashReporter.plist
  ExcResourceDiagInfo_<프로세스 이름> (datetime)  여러 개
  bbtrace.enabled, bbtrace.data_logging, bbtrace.cellularloggingallowed,
  bbtrace.file, bbtrace.history, bbtrace.bootsessionuuid,
  profile.enabled, systemlogs.mode 등
```

관찰 메모에는 도메인 이름과 키 이름만 있어서 각 키의 뜻은 확인하지 못했습니다. 크래시·진단 기록 전반은 [충돌·진단 기록](../../../02-artifacts/app-usage/diagnostics.md)에서 다룹니다.

## 함정과 한계

sysdiagnose 는 조사자가 버튼을 눌러 기기에서 새로 만드는 자료라서, 만들면 기기 안에 결과물 파일이 새로 생깁니다. 타임라인에서는 수집 시각 전후의 진단 관련 기록을 조사자의 조작으로 구분해 둡니다. 설정 앱에서 결과물을 보는 경로와 AirDrop·Finder 로 옮기는 방법은 이번에 연 자료로 확인하지 못해서 적지 않았습니다.

## 결과를 어떻게 해석하나

sysdiagnose 는 만든 시점의 스냅숏이라서, 보고서에는 "이 시각에 만든 sysdiagnose 의 어느 로그에 이런 기록이 있다" 처럼 묶음을 만든 시각과 로그 이름을 함께 씁니다. 로그마다 거슬러 볼 수 있는 기간이 다르니, 기록이 없다는 결론을 쓸 때는 그 로그가 해당 시각을 담는 기간인지부터 밝힙니다.

## 참고 문헌

- Extracting and Analyzing Apple sysdiagnose Logs — ElcomSoft blog (2025-06) — https://blog.elcomsoft.com/2025/06/extracting-and-analyzing-apple-unified-logs/
