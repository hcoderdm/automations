#!/bin/bash
LABEL="com.hcoderdm.coursework-autocommit"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/$LABEL.plist"
echo "Uninstalled."
