# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) Optesis 2018 www.optesis.com

{
    'name': 'Plan Comptable SFD',
    'version': '1.4.1',
    'author': 'Moore senegal',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
                    Ce module permet de gérer le nouveau plan compable SYSCOHADA Révisé
                    applicable à partir du 1er janvier 2018 pour tous les pays faisant partie de l'espace OHADA.
                    **Credits:** cabinet d'expertise comptable www.moore.sn.
                    """,
    'website': 'http://www.moore.sn',
    'depends': [
        'account',
    ],
    'data': [
        'data/account_data.xml',
        'data/l10n_rcsfd_chart_data.xml',
        'data/account.account.template.csv',
        'data/l10n_rcsfd_chart_post_data.xml',
        'data/account_tax_template_data.xml',
        'data/account_chart_template_data.xml',
    ],
    'demo': [
        #'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',

}
