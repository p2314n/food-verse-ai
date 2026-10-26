"""Food Verse AI — multimodal food and kitchen intelligence demo."""
from __future__ import annotations
from typing import Any
import streamlit as st
from foodverse.ai import analyze_image, analyze_video, generate_text
from foodverse.meal_planner import build_week, calculate_targets, grocery_list
from foodverse.samples import demo_freshness, demo_hygiene, demo_nutrition, demo_recipe
st.set_page_config(page_title="Food Verse AI", page_icon="🥑", layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
.stApp{background:#f7f8f3} .block-container{padding-top:1.5rem;max-width:1320px} h1,h2,h3{font-family:Manrope,sans-serif!important;color:#172c28}
[data-testid="stSidebar"]{background:#edf3e8}.hero{background:linear-gradient(120deg,#153d32,#286c51);border-radius:24px;padding:30px 34px;color:#fff;margin:0 0 26px}.hero h1{color:white;font-size:2.3rem;margin:0 0 8px}.hero p{color:#d4e9d9;margin:0}.eyebrow{color:#d8ef73;font-weight:700;text-transform:uppercase;letter-spacing:.12em;font-size:.72rem;margin-bottom:8px}.pill{padding:5px 10px;background:#e6f3e8;color:#246449;border-radius:99px;font-size:.78rem;font-weight:700}div[data-testid="stMetric"]{background:white;border:1px solid #e6ebe3;border-radius:16px;padding:16px 18px}.stButton>button{border-radius:12px}.stButton>button[kind="primary"]{background:#1f765d;border-color:#1f765d;font-weight:700}
</style>""",unsafe_allow_html=True)
PILLARS={"🥗 Nutrition audit":"nutrition","🍓 Freshness check":"freshness","🧼 Kitchen safety":"hygiene","🍳 Recipe assistant":"recipe","📅 Meal planner":"planner"}
st.sidebar.markdown("# 🥑 Food Verse AI");st.sidebar.caption("Multimodal food intelligence");st.sidebar.markdown("---")
page=st.sidebar.radio("Explore",list(PILLARS),label_visibility="collapsed");st.sidebar.markdown("---");st.sidebar.markdown("**AI connection**")
provider=st.sidebar.selectbox("Provider",["Demo mode","Google Gemini","Groq"],index=1);api_key=""
if provider!="Demo mode":
    api_key=st.sidebar.text_input(f"{provider} API key",type="password",help="Used only for this session; not saved by the app.")
    st.sidebar.caption("Enter a key to run real analysis. It stays in session memory and is sent to the selected provider.")
st.sidebar.caption("AI food and hygiene assessments are estimates. Seek professional guidance for allergy, food-safety, or medical decisions.")
def hero(kicker,title,description): st.markdown(f'<div class="hero"><div class="eyebrow">{kicker}</div><h1>{title}</h1><p>{description}</p></div>',unsafe_allow_html=True)
def mode():
    st.caption("✨ Live AI analysis" if api_key and provider!="Demo mode" else "🧪 Demo mode — illustrative sample" if provider=="Demo mode" else "🔑 Enter your provider API key in the sidebar to run live analysis")
def model_notice(result):
    if result and result.get("_model")=="gemini-3.6-flash": st.info("Gemini 3.8 Flash was temporarily overloaded; this result was completed with Gemini 3.6 Flash.")
def vision(upload,prompt):
    if not upload: st.info("Upload an image to begin.");return None
    with st.spinner(f"Sending the image to {provider} (up to about 50 seconds)…"):
        try:
            result=analyze_image(provider,api_key,upload.getvalue(),upload.type or "image/jpeg",prompt)
            if result.get("_demo"):
                st.info("No API key connected. Showing an illustrative demo result.")
                if "health_score" in prompt: return demo_nutrition()
                if "stage" in prompt: return demo_freshness()
                if "indicators" in prompt: return demo_hygiene()
            model_notice(result)
            return result
        except Exception as exc: st.warning(f"AI analysis failed ({exc}). Check the provider and key, then try again.");return None
def nutrition():
    hero("Food Verse · 01","Know what’s on your plate.","A visual nutrition audit, from dish recognition to a practical macro snapshot.");mode();left,right=st.columns([1,1.1],gap="large")
    with left:
        photo=st.file_uploader("Upload a meal photo",type=["jpg","jpeg","png","webp"],key="meal")
        if photo: st.image(photo,width="stretch")
        context=st.text_input("Anything useful to know?",placeholder="Homemade, extra rice, dressing on the side…");go=st.button("Analyze meal",type="primary",width="stretch")
    if go:
        if not photo: st.warning("Choose a meal image first.")
        else: st.session_state.nutrition=vision(photo,"Identify visible dishes, cuisine, likely ingredients and portion; estimate serving nutrition; list likely allergens only when supported; score 1-100. Return JSON keys dish,cuisine,ingredients[],portion,nutrition{calories,protein_g,carbs_g,fat_g,fiber_g},allergens[],health_score,notes. State uncertainty; never claim hidden ingredients with certainty. Context: "+context)
    with right:
        r=st.session_state.get("nutrition")
        if not r: st.subheader("Your meal, made legible");st.write("Upload a plate photo for dish identification, macros, likely allergens, and a health score.");st.info("Photo portions and nutrition vary. Verify ingredients and labels, especially for allergies.");return
        n=r.get("nutrition",{});st.subheader(r.get("dish","Meal analysis"));st.caption(f"{r.get('cuisine','Cuisine unclear')} · Portion: {r.get('portion','not estimated')}")
        cols=st.columns(3)
        for c,label,key,unit in zip(cols,["Calories","Protein","Carbs"],["calories","protein_g","carbs_g"],["kcal","g","g"]): c.metric(label,f"{n.get(key,'—')} {unit}")
        c=st.columns(2);c[0].metric("Fat",f"{n.get('fat_g','—')} g");c[1].metric("Fiber",f"{n.get('fiber_g','—')} g")
        score=max(0,min(100,int(r.get("health_score",0) or 0)));st.markdown(f"**Health score**　<span class='pill'>{score} / 100</span>",unsafe_allow_html=True);st.progress(score/100)
        st.markdown("**Likely ingredients**");st.write(", ".join(r.get("ingredients",[])) or "Not identified");st.markdown("**Allergen flags**");st.warning(", ".join(r.get("allergens",[])) or "No obvious allergens identified; this is not an allergen guarantee.")
        if r.get("notes"): st.info(r["notes"])
        if n: st.bar_chart({"Estimated grams":{k:float(n.get(v,0) or 0) for k,v in [("Protein","protein_g"),("Carbs","carbs_g"),("Fat","fat_g"),("Fiber","fiber_g")]}})
def freshness():
    hero("Food Verse · 02","A closer look at freshness.","Check visible condition cues and get practical storage guidance.");mode();a,b=st.columns([.9,1.1],gap="large")
    with a:
        photo=st.file_uploader("Upload produce, meat, or dairy",type=["jpg","jpeg","png","webp"],key="fresh_upload");kind=st.selectbox("Food category",["Fruit or vegetables","Meat or seafood","Dairy","Other"])
        if photo: st.image(photo,width="stretch")
        go=st.button("Check visible condition",type="primary",width="stretch")
    if go:
        if not photo: st.warning("Choose an image first.")
        else: st.session_state.fresh=vision(photo,f"Assess visible discoloration, texture, wrinkling, wilting, mold for {kind}. JSON keys item,stage (Fresh|Moderately Fresh|Spoiled),action (Safe to consume|Consume within 24h|Discard immediately),cues[],storage,uncertainty. Be conservative: a photo cannot reveal smell, temperature history, or internal contamination. If uncertain recommend discarding.")
    with b:
        r=st.session_state.get("fresh")
        if not r: st.subheader("Visual clues, cautious advice");st.write("Check surface texture, discoloration, wrinkling, wilting, and visible mold.");st.warning("Do not taste food to test it. Follow food-safety guidance; discard anything with concerning odor, texture, packaging, or storage history.");return
        st.subheader(r.get("item","Condition check"));st.markdown(f"**Visible freshness**　<span class='pill'>{r.get('stage','Unclear')}</span>",unsafe_allow_html=True);action=r.get("action","Check carefully")
        (st.error if "Discard" in action else st.warning if "24h" in action else st.success)(f"**Suggested action:** {action}");st.markdown("**Visible cues**");[st.write("• "+x) for x in r.get("cues",[])];st.markdown("**Storage tip**");st.write(r.get("storage","Follow package guidance and keep perishables at a safe temperature."));st.caption(r.get("uncertainty","A photo cannot verify safety."))
def hygiene():
    hero("Food Verse · 03","See the safety signals.","A visual checklist for PPE, work surfaces, and possible cross-contamination.");mode();a,b=st.columns([.9,1.1],gap="large")
    with a:
        media=st.file_uploader("Upload a kitchen image or short video",type=["jpg","jpeg","png","webp","mp4","mov"],key="kitchen")
        if media and media.type.startswith("image"): st.image(media,width="stretch")
        elif media: st.video(media)
        go=st.button("Review visible indicators",type="primary",width="stretch")
    if go:
        if not media: st.warning("Choose an image or video first.")
        elif media.type.startswith("video"):
            with st.spinner("Sampling video frames…"):
                try: st.session_state.hygiene=analyze_video(provider,api_key,media.getvalue(),media.type,"Review visible kitchen hygiene throughout this clip. JSON keys score (0-100), indicators{hair_cover,gloves,sanitation,cross_contamination},violations[],actions[],limitations. Score visible evidence only; not regulatory compliance. Mention that a short clip may miss intermittent hazards.")
                except Exception as exc: st.warning(f"Video analysis failed ({exc}). Try a shorter clip or upload a representative image.")
        else: st.session_state.hygiene=vision(media,"Inspect visible kitchen cues: hair covering, gloves where appropriate, surface sanitation, raw poultry near ready-to-eat food or vegetables. JSON keys score (0-100), indicators{hair_cover,gloves,sanitation,cross_contamination},violations[],actions[],limitations. Score visible evidence only; not regulatory compliance.")
    with b:
        r=st.session_state.get("hygiene")
        if not r: st.subheader("A practical visual check");st.write("Review visible PPE, clean surfaces, and separation of raw and ready-to-eat food.");st.info("Gloves do not replace handwashing. Local rules determine compliance.");return
        score=max(0,min(100,int(r.get("score",0) or 0)));st.metric("Visible indicator score",f"{score}%");st.progress(score/100);st.caption("Visual screening aid, not an inspection or certification.");st.markdown("**Indicator checklist**");[st.write(f"**{k.replace('_',' ').title()}:** {v}") for k,v in r.get("indicators",{}).items()];st.markdown("**Potential violations**");[st.write("⚠️ "+x) for x in r.get("violations",[])];st.markdown("**Suggested actions**");[st.write("• "+x) for x in r.get("actions",[])];st.caption(r.get("limitations","Only visible evidence was considered."))
def recipe():
    hero("Food Verse · 04","Make something good with what you have.","Turn pantry ingredients into a flexible recipe idea.");mode();ingredients=st.text_area("What’s in your kitchen?",placeholder="chickpeas, spinach, tomatoes, onion, rice",height=110);a,b,c=st.columns(3)
    dietary=a.multiselect("Dietary preferences",["Vegan","Vegetarian","Gluten-free","Dairy-free","Keto","Diabetic-friendly"]);minutes=b.select_slider("Time available",options=[15,30,45,60],value=30,format_func=lambda x:f"{x} min");servings=c.number_input("Servings",1,12,2)
    if st.button("Create a recipe",type="primary"):
        if not ingredients.strip(): st.warning("Add pantry ingredients first.")
        else:
            prompt=f"Create a practical recipe using {ingredients}; constraints {dietary}; max {minutes} minutes, {servings} servings. Return JSON keys name,description,time_minutes,difficulty,ingredients[],steps[],substitutions[],nutrition_note."
            st.session_state.pop("recipe",None)
            try:
                with st.spinner("Building your recipe…"):
                    result=generate_text(provider,api_key,prompt)
                st.session_state.recipe=result if result else demo_recipe(ingredients,dietary,minutes,servings)
            except Exception as exc: st.error(f"Recipe generation failed: {exc}")
    r=st.session_state.get("recipe")
    if r:
        model_notice(r)
        st.markdown("---");st.subheader(r.get("name","Pantry recipe"));st.write(r.get("description","Flexible pantry meal."));st.caption(f"⏱ {r.get('time_minutes',minutes)} min · {r.get('difficulty','Easy')} · Serves {servings}");x,y=st.columns(2)
        with x: st.markdown("**Ingredients**");[st.write("• "+i) for i in r.get("ingredients",[])];st.markdown("**Substitutions**");[st.write("• "+i) for i in r.get("substitutions",[])]
        with y: st.markdown("**Method**");[st.write(f"{i}. {s}") for i,s in enumerate(r.get("steps",[]),1)];st.info(r.get("nutrition_note","Nutrition depends on portions and ingredients."))
def planner():
    hero("Food Verse · 05","A week shaped around you.","Estimate energy needs, then make a seven-day meal outline and grocery list.");mode()
    with st.form("profile"):
        a,b,c=st.columns(3);age=a.number_input("Age",16,100,30);gender=b.selectbox("BMR formula input",["Female","Male"]);weight=c.number_input("Weight (kg)",30.,300.,70.,step=.5)
        a,b,c=st.columns(3);height=a.number_input("Height (cm)",120,230,170);activity=b.selectbox("Activity level",["Sedentary","Lightly active","Moderately active","Very active","Extra active"]);goal=c.selectbox("Fitness goal",["Maintain","Fat loss","Muscle gain"])
        diets=st.multiselect("Dietary style or constraints",["Vegan","Vegetarian","Keto","Diabetic-friendly","Gluten-free","Dairy-free"]);avoid=st.text_input("Foods or ingredients to avoid",placeholder="e.g. peanuts, shellfish, mushrooms")
        submitted=st.form_submit_button("Build my week",type="primary")
    if submitted:
        targets=calculate_targets(age,gender,weight,height,activity,goal)
        if provider=="Demo mode":
            st.session_state.plan={"targets":targets,"week":build_week(targets["calories"],diets),"diets":diets,"grocery":grocery_list([],diets)}
        elif not api_key:
            st.session_state.pop("plan",None);st.error("Enter a Gemini or Groq API key in the sidebar to generate a personalized meal plan.")
        else:
            prompt=(f"Create an adaptive 7-day meal plan as JSON with keys days (array of objects with day, breakfast, lunch, dinner, snack) and grocery_list (array of grocery items). Daily energy target about {targets['calories']} kcal; estimated BMR {targets['bmr']} and TDEE {targets['tdee']}. Profile: age {age}, gender input {gender}, weight {weight} kg, height {height} cm, activity {activity}, goal {goal}, dietary constraints {', '.join(diets) or 'none'}, avoid these ingredients: {avoid or 'none'}. Give reasonable portions, vary meals, honor restrictions, and list groceries for the plan. This is a general informational plan, not medical nutrition therapy. Do not claim precise nutrition values.")
            try:
                with st.spinner("Generating your personalized week…"):
                    result=generate_text(provider,api_key,prompt)
                if not result or not isinstance(result.get("days"),list) or len(result["days"])!=7: raise ValueError("The provider did not return a complete seven-day plan. Please try again.")
                if not all(isinstance(day,dict) and all(key in day for key in ("day","breakfast","lunch","dinner","snack")) for day in result["days"]): raise ValueError("The generated schedule was missing meal details. Please try again.")
                grocery=result.get("grocery_list",[])
                if not isinstance(grocery,list) or not all(isinstance(item,str) for item in grocery): grocery=[]
                st.session_state.plan={"targets":targets,"week":result["days"],"diets":diets,"grocery":grocery,"model":result.get("_model")}
            except Exception as exc:
                st.session_state.pop("plan",None);st.error(f"Meal plan generation failed: {exc}")
    plan=st.session_state.get("plan")
    if plan:
        model_notice({"_model":plan.get("model")})
        t=plan["targets"];a,b,c=st.columns(3);a.metric("Estimated BMR",f"{t['bmr']:,} kcal/day");b.metric("Estimated TDEE",f"{t['tdee']:,} kcal/day");c.metric("Daily target",f"{t['calories']:,} kcal/day");st.caption("Mifflin–St Jeor estimate with goal adjustment, not medical nutrition therapy.");st.subheader("Your seven-day outline")
        for d in plan["week"]:
            with st.expander(d["day"]):
                for m in ["breakfast","lunch","dinner","snack"]: st.write(f"**{m.title()}** · {d[m]}")
        items=plan.get("grocery") or grocery_list(plan["week"],plan["diets"]);st.subheader("Grocery list");st.write(" · ".join(items));st.download_button("Download grocery list","\n".join("- "+i for i in items),file_name="food-verse-grocery-list.txt",mime="text/plain")
        if "Diabetic-friendly" in plan["diets"]: st.info("Diabetes care is individual; review this plan with your clinician or dietitian.")
{"nutrition":nutrition,"freshness":freshness,"hygiene":hygiene,"recipe":recipe,"planner":planner}[PILLARS[page]]()
st.markdown("---");st.caption("Food Verse AI · Skill Wallet Capstone Project 3 · Educational estimates should be verified.")
