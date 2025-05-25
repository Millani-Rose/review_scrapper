from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time

def get_driver():
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_reviews(url):
    print("🔍 Scraping reviews...")
    driver = get_driver()
    driver.get(url)
    time.sleep(5)  # wait for page to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    reviews = []
    if "amazon" in url:
        elements = soup.find_all("span", {"data-hook": "review-body"})
        reviews = [el.text.strip() for el in elements]
    elif "flipkart" in url:
        elements = soup.find_all("div", class_="_6K-7Co")
        reviews = [el.text.strip() for el in elements]

    print(f"✅ Collected {len(reviews)} reviews.")
    return reviews

# Analyze sentiment using TextBlob
def analyze_sentiments(reviews):
    print("💬 Analyzing sentiment...")
    df = pd.DataFrame(reviews, columns=["Review"])
    df["Polarity"] = df["Review"].apply(lambda x: TextBlob(x).sentiment.polarity)
    df["Sentiment"] = df["Polarity"].apply(
        lambda x: "Positive" if x > 0 else "Negative" if x < 0 else "Neutral"
    )
    print(df["Sentiment"].value_counts())
    return df

# Create word clouds and save images
def create_wordcloud(df):
    print("🎨 Generating word clouds...")
    pos_reviews = " ".join(df[df.Sentiment == "Positive"]["Review"])
    neg_reviews = " ".join(df[df.Sentiment == "Negative"]["Review"])

    if pos_reviews.strip():
        WordCloud(width=500, height=300, background_color="white").generate(pos_reviews).to_file("positive_wordcloud.png")
        print("🟢 Positive word cloud saved as positive_wordcloud.png")
    else:
        print("⚠️ No positive reviews found.")

    if neg_reviews.strip():
        WordCloud(width=500, height=300, background_color="black", colormap="Reds").generate(neg_reviews).to_file("negative_wordcloud.png")
        print("🔴 Negative word cloud saved as negative_wordcloud.png")
    else:
        print("⚠️ No negative reviews found.")

# Show pie chart and histogram
def show_graphs(df):
    print("📊 Showing graphs...")
    # PIE CHART
    df["Sentiment"].value_counts().plot(kind="pie", autopct="%1.0f%%", title="Sentiment Distribution", figsize=(6, 6))
    plt.tight_layout()
    plt.show()

    # HISTOGRAM
    df["Polarity"].plot(kind="hist", bins=20, title="Polarity Distribution", color='skyblue', edgecolor='black')
    plt.xlabel("Polarity Score")
    plt.tight_layout()
    plt.show()

# Run all steps
def run_pipeline(url):
    reviews = scrape_reviews(url)
    if not reviews:
        print("⚠️ No reviews found!")
        return
    df = analyze_sentiments(reviews)
    create_wordcloud(df)
    show_graphs(df)
    print("🎉 Done!")

# Entry point
if __name__ == "__main__":
    product_url = input("🛒 Enter Amazon or Flipkart product link: ")
    run_pipeline(product_url)

