from django.urls import path, include

from . import views


urlpatterns = [
    # path('js/graph_functions.js', views.js_graph_functions, name='js_graph_functions'),
    # path('myview2/<int:code>', views.myview2, name='myview2'),

    path('update_visit_info_metadata', views.update_visit_info_metadata, name='update_visit_info_metadata'),
    path('update_list_of_instruments', views.update_list_of_instruments, name='update_list_of_instruments'),

    path('create_instruments/<int:record_id>/<int:redcap_repeat_instance>', views.create_instruments, name='create_instruments'),
    path('create_instruments', views.create_instruments, name='create_instruments'),

    path('delete_instruments/<int:record_id>/<int:redcap_repeat_instance>', views.delete_instruments, name='delete_instruments'),
    path('delete_instruments', views.delete_instruments, name='delete_instruments'),
    path('', views.home, name='home'),
]