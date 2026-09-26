---
title: "에어드롭"
parent: "아티팩트 · 외부 장치"
nav_order: 1120
---

# 에어드롭 (AirDrop)

에어드롭이 근처 장치를 어떻게 찾고 연결하는지 정리하고, 그 과정이 맥에 남길 수 있는 흔적과 해석할 때의 한계를 다룹니다.

## 무엇을 기록하나 · 왜 생기나

에어드롭은 근처에 있는 애플 장치끼리 파일을 주고받는 기능이고, 근처 장치와 통신할 때 저전력 블루투스 (Bluetooth Low Energy, BLE)와 애플이 만든 P2P Wi-Fi 기술을 씁니다 [1]. 장치끼리 직접 통신하는 기능이라 조사할 때는 보낸 쪽과 받은 쪽 장치에 남은 흔적을 함께 봅니다.

장치는 먼저 사용자의 Apple 계정에 연결된 이메일 주소·전화번호로 짧은 신원 해시(AirDrop short identity hash)를 만듭니다 [1]. 기본 설정인 "연락처만 (Contacts Only)" 에서는 받는 쪽이 전달받은 짧은 해시를 자기 연락처의 해시와 비교해 일치할 때만 응답하고, "모든 사람 (Everyone)" 모드에서는 일치하는 사람이 없어도 응답합니다 [1]. 보내는 사람이 받는 사람을 고르면 보내는 장치가 받는 장치와 TLS 로 암호화한 연결을 열고, 양쪽이 iCloud 신원 인증서를 주고받습니다 [1].

그 인증서나 전송 내역이 맥의 어느 파일에 어떤 형식으로 남는지는 공식 문서에 나와 있지 않습니다 [1]. 그래서 아래 흔적 위치는 대부분 실제 기기에서 확인해야 합니다.

## 위치와 버전별 차이

에어드롭은 iOS 7 이상의 iPhone·iPad 와 OS X 10.11 이상의 맥에서 지원합니다 [1]. 이 핸드북이 주로 다루는 macOS 10.15 Catalina 이후는 모두 이 범위 안에 있습니다.

| 흔적 | 위치·이름 | 확인 여부 |
|---|---|---|
| 통합 로그 | 프로세스 `sharingd`, 서브시스템 `com.apple.sharing`, 카테고리 `AirDrop` | 실제 기기에서 확인 |
| 받은 파일 | 사용자 `~/Downloads` | 실제 기기에서 확인 |
| 받은 파일의 확장 속성 | `com.apple.quarantine`, `kMDItemWhereFroms` 가 붙는지, 값에 무엇이 들어가는지 | 실제 기기에서 확인 |
| 검색 허용 모드 설정 | `~/Library/Preferences/com.apple.sharingd.plist` (키 이름 `DiscoverableMode` 로 알려짐) | 키 이름·값 모두 실제 기기에서 확인 |
| 무선 직접 연결 인터페이스 | `awdl0` | 실제 기기에서 확인 |

"10분 동안 모든 사람 (Everyone for 10 minutes)" 설정이 있고 그 설정이 적용된 OS 버전이 따로 있다는 이야기가 있지만, 애플 보안 문서에는 나오지 않습니다 [1]. 실제 기기의 검색 허용 모드 값을 해석할 때는 이 설정이 있는 버전인지부터 확인해야 하고, 확인하기 전에는 모드 이름을 보고서에 단정해 쓰지 않습니다.

## 구조

에어드롭 전용 데이터베이스나 전송 기록 파일은 공개 자료에 알려진 것이 없습니다. 흔적은 위 표처럼 여러 곳에 흩어져 남는다고 알려져 있어서, 각 저장 형식은 해당 페이지에서 다룹니다.

통합 로그 형식은 [통합 로그 형식 (Unified Log)](../../01-foundations/data-formats/unified-log/index.md)에, 설정 plist 를 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에 있습니다. 받은 파일에 붙는 확장 속성은 [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md)과 [다운로드 출처 속성 (kMDItemWhereFroms)](../filesystem/where-froms.md)에서 형식을 봅니다. 에어드롭으로 받은 파일에 이 속성이 실제로 붙는지는 확인이 필요해서, 속성이 없다는 이유로 에어드롭이 아니라고 단정하지 않습니다.

## 증거로서 의미

**증명하는 것.** 공식 문서에 나와 있는 것은 동작 방식입니다 [1]. 받는 쪽이 "연락처만" 모드였다면 보내는 사람의 이메일 주소나 전화번호가 받는 쪽 연락처에 있었다는 뜻이 되고, 이 점은 두 사람의 관계를 따질 때 근거가 됩니다. 연결 과정에서 양쪽은 iCloud 신원 인증서를 주고받습니다 [1]. 맥에 남은 로그나 받은 파일에서 에어드롭 전송을 가리키는 기록을 찾았다면, 그 기록에 나온 시각에 근처의 애플 장치와 주고받은 기록이 있다고 쓸 수 있습니다.

**증명하지 못하는 것.** 이 페이지의 흔적 위치는 대부분 확인이 필요한 것이라, 흔적이 없다고 해서 에어드롭을 쓰지 않았다고 말할 수 없습니다. "모든 사람" 모드였다면 연락처에 없는 사람과도 주고받을 수 있어서 [1], 받는 쪽 연락처만으로 상대를 특정하지 못합니다. 짧은 신원 해시는 이메일 주소·전화번호로 만든 값이라 [1], 해시가 기록에 남아 있더라도 그 값을 사람 이름으로 바로 읽을 수는 없습니다.

보고서에는 "이 파일을 에어드롭으로 받았다" 가 아니라 "이 시각에 에어드롭 수신을 가리키는 로그가 있고, 같은 이름의 파일이 다운로드 폴더에 있다" 처럼 기록마다 나눠 씁니다.

## 시각 해석

통합 로그의 시각을 읽는 법은 [통합 로그 형식 (Unified Log)](../../01-foundations/data-formats/unified-log/index.md)에서 다룹니다. 받은 파일의 생성 시각은 파일이 이 맥에 만들어진 때를 가리키고, 보낸 쪽 원본 파일이 만들어진 때와는 다릅니다. 파일 안에 들어 있는 날짜(사진의 촬영 시각 같은 것)는 보낸 쪽에서 만든 값이라 [사진 메타데이터 (EXIF·HEIC)](../embedded-metadata/exif-heic.md)처럼 따로 해석합니다.

설정 plist 의 수정 시각은 설정이 바뀐 어느 때를 가리킬 뿐이고, 어느 모드로 언제 바꿨는지는 그 값만으로 알 수 없습니다.

## 함정과 한계

통합 로그에서 에어드롭 기록을 찾을 때 쓰는 프로세스·서브시스템·카테고리 이름은 확인이 필요한 값이라, 분석 대상과 같은 macOS 버전의 테스트 맥에서 먼저 확인한 뒤 걸러 봅니다. 로그가 얼마나 남는지와 수집 방법은 [통합 로그에서 찾을 것 (Unified Log Events)](../logs/unified-log-events/index.md)에서 봅니다.

받은 파일은 사용자가 다른 폴더로 옮기거나 이름을 바꿀 수 있고, 다운로드 폴더에 있다는 사실만으로는 브라우저 다운로드와 구분되지 않습니다. 파일 출처를 판별하는 흐름은 [이 파일은 어디서 왔나 (File Origin)](../../04-scenarios/activity/file-origin.md)을 따릅니다.

에어드롭은 저전력 블루투스를 쓰지만 [1], 에어드롭 상대가 [블루투스 장치 (Bluetooth)](bluetooth.md)의 페어링 목록에 남는지는 공개 자료가 없습니다. 페어링 목록에 상대 장치가 없다는 이유로 에어드롭 전송이 없었다고 보지 않습니다.

## 직접 분석해 보기

**헥스로 한 번.** 에어드롭 전용 파일 구조는 알려진 것이 없어서, 헥스로 따라갈 대상은 설정 plist 입니다. `com.apple.sharingd.plist` 가 있으면 첫 바이트로 이진 plist 인지 XML plist 인지 구분하고, 검색 허용 모드와 관련된 키 이름이 글자 영역에 보이는지 찾습니다. 이진 plist 를 오프셋 표로 따라가는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에 있습니다.

**공개 도구로 한 번.** 테스트 맥 두 대 사이에서 파일 하나를 에어드롭으로 보낸 뒤, 받은 쪽에서 아래처럼 확인합니다. 로그의 프로세스·서브시스템 이름은 확인이 필요한 값이라, 결과가 비면 이름부터 의심합니다.

```
log show --last 1h --predicate 'process == "sharingd"'
xattr -l ~/Downloads/받은파일
mdls -name kMDItemWhereFroms ~/Downloads/받은파일
plutil -p ~/Library/Preferences/com.apple.sharingd.plist
```

로그에서 전송 시각과 상대 장치를 가리키는 줄을 찾고, 받은 파일에 붙은 확장 속성이 브라우저로 내려받은 파일과 어떻게 다른지 비교해 봅니다.

## 교차 검증

받은 파일의 출처는 [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md)과 [다운로드 출처 속성 (kMDItemWhereFroms)](../filesystem/where-froms.md)으로, 파일이 만들어진 순서는 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)로 확인합니다. "연락처만" 모드에서 상대를 좁힐 때는 [연락처 (Contacts)](../cloud-apps/contacts.md)를, 이 맥의 Apple 계정은 [아이클라우드 계정 (iCloud Account)](../cloud-apps/icloud-account.md)을 봅니다. 무선 환경은 [와이파이 기록 (Wi-Fi)](../network/wifi.md)과 [네트워크 인터페이스와 설정 (SystemConfiguration)](../network/network-interfaces.md)에서, 자료가 밖으로 나갔는지 따지는 흐름은 [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md)에서 봅니다.

## 실습

테스트 맥 두 대, 또는 공개 시험 자료(NIST CFReDS 등)의 맥 이미지로 아래 질문을 풀어 봅니다.

1. 받은 파일이 어느 폴더에 생겼는가?
2. 받은 파일에 `com.apple.quarantine` 과 `kMDItemWhereFroms` 가 붙었는가? 붙었다면 값에 무엇이 들어 있는가?
3. 통합 로그에서 전송 시각을 가리키는 줄을 찾을 수 있는가? 어느 프로세스와 서브시스템으로 남았는가?
4. 검색 허용 모드를 "연락처만" 과 "모든 사람" 으로 바꿔 가며 설정 plist 의 어느 값이 바뀌는지 확인할 수 있는가?
5. 보낸 쪽 맥에는 어떤 흔적이 남는가? 받은 쪽 흔적과 시각이 맞는가?

## 참고 문헌

1. Apple Platform Security — AirDrop security — https://support.apple.com/guide/security/airdrop-security-sec2261183f4/web
