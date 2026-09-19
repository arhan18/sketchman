# Risk Register: WealthInk

**Methodology:** Likelihood (1-5) × Impact (1-5) = Risk Score (1-25)
**Review Cadence:** Monthly (quarterly deep-dive)

---

## Risk Matrix

| Score | Rating | Action |
|-------|--------|--------|
| 20-25 | **Critical** | Immediate mitigation, weekly monitoring |
| 15-19 | **High** | Mitigation within 2 weeks, bi-weekly monitoring |
| 10-14 | **Medium** | Mitigation within 1 month, monthly monitoring |
| 5-9 | **Low** | Track, mitigate opportunistically |
| 1-4 | **Minimal** | Accept, no action needed |

---

## Platform & API Risks

| # | Risk | Likelihood | Impact | Score | Category | Mitigation | Owner | Status |
|---|------|------------|--------|-------|----------|------------|-------|--------|
| R1 | YouTube Data API quota exhausted (10K/day default) | 4 | 5 | **20** | Platform | • 1 upload/day guard in code<br>• Quota tracking in state.py<br>• Apply for quota increase at 5K subs<br>• Stagger across 2 Google Cloud projects if needed | You | 🟢 Implemented |
| R2 | OAuth refresh token expires (Testing mode = 7 days) | 5 | 5 | **25** | Platform | • Publish OAuth consent screen to Production<br>• reauth.py for one-click rotation<br>• Alert on `invalid_grant`<br>• Monitor token age in state.py | You | 🟡 Pending (need to publish app) |
| R3 | YouTube API breaking changes / deprecation | 2 | 5 | 10 | Platform | • Pin google-api-python-client version<br>• Test in staging before deploy<br>• Monitor Google Workspace Updates blog | You | 🟢 Monitoring |
| R4 | Channel demonetization / limited ads | 2 | 5 | 10 | Platform | • Original scripts only (no copied content)<br>• AI disclosure in description<br>• No controversial/political topics<br>• Fair use only for public domain charts | You | 🟢 Compliant |
| R5 | Channel termination (3 strikes) | 1 | 5 | 5 | Platform | • Zero copyrighted music/assets<br>• Original visuals (PIL-generated)<br>• TTS voices licensed (Kokoro Apache 2.0, Edge Microsoft)<br>• Backup channel created | You | 🟢 Compliant |

---

## Content & AI Policy Risks

| # | Risk | Likelihood | Impact | Score | Category | Mitigation | Owner | Status |
|---|------|------------|--------|-------|----------|------------|-------|--------|
| R6 | YouTube AI content labeling becomes mandatory | 3 | 4 | 12 | Policy | • Add "Generated with AI assistance" to description now<br>• Keep scripts 100% human-written<br>• Visuals are code-generated (not generative AI)<br>• Voice is TTS (disclosed) | You | 🟡 Add to descriptions |
| R7 | "Repurposed content" flag on Shorts/Reels | 3 | 4 | 12 | Policy | • Shorts are distinct scripts (not clips from long)<br>• Unique thumbnails per format<br>• Platform-native captions/hashtags<br>• Cross-post within 24h, not simultaneous | You | 🟢 Process defined |
| R8 | Copyright claim on background music/effects | 1 | 4 | 4 | Legal | • No background music used<br>• Sound effects: none (silent visuals)<br>• TTS only — no third-party audio | You | 🟢 Safe |
| R9 | Defamation / financial advice liability | 2 | 4 | 8 | Legal | • Disclaimer: "Not financial advice. Educational only."<br>• No specific stock picks<br>• General principles only<br>• Indian jurisdiction disclaimer | You | 🟢 Add to descriptions |

---

## Technical & Operational Risks

| # | Risk | Likelihood | Impact | Score | Category | Mitigation | Owner | Status |
|---|------|------------|--------|-------|----------|------------|-------|--------|
| R10 | GitHub Actions runner failures (ephemeral) | 3 | 3 | 9 | Ops | • State persisted in git + Actions cache<br>• Concurrency group prevents race conditions<br>• `continue-on-error` on commit step<br>• Manual `workflow_dispatch` for re-runs | You | 🟢 Implemented |
| R11 | FFmpeg / PIL rendering failure (dependency drift) | 3 | 4 | 12 | Tech | • Pin system deps in workflow (apt packages)<br>• Pin Python deps in requirements.txt<br>• Test locally before push<br>• Cache Kokoro models (~200MB) | You | 🟢 Pinned |
| R12 | TTS failure (Kokoro + Edge both down) | 2 | 5 | 10 | Tech | • 3 retries with backoff for Edge<br>• Kokoro probe catches native crashes<br>• Local fallback test in generate.py<br>• Alert on TTS failure | You | 🟢 Implemented |
| R13 | Thumbnail upload fails (unverified channel) | 4 | 2 | 8 | Tech | • Non-fatal in upload.py (warn only)<br>• Video still publishes<br>• Apply for verification at 100K subs<br>• Custom thumbnail not required for Shorts | You | 🟢 Handled |
| R14 | State.json corruption / merge conflict | 2 | 4 | 8 | Data | • Dual store (git + cache) with timestamp merge<br>• Force-with-lease on push<br>• JSON schema validation on load<br>• Manual recovery: `python state.py record ...` | You | 🟢 Implemented |

---

## Financial & Business Risks

| # | Risk | Likelihood | Impact | Score | Category | Mitigation | Owner | Status |
|---|------|------------|--------|-------|----------|------------|-------|--------|
| R15 | AdSense revenue volatility (seasonality, RPM drops) | 3 | 3 | 9 | Financial | • Diversified revenue layers (affiliate, digital, sponsorship)<br>• 3-month expense runway in business account<br>• Don't rely on AdSense for living expenses | You | 🟡 Build reserves |
| R16 | Affiliate program termination / rate cuts | 3 | 3 | 9 | Financial | • Multiple partners per category<br>• Own digital products as primary<br>• Direct sponsorship relationships | You | 🟢 Diversified |
| R17 | Sponsorship payment defaults / net-60/90 terms | 2 | 3 | 6 | Financial | • Contract with 50% upfront for >₹50K<br>• Net-30 max for new sponsors<br>• Invoice immediately on delivery<br>• Track in Notion with follow-up dates | You | 🟢 Process defined |
| R18 | Tax compliance (GST, TDS, advance tax) | 2 | 4 | 8 | Legal | • CA consultation at ₹10L ARR<br>• Presumptive taxation (44AD) until ₹2Cr<br>• Quarterly advance tax payments<br>• Separate business bank account | You | 🟡 Hire CA at threshold |
| R19 | Key person risk (solo operator burnout) | 3 | 4 | 12 | Ops | • Document all SOPs in Notion<br>• Automate rendering/upload/alerting<br>• VA for comments/outreach at ₹15K/mo post-revenue<br>• Batch content: record 4 videos in 1 session | You | 🟡 Documentation in progress |

---

## Growth & Market Risks

| # | Risk | Likelihood | Impact | Score | Category | Mitigation | Owner | Status |
|---|------|------------|--------|-------|----------|------------|-------|--------|
| R20 | Niche saturation / algorithm change kills reach | 3 | 4 | 12 | Market | • Build email list (owned audience)<br>• Cross-platform presence (IG, TikTok, LinkedIn)<br>• Diversify topics within money-mindset<br>• Community (Discord) reduces platform dependency | You | 🟡 Start email list |
| R21 | Competitor copies format / out-produces | 3 | 3 | 9 | Market | • Visual style is code-defined (hard to copy exactly)<br>• Brand = "Ink Explainer" + narrator voice<br>• Speed: 3 long + 3 shorts/week is high volume<br>• Community loyalty > content commodity | You | 🟢 Moat building |
| R22 | Economic downturn reduces finance interest | 2 | 3 | 6 | Market | • Counter-cyclical: people need money help MORE<br>• Focus on basics (budgeting, emergency fund)<br>• Affiliate: essential tools (demat, banking) stay relevant | You | 🟢 Resilient niche |

---

## Compliance Checklist (YouTube + India)

### YouTube ToS Compliance
- [x] Original content (scripts, visuals, voice)
- [x] No spam, deceptive practices, or scams
- [x] No copyrighted material (music, footage, images)
- [x] AI disclosure in description: "Generated with AI assistance (visuals + voice). Scripts 100% original."
- [x] No misleading metadata (titles match content)
- [x] Made for Kids: FALSE (finance content)
- [x] Community Guidelines: No hate, harassment, dangerous acts

### India-Specific
- [x] ASCI guidelines: No unsubstantiated claims ("guaranteed returns")
- [x] SEBI: No stock recommendations, only education
- [x] RBI: No unauthorized payment aggregation
- [x] IT Act: Data protection for any collected emails
- [x] GST: Register at ₹20L, file quarterly
- [x] TDS: Deduct on contractor payments >₹30K/year

### Financial Advice Disclaimer (Add to EVERY description)
```
Disclaimer: This content is for educational purposes only and does not constitute financial advice. Consult a SEBI-registered investment advisor before making financial decisions. Past performance does not guarantee future results. Some links are affiliates — I earn a commission at no extra cost to you.
```

---

## Incident Response Plan

### Severity 1: Channel at Risk (Termination, Demonetization, 3 Strikes)
1. **Immediate:** Stop all uploads, assess strike/claim
2. **1 hour:** File counter-notification if false claim
3. **4 hours:** Legal consultation if needed
4. **24 hours:** Public statement if public-facing issue
5. **Post-mortem:** Root cause, process fix, document

### Severity 2: Pipeline Broken (No Uploads for 48h)
1. **Immediate:** Check GitHub Actions logs, alerts
2. **1 hour:** Identify root cause (API, TTS, render, quota)
3. **4 hours:** Fix + test locally + push
4. **24 hours:** Verify 2 successful runs
5. **Post-mortem:** Update runbook, improve monitoring

### Severity 3: Revenue Drop > 50% MoM
1. **Week 1:** Analyze traffic sources, RPM, CTR, AVD
2. **Week 2:** A/B test thumbnails, titles, topics
3. **Week 3:** Launch recovery content (high-CTR formats)
4. **Month 1:** Review monetization mix, add layer

---

## Risk Monitoring Dashboard (Notion)

| Risk ID | Current Status | Last Review | Next Review | Owner | Notes |
|---------|----------------|-------------|-------------|-------|-------|
| R1 | 🟢 Controlled | 2026-09-19 | 2026-10-19 | You | Quota tracking live |
| R2 | 🟡 Action needed | 2026-09-19 | 2026-09-26 | You | Publish OAuth app |
| R3 | 🟢 Monitoring | 2026-09-19 | 2026-12-19 | You | |
| R4 | 🟢 Compliant | 2026-09-19 | 2026-12-19 | You | |
| R5 | 🟢 Compliant | 2026-09-19 | 2026-12-19 | You | |
| R6 | 🟡 Pending | 2026-09-19 | 2026-09-26 | You | Add AI disclosure |
| R10 | 🟢 Implemented | 2026-09-19 | 2026-10-19 | You | |
| R12 | 🟢 Implemented | 2026-09-19 | 2026-10-19 | You | |
| R15 | 🟡 Building | 2026-09-19 | 2026-10-19 | You | Diversify revenue |
| R19 | 🟡 In progress | 2026-09-19 | 2026-10-19 | You | Document SOPs |

---

## Quick Wins (Reduce Top 5 Risks This Week)

| Risk | Action | Time | Done? |
|------|--------|------|-------|
| R2 | Publish OAuth app to Production in Google Cloud Console | 15 min | 🔲 |
| R6 | Add AI disclosure to all video descriptions (bulk edit via YT Studio) | 30 min | 🔲 |
| R1 | Apply for YouTube API quota increase (form at 5K subs, prep now) | 20 min | 🔲 |
| R10 | Test manual `workflow_dispatch` re-run with `--force` | 10 min | 🔲 |
| R19 | Write 3 SOPs: render, upload, thumbnail A/B | 2 hours | 🔲 |

---

## Risk Appetite Statement

> WealthInk accepts **technical/operational risk** (pipeline failures, quota limits) because they are controllable with engineering.
> 
> WealthInk **minimizes platform/policy risk** (ToS, copyright, AI labeling) because they are existential and uncontrollable.
> 
> WealthInk **diversifies financial risk** (single revenue source) because sustainability requires multiple layers.
> 
> WealthInk **invests in key-person risk reduction** (documentation, automation, future VA) because solo operator is the biggest bottleneck.