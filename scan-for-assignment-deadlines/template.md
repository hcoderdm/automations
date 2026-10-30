# Scan for Assignment Deadlines: response templates

Every response follows one of these templates. Lines in `<!-- -->` are instructions and are never output. Text in `<angle brackets>` gets filled in. Everything else is output exactly as written.

Formats used in every template:

- Datetime header: `**<EEEE, MMMM d, h:mm a z>**`, e.g. **Friday, September 4, 4:10 AM EDT**
- Date: `ddd MM-DD`, e.g. Fri 09-04, with the weekday checked against the calendar
- Time: 12-hour clock, e.g. 6:00 PM
- IDs: whole numbers counting up from 0
- Names, titles and locations: headline-style title case, with course codes as the course writes them, e.g. ABC 101
- Empty cells: `-`

A run's report starts with the datetime header. A reply in the same session doesn't. Only send a push notification when there's something to act on.

## Deadlines found

```markdown
**<EEEE, MMMM d, h:mm a z>**

<One-sentence overview of the next two weeks of coursework, counting deadlines already on the calendar too, e.g. which days are heaviest.>

| ID | Status | Course | Assignment | Type | Due | Time | Submit | Notes | Source |
|---|---|---|---|---|---|---|---|---|---|
| <id> | <status> | <course> | <assignment> | <type> | <due> | <time> | <submit> | <notes> | <source> |
<!-- One row per deadline, sorted by due date and time, soonest first. One table only, with no headings above it. Deadlines already on the calendar with the right date and time are left out entirely.
ID: 0, 1, 2, ...
Status: New or Changed
Type: Problem Set, Paper, Quiz, Exam, Project, Reading Response, Lab or Other
Due: date
Time: time, or - if the email doesn't say
Submit: Canvas, Gradescope, In Class, Email, or -
Notes: subjectless fragment. For Changed rows, always what the calendar says now, e.g. On your calendar for Wed 10-29 11:59 PM. Otherwise things like Due time not stated, or Course not on your calendar, or -
Source: [<email subject>](https://mail.google.com/mail/u/0/#all/<message-id>) -->

Reply with the IDs you want and I'll add or move exactly those on your calendar.

<!-- Send a push notification: one line, under 200 characters, naming the soonest one, e.g. "3 deadlines to add. Soonest: ABC 101 Problem Set 6, Fri 10-31 5:00 PM." Mention any Changed rows, e.g. "XYZ 200 Final Project moved to Mon 12-08." -->
<!-- Stop here. -->
```

## Nothing new

```markdown
**<EEEE, MMMM d, h:mm a z>**

<One-sentence overview of the next two weeks of coursework.>

<!-- Output exactly one of these two lines. -->
Every deadline I found is already on your calendar.
I didn't find any deadlines in the last 7 days of email.

<!-- No push notification. Stop here. -->
```

## Deadlines added

```markdown
Updated your calendar:

| ID | Change | Course | Assignment | Due | Time |
|---|---|---|---|---|---|
| <id> | <change> | <course> | <assignment> | <due> | <time> |
<!-- One row per approved deadline, using the IDs from the report.
Change: Added, or Moved from <date> <time>, e.g. Moved from Wed 10-29 11:59 PM
Due, Time: the event as it is now, with - in Time for an all-day event -->
```
