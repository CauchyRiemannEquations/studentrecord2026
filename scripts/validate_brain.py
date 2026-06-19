from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRAIN_DIR = ROOT / "brain"

OFFICIAL = "official_guidelines_2026_hs"

CHANGE_FILE = BRAIN_DIR / "04_change_2026_catalog.jsonl"
RULE_FILE = BRAIN_DIR / "05_rule_cards.jsonl"
QA_FILE = BRAIN_DIR / "06_qa_cards.jsonl"
TEST_FILE = BRAIN_DIR / "09_test_questions.json"

FORBIDDEN_BROKEN_STRINGS = [
    "년 3월 1일 : 고등학교",
    "고등학교 2학년 3.",
    "일련 번호, 정정 연월일",
    "2024.06.07",
]

FORBIDDEN_WRONG_PHRASES = [
    "학교장 중심에서 시도교육감",
    "유급 정의가 진급 불가뿐 아니라 졸업 요건 미충족까지 포괄",
    "실제 수업 횟수 기준으로 변경",
    "실제 운영한 수업 횟수의 3분의 2",
]

REQUIRED_RULE_IDS = [
    "rule_no_direct_ai_generated_text",
    "rule_accumulation_decided_by_principal",
    "rule_awards_must_follow_school_plan",
    "rule_subject_attendance_rate_16_sessions",
    "rule_small_class_rank_marker_by_grade",
    "rule_volunteer_curricular_link_grades_1_2",
    "rule_performance_assessment_ai_caution",
    "rule_correction_swapped_items_committee",
    "rule_school_sports_club_name_only",
    "rule_reading_same_book_different_evidence",
    "rule_certificate_only_designated_scope",
    "rule_behavior_300_chars",
    "rule_career_activity_500_chars",
    "rule_volunteer_content_50_chars",
    "rule_subject_notes_special_none",
    "rule_online_content_remark",
    "rule_regular_exam_term",
    "rule_grade_1_2_credit_5_grade",
    "rule_grade_3_unit_9_grade",
    "rule_retention_vs_graduation_deferral",
]

REQUIRED_TEST_QUESTIONS = [
    "2026년 변경사항",
    "2026년에 출결 특기사항 뭐가 바뀜?",
    "1,2학년이랑 3학년 생기부 차이",
    "졸업에 필요한 학점을 못 채우면 유급인가요?",
    "창체나 행특 누가기록은 교육청 기준으로 똑같이 운영되나요?",
    "수행평가에서 생성형 AI 사용을 허용해도 되나요?",
    "정규교육과정 이외 학교스포츠클럽은 시간과 특기사항도 적나요?",
    "세특 문장 하나 써줘",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def load_json(path: Path) -> tuple[dict | None, list[str]]:
    try:
        return json.loads(read_text(path)), []
    except json.JSONDecodeError as exc:
        return None, [f"{path.name}: JSON parse error at line {exc.lineno}, column {exc.colno}: {exc.msg}"]


def load_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    for line_no, raw_line in enumerate(read_text(path).splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{line_no}: JSONL parse error at column {exc.colno}: {exc.msg}")
    return records, errors


def has_official_ref(card: dict) -> bool:
    return any(source.get("docId") == OFFICIAL for source in card.get("sourceRefs", []))


def scan_top_level_brain_files() -> str:
    chunks: list[str] = []
    for path in sorted(BRAIN_DIR.glob("0*.json*")):
        if path.is_file():
            chunks.append(read_text(path))
    return "\n".join(chunks)


def collect_missing_required_fields(records: list[dict], id_field: str, required_fields: list[str]) -> list[str]:
    missing: list[str] = []
    for record in records:
        record_id = record.get(id_field, "<missing-id>")
        for field in required_fields:
            value = record.get(field)
            if value in (None, "", []):
                missing.append(f"{record_id}:{field}")
    return missing


def main() -> int:
    failures: list[str] = []

    changes, change_errors = load_jsonl(CHANGE_FILE)
    rules, rule_errors = load_jsonl(RULE_FILE)
    qas, qa_errors = load_jsonl(QA_FILE)
    tests_doc, test_errors = load_json(TEST_FILE)

    failures.extend(change_errors)
    failures.extend(rule_errors)
    failures.extend(qa_errors)
    failures.extend(test_errors)

    tests = tests_doc.get("tests", []) if tests_doc else []

    if len(changes) < 31:
        failures.append(f"04_change_2026_catalog.jsonl count is {len(changes)} but must be at least 31")
    if len(rules) < 35:
        failures.append(f"05_rule_cards.jsonl count is {len(rules)} but must be at least 35")
    if len(qas) < 20:
        failures.append(f"06_qa_cards.jsonl count is {len(qas)} but must be at least 20")
    if len(tests) < 16:
        failures.append(f"09_test_questions.json count is {len(tests)} but must be at least 16")

    missing_change_fields = collect_missing_required_fields(
        changes,
        "changeId",
        ["title", "before2025", "after2026", "practicalMeaning", "sourceRefs"],
    )
    if missing_change_fields:
        failures.append(f"change cards missing required fields: {missing_change_fields}")

    missing_rule_fields = collect_missing_required_fields(rules, "ruleId", ["title", "ruleSummary", "sourceRefs"])
    if missing_rule_fields:
        failures.append(f"rule cards missing required fields: {missing_rule_fields}")

    missing_qa_fields = collect_missing_required_fields(qas, "qaId", ["question", "answer", "sourceRefs"])
    if missing_qa_fields:
        failures.append(f"qa cards missing required fields: {missing_qa_fields}")

    official_missing_change_cards = sorted(card["changeId"] for card in changes if not has_official_ref(card))
    if official_missing_change_cards:
        failures.append(f"change cards without official sourceRef: {official_missing_change_cards}")

    rule_ids = {card["ruleId"] for card in rules}
    missing_required_rule_ids = [rule_id for rule_id in REQUIRED_RULE_IDS if rule_id not in rule_ids]
    if missing_required_rule_ids:
        failures.append(f"missing required rule IDs: {missing_required_rule_ids}")

    existing_ids = {card["changeId"] for card in changes}
    existing_ids.update(rule_ids)
    existing_ids.update(card["qaId"] for card in qas)

    should_use_cards = sorted(
        {
            card_id
            for test in tests
            for card_id in test.get("shouldUseCards", [])
            if isinstance(card_id, str) and card_id
        }
    )
    missing_should_use_cards = [card_id for card_id in should_use_cards if card_id not in existing_ids]
    if missing_should_use_cards:
        failures.append(f"missing shouldUseCards: {missing_should_use_cards}")

    test_questions = [test.get("question", "") for test in tests]
    missing_required_test_questions = [question for question in REQUIRED_TEST_QUESTIONS if question not in test_questions]
    if missing_required_test_questions:
        failures.append(f"missing required test questions: {missing_required_test_questions}")

    brain_text = scan_top_level_brain_files()
    broken_hits = [text for text in FORBIDDEN_BROKEN_STRINGS if text in brain_text]
    wrong_phrase_hits = [text for text in FORBIDDEN_WRONG_PHRASES if text in brain_text]

    for hit in broken_hits:
        failures.append(f'forbidden broken string found: "{hit}"')
    for hit in wrong_phrase_hits:
        failures.append(f'forbidden wrong phrase found: "{hit}"')

    summary = {
        "changeCardCount": len(changes),
        "ruleCardCount": len(rules),
        "qaCardCount": len(qas),
        "testQuestionCount": len(tests),
        "missingShouldUseCards": missing_should_use_cards,
        "officialSourceRefMissingChangeCards": official_missing_change_cards,
        "forbiddenBrokenStringHits": broken_hits,
        "forbiddenWrongPhraseHits": wrong_phrase_hits,
        "failures": failures,
        "validationPassed": not failures,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
