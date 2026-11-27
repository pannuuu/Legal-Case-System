export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(
  /\/+$/,
  ''
);

export function buildRetrievalQuery(summary) {
  if (!summary) {
    return '';
  }

  return [
    summary.problemType ? `Problem type: ${summary.problemType}` : '',
    summary.jurisdiction ? `Jurisdiction: ${summary.jurisdiction}` : '',
    summary.keyFacts ? `Key facts: ${summary.keyFacts}` : '',
    summary.claimedHarm ? `Claimed harm: ${summary.claimedHarm}` : '',
    summary.requestedOutcome ? `Requested outcome: ${summary.requestedOutcome}` : '',
  ]
    .filter(Boolean)
    .join('\n');
}

export function mapJudgmentRecord(item) {
  return {
    id: item.id,
    court: item.court || 'SUPREME COURT OF INDIA',
    title: item.title,
    citation: item.citation,
    date: item.date,
    category: item.category,
    similarityScore: item.similarity_score,
    semanticScore: item.semantic_score,
    lexicalScore: item.lexical_score,
    excerpt: item.excerpt,
    offsetStart: item.offset_start,
    offsetEnd: item.offset_end,
    context: item.context,
  };
}

export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function searchSimilarJudgments(summary, topK = 5) {
  const queryText = buildRetrievalQuery(summary);
  if (!queryText.trim()) {
    throw new Error('Cannot retrieve similar judgments without a confirmed case summary.');
  }

  const response = await fetch(`${API_BASE_URL}/api/retrieval/judgments/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query_text: queryText,
      top_k: topK,
    }),
  });

  if (!response.ok) {
    let detail = `Retrieval request failed with status ${response.status}.`;
    try {
      const errorPayload = await response.json();
      if (errorPayload?.detail) {
        detail = String(errorPayload.detail);
      }
    } catch {
      // Keep fallback message when body is not JSON.
    }
    throw new Error(detail);
  }

  const payload = await response.json();
  const records = Array.isArray(payload.judgments) ? payload.judgments : [];
  return records.map(mapJudgmentRecord);
}
