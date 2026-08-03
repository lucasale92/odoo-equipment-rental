from odoo import api, fields, models
from odoo.exceptions import UserError


class RentalReturnWizard(models.TransientModel):
    _name = 'rental.return.wizard'
    _description = 'Asistente de Devolución de Alquiler'

    order_id = fields.Many2one(
        'rental.order', string='Orden', required=True, readonly=True)
    return_date = fields.Date(
        string='Fecha de devolución',
        required=True,
        default=fields.Date.context_today,
    )
    expected_date = fields.Date(
        related='order_id.date_end', string='Fecha prevista', readonly=True)
    currency_id = fields.Many2one(related='order_id.currency_id')
    late_days = fields.Integer(
        string='Días de retraso', compute='_compute_late', store=False)
    late_fee_per_day = fields.Monetary(
        string='Recargo por día de retraso', currency_field='currency_id')
    late_fee_total = fields.Monetary(
        string='Recargo total', currency_field='currency_id',
        compute='_compute_late', store=False)

    @api.depends('return_date', 'expected_date', 'late_fee_per_day')
    def _compute_late(self):
        for wizard in self:
            late = 0
            if wizard.return_date and wizard.expected_date:
                late = max((wizard.return_date - wizard.expected_date).days, 0)
            wizard.late_days = late
            wizard.late_fee_total = late * wizard.late_fee_per_day

    def action_confirm_return(self):
        self.ensure_one()
        order = self.order_id
        if order.state not in ('confirmed', 'ongoing'):
            raise UserError(
                "Solo se pueden devolver órdenes confirmadas o en curso.")
        order.write({
            'state': 'returned',
            'return_date': self.return_date,
        })
        msg = "Devolución registrada el %s." % self.return_date
        if self.late_days > 0:
            msg += (" Retraso de %s día(s). Recargo aplicado: %s %s." % (
                self.late_days, self.late_fee_total,
                self.currency_id.symbol or ''))
        order.message_post(body=msg)
        return {'type': 'ir.actions.act_window_close'}
