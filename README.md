# GitHub Trending CLI

A simple command-line tool to fetch and display trending repositories from GitHub based on a selected time range.

## Features
- Fetches trending repositories using the GitHub Search API.
- Filter by duration: `day`, `week`, `month`, `year`.
- Customizable limit on the number of results.
- Clean, table-style output with repository details and descriptions.
- Proper error handling for network issues and rate limiting.

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/AIwolfie/Github-Trending-CLI.git
   cd Github-Trending-CLI
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the tool using Python:

```bash
python main.py --duration [day|week|month|year] --limit [number]
```

### Examples

```bash
# Top 10 trending repos this week (default)
python main.py

# Top 5 trending repos today
python main.py --duration day --limit 5

# Top 20 trending repos this month
python main.py --duration month --limit 20

# Top 10 trending repos this year
python main.py --duration year
```

### Options

| Flag         | Description                          | Default |
|--------------|--------------------------------------|---------|
| `--duration` | Time range: `day`, `week`, `month`, `year` | `week`  |
| `--limit`    | Number of results (1-100)            | `10`    |

## Sample Output

```
🔥 Fetching top 10 trending repositories (last week)...

+----+------------------------------+----------+---------+-----------+--------------------------------------------------------------+
| #  | Repository                   | ⭐ Stars | 🍴 Forks | Language  | Description                                                  |
+----+------------------------------+----------+---------+-----------+--------------------------------------------------------------+
| 1  | user/awesome-project         | 12345    | 678     | Python    | An awesome project that does amazing things...               |
| 2  | org/cool-tool                | 9876     | 432     | TypeScript| A cool tool for developers...                                |
+----+------------------------------+----------+---------+-----------+--------------------------------------------------------------+
```

## License

MIT
