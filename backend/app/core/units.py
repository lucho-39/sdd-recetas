"""Catalog whitelists shared by the ingredient endpoints.

Kept outside the routers so the admin routes and the public v1 routes
validate against the same set instead of carrying two copies that drift.
"""

VALID_UNITS = {
    "g",
    "kg",
    "ml",
    "l",
    "unidad",
    "cucharada",
    "cucharadita",
    "taza",
    "pizca",
}

VALID_CATEGORIES = {
    "proteina",
    "verdura",
    "fruta",
    "lacteo",
    "grano",
    "condimento",
    "grasa",
    "otro",
}
