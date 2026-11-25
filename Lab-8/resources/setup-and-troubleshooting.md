# Lab 8 · setup and troubleshooting

## If your team is behind: the catch-up list

Lab 8 needs one thing from earlier labs: a function that calls a model. If you do not have one that works today:

1. `pip install openai` and put `OPENROUTER_API_KEY` in your environment (your team's provisioned key; never in a committed file).
2. Copy `templates/one_call.py` to `src/one_call.py`.
3. In a Python shell: `from src.one_call import one_call; one_call([{"role": "user", "content": "hello"}], [], timeout=12, model="google/gemini-3.8-flash")`. A dict with `content` means you are ready for Step 1.

After today, finish earlier labs in order. Each one's README ends with a table of what your repo should contain: Lab 5 (one validated tool and `call_tool()`), Lab 6 (streaming and a store with deletion), Lab 7 (the loop and its gate test). Ask in your lab or on Teams which step you are on; say the step number.

## Errors you may meet

| What you see | What it means | What to do |
|---|---|---|
| `ModuleNotFoundError: No module named 'src.one_call'` | ADAPT 0 not done | copy `templates/one_call.py` to `src/one_call.py`, or point the import at your Lab 5 call |
| `TypeError: ... got an unexpected keyword argument 'model'` | your Lab 5 call does not accept `model` and `timeout` yet | add both, as in the Week 8 lines of `examples/campuspulse-router/src/llm.py`, or use `one_call.py` |
| `KeyError: 'OPENROUTER_API_KEY'` | the key is not in this shell | export it in the shell you run Python from |
| a 401 raised out of `complete()` | wrong or missing key. The router is right to raise it | fix the key; do not add 401 to `temporary()` |
| a 400 or 404 raised out of `complete()` | a model name is misspelt or the request is malformed | check each string in `CHAINS` against the model's page on OpenRouter |
| every request answered by `place: 2` | model 1 fails every time | read the `why` on the `failed` lines in `logs/router.jsonl` |
| `IndexError` in `tests/test_router.py` at `SECOND` | your chain has one model | add a second model from another company |
| the second identical call is not `cache` | something in your messages changes each time, or `CACHE_TTL_S` is 0 | print the messages twice and compare; look for a time or an id |
| `summary()` numbers look too big | it counts the whole log file | delete `logs/router.jsonl` before a measured run |
| `python -m evals.measure` says "ADAPT first" | fewer than 10 questions | put 10 real questions in `QUESTIONS` |
| tests pass locally, fail in CI | CI has no `logs/` folder or no key | the three lab tests need neither; check you did not import a module that reads the key at import time |

## Running the reference

```
cd Lab-8/examples/campuspulse-router
pip install -r requirements.txt
export CAMPUSPULSE_OFFLINE=1
pytest -q                                  # 152 passed: 145 from Weeks 4 to 7, 7 new
python -m demo.router_demo before
python -m demo.router_demo after
python -m demo.router_demo dark
python -m demo.router_demo bug
```

The Week 7 demos in the same folder still need `CAMPUSPULSE_TODAY=2026-11-18`, because their seeded events are dated; the Week 8 demos do not.
