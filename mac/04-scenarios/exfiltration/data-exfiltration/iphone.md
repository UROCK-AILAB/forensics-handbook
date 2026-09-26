---
title: "아이폰으로"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 2510
---

# 아이폰으로 (iPhone)

## 조사 질문

이 맥에 연결한 아이폰으로 자료를 옮겼는지 묻습니다. 맥에서 아이폰으로 파일을 옮기는 길은 케이블로 연결한 뒤 파인더로 파일을 공유하거나 동기화하는 방법, 에어드롭 등 여러 가지이지만, 어떤 파일을 옮겼는지 적어 두는 전송 기록은 공개된 분석 자료에 없습니다. 그래서 이 맥에 어떤 아이폰이 언제 연결되었는지를 먼저 세우고, 그 기기가 확보한 휴대전화와 같은지 맞춰 본 뒤, 연결 시간대에 파일을 다룬 흔적을 모으는 방식으로 조사합니다. 경로마다 공통으로 쓰는 판단 원칙은 [자료를 밖으로 빼돌렸나](index.md) 허브에 있습니다.

페어링 기록과 백업의 구조는 [아이폰·아이패드 연결 (iOS Devices)](../../../02-artifacts/external-devices/ios-devices/index.md) 페이지에서 다루고, 이 페이지는 사용자 설정 파일 `com.apple.iPod.plist`와 이 기록들을 유출 조사에 쓰는 순서를 다룹니다.

## 먼저 확인할 것

OS 버전과 시간대는 [OS 버전과 설치 기록](../../../02-artifacts/system-account/os-version-install-history.md)과 [시간대와 시계 설정](../../../02-artifacts/system-account/time-zone.md)에서 먼저 확인합니다. `com.apple.iPod.plist`가 어느 macOS 버전까지 갱신되는지, 아이폰 동기화를 파인더가 맡은 뒤에도 같은 파일이 쓰이는지는 공개된 분석 자료가 없습니다. 그래서 검체에서 이 파일의 수정 시각이 조사 시간대와 가까운지 먼저 보고, 오래전에 멈춘 파일이면 페어링 기록과 백업 쪽에 무게를 둡니다.

`com.apple.iPod.plist`는 사용자 홈의 `Library/Preferences` 아래에 있는 사용자별 파일이라 [2] 사용자마다 따로 봅니다. 수집 범위에는 각 사용자의 이 파일과 백업 폴더, 시스템 영역의 페어링 기록 폴더 `/var/db/lockdown/`가 들어 있어야 하고, 아이폰 자체를 확보할 수 있는지도 확인합니다. 아이폰 쪽 흔적은 이 핸드북(맥)의 범위 밖이라, 여기서는 맥 기록과 맞춰 볼 식별값만 다룹니다.

이 맥과 아이폰이 같은 애플 계정에 로그인되어 있는지도 확인합니다([아이클라우드 계정](../../../02-artifacts/cloud-apps/icloud-account.md)). 같은 계정 기기끼리 주고받은 에어드롭이 어떻게 처리되는지는 [에어드롭으로](airdrop.md) 페이지에서 다룹니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `~/Library/Preferences/com.apple.iPod.plist` | 이 사용자 환경에 연결된 기기의 식별값·기종, mac_apt가 연결 횟수·마지막 연결로 읽는 값 | 이 페이지 아래 |
| 2 | 페어링 기록 `/var/db/lockdown/` | 이 맥과 신뢰 관계를 맺은 기기 | [아이폰·아이패드 연결](../../../02-artifacts/external-devices/ios-devices/index.md) |
| 3 | `~/Library/Application Support/MobileSync/Backup/*` | 이 맥에 만든 기기 백업 | [아이폰·아이패드 연결](../../../02-artifacts/external-devices/ios-devices/index.md) |
| 4 | 최근 항목·파일 시스템 이벤트 | 연결 시간대에 이 맥에서 다룬 파일 | [최근 항목](../../../02-artifacts/file-folder-usage/recent-items/index.md), [파일 시스템 이벤트](../../../02-artifacts/filesystem/fsevents/index.md) |
| 5 | 에어드롭 흔적 | 케이블 없이 옮긴 경우 | [에어드롭으로](airdrop.md) |

`com.apple.iPod.plist`는 연결된 iOS 기기(Attached iDevices) 기록입니다. 백업은 `~/Library/Application Support/MobileSync/Backup/*` 아래에 있고, 그 안에 `info.plist`·`Manifest.plist`·`Status.plist`가 있습니다 [1].

### com.apple.iPod.plist 에서 볼 값

이 파일의 `Devices` 사전 아래에 기기마다 항목이 있고, 기기 항목에는 아래 키가 있습니다 [2]. 파일 형식을 읽는 법은 [속성 목록 파일](../../../01-foundations/data-formats/plist/index.md) 페이지에 있습니다.

| 묶음 | 키 | 조사에서 쓰는 곳 |
|---|---|---|
| 기기 식별 | `Serial Number`, `ID`, `IMEI`, `MEID` | 확보한 아이폰과 맞춰 보기, `ID`는 페어링 기록·백업 폴더 이름과도 맞춰 보기 |
| 기종과 소프트웨어 | `Device Class`, `Product Type`, `Firmware Version`, `Firmware Version String`, `Build Version` | 어떤 기기였는지 설명하기 |
| 판매 지역 | `Region Info` | 확보한 기기와 같은지 보조로 확인하기 |
| 연결 | `Use Count`, `Connected` | 연결 횟수와 마지막 연결 시각 |

`Connected`는 plist 날짜형이라 따로 변환하지 않고 날짜로 읽습니다. mac_apt는 이 값을 `Last_Connected`(마지막 연결) 칸으로 내보냅니다 [2]. 그래서 이 값은 마지막 연결 시각으로, `Use Count`는 연결 횟수로 흔히 읽지만, 이는 도구의 칸 이름에서 나온 해석이고 두 키의 뜻을 밝힌 공식 문서는 없습니다. `Region Info`는 '/' 앞부분 코드로 판매 지역을 알 수 있어서 "LL"이면 미국, "CH"면 중국입니다 [2].

## 분석 흐름

1. 사용자마다 `com.apple.iPod.plist`에서 기기 목록을 뽑고, 기기마다 식별값·기종·`Use Count`·`Connected`를 적습니다.
2. 1단계의 식별값을 페어링 기록 파일 이름과 백업 폴더 이름에 맞춰 봅니다. `ID` 값이 페어링 기록 파일 이름에 쓰이는 UDID와 같은지는 공개된 분석 자료가 없어서, 검체에서 실제로 겹치는지 보고 겹칠 때만 같은 기기로 잇습니다.
3. 아이폰을 확보했다면 그 기기의 일련번호와 IMEI를 1단계 값과 대조해 같은 기기인지 확인합니다.
4. `Connected` 시각 앞뒤로 이 맥에서 대상 파일을 열거나 옮긴 흔적을 최근 항목과 FSEvents에서 찾습니다.
5. 케이블 연결 흔적이 없거나 시간대가 맞지 않으면 에어드롭과 [클라우드로](cloud.md) 페이지의 흔적도 봅니다.
6. 1~5단계의 시각을 한 [타임라인](../../../03-techniques/analysis/timeline/index.md)에 올려, 기기 연결과 파일 접근이 한 시간대에 겹치는지 봅니다.

## 흔한 오판

- **연결 기록만으로 "아이폰으로 옮겼다"고 쓰는 경우.** 연결 기록은 기기가 이 맥에 붙었다는 사실까지만 말하고, 어떤 파일이 오갔는지는 말하지 않습니다.
- **`Connected`로 연결 이력 전체를 본다고 여기는 경우.** 이 값은 기기마다 시각 하나라서, 그보다 앞선 연결 시각은 이 파일로 알 수 없습니다. 앞선 연결은 페어링 기록과 백업 쪽에서 따로 찾습니다.
- **백업이 있으면 아이폰으로 자료를 옮겼다고 보는 경우.** 백업은 아이폰의 데이터를 맥에 복사해 둔 것이라 방향이 반대입니다. 다만 백업 시각은 기기가 연결되어 있던 시간대를 세우는 데 쓸 수 있습니다.
- **`Region Info`의 판매 지역을 사용자가 있던 곳으로 읽는 경우.** 판매 지역은 기기를 판 지역일 뿐이고 사용자의 위치와는 관계가 없습니다.

## 보고서 문장 예

> 사용자 ○○의 `com.apple.iPod.plist`에 일련번호 "○○"인 아이폰 항목이 있고, 이 항목의 `Connected` 값은 ○○○○년 ○월 ○일 ○시 ○분(UTC로 바꾼 시각)입니다. 이 일련번호는 확보한 휴대전화의 일련번호와 같습니다. 같은 사용자의 최근 항목에는 그보다 ○분 앞서 "○○.pdf" 파일을 연 기록이 있지만, 이 기록들만으로는 이 파일을 아이폰으로 옮겼는지 정할 수 없습니다.

## 함께 볼 페이지

- [아이폰·아이패드 연결 (iOS Devices)](../../../02-artifacts/external-devices/ios-devices/index.md) — 페어링 기록과 백업 구조
- [에어드롭으로 (AirDrop)](airdrop.md) — 케이블 없이 옮긴 경우
- [USB 저장 장치로 (USB)](usb.md) — 케이블로 연결한 저장 장치를 조사하는 순서
- [이 파일을 누가 언제 열었나 (File Access)](../../activity/file-access.md) — 파일 접근 흔적을 모으는 방법

## 참고 문헌

1. ForensicArtifacts, "artifacts/data/macos.yaml" — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. mac_apt, plugins/iDeviceInfo.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/iDeviceInfo.py
