# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime
import pytz

import logging
_logger = logging.getLogger(__name__)

class ResourceCalendarHoliday(models.Model):
    _name = 'resource.holiday.settings'
    _description = 'Translates a calendar entry to a resource leave.'
    
    name = fields.Char(string='Name')
    time_start = fields.Float(string='Start Time', help="Fill this out if this holiday isn't all day.")
    time_stop = fields.Float(string='End Time', help="Fill this out if this holiday isn't all day.")
    calendar_ids = fields.Many2many(comodel_name='resource.calendar', relation="resource_calendar_holiday_settings_rel", column1="holiday_setting_id", column2="calendar_id", string='Resource Calendar')
    
    @api.model
    def convert_to_utc(self, record, dt):
        if isinstance(record, basestring):
            tz_name = record
        else:
            tz_name = record._context.get('tz') or record.env.user.tz
        utc_dt = pytz.timezone(tz_name).localize(dt).astimezone(pytz.utc)
        return fields.Datetime.to_string(utc_dt)
    
    @api.model
    def get_datetime(self, date, time_float):
        h = int(time_float)
        m = int(round((time_float - h) * 60))
        return datetime.strptime('%s %s:%s:00' % (date, h, m), '%Y-%m-%d %H:%M:%S')
    
    @api.multi
    def convert_to_leave(self, event, timezone):
        for record in self:
            if event.name == record.name:
                if record.time_start and record.time_stop:
                    return (event.name,
                        self.convert_to_utc(timezone, self.get_datetime(event.start_date, record.time_start)),
                        self.convert_to_utc(timezone, self.get_datetime(event.start_date, record.time_stop)))
                else:
                    return (event.name,
                        self.convert_to_utc(timezone, datetime.strptime('%s 00:00:00' % event.start_date, '%Y-%m-%d %H:%M:%S')),
                        self.convert_to_utc(timezone, datetime.strptime('%s 23:59:59' % event.start_date, '%Y-%m-%d %H:%M:%S')))

@api.model
def _tz_get(self):
    # put POSIX 'Etc/*' entries at the end to avoid confusing users - see bug 1086728
    return [(tz,tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]

class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'
    
    @api.model
    def _default_timezone(self):
        return self.env.user.tz
    
    timezone = fields.Selection(selection=_tz_get, string="Timezone", help="Timezone to use when importing holidays.", default=_default_timezone)
    holidays_start_date = fields.Date(string='Earliest Import Date', help="Don't import holidays earlier than this date.")
    holidays_partner_id = fields.Many2one(comodel_name='res.partner', string='Holidays Calendar',
        help="Import holiday entries from the calendar belonging to this partner.")
    holiday_settings_ids = fields.Many2many(comodel_name='resource.holiday.settings', relation="resource_calendar_holiday_settings_rel",
        column1="calendar_id", column2="holiday_setting_id", string='Holiday Import Lines', help="Rules for translating calendar entries to leaves.")
    
    @api.multi
    def _check_if_leave_exists(self, leave):
        self.ensure_one()
        return self.env['resource.calendar.leaves'].search_count([('calendar_id', '=', self.id), ('name', '=', leave[0]), ('date_from', '=', leave[1]), ('date_to', '=', leave[2])]) and True or False
    
    @api.one
    def import_holidays_calendar(self):
        if self.holidays_partner_id and self.timezone:
            values = [('partner_ids', '=', self.holidays_partner_id.id)]
            if self.holidays_start_date:
                values.append(('start_date', '>=', self.holidays_start_date))
            for event in self.env['calendar.event'].search(values):
                leave = self.holiday_settings_ids.convert_to_leave(event, self.timezone)
                if leave and not self._check_if_leave_exists(leave):
                    self.env['resource.calendar.leaves'].create({
                        'calendar_id': self.id,
                        'name': leave[0],
                        'date_from': leave[1],
                        'date_to': leave[2],
                    })
    
    @api.one
    def clear_calendar_leaves(self):
        self.leave_ids = None
    
    @api.model
    def update_all_calendar_leaves(self, clear=False):
        _logger.warn('update_all_calendar_leaves')
        for calendar in self.search([('timezone', '!=', False),('holidays_partner_id', '!=', False)]):
            if clear:
                calendar.clear_calendar_leaves()
            calendar.import_holidays_calendar()
