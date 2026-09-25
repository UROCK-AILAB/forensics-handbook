---
title: "패키지 파일 변조 확인"
parent: "아티팩트 · 패키지와 소프트웨어"
nav_order: 630
---

# 패키지 파일 변조 확인 (debsums·rpm -V)

패키지 관리자는 설치할 때 파일마다 해시와 속성을 데이터베이스에 적어 두므로, 지금 디스크에 있는 파일과 비교하면 설치 뒤에 내용이 바뀐 시스템 파일을 골라낼 수 있습니다. Debian·Ubuntu 는 `dpkg -V` 와 `debsums`, RHEL 은 `rpm -V` 로 비교합니다.

## 무엇을 기록하나 · 왜 생기나

이 쪽이 다루는 것은 따로 남는 로그가 아니라, 패키지 데이터베이스에 적힌 기준값과 실제 파일을 맞춰 본 결과입니다. dpkg 는 패키지를 풀 때 패키지 안의 메타데이터를 파일 데이터베이스에 모아 두고, `dpkg -V` (`--verify`) 는 이 값과 설치된 파일을 비교합니다[1]. 기준값은 패키지마다 `/var/lib/dpkg/info/패키지.md5sums` (다중 아키텍처 패키지는 `패키지:아키텍처` 이름)에 있습니다[4][11]. rpm 은 패키지 메타데이터를 rpm 데이터베이스에 저장하고, `rpm -V` 는 그 안의 크기·다이제스트·권한·파일 형식·소유자·그룹 등을 디스크의 파일과 비교합니다[5][6].

조사에서 이 비교가 쓸모 있는 까닭은, 침입자가 `sshd`, `ls`, 공유 라이브러리, PAM 모듈처럼 패키지가 설치한 파일을 바꿔치기하는 경우가 있기 때문입니다. 바뀐 파일이 어디에 흔적을 남기는지는 [공유 라이브러리 가로채기](../persistence/ld-preload.md)·[PAM 모듈 변조](../persistence/pam-backdoor.md) 쪽에서 다룹니다.

## 위치와 버전별 차이

| 항목 | Ubuntu 24.04 (dpkg) | RHEL 9 (rpm 4.16) |
|---|---|---|
| 검사 명령 | `dpkg -V`, `debsums` | `rpm -V` (`rpm -Va` 는 전체) |
| 기준값이 있는 곳 | `/var/lib/dpkg/info/*.md5sums`[4][11] | `/var/lib/rpm` 의 rpm 데이터베이스[6] |
| 비교하는 것 | 내용 MD5, 일반 파일인지 여부[1][2] | 크기·모드·다이제스트·장치 번호·링크 대상·소유자·그룹·mtime·capabilities[6] |
| 설정 파일 | `dpkg -V` 는 함께 보고 `c` 로 표시, `debsums` 는 기본으로 뺌[1][4] | 함께 보고 `c` 로 표시[6][7] |
| 바뀐 파일이 있을 때 종료 코드 | `dpkg -V` 는 0, `debsums` 는 2[2][4] | 0 이 아닌 값[5][7] |

`dpkg -V` 는 dpkg 1.17.2 부터 있고, 두 번째 자리의 `M` 검사는 dpkg 1.21.0 부터 들어갔습니다[1]. 검체에 `debsums` 가 없으면 분석 PC 의 것을 씁니다. rpm 데이터베이스 파일 이름(`rpmdb.sqlite` 또는 `Packages`)과 WAL 파일을 함께 떠야 하는 이유는 [rpm·dnf·yum 기록](rpm-dnf.md) 쪽을 봅니다.

## 구조

### `.md5sums` 한 줄

`.md5sums` 는 한 줄에 파일 하나이고, 대소문자를 가리지 않는 16진수 32자리 MD5, 공백 두 칸, 경로 순서입니다[3]. 경로 앞에는 `/` 가 붙지 않습니다(예: `usr/bin/dpkg`)[3][11]. 패키지에 이 파일이 없으면 dpkg 1.16.3 부터는 풀 때 dpkg 가 직접 만들어 넣습니다[3].

### `dpkg -V` 출력

`dpkg -V` 는 검사에 실패한 경로만 한 줄씩 찍고, 출력 형식은 `rpm` 한 가지뿐입니다[1]. 줄 모양은 9글자 결과, 공백, 속성 한 글자, 공백, 경로 순서입니다[1][2].

```
??5??????   /usr/sbin/example-daemon
??5?????? c /etc/example.conf
missing     /usr/lib/example/libexample.so.1
```

위 줄은 형식 명세로 만든 예시입니다.

| 자리 | 글자 | 뜻 |
|---|---|---|
| 1, 4~9 | 늘 `?` | 지원하지 않는 검사[1] |
| 2 | `M` | 기준값에 MD5 가 있는데 디스크의 경로가 일반 파일이 아님[1][2] |
| 3 | `5` | MD5 가 다름, 곧 내용이 바뀜[1] |
| 속성 | `c` | 설정 파일 (conffile)[1][2] |

`.` 은 통과, `?` 는 검사하지 못했다는 뜻입니다[1]. 2번째 자리는 실패할 때만 `M` 이고 통과로 찍히는 일이 없어서, 정상 파일도 `?` 로 나옵니다[1]. 파일을 열 수 없으면 3번째 자리가 `?` 인 채로 줄이 찍힙니다[2]. 파일이 없거나 속성을 읽을 수 없으면 앞 9글자 대신 `missing` 이 오고[1][2], 원인이 "파일 없음" 이 아니면 끝에 괄호로 오류 문구가 붙습니다[2].

### `debsums` 출력

`debsums` 는 파일마다 `OK`, `FAILED`(MD5 불일치), `REPLACED`(다른 패키지의 파일로 바뀜) 중 하나를 붙입니다[4]. `-c` 는 바뀐 파일 목록만 내고, `-a` 는 설정 파일까지, `-e` 는 설정 파일만 봅니다[4]. `-l` 은 `.md5sums` 가 없는 패키지를 나열합니다[4]. 종료 코드는 0 이 성공, 1 이 지정한 패키지가 없거나 버전이 맞지 않음, 2 가 바뀌었거나 없는 파일, 3 이 1과 2가 함께, 255 가 잘못된 옵션입니다[4].

### `rpm -V` 출력

`rpm -V` 는 기본으로 차이가 있는 파일만 찍고, `--verbose` 를 붙이면 모든 파일을 찍습니다[5]. 줄 모양은 9글자 결과, 공백 두 칸, 속성 한 글자, 공백, 경로 순서이고, 파일이 없으면 `missing` 뒤에 속성과 경로가 옵니다[7].

```
S.5....T.    /usr/bin/example
..5....T.  c /etc/example/example.conf
.M.......    /usr/lib64/example/plugin.so
missing     /usr/libexec/example-helper
```

위 줄은 형식 명세로 만든 예시입니다.

| 자리 | 글자 | 뜻 |
|---|---|---|
| 1 | `S` | 크기 |
| 2 | `M` | 모드(권한과 파일 형식) |
| 3 | `5` | 다이제스트(예전 이름 MD5) |
| 4 | `D` | 장치 번호 |
| 5 | `L` | 심볼릭 링크 대상 |
| 6 | `U` | 소유자 |
| 7 | `G` | 그룹 |
| 8 | `T` | mtime |
| 9 | `P` | capabilities |

`.` 은 통과, `?` 는 권한 부족 등으로 검사하지 못했다는 뜻입니다[5][6]. 속성 글자는 `%doc`·`%config`·spec·`%missingok`·`%config(noreplace)`·`%ghost`·`%license`·`%readme`·`%artifact` 순서로 따져 처음 해당하는 하나만 찍습니다(`d`, `c`, `s`, `m`, `n`, `g`, `l`, `r`, `a`)[7]. 그래서 `%config(noreplace)` 파일은 `n` 이 아니라 `c` 로 나옵니다[7]. rpm 4.16 의 man 페이지는 `c`·`d`·`g`·`l`·`r` 만 설명하고, 최신 man 페이지는 `a`·`m`·`n`·`s` 까지 설명합니다[5][6]. 다른 패키지가 이 파일을 대신 설치해 상태가 "replaced" 이면 파일이 있는지만 보고 줄 끝에 `(replaced)` 를 붙입니다[7]. 권한·파일 형식 같은 속성이 실제로 무엇이 됐는지는 [권한·확장 속성·ACL·Capabilities](../../01-foundations/filesystem/permissions-xattr.md) 쪽에서 확인합니다.

## 증거로서 의미

### 증명하는 것

- 결과 줄에 나온 경로는 검사한 시점에 패키지가 설치할 때 적어 둔 기준값과 달랐습니다. `5` 는 내용이, rpm 의 `M`·`U`·`G`·`P` 는 모드·소유자·그룹·capabilities 가 달라졌다는 뜻입니다[1][6].
- `missing` 은 패키지가 설치한 파일이 지금 그 경로에 없다는 뜻입니다[1][7].
- 속성 `c` 로 설정 파일을 가려내면, 관리자가 고치는 것이 보통인 설정 파일과 바뀔 일이 드문 실행 파일·라이브러리를 나눠 볼 수 있습니다[1][6].

### 증명하지 못하는 것

- 누가, 언제, 어떤 방법으로 바꿨는지는 알려 주지 않습니다.
- 바뀐 것이 악성이라는 뜻도 아닙니다. 관리자의 수정, 다른 패키지의 덮어쓰기, 매체 오류도 같은 결과를 냅니다[4].
- 기준값이 같은 시스템 안에 있어서 root 권한을 얻은 사람은 파일과 기준값을 함께 고칠 수 있습니다. `dpkg -V` 는 무결성 검사일 뿐 보안 검증이 아니고, `.md5sums` 도 보안 목적으로 만든 파일이 아닙니다[1][3]. `debsums` 도 보안 도구로서는 쓰임이 좁아서, 보안 목적이라면 안전한 매체에서 돌리는 aide 같은 무결성 검사 도구를 씁니다[4].
- `dpkg -V` 는 내용 MD5 만 보므로 권한·소유자만 바꾼 파일은 걸리지 않습니다[1].
- 어느 패키지에도 속하지 않은 파일(새로 떨군 실행 파일, 추가된 라이브러리 등)은 검사 대상이 아닙니다. 이런 파일은 `dpkg -S` 나 `rpm -q -f` 로 소속 패키지가 없는지 따로 확인합니다[14][15].

## 시각 해석

검사 결과에는 시각이 없고, 결과는 검사를 돌린 순간의 상태입니다. `dpkg -V` 와 `debsums` 는 시각을 비교하지 않습니다[2][4].

`rpm -V` 의 `T` 는 헤더의 `Filemtimes` 값과 디스크 파일의 mtime 이 다르다는 표시일 뿐, 언제 바뀌었는지는 알려 주지 않습니다[7][8]. `Filemtimes` 는 Unix 시각(UTC 기준 초)이라 `--queryformat` 으로 뽑아 보면 패키지가 만든 파일의 원래 mtime 을 알 수 있습니다[8][10]. 여러 패키지가 함께 소유한 파일은 mtime 차이를 결과에서 뺍니다[7]. 바뀐 파일의 실제 시각은 파일 시스템에서 읽어야 하므로 [ext4](../../01-foundations/filesystem/ext4/index.md) 쪽과 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 쪽을 봅니다. 패키지가 언제 설치·업그레이드됐는지는 [dpkg·apt 기록](dpkg-apt.md)·[rpm·dnf·yum 기록](rpm-dnf.md) 에서 확인하고, 바뀐 파일의 시각이 그 뒤인지 따져 봅니다.

## 함정과 한계

- 라이브 시스템에서 돌리면 `dpkg`, `rpm`, `md5sum` 과 이들이 쓰는 라이브러리부터 바뀌었을 수 있습니다. 이미지를 분석 PC 에 마운트해 분석 PC 의 도구로 검사하거나, 해시를 따로 계산해 대조합니다.
- `dpkg -V` 는 바뀐 파일이 있어도 종료 코드 0 을 돌려주고, 이름을 댄 패키지가 설치돼 있지 않을 때만 1 을 돌려줍니다[2]. 스크립트에서 종료 코드만 보면 결과를 놓칩니다.
- `debsums` 는 기본으로 설정 파일을 빼므로 `-a` 를 붙이거나 `-ce` 로 설정 파일만 따로 봅니다[4].
- prelink·localepurge 가 설정돼 있으면 `debsums` 는 바뀐 ELF 파일과 지워진 로캘 파일을 기본으로 알리지 않습니다. `--no-prelink`, `--no-locale-purge` 를 붙이면 알립니다[4].
- `debsums -g ...,keep` 과 `debsums_init` 은 `/var/lib/dpkg/info/패키지.md5sums` 를 새로 씁니다[4]. 검체에서 돌리면 기준값 자체가 바뀝니다.
- `debsums` 는 다른 패키지가 덮어쓴 파일을 바뀐 것으로 잘못 알릴 수 있습니다[4].
- `rpm -V` 는 `%ghost` 파일의 내용·크기·mtime·링크 대상을 보지 않고, `%ghost`·`%missingok` 파일이 없는 것은 `--verbose` 가 아니면 알리지 않습니다[7]. 일반 파일이 아닌 경로는 다이제스트·크기·mtime·capabilities 를 보지 않습니다[7].
- rpm 의 소유자·그룹 비교는 로컬 `passwd`·`group` 만 봅니다[5].
- 다이제스트 알고리즘은 헤더의 `Filedigestalgo` 가 정하고, 이 값이 없으면 MD5 로 봅니다[8].
- `rpm --root` 로 이미지를 검사하면 스크립틀릿이 그 디렉터리로 chroot 한 뒤 실행되고, 검사 모드는 `%verifyscript` 를 돌립니다[6]. 검체 안의 스크립트가 분석 PC 에서 돌지 않게 `--noscripts` 를 붙입니다[6].
- `rpmdb --verifydb` 는 데이터베이스 파일 자체의 낮은 수준 검사이고, 설치된 파일을 보는 것은 `rpm --verify -a` 입니다[9].
- 결과가 깨끗해도 기준값까지 함께 고쳤을 가능성은 남습니다. 같은 이름·버전·아키텍처의 원본 `.deb`·`.rpm` 을 배포처에서 받아 그 안의 해시와 대조해야 이 가능성을 지울 수 있습니다.

## 직접 분석해 보기

### 손으로 한 번: 기준값과 해시를 직접 대조

검체를 `/mnt/evidence` 에 읽기 전용으로 마운트했다고 두고, `.md5sums` 의 한 줄과 실제 파일의 MD5 를 나란히 놓습니다.

```
$ grep 'usr/sbin/example-daemon$' /mnt/evidence/var/lib/dpkg/info/example.md5sums
3f2a9c0e5b1d47a8c6e0f9b2d4a1c7e3  usr/sbin/example-daemon
$ md5sum /mnt/evidence/usr/sbin/example-daemon
a81c4e7f02b9d3c65e1f8a0b7d2c9e46  /mnt/evidence/usr/sbin/example-daemon
```

위 출력은 만든 예시입니다. 두 값이 다르면 `dpkg -V` 가 이 경로에 `??5??????` 를 찍을 상황입니다[1][3]. 경로 앞에 `/` 가 없다는 점에 맞춰 검색합니다[3].

RHEL 은 헤더의 다이제스트와 mtime 을 뽑아 같은 방식으로 대조합니다. 대괄호 안에 배열 태그를 여럿 넣으면 같은 순번의 값끼리 한 줄로 나옵니다[10].

```
$ rpm --root /mnt/evidence -q --qf '[%{FILEDIGESTS} %{FILEMTIMES} %{FILENAMES}\n]' example
5e0b7c2a91d4f836b2a7e1c09f5d3b684c2e7a19d0f6b3852a9e4c7d1b0f2a63 1700000000 /usr/bin/example
```

위 출력은 만든 예시입니다. 헤더의 `Filedigestalgo` 가 정한 알고리즘(값이 없으면 MD5)으로 디스크 파일의 해시를 계산해 첫 칸과 비교하고, 두 번째 칸의 Unix 시각을 디스크 파일의 mtime 과 견줍니다[8].

### 공개 도구로 한 번

- 이미지를 마운트한 분석 PC 에서 `dpkg --root=/mnt/evidence -V` 를 돌리면 설치 폴더가 `/mnt/evidence`, 관리 폴더가 `/mnt/evidence/var/lib/dpkg` 가 됩니다(dpkg 1.21.10 부터, `DPKG_ROOT` 가 없을 때)[1].
- `debsums -ca` 는 설정 파일을 포함해 바뀐 파일만 나열하고, `-r` 로 루트, `-d` 로 관리 폴더를 지정합니다[4]. `--generate=all` 은 디스크의 `.md5sums` 를 무시하고 `.deb` 안의 값(없으면 `.deb` 에서 만든 값)으로 검사하고, `-p` 로 `.deb` 를 찾을 폴더를 줍니다[4]. `keep` 을 붙이지 않으면 기준값 파일을 덮어쓰지 않습니다[4].
- RHEL 은 `rpm --root /mnt/evidence -Va --noscripts` 로 전체를 검사합니다[6].
- dissect.target 의 `dpkg.packages --output-files` 는 `.md5sums` 의 값과 실제 파일의 MD5 를 비교해 파일마다 `digest_match` 를 냅니다[11].
- UAC 는 라이브 수집에서 `dpkg -V`, `rpm -V -a` 결과를 `dpkg_-V.txt`, `rpm_-V_-a.txt` 로 남기고, `/bin`·`/usr/bin`·`/usr/local/bin` 등의 파일마다 `dpkg -S`·`rpm -q -f` 로 소속 패키지를 찾아 둡니다[12][13][14]. 라이브 수집 전반은 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md) 쪽을 봅니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [dpkg·apt 기록](dpkg-apt.md)·[rpm·dnf·yum 기록](rpm-dnf.md) | 바뀐 파일의 패키지가 최근 업그레이드·재설치됐는가, 기준값이 바뀐 시점과 맞는가 |
| [공유 라이브러리 가로채기](../persistence/ld-preload.md)·[PAM 모듈 변조](../persistence/pam-backdoor.md) | 바뀐 라이브러리·PAM 모듈이 실제로 불려 쓰였는가 |
| [알려진 파일 대조와 YARA](../../03-techniques/analysis/hash-yara.md) | 바뀐 파일의 해시가 알려진 악성·정상 파일과 맞는가 |
| [루트킷 찾기](../../03-techniques/analysis/rootkit-detection.md) | 바뀐 시스템 명령이 결과를 숨기는 모양인가 |
| [셸 명령 기록](../execution/shell-history/index.md) | 파일을 덮어쓰거나 `chmod`·`chown` 한 명령이 있는가 |
| [타임라인 만들기](../../03-techniques/analysis/timeline.md) | 바뀐 파일의 시각 앞뒤로 무엇이 있었는가 |

지속성 전반의 순서는 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md) 쪽에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 검체 모음에서 Ubuntu 나 RHEL 계열 서버 이미지를 골라 풀어 봅니다.

1. 이미지를 마운트해 `dpkg --root` 나 `rpm --root ... --noscripts` 로 검사했을 때, 속성 `c` 가 없는 결과 줄은 몇 개이고 어느 폴더에 몰려 있는가?
2. 결과 줄에 나온 실행 파일의 파일 시스템 mtime·ctime 은 그 패키지의 마지막 설치·업그레이드 기록보다 뒤인가?
3. `debsums -l` 로 `.md5sums` 가 없는 패키지가 있는가, 있다면 그 패키지가 설치된 시각은 언제인가?
4. `/usr/local/bin` 이나 `/usr/lib` 아래에 어느 패키지에도 속하지 않는 파일이 있는가?
5. 결과 줄에 나온 파일 하나를 골라, 같은 버전의 원본 패키지를 배포처에서 받아 그 안의 해시와 대조했을 때도 다른가?

## 참고 문헌

1. dpkg, man/dpkg.pod (dpkg(1)). https://github.com/guillemj/dpkg/blob/main/man/dpkg.pod
2. dpkg, src/main/verify.c. https://github.com/guillemj/dpkg/blob/main/src/main/verify.c
3. dpkg, man/deb-md5sums.pod (deb-md5sums(5)). https://github.com/guillemj/dpkg/blob/main/man/deb-md5sums.pod
4. debsums(1) man 페이지(사본). https://github.com/rajpratik71/linux-manPages/blob/master/docs/debsums.md
5. RPM, docs/man/rpm.8.scd. https://github.com/rpm-software-management/rpm/blob/master/docs/man/rpm.8.scd
6. RPM 4.16, doc/rpm.8. https://github.com/rpm-software-management/rpm/blob/rpm-4.16.x/doc/rpm.8
7. RPM 4.16, lib/verify.c. https://github.com/rpm-software-management/rpm/blob/rpm-4.16.x/lib/verify.c
8. RPM, docs/manual/tags.md. https://github.com/rpm-software-management/rpm/blob/master/docs/manual/tags.md
9. RPM, docs/man/rpmdb.8.scd. https://github.com/rpm-software-management/rpm/blob/master/docs/man/rpmdb.8.scd
10. RPM, docs/man/rpm-queryformat.7.scd. https://github.com/rpm-software-management/rpm/blob/master/docs/man/rpm-queryformat.7.scd
11. fox-it dissect.target, dissect/target/plugins/os/unix/linux/debian/dpkg.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/debian/dpkg.py
12. UAC, artifacts/live_response/packages/dpkg.yaml. https://github.com/tclahr/uac/blob/main/artifacts/live_response/packages/dpkg.yaml
13. UAC, artifacts/live_response/packages/rpm.yaml. https://github.com/tclahr/uac/blob/main/artifacts/live_response/packages/rpm.yaml
14. UAC, artifacts/live_response/packages/package_owns_file.yaml. https://github.com/tclahr/uac/blob/main/artifacts/live_response/packages/package_owns_file.yaml
15. dpkg, man/dpkg-query.pod (dpkg-query(1)). https://github.com/guillemj/dpkg/blob/main/man/dpkg-query.pod
