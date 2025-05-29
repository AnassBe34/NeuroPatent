import fitz  
import os
import re

def remove_figure_pages(pdf_path: str, min_words_threshold: int = 100) :
    try:
        # Vérifier si le fichier existe
        if not os.path.exists(pdf_path):
            return ""
        
        # Ouvrir le PDF
        doc = fitz.open(pdf_path)
        output_doc = fitz.open()
        
        # Parcourir chaque page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            word_count = len(re.findall(r'\b\w+\b', text))
            
            # Conserver la page si elle a suffisamment de mots
            if word_count >= min_words_threshold:
                output_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
        # Vérifier si des pages ont été conservées
        if len(output_doc) == 0:
            doc.close()
            output_doc.close()
            return ""
        
        # Créer le chemin de sortie
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join('', f"{base_name}_no_figures.pdf")
        
        # Sauvegarder le PDF modifié
        output_doc.save('clean_pdf.pdf')
        output_doc.close()
        doc.close()
        return output_path
    
    except Exception:
        return ""
    
remove_figure_pages(pdf_path = 'clean_pdf.pdf')