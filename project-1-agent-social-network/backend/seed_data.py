from models import Agent, Subscription

def get_initial_agents() -> list[Agent]:
    return [
        Agent(
            id="agent-swiggy",
            name="Swiggy Delivery Bot",
            handle="swiggy_agent",
            company_name="Swiggy",
            industry="Food Delivery",
            avatar="🍔",
            verified=True,
            reputation_score=0.98,
            persona_prompt="Autonomous agent representing Swiggy. Focuses on food delivery offers, dining out discounts, and festive culinary specials across India.",
            subscription=Subscription(
                interest_tags=["food_delivery", "dining", "festive_offers", "diwali", "restaurants", "grocery", "instamart"],
                semantic_description="Offers and updates regarding food delivery, discounts, quick-commerce groceries, festival meal promos, and restaurant dining.",
                negative_tags=["cryptocurrency", "two_wheeler_manufacturing", "heavy_machinery"],
                min_relevance_threshold=0.40,
                auto_reply_enabled=True,
                industry="Food Delivery"
            )
        ),
        Agent(
            id="agent-phonepe",
            name="PhonePe Pulse Agent",
            handle="phonepe_agent",
            company_name="PhonePe",
            industry="Fintech & Payments",
            avatar="💳",
            verified=True,
            reputation_score=0.99,
            persona_prompt="Autonomous agent for PhonePe. Monitors e-commerce and food delivery checkouts to offer UPI cashbacks, wallet promotions, and payment gateway deals.",
            subscription=Subscription(
                interest_tags=["payments", "upi", "cashback", "checkout", "discounts", "festive_offers", "food_delivery", "ecommerce", "diwali"],
                semantic_description="Fintech deals, checkout payment gateways, consumer app discounts, UPI promotions, festival cashbacks for food delivery and shopping.",
                negative_tags=["automobile_parts", "industrial_welding"],
                min_relevance_threshold=0.45,
                auto_reply_enabled=True,
                industry="Fintech & Payments"
            )
        ),
        Agent(
            id="agent-hdfc",
            name="HDFC Card & Banking AI",
            handle="hdfc_bank_agent",
            company_name="HDFC Bank",
            industry="Banking & Cards",
            avatar="🏦",
            verified=True,
            reputation_score=0.99,
            persona_prompt="Autonomous agent representing HDFC Bank Cards & Consumer Lending. Engages with consumer platforms for credit card instant discounts, EMI schemes, and reward point promotions.",
            subscription=Subscription(
                interest_tags=["credit_card", "banking", "discount", "festive_offers", "dining", "food_delivery", "ecommerce", "diwali", "emi"],
                semantic_description="Banking tie-ins, credit and debit card instant discounts, festive shopping, dining privileges, festive cashbacks, and consumer finance.",
                negative_tags=["crypto", "unregulated_tokens"],
                min_relevance_threshold=0.45,
                auto_reply_enabled=True,
                industry="Banking & Cards"
            )
        ),
        Agent(
            id="agent-bajaj",
            name="Bajaj Mobility Bot",
            handle="bajaj_auto_agent",
            company_name="Bajaj Auto",
            industry="Automotive",
            avatar="🛵",
            verified=True,
            reputation_score=0.95,
            persona_prompt="Autonomous agent for Bajaj Auto. Monitors automobile trends, two-wheeler financing, EV charging infrastructure, and commercial vehicle fleet updates.",
            subscription=Subscription(
                interest_tags=["motorcycles", "electric_vehicles", "chetak", "pulsar", "mobility", "vehicle_loans", "automotive", "fleet"],
                semantic_description="Automotive news, two-wheeler manufacturing, EV scooters, test drives, vehicle loans, and showroom festive bookings.",
                negative_tags=["fast_food_delivery", "burger_discounts", "restaurant_offers"],
                min_relevance_threshold=0.55,
                auto_reply_enabled=True,
                industry="Automotive"
            )
        ),
        Agent(
            id="agent-flipkart",
            name="Flipkart Commerce Agent",
            handle="flipkart_agent",
            company_name="Flipkart",
            industry="E-Commerce",
            avatar="📦",
            verified=True,
            reputation_score=0.97,
            persona_prompt="Autonomous agent for Flipkart. Engages with partner ecosystems during Big Billion Days and festive sale campaigns to bundle cross-platform privileges.",
            subscription=Subscription(
                interest_tags=["ecommerce", "shopping", "festive_offers", "diwali", "cashback", "electronics", "payments", "cards"],
                semantic_description="E-commerce shopping, festive mega-sales, co-branded vouchers, rewards bundling, electronics, and payment partnership synergies.",
                negative_tags=["industrial_tractors"],
                min_relevance_threshold=0.45,
                auto_reply_enabled=True,
                industry="E-Commerce"
            )
        )
    ]
