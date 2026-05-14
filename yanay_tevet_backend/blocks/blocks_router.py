from blocks.views.blocks_views.create_block_item_view import PostCreateBlockItemView
from blocks.views.blocks_views.delete_block_item_view import DeleteBlockItemView
from blocks.views.blocks_views.download_block_by_id_view import DownloadBlockByIdView
from blocks.views.blocks_views.pagination_blocks_view import PaginationBlockView
from blocks.views.blocks_views.read_block_item_view import ReadBlockItemView
from blocks.views.blocks_views.run_action_build_block_item_view import RunActionBuildBlockItemView
from blocks.views.blocks_views.update_block_item_view import UpdateBlockItemView
from blocks.views.blocks_views.upload_data_to_block_by_id_view import UploadDataToBlockByIdView
from blocks.views.files_views.download_blocks_count_view import DownloadBlocksCountView
from blocks.views.files_views.upload_files_sum_size_view import UploadFilesSumSizeView
from blocks.views.post_sample_websocket_view import PostSampleWebsocketView
from common.django_utils.api_router_creator import ApiRouterCreator

api, router = ApiRouterCreator.create_api_and_router('blocks')

PaginationBlockView.register_get(router, '')
PostCreateBlockItemView.register_post(router)
ReadBlockItemView.register_get_by_id(router)
UpdateBlockItemView.register_patch_by_id(router)
DeleteBlockItemView.register_delete_by_id(router)
RunActionBuildBlockItemView.register_post_by_id(router, 'build/')
DownloadBlockByIdView.register_get_by_id(router, 'download/')
UploadDataToBlockByIdView.register_post_by_id(router, 'upload/')

DownloadBlocksCountView.register_get(router, 'download-count/')
UploadFilesSumSizeView.register_post(router, 'upload-sum-size/')
PostSampleWebsocketView.register_post(router, 'websocket-test/')
