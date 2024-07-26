function render({ model, el }) {
    const form = document.createElement('form');

    /**
     * Creates a form group with a label and a text input field.
     *
     * @param {string} labelText - The text content for the label.
     * @param {string} inputId - The id attribute for the input element.
     * @param {string} inputName - The name attribute for the input element.
     * @param {string} inputValue - The initial value for the input element.
     * 
     * @returns {HTMLDivElement} The form group element containing the label and input.
     */
    function createTextFormGroup(labelText, inputId, inputName, inputValue) {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';

        const label = document.createElement('label');
        label.setAttribute('for', inputId);
        label.textContent = labelText;

        const input = document.createElement('input');
        input.setAttribute('type', 'text');
        input.setAttribute('id', inputId);
        input.setAttribute('name', inputName);
        input.value = inputValue;

        formGroup.appendChild(label);
        formGroup.appendChild(input);

        return formGroup;
    }

    /**
     * Creates a form group with a label and a checkbox input field.
     *
     * @param {string} labelText - The text content for the label.
     * @param {string} inputId - The id attribute for the input element.
     * @param {string} inputName - The name attribute for the input element.
     * 
     * @returns {HTMLDivElement} The form group element containing the label and checkbox input.
     */
    function createCheckboxFormGroup(labelText, inputId, inputName) {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';

        const label = document.createElement('label');
        label.setAttribute('for', inputId);
        label.textContent = labelText;

        const input = document.createElement('input');
        input.setAttribute('type', 'checkbox');
        input.setAttribute('id', inputId);
        input.setAttribute('name', inputName);

        formGroup.appendChild(label);
        formGroup.appendChild(input);

        return formGroup;
    }

    form.appendChild(createTextFormGroup('Decay rates:', 'decay_rates_input', 'decay_rates_input', '0.055, 0.005'));
    form.appendChild(document.createElement('hr'));
    form.appendChild(createTextFormGroup('Amplitudes:', 'amplitude_input', 'amplitude_input', '1., 1.'));
    form.appendChild(createTextFormGroup('Location (mean) of spectra:', 'location_input', 'location_input', '22000, 20000'));
    form.appendChild(createTextFormGroup('Width of spectra:', 'width_input', 'width_input', '4000, 3500'));
    form.appendChild(createTextFormGroup('Skewness of spectra:', 'skewness_input', 'skewness_input', '0.1, -0.1'));
    form.appendChild(document.createElement('hr'));
    form.appendChild(createTextFormGroup('Timepoints, max:', 'timepoints_max_input', 'timepoints_max_input', '80'));
    form.appendChild(createTextFormGroup('Stepsize:', 'timepoints_stepsize_input', 'timepoints_stepsize_input', '1'));
    form.appendChild(document.createElement('hr'));
    form.appendChild(createTextFormGroup('Wavelength Min:', 'wavelength_min_input', 'wavelength_min_input', '400'));
    form.appendChild(createTextFormGroup('Wavelength Max:', 'wavelength_max_input', 'wavelength_max_input', '600'));
    form.appendChild(createTextFormGroup('Stepsize:', 'wavelength_stepsize_input', 'wavelength_stepsize_input', '5'));
    form.appendChild(document.createElement('hr'));
    form.appendChild(createTextFormGroup('Std.dev. noise:', 'stdev_noise_input', 'stdev_noise_input', '0.01'));
    form.appendChild(createTextFormGroup('Seed:', 'seed_input', 'seed_input', '123'));
    form.appendChild(document.createElement('hr'));
    form.appendChild(createCheckboxFormGroup('Add Gaussian IRF:', 'add_gaussian_irf_input', 'add_gaussian_irf_input'));
    form.appendChild(createTextFormGroup('IRF location:', 'irf_location_input', 'irf_location_input', '3'));
    form.appendChild(createTextFormGroup('IRF width:', 'irf_width_input', 'irf_width_input', '1'));
    form.appendChild(document.createElement('hr'));
    form.appendChild(createCheckboxFormGroup('Use Sequential Scheme:', 'use_sequential_scheme_input', 'use_sequential_scheme_input'));
    form.appendChild(document.createElement('hr'));
    form.appendChild(createTextFormGroup('Model File Name:', 'model_file_name_input', 'model_file_name_input', 'model.yml'));
    form.appendChild(createTextFormGroup('Parameter File Name:', 'parameter_file_name_input', 'parameter_file_name_input', 'parameters.csv'));
    form.appendChild(createTextFormGroup('Data File Name:', 'data_file_name_input', 'data_file_name_input', 'dataset.nc'));

    el.appendChild(form);

    /**
     * Converts the input values from the form into their respective data types.
     * 
     * @returns {Object|null} An object containing the converted input values, or null if an error occurs.
     * 
     * @property {number[]} decay_rates - Array of decay rates as floats.
     * @property {number[]} amplitude - Array of amplitudes as floats.
     * @property {number[]} location - Array of locations as floats.
     * @property {number[]} width - Array of widths as floats.
     * @property {number[]} skewness - Array of skewness values as floats.
     * @property {number} timepoints_max - Maximum number of timepoints as an integer.
     * @property {number} timepoints_stepsize - Step size for timepoints as a float.
     * @property {number} wavelength_min - Minimum wavelength value as a float.
     * @property {number} wavelength_max - Maximum wavelength value as a float.
     * @property {number} wavelength_stepsize - Step size for wavelength as a float.
     * @property {number} stdev_noise - Standard deviation of noise as a float.
     * @property {number} seed - Seed for random number generation as an integer.
     * @property {number} irf_location - Location of the IRF center as a float.
     * @property {number} irf_width - Width of the IRF as a float.
     */
    function convertInputs() {
        try {
            const decay_rates = decay_rates_input.value.split(',').map(parseFloat);
            const amplitude = amplitude_input.value.split(',').map(parseFloat);
            const location = location_input.value.split(',').map(parseFloat);
            const width = width_input.value.split(',').map(parseFloat);
            const skewness = skewness_input.value.split(',').map(parseFloat);
            const timepoints_max = parseInt(timepoints_max_input.value, 10);
            const timepoints_stepsize = parseFloat(timepoints_stepsize_input.value);
            const wavelength_min = parseFloat(wavelength_min_input.value);
            const wavelength_max = parseFloat(wavelength_max_input.value);
            const wavelength_stepsize = parseFloat(wavelength_stepsize_input.value);
            const stdev_noise = parseFloat(stdev_noise_input.value);
            const seed = parseInt(seed_input.value, 10);
            const irf_location = parseFloat(irf_location_input.value);
            const irf_width = parseFloat(irf_width_input.value);

            return { decay_rates, amplitude, location, width, skewness, timepoints_max, timepoints_stepsize, wavelength_min, wavelength_max, wavelength_stepsize, stdev_noise, seed, irf_location, irf_width };
        } catch (error) {
            alert('Error converting inputs: ' + error.message);
            return null;
        }
    }

    /**
     * Validates the input values for the simulation.
     * 
     * @param {Object} inputs - The input values to validate.
     * 
     * @param {number[]} inputs.decay_rates - Array of decay rates as floats.
     * @param {number[]} inputs.amplitude - Array of amplitudes as floats.
     * @param {number[]} inputs.location - Array of locations as floats.
     * @param {number[]} inputs.width - Array of widths as floats.
     * @param {number[]} inputs.skewness - Array of skewness values as floats.
     * @param {number} inputs.wavelength_min - Minimum wavelength value as a float.
     * @param {number} inputs.wavelength_max - Maximum wavelength value as a float.
     * @param {number} inputs.timepoints_max - Maximum number of timepoints as an integer.
     * 
     * @returns {boolean} True if all inputs are valid, otherwise false.
     */
    function validateInputs(inputs) {
        try {
            const { decay_rates, amplitude, location, width, skewness } = inputs;

            if (decay_rates.some(isNaN)) {
                alert('Invalid decay rates');
                return false;
            }
            if (amplitude.some(isNaN)) {
                alert('Invalid amplitudes');
                return false;
            }
            if (location.some(isNaN)) {
                alert('Invalid locations');
                return false;
            }
            if (width.some(isNaN)) {
                alert('Invalid widths');
                return false;
            }
            if (skewness.some(isNaN)) {
                alert('Invalid skewness values');
                return false;
            }

            const lengths = [decay_rates.length, amplitude.length, location.length, width.length, skewness.length];
            if (new Set(lengths).size !== 1) {
                alert('All input lists must have the same length');
                return false;
            }

            if (inputs.wavelength_min >= inputs.wavelength_max || inputs.timepoints_max <= 0) {
                alert('Invalid timepoints or wavelength specification');
                return false;
            }

            return true;
        } catch (error) {
            alert('Validation error: ' + error.message);
            return false;
        }
    }

    const btn = document.createElement("button");
    btn.textContent = 'Simulate';
    btn.addEventListener('click', function(event) {
        event.preventDefault();

        const convertedInputs = convertInputs();
        if (!convertedInputs) return;

        const isValid = validateInputs(convertedInputs);
        if (!isValid) return;

        model.set("decay_rates_input", convertedInputs.decay_rates);
        model.set("amplitude_input", convertedInputs.amplitude);
        model.set("location_input", convertedInputs.location);
        model.set("width_input", convertedInputs.width);
        model.set("skewness_input", convertedInputs.skewness);
        model.set("timepoints_max_input", convertedInputs.timepoints_max);
        model.set("timepoints_stepsize_input", convertedInputs.timepoints_stepsize);
        model.set("wavelength_min_input", convertedInputs.wavelength_min);
        model.set("wavelength_max_input", convertedInputs.wavelength_max);
        model.set("wavelength_stepsize_input", convertedInputs.wavelength_stepsize);
        model.set("stdev_noise_input", convertedInputs.stdev_noise);
        model.set("seed_input", convertedInputs.seed);
        model.set("add_gaussian_irf_input", add_gaussian_irf_input.checked);
        model.set("irf_location_input", convertedInputs.irf_location);
        model.set("irf_width_input", convertedInputs.irf_width);
        model.set("use_sequential_scheme_input", use_sequential_scheme_input.checked);
        model.set("model_file_name_input", model_file_name_input.value);
        model.set("parameter_file_name_input", parameter_file_name_input.value);
        model.set("data_file_name_input", data_file_name_input.value);
        model.set("simulate", self.crypto.randomUUID());

        model.save_changes();
    });
    el.appendChild(btn);
}

export default { render };
