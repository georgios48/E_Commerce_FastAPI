from fastapi import FastAPI, HTTPException, Request, status
from tortoise.contrib.fastapi import register_tortoise
from models import *
from authentication import *

# Signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from emails import *

# Response Classes
from fastapi.responses import HTMLResponse

# Templates
from fastapi.templating import Jinja2Templates

app = FastAPI()

@post_save(User)
async def create_business(sender: "Type[User]", instance: User, created: bool, isong_db: "Optional[BaseDBAsyncClient]", update_fields: List[str]):
    if created:
        business_obj = await Business.create(business_name = instance.username, owner = instance)
        await business_pydantic.from_tortoise_orm(business_obj)
        
        # Send the email
        await send_email([instance.email], instance)

@app.post("/registration")
async def user_registration(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)

    user_info["password"] = authenticate_password(user_info["password"])
    user_info["email"] = check_is_email_valid(user_info["email"])

    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    
    return {"Status": "OK",
            "data": f"Hello {new_user.username}, WELCOME! Please, check your email inbox to confirm your account."}


templates = Jinja2Templates(directory="templates")

@app.get("/verification", response_class=HTMLResponse)
async def email_verification(request: Request, token: str):
    # Verify token: deocdes the token and checks if its valid.
    user = await verify_token(token)
    
    # If there is not such a user and its not verified, add this user and verify it
    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse("verification.html",
                                            {"request": request,
                                            "username": User.username}
                                            )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"}
        )


@app.get("/")
def index():
    return {"Message": "Hello World"}

register_tortoise = register_tortoise(
    app,
    db_url = "sqlite://database.sqlite3",
    modules = {"models" : ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)