# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class HrExpense(models.Model):

    _inherit = "hr.expense"

    employee_fund      = fields.Many2one(string="Employee Fund",comodel_name='account.analytic.account',help="Use this account together with marked salary rule" ,related='employee_id.contract_id.employee_fund')
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
                                                         'amount':expense.total_amount * -1,'name':'test'})
            _logger.warning('robin: %s'%expense.total_amount)
#                    self.contract_id.employee_fund.balance = amount
        return super(HrExpense, self).write(vals)


 
