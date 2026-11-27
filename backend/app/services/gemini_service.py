"""Google Gemini API client and structured prompting for intake, FIRAC, and RAG synthesis."""

import json
import logging
import re
import threading
import time
from typing import Any, List, Optional

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.api.schemas.guidance_schemas import CaseSummaryPayload, ChatMessageOut
from app.api.schemas.retrieval_schemas import JudgmentResult
from app.config import get_settings

logger = logging.getLogger(__name__)

_FALLBACK_MODELS = (
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemma-4-26b-a4b-it",
    "gemini-3.8-flash",
    "gemini-4-hydrogen",
)

_COOLDOWN_LOCK = threading.Lock()
_MODEL_COOLDOWN_UNTIL: dict[str, float] = {}
_QUOTA_COOLDOWN_SECONDS = 600.0
_TIMEOUT_COOLDOWN_SECONDS = 120.0


class GeminiServiceError(RuntimeError):
    """Raised when Gemini API configuration or generation fails."""


class _StructuredSummarySchema(BaseModel):
    problem_type: str = Field(default="")
    jurisdiction: str = Field(default="")
    key_facts: str = Field(default="")
    claimed_harm: str = Field(default="")
    requested_outcome: str = Field(default="")


class _IntakeTurnSchema(BaseModel):
    assistant_reply: str = Field(
        description="Helpful response acknowledging the user's facts in the Indian legal context."
    )
    next_question: Optional[str] = Field(
        default=None,
        description="One concise clarifying follow-up question, or null when sufficient facts exist.",
    )
    ready_for_summary: bool = Field(
        default=False,
        description="True once enough facts are gathered to populate the 5-field case summary.",
    )
    case_summary: Optional[_StructuredSummarySchema] = Field(
        default=None,
        description="Structured 5-field summary when ready_for_summary is true.",
    )


class _FiracMeritSchema(BaseModel):
    firac_text: str = Field(
        description="Neutral 180-260 word formal Indian legal FIRAC brief without outcome leakage."
    )
    merit_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Estimated factual/statutory merit score in [0.0, 1.0] under Indian law.",
    )
    applicable_provisions: List[str] = Field(
        default_factory=list,
        description="Up to 4 relevant Indian Acts, sections, or Constitutional articles governing the dispute.",
    )
    legal_basis_note: str = Field(
        default="",
        description="One concise sentence explaining how those provisions apply to the case.",
    )


def _sanitize_error_message(exc: Exception, api_key_or_keys: str | list[str]) -> str:
    msg = str(exc)
    keys = [api_key_or_keys] if isinstance(api_key_or_keys, str) else list(api_key_or_keys)
    for key in keys:
        if key:
            msg = msg.replace(key, "[REDACTED]")
    return msg


def _build_genai_client(api_key: str) -> genai.Client:
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=15000,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )


def _get_gemini_client() -> tuple[genai.Client, str, str]:
    settings = get_settings()
    keys = settings.gemini_api_keys_list
    if not keys:
        raise GeminiServiceError("GEMINI_API_KEY is not configured in backend/.env.")
    model_name = (settings.GEMINI_MODEL or "gemini-3.5-flash").strip()
    return _build_genai_client(keys[0]), model_name, keys[0]


def _get_configured_api_keys(primary_key: str) -> list[str]:
    settings = get_settings()
    ordered = [primary_key] if primary_key else []
    for extra in settings.gemini_api_keys_list:
        if extra not in ordered:
            ordered.append(extra)
    return ordered


def _cooldown_key(key_idx: int, model_id: str) -> str:
    return f"{key_idx}:{model_id}"


def _candidate_attempts(primary_model: str, num_keys: int) -> list[tuple[int, str]]:
    """Prioritize fast Flash models across current key first, then backup keys, then slower fallbacks."""
    now = time.monotonic()
    fast_models: list[str] = []
    for m in (primary_model, "gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"):
        if m and m not in fast_models:
            fast_models.append(m)
    slow_models = [m for m in _FALLBACK_MODELS if m not in fast_models]

    ordered: list[tuple[int, str]] = []
    for key_idx in range(max(1, num_keys)):
        for model_id in fast_models:
            ordered.append((key_idx, model_id))
    for key_idx in range(max(1, num_keys)):
        for model_id in slow_models:
            ordered.append((key_idx, model_id))

    with _COOLDOWN_LOCK:
        active = [
            pair
            for pair in ordered
            if _MODEL_COOLDOWN_UNTIL.get(_cooldown_key(pair[0], pair[1]), 0.0) <= now
            and _MODEL_COOLDOWN_UNTIL.get(f"key_invalid:{pair[0]}", 0.0) <= now
        ]
    return active if active else ordered


def _mark_model_cooldown_if_persistent(key_idx: int, model_id: str, error_text: str) -> None:
    """Cache cooldown per (key, model) on quota exhaustion, invalid key, retired model, or deadline."""
    upper = error_text.upper()
    if any(tok in upper for tok in ("API_KEY_INVALID", "PERMISSION_DENIED", "401", "403")):
        with _COOLDOWN_LOCK:
            _MODEL_COOLDOWN_UNTIL[f"key_invalid:{key_idx}"] = time.monotonic() + _QUOTA_COOLDOWN_SECONDS
    elif any(tok in upper for tok in ("429", "RESOURCE_EXHAUSTED", "404", "NOT_FOUND")):
        with _COOLDOWN_LOCK:
            _MODEL_COOLDOWN_UNTIL[_cooldown_key(key_idx, model_id)] = (
                time.monotonic() + _QUOTA_COOLDOWN_SECONDS
            )
    elif any(tok in upper for tok in ("504", "DEADLINE_EXCEEDED", "TIMED OUT", "TIMEOUT")):
        with _COOLDOWN_LOCK:
            _MODEL_COOLDOWN_UNTIL[_cooldown_key(key_idx, model_id)] = (
                time.monotonic() + _TIMEOUT_COOLDOWN_SECONDS
            )


def _is_retryable_error(error_text: str) -> bool:
    upper = error_text.upper()
    return any(
        token in upper
        for token in (
            "429",
            "RESOURCE_EXHAUSTED",
            "401",
            "403",
            "API_KEY_INVALID",
            "PERMISSION_DENIED",
            "504",
            "DEADLINE_EXCEEDED",
            "503",
            "UNAVAILABLE",
            "TIMED OUT",
            "TIMEOUT",
            "404",
            "NOT_FOUND",
            "DISCONNECTED",
        )
    )


def _strip_json_fences(raw_text: str) -> str:
    cleaned = raw_text.strip()
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned, re.IGNORECASE)
    if fence_match:
        cleaned = fence_match.group(1).strip()
    return cleaned


def _prepare_model_call(
    model_id: str,
    contents: str,
    config_kwargs: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Adapt generation config for Gemini Flash vs. Gemma instruction-tuned models."""
    attempt_kwargs = dict(config_kwargs)
    is_gemma = "gemma" in model_id.lower()

    if is_gemma:
        sys_inst = attempt_kwargs.pop("system_instruction", None)
        schema = attempt_kwargs.pop("response_schema", None)
        attempt_kwargs.pop("response_mime_type", None)
        parts: list[str] = []
        if sys_inst:
            parts.append(f"Instructions:\n{sys_inst}")
        if schema is not None:
            schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
            parts.append(
                f"Respond ONLY with a valid JSON object matching this JSON schema:\n{schema_json}"
            )
        parts.append(contents)
        return "\n\n".join(parts), attempt_kwargs

    if "lite" not in model_id.lower():
        attempt_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
    return contents, attempt_kwargs


def _invoke_once(
    client: genai.Client,
    model_id: str,
    call_contents: str,
    attempt_kwargs: dict[str, Any],
    api_keys: list[str],
) -> Any:
    try:
        return client.models.generate_content(
            model=model_id,
            contents=call_contents,
            config=types.GenerateContentConfig(**attempt_kwargs),
        )
    except Exception as exc:
        safe_msg = _sanitize_error_message(exc, api_keys)
        if "thinking" in safe_msg.lower() and "thinking_config" in attempt_kwargs:
            retry_kwargs = dict(attempt_kwargs)
            retry_kwargs.pop("thinking_config", None)
            try:
                return client.models.generate_content(
                    model=model_id,
                    contents=call_contents,
                    config=types.GenerateContentConfig(**retry_kwargs),
                )
            except Exception as inner_exc:
                raise GeminiServiceError(_sanitize_error_message(inner_exc, api_keys)) from inner_exc
        raise GeminiServiceError(safe_msg) from exc


def _generate_with_fallback(
    client: genai.Client,
    primary_model: str,
    api_key: str,
    contents: str,
    config_kwargs: dict[str, Any],
) -> Any:
    """Invoke Gemini/Gemma with automatic multi-key rotation, cooldowns, and inline 503 retries."""
    all_keys = _get_configured_api_keys(api_key)
    clients_by_idx: dict[int, genai.Client] = {0: client}
    last_error = ""
    saw_quota = False
    saw_overload = False

    for key_idx, model_id in _candidate_attempts(primary_model, len(all_keys)):
        active_client = clients_by_idx.get(key_idx)
        if active_client is None:
            active_client = _build_genai_client(all_keys[key_idx])
            clients_by_idx[key_idx] = active_client

        call_contents, attempt_kwargs = _prepare_model_call(
            model_id=model_id,
            contents=contents,
            config_kwargs=config_kwargs,
        )

        max_inline_tries = 3 if model_id == "gemini-3.5-flash-lite" else 1
        for inline_try in range(max_inline_tries):
            try:
                return _invoke_once(active_client, model_id, call_contents, attempt_kwargs, all_keys)
            except GeminiServiceError as exc:
                safe_msg = str(exc)
                last_error = safe_msg
                upper = safe_msg.upper()
                is_quota = "429" in upper or "RESOURCE_EXHAUSTED" in upper
                is_transient_503 = "503" in upper or "UNAVAILABLE" in upper

                if is_quota:
                    saw_quota = True
                elif is_transient_503 or "504" in upper or "DEADLINE_EXCEEDED" in upper:
                    saw_overload = True

                if is_transient_503 and inline_try + 1 < max_inline_tries:
                    time.sleep(0.75)
                    continue
                if _is_retryable_error(safe_msg):
                    _mark_model_cooldown_if_persistent(key_idx, model_id, safe_msg)
                    logger.warning(
                        "Key #%d model '%s' unavailable (%s); trying next fallback.",
                        key_idx + 1,
                        model_id,
                        safe_msg[:180],
                    )
                    break
                raise

    if saw_quota and not saw_overload:
        raise GeminiServiceError(
            "API rate/daily quota (429) reached across configured keys and models. "
            "Please wait before retrying or update GEMINI_API_KEY / GEMINI_API_KEYS in backend/.env."
        )
    if saw_quota and saw_overload:
        raise GeminiServiceError(
            "Configured Gemini keys hit free-tier quota (429) and fallback models are temporarily "
            "overloaded (503/504). Please retry in a moment or add keys in backend/.env."
        )
    raise GeminiServiceError(last_error or "All Gemini candidate keys/models failed.")


def _format_transcript(messages: List[ChatMessageOut]) -> str:
    lines: list[str] = []
    for msg in messages:
        speaker = "USER" if msg.role == "user" else "ASSISTANT"
        lines.append(f"{speaker}: {msg.content}")
    return "\n\n".join(lines)


def generate_intake_turn(
    messages: List[ChatMessageOut],
    current_summary: Optional[CaseSummaryPayload] = None,
) -> tuple[str, Optional[str], Optional[CaseSummaryPayload]]:
    """Run one conversational intake turn and extract CaseSummaryPayload when ready."""
    client, model_name, api_key = _get_gemini_client()
    user_turns = sum(1 for m in messages if m.role == "user")

    system_instruction = (
        "You are an academic AI legal guidance assistant focused on the Indian legal context. "
        "Your job during case intake is to gather clear, factual details from the user one step at a time "
        "and build a structured 5-field case summary.\n"
        "Rules:\n"
        "1. Never claim to provide formal legal advice; note briefly that guidance is general information only.\n"
        "2. Ask at most ONE focused follow-up question in `next_question` when critical facts are missing.\n"
        "3. On Turn 1 (user_turns == 1), normally ask 1 clarifying question (`next_question`) and set "
        "`ready_for_summary = false` unless all 5 summary fields are already exhaustively clear.\n"
        "4. Once user_turns >= 2, you MUST set `ready_for_summary = true`, provide practical general Indian "
        "legal information in `assistant_reply` (with a brief non-legal-advice caveat), set `next_question = null` "
        "(unless a field like jurisdiction or relief is completely missing), and populate all 5 fields of "
        "`case_summary` accurately from the user's stated facts ONLY (never invent facts, amounts, or cities).\n"
        "5. In `case_summary.key_facts`, write concise newline-separated factual points."
    )

    summary_context = (
        json.dumps(current_summary.model_dump(), ensure_ascii=False)
        if current_summary is not None
        else "None yet"
    )
    prompt = (
        f"Current user turn count: {user_turns}\n"
        f"Existing draft summary: {summary_context}\n\n"
        f"Conversation transcript:\n{_format_transcript(messages)}"
    )

    try:
        response = _generate_with_fallback(
            client=client,
            primary_model=model_name,
            api_key=api_key,
            contents=prompt,
            config_kwargs={
                "system_instruction": system_instruction,
                "temperature": 0.2,
                "response_mime_type": "application/json",
                "response_schema": _IntakeTurnSchema,
            },
        )
        parsed: Any = getattr(response, "parsed", None)
        if parsed is None:
            raw_text = _strip_json_fences(response.text or "")
            parsed = _IntakeTurnSchema.model_validate_json(raw_text)
    except GeminiServiceError:
        raise
    except Exception as exc:
        safe_msg = _sanitize_error_message(exc, api_key)
        logger.error("Gemini intake turn failed: %s", safe_msg)
        raise GeminiServiceError(f"Gemini intake generation failed: {safe_msg}") from exc

    reply = (parsed.assistant_reply or "").strip()
    if not reply:
        reply = (
            "Thank you for sharing these details. Please note this is general information and not legal advice."
        )

    next_q = parsed.next_question.strip() if parsed.next_question else None
    if next_q == "":
        next_q = None

    extracted_summary: Optional[CaseSummaryPayload] = None
    if (parsed.ready_for_summary or user_turns >= 2) and parsed.case_summary is not None:
        cs = parsed.case_summary
        fields = {
            "problem_type": (cs.problem_type or "").strip(),
            "jurisdiction": (cs.jurisdiction or "").strip(),
            "key_facts": (cs.key_facts or "").strip(),
            "claimed_harm": (cs.claimed_harm or "").strip(),
            "requested_outcome": (cs.requested_outcome or "").strip(),
        }
        if all(fields.values()):
            extracted_summary = CaseSummaryPayload(**fields)

    return reply, next_q, extracted_summary


def generate_rag_guidance(
    confirmed_summary: CaseSummaryPayload,
    messages: List[ChatMessageOut],
    judgments: List[JudgmentResult],
) -> str:
    """Synthesize grounded legal guidance using confirmed summary + 300-judgment RAG passages."""
    client, model_name, api_key = _get_gemini_client()

    system_instruction = (
        "You are an academic AI legal guidance assistant for the Indian legal context. "
        "You are given a user-confirmed case summary and verbatim passages retrieved from a persistent "
        "index of 300 authentic Supreme Court of India judgments.\n"
        "Strict grounding rules:\n"
        "1. Summarize the user's confirmed legal concern, key facts, and requested outcome accurately.\n"
        "2. Ground every precedent reference ONLY in the retrieved judgment excerpts provided below. "
        "Cite exact case titles, citations, and categories as shown.\n"
        "3. If the retrieved judgments address adjacent or different legal subjects than the user's specific "
        "fact pattern, state that transparently and accurately (never force a false analogy or invent precedents).\n"
        "4. Write 2 concise, well-structured paragraphs (plain prose, no markdown headings) and end with a "
        "brief reminder that this is educational information rather than legal advice."
    )

    if judgments:
        precedent_blocks = []
        for idx, j in enumerate(judgments, start=1):
            snippet = " ".join(j.excerpt.split())[:1600]
            precedent_blocks.append(
                f"[{idx}] Title: {j.title}\n"
                f"    Citation: {j.citation} | Date: {j.date or 'N/A'} | Category: {j.category} | "
                f"Match: {j.similarity_score:.1f}%\n"
                f"    Verbatim Excerpt: {snippet}"
            )
        precedents_text = "\n\n".join(precedent_blocks)
    else:
        precedents_text = "No judgment passages were retrieved."

    prompt = (
        "Confirmed Case Summary:\n"
        f"- Problem Type: {confirmed_summary.problem_type}\n"
        f"- Jurisdiction: {confirmed_summary.jurisdiction}\n"
        f"- Key Facts:\n{confirmed_summary.key_facts}\n"
        f"- Claimed Harm: {confirmed_summary.claimed_harm}\n"
        f"- Requested Outcome: {confirmed_summary.requested_outcome}\n\n"
        f"Conversation Context:\n{_format_transcript(messages[-4:])}\n\n"
        f"Retrieved Supreme Court Precedents:\n{precedents_text}"
    )

    try:
        response = _generate_with_fallback(
            client=client,
            primary_model=model_name,
            api_key=api_key,
            contents=prompt,
            config_kwargs={
                "system_instruction": system_instruction,
                "temperature": 0.2,
            },
        )
        text = (response.text or "").strip()
    except GeminiServiceError:
        raise
    except Exception as exc:
        safe_msg = _sanitize_error_message(exc, api_key)
        logger.error("Gemini RAG synthesis failed: %s", safe_msg)
        raise GeminiServiceError(f"Gemini RAG guidance failed: {safe_msg}") from exc

    if not text:
        raise GeminiServiceError("Gemini returned an empty RAG synthesis response.")
    return text


def generate_firac_and_merit(case_text: str) -> tuple[str, float, List[str], str]:
    """Convert confirmed case text into neutral FIRAC text, merit score, and contributing provisions."""
    client, model_name, api_key = _get_gemini_client()

    system_instruction = (
        "You are a legal assistant supporting an Indian legal ML pipeline.\n"
        "Return four fields:\n"
        "1. `firac_text`: Formal, strictly neutral 180-260 word Indian legal FIRAC (Facts, Issues, Rules, Analysis) "
        "brief relying ONLY on stated facts. Never invent dates, amounts, or party names, and NEVER include judicial "
        "disposition phrases like 'appeal allowed', 'appeal dismissed', 'set aside', 'quashed', 'dismissed with costs', "
        "or 'disposed of'. Frame the conclusion strictly as the relief sought.\n"
        "2. `merit_score`: A float in [0.0, 1.0] estimating substantive claim strength under applicable Indian "
        "statutory/civil/labour law strictly from the stated facts, jurisdiction, statutory eligibility (e.g., workman vs. "
        "managerial status), limitation, and documentary evidence:\n"
        "   - 0.75 to 0.92: Clear actionable statutory breach, eligible claimant, proper forum, strong documentary proof "
        "(e.g., appointment letter, pay slips, written payment notices).\n"
        "   - 0.45 to 0.65: Arguable claim with missing/incomplete evidence or disputed threshold issues.\n"
        "   - 0.10 to 0.38: Weak, unsubstantiated, time-barred, non-maintainable, or statutorily excluded claim.\n"
        "3. `applicable_provisions`: A short list of 2 to 4 relevant Indian Acts, specific Sections, or Constitutional "
        "Articles that govern this dispute (for example, 'Section 15, Payment of Wages Act, 1936', "
        "'Section 2(s) & 33C(2), Industrial Disputes Act, 1947', or relevant civil/criminal/constitutional provisions).\n"
        "4. `legal_basis_note`: Exactly one concise, plain sentence (15-30 words) explaining how these provisions "
        "relate to the facts and outcome without hedging or markdown."
    )

    try:
        response = _generate_with_fallback(
            client=client,
            primary_model=model_name,
            api_key=api_key,
            contents=f"Confirmed case details:\n{case_text}",
            config_kwargs={
                "system_instruction": system_instruction,
                "temperature": 0.15,
                "response_mime_type": "application/json",
                "response_schema": _FiracMeritSchema,
            },
        )
        parsed: Any = getattr(response, "parsed", None)
        if parsed is None:
            raw_text = _strip_json_fences(response.text or "")
            parsed = _FiracMeritSchema.model_validate_json(raw_text)
        firac_text = (parsed.firac_text or "").strip()
        merit_score = max(0.0, min(1.0, float(parsed.merit_score)))
        provisions = [
            str(item).strip()
            for item in (parsed.applicable_provisions or [])
            if str(item).strip()
        ][:4]
        basis_note = " ".join((parsed.legal_basis_note or "").split()).strip()
    except GeminiServiceError:
        raise
    except Exception as exc:
        safe_msg = _sanitize_error_message(exc, api_key)
        logger.error("Gemini FIRAC/merit formatting failed: %s", safe_msg)
        raise GeminiServiceError(f"Gemini FIRAC formatting failed: {safe_msg}") from exc

    if not firac_text:
        raise GeminiServiceError("Gemini returned an empty FIRAC representation.")
    return firac_text, merit_score, provisions, basis_note


def generate_firac_case_input(case_text: str) -> str:
    """Convert confirmed case text into a neutral FIRAC representation for RF Experiment 3."""
    firac_text, _, _, _ = generate_firac_and_merit(case_text)
    return firac_text
