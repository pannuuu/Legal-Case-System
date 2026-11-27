import { API_BASE_URL } from './retrievalService.js';

const KNOWN_CASE_TYPES = [
  'special leave petition',
  'arbitration appeal',
  'contempt petition',
  'curative petition',
  'election petition',
  'review petition',
  'tax reference case',
  'transfer petition',
  'transferred case',
  'writ petition',
  'appeal',
];

function inferCaseCategory(combinedText) {
  const lower = combinedText.toLowerCase();
  if (
    /\b(criminal|fir|bail|ipc|bns|crpc|bnss|murder|assault|theft|cheating|fraud|conviction|acquittal|offence|offense|prosecution)\b/.test(
      lower
    )
  ) {
    return 'criminal';
  }
  if (
    /\b(civil|salary|wage|wages|employment|workman|labour|labor|contract|property|land|arbitration|consumer|tax|compensation|divorce|maintenance|recovery|suit|writ)\b/.test(
      lower
    )
  ) {
    return 'civil';
  }
  return 'unknown';
}

function inferCaseType(combinedText) {
  const lower = combinedText.toLowerCase();
  for (const candidate of KNOWN_CASE_TYPES) {
    if (lower.includes(candidate)) {
      return candidate;
    }
  }
  return null;
}

export function buildPredictionPayload(summary, messages = []) {
  const userNarrative = messages
    .filter((msg) => msg.role === 'user')
    .map((msg) => msg.content.trim())
    .filter(Boolean)
    .join('\n');

  const summaryBlock = [
    summary?.problemType ? `Problem Type: ${summary.problemType}` : '',
    summary?.jurisdiction ? `Jurisdiction: ${summary.jurisdiction}` : '',
    summary?.keyFacts ? `Key Facts:\n${summary.keyFacts}` : '',
    summary?.claimedHarm ? `Claimed Harm: ${summary.claimedHarm}` : '',
    summary?.requestedOutcome ? `Requested Outcome: ${summary.requestedOutcome}` : '',
  ]
    .filter(Boolean)
    .join('\n');

  const caseText = [summaryBlock, userNarrative].filter(Boolean).join('\n\n').trim();

  return {
    case_text: caseText,
    use_firac: true,
    metadata: {
      case_category: inferCaseCategory(caseText),
      case_type: inferCaseType(caseText),
    },
  };
}

export async function predictCaseOutcome(summary, messages = []) {
  const payload = buildPredictionPayload(summary, messages);
  if (!payload.case_text) {
    throw new Error('Confirmed case details are required before running outcome prediction.');
  }

  const response = await fetch(`${API_BASE_URL}/api/prediction/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let detail = `Prediction request failed (HTTP ${response.status}).`;
    try {
      const errorBody = await response.json();
      if (errorBody?.detail) {
        detail =
          typeof errorBody.detail === 'string'
            ? errorBody.detail
            : JSON.stringify(errorBody.detail);
      }
    } catch {
      // Keep fallback message when body is not JSON.
    }
    throw new Error(detail);
  }

  const data = await response.json();
  const acceptedPct = Number(data?.probabilities?.accepted ?? 0) * 100;
  const rejectedPct = Number(data?.probabilities?.rejected ?? 0) * 100;
  const confidencePct = Number(data?.confidence ?? 0) * 100;

  return {
    model: data.model || 'Random Forest Experiment 3',
    classId: data.class_id,
    predictedClass: data.predicted_class,
    predictedOutcome: data.predicted_outcome,
    confidence: Number(confidencePct.toFixed(1)),
    acceptedProbability: Number(acceptedPct.toFixed(1)),
    rejectedProbability: Number(rejectedPct.toFixed(1)),
    featureCount: data.feature_count,
    matchedTfidfTerms: data.matched_tfidf_terms,
    inputMode: data.input_mode,
    applicableProvisions: Array.isArray(data.applicable_provisions)
      ? data.applicable_provisions
      : [],
    legalBasisNote:
      typeof data.legal_basis_note === 'string' ? data.legal_basis_note : '',
    metadataUsed: data.metadata_used,
  };
}
