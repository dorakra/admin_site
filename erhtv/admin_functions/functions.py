"""
admin.py-ben hasznalt function-ok
"""

from project_creation.settings import ADMIN_ORDERING

import logging
logger = logging.getLogger(__name__)

def get_app_list(self, request, app_label=None):
    """
        az admin menuben ezzel lehet szabalyozni az appok es a menupontok sorrendjet
        az ADMIN_ORDERING-et a settings.py-ban adom meg
    """
    app_dict = self._build_app_dict(request, None)
    app_list = []
    
    for app_name, settings in ADMIN_ORDERING.items():
        try:
            app = app_dict[app_name]
        except KeyError:
            continue
        
        try:
            object_list = settings['object_list']
            try:
                # hianytalan object_list eseten object_list szerint rendez
                # az object_listbe a 'model name' kerul, pl. JegyzokonyvFAA
                app['models'].sort(key=lambda x: object_list.index(x['object_name']))
            except ValueError:
                # ha hianyos az object_list, ABC
                app['models'].sort(key=lambda x: x['name'])
        except KeyError:
            # ha van 'rendezes', es ez 'ABC'
            try:
                if settings['rendezes'] == 'ABC':
                    app['models'].sort(key=lambda x: x['name'])
            # ha nincs megadva rendezes, vagy nem 'ABC', a models.py-ben levo sorrendet veszi
            except KeyError:
                app_list.append(app)
        app_list.append(app)
    
       
    # ha hianyzik az app az ADMIN_ORDERING listabol, ABC
    for app_name in app_dict:
        if app_name not in ADMIN_ORDERING:
            app = app_dict[app_name]
            app['models'].sort(key=lambda x: x['name'])
            app_list.append(app)

    # logger.warning(len(app_list))
    return app_list
