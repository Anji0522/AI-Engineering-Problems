from __future__ import annotations
import os
import sys
import uuid
import time
import asyncio
from typing import List, Dict, Optional, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from models import (
    Agent, Subscription, Post, Comment, Notification, RoutingDecision, FeedbackLog,
    CreatePostRequest, CreateCommentRequest, CreateAgentRequest
)
from router_engine import RelevanceRouter
from agent_runner import AgentPersonaRunner
from trust_safety import TrustAndSafetyManager
from seed_data import get_initial_agents

app = FastAPI(title="AgentVerse: A Social Network for AI Agents", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for rapid, transparent state inspection
agents_db: Dict[str, Agent] = {}
posts_db: Dict[str, Post] = {}
notifications_db: List[Notification] = []
feedback_logs_db: List[FeedbackLog] = []

router = RelevanceRouter()
runner = AgentPersonaRunner()
safety_manager = TrustAndSafetyManager()

# Active WebSocket connections
active_connections: List[WebSocket] = []

async def broadcast_event(event_type: str, data: Any):
    payload = {"type": event_type, "data": data, "timestamp": time.time()}
    disconnected = []
    for ws in active_connections:
        try:
            await ws.send_json(payload)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        if ws in active_connections:
            active_connections.remove(ws)

def initialize_database():
    initial_agents = get_initial_agents()
    for ag in initial_agents:
        agents_db[ag.id] = ag

initialize_database()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Keepalive / ping
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.get("/api/agents", response_model=List[Agent])
def list_agents():
    return list(agents_db.values())

@app.post("/api/agents", response_model=Agent)
async def register_agent(req: CreateAgentRequest):
    agent_id = req.id or f"agent-{uuid.uuid4().hex[:8]}"
    if agent_id in agents_db:
        raise HTTPException(status_code=400, detail="Agent ID already exists")

    agent = Agent(
        id=agent_id,
        name=req.name,
        handle=req.handle.replace("@", ""),
        company_name=req.company_name,
        industry=req.industry,
        avatar=req.avatar or "🤖",
        verified=True,
        reputation_score=1.0,
        persona_prompt=req.persona_prompt,
        subscription=Subscription(
            interest_tags=req.interest_tags,
            semantic_description=req.semantic_description,
            negative_tags=req.negative_tags,
            min_relevance_threshold=req.min_relevance_threshold,
            auto_reply_enabled=req.auto_reply_enabled,
            industry=req.industry
        )
    )
    agents_db[agent.id] = agent
    await broadcast_event("AGENT_REGISTERED", agent.dict())
    return agent

@app.get("/api/posts", response_model=List[Post])
def list_posts():
    # Return reverse chronological
    return sorted(list(posts_db.values()), key=lambda p: p.created_at, reverse=True)

@app.get("/api/posts/{post_id}", response_model=Post)
def get_post(post_id: str):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    return posts_db[post_id]

@app.post("/api/posts", response_model=Post)
async def create_post(req: CreatePostRequest):
    if req.author_id not in agents_db:
        raise HTTPException(status_code=404, detail="Author agent not registered")
    
    author = agents_db[req.author_id]

    # 1. Trust & Safety Screening
    is_safe, safety_msg = safety_manager.check_post_safety(author.id, req.content)
    if not is_safe:
        raise HTTPException(status_code=400, detail=safety_msg)

    # Auto-extract tags if not explicitly provided
    tags = req.tags or []
    if not tags:
        for word in ["diwali", "festive", "offer", "discount", "cashback", "delivery", "upi", "cards", "shopping"]:
            if word in req.content.lower() and word not in tags:
                tags.append(word)

    post_id = f"post-{uuid.uuid4().hex[:8]}"
    post = Post(
        id=post_id,
        author_id=author.id,
        author_name=author.name,
        author_handle=author.handle,
        company_name=author.company_name,
        industry=author.industry,
        avatar=author.avatar,
        content=req.content,
        tags=tags,
        category=req.category or "Offer",
        created_at=time.time()
    )

    # 2. Relevance Routing (Core Problem)
    notified_ids, routing_decisions = router.route_post(post, list(agents_db.values()))
    post.notified_agents = notified_ids
    post.routing_details = routing_decisions
    posts_db[post.id] = post

    # 3. Create Notifications
    for decision in routing_decisions:
        if decision.decision == "NOTIFIED":
            notif = Notification(
                id=f"notif-{uuid.uuid4().hex[:8]}",
                agent_id=decision.agent_id,
                post_id=post.id,
                post_author_name=author.name,
                post_content=post.content,
                relevance_score=decision.score,
                status="DELIVERED"
            )
            notifications_db.append(notif)

    await broadcast_event("POST_CREATED", post.dict())

    # 4. Asynchronous Notified Agent Auto-Response Loop
    asyncio.create_task(process_agent_responses(post, notified_ids))

    return post

async def process_agent_responses(post: Post, notified_agent_ids: List[str]):
    """
    Simulates agent response cycle:
    1. Agent receives notification
    2. Decides whether to engage
    3. Drafts response with LLM/persona
    4. Posts comment back
    5. Feeds engagement into learning loop
    """
    for agent_id in notified_agent_ids:
        agent = agents_db.get(agent_id)
        if not agent:
            continue

        # Brief realistic stagger between agent replies
        await asyncio.sleep(0.8)

        if not agent.subscription.auto_reply_enabled:
            router.record_feedback(agent.id, post.industry, engaged=False)
            continue

        # Draft comment via Agent Persona / LLM
        reply_text = runner.draft_comment(agent, post)
        if reply_text:
            comment = Comment(
                id=f"comment-{uuid.uuid4().hex[:8]}",
                post_id=post.id,
                agent_id=agent.id,
                agent_name=agent.name,
                agent_handle=agent.handle,
                company_name=agent.company_name,
                avatar=agent.avatar,
                content=reply_text,
                created_at=time.time(),
                likes_count=1
            )
            post.comments.append(comment)

            # Update notification status
            for notif in notifications_db:
                if notif.post_id == post.id and notif.agent_id == agent.id:
                    notif.status = "ENGAGED"

            # Record feedback: notification converted to comment!
            router.record_feedback(agent.id, post.industry, engaged=True)
            feedback_logs_db.append(FeedbackLog(
                agent_id=agent.id,
                post_id=post.id,
                industry_pair=f"{post.industry} -> {agent.industry}",
                notified=True,
                engaged=True
            ))

            await broadcast_event("COMMENT_ADDED", {
                "post_id": post.id,
                "comment": comment.dict(),
                "agent_id": agent.id
            })

@app.post("/api/posts/{post_id}/comments", response_model=Comment)
async def add_comment(post_id: str, req: CreateCommentRequest):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    if req.agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    post = posts_db[post_id]
    agent = agents_db[req.agent_id]

    comment = Comment(
        id=f"comment-{uuid.uuid4().hex[:8]}",
        post_id=post.id,
        agent_id=agent.id,
        agent_name=agent.name,
        agent_handle=agent.handle,
        company_name=agent.company_name,
        avatar=agent.avatar,
        content=req.content,
        created_at=time.time()
    )
    post.comments.append(comment)
    router.record_feedback(agent.id, post.industry, engaged=True)

    await broadcast_event("COMMENT_ADDED", {
        "post_id": post.id,
        "comment": comment.dict(),
        "agent_id": agent.id
    })
    return comment

@app.get("/api/notifications", response_model=List[Notification])
def get_notifications(agent_id: Optional[str] = None):
    if agent_id:
        return [n for n in notifications_db if n.agent_id == agent_id]
    return notifications_db[-50:]

@app.get("/api/feedback/stats")
def get_feedback_stats():
    total_notifications = len(notifications_db)
    engaged_count = len([n for n in notifications_db if n.status == "ENGAGED"])
    engagement_rate = (engaged_count / total_notifications * 100) if total_notifications > 0 else 0.0

    return {
        "total_notifications": total_notifications,
        "engaged_comments": engaged_count,
        "engagement_rate_pct": round(engagement_rate, 1),
        "feedback_weights": [
            {"agent_id": k[0], "author_industry": k[1], "boost": round(v, 3)}
            for k, v in router.feedback_weights.items()
        ],
        "agent_stats": router.agent_stats
    }

@app.post("/api/seed/swiggy-diwali", response_model=Post)
async def trigger_interview_example():
    """
    Exact scenario from Page 1 of Interview Problems:
    Swiggy posts: '5% off all deliveries on Diwali.'
    Platform routes to PhonePe & HDFC Bank, skips Bajaj Auto.
    PhonePe & HDFC Bank agents post comments.
    """
    swiggy_agent = agents_db.get("agent-swiggy")
    if not swiggy_agent:
        initialize_database()
        swiggy_agent = agents_db["agent-swiggy"]

    req = CreatePostRequest(
        author_id=swiggy_agent.id,
        content="5% off all deliveries on Diwali.",
        tags=["diwali", "delivery", "food_delivery", "festive_offers"],
        category="Offer"
    )
    return await create_post(req)

# Mount frontend directory for easy web UI preview
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
