"""Extended tests for split utility functionality to improve coverage."""

import os
import sys

import pytest

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

# Import functions directly from module files
try:
    sys.path.insert(
        0,
        os.path.join(
            os.path.dirname(__file__), "..", "custom_components", "satcom_forecast"
        ),
    )
    from split_util import (
        find_best_break_point,
        smart_split_text,
        split_line_to_fill_space,
        split_long_line_aggressively,
        split_message,
        split_single_line_text,
        split_summary_format,
    )
except ImportError:
    pytest.fail("Could not import split_util functions")


class TestSplitUtilExtended:
    """Extended tests for split utility functionality."""

    def test_smart_split_text_single_line(self):
        """Test smart_split_text with single line input."""
        text = "This is a single line of text that should be split properly."
        parts = smart_split_text(text, effective_limit=20)
        assert len(parts) > 1
        assert "This is a single" in parts[0]

    def test_smart_split_text_summary_format(self):
        """Test smart_split_text with summary format (pipes)."""
        text = "Day 1: Sunny | Day 2: Cloudy | Day 3: Rain"
        parts = smart_split_text(text, effective_limit=20)
        # Should split at pipes
        assert len(parts) >= 3
        assert "Day 1: Sunny" in parts[0]

    def test_smart_split_text_multiline(self):
        """Test smart_split_text with multiline input."""
        text = "Line 1\nLine 2\nLine 3"
        parts = smart_split_text(text, effective_limit=10)
        assert len(parts) >= 1

    def test_split_long_line_aggressively_safety(self):
        """Test split_long_line_aggressively with invalid limit."""
        text = "Some text"
        # Should return list with original text if limit <= 0
        parts = split_long_line_aggressively(text, effective_limit=0)
        assert parts == [text]
        parts = split_long_line_aggressively(text, effective_limit=-5)
        assert parts == [text]

    def test_split_long_line_aggressively_splitting(self):
        """Test split_long_line_aggressively actually splits."""
        text = "Word1 Word2 Word3"
        parts = split_long_line_aggressively(text, effective_limit=6)
        # "Word1 " is 6 chars. "Word2 " is 6 chars.
        assert "Word1" in parts
        assert "Word2" in parts
        assert "Word3" in parts

    def test_split_line_to_fill_space_beneficial(self):
        """Test split_line_to_fill_space only splits if beneficial."""
        line = "A very long line that might be split"
        # Available space is small, but enough for "A very" (6 chars)
        # Length of "A very" is 6. Available space 10. 6/10 = 0.6 > 0.4. Should split.
        result = split_line_to_fill_space(line, available_space=10)
        assert result is not None
        first, rest = result
        assert first == "A very"
        assert rest == "long line that might be split"

    def test_split_line_to_fill_space_not_beneficial(self):
        """Test split_line_to_fill_space rejects if not beneficial."""
        # Available space 20. "A" is 1 char. 1/20 = 0.05 < 0.4.
        # Wait, it tries to fill as much as possible.
        # If we give it space for just "A", it's 1 char.
        # If available space is 10. "A very" is 6. 6/10 = 0.6.
        # Let's try a case where the first word is very short compared to available
        # space, but the next word makes it overflow.
        # "I am" -> "I" (1). "am" (2).
        # If available space is 10. "I am" fits.
        # We need a case where current_length < available_space * 0.4

        # line = "I am a robot"
        # available_space = 10
        # "I am a" = 6 chars. 6/10 = 0.6.

        # line = "I cannotfitthisword"
        # available_space = 10
        # "I" fits (1 char). "cannotfitthisword" (17 chars) doesn't fit.
        # So current_part is ["I"]. Length 1.
        # 1 < 10 * 0.4 (4). So it should return None.
        result = split_line_to_fill_space("I cannotfitthisword", available_space=10)
        assert result is None

    def test_split_line_to_fill_space_no_fit(self):
        """Test split_line_to_fill_space when nothing fits."""
        line = "Supercalifragilisticexpialidocious"
        result = split_line_to_fill_space(line, available_space=5)
        assert result is None

    def test_split_single_line_text_breakpoints(self):
        """Test split_single_line_text finding breakpoints."""
        # "Hello. World" -> Split at ". "
        text = "Hello. World"
        parts = split_single_line_text(text, effective_limit=7)
        assert parts[0] == "Hello."
        assert parts[1] == "World"

    def test_find_best_break_point_priorities(self):
        """Test find_best_break_point priorities."""
        # Preference: newline > pipe > period > comma > space

        # Period vs Comma
        text = "Hello, World. Test"
        # If limit includes both, should pick period?
        # The code iterates patterns in order.
        # It finds ALL matches for a pattern and takes the last one.
        # But it returns immediately if it finds matches for a higher priority pattern.

        # So if we have newlines, it splits there.
        # If no newlines, looks for pipes.

        # "Hello, World. Test"
        # Limit 15.
        # No newline. No pipe.
        # Period: ". " at index 12.
        # Comma: ", " at index 5.
        # Should pick period.
        # Match is ". " (indices 12, 13). end() is 14.
        bp = find_best_break_point(text, limit=15)
        assert bp == 14

    def test_split_summary_format_aggressive(self):
        """Test split_summary_format splitting long segments."""
        # A segment longer than limit
        text = (
            "Short | This is a very long segment that needs to be split aggressively "
            "because it exceeds the limit | End"
        )
        parts = split_summary_format(text, effective_limit=20)
        # Should split the middle part
        assert len(parts) > 3

    def test_split_message_empty(self):
        """Test split_message with empty string."""
        assert split_message("") == [""]
