# 암호화된 SQLite (SQLCipher)

> 위치: [SQLite 데이터베이스 (SQLite)](index.md) > 암호화된 SQLite

## 한 줄 요약

SQLCipher 는 SQLite 파일을 페이지마다 따로 AES-256 으로 암호화하는 오픈소스 라이브러리이고, 파일 안에 평문으로 남는 것은 첫 16바이트의 솔트뿐입니다.
키와 설정 값은 파일에 없고 앱이 정하므로, 이 형식을 읽는 일은 대부분 "앱이 어떤 키와 설정을 썼는지" 를 찾는 일입니다.

## 이 형식을 쓰는 아티팩트

SQLCipher 는 Windows 구성 요소가 아니라 앱이 SQLite 대신 넣어서 쓰는 라이브러리라서, Windows 버전에 따른 차이는 없습니다.
차이는 앱이 쓰는 SQLCipher 버전과 설정에서 생깁니다.

대화 기록을 보호하려는 메신저가 주로 씁니다.
시그널 데스크톱은 `C:\Users\<사용자>\AppData\Roaming\Signal\sql\db.sqlite` 를 SQLCipher 로 암호화하고, 키는 같은 `Signal` 폴더의 `config.json` 에 있습니다.
예전 버전은 64자리 16진 키를 `key` 항목에 평문으로 적었지만, 지금 버전은 키를 암호화해 `encryptedKey` 항목에 두고 그 키를 푸는 키를 `Local State` 파일에 DPAPI 로 보호해 둡니다.
이 방식은 크롬 계열의 키 보호와 같으며 자세한 내용은 [쿠키·비밀번호 암호화 (DPAPI·App-Bound Encryption)](../../app-mail-data/chromium-electron-webview2/dpapi-app-bound-encryption.md) 와 [시그널 (Signal)](../../../02-artifacts/messengers/signal.md) 에 있습니다.

SQLite 를 암호화하는 확장은 SQLCipher 말고도 SQLite 개발진이 만든 SEE (SQLite Encryption Extension) 와 여러 암호 방식을 한데 모은 SQLite3 Multiple Ciphers 가 있으며, 겉으로 보면 모두 무작위 바이트처럼 보입니다.
대화 DB 를 암호화하는 방식은 메신저마다 다르므로 각 아티팩트 페이지를 함께 봅니다. 예: [대화 DB 암호화와 버전별 차이 (카카오톡 PC)](../../../02-artifacts/messengers/kakaotalk-pc/chat-db-encryption.md)

## 구조

평문 SQLite 의 페이지 구조는 [파일·페이지 구조 (B-tree·Record Format)](b-tree-record-format.md) 에 있고, 여기서는 SQLCipher 가 바꾸는 부분만 적습니다.

### 파일 전체

헤더 문자열 `SQLite format 3\0` 자리인 첫 16바이트에는 무작위 솔트 (Salt) 를 두며, 이 16바이트는 암호화하지 않습니다.
나머지는 페이지마다 따로 AES-256-CBC 로 암호화하고, 페이지 끝에 잡은 SQLite 의 예약 공간 (Reserved Space) 에 IV 와 HMAC 을 둡니다.
IV 는 페이지를 쓸 때마다 새로 뽑습니다.
첫 페이지의 암호화는 16바이트 뒤부터 시작하므로 페이지 크기·예약 크기가 적힌 헤더 16\~23바이트도 암호문 안에 들어가고, 결과적으로 파일만 보고는 페이지 크기도 알 수 없습니다.

### 페이지 한 개의 배치

아래 표는 SQLCipher 4.x 기본값(페이지 크기 4096, 예약 80바이트) 기준입니다. 위치는 페이지 시작에서 잰 값입니다.

| 페이지 안 위치 | 크기 | 첫 페이지 | 둘째 페이지부터 |
|---|---|---|---|
| 0x000–0x00F | 16 | 솔트 (평문) | 암호문 |
| 0x010–0xFAF | 4000 | 암호문 | 암호문 |
| 0xFB0–0xFBF | 16 | IV | IV |
| 0xFC0–0xFFF | 64 | HMAC-SHA512 | HMAC-SHA512 |

둘째 페이지부터는 0x000–0xFAF 의 4016바이트가 모두 암호문이고, IV 자리는 모든 페이지에서 같아서 페이지 끝에서 예약 크기만큼 앞입니다.
HMAC 은 그 페이지의 암호문과 IV 에 4바이트 페이지 번호(기본은 리틀 엔디언)를 붙여 계산하며, 첫 페이지의 HMAC 계산에는 솔트 16바이트가 들어가지 않습니다.
페이지 번호가 HMAC 에 들어가므로 페이지 순서를 바꾸면 검사에 걸립니다.
예약 공간에서 IV 와 HMAC 을 채우고 남은 자리에는 무작위 바이트가 들어갑니다.

> 그림 자리: SQLCipher 4.x 기본값에서 첫 페이지와 둘째 페이지의 바이트 배치(솔트·암호문·IV·HMAC)를 나란히 비교

### 키를 만드는 방법

앱이 비밀번호 (Passphrase) 를 넘기면 PBKDF2 로 솔트와 섞어 32바이트 암호화 키를 만듭니다.
HMAC 키는 따로 만드는데, 암호화 키를 입력으로 넣고 솔트의 각 바이트를 0x3A 와 XOR 한 값을 솔트로 쓰며 반복은 2회입니다.
앱이 원시 키 (Raw Key) 를 넘기면 PBKDF2 를 건너뜁니다.
원시 키는 `x'…'` 꼴의 16진 문자열이고, 64자리면 암호화 키 32바이트이며 96자리면 앞 32바이트가 키, 뒤 16바이트가 솔트입니다.

### 버전별 기본값

| 항목 | 1.x | 2.x | 3.x | 4.x |
|---|---|---|---|---|
| 페이지 크기 | 1024 | 1024 | 1024 | 4096 |
| 키 유도 | PBKDF2-HMAC-SHA1 | PBKDF2-HMAC-SHA1 | PBKDF2-HMAC-SHA1 | PBKDF2-HMAC-SHA512 |
| 반복 횟수 | 4,000 | 4,000 | 64,000 | 256,000 |
| 페이지 HMAC | 없음 | HMAC-SHA1 (20바이트) | HMAC-SHA1 (20바이트) | HMAC-SHA512 (64바이트) |
| 예약 크기 | 16 | 48 | 48 | 80 |

예약 크기는 IV 16바이트에 HMAC 길이를 더하고 AES 블록 크기(16)의 배수로 올린 값입니다. 2.x·3.x 는 16 + 20 = 36 을 올려 48 이 됩니다.
이 값들은 파일 어디에도 적혀 있지 않고, 앱은 기본값 대신 반복 횟수·페이지 크기·해시 종류를 바꿔 쓸 수 있습니다.

### 평문 헤더 설정

4.x 에는 첫 페이지 앞부분을 평문으로 두는 설정(`cipher_plaintext_header_size`)이 있습니다.
공식 문서가 권하는 크기는 32바이트이며, 헤더 문자열과 페이지 크기·읽기/쓰기 버전이 이 안에 들어갑니다.
이 설정을 쓰면 파일이 `SQLite format 3\0` 으로 시작하지만, 솔트가 파일에 없어서 앱이 솔트를 따로 보관하고 연결할 때 넘깁니다.

### 딸린 파일

딸린 파일 자체의 구조는 [WAL과 롤백 저널 (-wal·-journal·-shm)](wal-journal-shm.md) 에 있습니다.

| 파일 | 평문으로 남는 부분 | 암호화하는 부분 |
|---|---|---|
| -wal | WAL 헤더 32바이트, 프레임 헤더 24바이트 | 프레임에 담긴 페이지 내용 |
| -journal | 저널 헤더, 기록마다 붙는 페이지 번호·검사합 | 저널에 담긴 원래 페이지 |
| -shm | 전부 (페이지 내용이 들어 있지 않은 색인 파일) | 없음 |

페이지 내용은 DB 파일과 같은 키로 암호화합니다.
헤더는 평문으로 쓰고 페이지 내용만 암호화해 붙이는 흐름은 SQLCipher 소스(`wal.c`·`pager.c`)로 확인했습니다.

## 읽는 법

1. **사본을 만듭니다.** DB 파일과 -wal·-journal·-shm 을 함께 복사합니다. SQLite 는 마지막 연결을 닫을 때 -wal 을 DB 에 합치고 지울 수 있습니다. 원본은 열지 않습니다.
2. **형식을 가립니다.**
   - 첫 16바이트가 `SQLite format 3\0` 이 아니고, 파일 전체가 무작위 바이트처럼 보입니다.
   - 파일 크기가 페이지 크기의 배수인지 봅니다. 3.x 이하 기본값이면 1024, 4.x 기본값이면 4096 의 배수입니다.
   - 같은 이름의 -wal 이 있으면 그 헤더를 봅니다. 앞 4바이트가 0x377F0682 또는 0x377F0683 이면 SQLite WAL 입니다.
   - WAL 헤더 오프셋 8 의 4바이트(빅 엔디언)가 페이지 크기입니다. DB 파일에서 못 읽는 페이지 크기를 여기서 얻습니다.
   - 이것만으로는 SQLCipher 인지 다른 암호화 확장인지 가리지 못합니다. 앱 폴더의 라이브러리 이름과 앱 버전으로 좁힙니다. 암호화 파일을 찾는 일반 방법은 [암호화 컨테이너 찾기](../../../03-techniques/analysis/encrypted-evidence/encrypted-container-detection.md) 에 있습니다.
3. **키를 구합니다.** 키는 앱마다 다른 곳에 있습니다. 설정 파일, DPAPI 로 보호한 값, 실행 중인 앱의 메모리가 흔한 자리입니다. [DPAPI 구조](../../protection/data-protection-api/index.md) 와 [메모리 속 문자열·자격증명·암호 키](../../../03-techniques/analysis/memory-forensics/strings-credentials-keys.md) 를 봅니다.
4. **첫 페이지로 키와 설정을 확인합니다.**
   - 오프셋 0x10 의 암호문 첫 블록(16바이트)과 첫 페이지의 IV 만 있으면 헤더 16\~31바이트를 풀 수 있습니다.
   - 푼 16\~23바이트가 SQLite 헤더 규칙에 맞으면 키와 설정이 맞습니다.
   - 21·22·23번 바이트는 늘 64·32·32 입니다.
   - 20번 바이트는 예약 크기입니다. 4.x 기본값이면 80, 2.x·3.x 기본값이면 48 입니다. 이 값으로 버전 설정을 확인합니다.
5. **복호 방식을 고릅니다.** 지운 레코드까지 보려면 페이지 단위로 풉니다. 이유는 아래 "포렌식에서 중요한 점" 에 있습니다.
6. **기록합니다.** 쓴 키의 출처, 버전 설정, 복호 방식, -wal 포함 여부를 적습니다.

### 헥스로 한 번 따라가기

아래 바이트는 **명세로 만든 예시**입니다. 실제 검체에서 나온 값이 아닙니다. `??` 는 파일마다 다른 무작위 바이트입니다.

```
암호화된 DB 파일, 첫 페이지 (명세로 만든 예시, SQLCipher 4.x 기본값)
00000000  ?? ?? ?? ?? ?? ?? ?? ??  ?? ?? ?? ?? ?? ?? ?? ??   솔트 16바이트 (평문)
00000010  ?? ?? ?? ?? ?? ?? ?? ??  ?? ?? ?? ?? ?? ?? ?? ??   암호문 첫 블록 → 헤더 16~31바이트
   ...                                                       암호문 (0x0FAF 까지)
00000FB0  ?? ?? ?? ?? ?? ?? ?? ??  ?? ?? ?? ?? ?? ?? ?? ??   IV 16바이트
00000FC0  ?? ?? ?? ?? ...                                    HMAC-SHA512 64바이트 (0x0FFF 까지)
```

```
복호한 첫 페이지의 앞 24바이트 (명세로 만든 예시, WAL 모드 가정)
00000000  53 51 4C 69 74 65 20 66  6F 72 6D 61 74 20 33 00   SQLite format 3.
00000010  10 00 02 02 50 40 20 20
```

- 첫 16바이트는 복호할 때 헤더 문자열로 채워 넣습니다. 파일에 있던 솔트는 이 자리에서 사라집니다.
- 오프셋 16 의 `10 00` 은 페이지 크기 4096 입니다(빅 엔디언).
- 오프셋 18·19 의 `02 02` 는 WAL 모드입니다. 롤백 저널 모드면 `01 01` 입니다.
- 오프셋 20 의 `50` 은 예약 크기 80 입니다.
- 오프셋 21\~23 의 `40 20 20` 은 64·32·32 입니다.
- 키가 틀리면 이 여덟 바이트가 규칙에 맞게 나올 일은 거의 없습니다.

## 포렌식에서 중요한 점

### 지운 데이터

복호한 페이지 안은 평문 SQLite 와 같으므로 지운 레코드도 [파일 안에 남은 지운 레코드 (Freelist·Freeblock)](freelist-freeblock.md) 와 같은 방법으로 찾습니다.
다만 복호 방식에 따라 이 흔적이 남기도 하고 사라지기도 합니다.
`sqlcipher_export()` 나 `VACUUM` 으로 평문 DB 를 새로 만들면 살아 있는 레코드만 옮겨지고 빈 페이지와 Freeblock 은 따라오지 않지만, 페이지마다 풀어서 같은 위치에 쓰면 배치가 그대로 남습니다.
이렇게 만든 파일은 푼 헤더의 20번 바이트가 이미 예약 크기를 가리키므로 일반 SQLite 로 열리고, SQLite 는 페이지 끝의 IV·HMAC 을 예약 공간으로 보고 건너뜁니다.
디스크의 비할당 영역에 남은 옛 페이지는 무작위 바이트라 서명으로 찾을 수 없지만, 키가 있으면 이런 페이지도 풀 수 있습니다.
CBC 복호에는 키와 그 페이지 끝의 IV 만 필요하고 페이지 번호는 HMAC 검사에만 쓰입니다. 조각을 모으는 방법은 [레코드 카빙](../../../03-techniques/analysis/data-recovery/record-carving.md) 을 봅니다.

### 비정상 종료와 딸린 파일

앱이 체크포인트 전에 꺼지면 최근 변경은 -wal 에만 있습니다.
-wal 의 페이지도 같은 키로 풀리며, 한 페이지의 옛 판이 여러 프레임에 남아 있을 수 있습니다.
-journal 에 남은 페이지는 바뀌기 전 내용이고 이것도 같은 키로 풀립니다.
키가 없어도 -wal 의 프레임 헤더는 읽히므로 어느 페이지 번호가 몇 번 기록되었는지, 커밋이 어디서 끊기는지는 알 수 있지만, 그 페이지에 무엇이 적혔는지는 알 수 없습니다.

### 손상

SQLCipher 는 페이지를 읽다 HMAC 이 맞지 않으면 그 연결 전체를 오류 상태로 만들기 때문에, 페이지 하나만 깨져도 SQL 로는 아무것도 못 읽을 수 있습니다.
`PRAGMA cipher_integrity_check` 는 모든 페이지의 HMAC 을 검사해 맞지 않는 페이지 번호를 알려 주지만, 1.x 처럼 HMAC 이 없는 설정에서는 쓸 수 없습니다.
깨진 페이지를 건너뛰고 나머지를 페이지 단위로 풀면 더 많이 건집니다.

### 시각

SQLCipher 층에는 시각 값이 없고, 시각은 풀어낸 레코드 안에 앱이 적은 값뿐입니다. 형식은 [시각 값 형식](../../value-decoding/filetime-unix-webkit-dos-ole.md) 을 봅니다.
IV 를 쓸 때마다 새로 뽑으므로 같은 내용을 다시 써도 페이지 바이트가 모두 바뀌고, 그래서 섀도 복사본 속 옛 DB 와 지금 DB 를 페이지 단위로 비교하면 키 없이도 어느 페이지를 다시 썼는지 알 수 있습니다.
무엇이 바뀌었는지는 키 없이 알 수 없습니다. 비교 방법은 [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에 있습니다.

## 함정

- **오류만 보고 키가 틀렸다고 단정합니다.** 키가 틀려도, 버전 설정이 틀려도 대개 같은 오류 `file is not a database` 가 납니다. 페이지 크기·반복 횟수·해시 종류·평문 헤더 설정을 바꿔 가며 다시 확인합니다.
- **`PRAGMA key` 가 성공했으니 키가 맞다고 봅니다.** `PRAGMA key` 는 키가 틀려도 바로 오류를 내지 않습니다. 첫 읽기에서 오류가 납니다. 공식 문서는 `SELECT count(*) FROM sqlite_master;` 로 확인하라고 합니다.
- **증거 원본에 `PRAGMA cipher_migrate` 를 씁니다.** 이 명령은 옛 버전 DB 를 4.x 형식으로 바꿔 파일을 다시 씁니다. 옛 버전 파일은 사본에서 `cipher_compatibility` 설정으로 엽니다.
- **헤더 문자열이 보이니 평문이라고 봅니다.** 평문 헤더 설정을 쓴 SQLCipher 파일일 수 있습니다. 이때는 솔트도 앱에서 따로 구해야 합니다.
- **무차별 대입부터 시작합니다.** 앱이 무작위 32바이트 원시 키를 쓰면 대입은 소용없습니다. 키를 보관하는 자리를 찾는 편이 빠릅니다.
- **비밀번호 방식이면 쉽게 풀린다고 봅니다.** 4.x 기본값은 추측 하나마다 PBKDF2-HMAC-SHA512 를 256,000 번 돌립니다. [비밀번호 복구](../../../03-techniques/analysis/encrypted-evidence/password-recovery.md) 를 봅니다.
- **전원부터 끕니다.** 키를 메모리에서만 얻을 수 있는 앱도 있습니다. 켜진 PC 라면 메모리를 확보할지 먼저 정합니다. [메모리 덤프 확보](../../../03-techniques/analysis/memory-forensics/memory-acquisition.md) 를 봅니다.
- **복호 결과의 행 수를 그대로 비교합니다.** 내보내기와 페이지 단위 복호, -wal 포함 여부에 따라 결과가 다릅니다. 어떻게 풀었는지를 보고서에 함께 씁니다.

## 도구

아래 공개 도구는 예로만 듭니다. 한 도구의 결과에만 기대지 않습니다.

| 도구 | 쓰임 |
|---|---|
| SQLCipher 명령행 셸 (`sqlcipher`) | 키와 버전 설정을 주고 열어 보거나 평문 DB 로 내보냅니다 |
| DB Browser for SQLite (SQLCipher 빌드) | 비밀번호·원시 키와 버전 설정을 골라 열어 봅니다 |
| SQLite3 Multiple Ciphers | SQLCipher 호환 설정(버전·반복 횟수 등)을 따로 지정해 엽니다 |
| 일반 암호 라이브러리 (Python 등) | PBKDF2·AES-CBC·HMAC 으로 페이지 단위 복호를 직접 짭니다. 위의 구조 표가 그대로 명세입니다 |
| 헥스 편집기 | 첫 16바이트, 파일 크기, -wal 헤더를 직접 봅니다 |

결과가 서로 다르면 먼저 복호 방식과 -wal 포함 여부를 비교하며, 검증 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 에 있습니다.

## 참고 문헌

- Zetetic, *SQLCipher Design* — https://www.zetetic.net/sqlcipher/design/
- Zetetic, *SQLCipher API* — https://www.zetetic.net/sqlcipher/sqlcipher-api/
- SQLCipher 소스 코드 `src/sqlcipher.c`·`src/wal.c`·`src/pager.c` (4.19.0 기준) — https://github.com/sqlcipher/sqlcipher
- SQLite, *Database File Format* — https://www.sqlite.org/fileformat2.html
- Ulrich Telle, SQLite3 Multiple Ciphers, *SQLCipher: AES 256 Bit* — https://utelle.github.io/SQLite3MultipleCiphers/docs/ciphers/cipher_sqlcipher/
- Jeremy's Blog, *HowTo - Decryption of Signal Messages on Windows* (2025) — https://stolenfootball.github.io/posts/research/2025/signal_windows_decryption/
