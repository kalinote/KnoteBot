import time

from ai.gpt.chatgpt import ChatGPT
from ai.gpt.utils import count_message_tokens
from commands.tasks.prompts import PromptGenerator
from commands.tasks.memory import get_memory
from configs import bot_name, TaskConfig
from amiyabot import log

from exceptions.throw_message import ThrowMessage
from utils.task_commands.browse_website import browse_website
from utils.task_commands.google_search import google_search_by_api


class Agent:

    def __init__(self, role, goals, agent_name=bot_name, system_order=None, is_sub_agent=False, parent_agent=None, using_model='gpt-3.5-turbo'):
        self.full_message_history = []
        self.action_count = 0
        self.role = role
        self.goal = goals
        self.agent_name = agent_name
        self.PromptGenerator = PromptGenerator(role=self.role, goals=self.goal)
        self.system_order = system_order if system_order else self.PromptGenerator.init_prompt_string
        self.loop_count = 0
        self.using_model = using_model

        self.memory = get_memory(memory_type=TaskConfig.get('memory', {}).get('memory_type', 'local'))

        # 子代理人(Sub Agent)
        self.is_sub_agent = is_sub_agent
        self.parent_agent = parent_agent

    async def run_step(self, user_input=None):
        """
        启动Agent
        :return:
        """
        # '确定要使用的下一个命令，并使用上面指定的JSON格式响应:'
        token_limit = TaskConfig.get('token_limit', 4000)
        send_token_limit = token_limit - 1000

        relevant_memory = (
            ""
            if len(self.full_message_history) == 0
            else await self.memory.get_relevant(str(self.full_message_history[-9:]), 10)
        )

        log.debug(f"Memory Stats: {self.memory.get_stats()}")

        gpt = ChatGPT(temperature=0, system_order=self.system_order)
        gpt.add_conversation(role='system', content=f"The current time and date is {time.strftime('%c')}")
        gpt.add_conversation(role='system', content=f"This reminds you of these events from your past:\n{relevant_memory}\n\n",)

        current_context = gpt.get_raw_conversations_group()
        current_tokens_used = count_message_tokens(current_context, self.using_model)

        while current_tokens_used > 2400:
            # remove memories until we are under 2400 tokens
            gpt.pop_conversation()

            relevant_memory = relevant_memory[:-1]
            gpt.add_conversation(role='system',
                                 content=f"This reminds you of these events from your past:\n{relevant_memory}\n\n", )

            current_context = gpt.get_raw_conversations_group()
            current_tokens_used = count_message_tokens(current_context, self.using_model)

        next_message_to_add_index = len(self.full_message_history) - 1
        insertion_index = gpt.get_conversations_count()

        while next_message_to_add_index >= 0:
            # print (f"CURRENT TOKENS USED: {current_tokens_used}")
            message_to_add = self.full_message_history[next_message_to_add_index]

            # log.debug(
            #     f'message_to_add: {message_to_add}, type: {type(message_to_add)}'
            # )

            tokens_to_add = count_message_tokens(
                [message_to_add], self.using_model
            )
            if current_tokens_used + tokens_to_add > send_token_limit:
                break

            # Add the most recent message to the start of the current context,
            #  after the two system prompts.
            gpt.add_conversation_by_index(
                role=self.full_message_history[next_message_to_add_index]['role'],
                content=self.full_message_history[next_message_to_add_index]['content'],
                index=insertion_index,
            )

            # Count the currently used tokens
            current_tokens_used += tokens_to_add

            # Move to the next most recent message in the full message history
            next_message_to_add_index -= 1

        if user_input:
            gpt.add_conversation(role='user', content=user_input)

        # 计算剩余token
        current_context = gpt.get_raw_conversations_group()
        current_tokens_used = count_message_tokens(current_context, self.using_model)
        tokens_remaining = token_limit - current_tokens_used

        log.debug(f'当前token: {current_tokens_used}')
        log.debug(f'剩余token: {tokens_remaining}')

        # log.debug(f"\n{json.dumps(gpt.get_conversations_group(), indent=4)}")

        return await gpt.call()

    @staticmethod
    async def do_command(command=None, **args):
        if not command:
            return

        # 识别指令
        try:
            if command == 'google':
                google_api_key = TaskConfig.get('search', {}).get('google_api_key', None)
                keyword = args.get('input')
                if not keyword or not google_api_key:
                    return []

                if google_api_key:
                    try:
                        result_urls = await google_search_by_api(keyword)
                    except ThrowMessage as msg:
                        log.error(msg)
                        raise ThrowMessage(msg)
                    except Exception as e:
                        log.error(f'执行google命令发生错误: {e}')
                        raise ThrowMessage(f'执行google命令发生错误: {e}')

                    return result_urls

            elif command == "memory_add":
                pass
            elif command == "start_agent":
                pass
            elif command == "message_agent":
                pass
            elif command == "list_agents":
                pass
            elif command == "delete_agent":
                pass
            elif command == "get_text_summary":
                pass
            elif command == "get_hyperlinks":
                pass
            elif command == "clone_repository":
                pass
            elif command == "read_file":
                pass
            elif command == "write_to_file":
                pass
            elif command == "append_to_file":
                pass
            elif command == "delete_file":
                pass
            elif command == "search_files":
                pass
            elif command == "download_file":
                pass
            elif command == "browse_website":
                return await browse_website(args.get("url", ""), args.get("question", ""))
            elif command == "analyze_code":
                pass
            elif command == "improve_code":
                pass
            elif command == "write_tests":
                pass
            elif command == "execute_python_file":  # Add this command
                pass
            elif command == "execute_shell":
                pass
            elif command == "execute_shell_popen":
                pass
            elif command == "read_audio_from_file":
                pass
            elif command == "generate_image":
                pass
            elif command == "send_tweet":
                pass
            elif command == "do_nothing":
                return
            elif command == "task_complete":
                pass
            else:
                raise ThrowMessage(f"{bot_name} 尝试执行未知指令 '{command}'. ")
        except Exception as e:
            raise ThrowMessage('执行指令时发生错误: {e}')
