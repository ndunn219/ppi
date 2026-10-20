def shell(request):
    """Values every page's sidebar and header read."""
    return {"nav_active": getattr(request, "nav_active", "")}
