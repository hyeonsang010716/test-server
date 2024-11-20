from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()


class OCRAgent:
    def __init__(self):
        self.file_names = self.__file_names_init()
        self.__data_preprocessing_init()
    def __file_names_init(self):
        """ PDF 파일을 로드해서, 리스트에 저장 """
        file_names = []
        base_path = "./assets/pdfs"
        # TXT 파일 읽기
        pdf_files = [f for f in os.listdir(base_path) if f.endswith(".pdf")]
        for file in pdf_files:
            file_name = file.split("/")[-1][:-4]
            os.makedirs(f"assets/data/{file_name}", exist_ok=True)
            file_names.append(file_name)
        return file_names

    def get_ocr(self , file_path , file_name):
        """ PDF 파일 OCR 정보 추출 """
        ocr_file_path = f"assets/data/{file_name}/{file_name}.txt"
        if os.path.exists(ocr_file_path):
            with open(ocr_file_path, "r", encoding="utf-8") as txt_file:
                content = txt_file.read()
            
            return content
        else:
            loader = AzureAIDocumentIntelligenceLoader(
                api_endpoint=os.getenv("AZURE_COGNITIVE_API_ENDPOINT"),
                api_key=os.getenv("AZURE_COGNITIVE_API_KEY"),
                file_path=file_path,
                api_model="prebuilt-layout",
                mode="page",
            )
            documents = loader.load()

            combined_string = " ".join([doc.page_content for doc in documents])

            with open(ocr_file_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(combined_string)
            
            return combined_string

    def get_summary(self , file_name):
        """ 추출된 정보 요약 """
        summary_file_path = f"assets/data/{file_name}/{file_name}_summary.txt"
        if os.path.exists(summary_file_path):
            with open(summary_file_path, "r", encoding="utf-8") as txt_file:
                content = txt_file.read()
            return content
        else:
            ocr_file_path = f"assets/data/{file_name}/{file_name}.txt"
            if os.path.exists(ocr_file_path):
                with open(ocr_file_path, "r", encoding="utf-8") as txt_file:
                    content = txt_file.read()

            template_str = (
                "당신은 MBC+ 비대면 과정인 '생성형 AI활용 콘텐츠 전문가 양성과정 Cinema 4D' 수업을 담당하고 있는 선생님입니다.\n"
                "당신의 역할은 학생들이 Cinema 4D 수업 교재를 쉽게 이해하고 공부할 수 있도록 요약해주는 역할을 합니다.\n"
                "교재에서 핵심 개념을 요약합니다.\n"
                "절대 사전 학습된 데이터를 사용하지 말고, 주어진 교재만을 가지고 요약합니다.\n\n"
                "# 교재:\n"
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

            chain_output = chain.invoke({"content": content})

            with open(summary_file_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(chain_output)

            return chain_output

    def get_content(self , file_name):
        """ 추출된 정보 불러오기 """
        content_file_path = f"assets/data/{file_name}/{file_name}_content.txt"
        if os.path.exists(content_file_path):
            with open(content_file_path, "r", encoding="utf-8") as txt_file:
                content = txt_file.read()
            return content
        else:
            ocr_file_path = f"assets/data/{file_name}/{file_name}.txt"
            if os.path.exists(ocr_file_path):
                with open(ocr_file_path, "r", encoding="utf-8") as txt_file:
                    content = txt_file.read()

            template_str = (
                "아래 내용을 보기 좋게 정리해줘\n\n"
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

            chain_output = chain.invoke({"content": content})

            with open(content_file_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(chain_output)

            return chain_output


    def __data_preprocessing_init(self):
        """ 데이터 세팅 """
        for file_name in self.file_names:
            file_path = f"assets/pdfs/{file_name}.pdf"
            self.get_ocr(file_path , file_name)
            self.get_summary(file_name)
            self.get_content(file_name)

    def get_data(self , file_name):
        return {"summary" : self.get_summary(file_name) , "content" : self.get_content(file_name)}


if __name__ == "__main__":
    Agent = OCRAgent()

    
