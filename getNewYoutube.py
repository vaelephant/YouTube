
'''
v1.0--20240715 
主要功能：

	1.	获取频道 ID：
	•	从提供的频道 URL 中提取用户名，并通过 YouTube Data API 获取对应的频道 ID。
	2.	获取视频信息：
	•	使用频道 ID 调用 YouTube Data API 获取该频道的视频信息，并筛选出当天发布的视频。
	3.	输出视频信息：
	•	输出每个频道当天发布的视频标题、链接、发布时间和简介。
'''


import requests
from datetime import datetime, timedelta

API_KEY = 'AIzaSyChajhjGl2wj3MMAqjx0HorsALZwqG6Ljg'
CHANNEL_URLS = [
    'https://www.youtube.com/@AIsuperdomain',
    'https://www.youtube.com/@01coder30',
    'https://www.youtube.com/@MervinPraison',
    

]
DINGTALK_WEBHOOK = 'https://oapi.dingtalk.com/robot/send?access_token=986f9673d047547013597012d50823a3fb11be1b9d82f2fed7d728437f163623'

def get_channel_id_from_url(api_key, url):
    # 提取用户名
    if '@' in url:
        username = url.split('@')[1]
    else:
        raise ValueError("无效的频道URL")

    # 使用 API 查询频道 ID
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={username}&key={api_key}"
    response = requests.get(url)
    channels = response.json().get('items', [])
    if channels:
        return channels[0]['snippet']['channelId']
    return None

def get_channel_videos(api_key, channel_id):
    url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=50"
    response = requests.get(url)
    videos = response.json().get('items', [])
    channel_videos = []

    today = datetime.now().date()

    for video in videos:
        if video['id']['kind'] == "youtube#video":
            video_date = datetime.strptime(video['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').date()
            if video_date == today:
                video_data = {
                    'title': video['snippet']['title'],
                    'link': f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                    'publishedAt': video['snippet']['publishedAt'],
                    #'description': video['snippet']['description']
                }
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
            "content": '信息'+message
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
        message += f"Title: {video['title']}\nLink: {video['link']}\nPublished At: {video['publishedAt']}\nDescription: {video['description']}\n\n"
    return message

# 获取所有频道的视频信息
all_videos = get_all_channels_videos(API_KEY, CHANNEL_URLS)
if all_videos:
    message = format_videos_message(all_videos)
    send_dingtalk_message(DINGTALK_WEBHOOK, message)
else:
    print("今天没有新发布的视频")
    send_dingtalk_message(DINGTALK_WEBHOOK, "今天没有新发布的视频")

for video in all_videos:
    print(f"Title: {video['title']}\nLink: {video['link']}\nPublished At: {video['publishedAt']}\nDescription: {video['description']}\n")