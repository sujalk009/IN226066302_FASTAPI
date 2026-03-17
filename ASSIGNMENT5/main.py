from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="My E-commerce Store API - Day 6")

# ── Product Data ──────────────────────────────────────────────
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook",       "price": 99,  "category": "Stationery",  "in_stock": True},
    {"id": 3, "name": "USB Hub",        "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set",        "price": 49,  "category": "Stationery",  "in_stock": True},
]

# ── In-memory orders list ─────────────────────────────────────
orders = []

# ── Pydantic Model ────────────────────────────────────────────
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id:    int = Field(..., gt=0)
    quantity:      int = Field(..., gt=0, le=50)

# ── Helper ────────────────────────────────────────────────────
def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None


# ══════════════════════════════════════════════════════════════
# GET /products — All products
# ══════════════════════════════════════════════════════════════
@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}


# ══════════════════════════════════════════════════════════════
# Q1 — GET /products/search — Search by keyword (case-insensitive)
# ══════════════════════════════════════════════════════════════
@app.get("/products/search")
def search_products(keyword: str = Query(..., description="Search keyword")):
    results = [p for p in products if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message": f"No products found for: {keyword}"}
    return {"keyword": keyword, "total_found": len(results), "products": results}


# ══════════════════════════════════════════════════════════════
# Q2 — GET /products/sort — Sort by price or name
# ══════════════════════════════════════════════════════════════
@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price", description="Sort by 'price' or 'name'"),
    order:   str = Query("asc",   description="'asc' or 'desc'"),
):
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    reverse = (order == "desc")
    sorted_products = sorted(products, key=lambda p: p[sort_by], reverse=reverse)
    return {
        "sort_by":  sort_by,
        "order":    order,
        "products": sorted_products,
        "total":    len(sorted_products),
    }


# ══════════════════════════════════════════════════════════════
# Q3 — GET /products/page — Paginate products
# ══════════════════════════════════════════════════════════════
@app.get("/products/page")
def get_products_paged(
    page:  int = Query(1, ge=1,  description="Page number"),
    limit: int = Query(2, ge=1, le=20, description="Items per page"),
):
    start       = (page - 1) * limit
    paged       = products[start: start + limit]
