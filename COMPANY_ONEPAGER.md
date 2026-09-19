# Company One-Pager: **WealthInk**

---

## Mission
Demystify wealth-building for the everyday earner through bite-sized, visually distinct money-mindset explainers — automated, consistent, and free.

---

## Niche
**Financial literacy / money-mindset explainers**  
Whiteboard-style animated videos (long-form 16:9 + Shorts 9:16) that translate timeless wealth principles into actionable 5-10 minute lessons.

**Differentiator:** "Ink Explainer" visual language — hand-drawn aesthetic, second-person cold opens, contrarian flips, diary-line closers. Not generic finance content; a recognizable *style* viewers trust.

---

## Target Audience
| Primary | Secondary |
|---------|-----------|
| 22-35 yo urban professionals (India + diaspora) | Students, early-career, side-hustlers |
| ₹30K-1.5L/mo income | Aspiring investors, FIRE-curious |
| Consumes YouTube/Shorts/Reels daily | Prefers actionable over theoretical |

**Pain points:** Salary vanishes before month-end, "investing feels risky," no system for money, overwhelmed by jargon.

---

## Tone & Visual Identity
- **Tone:** Calm authority, slightly contrarian, zero fluff. "Your bank statement is a diary."
- **Visual:** Off-white paper texture, charcoal ink lines, gold accent ($/coins), 15 fps Ken Burns drift
- **Voice:** Male narrator (Kokoro `am_adam` @ 0.93x), deliberate pacing (~135 wpm), sentence-level subtitles
- **Thumb:** Dark bg (#0D0D12), gold bar, 4-word hook in DejaVu Bold, scene crop with white stroke

---

## Content Operations (Current)
- **Schedule:** 3 long (Mon/Wed/Fri) + 3 shorts (Tue/Thu/Sat) per week
- **Pipeline:** Topics → generate.py (PIL + ffmpeg) → voice.py (Kokoro → Edge TTS) → upload.py (YouTube API)
- **Automation:** GitHub Actions (daily 04:30 UTC), state persisted via git + Actions cache
- **Topics:** 3 long-form + 7 shorts in rotation (evergreen, reusable)

---

## Monetization Stack (Layered)

| Layer | Mechanism | Timeline | Target |
|-------|-----------|----------|--------|
| **1. AdSense (YPP)** | 1K subs + 4K watch hrs OR 10M Shorts views | Month 3-6 | ₹15-30K/mo |
| **2. Affiliate** | Finance tools (Zerodha, Groww, Cred), books, courses | Month 2+ | ₹10-25K/mo |
| **3. Digital Products** | Notion budget templates, compound calc sheets, 9-min habit tracker | Month 3+ | ₹20-50K/mo |
| **4. Sponsorships** | Fintech apps, finance books, course platforms | Month 6+ | ₹50K-2L+/deal |
| **5. Memberships** | Behind-the-scenes, early access, Discord, monthly Q&A | Month 9+ | ₹5-15K/mo |
| **6. Licensing** | TikTok/Reels repurposing, newsletter syndication | Month 4+ | Variable |

---

## Growth Engine
- **Cross-post:** YouTube → Shorts → Instagram Reels → TikTok (same assets, platform-native captions)
- **Community:** Pin comment with 1 action item, reply to every comment < 24h, weekly Discord thread
- **SEO:** Target "how to save money," "compound interest explained," "pay yourself first" — long-tail first
- **Collabs:** Guest on finance podcasts, swap Shorts with 5-10 similar-size channels
- **Paid:** Only after 10K subs organic; ₹5K test on YouTube Promotions for top-performing short

---

## Business Infrastructure
- **Legal:** Sole prop → OPC (India) at ₹10L ARR; YouTube ToS compliant (original scripts, AI-disclosed in description)
- **Finance:** Separate current account; expense buckets: API (~₹2K/mo), tools, contractors (VA ₹15K/mo post-revenue)
- **Team:** Solo operator. Keep automated: rendering, upload, scheduling. Outsource: comment moderation, outreach, thumbnail A/B tests
- **Metrics Dashboard:** Notion + Google Sheets (CTR, AVD, RPM, sub velocity, revenue/video, affiliate clicks)

---

## 90-Day Roadmap

| Weeks | Focus | Key Milestones |
|-------|-------|----------------|
| **1-2** | Fix automation, audit content, analytics setup | ✅ Pipeline green 7 days straight; GA4 + YT Studio linked |
| **3-6** | Relaunch consistent schedule, first 20 videos | 20 videos live; CTR > 4% (long), > 8% (shorts); 500 subs |
| **7-12** | Double down top performers, launch monetization | Affiliate links live; first digital product (Notion budget template); YPP application submitted |

---

## Quick Wins (Do This Week)
1. ✅ Fix GitHub Actions state persistence (cache key + force-with-lease)
2. ✅ Add quota guard (10K daily) + Discord/Slack alerts
3. ✅ Harden TTS fallback (Kokoro → Edge, 3 retries)
4. 🔲 Set up Discord webhook + test alert
5. 🔲 Add 3 affiliate links to video descriptions (Zerodha, Groww, 1 book)
6. 🔲 Create Notion budget template (lead magnet + paid version)
7. 🔲 Design thumbnail A/B test framework (hook text variant)

---

## Risk Register (Top 5)

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| YouTube API quota exhaustion | Medium | High | 1 upload/day guard; quota tracking in state.py; stagger across 2 API projects if needed |
| OAuth refresh token expiry (7-day Testing mode) | High | Critical | Publish OAuth app to Production; reauth.py one-click rotation; alert on invalid_grant |
| AI content policy change (disclosure/labeling) | Medium | High | "Generated with AI assistance" in description; keep scripts 100% original; monitor YT policy blog |
| Channel demonetization / limited ads | Low | High | No controversial topics; original visuals; fair-use only for public domain charts |
| TTS voice quality regression | Medium | Medium | Lock Kokoro model version; pin edge-tts version; local test before deploy |

---

**Next Action:** Deploy fixed workflow, verify 7-day green run, then activate affiliate layer.