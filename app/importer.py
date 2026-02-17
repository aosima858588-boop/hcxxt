import json
from .database import get_session
from .models import User, Purchase
from pathlib import Path
from sqlmodel import select

# Note: We'll provide a simple loader that can load data.js similarly to the Node script
# but in practice we'll accept CSV/JSON upload via /api/import. For now include a helper to load data.js

def import_from_dicts(dicts):
    session = get_session()
    imported = 0
    users_to_create = {}
    
    for rec in dicts:
        phone = rec.get('用户') or rec.get('会员ID')
        if not phone:
            continue
        address = rec.get('地址') or rec.get('address')
        product = rec.get('产品名称') or rec.get('产品')
        amount = float(rec.get('购买金额') or rec.get('认购额度') or 0)
        start = rec.get('开始') or rec.get('买入时间')
        end = rec.get('结束时间') or rec.get('结束')
        daily = rec.get('每日应返') or rec.get('每期返')
        status = rec.get('状态')
        extra = rec.get('额外')

        # Check if user exists in database or in pending batch
        user = session.exec(select(User).where(User.phone == phone)).first()
        if not user:
            if phone not in users_to_create:
                user = User(phone=phone, address=address)
                session.add(user)
                session.flush()  # Get the user.id without committing
                users_to_create[phone] = user
            else:
                user = users_to_create[phone]
        
        p = Purchase(user_id=user.id, product_name=product, amount=amount, start_date=start, end_date=end, daily_return=float(daily) if daily else None, status=status, extra=float(extra) if extra else None)
        session.add(p)
        imported += 1
    
    session.commit()
    session.close()
    return imported
