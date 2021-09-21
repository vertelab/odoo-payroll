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
    'name': "hr_payroll_employeefund_expenses",

    'summary': """
        Extends hr_payroll_employeefund with an extra employeefund""",

    'description': """
        Adds an employeefund-view to the Employee Contract and the Expense viewform.
        
        0.2 - Added a button to allow edit of cost/revenue from expense
    """,

    'author': "Vertel AB",
    'website': "https://www.vertel.se",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll_employeefund','hr_expense'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/expense_view.xml',
    ],
}
