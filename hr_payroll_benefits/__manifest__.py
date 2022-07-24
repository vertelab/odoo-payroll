# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2018 Vertel AB (<http://vertel.se>).
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
'name': 'Payroll Benefits',
'version': '0.1',
'summary': 'Extends contract with benefits',
'category': 'hr',
'description': """Extends the contract with benefits for use in rules

    In rules you can use benefits like this both in conditions and computation:
       return = contract.benefit_value('car')
""",
'author': 'Vertel AB',
'website': 'http://www.vertel.se',
'depends': ['payroll','hr_payroll_schema'],
'data': ['payslip_view.xml', 'security/ir.model.access.csv','hr_salary_rule_data.xml'],
'installable': True,
}
