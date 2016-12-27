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
from openerp.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class hr_timesheet_sheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"
    
    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        #~ {'user_id': 142,
        #~ 'product_id': 5241,
        #~ 'general_account_id': 665,
        #~ 'product_uom_id': 10,
        #~ 'journal_id': 5,
        #~ 'account_id': 129,
        #~ 'to_invoice': False,
        #~ 'amount': 0,
        #~ 'unit_amount': 0,
        #~ 'date': '2016-12-01',
        #~ 'name': '/'}
        if 'employee_id' in vals and 'date_from' in vals and 'date_to' in vals:
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            if employee and employee.user_id:
                values = self.env['hr.analytic.timesheet'].with_context({'user_id': employee.user_id.id}).default_get(['account_id','general_account_id', 'journal_id','date','name','user_id','product_id','product_uom_id','to_invoice','amount','unit_amount'])
                ids = self.pool.get('hr.analytic.timesheet').search(self._cr, self._uid, [
                    ('user_id', '=', employee.user_id.id),
                    ('date', '>=', vals['date_from']),
                    ('date', '<=', vals['date_to'])])
                account_ids = set()
                for v in self.env['hr.analytic.timesheet'].search_read([('id', 'in', ids)], ['account_id']):
                    account_ids.add(v['account_id'][0])
                vals['timesheet_ids'] = []
                for id in account_ids:
                    vals['timesheet_ids'].append((0, 0, values))
                    vals['timesheet_ids'][-1][2].update({
                        'name': '\\',
                        'account_id': id,
                    })
        _logger.warn(vals)
        return super(hr_timesheet_sheet, self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
