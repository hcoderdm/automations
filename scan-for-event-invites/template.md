# Scan for Event Invites: response templates

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

## Events found

```markdown
**<EEEE, MMMM d, h:mm a z>**

<One-sentence overview of the upcoming schedule, e.g. whether it's busy or has exams coming up.>

| ID | Score | Available | Organization | Event | Date | Start | End | RSVP | Deadline | Location | Description | Availability | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <id> | <score> | <available> | <organization> | <event> | <date> | <start> | <end> | <rsvp> | <deadline> | <location> | <description> | <availability> | <source> |
<!-- One row per event, sorted by score, highest first. One table only, with no headings above it and no split between new and previously seen events. Events already on the calendar are left out entirely.
ID: 0, 1, 2, ...
Score: 0.00 to 1.00, two decimals
Available: Yes if nothing on the calendar conflicts, otherwise No
Start, End: time, or - if the email doesn't say
RSVP: Yes if signing up, registering or buying a ticket is still needed, otherwise No
Deadline: date and optional time, e.g. Thu 09-03 5:00 PM, or -
Description: one complete sentence
Availability: subjectless fragment naming the conflict, e.g. Overlaps ABC 101 Section, or -
Source: [<email subject>](https://mail.google.com/mail/u/0/#all/<message-id>) -->

Reply with the IDs you want and I'll add exactly those to your calendar.

<!-- Add the "RSVPs still needed" section here if step 8 found any, with its IDs continuing after this table's. -->

<!-- Send a push notification: one line, under 200 characters, e.g. "4 events found. Top pick: Fall Kickoff Reception, Fri 09-04." If there are RSVPs still needed, add their count, e.g. "2 RSVPs still needed." -->
<!-- Stop here. -->
```

## Nothing to add

```markdown
**<EEEE, MMMM d, h:mm a z>**

<One-sentence overview of the upcoming schedule.>

<!-- Output exactly one of these two lines. -->
Every event I found is already on your calendar.
I didn't find any upcoming events in the last 7 days of email.

<!-- Add the "RSVPs still needed" section here if step 8 found any, with IDs starting at 0. -->

<!-- Send a push notification only if there are RSVPs still needed: one line, under 200 characters, naming the soonest deadline, e.g. "2 RSVPs still needed. Soonest: Fall Kickoff Reception by Thu 09-03 5:00 PM." Otherwise no push notification. Stop here. -->
```

## RSVPs still needed

This section is never a response on its own. It goes at the end of "Events found" or "Nothing to add" whenever step 8 finds events still waiting on an RSVP, and is left out entirely when there are none.

```markdown
### RSVPs still needed

These are on your calendar, but I couldn't find a confirmation in your inbox and you haven't told me you RSVPed.

| ID | Event | Date | Action | Link or Contact | Deadline | Notes |
|---|---|---|---|---|---|---|
| <id> | <event> | <date> | <action> | <link or contact> | <deadline> | <notes> |
<!-- One row per tracked event without proof of an RSVP, sorted by deadline, soonest first, with no-deadline rows last.
ID: keeps counting after the events found table, so every ID in the report is unique
Event: the title as it is on the calendar
Action: exactly what to do, e.g. Register at the link, Reply to the organizer, Buy a ticket, Fill out the form. If the deadline has passed, Deadline passed, check with the organizer
Link or Contact: the registration link or contact from the email, or the source email link if there's neither
Deadline: date and time, e.g. Thu 09-03 5:00 PM, or -
Notes: subjectless fragment, e.g. Possible confirmation in [<email subject>](<link>), or Added to your calendar by you, not by me, or - -->

If you've already RSVPed to any of these, tell me which and I'll mark them on your calendar.
```

## Events added

```markdown
Added to your calendar:

| ID | Event | Date | Start | End | Location |
|---|---|---|---|---|---|
| <id> | <event> | <date> | <start> | <end> | <location> |
<!-- One row per approved event, using the IDs from the report. -->

<!-- Only include the rest if at least one added event needs an RSVP or registration. Otherwise stop after the table and say nothing about RSVPs. -->
These still need an RSVP. Adding them to your calendar doesn't sign you up, and I never send email for you.

| ID | Event | Action | Link or Contact | Deadline |
|---|---|---|---|---|
| <id> | <event> | <action> | <link or contact> | <deadline> |
<!-- Action: exactly what to do, e.g. Register at the link, Reply to the organizer, Buy a ticket, Fill out the form
Link or Contact: the registration link or contact from the email, or -
Deadline: date and time, e.g. Thu 09-03 5:00 PM, or -
If the email doesn't make clear whether an RSVP is needed, put "Unclear, check the source email" in Action and the source email link in Link or Contact. -->
```

## RSVPs marked

```markdown
Marked as RSVPed on your calendar:

| ID | Event | Date |
|---|---|---|
| <id> | <event> | <date> |
<!-- One row per event they said they RSVPed to, using the IDs from the "RSVPs still needed" section, or - if they named an event that wasn't in it. -->
```
