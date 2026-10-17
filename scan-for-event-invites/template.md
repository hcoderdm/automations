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
Availability: subjectless fragment naming the conflict, e.g. Overlaps Stat 110 Section, or -
Source: [<email subject>](https://mail.google.com/mail/u/0/#all/<message-id>) -->

Reply with the IDs you want and I'll add exactly those to your calendar.

<!-- Send a push notification: one line, under 200 characters, e.g. "4 events found. Top pick: Fall Kickoff Reception, Fri 09-04." -->
<!-- Stop here. -->
```

## Nothing to add

```markdown
**<EEEE, MMMM d, h:mm a z>**

<One-sentence overview of the upcoming schedule.>

<!-- Output exactly one of these two lines. -->
Every event I found is already on your calendar.
I didn't find any upcoming events in the last 7 days of email.

<!-- No push notification. Stop here. -->
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
