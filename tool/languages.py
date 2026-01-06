SUPPORTED_LANGUAGES = {
    "afr": "Afrikaans", "amh": "Amharic", "arb": "Arabic", "ary": "Moroccan Arabic", "arz": "Egyptian Arabic",
    "asm": "Assamese", "ast": "Asturian", "azj": "North Azerbaijani", "bel": "Belarusian", "ben": "Bengali",
    "bos": "Bosnian", "bul": "Bulgarian", "cat": "Catalan", "ceb": "Cebuano", "ces": "Czech",
    "ckb": "Central Kurdish", "cmn": "Mandarin Chinese", "cym": "Welsh", "dan": "Danish", "deu": "German",
    "ell": "Greek", "eng": "English", "est": "Estonian", "eus": "Basque", "fas": "Persian",
    "fin": "Finnish", "fra": "French", "gaz": "West Central Oromo", "gle": "Irish", "glg": "Galician",
    "guj": "Gujarati", "heb": "Hebrew", "hin": "Hindi", "hrv": "Croatian", "hun": "Hungarian",
    "hye": "Armenian", "ibo": "Igbo", "ind": "Indonesian", "isl": "Icelandic", "ita": "Italian",
    "jav": "Javanese", "jpn": "Japanese", "kan": "Kannada", "kat": "Georgian", "kaz": "Kazakh",
    "khm": "Khmer", "kan": "Kannada", "kor": "Korean", "kir": "Kyrgyz", "lao": "Lao",
    "lit": "Lithuanian", "lug": "Ganda", "luo": "Luo", "lvs": "Standard Latvian", "mai": "Maithili",
    "mal": "Malayalam", "mar": "Marathi", "mkd": "Macedonian", "mlt": "Maltese", "mny": "Maguindanao",
    "mya": "Burmese", "nld": "Dutch", "nob": "Norwegian Bokmål", "npi": "Nepali", "nso": "Northern Sotho",
    "nya": "Nyanja", "oci": "Occitan", "ory": "Odia", "pan": "Punjabi", "pol": "Polish",
    "por": "Portuguese", "pus": "Pashto", "ron": "Romanian", "rus": "Russian", "sat": "Santali",
    "slk": "Slovak", "slv": "Slovenian", "sna": "Shona", "snd": "Sindhi", "som": "Somali",
    "spa": "Spanish", "sqi": "Albanian", "srp": "Serbian", "swe": "Swedish", "swh": "Swahili",
    "tam": "Tamil", "tel": "Telugu", "tgk": "Tajik", "tgl": "Tagalog", "tha": "Thai",
    "tur": "Turkish", "ukr": "Ukrainian", "urd": "Urdu", "uzn": "Northern Uzbek", "vie": "Vietnamese",
    "yor": "Yoruba", "zho": "Chinese (Traditional/Simplified)", "zul": "Zulu"
}

def validate_language(lang_code: str) -> bool:
    """Check if the given language code is supported by SeamlessM4T."""
    return lang_code in SUPPORTED_LANGUAGES or lang_code == "auto"

def get_language_name(lang_code: str) -> str:
    """Get the human-readable name of a language code."""
    return SUPPORTED_LANGUAGES.get(lang_code, "Unknown")
