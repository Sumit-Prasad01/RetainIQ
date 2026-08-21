"""Prescriptive AI Retention Action Plan and Strategy Generator."""

from typing import Any, Dict, List


def generate_retention_playbook(payload: Dict[str, Any], probability: float) -> Dict[str, Any]:
    """Generate prescriptive, actionable retention strategies tailored to the customer's profile and risk score."""
    strategies: List[Dict[str, Any]] = []
    urgent_actions: List[str] = []

    is_active = payload.get("isactive", True)
    num_products = payload.get("numproducts", 1)
    age = payload.get("age", 40)
    balance = payload.get("balance", 0.0)
    geography = payload.get("geography", "France")
    tenure = payload.get("tenure", 3)

    # Inactivity Strategy
    if not is_active:
        strategies.append({
            "title": "⚡ Priority Re-Activation Campaign",
            "priority": "Critical",
            "channel": "Direct Call / Dedicated RM Outreach",
            "action": "Assign a dedicated Relationship Manager to conduct a high-touch check-in call within 48 hours. Offer fee waivers or upgraded account tier to revive primary account usage.",
            "expected_reduction": "-15% to -20% Churn Probability",
        })
        urgent_actions.append("Trigger automated CRM alert to Regional Retention Desk for dormant account intervention.")

    # Product Cross-Sell Strategy
    if num_products == 1:
        strategies.append({
            "title": "📦 Relationship Deepening & Product Cross-Sell",
            "priority": "High",
            "channel": "Personalized Mobile App & Email Offer",
            "action": "Offer pre-approved High-Yield Savings Account or Cashback Credit Card with a introductory 0.5% APY bonus. Customers with 2 products have an 80% higher retention rate.",
            "expected_reduction": "-12% to -18% Churn Probability",
        })
    elif num_products >= 3:
        strategies.append({
            "title": "🔍 Product Fee & Account Consolidation Review",
            "priority": "High",
            "channel": "Advisory Consultation",
            "action": "Perform fee audit across customer's multi-product suite. Bundle accounts into a unified premier tier to eliminate unexpected transaction or maintenance charges.",
            "expected_reduction": "-10% to -15% Churn Probability",
        })

    # High Balance Protection
    if balance > 100000:
        strategies.append({
            "title": "🛡️ High-Net-Worth Deposit Retention Package",
            "priority": "High",
            "channel": "Private Banking Specialist",
            "action": f"Protect high-balance deposit (${balance:,.2f}) by offering customized Wealth Advisory, preferred FX rates, or fixed-term certificates of deposit (CD) with competitive yield.",
            "expected_reduction": "-8% to -14% Churn Probability",
        })
        urgent_actions.append(f"Place deposit liquidity watch on account (${balance:,.2f} at risk).")

    # Regional Germany Strategy
    if geography == "Germany":
        strategies.append({
            "title": "🇩🇪 German Market Retention Incentive",
            "priority": "Medium",
            "channel": "Direct Mail & Digital Banking Portal",
            "action": "Provide specialized German market fee concessions, free SEPA premium transfers, and local branch access perks to counter aggressive regional fintech competitors.",
            "expected_reduction": "-7% to -11% Churn Probability",
        })

    # Senior Cohort Strategy
    if age >= 50:
        strategies.append({
            "title": "👵 Senior Relationship Management & Retirement Planning",
            "priority": "Medium",
            "channel": "In-Branch Consultation / Concierge Phone Line",
            "action": "Provide complimentary retirement portfolio review, estate planning consultation, and priority phone line routing to experienced senior bankers.",
            "expected_reduction": "-6% to -10% Churn Probability",
        })

    # New Customer Onboarding Strategy
    if tenure <= 1:
        strategies.append({
            "title": "🚀 90-Day VIP Onboarding Journey",
            "priority": "Medium",
            "channel": "Multi-Channel (SMS + App + Email)",
            "action": "Enroll customer in structured digital onboarding series showcasing bill pay, mobile deposit, rewards catalog, and direct deposit setup incentives.",
            "expected_reduction": "-5% to -9% Churn Probability",
        })

    # Default baseline retention strategy if customer is already healthy
    if not strategies:
        strategies.append({
            "title": "🌟 Loyalty Reward & Recognition Campaign",
            "priority": "Low",
            "channel": "Annual Appreciation Notification",
            "action": "Send annual anniversary thank-you bonus, preferred interest rate coupons, and early access to new investment products.",
            "expected_reduction": "Maintains <5% baseline churn rate",
        })

    urgency_level = "Immediate Intervention" if probability >= 0.40 else "Proactive Nurture" if probability >= 0.20 else "Standard Retention"

    return {
        "urgency_level": urgency_level,
        "strategies": strategies,
        "urgent_actions": urgent_actions,
    }
