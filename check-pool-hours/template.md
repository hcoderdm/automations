# Check Pool Hours: response templates

Every response follows one of these templates. Lines in `<!-- -->` are instructions and are never output. Text in `<angle brackets>` gets filled in. Everything else is output exactly as written.

Formats used in every template:

- Datetime header: `**<EEEE, MMMM d, h:mm a z>**`, e.g. **Friday, September 4, 4:10 AM EDT**
- Date: `ddd MM-DD`, e.g. Fri 09-04, with the weekday checked against the calendar
- Time: 12-hour clock, e.g. 6:00 PM
- IDs: whole numbers counting up from 0
- Yes/No columns: exactly `Yes` or `No`
- Names, titles and locations: headline-style title case
- Empty cells: `-`

A run's report starts with the datetime header. A reply in the same session doesn't. Only send a push notification when there's something to act on.

## No swims

```markdown
**<EEEE, MMMM d, h:mm a z>**

No personal swims in the next 3 days, so there's nothing to check.

<!-- No push notification. Stop here. -->
```

## All swims open

```markdown
**<EEEE, MMMM d, h:mm a z>**

All <number> swims in the next 3 days fit the posted pool hours.

| Date | Start | End | Pool | Pool Hours | Open | Notes |
|---|---|---|---|---|---|---|
| <date> | <start> | <end> | <pool> | <pool hours> | <open> | <notes> |
<!-- One row per swim, in date order.
Pool: <your-pool> or <your-other-pool>
Pool Hours: that pool's posted hours for that date, e.g. 7:00 AM-7:00 PM
Open: Yes if the posted hours cover the whole swim and no closure note that matters overlaps it, otherwise No
Notes: subjectless fragment, e.g. No location on the event, assumed <your-pool>, or Might not be a swim, or a lane closure that overlaps, or -. Never mention closures of areas they don't use. -->

<!-- No push notification. Stop here. -->
```

## Swim at risk

```markdown
**<EEEE, MMMM d, h:mm a z>**

<number> of your <number> swims in the next 3 days may not fit the posted pool hours.

| Date | Start | End | Pool | Pool Hours | Open | Notes |
|---|---|---|---|---|---|---|
| <date> | <start> | <end> | <pool> | <pool hours> | <open> | <notes> |
<!-- One row per swim in the window, including the ones that are fine, in date order. Same columns as in All swims open. A date the posted table doesn't cover gets - in Pool Hours and No in Open. -->

### <date> <start> at <pool>

<Two or three sentences on what the posted hours say for that date and why this swim doesn't fit.>

| ID | Option | Pool | Start | End |
|---|---|---|---|---|
| <id> | <option> | <pool> | <start> | <end> |
<!-- One row per option the posted hours allow that day. Drop options the hours rule out, and add better ones the schedule suggests. Usual options:
Delay: same pool, at the earliest time it's open
Move: the other pool, at a time its hours allow
Evening: that pool's evening block, if it has one
Cancel: Pool, Start and End are -
Gym Instead: cancel the swim and put a dry-land or gym workout in the same slot, Pool is -
IDs keep counting across sections, so each option has its own ID.
Repeat this ### section for each swim that doesn't fit. -->

Reply with an ID and I'll update your calendar.

<!-- Send a push notification: one line, under 200 characters, naming the day, e.g. "Heads up: <your-pool> doesn't open until 9:00 AM Mon 09-14, so your 8:00 AM swim won't work. Open this run for options." -->
<!-- Stop here. -->
```

## Swim updated

```markdown
Updated on your calendar:

| ID | Change | Date | Start | End | Pool |
|---|---|---|---|---|---|
| <id> | <change> | <date> | <start> | <end> | <pool> |
<!-- One row for the option picked, using its ID from the report.
Change: subjectless fragment, e.g. Moved from 8:00 AM to 9:00 AM, or Moved to <your-other-pool>, or Cancelled, or Replaced with a gym workout
Date, Start, End, Pool: the event as it is now, or - where it was cancelled -->
```
