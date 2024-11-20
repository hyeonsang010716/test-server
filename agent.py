from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from prompts import system_prompt
from pdf_extractor import OCRAgent
from dotenv import load_dotenv
import os

load_dotenv()

class LectureAgent:
    def __init__(self):
        self.OcrAgent = OCRAgent()

    def get_summary(self , file_name):
        return self.OcrAgent.get_data(file_name)["summary"]
    
    def get_content(self, file_name):
        return self.OcrAgent.get_data(file_name)["content"]
    
    def get_quiz(self , file_name):
        template_str = (
            "당신은 MBC+ 비대면 과정인 '생성형 AI활용 콘텐츠 전문가 양성과정 Cinema 4D' 수업을 담당하는 선생님입니다.\n"
            "당신의 역할은 이번 수업 시간에 배운 진도를 바탕으로 이해도를 평가할 수 있는 문제를 출제하는 문제 출제자입니다.\n\n"
            "다음 지침을 참고하여 문제를 출제해 주세요:\n"
            "1. 문제 유형: 선택형, 서술형, 빈칸 채우기 중 적절하게 혼합하여 출제하세요.\n"
            "2. 선택형 문제는 4개의 보기와 정답을 포함해 주세요.\n"
            "3. 문제 수: 총 5문제를 출제하세요. 문제의 난이도는 초급부터 고급까지 다양하게 구성해 주세요.\n"
            "4. 서술형 문제는 수업 내용의 핵심 개념을 이해할 수 있도록 유도하는 질문을 포함해 주세요.\n"
            "5. 모든 문제는 Cinema 4D 수업 진도를 기반으로 출제하며, 수업에서 다룬 핵심 개념과 용어를 활용하세요.\n"
            "6. 문제와 정답은 '문제 출제'와 '정답 공개' 공간으로 따로 분리하세요.\n"
            "7. 정답은 **응답 마지막에 '## 정답 공개' 공간을 만들어서, 모든 문제의 정답을 공개해주세요.**\n\n"
            "수업 시간에 배웠던 진도:\n"
            "{content}"
        )

        prompt_template = PromptTemplate(
            template=template_str,
            input_variables=["content"],
        )

        model = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"), temperature=0
        )

        ouput_parser = StrOutputParser()

        chain = prompt_template | model | ouput_parser
        
        content = self.get_content(file_name)
        chain_output = chain.invoke({"content": content})

        return chain_output
    
    def query_filter(self , file_name , user_input):
        class QuestionFilterResult(BaseModel):
            result: bool = Field(
                description="Whether the question can be answered or not"
            )

        output_parser = PydanticOutputParser(pydantic_object=QuestionFilterResult)

        template_str = (
            "참고 자료에 근거하여 사용자 질문에 답변이 가능한지 여부를 판단합니다.\n"
            "당신은 사전 학습된 지식이 아닌 제공된 참고자료만을 바탕으로 답변이 가능한지 판단해야 합니다.\n\n"
            "사용자 질문:\n" 
            "{question}\n\n"
            "참고 자료:\n"
            "{context}\n\n"
            "{format_instructions}"
        )

        prompt_template = PromptTemplate(
            template=template_str,
            input_variables=["question" , "context"],
            partial_variables={
                "format_instructions": output_parser.get_format_instructions(),
            },
        )
        
        model = AzureChatOpenAI(model="gpt-4o", temperature=0)

        query_filter_chain = (
            prompt_template
            | model
            | output_parser  
        )

        chain_ouput = query_filter_chain.invoke({"context": self.get_summary(file_name), "question": user_input})

        return chain_ouput

    def get_chat(self , file_name , question):

        prompt_template = PromptTemplate(
            template=system_prompt,
            input_variables=["question" , "context"],
        )

        model = AzureChatOpenAI(model="gpt-4o", temperature=0)  
        
        chain = prompt_template | model | StrOutputParser()

        output = chain.invoke({"context" : self.get_content(file_name) , "question" : question})

        return output

if __name__ == "__main__" : 
    quiz = LectureAgent()

    # print(quiz.get_quiz("1강"))

    print(quiz.get_chat("1강" , "미드저니가 뭔지 모르겠어"))