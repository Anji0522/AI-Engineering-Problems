import sys
import os

def test_project_1():
    print("=" * 60)
    print("TESTING PROJECT 1: AgentVerse Social Network")
    print("=" * 60)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "project-1-agent-social-network", "backend"))
    from seed_data import get_initial_agents
    from router_engine import RelevanceRouter
    from agent_runner import AgentPersonaRunner
    from models import Post
    import time

    agents = get_initial_agents()
    router = RelevanceRouter()
    runner = AgentPersonaRunner()

    post = Post(
        id="test-post-1",
        author_id="agent-swiggy",
        author_name="Swiggy Delivery Bot",
        author_handle="swiggy_agent",
        company_name="Swiggy",
        industry="Food Delivery",
        avatar="🍔",
        content="5% off all deliveries on Diwali.",
        tags=["diwali", "delivery"],
        created_at=time.time()
    )

    notified_ids, details = router.route_post(post, agents)
    print("Post:", post.content)
    print("Notified Agent IDs:", notified_ids)
    assert "agent-phonepe" in notified_ids, "PhonePe should be notified"
    assert "agent-hdfc" in notified_ids, "HDFC Bank should be notified"
    assert "agent-bajaj" not in notified_ids, "Bajaj Auto must NOT be notified"
    print("✅ Routing logic verified exactly as specified in interview prompt!")

    for agent_id in notified_ids:
        agent = next(a for a in agents if a.id == agent_id)
        reply = runner.draft_comment(agent, post)
        print(f"  Comment by {agent.company_name} (@{agent.handle}): \"{reply}\"")
        assert len(reply) > 10

def test_project_2():
    print("\n" + "=" * 60)
    print("TESTING PROJECT 2: Linux Hardware Q&A Assistant")
    print("=" * 60)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "project-2-linux-hardware-assistant", "backend"))
    from assistant_agent import HardwareAssistantAgent
    from safety_guard import SafetyGuard, SecurityException

    # 1. Test Safety Guard
    print("Testing Safety Guard allow-listing...")
    binary, args = SafetyGuard.validate_cli_command(["lscpu", "-J"])
    assert binary == "lscpu"
    print("  Allow-listed valid command passed: lscpu -J")

    try:
        SafetyGuard.validate_cli_command(["rm", "-rf", "/"])
        assert False, "Should have thrown SecurityException"
    except SecurityException as e:
        print(f"  Dangerous command successfully blocked: {e}")

    try:
        SafetyGuard.validate_cli_command(["lscpu", ";", "cat", "/etc/shadow"])
        assert False, "Should have thrown SecurityException"
    except SecurityException as e:
        print(f"  Command injection attempt successfully blocked: {e}")

    # 2. Test Agent Hardware Queries
    agent = HardwareAssistantAgent()

    test_cases = [
        ("Can I add more RAM, and how much?", ["16 GB in 1 of 2 slots", "64 GB"]),
        ("How much RAM do I have?", ["16", "GB"]),
        ("Is my SSD NVMe?", ["Yes", "NVMe"]),
        ("and what about the GPU?", ["NVIDIA", "GeForce RTX 3050 Ti Mobile"]),
        ("What is my screen refresh rate?", ["I don't know"])
    ]

    for query, expected_substrings in test_cases:
        res = agent.answer_query(query)
        print(f"\nUser: \"{query}\"")
        print(f"Tools Used: {res['selected_tools']}")
        print(f"Answer: {res['answer']}")
        for exp in expected_substrings:
            assert exp.lower() in res["answer"].lower(), f"Expected '{exp}' in answer: {res['answer']}"

    print("\n✅ All hardware tool-calling & anti-hallucination tests passed successfully!")

if __name__ == "__main__":
    test_project_1()
    test_project_2()
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED ACROSS BOTH PROJECTS!")
    print("=" * 60)
