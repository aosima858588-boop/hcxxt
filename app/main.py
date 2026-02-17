from fastapi import FastAPI, UploadFile, File, HTTPException
from .database import init_db, get_session
from .models import User, Purchase
from .schemas import UserOut
from typing import List
from sqlalchemy import func
import csv, io, json

app = FastAPI(title="退款查询系统 API")
init_db()

@app.post('/api/import-json')
async def import_json(payload: dict):
    # payload can contain arrays: injData/usdt45Data/usdtFinanceData
    from .importer import import_from_dicts
    total = 0
    for k in ['injData','usdt45Data','usdtFinanceData']:
        arr = payload.get(k)
        if arr:
            total += import_from_dicts(arr)
    return {'imported': total}

@app.get('/api/overview')
def overview():
    session = get_session()
    total = session.query(func.sum(Purchase.amount)).scalar() or 0.0
    due_not_refunded = 0.0
    not_due_total = 0.0
    from datetime import datetime
    today = datetime.utcnow().date()
    purchases = session.query(Purchase).all()
    for p in purchases:
        if p.end_date:
            try:
                end = datetime.fromisoformat(p.end_date)
                if end.date() <= today:
                    due_not_refunded += p.amount
                else:
                    not_due_total += p.amount
            except:
                not_due_total += p.amount
        else:
            not_due_total += p.amount
    session.close()
    return {
        'total_subscribed': round(total,2),
        'total_refunded': 0.0,
        'due_not_refunded': round(due_not_refunded,2),
        'not_due_total': round(not_due_total,2)
    }

@app.get('/api/user')
def get_user(phone: str):
    session = get_session()
    user = session.query(User).filter_by(phone=phone).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    purchases = session.query(Purchase).filter_by(user_id=user.id).all()
    product_count = len(purchases)
    total_sub = sum([p.amount for p in purchases])
    from datetime import datetime
    today = datetime.utcnow().date()
    due = 0.0
    not_due = 0.0
    products = []
    for p in purchases:
        products.append({
            'name': p.product_name,
            'amount': p.amount,
            'start': p.start_date,
            'end': p.end_date,
            'daily_return': p.daily_return,
            'status': p.status,
            'extra': p.extra
        })
        if p.end_date:
            try:
                end = datetime.fromisoformat(p.end_date).date()
                if end <= today:
                    due += p.amount
                else:
                    not_due += p.amount
            except:
                not_due += p.amount
        else:
            not_due += p.amount
    session.close()
    return {
        'phone': user.phone,
        'address': user.address,
        'product_count': product_count,
        'total_subscribed': round(total_sub,2),
        'total_refunded': 0.0,
        'due_not_refunded': round(due,2),
        'not_due_total': round(not_due,2),
        'products': products
    }
