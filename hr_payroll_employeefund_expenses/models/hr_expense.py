# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class HrExpense(models.Model):

    _inherit = "hr.expense"

    employee_fund = fields.Many2one(string="Employee Fund",comodel_name='account.analytic.account',help="Use this account together with marked salary rule" ,related='employee_id.contract_id.employee_fund')
    employee_fund_balance = fields.Monetary(string='Balance',related='employee_fund.balance',currency_field='currency_id')
    employee_fund_name = fields.Char(string='Name',related='employee_fund.name')

    payment_mode = fields.Selection(selection_add = [("employee_fund","Kompetensutvecklingsfond")],)

    def _create_sheet_from_expenses(self):
        sheet = super(HrExpense,self)._create_sheet_from_expenses()
        todo = self.filtered(lambda x: x.payment_mode=='employee_fund')
        if len(todo) > 0:
            sheet.name = todo[0].name
            # ~ sheet.name = 'test'
            sheet.expense_line_ids = [(6, 0, todo.ids+sheet.expense_line_ids.ids)]
        return sheet

    # ~ def _create_sheet_from_expenses(self):
        # ~ if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            # ~ raise UserError(_("You cannot report twice the same line!"))
        # ~ if len(self.mapped('employee_id')) != 1:
            # ~ raise UserError(_("You cannot report expenses for different employees in the same report."))
        # ~ if any(not expense.product_id for expense in self):
            # ~ raise UserError(_("You can not create report without product."))

        # ~ todo = self.filtered(lambda x: x.payment_mode=='own_account') or self.filtered(lambda x: x.payment_mode=='company_account')
        # ~ sheet = self.env['hr.expense.sheet'].create({
            # ~ 'company_id': self.company_id.id,
            # ~ 'employee_id': self[0].employee_id.id,
            # ~ 'name': todo[0].name if len(todo) == 1 else '',
            # ~ 'expense_line_ids': [(6, 0, todo.ids)]
        # ~ })
        # ~ return sheet


    # ----------------------------------------
    # ORM Overrides
    # ----------------------------------------

    
    # ~ _logger.warning('TEST TEST TEST TEST TEST TEST')

    def write(self, vals):
        _logger.warning('robin %s %s'%(self,vals))
        todo = self.filtered(lambda x: x.payment_mode=='employee_fund')
        _logger.warning('robin %s'%todo)
        for expense in todo:            
            self.env['account.analytic.line'].create({'account_id':expense.employee_fund.id,
                                                         'amount':expense.total_amount * -1, 'name':'test'})
            _logger.warning('robin: %s'%expense.total_amount)
#                    self.contract_id.employee_fund.balance = amount
        return super(HrExpense, self).write(vals)

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

    credit_account_id = fields.Many2one('account.account', string="Credit Account")
    debit_account_id = fields.Many2one('account.account', string="Debit Account")

    def create_account_move(self):
        account_move_line = self.env['account.move.line'].with_context(check_move_validity=False)
        account_move = self.env['account.move'].create({'journal_id': self.journal_id.id})
        account_move_line.create({
            'account_id': self.credit_account_id.id,
            'name': self.employee_id.name,
            'analytic_account_id': self.employee_fund.id,
            'credit': self.employee_fund_balance,
            'exclude_from_invoice_tab': True,
            'move_id': account_move.id,
        })
        account_move_line.create({
            'account_id': self.debit_account_id.id,
            'name': self.employee_id.name,
            'debit': self.employee_fund_balance,
            'exclude_from_invoice_tab': True,
            'move_id': account_move.id,
        })
        account_move.action_post()
