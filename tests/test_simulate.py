"""Test for widget _simulate functionality."""

from __future__ import annotations

import tempfile
from contextlib import contextmanager
from pathlib import Path

import pytest

from pyparamgui.widget import Widget
from pyparamgui.widget import _simulate
from pyparamgui.widget import _widget as global_widget


def _create_mock_widget():
    widget = Widget()
    widget.decay_rates_input = [0.1, 0.2]
    widget.amplitude_input = [1.0, 2.0]
    widget.location_input = [400, 500]
    widget.width_input = [10, 20]
    widget.skewness_input = [0, 0]
    widget.timepoints_max_input = 100
    widget.timepoints_stepsize_input = 0.1
    widget.wavelength_min_input = 400
    widget.wavelength_max_input = 600
    widget.wavelength_stepsize_input = 1
    widget.stdev_noise_input = 0.01
    widget.seed_input = 42
    widget.add_gaussian_irf_input = True
    widget.irf_location_input = 0
    widget.irf_width_input = 0.1
    widget.use_sequential_scheme_input = False
    widget.model_file_name_input = "model.yml"
    widget.parameter_file_name_input = "parameters.csv"
    widget.data_file_name_input = "dataset.nc"
    return widget


@pytest.fixture()
def mock_widget():
    """Return a mock Widget for testing."""
    return _create_mock_widget()


@contextmanager
def use_mock_widget(mock_widget):
    """Mock the global Widget instance (`_widget`) during the test."""
    original_widget = global_widget
    import pyparamgui.widget

    pyparamgui.widget._widget = mock_widget
    try:
        yield
    finally:
        pyparamgui.widget._widget = original_widget


@pytest.fixture()
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


def test_simulate(mock_widget, temp_dir):
    """Test the _simulate function to ensure it generates non-empty files."""
    model_file_name_input_path = Path(temp_dir) / "model.yml"
    parameter_file_name_input_path = Path(temp_dir) / "parameters.csv"
    data_file_name_input_path = Path(temp_dir) / "dataset.nc"

    with use_mock_widget(mock_widget):
        mock_widget.model_file_name_input = str(model_file_name_input_path)
        mock_widget.parameter_file_name_input = str(parameter_file_name_input_path)
        mock_widget.data_file_name_input = str(data_file_name_input_path)
        _simulate(None)

        # Check if files exist and are not empty
        # Ideally you would also want to check their content here
        assert model_file_name_input_path.exists()
        assert model_file_name_input_path.stat().st_size > 0

        assert parameter_file_name_input_path.exists()
        assert parameter_file_name_input_path.stat().st_size > 0

        assert data_file_name_input_path.exists()
        assert data_file_name_input_path.stat().st_size > 0


if __name__ == "__main__":
    my_mock_widget = _create_mock_widget()
    with tempfile.TemporaryDirectory() as temp_dir:
        test_simulate(my_mock_widget, temp_dir)
