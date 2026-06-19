from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.brain_engine import BrainFirstEngine

ENGINE = BrainFirstEngine(ROOT / "brain")
TESTS = json.loads((ROOT / "brain" / "09_test_questions.json").read_text(encoding="utf-8-sig"))["tests"]
REQUIRED_SMOKE_QUESTIONS = [
    "2026년 변경사항",
    "2026년에 출결 특기사항 뭐가 바뀜?",
    "1,2학년이랑 3학년 생기부 차이",
    "졸업에 필요한 학점을 못 채우면 유급인가요?",
    "창체나 행특 누가기록은 교육청 기준으로 똑같이 운영되나요?",
    "세특 문장 하나 써줘",
]


def main() -> int:
    question_to_test = {test["question"]: test for test in TESTS}
    missing_questions = [question for question in REQUIRED_SMOKE_QUESTIONS if question not in question_to_test]
    if missing_questions:
        print(
            json.dumps(
                {
                    "overallPassed": False,
                    "error": "09_test_questions.json에 필수 smoke test 질문이 없습니다.",
                    "missingQuestions": missing_questions,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    results = []
    overall_passed = True

    for question in REQUIRED_SMOKE_QUESTIONS:
        test = question_to_test[question]
        result = ENGINE.answer_question(question)
        used_card_ids = set(result["usedChangeCards"]) | set(result["usedRuleCards"]) | set(result["usedQaCards"])
        matched_expected_cards = [card_id for card_id in test["shouldUseCards"] if card_id in used_card_ids]
        missing_expected_cards = [card_id for card_id in test["shouldUseCards"] if card_id not in used_card_ids]
        quality_passed = (
            bool(result["usedChangeCards"])
            and bool(result["usedRuleCards"])
            and bool(result["usedQaCards"])
            and result["detectedPolicyId"] == test["expectedPolicyId"]
            and bool(matched_expected_cards)
            and result["qualityPassed"]
        )
        overall_passed = overall_passed and quality_passed

        results.append(
            {
                "testId": test["testId"],
                "question": question,
                "expectedPolicyId": test["expectedPolicyId"],
                "detectedPolicyId": result["detectedPolicyId"],
                "detectedTopicIds": result["detectedTopicIds"],
                "usedChangeCards": result["usedChangeCards"],
                "usedRuleCards": result["usedRuleCards"],
                "usedQaCards": result["usedQaCards"],
                "matchedExpectedCards": matched_expected_cards,
                "missingExpectedCards": missing_expected_cards,
                "officialSourceRefs": result["officialSourceRefs"],
                "finalAnswer": result["finalAnswer"],
                "qualityPassed": quality_passed,
            }
        )

    print(json.dumps({"results": results, "overallPassed": overall_passed}, ensure_ascii=False, indent=2))
    return 0 if overall_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
