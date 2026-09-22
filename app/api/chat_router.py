from fastapi import APIRouter, Body, Depends, HTTPException, Query
from app.auth.security import get_current_user
from app.agents.banking_agent import create_banking_agent
from app.core.db.deps import get_db
from app.core.text_safety import remove_user_name
from app.schemas.user_schema import ChatRequest
from app.services.chat_cache import get_cached_response, set_cached_response
from sqlalchemy.ext.asyncio import AsyncSession

import logging

logger = logging.getLogger(__name__)
router = APIRouter()

chat_store = {}

@router.post("/chat")
async def chat(
        request: ChatRequest | None = Body(default=None),
        message: str | None = Query(default=None),
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user_message = request.message if request else message
    if not user_message:
        raise HTTPException(status_code=422, detail="Message is required")

    if user.id not in chat_store:
        chat_store[user.id] = []

    cached_response = await get_cached_response(user.id, user_message, db)
    if cached_response:
        chat_store[user.id].append({"role": "user", "content": user_message})
        chat_store[user.id].append({"role": "assistant", "content": cached_response})
        return cached_response

    agent = create_banking_agent(
         user_id=user.id,
         firstname=user.firstname,
         surname=user.surname,
         db=db
     )
    history = chat_store[user.id]
    history = history[-4:]
    response = await agent.ainvoke(
        {
            "messages": history + [
                {"role": "user", "content": user_message}
            ]
        }
    )

    final_response = remove_user_name(response["messages"][-1].content, user.firstname, user.surname)
    chat_store[user.id].append({"role": "user", "content": user_message})
    chat_store[user.id].append({"role": "assistant", "content": final_response})
    await set_cached_response(user.id, user_message, final_response, db)

    return final_response
