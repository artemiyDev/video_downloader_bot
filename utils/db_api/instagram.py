from asyncpg.exceptions import UniqueViolationError
from data.config import test
from loader import db

async def write_post_to_db(ig_type, short_code, post,file_id):
    if test:
        return
    if post.video_url:
        post_image = None
        post_video = post.video_url
    else:
        post_image = post.url
        post_video = None

    post_hashtags = ', '.join(post.caption_hashtags)
    post_caption_mentions = ', '.join(post.caption_mentions)
    post_tagged_users = ', '.join(post.tagged_users)

    sql = 'INSERT INTO used_posts(ig_type, short_code, owner_username, post_title, post_image,post_video, post_text, date_utc, ' \
          'caption_hashtags, caption_mentions, tagged_users, video_view_count, likes, post_comments, post_location,tg_file_id,download_times_counter) ' \
          'VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17)'
    try:
        await db.pool.execute(sql, ig_type, short_code, post.owner_username, post.title, post_image, post_video, post.caption,
                              post.date_utc,
                              post_hashtags, post_caption_mentions, post_tagged_users, post.video_view_count, post.likes, post.comments,
                              None, file_id, 1)
    except UniqueViolationError:
        pass


async def get_used_post_from_db(ig_type, short_code):
    sql = "SELECT * FROM used_posts where ig_type = $1 and short_code = $2;"
    result = await db.pool.fetchrow(sql, ig_type, short_code)
    if result:
        await db.pool.execute(
            "UPDATE used_posts set download_times_counter = download_times_counter + 1 where ig_type = $1 and short_code = $2;",
            ig_type, short_code)
    return result
