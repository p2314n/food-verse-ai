"""Gemini and Groq adapters with demo fallback."""
import base64,json,re
import time
from typing import Any
def _json(text:str)->dict[str,Any]:
    text=re.sub(r"^```(?:json)?\s*|\s*```$","",text.strip(),flags=re.I)
    try: obj=json.loads(text)
    except json.JSONDecodeError:
        a,b=text.find("{"),text.rfind("}")
        if a<0 or b<=a: raise ValueError("AI did not return JSON")
        obj=json.loads(text[a:b+1])
    if not isinstance(obj,dict): raise ValueError("Expected JSON object")
    return obj

def _gemini_json(api_key:str,contents:Any,temperature:float)->dict[str,Any]:
    """Call Gemini with bounded retries and a stable Flash fallback."""
    from google import genai
    from google.genai import types
    import httpx
    client=genai.Client(api_key=api_key,http_options=types.HttpOptions(timeout=25_000,retry_options=types.HttpRetryOptions(attempts=1)))
    try:
        models=("gemini-3.8-flash","gemini-3.6-flash")
        for index,model in enumerate(models):
            try:
                response=client.models.generate_content(model=model,contents=contents,config=types.GenerateContentConfig(response_mime_type="application/json",temperature=temperature))
                result=_json(response.text or "")
                result["_model"]=model
                return result
            except Exception as exc:
                status_code=getattr(exc,"code",None)
                is_transient=(status_code in {500,502,503,504} or "503 UNAVAILABLE" in str(exc) or isinstance(exc,httpx.TransportError))
                if not is_transient or index==len(models)-1: raise
                time.sleep(1)
    finally: client.close()
def analyze_image(provider:str,api_key:str,image:bytes,mime_type:str,prompt:str)->dict[str,Any]:
    if provider=="Demo mode": return {"_demo":True}
    if not api_key: raise ValueError("Enter the selected provider's API key in the sidebar.")
    if provider=="Google Gemini":
        from google.genai import types
        return _gemini_json(api_key,[prompt,types.Part.from_bytes(data=image,mime_type=mime_type)],.2)
    if provider=="Groq":
        from groq import Groq
        url=f"data:{mime_type};base64,{base64.b64encode(image).decode()}"
        r=Groq(api_key=api_key,timeout=45,max_retries=0).chat.completions.create(model="qwen/qwen3.8-27b",messages=[{"role":"user","content":[{"type":"text","text":prompt},{"type":"image_url","image_url":{"url":url}}]}],temperature=.2,response_format={"type":"json_object"})
        return _json(r.choices[0].message.content or "")
    raise ValueError("Unsupported provider")
def generate_text(provider:str,api_key:str,prompt:str)->dict[str,Any]|None:
    if provider=="Demo mode": return None
    if not api_key: raise ValueError("Enter the selected provider's API key in the sidebar.")
    if provider=="Google Gemini":
        return _gemini_json(api_key,prompt,.6)
    if provider=="Groq":
        from groq import Groq
        r=Groq(api_key=api_key,timeout=45,max_retries=0).chat.completions.create(model="qwen/qwen3.8-27b",messages=[{"role":"user","content":prompt}],temperature=.6,response_format={"type":"json_object"})
        return _json(r.choices[0].message.content or "")
    raise ValueError("Unsupported provider")

def analyze_video(provider:str,api_key:str,video:bytes,mime_type:str,prompt:str)->dict[str,Any]:
    """Inspect a short kitchen video with Gemini's native video input."""
    if provider=="Demo mode":
        from foodverse.samples import demo_hygiene
        return demo_hygiene()
    if not api_key: raise ValueError("Enter the selected provider's API key in the sidebar.")
    if provider!="Google Gemini": raise ValueError("For video analysis, select Google Gemini. Groq mode supports kitchen images.")
    from google.genai import types
    return _gemini_json(api_key,[prompt,types.Part.from_bytes(data=video,mime_type=mime_type)],.2)
