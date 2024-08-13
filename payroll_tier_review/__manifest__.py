# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2024- Vertel AB (<https://vertel.se>).
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
    'name': 'Payroll: Tier Review',
    'version': '0.1',
    'summary': """
        A glue module which adds tier validation to payslip""",
    'category': 'Productivity',
    'description': """
        A glue module which adds tier validation to payslip.
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-payroll/payroll_tier_review',
    'images': ['/static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-payroll',
    'category': 'Employee',
    'depends': ['base_tier_validation', 'payroll'],
    'data': [
        'views/hr_payslip_view.xml'
    ],
}
