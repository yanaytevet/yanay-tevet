import json
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.test import SimpleTestCase
from ninja import Schema

from common.db_fields.schema_field import SchemaField


class RowWithAwkwardTypes(Schema):
    """A row holding the types pydantic keeps as Python objects but JSON cannot encode."""

    name: str
    due_date: date | None = None
    amount: Decimal | None = None
    identifier: UUID | None = None


class SchemaFieldSerializationTest(SimpleTestCase):
    """What comes out of the field is handed straight to `json.dumps`, so it has to be JSON already.

    A python-mode dump leaves a `date` as a `date`, which raises `TypeError: Object of type date is
    not JSON serializable` at save time and takes the whole write with it. The failure only appears
    when a nullable awkward field is actually set.
    """

    def test_a_row_holding_a_date_is_dumped_to_json_primitives(self) -> None:
        field = SchemaField(list[RowWithAwkwardTypes])
        rows = [RowWithAwkwardTypes(name='permit', due_date=date(2026, 1, 1))]

        serialized = field._serialize(rows)

        self.assertEqual(serialized[0]['due_date'], '2026-01-01')
        # The real assertion: whatever comes out survives the encoder the column uses.
        json.dumps(serialized)

    def test_every_awkward_type_survives_the_encoder(self) -> None:
        field = SchemaField(RowWithAwkwardTypes)
        row = RowWithAwkwardTypes(
            name='permit',
            due_date=date(2026, 1, 1),
            amount=Decimal('1.5'),
            identifier=UUID('00000000-0000-0000-0000-000000000001'),
        )

        json.dumps(field._serialize(row))

    def test_a_row_round_trips_back_into_its_python_types(self) -> None:
        """Dumping to JSON must not cost the reader its types — a date has to come back a date."""
        field = SchemaField(list[RowWithAwkwardTypes])
        rows = [RowWithAwkwardTypes(name='permit', due_date=date(2026, 1, 1))]

        restored = field._deserialize(json.loads(json.dumps(field._serialize(rows))))

        self.assertEqual(restored[0].due_date, date(2026, 1, 1))

    def test_a_row_with_nothing_awkward_set_is_unaffected(self) -> None:
        field = SchemaField(list[RowWithAwkwardTypes])

        serialized = field._serialize([RowWithAwkwardTypes(name='permit')])

        self.assertEqual(serialized, [{'name': 'permit', 'due_date': None, 'amount': None,
                                       'identifier': None}])
