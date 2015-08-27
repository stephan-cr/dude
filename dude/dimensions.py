# Copyright (c) 2011, 2012, 2013, 2014, 2015 Stephan Creutz
# Distributed under the MIT License
# See accompanying file LICENSE

'''
this module is about handling of dimensions
'''

import cPickle
import os

import clean
import core

META_FILE = 'dude.meta'

class MetaData:
    '''mimics an 'cfg' object which can be pickled'''

    def __init__(self, cfg):
        self.optspace = cfg.optspace
        self.raw_output_dir = cfg.raw_output_dir

    def save(self, raw_folder):
        '''
        saves metadata of the experiment
        '''

        meta_tmp = 'meta-%d.tmp' % os.getpid()
        with open(os.path.join(raw_folder, meta_tmp), 'wb') as meta_file:
            cPickle.dump(self, meta_file, cPickle.HIGHEST_PROTOCOL)
            os.fsync(meta_file)

        os.rename(os.path.join(raw_folder, meta_tmp),
                  os.path.join(raw_folder, META_FILE))

    def __str__(self):
        return ', '.join([str(attr) for attr in [self.optspace,
                                                 self.raw_output_dir]])

def read_meta(cfg):
    '''
    read metadata from a file, if that fails it returns None
    '''

    meta_file = None
    try:
        meta_file = open(os.path.join(core.get_raw_folder(cfg), META_FILE), 'rb')

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
                              str(cfg.optspace[dim]) + ': ')
        casted_value = type(cfg.optspace[dim][0])(value)
        assert casted_value in cfg.optspace[dim]
        default_values[dim] = casted_value

    return default_values

def update(cfg):
    '''
    updates dimensions when a change in the definition of dimensions
    is detected
    '''

    saved_meta_data = read_meta(cfg)

    if saved_meta_data is not None:
        cfg.optspace.keys().sort()

        additional_dimensions = list_difference(cfg.optspace.keys(),
                                                saved_meta_data.optspace.keys())
        removed_dimensions = list_difference(saved_meta_data.optspace.keys(),
                                             cfg.optspace.keys())

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
            for old_experiment in old_experiments:
                old_name = core.get_folder(saved_meta_data,
                                           old_experiment)
                new_experiment = old_experiment.copy()

                # delete dimensions
                for rem_dim in removed_dimensions:
                    del(new_experiment[rem_dim])

                if should_del_exp(old_experiment, rem_default_values):
                    exp_to_clean.append(old_experiment)
                    continue

                # add dimensions
                new_experiment.update(add_default_values)

                new_name = core.get_folder(cfg, new_experiment)
                os.rename(old_name, new_name)

            clean.clean_experiments(saved_meta_data, exp_to_clean)

    MetaData(cfg).save(core.get_raw_folder(cfg))



def check_cfg(cfg):
    """
    Verifies if loaded configuration file has fields necessary for
    this module.
    """
    assert hasattr(cfg, 'dude_version')
    assert getattr(cfg, 'dude_version') >= 3

    assert hasattr(cfg, 'optspace')
    assert type(cfg.optspace) == dict

    assert hasattr(cfg, 'raw_output_dir')
