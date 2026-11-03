{
    'name': 'Access Manager: Hide Menus & Read-Only Users',
    'summary': 'Hide menus per user, make users read-only, turn off developer mode, import and export. '
               'Free, no coding.',
    'version': '19.0.1.0.0',
    'category': 'Extra Tools',
    'author': 'Novator Technologies',
    'website': 'https://www.novator.co',
    'support': 'support@novator.co',
    'license': 'LGPL-3',
    'depends': ['base_setup', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/profile_views.xml',
        'views/res_users_views.xml',
        'views/menus.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}
