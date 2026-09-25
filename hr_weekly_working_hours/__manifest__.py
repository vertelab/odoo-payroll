# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2023- Vertel AB (<https://vertel.se>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Payroll: Weekly Working Hours',
    'version': '18.0.1.0.0',
    'summary': 'Adds Weekly working hours fields to hr.contract.',
    'category': 'Hr',
    'description': '''
Weekly Working Hours
====================

    Adds Weekly working hours fields to hr.contract.

    Features:

        - UI Integration: Extends 1 view(s) in the Odoo interface.
        - Extends Odoo: Builds on hr.contract, hr.employee, resource.calendar.
    ''',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-payroll/hr_weekly_working_hours',
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-payroll',
    'depends': ['hr_contract'],
    'data': ['views/hr_view.xml'],
    'installable': True,
}
