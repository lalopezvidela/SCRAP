from web_scraper import WebScraper

def main():
    # URLs de ejemplo para probar
    urls = [
        "https://httpbin.org/html",
        "https://quotes.toscrape.com/",
        # Agrega más URLs aquí
    ]
    
    for url in urls:
        print(f"\n=== Scrapeando: {url} ===")
        scraper = WebScraper(url)
        data = scraper.scrape_page(url)
        
        if data:
            # Crear nombre de archivo único
            filename = f"data_{url.replace('https://', '').replace('/', '_')}.json"
            scraper.save_data(data, filename)
            
            # Mostrar resumen
            print(f"✓ Datos extraídos:")
            print(f"  - {len(data['headings'])} encabezados")
            print(f"  - {len(data['paragraphs'])} párrafos") 
            print(f"  - {len(data['tables'])} tablas")
        else:
            print("✗ Error al obtener datos")

if __name__ == "__main__":
    main()
