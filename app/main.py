import os
import io
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlmodel import Session, select, func, or_
import pandas as pd
from app.database import create_db_and_tables, get_session, engine
from app.models import Dataset, Record

app = FastAPI(title="Data Import & Query MVP")

# Create tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Root endpoint serves the static HTML
@app.get("/")
async def root():
    return FileResponse("app/static/index.html")


@app.post("/api/upload_csv")
async def upload_csv(
    name: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Upload and parse a CSV file, create Dataset and Records
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV using pandas
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Create dataset
        columns = df.columns.tolist()
        dataset = Dataset(
            name=name,
            columns=columns,
            row_count=len(df)
        )
        session.add(dataset)
        session.commit()
        session.refresh(dataset)
        
        # Create records
        for _, row in df.iterrows():
            record = Record(
                dataset_id=dataset.id,
                data=row.to_dict()
            )
            session.add(record)
        
        session.commit()
        
        return {
            "dataset_id": dataset.id,
            "row_count": dataset.row_count,
            "columns": columns
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")


@app.get("/api/datasets")
async def list_datasets(session: Session = Depends(get_session)):
    """
    List all datasets with row counts and columns
    """
    datasets = session.exec(select(Dataset)).all()
    return [
        {
            "id": ds.id,
            "name": ds.name,
            "columns": ds.columns,
            "row_count": ds.row_count,
            "created_at": ds.created_at.isoformat()
        }
        for ds in datasets
    ]


@app.get("/api/search")
async def search_records(
    dataset_id: int = Query(...),
    q: str = Query(""),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
):
    """
    Search dataset rows by LIKE/ILIKE on JSON text representation
    """
    # Get dataset
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Build query
    query = select(Record).where(Record.dataset_id == dataset_id)
    
    # Apply search filter if query string provided
    if q:
        # For SQLite, we'll filter in Python as JSON search is limited
        # For PostgreSQL, you could use JSON operators
        all_records = session.exec(query).all()
        filtered_records = []
        for record in all_records:
            # Convert record data to string and check if query is present (case-insensitive)
            data_str = str(record.data).lower()
            if q.lower() in data_str:
                filtered_records.append(record)
        
        # Apply pagination
        total = len(filtered_records)
        records = filtered_records[offset:offset + limit]
    else:
        # Get total count
        count_query = select(func.count()).select_from(Record).where(Record.dataset_id == dataset_id)
        total = session.exec(count_query).one()
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        records = session.exec(query).all()
    
    return {
        "dataset_id": dataset_id,
        "dataset_name": dataset.name,
        "total": total,
        "limit": limit,
        "offset": offset,
        "records": [
            {
                "id": r.id,
                "data": r.data
            }
            for r in records
        ]
    }


@app.delete("/api/datasets/{dataset_id}")
async def delete_dataset(
    dataset_id: int,
    session: Session = Depends(get_session)
):
    """
    Delete a dataset and all its records
    """
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Delete all records first
    records = session.exec(select(Record).where(Record.dataset_id == dataset_id)).all()
    for record in records:
        session.delete(record)
    
    # Delete dataset
    session.delete(dataset)
    session.commit()
    
    return {"message": f"Dataset {dataset_id} deleted successfully"}
