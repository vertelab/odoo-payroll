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


#VA = Veckoarbetstid                         Weekly Working Hours

#http://www.vismaspcs.se/visma-support/visma-lon-special/content/visma-lon-special/semester/semesterlon-vid-andrad-sysselsattningsgrad.htm
#APR = Arbetstidsprocent                     Working Percent
#ML = Månadslön                              Monthly Salary
#SSG = Sysselsättninggrad                    Employment Rate
#VAD = Veckoarbetstid dagar heltid           WWH Days Full Time
#VADI = Veckoarbetstid dagar intermittent    WWH Days Intermittent

class hr_contract(models.Model):
    _inherit = "hr.contract"
    
    weekly_working_hours = fields.Float('Weekly Working Hours', default=40)
    scheduled_working_hours = fields.Float('Scheduled Working Hours', compute='get_scheduled_working_hours', store=True)
    wwh_days_full = fields.Float('WWH Days Full Time', default=5)
    wwh_days_intermittent = fields.Float('WWH Days Intermittent', default=5)
    
    @api.one
    @api.depends('working_hours', 'working_hours.attendance_ids',
        'working_hours.attendance_ids.hour_from',
        'working_hours.attendance_ids.hour_to')
    def get_scheduled_working_hours(self):
        self.scheduled_working_hours = self.working_hours and self.working_hours.get_working_hours() or 0

class resource_calendar(models.Model):
    _inherit = "resource.calendar"
    
    @api.multi
    def get_working_hours(self):
        self.ensure_one()
        res = 0
        for line in self.attendance_ids:
            res += line.hour_to - line.hour_from
        return res

class hr_employee(models.Model):
    _inherit = "hr.employee"
    
    @api.multi
    def get_working_hours(self, date = None):
        self.ensure_one()
        if not date:
            date = fields.Date.today()
        res = 0
        for contract in self.contract_ids:
            if contract.date_start <= date and contract.date_end >= date:
                res += contract.weekly_working_hours
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
