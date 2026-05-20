from ninja import Schema


class ParticleSchema(Schema):
    particle: str
    primary_function: str = ''
