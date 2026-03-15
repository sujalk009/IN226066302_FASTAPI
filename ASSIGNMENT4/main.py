from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="My E-commerce Store API - Day 5 Cart System")

# ── Product Data ──────────────────────────────────────────────
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499,  "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook",       "price": 99,   "category": "Stationery",  "in_stock": True},
    {"id": 3, "name": "USB Hub",        "price": 799,  "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set",        "price": 49,   "category": "Stationery",  "in_stock": True},
]

# ── In-memory storage ─────────────────────────────────────────
cart   = []
orders = []

# ── Pydantic Model ────────────────────────────────────────────
class CheckoutRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    delivery_address: str = Field(..., min_length=10)

# ── Helper ────────────────────────────────────────────────────
def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None


# ══════════════════════════════════════════════════════════════
# GET /products — View all products
# ══════════════════════════════════════════════════════════════
@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}


# ══════════════════════════════════════════════════════════════
# Q1 — POST /cart/add — Add item to cart
# ══════════════════════════════════════════════════════════════
@app.post("/cart/add")
def add_to_cart(
    product_id: int = Query(..., description="Product ID to add"),
    quantity:   int = Query(1, gt=0, description="Quantity to add"),
):
    # Check product exists
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check product is in stock
    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    # Check if product already in cart → update quantity
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"]  = item["unit_price"] * item["quantity"]
            return {"message": "Cart updated", "cart_item": item}

    # New item → add to cart
    cart_item = {
        "product_id":   product_id,
        "product_name": product["name"],
        "quantity":     quantity,
        "unit_price":   product["price"],
        "subtotal":     product["price"] * quantity,
    }
    cart.append(cart_item)
    return {"message": "Added to cart", "cart_item": cart_item}


# ══════════════════════════════════════════════════════════════
# Q2 — GET /cart — View cart
# ══════════════════════════════════════════════════════════════
@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}
    grand_total = sum(item["subtotal"] for item in cart)
    return {
        "items":       cart,
        "item_count":  len(cart),
        "grand_total": grand_total,
    }


# ══════════════════════════════════════════════════════════════
# Q5 — DELETE /cart/{product_id} — Remove item from cart
# ══════════════════════════════════════════════════════════════
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}
    raise HTTPException(status_code=404, detail="Product not found in cart")


# ══════════════════════════════════════════════════════════════
# Q5 — POST /cart/checkout — Checkout
# ══════════════════════════════════════════════════════════════
@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):
    # BONUS — empty cart check
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")

    orders_placed = []
    grand_total   = 0

    for item in cart:
        order_id = len(orders) + 1
        new_order = {
            "order_id":        order_id,
            "customer_name":   data.customer_name,
            "delivery_address":data.delivery_address,
            "product":         item["product_name"],
            "quantity":        item["quantity"],
            "total_price":     item["subtotal"],
            "status":          "confirmed",
        }
        orders.append(new_order)
        orders_placed.append(new_order)
        grand_total += item["subtotal"]

    # Clear cart after checkout
    cart.clear()

    return {
        "message":      "Checkout successful",
        "orders_placed": orders_placed,
        "grand_total":  grand_total,
    }


# ══════════════════════════════════════════════════════════════
# GET /orders — View all orders
# ══════════════════════════════════════════════════════════════
@app.get("/orders")
def get_orders():
    if not orders:
        return {"message": "No orders yet"}
    return {"orders": orders, "total_orders": len(orders)}
