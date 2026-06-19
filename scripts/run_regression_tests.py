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

SYNONYM_GROUPS = [
    ["학교장이 정함", "학교장이 정한다", "학교장이 결정한다", "학교장이 정합니다"],
    ["누가기록 여부 및 방법은 학교장이 정함", "누가기록 여부 및 방법은 학교장이 정한다", "누가기록 여부 및 방법은 학교장이 정합니다", "누가기록 여부 및 방법은 학교장이 정하며"],
    ["학교별 방침 확인", "학교 방침을 확인", "학교별로 달라질 수", "학교 운영 기준 확인이 필요합니다", "학교별 방침이 다를 수 있으므로 학교 운영 기준 확인이 필요합니다"],
    ["전국 공통으로 단정하면 안 됨", "전국 공통 기준처럼 단정하지 말고", "전국 공통으로 단정하면 안 됩니다", "교육청 공통 기준으로 똑같이 운영한다고 단정할 수 없습니다", "전국 공통 기준이나 교육청 공통 기준처럼 단정하면 안 됩니다"],
    ["유급과 졸업유예 구분", "유급과 졸업유예를 구분", "유급과 졸업유예를 같은 말처럼 답하면 안 된다", "유급은 진급 불가 개념으로 정리되고, 졸업 학점 미충족은 졸업유예로 별도 구분됩니다"],
    ["진급 문제인지 졸업 자격 문제인지 구분", "진급 문제인지, 졸업 자격 문제인지를 구분", "진급 문제인지 졸업 자격 문제인지 먼저 구분"],
    ["출결 특기사항 기준 세분화", "출결 특기사항 기준이 세분화되었습니다", "출결 특기사항 입력 기준이 더 세분화되었습니다", "출결 특기사항은 장기결석 사유 입력, 기타결석 1일 이상 입력, 반복적인 지각·조퇴·결과 사유 입력 가능으로 세분화되었습니다"],
    ["글자 수 축소", "글자 수는 봉사활동 실적 활동내용 50자, 진로활동 특기사항 500자, 행동특성 및 종합의견 300자로 줄었습니다", "글자 수가 여러 항목에서 줄었습니다"],
    ["교과학습발달상황 1·2학년과 3학년 분리", "교과학습발달상황은 1·2학년과 3학년을 분리해서 봐야 합니다", "교과학습발달상황은 1·2학년과 3학년을 분리해서 설명해야 합니다", "교과학습발달상황은 1·2학년 학점·5등급 체계와 3학년 단위수·9등급 체계로 분리됩니다"],
    ["지필평가 → 정기시험", "지필평가 표현은 정기시험으로 정비되었습니다", "지필평가를 정기시험으로 정비", "지필평가라는 표현은 정기시험으로 정비되었습니다"],
    ["세특 모든 학생 입력 원칙", "세특은 모든 학생 입력이 원칙입니다", "세특은 모든 학생 입력 원칙을 적용합니다", "세특은 모든 학생 입력이 원칙이며"],
    ["사전 안내", "사전에 안내", "사전 고지"],
    ["공정성과 신뢰도", "공정성과 신뢰성", "공정성과 신뢰도를 해치지 않도록"],
    ["교사 직접 관찰", "교사가 직접 관찰", "교사 직접 관찰과 평가"],
    ["동아리명만 입력", "동아리명만 기재", "동아리명만 입력합니다"],
    ["활동시간 미기재", "활동시간 기재 삭제", "활동시간 미기재가 원칙"],
    ["특기사항 미입력", "특기사항은 입력하지", "특기사항 미입력으로 처리"],
    ["한글이 원칙", "문자는 한글이 원칙"],
    ["부득이한 경우 영문만 가능", "부득이한 경우에만 영문", "영문만 가능하게 안내"],
    ["한자 입력 불가", "한자를 포함한 다른 외국어 표기는 입력할 수 없습니다", "한자 입력 불가입니다"],
    ["학교교육계획 반영 여부 확인", "학교교육계획에 따른", "학교교육계획 반영 여부 확인이 우선"],
    ["2학기 초 30일 이내 변경계획 공개 여부 확인", "2학기 초 30일 이내", "변경계획 공개 여부 확인"],
    ["단순 기부는 봉사활동으로 인정하지 않음", "단순 기부는 봉사활동으로 인정하지 않는다", "단순 기부는 봉사활동으로 인정하지 않음이 원칙"],
    ["학교가 출석인정 결석 또는 기타결석으로 판단 가능", "출석인정 결석 또는 기타결석으로 판단", "학교가 출석인정 결석 또는 기타결석으로 판단 가능하므로"],
    ["자동으로 미인정결석이라고 단정하지 않음", "자동으로 미인정결석이라고 보면 안", "자동으로 미인정결석이라고 단정하면 안 됩니다"],
    ["증빙자료가 다르면 중복 입력 가능", "서로 다른 증빙자료", "증빙자료가 다르면 중복 입력 가능하게"],
    ["1학점당 수업량 16회의 3분의 2 이상", "1학점당 수업량 16회의 3분의 2 이상 출석"],
    ["1·2학년 기준", "1·2학년 기준으로 먼저"],
    ["출석인정 결석 또는 결과는 출석 반영", "출석인정 결석 또는 결과는 출석으로 반영", "출석 반영으로 처리합니다"],
    ["객관적 증빙자료", "객관적 증빙자료가 필요"],
    ["학업성적관리위원회 심의", "학업성적관리위원회 심의가 필요한지", "학업성적관리위원회 심의 여부"],
    ["입력 주체 과실 확인", "입력 주체 과실 확인이 중요", "입력 주체 과실 확인이 중요합니다"],
    ["교사가 직접 작성해야 함", "교사가 직접 작성", "교사가 직접 관찰하고 평가한 사실"],
    ["학생 작성 문장을 그대로 입력하면 안 됨", "학생 작성 문장을 그대로 입력하면 안 됩니다", "학생이 써 온 문장이나 AI가 만든 문장을 그대로 붙여 넣으면 안 됩니다"],
    ["교사가 직접 관찰한 사실 없이 대신 작성해 줄 수 없다고 안내", "실제 학생 사실 없이 세특 문장을 대신 작성해 주는 방식으로는 답할 수 없습니다"],
    ["작성 기준과 필요한 사실 정보를 먼저 확인", "학생의 과목, 학년, 수업 장면, 관찰 사실, 평가 근거를 먼저 정리"],
    ["1·2학년과 3학년 분리", "1·2학년과 3학년을 같은 기준으로 보면 안 됩니다", "1·2학년과 3학년을 분리해서 봐야"],
    ["학점과 5등급", "학점, 5등급"],
    ["단위수와 9등급", "단위수, 9등급"],
    ["창체 영역명 차이", "창체 영역명 학년별 차이", "창체 영역명은 학년별 차이가 있습니다", "창의적 체험활동 영역명은 1·2학년과 3학년이 다르다", "창체는 1·2학년과 3학년의 영역명과 운영 체계를 나눠 설명해야 합니다"],
    ["기타결석 1일이라도 입력", "기타결석은 1일이라도 입력"],
    ["지각·조퇴·결과는 반복적일 때만 사유 입력 가능", "지각·조퇴·결과는 반복적일 때만 사유 입력", "반복적일 때만 사유 입력 가능", "반복적이거나 잦은 경우에만 사유를 입력할 수 있습니다"],
]


def normalize(text: str) -> str:
    return " ".join(text.split())


def includes_meaning(text: str, phrase: str) -> bool:
    normalized_text = normalize(text)
    normalized_phrase = normalize(phrase)
    if normalized_phrase in normalized_text:
        return True

    for group in SYNONYM_GROUPS:
        if normalized_phrase in group:
            return any(normalize(candidate) in normalized_text for candidate in group)
    return False


def main() -> int:
    results = []
    overall_passed = True

    for test in TESTS:
        result = ENGINE.answer_question(test["question"])
        joined_text = " ".join(
            [
                result["sections"]["conclusion"],
                *result["sections"]["coreSummary"],
                *result["sections"]["gradeDifferences"],
                *result["sections"]["practicalNotes"],
                result["finalAnswer"],
            ]
        )

        used_card_ids = set(result["usedChangeCards"]) | set(result["usedRuleCards"]) | set(result["usedQaCards"])
        matched_cards = [card_id for card_id in test["shouldUseCards"] if card_id in used_card_ids]
        missing_cards = [card_id for card_id in test["shouldUseCards"] if card_id not in used_card_ids]
        missing_mentions = [phrase for phrase in test["mustMention"] if not includes_meaning(joined_text, phrase)]
        topic_hits = [topic_id for topic_id in test["expectedTopicIds"] if topic_id in result["detectedTopicIds"]]

        quality_passed = (
            result["detectedPolicyId"] == test["expectedPolicyId"]
            and bool(topic_hits)
            and bool(matched_cards)
            and not missing_mentions
            and result["qualityPassed"]
        )
        overall_passed = overall_passed and quality_passed

        results.append(
            {
                "testId": test["testId"],
                "question": test["question"],
                "expectedPolicyId": test["expectedPolicyId"],
                "detectedPolicyId": result["detectedPolicyId"],
                "expectedTopicIds": test["expectedTopicIds"],
                "detectedTopicIds": result["detectedTopicIds"],
                "usedChangeCards": result["usedChangeCards"],
                "usedRuleCards": result["usedRuleCards"],
                "usedQaCards": result["usedQaCards"],
                "matchedCards": matched_cards,
                "missingCards": missing_cards,
                "missingMentions": missing_mentions,
                "qualityPassed": quality_passed,
            }
        )

    print(json.dumps({"results": results, "overallPassed": overall_passed}, ensure_ascii=False, indent=2))
    return 0 if overall_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
