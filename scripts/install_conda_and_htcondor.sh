#!/usr/bin/env bash
# This script is used to install conda and htcondor on macos for local development
set -x

brew install --cask miniconda
/opt/homebrew/bin/conda create -y -n py3115 python=3.11.5
/opt/homebrew/bin/conda env list
/opt/homebrew/bin/conda update -n base -c defaults conda
/opt/homebrew/bin/conda install -c conda-forge python-htcondor


export PATH=/opt/homebrew/Caskroom/miniconda/base/envs/py3115/bin:$PATH
export PYTHONPATH=/opt/homebrew/Caskroom/miniconda/base/envs/py3115/lib/python3.11/site-packages:$PYTHONPATH
export PYTHONPATH=/opt/homebrew/Caskroom/miniconda/base/lib/python3.11/site-packages:$PYTHONPATH

# Need to add this path into pycharm interpreter PYTHONPATH as well

pip install poetry
poetry config virtualenvs.create false
poetry update
pip install fastapi==0.104.1
pip install uvicorn==0.23.2
pip install pysocks==1.7.1
pip install httpx==0.18.2
pip install pytest==6.2.5
