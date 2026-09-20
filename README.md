# planalyzer

**Critically analyze plans, PRDs, and proposals with a diversified [Jev](https://docs.typesafe.ai/) (TypeSafe System One) panel.**

One batched System One call. **Code** owns `pass` | `review` | `block`. Cheerleading is out of scope.

## Install skill

```bash
npx skills add austindixson/planalyzer --skill planalyzer
```

Claude Code plugin-style installs work the same pattern as other public skill repos when supported by your agent.

## CLI

```bash
export TYPESAFE_API_KEY=…   # required; JEV_API_KEY also accepted
python3 planalyze.py examples/sample_plan.md
python3 planalyze.py --context reality.md my_prd.md
python3 planalyze.py --json-only < plan.md
```

No third-party Python deps (stdlib only).

## Panel seats

| Seat | Primitive | Role |
|------|-----------|------|
| literalist | Noul | Near-term claims follow from context |
| skeptic | Noul | Invented capability / timeline |
| reward_hack | Noul | Impressive narrative without wedge value |
| scope | Noul | Sequenced vs boil-the-ocean |
| severity | Score | Cost of wrong branch |
| strategic_coherence | Score | North star ↔ wedge |
| execution_risk | Score | Committed-path load |
| product_fit | Score | Wedge fit |
| recommended_next_step | Choice | Advisory next move |

## Env

| Variable | Required |
|----------|----------|
| `TYPESAFE_API_KEY` | Yes (preferred) |
| `JEV_API_KEY` | Alternate |

Never commit keys.

## License

MIT
