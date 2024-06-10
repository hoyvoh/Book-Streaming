from flask import Blueprint, render_template, request
from . import collection, db
from pymongo import DESCENDING
from vectorizer import update_user_vector_a1, update_user_vector_a2, semantic_search_vector, search_by_key

product = Blueprint('product', __name__)

@product.route('/', methods=["GET", "POST"])
def index():
    page=int(request.args.get('page', 1))
    limit = 40
    skip = (page -1)*limit
    
    products = list(collection.find().sort("_id", DESCENDING).skip(skip).limit(limit))
    number_of_products = collection.count_documents({})
    # print(products)
    return render_template('catalog.html', products=products, page=page, number_of_products=number_of_products) # 

@product.route('/product-details', methods=["GET", "POST"])
def product_details():
    print(request.args.get('product_id', 1))
    product = collection.find_one({'key': request.args.get('product_id', 1)})
    if product is None:
        return "Product not found", 404
    
    # Using similarity matrix
    '''similar_products = product.get('value', {}).get('RECOMMENDED', [])
    print(similar_products)
    s_products = []
    for sp in similar_products:
        if sp is None:
            continue
        p = collection.find_one({'key':sp})
        # print(p)
        s_products.append(p)'''
    # print(s_products)

    # Using dynamic vector indexing
    # get user vector:
    user_vector_1 = update_user_vector_a1(request.args.get('product_id', 1), db)
    user_vector_2 = update_user_vector_a2(request.args.get('product_id', 1), db)
    # get list of 10 products
    print("Recommend product list")
    list1 = semantic_search_vector(user_vector_1, db)
    list2 = semantic_search_vector(user_vector_2, db)
    list3 = search_by_key(request.args.get('product_id', 1), db)
    print(list1)
    print(list2)
    print(list3)
    sim1 = []
    for sp in list1:
        if sp is None:
            continue
        elif sp == request.args.get('product_id', 1):
            continue
        p = collection.find_one({'key':sp})
        # print(p)
        if p is None:
            continue
        sim1.append(p)
    #print(sim1)
    sim2 = []
    for sp in list2:
        if sp is None:
            continue
        elif sp == request.args.get('product_id', 1):
            continue
        p = collection.find_one({'key':sp})
        # print(p)
        if p is None:
            continue
        sim2.append(p)
    # print(sim1[1])
    sim3 = []
    for sp in list3:
        if sp is None:
            continue
        elif sp == request.args.get('product_id', 1):
            continue
        p = collection.find_one({'key':sp})
        # print(p)
        if p is None:
            continue
        sim3.append(p)
    # print(sim3)

    return render_template('product.html', product=product, recommendations= sim3, dynamic_recommend1=sim1, dynamic_recommend2=sim2)
