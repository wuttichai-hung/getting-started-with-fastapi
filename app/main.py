from fastapi import FastAPI, Depends
from app.database import engine, SessionLocal
from app import models, schemas, crud
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# create item
@app.post("/items/")
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)

# get item by id
@app.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    return crud.get_item(db=db, item_id=item_id)

# update item
@app.put("/items/{item_id}")
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    return crud.update_item(db=db, item_id=item_id, item=item)

# delete item
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    return crud.delete_item(db=db, item_id=item_id)