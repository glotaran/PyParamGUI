"""Schema module representing attributes used for simulation.

e.g. parameters, coordinates, and settings used in simulation.
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel
from pydantic import ConfigDict


class KineticParameters(BaseModel):
    """Kinetic parameters for the simulation.

    Attributes
    ----------
        decay_rates (list[float]): List of decay rates.
    """

    decay_rates: list[float]


class SpectralParameters(BaseModel):
    """Spectral parameters for the simulation.

    Attributes
    ----------
        amplitude (list[float]): List of amplitudes.
        location (list[float]): List of locations.
        width (list[float]): List of widths.
        skewness (list[float]): List of skewness values.
    """

    amplitude: list[float]
    location: list[float]
    width: list[float]
    skewness: list[float]


class TimeCoordinates(BaseModel):
    """Time coordinates for the simulation.

    Attributes
    ----------
        timepoints_max (int): Maximum number of time points.
        timepoints_stepsize (float): Step size between time points.
    """

    timepoints_max: int
    timepoints_stepsize: float


class SpectralCoordinates(BaseModel):
    """Spectral coordinates for the simulation.

    Attributes
    ----------
        wavelength_min (int): Minimum wavelength.
        wavelength_max (int): Maximum wavelength.
        wavelength_stepsize (float): Step size between wavelengths.
    """

    wavelength_min: int
    wavelength_max: int
    wavelength_stepsize: float


def generate_simulation_coordinates(
    time_coordinates: TimeCoordinates, spectral_coordinates: SpectralCoordinates
) -> dict[str, np.ndarray]:
    """Generate simulation coordinates based on time and spectral coordinates.

    Args:
        time_coordinates (TimeCoordinates): The time coordinates for the simulation.
        spectral_coordinates (SpectralCoordinates): The spectral coordinates for the simulation.

    Returns
    -------
    dict[str, np.ndarray]
        A dictionary containing two keys:
        - 'time': A numpy array representing the time axis.
        - 'spectral': A numpy array representing the spectral axis.
    """
    time_axis = np.arange(
        0,
        time_coordinates.timepoints_max * time_coordinates.timepoints_stepsize,
        time_coordinates.timepoints_stepsize,
    )
    spectral_axis = np.arange(
        spectral_coordinates.wavelength_min,
        spectral_coordinates.wavelength_max,
        spectral_coordinates.wavelength_stepsize,
    )
    return {"time": time_axis, "spectral": spectral_axis}


class Settings(BaseModel):
    """Other settings for the simulation.

    Attributes
    ----------
        stdev_noise (float): Standard deviation of the noise to be added to the simulation data.
        seed (int): Seed for the random number generator to ensure reproducibility.
        add_gaussian_irf (bool): Whether to add a Gaussian IRF to the simulation.
            Default is False.
        use_sequential_scheme (bool): Whether to use a sequential scheme in the simulation.
            Default is False.
    """

    stdev_noise: float
    seed: int
    add_gaussian_irf: bool = False
    use_sequential_scheme: bool = False


class IRF(BaseModel):
    """Instrument Response Function (IRF) settings for the simulation.

    Attributes
    ----------
        center (float): The center position of the IRF.
        width (float): The width of the IRF.
    """

    center: float
    width: float


class SimulationConfig(BaseModel):
    """Configuration for the simulation, combining various parameters and settings.

    Attributes
    ----------
        kinetic_parameters (KineticParameters): Kinetic parameters for the simulation.
        spectral_parameters (SpectralParameters): Spectral parameters for the simulation.
        coordinates (Dict[str, np.ndarray]): Dictionary containing the time and spectral axes as
            numpy arrays.
        settings (Settings): Other settings for the simulation, including noise standard deviation,
            random seed, and flags for adding Gaussian IRF and using a sequential scheme.
        irf (IRF): Instrument Response Function (IRF) settings, e.g. center position and width.
    """

    kinetic_parameters: KineticParameters
    spectral_parameters: SpectralParameters
    coordinates: dict[str, np.ndarray]
    settings: Settings
    irf: IRF

    model_config = ConfigDict(arbitrary_types_allowed=True)
