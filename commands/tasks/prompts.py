import json
from typing import Any

from configs import bot_name


class Prompt:
    def __init__(self, prompt, description='默认提示词描述'):
        self._prompt = prompt
        self._description = description

    def __str__(self):
        return str(self._prompt)

    def __add__(self, other):
        if isinstance(other, str):
            return str(self) + other
        elif isinstance(other, Prompt):
            return str(self) + str(other)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return other + str(self)
        return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, str):
            self._prompt = str(self) + other
            return self
        elif isinstance(other, Prompt):
            self._prompt = str(self) + str(other)
            return self
        return NotImplemented

    @property
    def prompt(self):
        return self._prompt

    @property
    def description(self):
        return self._description

class PromptGenerator:
    # 需返回消息格式
    response_format = {
        "thoughts": {
            "text": "thought",
            "reasoning": "reasoning",
            "plan": "- short bulleted\n- list that conveys\n- long-term plan",
            "criticism": "constructive self-criticism",
            "speak": "thoughts summary to say to user",
        },
        "command": {
            "name": "command name",
            "args": {
                "arg name": "value"
            }
        },
    }

    # 允许Bot执行的指令
    commands = [
        ("Google Search", "google", {"input": "<search>"}),
        (
            "Browse Website",
            "browse_website",
            {"url": "<url>", "question": "<what_you_want_to_find_on_website>"},
        ),
        (
            "Start GPT Agent",
            "start_agent",
            {"name": "<name>", "task": "<short_task_desc>", "prompt": "<prompt>"},
        ),
        (
            "Message GPT Agent",
            "message_agent",
            {"key": "<key>", "message": "<message>"},
        ),
        ("List GPT Agents", "list_agents", {}),
        ("Delete GPT Agent", "delete_agent", {"key": "<key>"}),
        (
            "Clone Repository",
            "clone_repository",
            {"repository_url": "<url>", "clone_path": "<directory>"},
        ),
        ("Write to file", "write_to_file", {"file": "<file>", "text": "<text>"}),
        ("Read file", "read_file", {"file": "<file>"}),
        ("Append to file", "append_to_file", {"file": "<file>", "text": "<text>"}),
        ("Delete file", "delete_file", {"file": "<file>"}),
        ("Search Files", "search_files", {"directory": "<directory>"}),
        ("Analyze Code", "analyze_code", {"code": "<full_code_string>"}),
        (
            "Get Improved Code",
            "improve_code",
            {"suggestions": "<list_of_suggestions>", "code": "<full_code_string>"},
        ),
        (
            "Write Tests",
            "write_tests",
            {"code": "<full_code_string>", "focus": "<list_of_focus_areas>"},
        ),
        ("Execute Python File", "execute_python_file", {"file": "<file>"}),
        ("Generate Image", "generate_image", {"prompt": "<prompt>"}),
        # ("Send Tweet", "send_tweet", {"text": "<text>"}),
        # ("Convert Audio to text", "read_audio_from_file", {"file": "<file>"}),
        # (
        #     "Execute Shell Command, non-interactive commands only",
        #     "execute_shell",
        #     {"command_line": "<command_line>"},
        # ),
        # (
        #     "Execute Shell Command Popen, non-interactive commands only",
        #     "execute_shell_popen",
        #     {"command_line": "<command_line>"},
        # ),
        # (
        #     "Downloads a file from the internet, and stores it locally",
        #     "download_file",
        #     {"url": "<file_url>", "file": "<saved_filename>"},
        # ),
        ("Do Nothing", "do_nothing", {}),
        ("Task Complete (Shutdown)", "task_complete", {"reason": "<reason>"}),
    ]

    # 条件约束
    constraints = [
        "短期内存限制为4000字左右。你的短期记忆是短暂的，所以立即将重要的信息保存到文件中。",
        "如果你不确定你以前是怎么做的，或者想回忆过去的事情，想想类似的事情会帮助你记忆。",
        "无用户协助。",
        "请在回复中文时本地化自然语言字符串。",
        '只使用双引号中列出的命令，例如: "command name"',
        "将子流程用于几分钟内不会终止的命令",
    ]

    # 资源
    resources = [
        "上网搜索和收集信息。",
        "长期记忆管理。",
        "支持GPT-3.5的代理，用于委派简单的任务。",
        "文件输出。",
    ]

    # 性能优化
    performance_evaluations = [
        "不断地回顾和分析你的行动，以确保你发挥出了最大的能力。",
        "不断地进行建设性的自我批评。",
        "反思过去的决策和策略，以改进你的方法，但专注于目标。",
        "每个命令都有成本，所以要聪明和高效。以最少的步骤完成任务为目标。",
    ]

    def __init__(self, role: str, goals: list):
        # 身份信息
        self.role = role
        self.goals = goals

        # 约束、系统指令及资源等
        self._constraints = []
        self._commands = []
        self._resources = []
        self._performance_evaluations = []

        # 执行初始化操作，添加约束、指令及资源
        # 约束条件
        for constraint in PromptGenerator.constraints:
            self.add_constraint(Prompt(constraint, "约束条件提示词"))
        # 指令
        for command_label, command_name, args in PromptGenerator.commands:
            self.add_command(command_label, command_name, args)
        # 资源
        for resource in PromptGenerator.resources:
            self.add_resource(Prompt(resource, "资源提示词"))
        # 性能优化
        for performance_evaluation in PromptGenerator.performance_evaluations:
            self.add_performance_evaluation(Prompt(performance_evaluation, "性能评估提示词"))

    @property
    def init_prompt_string(self):
        """
        初始化提示词getter
        :return:
        """
        target = "目标:"
        for i, goal in enumerate(self.goals):
            target += f"{i+1}. {goal}\n"

        full_prompt = Prompt(
            prompt=f"你是 {bot_name}, {self.role}\n"
                   f"您必须独立做出决策，不寻求用户的帮助。发挥您作为 LLM 的优势，追求简单的策略，避免法律问题的复杂性。\n"
                   f"\n"
                   f"{target}",
            description="启动时的完整提示词，包含目标和自我介绍以及系统的介绍"
        )
        full_prompt += self.full_prompt_string

        return full_prompt

    @property
    def full_prompt_string(self):
        """
        根据约束、命令、资源和性能评估生成提示字符串
        :return:
        """
        formatted_response_format = json.dumps(PromptGenerator.response_format, indent=4)
        return Prompt(
            f"约束:\n{self._generate_numbered_list(self._constraints)}\n\n"
            "指令:\n"
            f"{self._generate_numbered_list(self._commands, item_type='command')}\n\n"
            f"资源:\n{self._generate_numbered_list(self._resources)}\n\n"
            "绩效评估:\n"
            f"{self._generate_numbered_list(self._performance_evaluations)}\n\n"
            "你应该只以JSON格式响应，如下所述 \n"
            "响应格式: \n"
            f"{formatted_response_format} \n"
            "确保响应可以被Python json.loads解析"
        )

    @staticmethod
    def _generate_command_string(command: dict[str, Any]):
        """
        根据传入的命令字典生成格式化的命令字符串
        :param command:
        :return:
        """
        args_string = ", ".join(
            f'"{key}": "{value}"' for key, value in command["args"].items()
        )
        return f'{command["label"]}: "{command["name"]}", args: {args_string}'

    def _generate_numbered_list(self, items: list[Prompt], item_type="list"):
        """
        根据给定的项目列表和项目类型（item_type）生成一个编号列表
        :param items:
        :param item_type:
        :return:
        """
        if item_type == "command":
            return "\n".join(
                f"{i+1}. {self._generate_command_string(item.prompt)}"
                for i, item in enumerate(items)
            )
        else:
            return "\n".join(f"{i+1}. {item.prompt}" for i, item in enumerate(items))

    def add_constraint(self, constraints: Prompt):
        """
        添加约束
        :param constraints: 约束
        :return:
        """
        self._constraints.append(constraints)

    def add_command(self, command_label, command_name, args=None):
        """
        添加指令
        :param command_label: 指令标签
        :param command_name: 指令名称
        :param args: 参数
        :return:
        """
        if not args:
            args = {}

        command_args = {arg_key: arg_value for arg_key, arg_value in args.items()}
        command = {
            "label": command_label,
            "name": command_name,
            "args": command_args,
        }

        self._commands.append(Prompt(command, "指令提示词"))

    def add_resource(self, resource: Prompt):
        """
        添加资源
        :param resource:
        :return:
        """
        self._resources.append(resource)

    def add_performance_evaluation(self, performance_optimization: Prompt):
        """
        添加性能评估提示词
        :param performance_optimization:
        :return:
        """
        self._performance_evaluations.append(performance_optimization)
