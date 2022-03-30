# DuckToolkit
Encoding Tools for Rubber Ducky. 
The duck tools are available in the browser at [ducktoolkit.com](https://ducktoolkit.com). From here you can also generate payloads from a selection of predefined scripts and templates.

## Disclaimer

*The Duck Toolkit is an open source Penetration Testing tool for authorized network auditing and security analysis purposes only where permitted. Users are solely responsible for compliance with all laws of their locality. The Duck Toolkit software developers and affiliates claim no responsibility for unauthorized or unlawful use.*

## Installation

Download the release and install with ```python setup.py install``` Or ```sudo pip install --upgrade ducktoolkit```

There are no external dependencies other than python.
This has been tested on Ubuntu and Windows 10

## Usage

The DuckToolkit is provided with a script that will allow you to easily [encode and decode your files](https://github.com/readloud/DuckToolkit/wiki). 

### Encode

To encode point the script at your duckcode.txt file, select an output and a language as show in the example below:

```ducktools.py -e -l gb /path/to/duck_text.txt /path/to/output.bin```

### Decode

To decode point the script at your inject.bin file, select an output and a language as show in the example below:

```ducktools.py -d -l gb /path/to/inject.bin /path/to/output.txt```

### Library

The toolkit is python 3 compatible and can also be imported as a library. 

```
from ducktoolkit import encoder

duck_text = 'STRING Hello'
language = 'gb'
duck_bin = encoder.encode_script(duck_text, language)
```


## Limitations

The encoder can only deal with certain Command keys and key combinations. Please see for details on [supported commands](https://usbrubberducky.com). 

The decoder is a best effort decoder. It will attempt to restore all command keys and strings. But its a lot harder going backwards. You will NOT be able to generate 
a valid duck script from an inject.bin


## ToDo

- Support more keyboard layouts / languages.
- Improve the decoder.
- Pip Installation

> References

github.com/adamcaudill/Psychson
github.com/brandonlw/Psychson
github.com/flowswitch/phison
github.com/hak5darren/USB-Rubber-Ducky/wiki
