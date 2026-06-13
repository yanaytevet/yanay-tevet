from django.contrib import admin
from django.urls import path, include

from users.auth_router import api as auth_api
from users.users_router import api as users_api
from configurations.configurations_router import api as configurations_api
from blocks.blocks_router import api as blocks_api
from dream_diary.dream_diary_router import api as dream_diary_api
from genre_trainer.genre_trainer_router import api as genre_trainer_api
from japanese.japanese_router import api as japanese_api
from my_dashboard.my_dashboard_router import api as my_dashboard_api
from apartment_hunt.apartment_hunt_router import api as apartment_hunt_api
from itinerary_lists.itinerary_lists_router import api as itinerary_lists_api
from task_management.task_management_router import api as task_management_api


urlpatterns = [
    path(r'admin/log_viewer/', include('log_viewer.urls')),
    path(r'admin/', admin.site.urls),

    path(r'auth/', auth_api.urls),
    path(r'api/users/', users_api.urls),
    path(r'api/configurations/', configurations_api.urls),
    path(r'api/blocks/', blocks_api.urls),
    path(r'api/dream-diary/', dream_diary_api.urls),
    path(r'api/genre-trainer/', genre_trainer_api.urls),
    path(r'api/japanese/', japanese_api.urls),
    path(r'api/my-dashboard/', my_dashboard_api.urls),
    path(r'api/apartment-hunt/', apartment_hunt_api.urls),
    path(r'api/itinerary-lists/', itinerary_lists_api.urls),
    path(r'api/task-management/', task_management_api.urls),
]
