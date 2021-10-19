# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
import logging
from odoo import models, fields, api, _
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    expense_journal_id = fields.Many2one('account.journal', string='Default Expense Journal', default_model = 'account.journal', config_parameter='hr_expense.expense_journal_id')


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    employee_invoice_id = fields.Many2one('account.move', string="Employee invoice", readonly = True)

    @api.model
    def _default_journal_id(self):
        """ The journal is determining the company of the accounting entries generated from expense. We need to force journal company and expense sheet company to be the same. """
        journal = self.env['ir.config_parameter'].sudo().get_param('hr_expense.expense_journal_id', default=1)
        return journal

    journal_id = fields.Many2one('account.journal', string='Expense Journal', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, check_company=True, domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",
        default=_default_journal_id, help="The journal used when the expense is done.")

    def action_sheet_move_create(self):
        res = super().action_sheet_move_create()
        if self.expense_line_ids[0].payment_mode == 'employee_fund':
            account_move = self.env['account.move'].with_context(check_move_validity=False).create({
            'ref': self.expense_line_ids[0].reference,
            'move_type': 'in_invoice',
            'partner_id': self.employee_id.address_home_id.id,
            'invoice_date': fields.Datetime.now(),
            'journal_id': self.journal_id.id
            })
            for expense_line in self.expense_line_ids:
                line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'account_id': expense_line.product_id.property_account_expense_id.id,
                    'name': expense_line.product_id.name,
                    'tax_ids': [expense_line.product_id.supplier_taxes_id.id],
                    'quantity': expense_line.quantity,
                    'move_id': account_move.id,
                    'product_id': expense_line.product_id.id,
                    'price_unit': expense_line.unit_amount,
                })
                line._onchange_mark_recompute_taxes()
            account_move._onchange_partner_id()
            account_move._recompute_dynamic_lines()
            account_move.action_post()
            self.employee_invoice_id = account_move.id
        return res





class HrExpense(models.Model):

    _inherit = "hr.expense"

    employee_fund = fields.Many2one(string="Employee Fund",comodel_name='account.analytic.account',help="Use this account together with marked salary rule" ,related='employee_id.contract_id.employee_fund')
    employee_fund_balance = fields.Monetary(string='Balance',related='employee_fund.balance',currency_field='currency_id')
    employee_fund_name = fields.Char(string='Name',related='employee_fund.name')

    payment_mode = fields.Selection(selection_add = [("employee_fund","Kompetensutvecklingsfond")],)

    @api.onchange('employee_id', 'payment_mode')
    def _compute_analytic_account(self):
        for line in self:
            if line.payment_mode == 'employee_fund':
                line.analytic_account_id = line.employee_id.contract_id.employee_fund

    def _get_account_move_line_values(self):
        move_line_values_by_expense = super()._get_account_move_line_values()
        _logger.warning(f"move_line_values: {move_line_values_by_expense}")
        keys = move_line_values_by_expense.keys()
        for key in keys:
            expense = self.env['hr.expense'].browse(move_line_values_by_expense[key][0]['expense_id'])
            if expense.payment_mode != 'employee_fund':
                return move_line_values_by_expense
        for key in keys:
            expense = self.env['hr.expense'].browse(move_line_values_by_expense[key][0]['expense_id'])
            price = 0
            new_values = []
            for line in move_line_values_by_expense[key]:
                if 'tax_ids' in line.keys():
                    price = line['debit']
                    line['tax_ids'] = []
                    line['account_id'] = expense.employee_id.contract_id.credit_account_id.id
                if line['credit'] != 0:
                    line['credit'] = price
                    line['account_id'] = expense.employee_id.contract_id.debit_account_id.id
                if 'tax_repartition_line_id' not in line.keys():
                    new_values.append(line)
            move_line_values_by_expense[key] = new_values
        return move_line_values_by_expense

    def _create_sheet_from_expenses(self):
        sheet = super(HrExpense,self)._create_sheet_from_expenses()
        todo = self.filtered(lambda x: x.payment_mode=='employee_fund')
        if len(todo) > 0:
            sheet.name = todo[0].name
            # ~ sheet.name = 'test'
            sheet.expense_line_ids = [(6, 0, todo.ids+sheet.expense_line_ids.ids)]
        return sheet

    def update_analytic_line(self):
        expense_tree = self.env.ref('hr_payroll_employeefund_expenses.quick_view_account_analytic_line_tree')
        ctx = {
            'account_id': self.analytic_account_id.id,
            'partner_id': self.employee_id.address_home_id.id
        }
        return {
            'name': _('Cost and Revenue'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.analytic.line',
            'views': [
                (self.env.ref('hr_payroll_employeefund_expenses.quick_view_account_analytic_line_tree').id, 'tree'),
                (False, 'form')
            ],
            'view_id': expense_tree.id,
            'target': 'new',
            'context': dict(
                account_id=self.analytic_account_id.id,
                partner_id=self.employee_id.address_home_id.id,
                default_account_id=self.analytic_account_id.id,
                default_partner_id=self.employee_id.address_home_id.id,
                default_name=self.name
            ),
            'domain': [
                ('account_id', '=', self.analytic_account_id.id),
                ('partner_id', '=', self.employee_id.address_home_id.id),
            ],
         }


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    credit_account_id = fields.Many2one('account.account', string="Credit Account", default=lambda self: self._get_default_credit_account())
    debit_account_id = fields.Many2one('account.account', string="Debit Account", default=lambda self: self._get_default_debit_account())
    fill_amount = fields.Float(string="Fill Amount", Store=False)

    def _get_default_credit_account(self):
        return self.env['account.account'].search([('code','=','2829')])

    def _get_default_debit_account(self):
        return self.env['account.account'].search([('code','=','7699')])

    def create_account_move(self):
        if not self.credit_account_id or not self.debit_account_id or not self.journal_id or not self.fill_amount or not self.employee_fund:
            raise UserError(_("Kindly check if credit, debit account,Journal,Employee fund are set and the amount to fill employee fund "))
        account_move_line = self.env['account.move.line'].with_context(check_move_validity=False)
        account_move = self.env['account.move'].create({'journal_id': self.journal_id.id})
        account_move_line.create({
            'account_id': self.credit_account_id.id,
            'analytic_account_id': self.employee_fund.id,
            'name': self.employee_id.name,
            'credit': self.fill_amount,
            'exclude_from_invoice_tab': True,
            'move_id': account_move.id,
        })
        account_move_line.create({
            'account_id': self.debit_account_id.id,
            'name': self.employee_id.name,
            'debit': self.fill_amount,
            'exclude_from_invoice_tab': True,
            'move_id': account_move.id,
        })
        account_move.action_post()
        self.fill_amount = 0
