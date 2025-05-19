import re
import html
import json
from bs4 import BeautifulSoup

def parse_linkedin_code_tags(html_file_path):
    # 1. HTML-Datei einlesen
    with open(html_file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 2. Alle <code>-Tags mit style="display: none" und id="bpr-guid-<Zahl>" finden
    code_tags = soup.find_all(
        'code',
        {
            'style': 'display: none',
            'id': re.compile(r'^bpr-guid-\d+$')
        }
    )

    if not code_tags:
        raise RuntimeError("Keine <code>-Tags mit passender ID gefunden!")

    results = []

    for code in code_tags:
        # 3. Roh-Text extrahieren und HTML-Entities dekodieren
        raw = code.get_text().strip()
        decoded = html.unescape(raw)

        # 4a. Newlines entfernen
        single_line = decoded.replace('\r', '').replace('\n', '')

        # 4b. Unzulässige Steuerzeichen rausfiltern
        cleaned = ''.join(ch for ch in single_line if ord(ch) >= 32 or ch in '\t')

        # 4c. Trailing‐Commas in Objekten/Arrays entfernen
        cleaned = re.sub(r',(?=\s*[\]}])', '', cleaned)

        # 5. JSON parsen (strict=False toleriert unescaped Control-Chars)
        try:
            obj = json.loads(cleaned, strict=False)
        except json.JSONDecodeError:
            # Fallback: nochmal ohne alle Steuerzeichen außer \r\n\t
            filtered = ''.join(ch for ch in single_line if ch in '\r\n\t' or ord(ch) >= 32)
            filtered = re.sub(r',(?=\s*[\]}])', '', filtered)
            obj = json.loads(filtered, strict=False)

        results.append(obj)

    return results

if __name__ == '__main__':
    all_data = parse_linkedin_code_tags('meow.html')
    with open("./test.json", "w") as outfile:
        outfile.write(json.dumps(all_data, indent=2))
