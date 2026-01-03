def explain(decision, risk_score, factors):
    return {
        "decision": decision,
        "risk_score": round(risk_score, 3),
        "factors": sorted(factors.items(), key=lambda x: abs(x[1]), reverse=True)
    }
