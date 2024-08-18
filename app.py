
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Products
import cloudinary
import cloudinary.uploader
import cloudinary.api





load_dotenv()

#Configuracion en Cloudinary
cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET"),
  secure = True
)

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/') 
def sitemap():
    return generate_sitemap(app)  

#Creamos un usuario
@app.route('/createuser', methods=["POST"])
def create():
  get_from_body = request.json.get("email")
  user = User() 
  usuario_existente = User.query.filter_by(email=get_from_body).first()
  if usuario_existente is not None:
    return "The User already exist"
  else:
    user.name = request.json.get("name")
    user.lastname = request.json.get("lastname")
    user.email = request.json.get("email")
    user.password = request.json.get("password")
   

    db.session.add(user)
    db.session.commit()  

    return f"Se creo el usuario", 201
  
#Actualizamos un usuario
@app.route('/updateuser', methods=["PUT"])  
def update_user():
  current_email= request.json.get("email")
  user = User.query.filter_by(email=current_email).first()
  new_email= request.json.get("new_email")
  name =  request.json.get("name")
  lastname =  request.json.get("lastname")
  password =  request.json.get("password")
  
  if user:
    if new_email:
     user.email = new_email
    if name:
     user.name = name
    if lastname: 
      user.lastname = lastname
    if password:  
     user.password = password

  
    db.session.commit()

    return jsonify({'Success': 'User updated'}), 201
  else:
    return jsonify({'error': 'User not found'}), 404
  
@app.route("/deleteuser", methods=['DELETE'])
def delete_user():
  email= request.json.get("email")
  user = User.query.filter_by(email=email).first()
  if user is not None:
    db.session.delete(user)
    db.session.commit()
    return jsonify({
      "msg": "User deleted",
      "status": "Success"
    }), 203
  else:
    return jsonify({"error":"User not find"}),404
  


@app.route('/uploadproduct', methods=["POST"])
def upload_product():
  if 'image' not in request.files:
    return jsonify({ "msg": "Imagen es requerida"}), 400 

  if "name" not in request.form:
    return jsonify({ "msg": "Nombre es requerido"}), 400 
  
  if "price" not in request.form:
    return jsonify({ "msg": "Precio es requerido"}), 400 
  
#Capturo todos los datos a guardar
  image= request.files.get('image')
  name = request.form.get('name')
  price = request.form.get('price')
  offer = request.form.get('offer', None)  # Oferta es opcional

#Upload de la Imagen
  resp = cloudinary.uploader.upload(image, folder="Distribuidora Kiwan")

  if not 'secure_url' in resp:
    return jsonify({ "error": "No se pudo subir la imagen"}), 400
 
  product = Products( image=resp['secure_url'],name=name,price=price, offer=offer, public_id=resp['public_id'])

  db.session.add(product)
  db.session.commit()

  if product:
    return jsonify(product.serialize()), 200
    
  return jsonify({ "error": "No se pudo guardar la imagen"}), 400
   



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
