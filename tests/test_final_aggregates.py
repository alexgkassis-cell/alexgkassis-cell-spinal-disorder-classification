from pathlib import Path
import json


def test_final_result_internally_consistent():
    repo = Path(__file__).parents[1]
    data = json.loads((repo / 'results/final_test_metrics_public.json').read_text())
    confusion = data['heldout_test']['confusion_matrix_rows_actual_cols_predicted']
    assert [sum(row) for row in confusion] == [11, 28, 12]
    assert sum(sum(row) for row in confusion) == 51
    correct = sum(confusion[i][i] for i in range(3))
    assert correct == 47 == data['heldout_test']['correct']
    assert abs(data['heldout_test']['accuracy'] - correct / 51) < 1e-12
    assert data['validation']['correct'] == 50
    assert data['validation']['n'] == 52
    assert data['dataset_counts']['train'] + data['dataset_counts']['validation'] + data['dataset_counts']['heldout_test'] == 338
