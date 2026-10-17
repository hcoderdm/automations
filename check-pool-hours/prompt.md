It is early morning (about 4:00 AM in <your-timezone>). Look ahead at <your-name>'s personal swim sessions over the next 3 days and alert <your-name> only if a pool won't be open for one of them.

1. Get the current date and day of week in their timezone: `TZ=<your-timezone> date`.

2. Check <your-name>'s primary Google Calendar for events from now through the end of the third day (today, tomorrow, and the day after — in <your-timezone>).

   Identify their PERSONAL swim sessions. Do not rely on any one fixed event title — they may rename them. Treat an event as a personal swim if its title or location refers to swimming or a pool (e.g. "swim", "pool", "aquatics", "laps", "<your-pool>", "<your-other-pool>") and it is not a team event.

   EXCLUDE team events entirely: any event whose title contains "<your-team>" (e.g. "Practice | <your-team>", "Meet | <your-team>") is a team practice, meet, or social and is out of scope. Also exclude events that are clearly not pool sessions (team socials, banquets, elections, retreats, meetings).

   If a candidate is genuinely ambiguous, include it but say so in its Notes cell.

   - If there are no personal swim sessions in the next 3 days, STOP. Send no notification. Respond with the "No swims" template.

3. For each personal swim session found, note its date, start time, end time, and location (<your-pool> or <your-other-pool>). If a session has no location, check both pools and say which one you assumed in its Notes cell.

4. Fetch <your-pool-hours-url> and read the daily hours tables. The page lists one row per calendar date (e.g. "Wed 9/9") for a roughly two-week window, separately for <your-pool> and <your-other-pool>. Each row gives that pool's open hours plus notes about partial closures. Ask for the literal row text for the dates you need rather than a summary, and re-fetch with a narrower prompt if the answer is vague. Read both pools' rows for each relevant date, since the other pool may be the fallback. The page carries the disclaimer "ALL HOURS SUBJECT TO CHANGE" — the posted schedule is the best available signal, not a guarantee.

   IMPORTANT — ignore notes about parts of a facility <your-name> does not use, such as a separate small, teaching or diving pool. A note like "Small Pool CLOSED 12pm-1pm" is irrelevant: never treat it as a problem, never mention it in a notification, and never let it turn an otherwise-open day into an alert. Only each pool's overall posted open hours matter there. Lane-specific notes (e.g. "8 Lane CLOSED 12pm-1:15pm") do still matter — mention one if it overlaps a session at that pool.

5. Classify each session:
   - OPEN: the posted hours for that date fully cover the session window, and no closure note that actually affects <your-name> overlaps it (notes about areas they don't use do not count).
   - NOT OPEN / AT RISK: the pool opens later than the session starts, closes before it ends, is closed all day, has a relevant closure note overlapping the window, or that date is not present in the posted table (schedule not published that far out). Treat missing or unclear data as at-risk, never as open.

6. If EVERY session in the window is OPEN: send NO notification. Respond with the "All swims open" template.

7. If ANY session is NOT OPEN or AT RISK, respond with the "Swim at risk" template and send the push notification it describes. For each affected session, explain what the posted hours say and build the options from what that date's posted hours genuinely allow, with the concrete time and place in each row.

   If <your-name> replies with an ID in this session, make that change on their Google Calendar — edit ONLY that single occurrence of a recurring event, never the whole recurring series — and confirm with the "Swim updated" template.

Keep everything brief. Do not create any files. Never modify <your-team> events.

Format every response with the response templates at the end of this prompt.
