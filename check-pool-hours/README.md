# Check Pool Hours

A Claude routine that looks at my personal swims on Google Calendar for the next 3 days and checks them against the posted [MAC and Blodgett pool hours](https://recreation.gocrimson.com/sports/2021/5/14/facility-hours.aspx). If every swim fits, it stays quiet. If a pool won't be open, it sends a push notification and lists options (delay, switch pools, swim in the evening, cancel), and replying with an option's ID updates that one calendar event.

Club Swim events are ignored, and so are MAC Small Pool closures.

It runs on claude.ai, not through launchd, so `install.sh` skips this folder. It's scheduled for `0 8 * * *` UTC, which is 4:00 AM Eastern in summer and 3:00 AM in winter. It uses the Gmail and Google Calendar connectors.

The routine's prompt on claude.ai is [prompt.md](prompt.md) followed by [template.md](template.md), which has the formats for every response it sends. Editing them here doesn't change the routine, so make the change on claude.ai too. The copies have `<your-name>` in place of my name.
