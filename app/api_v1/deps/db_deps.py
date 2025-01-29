from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Request,Depends, HTTPException
from app.settings.config import settings
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.api_v1.deps.db import get_db


Base = declarative_base()

from app.api_v1.deps.user_deps import get_current_user

def get_transaction_session(request: Request, db_session: Session = Depends(get_db),current_user = Depends(get_current_user)):
    try:
        db_session.begin_nested()
        yield db_session
        db_session.commit()
    except SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        db_session.close()
