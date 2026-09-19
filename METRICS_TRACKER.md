# Metrics Tracker: WealthInk Dashboard Schema

**Tools:** Google Sheets (primary) + Notion (project management) + Google Data Studio (visualization)

---

## 1. Daily Video Metrics (Google Sheets: "Daily_Videos")

| Column | Type | Description | Source |
|--------|------|-------------|--------|
| date | DATE | Upload date (YYYY-MM-DD) | Manual |
| video_id | TEXT | YouTube video ID (e.g., `dQw4w9WgXcQ`) | YT Studio |
| title | TEXT | Full video title | YT Studio |
| format | SELECT | `long` \| `short` | Known |
| topic_index | NUMBER | Index from topics.py | Known |
| topic_title | TEXT | Topic title from topics.py | Known |
| publish_time | DATETIME | Exact publish timestamp (IST) | YT Studio |
| views_24h | NUMBER | Views at 24 hours | YT API / Studio |
| views_7d | NUMBER | Views at 7 days | YT API / Studio |
| views_30d | NUMBER | Views at 30 days | YT API / Studio |
| ctr_24h | PERCENT | Click-through rate (impressions CTR) | YT Studio |
| ctr_7d | PERCENT | CTR at 7 days | YT Studio |
| avd_seconds | NUMBER | Average view duration (seconds) | YT Studio |
| avd_percent | PERCENT | Average percentage viewed | YT Studio |
| watch_hours_24h | NUMBER | Watch time hours at 24h | YT Studio |
| watch_hours_7d | NUMBER | Watch time hours at 7 days | YT Studio |
| watch_hours_30d | NUMBER | Watch time hours at 30 days | YT Studio |
| subs_gained_24h | NUMBER | Subscribers gained in 24h | YT Studio |
| subs_gained_7d | NUMBER | Subscribers gained in 7 days | YT Studio |
| rpm_7d | CURRENCY | Revenue per mille (7-day) | YT Studio |
| rpm_30d | CURRENCY | Revenue per mille (30-day) | YT Studio |
| estimated_revenue_30d | CURRENCY | Estimated revenue at 30 days | YT Studio |
| likes_24h | NUMBER | Likes at 24h | YT Studio |
| comments_24h | NUMBER | Comments at 24h | YT Studio |
| shares_24h | NUMBER | Shares at 24h | YT Studio |
| thumbnail_ctr_a | PERCENT | CTR for variant A (if A/B test) | Manual |
| thumbnail_ctr_b | PERCENT | CTR for variant B (if A/B test) | Manual |
| thumbnail_winner | SELECT | `A` \| `B` \| `none` | Manual |
| affiliate_clicks | NUMBER | Total affiliate link clicks | Bitly/Gumroad |
| affiliate_conversions | NUMBER | Affiliate conversions (signups) | Partner dashboard |
| affiliate_revenue | CURRENCY | Affiliate commission earned | Partner dashboard |
| digital_sales | NUMBER | Digital product units sold | Gumroad |
| digital_revenue | CURRENCY | Digital product revenue | Gumroad |
| sponsorship_revenue | CURRENCY | Sponsorship payment (if any) | Manual |
| notes | TEXT | Qualitative notes, anomalies | Manual |

---

## 2. Weekly Rollup (Google Sheets: "Weekly_Rollup")

| Column | Type | Formula / Source |
|--------|------|------------------|
| week_start | DATE | Monday date |
| week_end | DATE | Sunday date |
| videos_published | COUNT | COUNTIF format=long + COUNTIF format=short |
| total_views_7d | SUM | SUM of views_7d for week |
| total_watch_hours_7d | SUM | SUM of watch_hours_7d |
| avg_ctr_long | AVERAGE | AVERAGEIF format=long, ctr_7d |
| avg_ctr_short | AVERAGE | AVERAGEIF format=short, ctr_7d |
| avg_avd_long_sec | AVERAGE | AVERAGEIF format=long, avd_seconds |
| avg_avd_short_sec | AVERAGE | AVERAGEIF format=short, avd_seconds |
| subs_gained_week | SUM | SUM of subs_gained_7d |
| total_revenue_week | SUM | SUM of estimated_revenue_30d + affiliate_revenue + digital_revenue + sponsorship_revenue |
| revenue_per_video | DIVIDE | total_revenue_week / videos_published |
| cpm_estimate | DIVIDE | (total_revenue_week / total_views_7d) * 1000 |
| top_video_id | TEXT | Video ID with max views_7d |
| top_video_ctr | PERCENT | CTR of top video |
| notes | TEXT | Weekly insights, experiments run |

---

## 3. Monthly Cohort (Google Sheets: "Monthly_Cohort")

| Column | Type | Description |
|--------|------|-------------|
| month | TEXT | `2026-01` format |
| videos_published | NUMBER | Total videos that month |
| total_views | NUMBER | All views in month |
| total_watch_hours | NUMBER | All watch time in month |
| avg_ctr | PERCENT | Weighted average CTR |
| avg_avd_percent | PERCENT | Weighted average % viewed |
| subs_start | NUMBER | Subscribers at month start |
| subs_end | NUMBER | Subscribers at month end |
| subs_velocity | NUMBER | subs_end - subs_start |
| sub_velocity_pct | PERCENT | (subs_velocity / subs_start) * 100 |
| ypp_watch_hours_cumulative | NUMBER | Running total for YPP eligibility |
| ypp_subs_current | NUMBER | Current subscriber count |
| adsense_revenue | CURRENCY | AdSense earnings (paid) |
| affiliate_revenue | CURRENCY | Affiliate commissions (paid) |
| digital_revenue | CURRENCY | Digital product sales |
| sponsorship_revenue | CURRENCY | Sponsorship payments received |
| total_revenue | CURRENCY | SUM of all revenue |
| revenue_per_sub | DIVIDE | total_revenue / subs_end |
| cost_api | CURRENCY | API/tooling costs |
| cost_tools | CURRENCY | Software subscriptions |
| cost_contractors | CURRENCY | VA, editor, designer |
| net_profit | CURRENCY | total_revenue - total_costs |
| profit_margin | PERCENT | net_profit / total_revenue |

---

## 4. Channel Health Dashboard (Google Data Studio / Notion)

### Key Metrics Cards (Real-time via YT API)
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Subscriber Count | 1,000 (YPP) | < 100/mo growth |
| Total Watch Hours (365d) | 4,000 (YPP) | < 300/mo |
| Shorts Views (90d) | 10M (YPP Shorts) | < 500K/mo |
| Avg CTR (Long) | > 4% | < 2.5% |
| Avg CTR (Shorts) | > 8% | < 5% |
| Avg AVD (Long) | > 50% | < 35% |
| Avg AVD (Shorts) | > 80% | < 60% |
| RPM (Finance niche) | > $2 | < $1 |
| Revenue/Video (30d) | > ₹500 | < ₹100 |

### Charts to Build
1. **Sub Growth:** Line chart (daily) with 7-day MA
2. **View Velocity:** Bar chart (views per video, colored by format)
3. **CTR Trend:** Line chart (weekly avg CTR by format)
4. **AVD Distribution:** Histogram (percentage viewed buckets)
5. **Revenue Stack:** Stacked bar (AdSense, Affiliate, Digital, Sponsorship)
6. **Topic Performance:** Scatter (CTR vs AVD, sized by views, colored by topic)
7. **Quota Usage:** Line (daily quota used vs 10K limit)

---

## 5. Affiliate Tracker (Google Sheets: "Affiliate_Tracking")

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Click date |
| partner | TEXT | `zerodha` \| `groww` \| `amazon` \| etc. |
| video_id | TEXT | Source video |
| link_id | TEXT | Unique tracking ID (UTM) |
| clicks | NUMBER | Raw clicks |
| signups | NUMBER | Completed registrations |
| commission | CURRENCY | Earned commission |
| status | SELECT | `pending` \| `approved` \| `paid` \| `rejected` |
| payout_date | DATE | When commission hits bank |

**UTM Convention:** `?utm_source=youtube&utm_medium=video&utm_campaign={video_id}&utm_content={partner}`

---

## 6. Digital Product Tracker (Google Sheets: "Digital_Products")

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Sale date |
| product | TEXT | `9-min-habit-starter` \| `9-min-habit-pro` \| `salary-trap-workbook` |
| price | CURRENCY | Sale price (after fees) |
| source | TEXT | `youtube` \| `newsletter` \| `direct` \| `affiliate` |
| video_id | TEXT | Attribution video (if from YT) |
| customer_email | TEXT | For follow-up |
| refunded | BOOLEAN | Yes/No |
| net_revenue | CURRENCY | price - fees - refunds |

---

## 7. Sponsorship Pipeline (Notion Database: "Sponsorships")

| Property | Type | Options |
|----------|------|---------|
| Company | Title | — |
| Contact | TEXT | Name + email |
| Tier | SELECT | `Micro` \| `Small` \| `Mid` \| `Large` |
| Status | SELECT | `Prospect` \| `Outreach Sent` \| `Replied` \| `Negotiating` \| `Contracted` \| `Delivered` \| `Paid` \| `Lost` |
| Rate_Integrated | NUMBER | ₹ for integrated mention |
| Rate_Dedicated | NUMBER | ₹ for dedicated video |
| Video_ID | TEXT | Delivered video |
| Invoice_Sent | DATE | — |
| Payment_Received | DATE | — |
| Amount_Received | NUMBER | — |
| Next_Followup | DATE | — |
| Notes | TEXT | — |

---

## 8. Automation: Pulling Data via API

### YouTube Analytics API (Daily Sync)
```python
# Pseudocode for daily metrics pull
from googleapiclient.discovery import build

def pull_daily_metrics(video_id, date):
    yt = build('youtubeAnalytics', 'v2', credentials=creds)
    # Video-level metrics
    resp = yt.reports().query(
        ids='channel==MINE',
        startDate=date, endDate=date,
        metrics='views,estimatedMinutesWatched,averageViewDuration,'
                'subscribersGained,likes,comments,shares,'
                'estimatedRevenue,cpm,adImpressions,clickThroughRate',
        dimensions='video',
        filters=f'video=={video_id}'
    ).execute()
    return resp
```

### Google Apps Script (Sheets Automation)
- Trigger: Daily 6 AM IST
- Pull: Yesterday's metrics for all videos
- Append: To "Daily_Videos" sheet
- Calculate: Weekly/Monthly rollups via QUERY formulas

---

## 9. Notion Dashboard Structure

```
WealthInk Dashboard
├── 📊 Overview (Key Metrics Cards)
├── 📅 Content Calendar (Linked to CONTENT_CALENDAR_30D)
├── 🎬 Video Database (All videos + metrics)
├── 💰 Revenue Tracker (Linked to Sheets)
├── 🤝 Sponsorship Pipeline (Database)
├── 🔗 Affiliate Links (Database with UTMs)
├── 📦 Digital Products (Database + Gumroad sync)
├── ⚙️ Operations (SOPs, Checklists, Templates)
└── 📈 Experiments (A/B tests, learnings)
```

---

## 10. Alert Thresholds (Automated)

| Condition | Channel | Action |
|-----------|---------|--------|
| Daily quota > 8,000 units | Discord/Slack | ⚠️ Warning |
| Upload failed (any reason) | Discord/Slack/Email | 🔴 Critical |
| CTR < 2% on new video (24h) | Discord | 🟡 Investigate thumbnail |
| AVD < 30% on long video (24h) | Discord | 🟡 Investigate hook/retention |
| Sub growth < 50/week for 2 weeks | Email | 📉 Strategy review |
| Affiliate conversion = 0 for 7 days | Discord | 🟡 Check links |
| Digital sales = 0 for 14 days | Email | 📉 Funnel audit |

---

## 11. Quarterly Review Template (Notion Page)

**Q{X} 2026 Review — WealthInk**

### Scorecard
| Metric | Q Target | Actual | Status |
|--------|----------|--------|--------|
| Subscribers | | | 🟢/🟡/🔴 |
| Watch Hours | | | 🟢/🟡/🔴 |
| Total Revenue | | | 🟢/🟡/🔴 |
| Revenue/Video | | | 🟢/🟡/🔴 |
| Avg CTR (Long) | | | 🟢/🟡/🔴 |
| Avg CTR (Shorts) | | | 🟢/🟡/🔴 |

### Top 3 Wins
1.
2.
3.

### Top 3 Learnings
1.
2.
3.

### Next Quarter Focus
- Content:
- Monetization:
- Operations:
- Team:

### Budget Allocation (Next Quarter)
| Category | Amount | % of Revenue |
|----------|--------|--------------|
| Contractors | | |
| Tools/Software | | |
| Paid Promotion | | |
| Equipment | | |
| Buffer | | |