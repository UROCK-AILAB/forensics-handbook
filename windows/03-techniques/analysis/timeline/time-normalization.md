# 시간대·시계 오차 보정 (Time Normalization)

상위 허브: [타임라인 작성 (Timeline)](index.md)

## 한 줄 요약

출처마다 다른 시각 기준을 하나로 맞추는 일입니다. 먼저 그 시각이 UTC 인지 현지 시각인지 가리고, 현지 시각이면 그 컴퓨터의 시간대 설정으로 UTC 로 바꾸며, 시스템 시계가 바뀐 적이 있는지도 함께 확인합니다.

## 언제 쓰나

여러 출처의 시각을 한 타임라인에 합치기 전에 씁니다. 다른 컴퓨터에서도 쓴 FAT 저장장치의 시각을 읽을 때, 도구가 보여 준 시각이 UTC 인지 분석 PC 의 현지 시각인지 확인할 때, 보고서에 현지 시각을 함께 적을 때, 사건 시간대 앞뒤로 시스템 시계가 바뀌었는지 볼 때도 씁니다.

## 출처마다 시각 기준이 다릅니다

| 출처 | 저장 기준 | 근거 |
|---|---|---|
| NTFS 파일 시각 | UTC | 참고 1 |
| FAT 파일 시각 | 그 컴퓨터의 현지 시각 | 참고 1 |
| USN 레코드의 TimeStamp | UTC FILETIME | 참고 3 |
| 이벤트 로그 XML 의 TimeCreated SystemTime | UTC. 끝에 Z 를 붙여 적음 | 참고 4 |
| CD (CDFS) 파일 날짜 | 현지 시간대에 맞춰 조정해 보여 줌 | 참고 1 |

- NTFS 는 시각을 UTC 로 저장하므로 시간대나 일광 절약 시간 (Daylight Saving Time) 이 바뀌어도 저장된 값은 그대로입니다(참고 1).
- FAT 는 현지 시각으로 저장하므로(참고 1) FAT 시각을 UTC 로 바꾸려면 그 시각을 적은 컴퓨터의 시간대를 알아야 합니다.
- 이벤트 로그의 시각은 `2015-10-09T05:04:29.995794600Z` 처럼 적습니다(참고 4). 끝의 Z 가 UTC 라는 표시입니다(참고 4).
- exFAT 에 시간대를 적는 칸이 있는지는 이 페이지에서 확인하지 못했습니다. 구조는 [FAT·exFAT 구조](../../../01-foundations/disk-volume/fat-exfat.md)를 봅니다.
- 값을 날짜로 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다. 레지스트리·브라우저처럼 다른 출처의 기준은 각 아티팩트 페이지를 봅니다.

Microsoft 문서의 예를 표로 옮기면 아래와 같습니다(참고 1). 워싱턴(PST)에서 오후 3시에 저장한 파일을 뉴욕 컴퓨터에서 본 경우입니다.

| 파일시스템 | 뉴욕 컴퓨터에 보이는 시각 (참고 1) |
|---|---|
| NTFS | 오후 6시 (EST) |
| FAT | 오후 3시 (EST) |

NTFS 는 UTC 를 저장하므로 보는 컴퓨터의 시간대로 다시 바꿔 보여 줍니다. FAT 는 적힌 현지 시각을 그대로 보여 줍니다. 그래서 FAT 쪽 오후 3시를 뉴욕 시각으로 읽으면 실제보다 3시간 이릅니다.

## 시간대 설정 읽기

### Bias 의 뜻

Windows 는 시간대를 TIME_ZONE_INFORMATION 구조체로 나타냅니다(참고 2). 시각 계산에는 아래 칸을 씁니다.

| 칸 | 자료형 | 뜻 (참고 2) |
|---|---|---|
| Bias | LONG (부호 있는 32비트) | UTC 와 현지 시각의 차이. 분 단위 |
| StandardBias | LONG | 표준시 동안 Bias 에 더하는 값. 대부분 시간대에서 0 |
| DaylightBias | LONG | 일광 절약 시간 동안 Bias 에 더하는 값. 대부분 시간대에서 -60 |
| StandardDate | SYSTEMTIME | 표준시로 바뀌는 날짜와 현지 시각 |
| DaylightDate | SYSTEMTIME | 일광 절약 시간으로 바뀌는 날짜와 현지 시각 |

공식은 하나입니다(참고 2).

**UTC = 현지 시각 + Bias**

- UTC+9 인 곳의 Bias 는 -540 이며(현장 관찰), 공식에 넣으면 현지 18:00 은 18:00 + (-540분) = 09:00 UTC 가 됩니다.
- DaylightBias 는 일광 절약 시간 동안 Bias 에 더하는 값이라(참고 2), 위 공식과 합치면 일광 절약 시간 동안에는 UTC = 현지 시각 + Bias + DaylightBias 가 됩니다.
- 가상의 예를 듭니다. Bias 가 300, DaylightBias 가 -60 인 시간대에서 일광 절약 시간 중 현지 12:00 은 12:00 + 240분 = 16:00 UTC 입니다. 같은 시간대의 표준시 중 현지 12:00 은 StandardBias 가 0 이면 17:00 UTC 입니다.

### 전환일 규칙

- StandardDate·DaylightDate 에는 전환 날짜와 그때의 현지 시각을 적습니다(참고 2).
- 일광 절약 시간이 없는 시간대는 wMonth 가 0 입니다(참고 2).
- wYear 가 0 이면 해마다 되풀이하는 규칙이고(참고 2), 이때 wDayOfWeek 는 요일이고, wDay 는 그 달의 몇 번째 요일인지입니다(참고 2). wDay 는 1~5 이고 5 는 마지막 요일입니다(참고 2).
- wYear 가 0 이 아니면 한 번만 일어나는 절대 날짜입니다(참고 2).
- 그래서 어떤 시각이 일광 절약 시간 안에 드는지는 그 시각의 연도로 전환일을 계산해 가립니다.

### 레지스트리에서 찾기

| 무엇 | 위치 | 값 |
|---|---|---|
| 시간대별 정의 | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Time Zones\<시간대 이름>` | Display, Dlt, Std, MUI_Display, MUI_Dlt, MUI_Std (REG_SZ), TZI (REG_BINARY) (참고 2) |
| 이 컴퓨터의 현재 설정 | `SYSTEM\ControlSet00X\Control\TimeZoneInformation\Bias` | REG_DWORD. 부호 있는 32비트로 읽음 (현장 관찰) |

- TZI 값은 REG_TZI_FORMAT 구조입니다(참고 2). Bias, StandardBias, DaylightBias 를 LONG 으로 차례로 적고, 그 뒤에 StandardDate, DaylightDate 를 SYSTEMTIME 으로 적습니다(참고 2).
- Bias 는 REG_DWORD 로 저장하지만 부호 있는 32비트로 읽어야 합니다(현장 관찰). UTC+9 의 -540 을 부호 없이 읽으면 4,294,966,756 이 됩니다(현장 관찰).
- 하이브의 REG_DWORD 를 글자로 보여 주는 도구는 부호 없는 10진으로 보여 주는 경우가 많습니다(현장 관찰). 부호에 뜻이 있는 값은 원시 바이트로 확인합니다.
- TimeZoneInformation 키의 다른 값과 그 뜻은 이 페이지에서 확인하지 못했습니다. 이 키의 풀이는 [시간대 설정](../../../02-artifacts/system-account/time-zone.md)을 봅니다.
- 오프라인 SYSTEM 하이브에서 어느 컨트롤셋을 읽을지는 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)를 봅니다.

### 헥스로 한 번

아래 바이트는 REG_TZI_FORMAT 명세를 따라 만든 예시입니다. 특정 컴퓨터에서 뽑은 값이 아닙니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B
0000    E4 FD FF FF 00 00 00 00 C4 FF FF FF
```

1. 0x00 의 `E4 FD FF FF` 는 Bias 입니다. 리틀 엔디언으로 0xFFFFFDE4 입니다. 부호 있는 32비트로 읽으면 -540 이고, 부호 없이 읽으면 4,294,966,756 입니다. -540 이 맞는 값입니다.
2. 0x04 의 `00 00 00 00` 은 StandardBias 0 입니다.
3. 0x08 의 `C4 FF FF FF` 는 DaylightBias 입니다. 0xFFFFFFC4 이고, 부호 있는 32비트로 -60 입니다.
4. 0x0C 부터는 StandardDate 와 DaylightDate 가 SYSTEMTIME 으로 이어집니다. 이 예시에서는 풀지 않습니다.
5. 이 시간대에서 현지 19:00 은 19:00 + (-540분) = 10:00 UTC 입니다.

## 변환할 때의 함정

### "지금" 설정으로 바꾸는 API

- FileTimeToLocalFileTime 은 지금 설정된 시간대와 일광 절약 시간을 씁니다(참고 1).
- 그래서 지금이 일광 절약 시간이면, 표준시 기간의 파일 시각을 바꿀 때도 일광 절약 시간을 적용해(참고 1) 결과가 일광 절약 시간의 차이만큼 어긋납니다.
- Microsoft 는 NTFS 시각을 현지 시각으로 바꿀 때 FileTimeToSystemTime → SystemTimeToTzSpecificLocalTime → SystemTimeToFileTime 순서를 권합니다(참고 1).
- 분석 PC 에서 "지금 설정" 으로 바꾸면 검체가 아닌 분석 PC 의 시간대가 들어갑니다. 도구가 어떤 방식으로 바꾸는지 모르면 UTC 로 뽑아 직접 바꿉니다.

### FAT 를 라이브로 읽을 때

- FAT 에서 GetFileTime 은 캐시해 둔 UTC 를 돌려줍니다(참고 1).
- 일광 절약 시간으로 바뀌어도 이 캐시는 갱신되지 않습니다(참고 1). 그래서 1시간 어긋나고, 재시작하면 맞습니다(참고 1).
- FindFirstFile 은 FAT 의 현지 시각을 읽어 지금 시간대 설정으로 UTC 로 바꿉니다(참고 1).
- 이 사실을 합치면, FAT 로 포맷한 이동식 저장장치의 시각을 UTC 로 바꾼 값은 그 장치를 읽는 컴퓨터의 시간대에 따라 달라집니다. 장치를 쓴 컴퓨터와 읽는 컴퓨터의 시간대가 다르면 그 차이만큼 어긋납니다.
- 이미지에서 원시 값을 읽으면 캐시와 분석 PC 의 설정이 끼어들지 않습니다.

## 시스템 시계가 바뀐 흔적

### 보안 로그 4616

- 시스템 시각이 바뀔 때마다 4616 "The system time was changed." 이 생깁니다(참고 4).
- 하위 범주는 Audit Security State Change 이지만 이 감사 설정과 관계없이 항상 남습니다(참고 4).
- 공급자는 Microsoft-Windows-Security-Auditing, 채널은 Security, Task 는 12288 입니다(참고 4).

| 이벤트 버전 | Windows (참고 4) | 달라진 점 (참고 4) |
|---|---|---|
| 0 | Windows Vista·Server 2008 | 최초 버전 |
| 1 | Windows 7·Server 2008 R2 | Process Information 절 추가 |

| EventData 칸 (참고 4) | 쓰는 곳 |
|---|---|
| SubjectUserSid · SubjectUserName · SubjectDomainName · SubjectLogonId | 시각을 바꾼 계정 확인 |
| PreviousTime | 바뀌기 전 시각 (UTC) |
| NewTime | 바뀐 뒤 시각 (UTC) |
| ProcessId · ProcessName | 시각을 바꾼 프로세스 확인 |

- PreviousTime·NewTime 은 UTC 이고, 형식은 `YYYY-MM-DDThh:mm:ss.nnnnnnnZ` 입니다(참고 4).
- 문서의 예시는 PreviousTime `2015-10-09T05:04:30.000941900Z`, NewTime `2015-10-09T05:04:30.000000000Z` 입니다(참고 4). 두 값을 빼면 시계를 약 0.94밀리초 뒤로 돌렸습니다.
- Subject 가 LOCAL SERVICE 이면 Windows Time 서비스가 한 보통의 시각 보정입니다(참고 4).
- Microsoft 는 Subject 가 LOCAL SERVICE 가 아니거나 프로세스 이름이 svchost.exe 가 아니면 보고하라고 권합니다(참고 4).
- 시각을 바꿀 때 System 로그에 함께 남는 이벤트는 이 페이지에서 확인하지 못했습니다. 이 이벤트의 자세한 풀이는 [시간 변경](../../../02-artifacts/event-logs/4616-kernel-general.md)을 봅니다.

### 바뀐 시계로 적힌 기록 읽기

아래는 위 사실에서 끌어낸 해석입니다.

NewTime 에서 PreviousTime 을 빼면 시계가 뛴 크기가 나오고, 시계를 바꾼 뒤 다음 보정까지 그 PC 가 적은 시각에는 그 크기만큼 차이가 들어 있을 수 있습니다. 시계가 뒤로 가면 같은 시각대가 두 번 생겨서 이 구간의 기록은 시각만으로 순서를 정할 수 없습니다.

- 시계가 조금씩 틀어지는 오차(드리프트, Drift)를 재는 방법은 이 페이지의 출처로 확인하지 못했습니다. 같은 사건을 이 PC 와 바깥 기준이 함께 적었다면 두 시각의 차이가 그 시점의 오차입니다.

## 절차

1. **검체의 시간대 설정을 읽습니다.** SYSTEM 하이브의 TimeZoneInformation\Bias 를 부호 있는 32비트로 읽습니다.
2. **일광 절약 시간 규칙을 읽습니다.** SOFTWARE 하이브의 Time Zones 아래에서 검체 시간대의 TZI 를 읽습니다. 전환일의 wMonth 가 0 이면 일광 절약 시간이 없는 시간대입니다.
3. **출처마다 저장 기준을 적습니다.** 위 "출처마다 시각 기준이 다릅니다" 표에서 시작합니다. 표에 없는 출처는 해당 아티팩트 페이지에서 확인합니다.
4. **도구 출력의 시간대를 확인합니다.** 헥스로 읽은 값 하나와 도구가 보여 준 값을 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../reporting/tool-validation.md)을 봅니다.
5. **현지 시각 출처를 UTC 로 바꿉니다.** UTC = 현지 시각 + Bias 를 씁니다. 그 시각이 일광 절약 시간 안이면 DaylightBias 를 더합니다. 전환일은 그 시각의 연도로 계산합니다.
6. **다른 컴퓨터에서 쓴 FAT 장치를 따로 봅니다.** 그 장치를 쓴 컴퓨터의 시간대를 확인합니다. 확인하지 못하면 보고서에 그 한계를 적습니다. 장치 연결 흔적은 [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md)에서 찾습니다.
7. **4616 을 모읍니다.** 보안 로그에서 4616 을 찾아 PreviousTime·NewTime·Subject·ProcessName 을 표로 적습니다.
8. **보통의 보정이 아닌 4616 을 표시합니다.** Subject 가 LOCAL SERVICE 가 아니거나 프로세스가 svchost.exe 가 아닌 것을 따로 봅니다. 그 뒤의 기록은 시계가 뛴 크기를 감안해 읽습니다.
9. **UTC 로 정렬합니다.** 합치는 방법은 [여러 아티팩트 합친 타임라인](super-timeline.md)을 봅니다.
10. **보정 근거를 남깁니다.** 보정한 줄마다 원래 값, 적용한 Bias, 일광 절약 시간 적용 여부를 함께 적습니다.

## 도구

- 레지스트리 뷰어로 Bias 를 볼 때는 부호 없는 10진으로 나오지 않는지 확인합니다(현장 관찰). 의심스러우면 원시 바이트를 읽습니다.
- 타임라인 도구의 출력 시간대는 결과의 시간대 칸으로 확인합니다. 출력 칸은 [여러 아티팩트 합친 타임라인](super-timeline.md)에서 다룹니다.
- 변환을 도구에 맡기더라도 한두 값은 위 공식으로 직접 계산해 맞춰 봅니다.
- 4616 은 이벤트 로그 파일에서 읽습니다. 파일을 읽는 법은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md)을 봅니다.

## 함정과 한계

1. **Bias 를 부호 없이 읽습니다.** -540 이 4,294,966,756 으로 보입니다(현장 관찰).
2. **Bias 를 거꾸로 적용합니다.** 공식은 UTC = 현지 시각 + Bias 입니다(참고 2). Bias 가 -540 이면 현지 시각에서 9시간을 뺍니다.
3. **지금 설정으로 과거 시각을 바꿉니다.** 일광 절약 시간을 적용할지는 그 시각의 날짜로 정합니다(참고 1).
4. **분석 PC 의 시간대가 섞입니다.** 도구가 현지 시각으로 보여 주면 그 현지는 분석 PC 의 설정일 수 있습니다.
5. **FAT 시각을 UTC 로 여깁니다.** FAT 는 현지 시각으로 저장합니다(참고 1).
6. **이동식 장치를 검체의 시간대로 풉니다.** 그 장치는 시간대가 다른 컴퓨터에서 쓰였을 수 있습니다.
7. **4616 을 모두 조작으로 읽습니다.** Subject 가 LOCAL SERVICE 인 것은 보통의 시각 보정입니다(참고 4).
8. **4616 이 없으면 시계가 그대로였다고 단정합니다.** 보안 로그를 지웠거나 오래된 기록이 밀려났을 수 있습니다. 로그 삭제 흔적은 [이벤트 로그 삭제](../../../02-artifacts/event-logs/1102-104.md)를 봅니다.
9. **시계 오차를 재지 않고 초 단위 순서를 단정합니다.** 다른 PC 나 서버의 기록과 섞을 때는 두 시계의 차이를 먼저 따집니다.

## 결과를 어떻게 해석하나

보정한 시각은 "원래 값 + 보정 근거" 로 적습니다.

- 쓸 수 있는 문장(예): "이 컴퓨터의 Bias 는 -540 입니다. 이 장치를 이 컴퓨터에서만 썼다고 보면, FAT 쓰기 시각 2024-03-15 19:00:00 은 2024-03-15 10:00:00 UTC 에 해당합니다."
- 쓰면 안 되는 문장(예): "파일은 2024-03-15 10:00:00 UTC 에 저장됐습니다." 전제와 보정 근거가 빠져 있습니다.
- 쓸 수 있는 문장(예): "보안 로그에 PreviousTime 과 NewTime 이 1시간 차이 나는 4616 기록이 있습니다. Subject 는 LOCAL SERVICE 가 아닙니다."
- 쓰면 안 되는 문장(예): "사용자가 시계를 1시간 되돌렸습니다." 누가 바꿨는지는 Subject·ProcessName 과 다른 기록으로 따로 확인합니다.
- 파일 시각 자체를 고친 흔적은 [시각 조작 탐지](timestomping.md)에서 따집니다.

## 참고 문헌

1. Microsoft Learn, "File Times" — https://learn.microsoft.com/en-us/windows/win32/sysinfo/file-times
2. Microsoft Learn, "TIME_ZONE_INFORMATION structure (timezoneapi.h)" — https://learn.microsoft.com/en-us/windows/win32/api/timezoneapi/ns-timezoneapi-time_zone_information
3. Microsoft Learn, "USN_RECORD_V2 structure (winioctl.h)" — https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-usn_record_v2
4. Microsoft Learn, "4616(S) The system time was changed." (Windows 10 보관 문서) — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4616
