import panel as pn
import numpy as np

from pyparamgui.config import KineticParameters, SpectralParameters, TimeCoordinates, SpectralCoordinates, Settings, IRF, SimulationConfig, generate_simulation_coordinates
from pyparamgui.io import generate_model_parameter_and_data_files

class SimulationWidget:
    def __init__(self):
        pn.extension()
        self.simulation_config = None
        self.decay_rates = pn.widgets.TextInput(name='Decay rates', value='0.055, 0.005')
        self.amplitudes = pn.widgets.TextInput(name='Amplitudes', value='1., 1.')
        self.location = pn.widgets.TextInput(name='Location (mean) of spectra', value='22000, 20000')
        self.width = pn.widgets.TextInput(name='Width of spectra', value='4000, 3500')
        self.skewness = pn.widgets.TextInput(name='Skewness of spectra', value='0.1, -0.1')
        self.timepoints_max = pn.widgets.IntInput(name='Timepoints, max', value=80)
        self.timepoints_stepsize = pn.widgets.FloatInput(name='Stepsize', value=1)
        self.wavelength_min = pn.widgets.IntInput(name='Wavelength Min', value=400)
        self.wavelength_max = pn.widgets.IntInput(name='Wavelength Max', value=600)
        self.wavelength_stepsize = pn.widgets.IntInput(name='Stepsize', value=5)
        self.stdev_noise = pn.widgets.FloatInput(name='Std.dev. noise', value=0.01)
        self.seed = pn.widgets.IntInput(name='Seed', value=123)
        self.add_gaussian_irf = pn.widgets.Checkbox(name='Add Gaussian IRF')
        self.irf_location = pn.widgets.FloatInput(name='IRF location', value=0)
        self.irf_width = pn.widgets.FloatInput(name='IRF width', value=0)
        self.use_sequential_scheme = pn.widgets.Checkbox(name='Use a sequential scheme')
        self.model_file_name = pn.widgets.TextInput(name='Model File Name', value='model.yml')
        self.parameter_file_name = pn.widgets.TextInput(name='Parameter File Name', value='parameters.csv')
        self.data_file_name = pn.widgets.TextInput(name='Data File Name', value='dataset.nc')
        self.button = pn.widgets.Button(name='Simulate', button_type='primary')
        self.output_pane = pn.pane.Markdown("")

        self.widget = pn.Column(
            self.decay_rates, self.amplitudes, self.location, self.width, self.skewness,
            pn.Row(self.timepoints_max, self.timepoints_stepsize),
            pn.Row(self.wavelength_min, self.wavelength_max, self.wavelength_stepsize),
            self.stdev_noise, self.seed, self.add_gaussian_irf, self.irf_location, self.irf_width,
            self.use_sequential_scheme,
            pn.Row(self.model_file_name, self.parameter_file_name, self.data_file_name),
            self.button, self.output_pane
        )

        self.button.on_click(self.callback)

    def callback(self, event):
        try:
            decay_rates = np.fromstring(self.decay_rates.value, sep=',')
            amplitudes = np.fromstring(self.amplitudes.value, sep=',')
            location = np.fromstring(self.location.value, sep=',')
            width = np.fromstring(self.width.value, sep=',')
            skewness = np.fromstring(self.skewness.value, sep=',')

            valid_input = True
            messages = []

            if self.wavelength_min.value >= self.wavelength_max.value or self.timepoints_max.value <= 0:
                valid_input = False
                messages.append("Invalid timepoints or wavelength specification")

            lengths = {len(decay_rates), len(amplitudes), len(location), len(width), len(skewness)}
            if len(lengths) > 1:
                valid_input = False
                messages.append("Parameter fields of unequal length")

            if not valid_input:
                self.output_pane.object = pn.pane.Markdown('\n'.join(f"**Error:** {msg}" for msg in messages))
            else:
                self.simulation_config = SimulationConfig(
                    kinetic_parameters=KineticParameters(
                        decay_rates=decay_rates.tolist()
                    ),
                    spectral_parameters=SpectralParameters(
                        amplitudes=amplitudes.tolist(),
                        location_mean=location.tolist(),
                        width=width.tolist(),
                        skewness=skewness.tolist()
                    ),
                    coordinates=generate_simulation_coordinates(
                        TimeCoordinates(
                            timepoints_max=self.timepoints_max.value,
                            timepoints_stepsize=self.timepoints_stepsize.value
                        ),
                        SpectralCoordinates(
                            wavelength_min=self.wavelength_min.value,
                            wavelength_max=self.wavelength_max.value,
                            wavelength_stepsize=self.wavelength_stepsize.value
                        )
                    ),
                    settings=Settings(
                        stdev_noise=self.stdev_noise.value,
                        seed=self.seed.value,
                        add_gaussian_irf=self.add_gaussian_irf.value,
                        use_sequential_scheme=self.use_sequential_scheme.value
                    ),
                    irf=IRF(
                        center=self.irf_location.value,
                        width=self.irf_width.value
                    )
                )
                generate_model_parameter_and_data_files(
                    self.simulation_config,
                    model_file_name=self.model_file_name.value,
                    parameter_file_name=self.parameter_file_name.value,
                    data_file_name=self.data_file_name.value
                )
                self.output_pane.object = "**Simulation successful!**\n\n**Files created!**"

        except Exception as e:
            self.output_pane.object = f"**Error in simulation:** {str(e)}"


simulation_form = SimulationWidget()
simulation_form.widget.servable()