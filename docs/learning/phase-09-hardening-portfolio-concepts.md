# Concepts — Phase 09

## Release engineering

### Definition

Release engineering creates a traceable, reproducible version of a system suitable for
delivery or demonstration.

### Why it exists

A Git branch can move; a release tag identifies a specific tested commit and its
evidence. It prevents portfolio documentation from drifting away from the code.

### Production considerations

Use semantic versions, immutable image tags, changelogs, signed artifacts, rollback
plans, and evidence from CI and runtime monitoring.

### Interview question

Why should a README distinguish implemented features from planned ones?

### Interview answer

Engineering credibility depends on reproducible claims. Clear limitations show that
the author understands operational risk and does not mistake configuration for proof.
