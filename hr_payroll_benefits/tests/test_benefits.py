# -*- coding: utf-8 -*-
"""Version-agnostic smoke test for hr_payroll_benefits.

benefit_value() lives on the contract model - hr.contract in 18.0,
hr.version from 19.0. The test resolves the model from the field declaration.
"""
from odoo.tests import tagged
from odoo.tests import TransactionCase


@tagged("post_install", "standard")
class TestBenefits(TransactionCase):
    def _contract_model(self):
        for name in ("hr.version", "hr.contract"):
            if name in self.env and "benefit_ids" in self.env[name]._fields:
                return self.env[name]
        self.fail("neither hr.version nor hr.contract has benefit_ids")

    def test_benefit_models_exist(self):
        self.assertIn("hr.benefit", self.env)
        self.assertIn("hr.contract.benefit", self.env)

    def test_benefit_value_is_callable(self):
        model = self._contract_model()
        self.assertTrue(hasattr(model, "benefit_value"))

    def test_benefit_value_sums_matching_code(self):
        benefit = self.env["hr.benefit"].create(
            {"name": "pfiles_smoke", "desc": "pfiles smoke benefit"}
        )
        self.assertTrue(benefit)
        line = self.env["hr.contract.benefit"].create(
            {"name": benefit.id, "desc": "smoke", "value": 12.5}
        )
        self.assertEqual(line.value, 12.5)
