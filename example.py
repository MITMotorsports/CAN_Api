from ParseCAN import spec, data
import can

car = spec.car('../MY18/can_spec_my18.yml')
bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)


def bitstr(bytes):
    return int.from_bytes(bytes, byteorder='big', signed=False)


def msg_conv(msg):
    return data.message(can_id=msg.arbitration_id, data=bitstr(msg.data))


try:
    for msg in bus:
        print(hex(msg_conv(msg).data))
        print(car.unpack(msg_conv(msg))['can0'])
except KeyboardInterrupt:
    pass
