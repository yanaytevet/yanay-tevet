from common.django_utils.api_router_creator import ApiRouterCreator
from genre_trainer.views.get_genres_view import GetGenresView
from genre_trainer.views.get_random_track_view import GetRandomTrackView

api, router = ApiRouterCreator.create_api_and_router('genre-trainer')

GetRandomTrackView.register_get(router, 'random-track/')
GetGenresView.register_get(router, 'genres/')
