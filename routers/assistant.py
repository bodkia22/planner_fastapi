from datetime import date
from sqlalchemy import select

from anthropic import Anthropic
from fastapi import APIRouter, Depends, HTTPException

from models.conversation import Conversation
from models.message import Message
from schemas.assistant import (
    AssistantRequest,
    AssistantResponse,
    ChatRequest,
    ChatResponse,
)
import database
from utils.jwt import get_current_user
from anthropic.types import TextBlock, ToolUseBlock
from tools.definitions import TOOLS
from tools.executor import execute_tool

router = APIRouter()
client = Anthropic()  # ← один раз, на рівні модуля

MAX_ITERATIONS = 15

SYSTEM_PROMPT = (
    "Ти асистент для Weekly Planer застосунку. Відповідай коротко і по суті, допомагай користувачу з його завданнями. "
    "Не відповідай на питання що не стосуються задач. Якщо користувач запитує про щось поза завданнями, ввічливо відмовся відповідати."
    "Ти плануєш задачі по дефолту на цей тиждень, тиждень це період з понеділка по неділю. Але якщо користувач каже 'на наступний тиждень', то плануй на наступний тиждень. Якщо користувач каже 'на завтра', то плануй на завтра. "
    "Не добавляй задачі в минуле"
    "Якщо треба якійсь уточнення по задачі, запитай користувача, не вигадуй сам. Якщо користувач хоче створити задачу, але не вказує дату,"
    " то ця задача не має дати і попадає в To Do list"
)


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db=Depends(database.get_db),
):
    if request.conversation_id is None:
        conversation = Conversation(user_id=current_user.id, title=request.content[:50])
        db.add(conversation)
        db.flush()
    else:
        # якщо conversation_id є, перевіряємо, що така розмова існує і належить користувачу
        stmt = select(Conversation).where(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id,
        )

        conversation = db.execute(stmt).scalar_one_or_none()

        if conversation is None:
            raise HTTPException(status_code=404)

    user_message = Message(
        conversation_id=conversation.id, content=request.content, role="user"
    )
    db.add(user_message)
    db.flush()

    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    db_messages = db.execute(stmt).scalars().all()

    #
    today = date.today().isoformat()
    system_prompt = f"{SYSTEM_PROMPT}\n\nСьогодні: {today}"

    messages: list[dict] = [
        {"role": msg.role, "content": msg.content} for msg in db_messages
    ]

    # цикл: модель може хотіти кілька tool-ів підряд
    iterations = 0
    while True:
        iterations += 1
        if iterations > MAX_ITERATIONS:
            raise ValueError("Too many tool calls")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,  # type: ignore
        )

        # якщо модель закінчила — виходимо
        if response.stop_reason == "end_turn":
            break

        # якщо модель хоче tool — обробляємо
        if response.stop_reason == "tool_use":
            # 1. Додаємо відповідь моделі в історію
            messages.append(
                {
                    "role": "assistant",
                    "content": response.content,  # повний content (TextBlock + ToolUseBlock)
                }
            )

            # 2. Знаходимо ВСІ ToolUseBlock-и (модель може хотіти кілька одразу)
            tool_results = []
            for block in response.content:
                if isinstance(block, ToolUseBlock):
                    # викликаємо реальну функцію
                    result = execute_tool(
                        tool_name=block.name,
                        tool_input=block.input,  # type: ignore[arg-type]
                        db=db,
                        user_id=current_user.id,
                    )
                    # формуємо tool_result для моделі
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,  # звідки?
                            "content": result,
                        }
                    )

            # 3. Додаємо результати tool-ів як user message
            messages.append({"role": "user", "content": tool_results})

            # цикл продовжується — наступний виклик моделі вже з результатами
            continue

        # все інше — несподівано, кидаємо помилку
        raise ValueError(f"Unexpected stop_reason: {response.stop_reason}")

    # після виходу з циклу — дістаємо текст із останньої відповіді
    text = "".join(b.text for b in response.content if isinstance(b, TextBlock))

    assistant_message = Message(
        conversation_id=conversation.id, content=text, role="assistant"
    )
    db.add(assistant_message)
    db.commit()

    return ChatResponse(conversation_id=conversation.id, message=text)
    ...
