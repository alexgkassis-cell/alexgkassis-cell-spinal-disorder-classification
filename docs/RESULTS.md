# Locked model results

The final decision, made **before any test image was decoded**, was the Stage 3F C08 seed-456 reference CNN, maximum validation accuracy checkpoint (lower validation loss breaks ties), epoch 11. Input: grayscale 128×128 plus CLAHE clipLimit 3.0 with an 8×8 tile grid.

## Model selection versus final evaluation

| Metric | Validation | Final test |
|---|---:|---:|
| Images | 52 | 51 |
| Correct | 50 | 47 |
| Accuracy | 0.961538 | 0.921569 |
| Macro F1 | 0.95283 | 0.9152 |
| Balanced accuracy | 0.960317 | 0.915584 |
| Test cross-entropy | n/a | 0.2189 |

The **best-validation-accuracy** epoch was 11; its validation cross-entropy was approximately 0.4027. The final test was performed only once. Test accuracy had a descriptive Wilson 95% interval of 0.8150–0.9691. Do not re-run test model comparisons on the same 51 images.

## Held-out test confusion matrix

Order = Normal, Scoliosis, Spondylolisthesis. Rows = actual, columns = predicted.

```text
[[ 9,  2,  0],
 [ 1, 26,  1],
 [ 0,  0, 12]]
```

- Normal: recall 9/11 = 0.8182, precision 9/10 = 0.9000, F1 0.8571.
- Scoliosis: recall 26/28 = 0.9286, precision 26/28 = 0.9286, F1 0.9286.
- Spondylolisthesis: recall 12/12 = 1.0000, precision 12/13 = 0.9231, F1 0.9600.

Aggregate public machine-readable file: [`../results/final_test_metrics_public.json`](../results/final_test_metrics_public.json). Full detailed private logs and image-level records are intentionally excluded.

## Interpretation

Test accuracy (92.16%) is **3.99 percentage points lower** than the selected validation accuracy (96.15%). This should be presented prominently, not hidden. Small sample sizes make apparent changes of one or two cases disproportionately important. An observed 100% recall on just 12 test Spondylolisthesis images does not guarantee that performance in larger or external cohorts.

Repeated architecture, preprocessing, epoch and seed selection on the same 52 validation cases makes that validation accuracy optimistic. There is **no proven patient-disjoint or external validation**, and the X-ray collection may encode source-specific color or acquisition shortcuts. No clinical claims are justified.
