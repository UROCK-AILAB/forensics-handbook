---
title: "그 시각에 맥을 쓴 사람이 누구인가"
parent: "시나리오 · 행위 재구성"
nav_order: 2370
---

# 그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)

## 조사 질문

특정 시각에 맥에서 일어난 행위를 누가 했는지 묻습니다. 맥의 기록 대부분은 "어느 계정으로" 까지만 말하고 "어느 사람이" 는 말하지 않아서, 이 페이지는 행위를 계정에 붙이는 단계와 계정을 사람에 잇는 단계를 나눠, 각 단계에서 어떤 기록이 근거가 되고 어떤 설정이 그 근거를 약하게 만드는지를 다룹니다.

## 먼저 확인할 것

먼저 맥에 있는 계정 목록과 계정마다 누가 쓰는지 알려진 정보를 확인합니다. 계정 목록은 [사용자 계정 (Local Accounts)](../../02-artifacts/system-account/user-accounts/index.md)에 있습니다.

다음으로 계정 하나를 여러 사람이 쓸 수 있게 만드는 설정이 있는지 봅니다. 로그인 창 설정 `/Library/Preferences/com.apple.loginwindow.plist` 의 `autoLoginUser` 는 자동 로그인 계정을, `GuestEnabled` 는 손님 계정을 켰는지를, `lastUserName` 은 마지막으로 로그인한 사용자를 보여 주고, 자동 로그인 암호는 `/private/etc/kcpassword` 파일에 저장됩니다. 자동 로그인이 켜져 있으면 맥을 켠 사람 누구나 그 계정으로 들어가게 되어, 계정 기록을 특정 사람에게 붙이는 근거가 크게 약해집니다. 자세한 키는 [로그인 창 설정 (loginwindow)](../../02-artifacts/system-account/loginwindow.md)에 있습니다.

마지막으로 시간대와 조사 구간을 정합니다. 계정 기록과 사람 쪽 자료(출입 기록, 다른 기기의 기록, 진술)를 맞추려면 모든 시각을 UTC 로 맞춰야 하고, 시간대는 [시간대와 시계 설정 (Time Zone·NTP)](../../02-artifacts/system-account/time-zone.md)에서 확인합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `/private/var/run/utmpx` 의 USER_PROCESS(7) 레코드 | 로그인한 사용자 이름, 단말, 호스트 이름 [1] | [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](usage-time.md) |
| 2 | 통합 로그의 로그인·잠금 해제 기록 | 로그인과 잠금 해제 시점. Apple Watch 잠금 해제는 `com.apple.sharing` 서브시스템, `AutoUnlock` 카테고리 | [통합 로그에서 찾을 것 (Unified Log Events)](../../02-artifacts/logs/unified-log-events/index.md) |
| 3 | `com.apple.loginwindow.plist`, `/private/etc/kcpassword` | 자동 로그인·손님 계정·마지막 사용자 | [로그인 창 설정 (loginwindow)](../../02-artifacts/system-account/loginwindow.md) |
| 4 | 파일의 `kMDItemLastUsedDate` | 파일을 연 마지막 시각 [3] | [이 파일을 누가 언제 열었나 (File Access)](file-access.md) |
| 5 | 문서의 `kMDItemAuthors`, `kMDItemCreator` | 문서에 적힌 저자와 만든 앱 [3] | [문서 메타데이터 (iWork·Office)](../../02-artifacts/embedded-metadata/iwork-office.md) |
| 6 | 메시지 `chat.db` 의 `account`, `destination_caller_id` | 어느 계정으로 메시지를 주고받았는지 [2] | [누구와 연락을 주고받았나 (Communication)](communication.md) |
| 7 | 원격 접속 기록 | 맥 앞이 아닌 곳에서 들어온 세션 | [원격 접속 (Remote Access)](../../02-artifacts/network/remote-access/index.md) |

### 행위를 계정에 붙이기

utmpx 의 USER_PROCESS 레코드에는 user·terminal·hostname 칸이 있어서 [1], 어느 계정이 언제 세션을 열었는지를 보여 줍니다. hostname 칸에 값이 있는 세션을 원격 세션으로, 없는 세션을 맥 앞의 콘솔 로그인으로 가르는 것은 칸 구조를 보고 필자가 내린 해석이고, SSH 나 화면 공유 세션이 실제로 어떤 terminal·hostname 값으로 남는지는 확인하지 못했습니다. 그래서 이 구분은 원격 접속 기록과 맞춰 본 뒤에만 보고서에 씁니다.

`kMDItemLastUsedDate` 는 LaunchServices 가 파일을 열 때마다(더블클릭 등) 자동으로 갱신합니다 [3]. 사용자 홈 폴더 아래 파일이면 그 계정으로 로그인한 세션에서 연 것으로 볼 근거가 된다는 해석은 필자 판단이고, 이 값은 마지막으로 연 시각 하나만 남아서 그보다 앞선 열람은 따로 찾아야 합니다.

메시지 데이터베이스의 `account` 와 `destination_caller_id` 칸에는 어느 계정으로 주고받았는지가 담깁니다 [2]. 이 값은 맥의 로그인 계정이 아니라 메시지 서비스의 계정이라서, 로그인 계정과 서비스 계정이 서로 맞는지를 확인하는 데 씁니다. 두 칸 값의 정확한 뜻은 확인하지 못했습니다.

### 문서에 적힌 사람

`kMDItemAuthors` 는 문서 저자(배열)이고 순서는 보존되지만 주 저자나 중요도를 뜻하지 않으며, `kMDItemCreator` 는 문서 내용을 만든 앱 이름(예: "Pages")입니다 [3]. 두 값 모두 앱이 문서에 적는 값이라서 그 시각에 로그인해 있던 사용자와 다를 수 있다는 점은 필자 판단입니다. 문서가 다른 컴퓨터에서 만들어졌거나 앱 설정의 사용자 이름이 계정과 다르면 저자 값은 로그인 계정과 맞지 않게 되니, 저자 값은 "문서에 이렇게 적혀 있다" 까지만 씁니다.

### 계정을 사람에 잇기

계정을 사람에 잇는 근거는 맥 안보다 맥 밖에 많습니다. 맥 안에서는 잠금을 푼 방식이 단서가 되는데, 통합 로그의 `com.apple.sharing` 서브시스템 `AutoUnlock` 카테고리 기록은 Apple Watch 로 잠금을 푼 흔적입니다. 이 기록을 그 계정에 연결된 Apple Watch 가 가까이 있었다는 뜻으로 읽는 것은 필자 판단이고, 시계를 찬 사람이 누구였는지는 알려 주지 않습니다. Touch ID 로 잠금을 풀 때 남는 로그 문구는 확인하지 못했습니다.

그 밖에는 같은 구간에 그 사람만 쓰는 계정(메시지·메일·메신저)이 활동했는지, 출입 기록이나 다른 기기의 기록이 맥 앞에 있었다는 사실과 맞는지를 봅니다. 빠른 사용자 전환 (Fast User Switching) 흔적과 콘솔 사용자가 바뀔 때 남는 로그는 확인하지 못해서, 한 맥에서 여러 계정이 동시에 세션을 열고 있던 경우는 utmpx 레코드로 세션 겹침만 확인합니다.

## 분석 흐름

1. 계정 목록, 자동 로그인·손님 계정 설정, `kcpassword` 파일이 있는지를 확인하고 결과를 먼저 적습니다. 자동 로그인이 켜져 있었다면 뒤 단계의 결론마다 이 사실을 함께 적습니다.
2. 조사 시각을 포함하는 로그인 세션을 utmpx 와 통합 로그에서 찾아, 그 시각에 세션을 연 계정을 정합니다. 여러 계정의 세션이 겹치면 모두 적습니다.
3. hostname 칸과 원격 접속 기록으로 그 세션이 맥 앞에서 열렸는지 원격으로 열렸는지를 가립니다. 가릴 수 없으면 "가리지 못했다" 고 적습니다.
4. 조사 대상 행위(파일 열기, 메시지 전송 등)의 기록이 2단계에서 찾은 계정의 홈 폴더와 세션 구간 안에 있는지 확인합니다.
5. 잠금 해제 방식, 같은 구간의 개인 계정 활동, 문서에 적힌 저자를 모아 그 계정을 쓰던 사람을 가리키는 근거와 반대 근거를 나란히 적습니다.
6. 맥 밖의 자료(출입 기록, 다른 기기, 진술)와 시각을 맞춰, 계정에서 사람으로 넘어가는 근거가 어디까지 이어지는지를 정리합니다.

> 그림 자리: "행위 → 계정 → 사람" 세 단계와 단계마다 근거가 되는 기록, 근거를 약하게 만드는 설정(자동 로그인·손님 계정·공유 암호)을 나란히 그린 도식

## 흔한 오판

계정 이름을 사람 이름과 같게 보는 경우가 가장 흔합니다. 기록으로 알 수 있는 것은 그 계정으로 행위가 있었다는 사실이고, 암호를 나눠 쓰거나 자동 로그인이 켜져 있거나 잠그지 않은 채 자리를 비운 경우에는 다른 사람이 같은 계정을 쓸 수 있습니다.

문서 저자 값을 그 문서를 만든 사람의 증거로 보는 것도 오판입니다. 저자 값은 앱이 적는 값이라서 다른 컴퓨터에서 만든 문서를 복사해 오거나 앱 설정의 이름이 달라도 그대로 남습니다.

`lastUserName` 에 적힌 사용자를 사건 시각의 사용자로 보는 것도 조심해야 합니다. 이 키는 확보 시점을 기준으로 한 마지막 사용자라서, 사건 시각의 사용자는 그 시각을 포함하는 세션 기록으로 따로 확인합니다.

## 보고서 문장 예

- "YYYY-MM-DD HH:MM UTC 를 포함하는 로그인 세션은 계정 A 의 세션 하나이며(`/private/var/run/utmpx` USER_PROCESS 레코드, 통합 로그 로그인 기록), 이 세션의 hostname 칸은 비어 있습니다. 이 맥에는 자동 로그인이 설정돼 있지 않았습니다."
- "이 기록들은 해당 행위가 계정 A 로 이뤄졌다는 점을 보여 줍니다. 계정 A 를 사용한 사람이 누구인지는 맥의 기록만으로 확정할 수 없으며, 같은 구간에 Apple Watch 잠금 해제 기록(`com.apple.sharing`, `AutoUnlock`)이 있다는 점을 함께 적습니다."

## 함께 볼 페이지

- [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](usage-time.md) — 세션 구간과 utmpx 레코드 구조
- [원격 접속 침입 확인 (Remote Intrusion)](../incident/remote-intrusion.md) — 원격 세션이 의심될 때
- [이 파일을 누가 언제 열었나 (File Access)](file-access.md) — 파일 열람을 계정에 붙이는 방법
- [포렌식 보고서 (Forensic Report)](../../03-techniques/reporting/forensic-report.md) — 계정과 사람을 나눠 적는 보고서 문장

## 참고 문헌

1. mac_apt `plugins/utmpx.py` (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/utmpx.py
2. mac_apt `plugins/imessage.py` (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/imessage.py
3. Apple Developer 문서 보관소 — MDItem Common Metadata Attribute Keys — https://developer.apple.com/library/archive/documentation/CoreServices/Reference/MetadataAttributesRef/Reference/CommonAttrs.html
