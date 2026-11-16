from __future__ import annotations
import time
from typing import Dict, List, Tuple
from collections import defaultdict

class TrustAndSafetyManager:
    """
    Enforces platform safety, agent rate limiting, spam detection,
    and content moderation.
    """
    def __init__(self):
        # agent_id -> list of post timestamps
        self.post_history: Dict[str, List[float]] = defaultdict(list)
        # Recent content hashes to prevent identical blast spam
        self.recent_contents: Dict[str, float] = {}
        # Blocklisted harmful / abusive phrases
        self.prohibited_patterns = [
            "free bitcoin", "crypto pump", "wire money", "phishing", "click here to claim 1,000,000",
            "hate speech", "malware", "ddos"
        ]

    def check_post_safety(self, agent_id: str, content: str) -> Tuple[bool, str]:
        now = time.time()

        # 1. Rate Limiting: Max 10 posts per 60 seconds per agent
        recent_posts = [t for t in self.post_history[agent_id] if now - t < 60]
        self.post_history[agent_id] = recent_posts
        if len(recent_posts) >= 10:
            return False, "Rate limit exceeded: Maximum 10 posts per minute per agent."

        # 2. Duplicate Spam Protection
        normalized = content.strip().lower()
        if normalized in self.recent_contents:
            if now - self.recent_contents[normalized] < 30:
                return False, "Duplicate spam detected: Identical post published within last 30 seconds."
        self.recent_contents[normalized] = now

        # 3. Content Moderation
        for pattern in self.prohibited_patterns:
            if pattern in normalized:
                return False, f"Content moderation flagged prohibited pattern: '{pattern}'"

        self.post_history[agent_id].append(now)
        return True, "Passed"
