# Personal Knowledge Base Intelligent Organization Assistant

A local document automation processing tool based on DeepSeek API (also compatible with Gemini API), which can instantly transform messy local documents into a structured knowledge base. 

## 1. Problem Statement

Three core pain points in personal knowledge management:

1. **Format chaos**: Local documents include various formats such as PDF, WORD, TXT, with mixed content (e.g., notes containing code, random annotations);
2. **Inefficient organization**: Manual classification and key information extraction require reading each document one by one, taking an average of 8 hours for 100 documents, and it is easy to miss key information;
3. **Difficult retrieval**: Lack of a unified index, making it inefficient to find "Python list operations" by searching through multiple folders.

These problems lead to fragmented personal knowledge accumulation, making it difficult to form a systematic knowledge network.

## 2. Why agents?

Compared with traditional document management tools (such as Notion, Evernote), Agents are a better solution for the following reasons:

- **Autonomy**: Agents can automatically complete the entire process of "parsing → classification → extraction → association" without manual step-by-step operations (traditional tools require manual labeling of tags and classification);
- **Adaptability**: By memorizing user preferences (e.g., "prioritize classification by 'learning stage'"), subsequent organization will automatically adapt, becoming more in line with personal habits over time;
- **In-depth processing**: Based on the understanding ability of LLM, it can extract implicit information (e.g., summarizing "Python function usage skills" from code examples), while traditional tools can only perform shallow processing based on keywords.

## 3. What you created

### 3.1 Overall Architecture

Adopting a "three-level Agent serial architecture" with the following core components:

| Layer Name                    | Core Components/Content                                      | Function Description                                                                                                          | Tool/Logic Support                                                                                                        |
|-------------------------------|--------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| Input Layer                   | Local document folder                                        | Receive local documents to be organized as the data source for processing                                                     | Support PDF, WORD, TXT formats                                                                                            |
| Agent Layer (Core Processing) | 1. Document Parsing Agent<br>2. Content Classification Agent | 1. Read local files and extract plain text (remove format markers)<br>2. Automatically classify by subject/subject            | 1. PyPDF2, python-docx, fitz<br>2. Generate classification labels based on DeepSeek, matching user historical preferences |
| Output Layer                  | 1. Structured knowledge base<br>2. Retrieval interface       | 1. Persistently store structured knowledge<br>2. Support multi-dimensional quick query                                        | 1. JSON format (local file storage)<br>2. Query by classification, keywords, related documents                            |
| Memory Layer                  | 1. User preference memory<br>2. Session state                | 1. Record user classification habits to adapt to personalized needs<br>2. Track the progress of current document organization | Local JSON file storage (persistence of memory data)                                                                      |
### 3.2 Key Features

1. **Multi-format parsing**: Automatically read PDF (except scanned copies), TXT, WORD documents, and extract plain text content;
2. **Intelligent classification**: Automatically classify by "first-level classification (e.g., technology/life) → second-level classification (e.g., programming language/cuisine)", supporting memory of preferences after manual adjustment by users;
3. **Information extraction**: Extract core viewpoints (3-5 items) and keywords (5-8 items) of documents, such as extracting "list comprehension syntax" from Python tutorials;
4. **Association discovery**: Automatically identify associations between documents to form a knowledge network;
5. **Local retrieval**: Query through simple instructions and return classification, core viewpoints, and file paths.

## 4. Demo

### 4.1 Step-by-Step Operation Process

1. **Prepare documents**: Put 4 documents (including 1 PDF file, 2 DOC documents, 1 TXT file) into the `input_docs` folder;
2. **Start the tool**: Run `python main.py`, and the tool will automatically detect the folder and start processing;
3. **Agent execution**:
   - Document Parsing Agent: Extract plain text from all documents (e.g., remove headers and footers in PDF);
   - Content Classification Agent: Classify 2 documents into "Technology → Programming Language → Python";
   - Association Extraction Agent: Extract the core viewpoint "List comprehension is more efficient than for loops" from Python documents, and mark the association with the "Python performance optimization" document;
4. **View results**: After processing, `knowledge_base.json` will be generated in the `output_kb` folder, containing all structured information.

## 5. The Build

### 5.1 Technologies Used

| Module               | Tools/Libraries                                          | Purpose                                                                         |
|----------------------|----------------------------------------------------------|---------------------------------------------------------------------------------|
| LLM Model            | DeekSeek API, Gemini API                                 | Classification decision-making, core viewpoint extraction, correlation analysis |
| Document Parsing     | PyPDF2, python-docx, python-dotenv                       | Extract plain text content from PDF/WORD/TXT                                    |
| Data Storage         | JSON files (local)                                       | Store structured knowledge base and user preferences                            |
| Session Memory       | Custom Memory class (implemented with Python dictionary) | Record organization progress and user classification preferences                |
| Development Language | Python 3.10                                              | Implementation of core logic                                                    |

### 5.2 Setup Instructions

#### 5.2.1 Prerequisites

- Install Python 3.10+;
- Obtain DeepSeek API Key and Google Gemini API Key;
- Prepare local documents to be organized (PDF/WORD/TXT, placed in the `input_docs` folder).

#### 5.2.2 Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/SitaoZheng/Knowledge-Organizer-base-on-AI-agent-.git
cd knowledge-organizer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```
Contents of requirements.txt:
```
google-generativeai==0.7.2
PyPDF2==3.0.1
python-docx==1.2.0
python-dotenv==1.2.1
openai==2.8.1
fitz==0.0.1.dev2
```

3. **Configure API Key**
Fill in the API Key in the `.env` file:
```
# AGENT MODEL CONFIGURATION

# Optional value: 'google', 'deepseek', 'mock'
MODEL_TYPE='deepseek'

# Google Gemini API Configuration
GOOGLE_API_KEY='Your-Google-API-Key'
GOOGLE_MODEL_NAME='gemini-2.5-flash-lite'

# DeepSeek API Configuration
DEEPSEEK_API_KEY='Your-Deepseek-API-Key'
DEEPSEEK_MODEL_NAME='deepseek-chat'

# Is it mandatory to use the simulation mode (even if other models are configured, local simulation will be used instead) (code debugging can be enabled)?
FORCE_MOCK_MODE=False
```

4. **Prepare input documents**
Create an `input_docs` folder in the project root directory and place the documents to be organized (supporting PDF, WORD, TXT).

5. **Run the tool**
```bash
python main.py
```
After processing, the structured knowledge base will be saved to `output_kb/knowledge_base.json`.

### 5.3 Key Code Snippets

#### 1. Positioning of main.py

`main.py` is the **core entry file** of the entire "Personal Knowledge Base Intelligent Organization Assistant". It is responsible for connecting all underlying components (Agents, memory modules), organizing the entire document processing workflow, providing retrieval functions, and defining user interaction logic. Users do not need to pay attention to complex Agent implementation details; they can complete the entire process of "document input → automated processing → structured knowledge base output → retrieval and use" just by running this file, serving as the "operation center" of the tool.

#### 2. Analysis of Core Methods

##### (1) `init_folders()`: Folder Initialization Method

- **Function**: Automatically create core folders required for tool operation, avoiding file read/write errors caused by non-existent paths, and reducing the cost of manual configuration for users.
- **Specific Logic**:
  - Check and create the `input_docs` folder: used to store users' original documents to be organized (PDF/WORD/TXT);
  - Check and create the `output_kb` folder: used to store the processed structured knowledge base (`knowledge_base.json`);
  - Use the `exist_ok=True` parameter to ensure no error is reported when the folder already exists, supporting repeated runs.
- **User Value**: Users do not need to manually create folders; they can directly put documents into the automatically generated `input_docs`, simplifying operation steps.

##### (2) `process_documents()`: Core Process of Automated Document Processing

- **Function**: Connect all Agents and memory modules to execute the fully automated process of "parsing → classification → extraction → storage", which is the core business logic of the tool.
- **Specific Execution Steps**:
  1. **Component Initialization**: Create instances of `MemoryManager` (memory management), `DocumentParserAgent` (document parsing), `ContentClassifierAgent` (content classification), and `RelationExtractorAgent` (association extraction) to establish the toolchain;
  2. **Knowledge Base Loading**: Check if `output_kb/knowledge_base.json` exists. If it exists, load the existing knowledge base (to avoid reprocessing documents); if not, initialize an empty knowledge base structure;
  3. **Document List Acquisition**: Read all files in the `input_docs` folder and filter out valid documents (skip subfolders);
  4. **Batch Document Processing**: Traverse each document and execute the following sub-steps:
     - Skip processed documents: Judge by comparing file names to avoid redundant work;
     - Document Parsing: Call `DocumentParserAgent.parse()` to extract plain text, automatically adapting to different file formats;
     - Intelligent Classification: Call `ContentClassifierAgent.classify()` to generate three-level classification, and update user preference memory at the same time;
     - Information Extraction: Call `RelationExtractorAgent.extract()` to extract core viewpoints, keywords, and related documents;
     - Knowledge Base Update: Generate a unique ID for the current document, and add structured information (classification, core viewpoints, path, etc.) to the knowledge base;
     - Memory Update: Record the current processing progress (e.g., "last processed document name", "total processing quantity");
  5. **Knowledge Base Saving**: Write the updated knowledge base (including all document structured data and user preferences) to `output_kb/knowledge_base.json` to ensure data persistence.
- **Core Value**: Users can complete automated organization of all documents without intervention, just by waiting for the script to execute.

##### (3) `search_knowledge(query_type, query_value)`: Local Knowledge Base Retrieval Function

- **Function**: Provide an easy-to-use local retrieval interface, supporting queries by classification, keywords, and related document IDs, solving the problem of "how to quickly find in a structured knowledge base".
- **Parameter Description**:
  - `query_type`: Retrieval type, supporting 3 types:
    - "category": Retrieve by classification (matching any level in the three-level classification, such as "Python", "Travel");
    - "keyword": Retrieve by keyword (matching the extracted keywords of documents, such as "list comprehension", "subway ticket");
    - "related": Retrieve by related document ID (matching the `related_docs` field of documents, such as "doc_001");
  - `query_value`: Retrieval keyword (e.g., "Python", "Travel", "doc_001").
- **Execution Logic**:
  1. Check if the knowledge base file exists; if not, return a prompt;
  2. Traverse all documents in the knowledge base and match documents that meet the conditions according to the retrieval type;
  3. Format and output results: Include the file name, classification path, core viewpoint preview, and file path of the matched documents, facilitating users to quickly locate the original documents.
- **User Value**: Avoid users manually browsing JSON files; quickly find target documents through simple instructions, improving the reuse efficiency of the knowledge base.

#### 3. Code Running Organization Logic

The running process of `main.py` follows a linear logic of "**initialization → processing → retrieval**", with a clear and non-redundant structure:

1. First execute `init_folders()`: Ensure input and output directories are ready, paving the way for subsequent processing;
2. Then execute `process_documents()`: The core processing flow completes the automated structured transformation of documents;
3. Finally, execute example retrievals: Demonstrate the retrieval function through 2 common scenarios (searching for "Python" by classification, searching for "Travel" by keyword) to guide users to use it.

The entire running process requires no additional operations from users. As long as the `input_docs` folder contains documents and the `.env` file is configured with the API Key, it can run with one click.

#### 4. User Interaction Part (`__name__ == "__main__"`)

This is the direct interaction entry between users and the tool, defining the "usage process" of the tool:

- **User Operation Steps**:
  1. Preparations: Users put documents to be organized into the `input_docs` folder and configure the API Key in `.env`;
  2. Start the tool: Run `python main.py`, and the script will execute automatically;
  3. View results:
     - After processing, the structured knowledge base is automatically saved to `output_kb/knowledge_base.json`, which users can directly view or edit secondarily;
     - The script will output example retrieval results at the end, allowing users to intuitively understand the effect of the retrieval function;
  4. Custom retrieval: Users can modify the parameters of `search_knowledge()` (e.g., `search_knowledge("keyword", "performance optimization")`) to achieve personalized queries.
- **Interaction Design Highlights**:
  - Zero learning cost: Users do not need to master programming knowledge, only need two steps: "put documents → run script";
  - Visual feedback: Progress prompts will be output during processing (e.g., "Start processing: python_list.pdf", "Classification result: Technology → Programming Language → Python"), allowing users to understand the current status;
  - Fault tolerance: Documents that fail to be parsed will be skipped and prompted, without causing the entire script to terminate.

## IV. Core Concepts and Values

### 1. Core Concept

The project is centered on "**minimalist local knowledge management**", solving the inefficiency problem of personal document organization through Agent-based design:

- **Local first**: memory.json will be automatically generated after use, and all data is stored in local JSON files, without the need for external APIs or databases, protecting privacy and reducing the threshold for use;
- **Progressive learning**: Record user classification preferences through the memory module, so that the Agent becomes more in line with personal habits over time (e.g., prioritizing classification by "learning stage" rather than "subject");
- **Lightweight implementation**: Only rely on basic document parsing libraries and APIs, avoiding complex dependencies, allowing ordinary users to deploy with one click.

### 2. Relevance to Track

The project belongs to the "Freestyle Track", with the following core alignment points:

- **Scenario freedom**: Focus on the flexible scenario of personal knowledge management, not limited to enterprise-level or specific fields;
- **Technical simplicity**: Abandon complex external API integration and multi-service architecture, and only implement core functions through local tools, conforming to the "lightweight" tolerance of the free track;
- **Innovative flexibility**: Apply Agent architecture to personal document processing, breaking through the manual operation mode of traditional document management tools, reflecting the innovative attempts encouraged by the free track.

### 3. Innovation & Value

- **Innovation Points**:
  1. Simplified Agent architecture: Simplify the complex multi-Agent system into a "parsing → classification → extraction" three-level serial structure, reducing implementation difficulty;
  2. Local memory mechanism: Lightly store user preferences through JSON files, enabling personalized adaptation without professional databases;
  3. Seamless processing: Users only need to put documents and run the script, with no intervention throughout the process, achieving "zero learning cost" use.
- **Value Points**:
  1. Efficiency improvement: Shorten document organization time from hours to minutes, freeing up personal time;
  2. Knowledge externalization: Convert implicit knowledge (e.g., associations between documents) into structured data for easy reuse;
  3. Privacy protection: All data is stored locally, avoiding the risk of sensitive notes (e.g., work records, learning experiences) being uploaded to the cloud.

## V. Writeup (Project Journey and Summary)

### 1. Project Journey

#### Phase 1: Pain Point Identification and Solution Design (2 days)

- **Pain point research**: Through personal experience of organizing study notes, three problems were identified: "format chaos", "time-consuming classification", and "difficult retrieval";
- **Solution design**: Determine the "three-level Agent serial processing" scheme, avoiding the introduction of external APIs (such as document translation, web search) to ensure simplicity and controllability.

#### Phase 2: Core Function Development (3 days)

- **Document parsing**: Integrate libraries such as PyPDF2 and python-docx to realize multi-format text extraction, solving the "format chaos" problem;
- **Agent logic**: Complete the Prompt design of classification and extraction Agents, and realize automatic classification and information extraction through DeepSeek;
- **Memory module**: Design a simple JSON memory mechanism to record user classification preferences and avoid re-learning each time.

#### Phase 3: Testing and Optimization (2 days)

- **Function testing**: Test with multiple mixed-format documents, fixing problems such as "unable to parse PDF scanned copies" and "timeout in long text processing";
- **Experience optimization**: Add progress prompts and failure skipping mechanisms to improve user experience;
- **Retrieval function**: Implement retrieval by classification and keywords to solve the "difficulty in finding" problem.

### 2. Project Summary

The project successfully built a lightweight personal knowledge base intelligent organization assistant, achieving three goals:

1. **Functional integrity**: Complete the full-process functions of document parsing, automatic classification, information extraction, association discovery, and local retrieval;
2. **Usability**: No complex configuration is required; users can generate a structured knowledge base by putting documents and running the script;

The core insight of the project is that the Agent architecture is not only applicable to complex enterprise-level scenarios but can also solve personal daily problems through simplified design. By focusing on the three principles of "local", "lightweight", and "practical", even without complex external tool integration, a practical AI Agent application can be built. 
### ! Only the first 500 characters of each document are processed in the code. You can modify {text[:500]} to change the length of the characters of the processed file content.
