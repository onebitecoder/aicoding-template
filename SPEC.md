# Stock Portfolio Tracker - Technical Specification

> **이 문서의 용도**: 프로젝트 초기 구현 시 Claude가 참고하는 **설계 청사진**입니다.
> 구현 완료 후에는 코드와 테스트가 진실의 원천(Source of Truth)이 됩니다.
> 큰 아키텍처 변경이 있을 때만 이 문서를 업데이트합니다.
>
> **참고**: 이 프로젝트는 웹 애플리케이션 개발을 위한 **예시 샘플 프로젝트**입니다.
> React + FastAPI 풀스택 개발의 구조, 패턴, 베스트 프랙티스를 보여주는 학습 및 참고용 자료입니다.

---

## 0. Data Flow Definition (필수 - 프로젝트 시작 전 정의)

> **IMPORTANT**: 프로젝트 개발 전에 이 섹션을 먼저 작성하세요.
> 데이터 소스와 흐름을 명확히 정의하지 않으면 개발 중 큰 삽질이 발생합니다.

### 0.1 Data Source (데이터 소스)

| 항목 | 내용 |
|------|------|
| **소스 타입** | External API (무료) |
| **소스 이름** | Yahoo Finance (yfinance 라이브러리) |
| **접근 방법** | Python 라이브러리 (pip install yfinance) |
| **인증 필요** | No (API 키 불필요) |
| **비용** | 무료 |
| **Rate Limit** | 비공식 API이므로 과도한 요청 시 차단 가능 (1초 간격 권장) |

<details>
<summary>📋 참고 가이드: 데이터 소스 타입 비교 (구현 대상 아님, 접어두기)</summary>

#### 데이터 소스 타입 가이드

| 타입 | 예시 | 난이도 | 비용 |
|------|------|--------|------|
| **Public API (무료)** | Yahoo Finance, CoinGecko | 쉬움 | 무료 |
| **Public API (유료)** | Alpha Vantage Pro, Bloomberg | 쉬움 | 유료 |
| **API 키 필요** | Alpha Vantage (무료), Finnhub | 보통 | 무료/유료 |
| **OAuth 필요** | Google Sheets, Notion | 어려움 | 무료 |
| **크롤링** | 네이버 금융, 다음 금융 | 보통 | 무료 |
| **파일 업로드** | CSV 거래내역, Excel 포트폴리오 | 쉬움 | 무료 |
| **사용자 입력** | 매수/매도 기록 직접 입력 | 쉬움 | 무료 |

#### 주식 데이터 API 비교

| API | 무료 한도 | API 키 | 실시간 | 한국 주식 |
|-----|----------|--------|--------|----------|
| **Yahoo Finance** | 무제한* | 불필요 | 15분 지연 | 지원 (.KS, .KQ) |
| Alpha Vantage | 25회/일 | 필요 | 유료만 | 미지원 |
| Finnhub | 60회/분 | 필요 | 지원 | 미지원 |
| 한국투자증권 API | 무제한 | 필요 | 지원 | 지원 |

*비공식 API이므로 안정성 보장 없음

</details>

### 0.2 Input (사용자 입력)

| 입력 항목 | 타입 | 예시 | 필수 여부 |
|-----------|------|------|----------|
| 종목 코드 | String | AAPL, 005930.KS (삼성전자) | 필수 |
| 매수 가격 | Number | 150.00 (USD), 70000 (KRW) | 필수 |
| 매수 수량 | Number | 10 | 필수 |
| 매수 날짜 | Date | 2024-01-15 | 필수 |
| 메모 | String | "장기 투자용" | 선택 |

### 0.3 Output (결과 출력)

| 출력 항목 | 형태 | 설명 |
|-----------|------|------|
| 포트폴리오 요약 | 카드 UI | 총 자산, 총 수익률, 일간 변동 |
| 보유 종목 목록 | 테이블 | 종목별 현재가, 평가금액, 수익률 |
| 포트폴리오 차트 | 파이 차트 | 종목별 비중 |
| 수익률 그래프 | 라인 차트 | 시간별 포트폴리오 가치 변동 |
| 종목 상세 정보 | 상세 페이지 | 차트, 재무정보, 뉴스 |

### 0.4 Data Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │     │  Frontend   │     │   Backend   │     │ Data Source │
│   Input     │────▶│   (React)   │────▶│  (FastAPI)  │────▶│  (Yahoo     │
│ (종목, 수량) │     │             │     │             │     │  Finance)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   │                   │
                           │                   │                   │
                           ▼                   ▼                   │
                    ┌─────────────┐     ┌─────────────┐            │
                    │   Output    │◀────│  Database   │◀───────────┘
                    │ (대시보드)   │     │  (SQLite3)  │  (시세 캐싱)
                    └─────────────┘     └─────────────┘
```

### 0.5 Data Refresh (데이터 갱신 주기)

| 데이터 | 갱신 주기 | 방법 |
|--------|----------|------|
| 주가 시세 | 1분마다 (장중) | Polling / WebSocket |
| 포트폴리오 계산 | 시세 업데이트 시 | Event-driven |
| 종목 기본정보 | 1일 1회 | Daily batch |
| 차트 데이터 | 요청 시 | On-demand |

### 0.6 Data Access Checklist (개발 전 확인사항)

프로젝트 시작 전 반드시 확인하세요:

- [x] 데이터 소스에 접근 가능한가? → Yahoo Finance는 API 키 없이 접근 가능
- [x] Rate limit이 있는가? → 비공식 API, 1초 간격 요청 권장
- [x] 데이터 형식은 무엇인가? → JSON (yfinance가 DataFrame으로 변환)
- [x] 인증 방식은 무엇인가? → 인증 불필요
- [x] 비용이 발생하는가? → 무료
- [x] 데이터 갱신 주기는 어떻게 되는가? → 15분 지연 (무료)
- [x] 오프라인/에러 시 대체 방안은? → DB 캐시된 마지막 시세 사용

---

## 1. Project Overview

### 1.1 Purpose
Stock Portfolio Tracker는 개인 투자자가 자신의 주식 포트폴리오를 관리하고 수익률을 추적할 수 있는 웹 애플리케이션입니다.

**이 프로젝트의 목적**:
1. **학습 자료**: React + FastAPI 풀스택 웹 개발의 실전 예제
2. **참고 샘플**: 프로젝트 구조, API 설계, 데이터베이스 스키마 설계의 좋은 예시
3. **템플릿**: 새로운 웹 프로젝트 시작 시 참고할 수 있는 boilerplate

### 1.2 Goals
- 보유 종목 및 거래 내역 관리
- 실시간 포트폴리오 가치 및 수익률 계산
- 종목별/전체 수익률 시각화
- 포트폴리오 비중 분석

### 1.3 Target Users
- 주식 투자를 시작한 개인 투자자
- 여러 증권사 계좌를 통합 관리하고 싶은 사용자
- 투자 성과를 체계적으로 기록하고 싶은 사용자

### 1.4 Key Use Cases
- 매수/매도 거래 기록 추가
- 포트폴리오 현황 대시보드 조회
- 종목별 상세 정보 및 차트 확인
- 수익률 분석 및 리포트 생성

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │   Portfolio  │  │    Stock     │      │
│  │   Summary    │  │    Table     │  │   Detail     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Trade Form   │  │    Charts    │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  API Layer   │  │   Portfolio  │  │    Stock     │      │
│  │  (FastAPI)   │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
           ↕                    ↕                    ↕
┌──────────────────┐  ┌─────────────────────────────────────┐
│   SQLite3        │  │     Yahoo Finance API               │
│   (Database)     │  │     (yfinance library)              │
└──────────────────┘  └─────────────────────────────────────┘
```

### 2.2 Component Breakdown

#### Frontend (React)
- **역할**: 사용자 인터페이스 제공 및 데이터 시각화
- **기술**: React, Recharts (차트), Axios
- **주요 컴포넌트**:
  - Dashboard Summary (총 자산, 수익률)
  - Portfolio Table (보유 종목 목록)
  - Stock Detail View (종목 상세 정보)
  - Trade Form (매수/매도 입력)
  - Charts (파이차트, 라인차트)

#### Backend API (FastAPI)
- **역할**: 비즈니스 로직 처리, API 제공
- **기술**: Python, FastAPI, SQLAlchemy
- **주요 모듈**:
  - REST API endpoints
  - Portfolio calculation
  - Stock data fetching
  - Request validation

#### Stock Service
- **역할**: Yahoo Finance에서 주식 데이터 조회
- **기술**: Python, yfinance
- **주요 기능**:
  - 현재가 조회
  - 과거 시세 조회
  - 종목 기본 정보 조회
  - 데이터 캐싱

#### Database (SQLite3)
- **역할**: 사용자 데이터 저장
- **저장 데이터**:
  - 보유 종목 (holdings)
  - 거래 내역 (transactions)
  - 시세 캐시 (price_cache)

---

## 3. Data Flow

### 3.1 주가 조회 Flow
```
사용자 대시보드 접속 → Frontend 렌더링 →
Backend API 호출 → yfinance로 현재가 조회 →
DB에서 보유 종목 조회 → 수익률 계산 →
JSON 응답 → Frontend 렌더링
```

### 3.2 거래 추가 Flow
```
사용자 거래 입력 (종목, 가격, 수량) →
Frontend Form Submit → Backend API 호출 →
DB에 거래 저장 → Holdings 업데이트 →
성공 응답 → Frontend 새로고침
```

---

## 4. Core Features & Functionality

### 4.1 Portfolio Dashboard

#### 요약 정보
- 총 평가금액 (현재 시세 기준)
- 총 투자금액 (매수 금액 합계)
- 총 수익/손실 (금액)
- 총 수익률 (%)
- 일간 변동 (금액, %)

#### 보유 종목 테이블
```
| 종목명 | 종목코드 | 보유수량 | 평균단가 | 현재가 | 평가금액 | 수익률 |
|--------|----------|----------|----------|--------|----------|--------|
| 애플   | AAPL     | 10       | $150.00  | $175.00| $1,750   | +16.7% |
| 삼성전자| 005930.KS| 50       | ₩70,000  | ₩75,000| ₩3,750,000| +7.1% |
```

### 4.2 Trade Management

#### 거래 유형
- **매수 (BUY)**: 종목 추가 또는 수량 증가
- **매도 (SELL)**: 보유 수량 감소
- **배당 (DIVIDEND)**: 배당금 기록 (선택)

#### 거래 입력 필드
```python
class TradeInput:
    symbol: str          # 종목 코드 (AAPL, 005930.KS)
    trade_type: str      # BUY, SELL, DIVIDEND
    quantity: int        # 수량
    price: float         # 단가
    trade_date: date     # 거래일
    memo: str = None     # 메모 (선택)
```

### 4.3 Stock Information

#### Yahoo Finance에서 조회 가능한 데이터
```python
import yfinance as yf

stock = yf.Ticker("AAPL")

# 기본 정보
stock.info['longName']        # Apple Inc.
stock.info['sector']          # Technology
stock.info['marketCap']       # 2,800,000,000,000

# 현재가
stock.info['currentPrice']    # 175.00

# 과거 시세
stock.history(period="1y")    # 1년 데이터 (DataFrame)

# 재무 정보
stock.info['trailingPE']      # PER
stock.info['dividendYield']   # 배당수익률
```

### 4.4 Charts & Visualization

#### 포트폴리오 비중 (파이 차트)
```javascript
const data = [
  { name: 'AAPL', value: 35, color: '#8884d8' },
  { name: '삼성전자', value: 25, color: '#82ca9d' },
  { name: 'TSLA', value: 20, color: '#ffc658' },
  { name: '현금', value: 20, color: '#ff8042' },
];
```

#### 포트폴리오 가치 변동 (라인 차트)
```javascript
const data = [
  { date: '2024-01', value: 10000000 },
  { date: '2024-02', value: 10500000 },
  { date: '2024-03', value: 11200000 },
  // ...
];
```

---

## 5. API Design

### 5.1 REST Endpoints

> **규칙**: 모든 엔드포인트는 trailing slash 없이 통일 (`/api/v1/users` O, `/api/v1/users/` X)

#### System Endpoints
```
GET /health
- 서버 상태 확인 (Railway 배포 필수)
- Response: { "status": "healthy" }
```

#### Portfolio Endpoints
```
GET /api/v1/portfolio/summary
- 포트폴리오 요약 정보
- Response: { total_value, total_cost, total_return, return_rate, daily_change }

GET /api/v1/portfolio/holdings
- 보유 종목 목록
- Response: { holdings: [...], total_count }

GET /api/v1/portfolio/history
- 포트폴리오 가치 변동 내역
- Query params: period (1m, 3m, 6m, 1y, all)
- Response: { history: [{ date, value }, ...] }
```

#### Trade Endpoints
```
GET /api/v1/trades
- 거래 내역 조회
- Query params: symbol, start_date, end_date, limit, offset
- Response: { trades: [...], total, page }

POST /api/v1/trades
- 거래 추가
- Body: { symbol, trade_type, quantity, price, trade_date, memo }
- Response: { id, message: "거래가 추가되었습니다" }

DELETE /api/v1/trades/{trade_id}
- 거래 삭제
- Response: { message: "거래가 삭제되었습니다" }
```

#### Stock Endpoints
```
GET /api/v1/stocks/{symbol}
- 종목 정보 조회
- Response: { symbol, name, price, change, change_percent, ... }

GET /api/v1/stocks/{symbol}/history
- 종목 과거 시세
- Query params: period (1d, 5d, 1m, 3m, 6m, 1y, 5y)
- Response: { history: [{ date, open, high, low, close, volume }, ...] }

GET /api/v1/stocks/search?q={query}
- 종목 검색
- Response: { results: [{ symbol, name, exchange }, ...] }
```

### 5.2 Response Format
```json
{
  "status": "success",
  "data": { ... },
  "error": null,
  "metadata": {
    "timestamp": "2024-01-15T09:30:00Z",
    "version": "1.0.0"
  }
}
```

### 5.3 Error Codes
- `400`: Bad Request (잘못된 종목 코드, 유효하지 않은 수량 등)
- `404`: Not Found (종목 없음, 거래 없음)
- `429`: Too Many Requests (API rate limit)
- `500`: Internal Server Error
- `503`: Service Unavailable (Yahoo Finance 연결 실패)

---

## 6. Database Schema (SQLite3)

### 6.1 SQLAlchemy Models (스키마 원천)

> **규칙**: Raw SQL 사용 금지. SQLAlchemy ORM 모델이 DB 스키마의 원천이며, Alembic으로 마이그레이션한다.

```python
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Holding(Base):
    """보유 종목"""
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, nullable=False, index=True)  # 종목 코드
    name = Column(String)                        # 종목명
    quantity = Column(Integer, default=0)         # 보유 수량
    avg_price = Column(Float, default=0)          # 평균 매수가
    total_cost = Column(Float, default=0)         # 총 매수 금액
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="holding")


class Transaction(Base):
    """거래 내역"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, ForeignKey("holdings.symbol"), nullable=False, index=True)
    trade_type = Column(String, nullable=False)   # BUY, SELL, DIVIDEND
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    trade_date = Column(DateTime, nullable=False, index=True)
    memo = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    holding = relationship("Holding", back_populates="transactions")


class PriceCache(Base):
    """시세 캐시"""
    __tablename__ = "price_cache"

    symbol = Column(String, primary_key=True)
    price = Column(Float, nullable=False)
    change = Column(Float)
    change_percent = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PortfolioHistory(Base):
    """포트폴리오 히스토리"""
    __tablename__ = "portfolio_history"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)
    total_value = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 6.2 Pydantic Schemas (API 요청/응답)

> **규칙**: DB 스키마 변경 시 Pydantic 스키마도 반드시 함께 업데이트한다.

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# --- Trade ---
class TradeCreate(BaseModel):
    symbol: str
    trade_type: str        # BUY, SELL, DIVIDEND
    quantity: int
    price: float
    trade_date: datetime
    memo: Optional[str] = None

class TradeResponse(BaseModel):
    id: int
    symbol: str
    trade_type: str
    quantity: int
    price: float
    total_amount: float
    trade_date: datetime
    memo: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Holding ---
class HoldingResponse(BaseModel):
    id: int
    symbol: str
    name: Optional[str]
    quantity: int
    avg_price: float
    total_cost: float
    current_price: float       # 실시간 조회
    market_value: float        # quantity * current_price
    return_amount: float       # market_value - total_cost
    return_rate: float         # return_amount / total_cost * 100

    class Config:
        from_attributes = True


# --- Portfolio ---
class PortfolioSummary(BaseModel):
    total_value: float
    total_cost: float
    total_return: float
    return_rate: float
    daily_change: float
    daily_change_percent: float
```

---

## 7. Design Reference

### 7.0 디자인 레퍼런스 이미지 (IMPORTANT)

> **디자인 시작 전 필수 확인**: `design/` 폴더에 레퍼런스 이미지가 있는지 확인하세요.

```
design/
├── reference/           # 디자인 레퍼런스 이미지
│   ├── dashboard.png    # 대시보드 레이아웃
│   ├── mobile.png       # 모바일 화면
│   ├── components.png   # 컴포넌트 스타일
│   └── colors.png       # 색상 팔레트
└── README.md            # 디자인 가이드 설명
```

**레퍼런스 이미지 사용 방법**:
1. `design/reference/` 폴더에 원하는 디자인 이미지를 넣어주세요
2. Claude Code가 이미지를 분석하여 스타일을 적용합니다
3. 이미지가 없으면 Claude Code가 디자인 방향을 질문합니다

**지원 이미지 형식**: PNG, JPG, JPEG, WebP

### 7.1 UI/UX Design Guidelines

**디자인 컨셉**: 깔끔하고 직관적인 금융 대시보드

#### 색상 팔레트
- **Primary**: Blue (#3B82F6) - 신뢰, 안정
- **Success**: Green (#10B981) - 수익, 상승
- **Danger**: Red (#EF4444) - 손실, 하락
- **Background**: Gray (#F9FAFB)
- **Card**: White (#FFFFFF)

#### 수익/손실 색상 규칙
```jsx
// 수익: 초록색
<span className="text-green-500">+16.7%</span>

// 손실: 빨간색
<span className="text-red-500">-5.2%</span>

// 변동 없음: 회색
<span className="text-gray-500">0.0%</span>
```

#### 카드 레이아웃
```jsx
// 대시보드 요약 카드
<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
  <Card>
    <CardTitle>총 평가금액</CardTitle>
    <CardValue>₩15,230,000</CardValue>
    <CardChange positive>+₩1,230,000 (8.8%)</CardChange>
  </Card>
  // ...
</div>
```

### 7.2 Mobile-First Design
- 모바일에서 카드는 1열 배치
- 테이블은 가로 스크롤 또는 카드 형태로 변환
- 터치 타깃 최소 44x44px

---

## 8. Frontend Routes & Components

### 8.0 Page Routes

| URL | 페이지 | 설명 |
|-----|--------|------|
| `/` | Dashboard | 포트폴리오 요약, 보유 종목, 차트 |
| `/trades` | Trade List | 거래 내역 목록 |
| `/trades/new` | Trade Form | 새 거래 추가 |
| `/stocks/:symbol` | Stock Detail | 종목 상세 정보, 차트, 거래 내역 |

> **규칙**: 새 페이지는 반드시 새 URL로 생성. 모달/조건부 렌더링으로 페이지를 대체하지 않는다.

### 8.1 Frontend Components

#### Dashboard Summary
```jsx
function DashboardSummary({ portfolio }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4">
      <SummaryCard
        title="총 평가금액"
        value={formatCurrency(portfolio.totalValue)}
        change={portfolio.dailyChange}
      />
      <SummaryCard
        title="총 투자금액"
        value={formatCurrency(portfolio.totalCost)}
      />
      <SummaryCard
        title="총 수익"
        value={formatCurrency(portfolio.totalReturn)}
        change={portfolio.returnRate}
      />
      <SummaryCard
        title="일간 변동"
        value={formatCurrency(portfolio.dailyChangeAmount)}
        change={portfolio.dailyChangePercent}
      />
    </div>
  );
}
```

#### Holdings Table
```jsx
function HoldingsTable({ holdings }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>종목</TableHead>
          <TableHead>보유수량</TableHead>
          <TableHead>평균단가</TableHead>
          <TableHead>현재가</TableHead>
          <TableHead>평가금액</TableHead>
          <TableHead>수익률</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {holdings.map((holding) => (
          <TableRow key={holding.symbol}>
            <TableCell>{holding.name}</TableCell>
            <TableCell>{holding.quantity}</TableCell>
            <TableCell>{formatCurrency(holding.avgPrice)}</TableCell>
            <TableCell>{formatCurrency(holding.currentPrice)}</TableCell>
            <TableCell>{formatCurrency(holding.marketValue)}</TableCell>
            <TableCell className={holding.returnRate >= 0 ? 'text-green-500' : 'text-red-500'}>
              {formatPercent(holding.returnRate)}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

#### Trade Form
```jsx
function TradeForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    symbol: '',
    tradeType: 'BUY',
    quantity: '',
    price: '',
    tradeDate: new Date().toISOString().split('T')[0],
    memo: ''
  });

  return (
    <form onSubmit={handleSubmit}>
      <Input
        label="종목 코드"
        placeholder="AAPL, 005930.KS"
        value={formData.symbol}
        onChange={(e) => setFormData({...formData, symbol: e.target.value})}
      />
      <Select
        label="거래 유형"
        value={formData.tradeType}
        options={[
          { value: 'BUY', label: '매수' },
          { value: 'SELL', label: '매도' },
        ]}
      />
      <Input label="수량" type="number" />
      <Input label="단가" type="number" />
      <Input label="거래일" type="date" />
      <Button type="submit">거래 추가</Button>
    </form>
  );
}
```

---

## 9. Technical Considerations

### 9.1 Yahoo Finance (yfinance) 사용법

```python
import yfinance as yf

# 단일 종목 조회
stock = yf.Ticker("AAPL")
current_price = stock.info.get('currentPrice') or stock.info.get('regularMarketPrice')

# 한국 주식 조회 (코스피: .KS, 코스닥: .KQ)
samsung = yf.Ticker("005930.KS")
price = samsung.info.get('currentPrice')

# 여러 종목 한번에 조회
tickers = yf.Tickers("AAPL MSFT GOOGL")
for ticker in tickers.tickers.values():
    print(ticker.info['currentPrice'])

# 과거 데이터 조회
history = stock.history(period="1y")  # 1년
# period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
```

### 9.2 Rate Limiting 처리

```python
import time
from functools import wraps

def rate_limit(calls_per_second=1):
    """Yahoo Finance API 호출 속도 제한"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=1)
def get_stock_price(symbol: str):
    stock = yf.Ticker(symbol)
    return stock.info.get('currentPrice')
```

### 9.3 Caching Strategy

```python
from datetime import datetime, timedelta

CACHE_TTL = 60  # 60초

def get_price_with_cache(symbol: str, db: Session):
    # 캐시 확인
    cached = db.query(PriceCache).filter_by(symbol=symbol).first()

    if cached:
        updated = datetime.fromisoformat(cached.updated_at)
        if datetime.now() - updated < timedelta(seconds=CACHE_TTL):
            return cached.price

    # 캐시 미스 또는 만료: API 호출
    stock = yf.Ticker(symbol)
    price = stock.info.get('currentPrice')

    # 캐시 업데이트
    if cached:
        cached.price = price
        cached.updated_at = datetime.now().isoformat()
    else:
        db.add(PriceCache(symbol=symbol, price=price))

    db.commit()
    return price
```

### 9.4 Database Migration (Alembic)

```bash
# 초기 설정
alembic init alembic

# 모델 변경 후 마이그레이션 생성
alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
alembic upgrade head
```

> **규칙**: 모델 변경 후 반드시 마이그레이션 파일을 생성하고 Git에 커밋한다.

### 9.5 Error Handling

```python
class StockNotFoundError(Exception):
    pass

class APIRateLimitError(Exception):
    pass

def get_stock_info(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        # 유효한 종목인지 확인
        if not info or 'regularMarketPrice' not in info:
            raise StockNotFoundError(f"종목을 찾을 수 없습니다: {symbol}")

        return info

    except Exception as e:
        if "Too Many Requests" in str(e):
            raise APIRateLimitError("API 호출 한도 초과. 잠시 후 다시 시도하세요.")
        raise
```

---

## 10. Development Phases

### Phase 1: Foundation
- [ ] 프로젝트 초기 설정 (FastAPI + React)
- [ ] SQLite3 데이터베이스 스키마 생성
- [ ] yfinance 연동 테스트
- [ ] 기본 API 엔드포인트 구현

### Phase 2: Core Features
- [ ] 거래 추가/조회/삭제 API
- [ ] 포트폴리오 계산 로직
- [ ] 시세 캐싱 구현
- [ ] Holdings 자동 업데이트

### Phase 3: Frontend
- [ ] Dashboard Summary 컴포넌트
- [ ] Holdings Table 컴포넌트
- [ ] Trade Form 컴포넌트
- [ ] 차트 (Recharts)

### Phase 4: Enhancement
- [ ] 종목 검색 기능
- [ ] 종목 상세 페이지
- [ ] 포트폴리오 히스토리
- [ ] 반응형 디자인

---

## 11. Project Structure

```
stock-portfolio-tracker/
├── frontend/                # React 프론트엔드
│   ├── src/
│   │   ├── components/     # 재사용 컴포넌트
│   │   │   ├── DashboardSummary.jsx
│   │   │   ├── HoldingsTable.jsx
│   │   │   ├── TradeForm.jsx
│   │   │   └── Charts.jsx
│   │   ├── pages/          # 페이지 컴포넌트 (라우트 단위)
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── TradeListPage.jsx
│   │   │   ├── TradeNewPage.jsx
│   │   │   └── StockDetailPage.jsx
│   │   ├── api/            # Axios API 클라이언트
│   │   ├── utils/          # 유틸리티 (포맷터 등)
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── api/            # API 라우터
│   │   │   ├── portfolio.py
│   │   │   ├── trades.py
│   │   │   └── stocks.py
│   │   ├── models/         # SQLAlchemy 모델
│   │   ├── schemas/        # Pydantic 스키마
│   │   ├── services/       # 비즈니스 로직
│   │   │   ├── portfolio_service.py
│   │   │   └── stock_service.py
│   │   ├── repositories/   # 데이터 접근 계층
│   │   ├── utils/          # 유틸리티
│   │   ├── database.py     # DB 연결
│   │   └── main.py         # FastAPI 앱
│   ├── alembic/             # DB 마이그레이션
│   ├── tests/
│   └── requirements.txt
│
├── .claude/                 # Claude 설정
├── scripts/
│   ├── install.py           # 의존성 설치 스크립트
│   ├── dev.py               # 개발 서버 실행 스크립트
│   └── test.py              # 테스트 실행 스크립트
├── SPEC.md                  # 이 문서
├── README.md
├── Dockerfile
└── railway.toml
```

---

## 12. Environment Variables

```bash
# .env.example

# Backend
DATABASE_URL=sqlite:///./portfolio.db
LOG_LEVEL=INFO
ENVIRONMENT=development

# Frontend
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Stock Portfolio Tracker

# Railway (production)
# DATABASE_URL=postgresql://... (Railway 자동 제공)
# PORT=8000 (Railway 자동 제공)
```

---

## 13. Testing Strategy

### 13.1 Backend 테스트 시나리오

| 영역 | 테스트 항목 | 검증 내용 |
|------|-----------|----------|
| Portfolio | 포트폴리오 가치 계산 | 보유 종목 × 현재가 합산 정확성 |
| Portfolio | 수익률 계산 | (현재가 - 평균단가) / 평균단가 × 100 |
| Trade | 매수 거래 추가 | holdings 수량/평균단가 업데이트 |
| Trade | 매도 거래 추가 | 보유 수량 초과 매도 시 에러 |
| Trade | 거래 삭제 | holdings 재계산 |
| Stock | 시세 조회 | yfinance 모킹, 캐시 TTL 검증 |
| Stock | 잘못된 종목 코드 | StockNotFoundError 발생 |
| API | /health 엔드포인트 | 200 OK 응답 |

```python
# tests/test_portfolio.py
def test_calculate_portfolio_value():
    """포트폴리오 총 가치와 총 비용 계산"""
    holdings = [
        {"symbol": "AAPL", "quantity": 10, "avg_price": 150},
        {"symbol": "GOOGL", "quantity": 5, "avg_price": 2800},
    ]
    prices = {"AAPL": 175, "GOOGL": 2900}

    result = calculate_portfolio_value(holdings, prices)

    assert result["total_value"] == 10 * 175 + 5 * 2900
    assert result["total_cost"] == 10 * 150 + 5 * 2800


def test_add_buy_trade_updates_holding(db_session):
    """매수 거래 추가 시 보유 종목의 수량과 평균단가가 업데이트된다"""
    # Arrange: 기존 보유 종목 (10주, 평균 $150)
    # Act: 10주 추가 매수 ($200)
    # Assert: 20주, 평균 $175


def test_sell_exceeding_quantity_raises_error(db_session):
    """보유 수량보다 많은 매도 시 에러가 발생한다"""
    # Arrange: 10주 보유
    # Act & Assert: 15주 매도 시도 → ValueError
```

### 13.2 Frontend 테스트 시나리오

| 영역 | 테스트 항목 | 검증 내용 |
|------|-----------|----------|
| TradeForm | 필수 필드 검증 | 종목코드/수량/단가 비어있으면 제출 불가 |
| TradeForm | 정상 제출 | API 호출 + 성공 메시지 표시 |
| HoldingsTable | 데이터 렌더링 | 종목 목록이 테이블에 표시 |
| HoldingsTable | 수익률 색상 | 양수=초록, 음수=빨강 |
| Dashboard | API 에러 처리 | 에러 시 에러 메시지 표시 (더미값 X) |

```javascript
// TradeForm.test.jsx
describe('TradeForm', () => {
  it('종목코드 없이 제출하면 에러 메시지를 표시한다', () => {});
  it('정상 입력 후 제출하면 API를 호출하고 성공 메시지를 표시한다', () => {});
});

// HoldingsTable.test.jsx
describe('HoldingsTable', () => {
  it('보유 종목 목록을 렌더링한다', () => {});
  it('수익률이 양수면 초록색, 음수면 빨간색으로 표시한다', () => {});
});
```

---

## 14. Success Metrics

- [ ] 종목 시세 조회 성공률 > 99%
- [ ] API 응답 시간 < 500ms
- [ ] 포트폴리오 계산 정확도 100%
- [ ] 모바일 UI 반응형 지원
- [ ] 에러 발생 시 명확한 메시지 표시

---

**Document Version**: 3.0
**Template Type**: Stock Portfolio Tracker
**용도**: 초기 구현 청사진 (구현 후에는 코드가 Source of Truth)
