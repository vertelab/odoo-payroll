{
    'name': 'Payroll: Tier Review',
    'version': '14.0.0.0.0',
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
    'version': '0.1',
    'depends': ['base_tier_validation', 'payroll'],
    'data': [
        'views/hr_payslip_view.xml'
    ],
}
