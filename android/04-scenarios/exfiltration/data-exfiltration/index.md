---
title: "자료를 밖으로 보냈나"
parent: "시나리오 · 정보 유출"
nav_order: 1690
has_children: true
has_toc: false
---

# 자료를 밖으로 보냈나 (Data Exfiltration)

기기 안의 파일이나 대화가 메신저·클라우드·메일·PC 연결·근거리 공유 가운데 어느 길로 밖에 나갔는지를 경로별 흔적으로 확인하는 조사 묶음입니다.

## 왜 중요한가

유출 조사는 "보냈다"는 한 마디를 확인하는 일이지만, Android 에는 이 한 마디를 한곳에 모아 적는 기록이 없습니다. 보내는 길마다 흔적이 남는 자리가 다르고, 크게 네 갈래로 나눠 볼 수 있습니다. 첫째는 메신저·메일·클라우드 앱이 자기 폴더에 두는 데이터베이스이고, 둘째는 시스템 설정 값, 셋째는 사용 기록(usagestats)이나 dumpsys 처럼 시스템 서비스가 남기는 기록, 넷째는 ADB 인증 키나 블루투스 설정 파일 같은 연결 기록입니다. 이 네 갈래는 이 핸드북이 여러 자료를 묶어 정리한 분류이고, 이렇게 나눈 공식 문서는 없습니다.

흔적마다 증명하는 범위도 다릅니다. 앱 사용 기록은 그 앱을 언제 앞에 띄웠는지까지만 알려 주고 무엇을 보냈는지는 알려 주지 않습니다. ADB 인증 기록 한 줄은 그 PC 를 인증해 두었다는 뜻이지 파일이 옮겨졌다는 뜻이 아니고 [2], 블루투스·Nearby 캐시의 한 줄도 기기를 짝지었거나 주변에서 발견했다는 기록일 뿐 파일 전송 기록이 아닙니다 [3][4]. 그래서 보고서에는 "자료를 유출했다" 가 아니라 "이 시각에 이 앱에서 보낸 것으로 표시된 메시지와 첨부가 있다" 처럼 기록이 말하는 만큼만 씁니다.

앱 폴더(/data/data 아래)의 데이터베이스는 루팅이나 전체 추출 없이 adb 일반 권한으로 읽을 수 없어서, 어떤 방법으로 증거를 확보했는지에 따라 볼 수 있는 흔적이 달라집니다. 확보 방법은 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md)에서, 폴더 구조는 [앱 데이터 폴더 구조](../../../01-foundations/storage/app-data-layout.md)에서 다룹니다.

## 한눈에 보기

아래 경로는 공개 도구 ALEAPP 가 파일을 찾을 때 쓰는 패턴(`*/...`)이라서 앞부분이 `*` 로 줄어 있습니다. "시험 이미지"는 ALEAPP 모듈이 시험한 공개 이미지를 말하고, 그 버전·제조사에서 반드시 동작한다는 보증은 아닙니다.

| 유출 길 | 위치 | Android 버전·제조사 | 알려 주는 것 |
|---|---|---|---|
| 메신저 | 왓츠앱 `*/com.whatsapp/databases/msgstore.db*` [5] | 앱 버전에 따라 요즘 표 `message`, 예전 표 `messages` 로 구조가 다름. 시험 이미지에 Android 14 포함 [5] | 보낸 메시지(`from_me`=1)와 첨부 파일 경로·크기, 대화 상대 |
| 클라우드 | 구글 드라이브 `*/com.google.android.apps.docs/databases/DocList.db*` [7] | 시험 이미지 10개(Android 10~16, 삼성 포함) 모두 0행이라 최근 앱에서 채워지는지는 검체에서 확인 [7] | 파일 제목·크기·MD5·공유 주소, 만든·고친·연 시각 |
| 메일 | 지메일 `*/com.google.android.gm/databases/bigTopDataDB.*` [6] | 시험 이미지에 삼성 Galaxy S10(Android 10) 포함 [6] | 메일과 첨부(본문·머리는 압축한 protobuf) |
| PC 연결 | ADB 인증 기록 `*/misc/adb/adb_temp_keys.xml` [2] | 요즘은 ABX, 예전은 일반 XML. 바뀐 버전은 공개 자료 없음 [2] | 인증해 둔 PC 의 이름과 마지막 연결 시각 |
| PC 연결 | 휴대폰과 연결 `*/com.microsoft.appmanager/databases/eventstore*` [9] | 시험 이미지 삼성 Android 13·14 에서 행이 나옴 [9] | 연결된 계정, 내용 접근 이벤트 |
| PC 연결 | 삼성 내 파일 `*/com.sec.android.app.myfiles/databases/OperationHistory.db*` [8] | 경로 풀이가 Android 10~12 에서만 맞고 13·14 값은 풀지 못함 [8] | 파일 복사·이동 같은 작업 기록 |
| 근거리 공유 | 블루투스 `*/bt_config.conf` [3] | 전체 경로의 버전별 차이는 공개 자료 없음 | 짝지은 기기의 MAC 주소·이름·시각(유닉스 초) |
| 근거리 공유 | Nearby 캐시 `*/nearby-fast-pair/...`, `*/nearby-discovery/...`(LevelDB) [4] | Google Play 서비스 캐시 | 주변에서 발견한 액세서리·기기(전송 기록 아님) |
| 공통 | `dumpsys account` 의 Accounts History | | 계정을 붙이고 뗀 기록(`action_account_add`, `action_account_remove` 등) |
| 공통 | `dumpsys usagestats` | | 앱을 앞에 띄우고 내린 순서(`ACTIVITY_RESUMED` 등) |
| 공통 | 설정 값(global·secure·system) | 삼성 전용 키가 섞여 있음 | 기능이 켜졌는지(`adb_enabled`, `quickshare_enabled`, `backup_enabled` 등) |

카카오톡 전용 ALEAPP 모듈은 목록에 없고, 삼성 이메일·Quick Share 전송 기록·블루투스 파일 전송(OPP)을 이름으로 내건 모듈도 목록에서 보이지 않습니다 [1]. 이 앱들은 공개 도구의 결과만으로 판단하지 말고 [앱 데이터 분석](../../../03-techniques/analysis/app-data-analysis/index.md)처럼 데이터를 직접 열어 봅니다.

/sdcard 최상위에는 Download·Documents·DCIM 같은 표준 폴더가 있고, 받은 파일과 보낼 파일은 Download 폴더에 모이기 쉽습니다. 공용 저장 공간의 구조는 [공용 저장 공간](../../../01-foundations/storage/shared-storage.md)에서 다룹니다.

## 읽는 순서

유출 경로를 모를 때는 공통 흔적으로 범위를 먼저 좁힙니다. 계정 기록으로 클라우드·메일 계정이 언제 붙었는지 보고, 앱 사용 기록으로 사건 시각 전후에 어떤 앱을 띄웠는지 본 다음, 해당 경로의 하위 페이지로 들어갑니다.

1. [메신저로 (Messenger)](messenger.md) — 메신저 데이터베이스에서 보낸 메시지와 첨부를 가려내고 알림 기록과 맞춰 봅니다.
2. [클라우드로 (Cloud)](cloud.md) — 클라우드 앱의 파일 목록, 백업·동기화 설정, 계정 연결 기록을 봅니다.
3. [메일로 (Email)](email.md) — 메일 앱 데이터베이스의 메일·첨부와 다운로드 기록을 봅니다.
4. [PC 연결로 (USB·PC)](usb-pc.md) — ADB 인증 기록, 휴대폰과 연결, USB·DeX 관련 설정, 내 파일 작업 기록을 봅니다.
5. [근거리 공유로 (Quick Share·Bluetooth)](nearby-share.md) — 블루투스 짝지음 기록, Quick Share 설정, Nearby 캐시가 알려 주는 것과 알려 주지 못하는 것을 나눠 봅니다.

## 함께 볼 페이지

- [계정 (Accounts)](../../../02-artifacts/system-account/accounts/index.md)
- [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md)
- [설정 값 (Settings Global·Secure·System)](../../../02-artifacts/system-account/settings.md)
- [dumpsys 출력 (dumpsys)](../../../02-artifacts/logs/dumpsys.md)
- [알림 기록 (Notification History)](../../../02-artifacts/app-usage/notification-history.md)
- [설치된 앱 (packages.xml)](../../../02-artifacts/app-usage/packages/index.md)
- [왓츠앱 (WhatsApp)](../../../02-artifacts/messengers/whatsapp.md) · [지메일 (Gmail)](../../../02-artifacts/mail-cloud/gmail.md) · [구글 드라이브 (Google Drive)](../../../02-artifacts/mail-cloud/google-drive.md)
- [블루투스 장치 (Bluetooth)](../../../02-artifacts/network/bluetooth.md) · [파일 공유 (Quick Share·Nearby Share)](../../../02-artifacts/network/quick-share.md) · [USB 연결 기록 (USB)](../../../02-artifacts/network/usb.md)
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)
- [누구와 연락을 주고받았나 (Communication)](../../activity/communication.md)
- [증거를 없애려 했나 (Anti-Forensics)](../../activity/anti-forensics/index.md)
- [포렌식 보고서 (Forensic Report)](../../../03-techniques/reporting/forensic-report.md)

## 참고 문헌

1. ALEAPP scripts/artifacts 폴더 목록 — GitHub API, https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
2. adbAuthorizations.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/adbAuthorizations.py
3. bluetoothConnections.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/bluetoothConnections.py
4. nearbyDevices.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/nearbyDevices.py
5. WhatsApp.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/WhatsApp.py
6. gmailEmails.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/gmailEmails.py
7. DocList.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/DocList.py
8. smyfilesOpHistory.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/smyfilesOpHistory.py
9. phoneLink.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/phoneLink.py
