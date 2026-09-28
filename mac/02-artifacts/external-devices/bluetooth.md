---
title: "블루투스 장치"
parent: "아티팩트 · 외부 장치"
nav_order: 1080
---

# 블루투스 장치 (Bluetooth)

맥에 블루투스로 짝을 맺은(페어링한) 장치의 흔적을 어디서 찾고, 그 기록이 무엇을 말하고 무엇을 말하지 못하는지 정리합니다.

## 무엇을 기록하나 · 왜 생기나

맥은 블루투스 설정과 페어링한 장치 정보를 시스템 전역 속성 목록 파일 (Property List) 하나에 적어 둡니다 [1][2]. 키보드·마우스·헤드폰 같은 장치를 짝지은 정보가 남는 파일이라, 분석가에게는 "이 맥에 이런 이름의 장치가 짝지어진 적이 있다" 는 단서가 됩니다.

이 파일에는 블루투스 설정과 페어링한 장치 정보가 들어 있습니다(Mac OS X 10.9 기준) [1][2]. 수집 규칙 모음 ForensicArtifacts 에서는 이 파일을 `MacOSBluetoothPlistFile` 이라는 이름으로 정의합니다 [1].

## 위치와 버전별 차이

| 기록 | 위치 | 기준 | 출처 |
|---|---|---|---|
| 블루투스 설정·페어링 장치 plist | `/Library/Preferences/com.apple.Bluetooth.plist` | Mac OS X 10.9 기준, ForensicArtifacts 정의에 있음 | [1][2] |
| 최근 macOS 의 페어링 정보 | `/Library/Bluetooth/` 아래(`com.apple.MobileBluetooth.devices.plist`, `com.apple.MobileBluetooth.ledevices.paired.db` 등) | 실제 데이터로 확인 | — |

ForensicArtifacts 의 macOS 정의에서 블루투스 항목은 위 plist 하나뿐이고 다른 경로는 정의돼 있지 않습니다 [1]. macOS 12 Monterey 무렵부터 페어링 정보가 `/Library/Bluetooth/` 아래로 옮겨졌다는 설명이 있지만, 경로와 버전 경계는 실제 기기에서 확인해야 합니다. 그래서 분석할 때는 `com.apple.Bluetooth.plist` 만 보고 끝내지 말고 `/Library/Bluetooth/` 폴더가 있는지, 있다면 어떤 파일이 들어 있는지도 함께 봅니다.

## 구조

plist 파일을 읽는 방법 자체는 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

파일 안의 키 이름으로는 `DeviceCache`, `PairedDevices`, `LastInquiryUpdate`, `LastNameUpdate` 같은 것이 알려져 있습니다. 실제 파일에서 이 이름들이 보이면 이름 그대로 읽되, 각 키가 어떤 값을 담는지는 테스트 맥에서 장치를 짝지었다 풀어 보며 직접 확인한 뒤에 보고서에 씁니다.

페어링할 때 만드는 키(링크 키, link key)는 이 plist 가 아니라 시스템 키체인에 저장된다는 설명도 있습니다. 이 역시 확인이 필요하고, 키체인을 다루는 법은 [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 이 plist 에 어떤 장치 항목이 있으면, 그 장치가 이 맥과 짝지어진 적이 있다는 단서가 됩니다 [1][2]. 장치 이름이나 주소가 적혀 있다면 다른 기록에 나온 장치와 이어 볼 때 그 값을 씁니다.

**증명하지 못하는 것.** 짝지어진 적이 있다는 사실만으로는 언제 연결했는지, 몇 번 연결했는지, 누가 연결했는지를 말할 수 없습니다. 블루투스 장치로 파일을 주고받았는지도 이 파일로는 알 수 없습니다. 파일이 시스템 전역 위치에 있어서 사용자 계정이 여럿인 맥에서는 어느 계정이 짝지었는지도 이 파일만으로는 구분하지 못합니다.

보고서에는 "이 장치를 연결해 자료를 옮겼다" 가 아니라 "블루투스 설정 파일에 이 이름의 장치 항목이 남아 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

키 이름에 `Update` 가 들어간 값이 날짜 형식이면 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)의 방식 몇 가지로 풀어 보고, 같은 무렵의 다른 기록과 맞는 쪽을 고릅니다.

연결 이력은 KnowledgeC 의 `/bluetooth/isConnected` 스트림에서 찾습니다. 이 스트림의 `ZOBJECT` 행에는 시작·종료 시각이, `ZSTRUCTUREDMETADATA` 의 `Z_DKBLUETOOTHMETADATAKEY__NAME`·`Z_DKBLUETOOTHMETADATAKEY__ADDRESS`·`Z_DKBLUETOOTHMETADATAKEY__DEVICETYPE` 열에는 장치 이름·주소·종류가 들어 있습니다 [3]. 시각은 맥 절대 시각(2001-01-01 UTC 기준 초)이라 `ZSTARTDATE` 에 978307200 을 더하면 유닉스 시각이 됩니다 [3]. 이 구조가 알려진 버전은 iOS 11~14 와 macOS 10.16(Big Sur)이라 [3], 그 밖의 버전에서는 스트림과 열이 그대로인지 실제 데이터로 확인합니다. KnowledgeC 자체의 구조는 [KnowledgeC (knowledgeC.db)](../execution/knowledgec/index.md)에 있습니다.

파일의 수정 시각은 설정이나 장치 목록이 바뀐 어느 때를 가리킬 뿐이고, 특정 장치를 연결한 시각으로 읽으면 안 됩니다.

## 함정과 한계

위치 설명은 Mac OS X 10.9 기준이라 [2], 최근 macOS 에서 같은 파일에 같은 내용이 남는지는 실제 기기에서 확인해야 합니다. 분석 대상의 macOS 버전을 먼저 확인하고([OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../system-account/os-version-install-history.md)), 그 버전의 테스트 맥에서 같은 조작을 해 본 결과로 해석합니다.

수집 도구가 ForensicArtifacts 정의만 따라 파일을 모으면 `/Library/Bluetooth/` 아래 파일은 빠질 수 있습니다. 이 폴더는 정의에 없기 때문입니다 [1].

사용자가 장치를 목록에서 지웠을 때 plist 항목이 어떻게 되는지는 테스트 맥에서 장치를 짝지었다가 목록에서 지워 보고 확인합니다. 그 전에는 항목이 없어도 짝지은 적이 없다고 단정하지 않고, 통합 로그나 KnowledgeC 처럼 따로 남는 기록을 함께 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** `com.apple.Bluetooth.plist` 를 헥스 편집기로 열어 첫 바이트를 보고, 이진 plist 인지 XML plist 인지부터 구분합니다. 그 기준과 이진 plist 의 오프셋 표 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에 있어서 여기서 되풀이하지 않습니다. 장치 이름처럼 사람이 아는 글자가 헥스 창의 글자 영역에 보이는지 찾아보면, 어느 부분이 장치 항목인지 짐작하기 쉽습니다.

**공개 도구로 한 번.** 확보한 파일 사본을 macOS 에 들어 있는 `plutil` 로 풀어 봅니다.

```
plutil -p com.apple.Bluetooth.plist
```

출력에서 장치 주소처럼 보이는 키 아래에 이름과 날짜 값이 있는지 보고, 날짜 값은 위의 시각 해석 절대로 풉니다. 통합 로그에서 블루투스 기록을 찾을 때는 서브시스템 `com.apple.bluetooth`, 프로세스 `bluetoothd` 로 걸러 보는 방법이 알려져 있지만, 이 두 이름은 확인이 필요합니다.

```
log show --archive system_logs.logarchive --predicate 'process == "bluetoothd"'
```

## 교차 검증

연결된 순간의 기록은 [통합 로그에서 찾을 것 (Unified Log Events)](../logs/unified-log-events/index.md)과 [KnowledgeC (knowledgeC.db)](../execution/knowledgec/index.md)에서 찾습니다. 블루투스를 쓰는 다른 기능과 함께 볼 때는 [에어드롭 (AirDrop)](airdrop.md)과 [연속성과 유니버설 클립보드 (Continuity·Handoff)](../cloud-apps/continuity.md)를, 장치로 자료가 나갔는지 따질 때는 [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md)를 봅니다. 외장 장치 전체의 길잡이는 [USB 저장 장치 (USB Storage)](usb/index.md)부터 시작합니다.

## 실습

블루투스 장치를 짝지었다가 목록에서 지운 테스트 맥, 또는 공개 시험 자료(NIST CFReDS 등)의 맥 이미지로 아래 질문을 풀어 봅니다.

1. `/Library/Preferences/com.apple.Bluetooth.plist` 가 있는가? 이진 plist 인가, XML plist 인가?
2. `/Library/Bluetooth/` 폴더가 있는가? 있다면 안에 어떤 파일이 있고, 그 맥의 macOS 버전은 무엇인가?
3. 짝지은 장치의 이름이 어느 파일, 어느 키 아래에 나오는가?
4. 장치를 목록에서 지운 뒤에도 그 이름이 어느 파일에든 남아 있는가?
5. 같은 장치의 연결 시각을 통합 로그나 KnowledgeC 에서 찾을 수 있는가? 찾았다면 plist 의 날짜 값과 어떤 관계인가?

## 참고 문헌

1. ForensicArtifacts — artifacts/data/macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. Forensics Wiki — Mac OS X 10.9 Artifacts Location — https://forensics.wiki/mac_os_x_10.9_artifacts_location
3. APOLLO (Sarah Edwards) — modules/knowledge_audio_bluetooth_connected.txt — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_audio_bluetooth_connected.txt
