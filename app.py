from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
import io, json, hashlib

app = Flask(__name__)

def pixel_codes(img):
    w, h = img.size
    pixels = img.load()
    data=[]
    for y in range(h):
        for x in range(w):
            r,g,b = pixels[x,y][:3]
            code = f"X{x}Y{y}R{r}G{g}B{b}"
            hcode = hashlib.sha256(code.encode()).hexdigest()
            data.append({"x":x,"y":y,"r":r,"g":g,"b":b,"code":code,"hash":hcode})
    return {"width":w,"height":h,"pixels":data}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/encode", methods=["GET","POST"])
def encode():
    if request.method=="POST":
        file=request.files["image"]
        img=Image.open(file.stream).convert("RGBA")
        data=pixel_codes(img)
        buf=io.BytesIO()
        buf.write(json.dumps(data).encode())
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name="pixel_codes.json", mimetype="application/json")
    return render_template("encode.html")

@app.route("/decode", methods=["GET","POST"])
def decode():
    if request.method=="POST":
        file=request.files["codes"]
        data=json.load(file.stream)
        w,h=data["width"], data["height"]
        img=Image.new("RGBA",(w,h))
        px=img.load()
        for p in data["pixels"]:
            px[p["x"],p["y"]] = (p["r"],p["g"],p["b"],255)
        buf=io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name="reconstructed.png", mimetype="image/png")
    return render_template("decode.html")

if __name__=="__main__":
    app.run(debug=True)
