# simple_api View Framework Reference

## Router Setup

Pass a `PermissionsChecker` to gate the **entire router** — every endpoint inherits it automatically. When you do this, individual views `pass` in all `check_permitted*` methods; they only add object-level ownership checks.

```python
from common.django_utils.api_router_creator import ApiRouterCreator
from myapp.permissions_checkers.my_feature_permission_checker import MyFeaturePermissionChecker

# Gate the whole router with a permission:
api, router = ApiRouterCreator.create_api_and_router('items', MyFeaturePermissionChecker())

CreateItemView.register_post(router)
GetItemByIdView.register_get_by_id(router)
UpdateItemView.register_patch_by_id(router)
DeleteItemView.register_delete_by_id(router)
PaginateMyItemsView.register_get(router, 'my-items')
```

---

## View Base Classes — Full API

### `CreateItemAPIView` — POST that creates a model instance
- **Abstract**: `check_permitted_before_creation`, `get_model_cls`, `get_serializer`, `get_data_schema`
- **Optional hooks**: `modify_creation_data`, `run_before_creation`, `run_after_creation`
- **Register**: `cls.register_post(router)`

### `ReadItemByIdAPIView` — GET `/{object_id}/`
- **Abstract**: `check_permitted_before_object`, `check_permitted_after_object`, `get_model_cls`, `get_serializer`
- **Register**: `cls.register_get_by_id(router)`

### `UpdateItemByIdAPIView` — PATCH `/{object_id}/`
- **Abstract**: `check_permitted_before_object`, `check_permitted_after_object`, `get_model_cls`, `get_serializer`, `get_data_schema`
- **Optional hooks**: `run_before_update`, `apply_post_update_pre_save_changes`, `run_after_update`
- **Register**: `cls.register_patch_by_id(router)`

### `DeleteItemByIdAPIView` — DELETE `/{object_id}/`
- **Abstract**: `check_permitted_before_object`, `check_permitted_after_object`, `get_model_cls`
- **Optional hooks**: `run_before_deletion`, `run_after_deletion`
- **Register**: `cls.register_delete_by_id(router)`

### `RunActionOnItemByIdAPIView` — POST `/{object_id}/action-name/`
- **Abstract**: `check_permitted_before_object`, `check_permitted_after_object`, `get_object`, `run_action`, `get_model_cls`, `get_data_schema`
- If `run_action` returns `None`, the object is re-serialized; return a schema to override
- **Register**: `cls.register_post_by_id(router, 'action-name')`

### `PaginateItemsAPIView` — GET with pagination, filtering, ordering
- **Abstract**: `check_permitted_before_pagination`, `get_model_cls`, `get_serializer`, `get_filter_schema`, `get_allowed_order_by`
- **Optional hooks**: `apply_initial_filter_and_order`, `apply_final_filter`, `apply_dict_filter`
- Filter schema uses Django Ninja's `FilterSchema` with `q=[...]` for multi-field search
- **Register**: `cls.register_get(router, 'url')`

### `SimpleGetAPIView` — custom GET, no model
- **Abstract**: `check_permitted`, `get_data`, `get_output_schema`
- **Register**: `cls.register_get(router, 'url')`

### `SimplePostAPIView` — custom POST, no model
- **Abstract**: `check_permitted`, `run_action`, `get_output_schema`, `get_data_schema`
- **Register**: `cls.register_post(router, 'url')`

---

## `check_permitted` Signatures — Must Match Exactly

Django Ninja will error if the signatures don't match. Always use exactly these:

| View base class | `check_permitted_before_object` | `check_permitted_after_object` |
|---|---|---|
| `ReadItemByIdAPIView` | `(cls, request, query, path)` | `(cls, request, obj, query, path)` |
| `UpdateItemByIdAPIView` | `(cls, request, data, path)` | `(cls, request, obj, data, path)` |
| `DeleteItemByIdAPIView` | `(cls, request, data, path)` | `(cls, request, obj, data, path)` |
| `RunActionOnItemByIdAPIView` | `(cls, request, data, path)` | `(cls, request, obj, data, path)` |
| `UploadFilesByIdView` | `(cls, request, path)` | `(cls, request, obj, path)` |

- `check_permitted_before_object` should always `pass` — the object isn't loaded yet
- `check_permitted_after_object` is where permissions are checked using the loaded `obj`
- For `ReadItemByIdAPIView` the second param is `query` (not `data`) in both hooks

```python
# ReadItemByIdAPIView
@classmethod
async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
    pass

@classmethod
async def check_permitted_after_object(cls, request: APIRequest, obj: MyModel, query: Query, path: Path) -> None:
    user = await request.future_user
    await MyPermissionChecker().async_raise_exception_if_not_valid(user, obj)

# Update / Delete / RunAction
@classmethod
async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
    pass

@classmethod
async def check_permitted_after_object(cls, request: APIRequest, obj: MyModel, data: Schema, path: Path) -> None:
    user = await request.future_user
    await MyPermissionChecker().async_raise_exception_if_not_valid(user, obj)
```

---

## `ByID` Mixin

`ItemByIdAPIMixin` provides `get_object` which fetches by `path.object_id` and raises `ObjectDoesntExistAPIException` if not found. Path schema is automatically `ItemByIdPath` (`object_id: int`). Override `get_object` for custom lookup (e.g. filtering by owner).

---

## Concrete Example

```python
class CreatePostView(CreateItemAPIView):
    @classmethod
    def get_model_cls(cls): return Post

    @classmethod
    def get_serializer(cls): return PostSerializer()

    @classmethod
    def get_data_schema(cls): return CreatePostInput

    @classmethod
    async def check_permitted_before_creation(cls, request, data, path):
        pass  # router-level checker handles it

    # Override create_object to inject FK fields (like user) not in the schema.
    # Never add user_id to the schema — override create_object instead.
    @classmethod
    async def create_object(cls, request, data, path) -> Post:
        user = await request.future_user
        return await Post.objects.acreate(
            owner_id=user.id,
            title=data.title,
            text=data.text,
        )

    @classmethod
    async def run_after_creation(cls, request, obj, data, path):
        await PostInitializer(obj).initialize()
```

---

## Ownership Permission Checker Pattern

When a model belongs to a user, create a checker that accepts the loaded object and verifies ownership. Always pair with a router-level app permission checker.

```python
# myapp/permissions_checkers/own_post_permission_checker.py
class OwnPostPermissionChecker(PermissionsChecker):
    def __init__(self, post: Post) -> None:
        self.post = post

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        if self.post.owner_id != user.id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='You do not own this post.',
                error_code='not_owner',
            )

# In the delete / update / run-action view:
@classmethod
async def check_permitted_before_object(cls, request, data, path) -> None:
    pass  # router handles app-level permission

@classmethod
async def check_permitted_after_object(cls, request, obj, data, path) -> None:
    await OwnPostPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)
```
