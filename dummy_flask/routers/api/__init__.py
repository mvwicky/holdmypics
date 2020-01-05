import asyncio

import attr
from fastapi import APIRouter, Depends, Path, Query
from PIL import Image
from starlette.responses import StreamingResponse

from ..._types import Dimension
from ...constants import Fonts
from .image_args import ImagePathArgs, ImageQueryArgs
from .utils import ImageFormat, create_image_sync, im_to_bytes

router = APIRouter()

width_path = Path(..., gt=0, description="Width of the image in pixels.")
height_path = Path(..., gt=0, description="Height of the image in pixels.")
fmt_path = Path(..., title="Format", description="Image format")
bg_path = Path("cef")
fg_path = Path("555")


def image_path(
    width: int = width_path,
    height: int = height_path,
    bg_color: str = bg_path,
    fg_color: str = fg_path,
    fmt: ImageFormat = fmt_path,
):
    return ImagePathArgs((width, height), bg_color, fg_color, fmt.value)
    return (width, height), bg_color, fg_color, fmt.value


def image_query(
    text: str = Query(None, description="The text that will be put on the image."),
    dpi: int = Query(72, description="Dots per inch", gt=0),
    font: Fonts = Query("overpass", description="The font."),
    alpha: float = Query(1.0, description="Transparency.", ge=0, lt=1),
):
    return ImageQueryArgs(text=text, font_name=font.value, dpi=dpi, alpha=alpha)


async def create_image(
    size: Dimension, bg_color: str, fg_color: str, fmt: str, args: ImageQueryArgs
):
    loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
    im: Image.Image = await loop.run_in_executor(
        None, create_image_sync, size, bg_color, fg_color, fmt, args
    )
    return await loop.run_in_executor(None, im_to_bytes, im, fmt, args)


@router.get(
    "/{width}/{height}/{bg_color}/{fg_color}/{fmt}/",
    response_class=StreamingResponse,
    responses={200: {"description": "A generated image.", "content": {"image/*": {}}}},
)
async def size_and_format(
    path: ImagePathArgs = Depends(image_path),
    args: ImageQueryArgs = Depends(image_query),
):

    image = await create_image(*attr.astuple(path), args)
    res = StreamingResponse(image, media_type=f"image/{path.fmt}")
    return res


@router.get("/json/{width}/{height}/{bg_color}/{fg_color}/{fmt}/")
async def size_and_format_json(
    path: ImagePathArgs = Depends(image_path),
    args: ImageQueryArgs = Depends(image_query),
):
    fmt = path[-1]
    image = await create_image(*attr.astuple(path), args)
    return {"size": len(image.getvalue()), "media-type": f"image/{fmt}"}
