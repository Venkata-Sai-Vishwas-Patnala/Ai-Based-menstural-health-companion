from datetime import date

PHASE_RULES = {
    "menstrual": {
        "days_range": (1, 5),
        "description": "Your body is shedding the uterine lining. Focus on replenishing lost nutrients.",
        "foods": [
            {"name": "Spinach & lentils", "reason": "High iron — replenishes blood loss"},
            {"name": "Ginger & turmeric tea", "reason": "Anti-inflammatory, reduces cramps"},
            {"name": "Dark chocolate (70%+)", "reason": "Magnesium — eases muscle cramps"},
            {"name": "Oranges & bell peppers", "reason": "Vitamin C — boosts iron absorption"},
            {"name": "Watermelon & cucumber", "reason": "Hydrating, reduces bloating"},
            {"name": "Salmon & sardines", "reason": "Omega-3 — reduces prostaglandins (cramp triggers)"},
        ],
        "avoid": [
            {"name": "Salty snacks", "reason": "Worsens bloating and water retention"},
            {"name": "Caffeine", "reason": "Constricts blood vessels, intensifies cramps"},
            {"name": "Alcohol", "reason": "Increases inflammation and dehydration"},
            {"name": "Red meat in excess", "reason": "High saturated fat increases prostaglandins"},
        ],
        "supplements": ["Iron", "Magnesium", "Vitamin C", "Omega-3"],
        "hydration": "Aim for 2.5L water/day. Herbal teas (ginger, chamomile) count.",
        "tips": "Rest is important. Warm foods and drinks help relax uterine muscles.",
        "energy_level": "low",
        "exercise": "Light yoga, walking, gentle stretching",
    },
    "follicular": {
        "days_range": (6, 13),
        "description": "Estrogen is rising. Your energy and mood are improving — great time to build healthy habits.",
        "foods": [
            {"name": "Flaxseeds & soy", "reason": "Phytoestrogens — support rising estrogen"},
            {"name": "Eggs & chicken", "reason": "Lean protein — supports follicle development"},
            {"name": "Quinoa & oats", "reason": "Complex carbs — sustained energy"},
            {"name": "Pumpkin seeds", "reason": "Zinc — supports hormone production"},
            {"name": "Yogurt & kefir", "reason": "Probiotics — gut health affects hormones"},
            {"name": "Broccoli & cauliflower", "reason": "DIM compound — helps metabolise estrogen"},
        ],
        "avoid": [
            {"name": "Excess sugar", "reason": "Spikes insulin, disrupts estrogen balance"},
            {"name": "Refined carbs", "reason": "Causes energy crashes"},
        ],
        "supplements": ["B vitamins", "Zinc", "Probiotics", "Vitamin D"],
        "hydration": "Aim for 2L water/day. Green smoothies are excellent.",
        "tips": "Energy is rising — great time to try new foods and meal prep.",
        "energy_level": "medium-high",
        "exercise": "Cardio, strength training, HIIT",
    },
    "ovulation": {
        "days_range": (14, 16),
        "description": "Peak estrogen and LH surge. You are at your highest energy and most fertile.",
        "foods": [
            {"name": "Berries & pomegranate", "reason": "Antioxidants — protect egg quality"},
            {"name": "Avocado & olive oil", "reason": "Healthy fats — support hormone synthesis"},
            {"name": "Asparagus & leafy greens", "reason": "Folate — essential for cell health"},
            {"name": "Oysters & pumpkin seeds", "reason": "Zinc — supports ovulation"},
            {"name": "Bananas & salmon", "reason": "Vitamin B6 — hormone regulation"},
            {"name": "Lentils & chickpeas", "reason": "Plant protein + fiber — hormone balance"},
        ],
        "avoid": [
            {"name": "Heavy fried meals", "reason": "Slows digestion, causes sluggishness"},
            {"name": "Excess alcohol", "reason": "Disrupts LH surge and ovulation timing"},
        ],
        "supplements": ["Folate", "Zinc", "Vitamin B6", "CoQ10"],
        "hydration": "Aim for 2L water/day. Coconut water is great for electrolytes.",
        "tips": "Peak energy phase — eat light, colourful, nutrient-dense meals.",
        "energy_level": "high",
        "exercise": "High-intensity workouts, running, cycling",
    },
    "luteal": {
        "days_range": (17, 28),
        "description": "Progesterone rises then drops. PMS symptoms may appear in the second half.",
        "foods": [
            {"name": "Turkey & tuna", "reason": "Vitamin B6 — supports progesterone production"},
            {"name": "Dairy, almonds & broccoli", "reason": "Calcium — reduces PMS mood symptoms by 48%"},
            {"name": "Dark chocolate & leafy greens", "reason": "Magnesium — reduces bloating and anxiety"},
            {"name": "Brown rice & sweet potato", "reason": "Complex carbs — stabilise serotonin levels"},
            {"name": "Walnuts & chia seeds", "reason": "Omega-3 — reduces inflammation and mood swings"},
            {"name": "Chamomile & peppermint tea", "reason": "Calming, reduces bloating"},
        ],
        "avoid": [
            {"name": "Caffeine", "reason": "Worsens anxiety, breast tenderness, and sleep issues"},
            {"name": "Alcohol", "reason": "Depletes B vitamins, worsens mood swings"},
            {"name": "High-sodium foods", "reason": "Increases water retention and bloating"},
            {"name": "Refined sugar", "reason": "Causes blood sugar crashes, worsens mood"},
        ],
        "supplements": ["Magnesium", "Calcium", "Vitamin B6", "Evening Primrose Oil"],
        "hydration": "Aim for 2.5L water/day. Reduce caffeine, increase herbal teas.",
        "tips": "Prioritise sleep and stress management. Magnesium before bed helps with sleep and cramps.",
        "energy_level": "medium-low",
        "exercise": "Pilates, yoga, light strength training, walking",
    },
}


def get_cycle_phase(cycle_day: int) -> str:
    if cycle_day <= 5:
        return "menstrual"
    elif cycle_day <= 13:
        return "follicular"
    elif cycle_day <= 16:
        return "ovulation"
    else:
        return "luteal"


def get_diet_for_phase(phase: str) -> dict:
    return PHASE_RULES.get(phase, PHASE_RULES["follicular"])


def calculate_cycle_day(last_period_start: date, today: date = None) -> int:
    today = today or date.today()
    delta = (today - last_period_start).days
    return max(1, (delta % 28) + 1)
