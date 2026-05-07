const boardElement = document.getElementById("board");
const boardContainerElement = document.getElementById("boardContainer");
const highlightLayerElement = document.getElementById("highlightLayer");
const arrowLayerElement = document.getElementById("arrowLayer");
const statusElement = document.getElementById("status");
const qualityLabelElement = document.getElementById("qualityLabel");
const qualityBadgeElement = document.getElementById("qualityBadge");
const evalSummaryElement = document.getElementById("evalSummary");
const evalBarWhiteElement = document.getElementById("evalBarWhite");
const evalBarBlackElement = document.getElementById("evalBarBlack");
const turnBadgeElement = document.getElementById("turnBadge");
const modeHintElement = document.getElementById("modeHint");
const moveListElement = document.getElementById("moveList");
const openingNameElement = document.getElementById("openingName");
const openingMetaElement = document.getElementById("openingMeta");
const openingSummaryElement = document.getElementById("openingSummary");
const openingIdeasListElement = document.getElementById("openingIdeasList");
const openingResponsesElement = document.getElementById("openingResponses");
const openingLinkWrapElement = document.getElementById("openingLinkWrap");
const studyChecklistListElement = document.getElementById("studyChecklistList");
const headlineElement = document.getElementById("headline");
const engineLineElement = document.getElementById("engineLine");
const whatHappenedListElement = document.getElementById("whatHappenedList");
const keyIdeasListElement = document.getElementById("keyIdeasList");
const watchOutListElement = document.getElementById("watchOutList");
const bulletsElement = document.getElementById("bullets");
const candidateMovesElement = document.getElementById("candidateMoves");
const aiHeadlineElement = document.getElementById("aiHeadline");
const aiStatusLineElement = document.getElementById("aiStatusLine");
const aiSummaryElement = document.getElementById("aiSummary");
const aiPlanListElement = document.getElementById("aiPlanList");
const aiMistakeListElement = document.getElementById("aiMistakeList");
const aiTakeawayListElement = document.getElementById("aiTakeawayList");
const fenBoxElement = document.getElementById("fenBox");
const studiesListElement = document.getElementById("studiesList");
const studyTitleElement = document.getElementById("studyTitle");
const saveStatusElement = document.getElementById("saveStatus");
const analysisLoadingElement = document.getElementById("analysisLoading");
const analysisLoadingTextElement = document.getElementById("analysisLoadingText");
const authSummaryElement = document.getElementById("authSummary");
const authStatusElement = document.getElementById("authStatus");
const authGuestFieldsElement = document.getElementById("authGuestFields");
const authUserPanelElement = document.getElementById("authUserPanel");
const authUserNameElement = document.getElementById("authUserName");
const authUserEmailElement = document.getElementById("authUserEmail");
const authNameInputElement = document.getElementById("authNameInput");
const authEmailInputElement = document.getElementById("authEmailInput");
const authPasswordInputElement = document.getElementById("authPasswordInput");
const loginButton = document.getElementById("loginButton");
const registerButton = document.getElementById("registerButton");
const logoutButton = document.getElementById("logoutButton");
const applyTextEditsButton = document.getElementById("applyTextEditsButton");
const resetTextEditsButton = document.getElementById("resetTextEditsButton");
const editOpeningNameInputElement = document.getElementById("editOpeningNameInput");
const editOpeningSummaryInputElement = document.getElementById("editOpeningSummaryInput");
const editOpeningResponsesInputElement = document.getElementById("editOpeningResponsesInput");
const editHeadlineInputElement = document.getElementById("editHeadlineInput");
const editEngineLineInputElement = document.getElementById("editEngineLineInput");
const editWhatHappenedInputElement = document.getElementById("editWhatHappenedInput");
const editKeyIdeasInputElement = document.getElementById("editKeyIdeasInput");
const editWatchOutInputElement = document.getElementById("editWatchOutInput");
const editBulletsInputElement = document.getElementById("editBulletsInput");
const editAiVerdictInputElement = document.getElementById("editAiVerdictInput");
const editAiPlanInputElement = document.getElementById("editAiPlanInput");
const editAiMistakeInputElement = document.getElementById("editAiMistakeInput");
const editAiTakeawayInputElement = document.getElementById("editAiTakeawayInput");
const commentInputElement = document.getElementById("commentInput");
const customExplanationInputElement = document.getElementById("customExplanationInput");
const newStudyButton = document.getElementById("newStudyButton");
const saveStudyButton = document.getElementById("saveStudyButton");
const undoButton = document.getElementById("undoButton");
const redoButton = document.getElementById("redoButton");
const clearAnnotationsButton = document.getElementById("clearAnnotationsButton");
const flipButton = document.getElementById("flipButton");
const modeButtons = {
  move: document.getElementById("modeMove"),
  arrow: document.getElementById("modeArrow"),
  highlight: document.getElementById("modeHighlight"),
};
const colorButtons = Array.from(document.querySelectorAll(".color-button"));
const arrowDefs = arrowLayerElement.innerHTML;

const PIECES = {
  P: "♙",
  N: "♘",
  B: "♗",
  R: "♖",
  Q: "♕",
  K: "♔",
  p: "♟",
  n: "♞",
  b: "♝",
  r: "♜",
  q: "♛",
  k: "♚",
};

const MODE_HINTS = {
  move: "Move mode lets you play on the board. Right click still adds study marks at any time.",
  arrow: "Arrow mode is useful on touch devices. On desktop, right drag is the fastest way to draw arrows.",
  highlight: "Highlight mode is useful on touch devices. On desktop, right click is the fastest way to mark a square.",
};

let state = {
  studyId: null,
  studies: [],
  title: "Untitled Study",
  moveHistoryUci: [],
  fenHistory: [],
  currentPly: 0,
  flipped: false,
  selectedSquare: null,
  legalTargets: [],
  mode: "move",
  selectedColor: "#4f46e5",
  annotationAnchor: null,
  rightDragAnchor: null,
  rightDragMoved: false,
  rightDragModifiers: null,
  notesByPly: {},
  annotationsByPly: {},
  analysisCacheByPly: {},
  lastAnalysis: null,
  saveTimer: null,
  dirty: false,
  engineEnabled: false,
  aiEnabled: false,
  aiModel: "gpt-5",
  authUser: null,
  analysisLoading: false,
  analysisRequestId: 0,
};

function setStatus(message) {
  statusElement.textContent = message;
}

function setSaveStatus(message) {
  saveStatusElement.textContent = message;
}

function renderList(element, items, emptyMessage) {
  element.innerHTML = "";
  const values = items && items.length > 0 ? items : [emptyMessage];
  values.forEach((text) => {
    const item = document.createElement("li");
    item.textContent = text;
    element.appendChild(item);
  });
}

function textToLines(value) {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function linesToText(value) {
  return (value || []).join("\n");
}

function inlineLoadingMarkup(label) {
  return `<span class="loading-chip"><img src="/logo.svg?v=20260402" alt="" class="loading-logo" /><span>${label}</span></span>`;
}

function setAnalysisLoading(isLoading, text = "Analyzing move...") {
  state.analysisLoading = isLoading;
  analysisLoadingElement.classList.toggle("hidden", !isLoading);
  analysisLoadingTextElement.textContent = text;
}

function currentAnalysisCacheKey() {
  return String(state.currentPly);
}

function currentCachedAnalysis() {
  return state.analysisCacheByPly[currentAnalysisCacheKey()] || null;
}

function cacheAnalysisForCurrentPly(result) {
  state.analysisCacheByPly[currentAnalysisCacheKey()] = JSON.parse(JSON.stringify(result));
}

function currentFen() {
  return state.fenHistory[state.currentPly] || state.fenHistory[0] || "";
}

function currentTurnCode() {
  const fen = currentFen();
  const [, activeColor] = fen.split(" ");
  return activeColor || "w";
}

function activeColorFromFen(fen) {
  const [, activeColor] = fen.split(" ");
  return activeColor === "b" ? "black" : "white";
}

function parseFenBoard(fen) {
  const [placement] = fen.split(" ");
  const rows = placement.split("/");
  const board = {};
  rows.forEach((row, rowIndex) => {
    let file = 0;
    for (const char of row) {
      if (/\d/.test(char)) {
        file += Number(char);
        continue;
      }
      board[`${"abcdefgh"[file]}${8 - rowIndex}`] = char;
      file += 1;
    }
  });
  return board;
}

function orderedSquares() {
  const files = state.flipped ? "hgfedcba" : "abcdefgh";
  const ranks = state.flipped ? [1, 2, 3, 4, 5, 6, 7, 8] : [8, 7, 6, 5, 4, 3, 2, 1];
  const result = [];
  for (const rank of ranks) {
    for (const file of files) {
      result.push(`${file}${rank}`);
    }
  }
  return result;
}

function squareColor(fileIndex, rankIndex) {
  return (fileIndex + rankIndex) % 2 === 0 ? "dark" : "light";
}

function pieceColor(piece) {
  return piece === piece.toUpperCase() ? "w" : "b";
}

function fetchJson(url, options = {}) {
  return fetch(url, options).then(async (response) => {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Unexpected server error" }));
      throw new Error(error.detail || "Unexpected server error");
    }
    return response.json();
  });
}

async function rebuildFenHistory() {
  if (state.moveHistoryUci.length === 0) {
    const game = await fetchJson("/api/game");
    state.fenHistory = [game.fen];
    state.currentPly = 0;
    return;
  }

  const params = new URLSearchParams();
  state.moveHistoryUci.forEach((move) => params.append("move_history_uci", move));
  const response = await fetchJson(`/api/fen-history?${params.toString()}`);
  state.fenHistory = response.history;
  if (state.currentPly > state.moveHistoryUci.length) {
    state.currentPly = state.moveHistoryUci.length;
  }
}

function renderStudies() {
  studiesListElement.innerHTML = "";
  if (state.studies.length === 0) {
    studiesListElement.innerHTML = '<p class="muted compact">No saved studies yet.</p>';
    return;
  }

  state.studies.forEach((study) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "study-item";
    if (study.id === state.studyId) {
      button.classList.add("active");
    }
    button.innerHTML = `
      <strong>${study.title}</strong>
      <div class="muted compact">${study.move_count} moves</div>
    `;
    button.addEventListener("click", () => openStudy(study.id));
    studiesListElement.appendChild(button);
  });
}

function renderMoveList() {
  moveListElement.innerHTML = "";
  if (state.moveHistoryUci.length === 0) {
    moveListElement.innerHTML = '<p class="muted compact">No moves yet.</p>';
    return;
  }

  for (let index = 0; index < state.moveHistoryUci.length; index += 2) {
    const row = document.createElement("div");
    row.className = "candidate-item";

    const whitePly = index + 1;
    const blackPly = index + 2;

    const whiteButton = document.createElement("button");
    whiteButton.type = "button";
    whiteButton.className = "move-item";
    if (state.currentPly === whitePly) {
      whiteButton.classList.add("active");
    }
    whiteButton.textContent = `${Math.floor(index / 2) + 1}. ${state.moveHistoryUci[index]}`;
    whiteButton.addEventListener("click", () => jumpToPly(whitePly));
    row.appendChild(whiteButton);

    if (state.moveHistoryUci[index + 1]) {
      const blackButton = document.createElement("button");
      blackButton.type = "button";
      blackButton.className = "move-item";
      if (state.currentPly === blackPly) {
        blackButton.classList.add("active");
      }
      blackButton.textContent = state.moveHistoryUci[index + 1];
      blackButton.addEventListener("click", () => jumpToPly(blackPly));
      row.appendChild(blackButton);
    }

    moveListElement.appendChild(row);
  }
}

function openingThemeBullets(opening, result) {
  const bullets = [];
  const summary = opening?.summary || "";
  const summarySentences = summary
    .split(/(?<=[.!?])\s+/)
    .map((item) => item.trim())
    .filter(Boolean);
  bullets.push(...summarySentences.slice(0, 2));

  if (result?.candidate_moves?.length) {
    const candidateLine = result.candidate_moves
      .slice(0, 3)
      .map((candidate) => candidate.san)
      .join(", ");
    bullets.push(`Common practical continuations to compare: ${candidateLine}.`);
  }

  if (result?.move_quality_summary) {
    bullets.push(result.move_quality_summary);
  }

  return bullets.slice(0, 4);
}

function buildStudyChecklist(result) {
  const openingName = result?.opening?.name;
  const candidateMoves = (result?.candidate_moves || []).slice(0, 3).map((candidate) => candidate.san);
  const checklist = [];

  if (openingName) {
    checklist.push(`Opening: know the purpose of the ${openingName}, not only the move order.`);
  } else {
    checklist.push("Opening: identify what the move changes in development, centre, and king safety.");
  }

  checklist.push("Middlegame: note the pawn structure and the pawn breaks each side is aiming for.");
  checklist.push("Middlegame: collect one or two tactical motifs that usually appear from this setup.");

  if (candidateMoves.length > 0) {
    checklist.push(`Review: compare your choice with these practical continuations: ${candidateMoves.join(", ")}.`);
  }

  checklist.push("Endgame: ask which pieces you would like to exchange and what endgame would favor your side.");
  return checklist.slice(0, 5);
}

function renderAuthState() {
  if (state.authUser) {
    authSummaryElement.textContent = state.authUser.display_name;
    authStatusElement.textContent = "Your studies are now kept under your account on this device.";
    authGuestFieldsElement.classList.add("hidden");
    authUserPanelElement.classList.remove("hidden");
    authUserNameElement.textContent = state.authUser.display_name;
    authUserEmailElement.textContent = state.authUser.email;
    return;
  }

  authSummaryElement.textContent = "Guest mode";
  authStatusElement.textContent = "Sign in to keep a personal library of studies.";
  authGuestFieldsElement.classList.remove("hidden");
  authUserPanelElement.classList.add("hidden");
  authUserNameElement.textContent = "";
  authUserEmailElement.textContent = "";
}

function renderBoard() {
  const fen = currentFen();
  const pieces = parseFenBoard(fen);
  boardElement.innerHTML = "";
  turnBadgeElement.textContent = `Turn: ${activeColorFromFen(fen)}`;
  fenBoxElement.textContent = fen;
  modeHintElement.textContent = MODE_HINTS[state.mode];

  orderedSquares().forEach((square) => {
    const fileIndex = "abcdefgh".indexOf(square[0]);
    const rankIndex = Number(square[1]) - 1;
    const piece = pieces[square];
    const squareElement = document.createElement("button");
    squareElement.type = "button";
    squareElement.className = `square ${squareColor(fileIndex, rankIndex)}`;
    squareElement.dataset.square = square;

    if (state.selectedSquare === square) {
      squareElement.classList.add("selected");
    }
    if (state.legalTargets.includes(square)) {
      squareElement.classList.add("target");
    }

    if (piece) {
      const pieceElement = document.createElement("span");
      pieceElement.className = "piece";
      pieceElement.textContent = PIECES[piece];
      squareElement.appendChild(pieceElement);
    }

    const label = document.createElement("span");
    label.className = "square-label";
    label.textContent = square;
    squareElement.appendChild(label);

    squareElement.addEventListener("click", () => handleSquareClick(square, piece));
    squareElement.addEventListener("contextmenu", (event) => {
      event.preventDefault();
    });
    squareElement.addEventListener("mousedown", (event) => {
      if (event.button === 2) {
        event.preventDefault();
        startRightDrag(square, event);
      }
    });
    squareElement.addEventListener("mouseenter", () => {
      if (state.rightDragAnchor && state.rightDragAnchor !== square) {
        state.rightDragMoved = true;
      }
    });
    squareElement.addEventListener("mouseup", (event) => {
      if (event.button === 2) {
        event.preventDefault();
        finishRightDrag(square, event);
      }
    });
    boardElement.appendChild(squareElement);
  });

  renderAnnotations();
}

function squareToDisplayPosition(square) {
  const file = "abcdefgh".indexOf(square[0]);
  const rank = Number(square[1]) - 1;
  const col = state.flipped ? 7 - file : file;
  const row = state.flipped ? rank : 7 - rank;
  return { col, row };
}

function currentAnnotations() {
  const key = String(state.currentPly);
  if (!state.annotationsByPly[key]) {
    state.annotationsByPly[key] = { arrows: [], highlights: [] };
  }
  return state.annotationsByPly[key];
}

function renderAnnotations() {
  const annotations = currentAnnotations();
  highlightLayerElement.innerHTML = "";
  annotations.highlights.forEach((item) => {
    const { col, row } = squareToDisplayPosition(item.square);
    const square = document.createElement("div");
    square.className = "highlight-square";
    square.style.left = `${col * 12.5}%`;
    square.style.top = `${row * 12.5}%`;
    square.style.width = "12.5%";
    square.style.height = "12.5%";
    square.style.background = item.color;
    highlightLayerElement.appendChild(square);
  });

  arrowLayerElement.innerHTML = arrowDefs;
  annotations.arrows.forEach((item) => {
    const arrow = buildArrowGeometry(item.from_square, item.to_square);
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", arrow.path);
    path.setAttribute("stroke", item.color);
    arrowLayerElement.appendChild(path);

    const head = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
    head.setAttribute("points", arrow.headPoints);
    head.setAttribute("fill", item.color);
    arrowLayerElement.appendChild(head);
  });
}

function squareCenterPercent(square) {
  const { col, row } = squareToDisplayPosition(square);
  return {
    x: col * 12.5 + 6.25,
    y: row * 12.5 + 6.25,
  };
}

function buildArrowGeometry(fromSquare, toSquare) {
  const from = squareCenterPercent(fromSquare);
  const to = squareCenterPercent(toSquare);
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const distance = Math.hypot(dx, dy) || 1;
  const ux = dx / distance;
  const uy = dy / distance;
  const px = -uy;
  const py = ux;

  const start = {
    x: from.x + ux * 1.8,
    y: from.y + uy * 1.8,
  };
  const tip = {
    x: to.x - ux * 1.1,
    y: to.y - uy * 1.1,
  };
  const shaftEnd = {
    x: tip.x - ux * 2.6,
    y: tip.y - uy * 2.6,
  };
  const curve = Math.min(4, distance * 0.12);
  const control = {
    x: (start.x + shaftEnd.x) / 2 + px * curve,
    y: (start.y + shaftEnd.y) / 2 + py * curve,
  };

  const headBase = {
    x: tip.x - ux * 2.9,
    y: tip.y - uy * 2.9,
  };
  const headLeft = {
    x: headBase.x + px * 1.45,
    y: headBase.y + py * 1.45,
  };
  const headRight = {
    x: headBase.x - px * 1.45,
    y: headBase.y - py * 1.45,
  };

  return {
    path: `M ${start.x} ${start.y} Q ${control.x} ${control.y} ${shaftEnd.x} ${shaftEnd.y}`,
    headPoints: `${tip.x},${tip.y} ${headLeft.x},${headLeft.y} ${headRight.x},${headRight.y}`,
  };
}

function setEngineState(result) {
  qualityBadgeElement.className = "quality-badge quality-neutral";

  if (!result || !result.move_quality) {
    qualityLabelElement.textContent = state.engineEnabled ? "Engine ready" : "No engine judgement";
    qualityBadgeElement.textContent = state.engineEnabled ? "Ready" : "No engine";
    evalSummaryElement.textContent = state.engineEnabled
      ? "Stockfish is available. Play a move to get a verdict, best move, and evaluation bar update."
      : "Install Stockfish and configure STOCKFISH_PATH to unlock engine judgement.";
    evalBarWhiteElement.style.width = "50%";
    evalBarBlackElement.style.width = "50%";
    engineLineElement.textContent =
      state.engineEnabled
        ? "Play a move to see whether it is best, good, inaccurate, a mistake, a blunder, or an interesting idea."
        : "The move assessment will explain whether the move is good, inaccurate, a mistake, a blunder, or an interesting idea.";
    return;
  }

  qualityLabelElement.textContent = result.move_quality_label;
  qualityBadgeElement.textContent = result.move_quality_label;
  qualityBadgeElement.classList.add(`quality-${result.move_quality}`);
  evalSummaryElement.textContent = result.move_quality_summary;

  const whitePct = result.evaluation_bar_white_pct ?? 50;
  evalBarWhiteElement.style.width = `${whitePct}%`;
  evalBarBlackElement.style.width = `${100 - whitePct}%`;

  engineLineElement.textContent =
    result.engine_line_override
      || (`Played score: ${result.played_move_score}. Best move: ${result.best_move_san} `
      + `(${result.best_move_score}). Centipawn loss: ${result.centipawn_loss ?? 0}.`);
}

function renderOpening(opening) {
  openingResponsesElement.innerHTML = "";
  openingLinkWrapElement.innerHTML = "";
  renderList(openingIdeasListElement, [], "The main opening themes will appear here.");

  if (!opening || !opening.name) {
    openingNameElement.textContent = "Opening not identified yet";
    openingMetaElement.textContent = "Play a few moves to detect the opening.";
    openingSummaryElement.textContent =
      "When available, the app will show the opening name, ECO code, parent opening, and educational context.";
    renderList(studyChecklistListElement, [], "Play a move to generate a study checklist.");
    return;
  }

  openingNameElement.textContent = opening.name;
  openingMetaElement.textContent = [opening.eco, opening.parent].filter(Boolean).join(" • ") || "Opening information";
  openingSummaryElement.textContent = opening.summary || "Wikibooks has an opening page for this line.";

  (opening.common_responses || []).slice(0, 8).forEach((response) => {
    const chip = document.createElement("span");
    chip.className = "tag-chip";
    chip.textContent = response;
    openingResponsesElement.appendChild(chip);
  });

  if (opening.wikibooks_url) {
    const link = document.createElement("a");
    link.href = opening.wikibooks_url;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = "Open Wikibooks page";
    openingLinkWrapElement.appendChild(link);
  }
}

function renderCandidates(result) {
  candidateMovesElement.innerHTML = "";
  const candidates = result?.candidate_moves || [];
  if (candidates.length === 0) {
    candidateMovesElement.innerHTML =
      '<p class="muted compact">Engine candidate moves will appear here when Stockfish is available.</p>';
    return;
  }

  candidates.forEach((candidate, index) => {
    const item = document.createElement("div");
    item.className = "candidate-item";
    item.innerHTML = `
      <strong>${index + 1}. ${candidate.san}</strong>
      <span class="muted compact">${candidate.score}</span>
    `;
    candidateMovesElement.appendChild(item);
  });
}

function renderAi(result) {
  aiStatusLineElement.textContent = state.aiEnabled
    ? `AI key detected for model ${state.aiModel}.`
    : "AI disabled. Add OPENAI_API_KEY to the .env file, then restart the server.";
  if (result && result.ai_error) {
    aiStatusLineElement.textContent = `AI unavailable for this move. Showing local coaching instead. ${result.ai_error}`;
  }
  if (!result || !result.ai_summary) {
    aiHeadlineElement.textContent = "AI study coach";
    aiSummaryElement.textContent =
      state.aiEnabled
        ? "A local coaching fallback will appear here if the live AI call fails."
        : "Add OPENAI_API_KEY if you want a polished coaching summary built from the engine verdict and opening context.";
    renderList(aiPlanListElement, [], "The AI plan will appear here.");
    renderList(aiMistakeListElement, [], "The AI warning will appear here.");
    renderList(aiTakeawayListElement, [], "The AI takeaway will appear here.");
    return;
  }

  aiHeadlineElement.textContent = "AI study coach";
  aiSummaryElement.textContent = result.ai_verdict || result.ai_summary;
  renderList(
    aiPlanListElement,
    result.ai_best_plan ? [result.ai_best_plan] : [],
    "No AI plan available for this move.",
  );
  renderList(
    aiMistakeListElement,
    result.ai_typical_mistake ? [result.ai_typical_mistake] : [],
    "No AI warning available for this move.",
  );
  renderList(
    aiTakeawayListElement,
    result.ai_training_takeaway ? [result.ai_training_takeaway] : [],
    "No AI takeaway available for this move.",
  );
}

function renderAnalysis(result) {
  state.lastAnalysis = result;
  if (!result) {
    headlineElement.textContent = "Waiting for a move";
    renderList(whatHappenedListElement, [], "Play a move to generate a structured explanation.");
    renderList(keyIdeasListElement, [], "The app will highlight the main ideas to keep in mind.");
    renderList(watchOutListElement, [], "Warnings and tactical alerts will appear here.");
    bulletsElement.innerHTML = "<li>Play a move to generate a structured explanation.</li>";
    renderOpening(null);
    renderCandidates(null);
    renderAi(null);
    setEngineState(null);
    populateStudyTextEditors(null);
    return;
  }

  headlineElement.textContent = result.headline;
  renderList(whatHappenedListElement, result.what_happened, "No short explanation available.");
  renderList(keyIdeasListElement, result.key_ideas, "No key ideas were generated.");
  renderList(watchOutListElement, result.watch_out, "No immediate warning was generated.");
  renderList(bulletsElement, result.bullets, "No full notes available.");

  renderOpening(result.opening);
  renderList(openingIdeasListElement, openingThemeBullets(result.opening, result), "No opening themes available.");
  renderList(studyChecklistListElement, buildStudyChecklist(result), "No study checklist available.");
  renderCandidates(result);
  renderAi(result);
  setEngineState(result);
  populateStudyTextEditors(result);
}

function renderPendingAnalysis(moveUci) {
  const moveLabel = moveUci ? moveUci : "the position";
  headlineElement.textContent = `Analyzing ${moveLabel}...`;
  renderList(whatHappenedListElement, [], "Loading the move explanation...");
  renderList(keyIdeasListElement, [], "Loading the key ideas...");
  renderList(watchOutListElement, [], "Loading warnings and tactical alerts...");
  renderList(bulletsElement, [], "Loading full notes...");

  openingNameElement.textContent = "Opening analysis is loading";
  openingMetaElement.textContent = "Checking opening name, ECO code, and typical replies.";
  openingSummaryElement.innerHTML = inlineLoadingMarkup("Loading opening context");
  renderList(openingIdeasListElement, [], "Loading opening themes...");
  openingResponsesElement.innerHTML = "";
  openingLinkWrapElement.innerHTML = "";
  renderList(studyChecklistListElement, [], "Loading the study checklist...");

  candidateMovesElement.innerHTML = inlineLoadingMarkup("Loading engine candidate moves");
  aiHeadlineElement.textContent = "AI study coach";
  aiStatusLineElement.textContent = "Preparing the study summary.";
  aiSummaryElement.innerHTML = inlineLoadingMarkup("Loading coaching summary");
  renderList(aiPlanListElement, [], "Loading the best plan...");
  renderList(aiMistakeListElement, [], "Loading the typical mistake...");
  renderList(aiTakeawayListElement, [], "Loading the training takeaway...");

  qualityLabelElement.textContent = "Analyzing";
  qualityBadgeElement.className = "quality-badge quality-neutral";
  qualityBadgeElement.textContent = "Loading";
  evalSummaryElement.textContent = "Stockfish is evaluating the move.";
  engineLineElement.textContent = "The move is already on the board. Engine details will appear in a moment.";
}

function populateStudyTextEditors(result) {
  const opening = result?.opening || {};
  editOpeningNameInputElement.value = opening.name || "";
  editOpeningSummaryInputElement.value = opening.summary || "";
  editOpeningResponsesInputElement.value = linesToText(opening.common_responses || []);
  editHeadlineInputElement.value = result?.headline || "";
  editEngineLineInputElement.value = engineLineElement.textContent || "";
  editWhatHappenedInputElement.value = linesToText(result?.what_happened || []);
  editKeyIdeasInputElement.value = linesToText(result?.key_ideas || []);
  editWatchOutInputElement.value = linesToText(result?.watch_out || []);
  editBulletsInputElement.value = linesToText(result?.bullets || []);
  editAiVerdictInputElement.value = result?.ai_verdict || result?.ai_summary || "";
  editAiPlanInputElement.value = result?.ai_best_plan || "";
  editAiMistakeInputElement.value = result?.ai_typical_mistake || "";
  editAiTakeawayInputElement.value = result?.ai_training_takeaway || "";
}

function applyStudyTextEdits() {
  const cached = currentCachedAnalysis() || state.lastAnalysis;
  if (!cached) {
    setStatus("Play a move before editing the study text.");
    return;
  }

  const updated = JSON.parse(JSON.stringify(cached));
  updated.opening = updated.opening || {};
  updated.opening.name = editOpeningNameInputElement.value.trim() || null;
  updated.opening.summary = editOpeningSummaryInputElement.value.trim() || null;
  updated.opening.common_responses = textToLines(editOpeningResponsesInputElement.value);
  updated.headline = editHeadlineInputElement.value.trim() || updated.headline;
  updated.what_happened = textToLines(editWhatHappenedInputElement.value);
  updated.key_ideas = textToLines(editKeyIdeasInputElement.value);
  updated.watch_out = textToLines(editWatchOutInputElement.value);
  updated.bullets = textToLines(editBulletsInputElement.value);
  updated.ai_verdict = editAiVerdictInputElement.value.trim() || null;
  updated.ai_summary = updated.ai_verdict;
  updated.ai_best_plan = editAiPlanInputElement.value.trim() || null;
  updated.ai_typical_mistake = editAiMistakeInputElement.value.trim() || null;
  updated.ai_training_takeaway = editAiTakeawayInputElement.value.trim() || null;
  updated.engine_line_override = editEngineLineInputElement.value.trim();

  state.analysisCacheByPly[currentAnalysisCacheKey()] = updated;
  state.lastAnalysis = updated;
  renderAnalysis(updated);
  scheduleAutosave();
  setStatus("Study text updated for this position.");
}

function resetStudyTextEdits() {
  if (state.currentPly === 0) {
    setStatus("There is no generated study text on the starting position.");
    return;
  }
  delete state.analysisCacheByPly[currentAnalysisCacheKey()];
  void analyseCurrentPly().catch((error) => {
    setAnalysisLoading(false);
    setStatus(error.message);
  });
}

function currentNote() {
  const key = String(state.currentPly);
  if (!state.notesByPly[key]) {
    state.notesByPly[key] = { comment: "", custom_explanation: "" };
  }
  return state.notesByPly[key];
}

function renderNoteEditors() {
  const note = currentNote();
  commentInputElement.value = note.comment || "";
  customExplanationInputElement.value = note.custom_explanation || "";
}

async function analyseCurrentPly() {
  const requestId = ++state.analysisRequestId;
  if (state.currentPly === 0) {
    setAnalysisLoading(false);
    renderAnalysis(null);
    renderBoard();
    renderMoveList();
    renderNoteEditors();
    return;
  }

  const cached = currentCachedAnalysis();
  if (cached) {
    setAnalysisLoading(false);
    renderAnalysis(cached);
    renderBoard();
    renderMoveList();
    renderNoteEditors();
    return;
  }

  const moveUci = state.moveHistoryUci[state.currentPly - 1];
  const moveHistoryBefore = state.moveHistoryUci.slice(0, state.currentPly - 1);
  const fromSquare = moveUci.slice(0, 2);
  const toSquare = moveUci.slice(2, 4);
  const promotion = moveUci.length > 4 ? moveUci.slice(4, 5) : null;

  setAnalysisLoading(true, `Analyzing ${moveUci}...`);
  renderPendingAnalysis(moveUci);
  try {
    const result = await fetchJson("/api/explain-move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        fen: state.fenHistory[state.currentPly - 1],
        from_square: fromSquare,
        to_square: toSquare,
        promotion,
        move_history_uci: moveHistoryBefore,
      }),
    });

    if (requestId !== state.analysisRequestId) {
      return;
    }

    setAnalysisLoading(false);
    cacheAnalysisForCurrentPly(result);
    renderAnalysis(result);
    renderBoard();
    renderMoveList();
    renderNoteEditors();
  } catch (error) {
    if (requestId !== state.analysisRequestId) {
      return;
    }
    setAnalysisLoading(false);
    throw error;
  }
}

function scheduleAutosave() {
  state.dirty = true;
  setSaveStatus("Unsaved changes...");
  clearTimeout(state.saveTimer);
  state.saveTimer = setTimeout(() => {
    void saveCurrentStudy();
  }, 600);
}

async function saveCurrentStudy() {
  if (!state.studyId) {
    return;
  }

  await fetchJson(`/api/studies/${state.studyId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: state.title,
      move_history_uci: state.moveHistoryUci,
      current_ply: state.currentPly,
      flipped: state.flipped,
      notes_by_ply: state.notesByPly,
      annotations_by_ply: state.annotationsByPly,
      analysis_cache_by_ply: state.analysisCacheByPly,
    }),
  });
  state.dirty = false;
  setSaveStatus("Saved");
  await refreshStudies();
}

async function refreshStudies() {
  state.studies = await fetchJson("/api/studies");
  renderStudies();
}

async function loadAuthState() {
  const auth = await fetchJson("/api/auth/me");
  state.authUser = auth.user;
  renderAuthState();
}

async function createNewStudy() {
  const created = await fetchJson("/api/studies", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: "Untitled Study" }),
  });
  await refreshStudies();
  localStorage.setItem("chessStudy:lastStudyId", created.id);
  await openStudy(created.id);
  setStatus("New study created.");
}

async function openStudy(studyId) {
  const study = await fetchJson(`/api/studies/${studyId}`);
  state.studyId = study.id;
  state.title = study.title;
  state.moveHistoryUci = study.move_history_uci;
  state.currentPly = study.current_ply;
  state.flipped = study.flipped;
  state.notesByPly = study.notes_by_ply || {};
  state.annotationsByPly = study.annotations_by_ply || {};
  state.analysisCacheByPly = study.analysis_cache_by_ply || {};
  state.selectedSquare = null;
  state.legalTargets = [];
  state.annotationAnchor = null;
  studyTitleElement.value = study.title;
  localStorage.setItem("chessStudy:lastStudyId", study.id);
  await rebuildFenHistory();
  renderBoard();
  renderMoveList();
  renderNoteEditors();
  await analyseCurrentPly();
  renderStudies();
  setSaveStatus(`Loaded. Last update: ${new Date(study.updated_at).toLocaleString()}`);
}

async function syncWorkspaceAfterAuth(statusMessage) {
  state.studyId = null;
  await refreshStudies();
  if (state.studies.length > 0) {
    await openStudy(state.studies[0].id);
  } else {
    await createNewStudy();
  }
  setStatus(statusMessage);
}

function truncateFuture() {
  state.moveHistoryUci = state.moveHistoryUci.slice(0, state.currentPly);
  Object.keys(state.notesByPly).forEach((key) => {
    if (Number(key) > state.currentPly) {
      delete state.notesByPly[key];
    }
  });
  Object.keys(state.annotationsByPly).forEach((key) => {
    if (Number(key) > state.currentPly) {
      delete state.annotationsByPly[key];
    }
  });
  Object.keys(state.analysisCacheByPly).forEach((key) => {
    if (Number(key) > state.currentPly) {
      delete state.analysisCacheByPly[key];
    }
  });
}

async function submitMove(fromSquare, toSquare) {
  const moveUci = `${fromSquare}${toSquare}`;
  if (state.currentPly < state.moveHistoryUci.length) {
    truncateFuture();
  }

  state.moveHistoryUci = [...state.moveHistoryUci, moveUci];
  state.currentPly += 1;
  state.selectedSquare = null;
  state.legalTargets = [];
  await rebuildFenHistory();
  renderBoard();
  renderMoveList();
  renderNoteEditors();
  renderPendingAnalysis(moveUci);
  setAnalysisLoading(true, `Analyzing ${moveUci}...`);
  scheduleAutosave();
  setStatus(`Played ${moveUci}.`);
  void analyseCurrentPly().catch((error) => {
    setAnalysisLoading(false);
    setStatus(error.message);
  });
}

async function selectSquare(square) {
  const result = await fetchJson(
    `/api/legal-moves?fen=${encodeURIComponent(currentFen())}&from_square=${square}`,
  );
  state.selectedSquare = square;
  state.legalTargets = result.legal_targets;
  renderBoard();
}

function toggleHighlight(square, color = state.selectedColor) {
  const annotations = currentAnnotations();
  const existing = annotations.highlights.find((item) => item.square === square);
  if (existing && existing.color === color) {
    annotations.highlights = annotations.highlights.filter((item) => item !== existing);
  } else if (existing) {
    existing.color = color;
  } else {
    annotations.highlights.push({ square, color });
  }
  renderBoard();
  scheduleAutosave();
}

function toggleArrow(fromSquare, toSquare, color = state.selectedColor) {
  const annotations = currentAnnotations();
  const existing = annotations.arrows.find(
    (item) => item.from_square === fromSquare && item.to_square === toSquare,
  );
  if (existing && existing.color === color) {
    annotations.arrows = annotations.arrows.filter((item) => item !== existing);
  } else if (existing) {
    existing.color = color;
  } else {
    annotations.arrows.push({
      from_square: fromSquare,
      to_square: toSquare,
      color,
    });
  }
  renderBoard();
  scheduleAutosave();
}

function annotationColorFromModifiers(modifiers, annotationType) {
  if (modifiers?.altKey) {
    return "#2563eb";
  }
  if (modifiers?.shiftKey) {
    return "#16a34a";
  }
  if (modifiers?.ctrlKey || modifiers?.metaKey) {
    return annotationType === "arrow" ? "#e11d48" : "#f59e0b";
  }
  return annotationType === "arrow" ? "#f59e0b" : "#e11d48";
}

function startRightDrag(square, event) {
  state.rightDragAnchor = square;
  state.rightDragMoved = false;
  state.rightDragModifiers = {
    altKey: event.altKey,
    ctrlKey: event.ctrlKey,
    metaKey: event.metaKey,
    shiftKey: event.shiftKey,
  };
}

function finishRightDrag(square, event) {
  if (!state.rightDragAnchor) {
    return;
  }

  if (state.rightDragMoved && state.rightDragAnchor !== square) {
    const color = annotationColorFromModifiers(state.rightDragModifiers, "arrow");
    toggleArrow(state.rightDragAnchor, square, color);
    setStatus(`Arrow updated: ${state.rightDragAnchor} to ${square}`);
  } else {
    const modifiers = state.rightDragModifiers || {
      altKey: event.altKey,
      ctrlKey: event.ctrlKey,
      metaKey: event.metaKey,
      shiftKey: event.shiftKey,
    };
    const color = annotationColorFromModifiers(modifiers, "highlight");
    toggleHighlight(square, color);
    setStatus(`Highlight updated: ${square}`);
  }

  state.rightDragAnchor = null;
  state.rightDragMoved = false;
  state.rightDragModifiers = null;
}

async function handleSquareClick(square, piece) {
  try {
    if (state.rightDragAnchor) {
      return;
    }

    if (state.mode === "highlight") {
      toggleHighlight(square);
      return;
    }

    if (state.mode === "arrow") {
      if (!state.annotationAnchor) {
        state.annotationAnchor = square;
        setStatus(`Arrow start: ${square}`);
      } else {
        toggleArrow(state.annotationAnchor, square);
        state.annotationAnchor = null;
        setStatus(`Arrow updated: ${square}`);
      }
      return;
    }

    const activeTurn = currentTurnCode();

    if (state.selectedSquare && state.legalTargets.includes(square)) {
      await submitMove(state.selectedSquare, square);
      return;
    }

    if (piece && pieceColor(piece) === activeTurn) {
      if (state.selectedSquare === square) {
        state.selectedSquare = null;
        state.legalTargets = [];
        renderBoard();
        return;
      }
      await selectSquare(square);
      setStatus(`Selected ${square}.`);
      return;
    }

    state.selectedSquare = null;
    state.legalTargets = [];
    renderBoard();
    setStatus("Select a piece from the side to move.");
  } catch (error) {
    state.selectedSquare = null;
    state.legalTargets = [];
    renderBoard();
    setStatus(error.message);
  }
}

async function jumpToPly(ply) {
  state.currentPly = ply;
  state.selectedSquare = null;
  state.legalTargets = [];
  await analyseCurrentPly();
}

async function undo() {
  if (state.currentPly === 0) {
    return;
  }
  state.currentPly -= 1;
  await analyseCurrentPly();
}

async function redo() {
  if (state.currentPly >= state.moveHistoryUci.length) {
    return;
  }
  state.currentPly += 1;
  await analyseCurrentPly();
}

function bindModeButtons() {
  Object.entries(modeButtons).forEach(([mode, button]) => {
    button.addEventListener("click", () => {
      state.mode = mode;
      state.annotationAnchor = null;
      Object.values(modeButtons).forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      renderBoard();
    });
  });
}

function bindColorButtons() {
  colorButtons.forEach((button) => {
    button.style.background = button.dataset.color;
    button.addEventListener("click", () => {
      state.selectedColor = button.dataset.color;
      colorButtons.forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
    });
  });
}

function bindKeyboardShortcuts() {
  document.addEventListener("keydown", (event) => {
    const target = event.target;
    if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) {
      return;
    }

    if (event.key === "ArrowLeft") {
      event.preventDefault();
      void undo();
      return;
    }

    if (event.key === "ArrowRight") {
      event.preventDefault();
      void redo();
      return;
    }

    const mapping = {
      "1": "#4f46e5",
      "2": "#e11d48",
      "3": "#0f766e",
      "4": "#f59e0b",
    };
    const color = mapping[event.key];
    if (!color) {
      return;
    }

    state.selectedColor = color;
    colorButtons.forEach((button) => {
      button.classList.toggle("active", button.dataset.color === color);
    });
    setStatus(`Annotation color changed.`);
  });
}

function clearCurrentAnnotations() {
  state.annotationsByPly[String(state.currentPly)] = { arrows: [], highlights: [] };
  renderBoard();
  scheduleAutosave();
  setStatus("Annotations cleared for this position.");
}

function bindNoteEditors() {
  commentInputElement.addEventListener("input", () => {
    currentNote().comment = commentInputElement.value;
    scheduleAutosave();
  });

  customExplanationInputElement.addEventListener("input", () => {
    currentNote().custom_explanation = customExplanationInputElement.value;
    scheduleAutosave();
  });
}

function authPayload() {
  return {
    display_name: authNameInputElement.value.trim(),
    email: authEmailInputElement.value.trim(),
    password: authPasswordInputElement.value,
  };
}

async function login() {
  const payload = authPayload();
  const auth = await fetchJson("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: payload.email, password: payload.password }),
  });
  state.authUser = auth.user;
  renderAuthState();
  await syncWorkspaceAfterAuth(`Signed in as ${auth.user.display_name}.`);
}

async function register() {
  const payload = authPayload();
  const auth = await fetchJson("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  state.authUser = auth.user;
  renderAuthState();
  await syncWorkspaceAfterAuth(`Account created for ${auth.user.display_name}.`);
}

async function logout() {
  await fetchJson("/api/auth/logout", { method: "POST" });
  state.authUser = null;
  renderAuthState();
  await syncWorkspaceAfterAuth("Signed out. Back to guest studies.");
}

async function bootstrap() {
  bindModeButtons();
  bindColorButtons();
  bindKeyboardShortcuts();
  bindNoteEditors();

  applyTextEditsButton.addEventListener("click", () => applyStudyTextEdits());
  resetTextEditsButton.addEventListener("click", () => resetStudyTextEdits());
  loginButton.addEventListener("click", () => {
    void login().catch((error) => setStatus(error.message));
  });
  registerButton.addEventListener("click", () => {
    void register().catch((error) => setStatus(error.message));
  });
  logoutButton.addEventListener("click", () => {
    void logout().catch((error) => setStatus(error.message));
  });
  newStudyButton.addEventListener("click", () => void createNewStudy());
  saveStudyButton.addEventListener("click", () => void saveCurrentStudy());
  undoButton.addEventListener("click", () => void undo());
  redoButton.addEventListener("click", () => void redo());
  clearAnnotationsButton.addEventListener("click", () => clearCurrentAnnotations());
  flipButton.addEventListener("click", () => {
    state.flipped = !state.flipped;
    renderBoard();
    scheduleAutosave();
  });

  studyTitleElement.addEventListener("input", () => {
    state.title = studyTitleElement.value.trim() || "Untitled Study";
    state.studies = state.studies.map((study) =>
      study.id === state.studyId ? { ...study, title: state.title } : study,
    );
    scheduleAutosave();
    renderStudies();
  });

  const engineStatus = await fetchJson("/api/engine-status");
  const aiStatus = await fetchJson("/api/ai-status");
  state.engineEnabled = engineStatus.enabled;
  state.aiEnabled = aiStatus.enabled;
  state.aiModel = aiStatus.model;
  await loadAuthState();
  await refreshStudies();
  const lastStudyId = localStorage.getItem("chessStudy:lastStudyId");
  if (lastStudyId && state.studies.some((study) => study.id === lastStudyId)) {
    await openStudy(lastStudyId);
    return;
  }

  if (state.studies.length > 0) {
    await openStudy(state.studies[0].id);
    return;
  }

  await createNewStudy();
}

bootstrap().catch((error) => {
  setStatus(error.message);
});
