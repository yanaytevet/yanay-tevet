from common.django_utils.api_router_creator import ApiRouterCreator
from japanese.views.approve_node_view import ApproveNodeView
from japanese.views.generate_content_view import GenerateContentView
from japanese.views.get_random_nodes_view import GetRandomNodesView
from japanese.views.get_review_queue_view import GetReviewQueueView
from japanese.views.ingest_node_view import IngestNodeView
from japanese.views.read_node_view import ReadNodeView
from japanese.views.update_node_title_view import UpdateNodeTitleView


api, router = ApiRouterCreator.create_api_and_router('japanese')

ReadNodeView.register_get_by_id(router)
GetRandomNodesView.register_get(router, 'random/')
GetReviewQueueView.register_get(router, 'review-queue/')
IngestNodeView.register_post(router, 'ingest/')
GenerateContentView.register_post_by_id(router, 'generate/')
ApproveNodeView.register_post_by_id(router, 'approve/')
UpdateNodeTitleView.register_post_by_id(router, 'update-title/')
