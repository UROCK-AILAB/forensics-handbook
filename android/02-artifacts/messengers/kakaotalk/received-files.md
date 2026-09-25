---
title: "받은 파일"
parent: "카카오톡"
grand_parent: "아티팩트 · 메신저"
nav_order: 930
---

# 받은 파일 (Received Files)

대화에 붙은 파일·사진 정보는 `chat_logs` 표의 암호화된 `attachment` 칸에 들어가고, 받은 파일 원본이 기기의 어느 폴더에 얼마 동안 남는지는 공개 자료로 아직 확인하지 못했습니다.

## 무엇을 기록하나 · 왜 생기나

카카오톡은 메시지 한 건에 붙은 파일이나 사진의 정보를 그 메시지 행의 `attachment` 칸에 적습니다. 이 칸은 `message` 칸과 함께 암호화 대상이라서, DB 를 열어도 풀기 전에는 파일 이름이나 종류를 읽을 수 없습니다. 칸의 위치와 암호화 방식은 [대화 DB 구조와 암호화](chat-db.md)에서 다룹니다. `attachment` 칸을 풀었을 때 안이 JSON 인지, 파일 이름·URL·크기를 어떤 키로 적는지는 확인하지 못했습니다.

## 위치와 버전별 차이

받은 파일과 관련해 확인한 것과 확인하지 못한 것을 나누면 다음과 같습니다. 확인한 것은 카카오톡 10.1.7 을 Android 11 에뮬레이터에서 조사한 공개 기록에서 나왔습니다.

| 항목 | 상태 |
|---|---|
| 첨부 정보가 들어가는 칸 | `KakaoTalk.db` 의 `chat_logs.attachment` (암호화) |
| 외부 캐시 `/storage/emulated/0/Android/data/com.kakao.talk/cache` | 로그인 직후 `MiniProfile`, `default`, `journal` 이 생김. 받은 파일 원본이 여기 남는지는 확인 못 함 |
| 내부 캐시 `cache/media` | 16진수 이름에 `.uid` 가 붙은 파일이 설치 직후와 로그인 뒤 각각 생김. 역할은 확인 못 함 |
| 사용자가 "저장" 한 파일이 가는 `/sdcard` 폴더 | 확인 못 함 |
| 원본이 기기에 남는 기간, 자동 삭제 여부 | 확인 못 함 |
| 서버 보관 기간 | 확인 못 함 |

이 핸드북의 관찰 기기(확인 범위: Android 16, One UI 8.5)에서 `/sdcard` 최상위와 `Download`, `Pictures`, `DCIM` 아래에는 표준이 아닌 폴더가 있었지만, 관찰 메모에서 이름을 가려 두어 그중에 카카오톡 폴더가 있는지는 알 수 없습니다. Android 버전이나 삼성 One UI 에 따라 저장 폴더가 달라지는지 보여 주는 자료도 찾지 못했습니다.

## 증거로서 의미

**증명하는 것.** `attachment` 칸에 값이 있는 행은 그 메시지에 첨부 정보가 적혀 있었다는 뜻이고, 같은 행의 `chat_id`, `user_id`, `created_at` 으로 어느 대화방에서 누구에게서 언제 들어온 기록인지 정리할 수 있습니다.

**증명하지 못하는 것.** 첨부 정보가 있다고 해서 파일 원본을 기기에 내려받았다거나, 사용자가 열어 봤다거나, 따로 저장했다고 말할 수는 없습니다. `/sdcard` 에서 비슷한 이름의 파일을 찾더라도, 그 파일이 카카오톡으로 받은 것이라고 이어 주는 기록은 아직 확인하지 못했습니다. 보고서에는 "이 대화방에 이 시각 첨부 정보가 적힌 메시지 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 함정과 한계

받은 파일 저장 위치를 확인한 공개 자료가 없어서, 다른 메신저에서 쓰는 폴더 이름을 떠올려 카카오톡도 같을 것이라고 가정하기 쉽습니다. 시험 기기에서 직접 파일을 받아 보고 어디에 생기는지 확인하기 전에는 경로를 보고서에 쓰지 않습니다.

외부 캐시의 `MiniProfile`, `default`, `journal` 은 조사 기록에 이름과 생긴 시점만 있어서, 이 폴더에 있는 파일을 받은 파일로 곧바로 해석하지 않습니다.

## 직접 분석해 보기

먼저 `attachment` 칸에 값이 있는 행을 골라 대화방과 시각별로 수를 세고, 공개 도구로 칸을 풀 수 있다면 풀린 값의 구조를 기록해 둡니다. 그다음 `/sdcard` 의 파일을 [미디어 저장소 (MediaStore)](../../media/mediastore/index.md)에서 찾아 저장 경로와 추가 시각을 보고, 그 시각이 첨부 메시지의 `created_at` 과 가까운지 봅니다. 시각 칸의 단위를 먼저 밝혀야 하는 이유는 [대화 DB 구조와 암호화](chat-db.md)에서 설명합니다.

## 교차 검증

- [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md) — 앱이 `/sdcard` 에 파일을 쓰는 방식과 `Android/data` 폴더의 성격을 다룹니다.
- [미디어 저장소 (MediaStore)](../../media/mediastore/index.md) — 받은 사진·동영상이 공용 저장 공간에 저장됐다면 여기서 경로와 시각을 찾습니다.
- [섬네일 캐시 (Thumbnails)](../../media/thumbnails.md) — 원본을 지운 뒤에도 남을 수 있는 작은 그림을 찾습니다.
- [자료를 밖으로 보냈나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md) — 메신저로 파일이 오간 흔적을 다른 기록과 함께 보는 조사 흐름입니다.

## 실습

직접 만든 시험 기기에서 다음을 해 보고 기록합니다.

1. 사진 한 장과 문서 파일 한 개를 받은 뒤, 앱 내부 저장소와 `/sdcard` 에서 새로 생긴 파일을 찾습니다. 어느 폴더에 생겼습니까?
2. 받은 파일을 앱에서 "저장" 한 뒤 새로 생긴 파일은 어디에 있고, MediaStore 에는 어떤 경로로 들어갔습니까?
3. 그 메시지 행의 `attachment` 칸을 풀 수 있다면 어떤 키가 보이고, 1·2번에서 찾은 파일과 이어 줄 값이 있습니까?

## 참고 문헌

1. jiru/kakaodecrypt — kakaodecrypt.py. https://github.com/jiru/kakaodecrypt/blob/HEAD/kakaodecrypt.py
2. dfrc-korea/carpe — modules/schema/kakaotalk_mobile/lv1_app_kakaotalk_mobile_chatlogs.yaml. https://github.com/dfrc-korea/carpe/blob/HEAD/modules/schema/kakaotalk_mobile/lv1_app_kakaotalk_mobile_chatlogs.yaml
3. stulle123/kakaotalk_analysis — recon/file_diff_before_and_after_login.txt. https://github.com/stulle123/kakaotalk_analysis/blob/HEAD/recon/file_diff_before_and_after_login.txt
4. stulle123/kakaotalk_analysis — doc/RECON.md. https://github.com/stulle123/kakaotalk_analysis/blob/HEAD/doc/RECON.md
