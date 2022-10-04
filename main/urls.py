from django.urls import path, include

from . import views


urlpatterns = [
   # path('js/graph_functions.js', views.js_graph_functions, name='js_graph_functions'),
   # path('myview2/<int:code>', views.myview2, name='myview2'),
   path('update_new_visits', views.update_new_visits, name='update_new_visits'),
   path('delete_all_created_instruments', views.delete_all_created_instruments, name='delete_all_created_instruments'),
   path('', views.home, name='home'),
]