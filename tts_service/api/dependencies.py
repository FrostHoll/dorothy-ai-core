from fastapi import Depends
from typing_extensions import Annotated
from starlette.requests import Request

from tts_service.application.container import Container

def get_container(request: Request) -> Container:
    return request.app.state.container

ContainerDep = Annotated[Container, Depends(get_container)]