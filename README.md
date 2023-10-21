# Lahipalvelujen saavutettavuus
This repo contains Python scripts for project 319456 "Lähipalvelujen saavutettavuus seurantatyökalu".

## Usage
Analysis run is executed with `main.py`. 
External data paths are stored in `config.json`.
Results are written to `./results/`.

### Setup
We are using Python 3.12 and `pipenv` to isolate our environment from the other global Python modules and makes sure we don't break anything with our setup.

To activate this project's virtualenv, `pipenv shell`. At this point analysis uses packages `pandas`, `NumPy`, `geopandas`, `OSMnx` and depedencies. If you want to add new pakcges to pipenv use command `pipenv install [package_name]`.

## Authors

**Atte Supponen**, [atte-wsp](https://github.com/atte-wsp)
**Abdulrahman Al-Metwali**, [abdulrr](https://github.com/abrulrr)
