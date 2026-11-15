"""生成した音声をGeminiで書き起こし、関西弁らしさを判定する（聞き取り確認用）"""
import base64,json,sys,urllib.request
def ask(path,model='gemini-3.5-flash'):
    b=base64.b64encode(open(path,'rb').read()).decode()
    body={"contents":[{"parts":[{"inlineData":{"mimeType":"audio/wav","data":b}},
      {"text":"この音声に含まれる発話をすべて（英語の部分も含めて）一字一句そのまま書き起こしてください。その後、1行で『話者の性別』『アクセントが関西（京阪式）か東京式か』を答えてください。形式: 書き起こし: ... / 性別: ... / アクセント: ..."}]}]}
    req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    r=json.load(urllib.request.urlopen(req,timeout=120))
    return r["candidates"][0]["content"]["parts"][0]["text"].strip()
for p in sys.argv[1:]: print(p,'\n',ask(p),'\n')
