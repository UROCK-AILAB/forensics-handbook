---
title: "볼륨 UUID로 장치 잇기"
parent: "USB 저장 장치"
grand_parent: "아티팩트 · 외부 장치"
nav_order: 1070
---

# 볼륨 UUID로 장치 잇기 (Volume UUID)

호스트 맥에 남은 볼륨 기록과, 외장 장치의 볼륨 루트에 맥이 남긴 파일을 볼륨 이름과 식별 값으로 맞춰서 "이 맥에 붙었던 볼륨이 지금 압수한 이 장치의 볼륨인가" 를 좁혀 가는 방법을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

통합 로그는 디스크가 나타나고 사라진 시각을 알려 주지만 연결 메시지의 형식 문자열에는 시리얼 번호 같은 장치 식별 값 자리가 없어서, 로그에서 본 디스크가 손에 든 장치와 같은지는 다른 기록으로 이어야 합니다. 이때 쓰는 값이 볼륨 이름과 볼륨 식별 값이고, 그 값은 호스트 맥 쪽과 외장 볼륨 쪽 양쪽에 흩어져 남습니다.

DiskArbitration은 디스크를 설명할 때 볼륨 UUID(`DAVolumeUUID`)와 미디어 UUID(`DAMediaUUID`)를 서로 다른 키로 둡니다 [2]. 두 값이 각각 파일 시스템과 파티션 중 무엇을 가리키는지, 장치를 다시 포맷하면 어느 쪽이 바뀌는지는 확인한 자료가 없어서, 대조할 때는 같은 키의 값끼리만 맞춥니다. 키 목록 전체는 [마운트 기록 (DiskArbitration)](mount-records.md)에 있습니다.

## 위치와 버전별 차이

| 쪽 | 경로 | 담기는 것 | 출처 |
|---|---|---|---|
| 호스트 맥 | `/private/var/db/volinfo.database` | 이전에 붙었던 볼륨의 파일 소유권 정보 | [1] |
| 호스트 맥 | `~/Library/Preferences/com.apple.sidebarlists.plist` | 데스크톱에 마운트되어 사이드바 목록에 나타났던 볼륨 이름 | [1] |
| 외장 볼륨 | `/.Spotlight-V100/VolumeConfiguration.plist` | 스포트라이트가 볼륨에 남긴 설정 파일 | [1] |
| 외장 볼륨 | `/.Spotlight-V100/Store-V1/VolumeConfig.plist` | 스포트라이트가 볼륨에 남긴 설정 파일 | [1] |
| 외장 볼륨 | `/.fseventsd/` | 파일 시스템 이벤트 기록 | [1] |

외장 볼륨 쪽 경로는 그 볼륨의 루트를 기준으로 적었습니다. `com.apple.sidebarlists.plist` 가 어느 macOS 버전까지 쓰였는지는 확인한 자료가 없어서, 최근 버전의 검체에서는 파일이 있는지부터 봅니다. 스포트라이트 plist 안의 키 이름과 버전에 따라 달라지는 저장소 경로도 확인하지 못했고, 스포트라이트 저장소 자체는 [스포트라이트 (Spotlight)](../../file-folder-usage/spotlight/index.md)에서, `.fseventsd` 는 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)에서 다룹니다. `volinfo.database` 설명은 [마운트 기록 (DiskArbitration)](mount-records.md)에 있습니다.

## 잇는 순서

아래 순서는 이 핸드북이 권하는 정리이고, 출처 문서에 정해진 절차는 아닙니다.

1. 통합 로그에서 diskarbitrationd의 `created disk`·`removed disk` 메시지로 디스크가 붙어 있던 구간을 잡습니다. 메시지 찾는 법은 [통합 로그의 연결 기록 (Unified Log)](unified-log.md)에 있습니다.
2. 같은 구간의 볼륨 이름 변경 메시지에서 볼륨 이름을 얻고, 호스트 맥의 `com.apple.sidebarlists.plist` 에 같은 이름이 있는지 봅니다 [1].
3. `volinfo.database` 에 볼륨을 식별하는 값이 들어 있는지 열어 보고, 들어 있으면 그 값을 적어 둡니다 [1].
4. 압수한 외장 장치는 쓰기 방지 상태로 이미지를 뜬 뒤, 볼륨 루트의 `.Spotlight-V100` 설정 plist와 `.fseventsd` 를 열어 볼륨을 식별하는 값이 있는지 봅니다 [1].
5. 3번과 4번에서 같은 종류의 값이 나오면 서로 맞춰 보고, 맞으면 로그의 구간·볼륨 이름과 함께 "같은 볼륨으로 볼 근거" 로 묶습니다.

값이 들어 있는 키 이름이 검체마다 다를 수 있어서, 3번과 4번에서는 키 이름을 짐작해 찾지 말고 파일을 통째로 풀어 UUID 형태의 값을 모두 적은 뒤 비교합니다. UUID를 읽는 법은 [식별자 읽기 (UUID·UID·GUID)](../../../01-foundations/value-decoding/uuid-uid.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 호스트 맥의 기록과 외장 볼륨의 파일에서 같은 식별 값이 나오면, 그 볼륨이 이 맥에 붙은 적이 있다는 근거가 됩니다. 볼륨 이름만 맞을 때보다 식별 값까지 맞을 때 근거가 더 단단해지고, 통합 로그의 구간을 함께 적으면 "이 구간에 이 이름의 볼륨이 붙어 있었다" 까지 말할 수 있습니다.

**증명하지 못하는 것.** 볼륨이 같아도 물리 장치까지 같다고 볼 수는 없습니다. 디스크 설명 키에는 시리얼 번호가 없어서 [2], 볼륨 UUID가 맞아도 장치를 시리얼 번호로 특정하지는 못합니다. 볼륨 이름은 사용자가 바꿀 수 있고 같은 이름의 볼륨도 흔해서, 이름만 맞는 결과를 같은 장치의 근거로 쓰지 않습니다. 이 방법은 볼륨이 붙었다는 사실까지만 말해 주고, 어떤 파일을 옮겼는지는 [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)의 흐름처럼 파일 쪽 기록을 더해야 말할 수 있습니다.

## 함정과 한계

`DAVolumeUUID` 와 `DAMediaUUID` 는 다른 값이라 [2], 한쪽 기록의 볼륨 UUID를 다른 쪽 기록의 미디어 UUID와 맞춰 보면 틀린 결론이 나옵니다. 어느 쪽이 재포맷에 따라 바뀌는지 확인하지 못했으니, 값이 맞지 않는다고 해서 다른 장치라고 단정하지도 않습니다.

외장 장치를 분석하는 맥에 그냥 꽂으면 그 맥이 볼륨 루트에 스포트라이트·파일 시스템 이벤트 파일을 새로 쓰거나 고칠 수 있습니다. 볼륨 쪽 파일은 반드시 쓰기 방지 장치를 거쳐 확보한 이미지에서 읽고, 방법은 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)에서 다룹니다.

최근 항목(sfl·sfl2)이나 북마크 데이터에 볼륨 식별 값이 들어 있는지는 확인하지 못했습니다. 들어 있다면 쓸 만한 연결 고리라서, [최근 항목 (Shared File Lists)](../../file-folder-usage/recent-items/index.md)과 [파일 참조 데이터 (Alias·Bookmark)](../../../01-foundations/value-decoding/alias-bookmark.md)를 보면서 검체에서 직접 확인합니다.

## 교차 검증

디스크가 붙어 있던 구간은 [통합 로그의 연결 기록 (Unified Log)](unified-log.md)에서, 볼륨 기록과 디스크 설명 키는 [마운트 기록 (DiskArbitration)](mount-records.md)에서 봅니다. 외장 볼륨 안에서 무엇이 바뀌었는지는 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)에, 볼륨 구조는 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md)와 [HFS+ 구조 (HFS+)](../../../01-foundations/disk-volume/hfs-plus.md)에 있습니다.

## 실습

USB 저장 장치 하나를 테스트 맥에 꽂았다 뺀 뒤, 호스트 맥과 장치를 따로 이미지로 떠서 아래 질문을 풀어 봅니다.

1. 호스트 맥의 `com.apple.sidebarlists.plist` 에 장치의 볼륨 이름이 남았는가? 파일이 없다면 그 macOS 버전에서는 어디를 더 봐야 하는가?
2. 장치 볼륨 루트의 `.Spotlight-V100` 설정 plist에서 UUID 형태의 값을 모두 적으면 몇 개이고, 그중 호스트 맥 기록에도 나오는 값이 있는가?
3. 장치를 다시 포맷한 뒤 같은 맥에 꽂으면, 2번에서 적은 값 중 어느 것이 바뀌는가?

## 참고 문헌

1. ForensicArtifacts — artifacts/data/macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. Apple Open Source, DiskArbitration — diskarbitrationd/DAInternal.c (main 브랜치) — https://raw.githubusercontent.com/apple-oss-distributions/DiskArbitration/main/diskarbitrationd/DAInternal.c
