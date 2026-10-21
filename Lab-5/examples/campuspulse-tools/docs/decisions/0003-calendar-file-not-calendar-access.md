# 0003 · Give the student a calendar file, do not ask for calendar access

**Context.** Students want "add this to my calendar". The obvious build is Google Calendar or Outlook write access through OAuth, so the model can create the event directly.

**Decision.** `make_calendar_file` returns an `.ics` file. The student opens it and their own calendar app adds the event. CampusPulse never holds a token to anyone's calendar.

**Why.** Least privilege. A calendar write scope also lets a hijacked or confused model read, move or delete every event in that calendar. The file does the one thing the student asked for and nothing else. The tool stays read-only, so it is safe to offer to visitors who are not signed in.

**Alternatives.** OAuth calendar write (more convenient, far larger blast radius, a consent screen students will rightly hesitate at). A "subscribe to all club events" feed (useful later, still read-only).

**Consequences.** One extra tap for the student. No tokens to store, rotate or leak. Revisit only if students ask for automatic updates when an event moves; even then, a read-only subscription feed comes before write access.
