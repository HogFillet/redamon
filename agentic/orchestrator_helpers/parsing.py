"""LLM response parsing helpers for the orchestrator."""

import json
import re
import logging

from state import LLMDecision, OutputAnalysis, ExtractedTargetInfo
from .json_utils import extract_json

logger = logging.getLogger(__name__)


def parse_llm_decision(response_text: str) -> LLMDecision:
    """Parse LLM decision from JSON response using Pydantic validation."""
    try:
        json_str = extract_json(response_text)
        if json_str:
            # Pre-process JSON to handle empty nested objects that would fail validation
            # LLM sometimes outputs empty objects like user_question: {} or phase_transition: {}
            data = json.loads(json_str)

            # Remove empty user_question object (would fail validation due to required fields)
            if "user_question" in data and (not data["user_question"] or data["user_question"] == {}):
                data["user_question"] = None

            # Remove empty phase_transition object
            if "phase_transition" in data and (not data["phase_transition"] or data["phase_transition"] == {}):
                data["phase_transition"] = None

            return LLMDecision.model_validate(data)
    except Exception as e:
        logger.warning(f"Failed to parse LLM decision: {e}")

    # Fallback - return a completion action with error context
    return LLMDecision(
        thought=response_text,
        reasoning="Failed to parse structured response",
        action="complete",
        completion_reason="Unable to continue due to response parsing error",
        updated_todo_list=[],
    )


def parse_analysis_response(response_text: str) -> OutputAnalysis:
    """Parse analysis response from LLM using Pydantic validation."""
    try:
        json_str = extract_json(response_text)
        if json_str:
            data = json.loads(json_str)

            # Pre-process sessions field to extract integers from strings
            # LLM sometimes returns session descriptions like "Meterpreter session 1 opened..."
            if "extracted_info" in data and "sessions" in data["extracted_info"]:
                sessions = data["extracted_info"]["sessions"]
                parsed_sessions = []
                for item in sessions:
                    if isinstance(item, int):
                        parsed_sessions.append(item)
                    elif isinstance(item, str):
                        # Extract session ID from strings like "Meterpreter session 1 opened..."
                        match = re.search(r'[Ss]ession\s+(\d+)', item)
                        if match:
                            parsed_sessions.append(int(match.group(1)))
                        else:
                            try:
                                parsed_sessions.append(int(item))
                            except ValueError:
                                pass
                data["extracted_info"]["sessions"] = parsed_sessions

            return OutputAnalysis.model_validate(data)
    except Exception as e:
        logger.warning(f"Failed to parse analysis response: {e}")

    # Fallback - extract fields from JSON if possible, even when validation fails
    fallback_interpretation = response_text
    fallback_findings = []
    fallback_next_steps = []

    try:
        json_str = extract_json(response_text)
        if json_str:
            data = json.loads(json_str)
            if "interpretation" in data:
                fallback_interpretation = data["interpretation"]
            if "actionable_findings" in data and isinstance(data["actionable_findings"], list):
                fallback_findings = data["actionable_findings"]
            if "recommended_next_steps" in data and isinstance(data["recommended_next_steps"], list):
                fallback_next_steps = data["recommended_next_steps"]
    except Exception:
        # If JSON extraction also fails, strip markdown code blocks from raw text
        # Remove ```json ... ``` wrapper
        fallback_interpretation = re.sub(r'^```(?:json)?\s*', '', fallback_interpretation)
        fallback_interpretation = re.sub(r'\s*```$', '', fallback_interpretation)
        fallback_interpretation = fallback_interpretation.strip()

    return OutputAnalysis(
        interpretation=fallback_interpretation,
        extracted_info=ExtractedTargetInfo(),
        actionable_findings=fallback_findings,
        recommended_next_steps=fallback_next_steps,
    )
