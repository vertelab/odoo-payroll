# -*- coding: utf-8 -*-
"""Version-agnostic smoke test for hr_payroll_employeefund.

The module adds employee_fund to the contract (hr.contract in 18.0,
hr.version from 19.0) and use_employee_fund to the salary rule.
"""
from odoo.tests import tagged
from odoo.tests import TransactionCase


@tagged("post_install", "standard")
class TestEmployeeFund(TransactionCase):
    def _contract_model(self):
        for name in ("hr.version", "hr.contract"):
            if name in self.env and "employee_fund" in self.env[name]._fields:
                return self.env[name]
        self.fail("neither hr.version nor hr.contract has employee_fund")

    def test_contract_has_fund_fields(self):
        model = self._contract_model()
        for fname in ("employee_fund", "employee_fund_balance", "employee_fund_name"):
            self.assertIn(fname, model._fields, f"{fname} missing on {model._name}")

    def test_salary_rule_flag(self):
        self.assertIn("use_employee_fund", self.env["hr.salary.rule"]._fields)

    def test_group_contract_holder_exists(self):
        group = self.env.ref(
            "hr_payroll_employeefund.group_contract_holder", raise_if_not_found=False
        )
        self.assertTrue(group, "group_contract_holder must exist")
