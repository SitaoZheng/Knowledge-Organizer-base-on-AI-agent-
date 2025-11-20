import os
import json
import re
from datetime import datetime
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from dotenv import load_dotenv

load_dotenv()
MODEL_TYPE = os.getenv('MODEL_TYPE', 'mock').lower()
FORCE_MOCK_MODE = os.getenv('FORCE_MOCK_MODE', 'false').lower() == 'true'

def get_model():
    if FORCE_MOCK_MODE:
        return None, 'mock'

    try:
        if MODEL_TYPE == 'google':
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model_name = os.getenv('GOOGLE_MODEL_NAME', 'gemini-2.5-flash-lite')
            return genai.GenerativeModel(model_name), 'google'
        elif MODEL_TYPE == 'deepseek':
            try:
                import openai
                api_key = os.getenv("DEEPSEEK_API_KEY")
                base_url = "https://api.deepseek.com/v1"
                model_name = os.getenv('DEEPSEEK_MODEL_NAME', 'deepseek-chat')
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
                return (client, model_name), 'deepseek'
            except ImportError:
                print("openai package not installed, cannot use DeepSeek model, switching to mock mode")
                return None, 'mock'
        else:
            print(f"Unknown model type: {MODEL_TYPE}, using mock mode")
            return None, 'mock'
    except Exception as e:
        print(f"Model initialization failed: {e}, using mock mode")
        return None, 'mock'

model, current_model_type = get_model()

def generate_text(prompt, max_tokens=1000):
    if current_model_type == 'google' and model:
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Google model call failed: {e}")
            return None
    elif current_model_type == 'deepseek' and model:
        try:
            client, model_name = model
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"DeepSeek model call failed: {e}")
            return None
    else:
        print("Generating response using mock mode")
        return None

class MemoryManager:
    def __init__(self, memory_path="memory.json"):
        self.memory_path = memory_path
        self.data = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "user_preferences": {
                "category_hierarchy": ["Technology", "Life", "Work", "Study"],
                "preferred_level3": {}
            },
            "session_status": {
                "last_processed": "",
                "total_processed": 0
            }
        }

    def save_memory(self):
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def update_preferences(self, new_prefs):
        self.data["user_preferences"].update(new_prefs)
        self.save_memory()

    def update_session(self, doc_name):
        self.data["session_status"]["last_processed"] = doc_name
        self.data["session_status"]["total_processed"] += 1
        self.save_memory()


class DocumentParserAgent:
    def parse(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext == ".docx":
            return self._parse_docx(file_path)
        elif ext == ".txt":
            return self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _parse_pdf(self, file_path):
        try:
            reader = PdfReader(file_path)
            text = ""
            page_count = len(reader.pages)
            print(f"PDF file contains {page_count} pages")

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                    print(f"Extracted text from page {i + 1}")
                else:
                    print(f"No text extracted from page {i + 1}")

            print(f"Original text length after PDF parsing: {len(text)} characters")
            cleaned_text = self._clean_text(text)
            print(f"Cleaned text length after PDF parsing: {len(cleaned_text)} characters")

            if len(cleaned_text) < 10:
                print("Warning: PDF parsing result is too short, it may be an image-based PDF or encrypted PDF")
                try:
                    import fitz
                    doc = fitz.open(file_path)
                    alt_text = ""
                    for page in doc:
                        alt_text += page.get_text()
                    if alt_text:
                        print(f"Extracted text using PyMuPDF alternative method, length: {len(alt_text)} characters")
                        return self._clean_text(alt_text)
                except ImportError:
                    print("PyMuPDF not installed, cannot use alternative parsing method")
                except Exception as e:
                    print(f"Alternative parsing method failed: {e}")

            return cleaned_text
        except Exception as e:
            print(f"Error occurred during PDF parsing: {e}")
            return ""

    def _parse_docx(self, file_path):
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return self._clean_text(text)

    def _parse_txt(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return self._clean_text(text)

    def _clean_text(self, text):
        text = re.sub(r"\n+", "\n", text)
        text = re.sub(r'[^\w\s\u4e00-\u9fa5，。！？；："\'()\[\]{}\-.,;:!?()\[\]{}/@#$%^&*+=]', '', text)
        text = re.sub(r"\s+", " ", text)
        result = text.strip()
        print(f"Text length after cleaning: {len(result)} characters")
        return result

class ContentClassifierAgent:
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    def classify(self, text, filename):
        prefs = self.memory.data["user_preferences"]
        prompt = f"""
Please classify the document according to the three-level classification system, output in JSON format:
{{
    "level1": "Level 1 category (select from {list(prefs['category_hierarchy'])} or add new)",
    "level2": "Level 2 category (e.g., Technology→Programming Languages)",
    "level3": "Level 3 category (more detailed, e.g., Programming Languages→Python)"
}}
Document content summary: {text[:500]}
Document filename: {filename}
Note: Prioritize using user's commonly used categories (e.g., Level 3 categories for Programming Languages include {prefs['preferred_level3'].get('Programming Languages', [])})
Please ensure all categories are in English.
Please output ONLY the JSON and nothing else.
"""
        response_text = generate_text(prompt)
        print(f"Classification response: {response_text[:150]}..." if response_text else "No response")
        if not response_text:
            print("Error: Empty response from model")
            return {"level1": "Unclassified", "level2": "Unclassified", "level3": "Unclassified"}
        try:
            cleaned_response = response_text.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3].strip()

            category = json.loads(cleaned_response)

            required_keys = ['level1', 'level2', 'level3']
            for key in required_keys:
                if key not in category or not category[key]:
                    raise ValueError(f"Missing or empty required field: {key}")

            if category["level2"] not in prefs["preferred_level3"]:
                prefs["preferred_level3"][category["level2"]] = []
            if category["level3"] not in prefs["preferred_level3"][category["level2"]]:
                prefs["preferred_level3"][category["level2"]].append(category["level3"])
            self.memory.update_preferences(prefs)

            return category
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response_text}")
            try:
                import re
                json_match = re.search(r'\{[^{}]*\}', cleaned_response)
                if json_match:
                    category = json.loads(json_match.group(0))
                    print("Successfully extracted JSON using regex fallback")
                    return category
            except Exception as fallback_error:
                print(f"Fallback extraction failed: {fallback_error}")
            return {"level1": "Unclassified", "level2": "Unclassified", "level3": "Unclassified"}
        except Exception as e:
            print(f"Classification processing error: {e}")
            return {"level1": "Unclassified", "level2": "Unclassified", "level3": "Unclassified"}


class RelationExtractorAgent:
    def extract(self, text, all_docs):
        prompt = f"""
        Extract from the document content:
        1. Core ideas (3-5 items, concise and clear)
        2. Keywords (5-8 items, separated by commas)
        Output format: JSON
        {{
            "core_ideas": ["Idea 1", "Idea 2"],
            "keywords": ["Keyword 1", "Keyword 2"]
        }}
        Document content: {text[:1000]}
        """
        response_text = generate_text(prompt)
        try:
            result = json.loads(response_text)
        except:
            result = {"core_ideas": ["No core ideas extracted"], "keywords": ["No keywords extracted"]}

        related_docs = []
        if all_docs:
            doc_summaries = "\n".join([
                f"Document ID: {doc['id']}, Title: {doc['filename']}, Keywords: {','.join(doc['keywords'])}"
                for doc in all_docs
            ])
            prompt_relation = f"""
            Below is the current document content and summaries of processed documents. Please determine which processed documents are related to the current document (based on keywords or topics):
            Current document keywords: {','.join(result['keywords'])}
            Processed documents summaries: {doc_summaries}
            Output list of related document IDs (return empty list if no relevance): ["doc_001", "doc_003"]
            """

            relation_response_text = generate_text(prompt_relation)
            try:
                related_docs = json.loads(relation_response_text)
            except:
                related_docs = []

        return {
            "core_ideas": result["core_ideas"],
            "keywords": result["keywords"],
            "related_docs": related_docs
        }