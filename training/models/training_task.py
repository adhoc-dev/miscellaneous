# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class TrainingTask(models.Model):

    """docstring for ClassName"""
    _name = 'training.task'
    _order = 'sequence'

    # @api.model
    # def create(self, vals):
    #     vals['states'] = 'pending'
    #     print 'asdfasdfasf', vals
    #     return super(TrainingTask, self).create(vals)

    name = fields.Char(
        required=True,
        readonly=True,
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
    )
    parent_id = fields.Many2one(
        'training.task',
        'Parent',
        readonly=True,
        ondelete='cascade',
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
    )
    child_ids = fields.One2many(
        'training.task',
        'parent_id',
        'Childs',
        readonly=True,
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
        # copy=True,
    )
    start_date = fields.Date(
        default=fields.Date.today,
        readonly=True,
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
    )
    end_date = fields.Date(
        readonly=True,
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
    )
    trainee_id = fields.Many2one(
        'res.partner',
        'Trainee',
        # required=True,
        readonly=True,
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
    )
    trainee_user_id = fields.Many2one(
        'res.users',
        compute='get_trainee_user_id',
        store=True,
        )
    trainer_id = fields.Many2one(
        'res.users',
        'Trainer',
        default=lambda self: self.env.user,
        readonly=True,
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
    )
    # project_id = fields.Many2one(
    #     'project.project',
    #     'Project',
    #     readonly=True,
    #     states={'pending': [('readonly', False)]},
    #     )
    task_done = fields.Integer(
        compute='get_task_data',
    )
    task_total = fields.Integer(
        compute='get_task_data',
    )
    description = fields.Html(
        readonly=True,
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
    )
    solution = fields.Html(
        readonly=True,
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
    )
    url = fields.Char(
        'URL',
        readonly=True,
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
    )
    sequence = fields.Integer(
        'Sequence',
        default=10,
        readonly=True,
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
    )
    type = fields.Selection([
        ('view', 'View'),
        ('tutorial', 'Tutorial'),
        ('exercise', 'Exercise'),
    ],
        default='view',
        required=True,
        readonly=True,
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
    )
    state = fields.Selection([
        ('template', 'Template'),
        ('pending', 'Pending'),
        ('done', 'Done')
    ],
        default='template',
        # default='pending',
        required=True,
        readonly=True,
        states={
            'pending': [('readonly', False)],
            'template': [('readonly', False)]
        },
    )

    # def get_user_task(self):
    #     self.trainer_id = lambda x: x.self.env.user

    @api.multi
    def action_new_training(self):
        self.ensure_one()
        self.new_training()

    @api.multi
    def new_training(self, trainee, trainer, parent_task=False):
        default = {
            'state': 'pending',
            'trainee_id': trainee.id,
            'trainer_id': trainer.id,
            'parent_id': parent_task and parent_task.id or False,
            }

        new_training = self.copy(default=default)
        for child in self.child_ids:
            child.new_training(
                trainee, trainer, parent_task=new_training)

    def get_task_data(self):
        for task in self:
            task.task_done = self.search([
                ('parent_id', '=', task.id),
                ('state', '=', 'done'),
            ], count=True)
            task.task_total = self.search([
                ('parent_id', '=', task.id),
            ], count=True)

    @api.constrains('state')
    def set_date_end(self):
        for task in self:
            if task.state == 'done' and not task.end_date:
                task.end_date = fields.Date.today()

    @api.constrains('state')
    def get_state_done(self):
        for task in self:
            if task.state == 'done':
                task.parent_id.state == 'done'

    @api.constrains('state')
    def check_done(self):
        for task in self:
            if task.state == 'done':
                child_tasks = self.search([
                    ('id', 'child_of', task.id),
                    ('state', '!=', 'done')])
                if child_tasks:
                    raise UserError(_(
                        'task can not be done if the daughters tasks not '
                        'performed'))

    @api.multi
    @api.depends('trainee_id.user_ids')
    def get_trainee_user_id(self):
        for task in self:
            users = task.trainee_id.user_ids
            task.trainee_user_id = users and users[0] or False

    @api.constrains('trainee_id', 'parent_id')
    def set_trainee_id(self):
        for task in self:
            if task.parent_id and task.trainee_id != task.parent_id.trainee_id:
                raise UserError(_(
                    'Trainee must be the same as parent task trainee'))

    # @api.multi
    # def open_windows(self, cr, uid, ids, context=None):
    # @api.one
    # def open_windows(self, cr, uid, id, context=None):
    # @api.model
    # def open_windows(self, cr, uid, context=None):
    # def open_windows(self):

    # @api.multi
    # def action_open_template_task(self):
    #     self.ensure_one()
    #     task_form = self.env.ref(
    #        'training.view_training_task_template_form', False)
    #     if not task_form:
    #         return False
    #     return {
    #         'name': _('Training Tasks'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'training.task',
    #         'view_id': task_form.id,
    #         'res_id': self.id,
    #         'target': 'current',
    #         'context': self._context,
    #         # top open in editable form
    #         'flags': {
    #             'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
    #     }

    @api.multi
    def action_open_task(self):
        self.ensure_one()
        if self.state != 'template':
            task_form = self.env.ref(
               'training.view_training_task_form', False)
        else:
            task_form = self.env.ref(
               'training.view_training_task_template_form', False)
        if not task_form:
            return False
        return {
            'name': _('Training Tasks'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'training.task',
            'view_id': task_form.id,
            'res_id': self.id,
            'target': 'current',
            'context': self._context,
            # top open in editable form
            # 'flags': {
                # 'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }

    @api.multi
    def action_open_url(self):
        url = self.url
        if not url.startswith('http'):
            url = '%s%s' % ('http://', url)
        return {
            'target': 'new',
            'name': 'Open URL',
            'url': url,
            'type': 'ir.actions.act_url',
        }

    @api.one
    def action_state_done(self):
        self.state = 'done'

    # def write(self, vals):
    #     if vals.get('state') == 'done':
    #         vals['end_date'] == today
    #     return super(TrainingTask, self).write(vals)
