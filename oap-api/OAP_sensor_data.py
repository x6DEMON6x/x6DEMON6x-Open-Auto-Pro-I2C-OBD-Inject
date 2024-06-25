import time
import board
import json
import asyncio

#########################
# Import Sensor Libarys #
#########################
import adafruit_mpl3115a2
import adafruit_ahtx0





##################################################
# Communicating over the board's default I2C bus #
##################################################
i2c = board.I2C()  # uses board.SCL and board.SDA



################
# I2C Adresses #
################
sensorALT = adafruit_mpl3115a2.MPL3115A2(i2c, address=0x60)
sensorTempIN = adafruit_ahtx0.AHTx0(i2c, address=0x38)
sensorTempOUT = adafruit_ahtx0.AHTx0(i2c, address=0x39)


############
# Get Data #
############
while True:

    SENSOR_LIST = [ "ALT", "TEMP_IN", "TEMP_OUT" ]
    SENSOR_DATA_DICT = dict.fromkeys(SENSOR_LIST)

    SENSOR_DATA_DICT["ALT"] = "{0:0.0f}".format(sensorALT.altitude)
    SENSOR_DATA_DICT["TEMP_IN"] = ("%0.1f" % sensorTempIN.temperature)
    SENSOR_DATA_DICT["TEMP_OUT"] = ("%0.1f" % sensorTempOUT.temperature)

    SENSOR_DATA_DICT = json.dumps(SENSOR_DATA_DICT)

    print(json.loads(SENSOR_DATA_DICT))
    time.sleep(1.0)
