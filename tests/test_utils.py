import pytest
from pathlib import Path
from tool.utils import calculate_checksum, ensure_dir, format_size

def test_calculate_checksum(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world")
    
    checksum = calculate_checksum(file_path)
    assert isinstance(checksum, str)
    assert len(checksum) == 64 # SHA256 length

def test_ensure_dir(tmp_path):
    new_dir = tmp_path / "new_dir"
    ensure_dir(new_dir)
    assert new_dir.exists()
    assert new_dir.is_dir()

def test_format_size():
    assert format_size(100) == "100.00 B"
    assert format_size(1024) == "1.00 KB"
    assert format_size(1024 * 1024) == "1.00 MB"
    assert format_size(1024 * 1024 * 1024) == "1.00 GB"
    assert format_size(1024 * 1024 * 1024 * 1024) == "1.00 TB"
    assert format_size(1024 * 1024 * 1024 * 1024 * 1024) == "1.00 PB"
    assert format_size(1024 * 1024 * 1024 * 1024 * 1024 * 1024) == "1024.00 PB"
