from typing import Any, Dict, Union
import yaml

import numpy as np

from pyparamgui.generator import generate_model
from pyparamgui.config import SimulationConfig, Settings
from glotaran.model.model import Model
from glotaran.builtin.io.yml.yml import save_model
from glotaran.parameter.parameters import Parameters
from glotaran.plugin_system.project_io_registration import save_parameters
from glotaran.plugin_system.data_io_registration import save_dataset
from glotaran.simulation.simulation import simulate

def _generate_model_file(simulation_config: SimulationConfig, nr_compartments: int, file_name: str) -> Model:
    generator_name = "spectral_decay_sequential" if simulation_config.settings.use_sequential_scheme else "spectral_decay_parallel"
    model = generate_model(generator_name=generator_name, generator_arguments={"nr_compartments": nr_compartments, "irf": simulation_config.settings.add_gaussian_irf})
    save_model(model, "temp_model.yml", allow_overwrite=True)
    _sanitize_yaml_file("temp_model.yml", file_name)
    return model

def _generate_parameter_file(model: Model, file_name: str) -> Parameters:
    parameters = model.generate_parameters()
    model.validate(parameters)
    save_parameters(parameters, file_name, allow_overwrite=True)
    return parameters

def _generate_data_file(model: Model, parameters: Parameters, coordinates: Dict[str, np.ndarray], settings: Settings, file_name: str):
    noise = False if settings.stdev_noise == 0 else True
    data = simulate(model, "dataset_1", parameters, coordinates, noise=noise, noise_std_dev=settings.stdev_noise, noise_seed=settings.seed)
    save_dataset(data, file_name, "nc", allow_overwrite=True)

def generate_model_parameter_and_data_files(simulation_config: SimulationConfig, model_file_name: str = "model.yml", parameter_file_name: str = "parameters.csv", data_file_name: str = "dataset.nc"):
    nr_compartments = len(simulation_config.kinetic_parameters.decay_rates)
    model = _generate_model_file(simulation_config, nr_compartments, model_file_name)
    parameters = _generate_parameter_file(model, parameter_file_name)
    _generate_data_file(model, parameters, simulation_config.coordinates, simulation_config.settings, data_file_name)

def _sanitize_dict(d: Union[Dict[str, Any], Any]) -> Union[Dict[str, Any], Any]:
    if not isinstance(d, dict):
        return d
    return {k: _sanitize_dict(v) for k, v in d.items() if v not in (None, [], {})}

def _sanitize_yaml_file(input_file: str, output_file: str) -> None:
    with open(input_file, 'r') as f:
        data = yaml.safe_load(f)
    
    sanitized_data = _sanitize_dict(data)
    
    with open(output_file, 'w') as f:
        yaml.safe_dump(sanitized_data, f)