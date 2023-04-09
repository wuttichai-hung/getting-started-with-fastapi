# 1. Introduction

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. It is designed to be easy to use and to provide high performance out-of-the-box. FastAPI is built on top of the Starlette framework for the web parts and Pydantic for the data parts. Here are some key features of FastAPI:

1. High performance: FastAPI is built on top of Starlette, an ASGI (Asynchronous Server Gateway Interface) framework, which allows for high performance and asynchronous execution.
2. Fast development: FastAPI provides automatic generation of OpenAPI and JSON Schema documentation, as well as automatic data validation, which speeds up development time.
3. Easy to use: FastAPI is designed to be easy to use, with a simple syntax for defining endpoints and models.
4. Standards-based: FastAPI is built on top of industry-standard tools such as Pydantic for data validation and type hints, and is fully compliant with the OpenAPI standard.
5. Supports async/await: FastAPI fully supports asynchronous programming using Python's async/await syntax, allowing for efficient and non-blocking I/O operations.

In this blog post, we will explore how to create a simple FastAPI application, including the folder hierarchy, code for main.py, Dockerfile, schema.py, models.py, crud.py, and how to connect to SQLite.

# 2. The simplest FastAPI app

```python:main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

```bash:run_fastapi.sh
uvicorn main:app --reload
```

# 3. The common FastAPI app

## Folder Hierarchy

```
getting-started-with-fastapi/
├── app/
│   ├── __init__.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── Dockerfile
└── requirements.txt
```

Here's a brief explanation of what each file and folder is for:

- `app`: This folder contains the main FastAPI application code, including the main.py file, which defines the application instance and routes, and the routers folder, which contains the route handlers.
- `app/__init__.py`: This file makes the app directory a Python package.
- `app/crud.py`: This file defines the CRUD (Create, Read, Update, Delete) operations for the application.
- `app/database.py`: This file contains the code to connect to the SQLite database.
- `app/main.py`: This file defines the FastAPI application instance and routes.
- `app/models.py`: This file defines the Pydantic models used in the application.
- `app/schemas.py`: This file defines the Pydantic schemas used in the application.
- `Dockerfile`: This file defines the Docker image for the application.
- `requirements.txt`: This file specifies the Python dependencies for the application.

## main.py

```python:app/main.py
from fastapi import FastAPI
from app.database import engine, SessionLocal
from app import models, schemas, crud
from fastapi import Depends

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
```

## database.py

```python:app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

## schemas.py

```python:app/schemas.py
from pydantic import BaseModel

class ItemBase(BaseModel):
    title: str
    description: str = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True
```

## models.py

```python:app/models.py
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
```

## crud.py

```python:app/crud.py
from sqlalchemy.orm import Session
from app import models, schemas

def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(title=item.title, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def update_item(db: Session, item_id: int, item: schemas.ItemUpdate):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    db_item.title = item.title
    db_item.description = item.description
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    db.delete(db_item)
    db.commit()
    return db_item
```

# 4. Deployment

## requirements.txt

```docker:requirements.txt
fastapi>=0.68.0,<0.69.0
pydantic>=1.8.0,<2.0.0
uvicorn>=0.15.0,<0.16.0
sqlalchemy>=1.3,<2.0
```

## Dockerfile

```docker:Dockerfile
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

# Install the package dependencies in the requirements file.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# Set the command to run the uvicorn server.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Build image

```bash
docker build -t fastapi .
```

## Run container

```bash
docker run -p 8000:8000 --restart unless-stopped --name fastapi -d fastapi
```

# Refference
- https://fastapi.tiangolo.com/
- https://hub.docker.com/r/tiangolo/uvicorn-gunicorn-fastapi
- https://www.datahungry.dev/blog/getting-started-with-fastapi
