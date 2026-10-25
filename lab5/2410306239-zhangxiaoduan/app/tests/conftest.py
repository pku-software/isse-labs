"""让 pytest 能找到仓库根目录的 app.py（app.py 在仓库根目录，不在 tests/ 里）"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
