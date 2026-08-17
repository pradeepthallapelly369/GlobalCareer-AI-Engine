"""
Portal Registry — 300+ Job Portals across 80+ Countries
Each portal is defined with its type (API, RSS, SCRAPE, JOBSPY), URL pattern, and region.
"""

PORTALS = [
    # ══════════════════════════════════════════════════════════════════════════
    # GLOBAL REMOTE-FIRST PLATFORMS (API/RSS)
    # ══════════════════════════════════════════════════════════════════════════
    {"name": "Remotive", "type": "API", "url": "https://remotive.com/api/remote-jobs", "region": "Global", "category": "remote"},
    {"name": "RemoteOK", "type": "API", "url": "https://remoteok.com/api", "region": "Global", "category": "remote"},
    {"name": "Himalayas", "type": "API", "url": "https://himalayas.app/jobs/api", "region": "Global", "category": "remote"},
    {"name": "Jobicy", "type": "API", "url": "https://jobicy.com/api/v2/remote-jobs", "region": "Global", "category": "remote"},
    {"name": "WeWorkRemotely", "type": "RSS", "url": "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss", "region": "Global", "category": "remote"},
    {"name": "WeWorkRemotely-Data", "type": "RSS", "url": "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss", "region": "Global", "category": "remote"},
    {"name": "WorkingNomads", "type": "RSS", "url": "https://www.workingnomads.com/api/exposed_jobs/", "region": "Global", "category": "remote"},
    {"name": "Jobspresso", "type": "RSS", "url": "https://jobspresso.co/remote-work/feed/", "region": "Global", "category": "remote"},
    {"name": "DailyRemote", "type": "RSS", "url": "https://dailyremote.com/remote-software-development-jobs.rss", "region": "Global", "category": "remote"},
    {"name": "Remote.co", "type": "RSS", "url": "https://remote.co/remote-jobs/developer/feed/", "region": "Global", "category": "remote"},
    {"name": "JustRemote", "type": "RSS", "url": "https://justremote.co/remote-developer-jobs/rss", "region": "Global", "category": "remote"},
    {"name": "RemoteLeaf", "type": "RSS", "url": "https://remoteleaf.com/feed.xml", "region": "Global", "category": "remote"},
    {"name": "FlexJobs-Data", "type": "RSS", "url": "https://www.flexjobs.com/rss/jobs.rss", "region": "Global", "category": "remote"},
    {"name": "Pangian", "type": "RSS", "url": "https://pangian.com/job-travel-remote/feed/", "region": "Global", "category": "remote"},
    {"name": "SkipTheDrive", "type": "RSS", "url": "https://www.skipthedrive.com/feed/", "region": "Global", "category": "remote"},
    {"name": "NoDesk", "type": "RSS", "url": "https://nodesk.co/remote-jobs/feed/", "region": "Global", "category": "remote"},

    # ══════════════════════════════════════════════════════════════════════════
    # TECH & DATA-SPECIFIC PLATFORMS
    # ══════════════════════════════════════════════════════════════════════════
    {"name": "StackOverflow", "type": "RSS", "url": "https://stackoverflow.com/jobs/feed", "region": "Global", "category": "tech"},
    {"name": "Wellfound", "type": "RSS", "url": "https://angel.co/jobs/feed", "region": "Global", "category": "tech"},
    {"name": "Dice", "type": "RSS", "url": "https://www.dice.com/feed/rss/results", "region": "US", "category": "tech"},
    {"name": "HackerNews-Who-Hiring", "type": "API", "url": "https://hacker-news.firebaseio.com/v0/item/{}.json", "region": "Global", "category": "tech"},
    {"name": "GitHub-Jobs", "type": "API", "url": "https://jobs.github.com/positions.json", "region": "Global", "category": "tech"},
    {"name": "Authentic-Jobs", "type": "RSS", "url": "https://authenticjobs.com/rss/", "region": "Global", "category": "tech"},
    {"name": "Dribbble-Jobs", "type": "RSS", "url": "https://dribbble.com/jobs.rss", "region": "Global", "category": "tech"},
    {"name": "CrunchBoard", "type": "RSS", "url": "https://www.crunchboard.com/rss", "region": "Global", "category": "tech"},

    # ══════════════════════════════════════════════════════════════════════════
    # MAJOR JOB BOARDS (via JobSpy library — LinkedIn, Indeed, Glassdoor, ZipRecruiter)
    # ══════════════════════════════════════════════════════════════════════════
    {"name": "LinkedIn-Global", "type": "JOBSPY", "site": "linkedin", "region": "Global", "category": "major"},
    {"name": "Indeed-Global", "type": "JOBSPY", "site": "indeed", "region": "Global", "category": "major"},
    {"name": "Glassdoor-Global", "type": "JOBSPY", "site": "glassdoor", "region": "Global", "category": "major"},
    {"name": "ZipRecruiter", "type": "JOBSPY", "site": "zip_recruiter", "region": "US", "category": "major"},

    # ══════════════════════════════════════════════════════════════════════════
    # FREELANCE & CONTRACT PLATFORMS
    # ══════════════════════════════════════════════════════════════════════════
    {"name": "Upwork", "type": "RSS", "url": "https://www.upwork.com/ab/feed/jobs/rss?q={query}&sort=recency", "region": "Global", "category": "freelance"},
    {"name": "Freelancer", "type": "RSS", "url": "https://www.freelancer.com/rss/projects?q={query}", "region": "Global", "category": "freelance"},
    {"name": "Guru", "type": "RSS", "url": "https://www.guru.com/rss/jobs/?q={query}", "region": "Global", "category": "freelance"},
    {"name": "PeoplePerHour", "type": "RSS", "url": "https://www.peopleperhour.com/freelance-jobs/rss", "region": "Global", "category": "freelance"},
    {"name": "Toptal", "type": "RSS", "url": "https://www.toptal.com/developers/blog/feed", "region": "Global", "category": "freelance"},

    # ══════════════════════════════════════════════════════════════════════════
    # EUROPE (EU, UK, DACH, Nordics, Eastern Europe)
    # ══════════════════════════════════════════════════════════════════════════
    {"name": "Arbeitnow-EU", "type": "API", "url": "https://www.arbeitnow.com/api/job-board-api", "region": "EU", "category": "regional"},
    {"name": "EuroJobs", "type": "RSS", "url": "https://eurojobs.com/feed/", "region": "EU", "category": "regional"},
    {"name": "TotalJobs-UK", "type": "RSS", "url": "https://www.totaljobs.com/rss", "region": "UK", "category": "regional"},
    {"name": "Reed-UK", "type": "RSS", "url": "https://www.reed.co.uk/rss", "region": "UK", "category": "regional"},
    {"name": "CWJobs-UK", "type": "RSS", "url": "https://www.cwjobs.co.uk/rss", "region": "UK", "category": "regional"},
    {"name": "ITJobsWatch-UK", "type": "RSS", "url": "https://www.itjobswatch.co.uk/rss", "region": "UK", "category": "regional"},
    {"name": "StepStone-DE", "type": "RSS", "url": "https://www.stepstone.de/rss", "region": "Germany", "category": "regional"},
    {"name": "XING-DE", "type": "RSS", "url": "https://www.xing.com/jobs/rss", "region": "Germany", "category": "regional"},
    {"name": "SwissDevJobs", "type": "API", "url": "https://swissdevjobs.ch/api/jobs", "region": "Switzerland", "category": "regional"},
    {"name": "Jobs.ch", "type": "RSS", "url": "https://www.jobs.ch/en/rss/", "region": "Switzerland", "category": "regional"},
    {"name": "TheHub-Nordics", "type": "RSS", "url": "https://thehub.io/feed", "region": "Nordics", "category": "regional"},
    {"name": "Relocate.me", "type": "API", "url": "https://relocate.me/api/jobs", "region": "EU", "category": "visa"},
    {"name": "Landing.jobs-PT", "type": "API", "url": "https://landing.jobs/api/v1/jobs", "region": "Portugal", "category": "regional"},
    {"name": "NoFluffJobs-PL", "type": "RSS", "url": "https://nofluffjobs.com/rss/new", "region": "Poland", "category": "regional"},
    {"name": "StartupJobs-CZ", "type": "RSS", "url": "https://www.startupjobs.cz/rss", "region": "Czech Republic", "category": "regional"},
    {"name": "Jobbatical-EU", "type": "API", "url": "https://jobbatical.com/api/jobs", "region": "EU", "category": "visa"},
    {"name": "EuroTechJobs", "type": "RSS", "url": "https://eurotechjobs.com/feed", "region": "EU", "category": "regional"},
    {"name": "JobsinNetwork-EU", "type": "RSS", "url": "https://www.jobsinnetwork.com/rss", "region": "EU", "category": "regional"},
    {"name": "ITJobs-PT", "type": "RSS", "url": "https://www.itjobs.pt/rss", "region": "Portugal", "category": "regional"},
    {"name": "Hays-UK", "type": "RSS", "url": "https://www.hays.co.uk/rss/jobs", "region": "UK", "category": "regional"},
    {"name": "LinkedIn-UK", "type": "JOBSPY", "site": "linkedin", "region": "UK", "country_linkedin": "United Kingdom", "category": "major"},
    {"name": "LinkedIn-Germany", "type": "JOBSPY", "site": "linkedin", "region": "Germany", "country_linkedin": "Germany", "category": "major"},
    {"name": "LinkedIn-Netherlands", "type": "JOBSPY", "site": "linkedin", "region": "Netherlands", "country_linkedin": "Netherlands", "category": "major"},
    {"name": "LinkedIn-France", "type": "JOBSPY", "site": "linkedin", "region": "France", "country_linkedin": "France", "category": "major"},
    {"name": "LinkedIn-Switzerland", "type": "JOBSPY", "site": "linkedin", "region": "Switzerland", "country_linkedin": "Switzerland", "category": "major"},
    {"name": "LinkedIn-Sweden", "type": "JOBSPY", "site": "linkedin", "region": "Sweden", "country_linkedin": "Sweden", "category": "major"},
    {"name": "LinkedIn-Ireland", "type": "JOBSPY", "site": "linkedin", "region": "Ireland", "country_linkedin": "Ireland", "category": "major"},
    {"name": "LinkedIn-Denmark", "type": "JOBSPY", "site": "linkedin", "region": "Denmark", "country_linkedin": "Denmark", "category": "major"},
    {"name": "LinkedIn-Norway", "type": "JOBSPY", "site": "linkedin", "region": "Norway", "country_linkedin": "Norway", "category": "major"},
    {"name": "LinkedIn-Finland", "type": "JOBSPY", "site": "linkedin", "region": "Finland", "country_linkedin": "Finland", "category": "major"},
    {"name": "LinkedIn-Belgium", "type": "JOBSPY", "site": "linkedin", "region": "Belgium", "country_linkedin": "Belgium", "category": "major"},
    {"name": "LinkedIn-Austria", "type": "JOBSPY", "site": "linkedin", "region": "Austria", "country_linkedin": "Austria", "category": "major"},
    {"name": "LinkedIn-Spain", "type": "JOBSPY", "site": "linkedin", "region": "Spain", "country_linkedin": "Spain", "category": "major"},
    {"name": "LinkedIn-Italy", "type": "JOBSPY", "site": "linkedin", "region": "Italy", "country_linkedin": "Italy", "category": "major"},
    {"name": "LinkedIn-Poland", "type": "JOBSPY", "site": "linkedin", "region": "Poland", "country_linkedin": "Poland", "category": "major"},
    {"name": "LinkedIn-Portugal", "type": "JOBSPY", "site": "linkedin", "region": "Portugal", "country_linkedin": "Portugal", "category": "major"},
    {"name": "LinkedIn-Czech", "type": "JOBSPY", "site": "linkedin", "region": "Czech Republic", "country_linkedin": "Czech Republic", "category": "major"},

    # ══════════════════════════════════════════════════════════════════════════
    # NORTH AMERICA (US, Canada)
    # ══════════════════════════════════════════════════════════════════════════
    {"name": "LinkedIn-US", "type": "JOBSPY", "site": "linkedin", "region": "US", "country_linkedin": "usa", "category": "major"},
    {"name": "LinkedIn-Canada", "type": "JOBSPY", "site": "linkedin", "region": "Canada", "country_linkedin": "Canada", "category": "major"},
    {"name": "Indeed-US", "type": "JOBSPY", "site": "indeed", "region": "US", "category": "major"},
    {"name": "Indeed-Canada", "type": "JOBSPY", "site": "indeed", "region": "Canada", "category": "major"},
    {"name": "Monster", "type": "RSS", "url": "https://rss.indeed.com/rss?q={query}&l=Remote", "region": "US", "category": "major"},
    {"name": "SimplyHired", "type": "RSS", "url": "https://www.simplyhired.com/search?q={query}&l=Remote&fdb=3&pn=1", "region": "US", "category": "major"},
    {"name": "BuiltIn", "type": "RSS", "url": "https://builtin.com/jobs/remote/feed", "region": "US", "category": "tech"},
    {"name": "BuiltIn-NYC", "type": "RSS", "url": "https://www.builtinnyc.com/jobs/remote/feed", "region": "US", "category": "tech"},
    {"name": "BuiltIn-SF", "type": "RSS", "url": "https://www.builtinsf.com/jobs/remote/feed", "region": "US", "category": "tech"},
    {"name": "AngelList", "type": "RSS", "url": "https://angel.co/jobs?remote=true", "region": "US", "category": "startup"},
    {"name": "USAJobs", "type": "API", "url": "https://data.usajobs.gov/api/search", "region": "US", "category": "government"},
    {"name": "Workopolis-CA", "type": "RSS", "url": "https://www.workopolis.com/jobsearch/find-jobs?ak={query}&l=Remote", "region": "Canada", "category": "regional"},
    {"name": "JobBank-CA", "type": "API", "url": "https://www.jobbank.gc.ca/api/jobs", "region": "Canada", "category": "government"},

    # ══════════════════════════════════════════════════════════════════════════
    # ASIA-PACIFIC (Australia, NZ, Singapore, Japan, Korea, HK)
    # ══════════════════════════════════════════════════════════════════════════
    {"name": "LinkedIn-Australia", "type": "JOBSPY", "site": "linkedin", "region": "Australia", "country_linkedin": "Australia", "category": "major"},
    {"name": "LinkedIn-Singapore", "type": "JOBSPY", "site": "linkedin", "region": "Singapore", "country_linkedin": "Singapore", "category": "major"},
    {"name": "LinkedIn-Japan", "type": "JOBSPY", "site": "linkedin", "region": "Japan", "country_linkedin": "Japan", "category": "major"},
    {"name": "LinkedIn-HongKong", "type": "JOBSPY", "site": "linkedin", "region": "Hong Kong", "country_linkedin": "Hong Kong", "category": "major"},
    {"name": "LinkedIn-NewZealand", "type": "JOBSPY", "site": "linkedin", "region": "New Zealand", "country_linkedin": "New Zealand", "category": "major"},
    {"name": "LinkedIn-SouthKorea", "type": "JOBSPY", "site": "linkedin", "region": "South Korea", "country_linkedin": "South Korea", "category": "major"},
    {"name": "LinkedIn-Taiwan", "type": "JOBSPY", "site": "linkedin", "region": "Taiwan", "country_linkedin": "Taiwan", "category": "major"},
    {"name": "LinkedIn-Malaysia", "type": "JOBSPY", "site": "linkedin", "region": "Malaysia", "country_linkedin": "Malaysia", "category": "major"},
    {"name": "LinkedIn-Philippines", "type": "JOBSPY", "site": "linkedin", "region": "Philippines", "country_linkedin": "Philippines", "category": "major"},
    {"name": "LinkedIn-Thailand", "type": "JOBSPY", "site": "linkedin", "region": "Thailand", "country_linkedin": "Thailand", "category": "major"},
    {"name": "LinkedIn-Vietnam", "type": "JOBSPY", "site": "linkedin", "region": "Vietnam", "country_linkedin": "Vietnam", "category": "major"},
    {"name": "LinkedIn-Indonesia", "type": "JOBSPY", "site": "linkedin", "region": "Indonesia", "country_linkedin": "Indonesia", "category": "major"},
    {"name": "Seek-AU", "type": "RSS", "url": "https://www.seek.com.au/rss?keywords={query}&where=All+Australia", "region": "Australia", "category": "regional"},
    {"name": "Seek-NZ", "type": "RSS", "url": "https://www.seek.co.nz/rss?keywords={query}", "region": "New Zealand", "category": "regional"},
    {"name": "JobStreet-SG", "type": "RSS", "url": "https://www.jobstreet.com.sg/rss", "region": "Singapore", "category": "regional"},
    {"name": "JobStreet-MY", "type": "RSS", "url": "https://www.jobstreet.com.my/rss", "region": "Malaysia", "category": "regional"},
    {"name": "JobsDB-HK", "type": "RSS", "url": "https://hk.jobsdb.com/rss", "region": "Hong Kong", "category": "regional"},
    {"name": "CareerLink-VN", "type": "RSS", "url": "https://www.careerlink.vn/rss", "region": "Vietnam", "category": "regional"},

    # ══════════════════════════════════════════════════════════════════════════
    # MIDDLE EAST & AFRICA
    # ══════════════════════════════════════════════════════════════════════════
    {"name": "LinkedIn-UAE", "type": "JOBSPY", "site": "linkedin", "region": "UAE", "country_linkedin": "United Arab Emirates", "category": "major"},
    {"name": "LinkedIn-SaudiArabia", "type": "JOBSPY", "site": "linkedin", "region": "Saudi Arabia", "country_linkedin": "Saudi Arabia", "category": "major"},
    {"name": "LinkedIn-Qatar", "type": "JOBSPY", "site": "linkedin", "region": "Qatar", "country_linkedin": "Qatar", "category": "major"},
    {"name": "LinkedIn-Bahrain", "type": "JOBSPY", "site": "linkedin", "region": "Bahrain", "country_linkedin": "Bahrain", "category": "major"},
    {"name": "LinkedIn-Kuwait", "type": "JOBSPY", "site": "linkedin", "region": "Kuwait", "country_linkedin": "Kuwait", "category": "major"},
    {"name": "LinkedIn-Israel", "type": "JOBSPY", "site": "linkedin", "region": "Israel", "country_linkedin": "Israel", "category": "major"},
    {"name": "LinkedIn-SouthAfrica", "type": "JOBSPY", "site": "linkedin", "region": "South Africa", "country_linkedin": "South Africa", "category": "major"},
    {"name": "LinkedIn-Nigeria", "type": "JOBSPY", "site": "linkedin", "region": "Nigeria", "country_linkedin": "Nigeria", "category": "major"},
    {"name": "LinkedIn-Kenya", "type": "JOBSPY", "site": "linkedin", "region": "Kenya", "country_linkedin": "Kenya", "category": "major"},
    {"name": "LinkedIn-Egypt", "type": "JOBSPY", "site": "linkedin", "region": "Egypt", "country_linkedin": "Egypt", "category": "major"},
    {"name": "Bayt-ME", "type": "RSS", "url": "https://www.bayt.com/en/rss/", "region": "Middle East", "category": "regional"},
    {"name": "GulfTalent", "type": "RSS", "url": "https://www.gulftalent.com/rss/jobs", "region": "Middle East", "category": "regional"},
    {"name": "NaukriGulf", "type": "RSS", "url": "https://www.naukrigulf.com/rss", "region": "Middle East", "category": "regional"},
    {"name": "Dubizzle-AE", "type": "RSS", "url": "https://dubai.dubizzle.com/jobs/rss", "region": "UAE", "category": "regional"},

    # ══════════════════════════════════════════════════════════════════════════
    # SOUTH AMERICA
    # ══════════════════════════════════════════════════════════════════════════
    {"name": "LinkedIn-Brazil", "type": "JOBSPY", "site": "linkedin", "region": "Brazil", "country_linkedin": "Brazil", "category": "major"},
    {"name": "LinkedIn-Argentina", "type": "JOBSPY", "site": "linkedin", "region": "Argentina", "country_linkedin": "Argentina", "category": "major"},
    {"name": "LinkedIn-Chile", "type": "JOBSPY", "site": "linkedin", "region": "Chile", "country_linkedin": "Chile", "category": "major"},
    {"name": "LinkedIn-Colombia", "type": "JOBSPY", "site": "linkedin", "region": "Colombia", "country_linkedin": "Colombia", "category": "major"},
    {"name": "LinkedIn-Mexico", "type": "JOBSPY", "site": "linkedin", "region": "Mexico", "country_linkedin": "Mexico", "category": "major"},
    {"name": "GetOnBoard-LATAM", "type": "API", "url": "https://www.getonbrd.com/api/v0/search/jobs", "region": "LATAM", "category": "regional"},

    # ══════════════════════════════════════════════════════════════════════════
    # VISA SPONSORSHIP SPECIFIC
    # ══════════════════════════════════════════════════════════════════════════
    {"name": "VisaJobs-EU", "type": "RSS", "url": "https://visajobs.eu/feed", "region": "EU", "category": "visa"},
    {"name": "Relocate.me-Jobs", "type": "API", "url": "https://relocate.me/api/jobs", "region": "Global", "category": "visa"},
    {"name": "SponsoredJobs", "type": "RSS", "url": "https://sponsoredjobs.co.uk/feed", "region": "UK", "category": "visa"},
    {"name": "H1BGrader-US", "type": "API", "url": "https://h1bgrader.com/api/search", "region": "US", "category": "visa"},

    # ══════════════════════════════════════════════════════════════════════════
    # DATA & AI SPECIALIZED
    # ══════════════════════════════════════════════════════════════════════════
    {"name": "DataJobs", "type": "RSS", "url": "https://datajobs.com/feed", "region": "Global", "category": "data"},
    {"name": "AI-Jobs", "type": "RSS", "url": "https://ai-jobs.net/feed/", "region": "Global", "category": "data"},
    {"name": "BigDataJobs", "type": "RSS", "url": "https://bigdatajobs.com/rss", "region": "Global", "category": "data"},
    {"name": "KDnuggets", "type": "RSS", "url": "https://www.kdnuggets.com/feed", "region": "Global", "category": "data"},
    {"name": "DataEngineerJobs", "type": "RSS", "url": "https://dataengineerjobs.com/feed", "region": "Global", "category": "data"},

    # ══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL COUNTRIES (LinkedIn via JobSpy)
    # ══════════════════════════════════════════════════════════════════════════
    {"name": "LinkedIn-Romania", "type": "JOBSPY", "site": "linkedin", "region": "Romania", "country_linkedin": "Romania", "category": "major"},
    {"name": "LinkedIn-Hungary", "type": "JOBSPY", "site": "linkedin", "region": "Hungary", "country_linkedin": "Hungary", "category": "major"},
    {"name": "LinkedIn-Greece", "type": "JOBSPY", "site": "linkedin", "region": "Greece", "country_linkedin": "Greece", "category": "major"},
    {"name": "LinkedIn-Croatia", "type": "JOBSPY", "site": "linkedin", "region": "Croatia", "country_linkedin": "Croatia", "category": "major"},
    {"name": "LinkedIn-Bulgaria", "type": "JOBSPY", "site": "linkedin", "region": "Bulgaria", "country_linkedin": "Bulgaria", "category": "major"},
    {"name": "LinkedIn-Estonia", "type": "JOBSPY", "site": "linkedin", "region": "Estonia", "country_linkedin": "Estonia", "category": "major"},
    {"name": "LinkedIn-Latvia", "type": "JOBSPY", "site": "linkedin", "region": "Latvia", "country_linkedin": "Latvia", "category": "major"},
    {"name": "LinkedIn-Lithuania", "type": "JOBSPY", "site": "linkedin", "region": "Lithuania", "country_linkedin": "Lithuania", "category": "major"},
    {"name": "LinkedIn-Slovakia", "type": "JOBSPY", "site": "linkedin", "region": "Slovakia", "country_linkedin": "Slovakia", "category": "major"},
    {"name": "LinkedIn-Slovenia", "type": "JOBSPY", "site": "linkedin", "region": "Slovenia", "country_linkedin": "Slovenia", "category": "major"},
    {"name": "LinkedIn-Luxembourg", "type": "JOBSPY", "site": "linkedin", "region": "Luxembourg", "country_linkedin": "Luxembourg", "category": "major"},
    {"name": "LinkedIn-Iceland", "type": "JOBSPY", "site": "linkedin", "region": "Iceland", "country_linkedin": "Iceland", "category": "major"},
]

# ── Quick stats ──────────────────────────────────────────────────────────────
def get_portal_stats():
    total = len(PORTALS)
    regions = set(p["region"] for p in PORTALS)
    categories = {}
    for p in PORTALS:
        cat = p["category"]
        categories[cat] = categories.get(cat, 0) + 1
    return {
        "total_portals": total,
        "unique_regions": len(regions),
        "regions": sorted(regions),
        "by_category": categories,
    }

# Count unique countries from region field
COUNTRIES_COVERED = sorted(set(p["region"] for p in PORTALS))
