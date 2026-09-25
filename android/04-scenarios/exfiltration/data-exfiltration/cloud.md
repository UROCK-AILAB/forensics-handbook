---
title: "클라우드로"
parent: "자료를 밖으로 보냈나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 1710
---

# 클라우드로 (Cloud)

클라우드 저장소 앱이나 자동 백업으로 자료가 기기 밖으로 나갔는지 확인하는 순서를 정리합니다. 클라우드 앱은 올린 파일 목록을 앱 DB 에 캐시로 두는 경우가 있지만, 이번에는 Google Drive 한 가지만 구조를 확인했고 그마저도 최근 기기에서 채워지는지는 확인하지 못했습니다. 그래서 이 페이지는 앱 DB 와 함께 계정·동기화·백업 설정 값을 묶어 보는 흐름으로 씁니다. 유출 경로 전체의 길잡이는 [자료를 밖으로 보냈나 (Data Exfiltration)](index.md) 허브에 있습니다.

## 조사 질문

문제의 파일이 이 기기에서 클라우드 저장소로 올라갔는지, 올라갔다면 어느 계정의 어느 서비스로 언제 올라갔는지 묻습니다. 사용자가 직접 올린 경우와 사진 자동 백업처럼 설정에 따라 저절로 올라간 경우를 나눠야 하는데, 기기 쪽 기록만으로는 이 둘을 가르기 어려운 경우가 많습니다.

## 먼저 확인할 것

어떤 클라우드 계정이 기기에 붙어 있었는지부터 봅니다. `dumpsys account` 의 계정 목록과 계정 추가·삭제 기록(Accounts History)은 허브에서 요약하고, 구조는 [계정 (Accounts)](../../../02-artifacts/system-account/accounts/index.md) 페이지에 있습니다. 조사 기간 전후로 클라우드 계정이 붙었다가 떨어졌다면 그 시각이 이후 분석의 기준점이 됩니다.

다음으로 클라우드 앱이 설치돼 있었는지를 [설치된 앱 (packages.xml)](../../../02-artifacts/app-usage/packages/index.md)에서, 조사 기간에 그 앱을 앞에 띄웠는지를 [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md)에서 확인합니다. 앱 DB 는 앱 데이터 폴더 안에 있어서 수집본에 그 폴더가 들어 있는지도 먼저 봅니다([앱 데이터 폴더 구조 (/data/data·/data/user)](../../../01-foundations/storage/app-data-layout.md)). 시각은 유닉스 밀리초가 많으니 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../../01-foundations/value-decoding/time-values.md)과 기기 시간대를 함께 봅니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 계정 목록과 변경 기록 | 어떤 클라우드 계정이 언제 붙고 떨어졌는지 | [계정 (Accounts)](../../../02-artifacts/system-account/accounts/index.md) |
| 2 | 설정 값(동기화·백업) | 동기화·백업이 켜져 있을 수 있는 설정 키 | [설정 값 (Settings Global·Secure·System)](../../../02-artifacts/system-account/settings.md) |
| 3 | 클라우드 앱 DB | 드라이브 항목의 제목·크기·MD5·시각 | [구글 드라이브 (Google Drive)](../../../02-artifacts/mail-cloud/google-drive.md) 등 |
| 4 | 앱 사용 기록 | 클라우드 앱을 언제 앞에 띄웠는지 | [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) |
| 5 | 계정 쪽 자료 | 서버에 남은 기록 | [클라우드 데이터 (Google Takeout 등)](../../../03-techniques/acquisition/cloud-data.md) |

## Google Drive 의 항목 목록

Google Drive 앱의 DB 는 ALEAPP 가 `*/com.google.android.apps.docs/databases/DocList.db*` 패턴으로 찾고, 그 안의 `EntryView` 에서 항목 목록을 읽습니다 [2]. 앱 전체 구조는 [구글 드라이브 (Google Drive)](../../../02-artifacts/mail-cloud/google-drive.md) 페이지에 있고, 유출 조사에 쓰는 칸은 다음과 같습니다.

| 칸 | 담긴 것 |
|---|---|
| `title` | 항목 이름 |
| `kind` | 항목 종류 |
| `size` | 크기 |
| `md5Checksum` | 파일의 MD5 |
| `owner` | 소유자 |
| `creationTime`, `lastModifiedTime`, `lastOpenedTime` | 만든·고친·연 시각(유닉스 밀리초, 0 이면 비어 있음) |
| `lastModifierAccountAlias`, `lastModifierAccountName` | 마지막으로 고친 계정 |
| `shareableUri`, `htmlUri` | 항목 주소 |

`md5Checksum` 은 기기 안에 남은 파일의 MD5 와 맞춰 볼 수 있는 칸입니다 [2]. 문제의 파일과 MD5 가 같은 항목이 드라이브 목록에 있다면 같은 내용의 파일이 그 계정의 드라이브에 있었다고 말할 수 있고, 제목이 바뀌었어도 이 대조는 성립합니다. 다만 이 칸들은 드라이브 항목의 속성이라서, 그 항목을 이 기기에서 올렸는지 다른 기기에서 올렸는지는 모듈 설명에 나오지 않습니다.

이 모듈에는 주의할 점이 있습니다. ALEAPP 시험 이미지 10개(Android 10~16, 삼성 기기 포함)에서 모두 0행이 나왔고, 모듈은 2020-12-21 뒤로 갱신되지 않았습니다 [2]. 요즘 Drive 앱에서 이 표가 채워지는지는 확인하지 못했으니, 0행이 나와도 드라이브를 쓰지 않았다는 결론으로 가지 않습니다.

## 다른 클라우드 서비스

ALEAPP 에는 googlePhotos.py, androidDropbox.py, dropbox.py, microsoft_onedrive.py, mega.py, megaCloud.py, mega_transfers.py, ProtonDrive.py, pikpakCloudlist.py, syncthing.py 모듈이 있습니다 [1]. 이번에 모듈 안의 표·칸은 열어 보지 않았고, 앱별 구조는 [구글 포토 (Google Photos)](../../../02-artifacts/media/google-photos.md), [삼성 클라우드와 원드라이브 (Samsung Cloud·OneDrive)](../../../02-artifacts/mail-cloud/samsung-cloud-onedrive.md), [네이버 MYBOX (MYBOX)](../../../02-artifacts/mail-cloud/mybox.md) 페이지에서 다룹니다. 모듈 이름에 transfers 가 들어간 것처럼 전송 기록을 따로 두는 앱이 있을 수 있어서, 앱마다 올리기 대기열이나 전송 기록 표가 있는지 찾아봅니다.

사진 자동 백업(Google 포토, 삼성 갤러리 동기화)의 업로드 기록이 어디에 남는지는 이번에 확인하지 못했습니다. 사진이 올라갔는지는 [구글 포토 (Google Photos)](../../../02-artifacts/media/google-photos.md)와 [삼성 갤러리 (Samsung Gallery)](../../../02-artifacts/media/samsung-gallery.md) 페이지에서 따로 봅니다.

## 동기화·백업 설정 키

실제 폰의 설정 표에서 다음 키 이름을 확인했습니다 (확인 범위: Android 16, One UI 8.5). 값은 가려져 있었고 각 키의 뜻과 시각 기준도 확인하지 못해서, 이 표는 "어느 키를 볼 수 있는지" 까지만 알려 줍니다.

| 표 | 키 |
|---|---|
| secure | `backup_enabled`, `backup_transport`, `backup_auto_restore`, `backup_manager_constants` |
| secure | `backup_enabled:com.android.calllogbackup`, `backup_enabled:com.android.providers.telephony` |
| secure | `mms_backup_enabled`, `mms_backup_in_progress`, `mms_backup_last_completed` |
| secure | `appprotection_permission_scloud_function_usage`, `appprotection_permission_scloud_usage_user_decided` |
| secure | `ltw_clipboard_sync_state`, `samsungflow_clipboard_sync_state` |
| global | `master_sync_status`, `synced_account_name` |

이름에 scloud 가 들어간 키는 삼성 클라우드와 관련이 있어 보이지만 어떤 기능인지는 확인하지 못했습니다. `ltw_clipboard_sync_state` 와 `samsungflow_clipboard_sync_state` 는 이름으로 보아 클립보드 동기화 상태 키인데, 이 역시 어떤 기능인지는 확인하지 못했습니다. 설정 값을 읽는 방법은 [설정 값 (Settings Global·Secure·System)](../../../02-artifacts/system-account/settings.md) 페이지에 있습니다.

## 분석 흐름

1. 계정 목록과 계정 변경 기록으로 조사 기간에 붙어 있던 클라우드 계정을 적습니다.
2. 설치된 앱과 usagestats 로 그 계정을 쓰는 클라우드 앱과 사용 시각대를 좁힙니다.
3. 클라우드 앱 DB 에서 항목 이름·크기·MD5·시각을 뽑아, 문제의 파일과 MD5 로 맞춰 봅니다.
4. 동기화·백업 설정 키를 적어 두고, 자동으로 올라갔을 가능성을 따로 표시합니다.
5. 기기 쪽 기록이 비어 있거나 부족하면, 적법한 절차로 계정 쪽 자료를 받아 서버의 업로드 기록과 맞춥니다.

## 흔한 오판

드라이브 목록에 문제의 파일이 있다는 사실을 "이 기기에서 올렸다" 로 적지 않습니다. 같은 계정으로 로그인한 다른 기기나 웹에서 올린 항목도 목록에 함께 나올 수 있고, `lastModifierAccountName` 이 이 기기의 계정과 다르면 다른 사람이 고친 항목일 수 있습니다.

앱 DB 가 0행이라는 사실만으로 클라우드를 쓰지 않았다고 보지 않습니다. Drive 모듈처럼 최근 앱 판에서 표가 비어 있을 수 있습니다 [2].

사용자가 직접 올린 것과 자동 백업을 섞지 않습니다. 설정 키만으로는 켜져 있었는지 알기 어렵고, 켜져 있었다 해도 특정 파일이 올라갔다는 뜻은 아닙니다.

## 보고서 문장 예

- "Google Drive 앱의 `DocList.db` 에서 `md5Checksum` 이 문제의 파일 MD5 와 같은 항목이 확인되며, 이 항목의 `creationTime` 은 (현지 시각)입니다. 이 기록은 같은 내용의 파일이 해당 계정의 드라이브에 있었다는 뜻이며, 이 기기에서 올렸는지는 이 기록만으로 알 수 없습니다."
- "조사 기간에 이 기기에는 (계정 종류)의 계정이 등록돼 있었고, 계정 변경 기록에 (시각) 추가 기록이 있습니다."

## 함께 볼 페이지

- [클라우드 데이터 (Google Takeout 등)](../../../03-techniques/acquisition/cloud-data.md)
- [구글 백업 (Google Backup)](../../../02-artifacts/mail-cloud/google-backup.md)
- [계정 탈취 흔적 (Account Takeover)](../../incident/account-takeover.md)
- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)
- 같은 허브의 다른 경로: [메신저로 (Messenger)](messenger.md), [메일로 (Email)](email.md), [PC 연결로 (USB·PC)](usb-pc.md), [근거리 공유로 (Quick Share·Bluetooth)](nearby-share.md)

## 참고 문헌

1. ALEAPP scripts/artifacts 폴더 목록 — GitHub API, https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
2. DocList.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/DocList.py
