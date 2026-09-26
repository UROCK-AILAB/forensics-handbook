---
title: "해석 함정"
parent: "파일 시스템 이벤트"
grand_parent: "아티팩트 · 파일 시스템"
nav_order: 960
---

# 해석 함정 (Pitfalls)

FSEvents 기록에는 시각이 없고, 짧은 시간 안의 변경이 한 레코드로 합쳐지며, 기록이 빠지거나 지워질 수도 있습니다. 날짜를 어떻게 어림했는지, 한 레코드를 몇 번의 동작으로 볼지, 도구가 무엇을 읽고 무엇을 놓쳤는지를 확인한 뒤에 보고서에 옮깁니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 그 볼륨의 어떤 경로에 어떤 종류의 변경(만들기·지우기·이름 바꾸기 등)이 기록됐다는 것 | 변경이 일어난 정확한 시각 |
| 같은 볼륨 기록 안에서 이벤트 ID로 본 앞뒤 순서 | 한 레코드가 동작 한 번이라는 것 |
| 지금은 없는 파일이나 폴더의 경로가 한때 기록됐다는 것 | 어느 프로그램이나 사람이 바꿨는지 |
| 외장 장치에서 나온 기록이라면 그 장치가 어떤 Mac에 꽂혔던 적이 있다는 것 [6] | 모든 변경이 빠짐없이 남았다는 것 |

플래그별 뜻은 [이벤트 플래그 읽기 (Flags)](flags.md)에, 이벤트 ID가 매겨지는 방식은 [파일 형식 (.fseventsd)](format.md)에 있습니다.

## 시각이 없다

레코드에는 시각 필드가 없어서 [1], 도구가 보여 주는 날짜는 모두 다른 곳에서 빌려 온 값입니다. 어느 값을 빌려 왔는지에 따라 뜻이 달라집니다.

plaso는 각 이벤트에 그 fseventsd 파일 항목의 수정 시각("file entry last modification date and time")을 붙입니다 [5]. 이 값은 사건이 일어난 시각이 아니라 이벤트 파일이 마지막으로 쓰인 시각이라서, 한 파일에 든 레코드가 모두 같은 시각을 받습니다.

FSEventsParser는 `Created` 플래그가 붙은 로그 파일 경로에서 파일 이름 속 날짜를 뽑고, 그 날짜를 이벤트 ID와 짝지어 날짜 범위를 만듭니다 [2]. 날짜를 뽑는 경로는 아래와 같고, 결과는 `approx_dates_plus_minus_one_day` 열에 들어갑니다 [2].

```
private/var/log/asl/Logs/aslmanager
mobile/Library/Logs/CrashReporter/DiagnosticLogs/security.log
private/var/log/asl/AUX
private/var/log/asl
private/var/log/DiagnosticMessages
private/var/log/com.apple.clouddocs.asl
private/var/log/powermanagement
private/var/audit
```

이렇게 얻은 값은 날짜뿐이고 시간이 없으며, 시간대 차이로 하루가 어긋날 수 있습니다 [6]. 로그 날짜를 얻지 못하면 FSEventsParser는 이벤트 파일의 수정 시각을 쓰고, 그것도 없으면 "Unknown" 으로 둡니다 [2]. 보고서에는 어느 방법으로 얻은 날짜인지를 함께 적습니다.

수집할 때 이벤트 파일의 수정 시각이 바뀌면 날짜 추정이 무너집니다. FSEventsParser는 첫 파일과 마지막 파일의 수정 시각이 같으면 수정 시각이 보존되지 않은 것으로 보고 날짜 추정에 쓰지 않습니다 [2]. 파일을 복사해서 분석할 때는 수정 시각을 보존하는 방법으로 복사하고, 확보 방법은 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)에서 다룹니다.

## 한 레코드가 한 동작은 아니다

fseventsd는 짧은 시간 안에 한 디렉터리에서 여러 번 일어난 알림을 하나로 합칩니다 [3][4]. 그래서 한 레코드에 Created·Modified·Removed 같은 플래그가 함께 켜져 있어도 동작이 세 번 있었다고 세지 않고, 반대로 여러 번 저장한 파일이 레코드 하나로만 남을 수도 있습니다. 합쳐진 이벤트를 알리는 API 플래그는 [이벤트 플래그 읽기 (Flags)](flags.md)에 있습니다.

## 빠진 이벤트와 지운 기록

커널과 데몬 사이에 통신 오류가 나면 이벤트가 빠질 수 있습니다 [4]. 레코드가 없다는 사실만으로 그 경로에 아무 변경이 없었다고 말하지 않습니다.

과거 기록을 일부러 지우는 방법도 있습니다. `FSEventsPurgeEventsForDeviceUpToEventId` 는 root만 부를 수 있고, 지정한 이벤트 ID 이전의 과거 기록을 지웁니다 [4]. Apple API는 볼륨마다 이벤트 기록의 고유 ID(UUID)를 두고 `FSEventsCopyUUIDForDevice` 로 알려 줍니다. 이 UUID가 바뀌었거나, UUID는 같은데 이벤트 ID가 이전보다 낮아졌다면 백업 복원이나 ID 되돌림, 기록 지우기(purge)가 있었을 수 있습니다 [4]. 탐지할 때는 이전에 확보한 기록이나 백업과 이 두 값을 비교하고, 흔적을 지우려 한 정황을 모으는 흐름은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 이벤트 ID가 겹칠 때

호스트 단위 스트림의 이벤트 ID는 그 호스트의 다른 이벤트보다 커지는 방향으로 매겨지고, 디스크 단위 스트림의 ID는 그 디스크의 이전 이벤트보다 커질 뿐 다른 디스크와는 관계가 없습니다 [4]. 다른 컴퓨터(Mac OS X 10.5 이상)에서 쓰던 디스크를 붙이면 과거 ID가 겹칠 수 있고, 새 이벤트는 붙은 드라이브 가운데 가장 큰 과거 ID 다음부터 시작합니다 [4]. 서로 다른 볼륨의 이벤트 ID를 한데 섞어 순서를 매기지 않고, 볼륨마다 따로 읽습니다.

외장 저장 장치에서 나온 기록은 그 장치를 꽂았던 Mac이 남긴 것입니다 [6]. 장치에 남은 기록이 조사 대상 Mac에서 생겼는지는 [USB 저장 장치 (USB Storage)](../../external-devices/usb/index.md)의 연결 기록과 맞춰 봐야 합니다.

## 카빙한 기록을 읽을 때

비할당 영역에서 카빙한 GZIP은 끝이 잘려 있을 수 있어서, FSEventsParser는 GZIP 끝 검사를 끄고 읽습니다 [2]. 카빙한 GZIP과 할당된 이벤트 파일을 함께 넣으면 같은 레코드가 두 번 나오는데, FSEventsParser는 중복을 지우지 않습니다 [6]. 결과를 셀 때는 이벤트 ID와 경로로 중복을 먼저 걸러 냅니다.

잘못 읽은 레코드를 걸러 내는 단서도 있습니다. ItemCloned 플래그는 High Sierra부터 쓰여서, FSEventsParser는 버전 1(`1SLD`) 파일에서 ItemCloned가 나오면 잘못 읽은 레코드로 봅니다 [2].

## 플래그 16진수를 도구끼리 섞지 않는다

libyal 문서는 플래그를 little-endian 값으로, FSEventsParser는 빅엔디언 값으로 적어서 같은 플래그가 다른 16진수로 보입니다 [1][2]. 두 도구의 결과를 비교할 때는 [이벤트 플래그 읽기 (Flags)](flags.md)의 대조표로 이름을 맞춘 뒤에 비교합니다.

## 경로가 잘렸을 수 있다

디스크 값 0x00020000 비트의 이름은 FSE_TRUNCATED_PATH입니다 [1][7]. 이 비트가 켜진 레코드는 경로가 잘렸을 수 있다고 보고, 기록된 경로를 온전한 전체 경로로 단정하지 않습니다. FSEventsParser는 이 비트에 이름을 붙이지 않고 `NOT_USED-0x00000200` 으로 보여 줍니다 [2].

## 도구가 읽는 버전

plaso `fseventsd` 파서의 코드 설명은 `1SLD` 와 `2SLD` 만 적고 있습니다 [5]. macOS 14 Sonoma 이후의 `3SLD` 기록을 다룰 때는 쓰는 도구가 이 버전을 읽는지, 읽지 못한 파일을 조용히 건너뛰지 않는지 먼저 확인하고, 확인 방법은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 보고서 문장 예

기록으로 확인되는 만큼만 씁니다.

> 데이터 볼륨의 `.fseventsd` 이벤트 파일에 경로 `Users/(사용자)/Documents/(파일 이름).docx` 와 Created·IsFile 플래그가 함께 기록된 레코드가 있다(이벤트 ID ○○). FSEvents 레코드에는 시각이 없고, 이 날짜는 같은 기록의 로그 파일 이름으로 어림한 범위이며 하루 정도 어긋날 수 있다.

"사용자가 ○○일 ○○시에 파일을 만들었다" 처럼 시각과 행위자를 단정하는 문장은 FSEvents만으로 쓰지 않습니다.

## 교차 검증

FSEvents는 경로와 변경 종류를, 다른 기록은 시각과 행위자를 채워 줍니다. 날짜 추정에 쓰인 로그는 [예전 시스템 로그 (ASL·syslog)](../../../01-foundations/data-formats/asl-syslog.md), [감사 로그 (OpenBSM Audit)](../../logs/openbsm-audit.md), [전원·잠자기 기록 (pmset)](../../logs/power-events.md)에서, 하루 오차를 따질 때 필요한 시간대 설정은 [시간대와 시계 설정 (Time Zone·NTP)](../../system-account/time-zone.md)에서 확인합니다. 여러 기록을 한 시간축에 놓는 방법은 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)에, 지운 파일을 쫓는 흐름은 [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md)에 있습니다.

## 참고 문헌

1. libyal dtformats — MacOS File System Events Disk Log Stream format — https://github.com/libyal/dtformats/blob/main/documentation/MacOS%20File%20System%20Events%20Disk%20Log%20Stream%20format.asciidoc
2. FSEventsParser 4.1 소스 (Nicole Ibrahim) — https://raw.githubusercontent.com/dlcowen/FSEventsParser/master/FSEParser_V4.1.py
3. Apple, File System Events Programming Guide — Technology Overview (2012-12-13) — https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/FSEvents_ProgGuide/TechnologyOverview/TechnologyOverview.html
4. Apple, File System Events Programming Guide — Using the File System Events API — https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/FSEvents_ProgGuide/UsingtheFSEventsFramework/UsingtheFSEventsFramework.html
5. plaso fseventsd 파서 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/fseventsd.py
6. FSEventsParser README — https://raw.githubusercontent.com/dlcowen/FSEventsParser/master/README.md
7. Apple xnu bsd/sys/fsevents.h — https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/sys/fsevents.h
