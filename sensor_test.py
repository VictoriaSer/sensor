from conftest import wait
from conftest import SensorInfo
import logging
import pytest

from requests import post

log = logging.getLogger(__name__)
METHOD_ERROR_CODE = -32000
METHOD_ERROR_MSG = "Method execution error"
PARSE_ERROR_CODE = -32700
PARSE_ERROR_MSG = "Parse error"
INVALID_REQUEST_CODE = -32600
INVALID_REQUEST_MSG = "Invalid request"
METHOD_NOT_FOUND_CODE = -32601
METHOD_NOT_FOUND_MSG = "Method not found"
INVALID_PARAMS_CODE = -32602
INVALID_PARAMS_MSG = "Invalid params"


def test_sanity(get_sensor_info, get_sensor_reading):
    sensor_info = get_sensor_info()

    sensor_name = sensor_info.name
    assert isinstance(sensor_name, str), "Sensor name is not a string"

    sensor_hid = sensor_info.hid
    assert isinstance(sensor_hid, str), "Sensor hid is not a string"

    sensor_model = sensor_info.model
    assert isinstance(sensor_model, str), "Sensor model is not a string"

    sensor_firmware_version = sensor_info.firmware_version
    assert isinstance(sensor_firmware_version, int), "Sensor firmware_version is not an int"

    sensor_reading_interval = sensor_info.reading_interval
    assert isinstance(sensor_reading_interval, int), "Sensor reading_interval is not an int"

    sensor_reading = get_sensor_reading()
    assert isinstance(sensor_reading, float), "Sensor doesn't register a temperature"

    
def test_reboot(get_sensor_info, reboot):
    """
    Steps:
        1. Get original sensor info
        2. Reboot sensor
        3. Wait for sensor to come back online
        4. Get current sensor info
        5. Validate, that info from step 1 is equal to the info from step 4
    """

    log.info("Get original sensor info")   
    sensor_info_before_reboot = get_sensor_info()

    log.info("Reboot sensor")
    reboot_response = reboot()
    assert reboot_response == "rebooting", "Sensor did not return expected test in response to the reboot request"

    log.info("Wait for sensor to come back online")
    sensor_info_after_reboot = wait(
        func=get_sensor_info,
        condition=lambda x: isinstance (x, SensorInfo),
        tries=10,
        timeout=1
    )

    log.info("Validate, that info from step 1 is equal to the info from step 4")
    assert sensor_info_before_reboot == sensor_info_after_reboot, "Sensor info after reboot doesn't match sensor info before reboot"
        
       
def test_set_sensor_name(get_sensor_info, set_sensor_name):
    """ 
    1. Set sensor name to "new_name".
    2. Get sensor_info.
    3. Validate that current sensor name matches the name set in Step 1.
    """ 

    updated_name = "new_name"
    log.info(f"Set sensor name to {updated_name}")
    set_sensor_name(updated_name)

    log.info("Get sensor info")
    sensor_info_after_rename = get_sensor_info()

    log.info("Validate that current sensor name matches the name set in Step 1")
    assert sensor_info_after_rename.name == updated_name

def test_set_sensor_reading_interval(get_sensor_info, set_sensor_reading_interval, get_sensor_reading):
    
    """ 
    1. Set sensor reading interval to 1.
    2. Get sensor info.
    3. Validate that sensor reading interval is set to interval from Step 1.
    4. Get sensor reading.
    5. Wait for interval specified in Step 1.
    6. Get sensor reading.
    7. Validate that reading from Step 4 doesn't equal reading from Step 6.
    """ 

    new_interval = 1
    log.info(f"Set sensor reading interval to {new_interval}")
    set_sensor_reading_interval(new_interval)

    log.info("Get sensor info")
    sensor_info_after_resetting_reading_interval = get_sensor_info()

    log.info("Validate that sensor reading interval is set to interval from Step 1")
    assert sensor_info_after_resetting_reading_interval.reading_interval == new_interval

    log.info("Get sensor reading")
    first_sensor_reading_with_new_interval = get_sensor_reading()
    
    log.info("Wait for interval specified in Step 1 and Get sensor reading")
    second_sensor_reading_with_new_interval = wait(
        func=get_sensor_reading,
        condition=lambda x: isinstance (x, dict),
        tries=10,
        timeout=1
    )
    
    log.info("Validate that reading from Step 4 doesn't equal reading from Step 6")
    assert first_sensor_reading_with_new_interval != second_sensor_reading_with_new_interval



# Максимальна версія прошивки сенсора -- 15
def test_update_sensor_firmware(get_sensor_info, update_sensor_firmware):
    """ 
    1. Get original sensor firmware version.
    2. Request firmware update.
    3. Get current sensor firmware version.
    4. Validate that current firmware version is +1 to original firmware version.
    5. Repeat steps 1-4 until sensor is at max_firmware_version - 1.
    6. Update sensor to max firmware version.
    7. Validate that sensor is at max firmware version.
    8. Request another firmware update.
    9. Validate that sensor doesn't update and responds appropriately.
    10. Validate that sensor firmware version doesn't change if it's at maximum value.
    """ 
    
    log.info("1. Get original sensor firmware version")
    sensor_original_firmware_version = get_sensor_info()

    log.info("2. Request firmware update")
    update_sensor_firmware()

    log.info("3. Get current sensor firmware version")
    sensor_current_firmware_version = wait(
            func=get_sensor_info,
            condition=lambda x: isinstance (x, SensorInfo),
            tries=15,
            timeout=1
    )
  
    log.info("4. Validate that current firmware version is +1 to original firmware version")
    assert sensor_current_firmware_version.firmware_version - sensor_original_firmware_version.firmware_version == 1

    log.info("5. Repeat steps 1-4 until sensor is at max_firmware_version - 1")
    max_firmware_version = 15
    current_sensor_state = get_sensor_info()
    current_firmware_version = current_sensor_state.firmware_version
    while current_firmware_version < max_firmware_version:
        update_sensor_firmware()
        updated_firmware_version = wait(
            func=get_sensor_info,
            condition=lambda x: isinstance (x, SensorInfo),
            tries=15,
            timeout=1
        )
        updated_firmware_version = updated_firmware_version.firmware_version
        
        assert updated_firmware_version - current_firmware_version == 1

        current_firmware_version +=1

    log.info("6. Update sensor to max firmware version")
    update_sensor_firmware()

    log.info("7. Validate that sensor is at max firmware version")
    assert current_firmware_version == max_firmware_version

    log.info("8. Request another firmware update")
    update_sensor_firmware()

    log.info("9. Validate that sensor doesn't update and responds appropriately")
    updated_firmware_version = wait(
            func=get_sensor_info,
            condition=lambda x: isinstance (x, SensorInfo),
            tries=15,
            timeout=1
    )
    updated_firmware_version = updated_firmware_version.firmware_version
    if updated_firmware_version == max_firmware_version:
        log.info("Sensor has maximal firmware version")

    
    log.info("10. Validate that sensor firmware version doesn't change if it's at maximum value")
    update_sensor_firmware()
    updated_firmware_version = wait(
            func=get_sensor_info,
            condition=lambda x: isinstance (x, SensorInfo),
            tries=15,
            timeout=1
    )
    updated_firmware_version = updated_firmware_version.firmware_version
    if updated_firmware_version == max_firmware_version:
        log.info("Sensor already has maximal firmware version")


@pytest.mark.parametrize(
        "payload, expected_error_code, expected_error_msg",
        [
            (
                '{"method": "get_methods" "jsonrpc": "2.0", "id": 1}',
                PARSE_ERROR_CODE,
                PARSE_ERROR_MSG,
            ),
            (
                '{"method": "get_method", "jsonrpc": "2.0", "id": 1}',
                METHOD_NOT_FOUND_CODE,
                METHOD_NOT_FOUND_MSG,
            ),
            (
                '{"method": "set_reading_interval", "params": {"reading_interval": 1}, "jsonrpc": "2.0", "id": 1}',
                INVALID_PARAMS_CODE,
                INVALID_PARAMS_MSG
            ),
            (
                '{"method": "set_name", "params": {"name": 1}, "jsonrpc": "2.0", "id": 1}',
                METHOD_ERROR_CODE,
                METHOD_ERROR_MSG,
            ),
            (
                '{"method": "get_reading", "jsonrpc": "20", "id": 1}',
                INVALID_REQUEST_CODE,
                INVALID_REQUEST_MSG,
            )
        ]
)

def test_sensor_errors(
    sensor_host, 
    sensor_port, 
    sensor_pin, 
    payload, 
    expected_error_code, 
    expected_error_msg):
    
    sensor_response = post(
        f"{sensor_host}:{sensor_port}/rpc", 
        data=payload, 
        headers={"authorization": sensor_pin})

    assert (sensor_response.status_code == 200), "Wrong sctatus code from sensor in response to invalid request"

    sensor_response_json = sensor_response.json()
    assert ("error" in sensor_response_json), "Sensor didn't respond with error to invalid request"
    
    error_from_sensor = sensor_response_json["error"]
    
    assert (error_from_sensor.get("code") == expected_error_code), "Sensor didn't respond with correct error code"
    assert (error_from_sensor.get("message") == expected_error_msg), "Sensor didn't respond with correct error message"
    

def test_set_empty_sensor_name(get_sensor_info, set_sensor_name):
    """
    Test Steps:
        1. Get original sensor name.
        2. Set sensor name to an empty string.
        3. Validate that sensor responds with an error.
        4. Get current sensor name.
        5. Validate that sensor name didn't change.
    """
    
    log.info("1. Get original sensor name")
    original_sensor_info = get_sensor_info().name

    log.info("2. Set sensor name to an empty string")
    log.info("3. Validate that sensor responds with an error")
    sensor_response = set_sensor_name("")
    assert sensor_response.get("code") and sensor_response.get("message"), "Sensor response doesn't seem to be an error"
    assert sensor_response.get("code") == METHOD_ERROR_CODE, "Error code doesn't match expected"
    assert sensor_response.get("message") == METHOD_ERROR_MSG, "Error message doesn't match expected"

    log.info("4. Get current sensor name")
    log.info("5. Validate that sensor name didn't change")
    assert original_sensor_info == get_sensor_info().name, "Sensor name was changed, when it should not"


@pytest.mark.parametrize("invalid_interval", [0.4, -1])
def test_set_invalid_sensor_reading_interval(get_sensor_info, set_sensor_reading_interval, invalid_interval):
    """
    Test Steps:
        1. Get original sensor reading interval.
        2. Set interval to < 1
        3. Validate that sensor responds with an error.
        4. Get current sensor reading interval.
        5. Validate that sensor reading interval didn't change.
    """
    log.info("1. Get original sensor reading interval")
    original_sensor_info = get_sensor_info().reading_interval

    log.info("2. Set interval to < 1")
    log.info("3. Validate that sensor responds with an error")
    sensor_response = set_sensor_reading_interval(invalid_interval)
    assert sensor_response.get("code") and sensor_response.get("message"), "Sensor response doesn't seem to be an error"
    assert sensor_response.get("code") == METHOD_ERROR_CODE, "Error code doesn't match expected"
    assert sensor_response.get("message") == METHOD_ERROR_MSG, "Error message doesn't match expected"
        
    log.info("4. Get current sensor reading interval")
    log.info("5. Validate that sensor reading interval didn't change")
    assert original_sensor_info == get_sensor_info().reading_interval, "Sensor reading interval changed but it shouldn't have"