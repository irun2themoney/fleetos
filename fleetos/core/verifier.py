"""
Verifier: VerdictNet-style confidence scoring and human approval gates.

Scores agent outputs (0-100 confidence) and routes low-confidence actions
to human approval via Telegram before execution.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ActionRisk(Enum):
    """Risk levels for actions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Verifier:
    """
    Verifies and gates agent actions based on confidence scoring.

    Example:
        verifier = Verifier()
        score = verifier.score_action("send_email", action_data)
        if score < 80:
            verifier.request_approval("user_id", "send_email", action_data)
    """

    def __init__(self):
        """Initialize verifier."""
        # Risk thresholds
        self.confidence_thresholds = {
            ActionRisk.LOW: 50,       # Low risk: approve if > 50% confidence
            ActionRisk.MEDIUM: 70,    # Medium risk: approve if > 70% confidence
            ActionRisk.HIGH: 85,      # High risk: approve if > 85% confidence
            ActionRisk.CRITICAL: 95,  # Critical: approve if > 95% confidence
        }

        logger.info("Verifier initialized")

    def score_action(
        self,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> float:
        """
        Score confidence in an agent action.

        Args:
            action_type: Type of action (e.g., "send_email", "charge_card")
            action_data: Action details

        Returns:
            Confidence score (0-100)
        """
        risk_level = self._classify_risk(action_type)
        score = self._calculate_confidence(action_data)

        logger.info(
            f"Scored action '{action_type}': {score:.1f}% "
            f"(risk: {risk_level.value})"
        )

        return score

    def should_approve_automatically(
        self,
        action_type: str,
        confidence_score: float
    ) -> bool:
        """
        Determine if action should be approved automatically.

        Args:
            action_type: Type of action
            confidence_score: Confidence score (0-100)

        Returns:
            True if auto-approval okay, False if human approval needed
        """
        risk_level = self._classify_risk(action_type)
        threshold = self.confidence_thresholds[risk_level]

        approved = confidence_score >= threshold

        action = "approved" if approved else "REQUIRES HUMAN APPROVAL"
        logger.info(
            f"Auto-approval decision for '{action_type}': {action} "
            f"({confidence_score:.1f}% >= {threshold}%)"
        )

        return approved

    def request_approval(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any],
        confidence_score: float
    ) -> str:
        """
        Request human approval for an action.

        Args:
            user_id: User ID for approval
            action_type: Type of action
            action_data: Action details
            confidence_score: Confidence score

        Returns:
            Approval request ID
        """
        request_id = f"approval_{datetime.utcnow().timestamp()}"

        approval_message = self._format_approval_message(
            action_type,
            action_data,
            confidence_score
        )

        logger.info(f"Requesting approval: {request_id}")
        logger.info(f"Message: {approval_message}")

        # Phase 5: Integrate Telegram notification here
        # telegram_client.send_message(user_id, approval_message)

        return request_id

    def _classify_risk(self, action_type: str) -> ActionRisk:
        """
        Classify risk level of an action.

        Args:
            action_type: Type of action

        Returns:
            Risk classification
        """
        # Risk classification rules
        critical_actions = {"charge_card", "delete_data", "fire_employee"}
        high_actions = {
            "send_email_bulk", "publish_post", "make_api_call",
            "update_customer_data"
        }
        medium_actions = {"create_draft", "schedule_post", "generate_report"}

        if action_type in critical_actions:
            return ActionRisk.CRITICAL
        elif action_type in high_actions:
            return ActionRisk.HIGH
        elif action_type in medium_actions:
            return ActionRisk.MEDIUM
        else:
            return ActionRisk.LOW

    def _calculate_confidence(self, action_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on action data.

        Args:
            action_data: Action details

        Returns:
            Confidence score (0-100)
        """
        # Phase 1: Simple heuristic scoring
        # Phase 5+: LLM-based confidence scoring

        score = 50.0  # Base score

        # Bonus for good data quality
        if action_data.get("is_validated"):
            score += 15
        if action_data.get("has_template"):
            score += 10
        if action_data.get("is_tested"):
            score += 15

        # Penalty for missing data
        if action_data.get("missing_fields"):
            score -= 20

        # Clamp to 0-100
        return max(0, min(100, score))

    def _format_approval_message(
        self,
        action_type: str,
        action_data: Dict[str, Any],
        confidence_score: float
    ) -> str:
        """
        Format approval request message.

        Args:
            action_type: Type of action
            action_data: Action details
            confidence_score: Confidence score

        Returns:
            Formatted message
        """
        message = f"""
⚠️  Action Requires Approval

Action: {action_type}
Confidence: {confidence_score:.1f}%

Details:
{self._format_action_details(action_data)}

[✓ Approve] [✗ Reject]
"""
        return message.strip()

    def _format_action_details(self, action_data: Dict[str, Any]) -> str:
        """Format action data for display."""
        details = []
        for key, value in action_data.items():
            if key.startswith("_"):
                continue
            details.append(f"  {key}: {value}")
        return "\n".join(details) if details else "  (none)"


# TODO: Phase 5 - Integrate LLM-based confidence scoring
# TODO: Phase 5 - Integrate Telegram approval flow
# TODO: Phase 5 - Add approval history and logging
