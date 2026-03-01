import os
import zipfile
import xml.etree.ElementTree as ET

def read_docx(path):
    try:
        with zipfile.ZipFile(path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.XML(xml_content)
            NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            text = []
            for paragraph in tree.iter(NAMESPACE + 'p'):
                texts = [node.text for node in paragraph.iter(NAMESPACE + 't') if node.text]
                if texts: text.append(''.join(texts))
            return '\n'.join(text)
    except Exception as e:
        return str(e)

with open('output.txt', 'w', encoding='utf-8') as out:
    base_dir = r"d:\PycharmProjects\task5"
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.docx') and not f.startswith('~$'):
                path = os.path.join(root, f)
                out.write("====================================\n")
                out.write(f"ФАЙЛ: {path}\n")
                out.write(read_docx(path) + "\n")
