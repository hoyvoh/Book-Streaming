from flask import Blueprint, render_template, request
from . import collection, db, glove
from pymongo import DESCENDING
from vectorizer import update_user_vector_a1, update_user_vector_a2, semantic_search_vector, search_by_key
from bson.son import SON
from word2vec import update_user_log, queryByTitle, get10_user_log, get_all_user_log, w2vsemantic_search_vector

product = Blueprint('product', __name__)

def get_recommendations(vector_func, product_title, path):
    static_titles = queryByTitle(product_title, path)
    static = fetch_products_by_titles(static_titles, product_title)
    
    top10_embedding = vector_func(path)
    last10_titles = w2vsemantic_search_vector(path, top10_embedding)
    dynamic10 = fetch_products_by_titles(last10_titles, product_title)

    all_embedding = get_all_user_log(path)
    all_titles = w2vsemantic_search_vector(path, all_embedding)
    dynamic_all = fetch_products_by_titles(all_titles, product_title)

    return static, dynamic10, dynamic_all

def fetch_products_by_titles(titles, exclude_title):
    products = [
        collection.find_one({'value.TITLE': title})
        for title in titles if title and title != exclude_title and collection.find_one({'value.TITLE': title}) != None
    ]
    #print("Fetched Products:", products)  # Add this line
    return products

def output_bert_based(list1, list2, list3):
    tt1 = [collection.find_one({'value.ID':id}).get('value').get('TITLE')
           for id in list1]
    tt2 = [collection.find_one({'value.ID':id}).get('value').get('TITLE')
           for id in list2]
    tt3 = [collection.find_one({'value.ID':id}).get('value').get('TITLE')
           for id in list3]
    print('BERT-based Embedding Recommendation')
    print('Static Recommendation')
    print(tt3)
    print('Last 10 user history-based')
    print(tt1)
    print('All seen RCM')
    print(tt2)
    print('---------')
    

@product.route('/', methods=["GET", "POST"])
def index():
    page = int(request.args.get('page', 1))
    limit = 40
    skip = (page - 1) * limit
    pipeline = [
        {"$addFields": {"feature_3": {"$arrayElemAt": ["$FEATURES", 3]}, "feature_4_3": {"$arrayElemAt": ["$FEATURES.4", 3]}}},
        {"$sort": SON([("feature_3", DESCENDING), ("feature_4_3", DESCENDING)])},
        {"$skip": skip},
        {"$limit": limit},
        {"$project": {"feature_3": 0, "feature_4_3": 0}}
    ]
    products = list(collection.aggregate(pipeline))
    number_of_products = collection.count_documents({})
    return render_template('catalog.html', products=products, page=page, number_of_products=number_of_products)

@product.route('/product-details', methods=["GET", "POST"])
def product_details():
    product_id = request.args.get('product_id', 1)
    product_title = request.args.get('product_title', 1)
    product = collection.find_one({'key': product_id})
    if product is None:
        return "Product not found", 404

    user_vector_1 = update_user_vector_a1(product_id, db)
    user_vector_2 = update_user_vector_a2(product_id, db)
    list1 = semantic_search_vector(user_vector_1, db)
    list2 = semantic_search_vector(user_vector_2, db)
    list3 = search_by_key(product_id, db)
    print(list1)

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

    output_bert_based(list1, list2, list3)

    update_user_log({'ID': product_id, 'TITLE': product_title})

    pathsk = 'model/skipgram_w2v.model'
    skg_static, skg_rcm_10, skg_rcm_all = get_recommendations(get10_user_log, product_title, pathsk)

    print('Word2Vec Recommendation')
    print('> Continuous Skip-gram embedding recommendation')
    print('Static Recommendation')
    print([p['value']['TITLE'] for p in skg_static if p])
    print('Last 10 user history-based')
    print([p['value']['TITLE'] for p in skg_rcm_10 if p])
    print('All seen RCM')
    print([p['value']['TITLE'] for p in skg_rcm_all if p])
    print('---')

    pathcbow = 'model/cbow_w2v.model'
    cbow_static, cbow_rcm_10, cbow_rcm_all = get_recommendations(get10_user_log, product_title, pathcbow)

    print('> Continuous Bag-of-Words embedding recommendation')
    print('Static Recommendation')
    print([p['value']['TITLE'] for p in cbow_static if p])
    print('Last 10 user history-based')
    print([p['value']['TITLE'] for p in cbow_rcm_10 if p])
    print('All seen RCM')
    print([p['value']['TITLE'] for p in cbow_rcm_all if p])
    print('------------------')

    pathglove = 'model/glove_embedding.model'
    static_embedding = glove.get_embedding(product_id)
    glove_titles_static = w2vsemantic_search_vector(pathglove, static_embedding)
    glove_static = fetch_products_by_titles(glove_titles_static, product_title)
    glove_top10_embedding = glove.get_user_vector()
    glove_10_rcm = fetch_products_by_titles(glove.get_most_similars(glove_top10_embedding), product_title)
    glove_all_embedding = glove.get_user_vector_all()
    glove_all_rcm = fetch_products_by_titles(glove.get_most_similars(glove_all_embedding), product_title)

    print('> Global Vectors embedding recommendation')
    print('Static Recommendation')
    print([p['value']['TITLE'] for p in glove_static if p])
    print('Last 10 user history-based')
    print([p['value']['TITLE'] for p in glove_10_rcm if p])
    print('All seen RCM')
    print([p['value']['TITLE'] for p in glove_all_rcm if p])
    print('------------------')

    return render_template(
        'product.html',
        product=product,
        recommendations=sim3,
        dynamic_recommend1=sim1,
        dynamic_recommend2=sim2,
        skg_static=skg_static,
        skg_dy10=skg_rcm_10,
        skg_all=skg_rcm_all,
        cbow_static=cbow_static,
        cbow_dy10=cbow_rcm_10,
        cbow_all=cbow_rcm_all,
        glove_static=glove_static,
        glove_10=glove_10_rcm,
        glove_all=glove_all_rcm
    )
