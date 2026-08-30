class ShortTermMemory:

    def add(
        self,
        state,
        role,
        content
    ):

        messages = state.setdefault(
            "messages",
            []
        )

        messages.append({

            "role": role,

            "content": content

        })

        return state


    def get(
        self,
        state
    ):

        return state.get(
            "messages",
            []
        )