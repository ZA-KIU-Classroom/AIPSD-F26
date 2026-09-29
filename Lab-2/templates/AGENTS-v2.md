# AGENTS.md · [Product name]
[One line: what this is and who it is for.] Spec: docs/spec.md

## Commands
install:  [exact command]
run:      [exact command]
test:     [exact command, and it must pass on a clean clone]

## Conventions
- [How the model is chosen: env variable name and default]
- [Where every model call goes, and what it logs]
- [Time, date, language, units: the rules a newcomer gets wrong]
- [Error shape]
- [What every new feature ships with]

## Always
- Run the test command before saying you are done, and paste the result

## Ask first
- Adding a dependency
- Changing a public response shape
- Editing CI configuration

## Never
- Read or write .env, or print a key
- Delete, skip, or weaken a test to make it pass
- [Your third line: what would hurt most at 2 a.m.?]

<!-- Keep it under about 40 lines. It is loaded into every agent session: every line costs budget every time. -->
