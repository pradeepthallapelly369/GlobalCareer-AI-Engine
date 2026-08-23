import os
import time
import random
from playwright.sync_api import sync_playwright

# 🎯 Customize your target audience here
SEARCH_QUERIES = [
    "Technical Recruiter Qlik",
    "Technical Recruiter Databricks",
    "Data Migration Manager",
    "BI Engineering Manager",
    "Talent Acquisition Data Engineering"
]

# 📝 Customize your connection pitch here
PITCH_MESSAGE = (
    "Hi {first_name}, I'm a Sr. BI/Data Engineer & Tech Lead (6+ yrs) specializing in Qlik Sense, "
    "PowerBI, Databricks, and complex Data Migrations (dbt/SQL). I'm actively looking for remote, "
    "global opportunities and would love to connect to see if I'm a fit for your team!"
)

def human_delay(min_sec=3, max_sec=8):
    """Adds a randomized delay to simulate human browsing."""
    time.sleep(random.uniform(min_sec, max_sec))

def main():
    print("🚀 Initializing LinkedIn Outreach Bot...")
    with sync_playwright() as p:
        # Launch browser with a persistent context to save login cookies
        user_data_dir = os.path.join(os.getcwd(), "chrome_data")
        
        # 🔧 FIX: Remove lock file if previous session crashed
        lock_file = os.path.join(user_data_dir, "SingletonLock")
        if os.path.exists(lock_file):
            try:
                os.unlink(lock_file)
            except Exception:
                pass
                
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False, # Must be visible for initial login
            args=["--start-maximized"],
            no_viewport=True
        )
        
        page = browser.pages[0]
        page.goto("https://www.linkedin.com/")
        
        print("\n" + "="*60)
        print("🔔 PLEASE LOG IN MANUALLY IF REQUIRED")
        print("Once you have logged in and passed any 2FA/Captchas,")
        print("navigate to the main LinkedIn feed, then return to this terminal.")
        print("="*60 + "\n")
        
        input("👉 Press [ENTER] here in the terminal to start the outreach... ")
        
        for query in SEARCH_QUERIES:
            print(f"\n🔍 Searching for: {query}")
            encoded_query = query.replace(" ", "%20")
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}"
            page.goto(search_url)
            human_delay(5, 10)
            
            # Loop through first 3 pages of results to keep it safe
            for page_num in range(1, 4):
                print(f"📄 Scraping Page {page_num}...")
                
                # Scroll down slowly to load lazy elements
                for i in range(3):
                    page.mouse.wheel(0, 500)
                    human_delay(1, 2)
                
                # Get all 'Connect' buttons
                connect_buttons = page.locator("button:has-text('Connect')").all()
                
                if not connect_buttons:
                    print("No 'Connect' buttons found on this page. Moving to next...")
                
                for button in connect_buttons:
                    try:
                        if button.is_visible() and button.is_enabled():
                            # Extract name for personalization
                            aria_label = button.get_attribute("aria-label") or ""
                            name = "there"
                            if "Invite " in aria_label:
                                # "Invite John Doe to connect" -> "John"
                                name = aria_label.replace("Invite ", "").split(" ")[0]
                            elif "Connect with " in aria_label:
                                name = aria_label.replace("Connect with ", "").split(" ")[0]
                                
                            button.click()
                            human_delay(2, 4)
                            
                            # Click "Add a note"
                            add_note_btn = page.locator("button:has-text('Add a note')")
                            if add_note_btn.is_visible():
                                add_note_btn.click()
                                human_delay(1, 3)
                                
                                # Type the personalized message
                                textbox = page.locator("textarea[name='message']")
                                message = PITCH_MESSAGE.format(first_name=name)
                                textbox.fill(message)
                                human_delay(3, 6) # Simulate typing time
                                
                                # Click "Send"
                                send_btn = page.locator("button:has-text('Send')")
                                send_btn.click()
                                print(f"✅ Sent tailored connection request to: {name}")
                                
                                # Long delay after sending to prevent rate limits
                                human_delay(10, 20) 
                            else:
                                # Dismiss modal if 'Add a note' isn't available
                                dismiss_btn = page.locator("button[aria-label='Dismiss']")
                                if dismiss_btn.is_visible():
                                    dismiss_btn.click()
                                    human_delay(1, 2)
                    except Exception as e:
                        print(f"⚠️ Skipped a profile due to UI change.")
                        continue
                
                # Navigate to next page
                next_btn = page.locator("button[aria-label='Next']")
                if next_btn.is_visible() and next_btn.is_enabled():
                    next_btn.click()
                    human_delay(6, 12)
                else:
                    break

        print("\n🎉 Sequence complete! All requests sent.")
        input("Press [ENTER] to close the browser...")
        browser.close()

if __name__ == "__main__":
    main()
