---
title: "대화 DB 암호화와 버전별 차이"
parent: "카카오톡 PC"
grand_parent: "아티팩트 · 메신저"
nav_order: 2000
---

# 대화 DB 암호화와 버전별 차이 (Chat DB Encryption)

> 위치: [카카오톡 PC (KakaoTalk PC)](index.md) > 대화 DB 암호화와 버전별 차이

## 한 줄 요약

카카오톡 PC 는 대화방마다 대화 기록을 `chatLogs_<대화방 식별자>.edb` 파일에 저장하는데, 확장자는 `.edb` 이지만 형식은 SQLite 입니다. 논문은 25.7.2 미만은 카카오톡 자체 모듈인 EvaSQLite 로, 25.7.2 이상은 SQLCipher 4 로 암호화한다고 적습니다. 실제 파일이 평문인지 암호문인지는 첫 16바이트를 보면 바로 갈립니다.

## 무엇을 기록하나 · 왜 생기나

`chatLogs_<대화방 식별자>.edb` 파일 하나에 대화방 하나의 대화 기록이 들어 있습니다(논문). 관찰한 PC 에서 이 DB 에는 `message`·`authorId`·`threadId` 칸과 시각 칸이 있었습니다(카카오톡 PC 26.6.0.5208 기준). 대화방 목록과 연락처는 다른 DB 에 따로 있고, 파일 이름과 위치는 [설치 위치와 파일 구성](install-paths-files.md) 에 정리했습니다.

## 위치와 버전별 차이

암호화 방식은 카카오톡 버전에 따라 다릅니다.

| 카카오톡 버전 | 암호화 방식 | 알고리즘과 키 | 근거 |
|---|---|---|---|
| 25.7.2 미만 | 카카오톡 자체 모듈 EvaSQLite | AES-128-CBC. 키와 초기화 벡터 (Initialization Vector, IV) 는 MD5 로 만듭니다 | 논문 |
| 25.7.2 이상 | SQLCipher 4 | 아래 "SQLCipher 로 암호화한 파일" 절 | 논문, SQLCipher 설계 문서 |

논문이 나눈 경계는 카카오톡 버전입니다.
Windows 버전에 따른 차이는 확인하지 못했습니다.

관찰한 PC 에서는 파일마다 상태가 달랐습니다.

활성 `chatLogs_*.edb` 다수가 디스크에 평문 SQLite 로 있었고 첫 16바이트가 `SQLite format 3` 이었습니다. 이 파일들은 로그인하지 않고 키도 없이 그대로 열렸습니다. 반면 `TalkUserDB.edb` 같은 연락처·계정 DB 와 일부 파일은 암호문이었습니다.

카카오톡 PC 26.6.0.5208 기준입니다. 이 모습은 저장 방식을 바꾸는 도중의 상태일 수 있으므로, 모든 PC·버전에서 대화 DB 가 평문이라고 일반화하지 않습니다.

## 구조

### 평문 SQLite 파일의 머리

| 오프셋 | 크기 (바이트) | 뜻 |
|---|---|---|
| 0 | 16 | `"SQLite format 3\0"` 문자열 (`53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00`) |
| 16 | 2 | 페이지 크기 |
| 18 | 1 | 쓰기 버전. 1 이면 롤백 저널, 2 이면 WAL |
| 19 | 1 | 읽기 버전 |
| 20 | 1 | 페이지마다 끝에 비워 두는 바이트 수 |

위 표는 SQLite 파일 형식 문서에서 가져왔습니다.
머리 전체와 페이지 구조는 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

### SQLCipher 로 암호화한 파일

SQLCipher 는 SQLite 파일을 머리까지 통째로 암호화합니다(SQLCipher 설계 문서).
그래서 첫 바이트부터 무작위 값처럼 보이고, `SQLite format 3` 문자열이 없습니다.

- 파일 첫 16바이트는 솔트 (Salt) 입니다.
- 페이지 단위로 AES-256-CBC 암호화를 합니다.
- 페이지마다 끝에 난수 IV 와 무결성 확인 값(HMAC-SHA512)을 둡니다.
- 비밀번호에서 키를 만들 때는 기본으로 PBKDF2-HMAC-SHA512 를 256,000번 돌립니다.
- 응용 프로그램이 이미 만든 키(raw 키)를 바로 넣으면 이 단계를 건너뜁니다.

256,000번은 SQLCipher 의 기본값입니다.
카카오톡이 이 기본값을 그대로 쓰는지는 이 페이지의 자료로 확인하지 못했습니다.

### EvaSQLite 로 암호화한 파일

EvaSQLite 로 암호화한 파일의 머리 모양은 이번 자료로 확인하지 못했지만, 판별 기준은 같아서 첫 16바이트가 `SQLite format 3\0` 이 아니면 평문 SQLite 가 아닙니다.

### 키 재료

EvaSQLite 키는 기기 지문과 계정 userId 를 섞어 만듭니다(논문).

- 기기 지문 (논문 용어 "Pragma") 은 메인보드 UUID 와 저장장치 모델·시리얼로 만듭니다.
- 이 값은 레지스트리 `DeviceInfo` 키의 `sys_uuid`·`hdd_model`·`hdd_serial` 에서 옵니다. 키 전체 경로는 [계정·로그인 흔적](account-login.md) 에 있습니다.
- userId 가 어디 있는지도 [계정·로그인 흔적](account-login.md) 에서 다룹니다.
- 패스프레이즈를 짜는 방식은 여러 가지이고, 씨앗 값도 들어갑니다. 세부는 논문이 정리했습니다. 이 핸드북은 그 값을 옮기지 않습니다.

25.7.2 이상에서 SQLCipher 키를 무엇으로 만드는지는 이 페이지에서 다루지 않습니다.

### 전원을 끈 디스크만으로 읽히는가

- 평문 파일은 키 없이 바로 열립니다.
- 25.7.2 이상에서 SQLCipher 로 암호화한 대화 DB 를 전원을 끈 뒤 만든 디스크 이미지만으로 푸는 공개된 방법은 이번에 연 자료에서 찾지 못했습니다.
- 논문의 복호 방법은 25.7.2 미만에 맞춘 것입니다. 25.7.2 이상으로 업데이트하면 계정 폴더가 `<계정 폴더>_backup_<백업 시각>` 으로 이름이 바뀌고, 논문의 방법은 이 백업 폴더에만 적용됩니다.
- 암호문을 풀려면 키가 있어야 합니다. 키를 얻는 절차는 이 핸드북 범위 밖입니다.
- 메모리 이미지를 다루는 법은 [메모리 분석](../../../03-techniques/analysis/memory-forensics/index.md) 에서, 암호문을 다루는 일반 절차는 [암호화 증거 다루기](../../../03-techniques/analysis/encrypted-evidence/index.md) 에서 다룹니다.
- 키 없이 볼 수 있는 다른 단서는 [대화 DB가 안 열릴 때 남는 단서](when-db-wont-open.md) 에 모았습니다.

## 증거로서 의미

**증명하는 것**

- 이 대화방 DB 에 이런 메시지·발신자 ID·시각의 기록이 남아 있다는 사실

**증명하지 못하는 것**

- 파일이 평문이라는 사실이 "카카오톡은 원래 평문으로 저장한다" 는 뜻은 아닙니다. 저장 방식을 바꾸는 도중의 상태일 수 있습니다.
- 발신자 ID 가 누구인지는 연락처 DB 와 맞춰 봐야 압니다.
- 기록이 남아 있다는 사실과 사용자가 그 메시지를 읽었다는 사실은 다릅니다.
- 암호문이라 열지 못했다고 해서 대화가 없었다는 뜻은 아닙니다.

보고서에는 기록이 말하는 만큼만 씁니다.

> 예: "`chatLogs_<대화방 식별자>.edb` 에 <처음 시각>부터 <마지막 시각>까지 발신자 ID <값> 의 메시지 기록 N건이 남아 있다."

## 시각 해석

- 메시지 시각 칸이 어떤 형식인지는 이번 자료로 확인하지 못했습니다.
- 값을 풀 때는 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 의 후보와 맞춰 봅니다. 시험 PC 에서 알고 있는 시각에 보낸 메시지로 검증합니다.
- `.edb` 파일의 파일 시스템 시각은 DB 파일이 바뀐 때를 보여 줄 뿐입니다. 메시지 하나하나의 시각이 아닙니다.
- 최근 변경이 아직 `-wal` 에만 있으면 주 파일의 수정 시각이 마지막 메시지보다 이를 수 있습니다.

## 함정과 한계

- `.edb` 를 ESE 로 오인해 ESE 도구로 열면 실패합니다. SQLite 로 엽니다(논문, 관찰). ESE 형식의 `.edb` 는 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다.
- 도구나 문서가 "암호화 대상" 이라고 해도 먼저 첫 16바이트를 봅니다. 관찰한 PC 에서는 대화 DB 다수가 평문이었습니다.
- 같은 계정 폴더 안에서도 파일마다 평문·암호문이 다를 수 있습니다.
- 한 PC 의 관찰을 모든 PC·버전으로 넓히지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 파일 형식 문서와 SQLCipher 설계 문서로 만든 예시입니다.
실제 검체에서 뽑은 값이 아닙니다.

평문 SQLite 파일입니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
00000010  PP PP WW RR NN .. .. .. .. .. .. .. .. .. .. ..
```

- `PP PP` 는 오프셋 16~17 의 페이지 크기입니다.
- `WW` 는 오프셋 18 의 쓰기 버전입니다.
- `RR` 은 오프셋 19 의 읽기 버전입니다.
- `NN` 은 오프셋 20 의 페이지 끝 예약 바이트 수입니다.

SQLCipher 로 암호화한 파일입니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000000  ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??   (솔트 16바이트)
00000010  ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??   (암호문)
```

- 첫 16바이트가 무작위 솔트라서 `SQLite format 3` 문자열이 보이지 않습니다.

### 공개 도구로 한 번

1. 원본이 아닌 사본에서 작업합니다.
2. 헥스 편집기나 `xxd -l 16 <파일>` 로 첫 16바이트를 봅니다.
3. 파일이 많으면 아래 파이썬 스크립트로 한꺼번에 가립니다.

```python
from pathlib import Path

MAGIC = b"SQLite format 3\x00"
root = Path(r"<사본 폴더>\KakaoTalk\users")
for p in sorted(list(root.rglob("*.edb")) + list(root.rglob("*.backup"))):
    with p.open("rb") as f:
        head = f.read(16)
    print("평문 SQLite" if head == MAGIC else "평문 아님", p)
```

4. 평문이면 `sqlite3 <사본> ".tables"` 로 표 목록을 보고, `.schema` 로 칸을 봅니다.
5. 평문이 아니면 SQLite 도구로 열리지 않습니다. 키 없이 볼 단서는 [대화 DB가 안 열릴 때 남는 단서](when-db-wont-open.md) 에서 찾습니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [계정·로그인 흔적](account-login.md) | 키 재료인 기기 정보 레지스트리 값과 userId 위치 |
| [받은 파일·사진 폴더](received-files.md) | 같은 모듈로 암호화한 `.cng` 이미지 |
| [대화 DB가 안 열릴 때 남는 단서](when-db-wont-open.md) | 평문 백업과 `-wal` 처럼 키 없이 볼 수 있는 단서 |
| [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) | 머리 전체, WAL, 지운 행을 찾는 법 |
| [누구와 연락을 주고받았나](../../../04-scenarios/activity/communication-reconstruction.md) | 대화 기록을 다른 연락 흔적과 맞추는 흐름 |

## 실습

카카오톡 PC 가 든 공개 검체는 이번에 확인하지 못했으므로, 시험용 PC 에 카카오톡 PC 를 깔고 아래 질문을 풀어 봅니다.

1. `chatLogs_*.edb` 가운데 첫 16바이트가 `SQLite format 3` 인 파일은 몇 개입니까?
2. 평문 파일의 `authorId` 값은 연락처 DB 의 어느 값과 이어집니까?
3. 알고 있는 시각에 보낸 메시지 하나를 찾아, 시각 칸이 어떤 형식인지 알아냅니다.
4. 카카오톡을 업데이트하기 전과 뒤에 같은 파일의 첫 16바이트가 바뀝니까?

## 참고 문헌

- 논문: 카카오톡 PC 포렌식 연구 논문(EvaSQLite·SQLCipher, 버전 경계·키 파생·파일/레지스트리 경로), KoreaScience — https://www.koreascience.kr/article/JAKO202530836043843.page
- SQLite 파일 형식 문서: SQLite, "Database File Format"(파일 머리 문자열, 오프셋 16·18·19·20), SQLite.org — https://www.sqlite.org/fileformat.html
- SQLCipher 설계 문서: Zetetic, "SQLCipher Design"(파일 전체 암호화, 페이지별 IV·HMAC-SHA512, AES-256-CBC, PBKDF2-HMAC-SHA512, raw 키), Zetetic — https://www.zetetic.net/sqlcipher/design/
