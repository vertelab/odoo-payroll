# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    employee_fund      = fields.Many2one(string="Employee Fund",comodel_name='account.analytic.account',help="Use this account together with marked salary rule" )
    employee_fund_balance = fields.Float(string='Balance',digits_compute=dp.get_precision('Payroll'),related='employee_fund.balance')
    employee_fund_name = fields.Char(string='Name',related='employee_fund.name')


class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'

    use_employee_fund = fields.Boolean(string="Use for employee fund",default=False)

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def get_employeefund_addition(self):
        return sum(self.env['account.analytic.line'].search([('account_id','=',self.contract_id.employee_fund.id),('date','>=',self.date_from),('date','<=',self.date_to),('amount','>',0.0)]).mapped('amount'))


    @api.one
    def process_sheet(self):
        for line in self.details_by_salary_rule_category:
            if line.salary_rule_id.use_employee_fund and self.employee_id.contract_id.employee_fund:
                self.env['account.analytic.line'].create({
                    'name': 'Payslip %s' % self.name,
                    'date': fields.Date.today(),
                    'account_id': self.employee_id.contract_id.employee_fund.id,
                    'unit_amount': 1.0,
                    'amount': line.amount,
                    'general_account_id': self.env['account.account'].search([('code', 'in', ['7690','7610','7600','7699'])])[0].id,
                    'user_id': self.employee_id.user_id.id if self.employee_id.user_id else None,
                    'journal_id': self.env.ref('account.exp').id,
                })
        return super(hr_payslip, self).process_sheet()

class hr_timesheet_sheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    @api.one
    def _employee_fund(self):
        self.employee_fund = self.employee_id.sudo().contract_id.employee_fund
    employee_fund = fields.Many2one(comodel_name='account.analytic.account', string='Employee Fund', compute='_employee_fund')
    @api.one
    def _employee_fund_balance(self):
        self.employee_fund_balance = self.employee_id.sudo().contract_id.employee_fund_balance
    employee_fund_balance = fields.Float(string='Balance', compute='_employee_fund_balance')
    @api.one
    def _employee_fund_name(self):
        self.employee_fund_name = self.employee_id.sudo().contract_id.employee_fund_name
    employee_fund_name = fields.Char(string='Name', compute='_employee_fund_name')
    company_currency = fields.Many2one(related='company_id.currency_id')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
