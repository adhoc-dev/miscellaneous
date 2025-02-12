from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    send_message_delay = fields.Integer()