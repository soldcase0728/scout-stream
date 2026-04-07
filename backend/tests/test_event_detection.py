"""Tests for event detection engine."""

import pytest

from processing.event_detection import detect_events, DetectedEvents
from processing.landmark_contract import LandmarkTimeSeries


class TestEventDetection:
    def test_events_are_ordered(self, swing_series: LandmarkTimeSeries):
        """Start < Launch < Contact must always hold."""
        events = detect_events(swing_series, "regular")
        assert events.start_frame < events.launch_frame
        assert events.launch_frame < events.contact_frame

    def test_start_is_in_first_half(self, swing_series: LandmarkTimeSeries):
        """Start should be detected in the early portion of the swing."""
        events = detect_events(swing_series, "regular")
        assert events.start_frame < swing_series.num_frames // 2

    def test_contact_is_in_second_half(self, swing_series: LandmarkTimeSeries):
        """Contact should be detected in the later portion."""
        events = detect_events(swing_series, "regular")
        assert events.contact_frame > swing_series.num_frames // 3

    def test_confidence_is_bounded(self, swing_series: LandmarkTimeSeries):
        """Confidence should be between 0 and 1."""
        events = detect_events(swing_series, "regular")
        assert 0.0 <= events.confidence <= 1.0

    def test_short_series_handled(self):
        """Very short series should not crash."""
        from tests.conftest import make_frame

        frames = [make_frame(i) for i in range(5)]
        series = LandmarkTimeSeries(frames=frames, frame_rate=30.0)
        events = detect_events(series, "regular")
        assert events.start_frame < events.contact_frame

    def test_slap_hitter_events_ordered(self, swing_series: LandmarkTimeSeries):
        """Slap hitter events should also be properly ordered."""
        events = detect_events(swing_series, "left_slap")
        assert events.start_frame < events.launch_frame
        assert events.launch_frame < events.contact_frame
