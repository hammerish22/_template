from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from sqlalchemy.orm import Session

from api._database._session import get_db
from api.model._user import User_Type


router = APIRouter(prefix="/user")


class UserTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    external_uid: Optional[str] = None


class UserCreate(BaseModel):
    user_type_uid: str
    first_name: str
    last_name: str
    email: str
    external_uid: Optional[str] = None


@router.post("/user_type", status_code=201, tags=["config", "user"])
def post_user_type(body: UserTypeCreate, db: Session = Depends(get_db)):
    existing = db.query(User_Type).filter(User_Type.name == body.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="User type with this name already exists")
    
    user_type = User_Type(
        name=body.name,
        description=body.description,
        external_uid=body.external_uid,
    )

    print(user_type)

    # db.add(user_type)
    # db.commit()
    # db.refresh(user_type)

    return JSONResponse(status_code=201, content={
        "uid":          user_type.uid,
        "name":         user_type.name,
        "description":  user_type.description,
        "external_uid": user_type.external_uid,
        "state":        user_type.state,
    })


@router.get("/user_types", tags=["config", "user"])
def get_user_types(db: Session = Depends(get_db)):
    user_types = db.query(User_Type).filter(User_Type.is_deleted == False).all()
    
    return JSONResponse(
        content=[
            {
                "uid":          ut.uid,
                "name":         ut.name,
                "description":  ut.description,
                "external_uid": ut.external_uid,
                "state":        ut.state,
            }
            for ut in user_types
        ]
    )
