import json
import logging
import uuid
from datetime import datetime

# Assuming existing modules are in the same dir
import ai_firewall_core
import tool_authorization
import drift_detection_fixed
import decision_ledger

logging.basicConfig(level=logging.INFO)


class WorkflowGraph:
    def __init__(self):
        self.nodes = {
            "planner": {"agent": "Planner", "next": "executor"},
            "executor": {"agent": "Executor", "next": "auditor"},
            "auditor": {"agent": "Auditor", "next": None},
        }


class AgentContext:
    def __init__(self, role, permissions):
        self.role = role
        self.permissions = permissions


def execute_workflow(graph, initial_prompt, workflow_id=None):
    if not workflow_id:
        workflow_id = str(uuid.uuid4())

    current_node = "planner"
    context = {
        "prompt": initial_prompt,
        "plan": None,
        "action": None,
        "verification": None,
    }
    ledger_events = []

    while current_node:
        agent = graph.nodes[current_node]["agent"]
        logging.info(f"Executing node: {current_node} with agent: {agent}")

        if current_node == "planner":
            # Simulate planning
            context["plan"] = "Planned action: file_system_read"
            metadata = {
                "workflow_id": workflow_id,
                "agent_id": agent,
                "node_id": current_node,
            }
            decision_ledger.log_event("planner_output", metadata)
            ledger_events.append(metadata)

        elif current_node == "executor":
            # Filter input and authorize tool
            filter_result = ai_firewall_core.filter_input(context["prompt"])
            if not filter_result["allowed"]:
                logging.warning(
                    f"Blocked at executor: {filter_result['threat_reason']}"
                )
                return {
                    "status": "blocked",
                    "reason": filter_result["threat_reason"],
                    "ledger_events": ledger_events,
                }

            auth_result = tool_authorization.authorize_action(
                "alice", context["plan"]
            )  # Assuming from existing
            if not auth_result["authorized"]:
                logging.warning(f"Unauthorized at executor: {auth_result['error']}")
                return {
                    "status": "blocked",
                    "reason": auth_result["error"],
                    "ledger_events": ledger_events,
                }

            context["action"] = "Executed: " + context["plan"]
            metadata = {
                "workflow_id": workflow_id,
                "agent_id": agent,
                "node_id": current_node,
            }
            decision_ledger.log_event("executor_output", metadata)
            ledger_events.append(metadata)

        elif current_node == "auditor":
            # Detect drift
            drift_result = drift_detection_fixed.detect_drift(
                context["plan"], context["action"], threshold=0.2
            )
            if drift_result["drift_detected"]:
                logging.critical("Drift detected at auditor")
                return {
                    "status": "blocked",
                    "reason": "Drift detected",
                    "ledger_events": ledger_events,
                }

            context["verification"] = "Verified"
            metadata = {
                "workflow_id": workflow_id,
                "agent_id": agent,
                "node_id": current_node,
            }
            decision_ledger.log_event("auditor_output", metadata)
            ledger_events.append(metadata)

        current_node = graph.nodes[current_node]["next"]

    return {"status": "success", "result": context, "ledger_events": ledger_events}


if __name__ == "__main__":
    graph = WorkflowGraph()
    result = execute_workflow(graph, "Clean prompt: Read file")
    print(json.dumps(result, indent=2))
