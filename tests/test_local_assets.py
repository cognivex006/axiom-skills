"""The local collection cannot overwrite output or build uncommitted source."""

from unittest.mock import patch

import pytest

from release.build_local_assets import build


def test_existing_output_is_preserved(tmp_path):
    output = tmp_path / "human"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("preserve")
    with pytest.raises(ValueError, match="new output"):
        build(output, "a" * 40)
    assert sentinel.read_text() == "preserve"


def test_dirty_or_wrong_source_refuses_before_output(tmp_path):
    for head, dirty in (("a" * 40, b" M changed"), ("b" * 40, b"")):
        output = tmp_path / "output"
        with patch("release.build_local_assets.subprocess.check_output", side_effect=[head, dirty]):
            with pytest.raises(ValueError, match="exact clean"):
                build(output, "a" * 40)
        assert not output.exists()
