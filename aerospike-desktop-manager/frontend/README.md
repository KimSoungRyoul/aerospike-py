# Aerospike Desktop Manager — Frontend

React + TypeScript + Vite 기반의 SPA 프론트엔드.
Tailwind CSS + shadcn/ui 컴포넌트로 구성된 Aerospike 클러스터 관리 UI입니다.

## Tech Stack

| Category | Technology |
|----------|-----------|
| Framework | React 19 |
| Language | TypeScript 5.7 |
| Build | Vite 6 |
| Styling | Tailwind CSS 3 + tailwindcss-animate |
| UI Components | shadcn/ui (Radix UI primitives) |
| State | Zustand 5 |
| HTTP Client | Axios |
| Charts | Recharts 2 |
| Routing | React Router 7 |
| Table | TanStack Table 8 |
| Icons | Lucide React |

## Quick Start

```bash
# 의존성 설치
npm install

# 개발 서버 (http://localhost:5173)
npm run dev

# 프로덕션 빌드
npm run build

# 빌드 결과 미리보기
npm run preview
```

개발 서버는 `/api` 경로를 `http://localhost:8000`으로 프록시합니다 (vite.config.ts).

## Project Structure

```
frontend/
├── package.json
├── tsconfig.json
├── vite.config.ts              # Vite 설정 + API 프록시
├── tailwind.config.ts
├── postcss.config.js
├── index.html
│
└── src/
    ├── main.tsx                # 앱 진입점
    ├── App.tsx                 # 라우팅 설정
    ├── index.css               # Tailwind 기본 스타일
    │
    ├── api/                    # Backend API 클라이언트
    │   ├── client.ts           #   Axios 인스턴스 (baseURL: /api/v1)
    │   ├── types.ts            #   TypeScript 인터페이스 (backend 모델과 동기화)
    │   ├── connections.ts      #   연결 관리 API
    │   ├── cluster.ts          #   클러스터/네임스페이스 API
    │   ├── records.ts          #   레코드 CRUD + scan API
    │   ├── indexes.ts          #   인덱스 API
    │   ├── udfs.ts             #   UDF API
    │   └── metrics.ts          #   메트릭 + info terminal API
    │
    ├── stores/                 # Zustand 상태 관리
    │   ├── connectionStore.ts  #   연결 목록, 활성 연결
    │   ├── browserStore.ts     #   레코드 브라우저 (NS/셋 선택, scan 결과)
    │   ├── metricsStore.ts     #   WebSocket 메트릭 스트림 (60개 스냅샷 히스토리)
    │   └── uiStore.ts          #   UI 상태 (탭, 사이드바 등)
    │
    ├── pages/                  # 페이지 컴포넌트
    │   ├── ConnectionsPage.tsx #   연결 관리
    │   ├── ClusterPage.tsx     #   클러스터 개요
    │   ├── BrowserPage.tsx     #   레코드 브라우저
    │   ├── IndexesPage.tsx     #   인덱스 관리
    │   ├── UdfsPage.tsx        #   UDF 관리
    │   ├── MetricsPage.tsx     #   실시간 메트릭 대시보드
    │   ├── TerminalPage.tsx    #   Info 명령 터미널
    │   └── SettingsPage.tsx    #   설정
    │
    ├── components/
    │   ├── browser/            #   레코드 테이블, 상세, 필터, 편집기
    │   ├── cluster/            #   클러스터 개요, 네임스페이스, 노드 목록
    │   ├── connection/         #   연결 다이얼로그, 상태, 트리
    │   ├── layout/             #   AppLayout, Sidebar, TabBar
    │   ├── metrics/            #   차트, 대시보드, 운영 통계
    │   ├── terminal/           #   터미널 패널
    │   ├── common/             #   EmptyState, ErrorState, JsonViewer 등
    │   └── ui/                 #   shadcn/ui 컴포넌트 (24개)
    │
    ├── hooks/                  # 커스텀 훅
    │   ├── useKeyboardShortcuts.ts
    │   ├── useMediaQuery.ts
    │   ├── usePagination.ts
    │   └── useWebSocket.ts
    │
    └── lib/                    # 유틸리티
        ├── constants.ts
        ├── formatters.ts
        └── utils.ts            # cn() (clsx + tailwind-merge)
```

## API Client

모든 API 호출은 `src/api/client.ts`의 Axios 인스턴스를 통해 이루어집니다.

```typescript
// baseURL: "/api/v1"
// 연결별 경로: /c/{connId}/...

// 예시
await api.get(`/c/${connId}/cluster`);
await api.post(`/c/${connId}/records/scan`, { namespace, set, page, page_size });
```

### API 경로 매핑

| Module | Backend Path |
|--------|-------------|
| `connections.ts` | `/api/v1/connections` |
| `cluster.ts` | `/api/v1/c/{connId}/cluster`, `/c/{connId}/namespaces` |
| `records.ts` | `/api/v1/c/{connId}/records/scan`, `/put`, `/{ns}/{set}/{pk}` |
| `indexes.ts` | `/api/v1/c/{connId}/indexes/{ns}` |
| `udfs.ts` | `/api/v1/c/{connId}/udfs`, `/apply` |
| `metrics.ts` | `/api/v1/c/{connId}/metrics/server`, `/c/{connId}/info` |

### WebSocket

`metricsStore.ts`에서 실시간 메트릭 스트리밍:

```
ws(s)://{host}/api/v1/c/{connId}/metrics/stream
```

2초 간격으로 서버/네임스페이스 통계를 수신하며, 최근 60개 스냅샷을 유지합니다.

## Development Notes

- `@` alias는 `src/`를 가리킵니다 (vite.config.ts, tsconfig.json)
- shadcn/ui 컴포넌트 추가: `npx shadcn@latest add <component>`
- 개발 중 API 프록시: Vite가 `/api` → `http://localhost:8000` 으로 프록시
- 프로덕션: 빌드 결과물(`dist/`)을 백엔드가 static files로 서빙
