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
    'version': '1.0',
    'summary': 'Adds Weekly working hours fields to hr.contract.',
    'category': 'Hr',
    'description': """
    Adds Weekly working hours fields to hr.contract.
    """,
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
