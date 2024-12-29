"""Utility module for generating files, sanitizing yaml files, etc."""

from __future__ import annotations

from pathlib import Path
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
    from glotaran.parameter.parameter import Parameter
    from glotaran.parameter.parameters import Parameters

    from pyparamgui.schema import Settings
    from pyparamgui.schema import SimulationConfig


def _generate_model_file(
    simulation_config: SimulationConfig, nr_compartments: int, file_name: str
) -> Model:
    """Generate and save a model file for the simulation.

    This function generates a model based on the provided simulation configuration
    and number of compartments.
    It saves the generated model to a temporary YAML file, sanitizes the file,
    and then saves it to the specified file name.

    Args:
        simulation_config (SimulationConfig): The configuration for the simulation.
        nr_compartments (int): The number of compartments in the model.
        file_name (str): The name of the file to save the sanitized model.

    Returns
    -------
    Model
        The generated model object, which can be used for further processing or simulation.
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


def _update_parameter_values(
    parameters: Parameters, simulation_config: SimulationConfig
) -> Parameters:
    """Update parameter values based on the simulation configuration.

    This function iterates through all parameters and updates their values
    based on the provided simulation configuration. It handles shape parameters,
    rate parameters, and IRF (Instrument Response Function) parameters.

    Parameters
    ----------
    parameters : Parameters
        The set of parameters to be updated.
    simulation_config : SimulationConfig
        The configuration object containing the simulation settings and parameter values.

    Returns
    -------
    `Parameters`
        The updated set of parameters with new values based on the
        simulation configuration.
    """
    for param in parameters.all():
        label = param.label
        if label.startswith("shapes.species_"):
            _update_shape_parameter(param, label, simulation_config)
        elif label.startswith("rates.species_"):
            _update_rate_parameter(param, label, simulation_config)
        elif label.startswith("irf") and simulation_config.settings.add_gaussian_irf:
            _update_irf_parameter(param, label, simulation_config)
    return parameters


def _update_shape_parameter(param: Parameter, label: str, simulation_config: SimulationConfig):
    """Update shape parameters."""
    parts = label.split(".")
    species_index = int(parts[1].split("_")[1]) - 1
    attribute = parts[2]
    spectral_params = simulation_config.spectral_parameters

    if attribute == "amplitude":
        param.value = spectral_params.amplitude[species_index]
    elif attribute == "location":
        param.value = spectral_params.location[species_index]
    elif attribute == "width":
        param.value = spectral_params.width[species_index]
    elif attribute == "skewness":
        param.value = spectral_params.skewness[species_index]


def _update_rate_parameter(param: Parameter, label: str, simulation_config: SimulationConfig):
    """Update rate parameters."""
    species_index = int(label.split("_")[1]) - 1
    param.value = simulation_config.kinetic_parameters.decay_rates[species_index]


def _update_irf_parameter(param: Parameter, label: str, simulation_config: SimulationConfig):
    """Update IRF parameters."""
    if "width" in label:
        param.value = simulation_config.irf.width
    elif "center" in label:
        param.value = simulation_config.irf.center


def _generate_parameter_file(
    simulation_config: SimulationConfig, model: Model, file_name: str
) -> Parameters:
    """Generate and save the parameter file for the simulation.

    This function generates the parameters for the given model,
    updates them based on the simulation configuration,
    validates the updated parameters, and saves them to a file.

    Args:
        simulation_config (SimulationConfig): The configuration for the simulation.
        model (Model): The model for which parameters are to be generated.
        file_name (str): The name of the file to save the parameters.

    Returns
    -------
    `Parameters`
        The updated and validated parameters.
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

    This function simulates the data based on the given model, parameters, coordinates,
    and settings, and saves the simulated data to a file.

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

    This function generates the model file, parameter file, and data file based on the given
    simulation configuration.

    Args:
        simulation_config (SimulationConfig): The configuration for the simulation.
        model_file_name (str, optional): The name of the file to save the model.
            Defaults to "model.yml".
        parameter_file_name (str, optional): The name of the file to save the parameters.
            Defaults to "parameters.csv".
        data_file_name (str, optional): The name of the file to save the data.
            Defaults to "dataset.nc".
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
    """Sanitize an input dictionary and produce a new sanitized dictionary.

    Recursively sanitize a dictionary by removing keys with values that are None, empty lists,
    or empty dictionaries.

    Parameters
    ----------
    d : dict[str, Any] | Any
        The dictionary to sanitize or any other value.

    Returns
    -------
    dict[str, Any] | Any
        The sanitized dict or the original value if input is not a dict.
    """
    if not isinstance(d, dict):
        return d
    return {k: _sanitize_dict(v) for k, v in d.items() if v not in (None, [], {})}


def _sanitize_yaml_file(input_file: str, output_file: str) -> None:
    """Sanitize an input YAML file and produce a new sanitized YAML file.

    Sanitize by removing keys with values that are None, empty lists, or empty
    dictionaries, and save the sanitized content to a new file.

    Args:
        input_file (str): The path to the input YAML file.
        output_file (str): The path to the output sanitized YAML file.
    """
    with Path(input_file).open() as f:
        data = yaml.safe_load(f)

    sanitized_data = _sanitize_dict(data)

    with Path(output_file).open("w") as f:
        yaml.safe_dump(sanitized_data, f)
    Path(input_file).unlink()
