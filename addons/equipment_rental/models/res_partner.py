from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    rental_order_ids = fields.One2many(
        'rental.order', 'partner_id', string='Órdenes de alquiler')
    rental_order_count = fields.Integer(
        string='Nº de alquileres', compute='_compute_rental_order_count')

    def _compute_rental_order_count(self):
        rental_data = self.env['rental.order']._read_group(
            domain=[('partner_id', 'in', self.ids)],
            groupby=['partner_id'],
            aggregates=['__count'],
        )
        mapped_data = {partner.id: count for partner, count in rental_data}
        for partner in self:
            partner.rental_order_count = mapped_data.get(partner.id, 0)

    def action_view_rental_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Órdenes de alquiler',
            'res_model': 'rental.order',
            'view_mode': 'list,form,calendar',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
