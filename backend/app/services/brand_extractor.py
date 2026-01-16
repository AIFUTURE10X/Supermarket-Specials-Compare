"""
Brand Extractor Service

Extracts brand names from product names using a comprehensive list of
Australian supermarket brands.
"""
from typing import Optional


# Comprehensive list of Australian supermarket brands
# Sorted by category for maintainability
KNOWN_BRANDS = [
    # Major food brands
    "Heinz", "Kellogg's", "Kelloggs", "Nestlé", "Nestle", "Cadbury", "Kraft",
    "Arnott's", "Arnotts", "Sanitarium", "Uncle Tobys", "Tip Top",
    "Helga's", "Helgas", "Bakers Delight", "Abbott's", "Abbotts",

    # Dairy & Refrigerated
    "Bega", "Devondale", "Dairy Farmers", "Pauls", "Pura", "Yoplait",
    "Chobani", "Vaalia", "Jalna", "Brownes", "Farmers Union", "Anchor",
    "Western Star", "Lurpak", "Mainland", "Philadelphia", "Babybel",
    "The Collective", "Rokeby Farms", "Coon", "Cracker Barrel",

    # Sauces & Condiments
    "Masterfoods", "MasterFoods", "Fountain", "Rosella", "Leggo's", "Leggos",
    "Dolmio", "Barilla", "San Remo", "Latina", "Lee Kum Kee", "Kikkoman",
    "Ayam", "Maggi", "Continental", "Kantong", "Valcom", "Passage To",

    # Canned goods & Seafood
    "John West", "Sirena", "Safcol", "Greenseas", "SPC", "Edgell",
    "Ardmona", "Annalisa", "La Gina", "Ocean Rise", "Brunswick",

    # Snacks & Confectionery
    "Smith's", "Smiths", "Doritos", "Pringles", "Red Rock Deli", "Kettle",
    "Lindt", "Ferrero", "Mars", "Snickers", "Kit Kat", "KitKat", "Twix",
    "M&M's", "M&Ms", "Maltesers", "Bounty", "Milky Way", "Toblerone",
    "Darrell Lea", "Allen's", "Allens", "The Natural Confectionery",
    "Mentos", "Skittles", "Starburst", "Haribo", "Werther's", "Werthers",
    "Tim Tam", "Shapes", "Tiny Teddy", "Tiny Teddys", "Oreo",

    # Chips & Crackers
    "Thins", "CC's", "CCs", "Twisties", "Cheetos", "Cheezels", "Grain Waves",
    "Sakata", "Fantastic", "Ritz", "Jatz", "Salada", "Vita-Weat", "Vitaweat",

    # Breakfast & Cereals
    "Weet-Bix", "Weetbix", "Nutri-Grain", "Nutrigrain", "Coco Pops",
    "Corn Flakes", "Special K", "Just Right", "Sultana Bran", "All-Bran",
    "Milo", "Quick Oats", "Carman's", "Carmans", "Freedom Foods",

    # Bread & Bakery
    "Wonder", "Burgen", "Abbotts Village", "Lawson's", "Lawsons",
    "Golden", "Coupland's", "Couplands",

    # Drinks - Soft Drinks
    "Coca-Cola", "Coca Cola", "Pepsi", "Schweppes", "Kirks", "Solo",
    "Fanta", "Sprite", "Lift", "Sunkist", "Bundaberg", "L&P",

    # Drinks - Water
    "Mount Franklin", "Pump", "Cool Ridge", "Frantelle", "Evian",
    "San Pellegrino", "Perrier", "Voss",

    # Drinks - Juice
    "Golden Circle", "Berri", "Daily Juice", "Nudie", "Boost",

    # Drinks - Coffee & Tea
    "Lipton", "Moccona", "Nescafé", "Nescafe", "Vittoria", "Lavazza",
    "Robert Timms", "International Roast", "Twinings", "T2", "Dilmah",

    # Drinks - Energy & Sports
    "Red Bull", "V", "Mother", "Monster", "Gatorade", "Powerade", "Maximus",

    # Drinks - Alcohol
    "VB", "Carlton", "XXXX", "Tooheys", "Coopers", "James Boag's",
    "James Boags", "Corona", "Heineken", "Smirnoff", "Absolut",
    "Jack Daniel's", "Jack Daniels", "Jim Beam", "Johnnie Walker",
    "Penfolds", "Jacob's Creek", "Jacobs Creek", "Yellowtail", "Wolf Blass",

    # Cleaning & Household
    "Dettol", "Pine O Cleen", "Pine O Clean", "Glen 20", "Finish", "Fairy",
    "OMO", "Omo", "Dynamo", "Cold Power", "Surf", "Napisan", "Vanish",
    "Ajax", "Domestos", "Harpic", "Mr Muscle", "Spray & Wipe",
    "White King", "Earth Choice", "Ecostore", "Morning Fresh",
    "Palmolive", "Radiant", "Biozet", "Drive", "Fab",

    # Paper & Tissues
    "Kleenex", "Viva", "Sorbent", "Quilton", "Purex", "Handee",

    # Personal Care - Body
    "Dove", "Palmolive", "Nivea", "Lux", "Rexona", "Lynx", "Impulse",
    "Sure", "Degree", "Brut", "Old Spice",

    # Personal Care - Oral
    "Colgate", "Oral-B", "Oral B", "Sensodyne", "Listerine", "Macleans",

    # Personal Care - Hair
    "Pantene", "Head & Shoulders", "Head and Shoulders", "Garnier",
    "L'Oreal", "LOreal", "Schwarzkopf", "Tresemme", "TRESemme", "Sunsilk",
    "Herbal Essences", "John Frieda", "OGX",

    # Personal Care - Skincare
    "Olay", "Neutrogena", "Cetaphil", "QV", "Aveeno", "Simple",

    # Personal Care - Shaving
    "Gillette", "Schick", "Wilkinson Sword", "BIC",

    # Baby Care
    "Huggies", "Pampers", "BabyLove", "Curash", "Johnson's", "Johnsons",
    "Sudocrem", "Bepanthen", "Nappy San",

    # Baby Food
    "Heinz Baby", "Rafferty's Garden", "Raffertys Garden", "Bellamy's",
    "Bellamys", "Only Organic", "Farex", "Wattie's", "Watties",

    # Pet Food
    "Pedigree", "Whiskas", "Dine", "Fancy Feast", "Purina", "Advance",
    "Optimum", "Supercoat", "My Dog", "Schmackos", "Lucky Dog",

    # Health & Vitamins
    "Blackmores", "Swisse", "Nature's Own", "Natures Own", "Cenovis",
    "Berocca", "Panadol", "Nurofen", "Voltaren",

    # International Foods
    "Ayam", "Valcom", "Yeo's", "Yeos", "S&B", "Nongshim", "Nissin",
    "Indomie", "Mama", "Pandaroo", "Blue Dragon", "Sharwood's", "Sharwoods",

    # ALDI Brands
    "Remano", "Brooklea", "Monarc", "Farmdale", "Belmont", "Grandessa",
    "Specially Selected", "Jindurra", "Bakers Life", "Choceur",
    "Knoppers", "Moser Roth", "Berryhill", "Colway", "Lacura", "Ombra",
    "Tandil", "Di-San", "Power Force", "Mamia", "Little Journey",
    "Fusia", "Asia Specialities", "Asia Green Garden", "Ocean Rise",

    # Store brands (include for matching, lower priority)
    "Woolworths", "Coles", "IGA", "Macro", "Homebrand", "Black & Gold",
    "Essentials", "Community Co", "You'll Love Coles",
]


def extract_brand_from_name(product_name: str) -> Optional[str]:
    """
    Extract brand from product name.

    Uses a comprehensive list of known brands and falls back to
    extracting capitalized first words.

    Examples:
        - "Heinz Ketchup Tomato Sauce 500mL" → "Heinz"
        - "John West Tuna In Tomato Sauce 95g" → "John West"
        - "Woolworths Full Cream Milk 2L" → "Woolworths"
        - "ASIA SPECIALITIES Tikka Masala Sauce 500g" → "Asia Specialities"

    Args:
        product_name: The full product name

    Returns:
        The extracted brand name, or None if not found
    """
    if not product_name:
        return None

    name_lower = product_name.lower()

    # Check each known brand (longest match first to handle "John West" before "John")
    sorted_brands = sorted(KNOWN_BRANDS, key=len, reverse=True)

    for brand in sorted_brands:
        brand_lower = brand.lower()
        # Check if product name starts with this brand
        if name_lower.startswith(brand_lower + " "):
            # Return the brand in its canonical form
            return brand
        if name_lower.startswith(brand_lower):
            # Handle cases like "Heinz500ml" (no space)
            remaining = name_lower[len(brand_lower):]
            if not remaining or not remaining[0].isalpha():
                return brand

    # Fallback: try to extract brand from first word(s)
    words = product_name.split()
    if not words:
        return None

    first_word = words[0]

    # Skip if first word looks like a size/quantity
    if any(c.isdigit() for c in first_word):
        return None

    # Skip common non-brand words
    skip_words = {"the", "a", "an", "new", "fresh", "organic", "free", "range"}
    if first_word.lower() in skip_words:
        if len(words) > 1:
            first_word = words[1]
        else:
            return None

    # Accept if it's capitalized and reasonable length
    if first_word[0].isupper() and len(first_word) >= 2:
        # Check for two-word brands (e.g., "Red Rock")
        if len(words) > 1 and words[1][0].isupper() and len(words[1]) >= 2:
            # Avoid "Tomato Sauce" being detected as brand
            second_lower = words[1].lower()
            if second_lower not in {"sauce", "milk", "bread", "cheese", "juice", "water"}:
                potential_brand = f"{first_word} {words[1]}"
                if len(potential_brand) <= 20:  # Reasonable brand name length
                    return potential_brand

        return first_word

    return None


def extract_size_from_name(product_name: str) -> Optional[str]:
    """
    Extract size/quantity from product name.

    Examples:
        - "Heinz Ketchup Tomato Sauce 500mL" → "500mL"
        - "John West Tuna 95g" → "95g"
        - "Milk 2 Litres" → "2 Litres"

    Args:
        product_name: The full product name

    Returns:
        The extracted size, or None if not found
    """
    import re

    if not product_name:
        return None

    # Common size patterns
    patterns = [
        r'(\d+(?:\.\d+)?\s*(?:ml|mL|ML|l|L|litre|litres|liter|liters))',
        r'(\d+(?:\.\d+)?\s*(?:g|kg|KG|Kg))',
        r'(\d+\s*(?:pack|pk|Pack|PK))',
        r'(\d+\s*x\s*\d+(?:\.\d+)?\s*(?:ml|mL|g|kg)?)',  # e.g., "6 x 375ml"
        r'(\d+(?:\.\d+)?\s*(?:oz|OZ))',
    ]

    for pattern in patterns:
        match = re.search(pattern, product_name, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None
