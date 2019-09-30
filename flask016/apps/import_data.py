# _*_ coding:utf-8 _*_
from apps import db
from apps.models import User, Article

if __name__ == "__main__":
    # users = User.query.all()
    # print(users)
    # bestCreators = User.query.order_by(User.creator_score.desc()).all()
    # print(bestCreators)
    # for user in users:
    #     user.articles_score = 0
    #     for art in user.articles:
    #         user.articles_score += art.clicknum
    #     user.albums_score = 0
    #     for album in user.albums:
    #         user.albums_score += album.clicknum
    #     user.creator_score = user.articles_score + user.albums_score
    #     user.comments_score = len(user.articlecomments) + \
    #                           len(user.musiccomments) + \
    #                           len(user.moviecomments)
    #
    #     db.session.add(user)
    #     db.session.commit()
    articles = Article.query.all()
    for item in articles:
        item.commtnum = 0
        db.session.add(item)
    db.session.commit()
