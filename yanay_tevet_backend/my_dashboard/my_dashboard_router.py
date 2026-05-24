from common.django_utils.api_router_creator import ApiRouterCreator
from my_dashboard.views.get_openai_costs_view import GetOpenAICostsView

api, router = ApiRouterCreator.create_api_and_router('my-dashboard')

GetOpenAICostsView.register_get(router, 'openai-costs/')
