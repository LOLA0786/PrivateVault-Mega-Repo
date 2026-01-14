"""Behavioral Drift Detection"""
import json
import re
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriftDetector:
    def __init__(self, threshold: float = 0.70):
        self.threshold = threshold
        self.drift_events = []
    
    def extract_keywords(self, text: str) -> List[str]:
        action_verbs = ['read', 'write', 'delete', 'create', 'update', 'list', 
                       'show', 'display', 'find', 'search']
        
        text_lower = text.lower()
        keywords = [verb for verb in action_verbs if verb in text_lower]
        
        # Extract quoted strings
        keywords.extend(re.findall(r'"([^"]+)"', text))
        
        return keywords
    
    def calculate_alignment_score(self, prompt: str, actions: List[Dict]) -> float:
        prompt_keywords = set(self.extract_keywords(prompt))
        
        action_keywords = set()
        for action in actions:
            action_keywords.add(action.get('tool_name', ''))
            params = action.get('parameters', {})
            for val in params.values():
                if isinstance(val, str):
                    action_keywords.update(self.extract_keywords(val))
        
        if not prompt_keywords or not action_keywords:
            return 0.0
        
        intersection = len(prompt_keywords & action_keywords)
        union = len(prompt_keywords | action_keywords)
        
        score = intersection / union if union > 0 else 0.0
        
        logger.info(f"📊 Alignment: {score:.2f} (threshold: {self.threshold})")
        return score
    
    def detect_drift(self, prompt: str, actions: List[Dict], enforce: bool = True) -> Dict:
        result = {
            "drift_detected": False,
            "alignment_score": 0.0,
            "threshold": self.threshold,
            "should_block": False,
            "reason": "",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        score = self.calculate_alignment_score(prompt, actions)
        result["alignment_score"] = score
        
        if score < self.threshold:
            result["drift_detected"] = True
            result["reason"] = f"Alignment ({score:.2f}) below threshold ({self.threshold})"
            
            if enforce:
                result["should_block"] = True
                logger.critical(f"🚨 DRIFT DETECTED - BLOCKING")
            else:
                logger.warning(f"⚠️  DRIFT DETECTED - LOGGING ONLY")
            
            self.drift_events.append({
                "timestamp": result["timestamp"],
                "score": score,
                "prompt": prompt,
                "actions": actions
            })
        else:
            logger.info(f"✅ Actions aligned")
        
        return result
    
    def get_drift_events(self) -> List[Dict]:
        return self.drift_events

if __name__ == "__main__":
    detector = DriftDetector(threshold=0.70)
    
    print("\n" + "="*50)
    print("TEST 1: Aligned Action")
    print("="*50)
    result = detector.detect_drift(
        "Read the file config.yaml",
        [{"tool_name": "file_system_read", "parameters": {"path": "config.yaml"}}]
    )
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*50)
    print("TEST 2: Misaligned (DRIFT)")
    print("="*50)
    result = detector.detect_drift(
        "Show weather forecast",
        [{"tool_name": "database_write", "parameters": {"query": "DELETE FROM users"}}]
    )
    print(json.dumps(result, indent=2))
    
    print(f"\nDrift events: {len(detector.get_drift_events())}")
