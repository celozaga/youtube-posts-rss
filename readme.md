# YouTube Community RSS Feeds

This project provides an automated solution to generate RSS feeds for YouTube channel community posts. It uses a Python script and a GitHub Actions workflow to periodically scrape community posts from a list of channels and publish them as standard RSS files, which can be used with any RSS reader or automation tool.

The primary use case is to easily cross-post your YouTube community announcements to other platforms like Discord, Twitter, or Mastodon, which often support RSS feeds.

## Features

* **Automated Generation:** A GitHub Action runs on a schedule (e.g., hourly) to automatically update the feeds.
* **Multiple Channels:** Easily configure multiple YouTube channels to generate separate RSS files for each one.
* **Clean Output:** The RSS feed descriptions contain clean, plain text, making them compatible with various platforms that do not support HTML.
* **Optimized Titles:** Post titles are truncated for a cleaner and more consistent look in RSS readers.
* **GitHub Pages Integration:** The generated feeds are automatically published to GitHub Pages, providing a public URL for your feeds.
* **Error Handling:** The script is robust and handles potential API/HTML structure changes and channels with no new posts.

## How to Get Started

### Step 1: Fork this Repository

Start by forking this repository to your own GitHub account. This will create a copy of the entire project under your user profile.

### Step 2: Configure GitHub Secrets

The GitHub Actions workflow needs permission to commit the generated RSS files back to your repository. You must create a Personal Access Token and add it as a secret.

1.  Go to your GitHub **Settings**.
2.  Navigate to **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
3.  Click on **Generate new token (classic)**.
4.  Give the token a descriptive name (e.g., `YOUTUBE_RSS_BOT`).
5.  Set an expiration date for security.
6.  Under **Select scopes**, check the box for `repo` (Full control of private repositories). This is the only permission needed.
7.  Click **Generate token** and **copy the generated token immediately**. You will not be able to see it again.
8.  Go to your forked repository's **Settings**.
9.  Click on **Secrets and variables** > **Actions**.
10. Click **New repository secret**.
11. Set the name as `GH_TOKEN` and paste the token you copied into the "Secret" field.
12. Click **Add secret**.

### Step 3: Edit the Workflow File

The workflow file (`.github/workflows/rss.yml`) is where you define which channels to follow. Open this file in your repository's editor.

In the `jobs` section, you will find the script execution steps. The current setup is designed to be easily extensible. You can add more channels to the list.

Here is an example:
```yaml
      - name: Generate RSS Feeds
        run: |
          python generate_rss.py UCO6axYvGFekWJjmSdbHo-8Q celozaga.xml
          python generate_rss.py UClgqiSfCPt-HJ3SrF3PNSNA my-second-channel.xml
````markdown
# YouTube Community RSS Feeds

This project provides an automated solution to generate RSS feeds for YouTube channel community posts. It uses a Python script and a GitHub Actions workflow to periodically scrape community posts from a list of channels and publish them as standard RSS files, which can be used with any RSS reader or automation tool.

The primary use case is to easily cross-post your YouTube community announcements to other platforms like Discord, Twitter, or Mastodon, which often support RSS feeds.

## Features

* **Automated Generation:** A GitHub Action runs on a schedule (e.g., hourly) to automatically update the feeds.
* **Multiple Channels:** Easily configure multiple YouTube channels to generate separate RSS files for each one.
* **Clean Output:** The RSS feed descriptions contain clean, plain text, making them compatible with various platforms that do not support HTML.
* **Optimized Titles:** Post titles are truncated for a cleaner and more consistent look in RSS readers.
* **GitHub Pages Integration:** The generated feeds are automatically published to GitHub Pages, providing a public URL for your feeds.
* **Error Handling:** The script is robust and handles potential API/HTML structure changes and channels with no new posts.

## How to Get Started

### Step 1: Fork this Repository

Start by forking this repository to your own GitHub account. This will create a copy of the entire project under your user profile.

### Step 2: Configure GitHub Secrets

The GitHub Actions workflow needs permission to commit the generated RSS files back to your repository. You must create a Personal Access Token and add it as a secret.

1.  Go to your GitHub **Settings**.
2.  Navigate to **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
3.  Click on **Generate new token (classic)**.
4.  Give the token a descriptive name (e.g., `YOUTUBE_RSS_BOT`).
5.  Set an expiration date for security.
6.  Under **Select scopes**, check the box for `repo` (Full control of private repositories). This is the only permission needed.
7.  Click **Generate token** and **copy the generated token immediately**. You will not be able to see it again.
8.  Go to your forked repository's **Settings**.
9.  Click on **Secrets and variables** > **Actions**.
10. Click **New repository secret**.
11. Set the name as `GH_TOKEN` and paste the token you copied into the "Secret" field.
12. Click **Add secret**.

### Step 3: Edit the Workflow File

The workflow file (`.github/workflows/rss.yml`) is where you define which channels to follow. Open this file in your repository's editor.

In the `jobs` section, you will find the script execution steps. The current setup is designed to be easily extensible. You can add more channels to the list.

Here is an example:
```yaml
      - name: Generate RSS Feeds
        run: |
          python generate_rss.py UCO6axYvGFekWJjmSdbHo-8Q celozaga.xml
          python generate_rss.py UClgqiSfCPt-HJ3SrF3PNSNA my-second-channel.xml
````

You can add as many channels as you need by following the same pattern.

### Step 4: Enable GitHub Pages

For the RSS feeds to be publicly accessible, you must enable GitHub Pages.

1.  Go to your repository's **Settings**.
2.  Click on **Pages** in the left sidebar.
3.  Under **Build and deployment**, set the `Source` to `Deploy from a branch`.
4.  Select `main` as the branch and `/` (root) as the folder.
5.  Click **Save**.

It may take a few minutes for your site to be published.

### Step 5: Run the Workflow

For the initial generation of the feeds, you need to manually run the workflow.

1.  Go to the **Actions** tab of your repository.
2.  Click on the `Generate RSS Feeds` workflow in the left sidebar.
3.  Click the **Run workflow** dropdown button.
4.  Click the green **Run workflow** button to start the process.

The workflow will run and commit the new RSS files. Once finished, you can find your feeds at a URL like this:
`https://[seu-usuario].github.io/[seu-repositorio]/[nome-do-arquivo].xml`

For example:
`https://celozaga.github.io/youtube-posts-rss/celozaga.xml`

Enjoy your automated feeds\!

-----

*This project is based on a community chat discussion with Gemini AI for educational purposes.*

```
```
