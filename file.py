import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_video_stats(api_key, channel_id):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)

        request = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        )
        response = request.execute()

        if not response['items']:
            raise ValueError(f"No channel found with the provided channel ID: {channel_id}")

        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Retrieve all videos from the uploads playlist
        video_ids = []
        next_page_token = None

        while True:
            playlist_request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            playlist_response = playlist_request.execute()

            # Collect video IDs
            for item in playlist_response['items']:
                video_ids.append(item['contentDetails']['videoId'])

            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break

        # Collect video stats
        video_data = []

        for i in range(0, len(video_ids), 50):
            video_request = youtube.videos().list(
                part='statistics,snippet',
                id=','.join(video_ids[i:i + 50])
            )
            video_response = video_request.execute()

            for video in video_response['items']:
                video_stats = {
                    'video_id': video['id'],
                    'title': video['snippet']['title'],
                    'published_at': video['snippet']['publishedAt'],
                    'view_count': int(video['statistics'].get('viewCount', 0)),
                    'like_count': int(video['statistics'].get('likeCount', 0)),
                    'comment_count': int(video['statistics'].get('commentCount', 0))
                }
                video_data.append(video_stats)

        # Convert the list of dicts to a pandas DataFrame
        video_df = pd.DataFrame(video_data)

        return video_df

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Insert your YouTube Data API key
api_key = ''

# Insert YouTube channel ID
channel_id = 'UCwrVwiJllwhJUKXKmjLcckQ'

df = get_video_stats(api_key, channel_id)

# Save the DataFrame to a CSV file
if df is not None:
    df.to_csv('youtube_video_stats.csv', index=False)
    print(df)
else:
    print("No data to save.")

