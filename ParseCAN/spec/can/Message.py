from ... import spec, data, meta, parse


class MessageSpec(meta.message):
    '''
    A specification describing an arbitrary CAN Message's format and contents.
    '''

    attributes = ('name', 'can_id', 'is_big_endian', 'frequency', 'segments')

    def __init__(self, name, can_id, is_big_endian, frequency=None, segments=None):
        self.name = str(name)
        self.can_id = parse.number(can_id)
        self.is_big_endian = bool(is_big_endian)
        self.frequency = parse.SI(frequency, 'Hz') if frequency else None
        self.segments = {}

        for segnm in segments:
            if isinstance(segments[segnm], dict):
                try:
                    cand = spec.segment(name=segnm, **segments[segnm])
                except Exception as e:
                    raise ValueError(
                        'in segment {}: {}'
                        .format(
                            segnm,
                            e
                        )
                    )
                    continue

                self.upsert_segment(cand)
            else:
                self.upsert_segment(segments[segnm])

    def __iter__(self):
        return iter(self.segments.values())

    def get_segment(self, seg):
        '''
        Given a spec.segment return the corresponding
        spec.segment in this spec.message.
        '''
        assert isinstance(seg, spec.segment)
        return self.segments[seg.name]

    def segment_fits(self, seg):
        assert isinstance(seg, spec.segment)
        within = lambda x, s: x.position < s < x.position + x.length
        return not any(within(x, seg.position) or within(x, seg.position + seg.length) for x in self)

    def upsert_segment(self, seg):
        '''
        Attach, via upsert, a spec.segment to this spec.message.
        Returns true if replacement ocurred.
        '''
        assert isinstance(seg, spec.segment)
        if not self.segment_fits(seg):
            raise ValueError('segment {} intersects'.format(seg.name))
        replacement = seg.name in self.segments and self.segments[seg.name] != seg
        self.segments[seg.name] = seg

        return replacement

    def interpret(self, message):
        assert isinstance(message, data.message)

        names = self.segments.values()
        return (self.name, {seg.name: seg.interpret(message) for seg in names})

    def __str__(self):
        '''
        A comma separated representation of a spec.message's values.
        In the same order as spec.message.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)