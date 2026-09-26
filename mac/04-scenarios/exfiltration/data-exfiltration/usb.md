---
title: "USB 저장 장치로"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 2450
---

# USB 저장 장치로 (USB)

## 조사 질문

이 맥에 USB 저장 장치를 연결하고 자료를 그 장치로 옮겼는지 묻습니다. 장치를 연결한 기록은 여러 곳에 남지만, 어떤 파일을 장치로 복사했는지 곧바로 적어 두는 기록은 공개된 분석 자료에 없습니다. 그래서 장치를 연결한 시각을 먼저 확인하고, 그 시간대에 어떤 파일을 다뤘는지 여러 흔적을 모아 맞춰 보는 방식으로 조사합니다. 경로마다 공통으로 쓰는 판단 원칙은 [자료를 밖으로 빼돌렸나](index.md) 허브에 있습니다.

장치 연결 기록 하나하나의 구조와 읽는 법은 [USB 저장 장치 (USB Storage)](../../../02-artifacts/external-devices/usb/index.md) 페이지에서 다루고, 이 페이지는 그 기록들을 유출 조사에 어떤 순서로 쓰는지만 다룹니다.

## 먼저 확인할 것

OS 버전과 시간대는 [OS 버전과 설치 기록](../../../02-artifacts/system-account/os-version-install-history.md)과 [시간대와 시계 설정](../../../02-artifacts/system-account/time-zone.md)에서 먼저 확인합니다. 흔적마다 시각을 적는 기준이 달라서, 모든 시각을 한 기준으로 바꿔 적어 두어야 뒤에서 대조할 수 있습니다([맥의 시각 값](../../../01-foundations/value-decoding/mac-time-values.md)).

사용자 범위는 누구의 홈 폴더를 볼지 정하는 일입니다. 파인더 사이드바 목록 파일 `com.apple.sidebarlists.plist`는 사용자 홈의 `Library/Preferences` 아래에 있어서 사용자마다 따로 보고, `volinfo.database`는 시스템 영역인 `/private/var/db/` 아래에 있어서 맥 전체에 하나입니다.

수집 범위에서는 맥 본체뿐 아니라 USB 장치 자체를 확보할 수 있는지가 중요합니다. 장치 쪽 볼륨에 남는 `.fseventsd`·`.Spotlight-V100` 폴더는 장치를 확보해야만 볼 수 있습니다. 통합 로그가 수집 범위에 들어 있는지도 함께 확인합니다([맥 증거 확보](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 통합 로그의 DiskArbitration 메시지 | 외부 볼륨이 붙고 떨어진 시각과 볼륨 정보 | [USB 저장 장치](../../../02-artifacts/external-devices/usb/index.md) |
| 2 | `/private/var/db/volinfo.database` | 예전에 연결했던 볼륨 일부의 파일 소유권 설정 | [USB 저장 장치](../../../02-artifacts/external-devices/usb/index.md) |
| 3 | `~/Library/Preferences/com.apple.sidebarlists.plist` | 파인더 사이드바에 나타난 항목 목록 | [파인더 설정과 기록](../../../02-artifacts/file-folder-usage/finder-plist.md) |
| 4 | 장치 볼륨의 `.fseventsd` | 장치 쪽에서 생기고 바뀐 파일 이름 | [파일 시스템 이벤트](../../../02-artifacts/filesystem/fsevents/index.md) |
| 5 | 장치 볼륨의 `.Spotlight-V100` | 장치 쪽 파일의 색인 정보 | [스포트라이트](../../../02-artifacts/file-folder-usage/spotlight/index.md) |
| 6 | 맥 쪽 최근 항목과 FSEvents | 같은 파일을 이 맥에서 열거나 옮긴 흔적 | [최근 항목](../../../02-artifacts/file-folder-usage/recent-items/index.md) |

`volinfo.database`는 예전에 연결한 볼륨의 파일 소유권 정보를 담는 파일이고, 경로는 `/private/var/db/volinfo.database`와 `/var/db/volinfo.database` 두 가지로 적힙니다 [1]. 볼륨마다 "볼륨 식별자: 플래그" 한 줄씩 적는 텍스트 파일입니다. 파인더에서 "이 볼륨의 소유권 무시" 설정을 바꿀 때 볼륨이 추가되는 것으로 보여서, 예전에 연결한 볼륨을 빠짐없이 적은 목록은 아닐 가능성이 있습니다 [1]. 그래서 이 파일에 볼륨이 없다고 연결한 적이 없다고 보지 않습니다. `com.apple.sidebarlists.plist`는 `~/Library/Preferences/` 아래와 함께 `~/Preferences/` 아래에 있을 수도 있습니다 [1].

## 분석 흐름

1. 통합 로그에서 DiskArbitration 메시지를 찾아 외부 볼륨이 붙은 시각과 떨어진 시각, 볼륨 이름을 뽑습니다. 찾을 문구와 디스크 설명 키는 [USB 저장 장치](../../../02-artifacts/external-devices/usb/index.md) 페이지에 정리해 두었습니다.
2. `volinfo.database`와 `com.apple.sidebarlists.plist`로 같은 볼륨이 이 맥에 연결된 적이 있는지 보강하고, 1단계에서 찾은 볼륨과 이어지는지 봅니다. `volinfo.database`는 모든 볼륨을 적는 목록이 아니라서 있으면 보강 근거로만 쓰고, 없다고 연결을 부정하지 않습니다.
3. 장치를 확보했다면 장치 볼륨의 `.fseventsd`에서 파일 이름을 뽑고, `.Spotlight-V100` 색인에 같은 이름이 있는지 찾습니다.
4. 3단계에서 나온 파일 이름을 맥 쪽 최근 항목과 FSEvents에서 찾아, 그 파일을 이 맥에서 열거나 옮긴 흔적이 있는지 봅니다.
5. 1~4단계의 시각과 이름을 한 [타임라인](../../../03-techniques/analysis/timeline/index.md)에 올려, 장치가 붙어 있던 시간대와 파일을 다룬 흔적이 겹치는지 봅니다.

흔적 하나로 결론을 내지 않고, 장치 연결·파일 접근·시각 세 가지가 서로 맞는지로 판단합니다.

## 흔한 오판

- **장치 연결 기록만으로 "복사했다"고 쓰는 경우.** 연결 기록은 장치가 이 맥에 붙었다는 사실까지만 말하고, 어떤 파일이 오갔는지는 말하지 않습니다.
- **통합 로그에 복사한 파일 이름이 남아 있으리라 기대하는 경우.** 파인더로 복사할 때 통합 로그에 파일 이름이 남는지는 공개된 분석 자료가 없습니다. USB 커널 로그 문구도 마찬가지라서, 테스트 기기에서 재현해 확인하기 전에는 근거로 쓰지 않습니다([도구 검증](../../../03-techniques/reporting/tool-validation.md)).
- **장치의 `.fseventsd`에 파일 이름이 있으면 이 맥에서 옮겼다고 보는 경우.** 같은 장치를 다른 컴퓨터에서도 썼다면 그 컴퓨터에서 생긴 기록일 수 있어서, 맥 쪽 흔적과 시각이 맞는지 따로 확인합니다.
- **흔적이 없으면 지웠다고 보는 경우.** 흔적이 없는 이유는 여러 가지이고, 지운 흔적은 [증거를 없애려 했나](../../activity/anti-forensics/index.md)의 방법으로 따로 찾습니다.

## 보고서 문장 예

> ○○○○년 ○월 ○일 ○시 ○분(UTC로 바꾼 시각) 통합 로그에 볼륨 이름 "○○"인 외부 볼륨이 연결된 기록이 있고, 같은 날 ○시 ○분에 이 볼륨이 분리된 기록이 있습니다. 이 볼륨이 들어 있는 USB 장치의 `.fseventsd`에는 "○○.xlsx" 파일 항목이 있고, 사용자 ○○의 최근 항목에는 같은 이름의 파일을 연 기록이 있습니다. 이 기록들만으로는 파일을 복사한 사람과 정확한 복사 시각을 정할 수 없습니다.

## 함께 볼 페이지

- [USB 저장 장치 (USB Storage)](../../../02-artifacts/external-devices/usb/index.md) — 연결 기록의 구조와 읽는 법
- [파일 시스템 이벤트 (FSEvents)](../../../02-artifacts/filesystem/fsevents/index.md) — 장치 쪽과 맥 쪽 파일 변경 기록
- [이 파일을 누가 언제 열었나 (File Access)](../../activity/file-access.md) — 파일 접근 흔적을 모으는 방법
- [아이폰으로 (iPhone)](iphone.md) — 케이블로 아이폰을 연결한 경우

## 참고 문헌

1. ForensicArtifacts, "artifacts/data/macos.yaml" — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
