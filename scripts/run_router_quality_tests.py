from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.brain_engine import BrainFirstEngine

ENGINE = BrainFirstEngine(ROOT / "brain")

QUESTIONS = [
    "학생의 단점을 써도 돼?",
    "행특에 학생의 부정적인 행동을 적어도 되나요?",
    "수업태도가 안 좋은 학생이라고 써도 되나요?",
    "학생의 약점을 생기부에 적어도 되나요?",
    "학생이 게으르다고 행특에 써도 돼?",
    "친구랑 자주 다툰다고 적어도 돼?",
    "수업 중 잠을 자는 학생이라고 써도 돼?",
    "소극적인 학생이라고 써도 돼?",
    "발표를 잘 안 하는 학생이라고 써도 돼?",
    "비협조적이라고 적어도 되나요?",
]

REQUIRED_GROUPS = {
    "조건부 가능": ["조건부 가능"],
    "단순한 단점 나열은 부적절": ["단순한 단점 나열은 부적절", "학생의 단점만 나열하는 방식은 피해야"],
    "낙인찍는 표현은 부적절": ["낙인 표현도 쓰면 안 됩니다", "낙인찍거나 비난하는 표현", "학생을 깎아내리는 표현"],
    "관찰 근거 필요": ["구체적 관찰 근거", "관찰 근거", "지속적으로 관찰"],
    "학생의 성장 정도와 발전 가능성": ["학생의 성장 정도와 발전 가능성", "성장 정도와 발전 가능성", "발전 가능성"],
    "교육적 관점에서 작성": ["교육적 관점", "학생의 성장을 지원하는 교육적 관점"],
    "부정적 행동특성은 구체적 누가기록을 바탕으로 작성 권장": ["구체적 누가기록 권장", "누가기록", "구체적인 누가기록"],
    "행동특성 및 종합의견 관련 근거 페이지 표시": ["공식 기재요령: 인쇄 158", "공식 기재요령: 인쇄 159"],
}


def includes_any(text: str, candidates: list[str]) -> bool:
    return any(candidate in text for candidate in candidates)


def classify_fix(result: dict[str, Any], fail_reason: str) -> str:
    if result["detectedPolicyId"] != "recordability":
        return "router 규칙 수정"
    if "behavior" not in result["detectedTopicIds"]:
        return "synonym 추가"
    if "rule_behavior_negative_traits_educational_perspective" not in result["usedRuleCards"]:
        return "router 규칙 수정"
    if "qa_behavior_can_record_student_weakness" not in result["usedQaCards"]:
        return "qa card 추가"
    return "router 규칙 수정"


def main() -> int:
    results: list[dict[str, Any]] = []
    failed_rows: list[dict[str, Any]] = []

    for question in QUESTIONS:
        result = ENGINE.answer_question(question)
        answer = result["finalAnswer"]
        answer_first_line = result["sections"]["conclusion"]

        failures: list[str] = []
        if result["detectedPolicyId"] != "recordability":
            failures.append("detectedPolicyId가 recordability가 아님")
        if result["detectedTopicIds"] != ["behavior"]:
            failures.append("detectedTopicIds가 ['behavior']가 아님")
        if "rule_behavior_negative_traits_educational_perspective" not in result["usedRuleCards"]:
            failures.append("behavior rule card를 사용하지 않음")
        if not result["usedRuleCards"]:
            failures.append("usedRuleCards가 비어 있음")
        if result["usedChangeCards"] and not result["usedRuleCards"]:
            failures.append("change card만 사용하고 rule card를 사용하지 않음")
        if not answer_first_line.startswith("조건부 가능"):
            failures.append("답변 첫 줄이 조건부 가능으로 시작하지 않음")
        if not result["officialSourceRefs"]:
            failures.append("공식 참고 페이지가 없음")

        for label, candidates in REQUIRED_GROUPS.items():
            if not includes_any(answer, candidates):
                failures.append(f"필수 내용 누락: {label}")

        passed = not failures
        fail_reason = "; ".join(failures)

        row = {
            "question": question,
            "detectedPolicyId": result["detectedPolicyId"],
            "detectedTopicIds": result["detectedTopicIds"],
            "usedChangeCards": result["usedChangeCards"],
            "usedRuleCards": result["usedRuleCards"],
            "usedQaCards": result["usedQaCards"],
            "answerFirstLine": answer_first_line,
            "answer": answer,
            "pass": passed,
            "failReason": fail_reason,
        }
        results.append(row)

        if not passed:
            failed_rows.append(
                {
                    "question": question,
                    "expectedPolicyId": "recordability",
                    "actualPolicyId": result["detectedPolicyId"],
                    "expectedTopicIds": ["behavior"],
                    "actualTopicIds": result["detectedTopicIds"],
                    "usedChangeCards": result["usedChangeCards"],
                    "usedRuleCards": result["usedRuleCards"],
                    "usedQaCards": result["usedQaCards"],
                    "failReason": fail_reason,
                    "suggestedFix": classify_fix(result, fail_reason),
                }
            )

    failed_path = ROOT / "failed_questions.jsonl"
    failed_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in failed_rows) + ("\n" if failed_rows else ""),
        encoding="utf-8",
    )

    summary = {
        "totalTests": len(results),
        "passCount": sum(1 for row in results if row["pass"]),
        "failCount": sum(1 for row in results if not row["pass"]),
        "failedQuestions": [row["question"] for row in results if not row["pass"]],
        "failureCauseCategories": dict(Counter(reason for row in results if not row["pass"] for reason in row["failReason"].split("; ") if reason)),
        "failedQuestionsPath": str(failed_path),
    }

    report_path = ROOT / "router_quality_test_results.json"
    report_path.write_text(json.dumps({"results": results, "summary": summary}, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"results": results, "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if summary["failCount"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
