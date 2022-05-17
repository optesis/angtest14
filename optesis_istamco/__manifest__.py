{
    'name': 'Istamco',
    'author': 'Optesis ANG',
    'version': '1.4.0',
    'category': 'Tools',
    'description': """
   ...
""",
    'summary': 'Module de ...',
    'sequence': 9,
    'depends': ['base', 'account', 'account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_inherit.xml',
        'views/menu.xml',
        'views/optesis_header_footer.xml',
        'views/optesis_external_layout.xml',
        'views/optesis_report_istamco.xml',
        'report/optesis_custom_report.xml',
        'report/optesis_custom_report_bad.xml',
        'views/optesis_report_istamco_modele_bd_correct.xml',
        'report/report.xml'
    ],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
