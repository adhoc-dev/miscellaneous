import base64

from odoo import fields, models, _
from odoo.exceptions import UserError
from lxml.etree import ParserError


class IrActionsReport(models.Model):

    _inherit = 'ir.actions.report'

    iot_rule_ids = fields.One2many('ir.actions.report.iot.rule', 'report_id', string='IoT Report Rules')

    def report_action(self, docids, data=None, config=True):
        result = super().report_action(docids, data, config)
        if result.get('type') != 'ir.actions.report':
            return result

        if user_rule := self.iot_rule_ids.filtered(lambda r: r.user_id == self.env.user):
            result['id'] = self.id
            result['device_ids'] = user_rule.device_id.mapped('identifier')
            device = user_rule.device_id
        if self.env.user.iot_device_id:
            result['id'] = self.id
            result['iot_rule_ids'] = self.env.user.iot_device_id.mapped('identifier')

        return result

    def _get_readable_fields(self):
        return super()._get_readable_fields() | {
            "device_ids",
        }

    #def render_document(self, device_id_list, res_ids, data=None):

class IrActionsReportIotRule(models.Model):

    _name = 'ir.actions.report.iot.rule'
    _description = 'Report IoT Rule'

    report_id = fields.Many2one(
        'ir.actions.report',
        required=True
    )
    user_id = fields.Many2one(
        'res.users',
        required=True,
    )
    device_id = fields.Many2one(
        'iot.device',
        ondelete='set null',
        domain="[('type', '=', 'printer')]"
    )
    active = fields.Boolean(default=True)
    
    _unique_report_users = models.Constraint(
        'UNIQUE(report_id, user_id)',
        "Only can have one IoT rule per report and user.",
    )
