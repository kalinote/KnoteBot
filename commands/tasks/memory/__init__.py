from commands.tasks.memory.local import LocalCache


def get_memory(memory_type='local', init=False):
    memory = None

    # 默认local
    if not memory:
        memory = LocalCache()
        if init:
            memory.clear()

    return memory