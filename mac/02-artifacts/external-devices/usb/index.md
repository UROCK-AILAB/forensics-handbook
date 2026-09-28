---
title: "USB 저장 장치"
parent: "아티팩트 · 외부 장치"
nav_order: 1040
has_children: true
has_toc: false
---

# USB 저장 장치 (USB Storage)

맥에 USB 저장 장치가 붙었던 흔적을 통합 로그의 연결 메시지, DiskArbitration의 디스크 설명 값과 볼륨 기록, 외장 볼륨에 맥이 남긴 파일에서 찾아 서로 맞춰 보는 방법을 모았습니다.

## 왜 중요한가

자료 유출이나 악성 코드 유입을 조사할 때는 "언제 어떤 외장 장치가 이 맥에 붙었나" 를 먼저 묻게 되고, 맥에서는 그 답이 한 파일에 모여 있지 않습니다. 이 허브가 다루는 흔적은 통합 로그, DiskArbitration 쪽 기록, 호스트 맥과 외장 볼륨에 남은 볼륨 파일로 흩어져 있어서, 로그로 시각을 잡고 볼륨 기록으로 어떤 볼륨이었는지를 좁히는 식으로 여러 기록을 이어 봐야 합니다. 이 흔적들로 장치의 시리얼 번호까지 얻지는 못하고, 그 한계는 하위 페이지마다 따로 적었습니다.

Apple silicon 맥 노트북은 새 USB·Thunderbolt 액세서리나 SD 카드를 연결할 때 사용자에게 허용 여부를 묻습니다 [3]. 이 설정은 시스템 설정의 개인정보 보호 및 보안 항목 중 "Allow accessories to connect" 에 있고, "Always ask", "Ask for new accessories"(기본값), "Automatically allow when unlocked", "Always allow" 중에서 고릅니다 [3]. 맥이 잠겨 있으면 잠금을 먼저 풀어야 허용할 수 있고, 3일 넘게 잠겨 있었으면 전에 허용한 액세서리도 다시 잠금 해제를 요구할 수 있으며, "Don't Allow" 를 골라도 충전은 됩니다 [3]. 감독(supervised) 상태의 맥 노트북에서는 관리자가 이 설정을 통제할 수 있어서 [3], 조사 대상 맥이 기관 관리 기기라면 [구성 프로파일 (Configuration Profiles·MDM)](../../persistence/configuration-profiles.md)도 함께 봅니다. Apple 문서에는 이 기능이 들어온 macOS 버전이 적혀 있지 않습니다. 허용·거부 결정이 어느 파일이나 로그에 남는지는 같은 macOS 버전의 시험 기기에서 액세서리를 허용·거부해 본 뒤 통합 로그와 파일 변경 기록을 보고 확인합니다.

## 한눈에 보기

| 기록 | 위치 | macOS 버전 | 알려 주는 것 | 페이지 |
|---|---|---|---|---|
| 통합 로그의 연결 메시지 | `/private/var/db/diagnostics/`, `/private/var/db/uuidtext/` | 통합 로그는 10.12 Sierra부터 [2], 메시지 문구의 버전 범위는 확인 안 됨 | 디스크가 나타나고 사라진 시각, 볼륨 이름 변경, 디스크 작업 요청 | [통합 로그의 연결 기록](unified-log.md) |
| 디스크 설명 키 | DiskArbitration이 디스크를 설명할 때 쓰는 이름 | 확인 안 됨 | 파일 시스템 종류, 마운트 경로, 연결 방식, 볼륨·미디어 UUID | [마운트 기록](mount-records.md) |
| 이전 볼륨 기록 | `/private/var/db/volinfo.database` | 확인 안 됨 | 이전에 붙었던 볼륨의 파일 소유권 정보 [1] | [마운트 기록](mount-records.md) |
| 사이드바 볼륨 이름 | `~/Library/Preferences/com.apple.sidebarlists.plist` | 확인 안 됨 | 사이드바에 나타났던 볼륨 이름 [1] | [볼륨 UUID로 장치 잇기](volume-uuid.md) |
| 외장 볼륨의 맥 파일 | 볼륨 루트의 `/.Spotlight-V100/`, `/.fseventsd/` | 확인 안 됨 | 볼륨을 이 맥 기록과 맞춰 볼 단서 [1] | [볼륨 UUID로 장치 잇기](volume-uuid.md) |

## 읽는 순서

1. [통합 로그의 연결 기록 (Unified Log)](unified-log.md) — diskarbitrationd가 남기는 디스크 등장·사라짐 메시지와 수준, `log show` 로 뽑는 법, 시각을 UTC로 읽는 법을 다룹니다.
2. [마운트 기록 (DiskArbitration)](mount-records.md) — 디스크 설명 키를 묶음별로 정리하고, `volinfo.database` 와 `hdiutil info` 로 볼륨과 디스크 이미지를 가려내는 법을 봅니다.
3. [볼륨 UUID로 장치 잇기 (Volume UUID)](volume-uuid.md) — 호스트 맥 기록과 외장 볼륨 파일을 볼륨 이름과 식별 값으로 맞춰, 붙었던 볼륨이 압수한 장치의 볼륨인지 좁혀 가는 순서를 정리합니다.

## 함께 볼 페이지

- [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) — 외장 볼륨 안에서 무엇이 바뀌었는지 볼 때
- [스포트라이트 (Spotlight)](../../file-folder-usage/spotlight/index.md) — 외장 볼륨의 `.Spotlight-V100` 저장소를 읽을 때
- [아이폰·아이패드 연결 (iOS Devices)](../ios-devices/index.md) — 저장 장치가 아닌 아이폰·아이팟 연결 기록(`~/Library/Preferences/com.apple.iPod.plist` [1])을 볼 때
- [디스크 이미지 형식 (DMG·Sparsebundle)](../../../01-foundations/disk-volume/dmg-sparsebundle.md) — 로그에 나온 디스크가 디스크 이미지일 수 있을 때
- [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md) — 연결 메시지 말고 다른 사건을 찾을 때
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) — 연결 시각을 다른 기록과 한 시간축에 놓을 때
- [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md) — 외장 장치로 자료가 나갔는지 조사하는 흐름

## 참고 문헌

1. ForensicArtifacts — artifacts/data/macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. libyal dtformats — Apple Unified Logging and Activity Tracing formats — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
3. Apple Support 102282, 맥 노트북의 액세서리 연결 허용 안내 — https://support.apple.com/en-us/102282
