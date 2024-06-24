import random
import threading
import time
import json
import common.Api_pb2 as oap_api
from common.Client import Client, ClientEventHandler

from OAP_sensor_data import SENSOR_DATA_DICT


###########
# Config #
##########
CLIENT_NAME = "OAP Sensor Inject"
SENSOR_LIST = [ "ALT", "TEMP_IN", "TEMP_OUT" ]
SENSOR_DICT = {"ALT" : (10) , "TEMP_IN" : (11) , "TEMP_OUT" : (12)}


injecting_active = True
logging = True

###################
# Get Sensor Data #
###################
def get_sensor_data(sensortype, sensordata):
    sensor_json_dict = json.loads(SENSOR_DATA_DICT)
    if logging:
        print(sensor_json_dict, flush= True)
        print(sensortype, flush=True)
    data_list = sensor_json_dict[sensortype]
    if data_list is not None:
        ALT = data_list[0]
        TEMP_IN = data_list[1]
        TEMP_OUT = data_list[2]
        if sensordata == "ALT":
            result = ALT
        elif sensordata == "TEMP_IN":
            result = TEMP_IN
        elif sensordata == "TEMP_OUT":
            result = TEMP_OUT
        return float(result)
    else:
        return 0
    

##############
# OBD Inject #
##############
def inject_obd_gauge_formula_value(client):
    obd_inject_gauge_formula_value = oap_api.ObdInjectGaugeFormulaValue()

    while injecting_active:

        for sensordata, pids in SENSOR_DICT.items():
            print(sensordata, flush=True)

            j = 0
            for i in range(*pids):

                for formula in [("getPidValue("+str(i)+")")]:
                    if logging:
                        print(formula, flush=True)

                    obd_inject_gauge_formula_value.formula = formula
                    sensortype = SENSOR_LIST[j]
                    print(sensortype)
                    datavalue = get_sensor_data(sensortype, sensordata)
                    obd_inject_gauge_formula_value.value = datavalue

                    client.send(oap_api.MESSAGE_OBD_INJECT_GAUGE_FORMULA_VALUE, 0,
                                    obd_inject_gauge_formula_value.SerializeToString())

                    if logging:
                        print("sent to OAP!", flush=True)

                    time.sleep(1)
            j += 1


class EventHandler(ClientEventHandler):

    def on_hello_response(self, client, message):
        print(
            "received hello response, result: {}, oap version: {}.{}, api version: {}.{}"
            .format(message.result, message.oap_version.major,
                    message.oap_version.minor, message.api_version.major,
                    message.api_version.minor))

        threading.Thread(target=inject_obd_gauge_formula_value,
                         args=(client, )).start()


def main():
    event_handler = EventHandler()
    oap_client = Client(CLIENT_NAME)
    oap_client.set_event_handler(event_handler)
    oap_client.connect('127.0.0.1', 44405)

    print("Starting injection...", flush=True)
    active = True
    while active:
        try:
            active = oap_client.wait_for_message()
            if logging:
                print("waiting for api connection")
        except KeyboardInterrupt:
            break

    global injecting_active
    injecting_active = False

    oap_client.disconnect()


if __name__ == "__main__":
    main()