---
title: "journalctl 로 읽기"
parent: "systemd 저널"
grand_parent: "기반 · 로그 체계"
nav_order: 210
---

# journalctl 로 읽기 (journalctl)

`journalctl` 은 저널 파일을 읽는 systemd 의 기본 도구이고, 검체에서 떼어 낸 폴더나 디스크 이미지도 옵션 몇 개로 열 수 있습니다[1].

저널 파일이 어디에 생기고 어떤 설정으로 남는지는 [systemd 저널](index.md) 에서, 파일 안의 바이트 구조는 [저널 파일 구조](file-format.md) 에서 다룹니다. 이 쪽은 검체를 `journalctl` 로 읽을 때 쓰는 옵션과, 출력을 해석할 때 조심할 점만 다룹니다.

## 검체를 여는 법

옵션 없이 실행하면 `journalctl` 은 분석 PC 자신의 저널(`/run/log/journal`·`/var/log/journal`)을 읽습니다[1]. 검체를 읽으려면 아래 옵션으로 읽을 곳을 바꿉니다.

| 옵션 | 읽는 곳 | 비고 |
|---|---|---|
| `-D DIR`, `--directory=DIR` | 지정한 저널 폴더 | systemd 187 부터[1] |
| `-i GLOB`, `--file=GLOB` | glob 에 맞는 파일 | 여러 번 줄 수 있고, 준 파일을 모두 끼워 맞춰 한 흐름으로 냄[1] |
| `--root=ROOT` | ROOT 아래의 저널 폴더와 메시지 카탈로그 | 마운트한 검체 루트에 씀[1] |
| `--image=IMAGE` | 디스크 이미지 파일이나 블록 장치 안의 파일 시스템 | 파일 시스템 하나만 든 이미지이거나, GPT 로 나눈 이미지면 Discoverable Partitions 규격을 따라야 함. systemd 247 부터[1] |
| `--namespace=NAMESPACE` | 저널 네임스페이스 | 주지 않으면 기본 네임스페이스만 보이고, `*` 를 주면 모든 네임스페이스를 끼워 맞춤. systemd 245 부터[1] |

아래는 마운트한 검체의 저널 폴더 하나를 읽는 만든 예시입니다. 경로의 `MACHINE_ID` 는 검체의 기계 ID 폴더 이름으로 바꿉니다.

```text
journalctl --no-pager -D /mnt/evidence/var/log/journal/MACHINE_ID -o export > journal.export
journalctl --no-pager --file='/mnt/evidence/var/log/journal/MACHINE_ID/system@*.journal' --utc
```

`journalctl` 은 이름이 `.journal` 이나 `.journal~` 로 끝나는 파일만 저널로 봅니다[4]. 복사하면서 이름을 바꾼 파일은 `--file=` 로 직접 주거나 원래 확장자로 되돌려야 읽힙니다. 출력은 회전한 파일과 활성 파일, 시스템 파일과 사용자 파일을 모두 끼워 맞춘 하나의 흐름이고, 어떤 파일을 읽었는지는 `--header` 로 확인합니다[1].

분석 PC 의 `journalctl` 판이 곧 쓸 수 있는 옵션을 정합니다. `-T/--exclude-identifier` 는 systemd 256 부터, `-I/--invocation` 과 `--list-invocations` 는 257 부터 있는 옵션이라서[1], systemd 252 를 싣는 RHEL 9[5] 의 `journalctl` 에는 없습니다.

## 거르기

명령 끝에 `필드이름=값` 을 붙이면 그 값이 든 항목만 나옵니다[1]. 서로 다른 필드를 여럿 주면 모두 맞는 항목(AND)만, 같은 필드를 여럿 주면 어느 하나라도 맞는 항목(OR)이 나오고, 낱말 `+` 는 앞뒤 조건을 OR 로 묶습니다[1].

| 옵션 | 걸리는 조건 | 검체에서 쓸 때 |
|---|---|---|
| `-b ID`, `--boot=ID` | `_BOOT_ID=` | 양수는 저널 처음부터 센 부팅 순번(1 이 처음), 0 이하는 끝에서 센 순번(-0 이 마지막, -1 이 그 앞)입니다[1]. 32자리 부팅 ID 를 직접 줄 수 있고, `all` 은 앞서 준 `-b` 를 없앱니다[1] |
| `-u UNIT`, `--unit=UNIT` | `_SYSTEMD_UNIT=` 에 더해 PID 1 이 그 유닛에 대해 남긴 메시지, 코어 덤프 메시지, `_SYSTEMD_SLICE=` | 유닛이 남긴 기록과 유닛에 대한 기록을 함께 봅니다[1] |
| `--user-unit=UNIT` | `_SYSTEMD_USER_UNIT=` 과 `_UID=` 등 | 사용자 세션의 유닛[1] |
| `-t ID`, `--identifier=ID` | `SYSLOG_IDENTIFIER=` | 보낸 쪽이 적은 값이라 검증되지 않은 값입니다[2] |
| `-p`, `--priority=` | `PRIORITY=` | 값 하나를 주면 그 등급과 그보다 중요한 등급(0 emerg 에서 7 debug 까지 중 숫자가 더 작은 쪽)을 모두, `FROM..TO` 를 주면 그 범위를 냅니다[1] |
| `--facility=` | syslog facility | 쉼표로 여럿 줄 수 있습니다[1] |
| `-g`, `--grep=` | `MESSAGE=` 에 PCRE2 정규식 | 패턴이 모두 소문자면 대소문자를 가리지 않습니다[1]. `MESSAGE` 말고 다른 필드는 찾지 않습니다 |
| `-k`, `--dmesg` | `_TRANSPORT=kernel` | 따로 주지 않으면 `--boot=0` 이 함께 걸립니다[1] |
| `-S`, `--since=` / `-U`, `--until=` | 그 시각 이후 / 이전 | `2026-01-15 09:00:00` 꼴. `yesterday`·`today`·`now` 와 `-`·`+` 상대 시각도 받습니다[1] |

`-u` 는 실제로 아래 조건을 OR 로 묶은 것과 비슷하게 풀립니다[1].

```text
_SYSTEMD_UNIT=name.service
+ UNIT=name.service _PID=1
+ OBJECT_SYSTEMD_UNIT=name.service _UID=0
+ COREDUMP_UNIT=name.service _UID=0 MESSAGE_ID=fc2e22bc6ee647b6b90729ab34a250b1
```

오프라인 검체에서는 분석 PC 의 상태를 기준으로 삼는 조건을 피합니다. 절대 경로를 인자로 주면 실행 파일이면 `_EXE=`, 스크립트면 `_COMM=`, 장치 노드면 `_KERNEL_DEVICE=` 조건이 붙는데, 이 경로는 질의하는 순간 분석 PC 에 있어야 하고 장치 노드는 현재 부팅으로 범위가 좁혀집니다[1]. 검체의 실행 파일로 거를 때는 `_EXE=/usr/sbin/sshd` 처럼 필드 조건을 직접 씁니다. 부팅 순번은 저널 끝이나 처음에서 센 값이고, 빈 `-b` 는 다른 기계의 저널을 볼 때 `-0` 과 다르게 동작할 수 있습니다[1]. 검체에서는 `--list-boots` 로 부팅 ID 를 먼저 뽑고 그 ID 로 고릅니다. `-k` 는 현재 부팅이 함께 걸리므로 검체의 커널 메시지 전체를 보려면 `-k -b all` 이나 `_TRANSPORT=kernel` 조건을 씁니다.

## 출력 형식과 시각

| `-o` 값 | 시각 표시 | 쓰임 |
|---|---|---|
| `short` | 전통 syslog 꼴, 연도·시간대 없음 | 기본값[1] |
| `short-full` | 요일·연도·시간대 포함, 로캘과 무관 | `--since`·`--until` 이 받는 꼴과 같음[1] |
| `short-iso` / `short-iso-precise` | RFC 3339 꼴 / 여기에 마이크로초까지 | [1] |
| `short-precise` | syslog 꼴에 마이크로초 | [1] |
| `short-unix` | 1970-01-01 UTC 부터 센 초, 마이크로초 정밀도 | [1] |
| `short-monotonic` / `short-delta` | 단조 시각 / 여기에 앞 항목과의 차이 | `short-delta` 는 systemd 252 부터[1] |
| `verbose` | 모든 필드 | [1] |
| `export` | `__REALTIME_TIMESTAMP` 등 마이크로초 정수 | 보관·전송용 스트림, 필드를 빠짐없이 남김[1][3] |
| `json`, `json-pretty`, `json-seq`, `json-sse` | 마이크로초 값을 숫자 문자열로 | 한 항목이 JSON 객체 하나[1][3] |
| `cat` | 없음 | 메시지만[1] |
| `with-unit` | `short-full` 과 같음 | 식별자 대신 유닛 이름을 앞에 붙임[1] |

`--utc` 를 주면 사람이 읽는 시각을 UTC 로 냅니다[1]. 주지 않으면 `short` 계열은 분석 PC 의 현지 시각으로 찍히고, `short` 는 연도와 시간대도 빠지므로[1] 보고서에 옮길 시각은 `--utc` 와 `short-iso-precise` 나 `short-full` 을 함께 써서 뽑습니다. 연도 없는 syslog 시각의 문제는 [syslog 형식과 rsyslog](../syslog-rsyslog.md) 에서 다룹니다.

`export` 와 `json` 은 시각을 마이크로초 값 그대로 남겨 두므로 가공 없이 타임라인에 옮기기 좋습니다. 아래는 `-o export` 출력 꼴을 보여 주려고 만든 예시이고, 값은 모두 지어낸 것입니다.

```text
__REALTIME_TIMESTAMP=1768435200000000
__MONOTONIC_TIMESTAMP=3600123456
_BOOT_ID=33333333333333333333333333333333
_TRANSPORT=syslog
PRIORITY=6
SYSLOG_IDENTIFIER=sshd
MESSAGE=만든 예시 메시지
_PID=4321
_UID=1000
_COMM=python3
_EXE=/usr/bin/python3.12
_SOURCE_REALTIME_TIMESTAMP=1768435199998000
_HOSTNAME=host01
```

한 항목에는 뜻이 다른 시각이 여럿 있습니다. `__REALTIME_TIMESTAMP` 는 journald 가 항목을 받은 순간의 벽시계 시각이고 UTC 기준 마이크로초입니다[2]. 위 예시의 1768435200000000 은 2026-01-15 00:00:00 UTC 입니다. `_SOURCE_REALTIME_TIMESTAMP` 는 받은 시각과 다를 때만 붙는, 알 수 있는 가장 이른 신뢰 시각입니다[2]. `__MONOTONIC_TIMESTAMP` 는 부팅 뒤 흐른 시간이라서 `_BOOT_ID` 와 짝지어야 뜻이 생깁니다[2]. `SYSLOG_TIMESTAMP` 는 syslog 데이터그램에 원래 적힌 시각을 그대로 옮긴 값이고 journald 가 검증하지 않습니다[2]. systemd 257 부터는 부팅 기준 시각인 `_SOURCE_BOOTTIME_TIMESTAMP` 도 붙습니다[2]. 마이크로초 값을 날짜로 바꾸는 방법은 [Linux 의 시각 값](../../value-decoding/time-values.md) 에서 다룹니다.

`--since`·`--until` 에 준 `yesterday`·`today`·`now` 와 `-`·`+` 상대 시각은 명령을 실행하는 날짜와 시각을 기준으로 풀립니다[1]. 검체에서는 절대 시각을 주고, 경계 근처 항목은 `-o short-unix` 나 `__REALTIME_TIMESTAMP` 값으로 한 번 더 확인합니다.

## 저널 전체를 훑는 명령

항목을 하나씩 읽기 전에 아래 명령으로 저널의 윤곽을 먼저 잡습니다. 모두 `-D`·`--file=`·`--root=` 와 함께 쓸 수 있습니다.

| 명령 | 알려 주는 것 |
|---|---|
| `-N`, `--fields` | 저널에 쓰인 모든 필드 이름[1] |
| `-F FIELD`, `--field=FIELD` | 한 필드에 들어 있는 값 전부(예: `-F _SYSTEMD_UNIT`, `-F _UID`)[1] |
| `--list-boots` | 부팅 순번·부팅 ID·그 부팅의 첫 메시지와 마지막 메시지 시각[1] |
| `--header` | 파일마다 머리 정보. 시계가 틀린 채 부팅해 순서가 어긋난 항목을 찾을 때 쓸모가 있습니다[1] |
| `--verify` | 파일 내부 일관성. 봉인 (Forward Secure Sealing) 한 파일이고 `--verify-key=` 로 검증 키를 주면 진위도 확인합니다[1] |
| `--disk-usage` | 보관 파일과 활성 파일을 더한 디스크 사용량[1] |

`--list-boots` 의 첫·마지막 메시지 시각은 그 부팅의 저널 기록 범위를 알려 주고, 이 범위 사이의 빈 곳은 [부팅과 종료 기록](../../../02-artifacts/system-info/boot-shutdown.md) 과 맞춰 봅니다. `--header` 가 내는 필드의 뜻은 [저널 파일 구조](file-format.md) 의 파일 머리 표와 같습니다.

## 포렌식에서 중요한 점

이름이 밑줄(`_`)로 시작하는 필드는 journald 가 스스로 붙이는 신뢰 필드라서 보낸 프로그램이 바꿀 수 없습니다[2]. 그래서 `_PID`·`_UID`·`_EXE`·`_COMM` 은 어느 프로세스가 기록을 보냈는지를 보여 줍니다. 밑줄이 없는 필드(`MESSAGE`·`SYSLOG_IDENTIFIER`·`PRIORITY` 등)는 journald 가 검증하지 않습니다[2]. 위 만든 예시처럼 `SYSLOG_IDENTIFIER=sshd` 인데 `_EXE` 가 다른 프로그램이면, 이 항목은 sshd 가 남긴 기록이 아니라 그 프로그램이 sshd 라는 이름을 달고 보낸 기록입니다. `-t` 와 `short` 출력은 밑줄 없는 식별자를 보여 주므로, 보낸 쪽이 중요한 항목은 `-o verbose` 나 `-o export` 로 신뢰 필드까지 확인합니다.

보고서에는 "`_UID=1000` 인 프로세스 `_EXE=…` 가 이 시각에 이 메시지를 journald 에 보낸 기록이 있다" 처럼 필드가 말하는 만큼만 씁니다. `MESSAGE` 의 내용이 사실인지는 이 기록만으로 말할 수 없습니다.

`journalctl` 에는 저널을 읽는 명령 말고 journald 에 일을 시키는 명령도 있습니다. `--rotate` 는 활성 파일을 모두 보관 상태로 바꾸고 이름을 바꾸며, `--vacuum-size`·`--vacuum-time`·`--vacuum-files` 는 오래된 보관 파일을 지우고, `--flush` 와 `--relinquish-var` 는 journald 가 쓰는 폴더를 `/run/log/journal` 과 `/var/log/journal` 사이에서 옮깁니다[1]. `--sync` 는 아직 디스크에 쓰지 않은 데이터를 쓰게 합니다[1]. 살아 있는 검체에서 라이브 응답을 할 때 이 명령들은 증거를 바꾸므로 목적이 분명할 때만 쓰고, 쓴 사실과 시각을 기록합니다. 반대로 검체의 셸 기록에 이 명령이 있으면 사람이 저널을 회전하거나 지운 흔적일 수 있으므로 [손상·삭제된 저널](corruption.md) 과 함께 봅니다.

## 함정

- 같은 필드가 한 항목에 여러 번 나올 수 있습니다[3]. `json` 출력은 이런 필드를 배열로 내지만[1], plaso 와 dissect.target 은 필드를 사전에 차례로 넣어 마지막 값만 남깁니다[6][7].
- `json` 출력은 4096바이트보다 큰 필드를 `null` 로 내고, 기본 출력은 출력할 수 없는 문자가 든 필드를 "blob data" 로 줄입니다[1]. 긴 필드나 이진 필드를 빠짐없이 보려면 `--all` 을 줍니다[1].
- `--show-cursor` 가 내는 커서는 형식이 공개되지 않았고 바뀔 수 있습니다[1]. 커서 문자열을 풀어서 해석하지 말고, 이어 읽기용 표시로만 씁니다.
- dissect.target 은 필드 이름 앞의 밑줄을 떼고 소문자로 바꿉니다[7]. 결과에서 `_PID` 와 `PID` 처럼 신뢰 필드와 보낸 쪽이 적은 필드가 구분되지 않을 수 있습니다. 또 우선순위를 `if priority` 로 거르기 때문에 `PRIORITY=0`(emerg) 이 빈 값으로 나옵니다[7].
- 분석 PC 의 systemd 가 검체보다 오래되면 새 기능 플래그 때문에 파일을 열지 못할 수 있습니다. 이 경우는 [저널 파일 구조](file-format.md) 의 함정에서 다룹니다.
- `--user` 는 영구 저장일 때만 동작합니다[1]. 사용자별 파일이 없는 검체에서는 사용자 기록도 시스템 파일 안에 있을 수 있으므로 `_UID=` 조건으로 찾습니다.

## 도구

| 도구 | 하는 일 | 참고 |
|---|---|---|
| `journalctl` | 위에서 다룬 모든 읽기·거르기·내보내기[1] | 분석 PC 의 판에 따라 옵션이 다름 |
| plaso `systemd_journal` 파서 | 항목을 이벤트로 바꿈. `__REALTIME_TIMESTAMP` 는 written_time, `_SOURCE_REALTIME_TIMESTAMP` 는 recorded_time 으로 나눔[6] | systemd-journal-remote 로 모은 저널이면 앞의 값은 수집 서버가 받은 시각이라 두 값이 벌어짐[6] |
| dissect.target journal 플러그인 | 항목을 레코드로 바꿈[7] | 필드 이름을 바꾸는 점은 위 함정 참고 |
| Velociraptor `Linux.Forensics.Journal.Fields` | `journalctl -N`·`-F` 와 같은 일을 색인에서 바로 하고, 값마다 항목 수와 첫·마지막 시각을 냄[8] | 압축형 (compact) 형식(systemd 252 이후)만 읽고, 읽을 수 없거나 비었거나 손상된 파일과 옛 형식 파일은 건너뜀[8] |
| UAC | 라이브 응답에서 `journalctl --list-boots` 결과만 명령으로 받음[9] | |

도구끼리 결과를 맞출 때는 `-o export` 나 `-o json` 으로 뽑은 `journalctl` 결과를 기준으로 삼고, 항목 수가 다르면 손상 파일을 도구마다 다르게 처리했을 가능성을 [손상·삭제된 저널](corruption.md) 에서 확인합니다. 여러 로그를 시간순으로 합치는 방법은 [타임라인 만들기](../../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 참고 문헌

1. systemd, man/journalctl.xml. https://github.com/systemd/systemd/blob/main/man/journalctl.xml
2. systemd, man/systemd.journal-fields.xml. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
3. systemd, "Journal Export Formats" (docs/JOURNAL_EXPORT_FORMATS.md). https://github.com/systemd/systemd/blob/main/docs/JOURNAL_EXPORT_FORMATS.md
4. systemd, man/journald.conf.xml. https://github.com/systemd/systemd/blob/main/man/journald.conf.xml
5. Red Hat, systemd-rhel9 source-git (meson.build `version : '252'`). https://github.com/redhat-plumbers/systemd-rhel9
6. log2timeline plaso, plaso/parsers/systemd_journal.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/systemd_journal.py
7. fox-it dissect.target, dissect/target/plugins/os/unix/log/journal.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/journal.py
8. Velocidex velociraptor, artifacts/definitions/Linux/Forensics/Journal/Fields.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Forensics/Journal/Fields.yaml
9. tclahr UAC, artifacts/live_response/system/journalctl.yaml. https://github.com/tclahr/uac/blob/main/artifacts/live_response/system/journalctl.yaml
