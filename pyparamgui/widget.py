"""This module contains the simulation widget."""

from __future__ import annotations

import pathlib

import traitlets
import anywidget

from pyparamgui.schema import KineticParameters, SpectralParameters, TimeCoordinates, SpectralCoordinates, Settings, IRF, SimulationConfig, generate_simulation_coordinates
from pyparamgui.utils import generate_model_parameter_and_data_files

class Widget(anywidget.AnyWidget):
    """
    A widget class for handling simulation parameters, coordinates and settings.

    Attributes:
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

widget = Widget()

def _simulate(change) -> None:
    """
    A Private callback function for simulating the data based on the parameters, coordinates, and other simulation settings.
    
    This function generates the model, parameter, and data files using the provided widget inputs.

    The 'change' parameter is not used within this function, but it is required to be present
    because it represents the state change of the traitlets. This is a common pattern when
    using traitlets to observe changes in widget state.
    """
    simulation_config = SimulationConfig(
        kinetic_parameters=KineticParameters(
            decay_rates=widget.decay_rates_input
        ),
        spectral_parameters=SpectralParameters(
            amplitude=widget.amplitude_input,
            location=widget.location_input,
            width=widget.width_input,
            skewness=widget.skewness_input
        ),
        coordinates=generate_simulation_coordinates(
            TimeCoordinates(
                timepoints_max=widget.timepoints_max_input,
                timepoints_stepsize=widget.timepoints_stepsize_input
            ),
            SpectralCoordinates(
                wavelength_min=widget.wavelength_min_input,
                wavelength_max=widget.wavelength_max_input,
                wavelength_stepsize=widget.wavelength_stepsize_input
            )
        ),
        settings=Settings(
            stdev_noise=widget.stdev_noise_input,
            seed=widget.seed_input,
            add_gaussian_irf=widget.add_gaussian_irf_input,
            use_sequential_scheme=widget.use_sequential_scheme_input
        ),
        irf=IRF(
            center=widget.irf_location_input,
            width=widget.irf_width_input
        )
    )
    generate_model_parameter_and_data_files(
        simulation_config,
        model_file_name=widget.model_file_name_input,
        parameter_file_name=widget.parameter_file_name_input,
        data_file_name=widget.data_file_name_input
    )

def setup_widget_observer() -> None:
    """
    Sets up the observer pattern on the 'simulate' traitlet to synchronize the frontend widget
    with the backend simulation code. This function ensures that any changes in the widget's state
    trigger the simulation process, which generates the model, parameter, and data files.
    """
    widget.observe(handler=_simulate, names=['simulate'])
