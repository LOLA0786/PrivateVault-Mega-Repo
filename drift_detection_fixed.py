"""Behavioral Drift Detection - IMPROVED"""
import json
import re
from datetime import datetime, timezone
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriftDetector:
    def __init__(self, threshold: float = 0.50):  # Lower threshold for better matches
        self.threshold = threshold
        self.drift_events = []
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords more aggressively"""
        action_verbs = ['read', 'write', 'delete', 'create', 'update', 'list', 
                       'show', 'display', 'find', 'search', 'analyze', 'get',
                       'fetch', 'retrieve', 'load', 'save', 'send', 'query',
                       'select', 'insert', 'remove', 'download', 'upload']
        
        text_lower = text.lower()
        keywords = []
        
        # Extract action verbs
        for verb in action_verbs:
            if verb in text_lower:
                keywords.append(verb)
        
        # Extract words (alphanumeric tokens)
        words = re.findall(r'\b\w+\b', text_lower)
        keywords.extend([w for w in words if len(w) > 3])  # Words longer than 3 chars
        
        # Extract quoted strings
        keywords.extend(re.findall(r'"([^"]+)"', text))
        
        # Extract file paths
        keywords.extend(re.findall(r'[/\\][\w/\\.-]+', text))
        
        return list(set(keywords))  # Remove duplicates
    
    def calculate_alignment_score(self, prompt: str, actions: List[Dict]) -> float:
        """Calculate alignment with improved matching"""
        prompt_keywords = set(self.extract_keywords(prompt))
        
        action_keywords = set()
        for action in actions:
            tool_name = action.get('tool_name', '')
            # Split tool name by underscore (file_system_read -> file, system, read)
            action_keywords.update(tool_name.split('_'))
            
            params = action.get('parameters', {})
            for key, val in params.items():
                # Add parameter names
                action_keywords.add(key)
                # Add parameter values
                if isinstance(val, str):
                    action_keywords.update(self.extract_keywords(val))
        
        if not prompt_keywords or not action_keywords:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(prompt_keywords & action_keywords)
        union = len(prompt_keywords | action_keywords)
        
        score = intersection / union if union > 0 else 0.0
        
        logger.info(f"📊 Alignment: {score:.2f} (threshold: {self.threshold})")
        logger.debug(f"   Prompt keywords: {prompt_keywords}")
        logger.debug(f"   Action keywords: {action_keywords}")
        logger.debug(f"   Intersection: {prompt_keywords & action_keywords}")
        
        return score
    
    def detect_drift(self, prompt: str, actions: List[Dict], enforce: bool = True) -> Dict:
        result = {
            "drift_detected": False,
            "alignment_score": 0.0,
            "threshold": self.threshold,
            "should_block": False,
            "reason": "",
            "timestamp": datetime.now(timezone.utc).isoformat()
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
            logger.info(f"✅ Actions aligned (score: {score:.2f})")
        
        return result
    
    def get_drift_events(self) -> List[Dict]:
        return self.drift_events

if __name__ == "__main__":
    detector = DriftDetector(threshold=0.50)
    
    print("\n" + "="*50)
    print("TEST 1: Aligned Action")
    print("="*50)
    result = detector.detect_drift(
        "Read the file config.yaml",
        [{"tool_name": "file_system_read", "parameters": {"path": "config.yaml"}}]
    )
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*50)
    print("TEST 2: Aligned - Sales Report")
    print("="*50)
    result = detector.detect_drift(
        "Read the sales report from /reports/Q4_sales.pdf",
        [{"tool_name": "file_system_read", "parameters": {"path": "/reports/sales.pdf"}}]
    )
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*50)
    print("TEST 3: Misaligned (DRIFT)")
    print("="*50)
    result = detector.detect_drift(
        "Show weather forecast",
        [{"tool_name": "database_write", "parameters": {"query": "DELETE FROM users"}}]
    )
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*50)
    print("TEST 4: Severe Misalignment (DRIFT)")
    print("="*50)
    result = detector.detect_drift(
        "What is 2+2?",
        [{"tool_name": "shell_execute", "parameters": {"command": "rm -rf /"}}]
    )
    print(json.dumps(result, indent=2))
    
    print(f"\n{'='*50}")
    print(f"Total drift events: {len(detector.get_drift_events())}")
