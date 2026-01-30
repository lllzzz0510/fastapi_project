from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.util import total_size

from config.db_config import get_db
from crud import news

#1创建路由对象
# prefix路由前缀，tags路由标签
router = APIRouter(prefix="/api/news",tags=["news"])

###接口实现流程
#1模块化路由-》api定义文档
#2定义模型类-》数据库表
#3在crud中创建文件，封装数据库的方法
#4在路由处理函数里调用crud封装好的方法，响应结果


#2定义路由->3挂载路由/注册路由，到main中

#获取新闻分类
@router.get("/categories")
async def get_categories(skip:int=0,limit:int=100,db:AsyncSession=Depends(get_db),):
#获取新闻分类列表-》定义模型类Category——》封装查询数据的方法-》调用方法-》响应结果
    categories=await news.get_categories(db, skip, limit)
    return {
        "code":200,
        "msg":"获取新闻分类",
        "data":categories,
    }

@router.get("/list")
async def get_news_list(
        category_id:int=Query(...,alias="categoryId"),
        page:int=1,
        page_size:int = Query(10,alias="pageSize",le=100),
        db:AsyncSession=Depends(get_db),
):
    offset=(page-1)*page_size
    news_list=await news.get_news_list(db, category_id, offset, page_size)
    total=await news.get_news_count(db,category_id)
    more=(offset+page_size)<total
    return {
        "code":200,
        "msg":"获取新闻列表",
        "data":{"list":news_list,
                "total":total,
                "More":more,}
    }


@router.get("/detail")
async def get_news_detail(news_id:int=Query(...,alias="id"),db:AsyncSession=Depends(get_db)):
    #获取新闻核心数据
    news_detail=await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    #增加新闻点击量
    views_inc=await news.increase_news_views(db, news_detail.id)
    if not views_inc:
        raise HTTPException(status_code=404, detail="增加新闻点击量失败")

    #获取相关新闻
    related_news=await news.get_related_news(db, news_detail.id, news_detail.category_id)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news,
        }
    }
