# agents/patient_evaluation_agent.py

from typing import Dict
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI


class PatientEvaluationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.1)

        self.prompt = PromptTemplate(
            input_variables=["patient_data"],
            template="""
            You are a clinical assistant summarizing a diabetic patient's condition for a physician.

            Below is structured patient data in JSON format:

            {patient_data}

            Write a natural-language clinical summary that includes:
            1. Age and gender
            2. Major chronic conditions (diabetes, hypertension, CKD, etc.)
            3. Most recent lab results (HbA1c, eGFR, LDL, etc.)
            4. Active medications (highlight diabetes meds)
            5. Any abnormal vitals
            6. Anything clinically urgent

            Be concise, structured, and use medical terminology. Use bullet points or paragraphs as needed.
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    async def run(self, patient_json: Dict) -> Dict:
        """
        Main entry for the Patient Evaluation Agent.

        Args:
            patient_json (Dict): Combined patient data object

        Returns:
            Dict: {"summary": "..."}
        """
        from json import dumps

        input_text = dumps(patient_json, indent=2)
        result = await self.chain.arun(patient_data=input_text)
        return {"summary": result.strip()}

print("Hello")