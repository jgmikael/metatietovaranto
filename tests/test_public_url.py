from apps.api.public_url import public_base_url


def test_local_url_default(monkeypatch):
    monkeypatch.delenv("PUBLIC_BASE_URL", raising=False)
    monkeypatch.delenv("CODESPACE_NAME", raising=False)
    assert public_base_url() == "http://localhost:8000"


def test_codespaces_forwarded_url(monkeypatch):
    monkeypatch.setenv("PUBLIC_BASE_URL", "http://localhost:8000")
    monkeypatch.setenv("CODESPACE_NAME", "synthetic-demo-name")
    monkeypatch.setenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
    assert public_base_url() == "https://synthetic-demo-name-8000.app.github.dev"


def test_explicit_url_wins(monkeypatch):
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://catalog.example.org/")
    monkeypatch.setenv("CODESPACE_NAME", "synthetic-demo-name")
    assert public_base_url() == "https://catalog.example.org"
