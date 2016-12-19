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

from openerp import models, fields, api, _, tools

import logging
_logger = logging.getLogger(__name__)

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    def _attendance_working_hours(self):
        self.attendance_working_hours = sum(self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('name','>',self.date_from + ' 00:00:00'),('name','<',self.date_to + ' 23:59:59')]).mapped("get_working_hours"))
    attendance_working_hours = fields.Float(string='Attendance Schema Time',compute="_attendance_working_hours")


class hr_contract_type(models.Model):
    _inherit = 'hr.contract.type'

    work_time = fields.Selection(selection_add=[('schema_hour','Hourly Schema')])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
