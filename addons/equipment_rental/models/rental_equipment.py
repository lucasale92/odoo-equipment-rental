from odoo import api, fields, models


class RentalEquipment(models.Model):
    _name = 'rental.equipment'
    _description = 'Equipo Alquilable'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Nombre', required=True, tracking=True)
    reference = fields.Char(
        string='Referencia',
        copy=False,
        readonly=True,
        default=lambda self: ('Nuevo'),
    )
    active = fields.Boolean(default=True)
    category = fields.Selection(
        selection=[
            ('tool', 'Herramienta'),
            ('machine', 'Maquinaria'),
            ('electronic', 'Electrónica'),
            ('vehicle', 'Vehículo'),
            ('other', 'Otro'),
        ],
        string='Categoría',
        default='tool',
        required=True,
        tracking=True,
    )
    status = fields.Selection(
        selection=[
            ('available', 'Disponible'),
            ('maintenance', 'En mantenimiento'),
        ],
        string='Estado operativo',
        default='available',
        required=True,
        tracking=True,
        help='Un equipo en mantenimiento no puede alquilarse.',
    )
    image = fields.Image(string='Foto')
    daily_price = fields.Monetary(
        string='Tarifa por día',
        currency_field='currency_id',
        required=True,
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    description = fields.Text(string='Descripción')

    # --- Métricas (campos calculados) ---
    rental_line_ids = fields.One2many(
        'rental.order.line', 'equipment_id', string='Líneas de alquiler')
    rental_count = fields.Integer(
        string='Nº de alquileres', compute='_compute_rental_stats')
    total_revenue = fields.Monetary(
        string='Ingresos totales',
        currency_field='currency_id',
        compute='_compute_rental_stats',
    )

    @api.depends('rental_line_ids', 'rental_line_ids.order_id.state',
                 'rental_line_ids.price_subtotal')
    def _compute_rental_stats(self):
        for equipment in self:
            valid_lines = equipment.rental_line_ids.filtered(
                lambda l: l.order_id.state in ('confirmed', 'ongoing', 'returned')
            )
            equipment.rental_count = len(valid_lines.order_id)
            equipment.total_revenue = sum(valid_lines.mapped('price_subtotal'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference') or vals.get('reference') == 'Nuevo':
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'rental.equipment') or 'Nuevo'
        return super().create(vals_list)

    def action_set_maintenance(self):
        self.write({'status': 'maintenance'})

    def action_set_available(self):
        self.write({'status': 'available'})
