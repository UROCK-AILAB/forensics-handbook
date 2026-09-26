---
title: "조사 절차"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 1900
---

# 조사 절차 (Investigation Process)

맥 조사는 NIST SP 800-86의 네 단계인 수집·검사·분석·보고를 뼈대로 삼고 RFC 3227의 증거 수집 원칙을 지키며 진행하지만, 맥은 끄기 전에 칩 종류와 파일볼트 (FileVault) 상태, 원격 지우기 위험을 먼저 확인해야 한다는 점이 다릅니다.

## 언제 쓰나

사고 대응 중 맥을 증거로 다뤄야 할 때, 그리고 압수하거나 넘겨받은 맥을 분석하기 전에 이 절차를 씁니다. 절차의 틀은 NIST SP 800-86[1]과 RFC 3227[3] 두 문서에서 가져옵니다. SP 800-86은 포렌식을 네 단계로 나누고, 단계마다 뜻을 아래처럼 정합니다.

| 단계 | SP 800-86의 정의(요약) | 이 핸드북에서 이어지는 곳 |
|---|---|---|
| 수집 (Collection) | 관련 데이터가 있을 만한 출처를 찾고, 표시하고, 기록하고, 데이터를 확보합니다. 이때 데이터의 무결성을 지키는 절차를 따릅니다. | [라이브 대응](live-response/index.md), [맥 증거 확보](evidence-acquisition/index.md) |
| 검사 (Examination) | 모은 데이터를 자동·수동 방법으로 처리하고, 관심 있는 데이터를 가려 뽑습니다. 여기서도 무결성을 지킵니다. | [콘텐츠 검색](../analysis/content-search.md), [암호화된 증거 다루기](../analysis/encrypted-evidence/index.md) |
| 분석 (Analysis) | 검사 결과를 법적으로 정당화할 수 있는 방법으로 분석해, 수집과 검사를 시작하게 한 질문에 답할 정보를 끌어냅니다. | [타임라인 작성](../analysis/timeline/index.md) |
| 보고 (Reporting) | 분석 결과를 보고합니다. 쓴 조치, 도구·절차를 고른 이유, 더 해야 할 조치(추가 데이터 확보, 취약점 조치, 보안 통제 개선), 권고를 담을 수 있습니다. | [포렌식 보고서](../reporting/forensic-report.md) |

증거를 모으고 보관할 때는 시스템 상태를 정확히 떠 두고, 수집하면서 데이터를 되도록 바꾸지 않고, 분석보다 수집을 먼저 하고, 휘발성이 큰 것부터 작은 것 순으로 모읍니다[3]. 사고 대응 전체의 틀은 NIST SP 800-61이 다루는데, 2025년 4월에 나온 Rev. 3가 2012년의 Rev. 2를 대체했고 사고 대응을 CSF 2.0의 기능(Govern, Identify, Protect, Detect, Respond, Recover)에 맞춰 정리합니다[2]. 이 페이지는 그중 포렌식 절차만 다룹니다.

절차의 틀은 OS와 상관없이 같아서 윈도우 조사와 뼈대가 같지만, 맥은 기종별 하드웨어 암호화 때문에 "끄기 전에 무엇을 판단하나"의 비중이 큽니다.

> 그림 자리: 준비 → 현장 판단(켜짐·꺼짐, 잠금, 칩, 파일볼트, 네트워크) → 수집(휘발성 먼저) → 확보 → 검사·분석 → 보고로 이어지는 흐름도. 각 상자에 이 핸드북의 해당 페이지 이름을 적는다.

## 절차

1. **증거를 법적 절차에 쓸지 먼저 정합니다.** 수집 전에 증거를 법적 절차나 내부 징계 절차에 쓸 수 있게 보존할지를 분석가나 관리자가 조직 정책과 법무 자문에 따라 먼저 정합니다[1]. 그렇게 쓰기로 했다면 증거 보관 연속성 (Chain of Custody)을 지키고, 증거를 물리적으로 맡은 모든 사람과 그 사람이 한 조치, 그 시각을 기록하며, 쓰지 않을 때는 안전한 곳에 보관합니다. 출처가 많으면 전부 확보하기는 현실적으로 어려워서, 우선순위를 판단하는 계획·지침·절차를 조직이 미리 문서로 만들어 둡니다[1].

2. **현장에서 시스템 상태와 시각을 기록합니다.** 시각을 적은 상세 기록을 남기고(가능하면 자동으로), 기록하는 시각마다 시스템 시계와 UTC의 차이를 적고, 모든 조치와 그 시각을 나중에 증언할 수 있게 준비합니다[3]. 맥이라면 아래 항목을 현장 기록에 넣습니다.

   | 기록 항목 | 자세한 내용 |
   |---|---|
   | 시스템 시각, 표준 시간대, UTC와의 차이 | [시간대와 시계 설정](../../02-artifacts/system-account/time-zone.md) |
   | 기종과 칩 종류 | [컴퓨터 이름과 하드웨어 정보](../../02-artifacts/system-account/computer-name-hardware.md), 이 페이지의 4단계 |
   | macOS 버전 | [OS 버전과 설치 기록](../../02-artifacts/system-account/os-version-install-history.md) |
   | 파일볼트 상태 | [파일볼트](../../01-foundations/protection/filevault/index.md), 이 페이지의 도구 절 |
   | 화면 잠금 여부, 전원 상태(켜짐·잠자기·꺼짐) | 현장에서 눈으로 확인한 대로 적습니다 |
   | 네트워크 연결 상태(유선, Wi-Fi) | [네트워크 인터페이스와 설정](../../02-artifacts/network/network-interfaces.md) |

3. **외부에서 바꿀 수 있는 경로를 막습니다.** 외부에서 증거를 바꿀 수 있는 경로는 없앱니다[3]. 맥에서는 원격 지우기가 대표적인 경로입니다. iCloud.com의 기기 찾기(Find Devices)로 맥도 지울 수 있고, 맥이 오프라인일 때 요청이 들어오면 다음에 온라인이 될 때 지우기가 시작됩니다[6]. 그래서 확보한 맥은 Wi-Fi를 포함한 네트워크에서 떼어 둡니다. 봉쇄 (Containment) 방법에는 네트워크 케이블 분리, 전원 분리, 물리 보안 강화, 정상 종료 (Graceful Shutdown)가 있고, 기존 정책과 위험 평가에 따라 가능하면 증거 무결성을 지키는 쪽을 고릅니다[1]. 다만 연결이 끊기면 증거를 지우는 장치(deadman switch)가 작동할 수 있으니[3], 떼기 전에 그런 구성이 있는지 따져 보고 판단과 조치를 기록합니다.

4. **칩 종류를 확인합니다.** 칩 종류에 따라 확보 경로가 달라지고, 세부 방법은 [맥 증거 확보](evidence-acquisition/index.md)에서 다룹니다. 켜진 맥에서는 Option 키를 누른 채 Apple 메뉴에서 시스템 정보(System Information)를 열고, 사이드바에서 "Controller" 또는 "iBridge"(macOS 버전에 따라 이름이 다릅니다)를 고릅니다. 오른쪽에 "Apple T2 chip"이 보이면 T2 맥입니다.

   | 종류 | 해당 기종[4] |
   |---|---|
   | 인텔, T2 없음 | 아래 T2 기종 목록에 없는 인텔 맥 |
   | 인텔, T2 있음 | MacBook Pro(2018~2020, M1 2020 제외), MacBook Air(2018~2020, M1 2020 제외), iMac(Retina 5K, 27-inch, 2020), iMac Pro, Mac mini(2018), Mac Pro(2019, 랙 장착형 포함) |
   | Apple silicon | 2020년 말 일부 기종부터 전환이 시작됨 |

5. **파일볼트 상태와 잠금 여부를 보고 끌지 말지를 정합니다.** 켜진 맥이 파일볼트가 켜져 있고 잠금이 풀린 상태라면, 끄기 전에 라이브 수집을 할지부터 정합니다([맥 증거 확보](evidence-acquisition/index.md)). 전원을 끄면 무엇이 다시 잠기는지는 [파일볼트](../../01-foundations/protection/filevault/index.md) 페이지에서 다룹니다. 상태를 확인하는 명령은 아래 도구 절에 있습니다.

6. **수집 우선순위를 정합니다.** 데이터 확보는 계획 세우기, 확보, 확보한 데이터의 무결성 확인의 세 단계로 나뉘고, 계획 단계에서 출처별 확보 순서를 정합니다[1]. 순서는 세 가지를 따져 정합니다.

   | 요소 | 뜻 |
   |---|---|
   | 쓸모 있을 가능성 (Likely Value) | 상황 이해와 경험으로 출처마다 가치를 가늠합니다. |
   | 휘발성 (Volatility) | 전원을 끄거나 시간이 지나면 사라지는 데이터입니다. 대개 휘발성 데이터를 먼저 확보하지만, 새 이벤트로 덮어쓰이는 로그 파일처럼 비휘발성 데이터도 바뀔 수 있습니다. |
   | 드는 노력 (Amount of Effort Required) | 분석가의 시간, 법무 자문, 장비와 외부 전문가 비용입니다. |

7. **휘발성 데이터부터 모읍니다.** RFC 3227의 휘발성 순서를 따라 메모리와 프로세스 표처럼 사라지기 쉬운 것부터 모으고, 맥에서 쓰는 명령과 순서는 [라이브 대응](live-response/index.md)에서 다룹니다. 증거 수집을 마치기 전에는 끄지 않고, 대상 시스템의 프로그램을 믿지 않습니다[3]. 메모리를 모았다면 [메모리 분석](../analysis/memory-forensics/index.md)으로 넘어갑니다.

8. **끌 때는 방법을 골라 기록합니다.** 정상 종료는 열린 파일을 닫고 임시 파일을 지우고 스왑을 비울 수 있고, 메모리에만 있는 루트킷이 사라지거나 트로이 목마가 흔적을 지울 수도 있습니다[1]. 전원 분리는 정상 종료 때 바뀌거나 지워질 스왑·임시 파일 같은 정보를 남길 수 있지만, 일부 OS에서는 열린 파일이 깨질 수 있습니다. 벽 콘센트에서 플러그를 뽑는 방법은 무정전 전원 장치(UPS)에 꽂혀 있을 수 있어서 권하지 않습니다. OS별 종료 동작을 알고 보존할 데이터 종류에 맞춰 종료 방법을 고릅니다[1].

9. **비휘발성 출처를 복제하고 원본을 보관합니다.** 도구로 휘발성 데이터를 모은 다음 비휘발성 출처를 복제하고, 원본은 안전하게 보관합니다[1]. 현장(로컬)에서 확보하면 통제하기 쉬워 대개 더 낫습니다[1]. 맥의 확보 방법은 [맥 증거 확보](evidence-acquisition/index.md)에서 다룹니다.

10. **해시로 무결성을 확인합니다.** 비트 스트림 이미지는 이미징 전에 원본의 해시 (hash)를 기록하고, 이미징 뒤 사본의 해시를 계산해 비교하고, 원본의 해시를 다시 계산해 이미징이 원본을 바꾸지 않았는지 확인한 뒤 결과를 모두 기록합니다. SP 800-86은 해시 알고리즘으로 MD5와 SHA-1을 가장 흔한 것으로 들고 연방 기관에는 SHA-1을 쓰라고 하는데, 이는 2006년 문서의 기준입니다[1].

11. **사본으로 검사·분석하고 보고합니다.** 비트 수준 사본을 만들고 분석은 사본으로 합니다[3]. 검사와 분석은 [타임라인 작성](../analysis/timeline/index.md) 같은 분석 페이지로, 결과 정리는 [포렌식 보고서](../reporting/forensic-report.md)로 이어지고, 쓴 도구를 믿을 근거는 [도구 검증](../reporting/tool-validation.md)에서 다룹니다.

## 증거 보관 연속성 기록

보관 연속성 기록에는 증거를 어디서, 언제, 누가 발견하고 수집했는지와 어디서, 언제, 누가 검사하고 취급했는지를 적습니다. 여기에 기간마다 누가 보관을 책임졌고 어떻게 보관했는지, 증거를 넘길 때의 시각과 방법, 추적 번호까지 담습니다[3].

## 도구

켜진 맥에서 파일볼트 상태는 macOS에 들어 있는 `fdesetup`으로 확인합니다. 대부분의 명령에 root가 필요해서[5] 아래 예는 `sudo`를 붙였습니다.

```sh
sudo fdesetup status                  # 파일볼트 켜짐/꺼짐
sudo fdesetup status -extended        # 암호화·복호화 진행률과 예상 시간
sudo fdesetup isactive; echo $?       # 켜짐: "true", 종료 코드 0 / 꺼짐: "false", 종료 코드 1
sudo fdesetup list -extended          # 파일볼트를 쓸 수 있는 사용자, 사용자 종류, 복구 키 위탁 상태
sudo fdesetup haspersonalrecoverykey       # 개인 복구 키가 있으면 "true"
sudo fdesetup hasinstitutionalrecoverykey  # 기관 복구 키가 있으면 "true"
```

`fdesetup authrestart`는 파일볼트가 켜진 맥을 첫 잠금 해제 없이 재시작하는 명령이고(`supportsauthrestart`로 지원 여부를 봅니다), 이렇게 인증된 재시작을 하는 동안에는 파일볼트 보호가 약해집니다[5]. 조사 중 이 명령을 포함해 어떤 명령이든 실행했다면 명령과 시각을 현장 기록에 남깁니다. 칩 종류는 앞의 4단계처럼 시스템 정보 앱에서 확인합니다.

## 함정과 한계

라이브 시스템에서 명령을 실행하면 그 자체로 시스템이 바뀝니다. tar나 xcopy처럼 접근 시각을 바꾸는 프로그램은 조심해서 씁니다[3]. 사고가 난 뒤에 감사 로깅을 켜면 증거가 바뀌고 공격자에게 대응 사실이 알려질 수 있으니, 영향을 따져 보고 조치를 기록합니다[1].

원격 지우기는 기기를 찾으면 요청을 취소할 수 있지만("Stop Erase Request") 이때 Apple 계정 암호가 필요하고, 지운 뒤에도 활성화 잠금 (Activation Lock)은 그대로라서 맥을 다시 쓰려면 Apple 계정과 암호가 필요합니다[6]. 지운 뒤에도 맥이 전에 쓰던 Wi-Fi 근처에 있으면 위치가 잡힐 수 있습니다[6]. 지우기 요청이 들어왔다는 사실이 맥 안의 어느 기록에 남는지는 실제 기기로 확인해야 합니다.

해시 알고리즘에 관한 SP 800-86의 기준은 2006년 것이라, 지금 조직에서 어떤 알고리즘을 쓸지는 그 조직의 지침과 법무 자문을 따릅니다. 또 SP 800-61의 최신판인 Rev. 3는 사고 대응을 CSF 2.0 기능에 맞춰 정리한 문서이고 Rev. 2를 대체했으니, 사고 대응 단계를 인용할 때는 어느 판인지 밝힙니다.

## 결과를 어떻게 해석하나

증거는 증거능력 (Admissible), 진정성 (Authentic), 완전성 (Complete), 신뢰성 (Reliable), 설득력 (Believable)을 갖춰야 합니다[3]. 원본과 사본의 해시가 같다는 기록은 확보 시점에 사본이 원본과 같았다는 뜻이고, 그 뒤의 보관 연속성 기록이 사본이 그 뒤로도 바뀌지 않았다는 근거를 보탭니다. 해시가 같다는 사실만으로는 원본에 담긴 내용이 누구의 행위인지까지 알 수 없습니다.

라이브 대응 중에는 조사자의 조치도 맥에 흔적을 남깁니다. 모든 조치와 그 시각을 UTC와의 차이와 함께 적어 두면, 분석 단계에서 타임라인에 나온 사건 가운데 조사자가 만든 것을 가려낼 근거가 됩니다. 보고서에는 현장 판단(네트워크를 뗀 시각, 끄지 않은 이유, 종료 방법)과 그 근거를 함께 적고, 기록으로 확인되는 만큼만 씁니다.

## 참고 문헌

1. NIST SP 800-86, Guide to Integrating Forensic Techniques into Incident Response (Kent·Chevalier·Grance·Dang, 2006-08) — https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf
2. NIST SP 800-61 Rev. 3, Incident Response Recommendations and Considerations for Cybersecurity Risk Management: A CSF 2.0 Community Profile (2025-04) — https://csrc.nist.gov/pubs/sp/800/61/r3/final
3. RFC 3227 / BCP 55, Guidelines for Evidence Collection and Archiving (2002-02) — https://www.rfc-editor.org/rfc/rfc3227
4. Apple Support, Mac computers with the Apple T2 Security Chip — https://support.apple.com/en-us/103265
5. fdesetup(8) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/fdesetup.8.html
6. iCloud User Guide, Erase a device in Find Devices on iCloud.com — https://support.apple.com/guide/icloud/erase-a-device-mmfc0ef36f/icloud
