#conda install -c conda-forge poppler
import pdf2image #1.17.0
import pytesseract
import tempfile
import ollama
from tqdm import tqdm
import chromadb

def keyword_generator(p, top=3):
    prompt = "summarize the following paragraph in 3 keywords separated by ,: "+p
    res = ollama.generate(model="llama3", prompt=prompt)["response"]
    return res.replace("\n"," ").strip()

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

with tempfile.TemporaryDirectory() as path:
    doc_img = pdf2image.convert_from_path("pdf_data\Detection_and_Mitigation_of_Label-Flipping_Attacks_in_Federated_Learning_Systems_with_KPCA_and_K-Means.pdf", dpi=300,poppler_path=r'D:\Release-24.02.0-0\poppler-24.02.0\Library\bin')

    # print one page as example
    
    doc_txt = []
    for page in doc_img:
        text = pytesseract.image_to_string(page)
        doc_txt.append(text)
   
    title_map = {
    "1-1":"I. INTRODUCTION",
    "1-2":"II. RELATED STUDIES",
    "2-2":"III. PRELIMINARIES",
    "2-5":"IV.ANALYSIS OF DEFENSE STRATEGIES AGAINST LABELFLIPPING ATTACKS IN FL",
    "5-8":"V. RESULTS COMPARISON AND ANALYSIS",
    "8-8":"VI.CONCLUSION AND FUTURE DIRECTION",
    "8-9":"REFERENCE",
    }

    lst_docs, lst_ids, lst_metadata = [], [], []
    for n,page in enumerate(doc_txt):
        try:
            ## get title
            title = [v for k,v in title_map.items() 
                     if n in range(int(k.split("-")[0]), 
                                   int(k.split("-")[1])+1)][0]
            ## clean page
            page = page.replace("Table of Contents","")
            ## get paragraph
            for i,p in enumerate(page.split('\n\n')):
                if len(p.strip())>5:  ##<--clean paragraph
                    lst_docs.append(p.strip())
                    lst_ids.append(str(n)+"_"+str(i))
                    lst_metadata.append({"title":title})
        except:
            continue
    
    for i,doc in tqdm(enumerate(lst_docs)):
        lst_metadata[i]["keywords"] = keyword_generator(doc)

    ## print example
    for id,doc,meta in zip(lst_ids[75:78], 
                           lst_docs[75:78], 
                           lst_metadata[75:78]):
        print(id, "-", meta, "\n", doc, "\n")
