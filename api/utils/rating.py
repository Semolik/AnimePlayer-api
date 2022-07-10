def ChangeToShikimoriRating(data):
    shikimori = data.get('shikimori')
    if shikimori:
        rating = shikimori.get('rating')
        if rating:
            data['rating'] = rating
    return data
