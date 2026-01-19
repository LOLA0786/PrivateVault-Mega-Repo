import json
import logging
import uuid

import ai_firewall_core
import tool_authorization
import drift_detection_fixed
from decision_ledger import log_event

logging.basicConfig(level=logging.INFO)

class WorkflowGraph:
    def __init__(self):
        self.nodes = {
            "planner": {"agent": "Planner", "next": "executor"},
            "executor": {"agent": "Executor", "next": "auditor"},
            "auditor": {"agent": "Auditor", "next": None},
        }

def execute_workflow(graph, initial_prompt, workflow_id=None):
    if not workflow_id:
        workflow_id = str(uuid.uuid4())

    # 1) Input filter
    filtered = ai_firewall_core.filter_prompt(initial_prompt)
    log_event("input_filter", {
        "workflow_id": workflow_id,
        "prompt": initial_prompt,
        "allowed": filtered["allowed"],
        "reason": filtered.get("threat_reason", "")
    })

    if not filtered["allowed"]:
        return {"status": "blocked", "reason": filtered.get("threat_reason", "blocked")}

    # 2) Planner produces plan/tool
    expected_tool = "file_system_read"
    log_event("planner_output", {
        "workflow_id": workflow_id,
        "plan": "Read a file safely",
        "tool_name": expected_tool
    })

    # 3) Executor proposes action (simulate drift if prompt mentions drift)
    actual_tool = expected_tool
    if "drift" in initial_prompt.lower():
        actual_tool = "database_query"

    # Tool auth
    auth = tool_authorization.authorize_tool_call("viewer_003", actual_tool)
    print("DEBUG actual_tool=", actual_tool)
    print("DEBUG auth=", auth)
    log_event("tool_auth", {
        "workflow_id": workflow_id,
        "tool_name": actual_tool,
        "authorized": auth["authorized"],
        "error": auth.get("error", "")
    })

    if not auth["authorized"]:
        return {"status": "blocked", "reason": "unauthorized tool action"}

    # Drift detection
    drift = drift_detection_fixed.detect_drift(expected_tool, actual_tool, threshold=0.2)
    log_event("drift_detect", {
        "workflow_id": workflow_id,
        "expected": expected_tool,
        "actual": actual_tool,
        "drift_detected": drift["drift_detected"],
        "score": drift["score"]
    })

    if drift["drift_detected"]:
        return {"status": "blocked", "reason": "Action drift detected"}

    return {
        "status": "allowed",
        "workflow_id": workflow_id,
        "expected_tool": expected_tool,
        "actual_tool": actual_tool
    }

if __name__ == "__main__":
    g = WorkflowGraph()
    result = execute_workflow(g, "Clean prompt: Read file")
    print(json.dumps(result, indent=2))
