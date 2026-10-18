"""Non-exhaustive safety preflight for this curated public repository.

Does not replace human review or git-history inspection.
"""
from pathlib import Path
import re
import sys
import nbformat

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_EXTENSIONS = {'.jpg','.jpeg','.png','.dcm','.dicom','.keras','.h5','.hdf5','.npy','.npz','.pt','.pth','.onnx','.pkl','.joblib'}
FORBIDDEN_NAME = re.compile(r'(?:PRIVATE|per[_-]?image|split_manifest)', re.I)
ALLOWED_CONTENT_PATHS = ('notebooks/', 'src/', 'docs/', 'results/', 'tests/', 'data/', 'models/', 'scripts/', '.github/')


def check():
    problems=[]
    files=list(ROOT.rglob('*'))
    for path in files:
        if not path.is_file(): continue
        rel=path.relative_to(ROOT).as_posix()
        if '.git/' in rel or '__pycache__/' in rel or '.pytest_cache/' in rel:continue
        if path.suffix.lower() in FORBIDDEN_EXTENSIONS:
            problems.append(f'Forbidden data/model extension: {rel}')
        if FORBIDDEN_NAME.search(path.name):
            problems.append(f'Potential private file name: {rel}')
        if path.suffix=='.ipynb':
            try: notebook=nbformat.read(path,as_version=4)
            except Exception as e: problems.append(f'Unreadable notebook {rel}: {e}');continue
            for i,cell in enumerate(notebook.cells):
                if cell.get('attachments'):
                    problems.append(f'Embedded attachment in {rel}: cell {i}')
                if cell.cell_type=='code' and (cell.get('outputs') or cell.get('execution_count') is not None):
                    problems.append(f'Non-empty notebook outputs in {rel}: cell {i}')
    return problems

if __name__=='__main__':
    issues=check()
    if issues:
        print('\n'.join(issues));sys.exit(1)
    print('PASS: no known medical-image/checkpoint artifacts or notebook outputs detected. Human review still required.')
