import asyncio
from datetime import datetime as dt
from typing import Union

from bleak import discover
import psycopg2

from config import get_setting
from db import insert_record

ruuvi_tag_macs = [
    s.lower() for s in
    get_setting('TAG_FILTER', 'mac_addresses').split(',')
]

DEFAULT_TIMEOUT_SECONDS = int(get_setting('BLUETOOTH', 'timeout_seconds'))


def to_int(raw_bytes: bytes) -> int:
    return int.from_bytes(raw_bytes, 'big')


def parse_message(raw_bytes: bytes) -> dict[str, Union[int, float]]:
    try:
        temperature = round(0.005 * to_int(raw_bytes[1:3]), 2)
        humidity = round(to_int(raw_bytes[3:5]) * 0.000025, 4)
        pressure = to_int(raw_bytes[5:7]) + 50000  # mf given offset
        # acc_x = to_int(raw_bytes[7:9])
        # acc_y = to_int(raw_bytes[9:11])
        # acc_z = to_int(raw_bytes[11:13])
        power_binary = bin(to_int(raw_bytes[13:15]))[2:]  # because
        power_voltage = int(power_binary[:11], 2) + 1600  # mV
        power_tx = int(power_binary[11:], 2) * 2 - 40  # dBm
        # movement_counter = to_int(raw_bytes[15])
        sequence = to_int(raw_bytes[16:18])
        return {
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure,
            'voltage': power_voltage,
            'tx_power': power_tx,
            'measurement_sequence': sequence,
        }
    except BaseException as e:
        raise Exception(f'Unable to parse data from familiar MAC: {raw_bytes}, exception: {e}') from e 


async def run():
    poll_start_ts = dt.now()
    devices = await discover(timeout=DEFAULT_TIMEOUT_SECONDS)
    for device in devices:
        data = device.metadata.get('manufacturer_data')
        if not data:
            continue
        raw_bytes = list(data.values())[0]
        decoded = [format(x, '02x') for x in raw_bytes]
        assumed_mac = ':'.join(decoded[-6:])
        if assumed_mac in ruuvi_tag_macs:
            parsed_data = parse_message(raw_bytes)
            parsed_data['mac'] = assumed_mac
            parsed_data['poll_start_ts'] = poll_start_ts
            insert_record(parsed_data)
            

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
