"""This module has various utility functions related to generating files, sanitizing yaml files,
etc.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from typing import Any

import yaml
from glotaran.builtin.io.yml.yml import save_model
from glotaran.plugin_system.data_io_registration import save_dataset
from glotaran.plugin_system.project_io_registration import save_parameters
from glotaran.simulation.simulation import simulate

from pyparamgui.generator import generate_model

if TYPE_CHECKING:
    import numpy as np
    from glotaran.model.model import Model
    from glotaran.parameter.parameters import Parameters

    from pyparamgui.schema import Settings
    from pyparamgui.schema import SimulationConfig


def _generate_model_file(
    simulation_config: SimulationConfig, nr_compartments: int, file_name: str
) -> Model:
    """Generate and save a model file for the simulation.

    This function generates a model based on the provided simulation configuration and number of compartments.
    It saves the generated model to a temporary YAML file, sanitizes the file, and then saves it to the specified file name.

    Args:
        simulation_config (SimulationConfig): The configuration for the simulation.
        nr_compartments (int): The number of compartments in the model.
        file_name (str): The name of the file to save the sanitized model.

    Returns
    -------
        Model: The generated model.
    """
    generator_name = (
        "spectral_decay_sequential"
        if simulation_config.settings.use_sequential_scheme
        else "spectral_decay_parallel"
    )
    model = generate_model(
        generator_name=generator_name,
        generator_arguments={
            "nr_compartments": nr_compartments,
            "irf": simulation_config.settings.add_gaussian_irf,
        },
    )
    save_model(model, "temp_model.yml", allow_overwrite=True)
    _sanitize_yaml_file("temp_model.yml", file_name)
    return model


def _update_parameter_values(parameters: Parameters, simulation_config: SimulationConfig):
    """Update parameter values based on the simulation configuration.

    This function iterates through all parameters and updates their values according to the
    provided simulation configuration. It handles parameters related to spectral shapes,
    kinetic rates, and IRF (Instrument Response Function).

    Args:
        parameters (Parameters): The parameters to be updated.
        simulation_config (SimulationConfig): The configuration containing the new values for the parameters.

    Returns
    -------
        Parameters: The updated parameters.
    """
    for param in parameters.all():
        label = param.label
        if label.startswith("shapes.species_"):
            parts = label.split(".")
            species_index = int(parts[1].split("_")[1]) - 1
            attribute = parts[2]

            if attribute == "amplitude":
                param.value = simulation_config.spectral_parameters.amplitude[species_index]
            elif attribute == "location":
                param.value = simulation_config.spectral_parameters.location[species_index]
            elif attribute == "width":
                param.value = simulation_config.spectral_parameters.width[species_index]
            elif attribute == "skewness":
                param.value = simulation_config.spectral_parameters.skewness[species_index]

        elif label.startswith("rates.species_"):
            species_index = int(label.split("_")[1]) - 1
            param.value = simulation_config.kinetic_parameters.decay_rates[species_index]

        elif label.startswith("irf") and simulation_config.settings.add_gaussian_irf:
            if "width" in label:
                param.value = simulation_config.irf.width
            if "center" in label:
                param.value = simulation_config.irf.center
    return parameters


def _generate_parameter_file(
    simulation_config: SimulationConfig, model: Model, file_name: str
) -> Parameters:
    """Generate and save the parameter file for the simulation.

    This function generates the parameters for the given model, updates them based on the simulation configuration,
    validates the updated parameters, and saves them to a file.

    Args:
        simulation_config (SimulationConfig): The configuration for the simulation.
        model (Model): The model for which parameters are to be generated.
        file_name (str): The name of the file to save the parameters.

    Returns
    -------
        Parameters: The updated and validated parameters.
    """
    parameters = model.generate_parameters()
    updated_parameters = _update_parameter_values(parameters, simulation_config)
    model.validate(updated_parameters)
    save_parameters(updated_parameters, file_name, allow_overwrite=True)
    return updated_parameters


def _generate_data_file(
    model: Model,
    parameters: Parameters,
    coordinates: dict[str, np.ndarray],
    settings: Settings,
    file_name: str,
):
    """Generate and save the data file for the simulation.

    This function simulates the data based on the given model, parameters, coordinates, and settings,
    and saves the simulated data to a file.

    Args:
        model (Model): The model used for simulation.
        parameters (Parameters): The parameters used for simulation.
        coordinates (Dict[str, np.ndarray]): The coordinates for the simulation.
        settings (Settings): The settings for the simulation.
        file_name (str): The name of the file to save the simulated data.
    """
    noise = settings.stdev_noise != 0
    data = simulate(
        model,
        "dataset_1",
        parameters,
        coordinates,
        noise=noise,
        noise_std_dev=settings.stdev_noise,
        noise_seed=settings.seed,
    )
    save_dataset(data, file_name, "nc", allow_overwrite=True)


def generate_model_parameter_and_data_files(
    simulation_config: SimulationConfig,
    model_file_name: str = "model.yml",
    parameter_file_name: str = "parameters.csv",
    data_file_name: str = "dataset.nc",
):
    """Generate and save the model, parameter, and data files for the simulation.

    This function generates the model file, parameter file, and data file based on the given simulation configuration.

    Args:
        simulation_config (SimulationConfig): The configuration for the simulation.
        model_file_name (str, optional): The name of the file to save the model. Defaults to "model.yml".
        parameter_file_name (str, optional): The name of the file to save the parameters. Defaults to "parameters.csv".
        data_file_name (str, optional): The name of the file to save the data. Defaults to "dataset.nc".
    """
    nr_compartments = len(simulation_config.kinetic_parameters.decay_rates)
    model = _generate_model_file(simulation_config, nr_compartments, model_file_name)
    parameters = _generate_parameter_file(simulation_config, model, parameter_file_name)
    _generate_data_file(
        model,
        parameters,
        simulation_config.coordinates,
        simulation_config.settings,
        data_file_name,
    )


def _sanitize_dict(d: dict[str, Any] | Any) -> dict[str, Any] | Any:
    """Recursively sanitize a dictionary by removing keys with values that are None, empty lists,
    or empty dictionaries.

    Args:
        d (Union[Dict[str, Any], Any]): The dictionary to sanitize or any other value.

    Returns
    -------
        Union[Dict[str, Any], Any]: The sanitized dictionary or the original value if it is not a dictionary.
    """
    if not isinstance(d, dict):
        return d
    return {k: _sanitize_dict(v) for k, v in d.items() if v not in (None, [], {})}


def _sanitize_yaml_file(input_file: str, output_file: str) -> None:
    """Sanitize a YAML file by removing keys with values that are None, empty lists, or empty
    dictionaries, and save the sanitized content to a new file.

    Args:
        input_file (str): The path to the input YAML file.
        output_file (str): The path to the output sanitized YAML file.
    """
    with open(input_file) as f:
        data = yaml.safe_load(f)

    sanitized_data = _sanitize_dict(data)

    with open(output_file, "w") as f:
        yaml.safe_dump(sanitized_data, f)
    os.remove(input_file)
