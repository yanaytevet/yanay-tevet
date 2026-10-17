# Backend conventions

How the Django code in `yanay_tevet_backend/` is put together. CLAUDE.md's Hard Rules — imports at the
top, no `getattr`/`setattr`, no `@property` on models, permission checks in checker classes, business
logic in managers, no schema field named after its type — hold throughout and are not repeated here.
`blocks/` is a worked example of nearly every view type and the place to see one in isolation;
`task_management/` is the most complete real app — a gated router, a membership checker, managers,
sharing, reordering — and the model to copy for a new one.

## An app's layout

```
task_management/
├── models/                     # one model per file
├── enums/
├── serializers/                # output schema + its serializer, grouped by resource: task_serializers/, …
├── views/                      # one view per file, grouped by resource: project_views/, task_views/
├── managers/                   # domain logic that is not a view
├── permissions_checkers/
└── task_management_router.py   # registers the views; mounted in yanay_tevet_backend/urls.py
```

An input schema is declared in the view file that takes it; one shared between views (such as
`TaskWritableSchema`) sits with the serializer. `users`, `japanese` and `mcp_server` also keep a
`schemas/` package.

## Adding an app

1. Create it under `yanay_tevet_backend/` in the layout above and add it to `INSTALLED_APPS`.
2. If it is gated, add a member to `users/enums/permissions.py` and a `HasPermissionChecker` subclass for
   it (`TaskManagementPermissionChecker` is the whole pattern), and pass that to the router.
3. Mount the router in `yanay_tevet_backend/urls.py` as `path(r'api/<name>/', <app>_api.urls)`. Keep the
   `r` prefix: `create-api` finds the routers with a regex that only matches `path(r'…'`, and a router it
   misses gets no generated client.
4. `bash run_manage.sh makemigrations` + `migrate`, then `npm run create-api` with the backend up.
5. The frontend side — route, `RoutingService` methods, home tile, nav drawer — is `docs/frontend.md`
   and CLAUDE.md's rule about linking a new app.

## Views: `common/simple_api`

Every endpoint is an async class-based view on top of Django Ninja. A view is a class of classmethods,
and the app's router registers it:

```python
api, router = ApiRouterCreator.create_api_and_router('task-management', TaskManagementPermissionChecker())

PaginateTaskProjectsView.register_get(router, 'projects/')
CreateTaskProjectView.register_post(router, 'projects/')
UpdateTaskProjectView.register_patch_by_id(router, prefix='projects')
```

A checker passed to `create_api_and_router` becomes the router's Ninja `auth`, so it runs before every
endpoint on it and the views add only the object-level check. Without one, each view checks for itself
(`blocks` does this with `LoginPermissionChecker`).

| Base class | Endpoint | Registered with |
|---|---|---|
| `CreateItemAPIView` | POST that creates a model | `register_post(router, url='')` |
| `ReadItemByIdAPIView` | GET `/{object_id}/<suffix>` | `register_get_by_id(router, suffix='')` |
| `UpdateItemByIdAPIView` | PATCH `<prefix>/{object_id}/<suffix>` | `register_patch_by_id(router, prefix='', suffix='')` |
| `DeleteItemByIdAPIView` | DELETE `<prefix>/{object_id}/<suffix>` | `register_delete_by_id(router, prefix='', suffix='')` |
| `RunActionOnItemByIdAPIView` | POST `/{object_id}/<suffix>` | `register_post_by_id(router, '<suffix>')` |
| `PaginateItemsAPIView` | GET, paginated, filtered and ordered | `register_get(router, '<url>')` |
| `SimpleGetAPIView` / `SimplePostAPIView` | a custom GET / POST with no model behind it | `register_get` / `register_post(router, '<url>')` |

The by-id classes also inherit the plain `register_get` / `register_patch` / `register_delete` /
`register_post`, which take the whole URL; `task_management` uses them to put the id under a resource
prefix (`ShareTaskProjectView.register_post(router, 'projects/{int:object_id}/share/')`). Each by-id view
also comes without `ById` (`ReadItemAPIView`, `UpdateItemAPIView`, …) for an object found some other
way. Files go through `UploadFilesByIdView` and `DownloadFileByIdView` (examples in
`blocks/views/blocks_views/`).

What a view must and may define:

- **Create** — must: `check_permitted_before_creation`, `get_model_cls`, `get_serializer`,
  `get_data_schema`; may: `modify_creation_data`, `run_before_creation`, `run_after_creation`, or
  `create_object` to hand creation to a manager (`CreateTaskView`).
- **Read / update / delete by id** — must: `check_permitted_before_object`,
  `check_permitted_after_object`, `get_model_cls`; read and update also `get_serializer`, update also
  `get_data_schema`; may: `run_after_get`, `run_before_update`, `apply_post_update_pre_save_changes`,
  `run_after_update`, `run_before_deletion`, `run_after_deletion`.
- **Run action** — also `get_serializer`, `get_data_schema` and `run_action`. Returning `None`
  re-serializes the object with the view's serializer; return a schema to answer with something else.
- **Paginate** — must: `check_permitted_before_pagination`, `get_model_cls`, `get_serializer`,
  `get_filter_schema`, `get_allowed_order_by`; may: `apply_initial_filter_and_order` (async; defaults to
  ordering by `id`), `apply_dict_filter`, `apply_final_filter`.
- **Simple** — `check_permitted`, `get_output_schema`, and `get_data` (GET) or `run_action` plus
  `get_data_schema` (POST); `get_path_args_schema` for path parameters (`ReorderTasksView`).

The by-id views load the object through `ItemByIdAPIMixin.get_object`, which reads `path.object_id` and
raises `ObjectDoesntExistAPIException` when there is no such row; override it for any other lookup.

A field the server fills in rather than the client — an owner id — goes on the input schema as
`Optional[int] = None`, is hidden from the OpenAPI schema with `model_config =
hidden_fields_config('owner_id')` (`common/simple_api/schemas/schema_config.py`), and is set in
`modify_creation_data`. `CreateTaskProjectView` does exactly this.

### Permission checks

`check_permitted_before_object` runs before the object is loaded and is `pass`. The check lives in
`check_permitted_after_object`, which has the object. Django Ninja reads these signatures, so they must
match exactly:

| View | `check_permitted_before_object` | `check_permitted_after_object` |
|---|---|---|
| `ReadItemByIdAPIView` | `(cls, request, query, path)` | `(cls, request, obj, query, path)` |
| `UpdateItemByIdAPIView`, `DeleteItemByIdAPIView`, `RunActionOnItemByIdAPIView` | `(cls, request, data, path)` | `(cls, request, obj, data, path)` |
| `UploadFilesByIdView` | `(cls, request, path)` | `(cls, request, obj, path)` |
| `DownloadFileByIdView` | `(cls, request, query, path)` | `(cls, request, obj, query, path)` |

The user is a future on the request:

```python
@classmethod
async def check_permitted_after_object(cls, request: APIRequest, obj: TaskProject, query: Query, path: Path) -> None:
    await ProjectMemberPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)
```

A checker subclasses `PermissionsChecker` and lives in its app's `permissions_checkers/`; one that needs
the object takes it in `__init__` (`ProjectMemberPermissionChecker(project, require_owner=True)`). The
built-ins are `LoginPermissionChecker` and `NotLoggedInPermissionChecker` in
`common/simple_api/permissions_checkers/`, and `AdminPermissionsChecker` and `HasPermissionChecker` in
`users/permissions_checkers/`. A checker raises `RestAPIException(status_code=…, message=…,
error_code=…)`.

## Serializers

```python
class TaskSerializer(Serializer[TaskSchema]):
    async def inner_serialize(self, obj: Task) -> TaskSchema:
        return TaskSchema(id=obj.id, ...)
```

The output schema is read off `inner_serialize`'s return annotation — a missing annotation raises. Every
output schema has its serializer and is built only there: reuse the serializer rather than constructing
the schema inline in a view.

## Models

Foreign keys are read through async getters that use `.afirst()` and admit the row may be gone:

```python
async def get_project(self) -> TaskProject | None:
    return await TaskProject.objects.filter(id=self.project_id).afirst()
```

The attributes Django adds at runtime — `id`, each `<fk>_id`, reverse managers — are declared for the
type checker in a `TYPE_CHECKING` block in the class body. A reverse manager's model would make a
circular import, so that one import goes in a module-level `TYPE_CHECKING` block:

```python
if TYPE_CHECKING:
    from shopping_lists.models.shopping_item import ShoppingItem


class ShoppingList(models.Model):
    if TYPE_CHECKING:
        id: int
        owner_id: int
        items: Manager['ShoppingItem']
```

## Enums

Each app keeps its enums in its own `enums/`, as subclasses of `common/base_enum.py`'s `BaseEnum` (a
`StrEnum`). A model field takes `MyEnum.choices()` — a classmethod — and `MyEnum.get_list()` gives the
values. A parameter that always holds an enum value is typed as the enum, never as `str`.

## Tests

Django's own runner, against the dev Postgres and Redis (`start_dev.sh` first): from `deploy/dev_scripts/`,
`bash run_manage.sh test`, or `bash run_manage.sh test users` for one app. Tests live in each app's
`tests/` package and use `SimpleTestCase` when they need no database, `TestCase` otherwise, with `async def`
test methods. `common/testing/authenticated_client.py` calls the API as a given user.

- A websocket consumer test needs `TransactionTestCase`: channels closes the database connection around
  each frame, which would close a `TestCase`'s wrapping transaction with it.
- Override `CHANNEL_LAYERS` with `InMemoryChannelLayer` in a test that sends on the channel layer.

## Background work

Work that outlives a request runs in-process: `run_in_background(coro)` in
`common/async_utils/background_task_runner.py` gives the coroutine its own thread and event loop, and a
websocket event reports when it is done (`japanese` content generation is the user). Celery is set up in
`yanay_tevet_backend/celery.py` (queues `main` and `emails`, one beat task) but is dormant: no code
enqueues a task and `settings.py` has no `CELERY_BROKER_URL`, so the dev stack runs no worker.
`run_backend_worker.sh` and `run_backend_celery_beat.sh` start one by hand once a broker is set.
