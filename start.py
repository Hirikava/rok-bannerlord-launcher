import asyncio

from src.presentation.launcher_app import RokBannerlordLauncherApp

ADB_TOOLS_PACKAGE_NAME = "adb-platform-tools"
ROK_BANNERLORD_CLIENT = "rok-bannerlord-client"
ROK_BANNERLORD_AGENT = "rok-bannerlord-agent"

PACKAGES_TO_UPDATE = [
    ROK_BANNERLORD_CLIENT,
    ADB_TOOLS_PACKAGE_NAME,
    ROK_BANNERLORD_AGENT
]


async def main():
    launcher_app = RokBannerlordLauncherApp(
        packages_names=PACKAGES_TO_UPDATE)

    await launcher_app.run()


if __name__ == "__main__":
    asyncio.run(main())
