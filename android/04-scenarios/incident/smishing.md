---
title: "스미싱 흔적"
parent: "시나리오 · 침해 사고"
nav_order: 1770
---

# 스미싱 흔적 (Smishing)

## 조사 질문

"그 문자를 언제, 어느 번호로 받았나", "문자 속 링크를 눌렀나", "링크를 거쳐 파일을 받거나 앱을 깔았나", "피해자 폰에서 다른 사람에게 같은 문자가 나갔나" 같은 질문에 답하는 흐름입니다. 문자로 받은 링크에서 설치까지 이어졌다면 설치 쪽은 [악성 앱은 어디서 들어왔나](initial-access.md) 에서, 가짜 페이지에 계정 정보를 넣은 뒤의 일은 [계정 탈취 흔적](account-takeover.md) 에서 이어 봅니다.

Google Play 보호 기능(Play Protect)의 분류에서 피싱(Phishing)은 믿을 만한 곳에서 온 것처럼 꾸며 사용자의 인증 정보나 결제 정보를 요청하고 그 데이터를 제3자에게 보내는 코드이고, 흔한 목표로 은행 계정, 카드, SNS 계정을 듭니다 [1]. 같은 문서는 트로이 목마(Trojan)의 예로 겉으로는 게임이지만 뒤에서 유료 문자(premium SMS)를 보내는 코드를 듭니다 [1].

기록은 문자를 받고 보낸 시각과 상대 주소, 본문, 보낸 문자를 만든 앱까지 알려 주지만, 사용자가 문자를 읽고 속았는지나 링크를 누른 사람이 누구인지는 알려 주지 않습니다.

## 먼저 확인할 것

- **OS 버전과 기본 문자 앱** — 받은 문자를 문자 저장소에 쓰는 것은 `SMS_DELIVER` 방송을 받는 기본 문자(SMS) 앱입니다 [2]. Android 10(Q)부터는 기본 문자 앱을 바꾸는 인텐트(`ACTION_CHANGE_DEFAULT`)를 지원하지 않고 역할 관리자(RoleManager)의 `ROLE_SMS` 를 씁니다 [2]. 관찰 기기의 settings secure 키 목록에는 `sms_default_application` 이 없었는데, 기본 문자 앱을 역할로 정한다는 소스 내용과 어긋나지 않습니다. 역할을 저장하는 파일의 경로와 삼성 메시지 앱의 DB 경로·표는 이번 조사에서 확인하지 못했으니 [문자](../../02-artifacts/communications/messages/index.md) 페이지를 기준으로 읽습니다.
- **시간대와 시각 단위** — 문자 기록의 `date`(받은 시각)와 `date_sent`(보낸 시각)는 INTEGER long 이고 [2], 단위는 이번에 연 소스 주석에 적혀 있지 않습니다. 단위와 변환은 [문자](../../02-artifacts/communications/messages/index.md) 와 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 확인하고, 기기 시간대는 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md) 에서 봅니다.
- **SIM 구분** — 문자 기록에는 `sub_id` 칸이 있습니다 [2]. 이름으로 보아 가입 정보(SIM)를 가리는 칸이지만 이번 조사에서 뜻을 확인하지는 않았으니, 듀얼 SIM 기기라면 [문자](../../02-artifacts/communications/messages/index.md) 페이지 기준으로 어느 번호로 받은 문자인지부터 나눕니다.
- **수집 범위** — 문자 본문은 기본 문자 앱과 문자 저장소에 있고, 링크를 연 흔적은 브라우저 쪽에, 내려받은 파일은 미디어 저장소 쪽에 있어서 세 곳을 모두 확보해야 한 흐름이 이어집니다. 확보 방식은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 정합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 문자 저장소 (`content://sms`) | 받은·보낸 문자의 상대 주소, 시각, 본문, 읽음 여부 | [문자](../../02-artifacts/communications/messages/index.md) |
| 2 | 문자 기록의 `creator` 칸 | 보낸 문자를 만든 앱 | [문자](../../02-artifacts/communications/messages/index.md) |
| 3 | 알림 기록 | 문자 도착 알림의 제목과 내용 | [알림 기록](../../02-artifacts/app-usage/notification-history.md) |
| 4 | 브라우저 기록 | 문자 속 링크를 연 시각과 이어서 연 페이지 | [크롬](../../02-artifacts/browsers/chrome/index.md), [삼성 인터넷](../../02-artifacts/browsers/samsung-internet.md) |
| 5 | 미디어 저장소의 내려받은 항목 | 링크를 거쳐 받은 파일과 받은 주소 | [악성 앱은 어디서 들어왔나](initial-access.md) |
| 6 | 스팸·사기 탐지 관련 설정 키 | 관련 기능의 설정이 있는지 | [설정 값](../../02-artifacts/system-account/settings.md) |

## 분석 흐름

1. **문제의 문자를 찾습니다.** 문자 저장소의 내용 URI 는 `content://sms` 이고, 그 아래에 `content://sms/inbox`, `/sent`, `/draft`, `/outbox`, `/conversations` 가 있습니다 [2]. 문자 한 건에는 `type`, `thread_id`, `address`(상대방 주소), `date`, `date_sent`, `read`, `seen`, `status`, `subject`, `body`, `person`, `protocol`, `reply_path_present`, `service_center`, `locked`, `sub_id`, `error_code`, `creator` 칸이 있습니다 [2]. 본문(`body`)에서 링크가 든 문자를 찾고, 상대 주소와 받은 시각, 읽음(`read`)과 확인(`seen`) 값을 적습니다. `service_center` 에는 메시지가 거친 SMS 센터가 있을 때 적힙니다 [2].

   `type` 값은 아래와 같습니다 [2].

   | 값 | 뜻 |
   |---|---|
   | 0 | ALL |
   | 1 | INBOX(받은 문자) |
   | 2 | SENT(보낸 문자) |
   | 3 | DRAFT(임시 저장) |
   | 4 | OUTBOX(보낼 문자) |
   | 5 | FAILED(보내기 실패) |
   | 6 | QUEUED(보내기 대기) |

2. **누가 문자를 받아 적었는지 가립니다.** `SMS_DELIVER` 방송(`android.provider.Telephony.SMS_DELIVER`)은 기본 문자 앱에만 가고, 그 앱이 메시지를 저장소에 쓰고 사용자에게 알립니다 [2]. `SMS_RECEIVED` 방송은 등록한 모든 수신자에게 가고 `RECEIVE_SMS` 권한이 필요하지만, 이 수신자들은 메시지를 쓰거나 알리지 않습니다 [2]. 기본 문자 앱이 아닌 앱도 이 권한으로 들어오는 문자를 받아 볼 수 있다는 뜻으로 읽을 수 있어서, 수상한 앱이 있으면 그 앱이 `RECEIVE_SMS` 권한을 받았는지 [앱 샌드박스와 권한](../../01-foundations/security-model/sandbox-permissions.md) 기준으로 확인합니다.

3. **피해자 폰에서 나간 문자를 봅니다.** `creator` 는 보낸 메시지를 만든 쪽이고 보통 보낸 앱의 패키지 이름이며, 문자 저장소가 채우는 읽기 전용 칸이라서 앱이 바꿀 수 없습니다 [2]. `type` 이 2(SENT)나 4·5·6 인 행에서 `creator` 가 기본 문자 앱이 아니면 그 앱이 문자를 보냈거나 보내려 한 기록입니다. 같은 본문이 여러 주소로 짧은 간격에 나갔는지, 유료 문자로 보이는 번호로 나갔는지를 함께 적습니다. 패키지 이름을 앱으로 풀어 보는 법은 [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md) 에 있습니다.

4. **문자가 지워졌으면 알림에서 찾습니다.** 관찰 기기의 `dumpsys notification` 알림 기록에는 `pkg=` 와 함께 `extras` 안에 `android.title`, `android.text` 칸이 있었습니다. 문자 앱이 띄운 알림에서 보낸 사람과 본문 일부를 볼 수 있는 모양이지만, 관찰 기기에서는 값이 가려져 있어 실제로 문자 알림이 찍혔는지는 관찰하지 않았습니다. 지난 알림을 저장하는 기록은 [알림 기록](../../02-artifacts/app-usage/notification-history.md) 에서 봅니다.

5. **링크를 열었는지 봅니다.** 문자를 받은 시각 뒤에 본문 속 주소나 그 주소가 넘겨준 페이지가 브라우저 기록에 있는지 찾습니다. 브라우저마다 기록 위치가 달라 [크롬](../../02-artifacts/browsers/chrome/index.md) 과 [삼성 인터넷](../../02-artifacts/browsers/samsung-internet.md), [그 밖의 브라우저](../../02-artifacts/browsers/other-browsers.md) 페이지를 따르고, 웹 기록을 시간순으로 세우는 법은 [웹 사용 행위 재구성](../activity/web-activity.md) 에 있습니다.

6. **파일을 받았는지 봅니다.** 링크를 거쳐 받은 파일은 미디어 저장소의 받은 주소, 리퍼러, 파일을 넣은 앱, 추가된 시각으로 찾고, 칸 이름과 단위는 [악성 앱은 어디서 들어왔나](initial-access.md) 의 4단계에 있습니다. 받은 파일이 APK 이고 설치까지 이어졌다면 같은 페이지의 흐름으로 설치자와 설치 시각을 읽습니다.

7. **보호 기능 설정을 적어 둡니다.** 관찰 기기의 settings global 키 목록에는 `spam_call_enable`, `spam_call_mute_first_ring`, `kt_scam_detection_is_supported`, `do_not_show_scam_detection_badge`, `do_not_show_caller_id_spam_protection_badge`, `sms_short_codes_content_url`, `sms_short_codes_metadata_url` 이 있었습니다. 각 키의 뜻은 확인하지 못했고, `kt_` 로 시작하는 키가 국내 통신사와 관련된 것인지도 이름에서 짐작할 뿐입니다. 삼성 자동 차단(Auto Blocker)의 최대 제한에는 첨부 자동 내려받기와 하이퍼링크·미리보기를 막는 항목이 있고 [3], 기능 전체 설명은 [악성 앱은 어디서 들어왔나](initial-access.md) 에 있습니다.

8. **한 줄로 정리합니다.** 문자를 받은 시각, 링크를 연 시각, 파일을 받은 시각, 설치 시각, 나간 문자의 시각을 한 시간 축에 놓고, 어느 칸이 비어 있는지 함께 남깁니다. 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

> 그림 자리: "문자 받음(address·date) → 링크 열람(브라우저 기록) → 파일 받음(download_uri) → 설치(installer) → 문자 발송(creator)" 을 시간 축에 놓고, 단계마다 근거 칸 이름을 적은 그림

## 흔한 오판

**문자 저장소에 없으니 문자를 받지 않았다고 보는 오판**이 흔합니다. 사용자가 지웠을 수 있고, `SMS_RECEIVED` 로 문자를 받은 기본 문자 앱이 아닌 앱은 메시지를 저장소에 쓰지 않습니다 [2].

**`date` 와 `date_sent` 를 섞어 쓰는 실수**도 있습니다. 앞은 받은 시각, 뒤는 보낸 시각이라서 [2] 두 값의 차이만큼 보고서의 시각이 달라집니다.

**링크가 든 문자가 있으니 링크를 눌렀다고 적는 것**은 지나칩니다. 읽음 값이 있어도 링크를 열었는지는 브라우저 기록 같은 다른 기록으로 따로 확인합니다.

**`creator` 가 기본 문자 앱이면 사람이 직접 보냈다고 단정하는 것**도 조심합니다. `creator` 는 문자를 만든 앱을 가리킬 뿐이고 [2], 누가 그 앱을 조작했는지는 담지 않습니다.

## 보고서 문장 예

| 쓰지 않을 문장 | 쓸 문장 |
|---|---|
| 피해자는 스미싱 문자를 받고 링크를 눌러 악성 앱을 깔았다. | 문자 저장소에 ○○일 ○○:○○(UTC ○○:○○)에 ○○ 번호에서 받은 문자(`type`=1)가 있고, 본문에 ○○ 주소가 들어 있습니다. 같은 날 ○○:○○에 이 주소를 연 브라우저 기록이 있습니다. |
| 악성 앱이 지인들에게 문자를 뿌렸다. | ○○일 ○○:○○부터 ○○:○○까지 보낸 문자(`type`=2) ○○건의 `creator` 칸에 ○○ 앱의 패키지 이름이 기록되어 있습니다. |
| 피해자는 그 문자를 읽지 않았다. | 해당 문자의 `read` 값은 ○○, `seen` 값은 ○○로 기록되어 있습니다. |

보고서 전체의 틀은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 아티팩트 본문: [문자 (SMS·MMS·RCS)](../../02-artifacts/communications/messages/index.md), [알림 기록](../../02-artifacts/app-usage/notification-history.md), [크롬](../../02-artifacts/browsers/chrome/index.md), [삼성 인터넷](../../02-artifacts/browsers/samsung-internet.md), [미디어 저장소](../../02-artifacts/media/mediastore/index.md), [설정 값](../../02-artifacts/system-account/settings.md)
- 값 해석: [시각 값](../../01-foundations/value-decoding/time-values.md), [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md)
- 이어지는 시나리오: [악성 앱은 어디서 들어왔나](initial-access.md), [계정 탈취 흔적](account-takeover.md), [누구와 연락을 주고받았나](../activity/communication.md), [웹 사용 행위 재구성](../activity/web-activity.md)
- 기법: [악성 앱 흔적 분석](../../03-techniques/analysis/malicious-app-triage/index.md), [타임라인 작성](../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. Malware categories — Play Protect (Google for Developers) — https://developers.google.com/android/play-protect/phacategories
2. Telephony.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/provider/Telephony.java
3. Samsung Auto Blocker — Samsung Knox Documentation (2025-03-07 수정) — https://docs.samsungknox.com/admin/fundamentals/whitepaper/samsung-knox-mobile-security/system-security/samsung-auto-blocker/
