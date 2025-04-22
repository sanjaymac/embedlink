import streamlit as st
import asyncio
import re
import pandas as pd
from playwright.async_api import async_playwright

st.set_page_config(page_title="🎥 Embed Link Interceptor", layout="wide")
st.title("🎯 Playwright Network Link Interceptor")
st.markdown("Enter multiple video URLs. The app will intercept network requests and return only links containing the keyword (e.g. `embed`).")

urls_input = st.text_area("🔗 Enter Base URLs", placeholder="https://tamilgun.club/video/perusu/\nhttps://tamilgun.club/video/xyz/")
keyword = st.text_input("🧩 Keyword or Regex (Optional)", value="embed")
start_button = st.button("🚀 Start Scraping")

async def fetch_video_requests(url: str, pattern: str):
    video_links = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        def capture_video_links(request):
            req_url = request.url
            if re.search(pattern, req_url):
                video_links.add(req_url)

        page.on("request", capture_video_links)

        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(10000)  # Wait 10s
        except Exception as e:
            video_links.add(f"Error: {e}")
        finally:
            await browser.close()

    return list(video_links)

async def run_all(urls, pattern):
    results = []
    for url in urls:
        links = await fetch_video_requests(url, pattern)
        for link in links:
            results.append({
                "Base URL": url,
                "Intercepted URL": link
            })
    return results

if start_button:
    base_urls = [u.strip() for u in urls_input.strip().splitlines() if u.strip()]
    if not base_urls:
        st.warning("Please enter at least one valid base URL.")
    else:
        with st.spinner("⏳ Intercepting embed/video links..."):
            results = asyncio.run(run_all(base_urls, keyword))
            if results:
                df = pd.DataFrame(results)
                st.success(f"✅ Found {len(df)} intercepted links.")
                st.dataframe(df, use_container_width=True)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download CSV", csv, file_name="intercepted_links.csv", mime="text/csv")
            else:
                st.warning("No matching links found.")
