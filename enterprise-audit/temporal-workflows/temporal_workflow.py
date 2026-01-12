import asyncio
from datetime import timedelta
from temporalio import workflow

@workflow.definition
class AgentGovernanceWorkflow:
    @workflow.run
    async def run(self, agent_id: str) -> str:
        # Step 1: Suspend the Agent in the Data Plane (Envoy/OPA)
        print(f"Workflow Started: Suspending Agent {agent_id}")
        status = "SUSPENDED"
        
        # Step 2: Human-in-the-loop (Wait for external signal from Admin Console)
        print(f"Agent {agent_id} is now {status}. Waiting for Admin Approval...")
        
        # This 'wait_condition' pauses the workflow until a human clicks 'Approve'
        await workflow.wait_condition(lambda: self.approved)
        
        # Step 3: Resolution & Re-activation
        print(f"Approval Received for {agent_id}. Promoting to ACTIVE.")
        return f"Agent {agent_id} has been restored to service."

    def __init__(self):
        self.approved = False

    @workflow.signal
    def approve_action(self):
        self.approved = True
