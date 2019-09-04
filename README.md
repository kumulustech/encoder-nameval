# encoder-nameval

Plug-in `name=value` settings encoder for servo

## Usage

To be included in `/servo/encoders/` folder on servo host. 
Further packaging steps can be found in the repo `opsani/servo`.

## Available settings and their defaults

The available settings within this encoder are derived from the encoder's config section of config.yaml (see config.yaml.example for usage)

Each setting contains a `type` property which determines its behaviour as well as the acceptable values from config.
More specifically, the value of type is used to dynamically instantiate a setting class definition
corresponding to the name of the type then perform validation as well as conversion of values to and from the strings of adjust output. 
The required properties for each setting type/class is validated by it's respective init and/or check_config methods

Additionally, the `default` property is required for all settings and is returned when there is no data to be decoded

The following types of settings are available to define:

- `enum`: Value of arbitrary type and definition, can only be one of the specified `values`
  - `values`: List of acceptable values for this setting
- `bool`: Boolean value, converts integer input from driver to string of "True" and "False"
- `range-int` and `range-float`: Settings for Integer and Floating point values respectively
  - All range types require the additional properties:
    - `min`: Minumum value
    - `max`: Maximum value
    - `step`: Minimum unit of change
  - In some cases, it may be desirable to scale the adjustment input(eg. a decimal input to an integer number of megabytes). The `scale` property may be included for this purpose so long as it is a numeric type

The `unit` property may also be included but does not have meaningful influence on encoder logic. It is simply a human readable label included in the describe
 output

See encoded.example for example adjust output

## How to run tests

Prerequisites:

- Python 3.5 or higher
- PyTest 4.3.0 or higher

Follow these steps: (NOTE: small tweaks have been made to the base.py herein that should be backwards compatible)

1. Pull the repository
1. Copy/symlink `base.py` from `https://github.com/opsani/servo/tree/master/encoders` to folder `encoders/`
1. Copy/symlink config.yaml.example to config.yaml
1. Run `pytest` from the root folder
