# Public aggregate metrics only

- `final_test_metrics_public.json`: locked Stage 4 test/validation aggregates, no per-image data.
- `stability_multiseed_public.csv`: Stage 3F aggregate metrics for seeds 123, 456, 777, best-validation-loss and best-validation-accuracy checkpoints.

These numbers were transcribed from completed experiment outputs and do not include trained models, patient images, row-level predictions or private dataset fingerprints. Seed 42 is not included in the Stage 3F three-seed CSV; its earlier run is documented separately. All model selection was based on repeatedly examined validation data, not the one-time final test.
