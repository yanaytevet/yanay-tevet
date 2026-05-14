# Django Patterns Reference

## Model Patterns

Import related models at the top of the file. Async FK getters use `.afirst()` and always declare `-> X | None`.

```python
from myapp.models.post import Post

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    async def get_post(self) -> Post | None:
        return await Post.objects.filter(id=self.post_id).afirst()
```

Declare reverse managers in the `TYPE_CHECKING` block:

```python
if TYPE_CHECKING:
    from django.db.models import Manager
    from myapp.models.comment import Comment
    comments: 'Manager[Comment]'
```

---

## Enums

All enums in an app's `enums/` directory, extend `BaseEnum`:

```python
from common.base_enum import BaseEnum

class MyVisibility(BaseEnum):
    PUBLIC = 'public'
    HIDDEN = 'hidden'
```

Use `.choices()` (classmethod, not property) in model field definitions.

---

## Never Use `getattr`/`setattr`

Always use explicit `if`/`elif` or `match`/`case`:

```python
# Bad
setattr(obj, field_name, new_list)

# Good
if condition_type == ConditionTypes.TYPE_A:
    obj.type_a_items = new_list
elif condition_type == ConditionTypes.TYPE_B:
    obj.type_b_items = new_list
```

---

## Manager Sub-Modules

When a domain area has multiple managers, group them in a sub-module under `managers/`:

```
myapp/managers/
├── content_managers/
│   ├── __init__.py
│   ├── published_content_manager.py
│   └── draft_content_manager.py
├── media_managers/
└── websocket_events_manager/
```

Always create a sub-module when adding a second manager for the same domain.

---

## Ordering / Priority (Reorder Pattern)

1. In `run_action`, offset the `order`/`priority` field by ±1.5 and save.
2. Call a manager method that re-numbers all rows sequentially (1.0, 2.0, 3.0…) ordered by `(order, id)`.
3. Send the WebSocket update after recalc.

```python
async def update_item_orders(self) -> None:
    count = 1.0
    items = []
    async for item in self.parent.items.order_by('order', 'id').all():
        item.order = count
        count += 1.0
        items.append(item)
    await MyModel.objects.abulk_update(items, ['order'])
```

Use `FloatField` (not `IntegerField`) for order/priority fields so the ±1.5 offset works cleanly.
