# Lahipalvelujen saavutettavuus
This repo contains Python scripts for project 319456 "Lähipalvelujen saavutettavuus seurantatyökalu".

## Usage
Analysis run is executed with `main.py`. 
External data paths are stored in `config.json`.
Results are written to `./results/`.

### Setup
The repository is built with Python 3.10. Analysis uses packages `pandas`, `NumPy`, `geopandas`, `OSMnx`, `yaml` and depedencies.

We are using `conda` to manage packages and virtual environment. Conda is used as it is recommended way of installing `OSMnx` and dependencies.

Environment can be set up following way:
1. Conda is installed via installing Anaconda or Miniconda Python distributions. Recommeded to download and install Miniconda for Python 3.10. 
2. Open Anaconda Promt and type `conda init powershell` to enable conda in PowerShell, if you want to run scripts in VScode or PowerShell (recommended).
3. Install conda environment with osmnx and other packages with command `conda create -n ox -c conda-forge --strict-channel-priority osmnx networkx pyyaml pygrio`.
4. Now you can activate conda enviroment with `conda activate ox`.


## Authors

**Atte Supponen**, [atte-wsp](https://github.com/atte-wsp)
**Abdulrahman Al-Metwali**, [abdulrr](https://github.com/abrulrr)
