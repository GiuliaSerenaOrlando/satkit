import sys
from contextlib import closing
from enum import Enum
from pathlib import Path
from typing import Union

from strictyaml import (Bool, Float, Int, Map, Optional, ScalarValidator, Seq,
                        Str, YAMLError, load)

config = {}
data_run_params = {}
gui_params = {}

# This is where we store the metadata needed to write out the configuration and
# possibly not mess up the comments in it.
_raw_config_dict = {}
_raw_data_run_params_dict = {}
_raw_gui_params_dict = {}

class Datasource(Enum):
    aaa = 'AAA'
    rasl = 'RASL'

class DatasourceValidator(ScalarValidator):
    """
    Validate yaml representing a Path.
    
    Please note that empty fields are interpeted as not available and
    represented by None. If you want to specify current working directory, use
    '.'
    """
    def validate_scalar(self, chunk):
        if chunk.contents:
            try:
                return Datasource(chunk.contents)
            except ValueError:
                values = [ds.value for ds in Datasource]
                print(f"Error. Only following values for data source are recognised: {str(values)}")
                raise
        else:
            return None

class PathValidator(ScalarValidator):
    """
    Validate yaml representing a Path.
    
    Please note that empty fields are interpeted as not available and
    represented by None. If you want to specify current working directory, use
    '.'
    """
    def validate_scalar(self, chunk):
        if chunk.contents:
            return Path(chunk.contents)
        else:
            return None

def load_config(filepath: Union[Path, str, None]=None) -> None:
    """
    Read the config file from filepath and recursively the other config files.
    
    If filepath is None, read from the default file
    'configuration/configuration.yaml'. In both cases if the file does not
    exist, report this and exit.
    """
    load_main_config(filepath)
    load_run_params(config['data run parameter file'])
    load_gui_params(config['gui parameter file'])


def load_main_config(filepath: Union[Path, str, None]=None) -> None:
    """
    Read the config file from filepath.
    
    If filepath is None, read from the default file
    'configuration/configuration.yaml'. In both cases if the file does not
    exist, report this and exit.
    """
    if filepath is None:
        filepath = Path('configuration/configuration.yaml')
    elif isinstance(filepath, str):
        filepath = Path(filepath)

    global config
    global _raw_config_dict

    if filepath.is_file():
        with closing(open(filepath, 'r')) as yaml_file:
            schema = Map({
                "epsilon": Float(),
                "mains frequency": Float(),
                "data run parameter file": PathValidator(),
                "gui parameter file": PathValidator()
                })
            try:
                _raw_config_dict = load(yaml_file.read(), schema)
            except YAMLError as error:
                print(f"Fatal error in reading {filepath}:")
                print(error)
                sys.exit()
    else:
        print(f"Didn't find {filepath}. Exiting.".format(str(filepath)))
        sys.exit()
    config.update(_raw_config_dict.data)

def load_run_params(filepath: Union[Path, str, None]=None) -> None:
    """
    Read the config file from filepath.
    
    If filepath is None, read from the default file
    'configuration/configuration.yaml'. In both cases if the file does not
    exist, report this and exit.
    """
    if filepath is None:
        print(f"Fatal error in reading {filepath}:")
        print(error)
        sys.exit()
    elif isinstance(filepath, str):
        filepath = Path(filepath)

    global data_run_params
    global _raw_data_run_params_dict

    if filepath.is_file():
        with closing(open(filepath, 'r')) as yaml_file:
            schema = Map({
                "data properties": Map({
                    "data source": DatasourceValidator(), 
                    "exclusion list": PathValidator(), 
                    "pronunciation dictionary": PathValidator(),
                    "speaker id": Str(), 
                    "data directory": PathValidator(), 
                    Optional("wav directory"): PathValidator(), 
                    Optional("textgrid directory"): PathValidator(), 
                    Optional("ultrasound directory"): PathValidator(), 
                    Optional("output directory"): PathValidator()
                    }), 
                "flags": Map({
                    "detect beep": Bool(),
                    "test": Bool(),
                    "cast flags": Map({
                        "only words": Bool(),
                        "file": Bool(),
                        "utterance": Bool()})
                    })
                })
            try:
                _raw_data_run_params_dict = load(yaml_file.read(), schema)
            except YAMLError as error:
                print(f"Fatal error in reading {filepath}:")
                print(error)
                sys.exit()
    else:
        print(f"Didn't find {filepath}. Exiting.".format(str(filepath)))
        sys.exit()
    data_run_params.update(_raw_data_run_params_dict.data)

def load_gui_params(filepath: Union[Path, str, None]=None) -> None:
    """
    Read the config file from filepath.
    
    If filepath is None, read from the default file
    'configuration/configuration.yaml'. In both cases if the file does not
    exist, report this and exit.
    """
    if filepath is None:
        print(f"Fatal error in reading {filepath}:")
        print(error)
        sys.exit()
    elif isinstance(filepath, str):
        filepath = Path(filepath)

    global gui_params
    global _raw_gui_params_dict

    if filepath.is_file():
        with closing(open(filepath, 'r')) as yaml_file:
            schema = Map({
                "data/tier height ratios": Map({
                    "data": Int(), 
                    "tier": Int()
                    }),
                "data axes": Seq(Str()),
                "pervasive tiers": Seq(Str())
                })
            try:
                _raw_gui_params_dict = load(yaml_file.read(), schema)
            except YAMLError as error:
                print(f"Fatal error in reading {filepath}:")
                print(error)
                sys.exit()
    else:
        print(f"Didn't find {filepath}. Exiting.".format(str(filepath)))
        sys.exit()
    gui_params.update(_raw_gui_params_dict.data)