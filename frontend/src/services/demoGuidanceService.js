/**
 * Isolated temporary frontend demonstration interaction layer for Phase 3.
 * Simulates conversational intake and preliminary draft summary extraction
 * without fabricating legal judgments or Random Forest outcome predictions.
 * This module will be replaced by real FastAPI service calls in later phases.
 */

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function extractJurisdiction(text) {
  const cityMatch = text.match(
    /\b(Bengaluru|Bangalore|Mumbai|Delhi|New Delhi|Chennai|Kolkata|Hyderabad|Pune|Ahmedabad|Jaipur|Kochi|Lucknow|Chandigarh)\b/i
  );
  if (cityMatch) {
    return `${cityMatch[1]}, India`;
  }
  return 'India (to be specified)';
}

function inferProblemType(text) {
  const lower = text.toLowerCase();
  if (lower.includes('salary') || lower.includes('wages') || lower.includes('employer')) {
    return 'Employment & unpaid wages';
  }
  if (lower.includes('tenant') || lower.includes('rent') || lower.includes('landlord') || lower.includes('evict')) {
    return 'Tenancy & property dispute';
  }
  if (lower.includes('contract') || lower.includes('breach') || lower.includes('agreement')) {
    return 'Contractual dispute';
  }
  if (lower.includes('consumer') || lower.includes('refund') || lower.includes('defective')) {
    return 'Consumer protection dispute';
  }
  return 'General legal concern (draft)';
}

function buildDraftSummary(conversationMessages) {
  const userEntries = conversationMessages
    .filter((msg) => msg.role === 'user')
    .map((msg) => msg.content.trim());
  const combined = userEntries.join('\n');

  const keyFacts = userEntries
    .flatMap((entry) =>
      entry
        .split(/(?<=[.!?])\s+/)
        .map((line) => line.trim())
        .filter(Boolean)
    )
    .slice(0, 5)
    .join('\n');

  return {
    problemType: inferProblemType(combined),
    jurisdiction: extractJurisdiction(combined),
    keyFacts: keyFacts || combined,
    claimedHarm: userEntries[0]
      ? `Reported concern: ${userEntries[0].slice(0, 120)}${userEntries[0].length > 120 ? '...' : ''}`
      : '',
    requestedOutcome: 'Legal guidance and review of applicable remedies',
  };
}

export async function submitDemoIntakeMessage(currentMessages, userInput) {
  await delay(550);

  const nextMessages = [
    ...currentMessages,
    {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userInput,
    },
  ];

  const userTurnCount = nextMessages.filter((msg) => msg.role === 'user').length;

  if (userTurnCount === 1) {
    return {
      assistantMessage: {
        id: `assistant-${Date.now() + 1}`,
        role: 'assistant',
        content:
          'Thank you for sharing the initial facts. To prepare a clearer case summary for the Indian legal context, please clarify one key detail below.',
      },
      nextQuestion:
        'What specific supporting documents, dates, or legal status (such as employment terms, written agreements, or prior notices) apply to your situation?',
      draftSummary: null,
    };
  }

  return {
    assistantMessage: {
      id: `assistant-${Date.now() + 1}`,
      role: 'assistant',
      content:
        'I have captured your additional context and prepared a preliminary draft case summary in Section 02 below. Please review and edit every field before confirming. Note: this frontend demonstration provides general informational framing only and not legal advice.',
    },
    nextQuestion: null,
    draftSummary: buildDraftSummary(nextMessages),
  };
}

export async function saveDemoSummaryRevision(summaryValues) {
  await delay(300);
  return { ...summaryValues };
}

export async function confirmDemoSummary(summaryValues) {
  await delay(450);
  return {
    confirmedSummary: { ...summaryValues },
    synthesisMessage: {
      id: `assistant-confirm-${Date.now()}`,
      role: 'assistant',
      content: `Case summary confirmed for "${summaryValues.problemType}" (${summaryValues.jurisdiction}). Downstream sections 03 (Similar Judgments) and 04 (Random Forest Outcome Prediction) are now unlocked and ready for backend integration.`,
    },
  };
}
