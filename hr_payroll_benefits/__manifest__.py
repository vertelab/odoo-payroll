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
    'name': 'Payroll: HR Payroll Benefits',
    'version': '1.1',
    'summary': 'Extends contract with benefits',
    'category': 'Payroll Localization',
    'description': """
Extends the contract with benefits for use in rules

In rules you can use benefits like this both in conditions and computation:
return = contract.benefit_value('car')
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-payroll/hr_payroll_benefits',
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-l10n_se_payroll',
    'depends': ['payroll', 'l10n_se_hr_payroll'],
    'data': ['views/hr_contract_view.xml', 'security/ir.model.access.csv','data/hr_salary_rule_data.xml'],
    'installable': True,
}
