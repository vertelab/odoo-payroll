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
'name': 'Attendance Terminal',
'version': '0.1',
'summary': 'Human Resource',
'category': 'hr',
'description': """
Attendance report in web form

""",
'author': 'Vertel AB',
'website': 'http://www.vertel.se',
'depends': ['hr_attendance', 'bus',],
'data': [
    'hr_attendance_terminal_view.xml',
    'hr_employee_view.xml',
    'hr_attendance_terminal_data.xml',
    ],
'installable': True,
}
