from datetime import datetime

from app.application.prompt_builder import PromptBuilder
from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities.conversation import Conversation
from app.domain.entities.message import Message
from app.domain.interfaces.llm_interface import LLMInterface


class GenerateResponseUseCase:
    uow: AbstractUnitOfWork

    def __init__(self, llm: LLMInterface, prompt_builder: PromptBuilder):
        self.llm = llm
        self.prompt_builder = prompt_builder

    async def execute(self, user_input: str, platform: str, external_id: str) -> tuple[str, str, datetime]:
        async with self.uow as uow:
            new_chat = False
            conversation_id = await uow.conversations.get_id_by_metadata(platform, external_id)
            if not conversation_id:
                conversation_id = await uow.conversations.get_new_id()
                new_chat = True
            user_input_tokens = self.llm.count_tokens(user_input)
            system_prompt_tokens = self.llm.count_tokens(self.prompt_builder.persona_manager.get_persona().system_prompt)
            token_budget = self.llm.get_context_window() - self.llm.get_reserved_tokens() - user_input_tokens - system_prompt_tokens
            user_message = Message(role="user", content=user_input, token_count=user_input_tokens)
            messages = await self.prompt_builder.build(user_message, uow.messages, conversation_id, token_budget)
            msg, response, _ = await self.llm.create_chat_completion(messages)

            await uow.messages.add_many_memory([
                user_message,
                msg
            ], conversation_id)
            created_at = datetime.now()
            if new_chat:
                conversation = Conversation(
                    id=conversation_id,
                    platform=platform,
                    external_id=external_id,
                    title=f"Chat {conversation_id}",
                    last_user_message=user_input,
                    last_updated_at=created_at
                )
                await uow.conversations.add(conversation)
            else:
                await uow.conversations.update_last_info(
                    conversation_id,
                    user_input,
                    created_at
                )

            return response, conversation_id, created_at

class PreviewContextWindowUseCase:
    uow: AbstractUnitOfWork

    def __init__(self, llm: LLMInterface, prompt_builder: PromptBuilder):
        self.llm = llm
        self.prompt_builder = prompt_builder

    async def execute(self, conversation_id: str) -> list[Message]:
        async with self.uow as uow:
            system_prompt_tokens = self.llm.count_tokens(
                self.prompt_builder.persona_manager.get_persona().system_prompt)
            token_budget = self.llm.get_context_window() - self.llm.get_reserved_tokens() - system_prompt_tokens
            user_message = Message(role="user", content="")
            messages = await self.prompt_builder.build(user_message, uow.messages, conversation_id, token_budget)

            return messages