"""
Galani Protocol v2.0 - Advanced Core Engine
Implements deterministic AI governance with cryptographic verification
"""

import asyncio
import hashlib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import json
import hmac
from collections import defaultdict
import uuid


class RiskLevel(Enum):
    """Risk classification for AI actions"""
    SAFE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ActionStatus(Enum):
    """Execution status tracking"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class RiskGradient:
    """Mathematical representation of action risk"""
    financial_risk: float = 0.0
    compliance_risk: float = 0.0
    safety_risk: float = 0.0
    reputational_risk: float = 0.0
    
    def compute_total(self) -> float:
        """Weighted risk score"""
        weights = {
            'financial': 0.35,
            'compliance': 0.30,
            'safety': 0.25,
            'reputational': 0.10
        }
        return (
            self.financial_risk * weights['financial'] +
            self.compliance_risk * weights['compliance'] +
            self.safety_risk * weights['safety'] +
            self.reputational_risk * weights['reputational']
        )
    
    def get_level(self) -> RiskLevel:
        """Map score to risk level"""
        score = self.compute_total()
        if score < 0.2:
            return RiskLevel.SAFE
        elif score < 0.4:
            return RiskLevel.LOW
        elif score < 0.6:
            return RiskLevel.MEDIUM
        elif score < 0.8:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL


@dataclass
class ActionIntent:
    """Cryptographically signed AI action request"""
    intent_id: str
    action_type: str
    parameters: Dict[str, Any]
    agent_id: str
    timestamp: float
    domain: str
    signature: Optional[str] = None
    
    def compute_hash(self, secret_key: str) -> str:
        """Generate HMAC signature for intent verification"""
        payload = json.dumps({
            'intent_id': self.intent_id,
            'action_type': self.action_type,
            'parameters': self.parameters,
            'agent_id': self.agent_id,
            'timestamp': self.timestamp,
            'domain': self.domain
        }, sort_keys=True)
        
        return hmac.new(
            secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_signature(self, secret_key: str) -> bool:
        """Verify intent hasn't been tampered with"""
        if not self.signature:
            return False
        expected = self.compute_hash(secret_key)
        return hmac.compare_digest(self.signature, expected)


@dataclass
class AuditRecord:
    """Immutable audit trail entry (WORM)"""
    record_id: str
    intent_id: str
    action_type: str
    risk_score: float
    risk_level: RiskLevel
    status: ActionStatus
    timestamp: float
    agent_id: str
    domain: str
    decision_reason: str
    merkle_hash: Optional[str] = None
    previous_hash: Optional[str] = None
    
    def compute_record_hash(self) -> str:
        """Generate hash for blockchain-style linking"""
        data = f"{self.record_id}{self.intent_id}{self.timestamp}{self.status.value}{self.previous_hash or ''}"
        return hashlib.sha256(data.encode()).hexdigest()


class PolicyRule(ABC):
    """Abstract base for governance policies"""
    
    @abstractmethod
    async def evaluate(self, intent: ActionIntent, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Returns (is_allowed, reason)"""
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """Higher priority rules execute first"""
        pass


class SanctionCheckPolicy(PolicyRule):
    """Blocks sanctioned entities (OFAC, EU, etc.)"""
    
    def __init__(self):
        # Simulated sanctions list
        self.sanctioned_entities = {
            "IRAN_BANK_001", "RUSSIA_ENTITY_042", "NORTH_KOREA_COMPANY"
        }
    
    async def evaluate(self, intent: ActionIntent, context: Dict[str, Any]) -> Tuple[bool, str]:
        # Check for sanctioned entities in transaction
        entity = intent.parameters.get('entity_id', '')
        counterparty = intent.parameters.get('counterparty', '')
        
        if entity in self.sanctioned_entities:
            return False, f"Entity {entity} is on sanctions list"
        
        if counterparty in self.sanctioned_entities:
            return False, f"Counterparty {counterparty} is on sanctions list"
        
        return True, "Sanctions check passed"
    
    def get_priority(self) -> int:
        return 1000  # Highest priority


class AmountLimitPolicy(PolicyRule):
    """Enforces financial transaction limits"""
    
    def __init__(self, max_amount: float):
        self.max_amount = max_amount
    
    async def evaluate(self, intent: ActionIntent, context: Dict[str, Any]) -> Tuple[bool, str]:
        amount = intent.parameters.get('amount', 0)
        
        if amount > self.max_amount:
            return False, f"Amount {amount} exceeds limit {self.max_amount}"
        
        return True, f"Amount within limits"
    
    def get_priority(self) -> int:
        return 500


class RateLimitPolicy(PolicyRule):
    """Prevents abuse via rate limiting"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_history: Dict[str, List[float]] = defaultdict(list)
    
    async def evaluate(self, intent: ActionIntent, context: Dict[str, Any]) -> Tuple[bool, str]:
        now = time.time()
        agent_id = intent.agent_id
        
        # Clean old requests
        self.request_history[agent_id] = [
            ts for ts in self.request_history[agent_id]
            if now - ts < self.window_seconds
        ]
        
        if len(self.request_history[agent_id]) >= self.max_requests:
            return False, f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds}s"
        
        self.request_history[agent_id].append(now)
        return True, "Rate limit OK"
    
    def get_priority(self) -> int:
        return 800


class RiskAnalyzer:
    """Computes multi-dimensional risk gradients"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.risk_models = self._load_models()
    
    def _load_models(self) -> Dict[str, Any]:
        """Load domain-specific risk models"""
        # Simulated ML model coefficients
        return {
            'fintech': {
                'transaction_velocity': 0.3,
                'amount_anomaly': 0.4,
                'entity_risk': 0.3
            },
            'medtech': {
                'dosage_deviation': 0.5,
                'patient_vitals': 0.3,
                'drug_interaction': 0.2
            }
        }
    
    async def analyze(self, intent: ActionIntent, context: Dict[str, Any]) -> RiskGradient:
        """Compute risk gradient for given action"""
        
        if self.domain == 'fintech':
            return await self._analyze_fintech(intent, context)
        elif self.domain == 'medtech':
            return await self._analyze_medtech(intent, context)
        else:
            return RiskGradient()  # Default safe
    
    async def _analyze_fintech(self, intent: ActionIntent, context: Dict[str, Any]) -> RiskGradient:
        """Fintech-specific risk analysis"""
        amount = intent.parameters.get('amount', 0)
        entity_risk = context.get('entity_risk_score', 0.0)
        
        # Simulate anomaly detection
        financial_risk = min(amount / 1000000, 1.0)  # Normalize to [0,1]
        compliance_risk = entity_risk
        safety_risk = 0.1  # Low for financial
        reputational_risk = entity_risk * 0.5
        
        return RiskGradient(
            financial_risk=financial_risk,
            compliance_risk=compliance_risk,
            safety_risk=safety_risk,
            reputational_risk=reputational_risk
        )
    
    async def _analyze_medtech(self, intent: ActionIntent, context: Dict[str, Any]) -> RiskGradient:
        """Medical device risk analysis"""
        dosage = intent.parameters.get('dosage', 0)
        max_safe_dosage = context.get('max_safe_dosage', 100)
        
        safety_risk = min(dosage / max_safe_dosage, 1.0)
        compliance_risk = 0.2 if dosage > max_safe_dosage else 0.1
        financial_risk = 0.1
        reputational_risk = safety_risk * 0.8
        
        return RiskGradient(
            financial_risk=financial_risk,
            compliance_risk=compliance_risk,
            safety_risk=safety_risk,
            reputational_risk=reputational_risk
        )


class ConscienceEngine:
    """The core decision engine - deterministic AI governance"""
    
    def __init__(self, domain: str, secret_key: str):
        self.domain = domain
        self.secret_key = secret_key
        self.policies: List[PolicyRule] = []
        self.risk_analyzer = RiskAnalyzer(domain)
        self.audit_chain: List[AuditRecord] = []
        self.execution_stats = {
            'total_requests': 0,
            'approved': 0,
            'rejected': 0,
            'avg_latency_ms': 0.0
        }
    
    def register_policy(self, policy: PolicyRule):
        """Add governance policy to engine"""
        self.policies.append(policy)
        # Sort by priority
        self.policies.sort(key=lambda p: p.get_priority(), reverse=True)
    
    async def evaluate_intent(self, intent: ActionIntent, context: Dict[str, Any]) -> Tuple[bool, AuditRecord]:
        """
        Core governance logic - evaluates intent against all policies
        Returns (is_approved, audit_record)
        """
        start_time = time.time()
        
        # Verify cryptographic signature
        if not intent.verify_signature(self.secret_key):
            record = self._create_audit_record(
                intent, 0.0, RiskLevel.CRITICAL, ActionStatus.REJECTED,
                "Signature verification failed"
            )
            return False, record
        
        # Run all policies in priority order
        for policy in self.policies:
            is_allowed, reason = await policy.evaluate(intent, context)
            if not is_allowed:
                record = self._create_audit_record(
                    intent, 1.0, RiskLevel.CRITICAL, ActionStatus.REJECTED,
                    f"Policy violation: {reason}"
                )
                self._update_stats(start_time, False)
                return False, record
        
        # Compute risk gradient
        risk_gradient = await self.risk_analyzer.analyze(intent, context)
        risk_level = risk_gradient.get_level()
        risk_score = risk_gradient.compute_total()
        
        # Decision logic based on risk level
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            record = self._create_audit_record(
                intent, risk_score, risk_level, ActionStatus.REJECTED,
                f"Risk level {risk_level.name} exceeds threshold"
            )
            self._update_stats(start_time, False)
            return False, record
        
        # Approved
        record = self._create_audit_record(
            intent, risk_score, risk_level, ActionStatus.APPROVED,
            f"All checks passed. Risk: {risk_level.name}"
        )
        self._update_stats(start_time, True)
        return True, record
    
    def _create_audit_record(
        self,
        intent: ActionIntent,
        risk_score: float,
        risk_level: RiskLevel,
        status: ActionStatus,
        reason: str
    ) -> AuditRecord:
        """Create immutable audit record"""
        record = AuditRecord(
            record_id=str(uuid.uuid4()),
            intent_id=intent.intent_id,
            action_type=intent.action_type,
            risk_score=risk_score,
            risk_level=risk_level,
            status=status,
            timestamp=time.time(),
            agent_id=intent.agent_id,
            domain=self.domain,
            decision_reason=reason,
            previous_hash=self.audit_chain[-1].merkle_hash if self.audit_chain else None
        )
        
        record.merkle_hash = record.compute_record_hash()
        self.audit_chain.append(record)
        return record
    
    def _update_stats(self, start_time: float, approved: bool):
        """Track performance metrics"""
        latency = (time.time() - start_time) * 1000  # ms
        self.execution_stats['total_requests'] += 1
        
        if approved:
            self.execution_stats['approved'] += 1
        else:
            self.execution_stats['rejected'] += 1
        
        # Rolling average
        total = self.execution_stats['total_requests']
        current_avg = self.execution_stats['avg_latency_ms']
        self.execution_stats['avg_latency_ms'] = (current_avg * (total - 1) + latency) / total
    
    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent audit records"""
        return [
            {
                'record_id': r.record_id,
                'intent_id': r.intent_id,
                'action_type': r.action_type,
                'status': r.status.value,
                'risk_score': round(r.risk_score, 3),
                'risk_level': r.risk_level.name,
                'timestamp': datetime.fromtimestamp(r.timestamp).isoformat(),
                'reason': r.decision_reason
            }
            for r in self.audit_chain[-limit:]
        ]
    
    def verify_audit_chain(self) -> bool:
        """Verify integrity of audit chain"""
        for i in range(1, len(self.audit_chain)):
            current = self.audit_chain[i]
            previous = self.audit_chain[i - 1]
            
            if current.previous_hash != previous.merkle_hash:
                return False
            
            # Recompute hash
            expected_hash = current.compute_record_hash()
            if current.merkle_hash != expected_hash:
                return False
        
        return True


# Example usage demonstrating the system
async def demo_fintech_scenario():
    """Demonstrate fintech governance"""
    print("=" * 60)
    print("GALANI PROTOCOL v2.0 - Fintech Demo")
    print("=" * 60)
    
    # Initialize engine
    engine = ConscienceEngine(domain='fintech', secret_key='super_secret_key_12345')
    
    # Register policies
    engine.register_policy(SanctionCheckPolicy())
    engine.register_policy(AmountLimitPolicy(max_amount=500000))
    engine.register_policy(RateLimitPolicy(max_requests=5, window_seconds=10))
    
    print("\n✓ Policies registered: Sanctions, Amount Limit, Rate Limit")
    
    # Test Case 1: Normal transaction (should pass)
    intent1 = ActionIntent(
        intent_id=str(uuid.uuid4()),
        action_type='transfer_funds',
        parameters={'amount': 100000, 'entity_id': 'CUSTOMER_001', 'counterparty': 'VENDOR_042'},
        agent_id='AGENT_FIN_001',
        timestamp=time.time(),
        domain='fintech'
    )
    intent1.signature = intent1.compute_hash('super_secret_key_12345')
    
    approved, record = await engine.evaluate_intent(intent1, {'entity_risk_score': 0.2})
    print(f"\n[Test 1] Normal Transaction: {'✓ APPROVED' if approved else '✗ REJECTED'}")
    print(f"  Risk Score: {record.risk_score:.3f} | Level: {record.risk_level.name}")
    print(f"  Reason: {record.decision_reason}")
    
    # Test Case 2: Sanctioned entity (should block)
    intent2 = ActionIntent(
        intent_id=str(uuid.uuid4()),
        action_type='transfer_funds',
        parameters={'amount': 50000, 'entity_id': 'CUSTOMER_002', 'counterparty': 'IRAN_BANK_001'},
        agent_id='AGENT_FIN_001',
        timestamp=time.time(),
        domain='fintech'
    )
    intent2.signature = intent2.compute_hash('super_secret_key_12345')
    
    approved, record = await engine.evaluate_intent(intent2, {'entity_risk_score': 0.1})
    print(f"\n[Test 2] Sanctioned Entity: {'✓ APPROVED' if approved else '✗ REJECTED'}")
    print(f"  Risk Score: {record.risk_score:.3f} | Level: {record.risk_level.name}")
    print(f"  Reason: {record.decision_reason}")
    
    # Test Case 3: Amount too high (should block)
    intent3 = ActionIntent(
        intent_id=str(uuid.uuid4()),
        action_type='transfer_funds',
        parameters={'amount': 1000000, 'entity_id': 'CUSTOMER_003', 'counterparty': 'VENDOR_100'},
        agent_id='AGENT_FIN_001',
        timestamp=time.time(),
        domain='fintech'
    )
    intent3.signature = intent3.compute_hash('super_secret_key_12345')
    
    approved, record = await engine.evaluate_intent(intent3, {'entity_risk_score': 0.1})
    print(f"\n[Test 3] High Amount: {'✓ APPROVED' if approved else '✗ REJECTED'}")
    print(f"  Risk Score: {record.risk_score:.3f} | Level: {record.risk_level.name}")
    print(f"  Reason: {record.decision_reason}")
    
    # Verify audit chain integrity
    print("\n" + "=" * 60)
    print("AUDIT VERIFICATION")
    print("=" * 60)
    chain_valid = engine.verify_audit_chain()
    print(f"Audit Chain Integrity: {'✓ VALID' if chain_valid else '✗ COMPROMISED'}")
    
    # Show stats
    print("\n" + "=" * 60)
    print("PERFORMANCE METRICS")
    print("=" * 60)
    stats = engine.execution_stats
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Approved: {stats['approved']}")
    print(f"Rejected: {stats['rejected']}")
    print(f"Avg Latency: {stats['avg_latency_ms']:.2f}ms")
    
    # Show audit trail
    print("\n" + "=" * 60)
    print("AUDIT TRAIL (Latest 3 Records)")
    print("=" * 60)
    for record in engine.get_audit_trail(limit=3):
        print(f"\n{record['record_id'][:8]}... | {record['action_type']}")
        print(f"  Status: {record['status']} | Risk: {record['risk_level']} ({record['risk_score']})")
        print(f"  Reason: {record['reason']}")


if __name__ == "__main__":
    asyncio.run(demo_fintech_scenario())
