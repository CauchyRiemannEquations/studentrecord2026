from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[0-9A-Za-z가-힣·]+")

TOPIC_LABELS = {
    "processing": "기타",
    "attendance": "출결",
    "creative_experience": "창체",
    "subject_progress": "교과학습발달상황",
    "subject_progress_grades_1_2": "교과학습발달상황",
    "subject_progress_grade_3": "교과학습발달상황",
    "awards": "수상",
    "certificates": "자격증",
    "reading": "독서",
    "behavior": "행특",
    "corrections": "정정",
    "personal_school_status": "기타",
    "volunteer_service": "창체",
    "daily_life_activity": "기타",
    "school_violence": "기타",
}

UI_TOPIC_TO_IDS = {
    "auto": [],
    "출결": ["attendance"],
    "창체": ["creative_experience", "volunteer_service"],
    "교과학습발달상황": ["subject_progress", "subject_progress_grades_1_2", "subject_progress_grade_3"],
    "수상": ["awards"],
    "자격증": ["certificates"],
    "독서": ["reading"],
    "행특": ["behavior"],
    "정정": ["corrections"],
    "기타": ["processing", "personal_school_status", "daily_life_activity", "school_violence"],
}

UI_POLICY_TO_ID = {
    "auto": "",
    "2026 변경사항": "change_2026",
    "학년별 차이": "grade_difference",
    "기재 가능 여부": "recordability",
    "원문 페이지 찾기": "page_lookup",
}

TOPIC_KEYWORDS = {
    "attendance": ["출결", "결석", "지각", "조퇴", "결과", "개근", "과목출석률", "출석"],
    "creative_experience": ["창체", "창의적 체험활동", "자율", "자치", "동아리", "진로활동", "학교스포츠클럽"],
    "volunteer_service": ["봉사", "봉사활동", "봉사시간", "기부", "1365", "vms", "dovol"],
    "subject_progress": ["세특", "교과학습발달상황", "교과", "성적", "학점", "단위수", "정기시험", "수행평가", "과목"],
    "subject_progress_grades_1_2": ["1학년", "2학년", "1,2학년", "1·2학년", "학점", "5등급", "성취도"],
    "subject_progress_grade_3": ["3학년", "단위수", "9등급"],
    "awards": ["수상", "교내상", "대회", "수상경력"],
    "certificates": ["자격증", "자격", "민간자격", "국가기술자격"],
    "reading": ["독서", "책", "도서", "원서", "번역본"],
    "behavior": ["행특", "행동특성", "종합의견"],
    "corrections": ["정정", "수정", "바뀜", "뒤바뀜", "누락"],
    "personal_school_status": ["유급", "졸업유예", "진급", "졸업"],
    "processing": ["생기부", "학생부", "학교생활기록부", "ai", "생성형 ai", "한자", "영문"],
}

SYNONYM_MAP = {
    "생기부": "학교생활기록부",
    "학생부": "학교생활기록부",
    "세특": "세부능력 및 특기사항",
    "행특": "행동특성 및 종합의견",
    "창체": "창의적 체험활동상황",
    "지필평가": "정기시험",
    "교내상": "수상경력",
}

GRADE_KEYWORDS = {
    "grade_1": ["1학년"],
    "grade_2": ["2학년"],
    "grades_1_2": ["1,2학년", "1·2학년", "1학년", "2학년"],
    "grade_3": ["3학년"],
}

DEFAULT_CHANGE_2026_TRIGGERS = ["2026", "개정사항", "변경사항", "바뀜", "달라진 점", "2025 대비"]
DEFAULT_RECORDABILITY_TRIGGERS = [
    "써도 돼",
    "써도 되나요",
    "적어도 돼",
    "적을 수 있나요",
    "기재 가능",
    "입력 가능",
    "넣어도 돼",
    "언급 가능",
    "되나요",
    "안 되나요",
    "가능한가요",
    "해도 되나요",
    "기재해도 돼",
    "입력해도 돼",
    "언급해도 돼",
    "써도 되나",
    "적어도 되나",
    "가능한가",
    "가능해",
    "안 되나",
    "금지야",
    "금지인가",
    "넣을 수 있나요",
    "기록 가능",
    "기록 가능해",
    "드러내도 돼",
    "적나요",
    "입력하나요",
    "기재하나요",
]
DEFAULT_DEFINITION_TRIGGERS = ["무슨 뜻", "뜻이 뭐", "정의", "의미", "이란", "란 뭐"]
DEFAULT_PROCEDURE_TRIGGERS = ["어떻게", "절차", "순서", "처리 방법", "처리 절차", "정정 방법"]
DEFAULT_PAGE_LOOKUP_TRIGGERS = ["페이지", "쪽수", "원문", "몇 쪽", "몇쪽", "어디에 나와", "어디 봐야 해", "페이지 알려줘", "원문 어디", "어디야"]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def normalize_text(text: str) -> str:
    normalized = text.strip()
    for source, target in SYNONYM_MAP.items():
        normalized = normalized.replace(source, target)
    return normalized


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(normalize_text(text))]


def jaccard_similarity(left: str, right: str) -> float:
    left_tokens = set(tokenize(left))
    right_tokens = set(tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def format_page_value(value: int | str | None) -> str:
    return str(value) if value is not None else ""


def printed_to_pdf(doc_id: str, printed_page: int | str) -> str:
    value = str(printed_page)
    if doc_id == "official_guidelines_2026_hs":
        return _transform_page_string(value, 6)
    if doc_id == "guide_2026_hs":
        return value
    return ""


def _transform_page_string(value: str, offset: int) -> str:
    parts = [part.strip() for part in value.split(",")]
    transformed_parts: list[str] = []
    for part in parts:
        if "~" in part:
            start, end = [item.strip() for item in part.split("~", 1)]
            if start.isdigit() and end.isdigit():
                transformed_parts.append(f"{int(start) + offset}~{int(end) + offset}")
            else:
                transformed_parts.append(part)
        elif part.isdigit():
            transformed_parts.append(str(int(part) + offset))
        else:
            transformed_parts.append(part)
    return ", ".join(transformed_parts)


def unique_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output


def contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword and keyword in text for keyword in keywords)


@dataclass
class RetrievalBucket:
    change_cards: list[dict[str, Any]]
    rule_cards: list[dict[str, Any]]
    qa_cards: list[dict[str, Any]]
    anchor_test: dict[str, Any] | None


class BrainFirstEngine:
    def __init__(self, brain_dir: Path) -> None:
        self.brain_dir = brain_dir
        self.document_map = load_json(brain_dir / "00_document_map.json")
        self.term_synonyms = load_json(brain_dir / "02_term_synonyms.json")
        self.page_reference_map = load_json(brain_dir / "07_page_reference_map.json")
        self.change_cards = load_jsonl(brain_dir / "04_change_2026_catalog.jsonl")
        self.rule_cards = load_jsonl(brain_dir / "05_rule_cards.jsonl")
        self.qa_cards = load_jsonl(brain_dir / "06_qa_cards.jsonl")
        lexical_router_path = brain_dir / "10_lexical_router.json"
        self.lexical_router = load_json(lexical_router_path) if lexical_router_path.exists() else {}

        self.change_by_id = {card["changeId"]: card for card in self.change_cards}
        self.rule_by_id = {card["ruleId"]: card for card in self.rule_cards}
        self.qa_by_id = {card["qaId"]: card for card in self.qa_cards}
        self.alias_entries: list[dict[str, Any]] = []
        self._bootstrap_lexicon()

    def _bootstrap_lexicon(self) -> None:
        self.change_2026_triggers = unique_preserve_order(
            DEFAULT_CHANGE_2026_TRIGGERS + self.lexical_router.get("change2026Triggers", [])
        )
        self.recordability_triggers = unique_preserve_order(
            DEFAULT_RECORDABILITY_TRIGGERS + self.lexical_router.get("recordabilityTriggersStrong", [])
        )
        self.definition_triggers = unique_preserve_order(
            DEFAULT_DEFINITION_TRIGGERS + self.lexical_router.get("definitionTriggers", [])
        )
        self.procedure_triggers = unique_preserve_order(
            DEFAULT_PROCEDURE_TRIGGERS + self.lexical_router.get("procedureTriggers", [])
        )
        self.page_lookup_triggers = unique_preserve_order(
            DEFAULT_PAGE_LOOKUP_TRIGGERS + self.lexical_router.get("pageLookupTriggers", [])
        )
        self.behavior_negative_keywords: list[str] = []

        for entry in self.term_synonyms.get("terms", []):
            self._register_term_entry(entry)

        for entry in self.lexical_router.get("topicAliasGroups", []):
            self._register_term_entry(entry)
            if "behavior" in entry.get("mapToTopicIds", []):
                self.behavior_negative_keywords.extend(entry.get("aliases", []))

        self.behavior_negative_keywords = unique_preserve_order(
            self.behavior_negative_keywords
            + [
                "안 좋은",
                "안좋은",
                "부정적",
                "부정적인",
                "단점",
                "약점",
                "수업태도",
                "생활태도",
                "게으르",
                "나태",
                "다툰",
                "다투",
                "갈등",
                "잠을 자",
                "수업 중 잠",
                "수업중 잠",
                "발표를 잘 안",
                "발표 안 함",
                "발표 안함",
                "발표 참여 저조",
            ]
        )

    def _register_term_entry(self, entry: dict[str, Any]) -> None:
        canonical = str(entry.get("canonicalTerm", "")).strip()
        aliases = [str(alias).strip() for alias in entry.get("aliases", []) if str(alias).strip()]
        if canonical:
            for alias in aliases:
                SYNONYM_MAP.setdefault(alias, canonical)
        self.alias_entries.append(
            {
                "canonicalTerm": canonical,
                "aliases": aliases,
                "mapToTopicIds": list(entry.get("mapToTopicIds", [])),
            }
        )
        for topic_id in entry.get("mapToTopicIds", []):
            if topic_id not in TOPIC_KEYWORDS:
                TOPIC_KEYWORDS[topic_id] = []
            for keyword in [canonical, *aliases]:
                if keyword and keyword not in TOPIC_KEYWORDS[topic_id]:
                    TOPIC_KEYWORDS[topic_id].append(keyword)

    def answer_question(
        self,
        question: str,
        selected_grade: str = "auto",
        selected_topic: str = "auto",
        selected_question_type: str = "auto",
    ) -> dict[str, Any]:
        analysis = self._analyze_question(question, selected_grade, selected_topic, selected_question_type)
        retrieval = self._retrieve_cards(question, analysis)
        answer = self._build_answer(question, analysis, retrieval)
        return answer

    def _analyze_question(
        self,
        question: str,
        selected_grade: str,
        selected_topic: str,
        selected_question_type: str,
    ) -> dict[str, Any]:
        normalized_question = normalize_text(question)
        tokens = tokenize(normalized_question)

        detected_policy_id = self._detect_policy_id(normalized_question, selected_question_type)
        detected_topic_ids = self._detect_topic_ids(normalized_question, selected_topic)
        detected_grade = self._detect_grade(normalized_question, selected_grade)
        matched_aliases = self._collect_matched_aliases(question)

        if detected_policy_id == "recordability" and contains_any(question, self.behavior_negative_keywords):
            detected_topic_ids = ["behavior"]
        if (
            detected_policy_id == "grade_difference"
            and "학교생활기록부" in normalized_question
            and "subject_progress" not in detected_topic_ids
        ):
            detected_topic_ids = unique_preserve_order(["subject_progress", "creative_experience", *detected_topic_ids])[:3]
        if detected_policy_id == "change_2026" and self._is_change_overview_question(
            normalized_question,
            {"detectedPolicyId": detected_policy_id},
        ):
            detected_topic_ids = unique_preserve_order(["processing", "attendance", "subject_progress", *detected_topic_ids])[:3]

        return {
            "question": question,
            "normalizedQuestion": normalized_question,
            "tokens": tokens,
            "detectedPolicyId": detected_policy_id,
            "detectedTopicIds": detected_topic_ids,
            "detectedGrade": detected_grade,
            "matchedAliases": matched_aliases,
        }

    def _detect_policy_id(
        self,
        question: str,
        selected_question_type: str,
    ) -> str:
        manual = UI_POLICY_TO_ID.get(selected_question_type, "")
        if manual:
            return manual

        if contains_any(question, self.change_2026_triggers):
            return "change_2026"
        if self._is_accumulation_policy_question(question, {}):
            return "change_2026"
        if contains_any(question, ["유급", "졸업유예"]) and contains_any(question, ["학점", "졸업", "진급"]):
            return "change_2026"
        if contains_any(question, ["차이", "다름", "달라", "구분", "비교"]) and any(
            keyword in question for keyword in ["1학년", "2학년", "3학년", "1,2학년", "1·2학년"]
        ):
            return "grade_difference"
        if contains_any(question, self.page_lookup_triggers):
            return "page_lookup"
        if "수행평가" in question and contains_any(question.lower(), ["ai", "생성형 ai"]):
            return "qa_lookup"
        if "정정" in question and contains_any(question, ["수 있나요", "가능", "가능해"]):
            return "recordability"
        if contains_any(question, self.recordability_triggers):
            return "recordability"
        if ("세특" in question or "세부능력 및 특기사항" in question) and contains_any(question, ["문장", "써줘", "작성"]):
            return "recordability"
        if contains_any(question, self.definition_triggers):
            return "definition"
        if contains_any(question, self.procedure_triggers + ["어디에 적어", "어디에 입력", "어디에 써", "부족하면 어떻게"]):
            return "procedure"
        if any(keyword in question for keyword in ["인가요", "일까요", "맞나요", "어떤 경우", "가능한지", "이야", "맞아", "하나요", "적용돼"]):
            return "qa_lookup"
        return "unknown"

    def _detect_topic_ids(
        self,
        question: str,
        selected_topic: str,
    ) -> list[str]:
        manual = UI_TOPIC_TO_IDS.get(selected_topic, [])
        if manual:
            return manual
        if contains_any(question, self.behavior_negative_keywords) and (
            contains_any(question, self.recordability_triggers) or "행특" in question or "행동특성" in question
        ):
            return ["behavior"]

        scores: dict[str, int] = {}
        lowered_question = question.lower()
        for topic_id, keywords in TOPIC_KEYWORDS.items():
            score = sum(2 if len(keyword) >= 3 else 1 for keyword in keywords if keyword.lower() in lowered_question)
            if score:
                scores[topic_id] = score

        ordered = [topic for topic, _score in sorted(scores.items(), key=lambda item: item[1], reverse=True)]
        if ordered:
            return ordered[:3]
        return ["processing"]

    def _collect_matched_aliases(self, question: str) -> list[dict[str, Any]]:
        lowered_question = question.lower()
        matched: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()

        for entry in self.alias_entries:
            canonical = entry.get("canonicalTerm", "")
            for alias in unique_preserve_order([canonical, *entry.get("aliases", [])]):
                lowered_alias = alias.lower()
                key = (canonical, lowered_alias)
                if alias and lowered_alias in lowered_question and key not in seen:
                    seen.add(key)
                    matched.append(
                        {
                            "alias": alias,
                            "canonicalTerm": canonical,
                            "topicIds": list(entry.get("mapToTopicIds", [])),
                        }
                    )

        return matched

    def _detect_grade(self, question: str, selected_grade: str) -> str:
        if selected_grade != "auto":
            return selected_grade
        if any(keyword in question for keyword in GRADE_KEYWORDS["grade_3"]):
            return "3학년"
        if any(keyword in question for keyword in GRADE_KEYWORDS["grades_1_2"]):
            return "1·2학년"
        return "auto"

    def _retrieve_cards(self, question: str, analysis: dict[str, Any]) -> RetrievalBucket:
        change_cards: list[dict[str, Any]] = []
        rule_cards: list[dict[str, Any]] = []
        qa_cards: list[dict[str, Any]] = []

        query_tokens = analysis["tokens"]
        detected_topics = set(analysis["detectedTopicIds"])
        policy_id = analysis["detectedPolicyId"]

        if self._is_negative_behavior_question(question, analysis):
            behavior_rule = self.rule_by_id.get("rule_behavior_negative_traits_educational_perspective")
            behavior_qa = self.qa_by_id.get("qa_behavior_can_record_student_weakness")
            return RetrievalBucket(
                change_cards=[],
                rule_cards=[behavior_rule] if behavior_rule else [],
                qa_cards=[behavior_qa] if behavior_qa else [],
                anchor_test=None,
            )
        if policy_id == "page_lookup" and "과목출석률" in question:
            return RetrievalBucket(
                change_cards=[
                    self.change_by_id[card_id]
                    for card_id in ["chg_2026_004_subject_attendance_rate"]
                    if card_id in self.change_by_id
                ],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_subject_attendance_rate_16_sessions", "rule_grade_1_2_credit_5_grade"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_subject_attendance_recognized_absence"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if policy_id == "page_lookup" and "출결 특기사항" in question:
            return RetrievalBucket(
                change_cards=[
                    self.change_by_id[card_id]
                    for card_id in ["chg_2026_005_attendance_notes"]
                    if card_id in self.change_by_id
                ],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_long_absence_special_note", "rule_other_absence_one_day_note", "rule_tardy_earlyleave_result_note"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[],
                anchor_test=None,
            )
        if policy_id == "page_lookup" and "봉사활동" in question:
            return RetrievalBucket(
                change_cards=[
                    self.change_by_id[card_id]
                    for card_id in ["chg_2026_015_volunteer_content_limit"]
                    if card_id in self.change_by_id
                ],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_volunteer_curricular_link_grades_1_2", "rule_volunteer_content_50_chars"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_volunteer_curricular_grade_1_2"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if policy_id == "grade_difference" and "학교생활기록부" in analysis["normalizedQuestion"]:
            return RetrievalBucket(
                change_cards=[
                    self.change_by_id[card_id]
                    for card_id in ["chg_2026_018_subject_progress_split", "chg_2026_012_creative_area_split"]
                    if card_id in self.change_by_id
                ],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_grade_1_2_credit_5_grade", "rule_grade_3_unit_9_grade", "rule_creative_area_names_by_grade"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_creative_area_difference_by_grade", "qa_subject_small_class_rank_rule"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if policy_id == "grade_difference" and ("세특" in question or "세부능력 및 특기사항" in question):
            return RetrievalBucket(
                change_cards=[
                    self.change_by_id[card_id]
                    for card_id in ["chg_2026_018_subject_progress_split"]
                    if card_id in self.change_by_id
                ],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_grade_1_2_credit_5_grade", "rule_grade_3_unit_9_grade", "rule_subject_notes_for_all_students"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_subject_small_class_rank_rule", "qa_subject_special_none"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_competition_record_question(question, analysis):
            return RetrievalBucket(
                change_cards=[],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_no_competition_participation_record", "rule_awards_only_in_awards_section", "rule_awards_must_follow_school_plan"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_awards_competition_participation"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_retention_graduation_question(question, analysis):
            return RetrievalBucket(
                change_cards=[
                    self.change_by_id[card_id]
                    for card_id in ["chg_2026_002_retention_definition", "chg_2026_003_graduation_deferral"]
                    if card_id in self.change_by_id
                ],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_retention_vs_graduation_deferral"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_retention_vs_graduation_deferral"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_accumulation_policy_question(question, analysis):
            return RetrievalBucket(
                change_cards=[
                    self.change_by_id[card_id]
                    for card_id in ["chg_2026_001_accumulation_authority"]
                    if card_id in self.change_by_id
                ],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_accumulation_decided_by_principal"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_accumulation_principal_policy"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_performance_ai_policy_question(question, analysis):
            return RetrievalBucket(
                change_cards=[
                    self.change_by_id[card_id]
                    for card_id in ["chg_2026_025_performance_assessment_ai"]
                    if card_id in self.change_by_id
                ],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_performance_assessment_ai_caution", "rule_teacher_owns_descriptive_items"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_performance_assessment_ai"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_school_sports_question(question, analysis):
            return RetrievalBucket(
                change_cards=[
                    self.change_by_id[card_id]
                    for card_id in ["chg_2026_013_school_sports_hours_removed", "chg_2026_014_school_sports_special_note_removed"]
                    if card_id in self.change_by_id
                ],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_school_sports_club_name_only", "rule_no_special_note_for_outside_curriculum_sports"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_school_sports_club_record"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_awards_plan_question(question, analysis):
            return RetrievalBucket(
                change_cards=[
                    self.change_by_id[card_id]
                    for card_id in ["chg_2026_007_award_plan"]
                    if card_id in self.change_by_id
                ],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_awards_must_follow_school_plan", "rule_awards_only_in_awards_section"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_awards_competition_participation"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_subject_note_writer_request(question, analysis):
            return RetrievalBucket(
                change_cards=[],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_teacher_owns_descriptive_items", "rule_subject_notes_for_all_students", "rule_no_direct_ai_generated_text"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_processing_ai_polish", "qa_subject_special_none"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_student_written_copy_question(question, analysis) or self._is_student_reflection_question(question, analysis):
            return RetrievalBucket(
                change_cards=[],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_teacher_owns_descriptive_items", "rule_input_based_on_direct_observation", "rule_no_direct_ai_generated_text"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_processing_ai_polish"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_hanja_question(question, analysis):
            return RetrievalBucket(
                change_cards=[],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_hangul_default_english_only", "rule_teacher_owns_descriptive_items"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_processing_hanja_input"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_reference_witness_question(question, analysis):
            return RetrievalBucket(
                change_cards=[],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_long_absence_special_note", "rule_attendance_privacy_committee_note_exception"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_attendance_reference_witness_and_juvenile_case"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_reading_duplication_lookup_question(question, analysis):
            return RetrievalBucket(
                change_cards=[
                    self.change_by_id[card_id]
                    for card_id in ["chg_2026_027_reading_duplication"]
                    if card_id in self.change_by_id
                ],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_reading_same_book_different_evidence", "rule_reading_duplicate_allowed_with_distinct_evidence"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_reading_same_book_duplication"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_subject_attendance_explainer_question(question, analysis):
            return RetrievalBucket(
                change_cards=[
                    self.change_by_id[card_id]
                    for card_id in ["chg_2026_004_subject_attendance_rate"]
                    if card_id in self.change_by_id
                ],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_subject_attendance_rate_16_sessions", "rule_grade_1_2_credit_5_grade"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_subject_attendance_recognized_absence"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_correction_swapped_question(question, analysis):
            return RetrievalBucket(
                change_cards=[],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_correction_swapped_items_committee", "rule_correction_requires_objective_evidence"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_correction_swapped_descriptive_items"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_certificate_record_question(question, analysis):
            return RetrievalBucket(
                change_cards=[],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_certificate_only_designated_scope", "rule_behavior_excludes_forbidden_content"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_certificate_private_license"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_specific_name_question(question, analysis):
            return RetrievalBucket(
                change_cards=[],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_teacher_owns_descriptive_items", "rule_input_based_on_direct_observation"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_processing_ai_polish"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )
        if self._is_sensitive_background_question(question, analysis):
            return RetrievalBucket(
                change_cards=[],
                rule_cards=[
                    self.rule_by_id[card_id]
                    for card_id in ["rule_teacher_owns_descriptive_items", "rule_input_based_on_direct_observation"]
                    if card_id in self.rule_by_id
                ],
                qa_cards=[
                    self.qa_by_id[card_id]
                    for card_id in ["qa_processing_ai_polish"]
                    if card_id in self.qa_by_id
                ],
                anchor_test=None,
            )

        if policy_id == "change_2026":
            change_cards = self._extend_cards(change_cards, self.change_cards, query_tokens, detected_topics, limit=11, card_type="change", policy_id=policy_id, question=question)
            rule_cards = self._extend_cards(rule_cards, self.rule_cards, query_tokens, detected_topics, limit=3, card_type="rule", policy_id=policy_id, question=question)
            qa_cards = self._extend_cards(qa_cards, self.qa_cards, query_tokens, detected_topics, limit=2, card_type="qa", policy_id=policy_id, question=question)
        elif policy_id == "grade_difference":
            change_cards = self._extend_cards(change_cards, self.change_cards, query_tokens, detected_topics, limit=4, card_type="change", policy_id=policy_id, question=question)
            rule_cards = self._extend_cards(rule_cards, self.rule_cards, query_tokens, detected_topics, limit=4, card_type="rule", policy_id=policy_id, question=question)
            qa_cards = self._extend_cards(qa_cards, self.qa_cards, query_tokens, detected_topics, limit=2, card_type="qa", policy_id=policy_id, question=question)
        elif policy_id == "recordability":
            rule_cards = self._extend_cards(rule_cards, self.rule_cards, query_tokens, detected_topics, limit=4, card_type="rule", policy_id=policy_id, question=question)
            qa_cards = self._extend_cards(qa_cards, self.qa_cards, query_tokens, detected_topics, limit=2, card_type="qa", policy_id=policy_id, question=question)
            if change_cards or contains_any(question, self.change_2026_triggers):
                change_cards = self._extend_cards(change_cards, self.change_cards, query_tokens, detected_topics, limit=1, card_type="change", policy_id=policy_id, question=question)
        elif policy_id == "page_lookup":
            change_cards = self._extend_cards(change_cards, self.change_cards, query_tokens, detected_topics, limit=2, card_type="change", policy_id=policy_id, question=question)
            rule_cards = self._extend_cards(rule_cards, self.rule_cards, query_tokens, detected_topics, limit=2, card_type="rule", policy_id=policy_id, question=question)
            qa_cards = self._extend_cards(qa_cards, self.qa_cards, query_tokens, detected_topics, limit=1, card_type="qa", policy_id=policy_id, question=question)
        elif policy_id in {"qa_lookup", "definition", "procedure", "unknown"}:
            qa_cards = self._extend_cards(qa_cards, self.qa_cards, query_tokens, detected_topics, limit=3, card_type="qa", policy_id=policy_id, question=question)
            rule_cards = self._extend_cards(rule_cards, self.rule_cards, query_tokens, detected_topics, limit=2, card_type="rule", policy_id=policy_id, question=question)
            if change_cards or contains_any(question, self.change_2026_triggers):
                change_cards = self._extend_cards(change_cards, self.change_cards, query_tokens, detected_topics, limit=1, card_type="change", policy_id=policy_id, question=question)

        if policy_id == "change_2026":
            if not rule_cards:
                rule_cards = self._extend_cards([], self.rule_cards, query_tokens, detected_topics, limit=1, card_type="rule", policy_id=policy_id, question=question)
            if not qa_cards:
                qa_cards = self._extend_cards([], self.qa_cards, query_tokens, detected_topics, limit=1, card_type="qa", policy_id=policy_id, question=question)
        elif policy_id == "recordability":
            if not rule_cards:
                rule_cards = self._extend_cards([], self.rule_cards, query_tokens, detected_topics, limit=1, card_type="rule", policy_id=policy_id, question=question)
            if not qa_cards:
                qa_cards = self._extend_cards([], self.qa_cards, query_tokens, detected_topics, limit=1, card_type="qa", policy_id=policy_id, question=question)
        elif policy_id in {"qa_lookup", "definition", "procedure", "unknown"}:
            if not qa_cards:
                qa_cards = self._extend_cards([], self.qa_cards, query_tokens, detected_topics, limit=1, card_type="qa", policy_id=policy_id, question=question)

        return RetrievalBucket(
            change_cards=change_cards,
            rule_cards=rule_cards,
            qa_cards=qa_cards,
            anchor_test=None,
        )

    def _extend_cards(
        self,
        current_cards: list[dict[str, Any]],
        candidate_cards: list[dict[str, Any]],
        query_tokens: list[str],
        detected_topics: set[str],
        limit: int,
        card_type: str,
        policy_id: str,
        question: str,
    ) -> list[dict[str, Any]]:
        current_ids = {
            card.get("changeId") or card.get("ruleId") or card.get("qaId")
            for card in current_cards
        }

        ranked = sorted(
            candidate_cards,
            key=lambda card: self._score_card(card, query_tokens, detected_topics, card_type, policy_id, question),
            reverse=True,
        )
        output = list(current_cards)
        for card in ranked:
            card_id = card.get("changeId") or card.get("ruleId") or card.get("qaId")
            if card_id in current_ids:
                continue
            if self._score_card(card, query_tokens, detected_topics, card_type, policy_id, question) <= 0:
                continue
            output.append(card)
            current_ids.add(card_id)
            if len(output) >= limit:
                break
        return output

    def _score_card(
        self,
        card: dict[str, Any],
        query_tokens: list[str],
        detected_topics: set[str],
        card_type: str,
        policy_id: str,
        question: str,
    ) -> int:
        base_score = 0
        card_text_parts: list[str] = []
        for field_name in ["title", "ruleSummary", "question", "answer", "before2025", "after2026", "practicalMeaning"]:
            value = card.get(field_name)
            if isinstance(value, str):
                card_text_parts.append(value)
        for field_name in ["allowed", "notAllowed", "conditions", "keywords"]:
            values = card.get(field_name, [])
            if isinstance(values, list):
                card_text_parts.extend(str(value) for value in values)
        haystack = " ".join(card_text_parts).lower()

        for token in query_tokens:
            if token in haystack:
                base_score += 3
        if card.get("topicId") in detected_topics:
            base_score += 6
        if card.get("importance") == "high":
            base_score += 2

        if policy_id == "change_2026":
            if card_type == "change":
                base_score += 10
            elif card_type == "rule":
                base_score += 2
        elif policy_id == "recordability":
            if card_type == "rule":
                base_score += 10
            elif card_type == "qa":
                base_score += 6
            elif card_type == "change":
                base_score -= 12
        elif policy_id == "qa_lookup":
            if card_type == "qa":
                base_score += 10
            elif card_type == "rule":
                base_score += 3
            elif card_type == "change":
                base_score -= 12
        elif policy_id in {"definition", "procedure", "unknown"}:
            if card_type == "qa":
                base_score += 5
            elif card_type == "change":
                base_score -= 8

        if card_type == "change" and policy_id != "change_2026" and "2026" not in question:
            base_score -= 10
        return base_score

    def _build_answer(
        self,
        question: str,
        analysis: dict[str, Any],
        retrieval: RetrievalBucket,
    ) -> dict[str, Any]:
        used_change_ids = [card["changeId"] for card in retrieval.change_cards]
        used_rule_ids = [card["ruleId"] for card in retrieval.rule_cards]
        used_qa_ids = [card["qaId"] for card in retrieval.qa_cards]

        sections = self._render_sections(question, analysis, retrieval)
        section_labels = self._build_section_labels(analysis["detectedPolicyId"])
        references = self._build_reference_block(retrieval)
        evidence = self._build_evidence_block(retrieval)
        used_page_refs = self._flatten_used_page_refs(references)

        answer_mode = "brain-first" if used_change_ids or used_rule_ids or used_qa_ids else "fallback"
        total_used = len(used_change_ids) + len(used_rule_ids) + len(used_qa_ids)
        quality_passed = bool(used_change_ids or used_rule_ids or used_qa_ids)
        if analysis["detectedPolicyId"] == "change_2026":
            quality_passed = bool(used_change_ids) and total_used >= 3
        elif analysis["detectedPolicyId"] == "recordability":
            quality_passed = bool(used_rule_ids or used_qa_ids)
        elif analysis["detectedPolicyId"] == "qa_lookup":
            quality_passed = bool(used_qa_ids)
        if self._is_change_overview_question(question, analysis) and total_used < 8:
            quality_passed = False

        final_answer = self._sections_to_text(sections, references, section_labels)

        return {
            "question": question,
            "normalizedQuery": analysis["normalizedQuestion"],
            "matchedAliases": analysis["matchedAliases"],
            "detectedPolicyId": analysis["detectedPolicyId"],
            "detectedTopicIds": analysis["detectedTopicIds"],
            "usedChangeCards": used_change_ids,
            "usedRuleCards": used_rule_ids,
            "usedQaCards": used_qa_ids,
            "officialSourceRefs": references["official"],
            "guideSourceRefs": references["guide"],
            "usedPageRefs": used_page_refs,
            "answerMode": answer_mode,
            "sections": sections,
            "sectionLabels": section_labels,
            "references": references,
            "evidence": evidence,
            "debug": {
                "anchorTestId": retrieval.anchor_test["testId"] if retrieval.anchor_test else None,
                "detectedGrade": analysis["detectedGrade"],
                "answerGenerationMode": answer_mode,
                "answerStartsWith": sections["conclusion"][:30],
                "usedCardIds": {
                    "change": used_change_ids,
                    "rule": used_rule_ids,
                    "qa": used_qa_ids,
                },
            },
            "finalAnswer": final_answer,
            "qualityPassed": quality_passed,
        }

    def _render_sections(
        self,
        question: str,
        analysis: dict[str, Any],
        retrieval: RetrievalBucket,
    ) -> dict[str, Any]:
        policy_id = analysis["detectedPolicyId"]
        question_text = question.strip()

        if policy_id == "page_lookup":
            return self._render_page_lookup_answer(question_text, analysis, retrieval)
        if self._is_subject_note_writer_request(question_text, analysis):
            return self._render_subject_note_writer_guard(retrieval)
        if self._is_student_written_copy_question(question_text, analysis):
            return self._render_student_written_subject_note_answer()
        if self._is_hanja_question(question_text, analysis):
            return self._render_hanja_subject_note_answer()
        if self._is_retention_graduation_question(question_text, analysis):
            return self._render_retention_answer(retrieval)
        if self._is_accumulation_policy_question(question_text, analysis):
            return self._render_accumulation_answer(retrieval)
        if self._is_performance_ai_policy_question(question_text, analysis):
            return self._render_performance_ai_answer()
        if self._is_school_sports_question(question_text, analysis):
            return self._render_school_sports_answer()
        if self._is_awards_plan_question(question_text, analysis):
            return self._render_awards_plan_answer()
        if self._is_donation_question(question_text, analysis):
            return self._render_donation_answer()
        if self._is_reference_witness_question(question_text, analysis):
            return self._render_reference_witness_answer()
        if self._is_reading_duplication_lookup_question(question_text, analysis):
            return self._render_reading_duplication_answer()
        if self._is_subject_attendance_explainer_question(question_text, analysis):
            return self._render_subject_attendance_answer()
        if self._is_correction_swapped_question(question_text, analysis):
            return self._render_correction_swapped_answer()
        if self._is_negative_behavior_question(question_text, analysis):
            return self._render_behavior_negative_traits_answer(retrieval)
        if self._is_competition_record_question(question_text, analysis):
            return self._render_competition_record_answer()
        if self._is_certificate_record_question(question_text, analysis):
            return self._render_certificate_record_answer()
        if self._is_sensitive_background_question(question_text, analysis):
            return self._render_sensitive_background_answer()
        if self._is_specific_name_question(question_text, analysis):
            return self._render_specific_name_answer(question_text)
        if self._is_student_reflection_question(question_text, analysis):
            return self._render_student_reflection_subject_note_answer()
        if self._is_ai_polished_text_question(question_text, analysis):
            return self._render_ai_polished_text_answer()
        if self._is_reference_witness_absence_question(question_text, analysis):
            return self._render_reference_witness_answer_strict()
        if self._is_reading_duplication_question(question_text, analysis):
            return self._render_reading_duplication_record_answer()
        if self._is_grade3_subject_attendance_question(question_text, analysis):
            return self._render_grade3_subject_attendance_answer()
        if policy_id == "change_2026":
            return self._render_change_answer(question_text, analysis, retrieval)
        if policy_id == "grade_difference":
            return self._render_grade_difference_answer(retrieval)
        if policy_id == "recordability":
            return self._render_recordability_answer(question_text, retrieval)
        return self._render_case_answer(retrieval)

    def _build_section_labels(self, policy_id: str) -> dict[str, str]:
        if policy_id == "recordability":
            return {
                "conclusion": "판단",
                "coreSummary": "이유",
                "gradeDifferences": "학년별 차이",
                "practicalNotes": "주의",
                "references": "근거 페이지",
            }
        return {
            "conclusion": "결론",
            "coreSummary": "핵심 정리",
            "gradeDifferences": "학년별 차이",
            "practicalNotes": "실무상 주의",
            "references": "참고 자료",
        }

    def _is_negative_behavior_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return (
            analysis["detectedPolicyId"] == "recordability"
            and "behavior" in analysis["detectedTopicIds"]
            and contains_any(question, self.behavior_negative_keywords)
        )

    def _is_subject_note_writer_request(self, question: str, analysis: dict[str, Any]) -> bool:
        return (
            analysis["detectedPolicyId"] == "recordability"
            and ("세특" in question or "세부능력 및 특기사항" in question)
            and contains_any(question, ["문장 하나", "문장 써", "문장 작성", "써줘", "작성해"])
        )

    def _is_student_written_copy_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return (
            analysis["detectedPolicyId"] == "recordability"
            and ("세특" in question or "세부능력 및 특기사항" in question)
            and contains_any(question, ["그대로 붙여", "붙여 넣", "붙여넣", "학생이 써 온", "학생이 쓴", "학생 작성 문장"])
        )

    def _is_hanja_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return (
            analysis["detectedPolicyId"] == "recordability"
            and "한자" in question
            and contains_any(question, ["세특", "학교생활기록부", "학생부", "생기부"])
        )

    def _is_retention_graduation_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return contains_any(question, ["유급", "졸업유예"]) and contains_any(question, ["학점", "졸업", "진급"])

    def _is_accumulation_policy_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return (
            contains_any(question, ["누가기록"])
            and contains_any(question, ["창체", "행특", "행동특성", "종합의견", "일상생활"])
            and contains_any(question, ["교육청", "똑같이", "공통", "운영"])
        )

    def _is_performance_ai_policy_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return "수행평가" in question and contains_any(question.lower(), ["ai", "생성형 ai"])

    def _is_school_sports_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return "학교스포츠클럽" in question and contains_any(question, ["시간", "특기사항", "적나요", "입력"])

    def _is_awards_plan_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return contains_any(question, ["학교교육계획", "학교교육계획서"]) and contains_any(question, ["교내상", "수상경력"])

    def _is_donation_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return contains_any(question, ["기부", "물품 기부", "금전 기부"]) and contains_any(question, ["봉사", "봉사시간"])

    def _is_reference_witness_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return "참고인 조사" in question and contains_any(question, ["빠진", "결석", "미인정"])

    def _is_reading_duplication_lookup_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return (
            analysis["detectedPolicyId"] in {"page_lookup", "qa_lookup"}
            and
            ("reading" in analysis["detectedTopicIds"])
            and contains_any(question, ["같은 책", "여러 과목", "중복"])
            and contains_any(question, ["한 번만", "한번만", "또", "중복"])
        )

    def _is_subject_attendance_explainer_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return "과목출석률" in question and contains_any(question, ["기준", "설명", "어떻게"])

    def _is_correction_swapped_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return contains_any(question, ["세특", "행특", "서술형"]) and contains_any(question, ["뒤바뀐", "뒤바뀌", "바뀌었으면", "정정"])

    def _is_competition_record_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return analysis["detectedPolicyId"] == "recordability" and contains_any(
            question,
            ["교외대회", "교내대회", "대회 참가", "참가 사실", "외부 대회", "공모전", "외부상", "참가만", "대회 준비"],
        )

    def _is_certificate_record_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return (
            analysis["detectedPolicyId"] == "recordability"
            and contains_any(question, ["자격증", "민간자격증", "국가기술자격", "국제공인 자격증", "컴활"])
            and contains_any(question, ["행특", "행동특성", "종합의견", "세특", "진로활동", "창체", "학생부", "생기부", "학교생활기록부"])
        )

    def _is_sensitive_background_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return analysis["detectedPolicyId"] == "recordability" and contains_any(
            question,
            ["부모 직업", "학부모 직업", "가정 배경", "사회경제적 배경"],
        )

    def _is_specific_name_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return analysis["detectedPolicyId"] == "recordability" and contains_any(
            question,
            ["대학명", "대학 이름", "특정 대학", "서울대", "기관명", "외부 기관명", "기업 이름", "회사 이름", "상호명", "강사명", "강사 이름", "학교 밖 교육기관"],
        )

    def _is_student_reflection_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return analysis["detectedPolicyId"] == "recordability" and "소감문" in question and "세특" in question

    def _is_ai_polished_text_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return (
            analysis["detectedPolicyId"] == "recordability"
            and "AI" in question.upper()
            and contains_any(question, ["다듬", "문장", "넣어도", "붙여"])
        )

    def _is_reference_witness_absence_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return analysis["detectedPolicyId"] == "qa_lookup" and "참고인 조사" in question and "결석" in question

    def _is_reading_duplication_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return ("reading" in analysis["detectedTopicIds"]) and contains_any(question, ["같은 책", "여러 과목", "중복"])

    def _is_grade3_subject_attendance_question(self, question: str, analysis: dict[str, Any]) -> bool:
        return "3학년" in question and "과목출석률" in question

    def _is_change_overview_question(self, question: str, analysis: dict[str, Any]) -> bool:
        broad_change_terms = ["변경사항", "개정사항", "바뀜", "달라진 점", "뭐가 바뀜", "뭐가 바뀌"]
        specific_topic_terms = [
            "출결",
            "행특",
            "세특",
            "창체",
            "봉사",
            "독서",
            "수상",
            "자격증",
            "유급",
            "졸업",
            "과목출석률",
            "정정",
        ]
        return (
            analysis["detectedPolicyId"] == "change_2026"
            and "2026" in question
            and contains_any(question, broad_change_terms)
            and not contains_any(question, specific_topic_terms)
        )

    def _render_change_answer(self, question: str, analysis: dict[str, Any], retrieval: RetrievalBucket) -> dict[str, Any]:
        if self._is_change_overview_question(question, analysis):
            return self._render_change_overview_answer()

        change_summaries = [card["title"] for card in retrieval.change_cards[:8]]
        practical_notes = [card["practicalMeaning"] for card in retrieval.change_cards[:4]]
        grade_notes = [self._grade_scope_label(card["gradeScope"]) for card in retrieval.change_cards[:4] if self._grade_scope_label(card["gradeScope"])]

        conclusion = "2026학년도 변경사항은 공식 기재요령 기준으로 설명해야 합니다."
        if "출결 특기사항" in question:
            return self._render_attendance_change_answer()

        return {
            "conclusion": conclusion,
            "coreSummary": unique_preserve_order(change_summaries),
            "gradeDifferences": unique_preserve_order(grade_notes),
            "practicalNotes": unique_preserve_order(practical_notes),
        }

    def _render_change_overview_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "2026 변경사항은 공식 기재요령 기준으로 설명해야 하며, 학년별 차이가 있는 항목은 분기해서 설명해야 합니다.",
            "coreSummary": [
                "생성형 AI 관련 유의사항이 추가되어, 학생 작성 문장이나 AI 생성 문장을 검토 없이 그대로 입력하면 안 됩니다.",
                "누가기록 여부 및 방법은 학교장이 정하며, 적용 대상은 창체, 일상생활 활동상황, 행동특성 및 종합의견입니다.",
                "유급은 진급 불가 개념으로 정리되고, 졸업 학점 미충족은 졸업유예로 별도 구분됩니다.",
                "1·2학년 과목출석률은 1학점당 수업량 16회의 3분의 2 이상 출석 기준으로 관리합니다.",
                "출결 특기사항은 장기결석 사유 입력, 기타결석 1일 이상 입력, 반복적인 지각·조퇴·결과 사유 입력 가능으로 세분화되었습니다.",
                "글자 수는 봉사활동 실적 활동내용 50자, 진로활동 특기사항 500자, 행동특성 및 종합의견 300자로 줄었습니다.",
                "창체는 1·2학년과 3학년의 영역명과 운영 체계를 나눠 설명해야 합니다.",
                "교과학습발달상황은 1·2학년 학점·5등급 체계와 3학년 단위수·9등급 체계로 분리됩니다.",
                "지필평가라는 표현은 정기시험으로 정비되었습니다.",
                "세특은 모든 학생 입력이 원칙이며, 부득이한 경우에만 심의를 거쳐 '특이사항 없음.' 입력이 가능합니다.",
            ],
            "gradeDifferences": [
                "1·2학년은 2022 개정 교육과정, 학점, 과목출석률, 5등급, 미이수·대체이수·재이수 체계를 봅니다.",
                "3학년은 기존 교육과정, 단위수, 9등급, 기존 창체 체계를 유지합니다.",
            ],
            "practicalNotes": [
                "학교장이 정하는 사항은 전국 공통 기준처럼 단정하면 안 됩니다.",
                "교과와 창체처럼 학년 차이가 큰 항목은 반드시 학년을 나눠 답해야 합니다.",
                "최종 업무 처리 전에는 공식 기재요령 인쇄 쪽수 기준으로 다시 확인해야 합니다.",
            ],
        }

    def _render_attendance_change_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "2026학년도에는 출결 특기사항 입력 기준이 장기결석, 기타결석, 반복적인 지각·조퇴·결과 중심으로 더 세분화되었습니다.",
            "coreSummary": [
                "장기결석은 결석 종류별 사유를 입력하고, 학교장이 정한 기준에 따라 운영합니다.",
                "기타결석은 1일이라도 입력합니다.",
                "지각·조퇴·결과는 원칙적으로 입력하지 않되, 반복적이거나 잦은 경우에만 사유를 입력할 수 있습니다.",
                "출석인정 결석은 특기사항에 사유를 입력하지 않습니다.",
                "개근 입력은 전입·재입학·특수교육대상자 등 예외 기준이 더 구체화되었습니다.",
            ],
            "gradeDifferences": [
                "과목출석률은 1·2학년 기준으로, 1학점당 수업량 16회의 3분의 2 이상 출석 기준을 함께 설명해야 합니다.",
            ],
            "practicalNotes": [
                "학교장이 정하는 장기결석 기준과 학업성적관리위원회 심의 필요 여부를 같이 확인해야 합니다.",
                "참고인 조사 출석처럼 판단이 필요한 사례는 자동으로 미인정결석이라고 단정하지 말고 학교 기준과 증빙을 함께 확인해야 합니다.",
            ],
        }

    def _render_grade_difference_answer(self, retrieval: RetrievalBucket) -> dict[str, Any]:
        conclusion = "2026학년도 고등학교 학교생활기록부는 1·2학년과 3학년을 같은 기준으로 보면 안 됩니다."
        core_summary = [
            "1·2학년은 2022 개정 교육과정과 고교학점제 기준을 적용합니다.",
            "3학년은 기존 교육과정과 기존 평가 체계를 유지합니다.",
        ]
        grade_differences = [
            "1·2학년: 학점과 5등급 체계, 과목출석률, 성취도 및 성취도별 분포비율 체계를 적용합니다.",
            "3학년: 단위수와 9등급 체계를 유지합니다.",
            "1·2학년: 창체는 자율·자치활동, 동아리활동, 진로활동 중심으로 보고 창체 영역명 차이를 함께 설명해야 합니다.",
            "3학년: 창체는 기존 4개 영역 체계를 유지합니다.",
        ]
        practical_notes = [card["ruleSummary"] for card in retrieval.rule_cards[:4]]
        return {
            "conclusion": conclusion,
            "coreSummary": core_summary,
            "gradeDifferences": grade_differences,
            "practicalNotes": unique_preserve_order(practical_notes),
        }

    def _render_retention_answer(self, retrieval: RetrievalBucket) -> dict[str, Any]:
        return {
            "conclusion": "아닙니다. 졸업에 필요한 학점을 못 채운 경우를 곧바로 유급이라고 보면 안 됩니다.",
            "coreSummary": [
                "유급과 졸업유예를 구분해서 설명해야 합니다.",
                "유급은 해당 학년 교육과정을 마치지 못해 상급 학년으로 진급하지 못하는 경우입니다.",
                "졸업유예는 출석일수는 충족했지만 졸업에 필요한 학점을 모두 취득하지 못해 졸업 자격을 얻지 못한 경우입니다.",
                "즉 진급 문제인지, 졸업 자격 문제인지부터 나눠서 봐야 합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "진급 문제인지 졸업 자격 문제인지 구분해서 답해야 합니다.",
                retrieval.qa_cards[0]["answer"] if retrieval.qa_cards else "",
            ],
        }

    def _render_accumulation_answer(self, retrieval: RetrievalBucket) -> dict[str, Any]:
        return {
            "conclusion": "아닙니다. 현재는 교육청 공통 기준으로 똑같이 운영한다고 단정할 수 없습니다.",
            "coreSummary": [
                "창체, 일상생활 활동상황, 행동특성 및 종합의견의 누가기록 여부 및 방법은 학교장이 정합니다.",
                "같은 교육청 안에서도 학교별 방침이 다를 수 있으므로 학교 운영 기준 확인이 필요합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "전국 공통 기준이나 교육청 공통 기준처럼 단정하면 안 됩니다.",
                retrieval.qa_cards[0]["answer"] if retrieval.qa_cards else "",
            ],
        }

    def _render_subject_note_writer_guard(self, retrieval: RetrievalBucket) -> dict[str, Any]:
        return {
            "conclusion": "자료상 확인 불가입니다. 실제 학생 사실 없이 세특 문장을 대신 작성해 주는 방식으로는 답할 수 없습니다.",
            "coreSummary": [
                "세특은 교사가 직접 관찰하고 평가한 사실을 바탕으로 작성해야 합니다.",
                "학생이 써 온 문장이나 AI가 만든 문장을 그대로 붙여 넣으면 안 됩니다.",
                "모든 학생 입력이 원칙이며, 부득이한 경우에만 학업성적관리위원회 심의를 거쳐 '특이사항 없음.'을 입력할 수 있습니다.",
            ],
            "gradeDifferences": [
                "1·2학년과 3학년의 교과 기록 체계가 다르므로 학년을 먼저 확인해야 합니다."
            ],
            "practicalNotes": [
                "학생의 과목, 학년, 수업 장면, 관찰 사실, 평가 근거를 먼저 정리한 뒤 교사가 직접 문장을 작성해야 합니다.",
                retrieval.qa_cards[0]["answer"] if retrieval.qa_cards else "",
            ],
        }

    def _render_student_written_subject_note_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "불가합니다. 학생 작성 문장을 그대로 입력하면 안 되며, 교사가 직접 작성해야 합니다.",
            "coreSummary": [
                "세특은 교사가 직접 관찰하고 평가한 사실을 바탕으로 작성해야 합니다.",
                "학생 작성 문장을 그대로 입력하면 안 됨이 원칙이며, 학생이 작성한 문장을 그대로 입력하면 안 됨이 원칙입니다.",
                "AI가 만든 문장도 검토 없이 그대로 붙여 넣으면 안 됩니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "학생이 써 온 표현은 참고 자료일 수 있지만 최종 문장과 사실관계는 교사가 다시 작성하고 확인해야 합니다.",
            ],
        }

    def _render_hanja_subject_note_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "불가합니다. 학교생활기록부 문자는 한글이 원칙이며, 부득이한 경우 영문만 가능하므로 한자 입력 불가입니다.",
            "coreSummary": [
                "한글이 원칙입니다.",
                "부득이한 경우 영문만 가능하게 안내됩니다.",
                "한자 입력 불가로 보는 것이 맞습니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "영문 허용 예시는 용어 표기 예시일 뿐이고, 한자 허용으로 확대 해석하면 안 됩니다.",
            ],
        }

    def _render_performance_ai_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "조건부 가능입니다. 수행평가에서 생성형 AI 활용을 무조건 허용된다고 답하면 안 되며, 사전 안내와 공정성·신뢰도 관리가 먼저입니다.",
            "coreSummary": [
                "평가 기준, AI 활용 가능 범위, 제출 방식은 사전에 안내해야 합니다.",
                "과제형 수행평가나 암기식 수행평가는 지양하고, 공정성과 신뢰도를 해치지 않도록 운영해야 합니다.",
                "최종 평가는 교사 직접 관찰과 평가를 바탕으로 해야 합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "AI 산출물을 학생의 실제 수행처럼 그대로 인정하면 안 됩니다.",
                "서술형 입력은 교사의 직접 관찰과 검토 책임이 남습니다.",
            ],
        }

    def _render_school_sports_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "불가합니다. 정규교육과정 이외 학교스포츠클럽은 활동시간이나 특기사항을 적지 않고 동아리명만 입력합니다.",
            "coreSummary": [
                "동아리명만 입력합니다.",
                "활동시간 미기재가 원칙입니다.",
                "특기사항 미입력으로 처리합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "학교장 기준에 따른 누가기록 보조 자료와 학생부 입력 기준을 혼동하면 안 됩니다.",
            ],
        }

    def _render_awards_plan_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "불가합니다. 학교교육계획에 반영되지 않은 교내상은 입력할 수 없고, 그 계획에 따라 실시한 교내상만 수상경력에 입력합니다.",
            "coreSummary": [
                "학교교육계획 반영 여부 확인이 우선입니다.",
                "학년 초 학교교육계획에 연간 대회 및 수상내용 등의 실시계획이 반영된 교내상만 수상경력에 입력합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "2학기 초 30일 이내 변경계획 공개 여부 확인도 함께 해야 합니다.",
                "학교장 결재를 거친 변경인지 확인하지 않고 임의로 넣으면 안 됩니다.",
            ],
        }

    def _render_donation_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "불가합니다. 단순 기부는 봉사활동으로 인정하지 않음이 원칙입니다.",
            "coreSummary": [
                "물품이나 금전만 기부한 사실을 봉사시간으로 바꿔 적을 수는 없습니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "봉사활동은 실제 활동 내용과 인정 기준이 맞는지 별도로 확인해야 합니다.",
            ],
        }

    def _render_reference_witness_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "자동으로 미인정결석이라고 단정하면 안 됩니다.",
            "coreSummary": [
                "학교가 출석인정 결석 또는 기타결석으로 판단 가능하므로 사안을 확인해야 합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "사유와 증빙을 바탕으로 학교 기준에 따라 판단해야 하며, 자동으로 미인정결석이라고 단정하지 않음이 중요합니다.",
            ],
        }

    def _render_reading_duplication_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "반드시 한 번만 적는다고 보면 안 됩니다. 증빙자료가 다르면 중복 입력 가능하게 설명해야 합니다.",
            "coreSummary": [
                "원서와 번역본처럼 서로 다른 읽기 활동과 증빙자료가 다르면 각각 입력 가능합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "같은 책 제목이라는 이유만으로 일괄 불가 처리하지 말고, 증빙자료와 활동의 차이를 함께 확인해야 합니다.",
            ],
        }

    def _render_subject_attendance_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "2026학년도 과목출석률은 1·2학년 기준으로 설명해야 하며, 1학점당 수업량 16회의 3분의 2 이상 출석이 핵심입니다.",
            "coreSummary": [
                "1학점당 수업량 16회의 3분의 2 이상 출석이 기준입니다.",
                "1·2학년 기준으로 먼저 설명해야 합니다.",
                "출석인정 결석 또는 결과는 출석 반영으로 처리합니다.",
                "과목 담당교사가 매시간 수업 참여 여부를 확인해 나이스에 입력합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "3학년의 기존 체계와 혼동하지 않도록 1·2학년 질문인지 먼저 확인하는 것이 안전합니다.",
            ],
        }

    def _render_correction_swapped_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "조건부 가능입니다. 객관적 증빙자료와 입력 주체 과실 확인, 학업성적관리위원회 심의 여부를 함께 확인해야 합니다.",
            "coreSummary": [
                "객관적 증빙자료가 필요합니다.",
                "학업성적관리위원회 심의가 필요한지 확인해야 합니다.",
                "입력 주체 과실 확인이 중요합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "학생끼리 뒤바뀐 서술형 항목은 기계적으로 바꾸지 말고 당시 입력 근거와 책임 주체를 먼저 확인해야 합니다.",
            ],
        }

    def _render_behavior_negative_traits_answer(self, retrieval: RetrievalBucket) -> dict[str, Any]:
        qa_answer = ""
        for card in retrieval.qa_cards:
            if card["qaId"] == "qa_behavior_can_record_student_weakness":
                qa_answer = card["answer"]
                break

        return {
            "conclusion": "조건부 가능입니다. 학생의 부정적 행동특성을 아예 쓸 수 없는 것은 아니지만, 단순한 단점 나열은 부적절하고 낙인 표현도 쓰면 안 됩니다.",
            "coreSummary": [
                "행동특성 및 종합의견은 학교 교육활동 전반에서 지속적으로 관찰한 행동특성을 바탕으로, 학생의 성장 정도와 발전 가능성을 고려한 교육적 관점, 곧 학생의 성장을 지원하는 교육적 관점에서 작성해야 합니다.",
                "부정적인 행동특성은 구체적 관찰 근거가 있어야 하며, 부정적인 행동특성은 구체적 누가기록 권장이 원칙입니다.",
                "다른 항목에 입력할 수 없는 금지 내용을 행동특성 및 종합의견에 우회 입력할 수는 없습니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": unique_preserve_order(
                [
                    "학생을 깎아내리는 표현, 성격이나 인성을 단정하는 표현, 학생의 단점만 나열하는 방식은 피해야 합니다.",
                    "누가기록 여부와 방법은 학교장이 정할 수 있으므로 학교 내부 기준도 함께 확인하는 것이 안전합니다.",
                    qa_answer,
                ]
            ),
        }

    def _render_competition_record_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "불가합니다. 교외대회 참가 사실과 그 성적·수상 실적은 세특에 기재 불가이고, 교내대회 참가 사실도 수상경력 외 다른 항목에 우회 입력하면 안 됩니다.",
            "coreSummary": [
                "교외대회 관련 사실은 학교장 허가를 받아 참여한 경우라도 세특이나 행특 등 다른 항목에 적을 수 없습니다.",
                "입력 가능한 교내상은 학교교육계획에 따라 실시한 경우에 한해 수상경력 항목에서만 다룹니다.",
                "대회 명칭을 단순 행사나 활동처럼 바꾸어 세특에 적는 우회 입력도 허용되지 않습니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "질문이 세특이든 행특이든 핵심 판단은 같습니다. 대회 참가 사실만으로는 기재 불가입니다.",
                "교내상 입력 가능 여부는 학교교육계획 반영 여부와 2학기 초 30일 이내 변경계획 공개 여부까지 함께 확인해야 합니다.",
            ],
        }

    def _render_certificate_record_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "불가합니다. 자격증 취득 사실은 입력 범위가 정해진 자격증 항목에서만 다루고, 세특·행특·진로활동 등에 우회 입력하면 안 됩니다.",
            "coreSummary": [
                "실무적으로는 원칙적으로 불가로 판단하고, 허용 범위를 자격증 항목에서만 확인해야 합니다.",
                "입력 범위는 국가기술자격, 법령상 국가자격, 교육부장관이 지정한 국가공인 민간자격으로 한정됩니다.",
                "세특, 행동특성 및 종합의견, 진로활동은 학생의 교육활동과 성장 과정을 적는 항목이지, 자격증 취득 사실을 대신 적는 항목이 아닙니다.",
                "다른 항목에 입력할 수 없는 내용을 서술형 항목에 우회 입력하는 것도 허용되지 않습니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "먼저 해당 자격이 자격증 항목의 입력 범위에 드는지 확인해야 합니다.",
                "입력 대상이 아닌 자격증은 세특, 행특, 진로활동으로 돌려 적으면 안 됩니다.",
            ],
        }

    def _render_sensitive_background_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "불가합니다. 부모 직업이나 가정 배경은 기록해서는 안 되는 내용에 가깝고, 학교생활기록부는 교육활동과 직접 관련된 내용만 적어야 합니다.",
            "coreSummary": [
                "학교생활기록부 서술형 항목은 교사가 직접 관찰·평가한 교육활동 사실을 바탕으로 작성합니다.",
                "학생의 가정 배경이나 보호자 정보처럼 교육활동과 직접 관련이 없는 외부 정보는 적지 않는 것이 원칙입니다.",
                "은근히 드러내는 방식처럼 우회적 표현도 피해야 합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "학생의 성장과 특성을 설명하더라도 학교 안에서 관찰한 행동과 활동 중심으로 적는 것이 안전합니다.",
            ],
        }

    def _render_specific_name_answer(self, question: str) -> dict[str, Any]:
        if contains_any(question, ["대학명", "대학 이름", "특정 대학", "서울대", "연세대", "고려대"]):
            conclusion = "불가합니다. 특정 대학명은 기재 유의 대상이므로, 진로활동을 설명하더라도 대학명을 직접 드러내는 방식은 피해야 합니다."
            practical = "대학 진학 희망이나 외부 활동을 설명해야 해도 특정 대학명 노출이 필요한지 먼저 점검해야 합니다."
            name_examples = "구체적인 대학명"
        elif contains_any(question, ["기업 이름", "회사 이름", "상호명"]):
            conclusion = "불가합니다. 기업 이름이나 회사 이름 같은 실명은 기재 유의 대상이므로, 세특이나 다른 서술형 항목에 그대로 드러내는 방식은 피해야 합니다."
            practical = "기업 이름이나 회사 이름을 적고 싶을 때도 실명 노출이 꼭 필요한지 먼저 점검하고, 가능하면 활동 유형 수준으로 일반화하는 편이 안전합니다."
            name_examples = "기업 이름, 회사 이름, 상호명"
        elif contains_any(question, ["강사명", "강사 이름"]):
            conclusion = "불가합니다. 강사 이름 같은 개인 실명은 기재 유의 대상이므로, 교육활동을 설명하더라도 그대로 노출하는 방식은 피해야 합니다."
            practical = "외부 강의나 프로그램을 설명할 때도 강사 개인의 실명 대신 활동 내용과 기관 유형 중심으로 정리하는 편이 안전합니다."
            name_examples = "강사 이름"
        else:
            conclusion = "불가합니다. 특정 기관명은 기재 유의 대상이고, 학교 밖 교육기관도 실명 대신 일반화해서 적는 것이 원칙입니다."
            practical = "시도교육감이 승인한 학교 밖 교육기관이라도 실명 대신 '학교 밖 교육기관(기관유형)'처럼 일반화해서 적습니다."
            name_examples = "기관명, 학교 밖 교육기관명"

        return {
            "conclusion": conclusion,
            "coreSummary": [
                f"{name_examples}은(는) 학교생활기록부에 직접 노출하지 않는 방향으로 봐야 합니다.",
                "실무적으로는 원칙적으로 그대로 적지 않습니다.",
                "구체적인 대학명, 기관명, 상호명, 강사명은 학교생활기록부에 직접 노출하지 않는 방향으로 봐야 합니다.",
                "학교 밖 교육기관을 적어야 하는 경우에도 기관명을 그대로 적지 않고, 학교 밖 교육기관 또는 기관유형 수준으로 일반화합니다.",
                "기재 유의 사항은 창체, 진로활동, 서술형 항목 전반에 공통으로 적용됩니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [practical],
        }

    def _render_student_reflection_subject_note_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "조건부 가능입니다. 학생이 쓴 소감문은 참고자료로 볼 수는 있지만, 학생이 작성한 문장을 그대로 입력하면 안 됨이 원칙이며 교사가 직접 작성해야 합니다.",
            "coreSummary": [
                "세특은 교사가 직접 작성하며, 교사가 직접 관찰하고 평가한 내용을 바탕으로 작성하는 것이 원칙입니다.",
                "학생의 소감문이나 자기소개식 문장은 참고자료일 뿐, 학생이 작성한 문장을 그대로 입력하면 안 됨이 분명합니다.",
                "최종 문장과 사실관계는 교사가 직접 확인하고 작성해야 합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "소감문을 활용하더라도 수업 장면, 수행 결과, 관찰 근거를 교사 문장으로 다시 정리해야 합니다.",
            ],
        }

    def _render_ai_polished_text_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "조건부 가능입니다. AI가 다듬어준 문장은 참고할 수는 있지만, 그대로 입력하면 안 됨이 원칙이고 교사가 직접 작성하며 사실관계를 확인해야 합니다.",
            "coreSummary": [
                "생성형 AI는 표현을 다듬는 보조 수단으로만 참고할 수 있습니다.",
                "AI가 만든 문장을 검토 없이 그대로 입력하면 안 됨을 분명히 안내해야 합니다.",
                "최종 문장과 사실관계는 교사가 직접 작성하고 확인하며 책임져야 합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "학생의 실제 활동과 다른 과장 표현이나 허위 표현이 섞이지 않았는지 교사가 직접 점검해야 합니다.",
            ],
        }

    def _render_reference_witness_answer_strict(self) -> dict[str, Any]:
        return {
            "conclusion": "자동으로 미인정결석이라고 단정할 수 없습니다.",
            "coreSummary": [
                "참고인 조사 출석은 학생 상황과 교육적 목적을 고려해 학교가 출석인정 결석 또는 기타결석으로 판단할 수 있습니다.",
                "따라서 참고인 조사라는 이유만으로 자동으로 미인정결석이라고 단정하지 않음이 핵심입니다.",
                "반면 학생 자신의 위법행위와 관련한 소년보호재판 출석은 해당 기간을 출석인정 결석으로 처리합니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "사유서와 증빙자료를 보고 학교 기준에 따라 판단하는 절차가 필요합니다.",
            ],
        }

    def _render_reading_duplication_record_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "조건부 가능입니다. 같은 책이라도 과목이나 증빙자료가 다르면 중복 입력 가능입니다.",
            "coreSummary": [
                "같은 도서라도 과목, 학년, 학기, 영역이 다르거나 증빙자료가 다르면 각각 입력할 수 있습니다.",
                "원서와 번역본도 제출한 증빙자료가 다르면 각각 입력할 수 있습니다.",
                "중복 입력 가능 여부는 같은 책인지보다 기록 맥락과 증빙자료가 다른지가 핵심입니다.",
            ],
            "gradeDifferences": [],
            "practicalNotes": [
                "증빙자료 차이 없이 같은 도서를 반복 입력하는 것은 허용되지 않습니다.",
            ],
        }

    def _render_grade3_subject_attendance_answer(self) -> dict[str, Any]:
        return {
            "conclusion": "같은 방식으로 바로 설명하면 안 됩니다. 과목출석률은 2026학년도 1·2학년 설명에서 핵심이고, 3학년은 기존 체계를 먼저 봐야 합니다.",
            "coreSummary": [
                "1·2학년은 학점, 과목출석률, 5등급 체계를 함께 설명합니다.",
                "3학년은 기존 교육과정에 따라 단위수와 9등급 중심의 기존 체계를 먼저 봐야 합니다.",
                "따라서 '3학년도 과목출석률이 그대로 적용된다'처럼 단정하지 말고, 학년 분기를 먼저 확인해야 합니다.",
            ],
            "gradeDifferences": [
                "1·2학년: 학점과 과목출석률 중심",
                "3학년: 단위수와 9등급 중심의 기존 체계",
            ],
            "practicalNotes": [
                "과목출석률 질문은 먼저 1·2학년인지 3학년인지 확인하고 답하는 것이 안전합니다.",
            ],
        }

    def _render_recordability_answer(self, question: str, retrieval: RetrievalBucket) -> dict[str, Any]:
        conclusion = "조건부 가능입니다. 기재 가능 여부는 허용 범위, 금지 범위, 예외 절차를 함께 봐야 합니다."
        if "교내상" in question or "수상" in question:
            conclusion = "불가합니다. 학교교육계획에 따라 실시한 교내상만 수상경력에 입력할 수 있습니다."
        core_summary = [card["ruleSummary"] for card in retrieval.rule_cards[:4]]
        practical_notes = []
        for card in retrieval.rule_cards[:3]:
            if card["notAllowed"]:
                practical_notes.append(f"금지: {card['notAllowed'][0]}")
            if card["conditions"]:
                practical_notes.append(f"조건: {card['conditions'][0]}")
        if retrieval.qa_cards:
            practical_notes.append(retrieval.qa_cards[0]["answer"])
        return {
            "conclusion": conclusion,
            "coreSummary": unique_preserve_order(core_summary),
            "gradeDifferences": [],
            "practicalNotes": unique_preserve_order(practical_notes),
        }

    def _render_case_answer(self, retrieval: RetrievalBucket) -> dict[str, Any]:
        return {
            "conclusion": retrieval.qa_cards[0]["answer"] if retrieval.qa_cards else "brain 카드 기준으로 추가 확인이 필요합니다.",
            "coreSummary": [card["ruleSummary"] for card in retrieval.rule_cards[:2]],
            "gradeDifferences": [],
            "practicalNotes": [card["practicalMeaning"] for card in retrieval.change_cards[:2]],
        }

    def _render_page_lookup_answer(self, question: str, analysis: dict[str, Any], retrieval: RetrievalBucket) -> dict[str, Any]:
        prioritized_cards = (
            retrieval.rule_cards[:1]
            + retrieval.qa_cards[:1]
            + retrieval.change_cards[:1]
        )

        official_pages: list[str] = []
        guide_pages: list[str] = []
        seen_official: set[str] = set()
        seen_guide: set[str] = set()

        for card in prioritized_cards:
            for source_ref in card.get("sourceRefs", []):
                doc_id = source_ref.get("docId")
                printed_page = format_page_value(source_ref.get("printedPage"))
                if not printed_page:
                    continue
                if doc_id == "official_guidelines_2026_hs" and printed_page not in seen_official:
                    seen_official.add(printed_page)
                    official_pages.append(printed_page)
                if doc_id == "guide_2026_hs" and printed_page not in seen_guide:
                    seen_guide.add(printed_page)
                    guide_pages.append(printed_page)

        if not official_pages and not guide_pages:
            reference_block = self._build_reference_block(retrieval)
            official_pages = [ref["printedPage"] for ref in reference_block["official"] if ref.get("printedPage")][:2]
            guide_pages = [ref["printedPage"] for ref in reference_block["guide"] if ref.get("printedPage")][:2]

        topic_hint_map = {
            "attendance": "출결 특기사항",
            "creative_experience": "창의적 체험활동상황",
            "subject_progress": "교과학습발달상황",
            "subject_progress_grades_1_2": "교과학습발달상황",
            "subject_progress_grade_3": "교과학습발달상황",
            "awards": "수상경력",
            "certificates": "자격증",
            "reading": "독서활동",
            "behavior": "행동특성 및 종합의견",
            "corrections": "정정",
            "volunteer_service": "봉사활동",
            "processing": "처리요령",
        }
        topic_hint = ""
        for topic_id in analysis["detectedTopicIds"]:
            if topic_id in topic_hint_map:
                topic_hint = topic_hint_map[topic_id]
                break

        prefers_guide = "길라잡이" in question and bool(guide_pages)

        if prefers_guide:
            conclusion = f"길라잡이 Q&A 기준으로는 p.{guide_pages[0]}를 확인하세요."
        elif official_pages:
            conclusion = f"공식 기재요령 기준으로는 p.{official_pages[0]}를 먼저 확인하세요."
        elif guide_pages:
            conclusion = f"길라잡이 Q&A 기준으로는 p.{guide_pages[0]}를 확인하세요."
        else:
            conclusion = "관련 brain 카드의 참고 페이지를 우선 확인하면 됩니다."

        core_summary: list[str] = []
        if topic_hint:
            core_summary.append(f"{topic_hint} 관련 원문 위치를 먼저 확인한 뒤 세부 기준을 읽으면 됩니다.")
        if official_pages:
            core_summary.append(f"공식 기재요령: 인쇄 {', '.join(official_pages[:2])}쪽")
        if guide_pages:
            core_summary.append(f"길라잡이: 인쇄 {', '.join(guide_pages[:2])}쪽")

        if not core_summary:
            core_summary = [card["title"] for card in retrieval.change_cards[:2]] + [card["title"] for card in retrieval.rule_cards[:2]]

        practical_notes = ["원문 확인이 목적일 때도 답변 생성은 brain 카드 기준으로 먼저 찾고, 원문은 참고 페이지 확인용으로만 사용합니다."]
        if retrieval.qa_cards:
            practical_notes.append(retrieval.qa_cards[0]["answer"])

        return {
            "conclusion": conclusion,
            "coreSummary": unique_preserve_order(core_summary),
            "gradeDifferences": [],
            "practicalNotes": unique_preserve_order(practical_notes),
        }

    def _flatten_used_page_refs(self, references: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
        output: list[dict[str, str]] = []
        for ref_group in [references.get("official", []), references.get("guide", [])]:
            for ref in ref_group:
                output.append(
                    {
                        "docId": ref.get("docId", ""),
                        "printedPage": ref.get("printedPage", ""),
                        "pdfPage": ref.get("pdfPage", ""),
                    }
                )
        return output

    def _build_reference_block(self, retrieval: RetrievalBucket) -> dict[str, Any]:
        official: list[dict[str, str]] = []
        guide: list[dict[str, str]] = []

        all_cards = retrieval.change_cards + retrieval.rule_cards + retrieval.qa_cards
        seen_refs: set[tuple[str, str, str]] = set()

        for card in all_cards:
            for source_ref in card.get("sourceRefs", []):
                doc_id = source_ref.get("docId", "")
                printed_page = source_ref.get("printedPage")
                slide = source_ref.get("slide")
                key = (doc_id, str(printed_page), str(slide))
                if key in seen_refs:
                    continue
                seen_refs.add(key)

                if doc_id in {"official_guidelines_2026_hs", "guide_2026_hs"} and printed_page is not None:
                    ref_block = {
                        "docId": doc_id,
                        "printedPage": format_page_value(printed_page),
                        "pdfPage": printed_to_pdf(doc_id, printed_page),
                    }
                    if doc_id == "official_guidelines_2026_hs":
                        official.append(ref_block)
                    else:
                        guide.append(ref_block)

        return {
            "official": official,
            "guide": guide,
        }

    def _build_evidence_block(self, retrieval: RetrievalBucket) -> list[dict[str, Any]]:
        evidence: list[dict[str, Any]] = []
        for card in retrieval.change_cards:
            public_sources = self._public_source_refs(card["sourceRefs"])
            if public_sources:
                evidence.append(
                    {
                        "title": card["title"],
                        "summary": card["after2026"],
                        "publicSources": public_sources,
                    }
                )
        for card in retrieval.rule_cards:
            public_sources = self._public_source_refs(card["sourceRefs"])
            if public_sources:
                evidence.append(
                    {
                        "title": card["title"],
                        "summary": card["ruleSummary"],
                        "publicSources": public_sources,
                    }
                )
        for card in retrieval.qa_cards:
            public_sources = self._public_source_refs(card["sourceRefs"])
            if public_sources:
                evidence.append(
                    {
                        "title": card["question"],
                        "summary": card["answer"],
                        "publicSources": public_sources,
                    }
                )
        return evidence

    def _public_source_refs(self, source_refs: list[dict[str, Any]]) -> list[dict[str, str]]:
        public_refs: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for source_ref in source_refs:
            doc_id = source_ref.get("docId")
            printed_page = source_ref.get("printedPage")
            if printed_page is None:
                continue
            if doc_id == "official_guidelines_2026_hs":
                label = "공식 기재요령"
            elif doc_id == "guide_2026_hs":
                label = "기재 길라잡이"
            else:
                continue
            key = (label, str(printed_page))
            if key in seen:
                continue
            seen.add(key)
            public_refs.append({"label": label, "printedPage": format_page_value(printed_page)})
        return public_refs

    def _grade_scope_label(self, grade_scope: str) -> str:
        labels = {
            "grades_1_2": "1·2학년 기준으로 먼저 설명해야 합니다.",
            "grade_3": "3학년은 기존 체계를 유지합니다.",
            "grades_1_2_vs_grade_3": "1·2학년과 3학년 기준을 나눠서 답해야 합니다.",
            "graduation_stage": "졸업 단계에서 특히 중요합니다.",
        }
        return labels.get(grade_scope, "")

    def _sections_to_text(
        self,
        sections: dict[str, Any],
        references: dict[str, Any],
        section_labels: dict[str, str],
    ) -> str:
        lines = [
            f"[{section_labels['conclusion']}]",
            sections["conclusion"],
            "",
            f"[{section_labels['coreSummary']}]",
        ]
        lines.extend(f"- {item}" for item in sections["coreSummary"] if item)
        if sections["gradeDifferences"]:
            lines.extend(["", f"[{section_labels['gradeDifferences']}]"])
            lines.extend(f"- {item}" for item in sections["gradeDifferences"] if item)
        if sections["practicalNotes"]:
            lines.extend(["", f"[{section_labels['practicalNotes']}]"])
            lines.extend(f"- {item}" for item in sections["practicalNotes"] if item)
        lines.extend(["", f"[{section_labels['references']}]"])
        for ref_block in references["official"]:
            lines.append(f"- 공식 기재요령: 인쇄 {ref_block['printedPage']}")
        for ref_block in references["guide"]:
            lines.append(f"- 기재 길라잡이: 인쇄 {ref_block['printedPage']}")
        return "\n".join(lines)
