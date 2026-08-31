# History

Append-only. Newest last. One entry per event.

Actions: seed, choice, promote, demote, predict, recognise, tension, leak,
migrate.

`migrate` is a one-time binding for an imported non-empty `stable_baseline`,
not an ordinary promotion action. It records `schema:` and the baseline digest.

A `predict` or `recognise` entry carries `about:` with exactly one stable
principle slug, plus `result:`. Only a hit explicitly about the same principle
can promote it. Nothing else does.
