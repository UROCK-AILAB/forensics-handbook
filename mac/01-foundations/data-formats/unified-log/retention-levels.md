---
title: "보관 기간과 로그 수준"
parent: "통합 로그 형식"
grand_parent: "기반 · 데이터 저장 형식"
nav_order: 250
---

# 보관 기간과 로그 수준 (Persist·Info·Debug)

통합 로그는 메시지의 로그 수준에 따라 디스크에 남길지가 달라지고, 디스크에 남긴 메시지도 저장소가 정해진 크기를 넘으면 오래된 것부터 지워서, 로그가 얼마나 남는지는 정해진 날짜 수보다 수준과 용량에 따라 달라집니다.

## 로그 수준과 디스크 저장

Apple 문서는 로그 수준마다 디스크에 저장하는지를 아래처럼 적었습니다 [1]. 수준마다 tracev3 파일에 들어가는 로그 종류 값은 [tracev3 파일 구조 (tracev3)](tracev3.md)에 있습니다.

| 수준 | 디스크 저장 | 쓰임 |
|---|---|---|
| Debug | 저장하지 않음 | 개발 중 디버깅 |
| Info | `log` 도구로 모을 때만 저장 | 도움은 되지만 꼭 필요하지는 않은 정보 |
| Notice(Default) | 저장 한도까지 저장 | 기본 수준 |
| Error | 저장 한도까지 저장 | 활동(activity) 객체가 있으면 관련 프로세스 체인 정보도 함께 잡음 |
| Fault | 저장 한도까지 저장 | 활동 객체가 있으면 관련 프로세스 체인 정보도 함께 잡음 |

보통 debug·info 메시지는 메모리에만 두고, info 메시지는 `log` 명령으로 디스크에 쓰게 할 수 있습니다 [1]. 나머지 수준의 메시지는 압축해서 디스크 저장소에 쓰고, 저장소가 정해진 크기를 넘으면 가장 오래된 메시지부터 지웁니다 [1]. 메모리에만 있는 메시지는 전원을 끈 뒤 뜬 디스크 이미지에는 없고, 켜져 있는 맥에서 `log collect` 로 모으면 메모리에 있던 항목이 로그 아카이브에 함께 담깁니다 [5]. 그 방법은 [로그 아카이브 만들고 읽기 (logarchive)](logarchive.md)에서, 켜진 맥에서 증거를 모으는 순서는 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md)에서 다룹니다.

## 폴더별 용량 (관측값)

아래 표는 Mandiant 글이 관측한 값이고 Apple이 밝힌 한도가 아닙니다 [5]. 폴더 위치는 [tracev3 파일 구조 (tracev3)](tracev3.md)에 있습니다.

| 폴더 | tracev3 파일 하나의 최대 크기 | 관측한 최대 파일 개수 |
|---|---|---|
| Persist | 약 10.5 MB | 약 52개, 합계 최대 약 520 MB |
| Special | 약 2.1 MB | 다양함 |
| Signpost | 약 2.1 MB | 다양함 |
| HighVolume | 알 수 없음 | 다양함 |

같은 글은 약 10.5 MB짜리 tracev3 파일 하나에 로그가 30만~40만 건, 시스템 전체로는 1,800만~5,000만 건 정도 들어 있다고 적었습니다 [5]. 폴더마다 어떤 로그가 들어가는지와 보통 며칠치가 남는지는 참고 문헌에서 확인하지 못해서, 검체마다 가장 이른 항목의 시각을 직접 확인합니다.

## 로그 수준을 바꾼 흔적

서브시스템별 로그 수준은 `log config` 명령으로 바꿀 수 있고, 이 명령은 root 권한이 필요합니다 [3].

```
sudo log config --mode "level:debug" --subsystem <서브시스템 이름>
sudo log config --status --subsystem <서브시스템 이름>
```

첫 줄은 수준을 debug로 올리고 둘째 줄은 현재 설정을 확인합니다 [2]. `--mode` 에는 기록 수준을 정하는 `level:` 과 저장소에 쓸 수준을 정하는 `persist:` 가 있고 값은 둘 다 off·default·info·debug입니다 [3]. `--subsystem` 을 빼면 시스템 전체 설정을 바꾸고, `--category` 는 `--subsystem` 과 함께 써야 하며, `--process` 로 프로세스 하나만 바꿀 수도 있고, `--reset` 으로 설정을 되돌립니다 [3]. `log config` 로 바꾼 설정이 디스크의 어느 파일에 남는지는 참고 문헌에서 확인하지 못했습니다.

명령 대신 아래 경로에 서브시스템마다 로깅 설정 plist 파일을 만들어 넣어도 로그 수준을 바꿀 수 있습니다 [2].

```
/Library/Preferences/Logging/Subsystems/<서브시스템 역DNS 이름>.plist
```

plist의 최상위에는 서브시스템 전체에 적용하는 `DEFAULT-OPTIONS` 딕셔너리와 카테고리 이름으로 된 딕셔너리가 있고, 각 딕셔너리 안의 `Level` 딕셔너리에 `Enable` 과 `Persist` 키가 들어 있습니다 [2]. `Persist` 는 메시지를 메모리에만 둘지 저장소에도 쓸지 정합니다 [2]. plist 형식 자체는 [속성 목록 파일 (Property List)](../plist/index.md)에서 설명합니다.

| 키 | 값 | 뜻 |
|---|---|---|
| `Enable` | `Inherit`, `Default`, `Info`, `Debug` | 어느 수준까지 기록할지 |
| `Persist` | `Inherit`, `Default`, `Info`, `Debug` | 어느 수준까지 저장소에 쓸지 |

`Default` 는 default 수준만, `Info` 는 default·info 수준을, `Debug` 는 debug 수준까지 잡습니다 [2]. `Inherit` 는 윗단계 설정을 물려받는다는 뜻이고, 카테고리는 서브시스템 설정을, 서브시스템은 시스템 설정을 물려받습니다 [2].

같은 설정은 구성 프로필(MDM)로도 내려보낼 수 있습니다. 페이로드 이름은 `com.apple.system.logging` 이고 macOS 10.12부터 쓸 수 있으며, `Subsystems` 키는 위 plist와 같은 형식이고 `System` 키에는 `Enable-Private-Data` 하나가 들어가서 true이면 시스템 전체에서 비공개 데이터를 기록합니다 [4]. Apple 예시에서는 서브시스템의 `DEFAULT-OPTIONS` 딕셔너리 안에 값이 `Public` 인 `Default-Privacy-Setting` 키도 보입니다 [4]. 설치된 구성 프로필을 찾는 법은 [구성 프로파일 (Configuration Profiles·MDM)](../../../02-artifacts/persistence/configuration-profiles.md)에서 다룹니다.

## 비공개 값 (private)

기본 설정에서는 정수·실수·불리언 값은 그대로 기록하고, 동적 문자열과 복잡한 동적 객체의 내용은 가립니다 [1]. 개발자는 형식 문자열에 `%{private}` 나 `%{public}` 을 붙여 이 규칙을 바꿀 수 있습니다 [1]. 가려진 값은 `<private>` 로 보이고, 나중에 비공개 데이터 기록을 켜도 이미 기록된 항목은 풀리지 않습니다 [5]. 개발자가 `%{mask.hash}` 를 붙이면 가려진 자리에 원래 값을 해시한 문자열이 들어가서, 값은 모르더라도 같은 값이 쓰인 항목끼리 묶어 볼 수 있습니다 [1]. Mandiant 글의 DNS 질의 예에서도 비공개 데이터 기록이 꺼져 있을 때 호스트 이름이 해시한 뒤 base64로 바꾼 모양으로 나왔습니다 [5].

## 증거로서 의미

로그로 알 수 있는 범위는 그 수준의 메시지가 저장소에 남았다는 사실까지입니다. 기본 설정에서 debug·info 메시지는 디스크에 없어서 [1], 디스크 이미지에서 debug·info 항목을 찾지 못했다고 그 일이 없었다고 결론 내리지 않습니다. 오래된 메시지는 용량 한도에 따라 지워져서 [1], 어느 시점 이전에 로그가 없는 것도 그 자체로 삭제를 뜻하지 않습니다. 로그를 일부러 지운 경우와 가려 보는 법은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

거꾸로 조사 대상 맥에 `/Library/Preferences/Logging/Subsystems/` 아래 plist나 `com.apple.system.logging` 구성 프로필이 있으면, 그 서브시스템은 기본보다 더 많이 기록했거나 비공개 값까지 기록했을 수 있습니다. 이런 설정이 있는지 먼저 확인해야 같은 서브시스템의 로그 양이 다른 맥과 다른 까닭을 설명할 수 있습니다.

## 함정

Firehose·Oversize 청크에는 TTL 칸이 있고(칸 배치는 [tracev3 파일 구조 (tracev3)](tracev3.md)에 있음), `log erase --ttl` 이 TTL 로그를 따로 지우는 것으로 보아 [3] 용량과 별도로 수명이 정해진 로그도 있습니다. 다만 참고 문헌에 TTL의 단위와 동작이 적혀 있지 않아서, TTL 값으로 항목이 언제 지워질지 계산하지 않습니다. 폴더별 용량 표는 한 글의 관측값이라서 macOS 버전과 기기에 따라 다를 수 있습니다. 시스템 기본 로깅 설정 파일이 어디에 있는지도 참고 문헌에서 확인하지 못했습니다. `~/.logrc` 는 `log` 명령 자체의 사용자 설정 파일이라서 [3] 로그 수준 설정과 헷갈리지 않습니다.

## 참고 문헌

1. Apple Developer, Generating Log Messages from Your Code — https://developer.apple.com/tutorials/data/documentation/os/generating-log-messages-from-your-code.json
2. Apple Developer, Customizing Logging Behavior While Debugging — https://developer.apple.com/tutorials/data/documentation/os/customizing-logging-behavior-while-debugging.json
3. SS64, macOS `log` 명령 설명 — https://ss64.com/mac/log.html
4. Apple Developer, Device Management — SystemLogging 페이로드 — https://developer.apple.com/tutorials/data/documentation/devicemanagement/systemlogging.json
5. Alexander Holcomb (Mandiant), Reviewing macOS Unified Logs (Google Cloud 블로그, 2022-08-31) — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
