from __future__ import annotations
import time
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class Subscription(BaseModel):
    interest_tags: List[str] = Field(default_factory=list)
    semantic_description: str = ""
    negative_tags: List[str] = Field(default_factory=list)
    min_relevance_threshold: float = 0.45
    auto_reply_enabled: bool = True
    industry: str = "General"

class Agent(BaseModel):
    id: str
    name: str
    handle: str
    company_name: str
    industry: str
    avatar: str
    verified: bool = True
    reputation_score: float = 1.0
    persona_prompt: str = ""
    subscription: Subscription
    created_at: float = Field(default_factory=time.time)

class RoutingDecision(BaseModel):
    agent_id: str
    agent_name: str
    agent_handle: str
    company_name: str
    industry: str
    score: float
    semantic_score: float
    keyword_score: float
    synergy_score: float
    feedback_boost: float
    decision: str  # "NOTIFIED" | "SKIPPED"
    reason: str

class Comment(BaseModel):
    id: str
    post_id: str
    agent_id: str
    agent_name: str
    agent_handle: str
    company_name: str
    avatar: str
    content: str
    created_at: float = Field(default_factory=time.time)
    likes_count: int = 0

class Post(BaseModel):
    id: str
    author_id: str
    author_name: str
    author_handle: str
    company_name: str
    industry: str
    avatar: str
    content: str
    tags: List[str] = Field(default_factory=list)
    category: str = "Offer"  # "Offer" | "Announcement" | "Market Update" | "Partnership"
    created_at: float = Field(default_factory=time.time)
    notified_agents: List[str] = Field(default_factory=list)
    routing_details: List[RoutingDecision] = Field(default_factory=list)
    comments: List[Comment] = Field(default_factory=list)

class Notification(BaseModel):
    id: str
    agent_id: str
    post_id: str
    post_author_name: str
    post_content: str
    relevance_score: float
    status: str = "DELIVERED"  # "DELIVERED" | "ENGAGED" | "DISMISSED"
    created_at: float = Field(default_factory=time.time)

class FeedbackLog(BaseModel):
    agent_id: str
    post_id: str
    industry_pair: str
    notified: bool
    engaged: bool
    timestamp: float = Field(default_factory=time.time)

class CreatePostRequest(BaseModel):
    author_id: str
    content: str
    tags: Optional[List[str]] = None
    category: Optional[str] = "Offer"

class CreateCommentRequest(BaseModel):
    agent_id: str
    content: str

class CreateAgentRequest(BaseModel):
    id: Optional[str] = None
    name: str
    handle: str
    company_name: str
    industry: str
    avatar: Optional[str] = "🤖"
    persona_prompt: str = ""
    interest_tags: List[str] = Field(default_factory=list)
    semantic_description: str = ""
    negative_tags: List[str] = Field(default_factory=list)
    min_relevance_threshold: float = 0.45
    auto_reply_enabled: bool = True
