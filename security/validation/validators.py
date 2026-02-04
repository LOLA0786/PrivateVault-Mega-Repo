"""
Input validation to prevent injection attacks
"""

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AgentRequest(BaseModel):
    """Validated agent request"""

    agent_id: str = Field(..., min_length=8, max_length=64)
    action: str = Field(..., max_length=100)
    parameters: dict[str, Any]

    @field_validator("agent_id")
    def validate_agent_id(cls, v):
        """Only allow alphanumeric, underscore, hyphen"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Invalid agent_id: only alphanumeric, _, - allowed")
        return v

    @field_validator("action")
    def validate_action(cls, v):
        """Whitelist allowed actions"""
        allowed_actions = ["credit_check", "fraud_detect", "kyc_verify", "risk_assess"]
        if v not in allowed_actions:
            raise ValueError(f"Invalid action: must be one of {allowed_actions}")
        return v


class CreditCheckRequest(BaseModel):
    """Validated credit check request"""

    applicant_id: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0, lt=10_000_000)
    term_months: int = Field(..., ge=1, le=360)

    @field_validator("amount")
    def validate_amount(cls, v):
        """Ensure amount is reasonable"""
        if v <= 0:
            raise ValueError("Amount must be positive")
        if v > 10_000_000:
            raise ValueError("Amount exceeds maximum loan limit")
        return round(v, 2)  # Round to 2 decimal places


class FraudDetectRequest(BaseModel):
    """Validated fraud detection request"""

    transaction_id: str
    amount: float = Field(gt=0)
    merchant: str = Field(max_length=200)
    card_last4: str = Field(pattern=r"^\d{4}$")

    @field_validator("card_last4")
    def validate_card(cls, v):
        """Ensure card is 4 digits"""
        if not v.isdigit() or len(v) != 4:
            raise ValueError("card_last4 must be exactly 4 digits")
        return v


# SQL Injection Prevention
class SafeQueryBuilder:
    """Build SQL queries safely with parameterization"""

    @staticmethod
    def build_query(table: str, conditions: dict[str, Any]) -> tuple:
        """
        Build parameterized SQL query

        Returns:
            (query_string, parameters_dict)

        Example:
            query, params = SafeQueryBuilder.build_query(
                'agents',
                {'agent_id': 'abc123', 'status': 'active'}
            )
            # Returns:
            # ("SELECT * FROM agents WHERE agent_id = %(agent_id)s AND status = %(status)s",
            #  {'agent_id': 'abc123', 'status': 'active'})
        """
        # Whitelist table names (prevent SQL injection via table name)
        allowed_tables = ["agents", "decisions", "audit_log", "users"]
        if table not in allowed_tables:
            raise ValueError(f"Invalid table name: {table}")

        # Build WHERE clause
        where_clauses = []
        for key in conditions.keys():
            # Sanitize column names
            if not re.match(r"^[a-zA-Z0-9_]+$", key):
                raise ValueError(f"Invalid column name: {key}")
            where_clauses.append(f"{key} = %({key})s")

        where_sql = " AND ".join(where_clauses)
        query = f"SELECT * FROM {table} WHERE {where_sql}"

        return query, conditions


# Prompt Injection Prevention
class PromptSanitizer:
    """Sanitize AI prompts to prevent injection attacks"""

    DANGEROUS_PATTERNS = [
        r"ignore previous instructions",
        r"ignore all previous",
        r"new instructions:",
        r"system:",
        r"system prompt",
        r"<\|endoftext\|>",
        r"<\|im_end\|>",
    ]

    @staticmethod
    def sanitize(prompt: str, max_length: int = 10000) -> str:
        """
        Sanitize AI prompt

        Args:
            prompt: User-provided prompt
            max_length: Maximum allowed length

        Returns:
            Sanitized prompt
        """
        # Remove dangerous patterns
        sanitized = prompt
        for pattern in PromptSanitizer.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

        # Enforce length limit
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        # Remove excessive whitespace
        sanitized = " ".join(sanitized.split())

        return sanitized.strip()
