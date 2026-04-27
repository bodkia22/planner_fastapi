from datetime import date

from anthropic import Anthropic
from fastapi import APIRouter, Depends

from schemas.assistant import AssistantRequest, AssistantResponse
import database
from utils.jwt import get_current_user
from anthropic.types import TextBlock, ToolUseBlock, ToolUseBlock
from tools.definitions import TOOLS
from tools.executor import execute_tool

router = APIRouter()
client = Anthropic()  # ← один раз, на рівні модуля

MAX_ITERATIONS = 15

SYSTEM_PROMPT = (
    "Ти асистент для todo застосунку. Відповідай коротко і по суті, допомагай користувачу з його завданнями. "
    "Не відповідай на питання що не стосуються задач. Якщо користувач запитує про щось поза завданнями, ввічливо відмовся відповідати."
)


@router.post("/assistant")
def assistant(
    request: AssistantRequest,
    current_user=Depends(get_current_user),
    db=Depends(database.get_db),
):
    today = date.today().isoformat()
    system_prompt = f"{SYSTEM_PROMPT}\n\nСьогодні: {today}"

    messages: list[dict] = [{"role": "user", "content": request.message}]

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
    return AssistantResponse(message=text)
