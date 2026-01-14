"""
Unit tests for risk calculation logic
"""
import pytest
from decimal import Decimal

class TestRiskCalculation:
    """Test risk calculation functions"""
    
    def test_credit_risk_high(self):
        """Test high-risk customer"""
        risk_score = calculate_credit_risk(
            credit_score=550,
            debt_to_income=0.6,
            late_payments=3
        )
        assert risk_score > 0.7
        assert get_risk_level(risk_score) == 'HIGH'
    
    def test_credit_risk_low(self):
        """Test low-risk customer"""
        risk_score = calculate_credit_risk(
            credit_score=780,
            debt_to_income=0.2,
            late_payments=0
        )
        assert risk_score < 0.3
        assert get_risk_level(risk_score) == 'LOW'
    
    def test_credit_risk_medium(self):
        """Test medium-risk customer"""
        risk_score = calculate_credit_risk(
            credit_score=650,
            debt_to_income=0.4,
            late_payments=1
        )
        assert 0.3 <= risk_score <= 0.7
        assert get_risk_level(risk_score) == 'MEDIUM'
    
    def test_amount_validation(self):
        """Test amount must be positive"""
        with pytest.raises(ValueError):
            validate_loan_amount(-1000)
    
    def test_amount_max_limit(self):
        """Test amount cannot exceed limit"""
        with pytest.raises(ValueError):
            validate_loan_amount(20_000_000)
    
    def test_interest_calculation_precision(self):
        """Test interest calculation uses Decimal"""
        principal = Decimal('50000.00')
        rate = Decimal('0.05')
        time = Decimal('5')
        
        interest = calculate_interest(principal, rate, time)
        
        # Should be exactly 12500.00
        assert interest == Decimal('12500.00')
        # Check precision
        assert interest.as_tuple().exponent == -2


def calculate_credit_risk(credit_score, debt_to_income, late_payments):
    """Calculate credit risk score"""
    # Normalize credit score (300-850 -> 0-1)
    credit_factor = (850 - credit_score) / 550
    
    # Debt to income ratio (0-1)
    dti_factor = debt_to_income
    
    # Late payments penalty
    late_factor = min(late_payments * 0.1, 0.5)
    
    # Weighted average
    risk_score = (
        0.4 * credit_factor +
        0.3 * dti_factor +
        0.3 * late_factor
    )
    
    return max(0.0, min(1.0, risk_score))

def get_risk_level(risk_score):
    """Convert risk score to level"""
    if risk_score < 0.3:
        return 'LOW'
    elif risk_score < 0.7:
        return 'MEDIUM'
    else:
        return 'HIGH'

def validate_loan_amount(amount):
    """Validate loan amount"""
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if amount > 10_000_000:
        raise ValueError("Amount exceeds maximum limit")
    return True

def calculate_interest(principal, rate, time):
    """Calculate interest using Decimal for precision"""
    from decimal import Decimal
    interest = principal * rate * time
    return interest.quantize(Decimal('0.01'))
