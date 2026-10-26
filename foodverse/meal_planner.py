"""Database-free meal-planning helpers."""
ACTIVITY={"Sedentary":1.2,"Lightly active":1.375,"Moderately active":1.55,"Very active":1.725,"Extra active":1.9}
MEALS=[("Overnight oats with berries and seeds","Lentil and roasted vegetable bowl","Tofu stir-fry with brown rice","Apple with nut butter"),("Spinach mushroom omelette with toast","Chickpea cucumber salad with pita","Salmon, potatoes, and greens","Yogurt with fruit"),("Greek yogurt, banana, and oats","Black bean quinoa bowl","Chicken or tempeh fajita bowl","Carrots and hummus"),("Avocado toast with eggs or tofu","Tomato white bean soup","Vegetable curry with rice","Pear and pumpkin seeds"),("Chia pudding with fruit","Soba noodle edamame salad","Stuffed peppers with beans","Cottage cheese or soy yogurt"),("Peanut butter banana oats","Roasted vegetable and hummus wrap","Turkey or lentil meatballs with pasta","Orange and almonds"),("Savory tofu scramble","Lentil tabbouleh bowl","Sheet-pan vegetables with chickpeas","Berries and yogurt")]
def calculate_targets(age:int,gender:str,weight:float,height:int,activity:str,goal:str)->dict[str,int]:
    # Mifflin–St Jeor uses binary constants; individual needs vary.
    bmr=round(10*weight+6.25*height-5*age+(5 if gender=="Male" else -161));tdee=round(bmr*ACTIVITY.get(activity,1.2));return {"bmr":bmr,"tdee":tdee,"calories":max(1200,tdee+{"Fat loss":-400,"Muscle gain":250}.get(goal,0))}
def build_week(calories:int,diets:list[str])->list[dict[str,str]]:
    out=[]
    for i,(bf,lu,di,sn) in enumerate(MEALS):
        if "Vegan" in diets or "Vegetarian" in diets:
            bf=bf.replace("eggs","tofu").replace("Greek yogurt","soy yogurt").replace("Cottage cheese","soy yogurt");di=di.replace("Salmon","crispy tofu").replace("Chicken","tempeh").replace("Turkey","lentil");sn=sn.replace("yogurt","plant yogurt")
        if "Gluten-free" in diets: lu=lu.replace("pita","rice").replace("wrap","lettuce cups").replace("Soba noodles","rice noodles")
        if "Dairy-free" in diets: bf=bf.replace("Greek yogurt","soy yogurt").replace("yogurt","soy yogurt");sn=sn.replace("Yogurt","Soy yogurt").replace("yogurt","soy yogurt").replace("Cottage cheese","soy yogurt")
        if "Keto" in diets: bf,lu,di,sn="Egg or tofu scramble with avocado and spinach","Leafy greens with avocado, seeds, and protein","Roasted non-starchy vegetables with tofu or fish","Olives and a small handful of nuts"
        if "Diabetic-friendly" in diets: sn="Pair a small fruit portion with nuts or unsweetened yogurt"
        out.append({"day":f"Day {i+1}","breakfast":bf,"lunch":lu,"dinner":di,"snack":sn})
    return out
def grocery_list(week:list[dict[str,str]],diets:list[str]|None=None)->list[str]:
    """Return a diet-aware starter list matched to the built-in weekly menu."""
    diets=diets or []
    items=["Oats","Berries and seasonal fruit","Leafy greens","Tomatoes","Onions and garlic","Lentils and chickpeas","Beans","Tofu or preferred protein","Rice or quinoa","Potatoes","Mushrooms","Bell peppers","Carrots and cucumber","Nuts and seeds","Olive oil, herbs, and spices"]
    items.append("Plant yogurt" if "Dairy-free" in diets or "Vegan" in diets else "Yogurt or plant yogurt")
    items.extend(["Gluten-free bread","Rice noodles"] if "Gluten-free" in diets else ["Whole-grain bread or pita","Pasta or soba noodles"])
    if "Keto" in diets: items.extend(["Avocados","Low-carbohydrate vegetables","Olives"])
    if not any(d in diets for d in ["Vegan","Vegetarian"]): items.append("Eggs, fish, or poultry (optional)")
    return items
