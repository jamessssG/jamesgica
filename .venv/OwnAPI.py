from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dish_name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(200), nullable=False)
    calories = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

    if Food.query.count() == 0:
        sample_foods = [
            Food(dish_name='Chicken Adobo', ingredients='Chicken, soy sauce, vinegar, garlic', calories=350),
            Food(dish_name='Pancit Canton', ingredients='Noodles, vegetables, soy sauce, meat', calories=420),
            Food(dish_name='Mango Cake', ingredients='Mango,sugar, flour, baking soda', calories=410),
            Food(dish_name='Kare-Kare', ingredients='Oxtail, peanut sauce, vegetables', calories=500),
            Food(dish_name='Calamares', ingredients='Squid, salt, bread crumbs', calories=600)
        ]
        db.session.bulk_save_objects(sample_foods)
        db.session.commit()

parser = reqparse.RequestParser()
parser.add_argument('dish_name', type=str, required=True, help='Dish name is required')
parser.add_argument('ingredients', type=str, required=True, help='Ingredients are required')
parser.add_argument('calories', type=int, required=True, help='Calories are required')

class FoodList(Resource):
    def get(self):
        foods = Food.query.all()
        return [{'id': f.id, 'dish_name': f.dish_name, 'ingredients': f.ingredients, 'calories': f.calories} for f in foods], 200

    def post(self):
        args = parser.parse_args()
        new_food = Food(
            dish_name=args['dish_name'],
            ingredients=args['ingredients'],
            calories=args['calories']
        )
        db.session.add(new_food)
        db.session.commit()
        return {'message': 'Food added successfully'}, 201

class FoodItem(Resource):
    def put(self, food_id):
        args = parser.parse_args()
        food = Food.query.get(food_id)
        if not food:
            return {'message': 'Food not found'}, 404
        food.dish_name = args['dish_name']
        food.ingredients = args['ingredients']
        food.calories = args['calories']
        db.session.commit()
        return {'message': 'Food updated successfully'}, 200

    def delete(self, food_id):
        food = Food.query.get(food_id)
        if not food:
            return {'message': 'Food not found'}, 404
        db.session.delete(food)
        db.session.commit()
        return {'message': 'Food deleted successfully'}, 200

api.add_resource(FoodList, '/foods')
api.add_resource(FoodItem, '/foods/<int:food_id>')

if __name__ == '__main__':
    app.run(debug=True)