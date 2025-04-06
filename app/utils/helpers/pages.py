def get_predefined_pages() -> list[dict]:
    return [
        {"id": 1, "name": "Home", "endpoint": "web_front.index"},
        {"id": 2, "name": "Orders", "endpoint": "web_front.orders"},
        {"id": 3, "name": "Add Balance", "endpoint": "web_front.top_up"},
        {"id": 4, "name": "Sign Out", "endpoint": "web_front.logout"},
        {"id": 5, "name": "Store", "endpoint": "web_front.products"},
    ]