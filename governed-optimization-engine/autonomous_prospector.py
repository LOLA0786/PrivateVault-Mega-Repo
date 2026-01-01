import os
import json
import google.generativeai as genai

# Setup Gemini - Replace with your API Key
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

class SalesAgent:
    def __init__(self, industry):
        self.industry = industry

    def research_and_pitch(self, company_name):
        """
        Lethal Logic: Don't sell features. Sell 'Time-Travel' (Prediction).
        """
        prompt = f"""
        You are a world-class CTO Sales Engineer for OAAS (Optimization-as-a-Service).
        Target Company: {company_name} in the {self.industry} industry.
        
        Task:
        1. Identify a specific 'lag' problem this company likely has (e.g., inventory overstock, trading slippage, server latency).
        2. Explain how our 'Neural Nesterov Engine' predicts their next state 5 steps ahead, saving them millions.
        3. Write a 3-sentence 'Lethal Pitch' to their CTO. No fluff. 
        
        Format: JSON with keys 'pain_point', 'acceleration_benefit', 'pitch'.
        """
        
        response = model.generate_content(prompt)
        # Clean the response to ensure it's valid JSON
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(raw_text)

# --- Execution ---
if __name__ == "__main__":
    # Example: Targeting a Series C Logistics company
    agent = SalesAgent(industry="Logistics")
    
    target_companies = ["Flexport", "Deliveroo", "Stord"]
    
    print(f"--- STARTING OUTREACH SCAN ---")
    for co in target_companies:
        insight = agent.research_and_pitch(co)
        print(f"\n[TARGET: {co}]")
        print(f"Detected Pain: {insight['pain_point']}")
        print(f"The Fix: {insight['acceleration_benefit']}")
        print(f"Pitch: {insight['pitch']}")
