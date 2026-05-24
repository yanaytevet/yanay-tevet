---
name: backend
description: This skill should be used when working on the Django 5 backend, creating API endpoints, defining models, writing serializers, implementing views, adding migrations, or writing any Python code in yanay_tevet_backend/.
---

# Backend Development — Django 5

## Stack & Structure

Django Ninja (API), Channels (WebSockets), PostgreSQL, Redis, Pydantic, JWT auth.

```
yanay_tevet_backend/
├── users/            # Auth and user management
├── blocks/           # Reference implementation
├── common/           # Shared framework (simple_api, etc.)
├── configurations/   # Settings
└── yanay_tevet_backend/  # Django project root
```

Backend commands run via Docker. **Run from `deploy/dev_scripts/` — scripts use relative paths:**
```bash
cd deploy/dev_scripts
bash run_manage.sh migrate
bash run_manage.sh makemigrations
```

---

## Critical Rules

### Always Import at the Top

Import at the top of every Python file — models, managers, serializers, views, permission checkers, everywhere. Never use:
- String type annotations: `'Item'`
- String FK references: `'myapp.Item'`
- Lazy imports inside methods or `__init__`

```python
# Bad
item = models.ForeignKey('myapp.Item', ...)

# Good
from myapp.models.item import Item
item = models.ForeignKey(Item, on_delete=models.CASCADE, ...)
```

### Always Run Migrations After Model Changes

After adding, removing, or modifying any model field:
1. `bash run_manage.sh makemigrations`
2. `bash run_manage.sh migrate`

Never leave model changes without a migration. The backend won't start with unapplied migrations.

### Never Use `getattr`/`setattr`

Always use explicit `if`/`elif` or `match`/`case`. Dynamic attribute access hides intent and bypasses type checking.

---

## `common/simple_api` View Framework

All endpoints are built on a custom async class-based view layer in `common/simple_api/`, on top of Django Ninja. Every view is a class with classmethods; instantiation happens inside the registered handler.

Each app has a `*_router.py` that registers views:
```python
from common.django_utils.api_router_creator import ApiRouterCreator

api, router = ApiRouterCreator.create_api_and_router('items')
CreateItemView.register_post(router)
GetItemByIdView.register_get_by_id(router)
```

Every view receives an `APIRequest`. Resolve the user asynchronously:
```python
user = await request.future_user
```

### View Base Classes (summary)

| Class | Method | Register |
|---|---|---|
| `CreateItemAPIView` | POST — create model | `register_post(router)` |
| `ReadItemByIdAPIView` | GET `/{id}/` | `register_get_by_id(router)` |
| `UpdateItemByIdAPIView` | PATCH `/{id}/` | `register_patch_by_id(router)` |
| `DeleteItemByIdAPIView` | DELETE `/{id}/` | `register_delete_by_id(router)` |
| `RunActionOnItemByIdAPIView` | POST `/{id}/action/` | `register_post_by_id(router, 'name')` |
| `PaginateItemsAPIView` | GET with pagination | `register_get(router, 'url')` |
| `SimpleGetAPIView` | Custom GET, no model | `register_get(router, 'url')` |
| `SimplePostAPIView` | Custom POST, no model | `register_post(router, 'url')` |

`check_permitted_before_object` should always `pass`. `check_permitted_after_object` is where permissions are checked using the loaded object. **Signatures differ by view type — see references for the exact signatures.**

### Serializers

```python
class ItemSerializer(Serializer):
    async def inner_serialize(self, obj: Item) -> ItemSchema:
        return ItemSchema(id=obj.id, name=obj.name, ...)
```

`get_output_schema()` is derived automatically from the return type annotation. Every output schema must have a paired serializer — never construct schema instances inline. If a serializer already exists, use it.

### Permission Checkers

Permission checks **must** live in `PermissionsChecker` subclasses, never inline in views. Use the existing checkers before writing new ones:

| Checker | Location |
|---|---|
| `LoginPermissionChecker` | `common/simple_api/permissions_checkers/` |
| `NotLoggedInPermissionChecker` | `common/simple_api/permissions_checkers/` |
| `AdminPermissionsChecker` | `users/permissions_checkers/` (calls `LoginPermissionChecker` first, then `user.is_admin()`) |

Usage:
```python
@classmethod
async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: NinjaPath = None) -> None:
    user = await api_request.future_user
    await AdminPermissionsChecker().async_raise_exception_if_not_valid(user)
```

If no existing checker fits, add a new one under `<app>/permissions_checkers/` extending `PermissionsChecker`. **Never** write `if not user.is_admin(): raise RestAPIException(...)` inline in a view — the checker exists for a reason.

### Managers — Business Logic Lives Here

Views are thin: parse input → call permission checker → call a manager → return the output schema. **No third-party API calls, no multi-step computation, no DB orchestration in views.** All of that goes in `<app>/managers/<name>_manager.py`.

```python
# my_dashboard/managers/openai_costs_manager.py
class OpenAICostsManager:
    async def get_summary(self) -> OpenAICostsSummary:
        api_key = settings.CHATGPT_API_KEY
        # ... fetch from OpenAI, aggregate, return ...
        return OpenAICostsSummary(...)

# my_dashboard/views/get_openai_costs_view.py — thin view
class GetOpenAICostsView(SimpleGetAPIView):
    @classmethod
    async def check_permitted(cls, api_request, query=None, path=None) -> None:
        user = await api_request.future_user
        await AdminPermissionsChecker().async_raise_exception_if_not_valid(user)

    @classmethod
    async def get_data(cls, api_request, query=None, path=None) -> OpenAICostsOutput:
        summary = await OpenAICostsManager().get_summary()
        return OpenAICostsOutput(**summary.model_dump())
```

Managers typically take context (like `User`) via `__init__` and expose async methods. Reference: `dream_diary/managers/dream_diary_entry_manager.py`, `users/managers/webauthn_manager.py`.

---

## Model Patterns

- Async FK getters use `.afirst()` and always return `-> X | None` — never `-> X` alone.
- Declare reverse managers in `TYPE_CHECKING` block with `foos: 'Manager[Foo]'`.
- **No `@property`** — use regular methods instead. Properties hide that computation is happening and make it unclear in call sites.

---

## Enums

All enums in an app's `enums/` directory, extend `BaseEnum`:
```python
from common.base_enum import BaseEnum

class MyVisibility(BaseEnum):
    PUBLIC = 'public'
```

Use `.choices()` (classmethod) in model field definitions — not `.choices`.

**Always use enum types in method signatures, not `str`.** Never write `item_type: str` when the value is always an enum — use `item_type: ItemType`. This applies to all method parameters, not just models.

---

## References

For detailed patterns and full examples, consult:
- **[`references/simple-api.md`](references/simple-api.md)** — Full view base class API, `check_permitted` signature table, concrete creation example
- **[`references/django-patterns.md`](references/django-patterns.md)** — Model patterns, manager sub-modules, reorder/priority pattern
