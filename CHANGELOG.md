# Changes

## 2026-09-23 — Verification hardening and ChatGPT compatibility

Added opt-in strict metadata lookup exits, validated repository/API inputs, safe GitHub links, truthful license/freshness labels, and regression tests.

Both the README and skill entry point now cover Claude, ChatGPT and Codex. Added host-capability
fallbacks and OpenAI skill metadata. Fixed invalid original YAML descriptions. Existing Claude
installation remains supported. Documentation explains what the checks establish and what still
requires independent review; no live ChatGPT/Claude overnight run was claimed.

Validation used disposable repositories and mocked API responses, without owner data or credentials.
Exact gate output:

```text
$ /Applications/Xcode.app/Contents/Developer/usr/bin/python3 -m unittest discover -s tests -v
test_alias_full_url_resolves (test_helpers.Helpers) ... ok
test_empty_input_file_is_error (test_helpers.Helpers) ... ok
test_html_preserves_license_and_ignores_executable_urls (test_helpers.Helpers) ... ok
test_invalid_count_is_unverified_not_crash (test_helpers.Helpers) ... ok
test_malformed_api_payload_never_verified (test_helpers.Helpers) ... ok
test_realistic_metadata_and_unrecognized_license (test_helpers.Helpers) ... ok
test_slug_rejects_unrelated_urls_and_partial_matches (test_helpers.Helpers) ... ok
test_strict_returns_failure_but_preserves_json (test_helpers.Helpers) ... ok
test_unverified_consult_label_and_mixed_dates (test_helpers.Helpers) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.008s

OK
exit 0

$ /Users/idan/Orion/core-brain/.venv/bin/python3 /Users/idan/.codex/skills/.system/skill-creator/scripts/quick_validate.py /private/tmp/maestro-blindspot-review.uALgZO
Skill is valid!
exit 0

$ git diff --check
exit 0
```

Implementation commit: `979c6cb`. Recorded in this separate follow-up commit.
`git merge-base --is-ancestor 979c6cb HEAD`: exit 0.
