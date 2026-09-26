---
title: "페어링 기록"
parent: "아이폰·아이패드 연결"
grand_parent: "아티팩트 · 외부 장치"
nav_order: 1100
---

# 페어링 기록 (Lockdown)

페어링 기록 (Pairing Record)은 아이폰·아이패드가 맥을 "신뢰"한 뒤 맥의 `/var/db/lockdown` 폴더에 기기마다 하나씩 남는 plist 파일이고, 파일 이름이 기기의 UDID라서 이 맥과 짝을 맺은 기기를 가려내는 데 씁니다.

## 무엇을 기록하나 · 왜 생기나

기기를 컴퓨터에 연결하면 기기에 "이 컴퓨터 신뢰 (Trust This Computer)" 알림이 뜨고, 신뢰하는 과정에서 기기에 암호가 걸려 있으면 암호를 입력해야 합니다 [3]. 신뢰한 컴퓨터는 기기와 동기화하고 사진·동영상·연락처 같은 콘텐츠에 접근할 수 있으며, 이 신뢰는 사용자가 신뢰 목록을 바꾸거나 기기를 지우기 전까지 이어집니다 [3].

맥 쪽에서는 usbmuxd 데몬이 페어링 기록을 관리하고 [1], 기록 하나에는 인증서와 개인 키, 식별값이 들어갑니다 [2]. 파일 이름이 기기의 UDID라서 이 폴더를 보면 어떤 기기가 이 맥과 페어링했는지 알 수 있습니다 [2].

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 위치 | `/var/db/lockdown` (실제 경로 `/private/var/db/lockdown`) [1][2] |
| 파일 | 기기마다 `<UDID>.plist` 하나, 호스트 쪽 설정 파일 `SystemConfiguration.plist` 하나 [2] |
| 범위 | 시스템 폴더라서 사용자 계정과 관계없이 맥 전체에 하나 [1] |
| 관리하는 프로세스 | usbmuxd 데몬 [1] |

위 경로는 usbmuxd와 libimobiledevice 소스가 macOS에서 쓰는 값입니다 [1][2]. macOS 버전에 따라 경로나 키가 달라진다는 공개 자료는 없습니다. 윈도우에서는 공용 AppData 아래 `Apple\Lockdown` 폴더가 같은 역할을 합니다 [2].

## 구조

폴더에는 기기별 페어링 기록과 호스트 설정 파일만 놓입니다. `SystemConfiguration.plist` 를 뺀 나머지 `.plist` 파일은 이름에서 `.plist` 를 뗀 값이 기기 UDID입니다 [2]. 그래서 파일 목록만 봐도 페어링한 기기의 UDID를 모두 적을 수 있습니다.

기기별 페어링 기록에 들어가는 키는 아래와 같습니다 [2]. 두 개인 키는 호스트 쪽 개인 키이고 [2], 나머지 설명은 키 이름을 풀어 쓴 것입니다.

| 키 | 이름이 가리키는 것 |
|---|---|
| `DeviceCertificate` | 기기 인증서 |
| `HostCertificate` | 호스트(맥) 인증서 |
| `HostPrivateKey` | 호스트 개인 키 |
| `RootCertificate` | 루트 인증서 |
| `RootPrivateKey` | 루트 개인 키 |
| `HostID` | 호스트 식별값 |
| `SystemBUID` | 맥을 가리키는 값이라는 설명이 있음 |

`SystemBUID` 는 맥을 가리키는 값으로 `SystemConfiguration.plist` 와 각 페어링 기록에 함께 들어간다는 설명이 있습니다. 페어링 기록에 `EscrowBag` 과 `WiFiMACAddress` 키도 있다는 설명이 많으니, 이 키들이 있는지는 검체에서 확인합니다. 파일을 plist로 읽는 방법은 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| `<UDID>.plist` 가 있으면 이 맥이 그 UDID의 기기와 페어링했다는 것, 곧 기기에서 이 맥을 신뢰했다는 것 [2][3] | 페어링한 시각 |
| 페어링한 기기가 여러 대라면 그 UDID 목록 | 맥의 어느 사용자 계정으로 연결했는지 |
| 신뢰가 이어진 동안 이 맥이 기기와 동기화하고 콘텐츠에 접근할 수 있는 상태였다는 것 [3] | 실제로 어떤 데이터를 주고받았는지 |
| | 지금도 기기가 이 맥을 신뢰하고 있는지 |
| | USB로 연결했는지 Wi-Fi로 연결했는지 |

페어링 기록은 맥 전체에 하나라서 사용자 계정을 가려 주지 않습니다. 어느 계정에서 기기를 백업했는지는 사용자 홈 아래에 남는 [기기 백업 (MobileSync)](mobilesync.md)에서 확인합니다.

## 시각 해석

plist 안에 페어링 시각을 적는 키가 있다는 공개 자료는 없습니다. 파일의 생성·수정 시각으로 첫 페어링이나 다시 페어링한 시점을 어림한다는 설명이 알려져 있지만, 이 방법은 파일 시스템 시각에 기댄 추정이라서 보고서에는 "파일 시각으로 어림한 값" 이라고 적습니다. 파일 시스템 시각을 읽는 방법은 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md)와 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

## 함정과 한계

페어링 기록에는 호스트 개인 키(`HostPrivateKey`, `RootPrivateKey`)가 들어 있어서 [2], 증거로 다룰 때 민감 자료로 취급합니다. 사본을 보관하는 곳과 접근할 수 있는 사람을 제한하고, 보고서나 첨부 자료에 키 값을 그대로 옮기지 않습니다.

기기 쪽에서는 설정 → 일반 → 전송 또는 [기기] 재설정 → 재설정 → 위치 및 개인 정보 보호 재설정으로 신뢰 목록을 지울 수 있습니다 [3]. 이때 맥 쪽 `/var/db/lockdown` 파일도 함께 지워진다는 공개 자료는 없습니다. 그래서 맥에 파일이 남아 있다고 해서 지금도 기기가 이 맥을 신뢰한다고 말하지 않습니다. 반대로 파일이 없다는 사실만으로 페어링한 적이 없다고 말하지도 않는데, 파일이 지워졌을 수 있기 때문입니다. 지운 흔적은 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)와 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)로 찾아봅니다.

페어링이 USB 연결뿐 아니라 Wi-Fi 동기화에도 쓰인다는 설명이 흔하지만, 기록만으로 연결 방식을 단정하지 않습니다. 라이브 수집에서 파일이 보이지 않으면 권한 때문인지 먼저 확인하고 수집 방법은 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md)을 따릅니다.

## 직접 분석해 보기

헥스로 볼 때는 `<UDID>.plist` 파일을 헥스 편집기로 열어 첫 바이트로 plist 형식을 가리고, 그 형식에 맞는 방법으로 키를 따라갑니다. 형식별 머리와 읽는 순서는 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에 있습니다. 아래는 키 목록만 명세로 만든 예시이고, 특정 검체에서 나온 값이 아닙니다.

```
private/var/db/lockdown/
├── SystemConfiguration.plist      호스트 쪽 설정
└── <UDID>.plist                   기기마다 하나 (명세로 만든 예시)
      DeviceCertificate   (인증서 데이터)
      HostCertificate     (인증서 데이터)
      HostPrivateKey      (개인 키 - 보고서에 옮기지 않음)
      RootCertificate     (인증서 데이터)
      RootPrivateKey      (개인 키 - 보고서에 옮기지 않음)
      HostID              (식별값)
      SystemBUID          (식별값)
```

공개 도구로 볼 때는 libimobiledevice가 폴더를 읽는 방식을 그대로 따라 하면 됩니다 [2]. 확보한 이미지에서 `private/var/db/lockdown` 폴더의 파일 목록을 뽑아 `SystemConfiguration.plist` 를 빼고, 남은 파일 이름에서 `.plist` 를 떼면 페어링한 기기의 UDID 목록이 됩니다. 이미지를 확보하는 방법은 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)에서 다룹니다.

## 교차 검증

UDID를 [기기 백업 (MobileSync)](mobilesync.md)의 백업 폴더 이름, `Info.plist` 식별값과 맞춰 보면 페어링과 백업을 같은 기기로 묶을 수 있고, 맞춰 보는 방법은 그 페이지에 있습니다. 연결 시각은 페어링 기록에서 얻기 어려워서 다른 기록으로 채웁니다. 통합 로그에서 usbmuxd·AMPDevicesAgent 프로세스 항목으로 기기 연결을 찾는다는 설명이 있으니 서브시스템 이름은 검체에서 확인합니다. 로그를 다루는 방법은 [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md)에 있습니다. 다른 외장 장치 기록과 한 시간축에 놓을 때는 [USB 저장 장치 (USB Storage)](../usb/index.md)와 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)을 함께 봅니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 iOS 기기를 연결한 흔적이 있는 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. `private/var/db/lockdown` 폴더에서 페어링한 기기의 UDID를 모두 적어 보세요. 몇 대인가요?
2. 각 UDID와 같은 이름의 백업 폴더가 어느 사용자 홈에 있나요? 페어링 기록은 있는데 백업이 없는 기기는 무엇을 뜻할 수 있나요?
3. `<UDID>.plist` 파일의 생성·수정 시각을 다른 기록의 연결 시각과 비교해 보고, 파일 시각만으로 보고서에 쓸 수 있는 문장을 한 줄로 적어 보세요.

## 참고 문헌

1. libimobiledevice/usbmuxd README — https://github.com/libimobiledevice/usbmuxd
2. libimobiledevice 소스 common/userpref.c — https://raw.githubusercontent.com/libimobiledevice/libimobiledevice/master/common/userpref.c
3. Apple Support — About the "Trust This Computer" alert on your iPhone, iPad, or iPod touch — https://support.apple.com/en-us/109054
