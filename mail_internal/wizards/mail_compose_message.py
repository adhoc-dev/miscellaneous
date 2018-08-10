from odoo import fields, models

class MailComposeMessage(models.TransientModel):

    _inherit = 'mail.compose.message'

    is_internal = fields.Boolean(
        'Log an Internal Note',
        help='Whether the message is only for employees',
    )
