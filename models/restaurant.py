from odoo import models, fields, api

class RestaurantDish(models.Model):
    _name = 'restaurant.dish'
    _description = 'Plat du restaurant'

    name = fields.Char(string="Nom du Plat", required=True)
    price = fields.Float(string="Prix")
    description = fields.Text(string="Ingrédients")
    category = fields.Selection([
        ('pizza', 'Pizzas & Pates'),
        ('burger', 'Burgers & Sandwichs'),
        ('asian', 'Asiatique / Sushi'),
        ('drink', 'Boissons')
    ], string="Catégorie", required=True)

class RestaurantChef(models.Model):
    _name = 'restaurant.chef'
    _description = 'Chef Cuisinier'

    name = fields.Char(string="Nom du Chef", required=True)
    specialty = fields.Selection([
        ('pizza', 'Pizzas & Pates'),
        ('burger', 'Burgers & Sandwichs'),
        ('asian', 'Asiatique / Sushi'),
    ], string="Spécialité", required=True)

class RestaurantOrder(models.Model):
    _name = 'restaurant.order'
    _description = 'Commande Client'

    table_number = fields.Char(string="Numéro de Table", required=True)
    dish_ids = fields.Many2many('restaurant.dish', string="Plats commandés")
    chef_id = fields.Many2one('restaurant.chef', string="Chef Assigné", readonly=True)
    note = fields.Text(string="Note pour le Chef")
    
    priority = fields.Selection([
        ('0', 'Normale'),
        ('1', 'Urgent'),
        ('2', 'Très Urgent'),
        ('3', 'CRITIQUE')
    ], string="Priorité", default='0')

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('cooking', 'En Cuisine'),
        ('ready', 'Prêt'),
        ('done', 'Payé')
    ], string="Statut", default='draft')
    
    total_price = fields.Float(string="Total", compute='_compute_total_price')

    @api.depends('dish_ids')
    def _compute_total_price(self):
        for order in self:
            total = 0.0
            for dish in order.dish_ids:
                total += dish.price
            order.total_price = total

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            #  récupèration la note sinon chaîne vide
            note_content = (vals.get('note') or '').lower()
            
            keywords_urgent = ['urgent', 'vite', 'pressé', 'retard']
            keywords_critical = ['allergie', 'malade', 'danger']

            # modifie le dictionnaire 'vals' directement avant la création
            if any(word in note_content for word in keywords_critical):
                vals['priority'] = '3' 
            elif any(word in note_content for word in keywords_urgent):
                vals['priority'] = '1'

        # CRÉATION DE LA COMMANDE 
        orders = super(RestaurantOrder, self).create(vals_list)

        # 'orders' contient toutes les commandes créées, on boucle dessus
        for order in orders:
            for dish in order.dish_ids:
                if dish.category:
                    specialist_chef = self.env['restaurant.chef'].search([
                        ('specialty', '=', dish.category)
                    ], limit=1)
                    
                    if specialist_chef:
                        order.chef_id = specialist_chef.id
                        break 
        
        return orders

    def action_send_kitchen(self):
        self.state = 'cooking'
    
    def action_kitchen_ready(self):
        self.state = 'ready'

    def action_mark_done(self):
        self.state = 'done'