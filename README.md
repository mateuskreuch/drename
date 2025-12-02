# drename

**`drename`** is a Python CLI tool for recursively renaming files, directories, and text contents inside files by replacing occurrences of a target string (`OLD`) with a new string (`NEW`), while **preserving case style**. You indicate word bounds by using a slash (/).

Example:

```bash
drename test/my/user wow/very/nice
```

Will transform:

| Before            | After             |
|-------------------|-------------------|
| `test_My_USER`    | `wow_Very_NICE`   |
| `test-_my-user`   | `wow-_very-nice`  |
| `testMyUser`      | `wowVeryNice`     |
| `TEST_MY_USER`    | `WOW_VERY_NICE`   |

It supports:
- **Case-aware replacements** (e.g., `TestUser` → `WowNice`, `TEST_USER` → `WOW_NICE`).
- Replacements in **file contents** (skipping binary files).
- **Dry-run mode** to preview changes without making them.
- **Rich** terminal output with live updates and diff highlighting.

## 🚀 Usage

Basic syntax:

```bash
drename OLD NEW [OPTIONS] [PATH]
```

### **Arguments**
- **`OLD`** – The text to find and replace (in file names, folder names, and file contents).
- **`NEW`** – The replacement text.
- **`PATH`** *(optional)* – Root directory to start processing. Defaults to the current working directory.

### **Options**
| Option | Description |
|--------|-------------|
| `--dry` | Perform a dry run without making changes. |
| `--help` | Show the help message and exit. |
| `--force` |Force replacements even with pending git changes. |