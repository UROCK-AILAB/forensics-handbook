# 비밀번호 변경 기록 (CREDHIST)

> 위치: [DPAPI 구조 (Data Protection API)](/01-foundations/protection/data-protection-api/index.md) > CREDHIST

## 한 줄 요약

CREDHIST 파일은 사용자가 암호를 바꿀 때마다 이전 암호의 해시를 새 암호로 감싸 이어 붙인 사슬입니다.
목적은 옛 암호로 감싼 옛 마스터키를 지금 암호로 풀 수 있게 하는 것입니다.
포렌식에서는 이 파일 하나에서 이전 암호들의 SHA-1 해시를 한꺼번에 얻을 수 있습니다.

> 마스터키가 CREDHIST 를 왜 필요로 하는지는 [마스터키 파일](/01-foundations/protection/data-protection-api/master-key-protect-sid.md) 에 있습니다.
> 이 글은 CREDHIST 파일 자체의 구조와 쓰임을 다룹니다.

## 무엇을 담나 · 왜 생기나

- 사용자가 암호를 바꾸면 Windows 는 이전 암호의 SHA-1 해시를 새 암호로 암호화합니다.
- 그 결과를 CREDHIST 파일 끝에 덧붙입니다.
- 그래서 CREDHIST 는 암호를 바꿀 때마다 한 칸씩 자라는 사슬입니다.
- 각 항목은 바로 앞 해시로 암호화됩니다. 사슬의 첫 항목은 현재 암호로 암호화됩니다.

왜 이런 사슬이 필요한지는 마스터키 갱신과 이어집니다.

- 마스터키는 옛 암호로 감싸인 채 남아 있을 수 있습니다.
- 아직 새 암호로 다시 감싸지 않은 마스터키가 그렇습니다.
- 이런 마스터키를 풀려면 그 옛 암호의 SHA-1 이 필요합니다.
- 지금 암호로 CREDHIST 를 풀면 그 옛 SHA-1 을 꺼낼 수 있습니다.
- 한 단계로 안 되면 그 앞 암호로 다시 풉니다. 사슬을 거슬러 올라갑니다.

## 위치

- CREDHIST 파일은 사용자 프로필의 key-ring 폴더, 곧 `%APPDATA%\Microsoft\Protect` 아래에 있습니다.
- 이 폴더 아래에는 [마스터키 파일](/01-foundations/protection/data-protection-api/master-key-protect-sid.md) 이 든 `{SID}` 폴더도 있습니다.

## 구조

공식 명세는 없습니다. 아래 구조는 역공학 자료로 확인한 것입니다. 확인 범위는 Windows 7 까지입니다.

한 항목의 필드입니다. 필드 이름은 역공학 자료의 표기이고, 공개 복호 코드(impacket 의 CREDHIST_ENTRY)는 순서와 이름을 조금 다르게 읽습니다.

| 필드 | 뜻 |
|---|---|
| dwVersion | 버전 |
| guidLink | 다음 링크의 GUID |
| dwNextLinkSize | 다음 링크 크기 |
| dwCredLinkType | 링크 종류 |
| algHash | 해시 알고리즘 ID |
| dwPbkdf2IterationCount | PBKDF2 반복수 |
| dwSidSize | SID 크기 |
| algCrypt | 암호 알고리즘 ID |
| dwShaHashSize | SHA 해시 크기 |
| dwNtHashSize | NT 해시 크기 |
| pSalt (16바이트) | salt |

그 뒤에 가변 길이 데이터가 이어집니다.

| 데이터 | 뜻 |
|---|---|
| pSid | 사용자 SID |
| pShaHash | 이전 암호의 SHA-1 |
| pNtHash | 이전 암호의 NTLM 해시 |
| bPasswordID (16바이트) | 이 항목을 마스터키와 잇는 ID |

- pShaHash·pNtHash 는 앞 해시로 암호화되어 있습니다.
- bPasswordID 는 마스터키 푸터의 credHist GUID 와 짝을 이룹니다.
- SID 형식은 [윈도 식별자 형식](/01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 을 봅니다.

### SID 가 여럿 들어가는 까닭

- 역공학 논문은 CREDHIST 에 사용자 SID, 컴퓨터 SID, 계정 SID 가 들어간다고 적고, 도메인 컨트롤러의 전역 CREDHIST 를 위한 것으로 설명합니다.
- 위 구조 표에는 SID 칸이 한 항목에 하나뿐입니다. 실제 파일에서 SID 가 어떻게 나뉘는지는 이 글의 참고 문헌으로 확인하지 못했습니다.

### 암호화 알고리즘

CREDHIST 항목을 감싸는 알고리즘은 데이터 블롭과 비슷합니다. 버전마다 다릅니다.

| Windows | 암호 | 해시 | 반복수 |
|---|---|---|---|
| XP | 3DES | SHA-1 | 4000 |
| Vista | 3DES | SHA-1 | 24000 |
| 7 | AES256 | SHA-512 | 5600 |

- Windows 8·10·11 의 값은 이 글의 참고 문헌으로 확인하지 못했습니다.

## 읽는 법 — 사슬을 거슬러 올라가기

1. 지금 암호에서 만든 열쇠로 사슬의 첫 항목을 풉니다.
2. 첫 항목에서 바로 앞 암호의 SHA-1 을 얻습니다.
3. 그 SHA-1 로 다음 항목을 풉니다.
4. 필요한 옛 암호의 SHA-1 이 나올 때까지 사슬을 따라갑니다.
5. 얻은 SHA-1 로 그 암호에 감싸인 [마스터키](/01-foundations/protection/data-protection-api/master-key-protect-sid.md) 를 풉니다.

- bPasswordID 로 어느 항목이 어느 마스터키에 맞는지 짝을 찾습니다.

## 포렌식에서 중요한 점

CREDHIST 는 옛 암호 해시가 한자리에 모여 있어 크래킹 관점에서 눈여겨봅니다.

- 이전 암호들의 SHA-1 해시가 salt 없이 한꺼번에 들어 있습니다.
- salt 가 없어 병렬 크래킹과 레인보우 테이블을 쓸 수 있습니다.
- 다만 암호를 먼저 UTF-16LE 로 바꾼 뒤 해시합니다.
- 그래서 표준 SHA-1 크래커를 그대로 쓰면 맞지 않습니다.
- UTF-16LE 인코딩은 [문자 인코딩](/01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 을 봅니다.

증거로서 정리하면 이렇습니다.

- **말해 주는 것**: 이 사용자가 암호를 적어도 몇 번 바꿨는지. 사슬의 길이로 짐작합니다. 관리자가 암호를 재설정한 경우에도 항목이 생기는지는 이 글의 참고 문헌으로 확인하지 못했습니다.
- **말해 주는 것**: 옛 마스터키를 풀 실마리(옛 암호 해시).
- **말해 주지 못하는 것**: 암호의 원래 글자. 해시에서 바로 나오지 않습니다.
- **말해 주지 못하는 것**: 암호를 바꾼 정확한 시각. 항목에는 신뢰할 시각 칸이 없습니다.

## 함정

- **SHA-1 해시를 표준 크래커에 그대로 넣습니다.** Windows 는 UTF-16LE 로 인코딩한 뒤 해시합니다.
- **CREDHIST 를 빼고 마스터키만 모읍니다.** 옛 암호로 감싼 마스터키는 CREDHIST 없이 풀리지 않습니다.
- **사슬의 한 항목만 봅니다.** 필요한 옛 SHA-1 은 사슬을 여러 칸 거슬러야 나올 수 있습니다.

## 도구

아래 공개 도구는 예로만 듭니다.

| 도구 | CREDHIST 와 관련된 기능 |
|---|---|
| SharpDPAPI (공개 코드) | 지금 암호로 CREDHIST 를 풀어 옛 해시를 꺼냅니다 |
| 헥스 편집기 | 항목 헤더를 따라가며 사슬 구조를 직접 읽습니다 |

## 참고 문헌

- Microsoft (NAI Labs), *Windows Data Protection* (2001, Windows XP 기준) — https://learn.microsoft.com/en-us/previous-versions/ms995355(v=msdn.10)
- Elie Bursztein, Jean-Michel Picod, Ruben Sarfati, *Reversing DPAPI and Stealing Windows Secrets Offline*, USENIX WOOT 2010 — https://www.usenix.org/legacy/event/woot10/tech/full_papers/Burzstein.pdf
- Passcape Software, *Windows DPAPI* (마스터키·CREDHIST 구조) — https://www.passcape.com/index.php?section=docsys&cmd=details&id=28
