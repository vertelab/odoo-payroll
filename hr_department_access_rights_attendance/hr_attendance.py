# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class hr_attendance(models.Model):
    _inherit = 'hr.attendance'

    def init_records(self, cr, uid, context=None):
        access_hr_attendance_user = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_attendance', 'access_hr_attendance_system_user')
        self.pool.get('ir.model.access').write(cr, uid, access_hr_attendance_user[1],{
            'perm_read': True,
            'perm_write': False,
            'perm_create': True,
            'perm_unlink': False,
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
