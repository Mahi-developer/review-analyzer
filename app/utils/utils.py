import re


def process_integer_from_string(s):
    if s:
        return int(re.sub(r'[^0-9]', '', s.split('.')[0].strip()))
    return s


def separate_uid_from_url(url):
    base = url.split('?')[0]
    return base.split('/')[-1]


def separate_shop_name(s):
    return re.sub(
        r'[^a-zA-z]', '',
        s.replace('.in', '').replace('.com', '').replace('.co', '').replace('from', '').strip()
    )


def preprocess_reviews(r):
    return [
        re.sub(r'[^a-zA-Z0-9]', ' ', review.replace('\n', '').strip())
        for review in r
    ]


def preprocess_review(r):
    return re.sub(r'[^a-zA-Z]', ' ', r.replace('\n', '').strip())


# if __name__ == '__main__':
# Todo see the following are getting null for values that also present for sample uid 7596414811817512508
''' 
    * specification_flat
    * ratings_count
    * delivery  
'''

# git hub token
# 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
