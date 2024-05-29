from flask import Blueprint, render_template, request, render_template_string
from . import collection
from bson.objectid import ObjectId

product = Blueprint('product', __name__)

@product.route('/', methods=["GET", "POST"])
def index():
    page=int(request.args.get('page', 1))
    limit = 50
    skip = (page -1)*limit
    
    products = list(collection.find().skip(skip).limit(limit))
    # print(products)
    return render_template('catalog.html', products=products, page=page) # 

@product.route('/product-details', methods=["GET", "POST"])
def product_details():
    # print(request.args.get('product_id', 1))
    product = collection.find_one({'key': request.args.get('product_id', 1)})
    
    similar_products = product.get('value').get('RECOMMENDED')
    print(similar_products)
    s_products = []
    for sp in similar_products:
        if sp is None:
            break
        p = collection.find_one({'key':sp})
        print(p)
        s_products.append(p)
    print(s_products)
    return render_template('product.html', product=product, recommendations= s_products)
