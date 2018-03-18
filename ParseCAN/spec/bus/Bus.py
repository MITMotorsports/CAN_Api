from ... import data, spec, plural
from typing import Sequence, Union


class BusType:
    '''
    A (CAN) bus specification.
    Describes the set of messages that flow through a CAN bus.
    Can unpack CAN Messages that were sent based on this spec.bus.
    '''

    def __init__(self, name, baudrate, is_extended=None, messages=None):
        self.name = name
        self.baudrate = int(baudrate)
        self.is_extended = bool(is_extended)
        self.__messages = plural.unique('name', 'can_id', type=spec.message)

        for msgnm in messages:
            if isinstance(messages[msgnm], dict):
                try:
                    self.messages.safe_add(spec.message(
                        name=msgnm, **messages[msgnm]))
                except Exception as e:
                    e.args = (
                        'in message {}: {}'.format(
                            msgnm,
                            e
                        ),
                    )

                    raise
            else:
                self.messages.safe_add(messages[msgnm])

    @property
    def messages(self):
        return self.__messages

    def unpack(self, message):
        '''
        unpacks a data.message instance based on this spec.can.
        '''
        assert isinstance(message, data.message)
        return self.messages.unpack(message)

    def __str__(self):
        return self.name


class BusTypeFiltered(BusType):
    def __init__(self, bus: BusType, interests: Sequence[Union[int, str]]):
        self.bus = bus
        self.interests = interests

    @property
    def interests(self):
        return self._interests

    @interests.setter
    def interests(self, interests):
        for interest in interests:
            try:
                if isinstance(interest, int):
                    self.bus.messages.can_id[interest]
                elif isinstance(interest, str):
                    self.bus.messages.name[interest]
                else:
                    raise ValueError('in bus {}: in interest {}: must be of type int or str'.format(
                        self.bus, interest))
            except KeyError:
                raise ValueError('in bus {}: in interest {}: does not exist in the bus'.format(
                    self.bus, interest))

        self._interests = interests

    def interested(self, msg):
        assert isinstance(msg, spec.message)
        return msg.name in self.interests or msg.can_id in self.interests

    @property
    def messages(self):
        return (msg for msg in self.bus.messages if self.interested(msg))

    def __getattr__(self, attr):
        return getattr(self.bus, attr)
