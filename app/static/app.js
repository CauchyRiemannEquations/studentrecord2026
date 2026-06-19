const gradeSelect = document.getElementById("grade-select");
const topicSelect = document.getElementById("topic-select");
const questionTypeSelect = document.getElementById("question-type-select");
const questionInput = document.getElementById("question-input");
const askButton = document.getElementById("ask-button");
const emptyState = document.getElementById("empty-state");
const answerContent = document.getElementById("answer-content");
const answerSummaryTitle = document.getElementById("answer-summary-title");
const answerSummaryCaption = document.getElementById("answer-summary-caption");
const headingConclusion = document.getElementById("heading-conclusion");
const headingCore = document.getElementById("heading-core");
const headingGrade = document.getElementById("heading-grade");
const headingPractical = document.getElementById("heading-practical");
const headingReferences = document.getElementById("heading-references");
const sectionConclusion = document.getElementById("section-conclusion");
const sectionCore = document.getElementById("section-core");
const sectionGrade = document.getElementById("section-grade");
const sectionPractical = document.getElementById("section-practical");
const gradeSection = document.getElementById("grade-section");
const practicalSection = document.getElementById("practical-section");
const officialReferenceList = document.getElementById("official-reference-list");
const guideReferenceList = document.getElementById("guide-reference-list");
const evidenceList = document.getElementById("evidence-list");
const answerMode = document.getElementById("answer-mode");
const officialPages = document.getElementById("official-pages");
const guidePages = document.getElementById("guide-pages");
const usedChangeCards = document.getElementById("used-change-cards");
const usedRuleCards = document.getElementById("used-rule-cards");
const usedQaCards = document.getElementById("used-qa-cards");
const debugPolicy = document.getElementById("debug-policy");
const debugTopics = document.getElementById("debug-topics");
const debugAnswerStart = document.getElementById("debug-answer-start");
const debugQuality = document.getElementById("debug-quality");
const developerPanel = document.getElementById("developer-panel");

const isDevMode = new URLSearchParams(window.location.search).get("dev") === "1";

if (!isDevMode && developerPanel) {
  developerPanel.remove();
} else if (developerPanel) {
  developerPanel.classList.remove("hidden");
}

async function loadMeta() {
  const response = await fetch("/api/meta");
  const meta = await response.json();
  populateSelect(gradeSelect, meta.grades);
  populateSelect(topicSelect, meta.topics);
  populateSelect(questionTypeSelect, meta.questionTypes);
}

function populateSelect(element, values) {
  element.innerHTML = "";
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value === "auto" ? "자동" : value;
    element.appendChild(option);
  }
}

function renderList(element, items) {
  element.innerHTML = "";
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    element.appendChild(li);
  }
}

function renderPageChips(element, items) {
  element.innerHTML = "";
  const values = items.length ? items : ["해당 쪽수 없음"];
  for (const item of values) {
    const li = document.createElement("li");
    li.className = "page-chip";
    li.textContent = item;
    element.appendChild(li);
  }
}

function renderReferencePages(references) {
  renderPageChips(
    officialReferenceList,
    references.official.map((item) => `p.${item.printedPage}`),
  );
  renderPageChips(
    guideReferenceList,
    references.guide.map((item) => `p.${item.printedPage}`),
  );

  officialPages.textContent = references.official.length
    ? references.official.map((item) => `p.${item.printedPage}`).join(", ")
    : "-";
  guidePages.textContent = references.guide.length
    ? references.guide.map((item) => `p.${item.printedPage}`).join(", ")
    : "-";
}

function renderEvidence(evidence) {
  evidenceList.innerHTML = "";
  if (!evidence.length) {
    const empty = document.createElement("p");
    empty.className = "evidence-empty";
    empty.textContent = "답변과 직접 연결되는 기준이 아직 정리되지 않았습니다.";
    evidenceList.appendChild(empty);
    return;
  }

  const items = evidence.slice(0, 4);

  for (const item of items) {
    const wrapper = document.createElement("article");
    wrapper.className = "evidence-item";

    const title = document.createElement("h4");
    title.textContent = getEvidenceHeading(item.publicSources || []);
    wrapper.appendChild(title);

    const summary = document.createElement("p");
    summary.textContent = item.summary;
    wrapper.appendChild(summary);

    const refs = document.createElement("p");
    refs.className = "evidence-refs";
    refs.textContent = item.publicSources
      .map((source) => `${source.label} p.${source.printedPage}`)
      .join(" / ");
    wrapper.appendChild(refs);

    evidenceList.appendChild(wrapper);
  }
}

function getEvidenceHeading(publicSources) {
  const labels = [...new Set(publicSources.map((source) => source.label))];
  if (!labels.length) {
    return "근거 요약";
  }
  if (labels.length > 1) {
    return "공식 기재요령과 길라잡이 요약";
  }
  if (labels[0] === "공식 기재요령") {
    return "공식 기재요령 요약";
  }
  return "기재 길라잡이 요약";
}

function renderSectionHeadings(labels = {}) {
  headingConclusion.textContent = `[${labels.conclusion || "결론"}]`;
  headingCore.textContent = `[${labels.coreSummary || "핵심 정리"}]`;
  headingGrade.textContent = `[${labels.gradeDifferences || "학년별 차이"}]`;
  headingPractical.textContent = `[${labels.practicalNotes || "실무상 주의"}]`;
  headingReferences.textContent = "[참고 페이지]";
}

function updateAnswerOverview(question, references) {
  answerSummaryTitle.textContent = `‘${question}’ 기준 정리`;
  const officialText = references.official.length
    ? `공식 기재요령 p.${references.official[0].printedPage}`
    : "공식 기재요령 쪽수 확인 필요";
  const guideText = references.guide.length
    ? `기재 길라잡이 p.${references.guide[0].printedPage}`
    : "기재 길라잡이 보조 확인";
  answerSummaryCaption.textContent = `${officialText}부터 확인하고, 필요하면 ${guideText}를 함께 보시면 됩니다.`;
}

function showFriendlyError(message) {
  emptyState.classList.remove("hidden");
  answerContent.classList.add("hidden");
  emptyState.innerHTML = `
    <p class="eyebrow">확인 필요</p>
    <h2>${message}</h2>
    <ul>
      <li>질문 표현을 조금 더 구체적으로 바꿔 보세요.</li>
      <li>학년, 항목, 질문 유형을 직접 선택하면 더 안정적으로 찾을 수 있습니다.</li>
      <li>문제가 계속되면 개발 확인용 패널에서 라우팅 상태를 점검해 주세요.</li>
    </ul>
  `;
}

async function askQuestion() {
  const question = questionInput.value.trim();
  if (!question) {
    questionInput.focus();
    return;
  }

  askButton.disabled = true;
  askButton.textContent = "분석 중...";

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        selectedGrade: gradeSelect.value,
        selectedTopic: topicSelect.value,
        selectedQuestionType: questionTypeSelect.value,
      }),
    });

    if (!response.ok) {
      throw new Error("답변을 불러오지 못했습니다.");
    }

    const data = await response.json();

    emptyState.classList.add("hidden");
    answerContent.classList.remove("hidden");

    renderSectionHeadings(data.sectionLabels);
    updateAnswerOverview(question, data.references);
    sectionConclusion.textContent = data.sections.conclusion;
    renderList(sectionCore, data.sections.coreSummary);

    if (data.sections.gradeDifferences.length) {
      gradeSection.classList.remove("hidden");
      renderList(sectionGrade, data.sections.gradeDifferences);
    } else {
      gradeSection.classList.add("hidden");
      sectionGrade.innerHTML = "";
    }

    if (data.sections.practicalNotes.length) {
      practicalSection.classList.remove("hidden");
      renderList(sectionPractical, data.sections.practicalNotes);
    } else {
      practicalSection.classList.add("hidden");
      sectionPractical.innerHTML = "";
    }

    renderReferencePages(data.references);
    renderEvidence(data.evidence);

    if (isDevMode) {
      answerMode.textContent = data.answerMode;
      usedChangeCards.textContent = data.usedChangeCards.join(", ") || "-";
      usedRuleCards.textContent = data.usedRuleCards.join(", ") || "-";
      usedQaCards.textContent = data.usedQaCards.join(", ") || "-";
      debugPolicy.textContent = data.detectedPolicyId;
      debugTopics.textContent = data.detectedTopicIds.join(", ");
      debugAnswerStart.textContent = data.debug.answerStartsWith || "-";
      debugQuality.textContent = data.qualityPassed ? "통과" : "실패";
    }
  } catch (_error) {
    showFriendlyError("지금은 답변을 불러오지 못했습니다.");
  } finally {
    askButton.disabled = false;
    askButton.textContent = "질문하기";
  }
}

document.getElementById("preset-questions").addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) {
    return;
  }
  questionInput.value = target.dataset.question || "";
  askQuestion();
});

askButton.addEventListener("click", askQuestion);

questionInput.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    askQuestion();
  }
});

loadMeta();
