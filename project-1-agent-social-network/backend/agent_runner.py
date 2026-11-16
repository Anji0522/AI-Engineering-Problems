from __future__ import annotations
import os
import re
import random
import uuid
import time
import urllib.request
import json
from typing import Optional, List, Dict
from models import Agent, Post, Comment

class AgentPersonaRunner:
    """
    Simulates or executes AI Agent responses when notified about posts.
    Can utilize Gemini API / OpenAI API if keys are provided,
    or use contextual domain-grounded persona synthesis.
    """
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

    def draft_comment(self, agent: Agent, post: Post) -> str:
        # Check if external LLM can be used
        if self.gemini_api_key:
            try:
                llm_reply = self._call_gemini(agent, post)
                if llm_reply:
                    return llm_reply
            except Exception as e:
                print(f"[LLM Fallback] Error contacting Gemini: {e}")

        # Contextual Persona Engine
        return self._synthesize_persona_response(agent, post)

    def _call_gemini(self, agent: Agent, post: Post) -> Optional[str]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        prompt = (
            f"You are the official autonomous AI agent for {agent.company_name} ({agent.handle}). "
            f"Your industry is {agent.industry}. "
            f"Your persona description: {agent.persona_prompt}. "
            f"Another company's agent ({post.author_name} - @{post.author_handle}, Industry: {post.industry}) posted: "
            f"\"{post.content}\". "
            f"Draft a short, engaging, realistic social media comment (1-2 sentences) on how your company "
            f"can partner, complement, or offer a synergistic deal for this post. Keep it sharp and professional."
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 100}
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    def _synthesize_persona_response(self, agent: Agent, post: Post) -> str:
        company = agent.company_name.lower()
        content = post.content.lower()
        author = post.author_name

        # Diwali / Festive Context
        is_festive = "diwali" in content or "festive" in content or "holiday" in content or "celebration" in content

        # PhonePe Persona
        if "phonepe" in company:
            if is_festive:
                return f"Extra ₹50 cashback when you pay for {author} orders with PhonePe UPI this festive season! Let's celebrate together. 🪔✨"
            return f"Seamless checkout unlocked! Get flat 5% instant cashback on all {author} transactions using PhonePe UPI."

        # HDFC Bank Persona
        if "hdfc" in company:
            if is_festive:
                return f"Double the celebrations! Pay with HDFC Bank Credit Cards on {author} to get an additional 10% instant discount up to ₹150."
            return f"Great initiative by {author}! HDFC Bank cardholders get 5X Reward Points and zero convenience fee on every order."

        # Flipkart Persona
        if "flipkart" in company:
            return f"Diwali celebrations just leveled up! Pair your {author} feasts with exclusive Flipkart Big Billion Day vouchers inside the app. 🛍️"

        # Zomato Persona
        if "zomato" in company:
            return f"Game recognize game! May the festive food rush bring joy and rapid deliveries to everyone celebrating."

        # Bajaj Auto Persona
        if "bajaj" in company:
            return f"Power your festival with freedom! Explore zero-down-payment bookings on all Bajaj Pulsar and Chetak EV models today."

        # General / Custom Agent Persona
        if agent.persona_prompt:
            return f"Synergy alert from {agent.company_name}: We are excited to collaborate with {author} on this festive rollout!"

        return f"{agent.company_name} is excited to support {author}'s latest announcement with exclusive partner benefits."
