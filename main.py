from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
import models
import schemas
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request, Form
from fastapi.responses import RedirectResponse



# Creates all tables (based on models.py) in the database if they don't exist yet.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Management System")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Creates a new DB session for each request, and closes it afterward.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    product_count = db.query(models.Product).count()
    customer_count = db.query(models.Customer).count()
    order_count = db.query(models.Order).count()
    total_stock = sum(inv.quantity for inv in db.query(models.Inventory).all())
    recent_orders = db.query(models.Order).order_by(models.Order.id.desc()).limit(5).all()

    return templates.TemplateResponse(request, "dashboard.html", {
        "product_count": product_count,
        "customer_count": customer_count,
        "order_count": order_count,
        "total_stock": total_stock,
        "recent_orders": recent_orders,
    })


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------- PRODUCT ENDPOINTS ----------

# CREATE a product
@app.post("/products", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(
        name=product.name,
        sku=product.sku,
        description=product.description,
        price=product.price,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


# READ all products
@app.get("/products", response_model=list[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


# READ one product by id
@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# UPDATE a product
@app.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, updated: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = updated.name
    product.sku = updated.sku
    product.description = updated.description
    product.price = updated.price

    db.commit()
    db.refresh(product)
    return product


# DELETE a product
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": f"Product {product_id} deleted successfully"}


# ---------- INVENTORY ENDPOINTS ----------

# CREATE an inventory record
@app.post("/inventory", response_model=schemas.InventoryResponse)
def create_inventory(inventory: schemas.InventoryCreate, db: Session = Depends(get_db)):
    # First, check the product actually exists before linking inventory to it.
    product = db.query(models.Product).filter(models.Product.id == inventory.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_inventory = models.Inventory(
        product_id=inventory.product_id,
        quantity=inventory.quantity,
        location=inventory.location,
    )
    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)
    return new_inventory


# READ all inventory records
@app.get("/inventory", response_model=list[schemas.InventoryResponse])
def get_inventory(db: Session = Depends(get_db)):
    return db.query(models.Inventory).all()


# READ one inventory record by id
@app.get("/inventory/{inventory_id}", response_model=schemas.InventoryResponse)
def get_inventory_item(inventory_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    return item


# UPDATE an inventory record (e.g. quantity changes, or moved location)
@app.put("/inventory/{inventory_id}", response_model=schemas.InventoryResponse)
def update_inventory(inventory_id: int, updated: schemas.InventoryCreate, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory record not found")

    item.product_id = updated.product_id
    item.quantity = updated.quantity
    item.location = updated.location

    db.commit()
    db.refresh(item)
    return item


# DELETE an inventory record
@app.delete("/inventory/{inventory_id}")
def delete_inventory(inventory_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory record not found")

    db.delete(item)
    db.commit()
    return {"message": f"Inventory record {inventory_id} deleted successfully"}


# BONUS: get all inventory for a specific product
# This is where the relationship() we defined in models.py pays off.
@app.get("/products/{product_id}/inventory", response_model=list[schemas.InventoryResponse])
def get_product_inventory(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.inventory   # <-- this works because of the relationship() link


# ---------- CUSTOMER ENDPOINTS ----------

@app.post("/customers", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    new_customer = models.Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        address=customer.address,
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


@app.get("/customers", response_model=list[schemas.CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()


@app.get("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.put("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(customer_id: int, updated: schemas.CustomerCreate, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.name = updated.name
    customer.email = updated.email
    customer.phone = updated.phone
    customer.address = updated.address

    db.commit()
    db.refresh(customer)
    return customer


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()
    return {"message": f"Customer {customer_id} deleted successfully"}

# ---------- ORDER ENDPOINTS ----------

@app.post("/orders", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # 1. Make sure the customer actually exists
    customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # 2. Validate every item BEFORE creating anything —
    #    check the product exists AND there's enough stock.
    for item in order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        # Sum up all inventory records for this product across locations
        total_stock = sum(inv.quantity for inv in product.inventory)
        if total_stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {item.product_id}. Available: {total_stock}, requested: {item.quantity}"
            )

    # 3. All checks passed — now actually create the order
    new_order = models.Order(customer_id=order.customer_id, status="pending")
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # 4. Create each OrderItem, and reduce inventory accordingly
    for item in order.items:
        new_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
        )
        db.add(new_item)

        # Reduce stock: pull from inventory records until the quantity is covered
        remaining = item.quantity
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        for inv in product.inventory:
            if remaining <= 0:
                break
            deduct = min(inv.quantity, remaining)
            inv.quantity -= deduct
            remaining -= deduct

    db.commit()
    db.refresh(new_order)
    return new_order


@app.get("/orders", response_model=list[schemas.OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()


@app.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    db.commit()
    db.refresh(order)
    return order

# ---------- UI ROUTES: PRODUCTS ----------

@app.get("/ui/products")
def ui_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return templates.TemplateResponse(request, "products.html", {"products": products})


@app.post("/ui/products/create")
def ui_create_product(
    name: str = Form(...),
    sku: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    db: Session = Depends(get_db),
):
    new_product = models.Product(name=name, sku=sku, description=description or None, price=price)
    db.add(new_product)
    db.commit()
    return RedirectResponse(url="/ui/products", status_code=303)


@app.post("/ui/products/{product_id}/delete")
def ui_delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return RedirectResponse(url="/ui/products", status_code=303)

# ---------- UI ROUTES: INVENTORY ----------

@app.get("/ui/inventory")
def ui_inventory(request: Request, db: Session = Depends(get_db)):
    inventory = db.query(models.Inventory).all()
    products = db.query(models.Product).all()
    return templates.TemplateResponse(request, "inventory.html", {"inventory": inventory, "products": products})


@app.post("/ui/inventory/create")
def ui_create_inventory(
    product_id: int = Form(...),
    quantity: int = Form(...),
    location: str = Form(""),
    db: Session = Depends(get_db),
):
    new_item = models.Inventory(product_id=product_id, quantity=quantity, location=location or None)
    db.add(new_item)
    db.commit()
    return RedirectResponse(url="/ui/inventory", status_code=303)


@app.post("/ui/inventory/{inventory_id}/delete")
def ui_delete_inventory(inventory_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url="/ui/inventory", status_code=303)

# ---------- UI ROUTES: CUSTOMERS ----------

@app.get("/ui/customers")
def ui_customers(request: Request, db: Session = Depends(get_db)):
    customers = db.query(models.Customer).all()
    return templates.TemplateResponse(request, "customers.html", {"customers": customers})


@app.post("/ui/customers/create")
def ui_create_customer(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    address: str = Form(""),
    db: Session = Depends(get_db),
):
    new_customer = models.Customer(name=name, email=email, phone=phone or None, address=address or None)
    db.add(new_customer)
    db.commit()
    return RedirectResponse(url="/ui/customers", status_code=303)


@app.post("/ui/customers/{customer_id}/delete")
def ui_delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if customer:
        db.delete(customer)
        db.commit()
    return RedirectResponse(url="/ui/customers", status_code=303)

# ---------- UI ROUTES: ORDERS ----------

@app.get("/ui/orders")
def ui_orders(request: Request, db: Session = Depends(get_db)):
    orders = db.query(models.Order).all()
    customers = db.query(models.Customer).all()
    products = db.query(models.Product).all()
    return templates.TemplateResponse(
        request, "orders.html", {"orders": orders, "customers": customers, "products": products}
    )


@app.post("/ui/orders/create")
async def ui_create_order(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    customer_id = int(form["customer_id"])
    product_ids = form.getlist("product_id")
    quantities = form.getlist("quantity")

    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Validate stock for every item first
    for pid, qty in zip(product_ids, quantities):
        product = db.query(models.Product).filter(models.Product.id == int(pid)).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {pid} not found")
        total_stock = sum(inv.quantity for inv in product.inventory)
        if total_stock < int(qty):
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")

    new_order = models.Order(customer_id=customer_id, status="pending")
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for pid, qty in zip(product_ids, quantities):
        pid, qty = int(pid), int(qty)
        db.add(models.OrderItem(order_id=new_order.id, product_id=pid, quantity=qty))

        remaining = qty
        product = db.query(models.Product).filter(models.Product.id == pid).first()
        for inv in product.inventory:
            if remaining <= 0:
                break
            deduct = min(inv.quantity, remaining)
            inv.quantity -= deduct
            remaining -= deduct

    db.commit()
    return RedirectResponse(url="/ui/orders", status_code=303)


@app.post("/ui/orders/{order_id}/status")
def ui_update_order_status(order_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order:
        order.status = status
        db.commit()
    return RedirectResponse(url="/ui/orders", status_code=303)