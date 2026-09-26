---
title: "rpm·dnf·yum 기록"
parent: "아티팩트 · 패키지와 소프트웨어"
nav_order: 600
---

# rpm·dnf·yum 기록 (RHEL·Fedora)

RHEL·Fedora 계열에서는 rpm 데이터베이스가 지금 설치된 패키지와 설치 시각을, dnf(RHEL 7 은 yum)의 로그와 트랜잭션 기록 DB 가 언제 누가 어떤 명령으로 무엇을 넣고 뺐는지를 담습니다.

## 무엇을 기록하나 · 왜 생기나

rpm 은 패키지를 설치할 때 패키지 헤더를 자기 데이터베이스에 넣고, 이때 설치 시각 `Installtime` 같은 값을 헤더에 덧붙입니다[1]. 이 데이터베이스는 "지금 설치된 패키지" 목록이라서, 지운 패키지는 여기서 빠집니다.

dnf 는 rpm 위에서 저장소를 찾고 의존성을 풀어 트랜잭션을 돌리는 관리자입니다. dnf 는 한 번 실행할 때마다 트랜잭션 기록 DB 에 시작·끝 시각, 명령줄, 로그인 사용자 UID, 패키지별 동작과 이유를 남기고[13][15], 이와 따로 텍스트 로그 몇 개를 씁니다[11]. RHEL 7 의 yum 도 비슷한 구조로 `yum.log` 와 날짜별 history DB 를 남깁니다[17][18].

rpm 자체도 syslog 플러그인이나 audit 플러그인이 설치되어 있으면 트랜잭션마다 시스템 로그나 감사 로그에 줄을 남깁니다[7][8]. 그래서 한 번의 설치가 rpm DB·dnf 기록·시스템 로그 세 곳에 따로 흔적을 남길 수 있고, 한 곳을 지워도 다른 곳과 대조할 수 있습니다.

## 위치와 버전별 차이

| 항목 | RHEL 9 (rpm 4.16, dnf 4) | RHEL 7 (yum) | dnf5 를 쓰는 시스템 |
|---|---|---|---|
| rpm 데이터베이스 | `/var/lib/rpm/rpmdb.sqlite` 와 `-wal`, `-shm`[4] | `/var/lib/rpm/Packages` 와 색인 파일들(Berkeley DB)[2][4] | rpm 판에 따라 위 둘 가운데 하나. 실제 시스템에서 확인 |
| 텍스트 로그 | `/var/log/dnf.log`, `dnf.rpm.log`, `dnf.librepo.log`, `hawkey.log`[11][14] | `/var/log/yum.log`[17] | `/var/log/dnf5.log`(root 로 실행할 때)[16] |
| 트랜잭션 기록 DB | `/var/lib/dnf/history.sqlite`[11][15] | `/var/lib/yum/history/history-YYYY-MM-DD.sqlite`[18] | `/usr/lib/sysimage/libdnf5/transaction_history.sqlite`[16] |
| 패키지별 부가 정보 | 트랜잭션 기록 DB 안 | `/var/lib/yum/yumdb/`[18] | 트랜잭션 기록 DB 안 |
| 저장소 설정 | `/etc/yum.repos.d/*.repo`[14] | `/etc/yum.conf`, `/etc/yum.repos.d/*.repo`[22] | `/etc/yum.repos.d/*.repo`[16] |
| 플러그인 | `/etc/dnf/pluginconf.d/`, `/usr/lib` 아래 `dnf-plugins` 폴더[20] | `/etc/yum/pluginconf.d/`, `/usr/lib/yum-plugins/`[20] | `/etc/dnf/libdnf5-plugins/`(플러그인 설정)[16] |
| 받은 패키지 캐시 | `/var/cache/dnf`, 기본값 `keepcache=false`[11][14] | 실제 시스템에서 확인 | 실제 시스템에서 확인 |

rpm 데이터베이스 폴더의 기본값은 `%_dbpath` 매크로의 `/var/lib/rpm` 입니다[2][3]. rpm 4.16 은 설정한 백엔드 파일이 없으면 sqlite, ndb, Berkeley DB 순서로 폴더 안에 있는 파일을 찾아 씁니다[4]. 그래서 백엔드는 설정을 보지 않고 폴더 안에 `rpmdb.sqlite` 가 있는지, `Packages` 가 있는지로 판별하면 됩니다. ndb 백엔드라면 파일 이름이 `Packages.db` 입니다[4].

dnf5 는 root 가 아닌 사용자로 실행하면 로그를 사용자별 XDG 상태 폴더에 씁니다[16]. 플러그인 폴더와 저장소 설정은 영구 실행 수단으로 쓰일 수 있어서 UAC 도 따로 모읍니다[20]. 이 페이지는 기록만 다루고, 설정 파일로 남는 지속성은 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md) 에서 다룹니다.

## 구조

### rpm 데이터베이스 (rpmdb.sqlite)

rpm 4.16 의 sqlite 백엔드는 주 표 하나와 색인 표 여럿을 씁니다[4].

| 표 | 열 | 내용 |
|---|---|---|
| `Packages` | `hnum INTEGER PRIMARY KEY AUTOINCREMENT`, `blob BLOB NOT NULL` | 패키지 하나당 한 줄. `blob` 이 rpm 헤더 전체 |
| 색인 표(`Name`, `Basenames` 등 태그 이름) | `key`, `hnum`, `idx` | 태그 값으로 `Packages` 의 `hnum` 을 찾는 색인 |

설치 시각과 이름·판은 모두 `blob` 안 rpm 헤더의 태그로 들어 있습니다. 포렌식에서 자주 쓰는 태그는 아래와 같습니다[1].

| 태그 | 번호 | 형 | 뜻 |
|---|---|---|---|
| `Installtime` | 1008 | int32 | 설치한 시각(Unix 초). 설치할 때 헤더에 덧붙는 값 |
| `Installtid` | 1128 | int32 | 설치한 트랜잭션의 ID |
| `Buildtime` | 1006 | int32 | 패키지를 빌드한 시각 |
| `Buildhost` | 1007 | string | 빌드한 호스트 이름 |
| `Vendor`, `Packager` | 1011, 1015 | string | 배포 주체·패키저 연락처 |
| `Sourcerpm` | 1044 | string | 원본 소스 rpm 파일 이름 |
| `Filedigests`, `Filedigestalgo` | 1035, 5011 | string array, int32 | 파일별 해시와 해시 알고리즘. 알고리즘 값이 없으면 md5 |
| `Filemtimes` | 1034 | int32 array | 파일별 수정 시각 |

파일별 해시·크기·권한으로 설치한 뒤 바뀐 파일을 가려내는 방법은 [패키지 파일 변조 확인](package-verify.md) 에서 다룹니다.

rpm 은 쓰기로 열 때 `PRAGMA journal_mode = WAL` 을 걸고 `-wal` 파일이 닫힌 뒤에도 남도록 설정하며, `%_flush_io` 가 꺼져 있으면 자동 체크포인트를 끕니다(`wal_autocheckpoint = 0`)[4]. 정상으로 닫을 때는 `wal_checkpoint = TRUNCATE` 로 WAL 내용을 본 파일에 옮기고 WAL 을 비웁니다[4]. 그래서 rpm 이 도는 중에 수집했거나 비정상으로 끝났다면 최근 변경이 `rpmdb.sqlite-wal` 에만 있을 수 있습니다. 또 `PRAGMA secure_delete = OFF` 로 열기 때문에[4], 지운 패키지의 헤더가 빈 페이지에 남아 있을 가능성이 있습니다. WAL 과 빈 페이지를 읽는 법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html)에 있습니다.

### dnf 텍스트 로그 (RHEL 9)

`dnf.log`, `dnf.librepo.log`, `dnf.rpm.log` 는 같은 서식을 씁니다. 줄 모양은 `%(asctime)s %(levelname)s %(message)s` 이고, 시각은 `%Y-%m-%dT%H:%M:%S%z` 형식의 현지 시각에 UTC 와의 차이가 붙습니다[11]. `dnf.log` 와 `dnf.rpm.log` 에는 dnf 가 로깅을 시작할 때마다 `--- logging initialized ---` 줄이 `INFO` 수준으로 먼저 남습니다[11].

`dnf.rpm.log` 에는 패키지 동작이 `동작: 패키지` 모양으로 한 줄씩 남습니다[12]. 동작 문자열은 `Installed`, `Upgrade`, `Upgraded`, `Downgrade`, `Downgraded`, `Reinstall`, `Reinstalled`, `Obsolete`, `Obsoleted`, `Erase`, `Cleanup`, `Verified`, `Running scriptlet`, `Preparing` 이고 번역하지 않은 영어 그대로입니다[12]. 이 줄의 로그 수준은 `SUBDEBUG` 이고, 스크립틀릿(scriptlet)이 낸 출력도 같은 파일에 `INFO` 로 남습니다[12]. 아래는 만든 예시입니다.

```
2024-05-24T13:06:10+0900 INFO --- logging initialized ---
2024-05-24T13:06:12+0900 SUBDEBUG Installed: zip-3.0-35.el9.x86_64
2024-05-24T13:06:12+0900 SUBDEBUG Erase: unzip-6.0-56.el9.x86_64
```

세 로그는 파일 크기로 순환합니다. 기본값은 `log_size` 1 MiB, `log_rotate` 4, `log_compress` false 이고[14], `dnf.log.1` 부터 `.4` 까지 남습니다[11]. logrotate 설정은 `hawkey.log` 하나만 매주 4세대로 돌립니다[11].

### dnf 트랜잭션 기록 DB (history.sqlite)

libdnf 가 만드는 SQLite DB 이고, 스키마 판은 `config` 표의 `version` 키에 들어 있습니다(1.1, 1.2, 1.3)[15]. 1.2 에서 `trans.comment`, 1.3 에서 `trans.persistence` 열이 붙었습니다[15].

| 표 | 주요 열 | 내용 |
|---|---|---|
| `trans` | `id`, `dt_begin`, `dt_end`, `rpmdb_version_begin`, `rpmdb_version_end`, `releasever`, `user_id`, `cmdline`, `state` | 트랜잭션 한 번에 한 줄 |
| `trans_item` | `trans_id`, `item_id`, `repo_id`, `action`, `reason`, `state` | 트랜잭션 안 패키지 하나에 한 줄 |
| `rpm` | `item_id`, `name`, `epoch`, `version`, `release`, `arch` | 패키지 이름과 판. 빈 epoch 는 0 |
| `repo` | `id`, `repoid` | 저장소 ID |
| `console_output` | `trans_id`, `file_descriptor`(1 stdout, 2 stderr), `line` | 스크립틀릿 출력 |
| `item`, `trans_with`, `item_replaced_by`, `comps_group`, `comps_environment` 등 | | 항목 종류, 트랜잭션을 돌린 dnf·rpm 판, 교체 관계, 그룹 |

숫자로 들어가는 값의 뜻은 다음과 같습니다[15].

| 열 | 값 |
|---|---|
| `trans_item.action` | 1 INSTALL, 2 DOWNGRADE, 3 DOWNGRADED, 4 OBSOLETE, 5 OBSOLETED, 6 UPGRADE, 7 UPGRADED, 8 REMOVE, 9 REINSTALL, 10 REINSTALLED, 11 REASON_CHANGE |
| `trans_item.reason` | 0 UNKNOWN, 1 DEPENDENCY, 2 USER, 3 CLEAN, 4 WEAK_DEPENDENCY, 5 GROUP |
| `trans.state`, `trans_item.state` | 0 UNKNOWN, 1 DONE, 2 ERROR |
| `item.item_type` | 1 RPM, 2 GROUP, 3 ENVIRONMENT |

`dt_begin` 은 트랜잭션을 시작할 때 `calendar.timegm(time.gmtime())` 로, `dt_end` 는 끝날 때 `time.time()` 으로 넣는 UTC 기준 Unix 초입니다[13]. `user_id` 는 `/proc/self/loginuid` 값이고, 이 파일을 읽지 못할 때만 실행 중인 프로세스의 UID 로 대신합니다[13]. 로그인 UID(loginuid)는 사용자가 처음 로그인한 ID 라서[10], sudo 로 dnf 를 돌려도 처음 로그인한 계정의 UID 가 남습니다. loginuid 가 설정되지 않은 프로세스라면 -1 을 부호 없는 수로 찍은 4294967295 로 보입니다[10]. `history_record` 설정이 기본값 true 일 때만 기록이 쌓입니다[14].

### yum 기록 (RHEL 7 기준)

`/var/log/yum.log` 는 `%(asctime)s %(message)s` 서식에 `%b %d %H:%M:%S` 시각을 씁니다[17]. 연도가 없는 현지 시각입니다. 동작은 `Installed`, `Updated`, `Erased`, `Obsoleted`, `Cleanup` 이고 `동작: 패키지` 모양이며, 이 목록에 없는 동작은 `패키지: 동작` 순서로 남습니다[17]. 만든 예시는 `May 24 13:06:12 Installed: zip-3.0-24.el7.x86_64` 입니다.

yum history DB 는 `/var/lib/yum/history/` 에 `history-` 뒤에 만든 날짜(`%Y-%m-%d`)를 붙인 이름으로 생기고, 권한은 0600 입니다[18]. 주요 표는 `trans_beg(tid, timestamp, rpmdb_version, loginuid)`, `trans_end(tid, timestamp, rpmdb_version, return_code)`, `trans_cmdline(tid, cmdline)`, `trans_data_pkgs(tid, pkgtupid, done, state)`, `pkgtups(pkgtupid, name, arch, epoch, version, release, checksum)`, `pkg_yumdb`, `trans_script_stdout` 입니다[18]. `timestamp` 는 `int(time.time())` 로 넣은 UTC 기준 Unix 초이고, `loginuid` 는 `yum.misc.getloginuid()` 로 구합니다[18].

yumdb 는 `/var/lib/yum/yumdb/이름첫글자/pkgid-이름-버전-릴리스-아키텍처/` 폴더에 속성마다 파일 하나를 두는 구조입니다[18]. 속성 이름은 `checksum_type`, `reason`, `installed_by`, `changed_by`, `from_repo`, `from_repo_revision`, `from_repo_timestamp`, `releasever`, `group_member`, `command_line` 등입니다[18].

### rpm 플러그인이 남기는 줄 (설치되어 있을 때)

rpm 4.16 의 syslog 플러그인은 식별자 `[RPM]`, facility `LOG_USER` 로 다음 줄을 씁니다[7].

```
Transaction ID 6650a1b2 started
install zip-3.0-35.el9.x86_64: success
erase unzip-6.0-56.el9.x86_64: success
Transaction ID 6650a1b2 finished: 0
```

위는 만든 예시이고, 실패가 있으면 `N elements failed, N scripts failed` 요약과 `scriptlet 이름 failure: 코드` 줄이 더 붙습니다[7]. 테스트 트랜잭션과 루트가 `/` 가 아닌 트랜잭션은 기록하지 않습니다[7]. 최신 rpm 은 식별자가 `rpm` 이고 동작도 `cleanup`, `downgrade`, `erase`, `install`, `replace`, `restore`, `upgrade` 일곱 가지에 `(from: …)` 표기가 붙을 수 있어서[7], rpm 판에 따라 검색어가 다릅니다.

audit 플러그인은 패키지마다 `SOFTWARE_UPDATE`(1138) 감사 이벤트를 남깁니다[8][9]. 메시지 본문은 `op=install sw="zip-3.0-35.el9.x86_64" sw_type=rpm key_enforce=0 gpg_res=1 root_dir="/"` 모양(만든 예시)이고, `op` 는 `install`, `update`, `remove` 가운데 하나, `gpg_res` 는 서명 검증에 성공했으면 1 입니다[8]. 감사 로그 줄 전체의 구조는 [감사 로그 형식](../../01-foundations/logging/auditd-format.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

- `trans` 와 `trans_item` 을 이으면 어느 시각(UTC)에 어떤 패키지를 설치·갱신·제거했는지, 그때 명령줄이 무엇이었는지를 보여 줍니다[15].
- `user_id` 는 그 dnf 를 실행한 로그인 세션의 loginuid 입니다[13]. sudo 를 거쳤어도 처음 로그인한 계정을 가리킵니다.
- `reason` 으로 사용자가 직접 고른 패키지(2 USER)와 의존성으로 딸려 온 패키지(1 DEPENDENCY)를 나눌 수 있고, `repo` 로 어느 저장소에서 왔는지 알 수 있습니다[15].
- `state` 가 2 ERROR 이면 실패한 트랜잭션입니다[15]. 실패한 설치 시도도 흔적으로 남습니다.
- rpm DB 의 `Installtime` 은 지금 설치된 패키지 각각이 언제 들어왔는지 보여 주고, dnf 를 거치지 않고 `rpm -i` 로 넣은 패키지도 여기에는 있습니다[1].

### 증명하지 못하는 것

- `rpm -i` 로 직접 설치한 패키지는 dnf 트랜잭션 기록에 없습니다. dnf 기록이 비었다고 설치가 없었다는 뜻은 아닙니다.
- 패키지 파일을 어디서 받았는지는 `cmdline` 에 로컬 경로나 주소가 적힌 경우에만 알 수 있습니다.
- loginuid 가 4294967295 이면 어느 사람이 실행했는지 이 값만으로는 알 수 없습니다. 자동 업데이트 서비스나 cron 에서 돈 트랜잭션일 가능성이 있습니다.
- rpm DB 는 지금 상태만 담아서, 지운 패키지는 여기서 빠집니다. 제거는 `trans_item.action` 8 REMOVE, `dnf.rpm.log` 의 `Erase:`, `yum.log` 의 `Erased:` 로 봅니다.
- 이 기록들은 root 가 고칠 수 있는 평문 로그와 SQLite 파일입니다. 조작이 없었다는 것은 여러 기록을 대조해야 말할 수 있습니다.

## 시각 해석

| 값 | 형식 | 기준 | 바뀌는 때 |
|---|---|---|---|
| rpm `Installtime` | Unix 초(int32)[1] | UTC | 그 패키지를 설치하거나 새 판으로 바꿀 때 |
| rpm `Buildtime` | Unix 초(int32)[1] | UTC | 패키지를 빌드할 때. 이 시스템과 관계없음 |
| dnf `trans.dt_begin`, `dt_end` | Unix 초[13][15] | UTC | 트랜잭션 시작·끝 |
| dnf 텍스트 로그 | `YYYY-MM-DDTHH:MM:SS+hhmm`[11] | 현지 시각과 UTC 차이 | 줄을 쓸 때 |
| `yum.log` | `Mon DD HH:MM:SS`[17] | 현지 시각, 연도 없음 | 줄을 쓸 때 |
| yum `trans_beg.timestamp`, `trans_end.timestamp` | Unix 초[18] | UTC | 트랜잭션 시작·끝 |
| rpm syslog 플러그인 | 시스템 로그 시각 | [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md), [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 참고 | 줄을 쓸 때 |

`rpm -q --queryformat` 의 `:date` 는 strftime `%c`, `:day` 는 `%a %b %d %Y` 로 바꿔 찍으므로[5] 분석하는 PC 의 시간대가 들어갑니다. 여러 기록을 시간순으로 합칠 때는 `%{INSTALLTIME}` 숫자 그대로 뽑아 UTC 로 바꾸는 편이 안전합니다. `yum.log` 처럼 현지 시각만 있는 기록은 [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md)에서 구한 시간대로 옮기고, 에포크 값을 읽는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

## 함정과 한계

- `rpmdb.sqlite` 만 복사하고 `-wal` 을 빼면 최근 변경이 빠질 수 있습니다[4]. 세 파일을 함께 떠서 읽습니다.
- 증거 사본에 `rpm --dbpath` 를 쓸 때는 쓰기 가능한 경로라면 rpm 이 WAL 설정을 걸고 닫을 때 체크포인트를 해 파일을 바꿉니다[4]. 원본이 아니라 작업용 사본에서 돌립니다.
- `dnf.log` 계열은 1 MiB 로 5세대까지만 남아서[11][14], 패키지 작업이 잦은 시스템은 몇 주 전 기록도 없을 수 있습니다. 오래된 기간은 `history.sqlite` 와 rpm DB 를 봅니다.
- 소스 주석에는 `dnf.rpm.log` 가 `/var/log/dnf/` 아래에 있다고 적혀 있지만, 실제 경로는 `logdir`(기본 `/var/log`)에 파일 이름을 붙인 `/var/log/dnf.rpm.log` 입니다[11][12][14].
- `user_id` 0 이 곧 root 로 로그인했다는 뜻은 아닙니다. loginuid 를 읽지 못해 실행 UID 로 대신한 경우일 수 있습니다[13].
- 일반 사용자가 `history.sqlite` 를 열지 못하면 dnf 는 메모리 DB 로 대신하고 오류만 남깁니다[15]. 이런 실행은 파일에 기록되지 않습니다.
- dissect.target 에는 RHEL 계열용으로 `yum.log` 파서만 있습니다[19]. 이 파서는 `Installed`·`Updated`·`Erased`·`Obsoleted` 가 없는 줄을 만나면 그 뒤 줄과 아직 읽지 않은 `yum.*` 파일을 모두 건너뛰고, 연도는 추정해서 채웁니다[19]. `Cleanup:` 줄 같은 다른 줄이 나오면 그 뒤 기록이 도구 결과에서 빠질 수 있으니 원본 파일을 함께 봅니다.
- plaso 에는 rpm·dnf·yum 전용 파서가 없습니다[23]. `history.sqlite` 는 sqlite3 로 직접 조회합니다.
- Velociraptor 의 `Linux.RHEL.Packages` 와 UAC 의 rpm·dnf 수집은 실행 중인 시스템에서 명령을 실행합니다[20][21]. 디스크 이미지에는 쓸 수 없어서 파일을 직접 읽어야 합니다. ForensicArtifacts 정의에도 rpm DB 와 dnf 로그는 없고 저장소 설정(`YumSources`)만 있습니다[22].
- `Installtime` 과 `Buildtime` 을 헷갈리지 않습니다. `Buildtime` 은 배포처에서 패키지를 만든 시각입니다[1].

## 직접 분석해 보기

### 파일로 한 번

먼저 rpm DB 백엔드를 구분합니다. 이미지를 마운트한 경로가 `/mnt/img` 라고 두면(만든 예시) 다음처럼 봅니다.

```
ls -l /mnt/img/var/lib/rpm/
xxd -l 16 /mnt/img/var/lib/rpm/rpmdb.sqlite
ls -l /mnt/img/var/lib/rpm/rpmdb.sqlite-wal
```

`rpmdb.sqlite` 가 있고 첫 16바이트가 SQLite 파일 머리이면 sqlite 백엔드이고, `Packages` 만 있으면 Berkeley DB 백엔드입니다[4]. `-wal` 파일 크기가 0 보다 크면 본 파일에 옮기지 않은 페이지가 있을 수 있어 WAL 까지 읽어야 합니다[4]. 파일 머리와 WAL 구조는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html)를 봅니다.

`history.sqlite` 는 사본에서 sqlite3 로 조회합니다.

```
sqlite3 history.sqlite "
SELECT t.id, datetime(t.dt_begin,'unixepoch'), t.user_id, t.cmdline,
       r.name||'-'||r.version||'-'||r.release||'.'||r.arch,
       ti.action, ti.reason, ti.state, p.repoid
FROM trans t
JOIN trans_item ti ON ti.trans_id = t.id
JOIN rpm r ON r.item_id = ti.item_id
LEFT JOIN repo p ON p.id = ti.repo_id
ORDER BY t.id;"
```

아래는 만든 예시 출력입니다.

```
41|2024-05-24 04:06:12|1000|install zip|zip-3.0-35.el9.x86_64|1|2|1|appstream
42|2024-05-24 04:10:40|4294967295|-y upgrade|openssl-3.0.7-27.el9.x86_64|6|2|1|baseos
```

41번은 UID 1000 인 로그인 세션에서 사용자가 직접 요청한 설치(action 1, reason 2)이고, 42번은 로그인 세션 밖에서 돈 갱신입니다. UID 를 계정 이름으로 잇는 법은 [UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md) 에 있습니다.

### 공개 도구로 한 번

- rpm: 작업용 사본에 `rpm --dbpath 사본경로 -qa --last` 를 쓰면 설치 시각 순서로 목록이 나옵니다[2]. `rpm --dbpath 사본경로 -qa --queryformat '%{INSTALLTIME}~%{NAME}~%{VERSION}-%{RELEASE}\n'` 는 UAC 가 쓰는 질의와 같은 모양으로 에포크 숫자를 뽑습니다[20]. `rpmdb --exportdb` 는 DB 를 헤더 목록으로 내보내고, `rpmdb --verifydb` 는 DB 자체의 무결성을 점검합니다[6].
- dnf: 실행 중인 시스템에서 `dnf history list`, `dnf history info 번호`, `dnf history userinstalled` 로 같은 DB 를 봅니다[20][24].
- 감사 로그: `ausearch -m SOFTWARE_UPDATE` 로 audit 플러그인이 남긴 이벤트를 모읍니다[8].
- 저널: syslog 플러그인 줄은 rpm 4.16 이면 식별자 `[RPM]` 으로, 최신 rpm 이면 `journalctl -t rpm` 으로 찾습니다[7].

## 교차 검증

| 함께 볼 것 | 맞춰 볼 점 |
|---|---|
| [sudo·su 사용 기록](../logins/sudo-su.md) | `trans.cmdline` 과 같은 시각에 `dnf` 를 부른 sudo 줄이 있고, 그 계정이 `user_id` 와 맞는가 |
| [인증 로그 (auth.log·secure)](../logins/auth-log.md) | loginuid 가 가리키는 계정이 그 시각에 로그인해 있었는가 |
| [감사 로그 형식](../../01-foundations/logging/auditd-format.md) | `SOFTWARE_UPDATE` 이벤트가 dnf 트랜잭션과 같은 패키지·시각인가, dnf 기록에 없는 `rpm -i` 설치가 있는가 |
| [셸 명령 기록](../execution/shell-history/index.md) | `dnf`·`rpm` 명령이 셸 기록에도 있는가 |
| [패키지 파일 변조 확인](package-verify.md) | 설치 뒤 패키지 파일이 바뀌었는가 |
| [설치 날짜 가늠하기](../system-info/install-date.md) | 가장 이른 `Installtime`·`dt_begin` 이 설치 무렵과 맞는가 |
| [dpkg·apt 기록](dpkg-apt.md) | Debian·Ubuntu 계열에서 같은 질문을 풀 때 |

## 실습

NIST CFReDS 같은 공개 저장소의 RHEL·CentOS·Fedora 디스크 이미지로 다음을 풀어 봅니다.

1. `/var/lib/rpm` 에 어떤 파일이 있는가? 백엔드는 무엇이고, `-wal` 파일이 비어 있는가?
2. rpm DB 에서 `Installtime` 이 가장 늦은 패키지 다섯 개는 무엇이고, UTC 로 언제인가?
3. 그 다섯 개가 `history.sqlite` 의 어느 트랜잭션에 들어 있는가? 트랜잭션에 없는 패키지가 있다면 어떤 방법으로 설치했을 가능성이 있는가?
4. `user_id` 값의 종류는 몇 가지이고, 각각 어느 계정인가? 4294967295 인 트랜잭션은 몇 개인가?
5. `dnf.rpm.log` 의 `Erase:` 줄과 `trans_item.action` 8 줄이 같은 패키지·같은 시각을 가리키는가? 시간대 차이를 빼고 몇 초 차이가 나는가?

## 참고 문헌

1. rpm, docs/manual/tags.md. https://github.com/rpm-software-management/rpm/blob/master/docs/manual/tags.md
2. rpm 4.16, doc/rpm.8. https://github.com/rpm-software-management/rpm/blob/rpm-4.16.x/doc/rpm.8
3. rpm, macros.in. https://github.com/rpm-software-management/rpm/blob/master/macros.in
4. rpm 4.16, lib/backend/sqlite.c·dbi.c. https://github.com/rpm-software-management/rpm/tree/rpm-4.16.x/lib/backend
5. rpm, docs/man/rpm-queryformat.7.scd. https://github.com/rpm-software-management/rpm/blob/master/docs/man/rpm-queryformat.7.scd
6. rpm, docs/man/rpmdb.8.scd. https://github.com/rpm-software-management/rpm/blob/master/docs/man/rpmdb.8.scd
7. rpm, rpm-4.16.x/plugins/syslog.c·docs/man/rpm-plugin-syslog.8.scd. https://github.com/rpm-software-management/rpm/blob/rpm-4.16.x/plugins/syslog.c , https://github.com/rpm-software-management/rpm/blob/master/docs/man/rpm-plugin-syslog.8.scd
8. rpm, rpm-4.16.x/plugins/audit.c·docs/man/rpm-plugin-audit.8.scd. https://github.com/rpm-software-management/rpm/blob/rpm-4.16.x/plugins/audit.c , https://github.com/rpm-software-management/rpm/blob/master/docs/man/rpm-plugin-audit.8.scd
9. linux-audit, audit-documentation specs/messages/message-dictionary.csv. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
10. linux-audit, audit-userspace docs/audit.rules.7·docs/auditctl.8. https://github.com/linux-audit/audit-userspace/blob/master/docs/audit.rules.7 , https://github.com/linux-audit/audit-userspace/blob/master/docs/auditctl.8
11. dnf, dnf/const.py.in·dnf/logging.py·etc/logrotate.d/dnf. https://github.com/rpm-software-management/dnf/blob/master/dnf/const.py.in , https://github.com/rpm-software-management/dnf/blob/master/dnf/logging.py , https://github.com/rpm-software-management/dnf/blob/master/etc/logrotate.d/dnf
12. dnf, dnf/transaction.py·dnf/yum/rpmtrans.py. https://github.com/rpm-software-management/dnf/blob/master/dnf/transaction.py , https://github.com/rpm-software-management/dnf/blob/master/dnf/yum/rpmtrans.py
13. dnf, dnf/db/history.py·dnf/yum/misc.py. https://github.com/rpm-software-management/dnf/blob/master/dnf/db/history.py , https://github.com/rpm-software-management/dnf/blob/master/dnf/yum/misc.py
14. libdnf, libdnf/conf/ConfigMain.cpp. https://github.com/rpm-software-management/libdnf/blob/dnf-4-master/libdnf/conf/ConfigMain.cpp
15. libdnf, libdnf/transaction/sql/·Types.hpp·TransactionItemReason.hpp·Swdb.cpp·Swdb.hpp. https://github.com/rpm-software-management/libdnf/tree/dnf-4-master/libdnf/transaction
16. dnf5, include/libdnf5/conf/const.hpp·libdnf5/conf/config_main.cpp·libdnf5/transaction/db/db.cpp·dnf5/main.cpp. https://github.com/rpm-software-management/dnf5
17. yum, yum/logginglevels.py·yum/config.py·yum/rpmtrans.py. https://github.com/rpm-software-management/yum/tree/master/yum
18. yum, yum/history.py·yum/rpmsack.py·yum/config.py. https://github.com/rpm-software-management/yum/blob/master/yum/history.py , https://github.com/rpm-software-management/yum/blob/master/yum/rpmsack.py
19. fox-it dissect.target, plugins/os/unix/linux/redhat/yum.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/redhat/yum.py
20. UAC, artifacts/live_response/packages/rpm.yaml·dnf.yaml, artifacts/files/packages/dnf.yaml·yum.yaml. https://github.com/tclahr/uac/tree/main/artifacts/live_response/packages , https://github.com/tclahr/uac/tree/main/artifacts/files/packages
21. Velociraptor, artifacts/definitions/Linux/RHEL/Packages.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/RHEL/Packages.yaml
22. ForensicArtifacts, artifacts/data/linux.yaml (YumSources). https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
23. plaso, plaso/parsers/text_plugins·sqlite_plugins. https://github.com/log2timeline/plaso/tree/main/plaso/parsers
24. dnf, doc/command_ref.rst. https://github.com/rpm-software-management/dnf/blob/master/doc/command_ref.rst
