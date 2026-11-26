# -*- coding: utf-8 -*-
"""Version-agnostic smoke test for hr_weekly_working_hours.

The module extends the contract model - hr.contract in 18.0, hr.version from
19.0 (hr_contract was removed from core). The test resolves the model name
from the module's own field declaration instead of hardcoding it.
"""
from odoo.tests import tagged
from odoo.tests import TransactionCase


@tagged("post_install", "standard")
class TestWeeklyWorkingHours(TransactionCase):
    def _contract_model(self):
        """The model the module extends in this edition."""
        for name in ("hr.version", "hr.contract"):
            if name in self.env and "weekly_working_hours" in self.env[name]._fields:
                return self.env[name]
        self.fail("neither hr.version nor hr.contract has weekly_working_hours")

    def test_fields_exist(self):
        model = self._contract_model()
        for fname in (
            "weekly_working_hours",
            "scheduled_working_hours",
            "wwh_days_full",
            "wwh_days_intermittent",
            "working_percent",
        ):
            self.assertIn(fname, model._fields, f"{fname} missing on {model._name}")

    def test_defaults(self):
        """Defaults are callables in modern Odoo - call them, do not compare."""
        model = self._contract_model()
        defaults = model.default_get(["weekly_working_hours", "working_percent"])
        self.assertEqual(defaults.get("weekly_working_hours"), 40)
        self.assertEqual(defaults.get("working_percent"), 100)

    def test_weekly_hours_from_calendar(self):
        calendar = self.env["resource.calendar"].create(
            {
                "name": "pfiles smoke calendar",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Mon",
                            "dayofweek": "0",
                            "hour_from": 8.0,
                            "hour_to": 16.0,
                        },
                    )
                ],
            }
        )
        self.assertEqual(calendar.get_weekly_working_hours(), 8.0)
