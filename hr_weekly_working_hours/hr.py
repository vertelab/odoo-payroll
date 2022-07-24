# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2018 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _

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

    weekly_working_hours = fields.Float(string='Weekly Working Hours', default=40, help="The amount of hours/working week that should be used in calculations. Ought to be the same as the amount of hours in the schedule.")
    scheduled_working_hours = fields.Float(string='Scheduled Working Hours', compute='get_scheduled_working_hours', store=True, help="The amount of hours in the schedule for this contract.")
    wwh_days_full = fields.Float(string='WWH Days Full Time', default=5, help="The number of worked days/week for a full time employee. Currently not used.")
    wwh_days_intermittent = fields.Float(string='WWH Days Intermittent', default=5, help="The number of worked days/week for a part time employee. Currently used for both full and part time.")
    working_percent = fields.Float(string='Working Percent',default=100, help="Currently not used.")

    @api.depends('resource_calendar_id', 'resource_calendar_id.attendance_ids',
        'resource_calendar_id.attendance_ids.hour_from',
        'resource_calendar_id.attendance_ids.hour_to')
    def get_scheduled_working_hours(self):
        for contract in self:
            contract.scheduled_working_hours = contract.resource_calendar_id and contract.resource_calendar_id.get_weekly_working_hours() or 0
            

class resource_calendar(models.Model):
    _inherit = "resource.calendar"

    def get_weekly_working_hours(self):
        self.ensure_one()
        res = 0
        for line in self.attendance_ids:
            res += line.hour_to - line.hour_from
        return res

class hr_employee(models.Model):
    _inherit = "hr.employee"

    def get_working_hours(self, date = None):
        self.ensure_one()
        if not date:
            date = fields.Date.today()
        res = 0
        for contract in self.sudo().contract_ids:
            if contract.date_start <= date and (not contract.date_end or contract.date_end >= date):
                res += contract.weekly_working_hours
        if not res and date != fields.Date.today():
            res = self.get_working_hours()
        return res

    def get_working_days(self, date = None):
        self.ensure_one()
        if not date:
            date = fields.Date.today()
        res = 0
        for contract in self.sudo().contract_ids:
            if contract.date_start <= date and (not contract.date_end or contract.date_end >= date):
                res += contract.wwh_days_intermittent
        if not res and date != fields.Date.today():
            res = self.get_working_days()
        return res

    def get_working_hours_per_day(self, date = None):
        return self.get_working_hours(date) / (self.get_working_days(date) or 5) # Assume 5 day week if 0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
