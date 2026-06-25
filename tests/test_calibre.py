"""Tests for Calibre integration."""

from unittest.mock import patch

from kinder.calibre import check_calibre_installed


def test_check_calibre_installed_when_present():
    with patch("kinder.calibre.shutil.which", return_value="/usr/bin/ebook-convert"):
        assert check_calibre_installed() is True


def test_check_calibre_installed_when_absent():
    with patch("kinder.calibre.shutil.which", return_value=None):
        assert check_calibre_installed() is False
