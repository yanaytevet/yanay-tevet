from blocks import models
from blocks.models import Block
from blocks.views.blocks_views.download_block_by_id_view import DownloadBlockByIdView
from common.admin_utils.admin_action import AdminAction
from common.admin_utils.register_models_to_admin import ModelRegisterer

async def toggle_block(obj_id: int) -> None:
    block = await Block.objects.filter(id=obj_id).afirst()
    block.c = not block.c
    await block.asave()


ModelRegisterer(models,
                actions_by_model={
                    models.Block: [
                        AdminAction(label='Download Report', download_file_by_id_view_class=DownloadBlockByIdView),
                        AdminAction(label='Toggle C', callback=toggle_block),
                    ]
                }).register()
    