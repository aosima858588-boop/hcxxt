from fastapi import FastAPI, UploadFile, File, HTTPException
from .database import init_db, get_session
from .models import User, Purchase
from .schemas import UserOut
from typing import List
from sqlmodel import select
from sqlalchemy import func
import csv, io, json
import re

app = FastAPI(title="退款查询系统 API")
init_db()

def parse_date_string(date_str):
    """Parse various date formats to datetime object"""
    if not date_str:
        return None
    try:
        from datetime import datetime
        # Try ISO format first
        if '/' in date_str or '-' in date_str:
            # Handle formats like "2026/2/2 13:59" or "2026-02-02"
            return datetime.fromisoformat(date_str.replace('/', '-').split()[0])
        
        # Handle Chinese format like "1月14日"
        match = re.match(r'(\d{1,2})月(\d{1,2})日', date_str)
        if match:
            month = int(match.group(1))
            day = int(match.group(2))
            # Assume year 2026 for dates without year
            return datetime(2026, month, day)
    except:
        pass
    return None

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
    total = session.exec(select(func.sum(Purchase.amount))).one() or 0.0
    due_not_refunded = 0.0
    not_due_total = 0.0
    from datetime import datetime
    today = datetime.utcnow().date()
    purchases = session.exec(select(Purchase)).all()
    for p in purchases:
        if p.end_date:
            end_date = parse_date_string(p.end_date)
            if end_date and end_date.date() <= today:
                due_not_refunded += p.amount
            else:
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
    user = session.exec(select(User).where(User.phone == phone)).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    purchases = session.exec(select(Purchase).where(Purchase.user_id == user.id)).all()
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
            end_date = parse_date_string(p.end_date)
            if end_date and end_date.date() <= today:
                due += p.amount
            else:
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

