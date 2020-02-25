import pytest

import os
import importlib
import yaml
import json

import encoders.base as enc
from encoders.base import q, EncoderConfigException, \
    SettingConfigException, \
    SettingRuntimeException

config_path = os.environ.get('OPTUNE_CONFIG', './config.yaml')

def load_config():
    try:
        config = yaml.safe_load(open(config_path))
    except yaml.YAMLError as e:
        raise EncoderConfigException('Could not parse config file located at "{}". '
                        'Please check its contents. Error: {}'.format(config_path, str(e)))
    return validate_config(config)

def validate_config(config):
    try:
        enc_config = config['ec2win']['web']['encoder']
    except KeyError:
        raise EncoderConfigException("Unable to locate encoder config subsection in config file {}".format(config_path))


    if not isinstance(enc_config, dict):
        raise EncoderConfigException('Configuration object for dotnet encoder not found')
    if not enc_config.get('name'):
        raise EncoderConfigException('No encoder name specified')
    
    return enc_config

def load_encoder(encoder):
    if isinstance(encoder, str):
        try:
            return importlib.import_module('encoders.{}'.format(encoder)).Encoder
        except ImportError:
            raise ImportError('Unable to import encoder {}'.format(q(encoder)))
        except AttributeError:
            raise AttributeError('Were not able to import encoder\'s class from encoders.{}'.format(encoder))
    return encoder

def write_test_output_file(fname, data):
    fext = '.json' if isinstance(data, dict) else '.txt'
    f = open('output_{}{}'.format(fname, fext), 'w')
    if fext == '.json':
        json.dump(data, f)
    else:
        f.write(data)

    f.close()

decode_input = '''\
BoolStringSettingA=False
BoolNumSettingB=1
EnumSettingC=val3
RangeIntSettingD=16
RangeMBSettingE=2560
RangeFloatSettingF=0.25
'''

encode_input = {
    "application": {
        "components": {
            "web": {
                "settings": {
                    "BoolStringSettingA": {"value": 0},
                    "BoolNumSettingB": {"value": 1},
                    "EnumSettingC": {"value": "val2"},
                    "RangeIntSettingD": {"value": 32},
                    "RangeMBSettingE": {"value": 1.5},
                    "RangeFloatSettingF": {"value": 0.75},
                }
            }
        }
    }
}

def test_describe():
    enc_config = load_config()
    described = enc.describe(enc_config, decode_input)
    write_test_output_file('test_describe', described)
    assert True

def test_describe_no_input():
    enc_config = load_config()
    described = enc.describe(enc_config, '')
    write_test_output_file('test_describe_no_input', described)
    assert True

def test_encode():
    enc_config = load_config()
    encoded = enc.encode(enc_config, encode_input['application']['components']['web']['settings'])
    print(encoded)
    write_test_output_file('test_encode', encoded[0])
    assert True

# def test_describe():
#     enc_config = load_config()
#     encoder_klass = load_encoder(enc_config['name'])
#     encoder = encoder_klass(enc_config)
#     settings = encoder.describe()
#     write_test_output_file('test_describe', settings)
#     # TODO: implement test
#     assert True

# def test_encode_multi():
#     enc_config = load_config()
#     encoder_klass = load_encoder(enc_config['name'])
#     encoder = encoder_klass(enc_config)
#     settings = encoder.describe()
#     encodable = {name: encode_input['application']['components']['web']['settings'].get(name, {}).get('value') for name in settings.keys()}
#     config_expected_type = enc_config.get('expected_type')
#     encoded = encoder.encode_multi(encodable, expected_type=config_expected_type)
#     write_test_output_file('test_encode_multi', encoded)
#     # TODO: implement test
#     assert True

# def test_decode_multi():
#     enc_config = load_config()
#     encoder_klass = load_encoder(enc_config['name'])
#     encoder = encoder_klass(enc_config)
#     decoded = encoder.decode_multi(decode_input)
#     write_test_output_file('test_decode_multi', decoded)
#     # TODO: implement test
#     assert True