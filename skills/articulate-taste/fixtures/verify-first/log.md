# History

## [2026-08-07] predict | skipped-tests
about: verified-or-it-does-not-go-out
result: hit

## [2026-08-07] predict | 2019-spreadsheet
about: unfollowable-is-unusable
result: hit

## [2026-08-07] predict | reviewer-byline
about: ignored-over-implicated
result: miss

## [2026-08-07] choice | error-text-names-the-check
won: naming which check failed · lost: naming the failure
axis: whether a failure message says which check did not pass, or only that
something did not pass. Two build logs, identical but for that. They picked the
one that named the check, and said the other one made them go and look.

Locates only. A single-axis pick confirms nothing and promotes nothing.

## [2026-08-07] choice | retry-count-in-summary
won: nothing · lost: nothing
axis: whether the run summary shows a retry count. They could not tell the two
apart, so the axis does nothing here and is retired rather than reground.
