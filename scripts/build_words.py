"""국어 기초 어휘 목록(1~4등급)에서 명사를 골라 한국어기초사전 뜻을 붙여 words.json을 만든다.

사용법: python scripts/build_words.py
- API 키는 프로젝트 루트 .env 의 KRDICT_API_KEY 에서 읽는다.
- API 응답은 data/cache/krdict.json 에 저장되어, 중간에 멈춰도 다시 실행하면 이어서 진행한다.
"""
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "data/raw/basic_vocab.xlsx"
CACHE = ROOT / "data/cache/krdict.json"
OUT = ROOT / "words.json"
GRADES = 4
API = "https://krdict.korean.go.kr/api/search"
XML_DIR = ROOT / "data/krdict"  # 한국어기초사전 '사전 전체 내려받기' XML (있으면 API 대신 사용)
LEVELS = [("중간", {3}), ("쉬움", {1, 2}), ("어려움", {4})]
# 실패 시 기다릴 시간(초). 서버 차단이 풀릴 때까지 몇 시간 동안 다시 시도한다.
WAITS = [60, 300, 900] + [1800] * 12


def load_key():
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("KRDICT_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit(".env 에 KRDICT_API_KEY 가 없습니다.")


def first_sense(text):
    """표준국어대사전 뜻풀이에서 첫 번째 뜻만 꺼낸다. 예: '[Ⅰ]「1」집안 식구.\n「2」…' → '집안 식구.'"""
    line = (text or "").strip().split("\n")[0]
    return re.sub(r"^(\[[^\]]*\]|「[^」]*」)+", "", line).strip()


def load_words():
    """등급 시트 1~4에서 두 글자 이상 순한글 명사를 고른다. 같은 단어는 가장 쉬운 등급만 남긴다."""
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    words = {}
    for ws in wb.worksheets[:GRADES]:
        for row in list(ws.iter_rows(values_only=True))[1:]:
            grade, word, _, pos, _, origin, meaning = row[:7]
            word = str(word or "").strip()
            if "명사" not in str(pos or "").split("/") or not re.fullmatch(r"[가-힣]{2,}", word):
                continue
            g = int(re.sub(r"\D", "", str(grade)))
            if word not in words:
                words[word] = {"grade": g, "origin": (origin or "").strip(), "std": first_sense(meaning)}
    return words


def fetch(key, word):
    """기초사전에서 명사로 정확히 일치하는 항목을 [(원어, 첫 뜻)] 목록으로 돌려준다."""
    q = urllib.parse.urlencode({"key": key, "q": word, "part": "word", "num": 10,
                                "advanced": "y", "method": "exact", "pos": 1})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": "Mozilla/5.0"})
    root = ET.fromstring(urllib.request.urlopen(req, timeout=20).read())
    if root.tag == "error":
        raise RuntimeError(f"API 오류: {root.findtext('error_code')} {root.findtext('message')}")
    return [[(it.findtext("origin") or "").strip(), (it.findtext("sense/definition") or "").strip()]
            for it in root.iter("item") if it.findtext("word") == word]


def load_xml(words):
    """한국어기초사전 '사전 전체 내려받기' XML에서 명사 항목을 단어별 [(원어, 첫 뜻)]으로 모은다."""
    found = {w: [] for w in words}
    for path in sorted(XML_DIR.glob("*.xml")):
        # 원본 일부 번역 문장에 XML에서 허용하지 않는 제어 문자가 섞여 있어 지우고 읽는다.
        data = re.sub(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]", b"", path.read_bytes())
        for _, el in ET.iterparse(io.BytesIO(data)):
            if el.tag != "LexicalEntry":
                continue
            feat = {f.get("att"): f.get("val") for f in el.findall("feat")}
            lemma = el.find("Lemma/feat[@att='writtenForm']")
            word = lemma.get("val") if lemma is not None else ""
            if word in found and feat.get("partOfSpeech") == "명사":
                d = el.find("Sense/feat[@att='definition']")  # Sense 바로 아래 뜻만 (외국어 번역 뜻 제외)
                found[word].append((int(feat.get("homonym_number") or 0), feat.get("origin") or "",
                                    d.get("val").strip() if d is not None else ""))
            el.clear()
    return {w: [[o, d] for _, o, d in sorted(items)] for w, items in found.items()}


def pick(items, origin):
    """원어(한자)가 같은 항목을 우선 고르고, 없으면 첫 항목을 쓴다."""
    for o, d in items:
        if o == origin and d:
            return d
    return items[0][1] if items else ""


def save(words, cache):
    """조회 결과를 저장하고, 기초사전 뜻이 있으면 그 뜻을, 없으면 표준국어대사전 뜻을 넣어 words.json을 만든다."""
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    out, basic = [], 0
    for w in sorted(words):
        info = words[w]
        meaning = pick(cache.get(w, []), info["origin"])
        basic += bool(meaning)
        out.append([w, info["grade"], meaning or info["std"]])
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return basic


def main():
    key = load_key()
    words = load_words()
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    if any(XML_DIR.glob("*.xml")):
        print("data/krdict 의 한국어기초사전 전체 XML에서 뜻을 찾습니다.", flush=True)
        for w, items in load_xml(words).items():
            cache.setdefault(w, items)
    print(f"단어 {len(words)}개, 새로 조회할 단어 {sum(w not in cache for w in words)}개", flush=True)

    # 동시에 여러 번 요청하면 서버가 접속을 막으므로, 하나씩 쉬어 가며 요청하고 실패하면 기다렸다 다시 시도한다.
    # 난이도 순서: 중간 → 쉬움 → 어려움. 난이도 하나가 끝날 때마다 words.json을 갱신한다.
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    try:
        for name, grades in LEVELS:
            todo = [w for w in words if words[w]["grade"] in grades and w not in cache]
            print(f"[{name}] 새로 조회할 단어 {len(todo)}개", flush=True)
            for i, w in enumerate(todo, 1):
                for wait in WAITS:
                    try:
                        cache[w] = fetch(key, w)
                        break
                    except (OSError, ET.ParseError) as e:
                        print(f"  '{w}' 실패({e}), {wait}초 뒤 다시 시도", flush=True)
                        time.sleep(wait)
                else:
                    sys.exit("서버가 계속 응답하지 않아 멈춥니다. 나중에 다시 실행하면 이어서 진행합니다.")
                time.sleep(1)
                if i % 100 == 0:
                    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
                    print(f"  [{name}] {i}/{len(todo)}", flush=True)
            print(f"[{name}] 완료: 전체 기초사전 뜻 {save(words, cache)}개", flush=True)
    finally:
        basic = save(words, cache)
    print(f"완료: {len(words)}개 저장 (기초사전 뜻 {basic}개, 표준국어대사전 뜻 {len(words) - basic}개)")


if __name__ == "__main__":
    main()
