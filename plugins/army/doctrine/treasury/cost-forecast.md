# Cost forecaster

Goal: know what the product costs to run per user and in total, and when it becomes profitable.

## Cost categories
- **Infrastructure:** hosting, database, storage, bandwidth, CDN (from logistics/infra-cost if available)
- **Third-party APIs and SaaS:** email/SMS, maps, payments, auth, analytics, monitoring
- **AI/LLM usage:** calls per user per month × average input and output tokens × current price per token (verify), with prompt caching and batch discounts where they apply. Model choice matters a lot: route easy work to cheaper models.
- **Store and payment fees,** taxes, domains, legal and accounting, developer accounts (Apple Developer Program, Google Play)
- **People and time,** if the brief includes them

## Unit economics
- Cost per active user per month, revenue per user (ARPU), gross margin
- CAC estimate (from growth), payback period, and LTV in rough terms
- Break-even users = fixed costs ÷ (ARPU − variable cost per user)

## Output
Assumptions table · cost model in three scenarios (low/base/high) · unit economics · top 3 cost risks and levers to reduce them. Every price must be dated with a source.
