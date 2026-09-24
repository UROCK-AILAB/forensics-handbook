# 컨트롤셋 고르기 (ControlSet·Select)

> 위치: [레지스트리 하이브 구조](index.md) > 컨트롤셋 고르기

## 한 줄 요약

떼어 낸 SYSTEM 하이브에는 `CurrentControlSet` 키가 없습니다. 루트의 `Select` 키에 있는 `Current` 값을 먼저 읽고, 그 번호의 `ControlSet00N` 키를 엽니다.

## 이 구조를 쓰는 아티팩트

컨트롤셋 (Control Set)은 부팅·장치·서비스 설정을 한 벌로 묶은 키이고, SYSTEM 하이브 설정의 대부분이 컨트롤셋 아래에 있습니다. SYSTEM 하이브가 어디 있는지는 [하이브 파일 종류와 위치](system-software-sam-security-ntuser-dat-usrclass.md)에 있습니다.

공식 문서와 글은 이 경로를 보통 `HKLM\SYSTEM\CurrentControlSet\...` 으로 적지만, 떼어 낸 하이브에서는 이 부분을 `SYSTEM\ControlSet00N\...` 으로 바꿔 읽어야 합니다.

| 아티팩트 | 컨트롤셋 안 경로 | 자세히 |
|---|---|---|
| 시간대 설정 | `Control\TimeZoneInformation` | [시간대 설정](../../../02-artifacts/system-account/time-zone.md) |
| 마지막 종료 시각 | `Control\Windows` 의 `ShutdownTime` 값 | [시스템 기본 정보](../../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) |
| 서비스·드라이버 | `Services` | [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md) |
| USB 저장장치 목록 | `Enum\USBSTOR` | [USB 저장장치 목록](../../../02-artifacts/external-devices/usb-storage-artifacts/usbstor.md) |
| 심캐시 | `Control\Session Manager\AppCompatCache` | [심캐시](../../../02-artifacts/execution/shimcache-appcompatcache.md) |

SYSTEM 하이브의 모든 키가 컨트롤셋 안에 있는 것은 아니며, `Select` 와 `MountedDevices` 는 하이브 루트 바로 아래에 있습니다. `MountedDevices` 는 [드라이브 문자 매핑](../../../02-artifacts/external-devices/usb-storage-artifacts/mounteddevices.md)에서 다룹니다.

## 구조

### 하이브 루트의 키 배치

```
SYSTEM (하이브 루트)
├─ ControlSet001     ← 파일에 실제로 저장된 컨트롤셋
├─ ControlSet002     ← 번호와 개수는 검체마다 다릅니다
├─ Select            ← 어느 번호를 쓰는지 적은 키
├─ MountedDevices    ← 컨트롤셋 밖에 있는 키의 예
└─ …
CurrentControlSet   ← 파일에는 없습니다. 실행 중에만 생기는 링크입니다
```

> 그림 자리: SYSTEM 하이브 루트의 ControlSet001·ControlSet002·Select 와, 실행 중에만 생기는 CurrentControlSet 링크가 Current 번호의 컨트롤셋을 가리키는 모습

Windows 2000 문서는 번호 붙은 컨트롤셋이 보통 둘이고 많으면 넷까지 있다고 설명합니다. libyal 의 레지스트리 자료는 `Current` 값이 보통 1 이나 2 이지만 3 이나 47 같은 값도 쓰인 예가 있다고 적습니다. 그러니 번호와 개수를 짐작하지 말고 하이브에 있는 키를 직접 셉니다.

### Select 키의 네 값

네 값 모두 REG_DWORD 입니다. 값 1 은 `ControlSet001`, 값 2 는 `ControlSet002` 를 뜻합니다.

| 값 | 뜻 |
|---|---|
| `Current` | 이번 부팅에 실제로 쓴 컨트롤셋 번호입니다. `CurrentControlSet` 이 가리키는 번호입니다. |
| `Default` | 다음 부팅에 쓸 컨트롤셋 번호입니다. |
| `LastKnownGood` | 마지막으로 성공한 부팅 설정의 사본 번호입니다. 부팅 때 "마지막으로 성공한 구성 (Last Known Good Configuration)"을 고르면 이 번호로 부팅합니다. |
| `Failed` | 마지막으로 성공한 구성으로 부팅했을 때 밀려난 컨트롤셋 번호입니다. |

### CurrentControlSet 링크가 생기는 과정

XP·2003 시절 부트 로더(NTLDR) 기준으로 Microsoft 가 설명한 순서는 다음과 같습니다.

1. 부트 로더가 SYSTEM 하이브를 메모리에 올립니다.
2. 부트 로더가 `Select` 키를 읽습니다.
3. 평소에는 `Default` 번호를 고릅니다. 마지막으로 성공한 구성을 골랐으면 `LastKnownGood` 번호를 고릅니다.
4. 부트 로더가 고른 번호를 `Current` 에 적습니다.
5. 커널이 초기화될 때 `CurrentControlSet` 링크를 만듭니다.

링크 키 (Symbolic Link Key)는 `SymbolicLinkValue` 라는 값에 대상 경로를 절대 레지스트리 경로로 적습니다. 하이브 형식에서는 키 레코드 플래그 0x0010(KEY_SYM_LINK)이 링크 키를 뜻합니다.

`CurrentControlSet` 은 실행 중에만 있는 키이고, 메모리에만 있는 키 (Volatile Key)는 `RegSaveKey` 로 저장해도 파일에 들어가지 않습니다. 그래서 디스크 이미지에서 꺼낸 하이브든, 켜진 PC 에서 저장해 온 하이브든 `Select` 로 번호를 골라야 합니다.

### 버전별 차이

| Windows 버전 | 확인된 내용 |
|---|---|
| Windows NT 시절 문서 | 성공한 부팅 뒤에 예전 LastKnownGood 사본을 버리고 `Clone` 키를 복사해 새 사본으로 씁니다. 서비스 시작에 심각한 오류가 없고 로그온이 한 번 이상 성공해야 "성공한 부팅"으로 칩니다. |
| 2000·XP·2003 | 부트 로더(NTLDR)가 `Select` 로 컨트롤셋을 고릅니다. 부팅 메뉴에서 마지막으로 성공한 구성을 고를 수 있습니다. |
| Vista 이후 | `Select` 의 네 값과 번호 붙은 컨트롤셋 구조는 그대로 있습니다. 사본을 언제 어떻게 새로 만드는지는 공식 문서로 확인하지 못했습니다. |

Vista 이후 검체는 버전만 보고 컨트롤셋 개수나 LastKnownGood 동작을 추측하지 않고, 하이브에 남은 값과 키를 그대로 적습니다.

## 읽는 법

1. SYSTEM 하이브의 사본을 만듭니다. 같은 폴더의 `.LOG1`·`.LOG2` 도 함께 가져옵니다.
2. 하이브 루트의 `Select` 키를 엽니다.
3. `Current` 값을 읽습니다.
4. 번호를 세 자리로 맞춰 `ControlSet00N` 키를 엽니다. 1 이면 `ControlSet001` 입니다.
5. 하이브 루트에 있는 `ControlSet` 키를 모두 적습니다.
6. `Default`·`LastKnownGood`·`Failed` 값도 함께 적습니다.
7. 분석 기록에 어느 번호를 읽었는지 남깁니다.

### 헥스로 한 번 따라가 보기

아래는 regf 명세로 만든 예시입니다. 특정 검체에서 뽑은 바이트가 아닙니다. `Select` 키 아래의 `Current` 값 하나가 값 레코드 (Value Key, `vk`) 셀로 저장된 모습입니다. 셀과 값 레코드의 자세한 구조는 [하이브 내부 구조](regf-hbin-cell.md)에 있습니다.

```
오프셋    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  E0 FF FF FF 76 6B 07 00  04 00 00 80 01 00 00 00  ....vk..........
00000010  04 00 00 00 01 00 00 00  43 75 72 72 65 6E 74 00  ........Current.
```

| 셀 안 위치 | 바이트 | 읽은 값 |
|---|---|---|
| 0x00 | `E0 FF FF FF` | 셀 크기 -32 입니다. 음수이므로 사용 중인 셀입니다. |
| 0x04 | `76 6B` | 서명 `vk` 입니다. |
| 0x06 | `07 00` | 값 이름 길이 7 입니다. |
| 0x08 | `04 00 00 80` | 데이터 크기 0x80000004 입니다. 맨 윗비트가 켜져 있으면 데이터가 다음 4바이트 칸에 바로 들어 있습니다. 실제 크기는 4 입니다. |
| 0x0C | `01 00 00 00` | 데이터 1 입니다. `ControlSet001` 을 뜻합니다. |
| 0x10 | `04 00 00 00` | 데이터 형식 4, 곧 REG_DWORD 입니다. |
| 0x14 | `01 00` | 플래그 0x0001 입니다. 값 이름이 ASCII 문자열이라는 뜻입니다. |
| 0x16 | `00 00` | 쓰지 않는 칸입니다. 예전 데이터가 남아 있을 수 있습니다. |
| 0x18 | `43 75 72 72 65 6E 74` | 값 이름 `Current` 입니다. |
| 0x1F | `00` | 셀 크기를 8바이트 단위로 맞춘 채움 바이트입니다. |

위 표는 셀 크기 칸부터 셉니다. 명세는 값 레코드의 오프셋을 셀 크기 칸(4바이트) 다음부터 셉니다. 그래서 명세의 오프셋 0 이 위 표의 0x04 입니다.

### 공개 도구로 한 번 읽어 보기

하이브 내용을 보여 주는 공개 도구라면 `Select` 값을 그대로 볼 수 있습니다. 아래는 공개 파이썬 라이브러리 python-registry 로 번호를 고르는 예입니다.

```python
from Registry import Registry

reg = Registry.Registry("SYSTEM")          # 하이브 사본 경로
select = reg.open("Select")
for name in ("Current", "Default", "LastKnownGood", "Failed"):
    print(name, select.value(name).value())

current = select.value("Current").value()
cs = reg.open("ControlSet%03d" % current)  # 1 -> ControlSet001
print("읽을 컨트롤셋:", cs.name())
```

## 포렌식에서 중요한 점

**번호 붙은 컨트롤셋이 여럿이면 모두 봅니다.** `Current` 가 아닌 컨트롤셋은 예전 설정의 사본일 수 있고, 지금 컨트롤셋에서 지워진 서비스나 장치 키가 그쪽에 남아 있을 수 있습니다. 두 쪽을 키 단위로 비교하면 어느 한쪽에만 있는 항목이 드러납니다. 지운 키를 셀 단위로 되살리는 방법은 [지워진 키·값 복구](deleted-keys-values.md)에 있습니다.

**사본이 만들어진 시각은 이 값들로 알 수 없습니다.** 한쪽에만 있는 항목은 "사본을 만든 뒤에 생겼거나 지워졌다"까지만 말할 수 있습니다. 그 사본이 언제 만들어졌는지는 다른 기록으로 따로 확인해야 합니다.

**`Failed` 가 실제 있는 컨트롤셋을 가리키면 따로 적어 둡니다.** Microsoft 문서는 이 값을 마지막으로 성공한 구성으로 부팅했을 때 밀려난 컨트롤셋이라고 설명합니다. 부팅 문제를 겪은 적이 있다는 단서가 될 수 있지만, 언제 그런 부팅을 했는지는 이 값만으로 알 수 없습니다.

**비정상 종료된 하이브는 로그부터 봅니다.** `Select` 나 컨트롤셋의 최근 변경이 하이브 본문에 아직 반영되지 않고 로그에만 있을 수 있습니다. 반영하는 방법은 [트랜잭션 로그와 반영 안 된 변경](log1-log2.md)에 있습니다.

**옛 하이브마다 `Select` 를 따로 읽습니다.** 섀도 복사본에서 꺼낸 SYSTEM 하이브에는 그때의 `Select` 값이 남아 있습니다. 지금 하이브의 번호를 그대로 옮겨 쓰지 않습니다. 옛 하이브를 꺼내는 방법은 [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)에 있습니다.

**메모리에서 읽은 레지스트리는 다릅니다.** 실행 중인 시스템의 메모리에는 `CurrentControlSet` 링크가 있습니다. 메모리 덤프에서 레지스트리를 읽을 때는 [메모리 분석](../../../03-techniques/analysis/memory-forensics/index.md)을 함께 봅니다.

| 이 구조로 말할 수 있는 것 | 이 구조로 말할 수 없는 것 |
|---|---|
| 하이브가 마지막으로 저장될 때 어느 컨트롤셋이 "현재"로 적혀 있었는지 | 예비 사본이 언제 만들어졌는지 |
| 다음 부팅에 쓸 번호와 예비 사본 번호 | 마지막으로 성공한 구성으로 언제 부팅했는지 |
| 컨트롤셋끼리 설정이 어떻게 다른지 | 차이가 생긴 시각과 그 변경을 한 사람 |

## 함정

1. **`ControlSet001` 을 고정으로 읽습니다.** `Current` 가 2 이상인 검체에서는 현재 설정이 아닌 사본을 읽게 됩니다.
2. **`LastKnownGood` 을 현재 설정으로 읽습니다.** 현재 설정은 `Current` 입니다. `LastKnownGood` 은 예비 사본의 번호입니다.
3. **도구 결과의 `CurrentControlSet` 을 그대로 믿습니다.** 떼어 낸 하이브를 읽은 결과에 `CurrentControlSet` 이 보이면, 도구가 `Select` 로 번호를 풀어 적었다는 뜻입니다. 도구가 어느 번호로 풀었는지 확인합니다. 직접 짠 스크립트가 `ControlSet001` 을 고정으로 읽고 있지 않은지도 확인합니다.
4. **`Select` 키의 마지막 기록 시각을 마지막 부팅 시각으로 씁니다.** 같은 번호를 다시 적을 때도 이 시각이 바뀌는지 설명한 공식 문서를 찾지 못했습니다. 부팅 시각은 [켜짐·꺼짐](../../../02-artifacts/event-logs/power-on-off-events.md) 기록으로 확인합니다. 마지막 기록 시각의 일반적인 뜻은 [키 마지막 기록 시각](last-write-time.md)에 있습니다.
5. **`Current` 가 없는 키를 가리키는데 그냥 넘어갑니다.** 하이브 손상, 반영 안 된 로그, 누군가 값을 고친 흔적을 차례로 의심합니다. 로그와 섀도 복사본의 옛 하이브를 함께 봅니다.
6. **컨트롤셋 밖 키를 컨트롤셋 안에서 찾습니다.** `MountedDevices` 처럼 하이브 루트에 있는 키는 번호와 상관없이 하나뿐입니다.

## 도구

하이브 내용을 보여 주는 공개 도구라면 `Select` 값과 번호 붙은 컨트롤셋을 볼 수 있습니다. 예로 libregf(`regfexport` 등), python-registry, Registry Explorer, RegRipper 가 있습니다.
도구마다 `CurrentControlSet` 을 풀어 주는 방식이 다르므로 결과에 어느 번호를 읽었는지 적혀 있는지 확인합니다.
도구 하나에만 기대지 말고, 중요한 값은 위처럼 헥스로 한 번 직접 확인합니다. 도구 결과를 서로 맞춰 보는 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 참고 문헌

- Microsoft, "ControlSet00n", Windows 2000 레지스트리 참조 (Microsoft Learn 보관 문서). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc960234(v=technet.10)
- Microsoft, "HKEY_LOCAL_MACHINE\SYSTEM Subtree", Windows NT 레지스트리 문서 (MSDN Library 사본). https://techshelps.github.io/MSDN/DNWINNT/HTML/D1E/S8450.HTM
- Microsoft NTDebugging 블로그, "How Windows Starts Up (Part the second)", 2007 (Microsoft Learn 보관 문서). https://learn.microsoft.com/en-us/archive/blogs/ntdebugging/how-windows-starts-up-part-the-second
- Microsoft Learn, "RegCreateKeyExW function (winreg.h)" — REG_OPTION_CREATE_LINK·REG_OPTION_VOLATILE 설명. https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regcreatekeyexw
- libyal, Windows Registry knowledge base (winreg-kb), "Current control set". https://winreg-kb.readthedocs.io/en/latest/sources/system-keys/Current-control-set.html
- libyal, libregf, "Windows NT Registry File (REGF) format" — 값 레코드 구조와 키 플래그. https://github.com/libyal/libregf/blob/main/documentation/Windows%20NT%20Registry%20File%20(REGF)%20format.asciidoc
