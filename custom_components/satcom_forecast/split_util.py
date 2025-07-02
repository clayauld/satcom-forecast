import logging
import re

_LOGGER = logging.getLogger(__name__)

# Constants for device limits and part numbering overhead
ZOLEO_LIMIT = 200
INREACH_LIMIT = 160

# The longest possible part numbering prefix is "(99/99) " which is 8 characters.
PART_NUMBERING_OVERHEAD = 8


def split_message(text, device_type="zoleo", custom_limit=None):
    """Split a message into parts based on device type and character limits, ensuring no part ever exceeds the limit (including part numbering)."""
    # Reserve space for part numbering (e.g., "(1/10) ")
    # We'll use up to 8 chars for part numbering: "(99/99) "
    max_numbering_length = PART_NUMBERING_OVERHEAD
    min_safe_limit = (
        max_numbering_length + 10
    )  # Minimum safe limit to avoid infinite loops

    # Determine character limit
    if custom_limit is not None and custom_limit >= min_safe_limit:
        limit = custom_limit
    elif device_type == "zoleo":
        limit = 200
    elif device_type == "inreach":
        limit = 160
    else:
        limit = 200  # Default to ZOLEO limit

    effective_limit = limit - max_numbering_length

    # Determine format and split accordingly
    if " | " in text:
        # Summary format - split at pipe separators
        parts = split_summary_format(text, effective_limit)
    else:
        # Compact or full format - split at line breaks
        lines = text.split("\n")
        parts = split_multiline_text(lines, effective_limit)

    # Handle empty text case
    if not parts:
        return [""]

    # Add part numbering if needed, and ensure no part exceeds the hard limit
    if len(parts) > 1:
        total = len(parts)
        numbered_parts = []
        for i, part in enumerate(parts):
            prefix = f"({i+1}/{total}) "
            numbered = prefix + part
            # If this part is too long, split it further
            while len(numbered) > limit:
                # Split at the last word boundary within the allowed space
                allowed = limit - len(prefix)
                split_at = allowed
                for j in range(allowed, 0, -1):
                    if numbered[len(prefix) + j] in [" ", "\n"]:
                        split_at = j
                        break
                first = numbered[:len(prefix) + split_at].rstrip()
                rest = numbered[len(prefix) + split_at:].lstrip()
                numbered_parts.append(first)
                # Prepare next prefix (increment part number)
                i += 1
                prefix = f"({i+1}/{total+1}) "
                numbered = prefix + rest
                total += 1
            numbered_parts.append(numbered)
        parts = numbered_parts
    else:
        # Single part, no numbering needed
        if len(parts[0]) > limit:
            # Split single part if too long
            prefix = "(1/2) "
            allowed = limit - len(prefix)
            split_at = allowed
            for j in range(allowed, 0, -1):
                if parts[0][j] in [" ", "\n"]:
                    split_at = j
                    break
            first = prefix + parts[0][:split_at].rstrip()
            rest = "(2/2) " + parts[0][split_at:].lstrip()
            parts = [first, rest]
    return parts


def smart_split_text(text, effective_limit, config=None):
    """Intelligently split text to maximize character utilization."""
    parts = []

    # Split by lines first
    lines = text.split("\n")

    if len(lines) > 1:
        # Check if this is summary format (pipe-separated) or compact/full format (newline-separated)
        if " | " in text:
            # Summary format - split at pipe separators for better utilization
            parts = split_summary_format(text, effective_limit)
        else:
            # Compact/Full format - combine multiple days efficiently
            parts = split_multiline_text(lines, effective_limit)
    else:
        # Single line format - split by sentences or words
        parts = split_single_line_text(text, effective_limit)

    return parts


def split_multiline_text(lines, effective_limit):
    """Split multi-line text (compact/full format) more aggressively to fill character limits."""
    parts = []
    current_part = []
    current_length = 0

    # Calculate minimum target utilization (85% of limit)
    min_target = int(effective_limit * 0.85)

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Check if adding this line would exceed limit
        line_length = len(line)
        separator_length = 1 if current_part else 0  # Newline separator

        if current_length + line_length + separator_length <= effective_limit:
            # Add to current part
            current_part.append(line)
            current_length += line_length + separator_length
        else:
            # Check if current part meets minimum target utilization
            remaining_lines = len([line_item for line_item in lines[i:] if line_item.strip()])
            if current_part and current_length < min_target and remaining_lines > 0:
                # Try to split the line to fill the current part better
                remaining_space = effective_limit - current_length
                if remaining_space > 10:  # At least 10 chars available
                    split_result = split_line_to_fill_space(line, remaining_space)
                    if split_result:
                        first_part, remaining_part = split_result
                        # Verify we don't exceed the limit
                        if current_length + len(first_part) <= effective_limit:
                            current_part.append(first_part)
                            parts.append("\n".join(current_part))
                            current_part = [remaining_part]
                            current_length = len(remaining_part)
                            continue

            # Current part is full or can't be filled more, start new part
            if current_part:
                parts.append("\n".join(current_part))

            # Check if this single line is too long
            if line_length > effective_limit:
                # Split the long line at word boundaries across multiple parts
                sub_parts = split_long_line_aggressively(line, effective_limit)
                parts.extend(sub_parts)
                current_part = []
                current_length = 0
            else:
                # Check if splitting this line would fill the current part better
                remaining_space = effective_limit - current_length
                if (
                    remaining_space > effective_limit * 0.15
                ):  # If more than 15% of limit is unused
                    # Try to split the line to fill the remaining space
                    split_result = split_line_to_fill_space(line, remaining_space)
                    if split_result:
                        first_part, remaining_part = split_result
                        # Verify we don't exceed the limit
                        if current_length + len(first_part) <= effective_limit:
                            current_part.append(first_part)
                            parts.append("\n".join(current_part))
                            current_part = [remaining_part]
                            current_length = len(remaining_part)
                        else:
                            # Would exceed limit, start new part
                            current_part = [line]
                            current_length = line_length
                    else:
                        # Couldn't split effectively, start new part
                        current_part = [line]
                        current_length = line_length
                else:
                    # Start new part with this line
                    current_part = [line]
                    current_length = line_length

    # Add remaining content
    if current_part:
        parts.append("\n".join(current_part))

    return parts


def split_long_line_aggressively(line, effective_limit):
    """Split a long line aggressively across multiple parts to maximize utilization."""
    parts = []
    remaining_line = line

    # Safety check: ensure effective_limit is positive
    if effective_limit <= 0:
        # If effective_limit is not positive, just return the line as-is
        # This prevents infinite loops but may result in parts exceeding the intended limit
        return [line]

    while remaining_line:
        # Find the best word boundary within the effective limit
        if len(remaining_line) <= effective_limit:
            # Line fits completely
            parts.append(remaining_line)
            break

        # Find the last word boundary within the limit
        split_at = effective_limit
        for i in range(effective_limit, 0, -1):
            if remaining_line[i] in [" ", "\n"]:
                split_at = i
                break

        # If no word boundary found, force split at limit (but this shouldn't happen with our logic)
        if split_at == effective_limit:
            split_at = effective_limit - 1

        # Add the first part
        first_part = remaining_line[:split_at].rstrip()
        if first_part:  # Only add non-empty parts
            parts.append(first_part)

        # Prepare remaining line
        remaining_line = remaining_line[split_at:].lstrip()

    return parts


def split_line_to_fill_space(line, available_space):
    """Split a line to fill available space, returning (first_part, remaining_part) or None if not beneficial."""
    if len(line) <= available_space:
        return None  # Line fits completely, no need to split

    # Find the best word boundary within the available space
    words = line.split()
    current_part = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1  # +1 for space

        if current_length + word_length <= available_space:
            current_part.append(word)
            current_length += word_length
        else:
            break

    if not current_part:
        return None  # No words fit, don't split

    # Check if splitting is beneficial (at least 40% of available space used)
    if current_length < available_space * 0.4:
        return None  # Not beneficial to split

    first_part = " ".join(current_part)
    remaining_part = line[len(first_part):].strip()

    # Final safety check: ensure we don't exceed available space
    if len(first_part) > available_space:
        return None  # Would exceed limit, don't split

    return (first_part, remaining_part)


def split_single_line_text(text, effective_limit):
    """Split single line text efficiently."""
    if len(text) <= effective_limit:
        return [text]

    parts = []
    remaining_text = text

    while remaining_text:
        if len(remaining_text) <= effective_limit:
            parts.append(remaining_text)
            break

        # Try to find a good break point
        break_point = find_best_break_point(remaining_text, effective_limit)

        if break_point > 0:
            part_text = remaining_text[:break_point].strip()
            parts.append(part_text)
            remaining_text = remaining_text[break_point:].strip()
        else:
            # No good break point found, force split
            part_text = remaining_text[:effective_limit]
            parts.append(part_text)
            remaining_text = remaining_text[effective_limit:].strip()

    return parts


def find_best_break_point(text, limit):
    """Find the best point to break text without cutting words."""
    if len(text) <= limit:
        return len(text)

    # Look for natural break points in order of preference
    break_patterns = [
        r"\n",  # Newline (for compact/full formats)
        r" \| ",  # Pipe separator with spaces (for summary format)
        r"\. ",  # Period followed by space
        r", ",  # Comma followed by space
        r" ",  # Space
    ]

    for pattern in break_patterns:
        matches = list(re.finditer(pattern, text[:limit]))
        if matches:
            # Use the last match within the limit
            return matches[-1].end()

    # If no good break point found, try to break at a word boundary
    last_space = text[:limit].rfind(" ")
    if last_space > limit * 0.7:  # Only use if it's not too early
        return last_space

    return 0  # No good break point found


def split_summary_format(text, effective_limit):
    """Split summary format text more aggressively at pipe separators and word boundaries."""
    # Split at pipe separators first
    segments = text.split(" | ")

    parts = []
    current_part = []
    current_length = 0

    # Calculate minimum target utilization (85% of limit)
    min_target = int(effective_limit * 0.85)

    for i, segment in enumerate(segments):
        segment = segment.strip()
        if not segment:
            continue

        # Check if adding this segment would exceed limit
        segment_length = len(segment)
        separator_length = 1 if current_part else 0  # Newline separator

        if current_length + segment_length + separator_length <= effective_limit:
            # Add to current part
            current_part.append(segment)
            current_length += segment_length + separator_length
        else:
            # Check if current part meets minimum target utilization
            remaining_segments = len([s for s in segments[i:] if s.strip()])
            if current_part and current_length < min_target and remaining_segments > 0:
                # Try to split the segment to fill the current part better
                remaining_space = effective_limit - current_length
                if remaining_space > 10:  # At least 10 chars available
                    split_result = split_line_to_fill_space(segment, remaining_space)
                    if split_result:
                        first_part, remaining_part = split_result
                        # Verify we don't exceed the limit
                        if current_length + len(first_part) <= effective_limit:
                            current_part.append(first_part)
                            parts.append("\n".join(current_part))
                            current_part = [remaining_part]
                            current_length = len(remaining_part)
                            continue

            # Current part is full or can't be filled more, start new part
            if current_part:
                parts.append("\n".join(current_part))

            # Check if this single segment is too long
            if segment_length > effective_limit:
                # Split the long segment at word boundaries
                sub_parts = split_long_line_aggressively(segment, effective_limit)
                parts.extend(sub_parts)
                current_part = []
                current_length = 0
            else:
                # Check if splitting this segment would fill the current part better
                remaining_space = effective_limit - current_length
                if (
                    remaining_space > effective_limit * 0.15
                ):  # If more than 15% of limit is unused
                    # Try to split the segment to fill the remaining space
                    split_result = split_line_to_fill_space(segment, remaining_space)
                    if split_result:
                        first_part, remaining_part = split_result
                        # Verify we don't exceed the limit
                        if current_length + len(first_part) <= effective_limit:
                            current_part.append(first_part)
                            parts.append("\n".join(current_part))
                            current_part = [remaining_part]
                            current_length = len(remaining_part)
                        else:
                            # Would exceed limit, start new part
                            current_part = [segment]
                            current_length = segment_length
                    else:
                        # Couldn't split effectively, start new part
                        current_part = [segment]
                        current_length = segment_length
                else:
                    # Start new part with this segment
                    current_part = [segment]
                    current_length = segment_length

    # Add remaining content
    if current_part:
        parts.append("\n".join(current_part))

    return parts
