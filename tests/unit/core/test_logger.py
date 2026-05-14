# SPDX-License-Identifier: MIT
import logging

from pykeycloak.core.logger import SanitizingFilter
from pykeycloak.core.sanitizer import SensitiveDataSanitizer


class TestSanitizingFilter:
    def test_sanitizes_extra_content_and_message(self):
        sanitizer = SensitiveDataSanitizer()
        filt = SanitizingFilter(sanitizer=sanitizer)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="payload",
            args=(),
            exc_info=None,
        )
        record.content = {"access_token": "secret", "name": "n"}

        assert filt.filter(record) is True
        assert "<hidden>" in record.msg

    def test_sanitizes_args(self):
        sanitizer = SensitiveDataSanitizer()
        filt = SanitizingFilter(sanitizer=sanitizer)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="auth %s",
            args=({"access_token": "secret"},),
            exc_info=None,
        )

        assert filt.filter(record) is True
        assert record.args[0] == "access_token"

    def test_uses_fallback_message_on_format_error(self):
        sanitizer = SensitiveDataSanitizer()
        filt = SanitizingFilter(sanitizer=sanitizer)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="%s %s",
            args=("only-one",),
            exc_info=None,
        )
        record.content = {"access_token": "secret"}

        assert filt.filter(record) is True
        assert "content:" in record.msg
