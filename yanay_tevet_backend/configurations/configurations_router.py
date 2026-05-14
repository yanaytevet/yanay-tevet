from common.django_utils.api_router_creator import ApiRouterCreator
from configurations.views.configurations_views import FullConfigurationsView

api, router = ApiRouterCreator.create_api_and_router('configurations')

FullConfigurationsView.register_get(router, '')
