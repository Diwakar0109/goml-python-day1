from fastapi import APIRouter, Depends, HTTPException, status
 
import os
from app.schemas.ticket import SummarizeRequest, SummarizeResponse
from app.services.bedrock_services import (
    BedrockService,
    BedrockServiceError,
    FakeBedrockService,
)

def get_bedrock_service() -> BedrockService | FakeBedrockService:
    aws_demo_mode = os.getenv("AWS_DEMO_MODE", "false").lower() == "true"
    if aws_demo_mode:
        return FakeBedrockService()
    return BedrockService()
 
 
router = APIRouter(prefix="/ai", tags=["AI"])
 
 
@router.post("/summarize", response_model=SummarizeResponse)
def summarize_ticket(
    payload: SummarizeRequest,
    service: BedrockService | FakeBedrockService = Depends(get_bedrock_service),
) -> dict[str, str]:
    try:
        return service.summarize_ticket(payload.ticket_description)
    except BedrockServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI service is temporarily unavailable",
        ) from exc 