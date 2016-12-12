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

class hr_holidays(models.Model):
    _inherit = "hr.holidays"
 
    
    @api.multi
    def onchange_employee(self, employee_id):
        result = super(hr_holidays, self).onchange_employee(employee_id)
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.contract_id and employee.contract_id.working_hours:
            hours_from = {a[0]: a[1] for a in reversed(employee.contract_id.working_hours.attendance_ids.sorted(key=lambda a: a.hour_from).mapped(lambda a: (a.dayofweek,a.hour_from)))}
            #result['value']['date_from'] =  hours_from['0']
            hours_to={a.dayofweek: a.hour_to for a in employee.contract_id.working_hours.attendance_ids}
            #result['value']['date_to'] = hours_to['0']
        return result
         
    @api.multi
    def onchange_date_from(self,date_to, date_from):
        if date_from and not date_to:
            raise Warning(self.employee_id)
            hours_to={a.dayofweek: a.hour_to for a in self.contract_id.working_hours.attendance_ids}
        result = super(hr_holidays, self).onchange_date_from(self,date_to, date_from)
        
        
    #~ def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        #~ """
        #~ If there are no date set for date_to, automatically set one 8 hours later than
        #~ the date_from.
        #~ Also update the number_of_days.
        #~ """
        #~ # date_to has to be greater than date_from
        #~ if (date_from and date_to) and (date_from > date_to):
            #~ raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        #~ result = {'value': {}}

        #~ # No date_to set so far: automatically compute one 8 hours later
        #~ if date_from and not date_to:
            #~ date_to_with_delta = datetime.datetime.strptime(date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=8)
            #~ result['value']['date_to'] = str(date_to_with_delta)

        #~ # Compute and update the number of days
        #~ if (date_to and date_from) and (date_from <= date_to):
            #~ diff_day = self._get_number_of_days(date_from, date_to)
            #~ result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        #~ else:
            #~ result['value']['number_of_days_temp'] = 0

        #~ return result

    #~ def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        #~ """
        #~ Update the number_of_days.
        #~ """

        #~ # date_to has to be greater than date_from
        #~ if (date_from and date_to) and (date_from > date_to):
            #~ raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        #~ result = {'value': {}}

        #~ # Compute and update the number of days
        #~ if (date_to and date_from) and (date_from <= date_to):
            #~ diff_day = self._get_number_of_days(date_from, date_to)
            #~ result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        #~ else:
            #~ result['value']['number_of_days_temp'] = 0

        #~ return result


    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: