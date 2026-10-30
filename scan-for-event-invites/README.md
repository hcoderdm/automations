# Scan for Event Invites

A Claude routine that searches the last 7 days of Gmail for events in the next 30 days, drops any already on my calendar, and scores the rest by how likely I am to go based on my calendar history. It reports one table with conflicts, RSVP deadlines and a link to each source email. Replying with IDs adds those events to Google Calendar and reminds me which ones still need an RSVP.

Every run also lists events on my calendar that need an RSVP when there's no confirmation in my inbox and I haven't told it I RSVPed. Telling it I RSVPed marks the event's description with "RSVP done", so it stops listing that event.

It never sends email and doesn't touch the calendar until I reply.

It runs on claude.ai, not through launchd, so `install.sh` skips this folder. It's scheduled for `0 8 * * *` UTC, which is early morning in my timezone. It uses the Gmail and Google Calendar connectors.

The routine's prompt on claude.ai is [prompt.md](prompt.md) followed by [template.md](template.md), which has the formats for every response it sends. Editing them here doesn't change the routine, so make the change on claude.ai too. The copies have `<your-name>`, `<your-email>`, `<your-timezone>` and `<your-school>` in place of my name, address, timezone and school.
