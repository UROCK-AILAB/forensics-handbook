---
title: "Linux 포렌식 보고서"
parent: "기법 · 보고"
nav_order: 1020
---

# Linux 포렌식 보고서 (Forensic Report)

수집 기록과 분석 도구 출력에서 확인한 사실만 옮기고, 시각 기준과 수집 범위의 한계를 함께 밝혀 적는 문서입니다.

## 언제 쓰나

포렌식 보고서 (forensic report) 는 조사 결과를 다른 사람에게 넘길 때 씁니다. 내부 사고 보고, 법적 절차, 다른 분석가가 같은 결론을 다시 따라가 보는 재현이 모두 여기에 들어갑니다. 읽는 사람은 원본 검체를 직접 열어 보지 않는 경우가 많아서, 보고서의 문장 하나하나가 어느 파일의 어느 줄에서 나왔는지, 그 시각이 어떤 기준인지 보고서만 보고도 알 수 있어야 합니다.

이 쪽은 Linux 수집 도구와 분석 도구가 남기는 기록 가운데 보고서에 옮길 것과, 옮길 때 틀리기 쉬운 점을 다룹니다. 수집 순서와 수집 전에 정할 일은 [조사 절차](../acquisition/investigation-process.md)에, 수집 방법 자체는 [라이브 응답 수집](../acquisition/live-response.md)·[디스크 이미징](../acquisition/disk-imaging.md)·[메모리 수집](../acquisition/memory-acquisition.md)에 있습니다. 보고서의 뼈대(요약·범위·결론 순서)처럼 운영체제와 상관없는 부분은 [Windows 분석 보고서 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/reporting/forensic-report.html)과 [macOS 포렌식 보고서](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/reporting/forensic-report.html)를 함께 봅니다.

## 절차

1. **수집 기록을 그대로 옮깁니다.** UAC (Unix-like Artifacts Collector) 는 수집이 끝나면 결과물 옆에 `기본이름.log` 수집 기록을 따로 만들고, 이 파일은 결과물(tar·zip) 밖에 있습니다[1]. 수집 기록에는 사건 정보(`Case Number`, `Evidence Number`, `Description`, `Examiner`, `Notes`), 대상 시스템(`Operating System`, `System Architecture`, `Hostname`), 수집 정보(`Mount Point`, `Acquisition Started`, `Acquisition Finished`), 결과물 이름과 형식, 결과물 해시가 들어갑니다[1]. 절 이름과 전체 모양은 [라이브 응답 수집](../acquisition/live-response.md)에 있습니다. Velociraptor 오프라인 수집기는 수집 컨테이너(zip) 옆에 로그 파일을 만들고, 로그 끝부분에 `Container hash` 라는 메시지로 컨테이너의 SHA-256 을 남깁니다[2]. E01 이미지는 `ewfacquire` 에 넣은 사건 번호·설명·검사자·증거 번호·메모가 이미지 안에 들어가고, `-l` 로 지정한 로그 파일에 획득 오류와 해시가 남습니다[3]. 이 값들을 보고서의 "수집" 절에 옮기고, 원본 기록 파일도 부록으로 붙입니다.

2. **수집 도구의 실행 로그에서 설정을 옮깁니다.** UAC 는 수집하는 동안 `uac.log` 를 쓰고, 끝나면 이 파일을 결과물 안 맨 앞에 넣습니다[1]. 줄마다 `date "+%Y-%m-%d %H:%M:%S %z"` 시각, 수준(`DBG`, `INF`, `ERR`, `CMD`), 메시지가 붙습니다[1]. `INF` 줄에는 `Command line:`, `Operating system:`, `Hostname:`, `Time zone:`, `Mount point:`, `Running as:`, `Hash algorithm:`, `Exclude file systems:`, `Enable modifiers:` 가 남고, 끝에 `Artifacts collection completed in N seconds` 가 남습니다[1]. 실행한 명령은 모두 `CMD` 줄로 남고, 오류 출력이 있으면 줄 끝에 ` 2> 오류 내용` 이 붙습니다[1]. 만든 예시 한 줄은 `2026-09-24 10:15:03 +0900 INF Running as: root` 모양입니다. 보고서의 "사용 도구·설정" 절은 이 줄들을 근거로 씁니다.

3. **해시를 다시 맞춥니다.** 분석 사본을 옮긴 뒤에는 수집 때 계산한 해시와 지금 사본의 해시를 다시 맞춰 보고, 그 결과를 보고서에 적습니다. coreutils 의 `sha256sum --check` 같은 `--check` 모드는 앞서 만든 체크섬 목록을 읽어 파일마다 맞는지 한 줄씩 알려 줍니다[4]. Velociraptor 컨테이너는 `Container hash` 값과 `sha256sum` 결과를 견주면 됩니다[2]. E01 은 `ewfverify` 가 이미지에 저장된 해시 종류를 다시 계산해 대조하고, 저장된 해시가 없으면 MD5 를 씁니다[3]. 수집 때 MD5·SHA-1 만 계산했다면 이 단계에서 SHA-256 을 더 계산해 함께 적으면 됩니다(아래 "함정과 한계" 참고).

4. **대상 호스트의 기본 정보를 적습니다.** 배포판과 버전, 호스트 이름, 시간대를 보고서 앞쪽에 둡니다. 각 값을 어느 파일에서 읽었는지는 [배포판과 버전 (os-release)](../../02-artifacts/system-info/os-release.md)과 [호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md)에 있습니다. UAC 로 수집했다면 `uac.log` 의 `Operating system:`, `Hostname:`, `Time zone:` 줄과 견줘 봅니다[1].

5. **시각 기준을 하나로 정합니다.** 보고서 안 모든 시각을 한 기준(보통 UTC)으로 쓰고, 표 머리나 본문 첫머리에 그 기준을 밝힙니다. 원본 기록마다 저장된 기준이 달라서, 현지 시각으로 남은 기록은 대상 시간대를 근거로 바꿨다는 사실과 그 시간대를 어디서 얻었는지를 함께 적습니다. 기록별 기준은 아래 "결과를 어떻게 해석하나" 의 표에 모았습니다.

6. **분석 도구와 버전, 설정을 적습니다.** plaso 의 `pinfo` 는 저장 파일에 담긴 도구 버전(`version`), 실행한 명령줄(`cmd_line`), 쓴 파서 목록(`parsers`), 전처리에서 정한 시간대(`configured_zone`, `Time zone`)를 보여 줍니다[5]. 이 값을 그대로 옮기면 다른 분석가가 같은 조건으로 다시 돌릴 수 있습니다. dissect 로 만든 레코드는 `rdump` 로 CSV·JSON 으로 바꿔 부록에 붙일 수 있습니다[9].

7. **사실마다 원본 위치를 답니다.** 보고서의 사실 하나에 원본 파일 경로, 줄 번호나 레코드 위치(저널이면 커서), 그 값을 보여 준 도구 출력을 짝지어 적습니다. UAC 결과물 안의 경로는 마운트 지점이 `[root]/` 로 바뀌어 있으므로, 보고서에는 대상 시스템의 원래 경로로 되돌려 적습니다[1].

8. **계정은 번호와 이름을 함께 적습니다.** UID 와 함께, 그 UID 에 이름을 붙인 근거(어느 시점의 어느 `/etc/passwd`, 또는 enriched 감사 로그의 보충 값)를 적습니다. UID 와 이름을 잇는 원리는 [UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md)에 있습니다.

9. **한계를 따로 절로 씁니다.** 수집 범위 밖에 있던 것(날짜 필터, 제외한 파일 시스템, 권한 부족), 로그 순환으로 이미 사라진 구간, 수집 중에 시스템을 바꾼 동작을 모읍니다. 항목별 근거는 "함정과 한계" 에 있습니다.

10. **문장은 기록이 말하는 만큼만 씁니다.** 예시는 "결과를 어떻게 해석하나" 의 보고서 문장에 있습니다.

## 도구

| 도구 | 보고서에 옮길 것 | 참고 |
|---|---|---|
| UAC | 수집 기록 `기본이름.log`, 결과물 안 `uac.log`, `-H` 로 만든 `hash_list.md5`·`hash_list.sha1`·`hash_list.sha256` | 결과물 해시 기본값은 `[md5, sha1]`[1] |
| Velociraptor 오프라인 수집기 | 로그의 `Container hash`, 컨테이너 안 `results/` 업로드 메타데이터, `log.json`, `collection_context.json` | 업로드 메타데이터의 파일 시각은 UTC(`Z`)[2] |
| libewf `ewfacquire`·`ewfverify`·`ewfinfo` | 사건 정보, 획득 로그의 해시와 오류, 검증 결과 | 기본 해시는 MD5, `-d` 로 sha1·sha256 추가[3] |
| coreutils `sha256sum`·`cksum` | `--check` 결과 | untagged·tagged·BSD 역순 세 형식을 읽음[4] |
| plaso `log2timeline`·`pinfo`·`psort` | 도구 버전·명령줄·파서·시간대, 타임라인 출력 | `psort` 기본 출력 시간대는 UTC[5] |
| dissect `target-query`·`rdump` | 레코드 출력(CSV·JSON) | 시간대를 못 정하면 UTC 로 가정[8] |
| audit `ausearch` | `--format` 의 raw·default·interpret·csv·text 출력 | `-i` 의 이름 풀이 조건에 주의[11] |

타임라인을 만드는 방법은 [타임라인 만들기](../analysis/timeline.md)에, 해시로 알려진 파일을 가리는 방법은 [알려진 파일 대조와 YARA](../analysis/hash-yara.md)에 있습니다.

## 함정과 한계

**UAC 결과물 이름의 시각은 UTC 가 아닙니다.** 기본 이름 `uac-%hostname%-%os%-%timestamp%` 의 `%timestamp%` 는 `date "+%Y%m%d%H%M%S"` 값이라 대상 시스템의 현지 시각이고 UTC 와의 차이가 붙지 않습니다[1]. 수집 기록의 `Acquisition Started`·`Acquisition Finished` 는 `date "+%a %b %d %H:%M:%S %Y %z"` 형식이라 차이(`+0900` 등)가 붙습니다[1]. `%a`·`%b` 는 로캘의 요일·월 약어라서 로캘에 따라 영어가 아닐 수 있습니다[4]. 만든 예시는 `Thu Sep 24 10:15:02 2026 +0900` 입니다. 수집 시각은 파일 이름이 아닌 수집 기록에서 옮깁니다.

**UAC 기본 설정에는 SHA-256 이 없습니다.** `uac.conf` 의 `hash_algorithm` 기본값은 `[md5, sha1]` 이고, 받는 값은 md5·sha1·sha256 입니다[1]. 기본 설정으로 수집했다면 수집 기록의 `[Computed Hashes]` 절에 `SHA256 checksum:` 줄이 없습니다[1]. `ewfacquire` 도 `-d` 를 주지 않으면 MD5 만 계산합니다[3]. MD5·SHA-1 은 우연한 손상을 찾는 데는 CRC 보다 믿을 만하지만 의도적인 변조에는 안전하지 않고, 더 안전한 해시로는 sha2·sha3·blake2b 가 있습니다[4].

**수집 기록에 zip 암호가 평문으로 남습니다.** zip 형식에 암호를 주면 UAC 는 수집 기록에 `Password: "…"` 줄을 씁니다[1]. 수집 기록을 보고서 부록에 그대로 붙이면 암호가 함께 나가므로, 이 줄을 가리고 가렸다는 사실을 적습니다.

**전송 뒤 지우기를 켰다면 보관 위치를 적어야 합니다.** `--delete-local-on-successful-transfer` 를 주면 SFTP·S3 같은 원격 저장소로 전송이 끝난 뒤 로컬 결과물과 수집 기록을 지웁니다[1]. 이때 보고서의 보관 사본 위치는 전송받은 쪽입니다.

**결과 파일이 없다고 명령을 안 돌린 것은 아닙니다.** UAC 는 명령 결과가 비어 있으면 결과 파일을 지웁니다[1]. 이 삭제는 디버그 모드에서만 `DBG` 줄(`Empty output file: …`)로 남습니다[1]. 명령을 실행했는지는 `uac.log` 의 `CMD` 줄로 확인하고, 결과 파일이 없으면 "실행했고 출력이 비어 있었다" 로 적습니다.

**수집 중에 시스템을 바꿨는지 확인합니다.** 상태를 바꾸는 항목(modifier)은 `--enable-modifiers` 를 줄 때만 돌고, `uac.log` 에 `Enable modifiers: true` 또는 `false` 가 남습니다[1]. 켰다면 ftrace 설정과 `/proc` 위 마운트를 바꾼 사실을 보고서에 적습니다. 바꾸는 내용은 [라이브 응답 수집](../acquisition/live-response.md)에 있습니다.

**수집 범위 밖은 "없다" 가 아니라 "보지 않았다" 입니다.** `--start-date`·`--end-date` 로 날짜를 걸렀다면 그 기간 밖 파일은 수집하지 않았고, 기본 설정에서 이 필터는 mtime·ctime 만 봅니다[1]. 제외 파일 시스템 기본 목록은 `9p, afs, autofs, cifs, davfs, fuse, kernfs, nfs, nfs4, rpc_pipefs, smbfs, sysfs` 라서 네트워크 공유는 기본으로 빠집니다[1]. 이런 조건을 한계 절에 적습니다.

**ZIP 안 파일 시각을 원본 시각으로 옮기지 않습니다.** ZIP 형식은 파일마다 시각을 하나만, 1초 단위로 담습니다[2]. Velociraptor 는 원래 파일 시각을 `results/` 의 JSON 메타데이터(`Created`, `Changed`, `Modified`, `LastAccessed`)에 적고, ZIP 안 시각은 일부 파일에만 되는 대로 남깁니다[2]. 보고서의 파일 시각은 메타데이터에서 옮깁니다.

**도구마다 시간대를 정하는 규칙이 다릅니다.** plaso 는 `/etc/localtime` 이 링크면 `zoneinfo/` 뒤의 이름을 쓰고, 복사본이면 tzfile 에서 2017-01-01 기준 약어(예: `CET`)를 얻은 뒤, `/etc/timezone` 에 IANA 이름이 있으면 그 이름으로 덮습니다[6]. dissect 는 `/etc/timezone` 을 먼저 보고, 없으면 `/etc/localtime` 의 링크 대상, 하드 링크 짝, 크기와 SHA-1 이 같은 `zoneinfo` 파일 순으로 찾으며, RHEL 의 `posix` 로 시작하는 파일은 건너뜁니다[8]. 그래도 못 정하면 "Could not determine timezone of target, falling back to UTC for datetime helpers" 경고를 내고 UTC 로 가정합니다[8]. 같은 검체에서 두 도구가 다른 시간대를 쓸 수 있으므로, 보고서에는 어느 도구의 판정을 썼는지 적습니다. 시간대 파일의 해석은 [호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md)에 있습니다.

**`psort` 출력에는 시간대 칸을 남깁니다.** `psort` 는 기본으로 UTC 로 내보내고, dynamic·l2tcsv 같은 일부 출력 형식은 `--output-time-zone` 으로 시간대를 바꿀 수 있습니다[5]. 표에서 `timezone`(`zone`) 칸을 빼면 읽는 사람이 현지 시각으로 오해할 수 있습니다. dynamic 출력의 `datetime` 칸이 `0000-00-00T00:00:00.000000+00:00`, `date` 칸이 `0000-00-00`, `time` 칸이 `--:--:--` 이면 시각을 풀지 못한 행입니다[5]. `timestamp_desc`(`type`) 칸은 그 시각이 무엇의 시각인지 알려 주므로 함께 옮깁니다[5].

**dissect 레코드의 `_generated` 는 분석한 시각입니다.** flow.record 레코드에는 `_source`, `_classification`, `_generated`, `_version` 필드가 붙고, `_generated` 는 레코드를 만든 순간의 UTC 시각입니다[9]. 사건 시각으로 옮기지 않습니다.

**`ausearch -i` 의 계정 이름은 분석 PC 기준일 수 있습니다.** 감사 로그가 enriched 형식이 아니면 `-i` 는 분석하는 PC 의 계정 정보로 UID 를 이름으로 바꾸고, 계정 이름이 바뀌었거나 같은 계정이 없으면 틀린 결과가 나올 수 있습니다[11]. enriched 로그면 함께 기록된 보충 값으로 바꿉니다[11]. `log_format` 이 `ENRICHED` 이면 uid·gid·시스템 호출·아키텍처·소켓 주소를 풀어서 함께 적고, upstream 기본 설정 파일의 값은 `ENRICHED` 입니다[11]. 검체의 실제 값은 `/etc/audit/auditd.conf` 에서 확인합니다. `--format text` 는 영어 문장으로 바꿔 주지만 세부를 잃습니다[11].

**저널의 밑줄 없는 필드는 남긴 쪽이 적은 값입니다.** 밑줄로 시작하는 필드(`_PID`, `_UID`, `_COMM` 등)는 저널이 스스로 붙이고 클라이언트가 바꿀 수 없습니다[10]. `SYSLOG_IDENTIFIER`, `SYSLOG_PID`, `SYSLOG_TIMESTAMP` 같은 밑줄 없는 필드는 저널이 값을 검증하지 않습니다[10]. "프로그램 X 가 남겼다" 고 쓸 때는 근거가 `_COMM`·`_EXE` 인지 `SYSLOG_IDENTIFIER` 인지 밝힙니다.

**전통 syslog 의 연도는 도구가 채운 값입니다.** `Jan 22 07:54:32` 모양의 줄에는 연도와 시간대가 없습니다[7]. 분석 도구가 채운 연도는 추정이라고 적고, 추정 방식은 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)를 봅니다.

**E01 사건 정보가 자리 문자열이면 입력하지 않은 것입니다.** `ewfacquire` 의 사건 번호·설명·검사자·증거 번호·메모 기본값은 각각 `case_number`, `description`, `examiner_name`, `evidence_number`, `notes` 라는 글자입니다[3]. 이미지 메타데이터에 이 글자가 있으면 수집 때 값을 넣지 않은 것이라, 보고서에는 수집 일지의 값을 따로 적습니다.

## 결과를 어떻게 해석하나

### 기록별 시각 기준

보고서의 시각을 한 기준으로 맞추기 전에, 원본 기록이 어떤 기준으로 시각을 저장하는지 봅니다. 값의 형식은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)에 있습니다.

| 기록 | 저장된 모양 | 기준 |
|---|---|---|
| 저널 `__REALTIME_TIMESTAMP` | 저널이 받은 시각, 에포크 이후 마이크로초 | UTC[10] |
| 저널 `_SOURCE_REALTIME_TIMESTAMP` | 받은 시각과 다를 때만 있는 가장 이른 신뢰 시각, 마이크로초 | `CLOCK_REALTIME`[10] |
| 저널 `SYSLOG_TIMESTAMP` | syslog 데이터그램에 원래 있던 시각 | 저널이 검증하지 않음[10] |
| 전통 syslog `Jan 22 07:54:32` | 연도·시간대 없음 | 현지 시각[7] |
| RFC 3339 syslog `2020-05-31T00:00:45.698463+00:00` | 연도·마이크로초·UTC 와의 차이 | 차이가 붙은 시각[7] |
| dpkg.log `2016-08-03 15:25:53 install …` | 연도 있음, 차이 없음 | 현지 시각[7] |
| apt `history.log` 의 `Start-Date:`·`End-Date:` | 차이 없음 | 현지 시각[7] |
| bash 기록의 `#` 줄 | 에포크 초(9~10자리) | UTC[7] |
| wtmp·utmp 레코드 | 에포크 초와 마이크로초 | UTC[7] |
| 감사 로그 `msg=audit(1116360555.329:2401771)` | 에포크 초.밀리초, 콜론 뒤는 이벤트 번호 | UTC[11][14] |
| UAC 수집 기록·`uac.log` | `%z` 차이가 붙은 시각 | 수집 대상의 현지 시각[1] |
| UAC 결과물 이름 | `%Y%m%d%H%M%S` | 수집 대상의 현지 시각, 차이 없음[1] |
| Velociraptor 업로드 메타데이터 | 끝에 `Z` | UTC[2] |

위 표의 예시 값은 각 도구 문서와 코드 주석에 있는 예시입니다. 저널과 syslog, 감사 로그의 형식은 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md), [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md), [감사 로그 형식](../../01-foundations/logging/auditd-format.md)에 있습니다. 대상 시스템의 시계 자체가 틀렸을 가능성은 [시각을 조작했나](../../04-scenarios/insider/time-manipulation.md)에서 다룹니다.

### 증명하는 것

- 수집 때 계산한 해시와 지금 사본의 해시가 같으면, 분석한 사본이 수집 때 해시를 계산한 파일과 같다는 것을 보여 줍니다[2][3][4].
- UAC 수집 기록과 `uac.log` 는 언제, 어떤 옵션과 명령으로 수집했는지, 어떤 명령이 오류를 냈는지 보여 줍니다[1].
- `pinfo` 출력은 타임라인을 어떤 도구 버전과 파서, 시간대 설정으로 만들었는지 보여 줍니다[5].

### 증명하지 못하는 것

- 해시는 계산한 순간부터만 보증합니다. 수집 이전에 원본이 온전했다는 것은 해시로 보여 줄 수 없습니다.
- MD5·SHA-1 만 있으면 의도적인 변조에 대한 보증이 약합니다[4].
- 수집 기록의 사건 정보 칸(검사자 이름, 사건 번호 등)은 수집하는 사람이 입력한 값이라 도구가 검증하지 않습니다[1][3].
- 분석 도구가 정한 시간대가 맞았다는 것은 도구 출력만으로 보여 줄 수 없습니다. 약어로 정한 경우와 UTC 로 가정한 경우가 있기 때문입니다[6][8].
- 로그 두 줄 사이의 인과는 기록에 없습니다. 보통 로그에는 어떤 사건이 어떤 사건을 일으켰는지가 빠져 있고, 여러 로그를 잇는 일은 대개 시각에 기대는 느슨한 연결(fuzzy correlation)이라 NTP 같은 시계 동기화에 크게 기댑니다[12].

### 보고서 문장

기록 하나가 답할 수 있는 질문은 필드로 정해집니다. 웹 서버 접근 로그라면 "언제" 는 시각 필드가, "누가" 는 IP·사용자 필드가 답하지만, 사건이 왜·어떻게 일어났는지에 해당하는 인과 정보는 보통 로그에 빠져 있습니다[12]. 보고서 문장도 이 범위 안에서 씁니다. 아래 문장은 모두 만든 예시입니다.

- 쓸 만한 문장: "2026-09-24 01:12:07 UTC 에 기록된 저널 항목(`_UID=0`, 커서는 부록 A)에 198.51.100.23 에서 공개키 인증에 성공했다는 메시지가 있습니다."
- 피할 문장: "공격자가 SSH 로 침입해 파일을 빼냈습니다." 이 문장은 원인과 의도, 사람을 단정합니다. 로그에는 인과가 없고[12], 저널의 밑줄 없는 필드는 남긴 쪽이 적은 값이라서[10] 기록만으로는 여기까지 말할 수 없습니다.
- 현지 시각을 바꿔 옮길 때: "dpkg.log 의 `2026-09-24 10:15:53`(시간대 표시 없음)을 대상 시간대 Asia/Seoul(`/etc/localtime` 링크 대상)로 보고 UTC 2026-09-24 01:15:53 으로 바꿨습니다."
- 수집 한계를 적을 때: "수집은 UAC 로 2026-09-01 이후 수정·변경된 파일만 대상으로 했으며, NFS·CIFS 마운트는 수집 범위에 들지 않았습니다."

"누가 실행했나" 를 쓰는 기준은 [누가 그 명령을 실행했나](../../04-scenarios/attribution/user-attribution.md)에 있습니다. 감사 로그의 `auid` 는 로그인 사용자 ID, `uid` 는 사용자 ID, `ses` 는 로그인 세션 ID 라서[13], sudo 로 계정을 바꾼 뒤의 명령도 처음 로그인한 계정과 이을 수 있습니다. 해석은 [감사 로그 형식](../../01-foundations/logging/auditd-format.md)에 있습니다.

## 함께 볼 페이지

- [조사 절차](../acquisition/investigation-process.md) — 수집 전 기록과 증거 관리
- [라이브 응답 수집](../acquisition/live-response.md) — UAC 수집 기록 절과 modifier 동작
- [디스크 이미징](../acquisition/disk-imaging.md) — E01 획득과 검증
- [타임라인 만들기](../analysis/timeline.md) — 보고서에 붙일 시간순 표
- [호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md) — 시간대 판정의 근거 파일
- [AI 관련 포렌식 보고서](https://urock-ailab.github.io/forensics-handbook/ai/03-techniques/reporting/forensic-report.html), [Android 포렌식 보고서](https://urock-ailab.github.io/forensics-handbook/android/03-techniques/reporting/forensic-report.html), [iOS 포렌식 보고서](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/reporting/forensic-report.html)

## 참고 문헌

1. tclahr, UAC — `uac` 스크립트, `lib/create_acquisition_log.sh`, `lib/usage.sh`, `lib/log_msg.sh`, `lib/run_command.sh`, `lib/command_collector.sh`, `config/uac.conf`. https://github.com/tclahr/uac
2. Velociraptor 문서, "Collection data" (offline collections). https://github.com/Velocidex/velociraptor-docs/blob/master/content/docs/deployment/offline_collections/collection_data/index.md
3. libewf, `manuals/ewfacquire.1`, `manuals/ewfverify.1`, `manuals/ewfinfo.1`. https://github.com/libyal/libewf/tree/main/manuals
4. GNU coreutils, `doc/coreutils.texi` (md5sum·sha1sum 절, cksum `--check`, date 형식). https://github.com/coreutils/coreutils/blob/master/doc/coreutils.texi
5. plaso 문서, `Using-psort.md`, `Output-and-formatting.md`, `Using-pinfo.md`, `Using-log2timeline.md`. https://github.com/log2timeline/plaso/tree/main/docs/sources/user
6. plaso, `plaso/preprocessors/linux.py`. https://github.com/log2timeline/plaso/blob/main/plaso/preprocessors/linux.py
7. plaso, `plaso/parsers/text_plugins/syslog.py`, `dpkg.py`, `apt_history.py`, `bash_history.py`, `plaso/parsers/utmp.py`. https://github.com/log2timeline/plaso/tree/main/plaso/parsers
8. Fox-IT, dissect.target `dissect/target/plugins/os/unix/locale.py`, `datetime.py`. https://github.com/fox-it/dissect.target/tree/main/dissect/target/plugins/os/unix
9. Fox-IT, flow.record `README.md`, `flow/record/base.py`. https://github.com/fox-it/flow.record
10. systemd, `man/systemd.journal-fields.xml`. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
11. linux-audit, audit-userspace `ausearch.8`, `auditd.conf.5`, `init.d/auditd.conf`. https://github.com/linux-audit/audit-userspace
12. Johannes Olegård, Stefan Axelsson, Yuhong Li, "When is logging sufficient? — Tracking event causality for improved forensic analysis and correlation", Forensic Science International: Digital Investigation 52 (2025) 301877 (DFRWS EU 2025). https://doi.org/10.1016/j.fsidi.2025.301877
13. linux-audit, audit-documentation `specs/fields/field-dictionary.csv`. https://github.com/linux-audit/audit-documentation/blob/main/specs/fields/field-dictionary.csv
14. Linux 커널, `kernel/audit.c` (`audit_log_start` 의 `audit(%llu.%03lu:%u)` 머리). https://github.com/torvalds/linux/blob/master/kernel/audit.c
