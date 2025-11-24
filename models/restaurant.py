from odoo import models, fields, api # type: ignore

class RestaurantDish(models.Model):
    _name='restaurant.dish'
    _description='Plat du restaurant'

    name=fields.Char(string="Nom du Plat", required=True)
    price=fields.Float(string="Prix")
    description = fields.Text(string="Ingrédients")

class RestaurantOrder(models.Model):
    _name='restaurant.order'
    _description='Commande Client'

    table_number=fields.Char(string="Numero de Table", required=True)
    dish_ids=fields.Many2many('restaurant.dish',string="Plats commandés")
    note= fields.Text(string="Note pour le Chef")
    state = fields.Selection(
        [
            ('draft', 'Brouillon (Serveur)'),
            ('cooking', 'En Cuisine (Chef)'),
            ('ready', 'Prêt à servir'),
            ('done', 'Payé')
        ], string="Statut", default='draft')
    total_price=fields.Float(string="Prix total à payer",compute='_compute_total_price')
    @api.depends('dish_ids')
    def _compute_total_price(self):
        for order in self:
            current_total=0.0
            for dish in order.dish_ids:
                current_total += dish.price
            order.total_price=current_total
    def action_send_kitchen(self):
        self.state = 'cooking'

    def action_kitchen_ready(self):
        self.state = 'ready'

    def action_mark_done(self):
        self.state = 'done'