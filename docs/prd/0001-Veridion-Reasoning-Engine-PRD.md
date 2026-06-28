# PRD-0001: Veridion On-Demand Investment Reasoning Engine

| | |
|---|---|
| **Status** | Draft v1 |
| **Author** | Product (via PM interview process) |
| **Date** | 2026-06-28 |
| **Inputs** | `vision.md`, ADR-0001 (Architecture Design Document), Institutional Operations Research Guide |
| **Primary User** | Founder (single self-directed investor), v1 |
| **Document Type** | Product Requirements — defines *what* and *why*; engineering ADRs define *how* |

---

## 1. Summary

Veridion's first product is a single-purpose tool: given a publicly traded US equity ticker (or a narrow, single-company investment question), it produces a complete, evidence-grounded, self-critiqued investment thesis — a Buy / Hold / Avoid recommendation with full justification, explicit confidence, and visible internal disagreement.

This PRD covers only the **on-demand, ticker-driven entry point** to Veridion's reasoning engine ("Entry Point 2" in prior discussions). The always-on, event-driven monitoring entry point ("Entry Point 1") is explicitly deferred to a future PRD and is out of scope here.

The purpose of this product is not to provide investment information. It is to produce **a conclusion the user can decide whether to trust** — and the product succeeds only if it is willing to withhold a confident conclusion when one isn't earned.

---

## 2. Problem Statement

The founder's investing process today is bottlenecked by manual synthesis: financial news, filings, earnings, and price/technical data relevant to a single decision are scattered across many sources, and synthesizing them coherently — fundamentals, technicals, news context, valuation, and risk, weighed against each other — is slow and inconsistent to do by hand, every time, for every name under consideration.

General-purpose LLMs do not solve this safely: they synthesize quickly but ungrounded, frequently inventing facts, sources, or analogies, and presenting conclusions without calibrated uncertainty or visible reasoning.

Veridion's reasoning engine exists to close this gap: fast (relative to manual research) **and** trustworthy (evidence-grounded, self-critiquing, honest about its own uncertainty) — explicitly not optimizing for the speed regime of HFT or market-making firms, which is a different, unwinnable game for this product.

---

## 3. Goals

- **G1.** Given a single US-listed public equity ticker, produce a complete, structured investment thesis without further user input.
- **G2.** Every material claim in the thesis must be traceable to a specific, retrieved evidence source — never to model memory alone.
- **G3.** Every thesis must be challenged by an independent critique process before being finalized, and the critique — and the Research Agent's response to it — must be visible in the final output, not hidden or summarized away.
- **G4.** The system must explicitly represent its own uncertainty, including refusing to issue a confident recommendation when evidence or internal consensus does not support one.
- **G5.** Every analysis must be bounded and reproducible: fixed evidence scope, fixed debate limits, no open-ended or unbounded agent behavior.
- **G6.** Every completed report is persisted, so recommendation quality can be reviewed and calibrated against real-world outcomes over time.

## 4. Non-Goals (Explicitly Out of Scope for PRD-0001)

- Always-on event detection / monitoring (Entry Point 1) — next major milestone, not this one.
- Multi-entity, sector-level, or portfolio-level analysis (e.g., "how exposed am I to semiconductors") — v1 supports exactly one ticker per analysis.
- Any asset class other than US-listed public equities (no crypto, international listings, ETFs, options, fixed income, FX, commodities).
- Portfolio management, position sizing, or automated trade execution of any kind.
- Intrinsic/DCF-style valuation modeling — v1 valuation is multiples-based and deterministic only.
- Curated historical-analogue retrieval — v1 may report "no reliable historical analogue found" as a normal, frequent, and acceptable output.
- Specialist reasoning agents beyond the two defined in this document (no dedicated Macro, Risk, Technical, or Sentiment *agents*). These are data-source tools in v1, not independent reasoning processes — see §6.
- Conversational follow-up / chat interface. Each report is a self-contained, final artifact. A new question is a new analysis, not a continuation.
- Any specific data vendor, API, or model selection — these are engineering/architecture decisions, intentionally not fixed by this PRD.

---

## 5. Target User & Use Case

**User:** The founder, acting as a self-directed individual investor, with an investment horizon of days to weeks (occasionally months) — explicitly not an intraday or HFT timeframe.

**Primary use case:** The user has a candidate ticker or a narrow investment question about a single company ("Should I buy NVIDIA?", "Is this earnings report a reason to sell my position in X?"). They want a thorough, honest, evidence-backed second opinion before making their own decision — not an instruction to be obeyed, and not a raw data dump to be manually synthesized.

**Usage pattern during this phase:** Repeated, deliberate use across many different companies and situations, specifically to build (or lose) confidence in the reasoning engine's judgment before any further investment in the product (event monitoring, broader scope, multi-user productization) is justified.

---

## 6. Core Concept: Evidence Sources vs. Reasoning Agents

This distinction is foundational to the entire product and must be preserved by engineering at every layer:

- **Evidence sources are deterministic tools**, not agents. They retrieve or compute verifiable facts. They do not reason, opine, or interpret. (News retrieval, financial statement retrieval, price-history retrieval, technical-indicator computation, valuation-multiple computation.)
- **Reasoning agents are independent reasoning processes** that interpret evidence and can disagree with one another. v1 has exactly two.

A capability is only added as a third reasoning agent in a future version if there is evidence that splitting it out as an independent reasoning perspective measurably improves thesis quality — not merely because it represents a distinct topic area. Until proven otherwise, more data is not the same problem as more agents.

---

## 7. Functional Requirements

### 7.1 Input

- The system accepts a single US-listed public equity ticker, optionally accompanied by a short natural-language question scoped to that one company (e.g., "should I buy NVDA", "is NVDA's latest earnings report a concern").
- Multi-entity or sector/thematic questions are rejected or redirected; the system should clearly communicate that only single-company analysis is supported in this version, rather than silently attempting a broader analysis.

### 7.2 Evidence Gathering (Deterministic, Checklist-Driven)

The orchestrator — not the Research Agent — owns the evidence-gathering process. It executes a **fixed checklist** of required evidence categories. The Research Agent does not decide what to retrieve or when retrieval is "enough"; it begins reasoning only once the checklist has been executed in full.

| Category | Scope (v1 default) |
|---|---|
| Recent news | Company- and market-relevant news within a fixed lookback window (default: 90 days) |
| Financials | Recent financial statements and key metrics, with enough historical depth to establish trend (default: last 8 quarters) |
| Price / technical data | Historical price data over a fixed window (default: 2 years), used to compute deterministic indicators: moving averages, RSI, MACD, support/resistance |
| Earnings | Most recent earnings report and forward guidance |
| Valuation | Deterministic, multiples-based comparison only (e.g., P/E vs. own historical range, P/S and EV/EBITDA vs. peers) — **no DCF or intrinsic-value modeling in v1** |
| Historical analogues | Best-effort only; if no reliably citable analogue exists, the system must report this explicitly rather than infer one from model memory |

Specific data vendors/APIs are an engineering decision and are out of scope for this document.

**Missing data handling:** If a required evidence category is unavailable for a given ticker (e.g., thin analyst coverage, no recent news), the system proceeds with what is available, **explicitly discloses the gap** in the final report, and reduces confidence accordingly. The system must never fabricate a value for a missing evidence category.

### 7.3 Reasoning Agents

**Research Agent**
- Synthesizes all gathered evidence into a complete, structured investment thesis (see §7.5 for required report structure).
- Must ground every material claim in retrieved evidence; reasoning *about* evidence (interpretation, weighing, implications) is expected and encouraged — *inventing* evidence is not permitted under any circumstance.
- Arrives at an explicit conclusion (Buy / Hold / Avoid, or "Insufficient Confidence" per §7.4) — the system does not present a neutral information dump and leave the conclusion to the user to infer.

**Critic Agent**
- Does not produce a competing thesis. Its sole responsibility is to challenge the Research Agent's thesis: unsupported assumptions, contradictory or cherry-picked evidence, overconfidence, missing risks, logical gaps.
- The Research Agent must respond to each substantial objection raised — by revising the thesis, providing a justified rebuttal, or conceding the point.

### 7.4 Debate Protocol (Convergence-or-Cap)

- The debate proceeds in rounds. It terminates **early** if the Critic Agent has no remaining substantial objections (sign-off).
- If substantial disagreement remains, the debate continues up to a **fixed maximum of three rounds**, after which it terminates regardless of resolution status, to guarantee bounded, deterministic execution.
- The Critic Agent has no unilateral veto over the final recommendation. Unresolved disagreement does not automatically force a negative verdict; instead, it is disclosed and lowers confidence (§7.5).
- The debate's outcome is classified as one of: **Full Consensus**, **Partial Consensus**, or **Unresolved Disagreement** — this classification is a required, visible field in the final report, not an internal-only signal.

### 7.5 Confidence & Final Verdict

- The system computes a single **Confidence** value reflecting the system's estimated reliability of the thesis, informed by: evidence quality, evidence completeness (including any disclosed gaps from §7.2), and internal consensus status from §7.4. The exact calculation method is an engineering decision, not fixed by this PRD — but it must, at minimum, account for all three of these inputs and be inspectable (i.e., the report must show *why* confidence landed where it did, not just the number).
- A **configurable confidence threshold** determines whether the system issues a directional recommendation at all. If confidence falls below the configured threshold, the final verdict is **"Insufficient Confidence"** rather than a forced Buy/Hold/Avoid call — regardless of how compelling the Research Agent's original thesis appeared before critique.
- Confidence and consensus status are related but distinct: unresolved disagreement is one *input* to confidence, not a separate override mechanism. There is exactly one gate between the reasoning process and the final verdict: the confidence threshold.

### 7.6 Output: Investment Thesis Report

Every analysis produces one final, self-contained report artifact with the following required sections, in order:

1. **Final Recommendation** — Buy / Hold / Avoid / Insufficient Confidence
2. **Confidence Level** — with a brief stated rationale (what drove it up or down)
3. **Expected Investment Horizon**
4. **Executive Summary**
5. **Bull Case**
6. **Bear Case**
7. **Fundamental Analysis**
8. **Technical Analysis**
9. **Recent News & Key Catalysts**
10. **Valuation Summary** (multiples-based, per §7.2)
11. **Historical Context / Similar Situations** (or explicit statement that none was found)
12. **Key Risks**
13. **Supporting Evidence & Sources** — every cited source must trace to something actually retrieved in §7.2, never an unsourced assertion
14. **Critic Agent's Objections**
15. **Research Agent's Responses to Objections**
16. **Consensus Status** — Full Consensus / Partial Consensus / Unresolved Disagreement
17. **Final Revised Verdict** — confirming or revising the recommendation in (1) after the debate in §7.4

Any required evidence category that was unavailable (§7.2) must be visibly flagged within the relevant section — silently omitting a missing category is not acceptable.

### 7.7 Persistence

- Every completed report is stored locally, in full, including the underlying debate trail (objections and responses) and the evidence actually retrieved for that run.
- Purpose: enabling later review, audit, and comparison of past recommendations against real-world outcomes, as the primary mechanism for evaluating and improving the reasoning engine over time.
- No specific storage technology is prescribed here; this is an engineering decision (see ADR-0001 for current direction).

---

## 8. Explicit Design Principles Governing This Product

These principles, established during product discovery, constrain all future engineering and design decisions for this scope and should be treated as binding unless explicitly revisited in a future PRD:

- **Reason about evidence, not manufacture evidence.** Wherever a capability can be implemented deterministically against verifiable data, it must be — the LLM's role is interpretation, not fact generation.
- **Disagreement is disclosed, not vetoed.** No single agent has unilateral authority to force a negative outcome; honesty about unresolved disagreement is preferred over forced consensus.
- **A withheld recommendation is a valid, desirable outcome**, not a failure state. The system must be willing to say "Insufficient Confidence" whenever that is the most honest conclusion.
- **Every workflow has a predictable, bounded stopping point.** No open-ended evidence gathering, no unbounded debate.
- **Quality of reasoning is the product.** Event detection, broader scope, and additional agents are justified only once this core engine has demonstrated trustworthy judgment in repeated, real use.

---

## 9. Success Criteria for This Phase

Because the entire purpose of this phase is to validate reasoning quality (not to ship a finished product), success is evaluated primarily through the founder's own repeated use, not through usage metrics. Concretely, this phase should be considered successful if, across many repeated analyses on real tickers:

- Recommendations are consistently traceable — every material claim resolves to an actual cited, retrieved source.
- The Critic Agent demonstrably changes outcomes at least some of the time (revises confidence, forces revision, or produces a downgraded verdict) — if it never does, it is not functioning as an independent check and must be revisited before this phase is considered validated.
- "Insufficient Confidence" is issued when warranted, and not avoided in favor of a more decisive-sounding but less justified verdict.
- The founder develops a stable, calibrated sense of when to trust a given report — not necessarily that the recommendations are always *correct* (an explicitly non-goal — see vision.md §12, "not a black-box predictive oracle"), but that the reasoning behind them is consistently logical, evidence-based, and honest.

---

## 10. Open Risks & Known Limitations (Carried Forward, Not Resolved Here)

- **Confidence calculation is directionally specified but not fully defined.** It must incorporate evidence quality, completeness, and consensus status, and must be inspectable — but the precise formula/method is deferred to engineering design. This is the single most load-bearing undefined mechanism in this product and should be prioritized early in implementation.
- **This is a multi-month build, not a quick iteration**, even with the deliberate scope cuts in this PRD (two agents, no DCF, no historical-analogue database, no monitoring). The two-agent debate loop alone sits late in the engineering roadmap's own phased sequence (after data ingestion and memory). The cuts made here were the right cuts for learning speed — they are not a shortcut to a fast build.
- **No conversational follow-up is an accepted limitation, not an oversight.** The founder will likely want to interrogate individual reports ("why did you weight X so heavily") and will not be able to in this version. Re-running a fresh analysis is the accepted workaround for this phase.
- **Single-ticker scope will feel limiting quickly** given that real investment questions ("how exposed am I to semiconductors") are often multi-entity. This is intentional and deferred, not forgotten.

---

## 11. Future Phases (Not Specified Here, Noted for Context)

- **Phase 2:** Event-driven entry point — always-on monitoring that detects market-moving events and invokes this same reasoning engine as a trigger, once the engine's judgment is trusted in this on-demand form.
- **Later:** Multi-entity / sector-level questions; additional asset classes; specialist reasoning agents (Macro, Risk, etc.), if and only if evidence shows they improve outcomes; curated historical-analogue retrieval with proper citation; conversational interrogation of completed reports.

These are explicitly **not** committed to by this PRD and require their own product discovery process before being scoped.

---

*End of PRD-0001 draft. This document defines product requirements only; technical implementation, data vendor selection, and infrastructure decisions are governed separately by the project's ADR process.*
