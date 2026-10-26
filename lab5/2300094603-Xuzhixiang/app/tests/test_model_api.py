from unittest.mock import Mock


def test_model_reply_is_parsed_and_saved(app_module, monkeypatch):
    response = Mock(status_code=200, ok=True)
    response.json.return_value = {
        "choices": [{"message": {"content": "  模拟模型回复  "}}]
    }
    post_mock = Mock(return_value=response)
    monkeypatch.setattr(app_module.requests, "post", post_mock)

    with app_module.app.test_client() as client:
        created = client.post("/api/messages", json={"message": "你好"})
        assert created.status_code == 201
        record = created.get_json()
        assert record["message"] == "你好"
        assert record["reply"] == "模拟模型回复"
        assert client.get("/api/messages").get_json() == {"messages": [record]}

    post_mock.assert_called_once()
    args, kwargs = post_mock.call_args
    assert args == ("https://api.deepseek.com/chat/completions",)
    assert kwargs["json"]["messages"] == [{"role": "user", "content": "你好"}]
    assert kwargs["headers"]["Authorization"] == "Bearer lab5-test-placeholder"
    assert kwargs["timeout"] == 60


def test_model_timeout_does_not_create_record(app_module, monkeypatch):
    post_mock = Mock(side_effect=app_module.requests.Timeout("simulated timeout"))
    monkeypatch.setattr(app_module.requests, "post", post_mock)

    with app_module.app.test_client() as client:
        response = client.post("/api/messages", json={"message": "你好"})
        assert response.status_code == 502
        assert response.get_json() == {"error": "DeepSeek 请求超时，请稍后重试。"}
        assert client.get("/api/messages").get_json() == {"messages": []}

    post_mock.assert_called_once()
    assert not app_module.DATA_FILE.exists()
