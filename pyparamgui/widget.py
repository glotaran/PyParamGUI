"""Simulation widget module."""

from __future__ import annotations

import pathlib

import anywidget
import traitlets
from glotaran.io import load_dataset
from pyglotaran_extras import plot_data_overview

from pyparamgui.schema import IRF
from pyparamgui.schema import KineticParameters
from pyparamgui.schema import Settings
from pyparamgui.schema import SimulationConfig
from pyparamgui.schema import SpectralCoordinates
from pyparamgui.schema import SpectralParameters
from pyparamgui.schema import TimeCoordinates
from pyparamgui.schema import generate_simulation_coordinates
from pyparamgui.utils import generate_model_parameter_and_data_files


class Widget(anywidget.AnyWidget):
    """A widget class for handling simulation parameters, coordinates and settings.

    Attributes
    ----------
        _esm (pathlib.Path): Path to the JavaScript file for the widget.
        _css (pathlib.Path): Path to the CSS file for the widget.
        decay_rates_input (traitlets.List): List of decay rates as floats.
        amplitude_input (traitlets.List): List of amplitudes as floats.
        location_input (traitlets.List): List of locations as floats.
        width_input (traitlets.List): List of widths as floats.
        skewness_input (traitlets.List): List of skewness values as floats.
        timepoints_max_input (traitlets.Int): Maximum number of timepoints.
        timepoints_stepsize_input (traitlets.Float): Step size for timepoints.
        wavelength_min_input (traitlets.Float): Minimum wavelength value.
        wavelength_max_input (traitlets.Float): Maximum wavelength value.
        wavelength_stepsize_input (traitlets.Float): Step size for wavelength.
        stdev_noise_input (traitlets.Float): Standard deviation of noise.
        seed_input (traitlets.Int): Seed for random number generation.
        add_gaussian_irf_input (traitlets.Bool): Flag to add Gaussian IRF.
        irf_location_input (traitlets.Float): Location of the IRF center.
        irf_width_input (traitlets.Float): Width of the IRF.
        use_sequential_scheme_input (traitlets.Bool): Flag to use sequential scheme.
        model_file_name_input (traitlets.Unicode): Name of the model file.
        parameter_file_name_input (traitlets.Unicode): Name of the parameter file.
        data_file_name_input (traitlets.Unicode): Name of the data file.
        simulate (traitlets.Unicode): Trigger for simulation.
        visualize_data (traitlets.Bool): Flag to visualize data.
    """

    _esm: pathlib.Path = pathlib.Path(__file__).parent / "static" / "form.js"
    _css: pathlib.Path = pathlib.Path(__file__).parent / "static" / "form.css"
    decay_rates_input: traitlets.List = traitlets.List(trait=traitlets.Float()).tag(sync=True)
    amplitude_input: traitlets.List = traitlets.List(trait=traitlets.Float()).tag(sync=True)
    location_input: traitlets.List = traitlets.List(trait=traitlets.Float()).tag(sync=True)
    width_input: traitlets.List = traitlets.List(trait=traitlets.Float()).tag(sync=True)
    skewness_input: traitlets.List = traitlets.List(trait=traitlets.Float()).tag(sync=True)
    timepoints_max_input: traitlets.Int = traitlets.Int().tag(sync=True)
    timepoints_stepsize_input: traitlets.Float = traitlets.Float().tag(sync=True)
    wavelength_min_input: traitlets.Float = traitlets.Float().tag(sync=True)
    wavelength_max_input: traitlets.Float = traitlets.Float().tag(sync=True)
    wavelength_stepsize_input: traitlets.Float = traitlets.Float().tag(sync=True)
    stdev_noise_input: traitlets.Float = traitlets.Float().tag(sync=True)
    seed_input: traitlets.Int = traitlets.Int().tag(sync=True)
    add_gaussian_irf_input: traitlets.Bool = traitlets.Bool().tag(sync=True)
    irf_location_input: traitlets.Float = traitlets.Float().tag(sync=True)
    irf_width_input: traitlets.Float = traitlets.Float().tag(sync=True)
    use_sequential_scheme_input: traitlets.Bool = traitlets.Bool().tag(sync=True)
    model_file_name_input: traitlets.Unicode = traitlets.Unicode("").tag(sync=True)
    parameter_file_name_input: traitlets.Unicode = traitlets.Unicode("").tag(sync=True)
    data_file_name_input: traitlets.Unicode = traitlets.Unicode("").tag(sync=True)
    simulate: traitlets.Unicode = traitlets.Unicode("").tag(sync=True)
    visualize_data: traitlets.Bool = traitlets.Bool(default_value=True).tag(sync=True)

    def __init__(self):
        super().__init__()
        self.observe(handler=_simulate, names=["simulate"])


def _simulate(change: dict) -> None:
    """Generate simulation files based on (global) widget (`_widget`) inputs.

    This private callback function creates model, parameter, and data files
    using the current widget (`_widget`) state. The 'change' parameter is unused but
    required for traitlet observation.
    """
    widget_instance = change["owner"]
    simulation_config = SimulationConfig(
        kinetic_parameters=KineticParameters(decay_rates=widget_instance.decay_rates_input),
        spectral_parameters=SpectralParameters(
            amplitude=widget_instance.amplitude_input,
            location=widget_instance.location_input,
            width=widget_instance.width_input,
            skewness=widget_instance.skewness_input,
        ),
        coordinates=generate_simulation_coordinates(
            TimeCoordinates(
                timepoints_max=widget_instance.timepoints_max_input,
                timepoints_stepsize=widget_instance.timepoints_stepsize_input,
            ),
            SpectralCoordinates(
                wavelength_min=widget_instance.wavelength_min_input,
                wavelength_max=widget_instance.wavelength_max_input,
                wavelength_stepsize=widget_instance.wavelength_stepsize_input,
            ),
        ),
        settings=Settings(
            stdev_noise=widget_instance.stdev_noise_input,
            seed=widget_instance.seed_input,
            add_gaussian_irf=widget_instance.add_gaussian_irf_input,
            use_sequential_scheme=widget_instance.use_sequential_scheme_input,
        ),
        irf=IRF(center=widget_instance.irf_location_input, width=widget_instance.irf_width_input),
    )
    generate_model_parameter_and_data_files(
        simulation_config,
        model_file_name=widget_instance.model_file_name_input,
        parameter_file_name=widget_instance.parameter_file_name_input,
        data_file_name=widget_instance.data_file_name_input,
    )
    if widget_instance.visualize_data:
        irf_location = (
            None
            if not simulation_config.settings.add_gaussian_irf
            else simulation_config.irf.center
        )
        plot_data_overview(
            dataset=load_dataset(widget_instance.data_file_name_input), irf_location=irf_location
        )
