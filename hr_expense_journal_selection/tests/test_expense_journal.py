# -*- coding: utf-8 -*-
"""Version-agnostic smoke test for hr_expense_journal_selection.

The module's only job is to give hr.expense a journal. Odoo 19+ owns
hr.expense.journal_id (related to the payment method line's journal), so the
field exists on the model in every edition - but only this module declares it
for 18.0. The test therefore asserts the field exists and is a journal, not
who declared it.
"""
from odoo.tests import tagged
from odoo.tests import TransactionCase


@tagged("post_install", "standard")
class TestExpenseJournal(TransactionCase):
    def test_expense_has_journal_field(self):
        field = self.env["hr.expense"]._fields.get("journal_id")
        self.assertTrue(field, "hr.expense.journal_id must exist")
        self.assertEqual(field.comodel_name, "account.journal")

    def test_expense_created_with_journal(self):
        employee = self.env["hr.employee"].create({"name": "pfiles smoke employee"})
        product = self.env["product.product"].search(
            [("can_be_expensed", "=", True)], limit=1
        )
        if not product:
            self.skipTest("no expensable product in this database")
        expense = self.env["hr.expense"].create(
            {
                "name": "pfiles smoke test",
                "employee_id": employee.id,
                "product_id": product.id,
                "total_amount": 100.0,
            }
        )
        self.assertTrue(expense)
        self.assertEqual(expense.employee_id, employee)
