# Aerospike Desktop Manager - Playwright E2E Test Scenarios

## Step 1: 클러스터 연결 (Connection)

1. `http://localhost:5173` 접속
2. EmptyState 화면에서 "New Connection" 버튼 클릭
3. ConnectionDialog 폼 입력:
   - `#conn-name`: 기본값 "My Cluster" 지우고 `Docker Cluster` 입력
   - `#conn-host`: `127.0.0.1` (기본값 유지)
   - `#conn-port`: `3000` (기본값 유지)
   - `#conn-cluster`: `docker` 입력
4. "Connect" 버튼 클릭
5. **검증**: 연결 카드가 나타나고 `Connected` 배지, cluster_name `docker` 표시 확인
6. 스크린샷 캡처

---

## Step 2: 클러스터 정보 조회 (Cluster Overview)

1. 연결 카드의 `...` (더보기) 버튼 클릭하여 드롭다운 메뉴 열기
2. "View Cluster" 메뉴 항목 클릭
3. **검증 항목**:
   - "Cluster Overview" 제목 표시
   - 노드 수, 네임스페이스 정보 카드 표시
   - "Nodes" 탭 클릭 → 노드 목록 확인
   - "Namespaces" 탭 클릭 → `test` 네임스페이스 상세 확인
4. 스크린샷 캡처

---

## Step 3: Info Terminal 테스트

1. 탭 바에서 "Terminal" 텍스트 클릭하여 Terminal 페이지로 이동
2. 예제 배지 중 `namespaces` 클릭 → 입력창에 자동 입력 확인
3. "Execute" 버튼 클릭
4. **검증**: 결과에 `test` 네임스페이스 표시
5. 입력창 비우고 `build` 입력 후 "Execute" 클릭 → 빌드 버전 확인
6. 입력창 비우고 `statistics` 입력 후 "Execute" 클릭 → 통계 정보 확인
7. 스크린샷 캡처

---

## Step 4: 레코드 생성 (Record Create)

빈 DB에서 시작하므로 먼저 사이드바 확인 후 레코드를 생성합니다.

1. 탭 바에서 "Browser" 텍스트 클릭하여 Browser 페이지로 이동
2. 사이드바에서 `test` 네임스페이스 확인
3. "New Record" 버튼 클릭
4. RecordForm에서:
   - Namespace: `test`
   - Set: `users`
   - Key: `user1`
   - Bin 추가: name=`name`, value=`Alice`
   - Bin 추가: name=`age`, value=`25`
5. "Save" 또는 "Create" 버튼 클릭
6. **검증**: 레코드가 테이블에 표시됨
7. 스크린샷 캡처

---

## Step 5: 레코드 브라우징 및 상세 조회

1. 사이드바에서 `test` > `users` set 클릭
2. **검증**: RecordTable에 레코드 표시
3. 레코드 행 클릭 → RecordDetail 패널 확인 (PK, Gen, TTL, Bins)
4. "New Record" 버튼 → 새 레코드 추가:
   - Key: `user2`
   - Bin: name=`Bob`, age=`30`
5. **검증**: 레코드 수 증가 확인
6. 스크린샷 캡처

---

## Step 6: 레코드 삭제

1. 레코드 테이블에서 특정 레코드의 삭제 아이콘/버튼 클릭
2. 확인 다이얼로그가 있으면 "Delete" 클릭
3. **검증**: 해당 레코드 사라짐, toast "Record deleted" 표시
4. 스크린샷 캡처

---

## Step 7: Secondary Index 관리

1. 탭 바에서 "Indexes" 텍스트 클릭하여 Indexes 페이지로 이동
2. 네임스페이스 `test` 선택
3. 인덱스 생성 버튼 클릭
4. 인덱스 폼 입력:
   - Name: `idx_age`
   - Set: `users`
   - Bin: `age`
   - Type: `numeric`
5. Create/Save 클릭
6. **검증**: 인덱스가 목록에 표시
7. 인덱스 삭제 아이콘 클릭 → 확인 다이얼로그 → "Delete" 클릭
8. **검증**: 인덱스 사라짐
9. 스크린샷 캡처

---

## Step 8: Metrics 대시보드 확인

1. 탭 바에서 "Metrics" 텍스트 클릭하여 Metrics 페이지로 이동
2. **검증**: 실시간 메트릭 대시보드 로딩
3. 차트 (Read/Write TPS, Connections 등) 표시 확인
4. 스크린샷 캡처

---

## Step 9: 연결 삭제 (Cleanup)

1. 사이드바 또는 로고/홈 클릭하여 Connections 페이지(/)로 이동
2. 연결 카드의 `...` (더보기) 버튼 클릭하여 드롭다운 메뉴 열기
3. "Delete" 메뉴 항목 클릭
4. AlertDialog에서 "Delete" 확인 버튼 클릭
5. **검증**: EmptyState 화면 복원, 연결 카드 없음
6. 스크린샷 캡처
