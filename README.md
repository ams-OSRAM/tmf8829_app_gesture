# Gesture demo applicaiton - Work in progress

This is a fork of [tmf8829_driver_python](https://github.com/ams-OSRAM/tmf8829_driver_python) modifying tmf8829_driver_python/tmf8829
/zeromq/tmf8829_zeromq_client.py to implement a simple gesture detection application.

Python version 3.10.11 or higher is required.

## Virtual environment

Recommendation is to set-up a virtual environment. Open your favourite Windows PowerShell, VisualStudio Code etc.
To install a virtual environment named env, and use it:   
python -m venv env    
./env/Scripts/Activate.ps1    

## Requirements

To run the scripts in this folder you need to install the packages in the requirements.txt file with:    
pip install -r requirements.txt

All needed python packages are in the subdirectory packages.

## Folder and sub-folders:

### ./tmf8829_driver_python/tmf8829/zeromq/

Location of Python script tmf8829_zeromq_client.py
