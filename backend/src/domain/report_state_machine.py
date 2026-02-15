"""Report state machine and transition validation."""

from typing import Any

from src.db.models import ReportStatus


class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    pass


# Valid state transitions map
VALID_TRANSITIONS: dict[ReportStatus, set[ReportStatus]] = {
    ReportStatus.UPLOADED: {
        ReportStatus.PARSING,
        ReportStatus.FAILED,
        ReportStatus.DUPLICATE,
    },
    ReportStatus.PARSING: {
        ReportStatus.REVIEW_PENDING,
        ReportStatus.FAILED,
    },
    ReportStatus.REVIEW_PENDING: {
        ReportStatus.EDITING,
        ReportStatus.GENERATING_BUNDLE,
        ReportStatus.FAILED,
    },
    ReportStatus.EDITING: {
        ReportStatus.REVIEW_PENDING,
        ReportStatus.GENERATING_BUNDLE,
        ReportStatus.FAILED,
    },
    ReportStatus.GENERATING_BUNDLE: {
        ReportStatus.COMPLETED,
        ReportStatus.FAILED,
    },
    ReportStatus.REGENERATING_BUNDLE: {
        ReportStatus.COMPLETED,
        ReportStatus.FAILED,
    },
    ReportStatus.COMPLETED: {
        ReportStatus.REGENERATING_BUNDLE,
        ReportStatus.EDITING,
    },
    ReportStatus.FAILED: {
        ReportStatus.PARSING,  # Allow retry from failed parsing
        ReportStatus.GENERATING_BUNDLE,  # Allow retry from failed generation
    },
    ReportStatus.DUPLICATE: set(),  # Terminal state
}


def can_transition(from_status: ReportStatus, to_status: ReportStatus) -> bool:
    """
    Check if a state transition is valid.

    Args:
        from_status: Current report status
        to_status: Desired new status

    Returns:
        True if transition is valid, False otherwise
    """
    return to_status in VALID_TRANSITIONS.get(from_status, set())


def validate_transition(from_status: ReportStatus, to_status: ReportStatus) -> None:
    """
    Validate a state transition and raise an error if invalid.

    Args:
        from_status: Current report status
        to_status: Desired new status

    Raises:
        StateTransitionError: If the transition is invalid
    """
    if not can_transition(from_status, to_status):
        raise StateTransitionError(
            f"Invalid state transition from {from_status.value} to {to_status.value}"
        )


def get_allowed_transitions(status: ReportStatus) -> set[ReportStatus]:
    """
    Get all allowed transitions from a given status.

    Args:
        status: Current report status

    Returns:
        Set of allowed next statuses
    """
    return VALID_TRANSITIONS.get(status, set()).copy()


def is_terminal_status(status: ReportStatus) -> bool:
    """
    Check if a status is terminal (no valid transitions).

    Args:
        status: Report status to check

    Returns:
        True if status is terminal, False otherwise
    """
    return len(VALID_TRANSITIONS.get(status, set())) == 0


def get_status_metadata(status: ReportStatus) -> dict[str, Any]:
    """
    Get metadata about a status.

    Args:
        status: Report status

    Returns:
        Dictionary with status metadata
    """
    return {
        "status": status.value,
        "is_terminal": is_terminal_status(status),
        "allowed_transitions": [s.value for s in get_allowed_transitions(status)],
        "is_processing": status
        in {
            ReportStatus.PARSING,
            ReportStatus.GENERATING_BUNDLE,
            ReportStatus.REGENERATING_BUNDLE,
        },
        "is_user_actionable": status
        in {
            ReportStatus.REVIEW_PENDING,
            ReportStatus.EDITING,
            ReportStatus.FAILED,
        },
        "is_success": status == ReportStatus.COMPLETED,
        "is_error": status == ReportStatus.FAILED,
    }
