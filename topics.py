"""Topic queue: money-mindset themes in the reference channel's lane.
Original scripts only — no copied titles, no copied lines.
Each beat: {text (voiceover), scene (figures key), cap (on-screen caption)}."""

LONG_TOPICS = [
    {"title": "Why Poor People Stay Poor (And Don't Know It)",
     "beats": [
         ("Meet Ravi. He works hard every single day. But every month ends the same way. Zero balance.", "grind", "Hard work isn't the problem"),
         ("Ravi thinks money is for spending. The moment salary comes, it goes. New phone. New clothes. Same trap.", "trap", "Money in = money out"),
         ("Now meet Aman. Same salary. Same city. But Aman pays himself first. Ten percent, every month, no excuse.", "think", "Pay yourself first"),
         ("Ravi laughs at Aman's small savings. But small money, left alone, does something magical. It compounds.", "money", "Small money compounds"),
         ("Five years later, Ravi still waits for salary day. Aman stopped waiting long ago. His money works while he sleeps.", "freedom", "Money that works for you"),
         ("The difference was never income. It was never luck. It was one habit, repeated quietly for years.", "habit", "One habit. Repeated."),
         ("Old money mindset says look rich. New money mindset says be free. They are opposite games.", "choice", "Look rich vs be free"),
         ("Ravi bought things to impress people he doesn't like. Aman bought back his own time.", "chart_up", "Buy back your time"),
         ("Start today. Not with lakhs. With whatever is in your pocket right now. Direction beats amount.", "walk", "Start with pocket change"),
         ("Adopt the old money mindset, and your life changes the same way Aman's did. Slowly, then suddenly.", "intro", "Slowly, then suddenly"),
     ]},
    {"title": "The 1 Habit That Separates Rich From Broke",
     "beats": [
         ("Two friends. Same job. Same salary. Ten years later, one is free and one is stuck. What happened?", "intro", "Same start. Different end."),
         ("The broke one tracked his spending in his head. Which means he never tracked it at all.", "think", "Mental accounting lies"),
         ("The rich one wrote down every rupee. Boring? Yes. Powerful? More than any salary hike.", "habit", "Write every rupee"),
         ("Awareness is the whole game. You cannot fix a leak you refuse to see.", "trap", "See the leak"),
         ("Month one, he found three thousand leaking into food delivery. Month two, the leak closed.", "money", "Find the leak"),
         ("Saved money went straight into an index fund. Automatic. No willpower needed after setup.", "chart_up", "Automate investing"),
         ("His friend got two raises in ten years and has nothing to show. Raises feed lifestyle, not freedom.", "chart_down", "Raises feed lifestyle"),
         ("The habit takes nine minutes a day. Nine minutes between broke and free.", "clock", "Nine minutes a day"),
         ("Start tonight. Open your banking app. Look at last month. That shock you feel is the tuition.", "think", "Feel the shock"),
         ("One habit. Nine minutes. Ten years. That is the entire secret, and it was never a secret.", "freedom", "Never a secret"),
     ]},
    {"title": "Why Your Salary Is a Trap (And the Exit Door)",
     "beats": [
         ("Salary feels safe. It arrives every month. That safety is exactly what makes it a trap.", "trap", "Safety is the trap"),
         ("You trade thirty days for one payment. Miss a month of work, and the machine stops feeding you.", "grind", "30 days for 1 payment"),
         ("The exit door is not quitting. It is building one income stream your boss cannot switch off.", "choice", "Build, don't quit"),
         ("A skill. A small product. A channel. Anything that earns while you sleep counts as an exit brick.", "think", "One exit brick"),
         ("Brick one took him six months of evenings. Brick two took three. Skills compound like money.", "chart_up", "Skills compound too"),
         ("His salary stayed the same job. But his fear disappeared. That is what the second income buys first.", "freedom", "It buys courage first"),
         ("Never let one person control one hundred percent of your income. That is not a job. That is a leash.", "trap", "A job or a leash?"),
         ("Start with two hours after dinner. Not eight. Consistency beats intensity every single time.", "habit", "Two hours nightly"),
         ("In two years, his side income covered rent. In four, it covered the salary. Then he chose.", "money", "Then he chose"),
         ("The trap had an exit door all along. It was just hidden behind the television remote.", "intro", "The door was always there"),
     ]},
]

SHORT_TOPICS = [
    {"title": "Rich vs Broke Morning",
     "beats": [
         ("Broke morning: snooze three times, scroll phone, rush out.", "grind", "Broke morning"),
         ("Rich morning: wake early, plan the day, move the body.", "habit", "Rich morning"),
         ("Same twenty-four hours. Different owner.", "choice", "Same 24 hours"),
         ("Win the morning, and the money follows.", "freedom", "Win the morning"),
     ]},
    {"title": "The 10 Percent Rule",
     "beats": [
         ("Salary comes. Bills go. Nothing left. Sound familiar?", "trap", "Nothing left?"),
         ("Flip it. Save ten percent first, spend the rest guilt-free.", "think", "Save first"),
         ("Ten percent of little is little. Ten percent for years is freedom.", "chart_up", "Years beat amounts"),
         ("Pay yourself first. Everyone else can wait.", "money", "You first"),
     ]},
    {"title": "Things Rich People Never Buy",
     "beats": [
         ("New car on loan to impress the neighbours? Never.", "chart_down", "Never for show"),
         ("Old rich buy assets. New poor buy liabilities with interest.", "choice", "Assets, not liabilities"),
         ("Every rupee is a soldier. Send it to work, not to war.", "money", "Rupees are soldiers"),
         ("Look broke. Be free. That is the whole game.", "freedom", "Look broke, be free"),
     ]},
]

BEAT_WALK = ("grind",)  # fallback scene key alias
