from fastapi import FastAPI,Query
from pydantic import BaseModel, Field
from typing import Optional
from typing import List 


app = FastAPI()

class OrderRequest(BaseModel):

    customer_name:    str = Field(..., min_length=2, max_length=100)

    product_id:       int = Field(..., gt=0)

    quantity:         int = Field(..., gt=0, le=100)

    delivery_address: str = Field(..., min_length=10)

class CustomerFeedback(BaseModel):
    customer_name: str            = Field(..., min_length=2, max_length=100)
    product_id:   int            = Field(..., gt=0)
    rating:       int            = Field(..., ge=1, le=5)
    comment:      Optional[str]  = Field(None, max_length=300)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity:   int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name:  str           = Field(..., min_length=2)
    contact_email: str           = Field(..., min_length=5)
    items:         List[OrderItem] = Field(..., min_items=1)
# ── Temporary data — acting as our database for now ──────────

products = [

    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook',       'price':  99,  'category': 'Stationery',  'in_stock': True},
    {'id': 3, 'name': 'USB Hub',        'price': 799,  'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',        'price':  49,  'category': 'Stationery',  'in_stock': True},

    # NEW PRODUCTS
    {'id': 5, 'name': 'Laptop Stand', 'price': 1299, 'category': 'Electronics', 'in_stock': True},
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 2499, 'category': 'Electronics', 'in_stock': True},
    {'id': 7, 'name': 'Webcam', 'price': 1899, 'category': 'Electronics', 'in_stock': False},
]
orders = []
feedback = []

order_counter = 1

# ══ HELPER FUNCTIONS ═══════════════════════════════════════

def find_product(product_id: int):

    for p in products:

        if p['id'] == product_id:

            return p

    return None

 

def calculate_total(product: dict, quantity: int) -> int:

    return product['price'] * quantity

 

def filter_products_logic(category=None, min_price=None,

                          max_price=None, in_stock=None):

    result = products

    if category  is not None: result = [p for p in result if p['category']==category]

    if min_price is not None: result = [p for p in result if p['price']>=min_price]

    if max_price is not None: result = [p for p in result if p['price']<=max_price]

    if in_stock  is not None: result = [p for p in result if p['in_stock']==in_stock]

    return result

 


# ── Endpoint 0 — Home ────────────────────────────────────────

@app.get('/')

def home():

    return {'message': 'Welcome to our E-commerce API'}

 

@app.get('/products/compare')

def compare_products(product_id_1:int=Query(...), product_id_2:int=Query(...)):

    p1 = find_product(product_id_1)

    p2 = find_product(product_id_2)

    if not p1: return {'error': f'Product {product_id_1} not found'}

    if not p2: return {'error': f'Product {product_id_2} not found'}

    cheaper = p1 if p1['price'] < p2['price'] else p2

    return {'product_1':p1,'product_2':p2,

'better_value':cheaper['name'],

'price_diff':abs(p1['price']-p2['price'])}


# ── Endpoint 1 — Return all products ──────────────────────────
@app.get("/products/summary")
def product_summary():
    in_stock   = [p for p in products if     p["in_stock"]]
    out_stock  = [p for p in products if not p["in_stock"]]
    expensive  = max(products, key=lambda p: p["price"])
    cheapest   = min(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))
    return {
        "total_products":     len(products),
        "in_stock_count":     len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive":     {"name": expensive["name"], "price": expensive["price"]},
        "cheapest":           {"name": cheapest["name"],  "price": cheapest["price"]},
        "categories":         categories,
    }
@app.get('/products')

def get_all_products():

    return {'products': products, 'total': len(products)}


@app.get('/products/filter')

def filter_products(

    category:  str  = Query(None, description='Electronics or Stationery'),

    max_price: int  = Query(None, description='Maximum price'),
     min_price: int = Query(None, description='Minimum price'),
    in_stock:  bool = Query(None, description='True = in stock only')

):

    result = products          # start with all products

 

    if category:

        result = [p for p in result if p['category'] == category]

 

    if min_price is not None:
        result = [p for p in result if p['price'] >= min_price]

    if max_price :
        result = [p for p in result if p['price'] <= max_price]

    if in_stock is not None:

        result = [p for p in result if p['in_stock'] == in_stock]

 

    return {'filtered_products': result, 'count': len(result)}

 

# ── Endpoint 2 — Return one product by its ID ──────────────────
@app.get("/store/summary")
def store_summary():

    in_stock_count = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count
    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": categories
    }

@app.get("/products/deals")
def get_deals():

    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }

@app.get('/products/instock')
def get_instock():
    available=[p for p in products if p['in_stock']==True]
    return {
        "in_stock_products":available,
        "count": len(available)
        
    }


@app.get('/products/{product_id}')

def get_product(product_id: int):

    for product in products:

        if product['id'] == product_id:

            return {'product': product}

    return {'error': 'Product not found'}


@app.get('/products/category/{category_name}')
def get_by_category(category_name: str):

    result = [p for p in products if p["category"] == category_name]

    if not result:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": result,
        "total": len(result)
    }


@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": "No products matched your search"}

    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }



@app.post('/orders')

def place_order(order_data: OrderRequest):

    global order_counter

    product = next((p for p in products if p['id']==order_data.product_id), None)

    if product is None:          return {'error': 'Product not found'}

    if not product['in_stock']:  return {'error': f"{product['name']} is out of stock"}

    total_price = product['price'] * order_data.quantity

    order = {'order_id': order_counter, 'customer_name': order_data.customer_name,

'product': product['name'], 'quantity': order_data.quantity,

'delivery_address': order_data.delivery_address,

'total_price': total_price, 'status': 'pending'}

    orders.append(order)

    order_counter += 1

    return {'message': 'Order placed successfully', 'order': order}

 

@app.get('/orders')

def get_all_orders():

    return {'orders': orders, 'total_orders': len(orders)}




@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"name": product["name"], "price": product["price"]}
    return {"error": "Product not found"}


@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message":        "Feedback submitted successfully",
        "feedback":       data.dict(),
        "total_feedback": len(feedback),
    }


@app.get("/products/summary")
def product_summary():
    in_stock   = [p for p in products if     p["in_stock"]]
    out_stock  = [p for p in products if not p["in_stock"]]
    expensive  = max(products, key=lambda p: p["price"])
    cheapest   = min(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))
    return {
        "total_products":     len(products),
        "in_stock_count":     len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive":     {"name": expensive["name"], "price": expensive["price"]},
        "cheapest":           {"name": cheapest["name"],  "price": cheapest["price"]},
        "categories":         categories,
    }

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = find_product(item.product_id)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })

        elif not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })

        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal

            confirmed.append({
                "product": product["name"],
                "qty": item.quantity,
                "subtotal": subtotal
            })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }



@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}
    return {"error": "Order not found"}

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return {"message": "Order confirmed", "order": order}
    return {"error": "Order not found"}