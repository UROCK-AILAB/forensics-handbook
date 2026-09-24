# 계정·로그인 흔적 (Account·Login)

> 위치: [카카오톡 PC (KakaoTalk PC)](index.md) > 계정·로그인 흔적

## 한 줄 요약

카카오톡 PC 는 레지스트리 `HKEY_CURRENT_USER\SOFTWARE\Kakao\KakaoTalk\DeviceInfo\<DATE>` 에 기기 정보를 남깁니다.
계정 폴더의 `login_list.dat` 와 `last_pc_login.dat` 에는 로그인했던 이메일이 남아 있었습니다(관찰).
계정 userId 는 `ActionLogDB.edb` 의 `Common` 표 `userid` 칸에 있습니다(논문).
이 흔적으로 이 기기에서 어느 계정을 썼는지와 대략의 시기를 가늠합니다.

## 무엇을 기록하나

| 흔적 | 위치 | 담는 것 | 근거 |
|---|---|---|---|
| 기기 정보 키 | `HKEY_CURRENT_USER\SOFTWARE\Kakao\KakaoTalk\DeviceInfo\<DATE>` | `sys_uuid`, `hdd_model`, `hdd_serial`, `dev_id` 같은 값 | 논문, 관찰 |
| `login_list.dat` | 계정 폴더 | 로그인했던 이메일 (평문) | 관찰 |
| `last_pc_login.dat` | 계정 폴더 | 이메일과 base64 토큰 (구조 절 참고) | 관찰 |
| `profile.dat` | 계정 폴더 | 키로 감싼 계정 키 재료. 40바이트였습니다 | 관찰 |
| `appstate.dat` | 계정 폴더 | 앱 상태. CBOR 구조이고 약 99KB 였습니다 | 관찰 |
| `ActionLogDB.edb` | 계정 폴더 | 행동 로그와 `Common` 표의 `userid` 칸 | 논문 |
| 계정 폴더 이름 | `users\<40자리 16진수>` | 계정을 가리키는 고유 식별자 | 관찰 |

근거 칸의 "관찰" 은 카카오톡 PC 26.6.0.5208 이 깔린 Windows 11 한 대에서 본 것입니다.
다른 PC·버전에서 같다고 보장하지 못합니다.

## 위치와 버전별 차이

- `HKEY_CURRENT_USER` 는 그 Windows 사용자의 하이브입니다. 증거 이미지에서 사용자 하이브를 찾고 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.
- 계정 폴더의 전체 경로는 [설치 위치와 파일 구성](install-paths-files.md) 에 있습니다.
- `.dat` 파일과 계정 폴더 이름은 26.6.0.5208 한 대에서 본 것입니다. 다른 버전에서 같다고 보장하지 못합니다.

관찰한 PC 에서 카카오톡은 키를 Windows DPAPI 로 저장하지 않았습니다.
카카오 폴더와 레지스트리에서 DPAPI blob 시그니처가 한 건도 나오지 않았습니다.
(확인 범위: 카카오톡 PC 26.6.0.5208, Windows 11 한 대. 다른 버전은 다를 수 있습니다)
DPAPI blob 을 알아보는 법은 [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) 에서 다룹니다.

## 구조

### 기기 정보 키 (`DeviceInfo\<DATE>`)

- 하위 키 이름 `<DATE>` 가 시각 단서입니다(관찰).
- `sys_uuid`·`hdd_model`·`hdd_serial` 은 대화 DB 키의 재료인 기기 지문을 만드는 값입니다(논문). 쓰임은 [대화 DB 암호화와 버전별 차이](chat-db-encryption.md) 에서 다룹니다.
- `dev_id` 값의 뜻은 이번 자료로 확인하지 못했습니다.

### `login_list.dat`

- 로그인했던 이메일이 평문으로 들어 있었습니다(관찰).

### `last_pc_login.dat`

관찰한 파일은 아래 꼴이었습니다. 실제 값 대신 자리 표시만 적었습니다.

```
1|<이메일>|<base64 토큰>
```

- 칸은 `|` 로 나뉩니다.
- 세 번째 칸에는 자동 로그인 토큰으로 보이는 값이 들어 있었습니다(관찰).
- 첫 칸 `1` 의 뜻과 토큰의 만료·범위는 확인하지 못했습니다.

### `profile.dat` 와 `appstate.dat`

- 두 파일은 키로 감싼 값이라 그대로는 읽을 수 없습니다(관찰).
- `profile.dat` 는 계정 키 재료입니다.
- `appstate.dat` 는 CBOR 구조입니다. CBOR 은 JSON 과 비슷한 자료를 이진으로 적는 형식입니다.

### `ActionLogDB.edb` 의 userid

- 복호한 `ActionLogDB.edb` 의 `Common` 표 `userid` 칸에 계정 userId 가 있습니다(논문).
- userId 는 대화 DB 키의 재료이기도 합니다.
- 계정별 키 없이 이 DB 를 읽을 수 있는 경우는 [대화 DB가 안 열릴 때 남는 단서](when-db-wont-open.md) 에서 다룹니다.

### 계정 폴더 이름

- `users\` 아래 40자리 16진수 폴더 이름은 계정을 가리키는 고유 식별자였습니다(관찰).
- 이 이름과 userId 가 어떻게 이어지는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것**

- 이 기기에서 이 이메일·userId 의 계정을 설정하고 썼다는 사실(논문, 관찰)
- 그 대략의 시기. 레지스트리 하위 키 이름과 파일 시각이 근거입니다.

**증명하지 못하는 것**

- 파일·레지스트리 시각은 마지막으로 고친 때일 뿐입니다. 첫 로그인 순간이라고 단정할 수 없습니다.
- 토큰의 정확한 뜻은 알 수 없습니다.
- 그 계정을 실제로 조작한 사람이 누구인지는 알 수 없습니다. 이 물음은 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.

> 보고서 문장 예: "`login_list.dat` 에 이메일 <값> 이 평문으로 남아 있다. 이 파일의 마지막 수정 시각은 <시각> 이다."

## 시각 해석

- `DeviceInfo` 아래 하위 키 이름에 날짜가 들어 있습니다(관찰).
- 이 날짜가 어떤 사건의 시각인지와 어느 시간대 기준인지는 확인하지 못했습니다.
- 레지스트리 키의 마지막 쓰기 시각과 파일 시스템 시각은 마지막으로 고친 때를 보여 줍니다. 첫 로그인 시각이 아닙니다.
- 어떤 동작이 각 파일의 생성·수정 시각을 바꾸는지는 확인하지 못했습니다. 시험 PC 에서 로그인·로그아웃을 해 보며 확인합니다.
- 레지스트리 시각은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에서, 파일 시각은 [마스터 파일 테이블](../../filesystem/mft.md) 에서 다룹니다.

## 함정과 한계

- `last_pc_login.dat` 의 토큰을 비밀번호로 오해하지 않습니다. 토큰이 무엇을 허락하는지는 확인하지 못했습니다.
- 토큰은 자격 증명일 수 있습니다. 보고서에는 값 대신 있다는 사실만 적는 편이 안전합니다.
- 카카오톡이 키를 DPAPI 로 지킨다고 가정하지 않습니다. 관찰한 PC 에서는 DPAPI 를 쓰지 않았습니다.
- 계정 폴더 이름을 userId 로 적지 않습니다. 둘의 관계는 확인하지 못했습니다.

## 직접 분석해 보기

### 헥스로 한 번

1. `login_list.dat` 와 `last_pc_login.dat` 를 헥스 편집기로 엽니다.
2. 이메일 글자가 보이는지 봅니다.
3. 문자 인코딩은 이번 자료로 확인하지 못했습니다. 글자가 깨져 보이면 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 의 후보로 바꿔 봅니다.

### 공개 도구로 한 번

1. 사용자 하이브를 공개 레지스트리 뷰어로 엽니다.
2. `SOFTWARE\Kakao\KakaoTalk\DeviceInfo` 아래 하위 키 이름과 마지막 쓰기 시각을 적습니다.
3. `ActionLogDB.edb` 가 평문인지 먼저 가립니다. 가리는 법은 [대화 DB 암호화와 버전별 차이](chat-db-encryption.md) 에 있습니다.
4. 평문이면 사본을 `sqlite3` 로 열어 userId 를 봅니다.

```sql
SELECT userid FROM Common;
```

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [사용자 프로필 목록](../../system-account/profilelist.md) | 하이브와 데이터 폴더가 어느 Windows 계정의 것인지 |
| [로그온·로그오프](../../event-logs/logon-events/index.md) | 파일·키 시각 무렵 Windows 에 누가 로그온했는지 |
| [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) | 계정을 쓴 사람을 가리는 흐름 |
| [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) | DPAPI blob 이 무엇이고 어떻게 알아보는지 |
| [대화 DB 암호화와 버전별 차이](chat-db-encryption.md) | 기기 정보 값과 userId 가 키 재료로 쓰이는 방식 |

## 실습

카카오톡 PC 가 든 공개 검체는 이번에 확인하지 못했습니다.
시험용 PC 에 카카오톡 PC 를 깔고 아래 질문을 풀어 봅니다.

1. 처음 로그인한 날과 `DeviceInfo` 하위 키 이름의 날짜를 비교합니다. 같습니까?
2. 로그아웃하고 다시 로그인하면 `last_pc_login.dat`·`login_list.dat` 의 수정 시각이 바뀝니까?
3. 두 번째 계정으로 로그인하면 `login_list.dat` 에 이메일이 몇 개 남습니까?
4. `profile.dat` 크기는 계정마다 같습니까?

## 참고 문헌

- 논문: 카카오톡 PC 포렌식 연구 논문(레지스트리 `DeviceInfo` 값, 키 재료, `ActionLogDB.edb` 의 userid), KoreaScience — https://www.koreascience.kr/article/JAKO202530836043843.page
