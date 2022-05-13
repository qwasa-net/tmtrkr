import importlib.resources
import mimetypes
import os

from fastapi import HTTPException
from fastapi import status as status_code
from fastapi.responses import Response
from starlette.types import Receive, Scope, Send


class PackageStaticFiles:
    """ """

    def __init__(self, directory: str, package=None, html=True):
        """."""
        self.directory = directory
        self.html = html
        self.package = package or __name__
        self.resources = importlib.resources.files(self.package)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """The ASGI entry point."""
        try:
            path = os.path.normpath(scope["path"])
            if path.endswith("/") and self.html:
                path += "index.html"
            path_full = os.path.normpath(os.path.join(self.directory, path.lstrip("/")))
            ct_type, ct_encoding = mimetypes.guess_type(path_full)
            data = self.read(path_full)
        except Exception as x:
            print(x)
            raise HTTPException(status_code.HTTP_400_BAD_REQUEST)
        headers = {}
        if ct_type and "text" in ct_type:
            headers["content-type"] = f"{ct_type}; charset={ct_encoding or 'utf-8'}"
        elif ct_type:
            headers["content-type"] = ct_type
        if data:
            headers["content-length"] = str(len(data))
        response = Response(content=data, headers=headers)
        await response(scope, receive, send)

    def read(self, path):
        """."""
        file = self.resources.joinpath(path)
        with importlib.resources.as_file(file) as f:
            data = f.read_bytes()
        return data
