{
    'name': 'Access Manager: Hide Menus & Read-Only Users',
    'summary': 'Hide menus per user, make users read-only, turn off developer mode, import and export. '
               'Free, no coding.',
    'version': '17.0.1.0.3',
    'category': 'Extra Tools',
    'author': 'Novator Technologies',
    'website': 'https://docs.novatorapps.com/access-manager',
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
