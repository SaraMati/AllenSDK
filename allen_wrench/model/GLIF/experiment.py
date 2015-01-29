import numpy as np
#import matplotlib.pyplot as plt
import neuron
from os import remove
import json
import copy
import warnings

class GLIFExperiment( object ):
    def __init__(self, neuron, dt, stim_list, spike_time_steps, 
                 grid_spike_times, interpolated_spike_times, 
                 grid_spike_voltages, interpolated_spike_voltages, 
                 init_voltage, init_threshold, init_AScurrents, 
                 target_spike_mask, param_fit_names,
                 **kwargs):

        self.neuron = neuron
        self.dt = dt
        self.stim_list = stim_list
        self.spike_time_steps = spike_time_steps
        self.grid_spike_times = grid_spike_times
        self.interpolated_spike_times = interpolated_spike_times
        self.grid_spike_voltages = grid_spike_voltages,
        self.interpolated_spike_voltages = interpolated_spike_voltages
        self.init_voltage = init_voltage
        self.init_threshold = init_threshold
        self.init_AScurrents = init_AScurrents
        self.target_spike_mask = target_spike_mask
        self.param_fit_names = param_fit_names

        self.spike_errors = []

        assert len(self.init_AScurrents) == len(self.neuron.tau), Exception("init_AScurrents length (%d) must have same length as tau (%d)" % (len(self.init_AScurrents), len(self.neuron.tau)))
        
    def run(self, param_guess):
        '''This code will run the loaded neuron model in reference to the target neuron spikes.
        inputs:
            self: is the instance of the neuron model and parameters alone with the values of the target spikes.
                NOTE the values in each array of the self.gridSpikeIndexTarge_list and the self.interpolated_spike_times
                are in reference to the time start of of the stim in each induvidual array (not the universal time)
            param_guess: array of scalars of the values that will be inserted into the mapping function below.
        returns:
            voltage_list: list of array of voltage values. NOTE: IF THE MODEL NEURON SPIKES BEFORE THE TARGET THE VOLTAGE WILL 
                NOT BE CALCULATED THEREFORE THE RESULTING VECTOR WILL NOT BE AS LONG AS THE TARGET AND ALSO WILL NOT 
                MAKE SENSE WITH THE STIMULUS UNLEtarget_spike_maskSS YOU CUT IT AND OUTPUT IT TOO.
            grid_spike_times_list:
            interpolated_spike_time_list: an array of the actual times of the spikes. NOTE: THESE TIMES ARE CALCULATED BY ADDING THE 
                TIME OF THE INDIVIDUAL SPIKE TO THE TIME OF THE LAST SPIKE.
            gridISIFromLastTargSpike_list: list of arrays of spike times of the model in reference to the last target (biological) 
                spike (not in reference to sweep start)
            interpolatedISIFromLastTargSpike_list: list of arrays of spike times of the model in reference to the last target (biological) 
                spike (not in reference to sweep start)
            voltageOfModelAtGridBioSpike_list: list of arrays of scalars that contain the voltage of the model neuron when the target or bio neuron spikes.    
            theshOfModelAtGridBioSpike_list: list of arrays of scalars that contain the threshold of the model neuron when the target or bio neuron spikes.'''

        self.set_neuron_parameters(param_guess)    
        self.spike_errors = []

        run_data = []
        
        for stim_list_index in xrange(len(self.stim_list)):
            run_data.append(self.neuron.run_with_spikes(self.init_voltage, self.init_threshold, self.init_AScurrents, 
                                                        self.stim_list[stim_list_index], 
                                                        self.spike_time_steps[stim_list_index], 
                                                        self.interpolated_spike_times[stim_list_index],
                                                        self.interpolated_spike_voltages[stim_list_index]))

        return {
            'voltage': [ rd['voltage'] for rd in run_data ],
            'threshold': [ rd['threshold'] for rd in run_data ],
            'AScurrent_matrix': [ rd['AScurrent_matrix'] for rd in run_data ],
            'grid_spike_times': [ rd['grid_spike_times'] for rd in run_data ],
            'interpolated_spike_times': [ rd['interpolated_spike_times'] for rd in run_data ],
            'grid_ISI': [ rd['grid_ISI'] for rd in run_data ],
            'interpolated_ISI': [ rd['interpolated_ISI'] for rd in run_data ],
            'grid_spike_voltage': [ rd['grid_spike_voltage'] for rd in run_data ],
            'interpolated_spike_voltage': [ rd['interpolated_spike_voltage'] for rd in run_data ],
            'grid_spike_threshold': [ rd['grid_spike_threshold'] for rd in run_data ],
            'interpolated_spike_threshold': [ rd['interpolated_spike_threshold'] for rd in run_data ]
        }


    def run_base_model(self, param_guess):
        '''This code will run the loaded neuron model.
        inputs:
            self: is the instance of the neuron model and parameters alone with the values of the target spikes.
                NOTE the values in each array of the self.gridSpikeIndexTarge_list and the self.interpolated_spike_times
                are in reference to the time start of of the stim in each induvidual array (not the universal time)
            param_guess: array of scalars of the values that will be inserted into the mapping function below.
        returns:
            voltage_list: list of array of voltage values. NOTE: IF THE MODEL NEURON SPIKES BEFORE THE TARGET THE VOLTAGE WILL 
                NOT BE CALCULATED THEREFORE THE RESULTING VECTOR WILL NOT BE AS LONG AS THE TARGET AND ALSO WILL NOT 
                MAKE SENSE WITH THE STIMULUS UNLEtarget_spike_maskSS YOU CUT IT AND OUTPUT IT TOO.
            gridTime_list:
            interpolatedTime_list: an array of the actual times of the spikes. NOTE: THESE TIMES ARE CALCULATED BY ADDING THE 
                TIME OF THE INDIVIDUAL SPIKE TO THE TIME OF THE LAST SPIKE.
            grid_ISI_list: list of arrays of spike times of the model in reference to the last target (biological) 
                spike (not in reference to sweep start)
            interpolated_ISI_list: list of arrays of spike times of the model in reference to the last target (biological) 
                spike (not in reference to sweep start)
            grid_spike_voltage_list: list of arrays of scalars that contain the voltage of the model neuron when the target or bio neuron spikes.    
            grid_spike_threshold_list: list of arrays of scalars that contain the threshold of the model neuron when the target or bio neuron spikes.'''

        
        stim_list = self.stim_list
        
        self.set_neuron_parameters(param_guess)    
        self.spike_errors = []
        
        run_data = []

        for stim_list_index in xrange(len(stim_list)):
            run_data.append(self.neuron.run(self.init_voltage, self.init_threshold, self.init_AScurrents, stim_list[stim_list_index]))

          
        return {
            'voltage': [ rd['voltage'] for rd in run_data ],
            'threshold': [ rd['threshold'] for rd in run_data ],
            'AScurrent_matrix': [ rd['AScurrent_matrix'] for rd in run_data ],
            'grid_spike_times': [ rd['grid_spike_times'] for rd in run_data ],
            'interpolated_spike_times': [ rd['interpolated_spike_times'] for rd in run_data ],
            'spike_time_steps': [ rd['spike_time_steps'] for rd in run_data ],
            'interpolated_spike_voltage': [ rd['interpolated_spike_voltage'] for rd in run_data ],
            'interpolated_spike_threshold': [ rd['interpolated_spike_threshold'] for rd in run_data ]
        }

    def neuron_parameter_count(self):
        count = 0
        for fit_name in self.param_fit_names:
            try:
                coeff = self.neuron.coeffs[fit_name]
            except KeyError:
                logging.error("Neuron coefficient %s does not exist" % fit_name)
                raise

            # is it a list?
            try:
                # this will throw a type error if 'coeff' is a scalar
                coeff_size = len(coeff)
                count += coeff_size
            except TypeError:
                count += 1
        return count

    def set_neuron_parameters(self, param_guess): 
        '''Maps the parameter guesses to the attributes of the model.  
        input:
            param_guess is vector of values.  It is assumed that the length will be '''

        index = 0
        for fit_name in self.param_fit_names:
            try:
                coeff = self.neuron.coeffs[fit_name]
            except KeyError:
                logging.error("Neuron coefficient %s does not exist" % fit_name)
                raise

            # is it a list?
            try:
                # this will throw a type error if 'coeff' is a scalar
                coeff_size = len(coeff)
                self.neuron.coeffs[fit_name] = param_guess[index:index+coeff_size]
                index += coeff_size
            except TypeError:
                self.neuron.coeffs[fit_name] = param_guess[index]
                index += 1

