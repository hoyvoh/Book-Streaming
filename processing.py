import unicodedata
import regex as re
from pyvi import ViTokenizer
from time import time
import logistic_regression


'''
Context: 
For each row of data appended from the crawler, this package will be called to:
- Process data
- Feature extraction
- Update Similarity matrix
Also, for each book on screen, we also need to ** rank 10 most similar books ** 

Functions:
- Preprocessing for vietnamese data
- Threadpool processing for(
    + Keyword extraction (chunking > keyword embedding > title kmean clustering): -> string 10_most_relevant_keywords
    + Sales likeability (logistic regression(price, review count, rating avg)=>sales likeability) -> (0, 1) probability
    + Positive probability (phoBERT/other classification, count for probability) -> (0, 1) probability
    ): -> product_feature list [keywords string, sales probability, posititive probability]    

'''
# This is the expected format of the input data for this package
row = {'ID': 50685547, 
        'STOCK_KEEPING_UNIT': 2022689106017, 
        'TITLE': 'Bản Đồ', 
        'AUTHORS': 'Aleksandra Mizielińska, Daniel Mizieliński', 
        'PRICE': 224250, 
        'ORIGINAL_PRICE': 345000, 
        'RATING_AVERAGE': 4.8, 
        'REVIEW_COUNT': 931, 
        'INVENTORY_STATUS': 'available', 
        'all_time_quantity_sold': 5891.0, 
        'DESCRIPTION': 'Hãy khám phá thế giới cùng cuốn bản đồ khổng lồ đầu tiên ở Việt Nam! Sách gồm 52 tấm bản đồ minh họa sinh động các đặc điểm địa lý và biên giới chính trị, giới thiệu những địa điểm nổi tiếng, những nét đặc trưng, về động vật và thực vật bản địa, về con người địa phương, các sự kiện văn hóa cùng nhiều thông tin hấp dẫn khác.\nĐến với cuốn Bản đồ khổng lồ (27x37cm) gồm 52 tấm bản đồ đầy màu sắc sống động này, các bạn nhỏ sẽ được thỏa sức khám phá thế giới. Có tất cả 6 tấm bản đồ lục địa và 42 bản đồ quốc gia. Châu u có gì, châu Á nổi tiếng vì điều chi, khí hậu ở châu Phi như thế nào? Tất cả những chi tiết nổi bật của từng vùng miền, từng đất nước, như địa danh, trang phục, ẩm thực, lễ hội tập tục truyền thống, v…v… đều được liệt kê bằng những hình vẽ ngộ nghĩnh đáng yêu. Mỗi bản đồ có thống kê sơ bộ về diện tích, dân số, ngôn ngữ… để các bạn nhỏ nắm được thông tin tổng quát của từng đất nước, châu lục. Mỗi nước đều được phân chia thành các vùng địa lý cụ thể với tên vùng được viết mờ, các thành phố lớn trong từng nước được viết bằng màu đỏ nổi bật với chấm đỏ bên cạnh.\nCuốn sách này hứa hẹn sẽ là tấm vé đưa độc giả nhỏ du lịch khắp mọi miền trên thế giới. Các bậc phụ huynh cũng có thể đồng hành cùng con em mình, cùng ngâm cứu từng chi tiết trên mỗi tấm bản đồ, tìm hiểu và bàn luận về các địa phương. Thông qua việc chỉ dẫn, diễn giải cho các con về những thông tin trên bản đồ, đây sẽ là cuốn sách tương tác tốt để bố mẹ kết nối và gần gũi với con mình hơn.\nCUỐN SÁCH NÀY CÓ GÌ ĐẶC BIỆT?\nCuốn sách Bản đồ đã được xuất bản tại hơn 30 quốc gia, bán được hơn 3 triệu bản in, là một trong những cuốn bản đồ ăn khách nhất thế giới. Bản đồ của hai tác giả Aleksandra Mizielińska và Daniel Mizieliński đã giành được nhiều giải thưởng lớn, nổi bật nhất là giải Prix Sorcières của Pháp và giải Premio Andersen của Ý – hai giải thưởng danh giá cho dòng sách thiếu nhi.\nCác quốc gia đã xuất bản “Bản đồ”: Úc, Áo, Bỉ, Brazil, Canada, Chile, Trung Quốc, Croatia, Séc, Ecuador, Ai Cập, Fiji, Phần Land, Pháp, Đức, Ghana, Hy Lạp, Iceland, Ấn Độ, Ý, Nhật Bản, Jordan, Madagascar, Ma Rốc, Mexico, Mông Cổ, Namibia, Nepal, Hà Lan, New Zealand, Peru, Ba Lan, Nam Phi, Romania, Nga, Tây Ban Nha, Thụy Điển, Thụy Sĩ, Tanzania, Thái Lan, Anh, Mỹ.\nĐẶC BIỆT: Phiên bản "Bản đồ" Việt Nam đặc biệt được tác giả vẽ riêng đất nước Việt Nam.\nĐể thực hiện cuốn sách đồ sộ này, hai tác giả trẻ đã phải mất hơn 3 năm trời. Sau khi nghiên cứu và tìm hiểu kỹ lưỡng, họ lập một danh sách các thông tin hấp dẫn và thú vị với trẻ em, chọn lọc ra những chi tiết đặc sắc nhất của mỗi nước để vẽ vào bản đồ. Các tấm bản đồ đều được vẽ theo tỉ lệ chuẩn xác dựa trên các bản đồ địa lý đã được phát hành. Hai tác giả không chỉ vẽ tay tất cả các chi tiết hình ảnh mà còn dày công thiết kế tất cả các phông chữ được dùng trong sách.\nGiá sản phẩm trên Tiki đã bao gồm thuế theo luật hiện hành. Bên cạnh đó, tuỳ vào loại sản phẩm, hình thức và địa chỉ giao hàng mà có thể phát sinh thêm chi phí khác như phí vận chuyển, phụ phí hàng cồng kềnh, thuế nhập khẩu (đối với đơn hàng giao từ nước ngoài có giá trị trên 1 triệu đồng).....',
        'COMMENTS': [{'CommentTitle': 'Cực kì hài lòng', 'Content': 'Bé thích lắm, mắt tròn xoe và cứ quào quào miết', 'rating': 5, 'ProductID': 50685547},
{'CommentTitle': 'Cực kì hài lòng', 'Content': 'Sách to đẹp, giao hàng siêu nhanh, 100 sao nhé shop', 'rating': 5, 'ProductID': 50685547},
{'CommentTitle': 'Cực kì hài lòng', 'Content': 'Mua tặng cháu. Nhưng mình cũng rất thích. Cuốn sách to hơn tưởng tượng', 'rating': 5, 'ProductID': 50685547},
{'CommentTitle': 'Cực kì hài lòng', 'Content': 'Sách đẹp, dày dặn, nội dung rất thú vị. Tiki bán giá tốt và giao hàng trong ngày rất nhanh.', 'rating': 5, 'ProductID': 50685547},
{'CommentTitle': 'Cực kì hài lòng', 'Content': 'Sản phẩm đẹp, bé chơi rất thích', 'rating': 5, 'ProductID': 50685547},
{'CommentTitle': 'Cực kì hài lòng', 'Content': 'Mình nhận đc rồi. Bé nhà mình rất thích quyển sách này. Cảm ơn nhà xuất bản và shop nhé', 'rating': 5, 'ProductID': 50685547},
{'CommentTitle': 'Cực kì hài lòng', 'Content': 'cuốn sách khá dày, tiki cho mình thùng to quá, giao nhanh chóng mặt luôn tối trước đặt sau đã có.  còn được tặng bản đồ to nữa ?', 'rating': 5, 'ProductID': 50685547},
{'CommentTitle': 'Cực kì hài lòng', 'Content': 'sách rất đẹp nhaaaaaa, còn mua được với giá sale nữa. hihi', 'rating': 5, 'ProductID': 50685547},
{'CommentTitle': 'Cực kì hài lòng', 'Content': 'Sản phầm ổn với tầm giá này. \r\nSẽ giới thiệu bạn bè mua', 'rating': 5, 'ProductID': 50685547},
{'CommentTitle': 'Cực kì hài lòng', 'Content': 'Tiki giao hàng nhanh, đóng gói cẩn thận. Sách to hơn so với mình nghĩ. Mua mang tặng nên chưa mở ra xem nội dung thế nào.', 'rating': 5, 'ProductID': 50685547}],
        "CATEGORIES": "Nhà Sách Tiki, Sách tiếng Việt, Sách văn học, Truyện ngắn - Tản văn - Tạp Văn, Truyện ngắn - Tản văn - Tạp Văn Nước Ngoài, Điều Kỳ Diệu Của Tiệm Tạp Hóa NAMIYA (Tái Bản)"
        }

# Vietnamese preprocessing 
vietnamese_stopwords = {
    "bị", "bởi", "cả", "các", "cái", "cần", "càng", "chỉ", "chiếc", "cho",
    "chứ", "chưa", "chuyện", "có", "có thể", "cứ", "của", "cùng", "cũng", "đã",
    "đang", "đây", "để", "đến nỗi", "đều", "điều", "do", "đó", "được", "dưới",
    "gì", "khi", "không", "là", "lại", "lên", "lúc", "mà", "mỗi", "một cách",
    "này", "nên", "nếu", "ngay", "nhiều", "như", "nhưng", "những", "nơi", "nữa",
    "phải", "qua", "ra", "rằng", "rất", "rồi", "sau", "sẽ", "so", "sự", "tại",
    "theo", "thì", "trên", "trước", "từ", "từng", "và", "vẫn", "vào", "vậy", "vì",
    "việc", "với", "đó", "bên cạnh", "đó", "tùy", "cho", "trong", "đối_với", 'tất_cả'
}

bang_nguyen_am= [['a', 'à', 'á', 'ả', 'ã', 'ạ', 'a'],
                  ['ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ', 'aw'],
                  ['â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ', 'aa'],
                  ['e', 'è', 'é', 'ẻ', 'ẽ', 'ẹ', 'e'],
                  ['ê', 'ề', 'ế', 'ể', 'ễ', 'ệ', 'ee'],
                  ['i', 'ì', 'í', 'ỉ', 'ĩ', 'ị', 'i'],
                  ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'o'],
                  ['ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ', 'oo'],
                  ['ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ', 'ow'],
                  ['u', 'ù', 'ú', 'ủ', 'ũ', 'ụ', 'u'],
                  ['ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự', 'uw'],
                  ['y', 'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ', 'y']]

bang_ky_tu_dau = ['', 'f', 's', 'r', 'x', 'j']
nguyen_am_to_ids = {}

for i in range(len(bang_nguyen_am)):
    for j in range(len(bang_nguyen_am[i]) - 1):
        nguyen_am_to_ids[bang_nguyen_am[i][j]] = (i, j)

def chuan_hoa_unicode(text):
	text = unicodedata.normalize('NFC', text)
	return text

def chuan_hoa_dau_tu_tieng_viet(word):
    if not is_valid_vietnam_word(word):
        return word

    chars = list(word)
    dau_cau = 0
    nguyen_am_index = []
    qu_or_gi = False
    for index, char in enumerate(chars):
        x, y = nguyen_am_to_ids.get(char, (-1, -1))
        if x == -1:
            continue
        elif x == 9:  # check qu
            if index != 0 and chars[index - 1] == 'q':
                chars[index] = 'u'
                qu_or_gi = True
        elif x == 5:  # check gi
            if index != 0 and chars[index - 1] == 'g':
                chars[index] = 'i'
                qu_or_gi = True
        if y != 0:
            dau_cau = y
            chars[index] = bang_nguyen_am[x][0]
        if not qu_or_gi or index != 1:
            nguyen_am_index.append(index)
    if len(nguyen_am_index) < 2:
        if qu_or_gi:
            if len(chars) == 2:
                x, y = nguyen_am_to_ids.get(chars[1])
                chars[1] = bang_nguyen_am[x][dau_cau]
            else:
                x, y = nguyen_am_to_ids.get(chars[2], (-1, -1))
                if x != -1:
                    chars[2] = bang_nguyen_am[x][dau_cau]
                else:
                    chars[1] = bang_nguyen_am[5][dau_cau] if chars[1] == 'i' else bang_nguyen_am[9][dau_cau]
            return ''.join(chars)
        return word

    for index in nguyen_am_index:
        x, y = nguyen_am_to_ids[chars[index]]
        if x == 4 or x == 8:  # ê, ơ
            chars[index] = bang_nguyen_am[x][dau_cau]
            # for index2 in nguyen_am_index:
            #     if index2 != index:
            #         x, y = nguyen_am_to_ids[chars[index]]
            #         chars[index2] = bang_nguyen_am[x][0]
            return ''.join(chars)

    if len(nguyen_am_index) == 2:
        if nguyen_am_index[-1] == len(chars) - 1:
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
            chars[nguyen_am_index[0]] = bang_nguyen_am[x][dau_cau]
            # x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
            # chars[nguyen_am_index[1]] = bang_nguyen_am[x][0]
        else:
            # x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
            # chars[nguyen_am_index[0]] = bang_nguyen_am[x][0]
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
            chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
    else:
        # x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
        # chars[nguyen_am_index[0]] = bang_nguyen_am[x][0]
        x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
        chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
        # x, y = nguyen_am_to_ids[chars[nguyen_am_index[2]]]
        # chars[nguyen_am_index[2]] = bang_nguyen_am[x][0]
    return ''.join(chars)

def is_valid_vietnam_word(word):
    chars = list(word)
    nguyen_am_index = -1
    for index, char in enumerate(chars):
        x, y = nguyen_am_to_ids.get(char, (-1, -1))
        if x != -1:
            if nguyen_am_index == -1:
                nguyen_am_index = index
            else:
                if index - nguyen_am_index != 1:
                    return False
                nguyen_am_index = index
    return True

def chuan_hoa_dau_cau_tieng_viet(sentence):
    sentence = sentence.lower()
    words = sentence.split()
    for index, word in enumerate(words):
        cw = re.sub(r'(^\p{P}*)([p{L}.]*\p{L}+)(\p{P}*$)', r'\1/\2/\3', word).split('/')
        # print(cw)
        if len(cw) == 3:
            cw[1] = chuan_hoa_dau_tu_tieng_viet(cw[1])
        words[index] = ''.join(cw)
    return ' '.join(words)

def tach_tu_tieng_viet(text):
	text = ViTokenizer.tokenize(text)
	return text

def chuyen_chu_thuong(text):
	return text.lower()

def loai_bo_chu_dem(text):
    text = text.split()
    text = [w for w in text if w not in vietnamese_stopwords]
    text = ' '.join(text)
    return text

def chuan_hoa_cau(text):
	text = re.sub(r'[^\s\wáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ_]',' ',text)
	text = re.sub(r'\s+', ' ', text).strip()
	return text

def vietnamese_preprocessing(text):
    text = chuan_hoa_unicode(text)
    text = chuan_hoa_dau_cau_tieng_viet(text)
    text = tach_tu_tieng_viet(text)
    text = chuyen_chu_thuong(text)
    text = loai_bo_chu_dem(text)
    text = chuan_hoa_cau(text)
    return text

def row_processing(row):
    desc = vietnamese_preprocessing(row['DESCRIPTION'])
    row['DESCRIPTION'] = desc
    row['TITLE'] = row['TITLE'].lower()
    row['AUTHORS'] = row['AUTHORS'].lower()
    return row

# KeyBERT models
from keybert import KeyBERT
kw_model = KeyBERT()

# Features extraction
def keyword_extraction(row):
    row = row_processing(row)
    desc = row['DESCRIPTION']
    cates = row['CATEGORIES'].split(',')

    top_keywords = kw_model.extract_keywords(desc, keyphrase_ngram_range=(2, 2), stop_words=None,
                        use_maxsum=True, nr_candidates=20, top_n=3)
    # print(top_keywords)

    keywords = [key[0] for key in top_keywords]
    keywords = [key for keygroups in keywords for key in keygroups.split(" ")]

    # filter duplicates
    dup_filtered = []
    for key in keywords:
        if key not in dup_filtered:
            key = ' '.join(key.split('_'))
            dup_filtered.append(key)
    # print(dup_filtered)
    # dup_filtered = [' '.join(key.split('_')) for key in dup_filtered if len(key.split('_'))>1]
    for cat in cates:
        dup_filtered.append(cat)

    return dup_filtered

# Load logistic regression model
from joblib import load
from sklearn.preprocessing import StandardScaler
logistic_regression_model = load(logistic_regression.path)
scaler = StandardScaler()

def sales_likeability(row):
    # make it to standard
    cols = ['PRICE', 'REVIEW_COUNT', 'RATING_AVERAGE']
    # The line below only work when we pass in a df, otherwise, do not use
    # row = row[cols]
    row = [row[col] for col in cols]
    # print('Feature row:',row)
    scaled_row = scaler.fit_transform([row])
    # print('Scaled feature row:', scaled_row)
    prediction = logistic_regression_model.predict(scaled_row)
    # print(prediction)
    return prediction[0]

from transformers import pipeline

distilled_sentiment_classifier = pipeline(
    model= "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    return_all_scores=True
)

def positive_probability(row):
    comments = row['COMMENTS']
    if len(comments) == 0:
        return []
    labs = []

    for comment in comments:
        content = comment['Content']
        # print(content)
        content_chunks = [content[i:i+512] for i in range(0, len(content), 512)]
        for chunk in content_chunks:
            lab = distilled_sentiment_classifier(chunk)
            print(lab[0][0]['label'])
            labs.append(lab[0][0]['label'])
    # print(labs)
    if len(labs) == 0:
        return [0,0,0,0]
    pos = labs.count('positive')
    neu = labs.count('neutral')
    neg = labs.count('negative')
    prob = (labs.count('positive')+labs.count('neutral')*0.5)/len(labs)
    return [pos, neu, neg, prob]

def features_extraction(row):
    # Use thread pool to process this
    viet_row = row_processing(row)
    keywords = keyword_extraction(viet_row)
    sales_prob = sales_likeability(viet_row)
    positive_prob = positive_probability(row)

    features = [viet_row['TITLE'], viet_row['AUTHORS'], keywords, sales_prob, positive_prob]
    row['FEATURES'] = features
    # print(features)
    return row

'''
- For each new line(PID, product features) -> pass to similarity matrix to create indexing and update similarity matrix 
'''

def main(new_row=row):
    start = time()
    with_features = features_extraction(new_row)
    end = time()
    print(f">>> Extraction completed after: {end-start}s")
    doc = {
        'key': new_row['ID'],
        'value': with_features['FEATURES']
    }
    # print(doc.get('value'))
    end = time()
    print(f">>> Insertion completed after: {end-start}s")
    return with_features['FEATURES'], doc


if __name__ == '__main__':
    # Process new row
    start = time()
    new_row = row_processing(row)
    end = time()
    
    print(new_row)
    print(f">>> Preprocessing completed after: {end-start}s")

    # Extract features
    start = time()
    # something here
    sales = sales_likeability(new_row)
    print(f"Sales likeability: {sales}")
    positive = positive_probability(new_row)
    print(main(new_row))
    print(f"Positive likeability: {positive}")
    keywords = keyword_extraction(new_row)
    print(keywords)
    features = features_extraction(row)
    print(features)
    end = time()
    print(f">>> Extraction completed after: {end-start}s")