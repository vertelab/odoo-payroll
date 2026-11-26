# -*- coding: utf-8 -*-
"""Version-agnostic smoke test for payroll_driving_record."""
from odoo.tests import tagged
from odoo.tests import TransactionCase


@tagged("post_install", "standard")
class TestDrivingRecord(TransactionCase):
    def _employee(self):
        """An employee is required; the test user may not have one."""
        return self.env["hr.employee"].create({"name": "pfiles smoke employee"})

    def test_models_exist(self):
        self.assertIn("driving.record", self.env)
        self.assertIn("driving.record.line", self.env)

    def test_create_record(self):
        record = self.env["driving.record"].create(
            {
                "employee_id": self._employee().id,
            }
        )
        self.assertTrue(record)
        self.assertEqual(record.private_length, 0)
        self.assertEqual(record.business_length, 0)

    def test_create_line(self):
        record = self.env["driving.record"].create(
            {"employee_id": self._employee().id}
        )
        line = self.env["driving.record.line"].create(
            {
                "driving_record_id": record.id,
                "length": 10.0,
                "type": "business",
                "odometer_start": 1000.0,
                "odometer_stop": 1010.0,
            }
        )
        self.assertEqual(line.length, 10.0)
