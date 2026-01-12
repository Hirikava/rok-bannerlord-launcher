import abc


class LauncherStateBase:
    on_init_flag: bool = False

    async def run(self):
        if not self.on_init_flag:
            await self.on_init()
            self.on_init_flag = True

        await self.run_internal()

    def reset(self):
        self.on_init_flag = False

    @abc.abstractmethod
    async def on_init(self):
        ...

    @abc.abstractmethod
    def run_internal(self):
        ...
