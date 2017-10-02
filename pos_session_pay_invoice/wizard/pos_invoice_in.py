# -*- coding: utf-8 -*-
# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, api, models


class PosInvoiceIn(models.TransientModel):
    _name = 'pos.invoice.in'
    _inherit = 'cash.box.out'

    def default_company(self):
        active_model = self.env.context.get('active_model', False)
        if active_model:
            active_ids = self.env.context.get('active_ids', False)
            active = self.env[active_model].browse(active_ids)
            if active_model == 'pos.session':
                return active[0].config_id.company_id
            return active[0].company_id
        return None

    def default_currency(self):
        active_model = self.env.context.get('active_model', False)
        if active_model:
            active_ids = self.env.context.get('active_ids', False)
            active = self.env[active_model].browse(active_ids)
            if active_model == 'pos.session':
                return active[0].cash_register_id.currency_id or \
                        self.company_id.currency_id
            return active[0].company_id.currency_id
        return None

    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        required=True
    )
    name = fields.Char(
        related='invoice_id.number'
    )
    company_id = fields.Many2one(
        'res.company',
        default=default_company,
        required=True,
        readonly=True
    )
    currency_id = fields.Many2one('res.currency', default=default_currency,
                                  required=True, readonly=True)

    @api.onchange('invoice_id')
    def _onchange_invoice(self):
        self.amount = self.invoice_id.residual

    @api.multi
    def _calculate_values_for_statement_line(self, record):
        res = super(PosInvoiceIn, self)._calculate_values_for_statement_line(
            record
        )
        res['invoice_id'] = self.invoice_id.id
        res['account_id'] = self.invoice_id.account_id.id
        res['ref'] = self.invoice_id.number
        res['partner_id'] = self.invoice_id.partner_id.id
        return res
