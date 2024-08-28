
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

    return jsonify({'Success': 'Usuario actualizado'}), 201
  else:
    return jsonify({'error': 'Usuario no encontrado'}), 404
  
@app.route("/deleteuser", methods=['DELETE'])
def delete_user():
  email= request.json.get("email")
  user = User.query.filter_by(email=email).first()
  if user is not None:
    db.session.delete(user)
    db.session.commit()
    return jsonify({
      "msg": "Usuario eliminado",
      "status": "Success"
    }), 203
  else:
    return jsonify({"error":"Usuario no encontrado"}),404
  


@app.route('/uploadproduct', methods=["POST"])
def upload_product():
  if 'image' not in request.files:
    return jsonify({ "msg": "Imagen es requerida"}), 400 
  
  if "category" not in request.form:
    return jsonify({ "msg": "Categoría es requerido"}), 400 

  if "name" not in request.form:
    return jsonify({ "msg": "Nombre es requerido"}), 400 
  
  if "price" not in request.form:
    return jsonify({ "msg": "Precio es requerido"}), 400 
  
#Capturo todos los datos a guardar
  image= request.files.get('image')
  category = request.form.get('category')
  name = request.form.get('name')
  price = request.form.get('price')
  offer = request.form.get('offer', None)  # Oferta es opcional

#Upload de la Imagen
  resp = cloudinary.uploader.upload(image, folder=f"Distribuidora Kiwan/{category}")

  if not 'secure_url' in resp:
    return jsonify({ "error": "No se pudo subir la imagen"}), 400
 
  product = Products( image=resp['secure_url'], category=category, name=name,price=price, offer=offer, public_id=resp['public_id'])

  db.session.add(product)
  db.session.commit()

  if product:
    return jsonify(product.serialize()), 200
    
  return jsonify({ "error": "No se pudo guardar la imagen"}), 400


@app.route('/getproducts/<string:category>', methods=['GET'])
def get_products(category):
    # Obtén el número de página de los parámetros de la URL, por defecto la página 1
    page = request.args.get('page', 1, type=int)
    
    # Realiza la consulta y paginación
    products_category = Products.query.filter_by(category=category).paginate(page=page, per_page=20, error_out=False)
    
    
    if products_category.items:
        return jsonify({
            'products': [product.serialize() for product in products_category.items],
            'total_pages': products_category.pages,
            'current_page': products_category.page,
        }), 200
    else:
        return jsonify({'Error': 'No hay Productos en esta Categoría'}), 404


@app.route('/updateproduct/<int:id>', methods=["PUT"])
def update_product(id):
    product = Products.query.get(id)
    
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404
    
    
    if "category" in request.form:
        product.category = request.form.get('category')

    # Actualizar imagen si se envía una nueva
    if 'image' in request.files:
        image = request.files.get('image')
        if product.public_id:  # Si hay una imagen existente, eliminarla de Cloudinary
            cloudinary.uploader.destroy(product.public_id)
        resp = cloudinary.uploader.upload(image, folder=f"Distribuidora Kiwan/{product.category}")
        product.image = resp['secure_url']
        product.public_id = resp['public_id']

    # Actualizar los demás campos si se envían
      
    if "name" in request.form:
        product.name = request.form.get('name')
        
    if "price" in request.form:
        product.price = request.form.get('price')
        
    if "offer" in request.form:
        product.offer = request.form.get('offer')
    
    # Guardar cambios en la base de datos
    db.session.commit()

    return jsonify(product.serialize()), 200

@app.route('/deleteproduct/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Products.query.filter_by(id=id).first()

    if not product:
        return jsonify({ "msj": "El producto que quiere eliminar no existe"}), 400
    

    resp = cloudinary.uploader.destroy(product.public_id)
    if not 'result' in resp:
        return jsonify({ "msj": "No se pudo eliminar el Producto"}), 400
    
    db.session.delete(product)
    db.session.commit()

    return jsonify({ "Exitoso": "Producto eliminado correctamente"}), 200
   





# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
