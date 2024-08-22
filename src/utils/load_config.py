
import os
import yaml
import json
import torch
import shutil
import chromadb
from pyprojroot import here
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceInstructEmbeddings

import instructor
from InstructorEmbedding import instructor


print("Environment variables are loaded:", load_dotenv())


class LoadConfig:
    def __init__(self) -> None:
        with open(here("configs/app_config.yml")) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)
        self.load_directories(app_config=app_config)
        self.load_llm_configs(app_config=app_config)
        self.load_rag_config(app_config=app_config)
        self.load_ai_models()
        self.load_chroma_client()

        # Un comment the code below if you want to clean up the upload csv SQL DB on every fresh run of the chatbot. (if it exists)
        # self.remove_directory(self.uploaded_files_sqldb_directory)

    def load_directories(self, app_config):
        self.stored_csv_xlsx_directory = here(
            app_config["directories"]["stored_csv_xlsx_directory"])
        self.sqldb_directory = str(here(
            app_config["directories"]["sqldb_directory"]))
        self.uploaded_files_sqldb_directory = str(here(
            app_config["directories"]["uploaded_files_sqldb_directory"]))
        self.stored_csv_xlsx_sqldb_directory = str(here(
            app_config["directories"]["stored_csv_xlsx_sqldb_directory"]))
        self.persist_directory = app_config["directories"]["persist_directory"]

    def load_llm_configs(self, app_config):
        self.model_name = os.getenv("gpt_deployment_name")
        self.agent_llm_system_role = app_config["llm_config"]["agent_llm_system_role"]
        self.rag_llm_system_role = app_config["llm_config"]["rag_llm_system_role"]
        self.temperature = app_config["llm_config"]["temperature"]
        self.embedding_model_name = os.getenv("embed_deployment_name")

    def load_ai_models(self):
        gemini_api_key = os.environ["GEMINI_API_KEY"]
        gemini_model_endpoint = os.environ["GEMINI_ENDPOINT"]
        temprature = os.environ["temprature"]

        # kwargs for HFInstructEmbeddings
        
        
        # Determine the device to use and print GPU details if available
        if torch.cuda.is_available():
            device = 'cuda'
            gpu_details = torch.cuda.get_device_properties(0)  # Get properties of the first GPU
            print(f"Using GPU: {gpu_details.name}")
            print(f"  Memory Allocated: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
            print(f"  Memory Cached: {torch.cuda.memory_reserved(0) / 1e9:.2f} GB")
            print(f"  Total Memory: {gpu_details.total_memory / 1e9:.2f} GB")
        else:
            device = 'cpu'
            print("Using CPU")
        
        model_kwargs = {'device': device}
        encode_kwargs = json.loads(os.environ["local_embeddings_conversion_batchSize"])
        HFInstructEmbeddings_model = os.environ["HFInstructEmbedding_model"]
        # below code will be used for the GPT and embedding models

        self.embeddings_client = HuggingFaceInstructEmbeddings(
            model_name=HFInstructEmbeddings_model,
            model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)
        
        # initializing llm
        self.langchain_llm = ChatGoogleGenerativeAI(
            model=gemini_model_endpoint, google_api_key=gemini_api_key, temperature=temprature)

    def load_chroma_client(self) -> None:
        self.chroma_client = chromadb.PersistentClient(
            path=str(here(self.persist_directory)))

    def load_rag_config(self, app_config):
        self.collection_name = app_config["rag_config"]["collection_name"]
        self.top_k = app_config["rag_config"]["top_k"]

    def remove_directory(self, directory_path: str):
        """
        Removes the specified directory.

        Parameters:
            directory_path (str): The path of the directory to be removed.

        Raises:
            OSError: If an error occurs during the directory removal process.

        Returns:
            None
        """
        if os.path.exists(directory_path):
            try:
                shutil.rmtree(directory_path)
                print(
                    f"The directory '{directory_path}' has been successfully removed.")
            except OSError as e:
                print(f"Error: {e}")
        else:
            print(f"The directory '{directory_path}' does not exist.")
