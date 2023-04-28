from __future__ import annotations

import dataclasses
import os
from typing import Any, List

import numpy as np
import orjson

from commands.tasks.memory.base import MemoryProviderSingleton
from commands.tasks.utils import create_embedding_with_ada
from configs import TaskConfig

from amiyabot import log

EMBED_DIM = 1536
SAVE_OPTIONS = orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_DATACLASS


def create_default_embeddings():
    return np.zeros((0, EMBED_DIM)).astype(np.float32)


@dataclasses.dataclass
class CacheContent:
    texts: List[str] = dataclasses.field(default_factory=list)
    embeddings: np.ndarray = dataclasses.field(
        default_factory=create_default_embeddings
    )


class LocalCache(MemoryProviderSingleton):
    """A class that stores the memory in a local file"""

    def __init__(self) -> None:
        """Initialize a class instance

        Returns:
            None
        """
        self.filename = f"{TaskConfig['memory']['index']}.json"
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "w+b") as f:
                    file_content = f.read()
                    if not file_content.strip():
                        file_content = b"{}"
                        f.write(file_content)

                    loaded = orjson.loads(file_content)
                    self.data = CacheContent(**loaded)
            except orjson.JSONDecodeError:
                log.error(f"文件 '{self.filename}' 不是json格式.")
                self.data = CacheContent()
        else:
            log.warning(
                f"文件 '{self.filename}' 不存在. 本地内存不会保存到文件中."
            )
            self.data = CacheContent()

    async def add(self, text: str):
        """
        Add text to our list of texts, add embedding as row to our
            embeddings-matrix

        Args:
            text: str

        Returns: None
        """
        if "Command Error:" in text:
            return ""
        self.data.texts.append(text)

        embedding = await create_embedding_with_ada(text)

        vector = np.array(embedding).astype(np.float32)
        vector = vector[np.newaxis, :]
        self.data.embeddings = np.concatenate(
            [
                self.data.embeddings,
                vector,
            ],
            axis=0,
        )

        with open(self.filename, "wb") as f:
            out = orjson.dumps(self.data, option=SAVE_OPTIONS)
            f.write(out)
        return text

    def clear(self) -> str:
        """
        Clears the redis server.

        Returns: A message indicating that the memory has been cleared.
        """
        self.data = CacheContent()
        return "Obliviated"

    async def get(self, data: str) -> list[Any] | None:
        """
        Gets the data from the memory that is most relevant to the given data.

        Args:
            data: The data to compare to.

        Returns: The most relevant data.
        """
        return await self.get_relevant(data, 1)

    async def get_relevant(self, text: str, k: int) -> list[Any]:
        """ "
        matrix-vector mult to find score-for-each-row-of-matrix
         get indices for top-k winning scores
         return texts for those indices
        Args:
            text: str
            k: int

        Returns: List[str]
        """
        embedding = await create_embedding_with_ada(text)

        scores = np.dot(self.data.embeddings, embedding)

        top_k_indices = np.argsort(scores)[-k:][::-1]

        return [self.data.texts[i] for i in top_k_indices]

    def get_stats(self) -> tuple[int, tuple[int, ...]]:
        """
        Returns: The stats of the local cache.
        """
        return len(self.data.texts), self.data.embeddings.shape
