# FieldFuckers Website

The official FieldFuckers website that provides design guidelines and offers various logo designs and wallpapers for download. The site displays team members automatically synced from the Steam community group.

## Development

To run the website locally for development:

```bash
hugo server -D
```

This starts a local development server with draft content enabled. The site will be available at `http://localhost:1313` by default.

### Developing the Members Script

To work on the `scripts/members.py` script that syncs Steam group members:

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the required packages:
   ```bash
   pip install -r scripts/requirements.txt
   ```

3. Set the `STEAM_API_KEY` environment variable with your Steam API key:
   ```bash
   export STEAM_API_KEY=your_api_key_here
   ```

4. Run the script:
   ```bash
   python3 scripts/members.py > source/data/members.json
   ```

## Deployment

### GitHub Actions Pipeline

The repository uses GitHub Actions for automated deployment and data synchronization:

**Steam Sync Workflow** (`steam.yaml`)
- Runs automatically every hour via cron schedule
- Fetches the current list of Steam group members using the Steam API
- Updates `source/data/members.json` with the latest member information
- Commits changes back to the repository

**Upload Workflow** (`upload.yaml`)
- Triggers on every push to the `main` branch
- Builds the Hugo static site with minification
- Deploys the generated site to **Cloudflare R2** for hosting

The website is hosted on **Cloudflare R2**, and the deployment pipeline ensures that any changes pushed to the main branch are automatically built and uploaded to the hosting bucket.

