from typing import Dict

import numpy as np
from pydantic import BaseModel, ConfigDict

class KineticParameters(BaseModel):
    decay_rates: list[float]

class SpectralParameters(BaseModel):
    amplitudes: list[float]
    location_mean: list[float]
    width: list[float]
    skewness: list[float]

class TimeCoordinates(BaseModel):
    timepoints_max: int
    timepoints_stepsize: float

class SpectralCoordinates(BaseModel):
    wavelength_min: int
    wavelength_max: int
    wavelength_stepsize: int
    
def generate_simulation_coordinates(time_coordinates: TimeCoordinates, spectral_coordinates: SpectralCoordinates) -> Dict[str, np.ndarray]:
    time_axis = np.arange(0, time_coordinates.timepoints_max * time_coordinates.timepoints_stepsize, time_coordinates.timepoints_stepsize)
    spectral_axis = np.arange(spectral_coordinates.wavelength_min, spectral_coordinates.wavelength_max, spectral_coordinates.wavelength_stepsize)
    return {"time": time_axis, "spectral": spectral_axis}

class Settings(BaseModel):
    stdev_noise: float
    seed: int
    add_gaussian_irf: bool = False
    use_sequential_scheme: bool = False

class IRF(BaseModel):
    center: float = 0
    width: float = 0

class SimulationConfig(BaseModel):
    kinetic_parameters: KineticParameters
    spectral_parameters: SpectralParameters
    coordinates: Dict[str, np.ndarray]
    settings: Settings
    irf: IRF

    model_config = ConfigDict(arbitrary_types_allowed=True)
