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


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
