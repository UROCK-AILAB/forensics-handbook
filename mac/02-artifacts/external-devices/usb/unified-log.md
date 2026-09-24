---
title: "통합 로그의 연결 기록"
parent: "USB 저장 장치"
grand_parent: "아티팩트 · 외부 장치"
nav_order: 1050
---

# 통합 로그의 연결 기록 (Unified Log)

USB 저장 장치를 꽂고 뺄 때 디스크 중재 데몬(diskarbitrationd)이 통합 로그에 남기는 디스크 등장·사라짐·이름 바뀜 메시지를 찾아, 장치가 이 맥에 나타난 시각과 사라진 시각을 잡는 방법을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

diskarbitrationd는 macOS에서 디스크가 나타나고 사라지거나 파일 시스템이 마운트·언마운트될 때 알림을 받아 처리하는 데몬이고, 시작할 때 "media appeared", "media disappeared", "file system mounted" 같은 알림을 등록합니다 [3]. 이 데몬은 `os_log_create(_kDADaemonName, "default")` 로 로그 객체를 만들어서 통합 로그에 메시지를 쓰고, 그래서 이 데몬 메시지의 범주(category)는 `default` 입니다 [1].

USB 저장 장치를 꽂으면 macOS가 새 디스크를 인식하고, 이때 데몬이 디스크가 나타났다는 메시지를 남깁니다. 장치를 빼거나 꺼내면 디스크가 사라졌다는 메시지가 남습니다 [2]. 통합 로그의 저장 형식과 읽는 원리는 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있고, 이 페이지는 그중 외장 디스크 연결과 관련된 메시지만 다룹니다.

## 위치와 버전별 차이

통합 로그는 macOS 10.12 Sierra에서 처음 들어왔습니다 [4]. 로그 본문은 `/private/var/db/diagnostics/` 아래 `Persist`, `Special`, `Signpost`, `HighVolume`, `timesync` 폴더의 tracev3 파일에 있고, 메시지 문자열을 풀 때 쓰는 파일은 `/private/var/db/uuidtext/` 아래 16진수 두 글자 폴더(`00`~`FF`)와 `dsc` 폴더에 있습니다 [4]. 이 파일들을 다른 곳으로 옮겨 분석할 때는 `.logarchive` 디렉터리로 묶습니다 [4][5].

아래 메시지 문구는 apple-oss-distributions에 공개된 DiskArbitration 소스의 main 브랜치에서 가져온 것이라, 어느 macOS 버전의 문구인지는 정해져 있지 않습니다. 버전에 따라 문구가 다를 수 있어서, 검체에서는 문구 전체보다 앞부분의 짧은 단어로 먼저 찾아보고 실제 문구를 확인한 뒤 거르는 조건을 좁힙니다.

## 구조

### 로그 수준

데몬 소스는 로그 함수마다 통합 로그에 쓰는 호출을 정해 두었고, 함수 이름과 실제 수준이 서로 맞지 않는 것이 있습니다 [1]. `DALogInfo` 는 info 수준이 아니라 `os_log` 로 기본(Default) 수준에 쓰고, info 수준으로 쓰는 쪽은 `DALogDebug` 입니다.

| 소스 함수 | 소스 안의 호출 | 통합 로그 수준 |
|---|---|---|
| `DALog` | `os_log` | 기본(Default) |
| `DALogInfo` | `os_log` | 기본(Default) |
| `DALogDebug` | `os_log_info` | info |
| `DALogError` | `os_log_info` 와 `os_log_error` | info 한 번, error 한 번 |
| `DALogFault` | `os_log_fault` | fault |

데몬을 `-d` 옵션으로 디버그 모드로 켜면 `/var/log/<데몬 이름>.log` 파일을 직접 열어 `DALogInfo`·`DALogDebug` 메시지를 이 파일에도 씁니다 [1][3]. 평상시 검체에 이 파일이 있는지는 확인한 자료가 없어서, 파일이 있으면 디버그 모드로 돌린 적이 있는지부터 따져 봅니다.

### 연결과 관련된 메시지

아래 표는 소스에 적힌 형식 문자열이고, 모두 `DALogInfo` 로 쓰는 메시지라 수준은 기본(Default)입니다. `%@`, `%s`, `%016llX` 자리에 실제 값이 들어가고, 문구 앞뒤에 붙은 공백은 표에서 뺐습니다 [2][3].

| 상황 | 형식 문자열 | 수준 | 소스 위치 |
|---|---|---|---|
| 디스크가 나타남 | `created disk, id = %@.` | 기본 | `_DAMediaAppearedCallback` [2] |
| 디스크가 사라짐 | `removed disk, id = %@.` | 기본 | `_DAMediaDisappearedCallback` [2] |
| 볼륨 이름이 바뀜 | `mounted volume name changed for %@ to name %@.` | 기본 | DAServer.c [2] |
| 볼륨 이름이 바뀜 | `IOReg volume name changed for %@ to name %@.` | 기본 | DAServer.c [2] |
| 사용자 로그인으로 미뤄 둔 디스크를 마운트 | `console user change: mounting deferred disk %@` | 기본 | DAServer.c [2] |
| 로그인한 사용자가 없어 언마운트 | `console user is not logged in. unmounting disk %@` | 기본 | DAServer.c [2] |
| 사용자 로그아웃으로 언마운트 | `console user logout: unmounting  disk %@` | 기본 | DAServer.c [2] |
| 앱이 디스크 작업을 요청 | `%@ queued solicitation, id = %016llX:%016llX, kind = %s, disk = %@, options = 0x%08X.` | 기본 | DAServer.c [2] |
| 데몬 시작 | `server has been started.` | 기본 | DAMain.c [3] |
| 데몬 시작 때 콘솔 사용자 | `console user = %@ [%d].` | 기본 | DAMain.c [3] |

`queued solicitation` 메시지에는 요청 종류(`kind`)와 대상 디스크가 함께 적혀서, 어느 프로세스 쪽에서 마운트·언마운트·꺼내기를 요청했는지 짚는 단서가 될 수 있습니다. 이 해석은 형식 문자열을 보고 필자가 정리한 것이라, 실제 검체에서 앞의 `%@` 자리에 무엇이 찍히는지 확인하고 씁니다.

실제로 마운트가 끝났다는 메시지는 DAServer.c에서 찾지 못해서 이 표에 넣지 않았습니다. 마운트 쪽 흔적은 [마운트 기록 (DiskArbitration)](mount-records.md)에서 이어 봅니다.

### 서브시스템 이름

로그 객체의 서브시스템(subsystem) 자리에는 `_kDADaemonName` 이라는 상수가 들어가지만, 이 상수의 실제 문자열은 소스에서 끝까지 따라가 확인하지 못했습니다 [1]. 그래서 아래 예시는 서브시스템 대신 프로세스(process) 칸으로 거릅니다.

## 증거로서 의미

**증명하는 것.** `created disk` 메시지가 있으면 그 시각에 macOS가 새 디스크를 인식했다는 뜻이고, 짝이 되는 `removed disk` 메시지와 함께 보면 디스크가 이 맥에 붙어 있던 구간을 어림할 수 있습니다. 볼륨 이름이 바뀐 메시지에는 새 볼륨 이름이 적혀서, 로그만으로도 장치를 볼륨 이름으로 가리킬 수 있습니다. 콘솔 사용자 관련 메시지는 디스크가 로그인·로그아웃과 맞물려 마운트되거나 언마운트된 경우를 보여 줍니다.

**증명하지 못하는 것.** 형식 문자열에는 USB라는 말이 없어서, 메시지만으로는 이 디스크가 USB 저장 장치인지 디스크 이미지나 다른 외장 장치인지 가릴 수 없습니다. 장치의 제조사·제품 번호·시리얼 번호도 이 메시지들에는 없습니다. 어떤 파일을 읽거나 복사했는지, 누가 장치를 꽂았는지도 이 기록이 말해 주지 않고, 파일 쪽 흔적은 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)와 같은 다른 기록에서 찾습니다.

## 시각 해석

통합 로그 레코드의 시각은 부팅 뒤 흐른 틱(mach continuous time)으로 적혀 있고, timebase(분자/분모)를 곱해 나노초로 바꿉니다 [4]. 벽시계 시각은 timesync 레코드에 적힌 벽시계 시각에 기준 틱과의 차이를 더해 구하고, timesync 파일이 없으면 tracev3 헤더의 벽시계 시각을 기준으로 씁니다 [4]. timesync의 벽시계 시각은 1970-01-01 00:00:00 UTC부터 흐른 나노초라서 결과는 UTC이고, 부팅 UUID가 tracev3 파일과 timesync 기록을 이어 줍니다 [4]. 계산 방법은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)과 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

`log show` 는 시간대를 따로 정하지 않으면 레코드가 쓰였을 때의 시간대로 시각을 보여 주므로, `--timezone` 으로 시간대를 정해 두고 뽑습니다 [5]. 보고서에 옮길 때는 UTC로 적었는지 현지 시각으로 적었는지 함께 밝힙니다.

## 함정과 한계

`DALogInfo` 라는 함수 이름만 보고 연결 메시지를 info 수준으로 여기기 쉽지만, 소스를 따라가면 기본 수준으로 쓰여서 `log show` 에 `--info` 를 붙이지 않아도 보입니다 [1][5]. 반대로 `DALogDebug` 로 쓰는 자세한 메시지는 info 수준이라 `--info` 를 붙여야 나옵니다 [1][5]. 이 수준 대응은 main 브랜치 소스에서 확인한 것이라 옛 버전 검체에서는 다를 수 있고, 메시지가 디스크에 얼마나 오래 남는지도 확인한 자료가 없어서, 메시지가 없다는 사실만으로 장치를 꽂지 않았다고 쓰지 않습니다.

로그아웃 메시지의 `unmounting  disk` 에는 소스 문구 그대로 공백이 두 칸 들어 있어서 [2], 한 칸 띄운 문구로 찾으면 걸리지 않습니다. 버전마다 문구가 달라질 수도 있어서 `eventMessage CONTAINS "disk"` 처럼 넓게 찾은 뒤 좁혀 가는 편이 안전합니다.

장치의 제조사·시리얼 번호를 적는 커널 쪽 USB 메시지는 이 핸드북이 출처로 확인한 문구만 싣는다는 원칙에 따라 이 페이지에서 다루지 않습니다.

`log` 명령에는 로그를 지우는 `log erase` 하위 명령이 있습니다 [5]. 지운 흔적이 로그에 남는지는 확인한 자료가 없어서, 기록이 비어 있는 구간이 나오면 저장 한도 때문에 밀려난 것인지 지워진 것인지 다른 기록과 맞춰 가립니다. 이 흐름은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 직접 분석해 보기

tracev3 파일을 헥스로 따라가는 방법은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있고, 여기서는 macOS에 들어 있는 `log` 명령으로 연결 메시지를 뽑는 방법만 봅니다.

살아 있는 맥에서는 `log collect` 로 로그를 `.logarchive` 로 모으고, 분석하는 맥에서 `log show --archive` 로 그 아카이브를 엽니다 [5]. 수집 절차는 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md)에서 다룹니다.

```sh
# 수집한 아카이브에서 디스크 등장·사라짐 메시지만 UTC로 뽑는 예
log show --archive evidence.logarchive --info --timezone UTC --style ndjson \
  --predicate 'process == "diskarbitrationd" AND (eventMessage CONTAINS "created disk" OR eventMessage CONTAINS "removed disk")'
```

시간 범위는 `--start`, `--end` 에 "YYYY-MM-DD" 나 "YYYY-MM-DD HH:MM:SS" 형식으로 주거나 `--last` 로 최근 구간만 볼 수 있습니다 [5]. 거르는 조건(predicate)에는 `subsystem`, `category`, `process`, `eventMessage`, `sender`, `processImagePath`, `senderImagePath`, `eventType`, `messageType` 칸을 쓸 수 있고 [5], 결과 형식은 `--style` 로 default, compact, json, ndjson, syslog 중에서 고릅니다 [5]. 타임라인 도구에 넣을 때는 한 줄에 레코드 하나가 들어가는 ndjson이 다루기 편합니다.

뽑은 결과에서는 `created disk` 와 `removed disk` 를 같은 디스크끼리 짝지은 뒤, 그 사이에 나온 볼륨 이름 변경·`queued solicitation` 메시지를 시간순으로 붙여 봅니다.

## 교차 검증

로그에서 잡은 시각은 [마운트 기록 (DiskArbitration)](mount-records.md)의 디스크 설명 값·볼륨 기록과 맞춰 보고, 어떤 볼륨이었는지는 [볼륨 UUID로 장치 잇기 (Volume UUID)](volume-uuid.md)의 순서로 좁힙니다. 장치 안에서 무엇이 바뀌었는지는 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)와 [스포트라이트 (Spotlight)](../../file-folder-usage/spotlight/index.md)에서 찾습니다. 통합 로그에서 찾을 다른 사건은 [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md)에 모여 있고, 여러 기록을 한 시간축에 놓는 방법은 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)에 있습니다.

## 실습

USB 저장 장치를 꽂았다 뺀 테스트 맥이나 통합 로그가 들어 있는 공개 검체(NIST CFReDS 등)에서 아래 질문을 풀어 봅니다.

1. `--info` 없이 찾을 때와 붙여서 찾을 때 diskarbitrationd 메시지 수가 어떻게 다르고, `created disk` 메시지는 어느 쪽에서든 보이는가?
2. 같은 디스크의 `created disk` 와 `removed disk` 를 짝지으면 장치가 붙어 있던 구간은 얼마인가?
3. 그 구간에 볼륨 이름 변경 메시지가 있다면 어떤 이름이 찍혔고, 그 이름이 볼륨 쪽 기록과 맞는가?
4. `--timezone UTC` 로 뽑은 시각과 현지 시간대로 뽑은 시각을 보고서에 어떻게 구분해 적을 것인가?

## 참고 문헌

1. Apple Open Source, DiskArbitration — diskarbitrationd/DALog.c (main 브랜치) — https://raw.githubusercontent.com/apple-oss-distributions/DiskArbitration/main/diskarbitrationd/DALog.c
2. Apple Open Source, DiskArbitration — diskarbitrationd/DAServer.c (main 브랜치) — https://raw.githubusercontent.com/apple-oss-distributions/DiskArbitration/main/diskarbitrationd/DAServer.c
3. Apple Open Source, DiskArbitration — diskarbitrationd/DAMain.c (main 브랜치) — https://raw.githubusercontent.com/apple-oss-distributions/DiskArbitration/main/diskarbitrationd/DAMain.c
4. libyal dtformats — Apple Unified Logging and Activity Tracing formats — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
5. log(1) man page (Xcode man page 모음) — https://keith.github.io/xcode-man-pages/log.1.html
