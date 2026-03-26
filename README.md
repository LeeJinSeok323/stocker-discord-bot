# Stocker Discord Bot (주식 스크리너 백엔드)

디스코드를 기반으로 작동하는 미국 주식(SEC 공시) 실시간 알림 및 스크리닝 시스템입니다.

## 🚀 현재 작업 진행 현황

### 1. SEC 공시 수집 및 관리 (완료)
- [x] 특정 티커 기반 CIK 조회 및 SEC EDGAR API 연동
- [x] 최근 공시 내역(Submissions) 및 상세 문서 URL 파싱
- [x] MySQL 데이터베이스 연동 및 공시 메타데이터(`sec_filing`) 저장
- [x] 공시 중복 알림 방지 로직 (DB 접수번호 체크)

### 2. 디스코드 봇 및 알림 시스템 (완료)
- [x] 슬래시 명령어 기반 구독 시스템 (`/구독`, `/구독취소`, `/목록`)
- [x] 종목별 전용 알림 채널 자동 생성 및 사용자 권한(읽기 전용) 관리
- [x] '알림' 카테고리 내 채팅 금지 및 관리자 예외 처리
- [x] 20초 주기 고속 폴링 및 Asyncio 기반 티커 병렬 처리 (속도 최적화)
- [x] 중앙 집중식 문구 관리 시스템 (`config/messages.py`)
- [x] 관리자 전용 `/테스트공시` 명령어 구현

### 3. 데이터 관리 및 보안 (완료)
- [x] JSON 기반 설정을 MySQL DB(`sec_watchlist`, `sec_ticker_channel`)로 마이그레이션
- [x] `.env` 및 `.gitignore`를 통한 보안 강화 및 가상환경 설정
- [x] 티커 구독 시 SEC 등록 여부 사전 검증 로직 추가

---

## 🛠 미구현 및 향후 계획

### 1. AI 공시 분석 (예정)
- [ ] 8-K 등 중요 공시 발생 시 AI API(GPT 등)를 활용한 내용 요약 및 분석
- [ ] 분석 결과 DB 저장 및 디스코드 채널 전송

### 3. 태풍의 눈(Short Squeeze) 탐지기 (진행 예정)
- [ ] 금융 데이터 수집 파이프라인 구축 (Short Interest, CTB 등)
- [ ] 데이터 저장 및 관리용 `stock_metrics` 테이블 설계
- [ ] 스크리닝 알고리즘 구현 (거래량 응축, Short Interest 과다, CTB 300% 이상)
- [ ] `/태풍의눈` 탐지 결과 명령어 구현


---

---

## 🏗 시스템 아키텍처 및 데이터 전략
- **Language:** Python 3.14+
- **Database:** 
  - **MySQL (봇 설정용):** 사용자 구독 정보 및 공시 메타데이터 관리
  - **ClickHouse (주식 데이터 전용):** 대규모 시계열(일봉/분봉) 데이터 고속 처리
- **Library:** discord.py, requests, beautifulsoup4, clickhouse-driver
- **Scheduler:** tasks.loop (Asyncio)

### 📊 ClickHouse 데이터 아키텍처 (주식 데이터)
- **설계 배경:** Ubuntu Mini PC(16GB RAM) 환경에서의 리소스 최적화 및 열 지향(Columnar) DB 도입을 통한 쓰기/조회 병목 해소.
- **데이터 관리 전략 (Tiering):**
  - **Daily (일봉):** 영구 보관 (연도별 파티션) - 장기 추세 및 백테스팅.
  - **Intraday (1분봉):** 최근 5일 유지 (TTL 자동 삭제) - 실시간 변동성 및 알림 처리.
- **핵심 기술:** 
  - `MergeTree` 엔진 및 희소 인덱스를 통한 RAM 효율화.
  - 컨테이너 메모리 4GB 제한 및 ZSTD 압축으로 스토리지 사용량 90% 절감.

### 4. ClickHouse 인프라 및 수집 파이프라인
- [ ] Docker Compose 환경 구축: MySQL(봇 설정) + ClickHouse(데이터) 하이브리드 구성.
- [ ] Batch Collector 개발: yfinance/전문 API 활용하여 8,000개 종목 데이터 수집.
- [ ] MergeTree 설계 및 데이터 브릿지(Bulk Insert) 구현.
- [ ] `stock_metrics` 활용한 스크리닝 알고리즘 및 `/태풍의눈` 구현.

- **Project Structure:**
  - `bot/`: 디스코드 봇 로직 및 명령어
  - `config/`: DB 설정, 구독 관리, 메시지 템플릿
  - `core/`: SEC 공시 체크 핵심 비즈니스 로직
  - `sec/`: SEC API 연동 및 데이터 처리/저장
