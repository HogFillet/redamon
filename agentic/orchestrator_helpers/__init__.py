"""Orchestrator helper functions.

This module contains helper functions extracted from the main orchestrator
to keep the architectural flow clear and maintainable.
"""

from .json_utils import (
    DateTimeEncoder,
    json_dumps_safe,
    extract_json,
)

from .parsing import (
    parse_llm_decision,
    parse_analysis_response,
)

from .phase import (
    classify_attack_path,
    determine_phase_for_new_objective,
)

from .detection import (
    detect_session_from_output,
    detect_credentials_from_output,
    update_target_with_detections,
)

from .debug import (
    save_graph_image,
)

from .config import (
    set_checkpointer,
    get_checkpointer,
    get_thread_id,
    create_config,
    get_config_values,
    get_identifiers,
    is_session_config_complete,
)

__all__ = [
    # json_utils
    "DateTimeEncoder",
    "json_dumps_safe",
    "extract_json",
    # parsing
    "parse_llm_decision",
    "parse_analysis_response",
    # phase
    "classify_attack_path",
    "determine_phase_for_new_objective",
    # detection
    "detect_session_from_output",
    "detect_credentials_from_output",
    "update_target_with_detections",
    # debug
    "save_graph_image",
    # config
    "set_checkpointer",
    "get_checkpointer",
    "get_thread_id",
    "create_config",
    "get_config_values",
    "get_identifiers",
    "is_session_config_complete",
]
