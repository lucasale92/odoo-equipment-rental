from odoo import api, fields, models


class RentalOrderLine(models.Model):
    _name = 'rental.order.line'
    _description = 'Línea de Orden de Alquiler'

    order_id = fields.Many2one(
        'rental.order', string='Orden', required=True,
        ondelete='cascade', index=True)
    equipment_id = fields.Many2one(
        'rental.equipment', string='Equipo', required=True)
    quantity = fields.Integer(string='Cantidad', default=1, required=True)
    unit_price = fields.Monetary(
        string='Tarifa/día', currency_field='currency_id')

    # Campos relacionados / calculados
    currency_id = fields.Many2one(
        related='order_id.currency_id', string='Moneda', store=True)
    duration_days = fields.Integer(
        related='order_id.duration_days', string='Días', store=True)
    price_subtotal = fields.Monetary(
        string='Subtotal',
        currency_field='currency_id',
        compute='_compute_price_subtotal',
        store=True,
    )

    @api.depends('quantity', 'unit_price', 'duration_days')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.unit_price * line.duration_days

    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        if self.equipment_id:
            self.unit_price = self.equipment_id.daily_price
