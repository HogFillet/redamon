"""Session and credential detection helpers for the orchestrator."""

import re
import logging
from typing import Optional, List, Dict, Any, Tuple

from state import TargetInfo

logger = logging.getLogger(__name__)


def detect_session_from_output(
    tool_output: str,
    current_sessions: List[int],
    user_id: str,
    project_id: str,
    session_id: str
) -> Tuple[List[int], bool]:
    """
    Detect session establishment from tool output.

    Args:
        tool_output: Raw output from a tool execution
        current_sessions: Current list of session IDs
        user_id: User identifier for logging
        project_id: Project identifier for logging
        session_id: Session identifier for logging

    Returns:
        Tuple of (updated_sessions, stage_transfer_detected):
        - updated_sessions: Updated list of session IDs
        - stage_transfer_detected: Whether a stage transfer was detected
    """
    if not tool_output:
        return current_sessions, False

    tool_output_lower = tool_output.lower()
    updated_sessions = list(current_sessions)
    stage_transfer_detected = False

    # Detect session establishment from output
    session_match = re.search(
        r'(?:session|Session)\s+(\d+)\s+opened',
        tool_output
    )
    if session_match:
        session_id_detected = int(session_match.group(1))
        if session_id_detected not in updated_sessions:
            updated_sessions.append(session_id_detected)
            logger.info(f"[{user_id}/{project_id}/{session_id}] Detected session {session_id_detected} from exploit output")

    # Detect stage transfer indicator (session may be coming)
    elif "sending stage" in tool_output_lower:
        stage_transfer_detected = True
        logger.info(f"[{user_id}/{project_id}/{session_id}] Stage transfer detected - agent should use msf_wait_for_session")

    return updated_sessions, stage_transfer_detected


def detect_credentials_from_output(
    tool_output: str,
    current_credentials: List[Dict[str, Any]],
    user_id: str,
    project_id: str,
    session_id: str
) -> List[Dict[str, Any]]:
    """
    Detect brute force credential success from tool output.

    Args:
        tool_output: Raw output from a tool execution
        current_credentials: Current list of discovered credentials
        user_id: User identifier for logging
        project_id: Project identifier for logging
        session_id: Session identifier for logging

    Returns:
        Updated list of credentials
    """
    if not tool_output:
        return current_credentials

    updated_credentials = list(current_credentials)

    # Pattern: [+] 10.0.0.5:22 - Success: 'root:toor'
    cred_pattern = r'\[\+\]\s+(\S+):(\d+)\s+-\s+Success:\s+[\'"](\w+):(\S+)[\'"]'
    cred_matches = re.findall(cred_pattern, tool_output)

    for match in cred_matches:
        ip, port, username, password = match
        new_cred = {
            "username": username,
            "password": password,
            "service": f"{ip}:{port}",
            "source": "brute_force"
        }
        # Avoid duplicates
        if new_cred not in updated_credentials:
            updated_credentials.append(new_cred)
            logger.info(f"[{user_id}/{project_id}/{session_id}] Detected credential: {username}@{ip}:{port}")

    return updated_credentials


def update_target_with_detections(
    merged_target: TargetInfo,
    tool_output: str,
    phase: str,
    attack_path_type: str,
    post_expl_phase_type: str,
    user_id: str,
    project_id: str,
    session_id: str
) -> TargetInfo:
    """
    Update target info with detected sessions and credentials.

    Args:
        merged_target: Current merged target info
        tool_output: Raw output from a tool execution
        phase: Current execution phase
        attack_path_type: Type of attack path (cve_exploit, brute_force_credential_guess)
        post_expl_phase_type: Post-exploitation phase type
        user_id: User identifier for logging
        project_id: Project identifier for logging
        session_id: Session identifier for logging

    Returns:
        Updated TargetInfo with detected sessions/credentials
    """
    # Session detection for statefull exploitation
    if post_expl_phase_type == "statefull" and phase == "exploitation":
        new_sessions, _ = detect_session_from_output(
            tool_output,
            merged_target.sessions,
            user_id, project_id, session_id
        )
        if new_sessions != merged_target.sessions:
            merged_target = merged_target.model_copy(update={"sessions": new_sessions})

    # Credential detection for brute force attacks
    if attack_path_type == "brute_force_credential_guess" and phase == "exploitation":
        new_credentials = detect_credentials_from_output(
            tool_output,
            merged_target.credentials,
            user_id, project_id, session_id
        )
        if new_credentials != merged_target.credentials:
            merged_target = merged_target.model_copy(update={"credentials": new_credentials})

    return merged_target
