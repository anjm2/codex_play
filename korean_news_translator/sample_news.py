"""
Realistic sample news articles (Reuters/Benzinga style) for offline testing.
In production, fetcher.py fetches live articles from RSS feeds.
"""

SAMPLE_ARTICLES = [
    {
        "title": "NVIDIA Surpasses $3 Trillion Market Cap as AI Chip Demand Accelerates",
        "url": "https://www.reuters.com/technology/nvidia-market-cap-sample",
        "source": "reuters_technology",
        "published": "2026-02-21T09:30:00Z",
        "html": """
<article class="article-body">
  <h1>NVIDIA Surpasses $3 Trillion Market Cap as AI Chip Demand Accelerates</h1>
  <p>NVIDIA Corp. surged past a $3 trillion market capitalization on Friday, becoming
  the most valuable company in the world after its shares climbed 7.2% to $850, driven
  by surging demand for its Blackwell-architecture graphics processing units (GPUs)
  used in artificial intelligence data centers.</p>

  <h2>Record-Breaking Earnings</h2>
  <p>The Santa Clara, California-based chipmaker reported fiscal fourth-quarter revenue
  of $39.3 billion, up 78% year-over-year, handily beating Wall Street analyst
  expectations of $37.8 billion. Data center revenue — the company's largest segment —
  hit $35.6 billion, a 93% increase from the same period a year ago.</p>

  <p>"Demand for Blackwell is extraordinary," said Jensen Huang, NVIDIA's founder and
  chief executive officer, during the earnings call. "Every cloud service provider,
  enterprise, and sovereign AI initiative is racing to build out AI infrastructure."</p>

  <h2>Competition and Geopolitical Risks</h2>
  <p>Despite its dominant position, NVIDIA faces intensifying competition from Advanced
  Micro Devices (AMD), which launched its MI300X AI accelerator, and from custom chips
  designed by Amazon Web Services, Google, and Microsoft. Analysts estimate AMD could
  capture 15–20% of the high-end AI training chip market by end of 2026.</p>

  <p>The company also faces U.S. government restrictions on exporting advanced chips to
  China, including the H20 and L20 models. The Commerce Department's latest export
  controls, effective January 15, are estimated to reduce NVIDIA's annual revenue by
  approximately $5 billion to $8 billion.</p>

  <h2>Analyst Outlook</h2>
  <p>Analysts at Morgan Stanley raised their price target on NVIDIA to $1,000 per share,
  implying an additional 17.6% upside from current levels. The firm maintained an
  Overweight rating, citing the company's strong competitive moat in AI training
  infrastructure and the imminent ramp of its next-generation Rubin architecture,
  expected in late 2026.</p>

  <p>Goldman Sachs analysts estimated NVIDIA's total addressable market for AI
  accelerators could reach $500 billion by 2028, up from their previous estimate of
  $350 billion, as enterprises accelerate AI adoption across industries including
  healthcare, financial services, and autonomous vehicles.</p>

  <p>NVIDIA shares have returned 420% over the past 24 months, compared with a 28%
  gain for the S&amp;P 500 index over the same period. The stock trades at approximately
  35 times forward earnings, a premium that bulls argue is justified by its growth
  trajectory and market leadership.</p>
</article>
""",
    },
    {
        "title": "Federal Reserve Holds Rates Steady, Signals Two Cuts Possible in 2026",
        "url": "https://www.reuters.com/markets/us/fed-rates-sample",
        "source": "reuters_business",
        "published": "2026-02-21T14:00:00Z",
        "html": """
<article class="article-body">
  <h1>Federal Reserve Holds Rates Steady, Signals Two Cuts Possible in 2026</h1>
  <p>The Federal Reserve left its benchmark interest rate unchanged at 4.25%–4.50%
  on Wednesday, as policymakers continued to assess the impact of persistent inflation
  and a resilient labor market before making any further adjustments to monetary policy.</p>

  <p>The Federal Open Market Committee (FOMC) voted unanimously to hold rates, its
  third consecutive pause following a cumulative 100 basis-point reduction cycle that
  began in September 2025. The decision was in line with market expectations, as
  measured by the CME FedWatch Tool, which had priced in a 96% probability of no change.</p>

  <h2>Chair Powell's Press Conference</h2>
  <p>Federal Reserve Chair Jerome Powell told reporters that while inflation has made
  "meaningful progress" toward the Fed's 2% target, core personal consumption
  expenditure (PCE) inflation — the central bank's preferred gauge — remains at 2.6%,
  above the target. He added that the labor market remains "solid," with unemployment
  at 4.1% and monthly non-farm payroll gains averaging 150,000 over the past three months.</p>

  <p>"We are not in a hurry to adjust our policy stance," Powell said. "We want to be
  confident that inflation is sustainably moving to 2% before we consider further
  reductions in the federal funds rate."</p>

  <h2>Economic Projections</h2>
  <p>The updated Summary of Economic Projections, or "dot plot," showed the median FOMC
  member expects two quarter-point rate cuts in 2026, bringing the year-end federal
  funds rate to 3.75%–4.00%. That is one fewer cut than projected in December 2025.</p>

  <p>GDP growth for 2026 was revised upward to 2.1% from 1.9%, reflecting stronger
  consumer spending and business investment. Inflation forecasts were also revised
  slightly higher, with core PCE expected to end 2026 at 2.3%.</p>

  <h2>Market Reaction</h2>
  <p>U.S. Treasury yields fell modestly after the announcement. The 10-year yield
  declined 4 basis points to 4.42%, while the 2-year yield, which is most sensitive
  to near-term rate expectations, dropped 6 basis points to 4.18%. The U.S. dollar
  weakened 0.3% against a basket of major currencies.</p>

  <p>The S&amp;P 500 index rose 0.8% in the hour following the FOMC statement, with
  rate-sensitive sectors — utilities (up 1.9%) and real estate investment trusts
  (REITs, up 2.1%) — outperforming the broader market. The Nasdaq Composite gained
  1.2%, led by technology megacaps including Apple, Microsoft, and Alphabet.</p>

  <p>Traders in the futures market are now pricing in approximately 50 basis points of
  total rate cuts by December 2026, with the first reduction most likely in June, per
  CME FedWatch data.</p>
</article>
""",
    },
    {
        "title": "Apple to Invest $500 Billion in U.S. Manufacturing Over Next Four Years",
        "url": "https://www.benzinga.com/news/apple-us-investment-sample",
        "source": "benzinga",
        "published": "2026-02-20T11:00:00Z",
        "html": """
<article class="article-body">
  <h1>Apple to Invest $500 Billion in U.S. Manufacturing Over Next Four Years</h1>
  <p>Apple Inc. on Thursday announced a sweeping $500 billion U.S. investment pledge
  spanning four years, encompassing semiconductor manufacturing, server production,
  artificial intelligence research centers, and workforce training programs. The
  announcement, made at the White House alongside President Trump, is the largest
  domestic investment commitment in the company's history.</p>

  <h2>Details of the Investment</h2>
  <p>The investment includes a new advanced manufacturing facility in Texas that will
  produce custom silicon chips for Apple devices, including the A-series and M-series
  processors. The plant, built in partnership with Taiwan Semiconductor Manufacturing
  Company (TSMC), is expected to employ approximately 20,000 workers and become
  operational by 2028.</p>

  <p>Apple also plans to expand its existing supplier ecosystem across the United States,
  partnering with more than 900 domestic suppliers. The company said it would invest
  $10 billion in an AI research fund to partner with U.S. universities and startups
  working on next-generation machine learning technologies.</p>

  <p>"We believe deeply in the promise of America, and we are proud to build on our
  long history of investment and innovation here," said Apple Chief Executive Officer
  Tim Cook. "This investment will help power the next generation of revolutionary
  technology."</p>

  <h2>Competitive Context</h2>
  <p>The announcement comes as rivals including Samsung Electronics and Google are also
  ramping up domestic manufacturing investment. Samsung is building a $40 billion chip
  fabrication plant in Taylor, Texas, while Google parent Alphabet last month committed
  $75 billion in domestic AI infrastructure spending in 2026 alone.</p>

  <p>Apple's Services revenue — which includes the App Store, Apple Music, Apple TV+,
  and iCloud — hit $26.3 billion in the most recent quarter, growing 14% year-over-year
  and now accounting for approximately 26% of total company revenue. Analysts view the
  Services segment as a key driver of Apple's long-term valuation, as hardware growth
  matures in saturated smartphone markets.</p>

  <h2>Investor Reaction</h2>
  <p>AAPL shares rose 3.4% to $248.70 on the news. The stock has gained 18% year-to-date
  and trades at 30 times forward earnings. Short interest in Apple is at its lowest
  level in five years, at approximately 0.7% of shares outstanding, reflecting bullish
  investor sentiment.</p>

  <p>Wedbush Securities analyst Dan Ives called the announcement "a game changer for
  Apple's long-term supply chain strategy," noting that domestic manufacturing could
  reduce the company's geopolitical risk exposure related to China, where Apple
  currently manufactures approximately 85% of its iPhones.</p>
</article>
""",
    },
    {
        "title": "Tesla Reports Record Q4 Vehicle Deliveries Despite Price War Pressures",
        "url": "https://www.benzinga.com/news/tesla-q4-deliveries-sample",
        "source": "benzinga",
        "published": "2026-02-19T17:00:00Z",
        "html": """
<article class="article-body">
  <h1>Tesla Reports Record Q4 Vehicle Deliveries Despite Price War Pressures</h1>
  <p>Tesla Inc. reported record fourth-quarter vehicle deliveries of 560,000 units,
  exceeding analyst expectations of 535,000 and reversing a two-quarter decline that
  had alarmed investors. The Austin, Texas-based electric vehicle maker posted full-year
  2025 deliveries of 1.95 million vehicles, up 12% from 2024, as the launch of the
  refreshed Model Y and the new Model Q drove demand.</p>

  <h2>Pricing and Margins</h2>
  <p>Despite the delivery beat, Tesla maintained aggressive pricing in key markets
  including China, where it cut the Model 3 starting price by 8% to RMB 235,900
  ($32,400) to compete with domestic rivals BYD, Nio, and Li Auto. The price reductions
  weighed on gross margins, which analysts estimate declined to approximately 16.5% from
  17.9% in Q3 2025.</p>

  <p>CEO Elon Musk acknowledged the competitive environment in a post on X (formerly
  Twitter), writing: "Tough quarter on margins but we won on volume. Energy and FSD
  [Full Self-Driving] will carry the margin story in 2026."</p>

  <h2>Robotaxi and AI Business</h2>
  <p>Tesla's robotaxi service, launched in Austin and San Francisco in late 2025, now
  has a wait list of over 2 million customers. The company has submitted applications
  for commercial robotaxi operations in 12 additional U.S. cities and plans to expand
  to Europe by Q3 2026. Revenue from the autonomous driving service is not yet material
  but is expected to contribute meaningfully by 2027.</p>

  <p>The Optimus humanoid robot program produced 1,500 units in 2025, primarily deployed
  within Tesla factories. The company targets production of 50,000 Optimus units in
  2026, priced at $20,000 per robot for commercial customers in the manufacturing sector.</p>

  <h2>Energy Storage Momentum</h2>
  <p>Tesla's Energy Generation and Storage segment deployed 31.4 gigawatt-hours (GWh)
  of Megapack battery storage in Q4 2025, a 180% increase year-over-year, driven by
  utility-scale contracts across the United States, Australia, and the United Kingdom.
  The Energy segment is on track to generate $12 billion in revenue in 2026, analysts
  estimate, with gross margins materially above the automotive segment.</p>

  <p>TSLA shares rose 5.8% to $412.50 following the delivery announcement. The stock
  trades at 85 times forward earnings, reflecting investor confidence in Tesla's
  long-term differentiation in autonomous driving and energy storage relative to
  traditional automakers.</p>
</article>
""",
    },
    {
        "title": "Microsoft Azure Revenue Grows 35% as Enterprise AI Adoption Surges",
        "url": "https://www.reuters.com/technology/microsoft-azure-q2-sample",
        "source": "reuters_technology",
        "published": "2026-02-19T22:00:00Z",
        "html": """
<article class="article-body">
  <h1>Microsoft Azure Revenue Grows 35% as Enterprise AI Adoption Surges</h1>
  <p>Microsoft Corp. reported that revenue from its Azure cloud computing platform
  grew 35% year-over-year in the fiscal second quarter ended December 2025, accelerating
  from 31% growth in the prior quarter and exceeding analyst forecasts. The company's
  total revenue reached $69.6 billion, up 21% from the year-ago period, while
  net income increased 18% to $24.1 billion.</p>

  <h2>AI Driving Cloud Demand</h2>
  <p>Azure's AI services, which include access to OpenAI's GPT-4o and Microsoft's
  proprietary Phi models via the Azure OpenAI Service, contributed 13 percentage
  points to Azure's overall growth. More than 65,000 organizations are now using
  Azure AI services, up from 53,000 three months earlier.</p>

  <p>"The AI era is driving a massive upgrade cycle," said Microsoft Chief Executive
  Officer Satya Nadella during the earnings call. "Every company is rebuilding its
  technology stack around AI, and Azure is the platform of choice for that transformation."</p>

  <h2>Copilot Monetization</h2>
  <p>Microsoft's Copilot AI assistant, integrated across its Microsoft 365 productivity
  suite including Word, Excel, PowerPoint, and Teams, now has 30 million monthly active
  users paying $30 per user per month. Annualized Copilot revenue reached $5.4 billion,
  ahead of analyst estimates of $4.8 billion.</p>

  <p>The company's Intelligent Cloud segment — which encompasses Azure, SQL Server,
  and GitHub — generated $40.9 billion in revenue, up 26% year-over-year. Operating
  income for the segment rose 27% to $19.0 billion, reflecting improving economies
  of scale in cloud infrastructure.</p>

  <h2>Capital Expenditure Plans</h2>
  <p>Capital expenditure in the quarter reached $22.6 billion, nearly double the
  $11.5 billion spent in the year-ago period, as Microsoft continues to expand its
  global data center footprint to support AI workloads. The company has announced
  data center investments in 25 countries in the past 12 months, including $10 billion
  in Japan, $4.3 billion in the United Kingdom, and $3.2 billion in Brazil.</p>

  <p>MSFT shares rose 4.1% in after-hours trading to $478.20. The stock has gained
  22% year-to-date and trades at 32 times forward earnings. The company's market
  capitalization of approximately $3.55 trillion makes it the world's second most
  valuable publicly traded company, behind NVIDIA.</p>
</article>
""",
    },
]
