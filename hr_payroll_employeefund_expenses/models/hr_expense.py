# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
import logging
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.tools import email_split, float_is_zero
import datetime

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    expense_journal_id = fields.Many2one('account.journal', string='Default Expense Journal', default_model = 'account.journal', config_parameter='hr_expense.expense_journal_id')


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    employee_invoice_id = fields.Many2one('account.move', string="Employee invoice", readonly = True)
    employee_fund = fields.Many2one(string="Employee Fund", comodel_name='account.analytic.account', help="Use this account together with marked salary rule", related='employee_id.contract_id.employee_fund')
    employee_fund_balance = fields.Monetary(string='Balance', related='employee_fund.balance', currency_field='currency_id')
    
    @api.onchange('name')
    def _compute_reference(self):
        for line in self:
            line.reference = f"{line.name} - {datetime.datetime.now():%Y-%m-%d %H:%M}"

    @api.model
    def _default_journal_id(self):
        """ The journal is determining the company of the accounting entries generated from expense. We need to force journal company and expense sheet company to be the same. """
        journal = self.env['ir.config_parameter'].sudo().get_param('hr_expense.expense_journal_id', default=1)
        return journal

    journal_id = fields.Many2one('account.journal', string='Expense Journal', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, check_company=True, domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",
        default=_default_journal_id, help="The journal used when the expense is done.")

    def approve_expense_sheets(self):
        _logger.warning("approval lol")
        if self.expense_line_ids[0].date:
            date = self.expense_line_ids[0].date
        else:
            date = fields.Datetime.now()    
        self.accounting_date = date
        super().approve_expense_sheets()
        
    def action_sheet_move_create(self):
        # if self.expense_line_ids[0].payment_mode == 'employee_fund':
        samples = self.mapped('expense_line_ids.sample')
        if samples.count(True):
            if samples.count(False):
                raise UserError(_("You can't mix sample expenses and regular ones"))
            self.write({'state': 'post'})
            return

        if any(sheet.state != 'approve' for sheet in self):
            raise UserError(_("You can only generate accounting entry for approved expense(s)."))

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))
            
        for sheet in self.filtered(lambda s: not s.accounting_date):
            sheet.accounting_date = sheet.account_move_id.date
        to_post = self.filtered(lambda sheet: sheet.payment_mode == 'own_account' and sheet.expense_line_ids)
        to_post.write({'state': 'post'})
        (self - to_post).write({'state': 'done'})
        self.activity_update()

        if self.expense_line_ids[0].date:
            date = self.expense_line_ids[0].date
        else:
            date = fields.Datetime.now()    
        account_move = self.env['account.move'].with_context(check_move_validity=False).create({
        'ref': self.expense_line_ids[0].reference,
        'move_type': 'in_invoice',
        'partner_id': self.employee_id.address_home_id.id,
        'date': date,
        'invoice_date': date,
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
        #account_move._onchange_partner_id()
        account_move._recompute_dynamic_lines()
        account_move.action_post()
        res = {}
        if self.expense_line_ids[0].payment_mode != 'employee_fund':
            self.account_move_id = account_move.id
            res[self.id] = account_move
        else:
            expense_line_ids = self.mapped('expense_line_ids')\
                .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.company.currency_id).rounding))
            res = expense_line_ids.action_move_create()
            self.employee_invoice_id = account_move.id
        return res
        
    @api.depends(
    'currency_id',
    'account_move_id.line_ids.amount_residual',
    'account_move_id.line_ids.amount_residual_currency',
    'account_move_id.line_ids.account_internal_type',
    'employee_invoice_id.line_ids.amount_residual',
    'employee_invoice_id.line_ids.amount_residual_currency',
    'employee_invoice_id.line_ids.account_internal_type',)
    def _compute_amount_residual(self):
        for record in self:
            if record.payment_mode == "employee_fund":
                for sheet in self:
                    if sheet.currency_id == sheet.company_id.currency_id:
                        residual_field = 'amount_residual'
                    else:
                        residual_field = 'amount_residual_currency'
                    payment_term_lines = sheet.employee_invoice_id.line_ids.filtered(lambda line: line.account_internal_type in ('receivable', 'payable'))
                    sheet.amount_residual = -sum(payment_term_lines.mapped(residual_field))
                    if record.state != "cancel" and record.employee_invoice_id:
                        if sheet.amount_residual  > 0:
                            record.state = "post"
                        else:
                            record.state = "done"
            else:
                    super()._compute_amount_residual()
        
    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        for record in self:
            if record.payment_mode == "employee_fund":
                return {
                    'name': _('Register Payment'),
                    'res_model': 'account.payment.register',
                    'view_mode': 'form',
                    'context': {
                        'active_model': 'account.move',
                        'active_ids': self.employee_invoice_id.ids,
                    },
                    'target': 'new',
                    'type': 'ir.actions.act_window',
                }
            else:
                return super().action_register_payment()
        
    @api.onchange('expense_line_ids')
    def _compute_same_date_used(self):
        first_date = False
        for sheet in self:
            for line in sheet.expense_line_ids:
                if line.date and not first_date:
                    first_date = line.date
                if line.date != first_date:
                    raise UserError(_("All expense products do not have the same expense date. If you want to register expenses from different dates, please create separate expense reports"))




class HrExpense(models.Model):
    _inherit = "hr.expense"

    employee_fund = fields.Many2one(string="Employee Fund", comodel_name='account.analytic.account', help="Use this account together with marked salary rule", related='employee_id.contract_id.employee_fund')
    employee_fund_balance = fields.Monetary(string='Balance', related='employee_fund.balance', currency_field='currency_id')
    employee_fund_name = fields.Char(string='Name', related='employee_fund.name')
    payment_mode = fields.Selection(selection_add = [("employee_fund","Kompetensutvecklingsfond")],)
    attachment_reciept_should_be_warned = fields.Boolean(string='If should be given a warning, is given once', default = True)
    
    def action_submit_expenses(self):
        _logger.warning(f"action_submit_expenses {self.attachment_reciept_should_be_warned}")    
        if self.attachment_reciept_should_be_warned and self.payment_mode == "employee_fund" and self.attachment_number == 0:
                self.write({"attachment_reciept_should_be_warned": False})
                self.env.cr.commit()
                raise UserError(_("Warning! \nYou tried to send a report without a reciept, you probably want to add one but you can still submit after this warning since you only get this warning once."))
        return super().action_submit_expenses()
        
    @api.onchange('name')
    def _compute_reference(self):
        for line in self:
            line.reference = f"{line.name} - {datetime.datetime.now():%Y-%m-%d %H:%M}"

    @api.onchange('employee_id', 'payment_mode')
    def _compute_analytic_account(self):
        for line in self:
            if line.payment_mode == 'employee_fund':
                line.analytic_account_id = line.employee_id.contract_id.employee_fund

    def _get_account_move_line_values(self):
        move_line_values_by_expense = super()._get_account_move_line_values()
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
    employee_fund_journal_id = fields.Many2one('account.journal', string="Employeefund Journal")

    def _get_default_credit_account(self):
        return self.env['account.account'].search([('code','=','2829')])

    def _get_default_debit_account(self):
        return self.env['account.account'].search([('code','=','7699')])

    def create_account_move(self):
        if not self.credit_account_id or not self.debit_account_id or not self.employee_fund_journal_id or not self.fill_amount or not self.employee_fund:
            raise UserError(_("Kindly check if credit, debit account, Employeefund Journal, Employee fund are set and the amount to fill employee fund "))
        account_move_line = self.env['account.move.line'].with_context(check_move_validity=False)
        account_move = self.env['account.move'].create({'journal_id': self.employee_fund_journal_id.id})
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
