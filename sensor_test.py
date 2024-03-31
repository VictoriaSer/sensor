from conftest import wait

def test_sanity(get_sensor_info, get_sensor_reading):
    sensor_info = get_sensor_info()

    sensor_name = sensor_info.get("name")
    assert isinstance(sensor_name, str), "Sensor name is not a string"

    sensor_hid = sensor_info.get("hid")
    assert isinstance(sensor_hid, str), "Sensor hid is not a string"

    sensor_model = sensor_info.get("model")
    assert isinstance(sensor_model, str), "Sensor model is not a string"

    sensor_firmware_version = sensor_info.get("firmware_version")
    assert isinstance(sensor_firmware_version, int), "Sensor firmware_version is not an int"

    sensor_reading_interval = sensor_info.get("reading_interval")
    assert isinstance(sensor_reading_interval, int), "Sensor reading_interval is not an int"

    sensor_reading = get_sensor_reading()
    assert isinstance(sensor_reading, float), "Sensor doesn't register a temperature"

    print ("Sanity test passed")

def test_reboot(get_sensor_info, reboot):
    """
    Steps:
        1. Get original sensor info
        2. Reboot sensor
        3. Wait for sensor to come back online
        4. Get current sensor info
        5. Validate, that info from step 1 is equal to the info from step 4
    """

    print("Get original sensor info")   
    sensor_info_before_reboot = get_sensor_info()

    print("Reboot sensor")
    reboot_response = reboot()
    assert reboot_response == "rebooting", "Sensor did not return expected test in response to the reboot request"

    print ("Wait for sensor to come back online")
    sensor_info_after_reboot = wait(
        func=get_sensor_info,
        condition=lambda x: isinstance (x, dict),
        tries=10,
        timeout=1
    )

    print("Validate, that info from step 1 is equal to the info from step 4")
    assert sensor_info_before_reboot == sensor_info_after_reboot, "Sensor info after reboot doesn't match sensor info before reboot"
        
        
def test_set_sensor_name(get_sensor_info, set_sensor_name):
    """
    1. Set sensor name to "new_name".
    2. Get sensor_info.
    3. Validate that current sensor name matches the name set in Step 1.
    """

    print('Set sensor name to "new_name"')
    updated_name = "new_name"
    set_sensor_name(updated_name)

    print("Get sensor info")
    sensor_info_after_rename = get_sensor_info()

    print("Validate that current sensor name matches the name set in Step 1")
    assert sensor_info_after_rename.get("name") == updated_name


def test_set_sensor_reading_interval(
    get_sensor_info, set_sensor_reading_interval, get_sensor_reading
):
    """
    1. Set sensor reading interval to 1.
    2. Get sensor info.
    3. Validate that sensor reading interval is set to interval from Step 1.
    4. Get sensor reading.
    5. Wait for interval specified in Step 1.
    6. Get sensor reading.
    7. Validate that reading from Step 4 doesn't equal reading from Step 6.
    """

    print("Set sensor reading interval to 1")
    new_interval = 1
    set_sensor_reading_interval(new_interval)

    print("Get sensor info")
    sensor_info_after_resetting_reading_interval = get_sensor_info()

    print("Validate that sensor reading interval is set to interval from Step 1")
    assert sensor_info_after_resetting_reading_interval.get("reading_interval") == new_interval

    print("Get sensor reading")
    first_sensor_reading_with_new_interval = get_sensor_reading()
    
    print ("Wait for interval specified in Step 1 and Get sensor reading")
    second_sensor_reading_with_new_interval = wait(
        func=get_sensor_reading,
        condition=lambda x: isinstance (x, dict),
        tries=10,
        timeout=1
    )
    
    print("Validate that reading from Step 4 doesn't equal reading from Step 6")
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
  
    print("1. Get original sensor firmware version")
    sensor_original_firmware_version = get_sensor_info()

    print("2. Request firmware update")
    update_sensor_firmware()

    print("3. Get current sensor firmware version")
    sensor_current_firmware_version = wait(
            func=get_sensor_info,
            condition=lambda x: isinstance (x, dict),
            tries=15,
            timeout=1
    )
  
    print("4. Validate that current firmware version is +1 to original firmware version")
    assert sensor_current_firmware_version.get("firmware_version") - sensor_original_firmware_version.get("firmware_version") == 1

    print ("5. Repeat steps 1-4 until sensor is at max_firmware_version - 1")
    max_firmware_version = 15
    current_sensor_state = get_sensor_info()
    current_firmware_version = current_sensor_state.get("firmware_version")
    while current_firmware_version < max_firmware_version:
        update_sensor_firmware()
        updated_firmware_version = wait(
            func=get_sensor_info,
            condition=lambda x: isinstance (x, dict),
            tries=15,
            timeout=1
        )
        updated_firmware_version = updated_firmware_version.get("firmware_version")
        
        assert updated_firmware_version - current_firmware_version == 1

        current_firmware_version +=1

    print ("6. Update sensor to max firmware version")
    update_sensor_firmware()

    print ("7. Validate that sensor is at max firmware version")
    assert current_firmware_version == max_firmware_version

    print ("8. Request another firmware update")
    update_sensor_firmware()

    print ("9. Validate that sensor doesn't update and responds appropriately")
    updated_firmware_version = wait(
            func=get_sensor_info,
            condition=lambda x: isinstance (x, dict),
            tries=15,
            timeout=1
    )
    updated_firmware_version = updated_firmware_version.get("firmware_version")
    if updated_firmware_version == max_firmware_version:
        print ("Sensor has maximal firmware version")

    
    print ("10. Validate that sensor firmware version doesn't change if it's at maximum value")
    update_sensor_firmware()
    updated_firmware_version = wait(
            func=get_sensor_info,
            condition=lambda x: isinstance (x, dict),
            tries=15,
            timeout=1
    )
    updated_firmware_version = updated_firmware_version.get("firmware_version")
    if updated_firmware_version == max_firmware_version:
        print ("Sensor already has maximal firmware version")

    


