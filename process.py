import re


def clean_text(text):
    text = re.sub(r'[^\w\s\.,;:]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def structure_text(text):
    sections = ["Experiência", "Educação",
                "Habilidades", "Projetos", "Certificações"]
    formatted_text = ""
    for section in sections:
        pattern = re.compile(
            rf'({section}.*?)(?=\b(?:{"|".join(sections)}|$))', re.DOTALL | re.IGNORECASE)
        match = pattern.search(text)
        if match:
            section_text = match.group(1).strip()
            formatted_text += f"\n\n{section.upper()}\n{section_text}\n"
    remaining_text = re.sub(
        rf'\b(?:{"|".join(sections)})\b.*?', '', text, flags=re.DOTALL | re.IGNORECASE).strip()
    formatted_text += f"\n\nOUTRAS INFORMAÇÕES\n{remaining_text}"
    return formatted_text.strip()
