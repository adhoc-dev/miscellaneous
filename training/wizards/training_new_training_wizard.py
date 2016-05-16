# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class TrainingNewTrainingWizard(models.TransientModel):

    _name = 'training.new_training.wizard'

    trainee_id = fields.Many2one(
        'res.partner',
        'Trainee',
        required=True,
    )
    detail_ids = fields.One2many(
        'training.new_training.detail.wizard',
        'new_training_id',
        'Detail',
        )

    @api.multi
    def confirm(self):
        """
        1. poner tree editable al details
        2. hacer metodo mas o menos como:
        para cada detalle:
            duplicar la task poniendo el trainer y el trainee
        """
        self.ensure_one()
        # if default is None:
        #     default = {}
        # default = default.update({'parent_id': 'trainee_id'})
        # new_id = self.copy(default)
        for line in self.detail_ids:
            line.task_id.new_training(
                trainee=self.trainee_id, trainer=line.trainer_id)
        # for child in self.detail_ids:
        #     child.new_id({'parent_id': new_id.id})
        # return new_id

    # @api.multi
    # def confirm(self, default=None):

    #     new_detail = self.copy(default=default)
    #     for child in self.detail_ids:
    #         child.new_detail({'task_id': new_detail.id})
    #     return self.with_context(default_state='pending').copy(default={})


class TrainingNewTrainingDetailWizard(models.TransientModel):

    _name = 'training.new_training.detail.wizard'

    new_training_id = fields.Many2one(
        'training.new_training.wizard',
        'New Training',
        required=True,
        ondelete='cascade',
        )
    task_id = fields.Many2one(
        'training.task',
        'Parent',
        ondelete='cascade',
        required=True,
        domain=[('type', '=', 'view'), ('state', '=', 'template')],
        )
    trainer_id = fields.Many2one(
        'res.users',
        'Trainer',
        default=lambda self: self.env.user,
        required=True,
    )
