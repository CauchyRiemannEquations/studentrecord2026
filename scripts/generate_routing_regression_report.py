from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.brain_engine import BrainFirstEngine, printed_to_pdf
from scripts.run_regression_tests import includes_meaning

REPORT_DIR = ROOT / "reports"
REPORT_MD = REPORT_DIR / "routing_regression_report.md"
REPORT_JSON = REPORT_DIR / "routing_regression_results.json"
FAILED_JSONL = ROOT / "failed_questions.jsonl"
TEST_PATH = ROOT / "brain" / "09_test_questions.json"
ENGINE_PATH = ROOT / "app" / "brain_engine.py"

CHANGE_HINTS = ("2026", "개정사항", "변경사항", "달라진 점", "바뀜", "2025 대비")
RECORDABILITY_PREFIXES = (
    "가능",
    "불가",
    "조건부 가능",
    "학교 기준 확인 필요",
    "자료상 확인 불가",
)
PAGE_LOOKUP_PREFIXES = (
    "공식 기재요령 기준으로는 p.",
    "길라잡이 Q&A 기준으로는 p.",
)


def load_tests() -> list[dict[str, Any]]:
    return json.loads(TEST_PATH.read_text(encoding="utf-8-sig"))["tests"]


def joined_answer_text(result: dict[str, Any]) -> str:
    sections = result["sections"]
    return " ".join(
        [
            sections["conclusion"],
            *sections["coreSummary"],
            *sections["gradeDifferences"],
            *sections["practicalNotes"],
            result["finalAnswer"],
        ]
    )


def public_source_refs_for_result(engine: BrainFirstEngine, result: dict[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    all_cards: list[dict[str, Any]] = []

    for card_id in result["usedChangeCards"]:
        all_cards.append(engine.change_by_id[card_id])
    for card_id in result["usedRuleCards"]:
        all_cards.append(engine.rule_by_id[card_id])
    for card_id in result["usedQaCards"]:
        all_cards.append(engine.qa_by_id[card_id])

    for card in all_cards:
        for source_ref in card.get("sourceRefs", []):
            doc_id = source_ref.get("docId")
            printed_page = source_ref.get("printedPage")
            if doc_id not in {"official_guidelines_2026_hs", "guide_2026_hs"} or printed_page is None:
                continue
            key = (doc_id, str(printed_page))
            if key in seen:
                continue
            seen.add(key)
            refs.append(
                {
                    "docId": doc_id,
                    "printedPage": str(printed_page),
                    "pdfPage": printed_to_pdf(doc_id, printed_page),
                }
            )
    return refs


def has_change_trigger(question: str) -> bool:
    return any(trigger in question for trigger in CHANGE_HINTS)


def first_line_is_valid(policy_id: str, first_line: str) -> bool:
    if policy_id == "recordability":
        return any(first_line.startswith(prefix) for prefix in RECORDABILITY_PREFIXES)
    if policy_id == "page_lookup":
        return any(first_line.startswith(prefix) for prefix in PAGE_LOOKUP_PREFIXES)
    return True


def compare_page_refs(result: dict[str, Any], engine: BrainFirstEngine) -> list[str]:
    errors: list[str] = []
    expected_refs = public_source_refs_for_result(engine, result)
    expected_pairs = {(ref["docId"], ref["printedPage"]): ref for ref in expected_refs}

    if not result["usedPageRefs"]:
        errors.append("sourceRefs 없는 답변")
        return errors

    for ref in result["usedPageRefs"]:
        key = (ref.get("docId", ""), ref.get("printedPage", ""))
        if key not in expected_pairs:
            errors.append(f"표시된 참고 페이지가 사용 카드 sourceRefs와 불일치: {key[0]} {key[1]}")
            continue
        expected_pdf = expected_pairs[key]["pdfPage"]
        if ref.get("pdfPage", "") != expected_pdf:
            errors.append(
                f"PDF 화면상 페이지 불일치: {key[0]} {key[1]} (actual={ref.get('pdfPage', '')}, expected={expected_pdf})"
            )
    return errors


def suggest_fix(
    test: dict[str, Any],
    result: dict[str, Any],
    reasons: list[str],
    engine: BrainFirstEngine,
) -> str:
    if any("expectedPolicyId" in reason for reason in reasons):
        return "router 수정"
    if any("expectedTopicIds" in reason for reason in reasons):
        return "alias 추가"
    if any("usedPageRefs" in reason or "sourceRefs 없는 답변" in reason for reason in reasons):
        return "page map 수정"
    if any("answerFirstLine" in reason for reason in reasons):
        return "answer template 수정"

    missing_cards = [
        card_id
        for card_id in test.get("shouldUseCards", [])
        if card_id
        not in set(result["usedChangeCards"]) | set(result["usedRuleCards"]) | set(result["usedQaCards"])
    ]
    if missing_cards:
        if any(card_id.startswith("rule_") and card_id not in engine.rule_by_id for card_id in missing_cards):
            return "rule card 추가"
        if any(card_id.startswith("qa_") and card_id not in engine.qa_by_id for card_id in missing_cards):
            return "qa card 추가"
        return "router 수정"

    return "answer template 수정"


def validate_result(
    test: dict[str, Any],
    result: dict[str, Any],
    engine: BrainFirstEngine,
) -> tuple[bool, list[str], list[str]]:
    reasons: list[str] = []
    joined_text = joined_answer_text(result)

    if result["detectedPolicyId"] != test["expectedPolicyId"]:
        reasons.append(
            f"expectedPolicyId mismatch: expected={test['expectedPolicyId']} actual={result['detectedPolicyId']}"
        )

    topic_hits = [topic_id for topic_id in test["expectedTopicIds"] if topic_id in result["detectedTopicIds"]]
    if not topic_hits:
        reasons.append(
            f"expectedTopicIds mismatch: expected one of {test['expectedTopicIds']} actual={result['detectedTopicIds']}"
        )

    used_card_ids = set(result["usedChangeCards"]) | set(result["usedRuleCards"]) | set(result["usedQaCards"])
    expected_cards = test.get("shouldUseCards", [])
    matched_cards = [card_id for card_id in expected_cards if card_id in used_card_ids]
    if expected_cards and not matched_cards:
        reasons.append(f"no matched shouldUseCards: {expected_cards}")

    missing_mentions = [
        phrase
        for phrase in test.get("mustMention", [])
        if not includes_meaning(joined_text, phrase)
    ]
    if missing_mentions:
        reasons.append(f"missing mustMention: {missing_mentions}")

    answer_first_line = result["sections"]["conclusion"]
    if not first_line_is_valid(test["expectedPolicyId"], answer_first_line):
        reasons.append(f"answerFirstLine invalid for {test['expectedPolicyId']}: {answer_first_line}")

    if test["expectedPolicyId"] == "recordability" and not (result["usedRuleCards"] or result["usedQaCards"]):
        reasons.append("usedRuleCards/usedQaCards missing for recordability")
    if test["expectedPolicyId"] == "page_lookup" and not result["usedPageRefs"]:
        reasons.append("usedPageRefs missing for page_lookup")

    if (
        test["expectedPolicyId"] != "change_2026"
        and not has_change_trigger(test["question"])
        and result["usedChangeCards"]
        and not (result["usedRuleCards"] or result["usedQaCards"])
    ):
        reasons.append("change card only answer on non-change question")

    page_errors = compare_page_refs(result, engine)
    reasons.extend(page_errors)
    return (not reasons, reasons, page_errors)


def audit_hardcoding(engine_text: str, tests: list[dict[str, Any]]) -> dict[str, Any]:
    banned_pattern_specs = {
        "question_equality": r"\bif\s+(question|question_text)\s*==",
        "question_vs_test_data": r"==\s*test\[",
        "shouldUseCards_reference": r"\bshouldUseCards\b",
        "mustMention_reference": r"\bmustMention\b",
    }
    banned_hits = [
        {"name": name, "pattern": pattern}
        for name, pattern in banned_pattern_specs.items()
        if re.search(pattern, engine_text)
    ]
    exact_question_hits = [test["question"] for test in tests if test["question"] in engine_text]
    dormant_anchor_placeholder = "anchor_test" in engine_text

    return {
        "hardcodingSuspected": bool(banned_hits or exact_question_hits),
        "bannedPatternHits": banned_hits,
        "exactQuestionHits": exact_question_hits,
        "dormantAnchorPlaceholder": dormant_anchor_placeholder,
        "notes": [
            "Exact test question strings were scanned in app/brain_engine.py.",
            "Test-only fields like shouldUseCards and mustMention were scanned in app/brain_engine.py.",
            "Semantic category detectors remain allowed because they operate on aliases, intents, and card keywords rather than full test sentences.",
        ],
    }


def write_failed_questions(entries: list[dict[str, Any]]) -> None:
    if not entries:
        FAILED_JSONL.write_text("", encoding="utf-8")
        return
    FAILED_JSONL.write_text(
        "\n".join(json.dumps(entry, ensure_ascii=False) for entry in entries) + "\n",
        encoding="utf-8",
    )


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    audit = report["hardcodingAudit"]
    lines = [
        "# Routing Regression Report",
        "",
        f"- generatedAt: {report['generatedAt']}",
        f"- existingRegressionPassed: {summary['existingRegressionPassed']}/{summary['existingRegressionTotal']}",
        f"- paraphrasePassed: {summary['paraphrasePassed']}/{summary['paraphraseTotal']}",
        f"- overallPassed: {summary['overallPassed']}/{summary['overallTotal']}",
        f"- failedCount: {summary['failedCount']}",
        "",
        "## Hardcoding Audit",
        "",
        f"- hardcodingSuspected: {audit['hardcodingSuspected']}",
        f"- exactQuestionHitCount: {len(audit['exactQuestionHits'])}",
        f"- bannedPatternHitCount: {len(audit['bannedPatternHits'])}",
        f"- dormantAnchorPlaceholder: {audit['dormantAnchorPlaceholder']}",
        "",
        "## Page Reference Validation",
        "",
        f"- passed: {summary['pageReferenceValidation']['passed']}",
        f"- failed: {summary['pageReferenceValidation']['failed']}",
        "",
        "## Test Details",
        "",
    ]

    for item in report["tests"]:
        lines.extend(
            [
                f"### {item['testId']} {item['question']}",
                "",
                f"- detectedPolicyId: {item['detectedPolicyId']}",
                f"- detectedTopicIds: {json.dumps(item['detectedTopicIds'], ensure_ascii=False)}",
                f"- normalizedQuery: `{item['normalizedQuery']}`",
                f"- matchedAliases: `{json.dumps(item['matchedAliases'], ensure_ascii=False)}`",
                f"- usedChangeCards: `{json.dumps(item['usedChangeCards'], ensure_ascii=False)}`",
                f"- usedRuleCards: `{json.dumps(item['usedRuleCards'], ensure_ascii=False)}`",
                f"- usedQaCards: `{json.dumps(item['usedQaCards'], ensure_ascii=False)}`",
                f"- usedPageRefs: `{json.dumps(item['usedPageRefs'], ensure_ascii=False)}`",
                f"- answerFirstLine: {item['answerFirstLine']}",
                f"- result: {'pass' if item['pass'] else 'fail'}",
                f"- failReason: {item['failReason'] or '-'}",
                "",
                "```text",
                item["fullAnswer"],
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    engine = BrainFirstEngine(ROOT / "brain")
    tests = load_tests()
    engine_text = ENGINE_PATH.read_text(encoding="utf-8")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    test_results: list[dict[str, Any]] = []
    failed_entries: list[dict[str, Any]] = []
    failure_counter: Counter[str] = Counter()
    page_ref_passed = 0
    page_ref_failed = 0
    page_ref_failed_tests: list[str] = []

    existing_total = 0
    existing_passed = 0
    paraphrase_total = 0
    paraphrase_passed = 0

    for test in tests:
        result = engine.answer_question(test["question"])
        passed, reasons, page_errors = validate_result(test, result, engine)
        test_number = int(test["testId"][1:])
        if test_number <= 36:
            existing_total += 1
            if passed:
                existing_passed += 1
        else:
            paraphrase_total += 1
            if passed:
                paraphrase_passed += 1

        if page_errors:
            page_ref_failed += 1
            page_ref_failed_tests.append(test["testId"])
        else:
            page_ref_passed += 1

        answer_first_line = result["sections"]["conclusion"]
        fail_reason = "; ".join(reasons)
        test_results.append(
            {
                "testId": test["testId"],
                "question": test["question"],
                "expectedPolicyId": test["expectedPolicyId"],
                "detectedPolicyId": result["detectedPolicyId"],
                "expectedTopicIds": test["expectedTopicIds"],
                "detectedTopicIds": result["detectedTopicIds"],
                "normalizedQuery": result["normalizedQuery"],
                "matchedAliases": result["matchedAliases"],
                "usedChangeCards": result["usedChangeCards"],
                "usedRuleCards": result["usedRuleCards"],
                "usedQaCards": result["usedQaCards"],
                "usedPageRefs": result["usedPageRefs"],
                "answerFirstLine": answer_first_line,
                "fullAnswer": result["finalAnswer"],
                "pass": passed,
                "failReason": fail_reason,
            }
        )

        if not passed:
            suggestion = suggest_fix(test, result, reasons, engine)
            failure_counter[suggestion] += 1
            failed_entries.append(
                {
                    "question": test["question"],
                    "expectedPolicyId": test["expectedPolicyId"],
                    "actualPolicyId": result["detectedPolicyId"],
                    "expectedTopicIds": test["expectedTopicIds"],
                    "actualTopicIds": result["detectedTopicIds"],
                    "usedChangeCards": result["usedChangeCards"],
                    "usedRuleCards": result["usedRuleCards"],
                    "usedQaCards": result["usedQaCards"],
                    "usedPageRefs": result["usedPageRefs"],
                    "failReason": fail_reason,
                    "suggestedFix": suggestion,
                }
            )

    write_failed_questions(failed_entries)

    audit = audit_hardcoding(engine_text, tests)
    summary = {
        "existingRegressionTotal": existing_total,
        "existingRegressionPassed": existing_passed,
        "paraphraseTotal": paraphrase_total,
        "paraphrasePassed": paraphrase_passed,
        "overallTotal": len(tests),
        "overallPassed": sum(1 for item in test_results if item["pass"]),
        "failedCount": len(failed_entries),
        "failedQuestions": [entry["question"] for entry in failed_entries],
        "failureReasons": dict(failure_counter),
        "pageReferenceValidation": {
            "passed": page_ref_passed,
            "failed": page_ref_failed,
            "failedTests": page_ref_failed_tests,
        },
    }
    report = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "summary": summary,
        "hardcodingAudit": audit,
        "tests": test_results,
    }

    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")

    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(json.dumps(report["hardcodingAudit"], ensure_ascii=False, indent=2))
    return 0 if not failed_entries else 1


if __name__ == "__main__":
    raise SystemExit(main())
