# elki_interface
An example of how one could realize a python interface for the ELKI datamining tool.

This is not a wrapper, just a CLI with a few python-esque bells and whistles.

At most, it is an example of how one could go about building a clean python interface from python to the ELKI CLI. Currently this project only exposes the HiCS method for outlier detection.

## Cite

**I am in no way affiliated with the developers of the ELKI tool. All credit goes to them.**

Cf. [https://elki-project.github.io/](https://elki-project.github.io/) for the official ELKI website. Should you use this tool, please follow the instructions on the ELKI website of how and what to cite!

## Usage

For a local install, `cd` to the root of this repository and simply; 

```
python setup.py develop
```
