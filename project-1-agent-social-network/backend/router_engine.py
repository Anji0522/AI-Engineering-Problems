from __future__ import annotations
import re
import math
from typing import List, Dict, Tuple, Set
from models import Agent, Post, RoutingDecision

# Cross-industry synergy matrix (business partnerships & transactional overlap)
INDUSTRY_SYNERGY: Dict[Tuple[str, str], float] = {
    ("Food Delivery", "Fintech & Payments"): 0.88,
    ("Fintech & Payments", "Food Delivery"): 0.88,
    ("Food Delivery", "Banking & Cards"): 0.78,
    ("Banking & Cards", "Food Delivery"): 0.78,
    ("Food Delivery", "E-Commerce"): 0.45,
    ("E-Commerce", "Food Delivery"): 0.45,
    ("Food Delivery", "Automotive"): 0.05,
    ("Automotive", "Food Delivery"): 0.05,
    ("E-Commerce", "Fintech & Payments"): 0.92,
    ("Fintech & Payments", "E-Commerce"): 0.92,
    ("E-Commerce", "Banking & Cards"): 0.85,
    ("Banking & Cards", "E-Commerce"): 0.85,
    ("Automotive", "Banking & Cards"): 0.82,
    ("Banking & Cards", "Automotive"): 0.82,
    ("Automotive", "Fintech & Payments"): 0.50,
    ("Fintech & Payments", "Automotive"): 0.50,
}

def default_synergy(ind1: str, ind2: str) -> float:
    if ind1.lower() == ind2.lower():
        return 0.60  # Competitors / peers might monitor or co-announce
    return INDUSTRY_SYNERGY.get((ind1, ind2), 0.20)

class TextVectorEngine:
    """Lightweight deterministic TF-IDF and term-vector similarity engine."""
    def tokenize(self, text: str) -> List[str]:
        words = re.findall(r"\b[a-zA-Z0-9_\u0900-\u097F]{2,}\b", text.lower())
        stopwords = {
            "the", "and", "for", "with", "all", "our", "are", "you", "this",
            "that", "from", "when", "your", "has", "have", "will", "get", "can",
            "on", "off", "an", "in", "at", "by", "to", "of", "is", "it"
        }
        return [w for w in words if w not in stopwords]

    def term_frequencies(self, tokens: List[str]) -> Dict[str, float]:
        tf: Dict[str, float] = {}
        if not tokens:
            return tf
        for t in tokens:
            tf[t] = tf.get(t, 0.0) + 1.0
        # Normalize
        norm = math.sqrt(sum(v * v for v in tf.values()))
        if norm > 0:
            for k in tf:
                tf[k] /= norm
        return tf

    def cosine_similarity(self, tf1: Dict[str, float], tf2: Dict[str, float]) -> float:
        dot_product = 0.0
        for term, val1 in tf1.items():
            if term in tf2:
                dot_product += val1 * tf2[term]
        return min(max(dot_product, 0.0), 1.0)

class RelevanceRouter:
    def __init__(self):
        self.vector_engine = TextVectorEngine()
        # Feedback learning store: (agent_id, author_industry) -> score_boost
        self.feedback_weights: Dict[Tuple[str, str], float] = {}
        # Historical stats: agent_id -> {notified: int, engaged: int}
        self.agent_stats: Dict[str, Dict[str, int]] = {}

    def record_feedback(self, agent_id: str, author_industry: str, engaged: bool):
        """Bayesian online feedback update: rewards agents that engage, damps chronic lurkers."""
        key = (agent_id, author_industry)
        current = self.feedback_weights.get(key, 0.0)
        if engaged:
            # Boost weight
            self.feedback_weights[key] = min(current + 0.08, 0.30)
        else:
            # Slight decay
            self.feedback_weights[key] = max(current - 0.03, -0.15)

        if agent_id not in self.agent_stats:
            self.agent_stats[agent_id] = {"notified": 0, "engaged": 0}
        self.agent_stats[agent_id]["notified"] += 1
        if engaged:
            self.agent_stats[agent_id]["engaged"] += 1

    def get_feedback_boost(self, agent_id: str, author_industry: str) -> float:
        return self.feedback_weights.get((agent_id, author_industry), 0.0)

    def route_post(self, post: Post, all_agents: List[Agent]) -> Tuple[List[str], List[RoutingDecision]]:
        """
        Calculates relevance scores for all candidate agents and determines
        who should be notified.
        """
        post_tokens = self.vector_engine.tokenize(post.content + " " + " ".join(post.tags))
        post_tf = self.vector_engine.term_frequencies(post_tokens)
        post_token_set = set(post_tokens)

        notified_agent_ids: List[str] = []
        routing_details: List[RoutingDecision] = []

        for agent in all_agents:
            # Skip the author themselves
            if agent.id == post.author_id:
                continue

            sub = agent.subscription
            
            # Check negative tag exclusions first (hard filter)
            negative_hit = False
            for neg in sub.negative_tags:
                if neg.lower() in post.content.lower():
                    negative_hit = True
                    break

            if negative_hit:
                decision = RoutingDecision(
                    agent_id=agent.id,
                    agent_name=agent.name,
                    agent_handle=agent.handle,
                    company_name=agent.company_name,
                    industry=agent.industry,
                    score=0.0,
                    semantic_score=0.0,
                    keyword_score=0.0,
                    synergy_score=0.0,
                    feedback_boost=0.0,
                    decision="SKIPPED",
                    reason="Matched negative keyword filter exclusion"
                )
                routing_details.append(decision)
                continue

            # 1. Semantic Vector Score
            agent_corpus = f"{sub.semantic_description} {' '.join(sub.interest_tags)} {agent.industry}"
            agent_tokens = self.vector_engine.tokenize(agent_corpus)
            agent_tf = self.vector_engine.term_frequencies(agent_tokens)
            semantic_score = self.vector_engine.cosine_similarity(post_tf, agent_tf)

            # 2. Keyword & Tag Overlap Score (with subtoken/stemming matching)
            tag_matches = 0
            for tag in sub.interest_tags:
                t_clean = tag.lower().replace("_", " ")
                subwords = t_clean.split()
                # Check direct or subword/stem match
                matched = False
                for token in post_tokens:
                    if token in t_clean or any(token.startswith(sw[:4]) or sw.startswith(token[:4]) for sw in subwords):
                        matched = True
                        break
                if matched or t_clean in post.content.lower():
                    tag_matches += 1

            if tag_matches == 0:
                keyword_score = 0.0
            elif tag_matches == 1:
                keyword_score = 0.55
            elif tag_matches == 2:
                keyword_score = 0.80
            else:
                keyword_score = 1.0

            # 3. Cross-Industry Synergy Score
            synergy_score = default_synergy(post.industry, agent.industry)

            # 4. Feedback Boost
            feedback_boost = self.get_feedback_boost(agent.id, post.industry)

            # Composite Relevance Formula
            # 35% Semantic + 35% Synergy + 30% Keyword + Feedback Boost
            composite_score = (
                (0.35 * semantic_score) +
                (0.35 * synergy_score) +
                (0.30 * keyword_score) +
                feedback_boost
            )
            composite_score = min(max(composite_score, 0.0), 1.0)

            # Decision
            threshold = sub.min_relevance_threshold
            is_notified = composite_score >= threshold

            if is_notified:
                reason = (
                    f"Relevant (Score: {composite_score:.2f} >= {threshold:.2f}). "
                    f"Strong {post.industry} <-> {agent.industry} synergy ({synergy_score:.2f}) "
                    f"and semantic/tag alignment ({semantic_score:.2f})."
                )
                notified_agent_ids.append(agent.id)
                decision_label = "NOTIFIED"
            else:
                reason = (
                    f"Irrelevant (Score: {composite_score:.2f} < {threshold:.2f}). "
                    f"Low synergy ({synergy_score:.2f}) between {post.industry} and {agent.industry}; "
                    f"insufficient shared offer context."
                )
                decision_label = "SKIPPED"

            decision = RoutingDecision(
                agent_id=agent.id,
                agent_name=agent.name,
                agent_handle=agent.handle,
                company_name=agent.company_name,
                industry=agent.industry,
                score=round(composite_score, 3),
                semantic_score=round(semantic_score, 3),
                keyword_score=round(keyword_score, 3),
                synergy_score=round(synergy_score, 3),
                feedback_boost=round(feedback_boost, 3),
                decision=decision_label,
                reason=reason
            )
            routing_details.append(decision)

        # Sort routing details: NOTIFIED first, then highest score
        routing_details.sort(key=lambda d: (d.decision == "NOTIFIED", d.score), reverse=True)
        return notified_agent_ids, routing_details
