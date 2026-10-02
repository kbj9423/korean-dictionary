# 끝말잇기 낱말 사전 (korean-dictionary)

초2 아이용 끝말잇기 학습 사전. 정적 사이트(`index.html` + `words.json`)를 GitHub Pages로 공개.
- 원격: https://github.com/kbj9423/korean-dictionary (브랜치 `main`, 공개 저장소)
- 사이트: https://kbj9423.github.io/korean-dictionary/
- 데이터 생성: `python scripts/build_words.py` (필요: `openpyxl`, 프로젝트 루트 `.env`의 `KRDICT_API_KEY`). `data/krdict/*.xml`(한국어기초사전 전체 내려받기, git 제외)이 있으면 API 대신 XML에서 뜻을 찾는다.

## 멀티 PC 작업 규칙
- 집/사무실 PC를 번갈아 작업한다. 코드 수정 전 `git fetch` → `git log HEAD..origin/main --oneline`으로 뒤처졌는지 확인하고, 뒤처졌으면 먼저 `git pull`.
- 커밋 안 된 로컬 변경이 있는 상태에서 pull이 필요하면 사용자에게 먼저 알린다.
- 세션 초반에 최근 작업을 어느 PC에서 했는지 가볍게 확인한다.
- 작업이 끝나면 add → commit → push까지 마친다.
- `.env`(API 키)는 공개 저장소라 절대 커밋하지 않는다. PC마다 직접 만든다.
- 한국어기초사전 API는 짧은 시간에 50개 남짓만 요청해도 IP가 2시간 넘게 차단된다(2026-10-02~03 확인). 대량 조회는 API 대신 전체 내려받기 XML을 쓴다.

## 인계사항 (다음 PC 확인용)
2026-10-03 기준
- [x] 쉬운 뜻 교체 완료: 전체 XML로 14,083개 중 12,693개를 기초사전 뜻으로 교체, 나머지 1,390개(대부분 어려움)는 기초사전에 없어 표준국어대사전 첫 뜻 유지. 사용자 확인 후 이 섹션 삭제.
