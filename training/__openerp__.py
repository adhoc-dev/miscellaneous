# -*- encoding: utf-8 -*-
{
    'name': 'Training Management',
    'depends': [
        'base',
    ],
    'version': '8.0.0.0.0',
    'license': 'AGPL-3',
    'author': 'ADHOC SA',
    'data': [
        'wizards/training_new_training_wizard_view.xml',
        'view/training_task_view.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/training_demo.xml',
    ],
    'demo': [
        # 'data/training_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
