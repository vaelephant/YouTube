import requests
from datetime import datetime, timedelta
import pytz

API_KEY = 'AIzaSyC8c1-j15pE9yCchbDfqnsa_bVNqerYcHE'
CHANNEL_URLS = [
    'https://www.youtube.com/@AIsuperdomain',
    'https://www.youtube.com/@01coder30',
    'https://www.youtube.com/@MervinPraison',
    'https://www.youtube.com/@shoufu',
    'https://www.youtube.com/@GiantCutie-CH',
]
DINGTALK_WEBHOOK = 'https://oapi.dingtalk.com/robot/send?access_token=273f2679feb5915a2a178d1a961100b6bc34fb8eb21f5e9c75d17f7d343a62f1'

def get_channel_id_from_url(api_key, url):
    if '/@' in url:
        username = url.split('/@')[1]
    elif '/channel/' in url:
        return url.split('/channel/')[1]
    elif '/user/' in url:
        username = url.split('/user/')[1]
    elif '/c/' in url:
        username = url.split('/c/')[1]
    else:
        raise ValueError("无效的频道URL")

    api_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={username}&key={api_key}"
    response = requests.get(api_url)
    if response.status_code != 200:
        print(f"请求失败: {response.status_code}, {response.text}")
        return None

    channels = response.json().get('items', [])
    if channels:
        return channels[0]['snippet']['channelId']
    return None

def get_channel_videos(api_key, channel_id):
    url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=50"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"请求失败: {response.status_code}, {response.text}")
        return []

    videos = response.json().get('items', [])
    if not videos:
        print("未找到任何视频")
    else:
        print(f"找到 {len(videos)} 个视频")

    channel_videos = []

    # 设置北京时区
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    twenty_four_hours_ago = now - timedelta(hours=24)

    for video in videos:
        if video['id']['kind'] == "youtube#video":
            video_date = datetime.strptime(video['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            video_date = video_date.astimezone(beijing_tz)
            if video_date > twenty_four_hours_ago:
                video_data = {
                    'title': video['snippet']['title'],
                    'link': f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                    'publishedAt': video['snippet']['publishedAt'],
                }
                print(f"找到过去24小时内发布的视频: {video_data['title']}")  # 打印找到的视频标题
                channel_videos.append(video_data)
    
    return channel_videos

def get_all_channels_videos(api_key, channel_urls):
    all_videos = []
    for url in channel_urls:
        channel_id = get_channel_id_from_url(api_key, url)
        if channel_id:
            videos = get_channel_videos(api_key, channel_id)
            all_videos.extend(videos)
        else:
            print(f"频道ID未找到: {url}")
    return all_videos

def send_dingtalk_message(webhook, message):
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "msgtype": "text",
        "text": {
            "content": '信息监控:\n' + message
        }
    }
    response = requests.post(webhook, headers=headers, json=data)
    if response.status_code == 200:
        print("消息发送成功")
    else:
        print(f"消息发送失败，状态码: {response.status_code}")

def format_videos_message(videos):
    message = ""
    for video in videos:
        message += f"Title: {video['title']}\nLink: {video['link']}\nPublished At: {video['publishedAt']}\n\n"
    return message

# 获取所有频道的视频信息
beijing_tz = pytz.timezone('Asia/Shanghai')
current_time = datetime.now(beijing_tz)
print(f"脚本开始执行时间: {current_time}")

all_videos = get_all_channels_videos(API_KEY, CHANNEL_URLS)
if all_videos:
    message = format_videos_message(all_videos)
    send_dingtalk_message(DINGTALK_WEBHOOK, message)
    for video in all_videos:
        print(f"Title: {video['title']}\nLink: {video['link']}\nPublished At: {video['publishedAt']}\n")
else:
    print("过去24小时内没有新发布的视频")
    send_dingtalk_message(DINGTALK_WEBHOOK, "过去24小时内没有新发布的视频")

current_time = datetime.now(beijing_tz)
print(f"脚本结束执行时间: {current_time}")