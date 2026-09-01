# Assignment Dashboard

A dashboard view: one card per class, each sorted by due date with a color-coded flag (🔴 overdue, 🟠 due within 2 days, 🟡 due within a week, 🟢 later, ✅ done). Every card is a fully editable table — click any cell to change it, add or delete rows inline. Top banners surface anything overdue or due within 2 days across all classes.

## Run it locally first (optional but recommended)

```bash
pip install -r requirements.txt
streamlit run app.py
```

This opens it in your browser at `localhost:8501`. Add a few assignments and make sure it feels right before deploying.

## Deploy it (same flow as your data viz class)

1. Create a new GitHub repo (e.g. `assignment-tracker`) and push these three files: `app.py`, `requirements.txt`, `README.md`.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click "New app," pick the repo, branch `main`, and set the main file path to `app.py`.
4. Deploy. You'll get a public URL you can bookmark or add to your phone's home screen.

## About "reminders"

This isn't a push-notification app — there's no phone/email service wired in. Instead, it does the next best thing: every time you open it, it shows a banner for anything **overdue** or **due in the next 3 days**, sorted so the soonest stuff is always at the top. If you want actual push/email reminders later, that would need a separate service (e.g. connecting to Google Calendar or an email API) — happy to help add that if it turns out you want it.

## About persistence

Data saves to `assignments.csv` in the app's storage while it's running. On Streamlit Community Cloud's free tier, if the app goes to sleep from inactivity and later "wakes up," it re-clones from GitHub and any changes made only in that CSV (not committed to the repo) can be lost. Use the **Download backup** button in the sidebar every so often, or **Restore from backup** to reload a CSV you saved. If this becomes annoying, the fix is hooking it up to Google Sheets instead of a local CSV — ask me if you want that.

## Customizing

- Add/remove columns: edit the `COLUMNS` list and the form in `app.py`.
- Change priority/status options: edit the `options=[...]` lists in the `column_config` section.
- Add more classes: no setup needed, just type a new class name when adding an assignment — it'll show up in the filter dropdown automatically.
