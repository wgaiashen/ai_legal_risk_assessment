from typing_extensions import TypedDict
import enum

# Imports a string containing the list of risk factors, along with their 
# descriptions at each risk level.
from constants import RISK_FACTORS


class RiskLevel(enum.Enum):
    VERY_HIGH = "very high risk"
    HIGH = "high risk"
    MEDIUM = "medium risk"
    LOW = "low risk"


class LevelJustification(TypedDict):
    risk_level: RiskLevel
    justification: str


class RiskAssessment(TypedDict):
    User_and_Audience: LevelJustification
    Use_and_Functionality: LevelJustification
    Data_Processed: LevelJustification
    Legal_and_Regulatory_Compliance: LevelJustification
    Transparency: LevelJustification
    Technology: LevelJustification
    Bias_and_Fairness: LevelJustification
    Operational_Risk: LevelJustification
    Training_Data: LevelJustification
    Reputational_Risk: LevelJustification
    clarifying_questions: list[str]

class Summary(TypedDict):
    AI_tool_description: str
    risk_level_why: str
    recommendations: str