# encoder-nameval
Plug-in `name=value` settings encoder for servo

# Usage
To be included in `/servo/encoders/` folder on servo host. 
Further packaging steps can be found in the repo `opsani/servo`.

# Available settings and their defaults

The available settings within this encoder are derived from the encoder's config section of config.yaml (see config.yaml.example)

Each setting contains a `type` property which determines its behaviour as well as the acceptable values from config.
More specifically, the value of type (and certain config properties) is used to dynamically instantiate a setting class definition
corresponding to the name of the type then perform validation as well as conversion of values to and from the strings of adjust output 

Additionally, the `default` property is required for all settings to be returned when there is no data to be decoded

The following types of settings are available to define:

- `range`: Numeric value, requires additional properties:
  - `min`: Minumum value
  - `max`: Maximum value
  - `step`: Minimum unit of change
  - `value_type`: type of encoded value: int(default) or bool
- `enum`
  - `values`: List of acceptable values for this setting

The required properties for each setting type/class is validated by it's respective check_config method

The `unit` property may also be included. Initially it will only inform the describe output, but subclasses of the generic setting
types can be defined to add more nuanced behaviour (eg. a setting type that converts gigabytes represented by a decimal number to an integer number of megabytes)

See encoded.example for example adjust output

# How to run tests
Prerequisites:
* Python 3.5 or higher
* PyTest 4.3.0 or higher

Follow these steps: (NOTE: small tweaks have been made to the base.py herein that should be backwards compatible)
1. Pull the repository
2. Copy/symlink `base.py` from `https://github.com/opsani/servo/tree/master/encoders` to folder `encoders/`
3. Run `pytest` from the root folder
