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

import logging
_logger = logging.getLogger(__name__)

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    employee_fund      = fields.Many2one(string="Employee Fund", digits_compute=dp.get_precision('Payroll'),comodel_name='account.analytic.account',help="Use this account together with marked salary rule" )

class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'
    
    use_employee_fund = fields.Boolean(string="Use for employee fund",default=False)


class hr_payslip(models.Model):
	_inherit = 'hr.payslip'
	
	@api.one
    def process_sheet(self):
		for line in self.details_by_salary_rule_category:
			if line.salary_rule_id.use_employee_fund and self.employee_id.contract_id.employee_fund:
				request.env['account.analytic.line'].create({
					'name': 'Payslip %s' % self.name,
					'date': fields.Date.today(),
					'account_id': self.employee_id.contract_id.employee_fund,
					'unit_amount': 1,
					'amount': line.amount,  
					'general_account_id': request.env['account.account'].search([('code', '=', '3000')]).id,
					'user_id': employee.user_id.id if employee.user_id else None,
					'journal_id': request.env.ref('hr_timesheet.analytic_journal').id,
				})
		return super(hr_payslip, self).process_sheet()
		
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
