import streamlit as st
from openai import OpenAI
from pydantic import BaseModel
import re
import json

#page configurations
st.set_page_config(
    page_title="Recipe Drift Checker",
    page_icon="🍴",
    layout="centered",
)

#styling options
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;600&family=Roboto+Mono:wght@300;400&display=swap');

html, body, [class*="css"] {
    font-family: 'Roboto', sans-serif;
    background-color: #F7F3EE;
    color: #1a1208;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2.5rem; max-width: 780px; }

.hero {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
    border-bottom: 2px solid #C0392B;
    margin-bottom: 2rem;
}
.hero-jp {
    font-family: 'Roboto', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    color: #C0392B;
    letter-spacing: 0.12em;
    line-height: 1.1;
}
.hero-en {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #7a6a55;
    margin-top: 0.4rem;
}
.hero-sub {
    font-size: 0.9rem;
    color: #5c4a32;
    margin-top: 0.9rem;
    line-height: 1.6;
}
.input-card {
    background: #FFF8F0;
    border: 1px solid #d4c4a8;
    border-left: 4px solid #C0392B;
    border-radius: 2px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.8rem;
}
.section-header {
    font-family: 'Roboto', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #C0392B;
    letter-spacing: 0.08em;
    border-bottom: 1px solid #d4c4a8;
    padding-bottom: 0.4rem;
    margin: 1.6rem 0 0.9rem;
}
.ing-row {
    display: flex;
    align-items: baseline;
    gap: 0.7rem;
    padding: 0.35rem 0;
    border-bottom: 1px dotted #e0d4c0;
    font-size: 0.93rem;
}
.ing-row:last-child { border-bottom: none; }
.badge {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 2px 7px;
    border-radius: 2px;
    white-space: nowrap;
    flex-shrink: 0;
}
.badge-core       { background: #fde8e8; color: #C0392B; border: 1px solid #f5c0b8; }
.badge-supporting { background: #fdf4e3; color: #8a6500; border: 1px solid #e8d498; }
.badge-optional   { background: #eef3ee; color: #3a6040; border: 1px solid #b8d4bc; }
.badge-unknown    { background: #f0f0f0; color: #888;    border: 1px solid #ccc; }
.status-dot {
    font-size: 0.75rem;
    margin-left: auto;
    white-space: nowrap;
    font-family: 'DM Mono', monospace;
}
.status-unchanged { color: #888; }
.status-swapped   { color: #b07800; font-weight: 600; }
.status-removed   { color: #C0392B; font-weight: 600; }
.adapted-ing {
    padding: 0.32rem 0;
    border-bottom: 1px dotted #e0d4c0;
    font-size: 0.93rem;
    color: #2a2018;
}
.adapted-ing:last-child { border-bottom: none; }
.instruction-step {
    display: flex;
    gap: 1rem;
    padding: 0.6rem 0;
    border-bottom: 1px dotted #e0d4c0;
    font-size: 0.92rem;
    line-height: 1.65;
}
.step-num {
    font-family: 'Roboto', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: #C0392B;
    min-width: 1.6rem;
    line-height: 1.4;
}
.drift-banner {
    padding: 1.2rem 1.6rem;
    border-radius: 2px;
    margin-top: 1.6rem;
    border-left: 5px solid;
}
.drift-low    { background: #eef6ee; border-color: #3a8a4a; color: #1e4a26; }
.drift-medium { background: #fdf6e3; border-color: #c08a00; color: #5c4200; }
.drift-high   { background: #fdecea; border-color: #C0392B; color: #6a1010; }
.drift-label {
    font-family: 'Roboto', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    margin-bottom: 0.4rem;
}
.drift-msg { font-size: 0.92rem; line-height: 1.65; }
.drift-stats {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    color: #7a6a55;
    margin-top: 0.8rem;
    padding-top: 0.6rem;
    border-top: 1px solid #d4c4a8;
}
div[data-testid="stTextInput"] input {
    font-family: 'Roboto Mono', monospace !important;
    font-size: 0.88rem !important;
    border-radius: 2px !important;
    border-color: #c8b898 !important;
    background: #fffaf4 !important;
}
div[data-testid="stButton"] > button {
    background: #C0392B !important;
    color: white !important;
    font-family: 'Roboto Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
div[data-testid="stButton"] > button:hover { opacity: 0.85 !important; }
</style>
""", unsafe_allow_html=True)


#hero on app
st.markdown("""
<div class="hero">
    <div class="hero-jp">Recipe Drift Checker</div>
    <div class="hero-en">Powered by GPT & Fine-Tuned AI</div>
    <div class="hero-sub">
        Paste a Japanese recipe URL and your zip code.<br>
        We'll check what's available near you — and tell you how far the dish drifts from the original.
    </div>
</div>
""", unsafe_allow_html=True)


#Identify models to use (same as notebook)
GPT_MODEL   = "gpt-5"
FT_MODEL    = "ft:gpt-4.1-2025-04-14:personal:recipe-ingredient-classification:D8YBJCJA"
JUDGE_MODEL = "gpt-4.1-mini-2025-04-14"


#helper functions (same as notebook)
def normalize(s: str) -> str:
    """Lowercase and remove spaces for consistent matching."""
    return re.sub(r"\s+", " ", s.strip().lower())


def strip_quantity(ingredient: str) -> str:
    """
    Strips leading quantities, units, and prep notes from an ingredient string.

    Examples:
      "1 Gobo (burdock root, Sasagaki cut)"  -> "gobo (burdock root)"
      "2 1/2 Tbsp Soy Sauce"                 -> "soy sauce"
      "1/4 cup Dashi (or water)"             -> "dashi (or water)"
    """
    s = ingredient.strip()
    s = re.sub(r"^\d+\s+\d+/\d+\s+", "", s)   # "2 1/2 "
    s = re.sub(r"^\d+/\d+\s+",        "", s)   # "1/2 "
    s = re.sub(r"^\d+\s*",            "", s)   # "1 "
    units = r"(?:Tbsp|tbsp|tsp|cup|cups|oz|lb|lbs|g|kg|ml|cloves?|stalks?|pieces?|cans?)\s+"
    s = re.sub(r"^" + units, "", s, flags=re.IGNORECASE)
    prep_keywords = r"thinly|cut|sliced|chopped|diced|minced|grated|julienned|sasagaki|peeled|trimmed"
    s = re.sub(r"\s*\([^)]*(?:" + prep_keywords + r")[^)]*\)", "", s, flags=re.IGNORECASE)
    return normalize(s)


def clean_ingredient(s: str) -> str:
    """Remove links like ([site.com](https://...)) that GPT sometimes adds to ingredient lists."""
    return re.sub(r"\s*\(\[.*?\]\(.*?\)\)", "", s).strip()


#pydantic model (same as notebook)
class RecipeExtract(BaseModel):
    title: str
    servings: str | None = None
    prep_time: str | None = None
    cook_time: str | None = None
    total_time: str | None = None
    ingredients: list[str]
    instructions: list[str]


#functions defined (same as notebook)
def get_original_recipe(client: OpenAI, url: str) -> RecipeExtract:
    """Fetch and parse the original recipe from a URL."""
    prompt = f"""
    Open this recipe page and extract the recipe details:
    URL: {url}

    Return:
    - title
    - servings
    - prep_time, cook_time, total_time (if available)
    - ingredients (as a list, keep each ingredient on one line exactly as written)
    - instructions (numbered)
    Return in JSON.
    """
    resp = client.responses.parse(
        model=GPT_MODEL,
        tools=[{"type": "web_search"}],
        reasoning={"effort": "low"},
        input=prompt,
        text_format=RecipeExtract,
    )
    return resp.output_parsed


def get_adapted_recipe(client: OpenAI, url: str, zip_code: str) -> RecipeExtract:
    """
    Adapt the recipe for ingredients available in the given zip code.
    Instructs the model to keep ingredient names consistent where no substitution is needed.
    """
    prompt = f"""
    Open this recipe page and review the recipe details:
    URL: {url}

    I am located in zip code {zip_code}. Look up grocery stores in my zip code and check
    which ingredients from the recipe are available to me.

    Important instructions:
    - For ingredients that ARE available, keep the ingredient name exactly as it appears in the recipe.
    - For ingredients that are NOT available, substitute with what is available and clearly note the substitution.
    - Return the full updated ingredient list and any instruction changes needed.
    Return in JSON.
    """
    resp = client.responses.parse(
        model=GPT_MODEL,
        tools=[{"type": "web_search"}],
        reasoning={"effort": "low"},
        input=prompt,
        text_format=RecipeExtract,
    )
    adapted = resp.output_parsed

    #remove inline URLs that GPT sometimes adds to ingredient strings
    adapted.ingredients = [clean_ingredient(ing) for ing in adapted.ingredients]

    return adapted


def get_ingredient_roles(client: OpenAI, recipe_title: str, ingredients: list[str]) -> dict[str, str]:
    """
    Call the fine-tuned model to classify each ingredient as core, supporting, or optional.
    Returns a dict mapping normalized ingredient name -> role.
    """
    stripped = [strip_quantity(ing) for ing in ingredients]
    ingredient_lines = "\n".join(f"- {ing}" for ing in stripped)

    system_msg = (
        "You label each ingredient in a recipe as core, supporting, or optional. "
        "Respond with one ingredient per line in the format 'ingredient name: role'."
    )
    user_msg = f"Recipe title: {recipe_title}\nIngredients:\n{ingredient_lines}"

    resp = client.responses.create(
        model=FT_MODEL,
        input=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ],
    )

    text = resp.output[0].content[0].text.strip()

    roles: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        name, role = line.split(":", 1)
        roles[normalize(name)] = role.strip().lower()
    return roles


def detect_changes_with_model(
    client: OpenAI,
    original_ingredients: list[str],
    adapted_ingredients: list[str],
) -> dict[str, str]:
    """
    Uses a language model to compare the original and adapted ingredients.
    Returns a dict mapping original ingredient name as 'unchanged' | 'swapped' | 'removed'.
    """
    original_list = "\n".join(f"- {ing}" for ing in original_ingredients)
    adapted_list  = "\n".join(f"- {ing}" for ing in adapted_ingredients)

    prompt = f"""
You are a recipe ingredient comparison assistant.

Compare the ORIGINAL ingredient list to the ADAPTED ingredient list.
For each ingredient in the ORIGINAL list, determine its status in the ADAPTED list:
- "unchanged": the same ingredient is present (even if phrased slightly differently)
- "swapped": a different ingredient was substituted for it
- "removed": the ingredient was dropped with no substitute

ORIGINAL ingredients:
{original_list}

ADAPTED ingredients:
{adapted_list}

Respond ONLY with a valid JSON object. Keys are the original ingredient names (exactly as listed above).
Values are one of: "unchanged", "swapped", or "removed".
Do not include any explanation or extra text — only the JSON object.
"""
    resp = client.responses.create(
        model=JUDGE_MODEL,
        input=[{"role": "user", "content": prompt}],
    )

    raw = resp.output[0].content[0].text.strip()

    # Strip markdown code fences in case the model wraps the JSON
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    parsed: dict[str, str] = json.loads(raw)

    # Normalize keys so they match the role dict keys downstream
    return {strip_quantity(k): v.strip().lower() for k, v in parsed.items()}


def compute_drift(
    roles: dict[str, str],
    change_status: dict[str, str],
    recipe_title: str | None = None,
) -> dict:
    """
    Computes the drift level of the adapted recipe compared to the original.
    Drift rules:
      LOW    — 0 core changed AND <= 2 supporting changed
      MEDIUM — 1 core changed AND <= 3 supporting changed
               OR 0 core changed AND 3-5 supporting changed
      HIGH   — 2+ core changed
               OR 1+ core removed entirely
               OR 1 core changed AND 4+ supporting changed
               OR 6+ supporting changed
    """
    core_changed       = 0
    core_removed       = 0
    supporting_changed = 0
    optional_changed   = 0

    # Add up all changes first before making any drift decision
    for name, role in roles.items():
        status = change_status.get(name, "unchanged")

        if role == "core":
            if status != "unchanged":
                core_changed += 1
                if status == "removed":
                    core_removed += 1
        elif role == "supporting":
            if status != "unchanged":
                supporting_changed += 1
        elif role == "optional":
            if status != "unchanged":
                optional_changed += 1

    # Drift classification
    if core_changed == 0 and supporting_changed <= 2:
        drift = "low"
    elif (
        (core_changed == 1 and supporting_changed <= 3)
        or (core_changed == 0 and 3 <= supporting_changed <= 5)
    ):
        drift = "medium"
    elif (
        core_changed >= 2
        or core_removed >= 1
        or (core_changed == 1 and supporting_changed >= 4)
        or supporting_changed >= 6
    ):
        drift = "high"
    else:
        drift = "medium"  # fallback

    title = recipe_title or "this recipe"

    if drift == "low":
        label   = "🟢 Low Drift"
        message = (
            f"{title} is still very close to the original recipe. "
            "All core ingredients are unchanged and only a few supporting ingredients were swapped."
        )
    elif drift == "medium":
        label   = "🟡 Medium Drift"
        message = (
            f"{title} is still recognizable as the same dish, "
            "but at least one core ingredient or several supporting ingredients have been changed. "
            "It is still worth making, but know that it will taste slightly different from the original."
        )
    else:
        label   = "🔴 High Drift"
        message = (
            f"{title} has changed significantly. "
            "Multiple core and/or supporting ingredients have been removed or substituted. "
            "It may still taste good, but it is no longer the original dish. "
            "You can choose a different recipe or think of this as an 'inspired by' version."
        )

    return {
        "drift_level":        drift,
        "label":              label,
        "core_changed":       core_changed,
        "core_removed":       core_removed,
        "supporting_changed": supporting_changed,
        "optional_changed":   optional_changed,
        "message":            message,
    }


#request user input on the key variables needed to run the app

url      = st.text_input("Recipe URL", placeholder="https://www.japanesecooking101.com/...")
zip_code = st.text_input("Your Zip Code", placeholder="e.g. 80758", max_chars=10)

run = st.button("→  Analyze Recipe")


#putting it all together
if run:
    # Validate inputs
    if not url.strip():
        st.error("Please enter a recipe URL.")
        st.stop()
    if not zip_code.strip():
        st.error("Please enter your zip code.")
        st.stop()

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    try:
        with st.status("Working on it...", expanded=True) as status:
            st.write("📖  Fetching original recipe...")
            original = get_original_recipe(client, url)

            st.write(f"🗺️  Adapting recipe for zip code {zip_code}...")
            adapted = get_adapted_recipe(client, url, zip_code)

            st.write("🏷️  Classifying ingredient roles...")
            roles = get_ingredient_roles(client, original.title, original.ingredients)

            st.write("🔍  Detecting ingredient changes...")
            changes = detect_changes_with_model(client, original.ingredients, adapted.ingredients)

            st.write("📊  Computing recipe drift...")
            drift_info = compute_drift(
                roles=roles,
                change_status=changes,
                recipe_title=original.title,
            )

            status.update(label="Analysis complete!", state="complete", expanded=False)

    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.stop()

    # Displaying the results

    #recipe title
    st.markdown(
        f"<h2 style='font-family: 'Roboto', sans-serif; color:#1a1208; margin-top:1.5rem;'>"
        f"{original.title}</h2>",
        unsafe_allow_html=True,
    )

    #drift banner
    drift_class = f"drift-{drift_info['drift_level']}"
    st.markdown(f"""
    <div class="drift-banner {drift_class}">
        <div class="drift-label">{drift_info['label']}</div>
        <div class="drift-msg">{drift_info['message']}</div>
        <div class="drift-stats">
            core changed: {drift_info['core_changed']} &nbsp;|&nbsp;
            core removed: {drift_info['core_removed']} &nbsp;|&nbsp;
            supporting changed: {drift_info['supporting_changed']} &nbsp;|&nbsp;
            optional changed: {drift_info['optional_changed']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    #ingredient comparison
    st.markdown('<div class="section-header">Ingredient Comparison</div>', unsafe_allow_html=True)
    for ing in original.ingredients:
        key    = strip_quantity(ing)
        role   = roles.get(key, "unknown")
        status = changes.get(key, "unknown")

        badge_class  = f"badge-{role}" if role in ("core", "supporting", "optional") else "badge-unknown"
        status_class = f"status-{status}" if status in ("unchanged", "swapped", "removed") else "status-unchanged"
        status_icon  = {"unchanged": "✓ unchanged", "swapped": "⇄ swapped", "removed": "✕ removed"}.get(status, status)

        st.markdown(f"""
        <div class="ing-row">
            <span class="badge {badge_class}">{role}</span>
            <span>{ing}</span>
            <span class="status-dot {status_class}">{status_icon}</span>
        </div>
        """, unsafe_allow_html=True)

    #adapted ingredients
    st.markdown(
        f'<div class="section-header">Adapted Ingredients for Zip Code {zip_code}</div>',
        unsafe_allow_html=True,
    )
    for ing in adapted.ingredients:
        st.markdown(f'<div class="adapted-ing">· {ing}</div>', unsafe_allow_html=True)

    #adapted instructions
    st.markdown('<div class="section-header">Adapted Instructions</div>', unsafe_allow_html=True)
    for i, step in enumerate(adapted.instructions, 1):
        st.markdown(f"""
        <div class="instruction-step">
            <span class="step-num">{i}</span>
            <span>{step}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
