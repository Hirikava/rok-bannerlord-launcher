import asyncio

from src.presentation.launcher_app import RokBannerlordLauncherApp

ROK_BANNERLORD_PACKAGE_NAME = "rok-bannerlord"
TESSERACT_OCR_PACKAGE_NAME = "tesseract-ocr"
ADB_TOOLS_PACKAGE_NAME = "adb-platform-tools"

PACKAGES_TO_UPDATE = [
    "aboba"
    # ROK_BANNERLORD_PACKAGE_NAME,
    # TESSERACT_OCR_PACKAGE_NAME,
    # ADB_TOOLS_PACKAGE_NAME
]


async def main():
    host = "localhost"
    port = 7272

    launcher_app = RokBannerlordLauncherApp(
        host=host,
        port=port,
        packages_names=PACKAGES_TO_UPDATE)

    await launcher_app.run()


if __name__ == "__main__":
    asyncio.run(main())
