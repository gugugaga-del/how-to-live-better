import os
import requests

TOKEN = os.environ["COZE_TOKEN"]
KB_ID = os.environ["COZE_KNOWLEDGE_ID"]
BASE_URL = "https://api.coze.cn/open_api/v2"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
DOC_ROOT = "./docs"
CHUNK_SIZE = 700  # 切片长度，推荐700字

def split_text(text, chunk_size):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end
    return chunks

def get_exist_docs():
    page = 1
    all_docs = {}
    while True:
        resp = requests.get(f"{BASE_URL}/knowledge/{KB_ID}/documents?page={page}&size=100", headers=HEADERS)
        data = resp.json()
        items = data.get("data", [])
        if not items:
            break
        for item in items:
            all_docs[item["name"]] = item["document_id"]
        page += 1
    return all_docs

def upload_doc(file_name, content):
    payload = {
        "knowledge_id": KB_ID,
        "document_name": file_name,
        "content": content,
        "update_rule": {"update_type":0}
    }
    res = requests.post(f"{BASE_URL}/knowledge/document/create", headers=HEADERS, json=payload)
    print(f"上传 {file_name} 状态码: {res.status_code}")

def update_doc(doc_id, content):
    payload = {"document_id": doc_id, "content": content}
    res = requests.post(f"{BASE_URL}/knowledge/document/update", headers=HEADERS, json=payload)
    print(f"更新 {doc_id} 状态码: {res.status_code}")

def delete_doc(doc_id):
    res = requests.post(f"{BASE_URL}/knowledge/document/delete", headers=HEADERS, json={"document_id": doc_id})
    print(f"删除 {doc_id} 状态码: {res.status_code}")

def main():
    exist_docs = get_exist_docs()
    local_md = {}
    for root, _, files in os.walk(DOC_ROOT):
        for fname in files:
            if fname.endswith(".md"):
                full_path = os.path.join(root, fname)
                with open(full_path, "r", encoding="utf-8") as f:
                    text = f.read()
                # 文本分片，单个md拆成多个part文档
                chunks = split_text(text, CHUNK_SIZE)
                for idx, chunk in enumerate(chunks):
                    chunk_name = f"{fname}_part{idx+1}"
                    local_md[chunk_name] = chunk

    # 新增/更新文档
    for name, content in local_md.items():
        if name in exist_docs:
            update_doc(exist_docs[name], content)
        else:
            upload_doc(name, content)
    # 删除仓库已移除的旧分片文档
    for name, docid in exist_docs.items():
        if name not in local_md:
            delete_doc(docid)

if __name__ == "__main__":
    main()
