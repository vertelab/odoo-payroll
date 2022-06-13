# -*- coding: utf-8 -*-
# from odoo import http


# class HrPayrollEmployeefundExpenses(http.Controller):
#     @http.route('/hr_payroll_employeefund_expenses/hr_payroll_employeefund_expenses/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_payroll_employeefund_expenses/hr_payroll_employeefund_expenses/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_payroll_employeefund_expenses.listing', {
#             'root': '/hr_payroll_employeefund_expenses/hr_payroll_employeefund_expenses',
#             'objects': http.request.env['hr_payroll_employeefund_expenses.hr_payroll_employeefund_expenses'].search([]),
#         })

#     @http.route('/hr_payroll_employeefund_expenses/hr_payroll_employeefund_expenses/objects/<model("hr_payroll_employeefund_expenses.hr_payroll_employeefund_expenses"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_payroll_employeefund_expenses.object', {
#             'object': obj
#         })
