# 끝말잇기 낱말 사전 (korean-dictionary)

초2 아이용 끝말잇기 학습 사전. 정적 사이트(`index.html` + `words.json`)를 GitHub Pages로 공개.
- 원격: https://github.com/kbj9423/korean-dictionary (브랜치 `main`, 공개 저장소)
- 사이트: https://kbj9423.github.io/korean-dictionary/
- 데이터 생성: `python scripts/build_words.py` (필요: `openpyxl`, 프로젝트 루트 `.env`의 `KRDICT_API_KEY`)

## 멀티 PC 작업 규칙
- 집/사무실 PC를 번갈아 작업한다. 코드 수정 전 `git fetch` → `git log HEAD..origin/main --oneline`으로 뒤처졌는지 확인하고, 뒤처졌으면 먼저 `git pull`.
- 커밋 안 된 로컬 변경이 있는 상태에서 pull이 필요하면 사용자에게 먼저 알린다.
- 세션 초반에 최근 작업을 어느 PC에서 했는지 가볍게 확인한다.
- 작업이 끝나면 add → commit → push까지 마친다.
- `.env`(API 키)는 공개 저장소라 절대 커밋하지 않는다. PC마다 직접 만든다.
- 한국어기초사전 API는 동시 요청 시 IP가 차단된 적이 있다(2026-10-02). 반드시 하나씩, 쉬어 가며 요청한다(스크립트에 반영됨).

## 인계사항 (다음 PC 확인용)
2026-10-02 기준
- [ ] 쉬운 뜻 교체: 현재 `words.json`의 뜻은 대부분 표준국어대사전 첫 뜻(14,083개 중 기초사전 뜻 70개). 새 PC에서 `.env`에 `KRDICT_API_KEY=...`를 만들고 `python scripts/build_words.py` 실행 → 끝나면 `words.json`과 `data/cache/krdict.json`을 커밋·push. 조회 결과는 `data/cache/krdict.json`에 쌓여 중간에 멈춰도 이어서 진행됨. 1~2시간 예상.
- [ ] 위 작업 전, 사전 서버(krdict.korean.go.kr)가 열리는지 먼저 확인(2026-10-02 IP 차단 상태였음).
- [ ] 뜻 교체 후 사이트에서 몇 글자 검색해 뜻이 짧고 쉬운지 확인.
