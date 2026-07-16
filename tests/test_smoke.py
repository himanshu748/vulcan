from pathlib import Path

from vulcan import tools


def test_read_file_blocks_escape(tmp_path: Path):
    assert "escapes" in tools.read_file(tmp_path, "../secrets.txt")


def test_run_cmd_allowlist(tmp_path: Path):
    assert "not in allowlist" in tools.run_cmd(tmp_path, "rm -rf /")


def test_write_and_read_roundtrip(tmp_path: Path):
    tools.write_file(tmp_path, "a/b.txt", "hello")
    assert "hello" in tools.read_file(tmp_path, "a/b.txt")


def test_grep(tmp_path: Path):
    (tmp_path / "x.py").write_text("needle = 1\n")
    assert "x.py:1" in tools.grep(tmp_path, "needle")
