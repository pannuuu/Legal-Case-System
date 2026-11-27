import { API_BASE_URL, mapJudgmentRecord } from './retrievalService.js';

function toSummaryApiPayload(summary) {
  return {
    problem_type: summary.problemType,
    jurisdiction: summary.jurisdiction,
    key_facts: summary.keyFacts,
    claimed_harm: summary.claimedHarm,
    requested_outcome: summary.requestedOutcome,
  };
}

function fromSummaryApiPayload(raw) {
  if (!raw) {
    return null;
  }
  return {
    problemType: raw.problem_type || '',
    jurisdiction: raw.jurisdiction || '',
    keyFacts: raw.key_facts || '',
    claimedHarm: raw.claimed_harm || '',
    requestedOutcome: raw.requested_outcome || '',
  };
}

async function buildApiError(response, fallback) {
  let detail = `${fallback} (HTTP ${response.status})`;
  try {
    const body = await response.json();
    if (body?.detail) {
      detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
    }
  } catch {
    // Keep fallback message when body is not JSON.
  }
  const error = new Error(detail);
  error.status = response.status;
  return error;
}

export async function createGuidanceSession() {
  const response = await fetch(`${API_BASE_URL}/api/guidance/sessions`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw await buildApiError(response, 'Failed to create guidance session');
  }
  return response.json();
}

export async function sendGuidanceMessage(sessionId, message, history = null) {
  const payload = history && history.length > 0 ? { message, history } : { message };
  const response = await fetch(`${API_BASE_URL}/api/guidance/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw await buildApiError(response, 'Failed to process guidance message');
  }
  const data = await response.json();
  return {
    sessionId: data.session_id,
    userMessage: data.user_message,
    assistantMessage: data.assistant_message,
    nextQuestion: data.next_question || null,
    summary: fromSummaryApiPayload(data.summary),
    summaryConfirmed: Boolean(data.summary_confirmed),
  };
}

export async function saveSummaryRevision(sessionId, summary) {
  const response = await fetch(`${API_BASE_URL}/api/guidance/sessions/${sessionId}/summary`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(toSummaryApiPayload(summary)),
  });
  if (!response.ok) {
    throw await buildApiError(response, 'Failed to save summary revision');
  }
  const data = await response.json();
  return fromSummaryApiPayload(data.summary);
}

export async function confirmSummaryAndSynthesize(sessionId, summary) {
  const response = await fetch(`${API_BASE_URL}/api/guidance/sessions/${sessionId}/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(toSummaryApiPayload(summary)),
  });
  if (!response.ok) {
    throw await buildApiError(response, 'Failed to confirm summary');
  }
  const data = await response.json();
  return {
    confirmedSummary: fromSummaryApiPayload(data.summary),
    synthesisMessage: data.assistant_message,
    judgments: Array.isArray(data.judgments) ? data.judgments.map(mapJudgmentRecord) : [],
  };
}
