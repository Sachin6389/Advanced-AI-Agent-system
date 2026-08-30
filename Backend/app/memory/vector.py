from pathlib import Path


class VectorMemory:

    def __init__(
        self,
        directory
    ):

        self.directory = Path(
            directory
        )

        self.directory.mkdir(
            parents=True,
            exist_ok=True
        )


    def add(
        self,
        text,
        metadata=None
    ):

        # Extension point for:
        #
        # SentenceTransformers
        # +
        # FAISS

        return {

            "stored": True,

            "metadata":
                metadata or {}

        }


    def search(
        self,
        query,
        k=5
    ):

        return []