# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2016- Vertel AB (<http://vertel.se>).
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
{
    'name': 'Payroll Schema',
    'version': '14.0.0.1',
    'summary': 'Extends hr.attendance with normalized days using resource schema',
    'category': 'hr',
    'description': """Extends hr.attendance with normalized days using resource schema""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    #hr_contract_type: https://github.com/OCA/hr
    'depends': ['payroll', 'hr_timesheet_sheet', 'hr_attendance', 'hr_contract_work_time', 'hr_contract_type'],
    'data': [
        # 'views/hr_timesheet_sheet_view.xml'
    ],
    'installable': True,
}


