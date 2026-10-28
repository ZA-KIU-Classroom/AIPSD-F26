# <Product name> · State Contract

One row per thing your product remembers across turns. If it is not in this table, your product does not store it. Your `src/memory.py` (or equivalent) is the code version of this table; the two must agree, and your tests prove the scope, lifetime and deletion columns.

| What we remember | Why the product needs it | Scope: who can read it | Lifetime | Written when | Deleted by | Where it lives |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |

Rules for filling it in:

- **Scope** names a key: "this session", "this signed-in user (hashed id)", "this team". Never "everyone". If the honest answer is "everyone", it is not memory, it is content.
- **Lifetime** is a number with a unit, and your code enforces it. "Until the user deletes it" is only allowed for something the user explicitly asked you to keep.
- **Written when** says who triggered the write. "Automatically on every turn" is allowed for conversation turns only. Anything about the person (preferences, facts, interests) is written only when they ask.
- **Deleted by** must include a path the person can take themselves, without the model: an endpoint and a button. "Deleted" means rows removed, not a flag set.

## What we never store

List it. At minimum: raw identifiers (store a hash), audio or images after they were processed, anything the model inferred about the person that they did not state, and other people's data in anyone's prompt.

## How a person sees and controls it

- How they can see what you hold (an endpoint, a screen).
- What the reply says after a memory write (what was stored, how to delete it).
- What "forget me" does, exactly, and what it returns.

## What changes the contract

Any new row needs a decision record in `docs/decisions/` and tests for its scope, lifetime and deletion.
