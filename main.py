import os
import json
import uuid
from datetime import datetime
from agents.knowledge_agents import (
    MemoryManager, DocumentParserAgent,
    ContentClassifierAgent, RelationExtractorAgent
)


def init_folders():
    os.makedirs("input_docs", exist_ok=True)
    os.makedirs("output_kb", exist_ok=True)


def process_documents():
    memory = MemoryManager()
    parser = DocumentParserAgent()
    classifier = ContentClassifierAgent(memory)
    extractor = RelationExtractorAgent()

    kb_path = "output_kb/knowledge_base.json"
    if os.path.exists(kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)
    else:
        knowledge_base = {"documents": [], "user_preferences": memory.data["user_preferences"]}

    input_dir = "input_docs"
    doc_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    if not doc_files:
        print("No documents found in input_docs folder. Please add documents and try again.")
        return

    for filename in doc_files:
        if any(doc["filename"] == filename for doc in knowledge_base["documents"]):
            print(f"Document {filename} has already been processed, skipping")
            continue

        print(f"Starting processing: {filename}")
        file_path = os.path.join(input_dir, filename)

        try:
            text = parser.parse(file_path)
            print(f"Parsing completed, text length: {len(text)} characters")
        except Exception as e:
            print(f"Parsing failed: {e}, skipping this document")
            continue

        category = classifier.classify(text, filename)

        max_retries = 3
        retry_count = 0
        need_retry = True

        while need_retry and retry_count < max_retries:
            if retry_count == 0:
                extracted = extractor.extract(text, knowledge_base["documents"])
            else:
                print(f"Retrying extraction for the {retry_count}th time...")
                extracted = extractor.extract(text, knowledge_base["documents"])

            print(f"Extraction completed, number of core ideas: {len(extracted['core_ideas'])}")

            is_category_invalid = (category['level1'] == "Unclassified" or
                                   category['level2'] == "Unclassified" or
                                   category['level3'] == "Unclassified")

            has_invalid_core_ideas = len(extracted['core_ideas']) == 1 and "No core ideas extracted" in \
                                     extracted['core_ideas'][0]
            has_invalid_keywords = len(extracted['keywords']) == 1 and "No keywords extracted" in extracted['keywords'][0]

            need_retry = is_category_invalid or has_invalid_core_ideas or has_invalid_keywords

            if need_retry:
                retry_count += 1
                print(f"Retry required, reasons:")
                if is_category_invalid:
                    print(f"- Incomplete classification: {category}")
                if has_invalid_core_ideas:
                    print(f"- No core ideas extracted")
                if has_invalid_keywords:
                    print(f"- No keywords extracted")
            else:
                print(f"Information extraction is complete, no retry needed")

        if retry_count > 0:
            print(f"Total retries: {retry_count}")

        print(f"Classification result: {category['level1']}→{category['level2']}→{category['level3']}")
        print()

        doc_id = f"doc_{str(uuid.uuid4())[:8]}"  # Generate short ID
        knowledge_base["documents"].append({
            "id": doc_id,
            "filename": filename,
            "path": file_path,
            "category": category,
            "core_ideas": extracted["core_ideas"],
            "keywords": extracted["keywords"],
            "related_docs": extracted["related_docs"],
            "processed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        memory.update_session(filename)

    with open(kb_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    print(f"All documents processed, knowledge base saved to {kb_path}")


def search_knowledge(query_type, query_value):
    """
    Search knowledge base
    query_type: "category", "keyword", "related" (by related document ID)
    query_value: Value to search for
    """
    kb_path = "output_kb/knowledge_base.json"
    if not os.path.exists(kb_path):
        return "Knowledge base does not exist, please process documents first"

    with open(kb_path, "r", encoding="utf-8") as f:
        knowledge_base = json.load(f)

    results = []
    for doc in knowledge_base["documents"]:
        if query_type == "category":
            if (query_value in doc["category"]["level1"] or
                    query_value in doc["category"]["level2"] or
                    query_value in doc["category"]["level3"]):
                results.append(doc)
        elif query_type == "keyword":
            skip = False
            for core_ideas in doc["core_ideas"]:
                if query_value in core_ideas:
                    results.append(doc)
                    skip = True
                    break
            for keyword in doc["keywords"]:
                if query_value in keyword and skip is False:
                    results.append(doc)
                    break
        elif query_type == "related":
            if query_value in doc["related_docs"]:
                results.append(doc)
        else:
            return "Unsupported search type. Please use: category, keyword, related"

    if not results:
        return "No matching documents found"

    output = f"Found {len(results)} matching results:\n"
    for i, doc in enumerate(results, 1):
        output += f"{i}. Filename: {doc['filename']}\n"
        output += f"   Category: {doc['category']['level1']}→{doc['category']['level2']}→{doc['category']['level3']}\n"
        output += f"   Core Ideas: {doc['core_ideas'][0]} (and {len(doc['core_ideas'])} more)\n"
        output += f"   Path: {doc['path']}\n\n"
    return output


def reclassify_document(filename, knowledge_base):
    doc_index = -1
    for i, doc in enumerate(knowledge_base["documents"]):
        if doc["filename"] == filename:
            doc_index = i
            break

    if doc_index == -1:
        return False, f"Error: File '{filename}' not found in knowledge base"

    doc = knowledge_base["documents"][doc_index]
    file_path = doc["path"]

    parser = DocumentParserAgent()
    try:
        text = parser.parse(file_path)
        print(f"Document re-parsed successfully, text length: {len(text)} characters")
    except Exception as e:
        return False, f"Parsing failed: {e}"

    memory = MemoryManager()
    classifier = ContentClassifierAgent(memory)
    new_category = classifier.classify(text, filename)

    knowledge_base["documents"][doc_index]["category"] = new_category
    knowledge_base["documents"][doc_index]["processed_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    kb_path = "output_kb/knowledge_base.json"
    with open(kb_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)

    return True, new_category

if __name__ == "__main__":
    init_folders()
    process_documents()

    print("\n===== Knowledge Base Search System =====")
    print("Welcome to the Knowledge Base Search System!")

    while True:
        try:
            print("\nPlease select search type:")
            print("1. Search by Category")
            print("2. Search by Keyword")
            print("3. Search by Related Document ID")
            print("4. Reclassify/Organize Document")
            print("5. Exit System")

            choice = input("Please enter option number (1-5): ").strip()

            if choice == "1":
                query_type = "category"
                query_value = input("Please enter category keyword to search: ").strip()
                if not query_value:
                    print("Error: Category keyword cannot be empty!")
                    continue
                print(f"\nSearching for '{query_value}' in {query_type}...")
                result = search_knowledge(query_type, query_value)
                print("\n" + result)
            elif choice == "2":
                query_type = "keyword"
                query_value = input("Please enter keyword to search: ").strip()
                if not query_value:
                    print("Error: Keyword cannot be empty!")
                    continue
                print(f"\nSearching for '{query_value}' in {query_type}...")
                result = search_knowledge(query_type, query_value)
                print("\n" + result)
            elif choice == "3":
                query_type = "related"
                query_value = input("Please enter related document ID: ").strip()
                if not query_value:
                    print("Error: Document ID cannot be empty!")
                    continue
                print(f"\nSearching for '{query_value}' in {query_type}...")
                result = search_knowledge(query_type, query_value)
                print("\n" + result)
            elif choice == "4":
                kb_path = "output_kb/knowledge_base.json"
                if not os.path.exists(kb_path):
                    print("Knowledge base does not exist, please process documents first")
                    continue

                with open(kb_path, "r", encoding="utf-8") as f:
                    knowledge_base = json.load(f)

                if not knowledge_base["documents"]:
                    print("No processed documents in knowledge base")
                    continue

                print("\nList of processed documents:")
                for i, doc in enumerate(knowledge_base["documents"], 1):
                    print(
                        f"{i}. {doc['filename']} (Current category: {doc['category']['level1']}→{doc['category']['level2']}→{doc['category']['level3']})")

                filename = input("\nPlease enter the filename to reclassify: ").strip()
                if not filename:
                    print("Error: Filename cannot be empty!")
                    continue

                print(f"\nReclassifying document '{filename}'...")
                success, result = reclassify_document(filename, knowledge_base)

                if success:
                    new_category = result
                    print(f"\nReclassification successful!")
                    print(f"New category path: {new_category['level1']}→{new_category['level2']}→{new_category['level3']}")
                    print(f"Knowledge base has been updated")
                else:
                    print(f"\n{result}")
            elif choice == "5":
                print("\nThank you for using the Knowledge Base Search System, goodbye!")
                break
            else:
                print("Error: Invalid option, please try again!")
                continue

            continue_query = input("\nWould you like to continue? (y/n): ").strip().lower()
            if continue_query != 'y':
                print("\nThank you for using the Knowledge Base Search System, goodbye!")
                break
        except KeyboardInterrupt:
            print("\nProgram interrupted by user, exiting...")
            break