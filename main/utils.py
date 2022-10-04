
import requests
import json


def run_request(content, oConnection, addl_options={}):
    addl_options['content'] = content
    addl_options['token'] = oConnection.get_api_token()
    addl_options['format'] = 'json'
    addl_options['returnFormat'] = 'json'
    return requests.post(oConnection.api_url.url, addl_options).json()

study_map = {
    "0": "U54 P1",
    "1": "U54 K23 Ernie",
    "2": "DDNR K23 Schmitt",
    "3": "DDNR RO1 UCLA Carlos",
    "4": "P50",
    "5": "P50 Long",
    "6": "P50 Drug",
    "7": "Hessl RO1",
    "8": "MRIR",
    "9": "MRIDD",
    "10": "NIRS",
    "11": "BIO",
    "12": "DDNR",
    "13": "NIRDD",
}

def get_next_instance_number(oConnection, oInstrument, record_id):
    """
    Look in REDCap to find what the next instance should be for the specified instrument/record_id
    """
    options = {
        'records[0]': str(record_id),
        'forms[1]': oInstrument.instrument_name,
        'fields[1]': 'record_id',
        'events[0]': 'all_measures_arm_1',
    }
    response = run_request("record", oConnection, options)
    max_instance = 0
    for entry in response:
        instance_string = entry["redcap_repeat_instance"]
        if instance_string:
            instance = int(instance_string)
            if instance > max_instance:
                max_instance = instance
    return max_instance + 1

def delete_instrument(oConnection, record_id, instrument_name, repeat_instance):
    options = {
        "action": "delete",
        "records[0]": str(record_id),
        "event": "all_measures_arm_1",
        "instrument": instrument_name,
        "repeat_instance": repeat_instance,
    }
    response = run_request("record", oConnection, options)
    if str(response) == "1":
        return True
    return False

def create_instrument(oConnection, oInstrument, record_id, qStudy):
    instance = get_next_instance_number(oConnection, oInstrument, record_id)
    data = {
        "record_id": str(record_id),
        "redcap_event_name": "all_measures_arm_1",
        "redcap_repeat_instrument": oInstrument.instrument_name,
        "redcap_repeat_instance": str(instance),
    }
    studies_field = oInstrument.studies_field_name
    for oStudy in qStudy:
        data[f"{studies_field}___{oStudy.study_number}"] = "1"
    upload_data = [data]
    upload_data = json.dumps(upload_data)
    print("upl", upload_data)
    response = run_request("record", oConnection, {"data": upload_data})
    return instance, response

