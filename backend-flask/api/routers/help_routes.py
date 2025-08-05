import base64

from fastapi import APIRouter

router = APIRouter(
    tags=["help"],
    prefix="/help"
)


@router.get("")
async def get_help_document():
    with open("assets/help/ibs_help.pdf", "rb") as pdf_file:
        pdf_encoded = base64.b64encode(pdf_file.read()).decode("utf-8")

    return pdf_encoded
