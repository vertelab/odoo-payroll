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


class hr_holidays_status(models.Model):
    _inherit = "hr.holidays.status"
    _order = "sequence, name"
    sequence = fields.Integer(string="Seq")

#~ class hr_payslip(models.Model):
    #~ _inherit = 'hr.payslip'

    #~ def legal_non_vacation(self):
        #~ return [
            #~ self.env.ref('hr_holidays.holiday_status_comp').id,
            #~ self.env.ref('hr_holidays.holiday_status_sl').id,
            #~ self.env.ref('hr_payroll_flex100.compensary_leave').id,
            #~ self.env.ref('l10n_se_hr_holidays.holiday_status_cl3').id,
            #~ self.env.ref('l10n_se_hr_payroll.sick_leave_100').id,
            #~ self.env.ref('l10n_se_hr_payroll.sick_leave_214').id,
            #~ self.env.ref('l10n_se_hr_payroll.sick_leave_qualify').id
            #~ ]

    #~ @api.model
    #~ def get_legal_leaves(self):
        #~ return self.with_context({'employee_id' : self.employee_id.id}).holiday_ids.filtered(lambda h: h.remaining_leaves > 0 and h.holiday_status_id.id not in self.legal_non_vacation()).sorted(key=lambda s: s.holiday_status_id.sequence, s.holiday_status_id.name)

    #~ @api.model
    #~ def get_legal_leaves(self):
        #~ return self.with_context({'employee_id' : self.employee_id.id}).holiday_ids.filtered(lambda h: h.remaining_leaves > 0 and h.holiday_status_id.id not in self.legal_non_vacation())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
