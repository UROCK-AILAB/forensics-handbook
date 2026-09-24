# 랜섬웨어는 언제 어떻게 퍼졌나 (Ransomware)

이 페이지는 랜섬웨어 사고에서 암호화가 언제 시작해 어디로 퍼졌는지, 그 앞에 어떤 단계가 있었는지를 거슬러 찾는 순서를 다룹니다. 암호화 시각을 먼저 잡습니다. 그다음 복구 방해와 보안 프로그램 끄기, 랜섬웨어 실행 방법, 측면 이동, 초기 접근 순으로 올라갑니다. 단계마다의 세부는 각 시나리오·아티팩트 페이지에 있습니다.

"(관찰)" 을 붙인 내용은 Windows 11 Home(빌드 26200) 분석 PC 한 대에서 이벤트 공급자 정의를 직접 조회한 것입니다(확인 범위: Win11 Home 한 대). 한 대에서 본 것이므로 기본값으로 일반화하지 않습니다.

## 조사 질문

- 파일 암호화는 언제 시작해 언제 끝났습니까?
- 어느 PC 가 처음 암호화됐습니까? 랜섬웨어는 어디서, 어느 계정으로, 어떤 방법으로 실행됐습니까?
- 암호화 전에 복구를 막거나 보안 프로그램을 끈 흔적이 있습니까?
- 처음 침입한 때는 언제이고, 처음 침입한 PC 는 어디입니까?
- 암호화 전에 자료를 밖으로 빼돌렸습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | PC 마다 버전과 빌드를 [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 적습니다. |
| 시간대와 시계 | PC 여러 대의 기록을 합칩니다. PC 마다 [시간대 설정](../../02-artifacts/system-account/time-zone.md) 과 시계 오차를 적습니다. 맞추는 법은 [시간대·시계 오차 보정](../../03-techniques/analysis/timeline/time-normalization.md) 에 있습니다. |
| 수집 범위 | 암호화된 PC 여러 대, 파일 서버, 도메인 컨트롤러를 봅니다. 각 PC 에서 $MFT, $UsnJrnl:$J, $LogFile, 이벤트 로그, 레지스트리 하이브를 확보합니다. 섀도 복사본이 남아 있는지도 적습니다. |
| $UsnJrnl 추출 방법 | $UsnJrnl:$J 를 어떻게 뽑았는지 적습니다. 뽑는 방법에 따라 크기와 해시가 달라집니다(현장 관찰). 까닭은 [USN 변경 저널](../../02-artifacts/filesystem/usnjrnl.md) 에 있습니다. |
| 감사 정책·Sysmon | 프로세스 생성 기록과 명령줄은 감사 정책과 Sysmon 설정에 따라 남기도 하고 안 남기도 합니다. 기록이 없다고 해서 명령이 없었다고 읽지 않습니다. [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 확인합니다. |

## MITRE 가 설명하는 암호화와 복구 방해

**T1486 Data Encrypted for Impact.**

공격자는 대상 시스템이나 네트워크의 많은 시스템에서 데이터를 암호화해 쓸 수 없게 만듭니다[1]. 흔히 암호화되는 파일은 오피스 문서, PDF, 이미지, 동영상, 음성, 텍스트, 소스 코드이고, 이름이 바뀌거나 특정 표시가 붙는 경우가 많습니다[1]. 시스템 파일, 디스크 파티션, MBR 을 암호화하는 경우도 있고, ESXi 같은 하이퍼바이저의 가상 머신을 암호화하기도 합니다[1].

퍼뜨릴 때는 유효 계정 (Valid Accounts), 운영체제 자격 증명 덤프 (OS Credential Dumping), SMB·Windows 관리 공유 (SMB/Windows Admin Shares) 같은 다른 기법을 씁니다[1]. 바탕 화면 바꾸기 같은 내부 훼손이나, 연결된 프린터로 랜섬노트를 뿌리는 일도 듭니다[1].

탐지 문장은 드문 확장자로 파일 쓰기가 짧은 시간에 몰리는 모양을 보라고 하며, 뒤이어 랜섬노트 생성, 레지스트리 변경, 섀도 복사본 삭제가 나옵니다[1]. 이때 vssadmin·wbadmin·cipher·PowerShell 같은 명령줄 도구를 흔히 씁니다[1].

**T1490 Inhibit System Recovery.**

공격자는 망가진 시스템을 되살리는 데 쓰는 기본 데이터와 서비스를 지우거나 끕니다[2]. 탐지 문장은 기본 유틸리티(vssadmin·wbadmin·diskshadow·bcdedit·REAgentC·wmic)를 섀도 복사본 삭제, 복구 끄기, 백업 카탈로그 삭제 인자로 부르는 프로세스 사슬을 보라고 하지만, MITRE 페이지에는 윈도 이벤트 ID 나 레지스트리 키가 없습니다[2].

**명령줄에서 찾을 모양.** 아래 명령은 MITRE T1490 페이지에 적힌 것입니다[2]. 프로세스 생성 기록(4688·Sysmon 1)의 명령줄에서 이 모양을 찾습니다. "하는 일" 열은 명령과 인자를 보고 이 위키가 붙인 설명입니다.

| 명령줄 | 하는 일 |
|---|---|
| `vssadmin.exe delete shadows /all /quiet` | 섀도 복사본 삭제 |
| `wmic shadowcopy delete` | 섀도 복사본 삭제 |
| `diskshadow delete shadows all` | 섀도 복사본 삭제 |
| `wbadmin.exe delete catalog -quiet` | 백업 카탈로그 삭제 |
| `bcdedit.exe /set {default} bootstatuspolicy ignoreallfailures` | 복구 끄기 |
| `bcdedit /set {default} recoveryenabled no` | 복구 끄기 |
| REAgentC | Windows 복구 환경 (WinRE) 끄기 |

**분석 PC 에서 본 관련 이벤트 정의.**

공급자 Microsoft-Windows-Backup 의 524 는 Application 채널의 정보 이벤트이고, 메시지는 "The system catalog has been deleted." 입니다(관찰). `wbadmin delete catalog` 를 실행하면 524 가 남는지는 이번에 확인하지 못했습니다.

Microsoft-Windows-Windows Defender 운영 로그에는 실시간 보호 끄기(5001), 설정 변경(5007), 스파이웨어 검사 끄기(5010), 바이러스 검사 끄기(5012) 메시지가 정의돼 있습니다(관찰). 디펜더 끄기·설정 변경 이벤트를 읽는 법은 [보안 프로그램을 끄거나 지웠나](../activity/anti-forensics/defense-evasion.md) 에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | $MFT·$UsnJrnl·$LogFile | 암호화된 파일과 랜섬노트가 생긴 시각, 이름 바꾸기·쓰기가 몰린 구간 | [마스터 파일 테이블](../../02-artifacts/filesystem/mft.md) · [USN 변경 저널](../../02-artifacts/filesystem/usnjrnl.md) · [NTFS 트랜잭션 로그](../../02-artifacts/filesystem/logfile.md) · [파일시스템 타임라인](../../03-techniques/analysis/timeline/filesystem-timeline-mft-usnjrnl-logfile.md) |
| 2 | 프로세스 생성 | 복구 방해 명령, 랜섬웨어 실행 명령줄 | [프로세스 생성](../../02-artifacts/event-logs/4688.md) · [프로세스 생성 (Sysmon 1)](../../02-artifacts/event-logs/sysmon/1.md) |
| 3 | 보안 프로그램 기록 | 디펜더 끄기와 탐지 | [Windows Defender 탐지](../../02-artifacts/event-logs/1116-1117.md) · [보안 프로그램을 끄거나 지웠나](../activity/anti-forensics/defense-evasion.md) |
| 4 | 이벤트 로그 삭제 | 로그를 지운 흔적 | [이벤트 로그 삭제](../../02-artifacts/event-logs/1102-104.md) · [이벤트 로그를 지웠나](../activity/anti-forensics/log-clearing.md) |
| 5 | 섀도 복사본 | 남은 복사본과 그 안의 예전 파일 | [볼륨 섀도 복사본 구조](../../01-foundations/disk-volume/volume-shadow-copy.md) · [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 6 | 서비스 설치·예약 작업·공유 폴더 접근 | 원격 서비스·예약 작업·공유로 퍼뜨린 흔적 | [서비스 설치](../../02-artifacts/event-logs/7045-4697.md) · [예약 작업 이벤트](../../02-artifacts/event-logs/taskscheduler-4698.md) · [공유 폴더 접근](../../02-artifacts/event-logs/5140-5145.md) |
| 7 | 측면 이동·자격 증명 탈취 | 암호화 앞 단계 | [계정 탈취와 측면 이동](credential-theft-lateral-movement/index.md) · [다른 PC 에서 원격 실행했나](credential-theft-lateral-movement/psexec-wmi-winrm.md) |
| 8 | 유출 흔적 | 암호화 전에 빼돌렸는지 | [자료를 밖으로 빼돌렸나](../exfiltration/data-exfiltration/index.md) |

1 에서 시각의 기준점을 잡고, 2\~6 으로 암호화 직전과 퍼진 방법을 봅니다. 7\~8 은 그보다 앞선 단계입니다.

## 공개 사례: 침입부터 암호화까지

The DFIR Report 가 공개한 Hive 랜섬웨어 사례(2023-09-25)입니다[3]. 첫 접근에서 랜섬웨어 실행까지 61시간이 걸렸습니다[3].

| 단계 | 사례의 내용[3] | 이 위키에서 볼 곳 |
|---|---|---|
| 초기 접근 | 메일 링크로 받은 실행 파일 | [악성코드는 어디서 들어왔나](initial-access.md) |
| 원격 관리 도구 설치 | 정상 원격 관리 도구 설치 | [원격 제어 프로그램으로 누가 조작했나](remote-access-tool-abuse.md) |
| 발견 | systeminfo·nltest·AD 조회·3389 포트 훑기 | — |
| 자격 증명 탈취 | LSASS 덤프(사용자 정의 Mimikatz, m2.exe) | [계정 탈취와 측면 이동](credential-theft-lateral-movement/index.md) |
| 측면 이동 | RDP·WMIEXEC·원격 서비스 | [원격 데스크톱 침입 확인](rdp-intrusion.md) · [다른 PC 에서 원격 실행했나](credential-theft-lateral-movement/psexec-wmi-winrm.md) |
| 유출 | Rclone 으로 SFTP 유출(약 1.5시간) | [자료를 밖으로 빼돌렸나](../exfiltration/data-exfiltration/index.md) |
| 암호화 | 랜섬웨어 실행 | 이 페이지 |

**측면 이동 흔적.**

WMIEXEC 는 wmiprvse.exe 가 부모인 `cmd.exe /Q /c … 1> \\127.0.0.1\{공유}\_{시각} 2>&1` 모양의 명령줄로 남았고, 이 흔적은 공유 개체 접근 확인 이벤트 5145 로 잡혔습니다[3]. 원격 서비스로 DLL 을 돌린 흔적은 5145 와 7045 로 잡혔습니다[3].

**암호화 직전.**

관리자 비밀번호가 바뀌고 약 1시간 뒤 랜섬웨어가 실행됐습니다[3]. 공격자는 비콘과 cmd.exe 에서 랜섬웨어를 손으로 실행했고, 인자는 `-u {자격 증명}` 모양이었습니다[3]. 또 gpme.msc 로 그룹 정책 개체를 만들고 예약 작업을 넣었지만, 작업을 사용자 구성에 넣어 도메인 전체 배포는 실패했고 손으로 실행한 곳만 암호화됐습니다[3].

랜섬웨어 파일은 `C:\windows_x64_encrypt.exe` 와 `C:\ProgramData\windows_x64_encrypt.exe` 에 있었고, 공격자는 그룹 정책 배포용으로 네트워크 공유에도 같은 파일을 두었습니다[3]. 보고서에 적힌 복구 방해 명령은 아래와 같으며, 위 MITRE 표의 명령과 모양이 같습니다[3].

```
"C:\Windows\System32\wbem\WMIC.exe" shadowcopy delete
"C:\Windows\System32\vssadmin.exe" delete shadows /all /quiet
"C:\Windows\System32\bcdedit.exe" /set {default} recoveryenabled No
"C:\Windows\System32\bcdedit.exe" /set {default} bootstatuspolicy ignoreallfailures
```

보고서가 든 랜섬노트 경로의 예는 `C:\Users\Default\HOW_TO_DECRYPT.txt` 이고, 증거로 쓴 이벤트는 4688, 7045, 5145, Sysmon 1·8·10·11·13·17·18·23, PowerShell 4104 입니다[3].

## 분석 흐름

1. **암호화 시작·끝 시각을 잡습니다.** 암호화된 파일과 랜섬노트의 $MFT 시각을 봅니다. $UsnJrnl 에서 이름 바꾸기와 쓰기가 몰린 구간을 찾습니다. 순서는 [파일시스템 타임라인](../../03-techniques/analysis/timeline/filesystem-timeline-mft-usnjrnl-logfile.md) 을 따릅니다.
2. **암호화 직전을 봅니다.** 복구 방해 명령(vssadmin·wmic·bcdedit·wbadmin), 보안 프로그램 끄기(디펜더 5001·5007 등), 이벤트 로그 삭제를 찾습니다.
3. **랜섬웨어 실행 파일과 실행 방법을 찾습니다.** 어느 계정이, 어느 경로의 파일을, 어떤 방법(손으로 실행·원격 서비스·예약 작업·그룹 정책)으로 실행했는지 적습니다. 어느 PC 에서 먼저 실행됐는지도 적습니다.
4. **앞 단계를 거슬러 올라갑니다.** 측면 이동([다른 PC 에서 원격 실행했나](credential-theft-lateral-movement/psexec-wmi-winrm.md) · [원격 데스크톱 침입 확인](rdp-intrusion.md)), 자격 증명 탈취([계정 탈취와 측면 이동](credential-theft-lateral-movement/index.md)), 지속성([악성코드 지속성(자동실행) 찾기](persistence.md)), 초기 접근([악성코드는 어디서 들어왔나](initial-access.md)) 순으로 봅니다.
5. **유출 여부를 따로 봅니다.** 공개 사례에서는 암호화 전에 유출이 있었습니다[3]. [자료를 밖으로 빼돌렸나](../exfiltration/data-exfiltration/index.md) 를 따릅니다.
6. **PC 여러 대의 시각을 맞춥니다.** [여러 아티팩트 합친 타임라인](../../03-techniques/analysis/timeline/super-timeline.md) 에 올립니다. "처음 암호화된 PC" 와 "처음 침입한 PC" 를 따로 적습니다.

## 흔한 오판

1. **암호화 시각을 침입 시각으로 씁니다.** 공개 사례에서는 첫 접근과 랜섬웨어 실행 사이가 61시간이었습니다[3].
2. **암호화된 PC 를 시작점으로 봅니다.** 공격자는 관리 공유와 유효 계정으로 다른 PC 에서 퍼뜨립니다[1][3].
3. **섀도 복사본이 없으니 원래 꺼져 있었다고 봅니다.** 복구 방해 명령으로 지웠을 수 있습니다[2]. 명령 실행 흔적을 찾습니다.
4. **파일 수정 시각을 암호화 시각으로 씁니다.** 랜섬웨어가 파일 시각을 어떻게 남기는지는 이번 자료로 확인하지 못했습니다. 그래서 $MFT 시각 하나로 정하지 않습니다. $UsnJrnl 과 $LogFile 로 교차 확인합니다.
5. **유출은 없었다고 봅니다.** 암호화 전에 유출한 사례가 있습니다[3].
6. **$UsnJrnl 의 가장 오래된 기록 앞에는 아무 일도 없었다고 봅니다.** 대량 암호화가 저널의 오래된 기록을 밀어내는지는 이번 자료로 확인하지 못했습니다. 저널에 남은 가장 오래된 기록의 시각을 먼저 적고, 그보다 앞선 일은 다른 기록으로 봅니다.

## 보고서 문장 예

- 쓰지 않을 문장: "랜섬웨어는 ○○ 에 ○○ PC 에서 시작해 네트워크 전체로 퍼졌습니다."
- 쓸 문장: "PC ○○ 의 $UsnJrnl 에서 확장자 ○○ 로 이름을 바꾼 레코드는 ○○(UTC) 에 처음 나오고 ○○(UTC) 에 마지막으로 나옵니다. 같은 PC 의 보안 로그에 ○○(UTC) 의 4688 이 있고, 명령줄은 `vssadmin.exe delete shadows /all /quiet` 입니다. 이 기록은 이 구간에 이 PC 에서 파일 이름 바꾸기가 몰렸고, 그 전에 섀도 복사본 삭제 명령이 실행됐음을 보여 줍니다. 이 PC 가 처음 침입한 PC 인지는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [USN 변경 저널](../../02-artifacts/filesystem/usnjrnl.md) · [마스터 파일 테이블](../../02-artifacts/filesystem/mft.md) · [NTFS 트랜잭션 로그](../../02-artifacts/filesystem/logfile.md) · [파일시스템 타임라인](../../03-techniques/analysis/timeline/filesystem-timeline-mft-usnjrnl-logfile.md) — 암호화 시각을 잡습니다.
- [볼륨 섀도 복사본 구조](../../01-foundations/disk-volume/volume-shadow-copy.md) · [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 남은 복사본을 봅니다.
- [프로세스 생성](../../02-artifacts/event-logs/4688.md) · [프로세스 생성 (Sysmon 1)](../../02-artifacts/event-logs/sysmon/1.md) · [서비스 설치](../../02-artifacts/event-logs/7045-4697.md) · [예약 작업 이벤트](../../02-artifacts/event-logs/taskscheduler-4698.md) · [공유 폴더 접근](../../02-artifacts/event-logs/5140-5145.md) — 실행과 배포 방법을 봅니다.
- [Windows Defender 탐지](../../02-artifacts/event-logs/1116-1117.md) · [이벤트 로그 삭제](../../02-artifacts/event-logs/1102-104.md) · [보안 프로그램을 끄거나 지웠나](../activity/anti-forensics/defense-evasion.md) · [이벤트 로그를 지웠나](../activity/anti-forensics/log-clearing.md) — 암호화 직전의 방해 흔적입니다.
- [계정 탈취와 측면 이동](credential-theft-lateral-movement/index.md) · [다른 PC 에서 원격 실행했나](credential-theft-lateral-movement/psexec-wmi-winrm.md) · [자료를 밖으로 빼돌렸나](../exfiltration/data-exfiltration/index.md) — 암호화 앞 단계입니다.
- [여러 아티팩트 합친 타임라인](../../03-techniques/analysis/timeline/super-timeline.md) · [시간대·시계 오차 보정](../../03-techniques/analysis/timeline/time-normalization.md) — PC 여러 대의 시각을 맞춥니다.

## 참고 문헌

1. MITRE ATT&CK, "Data Encrypted for Impact, Technique T1486" (v1.5, 2026-05-12 수정) — https://attack.mitre.org/techniques/T1486/
2. MITRE ATT&CK, "Inhibit System Recovery, Technique T1490" (v1.6, 2026-05-12 수정) — https://attack.mitre.org/techniques/T1490/
3. The DFIR Report, "From ScreenConnect to Hive Ransomware in 61 hours" (2023-09-25) — https://thedfirreport.com/2023/09/25/from-screenconnect-to-hive-ransomware-in-61-hours/
