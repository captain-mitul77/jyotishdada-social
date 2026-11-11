"""Hindi (Devanagari) labels for the values the JyotishDada backend returns in English.

Keys are EXACTLY the spellings in backend app/core/constants.py. Anything not found here falls back to the
English string from the API (never an invented translation), and the renderer shows the English value under
the Hindi one anyway.
"""

TITHI = {
    "Pratipada": "प्रतिपदा", "Dwitiya": "द्वितीया", "Tritiya": "तृतीया", "Chaturthi": "चतुर्थी",
    "Panchami": "पंचमी", "Shashthi": "षष्ठी", "Saptami": "सप्तमी", "Ashtami": "अष्टमी",
    "Navami": "नवमी", "Dashami": "दशमी", "Ekadashi": "एकादशी", "Dwadashi": "द्वादशी",
    "Trayodashi": "त्रयोदशी", "Chaturdashi": "चतुर्दशी", "Purnima": "पूर्णिमा", "Amavasya": "अमावस्या",
}
PAKSHA = {"Shukla": "शुक्ल पक्ष", "Krishna": "कृष्ण पक्ष"}
NAKSHATRA = {
    "Ashwini": "अश्विनी", "Bharani": "भरणी", "Krittika": "कृत्तिका", "Rohini": "रोहिणी",
    "Mrigashira": "मृगशिरा", "Ardra": "आर्द्रा", "Punarvasu": "पुनर्वसु", "Pushya": "पुष्य",
    "Ashlesha": "आश्लेषा", "Magha": "मघा", "Purva Phalguni": "पूर्वा फाल्गुनी",
    "Uttara Phalguni": "उत्तरा फाल्गुनी", "Hasta": "हस्त", "Chitra": "चित्रा", "Swati": "स्वाति",
    "Vishakha": "विशाखा", "Anuradha": "अनुराधा", "Jyeshtha": "ज्येष्ठा", "Mula": "मूल",
    "Purva Ashadha": "पूर्वाषाढ़ा", "Uttara Ashadha": "उत्तराषाढ़ा", "Shravana": "श्रवण",
    "Dhanishta": "धनिष्ठा", "Shatabhisha": "शतभिषा", "Purva Bhadrapada": "पूर्वाभाद्रपद",
    "Uttara Bhadrapada": "उत्तराभाद्रपद", "Revati": "रेवती",
}
YOGA = {
    "Vishkambha": "विष्कुम्भ", "Priti": "प्रीति", "Ayushman": "आयुष्मान", "Saubhagya": "सौभाग्य",
    "Shobhana": "शोभन", "Atiganda": "अतिगण्ड", "Sukarman": "सुकर्मा", "Dhriti": "धृति",
    "Shoola": "शूल", "Ganda": "गण्ड", "Vriddhi": "वृद्धि", "Dhruva": "ध्रुव", "Vyaghata": "व्याघात",
    "Harshana": "हर्षण", "Vajra": "वज्र", "Siddhi": "सिद्धि", "Vyatipata": "व्यतीपात",
    "Variyana": "वरीयान", "Parigha": "परिघ", "Shiva": "शिव", "Siddha": "सिद्ध", "Sadhya": "साध्य",
    "Shubha": "शुभ", "Shukla": "शुक्ल", "Brahma": "ब्रह्म", "Indra": "इन्द्र", "Vaidhriti": "वैधृति",
}
KARANA = {
    "Bava": "बव", "Balava": "बालव", "Kaulava": "कौलव", "Taitila": "तैतिल", "Gara": "गर",
    "Vanija": "वणिज", "Vishti": "विष्टि (भद्रा)", "Shakuni": "शकुनि", "Chatushpada": "चतुष्पद",
    "Naga": "नाग", "Kimstughna": "किंस्तुघ्न",
}
WEEKDAY = {  # API gives e.g. "Monday (Somavara)"; key on the English day name
    "Monday": "सोमवार", "Tuesday": "मंगलवार", "Wednesday": "बुधवार", "Thursday": "गुरुवार",
    "Friday": "शुक्रवार", "Saturday": "शनिवार", "Sunday": "रविवार",
}
MONTH = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर",
         "अक्टूबर", "नवंबर", "दिसंबर"]
# Only cities we have actually checked; anything else shows the API's English city name.
CITY = {"delhi": "नई दिल्ली", "mumbai": "मुंबई", "ahmedabad": "अहमदाबाद", "chennai": "चेन्नई",
        "kolkata": "कोलकाता", "bengaluru": "बेंगलुरु", "jaipur": "जयपुर", "lucknow": "लखनऊ"}


def hi(table: dict, key: str) -> str:
    """Hindi form if known, otherwise the original string (never guess)."""
    return table.get(key, key)


def weekday_en(api_weekday: str) -> str:
    return api_weekday.split(" ")[0]
