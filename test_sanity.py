def test_sanity(get_sensor_info, get_sensor_reading, get_sensor_methods, set_sensor_name, set_reading_interval, reset_to_factory, update_firmware, reboot):
    sensor_info = get_sensor_info()
    """"
    sensor_methods = get_sensor_methods
    sensor_name = set_sensor_name
    sensor_reading_interval = set_reading_interval
    sensor_reset = reset_to_factory
    sensor_firmware_version = update_firmware
    sensor_reboot = reboot
    """

    
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