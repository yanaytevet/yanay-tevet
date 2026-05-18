from django.contrib import admin
from django.urls import path, include

from users.auth_router import api as auth_api
from users.users_router import api as users_api
from configurations.configurations_router import api as configurations_api
from blocks.blocks_router import api as blocks_api
from dream_diary.dream_diary_router import api as dream_diary_api
from genre_trainer.genre_trainer_router import api as genre_trainer_api


urlpatterns = [
    path(r'admin/log_viewer/', include('log_viewer.urls')),
    path(r'admin/', admin.site.urls),

    path(r'auth/', auth_api.urls),
    path(r'api/users/', users_api.urls),
    path(r'api/configurations/', configurations_api.urls),
    path(r'api/blocks/', blocks_api.urls),
    path(r'api/dream-diary/', dream_diary_api.urls),
    path(r'api/genre-trainer/', genre_trainer_api.urls),
]
