import praw
import pandas as pd
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

# Initialize Reddit API
reddit = praw.Reddit(
    client_id='eUh9Ij2zNLY1adoKkYdGqA',
    client_secret='eBfX4QmE5B6GOnvdghcx5g6YDDZSMQ',
    user_agent='SentimentAnalysisApp v1.0'
)

# Confirm Reddit connection
try:
    print(f"Connected to Reddit as {reddit.user.me()}")
except Exception as e:
    print(f"Error connecting to Reddit: {e}")

# Choose your subreddit
subreddit = reddit.subreddit('datascience')  # You can change to any subreddit
posts = []
for post in subreddit.top(limit=100):  # # Fetch top 100 posts
    posts.append({
        'title': post.title,
        'score': post.score,
        'comments': post.num_comments,
        'created': post.created_utc,
        'url': post.url,
        'selftext': post.selftext  # body of the post
    })
print("✅ Step 1 complete: Fetched posts from Reddit")

# Convert to DataFrame and show
df = pd.DataFrame(posts)
print("✅ Step 2 complete: Converted posts to DataFrame")

# 🧹 Drop empty posts (posts with no title and no text)
df.dropna(subset=['title', 'selftext'], inplace=True)

# 🧬 Combine title and body into one field called 'text'
df['text'] = df['title'] + ' ' + df['selftext']
print("✅ Step 3 complete: Cleaned and combined text fields")

# 🧼 Clean text: remove links, special characters, etc.
def clean_text(text):
    text = re.sub(r'http\S+', '', text)  # remove links
    text = re.sub(r'[^A-Za-z\s]', '', text)  # remove special chars & numbers
    text = re.sub(r'\s+', ' ', text)  # remove extra spaces
    return text.strip().lower()

df['clean_text'] = df['text'].apply(clean_text)
print("✅ Step 4 complete: Text cleaned")

# 👀 Show cleaned version
print(df[['text', 'clean_text']].head())

# Sentiment analysis
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

df['sentiment_scores'] = df['clean_text'].apply(sid.polarity_scores)
df['sentiment'] = df['sentiment_scores'].apply(lambda score: score['compound'])
print("✅ Step 5 complete: Sentiment scores calculated")

# Function to get sentiment label
def get_sentiment_label(score):
    if score >= 0.05:
        return 'Positive'
    elif score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

df['sentiment_label'] = df['sentiment'].apply(get_sentiment_label)
print("✅ Step 6 complete: Sentiment labels assigned")

# Show sentiment analysis results
print(df[['clean_text', 'sentiment', 'sentiment_label']].head())

# 📊 Count the number of posts in each sentiment category
sentiment_counts = df['sentiment_label'].value_counts()

# 💾 Save the full DataFrame to a CSV file
df.to_csv('reddit_sentiment_results.csv', index=False)
print("✅ Step 7 complete: CSV file 'reddit_sentiment_results.csv' saved.")

# 🖼️ Plot the counts as a bar chart
plt.figure(figsize=(6, 4))
sentiment_counts.plot(kind='bar', color=['green', 'red', 'gray'])
plt.title('Sentiment of Reddit Posts')
plt.xlabel('Sentiment')
plt.ylabel('Number of Posts')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()


# Print message to confirm file was saved
print("Sentiment results saved as 'reddit_sentiment_results.csv'.")
