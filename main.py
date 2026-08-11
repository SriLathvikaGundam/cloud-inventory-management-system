from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
import models
import schemas

# Creates all tables (based on models.py) in the database if they don't exist yet.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Management System")


# Creates a new DB session for each request, and closes it afterward.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Inventory API is running"}


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