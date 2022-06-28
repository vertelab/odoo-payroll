# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<https://vertel.se>).
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
    'name': 'Payroll: HR Payroll Employee Fund',
    'version': '14.0.0.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Extends hr.contract with an analytic account for a fund.',
    'category': 'Productivity',
'description': """Extends the Employee Contract with an analytic account to be used as a fund. 
This can be used as a flexible time bank (hours) or monetary values (cost/revenue).

Financed by Dermanord-Svensk Hudvård AB
""",
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-payroll/hr_payroll_employeefund',
    'images': ['/static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-payroll',
    'depends': ['hr_payroll_account_community','hr_timesheet_sheet'],
    'data': ['payslip_view.xml',
            'security/security.xml',
            'views/hr_expense_view_form.xml',
            'security/ir.model.access.csv',
            ],
'installable': True,
}
