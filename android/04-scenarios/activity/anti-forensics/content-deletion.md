---
title: "메시지·사진 지우기"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 1670
---

# 메시지·사진 지우기 (Content Deletion)

앱은 그대로 두고 대화나 사진만 지운 흔적을 찾는 흐름을 정리합니다. 여기서는 "지운 행위가 있었는가, 언제쯤인가" 를 다루고, 지운 내용 자체를 되살리는 절차는 [지운 대화와 사진 찾기](../deleted-content.md) 시나리오에 맡깁니다. 소스로 확인한 동작은 현행 AOSP 기준(MediaProvider 의 main 가지, 2026-09-25 에 읽음)이고, 실제 폰에서 본 내용에는 확인 범위를 붙였습니다.

## 조사 질문

"특정 시점 전후로 사진·동영상이나 메시지를 한꺼번에 지웠는가, 지웠다면 언제쯤인가" 를 묻습니다. 사진은 Android 11 이상에서 휴지통을 거칠 수 있어서 지운 시점을 파일 이름에서 거꾸로 셈할 수 있고, 메시지는 앱마다 삭제 방식이 달라 알림처럼 바깥에 남은 기록과 맞춰 봐야 합니다.

## 먼저 확인할 것

- **Android 버전**: 미디어 휴지통은 Android 11(API 30)부터라서 [1] 그 이전 버전에서는 아래 파일 이름 규칙을 기대하지 않습니다.
- **제조사와 갤러리 앱**: 삼성 갤러리의 휴지통이 MediaStore 휴지통을 쓰는지, 자체 폴더를 쓰는지, 보관 기간이 며칠인지는 확인하지 못했고, 구글 포토 휴지통 기간도 확인하지 못했습니다. [삼성 갤러리](../../../02-artifacts/media/samsung-gallery.md) 와 [구글 포토](../../../02-artifacts/media/google-photos.md) 페이지를 함께 봅니다.
- **수집 시점**: 휴지통 항목은 정해진 기간이 지나면 영구 삭제되니 [1], 지운 뒤 얼마 만에 수집했는지를 적어 둡니다.
- **수집 범위**: 점(.)으로 시작하는 숨김 파일까지 수집했는지 확인합니다.

## 사진·동영상: MediaStore 휴지통

Android 11 이상에서 앱은 여러 미디어 파일을 골라 한꺼번에 휴지통으로 보내거나(`createTrashRequest()`) 휴지통을 거치지 않고 바로 영구 삭제하도록(`createDeleteRequest()`) 사용자에게 요청할 수 있습니다 [1]. 휴지통 항목에 대해 문서는 "Items in the trash are permanently deleted after a system-defined time period." 라고 적고 있고 [1], 제조사 기본 갤러리 앱은 확인 창 없이 `IS_TRASHED` 칸을 1로 바꿔 휴지통으로 보낼 수 있습니다 [1]. 또 Android 10 이상에서 파일을 쓰는 동안 `IS_PENDING` 을 1로 두면 그 앱만 파일을 볼 수 있습니다 [1].

AOSP MediaProvider 의 기본 보관 기간은 아래와 같습니다 [2].

| 상수 | 기본값 | 뜻 |
|---|---|---|
| DEFAULT_DURATION_TRASHED | 30일 | 휴지통 보관 기간 |
| DEFAULT_DURATION_PENDING | 7일 | 작성 중(pending) 파일 보관 기간 |
| DEFAULT_DURATION_EXTENDED | 7일 | 연장 기간 |

휴지통과 작성 중 파일은 디스크에서 이름이 바뀌고, 이름 규칙(PATTERN_EXPIRES_FILE)은 다음과 같습니다 [2].

```
.trashed-<만료시각>-<원래 이름>
.pending-<만료시각>-<원래 이름>
```

이름 속 만료 시각은 밀리초가 아닌 유닉스 초이고, 코드는 `(System.currentTimeMillis() + DEFAULT_DURATION_TRASHED) / 1000` 입니다 [2]. 그래서 기본값을 쓰는 기기라면 휴지통으로 보낸 시각은 만료 시각에서 30일을 뺀 값에 가깝습니다(해석). 제조사가 기간을 바꿨다면 이 셈은 맞지 않고, 만료 시각도 기기 벽시계로 만든 값이라서 기기 시각을 바꿔 둔 상태였다면 그만큼 어긋납니다. 이름이 점으로 시작하니 일반 파일 목록에서는 숨김 파일로 보입니다(해석).

소스에 나온 이름 예 `.trashed-1621147340-test.jpg` 로 셈해 보면 아래와 같습니다. 특정 검체가 아니라 소스 속 예시를 풀어 본 것입니다.

```
만료 시각   1621147340 (유닉스 초) = 2021-05-16 06:42:20 UTC
30일 빼기   1621147340 - 2592000   = 2021-04-16 06:42:20 UTC  ← 휴지통으로 보낸 무렵(기본값 기준 해석)
```

MediaStore 의 `DATE_EXPIRES` 칸 설명은 이번에 받은 문서에 없어서, DB 칸과 파일 이름을 서로 맞춰 보는 방법은 다루지 않습니다. MediaStore DB 의 구조는 [미디어 저장소 (MediaStore)](../../../02-artifacts/media/mediastore/index.md) 에 있습니다.

## 메시지·연락처

삼성 메시지 앱의 휴지통과 구글 메시지의 삭제 동작이 어디에 얼마 동안 남는지는 이번에 출처를 열지 않아 다루지 않습니다. 앱별 DB 구조는 [문자 (SMS·MMS·RCS)](../../../02-artifacts/communications/messages/index.md) 와 각 메신저 페이지에 있고, SQLite 에서 지운 행을 찾는 법은 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) 와 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.

관찰한 폰의 설정 키 가운데 삭제·휴지통과 관련이 있어 보이는 것은 아래 둘이고, 둘 다 뜻은 확인하지 못했습니다 (확인 범위: Android 16, One UI 8.5).

| 출력 | 키 |
|---|---|
| `settings global` | `contact_setting_trash_bin_on` |
| `settings system` | `delete_shared_screenshots` |

## 지운 흔적을 보여 주는 다른 기록

메시지를 지워도 그 메시지가 도착했을 때의 알림 기록은 따로 남을 수 있습니다(해석). 관찰한 폰의 `dumpsys usagestats` 이벤트에는 `NOTIFICATION_INTERRUPTION`(`channelId=CHANNEL_ID_SMS_MMS` 처럼 채널 ID 포함)과 `NOTIFICATION_SEEN` 이 있었고, `dumpsys notification` 출력에는 `deleteIntent=` 칸이 있었습니다 (확인 범위: Android 16, One UI 8.5). 알림이 사라진 뒤에도 알림 기록에 남는지는 확인하지 못했으니, 알림이 없다는 사실을 "메시지가 없었다" 로 읽지 않습니다. 알림 기록의 구조는 [알림 기록 (Notification History)](../../../02-artifacts/app-usage/notification-history.md) 에 있습니다.

관찰한 폰의 `/sdcard` 아래에는 Alarms, Android, Audiobooks, DCIM, Documents, Download, Movies, Music, Notifications, Pictures, Podcasts, Recordings, Ringtones 와 이름을 가린 폴더 8개가 있었습니다 (확인 범위: Android 16, One UI 8.5). 이 폴더들에 `.trashed-` 파일이 있었는지는 관찰하지 않았습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 공용 저장 공간의 `.trashed-`·`.pending-` 파일 | 휴지통으로 보낸 파일과 만료 시각 | [공용 저장 공간](../../../01-foundations/storage/shared-storage.md) |
| 2 | MediaStore DB | 파일의 휴지통 상태와 메타데이터 | [미디어 저장소](../../../02-artifacts/media/mediastore/index.md) |
| 3 | 갤러리 앱 자체 기록 | 제조사 갤러리의 휴지통 | [삼성 갤러리](../../../02-artifacts/media/samsung-gallery.md) |
| 4 | 섬네일 캐시 | 사진의 작은 사본(원본을 지운 뒤에도 남는지는 그 페이지 참고) | [섬네일 캐시](../../../02-artifacts/media/thumbnails.md) |
| 5 | 메시지 DB | 남은 대화 | [문자](../../../02-artifacts/communications/messages/index.md) |
| 6 | 알림 기록과 usagestats 알림 이벤트 | 메시지가 도착한 시각 | [알림 기록](../../../02-artifacts/app-usage/notification-history.md) |
| 7 | 클라우드 | 기기 밖에 남은 사본 | [클라우드 데이터](../../../03-techniques/acquisition/cloud-data.md) |

## 분석 흐름

1. Android 버전과 갤러리 앱 종류를 적고, 숨김 파일까지 수집했는지 확인합니다.
2. 공용 저장 공간에서 `.trashed-` 와 `.pending-` 로 시작하는 파일을 모두 찾고, 이름 속 만료 시각을 UTC 로 바꿔 목록을 만듭니다. 시각 값을 바꾸는 법은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 에 있습니다.
3. 만료 시각이 짧은 간격으로 몰려 있으면 한꺼번에 휴지통으로 보낸 것으로 볼 수 있고(해석), 기본값 기준으로 30일을 빼 휴지통으로 보낸 무렵을 셈합니다. 제조사 기간을 확인하지 못했다면 셈한 값에 그 전제를 함께 적습니다.
4. 메시지는 남은 대화와 알림 기록·usagestats 알림 이벤트를 나란히 놓아, 알림은 있는데 대화가 없는 구간을 찾습니다.
5. 2~4단계의 시각을 사건 시각과 한 표에 놓습니다. 지운 내용을 되살려야 하면 [지운 대화와 사진 찾기](../deleted-content.md) 로 넘어갑니다.

## 흔한 오판

**휴지통 파일이 없으니 지운 적이 없다고 보는 경우.** `createDeleteRequest()` 는 휴지통을 거치지 않고 [1], 휴지통 항목도 기간이 지나면 영구 삭제됩니다 [1][2]. 제조사 갤러리가 MediaStore 휴지통을 쓰는지도 확인하지 못했습니다.

**만료 시각을 지운 시각으로 적는 경우.** 이름 속 시각은 영구 삭제 예정 시각이고, 휴지통으로 보낸 시각은 거기서 보관 기간을 빼야 나옵니다 [2]. 보관 기간이 기본값이라는 전제도 함께 밝힙니다.

**`.pending-` 파일을 지운 파일로 보는 경우.** 이 이름은 작성 중인 파일에 붙는 것이고 [2], 휴지통과는 다릅니다.

**휴지통으로 보낸 것을 증거 인멸 의도로 적는 경우.** 기록은 파일이 휴지통으로 갔다는 것까지만 말하고, 누가 왜 그랬는지는 말하지 않습니다. 앱이 사용자에게 요청하는 방식 [1] 과 제조사 갤러리가 확인 창 없이 옮기는 방식 [1] 이 모두 있습니다.

## 보고서 문장 예

> 공용 저장 공간의 (폴더) 에 `.trashed-` 로 시작하는 파일 (개수) 개가 있고, 이름 속 만료 시각은 (시각) UTC 부터 (시각) UTC 사이에 몰려 있습니다. AOSP 기본 보관 기간 30일을 적용하면 이 파일들은 (시각) UTC 무렵 휴지통으로 옮긴 것으로 계산되지만, 이 기기의 실제 보관 기간과 누가 옮겼는지는 이 기록만으로 알 수 없습니다.

## 함께 볼 페이지

- 이 묶음 전체의 길잡이는 [증거를 없애려 했나](index.md) 이고, 앱째 지운 경우는 [앱 지우기](app-removal.md), 기기 전체를 지운 경우는 [초기화](factory-reset.md) 를 봅니다.
- 만료 시각이 기기 시각에 따라 어긋나는 문제는 [시각 바꾸기](time-change.md) 에 있습니다.
- 사진 원본의 촬영 시각·장소는 [이 사진은 언제 어디서 찍었나](../photo-origin.md), 대화 상대는 [누구와 연락을 주고받았나](../communication.md) 에 있습니다.

## 참고 문헌

1. Access media files from shared storage — Android Developers, https://developer.android.com/training/data-storage/shared/media
2. FileUtils.java — AOSP packages/providers/MediaProvider (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_packages_providers_mediaprovider/main/src/com/android/providers/media/util/FileUtils.java
