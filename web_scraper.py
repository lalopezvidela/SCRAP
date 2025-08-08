import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_page(self, url):
        """Obtiene el contenido HTML de una página"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error al obtener la página {url}: {e}")
            return None
    
    def extract_headings(self, soup):
        """Extrae todas las etiquetas h1-h6"""
        headings = []
        for level in range(1, 7):
            tags = soup.find_all(f'h{level}')
            for tag in tags:
                headings.append({
                    'level': level,
                    'tag': f'h{level}',
                    'text': tag.get_text(strip=True),
                    'attributes': dict(tag.attrs) if tag.attrs else {}
                })
        return headings
    
    def extract_paragraphs(self, soup):
        """Extrae todas las etiquetas p"""
        paragraphs = []
        p_tags = soup.find_all('p')
        for tag in p_tags:
            text = tag.get_text(strip=True)
            if text:  # Solo incluir párrafos con contenido
                paragraphs.append({
                    'text': text,
                    'attributes': dict(tag.attrs) if tag.attrs else {}
                })
        return paragraphs
    
    def extract_tables(self, soup):
        """Extrae todas las etiquetas table con su contenido"""
        tables = []
        table_tags = soup.find_all('table')
        
        for table in table_tags:
            table_data = {
                'attributes': dict(table.attrs) if table.attrs else {},
                'headers': [],
                'rows': []
            }
            
            # Extraer encabezados
            headers = table.find_all('th')
            if headers:
                table_data['headers'] = [th.get_text(strip=True) for th in headers]
            
            # Extraer filas
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    table_data['rows'].append(row_data)
            
            tables.append(table_data)
        
        return tables
    
    def scrape_page(self, url):
        """Realiza el scraping completo de una página"""
        soup = self.get_page(url)
        if not soup:
            return None
        
        data = {
            'url': url,
            'title': soup.title.string if soup.title else '',
            'headings': self.extract_headings(soup),
            'paragraphs': self.extract_paragraphs(soup),
            'tables': self.extract_tables(soup)
        }
        
        return data
    
    def save_data(self, data, filename='scraped_data.json'):
        """Guarda los datos en un archivo JSON"""
        # Asegura que el archivo termine en .json
        if not filename.lower().endswith('.json'):
            filename += '.json'
        filepath = f"c:\\Users\\lulop\\OneDrive\\Escritorio\\scrap_python\\{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Datos guardados en: {filepath}")

# Ejemplo de uso
if __name__ == "__main__":
    # Cambia esta URL por la que quieras scrapear
    url = "https://quotes.tos.com/"
    
    scraper = WebScraper(url)
    data = scraper.scrape_page(url)
    
    if data:
        print(f"Título: {data['title']}")
        print(f"Encabezados encontrados: {len(data['headings'])}")
        print(f"Párrafos encontrados: {len(data['paragraphs'])}")
        print(f"Tablas encontradas: {len(data['tables'])}")
        
        # Guardar datos
        scraper.save_data(data)
        
        # Mostrar algunos resultados
        print("\n--- Primeros 3 encabezados ---")
        for heading in data['headings'][:3]:
            print(f"{heading['tag']}: {heading['text']}")
        
        # Mostrar algunos párrafos
        print("\n--- Primeros 3 párrafos ---")
        for i, para in enumerate(data['paragraphs'][:3], 1):
            print(f"{i}. {para['text'][:100]}...")
