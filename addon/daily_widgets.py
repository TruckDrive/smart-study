# -*- coding: utf-8 -*-

import hashlib
from datetime import date

# --- Translation Function ---
# NOTE on fact translations:
# The MEDICAL_FACTS / LAW_FACTS / GENERAL_FACTS / COUNTRY_FACTS dicts keep
# their English text as-is. The _() wrapper is applied at the READ site
# inside ``todays_fact`` so that live language switches actually
# take effect on the next render. Wrapping the dict literals directly with
# _() would freeze the translations at module-import time and break the
# live-update contract for the fact widget.
try:
    from .locales import _
except ImportError:
    def _(text): return text  # safety fallback

# --- Medizinische Fakten Liste ---
MEDICAL_FACTS = [
    {"text": "Did you know? Your brain consumes a significant amount of energy, about 20% of your body's total supply, despite only accounting for roughly 2% of your total body weight.", "image": "brain_energy.png"},
    {"text": "It's astounding: If you lined up all ~25 trillion erythrocytes (red blood cells) in your body end-to-end, they would form a chain long enough to circle the entire Earth four times at the equator!", "image": "erythrocyte_chain.png"},
    {"text": "Technically, you perceive sound with your brain, not directly with your ears. Your ears simply act as sophisticated collectors, converting sound waves into signals the brain interprets.", "image": "brain_hearing.png"},
    {"text": "Unique within the body, the cornea lacks its own blood supply. Instead, this transparent eye layer gets the oxygen it needs directly from the surrounding air.", "image": "cornea_oxygen.png"},
    {"text": "Your skeleton isn't static! Bones are constantly undergoing a process of breakdown and rebuilding, leading to a complete skeletal renewal approximately every 10 years.", "image": "bone_renewal.png"},
    {"text": "The power of the mind: The placebo effect can be so potent that treatments sometimes still work even when patients are fully aware they're receiving a placebo.", "image": "placebo_effect.png"},
    {"text": "Contrary to popular belief, human blood is never actually blue. It only appears bluish through the skin because of how different wavelengths of light penetrate and reflect off tissues.", "image": "blood_color.png"},
    {"text": "Those wrinkly fingers after a bath aren't just from water absorption! It's an active nervous system response, possibly evolved to improve grip on wet surfaces.", "image": "wrinkled_fingers.png"},
    {"text": "Your gut contains its own complex 'brain,' the enteric nervous system. This extensive network boasts over 100 million neurons, managing digestion largely independently.", "image": "gut_brain.png"},
    {"text": "The sheer complexity of the human brain is staggering: It contains more connections (synapses) between neurons than there are estimated stars in the entire Milky Way galaxy.", "image": "brain_synapses.png"},
    {"text": "During moments of intense fear, your body initiates the 'fight or flight' response, strategically redirecting blood flow away from non-essential areas and towards your major muscles.", "image": "fight_or_flight.png"},
    {"text": "A good laugh is like natural medicine! Laughter can actually increase your pain tolerance by triggering the release of endorphins, the body's natural feel-good chemicals, in the brain.", "image": "laughter_pain.png"},
    {"text": "Despite its widespread use in medicine for decades, the precise mechanisms of how general anesthesia works to induce unconsciousness remain surprisingly not fully understood by science.", "image": "anesthesia_mystery.png"},
    {"text": "Those tiny bumps on your skin? Goosebumps are a fascinating evolutionary leftover, a reflex inherited from our hairier ancestors used to raise fur for insulation or intimidation.", "image": "goosebumps_reflex.png"},
    {"text": "You're vastly outnumbered inside! Your gut microbiome hosts more individual bacterial cells than there are human cells comprising your entire body, playing vital roles in overall health.", "image": "gut_bacteria.png"},
    {"text": "A rare condition known as Superior Canal Dehiscence Syndrome allows some individuals to actually hear internal body sounds, such as their own eyeballs moving within their sockets.", "image": "eyeball_hearing.png"},
    {"text": "Why do we yawn? One leading theory suggests yawning might function as a natural thermostat, helping to cool down an overheating brain by increasing blood flow and air intake.", "image": "yawning_brain_cool.png"},
    {"text": "There's a physiological basis for connection: Studies show that when people hold hands or gaze into each other's eyes for a period, their heartbeats can actually synchronize.", "image": "heartbeat_sync.png"},
    {"text": "Over an average lifetime, you'll shed approximately 40 pounds (around 18kg) of dead skin cells. Much of the common household dust is actually composed of this sloughed-off skin.", "image": "skin_shedding.png"},
    {"text": "The brain's internal body map is powerful: Phantom limb sensations or even pain can occur in individuals born without that specific limb, demonstrating the map's innate nature.", "image": "phantom_limb.png"},
    {"text": "The liver possesses an incredible regenerative capacity. It's capable of regrowing back to its full, original size even if only 25% of the healthy tissue remains after damage or surgery.", "image": "liver_regrowth.png"},
    {"text": "Believe it or not, humans actually emit a faint glow through natural bioluminescence! However, this light is approximately 1,000 times weaker than what the unaided human eye is capable of detecting.", "image": "human_glow.png"},
    {"text": "You experience a slight height change daily! You're typically taller just after waking up because the cartilage discs in your spine gradually compress under gravity throughout the day.", "image": "spine_compression.png"},
    {"text": "Fibrodysplasia Ossificans Progressiva, sometimes called 'Stone Man Syndrome,' is an extremely rare genetic condition where injured muscle and connective tissue gradually ossify, turning into solid bone over time.", "image": "stone_man_syndrome.png"}
]

# --- Jura Fakten Liste ---
LAW_FACTS = [
    {"text": "The word 'lawyer' comes from the Middle English 'lawe,' meaning 'that which is laid down,' highlighting how laws were seen as fixed foundations of society.", "image": "lawyer_etymology.png"},
    {"text": "The first-year law curriculum is notoriously intense; it's designed less to teach content and more to train the mind to 'think like a lawyer.'", "image": "think_like_a_lawyer.png"},
    {"text": "Some students experience 'law school syndrome' — jokingly believing they have every legal condition they study, similar to medical student syndrome.", "image": "law_school_syndrome.png"},
    {"text": "Legal language, often mocked for being confusing, is intentionally precise, as small word choices can completely change a statute's interpretation.", "image": "legal_language_precision.png"},
    {"text": "The scales of justice, a symbol recognized globally, date back to ancient Egypt, representing the weighing of truth and fairness before the gods.", "image": "scales_of_justice.png"},
    {"text": "The adversarial system, where two sides argue before a neutral judge, is based on the belief that truth emerges from conflict, not harmony.", "image": "adversarial_system.png"},
    {"text": "In legal philosophy, a core debate exists between natural law (law based on morality) and legal positivism (law based on human-made rules).", "image": "natural_law_positivism.png"},
    {"text": "The phrase 'ignorance of the law is no excuse' exists in most legal systems, even though no one can possibly know all the laws that apply to them.", "image": "ignorance_no_excuse.png"},
    {"text": "Many of the world's influential legal systems, from civil law to common law, ultimately trace their roots back to Roman law.", "image": "roman_law_roots.png"},
    {"text": "The Latin phrases still used in modern law—like habeas corpus or mens rea—survive from medieval times, when Latin was the universal language of educated discourse.", "image": "latin_in_law.png"},
    {"text": "The first recorded 'law school' dates back to ancient Rome around 450 BCE, when the Twelve Tables were taught as the foundation of Roman law.", "image": "roman_law_school.png"},
    {"text": "Most legal disputes never reach a courtroom; the vast majority are settled privately through negotiation or mediation.", "image": "private_settlement.png"},
    {"text": "There's a famous saying in legal circles: 'Hard cases make bad law,' meaning emotionally charged cases often lead to poor general rules.", "image": "hard_cases_bad_law.png"},
    {"text": "In France, it is illegal to name a pig 'Napoleon' out of respect for the famous emperor.", "image": "napoleon_pig_law.png"},
    {"text": "In Samoa, it's illegal to forget your wife's birthday—a law meant to protect marital harmony.", "image": "samoa_birthday_law.png"},
    {"text": "The United States has more lawyers than any other country—roughly 1.3 million—which means about one lawyer for every 240 people.", "image": "usa_lawyer_count.png"},
    {"text": "In ancient Greece, lawyers didn't exist; citizens had to represent themselves in court, though they could hire speechwriters to craft their arguments.", "image": "ancient_greece_law.png"},
    {"text": "International law technically lacks a global 'police force'; compliance depends largely on mutual agreement and political pressure.", "image": "international_law.png"},
    {"text": "Lawyers are sometimes called 'professional pessimists,' as their job is to imagine every possible way something could go wrong to protect their clients.", "image": "professional_pessimist.png"},
    {"text": "The correct answer to almost any complex legal question is: 'It depends.'", "image": "it_depends.png"},
    {"text": "Many famous revolutions, from the American to the French, began not with weapons but with legal arguments about rights and legitimacy.", "image": "legal_revolutions.png"},
    {"text": "The phrase 'law and order' is misleading—in reality, law often creates conflict before it restores order, since every rule can be challenged or reinterpreted.", "image": "law_conflict_order.png"},
    {"text": "Law students often spend more time reading cases than attending lectures—a single case can run dozens of pages, filled with historical reasoning.", "image": "case_law_reading.png"},
    {"text": "In South Korea, law students may study for up to 20 hours a day before bar exams, preparing for years before even sitting the test.", "image": "south_korea_bar_exam.png"},
    {"text": "The shortest U.S. Supreme Court decision ever written contained only one word: 'Affirmed.' It meant the lower court's decision stood.", "image": "shortest_scotus_decision.png"},
    {"text": "In China, law students must study Marxist legal theory as part of their curriculum, as it is a foundation for the country's legal philosophy.", "image": "china_marxist_law.png"}
]

# --- Allgemeine Fakten Liste ---
GENERAL_FACTS = [
    {"text": "If you could remove all the empty space inside atoms, the entire human race would fit into a sugar cube.", "image": "sugar_cube_humanity.png"},
    {"text": "Sloths can hold their breath longer than dolphins — up to 40 minutes — by slowing their heart rate.", "image": "sloth_breath.png"},
    {"text": "The average cloud weighs around one million pounds, but floats because the air below it is even heavier.", "image": "cloud_weight.png"},
    {"text": "There are more trees on Earth than stars in the Milky Way — roughly three trillion versus 100–400 billion.", "image": "trees_vs_stars.png"},
    {"text": "A single strand of spider silk, if scaled up to the thickness of a pencil, could stop a passenger plane in flight.", "image": "spider_silk_plane.png"},
    {"text": "In Antarctica, there's a waterfall that runs red as blood — it's actually caused by oxidized iron in saltwater.", "image": "blood_falls_antarctica.png"},
    {"text": "Time passes slightly faster at your head than at your feet — thanks to Einstein's theory of relativity and gravity's effect on time.", "image": "time_relativity.png"},
    {"text": "Bananas are berries, but strawberries aren't — botanically speaking.", "image": "banana_berry.png"},
    {"text": "Wombat poop is cube-shaped, so it doesn't roll away and can be used to mark territory.", "image": "wombat_cube_poop.png"},
    {"text": "Octopuses have three hearts and blue blood; two hearts pump to the gills, one to the rest of the body.", "image": "octopus_hearts.png"},
    {"text": "Cleopatra lived closer in time to the invention of the iPhone than to the construction of the Great Pyramid.", "image": "cleopatra_iphone.png"},
    {"text": "There are more possible ways to shuffle a deck of cards than there are atoms on Earth.", "image": "card_shuffle.png"},
    {"text": "Sharks existed before trees did — by about 50 million years.", "image": "shark_before_trees.png"},
    {"text": "In theory, if you could fold a piece of paper 42 times, it would reach the Moon.", "image": "paper_fold_moon.png"},
    {"text": "The Eiffel Tower grows taller in summer; heat expands the metal by about 15 centimeters.", "image": "eiffel_tower_summer.png"},
    {"text": "Honey never spoils — archaeologists have found 3,000-year-old honey that's still edible.", "image": "honey_never_spoils.png"},
    {"text": "A day on Venus is longer than a year on Venus — it rotates so slowly that it spins once per orbit.", "image": "venus_day_year.png"},
    {"text": "The fingerprints of koalas are so similar to humans' that they've confused crime scene investigators.", "image": "koala_fingerprint.png"},
    {"text": "You can't hum while holding your nose closed — try it, it's impossible.", "image": "hum_nose.png"},
    {"text": "Some turtles can breathe through their rear ends during hibernation — it's called cloacal respiration.", "image": "turtle_breathe_rear.png"},
    {"text": "There's enough DNA in your body to stretch from the Sun to Pluto and back — 17 times.", "image": "dna_stretch.png"},
    {"text": "A teaspoon of neutron star material would weigh about six billion tons.", "image": "neutron_star_weight.png"},
    {"text": "The shortest war in history was between Britain and Zanzibar in 1896 — it lasted 38 minutes.", "image": "shortest_war.png"},
    {"text": "Cows have best friends and get stressed when they're separated.", "image": "cow_friends.png"},
    {"text": "Space smells like seared steak — astronauts report the odor comes from dying stars and cosmic dust.", "image": "space_smell.png"}
]

# --- Countries / Sprachen Fakten Liste ---
COUNTRY_FACTS = [
    {"text": "Did you know? Papua New Guinea is the most linguistically diverse country on Earth. With over 800 indigenous languages, it houses roughly 12% of the world's languages despite its small population.", "image": "png_languages.png"},
    {"text": "A musical masterpiece: South Africa's national anthem is globally unique. Its lyrics seamlessly switch between five of the country's twelve official languages: Xhosa, Zulu, Sesotho, Afrikaans, and English.", "image": "south_africa_anthem.png"},
    {"text": "A touch of antiquity: Because Latin is the official language of the Catholic Church, Vatican City is the only country in the world offering ATMs with a Latin language interface.", "image": "vatican_atm_latin.png"},
    {"text": "A matter of perception: Historically, Japan used only one word ('ao') for both blue and green. Due to this linguistic quirk, Japanese traffic lights often illuminate in a distinct blue instead of green.", "image": "japan_blue_traffic_lights.png"},
    {"text": "A record holder for inclusion: Bolivia holds the world record for the most official languages. Alongside Spanish, the country's constitution recognizes a staggering 36 indigenous languages as completely equal.", "image": "bolivia_official_languages.png"},
    {"text": "A linguistic quirk: The Irish language (Gaeilge) has no direct words for 'yes' or 'no'. Instead, you answer by repeating the question's verb in either a positive or negative form.", "image": "irish_yes_no.png"},
    {"text": "An artificial alphabet: The Korean script, Hangul, didn't evolve naturally; it was invented in 1443. The letter shapes ingeniously mimic the anatomical positions of your tongue and lips when speaking.", "image": "hangul_invention.png"},
    {"text": "Whistling instead of speaking: On the Canary Island of La Gomera, locals communicate across vast valleys using 'Silbo Gomero'—a fully whistled version of Spanish that translates vowels and consonants into tones.", "image": "silbo_gomero_whistling.png"},
    {"text": "Absolute orientation: The Australian Aboriginal language Guugu Yimithirr lacks words for 'left' or 'right'. Speakers use only cardinal directions, giving them an incredibly precise internal compass from birth.", "image": "aboriginal_compass.png"},
    {"text": "Strict naming rules: In Iceland, you can't just pick any name for a child. A government Naming Committee strictly reviews new names to ensure they follow traditional Icelandic grammatical rules.", "image": "iceland_naming_committee.png"},
    {"text": "It's astounding: Mandarin Chinese doesn't use a standard alphabet, but rather thousands of individual characters. To fluently read a daily newspaper, you must memorize approximately 3,000 of these logograms.", "image": "chinese_characters.png"},
    {"text": "Historical irony: Despite being linguistic rivals today, French was actually the official language of the English royal court and nobility for nearly 300 years following the Norman Conquest in 1066.", "image": "french_english_court.png"},
    {"text": "Living in the present: The Finnish language completely lacks a grammatical future tense. Finns simply use the present tense for future events, relying entirely on conversational context to establish the timeframe.", "image": "finnish_no_future.png"},
    {"text": "Mind your punctuation: When writing a question in Greek, don't use a standard question mark. The official Greek question mark actually looks exactly like an English semicolon (;).", "image": "greek_question_mark.png"},
    {"text": "An absolute mystery: Euskara, spoken by the Basque people in Spain and France, is a language isolate. It has absolutely no known genealogical relationship to any other living language on Earth.", "image": "basque_language_isolate.png"},
    {"text": "A singing culture: In the Indian village of Kongthong, residents don't use regular names. Instead, every person is assigned a unique melody composed by their mother, which is whistled to call them.", "image": "india_whistling_village.png"},
    {"text": "A completely different worldview: The Pirahã people of the Brazilian Amazon speak a language entirely lacking words for exact numbers or specific colors, relying only on concepts like 'few' or 'many'.", "image": "piraha_numbers.png"},
    {"text": "A historical misunderstanding: The name 'Canada' stems from an explorer's mistake. He wrongly believed the Iroquoian word 'kanata'—which simply means 'village' or 'settlement'—was the specific name for the entire country.", "image": "canada_name_origin.png"},
    {"text": "A surprising greeting: The famous word 'Ciao', used today in Italian for both 'hello' and 'goodbye', originated in the Venetian dialect where it literally translated to 'I am your slave'.", "image": "ciao_etymology.png"},
    {"text": "Culture encoded in law: The Kingdom of Bhutan measures national success by 'Gross National Happiness' rather than GDP. This Buddhist-inspired concept is officially enshrined directly in the country's constitution.", "image": "bhutan_national_happiness.png"},
    {"text": "A cartographical tongue-twister: The Welsh village of 'Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch' holds the record for Europe's longest place name. It meticulously describes the precise geographic location of the local parish church.", "image": "wales_long_name.png"},
    {"text": "A mark of inclusion: In 2006, New Zealand became the very first country in the world to make its national sign language (NZSL) an official state language, alongside English and Māori.", "image": "nz_sign_language.png"},
    {"text": "Unique in typography: The letter 'ß' (Eszett) exists exclusively in written German. Interestingly, it isn't even used in German-speaking Switzerland, where writers consistently use a double 'ss' instead.", "image": "german_eszett.png"},
    {"text": "No federal official language: Despite having the world's largest Spanish-speaking population, Spanish isn't Mexico's federal official language. Instead, 68 indigenous languages are recognized as co-equal national languages alongside it.", "image": "mexico_no_official_language.png"},
    {"text": "Linguistic distance: Despite being in Central Europe, Hungarian belongs to the Uralic language family. Distantly related to Finnish, it is completely incomprehensible to all of Hungary's direct geographical neighbors.", "image": "hungarian_uralic_language.png"}
]


def todays_fact(fact_theme: str = "Medical") -> str:
    """Only the text of today's fact (the side panel shows it without a picture)."""
    if fact_theme == "Random":
        facts = MEDICAL_FACTS + LAW_FACTS + GENERAL_FACTS + COUNTRY_FACTS
    else:
        facts = {"Law": LAW_FACTS, "General": GENERAL_FACTS, "Countries": COUNTRY_FACTS}.get(fact_theme, MEDICAL_FACTS)
    if not facts:
        return ""
    if fact_theme == "Random":
        seed = str(date.today().toordinal()).encode("ascii")
        index = int(hashlib.sha256(seed).hexdigest(), 16) % len(facts)
    else:
        index = (date.today().timetuple().tm_yday - 1) % len(facts)
    text = facts[index].get("text", "")
    return _(text) if text else ""

