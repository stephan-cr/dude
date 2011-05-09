# Copyright (c) 2011 Stephan Creutz
# Distributed under the MIT License
# See accompanying file LICENSE

'''
this module is about handling of dimensions
'''

import cPickle
import os

import clean
import core

class MetaData:
    '''mimics an 'cfg' object which can be pickled'''

    def __init__(self, cfg):
        self.options = cfg.options
        self.runs = cfg.runs if hasattr(cfg, 'runs') else 1
        self.raw_output_dir = cfg.raw_output_dir

    def save(self, raw_folder):
        '''
        saves metadata of the experiment
        '''

        meta_file = open(raw_folder + '/meta.tmp', 'w')
        cPickle.dump(self, meta_file, 2)
        os.fsync(meta_file)
        meta_file.close()
        os.rename(raw_folder + '/meta.tmp', raw_folder + '/meta')

    def __str__(self):
        return ', '.join([str(attr) for attr in [self.options, self.runs,
                                                 self.raw_output_dir]])

def read_meta(cfg):
    '''
    read metadata from a file, if that fails it returns None
    '''

    meta_file = None
    try:
        meta_file = open(core.get_raw_folder(cfg) + '/meta', 'r')

        return cPickle.load(meta_file)
    except IOError:
        # ignore
        return None
    finally:
        if meta_file is not None:
            meta_file.close()

def list_difference(list_a, list_b):
    '''
    helper function which calculates the difference elements of two lists
    '''

    return list(set(list_a).difference(list_b))

def should_del_exp(experiment, default_values):
    '''
    test whether an experiment should be deleted
    '''

    delete = False
    for key, value in default_values.iteritems():
        if experiment[key] != value:
            delete = True
            break

    return delete

def read_default(cfg, dimensions, text):
    '''
    read default values for dimensions which are going to be added or removed
    '''

    default_values = {}
    for dim in dimensions:
        value = raw_input(text + ' "' + str(dim) + '" ' + \
                              str(cfg.options[dim]) + ': ')
        casted_value = type(cfg.options[dim][0])(value)
        assert casted_value in cfg.options[dim]
        default_values[dim] = casted_value

    return default_values

def update(cfg):
    '''
    updates dimensions when a change in the definition of dimensions
    is detected
    '''

    saved_meta_data = read_meta(cfg)

    if saved_meta_data is not None:
        cfg.options.keys().sort()

        additional_dimensions = list_difference(cfg.options.keys(),
                                                saved_meta_data.options.keys())
        removed_dimensions = list_difference(saved_meta_data.options.keys(),
                                             cfg.options.keys())

        if len(additional_dimensions) > 0 or len(removed_dimensions) > 0:
            add_default_values = {}
            if len(additional_dimensions) > 0:
                # an additional dimension is detected
                print 'the following dimensions are detected to be added:', \
                    str(additional_dimensions)
                old_experiments = core.get_experiments(saved_meta_data)
                add_default_values = \
                    read_default(cfg, additional_dimensions,
                                 'default value for newly detected dimension')

            rem_default_values = {}
            if len(removed_dimensions) > 0:
                # a dimension removal is detected
                print 'the following dimensions are detected to be removed:', \
                    str(removed_dimensions)
                old_experiments = core.get_experiments(saved_meta_data)
                rem_default_values = \
                    read_default(saved_meta_data,
                                 removed_dimensions,
                                 'default value for removed dimension')

            exp_to_clean = []
            old_experiments = core.get_experiments(saved_meta_data)
            for run in range(1, saved_meta_data.runs + 1):
                for old_experiment in old_experiments:
                    old_name = core.get_folder(saved_meta_data,
                                               old_experiment,
                                               run)
                    new_experiment = old_experiment.copy()

                    # delete dimensions
                    for rem_dim in removed_dimensions:
                        del(new_experiment[rem_dim])

                    if should_del_exp(old_experiment, rem_default_values):
                        exp_to_clean.append((run, old_experiment))
                        continue

                    # add dimensions
                    new_experiment.update(add_default_values)

                    new_name = core.get_folder(cfg, new_experiment, run)
                    os.rename(old_name, new_name)

            clean.clean_experiments(saved_meta_data, exp_to_clean)

    MetaData(cfg).save(core.get_raw_folder(cfg))
