# Risk Register — WealthInk

## Risk Scoring Matrix
| Likelihood | Score | Impact | Score |
|------------|-------|--------|-------|
| Rare (<10%) | 1 | Insignificant | 1 |
| Unlikely (10-30%) | 2 | Minor | 2 |
| Possible (30-60%) | 3 | Moderate | 3 |
| Likely (60-90%) | 4 | Major | 4 |
| Almost Certain (>90%) | 5 | Critical | 5 |

**Risk Score = Likelihood × Impact**
- **Low (1-6):** Monitor, no immediate action
- **Medium (7-12):** Mitigate, assign owner
- **High (13-19):** Active management, contingency plan
- **Critical (20-25):** Immediate action, executive visibility

---

## Risk Register

| ID | Risk | Category | Likelihood | Impact | Score | Status | Owner | Mitigation | Contingency | Review |
|----|------|----------|------------|--------|-------|--------|-------|------------|-------------|--------|
| R1 | YouTube API quota exhausted (10K units/day) | Technical | 4 | 3 | **12** | 🟡 Active | Arhan | 1/day guard, quota tracking in state.py, multi-project staggering ready | Manual upload via YouTube Studio; request quota increase | Weekly |
| R2 | OAuth refresh token expires (invalid_grant) | Technical | 3 | 5 | **15** | 🔴 High | Arhan | Auto-verify step in workflow, reauth.py runbook, publish OAuth consent to Production | Emergency re-auth locally; backup refresh token in 1Password | Daily (verify step) |
| R3 | YouTube policy change on AI-generated content | Platform | 2 | 5 | **10** | 🟡 Monitor | Arhan | Disclosure in description ("AI-generated visuals & voice"), human review gate for scripts, original content only | Pivot to human-recorded voice + AI visuals; diversify to own platform | Monthly |
| R4 | Channel termination / strike | Platform | 1 | 5 | **5** | 🟢 Low | Arhan | Strict copyright compliance, fair use for concepts only, no copied scripts, backup channel created | Appeal process; migrate audience to backup + email list | Quarterly |
| R5 | TTS engine unavailable (Kokoro + Edge both fail) | Technical | 2 | 4 | **8** | 🟡 Active | Arhan | Dual-engine fallback, local model cache, probe detects phonemizer issues early | Use pre-recorded voice library; emergency manual recording | Per run |
| R6 | FFmpeg / PIL rendering failure | Technical | 2 | 3 | **6** | 🟢 Low | Arhan | System deps pinned in workflow, error logs uploaded as artifacts, structured logging | Debug locally from artifacts; fallback to simpler render | Per run |
| R7 | Thumbnail upload fails (unverified channel) | Technical | 3 | 2 | **6** | 🟢 Low | Arhan | Non-fatal in code, logged as warn, video still publishes | Verify channel ASAP; use auto-generated thumbnails | Per run |
| R8 | GitHub Actions state.json push race condition | Technical | 3 | 3 | **9** | 🟡 Active | Arhan | force-with-lease, cache fallback, in-memory fallback in state.py | Manual state recovery from cache; git history | Weekly |
| R9 | GitHub Actions runner failures (OOM, timeout) | Infrastructure | 2 | 3 | **6** | 🟢 Low | Arhan | 60-min timeout, ubuntu-latest (stable), minimal deps | Re-run workflow; increase runner size if needed | Monthly |
| R10 | Secrets leakage (API keys in logs) | Security | 1 | 5 | **5** | 🟢 Low | Arhan | No secrets in logs, structured logging filters, GitHub secret scanning | Rotate all secrets immediately; audit logs | Quarterly |
| R11 | Affiliate program termination / rate change | Business | 2 | 3 | **6** | 🟢 Low | Arhan | Diversify across 5+ programs, own digital products as hedge | Replace with alternative programs quickly | Quarterly |
| R12 | Sponsor demands creative control / non-disclosure | Business | 2 | 3 | **6** | 🟢 Low | Arhan | Contract template with editorial independence clause, FTC disclosure mandatory | Decline deals that compromise integrity | Per deal |
| R13 | AdSense account banned / invalid traffic | Platform | 1 | 5 | **5** | 🟢 Low | Arhan | No click fraud, no view bots, organic growth only, monitor invalid traffic report | Appeal; diversify revenue (affiliate, products) | Monthly |
| R14 | Key person dependency (solo operator) | Operational | 4 | 4 | **16** | 🔴 High | Arhan | Document all runbooks, automate 80%+, Notion SOPs, 1Password emergency access | Designated backup operator with access | Monthly |
| R15 | Burnout / inconsistent publishing | Operational | 3 | 4 | **12** | 🟡 Active | Arhan | Automated pipeline, batch content creation, 1 day/week maintenance | Pre-recorded buffer (2 weeks); reduce to 2 long/week | Weekly |
| R16 | Algorithm change kills reach | Platform | 3 | 4 | **12** | 🟡 Monitor | Arhan | Multi-platform (TikTok, Reels, LinkedIn), email list, SEO titles, community building | Pivot content strategy based on data | Monthly |
| R17 | Copyright claim on music/sound effects | Legal | 2 | 3 | **6** | 🟢 Low | Arhan | No background music (voice only), all art generated, CC0 fonts only | Dispute with evidence; replace audio track | Per claim |
| R18 | Financial advice liability (viewers lose money) | Legal | 2 | 4 | **8** | 🟡 Active | Arhan | Disclaimer in every description ("Not financial advice"), educational framing, no specific buy/sell | Legal review of disclaimer; insurance if scaling | Quarterly |
| R19 | Data loss (Notion, GitHub, local) | Operational | 1 | 4 | **4** | 🟢 Low | Arhan | GitHub repo = source of truth, Notion export weekly, local backups | Restore from Git + Notion export | Monthly |
| R20 | Competitor copies format / topics | Business | 3 | 2 | **6** | 🟢 Low | Arhan | Build brand moat (voice, style, community), consistent schedule, email list | Double down on unique personality; legal if direct copy | Quarterly |

---

## High-Priority Risks (Score ≥ 12) — Deep Dive

### R2: OAuth Refresh Token Expiration (Score: 15)
**Root Cause:** Google OAuth consent screen in "Testing" mode → refresh tokens expire ~7 days.
**Current State:** Workflow has verify step that catches this early. reauth.py exists.
**Gap:** No automated alert before expiry. Manual re-auth required.
**Action Items:**
1. [ ] Publish OAuth consent to Production (one-time, requires domain verification)
2. [ ] Add scheduled workflow to verify token weekly (separate from daily)
3. [ ] Store backup refresh token in 1Password with emergency access
4. [ ] Document 15-min re-auth runbook for backup operator

### R14: Key Person Dependency (Score: 16)
**Root Cause:** Solo operator knows all systems, no bus factor.
**Current State:** Code is documented, but operational knowledge is tribal.
**Action Items:**
1. [ ] Create `OPERATIONS.md` with: credentials locations, runbook for each failure mode, contact list
2. [ ] Grant 1Password emergency access to trusted person
3. [ ] Record 30-min Loom walkthrough of pipeline
4. [ ] Test "disaster recovery" quarterly (simulate Arhan unavailable)

### R1: API Quota Exhaustion (Score: 12)
**Root Cause:** 1600 units/upload + 1 verify = 1601/day. Default 10K allows 6/day. Current 1/day guard is safe but limits growth.
**Current State:** Quota tracking in state.py, can_upload() check, 1/day guard.
**Action Items:**
1. [ ] Request quota increase to 50K/day (form + 2-week wait)
2. [ ] Implement multi-project staggering (2-3 GCP projects)
3. [ ] Add quota dashboard in Notion (daily remaining)
4. [ ] Optimize: batch verify + upload in single API call where possible

### R15: Burnout / Inconsistent Publishing (Score: 12)
**Root Cause:** Solo operator, daily grind, no buffer.
**Current State:** Automated pipeline reduces daily work to ~30 min monitoring.
**Action Items:**
1. [ ] Build 2-week content buffer (pre-render 12 videos)
2. [ ] "Maintenance Monday" — 1 hr/week for pipeline health
3. [ ] Reduce to 2 long + 2 short/week if needed (still 4/week)
4. [ ] Hire VA for comment management (Month 4+, ₹5K/mo)

### R16: Algorithm Change (Score: 12)
**Root Cause:** YouTube algorithm opaque, Shorts/Longs priority shifts.
**Current State:** Multi-platform repurposing planned.
**Action Items:**
1. [ ] Build email list from Day 1 (ConvertKit free tier)
2. [ ] Repurpose to TikTok/Reels/LinkedIn (Layer 6)
3. [ ] SEO-optimized titles/descriptions (not just clickbait)
4. [ ] Community: Discord + weekly newsletter = owned audience

---

## Compliance Checklist

| Requirement | Status | Evidence |
|-------------|--------|----------|
| AI content disclosure (YouTube policy) | ✅ | "AI-generated visuals & voice" in every description |
| Financial advice disclaimer | ✅ | "Not financial advice. Educational only." in every description |
| Affiliate disclosure (FTC/ASCII) | ✅ | "Affiliate links may earn commission" in description + pinned comment |
| Sponsorship disclosure | ⏳ | Will add "Sponsored by @brand" + #ad in title/description |
| Copyright compliance (music, assets) | ✅ | No music, generated art, CC0 fonts |
| Data privacy (GDPR/India DPDP) | ⏳ | Privacy policy on landing page (when launched) |
| Terms of Service (YouTube) | ✅ | Automated upload via API (allowed), no spam, no manipulation |

---

## Incident Response Plan

### Severity 1: Channel Down / Termination
1. **Immediate:** Appeal via YouTube Studio
2. **Parallel:** Activate backup channel, email list broadcast
3. **Within 24h:** Redirect all links (Linktree, bio) to backup
4. **Post-mortem:** Root cause, policy fix, prevention

### Severity 2: Pipeline Broken > 2 Days
1. **Diagnose:** Check GitHub Actions logs, alerts
2. **Fix:** Apply patch, re-run failed workflow
3. **Buffer:** Use pre-rendered videos for manual upload
4. **Post-mortem:** Update runbook, improve monitoring

### Severity 3: Revenue Drop > 50% MoM
1. **Analyze:** Traffic sources, CTR, AVD, RPM trends
2. **Test:** Thumbnail A/B, title formats, publish times
3. **Diversify:** Accelerate next monetization layer
4. **Review:** Monthly strategy adjustment

---

## Risk Review Cadence

| Frequency | Activity | Participants |
|-----------|----------|--------------|
| **Daily** | Pipeline health (GitHub Actions + alerts) | Arhan (automated) |
| **Weekly** | Metrics review (Notion dashboard), top risks check | Arhan |
| **Monthly** | Full risk register review, update scores, compliance check | Arhan |
| **Quarterly** | Deep dive: key person test, legal review, budget review | Arhan + advisor |

---

## Risk Appetite Statement

> WealthInk accepts **technical risks** that can be automated away (quota, TTS, rendering) but has **zero tolerance** for:
> - Platform policy violations (AI disclosure, financial advice)
> - Security incidents (secrets leakage)
> - Legal liability (copyright, financial advice)
> - Single points of failure without documented recovery

We invest in **automation, documentation, and diversification** to keep the machine running with minimal human intervention.

---

*Register version: 1.0 | Created: 2026-09-19 | Next review: 2026-10-19 | Owner: Arhan Ahmad Khan*