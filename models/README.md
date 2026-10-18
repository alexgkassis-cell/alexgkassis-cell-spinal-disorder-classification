# Checkpoints are private

The published aggregate results used the locked C08 reference CNN trained with seed 456 and selected by the maximum validation accuracy checkpoint. The weight archive is intentionally not shared.

Private Drive relative path:
`Spinal_Classification_Optimization/experiments/stage3/stability_v1/C08/seed_456/best_accuracy_model.keras`.

For authorized private local inference, copy that file outside the repository and pass its path to `python -m spinal_classifier.inference`. `.gitignore` blocks common model-weight extensions, but check `git status` before pushing and never force-add weights.
