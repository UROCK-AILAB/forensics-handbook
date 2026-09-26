---
title: "마운트 기록"
parent: "USB 저장 장치"
grand_parent: "아티팩트 · 외부 장치"
nav_order: 1060
---

# 마운트 기록 (DiskArbitration)

디스크 중재 (DiskArbitration)가 외장 디스크를 설명할 때 쓰는 키 이름과, 호스트 맥에 남는 이전 볼륨 기록(`volinfo.database`)을 읽는 법을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

DiskArbitration은 macOS에서 디스크가 나타나고 사라지는 것을 받아 마운트를 처리하는 구성 요소이고, 그 일을 하는 데몬이 diskarbitrationd입니다. 데몬은 시작할 때 "media appeared", "media disappeared", "file system mounted", "file system unmounted", "file system updated" 알림을 등록하고, 이 알림을 등록하지 못하면 `could not create "media appeared" notification.` 같은 오류 문구를 남기도록 짜여 있습니다 [3]. 마운트할 자리의 폴더도 이 데몬이 만들고, 소스에서 그 경로는 `kDAMainMountPointFolder` 상수에 `/Volumes` 로 정해져 있습니다 [3]. 폴더를 만들지 못했을 때의 오류 문구는 `could not create mount point folder.` 입니다 [3].

데몬은 디스크 하나를 볼륨·미디어·장치·버스 정보를 담은 설명 사전(disk description)으로 다루고, 그 사전의 키 이름이 소스에 정의돼 있습니다 [2]. 분석 도구나 다른 기록에 `DAVolumeName`, `DAMediaBSDName` 같은 이름이 나오면 DiskArbitration이 디스크를 설명한 값이라고 읽으면 됩니다.

디스크가 나타나고 사라진 순간을 적은 로그 메시지는 [통합 로그의 연결 기록 (Unified Log)](unified-log.md)에 정리돼 있어서 이 페이지에서는 되풀이하지 않습니다.

## 위치와 버전별 차이

| 기록 | 위치 | 내용 | 출처 |
|---|---|---|---|
| 디스크 설명 키 | diskarbitrationd 소스(`DAInternal.c`)에 정의 | 볼륨·미디어·장치·버스를 설명하는 키 이름 | [2] |
| 이전 볼륨 기록 | `/private/var/db/volinfo.database` (`/var/db/volinfo.database`) | 이전에 붙었던 볼륨의 파일 소유권 정보 | [1] |
| 마운트된 디스크 이미지 | `hdiutil info` (켜져 있는 맥에서 실행) | 지금 마운트된 DMG 목록 | [1] |

키 이름은 DiskArbitration 소스의 main 브랜치 기준이라, 어느 macOS 버전부터 어느 키가 있었는지는 이 소스로 정해지지 않습니다. `volinfo.database` 가 어느 macOS 버전에 있고 파일 형식이 무엇인지는 공개된 분석 자료가 없어서, 실제 기기에서는 파일이 있는지와 첫 바이트가 어떤 형식인지부터 봅니다.

## 구조

### 디스크 설명 키

소스에 정의된 키를 묶음별로 나누면 아래와 같습니다 [2]. "분석에 쓰는 점" 칸이 빈 키는 소스에 뜻 설명이 없고 이름만으로도 뜻이 분명하지 않은 것입니다.

| 묶음 | 키 | 분석에 쓰는 점 |
|---|---|---|
| 볼륨 | `DAVolumeKind` | 파일 시스템 종류 |
| 볼륨 | `DAVolumePath` | 마운트 경로 |
| 볼륨 | `DAVolumeName` | 볼륨 이름 |
| 볼륨 | `DAVolumeUUID` | 볼륨 UUID, [볼륨 UUID로 장치 잇기](volume-uuid.md)에서 씀 |
| 볼륨 | `DAVolumeMountable`, `DAVolumeNetwork`, `DAVolumeType`, `DAVolumeLifsURL` | |
| 미디어 | `DAMediaBSDName` | BSD 장치 이름(예: `disk4s1`) |
| 미디어 | `DAMediaUUID` | 미디어 UUID, 볼륨 UUID와 따로 있음 |
| 미디어 | `DAMediaBlockSize`, `DAMediaBSDMajor`, `DAMediaBSDMinor`, `DAMediaBSDUnit`, `DAMediaContent`, `DAMediaEjectable`, `DAMediaIcon`, `DAMediaKind`, `DAMediaLeaf`, `DAMediaName`, `DAMediaPath`, `DAMediaRemovable`, `DAMediaSize`, `DAMediaType`, `DAMediaWhole`, `DAMediaWritable`, `DAMediaEncrypted`, `DAMediaEncryptionDetail`, `DAMediaMatch` | |
| 장치 | `DADeviceProtocol` | 연결 방식(예: USB) |
| 장치 | `DADeviceGUID`, `DADeviceInternal`, `DADeviceModel`, `DADevicePath`, `DADeviceRevision`, `DADeviceUnit`, `DADeviceVendor`, `DADeviceTDMLocked` | |
| 버스 | `DABusName`, `DABusPath` | |
| 기타 | `DAAppearanceTime` | 디스크가 나타난 시각 |
| 기타 | `DARepairRunning`, FSKit 쪽 접두사 `FS` | |

이 목록에 USB 시리얼 번호를 담는 키는 없습니다 [2]. 장치를 시리얼 번호로 특정하려면 이 키가 아닌 다른 기록을 찾아야 합니다.

이 키 묶음을 통째로 디스크에 저장하는 파일은 공개 자료에 나오지 않습니다. 그래서 키 목록은 "어느 파일을 열면 나온다" 가 아니라, 로그·도구 출력·보고서에 나온 값을 읽을 때 쓰는 이름표로 봅니다.

### volinfo.database

`/private/var/db/volinfo.database` 에는 이전에 이 맥에 붙었던 볼륨의 파일 소유권 정보가 남습니다 [1]. 담기는 필드(볼륨 UUID가 들어가는지 등)와 파일 형식은 실제 파일로 확인해야 합니다. 볼륨을 식별하는 값이 들어 있으면 [볼륨 UUID로 장치 잇기 (Volume UUID)](volume-uuid.md)의 대조에 씁니다.

## 증거로서 의미

**증명하는 것.** `volinfo.database` 에 어떤 볼륨의 항목이 있으면 그 볼륨이 이전에 이 맥에 붙은 적이 있다는 단서가 됩니다 [1]. 로그나 도구 출력에 디스크 설명 키 값이 찍혀 있으면 그 디스크의 파일 시스템 종류, 마운트 경로, 볼륨 이름, 연결 방식(`DADeviceProtocol`)을 그 값으로 말할 수 있습니다. 실행 중인 맥에서는 `hdiutil info` 로 지금 마운트된 DMG를 가려내서, 외장 장치와 디스크 이미지를 섞지 않을 수 있습니다 [1].

**증명하지 못하는 것.** 설명 키에 시리얼 번호가 없어서 이 값만으로는 물리 장치 한 개를 특정하지 못합니다. 볼륨 기록은 볼륨이 붙은 적이 있다는 데서 그치고, 언제 붙었는지·몇 번 붙었는지·무엇을 복사했는지는 알 수 없습니다.

## 시각 해석

`DAAppearanceTime` 은 디스크가 나타난 시각을 담는 키지만, 이 값이 2001-01-01 기준(맥 절대 시각)인지는 알려진 자료가 없습니다. 이 값을 날짜로 바꿀 때는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)의 방식 몇 가지로 풀어 보고, 같은 순간의 통합 로그 시각과 맞는 쪽을 고릅니다. 연결 시각의 기준은 [통합 로그의 연결 기록](unified-log.md)에서 잡는 편이 확실합니다.

## 함정과 한계

키 이름은 main 브랜치 소스 기준이라 오래된 macOS에는 없는 키가 섞여 있을 수 있습니다. `DAVolumeUUID` 와 `DAMediaUUID` 는 서로 다른 키라서, 보고서에 UUID를 적을 때는 어느 키의 값인지 밝힙니다.

`hdiutil info` 는 실행 중인 맥에서 지금 마운트된 것만 보여 주는 명령이라 [1], 이미지로 확보한 디스크에서는 쓸 수 없고 이미 떼어 낸 이미지도 나오지 않습니다. 디스크 이미지 형식 자체는 [디스크 이미지 형식 (DMG·Sparsebundle)](../../../01-foundations/disk-volume/dmg-sparsebundle.md)에서 다룹니다.

## 교차 검증

디스크가 나타나고 사라진 시각은 [통합 로그의 연결 기록 (Unified Log)](unified-log.md)에서, 볼륨이 어떤 장치였는지는 [볼륨 UUID로 장치 잇기 (Volume UUID)](volume-uuid.md)에서 봅니다. 외장 볼륨 안의 변경 기록은 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)에 남고, 실행 중인 맥에서 마운트 상태를 확보하는 방법은 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md)에 있습니다.

## 실습

USB 저장 장치를 꽂았다 뺀 테스트 맥에서 아래 질문을 풀어 봅니다.

1. `/private/var/db/volinfo.database` 가 있는가? 있다면 첫 바이트로 보아 어떤 형식인가?
2. 장치를 꽂기 전과 뺀 뒤에 이 파일의 크기나 수정 시각이 바뀌었는가?
3. 디스크 이미지를 하나 마운트한 상태에서 `hdiutil info` 를 실행하면, 외장 USB 장치와 어떻게 구분되는가?

## 참고 문헌

1. ForensicArtifacts — artifacts/data/macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. Apple Open Source, DiskArbitration — diskarbitrationd/DAInternal.c (main 브랜치) — https://raw.githubusercontent.com/apple-oss-distributions/DiskArbitration/main/diskarbitrationd/DAInternal.c
3. Apple Open Source, DiskArbitration — diskarbitrationd/DAMain.c (main 브랜치) — https://raw.githubusercontent.com/apple-oss-distributions/DiskArbitration/main/diskarbitrationd/DAMain.c
