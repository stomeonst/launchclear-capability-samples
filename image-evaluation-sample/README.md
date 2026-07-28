# Fictional Image Evaluation Sample

This sample demonstrates a compact, evidence based image evaluation workflow for an AI training or visual quality review task.

## Truth boundary

The dashboard image is a synthetic SVG created by LaunchClear. It contains no client data, customer account, production system, private image, credential, or real business result. No organization commissioned, reviewed, approved, sponsored, or endorsed this sample.

The defects are intentional. The purpose is to show how a reviewer can separate observable evidence from interpretation, assign consistent severity, and write an actionable correction.

## Files

1. [`assets/fictional-checkout-dashboard.svg`](assets/fictional-checkout-dashboard.svg) is the synthetic evaluation target.
2. [`annotations.json`](annotations.json) is the machine readable review record.
3. [`evaluation-report.md`](evaluation-report.md) is the human readable bilingual review.
4. [`tests/test_annotations.py`](tests/test_annotations.py) validates the annotation contract.

## Evaluation method

The reviewer checks five dimensions:

1. Data consistency
2. Visual alignment
3. Semantic encoding
4. Text legibility
5. Text completeness

Each finding includes one observable statement, one severity level, one bounded region, and one correction. The overall label is `needs_revision` because a critical reconciliation error and several major visual defects would make the dashboard unreliable for a business user.

## Reproduce the validation

```bash
python3 -m unittest discover -s image-evaluation-sample/tests -v
```

The validator checks the score range, required finding fields, unique finding identifiers, allowed severities, evidence quality, asset existence, synthetic data disclosure, and acceptance checks.

## Use boundary

This sample may be reviewed as current proof of structured image evaluation and written feedback. It must not be represented as paid client work, production QA, or a completed OpenTrain project.
