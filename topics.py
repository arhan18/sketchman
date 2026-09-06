"""Topic queue: money-mindset themes in the reference channel's lane.
Original scripts only — no copied titles, no copied lines.
Style: Ink Explainer formula — second-person cold open, wrong-guess,
flip, walkthrough, diary-line closer. Short sentences for TTS pauses.
Each beat: {text (voiceover), scene (figures key), cap (on-screen caption)}."""

LONG_TOPICS = [
    {"title": "Why Poor People Stay Poor (And Don't Know It)",
     "beats": [
         ("This morning, your salary hit your account. By tonight, most of it was already gone. Not to bills. To decisions you don't even remember making.", "grind", "Where did it go?"),
         ("Your brain already has an answer. I just don't earn enough. That's what everyone believes. For years, that was the official story.", "trap", "The official story"),
         ("Now look at two people. Same salary. Same city. Ravi and Aman. Ten years later, one has nothing. The other stopped worrying long ago. What split them?", "think", "Same salary. Split lives."),
         ("Aman did one boring thing. The day salary came, ten percent left first. Before rent. Before food. He paid himself like a bill.", "money", "Pay yourself first"),
         ("Ravi laughed at the small amount. But small money, left alone, does something magical. It compounds while you sleep.", "chart_up", "Small money compounds"),
         ("Five years later, Ravi still lives salary to salary. Aman's money works nights and weekends. Same income. Different owner.", "freedom", "Same income. Different owner."),
         ("Old mindset says look rich. New mindset says be free. They are opposite games. And you are already playing one of them.", "choice", "Look rich vs be free"),
         ("Ravi bought things to impress people he doesn't like. Aman bought back his own time. One receipt fades. The other pays forever.", "habit", "Buy back your time"),
         ("Start today. Not with lakhs. With whatever is in your pocket right now. Direction beats amount. Every single time.", "walk", "Start with pocket change"),
         ("Your bank statement is a diary. It remembers what your money did long after you forgot spending it. Slowly, then suddenly.", "intro", "Slowly, then suddenly"),
     ]},
    {"title": "The 1 Habit That Separates Rich From Broke",
     "beats": [
         ("Tonight, open your banking app. Look at last month. That shock you feel? That is the most expensive feeling in the world. And almost nobody looks.", "intro", "Look at last month"),
         ("Two friends. Same job. Same salary. Ten years later, one is free and one is stuck. Your first guess is luck. It wasn't luck.", "think", "Same start. Different end."),
         ("The stuck one tracked spending in his head. Which means he never tracked it at all. Mental accounting always lies to its owner.", "trap", "Mental accounting lies"),
         ("The free one wrote down every rupee. Boring? Yes. Powerful? More than any salary hike he ever got.", "habit", "Write every rupee"),
         ("Month one, he found three thousand leaking into food delivery. Month two, the leak closed. Awareness is the whole game.", "money", "Find the leak"),
         ("Saved money went straight into an index fund. Automatic. No willpower needed after setup. You cannot fix a leak you refuse to see.", "chart_up", "Automate investing"),
         ("His friend got two raises in ten years and has nothing to show. Raises feed lifestyle, not freedom. The data says the same everywhere.", "chart_down", "Raises feed lifestyle"),
         ("The habit takes nine minutes a day. Nine minutes between broke and free. That is the entire secret.", "clock", "Nine minutes a day"),
         ("Start tonight. Not tomorrow. Open the app. Look at the leak. That shock you feel is tuition, and it is cheap.", "walk", "Feel the shock"),
         ("One habit. Nine minutes. Ten years. It was never a secret. It was just boring enough that most people skipped it.", "freedom", "Never a secret"),
     ]},
    {"title": "Why Your Salary Is a Trap (And the Exit Door)",
     "beats": [
         ("Your salary arrives every month. Same date. Same amount. It feels safe. That safety is exactly what makes it a trap.", "trap", "Safety is the trap"),
         ("You trade thirty days for one payment. Miss one month of work, and the machine stops feeding you. Read that again.", "grind", "30 days for 1 payment"),
         ("Most people hear this and think the answer is quitting. It's not. The exit door is building one income your boss cannot switch off.", "think", "Build, don't quit"),
         ("A skill. A small product. A channel. Anything that earns while you sleep counts as one exit brick.", "money", "One exit brick"),
         ("Brick one took him six months of evenings. Brick two took three. Skills compound exactly like money does.", "chart_up", "Skills compound too"),
         ("His salary stayed the same. But his fear disappeared. That is what the second income buys first. Not luxury. Courage.", "freedom", "It buys courage first"),
         ("Never let one person control one hundred percent of your income. That is not a job. That is a leash with payslips.", "trap", "A job or a leash?"),
         ("Start with two hours after dinner. Not eight. Consistency beats intensity every single time. Boring wins.", "habit", "Two hours nightly"),
         ("In two years, his side income covered rent. In four, it covered the salary. Then he chose. The trap didn't open. He walked out.", "choice", "Then he chose"),
         ("The exit door was there all along. It was just hidden behind the television remote. Your evenings are the door.", "intro", "The door was always there"),
     ]},
]

SHORT_TOPICS = [
    {"title": "Rich vs Broke Morning",
     "beats": [
         ("Your alarm rings. You snooze three times, scroll the phone, rush out. Whose morning is that?", "grind", "Broke morning"),
         ("Now rewind. Wake early. Plan the day. Move the body. Same twenty-four hours. Different owner.", "habit", "Rich morning"),
         ("Nobody controls your salary today. Everybody controls their morning. That is the whole edge.", "choice", "Same 24 hours"),
         ("Win the morning, and the money follows. It always does. Slowly, then suddenly.", "freedom", "Win the morning"),
     ]},
    {"title": "The 10 Percent Rule",
     "beats": [
         ("Salary comes. Bills go. Nothing left. Sound familiar? That is not a math problem. It is an order problem.", "trap", "Nothing left?"),
         ("Flip the order. Save ten percent first. Spend the rest guilt-free. The person you pay first wins.", "think", "Save first"),
         ("Ten percent of little is little. Ten percent for years is freedom. Years beat amounts.", "chart_up", "Years beat amounts"),
         ("Pay yourself first. Everyone else can wait. Especially the version of you that wants new shoes.", "money", "You first"),
     ]},
    {"title": "Why Budgeting Fails (And the One Page Fix)",
     "beats": [
         ("You open a spreadsheet. Forty columns blink back. Your willpower dies at row three. Budgeting feels impossible.", "grind", "Forty columns"),
         ("That is the problem. Not discipline. Too many numbers at once. The brain quits.", "trap", "Too many numbers"),
         ("Now tear it up. One line. Income. Two lines. Expenses. Three lines total. Add a red bar when red.", "think", "Three lines, not forty"),
         ("The red bar is the whole trick. When it appears, pick one thing to cut. Then one thing only.", "money", "One cut"),
         ("A page this small fits in your pocket. A spreadsheet never did.", "intro", "One page beats forty"),
     ]},
    {"title": "The Compound Path (Or Why Slow Wins the Race)",
     "beats": [
         ("Your friend jumps into a hot stock. Up thirty percent in a month. You check your index fund. Zero.", "trap", "Up thirty, down zero"),
         ("Three months later, his stock is down forty percent. Your zero is still zero. That is the edge.", "chart_down", "His edge reversed"),
         ("Money that stays the course grows quietly. A percent today. A percent tomorrow. A hundred years later.", "think", "Stay the course"),
         ("Math punishes the fast. It rewards the stubborn. The fastest path is the slowest one.", "chart_up", "Slow is fast"),
         ("Your friend needs a home run every month. You need one decision, held for years.", "freedom", "One decision"),
     ]},
    {"title": "The Subscription Audit That Saves Thousands",
     "beats": [
         ("Scroll your bank app. See those three-dollar charges? Streaming, apps, memberships you forgot you had.", "grind", "Forgotten three dollars"),
         ("Add them up. Eight subscriptions. Forty-seven dollars a month. Two years. That is a flight.", "money", "Forty-seven dollars"),
         ("Cancel three. Keep five. Same entertainment. Half the bill. Your future self just breathed.", "choice", "Cancel three"),
         ("Set one calendar reminder every quarter. Renewals hide in fine print and auto-renew defaults.", "habit", "Quarterly check"),
         ("The leak was not big. It was many. Fix the many, and the big leaks fix themselves.", "freedom", "Fix the many"),
      ]},
    {"title": "The Autopilot Account",
     "beats": [
          ("You check your balance once a month. Maybe. What happens in between? Money leaks out like air, silently.", "trap", "Silent leaks"),
          ("One friend checks daily. She sees every latte, every subscription. Painful. The other set one rule.", "think", "Set one rule"),
          ("Ten percent of every cheque lands in a separate account before she can name a thing. Automatic.", "money", "Auto-save first"),
          ("She forgot the account existed for six months. Then she logged in. That small thing had grown into a real cushion.", "chart_up", "Forgot it grew"),
          ("Willpower is finite. Automation is forever. Pick the rule, then never think about it again.", "habit", "Rule > willpower"),
     ]},
    {"title": "The Emergency Fund Gap",
     "beats": [
          ("Experts say six months. You say 'when I earn more'. But the gap is not your salary. It is your speed.", "grind", "Speed, not salary"),
          ("Someone saving five hundred a month with expenses at four hundred has an emergency fund in twelve weeks.", "think", "Speed wins"),
          ("Someone saving two thousand a month with expenses at two thousand-five has negative sixteen months of runway.", "chart_down", "Negative runway"),
          ("The emergency fund is not about size. It is about how fast it fills. Cut one thing that renews monthly.", "choice", "Cut one subscription"),
          ("Start at twenty, start at five thousand. The number you can keep up decides when you stop worrying.", "freedom", "Keep it up"),
     ]},
    {"title": "How Your Credit Card Really Works",
     "beats": [
          ("Swipe. Done. That is what you think. The card company sees the same swipe and starts a clock counting days.", "trap", "The 21-day lie"),
          ("Interest kicks in on day twenty-three if the full balance sits unpaid. Not a penny before. Not a penny after.", "think", "Day 23 matters"),
          ("But only if you paid the statement in full last month. Miss that, and the clock starts yesterday.", "money", "Always full"),
          ("Cash back feels free. It is not. One three-percent fee on unpaid days erases a year of points.", "chart_down", "Fee eats rewards"),
          ("Set one reminder: statement balance, full payment, every month. One habit, and the card works for you.", "habit", "One habit"),
     ]},
]

BEAT_WALK = ("grind",)  # fallback scene key alias


# --- deterministic rotation (stateless runner) ---
# GitHub Actions runners have no persistent filesystem, so state.json is
# lost every run. Pick the topic by (day_of_year % len) so we get a
# different long topic every day and never repeat within the rotation
# window. Override with --topic N when a specific beat is wanted.
def pick(fmt):
    import datetime as dt, topics
    pool = topics.LONG_TOPICS if fmt == "long" else topics.SHORT_TOPICS
    day = dt.date.today().toordinal()
    return day % len(pool)
