---
title: "클라우드 데이터"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 1360
---

# 클라우드 데이터 (Google Takeout 등)

Android 기기와 이어진 계정의 서버 쪽 데이터를 어떻게 찾고 받는지 정리합니다. 기기에서 계정과 동기화 흔적을 읽어 대상을 정하는 부분, 계정 소유자가 Google Takeout 으로 받는 자료, Google 지도 타임라인처럼 기기와 서버 사이에 걸친 데이터를 다룹니다.

## 한 줄 요약

기기에 남은 계정·동기화·백업 흔적으로 어느 서비스에 데이터가 있을지 정하고, 서버 쪽 데이터는 계정 소유자의 내려받기(Google Takeout 등)나 기관 지침에 맞는 절차로 따로 얻습니다.

## 언제 쓰나

모바일 클라우드는 앱과 데이터를 기기 메모리가 아닌 인터넷 서버에 두는 방식이라서, 데이터가 지리적으로 여러 곳에 흩어져 있을 수 있습니다 [1]. 앱이 발전하면서 사용자도 자기 데이터가 클라우드에 있는지 기기에 있는지 알아채지 못하는 일이 많고 [1], 기기만 수집해서는 사건에 필요한 기록이 빠질 수 있습니다.

클라우드 데이터는 법과 규정 때문에 기기 데이터보다 얻기 어려울 수 있어서, NIST 는 수집과 분석을 기관의 클라우드 포렌식 지침에 따라 하라고 합니다 [1]. 클라우드 데이터의 흔적(브라우저 캐시 등) 이 주변 장비에 남아 있을 수 있으니 그쪽도 놓치지 않습니다 [1]. NIST 는 2014년 기준으로 이 분야를 새로 생겨나는 분야라고 적었습니다 [1]. 조사 전체의 순서는 [조사 절차](investigation-process.md) 페이지에 있습니다.

## 절차

1. **기기에서 계정 목록을 적습니다.** 관찰한 폰의 `dumpsys account` 출력에는 계정마다 `Account {name=..., type=...}` 줄이 있고, 그 아래에 `Accounts History` 표가 있었습니다. 표의 칸과 관찰한 `Action_Type` 값은 아래와 같았습니다.

   ```
   AccountId, Action_Type, timestamp, UID, TableName, Key

   Action_Type 값:
   action_account_add
   action_account_remove
   action_called_account_add
   action_called_account_remove
   action_authenticator_remove
   action_clear_password
   ```

   어떤 클라우드 계정이 기기에 붙어 있고 언제 추가·삭제됐는지 볼 출발점이지만, 이 표를 얼마나 오래 보관하는지와 `timestamp` 가 어느 시간대 기준인지는 확인하지 못했습니다. 계정 흔적 전반은 [계정](../../02-artifacts/system-account/accounts/index.md) 페이지를 봅니다.
2. **동기화·백업 설정을 적습니다.** 관찰한 폰의 설정에는 동기화, 삼성 클라우드, Smart Switch, 위치와 이름이 닿는 키가 아래처럼 있었습니다. 값의 뜻은 확인하지 못했으니 키가 있다는 사실과 수집 당시 값까지만 기록합니다. 백업 관련 키는 [백업으로 수집](mobile-acquisition/backups.md) 페이지에 따로 정리했습니다.

   | 어디서 | 키 이름 | 이름이 닿는 기능 |
   |---|---|---|
   | settings global | `master_sync_status`, `synced_account_name` | 동기화 |
   | settings system | `sync_disabled_accounts_with_hash`, `contact_default_account` | 동기화, 연락처 저장 계정 |
   | settings secure | `appprotection_permission_scloud_function_usage`, `appprotection_permission_scloud_usage_user_decided` | 삼성 클라우드로 보이나 확인하지 못함 |
   | settings global | `smartswitch_bnr_count`, `smartswitch_transfer_completed` | Smart Switch |
   | settings secure | `location_mode`, `gs_location_state` | 위치 |

   공용 저장 공간의 `/sdcard/Android/media` 아래에는 `com.google.android.gms` 앱 폴더가 있었지만, 안에 무엇이 있는지는 관찰하지 않았습니다. 설정 값을 읽는 법은 [설정 값](../../02-artifacts/system-account/settings.md) 페이지에 있습니다.
3. **어느 서비스에 무엇이 있을지 정리합니다.** 1·2단계의 계정과 설정을 바탕으로 메일, 사진, 위치, 백업처럼 서버에 있을 법한 데이터를 서비스별로 적습니다. 기기에서 본 계정 목록으로 대상을 정하고 서버 데이터는 따로 얻는다는 흐름은, NIST 의 "기관 지침을 따른다" [1] 와 관찰을 묶은 해석입니다.
4. **서버 쪽 데이터를 얻습니다.** 계정 소유자가 직접 내려받는 Google Takeout 이 한 방법이고, 그 밖의 법적 절차는 기관 지침을 따릅니다 [1]. 구체적인 법적 절차는 이 페이지에서 다루지 않습니다.
5. **받은 묶음을 보존합니다.** 내려받은 파일은 곧바로 해시를 계산해 두고, 분할된 파일은 모두 함께 보관합니다. 해시 계산과 기록은 [결과물 형식과 해시](mobile-acquisition/formats-hash.md) 페이지를 봅니다.
6. **기기 데이터와 맞춰 봅니다.** 서버 쪽 기록과 기기 쪽 기록을 한 시간축에 올리는 법은 [타임라인 작성](../analysis/timeline/index.md) 페이지에 있습니다.

## Google Takeout 으로 받는 자료

Google Takeout(Google 데이터 내려받기) 으로는 이메일, 문서, 캘린더, 사진, YouTube 동영상, "등록 및 계정 활동" 같은 자료를 내보낼 수 있습니다 [2]. 묶음을 만드는 데 몇 분에서 며칠이 걸리지만 대부분은 요청한 날 링크를 받고, 묶음이 준비되면 위치 링크를 이메일로 알려 줍니다 [2]. 한 번만 만들 수도 있고, 1년 동안 2개월마다 자동으로 만들게 할 수도 있습니다 [2].

내보내기를 요청할 때 고르는 항목은 아래와 같습니다 [2].

| 항목 | 고를 수 있는 것 |
|---|---|
| 전달 방식 | 이메일로 내려받기 링크 받기, Google Drive 에 넣기(Drive 저장 용량을 씀), Dropbox, OneDrive·Box 에 올리기 |
| 압축 형식 | zip 또는 tgz (tgz 는 Windows 에서 별도 소프트웨어가 필요할 수 있음) |
| 분할 크기 | 1GB, 2GB, 4GB, 10GB, 50GB 중 하나이고, 이보다 크면 여러 파일로 나뉨 |
| 내려받기 제한 | 링크는 약 7일 뒤 만료되고, 한 묶음은 5번까지만 내려받을 수 있음 |

묶음 안의 파일 형식은 제품마다 다릅니다. 연락처는 vCard 로 나오고 그 밖에 CSV·JSON·HTML 이 쓰이며, Gmail 의 라벨은 메일마다 `X-Gmail-Labels` 머리에 남습니다 [2]. Google Workspace 관리자는 사용자가 어떤 제품의 데이터를 내려받을 수 있는지 정할 수 있습니다 [2]. 제품별 전체 형식 목록, 묶음 안의 폴더 구조와 파일 이름, 시각 값이 UTC 인지 같은 세부는 이 페이지에서 확인하지 않았으니, 받은 묶음마다 직접 확인합니다.

## Google 지도 타임라인

Google 지도 타임라인은 Google 계정에서 기본으로 꺼져 있고, 사용자가 동의해야 켜집니다 [3]. 타임라인 데이터는 기기에서 나오고, 컴퓨터용 지도에서는 타임라인을 쓸 수 없으며 휴대전화의 지도 앱이 있어야 합니다 [3]. 타임라인을 백업하면 지도 앱이 암호화된 사본을 Google 서버에 저장합니다 [3].

타임라인은 자동 삭제 설정에 따라, 또는 사용자가 지울 때까지 남습니다 [3]. 전체 타임라인은 "내 Google 활동" 에서 끄거나 지울 수 있고, 일부만 지우려면 휴대전화의 지도 앱을 씁니다 [3]. 검색 기록은 타임라인이 아니라 "웹 및 앱 활동" 설정이 관리합니다 [3].

데이터가 기기에서 나온다는 설명에 비추어 보면, 타임라인을 찾을 때는 서버보다 기기 쪽 수집을 먼저 챙겨야 한다는 해석이 나옵니다. 타임라인이 Takeout 묶음에 들어가는지와 기기에서 내보내는 파일 형식은 확인하지 못했습니다. 기기에 남는 타임라인 흔적은 [구글 위치 기록과 타임라인](../../02-artifacts/location/google-timeline.md) 페이지를 봅니다.

## 기기 백업과 Takeout 은 다른 자료

Google 계정 백업이 무엇을 담고 어디에 저장되는지는 [백업으로 수집](mobile-acquisition/backups.md) 과 [구글 백업](../../02-artifacts/mail-cloud/google-backup.md) 페이지에 있습니다. Android 9 이상에서 사용자가 백업을 켜고 화면 잠금을 설정했다면 앱 데이터 자동 백업을 화면 잠금 PIN·패턴·비밀번호로 종단간 암호화하니 [5], 기기 백업의 내용은 Takeout 처럼 계정 소유자가 내려받아 바로 읽을 수 있는 자료로 다루지 않는다는 해석이 나옵니다. 이를 직접 적은 출처는 확인하지 못했습니다.

Google 의 저장소(Takeout, Google 백업) 와 삼성의 저장소(삼성 클라우드, Smart Switch) 는 서로 다른 곳입니다. 삼성 계정 데이터를 열람하거나 내려받는 방법, 삼성 클라우드에 저장되는 항목은 이 페이지에서 확인하지 못했고, 기기 쪽 흔적은 [삼성 클라우드와 원드라이브](../../02-artifacts/mail-cloud/samsung-cloud-onedrive.md) 페이지를 봅니다.

| 버전·제조사 | 달라지는 점 | 자세히 |
|---|---|---|
| Android 9 이상 | 화면 잠금을 설정한 기기에서는 앱 데이터 자동 백업을 화면 잠금 PIN·패턴·비밀번호로 종단간 암호화합니다 [5] | [백업으로 수집](mobile-acquisition/backups.md) |
| Android 11 이하 / 12 이상 | 앱의 백업 규칙이 `fullBackupContent` 에서 `dataExtractionRules` 로 바뀌고, 12 이상에서는 클라우드 백업(cloud-backup) 과 기기 간 이전(device-transfer) 규칙을 따로 정합니다 [5] | [백업으로 수집](mobile-acquisition/backups.md) |
| 삼성 One UI | Google 과 따로 삼성 클라우드·Smart Switch 저장소가 있고, 관찰한 폰에 Smart Switch 이름의 설정 키가 있었습니다 | [삼성 클라우드와 원드라이브](../../02-artifacts/mail-cloud/samsung-cloud-onedrive.md) |

## 도구

Takeout 묶음은 zip 이나 tgz 로 받고, 풀어 낸 파일은 제품마다 형식(vCard, CSV, JSON, HTML 등) 이 달라 형식에 맞는 도구로 봅니다 [2]. 공개 도구의 예로 RLEAPP(Returns Logs Events And Protobuf Parser) 가 있고, 아래처럼 입력 형식과 경로를 주어 실행하며 GUI 는 `rleappGUI.py` 입니다 [4].

```
python rleapp.py -t <zip | tar | fs | gz | raw> -i <입력 경로> -o <보고서 출력 경로>
```

이름의 "Returns" 는 서비스 제공자가 내준 자료를 뜻하는 것으로 보이지만, README 에 Google Takeout 을 지원한다는 설명은 없었습니다 [4]. 쓰기 전에 받은 묶음을 실제로 읽는지 [도구 검증](../reporting/tool-validation.md) 으로 확인합니다.

## 함정과 한계

Takeout 묶음이 준비되면 계정으로 이메일 알림이 가니 [2], 내려받기 자체가 계정 소유자 쪽에 알림 흔적을 남긴다고 해석할 수 있습니다. 이 요청이 계정의 보안 활동 기록에도 남는지는 확인하지 못했습니다.

내려받기 링크는 약 7일 뒤 만료되고 한 묶음은 5번까지만 받을 수 있어서 [2], 받는 즉시 해시를 떠서 보존하지 않으면 같은 묶음을 다시 얻지 못할 수 있습니다. 고른 분할 크기보다 묶음이 크면 여러 파일로 나뉘니 [2], 나뉜 파일을 모두 받아 함께 보관합니다.

묶음에 어떤 제품이 없다고 해서 그 서비스를 쓰지 않았다고 볼 수는 없습니다. 요청할 때 고르지 않았을 수도 있고, Google Workspace 관리자가 그 제품의 내려받기를 막았을 수도 있습니다 [2]. 타임라인도 기본으로 꺼져 있고 자동 삭제나 사용자 삭제로 사라지니 [3], 타임라인이 없다는 사실만으로 위치 기록이 처음부터 없었다고 쓰지 않습니다.

기기의 `Accounts History` 표는 보관 기간과 시각 기준을 확인하지 못했으니, 계정 추가·삭제 시각을 쓸 때는 다른 흔적과 맞춰 본 뒤에 씁니다. 관찰한 설정 키도 이름만 보고 동기화나 백업이 켜져 있었다고 단정하지 않습니다.

## 결과를 어떻게 해석하나

기기의 계정 흔적은 "이 계정이 이 기기에 등록된 기록이 있다" 까지를 보여 줄 뿐이고, 그 계정의 주인이 누구인지나 그 사람이 기기를 썼는지는 따로 밝혀야 합니다. 계정을 누가 썼는지 따지는 흐름은 [계정 탈취 흔적](../../04-scenarios/incident/account-takeover.md) 과 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 페이지에 있습니다.

Takeout 묶음은 내보낸 시점에 계정에 남아 있던 데이터를 보여 줍니다. 그래서 보고서에는 "이 계정의 Takeout 묶음(내보낸 날짜 기록) 안에 이 기간의 메일이 이만큼 있다" 처럼 묶음과 내보낸 날짜를 함께 밝혀 쓰고, 묶음에 없는 데이터는 "묶음에 들어 있지 않았다" 까지만 씁니다. 받은 과정(누가 요청했고 언제 받았으며 해시가 무엇인지) 은 [포렌식 보고서](../reporting/forensic-report.md) 의 보조 자료로 붙입니다.

## 참고 문헌

1. NIST SP 800-101 Rev.1, Guidelines on Mobile Device Forensics (Ayers, Brothers, Jansen, 2014). https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-101r1.pdf
2. How to download your Google data — Google Account Help. https://support.google.com/accounts/answer/3024190?hl=en
3. Manage your Google Maps Timeline — Google Maps Help. https://support.google.com/maps/answer/6258979?hl=en
4. RLEAPP — abrignoni/RLEAPP (GitHub README). https://github.com/abrignoni/RLEAPP
5. Back up user data with Auto Backup — Android Developers. https://developer.android.com/identity/data/autobackup
