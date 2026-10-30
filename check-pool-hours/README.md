# Check Pool Hours

A Claude routine that looks at my personal swims on Google Calendar for the next 3 days and checks them against the posted hours of two pools. If every swim fits, it stays quiet. If a pool won't be open, it sends a push notification and lists options (delay, switch pools, swim in the evening, cancel), and replying with an option's ID updates that one calendar event.

Team practices and meets are ignored, and so are closures of pool areas I don't use.

It runs on claude.ai, not through launchd, so `install.sh` skips this folder. It's scheduled for `0 8 * * *` UTC, which is early morning in my timezone. It uses the Gmail and Google Calendar connectors.

The routine's prompt on claude.ai is [prompt.md](prompt.md) followed by [template.md](template.md), which has the formats for every response it sends. Editing them here doesn't change the routine, so make the change on claude.ai too. The copies have placeholders like `<your-name>`, `<your-timezone>`, `<your-pool>`, `<your-other-pool>`, `<your-pool-hours-url>` and `<your-team>` in place of my details.
