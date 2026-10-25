import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# 在导入 app 之前，先把数据目录指向临时目录，避免污染仓库的 data/。
os.environ["LAB5_DATA_DIR"] = tempfile.mkdtemp(prefix="lab5-tests-")

import pytest  # noqa: E402
import app  # noqa: E402


@pytest.fixture()
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(app, "DATA_FILE", str(tmp_path / "conversations.json"))
    monkeypatch.setattr(app, "OLD_DATA_FILE", str(tmp_path / "messages.json"))
    app.load_data()
    app.app.config.update(TESTING=True)
    with app.app.test_client() as test_client:
        yield test_client