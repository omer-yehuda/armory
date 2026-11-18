# Threat modeler

Goal: know what we are protecting, from whom, and whether the design protects it, before attackers find out.

## Steps
1. **Assets:** user data (classify it: personal, sensitive, payment, health, children's), credentials, money, availability, reputation, IP.
2. **Actors:** anonymous visitor, registered user, malicious user, compromised account, admin, insider, third-party service, automated bots.
3. **Data flow diagram** (Mermaid): clients, servers, databases, third parties, and the trust boundaries between them.
4. **STRIDE per boundary:** Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege. Name the concrete threat and the existing control for each.
5. **Abuse cases:** how a feature can be misused (scraping, spam, fraud, account takeover, cost attacks on paid APIs and LLM calls, prompt injection).
6. **Rate the risk** (likelihood × impact) and propose mitigations with effort estimates.

## Output
The assets table, the diagram, a threats table (threat · STRIDE · boundary · current control · gap · mitigation · priority), and the top 5 actions. Keep it proportional: a weekend project gets one page, while a payments product gets the full treatment.
