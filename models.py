from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(120), nullable=False)
    lastname= db.Column(db.String(120),  nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    

   

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    

class Products(db.Model):
    __tablename__="products"
    id =   db.Column(db.Integer, primary_key=True)
    image= db.Column(db.String, nullable=False)
    category= db.Column(db.String, nullable=True)
    name=  db.Column(db.String, nullable=False)
    offer_carrusel= db.Column(db.Boolean, default=False)
    price= db.Column(db.String,  nullable=True)
    offer= db.Column(db.String, nullable= True)
    public_id= db.Column(db.String, nullable=False)

    def serialize(self):
        return{
            "id": self.id,
            "offer_carrusel": self.offer_carrusel,
            "image": self.image,
            "category": self.category,
            "name": self.name,
            "price": self.price,
            "offer": self.offer,
            "public_id": self.public_id
        }


    