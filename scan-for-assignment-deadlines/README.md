# Scan for Assignment Deadlines

A Claude routine that searches the last 7 days of Gmail (Canvas, Gradescope, Ed and course emails) for coursework due in the next 30 days and checks it against my Google Calendar. It reports one table of deadlines that aren't on the calendar yet, plus ones whose date changed since I added them, with a link to each source email. Replying with IDs adds those deadlines to Google Calendar as "Due: <course> <assignment>" events or moves the changed ones.

It never sends email and doesn't touch the calendar until I reply.

It runs on claude.ai, not through launchd, so `install.sh` skips this folder. It's scheduled for `0 8 * * *` UTC, which is early morning in my timezone. It uses the Gmail and Google Calendar connectors.

The routine's prompt on claude.ai is [prompt.md](prompt.md) followed by [template.md](template.md), which has the formats for every response it sends. Editing them here doesn't change the routine, so make the change on claude.ai too. The copies have `<your-name>` and `<your-email>` in place of my name and address.
