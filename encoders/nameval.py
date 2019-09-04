import json
from numbers import Number

from encoders.base import Encoder as BaseEncoder, RangeSetting as BaseRangeSetting, \
    Setting as BaseSetting, \
    EncoderConfigException, EncoderRuntimeException, \
    SettingConfigException, SettingRuntimeException, q

# Value encoders
class IntToStrValueEncoder:

    @staticmethod
    def encode(value):
        return str(int(value))

    @staticmethod
    def decode(data):
        return int(data)

class FloatToStrValueEncoder:

    @staticmethod
    def encode(value):
        return str(float(value))

    @staticmethod
    def decode(data):
        return float(data)


class BoolToStrValueEncoder:

    @staticmethod
    def encode(value):
        return str(bool(value))

    @staticmethod
    def decode(data):
        if isinstance(data, str):
            return int(data == 'True' or data == 'true')
        return int(data)

class RangeSetting(BaseRangeSetting):
    value_encoder = None
    scale = None

    def __init__(self, name, config=None):
        self.allowed_options.update({'type', 'unit', 'scale'})
        self.name = name
        self.type = config['type']
        super().__init__(config)

        if self.value_encoder is None:
            raise NotImplementedError('You must provide a value encoder for setting {} '
                                      'handled by class {}'.format(q(self.name), self.__class__.__name__))
        
        if self.default is None:
            raise NotImplementedError('You must provide a default value for setting {} '
                                      'handled by class {}'.format(q(self.name), self.__class__.__name__))
        
        self.scale = config.get('scale')
        if self.scale is not None:
            if not isinstance(self.scale, Number):
                raise SettingConfigException('Scale provided for setting {} must be a numeric type. Found: {} "{}"'.format(self.name, self.scale.__class__.__name__, self.scale))
        

    def describe(self):
        retVal = super().describe()
        retVal[1].pop('unit')
        if self.config.get('unit') and self.config['unit'] != '':
            retVal[1]['unit'] = self.config['unit']
        return retVal

    def format_value(self, value):
        return '{}={}'.format(self.name, value)
    
    def get_value_encoder(self):
        if callable(self.value_encoder):
            # pylint: disable=not-callable
            return self.value_encoder()
        return self.value_encoder

    def encode_option(self, value):
        value = self.validate_value(value)
        if self.scale is not None:
            value = value * self.scale
        encoded_value = self.get_value_encoder().encode(value)
        return self.format_value(encoded_value)
    
    def decode_option(self, data):
        if not isinstance(data, dict):
            raise SettingRuntimeException('Unrecognized data type passed on decode_option in nameval encoder setting type: {}. '
                                    'Supported: "dict (parsed multiline file)"'.format(q(data.__class__.__name__)))

        value = data.get(self.name)
        if value is None:
            return self.default
        decoded_value = self.get_value_encoder().decode(value)
        if self.scale is not None:
            return decoded_value / self.scale
        
        return decoded_value

class RangeIntSetting(RangeSetting):
    value_encoder = IntToStrValueEncoder()

class BoolSetting(RangeSetting):
    value_encoder = BoolToStrValueEncoder()
    min = 0
    max = 1
    step = 1

class RangeFloatSetting(RangeSetting):
    value_encoder = FloatToStrValueEncoder()

class EnumSetting(BaseSetting):
    def __init__(self, name, config=None):
        self.allowed_options.update({'values', 'type', 'unit'})
        self.name = name
        self.type = config['type']
        super().__init__(config)

        if not isinstance(self.config.get('values'), list):
            raise SettingConfigException('Incompatible values data provided for setting {} '
                                      'handled by class {}: {}'.format(q(self.name), self.__class__.__name__, self.config.get('values')))

        if self.config.get('default') is None:
            raise SettingConfigException('You must provide a default value for setting {} '
                                      'handled by class {}'.format(q(self.name), self.__class__.__name__))

        if self.config['default'] not in self.config['values']:
            raise SettingConfigException('Default value not contained in values for setting {} '
                                      'handled by class {}'.format(q(self.name), self.__class__.__name__))

    def describe(self):
        descr = {
            'type': self.config['type'],
            'values': self.config['values']
        }
        if self.config.get('unit') and self.config['unit'] != '':
            descr['unit'] = self.config['unit']
        return self.name, descr

    def format_value(self, value):
        return '{}={}'.format(self.name, value)

    def validate_value(self, value):
        if value not in self.config['values']:
            raise SettingRuntimeException('Value provided for setting {} was not contained in configured values. '
                                          'Value: {}.'.format(q(self.name), q(value)))

    def encode_option(self, value):
        self.validate_value(value)
        return self.format_value(value)

    def decode_option(self, data):
        if not isinstance(data, dict):
            raise SettingRuntimeException('Unrecognized data type passed on decode_option in nameval encoder setting type: {}. '
                                    'Supported: "dict (parsed multiline file)"'.format(q(data.__class__.__name__)))

        value = data.get(self.name)
        if value is None:
            return self.config['default']
        return value

# Encoder Class
class Encoder(BaseEncoder):
    # config subsection received is value dict of the 'encoder' key
    def __init__(self, config):
        super().__init__(config)
        self.settings = {} # Dict of { setting_name => instantiated_setting_class }

        requested_settings = self.config.get('settings', {})
        for name, enc_set_config in requested_settings.items():
            set_type = enc_set_config.get('type')
            if set_type is None:
                raise SettingConfigException('No type provided for setting name {} in nameval encoder'.format(name))
            if not isinstance(set_type, str):
                raise SettingConfigException('Value of type must be a string for setting name {} in nameval encoder. Found: {} "{}"'.format(name, set_type.__class__.__name__, set_type))

            frmt_type = set_type.replace('-', ' ').title().replace(' ', '')
            try:
                setting_class = globals()['{}Setting'.format(frmt_type)]
            except KeyError:
                raise EncoderConfigException('Setting type "{}" is not supported in nameval encoder.'.format(set_type))
            self.settings[name] = setting_class(name, enc_set_config)

    def describe(self):
        settings = {}
        for setting in self.settings.values():
            settings.update((setting.describe(),))
        return settings

    def _encode_multi(self, values):
        encoded = ''
        values_to_encode = values.copy()

        encoded += self.config.get('before', '')

        for name, setting in self.settings.items():
            # TODO: should default be encoded here when no value provided?
            val = values_to_encode.pop(name, None)
            if val is None:
                continue
            encoded +=  "{}\n".format(setting.encode_option(val))

        encoded += self.config.get('after', '')

        if values_to_encode:
            raise EncoderRuntimeException('We received settings to encode was not included in the config: {}'
                                          ''.format(', '.join(values_to_encode.keys())))

        return encoded

    def encode_multi(self, values, expected_type=None):
        encoded = self._encode_multi(values)
        expected_type = str if expected_type is None else expected_type
        if expected_type in ('str', str):
            return encoded
        if expected_type in ('list', list):
            return encoded.split('\n')
        raise EncoderConfigException('Unrecognized expected_type passed on encode in nameval encoder: {}. '
                                     'Supported: "list", "str"'.format(q(expected_type)))

    def _decode_multi(self, data):
        decoded = {}
        for name, setting in self.settings.items():
            decoded[name] = setting.decode_option(data)
        
        return decoded

    # Operates on the output of powershell describe script generated by encode_describe of this encoder
    def decode_multi(self, data):
        if not isinstance(data, str):
            raise EncoderRuntimeException('Unrecognized data type passed on decode in nameval encoder: {}. '
                                        'Supported: "str"'.format(q(data.__class__.__name__)))

        # parse lines into dict for more efficient setting decode
        # NOTE: section will need revision to support other setting formats
        data_dict = {}
        for sett_line in data.split('\n'):
            if sett_line == '':
                continue
            sett_tup = sett_line.split('=')
            if len(sett_tup) != 2:
                raise EncoderRuntimeException('Malformed setting line passed on decode in nameval encoder: '
                                        '{}'.format(q(sett_line)))
            
            data_dict[sett_tup[0]] = sett_tup[1]
            
        return self._decode_multi(data_dict)
