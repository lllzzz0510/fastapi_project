from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import Category, News


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    st = select(Category).offset(skip).limit(limit)
    res = await db.execute(st)
    return res.scalars().all()


async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    #查询指定分类下的所有新闻
    st = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    res = await db.execute(st)
    return res.scalars().all()


async def get_news_count(db: AsyncSession, category_id: int):
    #查询指定分类下的新闻数量
    st = select(func.count(News.id)).where(News.category_id == category_id)
    res = await db.execute(st)
    return res.scalar_one()


async def get_news_detail(db: AsyncSession, news_id: int,):
    st=select(News).where(News.id==news_id)
    res=await db.execute(st)
    return res.scalar_one_or_none()

async def increase_news_views(db: AsyncSession, news_id: int):
    st=update(News).where(News.id==news_id).values(views=News.views + 1)
    res=await db.execute(st)
    await db.commit()
    #返回是否成功增加点击量
    return res.rowcount>0


async def get_related_news(db: AsyncSession, news_id: int,category_id: int,limit:int=5):
    #推荐时用order_by排序，根据浏览量和发布时间进行推荐
    st=select(News).where(
        News.category_id == category_id,
        News.id != news_id).order_by(News.views.desc(),
News.publish_time.desc()
        ).limit(limit)
    res=await db.execute(st)
    related_news = res.scalars().all()
    #return related_news 直接返回也可以，但是为了前端的展示，我们需要返回新闻的核心数据
    # 列表推导式 推导出新闻的核心数据，然后再 return
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views
    } for news_detail in related_news]
