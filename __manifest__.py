{
    'name':'Restaurant Management',
    'version':'1.0',
    'category':'Sales',
    'summary':'Gestion de commandes restaurant',
    'depends':['base'],
    'data':[
        'security/ir.model.access.csv',
        'views/restaurant_views.xml',
        'views/restaurant_kanban.xml',
    ],
    'installable':True,
    'application':True,
}