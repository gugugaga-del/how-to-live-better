import requests
import os
import glob

PAT = os.environ["COZE_PAT"]
KNOWLEDGE_ID = os.environ["COZE_KNOWLEDGE_ID"]
BASE_URL = "https://api.coze.cn/open_api/v1"
HEADERS = {"Authorization": f"Bearer {PAT}", "Content-Type": "application/json"}

def list_all_docs():
    docs = []
    page = 1
    while True:
        res = requests.post(f"{BASE_URL}/knowledge/document/list", json={
            "knowledge_id": KNOWLEDGE_ID,
            "page": page,
            "page_size": 100
        }, headers=HEADERS)
        data = res.json()
        if data.get("code") !=0:
            print("列出文档失败",data)
            break
        items = data["data"]["documents"]
        if len(items)==0:
            break
        docs.extend(items)
        page +=1
    return docs

def delete_doc(doc_id):
    res = requests.post(f"{BASE_URL}/knowledge/document/delete",json={
        "knowledge_id":KNOWLEDGE_ID,
        "document_id":doc_id
    },headers=HEADERS)
    print("删除",doc_id,res.json())

def upload_doc(file_name,text):
    res = requests.post(f"{BASE_URL}/knowledge/document/create",json={
        "knowledge_id":KNOWLEDGE_ID,
        "document_name":file_name,
        "source_type":3,
        "text":text
    },headers=HEADERS)
    print("上传",file_name,res.json())

if __name__ == "__main__":
    old_docs = list_all_docs()
    for d in old_docs:
        delete_doc(d["document_id"])

    md_files = glob.glob("**/*.md",recursive=True)
    for fpath in md_files:
        try:
            with open(fpath,"r",encoding="utf-8") as f:
                content = f.read()
            upload_doc(fpath,content)
        except Exception as e:
            print(f"读取失败{fpath}",e)
