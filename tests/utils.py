def refresh(obj):
    return obj.__class__._base_manager.get(pk=obj.pk)
