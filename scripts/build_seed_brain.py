from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRAIN_DIR = ROOT / "brain"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(json.dumps(record, ensure_ascii=False) for record in records)
    path.write_text(body + ("\n" if body else ""), encoding="utf-8")


def build_document_map() -> dict:
    return {
        "schemaVersion": "2026-06-17.seed.v1",
        "project": "2026학년도 고등학교 학교생활기록부 기재요령 Q&A 봇",
        "brainPolicy": {
            "primaryKnowledgeSource": "brain 폴더의 JSON/JSONL",
            "rawSourceRole": "원문 PDF/PPT는 최종 근거 확인과 페이지 검증용",
            "sourcePriority": [
                "official_guidelines_2026_hs",
                "guide_2026_hs",
                "changes_ppt_2026_hs",
                "training_ppt_2026_hs",
            ],
            "conflictResolution": "brain 카드와 원문이 충돌하면 공식 기재요령을 기준으로 brain 데이터를 재검토한다.",
            "botAnswerRule": "답변 초안은 brain 카드로 만들고, 필요 시 원문 페이지를 다시 찾아 근거를 덧붙인다.",
        },
        "documents": [
            {
                "docId": "official_guidelines_2026_hs",
                "title": "2026학년도 학교생활기록부 기재요령(고등학교)",
                "kind": "pdf",
                "role": "최우선 기준 문서",
                "priority": 1,
                "trustLevel": "authoritative",
                "usedFor": [
                    "현행 기재 기준 확정",
                    "페이지 근거 확인",
                    "규칙 카드 최종 검증",
                ],
                "searchPatterns": [
                    "서울특별시교육청 학생역량·혁신교육과_2026 학교생활기록부 기재요령(고등학교).pdf",
                    "*2026*학교생활기록부*기재요령*고등학교*.pdf",
                    "2026 학교생활기록부 기재요령(고).pdf",
                ],
                "citationLabel": "공식 기재요령",
                "pageSystem": {
                    "screenLabel": "PDF 화면상 페이지",
                    "printedLabel": "문서 인쇄 쪽수",
                    "note": "본문 기준으로 대체로 pdf 화면상 페이지 = 인쇄 쪽수 + 6",
                },
            },
            {
                "docId": "guide_2026_hs",
                "title": "2026학년도 학교생활기록부 기재 길라잡이(고등학교)",
                "kind": "pdf",
                "role": "보조 참고자료 및 Q&A 원천",
                "priority": 2,
                "trustLevel": "supporting",
                "usedFor": [
                    "Q&A 카드 작성",
                    "현장 해석 보조",
                    "최근 변경사항 비교표 보조 확인",
                ],
                "searchPatterns": [
                    "2026학년도 학교생활기록부 기재 길라잡이(고등학교).pdf",
                    "*2026*학교생활기록부*기재 길라잡이*고등학교*.pdf",
                ],
                "citationLabel": "기재 길라잡이",
                "pageSystem": {
                    "screenLabel": "PDF 화면상 페이지",
                    "printedLabel": "문서 인쇄 쪽수",
                    "note": "이 파일은 화면상 페이지와 인쇄 쪽수가 거의 일치한다.",
                },
            },
            {
                "docId": "changes_ppt_2026_hs",
                "title": "2026 학교생활기록부 기재요령 주요 개정사항 안내(고등학교)",
                "kind": "pptx",
                "role": "2025 대비 2026 변경사항 추출",
                "priority": 3,
                "trustLevel": "supporting",
                "usedFor": [
                    "변경사항 카탈로그 초안",
                    "전년도 대비 before/after 비교",
                ],
                "searchPatterns": [
                    "2026 학교생활기록부 기재요령 주요 개정사항_고등_F_260218.pptx",
                    "*2026*학교생활기록부*주요 개정사항*.pptx",
                ],
                "citationLabel": "주요 개정사항 PPT",
            },
            {
                "docId": "training_ppt_2026_hs",
                "title": "2026 학교생활기록부 연수 자료",
                "kind": "pptx",
                "role": "평가·기록 맥락 보조",
                "priority": 4,
                "trustLevel": "contextual",
                "usedFor": [
                    "용어 변화 맥락 파악",
                    "학생평가·기록 연계 설명 보조",
                ],
                "searchPatterns": [
                    "2026 학교생활기록부 연수(성북강북교육지원청).pptx",
                    "*2026*학교생활기록부*연수*.pptx",
                ],
                "citationLabel": "연수자료 PPT",
            },
        ],
    }


def build_topic_taxonomy() -> dict:
    return {
        "schemaVersion": "2026-06-17.seed.v1",
        "note": "주요 토픽은 공식 기재요령의 목차와 길라잡이의 변경사항/Q&A 목차를 함께 반영한다.",
        "topics": [
            {
                "topicId": "processing",
                "label": "처리요령",
                "parentTopicId": None,
                "officialPageRanges": [
                    {"printedStart": 27, "printedEnd": 31, "pdfStart": 33, "pdfEnd": 37}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 9, "printedEnd": 9, "pdfStart": 9, "pdfEnd": 9}
                ],
                "guideQaPageRanges": [
                    {"printedStart": 92, "printedEnd": 93, "pdfStart": 92, "pdfEnd": 93}
                ],
                "keywords": ["처리요령", "한글", "영문", "영어", "한자", "작성 유의사항"],
                "gradeSensitive": False,
            },
            {
                "topicId": "personal_school_status",
                "label": "인적·학적사항",
                "parentTopicId": None,
                "officialPageRanges": [
                    {"printedStart": 32, "printedEnd": 46, "pdfStart": 38, "pdfEnd": 52}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 11, "printedEnd": 14, "pdfStart": 11, "pdfEnd": 14}
                ],
                "guideQaPageRanges": [
                    {"printedStart": 94, "printedEnd": 105, "pdfStart": 94, "pdfEnd": 105}
                ],
                "keywords": ["학적", "전입", "전출", "재입학", "복학", "외국인등록번호", "국내거소신고번호"],
                "gradeSensitive": False,
            },
            {
                "topicId": "attendance",
                "label": "출결상황",
                "parentTopicId": None,
                "officialPageRanges": [
                    {"printedStart": 47, "printedEnd": 60, "pdfStart": 53, "pdfEnd": 66}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 15, "printedEnd": 23, "pdfStart": 15, "pdfEnd": 23}
                ],
                "guideQaPageRanges": [
                    {"printedStart": 106, "printedEnd": 122, "pdfStart": 106, "pdfEnd": 122}
                ],
                "keywords": ["출결", "결석", "지각", "조퇴", "결과", "개근", "장기결석", "과목출석률"],
                "gradeSensitive": True,
            },
            {
                "topicId": "awards",
                "label": "수상경력",
                "parentTopicId": None,
                "officialPageRanges": [
                    {"printedStart": 61, "printedEnd": 65, "pdfStart": 67, "pdfEnd": 71}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 24, "printedEnd": 24, "pdfStart": 24, "pdfEnd": 24}
                ],
                "guideQaPageRanges": [
                    {"printedStart": 123, "printedEnd": 123, "pdfStart": 123, "pdfEnd": 123}
                ],
                "keywords": ["수상경력", "교내상", "대회", "시상 계획", "수상 실적"],
                "gradeSensitive": False,
            },
            {
                "topicId": "certificates",
                "label": "자격증 취득 및 국가직무능력표준 이수상황",
                "parentTopicId": None,
                "officialPageRanges": [
                    {"printedStart": 66, "printedEnd": 71, "pdfStart": 72, "pdfEnd": 77}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 24, "printedEnd": 25, "pdfStart": 24, "pdfEnd": 25}
                ],
                "guideQaPageRanges": [],
                "keywords": ["자격증", "국가기술자격", "국가자격", "국가공인 민간자격증", "NCS"],
                "gradeSensitive": False,
            },
            {
                "topicId": "school_violence",
                "label": "학교폭력 조치상황 관리",
                "parentTopicId": None,
                "officialPageRanges": [
                    {"printedStart": 72, "printedEnd": 76, "pdfStart": 78, "pdfEnd": 82}
                ],
                "guideChangePageRanges": [],
                "guideQaPageRanges": [
                    {"printedStart": 124, "printedEnd": 124, "pdfStart": 124, "pdfEnd": 124}
                ],
                "keywords": ["학교폭력", "조치사항", "기재유보", "출석정지", "전학"],
                "gradeSensitive": False,
            },
            {
                "topicId": "creative_experience",
                "label": "창의적 체험활동상황",
                "parentTopicId": None,
                "officialPageRanges": [
                    {"printedStart": 77, "printedEnd": 90, "pdfStart": 83, "pdfEnd": 96}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 26, "printedEnd": 34, "pdfStart": 26, "pdfEnd": 34}
                ],
                "guideQaPageRanges": [
                    {"printedStart": 125, "printedEnd": 138, "pdfStart": 125, "pdfEnd": 138}
                ],
                "keywords": ["창체", "창의적 체험활동", "자율·자치활동", "동아리활동", "진로활동", "누가기록"],
                "gradeSensitive": True,
                "childrenTopicIds": ["volunteer_service"],
            },
            {
                "topicId": "volunteer_service",
                "label": "봉사활동",
                "parentTopicId": "creative_experience",
                "officialPageRanges": [
                    {"printedStart": 87, "printedEnd": 90, "pdfStart": 93, "pdfEnd": 96}
                ],
                "guideChangePageRanges": [],
                "guideQaPageRanges": [
                    {"printedStart": 125, "printedEnd": 138, "pdfStart": 125, "pdfEnd": 138}
                ],
                "keywords": ["봉사활동", "봉사활동 실적", "1365", "VMS", "DOVOL", "헌혈"],
                "gradeSensitive": True,
            },
            {
                "topicId": "daily_life_activity",
                "label": "일상생활 활동상황",
                "parentTopicId": None,
                "officialPageRanges": [
                    {"printedStart": 91, "printedEnd": 92, "pdfStart": 97, "pdfEnd": 98}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 35, "printedEnd": 35, "pdfStart": 35, "pdfEnd": 35}
                ],
                "guideQaPageRanges": [
                    {"printedStart": 139, "printedEnd": 139, "pdfStart": 139, "pdfEnd": 139}
                ],
                "keywords": ["일상생활 활동상황", "학교폭력 피해학생", "특기사항"],
                "gradeSensitive": False,
            },
            {
                "topicId": "subject_progress",
                "label": "교과학습발달상황",
                "parentTopicId": None,
                "officialPageRanges": [
                    {"printedStart": 93, "printedEnd": 155, "pdfStart": 99, "pdfEnd": 161}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 36, "printedEnd": 67, "pdfStart": 36, "pdfEnd": 67}
                ],
                "guideQaPageRanges": [
                    {"printedStart": 140, "printedEnd": 151, "pdfStart": 140, "pdfEnd": 151}
                ],
                "keywords": ["교과학습발달상황", "세특", "과목별 세부능력 및 특기사항", "학점", "단위수", "성취도", "석차등급"],
                "gradeSensitive": True,
                "childrenTopicIds": ["subject_progress_grades_1_2", "subject_progress_grade_3"],
            },
            {
                "topicId": "subject_progress_grades_1_2",
                "label": "교과학습발달상황(1·2학년)",
                "parentTopicId": "subject_progress",
                "officialPageRanges": [
                    {"printedStart": 93, "printedEnd": 123, "pdfStart": 99, "pdfEnd": 129}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 36, "printedEnd": 67, "pdfStart": 36, "pdfEnd": 67}
                ],
                "guideQaPageRanges": [
                    {"printedStart": 140, "printedEnd": 151, "pdfStart": 140, "pdfEnd": 151}
                ],
                "keywords": ["1·2학년", "2022 개정 교육과정", "학점", "5등급", "과목출석률", "미이수", "대체이수", "재이수"],
                "gradeSensitive": True,
            },
            {
                "topicId": "subject_progress_grade_3",
                "label": "교과학습발달상황(3학년)",
                "parentTopicId": "subject_progress",
                "officialPageRanges": [
                    {"printedStart": 124, "printedEnd": 155, "pdfStart": 130, "pdfEnd": 161}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 36, "printedEnd": 67, "pdfStart": 36, "pdfEnd": 67}
                ],
                "guideQaPageRanges": [
                    {"printedStart": 140, "printedEnd": 151, "pdfStart": 140, "pdfEnd": 151}
                ],
                "keywords": ["3학년", "2015 개정 교육과정", "단위수", "9등급", "석차등급"],
                "gradeSensitive": True,
            },
            {
                "topicId": "reading",
                "label": "독서활동상황",
                "parentTopicId": None,
                "officialPageRanges": [
                    {"printedStart": 156, "printedEnd": 157, "pdfStart": 162, "pdfEnd": 163}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 68, "printedEnd": 68, "pdfStart": 68, "pdfEnd": 68}
                ],
                "guideQaPageRanges": [
                    {"printedStart": 152, "printedEnd": 153, "pdfStart": 152, "pdfEnd": 153}
                ],
                "keywords": ["독서", "독서활동상황", "동일 도서명", "독서 증빙자료"],
                "gradeSensitive": False,
            },
            {
                "topicId": "behavior",
                "label": "행동특성 및 종합의견",
                "parentTopicId": None,
                "officialPageRanges": [
                    {"printedStart": 158, "printedEnd": 159, "pdfStart": 164, "pdfEnd": 165}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 69, "printedEnd": 69, "pdfStart": 69, "pdfEnd": 69}
                ],
                "guideQaPageRanges": [
                    {"printedStart": 154, "printedEnd": 155, "pdfStart": 154, "pdfEnd": 155}
                ],
                "keywords": ["행특", "행동특성", "종합의견", "누가기록", "부정적 행동특성"],
                "gradeSensitive": False,
            },
            {
                "topicId": "corrections",
                "label": "자료의 정정",
                "parentTopicId": None,
                "officialPageRanges": [
                    {"printedStart": 165, "printedEnd": 171, "pdfStart": 171, "pdfEnd": 177}
                ],
                "guideChangePageRanges": [
                    {"printedStart": 70, "printedEnd": 71, "pdfStart": 70, "pdfEnd": 71}
                ],
                "guideQaPageRanges": [
                    {"printedStart": 156, "printedEnd": 159, "pdfStart": 156, "pdfEnd": 159}
                ],
                "keywords": ["정정", "정정대장", "증빙자료", "학업성적관리위원회", "과실"],
                "gradeSensitive": False,
            },
        ],
    }


def build_term_synonyms() -> dict:
    return {
        "schemaVersion": "2026-06-17.seed.v1",
        "terms": [
            {
                "canonicalTerm": "학교생활기록부",
                "aliases": ["생기부", "학생부"],
                "mapToTopicIds": [],
                "note": "가장 넓은 상위 용어",
            },
            {
                "canonicalTerm": "세부능력 및 특기사항",
                "aliases": ["세특", "교과세특", "과목별 세특"],
                "mapToTopicIds": ["subject_progress"],
                "note": "고등학교에서는 모든 학생 입력이 원칙",
            },
            {
                "canonicalTerm": "행동특성 및 종합의견",
                "aliases": ["행특", "행동특성", "종합의견"],
                "mapToTopicIds": ["behavior"],
                "note": "방과후학교 내용은 입력 불가",
            },
            {
                "canonicalTerm": "창의적 체험활동상황",
                "aliases": ["창체", "창체상황"],
                "mapToTopicIds": ["creative_experience"],
                "note": "1·2학년과 3학년 처리 차이가 크다",
            },
            {
                "canonicalTerm": "자율·자치활동",
                "aliases": ["자율활동", "자치활동"],
                "mapToTopicIds": ["creative_experience"],
                "note": "1·2학년은 2022 개정 교육과정 표현을 우선 사용",
            },
            {
                "canonicalTerm": "교과학습발달상황",
                "aliases": ["교학발", "성적", "교과 성적", "교과기록"],
                "mapToTopicIds": ["subject_progress"],
                "note": "학년 분기 강제 토픽",
            },
            {
                "canonicalTerm": "출결상황",
                "aliases": ["출결", "결석기록", "출결기록"],
                "mapToTopicIds": ["attendance"],
                "note": "과목출석률 질문은 1·2학년 분기 필요",
            },
            {
                "canonicalTerm": "수상경력",
                "aliases": ["수상", "교내상", "상장"],
                "mapToTopicIds": ["awards"],
                "note": "교내대회 참가 사실은 다른 항목에 입력 불가",
            },
            {
                "canonicalTerm": "자격증 취득 및 국가직무능력표준 이수상황",
                "aliases": ["자격증", "민간자격증", "국가기술자격", "NCS"],
                "mapToTopicIds": ["certificates"],
                "note": "입력 대상 자격증 범위 확인 필요",
            },
            {
                "canonicalTerm": "봉사활동 실적",
                "aliases": ["봉사", "봉사시간", "봉사활동"],
                "mapToTopicIds": ["volunteer_service"],
                "note": "1·2학년은 창체 연계 처리 여부를 함께 봐야 함",
            },
            {
                "canonicalTerm": "교육정보시스템",
                "aliases": ["나이스", "NEIS"],
                "mapToTopicIds": [],
                "note": "메뉴 경로와 입력 위치 설명 시 사용",
            },
            {
                "canonicalTerm": "정기시험",
                "aliases": ["지필평가", "중간고사", "기말고사"],
                "mapToTopicIds": ["subject_progress"],
                "note": "연수자료에서 용어 변경 맥락 확인 가능",
            },
            {
                "canonicalTerm": "학업성적관리위원회",
                "aliases": ["학관위"],
                "mapToTopicIds": ["subject_progress", "corrections", "attendance"],
                "note": "정정, 질병결석 사유 비공개, 성적 처리 예외에서 자주 등장",
            },
            {
                "canonicalTerm": "학교교육계획서",
                "aliases": ["학교교육계획", "시상 계획", "학교 시상 계획"],
                "mapToTopicIds": ["awards"],
                "note": "교내상 입력 가능 여부의 선행 조건",
            },
            {
                "canonicalTerm": "과목출석률",
                "aliases": ["과목별 출석률", "학점 취득 출석률"],
                "mapToTopicIds": ["attendance", "subject_progress_grades_1_2"],
                "note": "2026학년도 1·2학년 핵심 키워드",
            },
        ],
    }


def build_grade_split_rules() -> dict:
    return {
        "schemaVersion": "2026-06-17.seed.v1",
        "effectiveFrom": "2026-03-01",
        "defaultBehaviorWhenGradeUnknown": "학년이 드러나지 않으면 1·2학년과 3학년을 나눠 병렬 답변한다.",
        "disambiguationRequiredTopicIds": [
            "creative_experience",
            "volunteer_service",
            "subject_progress",
            "subject_progress_grades_1_2",
            "subject_progress_grade_3",
            "attendance",
        ],
        "cohorts": [
            {
                "cohortId": "grades_1_2_2026",
                "label": "2026학년도 고등학교 1·2학년",
                "grades": [1, 2],
                "curriculum": "2022 개정 교육과정",
                "coreFeatures": [
                    "고교학점제 적용",
                    "학점 단위 기록",
                    "과목출석률 적용",
                    "5등급 체계 질문 빈번",
                    "미이수·대체이수·재이수 설명 필요",
                    "창체는 자율·자치활동, 동아리활동, 진로활동 중심으로 설명",
                ],
                "sourceRefs": [
                    {"docId": "official_guidelines_2026_hs", "printedPage": 93},
                    {"docId": "guide_2026_hs", "printedPage": 125},
                    {"docId": "changes_ppt_2026_hs", "slide": 8},
                ],
            },
            {
                "cohortId": "grade_3_2026",
                "label": "2026학년도 고등학교 3학년",
                "grades": [3],
                "curriculum": "기존 교육과정(2015 개정 교육과정 기반)",
                "coreFeatures": [
                    "단위수 중심 기록을 우선 설명",
                    "9등급 체계 질문 빈번",
                    "기존 창체 체계와 봉사활동 영역 설명 필요",
                    "소인수 과목 13명 이하 규칙 설명 필요",
                ],
                "sourceRefs": [
                    {"docId": "official_guidelines_2026_hs", "printedPage": 124},
                    {"docId": "guide_2026_hs", "printedPage": 140},
                ],
            },
        ],
        "routingRules": [
            {
                "ruleId": "force_grade_branch_subject_progress",
                "triggerTopicIds": ["subject_progress"],
                "triggerKeywords": ["세특", "교과학습발달상황", "학점", "단위수", "석차등급", "성취도"],
                "resolution": "답변을 반드시 1·2학년 / 3학년 두 갈래로 나눈다.",
                "why": "교과 서식, 평가 체계, 학점·단위수, 석차등급 기준이 다르다.",
            },
            {
                "ruleId": "force_grade_branch_creative_experience",
                "triggerTopicIds": ["creative_experience", "volunteer_service"],
                "triggerKeywords": ["창체", "봉사활동", "자율활동", "동아리활동", "진로활동", "헌혈"],
                "resolution": "1·2학년과 3학년의 입력 위치와 설명 문구를 분리한다.",
                "why": "1·2학년은 2022 개정 교육과정 운영 맥락, 3학년은 기존 창체 체계를 따라야 한다.",
            },
            {
                "ruleId": "force_grade_branch_attendance_credit",
                "triggerTopicIds": ["attendance"],
                "triggerKeywords": ["과목출석률", "학점 취득", "개근", "수료", "장기결석"],
                "resolution": "출결 답변이 학점 취득 또는 과목 단위 출석과 연결되면 1·2학년 / 3학년을 나눠 설명한다.",
                "why": "2026학년도 1·2학년은 과목출석률이 핵심이고, 3학년은 기존 체계 설명이 우선이다.",
            },
            {
                "ruleId": "answer_with_both_branches_if_grade_missing",
                "triggerTopicIds": ["creative_experience", "volunteer_service", "subject_progress", "attendance"],
                "triggerKeywords": ["몇 명 이하", "봉사", "학점", "단위수", "석차등급"],
                "resolution": "질문에 학년이 없으면 추가 질문만 던지지 말고 두 학년군 답을 함께 제공한다.",
                "why": "사이트형 Q&A에서는 즉답성이 중요하고, 사용자도 자기 상황을 비교해 볼 수 있다.",
            },
        ],
    }


def build_change_catalog() -> list[dict]:
    return [
        {
            "changeId": "chg_2026_001_accumulation_authority",
            "topicId": "creative_experience",
            "title": "누가기록 방법 결정 주체가 학교장 중심에서 시도교육감 기준으로 이동",
            "before2025": "창의적 체험활동상황, 일상생활 활동상황, 행동특성 및 종합의견의 누가기록 여부와 방법은 학교장이 정하는 구조였다.",
            "after2026": "창의적 체험활동상황과 행동특성 및 종합의견의 누가기록 방법은 시도교육감이 정하는 체계에 따라 운영하도록 정리되었다.",
            "practicalMeaning": "학교별 임의 서식보다 시도교육청 지침과 나이스 운영 방식에 맞춘 통일적 관리가 중요해졌다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "changes_ppt_2026_hs", "slide": 3},
                {"docId": "changes_ppt_2026_hs", "slide": 4},
                {"docId": "guide_2026_hs", "printedPage": 10},
            ],
            "keywords": ["누가기록", "시도교육감", "학교장", "창체", "행특"],
        },
        {
            "changeId": "chg_2026_002_retention_definition",
            "topicId": "personal_school_status",
            "title": "유급 정의가 진급 불가뿐 아니라 졸업 요건 미충족까지 포괄",
            "before2025": "유급은 해당 학년 교육과정 미수료에 따라 상급 학년으로 진급하지 못한 경우를 중심으로 설명되었다.",
            "after2026": "유급은 해당 학년 교육과정 미수료로 진급하지 못한 경우뿐 아니라 졸업 요건을 충족하지 못한 경우까지 포괄하는 표현으로 정리되었다.",
            "practicalMeaning": "진급 실패와 졸업 요건 미충족을 같은 틀에서 설명하되, 졸업 단계 학생 상담에서는 학점 취득 여부를 별도로 점검해야 한다.",
            "gradeScope": "all_grades_emphasis_graduation_stage",
            "sourceRefs": [
                {"docId": "changes_ppt_2026_hs", "slide": 5}
            ],
            "keywords": ["유급", "진급", "졸업요건", "학적"],
        },
        {
            "changeId": "chg_2026_003_graduation_deferral",
            "topicId": "subject_progress",
            "title": "졸업유예 개념이 학점 미충족 중심으로 명확화",
            "before2025": "출석일수는 충족했지만 졸업 학점을 채우지 못한 상황을 설명하는 용어가 지금처럼 분명하게 정리되어 있지 않았다.",
            "after2026": "졸업유예는 출석일수는 충족했으나 졸업에 필요한 학점을 모두 취득하지 못해 졸업 자격을 얻지 못한 상태로 명확히 설명된다.",
            "practicalMeaning": "결석 문제와 학점 미충족 문제를 구분해서 상담해야 하며, 졸업 가능성 안내의 기준이 더 명확해졌다.",
            "gradeScope": "grade_3_and_graduation_stage",
            "sourceRefs": [
                {"docId": "changes_ppt_2026_hs", "slide": 6},
                {"docId": "changes_ppt_2026_hs", "slide": 7},
            ],
            "keywords": ["졸업유예", "학점", "졸업", "출석일수"],
        },
        {
            "changeId": "chg_2026_004_subject_attendance_rate",
            "topicId": "attendance",
            "title": "과목출석률 기준이 1학점당 16회 기준에서 실제 수업 횟수 기준으로 변경",
            "before2025": "과목출석률은 1학점당 수업량 16회의 3분의 2 이상 출석 기준으로 안내되었다.",
            "after2026": "과목출석률은 실제 운영한 수업 횟수의 3분의 2 이상 출석 기준으로 안내된다.",
            "practicalMeaning": "블록타임, 공동교육과정, 운영 횟수 조정이 있는 과목은 실제 수업 횟수 기준으로 출결을 계산해야 한다.",
            "gradeScope": "grades_1_2",
            "sourceRefs": [
                {"docId": "changes_ppt_2026_hs", "slide": 8}
            ],
            "keywords": ["과목출석률", "학점", "출결", "1·2학년"],
        },
        {
            "changeId": "chg_2026_005_attendance_notes",
            "topicId": "attendance",
            "title": "출결 특기사항 입력 기준이 장기결석·기타결석·단기결석·지각조퇴결과 중심으로 재구성",
            "before2025": "기타결석은 1일이라도 사유를 입력하고, 질병·미인정 결석은 필요한 경우 사유를 입력할 수 있도록 설명되었다.",
            "after2026": "장기결석은 결석 종류별 사유를 입력하고, 기타결석은 1일이라도 입력하며, 단기결석은 누계하여 주된 사유를 입력할 수 있고, 지각·조퇴·결과는 원칙적으로 입력하지 않되 횟수가 많으면 사유를 입력할 수 있도록 정리되었다.",
            "practicalMeaning": "학교는 장기결석 기준과 지각·조퇴·결과 입력 기준을 학교 규정으로 미리 정해 두어야 한다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "changes_ppt_2026_hs", "slide": 9},
                {"docId": "changes_ppt_2026_hs", "slide": 10},
            ],
            "keywords": ["장기결석", "기타결석", "단기결석", "지각", "조퇴", "결과"],
        },
        {
            "changeId": "chg_2026_006_perfect_attendance",
            "topicId": "attendance",
            "title": "개근 입력 예외와 합산 기준이 구체화",
            "before2025": "해당 학년에 결석·지각·조퇴·결과가 없으면 시스템 마감 시 개근을 입력하는 설명이 중심이었다.",
            "after2026": "중도 입학·편입, 재입학 전후 출결 합산, 순회교육학생·건강장애학생 등 개근 입력 예외와 판단 기준이 구체화되었다.",
            "practicalMeaning": "전입생, 재입학생, 특수 상황 학생은 시스템 자동 처리만 믿지 말고 사람이 최종 점검해야 한다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "changes_ppt_2026_hs", "slide": 11}
            ],
            "keywords": ["개근", "전입", "재입학", "건강장애학생", "순회교육"],
        },
        {
            "changeId": "chg_2026_007_award_plan",
            "topicId": "awards",
            "title": "교내상 입력 가능 여부를 학교교육계획서와 2학기 초 변경 공개 여부로 재정리",
            "before2025": "학년 초 학교교육계획에 따라 실시한 교내상만 입력할 수 있다고 안내되었다.",
            "after2026": "학년 초 학교교육계획서에 연간 대회 및 수상내용 등의 실시계획을 기재하고, 불가피한 경우 2학기 초 30일 이내 변경계획을 공개한 경우에만 그 실적을 입력할 수 있도록 정리되었다.",
            "practicalMeaning": "교내상 입력 전에는 시상 자체보다도 계획서 반영 여부와 공개 절차 이행 여부를 먼저 확인해야 한다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "changes_ppt_2026_hs", "slide": 12},
                {"docId": "guide_2026_hs", "printedPage": 123},
            ],
            "keywords": ["교내상", "학교교육계획서", "2학기 초", "변경계획"],
        },
        {
            "changeId": "chg_2026_008_certificate_scope",
            "topicId": "certificates",
            "title": "국가공인 민간자격증 기준이 기술 관련 여부에서 교육부장관 지정 여부로 이동",
            "before2025": "국가공인 민간자격증은 기술 관련 자격증에 한해 입력할 수 있도록 설명되었다.",
            "after2026": "국가공인 민간자격증 중 교육부장관이 정한 자격증만 입력할 수 있도록 기준이 바뀌었다.",
            "practicalMeaning": "기술 관련이라는 이유만으로 입력하지 말고, 교육부장관 지정 여부와 공인 유효기간을 함께 점검해야 한다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "changes_ppt_2026_hs", "slide": 13},
                {"docId": "changes_ppt_2026_hs", "slide": 14},
            ],
            "keywords": ["자격증", "국가공인 민간자격증", "교육부장관", "공인기간"],
        },
        {
            "changeId": "chg_2026_009_creative_record_form",
            "topicId": "creative_experience",
            "title": "창체 누가기록은 나이스 서식 또는 학교 자체 서식을 근거자료와 함께 활용 가능",
            "before2025": "영역별 누가기록은 공정성 등을 확보한 서식을 개발하여 활용하도록 설명되었다.",
            "after2026": "교육정보시스템 서식 또는 자체 개발한 서식 등을 활용하되, 학생의 구체적 활동 내용이 포함된 자료를 바탕으로 작성·관리할 수 있다고 정리되었다.",
            "practicalMeaning": "학교가 자체 누가기록 서식을 쓰더라도 학생 활동 근거자료와 나이스 반영 구조를 함께 관리해야 한다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "changes_ppt_2026_hs", "slide": 15}
            ],
            "keywords": ["창체", "누가기록", "서식", "근거자료"],
        },
    ]


def build_rule_cards() -> list[dict]:
    return [
        {
            "ruleId": "rule_teacher_owns_descriptive_items",
            "topicId": "processing",
            "ruleSummary": "서술형 항목의 작성 책임은 교사에게 있다.",
            "allowed": [
                "교사가 평소 직접 관찰·평가한 내용을 바탕으로 서술형 항목을 작성한다."
            ],
            "notAllowed": [
                "학생이 직접 써서 제출한 문장을 그대로 입력하는 것",
                "사실과 다른 내용이나 과장된 표현을 입력하는 것",
                "AI가 생성한 문장을 검토 없이 그대로 입력하는 것",
            ],
            "conditions": [
                "생성형 AI를 보조 수단으로 참고했더라도 최종 문장과 사실관계는 교사가 직접 확인해야 한다."
            ],
            "schoolRuleNeeded": False,
            "committeeNeeded": False,
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "changes_ppt_2026_hs", "slide": 2}
            ],
            "keywords": ["서술형 항목", "학생 작성", "AI", "허위", "과장"],
        },
        {
            "ruleId": "rule_awards_only_in_awards_section",
            "topicId": "awards",
            "ruleSummary": "교내상은 수상경력 항목에서만 다룬다.",
            "allowed": [
                "학년 초 학교교육계획서에 반영된 교내상만 수상경력 항목에 입력할 수 있다."
            ],
            "notAllowed": [
                "교내대회 준비 과정, 참가 사실, 성적 및 수상 실적을 수상경력 이외 항목에 입력하는 것",
                "학교 시상 계획에 없는 교내 행사 수상을 수상경력에 입력하는 것",
            ],
            "conditions": [
                "교육목표상 불가피한 경우에는 2학기 초 30일 이내 변경계획을 공개하고 그 실적만 입력할 수 있다."
            ],
            "schoolRuleNeeded": True,
            "committeeNeeded": False,
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "official_guidelines_2026_hs", "printedPage": 61},
                {"docId": "guide_2026_hs", "printedPage": 123},
            ],
            "keywords": ["교내상", "수상경력", "학교교육계획서", "대회 참가"],
        },
        {
            "ruleId": "rule_english_only_when_unavoidable",
            "topicId": "processing",
            "ruleSummary": "학교생활기록부 문자는 한글이 원칙이며 부득이한 경우에만 영문을 사용한다.",
            "allowed": [
                "외국인 성명, 도로명 주소의 영문, 일반화된 영문 약어, 고유명사, 단위 등은 부득이한 경우 영문 입력 가능",
            ],
            "notAllowed": [
                "한자 입력",
                "다른 외국어 표기",
            ],
            "conditions": [
                "누구나 이해하기 쉬운 표현이라는 원칙을 해치지 않아야 한다."
            ],
            "schoolRuleNeeded": False,
            "committeeNeeded": False,
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "official_guidelines_2026_hs", "printedPage": 28},
                {"docId": "guide_2026_hs", "printedPage": 92},
            ],
            "keywords": ["영문", "한자", "외국어", "표기"],
        },
        {
            "ruleId": "rule_long_absence_special_note",
            "topicId": "attendance",
            "ruleSummary": "출결 특기사항은 장기결석과 빈도 높은 지각·조퇴·결과를 중심으로 입력한다.",
            "allowed": [
                "장기결석은 결석 종류별 사유를 입력한다.",
                "기타결석은 1일이라도 사유를 입력한다.",
                "단기결석은 횟수가 많을 경우 누계하여 주된 사유를 입력할 수 있다.",
                "지각·조퇴·결과는 원칙적으로 입력하지 않지만 횟수가 많으면 사유를 입력할 수 있다.",
            ],
            "notAllowed": [
                "출석인정 결석 사유를 일반적으로 특기사항에 입력하는 것",
                "개인정보 보호가 필요한 질병명을 무심사로 공개하는 것",
            ],
            "conditions": [
                "장기결석 기준은 7일 내외 범위에서 학교장이 정한다.",
                "질병결석 사유를 입력하지 않을 필요가 있으면 학업성적관리위원회 심의를 거친다.",
            ],
            "schoolRuleNeeded": True,
            "committeeNeeded": True,
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "changes_ppt_2026_hs", "slide": 9},
                {"docId": "changes_ppt_2026_hs", "slide": 10},
            ],
            "keywords": ["장기결석", "특기사항", "학교장", "학업성적관리위원회"],
        },
        {
            "ruleId": "rule_perfect_attendance_exceptions",
            "topicId": "attendance",
            "ruleSummary": "개근은 무결석만으로 자동 입력하지 말고 예외 대상을 확인해야 한다.",
            "allowed": [
                "해당 학년 동안 결석·지각·조퇴·결과가 전혀 없으면 개근을 입력할 수 있다.",
                "전입학은 전출교와 전입교 출결을 합산하여 판단한다.",
                "재입학은 재입학 전후 출결을 합산하여 판단한다.",
            ],
            "notAllowed": [
                "수업일수가 다른 중도 입학·편입학생에게 개근을 입력하는 것",
                "순회교육학생이나 건강장애학생에게 무조건 개근을 입력하는 것",
            ],
            "conditions": [
                "특수교육대상자 중 순회교육학생, 건강장애학생은 공란 처리 예외를 확인한다."
            ],
            "schoolRuleNeeded": False,
            "committeeNeeded": False,
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "changes_ppt_2026_hs", "slide": 11}
            ],
            "keywords": ["개근", "전입", "재입학", "건강장애학생"],
        },
        {
            "ruleId": "rule_volunteer_no_simple_donation",
            "topicId": "volunteer_service",
            "ruleSummary": "물품이나 현금의 단순 기부는 봉사활동 시간으로 인정하지 않는다.",
            "allowed": [
                "실제 봉사활동 수행 시간이 확인되는 활동만 봉사활동 실적으로 입력한다."
            ],
            "notAllowed": [
                "물품 및 현금의 단순 기부를 봉사활동 시간으로 환산하여 입력하는 것"
            ],
            "conditions": [
                "학교생활기록부의 어떤 항목에도 봉사시간으로 바꾸어 입력할 수 없다."
            ],
            "schoolRuleNeeded": False,
            "committeeNeeded": False,
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "official_guidelines_2026_hs", "printedPage": 87}
            ],
            "keywords": ["봉사활동", "기부", "현금", "물품"],
        },
        {
            "ruleId": "rule_volunteer_personal_plan_workflow",
            "topicId": "volunteer_service",
            "ruleSummary": "학생 개인계획 봉사활동은 사전 승인과 사후 확인 절차가 필요하다.",
            "allowed": [
                "실적 연계 사이트를 사용한 봉사활동은 전송 자료 확인 후 승인하여 입력할 수 있다.",
                "실적 연계 사이트를 사용하지 않은 경우에는 사전 계획 승인과 확인서 평가 후 입력할 수 있다.",
            ],
            "notAllowed": [
                "사전 승인 없이 수행한 개인 봉사활동을 기존 방식으로 바로 입력하는 것"
            ],
            "conditions": [
                "1365, VMS, DOVOL 연계 여부를 먼저 확인한다.",
                "학생은 사전에 담임교사 또는 담당교사와 인정 기관과 활동 내용을 상담해야 한다.",
            ],
            "schoolRuleNeeded": False,
            "committeeNeeded": False,
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "official_guidelines_2026_hs", "printedPage": 88}
            ],
            "keywords": ["봉사활동", "1365", "VMS", "DOVOL", "사전 승인"],
        },
        {
            "ruleId": "rule_volunteer_grade_1_2_curricular",
            "topicId": "volunteer_service",
            "ruleSummary": "2026학년도 1·2학년의 정규교육과정 내 봉사활동은 창체 각 영역과 연계해 입력한다.",
            "allowed": [
                "1·2학년의 정규교육과정 내 봉사활동은 자율·자치활동, 동아리활동, 진로활동과 연계하여 입력할 수 있다.",
                "해당 실적은 창체 누가기록과 봉사활동 실적관리에서 함께 확인할 수 있다.",
            ],
            "notAllowed": [
                "같은 봉사활동 시간을 창체 영역 시수와 별개의 추가 시간으로 중복 인정하는 것"
            ],
            "conditions": [
                "정규교육과정 외 봉사활동과 학생 개인계획 봉사활동은 봉사활동실적관리 메뉴에서 입력한다.",
                "3학년은 기존 봉사활동실적관리 중심 체계를 따른다.",
            ],
            "schoolRuleNeeded": False,
            "committeeNeeded": False,
            "gradeScope": "grades_1_2_with_grade_3_comparison",
            "sourceRefs": [
                {"docId": "official_guidelines_2026_hs", "printedPage": 87},
                {"docId": "guide_2026_hs", "printedPage": 125},
            ],
            "keywords": ["1·2학년", "창체", "봉사활동", "헌혈"],
        },
        {
            "ruleId": "rule_subject_notes_for_all_students",
            "topicId": "subject_progress",
            "ruleSummary": "고등학교 세부능력 및 특기사항은 모든 학생 입력이 원칙이다.",
            "allowed": [
                "고등학교는 모든 학생에 대해 세부능력 및 특기사항을 입력한다.",
                "수업과 평가 과정에서 수시·상시 기록한 내용을 바탕으로 구체적이고 종합적으로 기술한다.",
            ],
            "notAllowed": [
                "특정 학생만 선별하여 세특을 입력하는 것",
                "수업 중 활동을 단순 나열만 하는 것",
            ],
            "conditions": [
                "성취기준과 성취수준에 근거하여 학생의 성취 과정과 성취 특성이 드러나야 한다."
            ],
            "schoolRuleNeeded": False,
            "committeeNeeded": False,
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "guide_2026_hs", "printedPage": 40}
            ],
            "keywords": ["세특", "모든 학생", "성취기준", "수업 과정"],
        },
        {
            "ruleId": "rule_gifted_invention_only_subject_record",
            "topicId": "subject_progress",
            "ruleSummary": "영재·발명교육 이수 내용은 교과학습발달상황의 전용 기록사항에만 입력한다.",
            "allowed": [
                "관련 교과의 영재·발명교육 기록사항에 입력한다.",
                "당해 학기에 관련 과목이 개설되지 않은 경우에는 개인별 세부능력 및 특기사항의 영재·발명교육 기록사항에 입력한다.",
            ],
            "notAllowed": [
                "행동특성 및 종합의견에 영재교육 이수 내용을 입력하는 것",
                "체험활동 특기사항처럼 다른 항목에 분산 입력하는 것",
            ],
            "conditions": [
                "구체적인 기관 명칭은 입력하지 않는다.",
                "이 기록은 대입전형자료에서 제외되는 항목임을 함께 고려한다.",
            ],
            "schoolRuleNeeded": False,
            "committeeNeeded": False,
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "official_guidelines_2026_hs", "printedPage": 150},
                {"docId": "official_guidelines_2026_hs", "printedPage": 159},
            ],
            "keywords": ["영재교육", "발명교육", "영재·발명교육 기록사항"],
        },
        {
            "ruleId": "rule_behavior_excludes_other_forbidden_content",
            "topicId": "behavior",
            "ruleSummary": "다른 항목에 입력할 수 없는 내용은 행특에도 입력할 수 없다.",
            "allowed": [
                "학교 교육활동 전반에서 지속적으로 관찰된 학습·행동·인성 특성을 교육적 관점에서 입력한다.",
                "학교교육활동을 통한 체육·예술활동은 종합적으로 입력할 수 있다.",
            ],
            "notAllowed": [
                "방과후학교 활동 등 다른 항목에도 입력할 수 없는 내용을 행특에 넣는 것"
            ],
            "conditions": [
                "부정적 행동특성을 입력할 경우에는 구체적 누가기록을 바탕으로 작성하는 것이 바람직하다."
            ],
            "schoolRuleNeeded": True,
            "committeeNeeded": False,
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "official_guidelines_2026_hs", "printedPage": 159},
                {"docId": "guide_2026_hs", "printedPage": 154},
            ],
            "keywords": ["행특", "방과후학교", "교육적 관점", "누가기록"],
        },
        {
            "ruleId": "rule_previous_year_correction",
            "topicId": "corrections",
            "ruleSummary": "이전 학년도 자료 정정은 객관적 증빙자료와 심의 절차가 원칙이다.",
            "allowed": [
                "객관적인 증빙자료가 있는 경우 학업성적관리위원회 심의를 거쳐 이전 학년도 자료를 정정할 수 있다.",
                "인적·학적사항의 학생정보는 증빙자료만으로 정정할 수 있다.",
            ],
            "notAllowed": [
                "증빙자료 없이 기억이나 추정만으로 서술형 항목을 정정하는 것"
            ],
            "conditions": [
                "입력 주체의 과실로 학생 간 내용이 뒤바뀌었거나 전체 누락된 경우에도 해당 학년도의 교육활동 결과물을 바탕으로 심의 후 정정할 수 있다.",
                "입력 주체가 부재하면 필요한 자료를 토대로 학업성적관리위원회가 정정 내용을 결정한다.",
            ],
            "schoolRuleNeeded": False,
            "committeeNeeded": True,
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "official_guidelines_2026_hs", "printedPage": 165},
                {"docId": "official_guidelines_2026_hs", "printedPage": 166},
                {"docId": "guide_2026_hs", "printedPage": 156},
            ],
            "keywords": ["정정", "증빙자료", "학업성적관리위원회", "과실"],
        },
    ]


def build_qa_cards() -> list[dict]:
    return [
        {
            "qaId": "qa_processing_hanja_input",
            "topicId": "processing",
            "question": "중국어·한문 과목처럼 한자 표기가 많은 경우, 세부능력 및 특기사항 일부를 한자로 입력할 수 있나요?",
            "answer": "원칙적으로 불가하다. 학교생활기록부는 한글 입력이 원칙이고, 부득이한 경우에 한해 영문만 허용된다. 따라서 한자를 포함한 다른 외국어 표기는 입력하지 않는다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "guide_2026_hs", "printedPage": 92},
                {"docId": "official_guidelines_2026_hs", "printedPage": 28},
            ],
            "keywords": ["한자", "영문", "외국어", "세특"],
        },
        {
            "qaId": "qa_school_status_overseas_korean_id",
            "topicId": "personal_school_status",
            "question": "주민등록번호가 없는 재외동포 학생이 국내거소신고증을 제출한 경우, 외국인등록증을 추가로 받아야 하나요?",
            "answer": "추가 제출이 필수는 아니다. 국내거소신고증 또는 국내거소신고 사실증명에 적힌 성명과 국내거소신고번호를 학생정보에 입력하면 된다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "guide_2026_hs", "printedPage": 94}
            ],
            "keywords": ["재외동포", "국내거소신고번호", "학생정보"],
        },
        {
            "qaId": "qa_attendance_reference_witness_and_juvenile_case",
            "topicId": "attendance",
            "question": "학생이 경찰서 참고인 조사나 가정법원 심리기일 때문에 결석한 경우, 출결은 어떻게 처리하나요?",
            "answer": "참고인 조사 출석은 곧바로 미인정결석으로 보지 않는다. 학생 상황과 교육적 목적을 고려해 학교장이 출석인정 결석 또는 기타결석으로 판단할 수 있다. 반면 자신의 위법행위와 관련한 가정법원 소년보호재판 출석은 법원소년부의 조사·심리 기간에 해당하므로 출석인정 결석으로 처리한다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "guide_2026_hs", "printedPage": 106}
            ],
            "keywords": ["참고인 조사", "가정법원", "출석인정 결석", "기타결석"],
        },
        {
            "qaId": "qa_awards_competition_participation",
            "topicId": "awards",
            "question": "학교 시상 계획에 있는 교내 대회의 참가 사실이나, 시상 계획에 반영하지 못한 교내 행사 수상을 학교생활기록부에 적을 수 있나요?",
            "answer": "둘 다 주의가 필요하다. 교내 대회라도 준비 과정, 참가 사실, 성적과 수상 실적은 수상경력 이외 항목에 적을 수 없다. 또한 학교 시상 계획에 없는 별도 행사 수상은 수상경력에 입력할 수 없고, 수상대장 입력 여부만 학교에서 별도로 결정할 수 있다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "guide_2026_hs", "printedPage": 123},
                {"docId": "official_guidelines_2026_hs", "printedPage": 61},
            ],
            "keywords": ["교내대회", "수상경력", "학교 시상 계획"],
        },
        {
            "qaId": "qa_creative_volunteer_grade_1_2",
            "topicId": "volunteer_service",
            "question": "2022 개정 교육과정이 적용되는 2026학년도 1·2학년의 봉사활동 실적은 어디에 입력하나요?",
            "answer": "봉사활동은 세 가지로 나누어 본다. 학교교육계획에 따른 정규교육과정 내 봉사활동은 창의적 체험활동 각 영역의 누가기록에서 봉사활동 실적 입력을 선택해 기록한다. 학교교육계획에 따른 정규교육과정 외 봉사활동과 학생 개인계획 봉사활동은 기존처럼 봉사활동실적관리 메뉴에서 입력한다. 3학년은 기존 봉사활동실적관리 중심 체계를 따른다.",
            "gradeScope": "grades_1_2_with_grade_3_comparison",
            "sourceRefs": [
                {"docId": "guide_2026_hs", "printedPage": 125},
                {"docId": "official_guidelines_2026_hs", "printedPage": 86},
            ],
            "keywords": ["1·2학년", "봉사활동", "창체", "봉사활동실적관리"],
        },
        {
            "qaId": "qa_subject_small_class_rank_rule",
            "topicId": "subject_progress",
            "question": "석차등급을 산출하는 과목에서, 수강자 수가 적어 '석차등급' 대신 '·' 표기를 선택할 수 있는 기준은 무엇인가요?",
            "answer": "1·2학년과 3학년이 다르다. 1·2학년은 수강자 수 5명 이하인 경우 같은 입학년도 교육과정 내 동일 과목에 대해 '석차등급' 또는 '·' 중 한 가지 방법을 통일해 적용한다. 3학년은 수강자 수 13명 이하인 경우 같은 원칙이 적용되며, 13명 이하 과목이 2과목 이상이면 3학년 전 과목에 동일한 표기 방식을 써야 한다.",
            "gradeScope": "grade_sensitive",
            "sourceRefs": [
                {"docId": "guide_2026_hs", "printedPage": 140}
            ],
            "keywords": ["수강자5명이하", "수강자13명이하", "석차등급", "1·2학년", "3학년"],
        },
        {
            "qaId": "qa_reading_same_book_duplication",
            "topicId": "reading",
            "question": "같은 책을 국어와 과학에서 서로 다른 관점으로 읽고 다른 독서 증빙자료를 냈다면, 독서활동상황에 중복 기재할 수 있나요?",
            "answer": "가능하다. 학생이 동일한 책을 반복해서 읽더라도 증빙자료가 서로 다르면 과목, 학년, 학기, 영역이 달라도 각각 입력할 수 있다. 원서와 번역본도 증빙자료가 다르면 각각 입력 가능하다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "guide_2026_hs", "printedPage": 152},
                {"docId": "official_guidelines_2026_hs", "printedPage": 157},
            ],
            "keywords": ["독서", "동일 도서명", "중복 기재", "증빙자료"],
        },
        {
            "qaId": "qa_behavior_accumulation_principal",
            "topicId": "behavior",
            "question": "행동특성 및 종합의견의 누가기록 여부를 학교장이 정할 수 있나요?",
            "answer": "그렇다. 누가기록 여부와 방법은 학교장이 정할 수 있다. 다만 학생의 성장과 발전 가능성을 교육적 관점에서 기록해야 하므로, 부정적 행동특성을 적을 때에는 구체적인 누가기록을 남겨 두는 것이 바람직하다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "guide_2026_hs", "printedPage": 154},
                {"docId": "official_guidelines_2026_hs", "printedPage": 158},
            ],
            "keywords": ["행특", "누가기록", "학교장", "부정적 행동특성"],
        },
        {
            "qaId": "qa_correction_swapped_descriptive_items",
            "topicId": "corrections",
            "question": "이전 학년도 세특이나 진로활동 특기사항이 학생끼리 서로 뒤바뀌었거나 완전히 동일하게 입력된 경우, 정정할 수 있나요?",
            "answer": "객관적인 증빙자료가 있고 입력 주체의 과실이 확인되면 학업성적관리위원회 심의를 거쳐 정정할 수 있다. 먼저 해당 교사에게 확인서를 받아 과실 여부를 검토하고, 정정 내용에 허위나 과장이 없는지 점검해야 한다. 입력 주체가 부재하면 필요한 자료를 바탕으로 학업성적관리위원회가 정정 내용을 결정한다.",
            "gradeScope": "all_grades",
            "sourceRefs": [
                {"docId": "guide_2026_hs", "printedPage": 156},
                {"docId": "official_guidelines_2026_hs", "printedPage": 165},
            ],
            "keywords": ["정정", "세특", "진로활동", "과실", "학업성적관리위원회"],
        },
    ]


def build_page_reference_map() -> dict:
    return {
        "schemaVersion": "2026-06-17.seed.v1",
        "documents": {
            "official_guidelines_2026_hs": {
                "title": "2026학년도 학교생활기록부 기재요령(고등학교)",
                "totalPdfPages": 223,
                "pageSystems": {
                    "pdfScreenPage": "PDF 뷰어 화면상 페이지 번호",
                    "printedPage": "본문에 인쇄된 쪽수",
                },
                "pageOffsetRule": {
                    "formula": "대체로 pdfScreenPage = printedPage + 6",
                    "confidence": "medium",
                    "note": "본문 시작 이후 주요 항목에서 확인한 경험칙이며, 앞표지·목차·부록은 개별 확인이 필요하다.",
                },
                "topicRanges": [
                    {"topicId": "processing", "printedStart": 27, "printedEnd": 31, "pdfStart": 33, "pdfEnd": 37},
                    {"topicId": "personal_school_status", "printedStart": 32, "printedEnd": 46, "pdfStart": 38, "pdfEnd": 52},
                    {"topicId": "attendance", "printedStart": 47, "printedEnd": 60, "pdfStart": 53, "pdfEnd": 66},
                    {"topicId": "awards", "printedStart": 61, "printedEnd": 65, "pdfStart": 67, "pdfEnd": 71},
                    {"topicId": "certificates", "printedStart": 66, "printedEnd": 71, "pdfStart": 72, "pdfEnd": 77},
                    {"topicId": "school_violence", "printedStart": 72, "printedEnd": 76, "pdfStart": 78, "pdfEnd": 82},
                    {"topicId": "creative_experience", "printedStart": 77, "printedEnd": 90, "pdfStart": 83, "pdfEnd": 96},
                    {"topicId": "volunteer_service", "printedStart": 87, "printedEnd": 90, "pdfStart": 93, "pdfEnd": 96},
                    {"topicId": "daily_life_activity", "printedStart": 91, "printedEnd": 92, "pdfStart": 97, "pdfEnd": 98},
                    {"topicId": "subject_progress_grades_1_2", "printedStart": 93, "printedEnd": 123, "pdfStart": 99, "pdfEnd": 129},
                    {"topicId": "subject_progress_grade_3", "printedStart": 124, "printedEnd": 155, "pdfStart": 130, "pdfEnd": 161},
                    {"topicId": "reading", "printedStart": 156, "printedEnd": 157, "pdfStart": 162, "pdfEnd": 163},
                    {"topicId": "behavior", "printedStart": 158, "printedEnd": 159, "pdfStart": 164, "pdfEnd": 165},
                    {"topicId": "corrections", "printedStart": 165, "printedEnd": 171, "pdfStart": 171, "pdfEnd": 177},
                ],
            },
            "guide_2026_hs": {
                "title": "2026학년도 학교생활기록부 기재 길라잡이(고등학교)",
                "totalPdfPages": 159,
                "pageSystems": {
                    "pdfScreenPage": "PDF 뷰어 화면상 페이지 번호",
                    "printedPage": "본문에 인쇄된 쪽수",
                },
                "pageOffsetRule": {
                    "formula": "pdfScreenPage = printedPage",
                    "confidence": "high",
                    "note": "점검한 주요 페이지에서 화면상 페이지와 인쇄 쪽수가 일치했다.",
                },
                "topicRanges": [
                    {"topicId": "processing", "section": "changes", "printedStart": 9, "printedEnd": 9, "pdfStart": 9, "pdfEnd": 9},
                    {"topicId": "personal_school_status", "section": "changes", "printedStart": 11, "printedEnd": 14, "pdfStart": 11, "pdfEnd": 14},
                    {"topicId": "attendance", "section": "changes", "printedStart": 15, "printedEnd": 23, "pdfStart": 15, "pdfEnd": 23},
                    {"topicId": "awards", "section": "changes", "printedStart": 24, "printedEnd": 24, "pdfStart": 24, "pdfEnd": 24},
                    {"topicId": "certificates", "section": "changes", "printedStart": 24, "printedEnd": 25, "pdfStart": 24, "pdfEnd": 25},
                    {"topicId": "creative_experience", "section": "changes", "printedStart": 26, "printedEnd": 34, "pdfStart": 26, "pdfEnd": 34},
                    {"topicId": "daily_life_activity", "section": "changes", "printedStart": 35, "printedEnd": 35, "pdfStart": 35, "pdfEnd": 35},
                    {"topicId": "subject_progress", "section": "changes", "printedStart": 36, "printedEnd": 67, "pdfStart": 36, "pdfEnd": 67},
                    {"topicId": "reading", "section": "changes", "printedStart": 68, "printedEnd": 68, "pdfStart": 68, "pdfEnd": 68},
                    {"topicId": "behavior", "section": "changes", "printedStart": 69, "printedEnd": 69, "pdfStart": 69, "pdfEnd": 69},
                    {"topicId": "corrections", "section": "changes", "printedStart": 70, "printedEnd": 71, "pdfStart": 70, "pdfEnd": 71},
                    {"topicId": "processing", "section": "qa", "printedStart": 92, "printedEnd": 93, "pdfStart": 92, "pdfEnd": 93},
                    {"topicId": "personal_school_status", "section": "qa", "printedStart": 94, "printedEnd": 105, "pdfStart": 94, "pdfEnd": 105},
                    {"topicId": "attendance", "section": "qa", "printedStart": 106, "printedEnd": 122, "pdfStart": 106, "pdfEnd": 122},
                    {"topicId": "awards", "section": "qa", "printedStart": 123, "printedEnd": 123, "pdfStart": 123, "pdfEnd": 123},
                    {"topicId": "school_violence", "section": "qa", "printedStart": 124, "printedEnd": 124, "pdfStart": 124, "pdfEnd": 124},
                    {"topicId": "creative_experience", "section": "qa", "printedStart": 125, "printedEnd": 138, "pdfStart": 125, "pdfEnd": 138},
                    {"topicId": "daily_life_activity", "section": "qa", "printedStart": 139, "printedEnd": 139, "pdfStart": 139, "pdfEnd": 139},
                    {"topicId": "subject_progress", "section": "qa", "printedStart": 140, "printedEnd": 151, "pdfStart": 140, "pdfEnd": 151},
                    {"topicId": "reading", "section": "qa", "printedStart": 152, "printedEnd": 153, "pdfStart": 152, "pdfEnd": 153},
                    {"topicId": "behavior", "section": "qa", "printedStart": 154, "printedEnd": 155, "pdfStart": 154, "pdfEnd": 155},
                    {"topicId": "corrections", "section": "qa", "printedStart": 156, "printedEnd": 159, "pdfStart": 156, "pdfEnd": 159},
                ],
            },
        },
    }


def build_answer_policies() -> dict:
    return {
        "schemaVersion": "2026-06-17.seed.v1",
        "defaultPolicy": {
            "brainFirst": True,
            "rawSourceVerificationOnly": True,
            "defaultAnswerOrder": ["결론", "왜 그런지", "조건·예외", "학년 분기", "근거 페이지"],
            "citationRule": "페이지를 제시할 때는 가능하면 인쇄 쪽수와 PDF 화면상 페이지를 함께 제시한다.",
            "forbiddenOutput": [
                "깨진 OCR 조각을 그대로 보여주는 답변",
                "질문과 무관한 원문 문단 덩어리 복사",
                "1·2학년 규칙과 3학년 규칙을 섞어서 단정하는 답변",
            ],
        },
        "policies": [
            {
                "policyId": "recordability",
                "questionSignals": ["기재 가능", "적을 수 있나요", "입력해도 되나요", "써도 되나요"],
                "answerFrame": ["한 줄 결론", "허용 범위", "금지 범위", "조건 또는 예외", "근거 카드"],
                "mustCheck": ["05_rule_cards.jsonl", "03_grade_split_rules.json"],
            },
            {
                "policyId": "change_2026",
                "questionSignals": ["2026에서 뭐가 바뀌었나요", "2025와 차이", "개정사항", "변경사항"],
                "answerFrame": ["핵심 변화", "이전 기준", "2026 기준", "실무상 의미", "적용 학년"],
                "mustCheck": ["04_change_2026_catalog.jsonl", "03_grade_split_rules.json"],
            },
            {
                "policyId": "grade_difference",
                "questionSignals": ["1학년과 3학년 차이", "1·2학년", "3학년", "학년별로"],
                "answerFrame": ["1·2학년", "3학년", "실무상 체크포인트", "근거"],
                "mustCheck": ["03_grade_split_rules.json", "05_rule_cards.jsonl", "06_qa_cards.jsonl"],
            },
            {
                "policyId": "page_lookup",
                "questionSignals": ["원문 페이지", "몇 쪽", "페이지 알려줘", "근거 페이지"],
                "answerFrame": ["추천 확인 문서", "인쇄 쪽수", "PDF 화면상 페이지", "왜 그 페이지를 봐야 하는지"],
                "mustCheck": ["07_page_reference_map.json", "00_document_map.json"],
            },
            {
                "policyId": "qa_lookup",
                "questionSignals": ["Q&A에 있나요", "사례로 설명", "예시", "길라잡이"],
                "answerFrame": ["핵심 답", "Q&A 요지", "실무 적용", "근거"],
                "mustCheck": ["06_qa_cards.jsonl", "07_page_reference_map.json"],
            },
        ],
        "gradeSensitiveHandling": {
            "ifGradeMissing": "추가 확인 질문만 던지지 말고 1·2학년 / 3학년 답을 모두 제시한다.",
            "alwaysSplitTopics": ["subject_progress", "creative_experience", "volunteer_service", "attendance"],
        },
        "fallbackRules": {
            "ifNoBrainCardMatch": "원문에서 근거를 재검토하되, 깨진 텍스트를 그대로 보여주지 말고 사람이 이해할 수 있는 문장으로 다시 작성한다.",
            "ifOfficialAndGuideConflict": "공식 기재요령을 우선 채택하고 길라잡이는 참고 의견으로만 남긴다.",
        },
    }


def build_test_questions() -> dict:
    return {
        "schemaVersion": "2026-06-17.seed.v1",
        "tests": [
            {
                "testId": "t01",
                "question": "교내 대회 참가 사실을 행특에 적을 수 있나요?",
                "expectedTopicIds": ["awards", "behavior"],
                "expectedPolicyId": "recordability",
                "mustMention": ["수상경력 이외 항목에는 기재할 수 없음", "준비 과정과 참가 사실도 금지"],
                "shouldUseCards": ["rule_awards_only_in_awards_section"],
            },
            {
                "testId": "t02",
                "question": "세특 문장을 학생이 써오면 그대로 붙여 넣어도 되나요?",
                "expectedTopicIds": ["processing", "subject_progress"],
                "expectedPolicyId": "recordability",
                "mustMention": ["교사가 직접 작성해야 함", "학생 작성 문장을 그대로 입력하면 안 됨"],
                "shouldUseCards": ["rule_teacher_owns_descriptive_items"],
            },
            {
                "testId": "t03",
                "question": "1학년 봉사활동은 창체에 넣나요, 봉사활동실적에 넣나요?",
                "expectedTopicIds": ["volunteer_service", "creative_experience"],
                "expectedPolicyId": "grade_difference",
                "mustMention": ["1·2학년과 3학년을 구분", "정규교육과정 내 봉사는 창체 연계", "정규교육과정 외·개인계획 봉사는 봉사활동실적관리"],
                "shouldUseCards": ["rule_volunteer_grade_1_2_curricular"],
            },
            {
                "testId": "t04",
                "question": "3학년 소인수 과목은 몇 명 이하일 때 석차등급 대신 점 하나를 쓸 수 있나요?",
                "expectedTopicIds": ["subject_progress_grade_3"],
                "expectedPolicyId": "grade_difference",
                "mustMention": ["3학년", "13명 이하", "동일 표기 방식 적용"],
                "shouldUseCards": ["qa_subject_small_class_rank_rule"],
            },
            {
                "testId": "t05",
                "question": "한자로 세특을 적어도 되나요?",
                "expectedTopicIds": ["processing"],
                "expectedPolicyId": "recordability",
                "mustMention": ["한글이 원칙", "부득이한 경우 영문만 가능", "한자는 불가"],
                "shouldUseCards": ["rule_english_only_when_unavoidable", "qa_processing_hanja_input"],
            },
            {
                "testId": "t06",
                "question": "학교 시상 계획에 없는 행사 상장은 생기부 수상경력에 넣을 수 있나요?",
                "expectedTopicIds": ["awards"],
                "expectedPolicyId": "recordability",
                "mustMention": ["수상경력에 입력 불가", "수상대장 입력 여부는 학교에서 결정 가능"],
                "shouldUseCards": ["rule_awards_only_in_awards_section", "qa_awards_competition_participation"],
            },
            {
                "testId": "t07",
                "question": "현금 기부를 봉사시간으로 바꿔서 입력할 수 있나요?",
                "expectedTopicIds": ["volunteer_service"],
                "expectedPolicyId": "recordability",
                "mustMention": ["단순 기부는 봉사활동 시간으로 인정 불가"],
                "shouldUseCards": ["rule_volunteer_no_simple_donation"],
            },
            {
                "testId": "t08",
                "question": "경찰서 참고인 조사 때문에 빠진 날은 미인정결석인가요?",
                "expectedTopicIds": ["attendance"],
                "expectedPolicyId": "qa_lookup",
                "mustMention": ["미인정결석으로 단정하지 않음", "학교장이 출석인정결석 또는 기타결석으로 판단 가능"],
                "shouldUseCards": ["qa_attendance_reference_witness_and_juvenile_case"],
            },
            {
                "testId": "t09",
                "question": "같은 책을 국어와 과학에서 읽었으면 독서활동상황에 둘 다 넣을 수 있나요?",
                "expectedTopicIds": ["reading"],
                "expectedPolicyId": "qa_lookup",
                "mustMention": ["증빙자료가 다르면 중복 기재 가능"],
                "shouldUseCards": ["qa_reading_same_book_duplication"],
            },
            {
                "testId": "t10",
                "question": "작년 세특이 학생끼리 뒤바뀌었는데 정정할 수 있나요?",
                "expectedTopicIds": ["corrections"],
                "expectedPolicyId": "recordability",
                "mustMention": ["객관적 증빙자료", "학업성적관리위원회 심의", "입력 주체 과실 확인"],
                "shouldUseCards": ["rule_previous_year_correction", "qa_correction_swapped_descriptive_items"],
            },
            {
                "testId": "t11",
                "question": "2026에서 과목출석률이 어떻게 바뀌었나요?",
                "expectedTopicIds": ["attendance", "subject_progress_grades_1_2"],
                "expectedPolicyId": "change_2026",
                "mustMention": ["실제 운영한 수업 횟수 기준", "1·2학년 맥락"],
                "shouldUseCards": ["chg_2026_004_subject_attendance_rate"],
            },
            {
                "testId": "t12",
                "question": "봉사활동 입력 방법 원문 페이지 좀 알려줘.",
                "expectedTopicIds": ["volunteer_service"],
                "expectedPolicyId": "page_lookup",
                "mustMention": ["공식 기재요령", "인쇄 쪽수", "PDF 화면상 페이지", "길라잡이 Q&A 페이지"],
                "shouldUseCards": [],
            },
        ],
    }


def main() -> None:
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)
    write_json(BRAIN_DIR / "00_document_map.json", build_document_map())
    write_json(BRAIN_DIR / "01_topic_taxonomy.json", build_topic_taxonomy())
    write_json(BRAIN_DIR / "02_term_synonyms.json", build_term_synonyms())
    write_json(BRAIN_DIR / "03_grade_split_rules.json", build_grade_split_rules())
    write_jsonl(BRAIN_DIR / "04_change_2026_catalog.jsonl", build_change_catalog())
    write_jsonl(BRAIN_DIR / "05_rule_cards.jsonl", build_rule_cards())
    write_jsonl(BRAIN_DIR / "06_qa_cards.jsonl", build_qa_cards())
    write_json(BRAIN_DIR / "07_page_reference_map.json", build_page_reference_map())
    write_json(BRAIN_DIR / "08_answer_policies.json", build_answer_policies())
    write_json(BRAIN_DIR / "09_test_questions.json", build_test_questions())


if __name__ == "__main__":
    main()
