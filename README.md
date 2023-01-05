![Alt text](images/Logo.jpg?raw=true "Logo")

# Agamotto

Agamotto is a open-source solution that uses Machine Learning (Computer Vision) to gather insights from physical locations using IoT. It uses Computer Vision to read from cameras using OpenCV and send the data to BigQuery. Then, it's possible to use DataStudio do connect to the table and see the results.

![Alt text](images/example.jpg?raw=true "Example")

## Pre-Requisites

1. GCP - BigQuery and DataStudio (If you want to save)
2. Python 3.7+
3. 2GB+ RAM, 16GB+ GPU (If you want to train) 
4. Available stream device, the default is a webcam (VideoCapture(0))

## How to Use

1. Insert your parameters in agamotto/agamotto.yaml
2. Go to Agamotto's root folder and execute: 

``` shell
pip install --no-cache-dir -r requirements.txt
cd agamotto
python3.7 main.py
```

3. It will download the weights and datasets (if you want to train), this could take up to 30min to 1 hour.
4. If you want to use your own webcam go to the stream folder and execute:

``` shell
pip install --no-cache-dir -r requirements.txt
cd stream
python3.7 main.py
```


