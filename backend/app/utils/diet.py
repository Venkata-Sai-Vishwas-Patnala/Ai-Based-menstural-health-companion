from copy import deepcopy
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
        "remedies": [
            "Use a heating pad on the lower abdomen for 15–20 minutes to reduce cramps.",
            "Drink ginger or chamomile tea to ease inflammation and discomfort.",
            "Take a gentle walk or do light stretching to help bloating and stiffness.",
            "Keep hydration high and rest when your energy dips.",
        ],
        "suggestions": [
            "Focus on iron-rich meals and warm liquids to support blood replenishment.",
            "Avoid salty, highly processed foods that worsen bloating and fluid retention.",
            "Consider a lower-intensity routine today to protect your energy and rest capacity.",
        ],
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
        "remedies": [
            "Use this phase to prioritise movement and sleep routine consistency.",
            "Try a high-protein breakfast to support stable energy and focus.",
            "Gentle outdoor activity can help lift mood and motivation.",
            "Keep meals balanced with complex carbs, protein, and vegetables.",
        ],
        "suggestions": [
            "This is a strong time for workouts, meal planning, and healthy routines.",
            "Keep sugar and ultra-processed snacks low so energy stays stable.",
            "Pair exercise with enough protein and hydration for recovery.",
        ],
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
        "remedies": [
            "Take advantage of your higher energy with movement you enjoy.",
            "Choose colorful, nutrient-dense meals to support energy and recovery.",
            "Keep your routine simple so you can stay hydrated and focused.",
            "Use this phase for social plans, training, and creative work.",
        ],
        "suggestions": [
            "Your energy is likely at its best — maintain hydration and stable meals.",
            "Avoid heavy, greasy meals if you feel sluggish or bloated.",
            "Track any pelvic sensitivity or cervical mucus changes to understand your cycle.",
        ],
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
        "remedies": [
            "Reduce caffeine and alcohol to limit mood swings and breast tenderness.",
            "Take a warm bath or use a heating pad to ease cramps and tension.",
            "Aim for an earlier bedtime and reduce overstimulation when your mood dips.",
            "Keep a simple magnesium-rich snack like dark chocolate or nuts nearby.",
        ],
        "suggestions": [
            "This is a good time to prioritise sleep, rest, and gentle movement.",
            "Keep blood sugar steady with protein-rich meals and low-sugar snacks.",
            "Track irritability, bloating, and sleep quality to understand your PMS pattern.",
        ],
    },
}

PHASE_VARIANTS = {
    "menstrual": [
        {"name": "Iron Recovery Plate", "foods": [{"name": "Spinach + lentil bowl", "reason": "Iron-rich and gentle on digestion during heavy bleeding."}, {"name": "Citrus salad", "reason": "Vitamin C helps absorb iron and supports your energy."}, {"name": "Ginger tea", "reason": "Anti-inflammatory and helps ease cramps."}]},
        {"name": "Hydration & Calm Plate", "foods": [{"name": "Watermelon-cucumber bowl", "reason": "Hydration reduces bloating and helps with fluid balance."}, {"name": "Salmon with quinoa", "reason": "Omega-3s help calm inflammation and cramping."}, {"name": "Chamomile tea", "reason": "Soothing and supportive when you feel tense or restless."}]},
        {"name": "Warm Comfort Plate", "foods": [{"name": "Tofu & spinach stir-fry", "reason": "Plant protein plus iron supports recovery without heavy meals."}, {"name": "Roasted sweet potato", "reason": "Gentle carbs restore energy and keep you stable."}, {"name": "Turmeric oat porridge", "reason": "Warm and anti-inflammatory for cramps and fatigue."}]},
        {"name": "Low-Effort Recovery Plate", "foods": [{"name": "Eggs + avocado toast", "reason": "Protein and healthy fats ease energy dips without being too heavy."}, {"name": "Bell peppers", "reason": "Vitamin C helps with iron absorption and skin health."}, {"name": "Warm herbal tea", "reason": "Comforting and useful when you want a lower-intensity rhythm."}]},
        {"name": "Cramps Relief Plate", "foods": [{"name": "Salmon rice bowl", "reason": "Omega-3s and complex carbs help fight inflammation and fatigue."}, {"name": "Dark chocolate", "reason": "Magnesium can help ease muscle cramps."}, {"name": "Cucumber mint water", "reason": "Improves hydration and reduces bloating."}]},
        {"name": "Blood Support Plate", "foods": [{"name": "Beetroot + spinach salad", "reason": "Nutrients support circulation and iron replenishment."}, {"name": "Yogurt with berries", "reason": "Protein plus antioxidants support recovery and hydration."}, {"name": "Peppermint tea", "reason": "Soothing for belly discomfort and bloating."}]},
        {"name": "Easy Digestive Plate", "foods": [{"name": "Rice porridge with pumpkin", "reason": "Gentle, digestible, and energy-friendly during heavier days."}, {"name": "Lentil soup", "reason": "Protein and iron help support blood loss recovery."}, {"name": "Orange slices", "reason": "Boosts iron absorption and vitamin C intake."}]},
        {"name": "Rest-Friendly Plate", "foods": [{"name": "Oatmeal with berries", "reason": "Supports steady energy while keeping the stomach settled."}, {"name": "Tofu and greens", "reason": "Iron and protein help with low energy and fatigue."}, {"name": "Herbal tea", "reason": "Gentle and calming during rest-heavy days."}]},
        {"name": "Ginger Recovery Plate", "foods": [{"name": "Ginger chicken soup", "reason": "Warm, comforting, and useful if you feel crampy or drained."}, {"name": "Steamed greens", "reason": "Iron and folate help replenish nutrients lost during bleeding."}, {"name": "Pear slices", "reason": "Hydration plus fiber help with comfort."}]},
        {"name": "Iron Boost Plate", "foods": [{"name": "Lentil quinoa salad", "reason": "Combines iron, fiber, and plant protein for recovery."}, {"name": "Kiwi fruit", "reason": "Vitamin C helps with better iron use."}, {"name": "Ginger tea", "reason": "Helps calm the stomach and reduce cramping."}]},
        {"name": "AIPanish Plate", "foods": [{"name": "Soft scrambled eggs", "reason": "Easy protein when appetite is low and you need gentle energy."}, {"name": "Spinach with mushrooms", "reason": "Nutrients support iron and recovery."}, {"name": "Warm broth", "reason": "Hydrating and soothing when you feel weak."}]},
        {"name": "Smooth Recovery Plate", "foods": [{"name": "Berry smoothie with spinach", "reason": "Quick nutrients and iron support when you need a light meal."}, {"name": "Banana with yogurt", "reason": "Easy energy and protein without heavy digestion."}, {"name": "Peppermint tea", "reason": "Calms the stomach and reduces belly pressure."}]}
    ],
    "follicular": [
        {"name": "Energy Lift Plate", "foods": [{"name": "Eggs + quinoa bowl", "reason": "Protein and slow carbs help lift energy and support follicle development."}, {"name": "Blueberries", "reason": "Antioxidants support reduced stress and better recovery."}, {"name": "Green tea", "reason": "Light hydration and steady focus without the caffeine spike."}]},
        {"name": "Estrogen Support Plate", "foods": [{"name": "Soy yogurt with flaxseeds", "reason": "Phytoestrogens and fiber support estrogen balance."}, {"name": "Chicken and greens", "reason": "Lean protein helps with muscle repair and hormone support."}, {"name": "Cucumber-water infusion", "reason": "Hydration supports your overall energy and metabolism."}]},
        {"name": "High-Output Plate", "foods": [{"name": "Oatmeal with pumpkin seeds", "reason": "Complex carbs and zinc support steady energy and hormone work."}, {"name": "Avocado toast", "reason": "Healthy fats and fiber support fullness and balanced energy."}, {"name": "Orange slices", "reason": "Vitamin C supports skin and immune function."}]},
        {"name": "Focus Fuel Plate", "foods": [{"name": "Greek yogurt bowl", "reason": "Protein helps with satiety and stable focus."}, {"name": "Broccoli and quinoa", "reason": "Fiber and phytonutrients support estrogen metabolism."}, {"name": "Herbal infusion", "reason": "Gentle hydration and calm energy during busy days."}]},
        {"name": "Workout Ready Plate", "foods": [{"name": "Chicken rice bowl", "reason": "Lean protein and carbs support training recovery."}, {"name": "Roasted carrots", "reason": "Vitamin-rich and easy to digest before movement."}, {"name": "Coconut water", "reason": "Electrolytes help support your active phase."}]},
        {"name": "Mood Lift Plate", "foods": [{"name": "Kefir + berries", "reason": "Probiotics support gut health, which connects closely to mood."}, {"name": "Egg white omelet", "reason": "Low-fat protein supports stable energy."}, {"name": "Pear slices", "reason": "Fiber and hydration help support digestive comfort."}]},
        {"name": "Meal Prep Plate", "foods": [{"name": "Lentil salad", "reason": "Iron, fiber, and steady energy keep your body grounded."}, {"name": "Roasted vegetables", "reason": "Supports hormone metabolism and nutrient intake."}, {"name": "Green smoothie", "reason": "A quick nutrient-dense option for busy days."}]},
        {"name": "Balanced Stability Plate", "foods": [{"name": "Chickpea bowl", "reason": "Protein and fiber help maintain stable blood sugar."}, {"name": "Tomato-cucumber salad", "reason": "Hydrating and full of antioxidants."}, {"name": "Dark chocolate square", "reason": "Magnesium and a small treat can support overall wellness."}]},
        {"name": "Cleansing Plate", "foods": [{"name": "Smoothie with spinach", "reason": "Easy nutrient density and support for estrogen clearance."}, {"name": "Turkey wrap", "reason": "Protein helps keep fullness and energy stable."}, {"name": "Herbal iced tea", "reason": "Great for afternoon hydration without excess caffeine."}]},
        {"name": "Lean Energy Plate", "foods": [{"name": "Oats with chia", "reason": "Long-lasting carbs and omega-3s help maintain energy."}, {"name": "Grilled fish", "reason": "High-quality protein and fats support hormone function."}, {"name": "Cabbage slaw", "reason": "Fiber and micronutrients support digestion and detox support."}]},
        {"name": "Zinc Support Plate", "foods": [{"name": "Pumpkin seeds + yogurt", "reason": "Zinc and protein support hormone production and satiety."}, {"name": "Brown rice bowl", "reason": "Steady energy and good fiber balance."}, {"name": "Herbal tea", "reason": "Helps you stay hydrated and keeps your routine calm."}]},
        {"name": "Gut & Hormone Plate", "foods": [{"name": "Kefir + fruit bowl", "reason": "Good probiotic source to support hormone and digestion health."}, {"name": "Grilled chicken salad", "reason": "Lean protein keeps energy and recovery steady."}, {"name": "Mint water", "reason": "Refreshes and supports hydration."}]}
    ],
    "ovulation": [
        {"name": "Peak Energy Plate", "foods": [{"name": "Salmon with greens", "reason": "Omega-3s and protein support hormone health during ovulation."}, {"name": "Berries", "reason": "Antioxidants help protect cells and support energy."}, {"name": "Coconut water", "reason": "Electrolytes help support higher activity and hydration."}]},
        {"name": "Hormone Balance Plate", "foods": [{"name": "Avocado burrito bowl", "reason": "Healthy fats support hormone production and fullness."}, {"name": "Pomegranate seeds", "reason": "Antioxidants support reproductive health and recovery."}, {"name": "Leafy greens", "reason": "Folate and minerals support cell health."}]},
        {"name": "Fertility Support Plate", "foods": [{"name": "Oysters or pumpkin seeds", "reason": "Zinc supports ovulation and reproductive hormone function."}, {"name": "Asparagus salad", "reason": "Folate and micronutrients support cell health."}, {"name": "Banana with yogurt", "reason": "Convenient source of B6 and quick energy."}]},
        {"name": "Light Energy Plate", "foods": [{"name": "Lentil quinoa bowl", "reason": "Plant protein and fiber support blood sugar while keeping energy steady."}, {"name": "Tomato and avocado salad", "reason": "Low effort, nutrient-dense, and good for digestion."}, {"name": "Lemon water", "reason": "Hydration helps you stay comfortable and energized."}]},
        {"name": "Busy Day Plate", "foods": [{"name": "Salmon rice bowl", "reason": "Balanced protein, carbs, and omega-3s for active days."}, {"name": "Chickpeas", "reason": "Fiber and plant protein support stability and fullness."}, {"name": "Citrus fruit", "reason": "Vitamin C is helpful during active, higher-output phases."}]},
        {"name": "Movement Fuel Plate", "foods": [{"name": "Chicken and sweet potato", "reason": "Carbs and lean protein support training and recovery."}, {"name": "Spinach salad", "reason": "Adds folate and minerals for cellular support."}, {"name": "Berries", "reason": "Very helpful for an antioxidant-rich, active rhythm."}]},
        {"name": "Fresh & Light Plate", "foods": [{"name": "Smoothie with banana + spinach", "reason": "Quick energy and greens for an active, lighter evening."}, {"name": "Wholegrain toast", "reason": "A simple carb source to keep energy even."}, {"name": "Herbal tea", "reason": "Hydration without extra stimulation."}]},
        {"name": "Nutrient Dense Plate", "foods": [{"name": "Avocado + salmon salad", "reason": "Healthy fats and omega-3s support hormone signalling."}, {"name": "Pomegranate", "reason": "Antioxidant support around the ovulation window."}, {"name": "Water with lemon", "reason": "Simple hydration support for high energy days."}]},
        {"name": "Balanced Recovery Plate", "foods": [{"name": "Greek yogurt bowl", "reason": "Protein and probiotics help keep digestion settled."}, {"name": "Roasted vegetables", "reason": "Fiber and minerals support hormone function."}, {"name": "Orange slices", "reason": "Vitamin C supports immunity and nutrient use."}]},
        {"name": "Glow Plate", "foods": [{"name": "Berry chia bowl", "reason": "Omega-3s, fiber, and antioxidants support fullness and wellbeing."}, {"name": "Chicken salad", "reason": "High-quality protein supports an active cycle phase."}, {"name": "Coconut water", "reason": "Electrolytes support your likely higher-output days."}]},
        {"name": "Vitality Plate", "foods": [{"name": "Tofu and bean bowl", "reason": "Plant protein and fiber help maintain steady energy."}, {"name": "Leafy greens", "reason": "Support folate and overall hormonal health."}, {"name": "Kiwi", "reason": "Vitamin C and hydration add a quick nutrient boost."}]},
        {"name": "Cycle-Boost Plate", "foods": [{"name": "Eggs with avocado", "reason": "Healthy fats and protein help support hormonal readiness."}, {"name": "Fruit salad", "reason": "Quick hydration and micronutrients without heavy digestion."}, {"name": "Green juice", "reason": "Easy way to get extra vitamins during your highest-energy phase."}]}
    ],
    "luteal": [
        {"name": "PMS Calm Plate", "foods": [{"name": "Turkey + quinoa bowl", "reason": "B6 and steady carbs support progesterone balance and mood stability."}, {"name": "Broccoli", "reason": "Calcium and fiber support PMS symptoms and digestion."}, {"name": "Chamomile tea", "reason": "Calming and useful when you feel tense or overstimulated."}]},
        {"name": "Mood Support Plate", "foods": [{"name": "Dark chocolate + nuts", "reason": "Magnesium helps with stress, mood swings, and sleep support."}, {"name": "Sweet potato", "reason": "Slow carbs help support stable mood and blood sugar."}, {"name": "Herbal tea", "reason": "Helpful when you need a gentler, lower-stress routine."}]},
        {"name": "Cramp Relief Plate", "foods": [{"name": "Salmon + brown rice", "reason": "Omega-3s and complex carbs reduce inflammation and steady energy."}, {"name": "Leafy greens", "reason": "Magnesium and calcium support muscle relaxation."}, {"name": "Peppermint tea", "reason": "Soothing for bloating and abdominal discomfort."}]},
        {"name": "Low-Sugar Stability Plate", "foods": [{"name": "Greek yogurt with walnuts", "reason": "Protein and healthy fats support stable blood sugar and mood."}, {"name": "Spinach salad", "reason": "Magnesium and fiber help reduce PMS discomfort."}, {"name": "Herbal infusion", "reason": "Hydration and calm for the evening routine."}]},
        {"name": "Sleep-Friendly Plate", "foods": [{"name": "Turkey lettuce wraps", "reason": "Lean protein supports recovery without heavy digestion."}, {"name": "Roasted potato", "reason": "Comforting carbs help you feel settled and less irritable."}, {"name": "Warm milk or herbal tea", "reason": "A calming evening option before sleep."}]},
        {"name": "Calm Energy Plate", "foods": [{"name": "Oatmeal with chia", "reason": "Fiber and omega-3s help prevent blood sugar crashes."}, {"name": "Spinach + eggs", "reason": "Protein and magnesium support mood and muscle relaxation."}, {"name": "Cinnamon tea", "reason": "Gentle and grounding for a low-stress evening."}]},
        {"name": "Bloating Ease Plate", "foods": [{"name": "Rice and lean fish", "reason": "Simple, digestible carbs and protein help when you feel bloated."}, {"name": "Cucumber salad", "reason": "Hydrating and refreshing without excess salt."}, {"name": "Ginger tea", "reason": "Supports digestion and eases bloating."}]},
        {"name": "Magnesium Boost Plate", "foods": [{"name": "Dark chocolate + almonds", "reason": "Magnesium-rich and useful during PMS or wave-like mood changes."}, {"name": "Sweet potato", "reason": "Complex carbs and micronutrients support lower stress and energy."}, {"name": "Chamomile tea", "reason": "Calming for your evening routine."}]},
        {"name": "Comfort Plate", "foods": [{"name": "Chicken soup with greens", "reason": "Warm, comforting, and easy to digest on low-energy days."}, {"name": "Brown rice", "reason": "Slow-release carbs keep mood more stable."}, {"name": "Peppermint tea", "reason": "Helpful for tension and bloating relief."}]},
        {"name": "PMS Recovery Plate", "foods": [{"name": "Salmon with quinoa", "reason": "Anti-inflammatory and rich in omega-3s for mood and cramps."}, {"name": "Broccoli and beans", "reason": "Fiber and nutrients support digestion and steady energy."}, {"name": "Warm water with lemon", "reason": "Simple hydration support for bloating and fullness."}]},
        {"name": "Balanced Mood Plate", "foods": [{"name": "Berries + yogurt", "reason": "Protein and antioxidants support steadier mood and digestion."}, {"name": "Turkey slices", "reason": "Lean protein helps keep energy from crashing."}, {"name": "Herbal tea", "reason": "Gentle hydration and calming support for late-cycle stress."}]},
        {"name": "Evening Ease Plate", "foods": [{"name": "Tofu and stir-fried greens", "reason": "Plant protein plus magnesium-rich veggies support recovery."}, {"name": "Rice cakes with nut butter", "reason": "Simple carbs and healthy fats keep blood sugar stable."}, {"name": "Warm ginger tea", "reason": "Comforting and useful for bloating or cramps."}]}
    ]
}

def _build_variant_list(phase: str, severity: int | None = None) -> list[dict]:
    variants = PHASE_VARIANTS.get(phase, PHASE_VARIANTS["follicular"])[:12]
    if severity is None:
        severity = 0
    if severity >= 7:
        return variants[:8]
    if severity >= 4:
        return variants[:10]
    return variants


def _build_phase_diet(phase: str, severity: int | None = None) -> dict:
    base_rule = deepcopy(PHASE_RULES.get(phase, PHASE_RULES["follicular"]))
    severity = max(0, min(int(severity or 0), 10))
    base_rule["severity_label"] = "low" if severity < 4 else "moderate" if severity < 8 else "high"

    if severity >= 8:
        base_rule["hydration"] = (
            f"{base_rule['hydration']} Extra hydration: sip water or electrolytes regularly and avoid dehydration triggers."
        )
        if phase == "menstrual":
            base_rule["remedies"] = [
                "Use a heating pad on the lower abdomen for 15–20 minutes to reduce cramps.",
                "Drink ginger or chamomile tea and keep your fluids high to reduce bloating.",
                "Reduce intense exercise and prioritize rest until the pain eases.",
                *base_rule.get("remedies", [])[:2],
            ]
        else:
            base_rule["remedies"] = [
                "Use a heating pad or a warm bath to ease tension and discomfort.",
                "Choose extra hydration and gentler movement while your body is under stress.",
                "Prioritize sleep and lighter meals if symptoms are flaring.",
                *base_rule.get("remedies", [])[:2],
            ]
        base_rule["suggestions"] = [
            "Ease back on intense activity and keep your routine lower-pressure today.",
            "Choose easily digestible meals and keep blood sugar stable with regular, gentle eating.",
            *base_rule.get("suggestions", [])[:2],
        ]
    elif severity >= 5:
        base_rule["hydration"] = f"{base_rule['hydration']} Try to add an extra glass of water or herbal tea this afternoon."
        base_rule["remedies"] = [
            "Keep your routine gentle and steady; rest when your body asks for it.",
            *base_rule.get("remedies", [])[:3],
        ]
        base_rule["suggestions"] = [
            "Keep meals regular and protein-rich to avoid energy dips.",
            *base_rule.get("suggestions", [])[:2],
        ]

    advice_bits = base_rule.get("suggestions", [])[:2] + base_rule.get("remedies", [])[:2]
    base_rule["daily_advice"] = " ".join(advice_bits[:4])
    base_rule["diet_variants"] = _build_variant_list(phase, severity)
    return base_rule


def get_cycle_phase(cycle_day: int) -> str:
    cycle_day = max(1, int(cycle_day))
    if cycle_day <= 5:
        return "menstrual"
    elif cycle_day <= 13:
        return "follicular"
    elif cycle_day <= 16:
        return "ovulation"
    else:
        return "luteal"


def get_diet_for_phase(phase: str, severity: int | None = None) -> dict:
    return _build_phase_diet(phase, severity)


def calculate_cycle_day(last_period_start: date, today: date = None, cycle_length: int | None = None) -> int:
    today = today or date.today()
    delta = (today - last_period_start).days
    if cycle_length and cycle_length > 0:
        return max(1, (delta % cycle_length) + 1)
    return max(1, (delta % 28) + 1)
