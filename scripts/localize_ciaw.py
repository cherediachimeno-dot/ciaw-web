#!/usr/bin/env python3
"""Build full Catalan and Spanish CIAW websites from exact English HTML sources.

Source of truth: English pages. Every section, asset and script is retained.
Human-authored translations are stored in locales/translations.json.
Run: python scripts/localize_ciaw.py
"""
import json
import re
from pathlib import Path
from html import unescape
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = json.loads((ROOT / 'locales/translations.json').read_text('utf-8'))
PAGE_NAMES = {
    'index.html': {'es': 'es.html', 'ca': 'ca.html'},
    'game-studies.html': {'es': 'game-studies-es.html', 'ca': 'game-studies-ca.html'},
    'research.html': {'es': 'research-es.html', 'ca': 'research-ca.html'},
    'resources.html': {'es': 'resources-es.html', 'ca': 'resources-ca.html'},
    'privacy.html': {'es': 'privacy-es.html', 'ca': 'privacy-ca.html'},
}
TITLES = {
    'index.html': ('CIAW | Center for Innovation in Ancient Worlds', 'CIAW | Center for Innovation in Ancient Worlds'),
    'game-studies.html': ('Game Studies y Antigüedad | CIAW', 'Game Studies i Antiguitat | CIAW'),
    'research.html': ('Investigación y publicaciones | CIAW', 'Recerca i publicacions | CIAW'),
    'resources.html': ('Recursos docentes | CIAW', 'Recursos docents | CIAW'),
    'privacy.html': ('Privacidad e información sobre la web | CIAW', 'Privacitat i informació sobre el web | CIAW'),
}
DESCRIPTIONS = {
    'index.html': (
        'CIAW es una iniciativa académica independiente con sede en Cataluña que impulsa la investigación sobre la Antigüedad, las publicaciones de acceso abierto, los Game Studies y la docencia inclusiva.',
        'El CIAW és una iniciativa acadèmica independent amb seu a Catalunya que impulsa la recerca sobre l’Antiguitat, les publicacions en accés obert, els Game Studies i la docència inclusiva.',
    ),
    'game-studies.html': (
        'Cómo estudia CIAW la representación del pasado en los videojuegos: autoridad histórica, simulación, recepción clásica y memoria cultural.',
        'Com estudia el CIAW la representació del passat en els videojocs: autoritat històrica, simulació, recepció clàssica i memòria cultural.',
    ),
    'research.html': (
        'Investigaciones, publicaciones y proyectos docentes vinculados a CIAW y sus colaboradores.',
        'Recerques, publicacions i projectes docents vinculats al CIAW i als seus col·laboradors.',
    ),
    'resources.html': (
        'Infografías docentes abiertas de CIAW sobre enseñanza inclusiva, Historia Antigua y alfabetización crítica en IA.',
        'Infografies docents obertes del CIAW sobre docència inclusiva, Història Antiga i alfabetització crítica en IA.',
    ),
    'privacy.html': (
        'Información sobre privacidad, servicios externos y contacto en la web de CIAW.',
        'Informació sobre privacitat, serveis externs i contacte al web del CIAW.',
    ),
}
ALT = {
    'en': {},
    'es': {
        'Open navigation menu': 'Abrir el menú de navegación',
        'Close navigation menu': 'Cerrar el menú de navegación',
        'Main navigation': 'Navegación principal',
        'On this page': 'En esta página',
        'CIAW — Back to top': 'CIAW — Volver arriba',
        'CIAW home': 'Inicio de CIAW',
        'A preview of CIAW\'s inclusive teaching infographics': 'Vista previa de las infografías docentes inclusivas de CIAW',
        'Explore CIAW teaching resources': 'Explorar los recursos docentes de CIAW',
        'Explore CIAW\'s Game Studies research area': 'Explorar la línea de Game Studies de CIAW',
        'Panoramic Playing Antiquity artwork featuring historical and fantasy game worlds': 'Ilustración panorámica de Playing Antiquity con mundos de videojuegos históricos y fantásticos',
        'Original artwork by Arturo Galindo García: an ancient-style helmet made from contrasting golden, pale pink and blue sections, against delicate circular geometric patterns': 'Ilustración original de Arturo Galindo García: casco de inspiración antigua formado por secciones doradas, rosas y azules sobre motivos geométricos',
        'See the original illustration in AI & Antiquity': 'Ver la ilustración original en AI & Antiquity',
        'Open the original seminar poster': 'Abrir el cartel original de las jornadas',
        'Poster for the 24 November 2026 seminar on Antiquity, the far right and social networks': 'Cartel de las jornadas del 24 de noviembre de 2026 sobre Antigüedad, extrema derecha y redes sociales',
        'Read AI & Antiquity volume 2 issue 2': 'Leer AI & Antiquity, volumen 2, número 2',
        'Events & Resources': 'Actividades y recursos',
        'Language': 'Idioma',
        'English version': 'Versión inglesa',
        'Areas of work': 'Ámbitos de trabajo',
        'Three key areas': 'Tres áreas principales',
        'Journal publication details': 'Información de la revista',
        'Explore CIAW\'s neurodiversity and inclusive teaching work': 'Explorar el trabajo de CIAW sobre neurodiversidad y docencia inclusiva',
        'Cover of AI & Antiquity, Volume 2, Issue 2 (2026), showing a stylised ancient helmet composition': 'Cubierta de AI & Antiquity, volumen 2, número 2 (2026), con una composición de casco de inspiración antigua',
        'Artwork by Arturo Galindo García: an ancient-style helmet made from contrasting golden, pale pink and blue sections, against delicate circular geometric patterns': 'Ilustración de Arturo Galindo García: casco de inspiración antigua con elementos dorados, rosas y azules sobre motivos geométricos circulares',
        'Playing Antiquity panoramic composition evoking historical and fantasy strategy and role-playing video games': 'Panorama de Playing Antiquity con referencias a videojuegos históricos y fantásticos de estrategia y rol',
        'Playing Antiquity confirmed publication information': 'Datos editoriales de Playing Antiquity',
        'Academic collaboration': 'Colaboración académica',
        'Teaching infographic about flipped learning and AI-supported classroom practice': 'Infografía docente sobre aula invertida y prácticas de clase apoyadas en IA',
        'Teaching infographic about overlooked historical experiences and cognitive diversity': 'Infografía docente sobre experiencias históricas marginadas y diversidad cognitiva',
        'Teaching infographic on verifying AI-generated historical information': 'Infografía docente sobre la verificación de información histórica generada por IA',

    },
    'ca': {
        'Open navigation menu': 'Obrir el menú de navegació',
        'Close navigation menu': 'Tancar el menú de navegació',
        'Main navigation': 'Navegació principal',
        'On this page': 'En aquesta pàgina',
        'CIAW — Back to top': 'CIAW — Tornar a dalt',
        'CIAW home': 'Inici del CIAW',
        'A preview of CIAW\'s inclusive teaching infographics': 'Vista prèvia de les infografies docents inclusives del CIAW',
        'Explore CIAW teaching resources': 'Explorar els recursos docents del CIAW',
        'Explore CIAW\'s Game Studies research area': 'Explorar la línia de Game Studies del CIAW',
        'Panoramic Playing Antiquity artwork featuring historical and fantasy game worlds': 'Il·lustració panoràmica de Playing Antiquity amb mons de videojocs històrics i fantàstics',
        'Original artwork by Arturo Galindo García: an ancient-style helmet made from contrasting golden, pale pink and blue sections, against delicate circular geometric patterns': 'Il·lustració original d’Arturo Galindo García: casc d’inspiració antiga format per seccions daurades, roses i blaves sobre motius geomètrics',
        'See the original illustration in AI & Antiquity': 'Consulta la il·lustració original a AI & Antiquity',
        'Open the original seminar poster': 'Obrir el cartell original de les jornades',
        'Poster for the 24 November 2026 seminar on Antiquity, the far right and social networks': 'Cartell de les jornades del 24 de novembre de 2026 sobre Antiguitat, extrema dreta i xarxes socials',
        'Read AI & Antiquity volume 2 issue 2': 'Llegir AI & Antiquity, volum 2, número 2',
        'Events & Resources': 'Activitats i recursos',
        'Language': 'Llengua',
        'English version': 'Versió anglesa',
        'Areas of work': 'Àmbits de treball',
        'Three key areas': 'Tres àrees principals',
        'Journal publication details': 'Informació de la revista',
        'Explore CIAW\'s neurodiversity and inclusive teaching work': 'Consultar els treballs del CIAW sobre neurodiversitat i docència inclusiva',
        'Cover of AI & Antiquity, Volume 2, Issue 2 (2026), showing a stylised ancient helmet composition': 'Coberta d’AI & Antiquity, volum 2, número 2 (2026), amb una composició de casc d’inspiració antiga',
        'Artwork by Arturo Galindo García: an ancient-style helmet made from contrasting golden, pale pink and blue sections, against delicate circular geometric patterns': 'Il·lustració d’Arturo Galindo García: casc d’inspiració antiga amb elements daurats, rosats i blaus sobre motius geomètrics circulars',
        'Playing Antiquity panoramic composition evoking historical and fantasy strategy and role-playing video games': 'Panorama de Playing Antiquity amb referències a videojocs històrics i fantàstics d’estratègia i rol',
        'Playing Antiquity confirmed publication information': 'Dades editorials de Playing Antiquity',
        'Academic collaboration': 'Col·laboració acadèmica',
        'Teaching infographic about flipped learning and AI-supported classroom practice': 'Infografia docent sobre aula invertida i pràctiques docents amb suport d’IA',
        'Teaching infographic about overlooked historical experiences and cognitive diversity': 'Infografia docent sobre experiències històriques marginades i diversitat cognitiva',
        'Teaching infographic on verifying AI-generated historical information': 'Infografia docent sobre la verificació d’informació històrica generada per IA',

    },
}
BLOB = {}
SCRIPT_STYLE = re.compile(r'(<(?:script|style|title)\b[^>]*>)(.*?)(</(?:script|style|title)>)', re.I | re.S)
TEXT_NODE = re.compile(r'(?<=>)([^<>]+)(?=<)')
TRANSLATABLE_ATTRIBUTE = re.compile(r'(\s(?:alt|aria-label|title|placeholder)=)(["\'])(.*?)\2', re.I | re.S)
PRESERVED = {
    'AI &amp; Antiquity', 'Game Studies', 'EN', 'CA', 'ES', '☰', 'EN ·', 'Català', '·',
    'Center for Innovation in', 'Ancient Worlds', 'The Center for Innovation in Ancient Worlds (CIAW)',
    'Playing Antiquity', '↗', '↘', 'Antiguitat, extrema dreta i xarxes socials',
    'L’Antiguitat al món actual II · UAB, 10.30–13.15 h',
    'ISSN 3081-4553', '01', '02', '03', '04', '24', '06', '2026', '⌄',
    'Arturo Galindo García', '(2026) ·', 'Same Standards, Different Pathways',
    'Isaías Arrayás Morales &amp; Carlos Heredia Chimeno ·',
    'Isaías Arrayás Morales &amp; Carlos Heredia Chimeno,',
    'Carlos Heredia Chimeno,',
    'Forgotten Voices in Antiquity', 'Universitat Autònoma de Barcelona (UAB)',
    'Universidad Europea de Madrid', 'CH', 'IA', 'SS', 'M', 'Montserrat Catà Lladó', 'Miquel Andraca Vilar', 'Research Associate', 'Sílvia Swan',
    'Carlos Heredia Chimeno', 'Isaías Arrayás Morales', 'ORCID ↗',
    '24 November 2026 · 10.30–13.15 h',
    'Sala de Graus · Facultat de Filosofia i Lletres (UAB)', 'UOC · UAB · CIAW',
    '10.30–10.45', '10.45–11.25', '11.25–12.05', '12.05–12.45', '12.45–13.15',
    'Presentació de les jornades', 'Carlos Heredia i Marc Mendoza (UAB)',
    'De Roma al', 'feed', ': com l’extrema dreta resignifica l’Antiguitat a les xarxes socials',
    'Laura Pérez Altabe (UPF)', 'Apropiaciones de la Antigüedad en el contexto actual de auge de las ultraderechas y de la IA generativa',
    'Oskar Aguado (EHU)', 'Iosephus Maria ad portas',
    ': l’extrema dreta catalana més enllà d’Ítaca', 'Marc Mendoza (UAB)', 'Debat final',
    'Journal of Classics Teaching', 'Archeion', 'ciaw.es', 'carlos.heredia@uab.cat',
    '.', ').', 'View original ↗', '© CIAW · Independent academic initiative based in Catalonia, Spain',
    'AI &amp; Antiquity →', 'Playing Antiquity ↓',
    'Video Games, Teaching and Historical Knowledge.',
    'Visit the journal ↗', 'Issue archive ↗',
    'Centre for Innovation in Ancient Worlds',
    'CIAW | Center for Innovation in Ancient Worlds',
    'CIAW · Center for Innovation in Ancient Worlds',
}
# A final small set of UI translations that also occurs in child pages.
SUPPLEMENT = {
    'es': {
        'Visit the journal ↗': 'Visitar la revista ↗',
        'Issue archive ↗': 'Archivo de números ↗',
        'Video Games, Teaching and Historical Knowledge.': 'Videojuegos, docencia y conocimiento histórico.',
        'Debat final': 'Debate final',
        'Playing Antiquity ↓': 'Playing Antiquity ↓',
        '← Return to CIAW': '← Volver a CIAW',
    },
    'ca': {
        'Visit the journal ↗': 'Visitar la revista ↗',
        'Issue archive ↗': 'Arxiu de números ↗',
        'Video Games, Teaching and Historical Knowledge.': 'Videojocs, docència i coneixement històric.',
        'Debat final': 'Debat final',
        'Playing Antiquity ↓': 'Playing Antiquity ↓',
        '← Return to CIAW': '← Tornar al CIAW',
    },
}


def full_dictionary(lang):
    return {**TRANSLATIONS[lang], **SUPPLEMENT[lang]}


def translate_body(source: str, translations: dict) -> tuple[str, list[str]]:
    placeholders = []
    def protect(match):
        token = f'__CIAW_SCRIPT_STYLE_{len(placeholders)}__'
        placeholders.append(match.group(2))
        return match.group(1) + token + match.group(3)
    html = SCRIPT_STYLE.sub(protect, source)
    missing = set()
    def translate_node(match):
        string = match.group(1)
        before = string[:len(string) - len(string.lstrip())]
        after = string[len(string.rstrip()):]
        content = string.strip()
        if not content or content.startswith('__CIAW_SCRIPT_STYLE_'):
            return match.group(0)
        key = re.sub(r'\s+', ' ', content)
        value = translations.get(key)
        if value is None:
            if key not in PRESERVED and not key.isnumeric():
                missing.add(key)
            return match.group(0)
        return before + value + after
    html = TEXT_NODE.sub(translate_node, html)
    for i, blob in enumerate(placeholders):
        html = html.replace(f'__CIAW_SCRIPT_STYLE_{i}__', blob)
    return html, sorted(missing)


def replace_local_links(html, lang, page):
    """Preserve the equivalent target page when switching languages."""
    for src, destinations in PAGE_NAMES.items():
        html = html.replace('href="' + src + '"', 'href="' + destinations[lang] + '"')
        html = html.replace('href="' + src + '#', 'href="' + destinations[lang] + '#')

    # The original English page often uses a static EN current-language element.
    english_target = page
    html = html.replace('<span class="current" aria-label="English version">EN</span>',
                        '<a href="' + english_target + '" lang="en">EN</a>')
    html = html.replace('<span aria-current="page">EN</span>',
                        '<a href="' + english_target + '" lang="en">EN</a>')
    html = html.replace('EN · <a href="ca.html"',
                        '<a href="' + english_target + '" lang="en">EN</a> · <a href="ca.html"')
    html = html.replace('<span>EN</span> · <a href="ca.html"',
                        '<a href="' + english_target + '" lang="en">EN</a> · <a href="ca.html"')

    # Language switching within a subject page points to the equivalent page,
    # not to the other language's homepage.
    for other in ('ca', 'es'):
        target = PAGE_NAMES[page][other]
        if target != other + '.html':
            html = html.replace('href="' + other + '.html" lang="' + other + '"',
                                'href="' + target + '" lang="' + other + '"')
    active_href = PAGE_NAMES[page][lang]
    active = '<a href="' + active_href + '" lang="' + lang + '">' + lang.upper() + '</a>'
    html = html.replace(active, '<span aria-current="page">' + lang.upper() + '</span>')
    # The older homepage mobile menu uses the full language names.
    active_mobile = '<a href="' + active_href + '" lang="' + lang + '">' + ('Català' if lang=='ca' else 'Castellano') + '</a>'
    html = html.replace(active_mobile, '<span aria-current="page">' + ('Català' if lang=='ca' else 'Castellano') + '</span>')
    return html

def translate_attributes(html, lang):
    attrs = ALT[lang]
    def sub(m):
        original = unescape(m.group(3))
        translated = attrs.get(original)
        if translated is None:
            return m.group(0)
        import html as esc
        return m.group(1) + m.group(2) + esc.escape(translated, quote=True) + m.group(2)
    return TRANSLATABLE_ATTRIBUTE.sub(sub, html)


def localize(source, page, lang):
    translations = full_dictionary(lang)
    html, missing = translate_body(source, translations)
    if missing:
        raise ValueError(f'{page} [{lang}] has {len(missing)} untranslated visible strings:\n' + '\n'.join(missing))
    if page == 'index.html':
        # Proper names remain unchanged, but doctoral titles agree with each person's gender.
        miquel_card = re.compile(r'(<h4>Miquel Andraca Vilar</h4>\\s*<p class="person-role">Research Associate</p>\\s*<p class="person-affiliation">)Doctoranda( · Universitat Autònoma de Barcelona</p>)')
        html, count = miquel_card.subn(lambda m: m.group(1) + ('Doctorando' if lang == 'es' else 'Doctorand') + m.group(2), html)
        if count != 1:
            raise AssertionError(f'Expected one Miquel Andraca Vilar associate card for {lang}; found {count}')
    html = translate_attributes(html, lang)
    if lang == 'ca':
        # Catalan elisions remain attached to an italicised or linked proper name.
        html = re.sub(r"(?<=d’)\s+(?=<(?:em|strong|a)\b)", "", html)
    html = replace_local_links(html, lang, page)
    html = html.replace('<html lang="en">', '<html lang="' + lang + '">', 1)
    # Localised metadata and discoverable alternate versions.
    html = re.sub(r'(<title>).*?(</title>)', lambda m:m.group(1) + TITLES[page][lang=='ca'] + m.group(2), html, count=1, flags=re.S)
    import html as escape_html
    desc = escape_html.escape(DESCRIPTIONS[page][lang=='ca'], quote=True)
    html = re.sub(r'(<meta name="description" content=")[^"]*("/>)', lambda m:m.group(1) + desc + m.group(2), html, count=1)
    destination = PAGE_NAMES[page][lang]
    html = re.sub(r'(<link rel="canonical" href=")[^"]*("/>)',lambda m:m.group(1)+'https://ciaw.es/'+destination+m.group(2), html,count=1)
    if page == 'index.html':
        # Homepage social URLs, otherwise the EN and ES shares duplicate.
        html = html.replace('property="og:url" content="https://ciaw.es/"',
                            'property="og:url" content="https://ciaw.es/'+destination+'"')
        html = html.replace('property="og:title" content="CIAW | Center for Innovation in Ancient Worlds"',
                            'property="og:title" content="'+TITLES[page][lang=='ca']+'"')
        html = html.replace('const seminarState=document.getElementById(\'seminar-state\');',
                            "const seminarState=document.getElementById('seminar-state');")
        html = html.replace("seminarState.textContent='PAST SEMINAR · L’ANTIGUITAT AL MÓN ACTUAL II'",
                            "seminarState.textContent='"+('SEMINARIO CELEBRADO' if lang=='es' else 'SEMINARI CELEBRAT')+" · L’ANTIGUITAT AL MÓN ACTUAL II'")
    elif page == 'game-studies.html':
        html = html.replace('property="og:url" content="https://ciaw.es/game-studies.html"',
                            'property="og:url" content="https://ciaw.es/'+destination+'"')
    # Keep translated social sharing previews consistent with the visible language.
    html = re.sub(r'(<meta property="og:description" content=")[^"]*("/>)',
                  lambda m: m.group(1)+desc+m.group(2), html, count=1)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*("/>)',
                  lambda m: m.group(1)+escape_html.escape(TITLES[page][lang=='ca'],quote=True)+m.group(2),
                  html, count=1)
    if True:
        opens, closes = ('Open navigation menu', 'Close navigation menu')
        html = html.replace("'"+opens+"'", "'"+ALT[lang][opens]+"'")
        html = html.replace("'"+closes+"'", "'"+ALT[lang][closes]+"'")
    # Hreflang for all five types of page, so translators and search engines see parity.
    en = 'https://ciaw.es/' if page=='index.html' else 'https://ciaw.es/'+page
    ca = 'https://ciaw.es/'+PAGE_NAMES[page]['ca']
    es = 'https://ciaw.es/'+PAGE_NAMES[page]['es']
    hreflang = ('\n<link rel="alternate" hreflang="en" href="'+en+'"/>'
                '\n<link rel="alternate" hreflang="ca" href="'+ca+'"/>'
                '\n<link rel="alternate" hreflang="es" href="'+es+'"/>')
    html = re.sub(r'<link rel="alternate" hreflang="(?:en|es|ca|x-default)"[^>]*>\s*', '', html)
    html = html.replace('</head>', hreflang+'\n</head>',1)
    return html


def structure_signature(html):
    # No parser rewrite: exactly the same section and image structures.
    sections = re.findall(r'<section\b[^>]*\bid="([^"]+)"', html)
    images = re.findall(r'<img\b', html)
    return sections, len(images), len(re.findall(r'<article\b',html)),len(re.findall(r'<details\b',html))


def main():
    total = 0
    for page, targets in PAGE_NAMES.items():
        source = (ROOT / page).read_text('utf-8')
        sig = structure_signature(source)
        for lang, dest in targets.items():
            html = localize(source, page, lang)
            parity = structure_signature(html)
            if sig != parity:
                raise AssertionError(f'Structure mismatch {page} → {dest}: {sig} vs {parity}')
            if re.findall(r'<a\b[^>]*href="#([^"]+)"', html):
                ids = set(re.findall(r'\bid="([^"]+)"',html))
                broken = set(re.findall(r'<a\b[^>]*href="#([^"]+)"',html)) - ids
                if broken: raise AssertionError(f'Broken anchors {dest}: {broken}')
            (ROOT / dest).write_text(html,'utf-8')
            print(f'BUILT {dest}: {len(html)} characters · {len(sig[0])} sections · {sig[1]} images · {sig[2]} articles')
            total+=1
    print('OK: all',total,'localized pages have structural parity with their English originals.')


if __name__=='__main__':
    main()
