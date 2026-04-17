so.........
how do run this?
which script do i start with first, or in sequence?

Since you’re running this twice daily, we’ll set this up in a logical sequence that moves from Setup to Verification to Automated Tracking.Follow this order to get the project live:Phase 1: Environment SetupBefore running any scripts, you need your "infrastructure" in place.Clone your repo to the machine where it will run (Local PC or Server).Install dependencies:Bashpip install websockets python-dotenv requests

Create your .env file in the root folder:BashAISSTREAM_KEY=paste_your_key_here

Create vessels.txt and add at least one MMSI to test:Plaintextmmsi,name
235102629,Queen Mary 2

Phase 2: The Sequence of Execution1. First: verify.py (One-Time or Manual)Run this script first to make sure the MMSI numbers you have actually "exist" and to see what names the AIS stream is currently associating with them.Goal: Confirm your list is correct.Run: python verify.pySuccess: You see ✅ Verified: 235102629 is 'QUEEN MARY 2' in your terminal.2. Second: sync_tracker.py (The Scheduled Script)This is your main "production" script. It combines the lookup and the Markdown generation.Goal: Capture the coordinates and generate the vessel_status.md file.Run: python sync_tracker.pySuccess: A new file appears in your folder called vessel_status.md. Open it to see the table and click your map links.Phase 3: Automation (2x Daily)Once you have manually run sync_tracker.py and confirmed the Markdown file looks good, you automate it.If you are on Linux/Mac (Cron):Run crontab -e and add these lines:Bash# Run at 8 AM and 8 PM
0 8,20 * * * cd /path/to/your/repo && /usr/bin/python3 sync_tracker.py

If you want to use GitHub Actions (Cloud Automation):You would create a file at .github/workflows/track.yml. This is arguably the "cleanest" way for a Platform Engineer because it runs on GitHub's servers for free and updates the Markdown file directly in your repo.Summary Table for your READMEYou can copy this into your README.md to keep the instructions clear:StepScriptFrequencyPurpose1verify.pyOnce / As NeededValidates MMSI list and catches ship names.2sync_tracker.py2x Daily (Auto)Fetches live coordinates and updates the Markdown report.

