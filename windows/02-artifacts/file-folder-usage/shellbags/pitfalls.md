---
title: "셸백 해석 함정"
parent: "셸백"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1200
---

# 셸백 해석 함정 (Pitfalls)

셸백 (ShellBags) 항목은 "이 사용자 환경에서 셸이 이 폴더를 다룬 적이 있다" 는 기록입니다. 폴더를 두 번 클릭해 열었다는 뜻도, 사람이 직접 했다는 뜻도 아닙니다.

## 이 페이지가 다루는 것

어떤 동작이 셸백을 만드는지, Windows 버전마다 어떻게 다른지 모으고, 셸백이 있을 때와 없을 때 각각 말할 수 없는 것을 정리합니다. 키 위치와 구조는 [저장 위치와 구조](ntuser-usrclass-bagmru-bags.md) 에 있고, 시각 함정은 [셸백 시각 해석](timestamps.md) 에서 자세히 다루며 이 페이지에는 요약만 있습니다. USB·네트워크·ZIP 셸 아이템을 읽을 때의 함정은 [외부 장치·네트워크·압축 폴더 탐색 흔적](removable-network-zip.md) 에 있습니다.

이 페이지에서는 "열었다" 대신 "다뤘다 (interacted)" 라고 씁니다. 폴더를 고르기만 한 경우도 들어가는 말입니다.

## 한눈에 보기 — 흔한 오해

| 흔한 오해 | 실제 | 절 |
|---|---|---|
| 셸백이 있으면 그 폴더를 열었다 | Vista~8.1 에서는 한 번 클릭·오른쪽 클릭·이름 바꾸기·복사·지우기로도 생겼습니다. 10 에서도 한 번 클릭으로 생겼습니다 | 1 |
| 셸백은 사람이 한 일만 남긴다 | 명령 프롬프트로 만든 폴더, 복사 대상 폴더에도 항목이 생겼습니다. XP 에서는 탐색기가 스스로 MRU 순서를 바꿨습니다 | 2 |
| 셸백이 없으면 그 폴더에 간 적이 없다 | 명령줄 탐색은 보통 남지 않습니다. 지운 기록, 로그에만 있는 기록도 있습니다 | 3 |
| 셸백 경로 하나는 폴더 하나다 | 같은 이름으로 다시 만든 폴더가 옛 항목을 이어받았습니다 | 4 |
| 키 시각은 각 폴더를 연 시각이다 | MRUListEx 맨 앞 자식 하나에만 붙습니다 | 5 |
| 도구 결과가 곧 레지스트리 내용이다 | 도구마다 계산 방식과 읽는 형식이 다릅니다 | 6 |
| 한 버전의 실험 결과는 다른 버전에도 맞다 | 생성 조건은 버전마다 달랐습니다 | 1, 8 |

## 1. 무엇이 셸백을 만드나 — 버전마다 다르다

셸백을 만드는 조건은 연구가 쌓이면서 여러 번 바뀌었습니다.

| 발표 | 시험한 판 | 알려진 생성 조건 | 출처 |
|---|---|---|---|
| 2009 | — | "탐색기에서 한 번 이상 열고 닫은 폴더에만" 생긴다고 적었습니다 | Zhu·Gladyshev·James (SANS 2011 글에서 인용) |
| 2014 | XP | 하위 항목이 있는 폴더는 여는 순간 생겼습니다. 빈 폴더는 창을 닫거나 같은 창에서 다른 폴더로 옮길 때 생겼습니다 | Lo |
| 2014 | Vista·7·8·8.1 | 폴더를 만들기, 한 번 클릭해 고르기, 오른쪽 클릭만 해도 생겼습니다. 빈 폴더도 같았습니다 | Lo |
| 2017 | Windows 10 | 폴더를 한 번 클릭만 해도 생겼습니다 | 4n6k (UPDATE #14) |
| 2025 | Windows 11 | 한 번 클릭으로는 더 이상 생기지 않을 수 있다는 단서만 붙었습니다 | 4n6k (UPDATE #15) |

Lo 의 실험(Vista·7·8·8.1)에서 셸백을 만든 동작은 아래와 같습니다.

- **폴더 열기.** 두 번 클릭해 여는 경우입니다.
- **고르기.** 한 번 클릭해 고르거나 오른쪽 클릭하면 생겼습니다.
- **화살표 키.** 폴더 하나를 고른 뒤 화살표 키로 선택을 옮기면, 선택이 지나간 폴더마다 생겼습니다.
- **이름 바꾸기.** 탐색기 창에서는 옛 이름과 새 이름 항목이 둘 다 생겼습니다.
- **지우기.** 폴더를 골라 지우는 동작도 셸백을 만들었습니다.
- **복사.** 두 폴더가 모두 로컬 디스크에 있으면 원본과 대상 항목이 둘 다 생겼습니다.
- **바탕 화면.** 잘라내기(Ctrl+X)·복사(Ctrl+C)·이름 바꾸기·지우기도 셸백을 만들었습니다.
- **ZIP 파일.** 탐색기에서 열고 닫거나, 같은 창에서 다른 폴더로 옮기면 생겼습니다. ZIP 안을 둘러보기만 해도 셸백이 생깁니다.
- **검색 결과 창.** 검색 결과 창도 셸백을 남겼습니다. Vista·7 에서는 시작 메뉴에 친 검색어가 `query=ab` 모양으로 남았습니다. 8·8.1 의 시작 화면 검색은 남지 않았습니다.
- **desktop.ini.** desktop.ini 로 폴더 유형이나 CLSID 를 정한 폴더는 열어야만 생겼습니다.
- **원격 공유의 하위 폴더.** Vista 에서는 공유 폴더 안 하위 폴더를 열어야 생겼습니다. 7·8·8.1 에서는 고르기 같은 동작만으로도 생겼습니다.

XP 에서는 폴더를 열지 않아도 셸백이 생긴 경우가 있습니다. 속성 창에서 "사용자 지정" 탭을 열고 "확인" 을 누르면 생겼습니다. (Lo)

그래서 셸백 항목 하나를 "폴더를 열었다" 로 옮기지 않습니다. 분석 대상과 같은 버전의 실험 결과가 없으면 "다뤘다" 까지만 씁니다.

## 2. 사람이 직접 연 것이 아닌 항목

셸백 항목과 키 시각은 사용자가 폴더를 고르지 않아도 생기거나 바뀔 수 있습니다.

- **명령 프롬프트.** Vista 에서 `mkdir` 로 `%UserProfile%\Desktop` 에 폴더를 만들었더니 그 폴더의 셸백이 생겼습니다. (Lo)
- **복사·이름 바꾸기의 대상.** 복사 대상 폴더와 새 이름 폴더는 그 안을 본 적이 없어도 항목이 생겼습니다. (Lo, Vista~8.1)
- **XP 미리 보기(Thumbnails) 보기.** 부모 폴더를 열 때마다 탐색기가 하위 폴더에서 `folder.jpg`·`folder.gif` 를 찾았습니다. 이때 부모 키의 MRUListEx 가 다시 쓰이고 키 시각도 바뀌었습니다. 이 경우 MRUListEx 는 사용자 동작이 아니라 탐색기 동작을 보여 줍니다. Vista~8.1 에는 이 보기가 없어 같은 일이 생기지 않았습니다. (Lo)
- **특수 폴더·가상 폴더·라이브러리.** 바탕 화면은 특수 폴더·가상 폴더·실제 폴더 가운데 어느 것도 될 수 있습니다. "문서" 는 실제 폴더·가상 폴더·라이브러리가 될 수 있습니다. 이런 폴더는 셸백이 생기는 조건이 복잡합니다. 사건에서 중요하면 비슷한 환경에서 따로 실험해 확인합니다.

## 3. 셸백이 없다고 가지 않은 것은 아니다

- **명령줄·스크립트.** 셸백은 탐색기 창의 보기 설정을 담는 곳입니다 (SANS 2011). 명령줄이나 스크립트로 폴더를 오가면 보통 셸백이 남지 않습니다.
- **XP 의 이동식 장치.** Lo 의 실험에서 XP 는 이동식 장치 안 폴더에 셸백을 만들지 않았습니다. Vista~8.1 은 열고 닫을 때 만들었습니다.
- **XP 의 빈 폴더.** 빈 폴더나 숨긴 항목이 있는 폴더(숨긴 항목을 안 보이게 설정한 경우)는 창을 닫거나 다른 폴더로 옮길 때 셸백이 생겼습니다. 그래서 실행 중인 시스템에서 수집할 때 창이 열려 있으면 아직 항목이 없을 수 있습니다. (Lo)
- **하이브 한쪽만 본 경우.** Vista 이후 로컬 폴더는 UsrClass.dat, 네트워크 쪽은 NTUSER.DAT 에 남을 수 있습니다. 두 하이브를 다 읽습니다. 경로는 [저장 위치와 구조](ntuser-usrclass-bagmru-bags.md) 에 있습니다.
- **로그에만 있는 변경.** 가장 최근 변경은 하이브 본문이 아니라 `UsrClass.dat.LOG1`·`.LOG2` 에만 있을 수 있습니다. 하이브와 로그 파일을 함께 뽑습니다. ([트랜잭션 로그와 반영 안 된 변경](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md))
- **지운 기록.** 폴더를 지워도 셸백은 그대로 남습니다. 대신 셸백만 지우는 도구가 있습니다. (Lo) 지운 키는 하이브의 빈 공간에 남을 수 있습니다. ([지워진 키·값 복구](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md), [지운 폴더 흔적 찾기](deleted-folders.md))

## 4. 경로 하나가 폴더 하나를 뜻하지 않는다

- **같은 이름으로 다시 만든 폴더.** Lo 의 실험(XP~8.1)에서 폴더나 ZIP 파일을 지우고 같은 이름으로 다시 만들면, 새 것이 옛 셸백 정보를 이어받았습니다. 그래서 셸백 경로 하나가 서로 다른 두 폴더를 가리킬 수 있습니다.
- **대조하는 법.** 셸 아이템 속 만든 시각과 NTFS 파일 참조(MFT 번호·순번)를 지금의 [$MFT](../../filesystem/mft.md) 와 맞춰 봅니다. 이 필드에 늘 파일 참조가 들어 있는지는 확정되지 않았습니다. 필드 위치는 [셸 아이템 (Shell Item·PIDL)](../../../01-foundations/shell-document-formats/shell-item-pidl.md) 에 있습니다.
- **드라이브 문자는 그때의 문자입니다.** 볼륨 셸 아이템에는 `E:\` 같은 이름이 들어 있습니다 (libfwsi). 같은 문자에 다른 장치가 붙었을 수 있습니다. 어느 장치였는지는 [드라이브 문자 매핑 (MountedDevices)](../../external-devices/usb-storage-artifacts/mounteddevices.md) 과 [사용자별 장치 연결 (MountPoints2)](../../external-devices/usb-storage-artifacts/mountpoints2.md) 으로 구분합니다.
- **같은 폴더가 여러 가지에 남을 수 있습니다.** 2절에서 본 것처럼 "문서" 는 라이브러리로도, 실제 폴더로도 다룰 수 있습니다. 들어간 길이 다르면 BagMRU 트리의 다른 가지에 따로 남을 수 있습니다. 항목 수를 폴더 수로 세지 않습니다.

## 5. 시각 함정 요약

자세한 규칙과 예는 [셸백 시각 해석](timestamps.md) 에 있습니다.

| 시각 | 흔한 잘못 | 바르게 읽는 법 |
|---|---|---|
| 키 마지막 기록 시각 (FILETIME, UTC) | 그 키 아래 모든 자식 폴더의 마지막 사용 시각으로 읽습니다 | MRUListEx 맨 앞 자식 하나가 맨 앞에 올라온 때입니다 (4n6k) |
| 루트 BagMRU 키 시각 | 바로 아래 항목(내 PC 등)을 방금 연 때로 읽습니다 | 이 키의 MRUListEx 나 NodeSlots 가 바뀌면 이 시각도 바뀝니다 (Lo). NodeSlots 는 어디서든 새 항목이 생길 때 바뀝니다 ([셸백 시각 해석](timestamps.md)) |
| 셸 아이템 속 만든·수정·접근 시각 (FAT 형식, 2초 단위) | 폴더를 연 때로 읽습니다 | 항목을 처음 만들 때 옮겨 적은 폴더 자신의 시각입니다. 그 뒤로 갱신되지 않습니다 (4n6k) |
| 도구의 "처음 연 때·마지막 연 때" 열 | 레지스트리에 적힌 값으로 읽습니다 | 도구가 키 시각과 MRU 순서로 계산한 값입니다 |

키 시각은 키 안의 값이 하나라도 바뀌면 바뀌므로, 사용자 동작과 시스템 동작이 모두 이 값을 바꿉니다. 셸 아이템 속 수정·접근 시각은 폴더에 파일을 넣거나 빼는 일처럼 셸백과 상관없는 동작으로도 바뀌므로 조심해서 읽습니다. 셋 가운데 만든 시각이 가장 쓸모 있다는 의견이 있습니다 (Carvey). 키 시각은 API 로 바꿀 수 있으며, 조작 흔적은 [키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md) 에서 다룹니다.

## 6. 도구가 보여 주는 것과 레지스트리 내용이 다르다

- 2013년 무렵 공개 도구 하나는 MRU 맨 앞 여부를 따지지 않고 모든 형제 항목에 키 시각을 붙였습니다. 그 도구는 2014년 판에서 고쳐졌습니다 (4n6k UPDATE #04).
- 같은 시기 일부 도구는 0x52 형식 셸 아이템과 MTP 장치 항목을 읽지 못하거나 결과에서 빠뜨렸습니다 (4n6k UPDATE #01·#03·#04).
- libfwsi 명세에도 뜻이 밝혀지지 않은 필드와 형식이 남아 있습니다. 도구마다 모르는 셸 아이템을 건너뛰거나 경로 일부를 비워 둘 수 있습니다.
- 보고서에는 도구 이름과 판을 적습니다. 공개 도구 두 가지 이상(예: RegRipper 의 shellbags 플러그인, ShellBags Explorer)으로 같은 하이브를 읽고 항목 수·경로·시각 열을 비교합니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 에 있습니다.
- 결과가 다른 항목은 원시 바이트로 직접 봅니다. 헥스로 읽는 법은 [저장 위치와 구조](ntuser-usrclass-bagmru-bags.md) 와 [셸백 시각 해석](timestamps.md) 에 있습니다.

## 7. 증거로서 의미 — 보고서에 쓸 때

### 증명하는 것

- 이 하이브를 쓰는 사용자 환경에서 셸이 이 경로를 다룬 기록이 있습니다.
- 셸 아이템을 만들 때 그 경로에 폴더나 ZIP 파일이 있었습니다.
- MRUListEx 맨 앞 자식은 부모 키 시각 무렵 그 부모 목록의 맨 앞에 올라왔습니다.

### 증명하지 못하는 것

- 폴더를 두 번 클릭해 열었다는 사실. 고르기만 해도 생긴 버전이 있습니다.
- 폴더 안의 파일을 보거나 열었다는 사실. 셸백은 폴더 단위 기록입니다.
- 사람이 직접 했다는 사실. 탐색기 동작이나 명령으로 생긴 사례가 있습니다.
- 지금 디스크의 같은 이름 폴더와 같은 폴더라는 사실.
- 셸백이 없으니 그 폴더에 가지 않았다는 사실.
- 그 계정을 쓴 사람이 누구인지. 계정과 사람을 잇는 법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 에 있습니다.

### 문장 예

- 쓰면 안 되는 문장: "사용자는 `E:\기밀` 폴더를 열어 내용을 확인했습니다."
- 쓸 수 있는 문장: "사용자 A 의 UsrClass.dat 셸백에 `E:\기밀` 경로가 있습니다. 이 기록은 A 의 로그온 환경에서 탐색기가 이 폴더를 다룬 적이 있음을 보여 줍니다. 이 기록만으로는 폴더를 열었는지, 안의 파일을 열었는지 알 수 없습니다."

## 8. 직접 확인해 보기 — 같은 버전에서 재현하기

셸백이 생기는 조건은 버전마다 다르고, Windows 11 처럼 새 버전은 동작이 또 다를 수 있습니다. 판단이 결과를 바꾸는 항목이면 사건 환경과 가까운 환경에서 아래처럼 직접 확인합니다.

1. 분석 대상과 같은 Windows 판·빌드를 가상 머신에 설치합니다. 판·빌드는 [시스템 기본 정보](../../system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 확인합니다.
2. 새 사용자 계정으로 로그온합니다. 기존 항목이 섞이지 않게 하려는 것입니다.
3. 확인할 동작 하나만 합니다(예: 폴더 한 번 클릭). 동작한 시각을 UTC 로 적습니다.
4. 가상 머신을 끄고 디스크에서 UsrClass.dat·NTUSER.DAT 와 각 `.LOG1`·`.LOG2` 를 꺼냅니다.
5. 동작 전 사본과 비교합니다. 새 키, 번호 값, MRUListEx 순서, 키 시각이 어떻게 바뀌었는지 봅니다.
6. 동작을 하나씩 바꿔 되풀이합니다. 한 번에 두 동작을 섞지 않습니다.
7. 결과를 "(Windows 판·빌드 기준)" 와 함께 보고서에 적습니다.

## 9. 교차 검증 — 함께 볼 아티팩트

| 확인할 것 | 볼 아티팩트 |
|---|---|
| 폴더 안 파일을 실제로 열었나 | [바로가기 파일 (LNK)](../lnk.md), [점프리스트](../jump-lists.md), [최근 문서 (RecentDocs)](../recentdocs.md) |
| 열기·저장 대화상자로 다뤘나 | [열기·저장 대화상자 기록 (ComDlg32)](../comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) |
| 주소창에 경로를 직접 쳤나 | [탐색기 입력 기록 (TypedPaths·WordWheelQuery)](../typedpaths-wordwheelquery.md) |
| 같은 폴더인가, 언제 생기고 지워졌나 | [$MFT](../../filesystem/mft.md), [$UsnJrnl](../../filesystem/usnjrnl.md), [$I30](../../filesystem/i30.md) |
| 드라이브 문자가 어느 장치였나 | [MountedDevices](../../external-devices/usb-storage-artifacts/mounteddevices.md), [MountPoints2](../../external-devices/usb-storage-artifacts/mountpoints2.md) |
| 셸백이 언제 처음 생겼나 | [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 옛 UsrClass.dat 사본끼리 비교 |
| 그 시각 누가 로그온해 있었나 | [로그온·로그오프 (Logon Events)](../../event-logs/logon-events/index.md) |

## 10. 실습

공개 이미지(예: NIST CFReDS 의 Data Leakage Case, Windows 7)로 풀어 봅니다.

1. 사용자의 UsrClass.dat 와 NTUSER.DAT 에서 셸백을 뽑습니다. 공개 도구 두 가지의 항목 수와 경로가 같습니까? 다르다면 어느 항목이 다릅니까?
2. 이동식 드라이브 문자로 시작하는 경로를 고릅니다. 그 문자가 어느 장치였는지 다른 아티팩트로 확인할 수 있습니까?
3. 지금 디스크에 없는 폴더의 셸백 경로를 찾습니다. 그 폴더를 "열었다" 고 쓸 근거가 셸백 말고 더 있습니까?
4. 한 BagMRU 키에서 MRUListEx 맨 앞 자식을 찾습니다. 도구가 보여 주는 "마지막 연 때" 가 그 자식에게만 붙어 있습니까?
5. 가상 머신에서 폴더 한 번 클릭·이름 바꾸기·복사를 따로 해 봅니다. 어느 동작이 셸백을 만드는지 적습니다.

## 참고 문헌

- Vincent Lo, "Windows ShellBag Forensics in Depth", SANS Institute (2014) — https://www.sans.org/white-papers/34545/
- Dan Pullega (4n6k), "Shellbags Forensics: Addressing a Misconception (interpretation, step-by-step testing, new findings, and more)" (2013, 2025 갱신) — https://www.4n6k.com/2013/12/shellbags-forensics-addressing.html
- Chad Tilbury, "Computer Forensic Artifacts: Windows 7 Shellbags", SANS DFIR Blog (2011) — https://www.sans.org/blog/computer-forensic-artifacts-windows-7-shellbags/ (지금 주소는 블로그 첫 화면으로 넘어가서 웹 아카이브 사본으로 읽었습니다)
- Harlan Carvey, "DOSDate Time Stamps in Shell Items", Windows Incident Response (2012) — https://windowsir.blogspot.com/2012/10/dosdate-time-stamps-in-shell-items.html
- Joachim Metz, "Windows Shell Item format", libfwsi — https://github.com/libyal/libfwsi/blob/main/documentation/Windows%20Shell%20Item%20format.asciidoc
- Joachim Metz, "Most recently used (MRU)", winreg-kb — https://github.com/libyal/winreg-kb/blob/main/docs/sources/explorer-keys/Most-recently-used.md
