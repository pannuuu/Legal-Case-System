import { useEffect, useState } from 'react';
import Header from './components/Header.jsx';
import HeroBanner from './components/HeroBanner.jsx';
import WorkflowSidebar from './components/WorkflowSidebar.jsx';
import CaseIntakeSection from './components/CaseIntakeSection.jsx';
import CaseSummarySection from './components/CaseSummarySection.jsx';
import SimilarJudgmentsSection from './components/SimilarJudgmentsSection.jsx';
import OutcomePredictionSection from './components/OutcomePredictionSection.jsx';
import Footer from './components/Footer.jsx';
import {
  confirmSummaryAndSynthesize,
  createGuidanceSession,
  saveSummaryRevision,
  sendGuidanceMessage,
} from './services/guidanceService.js';
import { checkBackendHealth } from './services/retrievalService.js';
import { predictCaseOutcome } from './services/predictionService.js';

const INITIAL_SUMMARY_ERRORS = {
  problemType: '',
  jurisdiction: '',
  keyFacts: '',
  claimedHarm: '',
  requestedOutcome: '',
};

function validateSummaryFields(values) {
  const errors = { ...INITIAL_SUMMARY_ERRORS };
  let isValid = true;

  if (!values.problemType.trim()) {
    errors.problemType = 'Problem type is required.';
    isValid = false;
  }
  if (!values.jurisdiction.trim()) {
    errors.jurisdiction = 'Jurisdiction is required.';
    isValid = false;
  }
  if (!values.keyFacts.trim()) {
    errors.keyFacts = 'Key facts are required.';
    isValid = false;
  }
  if (!values.claimedHarm.trim()) {
    errors.claimedHarm = 'Claimed harm is required.';
    isValid = false;
  }
  if (!values.requestedOutcome.trim()) {
    errors.requestedOutcome = 'Requested outcome is required.';
    isValid = false;
  }

  return { isValid, errors };
}

function App() {
  const [activeTab, setActiveTab] = useState('guidance');
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  const [messages, setMessages] = useState([]);
  const [nextQuestion, setNextQuestion] = useState(null);
  const [draftMessage, setDraftMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [intakeError, setIntakeError] = useState('');

  const [summary, setSummary] = useState(null);
  const [summaryErrors, setSummaryErrors] = useState(INITIAL_SUMMARY_ERRORS);
  const [isSummaryConfirmed, setIsSummaryConfirmed] = useState(false);
  const [isSavingSummary, setIsSavingSummary] = useState(false);
  const [isConfirmingSummary, setIsConfirmingSummary] = useState(false);
  const [summaryFeedback, setSummaryFeedback] = useState('');

  const [judgments, setJudgments] = useState([]);
  const [isLoadingJudgments, setIsLoadingJudgments] = useState(false);
  const [judgmentsError, setJudgmentsError] = useState('');

  const [prediction, setPrediction] = useState(null);
  const [isLoadingPrediction, setIsLoadingPrediction] = useState(false);
  const [predictionError, setPredictionError] = useState('');

  useEffect(() => {
    let active = true;

    const refreshHealth = async () => {
      const ok = await checkBackendHealth();
      if (!active) {
        return;
      }
      setIsConnected(ok);
      if (ok && !sessionId) {
        try {
          const session = await createGuidanceSession();
          if (active) {
            setSessionId(session.session_id);
          }
        } catch {
          // Session will be created on demand on first message.
        }
      }
    };

    refreshHealth();
    const intervalId = window.setInterval(() => {
      if (!isConnected) {
        refreshHealth();
      }
    }, 4000);
    window.addEventListener('focus', refreshHealth);

    return () => {
      active = false;
      window.clearInterval(intervalId);
      window.removeEventListener('focus', refreshHealth);
    };
  }, [isConnected, sessionId]);

  const ensureSessionId = async () => {
    if (sessionId) {
      return sessionId;
    }
    const created = await createGuidanceSession();
    setSessionId(created.session_id);
    return created.session_id;
  };

  const scrollToSection = (sectionId) => {
    window.requestAnimationFrame(() => {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  };

  const handleSelectTab = (tabId) => {
    setActiveTab(tabId);
    if (tabId === 'guidance') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (tabId === 'judgments') {
      scrollToSection('section-judgments');
    } else if (tabId === 'prediction') {
      scrollToSection('section-prediction');
    }
  };

  const handleSelectWorkflowStep = (target) => {
    if (target === 'section-intake' || target === 'section-summary') {
      setActiveTab('guidance');
      scrollToSection(target);
      return;
    }
    if (target === 'section-judgments') {
      handleSelectTab('judgments');
      return;
    }
    if (target === 'section-prediction') {
      handleSelectTab('prediction');
    }
  };

  const handleNewCase = async () => {
    setActiveTab('guidance');
    setSessionId(null);
    setMessages([]);
    setNextQuestion(null);
    setDraftMessage('');
    setIsSending(false);
    setIntakeError('');
    setSummary(null);
    setSummaryErrors(INITIAL_SUMMARY_ERRORS);
    setIsSummaryConfirmed(false);
    setIsSavingSummary(false);
    setIsConfirmingSummary(false);
    setSummaryFeedback('');
    setJudgments([]);
    setIsLoadingJudgments(false);
    setJudgmentsError('');
    setPrediction(null);
    setIsLoadingPrediction(false);
    setPredictionError('');
    window.scrollTo({ top: 0, behavior: 'smooth' });

    try {
      const session = await createGuidanceSession();
      setSessionId(session.session_id);
      setIsConnected(true);
    } catch {
      // Session will be created lazily on next submit if backend is starting.
    }
  };

  const withSessionRecovery = async (action, priorHistory = null) => {
    const currentId = await ensureSessionId();
    try {
      return await action(currentId, null);
    } catch (err) {
      if (err?.status === 404) {
        const fresh = await createGuidanceSession();
        setSessionId(fresh.session_id);
        return await action(fresh.session_id, priorHistory);
      }
      throw err;
    }
  };

  const handleSendMessage = async () => {
    const trimmed = draftMessage.trim();
    if (!trimmed || isSending) {
      return;
    }

    const optimisticUserMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: trimmed,
    };

    const previousMessages = messages;
    const historySnapshot = previousMessages.map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    setMessages([...previousMessages, optimisticUserMsg]);
    setDraftMessage('');
    setIntakeError('');
    setIsSending(true);

    try {
      const result = await withSessionRecovery(
        (activeId, recoveredHistory) =>
          sendGuidanceMessage(activeId, trimmed, recoveredHistory),
        historySnapshot
      );
      setIsConnected(true);

      setMessages([
        ...previousMessages,
        result.userMessage,
        result.assistantMessage,
      ]);
      setNextQuestion(result.nextQuestion);

      if (result.summary) {
        setSummary(result.summary);
        setSummaryErrors(INITIAL_SUMMARY_ERRORS);
        setIsSummaryConfirmed(result.summaryConfirmed);
        setSummaryFeedback('');
      }
    } catch (err) {
      if (err instanceof TypeError) {
        setIsConnected(false);
      }
      setMessages(previousMessages);
      setDraftMessage(trimmed);
      setIntakeError(
        err?.message || 'Unable to reach the legal guidance service. Please try again.'
      );
    } finally {
      setIsSending(false);
    }
  };

  const handleSummaryFieldChange = (field, value) => {
    setSummary((prev) => (prev ? { ...prev, [field]: value } : prev));
    setSummaryErrors((prev) => ({ ...prev, [field]: '' }));
    setIsSummaryConfirmed(false);
    setSummaryFeedback('');
  };

  const handleSaveRevision = async () => {
    if (!summary || isSavingSummary || isConfirmingSummary) {
      return;
    }

    const { isValid, errors } = validateSummaryFields(summary);
    setSummaryErrors(errors);
    if (!isValid) {
      setSummaryFeedback('Please complete all required summary fields before saving.');
      return;
    }

    setIsSavingSummary(true);
    setSummaryFeedback('');
    try {
      const saved = await withSessionRecovery((activeId) =>
        saveSummaryRevision(activeId, summary)
      );
      setSummary(saved);
      setSummaryFeedback('Revision saved.');
    } catch (err) {
      if (err instanceof TypeError) {
        setIsConnected(false);
      }
      setSummaryFeedback(err?.message || 'Failed to save revision.');
    } finally {
      setIsSavingSummary(false);
    }
  };

  const handleConfirmSummary = async () => {
    if (!summary || isSavingSummary || isConfirmingSummary) {
      return;
    }

    const { isValid, errors } = validateSummaryFields(summary);
    setSummaryErrors(errors);
    if (!isValid) {
      setSummaryFeedback('Please complete all required summary fields before confirming.');
      return;
    }

    setIsConfirmingSummary(true);
    setIsLoadingJudgments(true);
    setIsLoadingPrediction(true);
    setJudgmentsError('');
    setPredictionError('');
    setSummaryFeedback('');

    try {
      const [ragSettled, predSettled] = await Promise.allSettled([
        withSessionRecovery((activeId) =>
          confirmSummaryAndSynthesize(activeId, summary)
        ),
        predictCaseOutcome(summary, messages),
      ]);

      if (ragSettled.status === 'fulfilled') {
        const result = ragSettled.value;
        setIsConnected(true);
        setSummary(result.confirmedSummary);
        setIsSummaryConfirmed(true);
        setNextQuestion(null);
        setJudgments(result.judgments);
        setMessages((prev) => [...prev, result.synthesisMessage]);
        setSummaryFeedback(
          `Summary confirmed. Retrieved ${result.judgments.length} relevant precedent passages.`
        );
      } else {
        const err = ragSettled.reason;
        if (err instanceof TypeError) {
          setIsConnected(false);
        }
        setJudgmentsError(err?.message || 'Unable to complete RAG synthesis and retrieval.');
        setSummaryFeedback(err?.message || 'Failed to confirm summary.');
      }

      if (predSettled.status === 'fulfilled') {
        setPrediction(predSettled.value);
      } else {
        const predErr = predSettled.reason;
        if (predErr instanceof TypeError) {
          setIsConnected(false);
        }
        setPrediction(null);
        setPredictionError(predErr?.message || 'Unable to compute Random Forest outcome prediction.');
      }
    } finally {
      setIsConfirmingSummary(false);
      setIsLoadingJudgments(false);
      setIsLoadingPrediction(false);
    }
  };

  const workflowSteps = [
    {
      number: '01',
      title: 'Share your concern',
      subtitle:
        messages.length > 0
          ? `${messages.filter((m) => m.role === 'user').length} message(s) shared`
          : 'Conversational guidance',
      active: true,
      completed: Boolean(summary),
      target: 'section-intake',
    },
    {
      number: '02',
      title: 'Review your summary',
      subtitle: isSummaryConfirmed ? 'Confirmed ✓' : 'Review key facts',
      active: Boolean(summary),
      completed: isSummaryConfirmed,
      target: 'section-summary',
    },
    {
      number: '03',
      title: 'Explore references',
      subtitle: isLoadingJudgments
        ? 'Searching index...'
        : judgments.length > 0
          ? `${judgments.length} retrieved`
          : isSummaryConfirmed
            ? 'Retrieval attempted'
            : 'Persistent index',
      active: isSummaryConfirmed,
      completed: judgments.length > 0,
      target: 'section-judgments',
    },
    {
      number: '04',
      title: 'Experimental prediction',
      subtitle: isLoadingPrediction
        ? 'Running Random Forest...'
        : prediction
          ? `Random Forest (${prediction.predictedClass})`
          : isSummaryConfirmed
            ? 'Prediction attempted'
            : 'Random Forest inputs',
      active: isSummaryConfirmed,
      completed: Boolean(prediction),
      target: 'section-prediction',
    },
  ];

  const isGuidanceView = activeTab === 'guidance';

  return (
    <div className="app-shell">
      <Header
        activeTab={activeTab}
        onSelectTab={handleSelectTab}
        onNewCase={handleNewCase}
        isConnected={isConnected}
      />

      <main className="app-main">
        {isGuidanceView ? (
          <>
            <HeroBanner />
            <div className="guidance-grid">
              <div className="guidance-main-column">
                <CaseIntakeSection
                  messages={messages}
                  nextQuestion={nextQuestion}
                  draftMessage={draftMessage}
                  onDraftChange={setDraftMessage}
                  onSendMessage={handleSendMessage}
                  isSending={isSending}
                  errorMessage={intakeError}
                />

                <CaseSummarySection
                  summary={summary}
                  isConfirmed={isSummaryConfirmed}
                  errors={summaryErrors}
                  onChangeField={handleSummaryFieldChange}
                  onSaveRevision={handleSaveRevision}
                  onConfirmSummary={handleConfirmSummary}
                  isSaving={isSavingSummary}
                  isConfirming={isConfirmingSummary}
                  feedbackMessage={summaryFeedback}
                />

                <SimilarJudgmentsSection
                  judgments={judgments}
                  isSummaryConfirmed={isSummaryConfirmed}
                  isLoading={isLoadingJudgments}
                  isPreview={!isSummaryConfirmed && judgments.length === 0 && !isLoadingJudgments}
                  errorMessage={judgmentsError}
                />
              </div>

              <WorkflowSidebar
                steps={workflowSteps}
                onSelectStep={handleSelectWorkflowStep}
              />
            </div>
          </>
        ) : (
          <div className="results-stack">
            <SimilarJudgmentsSection
              judgments={judgments}
              isSummaryConfirmed={isSummaryConfirmed}
              isLoading={isLoadingJudgments}
              isPreview={false}
              errorMessage={judgmentsError}
            />

            <OutcomePredictionSection
              prediction={prediction}
              isSummaryConfirmed={isSummaryConfirmed}
              isLoading={isLoadingPrediction}
              errorMessage={predictionError}
            />
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}

export default App;
